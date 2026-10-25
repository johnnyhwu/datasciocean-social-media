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
4. **（新系列／規劃時）** 跑 `series_deps.py <系列 id>` 並**一定要問人哪些卡要合併**（`references/batch-and-publish.md` §1）；成員定案後在 `series.md` 加 `members_locked: true`，再發第 1 則；**預設先把整個系列每一則的 spec 都做完、張數與 `planned_title` 定案，才鎖定並發第 1 則**（2026-10-11 人決定；鎖定後不改成員與標題）。人明確要求先發時可以，規則與要講明的代價見 `CLAUDE.md`「工作方式」。
4b. **決定這次做哪一則**：照系列檔 `series/<id>/series.md` 的 `members` 順序，找第一個還是 `not_tried` 的觀念；這是預設，要不要照做由人決定。
5. 要做的觀念，**只讀它的卡**（`concept-wiki/wiki/concepts/<id>.md`），不讀 blog。同時讀 `concept-wiki/docs/card-format.md`（卡格式與 status 語意）。**卡上主張若附 `figures`，用 Read 實際打開圖檔看**（路徑 `concept-wiki/wiki/<file>`），不要只看路徑或圖說；圖只是參考，貼文要用就重製（`references/anchor-writing-rules.md`「參考圖」）。
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
| 3 | **先做版型規劃**（每張選好版型、圖上術語在哪張定義，`references/ig-carousel.md` §0；**卡上附了圖的主張，先看圖再決定要不要重製：圖能讓觀念更好懂就用程式重畫一張（`fig_refs`，內容以主張為準），不需要就不用**；**機制類的圖看 `design-series-visuals/references/brand-and-layouts.md` §4.2「機制 → 圖型」，圖要大膽、有故事，同則連續 3 張以上同圖型要換；Threads 預設輪播**；**每張帶數字的圖先用 `chart-thinking` skill 想過：要比什麼、圖有沒有直接支撐主標；每張圖寫一句「比文字多給什麼」，定義與機制類預設用具體的假設例子**；獨立貼文的轉折張、延伸閱讀、導流連結、Threads 回覆打包成一個問題先問人；機制／數學類先做概念依賴表），再寫 `out/<series>/<concept>/_build/spec.json`：投影片、Threads、caption、每個區塊標引用的 claim id | `references/spec-json.md`、`references/ig-carousel.md`、`references/threads-and-caption.md`、`references/anchor-writing-rules.md` |
| 4 | `check_a.py <spec.json>`，ERROR 清零 | `references/program-a.md` |
| 5 | `render.py <spec.json>`，程式 B 全過；`contact_sheet.py <發布包資料夾>` 拼縮圖；**自己看一次渲染後的 PNG** | `references/program-b.md` |
| 6 | （在 `contact_sheet.py` 之後）`build_package.py <spec.json>`：產生人看的 `README.md`、`ig/post.md`、`threads/post.md`、審查用的 `_build/post-with-refs.md`／`post-reader.md`，並更新 `out/README.md` 索引 | `references/threads-and-caption.md` |
| 7 | **先照 `references/self-check.md` 自檢**，再派忠實者、讀者（一般讀者，附圖）、編輯（附圖）；**有 `fig_refs` 再派重製圖審查者**（`references/figure-prompt.md`，看原圖＋主張＋重製圖）；`verify_faithful.py`、`verify_reader.py`、`verify_figure.py`。**審查通過後再新增文字或改數字，要重審改過的區塊**：`spec_diff.py` 列出範圍、`--mark` 記下通過版本 | `references/review-loop.md`、`references/self-check.md` |
| 8 | `batch_check.py <spec>...`（參數順序 = 預計發文順序） | `references/batch-and-publish.md` §4 |
| 9–10 | 給人看貼文 `README.md`（含縮圖）、`ig/post.md`、`threads/post.md`，確認後 `state.py ready <觀念> <格式> <發布包>`（兩個格式各一次） | `references/batch-and-publish.md` §5–6 |
| 11 | **發布**：`prepare` → push `ig/jpg/` → IG `preflight` → IG dry-run → 人說「發」→ `--confirm` → `series_links.py`（系列已有發布的前幾則時）→ Threads dry-run → 人說「發」→ `--confirm`；成功後自動寫回 state | **`references/publish-flow.md`**（照做）、`references/instagram-publish.md`、`references/threads-publish.md` |

第一次是新系列時，先用 `design-series-visuals` 把視覺哲學與各版型的樣張做出來、**由人審過**才量產。系列已有模板就直接用，同一系列的所有貼文用同一版模板。

## 新增格式（Reels、Shorts…）

