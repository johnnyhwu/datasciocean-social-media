# CLAUDE.md

這個 repo 是 **Stage 2：把觀念卡做成 IG 輪播與 Threads 串文**（DataSci Ocean，繁體中文）。進入專案後先讀完這份。

```
datasciocean-concept-wiki（Stage 1，submodule：concept-wiki/）
        觀念卡 wiki/concepts/*.md ──[Stage 2：呈現觀念]──> out/<系列>/<觀念>/ 發布包
                                                            IG 輪播 PNG、caption、Threads 串文
```

- 本 repo 只做 Stage 2。**Stage 1 在另一個 repo**（`datasciocean-concept-wiki`，被本 repo 當 submodule 放在 `concept-wiki/`）。**只讀不寫**：不修改卡、不把問題退回 Stage 1；寫不出合格貼文，只在本 repo 的 `state/` 標該格式 `unsuitable`。
- 兩個 repo 只透過**觀念卡格式**交接，契約是 `concept-wiki/docs/card-format.md`。
- 未來會加更多格式（Reels、Shorts），格式是插件；觀念卡不放任何格式欄位。

## 每次開始前

1. `git submodule update --remote`（觀念卡要是最新的）。第一次 clone 用 `git submodule update --init --remote`。
2. 缺環境才跑 `uv sync`（Chromium 見 `.claude/skills/make-social-post/references/setup.md`）。環境全在 repo 內（`.venv/`、`.uv-cache/`、`.playwright-browsers/`），**不要裝任何東西到全域**。腳本一律 `uv run python <script>`。

## 要做什麼就讀什麼

| 要做的事 | 讀 |
|---|---|
| 把觀念做成貼文、規劃系列、寫 hook、審貼文、記錄已發布 | `.claude/skills/make-social-post/SKILL.md`（流程與細節都從它往下讀） |
| 開新系列、設計模板、新增版型或圖表類型、調整品牌常數 | `.claude/skills/design-series-visuals/SKILL.md` |
| 卡長什麼樣、`status` 的語意（pending 不用、author_confirmed 取保守） | `concept-wiki/docs/card-format.md` |
| 調整參數（張數、字數、詞表、輪數、存量） | `config/params.yaml` |

## 不可違反的規則

1. **只讀卡，不讀 blog。** Stage 2 不讀 `concept-wiki/blog/`。**卡是貼文內容的上限，貼文是卡的子集**，不得加入卡上沒有的判斷、數字、比較詞、缺席型主張。blog 沉默不等於「論文沒有做」。
2. **單向。** 不修改卡、不退回 Stage 1。寫不出合格貼文就標 `unsuitable` 並附原因，或刪掉做不出來的那張投影片。
3. **`pending_author_confirmation` 的主張一律不用；`author_confirmed` 的寫法取保守。**
4. **審查者要獨立、要嚴格。** 每輪用全新的 subagent，審查者看不到撰寫者的推理；忠實者預設不通過、必須引用卡上原文；撰寫者不能反駁審查者，只能標「爭議」交給人。
5. **能用程式強制的規則，就寫在程式裡，不靠 LLM。** 引用標記、數字比對、字數、座標軸從 0 起、重疊與對比度、批次檢查都在 `scripts/`。LLM 負責需要判斷的事。
6. **每個數字都要有比較對象；錨點類型決定寫法。** 設計參數主詞要是方法名、官方宣稱主詞要是宣稱方、我的判斷要標「我的判斷」。
7. **限定條件綁在主張上。** 用了某條主張，它的限定條件必須一起出現。
8. **圖片由程式產生。** LLM 只產出內容規格 JSON；外觀由模板決定；數據圖與文字圖不用 AI 生圖。同一系列用同一份視覺哲學與同一套模板。
9. **不自動發布。** 發布由人手動做。系統只產出發布包與待辦清單。
10. **貼文不提 podcast，不加 AI 揭露。** podcast 連結只放個人檔案。
11. **寧可暫停，也不降低標準。** 存量不足時暫停發文，不為了維持每天一則而放行未通過審查的內容。
12. **不確定就停下來問人。** hook（由人挑）、版型樣張（由人審）、審查者爭議、最後確認、任何與先前慣例不同的做法，都由人決定。
13. **審查者要求改人選的 hook 時，要告知人**（原文、改後、原因）。與審查者對語氣或留白有爭議時，標「爭議」交給人，人可以改審查者提示詞。
14. **封面 hook 以吸引點擊為先，不欺騙為界**：可以沒說完整（留白、反差、口語語氣詞），但主標副標合看字面為真、範圍不放大、限定條件在內文出現（`references/hooks.md`）。取捨時預設選更吸引人。
15. **不要自己 commit 或 push**；commit 與 push 由人決定時機。

## 範圍外（不要做）

- 成效分析（觸及、按讚、導流）：另做獨立系統。本專案只負責記錄識別碼（觀念 id、系列 id、格式、網址、時間、hook 樣態；在 `state/`）。
- 帳號設定、頭像、簡介、發文時段：人手動做。
- 英文版：目前只做繁體中文，語言是參數（`lang: zh-TW`）。
- Reels、Shorts、長影片：目前只保留插件介面。

