---
id: confound-three-questions
title: 看效能對比數字之前，先問三個問題：分母、比法、標準答案
type_hint: 可遷移原則
context_type: evidence_from_single_source
sources:
- article: jev-overview
  article_title: "TypeSafe AI 的 Jev 號稱快 193.6 倍？第三方實測只到約 25 倍"
  url: https://datasciocean.com/ai-concept/jev-overview/
  sections:
  - 前言
  - 兩條舊路線之間，那塊沒人補上的空隙
  - 官方頭條數字怎麼算出來的
  - 「一致率」是什麼意思，為什麼不等於「對不對」？
  - 拆開混淆變因（confound）
  - 第三方獨立驗證的實際數字
  - Confound（混淆變因）的識別習慣
  - 「一致率」不等於「對不對」
  first_appearance: true
parent: null
related:
  - jev-overview
  - efficiency-accuracy-error-cost
  - schema-valid-not-correct
status: active
---

## 主張

```yaml
claims:
- id: c1
  role: thesis
  text: 任何效能對比數字出現之前，先問三個問題：分母怎麼選的、評測方法本身有沒有讓某一方吃虧、參考答案的選擇會不會系統性偏袒某一方
  source_quotes:
  - 任何效能對比數字出現之前，先問三個問題：分母怎麼選的？評測方法本身有沒有讓某一方吃虧，例如被迫用不自然的方式跑？參考答案的選擇會不會系統性偏袒某一方？
  anchor_type: 部落格判斷
  importance: 1
  status: normal
- id: c2
  role: context
  text: Jev 是新創公司 TypeSafe AI 推出的產品，官方把它叫做「decision layer」或「smart if-statement」；官方的頭條數字拿它去比前沿大模型
  source_quotes:
  - 新創公司 TypeSafe AI 結束兩年隱身期，推出一款叫做 Jev 的產品
  - 官方把 Jev 叫做「decision layer」或「smart if-statement」，而不是「取代 LLM」
  - 官方的頭條數字很聳動：比前沿大模型快 193.6 倍、便宜 444.6 倍
  anchor_type: 官方宣稱
  importance: 2
  status: normal
- id: c3
  role: anchor
  text: TypeSafe 官網頭條宣稱 Jev 比前沿大模型快 193.6 倍、便宜 444.6 倍，這是官網上的最佳案例，不是平均值
  source_quotes:
  - 官方的頭條數字很聳動：比前沿大模型快 193.6 倍、便宜 444.6 倍
  - 官方最常被引用的兩個數字是快 193.6 倍、便宜 444.6 倍，這是官網上的最佳案例（best case），不是平均值。
  anchor_type: 官方宣稱
  comparison_target: 前沿大模型（444.6 倍的確切分母模型，官方沒講清楚）
  qualifiers:
  - text: 這是官網上的最佳案例，不是平均值
    source_quote: 這是官網上的最佳案例（best case），不是平均值。
  importance: 3
  status: normal
- id: c4
  role: anchor
  text: blog 說 193.6 倍是拿 Jev 最快的一次去除前沿模型最慢的一次算出來的，分子分母都挑了對自己最有利的極端值；端到端延遲是 Jev 70 到 500 毫秒對前沿模型 3 到 329 秒
  source_quotes:
  - 端到端延遲（70 到 500 毫秒）對比前沿模型的 3 到 329 秒，193.6 倍對應的是拿 Jev 最快的一次去除前沿模型最慢的一次算出來的，分子分母都挑了對自己最有利的極端值。
  anchor_type: 部落格考證
  comparison_target: 前沿模型最慢的一次（3 到 329 秒）
  importance: 4
  status: pending_author_confirmation
- id: c5
  role: evidence
  text: 第三方測出的速度優勢，Every 是對比 Fable 5.1 的 25 倍，Near Here 約 5 倍、對比的是較輕量的模型
  source_quotes:
  - Every 測出 25 倍（對比 Fable 5.1），Near Here 只有約 5 倍（對比較輕量的模型）
  anchor_type: 第三方實測
  comparison_target: Every 對比 Fable 5.1；Near Here 對比較輕量的模型（blog 未指明型號）
  importance: 5
  status: normal
- id: c6
  role: evaluation
  text: 加速倍數高度依賴拿哪個模型當分母；分母模型越重越慢，倍數自然越好看
  source_quotes:
  - 「加速倍數」高度依賴拿哪個模型當分母
  - 分母模型越重越慢，倍數自然越好看
  anchor_type: 部落格判斷
  importance: 6
  status: normal
- id: c7
  role: anchor
  text: 官方的成本倍數約 238 倍，算法是拿 Jev 的 $0.042/MTok 對比 Claude Fable 5.1 的標價 $10/MTok
  source_quotes:
  - 官方拿 Jev 的 $0.042/MTok 對比 Claude Fable 5.1 的**標價** $10/MTok 算出約 238 倍
  anchor_type: 官方宣稱
  comparison_target: Claude Fable 5.1 的標價
  importance: 7
  status: normal
- id: c8
  role: evaluation
  text: 前沿模型廠商實際上有 cache 折扣與 batch 折扣，真實應用成本通常遠低於標價，所以用標價算出的成本倍數，真實倍數會顯著縮小
  source_quotes:
  - 但前沿模型廠商實際上都有 cache 折扣…跟 batch 折扣，真實應用成本通常遠低於標價。
  - 對手用標價、不用 cache/batch 折扣 | 238x/444.6x 成本倍數 | 真實倍數會顯著縮小
  anchor_type: 部落格判斷
  importance: 8
  status: pending_author_confirmation
- id: c9
  role: anchor
  text: 官方沒有把 444.6 倍這個成本倍數的確切分母模型講清楚，只知道是官網最佳案例
  source_quotes:
  - 拿去對比某個更貴的模型算出 444.6 倍，但官方沒有把這個數字的確切分母模型講清楚，只知道是官網最佳案例。
  anchor_type: 部落格考證
  comparison_target: 某個更貴的模型（官方未明說是哪一個）
  importance: 9
  status: normal
- id: c10
  role: anchor
  text: 官方為了讓前沿模型也能輸出跟 Jev 一樣的機率格式，用自己開源的 System One adapter 去包裝這些對手模型
  source_quotes:
  - 官方為了讓前沿模型也能輸出跟 Jev 一樣的機率格式，用了自己開源的 System One adapter 去包裝這些對手模型
  anchor_type: 設計參數
  importance: 10
  status: normal
- id: c11
  role: evaluation
  text: 這個 adapter 讓對手模型的呼叫方式變得不自然，讓對手顯得比原生使用時更慢更貴，可能高估 Jev 的相對優勢
  source_quotes:
  - 這個 adapter 本身會讓對手模型的呼叫方式變得不自然，讓對手顯得比原生使用時更慢更貴
  - System One adapter 拖慢對手 | 延遲/成本倍數 | 可能高估 Jev 相對優勢
  anchor_type: 部落格判斷
  importance: 11
  status: normal
- id: c12
  role: anchor
  text: 官方 4-workflow benchmark 表格裡的一致率，做法是不用人工標註的真值，而是拿 GPT-6 Astra 與 Fable 5.1 兩個模型的平均答案當標準答案；一致率量的是模型答案跟這兩個模型有多像
  source_quotes:
  - 這張表裡 67.8% 一致率的「參考答案」不是人工標註的真值（ground truth），而是用 GPT-6 Astra 跟 Fable 5.1 兩個模型的平均答案當標準答案。
  - 這代表 Jev 的「準確率」本質上量的是「Jev 的答案跟這兩個前沿模型有多像」
  anchor_type: 設計參數
  numeric_kind: non_comparative
  numeric_reason: 名稱
  importance: 12
  status: normal
- id: c13
  role: evaluation
  text: 官方一致率的參考答案偏向 OpenAI 與 Anthropic 系模型，對 DeepSeek 系模型的差距可能被低估
  source_quotes:
  - 參考答案偏向 OpenAI/Anthropic 系 | 67.8% 一致率 | 對 DeepSeek 系模型的差距可能被低估
  anchor_type: 部落格判斷
  importance: 13
  status: pending_author_confirmation
- id: c14
  role: evaluation
  text: 官方的 workflow 是自家設計的，一致率可能偏向對 Jev 有利的任務類型
  source_quotes:
  - Workflow 自家設計 | 整體 67.8% 一致率 | 可能偏向對 Jev 有利的任務類型
  anchor_type: 部落格判斷
  importance: 14
  status: normal
- id: c15
  role: anchor
  text: Every 測 37 份文件、777 個判斷，Jev 比 Fable 5.1 快 25 倍，抓瑕疵 7 個抓到 6 個，Fable 5.1 全中
  source_quotes:
  - Every | 37 份文件、777 判斷 | 25x（對比 Fable 5.1） | 580x（對比 Fable 5.1） | 瑕疵抓取：6/7（Fable 5.1 全中 7/7）
  anchor_type: 第三方實測
  comparison_target: Fable 5.1
  importance: 15
  status: normal
- id: c16
  role: anchor
  text: Every 測得 Jev 成本比 Fable 5.1 便宜 580 倍
  source_quotes:
  - Every | 37 份文件、777 判斷 | 25x（對比 Fable 5.1） | 580x（對比 Fable 5.1）
  anchor_type: 第三方實測
  comparison_target: Fable 5.1
  importance: 16
  status: pending_author_confirmation
- id: c17
  role: anchor
  text: Near Here 審核 50 筆真實 listing，Jev 在「準確率/一致率」欄是 96%（blog 沒說明是哪一種），對比 Mistral Small 4 的 84%、Gemini 3.5 Flash-Lite 的 86%
  source_quotes:
  - Near Here | 50 筆真實 listing 審核 | 約 5x | 約 8.6x | 96%（對比 Mistral Small 4 的 84%、Gemini 3.5 Flash-Lite 的 86%）
  anchor_type: 第三方實測
  comparison_target: Mistral Small 4 與 Gemini 3.5 Flash-Lite
  importance: 17
  status: normal
- id: c18
  role: anchor
  text: Good Start Labs 跑 6,003 個 rubric checks，Jev 成本便宜 1.6 倍（對比 DeepSeek V4.1 Flash）；一致率 91.5%（對比 Fable 5.1），DeepSeek 是 93.5%
  source_quotes:
  - Good Start Labs | 6,003 rubric checks | （未測速度） | 1.6x（對比 DeepSeek V4.1 Flash） | 91.5%（對比 Fable 5.1）；DeepSeek 是 93.5%
  anchor_type: 第三方實測
  comparison_target: 成本對比 DeepSeek V4.1 Flash；一致率 91.5% 是對比 Fable 5.1，DeepSeek 是 93.5%
  importance: 18
  status: normal
- id: c19
  role: evaluation
  text: 任何用另一個模型的輸出當 ground truth 的 benchmark，測出來的是「像不像裁判」，不是「客觀對不對」
  source_quotes:
  - 任何用另一個模型的輸出當 ground truth 的 benchmark，測出來的都是「像不像裁判」，不是「客觀對不對」
  anchor_type: 部落格判斷
  importance: 19
  status: normal
- id: c20
  role: mechanism
  text: 因此 Jev 的「準確率」量的是它的答案跟這兩個前沿模型有多像；如果 Jev 跟這兩個模型因同樣原因答錯（shared errors），這個方法完全偵測不出來
  source_quotes:
  - 這代表 Jev 的「準確率」本質上量的是「Jev 的答案跟這兩個前沿模型有多像」，不是「Jev 的答案客觀上對不對」——如果 Jev 跟這兩個模型都因為同樣的原因答錯（shared errors，共享誤差），這個方法完全偵測不出來。
  anchor_type: 部落格判斷
  importance: 20
  status: normal
- id: c21
  role: anchor
  text: 在官方 benchmark 的表格中，Jev 的一致率是 67.8%，GPT-5.6 Terra 是 67.9%、GPT-5.6 Sol 是 74.1%、Claude Opus 5 是 73.1%
  source_quotes:
  - Jev | 67.8% | $0.0004 | 0.4s
  - GPT-5.6 Terra | 67.9% | $0.0304 | 10–38s 區間內
  - GPT-5.6 Sol | 74.1% | $0.0836 | 10–38s 區間內
  - Claude Opus 5 | 73.1% | $0.1761 | 10–38s 區間內
  anchor_type: 官方宣稱
  comparison_target: 各模型互相比較；一致率的參考答案是 GPT-6 Astra 與 Fable 5.1 兩個模型的平均答案
  qualifiers:
  - text: 這張表的一致率，參考答案不是人工標註真值，而是兩個模型的平均答案
    source_quote: 這張表裡 67.8% 一致率的「參考答案」不是人工標註的真值（ground truth），而是用 GPT-6 Astra 跟 Fable 5.1 兩個模型的平均答案當標準答案。
  importance: 21
  status: normal
- id: c22
  role: evaluation
  text: 看到任何「跟前沿模型的一致率 X%」的宣稱，第一個要問的是參考答案是誰定的，是人工標註的真值，還是另一個模型的輸出
  source_quotes:
  - 以後看到任何「跟前沿模型的一致率 X%」這種宣稱，第一個要問的問題就是：參考答案是誰定的？是人工標註的真值，還是另一個模型的輸出？
  anchor_type: 部落格判斷
  importance: 22
  status: normal
```
