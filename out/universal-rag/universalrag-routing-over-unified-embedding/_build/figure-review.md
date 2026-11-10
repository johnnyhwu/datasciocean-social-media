# 重製圖審查材料：universalrag-routing-over-unified-embedding

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 6 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/universal-rag/universalrag-routing-over-unified-embedding/ig/06.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 小標籤：舊做法
  - 主標：但資料多半按形式分群，
而不是按意思
  - 補充：論文發現，在這個空間裡，資料多半依形式（模態）而不是意思（語意）聚在一起。明明有張圖片更對題，文字問題卻往往離文字資料比較近。這種偏見叫 Modality Gap。
  - 示意圖（clusters）上的文字與數字：文字問題｜語意更相關的圖片，往往反而比較遠｜圖片｜影片｜文字
  - 圖註：示意圖，改繪自論文的分布圖，點的位置不是實際資料。

### 原圖 universal-rag/figure2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/universal-rag/figure2.png
- blog 圖說原文（不是主張）：統一嵌入空間的 t-SNE 可視化圖。我們可以看到不同模態 (文字、影像、影片) 形成了明顯的分離簇，這就是所謂的 Modality Gap，它會導致檢索時的偏向性。
- 附這張圖的主張：c4

### 這張引用的主張（圖要以它們為準）
- **c4**（原作者解讀）：最直觀的多模態做法，是用 CLIP 這樣的多模態編碼器把文字、圖片和影片全部映射到同一個向量空間（Unified Embedding Space）做相似度檢索，但這會導致嚴重的模態偏見：資料點傾向於根據「模態」而非「語意」聚集，文字查詢與文字資料的距離，往往比它與語意更相關的影像資料還要近；blog 把這種檢索偏見稱為 Modality Gap
