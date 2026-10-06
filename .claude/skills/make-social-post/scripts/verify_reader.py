"""驗證工程師讀者輸出（references/review-loop.md）：引用必須逐字出現在貼文。

用法：uv run python .claude/skills/make-social-post/scripts/verify_reader.py <post-reader.md> <reader.json> [--trap N ...]
- 快滑：必須講得出結論，且有有效引用（只看封面與主標）。
- 細讀：論點、機制、證據每題都要有有效引用。
- 只能從貼文回答的題目：只有陷阱題可答「貼文沒寫」，其他答沒寫算漏看；有答案卻無有效引用算硬答。
- 名詞 blocks_core=true 算退回。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cardlib as W

NONE = ("貼文沒寫", "貼文沒有", "講不出來", "沒寫")


def main(post: str, out: str, traps: list[int] | None) -> int:
    pn = W.normalize(Path(post).read_text(encoding="utf-8"))
    d = json.loads(Path(out).read_text(encoding="utf-8"))

    def cites(cs):
        ok, bad = 0, []
        for c in cs or []:
            q = c.get("quote", "")
            if q and W.quote_in_text(q, pn):
                ok += 1
            else:
                bad.append(q[:30])
        return ok, bad

    rej, notes = [], []
    sk = d.get("skim", {})
    ok, bad = cites(sk.get("citations"))
    if any(n in sk.get("conclusion", "") for n in ("講不出來",)) or ok == 0:
        rej.append("快滑：只看封面與主標講不出結論或沒有有效引用")
    if bad:
        notes.append(f"快滑有 {len(bad)} 筆引用不在貼文：{bad}")
    for key, label in (("thesis", "論點"), ("mechanism", "機制"), ("evidence", "證據")):
        it = (d.get("core") or {}).get(key) or {}
        ok, bad = cites(it.get("citations"))
        if ok == 0:
            rej.append(f"細讀「{label}」：沒有有效引用")
        if bad:
            notes.append(f"細讀「{label}」有 {len(bad)} 筆引用不在貼文：{bad}")
    for t in d.get("terms", []):
        (rej if t.get("blocks_core") else notes).append(f"名詞 {t.get('term')}：{t.get('note','')[:60]}")
    qs = d.get("post_only_questions", [])
    trap = set(traps or [len(qs)])
    for i, q in enumerate(qs, 1):
        said_none = any(n in q.get("answer", "") for n in NONE)
        ok, _ = cites(q.get("citations"))
        if i in trap:
            if not said_none:
                rej.append(f"陷阱題硬答：{q.get('q','')[:40]}")
        elif said_none:
            rej.append(f"漏看（貼文有答案卻答沒寫）：{q.get('q','')[:40]}")
        elif ok == 0:
            rej.append(f"硬答（沒有有效引用）：{q.get('q','')[:40]}")
        notes.append(f"題目：{q.get('q','')[:40]} → {'貼文沒寫' if said_none else q.get('answer','')[:50]}")
    feel = d.get("feel", {})
    if feel.get("felt_misled") and not str(feel["felt_misled"]).startswith(("沒有", "無", "否")):
        notes.append(f"讀者感受（被封面騙？）：{str(feel['felt_misled'])[:80]}")
    for u in feel.get("unclear_slides", []) or []:
        notes.append(f"讀者感受（看不懂）：{str(u)[:60]}")
    print(f"== 工程師讀者 {d.get('post','')}: {'退回' if rej else '通過'}（退回 {len(rej)}，備註 {len(notes)}）")
    for r in rej:
        print("  退回", r)
    for n in notes:
        print("  備註", n)
    return 1 if rej else 0


if __name__ == "__main__":
    args = sys.argv[3:]
    sys.exit(main(sys.argv[1], sys.argv[2], [int(a) for a in args[1:]] if args and args[0] == "--trap" else None))
