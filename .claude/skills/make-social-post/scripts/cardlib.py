"""共用函式：專案路徑、參數、讀觀念卡（唯讀）、文字正規化與逐字比對。

觀念卡由 `datasciocean-concept-wiki` repo 產生，本 repo 以 submodule（預設路徑 `concept-wiki/`）讀取，
**只讀不寫**。卡的格式契約：concept-wiki/docs/card-format.md。這裡只實作「讀」所需的最小部分，
刻意不依賴 concept-wiki 裡的程式碼，兩個 repo 只靠卡格式耦合。

要換位置（例如測試）：環境變數 DSO_CONCEPT_WIKI 指向 concept-wiki 的根目錄；DSO_SERIES_DIR 指向系列檔目錄。
"""
from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml


def project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "CLAUDE.md").exists() and (parent / "config" / "params.yaml").exists():
            return parent
    raise RuntimeError("找不到專案根目錄（需有 CLAUDE.md 與 config/params.yaml）")


ROOT = project_root()
WIKI = Path(os.environ.get("DSO_CONCEPT_WIKI") or ROOT / "concept-wiki")
# 系列檔目錄；DSO_SERIES_DIR 只給測試用（指向 tests/fixtures/series）
SERIES_DIR = Path(os.environ.get("DSO_SERIES_DIR") or ROOT / "series")
# 獨立貼文（沒有系列）各有自己的視覺：standalone/<觀念 id>/ 放 standalone.md（風格、色）、philosophy.md、templates/、sketches/
STANDALONE_DIR = Path(os.environ.get("DSO_STANDALONE_DIR") or ROOT / "standalone")


# state/ 目錄；DSO_STATE_DIR 只給測試用
STATE_DIR = Path(os.environ.get("DSO_STATE_DIR") or ROOT / "state")


def published_formats(concept: str) -> list[str]:
    """這個觀念已經發布的格式（state/<concept>.yaml）。併入別張卡的（merged_into）也算。"""
    f = STATE_DIR / f"{concept}.yaml"
    if not f.exists():
        return []
    d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    return [k for k, v in (d.get("formats") or {}).items() if (v or {}).get("status") == "published"]


def guard_published(doc: dict, force: bool = False) -> None:
    """已發布的貼文，渲染與組包預設拒絕（會覆寫已發布貼文在本機的圖與文字檔）；確定要重做才加 --force。"""
    pub = published_formats(doc["concept"])
    if pub and not force:
        raise SystemExit(f"拒絕：{doc['concept']} 已發布（{', '.join(pub)}），重新渲染或組包會覆寫它在本機的圖與文字檔。"
                         "確定要重做（例如改版型後讓 template hash 一致）請加 --force，並先確認只有預期的檔案會變。")


def series_lock_warning(series_id: str | None, concept: str) -> str | None:
    """系列的第一則發布前，成員清單（含合併）必須定案：IG 系列地圖發布後改不了。series.md 要有 members_locked: true。"""
    if not series_id or not series_file(series_id).exists():
        return None
    m = re.match(r"^---\n(.*?)\n---", series_file(series_id).read_text(encoding="utf-8"), re.S)
    s = yaml.safe_load(m.group(1)) or {}
    if s.get("members_locked"):
        return None
    for mem in s.get("members") or []:
        if published_formats(mem["concept"]):
            return None      # 已有成員發布過（沒有鎖定欄位的舊系列），不再提醒
    return (f"系列 {series_id} 的成員清單還沒定案：第一則發布後，IG 系列地圖的圖就改不了。"
            "請先確認成員與合併都定案，並在 series/<id>/series.md 加 members_locked: true")


def series_dir(sid: str) -> Path:
    """一個系列的所有東西都在 series/<id>/：series.md、philosophy.md、templates/。"""
    return SERIES_DIR / sid


def standalone_dir(concept: str) -> Path:
    return STANDALONE_DIR / concept


def series_file(sid: str) -> Path:
    return series_dir(sid) / "series.md"


def series_ids() -> list[str]:
    return sorted(p.name for p in SERIES_DIR.iterdir() if (p / "series.md").exists()) if SERIES_DIR.exists() else []


def build_dir(spec_path: Path) -> Path:
    """機器用的中間檔都在發布包的 _build/（spec.json、checks-b.json、html/…）。"""
    return Path(spec_path).resolve().parent


def pack_dir(spec_path: Path) -> Path:
    """發布包資料夾：spec 在 <pack>/_build/spec.json 時是上一層；測試用的暫存資料夾直接放 spec，就是同一層。"""
    b = build_dir(spec_path)
    return b.parent if b.name == "_build" else b


