# 流量追蹤與改進（growth）

目標：**長期讓讀者與追蹤人數變多**（人 2026-11-21）。做法是一個迴圈：每發布一則，就抓過去貼文的成效、寫下 insight、更新行動清單；下一則從行動清單挑 1～2 個改變做實驗、記錄下來；之後的快照再判斷有沒有效。

流程在 `.claude/skills/make-social-post/references/growth-loop.md`；這個資料夾只放狀態。

| 要做的事 | 讀 |
|---|---|
| 發布完一則（迴圈的「量」與「想」） | `growth-loop.md` §1，然後 `plan.md` |
| 開始做新的一則（迴圈的「改」） | `plan.md`（挑 action）、`experiments.md`（記下這則套用了什麼） |
| 判斷某個改變有沒有效 | `experiments.md` 的套用紀錄，再看對應日期的 `reports/` |

| 路徑 | 是什麼 |
|---|---|
| `plan.md` | 活的行動清單：每個 action 的假設、證據、狀態、怎麼判斷有效 |
| `experiments.md` | 每則貼文套用了哪些 action（一行一則）＋每次判讀的結果 |
| `reports/YYYY-MM-DD-<主題>.md` | 有日期、不改的分析快照；要更新就寫新的一份 |
| `snapshots/YYYY-MM-DD.json` | `insights.py pull` 抓的原始數字（每則貼文的 IG／Threads 指標、帳號追蹤數），不含任何 token |

## 規則

1. 不重算已經寫下的結論；只拿**新的日期**重跑，結果寫成新的 report。
2. `plan.md` 的 action 改狀態時，就地更新，並在 `experiments.md` 記一行。
3. 結論要寫出資料來源與時間（哪個快照、貼文發布幾天）；推論標「推論」。
4. 樣本很小（每天一則）：**單則貼文的高低不下結論**；一個 action 至少套用 3 則、而且差距明顯（例：中位數差 2 倍）才判有效或無效，否則寫「方向」。
5. 比較要對齊貼文年齡（發布後天數）；Threads 的 views 官方標為「開發中」指標。
6. 憑證不進這裡：`insights.py` 輸出前會拿掉 token（API 的 paging 網址夾帶 token，2026-11-21 外洩過一次）。
7. 只做「讀數據 → 改內容」：不買廣告、不互讚、不改帳號設定。發文時段、帳號簡介目前不在本專案範圍（`CLAUDE.md`），要試得先問人。
