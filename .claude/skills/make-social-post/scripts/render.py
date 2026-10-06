"""投影片渲染引擎與程式 B（references/program-b.md）。

內容規格 JSON -> 填入系列模板 -> Playwright 截圖 1080x1350 PNG -> 版面檢查。
外觀完全由模板決定；LLM 只給內容規格。

用法（repo 根目錄；Chromium 在 repo 內 .playwright-browsers/，程式會自己設好路徑）：
  uv run python .claude/skills/make-social-post/scripts/render.py out/<series>/<concept>/_build/spec.json [--only 3,5]
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

ROOT = W.ROOT
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".playwright-browsers"))
PARAMS = W.load_params()
RP = PARAMS["render"]
WD, HT, SAFE_X, PAD_X = RP["width"], RP["height"], RP["safe_x"], RP["pad_x"]
CREAM, TEAL, DEEP, GOLD = "#F2E0C0", "#076876", "#01353F", "#DDA642"
MID, LIGHT, ABYSS = "#1F8A8D", "#69B4AA", "#032027"
SERIES_COLORS = {"teal-mid": MID}
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


def bob(x, y_end, col, v="", emph=False):
    g = ""
    if emph:
        g += f'<circle class="bg" cx="{x}" cy="{y_end:.1f}" r="95" fill="url(#glow)"/>'
    return g


# ---------------------------------------------------------------- 各版型
def build(spec: dict, series: dict, tag: str) -> dict:
    """回傳 {layout, html_body, ...}。HTML 片段以模板檔填入。"""
    lay = spec["layout"]
    tdir = template_dir(series["id"])
    tpl = (tdir / f"{lay}.html").read_text(encoding="utf-8")
    sc = SERIES_COLORS.get(series.get("color"), MID)
    kw = {"SERIES_TAG": esc(tag), "TITLE": title_html(spec.get("title", "")), "BODY": esc(bind_nums(spec.get("body", "")))}

    if lay == "cover":
        kw["SVG"] = svg_wrap(waves(1000, sc))
        kw["SUB_TOP"] = 560
    elif lay == "context":
        pass
    elif lay == "text":
        kw["SVG"] = svg_wrap(
            waves(760, sc)
            + f'<g><line class="g deco" x1="540" y1="832" x2="540" y2="1040" stroke="{CREAM}" stroke-width="4"/>'
              f'<circle class="bg" cx="540" cy="1040" r="95" fill="url(#glow)"/>'
              f'<polygon class="g deco" data-e="1" points="540,1028 548,1040 540,1052 532,1040" fill="{GOLD}"/></g>')
    elif lay == "table":
        rows = spec["rows"]
        y0 = 500

        def est_lines(txt, per_line):
            # 模擬 word-break: keep-all：只在標點或空白後斷行，其餘中文連續串不可拆
            def width(t):
                return sum(1 if ord(ch) > 127 else 0.55 for ch in t)
            chunks = [c for c in re.split(r"(?<=[、，；,;。：:])|(?<=\s)", txt) if c]
            lines, cur = 1, 0.0
            for c in chunks:
                w = width(c)
                if cur + w > per_line and cur > 0:
                    lines, cur = lines + 1, 0.0
                cur += w
                while cur > per_line:
                    lines, cur = lines + 1, cur - per_line
            return lines

        parts, cells, y = "", "", y0
        for (k, v) in rows:
            parts += f'<line class="g sep" x1="80" y1="{y}" x2="1000" y2="{y}" stroke="{DEEP}" stroke-width="2" opacity=".35"/>'
            cells += (f'<div class="t abs cell k" style="left:80px;top:{y + 28}px;width:300px">{esc(k)}</div>'
                      f'<div class="t abs cell" style="left:400px;top:{y + 28}px;width:600px">{esc(v)}</div>')
            lines = max(est_lines(v, 15.0), est_lines(k, 7.5))
            y += 56 + lines * 57 + 8
        parts += f'<line class="g sep" x1="80" y1="{y}" x2="1000" y2="{y}" stroke="{DEEP}" stroke-width="2" opacity=".35"/>'
        kw["SVG"] = svg_wrap(parts)
        kw["CELLS"] = cells
        kw["NOTE_BLOCK"] = (f'<div class="t abs note" style="left:80px;top:1196px">{esc(spec["note"])}</div>' if spec.get("note") else "")
    elif lay == "chart_bars":
        bars = spec["bars"]
        x0, maxlen = 72, 640
        s = maxlen / max(b["value"] for b in bars)
        labels, svg, y = "", "", 500
        top = y - 20
        for b in bars:
            subs = b.get("subs", [])
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
            y = by + 44 + 50
        svg += f'<line class="g axis" x1="{x0}" y1="{top}" x2="{x0}" y2="{y - 40}" stroke="{DEEP}" stroke-width="3"/>'
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
    elif lay == "takeaway":
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
            if i == cur:
                svg += f'<rect class="bg" x="72" y="{y - 10}" width="936" height="84" rx="6" fill="{DEEP}"/>'
                svg += f'<polygon class="g mark" data-e="1" points="100,{y + 32} 112,{y + 44} 100,{y + 56} 88,{y + 44}" fill="{GOLD}"/>'
                out += f'<div class="t abs item cur" style="left:132px;top:{y + 8}px">{esc(t)}</div>'
            else:
                svg += f'<polygon class="g mark" points="100,{y + 36} 108,{y + 44} 100,{y + 52} 92,{y + 44}" fill="{TEAL}"/>'
                out += f'<div class="t abs item" style="left:132px;top:{y + 8}px">{esc(t)}</div>'
            y += 112
        kw["SVG"] = svg_wrap(svg)
        kw["ITEMS"] = out
        kw["NAV"] = esc(spec.get("nav", ""))
    else:
        raise ValueError(f"未知版型 {lay}")

    # 模板填入
    for k, v in kw.items():
        tpl = tpl.replace("{{" + k + "}}", str(v))
    assert "{{" not in tpl, re.findall(r"\{\{\w+\}\}", tpl)
    return {"body": tpl}


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
  return {ts,gs,ropes,bobs,bars,axis,ticks,emph,chk,
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
        mx = 4 if lay == "takeaway" else PARAMS["title_max_lines"]
        chk(f"標題最多 {mx} 行", ti["lines"] <= mx, f"{ti['lines']} 行")
        chk("標題末行 >= 2 字、換行不拆詞", ti["lastChars"] >= 2 and not ti["bad"], {"lastChars": ti["lastChars"], "bad": ti["bad"]})
        chk("標題的數字與單位不拆成兩行", not ti["badNum"], ti["badNum"])
    bo = m["chk"].get("body")
    if bo:
        if lay in ("table", "chart_bars", "chart_sounding"):
            chk("圖表版型補充只有一行、不拆詞", bo["lines"] == 1 and not bo["bad"], {"lines": bo["lines"], "bad": bo["bad"]})
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
    if lay not in ("cover", "context", "takeaway"):
        chk("只有一組強調元素", m["emph"] <= 1, m["emph"])
    chk("系列標籤與系列檔的名稱完全相同", all(t == series_name for t in tag_texts), tag_texts)
    return res


def render_all(spec_path: Path, only: set[int] | None = None) -> int:
    doc = json.loads(spec_path.read_text(encoding="utf-8"))
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
            built = build(sl, series, tag)
            page = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><style>{css}</style></head>'
                    f'<body>{built["body"]}</body></html>')
            hp = htmldir / f"{i:02d}.html"
            hp.write_text(page, encoding="utf-8")
            pg.goto(hp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(200)
            if sl["layout"] == "cover":
                pg.evaluate("() => {const t=document.getElementById('title'), s=document.getElementById('body'); "
                            "s.style.top=(t.getBoundingClientRect().bottom+36)+'px'}")
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
                alts[f"{i:02d}.png"] = (plain(sl.get("title", "")) + ("。" + body if body else ""))
        b.close()
    (bld / "alt-text.json").write_text(json.dumps(alts, ensure_ascii=False, indent=2), encoding="utf-8")
    (bld / "checks-b.json").write_text(json.dumps({"template_hash": thash, "slides": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"template_hash={thash}  程式 B：{len(report) - failed}/{len(report)} 張通過")
    return 1 if failed else 0


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    sys.exit(render_all(Path(sys.argv[1]).resolve(), only))
