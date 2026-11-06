---
id: llm-as-a-verifier
name: "拆解 LLM-as-a-Verifier：AI 怎麼替 AI 打分數"   # 人 2026-11-03 挑定（候選甲）；會印在每張圖上，發布後不能改
philosophy: series/llm-as-a-verifier/philosophy.md   # 濃淡帶；人 2026-11-03 從三個草圖選 V3
color: band   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window、hourglass）
style: band   # 2026-11-03 人選 V3「濃淡帶」
members:   # 人 2026-11-03 決定方案 B：3 則（第 1 則雙卡）；第 1 則 planned_title 人已挑定
  - concept: verifier-expected-value-vs-argmax
    also: [verifier-three-knobs-g-k-c]
    planned_title: 叫 AI 打 1 到 5 分，為什麼一堆平手？   # 人 2026-11-03 從 hook 候選挑定 A
    summary: 只取最高分丟掉了機率；改算期望值，平手就拆開，代價是每次都得表態。另有三個能調的旋鈕。   # 2026-11-04 初稿，送忠實者與讀者審
  - concept: ppt-pivot-tournament
    also: [verifier-three-knobs-g-k-c]   # 2026-11-05：第 5 張「每對 24 次＝3 個標準×各問 8 次」引用 knobs c3（人回饋要解釋 24 次）
    planned_title: 從 20 個答案挑最好的，AI 評審不必兩兩都比   # 人 2026-11-05 從 hook 候選挑定 A；「全」→「都」是程式 A 擋比較詞（卡上沒有「全」），待告知人
    summary: 先繞一圈粗排、挑出前幾名當基準，其他候選只跟它們比；20 條時少比約 45%，候選只有幾條時省不了多少。   # 2026-11-05 初稿，送審
  - concept: verifier-results-how-to-read
    planned_title: 論文說 LLM-as-a-Verifier 表現最好，功勞真的是它的嗎？   # 人 2026-11-06 挑 A 後改寫主標
    summary: 拆開論文的成績：哪些進步混了別的差異、哪些才算得到方法頭上，還有預警說法的問題。   # 2026-11-06 人回饋後改寫，審查通過
members_locked: true   # 2026-11-06 三則 spec 審查完成
hashtag: LLMVerifier   # 人 2026-11-03 同意（不加 DSO_ 前綴）
status: planning
---

# LLM-as-a-Verifier

來源文章：`llm-as-a-verifier`（4 張卡）。
文章標題：LLM 打分數老是平手？LLM-as-a-Verifier 改讀機率分佈
網址：https://datasciocean.com/paper-intro/llm-as-a-verifier/

## 規劃備忘（2026-11-03）

- 4 張卡，主張數 20／19／19／18；pending 只有 `ppt-pivot-tournament` c16（k=9 逼近循環賽、省 27%）不能用，c15 的原始數字可用。
- 附參考圖的主張很多（expected c17–18、knobs c5/c8/c11/c12/c16、ppt c6/c15–17、results c4–6/c8/c10/c11/c15/c18），做每則時要用 Read 看圖。
- `series_deps.py` 照例沒有鑑別力（都是 token、verifier、prompt 這類基礎詞）。用讀者角度看的術語依賴：
  - 三個調整項 G／K／C 要先懂「期望值取代 argmax」→ 第 2 則的 recap 與自己卡上的 c2 就能交代。
  - G 在兩張卡都出現（expected c17–18 的 1–5 → 1–20；knobs c5 的 G 曲線），K 的「靠平均打破平手」延續第 1 則的平手主線。
  - PPT 卡自己 c2 交代成對比較與 Bradley–Terry；c3 的「每對 C×K=24 次」需要 C、K，可只寫「24 次 LLM 呼叫」或靠 recap。
  - 實驗卡 c2／c3 自帶 PPT 與 G=20、K=8、C=3 的交代，放最後最好讀。
- 方案（人 2026-11-03 選 B）：
  - A（建議）4 則、一卡一則：期望值 → G/K/C → PPT → 實驗怎麼讀。每則約 13–16 張。
  - B 3 則：期望值＋G/K/C 合併（G 不用講兩次、平手主線一路講完）→ PPT → 實驗。第 1 則會有 39 條主張，估 20 張以上。
  - C 3 則：期望值 → G/K/C＋PPT → 實驗。兩張卡沒有依賴，硬合，估 20 張以上。

## 視覺草圖（2026-11-03，人選 V3 濃淡帶）

`series/llm-as-a-verifier/sketches/`：V1 重心、V2 刻度、V3 濃淡帶，各有封面 1–3、內頁、IG 首頁 3×3（上排本系列三則，下面是 Cerebras、Claude Code、SAG 的封面）、`總覽-三個方向.png`。封面標題是暫用，hook 之後由人挑。

## 濃淡帶模板與樣張（2026-11-03，待人審）

- 哲學 `philosophy.md`；模板 `templates/`（由 cerebras-rag 複製，封面改成系列名在上、無底部色帶）；`render.py` 新增 `style: band`（`bd_*`：封面中段全寬濃淡帶＋1～5 刻度＋金針在期望值；內頁頂端細帶、針＝讀到第幾張；文字張下半一條中帶；帶走張深色底濃淡反轉）。每則一種示意分佈 `BD_DISTS`（第 1 則最濃在右、第 2 則偏左、第 3 則兩頭）。
- 樣張：`sketches/sample/`（8 種版型，`_build/contact-sheet.png`）、`sketches/樣張-濃淡帶-封面1～3.png`、`樣張-濃淡帶-IG首頁3x3.png`。
- 人審過才寫 `tests/test_band_style.py` 並量產。