def load_params() -> dict:
    return yaml.safe_load((ROOT / "config" / "params.yaml").read_text(encoding="utf-8"))


def background_terms_path() -> Path:
    """背景詞清單由 concept-wiki 維護（人維護），這裡只讀。"""
    return WIKI / "config" / "background-terms.md"


# ---------------------------------------------------------------- 文字正規化與逐字比對
# 與 concept-wiki 的 wikilib.normalize 同一套規則（契約 §8）：NFKC、去 markdown 標記與引號、去空白。

_QUOTE_MARKS = "“”\"'‘’「」『』"
_SHORTCODE = re.compile(r"\{\{[<%].*?[>%]\}\}")


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text)
    t = _SHORTCODE.sub("", t)
    lines = []
    for line in t.splitlines():
        s = line.strip()
        if re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?", s):
            continue
        if s.startswith("|"):
            s = s.strip("|")
        s = re.sub(r"^(#{1,6}\s+|>\s*|[-*+]\s+|\d+\.\s+)", "", s)
        lines.append(s)
    t = "\n".join(lines)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("**", "").replace("__", "").replace("`", "")
    t = re.sub(r"(?<!\w)\*(?=\S)|(?<=\S)\*(?!\w)", "", t)
    for ch in _QUOTE_MARKS:
        t = t.replace(ch, "")
    return re.sub(r"\s+", "", t)


_ELLIPSIS = re.compile(r"…+|\.{3,}")


def quote_fragments(quote: str) -> list[str]:
    """引用中的「…」代表省略；每個片段都必須逐字出現且依序。"""
    return [f for f in (normalize(p) for p in _ELLIPSIS.split(quote)) if f]


def quote_in_text(quote: str, text_norm: str) -> bool:
    pos = 0
    frags = quote_fragments(quote)
    if not frags:
        return False
    for f in frags:
        k = text_norm.find(f, pos)
        if k == -1:
            return False
        pos = k + len(f)
    return True


# ---------------------------------------------------------------- 觀念卡（唯讀）

@dataclass
class Card:
    path: Path
    front: dict
    claims: list[dict]
    errors: list[str] = field(default_factory=list)


_FENCE = re.compile(r"```ya?ml\s*\n(.*?)\n```", re.S)


def parse_card(path: Path) -> Card:
    """卡 = YAML frontmatter + 一個含 `claims:` 的 ```yaml 區塊（契約 §3）。"""
    if not Path(path).exists():
        raise FileNotFoundError(
            f"找不到觀念卡 {path}。concept-wiki submodule 是否已初始化？"
            "（git submodule update --init --remote；或設 DSO_CONCEPT_WIKI）")
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return Card(Path(path), {}, [], ["缺少 YAML frontmatter"])
    front = yaml.safe_load(m.group(1)) or {}
    claims: list[dict] = []
    found = False
    for fence in _FENCE.finditer(m.group(2)):
        data = yaml.safe_load(fence.group(1)) or {}
        if isinstance(data, dict) and "claims" in data:
            found = True
            claims = data.get("claims") or []
    return Card(Path(path), front, claims, [] if found else ["找不到含 claims 的 ```yaml 區塊"])


def spec_claims(doc: dict) -> dict[str, dict]:
    """一則貼文引用得到的所有主張。主卡（doc["concept"]）用裸 id（c1）；併入的卡（doc["also_concepts"]）
    用「卡id:cN」，例如 confidence-three-metrics:c3。限定條件標記也一樣加前綴（卡id:c3#1）。"""
    out = {c["id"]: c for c in parse_card(WIKI / "wiki" / "concepts" / f"{doc['concept']}.md").claims}
    for other in doc.get("also_concepts") or []:
        for c in parse_card(WIKI / "wiki" / "concepts" / f"{other}.md").claims:
            out[f"{other}:{c['id']}"] = c
    return out


# ---------------------------------------------------------------- 主張附的參考圖（契約 card-format.md §4.2）
# 圖只是參考，不是證據；貼文要用必須重製（由程式畫，不直接貼原圖）。這裡只負責「找到圖、確認沒被動過」。

def figure_path(fig: dict) -> Path:
    """圖檔實際路徑：<wiki>/wiki/<file>（file 相對於 wiki/）。"""
    return WIKI / "wiki" / fig["file"]


def figure_id(fig: dict) -> str:
    """spec 的 fig_refs 用的圖編號：<article>/<src>，例如 sag/figure1.png。"""
    return f"{fig['article']}/{fig['src']}"


