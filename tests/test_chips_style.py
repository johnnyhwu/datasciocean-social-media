"""系列 series/cer（style: chips，籌碼）的回歸測試。
每個版型都要通過程式 B；封面三疊籌碼、金色只給最高那疊的頂端一枚、最高那疊不是枚數最多的那疊、每一則金色那疊位置不同；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_chips_style.py
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".agents/skills/make-social-post/scripts/render.py"
sys.path.insert(0, str(ROOT / ".agents/skills/make-social-post/scripts"))
import render as R

SERIES, CONCEPT = "cer", "cer-process-confidence-weighted-voting"
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
    {"layout": "recap", "title": "[[前情提要]]與這一則重點", "current": "cer-critical-token-confidence"},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "這個系列共三則", "current": CONCEPT, "nav": "示範導流行"},
]
code, out, html = render(DECK)
expect("籌碼風格每個版型通過程式 B（10 張）", code == 0 and "10/10 張通過" in out, out)
expect(f"每一張都有系列標籤（{TAG}）", html.count(TAG) >= 10, str(html.count(TAG)))

GOLD = f'fill="{R.GOLD}"'
wins = []
for mi in (0, 1, 2):
    s, top = R.ch_cover(mi)
    expect(f"第 {mi + 1} 則封面：金色只給一枚", s.count(GOLD) == 1, str(s.count(GOLD)))
    stacks = R.CH_SETS[mi]
    hs = [R.ch_height(t, 30, 118, 10) for t in stacks]
    win = hs.index(max(hs))
    wins.append(win)
    expect(f"第 {mi + 1} 則封面：最高那疊不是枚數最多的那疊（看把握、不只數票）", len(stacks[win]) < max(len(t) for t in stacks), str(stacks))
    expect(f"第 {mi + 1} 則封面：籌碼在封面下半（頂端 y > 700）", top > 700, str(top))
expect("三則封面金色那疊位置都不同", len(set(wins)) == 3, str(wins))
expect("內頁右上角：金色那疊隨張數換位置", R.ch_corner(1, 10) != R.ch_corner(10, 10))
d1, d2 = R.ch_deco(2, 10), R.ch_deco(9, 10)
expect("文字張下半：五疊籌碼、金色一枚、隨張數移動", d1.count(GOLD) == 1 and d1 != d2)
expect("帶走張：金色一枚", R.ch_takeaway(0).count(GOLD) == 1)
# 主標照 \n 換行
code, out, html = render([{"layout": "diagram", "kind": "flow", "title": "第一行\n[[第二行]]", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}]}])
expect("主標的 \\n 變成 <br>，程式 B 通過", code == 0 and "第一行<br>" in html, out)
# 封面的標題位置固定在上方
code, out, h1 = render([{"layout": "cover", "title": "短的標題", "body": "短副標"}])
m = re.search(r'id="title" style="top:(\d+)px', h1)
expect("封面：短標題也通過程式 B，標題在上方", code == 0 and m and int(m.group(1)) < 300, out[-300:])
# 故意做壞：封面寫了分岔軌道才有的 branches
code, out, _ = render([{**DECK[0], "branches": ["甲", "乙"], "hot": [0]}])
expect("故意做壞：籌碼風格的封面寫 branches → 報錯（不默默丟掉）", code != 0 and "branches" in out, out)
# 故意做壞：副標太長，壓到下半的籌碼 → 報錯
code, out, _ = render([{"layout": "cover", "title": "很長的封面主標第一行\n很長的封面主標第二行\n很長的封面主標第三行", "body": "\n".join(["很長很長的副標一行"] * 9)}])
expect("故意做壞：副標太長壓到籌碼 → 報錯「封面放不下」", code != 0 and "封面放不下" in out, out)

print("\n全部通過" if not fails else f"\n{len(fails)} 項失敗")
raise SystemExit(1 if fails else 0)
