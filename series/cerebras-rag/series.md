---
id: cerebras-rag
name: "拆解 Cerebras 知識庫：資料怎麼進來，答案怎麼出去"   # 人挑定（2026-10-31，候選 B）；會印在每張圖上，發布後不能改
philosophy: series/cerebras-rag/philosophy.md   # 沙漏；人 2026-10-31 審過樣張
color: hourglass   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window）
style: hourglass   # 2026-10-31 人從三個草圖選 C1「沙漏」
members:   # 人 2026-10-31 決定方案 B：3 則、每則雙卡。planned_title 是人挑定的 hook，summary 已經忠實者與讀者審過
  - concept: rag-narrow-waist
    also: [slack-distillation-and-bursting]
    planned_title: Slack、Wiki、程式碼、Jira，怎麼塞進同一張表？   # 人 2026-10-31 從 hook 候選挑定 A
    summary: 異質來源收斂成只有五個欄位的一張表；寫入前先把討論串正規化成固定四樣再做 embedding。
  - concept: slack-vector-failure-orthogonal-signals
    also: [rrf-rank-fusion]
    planned_title: 搜尋出三種毛病，Cerebras 不是多加幾招，是一種毛病配一帖藥   # 人 2026-11-01 從 hook 候選挑定 A
    summary: 用向量搜尋找對話紀錄有三種毛病，每種配一個不會跟著犯錯的做法；好幾種搜法的結果，改用名次合成一份。
  - concept: rag-planner-single-round-vs-agentic
    also: [retrieval-reasoning-decoupling]
    planned_title: 搜尋每次都把所有工具叫一遍？又慢又貴   # 人 2026-11-01 從 hook 候選挑定 B（第 1 輪）
    summary: LLM 先挑這次用哪些工具、平行查一輪，推理留到最後才做；整條流程只走一輪，不會回頭再查。   # 2026-11-01 人的回饋：不寫「作者判斷」
members_locked: true   # 2026-11-01 鎖定：三則 spec 都做完、張數定案（18／18／19 張）、人同意 ready；第 1 則發布後，成員與 planned_title 都不能再動
hashtag: CerebrasRAG   # 人 2026-10-31 同意（不加 DSO_ 前綴，照 #ClaudeCode 那次）
status: planning
---

# 拆解 Cerebras 企業知識庫 RAG

來源文章：`cerebras-rag`（6 張卡，同一篇文章，預設組成系列）。
文章標題：拆解 Cerebras 企業知識庫 RAG：窄腰設計、檢索推理解耦與 Pipeline 的邊界
網址：https://datasciocean.com/paper-intro/cerebras-rag/

## 規劃備忘（2026-10-31）

- 人的要求：**2 則最好，最多 3 則**。6 張卡 → 要大幅合併。
- 六張卡共用的背景主張（每張卡的 c2／c3：Cerebras Knowledge 每天 15,000 次查詢、資料橫跨 Slack／Wiki／程式碼／Jira）每則都重複，只在第 1 則完整講。
- 沒有任何主張附 `figures`（這篇文章的卡都沒有參考圖）。
- `pending_author_confirmation`：無（六張卡全部主張都是 `normal`，都可用）。
- `series_deps.py` 一如預期沒有鑑別力（六張卡兩兩都「有 1 條幾乎相同的主張」，就是那條 15,000 次查詢的背景）。有意義的訊號只有兩個：
  planner 有 4 條主張用了 decoupling 的主題術語；vector-failure 用了 rrf 定義的 BM25／IDF／cosine，distillation 也用了 IDF。
- 六張卡的讀者面主題（文章的四層結構）：
  1. `rag-narrow-waist`（19 條）心智模型：沙漏、embeddings table 五欄位、connector 只回答三個問題、Projects／scoping、「形式統一但語意分裂」陷阱
  2. `slack-vector-failure-orthogonal-signals`（13 條）診斷：純向量在對話資料上的三種失效、失效根因 → 不受該根因影響的訊號、訊號失效模式要正交、IDF vs BM25
  3. `slack-distillation-and-bursting`（14 條）寫入端：distillation 正規化成四樣結構化資料、bursting 撈回旁枝＋三道品質門檻、寫入時過濾比 rerank 便宜
  4. `rrf-rank-fusion`（17 條）讀取端：只看名次不看分數、k=60 偏好共識、單路缺席時共識變懲罰、reranker 補救、去重與補回上下文、漸進昂貴
  5. `rag-planner-single-round-vs-agentic`（17 條）編排層：planner 只路由、故意比工具便宜、executor 平行＋evidence schema、單輪 pipeline vs agentic loop、兩個結構限制
  6. `retrieval-reasoning-decoupling`（17 條）編排層：檢索與推理解耦、lookup vs compute 判準、MCP 不藏 planner vs Web UI 全包

## 合併方案（2026-10-31 提給人決定）

