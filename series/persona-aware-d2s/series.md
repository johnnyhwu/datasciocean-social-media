---
id: persona-aware-d2s
name: "Persona-Aware-D2S: 同一份文件，怎麼長出不同簡報"
philosophy: series/persona-aware-d2s/philosophy.md
color: paper-cards         # 2026-10-14 人選定：米色紙面＋深海直欄（H2 直切），金色只給一張卡
style: cards               # 一式四份；render.py 的 cards 分支
members:
  - concept: persona-d2s-task-and-pipeline
    planned_title: 同一份文件，怎麼長出四種簡報？
  - concept: persona-d2s-training-design-flaws
    planned_title: 80 筆資料訓出來的模型，能信嗎？
  - concept: persona-d2s-what-to-borrow
    planned_title: 不用訓練就能抄的兩招，各有什麼代價？
hashtag: DSO_PersonaD2S    # 2026-10-14 人定案
members_locked: true   # 2026-10-14 鎖定：三則 spec 都做完、張數定案（16／14／13 張）；第 1 則發布後，成員與 planned_title 都不能再動
status: planning
---

# Persona-Aware-D2S: 同一份文件，怎麼長出不同簡報

來源文章：`persona-aware-d2s`（5 張卡）。本系列用其中 3 張（`bound_to_source`、`bound_to_source`、`evidence_from_single_source`），一卡一則，共 3 則。

另外兩張 `decision-transformer-reward-conditioning`、`bradley-terry-pairwise-preference` 是 `standalone_classic`，不進系列，之後獨立發文（2026-10-14 人決定）。

發文順序（2026-10-14 人決定）：概覽 → 訓練設計站不住腳 → 值得借鑑。2、3 不合併（兩者不互相依賴，合併要砍機制說明，限定條件綁主張會塞不下）。

系列名與三個 `planned_title` 由人定案（2026-10-14）；系列名會印在每張圖上，發布後不能改。

**已定案（2026-10-14 人決定）**：視覺哲學「一式四份」，構圖選「直切」（右邊一條深海直欄，四張投影片錯開橫跨交界；封面左下一份文件接到投影片；圖表類版型用右緣索引欄）。曾被退回的：分光、藍綠底與座標、D3（米色底加下方一排卡，和前兩個系列構圖太像、IG 主頁會混淆）。hashtag `DSO_PersonaD2S` 已定案（2026-10-14）。

**定位語（人決定 A+C）**：第 1 則要讓讀者知道這個系列在看 2024 年 EACL 的早期簡報生成怎麼做。A：只寫卡上的事實（EACL 2024、微調 GPT-3.5-turbo）。C：再加一行人口吻的定位語（例：「這個系列是在了解早期的簡報生成怎麼做」）。**這一行不在卡上，是人授權的例外**（規則 1）；審查時要明確告訴忠實者這是放行項，其餘仍要有卡上原文。「過時」之類更強的判斷人沒有授權，不寫。

**已鎖定**（2026-10-14）：三則 spec 都做完、張數與標題定案。
