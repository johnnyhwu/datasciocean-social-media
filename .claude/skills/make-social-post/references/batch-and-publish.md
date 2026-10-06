# 批次、系列、發布包、寫回

## 1. 選觀念與獨立或系列

選觀念：依系列規劃與存量（`state.py status`）。同一個觀念預設每種格式都做；做不出合格版本的格式標 `unsuitable`。新增格式（Reels、Shorts）時，所有觀念的該格式自動視為 `not_tried`。

| 卡的情況 | 處理 |
|---|---|
| `bound_to_source`、`evidence_from_single_source` | 預設組成系列（同一篇文章的觀念） |
| `standalone_classic` | 預設獨立 post |
| 系列只剩一則 | 視為獨立 post |

## 2. 系列檔 `series/<series-id>.md`

```yaml
id: jev-teardown
name: Jev 拆解系列               # 每張投影片的系列標籤，必須與此完全相同
philosophy: design/series-philosophies/jev-sounding.md
color: teal-mid                  # 封面海浪色帶，相鄰系列不同色
members:                         # 發文順序
  - concept: jev-overview
    planned_title: Jev 補的是分類器與 LLM 之間的空隙
hashtag: DSO_Jev
status: planning                 # planning | publishing | done
```

`planned_title` 在系列規劃時就定下，系列地圖與 Threads 最後一則都用它。獨立 post 沒有系列檔。系列檔、視覺哲學與模板都在本 repo；**觀念卡在 concept-wiki submodule，不得修改**。

## 3. 發文順序

1. 概覽先發。
2. 其後「被依賴的先發」（例如 confound 先於 efficiency）。
3. 相鄰兩則（含跨系列）的 hook 樣態不同。
4. 同時只進行一個系列，系列內連續每天一則；獨立 post 安插在系列之間或填補空檔。
5. 相鄰系列的封面色不同。

## 4. 批次層檢查（`batch_check.py`）

每週批次約 7 則，交給人確認之前跑一次，參數順序 = 預計發文順序：相鄰 hook 樣態不同、相鄰系列封面色不同、同系列模板 hash 相同、串文裡的「同系列：…」標題與 `planned_title` 一致、存量（`state/` 裡 ready 的觀念數）低於 `min_stock`（7）就提醒、為 0 就暫停發文。

**存量不夠時，寧可跳過一天，也不降低審查標準。** 「每天一則」是內部目標，不對外公開承諾。

## 5. 人最後確認

交給人看：`contact-sheet.png` 加每則的 `ig/caption.txt`、`threads.txt`、`alt-text.json`；報告裡說明：被審查者改過的 hook、被刪掉的投影片、HINT 與未解決的 minor、任何和先前慣例不同的地方（例如導流行寫法）。人確認後才進入發布包。

## 6. 輸出

發布包（`out/<series-or-standalone>/<concept-id>/`）：
- `ig/01.png` … 依順序編號的投影片
- `ig/caption.txt`、`alt-text.json`
- `threads.txt`（正文，加每則串文的文字與對應圖檔）
- `spec.json`（投影片規格，含引用編號；`checks-b.json` 含模板版本 hash）
- 審查用的中間檔（`post-with-refs.md`、`post-reader.md`、`contact-sheet.png`）一併留著

確認後：`state.py ready <concept> <format> <pack-dir>`（每個格式各一次），並寫（或更新）`out/<series>/publish-checklist.md`：

```
# <系列名>：發布後待辦清單
系統不自動發布。以下由人手動做。
| 順序 | 觀念 | 貼文資料夾 | hook 樣態 |
## 發布前
- [ ] 人最後確認圖、caption、threads.txt、alt-text.json
- [ ] IG：依 ig/01.png… 順序上傳，貼 ig/caption.txt，替代文字貼自 alt-text.json
- [ ] Threads：正文用「新增到串文」一次發出，每則串文附 threads.txt 標註的圖檔，最後一則（置頂）含文章連結
- [ ] 存量提醒（低於 min_stock 時）
## 發布後（每則）
- [ ] 發限時動態並加連結貼紙，指向文章
- [ ] 收進系列精選集；概覽發布後置頂概覽 post；置頂最後一則 Threads 回覆
- [ ] 把發布紀錄（網址、時間）交給系統寫回
- [ ] 系列其他則發布後，依 state/backfill.md 回補：IG 改 caption 補延伸連結；Threads 在原串文下加回覆補完整連結
```

範例：`out/jev-teardown/publish-checklist.md`。

## 7. 人手動發布後：寫回狀態

人回報網址與時間後：

```
uv run python .claude/skills/make-social-post/scripts/state.py record <concept> <format> \
    --url <網址> --published-at <ISO 時間> --series-id <系列 id> --hook-type <hook 樣態> --mentions <觀念 id,…>
```

寫入 `state/<concept>.yaml` 的 `posts[]`（必須記錄：觀念 id、系列 id、格式、網址、發布時間、hook 樣態、提及的觀念；成效分析另做獨立系統，這些識別碼事後很難補），格式狀態改 `published`，並重算 `state/backfill.md`（已發布、但缺少「之後才發布的同系列或提及觀念」連結的貼文）。

| 平台 | 回補方式 |
|---|---|
| IG | 修改 caption，補一行延伸連結。投影片發布後不能新增或刪除 |
| Threads | 在原串文下新增一則回覆，補上完整連結（發文後可編輯的時間很短，不能靠編輯） |

回補做完後，在該貼文的 `state/<觀念>.yaml` 的 `backfilled` 加上被補的觀念 id，清單就會消失。

## 8. 未驗證事項（需要人手動驗證，結果影響參數，不影響產出內容）

限時動態精選集的連結貼紙是否仍可點、Threads 最多置頂幾則回覆、系列 hashtag 頁面能否完整顯示、平台排程能不能排 IG 輪播與 Threads 多則串文、手機上 caption 中文大約在哪裡摺疊、blog 搜尋功能是否可用、手機實機顯示。數字參數（補充 40～60 字、10 張上限、重疊率 40%、caption 第一句 50 字）皆為判斷值，非實測。
