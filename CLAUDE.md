# CLAUDE.md

這個 repo 是 **Stage 2：把觀念卡做成 IG 輪播與 Threads 串文，並用官方 API 發布**（DataSci Ocean，繁體中文）。進入專案後先讀完這份。

```
datasciocean-concept-wiki（Stage 1，submodule：concept-wiki/）
        觀念卡 wiki/concepts/*.md ──[Stage 2：呈現觀念]──> out/<系列>/<觀念>/ 發布包
                                                            ──[人確認後，官方 API]──> IG 輪播、Threads 串文
```

- 本 repo 只做 Stage 2。**Stage 1 在另一個 repo**（`datasciocean-concept-wiki`，被本 repo 當 submodule 放在 `concept-wiki/`）。**只讀不寫**：不修改卡、不把問題退回 Stage 1；寫不出合格貼文，只在本 repo 的 `state/` 標該格式 `unsuitable`。
- 兩個 repo 只透過**觀念卡格式**交接，契約是 `concept-wiki/docs/card-format.md`。
- 未來會加更多格式（Reels、Shorts），格式是插件；觀念卡不放任何格式欄位。

## 要做什麼就讀什麼

| 要做的事 | 讀 |
|---|---|
| **做下一則貼文、規劃系列、寫 hook、審貼文、發布到 IG 與 Threads、記錄已發布** | `.claude/skills/make-social-post/SKILL.md`（新 session 從它的「開始前」起手；流程與細節都從它往下讀；發布照 `references/publish-flow.md`） |
| 開新系列、設計模板、新增版型或圖表類型、調整品牌常數 | `.claude/skills/design-series-visuals/SKILL.md` |
| 卡長什麼樣、`status` 的語意（pending 不用、author_confirmed 取保守） | `concept-wiki/docs/card-format.md` |
| 調整參數（張數、字數、詞表、輪數、存量）與用語對照 | `config/params.yaml`、`config/terms.yaml` |

環境全在 repo 內（`.venv/`、`.uv-cache/`、`.playwright-browsers/`），**不要裝任何東西到全域**。腳本一律 `uv run python <script>`。

## 不可違反的規則

1. **只讀卡，不讀 blog。** Stage 2 不讀 `concept-wiki/blog/`。**卡是貼文內容的上限，貼文是卡的子集**，不得加入卡上沒有的判斷、數字、比較詞、缺席型主張。blog 沉默不等於「論文沒有做」。
2. **單向。** 不修改卡、不退回 Stage 1。寫不出合格貼文就標 `unsuitable` 並附原因，或刪掉做不出來的那張投影片。
3. **`pending_author_confirmation` 的主張一律不用；`author_confirmed` 的寫法取保守。**
4. **審查者要獨立、要嚴格。** 每輪用全新的 subagent，審查者看不到撰寫者的推理；忠實者預設不通過、必須引用卡上原文；撰寫者不能反駁審查者，只能標「爭議」交給人。
5. **能用程式強制的規則，就寫在程式裡，不靠 LLM。** 引用標記、數字比對、字數、座標軸從 0 起、重疊與對比度、用語、批次檢查、發布前檢查都在 `scripts/`。LLM 負責需要判斷的事。
6. **每個數字都要有比較對象；錨點類型決定寫法。** 設計參數主詞要是方法名、官方宣稱主詞要是宣稱方、我的判斷要標「我的判斷」。
7. **限定條件綁在主張上。** 用了某條主張，它的限定條件必須一起出現。
8. **圖片由程式產生。** LLM 只產出內容規格 JSON；外觀由模板決定；數據圖與文字圖不用 AI 生圖。同一系列用同一份視覺哲學與同一套模板。
9. **發布一定要經人確認；經確認後 IG 與 Threads 都用官方 API 發布。** `ig_publish.py`、`threads_publish.py` 預設是 dry-run，**只有人明確說「發」之後才加 `--confirm`**，不可在同一輪自己決定；已發布過的貼文不重複發；不用真實貼文做測試（測試用專用測試包與 `--no-record`，測完刪掉）。限時動態、精選集、置頂、回補由人手動（`references/publish-flow.md`）。
10. **貼文不提 podcast，不加 AI 揭露。** podcast 連結只放個人檔案。
11. **寧可暫停，也不降低標準。** 存量不足時暫停發文，不為了維持每天一則而放行未通過審查的內容。
12. **不確定就停下來問人。** hook（由人挑）、版型樣張（由人審）、審查者爭議、最後確認、任何與先前慣例不同的做法，都由人決定。
13. **審查者要求改人選的 hook 時，要告知人**（原文、改後、原因）。與審查者對語氣或留白有爭議時，標「爭議」交給人，人可以改審查者提示詞。
14. **封面 hook 以吸引點擊為先，不欺騙為界**：可以沒說完整（留白、反差、口語語氣詞），但主標副標合看字面為真、範圍不放大、限定條件在內文出現（`references/hooks.md`）。取捨時預設選更吸引人。
15. **不要自己 commit 或 push**；commit 與 push 由人決定時機（人明確要求時例外）。發布前要 push `ig/jpg/`（託管是這個公開 repo 的 raw 網址），要 push 時先問人。
16. **憑證只放 `.env`**（已在 `.gitignore`）：token 與 App Secret 不得出現在聊天、log、錯誤訊息、commit；**不要 `cat .env`、不要要求人把 token 貼進聊天**，用 `whoami`、`token-status`、`token-info` 檢查即可。

## 範圍外（不要做）

