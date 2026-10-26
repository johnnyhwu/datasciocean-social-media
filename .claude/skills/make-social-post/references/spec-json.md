# 內容規格 JSON（`out/<series>/<concept>/_build/spec.json`）

LLM 只產出這份 JSON；外觀完全由模板決定。範例：`out/skillopt/skillopt-batch-evidence-minibatch/_build/spec.json` 與 `skillopt-blind-acceptance-gate`（品質基準：雙卡、17 張、多種示意圖）；`skillopt-overview`（單卡）；`out/standalone/decision-transformer-reward-conditioning/`（獨立貼文）；`cascade-complementary-errors`（成對橫條圖）。`jev-cascade-overview` 的寫法已過時。
**卡上的圖與限定條件**：主張可附 `figures`（blog 的圖，只是參考）；限定條件可有 `source: figure_caption`（範圍取自圖說），`quals` 照樣用 `"c14#1"` 標記帶出。見 `anchor-writing-rules.md`「參考圖」。
`build_package.py` 有投影片欄位白名單：spec 出現不認得的欄位就報錯，避免新欄位漏了輸出。要新增欄位，先在 `build_package.py` 的 `CONTENT_KEYS`／`LAYOUT_KEYS` 加上、讓它輸出到審查文字與 `ig/post.md`，並補測試。

## 頂層

```json
{
  "series": "jev-cascade",            // series/<id>/series.md；獨立 post 沒有系列
  "concept": "confound-three-questions",
  "also_concepts": [],                // 雙卡貼文才填：併入的卡（要與系列檔成員的 also 一致），見下方「雙卡貼文」
  "lang": "zh-TW",
  "status": "draft",
  "hook": { "style": "反直覺斷言", "title": "快 [[193.6 倍、25 倍、約 5 倍]]？", "subtitle": "…",
            "refs": ["c3", "c5"], "candidate": "B4" },
  "slides": [ … ],
  "threads": { … },
  "caption": { … }
}
```

- `[[…]]` 在主標與 hook 標題裡標出要用金色螢光筆畫底的關鍵字；渲染、替代文字與 caption 會自動去掉括號。
- `hook.style` 是 hook 樣態（見 `hooks.md`），寫回狀態時要記錄；`hook.candidate` 是人挑的候選編號。

## 獨立貼文（沒有系列；2026-10-18 起，第一則是 `decision-transformer-reward-conditioning`）

`standalone_classic` 的卡預設獨立發文。spec 頂層寫 `"series": null`，發布包放 `out/standalone/<觀念 id>/`。
- **視覺**：每則獨立貼文各有自己的一套，放 `standalone/<觀念 id>/`（`standalone.md` front matter 的 `style`、`color`；`philosophy.md`；`templates/`；`sketches/`），不共用（人決定，2026-10-18：Bradley-Terry 要獨立重做、不沿用 Decision Transformer 的「地平線」）。`render.py`、`check_a.py`、`batch_check.py` 在 `series` 為 null 時讀這裡。
- **沒有系列標籤**：`caption.hashtags` 不放系列專屬標籤；封面沒有系列色帶；Threads 最後一則沒有「同系列」。
- **最後一張**：可以是帶走張（人決定不連回別則時）；要放「延伸閱讀」就用 `series_map`，寫 `items`（觀念 id 清單，必須是某系列成員且**已發布**，標題由系列檔的 `planned_title` 自動填）、不寫 `current`。
- 導流行（`caption.nav`）與 Threads 最後一則可省略。**規劃時把「轉折張、延伸閱讀、導流連結、Threads 回覆」打包成一個問題問人，每個選項附發出去的樣子**（2026-10-23：只問「連結要不要放」，人發布後才發現 Threads 輪播下沒有回覆而覺得怪）。沒有文章連結時，**`threads.last` 整個不寫**（只發輪播，人的決定 2026-10-23；`check_a`、`build_package`、`threads_publish` 都支援），不要用只有一句話的回覆湊數。

## 雙卡貼文（一則 post 併入兩張卡）

