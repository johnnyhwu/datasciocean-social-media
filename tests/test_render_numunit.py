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


def run_hyphen():
    """手動把長串綁成不斷行，瀏覽器只好從「GPT-6」的連字號處斷行；程式 B 必須抓到。"""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(HYPHEN_SPEC, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["uv", "run", "python", str(RENDER), str(p)], capture_output=True, text=True, cwd=ROOT)
        rep = json.loads((Path(d) / "checks-b.json").read_text(encoding="utf-8"))
        return {c["name"]: c["ok"] for c in rep["slides"][0]["checks"]}


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
    hy = run_hyphen()
    caught = hy.get("補充的數字與單位不拆成兩行") is False
    fails += not caught
    print(("PASS " if caught else "FAIL ") + "抓得到：「GPT-6」被連字號拆成兩行")
    print(f"\n{'全部通過' if not fails else f'{fails} 項失敗'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