- 成效分析（觸及、按讚、導流）：另做獨立系統。本專案只負責記錄識別碼（觀念 id、系列 id、格式、網址、時間、hook 樣態；在 `state/`）。
- 帳號設定、頭像、簡介、發文時段：人手動做。
- 英文版：目前只做繁體中文，語言是參數（`lang: zh-TW`）。
- Reels、Shorts、長影片：目前只保留插件介面。
- 用 API 發限時動態：官方不支援連結貼紙，維持人手動。

## 目錄

```
CLAUDE.md
.claude/skills/make-social-post/        做貼文與發布的流程：SKILL.md、references/（規格與步驟）、scripts/
.claude/skills/design-series-visuals/   系列視覺哲學、版型、品牌常數（新系列才用）
concept-wiki/                           submodule：觀念卡（唯讀）
config/                                 人會改的設定：params.yaml（參數）、terms.yaml（用語對照，判官 → Judge）
.env / .env.example                     IG 與 Threads 的憑證（.env 不進 git；範本是 .env.example）
assets/                                 fonts/（內嵌字型）、brand/（品牌來源圖）
series/<系列 id>/                       一個系列的一切都在這裡：series.md（成員、planned_title、hashtag、色）、philosophy.md（視覺哲學）、templates/
state/                                  <觀念 id>.yaml（各格式狀態、發布紀錄）、backfill.md（待回補清單）、ig-publish-log.jsonl、threads-publish-log.jsonl（API 發文紀錄，含曾經的測試發文，不要刪）
out/                                    發布包（程式產生）
    README.md                             總入口：待發布清單、各系列狀態（build_package.py 產生，不手改）
    <系列 id>/README.md                   系列的發文順序與各則狀態
    <系列 id>/<觀念 id>/                  一則貼文
        README.md                           這則貼文的入口：縮圖、檢查結果、發布前後待辦
        ig/post.md、ig/01.png …             IG 輪播：每一頁的圖與文字、替代文字、整段 caption
        ig/jpg/01.jpg …                     給 IG 與 Threads API 用的 JPEG（`ig_publish.py prepare` 產生，要 push 才有公開網址）
        threads/post.md                     Threads 串文：正文、每則串文（附圖）、最後一則
        _build/                             機器用：spec.json（內容規格，唯一的真相來源）、checks-b.json、審查用文字…
docs/                                   stage2-token-usage.md（token 用量與流程觀察）
tests/                                  五份回歸測試 + fixtures/（舊的 jev-teardown 兩則貼文、系列檔與觀念卡，只給測試用）
```

**找東西的規則**：要發文，從 `out/README.md` 進去，打開貼文的 `README.md`；要改內容，改該貼文 `_build/spec.json`，然後依序重跑 `check_a.py` → `render.py` → `contact_sheet.py` → `build_package.py`（`contact_sheet.py` 要在 `build_package.py` 之前，README 才會有縮圖）。

為什麼 `config/`、`series/`、`state/` 在根目錄而不在 skill 裡：這些是人會改、會審、會長期累積的資料與設定；`.claude/` 放的是「Claude 怎麼做事」的流程與腳本。

## 目前狀態（2026-10-07）

- 系列 `jev-cascade`（JEV 串接 Judge 系列，5 張卡，來自文章 `jev-as-a-judge`；視覺哲學「潮線」；沿用上一輪的版型幾何）。系列標題（`planned_title`）是草案。
- **`jev-cascade-overview`（第 1 則）已用 API 發到 IG 與 Threads**，兩個格式都是 `published`。其他 4 則（`judge-readable-vs-derive`、`confidence-three-metrics`、`cascade-complementary-errors`、`cascade-threshold-and-failure-mode`）還沒做，下一則預設是 `judge-readable-vs-derive`。存量（`ready`）0 則。
- 發布流程已用真實帳號實測過（IG 輪播與 Threads 串文）：照 `references/publish-flow.md`。已驗證的事實與還沒驗證的事項在 `instagram-publish.md`、`threads-publish.md`。
- **待人決定**：圖要承載意義（光看圖就看懂方法，需要流程／分流圖版型與樣張，見 `design-series-visuals/references/principles.md` 八）；封面主標是否放寬成 3 行；`config/params.yaml` 的 `structure_text_max_chars` 與 `ai_tone_blacklist` 仍是初稿；Threads token 是否補上 `threads_delete` 權限（目前沒有，刪除只能手動）。

## 工作方式

- **一張觀念卡 = 一則 post**；IG 輪播與 Threads 串文是同一則的兩種格式。同一篇文章的多張卡預設組成系列，`standalone_classic` 的卡預設獨立發文（`references/batch-and-publish.md` §1）。
- **請人拍板的事，要用白話說清楚**：這是什麼、選了會怎樣、代價是什麼、我的建議；不要只丟一句簡短的選項。
- **做完一個階段，主動列出人接下來要注意或完成的事**（要確認什麼、要手動做什麼、還沒決定什麼）。
- skill 與 `references/` 是依實測整理出來的；細節有疑問時以它們為準，沒寫到的先問人，不要自己決定。
- 修改任何程式檢查、審查或發布流程後，**重跑全部回歸測試**：`uv run python tests/test_check_a.py`、`test_state_and_batch.py`、`test_render_numunit.py`、`test_ig_publish.py`、`test_threads_publish.py`；新增檢查要加「故意做壞的版本」確認抓得到。
- 整理 repo 或文件時，順便檢查：討論中得到的回饋是否已寫進 CLAUDE.md 或 skill、有沒有過時（legacy）內容可刪、哪些屬於 `.claude/`（Claude 怎麼做事）而不是資料與設定。
- 範例資料：現行完整範例是 `out/jev-cascade/jev-cascade-overview/`（內容規格在 `_build/spec.json`）；`tests/fixtures/` 只給回歸測試用。
