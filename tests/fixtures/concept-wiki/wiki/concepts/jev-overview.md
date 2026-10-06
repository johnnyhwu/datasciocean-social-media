---
id: jev-overview
title: Jev 補的是分類器與 LLM 之間的空隙，這個空隙是真的
type_hint: 判斷
context_type: bound_to_source
sources:
- article: jev-overview
  article_title: "TypeSafe AI 的 Jev 號稱快 193.6 倍？第三方實測只到約 25 倍"
  url: https://datasciocean.com/ai-concept/jev-overview/
  sections:
  - 前言
  - 兩條舊路線之間，那塊沒人補上的空隙
  - 非自回歸架構：「一次 forward pass」到底是什麼意思
  - 輸入結構與多問題平行輸入
  - 三種輸出型別：Choice / Score / Noul
  - LLM 的 token 機率不是本來就可以當信心值嗎？為什麼還需要 RLCD？
  - 官方頭條數字怎麼算出來的
  - 「一致率」是什麼意思，為什麼不等於「對不對」？
  - 官方建議情境與明確排除的任務
  - 可持續性存疑
  - 結論
  - 拆解問題不能只拆「窄」，還要拆「淺」
  - 官方自己揭露的失效模式
  first_appearance: true
parent: null
related:
  - schema-valid-not-correct
  - confound-three-questions
  - honest-probability-training
  - decompose-narrow-and-shallow
  - efficiency-accuracy-error-cost
status: active
---

## 主張

