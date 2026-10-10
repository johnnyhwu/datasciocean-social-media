---
name: chart-thinking
description: 決定 IG 輪播裡「這一張該用什麼圖、怎麼讓圖直接支撐主標、怎麼評一張圖好不好」。規劃或修改任何帶數字的投影片（橫條圖、成對橫條圖、測深圖、對照表）之前先讀；使用者說圖表不夠好、看不懂、該換圖型時也讀。內含從 OpenAI data-visualization plugin 挑來的選圖、感知與色彩、不確定性、評圖參考資料。
---

# chart-thinking：先想清楚要比什麼，再選圖

本專案的圖是 1080×1350 的靜態圖，由 `make-social-post/scripts/render.py` 依 spec 畫（只有 `chart_bars`、成對的 `chart_bars`、`chart_sounding`、`table` 這幾種），讀者看的是手機上的一張張圖，沒有 hover、沒有圖例以外的說明。**規則（卡是上限、數字有比較對象、圖由程式產生…）全在 `CLAUDE.md`，這裡只講「怎麼想」。**

為什麼有這份：2026-10-10 人看完 `cascade-complementary-errors` 後的回饋——「圖要更謹慎思考，怎樣的 chart 更適合解釋那一頁想傳達的內容，這是現在做的 post 的通病」。第 7 張原本是 4 條單純的橫條（只畫費用，轉出比例藏在副標籤），讀者看不出「費用跟著轉出比例走」。

## 每張圖先回答四件事（寫進版型規劃，`ig-carousel.md` §0）

1. **讀者看完這張要記住的一句話**是什麼？（就是主標，寫成可以被圖證實或推翻的句子。）
2. **要比的是什麼？**哪兩個東西、同一個單位嗎、跟誰比（比較對象）？
3. **圖要直接支撐主標。**主標說的那件事，圖上要看得到。反例：主標寫「不會掉分」，圖卻只畫費用，準確度只出現在補充文字——讀者要靠文字才懂，圖就沒有在做事。做不到就改主標說圖上有的事，或把圖換成能畫出那件事的型態，或把數字放進表。
4. **這張圖少了哪些詞讀者就看不懂？**圖上的名稱、單位、基準的白話說明在哪裡（同一張或更早的張）。

## 這個專案的選圖對照

| 要比的事 | 用什麼 | 備註 |
|---|---|---|
| 一組同單位數字的大小（3～4 項） | `chart_bars` | 軸從 0 起；強調全圖最多一組；`subs_inline` 讓 3 條自動拉開 |
| **同一批對象的兩個量一起看**（例如每個任務的「轉出比例」與「費用」，同單位 %） | `chart_bars` 加 `value2` 與 `legend`（成對橫條圖） | 兩個量共用同一個 0 起點與比例尺，**不用雙軸**；用 `axis_max` 把 100% 當滿格；圖例放在圖上方、色塊與文字貼在一起 |
| 一個量被拆成幾部分（75 題 = 60 題補得回 + 15 題補不回） | `chart_bars`（現行）；之後可考慮堆疊條 | 用名稱與副標籤把「其中」寫出來 |
| 差距要有「水面」感、數值很大且只有 2～3 項 | `chart_sounding` | 只在系列哲學需要時用 |
| 「A 是什麼、B 是什麼」或每列一個完整句子 | `table` | 鍵可寫「主｜小字」，小字當小標；圖放不下的白話解釋放這裡 |
| 兩個**不同單位**的量 | 兩張圖或表，不要共用一條軸 | 上游指南的反面清單明列「雙軸除非有極仔細的說明」。人提過 two-axis，做法是**同單位就成對橫條、不同單位就拆開**，不是畫兩條不同比例尺的軸 |
| 兩個量的關係本身就是重點（斜線、離群點） | 散布圖（目前沒有版型） | 要新增版型照 `design-series-visuals` 流程，程式 B 要補比例檢查；給一般讀者看要先想清楚讀不讀得懂 |

