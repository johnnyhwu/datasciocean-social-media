---
name: make-social-post
description: 把 concept-wiki 的觀念卡做成 IG 輪播與 Threads 串文的發布包，並用官方 API 發布到 IG 與 Threads（Stage 2）。使用者要「做貼文」「產生 IG／Threads」「為某個觀念出貼文」「規劃系列」「寫 hook」「渲染投影片」「審貼文」「發布到 IG／Threads」「記錄已發布」「下一則貼文」時使用。涵蓋選觀念、系列規劃、hook、內容規格 JSON、程式 A、渲染與程式 B、忠實者與讀者審查、批次檢查、發布包、IG 與 Threads 發佈、寫回狀態。新系列的視覺設計用 design-series-visuals。
---

# make-social-post：觀念卡 → 發布包 → 發布到 IG 與 Threads

輸入 `concept-wiki/` submodule 裡的觀念卡，輸出 `out/<series>/<concept>/` 發布包，經人確認後用官方 API 發布，並寫回狀態。**規則（只讀卡、卡是內容上限、發布要經人確認、憑證只放 `.env`…）全部在 `CLAUDE.md`，這裡不重複；違反任何一條就是做錯。**

## 開始前（新 session 從這裡起手，每次都做）

1. `git submodule update --remote`（卡要是最新的）。第一次 clone 用 `git submodule update --init --remote`。
2. `uv sync`；Chromium 在 repo 內，沒有就 `PLAYWRIGHT_BROWSERS_PATH=$PWD/.playwright-browsers uv run playwright install chromium`（細節見 `references/setup.md`）。腳本一律 `uv run python .claude/skills/make-social-post/scripts/<name>.py`。
3. **看現況**：`state.py status`（每個觀念各格式是 `not_tried`／`ready`／`published`、存量），再看 `out/README.md`（待發布與各系列狀態）。
4. **（新系列／規劃時）** 跑 `series_deps.py <系列 id>` 並**一定要問人哪些卡要合併**（`references/batch-and-publish.md` §1）；成員定案後在 `series.md` 加 `members_locked: true`，再發第 1 則。
4b. **決定這次做哪一則**：照系列檔 `series/<id>/series.md` 的 `members` 順序，找第一個還是 `not_tried` 的觀念；這是預設，要不要照做由人決定。
5. 要做的觀念，**只讀它的卡**（`concept-wiki/wiki/concepts/<id>.md`），不讀 blog。同時讀 `concept-wiki/docs/card-format.md`（卡格式與 status 語意）。
6. 如果這次要**發布**，先看 `references/publish-flow.md` 的「發文前的前提」。

## 流程

```
[1] 選觀念、系列規劃 → [2] hook 候選（人挑）→ [3] 寫內容規格 spec.json
 → [4] 程式 A（check_a）→ [5] 渲染 + 程式 B（render）→ [6] 組發布文字（build_package）
 → [7] 自檢 + 審查：忠實者（嚴格）、讀者（預設一般讀者，要看圖）、編輯（只給建議，要看圖）→ [8] 批次層檢查（batch_check）
 → [9] 人最後確認 → [10] state.py ready → [11] 發布到 IG 與 Threads（人確認後）→ 寫回狀態
```

**先渲染、先過程式 B，再讓 subagent 審查**：版面檢查若逼撰寫者縮短文字，已通過的審查會作廢。subagent 審的是版面已定案的最終文字。程式 A、B 不算輪數，撰寫者可以自己先跑到通過。

