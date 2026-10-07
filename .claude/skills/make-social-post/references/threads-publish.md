# 用 Threads 官方 API 發佈串文

走 Meta 官方 Threads API（host: `graph.threads.net`，官方頁面也出現 `graph.threads.com`，可用 `THREADS_API_HOST` 切換），不使用任何第三方封裝服務。

**兩個平台從頭到尾的發布程序見 `publish-flow.md`**（照那份做）；這份是 Threads 的設定、官方限制與實測結果。

**規則**：預設 dry-run；實際發佈必須由人明確確認後才加 `--confirm`（CLAUDE.md 規則 9）。token 與 app secret 只放 `.env`，不得出現在聊天、log、錯誤訊息、commit。

## 一次性設定（人做）

依官方文件 `threads/get-started`；實際畫面可能略有不同，以 Meta 的畫面為準。**Threads 的 token 和 IG 的是兩組，不能共用。**

1. 在 developers.facebook.com 你原本的 App（或新建一個）裡，加入 **「Access the Threads API」use case**。官方說會拿到「兩組 App ID 與 secret，要用 Threads 專屬的那組」。
2. **加入 Threads Tester**：App Dashboard > App roles > Roles > Add People > 選 **Threads Tester** > 輸入你的 Threads 帳號 username。
3. **在 Threads 接受邀請**：Threads app 或網站 > 帳號設定 > **Website permissions**（網站權限）> 接受邀請。
4. 在 Use cases > Access the Threads API > Customize > **Settings**，確認權限有 `threads_basic`、`threads_content_publish`；**建議再勾 `threads_delete`**（測試後可以用 API 刪除、發到一半失敗時可以 rollback）。
5. 同一頁底部的 **Generate Access Token**，產生 token（會以 `TH` 開頭）。複製到 `.env` 的 `THREADS_ACCESS_TOKEN=`。**不要把 token 貼進聊天。**
6. 驗證：`uv run python .claude/skills/make-social-post/scripts/threads_publish.py whoami --no-write`，成功會印出 username 與 user id；確認後再執行不加 `--no-write` 的版本，或自己把 user id 補進 `.env`。

**已驗證**：Dashboard 的 Generate Access Token 產生的是 **60 天長效 token**（`token-info` 查到的 `expires_at` 約 60 天後），不需要 `THREADS_APP_SECRET`。若哪天拿到的是短效 token（`token-info` 顯示不到 2 天），才需要 App Secret 與 `exchange-token`。

**查 token 實際被授予哪些權限與到期時間**：`threads_publish.py token-info`（用官方 `GET /debug_token`，不需要 App Secret；`--write` 會把 `THREADS_TOKEN_REFRESHED_AT` 校正成到期時間減 60 天）。**權限是在產生 token 時決定的**：要用 `rollback`／`delete`，必須先在 App 的 Threads 設定頁把 `threads_delete` 加進權限清單，**再重新產生 token**；`token-info` 的 `can_delete` 要是 `true`。

## 流程

```
（圖要先 prepare 並 push：Threads 沿用 IG 的 ig/jpg/NN.jpg，公開網址是這個 repo 的 raw 網址）
publish  → dry-run：列出每一則的文字、字數、圖片網址、將送出的請求，檢查網址公開可抓、有沒有發布過
人看 threads/post.md 確認
人說「發」
publish --confirm → 依序發 N 則：
    第 1 則：正文（TEXT）
    第 2…N-1 則：每則附圖（IMAGE，image_url + 描述），reply_to_id = 前一則
    最後一則：TEXT，帶 link_attachment（文章連結預覽），reply_to_id = 前一則
  每一則：建 container → 等約 30 秒（官方建議）並確認完成 → threads_publish → 立刻把 id 寫進 _build/threads-progress.json
  全部完成 → 取根貼文的 permalink → state.py record（threads_thread 變 published）→ 寫 state/threads-publish-log.jsonl
```

- **中途失敗**：修好問題後再執行同一個指令，會從下一則繼續，不會重複發。內容在發到一半後被改過會被擋下。
- **撤掉整串**：`rollback --confirm`（`DELETE /{id}`，由後往前刪；需要 `threads_delete` 權限，每天 100 次）。
- 與 IG 不同：Threads 的串文**無法預檢**（回覆需要前一則「已發佈」的 id），所以沒有 preflight；風險由 dry-run、進度檔、rollback 承擔。
- 第一次實測用 `--no-record`，並用 `rollback` 或 `delete` 清掉測試串文。

## 官方限制（已查證；來源是官方文件）

| 項目 | 內容 |
|---|---|
| 發文 | `POST /{id}/threads`（建 container）→ `POST /{id}/threads_publish`；`media_type`：TEXT、IMAGE、VIDEO、CAROUSEL |
| 文字 | 500 字元；emoji 以 UTF-8 位元組計；每則最多 5 個不同連結；文字中的第一個網址會成為連結預覽；`link_attachment` 只限純文字貼文 |
| 圖片 | JPEG 與 PNG、8 MB 以內、寬 320～1440、比例最多 10:1、sRGB。我們的 IG JPEG 直接可用 |
| 等待 | 官方：建好 container 後平均約等 30 秒再發佈 |
| 發文上限 | 250 則／24 小時（輪播算 1 則） |
| 回覆 | `reply_to_id`；官方寫需為根貼文擁有者，或有 `threads_keyword_search`／`threads_manage_mentions` |
| 刪除 | `DELETE /{threads-media-id}`，需要 `threads_delete`；每天 100 次 |
| token | 短效 1 小時；長效 60 天；`GET /refresh_access_token?grant_type=th_refresh_token`（token 存在滿 24 小時、未過期）；`GET /access_token?grant_type=th_exchange_token&client_secret=…`（短效換長效，只在本機）；60 天沒 refresh 就失效 |

## 還沒驗證（要實測）

1. **每一則都回覆「前一則」，會不會在 Threads 裡形成「新增到串文」那樣的一串**，官方沒有寫。第一次實測用 3 則的測試串文確認，再用 `rollback` 刪掉。
3. 額度查詢端點 `threads_publishing_limit` 的欄位官方頁沒寫；失敗只會在 dry-run 輸出一行說明，不影響發佈。
4. container 的 `status` 值官方沒列全：程式把 `FINISHED`／`PUBLISHED` 視為完成，`ERROR`／`EXPIRED` 視為失敗，其餘繼續等。
5. 圖片的替代文字：官方參數表沒有 `alt_text`，所以 Threads 附圖沒有替代文字。
6. `graph.threads.net` 與 `graph.threads.com` 哪個較穩，實測時確認。

## 已實測驗證（2026-10-07，帳號 @datasciocean）

1. **每則回覆前一則，會形成「同一串」**（人在 Threads app 確認），附圖與連結預覽（`link_attachment`）都正常。
2. `graph.threads.net` + `v1.0` 可用；額度端點 `threads_publishing_limit` 可用：貼文 250、**回覆 1000**／24 小時。
3. Dashboard 產生的 token 是 60 天長效。
4. `DELETE` 需要 `threads_delete`：沒有時回 `HTTP 403｜code 10｜Application does not have permission for this action`，程式會回報並提示，不會假裝成功。
