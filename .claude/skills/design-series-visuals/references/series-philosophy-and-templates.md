# 新系列：視覺哲學與模板

## 兩層視覺哲學

| 層 | 內容 | 由誰寫 |
|---|---|---|
| 品牌哲學（固定） | 海、鉛錘、四個品牌色（`brand-and-layouts.md` §2） | 不隨系列變動 |
| 系列哲學（每系列一份） | 在品牌語言之內，**暗藏該系列主題的參照**。例：Jev 系列的主題是「數字要知道分母才有意義」，對應「測深」 | 系列規劃時由 Claude 產生，**由人審一次**，之後固定 |

- 系列哲學存成 `design/series-philosophies/<series-id>.md`。範例：`jev-sounding.md`（「測深」），在 git 歷史 commit `4b5a42e`。系列檔 `series/<id>.md` 的 `philosophy` 欄指向它。
- 哲學的格式：運動名稱（1～2 個詞）加 4～6 段，依序談空間與形式、色彩與材質、尺度與節奏、構圖與層次、工藝。每個面向只講一次。**哲學只談形式，不談主題本身。**
- **同一系列的所有貼文、所有投影片，共用同一份哲學與同一套模板。** 每張可以不同，但是同一種語言（像一本書的頁面）。
- 做完後的最後一步只減不加：問「怎麼讓現有的更像一件作品」，不問「還能加什麼」。

## 模板

**模板由哲學導出一次，存進 repo**（`templates/<series-id>/`：`style.css` 加每種版型一個 `.html`），之後每則貼文只填內容 JSON，不重新設計。風格調整只改哲學檔與模板，不用重新生成內容。

第一次實跑的 `templates/jev-teardown/`（git 歷史 commit `4b5a42e`）有：`cover.html`、`context.html`、`text.html`、`table.html`、`chart_bars.html`、`chart_sounding.html`、`takeaway.html`、`series_map.html`、`style.css`。模板用 `{{PLACEHOLDER}}` 接 `render.py` 填入的內容；`render.py` 的 `build()` 負責各版型的幾何（海浪、測深圖的水面與刻度、表格列高）。

**模板版本 hash**：`render.py` 對 `templates/<series-id>/` 全部檔案算 hash，寫進 `checks-b.json`；同一系列所有貼文必須是同一個 hash。**改模板就會改 hash，等於整個系列要重渲**，所以模板定案後不要為單一貼文改它。

## 做一個新系列的步驟

1. 讀 `principles.md`（IG 設計原則）與 `brand-and-layouts.md`；想看範例讀 git 歷史 commit `4b5a42e` 的 `design/series-philosophies/jev-sounding.md` 與 `templates/jev-teardown/`；需要原始設計哲學時讀 `canvas-design-original.md`（Anthropic canvas-design skill，授權見 `canvas-design-LICENSE.txt`）。
2. 寫系列哲學：從系列主題推出一個暗藏的參照，只談形式。存 `design/series-philosophies/<id>.md`。
3. 選系列色（四層海浪深淺，相鄰系列不同色）。**目前 `render.py` 的 `SERIES_COLORS` 只有 `teal-mid`，新色要在那裡加。**
4. 從哲學導出六種以上版型的模板，放 `templates/<id>/`。可以從 commit `4b5a42e` 的 `templates/jev-teardown/` 取出複製後改外觀，但幾何與檢查改動要同步改 `render.py` 與程式 B，並確認：不重疊、對比度、換行不拆詞。
5. 建 `series/<id>.md`（成員、`planned_title`、hashtag、色）。
6. 產生**所有版型的樣張**（用一則真實或假想的 spec 渲染，過程式 B），拼成縮圖（`contact_sheet.py`）給人看，**人審過才開始量產**。人看過才算數：檢查全過不代表好看。
7. 樣張通過後，才用 `make-social-post` 量產貼文。

## 第一次實跑的經驗

- 圖表版型之外的版型（封面、脈絡、文字、帶走、系列地圖）是實作時才第一次做樣張；人看過樣張後說「可以，就用這套」，直接採用。
- 渲染引擎中途改過幾次：文字框重疊判定要含線寬、裝飾圖形不算圖表元素（class `deco`）、keep-all 對中文的斷行會讓長串超出版心、對照表列高要模擬斷行估算。這些都已寫進 `render.py` 與程式 B。
