"""由 spec.json 產生：貼文文字（給審查者）、IG caption、Threads 文字（references/threads-and-caption.md、batch-and-publish.md）。

用法：uv run python .claude/skills/make-social-post/scripts/build_package.py out/<series>/<concept>/spec.json
輸出（同資料夾）：post-with-refs.md（忠實者用）、post-reader.md（讀者與編輯用，不含引用編號）、
                 ig/caption.txt、threads.txt
caption 的逐張摘要由「最終的投影片規格」自動產生（必須在張數定案之後）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CONTENT = {"text", "table", "chart_bars", "chart_sounding"}
mark = lambda s: re.sub(r"\[\[(.+?)\]\]", r"\1", s)


def first_clause(s: str) -> str:
    return re.split(r"[；。]", s)[0]


def slide_lines(sl: dict, with_refs: bool) -> list[str]:
    out = [f"版型：{sl['layout']}"]
    if sl.get("label"):
        out.append(f"小標籤：{sl['label']}")
    out.append(f"主標：{mark(sl.get('title', ''))}")
    if sl.get("body"):
        out.append(f"補充：{sl['body']}")
    for r in sl.get("rows", []):
        out.append(f"表列：{r[0]}｜{r[1]}")
    if sl.get("bars"):
        out.append(f"圖表單位：{sl.get('unit', '')}（軸從 0 起；繩長或橫條長度與數值成正比）")
        for b in sl["bars"]:
            out.append(f"圖表項目：{b['name']}｜{'／'.join(b.get('subs', []))}｜{b['value']:g} {sl.get('unit', '')}" + ("｜強調" if b.get("emphasize") else ""))
    if sl.get("note"):
        out.append(f"圖註：{sl['note']}")
    if sl.get("nav"):
        out.append(f"導流行：{sl['nav']}")
    if with_refs:
        out.append(f"引用：{', '.join(sl.get('refs', []))}" + (f"｜帶出限定條件：{', '.join(sl['quals'])}" if sl.get("quals") else ""))
    return out


def build(spec_path: Path) -> None:
    d = json.loads(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    for with_refs, name in ((True, "post-with-refs.md"), (False, "post-reader.md")):
        L = [f"# 貼文：{d['concept']}（{d['lang']}）", "", f"## IG 輪播（共 {len(d['slides'])} 張）"]
        for i, sl in enumerate(d["slides"], 1):
            L += ["", f"### 第 {i} 張"] + slide_lines(sl, with_refs)
        th = d["threads"]
        L += ["", "## Threads 串文", "", "### 正文", th["body"]["text"]]
        if with_refs:
            L.append(f"引用：{', '.join(th['body']['refs'])}" + (f"｜帶出限定條件：{', '.join(th['body'].get('quals', []))}" if th['body'].get("quals") else ""))
        for j, it in enumerate(th["items"], 1):
            L += ["", f"### 串文 {j}（配第 {it['slide']} 張圖）", it["text"]]
            if with_refs:
                L.append(f"引用：{', '.join(it['refs'])}")
        L += ["", "### 最後一則（置頂）", th["last"]["text"]]
        if with_refs:
            L.append(f"引用：{', '.join(th['last']['refs'])}")
        cap = d["caption"]
        L += ["", "## IG caption", "", cap["first"]]
        for i, sl in enumerate(d["slides"], 1):
            if sl["layout"] in CONTENT:
                L.append(f"{i}｜{mark(sl['title'])}（{first_clause(sl.get('body', ''))}）")
        L += [cap["nav"], " ".join("#" + h for h in cap["hashtags"])]
        (base / name).write_text("\n".join(L) + "\n", encoding="utf-8")
    cap = d["caption"]
    lines = [cap["first"], ""]
    for i, sl in enumerate(d["slides"], 1):
        if sl["layout"] in CONTENT:
            lines.append(f"{i}｜{mark(sl['title'])}（{first_clause(sl.get('body', ''))}）")
    lines += ["", cap["nav"], "", " ".join("#" + h for h in cap["hashtags"])]
    (base / "ig").mkdir(exist_ok=True)
    (base / "ig" / "caption.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    th = d["threads"]
    t = ["【正文】", th["body"]["text"], ""]
    for j, it in enumerate(th["items"], 1):
        t += [f"【串文 {j}】附圖 ig/{it['slide']:02d}.png", it["text"], ""]
    t += ["【最後一則（置頂）】", th["last"]["text"]]
    (base / "threads.txt").write_text("\n".join(t) + "\n", encoding="utf-8")
    print("wrote", base)


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve())
