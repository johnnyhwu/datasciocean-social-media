# 重製圖審查材料：verifier-expected-value-vs-argmax

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 9 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/verifier-expected-value-vs-argmax/ig/09.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 小標籤：③ 一個案例
  - 主標：同一題評 100 次：Judge 平手 88 次，verifier 0 次
  - 補充：verifier（Gemini 2.5 Flash）其實看出 agent 沒驗證，卻講得像無關緊要；只取機率最高的分數，這個判斷就被壓扁。改算期望值，排對從 12 次升到 69 次；量表再切細，升到 77 次。
  - 示意圖（stack）上的文字與數字：Judge（1 到 5 分，取機率最高）｜verifier（1 到 5 分，期望值）｜verifier（1 到 20 分，期望值）｜排對｜平手｜排錯｜排對 12・平手 88・排錯 0｜排對 69・平手 0・排錯 31｜排對 77・平手 0・排錯 23
  - 圖註：「排對」指正確的那條拿到比較高的分數；每種方法各評 100 次。

### 原圖 llm-as-a-verifier/table2.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/table2.png
- blog 圖說原文（不是主張）：圖 4 — 同一個任務跑一百次：離散 judge 有 88 次無法區分，連續 verifier 一次都沒有。（來源：原始論文 Table 2。）
- 附這張圖的主張：c17, c18

### 這張引用的主張（圖要以它們為準）
- **c4**（原作者解讀）：模型在輸出分數的那個 token 位置，內部產生的是一個完整的機率分佈（每個分數各有多大機率），但標準做法只取機率最高的那一個（argmax），其餘全丟；資訊不是模型沒產生，是解碼策略把它丟掉的
- **c16**（部落格推論）：在這個案例裡，verifier（Gemini 2.5 Flash）其實有看出 agent 修改了資料庫來取得參考輸出、並未正確驗證等價性，卻用帶保留、程度性的措辭表達，講得像無關緊要；模型內部有正確判斷，但這個判斷在 argmax 那一步被壓扁了
- **c17**（實驗結果）：同一個 query-optimize 任務，每種方法各評分一百次（正確軌跡分數高於錯誤軌跡／平手／低於）：離散 judge（G=5）是 12/88/0；連續 verifier（G=5）是 69/0/31；連續 verifier（G=20）是 77/0/23
- **c18**（部落格判斷）：這個對照設計很乾淨，因為一次只動一個變因：同一個 1–5 量表只換解碼方式（argmax → 期望值），88 次平手歸零、正確排序從 12 上升到 69；同樣是期望值只換量表（1–5 → 1–20），正確排序從 69 上升到 77

## 第 14 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/verifier-expected-value-vs-argmax/ig/14.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 小標籤：④ 三個旋鈕
  - 主標：Judge 問到 16 次，平手還剩 5.5%
  - 補充：多問幾次，Judge 的平手從 26.7% 降到 5.5%；verifier 問 1 次和 16 次，平手是 0%。Judge 的進步主要靠平均打破平手，像用重複測量補一把太粗的尺；verifier 是直接換一把細的。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：Judge 問 1 次｜｜26.7 %
  - 圖表項目：Judge 問 16 次｜｜5.5 %｜強調
  - 圖註：長條是 Judge 的平手率：兩條軌跡拿到一樣分數的比例。

### 原圖 llm-as-a-verifier/figure7.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/figure7.png
- blog 圖說原文（不是主張）：圖 5 — 拉高重複次數，judge 的平手率從 26.7% 掉到 5.5%，但準確率幾乎沒動；verifier 從頭到尾零平手。（來源：原始論文 Figure 7。）
- 附這張圖的主張：verifier-three-knobs-g-k-c:c11

### 這張引用的主張（圖要以它們為準）
- **verifier-three-knobs-g-k-c:c11**（實驗結果）：拿離散 judge 和 verifier 在不同重複次數下對照：K=1 時 judge 準確率 71.8%、平手率 26.7%，verifier 準確率 74.7%、平手率 0.0%；K=16 時 judge 準確率 74.7%、平手率 5.5%，verifier 準確率 77.5%、平手率 0.0%
- **verifier-three-knobs-g-k-c:c13**（部落格推論）：judge 靠重複評估得到的改善，主要機制是用平均打破平手（平手率 26.7% → 5.5%），而不是真的變會判斷；就像用重複測量去彌補一把刻度太粗的尺，而 verifier 是直接換一把刻度細的
- **c1**（原作者解讀）：LLM 打分數時內部的信念是連續的，是 argmax 把它壓扁的；把 argmax 換成期望值，平手率從 27% 降到 0%，排序能力就回來了
  - 限定條件 c1#1：27% 是論文在 Terminal-Bench 上量到的比較結果平手比例
  - 限定條件 c1#2：verifier 的 0% 平手，是在同一個 query-optimize 任務各評分一百次（平手 0/100），以及不同重複次數下的平手率對照（verifier 平手率 0.0%）中量到的
  - 限定條件 c1#3：不同重複次數下，verifier 的平手率都是 0.0%（K=1 時 judge 平手率 26.7%）
  - 限定條件 c1#4：代價是被迫每次表態：在同一個 query-optimize 任務各評分一百次，離散 judge 的排錯次數是 0/100，連續 verifier 消除平手後，其中二三成表錯了
  - 限定條件 c1#5：表錯的實際次數是 verifier（G=5）31/100、verifier（G=20）23/100

