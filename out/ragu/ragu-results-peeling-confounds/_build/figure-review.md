# 重製圖審查材料：ragu-results-peeling-confounds

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 9 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/ragu/ragu-results-peeling-confounds/ig/09.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 小標籤：難度分級
  - 主標：論文說越難越強？
主要是對手往下掉
  - 補充：拆開看：RAGU 沒有一路掉分，HippoRAG 2 從 72.4% 掉到 56.9%；最難那級只差 2.1%，在 AI 裁判的雜訊範圍內。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：第 1 級｜Fact Retrieval｜HippoRAG 2 72.4 %｜RAGU 54.2 %
  - 圖表項目：第 2 級｜Complex Reasoning｜HippoRAG 2 68.4 %｜RAGU 53.7 %
  - 圖表項目：第 3 級｜Contextual Summarize｜HippoRAG 2 65 %｜RAGU 64.1 %
  - 圖表項目：第 4 級（最難）｜Creative Generation｜HippoRAG 2 56.9 %｜RAGU 59 %
  - 圖註：答對率（AC）；都用 RAGU 附帶的抽取模型建圖

### 原圖 ragu/figure3.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/ragu/figure3.png
- blog 圖說原文（不是主張）：圖四 — 依任務複雜度呈現的 cross-over。(a) 是 Answer Correctness，(b) 是 Evidence Recall。（來源：原始論文 Figure 3）
- 附這張圖的主張：c13, c14

### 這張引用的主張（圖要以它們為準）
- **c1**（部落格判斷）：把 RAGU 的實驗混淆變因一層層剝掉之後，扣掉答案格式，RAGU 對 HippoRAG 2 是追平或落後、沒有任何一項贏；整套 GraphRAG 相對於純向量檢索（NaiveRAG）的淨貢獻只有 1.2 到 4.3 pp；最漂亮的 cross-over 敘事拆開來看，主要是對手掉下去，不是它爬上來
  - 限定條件 c1#1：「沒有任何一項贏」指的是扣掉格式之後 terse 設定下的 AC 對照（BioASQ、2Wiki、MuSiQue）
  - 限定條件 c1#2：在 GraphRAG-Bench Medical 最難的 Creative Generation 層級，RAGU 以 59.0 對 56.9 贏 HippoRAG 2，blog 說這 2.1 pp 落在 LLM-judge 的雜訊範圍內
  - 限定條件 c1#3：AC 是單一 judge 模型的單次評分，論文沒有 error bar、也沒有人工驗證 judge 準確度，blog 提醒個位數 pp 的差距不宜當結論
  - 限定條件 c1#4：淨貢獻是用 RAGU 自己的程式、自己的 prompt 做的對照
  - 限定條件 c1#5：cross-over 是在 GraphRAG-Bench Medical 的四個難度層級上比的 AC，都用 Meno-Lite-0.1（RAGU 附帶的抽取模型）建圖
- **c13**（原作者解讀）：論文的 cross-over 敘事：在 GraphRAG-Bench Medical 的四個難度層級（Fact Retrieval、Complex Reasoning、Contextual Summarize、Creative Generation），RAGU 對 HippoRAG 2 的 AC 差距從 −18.2 單調收斂到 +2.1，論文說這是「越難越強」的證據
  - 限定條件 c13#1：這四個難度層級的 AC 都用 Meno-Lite-0.1（RAGU 附帶的 7B 抽取模型）建圖
- **c14**（部落格考證）：blog 拆解這個 cross-over：RAGU 自己那一欄是 54.2 → 53.7 → 64.1 → 59.0，HippoRAG 2 則從 72.4 掉到 56.9、跌了 15.5 pp；所謂 cross-over 主要不是 RAGU 變強，而是 HippoRAG 2 往下掉，blog 認為準確的描述是 RAGU 的表現對任務難度不敏感、HippoRAG 2 敏感，所以在最難的一格被追過
  - 限定條件 c14#1：這四個難度層級的 AC 都用 Meno-Lite-0.1 建圖
- **c15**（部落格判斷）：blog 認為「在難任務上更強」跟「在難任務上比較不會退步」是兩件事，論文的敘事把後者說成了前者；而且最難那格贏的是 59.0 對 56.9，2.1 pp，落在 LLM-judge 的雜訊範圍內
- **c9**（部落格判斷）：論文說這是「互補的強項而非全面壓制」，blog 認為這個說法站得住，但要注意扣掉格式後 RAGU 是追平或落後，沒有任何一項贏
  - 限定條件 c9#1：「沒有任何一項贏」指的是扣掉格式之後 terse 設定下的 AC 對照（BioASQ、2Wiki、MuSiQue）
  - 限定條件 c9#2：在 GraphRAG-Bench Medical 最難的 Creative Generation 層級，RAGU 以 59.0 對 56.9 贏 HippoRAG 2，blog 說這 2.1 pp 落在 LLM-judge 的雜訊範圍內