**方案 A（2 則，每則 3 卡）**：寫入端／讀取端對切
- 第 1 則：`rag-narrow-waist` ＋ `slack-vector-failure-orthogonal-signals` ＋ `slack-distillation-and-bursting`
- 第 2 則：`rrf-rank-fusion` ＋ `rag-planner-single-round-vs-agentic` ＋ `retrieval-reasoning-decoupling`
- 代價：3 卡貼文是新做法（目前最多雙卡）；每則要砍掉約三分之一主張，第 2 則特別擠，預期要整塊捨棄（MCP vs Web UI、lookup vs compute、RRF 收尾動作）。

**方案 B（3 則，每則雙卡）**：Claude 的建議
- 第 1 則：`rag-narrow-waist` ＋ `slack-distillation-and-bursting`（四種完全不同的資料怎麼塞進同一張表還搜得到：schema 收窄 ＋ 寫入前先正規化）
- 第 2 則：`slack-vector-failure-orthogonal-signals` ＋ `rrf-rank-fusion`（為什麼一路檢索不夠 → 多路的排名怎麼合成一份；RRF 的弱點正好回到「訊號要正交」）
- 第 3 則：`rag-planner-single-round-vs-agentic` ＋ `retrieval-reasoning-decoupling`（誰決定這次查哪些工具、推理該放在哪裡、這到底算不算 agentic）
- 代價：3 則，發文週期長一點；第 1 則要自己用白話定義「詞彙稀有度（IDF）」，不能等第 2 則。

**人 2026-10-31 決定：方案 B。** 成員已寫進 `members`（主卡 ＋ `also`），發文順序照 `members` 的順序。

## 待人決定（照順序）

1. ~~系列名~~ 已定（2026-10-31，候選 B「拆解 Cerebras 知識庫：資料怎麼進來，答案怎麼出去」）。
   **hashtag 還沒定**：Claude 建議 `#CerebrasRAG`（照 Claude Code 那次，不加 `DSO_` 前綴），人尚未明確回答。
2. **視覺風格與色**：新系列要先用 `design-series-visuals` 做視覺哲學與版型樣張，人審過才量產。
   已用過的色／風格：`teal-mid`、`paper-cards`、`spotlight`、`abyss-contour`、`window`（相鄰系列不能同色）。
   2026-10-31：三個方向的草圖已做好，在 `series/cerebras-rag/sketches/`（`總覽-三個方向.png` 與各方向的
   `-封面1/2/3.png`、`-內頁.png`、`-IG首頁3x3.png`）。**待人選方向**：
   - **C1 沙漏**：上面四種來源收斂 → 中間一條只有五格的窄帶 → 下面重新展開；米色底，標題在下段。
   - **C2 腰線**：滿版橫切，上半米色（寫入端）、下半深海漸層（讀取端），腰帶貫穿全幅，標題壓在深色上。
   - **C3 五個格子**：標題在上，下半是五根等寬直欄（五個欄位），異質紙片正要落進去。
   草圖上的標題是暫用佔位，不是已挑定的 hook。
   **人 2026-10-31 選 C1「沙漏」**。已做好：`philosophy.md`（沙漏）、`templates/`（複製自 window 再改封面）、
   `render.py` 的 `hourglass` 風格（`hg_shape`／`hg_waist`／`hg_cover`／`hg_deco`／`hg_corner`／`hg_takeaway`，
   `SERIES_COLORS["hourglass"]`）、九種版型的樣張 `sketches/sample/`（程式 B 9/9 通過，縮圖
   `sketches/sample/_build/contact-sheet.png`）。樣張的內容取自第 2 則的卡，只為了看版型，不會發布。
   **待人審樣張**；通過後才寫 `tests/test_hourglass_style.py`（風格定案才寫測試，避免外觀再改就要重寫）。
   草圖腳本（暫存，未進 repo）：`/private/tmp/claude-501/-Users-johnnyhwu-Desktop-datasciocean-social-media/6deeac8a-f716-4098-8cf4-25602f3a3de6/scratchpad/sketch_cerebras.py`
3. **各則 hook**：一則一則出 5～6 個候選（存 `out/cerebras-rag/<觀念>/_build/hook-candidates.md`），人挑定後才寫進 `planned_title`。
4. 三則 spec 全部做完、張數與標題定案 → 加 `members_locked: true` → 發第 1 則。

## 寫 spec 時要記得

- 三則都會用到的背景（每天 15,000 次查詢、資料橫跨 Slack／Wiki／程式碼／Jira）只在第 1 則完整講，第 2、3 則一句帶過。
- 第 2、3 則的第 2 頁要是 `recap`（前情回顧），所以每個成員要寫 `summary`（≤58 字、白話、不放沒定義的術語）；新系列的模板要加 `recap.html` 與 `.isum`／`.ilab` 樣式。
- 第 1 則要自己用白話定義「詞彙稀有度（IDF）」（bursting 的品質門檻 IDF ≥ 4.0 會用到），不能等第 2 則。
- 第 3 則的兩張卡，核心主張都帶同一個限定條件：「單輪 pipeline 不是 agentic loop」與「檢索與推理必須解耦」是**作者自己推導的判斷，Cerebras 文章沒有直接講**。用了就必須一起出現。

