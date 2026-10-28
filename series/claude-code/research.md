# Claude Code 系列：網路補充資料（2026-10-28）

人的例外授權（2026-10-28）：這個系列的貼文**可以用網路上查到的資料補充觀念卡**（平常只能用卡）。

**流程（人決定，2026-10-28；不改原本的 workflow、不改程式）**：
1. 貼文照原流程只用卡做完，subagent 審查照常。
2. 補充資料**只准來自官方網站**（code.claude.com、anthropic.com 官方頁面），不用第二手；每條附 URL 與原文。
3. 補充資料**由人審查**（不經 subagent 審查者）：人看過、同意，才補進貼文。
4. 補上後重跑程式 A、B 與渲染；若程式 A 擋住沒有卡主張引用的區塊，回報給人，不自行改程式。
內容標準不變：不得寫成來源沒有的事；每條補充都要附來源 URL 與原文，才能讓忠實者核對。
資料都是 2026-10-28 當天抓的；Claude Code 版本變動快，發布前要重查一次。

來源等級：**官方文件**（code.claude.com/docs）＞ **Anthropic 工程部落格**（anthropic.com/engineering）＞ 第二手報導（不用，只列出來提醒）。

---

## 對應第 1 則（迴圈與工具）

來源：https://code.claude.com/docs/en/how-claude-code-works

- **E1-1** 迴圈三個階段：gather context（蒐集脈絡）、take action（動手）、verify results（驗證）。「These phases blend together.」你可以隨時中斷；Esc 立刻停止、或直接打字修正，Claude 會在這一輪的工具呼叫結束後讀到。
- **E1-2** 內建工具分五類：File operations、Search、Execution、Web、Code intelligence（需要外掛）。另有開 subagent、問使用者問題等協調用的工具。
- **E1-3** 例子：「fix the failing tests」→ 跑測試 → 讀錯誤 → 搜尋相關檔案 → 讀檔 → 改檔 → 再跑測試（官方列的六步）。
- **E1-4** 「Claude Code is the layer around the model that provides the tools and manages the context the model sees. This surrounding layer is what the term agentic harness refers to.」
- **E1-5** 同一個迴圈跑在終端機、桌面 app、IDE、網頁、Slack、CI/CD；介面不同、迴圈相同。
- **E1-6** 對話每則訊息、工具呼叫與結果都以純文字 JSONL 寫在 `~/.claude/projects/`；改檔前會先快照，按兩下 Esc 可倒回。**檢查點只涵蓋檔案修改**，資料庫、API、部署這類對外動作無法回復，靠權限控制。
- **E1-7** 模型選擇：Sonnet 處理多數編碼任務，Opus 給較複雜的架構決策；`/model` 切換。

## 對應第 2 則（權限與犯錯代價）

來源：permissions、permission-modes、sandboxing 三頁官方文件，與兩篇工程部落格。

官方文件
- **E2-1** 預設（Manual）：讀檔與 Grep 不用問（在工作目錄內）；Bash、改檔、WebSearch 要問；Bash 有一組內建的唯讀指令例外（https://code.claude.com/docs/en/permissions）。
- **E2-2** 規則求值順序 deny → ask → allow，第一個命中的決定結果；「An allow rule can't carve an exception out of a deny rule.」
- **E2-3** 權限模式（https://code.claude.com/docs/en/permission-modes）：Manual（`default`，只自動放行讀取）、`acceptEdits`（讀、改檔與 mkdir／mv 等，限工作目錄）、`plan`（只讀、先提計畫）、`auto`（背景分類器審查）、`dontAsk`（要問的一律拒絕，給 CI）、`bypassPermissions`（全放行，只准在隔離的容器／VM）。Shift+Tab 切換。
  - 注意：卡上 permission c9（三種權限模式）是 `pending_author_confirmation`，**卡不能用，但官方文件的模式可以用**——寫法要以官方文件為準，不要借卡的三段說法。
