"""程式 A 的回歸測試：故意做壞的貼文，程式 A 必須抓到；正確的貼文必須通過（測誤殺）。

測試資料在 tests/fixtures/（不需要 submodule，也不依賴 out/ 與 series/）。
用法（repo 根目錄）：uv run python tests/test_check_a.py
"""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 測試資料放在 tests/fixtures/（第一次實跑的兩則貼文、系列檔與對應的觀念卡），不依賴真實的 out/、series/、concept-wiki/
import os
FX = Path(__file__).resolve().parent / "fixtures"
os.environ["DSO_CONCEPT_WIKI"] = str(FX / "concept-wiki")
os.environ["DSO_SERIES_DIR"] = str(FX / "series")
SCRIPT = ROOT / ".claude/skills/make-social-post/scripts/check_a.py"
import yaml
SLIDES_MAX = yaml.safe_load((ROOT / "config" / "params.yaml").read_text(encoding="utf-8"))["slides_max"]
GOOD_A = json.loads((FX / "out/jev-teardown/jev-overview/spec.json").read_text(encoding="utf-8"))
GOOD_B = json.loads((FX / "out/jev-teardown/confound-three-questions/spec.json").read_text(encoding="utf-8"))


# 獨立貼文（series: null）的延伸閱讀會查 state/ 確認已發布：用暫存的 state 目錄，裡面 jev-overview 已發布
_STATE = tempfile.mkdtemp()
(Path(_STATE) / "jev-overview.yaml").write_text("concept: jev-overview\nformats:\n  ig_carousel:\n    status: published\n", encoding="utf-8")
os.environ["DSO_STATE_DIR"] = _STATE


def standalone(s):
    """把 GOOD_A 改成獨立貼文：沒有系列、沒有系列標籤、最後一張是延伸閱讀（items 是已發布的相關貼文）。"""
    s["series"] = None
    s["caption"]["hashtags"] = [h for h in s["caption"]["hashtags"] if h != "DSO_Jev"]
    s["slides"][-1] = {"layout": "series_map", "title": "延伸閱讀", "items": ["jev-overview"], "nav": "完整文章：datasciocean.com/ai-concept/jev-overview", "refs": ["結構"]}


# 有「標題＋細節」（summary）的系列：把 fixtures 的系列檔每個成員補上 summary（回顧頁與系列地圖用；缺一個就要報錯）
def series_with_summary(drop_one=False, long_one=False):
    d = tempfile.mkdtemp()
    src = FX / "series" / "jev-teardown" / "series.md"
    (Path(d) / "jev-teardown").mkdir()
    txt = src.read_text(encoding="utf-8")
    for k, line in enumerate([l for l in txt.split("\n") if l.startswith("    planned_title:")]):
        if drop_one and k == 1:
            continue
        txt = txt.replace(line, line + f"\n    summary: 第 {k + 1} 則的細節" + ("很長" * 40 if long_one and k == 1 else ""), 1)
    (Path(d) / "jev-teardown" / "series.md").write_text(txt, encoding="utf-8")
    return d


def run(spec, series_dir=None):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        env = {**os.environ, **({"DSO_SERIES_DIR": series_dir} if series_dir else {})}
        r = subprocess.run(["uv", "run", "python", str(SCRIPT), str(p)], capture_output=True, text=True, cwd=ROOT, env=env)
        return r.returncode, r.stdout + r.stderr


RECAP = {"layout": "recap", "title": "前情提要", "current": "confound-three-questions", "refs": ["結構"]}


def mut(base, fn):
    s = copy.deepcopy(base)
    fn(s)
    return s


