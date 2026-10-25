"""卡上主張附的參考圖（figures）的回歸測試：解析、程式 A 的 fig_refs 檢查、組包（審查材料與 caption 出處）、重製圖審查者的驗證。

測試資料：把 tests/fixtures/concept-wiki 複製到暫存目錄，在 jev-overview 的 c5 掛一張圖（不依賴真實的 submodule）。
用法（repo 根目錄）：uv run python tests/test_figures.py
"""
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FX = Path(__file__).resolve().parent / "fixtures"
SCRIPTS = ROOT / ".claude/skills/make-social-post/scripts"
TMP = Path(tempfile.mkdtemp())
WIKI = TMP / "concept-wiki"
shutil.copytree(FX / "concept-wiki", WIKI)
os.environ["DSO_CONCEPT_WIKI"] = str(WIKI)
os.environ["DSO_SERIES_DIR"] = str(FX / "series")
os.environ["DSO_STATE_DIR"] = str(TMP / "state")
sys.path.insert(0, str(SCRIPTS))
import cardlib as W   # noqa: E402

# 一張假的 PNG（內容只要固定即可）
PNG = b"\x89PNG\r\n\x1a\n" + b"fake-figure-for-test"
FIG_DIR = WIKI / "wiki" / "figures" / "jev"
FIG_DIR.mkdir(parents=True)
(FIG_DIR / "figure1.png").write_bytes(PNG)
SHA = hashlib.sha256(PNG).hexdigest()
CARD = WIKI / "wiki" / "concepts" / "jev-overview.md"
ORIG = CARD.read_text(encoding="utf-8")
FIG_YAML = ("  figures:\n  - file: figures/jev/figure1.png\n    article: jev\n    src: figure1.png\n"
            "    caption: 圖一 — Jev 的級聯流程。（來源：原始論文）\n    sha256: {sha}\n")
GOOD_A = json.loads((FX / "out/jev-teardown/jev-overview/spec.json").read_text(encoding="utf-8"))


def write_card(figures: str = "", status: str | None = None) -> None:
    """在 c5 掛 figures；status 可改成 pending_author_confirmation 測「圖跟著主張被排除」。"""
    m = re.search(r"(- id: c5\n.*?  importance: 5\n  status: )(\w+)\n", ORIG, re.S)
    assert m, "fixture 的 c5 結構變了，請更新測試"
    new = m.group(1) + (status or m.group(2)) + "\n" + figures
    CARD.write_text(ORIG[:m.start()] + new + ORIG[m.end():], encoding="utf-8")


def run(script, *args):
    r = subprocess.run(["uv", "run", "python", str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True, cwd=ROOT, env=os.environ)
    return r.returncode, r.stdout + r.stderr


def with_fig(s):
    s["slides"][2]["fig_refs"] = ["jev/figure1.png"]      # 第 3 張引用 c5


def spec_in(d: Path, spec: dict) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    p = d / "spec.json"
    p.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return p


def mut(fn):
    s = copy.deepcopy(GOOD_A)
    fn(s)
    return s


fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"\n{detail}"))


# ---- 解析 ----
write_card()                                   # 沒有 figures 的舊卡
claims = W.spec_claims({"concept": "jev-overview"})
check("舊卡（沒有 figures）照常解析：claim_figures 回空清單", all(W.claim_figures(c) == [] for c in claims.values()))
check("沒有 figures 的 slide_figures 回空", W.slide_figures(claims, ["c5"]) == {})

write_card(FIG_YAML.format(sha=SHA))
claims = W.spec_claims({"concept": "jev-overview"})
figs = W.slide_figures(claims, ["c5"])
check("有 figures：取得圖編號與實際路徑", list(figs) == ["jev/figure1.png"] and figs["jev/figure1.png"]["fig"]["path"].exists() and figs["jev/figure1.png"]["claims"] == ["c5"], str(figs))
check("sha256 一致時沒有警告", W.figure_hash_problem(figs["jev/figure1.png"]["fig"]) is None)
check("沒引用附圖的主張時不會取到圖", W.slide_figures(claims, ["c2"]) == {})

(FIG_DIR / "figure1.png").write_bytes(PNG + b"x")
check("sha256 不一致會被發現", "不一致" in (W.figure_hash_problem(figs["jev/figure1.png"]["fig"]) or ""))
(FIG_DIR / "figure1.png").write_bytes(PNG)

(FIG_DIR / "figure1.png").rename(FIG_DIR / "gone.png")
try:
    W.slide_figures(claims, ["c5"])
    check("缺檔要明確報錯（不靜默略過）", False, "沒有丟出例外")
except FileNotFoundError as e:
    check("缺檔要明確報錯（不靜默略過）", "圖不存在" in str(e), str(e))
check("沒用到附圖的主張時，缺檔不影響", W.slide_figures(claims, ["c2"]) == {})
(FIG_DIR / "gone.png").rename(FIG_DIR / "figure1.png")

write_card(FIG_YAML.format(sha=SHA), status="pending_author_confirmation")
claims_p = W.spec_claims({"concept": "jev-overview"})
check("pending 主張的圖跟著被排除", W.slide_figures(claims_p, ["c5"]) == {})
write_card(FIG_YAML.format(sha=SHA))

