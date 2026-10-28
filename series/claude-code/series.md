---
id: claude-code
name: "拆解 Claude Code"   # 草案，待人確認；會印在每張圖上，發布後不能改
philosophy: series/claude-code/philosophy.md   # 尚未做：新系列要先做視覺哲學與樣張，人審過才量產
color: window   # 相鄰系列不同色（目前已用：teal-mid、paper-cards、spotlight、abyss-contour）
style: window   # 2026-10-28 人選 A「視窗」（終端機視窗）
members:   # 草案（人決定 2026-10-28：合成 2 則；未鎖定、一則一則發）
  - concept: claude-code-agentic-loop-and-tools
    also: [claude-code-permission-blast-radius]   # 雙卡：迴圈與工具＋權限與犯錯代價（待人看成果再定發文順序）
    planned_title: Claude Code 為什麼敢自己動手改程式？   # 暫用，待人確認
    summary: 核心只有一個迴圈：讀、改、驗證，失敗也只是下一輪的輸入；安全機制的目標是讓犯錯便宜又可逆。   # 暫用，依該則的卡寫，發布前由忠實者審過一次
  - concept: claude-code-extension-and-context
    planned_title: Skills、Hooks、MCP 怎麼組成一套 Harness？   # 暫用，待人確認
    summary: 摘要、Subagent、CLAUDE.md 單獨都不新鮮，能自動彼此組合才讓它成為 Harness。   # 暫用，依該則的卡寫，發布前由忠實者審過一次
hashtag: DSO_ClaudeCode   # 暫用，待人確認
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
