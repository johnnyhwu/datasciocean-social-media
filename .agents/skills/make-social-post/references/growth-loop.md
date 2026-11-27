# 流量追蹤與改進迴圈（人 2026-11-21）

目標是讓讀者與追蹤人數長期變多。**Claude 自己維護這個迴圈，不等人提醒**：每發布一則就量一次、想一次；每做一則新的就從行動清單挑改變。狀態在 `growth/`（先讀 `growth/README.md` 的規則）。

```
發布 → [1 量] insights.py pull → [2 想] 判讀＋insight → 更新 growth/plan.md
                                                         ↓
下一則 ← [3 改] 從 plan.md 挑 1～2 個 action ← ─────────────┘
       → [4 記] experiments.md 套用紀錄 → 發布 → 回到 [1]
```

## 1. 量（每次兩個平台都發布成功之後，`publish-flow.md` 第 9.5 步）

`uv run python .agents/skills/make-social-post/scripts/insights.py pull`

寫出 `growth/snapshots/<今天>.json` 並印表（每則的 IG 與 Threads 指標、發布天數、套用的 action；帳號追蹤數）。同一天發兩次就覆寫當天的快照。抓不到（token 過期、網路）就說一聲、跳過，不擋發布。

## 2. 想（同一次，接著做；約 10 分鐘）

1. 和上一份快照比：追蹤數變化（IG、Threads）、這期間發了哪幾則。
2. 每個 `trying` 的 action：套用了幾則？表現和基準（`plan.md` 上方，對齊貼文年齡）比起來如何？照 `growth/README.md` 規則 4 判斷，未滿 3 則只寫方向。
3. 有沒有新的現象（某則特別高或特別低）？寫成假設，不要直接當結論。
4. 寫進 `growth/experiments.md` 的「判讀紀錄」一行；有新假設就加進 `plan.md` 成新的 action（`todo`）；判定有效的改 `kept` 並把做法寫進對應的 reference（例如 `ig-carousel.md`、`hooks.md`），無效的改 `dropped` 寫原因。
5. 發現值得寫成一份報告的大變化（例如追蹤數一週多 10%、或某個 action 判定），寫 `growth/reports/<日期>-<主題>.md`。平常只寫判讀紀錄一行就好。
6. 回報給人：發布結果之後附 2～4 行「流量追蹤」：追蹤數變化、最值得注意的一則、下一則打算試什麼。

## 3. 改（開始做新的一則時，在寫 spec 之前）

1. 讀 `growth/plan.md`，挑 1～2 個 action：`trying` 但還不滿 3 則的優先（才判讀得了），其次證據最強、成本最低的 `todo`。`decide` 的不挑（要人決定）。
2. 不能為了 action 違反 `AGENTS.md` 規則：卡仍是內容上限，hook 仍不欺騙，改了的文字照常審查。
3. 把挑的 action 寫進這則的 `_build/progress.md`（為什麼挑、怎麼做）。

## 4. 記

在 `growth/experiments.md` 的「套用紀錄」加一行：`| 觀念 id | 發布日 | A1, A3 | 做了什麼 |`（發布日在發布後補上）。`insights.py` 靠這一欄把 action 帶進快照。交成品給人時，順便說這則套用了哪些 action。

## 注意

- 樣本很小，每天只多一則：單則爆紅或爆冷都不改方向，要看連續 3 則以上。
- 改變要能歸因：同一段期間不要一次改太多 action。
- 改模板（例如 A3 的追蹤邀請）是全系列的改變：已發布的貼文不重渲；同一系列還沒發的貼文要一起改（模板 hash 要一致），回歸測試照常跑。
- 只讀 API：`insights.py` 不發文、不改任何東西。
