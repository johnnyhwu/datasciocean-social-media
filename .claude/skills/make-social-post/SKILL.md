---
name: make-social-post
description: 把 concept-wiki 的觀念卡做成 IG 輪播與 Threads 串文的發布包（Stage 2）。使用者要「做貼文」「產生 IG／Threads」「為某個觀念出貼文」「規劃系列」「寫 hook」「渲染投影片」「審貼文」「記錄已發布」時使用。涵蓋選觀念、系列規劃、hook、內容規格 JSON、程式 A、渲染與程式 B、忠實者與讀者審查、批次檢查、發布包、寫回狀態。新系列的視覺設計用 design-series-visuals。
---

# make-social-post：觀念卡 → IG 輪播與 Threads 串文

輸入 `concept-wiki/` submodule 裡的觀念卡，輸出 `out/<series>/<concept>/` 發布包。**不自動發布**，發布由人手動做；系統只產出發布包與待辦清單，並在人發布後寫回狀態。

## 開始前（每次都做）

1. `git submodule update --remote`（卡要是最新的；新增或改過的卡才會出現）。第一次 clone 用 `git submodule update --init --remote`。
2. `uv sync`；Chromium 在 repo 內，沒有就 `PLAYWRIGHT_BROWSERS_PATH=$PWD/.playwright-browsers uv run playwright install chromium`（細節見 `references/setup.md`）。腳本一律 `uv run python .claude/skills/make-social-post/scripts/<name>.py`。
3. `uv run python .claude/skills/make-social-post/scripts/state.py status`：哪些觀念、哪些格式還是 `not_tried`、存量（ready）有幾則。
4. 要做的觀念，**只讀它的卡**（`concept-wiki/wiki/concepts/<id>.md`）。**不讀 blog**。同時讀 `concept-wiki/docs/card-format.md`（卡格式與 status 語意）。

## 鐵則（違反就是做錯）

- **卡是內容上限，貼文是卡的子集。** 不得加入卡上沒有的判斷、數字、比較詞、缺席型主張。卡上沒有的內容，貼文就寫不出來；寫不出就刪那張投影片（或標該格式 `unsuitable`），**不退回 Stage 1、不改卡**。
- `pending_author_confirmation` 的主張**一律不用**；`author_confirmed` 的寫法取保守的一邊。
- 每個數字都要有比較對象；錨點類型決定寫法（`references/anchor-writing-rules.md`）；用了某條主張，它的限定條件必須一起出現。
- 圖片由程式產生，LLM 只產出內容規格 JSON。**不用 AI 生圖。**
- 貼文不提 podcast、不加 AI 揭露。不使用「留言關鍵字換連結」。
- 存量不夠時暫停發文，不降低審查標準。
- **一張觀念卡 = 一則 post**（IG 輪播與 Threads 串文是同一則的兩種格式）。請人拍板時用白話說清楚：是什麼、選了會怎樣、代價、我的建議。做完一個階段，主動列出人接下來要注意或完成的事。
- 不確定就停下來問人：hook 要人挑、版型樣張要人審、最後確認要人看、審查者與撰寫者的爭議要交給人。

## 流程

```
[1] 選觀念、系列規劃 → [2] hook 候選（人挑）→ [3] 寫內容規格 spec.json
 → [4] 程式 A（check_a）→ [5] 渲染 + 程式 B（render）→ [6] 組發布文字（build_package）
 → [7] 審查：忠實者（嚴格）、工程師讀者、編輯（只給建議）→ [8] 批次層檢查（batch_check）
 → [9] 人最後確認 → [10] 發布包與待辦清單 → 人手動發布 → [11] 寫回狀態與回補清單
```

**先渲染、先過程式 B，再讓 subagent 審查**：版面檢查若逼撰寫者縮短文字，已通過的審查會作廢。subagent 審的是版面已定案的最終文字。程式 A、B 不算輪數，撰寫者可以自己先跑到通過。

