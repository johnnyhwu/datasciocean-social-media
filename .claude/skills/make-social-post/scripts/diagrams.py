"""示意圖版型（layout: diagram）的幾何與繪製。由 render.py 呼叫：build(spec, y0, ctx) -> (svg 內容, 文字 html, 底部 y)。

為什麼有這份：2026-10-11 人的回饋——「每篇 post 的 chart 都是同一個模板、都是 bar chart；文字下面空出來的區塊是塗鴉牆，
流程圖、任何圖都可以，只要讓讀者更好理解、覺得有趣」。所以除了橫條圖，另有下列 kind（spec 的 `kind` 欄位）：
  flow      由上往下的流程：nodes（每個 text、選用 sub）、選用 outcomes（兩三個結果，good 金色／bad 外框）、選用 loop（底部虛線框的說明）
  compare   兩欄並列：columns = [{head, items:[{text, sub?, gone?, emph?}]}]（gone = 劃掉、emph = 左側金條）
  pairs     「換掉什麼 → 換成什麼」：heads = [左標, 右標]、pairs = [[左, 右], …]
  samples   一個點 vs 一批點：nodes = [{text, sub?}, {text, sub?}]
  paths     亂走 vs 小步走：nodes = [{text, sub?}, {text, sub?}]
  epochs    小步子與每輪結束的檢查旗：nodes = [{text}（小點是什麼）, {text}（金旗是什麼）]
  dotgrid   點陣：count、選用 cols（每列幾個點）、nodes = [{text}]（一個點代表什麼）
  dumbbell  前後對比（軸從 0 起）：points = [{name, value}, {name, value}]、ref = {name, value}、unit、axis_max
  range     區間條（軸從 0 起）：ranges = [{name, sub?, lo, hi, emph?}]（lo == hi 畫成標記線）、unit、axis_max
  funnel    漏斗：nodes（3 層，每層 text、選用 sub）
  batches   一個池子切成幾組（2026-10-12）：count（池子有幾個點）、group（每組幾個）、nodes = [{text}（池子是什麼）, {text}（每一組做什麼）]
  decay     從 start 慢慢降到 end 的曲線（軸從 0 起、高度與數值成正比）：start、end、unit、axis_max、nodes = [{text}（初期）, {text}（後期）]
  fan       幾組同時做事、再匯成一份：heads（2～4 個組別標籤）、nodes = [{text}（組別上方的說明）, {text, sub?}（匯整後的結果）]
  peaks     兩條曲線的最高點落在同一處（純示意）：nodes = [{text}（線一）, {text}（線二）, {text}（最高點的標籤）]
  equation  算式 A × B ＝ C：nodes = 算元 [{text（大數字）, sub（單位）, sub2?, emph?}]、選用 ops、選用 outcomes[0]（底下一條橫框）
  quad      2×2 四個格子：nodes = 4 個 [{text, sub?, emph?, bars?}]（bars＝格子上方的小投影片有幾條條列）
  locked    文件裡一塊受保護的區塊：heads = [被擋下的來源, 能更新的來源]、nodes = [{text}（文件名）, {text}（受保護區塊）]
  tokens    符號序列（2026-10-18）：steps = [{label, cells:[{text, sub?, tone}]}]，一列一步；tone = rtg／state／action／reward／mask；選用 more、outcomes[0]
  stops     由上往下三個停靠點（不按比例）：nodes = [{text, sub?, emph?}]、選用 heads = [上端標籤, 下端標籤]

規則：圖形全部用 class "bg"（不進程式 B 的文字與圖形重疊檢查），所以排版由這裡負責避開文字；框內的文字由程式 B 的「框內文字不超出框」檢查；
比例（dumbbell／range）由程式 B 檢查圖形位置與數值成正比。字級只用 {28, 34, 40, 56}。
"""
from __future__ import annotations

import math

CREAM, TEAL, DEEP, GOLD = "#F2E0C0", "#076876", "#01353F", "#DDA642"
MID, LIGHT, ABYSS = "#1F8A8D", "#69B4AA", "#032027"
X0, X1 = 80, 1000
BOTTOM = 1235          # 示意圖最低可到的 y（頁尾的 @datasciocean 在 1262）


class Ctx:
    """render.py 傳進來的小工具：est_lines(txt, per_line)、bind(txt)、esc(txt)。"""
    def __init__(self, est_lines, bind, esc):
        self.est_lines, self.bind, self.esc = est_lines, bind, esc


class Canvas:
    def __init__(self, ctx: Ctx):
        self.ctx, self.svg, self.html = ctx, [], []

    # ---- 圖形（class bg）
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=3, rx=16, dash=None, op=None):
        a = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        a += f' stroke-dasharray="{dash}"' if dash else ""
        a += f' fill-opacity="{op}"' if op is not None else ""
        self.svg.append(f'<rect class="bg" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{a}/>')

    def line(self, x1, y1, x2, y2, color=TEAL, sw=4, dash=None, op=None):
        a = f' stroke-dasharray="{dash}"' if dash else ""
        a += f' stroke-opacity="{op}"' if op is not None else ""
        self.svg.append(f'<line class="bg" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{a}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=3, op=None, dash=None, cls="bg", extra=""):
        a = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        a += f' stroke-dasharray="{dash}"' if dash else ""
        a += f' fill-opacity="{op}"' if op is not None else ""
        self.svg.append(f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{a}{extra}/>')

    def poly(self, pts, fill="none", stroke=None, sw=4, closed=False, op=None):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        a = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
        a += f' fill-opacity="{op}"' if op is not None else ""
        tag = "polygon" if closed else "polyline"
        self.svg.append(f'<{tag} class="bg" points="{d}" fill="{fill}"{a}/>')

    def arrow(self, x1, y1, x2, y2, color=TEAL, sw=4, head=14):
        self.line(x1, y1, x2, y2, color, sw)
        ang = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2), (x2 - head * math.cos(ang - .45), y2 - head * math.sin(ang - .45)),
             (x2 - head * math.cos(ang + .45), y2 - head * math.sin(ang + .45))]
        self.poly(p, fill=color, closed=True)

    # ---- 文字（class t；data-box 讓程式 B 檢查文字不超出框）
    def text(self, x, y, w, s, cls="dn", color=DEEP, align="left", box=None, extra=""):
        b = f' data-box="{box[0]:.1f},{box[1]:.1f},{box[2]:.1f},{box[3]:.1f}"' if box else ""
        t = self.ctx.bind(s).replace("\n", "<br>")
        self.html.append(f'<div class="t abs {cls}" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;color:{color};text-align:{align}{extra}"{b}>{self.ctx.esc(t) if "<br>" not in t else "<br>".join(self.ctx.esc(p) for p in t.split("<br>"))}</div>')

    def lines(self, s, w, size):
        return self.ctx.est_lines(self.ctx.bind(s), w / size - 0.7)

    def textbox(self, x, y, w, title, sub=None, fill=DEEP, tcolor=CREAM, scolor=LIGHT, stroke=None, dash=None, align="left", pad=22, h=None, size=34):
        """畫一個框，框裡放標題與副標；回傳框高。h 給定時用固定高（文字垂直置中）。"""
        iw = w - 2 * pad
        l1 = self.lines(title, iw, size)
        l2 = self.lines(sub, iw, 28) if sub else 0
        th = l1 * (size * 1.3) + (l2 * 28 * 1.4 + 6 if l2 else 0)
        bh = h if h else th + 2 * pad
        self.rect(x, y, w, bh, fill=fill, stroke=stroke, dash=dash)
        ty = y + (bh - th) / 2
        box = (x, y, w, bh)
        cls = "dn" if size == 34 else "dv"
        self.text(x + pad, ty, iw, title, cls, tcolor, align, box)
        if sub:
            self.text(x + pad, ty + l1 * (size * 1.3) + 6, iw, sub, "ds", scolor, align, box)
        return bh


