"""系列 series/universal-rag（style: junction，分岔軌道）的回歸測試。
每個版型都要通過程式 B；金色只給一條軌道、每一則亮的軌道不同；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_junction_style.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))
import render as R

SERIES, CONCEPT = "universal-rag", "universalrag-routing-over-unified-embedding"
TAG = R.load_series(SERIES)["name"]
fails = []


def render(slides):
    doc = {"series": SERIES, "concept": CONCEPT, "slides": slides}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(RENDER), str(p), "--force"], capture_output=True, text=True, cwd=ROOT)
        html = "".join(f.read_text(encoding="utf-8") for f in sorted((Path(d) / "html").glob("*.html"))) if (Path(d) / "html").exists() else ""
        return r.returncode, r.stdout + r.stderr, html


def expect(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail[:300]}]" if not ok else ""))
    if not ok:
        fails.append(name)


DECK = [
    {"layout": "cover", "title": "示範封面\n[[第二行]]", "body": "示範副標"},
    {"layout": "context", "title": "先講兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "context", "title": "脈絡張沒有名詞表", "body": "示範脈絡文字。"},
    {"layout": "text", "title": "文字版型", "body": "示範補充文字。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "label": "② 代價", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "body": "示範補充。", "unit": "%", "bars": [{"name": "甲", "value": 30}, {"name": "乙", "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "示意圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "一次看完這個系列", "current": CONCEPT, "nav": "示範導流行"},
]
code, out, html = render(DECK)
expect("分岔軌道每個版型通過程式 B（9 張）", code == 0 and "9/9 張通過" in out, out)
expect(f"內頁與封面都有系列標籤（{TAG}）", html.count(TAG) >= 9, str(html.count(TAG)))
for mi in (0, 1):
    s, h = R.jc_cover(mi)
    expect(f"第 {mi + 1} 則封面只有一條金色軌道", s.count(R.GOLD) == 1 and h == "", str(s.count(R.GOLD)))
expect("不同則亮的軌道不同", R.jc_cover(0) != R.jc_cover(1))
# 2026-11-10：封面岔路的站牌（branches）、亮哪幾條（hot，可多條＝多選）、岔口的一句話（fork）
GOLD_TRACK = f'stroke="{R.GOLD}" stroke-width="16"'
s, h = R.jc_cover(0, ["文字", "表格", "圖片 ✓", "影片"], [2], "先判斷")
expect("封面站牌：四條軌道一條金色，站牌與岔口的字都在", s.count(GOLD_TRACK) == 1 and all(t in h for t in ("文字", "表格", "圖片 ✓", "影片", "先判斷")), h[:300])
s, h = R.jc_cover(1, ["不用查", "段落 ✓", "文件", "表格", "圖片 ✓", "短片段", "整部影片"], [1, 4])
expect("封面站牌：七條軌道、兩條金色（多選）", s.count(GOLD_TRACK) == 2 and h.count('class="t abs dl"') == 7, str(s.count(GOLD_TRACK)))
code, out, html = render([{**DECK[0], "branches": ["文字", "表格", "圖片 ✓", "影片"], "hot": [2], "fork": "先判斷"},
                          {**DECK[0], "branches": ["不用查", "段落 ✓", "文件", "表格", "圖片 ✓", "短片段", "整部影片"], "hot": [1, 4]}])
expect("有站牌的封面（4 條、7 條）通過程式 B（站牌在軌道上，字的對比量得過）", code == 0 and "2/2 張通過" in out, out)
code, out, _ = render([{**DECK[0], "branches": ["文字", "圖片"]}])
expect("故意做壞：有 branches 卻沒寫 hot → 報錯", code != 0 and "hot" in out, out)
code, out, _ = render([{**DECK[0], "fork": "先判斷"}])
expect("故意做壞：只有 fork 沒有 branches → 報錯", code != 0 and "fork" in out, out)
with tempfile.TemporaryDirectory() as d_:
    p_ = Path(d_) / "spec.json"
    p_.write_text(json.dumps({"series": "skillopt", "concept": "skillopt-overview", "slides": [{**DECK[0], "branches": ["甲", "乙"], "hot": [0]}]}, ensure_ascii=False), encoding="utf-8")
    r_ = subprocess.run(["uv", "run", "python", str(RENDER), str(p_), "--force"], capture_output=True, text=True, cwd=ROOT)
    expect("故意做壞：別的系列的封面寫 branches → 報錯（不默默丟掉）", r_.returncode != 0 and "branches" in (r_.stdout + r_.stderr), r_.stdout + r_.stderr)
# 2026-11-10：這個系列的主標照 \n 換行（不換的話 \n 變成空格，中文標題中間多一格空白）
code, out, html = render([{"layout": "diagram", "kind": "flow", "title": "UniversalRAG 先把資料\n[[按形式和大小拆開]]", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}]}])
expect("主標的 \\n 變成 <br>，程式 B 通過", code == 0 and "先把資料<br>" in html, out)
import build_package as BP
cap = BP.caption_text({"slides": [{"layout": "text", "title": "只問 10 秒的動作\n[[卻抓回兩小時的影片]]", "body": "示範。"},
                                  {"layout": "text", "title": "但資料[[多半按形式分群]]，\n而不是按意思", "body": "示範。"}],
                       "caption": {"first": "第一句", "hashtags": ["UniversalRAG"]}})
expect("caption 逐張摘要：換行處沒有標點就補逗號、有標點就直接接", "只問 10 秒的動作，卻抓回兩小時的影片" in cap and "但資料多半按形式分群，而不是按意思" in cap, cap)
expect("內頁小岔口的金色軌道隨張數換", R.jc_corner(1, 15) != R.jc_corner(15, 15))
code, out, _ = render([{**DECK[0], "title": "連續很長沒有標點的封面標題會超出版心所以必須被擋下來才對的一句話"}])
expect("故意做壞：封面標題無標點超長 → 抓得到", code != 0, out)
import check_a as CA
expect("程式 A：名稱裡的數字（VLM2Vec）不算數字，一般數字照抓", "2" not in CA.numbers("VLM2Vec 這類模型") and "85" in CA.numbers("成功率 85%"), str(CA.numbers("VLM2Vec")))
print("\n全部通過" if not fails else f"\n{len(fails)} 項失敗")
raise SystemExit(1 if fails else 0)
