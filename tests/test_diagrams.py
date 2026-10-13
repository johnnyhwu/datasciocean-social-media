"""示意圖版型（layout: diagram）的回歸測試：正確的圖要通過程式 B；故意做壞的（文字塞不進框、放不下）必須被抓到。
用法（repo 根目錄）：uv run python tests/test_diagrams.py
用 series/skillopt 的模板（真實系列），spec 放暫存資料夾，不碰 out/。
"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
fails = []


def render(slide):
    doc = {"series": "skillopt", "concept": "skillopt-overview", "slides": [slide]}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(RENDER), str(p), "--force"], capture_output=True, text=True, cwd=ROOT)   # --force：測試借用的 concept 之後可能已發布（render 預設拒絕已發布的貼文），這裡只渲染暫存資料夾，不碰真貼文
        return r.returncode, r.stdout + r.stderr


def expect(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail[:200]}]" if not ok else ""))
    if not ok:
        fails.append(name)


D = lambda kind, **kw: {"layout": "diagram", "kind": kind, "title": "測試標題", "body": "測試補充。", **kw}

code, out = render(D("flow", nodes=[{"text": "第一步", "sub": "說明"}, {"text": "第二步"}],
                     outcomes=[{"text": "收下", "tone": "good"}, {"text": "丟掉"}], loop="每一輪再檢查一次"))
expect("正確的流程圖通過程式 B", code == 0, out)

code, out = render(D("range", ranges=[{"name": "甲", "lo": 100, "hi": 100}, {"name": "乙", "lo": 56, "hi": 74, "emph": True}], unit="%", axis_max=100))
expect("正確的區間條通過程式 B（含比例檢查）", code == 0 and "PASS" in out, out)

code, out = render(D("dumbbell", points=[{"name": "前", "value": 22.1}, {"name": "後", "value": 81.8}], ref={"name": "參考", "value": 80.4}, unit="分", axis_max=100))
expect("正確的前後對比圖通過程式 B（含位置檢查）", code == 0, out)

code, out = render(D("funnel", nodes=[{"text": "上"}, {"text": "中"}, {"text": "這是一段沒有任何標點而且非常非常長的底層文字讓它塞不進漏斗的最後一層"}]))
expect("故意做壞：文字塞不進框 → 抓得到", code != 0 and "框內文字不超出框" in out, out)

code, out = render(D("compare", columns=[{"head": "甲", "items": [{"text": "很長的項目" * 6, "sub": "很長的說明" * 8} for _ in range(8)]}, {"head": "乙", "items": [{"text": "x"}]}]))
expect("故意做壞：圖太高放不下 → 報錯", code != 0 and "放不下" in out, out)

code, out = render(D("batches", count=20, group=8, nodes=[{"text": "一個池子"}, {"text": "每組各自診斷"}]))
expect("正確的切組圖通過程式 B", code == 0, out)
code, out = render(D("decay", start=4, end=2, unit="處", axis_max=5, nodes=[{"text": "初期"}, {"text": "後期"}]))
expect("正確的遞減曲線通過程式 B", code == 0, out)
code, out = render(D("stops", heads=["太小", "太大"], nodes=[{"text": "甲", "sub": "說明"}, {"text": "乙", "emph": True}, {"text": "丙"}]))
expect("正確的三個停靠點通過程式 B", code == 0, out)
code, out = render(D("stops", nodes=[{"text": "很長的項目" * 12, "sub": "很長的說明" * 14} for _ in range(3)]))
expect("故意做壞：停靠點的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("batches", count=20, group=8, nodes=[{"text": "很長的池子說明" * 20}, {"text": "很長的每組說明" * 20}]))
expect("故意做壞：切組圖的標籤太長放不下 → 報錯", code != 0 and "放不下" in out, out)

code, out = render(D("fan", heads=["第 1 組", "第 2 組", "第 3 組"], nodes=[{"text": "各組同時診斷"}, {"text": "彙整成一份", "sub": "再往下走"}]))
expect("正確的匯整圖通過程式 B", code == 0, out)
code, out = render(D("fan", heads=["很長的組名" * 6, "乙", "丙"], nodes=[{"text": "很長的說明" * 40}, {"text": "很長的結果" * 30, "sub": "很長的小字" * 30}]))
expect("故意做壞：匯整圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

code, out = render(D("peaks", nodes=[{"text": "甲線"}, {"text": "乙線"}, {"text": "重合"}]))
expect("正確的最高點重合圖通過程式 B", code == 0, out)
code, out = render(D("quad", nodes=[{"text": "進步"}, {"text": "退步", "sub": "重點", "emph": True}, {"text": "持續失敗"}, {"text": "穩定成功"}]))
expect("正確的四格圖通過程式 B", code == 0, out)
code, out = render(D("locked", heads=["步驟級修改", "Epoch 邊界的流程"], nodes=[{"text": "best_skill.md"}, {"text": "受保護區塊：戰略筆記"}]))
expect("正確的受保護區塊圖通過程式 B", code == 0, out)
code, out = render(D("quad", nodes=[{"text": "很長的格子" * 12, "sub": "很長的說明" * 15} for _ in range(4)]))
expect("故意做壞：四格圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("locked", heads=["很長的來源" * 10, "乙"], nodes=[{"text": "文件" * 30}, {"text": "很長的區塊說明" * 30}]))
expect("故意做壞：受保護區塊圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

print("\n全部通過" if not fails else f"\n{len(fails)} 項失敗")
raise SystemExit(1 if fails else 0)
