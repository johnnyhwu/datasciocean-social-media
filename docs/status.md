# Stage 2 目前狀態（各系列的進度、發布網址、待辦）

CLAUDE.md 只留「進行中的系列」；已發布完的系列與歷史細節放在這裡。

## skillopt（進行中）

見 CLAUDE.md「目前狀態」；更詳細的規劃與決定記在 memory `project_skillopt_series_plan`。

## persona-aware-d2s（進行中）

見 CLAUDE.md「目前狀態」。第 1 則 `persona-d2s-task-and-pipeline`（16 張）已發布（2026-10-15）：IG https://www.instagram.com/p/DefqxZOH0Ot/ 、Threads https://www.threads.com/@datasciocean/post/DefrJYsH5nk 。第 2 則 `persona-d2s-training-design-flaws`（14 張）已發布（2026-10-16）：IG https://www.instagram.com/p/Dejx3ZWGGGt/ 、Threads https://www.threads.com/@datasciocean/post/DejyJ7bmJTr ；第 1 則 Threads 已回補（連到第 2 則）。第 3 則 `ready`。

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
