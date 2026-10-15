# 新系列：視覺哲學與模板

## 兩層視覺哲學

| 層 | 內容 | 由誰寫 |
|---|---|---|
| 品牌哲學（固定） | 海、鉛錘、四個品牌色（`brand-and-layouts.md` §2） | 不隨系列變動 |
| 系列哲學（每系列一份） | 在品牌語言之內，**暗藏該系列主題的參照**。例：Jev 系列的主題是「數字要知道分母才有意義」，對應「測深」 | 系列規劃時由 Claude 產生，**由人審一次**，之後固定 |

- 系列哲學存成 `series/<series-id>/philosophy.md`。範例：`series/jev-cascade/philosophy.md`（「潮線」）。系列檔 `series/<id>.md` 的 `philosophy` 欄指向它。
- 哲學的格式：運動名稱（1～2 個詞）加 4～6 段，依序談空間與形式、色彩與材質、尺度與節奏、構圖與層次、工藝。每個面向只講一次。**哲學只談形式，不談主題本身。**
- **同一系列的所有貼文、所有投影片，共用同一份哲學與同一套模板。** 每張可以不同，但是同一種語言（像一本書的頁面）。
- 做完後的最後一步只減不加：問「怎麼讓現有的更像一件作品」，不問「還能加什麼」。

## 模板

**模板由哲學導出一次，存進 repo**（`series/<series-id>/templates/`：`style.css` 加每種版型一個 `.html`），之後每則貼文只填內容 JSON，不重新設計。風格調整只改哲學檔與模板，不用重新生成內容。

現行範本 `series/jev-cascade/templates/` 有：`cover.html`、`context.html`、`text.html`、`table.html`、`chart_bars.html`（成對橫條圖共用同一個模板，幾何在 `render.py`）、`chart_sounding.html`、`takeaway.html`、`series_map.html`、`style.css`。模板用 `{{PLACEHOLDER}}` 接 `render.py` 填入的內容；`render.py` 的 `build()` 負責各版型的幾何（海浪、測深圖的水面與刻度、表格列高）。

**模板版本 hash**：`render.py` 對 `series/<series-id>/templates/` 全部檔案算 hash，寫進 `checks-b.json`；同一系列所有貼文必須是同一個 hash。**改模板就會改 hash**；已發布的貼文不重渲（網路上的圖已定，`batch_check.py` 也不比對已發布貼文的 hash），所以影響的只有還沒發布的貼文。模板定案後仍不要為單一貼文隨意改它；非改不可（例如 2026-10-10 加成對橫條圖的 `.num2`），要重跑回歸測試，並在報告裡告訴人。

## 做一個新系列的步驟

1. 讀 `principles.md`（IG 設計原則）與 `brand-and-layouts.md`；想看範例讀 `series/jev-cascade/`；需要原始設計哲學時讀 `canvas-design-original.md`（Anthropic canvas-design skill，授權見 `canvas-design-LICENSE.txt`）。
2. 寫系列哲學：從系列主題推出一個暗藏的參照，只談形式。存 `series/<id>/philosophy.md`。
3. 選系列色（四層海浪深淺，相鄰系列不同色）。**`render.py` 的 `SERIES_COLORS` 目前有 `teal-mid`、`abyss-contour`、`paper-cards`，新色要在那裡加。**新的風格（像 `contour`、`cards`）要在 `render.py` 的 `build()` 加對應分支（封面、`text`、`takeaway`、`series_map` 的 SVG 背景；`cards` 的元件是 `slide_card()`、`source_doc()`、`stagger()`、`rail()`），並補回歸測試（`tests/test_cards_style.py` 是範例）。**新系列的外觀要先出草圖給人選**：2026-10-14 persona-aware-d2s 前後試了四個方向人才定案，其中平塗的藍綠或淺藍綠底與品牌的米色紙面加海漸層不搭，人說「顏色怪怪的」；顏色留在米色、深海漸層、金色。**構圖也要和相鄰系列分得開**：人看了第一版樣張說「跟前兩則都很像，IG 主頁會混淆；核心配色一樣，但構圖要更大膽」——前兩個系列的封面骨架（標題靠左、y≈350～500、副標接著、下面一條裝飾）一樣，只換底色與下半裝飾，縮圖就像同一家。要比的是整張封面的骨架，不只配色；提草圖時並排放上相鄰系列的封面比。persona-aware-d2s 最後選了「直切」：右邊一條深海直欄、四張投影片錯開橫跨交界。**草圖選中的是它的動感（錯開、跨界、歪放的文件），第一次照著做時把東西全關進直欄、排得整齊死板，人說「好醜、跟剛剛的感覺不一樣」：把草圖選中的元素逐項列出來照做，不要「整理」成規矩的版本。**窄欄的代價是 `keep-all` 下標題要每約 9 個字、補充每約 13～15 個字就有標點。
4. 從哲學導出所有版型的模板，放 `series/<id>/templates/`。可以複製 `series/jev-cascade/templates/` 後改外觀，但幾何與檢查改動要同步改 `render.py` 與程式 B，並確認：不重疊、對比度、換行不拆詞。
5. 建 `series/<id>/series.md`（成員、`planned_title`、hashtag、色）。
6. 產生**所有版型的樣張**（用一則真實或假想的 spec 渲染，過程式 B），拼成縮圖（`contact_sheet.py`）給人看，**人審過才開始量產**。人看過才算數：檢查全過不代表好看。
7. 樣張通過後，才用 `make-social-post` 量產貼文。

## 設計上的經驗

- 新系列的版型要先出樣張、由人審過才量產（檢查全過不代表好看；單一新的示意圖型不在此限，見 `SKILL.md`）；沿用既有版型幾何、只換哲學、系列名與標籤也要讓人看樣張。
- 渲染引擎中途改過幾次：文字框重疊判定要含線寬、裝飾圖形不算圖表元素（class `deco`）、keep-all 對中文的斷行會讓長串超出版心、對照表列高要模擬斷行估算。這些都已寫進 `render.py` 與程式 B。
