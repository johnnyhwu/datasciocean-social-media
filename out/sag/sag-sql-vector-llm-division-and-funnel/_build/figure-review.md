# 重製圖審查材料：sag-sql-vector-llm-division-and-funnel

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 6 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-sql-vector-llm-division-and-funnel/ig/06.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 主標：線上三步找出資料，不走預先建好的全域圖譜
  - 補充：線上只跑三個步驟，細節接下來一張一張看。
  - 示意圖（online）上的文字與數字：Step 1・路徑 A｜輕量 LLM 抽實體，SQL 精確撈事件｜Step 1・路徑 B｜整個問題轉向量，撈相似度大於 0.4 的事件｜Step 2：用 SQL 擴展｜沿著共用的實體，撈回新的相關事件｜Step 3・LLM 精選｜先粗篩到 100 個，LLM 挑 5 個｜Step 3・直接檢索｜問題直接去原始 chunk 向量庫，挑 5 個｜使用者發問｜10 個 chunk 交給生成模組

### 原圖 sag/figure2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/figure2.png
- blog 圖說原文（不是主張）：圖二 — SAG 的整體架構。上半部是線下攝取，下半部是線上檢索。（來源：原始論文）
- 附這張圖的主張：c10, c12, c17

### 這張引用的主張（圖要以它們為準）
- **c8**（設計參數）：線上完全不走全域圖譜，三個步驟跑完就出答案
- **c9**（設計參數）：Step 1 路徑 A（實體引導的 SQL 檢索）：先用輕量 LLM 從問題裡抽出實體，拿去實體向量索引做相似度搜尋（門檻 0.9 以上）擴充出別名集合，再用 SQL 的 OR 邏輯，精確撈出關聯到其中任何一個實體的事件
- **c10**（設計參數）：Step 1 路徑 B（純事件向量檢索）：把問題轉成向量，直接在事件向量庫裡撈相似度大於門檻 τ（預設 0.4）的事件；兩條路取聯集去重，B 的存在是為了保底，預防 A 的實體提取漏接
- **c12**（設計參數）：Step 2 是「反向收集實體 → 正向撈回事件」的批次 SQL：把種子事件綁定的實體全部提出來，組成一個實體前線集合，再用批次 JOIN 撈回所有新關聯的事件，跟種子事件合併成候選池，這批事件交織出來的網絡就是那個臨時的局部超圖
- **c14**（設計參數）：Step 3 先做向量粗篩：算所有候選事件跟 query 的相似度，截取 Top 100，這是個工程妥協，用便宜的方式把 LLM 要看的量壓到可負擔範圍
- **c15**（設計參數）：Step 3 路徑 A（LLM 結構化精選）：把這 100 個事件一起送進推理 LLM，做聯合評估（joint assessment），通盤考量哪些事件「組合起來」能構成一條多跳推論鏈，挑出最關鍵的 5 個，還原成對應的原始 chunk
- **c17**（設計參數）：Step 3 路徑 B（直接語意檢索）：拿問題向量直接去原始 chunk 向量庫撈相似度最高的 5 個；兩路聯集去重，輸出 Top 10 給生成模組
- **c18**（部落格判斷）：雙軌決選設計的用意是互補：結構路徑負責召回「需要跨文件拼湊、字面相似度低」的邏輯證據，語意路徑負責召回「跟問題高度相關」的直球證據

## 第 10 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-sql-vector-llm-division-and-funnel/ig/10.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 主標：Step 2：先收集實體，再撈回新事件
  - 補充：先把種子事件（Step 1 撈到的第一批事件）綁定的實體全部提出來，叫實體前線；再用 SQL JOIN 一次撈回跟這些實體有關的新事件，一起放進候選池。
  - 示意圖（links）上的文字與數字：撈回：張忠謀拿到史丹佛博士｜種子事件：張忠謀創立了 TSMC｜撈回：TSMC 推出新製程｜張忠謀｜TSMC｜事件｜實體前線
  - 示意圖的連線（左—右）：撈回：張忠謀拿到史丹佛博士—張忠謀｜種子事件：張忠謀創立了 TSMC—張忠謀（金色）｜種子事件：張忠謀創立了 TSMC—TSMC（金色）｜撈回：TSMC 推出新製程—TSMC
  - 圖註：假設的例子：金線是種子事件提出的實體，其餘是新撈回的事件

### 原圖 sag/figure2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/figure2.png
- blog 圖說原文（不是主張）：圖二 — SAG 的整體架構。上半部是線下攝取，下半部是線上檢索。（來源：原始論文）
- 附這張圖的主張：c12

### 這張引用的主張（圖要以它們為準）
- **c12**（設計參數）：Step 2 是「反向收集實體 → 正向撈回事件」的批次 SQL：把種子事件綁定的實體全部提出來，組成一個實體前線集合，再用批次 JOIN 撈回所有新關聯的事件，跟種子事件合併成候選池，這批事件交織出來的網絡就是那個臨時的局部超圖

## 第 14 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/sag/sag-sql-vector-llm-division-and-funnel/ig/14.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 主標：兩路合成 10 個 chunk，交給生成模組
  - 補充：兩路的設計用意是互補：LLM 精選那一路，撈需要跨文件拼湊、字面相似度低的邏輯證據；直接檢索那一路，拿問題直接去原始 chunk 向量庫，撈跟問題高度相關的直球證據。
  - 示意圖（concat）上的文字與數字：兩路各挑 5 個 chunk｜聯集去重，輸出 10 個 chunk｜交給生成模組｜LLM 精選｜直接檢索

### 原圖 sag/figure2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/sag/figure2.png
- blog 圖說原文（不是主張）：圖二 — SAG 的整體架構。上半部是線下攝取，下半部是線上檢索。（來源：原始論文）
- 附這張圖的主張：c17

### 這張引用的主張（圖要以它們為準）
- **c15**（設計參數）：Step 3 路徑 A（LLM 結構化精選）：把這 100 個事件一起送進推理 LLM，做聯合評估（joint assessment），通盤考量哪些事件「組合起來」能構成一條多跳推論鏈，挑出最關鍵的 5 個，還原成對應的原始 chunk
- **c17**（設計參數）：Step 3 路徑 B（直接語意檢索）：拿問題向量直接去原始 chunk 向量庫撈相似度最高的 5 個；兩路聯集去重，輸出 Top 10 給生成模組
- **c18**（部落格判斷）：雙軌決選設計的用意是互補：結構路徑負責召回「需要跨文件拼湊、字面相似度低」的邏輯證據，語意路徑負責召回「跟問題高度相關」的直球證據
