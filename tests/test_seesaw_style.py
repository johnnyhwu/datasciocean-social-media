"""獨立貼文 standalone/bradley-terry-pairwise-preference（style: seesaw，蹺蹺板）的回歸測試。
樣張的每個版型與三種新示意圖（seesaw、hidden、cycle）都要通過程式 B；沒有系列標籤；封面副標位置固定；
蹺蹺板的橫條比例與方塊數一致；故意做壞的版本必須被抓到。
用法（repo 根目錄）：uv run python tests/test_seesaw_style.py
spec 放暫存資料夾，不碰 out/；--force 只渲染暫存資料夾。
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
CONCEPT = "bradley-terry-pairwise-preference"
fails = []


def render(slides, concept=CONCEPT, math=False):
    doc = {"series": None, "concept": concept, "slides": slides}
    if math:
        doc["math"] = True
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


SEESAW = {"layout": "diagram", "kind": "seesaw", "title": "實力 8 對 2，A 贏面八成", "body": "示範補充，A 隊實力值 8、B 隊實力值 2。",
          "nodes": [{"text": "A 隊", "sub": "實力值 8", "blocks": 8, "win": "A 贏 80%"}, {"text": "B 隊", "sub": "實力值 2", "blocks": 2, "win": "B 贏 20%"}],
          "outcomes": [{"text": "B 隊雖然弱，仍有兩成機率爆冷"}], "note": "假設的例子"}
HIDDEN = {"layout": "diagram", "kind": "hidden", "title": "結果看得見，實力值看不見", "body": "示範補充。", "heads": ["看得到：比賽結果", "看不到：每支球隊的實力值"],
          "nodes": [{"text": "第 1 場：A 隊贏"}, {"text": "第 2 場：A 隊贏"}, {"text": "第 3 場：B 隊贏"}],
          "outcomes": [{"text": "A 隊", "sub": "實力值 ？"}, {"text": "B 隊", "sub": "實力值 ？"}], "note": "假設的例子"}
CYCLE = {"layout": "diagram", "kind": "cycle", "title": "人的偏好可能繞成一圈", "body": "示範補充。", "heads": ["A 比 B 好", "B 比 C 好", "C 比 A 好"],
         "nodes": [{"text": "A"}, {"text": "B"}, {"text": "C"}], "outcomes": [{"text": "示範：照假設 A 會比 C 好"}]}

DECK = [
    {"layout": "cover", "title": "實力差 4 倍，弱的那隊還有[[2 成]]會爆冷", "body": "示範副標第一行\n示範副標第二行"},
    {"layout": "context", "title": "先認識兩個詞", "body": "示範脈絡：", "rows": [["甲", "第一個詞"], ["乙", "第二個詞"]], "key_w": 170},
    HIDDEN, SEESAW, CYCLE,
    {"layout": "text", "title": "文字版型：中段一座蹺蹺板", "body": "示範補充文字，最多五行。"},
    {"layout": "table", "title": "對照表版型", "body": "示範補充。", "rows": [["甲", "第一列"], ["乙", "第二列"]], "key_w": 170},
    {"layout": "chart_bars", "title": "橫條圖版型", "subs_inline": True, "body": "示範補充。", "unit": "%",
     "note": "示範圖註", "bars": [{"name": "甲", "subs": ["對照"], "value": 30}, {"name": "乙", "subs": ["重點"], "value": 60, "emphasize": True}]},
    {"layout": "diagram", "kind": "flow", "title": "流程圖版型", "body": "示範補充。", "nodes": [{"text": "一"}, {"text": "二"}, {"text": "三"}]},
    {"layout": "takeaway", "question": "示範問題？", "title": "示範帶走：一句話"},
    {"layout": "series_map", "title": "想接著看？", "items": ["persona-d2s-training-design-flaws"], "nav": "示範導流行"},
]

code, out, html = render(DECK)
expect("蹺蹺板樣張的每個版型與三種新示意圖通過程式 B（11 張）", code == 0 and "11/11 張通過" in out, out)
expect("獨立貼文沒有系列標籤（HTML 裡沒有 class tag）", 'class="t abs tag"' not in html, "")

# 封面副標固定在 y=400（標題一行或兩行都一樣）
_, _, h1 = render([{"layout": "cover", "title": "先問，再答？", "body": "示範副標"}])
_, _, h2 = render([{"layout": "cover", "title": "實力差 4 倍，弱的那隊還有 2 成會爆冷", "body": "示範副標"}])
expect("封面副標位置固定（SUB_TOP = 400）", "top:400px" in h1 and "top:400px" in h2, "")

# 蹺蹺板下面的橫條：左段寬度 / 總寬 = 8/(8+2)；金色那段是右端（輕的一端）
_, _, hs = render([SEESAW])
bars = re.findall(r'<rect class="bg" x="([\d.]+)" y="[\d.]+" width="([\d.]+)" height="84\.0" rx="14" fill="(#[0-9A-Fa-f]{6})"', hs)
ok = len(bars) == 2 and abs(float(bars[0][1]) / (float(bars[0][1]) + float(bars[1][1])) - 0.8) < 0.005 and bars[1][2].upper() == "#DDA642"
expect("蹺蹺板的機率橫條：左段 = 方塊數比例（8:2 → 80%），右段金色", ok, str(bars))

# 傾斜角隨兩端比例：8 對 2 向左傾（rotate 為負），2 對 8 與 5 對 5 見下
even = json.loads(json.dumps(SEESAW)); even["nodes"][0]["blocks"] = 5; even["nodes"][1]["blocks"] = 5
_, _, he = render([even])
expect("故意改成 5 對 5：梁不傾斜（rotate(-0.00 ...)）", "rotate(-0.00" in he or "rotate(0.00" in he, "")

bad = [{"layout": "text", "title": "故意做壞", "body": "很長的補充文字，" * 40}]
code, out, _ = render(bad)
expect("故意做壞：補充文字太長 → 抓得到", code != 0 and "FAIL" in out, out)

bad = [{"layout": "cover", "title": "實力差四倍但是弱的那隊還有兩成機率會爆冷而且這個差距讓人意外不已", "body": "示範副標"}]
code, out, _ = render(bad)
expect("故意做壞：封面主標超過兩行 → 抓得到", code != 0 and "FAIL" in out, out)

b = json.loads(json.dumps(SEESAW)); b["nodes"][0]["sub"] = "很長的說明" * 30
code, out, _ = render([b])
expect("故意做壞：蹺蹺板的標籤太長放不下 → 報錯", code != 0 and "放不下" in out, out)

b = json.loads(json.dumps(HIDDEN)); b["nodes"][0]["text"] = "很長的結果說明" * 12
code, out, _ = render([b])
expect("故意做壞：水面上的結果太長 → 抓得到", code != 0, out)

b = json.loads(json.dumps(CYCLE)); b["outcomes"][0]["text"] = "很長的說明" * 60
code, out, _ = render([b])
expect("故意做壞：繞圈圖底下的框太長放不下 → 報錯", code != 0 and "放不下" in out, out)

PAIRS = {"layout": "diagram", "kind": "pairs", "title": "測試標題", "body": "測試補充。", "heads": ["左", "右"], "pairs": [["甲", "乙"], ["丙", "丁"]],
         "outcomes": [{"text": "底下一條橫框", "sub": "小字", "tone": "good"}]}
code, out, _ = render([PAIRS])
expect("pairs 底下的橫框（outcomes）通過程式 B", code == 0 and "1/1 張通過" in out, out)
b = json.loads(json.dumps(PAIRS)); b["outcomes"][0]["text"] = "很長的說明" * 60
code, out, _ = render([b])
expect("故意做壞：pairs 底下的橫框太長放不下 → 報錯", code != 0 and "放不下" in out, out)

# 文字裡的 \n 是明確換行：框高要把每一段都算進去（2026-10-22：arXiv 網址換行後貼到框線）
NL = {"layout": "diagram", "kind": "stops", "title": "測試標題", "body": "測試補充。",
      "nodes": [{"text": "甲", "sub": "說明\narxiv.org/abs/0000.00000"}, {"text": "乙", "sub": "說明\n網址"}, {"text": "丙"}]}
code, out, html = render([NL])
expect("子標籤含 \\n 換行的 stops 通過程式 B", code == 0 and "1/1 張通過" in out, out)

# LaTeX（spec 頂層 "math": true，`$...$` 由 KaTeX 排版）
import sys
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))
import cardlib as W
expect("tex_plain：分數、上下標、希臘字母", W.tex_plain(r"贏的機率 ＝ $\dfrac{p_i}{p_i + p_j}$，$\sigma(r_i - r_j)$") == "贏的機率 ＝ p_i/(p_i + p_j)，σ(r_i - r_j)")
expect("tex_plain：巢狀大括號", W.tex_plain(r"$\dfrac{e^{r_i}}{1 + e^{-(r_i - r_j)}}$") == "(e^(r_i))/(1 + e^(-(r_i - r_j)))")
expect("tex_plain：mathcal、mathbb 與 loss 公式", W.tex_plain(r"$\mathcal{L} = -\mathbb{E}[\log \sigma(s_w - s_r)]$") == "L = -E[log σ(s_w - s_r)]")
expect("tex_plain：沒有 $ 的字串原樣不動", W.tex_plain("A 贏 B 的機率是 0.8") == "A 贏 B 的機率是 0.8")
expect("untex：遞迴處理 dict 與 list", W.untex({"a": [r"$\sigma$"], "b": {"c": "x"}}) == {"a": ["σ"], "b": {"c": "x"}})
MATH = {"layout": "diagram", "kind": "flow", "title": "數學：$r$ 的差", "body": "把實力 $p$ 寫成 $e^{r}$，只剩 $r_i - r_j$。",
        "nodes": [{"text": "贏的機率 ＝ $\\dfrac{p_i}{p_i + p_j}$", "sub": "$i$ 的實力占總和"}, {"text": "$\\sigma(2.5) \\approx 0.92$"}]}
code, out, html = render([MATH], math=True)
expect("含 LaTeX 的示意圖通過程式 B（含 LaTeX 語法檢查）", code == 0 and "1/1 張通過" in out and "katex" in html, out)
bad = json.loads(json.dumps(MATH)); bad["nodes"][0]["text"] = "壞算式 $\\frac{1}$"
code, out, _ = render([bad], math=True)
expect("故意做壞：LaTeX 語法錯誤 → 抓得到", code != 0 and "LaTeX" in out, out)
code, out, html = render([MATH], math=False)
expect("沒開 math 時 `$` 原樣（不載入 KaTeX）", "katex" not in html, "")

# 發布程式讀 spec 時也要把 `$...$` 轉純文字（2026-10-22：IG caption 曾出現「$r$」）
import tempfile as _tf
import ig_publish as IGP
with _tf.TemporaryDirectory() as _d:
    _b = Path(_d) / "_build"
    _b.mkdir()
    _spec = {"series": None, "concept": CONCEPT, "slides": [{"layout": "cover", "title": "封面", "body": "副標"},
             {"layout": "diagram", "kind": "flow", "title": "為什麼只看 $r$ 的差？", "body": "補充 $r_i - r_j$。", "nodes": [{"text": "一"}]}],
             "caption": {"first": "第一句", "nav": "", "hashtags": ["測試"]}}
    (_b / "spec.json").write_text(json.dumps(_spec, ensure_ascii=False), encoding="utf-8")
    _cap = IGP.load_pack(Path(_d))["caption"]
    expect("IG caption 沒有殘留的 $（LaTeX 已轉純文字）", "$" not in _cap and "為什麼只看 r 的差" in _cap, _cap)

# 發布文字不能殘留 LaTeX 記號（build_package.check_tex_leftovers；spec 開 math 才檢查）
import build_package as BP
expect("tex_leftovers：抓得到 $ 與 \\frac", W.tex_leftovers(r"贏的機率 $r$ 與 \frac{a}{b}") == ["$", "\\frac"], "")
expect("tex_leftovers：純文字沒有殘留", W.tex_leftovers("σ(r_i - r_j) 與 p_i/(p_i + p_j)") == [], "")
with _tf.TemporaryDirectory() as _d:
    _p = Path(_d)
    (_p / "ig").mkdir()
    (_p / "threads").mkdir()
    (_p / "_build").mkdir()
    (_p / "ig" / "post.md").write_text("乾淨的 caption", encoding="utf-8")
    BP.check_tex_leftovers({"math": True}, _p, _p / "_build")
    expect("沒有殘留時通過", True, "")
    (_p / "_build" / "alt-text.json").write_text('{"01.png": "替代文字 $r$"}', encoding="utf-8")
    BP.check_tex_leftovers({}, _p, _p / "_build")      # 沒開 math：不檢查
    expect("沒開 math 時不檢查", True, "")
    try:
        BP.check_tex_leftovers({"math": True}, _p, _p / "_build")
        expect("故意做壞：替代文字殘留 $ → 抓得到", False, "沒有擋下")
    except SystemExit as e:
        expect("故意做壞：替代文字殘留 $ → 抓得到", "alt-text.json" in str(e), str(e))

print("\n全部通過" if not fails else f"\n失敗 {len(fails)} 項：{fails}")
raise SystemExit(1 if fails else 0)