CASES = [  # (名稱, 基底, 修改, 預期錯誤中要出現的字串)
    ("區塊沒有 refs", GOOD_A, lambda s: s["slides"][2].pop("refs"), "沒有 refs"),
    ("結構區塊含數字", GOOD_A, lambda s: s["slides"][-1].update(title="第 3 則"), "標「結構」卻含數字"),
    ("結構區塊太長", GOOD_A, lambda s: s["slides"][-1].update(title="這是一個太長的結構標題絕對超過字數上限"), "「結構」區塊超過"),
    ("引用 pending 主張", GOOD_B, lambda s: s["slides"][2].update(refs=["c1", "c4"]), "不得使用"),
    ("限定條件被砍", GOOD_A, lambda s: s["threads"]["body"].update(quals=[]), "限定條件未帶出"),
    ("限定條件放行沒寫理由", GOOD_A, lambda s: (s["threads"]["body"].update(quals=[]), s.update(waived_quals=[{"id": "c1#1"}])), "waived_quals 每項要有 id 與 reason"),
    ("卡上沒有的比較詞「最」", GOOD_A, lambda s: s["slides"][6].update(body="計數不可靠、日期是文字不是有序量，這是最嚴重的失效模式，算術要留在程式碼裡做。"), "比較詞/全稱詞 '最'"),
    ("數字在引用主張之外（HINT）", GOOD_A, lambda s: s["slides"][4]["bars"][0].update(value=99.9), "不在引用主張原文"),
    ("引用不存在的主張", GOOD_A, lambda s: s["slides"][2].update(refs=["c99"]), "不存在的主張"),
    ("圖上名稱沒有來源", GOOD_A, lambda s: s["slides"][4]["bars"][1].update(name="GPT-9 Ultra"), "圖上名稱"),
    ("Threads 串文與內容張不一對一", GOOD_A, lambda s: s["threads"]["items"].pop(), "不是一對一"),
    ("串文描述只是重述圖", GOOD_A, lambda s: s["threads"]["items"][2].update(text="參考答案是兩個前沿模型的平均答案"), "重疊率"),
    ("Threads 正文含連結", GOOD_A, lambda s: s["threads"]["body"].update(text=s["threads"]["body"]["text"] + " datasciocean.com"), "連結只能放在最後一則"),
    ("Threads 正文超過 500 字", GOOD_A, lambda s: s["threads"]["body"].update(text="分" * 501), "超過 500"),
    ("hashtag 超過 5 個", GOOD_A, lambda s: s["caption"].update(hashtags=["DSO_Jev", "a", "b", "c", "d", "e"]), "hashtag"),
    ("缺系列標籤", GOOD_A, lambda s: s["caption"].update(hashtags=["LLM"]), "系列標籤"),
    ("出現 podcast", GOOD_A, lambda s: s["caption"].update(nav="歡迎收聽 podcast"), "podcast"),
    ("前向指稱「系列後面」會被讀成這則的後面幾頁", GOOD_A, lambda s: s["slides"][6].update(body="Jev 會漏掉計數與日期這類題目，細節系列後面會再細講，算術要留在程式碼裡做。"), "前向指稱"),
    ("AI 腔黑名單", GOOD_A, lambda s: s["slides"][6].update(body="總而言之，需要注意到主張不成立、反覆推敲的深思型判斷，Jev 在這類判斷上會漏掉。"), "AI 腔"),
    ("脈絡張沒引用 context 主張", GOOD_A, lambda s: s["slides"][1].update(refs=["c11"]), "脈絡張"),
    ("補充字數不在 40 到 60", GOOD_A, lambda s: s["slides"][6].update(body="Jev 會漏掉。"), "補充"),
    ("投影片超過上限張數（slides_max）", GOOD_A, lambda s: s["slides"].extend([copy.deepcopy(s["slides"][2]) for _ in range(SLIDES_MAX)]), "超過 %d" % SLIDES_MAX),
    ("用語：貼文寫了「判官」而不是 Judge", GOOD_A, lambda s: s["threads"]["items"][0].update(text=s["threads"]["items"][0]["text"] + "這個判官很快。"), "用語"),
    ("Threads 輪播模式卻還有逐張 items", GOOD_A, lambda s: s["threads"].update(mode="carousel"), "不該有 items"),
    ("Threads 輪播超過 20 張", GOOD_A, lambda s: (s["threads"].update(mode="carousel", items=[]), s["slides"].extend([copy.deepcopy(s["slides"][2]) for _ in range(20)])), "輪播要 2～20 張"),
    ("獨立貼文的延伸閱讀沒有 items", GOOD_A, lambda s: (standalone(s), s["slides"][-1].pop("items")), "要有 items"),
    ("獨立貼文的延伸閱讀寫了 current", GOOD_A, lambda s: (standalone(s), s["slides"][-1].update(current="jev-overview")), "不用 current"),
    ("獨立貼文的延伸閱讀列了不存在的觀念", GOOD_A, lambda s: (standalone(s), s["slides"][-1].update(items=["no-such-concept"])), "不是任何系列的成員"),
    ("獨立貼文的延伸閱讀列了還沒發布的貼文", GOOD_A, lambda s: (standalone(s), s["slides"][-1].update(items=["confound-three-questions"])), "還沒發布"),
    ("圖上的拉丁字詞（網址）不在卡上也沒被 latin_allow 放行", GOOD_A, lambda s: s["slides"][4]["bars"][1].update(name="arxiv.org"), "圖上名稱"),
    ("示意圖只是把同張的補充重講一遍（HINT）", GOOD_A, lambda s: s["slides"].__setitem__(2, {**s["slides"][2], "layout": "diagram", "kind": "flow", "title": "先判再轉交", "body": "便宜的 Judge 先判斷，信心低的題目再轉交給強的 Judge 處理。", "nodes": [{"text": "便宜的 Judge 先判斷"}, {"text": "信心低的題目再轉交給強的 Judge 處理"}]}), "重述同張"),
    ("最後一則的正文（不是「同系列」行）含卡上沒有的比較詞", GOOD_A, lambda s: s["threads"]["last"].update(text="一定要看。\n" + s["threads"]["last"]["text"]), "比較詞/全稱詞 '一定'"),
    ("caption 第一句太長", GOOD_A, lambda s: s["caption"].update(first="很長" * 30), "第一句"),
]


