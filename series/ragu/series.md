---
id: ragu
name: "拆解 RAGU：GraphRAG 的天花板有多高"   # 2026-11-19 Claude 決定（規則 12）
philosophy: series/ragu/philosophy.md   # 低天花板
color: ceiling   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window、hourglass、band、junction、echo、chips）
style: ceiling
members:
  - concept: ragu-pipeline-two-stage-extraction-consolidation
    planned_title: 先定好名單再讓 AI 選，圖就少了斷線
    summary: 抽取拆兩趟是能帶走的招式；圖畫錯了，答案仍可能是對的
  - concept: ragu-results-peeling-confounds
    planned_title: 剝掉混淆後，用圖只多答對 1.2 到 4.3%
    summary: 扣掉答案格式，RAGU 對 HippoRAG 2 平手或落後
  - concept: retrieval-recall-not-answer-quality
    planned_title: 證據撈得更完整，答案不一定更好
    summary: Evidence Recall 不看撈進多少雜訊，多撈可能是干擾
  - concept: small-extractor-saturation-not-scale
    planned_title: 小模型夠用，是因為任務簡單
    summary: 抽取落在大模型也加不了分的區；7B 的優勢接到問答就消失
hashtag: RAGU
status: planning
---

# RAGU

來源文章：`ragu`（6 張卡；系列只用 4 張）。
文章標題：RAGU：一篇替 GraphRAG 量出天花板的論文
網址：https://datasciocean.com/paper-intro/ragu/

## 規劃備忘

- **2026-11-21 人決定砍成 4 則**：系列層測試讀者（一般讀者、照順序讀完六則，`out/ragu/_series-reader-test.json`）封面點擊意願 4/4/2/1/2/3，第 3～5 則像建圖教學、和第 1 則「圖只多 1.2 到 4.3%」接不上，讀者會在第 3、4 則流失。保留 1 → 2 → 精簡的 3 → 6；第 3 則只留「先給名單再讓它選」與「圖畫錯了答案卻是對的」（拿掉路線圖、型別表、六步驟、先合併再建圖）；第 1 則併掉重複的「比較不會退步」那張。`entity-resolution-not-clustering`、`graph-vs-vector-clustering-modularity` 移出系列、不發，發布包留在 `out/ragu/`、state 維持未做，之後可能改成獨立貼文（第 5 則要先淡化 RAGU、拿掉公式）。
- **2026-11-21 順序改成 建圖招式 → 剝混淆 → 撈得多 → 小模型**（測試讀者：先知道知識圖怎麼畫，再看它幫多少）；每則仍有前情提要（程式 A 規則），第 2～4 則拿掉結尾的系列地圖（和前情提要重複）；第 4 則併掉「起點幾乎是 0」與路線圖，15 → 12 張；第 2 則第 2 張改白話。第三次系列讀者測試（新順序）封面 2/3/4/2，三次測試給的建議彼此不一致，單一 LLM 讀者雜訊大，不再據此大改，交人判斷。
- 教訓：做系列時，每則各自通過讀者審查不代表系列讀起來好；系列做完要派一個讀者照順序讀完全部（見 batch-and-publish.md）。

## 規劃備忘（2026-11-19，Claude 依規則 12 決定）

- 6 張卡各做 1 則，不合併。發文順序照「讀者先問的先答」：先給結論（第 1 則：剝掉混淆後圖只多一點點），接著回答第 1 則留下的疑問（第 2 則：證據撈得多、答案為什麼沒變好），再照 RAGU 流程的順序拆三個步驟（第 3 則 Step 2 抽取、第 4 則 Step 3 去重、第 5 則 Step 5 社群偵測），最後是抽取模型該用多大（第 6 則）。
  - 合併檢查：
    - 第 1、2 則都講到 cross-over。第 1 則講「是誰在動」（HippoRAG 2 往下掉），第 2 則講「為什麼」（RAGU 一路多撈，在合成類題目才變成優勢），角度不同；第 2 則只用一張帶過 cross-over，前面靠回顧頁接上。兩張卡可用主張 18／15，合併會超過 20 張。
    - 第 3、4 則都講到 Step 3（提及、DBSCAN、Alistair 父子被合併）。第 3 則只講 Step 2 的兩階段抽取，Step 3 只交代「這是唯一新的一步、沒有對照實驗」，提及與 DBSCAN 的細節全部留給第 4 則，兩則就不重複。
    - 第 5 則（Leiden 與模組度）只需要「GraphRAG 會建圖」這個背景，自己的卡就有，不必合併。
  - 第 1 則同時是系列概覽：交代 GraphRAG 是什麼、RAGU 主張什麼。
- 不能用（`pending_author_confirmation`）：`retrieval-recall-not-answer-quality` 的 c6（Evidence Recall 四格都高過對手）。第 2 則的「RAGU 撈得比較完整」只能靠 c5（Coverage）與 c8（假設的例子）撐，不寫四格 ER 的數字。
- 用語：準確度差距寫 %（卡上是 pp）；AC 寫「答案正確率（AC）」；Evidence Recall 寫英文；NaiveRAG＝同一套程式、不用圖的版本；實體＝圖上的點（人、組織、產品）；關係＝點之間的線。
- 新系列的草圖與樣張省略（`CLAUDE.md` 規則 12）；風格回歸測試 `tests/test_ceiling_style.py`。
