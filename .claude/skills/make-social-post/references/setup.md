# 環境與安裝

**所有東西都限縮在 repo 內，不污染本機。**（使用者要求：uv 與其他工具都不得裝到全域。）

| 項目 | 位置 | 設定 |
|---|---|---|
| Python 依賴（pyyaml、playwright、pillow） | `.venv/` | `pyproject.toml`、`uv.lock` |
| uv 快取 | `.uv-cache/` | `pyproject.toml` 的 `[tool.uv] cache-dir` |
| Chromium（無頭瀏覽器，約 557MB） | `.playwright-browsers/` | `render.py` 啟動時自己設 `PLAYWRIGHT_BROWSERS_PATH` |
| 字型 Noto Sans CJK TC（Regular、Bold，OFL 授權） | `assets/fonts/` | 內嵌進每張投影片，不依賴系統字型 |

以上目錄都在 `.gitignore`（字型除外，授權允許隨 repo 散布）。

## 第一次在新機器上

```
git submodule update --init --remote      # concept-wiki（觀念卡）
uv sync                                    # 建 .venv，依 uv.lock 安裝
PLAYWRIGHT_BROWSERS_PATH=$PWD/.playwright-browsers uv run playwright install chromium
```

## 之後每次

`git submodule update --remote`，然後直接用 `uv run python .claude/skills/make-social-post/scripts/<name>.py`。

## 驗證環境

```
uv run python tests/test_check_a.py          # 程式 A 回歸，需要 concept-wiki 已初始化
uv run python tests/test_state_and_batch.py
uv run python .claude/skills/make-social-post/scripts/render.py out/<series>/<concept>/_build/spec.json
```

渲染是確定性的：同一份 spec.json 與同一版模板，重渲染的 PNG 與既有發布包逐位元相同（重構時用來驗證搬家沒有改壞任何東西）。

## 已知限制

- `render.py` 的版型幾何（海浪、測深圖的水面線與刻度、系列色對應 `SERIES_COLORS`）有一部分寫在程式裡，不只在 HTML 模板；新系列若用不同的系列色或新版型，要同時改 `render.py` 與 `series/<id>/templates/`，詳見 `design-series-visuals` skill。
- 測深圖最多 3 條繩（`chart_sounding`），橫條圖版型沒有條數預檢。
- 只在 1080 寬的畫面檢查過；手機實機顯示（含個人頁面縮圖左右各裁約 34px 的假設）還沒驗證。