人決定把系列裡相鄰的兩張卡合成一則時（2026-10-08，`judge-readable-vs-derive` ＋ `confidence-three-metrics`）：
- 系列檔該成員加 `also: [併入的卡 id]`，並刪掉併入卡原本的獨立成員；`planned_title` 沿用主卡的。
- spec 頂層 `concept` 是主卡（發布包資料夾、state、發布網址都記在主卡），`also_concepts` 列併入的卡；程式 A 檢查兩者一致。
- 引用主卡的主張用裸 id（`c1`）；併入卡的主張與限定條件加卡 id 前綴（`confidence-three-metrics:c3`、`confidence-three-metrics:c10#1`）。
- 併入卡的 `pending_author_confirmation` 主張照樣不能用；併入卡的限定條件照樣要帶出。
- state：主卡 `ready`／`published` 時，併入卡自動同步並標 `merged_into`，不計入存量、不另記貼文（回補清單不重複）。
- 忠實者驗證：`verify_faithful.py 主卡.md,併入卡.md <faithful.json>`；提示詞的 `{CARD_PATH}` 填兩張卡。

## LaTeX 數學式（2026-10-22，Bradley-Terry 起）

圖上的數學符號與算式用 `$...$` 寫 LaTeX，頂層加 `"math": true` 才啟用（沒開的貼文，`$` 原樣當文字；已發布的貼文不受影響）。`render.py` 用 KaTeX 排版（`assets/katex/`，MIT，內嵌在 repo、不連網；只處理 class `t` 的文字區塊）。規則：
- **只放在圖上的欄位**（主標、補充、示意圖裡的 `text`／`sub`、`pairs`、`rows`…）。Threads 正文、caption 不能渲染 LaTeX，維持純文字（σ、÷、上下標用 Unicode）。
- 其他所有吃文字的地方（程式 A、`post-with-refs.md`、README、alt text）看到的是 `cardlib.tex_plain()` 轉出的純文字：`\dfrac{a}{b}` → `a/b`、`e^{r_i}` → `e^(r_i)`、`\sigma` → σ。所以程式 A 的數字與拉丁字詞檢查照常（算式裡的變數，例如 x，不在卡上時要用頂層 `latin_allow`）。
- 補充與標題裡用行內短式（`$8/(8+2) = 0.8$`、`$r_i - r_j$`）；**分數 `\dfrac` 只放在示意圖的框裡**（比一般行高，`diagrams.py` 的 `Canvas.lines` 對含分數的段落多算約一行）。
- 程式 B 多一項「LaTeX 算式沒有語法錯誤」（找 `.katex-error`）。回歸測試 `tests/test_seesaw_style.py`。

## 引用標記（每個區塊都要有）

每張投影片、hook、Threads 的正文／每則串文／最後一則、caption 第一句，都要有：

| 欄位 | 內容 |
|---|---|
| `refs` | 這個區塊引用卡上哪幾條主張（claim id，例如 `["c3", "c5"]`）。純結構文字（轉場、系列地圖）寫 `["結構"]` |
| `quals` | 這個區塊帶出的限定條件，格式 `"c3#1"`（c3 的第 1 條 `qualifiers`）。被使用的主張的所有限定條件，必須在整則貼文某處出現 |
| `fig_refs`（投影片，選用） | 這張重製圖參考了卡上哪張圖，格式 `"<article>/<src>"`，例如 `["sag/figure1.png"]`。必須是這張 `refs` 的主張所附的圖（程式 A 檢查；檔案要在、sha256 要對）。有它，`build_package.py` 會產生 `_build/figure-review.md`（給重製圖審查者）並在 caption 自動註明圖片來源。**原圖不會被複製進貼文**：圖一律由程式依這份 spec 重畫（`anchor-writing-rules.md`「參考圖」）。沒有用卡上的圖就不寫 |
| `latin_allow`（頂層） | 人決定放在圖上、但卡上沒有的拉丁字詞（例如論文網址 `["arxiv.org", "abs"]`），程式 A 不再要求被引用的主張涵蓋；只在人要求時用 |
| `waived_quals`（頂層） | 人明確決定不帶出的限定條件：`[{"id": "c8#1", "reason": "…"}]`，`reason` 必填，程式 A 不再要求它出現。只有人決定時才用（規則 7），不可自己放行 |

caption 第一句用 `first_refs`。`refs` 只證明「有對應」，不證明意思沒走樣；走樣由忠實者判斷。

## slides[]

