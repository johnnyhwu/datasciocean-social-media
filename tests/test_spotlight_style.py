"""系列 series/sag（style: spotlight，探照燈）的回歸測試。
每個版型都要通過程式 B；封面與內頁都有系列標籤；探照燈的點線是固定規則（同種子同結果、落點隨則換）；
底部窄帶的點數 = 張數；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_spotlight_style.py
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

CONCEPT = "sag-latent-hyperedge-one-hop"
fails = []


def render(slides, concept=CONCEPT):
    doc = {"series": "sag", "concept": concept, "slides": slides}
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
    {"layout": "cover", "title": "多步推理，\n一定要先建[[知識圖譜]]嗎？", "body": "示範副標：線下只存標籤，查詢時才連成圖。"},
    {"layout": "context", "title": "先認識兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "context", "title": "脈絡張沒有名詞表", "body": "示範脈絡文字。"},
    {"layout": "text", "title": "文字版型：下半一片暗處的點線", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "流程圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "想接著看？", "current": CONCEPT, "nav": "示範導流行"},
]

code, out, html = render(DECK)
expect("探照燈樣張的每個版型通過程式 B（9 張）", code == 0 and "9/9 張通過" in out, out)
expect("內頁與封面都有系列標籤（SAG：不先建圖，查詢時才連）", html.count("SAG：不先建圖，查詢時才連") >= 9, str(html.count("SAG：不先建圖，查詢時才連")))

# 探照燈的點線：同一組參數 → 同一結果；落點（pick）不同 → 光圈中心不同
a = R.sp_field((90, 180, 990, 730), 38, 7, 0, 270)
b = R.sp_field((90, 180, 990, 730), 38, 7, 0, 270)
c = R.sp_field((90, 180, 990, 730), 38, 7, 1, 270)
expect("sp_field：同參數同結果（固定亂數種子）", a == b, "")
ctr = lambda s: re.findall(r'<circle class="bg" cx="(\d+)" cy="(\d+)" r="24" fill="#DDA642"/>', s)
expect("sp_field：落點隨 pick 換（光圈中心不同）", ctr(a) and ctr(c) and ctr(a) != ctr(c), f"{ctr(a)} {ctr(c)}")
expect("sp_field：有被照亮的金色連線（stroke-width=5）", 'stroke="#DDA642" stroke-width="5"' in a, "")
expect("sp_field：暗處的連線比亮處細（stroke-width=2）", 'stroke-width="2"' in a, "")

# 底部窄帶：點數 = 張數；走過的連線是金色、現在這張有一圈光
strip = R.sp_strip(3, 9)
expect("sp_strip：9 張 → 9 個點（走過 2 個實心、現在 1 個金色、未到 6 個空心）",
       strip.count('r="6" fill="#076876"') == 2 and strip.count('r="10" fill="#DDA642"') == 1 and strip.count('r="6" fill="none"') == 6, strip[:200])
expect("sp_strip：走過的連線是金色（2 條）", strip.count('stroke="#DDA642" stroke-width="4"') == 2, "")

# 封面副標接在標題下面；標題固定在 y=810
_, _, h1 = render([{"layout": "cover", "title": "先問，再答？", "body": "示範副標"}])
expect("封面標題固定在 y=810", 'id="title" style="top:810px"' in h1, "")

# 成對橫條圖：有小數的圖，整數值也要顯示一位小數（80.0，不是 80；2026-10-24 讀者抓到圖上 80% 與主標 80.0% 不一致）
_, _, hp = render([{"layout": "chart_bars", "title": "成對橫條圖", "body": "示範補充。", "unit": "%", "legend": ["甲", "乙"], "axis_max": 100,
                    "bars": [{"name": "一", "value": 35.7, "value2": 36.2}, {"name": "二", "value": 69.4, "value2": 80.0}]}])
expect("成對橫條圖有小數時，80.0 顯示成「80.0%」", "80.0%" in hp and ">80%<" not in hp, "")
_, _, hq = render([{"layout": "chart_bars", "title": "成對橫條圖", "body": "示範補充。", "unit": "%", "legend": ["甲", "乙"], "axis_max": 100,
                    "bars": [{"name": "一", "value": 30, "value2": 40}, {"name": "二", "value": 60, "value2": 80}]}])
expect("成對橫條圖全是整數時維持原樣（80%）", "80%" in hq and "80.0%" not in hq, "")

# 故意做壞
code, out, _ = render([{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}])
expect("故意做壞：補充文字太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "cover", "title": "實力差四倍但是弱的那隊還有兩成機率會爆冷而且這個差距讓人意外不已", "body": "示範副標"}])
expect("故意做壞：封面主標太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "series_map", "title": "想接著看？", "current": "不存在的觀念", "nav": "x"}])
expect("故意做壞：系列地圖的 current 不在成員裡 → 報錯", code != 0, out)

print("\n全部通過" if not fails else f"\n失敗 {len(fails)} 項：{fails}")
raise SystemExit(1 if fails else 0)
