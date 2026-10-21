"""獨立貼文（沒有系列）的回歸測試：standalone/decision-transformer-reward-conditioning（style: horizon，地平線）。
樣張的每個版型都要通過程式 B；沒有系列標籤；延伸閱讀（series_map）的 items 要查得到標題；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_standalone_style.py
spec 放暫存資料夾，不碰 out/；--force 只渲染暫存資料夾。
"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
CONCEPT = "decision-transformer-reward-conditioning"
fails = []


def render(slides, concept=CONCEPT):
    doc = {"series": None, "concept": concept, "slides": slides}
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
    {"layout": "cover", "title": "先許願要拿幾分，AI 再回推[[該怎麼走]]？", "body": "示範副標第一行\n示範副標第二行"},
    {"layout": "context", "title": "先認識兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "text", "title": "文字版型：底部一條地平線", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "流程圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "text", "title": "文字版型的第二張", "body": "淡太陽往右移一格。"},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "想接著看？", "items": ["persona-d2s-training-design-flaws"], "nav": "完整文章：datasciocean.com/paper-intro/persona-aware-d2s"},
]

code, out, html = render(DECK)
expect("地平線樣張的每個版型通過程式 B（9 張）", code == 0 and "9/9 張通過" in out, out)
expect("獨立貼文沒有系列標籤（HTML 裡沒有 class tag）", 'class="t abs tag"' not in html, "")
expect("延伸閱讀列出 planned_title", "80 筆資料訓出來的模型，能信嗎？" in html, "")

# 封面副標固定在地平線下面（不接在標題後面）：標題一行或兩行，副標位置不變
one = [{"layout": "cover", "title": "先許願，再回推？", "body": "示範副標"}]
two = [{"layout": "cover", "title": "先許願要拿幾分，AI 再回推該怎麼走？", "body": "示範副標"}]
_, _, h1 = render(one)
_, _, h2 = render(two)
expect("封面副標位置固定（SUB_TOP = 地平線 + 70）", "top:770px" in h1 and "top:770px" in h2, "")

bad = [{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}]
code, out, _ = render(bad)
expect("故意做壞：補充文字太長 → 抓得到", code != 0 and "FAIL" in out, out)

bad = [{"layout": "cover", "title": "先許願要拿幾分之後讓模型自己回推該怎麼走才能拿到那個分數", "body": "示範副標"}]
code, out, _ = render(bad)
expect("故意做壞：封面主標超過兩行 → 抓得到", code != 0 and "FAIL" in out, out)

bad = [{"layout": "series_map", "title": "想接著看？", "items": ["not-a-real-concept"], "nav": "示範"}]
code, out, _ = render(bad)
expect("故意做壞：延伸閱讀的觀念不在任何系列 → 渲染報錯", code != 0, out)

print("\n全部通過" if not fails else f"\n失敗 {len(fails)} 項：{fails}")
raise SystemExit(1 if fails else 0)
