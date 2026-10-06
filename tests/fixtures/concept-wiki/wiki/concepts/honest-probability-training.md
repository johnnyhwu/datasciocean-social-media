---
id: honest-probability-training
title: RLHF 為什麼讓機率過度自信，與適當計分規則為什麼讓誠實拿高分
type_hint: 可遷移原則
context_type: evidence_from_single_source
sources:
- article: jev-overview
  article_title: "TypeSafe AI 的 Jev 號稱快 193.6 倍？第三方實測只到約 25 倍"
  url: https://datasciocean.com/ai-concept/jev-overview/
  sections:
  - 訓練方法：從 RLHF 到 RLCD 的演化
  - Reward model：另外訓練一個模型來打分
  - PPO：reward 分數怎麼實際調整模型參數
  - LLM 的 token 機率不是本來就可以當信心值嗎？為什麼還需要 RLCD？
  - 前言
  - 強化學習的基本框架
  - RLHF vs. RLVR：reward 從哪裡來的兩種路線
  - RLCD 本身：reward 怎麼設計成「校準」而不是「討好」
  - RLCD 的訓練資料長什麼樣？模型到底學到什麼？
  - RLHF / RLVR / RLCD 的 reward 來源判斷框架
  - Proper scoring rule：誠實預測在數學上有必然優勢
  first_appearance: true
parent: null
related:
  - jev-overview
status: active
---

## 主張

