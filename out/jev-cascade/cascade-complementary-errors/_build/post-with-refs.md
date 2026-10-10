# 貼文：cascade-complementary-errors（zh-TW）

## IG 輪播（共 10 張）

### 第 1 張
版型：cover
主標：想用便宜的 Judge 幫 GPT-6 省錢？得先闖兩關！
補充：第一關 → 兩個 Judge 得錯在不同的題，不然 GPT-6 也補不回來
第二關 → 丟給強的 Judge 的門檻要設對，設太鬆也可能會掉分。
引用：c1, c12, cascade-threshold-and-failure-mode:c1, cascade-threshold-and-failure-mode:c13

### 第 2 張
版型：context
主標：串接：便宜的 Judge 先擋，沒把握才轉出去
補充：下面三個詞，後面會一直用到：
表列：Judge｜請一個 AI 評另一個 AI 的回答。JEV 是 TypeSafe AI 的託管模型，便宜又快，只輸出判決和機率
表列：信心 q｜JEV 對每個答案各給一個機率，q 是最高的那個，也就是它對自己所選答案的把握
表列：門檻 τ｜放行線：q 達到 τ 就用 JEV 的答案，低於 τ 就轉給強的 Judge。τ 設得越高，轉出越多
引用：c2, c3, c4, c5, cascade-threshold-and-failure-mode:c2

### 第 3 張
版型：table
小標籤：第一關
主標：第一關：兩個 Judge 要錯在不同的題
補充：串接能成立的前提：兩個 Judge 要錯在不同的題，這樣轉出去才補得回來。
表列：錯在不同的題｜便宜的 Judge 答錯的題，強的 Judge 大多答對，轉出去就能補回來
表列：兩邊都錯｜兩個 Judge 剛好栽在同一題，轉給強的 Judge 也還是錯，怎麼轉都修不回來
表列：天花板｜所以串接的上限，看的是「兩邊共同錯的題有幾題」，不是強的 Judge 自己有多準
圖註：提醒：串接有很多種設計，論文只實測了這一種，這則講的就是它
引用：c1, c9｜帶出限定條件：c1#1, c9#1

### 第 4 張
版型：chart_bars
小標籤：第一關
主標：共同錯只有 15 題，串接上限比 GPT-6 還高
補充：如果有個完美的挑題員，每題都挑到比較對的那一個，準確度可達 95.7%，高於 GPT-6 單獨的約 93%。但這只是上限，不是實際分流的結果。
圖表單位：題（軸從 0 起；繩長或橫條長度與數值成正比）
圖表項目：JEV 答錯｜350 題裡｜75 題
圖表項目：其中 GPT-6 答對｜｜60 題
圖表項目：兩邊共同錯｜轉也修不回來｜15 題｜強調
圖註：JudgeBench 全部 350 題（原順序判斷）
引用：c6, c7｜帶出限定條件：c7#1, c7#2

### 第 5 張
版型：table
小標籤：第一關
主標：實測：換一份題庫，省錢的程度差很多
補充：RewardBench 與 JudgeBench 是兩組不同的題目。費用以 GPT-6 單獨為 100%；JudgeBench 這裡用的是留作驗收的 270 題。
表列：RewardBench｜只轉 25% 的題｜費用只要 27%，準確度還稍微贏過 GPT-6（多 1.27%）
表列：JudgeBench｜要轉 65% 的題｜費用 67%，只省了三分之一；準確度和 GPT-6 看不出差別，是因為 65% 的題交給了 GPT-6 重判
表列：略勝的原因｜兩個 Judge 錯在不同的題，串接等於各挑了擅長的部分
引用：c12, c13, c14, c6｜帶出限定條件：c6#1

### 第 6 張
版型：table
小標籤：第二關
主標：第二關：門檻 τ 不能照抄，要自己重選
補充：換掉便宜的 Judge、強的 Judge 或任務，τ 都要用自己有標準答案的題重選。
表列：怎麼選｜拿有標準答案的題把串接模擬一遍，挑「最省錢、準確度比強的 Judge 單獨掉不超過 2%」的 τ
表列：誰決定｜「可以掉 2%」是使用者自己訂的容忍度，不是模型替你算出來的
表列：論文的做法｜試 7 個候選值（0.5 到 0.99），用 96 題挑好就固定。對 GPT-6 挑到 τ = 0.9
引用：cascade-threshold-and-failure-mode:c1, cascade-threshold-and-failure-mode:c5, cascade-threshold-and-failure-mode:c6｜帶出限定條件：cascade-threshold-and-failure-mode:c5#1