def _fit(total: float, avail: float, what: str) -> None:
    if total > avail + 0.5:
        raise ValueError(f"示意圖（{what}）放不下：需要 {total:.0f}px，只剩 {avail:.0f}px；請縮短補充或圖上的字")


# ------------------------------------------------------------------ flow
def flow(c: Canvas, spec: dict, y0: float) -> float:
    nodes, outs, loop = spec["nodes"], spec.get("outcomes", []), spec.get("loop")
    w = X1 - X0
    gap = 30
    hs = []
    for n in nodes:
        t = c.lines(n["text"], w - 44, 34) * 44.2 + (c.lines(n["sub"], w - 44, 28) * 39.2 + 6 if n.get("sub") else 0) + 44
        hs.append(t)
    ow = (w - 24 * (len(outs) - 1)) / len(outs) if outs else 0
    oh = max([c.lines(o["text"], ow - 44, 34) * 44.2 + (c.lines(o["sub"], ow - 44, 28) * 39.2 + 6 if o.get("sub") else 0) + 44 for o in outs], default=0)
    lh = (c.lines(loop, w - 44, 28) * 39.2 + 36) if loop else 0
    total = sum(hs) + gap * (len(nodes) - 1) + (gap + oh if outs else 0) + (gap + lh if loop else 0)
    _fit(total, BOTTOM - y0, "flow")
    extra = BOTTOM - y0 - total                         # 多出來的高度：先加厚各框，再拉大間距
    nbox = len(nodes) + (1 if outs else 0)
    add = min(extra * 0.55 / nbox, 46)
    hs = [h + add for h in hs]; oh += add if outs else 0
    gap += min((extra - add * nbox) / max(len(nodes) - 1 + (1 if outs else 0) + (1 if loop else 0), 1), 34)
    y = y0
    for i, n in enumerate(nodes):
        c.textbox(X0, y, w, n["text"], n.get("sub"), h=hs[i])
        y += hs[i]
        if i < len(nodes) - 1:
            c.arrow(X0 + w / 2, y + 3, X0 + w / 2, y + gap - 3)
            y += gap
    if outs:
        y += gap
        for k, o in enumerate(outs):
            x = X0 + k * (ow + 24)
            good = o.get("tone") == "good"
            c.textbox(x, y, ow, o["text"], o.get("sub"), fill=GOLD if good else CREAM, tcolor=DEEP,
                      scolor=DEEP, stroke=None if good else DEEP, h=oh, align="center")
            c.arrow(X0 + w / 2, y - gap + 3, x + ow / 2, y - 3)
        y += oh
    if loop:
        y += gap
        c.rect(X0, y, w, lh, fill="none", stroke=TEAL, sw=3, dash="10 8")
        c.text(X0 + 22, y + 18, w - 44, loop, "ds", TEAL, "left", (X0, y, w, lh))
        y += lh
    return y


# ------------------------------------------------------------------ compare
def compare(c: Canvas, spec: dict, y0: float) -> float:
    cols = spec["columns"]
    cw, gap = 440, 40
    xs = [X0, X0 + cw + gap]
    hh = 80
    n = max(len(col["items"]) for col in cols)
    rows = []
    for i in range(n):
        h = 0
        for col in cols:
            if i < len(col["items"]):
                it = col["items"][i]
                h = max(h, c.lines(it["text"], cw - 56, 34) * 46 + (c.lines(it["sub"], cw - 56, 28) * 39.2 + 6 if it.get("sub") else 0) + 40)
        rows.append(h)
    total = hh + 16 + sum(rows) + 16 * (n - 1)
    _fit(total, BOTTOM - y0, "compare")
    add = min((BOTTOM - y0 - total) / n, 70 if n >= 3 else 190)
    rows = [r + add for r in rows]
    total += add * n
    for k, col in enumerate(cols):
        c.rect(xs[k], y0, cw, hh, fill=DEEP if k == 0 else TEAL)
        c.text(xs[k] + 22, y0 + (hh - 44) / 2, cw - 44, col["head"], "dn", CREAM, "center", (xs[k], y0, cw, hh))
        y = y0 + hh + 16
        for i, it in enumerate(col["items"]):
            h = rows[i]
            c.rect(xs[k], y, cw, h, fill="none", stroke=DEEP, sw=3, dash="8 8" if (it.get("gone") or it.get("muted")) else None, rx=14)
            if it.get("emph"):
                c.rect(xs[k], y, 12, h, fill=GOLD, rx=6)
            col_t = TEAL if (it.get("gone") or it.get("muted")) else DEEP
            l1 = c.lines(it["text"], cw - 56, 34)
            th = l1 * 46 + (c.lines(it["sub"], cw - 56, 28) * 39.2 + 6 if it.get("sub") else 0)
            cls = "dt gone" if it.get("gone") else "dt"
            c.text(xs[k] + 30, y + (h - th) / 2, cw - 56, it["text"], cls, col_t, "left", (xs[k], y, cw, h))
            if it.get("sub"):
                c.text(xs[k] + 30, y + (h - th) / 2 + l1 * 46 + 6, cw - 56, it["sub"], "ds", col_t, "left", (xs[k], y, cw, h))
            y += h + 16
    return y0 + total


# ------------------------------------------------------------------ pairs
def pairs(c: Canvas, spec: dict, y0: float) -> float:
    heads, prs = spec["heads"], spec["pairs"]
    lw, rw, mid = 380, 460, 80
    rx = X0 + lw + mid
    rows = [max(c.lines(l, lw - 44, 34), c.lines(r, rw - 44, 34)) * 44.2 + 44 for l, r in prs]
    total = 44 + 14 + sum(rows) + 18 * (len(prs) - 1)
    _fit(total, BOTTOM - y0, "pairs")
    add = min((BOTTOM - y0 - total) / len(prs), 60)
    rows = [r + add for r in rows]
    total += add * len(prs)
    c.text(X0, y0, lw, heads[0], "dl", TEAL, "left")
    c.text(rx, y0, rw, heads[1], "dl", TEAL, "left")
    y = y0 + 58
    for (l, r), h in zip(prs, rows):
        c.rect(X0, y, lw, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=14)
        c.text(X0 + 22, y + (h - c.lines(l, lw - 44, 34) * 44.2) / 2, lw - 44, l, "dt", TEAL, "left", (X0, y, lw, h))
        c.rect(rx, y, rw, h, fill=DEEP, rx=14)
        c.text(rx + 22, y + (h - c.lines(r, rw - 44, 34) * 44.2) / 2, rw - 44, r, "dn", CREAM, "left", (rx, y, rw, h))
        c.arrow(X0 + lw + 10, y + h / 2, rx - 10, y + h / 2, color=GOLD, sw=5)
        y += h + 18
    return y0 + total


