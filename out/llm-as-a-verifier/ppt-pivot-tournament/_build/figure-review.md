# 重製圖審查材料：ppt-pivot-tournament

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 6 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/ppt-pivot-tournament/ig/06.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 小標籤：② PPT 怎麼走
  - 主標：PPT 分五步：先粗排，再找基準細比
  - 補充：PPT（Probabilistic Pivot Tournament）讓每條候選只跟一小群 pivot 比。封面的第一步是②③、第二步是④⑤；重點在②：用便宜的一圈找出值得當 pivot 的候選。
  - 示意圖（flow）上的文字與數字：① 準備好 N 條候選｜② 隨機繞一圈：只比相鄰的 N 場，粗略排名｜③ 取前 k 名當 pivot｜④ 其他候選各跟 pivot 比，pivot 彼此也互比｜⑤ 平均每場贏最多的那條勝出

### 原圖 llm-as-a-verifier/figure6.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/figure6.png
- blog 圖說原文（不是主張）：圖 6 — PPT 的五個階段，重點在第二階段那圈環狀比較。（來源：原始論文 Figure 6。）
- 附這張圖的主張：c6

### 這張引用的主張（圖要以它們為準）
- **c4**（部落格判斷）：PPT 的核心想法是每條候選只跟一小群 pivot（當作比較基準的候選）比，成本降到 O(Nk)（k 是 pivot 的數量）；但真正的設計重點不是「用 pivot 省錢」，而是怎麼用一個便宜的前置步驟，找出值得當 pivot 的候選
- **c6**（設計參數）：PPT 分五個階段：N 條候選；隨機環狀比較 N 場（ring pass），得到粗略排名並消除位置偏誤；取前 k 名為 pivot 集合；非 pivot 對 pivot、加上 pivot 彼此互比；累積每條的平均勝分，取最高者

## 第 12 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/ppt-pivot-tournament/ig/12.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：table
  - 小標籤：③ 省多少、準多少
  - 主標：pivot 越多越準，一路往上沒有掉頭
  - 補充：這組實驗每題 20 條候選，比主實驗多；準確率越高，代表挑得越準。V1 是論文前一代的排名方法（論文沒說明怎麼運作）。
  - 表列：PPT k＝1｜65.83%
  - 表列：PPT k＝5｜66.27%，往上
  - 表列：PPT k＝9｜67.13%，再往上
  - 表列：完整循環賽｜67.42%，每對各比一次
  - 表列：V1 預算 5→7 倍｜65.85% → 65.53%，掉了
  - 圖註：簡化重畫；共 89 題，agent 由 Terminus-2 程式驅動。

### 原圖 llm-as-a-verifier/table9.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/table9.png
- blog 圖說原文（不是主張）：圖 7 — PPT 的預算與準確率權衡：k 愈大愈準，但報酬遞減得很快。（來源：原始論文 Table 9。）
- 附這張圖的主張：c15, c17

### 這張引用的主張（圖要以它們為準）
- **c14**（設計參數）：預算對準確率的實驗設定是 N=20 候選、89 題、Terminus-2 harness（驅動 agent 的那層腳手架），候選數跟主結果表不同（主實驗的 N 只有 3 到 5），這裡的 pass@1 跟主結果表的 Pass@1 不是同一個設定；表裡的基準線 V1 是論文拿來對照的前一代排名方法，論文全文沒有解釋 V1 怎麼運作
- **c15**（實驗結果）：N=20 候選時，PPT k=1 用 2,570 個查詢配對、準確率 65.83%；k=5 用 6,609 對、66.27%；k=9 用 9,630 對、67.13%；完整循環賽用 13,111 對、67.42%；pass@1 是 52.64%
  - 限定條件 c15#1：這組結果是 N=20 候選、89 題、Terminus-2 harness 的設定，跟主結果表不同，pass@1 不要直接拿來跟主結果表比
- **c17**（部落格判斷）：基準線 V1 在 5N 預算之後不升反降（65.85% → 65.53%），PPT 則是單調上升，這點是站得住的
  - 限定條件 c17#1：論文全文沒有解釋 V1 怎麼運作，只把它當基準線用
  - 限定條件 c17#2：這組結果是 N=20 候選、89 題、Terminus-2 harness 的設定，跟主結果表不同
