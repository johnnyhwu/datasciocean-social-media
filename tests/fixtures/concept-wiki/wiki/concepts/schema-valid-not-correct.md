---
id: schema-valid-not-correct
title: 「格式保證合法」不等於「答案正確」
type_hint: 可遷移原則
context_type: evidence_from_single_source
sources:
  - article: jev-overview
    article_title: "TypeSafe AI 的 Jev 號稱快 193.6 倍？第三方實測只到約 25 倍"
    url: https://datasciocean.com/ai-concept/jev-overview/
    sections:
      - 前言
      - 非自回歸架構：「一次 forward pass」到底是什麼意思
      - 生態系採用狀況與批判性評價
      - 「不會幻覺」這句話，問題出在哪
    first_appearance: true
parent: null
related:
  - jev-overview
  - confound-three-questions
status: active
---

## 主張

```yaml
claims:
  - id: c1
    role: thesis
    text: 「不會幻覺」只保證輸出格式合法，不保證答案正確
    source_quotes:
      - "「不會幻覺」只保證輸出格式合法，不保證答案正確"
    anchor_type: 部落格判斷
    importance: 1
    status: normal
  - id: c2
    role: context
    text: Jev 是新創公司 TypeSafe AI 推出的產品，官方宣稱它「不會產生幻覺」
    source_quotes:
      - "新創公司 TypeSafe AI 結束兩年隱身期，推出一款叫做 Jev 的產品"
      - "還宣稱「不會產生幻覺」"
    anchor_type: 官方宣稱
    importance: 2
    status: normal
  - id: c2b
    role: mechanism
    text: 依 blog 的說明，Jev 輸出端每題答案都被限制在預先定義好的型別，所以不存在輸出格式跑掉的情況
    source_quotes:
      - "輸出端因為每題答案都被限制在預先定義好的型別，不存在「格式跑掉」這件事。"
    anchor_type: 部落格考證
    importance: 2
    status: normal
  - id: c3
    role: anchor
    text: 官方自己在 blog 承認，圖表上的 0% 錯誤率不是實測出來的，而是因為「schema 匹配是被保證的」，所以有信心把 0% 放進圖表
    source_quotes:
      - "官方自己在 blog 承認，0% 錯誤率這個數字不是實測出來的，而是「schema 匹配是被保證的，所以我們可以有信心地把 0% 放進圖表」。"
    anchor_type: 官方宣稱
    comparison_target: 經驗上驗證過的數字（blog 原話；這個 0% 不是）
    importance: 3
    status: normal
  - id: c4
    role: mechanism
    text: 這個 0% 是一個邏輯上必然成立的數字，因為型別系統被設計成不可能輸出非法格式
    source_quotes:
      - "這是一個邏輯上必然成立的數字——型別系統設計成不可能輸出非法格式"
    anchor_type: 部落格考證
    comparison_target: 經驗上驗證過的數字（blog 原話；這個 0% 不是）
    importance: 4
    status: normal
  - id: c5
    role: anchor
    text: 創辦人 Almeida 本人在 Hacker News 上也承認 Jev 會「schema 合法但事實答錯」
    source_quotes:
      - "創辦人 Almeida 本人在 Hacker News 上也直接承認 Jev 會「schema 合法但事實答錯」"
    anchor_type: 官方宣稱
    importance: 5
    status: normal
  - id: c6
    role: anchor
    text: Hacker News 最高票留言指出：型別安全保證的是「格式不會錯」，不保證「答案不會錯」
    source_quotes:
      - "Hacker News 最高票留言"
      - "型別安全保證的是「格式不會錯」，不保證「答案不會錯」。"
    anchor_type: 社群評論
    importance: 6
    status: normal
  - id: c7
    role: evaluation
    text: 官方把兩種性質完全不同的「0%」並排放在同一張圖表上，是這場爭議的根源
    source_quotes:
      - "這兩種「0%」的性質完全不同，官方把它們並排放在同一張圖表上，是這場爭議的根源。"
    anchor_type: 部落格判斷
    qualifiers:
      - text: blog 只說明了其中一種 0% 是邏輯必然而非實測，另一種 0% 是什麼，blog 原句語意含混
        source_quote: "不是一個經驗上驗證過的數字——答案對不對。"
    importance: 7
    status: pending_author_confirmation
  - id: c8
    role: evaluation
    text: 創辦人承認 Jev 會「schema 合法但事實答錯」，blog 認為這代表連官方自己都不否認這個區分；在「不會幻覺」的爭議上，爭議點純粹在於行銷用詞「no hallucination」有沒有誠實傳達這個區分，而不是技術本身有問題
    source_quotes:
      - "創辦人 Almeida 本人在 Hacker News 上也直接承認 Jev 會「schema 合法但事實答錯」"
      - "代表連官方自己都不否認這個區分，爭議點純粹在於行銷用詞（「no hallucination」）有沒有誠實傳達這個區分，而不是技術本身有問題。"
    anchor_type: 部落格判斷
    importance: 8
    status: normal
```