### 第 7 張
版型：chart_bars
小標籤：第二關
主標：門檻選對，失敗時只變貴、不掉分
補充：後兩個是 JEV 本來就弱的新任務，準確度和 GPT-6 完全一致，代價是費用接近 GPT-6 單獨。小字是準確度（串接減 GPT-6）。
圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
圖表項目：RewardBench｜準確度 +1.27%｜轉給 GPT-6 的題數比例 25 %｜費用（GPT-6 單獨 = 100%） 27 %
圖表項目：JudgeBench｜準確度 −0.74%｜轉給 GPT-6 的題數比例 65 %｜費用（GPT-6 單獨 = 100%） 67 %
圖表項目：PPE｜準確度和 GPT-6 一致｜轉給 GPT-6 的題數比例 68 %｜費用（GPT-6 單獨 = 100%） 69 %
圖表項目：JudgeBench Claude｜準確度和 GPT-6 一致｜轉給 GPT-6 的題數比例 89 %｜費用（GPT-6 單獨 = 100%） 91 %
圖註：對照組是低推理強度的 GPT-6，不是它的最強設定
引用：c12, c14, cascade-threshold-and-failure-mode:c10, cascade-threshold-and-failure-mode:c9｜帶出限定條件：cascade-threshold-and-failure-mode:c10#3, c12#2, c14#1

### 第 8 張
版型：table
小標籤：第二關
主標：門檻設太鬆，GPT-5.6 Sol 就掉分了
補充：同一套規則，換成 GPT-5.6 Sol 就出事了：在 JudgeBench 上，串接的準確度比它單獨作答還低。
表列：沒出事｜GPT-5.4、GPT-6 各挑到 τ = 0.90，串接跟自己單獨比，差距在 −0.74% 到 +1.27% 之間
表列：出事了｜GPT-5.6 Sol 挑到較鬆的 τ = 0.70，在 JudgeBench 掉了 4.81%，超過說好的 2% 容忍度
表列：為什麼｜論文說：挑 τ 的 96 題裡只有 32 題是 JudgeBench，其餘是放寬很安全的 RewardBench，所以選到偏鬆的 τ
引用：cascade-threshold-and-failure-mode:c12, cascade-threshold-and-failure-mode:c13, cascade-threshold-and-failure-mode:c14｜帶出限定條件：cascade-threshold-and-failure-mode:c1#1, cascade-threshold-and-failure-mode:c10#1

### 第 9 張
版型：takeaway
先問的問題：便宜的 Judge 想幫 GPT-6 省錢，要先過哪兩關？
主標：第一關：兩個 Judge 要錯在不同的題
第二關：門檻要選對，選錯可能掉分
引用：c1, cascade-threshold-and-failure-mode:c1

### 第 10 張
版型：series_map
主標：一次看完這個系列
導流行：完整文章：datasciocean.com/paper-intro/jev-as-a-judge
引用：結構

## Threads 串文

### 正文
想用便宜的 Judge 幫 GPT-6 省錢？得先闖兩關！
➡️ 第一關：兩個 Judge 得錯在不同的題，不然 GPT-6 也補不回來
➡️ 第二關：丟給強的 Judge 的門檻要設對，設太鬆也可能會掉分

做法是便宜的 Judge 先判全部的題，沒把握的才轉給強的 Judge。拿 JudgeBench 全部 350 題來看，JEV 錯 75 題，GPT-6 答對其中 60 題，剩下 15 題兩邊都錯，怎麼轉都修不回來。

先說明一下：串接有很多種設計，這裡講的是論文實測的這一種，別的設計論文沒有測。
引用：c1, c6, cascade-threshold-and-failure-mode:c1｜帶出限定條件：c1#1

### 串文 1（配第 3 張圖）
用考試來想：兩個人如果錯的是同一題，找第二個人來檢查也沒用；兩個人各有各的弱點，才有互補的價值。這也是為什麼評估串接，不能只看強的 Judge 本身多厲害，還要看便宜的 Judge 錯的題，它補得回幾題。
引用：c1, c9

