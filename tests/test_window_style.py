"""系列 series/claude-code（style: window，視窗）的回歸測試。
每個版型都要通過程式 B；封面與內頁都有系列標籤；視窗的圖形是固定規則（游標停的行隨張數換、封面假紀錄隨則換）；
故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_window_style.py
spec 放暫存資料夾，不碰 out/；--force 只渲染暫存資料夾。
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))
import render as R

CONCEPT = "claude-code-agentic-loop-and-tools"
TAG = "拆解 Claude Code"
fails = []


def render(slides, concept=CONCEPT):
    doc = {"series": "claude-code", "concept": concept, "slides": slides}
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
    {"layout": "cover", "title": "Claude Code 的核心，\n只有[[一個迴圈]]", "body": "示範副標：讀、改、跑，看結果，再決定下一步。"},
    {"layout": "recap", "title": "[[前情提要]]與這一則", "current": "claude-code-extension-and-context", "refs": ["結構"]},
    {"layout": "context", "title": "先認識兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "context", "title": "脈絡張沒有名詞表", "body": "示範脈絡文字。"},
    {"layout": "text", "title": "文字版型：下半一個視窗", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "流程圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "一次看完這個系列", "current": "claude-code-extension-and-context", "nav": "示範導流行"},
]

code, out, html = render(DECK, concept="claude-code-extension-and-context")
expect("視窗樣張的每個版型通過程式 B（10 張）", code == 0 and "10/10 張通過" in out, out)
expect(f"內頁與封面都有系列標籤（{TAG}）", html.count(TAG) >= 10, str(html.count(TAG)))

# 視窗：同一組參數 → 同一結果；游標停的行隨張數換；金色只有一個游標
a, b = R.wn_deco(1), R.wn_deco(1)
c = R.wn_deco(2)
expect("wn_deco：同參數同結果", a == b, "")
cur = lambda s: re.findall(r'<rect class="bg" x="\d+" y="(\d+)" width="26" height="48" fill="#DDA642"/>', s)
expect("wn_deco：游標停的行隨張數換", cur(a) and cur(c) and cur(a) != cur(c), f"{cur(a)} {cur(c)}")
expect("wn_deco：金色只有一個游標", a.count('fill="#DDA642"') == 1, str(a.count('fill="#DDA642"')))
expect("wn_deco：深色版（帶走張）游標改米色、沒有金色", R.wn_deco(1, dark=True).count("#DDA642") == 0, "")
cv0, cv1 = R.wn_cover(0), R.wn_cover(1)
expect("wn_cover：每一則的假紀錄不同", cv0 != cv1, "")
expect("wn_cover：金色只有一個游標", cv0.count('fill="#DDA642"') == 1 and cv1.count('fill="#DDA642"') == 1, "")
expect("wn_cover：字級只用 28／34", set(re.findall(r'font-size="(\d+)"', cv0 + cv1)) <= {"28", "34"}, str(set(re.findall(r'font-size="(\d+)"', cv0 + cv1))))

# 副標接在標題下面：封面主標 3 行也要通過
code, out, _ = render([{"layout": "cover", "title": "Claude Code 的核心，\n只有一個迴圈，\n讀、改、跑，再判斷", "body": "示範副標：直到它自己說做完了。"}])
expect("封面主標 3 行也通過程式 B", code == 0 and "1/1 張通過" in out, out)

# 故意做壞
code, out, _ = render([{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}])
expect("故意做壞：補充文字太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "cover", "title": "實力差四倍但是弱的那隊還有兩成機率會爆冷而且這個差距讓人意外不已", "body": "示範副標"}])
expect("故意做壞：封面主標太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "series_map", "title": "想接著看？", "current": "不存在的觀念", "nav": "x"}])
expect("故意做壞：系列地圖的 current 不在成員裡 → 報錯", code != 0, out)

print("\n全部通過" if not fails else f"\n失敗 {len(fails)} 項：{fails}")
raise SystemExit(1 if fails else 0)