```yaml
claims:
- id: c1
  role: thesis
  text: Jev 想補的是傳統分類器與直接呼叫 LLM 之間的空隙：要 LLM 的彈性，又要分類器的速度、成本與型別安全，外加可信賴的機率
  source_quotes:
  - Jev 想補的，正是這兩條路線中間那塊空隙：要路線二的彈性，但要路線一的速度、成本、型別安全，外加一個兩條路線都沒做好的東西——真正可信賴的機率。
  anchor_type: 部落格判斷
  importance: 1
  status: normal
- id: c2
  role: context
  text: Jev 是新創公司 TypeSafe AI 推出的產品，自稱「System One Model」；官方把它叫做「decision layer」或「smart if-statement」，而不是取代 LLM
  source_quotes:
  - 新創公司 TypeSafe AI 結束兩年隱身期，推出一款叫做 Jev 的產品，自稱是「System One Model」
  - 官方把 Jev 叫做「decision layer」或「smart if-statement」，而不是「取代 LLM」
  anchor_type: 官方宣稱
  importance: 2
  status: normal
- id: c3
  role: context
  text: blog 認為，Jev 瞄準的是答案空間已知、但用傳統分類器又太死板的判斷任務，不是開放式生成任務
  source_quotes:
  - 它瞄準的是答案空間已知、但用傳統分類器又太死板的判斷任務，不是開放式生成任務。
  anchor_type: 部落格判斷
  importance: 3
  status: normal
- id: c4
  role: evaluation
  text: Jev 想補的空隙是真的存在的
  source_quotes:
  - Jev 想補的空隙是真的存在的
  anchor_type: 部落格判斷
  importance: 4
  status: normal
- id: c5
  role: mechanism
  text: 傳統監督式分類器快、便宜、輸出永遠落在預先定義的類別裡，但每換一個任務就要重新標註資料與訓練；直接呼叫 LLM 不需要訓練資料、彈性高，但輸出是自由文字要自己 parse、逐 token 自回歸生成又慢又貴，而且 LLM 講得很篤定，那個篤定感跟實際答對的機率之間沒有可信賴的對應關係
  source_quotes:
  - 優點是快、便宜、型別安全，輸出永遠落在預先定義好的類別裡；缺點是每換一個任務就要重新標註資料、重新訓練，而且完全不懂自然語言指令。
  - 優點是不用訓練資料，用自然語言描述任務就能做零樣本或少樣本判斷，彈性極高。
  - 輸出是自由文字，得自己寫 parsing 邏輯去抓答案，格式隨時可能跑掉
  - 逐 token 自回歸生成很慢很貴
  - LLM 講得很篤定，但那個「篤定感」跟它實際答對的機率之間沒有可信賴的對應關係
  anchor_type: 背景說明
  importance: 5
  status: normal
- id: c6
  role: mechanism
  text: Jev 想達成的是不需要訓練資料、以 schema 保證輸出型別安全（輸出永遠落在預先定義好的類別裡）、速度與成本接近分類器、機率經過校準
  source_quotes:
  - 需要訓練資料 | 需要 | 不需要 | 不需要
  - 速度/成本 | 快/便宜 | 慢/貴 | 接近分類器
  - 輸出型別安全 | 是 | 否（需自己 parse） | 是（schema 保證）
  - 優點是快、便宜、型別安全，輸出永遠落在預先定義好的類別裡
  anchor_type: 部落格判斷
  qualifiers:
  - text: 校準只是官方宣稱，未經外部驗證
    source_quote: 官方宣稱有校準（未經外部驗證）
  importance: 6
  status: normal
- id: c7
  role: context
  text: 校準是指，把模型所有說「我 80% 確定」的預測收集起來，這些預測裡應該真的有大約 80% 是對的；校準講的不是有沒有機率值，而是這個機率值準不準
  source_quotes:
  - 校準的定義是：如果把模型所有「我 80% 確定」的預測收集起來，這些預測裡應該真的有大約 80% 是對的。
  - 校準講的不是「有沒有機率值」，而是「這個機率值準不準」。
  anchor_type: 背景說明
  comparison_target: 同一批預測實際答對的比例
  importance: 7
  status: normal
- id: c8
  role: mechanism
  text: Jev 的輸入是一份 state（背景資料或上下文）加上多個 typed questions，每個問題都要指定型別，可以一次送多題
  source_quotes:
  - 官方明講的輸入結構是 **state**（背景資料或上下文）加上**多個 typed questions**——每個問題都要指定型別，還要附上該型別需要的參數。可以同時輸入多題，這是設計核心
  anchor_type: 官方宣稱
  importance: 8
  status: normal
- id: c9
  role: mechanism
  text: 依 blog 的整理，Jev 的輸出被限制在 Choice、Score、Noul 三種預先定義好的型別，型別安全就是靠這個保證；三者都可以在同一次 API 呼叫裡混用、平行評估
  source_quotes:
  - Jev 的輸出被限制在三種預先定義好的型別，型別安全就是靠這個保證的。
  - 三者的共同點是都可以在同一次 API 呼叫裡混用、平行評估。
  anchor_type: 部落格考證
  importance: 9
  status: normal
- id: c10
  role: mechanism
  text: Choice 輸出選中的選項加每個選項的機率與 confidence，最多 255 個選項，適用場景範例是分類與路由；Score 輸出一個可落在等級之間的浮點分數加機率分布與 confidence，有 2 到 10 個有序等級，範例是評分；Noul 輸出一個 0 到 1 之間的機率值、沒有獨立的 confidence 欄位，範例是 guardrail 與二元判斷
  source_quotes:
  - 選中的選項 + 每個選項的機率 + confidence | 最多 255 個選項 | 分類、路由（例如信件該分派給哪個部門）
  - 一個可以落在等級之間的浮點分數 + 機率分布 + confidence | 2–10 個有序等級 | 評分、rubric（例如作文品質幾分）
  - 一個 0–1 之間的機率值，無獨立 confidence 欄位 | 是/否二元 | Guardrail、二元判斷（例如是否含惡意內容）
  anchor_type: 部落格考證
  numeric_kind: non_comparative
  numeric_reason: 規格上限
  importance: 10
  status: normal
- id: c11
  role: anchor
  text: 官方建議的情境有四類：AI-powered workflows 的「smart if-statements」、對每一列資料做決策的 Map-reduce 大數據、即時應用、以及 Verify everything（評分、判斷、驗證、guardrail、偵測 LLM 的 jailbreak）
  source_quotes:
  - AI-powered workflows，「smart if-statements」 | 分類、路由、評分、抽取、分支判斷
  - Map-reduce 大數據 | 對每一列資料做決策（例如替每則評論打分）
  - 即時應用 | 100ms 級延遲，適合 UX 關鍵場景
  - Verify everything | 評分、判斷、驗證、guardrail、偵測 LLM 的 jailbreak
  anchor_type: 官方宣稱
  importance: 11
  status: normal
- id: c12
  role: anchor
  text: 官方明確排除的是聊天、程式生成、需要書面說明或理由的任務、開放式生成、算術計數日期運算、需要可稽核理由的決策，以及一次性複雜推理
  source_quotes:
  - 官方明確排除的則是聊天、程式生成、需要書面說明或理由的任務
  - 開放式生成、算術/計數/日期運算、需要可稽核理由（auditor）的決策，以及一次性複雜推理。
  anchor_type: 官方宣稱
  importance: 12
  status: normal
- id: c13
  role: evaluation
  text: 建議清單的共同點是答案空間已知、可以拆成結構化判斷；排除清單的共同點是需要輸出自然語言或單次深度推理。blog 認為 Jev 不是刻意不做這些事，而是架構上就做不到
  source_quotes:
  - 排除清單的共同點是都需要「輸出自然語言」或「單次深度推理」；建議清單的共同點是都屬於「答案空間已知、可以拆成結構化判斷」的任務。
  - 它不是「刻意」不做這些事，而是「架構上就做不到」
  anchor_type: 部落格判斷
  qualifiers:
  - text: 官方沒有公開具體模型架構，只說是 a new architecture, a new sampler, and a new training algorithm
    source_quote: 官方只說「a new architecture, a new sampler, and a new training algorithm」，沒有發表論文。
  importance: 13
  status: normal
- id: c14
  role: evaluation
  text: 效率優勢的方向有官方 benchmark 與多個獨立第三方測試印證，只是幅度被大幅美化
  source_quotes:
  - 官方公布的 4-workflow benchmark 和多個獨立第三方測試也都證實了它的效率優勢方向不假——只是幅度被大幅美化。
  anchor_type: 部落格判斷
  importance: 14
  status: normal
- id: c15
  role: anchor
  text: 官方 4-workflow benchmark 中，Jev 的一致率是 67.8%，GPT-5.6 Sol 是 74.1%；一致率的參考答案不是人工標註的真值，而是 GPT-6 Astra 與 Fable 5.1 兩個模型的平均答案
  source_quotes:
  - Jev | 67.8% | $0.0004 | 0.4s
  - GPT-5.6 Sol | 74.1% | $0.0836 | 10–38s 區間內
  - 「參考答案」不是人工標註的真值（ground truth），而是用 GPT-6 Astra 跟 Fable 5.1 兩個模型的平均答案當標準答案。
  anchor_type: 官方宣稱
  comparison_target: GPT-5.6 Sol 的一致率；參考答案是 GPT-6 Astra 與 Fable 5.1 兩個模型的平均答案
  importance: 15
  status: normal
- role: evaluation
  text: blog 認為，在這張表裡 67.8% 一致率的設定下（參考答案是 GPT-6 Astra 與 Fable 5.1 兩個模型的平均答案），Jev 的「準確率」本質上量的是 Jev 的答案跟這兩個前沿模型有多像，不是 Jev 的答案客觀上對不對
  source_quotes:
  - 這張表裡 67.8% 一致率的「參考答案」不是人工標註的真值（ground truth），而是用 GPT-6 Astra 跟 Fable 5.1 兩個模型的平均答案當標準答案。
  - 這代表 Jev 的「準確率」本質上量的是「Jev 的答案跟這兩個前沿模型有多像」，不是「Jev 的答案客觀上對不對」
  anchor_type: 部落格判斷
  comparison_target: GPT-6 Astra 與 Fable 5.1 兩個模型的平均答案（參考答案）
  status: normal
  id: c16
  importance: 16
- id: c17
  role: evaluation
  text: blog 認為 Jev 的技術路線是紮實的，問題主要出在敘事層面的誇大；技術本身該打的折扣包括準確率與架構未公開
  source_quotes:
  - Jev 的技術路線是紮實的，問題主要出在敘事層面的誇大
  - 技術本身該打的折扣——準確率中段班、架構未公開——前面已經談過了。
  anchor_type: 部落格判斷
  importance: 17
  status: normal
- id: c18
  role: evaluation
  text: 錯誤代價低、量大的任務（分類、路由、guardrail 前置篩選）用 Jev 這類產品的效率權衡非常划算；錯誤代價高的任務（金流、法遵、需要可稽核理由的判斷）應該保留前沿大模型，或只把 Jev 當第一道篩選
  source_quotes:
  - 錯誤代價低、量大的任務——分類、路由、guardrail 前置篩選——Jev 這類產品的效率權衡非常划算；錯誤代價高的任務——金流、法遵、需要可稽核理由的判斷——應該保留前沿大模型，或只把 Jev 當第一道篩選。
  anchor_type: 部落格判斷
  importance: 18
  status: normal
- id: c19
  role: context
  text: 官方文件有專門一頁叫 jaggedness（參差不齊，模型在某些地方表現很好、某些地方莫名其妙地差），列出 Jev 的失效模式
  source_quotes:
  - 官方文件有專門一頁叫 jaggedness（意思是「參差不齊」，模型在某些地方表現很好、某些地方莫名其妙地差）。
  anchor_type: 官方宣稱
  importance: 19
  status: normal
- id: c20
  role: anchor
  text: 字面解讀：只答寫出來的問題，否定詞、範圍詞、隱含條件都照字面處理，不會自己腦補真正想問的；不是計算機：計數不可靠、誤差隨數量增大，算術必須留在程式碼裡做；日期是文字不是有序量：先後、間隔、是否落在某區間的判斷都不可靠
  source_quotes:
  - 字面解讀 | 只答寫出來的問題，否定詞、範圍詞、隱含條件都照字面處理，不會自己腦補「真正想問的」
  - 不是計算機 | 計數不可靠，誤差隨數量增大；算術必須留在程式碼裡做
  - 日期是文字，非有序量 | 先後順序、間隔長短、是否落在某個區間，這些判斷都不可靠
  anchor_type: 官方宣稱
  importance: 20
  status: normal
- id: c21
  role: anchor
  text: Context rot：state 塞進不相關的內容會拖累準確率，必須先做檢索或過濾，官方原文直接寫「Jev suffers from context rot」；不把 state 當敵意輸入：state 被植入刻意誤導、幫自己辯護的文字，答案會被影響，prompt injection 的風險要自己防；矛盾的指令或 criteria 會讓模型困惑；不生成：需要抽取自由文字時，要先用 regex 或另一個生成模型產生候選，再讓 Jev 從候選裡選
  source_quotes:
  - Context rot | state 塞進不相關的內容會拖累準確率，必須先做檢索或過濾，官方原文直接寫「Jev suffers from context rot」
  - 不把 state 當敵意輸入 | 如果 state 裡被植入了刻意誤導、幫自己辯護的文字，答案會被影響，prompt injection 的風險要自己防
  - 矛盾指令/criteria 會混淆 | 問題裡如果給的判斷標準彼此矛盾，模型會困惑
  - 不生成 | 需要抽取自由文字時，要先用 regex 或另一個生成模型產生候選，再讓 Jev 從候選裡選
  anchor_type: 官方宣稱
  importance: 21
  status: normal
- id: c22
  role: anchor
  text: Every 這個獨立測試方明確觀察到，Jev 在「需要注意到主張不成立」這種需要反覆推敲、質疑表面說法的深思型判斷上會漏掉
  source_quotes:
  - Every 這個獨立測試方明確觀察到，Jev 在「需要注意到主張不成立」這種深思型判斷上會漏掉——需要反覆推敲、質疑表面說法這種多步驟推理的子任務，Jev 表現不好。
  anchor_type: 第三方實測
  importance: 22
  status: normal
```
