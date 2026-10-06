---
id: decompose-narrow-and-shallow
title: 拆問題不能只拆窄，還要拆淺
type_hint: 可遷移原則
context_type: evidence_from_single_source
sources:
- article: jev-overview
  article_title: "TypeSafe AI 的 Jev 號稱快 193.6 倍？第三方實測只到約 25 倍"
  url: https://datasciocean.com/ai-concept/jev-overview/
  sections:
  - 前言
  - 非自回歸架構：「一次 forward pass」到底是什麼意思
  - 「一次算完」在技術上說不說得通？
  - 輸入結構與多問題平行輸入
  - 三種輸出型別：Choice / Score / Noul
  - 官方建議情境與明確排除的任務
  - 為什麼要把問題拆成很多個具體小題
  - 拆解問題不能只拆「窄」，還要拆「淺」
  - Constrained decoding 能不能做到跟 Jev 一樣的效果？
  - KV cache 加 batch 化：「感覺像一次算完」的工程原理
  - 訓練方法：從 RLHF 到 RLCD 的演化
  first_appearance: true
parent: null
related:
  - jev-overview
status: active
---

## 主張

```yaml
claims:
- id: c1
  role: thesis
  text: 把判斷拆成小題丟給單次前向傳播的模型時，不能只拆到主題夠窄，還要拆到每個子問題本身夠淺，也就是不需要中間推理草稿就能直接判斷
  source_quotes:
  - 拆解子問題時，不能只拆到「主題夠窄」，還要拆到判斷本身夠淺
  - 取決於拆出來的每一個原子問題，是不是可以在「不需要中間推理草稿」的情況下直接判斷
  anchor_type: 部落格判斷
  qualifiers:
  - text: 「單次前向傳播」這個前提是 blog 依機制做的推論，報告本身沒有明講
    source_quote: 這段架構推論報告本身沒有明講，是根據前面已知的機制做的推論。
  importance: 1
  status: normal
- id: c2
  role: context
  text: Jev 是新創公司 TypeSafe AI 推出的產品，輸入是一份 state（背景資料或上下文）加上多個 typed questions，輸出被限制在預先定義好的結構化型別，不生成文字
  source_quotes:
  - 新創公司 TypeSafe AI 結束兩年隱身期，推出一款叫做 Jev 的產品
  - 官方明講的輸入結構是 **state**（背景資料或上下文）加上**多個 typed questions**
  - Jev 的輸出被限制在三種預先定義好的型別，型別安全就是靠這個保證的。
  - Jev 完全不生成文字，前面三種 primitives 的輸出永遠是結構化的值
  anchor_type: 官方宣稱
  importance: 2
  status: normal
- id: c3
  role: context
  text: 自回歸模型一次只產生一個 token，再把它加回輸入產生下一個；Jev 是非自回歸、單次前向傳播（輸入跑一次，就同時算出所有問題的答案，不是一個 token 一個 token 生成），沒有思維鏈（chain-of-thought，先把中間推理步驟講出來當草稿紙）那種機制，是直接從輸入一步跳到輸出，結構上更接近分類器。這是 blog 依前面機制做的推論，報告本身沒有明講
  source_quotes:
  - 自回歸（autoregressive）是指模型一次只產生一個 token，然後把這個 token 加回輸入裡，再產生下一個 token
  - Jev 不是一個 token 一個 token 生成答案，而是用「parallel sampler」機制，單次前向傳播就把所有問題的答案一次全部算出來
  - Jev 是非自回歸、單次前向傳播，它不像自回歸 LLM 那樣，可以先生成一段思考過程
  - Jev 沒有這個草稿紙機制，它是直接從輸入一步跳到輸出，結構上更接近一個分類器
  - 這段架構推論報告本身沒有明講，是根據前面已知的機制做的推論。
  anchor_type: 部落格推論
  qualifiers:
  - text: blog 自己在推論段說，嚴格說這不是真正單一次的 forward pass，官方也沒有揭露具體模型架構
    source_quote: 嚴格說，這不是真正單一次的 forward pass
  importance: 3
  status: normal
- id: c4
  role: mechanism
  text: 拆解有兩個獨立的維度：任務能不能被拆成多個獨立子判斷（不是每個任務都能乾淨拆開），以及拆出來的每個子問題本身要不要做多步驟推理
  source_quotes:
  - 這是兩件獨立的事：任務能不能被拆成多個獨立子判斷，不是每個任務都能乾淨拆開；拆出來的每一個子問題，本身要不要做多步驟推理，即使只是單一小問題。
  anchor_type: 部落格判斷
  importance: 4
  status: normal
- id: c5
  role: anchor
  text: 官方的 meta-rule 是避免問模型可由程式精確計算的東西、避免把多個判斷藏在一個問題裡
  source_quotes:
  - 官方的 meta-rule 是：避免問模型可由程式精確計算的東西；避免把多個判斷藏在一個問題裡。
  anchor_type: 官方宣稱
  importance: 5
  status: normal
- id: c6
  role: mechanism
  text: blog 的理由是，Jev 平行評估、多個問題 batch 化，多問一題的邊際成本極低、幾乎不增加延遲，所以不需要像對一般 LLM 那樣省著問，可以把模糊的複合判斷拆成多個獨立的窄問題一次問完；這個機制是 blog 依一般電腦科學知識的推論，不是官方報告的內容
  source_quotes:
  - 「多問一題」的邊際成本極低，幾乎不增加延遲。
  - 可以放心把一個模糊、複合的判斷拆成好幾個各自獨立、範圍很窄的小問題，一次性平行問完。
  - 這一段是根據一般電腦科學知識的推論，不是官方報告的內容——原始報告完全沒有解釋這個機制細節。
  anchor_type: 部落格推論
  importance: 6
  status: normal
- id: c7
  role: anchor
  text: 以貿易公司授信風險評估為例（假設情境）：與其問籠統的「授信風險高不高」，不如拆成營收成長穩定度評分（Score）、是否有單一供應商佔比超過六成的集中度風險（Noul）、產業景氣位階評分（Score）、過去 12 個月是否延遲付款（Noul）、整體風險分級（Choice）五題，每個判斷來源可追溯、可拆解，還能自己用權重組合子分數
  source_quotes:
  - 與其問一個籠統的問題「這家貿易公司的授信風險高不高？」
  - 'Q1 (Score, 1-5): 近三年營收成長穩定度評分'
  - 'Q2 (Noul):       是否有單一供應商佔比超過 60% 的集中度風險'
  - 'Q3 (Score, 1-5): 產業景氣週期位階評分(景氣循環底部=1,高點=5)'
  - 'Q4 (Noul):       過去 12 個月是否有延遲付款紀錄'
  - 'Q5 (Choice):     整體風險分級 -> [低風險, 中風險, 高風險, 需人工覆核]'
  - 換來的是每個判斷的來源都可追溯、可拆解，可以自己寫程式碼用權重去組合這些子分數
  anchor_type: 部落格舉例
  numeric_kind: non_comparative
  numeric_reason: 假設題設
  qualifiers:
  - text: 這是假設情境
    source_quote: 假設情境是一家貿易公司的授信風險評估
  importance: 7
  status: normal
- id: c8
  role: anchor
  text: Every 這個獨立測試方明確觀察到，Jev 在「需要注意到主張不成立」這種需要反覆推敲、質疑表面說法的深思型判斷上會漏掉
  source_quotes:
  - Every 這個獨立測試方明確觀察到，Jev 在「需要注意到主張不成立」這種深思型判斷上會漏掉——需要反覆推敲、質疑表面說法這種多步驟推理的子任務，Jev 表現不好。
  anchor_type: 第三方實測
  importance: 8
  status: normal
- id: c9
  role: anchor
  text: 上面例子的「營收成長穩定度」要判斷穩定，通常得比較多年數字的變動幅度、排除單次異常值，這可能已經藏了推理；如果是這樣，該由程式碼先算好統計量（例如變異係數），Jev 只判斷「看到這個已經算好的統計量，判斷算不算穩定」
  source_quotes:
  - 要判斷「穩定」通常需要比較多年數字的變動幅度、排除單次異常值的干擾，這可能已經藏了推理。如果是這樣，該由程式碼先算好統計量（例如變異係數），Jev 只負責「看到這個已經算好的統計量，判斷算不算穩定」這種更淺層的判斷。
  anchor_type: 部落格判斷
  importance: 9
  status: normal
- id: c10
  role: evaluation
  text: 如果連拆到最小的那個子問題，答案本身都需要「先這樣想、再那樣想」才能得出，那不管拆得多細，Jev 都不適合；凡是需要先計算、先比較、先排除干擾的前置推理，應該用自己的程式碼先做完，只把最後一步、不需要中間推理的判斷留給 Jev
  source_quotes:
  - 如果連拆到最小的那個子問題，答案本身都需要「先這樣想、再那樣想」才能得出，那不管拆得多細，Jev 都不適合。
  - 凡是需要「先計算、先比較、先排除干擾」這類前置推理的部分，應該用自己的程式碼先做完，只把「最後一步、不需要中間推理的判斷」留給 Jev。
  anchor_type: 部落格判斷
  qualifiers:
  - text: 「單次前向傳播」這個前提是 blog 依機制做的推論，報告本身沒有明講
    source_quote: 這段架構推論報告本身沒有明講，是根據前面已知的機制做的推論。
  importance: 10
  status: normal
- id: c11
  role: evaluation
  text: 這是官方 meta-rule「避免問可由程式計算的東西」的延伸，只是從「數量」的角度推進到「深度」的角度
  source_quotes:
  - 這其實是官方 meta-rule「避免問可由程式計算的東西」這條原則的延伸，只是從「數量」的角度推進到「深度」的角度。
  anchor_type: 部落格判斷
  importance: 11
  status: normal
- id: c12
  role: evaluation
  text: 思維鏈能力來自能不能生成中間過程這個架構特性，不是模型大小或訓練方法決定的；任何非自回歸、單次映射的模型天生都缺這個能力，遇到這類模型第一件事是檢查任務是否偷偷藏了需要多步驟推理的部分
  source_quotes:
  - 思維鏈能力來自「能不能生成中間過程」這個架構特性，不是模型大小或訓練方法決定的——任何非自回歸、單次映射的模型，不只 Jev，天生都缺乏這個能力
  - 遇到這類模型時，第一件事就是檢查任務是否偷偷藏了需要多步驟推理的部分
  anchor_type: 部落格判斷
  qualifiers:
  - text: 「單次前向傳播」這個前提是 blog 依機制做的推論，報告本身沒有明講
    source_quote: 這段架構推論報告本身沒有明講，是根據前面已知的機制做的推論。
  importance: 12
  status: normal
- id: c13
  role: mechanism
  text: 「體感上像一次算完」不是魔法，而是「共用部分只算一次」（KV cache）加上「多個請求疊在一起丟進 GPU」（batch 化）兩個業界通用技巧疊加的效果
  source_quotes:
  - 不是魔法，是「共用部分只算一次」（KV cache）加上「多個請求疊在一起丟進 GPU」（batch 化）兩個業界通用技巧疊加的體感效果。
  anchor_type: 部落格推論
  qualifiers:
  - text: 這是 blog 依一般電腦科學知識做的推論，不是官方報告的內容
    source_quote: 這一段是根據一般電腦科學知識的推論，不是官方報告的內容——原始報告完全沒有解釋這個機制細節。
  importance: 13
  status: normal
- id: c14
  role: context
  text: 依 blog 的描述，Jev 用「parallel sampler」機制，單次前向傳播就把所有問題的答案一次算出來；官方沒有揭露具體模型架構
  source_quotes:
  - Jev 不是一個 token 一個 token 生成答案，而是用「parallel sampler」機制，單次前向傳播就把所有問題的答案一次全部算出來
  - 官方沒有揭露的部分是具體模型架構
  anchor_type: 部落格考證
  qualifiers:
  - text: blog 自己在推論段說，嚴格說這不是真正單一次的 forward pass
    source_quote: 嚴格說，這不是真正單一次的 forward pass
  importance: 14
  status: normal
- role: mechanism
  text: 官方明講，多問幾題幾乎不增加時間，因為是平行評估，不是排隊算
  source_quotes:
  - 多問幾題幾乎不增加時間，因為是平行評估，不是排隊算
  anchor_type: 官方宣稱
  status: normal
  id: c15
  importance: 15
- id: c16
  role: mechanism
  text: KV cache 把每個 token 在每層 attention 產生的 Key、Value 向量存起來，輸入內容不變就不用重算；後面的 token 回頭看前面的 token 時，拿自己的 Query 去跟存好的 Key/Value 比對
  source_quotes:
  - Transformer 每一層在算 attention 時，每個 token 都會產生一組 Key、Value 向量，後面的 token 要「回頭看」前面的 token，靠的就是拿自己的 Query 去跟前面存好的 Key/Value 做比對。
  - 這些向量一旦算出來，只要輸入內容不變就不用重算——KV cache 就是把算好的向量存起來重複使用。
  anchor_type: 背景說明
  importance: 16
  status: normal
- id: c17
  role: anchor
  text: 帶數字走一次（假設的例子）：state 有 500 個 token、3 個問題各 10 個 token，沒有 KV cache 要把 state 重算三次，總計算量約 1,530；用單一 KV cache，state 只算一次，總計算量約 530
  source_quotes:
  - 帶數字走一次：假設 state（背景資料）是 500 個 token，有 3 個問題各 10 個 token。
  - 總計算量約 510 x 3 = 1,530
  - 總計算量約 500 + 10 + 10 + 10 = 530
  anchor_type: 部落格舉例
  comparison_target: 沒有 KV cache、每個問題都把 state 重算一次的做法
  importance: 17
  status: normal
- id: c18
  role: mechanism
  text: 平行評估是把多個問題一起送進 GPU 算，而不是排隊一題一題算；GPU 擅長同時對一堆數字做一樣的運算，把三題疊成一個 batch，花的時間幾乎跟丟一題差不多
  source_quotes:
  - 把多個問題一起送進 GPU 算，而不是排隊一題一題算。GPU 本質上擅長「同時對一堆數字做一樣的運算」，把三題疊成一個 batch，幾乎跟丟一題所花的時間差不多。
  anchor_type: 背景說明
  importance: 18
  status: normal
- id: c19
  role: evaluation
  text: blog 推論：「一次算完」的體感可由 KV cache 省掉重複計算加上 batch 化省掉排隊等待兩個技巧疊加做到，嚴格說這不是真正單一次的 forward pass；Jev 實際怎麼做到，官方沒有揭露具體模型架構
  source_quotes:
  - 嚴格說，這不是真正單一次的 forward pass，而是「KV cache 省掉重複計算」加上「batch 化省掉排隊等待」兩個技巧疊加後，在體感延遲上表現得像一次算完。
  - 這一段是根據一般電腦科學知識的推論，不是官方報告的內容——原始報告完全沒有解釋這個機制細節。
  - 官方沒有揭露的部分是具體模型架構
  anchor_type: 部落格推論
  importance: 19
  status: normal
- id: c20
  role: evaluation
  text: KV cache 這個技巧不是 Jev 的專屬發明，vLLM 這類推論框架、Anthropic API 都有類似機制
  source_quotes:
  - 這個技巧不是 Jev 的專屬發明，vLLM 這類推論框架、Anthropic API 都有類似機制。
  anchor_type: 背景說明
  importance: 20
  status: normal
- id: c21
  role: evidence
  text: 開發者 Harsha Gundala 沒有重新訓練模型，只用現成的 Qwen2.5 搭配「平行評估 schema」加「單一 KV cache」，就做出比逐 token 解碼快 5.6 到 7.0 倍、100% schema 合法的效果
  source_quotes:
  - 開發者 Harsha Gundala 沒有重新訓練模型，只用現成的 Qwen2.5，搭配「平行評估 schema」加上「單一 KV cache」這兩個工程技巧，就做出比逐 token 解碼快 5.6 到 7.0 倍、100% schema 合法的效果。
  anchor_type: 外部研究引用
  comparison_target: 逐 token 解碼
  importance: 21
  status: normal
- id: c22
  role: mechanism
  text: Constrained decoding（生成時用文法或 schema 限制每一步只能選合法 token）能保證輸出符合 schema，但仍然逐 token 生成，只是每一步候選詞被縮小，不會自動變成一次全部算完，也不管答案的信心值可不可信
  source_quotes:
  - Constrained decoding（在生成時用文法或 schema 限制每一步只能選合法的 token）確實可以保證輸出一定符合 schema
  - constrained decoding 本身還是逐 token 生成，只是每一步候選詞被縮小——問 10 個問題，還是得跑 10 次以上的生成流程，不會自動變成「一次全部算完」。
  - constrained decoding 只管格式合不合法，不管這個答案的信心值可不可信
  anchor_type: 背景說明
  importance: 22
  status: normal
- id: c23
  role: anchor
  text: Hacker News 上的社群猜測，Jev 可能是 text-diffusion（整段同時去噪生成），也可能是 encoder-only 加上 classification heads（每個問題當成一個獨立分類頭）；TypeSafe 兩種都沒證實，只回應暫時保密
  source_quotes:
  - Hacker News 上的社群猜測可能是 text-diffusion（整段同時去噪生成），也可能是 encoder-only 加上 classification heads（每個問題當成一個獨立分類頭），但 TypeSafe 兩種都沒證實，只回應「暫時保密，論文可能之後發表」。
  anchor_type: 社群評論
  importance: 23
  status: normal
```
