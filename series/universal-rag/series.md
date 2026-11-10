---
id: universal-rag
name: "拆解 UniversalRAG：先問這題該去哪裡查"   # 2026-11-09 Claude 依人授權決定；人 2026-11-10 review 成品後接受
philosophy: series/universal-rag/philosophy.md   # 分岔軌道
color: junction   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window、hourglass、band）
style: junction
members:
  - concept: universalrag-routing-over-unified-embedding
    planned_title: 答案明明在圖片裡，AI 搜尋卻先去翻文字
    summary: 全混在一起比對會偏向抓文字；UniversalRAG 把資料分櫃放，查之前先用 Router 判斷去哪個櫃子。
  - concept: universalrag-router-design-and-rollout
    planned_title: AI 怎麼決定這題去哪裡查？
    summary: Router 一次能選好幾個櫃子，連「不用查」也算一個選項；企業可先用免訓練版起步，之後再訓練自己的。
hashtag: UniversalRAG
status: locked
members_locked: true
---

# UniversalRAG

來源文章：`universal-rag`（2 張卡）。
文章標題：UniversalRAG 深度解析：破解多模態 RAG 偏見，提升異質數據的檢索能力
網址：https://datasciocean.com/paper-intro/universal-rag/

## 規劃備忘（2026-11-09，人授權 Claude 自行判斷）

- 2 張卡各做 1 則：第 1 則「為什麼要路由、路由怎麼解決」，第 2 則「Router 怎麼設計、企業怎麼落地」。兩張卡各自可讀，第 2 則靠 recap 接上。
- 不能用的主張（`pending_author_confirmation`）：路由卡 c10、c12、c14；Router 卡 c12。c12 的「1/k」不能拿來解釋延遲為什麼低。
- 第 2 張起採用新骨架（`ig-carousel.md`：第 2 張是「為什麼在乎」）。
- 2026-11-10 人 review 兩則成品後接受系列名、兩則標題與 hook，`members_locked: true`。
- **新系列的草圖與樣張省略**（人 2026-11-09 說只 review 最後完成的第一則）；風格回歸測試 `tests/test_junction_style.py`。