## 一般讀者讀得懂嗎？（人的回饋，2026-10-10）

貼文不是給 AI 或工程師看的，**讀者可能完全沒有 AI 背景**。每張帶數字的圖要通過：

- 圖上的專有名稱（JudgeBench、PPE…）要有白話說明在同一張或更早的張；不能只靠名稱本身。
- 標籤用讀者的話：「轉給 GPT-6 的題數比例」比「轉出率」好；「費用（GPT-6 單獨 = 100%）」比「相對成本」好。
- 數字旁要有單位與比較對象；差距很小時（例如 25% 對 27%），圖上要看得出**是「兩條差不多長」這件事**在說話，補充文字要把這句話明說。
- 寧可文字多一點、好懂，也不要精簡到讀者要猜。

## 不確定性與統計（卡上有區間時）

- 區間、誤差範圍、「不含 0」是統計術語；給一般讀者要用白話（「重算很多次，差距大多是正的」之類）並且**不改變卡的意思**；不要在圖上畫區間，除非先在同一張用一句話定義它。
- 小樣本、不同題數的比較（例如 350 題與 270 題）要明講是不同的題集，不然讀者會覺得數字對不上。
- 不把平均畫成沒有誤差的事實：卡有「看不出差別（區間含 0）」就寫「看不出差別」，不寫「一樣」。

## 顏色角色（沿用系列哲學，不另設色）

中性底色 + 一個主色（teal）+ 一個對照色（深海色）+ 金色只給「全圖唯一要強調的」。成對橫條圖兩個量用 teal 與深海色，**不用金色**，因為金色是強調。圖旁不放遠處的圖例；直接標籤優先，圖例只在兩個量共用同一組名稱時才用，並貼在圖上方。

## 評一張圖（交稿前自己看渲染後的 PNG，再縮到 contact sheet 大小看一次）

照 `upstream/assets/templates/critique-checklist.md` 與 `human-visual-review-checklist.md`，加上本專案的幾題：

1. 只看圖與主標，不看補充，能不能講出結論？
2. 主標說的事，圖上有沒有畫出來？
3. 兩個量的差距是不是被畫成讀者看得出來的樣子（不是 1～2% 的差被畫成幾乎無差別，卻要讀者從中讀出重點）？
4. 有沒有大片空白、標籤擠成一團、數字壓到橫條？（程式 B 擋重疊與不超出版面，但「好不好看」要自己看。）
5. 縮成手機縮圖大小，最重要的那組數字還讀得到嗎？

## 參考資料（`upstream/`，MIT，來源見 `upstream/NOTICE.md`）

| 想知道 | 讀 |
|---|---|
| 怎麼從問題選圖型 | `upstream/references/foundations/task-abstraction-and-chart-selection.md`、`upstream/skills/visualization-strategy-and-critique/references/chart-selection-patterns.md` |
| 人怎麼讀圖、顏色與對比、直接標籤 | `upstream/references/foundations/perception-color-and-encoding.md` |
| 一頁的主從關係、不要用文字補救圖 | `upstream/references/foundations/layout-hierarchy-and-self-explanatory-ux.md` |
| 標題寫成結論、註解怎麼用 | `upstream/references/foundations/storytelling-annotation-and-critique.md`、`editorial-infographic-system.md` |
| 完整的評圖流程與反面清單 | `upstream/skills/visualization-strategy-and-critique/SKILL.upstream.md` |
| 誠實呈現不確定性、缺失、樣本數 | `upstream/skills/statistical-and-uncertainty-visualization/` |
| 色彩與對比、替代文字 | `upstream/skills/accessibility-and-inclusive-visualization/` |
| 圖的簡報單（先寫哪些再畫） | `upstream/assets/templates/chart-brief.md`、`editorial-infographic-brief.md` |

上游資料是為網頁與互動寫的，凡是講 hover、動畫、WebGL、React 的部分不適用；適用的是它的**判斷原則**（先有結論、先選對比較方式、直接標籤、色彩有角色、評圖先看語意再看外觀）。
