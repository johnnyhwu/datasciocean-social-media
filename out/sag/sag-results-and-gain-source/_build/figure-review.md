# 重製圖審查材料：sag-results-and-gain-source

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 5 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-results-and-gain-source/ig/05.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 主標：最難的 MuSiQue，SAG 領先近 15 個百分點
  - 補充：三個 Multi-Hop 資料集各比 Recall@2 和 Recall@5，都用同一個 BGE-Large embedding。最難的 MuSiQue 領先最多；六組比較只輸 2WikiMultiHopQA 的 Recall@5。
  - 示意圖（scoreboard）上的文字與數字：MuSiQue｜最難的一組｜HotpotQA｜只要連 2 跳｜2WikiMultiHopQA｜實體鏈很長｜SAG｜HippoRAG 2｜64.1｜49.5｜80.0｜65.1｜91.6｜78.4｜96.5｜94.4｜82.3｜76.6｜88.0｜90.4｜Recall@2｜Recall@5
  - 圖註：虛線框＝SAG 唯一輸的一格。MuSiQue：80.0 − 65.1 ≈ 15 個百分點

### 原圖 sag/table1.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/table1.png
- blog 圖說原文（不是主張）：表一 — 統一底層設定（BGE-Large-EN-v1.5 + Qwen3.6-Flash）下，SAG 與各 baseline 的 Recall@2/5 對照。（來源：原始論文）
- 附這張圖的主張：c5, c8, c11

### 這張引用的主張（圖要以它們為準）
- **c4**（背景說明）：主結果比較三個多跳資料集：MuSiQue 最難（4 跳且經反事實過濾）、HotpotQA 是 2 跳（橋樑與比較型問題）、2WikiMultiHopQA 是長實體鏈（含罕見橋樑）；主要對照是 HippoRAG 2，兩者用同一個 BGE-Large embedding
  - 限定條件 c4#1：blog 另一處說的是 MuSiQue 裡「有些」問題在二元圖譜上要跳 4 次，不是每一題都是 4 跳
- **c5**（實驗結果）：MuSiQue 上 SAG 的 Recall@2 / Recall@5 是 64.1 / 80.0，HippoRAG 2 是 49.5 / 65.1，領先近 15 個百分點
- **c8**（實驗結果）：HotpotQA 上 SAG 的 Recall@2 / Recall@5 是 91.6 / 96.5，HippoRAG 2 是 78.4 / 94.4：Recall@5 的差距縮到 2.1 個百分點，Recall@2 上 SAG 還是領先 13.2 個百分點
- **c11**（實驗結果）：2WikiMultiHopQA 是 SAG 唯一輸的一格：SAG 的 Recall@2 領先（82.3 對 76.6），Recall@5 卻落後（88.0 對 90.4）

## 第 8 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-results-and-gain-source/ig/08.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 主標：拆掉超邊，SAG 還是大幅贏過 HippoRAG 2
  - 補充：MuSiQue 的 Recall@5：拆成三元組的 SAG 有 77.1%，比 HippoRAG 2 的 65.1% 高 12 個百分點。拿掉超邊還贏這麼多，可見大頭不是靠超邊，而是靠 SQL JOIN 連事件的管線。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：HippoRAG 2｜｜65.1 %
  - 圖表項目：SAG 拆成三元組｜｜77.1 %｜強調
  - 圖表項目：SAG 完整事件｜｜80 %
  - 圖註：Recall@5：前 5 筆結果裡，抓到幾成答案需要的資料

### 原圖 sag/table2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/table2.png
- blog 圖說原文（不是主張）：表二 — 事件層級索引 vs. 三元組拆解索引的消融比較（MuSiQue）。（來源：原始論文）
- 附這張圖的主張：c1, c12, c13

