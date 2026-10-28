"""示意圖版型（layout: diagram）的幾何與繪製。由 render.py 呼叫：build(spec, y0, ctx) -> (svg 內容, 文字 html, 底部 y)。

為什麼有這份：2026-10-11 人的回饋——「每篇 post 的 chart 都是同一個模板、都是 bar chart；文字下面空出來的區塊是塗鴉牆，
流程圖、任何圖都可以，只要讓讀者更好理解、覺得有趣」。所以除了橫條圖，另有下列 kind（spec 的 `kind` 欄位）：
  flow      由上往下的流程：nodes（每個 text、選用 sub）、選用 outcomes（兩三個結果，good 金色／bad 外框）、選用 loop（底部虛線框的說明）
  compare   兩欄並列：columns = [{head, items:[{text, sub?, gone?, emph?}]}]（gone = 劃掉、emph = 左側金條）
  pairs     「換掉什麼 → 換成什麼」：heads = [左標, 右標]、pairs = [[左, 右], …]、選用 outcomes[0]（底下一條橫框，tone: good 金色）
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
  seesaw    蹺蹺板（2026-10-22，Bradley-Terry）：nodes = [{text（隊名）, sub?（實力值）, blocks（方塊數）, win（贏的機率標籤）}, {…}]；重的一端壓低（傾斜角隨兩端比例）；梁下面一條橫條，長度與兩端方塊數的比例成正比；選用 outcomes[0]（底下一條橫框）；純示意
  hidden    水面上看得到的、水面下看不到的：heads = [上標籤, 下標籤]、nodes = 水面上的結果 [{text}]（最多 3）、outcomes = 水面下藏著的東西 [{text, sub?}]（畫成虛線框的「？」；最多 3）
  cycle     三個節點繞成一圈（A→B→C→A，最後一條箭頭金色）：nodes = 3 個 [{text, sub?}]、heads = 3 條邊的標籤（依序 A→B、B→C、C→A）、選用 outcomes[0]（底下一條橫框）
  links     左右兩排節點之間的連線（二部圖，2026-10-24，SAG 的「事件↔實體」）：nodes = 左排 [{text, sub?, emph?}]、outcomes = 右排 [{text, sub?, emph?}]、edges = [[左序號, 右序號], …]（0 起）、選用 hot = 要畫成金色粗線的邊、選用 heads = [左標籤, 右標籤]；連線全由 edges 決定，純示意時圖註要標「示意」
  hops      幾跳才到答案（2026-10-24，SAG 的「4 跳 vs 1 跳」）：nodes = 每一列 [{text, sub?, hops}]（hops＝箭頭數，圖上就畫幾條；text／sub 若有數字，必須等於 hops）、選用 heads = [起點標籤, 終點標籤]；每一跳等長，所以越多跳越長
  bubble    一個大泡泡圈住好幾個東西（2026-10-24，SAG 的「超邊」）：heads = [左標籤, 右標籤]、nodes = [{text, sub?}（左：一般的邊，只連兩點）, {text, sub?}（右：泡泡的說明）]、outcomes = 泡泡裡的項目 [{text}]（2～8 個，畫成小標籤）；左邊預設畫兩個點與一條線（`chain: true` 時改畫一串只連兩點的邊，用 outcomes 的名字標點，2～4 個）；右邊畫金色泡泡
  drift     一路偏掉的路徑（2026-10-24，SAG 的「誤差沿推理鏈放大」）：heads = 每一站的標籤（3～6 個，第一個是起點、最後一個是答案）、nodes = [{text}（正確的路線）, {text, sub?}（實際走的路線）]；實際路線每一站偏得更多（偏移量由程式依站序算，只示意，不是數據）
  ingest    兩段式架構圖（2026-10-24，SAG 論文圖二的版型）：heads = [上段標籤, 下段標籤]；nodes = 上段四欄的標籤 4 個 [{text, sub?}]（原始片段、一對一轉成的東西、多對多綁定的東西、存放處）；
            outcomes = 下段由左到右的步驟 2～3 個 [{text, sub?}]（最後一個金色，下面畫一個小的局部超圖）。上段的方塊、圓點、連線是固定的示意（不帶文字）
  roles     三列角色卡（2026-10-25，SAG 第 2 則）：nodes = 三列 [{text（元件名）, sub（角色，一個詞）, sub2（做什麼）, icon: db／vec／llm}]
  embed     精確比對 vs 向量空間：heads = [左標, 右標]、nodes = 左邊比對列 [{text, sub?, ok}]、outcomes = 右邊向量空間的 3 個點 [{text, sub?}]（第一個是中心）；純示意
  online    線上檢索路線圖（SAG 論文圖二下半的重畫）：heads = [起點, 結果]、nodes = 第一步兩條路、outcomes = [第二步, 第三步左路, 第三步右路]
  gate      水庫閘門，兩道各一列：count（名額）、nodes = 兩列 [{text, sub?}]（每列：標題，下面左邊一池散點、中間閘門、右邊整齊的格子）；純示意，不是實際數量
  concat    兩路各一排、匯成一排：heads = [左路, 右路]、nodes = [{text}（上方一句話）, {text, sub?}（結果）]；每路 5 個、匯整後 10 個，純示意
  rails     兩條軌道各撈一排、合併成一排（A 漏掉的一格由 B 補上）：heads = [A 路, B 路]、nodes = [{text, sub?}, {text, sub?}]、outcomes[0] = {text}（合併後）；純示意
  joint     逐一打分 vs 一起評估：heads = [左標, 右標]、nodes = 兩邊 [{text, sub（例子）, sub2（結論）}]；純示意
  hops 的選用欄位（2026-10-26）：spec 頂層 fade: true＝箭頭一跳比一跳淡（圖上傳遞的分數越來越弱，純示意，圖註要說明）；每列 shortcut: true＝鏈上方畫一條被叉掉的虛線捷徑，標籤用該列的 sub2
  scoreboard 戰績表（2026-10-26，SAG 第 3 則）：nodes = 每列一個資料集 [{text, sub?, emph?}]、heads = 兩個欄標籤、outcomes = 圖例 [{text（深色那一方）}, {text（淺色那一方）}]、cells = 每列每欄的 [深色值, 淺色值]（字串，例 "64.1"）；
            每格兩條橫條，軸從 0 起、長度與數值成正比（axis_max 預設 100）；深色值小於淺色值的格子畫虛線框（圖註要說明）；emph 的列底下墊金色淡底
  leak      每一跳都漏一些（2026-10-26）：nodes = 兩條路 [{text, sub?}（走很多跳的）, {text, sub?}（一次到位的）]、heads = 兩條路箭頭上的標籤（例：剪枝）；兩條路從同一個起點到同一個終點，每個站畫一格點，漏掉的畫成虛線空點；點數是固定示意，圖註要標「示意」
  amplify   誤差沿路放大 vs 精確比對（2026-10-26）：nodes = 兩條路 [{text, sub?}, {text, sub?}]、heads = 第一條的兩端標籤（起點、終點）、outcomes[0] = 第二條的標籤；第一條畫一個越來越寬的楔形，第二條是一條等寬的金色帶；純示意
  receipt   帳單（2026-10-27，SAG 第 4 則）：heads = [抬頭, 「換來的」標籤]、nodes = 品項 2～4 個 [{text, sub?}]（自動編號）、outcomes = 換來的東西 1～3 個 [{text}]（金色小標籤）；米色紙、下緣鋸齒
  squeeze   名額線擠掉了誰（2026-10-27）：heads = [左端標, 右端標, 名額線標]、nodes = [{text, sub?}（上方說明）, {text, sub?}（被擠出去的金點）]、outcomes = 推理鏈兩端 [{text}, {text}]；排隊的點是固定示意，圖註要標「示意」
  alias     別名對齊：傳統合併、SAG 不合併（2026-10-27）：heads = [上段標, 下段標]、outcomes = 同一個東西的 3 種寫法 [{text}]、nodes = [{text, sub?}（合併後）, {text, sub?}（下段說明）]；純示意
  handoff   把工作從線下搬到線上（2026-10-27）：heads = [上帶標, 下帶標, 箭頭標]、nodes = [{text, sub?}（線下不做的事）, {text, sub?}（線上接手的做法）]、outcomes[0] = {text}（線下因此得到的好處）；純示意
  mismatch  同一個東西寫法不同就接不起來（2026-10-27）：heads = [上段標, 下段標, 缺口標]、nodes = [{text, sub?}（共同寫法＋上段說明）, {text, sub?}（另一種寫法＋下段說明）]、outcomes = 兩個事件 [{text, sub?}]；純示意
  ledger    只能往後新增的記錄簿（2026-10-27）：heads = [時間軸標籤]、nodes = 依時間排的紀錄 2～5 筆 [{text, sub?, new?, ask?}]（舊的畫鎖、new 金色加「＋」、ask 左邊釘金色「？」表示分不出誰有效）、outcomes[0] = {text, sub?}（右邊說明）；例子要標「假設」
  stops     由上往下三個停靠點（不按比例）：nodes = [{text, sub?, emph?}]、選用 heads = [上端標籤, 下端標籤]

規則：圖形全部用 class "bg"（不進程式 B 的文字與圖形重疊檢查），所以排版由這裡負責避開文字；框內的文字由程式 B 的「框內文字不超出框」檢查；
比例（dumbbell／range）由程式 B 檢查圖形位置與數值成正比。字級只用 {28, 34, 40, 56}。
"""
from __future__ import annotations

