# 重製圖審查材料：sag-latent-hyperedge-one-hop

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 10 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-latent-hyperedge-one-hop/ig/10.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 主標：線下不建圖，查詢那一瞬間才長出圖
  - 補充：線下不算實體之間的全域連線；查詢時才用 SQL JOIN，把共用實體的事件串起來。
  - 示意圖（ingest）上的文字與數字：chunk｜事件：一對一｜實體：多對多｜SQL 資料庫｜使用者發問｜SQL JOIN｜把共用實體的，事件配起來｜局部超圖｜記憶體裡形成，查完就丟｜線下：建索引時｜線上：使用者發問時

### 原圖 sag/figure1.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/figure1.png
- blog 圖說原文（不是主張）：圖一 — 三種 RAG 範式的流程與效能對照。（來源：原始論文）
- 附這張圖的主張：c2

### 原圖 sag/figure2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/figure2.png
- blog 圖說原文（不是主張）：圖二 — SAG 的整體架構。上半部是線下攝取，下半部是線上檢索。（來源：原始論文）
- 附這張圖的主張：c5

### 這張引用的主張（圖要以它們為準）
- **c2**（設計參數）：SAG（SQL-Retrieval Augmented Generation）論文提出的折衷方案：線下不建圖，只把每個 chunk 轉成一個保留完整語意的「事件」加上一組實體標籤，寫進標準 SQL 資料庫；線上查詢時再用 SQL JOIN 把共用實體的事件動態串起來；圖只在查詢的那一瞬間存在，查完就丟
- **c4**（設計參數）：在 SAG 中，一個 chunk 對應一個保留完整語意的事件，以及一組跟它綁定的實體集合；這個「事件 ↔ 實體集合」的綁定關係，本身就定義了一條超邊
- **c5**（設計參數）：「潛在」的意思是：線下建索引時，系統不會去計算實體與實體之間的全域連線，也不會畫出任何顯性圖譜；這些超邊只是以一張「事件-實體」多對多資料表的形式，潛伏在 SQL 裡
- **c6**（設計參數）：只有在使用者發問、系統下 SQL JOIN 的那一瞬間，共用實體的事件才會在記憶體裡被串起來，形成一個局部超圖；查完就釋放

## 第 15 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-latent-hyperedge-one-hop/ig/15.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 主標：加一跳擴展，Recall@5 升到 80.0%
  - 補充：在 MuSiQue 上，跟無擴展的 SAG 比。H=0 不擴展、H=1 擴展一跳。Recall@1（前 1 筆找回多少）等於沒動，Recall@5（前 5 筆）從 69.4% 升到 80.0%。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：Recall@1｜｜無擴展（H=0） 35.7 %｜有擴展（H=1） 36.2 %
  - 圖表項目：Recall@5｜｜無擴展（H=0） 69.4 %｜有擴展（H=1） 80 %
  - 圖註：Recall@K：前 K 筆結果裡，找回多少該找回的內容

### 原圖 sag/table3.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/table3.png
- blog 圖說原文（不是主張）：表三 — 動態超邊建構中擴展跳數的消融實驗（MuSiQue）。（來源：原始論文）
- 附這張圖的主張：c14

### 這張引用的主張（圖要以它們為準）
- **c14**（實驗結果）：擴展（H=1）完全沒有提升 Recall@1（35.7 → 36.2，等於沒動），卻讓 Recall@5 暴增 10.6 個百分點（69.4 → 80.0）
  - 限定條件 c14#1：這個消融（擴展 H=0 對 H=1）是在 MuSiQue 上做的（來源：圖說）
