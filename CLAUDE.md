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

1. **只讀卡，不讀 blog。** Stage 2 不讀 `concept-wiki/blog/`。**卡是貼文內容的上限，貼文是卡的子集**，不得加入卡上沒有的判斷、數字、比較詞、缺席型主張。blog 沉默不等於「論文沒有做」。例外：論文**書目資訊**（作者、年份、arXiv 連結）卡上沒有時，可外部查證，並標明來源非卡（`anchor-writing-rules.md`）。
2. **單向。** 不修改卡、不退回 Stage 1。寫不出合格貼文就標 `unsuitable` 並附原因，或刪掉做不出來的那張投影片。
3. **`pending_author_confirmation` 的主張一律不用；`author_confirmed` 的寫法取保守。**
4. **審查者要獨立、要嚴格。** 每輪用全新的 subagent，審查者看不到撰寫者的推理；忠實者預設不通過、必須引用卡上原文；撰寫者不能反駁審查者，只能標「爭議」交給人。**審查通過後新增文字、改數字／符號／論文資訊、圖上畫的東西變了，要重審改過的區塊**（`spec_diff.py`，圖變了也會列；只刪內容或削弱語氣免審，見 `review-loop.md`）。
5. **能用程式強制的規則，就寫在程式裡，不靠 LLM。** 引用標記、數字比對、字數、座標軸從 0 起、重疊與對比度、用語、批次檢查、發布前檢查都在 `scripts/`。LLM 負責需要判斷的事。
6. **每個數字都要有比較對象；錨點類型決定寫法。** 設計參數主詞要是方法名、官方宣稱主詞要是宣稱方；部落格判斷可直接以作者口吻寫、不必標「我的判斷」（人決定，2026-10-08），但不得寫成卡上沒有的事實或比卡更強。
7. **限定條件綁在主張上。** 用了某條主張，它的限定條件必須一起出現。
8. **圖片由程式產生。** LLM 只產出內容規格 JSON；外觀由模板決定；數據圖與文字圖不用 AI 生圖。同一系列用同一份視覺哲學與同一套模板。**圖要直接支撐主標**；同一批對象的兩個同單位的量用成對橫條圖，不用雙軸（`chart-thinking`）。已發布的貼文不重渲（本機的圖要和網路上一致）。
9. **發布一定要經人確認；經確認後 IG 與 Threads 都用官方 API 發布。** `ig_publish.py`、`threads_publish.py` 預設是 dry-run，**只有人明確說「發」之後才加 `--confirm`**，不可在同一輪自己決定（人在同一則訊息明確說「prepare、push `ig/jpg/`、發佈到兩個平台」視為整串授權，可連續執行，但每個 dry-run 都要看，出現 problems 或 warnings 就停下來問）；已發布過的不重複發；不用真實貼文做測試（用專用測試包與 `--no-record`，測完刪掉）。Threads 回補由 Claude 用 API 做（`backfill`，dry-run 給人看、人說「發」才發）；IG 回補、限時動態、精選集、置頂都不做。細節見 `publish-flow.md`。
10. **貼文不提 podcast，不加 AI 揭露。** podcast 連結只放個人檔案。
11. **寧可暫停，也不降低標準。** 存量不足時暫停發文，不為了維持每天一則而放行未通過審查的內容。
12. **不確定就停下來問人。** hook（由人挑；暫用的 hook 要單獨問、人明講接受才發，「目前可以」不算；`state.py ready` 會擋）、審查者爭議、最後確認、任何與先前慣例不同的做法，都由人決定。**新圖型不必先出樣張**（2026-10-12）：可直接在貼文裡做，但要附程式 B 檢查與回歸測試，交貼文時明講新增了哪些圖型。**問人時要說明選項的下游後果**，並附發出去的樣子。
13. **審查者要求改人選的 hook 時，要告知人**（原文、改後、原因）。與審查者對語氣或留白有爭議時，標「爭議」交給人，人可以改審查者提示詞。
14. **封面 hook 以吸引點擊為先，不欺騙為界**：可以沒說完整（留白、反差、口語語氣詞），但主標副標合看字面為真、範圍不放大、限定條件在內文出現（`references/hooks.md`）。取捨時預設選更吸引人。封面要**獨立可懂**（不假設讀者看過系列），口語活潑；圖上不放 emoji。
15. **不要自己 commit 或 push**；commit 與 push 由人決定時機（人明確要求時例外；commit 時 `git status` 裡不是這次改的變更，例如 submodule 指標，先說明再問）。發布前要 push `ig/jpg/`（託管是這個公開 repo 的 raw 網址）；人沒有一次授權整串時，push 前先問人。
16. **憑證只放 `.env`**（已在 `.gitignore`）：token 與 App Secret 不得出現在聊天、log、錯誤訊息、commit；**不要 `cat .env`、不要要求人把 token 貼進聊天**，用 `whoami`、`token-status`、`token-info` 檢查即可。
17. **卡上主張附的圖（`figures`）只是參考，不是證據**（2026-10-24 上游契約）。貼文內容只能來自主張文字與限定條件；要放視覺就由程式**重製**，圖上內容以這張引用的主張為準、原圖的範圍不得放大、`pending_author_confirmation` 主張的圖不能用；選主張時要用 Read 實際看圖；重製圖要派重製圖審查者。完全不用卡上的圖是合法的（`anchor-writing-rules.md`「參考圖」、`figure-prompt.md`）。

