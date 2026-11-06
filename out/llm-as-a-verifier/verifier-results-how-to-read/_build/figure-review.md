# 重製圖審查材料：verifier-results-how-to-read

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 7 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/verifier-results-how-to-read/ig/07.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 小標籤：① 第一名的成績
  - 主標：換 verifier 來挑，
成功率多 2.1～3.4%
  - 補充：跟「只交一次」相比，verifier 挑的多 2.1～3.4%，完美挑選也只多 4.8～9.0%。這才是算得到 verifier 的功勞：可搶的空間它搶到四分之一到三分之二。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：Terminal-Bench V2｜83.1→86.5%，搶到 38%｜完美挑選能多拿的 9 %｜verifier 多拿的 3.4 %
  - 圖表項目：SWE-Bench Verified｜76.1→78.2%，搶到 25%｜完美挑選能多拿的 8.3 %｜verifier 多拿的 2.1 %
  - 圖表項目：MedAgentBench｜70.2→73.3%，搶到 65%｜完美挑選能多拿的 4.8 %｜verifier 多拿的 3.1 %
  - 圖註：SWE-Bench 的 3 份候選來自三個不同模型，不能和另外兩列直接比。

### 原圖 llm-as-a-verifier/table3.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/table3.png
- blog 圖說原文（不是主張）：圖 8 — 主結果表。左半和右半是完全不同性質的比較，混著讀會得到錯誤結論。（來源：原始論文 Table 3。）
- 附這張圖的主張：c6

### 這張引用的主張（圖要以它們為準）
- **c6**（部落格考證）：同一候選池上 Pass@1 → Ours：Terminal-Bench V2 是 83.1% → 86.5%（+3.4pp），SWE-Bench Verified 是 76.1% → 78.2%（+2.1pp），MedAgentBench 是 70.2% → 73.3%（+3.1pp）；這是扣掉 harness 差異之後 verifier 真正的貢獻
  - 限定條件 c6#1：SWE-Bench 的候選池是異質的：N=3 是從三個不同模型各抽一條，Pass@1 是三模型平均，跟其他列不可直接比較
- **c7**（部落格考證）：實際候選池上可搶的 oracle 空間（oracle 減 Pass@1）不大（Terminal-Bench V2 9.0pp、SWE-Bench Verified 8.3pp、MedAgentBench 4.8pp），verifier 兌現了四分之一到三分之二（38%、25%、65%），跟「把 oracle 的巨大潛力兌現」的敘事還有距離
  - 限定條件 c7#1：SWE-Bench 的候選池是異質的（N=3，三個不同模型各抽一條），跟其他列不可直接比較

## 第 8 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/llm-as-a-verifier/verifier-results-how-to-read/ig/08.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：chart_bars
  - 小標籤：② 機器人實驗
  - 主標：同一個模型只換打分法，
準確率 70.8% → 87.4%
  - 補充：機器人的 Benchmark RoboRewardBench 上，同一個 Qwen 3.6 35B 只換打分法，偏好準確率就多 16.6%：最能歸功給方法的數字。
  - 圖表單位：%（軸從 0 起；繩長或橫條長度與數值成正比）
  - 圖表項目：改算期望值｜LLM-as-a-Verifier｜87.4 %｜強調
  - 圖表項目：RoboReward-8B｜訓練過，約 4.5 萬 episode｜81.4 %
  - 圖表項目：Robometer-4B｜訓練過，約 100 萬筆比較｜78.8 %
  - 圖表項目：只取最高分｜同一個模型｜70.8 %

### 原圖 llm-as-a-verifier/table4.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/llm-as-a-verifier/table4.png
- blog 圖說原文（不是主張）：圖 9 — 同一個模型，只改解碼方式，準確率從 70.8% 跳到 87.4%，還贏過兩個專門訓練的機器人 reward model。（來源：原始論文 Table 4。）
- 附這張圖的主張：c10, c11

### 這張引用的主張（圖要以它們為準）
- **c9**（背景說明）：機器人的 benchmark RoboRewardBench 量的是 preference accuracy（偏好準確率）；比較的對象包括能看影像的語言模型（VLM）與專門訓練的機器人 reward model
- **c10**（實驗結果）：RoboRewardBench 上，LLM-as-a-Verifier 是 87.4%，RoboReward-8B（訓練過，約 4.5 萬 episode）是 81.4%，Robometer-4B（訓練過，約 100 萬筆比較）是 78.8%，TOPReward 是 74.7%，同一個 VLM 的離散 LLM-as-a-Judge 是 70.8%
  - 限定條件 c10#1：RoboRewardBench 是共同作者也掛名的 RoboReward 論文提出的，被比較的 RoboReward-8B 正是那篇的模型，論文沒揭露這層利益關係
- **c11**（部落格判斷）：87.4% 和 70.8% 是同一個 Qwen 3.6 35B，唯一差別是離散 argmax 對上連續期望值；這 16.6pp 是全篇最大、也最能歸因給方法本身的數字，完全沒有 harness 混雜
