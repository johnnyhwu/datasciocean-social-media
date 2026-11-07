# 發布包總覽（程式產生，不手改）

每則貼文一個資料夾，打開裡面的 `README.md`；IG 看 `ig/post.md`，Threads 看 `threads/post.md`。

## 待發布

（目前沒有）

## 拆解 Cerebras 知識庫：資料怎麼進來，答案怎麼出去（`cerebras-rag`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `rag-narrow-waist`＋`slack-distillation-and-bursting` | Slack、Wiki、程式碼、Jira，怎麼塞進同一張表？ | 已發布 | 已發布 | [README](rag-narrow-waist/README.md) |
| 2 | `slack-vector-failure-orthogonal-signals`＋`rrf-rank-fusion` | 搜尋出三種毛病，Cerebras 不是多加幾招，是一種毛病配一帖藥 | 已發布 | 已發布 | [README](slack-vector-failure-orthogonal-signals/README.md) |
| 3 | `rag-planner-single-round-vs-agentic`＋`retrieval-reasoning-decoupling` | 搜尋每次都把所有工具叫一遍？又慢又貴 | 已發布 | 已發布 | [README](rag-planner-single-round-vs-agentic/README.md) |

## Claude Code：怎麼讓 AI 敢自己改你的程式（`claude-code`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `claude-code-agentic-loop-and-tools`＋`claude-code-permission-blast-radius` | 讓 Claude Code 自己改檔案、下指令，不會出事嗎？ | 已發布 | 已發布 | [README](claude-code-agentic-loop-and-tools/README.md) |
| 2 | `claude-code-extension-and-context` | Claude Code 靠六個機制，擴充能力又管住 context | 已發布 | 已發布 | [README](claude-code-extension-and-context/README.md) |

## JEV 串接 Judge 系列（`jev-cascade`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `jev-cascade-overview` | 便宜的 Judge 先判，沒把握才轉給 GPT-6 | 已發布 | 已發布 | [README](jev-cascade-overview/README.md) |
| 2 | `judge-readable-vs-derive`＋`confidence-three-metrics` | Judge 能不能用，先問答案能不能讀出來或核對 | 已發布 | 已發布 | [README](judge-readable-vs-derive/README.md) |
| 3 | `cascade-complementary-errors`＋`cascade-threshold-and-failure-mode` | 串接為什麼成立，門檻選錯又會怎樣 | 已發布 | 已發布 | [README](cascade-complementary-errors/README.md) |

## 拆解 LLM-as-a-Verifier：AI 怎麼替 AI 打分數（`llm-as-a-verifier`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `verifier-expected-value-vs-argmax`＋`verifier-three-knobs-g-k-c` | 叫 AI 打 1 到 5 分，為什麼一堆平手？ | 已發布 | 已發布 | [README](verifier-expected-value-vs-argmax/README.md) |
| 2 | `ppt-pivot-tournament`＋`verifier-three-knobs-g-k-c` | 從 20 個答案挑最好的，AI 評審不必兩兩都比 | 已發布 | 已發布 | [README](ppt-pivot-tournament/README.md) |
| 3 | `verifier-results-how-to-read` | 論文說 LLM-as-a-Verifier 表現最好，功勞真的是它的嗎？ | 未做 | 未做 | [README](verifier-results-how-to-read/README.md) |

## Persona-Aware-D2S: 同一份文件，怎麼長出不同簡報（`persona-aware-d2s`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `persona-d2s-task-and-pipeline` | 同一份文件，怎麼長出四種簡報？ | 已發布 | 已發布 | [README](persona-d2s-task-and-pipeline/README.md) |
| 2 | `persona-d2s-training-design-flaws` | 80 筆資料訓出來的模型，能信嗎？ | 已發布 | 已發布 | [README](persona-d2s-training-design-flaws/README.md) |
| 3 | `persona-d2s-what-to-borrow` | 不用訓練就能抄的兩招，各有什麼代價？ | 已發布 | 已發布 | [README](persona-d2s-what-to-borrow/README.md) |

## SAG：不先建圖，查詢時才連（`sag`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `sag-latent-hyperedge-one-hop`＋`multihop-vector-vs-graphrag-pain-points` | Multi-Hop 推理，一定要先建知識圖譜嗎？ | 已發布 | 已發布 | [README](sag-latent-hyperedge-one-hop/README.md) |
| 2 | `sag-sql-vector-llm-division-and-funnel` | SQL、向量、LLM 怎麼分工？ | 已發布 | 已發布 | [README](sag-sql-vector-llm-division-and-funnel/README.md) |
| 3 | `sag-results-and-gain-source` | SAG 的成績從哪來？ | 已發布 | 已發布 | [README](sag-results-and-gain-source/README.md) |
| 4 | `sag-tradeoffs-price-paid` | SAG 付出了什麼代價？ | 已發布 | 已發布 | [README](sag-tradeoffs-price-paid/README.md) |

## SkillOpt: 自動優化你的 Agent Skill（`skillopt`）

| 發文順序 | 觀念 | 標題（planned_title） | IG | Threads | 打開 |
|---|---|---|---|---|---|
| 1 | `skillopt-overview` | Skill 怎麼調才有效？讓 AI 照紀律自己調 | 已發布 | 已發布 | [README](skillopt-overview/README.md) |
| 2 | `skillopt-batch-evidence-minibatch`＋`skillopt-bounded-edit-budget` | 該改哪裡、改多少？別被一次失敗牽著走 | 已發布 | 已發布 | [README](skillopt-batch-evidence-minibatch/README.md) |
| 3 | `skillopt-blind-acceptance-gate`＋`skillopt-epoch-level-control` | 改完真的有變好嗎？拿沒看過的題目測試它 | 已發布 | 已發布 | [README](skillopt-blind-acceptance-gate/README.md) |

## 獨立貼文（沒有系列）

| 觀念 | IG | Threads | 打開 |
|---|---|---|---|
| `bradley-terry-pairwise-preference` | 已發布 | 已發布 | [README](standalone/bradley-terry-pairwise-preference/README.md) |
| `decision-transformer-reward-conditioning` | 已發布 | 已發布 | [README](standalone/decision-transformer-reward-conditioning/README.md) |

