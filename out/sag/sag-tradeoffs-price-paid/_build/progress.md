# SAG 第 4 則 sag-tradeoffs-price-paid 進度

- 2026-10-27 開始。單卡（E，最後一則）。卡沒有 `figures`，不用重製圖審查者。
- 規劃：15 張（封面、recap、context、receipt、squeeze、chart_bars、compare、alias、handoff、mismatch、ledger、hidden、pairs、takeaway、series_map）。
- 新圖型（規則 12）：receipt、squeeze、alias、handoff、mismatch、ledger（要補 tests/test_diagrams.py）。
- hook：候選存 hook-candidates.md，暫用 A，待人挑（相鄰第 3 則是「讀者疑問」，要換樣態時選 B～E）。
- 2026-10-27：spec 15 張完成；程式 A 通過、程式 B 15/15；contact_sheet、build_package 已跑；tests/test_diagrams.py 補 6 個新圖型（全過）。
- 模板：series/sag/templates/style.css 的 `.chip` padding 8→4（標題右緣超過小標籤左緣時，程式 B 對比度會量到小標籤的金色底線；已發布的貼文不重渲）。小標籤用 3 字（第一筆／第二筆／第三筆）。
- 第 1 輪審查已派（faithful／reader／editor，輸出 _build/reviews/*-r1.json）；審查期間不改 spec。
- 待人：hook（hook-candidates.md，暫用 A 代價與取捨）；放行項（論文網址、名詞補充、第 11／12 張假設例子、示意圖）；是否標 ready。
- 2026-10-27（後段）：審查 r1（15 張版）→ 依編輯與忠實者建議重做成 13 張（刪 receipt 總結張、併 ledger＋hidden）；r2、r3 審查檔在 reviews/（r1 的在 reviews/r1/）；r3 退回項（Threads「論文列出」、第 8 張「所以」、第 10 張主標、第 3／4 張主詞、第 6 張阻尼條件）已改；第 4 輪只重審改過的區塊（faithful-r4.json）。回歸測試 12/12、batch_check PASS。
- 編輯 r2 的 AI 腔／標題句型／caption 摘要冗長等建議只採用一部分（標籤統一、術語白話、第 10 張圖例）；沒採用的：第 2／13 張重複（系列地圖設計如此）、caption 逐張摘要（build_package 自動產生）。
- 等人：hook、放行項（論文網址、RAG／知識圖譜／線下線上白話、第 10 張假設例子、示意圖）、是否標 ready；未解 gap：第 10 張沒寫「SAG 設計對象是唯讀文件庫」。
- 2026-10-28：人指出「目前不能更新」會誤解（資料仍可一直新增，問題是新舊資料衝突時沒有機制判斷哪個有效）。全篇改為「新舊衝突沒有內建／原生判斷」（封面因字數用「新舊衝突難判斷」），第 10 張主標改「新增沒問題，新舊衝突，卻沒有原生機制判斷」；忠實者 r5（改過區塊）全過、讀者 r5 誤讀風險輕微（已補第 10 張圖例）。series.md 第 4 則 summary 同步改；已發布的第 2、3 則系列地圖／回顧若寫「目前不能更新資料」不重渲。
- 2026-10-28：人提出新 hook「SAG 相較 GraphRAG 不先建圖，很省事沒錯，但要付三筆帳」（採「不先建圖」）；人決定封面主標可放寬成 3 行、並要「省事」放第二行，最後排成 2 行（探照燈封面主標超過 2.5 行時自動縮成 56px）。第 3 張補 GraphRAG 白話（內文與各列同步縮短）。忠實者 r6 審封面／第 3 張／Threads 正文／caption，結果待回。hook 待人看過封面後明講接受。
- 2026-10-28：忠實者 r6（reviews/faithful-r6.json）：第 3 張、Threads 正文通過；封面與 caption 第一行各 1 個 blocker「範圍被放大」——「相較 GraphRAG」+「三筆帳」讀起來像三個代價是相對 GraphRAG 才多付的，卡上只有第一筆有 HippoRAG 對照（c7，帶阻尼限定）、第二筆只有傳統知識圖譜要對齊（c9）、第三筆沒有任何 GraphRAG 對照。標「爭議」交給人（hook 是人提的），等人決定：維持／改寫。尚未改任何字。