# ------------------------------------------------------------------ samples / paths（左右兩個小面板）
def _panel_labels(c: Canvas, nodes, y_label, pw=440, gap=40):
    xs = [X0, X0 + pw + gap]
    for k, n in enumerate(nodes):
        l1 = c.lines(n["text"], pw - 20, 34)
        c.text(xs[k] + 10, y_label, pw - 20, n["text"], "dn", DEEP, "center")
        if n.get("sub"):
            c.text(xs[k] + 10, y_label + l1 * 44.2 + 6, pw - 20, n["sub"], "ds", DEEP, "center")
    return max(c.lines(n["text"], pw - 20, 34) * 44.2 + (c.lines(n["sub"], pw - 20, 28) * 39.2 + 6 if n.get("sub") else 0) for n in nodes)


def samples(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    pw, gap, ph = 440, 40, 340
    ph = min(560, max(ph, BOTTOM - y0 - 140))
    lab = max(c.lines(n["text"], pw - 20, 34) * 44.2 + (c.lines(n["sub"], pw - 20, 28) * 39.2 + 6 if n.get("sub") else 0) for n in nodes)
    total = ph + 20 + lab
    _fit(total, BOTTOM - y0, "samples")
    xs = [X0, X0 + pw + gap]
    for x in xs:
        c.rect(x, y0, pw, ph, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
        c.text(x + 18, y0 + 10, 120, "示意", "ds", TEAL)
    # 左：一個點
    cx, cy = xs[0] + pw / 2, y0 + ph / 2 + 24
    c.circle(cx, cy, 30, fill=TEAL)
    c.text(xs[0], y0 + 34, pw, "？", "dv", TEAL, "center")
    # 右：一批點與方向
    pts = [(0.10, 0.80), (0.18, 0.62), (0.26, 0.74), (0.34, 0.56), (0.42, 0.66), (0.50, 0.46), (0.58, 0.58),
           (0.66, 0.36), (0.74, 0.50), (0.82, 0.28), (0.90, 0.40), (0.30, 0.44), (0.62, 0.72), (0.78, 0.66)]
    gx, gy, gw, gh = xs[1] + 30, y0 + 30, pw - 60, ph - 60
    for fx, fy in pts:
        c.circle(gx + fx * gw, gy + fy * gh, 13, fill=MID)
    c.arrow(gx + 0.04 * gw, gy + 0.90 * gh, gx + 0.98 * gw, gy + 0.18 * gh, color=DEEP, sw=5, head=18)
    _panel_labels(c, nodes, y0 + ph + 20)
    return y0 + total


def paths(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    pw, gap, ph = 440, 40, 360
    ph = min(580, max(ph, BOTTOM - y0 - 140))
    lab = max(c.lines(n["text"], pw - 20, 34) * 44.2 + (c.lines(n["sub"], pw - 20, 28) * 39.2 + 6 if n.get("sub") else 0) for n in nodes)
    total = ph + 20 + lab
    _fit(total, BOTTOM - y0, "paths")
    xs = [X0, X0 + pw + gap]
    for x in xs:
        c.rect(x, y0, pw, ph, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
        c.text(x + 18, y0 + 10, 120, "示意", "ds", TEAL)
    S, T = (60.0, ph - 60.0), (pw - 80.0, 90.0)
    nx, ny = (T[1] - S[1]), -(T[0] - S[0])
    nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl

    def path(kind):
        out = []
        n = 7
        for i in range(n):
            t = i / (n - 1)
            sgn = 1 if i % 2 else -1
            if kind == "wild":
                off = sgn * (14 + 26 * i) * (1 if i else 0)
            else:
                off = sgn * 70 * (1 - t) ** 1.6 * (1 if i else 0)
            out.append((S[0] + (T[0] - S[0]) * t + nx * off, S[1] + (T[1] - S[1]) * t + ny * off))
        return out

    for k, kind in enumerate(("wild", "steady")):
        ox, oy = xs[k], y0
        P = path(kind)
        for ring_r, op in ((40, .35), (24, .55)):
            c.circle(ox + T[0], oy + T[1], ring_r, stroke=DEEP, sw=3, op=0, dash=None)
        pts = [(ox + x, oy + y) for x, y in P]
        c.poly(pts, stroke=TEAL if kind == "steady" else DEEP, sw=4)
        for x, y in pts[:-1]:
            c.circle(x, y, 8, fill=TEAL if kind == "steady" else DEEP)
        ex, ey = pts[-1]
        if kind == "steady":
            c.circle(ex, ey, 44, fill=GOLD, op=.30)
            c.circle(ex, ey, 15, fill=GOLD)
        else:
            c.line(ex - 14, ey - 14, ex + 14, ey + 14, DEEP, 5)
            c.line(ex - 14, ey + 14, ex + 14, ey - 14, DEEP, 5)
    _panel_labels(c, nodes, y0 + ph + 20)
    return y0 + total


# ------------------------------------------------------------------ epochs
def epochs(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    leg = max(c.lines(n["text"], 420, 28) for n in nodes) * 39.2
    h = max(300, min(600, BOTTOM - y0 - 24 - leg))
    total = h + 24 + leg
    _fit(total, BOTTOM - y0, "epochs")
    c.rect(X0, y0, X1 - X0, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    c.text(X0 + 18, y0 + 10, 160, "示意", "ds", TEAL)
    bx0, bx1 = X0 + 90, X1 - 40
    base = y0 + h - 70
    top = y0 + 100
    c.arrow(bx0 - 24, base, bx0 - 24, top - 10, DEEP, 3, 12)          # 縱軸：表現
    c.text(X0 + 150, y0 + 10, 140, "表現", "ds", DEEP)
    c.line(bx0 - 24, base, bx1, base, DEEP, 3)
    n = 45
    pts = []
    for i in range(n):
        t = i / (n - 1)
        up = 1 - math.exp(-3.0 * t)                                     # 整體慢慢變好
        dip = 0.20 * math.exp(-((t - 0.285) / 0.035) ** 2) + 0.20 * math.exp(-((t - 0.615) / 0.035) ** 2)   # 兩次小退步（在慢檢查之前）
        wig = 0.02 * math.sin(i * 2.1)
        y = base - 40 - (base - top - 60) * max(0.05, min(0.97, up * 0.9 - dip + wig))
        pts.append((bx0 + (bx1 - bx0) * t, y))
    c.poly(pts, stroke=TEAL, sw=3)
    for x, y in pts:
        c.circle(x, y, 6, fill=TEAL)
    for k in (1, 2):
        x = bx0 + (bx1 - bx0) * k / 3
        c.line(x, top - 20, x, base, GOLD, 5)
        c.poly([(x, top - 36), (x + 14, top - 20), (x, top - 4), (x - 14, top - 20)], fill=GOLD, closed=True)
    c.text(X1 - 340, base + 14, 300, "訓練時間", "ds", DEEP, "right")
    lx = [X0, X0 + 480]
    for k, nd in enumerate(nodes):
        c.text(lx[k] + 6, y0 + h + 24, 420, nd["text"], "ds", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ dotgrid
def dotgrid(c: Canvas, spec: dict, y0: float) -> float:
    n = spec["count"]
    cols = int(spec.get("cols") or (13 if n > 40 else 10))      # cols（選用）：每列幾個點，例如 20 篇 × 4 種配置排成 20 欄 4 列
    rows = math.ceil(n / cols)
    legs = spec["nodes"]
    leg_h = [c.lines(l["text"], X1 - X0 - 70, 34) * 44.2 for l in legs]
    avail = BOTTOM - y0 - sum(leg_h) - 40 * len(legs) - 10
    pitch = min(72, avail / rows, (X1 - X0) / cols)
    r = pitch * 0.36
    gw = (cols - 1) * pitch
    gx = X0 + (X1 - X0 - gw) / 2
    gh = (rows - 1) * pitch + 2 * r
    total = gh + 34 + sum(leg_h) + 24 * (len(legs) - 1) + 10
    _fit(total, BOTTOM - y0, "dotgrid")
    for i in range(n):
        c.circle(gx + (i % cols) * pitch, y0 + r + (i // cols) * pitch, r, fill=MID)
    y = y0 + gh + 34
    for k, l in enumerate(legs):
        if k == 0:
            c.circle(X0 + 22, y + 22, 18, fill=MID)
        else:
            c.circle(X0 + 22, y + 22, 18, fill="none", stroke=DEEP, sw=4)
        c.text(X0 + 70, y, X1 - X0 - 70, l["text"], "dn", DEEP, "left")
        y += leg_h[k] + 24
    return y0 + total


# ------------------------------------------------------------------ dumbbell / range（比例由程式 B 檢查）
def _axis(c: Canvas, x0, x1, y, amax, unit, ticks):
    c.line(x0, y, x1, y, DEEP, 3)
    s = (x1 - x0) / amax
    for v in ticks:
        x = x0 + v * s
        c.line(x, y, x, y + 14, DEEP, 3)
        c.text(x - 50, y + 20, 100, f"{v:g}", "ds", DEEP, "center")
    return s


def _ticks(amax: float) -> list[float]:
    raw = amax / 4
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=raw)
    n = int(amax / step + 1e-9)
    return [step * k for k in range(n + 1)]


def dumbbell(c: Canvas, spec: dict, y0: float) -> float:
    a, b = spec["points"]
    ref = spec["ref"]
    amax = spec.get("axis_max", 100)
    unit = spec.get("unit", "")
    x0, x1 = 120, 980
    s = (x1 - x0) / amax
    ay = y0 + min(520, max(380, BOTTOM - y0 - 190))
    _fit(ay + 150 - y0, BOTTOM - y0 + 40, "dumbbell")
    ticks = _ticks(amax)
    _axis(c, x0, x1, ay, amax, unit, ticks)
    # 參考線（原地練的版本）：金色虛線，標籤放在軸下方
    rx = x0 + ref["value"] * s
    c.line(rx, ay - 26, rx, ay + 66, GOLD, 5, dash="10 8")
    c.text(rx - 230, ay + 84, 460, f"{ref['name']}：{ref['value']:g}{unit}", "dn", DEEP, "center")
    # 前 → 後
    py = ay - 56
    ax_, bx_ = x0 + a["value"] * s, x0 + b["value"] * s
    c.arrow(ax_ + 24, py, bx_ - 32, py, color=TEAL, sw=7, head=24)
    c.circle(ax_, py, 22, fill=CREAM, stroke=TEAL, sw=7, cls="bg dpt", extra=f' data-v="{a["value"]}" data-x0="{x0}" data-s="{s}"')
    c.circle(bx_, py, 24, fill=DEEP, cls="bg dpt", extra=f' data-v="{b["value"]}" data-x0="{x0}" data-s="{s}"')
    c.text(ax_ - 150, py - 130, 300, f"{a['value']:g}{unit}", "dv", TEAL, "center")
    c.text(bx_ - 150, py - 130, 300, f"{b['value']:g}{unit}", "dv", DEEP, "center")
    c.text(ax_ - 150, py - 188, 300, a["name"], "ds", DEEP, "center")
    c.text(bx_ - 150, py - 188, 300, b["name"], "ds", DEEP, "center")
    return ay + 84 + 60


def range_chart(c: Canvas, spec: dict, y0: float) -> float:
    rows = spec["ranges"]
    amax = spec.get("axis_max", 100)
    unit = spec.get("unit", "")
    x0, x1 = 120, 960
    s = (x1 - x0) / amax
    rh = min(230, max(170, (BOTTOM - y0 - 100) / len(rows)))
    total = len(rows) * rh + 90
    _fit(total, BOTTOM - y0, "range")
    y = y0
    for r in rows:
        nl = c.lines(r["name"], X1 - X0, 34)
        c.text(X0, y, X1 - X0, r["name"], "dn", DEEP, "left")
        sy = y + nl * 44.2 + (c.lines(r["sub"], X1 - X0, 28) * 39.2 + 8 if r.get("sub") else 0) + 18
        if r.get("sub"):
            c.text(X0, y + nl * 44.2 + 8, X1 - X0, r["sub"], "ds", DEEP, "left")
        c.rect(x0, sy, x1 - x0, 36, fill=LIGHT, op=.35, rx=8)
        lo, hi = r["lo"], r["hi"]
        extra = f' data-lo="{lo}" data-hi="{hi}" data-s="{s}" data-x0="{x0}"'
        if lo == hi:
            c.circle(x0 + lo * s, sy + 18, 0.01, cls="bg rbar", extra=extra)
            c.rect(x0 + lo * s - 5, sy - 10, 10, 56, fill=DEEP, rx=4)
        else:
            c.svg.append(f'<rect class="bg rbar" x="{x0 + lo * s:.1f}" y="{sy:.1f}" width="{(hi - lo) * s:.1f}" height="36" rx="8" fill="{GOLD if r.get("emph") else MID}"{extra}/>')
        lab = f"{lo:g}{unit}" if lo == hi else f"{lo:g}～{hi:g}{unit}"
        lx = x0 + hi * s + 16
        if lx + 200 > X1 + 20:
            c.text(x0 + lo * s - 216, sy - 4, 200, lab, "dv2", DEEP, "right")
        else:
            c.text(lx, sy - 4, 220, lab, "dv2", DEEP, "left")
        y += rh
    _axis(c, x0, x1, y + 10, amax, unit, _ticks(amax))
    return y + 10 + 70


# ------------------------------------------------------------------ funnel
def funnel(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    widths = [920, 740, 560, 400][:len(nodes) + 1]
    gap = 14
    sh = min(210, max(150, (BOTTOM - y0 - gap * (len(nodes) - 1)) / len(nodes)))
    total = len(nodes) * sh + gap * (len(nodes) - 1)
    _fit(total, BOTTOM - y0, "funnel")
    fills = [DEEP, TEAL, GOLD] if len(nodes) == 3 else [DEEP, GOLD]
    y = y0
    for i, n in enumerate(nodes):
        wt, wb = widths[i], widths[i + 1]
        cx = X0 + (X1 - X0) / 2
        pts = [(cx - wt / 2, y), (cx + wt / 2, y), (cx + wb / 2, y + sh), (cx - wb / 2, y + sh)]
        fill = fills[min(i, len(fills) - 1)] if len(nodes) == 3 else (DEEP if i < len(nodes) - 1 else GOLD)
        c.poly(pts, fill=fill, closed=True)
        tcol = DEEP if fill == GOLD else CREAM
        iw = wb - 40
        l1 = c.lines(n["text"], iw, 34)
        th = l1 * 44.2 + (c.lines(n["sub"], iw, 28) * 39.2 + 4 if n.get("sub") else 0)
        box = (cx - wb / 2, y, wb, sh)
        c.text(cx - iw / 2, y + (sh - th) / 2, iw, n["text"], "dn", tcol, "center", box)
        if n.get("sub"):
            c.text(cx - iw / 2, y + (sh - th) / 2 + l1 * 44.2 + 4, iw, n["sub"], "ds", tcol, "center", box)
        y += sh + gap
    return y0 + total


# ------------------------------------------------------------------ batches（一個池子切成幾組）
def batches(c: Canvas, spec: dict, y0: float) -> float:
    """count 個點的池子，切成每組 group 個的小組（最後一組可能不滿）。nodes = [{text}（池子是什麼）, {text}（每一組做什麼）]。"""
    n, g = spec["count"], spec["group"]
    k = math.ceil(n / g)
    w = X1 - X0
    top_h = c.lines(spec["nodes"][0]["text"], w, 34) * 44.2
    bot_h = c.lines(spec["nodes"][1]["text"], w, 34) * 44.2
    pool_h, arrow_h, grp_h = 150, 80, 190
    total = top_h + 14 + pool_h + arrow_h + grp_h + 22 + bot_h
    _fit(total, BOTTOM - y0, "batches")
    extra = BOTTOM - y0 - total
    pool_h += min(extra * .3, 60); grp_h += min(extra * .4, 80); arrow_h += min(extra * .3, 40)
    c.text(X0, y0, w, spec["nodes"][0]["text"], "dn", DEEP, "left")
    py = y0 + top_h + 14
    c.rect(X0, py, w, pool_h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    cols = 10
    rows = math.ceil(n / cols)
    pitch = min(48, (pool_h - 40) / max(rows, 1))
    gx = X0 + (w - (cols - 1) * pitch) / 2
    for i in range(n):
        c.circle(gx + (i % cols) * pitch, py + pool_h / 2 - (rows - 1) * pitch / 2 + (i // cols) * pitch, pitch * .3, fill=MID)
    gw = (w - 26 * (k - 1)) / k
    gy = py + pool_h + arrow_h
    left = n
    for j in range(k):
        x = X0 + j * (gw + 26)
        m = min(g, left); left -= m
        c.arrow(X0 + w / 2 + (j - (k - 1) / 2) * 60, py + pool_h + 6, x + gw / 2, gy - 6, color=TEAL, sw=4)
        c.rect(x, gy, gw, grp_h, fill=DEEP if m == g else CREAM, stroke=None if m == g else DEEP, sw=3, dash=None if m == g else "8 8", rx=16)
        pc, pr = 4, 2
        p2 = min(46, (gw - 40) / pc)
        ox = x + (gw - (pc - 1) * p2) / 2
        for i in range(m):
            c.circle(ox + (i % pc) * p2, gy + grp_h / 2 - p2 / 2 + (i // pc) * p2 - 4, p2 * .3, fill=GOLD if m == g else MID)
    c.text(X0, gy + grp_h + 22, w, spec["nodes"][1]["text"], "dn", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ decay（預算隨訓練慢慢變小）
def decay(c: Canvas, spec: dict, y0: float) -> float:
    """start→end 的平滑下降曲線（高度與數值成正比，軸從 0 起）。nodes = [{text}（初期）, {text}（後期）]，unit、axis_max。"""
    a, b, unit, amax = spec["start"], spec["end"], spec.get("unit", ""), spec.get("axis_max", 5)
    leg = max(c.lines(nd["text"], 420, 34) for nd in spec["nodes"]) * 44.2
    h = max(360, min(640, BOTTOM - y0 - 30 - leg))
    total = h + 30 + leg
    _fit(total, BOTTOM - y0, "decay")
    c.rect(X0, y0, X1 - X0, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    c.text(X0 + 18, y0 + 10, 160, "示意", "ds", TEAL)
    bx0, bx1 = X0 + 110, X1 - 50
    base = y0 + h - 56
    sc = (h - 56 - 90) / amax                              # 每 1 個單位的高度（零點在 base）
    c.line(bx0 - 24, base, bx1, base, DEEP, 3)
    c.line(bx0 - 24, base, bx0 - 24, base - amax * sc, DEEP, 3)
    c.text(bx0 - 50, base + 8, 50, "0", "ds", DEEP, "center")
    n = 40
    pts = []
    for i in range(n):
        t = i / (n - 1)
        v = b + (a - b) * (1 + math.cos(math.pi * t)) / 2
        pts.append((bx0 + (bx1 - bx0) * t, base - v * sc))
    c.poly([(pts[0][0], base)] + pts + [(pts[-1][0], base)], fill=LIGHT, closed=True, op=.35)
    c.poly(pts, stroke=TEAL, sw=5)
    for v, x, al in ((a, pts[0][0], "left"), (b, pts[-1][0], "right")):
        y = base - v * sc
        c.line(bx0 - 24, y, bx1, y, GOLD, 3, dash="10 8", op=.8)
    c.circle(pts[0][0], pts[0][1], 14, fill=GOLD)
    c.circle(pts[-1][0], pts[-1][1], 14, fill=GOLD)
    c.text(pts[0][0] - 8, pts[0][1] - 78, 150, f"{a:g}{unit}", "dv", DEEP, "left")
    c.text(pts[-1][0] - 142, pts[-1][1] - 104, 150, f"{b:g}{unit}", "dv", DEEP, "right")
    c.text(X1 - 340, base + 8, 290, "訓練時間 →", "ds", DEEP, "right")
    for k, nd in enumerate(spec["nodes"]):
        c.text(X0 + k * 480 + 6, y0 + h + 30, 440, nd["text"], "dn", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ stops（一條軸上的三個位置，中間那個是被選的）
def stops(c: Canvas, spec: dict, y0: float) -> float:
    """由上往下三個停靠點：nodes = [{text, sub?, emph?}]；heads = [上端標籤, 下端標籤]（選用）。不按比例。"""
    nodes, heads = spec["nodes"], spec.get("heads", [])
    cw = X1 - X0 - 90
    head_h = 40
    hs = [c.lines(n["text"], cw - 44, 34) * 44.2 + (c.lines(n["sub"], cw - 44, 28) * 39.2 + 6 if n.get("sub") else 0) + 44 for n in nodes]
    gap = 26
    total = sum(hs) + gap * (len(nodes) - 1) + ((head_h + 8) * len(heads))
    _fit(total, BOTTOM - y0, "stops")
    extra = BOTTOM - y0 - total
    add = min(extra / len(nodes), 70)
    hs = [h + add for h in hs]
    y = y0
    cx = X0 + 22
    if heads:
        c.text(X0 + 60, y - 4, cw, heads[0], "ds", TEAL, "left"); y += head_h + 8
    top = y
    ys = []
    for h in hs:
        ys.append((y, h)); y += h + gap
    c.line(cx, top + hs[0] / 2, cx, ys[-1][0] + hs[-1] / 2, TEAL, 5)
    for (yy, h), n in zip(ys, nodes):
        emph = n.get("emph")
        c.circle(cx, yy + h / 2, 22 if emph else 14, fill=GOLD if emph else CREAM, stroke=None if emph else TEAL, sw=5)
        c.textbox(X0 + 70, yy, cw, n["text"], n.get("sub"), fill=GOLD if emph else CREAM, tcolor=DEEP,
                  scolor=DEEP, stroke=None if emph else DEEP, dash=None if emph else "8 8", h=h)
    if heads:
        c.text(X0 + 60, y - gap + 12, cw, heads[1], "ds", TEAL, "left"); y += head_h - gap + 12
    return min(y, y0 + total)


# ------------------------------------------------------------------ fan（幾組同時做事，再匯成一份）
def fan(c: Canvas, spec: dict, y0: float) -> float:
    """heads = 2～4 個組別標籤（同時進行）；nodes = [{text}（組別上方的說明）, {text, sub?}（匯整後的結果）]。"""
    heads, (top, res) = spec["heads"], spec["nodes"]
    k = len(heads)
    w = X1 - X0
    th = c.lines(top["text"], w, 34) * 44.2
    rh = c.lines(res["text"], w - 44, 34) * 44.2 + (c.lines(res["sub"], w - 44, 28) * 39.2 + 6 if res.get("sub") else 0) + 44
    gh, ah = 150, 90
    total = th + 16 + gh + ah + rh
    _fit(total, BOTTOM - y0, "fan")
    extra = BOTTOM - y0 - total
    gh += min(extra * .35, 70); ah += min(extra * .35, 70); rh += min(extra * .3, 50)
    c.text(X0, y0, w, top["text"], "dn", DEEP, "left")
    gy = y0 + th + 16
    gw = (w - 24 * (k - 1)) / k
    ry = gy + gh + ah
    for j, h in enumerate(heads):
        x = X0 + j * (gw + 24)
        c.textbox(x, gy, gw, h, fill=DEEP, tcolor=CREAM, align="center", h=gh)
        c.arrow(x + gw / 2, gy + gh + 4, X0 + w / 2 + (j - (k - 1) / 2) * 90, ry - 6, color=TEAL, sw=4)
    c.textbox(X0, ry, w, res["text"], res.get("sub"), fill=GOLD, tcolor=DEEP, scolor=DEEP, align="center", h=rh)
    return y0 + total


# ------------------------------------------------------------------ peaks（兩條曲線的最高點落在同一處；純示意）
def peaks(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = [{text}（第一條線）, {text}（第二條線）, {text}（最高點的標籤）]。兩條曲線形狀不同、最高點在同一個位置（示意，不是實驗數據）。"""
    n1, n2, nl = spec["nodes"]
    leg = 2 * 56 + 20
    h = max(380, min(640, BOTTOM - y0 - 30 - leg))
    total = h + 30 + leg
    _fit(total, BOTTOM - y0, "peaks")
    c.rect(X0, y0, X1 - X0, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    c.text(X0 + 18, y0 + 10, 160, "示意", "ds", TEAL)
    bx0, bx1 = X0 + 60, X1 - 50
    base = y0 + h - 60
    top = y0 + 130
    c.line(bx0 - 20, base, bx1, base, DEEP, 3)
    c.text(X1 - 420, base + 8, 380, "訓練過程中的各個版本 →", "ds", DEEP, "right")
    n = 30
    pk = 19
    def curve(amp, wob, ph):
        out = []
        for i in range(n):
            t = i / (n - 1)
            v = 0.25 + 0.55 * (math.exp(-((i - pk) / 7.5) ** 2) if i >= pk else math.exp(-((i - pk) / 11.0) ** 2)) + wob * math.sin(i * 1.7 + ph)
            out.append(v)
        m = max(out)
        out = [v if i == pk else min(v, m * 0.0 + v) for i, v in enumerate(out)]
        out[pk] = max(out) + 0.02                         # 最高點一定在 pk
        return [(bx0 + (bx1 - bx0) * i / (n - 1), base - 30 - (base - top - 40) * min(v, 1.0)) for i, v in enumerate(out)]
    a, b = curve(1, 0.035, 0.4), curve(1, 0.05, 2.0)
    px = a[pk][0]
    c.line(px, top - 30, px, base, GOLD, 5, dash="10 8")
    c.circle(px, a[pk][1], 14, fill=GOLD)
    c.circle(px, b[pk][1], 14, fill=GOLD)
    c.text(px - 200, top - 86, 400, nl["text"], "dn", DEEP, "center")
    c.poly(a, stroke=MID, sw=5)
    c.poly(b, stroke=DEEP, sw=5)
    ly = y0 + h + 30
    for k, (nd, col) in enumerate(((n1, MID), (n2, DEEP))):
        c.line(X0, ly + 22 + k * 56, X0 + 60, ly + 22 + k * 56, col, 6)
        c.text(X0 + 80, ly + k * 56, X1 - X0 - 80, nd["text"], "dn", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ quad（2×2 四個格子，可標一格為重點）
def quad(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 4 個格子 [{text, sub?, emph?, bars?}]，依序是左上、右上、左下、右下。
    bars（選用，2026-10-14）：格子上方畫一張小投影片，條列數 = bars（長版多、短版少），讓格子不只是字。"""
    nodes = spec["nodes"]
    gap = 24
    cw = (X1 - X0 - gap) / 2
    ICON_H = 190                                           # 小投影片（約 150）加上下留白
    rows = []
    for r in range(2):
        pair = nodes[r * 2:r * 2 + 2]
        rows.append(max(c.lines(nd["text"], cw - 44, 34) * 44.2 + (c.lines(nd["sub"], cw - 44, 28) * 39.2 + 6 if nd.get("sub") else 0) + 60
                        + (ICON_H if nd.get("bars") else 0) for nd in pair))
    total = sum(rows) + gap
    _fit(total, BOTTOM - y0, "quad")
    extra = BOTTOM - y0 - total
    rows = [r + min(extra / 2, 150) for r in rows]
    y = y0
    for r in range(2):
        for k in range(2):
            nd = nodes[r * 2 + k]
            emph = nd.get("emph")
            x = X0 + k * (cw + gap)
            if not nd.get("bars"):
                c.textbox(x, y, cw, nd["text"], nd.get("sub"), fill=GOLD if emph else CREAM, tcolor=DEEP,
                          scolor=DEEP, stroke=None if emph else DEEP, dash=None if emph else "8 8", align="center", h=rows[r])
                continue
            h = rows[r]
            c.rect(x, y, cw, h, fill=GOLD if emph else CREAM, stroke=None if emph else DEEP, dash=None if emph else "8 8")
            k = 1.45                                            # 小投影片的放大倍數
            iw, ih = 168 * k, 104 * k
            l1 = c.lines(nd["text"], cw - 44, 34)
            th = l1 * 44.2 + (c.lines(nd["sub"], cw - 44, 28) * 39.2 + 6 if nd.get("sub") else 0)
            grp = ih + 18 + th                                  # 小投影片加文字，整組在格子裡垂直置中
            ix, iy = x + (cw - iw) / 2, y + max(14, (h - grp) / 2)
            c.rect(ix, iy, iw, ih, fill=DEEP, rx=12 * k)
            c.rect(ix + 16 * k, iy + 14 * k, iw * .42, 8 * k, fill=CREAM, rx=4 * k)
            n = int(nd["bars"])
            gp = (ih - 38 * k) / max(n, 1)
            for i in range(n):
                cy = iy + 28 * k + gp * i + gp / 2
                c.circle(ix + 20 * k, cy, 4 * k, fill=CREAM)
                c.rect(ix + 34 * k, cy - 3.5 * k, iw - 50 * k - (i % 3) * 14 * k, 7 * k, fill=CREAM, rx=3.5 * k, op=.8)
            ty = iy + ih + 18
            box = (x, y, cw, h)
            c.text(x + 22, ty, cw - 44, nd["text"], "dn", DEEP, "center", box)
            if nd.get("sub"):
                c.text(x + 22, ty + l1 * 44.2 + 6, cw - 44, nd["sub"], "ds", DEEP, "center", box)
        y += rows[r] + gap
    return y - gap


# ------------------------------------------------------------------ locked（文件裡一塊受保護的區塊）
def locked(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [被擋下的來源, 能更新的來源]；nodes = [{text}（文件名）, {text}（受保護區塊）]。"""
    (hl, hr), (doc, blk) = spec["heads"], spec["nodes"]
    w = X1 - X0
    sw = (w - 40) / 2
    sh = max(c.lines(hl, sw - 36, 34), c.lines(hr, sw - 36, 34)) * 44.2 + 36
    bh = c.lines(blk["text"], w - 150, 34) * 44.2 + 50
    gap = 70
    dh = 62 + 36 + 2 * 34 + 18 + bh + 18 + 34 + 16
    total = sh + gap + dh
    _fit(total, BOTTOM - y0, "locked")
    extra = BOTTOM - y0 - total
    gap += min(extra * .3, 50)
    more = int(min(extra * .7, 170) // 34)                  # 文件下半部多畫幾行灰線，把空間用滿
    dh += more * 34
    c.textbox(X0, y0, sw, hl, fill=CREAM, tcolor=DEEP, stroke=DEEP, dash="8 8", align="center", h=sh)
    c.textbox(X0 + sw + 40, y0, sw, hr, fill=DEEP, tcolor=CREAM, align="center", h=sh)
    dy = y0 + sh + gap
    c.rect(X0, dy, w, dh, fill=CREAM, stroke=DEEP, sw=4, rx=20)
    c.text(X0 + 30, dy + 12, 320, doc["text"], "ds", TEAL, "left")
    ly = dy + 62
    for i in range(2):
        c.rect(X0 + 40, ly + i * 34, w - 80 - (i * 90 % 200), 14, fill=LIGHT, op=.55, rx=7)
    by = ly + 2 * 34 + 12
    c.rect(X0 + 28, by, w - 56, bh, fill=GOLD, rx=14)
    c.text(X0 + 60, by + (bh - c.lines(blk["text"], w - 150, 34) * 44.2) / 2, w - 150, blk["text"], "dn", DEEP, "left", (X0 + 28, by, w - 56, bh))
    ly2 = by + bh + 24
    for i in range(1 + more):
        c.rect(X0 + 40, ly2 + i * 34, w - 80 - ((i + 1) * 110 % 260), 14, fill=LIGHT, op=.55, rx=7)
    # 左邊的箭頭被擋下（×），右邊的箭頭到達受保護區塊
    lx, rx = X0 + sw / 2, X0 + sw + 40 + sw / 2
    my = y0 + sh + gap * 0.5                            # ×（被擋下）畫在文件上緣之上，不壓到文件裡的字
    c.line(lx, y0 + sh + 6, lx, my - 22, TEAL, 4)
    c.line(lx - 18, my - 18, lx + 18, my + 18, DEEP, 7)
    c.line(lx - 18, my + 18, lx + 18, my - 18, DEEP, 7)
    c.arrow(rx, y0 + sh + 6, rx, by + 8 + (dy - (y0 + sh)) * 0 , color=GOLD, sw=6, head=20)
    return y0 + total


# ------------------------------------------------------------------ equation（算式：A × B ＝ C，底下可接一行補充）
def equation(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 算元 [{text（大數字）, sub（單位或名稱）, sub2?（小字說明）, emph?}]；ops（選用，預設 ["×", "="]）；
    outcomes[0]（選用）= 底下一條橫框 {text, sub?}。2026-10-14 新增：點陣排成方陣說不出「幾乘幾等於幾」，算式圖才是這個畫面。"""
    nodes, ops = spec["nodes"], spec.get("ops", ["×", "="])
    foot = (spec.get("outcomes") or [None])[0]
    n, opw, w = len(nodes), 88, X1 - X0
    bw = (w - opw * (n - 1)) / n
    iw = bw - 36
    hs = [90 + c.lines(nd["sub"], iw, 34) * 44.2 + (c.lines(nd["sub2"], iw, 28) * 39.2 + 6 if nd.get("sub2") else 0) + 56 for nd in nodes]
    bh = max(hs)
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    gap = 34 if foot else 0
    total = bh + gap + fh
    _fit(total, BOTTOM - y0, "equation")
    extra = BOTTOM - y0 - total
    bh += min(extra * .5, 140)
    twm = max(90 + c.lines(nd["sub"], iw, 34) * 44.2 + (c.lines(nd["sub2"], iw, 28) * 39.2 + 6 if nd.get("sub2") else 0) for nd in nodes)   # 三個算元的數字對齊在同一高度
    for i, nd in enumerate(nodes):
        x = X0 + i * (bw + opw)
        emph = nd.get("emph")
        c.rect(x, y0, bw, bh, fill=GOLD if emph else CREAM, stroke=None if emph else DEEP, dash=None if emph else "8 8")
        ty = y0 + (bh - twm) / 2
        box = (x, y0, bw, bh)
        c.text(x + 18, ty, iw, nd["text"], "dv", DEEP, "center", box)
        c.text(x + 18, ty + 90, iw, nd["sub"], "dn", DEEP, "center", box)
        if nd.get("sub2"):
            c.text(x + 18, ty + 90 + c.lines(nd["sub"], iw, 34) * 44.2 + 6, iw, nd["sub2"], "ds", DEEP, "center", box)
        if i < n - 1:
            c.text(x + bw + 8, y0 + bh / 2 - 40, opw - 16, ops[i], "dv", DEEP, "center")
    y = y0 + bh
    if foot:
        y += gap
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ tokens（符號序列：一列一步，每格一個符號）
TOKEN_TONES = {   # tone → (fill, stroke, dash, 主字色, 小字色)
    "rtg":    (TEAL, None, None, CREAM, CREAM),
    "state":  (DEEP, None, None, CREAM, LIGHT),
    "action": (CREAM, DEEP, None, DEEP, DEEP),
    "reward": (LIGHT, None, None, DEEP, DEEP),
    "mask":   (GOLD, None, None, DEEP, DEEP),
}


def tokens(c: Canvas, spec: dict, y0: float) -> float:
    """steps = [{label（列首小字，例如「第一步」）, cells:[{text, sub?, tone}]}]，一列一步、每格一個符號；
    tone：rtg／state／action／reward／mask（mask＝被蓋住、要模型猜的那格，金色）；more（選用，true）＝最後一列後面畫三個點，表示還有下去；
    outcomes[0]（選用）＝底下一條橫框 {text, sub?, tone?}（tone: good 金色，否則深海）。
    2026-10-18 新增（Decision Transformer）：「交錯排列的序列」「蓋住其中一格」是符號序列，流程圖與表格說不出這個畫面。"""
    steps, foot, more = spec["steps"], (spec.get("outcomes") or [None])[0], bool(spec.get("more"))
    w, lw, gap, vgap, pad = X1 - X0, 120, 16, 30, 14
    ncell = max(len(s["cells"]) for s in steps)
    cw = (w - lw - gap * (ncell - 1)) / ncell
    iw = cw - 2 * pad

    def ch(cell):
        return c.lines(cell["text"], iw, 34) * 44.2 + (c.lines(cell["sub"], iw, 28) * 39.2 + 6 if cell.get("sub") else 0) + 2 * pad + 8
    hs = [max(ch(cell) for cell in s["cells"]) for s in steps]
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    more_h = 64 if more else 0
    total = sum(hs) + vgap * (len(steps) - 1) + more_h + (vgap + fh if foot else 0)
    _fit(total, BOTTOM - y0, "tokens")
    extra = BOTTOM - y0 - total
    add = min(extra * .6 / len(steps), 60)
    hs = [h + add for h in hs]
    vg = vgap + min((extra - add * len(steps)) / max(len(steps) - 1 + (1 if foot else 0) + (1 if more else 0), 1), 30)
    y = y0
    ax = X0 + 44                                         # 列首小字下方的箭頭（一步接一步）
    for i, st in enumerate(steps):
        h = hs[i]
        c.text(X0, y + h / 2 - 20, lw - 8, st["label"], "ds", TEAL, "left")
        for k, cell in enumerate(st["cells"]):
            fill, stroke, dash, tc, sc = TOKEN_TONES[cell.get("tone", "state")]
            c.textbox(X0 + lw + k * (cw + gap), y, cw, cell["text"], cell.get("sub"), fill=fill, tcolor=tc, scolor=sc,
                      stroke=stroke, dash=dash, align="center", pad=pad, h=h)
        y += h
        if i < len(steps) - 1 or more:
            c.arrow(ax, y + 4, ax, y + vg - 4, TEAL, 4, 12)
            y += vg
    if more:
        for j in range(3):
            c.circle(ax, y + 8 + j * 18, 5, fill=TEAL)
        y += more_h
    if foot:
        y += vg if not more else 18
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=GOLD if foot.get("tone") == "good" else DEEP,
                  tcolor=DEEP if foot.get("tone") == "good" else CREAM, scolor=DEEP if foot.get("tone") == "good" else LIGHT, align="center", h=fh)
        y += fh
    return y


KINDS = {"flow": flow, "compare": compare, "pairs": pairs, "samples": samples, "paths": paths, "epochs": epochs,
         "dotgrid": dotgrid, "dumbbell": dumbbell, "range": range_chart, "funnel": funnel,
         "batches": batches, "decay": decay, "stops": stops, "fan": fan, "peaks": peaks, "quad": quad, "locked": locked, "equation": equation, "tokens": tokens}


def build(spec: dict, y0: float, ctx: Ctx) -> tuple[str, str, float]:
    global BOTTOM
    BOTTOM = 1180 if spec.get("note") else 1235       # 有圖註（y=1196）時，圖要在它上面結束
    c = Canvas(ctx)
    bottom = KINDS[spec["kind"]](c, spec, y0)
    return "".join(c.svg), "".join(c.html), bottom


def texts(sl: dict) -> list[str]:
    """示意圖上的所有文字與數字（逐欄位，給 check_a 的數字／名稱檢查與 build_package 的審查文字用）。"""
    out = []
    for st in sl.get("steps", []):
        out.append(st["label"])
        for cell in st["cells"]:
            out.append(cell["text"]); out += [cell["sub"]] if cell.get("sub") else []
    for n in sl.get("nodes", []) + sl.get("outcomes", []):
        out.append(n["text"]); out += [n["sub"]] if n.get("sub") else []; out += [n["sub2"]] if n.get("sub2") else []
    if sl.get("loop"):
        out.append(sl["loop"])
    for col in sl.get("columns", []):
        out.append(col["head"])
        for it in col["items"]:
            out.append(it["text"]); out += [it["sub"]] if it.get("sub") else []
    out += list(sl.get("heads", []))
    for l, r in sl.get("pairs", []):
        out += [l, r]
    if "count" in sl:
        out.append(f"{sl['count']}")
    if "group" in sl:
        out.append(f"{sl['group']}")
    u = sl.get("unit", "")
    if "start" in sl:
        out += [f"{sl['start']:g}{u}", f"{sl['end']:g}{u}"]
    for p in sl.get("points", []):
        out += [p["name"], f"{p['value']:g}{u}"]
    if sl.get("ref"):
        out += [sl["ref"]["name"], f"{sl['ref']['value']:g}{u}"]
    for r in sl.get("ranges", []):
        out.append(r["name"]); out += [r["sub"]] if r.get("sub") else []
        out += [f"{r['lo']:g}{u}", f"{r['hi']:g}{u}"]
    return out
