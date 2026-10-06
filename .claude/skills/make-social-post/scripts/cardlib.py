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


def load_all_cards() -> list[Card]:
    return [parse_card(p) for p in sorted((WIKI / "wiki" / "concepts").glob("*.md"))]
