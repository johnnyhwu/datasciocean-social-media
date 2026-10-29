---
id: claude-code
name: "Claude Code：怎麼讓 AI 敢自己改你的程式"   # 人挑定（2026-10-29，候選 A）；會印在每張圖上，發布後不能改
philosophy: series/claude-code/philosophy.md   # 尚未做：新系列要先做視覺哲學與樣張，人審過才量產
color: window   # 相鄰系列不同色（目前已用：teal-mid、paper-cards、spotlight、abyss-contour）
style: window   # 2026-10-28 人選 A「視窗」（終端機視窗）
members:   # 草案（人決定 2026-10-28：合成 2 則；未鎖定、一則一則發）
  - concept: claude-code-agentic-loop-and-tools
    also: [claude-code-permission-blast-radius]   # 雙卡：迴圈與工具＋權限與犯錯代價（待人看成果再定發文順序）
    planned_title: 讓 Claude Code 自己改檔案、下指令，不會出事嗎？   # 人挑定（2026-10-28）
    summary: 反覆讀程式碼、改程式碼、驗證，出錯就拿錯誤再來一輪；Agent 無人看管時，安全設計的目標是讓犯錯代價低、能還原。   # 2026-10-29 白話改寫，忠實者重審通過（BLOCKER 無），讀者已看過
  - concept: claude-code-extension-and-context
    planned_title: Claude Code 靠六個機制，擴充能力又管住 context   # 人挑定（2026-10-29，C1）
    summary: 三個幫 Claude Code 加功能的做法，三個管理 AI 讀進內容的做法；各自不特殊，能彼此組合才是重點。   # 2026-10-29 忠實者重審通過（BLOCKER 無），讀者已看過；標題的 context 為人挑的 hook，不改
hashtag: ClaudeCode   # 人決定（2026-10-29）：不用特別把 DataSci Ocean 與 Claude Code 寫在一起，不用 DSO_ 前綴
members_locked: true   # 2026-10-29 人說發佈第一則；鎖定後系列名與各則 planned_title 不改
status: planning
---

# 拆解 Claude Code

來源文章：`claude-code`（3 張卡，皆 `bound_to_source`，預設組成系列）。

## 規劃備忘（2026-10-28）

- 2026-10-28 人決定：合成 2 則（迴圈＋權限一則雙卡、擴充一則）；發文順序待看成果再定；一則一則發（鎖定前要講明代價：系列名與後面各則的 planned_title 印在圖上不能改）；視覺人還在想。
- 原發文順序（建議，3 則版）：迴圈與工具 → 權限與爆炸半徑 → 擴充與 context。權限那張的核心（工具呼叫是攔截點、失敗變成下一輪輸入）接在迴圈後面最順；擴充那張當收尾（「單獨都不新穎，組合起來才是 Harness」）。
- 三張卡共用的背景主張（c2 是什麼、c3 Harness、c4 三層架構）每則都重複，只在第 1 則完整講，後兩則一句帶過。
- 迴圈卡與權限卡有兩組相同主張（c5=c8 攔截點、c6=c9 失敗變輸入）→ 合併候選，待人決定。
- `pending_author_confirmation`（不可用）：loop c12（刻意精簡工具）、c15、c16（窄工具優先於 Bash）；permission c9（三種權限模式）、c13（force-push／rm -rf 一律確認）。
- 沒有任何主張附 `figures`。
