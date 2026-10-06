# 程式 A：標記與格式檢查（`check_a.py`）

貼文被改寫過，不能比對字面，所以靠「標記編號」：每個區塊（hook、投影片、Threads 的正文／每則串文／最後一則、caption 第一句）都要標它引用的 claim id，或標「結構」。**引用只證明「有對應」，不證明意思沒走樣**；走樣由忠實者判斷。

`uv run python .claude/skills/make-social-post/scripts/check_a.py out/<series>/<concept>/_build/spec.json`：ERROR 清零才算過；HINT 交給忠實者重點檢查。程式 A 不算審查輪數，撰寫者可自己先跑到通過。

## ERROR（退回）

| 檢查 | 抓什麼 |
|---|---|
| 每個區塊至少引用一條主張，或標「結構」 | 撰寫者自己加的內容 |
| 引用的主張必須存在 | 引用錯 id |
| 引用的主張必須是 `normal` 或 `author_confirmed` | 用了 pending 的主張 |
| 結構區塊不得含數字；字數不得超過 `structure_text_max_chars`（12 字） | 把主張偷偷標成結構來躲檢查 |
| 區塊裡每個數字（逐欄位抽取，不得串接）所屬的引用主張必須有 `comparison_target`（或 `numeric_kind: non_comparative`） | 沒有比較對象的數字 |
| 圖上出現的名稱（拉丁字詞：模型名、系統名）要被引用的主張涵蓋 | 名稱沒有來源 |
| 比較詞與全稱詞（`comparative_words`）出現在貼文，卻不在引用主張的 text、source_quotes、qualifiers 裡 | 派生的比較判斷是最常見的走樣來源 |
| 中文 AI 腔黑名單（`ai_tone_blacklist`）；出現「podcast」 | 風格與規則違反 |
| 被使用的主張，它的每條限定條件（`cid#k`）必須在整則貼文某處被 `quals` 標記帶出 | 壓縮時限定條件被砍 |
| 卡的 `context_type` 是 `evidence_from_single_source` 或 `bound_to_source` 時，脈絡張必須引用 `role: context` 的主張 | 漏交代方法來源 |
| 貼文或系列檔的 `planned_title` 出現 `config/terms.yaml` 左邊的詞（例如「判官」，應寫 Judge） | 用語不一致（導流行引用的文章原標題不檢查） |
| 張數不超過 `slides_max`；文字張補充 40～60 字；圖表版型補充不超過 24 字；脈絡張補充不超過 90 字 | 超長 |
| Threads：正文不超過 500 字；連結只放最後一則；串文與內容投影片一對一；串文描述與圖上文字的二連詞重疊率不超過 40% | 格式違規；描述只是重述圖 |
| caption：第一句不超過 50 字；hashtag 不超過 5 個；系列貼文含系列標籤；整份 spec 不出現 podcast | 格式違規 |
| 系列地圖的 `current` 必須是該系列的成員 | 設定錯誤 |

## HINT（不退回，交忠實者）

| 檢查 | 為什麼不擋 |
|---|---|
| 區塊裡的數字不在引用主張的原文裡 | 寫法可能不同（「八分之一」與 1/8）；要看意思有沒有走樣 |
| 引用了「部落格判斷」的主張，區塊裡卻沒有「我的判斷」字樣（封面與系列地圖除外） | 寫法可能用別的標記，要人看；但忠實者會擋沒標的 |
| 主標字數超過預檢上限 + 10 | 以渲染後的行數為準（程式 B） |

## 回歸測試

`uv run python tests/test_check_a.py`：21 個故意做壞的貼文必須被抓到、2 則正確貼文必須通過（測誤殺）。新增或改動檢查時，先加一個壞貼文案例確認抓得到，再改程式。
