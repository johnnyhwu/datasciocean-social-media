# Bradley-Terry 把兩兩比較看成每個項目隱藏「實力值」的機率反映，是 RLHF reward model 的共同底層；成對比較比直接打分共識度高，但有傳遞性假設的缺陷

| 項目 | 內容 |
|---|---|
| 系列 | （獨立貼文） |
| 觀念 | `bradley-terry-pairwise-preference`（卡：`concept-wiki/wiki/concepts/bradley-terry-pairwise-preference.md`） |
| hook 樣態 | 反直覺斷言 |
| IG 輪播 | 已發布（12 張） |
| Threads 串文 | 已發布（2 則） |

## 要看／要發的檔案

| 要做什麼 | 打開哪個檔案 |
|---|---|
| 看 IG 每一頁的圖與文字、複製 caption | [`ig/post.md`](ig/post.md)（圖在 `ig/01.png` …） |
| 看 Threads（正文與附圖、最後一則回覆；舊格式是逐張串文） | [`threads/post.md`](threads/post.md) |
| 一眼看全部縮圖 | 下方縮圖，或 [`_build/contact-sheet.png`](_build/contact-sheet.png) |

![縮圖總覽](_build/contact-sheet.png)

## 檢查結果（程式產生）

- 程式 B：12/12 張通過（模板版本 `d69306c525a5`）
- 程式 A、批次檢查、忠實者與讀者審查的結果不存在發布包裡（審查產出放暫存，不進 repo）；最後確認時由 Claude 在報告中說明

## 已發布

- IG：https://www.instagram.com/p/De0b1Udnw6Z/
- Threads：https://www.threads.com/@datasciocean/post/De0cNARn6v9

## 發布後

- 網址與時間由 `--confirm` 自動寫回 `state/`，不用另外記錄
- [ ] 系列其他則發布後，Threads 回補由 Claude 做：`threads_publish.py backfill`（見 `state/backfill.md`）；IG 回補、限時動態、精選集、置頂都不做

## `_build/`（機器用，不用看）

`spec.json`（內容規格，唯一的真相來源）、`checks-b.json`、`alt-text.json`、`html/`、`post-with-refs.md`、`post-reader.md`、`contact-sheet.png`。
改內容請改 `spec.json` 後重跑 `check_a.py` → `render.py` → `build_package.py`。