# ---- 程式 A ----
d = TMP / "good"
code, out = run("check_a.py", spec_in(d, mut(with_fig)))
check("程式 A：正確的 fig_refs 通過（測誤殺）", code == 0, out)
code, out = run("check_a.py", spec_in(TMP / "nofig", GOOD_A))
check("程式 A：沒有 fig_refs 的貼文照常通過", code == 0, out)
code, out = run("check_a.py", spec_in(TMP / "wrongslide", mut(lambda s: s["slides"][3].update(fig_refs=["jev/figure1.png"]))))   # 第 4 張沒引用 c5
check("程式 A：fig_refs 的圖不是這張引用的主張所附 → 抓得到", code == 1 and "fig_refs" in out, out)
code, out = run("check_a.py", spec_in(TMP / "nosuch", mut(lambda s: s["slides"][2].update(fig_refs=["jev/figure9.png"]))))
check("程式 A：fig_refs 指到不存在的圖 → 抓得到", code == 1 and "fig_refs" in out, out)
(FIG_DIR / "figure1.png").write_bytes(PNG + b"x")
code, out = run("check_a.py", spec_in(TMP / "badsha", mut(with_fig)))
check("程式 A：圖檔被改過（sha256 不符）→ 抓得到", code == 1 and "sha256" in out, out)
(FIG_DIR / "figure1.png").write_bytes(PNG)
(FIG_DIR / "figure1.png").rename(FIG_DIR / "gone.png")
code, out = run("check_a.py", spec_in(TMP / "missing", mut(with_fig)))
check("程式 A：圖檔不存在 → 抓得到", code == 1 and "圖不存在" in out, out)
(FIG_DIR / "gone.png").rename(FIG_DIR / "figure1.png")
write_card(FIG_YAML.format(sha=SHA), status="pending_author_confirmation")
code, out = run("check_a.py", spec_in(TMP / "pending", mut(with_fig)))
check("程式 A：引用 pending 主張（圖也不能用）→ 抓得到", code == 1 and "不得使用" in out, out)
write_card(FIG_YAML.format(sha=SHA))

# ---- 組包：審查材料與 caption 出處 ----
d = TMP / "pack"
sp = spec_in(d, mut(with_fig))
code, out = run("build_package.py", sp)
rev = (d / "figure-review.md") if (d / "figure-review.md").exists() else d / "_build" / "figure-review.md"
text = rev.read_text(encoding="utf-8") if rev.exists() else ""
check("組包：產生 figure-review.md，含原圖路徑、圖說、主張與重製圖路徑", code == 0 and str(FIG_DIR / "figure1.png") in text and "不是主張" in text and "c5" in text and "03.png" in text, out + text)
cap = (d / "ig" / "post.md").read_text(encoding="utf-8") if (d / "ig" / "post.md").exists() else ""
check("組包：caption 自動註明圖片出處（改繪自原始論文，含圖號）", "圖片來源：第 3 張（圖一）改繪自原始論文的圖表" in cap, cap[-400:])
d2 = TMP / "pack2"
code, out = run("build_package.py", spec_in(d2, GOOD_A))
check("組包：沒有 fig_refs 的貼文不產生 figure-review.md、caption 沒有出處行", code == 0 and not (d2 / "figure-review.md").exists() and "圖片來源" not in (d2 / "ig" / "post.md").read_text(encoding="utf-8"), out)

# ---- 重製圖審查者的驗證 ----
def fig_json(**kw):
    item = {"what": "圖上的一個數字", "reproduced": "35.7", "original_position": "第二列第二欄", "original": "35.7", "in_claim": "", "verdict": "一致"}
    item.update(kw.pop("item", {}))
    s = {"slide": 3, "items": [item], "errors": kw.pop("errors", [])}
    p = TMP / "fig.json"
    p.write_text(json.dumps({"slides": [s] if not kw.get("empty") else []}, ensure_ascii=False), encoding="utf-8")
    return p


code, out = run("verify_figure.py", sp, fig_json())
check("重製圖審查：全部一致 → 通過（測誤殺）", code == 0, out)
code, out = run("verify_figure.py", sp, fig_json(empty=True))
check("重製圖審查：有 fig_refs 的張沒被審到 → 退回", code == 1 and "沒被審到" in out, out)
code, out = run("verify_figure.py", sp, fig_json(item={"verdict": "不一致", "reproduced": "35.9"}))
check("重製圖審查：項目判不一致 → 退回", code == 1 and "不一致" in out, out)
code, out = run("verify_figure.py", sp, fig_json(item={"verdict": "原圖沒有"}))
check("重製圖審查：項目判原圖沒有 → 退回", code == 1, out)
code, out = run("verify_figure.py", sp, fig_json(item={"original_position": ""}))
check("重製圖審查：沒寫原圖位置 → 退回（不准目測估算）", code == 1 and "原圖位置" in out, out)
code, out = run("verify_figure.py", sp, fig_json(errors=["範圍被放大"]))
check("重製圖審查：blocker 錯誤 → 退回", code == 1 and "範圍被放大" in out, out)
code, out = run("verify_figure.py", sp, fig_json(item={"verdict": "主張沒寫"}))
check("重製圖審查：主張沒寫只記錄、不擋（交人對照）", code == 0 and "主張沒寫" in out, out)

code, out = run("verify_figure.py", sp, fig_json(item={"verdict": "僅來自主張", "original_position": "", "original": "原圖沒畫"}))
check("重製圖審查：僅來自主張不需原圖位置、不擋", code == 0, out)

shutil.rmtree(TMP, ignore_errors=True)
print(f"\n{'全部通過' if not fails else f'{fails} 項失敗'}")
sys.exit(1 if fails else 0)
