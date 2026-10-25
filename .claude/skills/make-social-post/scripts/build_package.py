"""由 spec.json 產生發布包裡「人看的檔案」與「審查用的檔案」，並更新索引。

用法：uv run python .claude/skills/make-social-post/scripts/build_package.py out/<series>/<concept>/_build/spec.json [--force]
已發布的貼文預設拒絕（--force 才重組）。
--refresh：只重寫這則的 README.md 與索引（發布後狀態與網址會變；不動 ig/post.md、threads/post.md、審查用文字，已發布也可用）。
發布程式（ig_publish.py、threads_publish.py）成功發出後會自動呼叫它。

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
import diagrams as D

CONTENT = {"text", "table", "chart_bars", "chart_sounding", "diagram"}
# 投影片欄位白名單：文字內容欄位都必須輸出到審查文字與 ig/post.md；版面參數不輸出。遇到不認得的欄位就報錯，
# 避免「新增欄位、卻漏了輸出」（審查者與人都看不到那段內容）。
CONTENT_KEYS = {"title", "body", "label", "question", "rows", "bars", "note", "nav", "legend",
                "nodes", "outcomes", "loop", "columns", "heads", "pairs", "count", "points", "ref", "ranges", "group", "start", "end",
                "items", "steps"}
LAYOUT_KEYS = {"layout", "refs", "quals", "fig_refs", "unit", "key_w", "subs_inline", "current", "axis_max", "kind", "cols", "more", "edges", "hot"}   # cols：點陣每列幾個點（版面參數，不含文字）


def check_fields(d: dict) -> None:
    bad = [(i, k) for i, sl in enumerate(d["slides"], 1) for k in sl if k not in CONTENT_KEYS | LAYOUT_KEYS]
    if bad:
        raise ValueError(f"投影片有不認得的欄位（要新增欄位，請先讓 build_package 輸出它並加測試）：{bad}")
LAYOUT_NAME = {"cover": "封面", "context": "脈絡", "text": "文字", "table": "對照表", "chart_bars": "橫條圖",
               "chart_sounding": "測深圖", "diagram": "示意圖", "takeaway": "帶走", "series_map": "系列地圖"}
mark = lambda s: re.sub(r"\[\[(.+?)\]\]", r"\1", s)


def first_clause(s: str) -> str:
    """補充的第一個子句；太長就不放（不截斷成「…」）。"""
    c = re.split(r"[；。]", s)[0]
    return c if len(c) <= 24 else ""


def figure_label(fig: dict) -> str:
    """卡上圖說的圖號：「圖一 — …（來源：原始論文）」→「圖一」；圖說沒有「 — 」時回傳空字串。"""
    m = re.match(r"^\s*([^—:：]{1,12}?)\s*[—:：]", fig.get("caption", ""))
    return m.group(1).strip() if m else ""


def figure_credit(d: dict) -> str:
    """有重製圖（fig_refs）時，caption 自動註明出處：改繪自原始論文哪張圖，不說成我們自己做的實驗（契約 guideline §5-5）。"""
    if not any(sl.get("fig_refs") for sl in d["slides"]):
        return ""
    claims = W.spec_claims(d)
    parts = []
    for i, sl in enumerate(d["slides"], 1):
        if not sl.get("fig_refs"):
            continue
        figs = W.slide_figures(claims, sl.get("refs") or [])
        labels = [figure_label(figs[f]["fig"]) for f in sl["fig_refs"] if f in figs]
        parts.append(f"第 {i} 張" + (f"（{'、'.join(l for l in labels if l)}）" if any(labels) else ""))
    return ("圖片來源：" + "、".join(parts) + "改繪自原始論文的圖表") if parts else ""


def caption_text(d: dict) -> str:
    cap = d["caption"]
    lines = [cap["first"], ""]
    for sl in d["slides"]:
        if sl["layout"] in CONTENT:
            fc = first_clause(sl.get("body", ""))
            lead = f"{sl['label']}：" if sl.get("label") and not mark(sl["title"]).startswith(sl["label"]) else ""     # 小標籤放在前面；標題已經以同樣的詞開頭就不重複（「第一關：第一關：」）
            lines.append(f"・{lead}{mark(sl['title'])}" + (f"（{fc}）" if fc else ""))
    if figure_credit(d):
        lines += ["", figure_credit(d)]
    lines += ([""] + [cap["nav"]] if cap.get("nav") else []) + ["", " ".join("#" + h for h in cap["hashtags"])]   # 導流行可省略（獨立貼文，人決定不導回來源文章）
    return "\n".join(lines)


def planned_title_of(concept: str) -> str:
    """獨立貼文「延伸閱讀」的標題：取自系列檔裡這個觀念的 planned_title（與 render.py 同一規則）。"""
    for sid in W.series_ids():
        for m in (load_series(sid) or {}).get("members", []):
            if m["concept"] == concept or concept in (m.get("also") or []):
                return m["planned_title"]
    raise KeyError(f"系列檔裡找不到觀念 {concept}")


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
    if sl["layout"] == "diagram":
        out.append(f"示意圖（{sl['kind']}）上的文字與數字：" + "｜".join(D.texts(sl)))
    if sl.get("edges"):      # links 圖的連線是內容（誰跟誰相連），審查者要看得到
        hot = {tuple(e) for e in sl.get("hot", [])}
        out.append("示意圖的連線（左—右）：" + "｜".join(f"{sl['nodes'][l]['text']}—{sl['outcomes'][r]['text']}" + ("（金色）" if (l, r) in hot else "") for l, r in sl["edges"]))
    if sl["layout"] == "diagram" and sl.get("kind") == "hops":
        out.append("示意圖的跳數（箭頭數）：" + "｜".join(f"{n['text']}＝{n['hops']} 跳" for n in sl["nodes"]))
    if sl.get("note"):
        out.append(f"圖註：{sl['note']}")
    for cid in sl.get("items", []):
        out.append(f"延伸閱讀：{planned_title_of(cid)}")
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
        if th.get("mode") == "carousel":
            L += ["", f"（Threads 這則是輪播：正文下附與 IG 相同順序的全部 {len(d['slides'])} 張圖，沒有逐張串文）"]
        for j, it in enumerate(th.get("items", []), 1):
            L += ["", f"### 串文 {j}（配第 {it['slide']} 張圖）", it["text"]]
            if with_refs:
                L.append(f"引用：{', '.join(it['refs'])}")
        if th.get("last"):
            L += ["", "### 最後一則（置頂）", th["last"]["text"]]
            if with_refs:
                L.append(f"引用：{', '.join(th['last']['refs'])}")
        else:
            L += ["", "（沒有最後一則回覆：只發輪播貼文）"]
        L += ["", "## IG caption", "", caption_text(d)]
        (build / name).write_text("\n".join(L) + "\n", encoding="utf-8")


def figure_review_file(d: dict, pack: Path, build: Path) -> None:
    """重製圖的審查材料（guideline §4.5）：每張有 fig_refs 的投影片，給審查者原圖路徑、主張文字與限定條件、重製後的圖與圖上文字。
    沒有 fig_refs 的貼文不產生這個檔（並刪掉舊的）。"""
    f = build / "figure-review.md"
    todo = [(i, sl) for i, sl in enumerate(d["slides"], 1) if sl.get("fig_refs")]
    if not todo:
        f.unlink(missing_ok=True)
        return
    claims = W.spec_claims(d)
    L = [f"# 重製圖審查材料：{d['concept']}", "",
         "原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。"]
    for i, sl in todo:
        figs = W.slide_figures(claims, sl.get("refs") or [])
        L += ["", f"## 第 {i} 張", "", f"- 重製後的圖：{(pack / 'ig' / f'{i:02d}.png').resolve()}", "- 重製圖上的文字（貼文最終文字）："]
        L += [f"  - {x}" for x in slide_lines(sl, False)]
        for fid in sl["fig_refs"]:
            fg = figs[fid]
            L += ["", f"### 原圖 {fid}", f"- 檔案：{fg['fig']['path'].resolve()}", f"- blog 圖說原文（不是主張）：{fg['fig'].get('caption', '')}", f"- 附這張圖的主張：{', '.join(fg['claims'])}"]
        L += ["", "### 這張引用的主張（圖要以它們為準）"]
        for cid in sl.get("refs") or []:
            c = claims.get(cid)
            if not c:
                continue
            L.append(f"- **{cid}**（{c['anchor_type']}）：{c['text']}")
            for k, q in enumerate(c.get("qualifiers") or [], 1):
                L.append(f"  - 限定條件 {cid}#{k}：{q.get('text', '')}" + ("（來源：圖說）" if q.get("source") == "figure_caption" else ""))
    f.write_text("\n".join(L) + "\n", encoding="utf-8")


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
            L += [f"- **主標**：{mark(sl['title'])}"] + [f"- **延伸閱讀**：{planned_title_of(c)}" for c in sl.get("items", [])] + [f"- **導流行**：{sl.get('nav', '')}"]
        else:
            if sl.get("label"):
                L.append(f"- **小標籤**：{sl['label']}")
            L.append(f"- **主標**：{mark(sl['title'])}")
            if sl.get("body"):
                L.append(f"- **補充**：{sl['body']}")
            for r in sl.get("rows", []):
                L.append(f"- **表列**：{r[0]}｜{r[1]}")
            if sl["layout"] == "diagram":
                L.append(f"- **示意圖（{sl['kind']}）上的文字與數字**：" + "｜".join(D.texts(sl)))
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
    if th.get("mode") == "carousel":
        n = len(d["slides"])
        how = ("，再用一則回覆放連結與系列（連結只放那則回覆）" if th.get("last") else "；沒有連結要放，**不發回覆**，只發這一則")
        L = [f"# Threads：{title}", "",
             f"- 發文方式：**一則輪播貼文**（正文＋全部 {n} 張圖，順序與 IG 相同）{how}",
             "- 圖檔在 `../ig/`（與 IG 輪播共用同一套）", "", "## 貼文正文（附下方全部圖片）", ""] + fence(th["body"]["text"]) + [""]
        L += ["## 附圖（依序）", ""] + [f"![第 {i} 頁](../ig/{i:02d}.png)" for i in range(1, n + 1)] + [""]
        if th.get("last"):
            L += ["## 回覆：連結與系列", ""] + fence(th["last"]["text"]) + [""]
        return "\n".join(L)
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


def urls_of(concept: str) -> dict:
    f = W.STATE_DIR / f"{concept}.yaml"
    d = (yaml.safe_load(f.read_text(encoding="utf-8")) if f.exists() else None) or {}
    return {p.get("format"): p.get("url") for p in d.get("posts") or [] if p.get("url")}


def load_series(sid: str | None) -> dict | None:
    if not sid or not W.series_file(sid).exists():
        return None
    t = W.series_file(sid).read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---", t, re.S).group(1))


STATUS_ZH = {"not_tried": "未做", "ready": "待發布", "published": "已發布", "unsuitable": "不適合"}


def before_publish_lines(concept: str, st: dict) -> list[str]:
    """README 的「發布前」區段；兩個格式都已發布就改成列出網址（不再顯示過時的待辦）。"""
    urls = urls_of(concept)
    if st.get("ig_carousel") == "published" and st.get("threads_thread") == "published":
        L = ["## 已發布", ""]
        for f, label in (("ig_carousel", "IG"), ("threads_thread", "Threads")):
            L.append(f"- {label}：{urls.get(f, '（網址見 `state/' + concept + '.yaml`）')}")
        return L + [""]
    return ["## 發布前", "",
            "- [ ] 人最後確認圖、文字、caption",
            "- [ ] IG（API）：`ig_publish.py prepare` → push `ig/jpg/` → `preflight` → `publish`（dry-run）→ 人說「發」後 `--confirm`（見 references/publish-flow.md）",
            "- [ ] Threads（API）：`threads_publish.py publish`（dry-run）→ 人說「發」後 `--confirm`（見 references/publish-flow.md）", ""]


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
         f"| Threads 串文 | {STATUS_ZH.get(st.get('threads_thread', 'not_tried'), st.get('threads_thread'))}（{2 if d['threads'].get('mode') == 'carousel' else len(d['threads']['items']) + 2} 則） |", "",
         "## 要看／要發的檔案", "",
         "| 要做什麼 | 打開哪個檔案 |", "|---|---|",
         "| 看 IG 每一頁的圖與文字、複製 caption | [`ig/post.md`](ig/post.md)（圖在 `ig/01.png` …） |",
         "| 看 Threads（正文與附圖、最後一則回覆；舊格式是逐張串文） | [`threads/post.md`](threads/post.md) |",
         "| 一眼看全部縮圖 | 下方縮圖，或 [`_build/contact-sheet.png`](_build/contact-sheet.png) |", ""]
    if (build / "contact-sheet.png").exists():
        L += ["![縮圖總覽](_build/contact-sheet.png)", ""]
    L += ["## 檢查結果（程式產生）", "", f"- {chk or '（還沒渲染）'}",
          "- 程式 A、批次檢查、忠實者與讀者審查的結果不存在發布包裡（審查產出放暫存，不進 repo）；最後確認時由 Claude 在報告中說明", "",
          ] + before_publish_lines(d["concept"], st) + [
          "## 發布後", "",
          "- 網址與時間由 `--confirm` 自動寫回 `state/`，不用另外記錄",
          "- [ ] 系列其他則發布後，Threads 回補由 Claude 做：`threads_publish.py backfill`（見 `state/backfill.md`）；IG 回補、限時動態、精選集、置頂都不做", "",
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
    # 獨立貼文（沒有系列）：out/standalone/<觀念 id>/，視覺在 standalone/<觀念 id>/
    solo = sorted(c.name for c in (out / "standalone").iterdir() if (c / "README.md").exists()) if (out / "standalone").exists() else []
    if solo:
        rows = ["| 觀念 | IG | Threads | 打開 |", "|---|---|---|---|"]
        for c in solo:
            st = state_of(c)
            ig, th = (STATUS_ZH.get(st.get(f, "not_tried"), "?") for f in ("ig_carousel", "threads_thread"))
            rows.append(f"| `{c}` | {ig} | {th} | [README](standalone/{c}/README.md) |")
            if "ready" in st.values():
                ready_lines.append(f"- 獨立貼文：[{c}](standalone/{c}/README.md)")
        top += ["## 獨立貼文（沒有系列）", ""] + rows + [""]
    top[4:4] = ["## 待發布", ""] + (ready_lines or ["（目前沒有）"]) + [""]
    out.mkdir(exist_ok=True)
    (out / "README.md").write_text("\n".join(top) + "\n", encoding="utf-8")


def refresh(spec_path: Path) -> None:
    """發布後只重寫 README.md 與索引，反映最新的狀態與網址。"""
    d = W.untex(json.loads(spec_path.read_text(encoding="utf-8")))
    pack, bld = W.pack_dir(spec_path), W.build_dir(spec_path)
    card = W.parse_card(W.WIKI / "wiki" / "concepts" / f"{d['concept']}.md")
    series = load_series(d.get("series"))
    title = card.front["title"]
    if series:
        title = next((m["planned_title"] for m in series["members"] if m["concept"] == d["concept"]), title)
    (pack / "README.md").write_text(readme_md(d, title, series, pack, bld), encoding="utf-8")
    if bld.name == "_build":
        indexes()
    print("refreshed", pack)


def check_tex_leftovers(raw_spec: dict, pack: Path, bld: Path) -> None:
    """spec 有開 `math` 時，所有給人與給平台看的文字都不該殘留 LaTeX 記號（IG caption 曾出現「$r$」）。"""
    if not raw_spec.get("math"):
        return
    bad = []
    for f in (pack / "ig" / "post.md", pack / "threads" / "post.md", pack / "README.md",
              bld / "post-reader.md", bld / "post-with-refs.md", bld / "alt-text.json"):
        if f.exists():
            text = f.read_text(encoding="utf-8")
            if f.suffix == ".json":      # 只掃值；JSON 的 \n 跳脫不是 LaTeX
                text = "\n".join(str(v) for v in json.loads(text).values())
            left = W.tex_leftovers(text)
            if left:
                bad.append(f"{f.relative_to(pack)}：{' '.join(left)}")
    if bad:
        sys.exit("ERROR：發布文字殘留 LaTeX 記號（要在 cardlib.untex 轉成純文字）：\n  " + "\n  ".join(bad))


def build(spec_path: Path, force: bool = False) -> None:
    d = W.untex(json.loads(spec_path.read_text(encoding="utf-8")))
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
    figure_review_file(d, pack, bld)
    (pack / "ig").mkdir(exist_ok=True)
    (pack / "threads").mkdir(exist_ok=True)
    (pack / "ig" / "post.md").write_text(ig_md(d, title, series["name"] if series else None, alts), encoding="utf-8")
    (pack / "threads" / "post.md").write_text(threads_md(d, title), encoding="utf-8")
    (pack / "README.md").write_text(readme_md(d, title, series, pack, bld), encoding="utf-8")
    if bld.name == "_build":
        indexes()
    print("wrote", pack)


if __name__ == "__main__":
    (refresh if "--refresh" in sys.argv else lambda p: build(p, "--force" in sys.argv))(Path(sys.argv[1]).resolve())
