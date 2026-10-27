# SAG 第 3 則 sag-results-and-gain-source 進度

- 2026-10-26 開始。單卡（D）。規劃：13 張（封面、recap、context、scoreboard、hops(fade)、bubble、chart、leak、chart paired、amplify、pairs、takeaway、series_map）。
- 新圖型（規則 12）：scoreboard、leak、amplify；hops 加 fade 與 shortcut（要補 tests/test_diagrams.py）。
- hook：候選存 hook-candidates.md，暫用 A，待人挑。
- 2026-10-26：spec 13 張完成；程式 A 通過、程式 B 13/13；contact_sheet、build_package 已跑；tests/test_diagrams.py 補 scoreboard／leak／amplify／hops(fade, shortcut) 正反案例通過；render.py 的成對橫條圖在 1～2 組時條放粗（只影響新渲染）。
- 第 1 輪審查已派（faithful／reader／editor／figure，輸出 _build/reviews/*-r1.json）；審查期間不改 spec 文字。
- 待人：hook 挑選（hook-candidates.md，暫用 A 讀者疑問）；放行項：論文網址、第 3 張名詞補充、第 6 張 TSMC 假設例子、示意圖 5／8／10。
- 發布前：series_links.py 已補第 1、2 則網址；第 4 則仍「尚未發布」。

## 審查結果（2026-10-26）
- 審查通過版本已記錄（`reviewed-spec.json`）。批次檢查 PASS（存量 WARN 是預期）。
- 忠實者：第 1 輪抓到 caption 範圍放大、第 3 張把 HippoRAG 的描述套到 HippoRAG 2、第 11 張「起點事件」、第 8 張「每跳必剪枝」；全部改完。第 2～5 輪只審改動區塊，最後一輪 blocker 0。
- 重製圖審查者：第 4、7、9 張通過（第 7 張第一輪因補充寫「同用 BGE-Large」被擋，已刪；`figure-final.json` 是第 2 輪第 4、9 張加第 3 輪第 7 張合併而成）。
- 讀者（一般讀者）：第 3 輪通過（退回 0）。第 3 輪提示詞我加了一句「白話定義在後面幾張也算有定義」，比標準提示詞寬。
- 編輯（只給建議）：採納—第 7 張「無關」vs 第 8 張「加分」的矛盾、第 11 張標題方向（較弱／更強）、第 6 張畫出怎麼拆、第 8 張點的意義、Threads 正文改白話、caption 第一句放搜尋詞。沒採納—第 3 張加圖、第 4 張加差距數字、整張合併第 10／11。
- 爭議（交給人）：caption 逐張摘要（程式自動取各張主標）第 1、5、8 條，忠實者認為缺比較對象或比卡寬（第 8 條「串事件基本不受向量影響」）；已超過 3 輪，沒再改。
- 待人：hook（hook-candidates.md，暫用 A）；放行項（論文網址、第 3 張名詞補充、第 6 張 TSMC 假設例子、示意圖 5／8／10）；是否標 ready。

## 人的回饋後的改版（2026-10-27）
- 回饋：Recall 寫英文、Recall@K 解釋繞口令、第 4 頁文字與「橋樑」、腳註太簡潔、第 9 頁要講 SAG 比較不受 embedding 影響、實驗頁缺「所以呢」、整體文字太制式。
- 改動：全篇找回率→Recall（`terms.yaml` 加規則與測試）；標題與補充改口語、換句型；實驗頁補結論句；第 3 張拆成兩張名詞頁（SAG 的三個詞／成績單的三個詞），現在共 14 張；`render.py` 單組橫條圖有小數時全部顯示一位小數（80.0%）。
- 審查：忠實者 r6（第 5 張 blocker：領先縮小沒限定 Recall@5、「題目越深越能保住證據」比卡強）→ 改掉 → r7、r8 通過；讀者 r4/r5 退回（超邊、管線沒定義）→ 拆名詞頁 → r6 通過（退回 0）；重製圖審查者 r4～r6 通過；編輯 r2 只給建議。回歸測試 12/12 全部通過。審查通過版本已重新記錄。
- 沒採納的編輯／讀者建議：第 7、8 張合併、第 12 張補帶走觀念、圖例顏色統一、「前情提要」「先／再認識」標題改寫、「成績的大頭」同詞重複。
- 待人：hook、放行項（多了第 3、4 張名詞說明）、caption 爭議、是否標 ready。
