# 批次、系列、發布包、寫回

## 1. 選觀念與獨立或系列

選觀念：依系列規劃與存量（`state.py status`）。同一個觀念預設每種格式都做；做不出合格版本的格式標 `unsuitable`。新增格式（Reels、Shorts）時，所有觀念的該格式自動視為 `not_tried`。

| 卡的情況 | 處理 |
|---|---|
| `bound_to_source`、`evidence_from_single_source` | 預設組成系列（同一篇文章的觀念） |
| `standalone_classic` | 預設獨立 post |
| 系列只剩一則 | 視為獨立 post |

## 2. 系列檔 `series/<series-id>/series.md`（同資料夾還有 `philosophy.md`、`templates/`）

```yaml
id: jev-cascade
name: JEV 串接 Judge 系列        # 每張投影片的系列標籤，必須與此完全相同
philosophy: series/jev-cascade/philosophy.md
color: teal-mid                  # 封面海浪色帶，相鄰系列不同色
members:                         # 發文順序
  - concept: jev-cascade-overview
    planned_title: 便宜的 Judge 先判，沒把握才轉給 GPT-6
hashtag: DSO_LLMJudge
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

交給人看：每則貼文的 `README.md`（含縮圖）、`ig/post.md`、`threads/post.md`；報告裡說明：被審查者改過的 hook、被刪掉的投影片、HINT 與未解決的 minor、任何和先前慣例不同的地方（例如導流行寫法）。人確認後才進入發布包。

## 6. 輸出

發布包（`out/<series-or-standalone>/<concept-id>/`）的結構見 `spec-json.md`「發布包結構」。人只需要看三個檔案：

- `README.md`：入口。縮圖、檢查結果、發布前後待辦（`- [ ]` 清單，由 `build_package.py` 產生，不用另外寫 checklist）
- `ig/post.md`：IG 每一頁的圖與文字、替代文字、整段 caption
- `threads/post.md`：Threads 正文、每則串文（附圖）、最後一則

`out/README.md` 是全部貼文的總入口（待發布清單與各系列狀態），`out/<series>/README.md` 是系列的發文順序。

確認後：`state.py ready <concept> <format> <pack-dir>`（每個格式各一次）。

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
