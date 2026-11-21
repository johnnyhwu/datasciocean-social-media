"""系列 series/ragu（style: ceiling，低天花板）的回歸測試。
每個版型都要通過程式 B；封面的天花板貼齊兩側、金色只給頂到天花板的一點（圓的上緣貼著天花板下緣）、每一則金點位置不同、標題在圖的下面；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_ceiling_style.py
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

SERIES, CONCEPT = "ragu", "ragu-results-peeling-confounds"
TAG = R.load_series(SERIES)["name"]
fails = []


def render(slides, concept=CONCEPT):
    doc = {"series": SERIES, "concept": concept, "slides": slides}
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
    {"layout": "cover", "title": "示範封面\n[[第二行]]", "body": "示範副標\n第二行"},
    {"layout": "context", "title": "先講兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "context", "title": "脈絡張沒有名詞表", "body": "示範脈絡文字。"},
    {"layout": "text", "title": "文字版型", "body": "示範補充文字。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "label": "證據", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "body": "示範補充。", "unit": "%", "bars": [{"name": "甲", "value": 30}, {"name": "乙", "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "示意圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "recap", "title": "[[前情提要]]與這一則重點", "current": "retrieval-recall-not-answer-quality"},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "這個系列共六則", "current": CONCEPT, "nav": "示範導流行"},
]
code, out, html = render(DECK)
expect("低天花板風格每個版型通過程式 B（10 張）", code == 0 and "10/10 張通過" in out, out)
expect(f"每一張都有系列標籤（{TAG}）", html.count(TAG) >= 10, str(html.count(TAG)))

GOLD = f'fill="{R.GOLD}"'
tops = []
for mi in (0, 1, 2):
    s, bot = R.cl_cover(mi)
    expect(f"第 {mi + 1} 則封面：金色只給一點", s.count(GOLD) == 1, str(s.count(GOLD)))
    m = re.search(r'cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" fill="' + R.GOLD, s)
    cx, cy, r = map(float, m.groups())
    tops.append(cx)
    ceil_y, sw = R.CL_COVER[2], 28
    expect(f"第 {mi + 1} 則封面：金點的上緣剛好貼著天花板下緣", abs((cy - r) - (ceil_y + sw / 2)) < 0.6, f"{cy - r} vs {ceil_y + sw / 2}")
    others = [float(a) - float(b) for a, b in re.findall(r'cy="([\d.]+)" r="([\d.]+)" fill="' + R.TEAL, s)]
    expect(f"第 {mi + 1} 則封面：其他點都沒頂到天花板", min(others) > ceil_y + sw / 2 + 5, str(min(others)))
    expect(f"第 {mi + 1} 則封面：天花板貼齊兩側出血", f'x1="0" y1="{ceil_y}" x2="{R.WD}"' in s)
    expect(f"第 {mi + 1} 則封面：圖不超過畫面中段（最低點 y <= 820；2026-11-21 起圖會往下長、吃掉標題下方的空白）", bot <= 820, str(bot))
expect("三則封面金點位置都不同", len(set(tops)) == 3, str(tops))
expect("內頁右上角：金點隨張數換位置", R.cl_corner(1, 10) != R.cl_corner(10, 10))
d1, d2 = R.cl_deco(2, 10), R.cl_deco(9, 10)
expect("文字張下半：金色一點、隨張數移動", d1.count(GOLD) == 1 and d1 != d2)
expect("帶走張：金色一點、天花板米色", R.cl_takeaway(0).count(GOLD) == 1 and f'stroke="{R.CREAM}" stroke-width="8"' in R.cl_takeaway(0))
code, out, html = render([{"layout": "diagram", "kind": "flow", "title": "第一行\n[[第二行]]", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}]}])
expect("主標的 \\n 變成 <br>，程式 B 通過", code == 0 and "第一行<br>" in html, out)
code, out, h1 = render([{"layout": "cover", "title": "短的標題", "body": "短副標"}])
m = re.search(r'id="title" style="top:(\d+)px', h1)
expect("封面：標題在圖的下面", code == 0 and m and int(m.group(1)) > R.cl_cover(0)[1] + 30, out[-300:])
code, out, _ = render([{**DECK[0], "branches": ["甲", "乙"], "hot": [0]}])
expect("故意做壞：低天花板風格的封面寫 branches → 報錯（不默默丟掉）", code != 0 and "branches" in out, out)
code, out, _ = render([{"layout": "cover", "title": "很長的封面主標第一行\n很長的封面主標第二行\n很長的封面主標第三行", "body": "\n".join(["很長很長的副標一行"] * 6)}])
expect("故意做壞：副標太長壓到頁腳 → 報錯「封面放不下」", code != 0 and "封面放不下" in out, out)

print("\n全部通過" if not fails else f"\n{len(fails)} 項失敗")
raise SystemExit(1 if fails else 0)
