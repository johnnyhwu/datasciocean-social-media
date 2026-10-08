# 發布流程（IG 與 Threads）：從「發布包完成」到「寫回狀態」

這份是**可以照著做的完整程序**。兩個平台的設定、官方限制、錯誤碼細節在 `instagram-publish.md` 與 `threads-publish.md`；這裡只講順序、誰要確認、出錯怎麼辦。

```
S=.claude/skills/make-social-post/scripts      # 下面指令的簡寫；一律 uv run python $S/<name>.py
P=out/<系列>/<觀念>                              # 要發的發布包資料夾
```

## 0. 發文前的前提

| 前提 | 怎麼確認 |
|---|---|
| 系列成員已定案（`series.md` 有 `members_locked: true`；第 1 則發布前） | dry-run 的 `warnings` 沒有「成員清單還沒定案」 |
| 貼文已做完並經人最後確認 | `state.py status` 該觀念兩個格式都是 `ready`；人已看過貼文的 `README.md`、`ig/post.md`、`threads/post.md` |
| `.env` 有憑證 | 有 `IG_ACCESS_TOKEN`、`IG_USER_ID`、`THREADS_ACCESS_TOKEN`、`THREADS_USER_ID`（範本 `.env.example`）。**不要 `cat .env`，也不要請人貼 token**；只用下面的指令檢查 |
| `.env` 不存在或缺欄位 | 停下來，請人照 `instagram-publish.md`「一次性設定」與 `threads-publish.md` 設定；token 由人自己貼進 `.env` |
| token 還有效 | `ig_publish.py token-status`、`threads_publish.py token-status`（剩不到 14 天會警告，並在發文前自動 refresh）；`threads_publish.py token-info` 可查實際權限與到期時間 |
| 帳號正確 | `ig_publish.py whoami`、`threads_publish.py whoami --no-write`，確認是 `datasciocean` |
| 發文額度 | `ig_publish.py limit`、`threads_publish.py limit`（兩邊各有上限，我們一天頂多 1 則） |

## 1. 流程

**每一個 `--confirm` 之前，都要先把 dry-run 的結果用白話給人看，等人明確說「發」。不可以在同一輪裡自己決定發。不可以用真實貼文做測試；測試用專用的測試包與 `--no-record`，測完把測試包刪掉。**

| # | 做什麼 | 指令 | 誰 |
|---|---|---|---|
| 1 | 把投影片轉成 IG 與 Threads 都能用的 JPEG，驗證官方限制 | `ig_publish.py prepare $P` | Claude |
| 2 | **commit 並 push `$P/ig/jpg/`**（Meta 要從這個公開 repo 的 raw 網址抓圖；沒 push 就抓不到）。只 add 這個資料夾，commit message 簡短說明 | `git add $P/ig/jpg && git commit … && git push origin main` | Claude，**push 前先問人** |
| 3 | **IG 預檢**：建好所有 container、等到 FINISHED，**但不發佈**（帳號上看不到；23 小時內有效） | `ig_publish.py preflight $P` | Claude |
| 4 | **IG dry-run**：印出將送出的請求、檢查網址與額度、報告預檢能不能沿用。把 caption、張數、預檢狀態用白話給人 | `ig_publish.py publish $P` | Claude → 人看 |
| 5 | 人說「發」→ **IG 發佈**（沿用預檢，只送一個 `media_publish`）；成功後自動寫回 state 與 `state/ig-publish-log.jsonl` | `ig_publish.py publish $P --confirm` | 人確認，Claude 執行 |
| 6 | **Threads dry-run**：列出每一則（通常 7 則）的完整文字、字數、附圖、連結預覽、額度。把完整文字給人 | `threads_publish.py publish $P` | Claude → 人看 |
| 7 | 人說「發」→ **Threads 發佈**：依序發，每一則回覆前一則，每一則發完立刻記錄 id；整串約 4 到 5 分鐘；成功後自動寫回 state 與 `state/threads-publish-log.jsonl` | `threads_publish.py publish $P --confirm` | 人確認，Claude 執行 |
| 8 | 驗證：`state.py status` 該觀念兩格式都是 `published`；`state/<觀念>.yaml` 有兩個網址；把網址給人 | | Claude |
| 9 | 提醒人做**只能手動**的事（見下）；有回補清單項目就提醒 | `state/backfill.md` | 人 |
| 10 | 把這次的 state 與發佈紀錄 commit（問人要不要 push） | | Claude，**先問人** |

