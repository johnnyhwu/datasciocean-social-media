"""驗證忠實者輸出（references/review-loop.md）：引用必須逐字出現在觀念卡；依分級規則彙整。

用法：uv run python .claude/skills/make-social-post/scripts/verify_faithful.py <card.md> <faithful.json>
分級同 verify_audit.py（references/review-loop.md「分級退回」）：
  擋下：不支持／找不到、引用捏造（審查者的錯，改列備註）、錯誤屬於
        範圍被放大、限定條件掉了、夾帶卡上沒有的判斷、數字對不上、因果說得比卡強、
        封面比內文說得滿、圖上缺單位或比較對象、串文描述對錯圖，
        或「錨點寫法不符」。
  只記錄：措辭與卡不同、其他、部分支持但無上述錯誤。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cardlib as W

BLOCKER = {"範圍被放大", "限定條件掉了", "夾帶卡上沒有的判斷", "數字對不上", "因果說得比卡強",
           "封面比內文說得滿", "圖上缺單位或比較對象", "串文描述對錯圖", "錨點寫法不符"}
ALL = BLOCKER | {"措辭與卡不同", "其他"}
VERDICTS = {"完全支持", "部分支持", "不支持", "找不到"}


def main(card_path: str, out_path: str) -> int:
    card = W.parse_card(Path(card_path))
    card_norm = W.normalize(" ".join(
        [c["text"] for c in card.claims]
        + [q for c in card.claims for q in c.get("source_quotes", [])]
        + [str(x.get("text", "")) + " " + str(x.get("source_quote", "")) for c in card.claims for x in c.get("qualifiers", [])]))
    data = json.loads(Path(out_path).read_text(encoding="utf-8"))
    blockers, notes = [], []
    for b in data.get("blocks", []):
        name = b.get("block", "?")
        bl, mi = [], []
        for a in b.get("atoms", []):
            v, q = a.get("verdict"), a.get("card_quote", "")
            if v not in VERDICTS:
                bl.append(f"判定值非法 {v!r}"); continue
            if q and not W.quote_in_text(q, card_norm):
                mi.append(f"審查者引用未逐字出現在卡（審查者的錯，需人眼確認）：{q[:30]!r} 原判定 {v}")
                continue
            if v in ("不支持", "找不到"):
                bl.append(f"{v}：{a.get('text','')[:40]!r}｜{a.get('note','')[:80]}")
            elif v == "部分支持":
                mi.append(f"部分支持：{a.get('text','')[:40]!r}｜{a.get('note','')[:80]}")
        for e in b.get("errors", []):
            if e not in ALL:
                notes.append(f"[{name}] 錯誤類別不在固定清單：{e!r}")
            elif e in BLOCKER:
                bl.append(f"固定錯誤：{e}")
            else:
                mi.append(f"固定錯誤：{e}")
        if bl:
            blockers.append(f"[{name}] " + "；".join(bl))
        if mi:
            notes.append(f"[{name}] minor：" + "；".join(mi))
    for g in data.get("gaps", []):
        notes.append(f"貼文漏掉：{g.get('description','')[:100]}")
    for r in data.get("recalculations", []):
        notes.append(f"重算 [{r.get('block')}] {r.get('expression')} = {r.get('result')}")
    print(f"== 忠實者 {data.get('post','')}: {'退回' if blockers else '通過'}（blocker {len(blockers)}，備註 {len(notes)}）")
    for x in blockers:
        print("  BLOCKER", x)
    for n in notes:
        print("  備註", n)
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
