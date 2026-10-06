# 內容規格 JSON（`out/<series>/<concept>/_build/spec.json`）

LLM 只產出這份 JSON；外觀完全由模板決定。範例：`out/jev-cascade/jev-cascade-overview/_build/spec.json`（現行完整範例）。

## 頂層

```json
{
  "series": "jev-cascade",            // series/<id>/series.md；獨立 post 沒有系列
  "concept": "confound-three-questions",
  "lang": "zh-TW",
  "status": "draft",
  "hook": { "style": "反直覺斷言", "title": "快 [[193.6 倍、25 倍、約 5 倍]]？", "subtitle": "…",
            "refs": ["c3", "c5"], "candidate": "B4" },
  "slides": [ … ],
  "threads": { … },
  "caption": { … }
}
```

- `[[…]]` 在主標與 hook 標題裡標出要用金色螢光筆畫底的關鍵字；渲染、替代文字與 caption 會自動去掉括號。
- `hook.style` 是 hook 樣態（見 `hooks.md`），寫回狀態時要記錄；`hook.candidate` 是人挑的候選編號。

## 引用標記（每個區塊都要有）

每張投影片、hook、Threads 的正文／每則串文／最後一則、caption 第一句，都要有：

| 欄位 | 內容 |
|---|---|
| `refs` | 這個區塊引用卡上哪幾條主張（claim id，例如 `["c3", "c5"]`）。純結構文字（轉場、系列地圖）寫 `["結構"]` |
| `quals` | 這個區塊帶出的限定條件，格式 `"c3#1"`（c3 的第 1 條 `qualifiers`）。被使用的主張的所有限定條件，必須在整則貼文某處出現 |

caption 第一句用 `first_refs`。`refs` 只證明「有對應」，不證明意思沒走樣；走樣由忠實者判斷。

## slides[]

共同欄位：`layout`、`title`（主標，結論句）、`body`（補充）、`refs`、`quals`。

| layout | 用途 | 專屬欄位 |
|---|---|---|
| `cover` | 第 1 張 | `title`（hook 主標）、`body`（hook 副標） |
| `context` | 第 2 張，純文字，三句以內 | `body` 最多 90 字 |
| `text` | 機制、限制、評價 | `body` 40～60 字 |
| `table` | 兩欄對照（最多 3 列） | `rows: [["鍵","值"], …]`、`note`（選用，圖註）；`body` 一行（約 24 字內） |
| `chart_bars` | 橫條圖（米色底） | `unit`、`bars`、`note`；`body` 一行 |
| `chart_sounding` | 測深圖（深色海面面板，最多 3 條繩） | `unit`、`bars`、`note`；`body` 一行 |
| `takeaway` | 倒數第二張，深海底金色字，一句話 | `title`（一句話，字最大）、`label`（選用，例如「我的判斷」） |
| `series_map` | 最後一張（獨立 post 為「延伸閱讀」） | `current`（本則的 concept id）、`nav`（導流行）；標題清單由系列檔的 `planned_title` 自動填，不要自己寫 |

`bars[]` 的每一項：`{"name": "官網頭條", "subs": ["速度，最佳案例", "對比前沿大模型"], "value": 193.6, "emphasize": true}`。`emphasize` 全圖只能有一個；圖上所有名稱與數字都要被引用的主張涵蓋；軸從 0 起，長度與數值成正比（由程式計算）。

## threads

```json
{
  "body":  { "text": "…", "refs": ["c3"], "quals": ["c3#1"] },
  "items": [ { "slide": 4, "text": "…", "refs": ["c15"] } ],     // 內容投影片一對一
  "last":  { "text": "帶走一句話\n文章：datasciocean.com/…\n同系列：<planned_title>（尚未發布）",
             "refs": ["c1", "c2"], "link": "https://datasciocean.com/ai-concept/<slug>/" }
}
```

## caption

```json
{ "first": "第一句（含搜尋關鍵字）", "first_refs": ["c1"],
  "nav": "導流行", "hashtags": ["DSO_Jev", "benchmark", "LLM"] }
```

逐張摘要不放進 JSON，由 `build_package.py` 依最終投影片自動產生（所以必須在張數定案之後才跑）。

## 發布包結構（`out/<series>/<concept>/`）

```
README.md          這則貼文的唯一入口：縮圖、檢查結果、發布前後待辦        build_package.py
ig/post.md         每一頁的圖與文字、替代文字，最後是整段 caption           build_package.py
ig/01.png …        投影片                                                    render.py
threads/post.md    正文、每則串文（附圖，圖在 ../ig/）、最後一則            build_package.py
_build/            機器用，不用看
  spec.json        內容規格（唯一的真相來源）                                人／撰寫者寫
  checks-b.json    程式 B 結果與 template_hash；alt-text.json；html/          render.py
  post-with-refs.md、post-reader.md   審查者用                              build_package.py
  contact-sheet.png                                                          contact_sheet.py
```
另有索引 `out/README.md` 與 `out/<series>/README.md`（`build_package.py` 重新產生，不手改）。
