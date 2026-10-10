"""由 spec.json 產生發布包裡「人看的檔案」與「審查用的檔案」，並更新索引。

用法：uv run python .claude/skills/make-social-post/scripts/build_package.py out/<series>/<concept>/_build/spec.json [--force]
已發布的貼文預設拒絕（--force 才重組）。

輸出（發布包 out/<series>/<concept>/）：
  README.md              這則貼文的唯一入口：縮圖、檢查結果、要看哪些檔案、發布前後待辦
  ig/post.md             IG 輪播：每一頁的圖片與文字、替代文字，最後是整段 caption
  threads/post.md        Threads 串文：正文、每則串文（附圖）、最後一則
  _build/post-with-refs.md、_build/post-reader.md   審查者用（有引用編號／無引用編號）
索引（重新產生，不手改）：
  out/<series>/README.md  系列的發文順序與各則狀態
  out/README.md           全部貼文的總入口

caption 的逐張摘要由「最終的投影片規格」自動產生（必須在張數定案之後）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

import cardlib as W

CONTENT = {"text", "table", "chart_bars", "chart_sounding"}
# 投影片欄位白名單：文字內容欄位都必須輸出到審查文字與 ig/post.md；版面參數不輸出。遇到不認得的欄位就報錯，
# 避免「新增欄位、卻漏了輸出」（審查者與人都看不到那段內容）。
CONTENT_KEYS = {"title", "body", "label", "question", "rows", "bars", "note", "nav", "legend"}
LAYOUT_KEYS = {"layout", "refs", "quals", "unit", "key_w", "subs_inline", "current", "axis_max"}


def check_fields(d: dict) -> None:
    bad = [(i, k) for i, sl in enumerate(d["slides"], 1) for k in sl if k not in CONTENT_KEYS | LAYOUT_KEYS]
    if bad:
        raise ValueError(f"投影片有不認得的欄位（要新增欄位，請先讓 build_package 輸出它並加測試）：{bad}")
LAYOUT_NAME = {"cover": "封面", "context": "脈絡", "text": "文字", "table": "對照表", "chart_bars": "橫條圖",
               "chart_sounding": "測深圖", "takeaway": "帶走", "series_map": "系列地圖"}
mark = lambda s: re.sub(r"\[\[(.+?)\]\]", r"\1", s)


def first_clause(s: str) -> str:
    """補充的第一個子句；太長就不放（不截斷成「…」）。"""
    c = re.split(r"[；。]", s)[0]
    return c if len(c) <= 24 else ""


def caption_text(d: dict) -> str:
    cap = d["caption"]
    lines = [cap["first"], ""]
    for sl in d["slides"]:
        if sl["layout"] in CONTENT:
            fc = first_clause(sl.get("body", ""))
            lead = f"{sl['label']}：" if sl.get("label") and not mark(sl["title"]).startswith(sl["label"]) else ""     # 小標籤放在前面；標題已經以同樣的詞開頭就不重複（「第一關：第一關：」）
            lines.append(f"・{lead}{mark(sl['title'])}" + (f"（{fc}）" if fc else ""))
    lines += ["", cap["nav"], "", " ".join("#" + h for h in cap["hashtags"])]
    return "\n".join(lines)


def slide_lines(sl: dict, with_refs: bool) -> list[str]:
    """審查者用（post-with-refs.md／post-reader.md）。"""
    out = [f"版型：{sl['layout']}"]
    if sl.get("label"):
        out.append(f"小標籤：{sl['label']}")
    if sl.get("question"):
        out.append(f"先問的問題：{sl['question']}")
    out.append(f"主標：{mark(sl.get('title', ''))}")
    if sl.get("body"):
        out.append(f"補充：{sl['body']}")
    for r in sl.get("rows", []):
        out.append(f"表列：{r[0]}｜{r[1]}")
    if sl.get("bars"):
        out.append(f"圖表單位：{sl.get('unit') or '無單位'}（軸從 0 起；繩長或橫條長度與數值成正比）")
        for b in sl["bars"]:
            v2 = f"｜{sl['legend'][1]} {b['value2']:g} {sl.get('unit', '')}" if "value2" in b else ""
            out.append(f"圖表項目：{b['name']}｜{'／'.join(b.get('subs', []))}｜{(sl['legend'][0] + ' ') if v2 else ''}{b['value']:g} {sl.get('unit', '')}{v2}" + ("｜強調" if b.get("emphasize") else ""))
    if sl.get("note"):
        out.append(f"圖註：{sl['note']}")
    if sl.get("nav"):
        out.append(f"導流行：{sl['nav']}")
    if with_refs:
        out.append(f"引用：{', '.join(sl.get('refs', []))}" + (f"｜帶出限定條件：{', '.join(sl['quals'])}" if sl.get("quals") else ""))
    return out


def review_files(d: dict, build: Path) -> None:
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
        L += ["", "## IG caption", "", caption_text(d)]
        (build / name).write_text("\n".join(L) + "\n", encoding="utf-8")


def fence(text: str) -> list[str]:
    return ["```text", text, "```"]


def ig_md(d: dict, title: str, series_name: str | None, alts: dict) -> str:
    n = len(d["slides"])
    L = [f"# IG 輪播：{title}", "",
         f"- 系列：{series_name or '（獨立貼文）'}　｜　hook 樣態：{d['hook']['style']}　｜　共 {n} 張，**依頁碼順序上傳**",
         "- 每頁下方的「替代文字」貼到 IG 的替代文字欄；最後的 Caption 整段貼上", ""]
    for i, sl in enumerate(d["slides"], 1):
        png = f"{i:02d}.png"
        L += [f"## 第 {i} 頁（{LAYOUT_NAME.get(sl['layout'], sl['layout'])}）", "", f"![第 {i} 頁]({png})", ""]
        if sl["layout"] == "cover":
            L += [f"- **主標**：{mark(sl['title'])}", f"- **副標**：{sl.get('body', '')}"]
        elif sl["layout"] == "takeaway":
            if sl.get("label"):
                L.append(f"- **小標籤**：{sl['label']}")
            if sl.get("question"):
                L.append(f"- **先問的問題**：{sl['question']}")
            L.append(f"- **一句話**：{mark(sl['title'])}")
        elif sl["layout"] == "series_map":
            L += [f"- **主標**：{mark(sl['title'])}", f"- **導流行**：{sl.get('nav', '')}"]
        else:
            if sl.get("label"):
                L.append(f"- **小標籤**：{sl['label']}")
            L.append(f"- **主標**：{mark(sl['title'])}")
            if sl.get("body"):
                L.append(f"- **補充**：{sl['body']}")
            for r in sl.get("rows", []):
                L.append(f"- **表列**：{r[0]}｜{r[1]}")
            for b in sl.get("bars", []):
                v2 = f"；{sl['legend'][1]} {b['value2']:g} {sl.get('unit', '')}" if "value2" in b else ""
                L.append(f"- **圖上項目**：{b['name']}（{'、'.join(b.get('subs', []))}）＝ {(sl['legend'][0] + ' ') if v2 else ''}{b['value']:g} {sl.get('unit', '')}{v2}" + ("　★強調" if b.get("emphasize") else ""))
            if sl.get("note"):
                L.append(f"- **圖註**：{sl['note']}")
        if alts.get(png):
            L.append(f"- **替代文字**：{alts[png]}")
        L.append("")
    L += ["## Caption（整段貼到 IG）", ""] + fence(caption_text(d)) + [""]
    return "\n".join(L)


def threads_md(d: dict, title: str) -> str:
    th = d["threads"]
    L = [f"# Threads 串文：{title}", "",
         "- 發文方式：正文用「新增到串文」**一次發出**，每則串文附下方標註的圖；**連結只放最後一則**（置頂）",
         "- 圖檔在 `../ig/`（與 IG 輪播共用同一套）", "", "## 正文", ""] + fence(th["body"]["text"]) + [""]
    for j, it in enumerate(th["items"], 1):
        L += [f"## 串文 {j}（附圖：第 {it['slide']} 頁）", "", f"![第 {it['slide']} 頁](../ig/{it['slide']:02d}.png)", ""] + fence(it["text"]) + [""]
    L += ["## 最後一則（置頂）", ""] + fence(th["last"]["text"]) + [""]
    return "\n".join(L)


def state_of(concept: str) -> dict:
    f = W.STATE_DIR / f"{concept}.yaml"
    d = (yaml.safe_load(f.read_text(encoding="utf-8")) if f.exists() else None) or {}
    return {k: (v or {}).get("status", "not_tried") for k, v in (d.get("formats") or {}).items()}


def load_series(sid: str | None) -> dict | None:
    if not sid or not W.series_file(sid).exists():
        return None
    t = W.series_file(sid).read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---", t, re.S).group(1))


STATUS_ZH = {"not_tried": "未做", "ready": "待發布", "published": "已發布", "unsuitable": "不適合"}


def readme_md(d: dict, title: str, series: dict | None, pack: Path, build: Path) -> str:
    st = state_of(d["concept"])
    cb = build / "checks-b.json"
    chk = ""
    if cb.exists():
        r = json.loads(cb.read_text(encoding="utf-8"))
        okn = sum(1 for s in r["slides"] if all(c["ok"] for c in s["checks"]))
        chk = f"程式 B：{okn}/{len(r['slides'])} 張通過（模板版本 `{r['template_hash']}`）"
    L = [f"# {title}", "",
         "| 項目 | 內容 |", "|---|---|",
         f"| 系列 | {series['name'] if series else '（獨立貼文）'} |",
         f"| 觀念 | `{d['concept']}`（卡：`concept-wiki/wiki/concepts/{d['concept']}.md`）" + "".join(f"；併入 `{o}`" for o in d.get("also_concepts") or []) + " |",
         f"| hook 樣態 | {d['hook']['style']} |",
         f"| IG 輪播 | {STATUS_ZH.get(st.get('ig_carousel', 'not_tried'), st.get('ig_carousel'))}（{len(d['slides'])} 張） |",
         f"| Threads 串文 | {STATUS_ZH.get(st.get('threads_thread', 'not_tried'), st.get('threads_thread'))}（{len(d['threads']['items']) + 2} 則） |", "",
         "## 要看／要發的檔案", "",
         "| 要做什麼 | 打開哪個檔案 |", "|---|---|",
         "| 看 IG 每一頁的圖與文字、複製 caption | [`ig/post.md`](ig/post.md)（圖在 `ig/01.png` …） |",
         "| 看 Threads 串文（正文、每則附圖、最後一則） | [`threads/post.md`](threads/post.md) |",
         "| 一眼看全部縮圖 | 下方縮圖，或 [`_build/contact-sheet.png`](_build/contact-sheet.png) |", ""]
    if (build / "contact-sheet.png").exists():
        L += ["![縮圖總覽](_build/contact-sheet.png)", ""]
    L += ["## 檢查結果（程式產生）", "", f"- {chk or '（還沒渲染）'}",
          "- 程式 A、批次檢查、忠實者與讀者審查的結果不存在發布包裡（審查產出放暫存，不進 repo）；最後確認時由 Claude 在報告中說明", "",
          "## 發布前", "",
          "- [ ] 人最後確認圖、文字、caption",
          "- [ ] IG：手動上傳 `ig/01.png` …，貼 caption，替代文字貼自 `ig/post.md`；**或**用 API：`ig_publish.py prepare` → push `ig/jpg/` → `preflight` → `publish`（dry-run）→ 確認後 `--confirm`（見 references/instagram-publish.md）",
          "- [ ] Threads：手動用「新增到串文」一次發出，每則串文附圖，最後一則（置頂）含文章連結；**或**用 API：`threads_publish.py publish`（dry-run）→ 確認後 `--confirm`（見 references/threads-publish.md）", "",
          "## 發布後", "",
          "- [ ] 發限時動態並加連結貼紙，指向文章",
          "- [ ] 收進系列精選集；概覽發布後置頂概覽 post；置頂最後一則 Threads 回覆",
          "- [ ] 把網址與時間交給系統寫回：`state.py record <觀念> <格式> --url … --published-at …`",
          "- [ ] 系列其他則發布後，依 `state/backfill.md` 回補（IG 改 caption；Threads 在原串文下加回覆）", "",
          "## `_build/`（機器用，不用看）", "",
          "`spec.json`（內容規格，唯一的真相來源）、`checks-b.json`、`alt-text.json`、`html/`、`post-with-refs.md`、`post-reader.md`、`contact-sheet.png`。",
          "改內容請改 `spec.json` 後重跑 `check_a.py` → `render.py` → `build_package.py`。", ""]
    return "\n".join(L)


def indexes() -> None:
    out = W.ROOT / "out"
    top = ["# 發布包總覽（程式產生，不手改）", "",
           "每則貼文一個資料夾，打開裡面的 `README.md`；IG 看 `ig/post.md`，Threads 看 `threads/post.md`。", ""]
    ready_lines = []
    for sid in W.series_ids():
        s = load_series(sid)
        rows = ["| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |", "|---|---|---|---|---|---|"]
        any_pack = False
        for i, m in enumerate(s["members"], 1):
            c = m["concept"]
            st = state_of(c)
            has = (out / sid / c / "README.md").exists()
            any_pack |= has
            link = f"[README]({c}/README.md)" if has else "（還沒做）"
            ig, th = (STATUS_ZH.get(st.get(f, "not_tried"), "?") for f in ("ig_carousel", "threads_thread"))
            rows.append(f"| {i} | `{c}`" + "".join(f"＋`{o}`" for o in m.get("also") or []) + f" | {m['planned_title']} | {ig} | {th} | {link} |")
            if "ready" in st.values():
                ready_lines.append(f"- {s['name']} 第 {i} 則：[{m['planned_title']}]({sid}/{c}/README.md)")
        if any_pack:
            (out / sid / "README.md").write_text("\n".join([f"# {s['name']}", "", "發文順序依下表（概覽先發，被依賴的先發）。發文時間由人決定；經人確認後才發布。", ""] + rows) + "\n", encoding="utf-8")
        top += [f"## {s['name']}（`{sid}`）", ""] + rows + [""]
    top[4:4] = ["## 待發布", ""] + (ready_lines or ["（目前沒有）"]) + [""]
    out.mkdir(exist_ok=True)
    (out / "README.md").write_text("\n".join(top) + "\n", encoding="utf-8")


def build(spec_path: Path, force: bool = False) -> None:
    d = json.loads(spec_path.read_text(encoding="utf-8"))
    W.guard_published(d, force)
    check_fields(d)
    pack, bld = W.pack_dir(spec_path), W.build_dir(spec_path)
    card = W.parse_card(W.WIKI / "wiki" / "concepts" / f"{d['concept']}.md")
    series = load_series(d.get("series"))
    alt_f = bld / "alt-text.json"
    alts = json.loads(alt_f.read_text(encoding="utf-8")) if alt_f.exists() else {}
    title = card.front["title"]
    if series:   # 系列貼文用系列檔的 planned_title（簡短），否則用卡的標題
        title = next((m["planned_title"] for m in series["members"] if m["concept"] == d["concept"]), title)
    review_files(d, bld)
    (pack / "ig").mkdir(exist_ok=True)
    (pack / "threads").mkdir(exist_ok=True)
    (pack / "ig" / "post.md").write_text(ig_md(d, title, series["name"] if series else None, alts), encoding="utf-8")
    (pack / "threads" / "post.md").write_text(threads_md(d, title), encoding="utf-8")
    (pack / "README.md").write_text(readme_md(d, title, series, pack, bld), encoding="utf-8")
    if bld.name == "_build":
        indexes()
    print("wrote", pack)


if __name__ == "__main__":
    build(Path(sys.argv[1]).resolve(), "--force" in sys.argv)
