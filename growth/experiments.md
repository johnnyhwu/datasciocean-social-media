# 實驗紀錄

`insights.py` 會讀「套用紀錄」表，把 action id 帶進每則貼文的快照（第一欄觀念 id、第三欄 action id，逗號分隔）。2026-11-21 以前發布的 29 則都沒有套用任何 action，是基準。

## 套用紀錄

| 觀念 | 發布日 | actions | 做了什麼 |
|---|---|---|---|
| `cer-critical-token-confidence` | 2026-11-21 | A3 | 帶走張頁腳加追蹤邀請（人已 review 成品後才加，只改頁腳） |
| `cer-results-how-to-read` | 2026-11-22 | A3 | 同上 |
| `ragu-results-peeling-confounds` | （未發布） | A1, A3, A4 | 2026-11-23 重做：GraphRAG 值不值得做（系統取捨）；帶走張頁腳加追蹤邀請；7 張 |
| `retrieval-recall-not-answer-quality` | （未發布） | A1, A3, A4 | 調 RAG 時該看哪個分數；帶走張頁腳加追蹤邀請；9 張 |
| `ragu-pipeline-two-stage-extraction-consolidation` | （未發布） | A1, A3, A4 | 建圖的兩趟抽取（能帶走的做法）；帶走張頁腳加追蹤邀請；8 張 |
| `small-extractor-saturation-not-scale` | （未發布） | A3, A4 | 帶走張頁腳加追蹤邀請；8 張 |

## 判讀紀錄

每次發布後的判讀寫在這裡（新的在上面）：日期、用哪個快照、哪個 action 有幾則、結果或方向、狀態有沒有改。

| 日期 | 快照 | action | 則數 | 結果 | 狀態變化 |
|---|---|---|---|---|---|
| 2026-11-22 | 2026-11-22 | A3 | 2（1 則 0.8 天、1 則剛發） | 追蹤數 IG 1,687、Threads 583，和前一份相同。A3 第 1 則（CER 2）0.8 天：IG 看 104、觸及 36、因這則追蹤 0、點進個人檔案 0；Threads 187（第 1 則 3.5 天才 123）。方向：IG 還沒有效果，Threads 略高；未滿 3 則、樣本太小，不判讀 | — |
| 2026-11-22 | 2026-11-21（UTC，覆寫基準那份；基準版本在 git afdfa40） | A3 | 1（剛發） | 追蹤數 IG 1,688→1,687、Threads 583→583（距基準約 1 天，無變化）；A3 第 1 則剛發，下次快照才有數字 | — |
| 2026-11-21 | 2026-11-21 | — | — | 建立基準（`reports/2026-11-21-baseline.md`），還沒有套用任何 action | — |
