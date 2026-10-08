"""程式 A：貼文的引用標記與格式檢查（引用標記、比較詞、限定條件、字數、重疊率…；規則見 references/program-a.md）。

用法：uv run python .claude/skills/make-social-post/scripts/check_a.py out/<series>/<concept>/_build/spec.json
結束碼：0 通過（可能有 HINT）、1 有 ERROR。

貼文被改寫過，不能比對字面，所以靠「標記編號」：每個區塊（投影片、串文、caption 的各部分）
都要標 refs（引用卡上的 claim id），或標「結構」。引用只證明有對應，不證明意思沒走樣；走樣由忠實者判斷。

spec.json 欄位：
  slides[].refs        引用的 claim id 或 ["結構"]
  slides[].quals       這個區塊帶出的限定條件，格式 "c3#1"（c3 的第 1 條 qualifiers）
  threads.body / threads.items[] / threads.last   各有 text、refs、quals（items 另有 slide）
  caption.first / caption.nav / caption.hashtags / caption.nav_refs
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

import cardlib as W

P = W.load_params()
OK_STATUS = {"normal", "author_confirmed"}
BIGRAM = lambda s: {s[i:i + 2] for i in range(len(s) - 1)}
NUM = re.compile(r"\d+(?:\.\d+)?")
CONTENT_LAYOUTS = {"text", "table", "chart_bars", "chart_sounding"}


def strip_marks(s: str) -> str:
    return re.sub(r"\[\[(.+?)\]\]", r"\1", s)


def numbers(s: str) -> list[str]:
    return NUM.findall(re.sub(r"(?<=\w)-(?=\w)", " ", s)) if s else []


def slide_texts(sl: dict) -> list[str]:
    """逐欄位的文字（數字抽取要逐欄位，不得串接）。"""
    out = []
    for k in ("title", "body", "note", "label"):
        if sl.get(k):
            out.append(strip_marks(sl[k]))
    for r in sl.get("rows", []):
        out += list(r)
    for b in sl.get("bars", []):
        out.append(b["name"]); out += b.get("subs", [])
        out.append(f"{b['value']:g}")
    return out


def main(spec_path: str) -> int:
    sp = Path(spec_path)
    doc = json.loads(sp.read_text(encoding="utf-8"))
    card = W.parse_card(W.WIKI / "wiki" / "concepts" / f"{doc['concept']}.md")
    claims = W.spec_claims(doc)   # 主卡裸 id；併入的卡「卡id:cN」
    series = yaml.safe_load(re.match(r"^---\n(.*?)\n---", W.series_file(doc["series"]).read_text(encoding="utf-8"), re.S).group(1))
    err, hint = [], []
    terms = (yaml.safe_load((W.ROOT / "config" / "terms.yaml").read_text(encoding="utf-8")) or {}).get("replace", {})

    def claim_text(cid):
        c = claims[cid]
        return c["text"] + " " + " ".join(c.get("source_quotes", [])) + " " + " ".join(str(q.get("text", "")) for q in c.get("qualifiers", []))

    blocks = []  # (name, text_fields, refs, quals, kind)
    for i, sl in enumerate(doc["slides"], 1):
        blocks.append((f"slide{i:02d}({sl['layout']})", slide_texts(sl), sl.get("refs"), sl.get("quals", []), sl))
    th = doc["threads"]
    blocks.append(("threads.body", [th["body"]["text"]], th["body"].get("refs"), th["body"].get("quals", []), None))
    for j, it in enumerate(th["items"], 1):
        blocks.append((f"threads.item{j}(slide{it['slide']})", [it["text"]], it.get("refs"), it.get("quals", []), None))
    blocks.append(("threads.last", [th["last"]["text"]], th["last"].get("refs"), th["last"].get("quals", []), None))
    cap = doc["caption"]
    blocks.append(("caption.first", [cap["first"]], cap.get("first_refs"), [], None))
    blocks.append(("hook", [strip_marks(doc["hook"]["title"]), doc["hook"]["subtitle"]], doc["hook"].get("refs"), doc["hook"].get("quals", []), None))

    used_claims, used_quals = set(), set()
    for name, fields, refs, quals, sl in blocks:
        # 1. 每個區塊至少引用一條主張或標「結構」
        if not refs:
            err.append(f"{name}: 沒有 refs（需引用主張或標「結構」）"); continue
        structural = refs == ["結構"]
        txt_all = " ".join(fields)
        if structural:
            # 2. 結構區塊不得含數字、字數有上限
            if numbers(txt_all):
                err.append(f"{name}: 標「結構」卻含數字 {numbers(txt_all)}")
            if sum(len(f) for f in fields) > P["structure_text_max_chars"]:
                err.append(f"{name}: 「結構」區塊超過 {P['structure_text_max_chars']} 字（{sum(len(f) for f in fields)}）")
            continue
        bad = [r for r in refs if r not in claims]
        if bad:
            err.append(f"{name}: 引用不存在的主張 {bad}"); continue
        for r in refs:
            used_claims.add(r)
            # 5. 狀態
            if claims[r]["status"] not in OK_STATUS:
                err.append(f"{name}: 引用了 {r}，狀態是 {claims[r]['status']}（不得使用）")
        used_quals.update(quals)
        ref_text = " ".join(claim_text(r) for r in refs)
        ref_text_flat = re.sub(r"\s+", "", ref_text)
        # 6./7. 數字：逐欄位抽取；必須出現在引用主張裡（HINT）；必須有比較對象（ERROR）
        for f in fields:
            for n in numbers(f):
                inref = [r for r in refs if n in numbers(claim_text(r)) or n in numbers(" ".join(claims[r].get("source_quotes", [])))]
                if not inref:
                    hint.append(f"{name}: 數字 {n} 不在引用主張原文（交忠實者重點檢查）")
                    continue
                ok_t = any(claims[r].get("comparison_target") or claims[r].get("numeric_kind") == "non_comparative" for r in inref)
                if not ok_t:
                    err.append(f"{name}: 數字 {n} 的引用主張 {inref} 沒有 comparison_target")
        # 8. 圖上的名稱（拉丁字詞）要被引用的主張涵蓋
        if sl and sl["layout"] in ("chart_bars", "chart_sounding"):
            for b in sl["bars"]:
                for tok in re.findall(r"[A-Za-z][A-Za-z0-9.\-]*", b["name"] + " " + " ".join(b.get("subs", []))):
                    if tok.lower() not in ref_text.lower():
                        err.append(f"{name}: 圖上名稱 {tok!r} 沒有被引用的主張涵蓋")
        # 9. 比較詞與全稱詞
        for w in P["comparative_words"]:
            for f in fields:
                if w in f and w not in ref_text:
                    err.append(f"{name}: 比較詞/全稱詞 {w!r} 出現在貼文，卻不在引用主張原文")
                    break
        # 用語對照（config/terms.yaml）
        for old, new in terms.items():
            if old in txt_all:
                err.append(f"{name}: 用語 {old!r} 應寫成 {new!r}（config/terms.yaml）")
        # 12. AI 腔黑名單
        for w in P["ai_tone_blacklist"]:
            if w in txt_all:
                err.append(f"{name}: AI 腔黑名單命中 {w!r}")
        if "podcast" in txt_all.lower():
            err.append(f"{name}: 出現 podcast")

    # 併入的卡必須與系列檔裡這個成員的 also 一致
    mem = next((m for m in series["members"] if m["concept"] == doc["concept"]), None)
    if sorted(doc.get("also_concepts") or []) != sorted((mem or {}).get("also") or []):
        err.append(f"also_concepts {doc.get('also_concepts') or []} 與系列檔成員的 also {(mem or {}).get('also') or []} 不一致")
    # 系列檔的 planned_title 會自動填進系列地圖與 Threads 最後一則，也要符合用語對照
    for m in series["members"]:
        for old, new in terms.items():
            if old in m["planned_title"]:
                err.append(f"系列檔 planned_title {m['planned_title']!r}: 用語 {old!r} 應寫成 {new!r}")
    # 3. 被使用的主張，它綁定的限定條件必須出現在貼文某處（以 quals 標記）
    for cid in sorted(used_claims):
        for k, q in enumerate(claims[cid].get("qualifiers", []), 1):
            if f"{cid}#{k}" not in used_quals:
                err.append(f"限定條件未帶出：{cid}#{k} {q.get('text','')[:40]}")
    # 4. evidence_from_single_source：脈絡張必須引用方法來源（role=context）的主張
    if card.front["context_type"] in ("evidence_from_single_source", "bound_to_source"):
        ctx = [s for s in doc["slides"] if s["layout"] == "context"]
        if not ctx or not any(claims[r]["role"] == "context" for r in ctx[0].get("refs", []) if r in claims):
            err.append("脈絡張沒有引用 role=context 的主張（漏交代方法來源）")
    # 張數、字數
    if len(doc["slides"]) > P["slides_max"]:
        err.append(f"投影片 {len(doc['slides'])} 張，超過 {P['slides_max']}")
    for i, sl in enumerate(doc["slides"], 1):
        body = sl.get("body", "")
        if sl["layout"] in ("text",) and not (P["body_chars"][0] <= len(body) <= P["body_chars"][1]):
            err.append(f"slide{i:02d}: 補充 {len(body)} 字，不在 {P['body_chars']}")
        if sl["layout"] in ("table", "chart_bars", "chart_sounding") and len(body) > P["chart_body_max_chars"]:
            err.append(f"slide{i:02d}: 圖表版型補充 {len(body)} 字，超過 {P['chart_body_max_chars']}（補充行數預檢）")
        if sl["layout"] == "context" and len(body) > P["context_body_max_chars"]:
            err.append(f"slide{i:02d}: 脈絡張補充 {len(body)} 字，超過 {P['context_body_max_chars']}")
        lim = P["cover_title_precheck_chars"] if sl["layout"] == "cover" else P["title_precheck_chars"]
        if len(strip_marks(sl.get("title", ""))) > lim + 10:
            hint.append(f"slide{i:02d}: 主標 {len(strip_marks(sl.get('title','')))} 字，預檢上限 {lim}（以渲染行數為準）")
    # Threads
    if len(th["body"]["text"]) > P["thread_body_max_chars"]:
        err.append(f"Threads 正文 {len(th['body']['text'])} 字，超過 {P['thread_body_max_chars']}")
    if re.search(r"https?://|datasciocean\.com", th["body"]["text"]) or any(re.search(r"https?://|datasciocean\.com", it["text"]) for it in th["items"]):
        err.append("Threads：連結只能放在最後一則")
    content_idx = [i for i, s in enumerate(doc["slides"], 1) if s["layout"] in CONTENT_LAYOUTS]
    if sorted(it["slide"] for it in th["items"]) != content_idx:
        err.append(f"Threads 串文與內容投影片不是一對一：串文 {sorted(it['slide'] for it in th['items'])}，內容張 {content_idx}")
    for j, it in enumerate(th["items"], 1):
        sl = doc["slides"][it["slide"] - 1]
        img = re.sub(r"\s+", "", " ".join(slide_texts(sl)))
        d = re.sub(r"\s+", "", it["text"])
        bd = BIGRAM(d)
        if bd:
            ov = len(bd & BIGRAM(img)) / len(bd)
            if ov > P["thread_desc_overlap_max"]:
                err.append(f"threads.item{j}: 與圖上文字重疊率 {ov:.0%} 超過 {P['thread_desc_overlap_max']:.0%}（描述只是在重述圖）")
    # caption
    if len(cap["first"]) > P["caption_first_sentence_max_chars"]:
        err.append(f"caption 第一句 {len(cap['first'])} 字，超過 {P['caption_first_sentence_max_chars']}")
    if len(cap["hashtags"]) > P["hashtags_max"]:
        err.append(f"hashtag {len(cap['hashtags'])} 個，超過 {P['hashtags_max']}")
    if series["hashtag"] not in cap["hashtags"]:
        err.append(f"系列貼文必須含系列標籤 #{series['hashtag']}")
    if "podcast" in json.dumps(doc, ensure_ascii=False).lower():
        err.append("貼文內容出現 podcast")
    # 系列標籤與標題一致（由渲染引擎從 wiki 填入；這裡確認 series_map 的 current 存在）
    cur = [s.get("current") for s in doc["slides"] if s["layout"] == "series_map"]
    if cur and cur[0] not in [m["concept"] for m in series["members"]]:
        err.append(f"系列地圖 current={cur[0]} 不在系列成員內")

    print(f"== 程式 A {doc['concept']}: {'FAIL' if err else 'PASS'}（ERROR {len(err)}，HINT {len(hint)}）")
    for e in err:
        print("  ERROR", e)
    for h in hint:
        print("  HINT ", h)
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
