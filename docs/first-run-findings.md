# 第一次實跑（jev-overview、confound-three-questions）發現的問題：Stage 2 部分

這是**歷史紀錄**。Stage 1 的發現留在 `datasciocean-concept-wiki` repo 的 `docs/first-run-findings.md`。下表「規格已改」欄是當時（重構前，兩個階段還在同一個 repo、規格是 `docs/03`、`docs/04`）的狀態，現在以本 repo 的 skill 為準；處理對照見下。

## 重構後的處理對照

| 發現 | 現在放在哪 |
|---|---|
| #33 環境（Playwright、字型、uv 限縮在 repo 內） | `.claude/skills/make-social-post/SKILL.md`「開始前」、`references/setup.md` |
| #34 字級集合 | `.claude/skills/design-series-visuals/references/brand-and-layouts.md`；`render.py` 的 `ALLOWED_FONT_PX` |
| #35 圖表補充一行約 24 字、脈絡張上限 90 | `references/ig-carousel.md`；`config/params.yaml`；`check_a.py` |
| #36 結構區塊字數上限、AI 腔黑名單（初稿，待人確認） | `config/params.yaml`；`references/program-a.md` |
| #37 導流行需要 `article_title` | 已在 Stage 1 卡加 `sources[].article_title`；`references/threads-and-caption.md` 規定用它；**這次實跑的兩則貼文是用「搜尋 Jev」代替，尚未改** |
| #38–#40 程式 B 抓到的問題、`keep-all` 長串、回歸測試 | `references/program-b.md`；`tests/test_check_a.py` |
| #41 忠實者的 blocker 幾乎都是真問題 | `references/review-loop.md` |
| #42 卡上沒有的內容，貼文就寫不出來；砍掉整張投影片與串文 | `references/ig-carousel.md`、`references/review-loop.md` |
| #43 審查者與撰寫者對寫法標準不一致（第一人稱「我的判斷」） | `references/anchor-writing-rules.md` |
| #44 hook 被忠實者要求改字，須告知人 | `references/hooks.md`、`references/review-loop.md` |
| #45 最後一次刪內容只用程式驗證 | `references/review-loop.md`（刪除不新增風險，可免重審，但要在報告說明） |

## 發現清單

| # | 發現 | 處理 | 規格已改 |
|---|---|---|---|
| 33 | 環境：本機沒有 Playwright／字型。人要求「uv 限縮在 repo 內」 | 建 pyproject.toml、.venv、.uv-cache、.playwright-browsers 全放 repo 內，字型 Noto Sans CJK TC 放 reference/fonts（共 33MB）。Chromium 約 557MB | 否（需寫進 skill 的安裝說明） |
| 34 | 規格 04 §3 的字級集合不夠用：實作需要 36、30、84。改成都落在規格集合 28／34／38／40／56／72／76 內 | 版型字級已對齊 | 否 |
| 35 | 圖表版型補充「一行」在 38px 只容得下約 24 字；文字張補充 40–60 字在 40px 約 3 行 | 程式 A 加 24 字預檢；脈絡張另設上限 90（實作新增） | 否 |
| 36 | 規格 03 §8 說「結構」區塊有字數上限但沒給數字；中文 AI 腔黑名單也沒給名單 | params.yaml 暫定 12 字與 11 個詞的初稿，待人確認 | 否 |
| 37 | 導流行：規格預設寫「文章標題」，但文章標題不在任何 wiki 欄位，Stage 2 又不能讀 blog | 暫以「搜尋 Jev」與網址路徑代替。建議 Stage 1 在 sources 加 article_title | 否 |
| 38 | 程式 B 在建置中抓到真問題 11 次：文字框重疊（名稱與副標籤太近）、keep-all 長串超出版心、對照表列高估錯壓線、字級 16px（容器被誤當文字）、對比度、空元素座標 0 等。**撰寫者看圖也看過，但程式先抓到** | 見 render.py | — |
| 39 | `word-break: keep-all` 對中文只在標點處斷行；連續 13 字以上無標點會超出版心。模板需限制「無標點連續字數」 | 現靠程式 B 的溢出檢查擋下，建議加預檢 | 否 |
| 40 | 程式 A 回歸測試 21 項「故意做壞」全抓到、2 項正確貼文通過（`tests/stage2/test_check_a.py`） | 完成 | — |
| 41 | 忠實者在第 1 輪對兩則共擋下 20 個 blocker，**幾乎都是真問題**：把部落格判斷寫成事實、官方宣稱沒以官方為主詞、takeaway 漏掉「或只把 Jev 當第一道篩選」、「只拿標價」是缺席型主張、串文描述對錯圖。工程師讀者兩則第 1 輪就通過；編輯給 45 條建議（不擋） | 修正後第 2、3 輪 blocker 20 → 3 → 0 | 否 |
| 42 | **卡上沒有的內容，貼文就寫不出來**：jev-overview 的 Every 觀察（c22）整張卡只有一條，串文描述想不重述圖又不夾帶，做不到（程式 A 重疊率 62%）。結論：拿掉那張投影片與對應串文 | 貼文是卡的子集，不必用盡每條主張 | 否 |
| 43 | 審查者與撰寫者對「寫法」的標準不一致會造成往返：例如貼文以第一人稱寫「我的判斷」是否符合「直接以論文或官方為來源」。目前以「標我的判斷」處理 | 待人確認 | 否 |
| 44 | 使用者核准的 hook A3 副標「想要快又要彈性，Jev 想補中間那塊」是部落格判斷（c1），忠實者要求標「我的判斷」，已改成「我的判斷：Jev 想補的，正是這兩條路中間的空隙」；A3 主標加「換任務」以符合卡。**這是我改了你選的 hook 文字** | 報告中告知 | — |
| 45 | Stage 2 最後一處修改（刪除 jev-overview 的 Every 投影片與串文）只用程式 A、B 驗證；刪內容不新增忠實度風險，所以沒有再派審查者 | 同 Stage 1 c3 的處理方式 | 否 |
