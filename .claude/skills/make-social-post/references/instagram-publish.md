# 用 Instagram 官方 API 發佈（Instagram API with Instagram Login）

走 Meta 官方 API（host: `graph.instagram.com`，Instagram User access token，**不需要** Facebook Page），不使用任何第三方封裝服務。

**規則**：預設 dry-run；要實際發佈必須由人明確確認後才加 `--confirm`（CLAUDE.md 規則 9）。token 只放 `.env`，不得出現在聊天、log、錯誤訊息、commit。Threads 的設定與發佈見 `threads-publish.md`；**兩個平台從頭到尾的發布程序見 `publish-flow.md`**（照那份做）。

## 一次性設定（人做）

依官方文件 `instagram-api-with-instagram-login/get-started`；實際畫面可能略有不同，以 Meta 的畫面為準。

1. 確認 IG 帳號是**專業帳號**（Business 或 Creator）。
2. 到 developers.facebook.com 建 App，類型選 **Business**；加入 Instagram 產品，進「API setup with Instagram business login」。
3. 在「Generate access tokens」區塊加入你的 IG 帳號（要登入 IG 並授權），按帳號旁的 **Generate token**，得到 **60 天長效** token（只顯示一次）。
4. 複製 `.env.example` 成 `.env`，把 token 貼進 `IG_ACCESS_TOKEN=`。**不要把 token 貼進聊天。** 若 token 取得當下你記得時間，也可填 `IG_TOKEN_REFRESHED_AT`。
5. 驗證：`uv run python .claude/skills/make-social-post/scripts/ig_publish.py whoami`。成功會印出 username，並把 `IG_USER_ID` 寫進 `.env`。

權限（Instagram Login）：`instagram_business_basic`、`instagram_business_content_publish`。自己的帳號、自己的 App：官方寫 **App Review 不需要，Standard Access 即可**。

**還沒驗證**：App 在 Development 模式時，帳號是否要先被加進 App 角色／測試人員，官方沒有講；若 `whoami` 失敗，先查這個。

## 流程（API 沒有草稿功能，「預檢」是最接近的替代）

官方文件與 `POST /<IG_ID>/media` 的完整參數表裡，**沒有草稿、排程、在 IG app 預覽、或用 API 刪除貼文的功能**（第三方文章提到的 `scheduled_publish_time` 官方參數表沒有，不採信）。所以流程是：

```
prepare   → 發布包的 ig/NN.png 轉成 ig/jpg/NN.jpg（sRGB、品質 95），並驗證官方限制
commit + push ig/jpg/        （託管是這個公開 repo 的 raw 網址，圖一定要先 push，Meta 才抓得到）
preflight → 預檢：建好每張的 container 與 carousel container、等到 FINISHED，但「不發佈」
            （貼文不會出現在帳號上，IG app 裡也看不到；container 24 小時後自動過期）
            結果記在 _build/ig-prepared.json（不進 git）
人看 ig/post.md 確認
publish   → dry-run：印出將送出的請求、檢查網址與額度、報告預檢能不能沿用
人說「發」
publish --confirm → 預檢在 23 小時內、內容指紋沒變、container 仍是 FINISHED → 直接 media_publish（只送一個 POST）
                    否則（過期、改過內容、不是 FINISHED、加了 --no-reuse）→ 重新建 container 再發
                    → 取 permalink → state.py record（格式變 published）→ 寫 state/ig-publish-log.jsonl（media id、時間；不含 token）
```

預檢檢查的是 **Meta 那一邊**的事：Meta 的伺服器抓得到圖片網址嗎？接受這些 JPEG 嗎？替代文字與 caption 被接受嗎？沒過就在這步出錯，還沒有任何東西發出去。它不花發文額度（官方的 `quota_usage` 算的是「發佈」次數）。

指令見 `scripts/ig_publish.py` 開頭。其他：`limit`（查 `content_publishing_limit`）、`token-status`、`refresh-token`、`whoami [--no-write]`、`publish-image`（單張）。第一次實測的測試貼文用 `--no-record`。

## 官方限制（已查證；來源是官方文件的 `.md` 頁面）