### 這張引用的主張（圖要以它們為準）
- **c1**（部落格判斷）：論文的招牌是超邊，但績效的大頭其實來自管線設計；SAG 的結構收益主要來自字串精確匹配的 SQL JOIN，跟 embedding 品質基本無關
  - 限定條件 c1#1：別名對齊的壓力被推遲到線上，交給向量的模糊匹配去處理
  - 限定條件 c1#2：線上的種子預算（超過 50 就依向量相似度排序，只留 Top 50）與實體剪枝（前線實體超過 50 個時計算它們跟 query 的向量相似度，只留 Top 50）也都靠向量相似度排序
  - 限定條件 c1#3：實體剪枝也靠向量相似度：前線實體超過 50 個時，計算它們跟 query 的向量相似度，只留 Top 50
  - 限定條件 c1#4：支持這個論點的三元組消融是在 MuSiQue 上做的（來源：圖說）
  - 限定條件 c1#5：支持這個論點的換 embedding 實驗是在 MuSiQue 上做的（來源：圖說）
- **c12**（實驗結果）：把 SAG 強行拆成三元組來跑，Recall@5 從 80.0% 掉到 77.1%；就算拆成三元組，77.1% 依然大幅贏過 HippoRAG 2 的 65.1%
  - 限定條件 c12#1：這個消融（完整事件對三元組）是在 MuSiQue 上做的（來源：圖說）
- **c13**（部落格判斷）：SAG 這套 SQL 檢索管線本身就有系統性優勢，跟用不用超邊無關
  - 限定條件 c13#1：這個判斷依據的三元組消融是在 MuSiQue 上做的（來源：圖說）

## 第 10 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-results-and-gain-source/ig/10.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 主標：換更強的 embedding，SAG 只進步 1.7 個百分點
  - 補充：MuSiQue 上換成更強的 NV-Embed-v2，HippoRAG 2 進步 9.5 個百分點，SAG 只進步 1.7，但仍然領先。SAG 的成績比較不被 embedding 左右。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：HippoRAG 2｜進步 9.5 個百分點｜原本：BGE-Large 65.1 %｜換成：NV-Embed-v2 74.6 %
  - 圖表項目：SAG｜進步 1.7 個百分點｜原本：BGE-Large 80 %｜換成：NV-Embed-v2 81.7 %
  - 圖註：Recall@5：前 5 筆結果裡，抓到幾成答案需要的資料

### 原圖 sag/table4.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/table4.png
- blog 圖說原文（不是主張）：表四 — 換上 NV-Embed-v2 之後，SAG 與 HippoRAG 2 在 MuSiQue 上的表現。（來源：原始論文）
- 附這張圖的主張：c1, c15

### 這張引用的主張（圖要以它們為準）
- **c1**（部落格判斷）：論文的招牌是超邊，但績效的大頭其實來自管線設計；SAG 的結構收益主要來自字串精確匹配的 SQL JOIN，跟 embedding 品質基本無關
  - 限定條件 c1#1：別名對齊的壓力被推遲到線上，交給向量的模糊匹配去處理
  - 限定條件 c1#2：線上的種子預算（超過 50 就依向量相似度排序，只留 Top 50）與實體剪枝（前線實體超過 50 個時計算它們跟 query 的向量相似度，只留 Top 50）也都靠向量相似度排序
  - 限定條件 c1#3：實體剪枝也靠向量相似度：前線實體超過 50 個時，計算它們跟 query 的向量相似度，只留 Top 50
  - 限定條件 c1#4：支持這個論點的三元組消融是在 MuSiQue 上做的（來源：圖說）
  - 限定條件 c1#5：支持這個論點的換 embedding 實驗是在 MuSiQue 上做的（來源：圖說）
- **c15**（實驗結果）：把 embedding 從 BGE-Large 換成更強的 NV-Embed-v2，HippoRAG 2 的 Recall@5 從 65.1 升到 74.6（+9.5），SAG 從 80.0 升到 81.7（+1.7）
  - 限定條件 c15#1：這個換 embedding 的實驗是在 MuSiQue 上做的（來源：圖說）