## 目錄

```
CLAUDE.md
.claude/skills/make-social-post/        做貼文的流程、腳本、審查者提示詞（references/、scripts/）
.claude/skills/design-series-visuals/   系列視覺哲學、版型、品牌常數（新系列才用）
concept-wiki/                           submodule：觀念卡（唯讀）
config/                                 人會改的設定：params.yaml（參數）、terms.yaml（用語對照，判官 → Judge）
assets/                                 fonts/（內嵌字型）、brand/（品牌來源圖）
series/<系列 id>/                       一個系列的一切都在這裡
    series.md                             系列定義（成員、planned_title、hashtag、色）
    philosophy.md                         視覺哲學（開新系列時由 design-series-visuals 建立）
    templates/                            HTML 模板與 style.css
state/                                  <觀念 id>.yaml（各格式狀態、發布紀錄）、backfill.md（待回補清單）
out/                                    發布包（程式產生）
    README.md                             總入口：待發布清單、各系列狀態（build_package.py 產生，不手改）
    <系列 id>/README.md                   系列的發文順序與各則狀態
    <系列 id>/<觀念 id>/                  一則貼文
        README.md                           這則貼文的入口：縮圖、檢查結果、發布前後待辦
        ig/post.md、ig/01.png …             IG 輪播：每一頁的圖與文字、替代文字、整段 caption
        threads/post.md                     Threads 串文：正文、每則串文（附圖）、最後一則
        _build/                             機器用：spec.json（內容規格）、checks-b.json、html/、審查用文字…
docs/                                   stage2-token-usage.md（第一次實跑的 token 用量與觀察）
tests/                                  test_check_a.py、test_state_and_batch.py、test_render_numunit.py、fixtures/（第一次實跑的兩則貼文、系列檔與觀念卡，只給測試用）
```

**找東西的規則**：要發文，從 `out/README.md` 進去，打開貼文的 `README.md`；要改內容，改該貼文 `_build/spec.json`，然後依序重跑 `check_a.py` → `render.py` → `contact_sheet.py` → `build_package.py`（`contact_sheet.py` 要在 `build_package.py` 之前，README 才會有縮圖）。

為什麼 `config/`、`series/`、`state/` 在根目錄而不在 skill 裡：這些是人會改、會審、會長期累積的資料與設定；`.claude/` 放的是「Claude 怎麼做事」的流程與腳本。

## 目前狀態（2026-10-06）

- 第一次實跑新流程：系列 `jev-cascade`（`series/jev-cascade/`：`series.md`、`philosophy.md`「潮線」、`templates/`；5 張卡、來自文章 `jev-as-a-judge`；沿用上一輪的版型幾何，只換哲學、系列名、標籤）。
- 已完成並標 `ready`：`jev-cascade-overview` 的 IG 輪播與 Threads 串文（`out/jev-cascade/jev-cascade-overview/`，待人手動發布；發布前後待辦在該貼文的 `README.md`）。其他 4 則（`judge-readable-vs-derive`、`confidence-three-metrics`、`cascade-complementary-errors`、`cascade-threshold-and-failure-mode`）尚未做，狀態 `not_tried`；系列標題是草案。
- token 用量與流程觀察：`docs/stage2-token-usage.md`。
- **待辦（人的決定）**：圖要承載意義（光看圖就看懂方法，需要流程／分流圖版型與樣張）；`config/params.yaml` 的 `structure_text_max_chars` 與 `ai_tone_blacklist` 仍是初稿；封面主標是否放寬成 3 行。

## 工作方式

- **一張觀念卡 = 一則 post**；IG 輪播與 Threads 串文是同一則的兩種格式。同一篇文章的多張卡預設組成系列，`standalone_classic` 的卡預設獨立發文（`references/batch-and-publish.md` §1）。
- **請人拍板的事，要用白話說清楚**：這是什麼、選了會怎樣、代價是什麼、我的建議；不要只丟一句簡短的選項。（人說過簡短的拍板事項「看不懂」。）
- **做完一個階段，主動列出人接下來要注意或完成的事**（要確認什麼、要手動做什麼、還沒決定什麼）。
- 整理 repo 或文件時，順便檢查：討論中得到的回饋是否已寫進 CLAUDE.md 或 skill、有沒有過時（legacy）內容可刪、哪些屬於 `.claude/`（Claude 怎麼做事）而不是資料與設定。

- skill 與 `references/` 是依實測整理出來的；細節有疑問時以它們為準，沒寫到的先問人，不要自己決定。
- 修改任何程式檢查或審查流程後，重跑 `uv run python tests/test_check_a.py`、`uv run python tests/test_state_and_batch.py` 與 `uv run python tests/test_render_numunit.py`；新增檢查要加「故意做壞的版本」確認抓得到。
- 範例資料：現行的完整範例是 `out/jev-cascade/jev-cascade-overview/`（內容規格在 `_build/spec.json`）；`tests/fixtures/` 只給回歸測試用（第一次實跑 `jev-teardown` 的兩則貼文、系列檔與觀念卡）。
