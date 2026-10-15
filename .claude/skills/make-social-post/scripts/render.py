"""投影片渲染引擎與程式 B（references/program-b.md）。

內容規格 JSON -> 填入系列模板 -> Playwright 截圖 1080x1350 PNG -> 版面檢查。
外觀完全由模板決定；LLM 只給內容規格。

用法（repo 根目錄；Chromium 在 repo 內 .playwright-browsers/，程式會自己設好路徑）：
  uv run python .claude/skills/make-social-post/scripts/render.py out/<series>/<concept>/_build/spec.json [--only 3,5] [--force]
已發布的貼文預設拒絕（--force 才重渲）。
結束碼：0 全部通過、1 有程式 B 檢查不通過。
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import sys
from pathlib import Path

import yaml
from PIL import Image
from playwright.sync_api import sync_playwright

import cardlib as W
import diagrams as D

ROOT = W.ROOT
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".playwright-browsers"))
PARAMS = W.load_params()
RP = PARAMS["render"]
WD, HT, SAFE_X, PAD_X = RP["width"], RP["height"], RP["safe_x"], RP["pad_x"]
CREAM, TEAL, DEEP, GOLD = "#F2E0C0", "#076876", "#01353F", "#DDA642"
MID, LIGHT, ABYSS = "#1F8A8D", "#69B4AA", "#032027"
SERIES_COLORS = {"teal-mid": MID, "abyss-contour": LIGHT, "paper-cards": DEEP}
ALLOWED_FONT_PX = {28, 34, 38, 40, 56, 72, 76}
ZERO_Y = 706          # 測深圖水面（0）


def load_series(series_id: str) -> dict:
    txt = W.series_file(series_id).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    return yaml.safe_load(m.group(1))


def template_dir(series_id: str) -> Path:
    return W.series_dir(series_id) / "templates"


def template_hash(series_id: str) -> str:
    h = hashlib.sha1()
    for p in sorted(template_dir(series_id).glob("*")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def bind_nums(s: str) -> str:
    """數字與它的單位、前綴詞之間的空白改成不斷行空格，避免「1.87／秒」「只轉／25%」被拆成兩行。
    只在渲染時處理，spec 與 alt-text 保持原文。DSO_NO_NUMBIND=1 只給測試用（驗證程式 B 抓得到拆行）。"""
    if os.environ.get("DSO_NO_NUMBIND"):
        return s
    s = re.sub(r"(?<=[A-Za-z0-9])-(?=[A-Za-z0-9])", "-⁠", s)     # GPT-6、GPT-5.6：連字號後不斷行（不然會拆成「GPT-／6」）
    s = re.sub(r"(?<=[0-9%]) +(?=[\u4e00-\u9fff])", "\u00a0", s)      # 27% 的、GPT-6 單獨、1.87 秒
    return re.sub(r"(?<=[\u4e00-\u9fff]) +(?=[0-9])", "\u00a0", s)    # 只轉 25%、費用 27%


def title_html(s: str) -> str:
    return re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span class="hl">{esc(m.group(1))}</span>', esc(bind_nums(s)))


def plain(s: str) -> str:
    return re.sub(r"\[\[(.+?)\]\]", r"\1", s)


# ---------------------------------------------------------------- SVG 元件
def wave(y0, amp, wl, ph, fill):
    pts = [f"{x},{y0 + amp * math.sin(2 * math.pi * x / wl + ph):.1f}" for x in range(0, WD + 1, 10)]
    return f'<path class="bg" d="M{" L".join(pts)} L{WD},{HT} L0,{HT} Z" fill="{fill}"/>'


def defs():
    return (f'<defs><linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{TEAL}"/><stop offset=".38" stop-color="{DEEP}"/>'
            f'<stop offset="1" stop-color="{ABYSS}"/></linearGradient>'
            f'<radialGradient id="glow"><stop offset="0" stop-color="{GOLD}" stop-opacity=".42"/>'
            f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient></defs>')


def waves(y, series_color):
    return (wave(y, 5, 520, 0.0, LIGHT) + wave(y + 24, 5, 470, 1.4, series_color)
            + wave(y + 48, 5, 560, 2.6, TEAL) + wave(y + 72, 5, 500, 4.0, "url(#sea)"))


def svg_wrap(inner):
    return (f'<svg class="gfx" width="{WD}" height="{HT}" viewBox="0 0 {WD} {HT}" '
            f'xmlns="http://www.w3.org/2000/svg">{defs()}{inner}</svg>')


# ---------------------------------------------------------------- 等深線系列（style: contour）的 SVG 元件
# 都用 class "bg"（背景層，不進程式 B 的文字與圖形重疊檢查），所以排版時要自己確保不壓到文字（看圖確認）。
def ring(cx, cy, r, seed, n=120, wob=0.10):
    """不規則閉合等深線：半徑隨角度起伏（幾個低頻諧波疊加），seed 決定相位；橫向略寬。"""
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        k = 1 + wob * (math.sin(2 * a + seed) * .6 + math.sin(3 * a + seed * 1.7) * .3 + math.sin(5 * a + seed * .4) * .1)
        pts.append((cx + r * k * 1.18 * math.cos(a), cy + r * k * math.sin(a)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def contours(cx, cy, radii, color, op, sw=3, seed0=0.0):
    return "".join(f'<path class="bg" d="{ring(cx, cy, r, seed0 + i * .35)}" fill="none" stroke="{color}" '
                   f'stroke-opacity="{op}" stroke-width="{sw}"/>' for i, r in enumerate(radii))


def step_path(points, color, rejected=()):
    """步距遞減的路徑：點是每一步的落點，最後一點是目前的位置（金色，外圈淡光）；虛線小圓是被拒的落點。"""
    s = ""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        s += f'<line class="bg" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
    for x, y in points[:-1]:
        s += f'<circle class="bg" cx="{x}" cy="{y}" r="9" fill="{color}"/>'
    for x, y in rejected:
        s += f'<circle class="bg" cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="4 4"/>'
    x, y = points[-1]
    return s + (f'<circle class="bg" cx="{x}" cy="{y}" r="60" fill="{GOLD}" fill-opacity=".30"/>'
                f'<circle class="bg" cx="{x}" cy="{y}" r="15" fill="{GOLD}"/>')


# 完整的一條路徑（7 個落點，步距遞減，向谷底 (800,1010) 收攏）；封面與文字張只畫前 k 個。
COVER_PATH = [(250, 1060), (400, 1110), (505, 1075), (585, 1022), (650, 1003), (705, 1002), (760, 1008)]
COVER_RADII = [60, 130, 205, 285, 370, 460, 555, 655, 760]


# ---------------------------------------------------------------- 一式四份系列（style: cards）的 SVG 元件
# 一份來源文件，長出四張投影片：列＝受眾（上專家、下非專家），欄＝長度（左長版、右短版）；
# 長版條列多、短版條列少。金色只給一張卡（目前這一張在講的那一版）。
# 都用 class "bg"（背景層，不進程式 B 的文字與圖形重疊檢查），排版時要自己確保不壓到文字（看圖確認）。
CARD_BULLETS = [5, 2, 5, 3]         # 四張卡的條列數：專家長、專家短、非專家長、非專家短


def slide_card(x, y, w, h, nb, gold=False, dark=False, edge=False):
    """一張小投影片：頂端標題列，下面是帶圓點的條列。dark=True 用在深色底（只有細框）。"""
    k = w / 270
    s = ""
    if gold:
        s += f'<ellipse class="bg" cx="{x + w / 2:.1f}" cy="{y + h / 2:.1f}" rx="{w * .75:.1f}" ry="{h * .85:.1f}" fill="url(#glow)"/>'
    stroke = (f' stroke="{GOLD}" stroke-width="5"' if gold else (f' stroke="{LIGHT}" stroke-opacity=".6" stroke-width="3"' if dark else
              (f' stroke="{LIGHT}" stroke-opacity=".35" stroke-width="2"' if edge else "")))
    s += f'<rect class="bg" x="{x}" y="{y}" width="{w}" height="{h}" rx="{14 * k:.1f}" fill="{"none" if dark else "url(#sea)"}"{stroke}/>'
    c, op = (GOLD, 1) if gold else ((LIGHT, .6) if dark else (CREAM, 1))
    pad = w * .09
    s += f'<rect class="bg" x="{x + pad:.1f}" y="{y + pad:.1f}" width="{w * .42:.1f}" height="{11 * k:.1f}" rx="{5.5 * k:.1f}" fill="{c}" fill-opacity="{op}"/>'
    top = y + pad + 40 * k
    gap = (y + h - pad - top) / nb
    for i in range(nb):
        cy = top + i * gap + gap / 2
        s += f'<circle class="bg" cx="{x + pad + 6 * k:.1f}" cy="{cy:.1f}" r="{5 * k:.1f}" fill="{c}" fill-opacity="{op * .9:.2f}"/>'
        s += (f'<rect class="bg" x="{x + pad + 24 * k:.1f}" y="{cy - 4 * k:.1f}" width="{w - 2 * pad - 24 * k - (i % 3) * w * .1:.1f}" '
              f'height="{8 * k:.1f}" rx="{4 * k:.1f}" fill="{c}" fill-opacity="{op * .7:.2f}"/>')
    return s


def source_doc(x, y, w, h):
    """來源文件：米色紙面、藍綠細框、淡陰影、一疊字線。"""
    s = f'<rect class="bg" x="{x + 6}" y="{y + 9}" width="{w}" height="{h}" rx="10" fill="{DEEP}" fill-opacity=".14"/>'
    s += f'<rect class="bg" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CREAM}" stroke="{TEAL}" stroke-width="3"/>'
    n = int((h - 60) // 28)
    for i in range(n):
        s += f'<rect class="bg" x="{x + 24}" y="{y + 30 + i * 28}" width="{w - 48 - (i % 3) * 26}" height="8" rx="4" fill="{TEAL}" fill-opacity=".75"/>'
    return s


def link(d, color=TEAL, op=.6):
    return f'<path class="bg" d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="3"/>'


# 直切版面（2026-10-14 人選 H2）：右邊是一條深海直欄（x≥700），四張投影片錯開排列、橫跨米色與深色的交界（偶數張靠左、奇數張靠右一點），
# 金框一張一張往下換；封面左下角多一份來源文件，一條線接到最下面那張，再由一條匯流線往上分岔到其他三張。
# 圖表類版型要整幅寬度，改成右緣一條窄的索引欄（四張迷你投影片，金框同樣表示現在是哪一版）。
# 直欄與索引欄各有一個看不見的 class "g" 護欄矩形，文字壓進去程式 B 會抓到。
PANEL_X = 700       # 直欄左緣
GUARD_X = 620       # 護欄左緣：文字欄 80～600（寬 520），匯流線在 x=620
RAIL_X = 1032
CARD_W, CARD_H, CARD_GAP, CARD_Y0 = 400, 260, 36, 60


def stagger(gold, dark=False, doc=False):
    """四張投影片錯開排列。dark=True 用在深色整頁（帶走張）：直欄不畫，投影片只有細框。doc=True：左下角一份文件接到最下面那張。"""
    s = ""
    if not dark:
        s += f'<rect class="bg" x="{PANEL_X}" y="0" width="{WD - PANEL_X}" height="{HT}" fill="url(#sea)"/>'
    s += f'<rect class="g guard" x="{GUARD_X}" y="0" width="{WD - GUARD_X}" height="1300" fill="none" stroke="none"/>'
    xs = [640 + (k % 2) * 36 for k in range(4)]
    ys = [CARD_Y0 + k * (CARD_H + CARD_GAP) for k in range(4)]
    mids = [y + CARD_H / 2 for y in ys]
    if doc:
        dy = mids[3] - 125
        s += f'<g transform="rotate(-3 175 {mids[3]:.1f})">' + source_doc(80, dy, 190, 250) + '</g>'
        s += link(f"M270,{mids[3]:.1f} L{xs[3]},{mids[3]:.1f}")
        s += link(f"M{GUARD_X},{mids[3]:.1f} L{GUARD_X},{mids[0]:.1f}")
        for k in range(3):
            s += link(f"M{GUARD_X},{mids[k]:.1f} L{xs[k]},{mids[k]:.1f}")
        for k in range(4):
            s += f'<circle class="bg" cx="{GUARD_X}" cy="{mids[k]:.1f}" r="6" fill="{TEAL}" fill-opacity=".7"/>'
    for k in range(4):
        x, y = xs[k], ys[k]
        if not dark:
            s += f'<rect class="bg" x="{x + 8}" y="{y + 14}" width="{CARD_W}" height="{CARD_H}" rx="16" fill="{DEEP}" fill-opacity=".22"/>'
        s += slide_card(x, y, CARD_W, CARD_H, CARD_BULLETS[k], gold=(k == gold), dark=dark, edge=not dark)
    return s


def rail(gold):
    """圖表類版型的右緣索引欄：四張迷你投影片，金框 = 現在對應的版本。"""
    s = f'<rect class="bg" x="{RAIL_X}" y="0" width="{WD - RAIL_X}" height="{HT}" fill="{DEEP}"/>'
    s += f'<rect class="g guard" x="{RAIL_X}" y="0" width="{WD - RAIL_X}" height="1300" fill="none" stroke="none"/>'
    w, h, g = 30, 42, 16
    x, y0 = RAIL_X + 9, (HT - (4 * h + 3 * g)) / 2
    for k in range(4):
        y = y0 + k * (h + g)
        on = k == gold
        if on:
            s += f'<ellipse class="bg" cx="{x + w / 2}" cy="{y + h / 2}" rx="34" ry="40" fill="url(#glow)"/>'
        stroke = f' stroke="{GOLD}" stroke-width="3"' if on else f' stroke="{LIGHT}" stroke-opacity=".5" stroke-width="2"'
        s += f'<rect class="bg" x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="url(#sea)"{stroke}/>'
        c = GOLD if on else CREAM
        for j, ww in enumerate((18, 12)):
            s += f'<rect class="bg" x="{x + 6}" y="{y + 11 + j * 11}" width="{ww}" height="4" rx="2" fill="{c}" fill-opacity=".85"/>'
    return s


def progress_dots(idx, n, dark=False, panel=False):
    """內頁右下角的一排小點：點數 = 這則的張數，金色是現在這一張，已看過的實心、還沒看的空心。"""
    col = LIGHT if (dark or panel) else TEAL
    gap = min(30, 300 / max(n - 1, 1)) if panel else 30      # 直欄裡只有 300px 的寬度，張數多時縮小間距
    x0 = (1044 if panel else 1000) - (n - 1) * gap
    s = ""
    for k in range(1, n + 1):
        x = x0 + (k - 1) * gap
        if k == idx:
            s += f'<circle class="bg" cx="{x}" cy="1282" r="10" fill="{GOLD}"/>'
        elif k < idx:
            s += f'<circle class="bg" cx="{x}" cy="1282" r="6" fill="{col}"/>'
        else:
            s += f'<circle class="bg" cx="{x}" cy="1282" r="6" fill="none" stroke="{col}" stroke-width="3"/>'
    return s


def bob(x, y_end, col, v="", emph=False):
    g = ""
    if emph:
        g += f'<circle class="bg" cx="{x}" cy="{y_end:.1f}" r="95" fill="url(#glow)"/>'
    return g


def est_lines(txt: str, per_line: float) -> int:
    """模擬 word-break: keep-all：只在標點或空白後斷行，其餘中文連續串不可拆。per_line = 一行容納的全形字數。"""
    def width(t):
        return sum(0 if ch == "\u2060" else 0.35 if ch == "\u00a0" else 1 if ord(ch) > 127 else 0.55 for ch in t)
    chunks = [c for c in re.split(r"(?<=[、，；,;。：:」』）])|(?<= )", txt) if c]
    lines, cur = 1, 0.0
    for c in chunks:
        w = width(c)
        if cur + w > per_line and cur > 0:
            lines, cur = lines + 1, 0.0
        cur += w
        while cur > per_line:
            lines, cur = lines + 1, cur - per_line
    return lines


def body_end(body: str, size: int = 38, line_h: float = 1.6) -> float:
    """補充文字（top=352）排完的底部 y；圖與表從這之下再留一點空白開始。"""
    return 352 + est_lines(body, 920 / size - 0.5) * size * line_h


def table_block(rows: list, y0: float, key_w: int = 300) -> tuple[str, str, float]:
    """對照表的橫線與格子。鍵可以寫「主｜小字」，小字（例如指標名稱）排在主字下面。
    key_w：鍵欄寬（預設 300px）；鍵很短、值很長時調小，值欄就變寬、列數變少。"""
    vx = 80 + key_w + 20
    vw = 1000 - vx
    parts, cells, y = "", "", y0
    for (k, v) in rows:
        main, _, sub = k.partition("｜")
        parts += f'<line class="g sep" x1="80" y1="{y}" x2="1000" y2="{y}" stroke="{DEEP}" stroke-width="2" opacity=".35"/>'
        cells += f'<div class="t abs cell k" style="left:80px;top:{y + 28}px;width:{key_w}px">{esc(main)}</div>'
        if sub:
            cells += f'<div class="t abs cell ks" style="left:80px;top:{y + 28 + 57}px;width:{key_w}px">{esc(sub)}</div>'
        cells += f'<div class="t abs cell" style="left:{vx}px;top:{y + 28}px;width:{vw}px">{esc(bind_nums(v))}</div>'
        lines = max(est_lines(bind_nums(v), vw / 38 - 0.7), est_lines(main, key_w / 38 - 0.4) + (1 if sub else 0))   # 用綁定後的文字估：不斷行空格不能斷行
        y += 56 + lines * 57 + 8
    parts += f'<line class="g sep" x1="80" y1="{y}" x2="1000" y2="{y}" stroke="{DEEP}" stroke-width="2" opacity=".35"/>'
    return parts, cells, y


# ---------------------------------------------------------------- 各版型
def build(spec: dict, series: dict, tag: str) -> dict:
    """回傳 {layout, html_body, ...}。HTML 片段以模板檔填入。"""
    lay = spec["layout"]
    tdir = template_dir(series["id"])
    tpl = (tdir / f"{lay}.html").read_text(encoding="utf-8")
    sc = SERIES_COLORS.get(series.get("color"), MID)
    contour = series.get("style") == "contour"
    cards = series.get("style") == "cards"
    idx, n_sl = spec.get("_idx", 1), spec.get("_n", 1)          # 第幾張／共幾張（render_all 填入）
    mi, mn = spec.get("_mi", 0), spec.get("_mn", 1)            # 這則是系列的第幾則／共幾則
    kw = {"SERIES_TAG": esc(tag), "TITLE": title_html(spec.get("title", "")), "BODY": esc(bind_nums(spec.get("body", ""))), "FAM": "", "BODY_STYLE": ""}
    split = cards and (lay in ("cover", "text", "takeaway") or (lay == "context" and not spec.get("rows")))   # 直切版面（文字版型）
    if cards:
        kw["FAM"] = "split" if split else "rail"

    if lay in ("text", "table", "chart_bars", "chart_sounding", "diagram"):   # 小標籤（例如「我的判斷」）：右上角
        kw["LABEL"] = f'<div class="t abs chip">{esc(spec["label"])}</div>' if spec.get("label") else ""
    if lay == "cover" and contour:
        k = 4 + round(3 * mi / max(mn - 1, 1))                  # 越後面的一則，金點越靠近谷底
        kw["SVG"] = svg_wrap(contours(800, 1010, COVER_RADII, sc, .38) + step_path(COVER_PATH[:k], sc, rejected=[(610, 1090)]))
        kw["SUB_TOP"] = 560
        kw["BODY"] = kw["BODY"].replace("\n", "<br>")
    elif lay == "cover" and cards:     # 米色底；左邊文字欄，右邊直欄（文件在上、四張投影片由上疊到下）；金框每一則換一張
        kw["SVG"] = svg_wrap(stagger(mi % 4, doc=True))
        kw["SUB_TOP"] = 560
        kw["BODY"] = kw["BODY"].replace("\n", "<br>")
    elif lay == "cover":
        kw["SVG"] = svg_wrap(waves(1000, sc))
        kw["SUB_TOP"] = 560
        kw["BODY"] = kw["BODY"].replace("\n", "<br>")      # 副標可以用換行分成幾條
    elif lay == "context":
        if spec.get("rows"):      # 脈絡張也可以在補充下面放對照表（名詞表）
            y0_ = max(470, body_end(spec.get("body", ""), 40, 1.6) + 44)
            shift = 0
            if cards:     # 一式四份：補充加名詞表整塊，在標題下方到頁尾之間垂直置中（2026-10-14 人的回饋）
                _, _, yend = table_block(spec["rows"], y0_, spec.get("key_w", 300))
                shift = int(max(-52, min(200, 250 + (985 - (yend - 352)) / 2 - 352)))
                kw["BODY_STYLE"] = f"top:{352 + shift}px"
            parts, cells, _ = table_block(spec["rows"], y0_ + shift, spec.get("key_w", 300))
            kw["SVG"], kw["CELLS"] = svg_wrap(parts), cells
        else:
            kw["SVG"], kw["CELLS"] = (svg_wrap(stagger((idx - 1) % 4)) if cards else ""), ""
    elif lay == "text" and contour:
        k = 3 + round(3 * idx / max(n_sl, 1))                   # 同一則裡越後面的一張，路徑走得越遠
        # 最外圈的頂端要低於補充文字（最多 5 行，約到 y=690）：半徑上限 295 → 頂端約 y=795
        kw["SVG"] = svg_wrap(contours(620, 1120, [45, 100, 160, 225, 295], MID, .45, seed0=idx * .5)
                             + step_path([(x - 150, y + 110) for (x, y) in COVER_PATH[:k]], TEAL))
    elif lay == "text" and cards:      # 下方一排四張小投影片；金框每一張換到下一張
        kw["SVG"] = svg_wrap(stagger((idx - 1) % 4))
    elif lay == "text":
        kw["SVG"] = svg_wrap(
            waves(760, sc)
            + f'<g><line class="g deco" x1="540" y1="832" x2="540" y2="1040" stroke="{CREAM}" stroke-width="4"/>'
              f'<circle class="bg" cx="540" cy="1040" r="95" fill="url(#glow)"/>'
              f'<polygon class="g deco" data-e="1" points="540,1028 548,1040 540,1052 532,1040" fill="{GOLD}"/></g>')
    elif lay == "table":
        parts, cells, _ = table_block(spec["rows"], max(500, body_end(spec.get("body", "")) + 44), spec.get("key_w", 300))
        kw["SVG"] = svg_wrap(parts)
        kw["CELLS"] = cells
        kw["NOTE_BLOCK"] = (f'<div class="t abs note" style="left:80px;top:1196px">{esc(spec["note"])}</div>' if spec.get("note") else "")
    elif lay == "diagram":
        y0 = max(480, body_end(spec.get("body", "")) + 36)
        svg, labels, bottom = D.build(spec, y0, D.Ctx(est_lines, bind_nums, esc))
        kw["SVG"], kw["LABELS"] = svg_wrap(svg), labels
        kw["NOTE_BLOCK"] = (f'<div class="t abs note" style="left:80px;top:1196px">{esc(spec["note"])}</div>' if spec.get("note") else "")
    elif lay == "chart_bars" and any("value2" in b for b in spec["bars"]):
        # 成對橫條圖：每組（例如每個任務）兩條橫條，同一個 0 起點、同一個比例尺，用來看兩個量一起怎麼變
        # （2026-10-10：「轉出比例」與「費用」要放在一起看，單一橫條圖看不出它們同步變動）。
        bars = spec["bars"]
        x0, maxlen = 430, 400
        s = maxlen / spec.get("axis_max", max(max(b["value"], b["value2"]) for b in bars))
        l1, l2 = spec["legend"]
        y0 = max(500, body_end(spec.get("body", "")) + 44)
        x2 = 120 + len(l1) * 28 + 60
        svg = (f'<rect class="g deco" x="80" y="{y0 + 9}" width="28" height="28" fill="{MID}"/>'
               f'<rect class="g deco" x="{x2}" y="{y0 + 9}" width="28" height="28" fill="{DEEP}"/>')
        labels = (f'<div class="t abs legend" style="left:120px;top:{y0}px">{esc(l1)}</div>'
                  f'<div class="t abs legend" style="left:{x2 + 40}px;top:{y0}px">{esc(l2)}</div>')
        gy = y0 + 62
        step = max(140.0, min(190.0, (1150 - gy) / len(bars)))
        top, last_bottom = gy - 14, gy
        for b in bars:
            subs = b.get("subs", [])           # 名稱下面的小字（例如這個任務的準確度）；有小字時名稱上移
            ny = gy + (2 if subs else 22)
            labels += f'<div class="t abs name" style="left:80px;top:{ny}px">{esc(b["name"])}</div>'
            for k_, sline in enumerate(subs):
                labels += f'<div class="t abs sub" style="left:80px;top:{ny + 51 + k_ * 42}px">{esc(bind_nums(sline))}</div>'
            for j, (v, col) in enumerate(((b["value"], MID), (b["value2"], DEEP))):
                by = gy + j * 60
                ln = v * s
                svg += (f'<rect class="g bar" data-v="{v}" data-e="0" x="{x0}" y="{by}" width="{ln:.2f}" height="44" fill="{col}"/>')
                labels += (f'<div class="t abs num2" style="left:{x0 + ln + 18:.1f}px;top:{by - 2}px;color:{DEEP}">'
                           f'{v:g}{esc(spec.get("unit", ""))}</div>')
                last_bottom = by + 44
            gy += step
        svg += f'<line class="g axis" x1="{x0}" y1="{top}" x2="{x0}" y2="{last_bottom + 10}" stroke="{DEEP}" stroke-width="3"/>'
        kw["SVG"] = svg_wrap(svg)
        kw["LABELS"] = labels
        kw["NOTE"] = esc(spec.get("note", ""))
    elif lay == "chart_bars":
        bars = spec["bars"]
        x0, maxlen = 72, 640
        s = maxlen / max(b["value"] for b in bars)
        y = max(500, body_end(spec.get("body", "")) + 44)   # 補充排成多行時，圖往下讓出空間
        inline = bool(spec.get("subs_inline"))              # 副標籤接在名稱後面同一行（省 42px，長條才排得下）
        labels, svg = "", ""
        top = y - 20
        # 條數少、空間有剩時，拉開長條的間距，把圖面用滿（只對 subs_inline 的圖；舊圖維持原間距）
        step = max(162.0, min(240.0, (1150 - y) / len(bars))) if inline else None
        last_bottom = y
        for b in bars:
            subs = b.get("subs", [])
            if inline:
                si = "　".join(subs)
                labels += (f'<div class="t abs name" style="left:80px;top:{y}px">{esc(b["name"])}'
                           + (f'<span class="subi">　{esc(si)}</span>' if si else "") + '</div>')
                ty = y + 54
            else:
                labels += f'<div class="t abs name" style="left:80px;top:{y}px">{esc(b["name"])}</div>'
                ty = y + 54
                for sline in subs:
                    labels += f'<div class="t abs sub" style="left:80px;top:{ty}px">{esc(sline)}</div>'
                    ty += 42
            by = ty + 14
            ln = b["value"] * s
            col = GOLD if b.get("emphasize") else TEAL
            svg += (f'<rect class="g bar" data-v="{b["value"]}" data-e="{int(bool(b.get("emphasize")))}" x="{x0}" y="{by}" '
                    f'width="{ln:.2f}" height="44" fill="{col}"/>')
            labels += (f'<div class="t abs num" style="left:{x0 + ln + 22:.1f}px;top:{by - 11}px;color:{DEEP}">'
                       f'{b["value"]:g}{esc(spec.get("unit", ""))}</div>')
            last_bottom = by + 44
            y = (y + step) if inline else (by + 44 + 50)
        svg += f'<line class="g axis" x1="{x0}" y1="{top}" x2="{x0}" y2="{last_bottom + 10}" stroke="{DEEP}" stroke-width="3"/>'
        kw["SVG"] = svg_wrap(svg)
        kw["LABELS"] = labels
        kw["NOTE"] = esc(spec.get("note", ""))
    elif lay == "chart_sounding":
        bars = spec["bars"]
        maxv = max(b["value"] for b in bars)
        S = math.floor(424 / maxv * 100) / 100
        unit_ticks = next(u for u in [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000] if S * u >= 40)
        xs = [110, 425, 740][: len(bars)]
        svg = waves(470, sc) + (f'<line class="g zero" x1="56" y1="{ZERO_Y}" x2="1024" y2="{ZERO_Y}" '
                               f'stroke="{CREAM}" stroke-width="2" opacity=".85"/>')
        k = 1
        while ZERO_Y + k * unit_ticks * S <= 1170:
            y = ZERO_Y + k * unit_ticks * S
            L = 44 if k % 4 == 0 else 26
            for x1, x2 in ((0, L), (WD - L, WD)):
                svg += (f'<line class="g tick" data-k="{k}" x1="{x1}" y1="{y:.2f}" x2="{x2}" y2="{y:.2f}" '
                        f'stroke="{LIGHT}" stroke-width="3"/>')
            k += 1
        labels = ""
        for x, b in zip(xs, bars):
            y_end = ZERO_Y + b["value"] * S
            emph = bool(b.get("emphasize"))
            col = GOLD if emph else CREAM
            if emph:
                svg += f'<circle class="bg" cx="{x}" cy="{y_end:.1f}" r="95" fill="url(#glow)"/>'
            svg += (f'<g data-e="{int(emph)}"><line class="g rope" data-v="{b["value"]}" x1="{x}" y1="{ZERO_Y}" '
                    f'x2="{x}" y2="{y_end:.2f}" stroke="{col}" stroke-width="4"/>'
                    f'<polygon class="g bob" data-v="{b["value"]}" points="{x},{y_end - 12:.2f} {x + 8},{y_end:.2f} '
                    f'{x},{y_end + 12:.2f} {x - 8},{y_end:.2f}" fill="{col}"/></g>')
            subs = "".join(f'<div class="t sub">{esc(s)}</div>' for s in b.get("subs", []))
            labels += (f'<div class="abs" style="left:{x}px;top:566px;color:{CREAM}"><div class="t name">{esc(b["name"])}</div>{subs}</div>')
            labels += (f'<div class="t abs num" style="left:{x + 28}px;top:{max(y_end - 33, ZERO_Y + 24):.1f}px">'
                       f'{b["value"]:g} {esc(spec.get("unit", ""))}</div>')
        kw["SVG"] = svg_wrap(svg)
        kw["LABELS"] = labels
        kw["LEGEND"] = f'刻度每格 {unit_ticks:g} {esc(spec.get("unit", ""))}'
        kw["NOTE"] = esc(spec.get("note", ""))
        spec["_S"], spec["_unit_ticks"] = S, unit_ticks
    elif lay == "takeaway" and (contour or cards):
        kw["TITLE"] = kw["TITLE"].replace("\n", "<br>")
        q = spec.get("question")
        kw["QUESTION"] = f'<div class="t abs take-q" style="top:320px">{esc(q)}</div>' if q else ""
        kw["TAKE_STYLE"] = (f"top:{320 + est_lines(q, 520 / 56 - 0.4) * 73 + 36}px" if cards else f"top:{320 + math.ceil(len(q) / 15.0) * 73 + 36}px") if q else ""
        lab = spec.get("label")
        kw["LABEL"] = f'<div class="t abs take-label" style="top:370px">{esc(lab)}</div>' if lab else ""
        kw["SVG"] = (svg_wrap(contours(800, 1200, [60, 130, 205, 285, 370, 460], LIGHT, .30) + step_path(COVER_PATH, LIGHT)) if contour
                     else svg_wrap(stagger(mi % 4, dark=True)))
    elif lay == "takeaway":
        kw["TITLE"] = kw["TITLE"].replace("\n", "<br>")      # 兩關這類並列的結論，可以用換行分成幾條
        q = spec.get("question")        # 先問一個問題，再給答案（讀者才知道這句話在回答什麼）
        kw["QUESTION"] = f'<div class="t abs take-q" style="top:320px">{esc(q)}</div>' if q else ""
        kw["TAKE_STYLE"] = f"top:{320 + math.ceil(len(q) / 15.0) * 73 + 36}px" if q else ""
        lab = spec.get("label")
        kw["LABEL"] = f'<div class="t abs take-label" style="top:370px">{esc(lab)}</div>' if lab else ""
        lines = "".join(
            f'<polyline class="bg" fill="none" stroke="{LIGHT}" stroke-opacity=".28" stroke-width="3" points="' +
            " ".join(f"{x},{y + 7 * math.sin(2 * math.pi * x / wl + ph):.1f}" for x in range(0, WD + 1, 10)) + '"/>'
            for y, wl, ph in ((1090, 520, 0.0), (1130, 470, 1.4), (1170, 560, 2.6)))
        kw["SVG"] = svg_wrap(lines)
    elif lay == "series_map":
        items = [m["planned_title"] for m in series["members"]]
        cur = [m["concept"] for m in series["members"]].index(spec["current"])
        y, svg, out = 330, "", ""
        for i, t in enumerate(items):
            if (contour or cards) and i == cur:
                svg += f'<rect class="bg" x="72" y="{y - 10}" width="936" height="84" rx="6" fill="{DEEP}"/>'
                svg += f'<circle class="g mark" data-e="1" cx="100" cy="{y + 32}" r="12" fill="{GOLD}"/>'
                out += f'<div class="t abs item cur" style="left:132px;top:{y + 8}px">{esc(t)}</div>'
            elif contour or cards:
                svg += f'<circle class="g mark" cx="100" cy="{y + 32}" r="8" fill="{TEAL}"/>'
                out += f'<div class="t abs item" style="left:132px;top:{y + 8}px">{esc(t)}</div>'
            elif i == cur:
                svg += f'<rect class="bg" x="72" y="{y - 10}" width="936" height="84" rx="6" fill="{DEEP}"/>'
                svg += f'<polygon class="g mark" data-e="1" points="100,{y + 20} 112,{y + 32} 100,{y + 44} 88,{y + 32}" fill="{GOLD}"/>'
                out += f'<div class="t abs item cur" style="left:132px;top:{y + 8}px">{esc(t)}</div>'
            else:
                svg += f'<polygon class="g mark" points="100,{y + 24} 108,{y + 32} 100,{y + 40} 92,{y + 32}" fill="{TEAL}"/>'
                out += f'<div class="t abs item" style="left:132px;top:{y + 8}px">{esc(t)}</div>'
            y += 112
        if contour:      # 下半部：粗一點的等深線，一條朝圓心收斂的路徑；每一則是路徑上的一個節點（目前這則金色），最後一則落在最內圈裡
            cx, cy = 790, 935
            svg += contours(cx, cy, [55, 115, 180, 250, 320], MID, .55, sw=4)
            S_, T_ = (150.0, 1060.0), (float(cx), float(cy))
            nx_, ny_ = (T_[1] - S_[1]), -(T_[0] - S_[0])
            nl_ = math.hypot(nx_, ny_); nx_, ny_ = nx_ / nl_, ny_ / nl_
            N_ = 12
            pts_ = []
            for i_ in range(N_ + 1):
                t_ = i_ / N_
                off_ = (1 if i_ % 2 else -1) * 70 * (1 - t_) ** 1.5 * (1 if i_ else 0)
                pts_.append((S_[0] + (T_[0] - S_[0]) * t_ + nx_ * off_, S_[1] + (T_[1] - S_[1]) * t_ + ny_ * off_))
            svg += f'<polyline class="bg" points="{" ".join(f"{x_:.1f},{y_:.1f}" for x_, y_ in pts_)}" fill="none" stroke="{TEAL}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>'
            marks_ = {round((k_ + 1) / mn * N_) for k_ in range(mn)}
            for i_, (x_, y_) in enumerate(pts_):
                if i_ not in marks_:
                    svg += f'<circle class="bg" cx="{x_:.1f}" cy="{y_:.1f}" r="7" fill="{TEAL}"/>'
            for k_ in range(mn):
                x_, y_ = pts_[round((k_ + 1) / mn * N_)]
                if k_ == mi:
                    svg += (f'<circle class="bg" cx="{x_:.1f}" cy="{y_:.1f}" r="52" fill="{GOLD}" fill-opacity=".30"/>'
                            f'<circle class="bg" cx="{x_:.1f}" cy="{y_:.1f}" r="22" fill="{GOLD}"/>')
                else:
                    svg += f'<circle class="bg" cx="{x_:.1f}" cy="{y_:.1f}" r="16" fill="{CREAM}" stroke="{TEAL}" stroke-width="6"/>'
        if cards:    # 下半部：左邊一份來源文件，右邊一排 mn 張投影片，一張是一則（目前這則金框），相鄰兩張之間有短連線
            svg += source_doc(80, 860, 170, 230)
            cw_, cg_ = 200, 24
            x0_ = 1000 - mn * cw_ - (mn - 1) * cg_
            svg += link(f"M250,975 L{x0_},975")
            for k_ in range(mn):
                x_ = x0_ + k_ * (cw_ + cg_)
                svg += slide_card(x_, 900, cw_, 150, CARD_BULLETS[k_ % 4], gold=(k_ == mi))
                if k_ < mn - 1:
                    svg += link(f"M{x_ + cw_},975 L{x_ + cw_ + cg_},975")
        kw["SVG"] = svg_wrap(svg)
        kw["ITEMS"] = out
        kw["NAV"] = esc(spec.get("nav", ""))
    else:
        raise ValueError(f"未知版型 {lay}")

    if (contour or cards) and lay not in ("cover", "takeaway"):
        dots = progress_dots(idx, n_sl, panel=split)
        if cards and not split:      # 圖表類版型：右緣的索引欄（金框 = 這一張對應的版本；系列地圖用這一則）
            dots += rail(mi % 4 if lay == "series_map" else (idx - 1) % 4)
        kw["SVG"] = kw["SVG"].replace("</svg>", dots + "</svg>") if kw.get("SVG") else svg_wrap(dots)

    # 模板填入
    for k, v in kw.items():
        tpl = tpl.replace("{{" + k + "}}", str(v))
    assert "{{" not in tpl, re.findall(r"\{\{\w+\}\}", tpl)
    # 沒有圖註時，模板裡的空圖註框會被邊界檢查量成 left=0，填完後拿掉
    tpl = re.sub(r'<div class="t abs note"[^>]*></div>', "", tpl)
    return {"body": tpl, "dyn": split}


MEASURE_JS = r"""
() => {
  const tight = e => {const r=document.createRange(); r.selectNodeContents(e); const b=r.getBoundingClientRect();
    return {l:b.left,r:b.right,t:b.top,b:b.bottom}};
  const box = e => {const b=e.getBoundingClientRect(); return {l:b.left,r:b.right,t:b.top,b:b.bottom}};
  const ts=[...document.querySelectorAll('.t')].filter(e=>!e.querySelector('.t')).map(e=>({
     n:e.textContent.trim().slice(0,16), r:tight(e), fs:parseFloat(getComputedStyle(e).fontSize),
     c:getComputedStyle(e).color, ov:e.scrollWidth>e.clientWidth+1}));
  const gs=[...document.querySelectorAll('.g')].map(e=>{const b=box(e), sw=(parseFloat(getComputedStyle(e).strokeWidth)||0)/2;
    return {n:(e.getAttribute('class')||'')+(e.dataset.v||e.dataset.k||''), r:{l:b.l-sw,r:b.r+sw,t:b.t-sw,b:b.b+sw}}});
  const ropes=[...document.querySelectorAll('.rope')].map(e=>({v:+e.dataset.v,len:Math.abs(e.y2.baseVal.value-e.y1.baseVal.value)}));
  const bobs=[...document.querySelectorAll('.bob')].map(e=>{const p=e.points; return {v:+e.dataset.v,cy:(p[0].y+p[2].y)/2}});
  const bars=[...document.querySelectorAll('.bar')].map(e=>({v:+e.dataset.v,len:e.width.baseVal.value,x:e.x.baseVal.value}));
  const axis=[...document.querySelectorAll('.axis')].map(e=>e.x1.baseVal.value);
  const ticks=[...document.querySelectorAll('.tick')].filter(e=>e.x1.baseVal.value===0).map(e=>e.y1.baseVal.value);
  const inbox=[...document.querySelectorAll('[data-box]')].map(e=>{const [l,t,w,h]=e.dataset.box.split(',').map(Number);
    const rg=tight(e); return {n:e.textContent.trim().slice(0,14),out:rg.l<l-1||rg.r>l+w+1||rg.t<t-1||rg.b>t+h+1}});
  const rbars=[...document.querySelectorAll('.rbar')].map(e=>({lo:+e.dataset.lo,hi:+e.dataset.hi,s:+e.dataset.s,x0:+e.dataset.x0,
    x:e.tagName==='rect'?e.x.baseVal.value:null,w:e.tagName==='rect'?e.width.baseVal.value:null}));
  const dpts=[...document.querySelectorAll('.dpt')].map(e=>({v:+e.dataset.v,s:+e.dataset.s,x0:+e.dataset.x0,cx:e.cx.baseVal.value}));
  const emph=document.querySelectorAll('[data-e="1"]').length;
  function lines(el){
    const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT); const chars=[]; let n;
    while(n=w.nextNode()){ for(let i=0;i<n.length;i++){const rg=document.createRange(); rg.setStart(n,i); rg.setEnd(n,i+1);
      const r=rg.getClientRects()[0]; chars.push({c:n.data[i], top:r?Math.round(r.top):null});}}
    const text=chars.map(x=>x.c).join(''); const tops=chars.map(x=>x.top);
    const real=tops.filter(t=>t!==null); const uniq=[...new Set(real)].sort((a,b)=>a-b);
    const cl=[]; uniq.forEach(t=>{ if(!cl.length||t-cl[cl.length-1]>6) cl.push(t); });
    const lineOf=t=>cl.reduce((acc,c,i)=>t>=c-6?i:acc,0);
    const L=tops.map(t=>t===null?null:lineOf(t));
    const starts=[]; for(let i=1;i<L.length;i++) if(L[i]!==null&&L[i-1]!==null&&L[i]>L[i-1]) starts.push(i);
    const seg=[...new Intl.Segmenter('zh',{granularity:'word'}).segment(text)];
    const bad=starts.filter(i=>seg.some(g=>g.index<i&&i<g.index+g.segment.length)).map(i=>text.slice(Math.max(0,i-2),i+2));
    const lastLine=Math.max(...L.filter(x=>x!==null)); const lastChars=L.filter(x=>x===lastLine).length;
    const cjk=c=>/[\u4e00-\u9fff]/.test(c||''), num=c=>/[0-9.%]/.test(c||''), sp=c=>/[\s\u00a0]/.test(c||'');
    const badNum=starts.filter(i=>{let j=i-1; while(j>=0&&sp(text[j])) j--;
      return (num(text[j])&&cjk(text[i]))||(cjk(text[j])&&/[0-9]/.test(text[i]))||(text[j]==='-'&&/[0-9A-Za-z]/.test(text[i]));}).map(i=>text.slice(Math.max(0,i-3),i+3));
    return {lines:cl.length,lastChars,bad,badNum,text};
  }
  const chk={}; document.querySelectorAll('.chk').forEach(e=>chk[e.id]=lines(e));
  return {ts,gs,ropes,bobs,bars,axis,ticks,emph,chk,inbox,rbars,dpts,
    pageH:document.documentElement.scrollHeight,pageW:document.documentElement.scrollWidth,
    fontOk:document.fonts.check('700 40px DSO')&&document.fonts.check('400 40px DSO')};
}
"""


def lum(c):
    c = [x / 255 for x in c]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + .05) / (lb + .05)


def inter(a, b):
    return max(0, min(a["r"], b["r"]) - max(a["l"], b["l"])) > 1 and max(0, min(a["b"], b["b"]) - max(a["t"], b["t"])) > 1


def program_b(spec: dict, m: dict, img: Image.Image, series_name: str, tag_texts: list[str]) -> list[tuple]:
    res = []
    chk = lambda n, ok, d="": res.append((n, bool(ok), str(d)))
    lay = spec["layout"]
    chk("尺寸 1080x1350、無捲動溢出", m["pageH"] <= HT and m["pageW"] <= WD, f"scroll={m['pageW']}x{m['pageH']}")
    chk("字型已內嵌載入（Noto Sans CJK TC）", m["fontOk"])
    lo = min(t["r"]["l"] for t in m["ts"]); hi = max(t["r"]["r"] for t in m["ts"])
    chk(f"文字左右邊界 >= {SAFE_X}px", lo >= SAFE_X and hi <= WD - SAFE_X, f"最小左={lo:.0f}, 最大右={hi:.0f}")
    chk("文字框無橫向溢出", not any(t["ov"] for t in m["ts"]), [t["n"] for t in m["ts"] if t["ov"]])
    low = max([t["r"]["b"] for t in m["ts"]] + [g["r"]["b"] for g in m["gs"]])
    chk(f"文字與圖形不超出版面下緣（至少留 20px）", low <= HT - 20, f"最低 {low:.0f}px，版面 {HT}px")
    tt = [(a["n"], b["n"]) for i, a in enumerate(m["ts"]) for b in m["ts"][i + 1:] if inter(a["r"], b["r"])]
    chk("文字與文字不重疊", not tt, tt)
    tg = [(t["n"], g["n"]) for t in m["ts"] for g in m["gs"] if inter(t["r"], g["r"])]
    chk("文字與圖形不重疊（圖形邊界框含線寬）", not tg, tg[:4])
    fs = {t["fs"] for t in m["ts"]}
    chk(f"最小字級 >= {RP['min_font_px']}px", min(fs) >= RP["min_font_px"], f"最小 {min(fs)}px")
    chk("字級都在規定集合內", fs <= ALLOWED_FONT_PX, sorted(fs - ALLOWED_FONT_PX))
    worst = (99, "")
    for t in m["ts"]:
        r = t["r"]; fg = tuple(int(x) for x in re.findall(r"\d+", t["c"])[:3])
        for (x, y) in ((r["l"] - 3, r["t"] - 3), (r["r"] + 3, r["t"] - 3), (r["l"] - 3, r["b"] + 3), (r["r"] + 3, r["b"] + 3)):
            x = min(max(int(x), 0), WD - 1); y = min(max(int(y), 0), HT - 1)
            cr = contrast(fg, img.getpixel((x, y)))
            if cr < worst[0]:
                worst = (cr, t["n"])
    chk(f"文字對比度 >= {RP['min_contrast']}（取文字框外緣四角的實際背景色）", worst[0] >= RP["min_contrast"], f"最低 {worst[0]:.1f}（{worst[1]}）")
    ti = m["chk"].get("title")
    if ti:
        mx = 4 if lay == "takeaway" else (3 if spec.get("_split") else PARAMS["title_max_lines"])
        chk(f"標題最多 {mx} 行", ti["lines"] <= mx, f"{ti['lines']} 行")
        chk("標題末行 >= 2 字、換行不拆詞", ti["lastChars"] >= 2 and not ti["bad"], {"lastChars": ti["lastChars"], "bad": ti["bad"]})
        chk("標題的數字與單位不拆成兩行", not ti["badNum"], ti["badNum"])
    bo = m["chk"].get("body")
    if bo:
        if lay in ("table", "chart_bars", "chart_sounding", "diagram"):
            chk("圖表版型補充最多五行、不拆詞", bo["lines"] <= 5 and not bo["bad"], {"lines": bo["lines"], "bad": bo["bad"]})
        else:
            chk("補充不拆詞、末行 >= 2 字", not bo["bad"] and (bo["lines"] == 1 or bo["lastChars"] >= 2), {"lines": bo["lines"], "bad": bo["bad"], "lastChars": bo["lastChars"]})
    if bo:
        chk("補充的數字與單位不拆成兩行", not bo["badNum"], bo["badNum"])
    if m["ropes"]:
        rat = [r["len"] / r["v"] for r in m["ropes"]]
        chk("測深繩長與數值成正比（水面為 0）", max(rat) / min(rat) < 1.01, f"每單位 {min(rat):.3f}~{max(rat):.3f}px")
        S = spec["_S"]
        chk("菱形中心落在繩端", all(abs(b["cy"] - (ZERO_Y + b["v"] * S)) < 1 for b in m["bobs"]))
        gap = [m["ticks"][i + 1] - m["ticks"][i] for i in range(len(m["ticks"]) - 1)]
        if gap:
            chk("刻度等距且間距 = 單位 x 每單位像素", max(gap) - min(gap) < .5 and abs(gap[0] - spec["_unit_ticks"] * S) < .5,
                f"間距 {gap[0]:.1f}px，預期 {spec['_unit_ticks'] * S:.1f}px")
    if m["bars"]:
        rat = [b["len"] / b["v"] for b in m["bars"]]
        chk("橫條長度與數值成正比、軸從 0 起", max(rat) / min(rat) < 1.01 and all(abs(b["x"] - m["axis"][0]) <= 1 for b in m["bars"]),
            f"每單位 {min(rat):.3f}~{max(rat):.3f}px")
    if m["inbox"]:
        bad = [b["n"] for b in m["inbox"] if b["out"]]
        chk("框內文字不超出框（示意圖）", not bad, bad)
    if m["rbars"]:
        ok = all((abs(r["x"] - (r["x0"] + r["lo"] * r["s"])) < 1 and abs(r["w"] - (r["hi"] - r["lo"]) * r["s"]) < 1) for r in m["rbars"] if r["x"] is not None)
        chk("區間條的位置與長度和數值成正比（軸從 0 起）", ok, [(r["lo"], r["hi"]) for r in m["rbars"]])
    if m["dpts"]:
        chk("前後對比的點落在數值對應的位置（軸從 0 起）", all(abs(p["cx"] - (p["x0"] + p["v"] * p["s"])) < 1 for p in m["dpts"]), [p["v"] for p in m["dpts"]])
    if lay not in ("cover", "context", "takeaway"):
        chk("只有一組強調元素", m["emph"] <= 1, m["emph"])
    chk("系列標籤與系列檔的名稱完全相同", all(t == series_name for t in tag_texts), tag_texts)
    return res


def render_all(spec_path: Path, only: set[int] | None = None, force: bool = False) -> int:
    doc = json.loads(spec_path.read_text(encoding="utf-8"))
    W.guard_published(doc, force)
    series = load_series(doc["series"])
    series["id"] = series.get("id", doc["series"])
    tag = series["name"]
    pack, bld = W.pack_dir(spec_path), W.build_dir(spec_path)
    outdir = pack / "ig"
    htmldir = bld / "html"
    outdir.mkdir(parents=True, exist_ok=True); htmldir.mkdir(parents=True, exist_ok=True)
    css = (template_dir(series["id"]) / "style.css").read_text(encoding="utf-8")
    css = css.replace("{{FONT_REGULAR}}", (ROOT / "assets/fonts/NotoSansCJKtc-Regular.otf").as_uri())
    css = css.replace("{{FONT_BOLD}}", (ROOT / "assets/fonts/NotoSansCJKtc-Bold.otf").as_uri())
    thash = template_hash(series["id"])
    report, alts, failed = [], {}, 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": WD, "height": HT})
        for i, sl in enumerate(doc["slides"], 1):
            if only and i not in only:
                continue
            sl = dict(sl)
            sl["_idx"], sl["_n"] = i, len(doc["slides"])
            mids = [m_["concept"] for m_ in series["members"]]
            sl["_mi"], sl["_mn"] = (mids.index(doc["concept"]) if doc["concept"] in mids else 0), len(mids)
            built = build(sl, series, tag)
            sl["_split"] = bool(built.get("dyn")) and sl["layout"] != "cover"
            page = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><style>{css}</style></head>'
                    f'<body>{built["body"]}</body></html>')
            hp = htmldir / f"{i:02d}.html"
            hp.write_text(page, encoding="utf-8")
            pg.goto(hp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(200)
            if sl["layout"] == "cover" or built.get("dyn"):    # 封面與直切版面：補充文字接在標題下面
                pg.evaluate("() => {const t=document.getElementById('title'), s=document.getElementById('body'); "
                            "if(s) s.style.top=(t.getBoundingClientRect().bottom+36)+'px'}")
            m = pg.evaluate(MEASURE_JS)
            png = outdir / f"{i:02d}.png"
            pg.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": WD, "height": HT})
            img = Image.open(png).convert("RGB")
            tag_texts = [t["n"] for t in m["ts"] if t["n"] == tag[:16]] or []
            res = program_b(sl, m, img, tag, [tag] if tag_texts else [])
            bad = [r for r in res if not r[1]]
            failed += bool(bad)
            print(f"[{i:02d}] {sl['layout']:15s} {'PASS' if not bad else 'FAIL'}  ({len(res) - len(bad)}/{len(res)})")
            for n, ok, d in res:
                if not ok:
                    print(f"      FAIL {n}  [{d}]")
            report.append({"slide": i, "layout": sl["layout"], "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in res]})
            body = plain(sl.get("body", ""))
            if sl["layout"] == "series_map":
                alts[f"{i:02d}.png"] = plain(sl["title"]) + "。" + "、".join(m_["planned_title"] for m_ in series["members"])
            else:
                alts[f"{i:02d}.png"] = ((sl["question"] + "　" if sl.get("question") else "") + plain(sl.get("title", "")) + ("。" + body if body else "")
                                        + ("。圖上寫：" + "、".join(D.texts(sl)) if sl["layout"] == "diagram" else ""))
        b.close()
    (bld / "alt-text.json").write_text(json.dumps(alts, ensure_ascii=False, indent=2), encoding="utf-8")
    (bld / "checks-b.json").write_text(json.dumps({"template_hash": thash, "slides": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"template_hash={thash}  程式 B：{len(report) - failed}/{len(report)} 張通過")
    return 1 if failed else 0


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    sys.exit(render_all(Path(sys.argv[1]).resolve(), only, "--force" in sys.argv))
