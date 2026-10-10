"""批次層檢查（batch_check）與狀態／回補（state）的回歸測試。

用法（repo 根目錄）：uv run python tests/test_state_and_batch.py
測試資料在 tests/fixtures/；state 的測試用暫存目錄，不會動到 state/ 裡的真實資料。
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 測試資料放在 tests/fixtures/（第一次實跑的兩則貼文、系列檔與對應的觀念卡），不依賴真實的 out/、series/、concept-wiki/
import os
FX = Path(__file__).resolve().parent / "fixtures"
os.environ["DSO_CONCEPT_WIKI"] = str(FX / "concept-wiki")
os.environ["DSO_SERIES_DIR"] = str(FX / "series")
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))

import batch_check as BC  # noqa: E402
import state as S  # noqa: E402

fails: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


A = FX / "out/jev-teardown/jev-overview"
B = FX / "out/jev-teardown/confound-three-questions"


def run_batch(tweak_a=None, tweak_b=None, hash_b=None) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for name, src, tw, h in (("a", A, tweak_a, None), ("b", B, tweak_b, hash_b)):
            dst = Path(d) / name
            dst.mkdir()
            spec = json.loads((src / "spec.json").read_text(encoding="utf-8"))
            if tw:
                tw(spec)
            (dst / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            cb = json.loads((src / "checks-b.json").read_text(encoding="utf-8"))
            if h:
                cb["template_hash"] = h
            (dst / "checks-b.json").write_text(json.dumps(cb), encoding="utf-8")
            paths.append(str(dst / "spec.json"))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = BC.main(paths)
        return rc, buf.getvalue()


rc, out = run_batch()
check("batch：兩則正確貼文通過（存量不足只是 WARN）", rc == 0, out)
rc, out = run_batch(tweak_b=lambda s: s["hook"].update(style=json.loads((A / "spec.json").read_text(encoding="utf-8"))["hook"]["style"]))
check("batch：相鄰 hook 樣態相同 → 擋下", rc == 1 and "hook 樣態相同" in out)
rc, out = run_batch(hash_b="deadbeef0000")
check("batch：同系列模板 hash 不同 → 擋下", rc == 1 and "不同版模板" in out)
_orig_pf = BC.W.published_formats
BC.W.published_formats = lambda c: ["ig_carousel", "threads_thread"] if c == json.loads((B / "spec.json").read_text(encoding="utf-8"))["concept"] else _orig_pf(c)
rc, out = run_batch(hash_b="deadbeef0000")
BC.W.published_formats = _orig_pf
check("batch：已發布的貼文模板 hash 不同 → 不比對（不重渲已發布的貼文）", rc == 0 and "不同版模板" not in out, out)
rc, out = run_batch(tweak_a=lambda s: s["threads"]["last"].update(text=s["threads"]["last"]["text"].replace("看效能對比數字之前，先問三個問題", "亂寫的標題")))
check("batch：串文的同系列標題與 planned_title 不一致 → 擋下", rc == 1 and "planned_title" in out)

# ---------------------------------------------------------------- state
with tempfile.TemporaryDirectory() as d:
    S.STATE = Path(d)
    with contextlib.redirect_stdout(io.StringIO()):
        S.record("jev-overview", "ig_carousel", "https://ig/1", "2026-10-05T20:00", "jev-teardown", "情境痛點", ["confound-three-questions"])
    check("state：發布一則後，沒有更晚發布的相關貼文 → 沒有回補項目", "目前沒有待回補項目" in (Path(d) / "backfill.md").read_text(encoding="utf-8"))
    with contextlib.redirect_stdout(io.StringIO()):
        S.record("confound-three-questions", "ig_carousel", "https://ig/2", "2026-10-06T20:00", "jev-teardown", "反直覺斷言", [])
    text = (Path(d) / "backfill.md").read_text(encoding="utf-8")
    check("state：後發布的同系列貼文 → 先發布的那則出現在回補清單", "jev-overview:ig_carousel" in text and "confound-three-questions" in text and "修改 caption" in text)
    y = S.load("jev-overview")
    y["posts"][0]["backfilled"] = ["confound-three-questions"]
    S.save(y)
    with contextlib.redirect_stdout(io.StringIO()):
        S.backfill()
    check("state：標記已回補後，從清單消失", "目前沒有待回補項目" in (Path(d) / "backfill.md").read_text(encoding="utf-8"))
    p = S.load("jev-overview")["posts"][0]
    check("state：posts[] 記錄了全部識別碼", all(p.get(k) for k in ("post_id", "format", "series_id", "url", "published_at", "hook_type")) and "mentions" in p)
    check("state：發布後格式狀態是 published", S.load("jev-overview")["formats"]["ig_carousel"]["status"] == "published")
    with contextlib.redirect_stdout(io.StringIO()):
        S.set_format("schema-valid-not-correct", "threads_thread", status="unsuitable", reason="卡上內容不夠撐串文")
    check("state：unsuitable 附原因", S.load("schema-valid-not-correct")["formats"]["threads_thread"]["reason"])

print(f"\n{'全部通過' if not fails else f'{len(fails)} 項失敗：' + '; '.join(fails)}")
sys.exit(1 if fails else 0)
