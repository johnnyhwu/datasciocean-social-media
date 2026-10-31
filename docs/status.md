# Stage 2 目前狀態（各系列的進度、發布網址、待辦）

CLAUDE.md 只留「進行中的系列」；已發布完的系列與歷史細節放在這裡。

## skillopt（已發完）

視覺「等深線」，Threads 用輪播；規劃與決定在 memory `project_skillopt_series_plan`。
1. `skillopt-overview`（19 張，2026-10-12）：IG https://www.instagram.com/p/DeYn1j2oCAP/ 、Threads https://www.threads.com/@datasciocean/post/DeYo4JSIGcl
2. `skillopt-batch-evidence-minibatch`＋`skillopt-bounded-edit-budget`（雙卡，17 張，2026-10-13）：IG https://www.instagram.com/p/Dea5IgXIBKS/ 、Threads https://www.threads.com/@datasciocean/post/Dea6HxFICya
3. `skillopt-blind-acceptance-gate`＋`skillopt-epoch-level-control`（雙卡，17 張，2026-10-14）：IG https://www.instagram.com/p/DedaYcgk8zR/ 、Threads https://www.threads.com/@datasciocean/post/Dedbc--IMBp

## persona-aware-d2s（已發完）

視覺「一式四份」直切（`style: cards`）；3 卡 3 則不合併；hashtag `DSO_PersonaD2S`。第 1 則的定位語（人決定 A+C）：事實（EACL 2024、微調 GPT-3.5-turbo）加人口吻的一行「這個系列是在了解早期的簡報生成怎麼做」，這一行不在卡上，是人授權的放行項。新增圖型 `equation`、`quad` 的 `bars`、`dotgrid` 的 `cols`。第 1 則 `persona-d2s-task-and-pipeline`（16 張）已發布（2026-10-15）：IG https://www.instagram.com/p/DefqxZOH0Ot/ 、Threads https://www.threads.com/@datasciocean/post/DefrJYsH5nk 。第 2 則 `persona-d2s-training-design-flaws`（14 張）已發布（2026-10-16）：IG https://www.instagram.com/p/Dejx3ZWGGGt/ 、Threads https://www.threads.com/@datasciocean/post/DejyJ7bmJTr ；第 1 則 Threads 已回補（連到第 2 則）。第 3 則 `persona-d2s-what-to-borrow`（13 張）已發布（2026-10-17）：IG https://www.instagram.com/p/DelBriik7pd/ 、Threads https://www.threads.com/@datasciocean/post/DelDUocE7Zt ；第 1、2 則 Threads 已回補（連到第 3 則）。

## bradley-terry-pairwise-preference（獨立貼文，已發布）

2026-10-23，12 張：IG https://www.instagram.com/p/De0b1Udnw6Z/ 、Threads https://www.threads.com/@datasciocean/post/De0cNARn6v9 。視覺「蹺蹺板」（`standalone/bradley-terry-pairwise-preference/`，人從 S1 蹺蹺板／S2 對戰網／S3 八比二選 S1）；hook 反直覺斷言（候選 2，為了塞進兩行改了字）。人的決定：轉折張、延伸閱讀、導流連結都不放；第 5 與 6 張之間加一張 reward model 與 loss 的銜接；保留「改寫成指數」並另加逐步推導；DPO 與 InstructGPT 補作者、年份與 arXiv 短連結（`latin_allow`）。新增：`seesaw`／`hidden`／`cycle` 圖型、`pairs` 底部橫框、**LaTeX 數學式**（spec 頂層 `math: true`，KaTeX 在 `assets/katex/`；程式 A、發布程式讀 spec 都先 `untex`）。放行項：三組假設例子、第 7 張的 8 對 2 驗算（推導）、第 11 張「為什麼有這個假設」的推論句。

## decision-transformer-reward-conditioning（獨立貼文，已發布）

2026-10-21，9 張：IG https://www.instagram.com/p/DevHQBlk2nG/ 、Threads https://www.threads.com/@datasciocean/post/DevHi6skzg5 。視覺「地平線」（`standalone/decision-transformer-reward-conditioning/`）；hook 讀者疑問，人選 A 並微調。人的決定：不放 Persona-Aware-D2S 轉折張與延伸閱讀、導流行與文章連結全拿掉；老鼠走迷宮是假設的例子、PPO／DPO 的 arXiv 網址是放行項（`latin_allow`）；刪掉「多步驟威力」那張。新增：獨立貼文架構、`tokens` 圖型。

