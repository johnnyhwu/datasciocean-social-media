# Decision Transformer 把強化學習改寫成序列預測：訓練時學「怎麼走與最後拿多少分」的關聯，使用時先設定想要的分數；它的威力在多步決策，單次生成只借得到表層技巧

| 項目 | 內容 |
|---|---|
| 系列 | （獨立貼文） |
| 觀念 | `decision-transformer-reward-conditioning`（卡：`concept-wiki/wiki/concepts/decision-transformer-reward-conditioning.md`） |
| hook 樣態 | 讀者疑問 |
| IG 輪播 | 已發布（9 張） |
| Threads 串文 | 已發布（2 則） |

## 要看／要發的檔案

| 要做什麼 | 打開哪個檔案 |
|---|---|
| 看 IG 每一頁的圖與文字、複製 caption | [`ig/post.md`](ig/post.md)（圖在 `ig/01.png` …） |
| 看 Threads（正文與附圖、最後一則回覆；舊格式是逐張串文） | [`threads/post.md`](threads/post.md) |
| 一眼看全部縮圖 | 下方縮圖，或 [`_build/contact-sheet.png`](_build/contact-sheet.png) |

![縮圖總覽](_build/contact-sheet.png)

## 檢查結果（程式產生）

- 程式 B：9/9 張通過（模板版本 `0efc9af07dff`）
- 程式 A、批次檢查、忠實者與讀者審查的結果不存在發布包裡（審查產出放暫存，不進 repo）；最後確認時由 Claude 在報告中說明

## 已發布

- IG：https://www.instagram.com/p/DevHQBlk2nG/
- Threads：https://www.threads.com/@datasciocean/post/DevHi6skzg5

## 發布後

- 網址與時間由 `--confirm` 自動寫回 `state/`，不用另外記錄
- [ ] 系列其他則發布後，Threads 回補由 Claude 做：`threads_publish.py backfill`（見 `state/backfill.md`）；IG 回補、限時動態、精選集、置頂都不做

## `_build/`（機器用，不用看）

`spec.json`（內容規格，唯一的真相來源）、`checks-b.json`、`alt-text.json`、`html/`、`post-with-refs.md`、`post-reader.md`、`contact-sheet.png`。
改內容請改 `spec.json` 後重跑 `check_a.py` → `render.py` → `build_package.py`。
