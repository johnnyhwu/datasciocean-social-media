"""把一則貼文的投影片拼成一張縮圖總覽（給人看，也給撰寫者自己在交出前看一次）。

用法：uv run python .claude/skills/make-social-post/scripts/contact_sheet.py out/<series>/<concept>
輸出：out/<series>/<concept>/_build/contact-sheet.png
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def main(pack: Path) -> None:
    files = sorted((pack / "ig").glob("[0-9][0-9].png"))
    if not files:
        raise SystemExit(f"{pack}/ig 底下沒有投影片 PNG")
    tw = 360
    th = int(tw * 1350 / 1080)
    cols = 5
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 8) + 8), (60, 60, 60))
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((tw, th))
        sheet.paste(im, (8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 8)))
    out = (pack / "_build" if (pack / "_build").exists() else pack) / "contact-sheet.png"
    sheet.save(out)
    print(out, sheet.size, f"{len(files)} 張")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