## jev-cascade（已發完；2026-10-10 的狀態）

- 系列 `jev-cascade`（JEV 串接 Judge 系列，來自文章 `jev-as-a-judge`；視覺哲學「潮線」）**5 張卡做成 3 則 post，三則都已用 API 發到 IG 與 Threads**（兩個格式都是 `published`）。系列標題（`planned_title`）是草案。
  1. `jev-cascade-overview`：IG https://www.instagram.com/p/DeLvR1goG7Z/ 、Threads https://www.threads.com/@datasciocean/post/DeMHNAeEzm2
  2. `judge-readable-vs-derive`＋`confidence-three-metrics`（雙卡，2026-10-08）：IG https://www.instagram.com/p/DeNyAsCGDTq/ 、Threads https://www.threads.com/@datasciocean/post/DeNyxyxmAFX
  3. `cascade-complementary-errors`＋`cascade-threshold-and-failure-mode`（雙卡，2026-10-10；封面「想用便宜的 Judge 幫 GPT-6 省錢？得先闖兩關！」）：IG https://www.instagram.com/p/DeTsWaOD3Pd/ 、Threads https://www.threads.com/@datasciocean/post/DeTsbyVjw9E
- 第 1、2 則發布時系列地圖列的是 4 則（第 3 則是 2026-10-10 才把最後兩張卡合併的，已發布的圖改不了）。存量（`ready`）0 則；下一則要開新系列或做獨立 post，先問人。
- **回補已完成**（2026-10-10）：第 1 則與第 2 則的 Threads 串文最後一則下面，各接了一則回覆，連到後面發布的則（`state/backfill.md` 現在是 0 項）。之後每發一則新貼文，都要再跑 `threads_publish.py backfill`（dry-run 給人看、人說「發」才發）。IG 回補、限時動態、精選集、置頂都不做。
- 模板 hash 目前是 `e6ea36d49aa3`（2026-10-10 加成對橫條圖）；前兩則記的是舊 hash，這是預期的（已發布的不重渲、`batch_check.py` 不比對）。
- 發布流程已用真實帳號跑過三次：照 `references/publish-flow.md`。已驗證的事實與還沒驗證的事項在 `instagram-publish.md`、`threads-publish.md`。
- **待人決定**：流程／分流圖版型與樣張（`design-series-visuals/references/principles.md` 八）；封面主標是否放寬成 3 行；`config/params.yaml` 的 `structure_text_max_chars` 與 `ai_tone_blacklist` 仍是初稿；Threads token 是否補上 `threads_delete` 權限（目前沒有，刪除只能手動）；hook 與副標偏好的整理（見 memory `feedback_hook_style`，人說之後再談）。

## 卡上參考圖（`figures`）的接入與 SAG 試作（2026-10-24）

上游契約（`concept-wiki/docs/card-format.md` §4.2）：主張可附 blog 的圖，圖只是參考；貼文要用就重製。這邊已同步：`cardlib.py` 讀 `figures`（缺檔報錯、sha256 核對）、程式 A 檢查 spec 的 `fig_refs`、`build_package.py` 產生 `_build/figure-review.md` 並在 caption 自動註明圖片出處、新增「重製圖審查者」（`references/figure-prompt.md`、`verify_figure.py`）、規則文件與 CLAUDE.md 規則 17、`tests/test_figures.py`、「部落格推論」新定義。新增圖型 `links`、`hops`（`tests/test_diagrams.py`）。


## SAG 系列（2026-10-24 起，進行中）

