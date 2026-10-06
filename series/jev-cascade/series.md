---
id: jev-cascade
name: JEV 串接 Judge 系列
philosophy: series/jev-cascade/philosophy.md
color: teal-mid
members:
  - concept: jev-cascade-overview
    planned_title: 便宜的 Judge 先判，沒把握才轉給 GPT-6
  - concept: judge-readable-vs-derive
    planned_title: Judge 能不能用，先問答案能不能讀出來或核對
  - concept: confidence-three-metrics
    planned_title: 信心要分三件事看：判決、排序、機率
  - concept: cascade-complementary-errors
    planned_title: 串接的價值，來自兩個 Judge 錯在不同的題
  - concept: cascade-threshold-and-failure-mode
    planned_title: 門檻要隨 Judge 與任務重選
hashtag: DSO_LLMJudge
status: planning
---

# JEV 串接 Judge 系列

來源文章：`jev-as-a-judge`（5 張卡，皆 `bound_to_source` 或 `evidence_from_single_source`，預設組成系列）。

發文順序依 `.claude/skills/make-social-post/references/batch-and-publish.md`：概覽先發；其後被依賴的先發
（Judge 能不能用 → 信心怎麼量 → 串接為何成立 → 門檻怎麼選）。

`planned_title` 是系列規劃草案，待人確認。
