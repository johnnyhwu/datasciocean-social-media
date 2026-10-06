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
| 已討論但還沒做的改進 | `docs/backlog.md` |
| 第一次實跑發現的問題與當時的處理 | `docs/first-run-findings.md`（歷史紀錄，結論已併入 skill） |

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
13. **審查者要求改人選的 hook 時，要告知人**（原文、改後、原因）。
14. **不要自己 commit 或 push**；commit 與 push 由人決定時機。

## 範圍外（不要做）

- 成效分析（觸及、按讚、導流）：另做獨立系統。本專案只負責記錄識別碼（觀念 id、系列 id、格式、網址、時間、hook 樣態；在 `state/`）。
- 帳號設定、頭像、簡介、發文時段：人手動做。
- 英文版：目前只做繁體中文，語言是參數（`lang: zh-TW`）。
- Reels、Shorts、長影片：目前只保留插件介面。

## 目錄

```
CLAUDE.md
.claude/skills/make-social-post/        做貼文的流程、腳本、審查者提示詞
.claude/skills/design-series-visuals/   系列視覺哲學、版型、品牌常數（新系列才用）
concept-wiki/                           submodule：觀念卡（唯讀）
config/params.yaml                      Stage 2 所有可調參數
series/<系列 id>.md                     系列定義（成員、planned_title、hashtag、色）
design/series-philosophies/<id>.md      每個系列的視覺哲學
templates/<系列 id>/                    每個系列一套 HTML 模板
assets/fonts/、assets/brand/            內嵌字型、品牌來源圖
state/<觀念 id>.yaml、state/backfill.md  各觀念各格式的狀態、發布紀錄、待回補清單
out/<系列>/<觀念>/                      發布包
docs/                                   backlog.md、first-run-findings.md
tests/                                  test_check_a.py、test_state_and_batch.py
```

為什麼 `config/`、`series/`、`templates/`、`state/` 在根目錄而不在 skill 裡：這些是人會改、會審、會長期累積的資料與設定；`.claude/` 放的是「Claude 怎麼做事」的流程與腳本。

## 第一次建立 submodule（人做一次）

`concept-wiki/` 目前不存在（重構時 `datasciocean-concept-wiki` 還沒有 commit，沒辦法 `git submodule add`）。人在那個 repo commit 並 push 之後：

```
cd datasciocean-social-media
git submodule add https://github.com/johnnyhwu/datasciocean-concept-wiki concept-wiki
```

之後 `git submodule update --remote` 就會把最新的卡拉進來。

## 目前狀態（2026-10-04）

- 系列 `jev-teardown`（6 個觀念）：第一次實跑做了 2 則（`jev-overview`、`confound-three-questions`），程式 A、B、忠實者、工程師讀者都過了，**狀態 `ready`，等人最後確認與手動發布**（`state/` 裡兩個觀念的兩種格式都是 ready）；其餘 4 個觀念 `not_tried`。存量 2 則，低於 `min_stock: 7`。
- 兩則已產出的貼文導流行用「搜尋 Jev」，因為做的時候卡還沒有 `article_title`；現在卡有了，之後的貼文改用文章標題。
- `config/params.yaml` 的 `structure_text_max_chars` 與 `ai_tone_blacklist` 是初稿，待人確認。
- 流程已依第一次實跑整理成 skill，**重構後尚未用新流程做過新貼文**；第一次用新流程做貼文時，要量 token 並記進 `docs/`。

## 工作方式

- skill 與 `references/` 是依實測整理出來的；細節有疑問時以它們為準，沒寫到的先問人，不要自己決定。
- 修改任何程式檢查或審查流程後，重跑 `uv run python tests/test_check_a.py` 與 `uv run python tests/test_state_and_batch.py`；新增檢查要加「故意做壞的版本」確認抓得到。
- 範例資料：`out/jev-teardown/confound-three-questions/` 是完整發布包（`spec.json`、`ig/`、`threads.txt`、`checks-b.json`…）。
