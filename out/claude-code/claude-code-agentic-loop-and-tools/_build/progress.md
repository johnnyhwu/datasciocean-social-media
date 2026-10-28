# 進度：claude-code-agentic-loop-and-tools（Claude Code 系列第 1 則，雙卡：迴圈＋權限）

- 2026-10-28：spec 完成（現 14 張）；程式 A PASS；程式 B 14/14；contact sheet、build_package 完成。
- 新增圖型（diagrams.py＋tests/test_diagrams.py）：transcript、oneloop、intercept、dial（含兩端標籤）、lanes、layers；新風格 `window`（tests/test_window_style.py）。全部回歸測試通過（2026-10-28，R1 前跑；dial／lanes 之後有改，test_diagrams 重跑通過）。
- R1：忠實者 blocker 6（第 9 張「只專注」、因果「靠權限與沙盒」、第 7 張「只有三種走向」、第 12 張「容易復原」）＋讀者（Agent／Harness／權限模式未定義、第 8、11 張無結論）＋編輯 69 條 → 改版：刪第 5 張（併入失敗頁）、拿掉 OpenClaw、拿掉 Harness 列、工具表前移、重排順序（工具→失敗→攔截→範圍→可逆→刻度→通道→流程→防線）。
- R2：忠實者通過（blocker 0）；已 `spec_diff --mark`。讀者 R2：流程圖邏輯錯位、第 10 張自動核准像第三個動作、第 12 張缺圖例、「漸進式」不白話。
- R3：依 R2 讀者改（流程圖改單一節點三結果、lanes 加箭頭、layers 加圖註、第 7 張改 pairs、白話補充）→ 忠實者（改過的區塊）＋讀者 R3。
- hook：暫用初稿（hook.candidate 含「暫定」），候選在 hook-candidates.md，等人挑；takeaway 的 question、Threads 第一句要跟著改。
- 系列名、planned_title、hashtag、summary 皆暫用，待人確認；第 2 則 spec 尚未做。
- 編輯 R1 未處理的建議（需人知道）：caption 逐張摘要太長（11 條→可縮）、Threads 與 IG 分工、系列地圖「一次看完」標題、「系列第 1 則」序號語。
- 網路補充（官方來源）：series/claude-code/research.md，人審過才加進貼文（目前貼文是純卡版）。
- R3 結果：忠實者第 9 張夾帶（「權限模式＝刻度上的一格」「管得嚴」）→ 已刪；讀者仍有一項擋住主軸：「權限模式」沒說有哪些（卡上只有 pending 的 perm c9 講，不能用；留給人決定）。
- R4：忠實者第 4、9、11 張通過；第 7 張（c17／c18 範圍窄→兼顧）一再被擋（比較對象 OpenClaw 與「觀測性良好」被拿掉後變強）→ 依「評價類最先砍」整張刪除（只刪內容，免重審）。現 13 張。
- 狀態：程式 A PASS、程式 B 13/13、審查通過版本已 `spec_diff --mark`；batch_check PASS（存量 WARN 是預期）。**等人：挑 hook、確認系列名／標題／hashtag／summary、決定「權限模式」要不要補（需人授權用 pending c9）、官方來源補充審查。**
- 2026-10-28 補充：人要求把官方來源資料併進既有頁、由 Claude 自己驗證（不給審查者）。已重抓官方頁逐條核對（`_build/supplements.md`），併入第 3、4、6、7 張正文，新增第 9 張（六種權限模式）與第 13 張（沙盒兩種隔離、84%）。現 15 張；程式 A PASS、程式 B 15/15。忠實者 R5（只審卡上內容有沒有被補充句矛盾）：第 3、4、6、7、9、13 張完全支持、0 錯誤；已 `spec_diff --mark`。
- 驗證發現：auto 在 v2.1.283 起是內建起始模式，故不寫「Manual 是預設」；受保護路徑已核對但版面放不下；93% 沒放。
- 仍待人：挑 hook、系列名／標題／hashtag／summary、發布前再重抓官方頁。
- 2026-10-28 hook 人挑定（A2 主標加 Claude Code）；副標改保守；封面、帶走張、Threads 第一句已同步；忠實者 R6 通過並 mark。程式 A PASS、B 15/15。還待人：系列名／標題／hashtag／summary 確認、最後確認圖文。
- 2026-10-28 第 9 頁權限模式拆成兩張（前三種／後三種，中文名＋英文代號＋白話說明＋官方例子），新增圖型 `turn` 重畫「一輪怎麼走」（現第 12 張，標明範例、只寫需要確認的先問使用者）。現 16 張；程式 A PASS、程式 B 16/16、全部回歸測試通過。忠實者 R7（第 9、10 張放行）、R8 擋第 12 張→改→R9 通過；已 mark。
