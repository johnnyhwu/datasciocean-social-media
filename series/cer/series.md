---
id: cer
name: "拆解 CER：不只數票，還要看 AI 有多大信心"   # 2026-11-15 Claude 決定（規則 12）；2026-11-17 人 review 成品後接受（「把握」改「信心」）
philosophy: series/cer/philosophy.md   # 籌碼
color: chips   # 相鄰系列不同色（已用：teal-mid、paper-cards、spotlight、abyss-contour、window、hourglass、band、junction、echo）
style: chips
members:
  - concept: cer-process-confidence-weighted-voting
    planned_title: 不只數票，把每一票的信心加起來
    summary: 多數決讓每條推理路徑都算一票；CER 改成把支持同一答案的路徑信心加總，而且看的是每一步，不只最後答案。
  - concept: cer-critical-token-confidence
    planned_title: 整句平均會被廢話稀釋，只看關鍵字
    summary: 連接詞的機率通常非常高，整句平均會蓋過關鍵數字；CER 規定每步寫出答案，只算答案那幾個字的機率。
  - concept: cer-results-how-to-read
    planned_title: 數學比問答穩，因為信心補不了沒學過的知識
    summary: 和只看最後一步的對照組比，看每一步勝出；CER 在數學題通常比問答穩：濾得掉推理錯，補不了沒學過的知識。
hashtag: CER
status: locked
members_locked: true
---

# CER

來源文章：`cer`（3 張卡）。
文章標題：ACL 2025 | 超越 Self-Consistency！CER 論文解析：無需訓練，靠「過程自信度」激發 Llama 3 與 DeepSeek 推理潛能
網址：https://datasciocean.com/paper-intro/cer/

## 規劃備忘（2026-11-15，Claude 依規則 12 決定）

- 3 張卡各做 1 則，不合併：第 1 則「怎麼投票」（多數決的盲點、路徑分數、加權投票、CER-LAST 對照），第 2 則「信心怎麼量」（整句平均被功能性詞彙稀釋、Prompt 規定中間答案、只算關鍵字、多個 Token 相乘），第 3 則「效果與邊界」（數學比問答穩、強弱模型的差別、為什麼補不了知識）。
  - 合併檢查：三張卡共用的只有「CER 是什麼」的背景主張（各卡 c2），第 2、3 則靠回顧頁接上；第 1 則的「信心」只講到「模型對這一步中間答案有多大信心」，怎麼算留給第 2 則（卡 1 的 c9 只用到 c_aj，不需要第 2 則的細節就看得懂）。三張卡可用主張 16／13／12，合併會超過 20 張。
  - CER-LAST 對照組在卡 1（c14）與卡 3（c4、c5）都有：放第 1 則當「看過程」的證據；第 3 則只用一句帶過，主力放數學與問答、強弱模型。
- 不能用（`pending_author_confirmation`）：卡 3 的 c8（Llama 3.2 3B 的 4.1%）、c9（所有資料集都贏）、c14（弱模型提升巨大）、c15（DeepSeek-R1 變體 87.2%→90.2%）；c16 是由 c15 的結果推出來的，一併不用。
- 用語：Self-Consistency＝多數決（第一次出現寫「Self-Consistency（多數決）」）；推理路徑＝AI 從頭推到答案的一次完整過程；信心＝AI 對某個答案有多確定（模型輸出它的機率；卡上叫「自信度」，貼文一律寫「信心」，人 2026-11-17）；一票＝一條推理路徑。
- 新系列的草圖與樣張省略（前例：UniversalRAG、Prompt Repetition，人說只 review 成品；`CLAUDE.md` 規則 12）；風格回歸測試 `tests/test_chips_style.py`。
- 2026-11-17 人 review 三則成品後接受系列名、三則標題與 hook，`members_locked: true`；人的回饋：「把握」一律改「信心」（記進 config/terms.yaml）、第 1 則第 7 張拆成兩張、第 9 張籌碼標籤改寫。
