# 來源

這個資料夾是從 OpenAI 的 `openai/plugins` repo 的 `plugins/build-web-data-visualization` 挑出來的幾份資料，**原文未改**（授權：MIT，見該 plugin 的 `plugin.json`）。

- 網址：https://github.com/openai/plugins/tree/0722921d5542fc593105c27bd52630babd8b8c2a/plugins/build-web-data-visualization
- commit：`0722921d5542fc593105c27bd52630babd8b8c2a`
- 取用日期：2026-10-10

挑選原則：本專案出的是 **1080×1350 的靜態圖**（IG 輪播），圖由 `render.py` 用 HTML 與 SVG 畫，不寫 D3、React、Canvas、WebGL，也不做互動；所以只留跟「選什麼圖、怎麼讓圖支撐結論、怎麼評圖、怎麼誠實呈現不確定性、色彩與對比」有關的部分。

沒有收進來的：D3、Canvas2D、Three.js、React／Next.js、TypeScript 工程、地圖、儀表板、甘特圖、UML、捲動敘事、測試、報表與簡報匯出（和靜態圖無關）。

檔名調整：各 skill 的 `SKILL.md` 改名為 `SKILL.upstream.md`（避免被當成本 repo 的 skill 載入）；`agents/openai.yaml`（Codex 設定）已移除。檔案內互相引用的路徑（例如 `../SKILL.md`、`d3-data-visualization/…`）有些指向沒收進來的檔案，讀的時候略過即可。
