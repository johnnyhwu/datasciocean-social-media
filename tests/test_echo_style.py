"""系列 series/prompt-repetition（style: echo，複寫）的回歸測試。
每個版型都要通過程式 B；封面上下兩條字塊帶、金色只給第二排的一格、每一則金格位置不同；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_echo_style.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".agents/skills/make-social-post/scripts/render.py"
sys.path.insert(0, str(ROOT / ".agents/skills/make-social-post/scripts"))
import render as R

SERIES, CONCEPT = "prompt-repetition", "prompt-repetition-causal-bottleneck-and-fix"
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
    {"layout": "recap", "title": "[[前情提要]]與這一則重點", "current": "prompt-repetition-free-lunch-latency"},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "一次看完這個系列", "current": CONCEPT, "nav": "示範導流行"},
]
code, out, html = render(DECK)
expect("複寫風格每個版型通過程式 B（10 張）", code == 0 and "10/10 張通過" in out, out)
expect(f"每一張都有系列標籤（{TAG}）", html.count(TAG) >= 10, str(html.count(TAG)))
for mi in (0, 1, 2):
    s = R.ec_cover(mi)
    expect(f"第 {mi + 1} 則封面：金色只給一格", s.count(f'fill="{R.GOLD}"') == 1, str(s.count(R.GOLD)))
    expect(f"第 {mi + 1} 則封面：上排虛線空框、下排實心", 'stroke-dasharray="10 8"' in s and f'fill="{R.TEAL}"' in s)
expect("不同則的封面金格位置不同", len({R.ec_cover(m) for m in (0, 1, 2)}) == 3)
expect("內頁右上角：金格隨張數往右移", R.ec_corner(1, 10) != R.ec_corner(10, 10))
d1, d2 = R.ec_deco(2, 10), R.ec_deco(9, 10)
expect("文字張下半：第二排金格拉細線回到第一排（有曲線、金格一格）", "<path" in d1 and d1.count(f'fill="{R.GOLD}"') == 1 and d1 != d2)
# 標題與副標整塊在兩條帶子之間置中：短標題時標題往下移（不會擠在上帶下面、下面留大片空白）
code, out, h1 = render([{"layout": "cover", "title": "短的標題", "body": "短副標"}])
code2, out2, h2 = render([{"layout": "cover", "title": "很長的封面主標第一行\n[[很長的封面主標第二行]]\n第三行", "body": "副標第一行\n副標第二行\n副標第三行"}])
import re
t1 = int(re.search(r'id="title" style="top:(\d+)px', h1).group(1)); t2 = int(re.search(r'id="title" style="top:(\d+)px', h2).group(1))
expect("封面：短標題比長標題放得低（整塊置中），兩者都通過程式 B", t1 > t2 >= 300 and code == 0 and code2 == 0, f"{t1} {t2} {out[-200:]} {out2[-200:]}")
# 主標照 \\n 換行
code, out, html = render([{"layout": "diagram", "kind": "flow", "title": "第一行\n[[第二行]]", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}]}])
expect("主標的 \\n 變成 <br>，程式 B 通過", code == 0 and "第一行<br>" in html, out)
# 故意做壞：封面寫了分岔軌道才有的 branches
code, out, _ = render([{**DECK[0], "branches": ["甲", "乙"], "hot": [0]}])
expect("故意做壞：複寫風格的封面寫 branches → 報錯（不默默丟掉）", code != 0 and "branches" in out, out)
# 故意做壞：副標太長，封面擠到下帶 → 程式 B 抓得到
code, out, _ = render([{"layout": "cover", "title": "很長的封面主標第一行\n很長的封面主標第二行\n很長的封面主標第三行", "body": "\n".join(["很長很長的副標一行"] * 9)}])
expect("故意做壞：副標太長壓到下帶 → 報錯「封面放不下」", code != 0 and "封面放不下" in out, out)

print("\n全部通過" if not fails else f"\n{len(fails)} 項失敗")
raise SystemExit(1 if fails else 0)
