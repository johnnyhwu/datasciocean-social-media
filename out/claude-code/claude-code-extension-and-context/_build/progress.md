# 進度：claude-code-extension-and-context（Claude Code 系列第 2 則，單卡：擴充＋context）

- 2026-10-28：spec 初稿完成（16 張，`_build/spec.json`，由 scratchpad 的 mk_spec2.py 產生，之後直接改 spec.json）；程式 A PASS（ERROR 0）；程式 B 16/16；contact sheet 已產生。尚未 commit。
- 新增圖型（`diagrams.py`）：sockets、lazy、hub、pinned、compact、sidecar；transcript 加 tone「hook」；`_win` 窄視窗標題改放左邊；intercept 的標籤框改成依字寬（畫面不變）。**這些新圖型還沒補 `tests/test_diagrams.py` 的正案與壞案，也還沒跑全部回歸測試。**
- hook：暫用初稿（hook.candidate 含「暫定」），**候選還沒寫進 `_build/hook-candidates.md`**，要用純文字列給人挑；takeaway 的 question、Threads 第一句要跟著改。
- 系列檔：成員 2 的 summary 已改成白話（待忠實者與讀者審一次）；planned_title 仍是暫用的「Skills、Hooks、MCP 怎麼組成一套 Harness？」，與這則實際內容（還含 context 管理）不完全相符，且第 1 則系列地圖上印的也是 planned_title，兩則的 planned_title 要跟最後挑定的 hook 對齊後重渲第 1 則。
- 官方來源補充（2026-10-28 已重抓核對，Claude 自己驗證、不經審查者）：skills、hooks-guide、memory、sub-agents、mcp、how-claude-code-works、features-overview（context 成本表）、anthropic.com/engineering/effective-context-engineering-for-ai-agents。**`_build/supplements.md` 還沒寫**（要列每條補充的張數、URL、原文）。
- 還沒做：自己看 16 張 PNG 逐張確認（只看過第 7、12 張）、`build_package.py`、忠實者（只審卡內容是否被補充句矛盾）、讀者、編輯、`spec_diff --mark`、`batch_check.py`、回歸測試。
- 沒放進貼文的已核對事實：Explore／Plan 子代理不帶 CLAUDE.md（與卡 c20 的「一致套用」可能被讀成矛盾，故不放）；Hook 事件數；MCP 傳輸類型；SKILL.md 檔名（卡沒有，程式 A 擋拉丁名稱）。

## 2026-10-29 更新
- 新圖型已補 `tests/test_diagrams.py` 正案與壞案（通過）；全部回歸測試在背景重跑中（log 在 scratchpad regress2.log）。
- `supplements.md`、`hook-candidates.md` 已寫。第 7 張主標改為「提示裡的規則是寄望，Hook 讓它強制執行」（避開「才」）；第 15 張帶走縮成 3 行（4 行會撞到裝飾視窗）。
- 程式 A PASS、程式 B 16/16、`build_package` 完成。
- R1 已派：忠實者（放行項：官方補充、假設例子、視覺元素）、一般讀者（4 題，Q4 是陷阱題）、編輯；輸出在 `reviews/faithful-r1.json`、`reader-r1.json`、`editor-r1.json`。審查期間不改 spec 文字。

## 2026-10-29 審查 R2／R3 與修訂
- R1 通過版本 reviewed-spec 已於 R2 前記下；之後依讀者／編輯建議集中修訂（標題變化、白話定義、補 Model 列、結束碼說明、第 11 張圖例、第 13 張去重、第 14 張補鋪墊、Taiwan 用語）。
- 忠實者 R2：第 7 張標題「才」、第 12 張「讀檔」→ 已改。R3（只審改動區塊）：第 8 張與 caption 的「三種用法」、第 12 張「獨立 context」、第 14 張「檢查沒過」例 → 已用削弱或標明官方文件的方式改完（沒有再派 R4，依 review-loop 削弱語氣免審；第 12 張新增句為官方文件原文，已對 supplements.md）。
- 讀者 R2／R3：Q1～Q4 答得出、Q5 貼文沒寫（陷阱題過）；第 14 張仍被評為「抽象、說服力弱」，已補子標但未再審。
- 待人決定：hook 與系列名／標題；第 13 張 MCP 列（官方載入方式）與卡 c13 的張力是否接受；是否先發第 1 則。
- 尚未 `state.py ready`，未 commit，未發布。

## 2026-10-29 人的回饋與 R4／R5
- 人挑 hook C1；人要求：貼文不特別寫「blog」「官方」（內容我們負責）、第 8 張整合並寫得更易懂、第 14 張圖重做。已全部處理；新增圖型 `combo`（tests/test_diagrams.py 有正案與壞案，全過）。
- 忠實者 R4 抓到的：第 8 張「改完自動跑檢查」、第 14 張例一漏「可能」、第 15 張「六個機制單獨都不新」措辭 → 已改；R5 只審改動區塊（第 2、3、8、13、14、15、16 張）通過（blocker 0）。
- 讀者 R4：第 14 張「一輪」「Hook 觸發的重試」沒鋪墊 → 第 3 張補「每一輪（每回應一次）」、第 14 張補子標；第 13 張補「壓縮」列對上封面六個。讀者沒有再審 R5（只剩理解面的小調整）。
- 兩則的 planned_title 已對齊並重渲第 1 則系列地圖（第 1 則 spec 文字沒動）。
- 待人決定：系列名／hashtag、第 13 張 MCP 列（忠實者：不矛盾但有張力）、發布順序。尚未 ready、未 commit、未發布。

## 2026-10-31 發布
- 發布前重抓官方文件核對 `supplements.md` 的 13 條補充（how-claude-code-works、features-overview、hooks-guide、skills、memory、sub-agents、mcp）：原文一字未改，沒有改版。
- `series_links.py --write` 補上第 1 則 Threads 連結 → 重跑 check_a（PASS，ERROR 0）、build_package、batch_check（PASS，只有存量 WARN）。
- 人決定第 13 張 MCP 列照原樣發（卡 c13 沒提載入時機，忠實者判定不矛盾但有張力）；人授權整串發布與 commit／push。
- 兩個格式 `ready` →`prepare` → push `ig/jpg/`（894a27f）→ 預檢（16 張，可沿用）→ IG dry-run（problems 0、warnings 0）→ IG 發布：https://www.instagram.com/p/DfI172ND6Xv/ （media_id 18105037832457914，00:13:35+0000）
- Threads dry-run（2 則）→ 發布：https://www.threads.com/@datasciocean/post/DfI2QXrj7JH （root_id 18148411657569222，00:16:30+0000）
- 兩個格式 state 都是 `published`。第 1 則 Threads 回補已進 `state/backfill.md`，待人說「發」。
