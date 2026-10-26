"""審查後的改動範圍：目前的 spec.json 和「上次審查通過的版本」差在哪些區塊（references/review-loop.md）。

用法：
  uv run python .claude/skills/make-social-post/scripts/spec_diff.py <spec.json>          列出改過的區塊（給忠實者的 {ONLY_BLOCKS}）
  uv run python .claude/skills/make-social-post/scripts/spec_diff.py <spec.json> --mark   把目前版本記為「審查通過」（_build/reviewed-spec.json）

另記每張 PNG 的雜湊（`_build/reviewed-images.json`）：審查通過後圖變了（例如改了圖型程式）會列「圖變了」，要讓讀者或重製圖審查者重看那幾張。
只比內容：區塊 = 第 N 張投影片、threads.body、threads.last、threads.items[N]、caption、hook、其他頂層欄位。
沒有記錄過審查版本時，列出全部（等於全面重審）。結束碼 0＝沒有改動、1＝有改動。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SNAP = "reviewed-spec.json"
IMG_SNAP = "reviewed-images.json"


def image_hashes(spec: Path) -> dict[str, str]:
    """發布包 ig/NN.png 的 sha256（spec 在 <包>/_build/ 下）。"""
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((spec.parent.parent / "ig").glob("[0-9][0-9].png"))}


def changed_images(old: dict | None, new: dict) -> list[str]:
    if old is None:           # 沒有記錄過（舊貼文）就不比
        return []
    return [f"圖變了：{k[:-4]}" for k in new if old.get(k) != new[k]]


def blocks(d: dict) -> dict[str, object]:
    out: dict[str, object] = {f"slide{i:02d}": sl for i, sl in enumerate(d.get("slides", []), 1)}
    th = d.get("threads", {})
    for k, v in th.items():
        if k == "items":
            out.update({f"threads.item{j}": it for j, it in enumerate(v, 1)})
        else:
            out[f"threads.{k}"] = v
    for k, v in d.items():
        if k not in ("slides", "threads"):
            out[k] = v
    return out


def changed(old: dict | None, new: dict) -> list[str]:
    nb = blocks(new)
    if old is None:
        return list(nb)
    ob = blocks(old)
    return [k for k in nb if ob.get(k) != nb[k]] + [f"{k}（已刪除）" for k in ob if k not in nb]


def main(argv: list[str]) -> int:
    spec = Path(argv[1]).resolve()
    snap = spec.parent / SNAP
    new = json.loads(spec.read_text(encoding="utf-8"))
    if "--mark" in argv:
        snap.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (spec.parent / IMG_SNAP).write_text(json.dumps(image_hashes(spec), indent=2) + "\n", encoding="utf-8")
        print(f"已記為審查通過版本：{snap}")
        return 0
    old = json.loads(snap.read_text(encoding="utf-8")) if snap.exists() else None
    ch = changed(old, new)
    isnap = spec.parent / IMG_SNAP
    ch += changed_images(json.loads(isnap.read_text(encoding="utf-8")) if isnap.exists() else None, image_hashes(spec))
    if old is None:
        print("沒有審查過的版本記錄：全部區塊都要審")
    print("改過的區塊：" + ("、".join(ch) if ch else "（沒有）"))
    return 1 if ch else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
