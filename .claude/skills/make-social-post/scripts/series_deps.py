"""系列規劃用：列出「分開發可能不好懂、也許該合併成一則」的候選（references/batch-and-publish.md §1）。

用法：uv run python .claude/skills/make-social-post/scripts/series_deps.py <系列 id>
對系列檔 members 裡每一對卡，列出信號：
  - 重複的主張：兩張卡有幾條幾乎相同的主張（例如同一個指標的定義兩張卡都寫），分開發就得各解釋一次
  - 用到對方標題的術語：A 的主張有幾條用了 B 的標題裡的英文術語（B 的主題）
  - 術語依賴：A 用了某個英文術語、自己沒有在 role=context 的主張裡定義，但 B 有
  - related（卡上的相關連結）、共用的來源小節（只當參考）

**限制（2026-10-08 實測，要老實看待）**：這些信號都挑不出我們後來合併的那一對
（judge-readable-vs-derive ＋ confidence-three-metrics）。同一篇文章的系列裡，每張卡都會重講 q、JEV 這類基礎概念，
所以重複主張與共用小節幾乎每一對都有；真正該合併的理由（讀者要靠另一張卡才懂信心、校準那段）靠這些數字看不出來。
所以這個腳本**只是提醒與輔助，不是偵測器**：規劃系列時不論結果如何，都要走「規劃時一定要問人」的步驟
（batch-and-publish.md §1），用讀者的角度逐則看：這則圖上的術語，有沒有要靠別則才看得懂？
結束碼永遠是 0。
"""
from __future__ import annotations

import itertools
import re
import sys

import yaml

import cardlib as W

TERM = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}")
# 太一般、不算「要定義的術語」的詞（背景詞清單的精簡版）
COMMON = {"LLM", "API", "GPU", "RAG", "the", "and", "for", "log", "ln", "not"}


def load_series(sid: str) -> dict:
    t = W.series_file(sid).read_text(encoding="utf-8")
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---", t, re.S).group(1))


def terms_of(text: str) -> set[str]:
    return {t for t in TERM.findall(text) if t not in COMMON and not t.isdigit()}


def bigrams(t: str) -> set[str]:
    t = re.sub(r"\s+", "", t)
    return {t[i:i + 2] for i in range(len(t) - 1)}


def dup_claims(a_claims: list[dict], b_claims: list[dict], thr: float = 0.6) -> list[tuple[str, str]]:
    """兩張卡裡幾乎相同的主張（bigram 的 Jaccard >= thr），回傳 (a 的 id, b 的 id)。"""
    out = []
    for x in a_claims:
        bx = bigrams(x["text"])
        best = max(((len(bx & bigrams(y["text"])) / max(1, len(bx | bigrams(y["text"]))), y["id"]) for y in b_claims), default=(0, ""))
        if best[0] >= thr:
            out.append((x["id"], best[1]))
    return out


def info(concept: str) -> dict:
    card = W.parse_card(W.WIKI / "wiki" / "concepts" / f"{concept}.md")
    sections = {s for src in card.front.get("sources", []) for s in src.get("sections", [])}
    used, defined = set(), set()
    for c in card.claims:
        ts = terms_of(c["text"])
        used |= ts
        if c.get("role") == "context":
            defined |= ts
    return {"id": concept, "title_terms": terms_of(card.front.get("title", "")), "claims": card.claims, "sections": sections, "related": set(card.front.get("related") or []),
            "parent": card.front.get("parent"), "used": used, "defined": defined}


def analyse(sid: str) -> list[dict]:
    s = load_series(sid)
    cards = [info(m["concept"]) for m in s["members"]]
    # 已經併入（also）的卡不再參與
    merged = {o for m in s["members"] for o in (m.get("also") or [])}
    cards = [c for c in cards if c["id"] not in merged]
    out = []
    for a, b in itertools.combinations(cards, 2):
        shared = sorted(a["sections"] & b["sections"])
        rel = b["id"] in a["related"] or a["id"] in b["related"]
        dep_ab = sorted((a["used"] - a["defined"]) & b["defined"])      # a 用了 b 定義的詞
        dep_ba = sorted((b["used"] - b["defined"]) & a["defined"])
        dups = dup_claims(a["claims"], b["claims"])
        a_on_b = sum(1 for c in a["claims"] if terms_of(c["text"]) & b["title_terms"])     # a 有幾條用到 b 的主題術語
        b_on_a = sum(1 for c in b["claims"] if terms_of(c["text"]) & a["title_terms"])
        if dups or rel or dep_ab or dep_ba or len(shared) >= 2 or a_on_b >= 2 or b_on_a >= 2:
            out.append({"a": a["id"], "b": b["id"], "dup_claims": dups, "shared_sections": shared, "related": rel,
                        "a_uses_b_terms": dep_ab, "b_uses_a_terms": dep_ba, "a_on_b": a_on_b, "b_on_a": b_on_a})
    out.sort(key=lambda p: (-(p["a_on_b"] + p["b_on_a"]), -len(p["dup_claims"])))
    return out


def main(sid: str) -> int:
    pairs = analyse(sid)
    print(f"== 系列 {sid} 的依賴檢查（輔助，不是判決）")
    if not pairs:
        print("  沒有找到信號。規劃系列時仍要問人：有沒有哪些卡要合併？")
        return 0
    for p in pairs:
        print(f"\n- {p['a']}  ↔  {p['b']}")
        if p["dup_claims"]:
            print(f"    有 {len(p['dup_claims'])} 條幾乎相同的主張：" + "、".join(f"{x}↔{y}" for x, y in p["dup_claims"]) + "（分開發要各解釋一次）")
        if p["a_on_b"] >= 2 or p["b_on_a"] >= 2:
            print(f"    {p['a']} 有 {p['a_on_b']} 條主張用了 {p['b']} 的主題術語；{p['b']} 有 {p['b_on_a']} 條用了 {p['a']} 的主題術語")
        if p["shared_sections"]:
            print(f"    共用 {len(p['shared_sections'])} 個來源小節（參考用，鑑別力差）")
        if p["related"]:
            print("    卡上互相列為 related")
        if p["a_uses_b_terms"]:
            print(f"    {p['a']} 用了 {p['b']} 定義的術語：{'、'.join(p['a_uses_b_terms'])}")
        if p["b_uses_a_terms"]:
            print(f"    {p['b']} 用了 {p['a']} 定義的術語：{'、'.join(p['b_uses_a_terms'])}")
    print("\n請把以上與你的判斷（讀者看得懂嗎？是同一段論述嗎？）一起交給人，問：哪些要合併成一則雙卡貼文？")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