| 步驟 | 做什麼 | 細節 |
|---|---|---|
| 1 | 選觀念、決定獨立或系列、系列檔 | `references/batch-and-publish.md` §1–3 |
| 2 | 5～6 個大膽的 hook 候選（至少 3 種樣態），最多一次 haiku 讀者參考，**用 AskUserQuestion 讓人挑** | `references/hooks.md` |
| 3 | 寫 `out/<series>/<concept>/_build/spec.json`：投影片、Threads、caption、每個區塊標引用的 claim id | `references/spec-json.md`、`references/ig-carousel.md`、`references/threads-and-caption.md`、`references/anchor-writing-rules.md` |
| 4 | `check_a.py <spec.json>`，ERROR 清零 | `references/program-a.md` |
| 5 | `render.py <spec.json>`，程式 B 全過；`contact_sheet.py <發布包資料夾>` 拼縮圖；**自己看一次渲染後的 PNG** | `references/program-b.md` |
| 6 | （在 `contact_sheet.py` 之後）`build_package.py <spec.json>`：產生人看的 `README.md`、`ig/post.md`、`threads/post.md`，與審查用的 `_build/post-with-refs.md`（忠實者）、`_build/post-reader.md`（讀者與編輯，不含引用編號），並更新 `out/README.md` 索引 | `references/threads-and-caption.md` |
| 7 | **先照 `references/self-check.md` 自檢**，再派忠實者、工程師讀者、編輯；`verify_faithful.py`、`verify_reader.py` | `references/review-loop.md`、`references/self-check.md` |
| 8 | `batch_check.py <spec>...`（參數順序 = 預計發文順序） | `references/batch-and-publish.md` §4 |
| 9–10 | 給人看縮圖與文字，確認後 `state.py ready`（發布前後待辦在貼文的 `README.md`） | `references/batch-and-publish.md` §5–6 |
| 11 | 發布：IG 可用官方 API（`ig_publish.py prepare` → push `ig/jpg/` → `preflight`（建好 container 但不發佈）→ `publish` dry-run → 人確認 → `--confirm`（沿用預檢），成功後自動 `state.py record`）；Threads 與 API 之外的情況由人手動發，回報網址與時間 → `state.py record` | `references/instagram-publish.md`、`references/batch-and-publish.md` §7 |

第一次是新系列時，先用 `design-series-visuals` 把視覺哲學與六種版型的樣張做出來、**由人審過**才量產。系列已有模板就直接用，同一系列的所有貼文用同一版模板。

## 新增格式（Reels、Shorts…）

格式是插件：每種格式各自定義結構規則、寫作規則、審查清單、輸出欄位；格式之間共用 hook 候選、引用標記機制、回歸測試。新格式加進來時，所有觀念的該格式自動視為 `not_tried`（`state/` 裡沒有該格式的鍵就是 not_tried），成為候選。觀念卡不用改。目前只有 `ig_carousel` 與 `threads_thread`。

## 腳本（`scripts/`）

| 腳本 | 用途 |
|---|---|
| `check_a.py` | 程式 A：引用標記、比較詞、限定條件、數字、字數、重疊率… |
| `render.py` | 渲染引擎與程式 B：spec.json + 系列模板 → 1080×1350 PNG，並做版面檢查，寫 `checks-b.json`、`alt-text.json` |
| `build_package.py` | 由 spec.json 產生人看的入口（`README.md`、`ig/post.md`、`threads/post.md`）、審查用貼文文字，並更新 `out/README.md` 與系列索引 |
| `verify_faithful.py` | 驗證忠實者 JSON：引用逐字出自卡、分級（blocker 與 minor） |
| `verify_reader.py` | 驗證工程師讀者 JSON：引用逐字出自貼文、陷阱題 |
| `contact_sheet.py` | 把投影片拼成縮圖總覽 |
| `batch_check.py` | 批次層檢查：相鄰 hook 樣態、相鄰系列色、模板 hash、標題一致、存量 |
| `ig_publish.py`、`ig_api.py`、`hosting.py` | IG 官方 API 發佈（dry-run 預設、`--confirm` 才發）、API 客戶端、圖片託管介面（GitHub raw 網址） |
| `state.py` | 各觀念各格式的狀態、發布紀錄、回補清單（`state/`） |
| `cardlib.py` | 共用：唯讀解析觀念卡、文字正規化與逐字比對 |

改了任何腳本或審查流程，跑兩份回歸測試：`uv run python tests/test_check_a.py`、`uv run python tests/test_state_and_batch.py`。

## 派發 subagent 的做法

- 提示詞放在 `references/*-prompt.md`；派發訊息只給提示詞路徑與變數（檔案路徑），不貼全文。審查者看不到撰寫者推理，每輪用全新 subagent。
- 並行上限 20；派完用檔案數核對應到／實到。
- 審查產出（JSON）放暫存目錄，不進 repo。
