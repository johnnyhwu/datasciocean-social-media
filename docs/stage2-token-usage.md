# Stage 2 token 用量紀錄

第一則貼文 `jev-cascade-overview`（系列 `jev-cascade`，2026-10-06 到 07）從做貼文到發布到 IG 與 Threads 的紀錄。數字是各 subagent 完成通知上的 token；**主 session 的用量算不準，沒有列**。

## subagent 用量

| 階段 | 次數 | token | 佔比 | 模型 |
|---|---|---|---|---|
| 忠實者 | 5 輪：6.6 萬、5.9 萬、5.2 萬、5.1 萬、6.1 萬 | 約 28.8 萬 | 64% | sonnet |
| hook 讀者 | 3 輪：2.7 萬、2.6 萬、2.7 萬 | 約 8.0 萬 | 18% | haiku |
| 工程師讀者 | 1 | 約 4.5 萬 | 10% | sonnet |
| 編輯 | 1 | 約 3.8 萬 | 8% | haiku |
| 合計 | 10 個 subagent | 約 45 萬 | | |

另有一輪忠實者在送出後發現文字已改，被停掉，用量未計入。

## 觀察

- **忠實者最貴，而且每輪成本幾乎不降**（第 2 輪起只審改過的區塊，仍要 5～6 萬）：固定成本是提示詞、卡、貼文。能省的是輪數。5 輪中多數 blocker 是撰寫者自己能先抓到的 → 新增 `references/self-check.md`，派審查前先自檢。
- **hook 流程訊號弱**：三輪 haiku 讀者的排序，人都不滿意，最後是人用感覺選的。→ 改成自己提 5～6 個大膽候選、最多一次讀者參考、人挑（`hooks.md`）。
- **規則與人的偏好衝突**：「封面不能比內文說得滿」與「留白吸引點擊」互相拉扯，多花約 2 輪。→ 已改寫 `hooks.md` 與 `faithful-prompt.md`（主標副標合看、語氣詞不算判斷）。
- **程式 B 漏洞**：數字與單位被拆行沒被抓到。→ 加 `bind_nums` 與檢查，回歸測試 `tests/test_render_numunit.py`。
- **用語**：「判官」vs「Judge」靠逐處替換。→ `config/terms.yaml` 加程式 A 檢查。
- caption 摘要從「3｜」開始編號會誤導。→ 改成不編號。
- 改文字時有審查者在跑會白花一輪。→ `review-loop.md` 加規則。

## 發布階段（IG 與 Threads 官方 API）

沒有用 subagent；主要成本是研究官方文件與實測來回。學到的：

- **用 WebFetch 讀官方文件，摘要是小模型轉述，同一件事兩頁會互相矛盾**（例如發文上限出現 25、50、100 三種；圖片大小一頁說沒限制、另一頁說 8 MB）。關鍵數字要用第二次提問或實測再核對，不要只信一次摘要。
- **權限是在產生 token 的當下決定的**：Threads 沒勾 `threads_delete`，DELETE 回 403，更新 `.env` 的 token 也沒用，要在 App 設定頁加權限後**重新產生**。`threads_publish.py token-info`（官方 `/debug_token`）可以直接查實際權限與到期時間，不必猜。
- **IG API 沒有草稿、排程、預覽、刪除**；最接近草稿的是「預檢」（建好 container 但不發佈，23 小時內可沿用）。Threads 有 DELETE，但需要 `threads_delete`；Threads 的串文無法預檢（回覆需要前一則已發佈的 id）。
- 兩次真實帳號實測（IG 3 張測試輪播、Threads 3 則測試串文）都用專用測試包與 `--no-record`，並由人確認後才發；實測驗證了：4:5 輪播不會被裁、回覆前一則會形成同一串、圖片與連結預覽正常、Dashboard 的 Threads token 是 60 天長效。
- 狀態寫回的訊息（`state.py record` 會印字）混進 JSON 輸出，造成解析失敗；已導到 stderr。**輸出給 Agent 讀的指令，stdout 只能有 JSON。**

## 還沒做的（人的決定）

- 圖要有「意義」（光看圖就看懂方法）：見 `design-series-visuals/references/principles.md` 八。需要新版型（流程／分流圖）與樣張，由人審。
- 工程師讀者與編輯是否降到 haiku、主 session 在機械步驟是否降 effort：人說先當作沒討論過。
- 封面主標是否放寬成 3 行。
