"""程式 A 的回歸測試：故意做壞的貼文，程式 A 必須抓到；正確的貼文必須通過（測誤殺）。

需要 concept-wiki submodule 已初始化（測試用的是 out/ 裡兩則貼文與對應的觀念卡）。
用法（repo 根目錄）：uv run python tests/test_check_a.py
"""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".claude/skills/make-social-post/scripts/check_a.py"
GOOD_A = json.loads((ROOT / "out/jev-teardown/jev-overview/spec.json").read_text(encoding="utf-8"))
GOOD_B = json.loads((ROOT / "out/jev-teardown/confound-three-questions/spec.json").read_text(encoding="utf-8"))


def run(spec):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(SCRIPT), str(p)], capture_output=True, text=True, cwd=ROOT)
        return r.returncode, r.stdout + r.stderr


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
    ("AI 腔黑名單", GOOD_A, lambda s: s["slides"][6].update(body="總而言之，需要注意到主張不成立、反覆推敲的深思型判斷，Jev 在這類判斷上會漏掉。"), "AI 腔"),
    ("脈絡張沒引用 context 主張", GOOD_A, lambda s: s["slides"][1].update(refs=["c11"]), "脈絡張"),
    ("補充字數不在 40 到 60", GOOD_A, lambda s: s["slides"][6].update(body="Jev 會漏掉。"), "補充"),
    ("投影片超過 10 張", GOOD_A, lambda s: s["slides"].extend([copy.deepcopy(s["slides"][2]) for _ in range(2)]), "超過 10"),
    ("caption 第一句太長", GOOD_A, lambda s: s["caption"].update(first="很長" * 30), "第一句"),
]


def main():
    fails = 0
    for base, name in ((GOOD_A, "正確的貼文 A（必須通過）"), (GOOD_B, "正確的貼文 B（必須通過）")):
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
    print(f"\n{'全部通過' if not fails else f'{fails} 項失敗'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
