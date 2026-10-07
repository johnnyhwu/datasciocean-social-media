"""Stage 2 的狀態：每個觀念各格式做到哪、發布紀錄、待回補清單。

觀念卡在 concept-wiki submodule 裡唯讀，所以「這個觀念的 IG／Threads 做到哪、發了沒」記在本 repo 的
`state/<concept-id>.yaml`（人看得懂、git 可追）。

用法（repo 根目錄）：
  uv run python .claude/skills/make-social-post/scripts/state.py status
      列出每個觀念的論點、各格式狀態（新格式與沒有狀態檔的觀念都算 not_tried）
  uv run python .claude/skills/make-social-post/scripts/state.py ready <concept> <format> <pack-dir>
      發布包完成、等人確認後發布（存量就是 ready 的數量）
  uv run python .claude/skills/make-social-post/scripts/state.py unsuitable <concept> <format> "<原因>"
      這個格式做不出合格版本（pipeline 不再自動嘗試；觀念卡不動）
  uv run python .claude/skills/make-social-post/scripts/state.py record <concept> <format> --url URL
        --published-at 2026-10-05T20:00 [--series-id ID] [--hook-type 樣態] [--mentions a,b]
      寫回發布紀錄；狀態改為 published，並重算回補清單。API 發佈（--confirm）成功後會自動呼叫，只有人手動發布時才需要手動執行
  uv run python .claude/skills/make-social-post/scripts/state.py backfill
      重新產生 state/backfill.md（程式產生，不手改）

狀態值：not_tried | ready | published | unsuitable。
posts[] 必須記錄的識別碼（成效分析系統事後很難補）：觀念 id、系列 id、格式、網址、發布時間、hook 樣態、提及的觀念。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

import cardlib as W

STATE = W.ROOT / "state"
FORMATS = ["ig_carousel", "threads_thread"]
STATUSES = {"not_tried", "ready", "published", "unsuitable"}
BACKFILL_HOW = {
    "ig_carousel": "IG：修改 caption，補一行延伸連結（投影片發布後不能新增或刪除）",
    "threads_thread": "Threads：在原串文下新增一則回覆，補上完整連結（發文後可編輯的時間很短，不能靠編輯）",
}


def path_of(concept: str) -> Path:
    return STATE / f"{concept}.yaml"


def load(concept: str) -> dict:
    p = path_of(concept)
    d = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    d = d or {}
    d.setdefault("concept", concept)
    d.setdefault("formats", {})
    d.setdefault("posts", [])
    return d


def save(d: dict) -> None:
    STATE.mkdir(exist_ok=True)
    path_of(d["concept"]).write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False), encoding="utf-8")


def concept_ids() -> list[str]:
    return [c.front["id"] for c in W.load_all_cards()]


def status() -> None:
    cards = {c.front["id"]: c for c in W.load_all_cards()}
    print("| 觀念 | 一句話論點 | " + " | ".join(FORMATS) + " |")
    print("|---|---|" + "---|" * len(FORMATS))
    for cid, c in cards.items():
        d = load(cid)
        thesis = next(x["text"] for x in c.claims if x["role"] == "thesis")[:40]
        cells = [(d["formats"].get(f) or {}).get("status", "not_tried") for f in FORMATS]
        print(f"| {cid} | {thesis} | " + " | ".join(cells) + " |")
    ready = sum(1 for cid in cards if any((v or {}).get("status") == "ready" for v in load(cid)["formats"].values()))
    print(f"\n存量（ready）：{ready} 則")


def set_format(concept: str, fmt: str, **fields) -> None:
    assert concept in concept_ids(), f"觀念不存在：{concept}"
    assert fields["status"] in STATUSES
    d = load(concept)
    d["formats"][fmt] = fields
    save(d)


def record(concept: str, fmt: str, url: str, published_at: str, series_id: str | None, hook_type: str | None,
           mentions: list[str]) -> None:
    d = load(concept)
    pid = f"{concept}:{fmt}"
    d["posts"] = [p for p in d["posts"] if p["post_id"] != pid]
    d["posts"].append({"post_id": pid, "format": fmt, "series_id": series_id, "url": url,
                       "published_at": published_at, "hook_type": hook_type, "mentions": mentions, "backfilled": []})
    d["formats"][fmt] = {"status": "published"}
    save(d)
    backfill()


def backfill() -> None:
    """已發布、但缺少「之後才發布的同系列或提及觀念」連結的貼文。"""
    series_members: dict[str, list[str]] = {}
    for f in W.SERIES_DIR.glob("*/series.md"):
        s = yaml.safe_load(re.match(r"^---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S).group(1))
        series_members[s["id"]] = [m["concept"] for m in s["members"]]
    states = {cid: load(cid) for cid in concept_ids()}
    first_pub: dict[str, str] = {}   # 觀念 -> 最早的發布時間
    for cid, d in states.items():
        times = [p["published_at"] for p in d["posts"]]
        if times:
            first_pub[cid] = min(times)
    lines = ["# 待回補連結清單（程式產生，不手改）", "",
             "已發布、但還沒補上「之後才發布的相關貼文」連結的貼文。做完回補後，在該貼文的 `state/<觀念>.yaml` 的 `backfilled` 加上被補的觀念 id。", ""]
    n = 0
    for cid, d in states.items():
        for p in d["posts"]:
            targets = set(p.get("mentions") or [])
            if p.get("series_id"):
                targets |= set(series_members.get(p["series_id"], []))
            targets.discard(cid)
            for t in sorted(targets):
                if t in first_pub and first_pub[t] > p["published_at"] and t not in (p.get("backfilled") or []):
                    n += 1
                    lines.append(f"- [ ] `{p['post_id']}`（{p['url']}）需補 → `{t}`（{first_pub[t]} 發布）｜{BACKFILL_HOW[p['format']]}")
    if n == 0:
        lines.append("（目前沒有待回補項目）")
    STATE.mkdir(exist_ok=True)
    (STATE / "backfill.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote state/backfill.md（{n} 項）")


def main(a: list[str]) -> int:
    cmd = a[0] if a else "status"
    if cmd == "status":
        status()
    elif cmd == "ready":
        set_format(a[1], a[2], status="ready", pack=a[3])
    elif cmd == "unsuitable":
        set_format(a[1], a[2], status="unsuitable", reason=a[3])
    elif cmd == "record":
        opt = lambda k: a[a.index(k) + 1] if k in a else None
        record(a[1], a[2], opt("--url"), opt("--published-at"), opt("--series-id"), opt("--hook-type"),
               (opt("--mentions") or "").split(",") if opt("--mentions") else [])
    elif cmd == "backfill":
        backfill()
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