IG 與 Threads **可以各自獨立發**，順序由人決定（目前慣例是先 IG 再 Threads）。其中一個失敗不影響另一個。

## 2. 只能由人手動做的事（API 做不到或規則不自動）

| 事項 | 為什麼 |
|---|---|
| **限時動態**（分享貼文並加連結貼紙指向文章） | 官方 API 發限時動態不支援貼紙，包含連結貼紙，見 `instagram-publish.md` |
| 收進精選集、置頂（IG 概覽 post、Threads 最後一則回覆） | 不在 API 範圍 |
| 系列其他則發布後的**回補**：IG 修改 caption 補延伸連結；Threads 在原串文下加回覆補連結 | 由 `state/backfill.md` 列出；做完在 `state/<觀念>.yaml` 的 `backfilled` 加上觀念 id |
| 帳號設定、頭像、簡介、發文時段 | 不在本專案範圍 |
| **刪除貼文**（IG 一律手動；Threads 需 `threads_delete` 權限，目前 token 沒有） | 見下 |

## 3. 出錯怎麼辦

| 情況 | 做法 |
|---|---|
| dry-run 說圖片網址抓不到（HTTP 404） | 還沒 push `ig/jpg/`，或 push 剛完成 CDN 尚未更新；等幾秒重跑 |
| IG 預檢／發佈失敗 | 看輸出的 `error` 與 `hint`（9004 抓不到圖、9007 容器未完成、9 超過上限、190 token 失效）。**可重試的錯誤（網路、HTTP 5xx）程式會自動重試最多 3 次**，其他不重試 |
| IG 預檢過期（超過 23 小時）、預檢後改了內容 | 發佈時自動重建 container，不必手動處理；想強制重建加 `--no-reuse` |
| IG 已發出後發現有錯 | 只能人到 app 手動刪或編輯 caption（API 沒有）；**絕不要為了重發而再 `--confirm`**，程式本來就會因 state 已是 published 而拒絕 |
| Threads 發到一半失敗 | 輸出會寫「已發佈 k/N 則」。修好問題後**再執行同一個指令**，會從第 k+1 則繼續，不會重複發。內容在發到一半後被改過會被擋下 |
| Threads 要撤掉已發的 | `threads_publish.py rollback $P --confirm`（整串，由後往前刪）。**需要 `threads_delete` 權限**；沒有時 API 回 403（`token-info` 的 `can_delete: false`），這時請人在 Threads app 手動刪（或典藏）。要開權限：在 App 的 Threads 設定頁加入 `threads_delete` 後**重新產生 token** |
| token 失效或快到期 | 剩不到 14 天且 token 存在滿 24 小時時，指令會自動 refresh 並寫回 `.env`。已失效（超過 60 天沒 refresh）就必須由人重新產生：IG 在 App Dashboard 的「API setup with Instagram business login」按 Generate token；Threads 在 Use cases > Access the Threads API > Settings 的 Generate Access Token。**請人貼進 `.env`，不要貼進聊天** |
| dry-run 說「已發布過」 | state 顯示該格式已 published，不會重複發。若 state 錯了（例如測試時漏了 `--no-record`），要人確認後再修 `state/<觀念>.yaml` |

## 4. 測試與安全（修改發布程式時）

- 發布程式的回歸測試用假的 transport，不連網：`tests/test_ig_publish.py`、`tests/test_threads_publish.py`。改了發布程式就要跑，並為新行為補「故意做壞的版本」。
- 要對真的 API 實測，必須：先告訴人要發什麼、發到哪個帳號、之後怎麼清、請人明確同意；用專用測試包（`out/_test/…`，用完刪）與 `--no-record`。
- 任何輸出、log、紀錄都不得出現 token；token 與 App Secret 只在 `.env`。
- 發佈紀錄 `state/*-publish-log.jsonl` 是追溯用的真實紀錄（含曾經的測試發文），不要刪。
