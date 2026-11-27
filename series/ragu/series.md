---
id: ragu
name: "GraphRAG 值不值得做"   # 2026-11-23 重做（人：看不懂、不想看）；舊名「拆解 RAGU：GraphRAG 的天花板有多高」
philosophy: series/ragu/philosophy.md   # 低天花板
color: ceiling   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window、hourglass、band、junction、echo、chips）
style: ceiling
members:
  - concept: ragu-results-peeling-confounds
    planned_title: 換一句提示詞 +16.9%，加一整張知識圖 +1.2%
    summary: 同一份考題：答短 +16.9%，加圖只 +1.2%
  - concept: retrieval-recall-not-answer-quality
    planned_title: 資料撈得越多，AI 答得越好？
    summary: 給 AI 的資料不是越多越好，混進雜訊可能讓它挑錯
  - concept: ragu-pipeline-two-stage-extraction-consolidation
    planned_title: AI 會把同一個東西寫成兩個名字
    summary: 先給 AI 一份名單、讓它從裡面挑，名字就對得上
  - concept: small-extractor-saturation-not-scale
    planned_title: 小模型夠用，是因為題目太簡單
    summary: 簡單的事小模型夠用，要推理才看模型大小
hashtag: RAGU
members_locked: true   # 2026-11-27 鎖定：人說 RAGU 四則都可以定案（依序 7／9／8／8 張，hook 與系列名接受）；第 1 則發布後，成員與 planned_title 都不能再動
status: planning
---

# RAGU

來源文章：`ragu`（6 張卡；系列只用 4 張）。
文章標題：RAGU：一篇替 GraphRAG 量出天花板的論文
網址：https://datasciocean.com/paper-intro/ragu/

## 規劃備忘

- **2026-11-23 全部重做（人 review 後）**：人說封面上下顛倒、第 1 則第 2 張看不懂、四則都「不是很懂、不知道要表達什麼、看不下去」，要站在滑 Threads／IG 的一般人角度重做。舊的 6 個發布包已刪（spec 備份不進 repo；舊版在 git 歷史 e1db3ee）。
- 重做原則（Claude 依規則 12 決定）：
  1. **每則只講一件事，封面就是那件事**，第 2 張馬上回答，不鋪陳。系列名改成讀者會關心的問題「GraphRAG 值不值得做」，RAGU 只是例子，不是主角。
  2. **砍掉讀者記不住的名字**：題庫名、HippoRAG 2、NaiveRAG、AC、pp 盡量不上主標；需要時寫「同一套程式、不用圖的版本」。第 1 則不比 HippoRAG 2，「越難越強」的 cross-over 整段拿掉（要三層解釋才懂）。
  3. **每張一個數字、一個畫面**；主標是完整的白話句子。8 張左右（A4）。
  4. 每則結尾都是可以帶走的做法（A1：系統怎麼搭）：第 1 則「看到分數變好先查無聊的原因」、第 2 則「別只看撈回率」、第 3 則「先定名單再讓 AI 選」、第 4 則「小模型放在搬資料的地方，不要放在要推理的地方」。
  5. 順序：先給最有反差、最好懂的（提示詞 vs 知識圖），再講多撈的副作用，最後兩則是帶得走的做法。`entity-resolution-not-clustering`、`graph-vs-vector-clustering-modularity` 仍不在系列內。
- 封面改成字在上、圖在下（`render.py` `cl_cover`、`tests/test_ceiling_style.py`）。
- 用語：差距寫 %（卡上是 pp）；答對率＝另一個 AI 當裁判的單次評分（限定條件）；實體＝圖上的點（人、組織、產品）；關係＝點之間的線。
- 不能用（`pending_author_confirmation`）：`retrieval-recall-not-answer-quality` 的 c6（Evidence Recall 四格數字）。

## 舊規劃備忘（2026-11-19～21，已被 2026-11-23 重做取代，留著當教訓）

- 教訓：每則各自通過讀者審查，不代表一般人想看；舊版塞了太多名字與層次（三層混淆、cross-over、六步驟）。