```yaml
claims:
- role: thesis
  text: RLHF 讓 token 機率變得過度自信，是因為優化目標本身就沒有把校準放進去；適當計分規則（proper scoring rule）則是反過來，讓誠實報告真實機率的期望分數最高
  source_quotes:
  - 模型的 token 機率之所以變得過度自信，是這整條訓練流程的副作用，不是誰故意設計出來的錯誤，而是優化目標本身就沒有把校準放進去。
  - 一個適當的計分規則，必須讓模型在誠實報告自己真實機率的時候，拿到的期望分數是最高的；如果模型故意誇大或縮小機率，想討好、想聽起來自信，它的期望分數反而會變差。
  anchor_type: 部落格判斷
  status: normal
  id: c1
  importance: 1
- id: c2
  role: evidence
  text: LLM 在做完 RLHF 之後，token 機率會變得過度自信，這是業界公認、有實證研究支持的現象
  source_quotes:
  - 業界公認、有實證研究支持的現象是，LLM 在做完 RLHF 之後，token 機率會變得過度自信
  anchor_type: 外部研究引用
  importance: 2
  status: normal
- id: c3
  role: mechanism
  text: 有機率值不等於這個機率值可信，這兩件事要分開看；blog 認為整條 RLHF 訓練流程從頭到尾都沒有任何環節在乎機率值是不是真實反映了不確定性
  source_quotes:
  - 問題出在「有機率值」不等於「這個機率值可信」，這兩件事要分開看，而分開看的關鍵詞就是「校準」。
  - 整個 RLHF 流程從頭到尾都沒有任何一個環節在乎「這個 token 的機率值是不是真實反映了不確定性」。
  anchor_type: 部落格判斷
  importance: 3
  status: normal
- id: c4
  role: context
  text: 標準 RLHF 先給人類評分員看同一個問題的兩個回答，請他們選哪個比較好，收集大量比較資料；再訓練一個獨立的 reward model 模仿這種偏好，之後就能自動幫新回答打分；接著用 PPO 把生成高分回答的機率往上調、低分的往下調
  source_quotes:
  - 標準 [RLHF](../llm-fine-tuning-rlhf/) 的解法是先訓練另一個獨立的模型，專門模仿人類打分的行為，這個模型叫 reward model（獎勵模型）。
  - 給他們看同一個問題的兩個不同回答 A 跟 B，請他們選「A 比較好」還是「B 比較好」，收集大量這種比較資料
  - 訓練完成後，這個模型就可以自動幫任何新的回答打分了，不用真人即時介入。
  - PPO 演算法把生成這個回答的過程中每一個 token 被選中的機率往上或往下調一點點——reward 高就增加生成類似回答的機率，reward 低就降低。
  anchor_type: 背景說明
  importance: 4
  status: normal
- id: c5
  role: mechanism
  text: 人類評分員只做過 A 比 B 好的相對比較；標準 reward model 的 loss 只在乎 A 的分數是否大於 B，不管絕對數值
  source_quotes:
  - 人類只做了「A 跟 B 比，A 比較好」這種相對比較，沒有人說過「A 值 8.3 分、B 值 3.1 分」這種絕對數字
  - 這個 loss 只在乎「A 分數大於 B 分數」這個相對關係，完全不管 A、B 的絕對數值是多少
  anchor_type: 背景說明
  importance: 5
  status: normal
- id: c6
  role: mechanism
  text: blog 認為，因此標準 reward model 訓練出來的分數天生就不是校準過的機率，只是一個排序用的相對分數
  source_quotes:
  - 這代表標準 reward model 訓練出來的分數，天生就不是「校準過的機率」，只是一個排序用的相對分數。
  anchor_type: 部落格判斷
  importance: 6
  status: normal
- id: c7
  role: mechanism
  text: RLHF 的目標是讓人類評分員覺得回答好，不是讓機率誠實反映不確定性；講得斬釘截鐵的回答往往比誠實說不太確定的更討喜、拿到更高分。blog 指出，模型輸出「是」這個 token 的機率常常被訓練得逼近極端值，失去中間層次的區分度
  source_quotes:
  - RLHF 訓練的目標是「讓人類評分員覺得這個回答好」，不是「讓機率值誠實反映不確定性」，一個講得斬釘截鐵的回答往往比一個誠實說「我不太確定」的回答更討喜、拿到更高分。
  - 輸出「是」這個 token 的機率常常被訓練得逼近 1.0 或 0.0，失去中間層次的區分度
  anchor_type: 部落格判斷
  importance: 7
  status: normal
- id: c8
  role: evidence
  text: OpenAI 在 GPT-4 技術報告裡展示過：預訓練階段模型的 logprob 校準得還不錯，做完 RLHF 之後校準明顯變差
  source_quotes:
  - OpenAI 自己在 GPT-4 技術報告裡展示過這個現象：預訓練階段的模型 logprob 校準得還不錯，但做完 RLHF 之後校準明顯變差
  anchor_type: 外部研究引用
  comparison_target: 同一個模型在預訓練階段與 RLHF 之後的校準
  numeric_kind: non_comparative
  numeric_reason: 名稱
  importance: 8
  status: normal
- id: c9
  role: evaluation
  text: Jev 的核心賣點是校準過的機率，來自一套叫 RLCD 的訓練方法；官方文件的立場是 RLCD 訓練目標明確改成「優化校準決策」而非「優化人類偏好」。但 RLCD 訓練出的機率真的比較準，目前只是 TypeSafe 官方的自我宣稱，Jev 的校準曲線沒有公開，還沒被獨立驗證；這跟 RLHF 讓校準變差的現象（有 GPT-4 技術報告支持）不同
  source_quotes:
  - Jev 的核心賣點是「校準過的機率」，而這個能力來自一套叫做 RLCD 的訓練方法。
  - 官方文件（docs.typesafe.ai 的 ML primer）明講立場
  - RLCD 訓練目標明確改成「優化校準決策」而非「優化人類偏好」
  - Jev 自己的校準曲線也沒有公開，所以「RLCD 訓練出來的機率真的比較準」目前只是 TypeSafe 官方的自我宣稱，還沒有被獨立驗證過。
  - 後者是有公開研究（GPT-4 技術報告）支持的既定事實，前者還停留在廠商自己的說法階段。
  anchor_type: 官方宣稱
  numeric_kind: non_comparative
  numeric_reason: 名稱
  qualifiers:
  - text: 未經獨立驗證，校準曲線未公開
    source_quote: Jev 自己的校準曲線也沒有公開
  importance: 9
  status: normal
- id: c10
  role: context
  text: 強化學習的基本框架是 Agent 做出 Action、得到一個數字 Reward；reward 高以後更容易重複該動作，低就比較不會做。RLHF、RLVR、RLCD 的訓練機制相同，差別只在 reward 怎麼決定
  source_quotes:
  - Reward（反饋）是主人給的零食，一個數字，越高代表這個動作越好。
  - reward 高，以後更容易重複這個動作；reward 低，以後比較不會做。
  - 訓練「機制」是一樣的，差別只在「零食怎麼決定要不要給」。
  anchor_type: 背景說明
  qualifiers:
  - text: 官方沒有公開 RLCD 的 reward 怎麼跟 PPO 這類 policy gradient 演算法接軌
    source_quote: reward 怎麼跟 PPO 這類 policy gradient 演算法接軌
  importance: 10
  status: normal
- id: c11
  role: mechanism
  text: RLHF 的 reward 來自另一個模型的主觀判斷：先訓練一個 reward model 模仿人類偏好，適用主觀、沒有標準答案的任務；它繼承人類評分員的偏見，容易被講得篤定唬住，訓練出「討好」
  source_quotes:
  - 另外訓練出來的 reward model（模仿人類偏好） | 直接用規則或程式判斷答案對不對，不需要額外訓練模型
  - 主觀、沒有標準答案的任務（寫作品質、對話語氣）
  - 繼承人類評分員的偏見，容易被講得篤定唬住
  - RLHF 的 reward 是另一個模型的主觀判斷，訓練出「討好」
  anchor_type: 部落格判斷
  importance: 11
  status: normal
- id: c12
  role: mechanism
  text: RLVR 的 reward 來自規則或程式直接判斷答案對不對，不需要額外訓練 reward model，只適用有明確對錯的任務（數學題答案對不對、程式碼能不能通過測試）
  source_quotes:
  - 直接用規則或程式判斷答案對不對，不需要額外訓練模型
  - 客觀、有明確對錯的任務（數學題答案對不對、程式碼能不能通過測試）
  - RLVR 的 reward 是規則驗證對錯，只適用有標準答案的任務
  anchor_type: 背景說明
  importance: 12
  status: normal
- id: c13
  role: mechanism
  text: RLCD 是 Jev 的訓練方法，reward 不是由另一個模型的主觀判斷給的，而是用一條數學公式（proper scoring rule，適當計分規則），根據模型猜的機率與實際發生的結果計算；誠實報告真實機率時期望分數最高，訓練出「誠實的機率」
  source_quotes:
  - Jev 的核心賣點是「校準過的機率」，而這個能力來自一套叫做 RLCD 的訓練方法。
  - reward 不是由「另一個模型的主觀判斷」給的，而是直接用一條數學公式，根據「猜的機率」和「實際發生的結果」計算出來。
  - RLCD 的 reward 是數學公式（proper scoring），訓練出「誠實的機率」
  anchor_type: 部落格考證
  qualifiers:
  - text: 官方只寫高層描述，沒有公開具體用哪一種 proper scoring rule
    source_quote: 官方只寫「RLCD 訓練 TypeSafe 回傳決策與校準機率」這樣的高層描述，沒有公開具體用的是哪一種 proper scoring rule
  - text: RLCD 訓練出的機率真的比較準，目前只是 TypeSafe 官方的自我宣稱，還沒被獨立驗證
    source_quote: 「RLCD 訓練出來的機率真的比較準」目前只是 TypeSafe 官方的自我宣稱，還沒有被獨立驗證過
  - text: RLCD 的架構細節、reward function 設計、訓練資料來源、校準曲線全數未公開，外界無法完全驗證
    source_quote: RLCD 的架構細節、reward function 設計、訓練資料來源、校準曲線全數未公開，外界無法完全驗證。
  importance: 13
  status: normal
- id: c14
  role: anchor
  text: RLCD 的任務沒有在生成當下可用規則驗證的標準答案，但最終有實際發生的結果可當訓練標籤，所以不是完全沒有真值，而是真值要靠後續觀察或標註取得；RLCD 需要大量實際發生的結果當標籤，blog 指出 TypeSafe 是怎麼取得這些標籤的，並沒有交代
  source_quotes:
  - 不是完全沒有真值，而是真值不能在生成當下用規則算出來，只能靠後續觀察或標註取得。
  - 但 RLCD 需要「大量實際發生的結果」當標籤
  - 報告完全沒有交代 TypeSafe 是怎麼取得這些實際結果標籤的，這是訓練資料來源上的一塊資訊落差。
  anchor_type: 部落格判斷
  importance: 14
  status: normal
- id: c15
  role: evaluation
  text: RLCD 卡在 RLHF 與 RLVR 中間：它處理的任務沒有非黑即白的標準答案，不像數學題，但又不想像 RLHF 一樣讓 reward model 只學會討好而犧牲機率的誠實度
  source_quotes:
  - RLCD 剛好卡在 RLHF 跟 RLVR 中間那個縫隙——它要處理的任務（例如「這筆交易有 65% 機率異常」）沒有非黑即白的標準答案，不像數學題，但又不想像 RLHF 一樣讓 reward model 只學會「討好」而犧牲機率的誠實度。
  anchor_type: 部落格判斷
  qualifiers:
  - text: blog 隨後修正：這個任務最終仍有實際發生的結果可當標籤，不是完全沒有真值
    source_quote: 不是完全沒有真值，而是真值不能在生成當下用規則算出來
  importance: 15
  status: normal
- id: c16
  role: mechanism
  text: 適當計分規則（proper scoring rule）讓預測者誠實報告自己的真實機率時拿到最高的期望分數；故意誇大或縮小機率來討好或顯得自信，期望分數反而變差
  source_quotes:
  - 一個適當的計分規則，必須讓模型在誠實報告自己真實機率的時候，拿到的期望分數是最高的；如果模型故意誇大或縮小機率，想討好、想聽起來自信，它的期望分數反而會變差。
  anchor_type: 背景說明
  importance: 16
  status: normal
- id: c17
  role: context
  text: Brier score 是一種 proper scoring rule，公式是預測機率 p 與結果 y 之差的平方；結果發生記為 1、沒發生記為 0，分數越低代表預測越好。當真實值只能是 0 或 1 時，squared error 套用在機率預測上就叫 Brier score
  source_quotes:
  - Brier score（一種 proper scoring rule）
  - Brier score} = (p - y)^2
  - 其中結果…發生記為 1，沒發生記為 0，分數越低代表預測越好。
  - 當「真實值」被限制成只能是 0 或 1 時，squared error 套用在機率預測上，就叫做 Brier score
  anchor_type: 背景說明
  numeric_kind: non_comparative
  numeric_reason: 定義
  importance: 17
  status: normal
- id: c18
  role: context
  text: 校準是指，把模型所有說「我 80% 確定」的預測收集起來，這些預測裡應該真的有大約 80% 是對的；講的不是有沒有機率值，而是這個機率值準不準
  source_quotes:
  - 校準的定義是：如果把模型所有「我 80% 確定」的預測收集起來，這些預測裡應該真的有大約 80% 是對的。
  - 校準講的不是「有沒有機率值」，而是「這個機率值準不準」。
  anchor_type: 背景說明
  comparison_target: 同一批預測實際答對的比例
  importance: 18
  status: normal
- id: c19
  role: anchor
  text: 假設某筆交易真正的異常機率是 65%（這是上帝視角才知道的真值，模型不知道），期望分數是用這個真實機率加權算的：誠實猜 0.65 的期望 Brier score 是 0.2275，想講得篤定而猜 0.97 的期望 Brier score 約 0.33，誠實猜反而拿到比較好的分數
  source_quotes:
  - 假設真實世界裡，這筆交易真正的異常機率是 65%——這是上帝視角才知道的真值，模型不知道。
  - 期望 Brier(用真實機率加權) = 0.65×0.1225 + 0.35×0.4225 = 0.2275
  - 情況 B:模型想「講得篤定一點討好人」,猜 0.97
  - 期望 Brier(一樣用真實機率加權) = 0.65×0.0009 + 0.35×0.9409 ≈ 0.3298
  - 結果是 0.2275（誠實）小於 0.3298（過度自信），分數越低越好，誠實猜 0.65 反而拿到比較好的分數。
  anchor_type: 數學推導
  comparison_target: 誠實猜 0.65 與過度自信猜 0.97 互相比較
  qualifiers:
  - text: 前提是真實世界的結果服從 65/35 的分布
    source_quote: 只要真實世界的結果服從那個 65/35 的分布
  importance: 19
  status: normal
- id: c20
  role: anchor
  text: 假設訓練資料有 100 筆特徵幾乎一樣的交易，其中 65 筆最後異常、35 筆正常：模型每次都賭機率 1，平均 Brier score 是 0.35；輸出誠實的比例 0.65，平均是 0.2275，後者勝過每次都賭 1
  source_quotes:
  - 假設訓練資料裡有 100 筆特徵幾乎一樣的交易，但實際結果不同，65 筆最後真的異常、35 筆最後正常，這是資料本身的隨機性。
  - 這100筆的平均 Brier = 35/100 = 0.35
  - 這100筆的平均 Brier = (7.96+14.79)/100 = 0.2275
  - 0.2275 小於 0.35，輸出 0.65 這個誠實的比例，平均表現贏過每次都賭 1。
  anchor_type: 數學推導
  comparison_target: 每次都賭機率 1 與輸出 0.65 互相比較
  importance: 20
  status: normal
- id: c21
  role: mechanism
  text: 用 squared error 當 loss 訓練，資料量夠大時最優解收斂到條件期望值；結果只有 0/1 時，條件期望值就是條件機率，所以模型學到的是一個函數：輸入一組特徵，輸出歷史上相似案例中異常（例子裡指交易異常）發生的比例，而不是記住某一筆的答案
  source_quotes:
  - 用 squared error 當 loss 訓練模型，在資料量夠大時，模型的最優解會收斂到條件期望值（conditional mean）；對於結果只有 0/1 兩種的情況，條件期望值就是條件機率
  - 所以模型最後學到的，不是「記住某一筆的正確答案」，而是學到一個函數：輸入一組特徵，輸出「歷史上跟這組特徵相似的案例中，異常發生的比例」。
  anchor_type: 背景說明
  numeric_kind: non_comparative
  numeric_reason: 定義
  importance: 21
  status: normal
- id: c22
  role: mechanism
  text: 校準在統計上一定要靠大量資料才能成立，它是群體層次的性質，不是單筆預測能驗證或訓練出來的
  source_quotes:
  - 校準在統計上一定要靠大量資料才能成立——它是一個群體層次的性質，不是單筆預測能驗證或訓練出來的
  anchor_type: 背景說明
  importance: 22
  status: normal
- id: c23
  role: evaluation
  text: 只要設計得當的計分規則，像 Brier score，誠實報告自己真實信心的期望分數必然不會輸給講得比較篤定；這條原理適用於任何需要校準的預測系統，不只機器學習，天氣預報的降雨機率與醫療診斷的信心水準背後都是同一套數學
  source_quotes:
  - 只要設計得當的計分規則，像 Brier score，模型或預測者誠實報告自己的真實信心，期望分數必然不會輸給「講得比較篤定」
  - 這條原理適用於任何需要校準的預測系統，不只機器學習——天氣預報的降雨機率、醫療診斷的信心水準，背後都是同一套數學。
  anchor_type: 部落格判斷
  importance: 23
  status: normal
```
