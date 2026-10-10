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
| **帶數字的圖：這張該用什麼圖、圖有沒有直接支撐主標、怎麼評圖** | `.claude/skills/chart-thinking/SKILL.md`（含從 OpenAI data-visualization plugin 挑來的上游資料，`upstream/`） |
| 卡長什麼樣、`status` 的語意（pending 不用、author_confirmed 取保守） | `concept-wiki/docs/card-format.md` |
| 調整參數（張數、字數、詞表、輪數、存量）與用語對照 | `config/params.yaml`、`config/terms.yaml` |

環境全在 repo 內（`.venv/`、`.uv-cache/`、`.playwright-browsers/`），**不要裝任何東西到全域**。腳本一律 `uv run python <script>`。

## 不可違反的規則

1. **只讀卡，不讀 blog。** Stage 2 不讀 `concept-wiki/blog/`。**卡是貼文內容的上限，貼文是卡的子集**，不得加入卡上沒有的判斷、數字、比較詞、缺席型主張。blog 沉默不等於「論文沒有做」。
2. **單向。** 不修改卡、不退回 Stage 1。寫不出合格貼文就標 `unsuitable` 並附原因，或刪掉做不出來的那張投影片。
3. **`pending_author_confirmation` 的主張一律不用；`author_confirmed` 的寫法取保守。**
4. **審查者要獨立、要嚴格。** 每輪用全新的 subagent，審查者看不到撰寫者的推理；忠實者預設不通過、必須引用卡上原文；撰寫者不能反駁審查者，只能標「爭議」交給人。
5. **能用程式強制的規則，就寫在程式裡，不靠 LLM。** 引用標記、數字比對、字數、座標軸從 0 起、重疊與對比度、用語、批次檢查、發布前檢查都在 `scripts/`。LLM 負責需要判斷的事。
6. **每個數字都要有比較對象；錨點類型決定寫法。** 設計參數主詞要是方法名、官方宣稱主詞要是宣稱方；部落格判斷可直接以作者口吻寫、不必標「我的判斷」（人決定，2026-10-08），但不得寫成卡上沒有的事實或比卡更強。
7. **限定條件綁在主張上。** 用了某條主張，它的限定條件必須一起出現。
8. **圖片由程式產生。** LLM 只產出內容規格 JSON；外觀由模板決定；數據圖與文字圖不用 AI 生圖。同一系列用同一份視覺哲學與同一套模板。**圖要直接支撐主標**；同一批對象的兩個同單位的量用成對橫條圖，不用雙軸（`chart-thinking`）。已發布的貼文不重渲（本機的圖要和網路上一致）。
9. **發布一定要經人確認；經確認後 IG 與 Threads 都用官方 API 發布。** `ig_publish.py`、`threads_publish.py` 預設是 dry-run，**只有人明確說「發」之後才加 `--confirm`**，不可在同一輪自己決定（人在同一則訊息明確說「prepare、push `ig/jpg/`、發佈到兩個平台」，視為整串授權，可連續執行，但每個 dry-run 都要看，出現 problems 或 warnings 就停下來問；見 `publish-flow.md`）；已發布過的貼文不重複發；不用真實貼文做測試（測試用專用測試包與 `--no-record`，測完刪掉）。限時動態、精選集、置頂、回補由人手動（`references/publish-flow.md`）。
10. **貼文不提 podcast，不加 AI 揭露。** podcast 連結只放個人檔案。
11. **寧可暫停，也不降低標準。** 存量不足時暫停發文，不為了維持每天一則而放行未通過審查的內容。
12. **不確定就停下來問人。** hook（由人挑）、版型樣張（由人審）、審查者爭議、最後確認、任何與先前慣例不同的做法，都由人決定。
13. **審查者要求改人選的 hook 時，要告知人**（原文、改後、原因）。與審查者對語氣或留白有爭議時，標「爭議」交給人，人可以改審查者提示詞。
14. **封面 hook 以吸引點擊為先，不欺騙為界**：可以沒說完整（留白、反差、口語語氣詞），但主標副標合看字面為真、範圍不放大、限定條件在內文出現（`references/hooks.md`）。取捨時預設選更吸引人。封面要**獨立可懂**（不假設讀者看過系列），口語活潑；圖上不放 emoji。
15. **不要自己 commit 或 push**；commit 與 push 由人決定時機（人明確要求時例外）。發布前要 push `ig/jpg/`（託管是這個公開 repo 的 raw 網址）；人沒有一次授權整串時，push 前先問人。
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
.claude/skills/chart-thinking/          選圖與評圖：這張圖要比什麼、有沒有支撐主標（SKILL.md ＋ upstream/ 上游資料，MIT，來源見 upstream/NOTICE.md）
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
tests/                                  六份回歸測試（含 test_multicard.py：雙卡貼文與高密度版型）+ fixtures/（舊的 jev-teardown 兩則貼文、系列檔與觀念卡，只給測試用）
```

**找東西的規則**：要發文，從 `out/README.md` 進去，打開貼文的 `README.md`；要改內容，改該貼文 `_build/spec.json`，然後依序重跑 `check_a.py` → `render.py` → `contact_sheet.py` → `build_package.py`（`contact_sheet.py` 要在 `build_package.py` 之前，README 才會有縮圖）。

為什麼 `config/`、`series/`、`state/` 在根目錄而不在 skill 裡：這些是人會改、會審、會長期累積的資料與設定；`.claude/` 放的是「Claude 怎麼做事」的流程與腳本。

## 目前狀態（2026-10-10）

- 系列 `jev-cascade`（JEV 串接 Judge 系列，來自文章 `jev-as-a-judge`；視覺哲學「潮線」）**5 張卡做成 3 則 post，三則都已用 API 發到 IG 與 Threads**（兩個格式都是 `published`）。系列標題（`planned_title`）是草案。
  1. `jev-cascade-overview`：IG https://www.instagram.com/p/DeLvR1goG7Z/ 、Threads https://www.threads.com/@datasciocean/post/DeMHNAeEzm2
  2. `judge-readable-vs-derive`＋`confidence-three-metrics`（雙卡，2026-10-08）：IG https://www.instagram.com/p/DeNyAsCGDTq/ 、Threads https://www.threads.com/@datasciocean/post/DeNyxyxmAFX
  3. `cascade-complementary-errors`＋`cascade-threshold-and-failure-mode`（雙卡，2026-10-10；封面「想用便宜的 Judge 幫 GPT-6 省錢？得先闖兩關！」）：IG https://www.instagram.com/p/DeTsWaOD3Pd/ 、Threads https://www.threads.com/@datasciocean/post/DeTsbyVjw9E
- 第 1、2 則發布時系列地圖列的是 4 則（第 3 則是 2026-10-10 才把最後兩張卡合併的，已發布的圖改不了）。存量（`ready`）0 則；下一則要開新系列或做獨立 post，先問人。
- **待人手動**：回補第 1、2 則（IG 改 caption 補連結、Threads 在原串文下加回覆，連到後面發布的則；見 `state/backfill.md`，有 6 項）；第 2、3 則的限時動態、精選集、置頂。
- 模板 hash 目前是 `e6ea36d49aa3`（2026-10-10 加成對橫條圖）；前兩則記的是舊 hash，這是預期的（已發布的不重渲、`batch_check.py` 不比對）。
- 發布流程已用真實帳號跑過三次：照 `references/publish-flow.md`。已驗證的事實與還沒驗證的事項在 `instagram-publish.md`、`threads-publish.md`。
- **待人決定**：流程／分流圖版型與樣張（`design-series-visuals/references/principles.md` 八）；封面主標是否放寬成 3 行；`config/params.yaml` 的 `structure_text_max_chars` 與 `ai_tone_blacklist` 仍是初稿；Threads token 是否補上 `threads_delete` 權限（目前沒有，刪除只能手動）；hook 與副標偏好的整理（見 memory `feedback_hook_style`，人說之後再談）。

## 工作方式

- **規劃與防呆**（2026-10-08 整理，目的是下一則一次就到位）：
  - 做系列規劃時一定要**問人哪些卡要合併**（先跑 `series_deps.py` 當輔助；它不是偵測器，要用讀者角度逐則看）；成員定案後加 `members_locked: true`，**第 1 則發布前**就定案（IG 系列地圖發布後改不了）。
  - 寫 spec 前先做**版型規劃**（每張選好版型、下半部放什麼、圖上術語在哪張定義；術語不能只在 Threads 定義），見 `ig-carousel.md` §0 與 `self-check.md` 第 10～23 項。
  - `render.py`、`build_package.py` 對**已發布**的貼文預設拒絕（`--force` 才重做；一般不要做，模板改了已發布的記舊 hash 是預期的）；`build_package.py` 遇到不認得的投影片欄位會報錯（要新增欄位先讓它輸出並補測試）。
  - 系列成員鎖定後才又合併，已發布貼文的系列地圖改不了，回補時連到合併後那一則（`batch-and-publish.md` §2）。
- **貼文要口語、白話、資訊密度夠，讀者是沒有 AI 背景的一般人**（人的回饋，2026-10-08 與 2026-10-10）：像在跟朋友解釋，不要像摘要或條列結論；術語、題庫名稱、統計用語第一次出現就用白話講；**寧可文字多一點、好懂，也不要精簡到讀者要猜**；可以用生活化比喻（比喻只翻譯、不加卡上沒有的事實）；**每張圖都要用滿**（下半部是空海面就是浪費，改用對照表、橫條圖、名詞表）；**圖要直接支撐主標**（人的回饋：圖要謹慎思考，見 `chart-thinking`）；不標「我的判斷」；準確度差距寫 %；帶走張先問問題再回答；並列的結論可用「第一關／第二關」這類標號。細節見 `ig-carousel.md` §4。審查的讀者預設是一般讀者，並且要看圖（`review-loop.md`）。

- **預設一張觀念卡 = 一則 post**；IG 輪播與 Threads 串文是同一則的兩種格式。兩張卡互相依賴、分開發都不好懂時，**由人決定**合成一則雙卡貼文（系列檔成員的 `also`；做法見 `spec-json.md`「雙卡貼文」）。同一篇文章的多張卡預設組成系列，`standalone_classic` 的卡預設獨立發文（`references/batch-and-publish.md` §1）。
- **請人拍板的事，要用白話說清楚**：這是什麼、選了會怎樣、代價是什麼、我的建議；不要只丟一句簡短的選項。
- **做完一個階段，主動列出人接下來要注意或完成的事**（要確認什麼、要手動做什麼、還沒決定什麼）。
- skill 與 `references/` 是依實測整理出來的；細節有疑問時以它們為準，沒寫到的先問人，不要自己決定。
- 修改任何程式檢查、審查或發布流程後，**重跑全部回歸測試**：`uv run python tests/test_check_a.py`、`test_state_and_batch.py`、`test_render_numunit.py`、`test_ig_publish.py`、`test_threads_publish.py`、`test_multicard.py`；新增檢查要加「故意做壞的版本」確認抓得到。
- 整理 repo 或文件時，順便檢查：討論中得到的回饋是否已寫進 CLAUDE.md 或 skill、有沒有過時（legacy）內容可刪、哪些屬於 `.claude/`（Claude 怎麼做事）而不是資料與設定。
- 範例資料：**品質基準是 `out/jev-cascade/cascade-complementary-errors/`**（雙卡貼文；內容規格在 `_build/spec.json`；口語白話、讀者不需要 AI 背景、成對橫條圖、「第一關／第二關」標號、先問再答）。下一則的口吻、密度、版型選擇都以它為準；`judge-readable-vs-derive` 是前一個基準；`jev-cascade-overview` 的寫法已過時，不要參考。`tests/fixtures/` 只給回歸測試用。