共同欄位：`layout`、`title`（主標，結論句）、`body`（補充）、`refs`、`quals`。`label`（右上角小標籤）用來標分段（例如「第一關」「第二關」）；標題已經以同樣的詞開頭時，caption 逐張摘要不會重複前綴。

| layout | 用途 | 專屬欄位 |
|---|---|---|
| `cover` | 第 1 張 | `title`（hook 主標）、`body`（hook 副標） |
| `context` | 第 2 張，名詞表 | `body` 最多 140 字（`context_body_max_chars`）；選用 `rows`、`key_w`：補充下面放名詞對照表（補充 1 行時表從 y≈470 起，總共約 9～10 行文字放得下；要解釋的詞多於 3 個就要拆到別張或精簡）。圖上會出現的專有名詞（含 Judge、題庫名稱）要在這一張或更早的張定義 |
| `text` | 機制、限制、評價 | `body` 40～110 字（`body_chars`，約 5 行）；選用 `label`（右上角小標籤，例如「第一關」） |
| `table` | 兩欄對照（最多 4 列） | `rows: [["鍵","值"], …]`（鍵最多約 7 個字，否則換行；鍵可寫「主｜小字」把指標名稱排在下面；`key_w` 調鍵欄寬，預設 300；值很長時把 `key_w` 調小、值欄變寬）、`note`（選用，圖註，單行約 32 字內）；`body` 最多 110 字（`chart_body_max_chars`，約 5 行；表會往下讓位，總高度要放得下，不然程式 B 的「不超出版面下緣」會擋）；選用 `label` |
| `chart_bars` | 橫條圖（米色底） | `unit`、`bars`、`note`；`body` 可到約 4 行（圖會往下讓位）；選用 `label`；`subs_inline: true` 把副標籤接在名稱後面同一行（3 條時間距自動拉開；4 條橫條不要用 subs 或要用 inline） |
| `chart_bars`（**成對橫條圖**） | 同一批對象的兩個量一起看（同單位，例如每個任務的「轉出比例」與「費用」） | 每個 bar 多一個 `value2`；spec 多 `legend: ["第一個量","第二個量"]`（圖上方的圖例）、選用 `axis_max`（比例尺的滿格，例如 100）。兩個量共用同一個 0 起點與比例尺，不用雙軸；第一個量 MID、第二個量深海色，**不用金色**；`bars[].subs` 是名稱下面的小字（例如該任務的準確度），每組最多 1 行；`body` 最多 3 行、4 組，不然放不下。`emphasize` 在這個版型不用 |
| `diagram` | **示意圖**（2026-10-11 新增；除了最早的 jev-cascade，所有風格都有模板）。`kind` 決定畫法：`flow`（`nodes`、選用 `outcomes`／`loop`）、`compare`（`columns[{head, items[{text, sub?, gone?, muted?, emph?}]}]`）、`pairs`（`heads`、`pairs`、選用 `outcomes[0]` 底下一條橫框）、`samples`／`paths`（`nodes` 兩個）、`epochs`（`nodes` 兩個圖例）、`dotgrid`（`count`、選用 `cols`＝每列幾個點、`nodes` 圖例，第一個實心、第二個空心）、`dumbbell`（`points`、`ref`、`unit`、`axis_max`）、`range`（`ranges[{name, sub?, lo, hi, emph?}]`、`unit`、`axis_max`）、`funnel`（`nodes`）、`batches`（`count`、`group`、`nodes` 兩個）、`decay`（`start`、`end`、`unit`、`axis_max`、`nodes` 兩個）、`stops`（`nodes`、選用 `heads`）、`links`（2026-10-24 新增，左右兩排連線：`nodes` 左排、`outcomes` 右排、`edges` 連線 `[[左序號, 右序號], …]`、選用 `hot` 金色粗線的邊、選用 `heads`；連線內容會輸出到審查文字）、`hops`（2026-10-24 新增，幾跳才到答案：`nodes[{text, sub?, hops}]`，箭頭數＝`hops`，文字裡的數字必須等於 `hops`；選用 `heads`）、`bubble`（2026-10-24 新增，一個金色大泡泡圈住好幾個項目、左邊對照一條只連兩點的邊：`heads` 兩個、`nodes` 兩個 `{text, sub?}`（左右的說明）、`outcomes` 泡泡裡的項目 2～8 個 `{text}`）、`drift`（2026-10-24 新增，一路偏掉的路徑：`heads` 每一站的標籤 3～6 個、`nodes` 兩個 `{text, sub?}`（正確的路線、實際走的路線）；偏移量由程式依站序算，**純示意，圖註要標「示意」**）、`ingest`（2026-10-24 新增，兩段式架構圖，仿論文架構圖：`heads` 兩個（上段、下段標籤）、`nodes` 4 個（上段四欄的標籤：原始片段、一對一轉成的東西、多對多綁定的東西、存放處）、`outcomes` 2～3 個（下段由左到右的步驟，最後一個金色、下面畫小的局部超圖）；上段的方塊、圓點、連線是不帶文字的示意）、`roles`（2026-10-25 新增，三列角色卡、每列左邊一個圖示方塊：`nodes` 三個 `{text 元件名, sub 角色, sub2 做什麼, icon: db／vec／llm}`）、`embed`（2026-10-25 新增，精確比對 vs 向量空間：`heads` 兩個、`nodes` 左邊比對列 `{text, sub?, ok}`、`outcomes` 右邊向量空間的 3 個點 `{text, sub?}`，第一個是中心；純示意，圖註要說「例子是假設的」）、`online`（2026-10-25 新增，線上檢索路線圖，重畫論文圖二下半：`heads` 兩個（起點、結果）、`nodes` 第一步兩條路、`outcomes` 三個（第二步＋第三步左右兩路）；要 `fig_refs`）、`gate`（2026-10-25 新增，水庫閘門：`count` 名額、`nodes` 兩個（上游、下游）；純示意，圖註要說不是實際數量）、`concat`（2026-10-25 新增，兩路各 5 個合成 10 個：`heads` 兩個（兩路標籤）、`nodes` 兩個（上方一句話、結果）；純示意）、`joint`（2026-10-25 新增，逐一打分 vs 一起評估：`heads` 兩個、`nodes` 兩個 `{text, sub 例子, sub2 結論}`）、`rails`（2026-10-25 新增，兩條軌道各撈一排、合併成一排，A 漏掉的一格由 B 補上：`heads` 兩個、`nodes` 兩個 `{text, sub?}`、`outcomes[0]` 合併後的結果；純示意）、`fan`（`heads` 2～4 個、`nodes` 兩個：說明＋匯整結果）、`peaks`（`nodes` 三個：兩條線＋重合標籤，純示意）、`equation`（算式 A × B ＝ C，2026-10-14 新增：`nodes` 是算元 `{text 大數字, sub 單位, sub2?, emph?}`、選用 `ops`、選用 `outcomes[0]` 底下一條橫框）、`quad`（`nodes` 四格，選用 `bars`：格子上方畫一張小投影片，條列數＝bars，2026-10-14 新增）、`locked`（`heads` 兩個、`nodes` 兩個：文件名＋受保護區塊）、`seesaw`（蹺蹺板，2026-10-22 新增：`nodes` 兩個 `{text 隊名, sub?, blocks 方塊數, win 贏的機率標籤}`、選用 `outcomes[0]`；傾斜角與橫條比例由方塊數算）、`hidden`（`heads` 兩個、`nodes` 水面上的結果最多 3 個、`outcomes` 水面下藏著的東西最多 3 個 `{text, sub?}`）、`cycle`（`nodes` 三個、`heads` 三條邊的標籤、選用 `outcomes[0]`）、`tokens`（符號序列，2026-10-18 新增：`steps[{label, cells[{text, sub?, tone}]}]` 一列一步、`tone` 是 rtg／state／action／reward／mask（mask 金色＝被蓋住的那格）、選用 `more: true`（最後一列後畫省略點）、選用 `outcomes[0]` 底下一條橫框） | `body` 最多 130 字（`diagram_body_max_chars`），圖依補充行數往下讓位，放不下會直接報錯（縮短補充或圖上的字）；選用 `note`（圖註，有圖註時圖會在 y=1180 前結束）。圖上的文字與數字都要被引用的主張涵蓋（程式 A 檢查）；純示意的圖（`samples`、`paths`、`epochs`）圖上標「示意」，不得畫成實驗數據。幾何在 `scripts/diagrams.py` |
| `chart_sounding` | 測深圖（深色海面面板，最多 3 條繩） | `unit`、`bars`、`note`；`body` 最多 2 行；選用 `label` |
| `takeaway` | 倒數第二張，深海底金色字，一句話 | `title`（一句話，字最大；內含 `\n` 會換行，適合「第一關／第二關」這類並列結論，最多 4 行）、`question`（選用：先問的問題，較小的米色字，約 2 行內）、`label`（選用小字） |
| `recap` | **系列第 2 則以後的第 2 頁**（2026-10-25 人要求：看到這一則的人要知道它跟系列前面各則的關係）；系列第 1 則不用；系列檔每個成員都要有 `summary`（程式 A 檢查） | `current`（本則的 concept id）、`refs: ["結構"]`；`title` 很短（約 12 字內，一行放得下，例：`[[前情提要]]與這一則重點`）。內容由系列檔填：這一則與它之前每一則的 `planned_title`（第一層）加 `summary`（第二層，一句細節），這一則深色塊加金點；下半部是整個系列的路線（走過的實心點、這一則金色、後續空心）。**不要自己在 spec 寫清單**，改 `series/<系列>/series.md` 的 `summary` |
| `series_map` | 最後一張（獨立 post 為「延伸閱讀」） | `current`（本則的 concept id）、`nav`（導流行）；標題清單由系列檔的 `planned_title` 自動填，不要自己寫（系列檔每個成員有 `summary` 時，每則顯示「標題＋一句細節」並在下半部畫系列路線，2026-10-25 人要求；沒有就是舊的只列標題）；獨立貼文改寫 `items`（見上）、不寫 `current` |

