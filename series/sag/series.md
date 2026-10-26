---
id: sag
name: "SAG：不先建圖，查詢時才連"
philosophy: series/sag/philosophy.md
color: spotlight
style: spotlight
members:
  - concept: sag-latent-hyperedge-one-hop
    also: [multihop-vector-vs-graphrag-pain-points]   # 2026-10-24 人決定（方案 1）：兩張卡合成一則（問題：向量與 GraphRAG 各卡在哪；做法：潛在超邊、一跳）
    planned_title: Multi-Hop 推理，一定要先建知識圖譜嗎？
    summary: 線下不建圖，只存事件和實體標籤；查詢時才用 SQL 連事件，實務上從命中的事件出發，只多撈一次共用實體的事件。   # 系列地圖與第 2 頁回顧顯示的細節；依該則的卡寫，發布前由忠實者審過一次
  - concept: sag-sql-vector-llm-division-and-funnel
    planned_title: SQL、向量、LLM 怎麼分工？
    summary: SQL 串事件、向量補語意，候選縮到 100 個以內後，才由 LLM 決選。   # 系列地圖與第 2 頁回顧顯示的細節；依該則的卡寫，發布前由忠實者審過一次
  - concept: sag-results-and-gain-source
    planned_title: SAG 的成績從哪來？
    summary: 績效大頭來自 SQL 檢索管線，不是超邊本身（MuSiQue 上的實驗）；最難的 MuSiQue 上，同樣的 embedding 下領先 HippoRAG 2 近 15 個百分點。   # 系列地圖與第 2 頁回顧顯示的細節；依該則的卡寫，發布前由忠實者審過一次
  - concept: sag-tradeoffs-price-paid
    planned_title: SAG 付出了什麼代價？
    summary: 固定剪枝預算會漏掉罕見實體、不做別名合併會稀釋連結、目前不支援更新。   # 系列地圖與第 2 頁回顧顯示的細節；依該則的卡寫，發布前由忠實者審過一次
hashtag: DSO_SAG
members_locked: true   # 2026-10-25 鎖定：人要求先發第 1 則（第 2～4 則 spec 尚未做）；成員與 planned_title 之後不能再動
status: planning
---

# SAG：不先建圖，查詢時才連

來源文章：`sag`（5 張卡），人決定（2026-10-24，方案 1）合併成 4 則 post：A＋B → C → D → E。

**`planned_title` 與系列名都是草案**，待人確認；系列名會印在每一張圖上，發布後不能改。

**鎖定前的待辦**：四則的 spec 都做完、張數與 `planned_title` 定案、人同意發第 1 則，才加 `members_locked: true`（`CLAUDE.md` 工作方式）。