import math
import re

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

    def arrow(self, x1, y1, x2, y2, color=TEAL, sw=4, head=14, op=None):
        self.line(x1, y1, x2, y2, color, sw, op=op)
        ang = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2), (x2 - head * math.cos(ang - .45), y2 - head * math.sin(ang - .45)),
             (x2 - head * math.cos(ang + .45), y2 - head * math.sin(ang + .45))]
        self.poly(p, fill=color, closed=True, op=op)

    def raw(self, svg: str):
        self.svg.append(svg)

    # ---- 文字（class t；data-box 讓程式 B 檢查文字不超出框）
    def text(self, x, y, w, s, cls="dn", color=DEEP, align="left", box=None, extra=""):
        b = f' data-box="{box[0]:.1f},{box[1]:.1f},{box[2]:.1f},{box[3]:.1f}"' if box else ""
        t = self.ctx.bind(s).replace("\n", "<br>")
        self.html.append(f'<div class="t abs {cls}" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;color:{color};text-align:{align}{extra}"{b}>{self.ctx.esc(t) if "<br>" not in t else "<br>".join(self.ctx.esc(p) for p in t.split("<br>"))}</div>')

    def lines(self, s, w, size):
        # 文字裡的 \n 是明確換行（text() 會轉成 <br>），每一段各自估行數再加總
        # 分數（\\frac）比一般行高：含分數的那一段多算約一行；含上下標或 \\mathcal 的算式多算約三分之一行
        return sum(self.ctx.est_lines(self.ctx.bind(seg), w / size - 0.7) + (0.9 if re.search(r"\\[dt]?frac", seg) else 0.35 if re.search(r"\$[^$]*[_^\\][^$]*\$", seg) else 0) for seg in s.split("\n"))

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
    foot = (spec.get("outcomes") or [None])[0]      # 選用（2026-10-22）：底下一條橫框，例如拿前面的例子驗算 {text, sub?, tone?}
    fh = (c.lines(foot["text"], X1 - X0 - 44, 34) * 44.2 + (c.lines(foot["sub"], X1 - X0 - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    fgap = 30 if foot else 0
    total = 44 + 14 + sum(rows) + 18 * (len(prs) - 1) + fgap + fh
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
    if foot:
        good = foot.get("tone") == "good"
        y += fgap - 18
        c.textbox(X0, y, X1 - X0, foot["text"], foot.get("sub"), fill=GOLD if good else DEEP, tcolor=DEEP if good else CREAM,
                  scolor=DEEP if good else LIGHT, align="center", h=fh)
        return y + fh
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


# ------------------------------------------------------------------ seesaw（蹺蹺板：兩端各疊幾塊，梁向重的一邊傾斜；下面一條橫條是贏的機率）
def _stack(c: Canvas, x, base_y, n, u, fill, cols):
    """從 base_y（梁的上緣）往上疊 n 塊（每列 cols 塊）。"""
    for i in range(n):
        col, row = i % cols, i // cols
        c.rect(x + col * u, base_y - (row + 1) * u, u - 4, u - 4, fill=fill, rx=max(3, u * .1))


def seesaw(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = [{text（隊名）, sub?（實力值）, blocks（方塊數）, win（贏的機率標籤，放在下面橫條裡）}, {…}]。
    第一個是重的一端（左），第二個是輕的一端（右，金色）。傾斜角 = 16° x（重 − 輕）/（重 ＋ 輕），最多 14°；純示意。
    橫條的長度與兩端方塊數的比例成正比（左：深海、右：金色）；outcomes[0]（選用）= 底下一條橫框 {text, sub?}。"""
    (a, b), foot = spec["nodes"], (spec.get("outcomes") or [None])[0]
    na, nb = int(a["blocks"]), int(b["blocks"])
    w = X1 - X0
    ca, cb = (2 if na > 3 else 1), (2 if nb > 3 else 1)
    ra, rb = math.ceil(na / ca), math.ceil(nb / cb)
    tilt = min(14.0, 16.0 * (na - nb) / (na + nb))
    L = 800.0
    lab_h = max(c.lines(n["text"], 330, 34) * 44.2 + (c.lines(n["sub"], 330, 28) * 39.2 + 6 if n.get("sub") else 0) for n in (a, b))
    bar_h = 84
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    avail = BOTTOM - y0
    fixed = lab_h + 16 + 34 + bar_h + (30 + fh if foot else 0)
    u = max(28.0, min(52.0, (avail - fixed - 120) / (max(ra, rb) + 1.2)))      # 方塊大小：依剩下的高度決定
    drop = (L / 2) * math.sin(math.radians(tilt))
    top = max(ra * u - drop, rb * u + drop) + 8                                   # 梁中心以上要留的高度
    fk = 70.0                                                                       # 支點高度
    zone = top + max(fk, drop + 20)
    total = zone + 16 + lab_h + 34 + bar_h + (30 + fh if foot else 0)
    _fit(total, avail, "seesaw")
    cx, cy = X0 + w / 2, y0 + top
    thick = 14
    parts = []
    ux = cx - L / 2 + u * .5
    rx_ = cx + L / 2 - u * .5 - cb * u
    inner = Canvas(c.ctx)
    _stack(inner, ux, cy - thick / 2, na, u, TEAL, ca)
    _stack(inner, rx_, cy - thick / 2, nb, u, GOLD, cb)
    inner.rect(cx - L / 2, cy - thick / 2, L, thick, fill=DEEP, rx=thick / 2)
    c.raw(f'<g transform="rotate({-tilt:.2f} {cx:.1f} {cy:.1f})">' + "".join(inner.svg) + '</g>')
    c.poly([(cx, cy + 2), (cx - fk * .65, cy + fk), (cx + fk * .65, cy + fk)], fill=TEAL, closed=True)
    fy = cy + max(fk, drop + 20)
    c.line(cx - L / 2 - 20, fy, cx + L / 2 + 20, fy, DEEP, 4)
    # 兩端的標籤：放在梁兩端下方的地線之下，置中對齊各自的方塊堆
    ex = [cx - (L / 2) * math.cos(math.radians(tilt)) + u, cx + (L / 2) * math.cos(math.radians(tilt)) - u]
    y = fy + 16
    for ex_, n in zip(ex, (a, b)):
        l1 = c.lines(n["text"], 330, 34)
        c.text(ex_ - 165, y, 330, n["text"], "dn", DEEP, "center")
        if n.get("sub"):
            c.text(ex_ - 165, y + l1 * 44.2 + 6, 330, n["sub"], "ds", DEEP, "center")
    y += lab_h + 34
    # 贏的機率橫條：兩段的寬度與方塊數的比例成正比
    wa = w * na / (na + nb)
    c.rect(X0, y, wa, bar_h, fill=DEEP, rx=14)
    c.rect(X0 + wa, y, w - wa, bar_h, fill=GOLD, rx=14)
    c.text(X0 + 14, y + (bar_h - 44) / 2, wa - 28, a["win"], "dn", CREAM, "center", (X0, y, wa, bar_h))
    c.text(X0 + wa + 8, y + (bar_h - 39) / 2, w - wa - 16, b["win"], "dl", DEEP, "center", (X0 + wa, y, w - wa, bar_h))
    y += bar_h
    if foot:
        y += 30
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ hidden（水面上看得到的，水面下看不到的）
def hidden(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [上標籤, 下標籤]；nodes = 水面上的結果 [{text}]（1～3 個）；outcomes = 水面下藏著的東西 [{text, sub?}]（1～3 個，畫成虛線框的「？」）。"""
    h_up, h_dn = spec["heads"]
    res, hid = spec["nodes"], spec["outcomes"]
    w = X1 - X0
    gap = 20
    cw = (w - gap * (len(res) - 1)) / len(res)
    rh = max(c.lines(r["text"], cw - 36, 34) for r in res) * 44.2 + 40
    hw = (w - gap * (len(hid) - 1)) / len(hid)
    hh = 96 + max(c.lines(n["text"], hw - 28, 34) * 44.2 + (c.lines(n["sub"], hw - 28, 28) * 39.2 + 6 if n.get("sub") else 0) for n in hid) + 36
    top = 46 + rh + 50                                  # 標籤 + 結果 + 水面上的留白
    sea_head = 54
    total = top + 18 + sea_head + hh + 24
    avail = BOTTOM - y0
    _fit(total, avail, "hidden")
    extra = avail - total
    rh += min(extra * .3, 40); hh += min(extra * .4, 60)
    top = 46 + rh + 50
    sea_y = y0 + top
    sea_h = (BOTTOM - sea_y) if extra > 0 else (18 + sea_head + hh + 24)
    c.text(X0, y0, w, h_up, "ds", TEAL, "left")
    for k, r in enumerate(res):
        x = X0 + k * (cw + gap)
        c.rect(x, y0 + 46, cw, rh, fill=CREAM, stroke=DEEP, sw=3, rx=14)
        l1 = c.lines(r["text"], cw - 36, 34)
        c.text(x + 18, y0 + 46 + (rh - l1 * 44.2) / 2, cw - 36, r["text"], "dt", DEEP, "center", (x, y0 + 46, cw, rh))
    # 水面：一條浪線，浪線下面是深海色的面板
    pts = [(X0 + i * w / 40, sea_y + 7 * math.sin(i * 0.9)) for i in range(41)]
    c.poly(pts + [(X1, sea_y + sea_h), (X0, sea_y + sea_h)], fill=DEEP, closed=True)
    c.poly(pts, stroke=LIGHT, sw=4)
    c.text(X0 + 24, sea_y + 22, w - 48, h_dn, "ds", LIGHT, "left")
    by = sea_y + 22 + sea_head
    for k, n in enumerate(hid):
        x = X0 + k * (hw + gap)
        bh = sea_h - (by - sea_y) - 24
        c.rect(x + 14, by, hw - 28, bh, fill="none", stroke=LIGHT, sw=3, dash="10 8", rx=14)
        l1 = c.lines(n["text"], hw - 56, 34)
        th = 84 + l1 * 44.2 + (c.lines(n["sub"], hw - 56, 28) * 39.2 + 6 if n.get("sub") else 0)
        ty = by + (bh - th) / 2
        box = (x + 14, by, hw - 28, bh)
        c.text(x + 28, ty, hw - 56, "？", "dv", GOLD, "center", box)
        c.text(x + 28, ty + 84, hw - 56, n["text"], "dn", CREAM, "center", box)
        if n.get("sub"):
            c.text(x + 28, ty + 84 + l1 * 44.2 + 6, hw - 56, n["sub"], "ds", LIGHT, "center", box)
    return sea_y + sea_h


# ------------------------------------------------------------------ cycle（三個節點繞成一圈：A→B→C→A）
def cycle(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 3 個 [{text, sub?}]（上、左下、右下）；heads = 3 條邊的標籤，依序 A→B（左邊）、B→C（下邊）、C→A（右邊，金色）；
    outcomes[0]（選用）= 底下一條橫框 {text, sub?}。"""
    nodes, heads, foot = spec["nodes"], spec["heads"], (spec.get("outcomes") or [None])[0]
    w, r = X1 - X0, 64
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    avail = BOTTOM - y0
    under = 24 + 44                                      # 下邊標籤
    fixed = 2 * r + under + (28 + fh if foot else 0)
    tri = min(330.0, avail - fixed)
    _fit(fixed + 220, avail, "cycle")                    # 三角形至少要有 220 的高
    ya = y0 + r
    yb = ya + tri
    A, B, C = (X0 + w / 2, ya), (X0 + w / 2 - 250, yb), (X0 + w / 2 + 250, yb)
    pts = [A, B, C]
    def trim(p, q, d):
        dx, dy = q[0] - p[0], q[1] - p[1]; n = math.hypot(dx, dy)
        return (p[0] + dx / n * d, p[1] + dy / n * d)
    for i, (p, q) in enumerate(((A, B), (B, C), (C, A))):
        s_, e_ = trim(p, q, r + 8), trim(q, p, r + 14)
        gold = i == 2
        c.arrow(s_[0], s_[1], e_[0], e_[1], color=GOLD if gold else DEEP, sw=9 if gold else 6, head=26 if gold else 22)
    for p, n in zip(pts, nodes):
        c.circle(p[0], p[1], r, fill=DEEP)
        c.text(p[0] - r, p[1] - 36, 2 * r, n["text"], "dv", CREAM, "center", (p[0] - r, p[1] - r, 2 * r, 2 * r))
    lw = 300
    c.text(X0, (A[1] + B[1]) / 2 - 22, lw, heads[0], "dn", DEEP, "right")
    c.text(X0 + w / 2 - lw / 2, yb + r + 24, lw, heads[1], "dn", DEEP, "center")
    c.text(X1 - lw, (A[1] + C[1]) / 2 - 22, lw, heads[2], "dn", DEEP, "left")
    y = yb + r + under
    if foot:
        y += 28
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ links（左右兩排節點之間的連線）
def links(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 左排、outcomes = 右排、edges = [[左序號, 右序號], …]（0 起，連線只畫 edges 有的）、hot = 金色粗線的邊、heads = [左標籤, 右標籤]。"""
    L, R, edges = spec["nodes"], spec["outcomes"], spec["edges"]
    heads = spec.get("heads", [])
    hot = {tuple(e) for e in spec.get("hot", [])}
    for l, r in list(edges) + list(hot):
        if not (0 <= l < len(L) and 0 <= r < len(R)):
            raise ValueError(f"links 的邊 [{l}, {r}] 超出節點範圍（左 {len(L)} 個、右 {len(R)} 個）")
    if not set(map(tuple, hot)) <= set(map(tuple, edges)):
        raise ValueError("links 的 hot 必須是 edges 的子集")
    bw, pad = 390, 22
    w = X1 - X0

    def bh(n):
        return c.lines(n["text"], bw - 2 * pad, 34) * 44.2 + (c.lines(n["sub"], bw - 2 * pad, 28) * 39.2 + 6 if n.get("sub") else 0) + 2 * pad
    hl, hr = [bh(n) for n in L], [bh(n) for n in R]
    gmin = 16
    need = max(sum(hl) + gmin * (len(hl) - 1), sum(hr) + gmin * (len(hr) - 1))
    head_h = 50 if heads else 0
    avail = BOTTOM - y0 - head_h
    _fit(need, avail, "links")
    A = min(avail, max(need * 1.25, need + 100))

    def place(hs):
        if len(hs) == 1:
            return [y0 + head_h + (A - hs[0]) / 2]
        g = (A - sum(hs)) / (len(hs) - 1)
        ys, y = [], y0 + head_h
        for h in hs:
            ys.append(y); y += h + g
        return ys
    yl, yr = place(hl), place(hr)
    if heads:
        c.text(X0, y0, bw, heads[0], "ds", TEAL, "left")
        c.text(X1 - bw, y0, bw, heads[1], "ds", TEAL, "right")
    xl, xr = X0 + bw, X1 - bw
    for l, r in edges:           # 先畫線，再畫框蓋住線頭
        if (l, r) not in hot:
            c.line(xl, yl[l] + hl[l] / 2, xr, yr[r] + hr[r] / 2, TEAL, 4)
    for l, r in edges:
        if (l, r) in hot:
            c.line(xl, yl[l] + hl[l] / 2, xr, yr[r] + hr[r] / 2, GOLD, 8)
    for col, ys, hs, x in ((L, yl, hl, X0), (R, yr, hr, xr)):
        for n, y, h in zip(col, ys, hs):
            emph = n.get("emph")
            c.textbox(x, y, bw, n["text"], n.get("sub"), fill=GOLD if emph else DEEP, tcolor=DEEP if emph else CREAM,
                      scolor=DEEP if emph else LIGHT, align="left", h=h)
    return y0 + head_h + A


# ------------------------------------------------------------------ hops（幾跳才到答案）
def hops(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 每一列 [{text, sub?, sub2?, shortcut?, hops}]；heads = [起點標籤, 終點標籤]（選用）。每一跳等長，箭頭數 = hops。
    fade: true（頂層）＝箭頭一跳比一跳淡；shortcut: true（每列）＝鏈上方畫一條被叉掉的虛線捷徑，標籤是該列的 sub2。"""
    rows, heads = spec["nodes"], spec.get("heads", [])
    fade = bool(spec.get("fade"))
    r, w = 26, X1 - X0
    hmax = max(n["hops"] for n in rows)
    for n in rows:
        if not isinstance(n["hops"], int) or n["hops"] < 1:
            raise ValueError(f"hops 的 hops 必須是 1 以上的整數：{n['hops']!r}")
        nums = re.findall(r"\d+", n["text"] + " " + n.get("sub", ""))
        if nums and str(n["hops"]) not in nums:
            raise ValueError(f"hops 圖上的數字 {nums} 與箭頭數 {n['hops']} 不符（圖上畫幾跳，文字就要寫幾跳）")
        if n.get("shortcut") and not n.get("sub2"):
            raise ValueError("hops 的 shortcut 那一列要有 sub2（捷徑被叉掉的標籤）")
    step = (w - 2 * r) / hmax
    lab_h = 40 if heads else 0
    SC = 120                                    # 捷徑弧線與標籤佔的高度
    hs = [c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0) + 2 * r + lab_h + 30 + (SC if n.get("shortcut") else 0) for n in rows]
    total = sum(hs) + 36 * (len(rows) - 1)
    _fit(total, BOTTOM - y0, "hops")
    extra = min((BOTTOM - y0 - total) / len(rows), 90)
    y = y0
    for n, h in zip(rows, hs):
        h += extra
        l1 = c.lines(n["text"], w, 34)
        c.text(X0, y, w, n["text"], "dn", DEEP, "left")
        ty = y + l1 * 44.2
        if n.get("sub"):
            c.text(X0, ty + 4, w, n["sub"], "ds", TEAL, "left"); ty += c.lines(n["sub"], w, 28) * 39.2 + 6
        sc = SC if n.get("shortcut") else 0
        cy = ty + 18 + sc + r + (h - (ty - y) - 18 - sc - 2 * r - lab_h) / 2
        xs = [X0 + r + i * step for i in range(n["hops"] + 1)]
        if sc:                                  # 捷徑：從起點直接跳到答案，被叉掉
            top = cy - r - 54
            c.line(xs[0], cy - r - 6, xs[0] + 40, top, TEAL, 4, dash="10 10")
            c.line(xs[0] + 40, top, xs[-1] - 40, top, TEAL, 4, dash="10 10")
            c.line(xs[-1] - 40, top, xs[-1], cy - r - 6, TEAL, 4, dash="10 10")
            mx = (xs[0] + xs[-1]) / 2
            c.circle(mx, top, 22, fill=CREAM, stroke=DEEP, sw=4)
            c.line(mx - 11, top - 11, mx + 11, top + 11, DEEP, 5); c.line(mx - 11, top + 11, mx + 11, top - 11, DEEP, 5)
            c.text(mx - 330, top - 68, 660, n["sub2"], "ds", DEEP, "center")
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            c.arrow(a + r + 4, cy, b - r - 8, cy, DEEP, 6, 20, op=(round(1 - 0.2 * k, 2) if fade else None))
        for i, x in enumerate(xs):
            last = i == len(xs) - 1
            c.circle(x, cy, r, fill=GOLD if last else DEEP)
        if heads:
            c.text(xs[0] - 60, cy + r + 8, 120, heads[0], "ds", TEAL, "center")
            c.text(xs[-1] - 60, cy + r + 8, 120, heads[1], "ds", TEAL, "center")
        y += h + 36
    return min(y - 36, BOTTOM)


# ------------------------------------------------------------------ bubble（一個大泡泡圈住好幾個東西：超邊）
def bubble(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左標籤, 右標籤]；nodes = [{text, sub?}（左說明）, {text, sub?}（右說明）]；outcomes = 泡泡裡的項目 [{text}]（2～8 個）。"""
    heads, (ln, rn), items = spec["heads"], spec["nodes"], spec["outcomes"]
    if not 2 <= len(items) <= 8:
        raise ValueError(f"bubble 的 outcomes 要 2～8 個，現在是 {len(items)} 個")
    lw, gap = 300, 30
    rx0 = X0 + lw + gap
    rw = X1 - rx0
    pad, ch = 30, 72
    iw = rw - 2 * pad
    est = lambda t: sum(34 if ord(ch_) > 127 else 23 for ch_ in t) + 44
    rows, cur, used = [], [], 0
    for it in items:
        w = max(120, est(it["text"]))
        if w > iw:
            raise ValueError(f"bubble 的項目太長放不下：{it['text']!r}")
        if cur and used + w + 14 > iw:
            rows.append(cur); cur, used = [], 0
        cur.append((it, w)); used += w + 14
    rows.append(cur)
    bh = len(rows) * ch + (len(rows) - 1) * 16 + 2 * pad + 20
    hh = 56
    cap_l = c.lines(ln["text"], lw, 34) * 44.2 + (c.lines(ln["sub"], lw, 28) * 39.2 + 6 if ln.get("sub") else 0)
    cap_r = c.lines(rn["text"], rw, 34) * 44.2 + (c.lines(rn["sub"], rw, 28) * 39.2 + 6 if rn.get("sub") else 0)
    total = hh + bh + 26 + max(cap_l, cap_r)
    _fit(total, BOTTOM - y0, "bubble")
    extra = min(BOTTOM - y0 - total, 200)               # 空間有剩時把泡泡拉高
    top = y0 + hh
    bh += extra
    c.text(X0, y0, lw, heads[0], "ds", TEAL, "left")
    c.text(rx0, y0, rw, heads[1], "ds", TEAL, "left")
    cy = top + bh / 2
    if spec.get("chain"):                                           # 左：同一批實體拆成一串「只連兩點」的邊，每個點標名字
        m = len(items)
        cxs = [X0 + 40 + k * (lw - 80) / (m - 1) for k in range(m)]
        for a, b in zip(cxs, cxs[1:]):
            c.line(a, cy, b, cy, DEEP, 6)
        for x_, it in zip(cxs, items):
            c.circle(x_, cy, 20, fill=DEEP)
            c.text(x_ - 55, cy + 32, 110, it["text"], "ds", DEEP, "center")
    else:
        c.line(X0 + 36, cy, X0 + lw - 36, cy, DEEP, 6)              # 左：一條邊只連兩個點
        c.circle(X0 + 36, cy, 24, fill=DEEP)
        c.circle(X0 + lw - 36, cy, 24, fill=DEEP)
    c.rect(rx0, top, rw, bh, fill=GOLD, stroke=GOLD, sw=6, rx=int(min(bh / 2, 90)), op=.22)      # 右：金色泡泡
    y = top + (bh - (len(rows) * ch + (len(rows) - 1) * 16)) / 2
    for r in rows:
        tw = sum(w for _, w in r) + 14 * (len(r) - 1)
        x = rx0 + (rw - tw) / 2
        for it, w in r:
            c.rect(x, y, w, ch, fill=DEEP, rx=14)
            c.text(x + 22, y + (ch - 34 * 1.3) / 2, w - 44, it["text"], "dn", CREAM, "center", (x, y, w, ch))
            x += w + 14
        y += ch + 16
    ty = top + bh + 26
    c.text(X0, ty, lw, ln["text"], "dn", DEEP, "left")
    c.text(rx0, ty, rw, rn["text"], "dn", DEEP, "left")
    if ln.get("sub"):
        c.text(X0, ty + c.lines(ln["text"], lw, 34) * 44.2 + 4, lw, ln["sub"], "ds", TEAL, "left")
    if rn.get("sub"):
        c.text(rx0, ty + c.lines(rn["text"], rw, 34) * 44.2 + 4, rw, rn["sub"], "ds", TEAL, "left")
    return ty + max(cap_l, cap_r)


# ------------------------------------------------------------------ drift（一路偏掉的路徑：誤差沿推理鏈放大）
def drift_offsets(n: int, dmax: float) -> list[float]:
    """每一站的偏移量：起點為 0，之後越走偏得越多（二次增長）。"""
    return [dmax * (i / (n - 1)) ** 2 for i in range(n)]


def drift(c: Canvas, spec: dict, y0: float) -> float:
    """heads = 每一站的標籤（3～6 個）；nodes = [{text}（正確的路線）, {text, sub?}（實際走的路線）]。"""
    heads, (good, bad) = spec["heads"], spec["nodes"]
    n = len(heads)
    if not 3 <= n <= 6:
        raise ValueError(f"drift 的站數要 3～6 個，現在是 {n} 個")
    w = X1 - X0
    leg = [c.lines(good["text"], w - 120, 34) * 44.2, c.lines(bad["text"], w - 120, 34) * 44.2 + (c.lines(bad["sub"], w - 120, 28) * 39.2 + 6 if bad.get("sub") else 0)]
    legend_h = sum(leg) + 30
    lab_h = 44
    avail = BOTTOM - y0 - legend_h - lab_h - 40
    _fit(160, avail, "drift")
    dmax = min(avail - 40, 300)
    xs = [X0 + 70 + i * (w - 140) / (n - 1) for i in range(n)]
    ty = y0 + lab_h + 30                                         # 正確路線的高度
    offs = drift_offsets(n, dmax)
    for x, h in zip(xs, heads):
        c.text(x - 70, y0, 140, h, "ds", TEAL, "center")
    c.line(xs[0], ty, xs[-1], ty, TEAL, 5, dash="12 12")         # 正確路線：虛線
    for x in xs[1:-1]:
        c.circle(x, ty, 10, fill=CREAM, stroke=TEAL, sw=4)
    c.circle(xs[-1], ty, 24, fill=GOLD)                          # 正確的答案
    pts = [(x, ty + o) for x, o in zip(xs, offs)]
    c.poly(pts, stroke=DEEP, sw=7)                               # 實際路線：實線，越走越偏
    for x, y in pts[:-1]:
        c.circle(x, y, 14, fill=DEEP)
    x, y = pts[-1]
    c.circle(x, y, 24, fill=CREAM, stroke=DEEP, sw=6)
    c.line(x - 11, y - 11, x + 11, y + 11, DEEP, 6)
    c.line(x - 11, y + 11, x + 11, y - 11, DEEP, 6)
    ly = max(pts[-1][1] + 24 + 30, ty + dmax + 54)
    c.line(X0 + 6, ly + 22, X0 + 60, ly + 22, TEAL, 5, dash="12 12")
    c.text(X0 + 90, ly, w - 90, good["text"], "dn", DEEP, "left")
    ly2 = ly + leg[0] + 14
    c.line(X0 + 6, ly2 + 22, X0 + 60, ly2 + 22, DEEP, 7)
    c.text(X0 + 90, ly2, w - 90, bad["text"], "dn", DEEP, "left")
    if bad.get("sub"):
        c.text(X0 + 90, ly2 + c.lines(bad["text"], w - 90, 34) * 44.2 + 4, w - 90, bad["sub"], "ds", TEAL, "left")
    return ly2 + leg[1]


# ------------------------------------------------------------------ ingest（兩段式架構圖：上段線下建索引，下段查詢時）
INGEST_EDGES = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 3)]      # 事件 ↔ 實體 的多對多連線（示意）


def ingest(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [上段標籤, 下段標籤]；nodes = 上段四欄的標籤（4 個）；outcomes = 下段的步驟（2～3 個，最後一個金色）。"""
    heads, cols, steps = spec["heads"], spec["nodes"], spec["outcomes"]
    if len(cols) != 4:
        raise ValueError(f"ingest 的 nodes 要 4 個（四欄的標籤），現在是 {len(cols)} 個")
    if not 2 <= len(steps) <= 3:
        raise ValueError(f"ingest 的 outcomes 要 2～3 個，現在是 {len(steps)} 個")
    w, pad = X1 - X0, 22
    # 上段：四欄的 x 範圍
    cx = [(X0 + pad, 150), (X0 + 230, 170), (X0 + 470, 190), (X0 + 720, w - 720 - pad)]
    lab_h = max(c.lines(n["text"], cw, 28) * 39.2 + (c.lines(n["sub"], cw, 28) * 39.2 if n.get("sub") else 0) for n, (_, cw) in zip(cols, cx))
    rows_h = 2 * 58 + 30 + 44                          # 三列方塊（高 44），第二、三列之間有省略點
    top_h = 62 + lab_h + 16 + rows_h + pad
    sw_ = (w - 2 * pad - 60 * (len(steps) - 1)) / len(steps)
    box_h = max(c.lines(n["text"], sw_ - 44, 34) * 44.2 + (c.lines(n["sub"], sw_ - 44, 28) * 39.2 + 6 if n.get("sub") else 0) for n in steps) + 44
    bot_h = 62 + box_h + 12 + 50 + pad
    gap = 28
    total = top_h + gap + bot_h
    _fit(total, BOTTOM - y0, "ingest")
    extra = min(BOTTOM - y0 - total, 120)
    top_h += extra / 2; bot_h += extra / 2
    # ---- 上段
    c.rect(X0, y0, w, top_h, fill="none", stroke=TEAL, sw=3, rx=18)
    c.text(X0 + pad, y0 + 14, w - 2 * pad, heads[0], "dl", TEAL, "left")
    ly = y0 + 62
    for n, (x, cw) in zip(cols, cx):
        c.text(x, ly, cw, n["text"], "dl", DEEP, "left")
        if n.get("sub"):
            c.text(x, ly + c.lines(n["text"], cw, 28) * 39.2, cw, n["sub"], "ds", TEAL, "left")
    ry0 = ly + lab_h + 16 + (top_h - (62 + lab_h + 16 + rows_h + pad)) / 2
    ys = [ry0, ry0 + 58, ry0 + 58 * 2 + 30]
    for k in range(3):                                  # 原始片段（灰框）--> 事件（淺藍綠框），一對一
        y = ys[k]
        c.rect(cx[0][0], y, cx[0][1], 44, fill=DEEP, op=.12, rx=10)
        c.rect(cx[1][0], y, cx[1][1], 44, fill=LIGHT, op=.55, rx=10)
        c.line(cx[0][0] + cx[0][1] + 8, y + 22, cx[1][0] - 22, y + 22, TEAL, 3, dash="8 7")
        c.poly([(cx[1][0] - 8, y + 22), (cx[1][0] - 22, y + 14), (cx[1][0] - 22, y + 30)], fill=TEAL, closed=True)
    for x0_, cw_ in cx[:2]:                             # 省略點
        for i in (-1, 0, 1):
            c.circle(x0_ + cw_ / 2 + i * 16, ys[1] + 44 + 22, 4, fill=TEAL)
    ex = cx[2][0] + 40
    eys = [ry0 + 8 + i * (ys[2] + 36 - ry0 - 16) / 3 for i in range(4)]
    for ei, ni in INGEST_EDGES:                         # 事件 ↔ 實體，多對多
        c.line(cx[1][0] + cx[1][1], ys[ei] + 22, ex, eys[ni], DEEP, 3)
    for y in eys:
        c.circle(ex, y, 13, fill=GOLD, stroke=DEEP, sw=2)
    dbx, dbw = cx[3][0] + 30, 110                        # 存放處：資料庫圓柱
    dby, dbh = ry0 + 24, rows_h - 60
    c.arrow(ex + 30, (ry0 + ys[2] + 44) / 2, dbx - 14, (ry0 + ys[2] + 44) / 2, DEEP, 4, 16)
    c.rect(dbx, dby, dbw, dbh, fill=DEEP, rx=0)
    c.raw(f'<ellipse class="bg" cx="{dbx + dbw / 2:.1f}" cy="{dby + dbh:.1f}" rx="{dbw / 2:.1f}" ry="14" fill="{DEEP}"/>')
    c.raw(f'<ellipse class="bg" cx="{dbx + dbw / 2:.1f}" cy="{dby:.1f}" rx="{dbw / 2:.1f}" ry="14" fill="{TEAL}"/>')
    for k in (1, 2):
        c.raw(f'<path class="bg" d="M{dbx:.1f},{dby + dbh * k / 3:.1f} A{dbw / 2:.1f},14 0 0 0 {dbx + dbw:.1f},{dby + dbh * k / 3:.1f}" fill="none" stroke="{LIGHT}" stroke-width="3"/>')
    # ---- 下段
    by0 = y0 + top_h + gap
    c.rect(X0, by0, w, bot_h, fill=DEEP, rx=18)
    c.text(X0 + pad, by0 + 14, w - 2 * pad, heads[1], "dl", LIGHT, "left")
    sy = by0 + 62
    for k, n in enumerate(steps):
        x = X0 + pad + k * (sw_ + 60)
        last = k == len(steps) - 1
        c.textbox(x, sy, sw_, n["text"], n.get("sub"), fill=GOLD if last else CREAM, tcolor=DEEP, scolor=DEEP, h=box_h)
        if not last:
            c.arrow(x + sw_ + 8, sy + box_h / 2, x + sw_ + 52, sy + box_h / 2, CREAM, 5, 16)
    gx = X0 + pad + (len(steps) - 1) * (sw_ + 60)        # 最後一步下面：一個小的局部超圖（兩個事件靠一個共用實體串起來）
    gy = sy + box_h + 12 + 25
    c.rect(gx + 10, gy - 22, 90, 44, fill=LIGHT, rx=8)
    c.rect(gx + sw_ - 100, gy - 22, 90, 44, fill=LIGHT, rx=8)
    c.line(gx + 100, gy, gx + sw_ / 2 - 16, gy, GOLD, 6)
    c.line(gx + sw_ / 2 + 16, gy, gx + sw_ - 100, gy, GOLD, 6)
    c.circle(gx + sw_ / 2, gy, 16, fill=GOLD)
    return by0 + bot_h


# ------------------------------------------------------------------ roles（三列角色卡，每列一個圖示；2026-10-25，SAG 第 2 則）
def _icon(c: Canvas, kind: str, x: float, y: float, s: float) -> None:
    """在 (x, y) 起、邊長 s 的方塊裡畫圖示：db（資料庫圓柱）、vec（向量空間裡的幾個點）、llm（亮晶晶的大模型）。"""
    c.rect(x, y, s, s, fill=DEEP, rx=18)
    cx, cy = x + s / 2, y + s / 2
    if kind == "db":
        w, h = s * .5, s * .46
        c.rect(cx - w / 2, cy - h / 2 + 8, w, h - 8, fill=LIGHT, rx=0)
        c.raw(f'<ellipse class="bg" cx="{cx:.1f}" cy="{cy + h / 2:.1f}" rx="{w / 2:.1f}" ry="9" fill="{LIGHT}"/>'
              f'<ellipse class="bg" cx="{cx:.1f}" cy="{cy - h / 2 + 8:.1f}" rx="{w / 2:.1f}" ry="9" fill="{CREAM}"/>')
        for k in (1, 2):
            c.raw(f'<path class="bg" d="M{cx - w / 2:.1f},{cy - h / 2 + 8 + k * h / 3.2:.1f} q{w / 2:.1f},14 {w:.1f},0" fill="none" stroke="{DEEP}" stroke-width="3"/>')
    elif kind == "vec":
        for dx, dy, r, col in ((-30, 18, 8, LIGHT), (-8, 30, 7, LIGHT), (30, 26, 7, LIGHT), (-24, -26, 8, LIGHT), (24, -30, 7, LIGHT)):
            c.circle(cx + dx * s / 150, cy + dy * s / 150, r, fill=col, op=.5)
        pts = [(cx + 6 * s / 150, cy - 2), (cx + 30 * s / 150, cy - 14 * s / 150), (cx - 16 * s / 150, cy + 12 * s / 150)]
        c.line(*pts[0], *pts[1], CREAM, 3); c.line(*pts[0], *pts[2], CREAM, 3)
        c.circle(*pts[0], 13, fill=GOLD)
        c.circle(*pts[1], 9, fill=CREAM); c.circle(*pts[2], 9, fill=CREAM)
    else:
        for (dx, dy, r) in ((0, 0, 30), (34, -30, 13), (-34, 30, 10)):
            px, py, rr = cx + dx * s / 150, cy + dy * s / 150, r * s / 150 * 1.2
            c.poly([(px, py - rr * 1.5), (px + rr * .4, py - rr * .4), (px + rr * 1.5, py), (px + rr * .4, py + rr * .4),
                    (px, py + rr * 1.5), (px - rr * .4, py + rr * .4), (px - rr * 1.5, py), (px - rr * .4, py - rr * .4)], fill=GOLD, closed=True)


def roles(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 三列 [{text（元件名）, sub（它的角色，一個詞）, sub2（它做什麼）, icon: db／vec／llm}]；每列左邊一個圖示方塊，右邊三行字。"""
    nodes = spec["nodes"]
    w, ts, gap = X1 - X0, 150, 22
    tw = w - ts - 34
    hs = [max(ts, c.lines(n["text"], tw, 34) * 44.2 + 39.2 + c.lines(n["sub2"], tw, 28) * 39.2 + 26) for n in nodes]
    total = sum(hs) + gap * (len(nodes) - 1)
    _fit(total, BOTTOM - y0, "roles")
    extra = BOTTOM - y0 - total
    add = min(extra / len(nodes), 60)
    y = y0
    for n, h in zip(nodes, hs):
        h += add
        c.rect(X0, y, w, h, fill="none", stroke=DEEP, sw=3, rx=18)
        _icon(c, n.get("icon", "db"), X0 + 14, y + (h - ts + 28) / 2, ts - 28)
        th = c.lines(n["text"], tw, 34) * 44.2 + 39.2 + 14 + c.lines(n["sub2"], tw, 28) * 39.2
        ty = y + (h - th) / 2
        box = (X0, y, w, h)
        c.text(X0 + ts + 20, ty, tw, n["text"], "dn", DEEP, "left", box)
        c.text(X0 + ts + 20, ty + c.lines(n["text"], tw, 34) * 44.2 + 4, tw, n["sub"], "dl", TEAL, "left", box)
        c.text(X0 + ts + 20, ty + c.lines(n["text"], tw, 34) * 44.2 + 39.2 + 10, tw, n["sub2"], "ds", DEEP, "left", box)
        y += h + gap
    return y - gap


# ------------------------------------------------------------------ embed（精確比對 vs 向量空間）
def embed(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左標, 右標]；nodes = 左邊的比對列 [{text, sub?, ok: true／false}]（ok 畫勾，否則畫叉與虛線框）；
    outcomes = 右邊向量空間裡的 3 個點 [{text, sub?}]（第一個是中心點）；遠處的灰點只是陪襯，不帶文字。純示意。"""
    hl, hr = spec["heads"]
    rows, pts = spec["nodes"], spec["outcomes"]
    if len(pts) != 3:
        raise ValueError(f"embed 的 outcomes 要 3 個點，現在是 {len(pts)} 個")
    cw, gap, hh = 440, 40, 80
    xs = [X0, X0 + cw + gap]
    iw = cw - 44 - 56
    rh = [c.lines(r["text"], iw, 34) * 44.2 + (c.lines(r["sub"], iw, 28) * 39.2 + 6 if r.get("sub") else 0) + 44 for r in rows]
    lg = [c.lines(p["text"], cw - 100, 34) * 44.2 + (c.lines(p["sub"], cw - 100, 28) * 39.2 + 4 if p.get("sub") else 0) + 12 for p in pts]
    scat = 200
    left_h = sum(rh) + 16 * (len(rows) - 1)
    ph = max(left_h, scat + sum(lg) + 28)
    total = hh + 16 + ph
    _fit(total, BOTTOM - y0, "embed")
    ph += min(BOTTOM - y0 - total, 90)
    py = y0 + hh + 16
    for k, hd in enumerate((hl, hr)):
        c.rect(xs[k], y0, cw, hh, fill=DEEP if k == 0 else TEAL)
        c.text(xs[k] + 22, y0 + (hh - 44) / 2, cw - 44, hd, "dn", CREAM, "center", (xs[k], y0, cw, hh))
    add = (ph - left_h) / len(rows)
    y = py
    for r, h in zip(rows, rh):
        h += add
        ok = r.get("ok", True)
        c.rect(xs[0], y, cw, h, fill="none", stroke=DEEP, sw=3, dash=None if ok else "8 8", rx=14)
        ix, iy = xs[0] + 40, y + 40
        c.circle(ix, iy, 22, fill=GOLD if ok else CREAM, stroke=None if ok else DEEP, sw=4)
        if ok:
            c.poly([(ix - 10, iy), (ix - 3, iy + 8), (ix + 11, iy - 9)], stroke=DEEP, sw=5)
        else:
            c.line(ix - 9, iy - 9, ix + 9, iy + 9, DEEP, 5); c.line(ix - 9, iy + 9, ix + 9, iy - 9, DEEP, 5)
        th = c.lines(r["text"], iw, 34) * 44.2 + (c.lines(r["sub"], iw, 28) * 39.2 + 6 if r.get("sub") else 0)
        ty = y + (h - th) / 2
        c.text(xs[0] + 78, ty, iw, r["text"], "dn", DEEP if ok else TEAL, "left", (xs[0], y, cw, h))
        if r.get("sub"):
            c.text(xs[0] + 78, ty + c.lines(r["text"], iw, 34) * 44.2 + 6, iw, r["sub"], "ds", TEAL, "left", (xs[0], y, cw, h))
        y += h + 16
    c.rect(xs[1], py, cw, ph, fill="none", stroke=DEEP, sw=3, rx=14)
    cx, cy = xs[1] + cw / 2, py + scat / 2 + 6
    for dx, dy in ((-180, -66), (-150, 62), (-110, -20), (170, -62), (150, 72), (60, -80), (95, 82), (-30, 86), (-60, -82)):
        c.circle(cx + dx, cy + dy, 8, fill=LIGHT, op=.7)
    c.raw(f'<ellipse class="bg" cx="{cx:.1f}" cy="{cy:.1f}" rx="112" ry="70" fill="{GOLD}" fill-opacity=".28" stroke="{GOLD}" stroke-width="3" stroke-dasharray="8 7"/>')
    cols = (GOLD, TEAL, DEEP)
    for (dx, dy, r), col in zip(((0, 0, 16), (58, -24, 13), (-56, 26, 13)), cols):
        c.circle(cx + dx, cy + dy, r, fill=col, stroke=DEEP, sw=3)
    ly = py + scat + 4
    for p, h, col in zip(pts, lg, cols):
        c.circle(xs[1] + 34, ly + 22, 11, fill=col, stroke=DEEP, sw=2)
        c.text(xs[1] + 62, ly, cw - 80, p["text"], "dn", DEEP, "left", (xs[1], py, cw, ph))
        if p.get("sub"):
            c.text(xs[1] + 62, ly + c.lines(p["text"], cw - 100, 34) * 44.2 + 4, cw - 80, p["sub"], "ds", TEAL, "left", (xs[1], py, cw, ph))
        ly += h
    return py + ph


# ------------------------------------------------------------------ online（線上流程的路線圖：兩路進來、一路擴展、兩路決選）
def _loop_icon(c: Canvas, cx: float, cy: float, r: float, color: str) -> None:
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-50, 231, 10)]
    c.poly(pts, stroke=color, sw=6)
    a = math.radians(230)
    ex, ey = pts[-1]
    tx, ty = -math.sin(a), math.cos(a)                  # 順時針的切線方向
    nx, ny = -ty, tx
    c.poly([(ex + tx * 16, ey + ty * 16), (ex + nx * 11, ey + ny * 11), (ex - nx * 11, ey - ny * 11)], fill=color, closed=True)


def online(c: Canvas, spec: dict, y0: float) -> float:
    """SAG 論文圖二下半（線上檢索）的重畫（2026-10-25）：heads = [最上面的起點, 最下面的結果]；nodes = 第一步的兩條路 [{text, sub?}]；
    outcomes = [第二步（寬框）, 第三步左邊那路, 第三步右邊那路]，每個 {text, sub?}。箭頭由程式畫：起點→第一步兩路→第二步→左路；右路（直接檢索）不經過第二步，從起點沿右側繞下去（原圖如此，2026-10-25 重製圖審查者擋過）；兩路→結果。"""
    top, fin = spec["heads"]
    A, B = spec["nodes"]
    S2, L, R = spec["outcomes"]
    w = X1 - X0
    tw = (w - 30) / 2
    def bh(n, ww):
        return c.lines(n["text"], ww - 44, 34) * 44.2 + (c.lines(n["sub"], ww - 44, 28) * 39.2 + 6 if n.get("sub") else 0) + 36
    qh = 64
    fh = c.lines(fin, w - 44, 34) * 44.2 + 36
    h1, h3 = max(bh(A, tw), bh(B, tw)), max(bh(L, tw), bh(R, tw))
    s2w = w
    h2 = bh(S2, s2w + 44)
    ag = 38
    total = qh + h1 + h2 + h3 + fh + 4 * ag
    _fit(total, BOTTOM - y0, "online")
    extra = BOTTOM - y0 - total
    add = min(extra * .6 / 3, 40)
    h1, h2, h3 = h1 + add, h2 + add, h3 + add
    ag += min((extra - 3 * add) / 4, 22)
    cx = X0 + w / 2
    y = y0
    c.textbox(cx - 230, y, 460, top, fill=DEEP, tcolor=CREAM, align="center", h=qh); qy = y; y += qh + ag
    ax, bx = X0, X0 + tw + 30
    c.textbox(ax, y, tw, A["text"], A.get("sub"), fill=TEAL, scolor=CREAM, h=h1)
    c.textbox(bx, y, tw, B["text"], B.get("sub"), fill=TEAL, scolor=CREAM, h=h1)
    c.arrow(cx - 40, qy + qh + 3, ax + tw / 2 + 10, y - 4); c.arrow(cx + 40, qy + qh + 3, bx + tw / 2 - 10, y - 4)
    y1 = y; y += h1 + ag
    c.rect(X0, y, w, h2, fill=DEEP)
    c.text(X0 + 22, y + (h2 - (c.lines(S2["text"], s2w - 44, 34) * 44.2 + (c.lines(S2["sub"], s2w - 44, 28) * 39.2 + 6 if S2.get("sub") else 0))) / 2, s2w - 44, S2["text"], "dn", CREAM, "left", (X0, y, s2w, h2))
    if S2.get("sub"):
        c.text(X0 + 22, y + (h2 - (c.lines(S2["text"], s2w - 44, 34) * 44.2 + c.lines(S2["sub"], s2w - 44, 28) * 39.2 + 6)) / 2 + c.lines(S2["text"], s2w - 44, 34) * 44.2 + 6, s2w - 44, S2["sub"], "ds", LIGHT, "left", (X0, y, s2w, h2))
    c.arrow(ax + tw / 2, y1 + h1 + 3, ax + tw / 2, y - 4); c.arrow(bx + tw / 2, y1 + h1 + 3, bx + tw / 2, y - 4)
    y2 = y; y += h2 + ag
    c.textbox(ax, y, tw, L["text"], L.get("sub"), fill=TEAL, scolor=CREAM, h=h3)
    c.textbox(bx, y, tw, R["text"], R.get("sub"), fill=TEAL, scolor=CREAM, h=h3)
    c.arrow(ax + tw / 2, y2 + h2 + 3, ax + tw / 2, y - 4)      # 左路接在第二步後面；右路（直接檢索）不經過第二步，由起點繞過去（原圖：Query 直接走 Embedding Top-5）
    y3 = y; y += h3 + ag
    c.poly([(cx + 230 + 4, qy + qh / 2), (X1 + 34, qy + qh / 2), (X1 + 34, y3 + h3 / 2), (X1 + 8, y3 + h3 / 2)], stroke=TEAL, sw=4)
    c.poly([(X1 + 8, y3 + h3 / 2), (X1 + 22, y3 + h3 / 2 - 9), (X1 + 22, y3 + h3 / 2 + 9)], fill=TEAL, closed=True)
    c.textbox(X0, y, w, fin, fill=GOLD, tcolor=DEEP, align="center", h=fh)
    c.arrow(ax + tw / 2, y3 + h3 + 3, ax + tw / 2, y - 4); c.arrow(bx + tw / 2, y3 + h3 + 3, bx + tw / 2, y - 4)
    return y + fh


# ------------------------------------------------------------------ gate（水庫閘門：上游來多少，開度固定；兩道各一列）
def gate(c: Canvas, spec: dict, y0: float) -> float:
    """count = 閘門的名額（畫在每一道閘門上）；nodes = 兩列（兩道名額）[{text, sub?}]，每列：標題在上，下面左邊一池散落的點（上游，純示意、任意多）、
    中間閘門、右邊整齊排好的 count 個點（下游，點數 = 名額）。"""
    n = spec["count"]
    rows = spec["nodes"]
    if len(rows) != 2:
        raise ValueError(f"gate 的 nodes 要 2 列（兩道名額），現在是 {len(rows)} 列")
    w = X1 - X0
    def hh_(r):
        return c.lines(r["text"], w, 34) * 44.2 + (c.lines(r["sub"], w, 28) * 39.2 + 6 if r.get("sub") else 0)
    heads = [hh_(r) for r in rows]
    gapr = 26
    pmin = 130
    _fit(sum(heads) + 2 * 16 + 2 * pmin + gapr, BOTTOM - y0, "gate")
    ph = min(210, (BOTTOM - y0 - sum(heads) - 2 * 16 - gapr) / 2)
    y = y0
    seed = 7
    for k, r in enumerate(rows):
        c.text(X0, y, w, r["text"], "dn", DEEP, "left")
        if r.get("sub"):
            c.text(X0, y + c.lines(r["text"], w, 34) * 44.2 + 6, w, r["sub"], "ds", TEAL, "left")
        py = y + heads[k] + 16
        c.rect(X0, py, 400, ph, fill=LIGHT, stroke=TEAL, sw=3, rx=18, op=.30)
        for i in range(22):
            seed = (seed * 1103515245 + 12345) % 2147483648
            fx = (seed >> 8) % 1000 / 1000
            seed = (seed * 1103515245 + 12345) % 2147483648
            fy = (seed >> 8) % 1000 / 1000
            c.circle(X0 + 24 + fx * 352, py + 22 + fy * (ph - 44), 9, fill=MID)
        gx, gw, gap = X0 + 400, 110, 56
        gy = py + ph / 2 - gap / 2
        c.rect(gx, py, gw, gy - py, fill=DEEP, rx=0)
        c.rect(gx, gy + gap, gw, py + ph - gy - gap, fill=DEEP, rx=0)
        pt = py + (gy - py) / 2
        c.rect(gx + 6, pt - 34, gw - 12, 68, fill=GOLD, rx=4)
        c.text(gx + 26, pt - 24, gw - 52, f"{n}", "dv2", DEEP, "center", (gx + 6, pt - 34, gw - 12, 68))
        rx_ = X0 + 540
        c.arrow(X0 + 330, gy + gap / 2, rx_ + 40, gy + gap / 2, GOLD, 8, 22)
        c.rect(rx_, py, X1 - rx_, ph, fill="none", stroke=DEEP, sw=3, rx=18)
        cols = 10                                     # 右邊畫的點數 = 名額（50 就是 50 個），整齊排好
        nr = math.ceil(n / cols)
        pitch = min(38, (X1 - rx_ - 50) / cols, (ph - 36) / nr)
        sx = rx_ + (X1 - rx_ - (cols - 1) * pitch) / 2
        sy = py + ph / 2 - (nr - 1) * pitch / 2
        for q in range(n):
            c.circle(sx + (q % cols) * pitch, sy + (q // cols) * pitch, pitch * .36, fill=GOLD, stroke=DEEP, sw=2)
        y = py + ph + gapr
    return y - gapr


# ------------------------------------------------------------------ concat（兩路各一排，匯成一排）
def _chunk(c: Canvas, x: float, y: float, w: float, h: float, col: str) -> None:
    c.rect(x, y, w, h, fill=CREAM, stroke=col, sw=4, rx=8)
    for k in range(3):
        c.rect(x + 10, y + 14 + k * 20, w - 20 - (k == 2) * 16, 7, fill=col, op=.55, rx=3)


def concat(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左路標籤, 右路標籤]；nodes = [{text}（上方一句話，說兩路各挑幾個）, {text, sub?}（匯整後的結果）]。
    每路畫 5 個小文件，匯整後畫 10 個（只表示合成一份，不分來源）；純示意。"""
    hl, hr = spec["heads"]
    top, res = spec["nodes"]
    w = X1 - X0
    th = c.lines(top["text"], w, 34) * 44.2
    rh = c.lines(res["text"], w, 34) * 44.2 + (c.lines(res["sub"], w, 28) * 39.2 + 6 if res.get("sub") else 0)
    cw_, ch_, g_ = 62, 82, 14
    rowW = 5 * cw_ + 4 * g_
    total = th + 14 + 50 + ch_ + 90 + ch_ + 40 + rh
    _fit(total, BOTTOM - y0, "concat")
    extra = BOTTOM - y0 - total
    ag = 90 + min(extra * .5, 50)
    c.text(X0, y0, w, top["text"], "dn", DEEP, "left")
    ly = y0 + th + 14
    lx, rx_ = X0 + 60, X1 - 60 - rowW
    for x, hd, col in ((lx, hl, TEAL), (rx_, hr, DEEP)):
        c.text(x, ly, rowW, hd, "dl", col, "center")
        for i in range(5):
            _chunk(c, x + i * (cw_ + g_), ly + 54, cw_, ch_, col)
    mid = X0 + w / 2
    sy = ly + 54 + ch_
    shy = sy + ag
    sw_ = 10 * cw_ + 9 * g_ - 90
    c.arrow(lx + rowW / 2, sy + 8, mid - 60, shy - 8, TEAL, 5, 16)
    c.arrow(rx_ + rowW / 2, sy + 8, mid + 60, shy - 8, DEEP, 5, 16)
    shelfW = min(w, 10 * cw_ + 9 * g_ + 60)
    c.rect(mid - shelfW / 2, shy, shelfW, ch_ + 40, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=16)
    x0_ = mid - (10 * cw_ + 9 * g_) / 2
    for i in range(10):
        _chunk(c, x0_ + i * (cw_ + g_), shy + 20, cw_, ch_, DEEP)
    ry = shy + ch_ + 40 + 22
    c.text(X0, ry, w, res["text"], "dn", DEEP, "center")
    if res.get("sub"):
        c.text(X0, ry + c.lines(res["text"], w, 34) * 44.2 + 6, w, res["sub"], "ds", TEAL, "center")
    return ry + rh


# ------------------------------------------------------------------ joint（逐一打分 vs 一起評估）
def joint(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左標, 右標]；nodes = [{text（一句話）, sub（例子）, sub2（結論）}, {…}]。左邊三個小方塊之間各斷一條線、畫叉（各自獨立），
    右邊三個小方塊用金色接起來、外面括一個大括號（一起看）；純示意，方塊不帶文字。"""
    hl, hr = spec["heads"]
    nodes = spec["nodes"]
    cw, gap, hh = 440, 40, 80
    xs = [X0, X0 + cw + gap]
    iw = cw - 44
    def blk(n):
        return (c.lines(n["text"], iw, 34) * 44.2, c.lines(n["sub2"], iw, 34) * 44.2, c.lines(n["sub"], iw, 28) * 39.2)
    hs = [sum(blk(n)) for n in nodes]
    pic = 3 * 52 + 2 * 14 + 46
    total = hh + 16 + max(hs) + pic + 3 * 18 + 24
    _fit(total, BOTTOM - y0, "joint")
    pic += min(BOTTOM - y0 - total, 80)
    ph = max(hs) + pic + 3 * 18 + 24
    for k, (hd, n) in enumerate(zip((hl, hr), nodes)):
        x = xs[k]
        c.rect(x, y0, cw, hh, fill=DEEP if k == 0 else TEAL)
        c.text(x + 22, y0 + (hh - 44) / 2, cw - 44, hd, "dn", CREAM, "center", (x, y0, cw, hh))
        py = y0 + hh + 16
        c.rect(x, py, cw, ph, fill="none", stroke=DEEP, sw=3, rx=14, dash="8 8" if k == 0 else None)
        t1, t2, t3 = blk(n)
        y = py + 18
        c.text(x + 22, y, iw, n["text"], "dn", DEEP, "left", (x, py, cw, ph)); y += t1 + 6
        top = y + 8
        pitch = (pic - 36) / 2.7
        chip_h = min(52, pitch * .74)
        for i in range(3):
            cy_ = top + i * pitch
            if k == 0:
                c.rect(x + 40, cy_, 280, chip_h, fill=CREAM, stroke=DEEP, sw=3, rx=10)
                if i:      # 方塊之間沒有連結：虛線斷在中間，畫一個叉
                    my = cy_ - (pitch - chip_h) / 2
                    c.line(x + 172, my - 5, x + 188, my + 5, TEAL, 4); c.line(x + 172, my + 5, x + 188, my - 5, TEAL, 4)
            else:
                c.rect(x + 40, cy_, 280, chip_h, fill=GOLD, stroke=DEEP, sw=3, rx=10, op=.35)
                if i:
                    c.rect(x + 170, cy_ - (pitch - chip_h), 20, pitch - chip_h, fill=GOLD, rx=4)
        if k == 1:
            by0, by1 = top - 4, top + 2 * pitch + chip_h + 4
            c.poly([(x + 340, by0), (x + 366, by0 + 10), (x + 366, (by0 + by1) / 2 - 12), (x + 386, (by0 + by1) / 2), (x + 366, (by0 + by1) / 2 + 12), (x + 366, by1 - 10), (x + 340, by1)], stroke=GOLD, sw=7)
        for q in range(3):      # 方塊不只三個：下面三個小點
            c.circle(x + 180 + (q - 1) * 22, top + 2 * pitch + chip_h + 18, 5, fill=TEAL)
        y = top + 2 * pitch + chip_h + 34
        c.text(x + 22, y, iw, n["sub2"], "dn", DEEP if k else TEAL, "left", (x, py, cw, ph)); y += t2 + 6
        c.text(x + 22, y, iw, n["sub"], "ds", TEAL, "left", (x, py, cw, ph))
    return y0 + hh + 16 + ph


# ------------------------------------------------------------------ rails（兩條軌道各撈一排，合併成一排；A 漏掉的一格由 B 補上）
def rails(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [A 路標籤, B 路標籤]；nodes = [{text, sub?}（A 的做法）, {text, sub?}（B 的做法）]；outcomes[0] = {text, sub?}（合併後的結果）。
    每條軌道右邊畫 6 個格子：A 在第 4 格漏接（虛線空格），B 補上那一格（金色）；合併後 6 格都有。純示意，格子不帶文字。"""
    hl, hr = spec["heads"]
    A, B = spec["nodes"]
    res = spec["outcomes"][0]
    w = X1 - X0
    tw, cw_, ch_, g_ = 390, 58, 66, 12
    rowW = 6 * cw_ + 5 * g_
    cx0 = X1 - 24 - rowW
    def lane_h(n):
        return 18 + 45 + c.lines(n["text"], tw, 34) * 44.2 + (c.lines(n["sub"], tw, 28) * 39.2 + 6 if n.get("sub") else 0) + 18
    lh = max(lane_h(A), lane_h(B), ch_ + 60)
    rh = max(ch_ + 36, c.lines(res["text"], w - 44, 34) * 44.2 + 40)
    ag = 44
    gap = 18
    total = 2 * lh + gap + ag + rh
    _fit(total, BOTTOM - y0, "rails")
    extra = BOTTOM - y0 - total
    lh += min(extra * .5 / 2, 30)
    ag += min(extra * .5, 30)
    miss = 3
    y = y0
    lane_y = []
    for k, (hd, n, col, filled) in enumerate(((hl, A, DEEP, [0, 1, 2, 4, 5]), (hr, B, TEAL, [1, 3, 5]))):
        c.rect(X0, y, w, lh, fill="none", stroke=col, sw=3, rx=18)
        c.text(X0 + 22, y + 12, tw, hd, "dl", col, "left", (X0, y, w, lh))
        ty = y + 12 + 45
        c.text(X0 + 22, ty, tw, n["text"], "dn", DEEP, "left", (X0, y, w, lh))
        if n.get("sub"):
            c.text(X0 + 22, ty + c.lines(n["text"], tw, 34) * 44.2 + 6, tw, n["sub"], "ds", TEAL, "left", (X0, y, w, lh))
        cy = y + (lh - ch_) / 2
        for i in range(6):
            x = cx0 + i * (cw_ + g_)
            if i in filled:
                if k == 1 and i == miss:
                    c.rect(x, cy, cw_, ch_, fill=GOLD, stroke=DEEP, sw=4, rx=8)
                else:
                    _chunk(c, x, cy, cw_, ch_, col)
            elif k == 0 and i == miss:
                c.rect(x, cy, cw_, ch_, fill="none", stroke=TEAL, sw=4, rx=8, dash="7 7")
        lane_y.append(y)
        y += lh + gap
    y += ag - gap
    c.rect(X0, y, w, rh, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=18)
    rcy = y + (rh - ch_) / 2
    for i in range(6):
        x = cx0 + i * (cw_ + g_)
        if i == miss:
            c.rect(x, rcy, cw_, ch_, fill=GOLD, stroke=DEEP, sw=4, rx=8)
        else:
            _chunk(c, x, rcy, cw_, ch_, DEEP)
    th = c.lines(res["text"], tw, 34) * 44.2
    c.text(X0 + 22, y + (rh - th) / 2, tw, res["text"], "dn", DEEP, "left", (X0, y, w, rh))
    mx = cx0 + 3 * (cw_ + g_) + cw_ / 2                  # 補上的那一格往下接到合併後的同一格
    c.arrow(mx, lane_y[1] + lh + 4, mx, y - 6, GOLD, 6, 18)
    return y + rh


# ------------------------------------------------------------------ scoreboard（戰績表：資料集 × 欄，每格兩條橫條）
def scoreboard(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 每列一個資料集 [{text, sub?, emph?}]；heads = 兩個欄標籤；outcomes = 圖例 [{text（深色）}, {text（淺色）}]；
    cells[列][欄] = [深色值, 淺色值]（字串）。每格兩條橫條，軸從 0 起（axis_max 預設 100），長度與數值成正比；深色值小於淺色值的格子畫虛線框。"""
    rows, heads, leg, cells = spec["nodes"], spec["heads"], spec["outcomes"], spec["cells"]
    amax = float(spec.get("axis_max", 100))
    if len(cells) != len(rows) or any(len(r_) != len(heads) for r_ in cells):
        raise ValueError(f"scoreboard 的 cells 要 {len(rows)} 列 × {len(heads)} 欄")
    if len(leg) != 2:
        raise ValueError("scoreboard 的 outcomes 要 2 個（圖例：深色、淺色）")
    w = X1 - X0
    lw = 340
    cw = (w - lw) / len(heads)
    bh_, bg_, pad = 44, 14, 18
    head_h = 56
    gap = 14
    need_text = [c.lines(n["text"], lw - 28, 34) * 44.2 + (c.lines(n["sub"], lw - 28, 28) * 39.2 + 6 if n.get("sub") else 0) + 2 * pad for n in rows]
    rh = [max(2 * bh_ + bg_ + 2 * pad, t) for t in need_text]
    total = head_h + 10 + sum(rh) + gap * (len(rows) - 1)
    _fit(total, BOTTOM - y0, "scoreboard")
    add = min((BOTTOM - y0 - total) / len(rows), 40)
    rh = [h + add for h in rh]
    # 圖例（左上）與欄標籤
    lx = X0
    for col, n in zip((DEEP, LIGHT), leg):
        c.rect(lx, y0 + 14, 26, 26, fill=col, rx=5)
        c.text(lx + 36, y0 + 8, 200, n["text"], "dl", DEEP, "left")
        lx += 36 + (len(n["text"]) * 17 + 20)
    for j, hd in enumerate(heads):
        c.text(X0 + lw + j * cw, y0 + 8, cw, hd, "dl", TEAL, "center")
    y = y0 + head_h + 10
    barmax = cw - 2 * 18 - 84
    for i, (n, h) in enumerate(zip(rows, rh)):
        if n.get("emph"):
            c.rect(X0 - 12, y - 8, w + 24, h + 16, fill=GOLD, op=.22, rx=18)
        box = (X0, y, lw, h)
        th = c.lines(n["text"], lw - 28, 34) * 44.2 + (c.lines(n["sub"], lw - 28, 28) * 39.2 + 6 if n.get("sub") else 0)
        ty = y + (h - th) / 2
        c.text(X0 + 6, ty, lw - 28, n["text"], "dn", DEEP, "left", box)
        if n.get("sub"):
            c.text(X0 + 6, ty + c.lines(n["text"], lw - 28, 34) * 44.2 + 6, lw - 28, n["sub"], "ds", DEEP if n.get("emph") else TEAL, "left", box)
        for j in range(len(heads)):
            a, b = cells[i][j]
            cx = X0 + lw + j * cw + 8
            lose = float(a) < float(b)
            c.rect(cx, y, cw - 16, h, fill="none", stroke=DEEP, sw=3, rx=14, dash="9 8" if lose else None, op=None)
            by = y + (h - (2 * bh_ + bg_)) / 2
            for k, (val, col, tc) in enumerate(((a, DEEP, DEEP), (b, LIGHT, TEAL))):
                L = float(val) / amax * barmax
                yy = by + k * (bh_ + bg_)
                c.rect(cx + 14, yy, L, bh_, fill=col, rx=6)
                c.text(cx + 14 + L + 10, yy + (bh_ - 28 * 1.4) / 2, 84, val, "dl", DEEP if n.get("emph") else tc, "left")
        y += h + gap
    return y - gap


# ------------------------------------------------------------------ leak（每一跳都漏一些）
def leak(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 兩條路 [{text, sub?}（走很多跳的）, {text, sub?}（一次到位的）]；heads = 箭頭上的標籤（例：剪枝，兩條路共用）。
    兩條路從同一個起點走到同一個終點：第一條分 3 跳（4 格），第二條一跳（2 格）。每一格是 2 × 5 個點，實心＝留下、虛線空點＝漏掉；點數是固定示意。"""
    A, B = spec["nodes"]
    lab = spec["heads"][0]
    w = X1 - X0
    cols, rows_, pitch, rr = 2, 5, 30, 11
    binw, binh = cols * pitch + 18, rows_ * pitch + 18
    def th(n):
        return c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0)
    lane = lambda n: th(n) + 14 + binh + 12
    total = lane(A) + lane(B) + 30
    _fit(total, BOTTOM - y0, "leak")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    y = y0
    xs_a = [X0 + i * ((w - binw) / 3) for i in range(4)]
    xs_b = [X0, X0 + w - binw]
    plans = ((A, xs_a, [10, 8, 6, 5], TEAL, False), (B, xs_b, [10, 9], DEEP, True))
    for n, xs, keep, col, win in plans:
        c.text(X0, y, w, n["text"], "dn", DEEP, "left")
        if n.get("sub"):
            c.text(X0, y + c.lines(n["text"], w, 34) * 44.2 + 4, w, n["sub"], "ds", TEAL, "left")
        by = y + th(n) + 14 + extra / 2
        for k, (x, kp) in enumerate(zip(xs, keep)):
            last = k == len(xs) - 1
            c.rect(x, by, binw, binh, fill=GOLD if (win and last) else "none", stroke=col, sw=3, rx=10, op=.25 if (win and last) else None)
            for q in range(cols * rows_):
                px, py = x + 9 + pitch / 2 + (q % cols) * pitch, by + 9 + pitch / 2 + (q // cols) * pitch
                if q < kp:
                    c.circle(px, py, rr, fill=col)
                else:
                    c.circle(px, py, rr, fill="none", stroke=col, sw=2, dash="4 4")
            if k:
                x0_, x1_ = xs[k - 1] + binw + 10, x - 10
                c.arrow(x0_, by + binh / 2, x1_, by + binh / 2, col, 5, 18)
                c.text((x0_ + x1_) / 2 - 60, by + binh / 2 - 46, 120, lab, "ds", col, "center")
        y = by + binh + 12 + extra / 2 + 30
    return y - 30


# ------------------------------------------------------------------ amplify（誤差沿路放大 vs 精確比對）
def amplify(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 兩條路 [{text, sub?}, {text, sub?}]；heads = 第一條兩端的標籤 [起點, 終點]；outcomes[0] = 第二條帶子的標籤。
    第一條畫成越來越寬的楔形（誤差越傳越大），第二條是等寬的金色帶（精確比對）；沿路四個站；純示意。"""
    A, B = spec["nodes"]
    h0, h1 = spec["heads"]
    lb = spec["outcomes"][0]["text"]
    w = X1 - X0
    th = lambda n: c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0)
    band, lab_h = 170, 44
    total = th(A) + band + lab_h + 30 + th(B) + 120 + lab_h
    _fit(total, BOTTOM - y0, "amplify")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    stations = [X0 + 30 + i * ((w - 60) / 3) for i in range(4)]
    # 第一條：楔形
    y = y0
    c.text(X0, y, w, A["text"], "dn", DEEP, "left")
    if A.get("sub"):
        c.text(X0, y + c.lines(A["text"], w, 34) * 44.2 + 4, w, A["sub"], "ds", TEAL, "left")
    cy = y + th(A) + 14 + band / 2 + extra / 2
    c.poly([(X0 + 30, cy - 8), (X1 - 10, cy - band / 2), (X1 - 10, cy + band / 2), (X0 + 30, cy + 8)], fill=TEAL, closed=True, op=.30)
    c.line(X0 + 30, cy, X1 - 10, cy, DEEP, 5)
    for i, x in enumerate(stations):
        c.circle(x, cy, 16, fill=DEEP)
    ly = cy + band / 2 + 8
    c.text(X0, ly, 400, h0, "ds", TEAL, "left")
    c.text(X1 - 400, ly, 400, h1, "ds", DEEP, "right")
    # 第二條：等寬帶
    y2 = ly + lab_h + 30 + extra / 2
    c.text(X0, y2, w, B["text"], "dn", DEEP, "left")
    if B.get("sub"):
        c.text(X0, y2 + c.lines(B["text"], w, 34) * 44.2 + 4, w, B["sub"], "ds", TEAL, "left")
    cy2 = y2 + th(B) + 14 + 40
    c.rect(X0 + 30, cy2 - 20, w - 40, 40, fill=GOLD, op=.55, stroke=GOLD, sw=3, rx=8)
    for x in stations:
        c.circle(x, cy2, 16, fill=DEEP)
        c.line(x - 7, cy2 - 4, x + 7, cy2 - 4, CREAM, 3); c.line(x - 7, cy2 + 4, x + 7, cy2 + 4, CREAM, 3)     # 等號：精確相等才連上
    c.text(X0, cy2 + 40, w, lb, "ds", DEEP, "left")
    return cy2 + 40 + 39.2


# ------------------------------------------------------------------ 2026-10-27（SAG 第 4 則）：receipt／squeeze／alias／handoff／mismatch／ledger
def _th(c: Canvas, n: dict, w: float) -> float:
    """一個 {text, sub?} 在寬 w 內的文字高度（text 34 px、sub 28 px）。"""
    return c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0)


def _cross(c: Canvas, x: float, y: float, r: float, color: str = DEEP, sw: int = 5) -> None:
    c.line(x - r, y - r, x + r, y + r, color, sw)
    c.line(x - r, y + r, x + r, y - r, color, sw)


def receipt(c: Canvas, spec: dict, y0: float) -> float:
    """帳單（SAG 第 4 則「付的帳」）：heads = [抬頭, 「換來的」標籤]；nodes = 品項 2～4 個 [{text, sub?}]（每項前面自動編號）；
    outcomes = 換來的東西 1～3 個 [{text}]（畫成金色小標籤）。一張米色紙，下緣鋸齒；純示意。"""
    head, got = spec["heads"]
    items, gains = spec["nodes"], spec["outcomes"]
    if not 2 <= len(items) <= 4 or not 1 <= len(gains) <= 3:
        raise ValueError(f"receipt 的 nodes 要 2～4 個品項、outcomes 要 1～3 個，現在是 {len(items)}、{len(gains)}")
    w = X1 - X0
    px, pw = X0 + 20, w - 40                             # 紙比版心窄一點
    tw = pw - 150
    rows = [max(_th(c, n, tw) + 26, 76) for n in items]
    gain_h = 60
    total = 84 + sum(rows) + 8 * (len(rows) - 1) + 34 + 50 + gain_h + 56
    _fit(total, BOTTOM - y0, "receipt")
    add = min((BOTTOM - y0 - total) / len(items), 30)
    rows = [r + add for r in rows]
    total += add * len(items)
    zig = []
    bot = y0 + total
    steps = 24
    for i in range(steps + 1):
        zig.append((px + i * pw / steps, bot if i % 2 == 0 else bot - 16))
    c.poly([(px, y0), (px + pw, y0)] + zig[::-1], fill=GOLD, closed=True, op=.14)
    c.poly([(px, bot), (px, y0), (px + pw, y0), (px + pw, bot)], stroke=DEEP, sw=3)
    c.poly(zig, stroke=DEEP, sw=3)
    c.text(px + 28, y0 + 14, pw - 56, head, "dl", TEAL, "left")
    c.line(px + 28, y0 + 70, px + pw - 28, y0 + 70, DEEP, 3, dash="3 9")
    y = y0 + 86
    for k, (n, h) in enumerate(zip(items, rows), 1):
        c.circle(px + 64, y + h / 2, 28, fill=DEEP)
        c.text(px + 64 - 25, y + h / 2 - 19, 50, str(k), "dl", CREAM, "center")
        ty = y + (h - _th(c, n, tw)) / 2
        c.text(px + 120, ty, tw, n["text"], "dn", DEEP, "left")
        if n.get("sub"):
            c.text(px + 120, ty + c.lines(n["text"], tw, 34) * 44.2 + 6, tw, n["sub"], "ds", TEAL, "left")
        y += h + 8
    y += 4
    c.line(px + 28, y, px + pw - 28, y, DEEP, 3, dash="3 9")
    y += 18
    c.text(px + 28, y, 220, got, "dl", TEAL, "left")
    y += 50
    gw = (pw - 56 - 16 * (len(gains) - 1)) / len(gains)
    for k, g in enumerate(gains):
        x = px + 28 + k * (gw + 16)
        c.rect(x, y, gw, gain_h, fill=GOLD, rx=14)
        c.text(x + 10, y + (gain_h - 44.2) / 2, gw - 20, g["text"], "dn", DEEP, "center", (x, y, gw, gain_h))
    return bot


def squeeze(c: Canvas, spec: dict, y0: float) -> float:
    """名額線擠掉了誰（SAG 第 4 則：50 個名額擠掉罕見的橋樑實體）：
    heads = [排隊的左端標籤, 右端標籤, 名額線標籤]；nodes = [{text, sub?}（上方說明）, {text, sub?}（金點：被擠出去的那個）]；
    outcomes = 底下一條推理鏈的兩端 [{text}（起點）, {text}（終點）]，中間是金色的橋樑點，過了橋就斷（虛線打叉）。
    排隊的點是固定示意（不是實際數量），圖註要標「示意」。"""
    hl, hr, hcut = spec["heads"]
    top, bridge = spec["nodes"]
    a, b = spec["outcomes"]
    w = X1 - X0
    cols, rows_, pitch = 20, 3, 40
    keep = 12                                            # 前 12 欄留下，其餘被擠出去
    boxw, boxh = cols * pitch + 40, rows_ * pitch + 40
    th_top = _th(c, top, w)
    bh = _th(c, bridge, 560)
    chain_h = 40
    total = th_top + 14 + 54 + boxh + 18 + 44 + bh + 40 + chain_h + 34 + 39.2
    _fit(total, BOTTOM - y0, "squeeze")
    extra = min((BOTTOM - y0 - total) / 3, 40)
    y = y0
    c.text(X0, y, w, top["text"], "dn", DEEP, "left")
    if top.get("sub"):
        c.text(X0, y + c.lines(top["text"], w, 34) * 44.2 + 4, w, top["sub"], "ds", TEAL, "left")
    y += th_top + 14 + extra
    c.text(X0, y, 400, hl, "dl", TEAL, "left")
    c.text(X1 - 400, y, 400, hr, "dl", TEAL, "right")
    by = y + 54
    bx = X0 + (w - boxw) / 2
    c.rect(bx, by, boxw, boxh, fill="none", stroke=DEEP, sw=3, rx=18)
    cutx = bx + 20 + keep * pitch
    c.rect(bx + 6, by + 6, cutx - bx - 6 - pitch / 2 + 20, boxh - 12, fill=MID, rx=12, op=.14)
    for r in range(rows_):
        for k in range(cols):
            px, py = bx + 20 + pitch / 2 + k * pitch, by + 20 + pitch / 2 + r * pitch
            if k < keep:
                c.circle(px, py, 14, fill=MID)
            elif (r, k) == (2, 16):
                c.circle(px, py, 19, fill=GOLD, stroke=DEEP, sw=4)
            else:
                c.circle(px, py, 13, fill="none", stroke=TEAL, sw=2, dash="4 4")
    c.line(cutx, by - 14, cutx, by + boxh + 14, GOLD, 6, dash="12 8")
    c.text(cutx - 200, by + boxh + 18, 400, hcut, "dl", DEEP, "center")
    gx = bx + 20 + pitch / 2 + 16 * pitch
    gy = by + 20 + pitch / 2 + 2 * pitch
    ly = by + boxh + 18 + 44 + extra
    c.line(gx, gy + 22, gx, ly - 6, GOLD, 4)
    bw = 560
    bxl = min(max(gx - bw / 2, X0), X1 - bw)
    c.text(bxl, ly, bw, bridge["text"], "dn", DEEP, "center")
    if bridge.get("sub"):
        c.text(bxl, ly + c.lines(bridge["text"], bw, 34) * 44.2 + 4, bw, bridge["sub"], "ds", TEAL, "center")
    cy = ly + bh + 40 + chain_h / 2 + extra
    x1_, xm, x2_ = X0 + 40, X0 + 40 + w * .42, X1 - 40
    c.circle(x1_, cy, 20, fill=DEEP)
    c.circle(x2_, cy, 20, fill=DEEP)
    c.arrow(x1_ + 28, cy, xm - 28, cy, DEEP, 6, 18)
    c.circle(xm, cy, 24, fill=GOLD, stroke=DEEP, sw=4)
    c.line(xm + 30, cy, x2_ - 30, cy, TEAL, 5, dash="10 9")
    _cross(c, (xm + x2_) / 2, cy, 15, DEEP, 6)
    c.text(x1_ - 40, cy + 34, 220, a["text"], "ds", DEEP, "left")
    c.text(x2_ - 220 + 40, cy + 34, 220, b["text"], "ds", DEEP, "right")
    return cy + 34 + 39.2


def alias(c: Canvas, spec: dict, y0: float) -> float:
    """別名對齊：傳統做法合併、SAG 不合併（SAG 第 4 則）。heads = [上段標籤, 下段標籤]；
    outcomes = 同一個東西的 3 種寫法 [{text}]（上下兩段都畫）；nodes = [{text, sub?}（上段：合併後的那一個）, {text, sub?}（下段的說明）]。純示意。"""
    h1, h2 = spec["heads"]
    chips = spec["outcomes"]
    merged, plain = spec["nodes"]
    if len(chips) != 3:
        raise ValueError(f"alias 的 outcomes 要 3 種寫法，現在是 {len(chips)} 個")
    w = X1 - X0
    gap = 44
    cw = (w - 2 * gap) / 3
    chh = 64
    mh = _th(c, merged, w - 120) + 36
    ph = _th(c, plain, w)
    total = 44 + chh + 60 + mh + 40 + 44 + chh + 16 + ph
    _fit(total, BOTTOM - y0, "alias")
    extra = min((BOTTOM - y0 - total) / 3, 40)
    y = y0
    c.text(X0, y, w, h1, "dl", TEAL, "left")
    cy_ = y + 44
    cxs = [X0 + k * (cw + gap) + cw / 2 for k in range(3)]
    for k, ch in enumerate(chips):
        c.rect(cxs[k] - cw / 2, cy_, cw, chh, fill=DEEP, rx=14)
        c.text(cxs[k] - cw / 2 + 12, cy_ + (chh - 39.2) / 2, cw - 24, ch["text"], "ds", CREAM, "center", (cxs[k] - cw / 2, cy_, cw, chh))
    my = cy_ + chh + 60 + extra
    mx, mw = X0 + 60, w - 120
    for k in range(3):
        c.arrow(cxs[k], cy_ + chh + 4, X0 + w / 2 + (k - 1) * 150, my - 6, GOLD, 5, 16)
    c.rect(mx, my, mw, mh, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=18)
    mt = _th(c, merged, mw - 40)
    c.text(mx + 20, my + (mh - mt) / 2, mw - 40, merged["text"], "dn", DEEP, "center", (mx, my, mw, mh))
    if merged.get("sub"):
        c.text(mx + 20, my + (mh - mt) / 2 + c.lines(merged["text"], mw - 40, 34) * 44.2 + 6, mw - 40, merged["sub"], "ds", DEEP, "center", (mx, my, mw, mh))
    y = my + mh + 40 + extra
    c.line(X0, y - 18, X1, y - 18, TEAL, 2, dash="3 9")
    c.text(X0, y, w, h2, "dl", TEAL, "left")
    cy2 = y + 44
    for k, ch in enumerate(chips):
        c.rect(cxs[k] - cw / 2, cy2, cw, chh, fill="none", stroke=DEEP, sw=3, rx=14)
        c.text(cxs[k] - cw / 2 + 12, cy2 + (chh - 39.2) / 2, cw - 24, ch["text"], "ds", DEEP, "center", (cxs[k] - cw / 2, cy2, cw, chh))
    ty = cy2 + chh + 16
    c.text(X0, ty, w, plain["text"], "dn", DEEP, "left")
    if plain.get("sub"):
        c.text(X0, ty + c.lines(plain["text"], w, 34) * 44.2 + 4, w, plain["sub"], "ds", TEAL, "left")
    return ty + ph


def handoff(c: Canvas, spec: dict, y0: float) -> float:
    """把工作從線下搬到線上（SAG 第 4 則：別名對齊的壓力推遲到線上）。heads = [上帶標籤, 下帶標籤, 箭頭標籤]；
    nodes = [{text, sub?}（被搬走、線下不做的事）, {text, sub?}（線上接手的做法）]；outcomes[0] = {text}（線下因此得到的好處，金色）。純示意。"""
    ht, hb, ha = spec["heads"]
    gone, took = spec["nodes"]
    gain = spec["outcomes"][0]
    w = X1 - X0
    bw = 420
    top_h = max(_th(c, gone, bw - 40) + 40, c.lines(gain["text"], w - bw - 140, 34) * 44.2 + 40) + 66
    bot_h = _th(c, took, w - 84) + 40 + 66
    gap = 70
    total = top_h + gap + bot_h
    _fit(total, BOTTOM - y0, "handoff")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    top_h += extra * .5; bot_h += extra * .5; gap += extra * .0
    y = y0
    c.rect(X0, y, w, top_h, fill="none", stroke=DEEP, sw=3, rx=18)
    c.text(X0 + 22, y + 12, w - 44, ht, "dl", TEAL, "left")
    ih = top_h - 66 - 12
    iy = y + 66
    c.rect(X0 + 22, iy, bw, ih, fill="none", stroke=DEEP, sw=4, rx=14, dash="10 8")
    gt = _th(c, gone, bw - 40)
    c.text(X0 + 42, iy + (ih - gt) / 2, bw - 40, gone["text"], "dn", TEAL, "left", (X0 + 22, iy, bw, ih))
    if gone.get("sub"):
        c.text(X0 + 42, iy + (ih - gt) / 2 + c.lines(gone["text"], bw - 40, 34) * 44.2 + 6, bw - 40, gone["sub"], "ds", TEAL, "left", (X0 + 22, iy, bw, ih))
    _cross(c, X0 + 22 + bw - 30, iy + 30, 14, DEEP, 5)
    gx = X0 + 22 + bw + 50
    gw = X1 - 22 - gx
    c.rect(gx, iy, gw, ih, fill=GOLD, rx=14)
    c.text(gx + 20, iy + (ih - c.lines(gain["text"], gw - 40, 34) * 44.2) / 2, gw - 40, gain["text"], "dn", DEEP, "left", (gx, iy, gw, ih))
    y += top_h
    c.arrow(X0 + 22 + bw / 2, y - 6, X0 + 22 + bw / 2, y + gap - 4, GOLD, 8, 24)
    c.text(X0 + 22 + bw / 2 + 24, y + gap / 2 - 22, 440, ha, "ds", DEEP, "left")
    y += gap
    c.rect(X0, y, w, bot_h, fill=DEEP, rx=18)
    c.text(X0 + 22, y + 12, w - 44, hb, "dl", LIGHT, "left")
    bw = w - 44
    c.rect(X0 + 22, y + 66, bw, bot_h - 66 - 12, fill=TEAL, rx=14)
    tt = _th(c, took, bw - 40)
    ty = y + 66 + (bot_h - 66 - 12 - tt) / 2
    c.text(X0 + 42, ty, bw - 40, took["text"], "dn", CREAM, "left", (X0 + 22, y + 66, bw, bot_h - 78))
    if took.get("sub"):
        c.text(X0 + 42, ty + c.lines(took["text"], bw - 40, 34) * 44.2 + 6, bw - 40, took["sub"], "ds", CREAM, "left", (X0 + 22, y + 66, bw, bot_h - 78))
    return y + bot_h


def mismatch(c: Canvas, spec: dict, y0: float) -> float:
    """同一個東西寫法不同，SQL 就接不起來（SAG 第 4 則）。heads = [上段標籤, 下段標籤, 缺口標籤]；
    nodes = [{text（共同的寫法）, sub（上段說明）}, {text（另一種寫法）, sub（下段說明）}]；outcomes = 兩個事件 [{text, sub?}]。
    上段：兩個事件掛在同一個寫法上，金色粗線串起來；下段：兩個事件各掛不同寫法，中間斷開、標缺口標籤。純示意。"""
    h1, h2, hgap = spec["heads"]
    same, other = spec["nodes"]
    ea, eb = spec["outcomes"]
    w = X1 - X0
    evw, evh = 190, 112
    chw, chh = 190, 64
    ph = max(_th(c, {"text": same["sub"]}, w), 0) if same.get("sub") else 0
    qh = _th(c, {"text": other["sub"]}, w) if other.get("sub") else 0
    gh = c.lines(hgap, 300, 28) * 39.2
    total = 44 + evh + 14 + ph + 46 + 44 + evh + 14 + max(qh, gh)
    _fit(total, BOTTOM - y0, "mismatch")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    y = y0

    def ev(x, yy, e):
        c.rect(x, yy, evw, evh, fill=DEEP, rx=14)
        t = _th(c, e, evw - 30)
        c.text(x + 15, yy + (evh - t) / 2, evw - 30, e["text"], "dn", CREAM, "center", (x, yy, evw, evh))
        if e.get("sub"):
            c.text(x + 15, yy + (evh - t) / 2 + c.lines(e["text"], evw - 30, 34) * 44.2 + 4, evw - 30, e["sub"], "ds", LIGHT, "center", (x, yy, evw, evh))

    def chip(cx, cy, label):
        c.rect(cx - chw / 2, cy - chh / 2, chw, chh, fill=GOLD, rx=32)
        c.text(cx - chw / 2 + 10, cy - 22, chw - 20, label, "dn", DEEP, "center", (cx - chw / 2, cy - chh / 2, chw, chh))

    c.text(X0, y, w, h1, "dl", TEAL, "left")
    cy = y + 44 + evh / 2
    ev(X0, y + 44, ea); ev(X1 - evw, y + 44, eb)
    mid = X0 + w / 2
    c.line(X0 + evw, cy, mid - chw / 2, cy, GOLD, 10)
    c.line(mid + chw / 2, cy, X1 - evw, cy, GOLD, 10)
    chip(mid, cy, same["text"])
    ty = y + 44 + evh + 14
    if same.get("sub"):
        c.text(X0, ty, w, same["sub"], "ds", TEAL, "center")
    y = ty + ph + 46 + extra
    c.line(X0, y - 24, X1, y - 24, TEAL, 2, dash="3 9")
    c.text(X0, y, w, h2, "dl", TEAL, "left")
    cy2 = y + 44 + evh / 2
    ev(X0, y + 44, ea); ev(X1 - evw, y + 44, eb)
    lx, rx_ = X0 + evw + 40 + chw / 2, X1 - evw - 40 - chw / 2
    c.line(X0 + evw, cy2, lx - chw / 2, cy2, GOLD, 10)
    c.line(rx_ + chw / 2, cy2, X1 - evw, cy2, GOLD, 10)
    chip(lx, cy2, same["text"]); chip(rx_, cy2, other["text"])
    c.line(lx + chw / 2 + 8, cy2, rx_ - chw / 2 - 8, cy2, TEAL, 4, dash="8 8")
    _cross(c, (lx + rx_) / 2, cy2, 13, DEEP, 5)
    ty2 = y + 44 + evh + 14
    c.text((lx + rx_) / 2 - 150, ty2, 300, hgap, "ds", DEEP, "center")
    if other.get("sub"):
        c.text(X0, ty2 + gh + 6, w, other["sub"], "ds", TEAL, "center")
        return ty2 + gh + 6 + qh
    return ty2 + gh


def _lock(c: Canvas, cx: float, cy: float, s: float, color: str) -> None:
    c.rect(cx - s * .55, cy - s * .1, s * 1.1, s * .85, fill=color, rx=6)
    c.raw(f'<path class="bg" d="M {cx - s * .32:.1f} {cy - s * .1:.1f} v {-s * .22:.1f} a {s * .32:.1f} {s * .32:.1f} 0 0 1 {s * .64:.1f} 0 v {s * .22:.1f}" fill="none" stroke="{color}" stroke-width="5"/>')


def ledger(c: Canvas, spec: dict, y0: float) -> float:
    """只能往後新增的記錄簿（SAG 第 4 則：append-only）。heads = [時間軸標籤]；
    nodes = 依時間由上到下的紀錄 2～5 筆 [{text, sub?, new?: true}]（舊的畫鎖，new 的畫金色與「＋」）；
    outcomes[0] = {text, sub?}（右邊一塊說明：舊的改不了、只能再加新的）。純示意，例子要標「假設」。"""
    hd = spec["heads"][0]
    rows = spec["nodes"]
    note = spec["outcomes"][0]
    if not 2 <= len(rows) <= 5:
        raise ValueError(f"ledger 的 nodes 要 2～5 筆，現在是 {len(rows)}")
    w = X1 - X0
    cw, ax = 500, X0 + 52
    rh = [max(_th(c, r, cw - (140 if r.get('ask') else 120)) + 28, 84) for r in rows]
    nw = X1 - (ax + cw) - 36
    nh = _th(c, note, nw - 36) + 40
    total = 44 + sum(rh) + 16 * (len(rows) - 1)
    _fit(max(total, 44 + nh), BOTTOM - y0, "ledger")
    add = min((BOTTOM - y0 - total) / len(rows), 50 if len(rows) >= 3 else 110)   # 只有 2 筆時讓每列撐高，圖才用得滿
    rh = [h + add for h in rh]
    total += add * len(rows)
    c.text(X0, y0, 300, hd, "dl", TEAL, "left")
    c.arrow(X0 + 16, y0 + 50, X0 + 16, y0 + total - 4, TEAL, 5, 16)
    y = y0 + 44
    for k, (r, h) in enumerate(zip(rows, rh)):
        new = bool(r.get("new"))
        c.rect(ax, y, cw, h, fill=GOLD if new else "none", stroke=DEEP, sw=3, rx=14, op=.35 if new else None)
        tx, tw = (ax + 70, cw - 140) if r.get("ask") else (ax + 24, cw - 120)   # 有 ask 的，字往右讓出「？」
        t = _th(c, r, tw)
        c.text(tx, y + (h - t) / 2, tw, r["text"], "dn", DEEP, "left", (ax, y, cw, h))
        if r.get("sub"):
            c.text(tx, y + (h - t) / 2 + c.lines(r["text"], tw, 34) * 44.2 + 6, tw, r["sub"], "ds", DEEP if new else TEAL, "left", (ax, y, cw, h))   # 金色底的列用深色字，對比度才夠
        if r.get("ask"):                                  # 新舊衝突、分不出誰有效的那幾筆：左邊放一個金色「？」
            c.circle(ax + 38, y + h / 2, 22, fill=GOLD, stroke=DEEP, sw=3)
            c.text(ax + 24, y + h / 2 - 20, 28, "？", "dl", DEEP, "center")
        if new:
            c.circle(ax + cw - 48, y + h / 2, 24, fill=GOLD, stroke=DEEP, sw=3)
            c.line(ax + cw - 60, y + h / 2, ax + cw - 36, y + h / 2, DEEP, 5)
            c.line(ax + cw - 48, y + h / 2 - 12, ax + cw - 48, y + h / 2 + 12, DEEP, 5)
        else:
            _lock(c, ax + cw - 48, y + h / 2 - 4, 34, DEEP)
        y += h + 16
    ny = y0 + 44 + (total - 44 - nh) / 2
    nx = ax + cw + 36
    c.rect(nx, ny, nw, nh, fill=DEEP, rx=14)
    c.text(nx + 18, ny + 20, nw - 36, note["text"], "dn", CREAM, "left", (nx, ny, nw, nh))
    if note.get("sub"):
        c.text(nx + 18, ny + 20 + c.lines(note["text"], nw - 36, 34) * 44.2 + 6, nw - 36, note["sub"], "ds", LIGHT, "left", (nx, ny, nw, nh))
    c.arrow(nx - 6, ny + nh / 2, ax + cw + 6, ny + nh / 2, GOLD, 6, 18)
    return y0 + total


KINDS = {"flow": flow, "compare": compare, "pairs": pairs, "samples": samples, "paths": paths, "epochs": epochs,
         "dotgrid": dotgrid, "dumbbell": dumbbell, "range": range_chart, "funnel": funnel,
         "batches": batches, "decay": decay, "stops": stops, "fan": fan, "peaks": peaks, "quad": quad, "locked": locked, "equation": equation, "tokens": tokens,
         "seesaw": seesaw, "hidden": hidden, "cycle": cycle, "links": links, "hops": hops, "bubble": bubble, "drift": drift, "ingest": ingest,
         "roles": roles, "embed": embed, "online": online, "gate": gate, "concat": concat, "joint": joint, "rails": rails, "scoreboard": scoreboard, "leak": leak, "amplify": amplify,
         "receipt": receipt, "squeeze": squeeze, "alias": alias, "handoff": handoff, "mismatch": mismatch, "ledger": ledger}


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
        out.append(n["text"]); out += [n["sub"]] if n.get("sub") else []; out += [n["sub2"]] if n.get("sub2") else []; out += [n["win"]] if n.get("win") else []
    for row in sl.get("cells", []):
        for pair in row:
            out += list(pair)
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
