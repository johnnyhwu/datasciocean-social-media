# 行動清單

來源：`reports/2026-11-21-baseline.md`。狀態：`todo`（還沒試）／`trying`（有貼文套用中）／`kept`（有效，變成固定做法，寫進對應的 reference）／`dropped`（無效或做不到，寫原因）／`decide`（要人決定）。

**主要指標**：每次快照的追蹤數變化（IG、Threads）。**次要**：Threads views／shares、IG reach／saved／shares／follows／profile_visits（對齊貼文年齡比）。

**基準**（2026-11-21，發布 2 天以上的貼文）：IG views 中位數約 190、reach 約 70、follows 0；Threads views 中位數約 250、shares 中位數 2。

## 每則挑 1～2 個 action

挑的原則：先試**證據最強、成本最低**的；同一則不要同時改太多，否則分不出是哪個有效；一個 action 至少連續套用 3 則才判讀。

| ID | 假設（為什麼可能有效） | 證據 | 怎麼做 | 怎麼判斷 | 狀態 |
|---|---|---|---|---|---|
| A1 | **主題選「真實系統怎麼分工、怎麼搭」**的卡，Threads 會被工程師轉分享 | 爆紅 5 則都是這類（報告觀察 2、3） | 規劃系列與選卡時優先；系列內先發這類的那則 | 這類貼文 Threads views／shares 中位數 ≥ 基準 2 倍 | trying（RAGU） |
| A2 | **Threads 首句用「X 不靠 A，靠 B」或「怎麼把 A、B、C 塞進同一個 D」這種系統取捨句**，讓工程師一眼看出是架構題 | SAG 7,791（不靠更強的模型，靠分工）、Cerebras 2,571 | Threads 正文第一句改寫（仍在卡的範圍內、要過忠實者） | 同上，連續 3 則 | todo |
| A3 | **IG 最後一張（帶走張）加一行追蹤邀請**（例：「每天拆一篇 AI 論文，追蹤 @datasciocean」），把看完的人變成追蹤者 | IG follows 29 則全 0、profile_visits 0～5（觀察 1） | 模板在帶走張底部加固定一行（結構文字，不涉及卡） | IG follows／profile_visits 連續 3 則 > 0，且追蹤數變化比前 3 則多 | trying（RAGU） |
| A4 | **IG 縮短到 7～9 張**，讓更多人看完、願意收藏 | 系列讀者測試三次都說 11～15 張太長；IG 看不到完讀率，只能看 saved | 規劃時以 8 張為目標，多的移到 Threads 或砍掉 | IG saved／shares 中位數高於基準 | trying（RAGU） |
| A5 | **IG 第 2 張（第二封面）放一個讓人想收藏的「可以帶走的做法」**，而不是論文數字 | 收藏多半 0；收藏是 IG 推給非追蹤者的訊號（推論） | 第 2 張改成具體招式或檢查清單 | IG saved、reach | todo |
| A6 | **Threads 結尾問一個工程師會想回答的問題**（例：你們的 RAG 也遇過嗎？），多一些回覆 | 回覆多半 1～3 | Threads 正文最後一句 | replies 中位數 > 基準 | todo |
| A7 | **讀者審查的讀者設定改成「懂一點技術的工程師」**（至少 Threads），不再把架構細節砍掉 | 觀察 6 | 改 reader 提示詞或分平台 | 間接：A1、A2 的貼文表現 | decide（人 2026-11-22 照 Claude 建議：先不改；同時改讀者標準會和 A1 混在一起分不出效果。RAGU 前 3 則（A1）判讀完再提一次） |
| A8 | 發文時段 | 無資料 | — | — | dropped（人 2026-11-22 照 Claude 建議：維持 `CLAUDE.md` 範圍外，不試） |