| 步驟 | 做什麼 | 細節 |
|---|---|---|
| 1 | 選觀念、決定獨立或系列、系列檔 | `references/batch-and-publish.md` §1–3 |
| 2 | 5～6 個大膽的 hook 候選（至少 3 種樣態），最多一次 haiku 讀者參考，**用純文字列出完整候選讓人挑（不用 AskUserQuestion）** | `references/hooks.md` |
| 3 | **先做版型規劃**（每張選好版型、圖上術語在哪張定義，`references/ig-carousel.md` §0；**每張帶數字的圖先用 `chart-thinking` skill 想過：要比什麼、圖有沒有直接支撐主標**），再寫 `out/<series>/<concept>/_build/spec.json`：投影片、Threads、caption、每個區塊標引用的 claim id | `references/spec-json.md`、`references/ig-carousel.md`、`references/threads-and-caption.md`、`references/anchor-writing-rules.md` |
| 4 | `check_a.py <spec.json>`，ERROR 清零 | `references/program-a.md` |
| 5 | `render.py <spec.json>`，程式 B 全過；`contact_sheet.py <發布包資料夾>` 拼縮圖；**自己看一次渲染後的 PNG** | `references/program-b.md` |
| 6 | （在 `contact_sheet.py` 之後）`build_package.py <spec.json>`：產生人看的 `README.md`、`ig/post.md`、`threads/post.md`、審查用的 `_build/post-with-refs.md`／`post-reader.md`，並更新 `out/README.md` 索引 | `references/threads-and-caption.md` |
| 7 | **先照 `references/self-check.md` 自檢**，再派忠實者、讀者（一般讀者，附圖）、編輯（附圖）；`verify_faithful.py`、`verify_reader.py` | `references/review-loop.md`、`references/self-check.md` |
| 8 | `batch_check.py <spec>...`（參數順序 = 預計發文順序） | `references/batch-and-publish.md` §4 |
| 9–10 | 給人看貼文 `README.md`（含縮圖）、`ig/post.md`、`threads/post.md`，確認後 `state.py ready <觀念> <格式> <發布包>`（兩個格式各一次） | `references/batch-and-publish.md` §5–6 |
| 11 | **發布**：`prepare` → push `ig/jpg/` → IG `preflight` → IG dry-run → 人說「發」→ `--confirm` → Threads dry-run → 人說「發」→ `--confirm`；成功後自動寫回 state | **`references/publish-flow.md`**（照做）、`references/instagram-publish.md`、`references/threads-publish.md` |

第一次是新系列時，先用 `design-series-visuals` 把視覺哲學與各版型的樣張做出來、**由人審過**才量產。系列已有模板就直接用，同一系列的所有貼文用同一版模板。

## 新增格式（Reels、Shorts…）

格式是插件：每種格式各自定義結構規則、寫作規則、審查清單、輸出欄位；格式之間共用 hook 候選、引用標記機制、回歸測試。新格式加進來時，所有觀念的該格式自動視為 `not_tried`（`state/` 裡沒有該格式的鍵就是 not_tried），成為候選。觀念卡不用改。目前只有 `ig_carousel` 與 `threads_thread`。

## 腳本（`scripts/`）

| 腳本 | 用途 |
|---|---|
| `check_a.py` | 程式 A：引用標記、比較詞、限定條件、數字、字數、重疊率、用語… |
| `render.py` | 渲染引擎與程式 B：spec.json + 系列模板 → 1080×1350 PNG，並做版面檢查，寫 `_build/checks-b.json`、`alt-text.json` |
| `build_package.py` | 由 spec.json 產生人看的入口（`README.md`、`ig/post.md`、`threads/post.md`）、審查用貼文文字，並更新 `out/README.md` 與系列索引 |
| `contact_sheet.py` | 把投影片拼成縮圖總覽 |
| `verify_faithful.py`、`verify_reader.py` | 驗證忠實者／讀者的 JSON：引用逐字出自卡或貼文、分級、陷阱題 |
| `batch_check.py` | 批次層檢查：相鄰 hook 樣態、相鄰系列色、模板 hash、標題一致、存量 |
| `ig_publish.py`、`ig_api.py` | IG 官方 API 發佈：prepare／preflight／publish（dry-run 預設，`--confirm` 才發）、token 管理 |
| `threads_publish.py`、`threads_api.py` | Threads 官方 API 發佈整串：publish／rollback／delete／token-info（dry-run 預設；中途失敗可續發） |
| `publish_common.py`、`hosting.py` | 兩個平台共用：`.env` 讀寫、token 效期與自動 refresh、JPEG 驗證；圖片託管介面（GitHub raw 網址） |
| `series_deps.py` | 系列規劃：列出該合併成一則的候選（輔助，不是偵測器；規劃時一定要問人） |
| `state.py` | 各觀念各格式的狀態（`not_tried`／`ready`／`published`／`unsuitable`）、發布紀錄、回補清單（`state/`） |
| `cardlib.py` | 共用：唯讀解析觀念卡、系列與發布包路徑、文字正規化與逐字比對 |

`render.py`、`build_package.py` 對**已發布**的貼文預設拒絕，要重做才加 `--force`。

改了任何腳本或審查流程，跑 `CLAUDE.md`「工作方式」列的全部回歸測試。

## 派發 subagent 的做法

- 提示詞放在 `references/*-prompt.md`；派發訊息只給提示詞路徑與變數（檔案路徑），不貼全文。審查者看不到撰寫者推理，每輪用全新 subagent。
- 並行上限 20；派完用檔案數核對應到／實到。
- 審查產出（JSON）放暫存目錄，不進 repo。
