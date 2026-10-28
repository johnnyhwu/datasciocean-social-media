# 官方來源補充（人授權的例外；由 Claude 自己對照官方原文驗證，不經審查者）

2026-10-28 當天重新抓取下列頁面，逐條對照原文。發布前要再抓一次確認沒改版。

| 貼文位置 | 補充內容 | 來源 | 原文（核對過） |
|---|---|---|---|
| 第 3 張 | 官方把一輪描述成蒐集脈絡、動手、驗證三個階段，階段會混在一起 | code.claude.com/docs/en/how-claude-code-works | "it works through three phases: gather context, take action, and verify results. These phases blend together." |
| 第 4 張 | 內建工具分五類：檔案操作、搜尋、執行、網路、程式碼智慧 | 同上 | 表格 File operations / Search / Execution / Web / Code intelligence |
| 第 6 張 | 規則檢查順序 deny、ask、allow，第一個命中的決定結果 | code.claude.com/docs/en/permissions | "Rules are evaluated in order: deny, then ask, then allow. The first match in that order determines the outcome" |
| 第 7 張 | 改檔前先快照，按兩下 Esc 倒回；資料庫、API、部署倒不回來 | how-claude-code-works | "Before Claude edits a file, it snapshots the current contents... press Esc twice to rewind"；"Actions that affect remote systems (databases, APIs, deployments) can't be checkpointed." |
| 第 9 張 | 六種權限模式的名稱與一句話；Shift+Tab 切換 | code.claude.com/docs/en/permission-modes | default（Manual）Reads only／acceptEdits Reads, file edits, common filesystem commands／plan 探索並提計畫／auto 背景分類器審查並擋下危險動作／dontAsk 要問的一律拒絕／bypassPermissions Everything，Isolated containers and VMs only |
| 第 13 張 | 沙盒讓內部使用的權限提示減少 84%；兩種隔離要同時有；沙盒由 OS 強制執行，只管 shell 指令 | anthropic.com/engineering/claude-code-sandboxing（2025-10-20）；code.claude.com/docs/en/sandboxing | "In our internal usage, we've found that sandboxing safely reduces permission prompts by 84%."；"effective sandboxing requires both filesystem and network isolation"；"The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it." |

## 驗證時發現與先前整理（research.md）不同的地方
- 預設模式：auto 在 Claude Code v2.1.283 起是互動式終端機與 VS Code 的內建起始模式，所以貼文不寫「Manual 是預設」。
- auto 的描述改成「背景分類器把關」（官方原文是 reviews most actions，不是每個動作）。
- 受保護路徑（.git、.claude 等寫入不自動核准，bypassPermissions 例外）已核對屬實，但這則版面放不下，沒放；第 2 則可用。
- 沒放：auto 模式 93% 核准率（沒重抓、沒給樣本）。
