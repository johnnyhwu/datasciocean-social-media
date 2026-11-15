---
id: prompt-repetition
name: "拆解 Prompt Repetition：提示詞為什麼要貼兩次"   # 2026-11-11 Claude 決定（規則 12）；2026-11-15 人 review 成品後接受
philosophy: series/prompt-repetition/philosophy.md   # 複寫
color: echo   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window、hourglass、band、junction）
style: echo
members:
  - concept: prompt-repetition-causal-bottleneck-and-fix
    planned_title: 把提示詞貼兩次，第二遍就看得到全文
    summary: 主流 LLM 大多在讀到前面的字時，還不知道後文；貼兩次之後，第二遍的每個字都看得到整個第一遍。
  - concept: prompt-repetition-free-lunch-latency
    planned_title: 輸入變兩倍長，為什麼幾乎沒變慢？
    summary: 多出來的輸入落在可以平行算的讀題階段；主要花時間的是一個字一個字寫答案，而答案長度沒變。
  - concept: prompt-repetition-results-and-boundary
    planned_title: 70 組裡 47 勝 0 敗，叫 AI 先推理就變中性
    summary: 和只貼一次比，70 個組合裡 47 勝 0 敗；但要模型先一步步推理時，效果變成中性到小幅正面。
hashtag: PromptRepetition
status: locked
members_locked: true
---

# Prompt Repetition

來源文章：`prompt-repetition`（3 張卡）。
文章標題：Google 2025 論文解讀：只要「複製貼上」就能變強？Prompt Repetition 如何成為 LLM 的免費午餐
網址：https://datasciocean.com/paper-intro/prompt-repetition/

## 規劃備忘（2026-11-11，Claude 依規則 12 決定）

- 3 張卡各做 1 則，不合併：第 1 則「為什麼有效」（因果注意力的瓶頸、貼兩次怎麼補），第 2 則「為什麼不變慢」（Prefill／Decode），第 3 則「效果多好、什麼時候不靈」（47 勝 0 敗、CoT 後變中性、NameIndex）。
  - 合併檢查（`series_deps.py` 只有三張卡共用的 c2 背景主張）：第 2、3 則各自要的術語（Prefill、Decode；Baseline、CoT、McNemar）都在自己卡上，只需要「Prompt Repetition 是什麼」靠回顧頁接上；三張卡主張數 15／13／14，合併會超過 20 張。
  - 順序：被依賴的先發。第 2、3 則都要先知道「第二遍看得到第一遍」；第 2 則先回答讀者最直覺的疑慮（輸入兩倍會不會變慢），第 3 則再給成績與邊界。
- 卡上全部主張都是 `normal`，沒有 `pending_author_confirmation`。
- 用語：Prefill＝讀題階段、Decode＝寫答案階段（第 2 則起）；Token＝字（第一次出現放括號）；Baseline＝原本只貼一次；CoT＝要模型先一步步推理（"Think step by step"）。
- 2026-11-15 人 review 三則成品後接受系列名、三則標題與 hook，`members_locked: true`。
- 新系列的草圖與樣張省略（前例：UniversalRAG，人 2026-11-09 說只 review 成品；`CLAUDE.md` 規則 12）；風格回歸測試 `tests/test_echo_style.py`。