`bars[]` 的每一項：`{"name": "官網頭條", "subs": ["速度，最佳案例", "對比前沿大模型"], "value": 193.6, "emphasize": true}`。`emphasize` 全圖只能有一個；圖上所有名稱與數字都要被引用的主張涵蓋；軸從 0 起，長度與數值成正比（由程式計算）。

## threads

```json
{
  "body":  { "text": "…", "refs": ["c3"], "quals": ["c3#1"] },
  "mode": "carousel",                                           // 輪播；不寫 items（逐張串文是 legacy，見下）
  "last":  { "text": "帶走一句話\n文章：datasciocean.com/…\n同系列：<planned_title>（尚未發布）",
             "refs": ["c1", "c2"], "link": "https://datasciocean.com/ai-concept/<slug>/" }
}
```

**輪播模式（2026-10-12 起是預設；新貼文一律用，skillopt 三則都是）**：加 `"mode": "carousel"`、**不寫 `items`**。Threads 發成**一則輪播貼文**（`body` 當正文，附**全部投影片**，順序與 IG 相同，2～20 張）＋**一則回覆**（`last`，帶連結預覽與系列；獨立貼文沒有連結時可省略）；沒有逐張串文，所以正文要自己撐起重點與限定條件。沒寫 `mode` 是舊的逐張串文（legacy，只留給已發布的三則 jev-cascade 與測試；新貼文不要用）。

## caption

```json
{ "first": "第一句（含搜尋關鍵字）", "first_refs": ["c1"],
  "nav": "導流行", "hashtags": ["DSO_SAG", "SAG", "RAG"] }
```

逐張摘要不放進 JSON，由 `build_package.py` 依最終投影片自動產生（所以必須在張數定案之後才跑）。

## 發布包結構（`out/<series>/<concept>/`）

```
README.md          這則貼文的唯一入口：縮圖、檢查結果、發布前後待辦        build_package.py
ig/post.md         每一頁的圖與文字、替代文字，最後是整段 caption           build_package.py
ig/01.png …        投影片                                                    render.py
threads/post.md    輪播貼文（正文＋全部投影片）、（有 last 時）一則回覆            build_package.py
_build/            機器用，不用看
  spec.json        內容規格（唯一的真相來源）                                人／撰寫者寫
  checks-b.json    程式 B 結果與 template_hash；alt-text.json；html/          render.py
  post-with-refs.md、post-reader.md   審查者用                              build_package.py
  contact-sheet.png                                                          contact_sheet.py
```
另有索引 `out/README.md` 與 `out/<series>/README.md`（`build_package.py` 重新產生，不手改）。
