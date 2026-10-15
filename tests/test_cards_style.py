"""一式四份系列（series/persona-aware-d2s，style: cards）的回歸測試：樣張的每個版型都要通過程式 B；
系列地圖在三則各自的位置都要通過；故意做壞的（補充文字長到壓進小投影片區）必須被抓到。
用法（repo 根目錄）：uv run python tests/test_cards_style.py
spec 放暫存資料夾，不碰 out/；concept 借用系列成員，--force 只渲染暫存資料夾。
"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
MEMBERS = ["persona-d2s-task-and-pipeline", "persona-d2s-training-design-flaws", "persona-d2s-what-to-borrow"]
fails = []


def render(slides, concept=MEMBERS[0]):
    doc = {"series": "persona-aware-d2s", "concept": concept, "slides": slides}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(RENDER), str(p), "--force"], capture_output=True, text=True, cwd=ROOT)
        return r.returncode, r.stdout + r.stderr


def expect(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail[:300]}]" if not ok else ""))
    if not ok:
        fails.append(name)


DECK = [
    {"layout": "cover", "title": "同一份文件，能長出[[四種]]簡報嗎？", "body": "示範副標第一行\n示範副標第二行"},
    {"layout": "context", "title": "先認識兩個條件", "body": "示範脈絡：", "rows": [["受眾", "專家或非專家"], ["長度", "長版或短版"]], "key_w": 170},
    {"layout": "text", "title": "文字版型：光在下方分成四股", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "流程圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "text", "title": "文字版型的第二張", "body": "金點換到下一股。"},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
]

for mi, c in enumerate(MEMBERS):
    smap = {"layout": "series_map", "title": "一次看完這個系列", "current": c, "nav": "完整文章：datasciocean.com/paper-intro/persona-aware-d2s"}
    code, out = render(DECK + [smap], c)
    expect(f"一式四份樣張（第 {mi + 1} 則）每個版型通過程式 B", code == 0 and "9/9 張通過" in out, out)

# 沒有圖註的橫條圖：空的圖註框不能被程式 B 誤判（render.py 在填入後移除空框）
nonote = [{"layout": "chart_bars", "title": "沒有圖註的橫條圖", "subs_inline": True, "body": "示範補充。", "unit": "%",
           "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]}]
code, out = render(nonote)
expect("沒有圖註的橫條圖通過程式 B（空圖註框不誤判）", code == 0 and "1/1 張通過" in out, out)

bad = [{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}]
code, out = render(bad)
expect("故意做壞：補充文字長到壓進小投影片區 → 抓得到", code != 0 and "FAIL" in out, out)

bad = [{"layout": "cover", "title": "同一份文件怎麼長出專家版和外行版簡報", "body": "示範副標"}]
code, out = render(bad)
expect("故意做壞：直切版面的封面標題是沒有標點的長串 → 溢出抓得到", code != 0 and "文字框無橫向溢出" in out, out)

bad = [{"layout": "text", "title": "標題，很長的標題文字，很長的標題文字，很長的標題文字，很長的標題文字，很長的標題文字，很長的標題文字", "body": "示範"}]
code, out = render(bad)
expect("故意做壞：直切版面的文字頁標題超過三行 → 抓得到", code != 0 and "標題最多 3 行" in out, out)

print(f"\n{len(fails)} 個失敗" if fails else "\n全部通過")
raise SystemExit(1 if fails else 0)
