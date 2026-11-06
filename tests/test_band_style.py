"""系列 series/llm-as-a-verifier（style: band，濃淡帶）的回歸測試。
每個版型都要通過程式 B；封面與內頁都有系列標籤；濃淡帶的圖形是固定規則（哲學 series/llm-as-a-verifier/philosophy.md：
帶子全寬、越濃越重、金色只給針、針在分佈的期望值（封面、帶走張）或隨張數往右移（頂端細帶、文字張）、
深色底濃淡反過來、不同則換分佈）；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_band_style.py
spec 放暫存資料夾，不碰 out/；--force 只渲染暫存資料夾。
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))
import render as R

SERIES = "llm-as-a-verifier"
CONCEPT = "ppt-pivot-tournament"   # 第 2 則：recap 與系列地圖都要「前面有別則」才成立
TAG = R.load_series(SERIES)["name"]
fails = []


def render(slides, concept=CONCEPT):
    doc = {"series": SERIES, "concept": concept, "slides": slides}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(RENDER), str(p), "--force"], capture_output=True, text=True, cwd=ROOT)
        html = "".join(f.read_text(encoding="utf-8") for f in sorted((Path(d) / "html").glob("*.html"))) if (Path(d) / "html").exists() else ""
        return r.returncode, r.stdout + r.stderr, html


def expect(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail[:300]}]" if not ok else ""))
    if not ok:
        fails.append(name)


DECK = [
    {"layout": "cover", "title": "LLM 打分數老是平手？\n[[不是它分不出來]]", "body": "示範副標：模型心裡其實有偏好，\n是「只取最高分」把它丟掉了。"},
    {"layout": "recap", "title": "[[前情提要]]與這一則", "current": CONCEPT, "refs": ["結構"]},
    {"layout": "context", "title": "先講兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "context", "title": "脈絡張沒有名詞表", "body": "示範脈絡文字。"},
    {"layout": "text", "title": "文字版型：下半是濃淡帶", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "label": "② 代價", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "示意圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "一次看完這個系列", "current": CONCEPT, "nav": "示範導流行"},
]

code, out, html = render(DECK)
expect("濃淡帶樣張的每個版型通過程式 B（10 張）", code == 0 and "10/10 張通過" in out, out)
expect(f"內頁與封面都有系列標籤（{TAG}）", html.count(TAG) >= 10, str(html.count(TAG)))
expect("封面、文字張、帶走張與內頁頂端都有帶子", html.count("url(#bdc)") == 1 and html.count("url(#bdd)") == 2
       and html.count("url(#bdt)") == 1 and html.count("url(#bds)") >= 5,
       str([html.count(f"url(#{g})") for g in ("bdc", "bdd", "bdt", "bds")]))
expect("小標籤的框不是金色", R.GOLD not in (re.search(r"\.chip\{(.*?)\}", (ROOT / f"series/{SERIES}/templates/style.css").read_text(encoding="utf-8"), re.S) or [""])[0], "")

# 帶子：全寬、五個刻度、金色只有那根針、漸層停點不碰金色
needle_x = lambda s: [float(x) + float(w) / 2 for x, w in re.findall(r'<rect class="bg" x="([\d.]+)" y="-?[\d.]+" width="([\d.]+)" height="[\d.]+" fill="' + R.GOLD, s)]
p0 = R.BD_DISTS[0]
b = R.bd_band(600, 230, p0, 3.0, "t")
expect("bd_band：帶子貼齊畫布兩端（x=0、寬=畫布寬）", f'x="0" y="600" width="{R.WD}" height="230"' in b, b[:300])
expect("bd_band：五個刻度、五個數字", b.count("<line ") == 5 and len(re.findall(r">[1-5]</text>", b)) == 5, "")
expect("bd_band：金色只有一處（針）", b.count(R.GOLD) == 1, str(b.count(R.GOLD)))
stops = re.findall(r'stop-color="(#[0-9a-f]{6})"', b)
expect("bd_band：五個停點、都不是金色", len(stops) == 5 and R.GOLD.lower() not in stops, str(stops))
expect("bd_band：不帶刻度時沒有線與數字", "<line " not in R.bd_band(0, 18, p0, 1, "t", ticks=False) and "<text" not in R.bd_band(0, 18, p0, 1, "t", ticks=False), "")

# 濃淡：米色底越重越暗、深色底越重越亮
lum = lambda h: sum(c * k for c, k in zip((int(h[i:i + 2], 16) for i in (1, 3, 5)), (.299, .587, .114)))
qs = [0, .05, .12, .2, .3, .45, .6]
light = [lum(R.bd_shade(q)) for q in qs]
dark = [lum(R.bd_shade(q, dark=True)) for q in qs]
expect("bd_shade：米色底機率越高越暗", all(a >= b_ for a, b_ in zip(light, light[1:])) and light[0] > light[-1], str(light))
expect("bd_shade：深色底機率越高越亮", all(a <= b_ for a, b_ in zip(dark, dark[1:])) and dark[0] < dark[-1], str(dark))

# 封面：針在期望值；三則的分佈與針都不同
for mi in range(3):
    p = R.BD_DISTS[mi]
    nx = needle_x(R.bd_cover(mi))
    expect(f"bd_cover：第 {mi + 1} 則分佈加總為 1", abs(sum(p) - 1) < 1e-9, str(sum(p)))
    expect(f"bd_cover：第 {mi + 1} 則針在期望值", len(nx) == 1 and abs(nx[0] - R.bd_x(R.bd_ev(p))) < .2, f"{nx} vs {R.bd_x(R.bd_ev(p))}")
cv = [R.bd_cover(i) for i in range(3)]
expect("bd_cover：三則封面各不相同", len(set(cv)) == 3, "")
evs = sorted(R.bd_ev(p) for p in R.BD_DISTS)
expect("bd_cover：三則的針停在不同位置（期望值至少差 0.3）", all(b_ - a > .3 for a, b_ in zip(evs, evs[1:])), str(evs))
expect("bd_cover：針不落在刻度上（期望值不是整數）", all(abs(R.bd_ev(p) - round(R.bd_ev(p))) > .05 for p in R.BD_DISTS), str([R.bd_ev(p) for p in R.BD_DISTS]))

# 頂端細帶與文字張：針隨張數往右移；第一張在刻度 1、最後一張在刻度 5
n = 10
sx = [needle_x(R.bd_strip(i, n, 0))[0] for i in range(1, n + 1)]
expect("bd_strip：針隨張數往右移", all(a < b_ for a, b_ in zip(sx, sx[1:])), str(sx))
expect("bd_strip：第一張在最左刻度、最後一張在最右刻度", abs(sx[0] - R.BD_X0) < .2 and abs(sx[-1] - R.BD_X1) < .2, str(sx))
expect("bd_strip：高度只有 18（細線）", 'y="0" width="%d" height="18"' % R.WD in R.bd_strip(3, n, 0), "")
dx = [needle_x(R.bd_deco(i, n, 0))[0] for i in (2, 5, 8)]
expect("bd_deco：針隨張數往右移", dx[0] < dx[1] < dx[2], str(dx))
expect("bd_deco：金色只有那根針", R.bd_deco(4, n, 0).count(R.GOLD) == 1, "")
expect("bd_deco：沿用這一則封面的分佈", re.findall(r'stop-color="(#\w+)"', R.bd_deco(4, n, 1)) == re.findall(r'stop-color="(#\w+)"', R.bd_cover(1)), "")

# 帶走張（深色底）：濃淡反過來、金色只有針、針在期望值
t = R.bd_takeaway(0)
ts = re.findall(r'stop-color="(#[0-9a-f]{6})"', t)
expect("bd_takeaway：最重的停點最亮", max(range(5), key=lambda k: lum(ts[k])) == max(range(5), key=lambda k: p0[k]), str(ts))
expect("bd_takeaway：金色只有針、在期望值", t.count(R.GOLD) == 1 and abs(needle_x(t)[0] - R.bd_x(R.bd_ev(p0))) < .2, "")

# 封面主標 3 行也要放得下
code, out, _ = render([{"layout": "cover", "title": "LLM 打分數老是平手？\n不是它分不出來，\n是答案被丟掉了", "body": "示範副標：模型心裡其實有偏好。"}])
expect("封面主標 3 行也通過程式 B", code == 0 and "1/1 張通過" in out, out)

# 故意做壞
code, out, _ = render([{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}])
expect("故意做壞：補充文字太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "cover", "title": "LLM 打分數老是平手其實不是它分不出來而是只取最高分把模型心裡的偏好整個丟掉了這件事", "body": "示範副標"}])
expect("故意做壞：封面主標太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "cover", "title": "LLM 打分數老是平手？", "body": "示範副標很長，" * 40}])
expect("故意做壞：封面副標太長（壓到下緣）→ 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "series_map", "title": "想接著看？", "current": "不存在的觀念", "nav": "x"}])
expect("故意做壞：系列地圖的 current 不在成員裡 → 報錯", code != 0, out)

# caption 逐張摘要：標題裡的 \n 是圖上的換行，caption 要接成一行（2026-11-03，第 1 則「Terminal-Bench 上，\n27%…」被拆成兩行）
import build_package as BP
cap = BP.caption_text({"slides": [{"layout": "text", "title": "Terminal-Bench 上，\n[[27%]] 的比較是平手", "body": "示範。"}],
                       "caption": {"first": "第一句", "nav": "導流", "hashtags": ["LLMVerifier"]}, "series": SERIES})
expect("caption 逐張摘要把標題的換行接成一行", "・Terminal-Bench 上，27% 的比較是平手" in cap, cap)

print("\n全部通過" if not fails else f"\n失敗 {len(fails)} 項：{fails}")
raise SystemExit(1 if fails else 0)