- **E2-4** 「Deny rules block in every mode, including `bypassPermissions`.」；連 `bypassPermissions` 也不放行的：明確的 ask 規則、辨識出的 `rm`／`rmdir` 重要路徑刪除。
- **E2-5** 受保護路徑永遠不自動核准（`bypassPermissions` 除外）：`.git`、`.claude`、`.vscode`、`.idea`、shell 啟動檔（`.bashrc`、`.zshrc`）、`.mcp.json` 等。安全檢查在 allow 規則之前執行，allow 規則不能預先核准。
- **E2-6** auto 模式預設擋：`curl | bash`、把敏感資料送到外部、正式環境部署、雲端儲存大量刪除、force push、`git reset --hard`、`terraform destroy`、在沒人核准下合併 PR 等；預設放行：工作目錄內的檔案操作、安裝 lock file 裡宣告的相依套件、唯讀 HTTP、推送到目前 repo 的分支。
- **E2-7** 分類器連續擋 3 次、或累計 20 次，auto 模式暫停、回到逐次詢問。官方說明：「Auto mode reduces permission prompts but does not guarantee safety.」
- **E2-8** 你在對話裡說的界線（例如「別 push」）分類器會當作封鎖訊號，但「Boundaries are not stored as rules」，可能在壓縮後遺失；要硬保證用 deny 規則。
- **E2-9** `bypassPermissions`：「offers no protection against prompt injection or unintended actions」；Linux／macOS 上以 root／sudo 執行會被拒絕。
- **E2-10** 沙箱（https://code.claude.com/docs/en/sandboxing）：Bash 在 OS 強制的邊界裡執行（macOS Seatbelt、Linux／WSL2 bubblewrap）；寫入限工作目錄與暫存；網路沒有直接路徑、經 proxy 檢查網域白名單（預設空的）。官方稱沙箱與權限是「complementary layers」；「the operating system enforces the sandbox boundary on the running process, so it holds regardless of what the model chose to run.」預設關閉（`/sandbox` 開）。沙箱**不涵蓋** Read／Edit／Write／WebFetch 等內建工具與 hooks。
  - 與卡 c15（權限機制與執行邊界是兩道獨立防線）直接呼應。
- **E2-11** 檢查點：改檔前快照、Esc Esc 倒回；對資料庫、API、部署不適用（how-claude-code-works）。與卡 c1（讓犯錯代價低廉且可逆）呼應：檔案可逆、對外動作不可逆，所以後者靠權限擋。

Anthropic 工程部落格
- **E2-12** 沙箱：https://www.anthropic.com/engineering/claude-code-sandboxing（2025-10-20）「In our internal usage, we've found that sandboxing safely reduces permission prompts by 84%.」只有這一個數字，內部使用、未說明量測方法。必須同時有檔案系統與網路隔離：沒有網路隔離，被入侵的 Agent 可以外傳 SSH 金鑰；沒有檔案系統隔離，容易逃出沙箱取得網路。
- **E2-13** auto 模式：https://www.anthropic.com/engineering/claude-code-auto-mode（2026-03-25）「in practice users accept 93% of them anyway」（使用者實際上核准 93% 的提示）；「approval fatigue」＝人逐漸不再注意自己在核准什麼。分類器兩階段：第 1 階段是快速單 token 篩選（偏向擋）、第 2 階段才用思考鏈降低誤擋。實測：真實流量 n=10,000，完整流程誤擋率 0.4%（只有第 1 階段 8.5%）；真實「過度積極」動作 n=52，漏擋率 17%（只有第 1 階段 6.6%）；合成外洩 n=1,000，漏擋率 5.7%。
  - **警告**：文章對 93% 沒說樣本與期間；6.6% 在 n=52 對不出整數（約 3~4 件）。**不要把 0.4% 與 17% 並列成同一個「準確率」**（兩者來自不同測試集）。
  - **不用**：網路上流傳的「1,053 位測試者、人類攔下 13.6% vs 分類器 89%」我在這篇原文找不到，只有第二手報導，**不要用**。

## 對應第 3 則（擴充與 context）

