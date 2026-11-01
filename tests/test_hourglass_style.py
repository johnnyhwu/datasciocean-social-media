"""系列 series/cerebras-rag（style: hourglass，沙漏）的回歸測試。
每個版型都要通過程式 B；封面與內頁都有系列標籤；沙漏的圖形是固定規則（哲學 series/cerebras-rag/philosophy.md：
窄帶永遠五格、金色只給 metadata 那一格、內頁收束與展開對稱、亮起來的那一條隨張數換、小沙漏的沙隨進度流下）；
故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_hourglass_style.py
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

CONCEPT = "slack-vector-failure-orthogonal-signals"   # 第 2 則：recap 與系列地圖都要「前面有別則」才成立
TAG = R.load_series("cerebras-rag")["name"]    # 系列標籤必須與 series.md 的 name 相同；讀檔才不會在系列改名時失效
fails = []


def render(slides, concept=CONCEPT):
    doc = {"series": "cerebras-rag", "concept": concept, "slides": slides}
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
    {"layout": "cover", "title": "四種完全不同的資料，\n怎麼塞進[[同一張表]]？", "body": "示範副標：上面怎麼亂都行，都得先穿過同一個窄口。"},
    {"layout": "recap", "title": "[[前情提要]]與這一則", "current": CONCEPT, "refs": ["結構"]},
    {"layout": "context", "title": "先講兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    {"layout": "context", "title": "脈絡張沒有名詞表", "body": "示範脈絡文字。"},
    {"layout": "text", "title": "文字版型：下半是沙漏", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "label": "② 代價", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "示意圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "一次看完這個系列", "current": CONCEPT, "nav": "示範導流行"},
]

code, out, html = render(DECK)
expect("沙漏樣張的每個版型通過程式 B（10 張）", code == 0 and "10/10 張通過" in out, out)
expect(f"內頁與封面都有系列標籤（{TAG}）", html.count(TAG) >= 10, str(html.count(TAG)))

# 小標籤（「走到哪一段」）：右上角被小沙漏佔住，所以放右下角；框不用金色，免得跟圖上的金色搶焦點
CSS = (ROOT / "series/cerebras-rag/templates/style.css").read_text(encoding="utf-8")
chip_rule = re.search(r"\.chip\{(.*?)\}", CSS, re.S)
chip_top = re.search(r"top:(\d+)px", chip_rule.group(1)) if chip_rule else None
expect("小標籤有渲染出來", 'class="t abs chip"' in html, "")
expect("小標籤在下半部（右上角是小沙漏）", chip_top and int(chip_top.group(1)) > 1000, chip_rule.group(1) if chip_rule else "沒有 .chip 規則")
expect("小標籤的框不是金色", chip_rule and R.GOLD not in chip_rule.group(1), chip_rule.group(1) if chip_rule else "")

# 窄帶：永遠五格，金色只給 metadata 那一格
w = R.hg_waist(540, 430)
cells = re.findall(r'<rect class="g mark" data-e="(\d)"', w)
expect("hg_waist：窄帶永遠五格", len(cells) == 5, str(cells))
expect("hg_waist：金色只有一格", cells.count("1") == 1, str(cells))
expect("hg_waist：金色那格是 metadata（第 3 格）", R.HG_FIELDS[R.HG_GOLD_CELL] == "metadata" and cells[2] == "1", str(R.HG_GOLD_CELL))

# 內頁裝飾：同參數同結果；收束與展開對稱（上下各五條）；亮起來的那一條隨張數換；金色只有一條
a, b = R.hg_deco(1, 10), R.hg_deco(1, 10)
c = R.hg_deco(2, 10)
expect("hg_deco：同參數同結果", a == b, "")
expect("hg_deco：收束五條、展開五條", a.count("<line") == 10, str(a.count("<line")))
lit = lambda s: re.findall(r'x2="(\d+)" y2="\d+" stroke="#DDA642"', s)
expect("hg_deco：亮起來的那一條隨張數換", lit(a) and lit(c) and lit(a) != lit(c), f"{lit(a)} {lit(c)}")
expect("hg_deco：金色只有一條（一條線加一個端點）", a.count("#DDA642") == 2, str(a.count("#DDA642")))
xs = [int(x) for x in re.findall(r'<circle class="bg" cx="(\d+)" cy="790"', a)]
expect("hg_deco：窄口在正中央（上段端點左右對稱）", xs and xs[0] + xs[-1] == R.WD, str(xs))

# 封面：三則各強調不同的一段（腰以上、腰以下、腰本身），而且字級只用 28
cv = [R.hg_cover(i) for i in range(3)]
expect("hg_cover：每一則強調的段落不同", len({*cv}) == 3, "")
expect("hg_cover：四個來源都有標籤", all(all(n in cv[0] for n in ("Slack", "Wiki", "程式碼", "Jira")) for _ in (0,)), "")
sizes = set(re.findall(r'font-size="(\d+)"', "".join(cv)))
expect("hg_cover：字級只用 28", sizes <= {"28"}, str(sizes))
# 形狀外框的透明度（形狀內部的細線刻意更淡，不算在內）：淡的那一段也要看得見，不低於 .55
frames = [float(v) for s in cv for v in re.findall(r'stroke-width="3" stroke-opacity="(0?\.?\d+(?:\.\d+)?)"', s)]
expect("hg_cover：淡的那一段也看得見（形狀外框不低於 .55）", frames and min(frames) >= .55, str(sorted(set(frames))))

# 右上角小沙漏：沙隨進度流下（上半遞減、下半遞增）
tri = lambda s: re.findall(r'fill="#1F8A8D" fill-opacity="\.55"', s)
up = lambda idx: R.hg_corner(idx, 10)
expect("hg_corner：第一張只有上半有沙", up(0).count('fill-opacity=".55"') == 1, up(0))
expect("hg_corner：中間兩半都有沙", up(5).count('fill-opacity=".55"') == 2, "")
expect("hg_corner：最後一張只有下半有沙", up(10).count('fill-opacity=".55"') == 1, "")
expect("hg_corner：落下的那一粒是金色", up(5).count(R.GOLD) == 1, "")

# 帶走張（深色底）：沒有金色文字（金色禁止當米色底上的文字；深色底也只用在圖形）
expect("hg_takeaway：金色只給窄口那一點", R.hg_takeaway().count(R.GOLD) == 1, "")

# 封面主標 3 行也要放得下（cover_title_max_lines: 3）
code, out, _ = render([{"layout": "cover", "title": "四種完全不同的資料，\n怎麼塞進同一張表，\n而且還搜得到？", "body": "示範副標：先收窄，再展開。"}])
expect("封面主標 3 行也通過程式 B", code == 0 and "1/1 張通過" in out, out)

# 系列地圖與回顧頁：hook 當標題時可能比一行長（約 25 字以上）→ 折成兩行、整列下移；一行的標題照舊、不加寬度
_short = [{"concept": "a", "planned_title": "Slack、Wiki、程式碼、Jira，怎麼塞進同一張表？", "summary": "摘要一句。"}]
_long = [{"concept": "a", "planned_title": "搜尋出三種毛病，Cerebras 不是多加幾招，是一種毛病配一帖藥", "summary": "摘要一句。"}]
_s_svg, _s_out, _s_end = R.series_rows(_short, 0, 330)
_l_svg, _l_out, _l_end = R.series_rows(_long, 0, 330)
expect("series_rows：一行的標題不加寬度、不折行", "width:836px" not in _s_out, _s_out)
expect("series_rows：長標題折行並加寬度", "width:836px;white-space:normal" in _l_out, _l_out)
expect("series_rows：長標題的整列比一行的高一行（48px）", abs((_l_end - _s_end) - 48) < 1, f"{_l_end} vs {_s_end}")
expect("series_rows：長標題時細節往下移一行", f"top:{330 + 48 + 48}px" in _l_out, _l_out)

# 故意做壞
code, out, _ = render([{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}])
expect("故意做壞：補充文字太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "cover", "title": "四種完全不同的資料怎麼塞進同一張表而且還要搜得到答案這件事其實不簡單", "body": "示範副標"}])
expect("故意做壞：封面主標太長 → 抓得到", code != 0 and "FAIL" in out, out)
code, out, _ = render([{"layout": "series_map", "title": "想接著看？", "current": "不存在的觀念", "nav": "x"}])
expect("故意做壞：系列地圖的 current 不在成員裡 → 報錯", code != 0, out)

print("\n全部通過" if not fails else f"\n失敗 {len(fails)} 項：{fails}")
raise SystemExit(1 if fails else 0)