人決定（2026-10-24）：方案 1（5 卡合成 4 則：A＋B → C → D → E）與封面方向 S3「探照燈」。`series/sag/`：`series.md`（`status: planning`、已 `members_locked`（2026-10-25）；系列名「SAG：不先建圖，查詢時才連」與 `planned_title` 都是草案）、`philosophy.md`、`templates/`、`sketches/`。新視覺風格 `style: spotlight`（`render.py` 的 `sp_field`／`sp_strip`；`tests/test_spotlight_style.py`）。新圖型 `bubble`（金色泡泡圈住好幾個項目）與 `drift`（一路偏掉的路徑，純示意）（`tests/test_diagrams.py`）；2026-10-25 新增圖型 `ingest`（兩段式系統架構圖，仿論文 Figure 2：線下建索引、線上查詢；有回歸測試）；成對橫條圖有小數時整數值也顯示一位小數。
- 第 1 則 `out/sag/sag-latent-hyperedge-one-hop/`（A＋B 雙卡、19 張）spec 做完：程式 A、B 通過；重製圖審查者通過；忠實者第 1 輪 blocker 0，第 2 輪（改過的區塊）也 blocker 0；讀者與編輯建議已採用大部分易懂與圖的項目。2026-10-25 依人的 feedback 修改：封面與第 8 張補論文 arXiv（2606.15971，外部查證，非卡；2608.12129 已撤回不用）、全篇 Multi-Hop、第 3／8 張具體例子、第 9→10 張改用 `ingest` 架構圖並拿掉圖註、不標「我的想法」；之後忠實者第 3 輪 blocker 0，再改的區塊（讀者建議：SQL／實體白話、二元圖譜、例子）由忠實者第 4 輪重審。**已發布（2026-10-25）**：IG https://www.instagram.com/p/De5uaKSk-OW/ 、Threads https://www.threads.com/@datasciocean/post/De5vTr5E64N ；系列已鎖定（`members_locked`），第 2～4 則 spec 未做，發布後要做 Threads 回補。**hook 人已挑（2026-10-25，讀者疑問式「Multi-Hop 推理，一定要先建知識圖譜嗎？」）；arXiv 連結只寫網址、不寫「Wu 等人」；說明例子改為 TSMC／張忠謀；忠實者審查全過。**
- 第 2 則 `out/sag/sag-sql-vector-llm-division-and-funnel/`（單卡 C、16 張）**已發布（2026-10-26）**：IG https://www.instagram.com/p/De8MXyVGDo8/ 、Threads https://www.threads.com/@datasciocean/post/De8MzobmMZi 。hook 用候選 B（「SAG 不靠更強的模型，靠分工」）。人的 feedback 後新增：第 2 頁「前情回顧」`recap` 版型與系列地圖「標題＋細節」（細節 = `series.md` 每則 `summary`，忠實者審過）；新圖型 `roles`、`embed`、`online`、`gate`、`concat`、`joint`、`rails`（`online`／`concat` 重畫卡上 figure2，重製圖審查者通過；有回歸測試）。**待做**：第 1 則 Threads 回補（`state/backfill.md`）、第 3、4 則。
- 第 3 則 `out/sag/sag-results-and-gain-source/`（單卡 E、14 張）**已發布（2026-10-27）**：IG https://www.instagram.com/p/De-hkrKE_VA/ 、Threads https://www.threads.com/@datasciocean/post/De-h-d2k-fB 。hook 用候選 A（「SAG 贏在超邊，還是贏在 SQL？」；發布前人沒有單獨明講接受，只回「好的 可以 commit, push and publish」，之後起 `state.py ready` 會擋暫用 hook）。人的 feedback 後：Recall 一律寫英文（`terms.yaml`）、實驗頁補「所以呢」、文字不要制式（`ig-carousel.md` §4）；新圖型 `scoreboard`、`leak`、`amplify`，`hops` 加 `fade`／`shortcut`，`bubble` 加 `chain`（有回歸測試）。**待做**：第 1、2 則 Threads 回補（`state/backfill.md`）、第 4 則。第 1、2 則已發布的系列地圖仍寫舊的「找回率」，不重渲。
- 第 4 則 `out/sag/sag-tradeoffs-price-paid/`（單卡、13 張）**已發布（2026-10-28）**：IG https://www.instagram.com/p/DfCZvP4k6tz/ 、Threads https://www.threads.com/@datasciocean/post/DfCaIIyk0dJ 。hook 是人提的 F（「SAG 相較 GraphRAG 不先建圖，很省事沒錯，但要付三筆帳」）；忠實者 r6 對封面與 caption 第一行擋「範圍被放大」（相較 GraphRAG ＋ 三筆帳暗示 GraphRAG 沒有這些問題，卡上無支撐），人看過後接受爭議、維持原樣（`_build/reviews/faithful-r6.json`）。**待做**：第 1～3 則 Threads 回補（等人說「發」）。（以下為發布前紀錄）**發布包做完，待人決定（2026-10-27）**：程式 A 通過、程式 B 13/13、回歸測試 12/12、`batch_check` 通過（存量 WARN 是預期）。審查：忠實者第 1～3 輪、讀者與編輯第 1～2 輪（讀者第 3 輪）、改過的區塊由忠實者第 4 輪重審。第 1 輪初稿 15 張，依編輯建議刪掉「帳單」總結張、併掉重複的例子頁。新圖型 `receipt`（已不在這則使用）、`squeeze`、`alias`、`handoff`、`mismatch`、`ledger`（有回歸測試）；`series/sag/templates/style.css` 的 `.chip` padding 8→4（標題右緣超過小標籤左緣時，程式 B 對比度會量到小標籤的金色底線；已發布的記舊 hash 是預期）。**2026-10-28**：人指出「目前不能更新」會誤解，全篇改成「新舊衝突沒有內建／原生判斷」；人提出新 hook F「SAG 相較 GraphRAG 不先建圖，很省事沒錯，但要付三筆帳」並決定封面主標可放寬（`cover_title_max_lines: 3`；探照燈封面超過 2.5 行會縮成 56px），第 3 張補 GraphRAG 白話。**待人決定**：hook（候選在 `_build/hook-candidates.md`，目前封面是人提的 F，待人看過明講接受；第 3 則是讀者疑問式，所以候選 B 會違反相鄰）、放行項（論文網址、名詞白話補充、第 10 張假設例子、示意圖）、是否標 `ready`。發布後：`series_links.py` 並補第 1～3 則 Threads 回補連到第 4 則。
- （第 3 則的起手筆記，已完成）**第 3 則怎麼開始**（卡 `sag-results-and-gain-source`）：照 `make-social-post/SKILL.md` 從「開始前」起手；第 2 頁 `recap`（`current` 填這一則，內容來自 `series.md` 的 `summary`）、最後一頁 `series_map`（`current` 同）；`summary` 已改白話並限 ≤58 字（第 4 則要放得下 4 列，已試算）；圖像照 `CLAUDE.md`「大膽、有創意、變化多」那條，**不要沿用第 2 則的圖型當預設**（可重用，但先寫一句畫面再選）；Threads 回覆的「同系列」連結用 `series_links.py`；state 格式名是 `ig_carousel`／`threads_thread`。
- 第 2～4 則（C、D、E）還沒做；每發一則都要補 Threads 回補與「同系列」連結。