- **E3-1** CLAUDE.md（https://code.claude.com/docs/en/memory）：每次 session 開頭載入；「Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead.」位置：專案（`./CLAUDE.md`）、個人（`~/.claude/CLAUDE.md`）、組織管理（macOS `/Library/Application Support/ClaudeCode/CLAUDE.md` 等）；`@path` 匯入，最深 4 層；官方建議每個檔案「target under 200 lines」；`/init` 自動產生起始檔。也可讀 `AGENTS.md`（v2.1.277 起）。
- **E3-2** 自動記憶（auto memory）：Claude 自己寫下學到的偏好；每個 session 載入 MEMORY.md 的前 200 行或 25KB（先到者）。CLAUDE.md 是人寫的指令；auto memory 是 Claude 寫的筆記。
- **E3-3** Skills（https://code.claude.com/docs/en/skills）：資料夾＋必要的 `SKILL.md`（YAML frontmatter＋指示）；描述常駐 context、**內文用到才載入**；描述與 `when_to_use` 合計在清單中截斷於 1,536 字元；建議 `SKILL.md` 少於 500 行；位置：個人 `~/.claude/skills/`、專案 `.claude/skills/`；`/skill-name` 手動叫，或由 Claude 依描述自動載入；`disable-model-invocation: true` 讓它只能手動叫（適合有副作用的流程，如部署）。自訂指令（commands）已併入 skills。
- **E3-4** Hooks（https://code.claude.com/docs/en/hooks、hooks-guide）：目前文件列 33 種事件（例：`SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`Stop`、`SubagentStart`／`SubagentStop`、`PreCompact`／`PostCompact`…）；處理器種類：command、http、mcp_tool、prompt、agent。**結束碼**：exit 0＝成功；**exit 2＝阻擋**（連 JSON 寫 allow 也擋不了它）；其他結束碼（含 1）只是不阻擋的錯誤，「If your hook is meant to enforce a policy, use `exit 2`.」`PreToolUse` 可回傳 allow／deny／ask／defer，甚至改寫工具的輸入。官方說法：Hooks 提供「deterministic control: certain actions always happen rather than relying on the LLM to choose to run them」。
- **E3-5** Subagents（https://code.claude.com/docs/en/sub-agents）：自己的 context window、自己的 system prompt 與工具權限；內建 Explore（唯讀、快）、Plan（唯讀）、General-purpose；Explore 啟動時**不帶 CLAUDE.md**；可限制工具（allowlist／denylist）、指定較便宜的模型（如 Haiku）；`.claude/agents/*.md`；預設最多往下 3 層、同時最多 20 個。只有 subagent 最後的摘要回到主對話。
- **E3-6** 壓縮（how-claude-code-works）：接近上限自動壓成摘要；摘要保留你的請求與重要程式片段，「detailed instructions from early in the conversation may be lost」→ 持久規則要放 CLAUDE.md；CLAUDE.md 可加「Compact Instructions」段、或 `/compact focus on …`；`/context` 看佔用。連續壓縮都立刻又滿，會停止自動壓縮並報錯（不無限迴圈）。
- **E3-7** MCP（https://code.claude.com/docs/en/mcp）：開放標準；傳輸：HTTP（遠端建議）、stdio（本機行程）、SSE（已棄用）、WebSocket；範圍：local／project（`.mcp.json`，進版控）／user；工具定義預設延後載入（tool search），沒用到時只佔名稱；工具輸出超過 10,000 token 警告、預設上限 25,000；「Verify you trust each server」，抓外部內容的 server 有 prompt injection 風險；專案層級 server 要先經使用者核准。
- **E3-8** Anthropic「Effective context engineering for AI agents」（https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents，2025-09-29）：context rot（token 越多，模型從脈絡準確回想資訊的能力越下降）；壓縮＝把接近上限的對話摘要後開新視窗，Claude Code 會保留關鍵細節、丟掉多餘的工具輸出，並帶著最近存取的 5 個檔案繼續；sub-agent 可能花數萬 token 探索，只回傳約 1,000～2,000 token 的摘要；Claude Code 是混合式：CLAUDE.md 一開始就放進去，glob／grep 讓它即時去撈檔案（just-in-time）。

---

## 使用建議（各則可放的「卡以外」內容）

- 第 1 則：三階段迴圈（E1-1）＋「fix failing tests」六步實例（E1-3）當具體例子，比卡的抽象敘述好懂；五類工具（E1-2）；介面不同、迴圈相同（E1-5）；Harness 的官方定義（E1-4）。
- 第 2 則（卡被擋了兩條，最薄）：官方模式與規則順序（E2-2、E2-3）、受保護路徑（E2-5）、auto 分類器預設擋／放（E2-6、E2-7）、沙箱兩層與 84%（E2-10、E2-12）、93% 與審批疲勞（E2-13）。**這樣這則的論點「犯錯要便宜且可逆」才有東西可講。**
- 第 3 則：最適合補實務：CLAUDE.md 不是強制的 → 要強制用 Hook（E3-1、E3-4 的 exit 2）；Skill 的漸進載入；Subagent 的 1,000～2,000 token 摘要；壓縮會丟早期指示（E3-6）。

## 風險與待確認

1. **版本時效**：模式名、hook 事件數（33）、預設模式（auto 是否為起始模式依版本）、Sonnet 5 當分類器，都會變。貼文寫「截至 2026-10 的官方文件」，發布前重抓。
2. **第二手資料不用**：1,053 人測試、13.6%／89% 等只在第二手報導，原文查無。
3. **卡與官方文件不一致處**：卡是「blog 判斷」，官方文件是事實描述；兩者並列時要標清楚誰說的（主詞要是官方／部落格），不要混成一句。
4. **管線衝突**：`check_a.py` 目前只認卡的 claim id 與逐字引用；補充資料需要新的錨點類型與引用格式，見對話中的提案。
