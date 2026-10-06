# Jev 拆解系列：發布後待辦清單（docs/03 §15）

系統不自動發布。以下由人手動做。目前產出兩則：

| 順序 | 觀念 | 貼文資料夾 | hook 樣態 |
|---|---|---|---|
| 1（概覽先發） | jev-overview | `jev-overview/` | 情境痛點 |
| 2 | confound-three-questions | `confound-three-questions/` | 反直覺斷言 |

相鄰兩則 hook 樣態不同（符合 §4 發文順序規則）。兩則用同一版模板（template_hash 見各自 `checks-b.json`）。

## 發布前
- [ ] 人最後確認兩則的圖（`ig/*.png`）、`ig/caption.txt`、`threads.txt`、`ig/` 與 `alt-text.json`
- [ ] IG：依 `ig/01.png`… 順序上傳，貼 `ig/caption.txt`，替代文字貼自 `alt-text.json`
- [ ] Threads：正文用「新增到串文」一次發出，每則串文附 `threads.txt` 標註的圖檔，最後一則（置頂）含文章連結
- [ ] **存量提醒**：目前只有 2 則，低於 `min_stock: 7`。其餘 4 則（schema-valid、efficiency、honest-probability、decompose）的 Stage 2 格式仍是 not_tried

## 發布後（每則）
- [ ] 發限時動態並加連結貼紙，指向文章
- [ ] 收進「Jev 拆解系列」精選集
- [ ] 置頂最後一則 Threads 回覆
- [ ] 概覽（jev-overview）發布後，置頂概覽 post
- [ ] 把發布紀錄（網址、時間）交給系統寫回 wiki 的 `posts[]`，系統才會更新 `backfill.md`
- [ ] 系列其他則發布後，依回補清單：IG 改 caption 補延伸連結；Threads 在原串文下加回覆補完整連結

## 這次實跑的已知狀況
- 兩則的最後一則 Threads 與系列地圖，列出的同系列標題中，尚未發布的只寫標題
- IG caption 導流行寫「請在 datasciocean.com 搜尋「Jev」」，因為規格預設的「文章標題」不在任何 wiki 欄位（見 docs/first-run-findings.md）
