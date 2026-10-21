# 貼文：decision-transformer-reward-conditioning（zh-TW）

## IG 輪播（共 9 張）

### 第 1 張
版型：cover
主標：AI 學做決策，能不能先許願要幾分？
補充：Decision Transformer 把強化學習改成序列預測：除了 state，也把「還想拿多少分」當輸入，讓模型預測 action

### 第 2 張
版型：context
主標：2021 年，強化學習被改寫成序列預測
補充：Decision Transformer 在 2021 年 6 月掛上 arXiv，卡在 GPT-3 之後、ChatGPT 之前，是「Transformer 能不能解序列決策問題」那波研究風潮的代表作。先認識三個會用到的詞：
表列：強化學習｜讓 AI 一步步做決定，靠拿到的分數學習。
表列：價值函數｜估計「某個狀態下，未來預期能拿到多少總分」。
表列：bootstrapping｜拿自己目前的估計，去修正自己的估計，像用還沒核對的答案批改自己。

### 第 3 張
版型：diagram
主標：它想解決的，是傳統 RL 的老毛病
補充：想解決傳統 RL 的老毛病，Decision Transformer 把 RL 問題重新包裝成序列預測問題，用 GPT 式的監督學習來訓練。
示意圖（compare）上的文字與數字：傳統 RL｜訓練不穩定｜Q-learning、policy gradient 這類方法｜需要精細調參｜常常得跟環境 online 互動｜Decision Transformer｜改成序列預測｜用 GPT 式的監督學習訓練｜不估計價值函數｜不先估算未來總分｜不做 bootstrapping｜它是訓練不穩定的來源之一

### 第 4 張
版型：diagram
主標：reward 要先換成 return-to-go
補充：一條軌跡（trajectory）由一連串的 (state, action, reward) 組成：state 是現在在哪，action 是做了什麼動作，reward 是拿到的分數。訓練前，先把 reward 換成 return-to-go。
示意圖（tokens）上的文字與數字：第一步｜+2 分｜這一步拿到｜10 分｜從這步到終點，還能拿｜第二步｜+3 分｜這一步拿到｜8 分｜從這步到終點，還能拿｜第三步｜+5 分｜這一步拿到｜5 分｜從這步到終點，還能拿
圖註：假設的例子：老鼠走迷宮，路上撿飼料、終點吃起司

### 第 5 張
版型：diagram
主標：輸入交錯排列，訓練時蓋住 action
補充：模型的輸入是交錯排列的三元組序列：return-to-go、state、action，一組接一組。訓練時蓋住 action，讓模型根據前面的 return-to-go 和 state，預測該輸出什麼 action。
示意圖（tokens）上的文字與數字：第一步｜return-to-go｜還想拿多少分｜state｜現在在哪｜action｜做什麼動作｜第二步｜return-to-go｜還想拿多少分｜state｜現在在哪｜action｜被蓋住，模型來猜｜舉例來說，模型學到的大致是：想拿到某個分數、又在位置 A，就往右走

### 第 6 張
版型：diagram
主標：使用時，你先許願，模型再一步步走
補充：推論時（實際使用的時候），使用者先許願，設定一個目標 return（想拿到的分數）；模型根據這個目標加上目前的 state，吐出動作。
示意圖（flow）上的文字與數字：你先許願｜設定一個目標 return，也就是想拿到的分數｜模型看「目標加上目前的 state」｜吐出下一個動作｜走一步｜return-to-go 按實際拿到的分數遞減｜重複，直到走完

### 第 7 張
版型：diagram
主標：在研究圈內，它有影響力
補充：同期有 Trajectory Transformer 提出類似想法，後續有 Online Decision Transformer，也被延伸到這些領域：
示意圖（quad）上的文字與數字：推薦系統｜機器人｜embodied AI｜網頁導航 agent

### 第 8 張
版型：diagram
主標：但它沒成為 LLM 對齊的主流
補充：LLM 對齊，是讓語言模型的回答貼近人類偏好。今天的主流，仍是 PPO 或後來的 DPO。
示意圖（compare）上的文字與數字：LLM 對齊的主流｜PPO｜用強化學習微調，InstructGPT 那條線
arxiv.org/abs/1707.06347｜DPO｜後來出現，不用強化學習
arxiv.org/abs/2305.18290｜Decision Transformer｜offline RL 與機器人控制｜這個子領域，持續發揮影響力｜不是家喻戶曉｜的產品級技術

### 第 9 張
版型：takeaway
先問的問題：所以，Decision Transformer 在做什麼？
主標：訓練時，學走法跟
分數的關聯；
使用時，先許願，
模型回推怎麼走

## Threads 串文

### 正文
AI 學做決策，能不能先許願要幾分？

Decision Transformer（2021 年）把強化學習改寫成序列預測，用 GPT 式的監督學習訓練：訓練時，觀察別人怎麼走、最後拿多少分，學會兩者的關聯；使用時，你先設定想要的分數，模型回推該怎麼走。

它想解決傳統強化學習的老毛病：訓練不穩定、需要精細調參，而且常常得跟環境 online 互動（訓練時要不斷取得新資料）。

在研究圈內它有影響力，但沒有成為 LLM 對齊的主流（今天仍然是 PPO 或後來的 DPO）。

（Threads 這則是輪播：正文下附與 IG 相同順序的全部 9 張圖，沒有逐張串文）

### 最後一則（置頂）
Decision Transformer 是什麼？訓練時學「怎麼走」跟「最後拿多少分」的關聯，使用時你先設定想要的分數，模型回推該怎麼走。

## IG caption

Decision Transformer：把強化學習改成序列預測，先設定想要的分數

・它想解決的，是傳統 RL 的老毛病
・reward 要先換成 return-to-go
・輸入交錯排列，訓練時蓋住 action
・使用時，你先許願，模型再一步步走
・在研究圈內，它有影響力
・但它沒成為 LLM 對齊的主流（LLM 對齊，是讓語言模型的回答貼近人類偏好）

#DecisionTransformer #強化學習 #機器學習