格式是插件：每種格式各自定義結構規則、寫作規則、審查清單、輸出欄位；格式之間共用 hook 候選、引用標記機制、回歸測試。新格式加進來時，所有觀念的該格式自動視為 `not_tried`（`state/` 裡沒有該格式的鍵就是 not_tried），成為候選。觀念卡不用改。目前只有 `ig_carousel` 與 `threads_thread`。

## 腳本（`scripts/`）

| 腳本 | 用途 |
|---|---|
| `check_a.py` | 程式 A：引用標記、比較詞、限定條件、數字、字數、重疊率、用語… |
| `render.py` | 渲染引擎與程式 B：spec.json + 系列模板 → 1080×1350 PNG，並做版面檢查，寫 `_build/checks-b.json`、`alt-text.json` |
| `build_package.py` | 由 spec.json 產生人看的入口（`README.md`、`ig/post.md`、`threads/post.md`）、審查用貼文文字，並更新 `out/README.md` 與系列索引；`--refresh` 只重寫 README 與索引（發布成功後由發布程式自動呼叫） |
| `contact_sheet.py` | 把投影片拼成縮圖總覽 |
| `verify_faithful.py`、`verify_reader.py`、`verify_figure.py` | 驗證忠實者／讀者／重製圖審查者的 JSON：引用逐字出自卡或貼文、分級、陷阱題；重製圖要有原圖位置與讀到的內容 |
| `batch_check.py` | 批次層檢查：相鄰 hook 樣態、相鄰系列色、模板 hash、標題一致、存量 |
| `ig_publish.py`、`ig_api.py` | IG 官方 API 發佈：prepare／preflight／publish（dry-run 預設，`--confirm` 才發）、token 管理 |
| `threads_publish.py`、`threads_api.py` | Threads 官方 API 發佈整串：publish／rollback／delete／token-info（dry-run 預設；中途失敗可續發） |
| `publish_common.py`、`hosting.py` | 兩個平台共用：`.env` 讀寫、token 效期與自動 refresh、JPEG 驗證；圖片託管介面（GitHub raw 網址） |
| `spec_diff.py` | 審查後的改動範圍：目前 spec 與上次審查通過的版本差在哪些區塊（給忠實者的 `{ONLY_BLOCKS}`）；`--mark` 記下通過版本 |
| `series_links.py` | Threads 最後一則的「同系列」：把已發布的貼文從「（尚未發布）」補成標題＋網址（dry-run／`--write`）；發布 dry-run 會擋沒補的 |
| `series_deps.py` | 系列規劃：列出該合併成一則的候選（輔助，不是偵測器；規劃時一定要問人） |
| `state.py` | 各觀念各格式的狀態（`not_tried`／`ready`／`published`／`unsuitable`）、發布紀錄、回補清單（`state/`） |
| `cardlib.py` | 共用：唯讀解析觀念卡（含主張附的 `figures`：圖路徑、缺檔報錯、sha256 核對）、系列與發布包路徑、文字正規化與逐字比對 |

**腳本參數**：`check_a`、`render`、`build_package`、`spec_diff`、`series_links` 吃 `_build/spec.json`；`contact_sheet`、`ig_publish`、`threads_publish`、`state.py ready` 吃發布包資料夾。跑超過 2 分鐘的指令（`ig_publish.py preflight`、全部回歸測試）用背景執行。改 spec 的中文文字用 Python 取代，不用 `sed -i`（macOS 的 BSD sed 要 `-i ''`，中文與引號容易出錯）。

`render.py`、`build_package.py` 對**已發布**的貼文預設拒絕，要重做才加 `--force`（發布後要更新 README 與索引用 `--refresh`，不用 `--force`）。`ig_publish.py`、`threads_publish.py` 的 `publish` 都有 `--summary`（縮短版輸出，給人看 dry-run 用）。

改了任何腳本或審查流程，跑 `CLAUDE.md`「工作方式」列的全部回歸測試。

## 派發 subagent 的做法

- 提示詞在 `references/*-prompt.md`：把全文貼進派發訊息、填好檔案路徑（審查者只准讀指定的檔案，讀不到提示詞檔）；放行項逐項列出（`review-loop.md`）。審查者看不到撰寫者推理，每輪用全新 subagent。
- 並行上限 20；派完用檔案數核對應到／實到。
- 審查產出（JSON）放暫存目錄，不進 repo。
- 審查者遇到用量限制或電腦睡眠中斷時，用 `SendMessage` 對同一個 subagent 說「繼續」，它會接著跑；不要重派（會多花一輪）。
- **改動集中再派**：同一輪的文字修改（讀者建議、人的回饋）一次改完，跑完程式 A、B，再用 `spec_diff.py` 的區塊當 `{ONLY_BLOCKS}` 派一位忠實者；邊改邊審會多出好幾輪（sag 把例子換成真實公司那次，忠實者第一輪就抓出例子與機制不符，修完又審一輪）。