## 範圍外（不要做）

- 成效分析（觸及、按讚、導流）：另做獨立系統。本專案只負責記錄識別碼（觀念 id、系列 id、格式、網址、時間、hook 樣態；在 `state/`）。
- 帳號設定、頭像、簡介、發文時段：不在本專案範圍（不做、不提醒）。
- 英文版：目前只做繁體中文，語言是參數（`lang: zh-TW`）。
- Reels、Shorts、長影片：目前只保留插件介面。
- 限時動態、精選集、置頂、IG 回補：不做（API 不支援，人也不手動做）。

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
standalone/<觀念 id>/                  獨立貼文（沒有系列）自己的一套視覺：standalone.md（風格、色）、philosophy.md、templates/、sketches/；每則各有各的，不共用（spec 寫 series: null）
state/                                  <觀念 id>.yaml（各格式狀態、發布紀錄）、backfill.md（待回補清單）、ig-publish-log.jsonl、threads-publish-log.jsonl（API 發文紀錄，含曾經的測試發文，不要刪）
out/                                    發布包（程式產生）
    README.md                             總入口：待發布清單、各系列狀態（build_package.py 產生，不手改）
    <系列 id>/<觀念 id>/                  一則貼文（獨立貼文放 out/standalone/<觀念 id>/）；系列資料夾另有 README.md（發文順序）
        README.md                           這則貼文的入口：縮圖、檢查結果、發布前後待辦
        ig/post.md、ig/01.png …             IG 輪播：每一頁的圖與文字、替代文字、整段 caption
        ig/jpg/01.jpg …                     給 IG 與 Threads API 用的 JPEG（`ig_publish.py prepare` 產生，要 push 才有公開網址）
        threads/post.md                     Threads：輪播貼文＋（有連結時）一則回覆
        _build/                             機器用：spec.json（內容規格，唯一的真相來源）、checks-b.json、審查用文字、reviewed-spec.json（審查通過版本）…
