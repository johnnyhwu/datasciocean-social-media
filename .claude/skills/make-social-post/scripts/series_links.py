"""Threads 最後一則的「同系列」連結：把已發布的貼文從「（尚未發布）」改成「標題＋下一行網址」。

用法：uv run python .claude/skills/make-social-post/scripts/series_links.py out/<series>/<concept>/_build/spec.json [--write]
  預設只列出會改什麼（dry-run）；--write 才改 spec.json 的 threads.last.text。
改完之後要重跑 check_a.py 與 build_package.py（--refresh 不夠，Threads 文字在 threads/post.md）。
threads_publish.py 的 dry-run 也會呼叫 stale()：已發布的同系列貼文還寫「尚未發布」就列為 problem。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

import cardlib as W

PENDING = "（尚未發布）"


def _members(series_id: str) -> list[dict]:
    t = W.series_file(series_id).read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---", t, re.S).group(1))["members"]


def published_urls(series_id: str) -> dict[str, str]:
    """planned_title → Threads 網址（只含已發布的成員）。"""
    out = {}
    for m in _members(series_id):
        f = W.STATE_DIR / f"{m['concept']}.yaml"
        if not f.exists():
            continue
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        for p in d.get("posts") or []:
            if p.get("format") == "threads_thread" and p.get("url"):
                out[m["planned_title"]] = p["url"]
    return out


def fill(text: str, urls: dict[str, str]) -> tuple[str, list[str]]:
    lines, changes = [], []
    for line in text.split("\n"):
        if line.startswith("同系列：") and line.endswith(PENDING):
            title = line[len("同系列："):-len(PENDING)].strip()
            if title in urls:
                lines += [f"同系列：{title}", urls[title]]
                changes.append(title)
                continue
        lines.append(line)
    return "\n".join(lines), changes


def stale(d: dict) -> list[str]:
    """已發布、但最後一則還寫「尚未發布」的同系列貼文標題。"""
    if not d.get("series"):
        return []
    urls = published_urls(d["series"])
    return [t for t in (line[len("同系列："):-len(PENDING)].strip()
                        for line in d["threads"]["last"]["text"].split("\n")
                        if line.startswith("同系列：") and line.endswith(PENDING)) if t in urls]


def main(argv: list[str]) -> int:
    spec = Path(argv[1]).resolve()
    d = json.loads(spec.read_text(encoding="utf-8"))
    if not d.get("series"):
        print("不是系列貼文，沒有「同系列」要補")
        return 0
    new, changes = fill(d["threads"]["last"]["text"], published_urls(d["series"]))
    if not changes:
        print("沒有要補的（已發布的同系列貼文都已補好，或同系列的貼文都還沒發布）")
        return 0
    print("會補上網址的貼文：" + "、".join(changes))
    print(f"最後一則字數：{len(d['threads']['last']['text'])} → {len(new)}（Threads 文字上限 500，連結照完整長度計）")
    if "--write" in argv:
        d["threads"]["last"]["text"] = new
        spec.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("已寫入 spec.json；請重跑 check_a.py 與 build_package.py")
    else:
        print("（dry-run；加 --write 才寫入）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
