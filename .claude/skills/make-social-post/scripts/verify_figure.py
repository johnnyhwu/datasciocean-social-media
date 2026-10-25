"""驗證重製圖審查者的輸出（references/figure-prompt.md）：每張有 fig_refs 的投影片都要被審到、每個項目要有原圖位置與讀到的內容、錯誤必須在固定清單內。

用法：uv run python .claude/skills/make-social-post/scripts/verify_figure.py <spec.json> <figure.json>
擋下（退回）：沒被審到的投影片、項目判「不一致」或「原圖沒有」、缺原圖位置、錯誤屬於 blocker 清單。
只記錄：判「主張沒寫」（交人與忠實者的結果對照）、錯誤「其他」。
「僅來自主張」＝重製圖上的這個文字或元素是主張的內容、原圖沒畫但也不矛盾，不擋（不需原圖位置）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


BLOCKER = {"數字與原圖不一致", "關係與原圖不一致", "圖上超出主張", "範圍被放大", "圖例或範圍被省略",
           "搬了圖說原文", "說成自己的實驗", "原圖沒有的內容", "圖比原圖更容易誤解"}
ALL = BLOCKER | {"其他"}
VERDICTS = {"一致", "不一致", "原圖沒有", "主張沒寫", "僅來自主張"}


def main(spec_path: str, out_path: str) -> int:
    doc = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    need = {i for i, sl in enumerate(doc["slides"], 1) if sl.get("fig_refs")}
    data = json.loads(Path(out_path).read_text(encoding="utf-8"))
    got = {s.get("slide"): s for s in data.get("slides", [])}
    blockers, notes = [], []
    for i in sorted(need - set(got)):
        blockers.append(f"[第 {i} 張] 有 fig_refs 卻沒被審到")
    for i in sorted(set(got) - need):
        notes.append(f"[第 {i} 張] 不是有 fig_refs 的投影片，略過")
    for i in sorted(need & set(got)):
        s, bl, mi = got[i], [], []
        if not s.get("items"):
            bl.append("沒有逐項核對（items 為空）")
        for it in s.get("items", []):
            v = it.get("verdict")
            if v not in VERDICTS:
                bl.append(f"判定值非法 {v!r}"); continue
            if v != "僅來自主張" and (not str(it.get("original_position", "")).strip() or not str(it.get("original", "")).strip()):
                bl.append(f"沒寫原圖位置或讀到的內容：{it.get('what', '')[:30]!r}")
            if v in ("不一致", "原圖沒有"):
                bl.append(f"{v}：{it.get('what', '')[:40]!r}｜重製圖 {str(it.get('reproduced', ''))[:30]!r} 對原圖 {str(it.get('original', ''))[:30]!r}")
            elif v == "主張沒寫":
                mi.append(f"主張沒寫：{it.get('what', '')[:40]!r}")
        for e in s.get("errors", []):
            if e not in ALL:
                notes.append(f"[第 {i} 張] 錯誤類別不在固定清單：{e!r}")
            elif e in BLOCKER:
                bl.append(f"固定錯誤：{e}")
            else:
                mi.append(f"固定錯誤：{e}")
        if bl:
            blockers.append(f"[第 {i} 張] " + "；".join(bl))
        if mi:
            notes.append(f"[第 {i} 張] minor：" + "；".join(mi))
    print(f"== 重製圖審查者 {doc['concept']}: {'退回' if blockers else '通過'}（blocker {len(blockers)}，備註 {len(notes)}）")
    for x in blockers:
        print("  BLOCKER", x)
    for n in notes:
        print("  備註", n)
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