def claim_figures(claim: dict) -> list[dict]:
    """這條主張附的圖（沒有就空清單；舊卡沒有 figures 欄位照常）。每筆多一個 `path`；檔案不存在要明確報錯，不靜默略過。"""
    out = []
    for fig in claim.get("figures") or []:
        p = figure_path(fig)
        if not p.exists():
            raise FileNotFoundError(f"主張 {claim.get('id')} 附的圖不存在：{p}（concept-wiki submodule 是否更新到有 wiki/figures/ 的版本？）")
        out.append({**fig, "path": p})
    return out


def figure_hash_problem(fig: dict) -> str | None:
    """檔案 sha256 與卡上記錄不一致就回傳訊息（代表 submodule 內容被改過）；一致回 None。"""
    import hashlib
    h = hashlib.sha256(figure_path(fig).read_bytes()).hexdigest()
    return None if h == fig.get("sha256") else f"{figure_id(fig)} 的 sha256 與卡上記錄不一致（檔案被改過？）"


def slide_figures(claims: dict[str, dict], refs: list[str]) -> dict[str, dict]:
    """一張投影片引用的主張所附的圖：{圖編號: {"fig": 圖資料（含 path）, "claims": [附這張圖的主張 id]}}。
    只看這張引用的主張（缺檔只在用到時報錯）；pending_author_confirmation 的主張，它的圖不收（圖跟著主張被排除）。"""
    out: dict[str, dict] = {}
    for cid in refs:
        c = claims.get(cid)
        if not c or c.get("status") == "pending_author_confirmation":
            continue
        for fig in claim_figures(c):
            out.setdefault(figure_id(fig), {"fig": fig, "claims": []})["claims"].append(cid)
    return out


def load_all_cards() -> list[Card]:
    return [parse_card(p) for p in sorted((WIKI / "wiki" / "concepts").glob("*.md"))]


# ---------------------------------------------------------------- LaTeX 標記（spec 的 `$...$`，2026-10-22）
# 圖上的數學符號與算式用 `$...$` 寫 LaTeX（頂層 `"math": true` 才啟用，由 render.py 用 KaTeX 排版）。
# 其他所有吃文字的地方（程式 A、審查用文字、README、alt text）看到的都是下面轉出來的純文字。
_TEX_SYM = {r"\sigma": "σ", r"\approx": "≈", r"\div": "÷", r"\times": "×", r"\cdot": "·", r"\ln": "ln", r"\log": "log",
            r"\le": "≤", r"\ge": "≥", r"\neq": "≠", r"\pm": "±", r"\,": "", r"\;": " ", r"\!": "", r"\left": "", r"\right": ""}


def _tex_one(t: str) -> str:
    t = re.sub(r"\\(?:text|mathcal|mathbb|mathrm|mathbf)\{([^{}]*)\}", r"\1", t)
    for _ in range(4):                      # 上下標先展開（內層先），分數的 {} 裡就沒有巢狀大括號
        t = re.sub(r"\^\{([^{}]*)\}", lambda m: "^" + (m.group(1) if len(m.group(1)) == 1 else f"({m.group(1)})"), t)
        t = re.sub(r"_\{([^{}]*)\}", lambda m: "_" + (m.group(1) if len(m.group(1)) == 1 else f"({m.group(1)})"), t)
    for _ in range(6):                      # 由內往外展開分數
        t2 = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}",
                    lambda m: (m.group(1) if re.fullmatch(r"[\w.]+", m.group(1)) else f"({m.group(1)})") + "/"
                    + (m.group(2) if re.fullmatch(r"[\w.]+", m.group(2)) else f"({m.group(2)})"), t)
        if t2 == t:
            break
        t = t2
    for k in sorted(_TEX_SYM, key=len, reverse=True):
        t = t.replace(k, _TEX_SYM[k])
    return re.sub(r"[{}]", "", t).strip()


def tex_plain(s: str) -> str:
    """把字串裡的 `$...$` 轉成純文字（σ、÷、分數寫成 a/b、上下標寫成 ^ 與 _），其餘不動。"""
    return re.sub(r"\$([^$]+)\$", lambda m: _tex_one(m.group(1)), s) if "$" in s else s


def tex_leftovers(text: str) -> list[str]:
    """文字裡殘留的 LaTeX 記號（`$`、`\\frac` 這類反斜線指令）；發布文字與審查文字不該有。"""
    return sorted(set(re.findall(r"\$|\\[A-Za-z]+", text)))


def untex(obj):
    """遞迴把 spec 裡所有字串的 `$...$` 轉成純文字（給程式 A 與發布文字用）。"""
    if isinstance(obj, str):
        return tex_plain(obj)
    if isinstance(obj, list):
        return [untex(x) for x in obj]
    if isinstance(obj, dict):
        return {k: untex(v) for k, v in obj.items()}
    return obj
