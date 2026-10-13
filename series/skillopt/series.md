---
id: skillopt
name: "SkillOpt: 自動優化你的 Agent Skill"
philosophy: series/skillopt/philosophy.md
color: abyss-contour
style: contour
members:
  - concept: skillopt-overview
    planned_title: Skill 怎麼調才有效？讓 AI 照紀律自己調
  - concept: skillopt-batch-evidence-minibatch
    also: [skillopt-bounded-edit-budget]   # 2026-10-11 人決定：兩張卡合成一則（修改怎麼提：先收一批證據、再限量套用）
    planned_title: 該改哪裡、改多少？別被一次失敗牽著走
  - concept: skillopt-blind-acceptance-gate
    also: [skillopt-epoch-level-control]   # 2026-10-11 人決定：兩張卡合成一則（修改怎麼收：步驟級盲測守門 ＋ epoch 級 A/B）
    planned_title: 改完真的有變好嗎？拿沒看過的題目測試它
hashtag: DSO_SkillOpt
members_locked: true   # 2026-10-12 鎖定：三則的 spec 都做完、張數定案（19／17／17 張）、人同意發第 1 則；第 1 則發布後，成員與 planned_title 都不能再動
status: planning
---

# SkillOpt: 自動優化你的 Agent Skill

來源文章：`skillopt`（5 張卡：1 張 `bound_to_source` 概覽、4 張 `evidence_from_single_source`），組成系列，3 則 post。

發文順序：概覽先發；其後依一步訓練的流程：修改怎麼提出來（minibatch ＋ 編輯預算）→ 修改怎麼被檢查（盲測守門 ＋ epoch 級控制）。

**鎖定前的待辦（2026-10-11 人決定）**：三則的 spec 都做完（check_a、render、看過第 3 則砍了什麼）、決定好 IG 張數上限，才加 `members_locked: true` 並發第 1 則。這是為了避免 jev-cascade 的錯誤：第 1 則發布後系列規劃還在變，已發布的系列地圖過時。

`planned_title` 與系列名是草案，待人確認；系列名會印在每一張圖上，發布後不能改。
