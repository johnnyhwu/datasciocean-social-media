"""雙卡貼文（一則 post 併入兩張觀念卡）與較高資訊密度版型的回歸測試。

涵蓋：
  - check_a：併入的卡用「卡id:cN」引用；待確認主張、不存在的主張、限定條件沒帶出、also 與系列檔不一致、
    補充字數上限（文字張 110、圖表 46）都要抓到；正確的雙卡貼文必須通過（測誤殺）
  - state：主卡 ready／published 時，併入的卡同步，標 merged_into，不計入存量、不重複進回補清單
  - verify_faithful：引用可以出自任何一張併入的卡
  - render（程式 B）：小標籤、110 字補充；圖與表依補充行數往下讓位；subs_inline、鍵「主｜小字」、脈絡張名詞表、帶走張的問題；表太高壓到頁尾必須被抓到
測試資料在 tests/fixtures/；state 與系列檔用暫存目錄，不會動到真實資料。
用法（repo 根目錄）：uv run python tests/test_multicard.py
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FX = Path(__file__).resolve().parent / "fixtures"
SCRIPTS = ROOT / ".claude/skills/make-social-post/scripts"
os.environ["DSO_CONCEPT_WIKI"] = str(FX / "concept-wiki")
sys.path.insert(0, str(SCRIPTS))

TMP = Path(tempfile.mkdtemp())
SERIES_ALSO = TMP / "series-also"      # jev-overview 併入 confound-three-questions
SERIES_PLAIN = FX / "series"           # 沒有 also
shutil.copytree(FX / "series", SERIES_ALSO)
sf = SERIES_ALSO / "jev-teardown" / "series.md"
txt = sf.read_text(encoding="utf-8")
txt = txt.replace("  - concept: jev-overview\n", "  - concept: jev-overview\n    also: [confound-three-questions]\n")
txt = re.sub(r"  - concept: confound-three-questions\n    planned_title: .*\n", "", txt)
sf.write_text(txt, encoding="utf-8")
os.environ["DSO_SERIES_DIR"] = str(SERIES_ALSO)

import cardlib as W  # noqa: E402
import state as S  # noqa: E402
import build_package as BP  # noqa: E402
import series_deps as SD  # noqa: E402
import verify_faithful as VF  # noqa: E402
import verify_reader as VR  # noqa: E402

fails: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f"\n{detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


GOOD = json.loads((FX / "out/jev-teardown/jev-overview/spec.json").read_text(encoding="utf-8"))
GOOD["also_concepts"] = ["confound-three-questions"]
A = "confound-three-questions"


def run_a(spec, series_dir):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        env = {**os.environ, "DSO_SERIES_DIR": str(series_dir)}
        r = subprocess.run(["uv", "run", "python", str(SCRIPTS / "check_a.py"), str(p)], capture_output=True, text=True, cwd=ROOT, env=env)
        return r.returncode, r.stdout + r.stderr


def mut(fn, base=GOOD):
    s = copy.deepcopy(base)
    fn(s)
    return s


# ---------------------------------------------------------------- check_a
code, out = run_a(GOOD, SERIES_ALSO)
check("check_a：正確的雙卡貼文（只宣告 also）通過", code == 0, out)
code, out = run_a(mut(lambda s: s["slides"][2].update(refs=s["slides"][2]["refs"] + [f"{A}:c1"])), SERIES_ALSO)
check("check_a：引用併入卡的主張（卡id:c1）通過", code == 0, out)
code, out = run_a(mut(lambda s: s["slides"][2].update(refs=s["slides"][2]["refs"] + [f"{A}:c4"])), SERIES_ALSO)
check("抓得到：引用併入卡的 pending 主張", code == 1 and "不得使用" in out, out)
code, out = run_a(mut(lambda s: s["slides"][2].update(refs=s["slides"][2]["refs"] + [f"{A}:c99"])), SERIES_ALSO)
check("抓得到：引用併入卡不存在的主張", code == 1 and "不存在的主張" in out, out)
code, out = run_a(mut(lambda s: s["slides"][2].update(refs=s["slides"][2]["refs"] + [f"{A}:c3"])), SERIES_ALSO)
check("抓得到：併入卡的限定條件沒有帶出", code == 1 and f"限定條件未帶出：{A}:c3#1" in out, out)
code, out = run_a(mut(lambda s: s["slides"][2].update(refs=s["slides"][2]["refs"] + [f"{A}:c3"],
                                                      quals=s["slides"][2].get("quals", []) + [f"{A}:c3#1"])), SERIES_ALSO)
check("限定條件用「卡id:c3#1」帶出後通過", code == 0, out)
code, out = run_a(GOOD, SERIES_PLAIN)
check("抓得到：貼文宣告 also_concepts，系列檔成員卻沒有 also", code == 1 and "不一致" in out, out)
no_also = mut(lambda s: s.pop("also_concepts"))
code, out = run_a(no_also, SERIES_ALSO)
check("抓得到：系列檔成員有 also，貼文卻沒有宣告 also_concepts", code == 1 and "不一致" in out, out)


def text_slide(s):
    return next(i for i, sl in enumerate(s["slides"]) if sl["layout"] == "text")


body110 = "測" * 110
body111 = "測" * 111
code, out = run_a(mut(lambda s: s["slides"][text_slide(s)].update(body=body110)), SERIES_ALSO)
check("文字張補充 110 字不因字數被擋", "補充 110 字" not in out, out)
code, out = run_a(mut(lambda s: s["slides"][text_slide(s)].update(body=body111)), SERIES_ALSO)
check("抓得到：文字張補充 111 字", code == 1 and "補充 111 字" in out, out)


def chart_slide(s):
    return next(i for i, sl in enumerate(s["slides"]) if sl["layout"] in ("chart_bars", "chart_sounding"))


code, out = run_a(mut(lambda s: s["slides"][chart_slide(s)].update(body="測" * 111)), SERIES_ALSO)
check("抓得到：圖表補充超過 110 字", code == 1 and "圖表版型補充 111 字" in out, out)

# ---------------------------------------------------------------- state
S.STATE = TMP / "state"
W.SERIES_DIR = SERIES_ALSO
with contextlib.redirect_stdout(io.StringIO()):
    S.set_format("jev-overview", "ig_carousel", status="ready", pack="out/x")
o = S.load(A)["formats"]["ig_carousel"]
check("state：主卡 ready，併入的卡同步 ready 並標 merged_into", o["status"] == "ready" and o["merged_into"] == "jev-overview", str(o))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    S.status()
check("state：併入的卡不計入存量（只算 1 則）", "存量（ready）：1 則" in buf.getvalue(), buf.getvalue())
with contextlib.redirect_stdout(io.StringIO()):
    S.record("jev-overview", "ig_carousel", "https://ig/1", "2026-10-05T20:00", "jev-teardown", "情境痛點", [])
o = S.load(A)
check("state：發布後併入的卡也是 published、標 merged_into，且不另記一筆貼文",
      o["formats"]["ig_carousel"] == {"status": "published", "merged_into": "jev-overview"} and o["posts"] == [], str(o))
check("state：主卡有發布紀錄", len(S.load("jev-overview")["posts"]) == 1)
check("state：沒有 also 的貼文不受影響", S.also_of("schema-valid-not-correct") == [])

# ---------------------------------------------------------------- verify_faithful：多張卡
cardA = FX / "concept-wiki/wiki/concepts/jev-overview.md"
cardB = FX / "concept-wiki/wiki/concepts/confound-three-questions.md"
quoteB = W.parse_card(cardB).claims[0]["source_quotes"][0]
fj = TMP / "f.json"
fj.write_text(json.dumps({"post": "t", "blocks": [{"block": "第 3 張", "atoms": [
    {"text": "x", "verdict": "完全支持", "card_quote": quoteB, "note": ""}], "errors": []}], "gaps": [], "recalculations": []}), encoding="utf-8")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc2 = VF.main(f"{cardA},{cardB}", str(fj))
check("verify_faithful：引用出自併入的卡，兩張卡一起驗證時通過", rc2 == 0 and "引用未逐字" not in buf.getvalue(), buf.getvalue())
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    VF.main(str(cardA), str(fj))
check("抓得到：只給主卡時，出自併入卡的引用被列為審查者引用錯誤", "引用未逐字出現在卡" in buf.getvalue(), buf.getvalue())

# ---------------------------------------------------------------- render（程式 B）
RENDER = SCRIPTS / "render.py"


def render(slide):
    spec = {"series": "jev-cascade", "concept": "render-test", "lang": "zh-TW", "slides": [slide]}
    env = {k: v for k, v in os.environ.items() if k not in ("DSO_SERIES_DIR", "DSO_CONCEPT_WIKI")}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["uv", "run", "python", str(RENDER), str(p)], capture_output=True, text=True, cwd=ROOT, env=env)
        rep = json.loads((Path(d) / "checks-b.json").read_text(encoding="utf-8"))
        return {c["name"]: c["ok"] for c in rep["slides"][0]["checks"]}


chip = {"layout": "text", "title": "Judge 的工作是比對，不是從頭解題", "label": "我的判斷",
        "body": "答案直接寫在文字裡的任務，小模型看一遍就能判，不需要很強的模型；但要是得自己重新推導一遍才知道對不對，小模型就會吃力，這是用 JEV 之前要先分清楚的事。"}
res = render(chip)
check("render：文字張的「我的判斷」小標籤加 100 字以上補充，程式 B 全過", res and all(res.values()), str(res))
bars = [{"name": "知識", "value": 7.0}, {"name": "程式", "value": 12.9, "emphasize": True},
        {"name": "數學", "value": 14.3}, {"name": "邏輯謎題", "value": 27.6}]
four = {"layout": "chart_bars", "title": "要推導的任務，JEV 落後 GPT-6 7.0% 到 27.6%", "unit": "%", "bars": bars, "note": "JEV 1.13 版",
        "body": "拿 JEV 跟 GPT-6 比準確度（JEV 減 GPT-6）：答案讀得出的任務，差距在 2% 內；需要自己推導的任務，就落後很多。"}
res = render(four)
check("render：圖表補充 3 行、4 條橫條無副標籤，程式 B 全過", res and all(res.values()), str(res))
inline = {"layout": "chart_bars", "title": "沒有證據可對照時，三個 Judge 都接近丟硬幣", "unit": "%", "subs_inline": True, "note": "200 題",
          "body": "沒有證據可對照，是指 Judge 只拿到問題和回答，手上沒有證據文件或標準答案，要靠自己的知識判斷有沒有胡說。三個 Judge 的準確度都接近丟硬幣。",
          "bars": [{"name": "JEV", "subs": ["把握（平均最高機率）0.91"], "value": 53.5, "emphasize": True},
                   {"name": "GPT-4.1 mini", "subs": ["把握 0.94"], "value": 54.0}, {"name": "GPT-5.4", "subs": ["把握 0.96"], "value": 56.0}]}
res = render(inline)
check("render：subs_inline 的圖（副標籤同一行、長條間距自動拉開）程式 B 全過", res and all(res.values()), str(res))
tbl4 = {"layout": "table", "title": "沒證據可對照時，用信心分流會失效",
        "body": "串接靠的是「沒把握的才轉給強的 Judge」。這個做法能成立，前提是信心低的題比較容易錯。我們來看這個前提在這 200 題成不成立：",
        "rows": [["分流的前提", "信心低的題，比較容易錯"], ["這 200 題", "信心都很高，而且高低跟對錯無關"],
                 ["所以", "沒有任何門檻能把該轉的題挑出來"], ["就算轉出去", "強的 Judge GPT-5.4 也只有 56%，丟硬幣是 50%"]]}
res = render(tbl4)
check("render：對照表 4 列＋補充 3 行，程式 B 全過", res and all(res.values()), str(res))
tbl_key = {"layout": "table", "title": "Judge 的信心，要分三件事來看", "body": "三件事各有對應的指標：",
           "rows": [["判決｜準確度", "它的判決，到底對不對？"], ["排序｜AUROC", "它沒把握的題，是不是真的比較常錯？"],
                    ["數字大小｜Brier、NLL", "它說有 90% 把握，真的約有 90% 答對嗎？（校準）"]]}
res = render(tbl_key)
check("render：鍵可寫「主｜小字」（指標名稱排在下面），程式 B 全過", res and all(res.values()), str(res))
too_tall = dict(tbl4, rows=[["分流的前提", "信心低的題，比較容易錯，所以才會把它們轉給更強的 Judge 再判一次，這是整個做法能成立的前提條件"]] * 4)
res = render(too_tall)
check("抓得到：表太高掉出版面下緣", res.get("文字與圖形不超出版面下緣（至少留 20px）") is False, str(res))
ctx = {"layout": "context", "title": "Judge 就是請一個 AI，去評另一個 AI 的回答", "key_w": 170,
       "body": "就像請一個 AI 當裁判，幫你看「這兩個回答哪個比較好」。先認識三個名詞：",
       "rows": [["Judge", "請一個 LLM 去評另一個模型的輸出"], ["JEV", "TypeSafe AI 的託管模型，便宜又快；只輸出判決和每個標籤的機率"],
                ["串接", "便宜的 Judge 先判全部題目，沒把握的才交給強的 Judge"]]}
res = render(ctx)
check("render：脈絡張可在補充下面放名詞表（rows），程式 B 全過", res and all(res.values()), str(res))
take = {"layout": "takeaway", "question": "用便宜的 Judge 之前，要先把任務分成哪三類？",
        "title": "讀得出，便宜的 Judge 夠用；要推導，預期大量轉給強的；沒證據可對照，信心不可靠"}
res = render(take)
check("render：帶走張先問問題再給答案，程式 B 全過", res and all(res.values()), str(res))


# ---------------------------------------------------------------- 防呆：已發布的貼文不重渲、組包不漏欄位、系列要鎖定
STATE_TMP = TMP / "state-guard"
STATE_TMP.mkdir()
(STATE_TMP / "guard-test.yaml").write_text("concept: guard-test\nformats:\n  ig_carousel:\n    status: published\n", encoding="utf-8")
W.STATE_DIR = STATE_TMP
guard_spec = {"series": "jev-cascade", "concept": "guard-test", "lang": "zh-TW",
              "slides": [{"layout": "context", "title": "Judge 就是請一個 AI，去評另一個 AI 的回答", "body": "就像請一個 AI 當裁判。"}]}


def run_render(extra):
    env = {k: v for k, v in os.environ.items() if k not in ("DSO_SERIES_DIR", "DSO_CONCEPT_WIKI")}
    env["DSO_STATE_DIR"] = str(STATE_TMP)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(guard_spec, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(RENDER), str(p)] + extra, capture_output=True, text=True, cwd=ROOT, env=env)
        return r.returncode, r.stdout + r.stderr, (Path(d) / "ig" / "01.png").exists()


rc, out, made = run_render([])
check("抓得到：已發布的貼文，render 預設拒絕且沒有產生圖", rc != 0 and "已發布" in out and not made, out)
rc, out, made = run_render(["--force"])
check("--force 才能重渲已發布的貼文", rc == 0 and made, out)

GOODSPEC = json.loads((FX / "out/jev-teardown/jev-overview/spec.json").read_text(encoding="utf-8"))
GOODSPEC["also_concepts"] = ["confound-three-questions"]
W.STATE_DIR = TMP / "state-empty"
(TMP / "state-empty").mkdir()


def build_in_tmp(spec):
    d = Path(tempfile.mkdtemp(dir=TMP))
    (d / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    BP.build(d / "spec.json")
    return d


def mut2(fn):
    s2 = copy.deepcopy(GOODSPEC)
    fn(s2)
    return s2


bad = mut2(lambda s2: s2["slides"][2].update(mystery="這段文字不會被輸出"))
try:
    build_in_tmp(bad)
    check("抓得到：組包遇到不認得的投影片欄位報錯", False)
except ValueError as e:
    check("抓得到：組包遇到不認得的投影片欄位報錯", "mystery" in str(e), str(e))


def add_fields(s2):
    sl = next(x for x in s2["slides"] if x["layout"] == "takeaway")
    sl["question"] = "用便宜的 Judge 之前，要先問哪三件事？"
    sl["label"] = "小標籤測試"
    tb = next(x for x in s2["slides"] if x["layout"] == "table")
    tb["rows"][0][0] = "判決｜準確度"


d = build_in_tmp(mut2(add_fields))
texts = {n: (d / n).read_text(encoding="utf-8") for n in ("_build/post-reader.md", "_build/post-with-refs.md", "ig/post.md")} if (d / "_build").exists() else {}
if not texts:     # spec 不在 _build/ 時，審查檔寫在 spec 同一層
    texts = {n: (d / n).read_text(encoding="utf-8") for n in ("post-reader.md", "post-with-refs.md", "ig/post.md")}
check("組包：帶走張的 question 與 label 輸出到審查文字與 ig/post.md",
      all("用便宜的 Judge 之前，要先問哪三件事？" in t for t in texts.values()) and all("小標籤測試" in t for t in texts.values()), "\n".join(texts))
check("組包：表格鍵「判決｜準確度」輸出到審查文字", all("判決｜準確度" in t for t in texts.values()))

# 系列鎖定警告
SL = TMP / "series-lock" / "s1"
SL.mkdir(parents=True)
(SL / "series.md").write_text("---\nid: s1\nname: 測試系列\ncolor: teal-mid\nmembers:\n  - concept: aaa\n    planned_title: A\nhashtag: X\nstatus: planning\n---\n", encoding="utf-8")
W.SERIES_DIR = TMP / "series-lock"
w = W.series_lock_warning("s1", "aaa")
check("抓得到：系列成員還沒定案（沒有 members_locked）、也沒有人發布 → 警告", bool(w) and "members_locked" in w, str(w))
(SL / "series.md").write_text((SL / "series.md").read_text(encoding="utf-8").replace("status: planning", "members_locked: true\nstatus: planning"), encoding="utf-8")
check("系列加上 members_locked: true 之後不再警告", W.series_lock_warning("s1", "aaa") is None)
(SL / "series.md").write_text((SL / "series.md").read_text(encoding="utf-8").replace("members_locked: true\n", ""), encoding="utf-8")
(STATE_TMP / "aaa.yaml").write_text("concept: aaa\nformats:\n  ig_carousel:\n    status: published\n", encoding="utf-8")
W.STATE_DIR = STATE_TMP
check("已有成員發布過的舊系列（沒有鎖定欄位）不重複警告", W.series_lock_warning("s1", "aaa") is None)
W.SERIES_DIR = SERIES_ALSO

# verify_reader：答對、後面補一句「貼文沒有給個別數字」不能被誤判成答沒寫
post_txt = TMP / "post.md"
post_txt.write_text("差距在 2% 內，貼文只給範圍。", encoding="utf-8")
rj = TMP / "r.json"
good_reader = {"post": "t", "skim": {"conclusion": "差距在 2% 內", "citations": [{"quote": "差距在 2% 內"}]},
               "core": {k: {"answer": "x", "citations": [{"quote": "差距在 2% 內"}]} for k in ("thesis", "mechanism", "evidence")}, "terms": [],
               "post_only_questions": [
                   {"q": "差多少？", "answer": "差距在 2% 內。貼文沒有給各任務的個別數字。", "citations": [{"quote": "差距在 2% 內"}]},
                   {"q": "陷阱題", "answer": "貼文沒寫。整則沒有提到費用。", "citations": []}], "feel": {}}
rj.write_text(json.dumps(good_reader, ensure_ascii=False), encoding="utf-8")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc3 = VR.main(str(post_txt), str(rj), [2])
check("verify_reader：答對又補一句「貼文沒有…」不被誤判成漏看", rc3 == 0, buf.getvalue())
good_reader["post_only_questions"][0]["answer"] = "貼文沒寫"
rj.write_text(json.dumps(good_reader, ensure_ascii=False), encoding="utf-8")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc3 = VR.main(str(post_txt), str(rj), [2])
check("抓得到：非陷阱題答「貼文沒寫」仍算漏看", rc3 == 1 and "漏看" in buf.getvalue(), buf.getvalue())

# series_deps：重複主張偵測
c1 = [{"id": "c1", "text": "AUROC 衡量 q 排序錯題的能力：隨機抽一題答錯的、一題答對的，答錯那題的 q 比較低的機率"}]
c2 = [{"id": "c3", "text": "AUROC 衡量 q 排序錯題的能力：隨機抽一題答錯的、一題答對的，答錯那題的 q 比較低的機率；0.5 等於亂猜"},
      {"id": "c9", "text": "完全不相干的另一件事，講的是溫度縮放怎麼做"}]
check("series_deps：找得到幾乎相同的主張，不誤抓不相干的", SD.dup_claims(c1, c2) == [("c1", "c3")], str(SD.dup_claims(c1, c2)))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc4 = SD.main("jev-teardown")
check("series_deps：可以對系列跑完（結束碼 0）", rc4 == 0 and "依賴檢查" in buf.getvalue(), buf.getvalue()[:200])

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'全部通過' if not fails else f'{len(fails)} 項失敗：' + '; '.join(fails)}")
sys.exit(1 if fails else 0)