docs/                                   status.md（各系列進度與發布網址）、stage2-token-usage.md（token 用量與流程觀察）
tests/                                  回歸測試 `test_*.py`（`test_*_style.py` 各測一種視覺風格；`test_multicard.py` 雙卡與高密度版型；`test_figures.py` 卡上參考圖）+ fixtures/（舊貼文、系列檔與觀念卡，只給測試用）
```

**找東西的規則**：要發文，從 `out/README.md` 進去，打開貼文的 `README.md`；要改內容，改該貼文 `_build/spec.json`，然後依序重跑 `check_a.py` → `render.py` → `contact_sheet.py` → `build_package.py`（`contact_sheet.py` 要在 `build_package.py` 之前，README 才會有縮圖）。各腳本吃 spec.json 還是發布包資料夾不一致，常打錯，見 `make-social-post/SKILL.md`「腳本」。

為什麼 `config/`、`series/`、`state/` 在根目錄而不在 skill 裡：這些是人會改、會審、會長期累積的資料與設定；`.claude/` 放的是「Claude 怎麼做事」的流程與腳本。

## 目前狀態（各系列進度、網址、待決事項：`docs/status.md`）

- 已發布：系列 `skillopt`、`persona-aware-d2s`、`jev-cascade`、`sag`、`claude-code`，獨立貼文 `decision-transformer-reward-conditioning`、`bradley-terry-pairwise-preference`。模板 hash 與已發布貼文不一致是預期的（已發布的不重渲）。
- 進行中：`cerebras-rag`（第 1 則已發布（2026-11-01），第 2、3 則 `ready`）。
- 獨立貼文（沒有系列）：spec 寫 `series: null`，視覺在 `standalone/<觀念 id>/`，發布包在 `out/standalone/`。

## 工作方式

細節都在 skill 裡，這裡只列原則與去處；**同一條規則只寫在一處**（人的回饋寫進對應的 reference，不在這裡、memory、skill 各寫一次）。

- **流程**：`make-social-post/SKILL.md`。程式 B 通過後**先給人看初稿**（縮圖＋`ig/post.md`，看結構、順序、圖），人點頭才派審查者（步驟 6b，人 2026-11-01 決定）。
- **寫法**（讀者是沒有 AI 背景的一般人、口語白話、資訊密度夠、寧可多一點也不要讓讀者猜；整則要像一段旅程；主角先、對照後；敘事口吻不寫第三人稱「作者」；實驗頁要有所以呢；用語偏好）：`references/ig-carousel.md` §0、§0b、§4，用語在 `config/terms.yaml`。
- **圖**（要大膽、有創意、直接支撐主標、比文字多給資訊；畫面句要有具體物件；沒有合適的就發明新圖型）：`ig-carousel.md` §0、`design-series-visuals/references/brand-and-layouts.md` §4.2、`principles.md`；帶數字的圖用 `chart-thinking`。
- **系列規劃**（問人哪些卡合併、整個系列 spec 做完才鎖定並發第 1 則、第 2 則以後有 `recap`）：`references/batch-and-publish.md` §1–2、`spec-json.md`。
- **送審前自檢**：`references/self-check.md`（最上面四類是忠實者最常退回的）。審查：`review-loop.md`。
- **進度寫進檔案**：每則 `_build/progress.md`，最上面是 10 行內的「現況＋待人決定」；要人挑的清單（hook 候選、合併方案）也寫進檔案，對話壓縮後才不會丟。
- **請人拍板的事用白話說清楚**（這是什麼、選了會怎樣、代價、我的建議）；做完一個階段，主動列出人接下來要確認或決定的事。人不做手動事項：需要手動的，Claude 做或不做，不丟給人。
- skill 與 `references/` 是依實測整理出來的，有疑問以它們為準，沒寫到的先問人。
- 修改任何程式檢查、審查或發布流程後，**重跑全部回歸測試**：`for f in tests/test_*.py; do uv run python $f; done`（約 10 分鐘以上，用背景執行）；新增檢查要加「故意做壞的版本」，新增圖型要在 `tests/test_diagrams.py` 補正案與壞案。
- 整理 repo 或文件時，順便檢查：回饋是否已寫進對應的 reference、有沒有過時內容可刪、memory 有沒有和 repo 重複（重複的刪 memory）。
- 範例貼文：`make-social-post/SKILL.md`「範例」。
