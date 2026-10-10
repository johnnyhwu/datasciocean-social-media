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
      重新產生 state/backfill.md（程式產生，不手改；只列 Threads，回補由 threads_publish.py backfill 做）

狀態值：not_tried | ready | published | unsuitable。
posts[] 必須記錄的識別碼（成效分析系統事後很難補）：觀念 id、系列 id、格式、網址、發布時間、hook 樣態、提及的觀念。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

import cardlib as W

STATE = W.STATE_DIR
FORMATS = ["ig_carousel", "threads_thread"]
STATUSES = {"not_tried", "ready", "published", "unsuitable"}
# 回補只做 Threads（2026-10-10 人決定）：IG 的 API 不能改 caption、人也不手動做，所以 IG 不列回補；
# 限時動態、精選集、置頂同樣不做。Threads 由 Claude 用 API 在原串文後面接一則回覆（threads_publish.py backfill）。
BACKFILL_FORMATS = ["threads_thread"]


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


def also_of(concept: str) -> list[str]:
    """這個觀念的貼文併入了哪些其他卡（系列檔成員的 also）。併入的卡不單獨發文，狀態跟著主卡走。"""
    for sf in W.SERIES_DIR.glob("*/series.md") if W.SERIES_DIR.exists() else []:
        s = yaml.safe_load(re.match(r"^---\n(.*?)\n---", sf.read_text(encoding="utf-8"), re.S).group(1))
        for m in s.get("members") or []:
            if m["concept"] == concept:
                return list(m.get("also") or [])
    return []


def concept_ids() -> list[str]:
    return [c.front["id"] for c in W.load_all_cards()]


def status() -> None:
    cards = {c.front["id"]: c for c in W.load_all_cards()}
    print("| 觀念 | 一句話論點 | " + " | ".join(FORMATS) + " |")
    print("|---|---|" + "---|" * len(FORMATS))
    for cid, c in cards.items():
        d = load(cid)
        thesis = next(x["text"] for x in c.claims if x["role"] == "thesis")[:40]
        cells = [(d["formats"].get(f) or {}).get("status", "not_tried") + (
            f"（併入 {d['formats'][f]['merged_into']}）" if (d["formats"].get(f) or {}).get("merged_into") else "") for f in FORMATS]
        print(f"| {cid} | {thesis} | " + " | ".join(cells) + " |")
    ready = sum(1 for cid in cards if any((v or {}).get("status") == "ready" and not (v or {}).get("merged_into")
                                          for v in load(cid)["formats"].values()))
    print(f"\n存量（ready）：{ready} 則")


def set_format(concept: str, fmt: str, **fields) -> None:
    assert concept in concept_ids(), f"觀念不存在：{concept}"
    assert fields["status"] in STATUSES
    d = load(concept)
    d["formats"][fmt] = fields
    save(d)
    for other in also_of(concept):      # 併入的卡：狀態同步，標明併入哪一則（不計入存量）
        assert other in concept_ids(), f"併入的觀念不存在：{other}"
        o = load(other)
        o["formats"][fmt] = {**fields, "merged_into": concept}
        save(o)


def record(concept: str, fmt: str, url: str, published_at: str, series_id: str | None, hook_type: str | None,
           mentions: list[str]) -> None:
    d = load(concept)
    pid = f"{concept}:{fmt}"
    d["posts"] = [p for p in d["posts"] if p["post_id"] != pid]
    d["posts"].append({"post_id": pid, "format": fmt, "series_id": series_id, "url": url,
                       "published_at": published_at, "hook_type": hook_type, "mentions": mentions, "backfilled": []})
    d["formats"][fmt] = {"status": "published"}
    save(d)
    for other in also_of(concept):      # 併入的卡：標為已發布，但不另記一筆貼文（網址只記在主卡，回補清單才不會重複）
        o = load(other)
        o["formats"][fmt] = {"status": "published", "merged_into": concept}
        save(o)
    backfill()


def series_info() -> tuple[dict[str, list[str]], dict[str, str]]:
    """系列成員（發文順序）與各觀念的 planned_title。"""
    members: dict[str, list[str]] = {}
    titles: dict[str, str] = {}
    for f in W.SERIES_DIR.glob("*/series.md"):
        s = yaml.safe_load(re.match(r"^---\n(.*?)\n---", f.read_text(encoding="utf-8"), re.S).group(1))
        members[s["id"]] = [m["concept"] for m in s["members"]]
        for m in s["members"]:
            titles[m["concept"]] = m.get("planned_title", m["concept"])
    return members, titles


def backfill_items() -> list[dict]:
    """已發布、但缺少「之後才發布的同系列或提及觀念」連結的貼文（只列 BACKFILL_FORMATS）。
    每項：{post_id, concept, format, url, series_id, target, target_published_at}。"""
    series_members, _ = series_info()
    states = {cid: load(cid) for cid in concept_ids()}
    first_pub: dict[str, str] = {}   # 觀念 -> 最早的發布時間
    for cid, d in states.items():
        times = [p["published_at"] for p in d["posts"]]
        if times:
            first_pub[cid] = min(times)
    items = []
    for cid, d in states.items():
        for p in d["posts"]:
            if p["format"] not in BACKFILL_FORMATS:
                continue
            targets = set(p.get("mentions") or [])
            if p.get("series_id"):
                targets |= set(series_members.get(p["series_id"], []))
            targets.discard(cid)
            for t in sorted(targets):
                if t in first_pub and first_pub[t] > p["published_at"] and t not in (p.get("backfilled") or []):
                    items.append({"post_id": p["post_id"], "concept": cid, "format": p["format"], "url": p["url"],
                                  "series_id": p.get("series_id"), "target": t, "target_published_at": first_pub[t]})
    return items


def mark_backfilled(concept: str, fmt: str, targets: list[str]) -> None:
    """回補做完：在該貼文的 backfilled 加上被補的觀念 id，並重算清單。"""
    d = load(concept)
    for p in d["posts"]:
        if p["format"] == fmt:
            p["backfilled"] = sorted(set(p.get("backfilled") or []) | set(targets))
    save(d)
    backfill()


def backfill() -> None:
    lines = ["# 待回補連結清單（程式產生，不手改）", "",
             "已發布、但還沒補上「之後才發布的相關貼文」連結的 Threads 串文。**由 Claude 做**：`threads_publish.py backfill`（dry-run）→ 人說「發」→ `--confirm`，"
             "會在原串文最後一則下面接一則回覆，並自動標記已回補。IG 不回補（API 不能改 caption）；限時動態、精選集、置頂都不做。", ""]
    items = backfill_items()
    for it in items:
        lines.append(f"- [ ] `{it['post_id']}`（{it['url']}）需補 → `{it['target']}`（{it['target_published_at']} 發布）")
    if not items:
        lines.append("（目前沒有待回補項目）")
    STATE.mkdir(exist_ok=True)
    (STATE / "backfill.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote state/backfill.md（{len(items)} 項）")


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