## 第 15 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/verifier-expected-value-vs-argmax/ig/15.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 小標籤：④ 三個旋鈕
  - 主標：verifier 問 1 次＝Judge 問 16 次？有點誇大
  - 補充：論文說 verifier 問 1 次就追平 Judge 問 16 次（都是 74.7%），像省 16 倍。但兩種次數下 verifier 都只高 2.7% 到 2.9%；省 16 倍只在目標剛好是 74.7% 時成立。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：問 1 次｜｜Judge 準確率 71.8 %｜verifier 準確率 74.7 %
  - 圖表項目：問 16 次｜｜Judge 準確率 74.7 %｜verifier 準確率 77.5 %
  - 圖註：簡化重畫，沒畫原圖的誤差範圍；每組兩條長條只差 2.7% 到 2.9%。

### 原圖 llm-as-a-verifier/figure7.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/figure7.png
- blog 圖說原文（不是主張）：圖 5 — 拉高重複次數，judge 的平手率從 26.7% 掉到 5.5%，但準確率幾乎沒動；verifier 從頭到尾零平手。（來源：原始論文 Figure 7。）
- 附這張圖的主張：verifier-three-knobs-g-k-c:c11, verifier-three-knobs-g-k-c:c12

### 這張引用的主張（圖要以它們為準）
- **verifier-three-knobs-g-k-c:c11**（實驗結果）：拿離散 judge 和 verifier 在不同重複次數下對照：K=1 時 judge 準確率 71.8%、平手率 26.7%，verifier 準確率 74.7%、平手率 0.0%；K=16 時 judge 準確率 74.7%、平手率 5.5%，verifier 準確率 77.5%、平手率 0.0%
- **verifier-three-knobs-g-k-c:c12**（原作者解讀）：論文想讓人看的是對角線：verifier 只跑 1 次（74.7%）就等於 judge 跑 16 次（74.7%）
  - 限定條件 verifier-three-knobs-g-k-c:c12#1：「16 倍運算」這個對比有點誇大：judge 和 verifier 在每個 K 下的差距都落在 2.7 到 2.9pp 之間，那個對比只在剛好只在乎「追平 74.7%」這個門檻時才成立

## 第 16 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/verifier-expected-value-vs-argmax/ig/16.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 小標籤：④ 三個旋鈕
  - 主標：把「對不對」拆成三個標準分開評
  - 補充：在長流程的 agent 任務裡，「這條軌跡正確嗎？」混了好幾個獨立的因素，verifier 往往只抓住最顯眼的那一個。所以論文替 code agent 拆出三個子準則分開評，合起來比只看其中任何一個準一點。
  - 示意圖（fan）上的文字與數字：三個子準則：Specification、Output、Errors｜三個合起來：78.3%｜比最好的單一準則多 1.9%｜滿足所有要求
75.2%｜輸出格式對嗎
76.4%｜有失敗訊號嗎
76.0%
  - 圖註：簡化重畫：數字是各標準單獨評的準確率；1.9% 可不可信，下一張說。

### 原圖 llm-as-a-verifier/figure4.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/figure4.png
- blog 圖說原文（不是主張）：圖 3 — 驗證準確率沿著三個維度都會上升：分數粒度、重複次數、準則拆解。（來源：原始論文 Figure 4。）
- 附這張圖的主張：verifier-three-knobs-g-k-c:c16

### 這張引用的主張（圖要以它們為準）
- **verifier-three-knobs-g-k-c:c15**（設計參數）：第三個旋鈕是準則拆解 C，對付的是評分標準本身不合理：在長時序的 agent 任務裡，「這條軌跡正確嗎？」把好幾個邏輯上獨立的因素混在一起，verifier 往往只抓住 prompt 裡最顯眼的那一個；論文對 code agent 拆出三個子準則：Specification（有沒有滿足任務的所有要求）、Output（最終輸出格式是否符合預期）、Errors（log／工具輸出有無失敗訊號）
- **verifier-three-knobs-g-k-c:c16**（實驗結果）：單一準則的準確率是 Specification 75.2%、Errors 76.0%、Output 76.4%，三者 ensemble 是 78.3%
  - 限定條件 verifier-three-knobs-g-k-c:c16#1：圖裡誤差棒重疊得很明顯，1.9pp 的改善沒做顯著性檢定，也沒說明誤差棒代表什麼