def main():
    fails = 0
    carousel_ok = mut(GOOD_A, lambda s: (s["threads"].update(mode="carousel"), s["threads"].pop("items")))
    waived_ok = mut(GOOD_A, lambda s: (s.update(waived_quals=[{"id": q, "reason": "人決定刪除"} for q in s["threads"]["body"]["quals"]]), s["threads"]["body"].update(quals=[])))
    series_title_ok = mut(GOOD_A, lambda s: s["threads"]["last"].update(text=s["threads"]["last"]["text"] + "\n同系列：這一定要看（尚未發布）"))
    for base, name in ((series_title_ok, "正確的貼文 A：最後一則「同系列」的標題含比較詞（標題是系列檔的，不檢查；必須通過，測誤殺）"), (waived_ok, "正確的貼文 A：限定條件有寫理由地放行（必須通過，測誤殺）"), (GOOD_A, "正確的貼文 A（必須通過）"), (GOOD_B, "正確的貼文 B（必須通過）"), (carousel_ok, "正確的貼文 A 改成 Threads 輪播模式（必須通過，測誤殺）"), (mut(GOOD_A, standalone), "正確的獨立貼文（series: null，延伸閱讀列已發布的貼文；必須通過，測誤殺）"), (mut(GOOD_A, lambda s: (standalone(s), s["slides"].pop())), "正確的獨立貼文：最後一張是帶走、沒有延伸閱讀（必須通過，測誤殺）"), (mut(GOOD_A, lambda s: (standalone(s), s["slides"].pop(), s["threads"].update(mode="carousel"), s["threads"].pop("items"), s["threads"].pop("last"))), "正確的獨立貼文：Threads 輪播沒有最後一則回覆（必須通過，測誤殺）")):
        code, out = run(base)
        ok = code == 0
        fails += not ok
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else "\n" + out))
    for name, base, fn, expect in CASES:
        code, out = run(mut(base, fn))
        caught = expect in out and ("ERROR" in out or "HINT" in out)
        if name.endswith("（HINT）"):
            caught = expect in out
        elif code == 0:
            caught = False
        fails += not caught
        print(("PASS " if caught else "FAIL ") + f"抓得到：{name}" + ("" if caught else f"  [預期含 {expect!r}]\n{out}"))
    # 回顧頁（系列第 2 則以後的第 2 頁，2026-10-25）
    SS, SS_DROP, SS_LONG = series_with_summary(), series_with_summary(drop_one=True), series_with_summary(long_one=True)
    recap_ok = mut(GOOD_B, lambda s: (s["threads"].update(mode="carousel"), s["threads"].pop("items"), s["slides"].insert(1, copy.deepcopy(RECAP))))
    for name, spec, sd, expect in (
            ("正確的貼文：系列第 2 則、第 2 頁是回顧頁、系列檔有 summary（必須通過，測誤殺）", recap_ok, SS, None),
            ("正確的貼文：系列第 1 則不需要回顧頁（必須通過，測誤殺）", GOOD_A, SS, None),
            ("抓得到：系列第 2 則沒有回顧頁", mut(GOOD_B, lambda s: (s["threads"].update(mode="carousel"), s["threads"].pop("items"))), SS, "第 2 頁要是回顧頁"),
            ("抓得到：系列第 1 則放了回顧頁", mut(GOOD_A, lambda s: (s["threads"].update(mode="carousel"), s["threads"].pop("items"), s["slides"].insert(1, {**RECAP, "current": "jev-overview"}))), SS, "沒有「前面介紹過」"),
            ("抓得到：回顧頁不在第 2 頁", mut(GOOD_B, lambda s: (s["threads"].update(mode="carousel"), s["threads"].pop("items"), s["slides"].insert(3, copy.deepcopy(RECAP)))), SS, "回顧頁固定放第 2 頁"),
            ("抓得到：回顧頁的 current 不是這一則", mut(recap_ok, lambda s: s["slides"][1].update(current="jev-overview")), SS, "current 要是這一則"),
            ("抓得到：系列檔有成員沒有 summary", recap_ok, SS_DROP, "沒有 summary"),
            ("抓得到：系列檔 summary 太長（第 4 則放不下）", recap_ok, SS_LONG, "超過")):
        code, out = run(spec, sd)
        ok = (code == 0) if expect is None else (code != 0 and expect in out)
        fails += not ok
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  [預期含 {expect!r}]\n{out}"))
    print(f"\n{'全部通過' if not fails else f'{fails} 項失敗'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
