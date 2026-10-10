"""渲染的數字與單位綁定、程式 B 的「數字與單位不拆行」檢查的回歸測試。

做壞的版本：用 DSO_NO_NUMBIND=1 關掉綁定，標題「串接 1.87 秒」會在行尾拆成「1.87／秒」，程式 B 必須抓到；
正常版本（有綁定）必須通過這一項。用 jev-cascade 系列的模板（Chromium 要在 .playwright-browsers/）。
用法（repo 根目錄）：uv run python tests/test_render_numunit.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
CHECK = "標題的數字與單位不拆成兩行"
SPEC = {
    "series": "jev-cascade", "concept": "render-test", "lang": "zh-TW",
    "slides": [{
        "layout": "chart_bars", "title": "中位延遲：串接 1.87 秒，GPT-6 單獨 1.91 秒", "body": "前瞻實驗兩個任務合計",
        "unit": "秒", "note": "延遲單位：秒",
        "bars": [{"name": "串接", "subs": ["JEV 加轉出的題"], "value": 1.87, "emphasize": True},
                 {"name": "GPT-6 單獨", "subs": ["單獨判"], "value": 1.91}],
    }],
}


HYPHEN_SPEC = {
    "series": "jev-cascade", "concept": "render-test", "lang": "zh-TW",
    "slides": [{"layout": "context", "title": "一個便宜又快，一個難題強但費用高",
                "body": "JEV 是 TypeSafe AI 的託管模型，只輸出判決與機率，便宜、快；GPT-6 是推理型\u00a0Judge，難題上比較強，但費用高、速度慢。"}],
}


def run_hyphen(no_bind):
    """手動把長串綁成不斷行，瀏覽器只好從「GPT-6」的連字號處斷行；關掉綁定（DSO_NO_NUMBIND=1）時程式 B 必須抓到。
    開著綁定時，render 在連字號後加不斷行字元（U+2060），「GPT-6」不再被拆開，這一項必須通過。"""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(HYPHEN_SPEC, ensure_ascii=False), encoding="utf-8")
        env = dict(os.environ)
        env.pop("DSO_NO_NUMBIND", None)
        if no_bind:
            env["DSO_NO_NUMBIND"] = "1"
        subprocess.run(["uv", "run", "python", str(RENDER), str(p)], capture_output=True, text=True, cwd=ROOT, env=env)
        rep = json.loads((Path(d) / "checks-b.json").read_text(encoding="utf-8"))
        return {c["name"]: c["ok"] for c in rep["slides"][0]["checks"]}


PAIRS_SPEC = {
    "series": "jev-cascade", "concept": "render-test", "lang": "zh-TW",
    "slides": [{
        "layout": "chart_bars", "title": "費用跟著轉出比例走", "body": "每組兩條橫條，同一個比例尺。",
        "unit": "%", "axis_max": 100, "legend": ["轉出比例", "費用"], "note": "費用，GPT-6 單獨 = 100%",
        "bars": [{"name": "甲", "value": 25, "value2": 27}, {"name": "乙", "value": 65, "value2": 67},
                 {"name": "丙", "value": 68, "value2": 69}, {"name": "丁", "value": 89, "value2": 91}],
    }],
}


def run_pairs():
    """成對橫條圖（value2）：兩個量的橫條用同一個 0 起點與比例尺，程式 B 全部要過（含長度與數值成正比、不重疊、不超出下緣）。"""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(PAIRS_SPEC, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["uv", "run", "python", str(RENDER), str(p)], capture_output=True, text=True, cwd=ROOT)
        rep = json.loads((Path(d) / "checks-b.json").read_text(encoding="utf-8"))
        return {c["name"]: c["ok"] for c in rep["slides"][0]["checks"]}


def est_lines_closing_quote():
    """表格估算行數：「」』）後面也可以斷行（瀏覽器實測會在「…」後換行），估少了列高會壓到下一條橫線。"""
    sys.path.insert(0, str(RENDER.parent))
    import render
    return render.est_lines("「可以掉 2%」是使用者自己訂的容忍度，不是模型替你算出來的", 16.9)


def run(no_bind):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(SPEC, ensure_ascii=False), encoding="utf-8")
        env = dict(os.environ)
        env.pop("DSO_NO_NUMBIND", None)
        if no_bind:
            env["DSO_NO_NUMBIND"] = "1"
        subprocess.run(["uv", "run", "python", str(RENDER), str(p)], capture_output=True, text=True, cwd=ROOT, env=env)
        rep = json.loads((Path(d) / "checks-b.json").read_text(encoding="utf-8"))
        return {c["name"]: c["ok"] for c in rep["slides"][0]["checks"]}


def main():
    fails = 0
    broken = run(True)
    caught = CHECK in broken and broken[CHECK] is False
    fails += not caught
    print(("PASS " if caught else "FAIL ") + "抓得到：關掉綁定時，數字與單位被拆成兩行")
    good = run(False)
    ok = good.get(CHECK) is True and all(good.values())
    fails += not ok
    print(("PASS " if ok else "FAIL ") + "正常版本（有綁定）程式 B 全過" + ("" if ok else f"  {good}"))
    hy = run_hyphen(True)
    caught = hy.get("補充的數字與單位不拆成兩行") is False
    fails += not caught
    print(("PASS " if caught else "FAIL ") + "抓得到：關掉綁定時，「GPT-6」被連字號拆成兩行")
    hy = run_hyphen(False)
    ok = hy.get("補充的數字與單位不拆成兩行") is True
    fails += not ok
    print(("PASS " if ok else "FAIL ") + "正常版本（連字號後不斷行）：「GPT-6」不被拆開")
    pr = run_pairs()
    ok = bool(pr) and all(pr.values()) and "橫條長度與數值成正比、軸從 0 起" in pr
    fails += not ok
    print(("PASS " if ok else "FAIL ") + "成對橫條圖：程式 B 全過（含比例與軸從 0 起）" + ("" if ok else f"  {pr}"))
    n = est_lines_closing_quote()
    ok = n >= 3
    fails += not ok
    print(("PASS " if ok else "FAIL ") + f"表格行數估算：「」後可斷行（估 {n} 行，實測 3 行）")
    print(f"\n{'全部通過' if not fails else f'{fails} 項失敗'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
