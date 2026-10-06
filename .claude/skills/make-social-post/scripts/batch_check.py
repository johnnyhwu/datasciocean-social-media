"""批次層檢查（跨貼文）。一批貼文要交給人最後確認之前跑一次。

用法：uv run python .claude/skills/make-social-post/scripts/batch_check.py <spec.json> [<spec.json> ...]
      參數順序 = 預計的發文順序。
檢查（references/batch-and-publish.md §4）：
  1. 相鄰兩則的 hook 樣態不同
  2. 相鄰兩則若屬不同系列，系列封面色不同
  3. 同一系列的貼文用同一版模板（template_hash 相同；讀各貼文資料夾的 checks-b.json）
  4. Threads 最後一則與系列地圖裡出現的「同系列：…」標題，必須等於該系列某個成員的 planned_title
  5. 存量：已有發布包（state 為 ready）的觀念數量低於 min_stock 就提醒；為 0 就暫停發文
結束碼：1 有 ERROR；存量提醒是 WARN，不影響結束碼（存量不夠時是「暫停」而不是「失敗」）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

import cardlib as W

P = W.load_params()


def load_series(sid: str) -> dict:
    t = (W.SERIES_DIR / f"{sid}.md").read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---", t, re.S).group(1))


def main(specs: list[str]) -> int:
    docs = [(Path(p), json.loads(Path(p).read_text(encoding="utf-8"))) for p in specs]
    err, warn = [], []
    series = {d["series"]: load_series(d["series"]) for _, d in docs}

    for (pa, a), (pb, b) in zip(docs, docs[1:]):
        if a["hook"]["style"] == b["hook"]["style"]:
            err.append(f"相鄰兩則 hook 樣態相同（{a['hook']['style']}）：{a['concept']} → {b['concept']}")
        if a["series"] != b["series"] and series[a["series"]]["color"] == series[b["series"]]["color"]:
            err.append(f"相鄰系列封面色相同（{series[a['series']]['color']}）：{a['series']} → {b['series']}")

    by_series: dict[str, set] = {}
    for pa, a in docs:
        cb = pa.parent / "checks-b.json"
        if not cb.exists():
            err.append(f"{a['concept']}：沒有 checks-b.json（還沒渲染或程式 B 沒跑）")
            continue
        by_series.setdefault(a["series"], set()).add(json.loads(cb.read_text(encoding="utf-8"))["template_hash"])
    for sid, hashes in by_series.items():
        if len(hashes) > 1:
            err.append(f"系列 {sid} 的貼文用了不同版模板：{sorted(hashes)}")

    for pa, a in docs:
        titles = {m["planned_title"] for m in series[a["series"]]["members"]}
        for line in a["threads"]["last"]["text"].splitlines():
            if line.startswith("同系列："):
                t = re.sub(r"（尚未發布）$|（.*?）$", "", line[len("同系列："):]).strip()
                if t not in titles:
                    err.append(f"{a['concept']}：Threads 最後一則的同系列標題與 planned_title 不一致：{t!r}")

    ready = 0
    for f in (W.ROOT / "state").glob("*.yaml"):
        s = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if any((v or {}).get("status") == "ready" for v in (s.get("formats") or {}).values()):
            ready += 1
    if ready == 0:
        warn.append("存量 0：沒有任何待發布的貼文，暫停發文（寧可跳過一天，也不降低審查標準）")
    elif ready < P["min_stock"]:
        warn.append(f"存量 {ready} 則，低於 min_stock={P['min_stock']}")

    print(f"== 批次檢查 {len(docs)} 則: {'FAIL' if err else 'PASS'}（ERROR {len(err)}，WARN {len(warn)}）")
    for e in err:
        print("  ERROR", e)
    for w in warn:
        print("  WARN ", w)
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