## Claude Code 系列（2026-10-28 起，進行中；視窗風格 `window`）

人決定：3 卡合成 2 則（迴圈＋權限雙卡、擴充），一則一則發；系列名「Claude Code：怎麼讓 AI 敢自己改你的程式」（2026-10-29）；hashtag `#ClaudeCode`（不加 `DSO_` 前綴）；可上網補充，但只准官方來源（`series/claude-code/research.md`）。系列已鎖定（`members_locked`，2026-10-29）。
- 第 1 則 `out/claude-code/claude-code-agentic-loop-and-tools/`（雙卡、16 張）**已發布（2026-10-29）**：IG https://www.instagram.com/p/DfDuOUJk09k/ 、Threads https://www.threads.com/@datasciocean/post/DfDupxOk16t 。hook 人挑定（讀者疑問式）。系列摘要（`series.md` 的 `summary`）已改白話，忠實者重審通過、讀者看過。
- 第 2 則 `out/claude-code/claude-code-extension-and-context/`（單卡、16 張）**已發布（2026-10-31）**：IG https://www.instagram.com/p/DfI172ND6Xv/ 、Threads https://www.threads.com/@datasciocean/post/DfI2QXrj7JH 。hook 人挑 C1。發布前官方文件 13 條補充逐條重新核對，文字沒有改版；Threads「同系列」連結已用 `series_links.py` 補上第 1 則。第 13 張 MCP 列（卡 c13 沒提載入時機，忠實者判定不矛盾但有張力）人決定照原樣發（2026-10-31）。新圖型 `sockets`、`lazy`、`hub`、`pinned`、`compact`、`sidecar`、`combo`（有回歸測試）。
- 系列 2 則全發完。**第 1 則 Threads 回補（補上第 2 則連結）待人說「發」**（`state/backfill.md`）。