| 項目 | 內容 |
|---|---|
| 圖片 | 只支援 **JPEG**（MPO、JPS 不支援）；8 MB 以內；寬 320～1440；比例 4:5～1.91:1；sRGB。我們的 1080×1350 剛好是 4:5 下限 |
| 圖片網址 | 必須是公開、不需登入、可直接下載、**不帶 query 參數**；Meta 自己去抓。**圖片沒有「直接上傳本機檔案」的方式**（`rupload` 只文件化了影片） |
| 輪播 | 最多 10 張（實測 4:5 不會被裁）；`is_carousel_item=true` 的子項各建一個 container，再建 `media_type=CAROUSEL`、`children=…` 的 container；**caption 只放在 carousel container**，子項不支援 |
| alt_text | 單圖與輪播每張圖都支援 `alt_text` |
| is_ai_generated | 輪播只能設在 carousel container，子項會報錯。專案規則 10：預設不加（`IG_AI_GENERATED=false`） |
| caption | 最多 2200 字元、30 個 hashtag、20 個 @tag |
| container 狀態 | `IN_PROGRESS`、`FINISHED`、`ERROR`、`EXPIRED`、`PUBLISHED`；24 小時沒發佈就 EXPIRED；官方建議**每分鐘查一次，最多 5 分鐘** |
| 發文上限 | 官方各頁說法不一致（25、50、100 都出現）。不寫死，發文前用 `content_publishing_limit` 查 |
| token | 長效 60 天；`GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token`；token 存在滿 24 小時、未過期才能 refresh；60 天沒 refresh 就失效且無法再 refresh |
| 錯誤碼 | 9004（抓不到圖）、9007（容器還沒 FINISHED）、9（超過發文上限）、36000（圖太大）、36001（格式不支援）；token 過期（190）官方錯誤碼頁沒列 |

## 已實測驗證（2026-10-07，帳號 @datasciocean）

1. **4:5 的輪播不會被裁成 1:1。** 發了一則 3 張（1080×1350）的測試輪播，人在 IG app 確認上方系列標籤與下方 `@datasciocean` 都完整保留。所以版面的上下邊緣不需要為 1:1 預留安全區。
2. **自己的帳號、自己的 App，不需要額外設定角色**：用 Dashboard 產生的 token，`whoami`、建立 container、發佈都成功。（App 當時是不是 Development 模式我沒有查證。）
3. **Meta 抓得到 `raw.githubusercontent.com` 的圖**（公開 repo、JPEG、無 query 參數）。
4. 預檢建的 container 可以直接沿用於 `media_publish`，只送一個請求。

## 還沒驗證

1. API 能不能刪除或封存貼文：官方文件沒寫；發現錯誤時只報告給人，由人決定要不要處理（測試貼文曾由人手動封存）。
2. 官方各頁對發文上限的說法不一致；實際帳號 `content_publishing_limit` 回報上限 100／24 小時，用量 0。

## 錯誤處理

| 情況 | 做法 |
|---|---|
| 暫時性錯誤（網路、HTTP 5xx、code 1／2） | 最多重試 3 次，指數退避 |
| 9004、9、190、其他 | 不重試，印出錯誤與提示 |
| 9007 | 不是重試，是輪詢到 FINISHED 才發佈 |
| 已發布過（state 是 `published`） | 拒絕再發 |
| 圖片網址抓不到（常見：還沒 push） | 不發，列出哪張的網址不能用 |

## 限時動態（Stories）：研究結論（2026-10-07，尚未實作）

官方 `POST /<IG_ID>/media` 參考頁：`media_type=STORIES` 可以發限時動態，**但：**

| 項目 | 結果 |
|---|---|
| 圖片規格 | JPEG、8 MB 以內、sRGB；建議 9:16（否則會裁切或留白）。我們的版型是 4:5，要發 Stories 需要另做 9:16 的版型 |
| 可用參數 | `image_url`（或 `video_url`）、`user_tags`（標記帳號與座標）。**沒有 `caption`、`alt_text`** |
| **連結貼紙** | **不支援。** 官方寫「Publishing stickers (i.e., link, poll, location) is not supported」；互動貼紙只能在 app 內加 |
| 其他 | 提及帳號可以（用 `user_tags`，不是貼紙）；不支援 `collaborators`；是否計入發文額度、Stories 的存在時間，官方頁沒寫（一般是 24 小時） |

**結論**：我們限時動態的目的是「加連結貼紙指向文章」，API 做不到；人也不手動做（2026-10-10 決定），所以**不做限時動態**，也不提醒。要不要做 9:16 版型的純圖限時動態，是另一件事，需要人決定。精選集與置頂同樣不做。
