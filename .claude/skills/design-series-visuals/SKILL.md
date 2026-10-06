---
name: design-series-visuals
description: 設計 IG 輪播與 Threads 附圖的視覺：新系列的視覺哲學、版型模板、品牌常數、選圖規則。使用者要「開新系列」「設計模板」「改版型」「新增圖表類型」「調整配色或字級」「產生版型樣張」時使用。日常把觀念做成貼文用 make-social-post，不用這個。
---

# design-series-visuals：系列視覺哲學與模板

日常做貼文時模板已經存在，直接用 `make-social-post`。只有下列情況才用這個 skill：

- 開一個**新系列**（需要新的視覺哲學、系列色、模板與樣張）
- 新增或改**版型／圖表類型**（例如折線圖、流程圖，目前只有橫條圖、測深圖、對照表、純文字版型）
- 調整品牌常數、字級、對比度規則

## 設計之前必讀

1. `references/principles.md`：IG 圖片設計原則（先哲學後畫面、暗藏主題參照、文字是視覺元素、工藝感、不重疊不出框、最後一步只減不加、多張是同一哲學的變奏）。
2. `references/brand-and-layouts.md`：畫布與邊界、品牌色與字型字級、對比度、八種版型、依內容選圖、測深圖。
3. `references/series-philosophy-and-templates.md`：兩層視覺哲學、模板怎麼來、做新系列的步驟。
4. 想看範例：現行的 `series/jev-cascade/`（`philosophy.md`「潮線」、`templates/`、`series.md`），以及 `out/jev-cascade/jev-cascade-overview/` 的成品。
5. 需要原始設計哲學時再讀 `references/canvas-design-original.md`（上游 skill 原文；授權見 `references/canvas-design-LICENSE.txt`）。

## 鐵則

- **圖片由程式產生**（HTML 模板加 Playwright 截圖）；LLM 只產出內容規格 JSON。數據圖與文字圖**不用 AI 生圖**（文字常出錯、數字可能畫錯）。
- 同一系列用同一份視覺哲學與同一套模板；改模板會改 template hash，整個系列要重渲，所以不要為單一貼文改模板。
- 精確優先於藝術：長度、刻度、間距由程式依數值計算，不由 LLM 決定。
- **新系列或新版型要先產生樣張，由人審過才量產。** 檢查全過不代表好看。
- 字型內嵌（Noto Sans CJK TC，`assets/fonts/`），不依賴系統字型；字重只用 400 與 700；字級只用 {28, 34, 38, 40, 56, 72, 76}。
- 金色只給一個元素，且**禁止用於米色底上的文字**（對比度 1.7）。

## 做完要驗證什麼

- 程式 B 全過（`make-social-post` 的 `render.py`；檢查項目見它的 `references/program-b.md`）。新增檢查要用「故意做壞的版本」確認抓得到。
- 重渲既有發布包，PNG 的 md5 應與先前相同（除非你有意改版面）。
- 用 `make-social-post/scripts/contact_sheet.py` 拼縮圖給人看。
