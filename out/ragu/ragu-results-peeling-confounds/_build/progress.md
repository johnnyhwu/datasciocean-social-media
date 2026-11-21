# 進度：ragu-results-peeling-confounds（RAGU 第 1 則）

## 現況（2026-11-19）
- 審查全過：忠實者 r2、讀者 r2、重製圖 r2 通過（r1 編輯建議已處理）；spec_diff --mark 已記。
- 下一步：等系列其他則做完 → series 層審查（summary）→ batch_check → 交人。
- 不擋、未處理的讀者建議（交付時說明）：lift 圖例「重點那一列」語意稍弱；「整併」第 3 張出現、第 10 張才補「去重與摘要」；MuSiQue −3.4% 卡上沒有原因可寫。
- 等人決定的事：無。

## 投影片規劃（12 張）
1 封面 hook A：「AI 先畫知識圖再回答，\n[[真的比較準嗎？]]」；副標：RAGU 論文、和同一套程式只差不用圖的版本比，只多答對 1.2 到 4.3%（c1,c11）
2 lift 兩列（BioASQ）：只把答案改短 56.0→72.9；從不用圖改用圖 71.7→72.9；補充帶建圖成本 c12；圖註 c5（單一裁判、無誤差範圍）
3 context 名詞表：GraphRAG（c3）、RAGU（c2）、HippoRAG 2
4 route：答案格式／用圖 vs 不用圖／越難越強是誰在動；補充放 c4（同一個 gpt-4o-mini、gemini 裁判、AC 定義）
5 lift 三題庫 長→短答案（c6），emph BioASQ；說明標準答案很短（Bell Laboratories）
6 table 格式拉平後 RAGU vs HippoRAG 2（c8，c7，c9 圖註，c1#1）
7 lift 三題庫 NaiveRAG→RAGU（c10,c11,c1#4）
8 chart_bars 成對 四難度 HippoRAG 2 vs RAGU（c13,c14,c1#5，fig_refs ragu/figure3.png，圖註 Meno-Lite-0.1）
9 table 更強≠比較不會退步；59.0 對 56.9 在雜訊內（c14,c15,c1#2）
10 stops 讀論文三個檢查（c16,c17）
11 takeaway 回扣封面（c18,c11,c17）
12 series_map；nav「完整文章在 datasciocean.com，搜「RAGU」」；hashtags RAGU、GraphRAG、RAG、LLM
其他 hook 候選：B 數字落差「換句提示詞多答對 16.9%，整張知識圖只多 1.2%」（同為 BioASQ）、C「論文說越難越強，其實是對手掉下去」、D 代價「建一張知識圖多跑好幾道工，只多答對 1 到 4%」、E 情境痛點「想導入 GraphRAG？先看這組數字」、F 正面對決「知識圖 vs. 不用圖」。

## 2026-11-19 第 1 輪審查後的修改
- 忠實者：第 8 張補「主要」；第 4 張改「只換建圖用的 LLM」；Threads 補「沒有人工檢查裁判準不準」。
- 重製圖：第 8 張圖註補「答對率（AC）」。
- 讀者／編輯：lift 圖例加金色「重點那一列」；第 2 張每列自己的改前改後名字（lift 新增 pair）；第 4 張補四組題庫；刪掉建圖成本句（c12）；標題句型錯開；「更無聊」→「更平凡」；「格式拉平」→「都用短答案比」；Threads 第 3 段改講天花板（c18），不再重述圖。
- 不採用：答對率差距改「百分點」（人定的用語規則寫 %）；刪第 9 張（保留，改成講「不會退步被說成比較強」）。