### 串文 2（配第 4 張圖）
反過來算也對得上：GPT-6 答錯 24 題，JEV 答對其中 9 題，兩邊共同錯的還是那 15 題，就是串接補不回來的部分。95.7% 是有完美挑題員才有的上限，實際分流的成績，看下一張的實測。
引用：c6, c7

### 串文 3（配第 5 張圖）
先看 RewardBench 略勝的幅度：串接減 GPT-6 是 +1.27%，誤差範圍 [0.45, 2.03]，區間不含 0（整段大於 0），所以這個略勝是真的。不過有兩點要小心。第一，JEV 有沒有事先看過這些測試題當訓練資料，論文並不知道，就像考前有沒有看過考古題一樣，所以「JEV 在 RewardBench 追平 GPT-6」這類結果，無法排除訓練重疊。第二，拿來比的 GPT-6 用的是低推理強度的設定，不是它的最強設定。另外，這張的 JudgeBench 用 270 題，只是第 4 張那 350 題裡留作驗收的一部分，所以準確度數字不同。
引用：c12

### 串文 4（配第 6 張圖）
為什麼不能照抄？因為 τ 是三樣東西一起決定的：便宜的 Judge、強的 Judge、任務。論文對 GPT-6 選出的 0.9，只是其中一組的答案。
引用：cascade-threshold-and-failure-mode:c1, cascade-threshold-and-failure-mode:c6

### 串文 5（配第 7 張圖）
為什麼門檻選對時，失敗只是變貴？因為串接的規矩是 q 低就轉給強的 Judge：JEV 越不確定，轉出的題越多，最後的答案就越接近強的 Judge 單獨作答。兩個新任務是先把流程固定好再測的：每個任務抽 100 題當練習題，用保守的規則挑門檻，再即時跑剩下的題。練習題上 JEV 比 GPT-6 差 12.5%（PPE）和 17%（JudgeBench），所以規則挑了很嚴的門檻，PPE 是 0.95、JudgeBench 是 0.99。這個實驗只說明規則在弱任務上夠嚴、不會掉分，不代表串接在弱任務上很划算。
引用：cascade-threshold-and-failure-mode:c9, cascade-threshold-and-failure-mode:c10, cascade-threshold-and-failure-mode:c11, cascade-threshold-and-failure-mode:c16

### 串文 6（配第 8 張圖）
GPT-5.6 Sol 在 JudgeBench 掉了 4.81%，誤差範圍是 [−8.52, −1.48]，整段都是負的，所以不是運氣。原因是它在 JudgeBench 只轉出 28.5% 的題，漏掉太多 JEV 會錯的題。還有一種例外要小心：沒有證據可以對照的任務，強的 Judge 自己也近乎亂猜，轉出去不會變好，所以「失敗只是變貴」在那裡也不成立。那組任務只有 200 題，論文自己說只能證明結果跟任務有關，不能說差別純粹來自有沒有證據。
引用：cascade-threshold-and-failure-mode:c1, cascade-threshold-and-failure-mode:c9, cascade-threshold-and-failure-mode:c13

### 最後一則（置頂）
便宜的 Judge 想幫 GPT-6 省錢，要先過兩關：兩個 Judge 得錯在不同的題，門檻也要用自己的題選對。選對時，失敗只是變貴；選錯，可能掉分。
文章：datasciocean.com/paper-intro/jev-as-a-judge
同系列：便宜的 Judge 先判，沒把握才轉給 GPT-6
https://www.threads.com/@datasciocean/post/DeMHNAeEzm2
同系列：Judge 能不能用，先問答案能不能讀出來或核對
https://www.threads.com/@datasciocean/post/DeNyxyxmAFX
引用：c1, cascade-threshold-and-failure-mode:c1

## IG caption

LLM Judge 串接怎麼設計：便宜的 Judge 先判、GPT-6 補位，什麼條件下才省錢？

・第一關：兩個 Judge 要錯在不同的題
・第一關：共同錯只有 15 題，串接上限比 GPT-6 還高
・第一關：實測：換一份題庫，省錢的程度差很多
・第二關：門檻 τ 不能照抄，要自己重選
・第二關：門檻選對，失敗時只變貴、不掉分
・第二關：門檻設太鬆，GPT-5.6 Sol 就掉分了

完整文章請在 datasciocean.com 搜尋「便宜判官先判、沒把握才找 GPT-6：JEV 串接真的省錢嗎？」

#DSO_LLMJudge #LLMJudge #LLM評測 #JEV
