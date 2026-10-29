# 官方來源補充（人授權的例外；由 Claude 自己對照官方原文驗證，不經審查者）

2026-10-28 重新抓取下列頁面，逐條對照原文。發布前要再抓一次確認沒改版。

| 貼文位置 | 補充內容 | 來源 | 原文（核對過） |
|---|---|---|---|
| 第 3 張 | Harness 是包在模型外面、提供工具並管理模型所看內容的那一層 | code.claude.com/docs/en/how-claude-code-works | "Claude Code is the layer around the model that provides the tools and manages the context the model sees. This surrounding layer is what the term agentic harness refers to." |
| 第 3 張 | Context 裡有哪些東西 | 同上 | "Claude's context window holds your conversation history, file contents, command outputs, CLAUDE.md, auto memory, loaded skills, and system instructions." |
| 第 4 張 | 擴充是疊在核心迴圈上的一層 | 同上 | "These extensions form a layer on top of the core agentic loop." |
| 第 5 張 | Skill 的描述平常在 context 裡、整份內容用到才載入 | code.claude.com/docs/en/skills | "In a regular session, skill descriptions are loaded into context so Claude knows what's available, but full skill content only loads when invoked." |
| 第 6 張 | Hook 提供確定性的控制 | code.claude.com/docs/en/hooks-guide | "…which gives you deterministic control: certain actions always happen rather than relying on the LLM to choose to run them." |
| 第 7 張 | CLAUDE.md 或 Skill 裡的規則是請求，不是保證；要硬擋用 PreToolUse Hook | code.claude.com/docs/en/features-overview | "An instruction like "never edit `.env`" in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement." |
| 第 8 張 | 結束碼 2 才阻擋；結束碼 0 是沒意見；其他結束碼在多數事件裡動作照樣進行 | code.claude.com/docs/en/hooks-guide | "Exit 0: …exit 0 doesn't approve it." "Exit 2: write a reason to stderr." "With an exit code besides 0 and 2 and no valid JSON output, the action proceeds on most events…"；範例「Block edits to protected files」用 exit 2 阻擋 |
| 第 9 張 | 官方提醒只連你信任的 MCP server | code.claude.com/docs/en/mcp | "Verify you trust each server before connecting it. Servers that fetch external content can expose you to prompt injection risk." |
| 第 10 張 | CLAUDE.md 是 context，不是強制的設定 | code.claude.com/docs/en/memory | "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead." |
| 第 11 張 | 壓縮的摘要保留你的請求與重要程式片段；早期的詳細指示可能遺失，持久規則放 CLAUDE.md | code.claude.com/docs/en/how-claude-code-works | "The summary keeps your requests and key code snippets, but detailed instructions from early in the conversation may be lost. Put persistent rules in CLAUDE.md rather than relying on conversation history." |
| 第 12 張 | Subagent 在自己的 context window 裡工作，只回傳摘要 | code.claude.com/docs/en/sub-agents | "the subagent does that work in its own context and returns only the summary." |
| 第 13 張 | 各機制載入 context 的時機（整張表） | code.claude.com/docs/en/features-overview（Context cost by feature） | CLAUDE.md：Session start，Full content，Every request；Skills：Descriptions at start, full content when used；MCP servers：Tool names; full schemas on demand；Subagents：Isolated from main session；Hooks：Zero, unless hook returns additional context |

## 驗證時發現與先前整理（research.md）不同的地方
- research.md 的 E3-1 寫「CLAUDE.md 建議少於 200 行」：這則沒放（版面與數字檢查，且與卡無關）。
- 只有 Anthropic 工程部落格（2025-09-29）提到的「Subagent 通常回傳 1,000～2,000 token 的摘要」已核對屬實，但數字沒有卡上的比較對象，沒放進貼文。
- Explore／Plan 這兩種內建 Subagent 啟動時不帶 CLAUDE.md（sub-agents 頁）：已核對，但可能被讀成與卡 c20「CLAUDE.md 的慣例一致套用」互相矛盾，沒放。
- Hook 事件的總數沒重抓，貼文不寫數字。
- SKILL.md 這個檔名卡上沒有，程式 A 會擋圖上的名稱，所以圖上寫「整份指示」。

## 2026-10-29 重新查證：第 13 張 MCP 列
code.claude.com/docs/en/features-overview（MCP servers）："What loads: Tool names and server instructions from connected servers. Full JSON schemas stay deferred until Claude needs a specific tool." "Tool search is on by default, so idle MCP tools consume minimal context."
code.claude.com/docs/en/mcp：不使用 tool search 的情形包括 `ENABLE_TOOL_SEARCH=false`、較舊的模型、部分 gateway／Foundry 部署（改成 upfront loading，即一開始就載入定義）。
→ 貼文改成「預設只讀工具名稱，用到才讀定義」（加「預設」，不寫成所有情況）。
