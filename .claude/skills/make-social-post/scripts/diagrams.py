"""示意圖版型（layout: diagram）的幾何與繪製。由 render.py 呼叫：build(spec, y0, ctx) -> (svg 內容, 文字 html, 底部 y)。

為什麼有這份：2026-10-11 人的回饋——「每篇 post 的 chart 都是同一個模板、都是 bar chart；文字下面空出來的區塊是塗鴉牆，
流程圖、任何圖都可以，只要讓讀者更好理解、覺得有趣」。所以除了橫條圖，另有下列 kind（spec 的 `kind` 欄位）：
  flow      由上往下的流程：nodes（每個 text、選用 sub）、選用 outcomes（兩三個結果，good 金色／bad 外框）、選用 loop（底部虛線框的說明）
  compare   兩欄並列：columns = [{head, items:[{text, sub?, gone?, emph?}]}]（gone = 劃掉、emph = 左側金條）
  pairs     「換掉什麼 → 換成什麼」：heads = [左標, 右標]、pairs = [[左, 右], …]、選用 outcomes[0]（底下一條橫框，tone: good 金色）
  samples   一個點 vs 一批點：nodes = [{text, sub?}, {text, sub?}]
  paths     亂走 vs 小步走：nodes = [{text, sub?}, {text, sub?}]
  epochs    小步子與每輪結束的檢查旗：nodes = [{text}（小點是什麼）, {text}（金旗是什麼）]
  dotgrid   點陣：count、選用 cols（每列幾個點）、nodes = [{text}]（一個點代表什麼）
  dumbbell  前後對比（軸從 0 起）：points = [{name, value}, {name, value}]、ref = {name, value}、unit、axis_max
  range     區間條（軸從 0 起）：ranges = [{name, sub?, lo, hi, emph?}]（lo == hi 畫成標記線）、unit、axis_max
  funnel    漏斗：nodes（3 層，每層 text、選用 sub）
  batches   一個池子切成幾組（2026-10-12）：count（池子有幾個點）、group（每組幾個）、nodes = [{text}（池子是什麼）, {text}（每一組做什麼）]
  decay     從 start 慢慢降到 end 的曲線（軸從 0 起、高度與數值成正比）：start、end、unit、axis_max、nodes = [{text}（初期）, {text}（後期）]
  fan       幾組同時做事、再匯成一份：heads（2～4 個組別標籤）、nodes = [{text}（組別上方的說明）, {text, sub?}（匯整後的結果）]
  peaks     兩條曲線的最高點落在同一處（純示意）：nodes = [{text}（線一）, {text}（線二）, {text}（最高點的標籤）]
  equation  算式 A × B ＝ C：nodes = 算元 [{text（大數字）, sub（單位）, sub2?, emph?}]、選用 ops、選用 outcomes[0]（底下一條橫框）
  quad      2×2 四個格子：nodes = 4 個 [{text, sub?, emph?, bars?}]（bars＝格子上方的小投影片有幾條條列）
  locked    文件裡一塊受保護的區塊：heads = [被擋下的來源, 能更新的來源]、nodes = [{text}（文件名）, {text}（受保護區塊）]
  tokens    符號序列（2026-10-18）：steps = [{label, cells:[{text, sub?, tone}]}]，一列一步；tone = rtg／state／action／reward／mask；選用 more、outcomes[0]
  seesaw    蹺蹺板（2026-10-22，Bradley-Terry）：nodes = [{text（隊名）, sub?（實力值）, blocks（方塊數）, win（贏的機率標籤）}, {…}]；重的一端壓低（傾斜角隨兩端比例）；梁下面一條橫條，長度與兩端方塊數的比例成正比；選用 outcomes[0]（底下一條橫框）；純示意
  hidden    水面上看得到的、水面下看不到的：heads = [上標籤, 下標籤]、nodes = 水面上的結果 [{text}]（最多 3）、outcomes = 水面下藏著的東西 [{text, sub?}]（畫成虛線框的「？」；最多 3）
  cycle     三個節點繞成一圈（A→B→C→A，最後一條箭頭金色）：nodes = 3 個 [{text, sub?}]、heads = 3 條邊的標籤（依序 A→B、B→C、C→A）、選用 outcomes[0]（底下一條橫框）
  links     左右兩排節點之間的連線（二部圖，2026-10-24，SAG 的「事件↔實體」）：nodes = 左排 [{text, sub?, emph?}]、outcomes = 右排 [{text, sub?, emph?}]、edges = [[左序號, 右序號], …]（0 起）、選用 hot = 要畫成金色粗線的邊、選用 heads = [左標籤, 右標籤]；連線全由 edges 決定，純示意時圖註要標「示意」
  hops      幾跳才到答案（2026-10-24，SAG 的「4 跳 vs 1 跳」）：nodes = 每一列 [{text, sub?, hops}]（hops＝箭頭數，圖上就畫幾條；text／sub 若有數字，必須等於 hops）、選用 heads = [起點標籤, 終點標籤]；每一跳等長，所以越多跳越長
  bubble    一個大泡泡圈住好幾個東西（2026-10-24，SAG 的「超邊」）：heads = [左標籤, 右標籤]、nodes = [{text, sub?}（左：一般的邊，只連兩點）, {text, sub?}（右：泡泡的說明）]、outcomes = 泡泡裡的項目 [{text}]（2～8 個，畫成小標籤）；左邊預設畫兩個點與一條線（`chain: true` 時改畫一串只連兩點的邊，用 outcomes 的名字標點，2～4 個）；右邊畫金色泡泡
  drift     一路偏掉的路徑（2026-10-24，SAG 的「誤差沿推理鏈放大」）：heads = 每一站的標籤（3～6 個，第一個是起點、最後一個是答案）、nodes = [{text}（正確的路線）, {text, sub?}（實際走的路線）]；實際路線每一站偏得更多（偏移量由程式依站序算，只示意，不是數據）
  ingest    兩段式架構圖（2026-10-24，SAG 論文圖二的版型）：heads = [上段標籤, 下段標籤]；nodes = 上段四欄的標籤 4 個 [{text, sub?}]（原始片段、一對一轉成的東西、多對多綁定的東西、存放處）；
            outcomes = 下段由左到右的步驟 2～3 個 [{text, sub?}]（最後一個金色，下面畫一個小的局部超圖）。上段的方塊、圓點、連線是固定的示意（不帶文字）
  roles     三列角色卡（2026-10-25，SAG 第 2 則）：nodes = 三列 [{text（元件名）, sub（角色，一個詞）, sub2（做什麼）, icon: db／vec／llm}]
  embed     精確比對 vs 向量空間：heads = [左標, 右標]、nodes = 左邊比對列 [{text, sub?, ok}]、outcomes = 右邊向量空間的 3 個點 [{text, sub?}]（第一個是中心）；純示意
  online    線上檢索路線圖（SAG 論文圖二下半的重畫）：heads = [起點, 結果]、nodes = 第一步兩條路、outcomes = [第二步, 第三步左路, 第三步右路]
  gate      水庫閘門，兩道各一列：count（名額）、nodes = 兩列 [{text, sub?}]（每列：標題，下面左邊一池散點、中間閘門、右邊整齊的格子）；純示意，不是實際數量
  concat    兩路各一排、匯成一排：heads = [左路, 右路]、nodes = [{text}（上方一句話）, {text, sub?}（結果）]；每路 5 個、匯整後 10 個，純示意
  rails     兩條軌道各撈一排、合併成一排（A 漏掉的一格由 B 補上）：heads = [A 路, B 路]、nodes = [{text, sub?}, {text, sub?}]、outcomes[0] = {text}（合併後）；純示意
  joint     逐一打分 vs 一起評估：heads = [左標, 右標]、nodes = 兩邊 [{text, sub（例子）, sub2（結論）}]；純示意
  hops 的選用欄位（2026-10-26）：spec 頂層 fade: true＝箭頭一跳比一跳淡（圖上傳遞的分數越來越弱，純示意，圖註要說明）；每列 shortcut: true＝鏈上方畫一條被叉掉的虛線捷徑，標籤用該列的 sub2
  scoreboard 戰績表（2026-10-26，SAG 第 3 則）：nodes = 每列一個資料集 [{text, sub?, emph?}]、heads = 兩個欄標籤、outcomes = 圖例 [{text（深色那一方）}, {text（淺色那一方）}]、cells = 每列每欄的 [深色值, 淺色值]（字串，例 "64.1"）；
            每格兩條橫條，軸從 0 起、長度與數值成正比（axis_max 預設 100）；深色值小於淺色值的格子畫虛線框（圖註要說明）；emph 的列底下墊金色淡底
  leak      每一跳都漏一些（2026-10-26）：nodes = 兩條路 [{text, sub?}（走很多跳的）, {text, sub?}（一次到位的）]、heads = 兩條路箭頭上的標籤（例：剪枝）；兩條路從同一個起點到同一個終點，每個站畫一格點，漏掉的畫成虛線空點；點數是固定示意，圖註要標「示意」；選用 hops = 第一條的跳數（2 或 3，預設 3）
  amplify   誤差沿路放大 vs 精確比對（2026-10-26）：nodes = 兩條路 [{text, sub?}, {text, sub?}]、heads = 第一條的兩端標籤（起點、終點）、outcomes[0] = 第二條的標籤；第一條畫一個越來越寬的楔形，第二條是一條等寬的金色帶；純示意
  receipt   帳單（2026-10-27，SAG 第 4 則）：heads = [抬頭, 「換來的」標籤]、nodes = 品項 2～4 個 [{text, sub?}]（自動編號）、outcomes = 換來的東西 1～3 個 [{text}]（金色小標籤）；米色紙、下緣鋸齒
  squeeze   名額線擠掉了誰（2026-10-27）：heads = [左端標, 右端標, 名額線標]、nodes = [{text, sub?}（上方說明）, {text, sub?}（被擠出去的金點）]、outcomes = 推理鏈兩端 [{text}, {text}]；排隊的點是固定示意，圖註要標「示意」
  alias     別名對齊：傳統合併、SAG 不合併（2026-10-27）：heads = [上段標, 下段標]、outcomes = 同一個東西的 3 種寫法 [{text}]、nodes = [{text, sub?}（合併後）, {text, sub?}（下段說明）]；純示意
  handoff   把工作從線下搬到線上（2026-10-27）：heads = [上帶標, 下帶標, 箭頭標]、nodes = [{text, sub?}（線下不做的事）, {text, sub?}（線上接手的做法）]、outcomes[0] = {text}（線下因此得到的好處）；純示意
  mismatch  同一個東西寫法不同就接不起來（2026-10-27）：heads = [上段標, 下段標, 缺口標]、nodes = [{text, sub?}（共同寫法＋上段說明）, {text, sub?}（另一種寫法＋下段說明）]、outcomes = 兩個事件 [{text, sub?}]；純示意
  ledger    只能往後新增的記錄簿（2026-10-27）：heads = [時間軸標籤]、nodes = 依時間排的紀錄 2～5 筆 [{text, sub?, new?, ask?}]（舊的畫鎖、new 金色加「＋」、ask 左邊釘金色「？」表示分不出誰有效）、outcomes[0] = {text, sub?}（右邊說明）；例子要標「假設」
  turn      一輪怎麼走（2026-10-28，Claude Code 第 1 則）：nodes = [回應, 權限檢查, 對話紀錄第一行, 第二行]、heads = [箭頭標籤, 紀錄標題]、outcomes = [最終答案, 同意, 拒絕]、選用 loop
  transcript 終端機視窗裡的對話紀錄（2026-10-28，Claude Code 第 1 則）：heads[0] 視窗標題、nodes 一列一個動作 [{text, tone: prompt／tool／fail／ok, feeds?}]（「　」分開工具名與內容；feeds 的列畫金色箭頭繞到下一列）、outcomes[0] 箭頭標籤
  oneloop   一個圈、圈裡兩個框，兩側各一個被打叉的虛線框：nodes 兩個、outcomes 兩個、heads[0] 圈下面的說明
  intercept 上下兩條路，下面那條要過一道金框的關卡才到檔案：heads 4 個（上排、下排、關卡、檔案）、nodes 兩個（只用文字說的話、工具呼叫）、outcomes 關卡裡的檢查項目 2～3 個
  dial      有刻度的軌道與金色旋鈕：人轉旋鈕、模型被打叉：nodes 兩個（人、模型）、heads[0] 說明、選用 heads[1]／heads[2] 軌道左右端的標籤
  lanes     一個問題分成兩欄：nodes[0] 問題、nodes[1:] 左欄項目、heads 兩欄標題、outcomes 兩欄結果（左金色）
  layers    兩排各一道防線：上排指令過關卡、下排指令在虛線容器裡碰不到外面：heads 三個、nodes 兩個（工作目錄、指令）、outcomes[0] 關卡旁的字
  sockets   三個擴充點（2026-10-28，Claude Code 第 2 則）：heads[0] 上方橫條的字、nodes 剛好 3 個 [{text, sub}]
  lazy      平常一行、用到才全讀進來：heads = [左窗標題]、nodes 3 個 [{text, sub, emph?}]（剛好一個 emph）、outcomes[0] = {text, sub?}（文件）
  hub       共通介面接外部服務：heads = [共通介面標籤, 被叉掉的說明]、nodes[0] = Claude Code、outcomes = 2～4 個服務
  pinned    每場對話開頭釘著同一份：heads = 3 個視窗標題、nodes[0] = {text}（金色那行）、選用 outcomes[0] = {text}
  compact   快滿的對話壓成摘要：heads = [左窗, 右窗標題]、nodes = [箭頭標籤, 摘要項一, 摘要項二]、outcomes[0] = 底下虛線框的提醒
  sidecar   另開一扇窗做雜事、只有摘要回來：heads = [主視窗, 側視窗標題]、nodes = [派出那行, 收到摘要那行]、outcomes = [側視窗標籤, 回傳箭頭標籤]
  combo     兩個機制自動組合的例子（上：一個東西被收進另一個；下：兩種來源都套用同一份）：heads = [上標, 下標]、nodes = [被收進去的框, 視窗標題, 箭頭標籤]、outcomes = [來源一, 來源二, 金色那份{text, sub?}]
  stops     由上往下三個停靠點（不按比例）：nodes = [{text, sub?, emph?}]、選用 heads = [上端標籤, 下端標籤]
  waist     沙漏（2026-10-31，Cerebras RAG 第 1 則）：上段異質來源收斂成一條只有五格的窄帶、下段重新展開。
            heads = [上段標籤, 窄帶標籤, 下段標籤]、nodes = 上段的來源 2～5 個 [{text}]、outcomes = 下段展開的東西 2～5 個 [{text}]；純示意
  depend    序列依賴（2026-11-01）：heads = [上段標籤, 下段標籤]、nodes = [{text}（工具 A）, {text}（工具 B）]、outcomes = [{text}（A 的結果）, {text}（斷線旁的字）, {text}（金色框說明）]；上段同時出發、A 的結果送不到 B，下段金色框包成一個工具；純示意
  pick      勾選單 vs 寫一整段（2026-11-01）：heads = [左標, 右標]、nodes = 勾選單選項 2～5 個 [{text, on?}]、outcomes[0] = {text}（底下金色橫框）；右邊的灰條是示意
  pile      證據堆原樣交給最後一步（2026-11-01）：heads = [左欄標籤, 金框標籤]、nodes = [{text, sub?}（左欄說明）, {text, sub?}（金框）]、outcomes = 證據卡 2～5 張 [{text}]；純示意
  addlane   多接一種資料要做多少（2026-11-01）：heads = [上段, 下段]、nodes = 上段每一路的格子 2～3 個 [{text}]、outcomes = [上段新一路說明, 上段右框, 下段新一路說明, 下段右框]；純示意
  schema    一張只有幾個欄位的表（2026-10-31）：heads = [表名]、nodes = 欄位 3～5 個 [{text（欄位名）, sub（這一欄存什麼）, emph?（金色那一格，只能一個）}]、
            選用 outcomes[0] = {text}（底下一條金色橫框）
  branch    形式統一但語意分裂（2026-10-31）：窄帶右邊硬接上幾個來源專屬欄位，它們各拉一條線到下游，下游就得寫分支。
            heads = [上段標籤, 下段標籤]、nodes = [{text, sub?}（上段說明）, {text, sub?}（下游的檢索邏輯）]、outcomes = 額外欄位 2～3 個 [{text}]；純示意
  gates     幾道門檻，一條路一路通過、另一條在第一道就被擋下（2026-10-31）：heads = [通過那一條的標籤, 被擋那一條的標籤]、
            nodes = 門檻 2～4 個 [{text, sub?}]、outcomes = [{text}（通過之後）, {text}（沒過的下場）]；純示意
  route     路線圖（2026-10-31，人的回饋「讀起來不連貫、不知道處在 journey 的哪裡」）：一條金色的路由上往下走，路上幾站，
            每站一個編號圓與一句「這一站要回答什麼」；這一則不走的那一段畫成虛線與空心終點。
            nodes = 站 2～4 個 [{text, sub?}]、選用 heads = [最上面的標籤, 虛線那一段的說明]

  magnet    文字問題把文字吸過來、有答案的圖片被晾著（2026-11-09，UniversalRAG）：nodes[0] = {text}（問題）、outcomes = [{text, sub?}（文字）, {text, sub?}（圖片，金色＝答案在這）]、heads = [粗箭頭標籤, 虛線標籤]；純示意
  puzzle    一個問題要兩塊拼圖、只拿得到一塊（2026-11-09）：nodes = [{text}（問題）, {text}（拿得到的那塊）, {text}（缺的那塊）]、outcomes[0] = {text}（結果）；純示意
  merge     幾種資料經同一個編碼器進同一個空間（2026-11-09）：outcomes = 來源 2～4 個 [{text}]、nodes = [{text, sub?}（編碼器）, {text}（空間）]；純示意
  clusters  向量空間裡依形式分群（2026-11-09，重畫論文的分布圖）：heads = 三群標籤 [上, 左下, 右下]、nodes[0] = {text}（問題的標籤）、outcomes[0] = {text}（虛線旁的說明）；點的位置固定、純示意，圖註要標
  shelves   一列一種資料、每列幾個抽屜（2026-11-09）：columns = [{head, items:[{text, sub?}]}]，每列 1～2 個抽屜；純示意
  switch    問題過 Router、只亮一條軌道到一個庫（2026-11-09）：nodes = [{text}（問題）, {text, sub?}（Router）]、heads[0] = Router 旁的話、outcomes = 庫 3～5 個 [{text, on?}]（剛好一個 on）；純示意
  duel      同一題兩種決定方式（2026-11-09）：heads = [上段標, 下段標]、nodes = [{text}（文字庫）, {text}（影像庫）]、outcomes[0] = {text}（下段的判斷）；上段粗線連文字、細虛線連影像，下段文字庫被打叉；純示意
  matrix    列是系統、欄是情況的小矩陣（2026-11-09）：heads = 欄標籤、nodes = 列 [{text, sub?}]、cells[列][欄] = [文字]、選用 hot = 要塗金色的列序號
  grain     粒度抓錯的兩種下場（2026-11-10，UniversalRAG 第 2 則）：heads = [上段標籤, 下段標籤]、nodes = [{text}（膠捲下的說明）, {text}（文字段右邊的說明）]、outcomes = [{text}, {text}]（上下兩段的下場，畫成打叉）；
            上段整部影片的膠捲只有一小段金色、下段一段文字只抓到中間一行；金色那段寬度不按比例，圖註要標「示意」
  ballot    答案卡（2026-11-10）：heads = [抬頭, 選用：抬頭右邊的金色小字]、選用 nodes[0] = {text}（上方的問題）、outcomes = 選項 3～8 個 [{text, sub?, on?}]（on 打勾、整列淡金底）；純示意
  thresh    各自打分、超過門檻才啟動（2026-11-10）：nodes = [{text, p}]（p 在 0～1）、ref = {name, value}（門檻）、heads = [上方標籤]；超過門檻的橫條金色、長度與分數成正比；分數通常是假設的，圖註要標
  murky     表格和文字混在同一份文件、分不清（2026-11-10）：heads = [文件上方標籤, 右邊的問話]、nodes[0] = {text}（箭頭旁的話）、outcomes = 兩個下場 [{text}]（打叉）；純示意
  race      兩條路到同一個答案，不帶數字（2026-11-09）：heads = [繞路那一方, 直線那一方]、nodes = [{text}]（規模）、選用 outcomes[0] = {text}（直線那條路上的關卡，2026-11-10）；路的長短是固定示意，圖註要標「不是實測數字」
  dist      機率分佈直條（2026-11-03，LLM-as-a-Verifier）：nodes = 每個分數一根 [{text（1、2、3…）, p}]（加總 1）、pick = argmax（最高那根金色、其餘虛線）／ev（金針停在期望值，程式算）、heads = [上方標籤, 針的標籤前綴]、選用 outcomes[0]
  snap      刻度上的點（2026-11-03）：nodes = 2～3 列 [{text, sub?, lo?, hi, marks:[{v, text}], tie?}]；數值相同的點往上疊，旁邊放金色小牌 tie；點的位置由程式 B 檢查
  stack     結果切三段的橫條（2026-11-03）：heads = 三個圖例、nodes = 2～4 列 [{text, sub?, parts:[a,b,c]}]（加總 total，預設 100）；長度由程式 B 檢查
  target    打靶（2026-11-03）：heads = [左靶, 右靶]、nodes = [{text}（靶心）, {text}（金色 ✕＝落點平均）]、選用 outcomes[0]；左散右集、兩邊都偏同一個方向；純示意
  dotgrid 的選用欄位 on（2026-11-03）：前 on 個點實心、其餘空心

規則：圖形全部用 class "bg"（不進程式 B 的文字與圖形重疊檢查），所以排版由這裡負責避開文字；框內的文字由程式 B 的「框內文字不超出框」檢查；
比例（dumbbell／range）由程式 B 檢查圖形位置與數值成正比。字級只用 {28, 34, 40, 56}。
"""
from __future__ import annotations

import math
import re

CREAM, TEAL, DEEP, GOLD = "#F2E0C0", "#076876", "#01353F", "#DDA642"
MID, LIGHT, ABYSS = "#1F8A8D", "#69B4AA", "#032027"
X0, X1 = 80, 1000
BOTTOM = 1235          # 示意圖最低可到的 y（頁尾的 @datasciocean 在 1262）


class Ctx:
    """render.py 傳進來的小工具：est_lines(txt, per_line)、bind(txt)、esc(txt)。"""
    def __init__(self, est_lines, bind, esc):
        self.est_lines, self.bind, self.esc = est_lines, bind, esc


class Canvas:
    def __init__(self, ctx: Ctx):
        self.ctx, self.svg, self.html = ctx, [], []

    # ---- 圖形（class bg）
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=3, rx=16, dash=None, op=None):
        a = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        a += f' stroke-dasharray="{dash}"' if dash else ""
        a += f' fill-opacity="{op}"' if op is not None else ""
        self.svg.append(f'<rect class="bg" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{a}/>')

    def line(self, x1, y1, x2, y2, color=TEAL, sw=4, dash=None, op=None):
        a = f' stroke-dasharray="{dash}"' if dash else ""
        a += f' stroke-opacity="{op}"' if op is not None else ""
        self.svg.append(f'<line class="bg" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{a}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=3, op=None, dash=None, cls="bg", extra=""):
        a = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        a += f' stroke-dasharray="{dash}"' if dash else ""
        a += f' fill-opacity="{op}"' if op is not None else ""
        self.svg.append(f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{a}{extra}/>')

    def poly(self, pts, fill="none", stroke=None, sw=4, closed=False, op=None):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        a = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
        a += f' fill-opacity="{op}"' if op is not None else ""
        tag = "polygon" if closed else "polyline"
        self.svg.append(f'<{tag} class="bg" points="{d}" fill="{fill}"{a}/>')

    def arrow(self, x1, y1, x2, y2, color=TEAL, sw=4, head=14, op=None):
        self.line(x1, y1, x2, y2, color, sw, op=op)
        ang = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2), (x2 - head * math.cos(ang - .45), y2 - head * math.sin(ang - .45)),
             (x2 - head * math.cos(ang + .45), y2 - head * math.sin(ang + .45))]
        self.poly(p, fill=color, closed=True, op=op)

    def raw(self, svg: str):
        self.svg.append(svg)

    # ---- 文字（class t；data-box 讓程式 B 檢查文字不超出框）
    def text(self, x, y, w, s, cls="dn", color=DEEP, align="left", box=None, extra=""):
        b = f' data-box="{box[0]:.1f},{box[1]:.1f},{box[2]:.1f},{box[3]:.1f}"' if box else ""
        t = self.ctx.bind(s).replace("\n", "<br>")
        self.html.append(f'<div class="t abs {cls}" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;color:{color};text-align:{align}{extra}"{b}>{self.ctx.esc(t) if "<br>" not in t else "<br>".join(self.ctx.esc(p) for p in t.split("<br>"))}</div>')

    def lines(self, s, w, size):
        # 文字裡的 \n 是明確換行（text() 會轉成 <br>），每一段各自估行數再加總
        # 分數（\\frac）比一般行高：含分數的那一段多算約一行；含上下標或 \\mathcal 的算式多算約三分之一行
        return sum(self.ctx.est_lines(self.ctx.bind(seg), w / size - 0.7) + (0.9 if re.search(r"\\[dt]?frac", seg) else 0.35 if re.search(r"\$[^$]*[_^\\][^$]*\$", seg) else 0) for seg in s.split("\n"))

    def textbox(self, x, y, w, title, sub=None, fill=DEEP, tcolor=CREAM, scolor=LIGHT, stroke=None, dash=None, align="left", pad=22, h=None, size=34):
        """畫一個框，框裡放標題與副標；回傳框高。h 給定時用固定高（文字垂直置中）。"""
        iw = w - 2 * pad
        l1 = self.lines(title, iw, size)
        l2 = self.lines(sub, iw, 28) if sub else 0
        th = l1 * (size * 1.3) + (l2 * 28 * 1.4 + 6 if l2 else 0)
        bh = h if h else th + 2 * pad
        self.rect(x, y, w, bh, fill=fill, stroke=stroke, dash=dash)
        ty = y + (bh - th) / 2
        box = (x, y, w, bh)
        cls = "dn" if size == 34 else "dv"
        self.text(x + pad, ty, iw, title, cls, tcolor, align, box)
        if sub:
            self.text(x + pad, ty + l1 * (size * 1.3) + 6, iw, sub, "ds", scolor, align, box)
        return bh

    def cell(self, x, y, w, h, s, fill="none", stroke=None, dash=None, color=DEEP, pad=10):
        """矮格子（約 52px 高）裡放一行字。用 28px 粗體（dl）：34px 的字框約 49px 高，
        程式 B 取字框外緣四角算對比時會取到格子邊線或格子外的底色。"""
        self.rect(x, y, w, h, fill=fill, stroke=stroke, dash=dash)
        self.text(x + pad, y + (h - 39.2) / 2, w - 2 * pad, s, "dl", color, "center", (x, y, w, h))


def _fit(total: float, avail: float, what: str) -> None:
    if total > avail + 0.5:
        raise ValueError(f"示意圖（{what}）放不下：需要 {total:.0f}px，只剩 {avail:.0f}px；請縮短補充或圖上的字")


# ------------------------------------------------------------------ flow
def flow(c: Canvas, spec: dict, y0: float) -> float:
    nodes, outs, loop = spec["nodes"], spec.get("outcomes", []), spec.get("loop")
    w = X1 - X0
    gap = 30
    hs = []
    for n in nodes:
        t = c.lines(n["text"], w - 44, 34) * 44.2 + (c.lines(n["sub"], w - 44, 28) * 39.2 + 6 if n.get("sub") else 0) + 44
        hs.append(t)
    ow = (w - 24 * (len(outs) - 1)) / len(outs) if outs else 0
    oh = max([c.lines(o["text"], ow - 44, 34) * 44.2 + (c.lines(o["sub"], ow - 44, 28) * 39.2 + 6 if o.get("sub") else 0) + 44 for o in outs], default=0)
    lh = (c.lines(loop, w - 44, 28) * 39.2 + 36) if loop else 0
    total = sum(hs) + gap * (len(nodes) - 1) + (gap + oh if outs else 0) + (gap + lh if loop else 0)
    _fit(total, BOTTOM - y0, "flow")
    extra = BOTTOM - y0 - total                         # 多出來的高度：先加厚各框，再拉大間距
    nbox = len(nodes) + (1 if outs else 0)
    add = min(extra * 0.55 / nbox, 46)
    hs = [h + add for h in hs]; oh += add if outs else 0
    gap += min((extra - add * nbox) / max(len(nodes) - 1 + (1 if outs else 0) + (1 if loop else 0), 1), 34)
    y = y0
    for i, n in enumerate(nodes):
        c.textbox(X0, y, w, n["text"], n.get("sub"), h=hs[i])
        y += hs[i]
        if i < len(nodes) - 1:
            c.arrow(X0 + w / 2, y + 3, X0 + w / 2, y + gap - 3)
            y += gap
    if outs:
        y += gap
        for k, o in enumerate(outs):
            x = X0 + k * (ow + 24)
            good = o.get("tone") == "good"
            c.textbox(x, y, ow, o["text"], o.get("sub"), fill=GOLD if good else CREAM, tcolor=DEEP,
                      scolor=DEEP, stroke=None if good else DEEP, h=oh, align="center")
            c.arrow(X0 + w / 2, y - gap + 3, x + ow / 2, y - 3)
        y += oh
    if loop:
        y += gap
        c.rect(X0, y, w, lh, fill="none", stroke=TEAL, sw=3, dash="10 8")
        c.text(X0 + 22, y + 18, w - 44, loop, "ds", TEAL, "left", (X0, y, w, lh))
        y += lh
    return y


# ------------------------------------------------------------------ compare
def compare(c: Canvas, spec: dict, y0: float) -> float:
    cols = spec["columns"]
    cw, gap = 440, 40
    xs = [X0, X0 + cw + gap]
    hh = 80
    n = max(len(col["items"]) for col in cols)
    rows = []
    for i in range(n):
        h = 0
        for col in cols:
            if i < len(col["items"]):
                it = col["items"][i]
                h = max(h, c.lines(it["text"], cw - 56, 34) * 46 + (c.lines(it["sub"], cw - 56, 28) * 39.2 + 6 if it.get("sub") else 0) + 40)
        rows.append(h)
    total = hh + 16 + sum(rows) + 16 * (n - 1)
    _fit(total, BOTTOM - y0, "compare")
    add = min((BOTTOM - y0 - total) / n, 70 if n >= 3 else 190)
    rows = [r + add for r in rows]
    total += add * n
    for k, col in enumerate(cols):
        c.rect(xs[k], y0, cw, hh, fill=DEEP if k == 0 else TEAL)
        c.text(xs[k] + 22, y0 + (hh - 44) / 2, cw - 44, col["head"], "dn", CREAM, "center", (xs[k], y0, cw, hh))
        y = y0 + hh + 16
        for i, it in enumerate(col["items"]):
            h = rows[i]
            c.rect(xs[k], y, cw, h, fill="none", stroke=DEEP, sw=3, dash="8 8" if (it.get("gone") or it.get("muted")) else None, rx=14)
            if it.get("emph"):
                c.rect(xs[k], y, 12, h, fill=GOLD, rx=6)
            col_t = TEAL if (it.get("gone") or it.get("muted")) else DEEP
            l1 = c.lines(it["text"], cw - 56, 34)
            th = l1 * 46 + (c.lines(it["sub"], cw - 56, 28) * 39.2 + 6 if it.get("sub") else 0)
            cls = "dt gone" if it.get("gone") else "dt"
            c.text(xs[k] + 30, y + (h - th) / 2, cw - 56, it["text"], cls, col_t, "left", (xs[k], y, cw, h))
            if it.get("sub"):
                c.text(xs[k] + 30, y + (h - th) / 2 + l1 * 46 + 6, cw - 56, it["sub"], "ds", col_t, "left", (xs[k], y, cw, h))
            y += h + 16
    return y0 + total


# ------------------------------------------------------------------ pairs
def pairs(c: Canvas, spec: dict, y0: float) -> float:
    heads, prs = spec["heads"], spec["pairs"]
    lw, rw, mid = 380, 460, 80
    rx = X0 + lw + mid
    rows = [max(c.lines(l, lw - 44, 34), c.lines(r, rw - 44, 34)) * 44.2 + 44 for l, r in prs]
    foot = (spec.get("outcomes") or [None])[0]      # 選用（2026-10-22）：底下一條橫框，例如拿前面的例子驗算 {text, sub?, tone?}
    fh = (c.lines(foot["text"], X1 - X0 - 44, 34) * 44.2 + (c.lines(foot["sub"], X1 - X0 - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    fgap = 30 if foot else 0
    total = 44 + 14 + sum(rows) + 18 * (len(prs) - 1) + fgap + fh
    _fit(total, BOTTOM - y0, "pairs")
    add = min((BOTTOM - y0 - total) / len(prs), 60)
    rows = [r + add for r in rows]
    total += add * len(prs)
    c.text(X0, y0, lw, heads[0], "dl", TEAL, "left")
    c.text(rx, y0, rw, heads[1], "dl", TEAL, "left")
    y = y0 + 58
    for (l, r), h in zip(prs, rows):
        c.rect(X0, y, lw, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=14)
        c.text(X0 + 22, y + (h - c.lines(l, lw - 44, 34) * 44.2) / 2, lw - 44, l, "dt", TEAL, "left", (X0, y, lw, h))
        c.rect(rx, y, rw, h, fill=DEEP, rx=14)
        c.text(rx + 22, y + (h - c.lines(r, rw - 44, 34) * 44.2) / 2, rw - 44, r, "dn", CREAM, "left", (rx, y, rw, h))
        c.arrow(X0 + lw + 10, y + h / 2, rx - 10, y + h / 2, color=GOLD, sw=5)
        y += h + 18
    if foot:
        good = foot.get("tone") == "good"
        y += fgap - 18
        c.textbox(X0, y, X1 - X0, foot["text"], foot.get("sub"), fill=GOLD if good else DEEP, tcolor=DEEP if good else CREAM,
                  scolor=DEEP if good else LIGHT, align="center", h=fh)
        return y + fh
    return y0 + total


# ------------------------------------------------------------------ samples / paths（左右兩個小面板）
def _panel_labels(c: Canvas, nodes, y_label, pw=440, gap=40):
    xs = [X0, X0 + pw + gap]
    for k, n in enumerate(nodes):
        l1 = c.lines(n["text"], pw - 20, 34)
        c.text(xs[k] + 10, y_label, pw - 20, n["text"], "dn", DEEP, "center")
        if n.get("sub"):
            c.text(xs[k] + 10, y_label + l1 * 44.2 + 6, pw - 20, n["sub"], "ds", DEEP, "center")
    return max(c.lines(n["text"], pw - 20, 34) * 44.2 + (c.lines(n["sub"], pw - 20, 28) * 39.2 + 6 if n.get("sub") else 0) for n in nodes)


def samples(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    pw, gap, ph = 440, 40, 340
    ph = min(560, max(ph, BOTTOM - y0 - 140))
    lab = max(c.lines(n["text"], pw - 20, 34) * 44.2 + (c.lines(n["sub"], pw - 20, 28) * 39.2 + 6 if n.get("sub") else 0) for n in nodes)
    total = ph + 20 + lab
    _fit(total, BOTTOM - y0, "samples")
    xs = [X0, X0 + pw + gap]
    for x in xs:
        c.rect(x, y0, pw, ph, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
        c.text(x + 18, y0 + 10, 120, "示意", "ds", TEAL)
    # 左：一個點
    cx, cy = xs[0] + pw / 2, y0 + ph / 2 + 24
    c.circle(cx, cy, 30, fill=TEAL)
    c.text(xs[0], y0 + 34, pw, "？", "dv", TEAL, "center")
    # 右：一批點與方向
    pts = [(0.10, 0.80), (0.18, 0.62), (0.26, 0.74), (0.34, 0.56), (0.42, 0.66), (0.50, 0.46), (0.58, 0.58),
           (0.66, 0.36), (0.74, 0.50), (0.82, 0.28), (0.90, 0.40), (0.30, 0.44), (0.62, 0.72), (0.78, 0.66)]
    gx, gy, gw, gh = xs[1] + 30, y0 + 30, pw - 60, ph - 60
    for fx, fy in pts:
        c.circle(gx + fx * gw, gy + fy * gh, 13, fill=MID)
    c.arrow(gx + 0.04 * gw, gy + 0.90 * gh, gx + 0.98 * gw, gy + 0.18 * gh, color=DEEP, sw=5, head=18)
    _panel_labels(c, nodes, y0 + ph + 20)
    return y0 + total


def paths(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    pw, gap, ph = 440, 40, 360
    ph = min(580, max(ph, BOTTOM - y0 - 140))
    lab = max(c.lines(n["text"], pw - 20, 34) * 44.2 + (c.lines(n["sub"], pw - 20, 28) * 39.2 + 6 if n.get("sub") else 0) for n in nodes)
    total = ph + 20 + lab
    _fit(total, BOTTOM - y0, "paths")
    xs = [X0, X0 + pw + gap]
    for x in xs:
        c.rect(x, y0, pw, ph, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
        c.text(x + 18, y0 + 10, 120, "示意", "ds", TEAL)
    S, T = (60.0, ph - 60.0), (pw - 80.0, 90.0)
    nx, ny = (T[1] - S[1]), -(T[0] - S[0])
    nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl

    def path(kind):
        out = []
        n = 7
        for i in range(n):
            t = i / (n - 1)
            sgn = 1 if i % 2 else -1
            if kind == "wild":
                off = sgn * (14 + 26 * i) * (1 if i else 0)
            else:
                off = sgn * 70 * (1 - t) ** 1.6 * (1 if i else 0)
            out.append((S[0] + (T[0] - S[0]) * t + nx * off, S[1] + (T[1] - S[1]) * t + ny * off))
        return out

    for k, kind in enumerate(("wild", "steady")):
        ox, oy = xs[k], y0
        P = path(kind)
        for ring_r, op in ((40, .35), (24, .55)):
            c.circle(ox + T[0], oy + T[1], ring_r, stroke=DEEP, sw=3, op=0, dash=None)
        pts = [(ox + x, oy + y) for x, y in P]
        c.poly(pts, stroke=TEAL if kind == "steady" else DEEP, sw=4)
        for x, y in pts[:-1]:
            c.circle(x, y, 8, fill=TEAL if kind == "steady" else DEEP)
        ex, ey = pts[-1]
        if kind == "steady":
            c.circle(ex, ey, 44, fill=GOLD, op=.30)
            c.circle(ex, ey, 15, fill=GOLD)
        else:
            c.line(ex - 14, ey - 14, ex + 14, ey + 14, DEEP, 5)
            c.line(ex - 14, ey + 14, ex + 14, ey - 14, DEEP, 5)
    _panel_labels(c, nodes, y0 + ph + 20)
    return y0 + total


# ------------------------------------------------------------------ epochs
def epochs(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    leg = max(c.lines(n["text"], 420, 28) for n in nodes) * 39.2
    h = max(300, min(600, BOTTOM - y0 - 24 - leg))
    total = h + 24 + leg
    _fit(total, BOTTOM - y0, "epochs")
    c.rect(X0, y0, X1 - X0, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    c.text(X0 + 18, y0 + 10, 160, "示意", "ds", TEAL)
    bx0, bx1 = X0 + 90, X1 - 40
    base = y0 + h - 70
    top = y0 + 100
    c.arrow(bx0 - 24, base, bx0 - 24, top - 10, DEEP, 3, 12)          # 縱軸：表現
    c.text(X0 + 150, y0 + 10, 140, "表現", "ds", DEEP)
    c.line(bx0 - 24, base, bx1, base, DEEP, 3)
    n = 45
    pts = []
    for i in range(n):
        t = i / (n - 1)
        up = 1 - math.exp(-3.0 * t)                                     # 整體慢慢變好
        dip = 0.20 * math.exp(-((t - 0.285) / 0.035) ** 2) + 0.20 * math.exp(-((t - 0.615) / 0.035) ** 2)   # 兩次小退步（在慢檢查之前）
        wig = 0.02 * math.sin(i * 2.1)
        y = base - 40 - (base - top - 60) * max(0.05, min(0.97, up * 0.9 - dip + wig))
        pts.append((bx0 + (bx1 - bx0) * t, y))
    c.poly(pts, stroke=TEAL, sw=3)
    for x, y in pts:
        c.circle(x, y, 6, fill=TEAL)
    for k in (1, 2):
        x = bx0 + (bx1 - bx0) * k / 3
        c.line(x, top - 20, x, base, GOLD, 5)
        c.poly([(x, top - 36), (x + 14, top - 20), (x, top - 4), (x - 14, top - 20)], fill=GOLD, closed=True)
    c.text(X1 - 340, base + 14, 300, "訓練時間", "ds", DEEP, "right")
    lx = [X0, X0 + 480]
    for k, nd in enumerate(nodes):
        c.text(lx[k] + 6, y0 + h + 24, 420, nd["text"], "ds", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ dotgrid
def dotgrid(c: Canvas, spec: dict, y0: float) -> float:
    n = spec["count"]
    cols = int(spec.get("cols") or (13 if n > 40 else 10))      # cols（選用）：每列幾個點，例如 20 篇 × 4 種配置排成 20 欄 4 列
    rows = math.ceil(n / cols)
    legs = spec["nodes"]
    leg_h = [c.lines(l["text"], X1 - X0 - 70, 34) * 44.2 for l in legs]
    avail = BOTTOM - y0 - sum(leg_h) - 40 * len(legs) - 10
    pitch = min(72, avail / rows, (X1 - X0) / cols)
    r = pitch * 0.36
    gw = (cols - 1) * pitch
    gx = X0 + (X1 - X0 - gw) / 2
    gh = (rows - 1) * pitch + 2 * r
    total = gh + 34 + sum(leg_h) + 24 * (len(legs) - 1) + 10
    _fit(total, BOTTOM - y0, "dotgrid")
    on = spec.get("on", n)                                      # on（選用）：前幾個點實心，其餘空心（例：100 次裡 27 次平手）
    if not 0 <= on <= n:
        raise ValueError(f"dotgrid 的 on 要在 0～{n} 之間，現在是 {on}")
    for i in range(n):
        if i < on:
            c.circle(gx + (i % cols) * pitch, y0 + r + (i // cols) * pitch, r, fill=MID)
        else:
            c.circle(gx + (i % cols) * pitch, y0 + r + (i // cols) * pitch, r - 2, fill="none", stroke=DEEP, sw=3)
    y = y0 + gh + 34
    for k, l in enumerate(legs):
        if k == 0:
            c.circle(X0 + 22, y + 22, 18, fill=MID)
        else:
            c.circle(X0 + 22, y + 22, 18, fill="none", stroke=DEEP, sw=4)
        c.text(X0 + 70, y, X1 - X0 - 70, l["text"], "dn", DEEP, "left")
        y += leg_h[k] + 24
    return y0 + total


# ------------------------------------------------------------------ dumbbell / range（比例由程式 B 檢查）
def _axis(c: Canvas, x0, x1, y, amax, unit, ticks):
    c.line(x0, y, x1, y, DEEP, 3)
    s = (x1 - x0) / amax
    for v in ticks:
        x = x0 + v * s
        c.line(x, y, x, y + 14, DEEP, 3)
        c.text(x - 50, y + 20, 100, f"{v:g}", "ds", DEEP, "center")
    return s


def _ticks(amax: float) -> list[float]:
    raw = amax / 4
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=raw)
    n = int(amax / step + 1e-9)
    return [step * k for k in range(n + 1)]


def dumbbell(c: Canvas, spec: dict, y0: float) -> float:
    a, b = spec["points"]
    ref = spec["ref"]
    amax = spec.get("axis_max", 100)
    unit = spec.get("unit", "")
    x0, x1 = 120, 980
    s = (x1 - x0) / amax
    ay = y0 + min(520, max(380, BOTTOM - y0 - 190))
    _fit(ay + 150 - y0, BOTTOM - y0 + 40, "dumbbell")
    ticks = _ticks(amax)
    _axis(c, x0, x1, ay, amax, unit, ticks)
    # 參考線（原地練的版本）：金色虛線，標籤放在軸下方
    rx = x0 + ref["value"] * s
    c.line(rx, ay - 26, rx, ay + 66, GOLD, 5, dash="10 8")
    c.text(rx - 230, ay + 84, 460, f"{ref['name']}：{ref['value']:g}{unit}", "dn", DEEP, "center")
    # 前 → 後
    py = ay - 56
    ax_, bx_ = x0 + a["value"] * s, x0 + b["value"] * s
    c.arrow(ax_ + 24, py, bx_ - 32, py, color=TEAL, sw=7, head=24)
    c.circle(ax_, py, 22, fill=CREAM, stroke=TEAL, sw=7, cls="bg dpt", extra=f' data-v="{a["value"]}" data-x0="{x0}" data-s="{s}"')
    c.circle(bx_, py, 24, fill=DEEP, cls="bg dpt", extra=f' data-v="{b["value"]}" data-x0="{x0}" data-s="{s}"')
    c.text(ax_ - 150, py - 130, 300, f"{a['value']:g}{unit}", "dv", TEAL, "center")
    c.text(bx_ - 150, py - 130, 300, f"{b['value']:g}{unit}", "dv", DEEP, "center")
    c.text(ax_ - 150, py - 188, 300, a["name"], "ds", DEEP, "center")
    c.text(bx_ - 150, py - 188, 300, b["name"], "ds", DEEP, "center")
    return ay + 84 + 60


def range_chart(c: Canvas, spec: dict, y0: float) -> float:
    rows = spec["ranges"]
    amax = spec.get("axis_max", 100)
    unit = spec.get("unit", "")
    x0, x1 = 120, 960
    s = (x1 - x0) / amax
    rh = min(230, max(170, (BOTTOM - y0 - 100) / len(rows)))
    total = len(rows) * rh + 90
    _fit(total, BOTTOM - y0, "range")
    y = y0
    for r in rows:
        nl = c.lines(r["name"], X1 - X0, 34)
        c.text(X0, y, X1 - X0, r["name"], "dn", DEEP, "left")
        sy = y + nl * 44.2 + (c.lines(r["sub"], X1 - X0, 28) * 39.2 + 8 if r.get("sub") else 0) + 18
        if r.get("sub"):
            c.text(X0, y + nl * 44.2 + 8, X1 - X0, r["sub"], "ds", DEEP, "left")
        c.rect(x0, sy, x1 - x0, 36, fill=LIGHT, op=.35, rx=8)
        lo, hi = r["lo"], r["hi"]
        extra = f' data-lo="{lo}" data-hi="{hi}" data-s="{s}" data-x0="{x0}"'
        if lo == hi:
            c.circle(x0 + lo * s, sy + 18, 0.01, cls="bg rbar", extra=extra)
            c.rect(x0 + lo * s - 5, sy - 10, 10, 56, fill=DEEP, rx=4)
        else:
            c.svg.append(f'<rect class="bg rbar" x="{x0 + lo * s:.1f}" y="{sy:.1f}" width="{(hi - lo) * s:.1f}" height="36" rx="8" fill="{GOLD if r.get("emph") else MID}"{extra}/>')
        lab = f"{lo:g}{unit}" if lo == hi else f"{lo:g}～{hi:g}{unit}"
        lx = x0 + hi * s + 16
        if lx + 200 > X1 + 20:
            c.text(x0 + lo * s - 216, sy - 4, 200, lab, "dv2", DEEP, "right")
        else:
            c.text(lx, sy - 4, 220, lab, "dv2", DEEP, "left")
        y += rh
    _axis(c, x0, x1, y + 10, amax, unit, _ticks(amax))
    return y + 10 + 70


# ------------------------------------------------------------------ funnel
def funnel(c: Canvas, spec: dict, y0: float) -> float:
    nodes = spec["nodes"]
    widths = [920, 740, 560, 400][:len(nodes) + 1]
    gap = 14
    sh = min(210, max(150, (BOTTOM - y0 - gap * (len(nodes) - 1)) / len(nodes)))
    total = len(nodes) * sh + gap * (len(nodes) - 1)
    _fit(total, BOTTOM - y0, "funnel")
    fills = [DEEP, TEAL, GOLD] if len(nodes) == 3 else [DEEP, GOLD]
    y = y0
    for i, n in enumerate(nodes):
        wt, wb = widths[i], widths[i + 1]
        cx = X0 + (X1 - X0) / 2
        pts = [(cx - wt / 2, y), (cx + wt / 2, y), (cx + wb / 2, y + sh), (cx - wb / 2, y + sh)]
        fill = fills[min(i, len(fills) - 1)] if len(nodes) == 3 else (DEEP if i < len(nodes) - 1 else GOLD)
        c.poly(pts, fill=fill, closed=True)
        tcol = DEEP if fill == GOLD else CREAM
        iw = wb - 40
        l1 = c.lines(n["text"], iw, 34)
        th = l1 * 44.2 + (c.lines(n["sub"], iw, 28) * 39.2 + 4 if n.get("sub") else 0)
        box = (cx - wb / 2, y, wb, sh)
        c.text(cx - iw / 2, y + (sh - th) / 2, iw, n["text"], "dn", tcol, "center", box)
        if n.get("sub"):
            c.text(cx - iw / 2, y + (sh - th) / 2 + l1 * 44.2 + 4, iw, n["sub"], "ds", tcol, "center", box)
        y += sh + gap
    return y0 + total


# ------------------------------------------------------------------ batches（一個池子切成幾組）
def batches(c: Canvas, spec: dict, y0: float) -> float:
    """count 個點的池子，切成每組 group 個的小組（最後一組可能不滿）。nodes = [{text}（池子是什麼）, {text}（每一組做什麼）]。"""
    n, g = spec["count"], spec["group"]
    k = math.ceil(n / g)
    w = X1 - X0
    top_h = c.lines(spec["nodes"][0]["text"], w, 34) * 44.2
    bot_h = c.lines(spec["nodes"][1]["text"], w, 34) * 44.2
    pool_h, arrow_h, grp_h = 150, 80, 190
    total = top_h + 14 + pool_h + arrow_h + grp_h + 22 + bot_h
    _fit(total, BOTTOM - y0, "batches")
    extra = BOTTOM - y0 - total
    pool_h += min(extra * .3, 60); grp_h += min(extra * .4, 80); arrow_h += min(extra * .3, 40)
    c.text(X0, y0, w, spec["nodes"][0]["text"], "dn", DEEP, "left")
    py = y0 + top_h + 14
    c.rect(X0, py, w, pool_h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    cols = 10
    rows = math.ceil(n / cols)
    pitch = min(48, (pool_h - 40) / max(rows, 1))
    gx = X0 + (w - (cols - 1) * pitch) / 2
    for i in range(n):
        c.circle(gx + (i % cols) * pitch, py + pool_h / 2 - (rows - 1) * pitch / 2 + (i // cols) * pitch, pitch * .3, fill=MID)
    gw = (w - 26 * (k - 1)) / k
    gy = py + pool_h + arrow_h
    left = n
    for j in range(k):
        x = X0 + j * (gw + 26)
        m = min(g, left); left -= m
        c.arrow(X0 + w / 2 + (j - (k - 1) / 2) * 60, py + pool_h + 6, x + gw / 2, gy - 6, color=TEAL, sw=4)
        c.rect(x, gy, gw, grp_h, fill=DEEP if m == g else CREAM, stroke=None if m == g else DEEP, sw=3, dash=None if m == g else "8 8", rx=16)
        pc, pr = 4, 2
        p2 = min(46, (gw - 40) / pc)
        ox = x + (gw - (pc - 1) * p2) / 2
        for i in range(m):
            c.circle(ox + (i % pc) * p2, gy + grp_h / 2 - p2 / 2 + (i // pc) * p2 - 4, p2 * .3, fill=GOLD if m == g else MID)
    c.text(X0, gy + grp_h + 22, w, spec["nodes"][1]["text"], "dn", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ decay（預算隨訓練慢慢變小）
def decay(c: Canvas, spec: dict, y0: float) -> float:
    """start→end 的平滑下降曲線（高度與數值成正比，軸從 0 起）。nodes = [{text}（初期）, {text}（後期）]，unit、axis_max。"""
    a, b, unit, amax = spec["start"], spec["end"], spec.get("unit", ""), spec.get("axis_max", 5)
    leg = max(c.lines(nd["text"], 420, 34) for nd in spec["nodes"]) * 44.2
    h = max(360, min(640, BOTTOM - y0 - 30 - leg))
    total = h + 30 + leg
    _fit(total, BOTTOM - y0, "decay")
    c.rect(X0, y0, X1 - X0, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    c.text(X0 + 18, y0 + 10, 160, "示意", "ds", TEAL)
    bx0, bx1 = X0 + 110, X1 - 50
    base = y0 + h - 56
    sc = (h - 56 - 90) / amax                              # 每 1 個單位的高度（零點在 base）
    c.line(bx0 - 24, base, bx1, base, DEEP, 3)
    c.line(bx0 - 24, base, bx0 - 24, base - amax * sc, DEEP, 3)
    c.text(bx0 - 50, base + 8, 50, "0", "ds", DEEP, "center")
    n = 40
    pts = []
    for i in range(n):
        t = i / (n - 1)
        v = b + (a - b) * (1 + math.cos(math.pi * t)) / 2
        pts.append((bx0 + (bx1 - bx0) * t, base - v * sc))
    c.poly([(pts[0][0], base)] + pts + [(pts[-1][0], base)], fill=LIGHT, closed=True, op=.35)
    c.poly(pts, stroke=TEAL, sw=5)
    for v, x, al in ((a, pts[0][0], "left"), (b, pts[-1][0], "right")):
        y = base - v * sc
        c.line(bx0 - 24, y, bx1, y, GOLD, 3, dash="10 8", op=.8)
    c.circle(pts[0][0], pts[0][1], 14, fill=GOLD)
    c.circle(pts[-1][0], pts[-1][1], 14, fill=GOLD)
    c.text(pts[0][0] - 8, pts[0][1] - 78, 150, f"{a:g}{unit}", "dv", DEEP, "left")
    c.text(pts[-1][0] - 142, pts[-1][1] - 104, 150, f"{b:g}{unit}", "dv", DEEP, "right")
    c.text(X1 - 340, base + 8, 290, "訓練時間 →", "ds", DEEP, "right")
    for k, nd in enumerate(spec["nodes"]):
        c.text(X0 + k * 480 + 6, y0 + h + 30, 440, nd["text"], "dn", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ stops（一條軸上的三個位置，中間那個是被選的）
def stops(c: Canvas, spec: dict, y0: float) -> float:
    """由上往下三個停靠點：nodes = [{text, sub?, emph?}]；heads = [上端標籤, 下端標籤]（選用）。不按比例。"""
    nodes, heads = spec["nodes"], spec.get("heads", [])
    cw = X1 - X0 - 90
    head_h = 40
    hs = [c.lines(n["text"], cw - 44, 34) * 44.2 + (c.lines(n["sub"], cw - 44, 28) * 39.2 + 6 if n.get("sub") else 0) + 44 for n in nodes]
    gap = 26
    total = sum(hs) + gap * (len(nodes) - 1) + ((head_h + 8) * len(heads))
    _fit(total, BOTTOM - y0, "stops")
    extra = BOTTOM - y0 - total
    add = min(extra / len(nodes), 70)
    hs = [h + add for h in hs]
    y = y0
    cx = X0 + 22
    if heads:
        c.text(X0 + 60, y - 4, cw, heads[0], "ds", TEAL, "left"); y += head_h + 8
    top = y
    ys = []
    for h in hs:
        ys.append((y, h)); y += h + gap
    c.line(cx, top + hs[0] / 2, cx, ys[-1][0] + hs[-1] / 2, TEAL, 5)
    for (yy, h), n in zip(ys, nodes):
        emph = n.get("emph")
        c.circle(cx, yy + h / 2, 22 if emph else 14, fill=GOLD if emph else CREAM, stroke=None if emph else TEAL, sw=5)
        c.textbox(X0 + 70, yy, cw, n["text"], n.get("sub"), fill=GOLD if emph else CREAM, tcolor=DEEP,
                  scolor=DEEP, stroke=None if emph else DEEP, dash=None if emph else "8 8", h=h)
    if heads:
        c.text(X0 + 60, y - gap + 12, cw, heads[1], "ds", TEAL, "left"); y += head_h - gap + 12
    return min(y, y0 + total)


# ------------------------------------------------------------------ fan（幾組同時做事，再匯成一份）
def fan(c: Canvas, spec: dict, y0: float) -> float:
    """heads = 2～4 個組別標籤（同時進行）；nodes = [{text}（組別上方的說明）, {text, sub?}（匯整後的結果）]。"""
    heads, (top, res) = spec["heads"], spec["nodes"]
    k = len(heads)
    w = X1 - X0
    th = c.lines(top["text"], w, 34) * 44.2
    rh = c.lines(res["text"], w - 44, 34) * 44.2 + (c.lines(res["sub"], w - 44, 28) * 39.2 + 6 if res.get("sub") else 0) + 44
    gh, ah = 150, 90
    total = th + 16 + gh + ah + rh
    _fit(total, BOTTOM - y0, "fan")
    extra = BOTTOM - y0 - total
    gh += min(extra * .35, 70); ah += min(extra * .35, 70); rh += min(extra * .3, 50)
    c.text(X0, y0, w, top["text"], "dn", DEEP, "left")
    gy = y0 + th + 16
    gw = (w - 24 * (k - 1)) / k
    ry = gy + gh + ah
    for j, h in enumerate(heads):
        x = X0 + j * (gw + 24)
        c.textbox(x, gy, gw, h, fill=DEEP, tcolor=CREAM, align="center", h=gh)
        c.arrow(x + gw / 2, gy + gh + 4, X0 + w / 2 + (j - (k - 1) / 2) * 90, ry - 6, color=TEAL, sw=4)
    c.textbox(X0, ry, w, res["text"], res.get("sub"), fill=GOLD, tcolor=DEEP, scolor=DEEP, align="center", h=rh)
    return y0 + total


# ------------------------------------------------------------------ peaks（兩條曲線的最高點落在同一處；純示意）
def peaks(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = [{text}（第一條線）, {text}（第二條線）, {text}（最高點的標籤）]。兩條曲線形狀不同、最高點在同一個位置（示意，不是實驗數據）。"""
    n1, n2, nl = spec["nodes"]
    leg = 2 * 56 + 20
    h = max(380, min(640, BOTTOM - y0 - 30 - leg))
    total = h + 30 + leg
    _fit(total, BOTTOM - y0, "peaks")
    c.rect(X0, y0, X1 - X0, h, fill="none", stroke=DEEP, sw=3, dash="8 8", rx=18)
    c.text(X0 + 18, y0 + 10, 160, "示意", "ds", TEAL)
    bx0, bx1 = X0 + 60, X1 - 50
    base = y0 + h - 60
    top = y0 + 130
    c.line(bx0 - 20, base, bx1, base, DEEP, 3)
    c.text(X1 - 420, base + 8, 380, "訓練過程中的各個版本 →", "ds", DEEP, "right")
    n = 30
    pk = 19
    def curve(amp, wob, ph):
        out = []
        for i in range(n):
            t = i / (n - 1)
            v = 0.25 + 0.55 * (math.exp(-((i - pk) / 7.5) ** 2) if i >= pk else math.exp(-((i - pk) / 11.0) ** 2)) + wob * math.sin(i * 1.7 + ph)
            out.append(v)
        m = max(out)
        out = [v if i == pk else min(v, m * 0.0 + v) for i, v in enumerate(out)]
        out[pk] = max(out) + 0.02                         # 最高點一定在 pk
        return [(bx0 + (bx1 - bx0) * i / (n - 1), base - 30 - (base - top - 40) * min(v, 1.0)) for i, v in enumerate(out)]
    a, b = curve(1, 0.035, 0.4), curve(1, 0.05, 2.0)
    px = a[pk][0]
    c.line(px, top - 30, px, base, GOLD, 5, dash="10 8")
    c.circle(px, a[pk][1], 14, fill=GOLD)
    c.circle(px, b[pk][1], 14, fill=GOLD)
    c.text(px - 200, top - 86, 400, nl["text"], "dn", DEEP, "center")
    c.poly(a, stroke=MID, sw=5)
    c.poly(b, stroke=DEEP, sw=5)
    ly = y0 + h + 30
    for k, (nd, col) in enumerate(((n1, MID), (n2, DEEP))):
        c.line(X0, ly + 22 + k * 56, X0 + 60, ly + 22 + k * 56, col, 6)
        c.text(X0 + 80, ly + k * 56, X1 - X0 - 80, nd["text"], "dn", DEEP, "left")
    return y0 + total


# ------------------------------------------------------------------ quad（2×2 四個格子，可標一格為重點）
def quad(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 4 個格子 [{text, sub?, emph?, bars?}]，依序是左上、右上、左下、右下。
    bars（選用，2026-10-14）：格子上方畫一張小投影片，條列數 = bars（長版多、短版少），讓格子不只是字。"""
    nodes = spec["nodes"]
    gap = 24
    cw = (X1 - X0 - gap) / 2
    ICON_H = 190                                           # 小投影片（約 150）加上下留白
    rows = []
    for r in range(2):
        pair = nodes[r * 2:r * 2 + 2]
        rows.append(max(c.lines(nd["text"], cw - 44, 34) * 44.2 + (c.lines(nd["sub"], cw - 44, 28) * 39.2 + 6 if nd.get("sub") else 0) + 60
                        + (ICON_H if nd.get("bars") else 0) for nd in pair))
    total = sum(rows) + gap
    _fit(total, BOTTOM - y0, "quad")
    extra = BOTTOM - y0 - total
    rows = [r + min(extra / 2, 150) for r in rows]
    y = y0
    for r in range(2):
        for k in range(2):
            nd = nodes[r * 2 + k]
            emph = nd.get("emph")
            x = X0 + k * (cw + gap)
            if not nd.get("bars"):
                c.textbox(x, y, cw, nd["text"], nd.get("sub"), fill=GOLD if emph else CREAM, tcolor=DEEP,
                          scolor=DEEP, stroke=None if emph else DEEP, dash=None if emph else "8 8", align="center", h=rows[r])
                continue
            h = rows[r]
            c.rect(x, y, cw, h, fill=GOLD if emph else CREAM, stroke=None if emph else DEEP, dash=None if emph else "8 8")
            k = 1.45                                            # 小投影片的放大倍數
            iw, ih = 168 * k, 104 * k
            l1 = c.lines(nd["text"], cw - 44, 34)
            th = l1 * 44.2 + (c.lines(nd["sub"], cw - 44, 28) * 39.2 + 6 if nd.get("sub") else 0)
            grp = ih + 18 + th                                  # 小投影片加文字，整組在格子裡垂直置中
            ix, iy = x + (cw - iw) / 2, y + max(14, (h - grp) / 2)
            c.rect(ix, iy, iw, ih, fill=DEEP, rx=12 * k)
            c.rect(ix + 16 * k, iy + 14 * k, iw * .42, 8 * k, fill=CREAM, rx=4 * k)
            n = int(nd["bars"])
            gp = (ih - 38 * k) / max(n, 1)
            for i in range(n):
                cy = iy + 28 * k + gp * i + gp / 2
                c.circle(ix + 20 * k, cy, 4 * k, fill=CREAM)
                c.rect(ix + 34 * k, cy - 3.5 * k, iw - 50 * k - (i % 3) * 14 * k, 7 * k, fill=CREAM, rx=3.5 * k, op=.8)
            ty = iy + ih + 18
            box = (x, y, cw, h)
            c.text(x + 22, ty, cw - 44, nd["text"], "dn", DEEP, "center", box)
            if nd.get("sub"):
                c.text(x + 22, ty + l1 * 44.2 + 6, cw - 44, nd["sub"], "ds", DEEP, "center", box)
        y += rows[r] + gap
    return y - gap


# ------------------------------------------------------------------ locked（文件裡一塊受保護的區塊）
def locked(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [被擋下的來源, 能更新的來源]；nodes = [{text}（文件名）, {text}（受保護區塊）]。"""
    (hl, hr), (doc, blk) = spec["heads"], spec["nodes"]
    w = X1 - X0
    sw = (w - 40) / 2
    sh = max(c.lines(hl, sw - 36, 34), c.lines(hr, sw - 36, 34)) * 44.2 + 36
    bh = c.lines(blk["text"], w - 150, 34) * 44.2 + 50
    gap = 70
    dh = 62 + 36 + 2 * 34 + 18 + bh + 18 + 34 + 16
    total = sh + gap + dh
    _fit(total, BOTTOM - y0, "locked")
    extra = BOTTOM - y0 - total
    gap += min(extra * .3, 50)
    more = int(min(extra * .7, 170) // 34)                  # 文件下半部多畫幾行灰線，把空間用滿
    dh += more * 34
    c.textbox(X0, y0, sw, hl, fill=CREAM, tcolor=DEEP, stroke=DEEP, dash="8 8", align="center", h=sh)
    c.textbox(X0 + sw + 40, y0, sw, hr, fill=DEEP, tcolor=CREAM, align="center", h=sh)
    dy = y0 + sh + gap
    c.rect(X0, dy, w, dh, fill=CREAM, stroke=DEEP, sw=4, rx=20)
    c.text(X0 + 30, dy + 12, 320, doc["text"], "ds", TEAL, "left")
    ly = dy + 62
    for i in range(2):
        c.rect(X0 + 40, ly + i * 34, w - 80 - (i * 90 % 200), 14, fill=LIGHT, op=.55, rx=7)
    by = ly + 2 * 34 + 12
    c.rect(X0 + 28, by, w - 56, bh, fill=GOLD, rx=14)
    c.text(X0 + 60, by + (bh - c.lines(blk["text"], w - 150, 34) * 44.2) / 2, w - 150, blk["text"], "dn", DEEP, "left", (X0 + 28, by, w - 56, bh))
    ly2 = by + bh + 24
    for i in range(1 + more):
        c.rect(X0 + 40, ly2 + i * 34, w - 80 - ((i + 1) * 110 % 260), 14, fill=LIGHT, op=.55, rx=7)
    # 左邊的箭頭被擋下（×），右邊的箭頭到達受保護區塊
    lx, rx = X0 + sw / 2, X0 + sw + 40 + sw / 2
    my = y0 + sh + gap * 0.5                            # ×（被擋下）畫在文件上緣之上，不壓到文件裡的字
    c.line(lx, y0 + sh + 6, lx, my - 22, TEAL, 4)
    c.line(lx - 18, my - 18, lx + 18, my + 18, DEEP, 7)
    c.line(lx - 18, my + 18, lx + 18, my - 18, DEEP, 7)
    c.arrow(rx, y0 + sh + 6, rx, by + 8 + (dy - (y0 + sh)) * 0 , color=GOLD, sw=6, head=20)
    return y0 + total


# ------------------------------------------------------------------ equation（算式：A × B ＝ C，底下可接一行補充）
def equation(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 算元 [{text（大數字）, sub（單位或名稱）, sub2?（小字說明）, emph?}]；ops（選用，預設 ["×", "="]）；
    outcomes[0]（選用）= 底下一條橫框 {text, sub?}。2026-10-14 新增：點陣排成方陣說不出「幾乘幾等於幾」，算式圖才是這個畫面。"""
    nodes, ops = spec["nodes"], spec.get("ops", ["×", "="])
    foot = (spec.get("outcomes") or [None])[0]
    n, opw, w = len(nodes), 88, X1 - X0
    bw = (w - opw * (n - 1)) / n
    iw = bw - 36
    hs = [90 + c.lines(nd["sub"], iw, 34) * 44.2 + (c.lines(nd["sub2"], iw, 28) * 39.2 + 6 if nd.get("sub2") else 0) + 56 for nd in nodes]
    bh = max(hs)
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    gap = 34 if foot else 0
    total = bh + gap + fh
    _fit(total, BOTTOM - y0, "equation")
    extra = BOTTOM - y0 - total
    bh += min(extra * .5, 140)
    twm = max(90 + c.lines(nd["sub"], iw, 34) * 44.2 + (c.lines(nd["sub2"], iw, 28) * 39.2 + 6 if nd.get("sub2") else 0) for nd in nodes)   # 三個算元的數字對齊在同一高度
    for i, nd in enumerate(nodes):
        x = X0 + i * (bw + opw)
        emph = nd.get("emph")
        c.rect(x, y0, bw, bh, fill=GOLD if emph else CREAM, stroke=None if emph else DEEP, dash=None if emph else "8 8")
        ty = y0 + (bh - twm) / 2
        box = (x, y0, bw, bh)
        c.text(x + 18, ty, iw, nd["text"], "dv", DEEP, "center", box)
        c.text(x + 18, ty + 90, iw, nd["sub"], "dn", DEEP, "center", box)
        if nd.get("sub2"):
            c.text(x + 18, ty + 90 + c.lines(nd["sub"], iw, 34) * 44.2 + 6, iw, nd["sub2"], "ds", DEEP, "center", box)
        if i < n - 1:
            c.text(x + bw + 8, y0 + bh / 2 - 40, opw - 16, ops[i], "dv", DEEP, "center")
    y = y0 + bh
    if foot:
        y += gap
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ tokens（符號序列：一列一步，每格一個符號）
TOKEN_TONES = {   # tone → (fill, stroke, dash, 主字色, 小字色)
    "rtg":    (TEAL, None, None, CREAM, CREAM),
    "state":  (DEEP, None, None, CREAM, LIGHT),
    "action": (CREAM, DEEP, None, DEEP, DEEP),
    "reward": (LIGHT, None, None, DEEP, DEEP),
    "mask":   (GOLD, None, None, DEEP, DEEP),
}


def tokens(c: Canvas, spec: dict, y0: float) -> float:
    """steps = [{label（列首小字，例如「第一步」）, cells:[{text, sub?, tone}]}]，一列一步、每格一個符號；
    tone：rtg／state／action／reward／mask（mask＝被蓋住、要模型猜的那格，金色）；more（選用，true）＝最後一列後面畫三個點，表示還有下去；
    outcomes[0]（選用）＝底下一條橫框 {text, sub?, tone?}（tone: good 金色，否則深海）。
    2026-10-18 新增（Decision Transformer）：「交錯排列的序列」「蓋住其中一格」是符號序列，流程圖與表格說不出這個畫面。"""
    steps, foot, more = spec["steps"], (spec.get("outcomes") or [None])[0], bool(spec.get("more"))
    w, lw, gap, vgap, pad = X1 - X0, 120, 16, 30, 14
    ncell = max(len(s["cells"]) for s in steps)
    cw = (w - lw - gap * (ncell - 1)) / ncell
    iw = cw - 2 * pad

    def ch(cell):
        return c.lines(cell["text"], iw, 34) * 44.2 + (c.lines(cell["sub"], iw, 28) * 39.2 + 6 if cell.get("sub") else 0) + 2 * pad + 8
    hs = [max(ch(cell) for cell in s["cells"]) for s in steps]
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    more_h = 64 if more else 0
    total = sum(hs) + vgap * (len(steps) - 1) + more_h + (vgap + fh if foot else 0)
    _fit(total, BOTTOM - y0, "tokens")
    extra = BOTTOM - y0 - total
    add = min(extra * .6 / len(steps), 60)
    hs = [h + add for h in hs]
    vg = vgap + min((extra - add * len(steps)) / max(len(steps) - 1 + (1 if foot else 0) + (1 if more else 0), 1), 30)
    y = y0
    ax = X0 + 44                                         # 列首小字下方的箭頭（一步接一步）
    for i, st in enumerate(steps):
        h = hs[i]
        c.text(X0, y + h / 2 - 20, lw - 8, st["label"], "ds", TEAL, "left")
        for k, cell in enumerate(st["cells"]):
            fill, stroke, dash, tc, sc = TOKEN_TONES[cell.get("tone", "state")]
            c.textbox(X0 + lw + k * (cw + gap), y, cw, cell["text"], cell.get("sub"), fill=fill, tcolor=tc, scolor=sc,
                      stroke=stroke, dash=dash, align="center", pad=pad, h=h)
        y += h
        if i < len(steps) - 1 or more:
            c.arrow(ax, y + 4, ax, y + vg - 4, TEAL, 4, 12)
            y += vg
    if more:
        for j in range(3):
            c.circle(ax, y + 8 + j * 18, 5, fill=TEAL)
        y += more_h
    if foot:
        y += vg if not more else 18
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=GOLD if foot.get("tone") == "good" else DEEP,
                  tcolor=DEEP if foot.get("tone") == "good" else CREAM, scolor=DEEP if foot.get("tone") == "good" else LIGHT, align="center", h=fh)
        y += fh
    return y


# ------------------------------------------------------------------ seesaw（蹺蹺板：兩端各疊幾塊，梁向重的一邊傾斜；下面一條橫條是贏的機率）
def _stack(c: Canvas, x, base_y, n, u, fill, cols):
    """從 base_y（梁的上緣）往上疊 n 塊（每列 cols 塊）。"""
    for i in range(n):
        col, row = i % cols, i // cols
        c.rect(x + col * u, base_y - (row + 1) * u, u - 4, u - 4, fill=fill, rx=max(3, u * .1))


def seesaw(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = [{text（隊名）, sub?（實力值）, blocks（方塊數）, win（贏的機率標籤，放在下面橫條裡）}, {…}]。
    第一個是重的一端（左），第二個是輕的一端（右，金色）。傾斜角 = 16° x（重 − 輕）/（重 ＋ 輕），最多 14°；純示意。
    橫條的長度與兩端方塊數的比例成正比（左：深海、右：金色）；outcomes[0]（選用）= 底下一條橫框 {text, sub?}。"""
    (a, b), foot = spec["nodes"], (spec.get("outcomes") or [None])[0]
    na, nb = int(a["blocks"]), int(b["blocks"])
    w = X1 - X0
    ca, cb = (2 if na > 3 else 1), (2 if nb > 3 else 1)
    ra, rb = math.ceil(na / ca), math.ceil(nb / cb)
    tilt = min(14.0, 16.0 * (na - nb) / (na + nb))
    L = 800.0
    lab_h = max(c.lines(n["text"], 330, 34) * 44.2 + (c.lines(n["sub"], 330, 28) * 39.2 + 6 if n.get("sub") else 0) for n in (a, b))
    bar_h = 84
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    avail = BOTTOM - y0
    fixed = lab_h + 16 + 34 + bar_h + (30 + fh if foot else 0)
    u = max(28.0, min(52.0, (avail - fixed - 120) / (max(ra, rb) + 1.2)))      # 方塊大小：依剩下的高度決定
    drop = (L / 2) * math.sin(math.radians(tilt))
    top = max(ra * u - drop, rb * u + drop) + 8                                   # 梁中心以上要留的高度
    fk = 70.0                                                                       # 支點高度
    zone = top + max(fk, drop + 20)
    total = zone + 16 + lab_h + 34 + bar_h + (30 + fh if foot else 0)
    _fit(total, avail, "seesaw")
    cx, cy = X0 + w / 2, y0 + top
    thick = 14
    parts = []
    ux = cx - L / 2 + u * .5
    rx_ = cx + L / 2 - u * .5 - cb * u
    inner = Canvas(c.ctx)
    _stack(inner, ux, cy - thick / 2, na, u, TEAL, ca)
    _stack(inner, rx_, cy - thick / 2, nb, u, GOLD, cb)
    inner.rect(cx - L / 2, cy - thick / 2, L, thick, fill=DEEP, rx=thick / 2)
    c.raw(f'<g transform="rotate({-tilt:.2f} {cx:.1f} {cy:.1f})">' + "".join(inner.svg) + '</g>')
    c.poly([(cx, cy + 2), (cx - fk * .65, cy + fk), (cx + fk * .65, cy + fk)], fill=TEAL, closed=True)
    fy = cy + max(fk, drop + 20)
    c.line(cx - L / 2 - 20, fy, cx + L / 2 + 20, fy, DEEP, 4)
    # 兩端的標籤：放在梁兩端下方的地線之下，置中對齊各自的方塊堆
    ex = [cx - (L / 2) * math.cos(math.radians(tilt)) + u, cx + (L / 2) * math.cos(math.radians(tilt)) - u]
    y = fy + 16
    for ex_, n in zip(ex, (a, b)):
        l1 = c.lines(n["text"], 330, 34)
        c.text(ex_ - 165, y, 330, n["text"], "dn", DEEP, "center")
        if n.get("sub"):
            c.text(ex_ - 165, y + l1 * 44.2 + 6, 330, n["sub"], "ds", DEEP, "center")
    y += lab_h + 34
    # 贏的機率橫條：兩段的寬度與方塊數的比例成正比
    wa = w * na / (na + nb)
    c.rect(X0, y, wa, bar_h, fill=DEEP, rx=14)
    c.rect(X0 + wa, y, w - wa, bar_h, fill=GOLD, rx=14)
    c.text(X0 + 14, y + (bar_h - 44) / 2, wa - 28, a["win"], "dn", CREAM, "center", (X0, y, wa, bar_h))
    c.text(X0 + wa + 8, y + (bar_h - 39) / 2, w - wa - 16, b["win"], "dl", DEEP, "center", (X0 + wa, y, w - wa, bar_h))
    y += bar_h
    if foot:
        y += 30
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ hidden（水面上看得到的，水面下看不到的）
def hidden(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [上標籤, 下標籤]；nodes = 水面上的結果 [{text}]（1～3 個）；outcomes = 水面下藏著的東西 [{text, sub?}]（1～3 個，畫成虛線框的「？」）。"""
    h_up, h_dn = spec["heads"]
    res, hid = spec["nodes"], spec["outcomes"]
    w = X1 - X0
    gap = 20
    cw = (w - gap * (len(res) - 1)) / len(res)
    rh = max(c.lines(r["text"], cw - 36, 34) for r in res) * 44.2 + 40
    hw = (w - gap * (len(hid) - 1)) / len(hid)
    hh = 96 + max(c.lines(n["text"], hw - 28, 34) * 44.2 + (c.lines(n["sub"], hw - 28, 28) * 39.2 + 6 if n.get("sub") else 0) for n in hid) + 36
    top = 46 + rh + 50                                  # 標籤 + 結果 + 水面上的留白
    sea_head = 54
    total = top + 18 + sea_head + hh + 24
    avail = BOTTOM - y0
    _fit(total, avail, "hidden")
    extra = avail - total
    rh += min(extra * .3, 40); hh += min(extra * .4, 60)
    top = 46 + rh + 50
    sea_y = y0 + top
    sea_h = (BOTTOM - sea_y) if extra > 0 else (18 + sea_head + hh + 24)
    c.text(X0, y0, w, h_up, "ds", TEAL, "left")
    for k, r in enumerate(res):
        x = X0 + k * (cw + gap)
        c.rect(x, y0 + 46, cw, rh, fill=CREAM, stroke=DEEP, sw=3, rx=14)
        l1 = c.lines(r["text"], cw - 36, 34)
        c.text(x + 18, y0 + 46 + (rh - l1 * 44.2) / 2, cw - 36, r["text"], "dt", DEEP, "center", (x, y0 + 46, cw, rh))
    # 水面：一條浪線，浪線下面是深海色的面板
    pts = [(X0 + i * w / 40, sea_y + 7 * math.sin(i * 0.9)) for i in range(41)]
    c.poly(pts + [(X1, sea_y + sea_h), (X0, sea_y + sea_h)], fill=DEEP, closed=True)
    c.poly(pts, stroke=LIGHT, sw=4)
    c.text(X0 + 24, sea_y + 22, w - 48, h_dn, "ds", LIGHT, "left")
    by = sea_y + 22 + sea_head
    for k, n in enumerate(hid):
        x = X0 + k * (hw + gap)
        bh = sea_h - (by - sea_y) - 24
        c.rect(x + 14, by, hw - 28, bh, fill="none", stroke=LIGHT, sw=3, dash="10 8", rx=14)
        l1 = c.lines(n["text"], hw - 56, 34)
        th = 84 + l1 * 44.2 + (c.lines(n["sub"], hw - 56, 28) * 39.2 + 6 if n.get("sub") else 0)
        ty = by + (bh - th) / 2
        box = (x + 14, by, hw - 28, bh)
        c.text(x + 28, ty, hw - 56, "？", "dv", GOLD, "center", box)
        c.text(x + 28, ty + 84, hw - 56, n["text"], "dn", CREAM, "center", box)
        if n.get("sub"):
            c.text(x + 28, ty + 84 + l1 * 44.2 + 6, hw - 56, n["sub"], "ds", LIGHT, "center", box)
    return sea_y + sea_h


# ------------------------------------------------------------------ cycle（三個節點繞成一圈：A→B→C→A）
def cycle(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 3 個 [{text, sub?}]（上、左下、右下）；heads = 3 條邊的標籤，依序 A→B（左邊）、B→C（下邊）、C→A（右邊，金色）；
    outcomes[0]（選用）= 底下一條橫框 {text, sub?}。"""
    nodes, heads, foot = spec["nodes"], spec["heads"], (spec.get("outcomes") or [None])[0]
    w, r = X1 - X0, 64
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    avail = BOTTOM - y0
    under = 24 + 44                                      # 下邊標籤
    fixed = 2 * r + under + (28 + fh if foot else 0)
    tri = min(330.0, avail - fixed)
    _fit(fixed + 220, avail, "cycle")                    # 三角形至少要有 220 的高
    ya = y0 + r
    yb = ya + tri
    A, B, C = (X0 + w / 2, ya), (X0 + w / 2 - 250, yb), (X0 + w / 2 + 250, yb)
    pts = [A, B, C]
    def trim(p, q, d):
        dx, dy = q[0] - p[0], q[1] - p[1]; n = math.hypot(dx, dy)
        return (p[0] + dx / n * d, p[1] + dy / n * d)
    for i, (p, q) in enumerate(((A, B), (B, C), (C, A))):
        s_, e_ = trim(p, q, r + 8), trim(q, p, r + 14)
        gold = i == 2
        c.arrow(s_[0], s_[1], e_[0], e_[1], color=GOLD if gold else DEEP, sw=9 if gold else 6, head=26 if gold else 22)
    for p, n in zip(pts, nodes):
        c.circle(p[0], p[1], r, fill=DEEP)
        c.text(p[0] - r, p[1] - 36, 2 * r, n["text"], "dv", CREAM, "center", (p[0] - r, p[1] - r, 2 * r, 2 * r))
    lw = 300
    c.text(X0, (A[1] + B[1]) / 2 - 22, lw, heads[0], "dn", DEEP, "right")
    c.text(X0 + w / 2 - lw / 2, yb + r + 24, lw, heads[1], "dn", DEEP, "center")
    c.text(X1 - lw, (A[1] + C[1]) / 2 - 52, lw, heads[2], "dn", DEEP, "right")   # 靠右並上移，避開金色箭頭與右下的圓（2026-11-01）
    y = yb + r + under
    if foot:
        y += 28
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ links（左右兩排節點之間的連線）
def links(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 左排、outcomes = 右排、edges = [[左序號, 右序號], …]（0 起，連線只畫 edges 有的）、hot = 金色粗線的邊、heads = [左標籤, 右標籤]。"""
    L, R, edges = spec["nodes"], spec["outcomes"], spec["edges"]
    heads = spec.get("heads", [])
    hot = {tuple(e) for e in spec.get("hot", [])}
    for l, r in list(edges) + list(hot):
        if not (0 <= l < len(L) and 0 <= r < len(R)):
            raise ValueError(f"links 的邊 [{l}, {r}] 超出節點範圍（左 {len(L)} 個、右 {len(R)} 個）")
    if not set(map(tuple, hot)) <= set(map(tuple, edges)):
        raise ValueError("links 的 hot 必須是 edges 的子集")
    bw, pad = 390, 22
    w = X1 - X0

    def bh(n):
        return c.lines(n["text"], bw - 2 * pad, 34) * 44.2 + (c.lines(n["sub"], bw - 2 * pad, 28) * 39.2 + 6 if n.get("sub") else 0) + 2 * pad
    hl, hr = [bh(n) for n in L], [bh(n) for n in R]
    gmin = 16
    need = max(sum(hl) + gmin * (len(hl) - 1), sum(hr) + gmin * (len(hr) - 1))
    head_h = 50 if heads else 0
    avail = BOTTOM - y0 - head_h
    _fit(need, avail, "links")
    A = min(avail, max(need * 1.25, need + 100))

    def place(hs):
        if len(hs) == 1:
            return [y0 + head_h + (A - hs[0]) / 2]
        g = (A - sum(hs)) / (len(hs) - 1)
        ys, y = [], y0 + head_h
        for h in hs:
            ys.append(y); y += h + g
        return ys
    yl, yr = place(hl), place(hr)
    if heads:
        c.text(X0, y0, bw, heads[0], "ds", TEAL, "left")
        c.text(X1 - bw, y0, bw, heads[1], "ds", TEAL, "right")
    xl, xr = X0 + bw, X1 - bw
    for l, r in edges:           # 先畫線，再畫框蓋住線頭
        if (l, r) not in hot:
            c.line(xl, yl[l] + hl[l] / 2, xr, yr[r] + hr[r] / 2, TEAL, 4)
    for l, r in edges:
        if (l, r) in hot:
            c.line(xl, yl[l] + hl[l] / 2, xr, yr[r] + hr[r] / 2, GOLD, 8)
    for col, ys, hs, x in ((L, yl, hl, X0), (R, yr, hr, xr)):
        for n, y, h in zip(col, ys, hs):
            emph = n.get("emph")
            c.textbox(x, y, bw, n["text"], n.get("sub"), fill=GOLD if emph else DEEP, tcolor=DEEP if emph else CREAM,
                      scolor=DEEP if emph else LIGHT, align="left", h=h)
    return y0 + head_h + A


# ------------------------------------------------------------------ hops（幾跳才到答案）
def hops(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 每一列 [{text, sub?, sub2?, shortcut?, hops}]；heads = [起點標籤, 終點標籤]（選用）。每一跳等長，箭頭數 = hops。
    fade: true（頂層）＝箭頭一跳比一跳淡；shortcut: true（每列）＝鏈上方畫一條被叉掉的虛線捷徑，標籤是該列的 sub2。"""
    rows, heads = spec["nodes"], spec.get("heads", [])
    fade = bool(spec.get("fade"))
    r, w = 26, X1 - X0
    hmax = max(n["hops"] for n in rows)
    for n in rows:
        if not isinstance(n["hops"], int) or n["hops"] < 1:
            raise ValueError(f"hops 的 hops 必須是 1 以上的整數：{n['hops']!r}")
        nums = re.findall(r"\d+", n["text"] + " " + n.get("sub", ""))
        if nums and str(n["hops"]) not in nums:
            raise ValueError(f"hops 圖上的數字 {nums} 與箭頭數 {n['hops']} 不符（圖上畫幾跳，文字就要寫幾跳）")
        if n.get("shortcut") and not n.get("sub2"):
            raise ValueError("hops 的 shortcut 那一列要有 sub2（捷徑被叉掉的標籤）")
    step = (w - 2 * r) / hmax
    lab_h = 40 if heads else 0
    SC = 120                                    # 捷徑弧線與標籤佔的高度
    hs = [c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0) + 2 * r + lab_h + 30 + (SC if n.get("shortcut") else 0) for n in rows]
    total = sum(hs) + 36 * (len(rows) - 1)
    _fit(total, BOTTOM - y0, "hops")
    extra = min((BOTTOM - y0 - total) / len(rows), 90)
    y = y0
    for n, h in zip(rows, hs):
        h += extra
        l1 = c.lines(n["text"], w, 34)
        c.text(X0, y, w, n["text"], "dn", DEEP, "left")
        ty = y + l1 * 44.2
        if n.get("sub"):
            c.text(X0, ty + 4, w, n["sub"], "ds", TEAL, "left"); ty += c.lines(n["sub"], w, 28) * 39.2 + 6
        sc = SC if n.get("shortcut") else 0
        cy = ty + 18 + sc + r + (h - (ty - y) - 18 - sc - 2 * r - lab_h) / 2
        xs = [X0 + r + i * step for i in range(n["hops"] + 1)]
        if sc:                                  # 捷徑：從起點直接跳到答案，被叉掉
            top = cy - r - 54
            c.line(xs[0], cy - r - 6, xs[0] + 40, top, TEAL, 4, dash="10 10")
            c.line(xs[0] + 40, top, xs[-1] - 40, top, TEAL, 4, dash="10 10")
            c.line(xs[-1] - 40, top, xs[-1], cy - r - 6, TEAL, 4, dash="10 10")
            mx = (xs[0] + xs[-1]) / 2
            c.circle(mx, top, 22, fill=CREAM, stroke=DEEP, sw=4)
            c.line(mx - 11, top - 11, mx + 11, top + 11, DEEP, 5); c.line(mx - 11, top + 11, mx + 11, top - 11, DEEP, 5)
            c.text(mx - 330, top - 68, 660, n["sub2"], "ds", DEEP, "center")
        for k, (a, b) in enumerate(zip(xs, xs[1:])):
            c.arrow(a + r + 4, cy, b - r - 8, cy, DEEP, 6, 20, op=(round(1 - 0.2 * k, 2) if fade else None))
        for i, x in enumerate(xs):
            last = i == len(xs) - 1
            c.circle(x, cy, r, fill=GOLD if last else DEEP)
        if heads:
            c.text(xs[0] - 60, cy + r + 8, 120, heads[0], "ds", TEAL, "center")
            c.text(xs[-1] - 60, cy + r + 8, 120, heads[1], "ds", TEAL, "center")
        y += h + 36
    return min(y - 36, BOTTOM)


# ------------------------------------------------------------------ bubble（一個大泡泡圈住好幾個東西：超邊）
def bubble(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左標籤, 右標籤]；nodes = [{text, sub?}（左說明）, {text, sub?}（右說明）]；outcomes = 泡泡裡的項目 [{text}]（2～8 個）。"""
    heads, (ln, rn), items = spec["heads"], spec["nodes"], spec["outcomes"]
    if not 2 <= len(items) <= 8:
        raise ValueError(f"bubble 的 outcomes 要 2～8 個，現在是 {len(items)} 個")
    lw, gap = 300, 30
    rx0 = X0 + lw + gap
    rw = X1 - rx0
    pad, ch = 30, 72
    iw = rw - 2 * pad
    est = lambda t: sum(34 if ord(ch_) > 127 else 23 for ch_ in t) + 44
    rows, cur, used = [], [], 0
    for it in items:
        w = max(120, est(it["text"]))
        if w > iw:
            raise ValueError(f"bubble 的項目太長放不下：{it['text']!r}")
        if cur and used + w + 14 > iw:
            rows.append(cur); cur, used = [], 0
        cur.append((it, w)); used += w + 14
    rows.append(cur)
    bh = len(rows) * ch + (len(rows) - 1) * 16 + 2 * pad + 20
    hh = 56
    cap_l = c.lines(ln["text"], lw, 34) * 44.2 + (c.lines(ln["sub"], lw, 28) * 39.2 + 6 if ln.get("sub") else 0)
    cap_r = c.lines(rn["text"], rw, 34) * 44.2 + (c.lines(rn["sub"], rw, 28) * 39.2 + 6 if rn.get("sub") else 0)
    total = hh + bh + 26 + max(cap_l, cap_r)
    _fit(total, BOTTOM - y0, "bubble")
    extra = min(BOTTOM - y0 - total, 200)               # 空間有剩時把泡泡拉高
    top = y0 + hh
    bh += extra
    c.text(X0, y0, lw, heads[0], "ds", TEAL, "left")
    c.text(rx0, y0, rw, heads[1], "ds", TEAL, "left")
    cy = top + bh / 2
    if spec.get("chain"):                                           # 左：同一批實體拆成一串「只連兩點」的邊，每個點標名字
        m = len(items)
        cxs = [X0 + 40 + k * (lw - 80) / (m - 1) for k in range(m)]
        for a, b in zip(cxs, cxs[1:]):
            c.line(a, cy, b, cy, DEEP, 6)
        for x_, it in zip(cxs, items):
            c.circle(x_, cy, 20, fill=DEEP)
            c.text(x_ - 55, cy + 32, 110, it["text"], "ds", DEEP, "center")
    else:
        c.line(X0 + 36, cy, X0 + lw - 36, cy, DEEP, 6)              # 左：一條邊只連兩個點
        c.circle(X0 + 36, cy, 24, fill=DEEP)
        c.circle(X0 + lw - 36, cy, 24, fill=DEEP)
    c.rect(rx0, top, rw, bh, fill=GOLD, stroke=GOLD, sw=6, rx=int(min(bh / 2, 90)), op=.22)      # 右：金色泡泡
    y = top + (bh - (len(rows) * ch + (len(rows) - 1) * 16)) / 2
    for r in rows:
        tw = sum(w for _, w in r) + 14 * (len(r) - 1)
        x = rx0 + (rw - tw) / 2
        for it, w in r:
            c.rect(x, y, w, ch, fill=DEEP, rx=14)
            c.text(x + 22, y + (ch - 34 * 1.3) / 2, w - 44, it["text"], "dn", CREAM, "center", (x, y, w, ch))
            x += w + 14
        y += ch + 16
    ty = top + bh + 26
    c.text(X0, ty, lw, ln["text"], "dn", DEEP, "left")
    c.text(rx0, ty, rw, rn["text"], "dn", DEEP, "left")
    if ln.get("sub"):
        c.text(X0, ty + c.lines(ln["text"], lw, 34) * 44.2 + 4, lw, ln["sub"], "ds", TEAL, "left")
    if rn.get("sub"):
        c.text(rx0, ty + c.lines(rn["text"], rw, 34) * 44.2 + 4, rw, rn["sub"], "ds", TEAL, "left")
    return ty + max(cap_l, cap_r)


# ------------------------------------------------------------------ drift（一路偏掉的路徑：誤差沿推理鏈放大）
def drift_offsets(n: int, dmax: float) -> list[float]:
    """每一站的偏移量：起點為 0，之後越走偏得越多（二次增長）。"""
    return [dmax * (i / (n - 1)) ** 2 for i in range(n)]


def drift(c: Canvas, spec: dict, y0: float) -> float:
    """heads = 每一站的標籤（3～6 個）；nodes = [{text}（正確的路線）, {text, sub?}（實際走的路線）]。"""
    heads, (good, bad) = spec["heads"], spec["nodes"]
    n = len(heads)
    if not 3 <= n <= 6:
        raise ValueError(f"drift 的站數要 3～6 個，現在是 {n} 個")
    w = X1 - X0
    leg = [c.lines(good["text"], w - 120, 34) * 44.2, c.lines(bad["text"], w - 120, 34) * 44.2 + (c.lines(bad["sub"], w - 120, 28) * 39.2 + 6 if bad.get("sub") else 0)]
    legend_h = sum(leg) + 30
    lab_h = 44
    avail = BOTTOM - y0 - legend_h - lab_h - 40
    _fit(160, avail, "drift")
    dmax = min(avail - 40, 300)
    xs = [X0 + 70 + i * (w - 140) / (n - 1) for i in range(n)]
    ty = y0 + lab_h + 30                                         # 正確路線的高度
    offs = drift_offsets(n, dmax)
    for x, h in zip(xs, heads):
        c.text(x - 70, y0, 140, h, "ds", TEAL, "center")
    c.line(xs[0], ty, xs[-1], ty, TEAL, 5, dash="12 12")         # 正確路線：虛線
    for x in xs[1:-1]:
        c.circle(x, ty, 10, fill=CREAM, stroke=TEAL, sw=4)
    c.circle(xs[-1], ty, 24, fill=GOLD)                          # 正確的答案
    pts = [(x, ty + o) for x, o in zip(xs, offs)]
    c.poly(pts, stroke=DEEP, sw=7)                               # 實際路線：實線，越走越偏
    for x, y in pts[:-1]:
        c.circle(x, y, 14, fill=DEEP)
    x, y = pts[-1]
    c.circle(x, y, 24, fill=CREAM, stroke=DEEP, sw=6)
    c.line(x - 11, y - 11, x + 11, y + 11, DEEP, 6)
    c.line(x - 11, y + 11, x + 11, y - 11, DEEP, 6)
    ly = max(pts[-1][1] + 24 + 30, ty + dmax + 54)
    c.line(X0 + 6, ly + 22, X0 + 60, ly + 22, TEAL, 5, dash="12 12")
    c.text(X0 + 90, ly, w - 90, good["text"], "dn", DEEP, "left")
    ly2 = ly + leg[0] + 14
    c.line(X0 + 6, ly2 + 22, X0 + 60, ly2 + 22, DEEP, 7)
    c.text(X0 + 90, ly2, w - 90, bad["text"], "dn", DEEP, "left")
    if bad.get("sub"):
        c.text(X0 + 90, ly2 + c.lines(bad["text"], w - 90, 34) * 44.2 + 4, w - 90, bad["sub"], "ds", TEAL, "left")
    return ly2 + leg[1]


# ------------------------------------------------------------------ ingest（兩段式架構圖：上段線下建索引，下段查詢時）
INGEST_EDGES = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 3)]      # 事件 ↔ 實體 的多對多連線（示意）


def ingest(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [上段標籤, 下段標籤]；nodes = 上段四欄的標籤（4 個）；outcomes = 下段的步驟（2～3 個，最後一個金色）。"""
    heads, cols, steps = spec["heads"], spec["nodes"], spec["outcomes"]
    if len(cols) != 4:
        raise ValueError(f"ingest 的 nodes 要 4 個（四欄的標籤），現在是 {len(cols)} 個")
    if not 2 <= len(steps) <= 3:
        raise ValueError(f"ingest 的 outcomes 要 2～3 個，現在是 {len(steps)} 個")
    w, pad = X1 - X0, 22
    # 上段：四欄的 x 範圍
    cx = [(X0 + pad, 150), (X0 + 230, 170), (X0 + 470, 190), (X0 + 720, w - 720 - pad)]
    lab_h = max(c.lines(n["text"], cw, 28) * 39.2 + (c.lines(n["sub"], cw, 28) * 39.2 if n.get("sub") else 0) for n, (_, cw) in zip(cols, cx))
    rows_h = 2 * 58 + 30 + 44                          # 三列方塊（高 44），第二、三列之間有省略點
    top_h = 62 + lab_h + 16 + rows_h + pad
    sw_ = (w - 2 * pad - 60 * (len(steps) - 1)) / len(steps)
    box_h = max(c.lines(n["text"], sw_ - 44, 34) * 44.2 + (c.lines(n["sub"], sw_ - 44, 28) * 39.2 + 6 if n.get("sub") else 0) for n in steps) + 44
    bot_h = 62 + box_h + 12 + 50 + pad
    gap = 28
    total = top_h + gap + bot_h
    _fit(total, BOTTOM - y0, "ingest")
    extra = min(BOTTOM - y0 - total, 120)
    top_h += extra / 2; bot_h += extra / 2
    # ---- 上段
    c.rect(X0, y0, w, top_h, fill="none", stroke=TEAL, sw=3, rx=18)
    c.text(X0 + pad, y0 + 14, w - 2 * pad, heads[0], "dl", TEAL, "left")
    ly = y0 + 62
    for n, (x, cw) in zip(cols, cx):
        c.text(x, ly, cw, n["text"], "dl", DEEP, "left")
        if n.get("sub"):
            c.text(x, ly + c.lines(n["text"], cw, 28) * 39.2, cw, n["sub"], "ds", TEAL, "left")
    ry0 = ly + lab_h + 16 + (top_h - (62 + lab_h + 16 + rows_h + pad)) / 2
    ys = [ry0, ry0 + 58, ry0 + 58 * 2 + 30]
    for k in range(3):                                  # 原始片段（灰框）--> 事件（淺藍綠框），一對一
        y = ys[k]
        c.rect(cx[0][0], y, cx[0][1], 44, fill=DEEP, op=.12, rx=10)
        c.rect(cx[1][0], y, cx[1][1], 44, fill=LIGHT, op=.55, rx=10)
        c.line(cx[0][0] + cx[0][1] + 8, y + 22, cx[1][0] - 22, y + 22, TEAL, 3, dash="8 7")
        c.poly([(cx[1][0] - 8, y + 22), (cx[1][0] - 22, y + 14), (cx[1][0] - 22, y + 30)], fill=TEAL, closed=True)
    for x0_, cw_ in cx[:2]:                             # 省略點
        for i in (-1, 0, 1):
            c.circle(x0_ + cw_ / 2 + i * 16, ys[1] + 44 + 22, 4, fill=TEAL)
    ex = cx[2][0] + 40
    eys = [ry0 + 8 + i * (ys[2] + 36 - ry0 - 16) / 3 for i in range(4)]
    for ei, ni in INGEST_EDGES:                         # 事件 ↔ 實體，多對多
        c.line(cx[1][0] + cx[1][1], ys[ei] + 22, ex, eys[ni], DEEP, 3)
    for y in eys:
        c.circle(ex, y, 13, fill=GOLD, stroke=DEEP, sw=2)
    dbx, dbw = cx[3][0] + 30, 110                        # 存放處：資料庫圓柱
    dby, dbh = ry0 + 24, rows_h - 60
    c.arrow(ex + 30, (ry0 + ys[2] + 44) / 2, dbx - 14, (ry0 + ys[2] + 44) / 2, DEEP, 4, 16)
    c.rect(dbx, dby, dbw, dbh, fill=DEEP, rx=0)
    c.raw(f'<ellipse class="bg" cx="{dbx + dbw / 2:.1f}" cy="{dby + dbh:.1f}" rx="{dbw / 2:.1f}" ry="14" fill="{DEEP}"/>')
    c.raw(f'<ellipse class="bg" cx="{dbx + dbw / 2:.1f}" cy="{dby:.1f}" rx="{dbw / 2:.1f}" ry="14" fill="{TEAL}"/>')
    for k in (1, 2):
        c.raw(f'<path class="bg" d="M{dbx:.1f},{dby + dbh * k / 3:.1f} A{dbw / 2:.1f},14 0 0 0 {dbx + dbw:.1f},{dby + dbh * k / 3:.1f}" fill="none" stroke="{LIGHT}" stroke-width="3"/>')
    # ---- 下段
    by0 = y0 + top_h + gap
    c.rect(X0, by0, w, bot_h, fill=DEEP, rx=18)
    c.text(X0 + pad, by0 + 14, w - 2 * pad, heads[1], "dl", LIGHT, "left")
    sy = by0 + 62
    for k, n in enumerate(steps):
        x = X0 + pad + k * (sw_ + 60)
        last = k == len(steps) - 1
        c.textbox(x, sy, sw_, n["text"], n.get("sub"), fill=GOLD if last else CREAM, tcolor=DEEP, scolor=DEEP, h=box_h)
        if not last:
            c.arrow(x + sw_ + 8, sy + box_h / 2, x + sw_ + 52, sy + box_h / 2, CREAM, 5, 16)
    gx = X0 + pad + (len(steps) - 1) * (sw_ + 60)        # 最後一步下面：一個小的局部超圖（兩個事件靠一個共用實體串起來）
    gy = sy + box_h + 12 + 25
    c.rect(gx + 10, gy - 22, 90, 44, fill=LIGHT, rx=8)
    c.rect(gx + sw_ - 100, gy - 22, 90, 44, fill=LIGHT, rx=8)
    c.line(gx + 100, gy, gx + sw_ / 2 - 16, gy, GOLD, 6)
    c.line(gx + sw_ / 2 + 16, gy, gx + sw_ - 100, gy, GOLD, 6)
    c.circle(gx + sw_ / 2, gy, 16, fill=GOLD)
    return by0 + bot_h


# ------------------------------------------------------------------ roles（三列角色卡，每列一個圖示；2026-10-25，SAG 第 2 則）
def _icon(c: Canvas, kind: str, x: float, y: float, s: float) -> None:
    """在 (x, y) 起、邊長 s 的方塊裡畫圖示：db（資料庫圓柱）、vec（向量空間裡的幾個點）、llm（亮晶晶的大模型）。"""
    c.rect(x, y, s, s, fill=DEEP, rx=18)
    cx, cy = x + s / 2, y + s / 2
    if kind == "db":
        w, h = s * .5, s * .46
        c.rect(cx - w / 2, cy - h / 2 + 8, w, h - 8, fill=LIGHT, rx=0)
        c.raw(f'<ellipse class="bg" cx="{cx:.1f}" cy="{cy + h / 2:.1f}" rx="{w / 2:.1f}" ry="9" fill="{LIGHT}"/>'
              f'<ellipse class="bg" cx="{cx:.1f}" cy="{cy - h / 2 + 8:.1f}" rx="{w / 2:.1f}" ry="9" fill="{CREAM}"/>')
        for k in (1, 2):
            c.raw(f'<path class="bg" d="M{cx - w / 2:.1f},{cy - h / 2 + 8 + k * h / 3.2:.1f} q{w / 2:.1f},14 {w:.1f},0" fill="none" stroke="{DEEP}" stroke-width="3"/>')
    elif kind == "vec":
        for dx, dy, r, col in ((-30, 18, 8, LIGHT), (-8, 30, 7, LIGHT), (30, 26, 7, LIGHT), (-24, -26, 8, LIGHT), (24, -30, 7, LIGHT)):
            c.circle(cx + dx * s / 150, cy + dy * s / 150, r, fill=col, op=.5)
        pts = [(cx + 6 * s / 150, cy - 2), (cx + 30 * s / 150, cy - 14 * s / 150), (cx - 16 * s / 150, cy + 12 * s / 150)]
        c.line(*pts[0], *pts[1], CREAM, 3); c.line(*pts[0], *pts[2], CREAM, 3)
        c.circle(*pts[0], 13, fill=GOLD)
        c.circle(*pts[1], 9, fill=CREAM); c.circle(*pts[2], 9, fill=CREAM)
    else:
        for (dx, dy, r) in ((0, 0, 30), (34, -30, 13), (-34, 30, 10)):
            px, py, rr = cx + dx * s / 150, cy + dy * s / 150, r * s / 150 * 1.2
            c.poly([(px, py - rr * 1.5), (px + rr * .4, py - rr * .4), (px + rr * 1.5, py), (px + rr * .4, py + rr * .4),
                    (px, py + rr * 1.5), (px - rr * .4, py + rr * .4), (px - rr * 1.5, py), (px - rr * .4, py - rr * .4)], fill=GOLD, closed=True)


def roles(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 三列 [{text（元件名）, sub（它的角色，一個詞）, sub2（它做什麼）, icon: db／vec／llm}]；每列左邊一個圖示方塊，右邊三行字。"""
    nodes = spec["nodes"]
    w, ts, gap = X1 - X0, 150, 22
    tw = w - ts - 34
    hs = [max(ts, c.lines(n["text"], tw, 34) * 44.2 + 39.2 + c.lines(n["sub2"], tw, 28) * 39.2 + 26) for n in nodes]
    total = sum(hs) + gap * (len(nodes) - 1)
    _fit(total, BOTTOM - y0, "roles")
    extra = BOTTOM - y0 - total
    add = min(extra / len(nodes), 60)
    y = y0
    for n, h in zip(nodes, hs):
        h += add
        c.rect(X0, y, w, h, fill="none", stroke=DEEP, sw=3, rx=18)
        _icon(c, n.get("icon", "db"), X0 + 14, y + (h - ts + 28) / 2, ts - 28)
        th = c.lines(n["text"], tw, 34) * 44.2 + 39.2 + 14 + c.lines(n["sub2"], tw, 28) * 39.2
        ty = y + (h - th) / 2
        box = (X0, y, w, h)
        c.text(X0 + ts + 20, ty, tw, n["text"], "dn", DEEP, "left", box)
        c.text(X0 + ts + 20, ty + c.lines(n["text"], tw, 34) * 44.2 + 4, tw, n["sub"], "dl", TEAL, "left", box)
        c.text(X0 + ts + 20, ty + c.lines(n["text"], tw, 34) * 44.2 + 39.2 + 10, tw, n["sub2"], "ds", DEEP, "left", box)
        y += h + gap
    return y - gap


# ------------------------------------------------------------------ embed（精確比對 vs 向量空間）
def embed(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左標, 右標]；nodes = 左邊的比對列 [{text, sub?, ok: true／false}]（ok 畫勾，否則畫叉與虛線框）；
    outcomes = 右邊向量空間裡的 3 個點 [{text, sub?}]（第一個是中心點）；遠處的灰點只是陪襯，不帶文字。純示意。"""
    hl, hr = spec["heads"]
    rows, pts = spec["nodes"], spec["outcomes"]
    if len(pts) != 3:
        raise ValueError(f"embed 的 outcomes 要 3 個點，現在是 {len(pts)} 個")
    cw, gap, hh = 440, 40, 80
    xs = [X0, X0 + cw + gap]
    iw = cw - 44 - 56
    rh = [c.lines(r["text"], iw, 34) * 44.2 + (c.lines(r["sub"], iw, 28) * 39.2 + 6 if r.get("sub") else 0) + 44 for r in rows]
    lg = [c.lines(p["text"], cw - 100, 34) * 44.2 + (c.lines(p["sub"], cw - 100, 28) * 39.2 + 4 if p.get("sub") else 0) + 12 for p in pts]
    scat = 200
    left_h = sum(rh) + 16 * (len(rows) - 1)
    ph = max(left_h, scat + sum(lg) + 28)
    total = hh + 16 + ph
    _fit(total, BOTTOM - y0, "embed")
    ph += min(BOTTOM - y0 - total, 90)
    py = y0 + hh + 16
    for k, hd in enumerate((hl, hr)):
        c.rect(xs[k], y0, cw, hh, fill=DEEP if k == 0 else TEAL)
        c.text(xs[k] + 22, y0 + (hh - 44) / 2, cw - 44, hd, "dn", CREAM, "center", (xs[k], y0, cw, hh))
    add = (ph - left_h) / len(rows)
    y = py
    for r, h in zip(rows, rh):
        h += add
        ok = r.get("ok", True)
        c.rect(xs[0], y, cw, h, fill="none", stroke=DEEP, sw=3, dash=None if ok else "8 8", rx=14)
        ix, iy = xs[0] + 40, y + 40
        c.circle(ix, iy, 22, fill=GOLD if ok else CREAM, stroke=None if ok else DEEP, sw=4)
        if ok:
            c.poly([(ix - 10, iy), (ix - 3, iy + 8), (ix + 11, iy - 9)], stroke=DEEP, sw=5)
        else:
            c.line(ix - 9, iy - 9, ix + 9, iy + 9, DEEP, 5); c.line(ix - 9, iy + 9, ix + 9, iy - 9, DEEP, 5)
        th = c.lines(r["text"], iw, 34) * 44.2 + (c.lines(r["sub"], iw, 28) * 39.2 + 6 if r.get("sub") else 0)
        ty = y + (h - th) / 2
        c.text(xs[0] + 78, ty, iw, r["text"], "dn", DEEP if ok else TEAL, "left", (xs[0], y, cw, h))
        if r.get("sub"):
            c.text(xs[0] + 78, ty + c.lines(r["text"], iw, 34) * 44.2 + 6, iw, r["sub"], "ds", TEAL, "left", (xs[0], y, cw, h))
        y += h + 16
    c.rect(xs[1], py, cw, ph, fill="none", stroke=DEEP, sw=3, rx=14)
    cx, cy = xs[1] + cw / 2, py + scat / 2 + 6
    for dx, dy in ((-180, -66), (-150, 62), (-110, -20), (170, -62), (150, 72), (60, -80), (95, 82), (-30, 86), (-60, -82)):
        c.circle(cx + dx, cy + dy, 8, fill=LIGHT, op=.7)
    c.raw(f'<ellipse class="bg" cx="{cx:.1f}" cy="{cy:.1f}" rx="112" ry="70" fill="{GOLD}" fill-opacity=".28" stroke="{GOLD}" stroke-width="3" stroke-dasharray="8 7"/>')
    cols = (GOLD, TEAL, DEEP)
    for (dx, dy, r), col in zip(((0, 0, 16), (58, -24, 13), (-56, 26, 13)), cols):
        c.circle(cx + dx, cy + dy, r, fill=col, stroke=DEEP, sw=3)
    ly = py + scat + 4
    for p, h, col in zip(pts, lg, cols):
        c.circle(xs[1] + 34, ly + 22, 11, fill=col, stroke=DEEP, sw=2)
        c.text(xs[1] + 62, ly, cw - 80, p["text"], "dn", DEEP, "left", (xs[1], py, cw, ph))
        if p.get("sub"):
            c.text(xs[1] + 62, ly + c.lines(p["text"], cw - 100, 34) * 44.2 + 4, cw - 80, p["sub"], "ds", TEAL, "left", (xs[1], py, cw, ph))
        ly += h
    return py + ph


# ------------------------------------------------------------------ online（線上流程的路線圖：兩路進來、一路擴展、兩路決選）
def _loop_icon(c: Canvas, cx: float, cy: float, r: float, color: str) -> None:
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-50, 231, 10)]
    c.poly(pts, stroke=color, sw=6)
    a = math.radians(230)
    ex, ey = pts[-1]
    tx, ty = -math.sin(a), math.cos(a)                  # 順時針的切線方向
    nx, ny = -ty, tx
    c.poly([(ex + tx * 16, ey + ty * 16), (ex + nx * 11, ey + ny * 11), (ex - nx * 11, ey - ny * 11)], fill=color, closed=True)


def online(c: Canvas, spec: dict, y0: float) -> float:
    """SAG 論文圖二下半（線上檢索）的重畫（2026-10-25）：heads = [最上面的起點, 最下面的結果]；nodes = 第一步的兩條路 [{text, sub?}]；
    outcomes = [第二步（寬框）, 第三步左邊那路, 第三步右邊那路]，每個 {text, sub?}。箭頭由程式畫：起點→第一步兩路→第二步→左路；右路（直接檢索）不經過第二步，從起點沿右側繞下去（原圖如此，2026-10-25 重製圖審查者擋過）；兩路→結果。"""
    top, fin = spec["heads"]
    A, B = spec["nodes"]
    S2, L, R = spec["outcomes"]
    w = X1 - X0
    tw = (w - 30) / 2
    def bh(n, ww):
        return c.lines(n["text"], ww - 44, 34) * 44.2 + (c.lines(n["sub"], ww - 44, 28) * 39.2 + 6 if n.get("sub") else 0) + 36
    qh = 64
    fh = c.lines(fin, w - 44, 34) * 44.2 + 36
    h1, h3 = max(bh(A, tw), bh(B, tw)), max(bh(L, tw), bh(R, tw))
    s2w = w
    h2 = bh(S2, s2w + 44)
    ag = 38
    total = qh + h1 + h2 + h3 + fh + 4 * ag
    _fit(total, BOTTOM - y0, "online")
    extra = BOTTOM - y0 - total
    add = min(extra * .6 / 3, 40)
    h1, h2, h3 = h1 + add, h2 + add, h3 + add
    ag += min((extra - 3 * add) / 4, 22)
    cx = X0 + w / 2
    y = y0
    c.textbox(cx - 230, y, 460, top, fill=DEEP, tcolor=CREAM, align="center", h=qh); qy = y; y += qh + ag
    ax, bx = X0, X0 + tw + 30
    c.textbox(ax, y, tw, A["text"], A.get("sub"), fill=TEAL, scolor=CREAM, h=h1)
    c.textbox(bx, y, tw, B["text"], B.get("sub"), fill=TEAL, scolor=CREAM, h=h1)
    c.arrow(cx - 40, qy + qh + 3, ax + tw / 2 + 10, y - 4); c.arrow(cx + 40, qy + qh + 3, bx + tw / 2 - 10, y - 4)
    y1 = y; y += h1 + ag
    c.rect(X0, y, w, h2, fill=DEEP)
    c.text(X0 + 22, y + (h2 - (c.lines(S2["text"], s2w - 44, 34) * 44.2 + (c.lines(S2["sub"], s2w - 44, 28) * 39.2 + 6 if S2.get("sub") else 0))) / 2, s2w - 44, S2["text"], "dn", CREAM, "left", (X0, y, s2w, h2))
    if S2.get("sub"):
        c.text(X0 + 22, y + (h2 - (c.lines(S2["text"], s2w - 44, 34) * 44.2 + c.lines(S2["sub"], s2w - 44, 28) * 39.2 + 6)) / 2 + c.lines(S2["text"], s2w - 44, 34) * 44.2 + 6, s2w - 44, S2["sub"], "ds", LIGHT, "left", (X0, y, s2w, h2))
    c.arrow(ax + tw / 2, y1 + h1 + 3, ax + tw / 2, y - 4); c.arrow(bx + tw / 2, y1 + h1 + 3, bx + tw / 2, y - 4)
    y2 = y; y += h2 + ag
    c.textbox(ax, y, tw, L["text"], L.get("sub"), fill=TEAL, scolor=CREAM, h=h3)
    c.textbox(bx, y, tw, R["text"], R.get("sub"), fill=TEAL, scolor=CREAM, h=h3)
    c.arrow(ax + tw / 2, y2 + h2 + 3, ax + tw / 2, y - 4)      # 左路接在第二步後面；右路（直接檢索）不經過第二步，由起點繞過去（原圖：Query 直接走 Embedding Top-5）
    y3 = y; y += h3 + ag
    c.poly([(cx + 230 + 4, qy + qh / 2), (X1 + 34, qy + qh / 2), (X1 + 34, y3 + h3 / 2), (X1 + 8, y3 + h3 / 2)], stroke=TEAL, sw=4)
    c.poly([(X1 + 8, y3 + h3 / 2), (X1 + 22, y3 + h3 / 2 - 9), (X1 + 22, y3 + h3 / 2 + 9)], fill=TEAL, closed=True)
    c.textbox(X0, y, w, fin, fill=GOLD, tcolor=DEEP, align="center", h=fh)
    c.arrow(ax + tw / 2, y3 + h3 + 3, ax + tw / 2, y - 4); c.arrow(bx + tw / 2, y3 + h3 + 3, bx + tw / 2, y - 4)
    return y + fh


# ------------------------------------------------------------------ gate（水庫閘門：上游來多少，開度固定；兩道各一列）
def gate(c: Canvas, spec: dict, y0: float) -> float:
    """count = 閘門的名額（畫在每一道閘門上）；nodes = 兩列（兩道名額）[{text, sub?}]，每列：標題在上，下面左邊一池散落的點（上游，純示意、任意多）、
    中間閘門、右邊整齊排好的 count 個點（下游，點數 = 名額）。"""
    n = spec["count"]
    rows = spec["nodes"]
    if len(rows) != 2:
        raise ValueError(f"gate 的 nodes 要 2 列（兩道名額），現在是 {len(rows)} 列")
    w = X1 - X0
    def hh_(r):
        return c.lines(r["text"], w, 34) * 44.2 + (c.lines(r["sub"], w, 28) * 39.2 + 6 if r.get("sub") else 0)
    heads = [hh_(r) for r in rows]
    gapr = 26
    pmin = 130
    _fit(sum(heads) + 2 * 16 + 2 * pmin + gapr, BOTTOM - y0, "gate")
    ph = min(210, (BOTTOM - y0 - sum(heads) - 2 * 16 - gapr) / 2)
    y = y0
    seed = 7
    for k, r in enumerate(rows):
        c.text(X0, y, w, r["text"], "dn", DEEP, "left")
        if r.get("sub"):
            c.text(X0, y + c.lines(r["text"], w, 34) * 44.2 + 6, w, r["sub"], "ds", TEAL, "left")
        py = y + heads[k] + 16
        c.rect(X0, py, 400, ph, fill=LIGHT, stroke=TEAL, sw=3, rx=18, op=.30)
        for i in range(22):
            seed = (seed * 1103515245 + 12345) % 2147483648
            fx = (seed >> 8) % 1000 / 1000
            seed = (seed * 1103515245 + 12345) % 2147483648
            fy = (seed >> 8) % 1000 / 1000
            c.circle(X0 + 24 + fx * 352, py + 22 + fy * (ph - 44), 9, fill=MID)
        gx, gw, gap = X0 + 400, 110, 56
        gy = py + ph / 2 - gap / 2
        c.rect(gx, py, gw, gy - py, fill=DEEP, rx=0)
        c.rect(gx, gy + gap, gw, py + ph - gy - gap, fill=DEEP, rx=0)
        pt = py + (gy - py) / 2
        c.rect(gx + 6, pt - 34, gw - 12, 68, fill=GOLD, rx=4)
        c.text(gx + 26, pt - 24, gw - 52, f"{n}", "dv2", DEEP, "center", (gx + 6, pt - 34, gw - 12, 68))
        rx_ = X0 + 540
        c.arrow(X0 + 330, gy + gap / 2, rx_ + 40, gy + gap / 2, GOLD, 8, 22)
        c.rect(rx_, py, X1 - rx_, ph, fill="none", stroke=DEEP, sw=3, rx=18)
        cols = 10                                     # 右邊畫的點數 = 名額（50 就是 50 個），整齊排好
        nr = math.ceil(n / cols)
        pitch = min(38, (X1 - rx_ - 50) / cols, (ph - 36) / nr)
        sx = rx_ + (X1 - rx_ - (cols - 1) * pitch) / 2
        sy = py + ph / 2 - (nr - 1) * pitch / 2
        for q in range(n):
            c.circle(sx + (q % cols) * pitch, sy + (q // cols) * pitch, pitch * .36, fill=GOLD, stroke=DEEP, sw=2)
        y = py + ph + gapr
    return y - gapr


# ------------------------------------------------------------------ concat（兩路各一排，匯成一排）
def _chunk(c: Canvas, x: float, y: float, w: float, h: float, col: str) -> None:
    c.rect(x, y, w, h, fill=CREAM, stroke=col, sw=4, rx=8)
    for k in range(3):
        c.rect(x + 10, y + 14 + k * 20, w - 20 - (k == 2) * 16, 7, fill=col, op=.55, rx=3)


def concat(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左路標籤, 右路標籤]；nodes = [{text}（上方一句話，說兩路各挑幾個）, {text, sub?}（匯整後的結果）]。
    每路畫 5 個小文件，匯整後畫 10 個（只表示合成一份，不分來源）；純示意。"""
    hl, hr = spec["heads"]
    top, res = spec["nodes"]
    w = X1 - X0
    th = c.lines(top["text"], w, 34) * 44.2
    rh = c.lines(res["text"], w, 34) * 44.2 + (c.lines(res["sub"], w, 28) * 39.2 + 6 if res.get("sub") else 0)
    cw_, ch_, g_ = 62, 82, 14
    rowW = 5 * cw_ + 4 * g_
    total = th + 14 + 50 + ch_ + 90 + ch_ + 40 + rh
    _fit(total, BOTTOM - y0, "concat")
    extra = BOTTOM - y0 - total
    ag = 90 + min(extra * .5, 50)
    c.text(X0, y0, w, top["text"], "dn", DEEP, "left")
    ly = y0 + th + 14
    lx, rx_ = X0 + 60, X1 - 60 - rowW
    for x, hd, col in ((lx, hl, TEAL), (rx_, hr, DEEP)):
        c.text(x, ly, rowW, hd, "dl", col, "center")
        for i in range(5):
            _chunk(c, x + i * (cw_ + g_), ly + 54, cw_, ch_, col)
    mid = X0 + w / 2
    sy = ly + 54 + ch_
    shy = sy + ag
    sw_ = 10 * cw_ + 9 * g_ - 90
    c.arrow(lx + rowW / 2, sy + 8, mid - 60, shy - 8, TEAL, 5, 16)
    c.arrow(rx_ + rowW / 2, sy + 8, mid + 60, shy - 8, DEEP, 5, 16)
    shelfW = min(w, 10 * cw_ + 9 * g_ + 60)
    c.rect(mid - shelfW / 2, shy, shelfW, ch_ + 40, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=16)
    x0_ = mid - (10 * cw_ + 9 * g_) / 2
    for i in range(10):
        _chunk(c, x0_ + i * (cw_ + g_), shy + 20, cw_, ch_, DEEP)
    ry = shy + ch_ + 40 + 22
    c.text(X0, ry, w, res["text"], "dn", DEEP, "center")
    if res.get("sub"):
        c.text(X0, ry + c.lines(res["text"], w, 34) * 44.2 + 6, w, res["sub"], "ds", TEAL, "center")
    return ry + rh


# ------------------------------------------------------------------ joint（逐一打分 vs 一起評估）
def joint(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [左標, 右標]；nodes = [{text（一句話）, sub（例子）, sub2（結論）}, {…}]。左邊三個小方塊之間各斷一條線、畫叉（各自獨立），
    右邊三個小方塊用金色接起來、外面括一個大括號（一起看）；純示意，方塊不帶文字。"""
    hl, hr = spec["heads"]
    nodes = spec["nodes"]
    cw, gap, hh = 440, 40, 80
    xs = [X0, X0 + cw + gap]
    iw = cw - 44
    def blk(n):
        return (c.lines(n["text"], iw, 34) * 44.2, c.lines(n["sub2"], iw, 34) * 44.2, c.lines(n["sub"], iw, 28) * 39.2)
    hs = [sum(blk(n)) for n in nodes]
    pic = 3 * 52 + 2 * 14 + 46
    total = hh + 16 + max(hs) + pic + 3 * 18 + 24
    _fit(total, BOTTOM - y0, "joint")
    pic += min(BOTTOM - y0 - total, 80)
    ph = max(hs) + pic + 3 * 18 + 24
    for k, (hd, n) in enumerate(zip((hl, hr), nodes)):
        x = xs[k]
        c.rect(x, y0, cw, hh, fill=DEEP if k == 0 else TEAL)
        c.text(x + 22, y0 + (hh - 44) / 2, cw - 44, hd, "dn", CREAM, "center", (x, y0, cw, hh))
        py = y0 + hh + 16
        c.rect(x, py, cw, ph, fill="none", stroke=DEEP, sw=3, rx=14, dash="8 8" if k == 0 else None)
        t1, t2, t3 = blk(n)
        y = py + 18
        c.text(x + 22, y, iw, n["text"], "dn", DEEP, "left", (x, py, cw, ph)); y += t1 + 6
        top = y + 8
        pitch = (pic - 36) / 2.7
        chip_h = min(52, pitch * .74)
        for i in range(3):
            cy_ = top + i * pitch
            if k == 0:
                c.rect(x + 40, cy_, 280, chip_h, fill=CREAM, stroke=DEEP, sw=3, rx=10)
                if i:      # 方塊之間沒有連結：虛線斷在中間，畫一個叉
                    my = cy_ - (pitch - chip_h) / 2
                    c.line(x + 172, my - 5, x + 188, my + 5, TEAL, 4); c.line(x + 172, my + 5, x + 188, my - 5, TEAL, 4)
            else:
                c.rect(x + 40, cy_, 280, chip_h, fill=GOLD, stroke=DEEP, sw=3, rx=10, op=.35)
                if i:
                    c.rect(x + 170, cy_ - (pitch - chip_h), 20, pitch - chip_h, fill=GOLD, rx=4)
        if k == 1:
            by0, by1 = top - 4, top + 2 * pitch + chip_h + 4
            c.poly([(x + 340, by0), (x + 366, by0 + 10), (x + 366, (by0 + by1) / 2 - 12), (x + 386, (by0 + by1) / 2), (x + 366, (by0 + by1) / 2 + 12), (x + 366, by1 - 10), (x + 340, by1)], stroke=GOLD, sw=7)
        for q in range(3):      # 方塊不只三個：下面三個小點
            c.circle(x + 180 + (q - 1) * 22, top + 2 * pitch + chip_h + 18, 5, fill=TEAL)
        y = top + 2 * pitch + chip_h + 34
        c.text(x + 22, y, iw, n["sub2"], "dn", DEEP if k else TEAL, "left", (x, py, cw, ph)); y += t2 + 6
        c.text(x + 22, y, iw, n["sub"], "ds", TEAL, "left", (x, py, cw, ph))
    return y0 + hh + 16 + ph


# ------------------------------------------------------------------ rails（兩條軌道各撈一排，合併成一排；A 漏掉的一格由 B 補上）
def rails(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [A 路標籤, B 路標籤]；nodes = [{text, sub?}（A 的做法）, {text, sub?}（B 的做法）]；outcomes[0] = {text, sub?}（合併後的結果）。
    每條軌道右邊畫 6 個格子：A 在第 4 格漏接（虛線空格），B 補上那一格（金色）；合併後 6 格都有。純示意，格子不帶文字。"""
    hl, hr = spec["heads"]
    A, B = spec["nodes"]
    res = spec["outcomes"][0]
    w = X1 - X0
    tw, cw_, ch_, g_ = 390, 58, 66, 12
    rowW = 6 * cw_ + 5 * g_
    cx0 = X1 - 24 - rowW
    def lane_h(n):
        return 18 + 45 + c.lines(n["text"], tw, 34) * 44.2 + (c.lines(n["sub"], tw, 28) * 39.2 + 6 if n.get("sub") else 0) + 18
    lh = max(lane_h(A), lane_h(B), ch_ + 60)
    rh = max(ch_ + 36, c.lines(res["text"], w - 44, 34) * 44.2 + 40)
    ag = 44
    gap = 18
    total = 2 * lh + gap + ag + rh
    _fit(total, BOTTOM - y0, "rails")
    extra = BOTTOM - y0 - total
    lh += min(extra * .5 / 2, 30)
    ag += min(extra * .5, 30)
    miss = 3
    y = y0
    lane_y = []
    for k, (hd, n, col, filled) in enumerate(((hl, A, DEEP, [0, 1, 2, 4, 5]), (hr, B, TEAL, [1, 3, 5]))):
        c.rect(X0, y, w, lh, fill="none", stroke=col, sw=3, rx=18)
        c.text(X0 + 22, y + 12, tw, hd, "dl", col, "left", (X0, y, w, lh))
        ty = y + 12 + 45
        c.text(X0 + 22, ty, tw, n["text"], "dn", DEEP, "left", (X0, y, w, lh))
        if n.get("sub"):
            c.text(X0 + 22, ty + c.lines(n["text"], tw, 34) * 44.2 + 6, tw, n["sub"], "ds", TEAL, "left", (X0, y, w, lh))
        cy = y + (lh - ch_) / 2
        for i in range(6):
            x = cx0 + i * (cw_ + g_)
            if i in filled:
                if k == 1 and i == miss:
                    c.rect(x, cy, cw_, ch_, fill=GOLD, stroke=DEEP, sw=4, rx=8)
                else:
                    _chunk(c, x, cy, cw_, ch_, col)
            elif k == 0 and i == miss:
                c.rect(x, cy, cw_, ch_, fill="none", stroke=TEAL, sw=4, rx=8, dash="7 7")
        lane_y.append(y)
        y += lh + gap
    y += ag - gap
    c.rect(X0, y, w, rh, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=18)
    rcy = y + (rh - ch_) / 2
    for i in range(6):
        x = cx0 + i * (cw_ + g_)
        if i == miss:
            c.rect(x, rcy, cw_, ch_, fill=GOLD, stroke=DEEP, sw=4, rx=8)
        else:
            _chunk(c, x, rcy, cw_, ch_, DEEP)
    th = c.lines(res["text"], tw, 34) * 44.2
    c.text(X0 + 22, y + (rh - th) / 2, tw, res["text"], "dn", DEEP, "left", (X0, y, w, rh))
    mx = cx0 + 3 * (cw_ + g_) + cw_ / 2                  # 補上的那一格往下接到合併後的同一格
    c.arrow(mx, lane_y[1] + lh + 4, mx, y - 6, GOLD, 6, 18)
    return y + rh


# ------------------------------------------------------------------ scoreboard（戰績表：資料集 × 欄，每格兩條橫條）
def scoreboard(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 每列一個資料集 [{text, sub?, emph?}]；heads = 兩個欄標籤；outcomes = 圖例 [{text（深色）}, {text（淺色）}]；
    cells[列][欄] = [深色值, 淺色值]（字串）。每格兩條橫條，軸從 0 起（axis_max 預設 100），長度與數值成正比；深色值小於淺色值的格子畫虛線框。"""
    rows, heads, leg, cells = spec["nodes"], spec["heads"], spec["outcomes"], spec["cells"]
    amax = float(spec.get("axis_max", 100))
    if len(cells) != len(rows) or any(len(r_) != len(heads) for r_ in cells):
        raise ValueError(f"scoreboard 的 cells 要 {len(rows)} 列 × {len(heads)} 欄")
    if len(leg) != 2:
        raise ValueError("scoreboard 的 outcomes 要 2 個（圖例：深色、淺色）")
    w = X1 - X0
    lw = 340
    cw = (w - lw) / len(heads)
    bh_, bg_, pad = 44, 14, 18
    head_h = 56
    gap = 14
    need_text = [c.lines(n["text"], lw - 28, 34) * 44.2 + (c.lines(n["sub"], lw - 28, 28) * 39.2 + 6 if n.get("sub") else 0) + 2 * pad for n in rows]
    rh = [max(2 * bh_ + bg_ + 2 * pad, t) for t in need_text]
    total = head_h + 10 + sum(rh) + gap * (len(rows) - 1)
    _fit(total, BOTTOM - y0, "scoreboard")
    add = min((BOTTOM - y0 - total) / len(rows), 40)
    rh = [h + add for h in rh]
    # 圖例（左上）與欄標籤
    lx = X0
    for col, n in zip((DEEP, LIGHT), leg):
        c.rect(lx, y0 + 14, 26, 26, fill=col, rx=5)
        c.text(lx + 36, y0 + 8, 200, n["text"], "dl", DEEP, "left")
        lx += 36 + (len(n["text"]) * 17 + 20)
    for j, hd in enumerate(heads):
        c.text(X0 + lw + j * cw, y0 + 8, cw, hd, "dl", TEAL, "center")
    y = y0 + head_h + 10
    barmax = cw - 2 * 18 - 84
    for i, (n, h) in enumerate(zip(rows, rh)):
        if n.get("emph"):
            c.rect(X0 - 12, y - 8, w + 24, h + 16, fill=GOLD, op=.22, rx=18)
        box = (X0, y, lw, h)
        th = c.lines(n["text"], lw - 28, 34) * 44.2 + (c.lines(n["sub"], lw - 28, 28) * 39.2 + 6 if n.get("sub") else 0)
        ty = y + (h - th) / 2
        c.text(X0 + 6, ty, lw - 28, n["text"], "dn", DEEP, "left", box)
        if n.get("sub"):
            c.text(X0 + 6, ty + c.lines(n["text"], lw - 28, 34) * 44.2 + 6, lw - 28, n["sub"], "ds", DEEP if n.get("emph") else TEAL, "left", box)
        for j in range(len(heads)):
            a, b = cells[i][j]
            cx = X0 + lw + j * cw + 8
            lose = float(a) < float(b)
            c.rect(cx, y, cw - 16, h, fill="none", stroke=DEEP, sw=3, rx=14, dash="9 8" if lose else None, op=None)
            by = y + (h - (2 * bh_ + bg_)) / 2
            for k, (val, col, tc) in enumerate(((a, DEEP, DEEP), (b, LIGHT, TEAL))):
                L = float(val) / amax * barmax
                yy = by + k * (bh_ + bg_)
                c.rect(cx + 14, yy, L, bh_, fill=col, rx=6)
                c.text(cx + 14 + L + 10, yy + (bh_ - 28 * 1.4) / 2, 84, val, "dl", DEEP if n.get("emph") else tc, "left")
        y += h + gap
    return y - gap


# ------------------------------------------------------------------ leak（每一跳都漏一些）
def leak(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 兩條路 [{text, sub?}（走很多跳的）, {text, sub?}（一次到位的）]；heads = 箭頭上的標籤（例：剪枝，兩條路共用）。
    兩條路從同一個起點走到同一個終點：第一條分 3 跳（4 格），第二條一跳（2 格）。每一格是 2 × 5 個點，實心＝留下、虛線空點＝漏掉；點數是固定示意。
    選用 hops = 第一條的跳數，2 或 3（預設 3；2026-11-01 Cerebras 第 3 則：「摘要的摘要」是壓縮兩次）。"""
    A, B = spec["nodes"]
    hops = spec.get("hops", 3)
    if hops not in (2, 3):
        raise ValueError(f"leak 的 hops 只能是 2 或 3，現在是 {hops}")
    lab = spec["heads"][0]
    w = X1 - X0
    cols, rows_, pitch, rr = 2, 5, 30, 11
    binw, binh = cols * pitch + 18, rows_ * pitch + 18
    def th(n):
        return c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0)
    lane = lambda n: th(n) + 14 + binh + 12
    total = lane(A) + lane(B) + 30
    _fit(total, BOTTOM - y0, "leak")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    y = y0
    xs_a = [X0 + i * ((w - binw) / hops) for i in range(hops + 1)]
    xs_b = [X0, X0 + w - binw]
    plans = ((A, xs_a, [10, 8, 6, 5] if hops == 3 else [10, 7, 5], TEAL, False), (B, xs_b, [10, 9], DEEP, True))
    for n, xs, keep, col, win in plans:
        c.text(X0, y, w, n["text"], "dn", DEEP, "left")
        if n.get("sub"):
            c.text(X0, y + c.lines(n["text"], w, 34) * 44.2 + 4, w, n["sub"], "ds", TEAL, "left")
        by = y + th(n) + 14 + extra / 2
        for k, (x, kp) in enumerate(zip(xs, keep)):
            last = k == len(xs) - 1
            c.rect(x, by, binw, binh, fill=GOLD if (win and last) else "none", stroke=col, sw=3, rx=10, op=.25 if (win and last) else None)
            for q in range(cols * rows_):
                px, py = x + 9 + pitch / 2 + (q % cols) * pitch, by + 9 + pitch / 2 + (q // cols) * pitch
                if q < kp:
                    c.circle(px, py, rr, fill=col)
                else:
                    c.circle(px, py, rr, fill="none", stroke=col, sw=2, dash="4 4")
            if k:
                x0_, x1_ = xs[k - 1] + binw + 10, x - 10
                c.arrow(x0_, by + binh / 2, x1_, by + binh / 2, col, 5, 18)
                c.text((x0_ + x1_) / 2 - 60, by + binh / 2 - 46, 120, lab, "ds", col, "center")
        y = by + binh + 12 + extra / 2 + 30
    return y - 30


# ------------------------------------------------------------------ amplify（誤差沿路放大 vs 精確比對）
def amplify(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 兩條路 [{text, sub?}, {text, sub?}]；heads = 第一條兩端的標籤 [起點, 終點]；outcomes[0] = 第二條帶子的標籤。
    第一條畫成越來越寬的楔形（誤差越傳越大），第二條是等寬的金色帶（精確比對）；沿路四個站；純示意。"""
    A, B = spec["nodes"]
    h0, h1 = spec["heads"]
    lb = spec["outcomes"][0]["text"]
    w = X1 - X0
    th = lambda n: c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0)
    band, lab_h = 170, 44
    total = th(A) + band + lab_h + 30 + th(B) + 120 + lab_h
    _fit(total, BOTTOM - y0, "amplify")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    stations = [X0 + 30 + i * ((w - 60) / 3) for i in range(4)]
    # 第一條：楔形
    y = y0
    c.text(X0, y, w, A["text"], "dn", DEEP, "left")
    if A.get("sub"):
        c.text(X0, y + c.lines(A["text"], w, 34) * 44.2 + 4, w, A["sub"], "ds", TEAL, "left")
    cy = y + th(A) + 14 + band / 2 + extra / 2
    c.poly([(X0 + 30, cy - 8), (X1 - 10, cy - band / 2), (X1 - 10, cy + band / 2), (X0 + 30, cy + 8)], fill=TEAL, closed=True, op=.30)
    c.line(X0 + 30, cy, X1 - 10, cy, DEEP, 5)
    for i, x in enumerate(stations):
        c.circle(x, cy, 16, fill=DEEP)
    ly = cy + band / 2 + 8
    c.text(X0, ly, 400, h0, "ds", TEAL, "left")
    c.text(X1 - 400, ly, 400, h1, "ds", DEEP, "right")
    # 第二條：等寬帶
    y2 = ly + lab_h + 30 + extra / 2
    c.text(X0, y2, w, B["text"], "dn", DEEP, "left")
    if B.get("sub"):
        c.text(X0, y2 + c.lines(B["text"], w, 34) * 44.2 + 4, w, B["sub"], "ds", TEAL, "left")
    cy2 = y2 + th(B) + 14 + 40
    c.rect(X0 + 30, cy2 - 20, w - 40, 40, fill=GOLD, op=.55, stroke=GOLD, sw=3, rx=8)
    for x in stations:
        c.circle(x, cy2, 16, fill=DEEP)
        c.line(x - 7, cy2 - 4, x + 7, cy2 - 4, CREAM, 3); c.line(x - 7, cy2 + 4, x + 7, cy2 + 4, CREAM, 3)     # 等號：精確相等才連上
    c.text(X0, cy2 + 40, w, lb, "ds", DEEP, "left")
    return cy2 + 40 + 39.2


# ------------------------------------------------------------------ 2026-10-27（SAG 第 4 則）：receipt／squeeze／alias／handoff／mismatch／ledger
def _th(c: Canvas, n: dict, w: float) -> float:
    """一個 {text, sub?} 在寬 w 內的文字高度（text 34 px、sub 28 px）。"""
    return c.lines(n["text"], w, 34) * 44.2 + (c.lines(n["sub"], w, 28) * 39.2 + 6 if n.get("sub") else 0)


def _cross(c: Canvas, x: float, y: float, r: float, color: str = DEEP, sw: int = 5) -> None:
    c.line(x - r, y - r, x + r, y + r, color, sw)
    c.line(x - r, y + r, x + r, y - r, color, sw)


def receipt(c: Canvas, spec: dict, y0: float) -> float:
    """帳單（SAG 第 4 則「付的帳」）：heads = [抬頭, 「換來的」標籤]；nodes = 品項 2～4 個 [{text, sub?}]（每項前面自動編號）；
    outcomes = 換來的東西 1～3 個 [{text}]（畫成金色小標籤）。一張米色紙，下緣鋸齒；純示意。"""
    head, got = spec["heads"]
    items, gains = spec["nodes"], spec["outcomes"]
    if not 2 <= len(items) <= 4 or not 1 <= len(gains) <= 3:
        raise ValueError(f"receipt 的 nodes 要 2～4 個品項、outcomes 要 1～3 個，現在是 {len(items)}、{len(gains)}")
    w = X1 - X0
    px, pw = X0 + 20, w - 40                             # 紙比版心窄一點
    tw = pw - 150
    rows = [max(_th(c, n, tw) + 26, 76) for n in items]
    gain_h = 60
    total = 84 + sum(rows) + 8 * (len(rows) - 1) + 34 + 50 + gain_h + 56
    _fit(total, BOTTOM - y0, "receipt")
    add = min((BOTTOM - y0 - total) / len(items), 30)
    rows = [r + add for r in rows]
    total += add * len(items)
    zig = []
    bot = y0 + total
    steps = 24
    for i in range(steps + 1):
        zig.append((px + i * pw / steps, bot if i % 2 == 0 else bot - 16))
    c.poly([(px, y0), (px + pw, y0)] + zig[::-1], fill=GOLD, closed=True, op=.14)
    c.poly([(px, bot), (px, y0), (px + pw, y0), (px + pw, bot)], stroke=DEEP, sw=3)
    c.poly(zig, stroke=DEEP, sw=3)
    c.text(px + 28, y0 + 14, pw - 56, head, "dl", TEAL, "left")
    c.line(px + 28, y0 + 70, px + pw - 28, y0 + 70, DEEP, 3, dash="3 9")
    y = y0 + 86
    for k, (n, h) in enumerate(zip(items, rows), 1):
        c.circle(px + 64, y + h / 2, 28, fill=DEEP)
        c.text(px + 64 - 25, y + h / 2 - 19, 50, str(k), "dl", CREAM, "center")
        ty = y + (h - _th(c, n, tw)) / 2
        c.text(px + 120, ty, tw, n["text"], "dn", DEEP, "left")
        if n.get("sub"):
            c.text(px + 120, ty + c.lines(n["text"], tw, 34) * 44.2 + 6, tw, n["sub"], "ds", TEAL, "left")
        y += h + 8
    y += 4
    c.line(px + 28, y, px + pw - 28, y, DEEP, 3, dash="3 9")
    y += 18
    c.text(px + 28, y, 220, got, "dl", TEAL, "left")
    y += 50
    gw = (pw - 56 - 16 * (len(gains) - 1)) / len(gains)
    for k, g in enumerate(gains):
        x = px + 28 + k * (gw + 16)
        c.rect(x, y, gw, gain_h, fill=GOLD, rx=14)
        c.text(x + 10, y + (gain_h - 44.2) / 2, gw - 20, g["text"], "dn", DEEP, "center", (x, y, gw, gain_h))
    return bot


def squeeze(c: Canvas, spec: dict, y0: float) -> float:
    """名額線擠掉了誰（SAG 第 4 則：50 個名額擠掉罕見的橋樑實體）：
    heads = [排隊的左端標籤, 右端標籤, 名額線標籤]；nodes = [{text, sub?}（上方說明）, {text, sub?}（金點：被擠出去的那個）]；
    outcomes = 底下一條推理鏈的兩端 [{text}（起點）, {text}（終點）]，中間是金色的橋樑點，過了橋就斷（虛線打叉）。
    排隊的點是固定示意（不是實際數量），圖註要標「示意」。"""
    hl, hr, hcut = spec["heads"]
    top, bridge = spec["nodes"]
    a, b = spec["outcomes"]
    w = X1 - X0
    cols, rows_, pitch = 20, 3, 40
    keep = 12                                            # 前 12 欄留下，其餘被擠出去
    boxw, boxh = cols * pitch + 40, rows_ * pitch + 40
    th_top = _th(c, top, w)
    bh = _th(c, bridge, 560)
    chain_h = 40
    total = th_top + 14 + 54 + boxh + 18 + 44 + bh + 40 + chain_h + 34 + 39.2
    _fit(total, BOTTOM - y0, "squeeze")
    extra = min((BOTTOM - y0 - total) / 3, 40)
    y = y0
    c.text(X0, y, w, top["text"], "dn", DEEP, "left")
    if top.get("sub"):
        c.text(X0, y + c.lines(top["text"], w, 34) * 44.2 + 4, w, top["sub"], "ds", TEAL, "left")
    y += th_top + 14 + extra
    c.text(X0, y, 400, hl, "dl", TEAL, "left")
    c.text(X1 - 400, y, 400, hr, "dl", TEAL, "right")
    by = y + 54
    bx = X0 + (w - boxw) / 2
    c.rect(bx, by, boxw, boxh, fill="none", stroke=DEEP, sw=3, rx=18)
    cutx = bx + 20 + keep * pitch
    c.rect(bx + 6, by + 6, cutx - bx - 6 - pitch / 2 + 20, boxh - 12, fill=MID, rx=12, op=.14)
    for r in range(rows_):
        for k in range(cols):
            px, py = bx + 20 + pitch / 2 + k * pitch, by + 20 + pitch / 2 + r * pitch
            if k < keep:
                c.circle(px, py, 14, fill=MID)
            elif (r, k) == (2, 16):
                c.circle(px, py, 19, fill=GOLD, stroke=DEEP, sw=4)
            else:
                c.circle(px, py, 13, fill="none", stroke=TEAL, sw=2, dash="4 4")
    c.line(cutx, by - 14, cutx, by + boxh + 14, GOLD, 6, dash="12 8")
    c.text(cutx - 200, by + boxh + 18, 400, hcut, "dl", DEEP, "center")
    gx = bx + 20 + pitch / 2 + 16 * pitch
    gy = by + 20 + pitch / 2 + 2 * pitch
    ly = by + boxh + 18 + 44 + extra
    c.line(gx, gy + 22, gx, ly - 6, GOLD, 4)
    bw = 560
    bxl = min(max(gx - bw / 2, X0), X1 - bw)
    c.text(bxl, ly, bw, bridge["text"], "dn", DEEP, "center")
    if bridge.get("sub"):
        c.text(bxl, ly + c.lines(bridge["text"], bw, 34) * 44.2 + 4, bw, bridge["sub"], "ds", TEAL, "center")
    cy = ly + bh + 40 + chain_h / 2 + extra
    x1_, xm, x2_ = X0 + 40, X0 + 40 + w * .42, X1 - 40
    c.circle(x1_, cy, 20, fill=DEEP)
    c.circle(x2_, cy, 20, fill=DEEP)
    c.arrow(x1_ + 28, cy, xm - 28, cy, DEEP, 6, 18)
    c.circle(xm, cy, 24, fill=GOLD, stroke=DEEP, sw=4)
    c.line(xm + 30, cy, x2_ - 30, cy, TEAL, 5, dash="10 9")
    _cross(c, (xm + x2_) / 2, cy, 15, DEEP, 6)
    c.text(x1_ - 40, cy + 34, 220, a["text"], "ds", DEEP, "left")
    c.text(x2_ - 220 + 40, cy + 34, 220, b["text"], "ds", DEEP, "right")
    return cy + 34 + 39.2


def alias(c: Canvas, spec: dict, y0: float) -> float:
    """別名對齊：傳統做法合併、SAG 不合併（SAG 第 4 則）。heads = [上段標籤, 下段標籤]；
    outcomes = 同一個東西的 3 種寫法 [{text}]（上下兩段都畫）；nodes = [{text, sub?}（上段：合併後的那一個）, {text, sub?}（下段的說明）]。純示意。"""
    h1, h2 = spec["heads"]
    chips = spec["outcomes"]
    merged, plain = spec["nodes"]
    if len(chips) != 3:
        raise ValueError(f"alias 的 outcomes 要 3 種寫法，現在是 {len(chips)} 個")
    w = X1 - X0
    gap = 44
    cw = (w - 2 * gap) / 3
    chh = 64
    mh = _th(c, merged, w - 120) + 36
    ph = _th(c, plain, w)
    total = 44 + chh + 60 + mh + 40 + 44 + chh + 16 + ph
    _fit(total, BOTTOM - y0, "alias")
    extra = min((BOTTOM - y0 - total) / 3, 40)
    y = y0
    c.text(X0, y, w, h1, "dl", TEAL, "left")
    cy_ = y + 44
    cxs = [X0 + k * (cw + gap) + cw / 2 for k in range(3)]
    for k, ch in enumerate(chips):
        c.rect(cxs[k] - cw / 2, cy_, cw, chh, fill=DEEP, rx=14)
        c.text(cxs[k] - cw / 2 + 12, cy_ + (chh - 39.2) / 2, cw - 24, ch["text"], "ds", CREAM, "center", (cxs[k] - cw / 2, cy_, cw, chh))
    my = cy_ + chh + 60 + extra
    mx, mw = X0 + 60, w - 120
    for k in range(3):
        c.arrow(cxs[k], cy_ + chh + 4, X0 + w / 2 + (k - 1) * 150, my - 6, GOLD, 5, 16)
    c.rect(mx, my, mw, mh, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=18)
    mt = _th(c, merged, mw - 40)
    c.text(mx + 20, my + (mh - mt) / 2, mw - 40, merged["text"], "dn", DEEP, "center", (mx, my, mw, mh))
    if merged.get("sub"):
        c.text(mx + 20, my + (mh - mt) / 2 + c.lines(merged["text"], mw - 40, 34) * 44.2 + 6, mw - 40, merged["sub"], "ds", DEEP, "center", (mx, my, mw, mh))
    y = my + mh + 40 + extra
    c.line(X0, y - 18, X1, y - 18, TEAL, 2, dash="3 9")
    c.text(X0, y, w, h2, "dl", TEAL, "left")
    cy2 = y + 44
    for k, ch in enumerate(chips):
        c.rect(cxs[k] - cw / 2, cy2, cw, chh, fill="none", stroke=DEEP, sw=3, rx=14)
        c.text(cxs[k] - cw / 2 + 12, cy2 + (chh - 39.2) / 2, cw - 24, ch["text"], "ds", DEEP, "center", (cxs[k] - cw / 2, cy2, cw, chh))
    ty = cy2 + chh + 16
    c.text(X0, ty, w, plain["text"], "dn", DEEP, "left")
    if plain.get("sub"):
        c.text(X0, ty + c.lines(plain["text"], w, 34) * 44.2 + 4, w, plain["sub"], "ds", TEAL, "left")
    return ty + ph


def handoff(c: Canvas, spec: dict, y0: float) -> float:
    """把工作從線下搬到線上（SAG 第 4 則：別名對齊的壓力推遲到線上）。heads = [上帶標籤, 下帶標籤, 箭頭標籤]；
    nodes = [{text, sub?}（被搬走、線下不做的事）, {text, sub?}（線上接手的做法）]；outcomes[0] = {text}（線下因此得到的好處，金色）。純示意。"""
    ht, hb, ha = spec["heads"]
    gone, took = spec["nodes"]
    gain = spec["outcomes"][0]
    w = X1 - X0
    bw = 420
    top_h = max(_th(c, gone, bw - 40) + 40, c.lines(gain["text"], w - bw - 140, 34) * 44.2 + 40) + 66
    bot_h = _th(c, took, w - 84) + 40 + 66
    gap = 70
    total = top_h + gap + bot_h
    _fit(total, BOTTOM - y0, "handoff")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    top_h += extra * .5; bot_h += extra * .5; gap += extra * .0
    y = y0
    c.rect(X0, y, w, top_h, fill="none", stroke=DEEP, sw=3, rx=18)
    c.text(X0 + 22, y + 12, w - 44, ht, "dl", TEAL, "left")
    ih = top_h - 66 - 12
    iy = y + 66
    c.rect(X0 + 22, iy, bw, ih, fill="none", stroke=DEEP, sw=4, rx=14, dash="10 8")
    gt = _th(c, gone, bw - 40)
    c.text(X0 + 42, iy + (ih - gt) / 2, bw - 40, gone["text"], "dn", TEAL, "left", (X0 + 22, iy, bw, ih))
    if gone.get("sub"):
        c.text(X0 + 42, iy + (ih - gt) / 2 + c.lines(gone["text"], bw - 40, 34) * 44.2 + 6, bw - 40, gone["sub"], "ds", TEAL, "left", (X0 + 22, iy, bw, ih))
    _cross(c, X0 + 22 + bw - 30, iy + 30, 14, DEEP, 5)
    gx = X0 + 22 + bw + 50
    gw = X1 - 22 - gx
    c.rect(gx, iy, gw, ih, fill=GOLD, rx=14)
    c.text(gx + 20, iy + (ih - c.lines(gain["text"], gw - 40, 34) * 44.2) / 2, gw - 40, gain["text"], "dn", DEEP, "left", (gx, iy, gw, ih))
    y += top_h
    c.arrow(X0 + 22 + bw / 2, y - 6, X0 + 22 + bw / 2, y + gap - 4, GOLD, 8, 24)
    c.text(X0 + 22 + bw / 2 + 24, y + gap / 2 - 22, 440, ha, "ds", DEEP, "left")
    y += gap
    c.rect(X0, y, w, bot_h, fill=DEEP, rx=18)
    c.text(X0 + 22, y + 12, w - 44, hb, "dl", LIGHT, "left")
    bw = w - 44
    c.rect(X0 + 22, y + 66, bw, bot_h - 66 - 12, fill=TEAL, rx=14)
    tt = _th(c, took, bw - 40)
    ty = y + 66 + (bot_h - 66 - 12 - tt) / 2
    c.text(X0 + 42, ty, bw - 40, took["text"], "dn", CREAM, "left", (X0 + 22, y + 66, bw, bot_h - 78))
    if took.get("sub"):
        c.text(X0 + 42, ty + c.lines(took["text"], bw - 40, 34) * 44.2 + 6, bw - 40, took["sub"], "ds", CREAM, "left", (X0 + 22, y + 66, bw, bot_h - 78))
    return y + bot_h


def mismatch(c: Canvas, spec: dict, y0: float) -> float:
    """同一個東西寫法不同，SQL 就接不起來（SAG 第 4 則）。heads = [上段標籤, 下段標籤, 缺口標籤]；
    nodes = [{text（共同的寫法）, sub（上段說明）}, {text（另一種寫法）, sub（下段說明）}]；outcomes = 兩個事件 [{text, sub?}]。
    上段：兩個事件掛在同一個寫法上，金色粗線串起來；下段：兩個事件各掛不同寫法，中間斷開、標缺口標籤。純示意。"""
    h1, h2, hgap = spec["heads"]
    same, other = spec["nodes"]
    ea, eb = spec["outcomes"]
    w = X1 - X0
    evw, evh = 190, 112
    chw, chh = 190, 64
    ph = max(_th(c, {"text": same["sub"]}, w), 0) if same.get("sub") else 0
    qh = _th(c, {"text": other["sub"]}, w) if other.get("sub") else 0
    gh = c.lines(hgap, 300, 28) * 39.2
    total = 44 + evh + 14 + ph + 46 + 44 + evh + 14 + max(qh, gh)
    _fit(total, BOTTOM - y0, "mismatch")
    extra = min((BOTTOM - y0 - total) / 2, 50)
    y = y0

    def ev(x, yy, e):
        c.rect(x, yy, evw, evh, fill=DEEP, rx=14)
        t = _th(c, e, evw - 30)
        c.text(x + 15, yy + (evh - t) / 2, evw - 30, e["text"], "dn", CREAM, "center", (x, yy, evw, evh))
        if e.get("sub"):
            c.text(x + 15, yy + (evh - t) / 2 + c.lines(e["text"], evw - 30, 34) * 44.2 + 4, evw - 30, e["sub"], "ds", LIGHT, "center", (x, yy, evw, evh))

    def chip(cx, cy, label):
        c.rect(cx - chw / 2, cy - chh / 2, chw, chh, fill=GOLD, rx=32)
        c.text(cx - chw / 2 + 10, cy - 22, chw - 20, label, "dn", DEEP, "center", (cx - chw / 2, cy - chh / 2, chw, chh))

    c.text(X0, y, w, h1, "dl", TEAL, "left")
    cy = y + 44 + evh / 2
    ev(X0, y + 44, ea); ev(X1 - evw, y + 44, eb)
    mid = X0 + w / 2
    c.line(X0 + evw, cy, mid - chw / 2, cy, GOLD, 10)
    c.line(mid + chw / 2, cy, X1 - evw, cy, GOLD, 10)
    chip(mid, cy, same["text"])
    ty = y + 44 + evh + 14
    if same.get("sub"):
        c.text(X0, ty, w, same["sub"], "ds", TEAL, "center")
    y = ty + ph + 46 + extra
    c.line(X0, y - 24, X1, y - 24, TEAL, 2, dash="3 9")
    c.text(X0, y, w, h2, "dl", TEAL, "left")
    cy2 = y + 44 + evh / 2
    ev(X0, y + 44, ea); ev(X1 - evw, y + 44, eb)
    lx, rx_ = X0 + evw + 40 + chw / 2, X1 - evw - 40 - chw / 2
    c.line(X0 + evw, cy2, lx - chw / 2, cy2, GOLD, 10)
    c.line(rx_ + chw / 2, cy2, X1 - evw, cy2, GOLD, 10)
    chip(lx, cy2, same["text"]); chip(rx_, cy2, other["text"])
    c.line(lx + chw / 2 + 8, cy2, rx_ - chw / 2 - 8, cy2, TEAL, 4, dash="8 8")
    _cross(c, (lx + rx_) / 2, cy2, 13, DEEP, 5)
    ty2 = y + 44 + evh + 14
    c.text((lx + rx_) / 2 - 150, ty2, 300, hgap, "ds", DEEP, "center")
    if other.get("sub"):
        c.text(X0, ty2 + gh + 6, w, other["sub"], "ds", TEAL, "center")
        return ty2 + gh + 6 + qh
    return ty2 + gh


def _lock(c: Canvas, cx: float, cy: float, s: float, color: str) -> None:
    c.rect(cx - s * .55, cy - s * .1, s * 1.1, s * .85, fill=color, rx=6)
    c.raw(f'<path class="bg" d="M {cx - s * .32:.1f} {cy - s * .1:.1f} v {-s * .22:.1f} a {s * .32:.1f} {s * .32:.1f} 0 0 1 {s * .64:.1f} 0 v {s * .22:.1f}" fill="none" stroke="{color}" stroke-width="5"/>')


def ledger(c: Canvas, spec: dict, y0: float) -> float:
    """只能往後新增的記錄簿（SAG 第 4 則：append-only）。heads = [時間軸標籤]；
    nodes = 依時間由上到下的紀錄 2～5 筆 [{text, sub?, new?: true}]（舊的畫鎖，new 的畫金色與「＋」）；
    outcomes[0] = {text, sub?}（右邊一塊說明：舊的改不了、只能再加新的）。純示意，例子要標「假設」。"""
    hd = spec["heads"][0]
    rows = spec["nodes"]
    note = spec["outcomes"][0]
    if not 2 <= len(rows) <= 5:
        raise ValueError(f"ledger 的 nodes 要 2～5 筆，現在是 {len(rows)}")
    w = X1 - X0
    cw, ax = 500, X0 + 52
    rh = [max(_th(c, r, cw - (140 if r.get('ask') else 120)) + 28, 84) for r in rows]
    nw = X1 - (ax + cw) - 36
    nh = _th(c, note, nw - 36) + 40
    total = 44 + sum(rh) + 16 * (len(rows) - 1)
    _fit(max(total, 44 + nh), BOTTOM - y0, "ledger")
    add = min((BOTTOM - y0 - total) / len(rows), 50 if len(rows) >= 3 else 110)   # 只有 2 筆時讓每列撐高，圖才用得滿
    rh = [h + add for h in rh]
    total += add * len(rows)
    c.text(X0, y0, 300, hd, "dl", TEAL, "left")
    c.arrow(X0 + 16, y0 + 50, X0 + 16, y0 + total - 4, TEAL, 5, 16)
    y = y0 + 44
    for k, (r, h) in enumerate(zip(rows, rh)):
        new = bool(r.get("new"))
        c.rect(ax, y, cw, h, fill=GOLD if new else "none", stroke=DEEP, sw=3, rx=14, op=.35 if new else None)
        tx, tw = (ax + 70, cw - 140) if r.get("ask") else (ax + 24, cw - 120)   # 有 ask 的，字往右讓出「？」
        t = _th(c, r, tw)
        c.text(tx, y + (h - t) / 2, tw, r["text"], "dn", DEEP, "left", (ax, y, cw, h))
        if r.get("sub"):
            c.text(tx, y + (h - t) / 2 + c.lines(r["text"], tw, 34) * 44.2 + 6, tw, r["sub"], "ds", DEEP if new else TEAL, "left", (ax, y, cw, h))   # 金色底的列用深色字，對比度才夠
        if r.get("ask"):                                  # 新舊衝突、分不出誰有效的那幾筆：左邊放一個金色「？」
            c.circle(ax + 38, y + h / 2, 22, fill=GOLD, stroke=DEEP, sw=3)
            c.text(ax + 24, y + h / 2 - 20, 28, "？", "dl", DEEP, "center")
        if new:
            c.circle(ax + cw - 48, y + h / 2, 24, fill=GOLD, stroke=DEEP, sw=3)
            c.line(ax + cw - 60, y + h / 2, ax + cw - 36, y + h / 2, DEEP, 5)
            c.line(ax + cw - 48, y + h / 2 - 12, ax + cw - 48, y + h / 2 + 12, DEEP, 5)
        else:
            _lock(c, ax + cw - 48, y + h / 2 - 4, 34, DEEP)
        y += h + 16
    ny = y0 + 44 + (total - 44 - nh) / 2
    nx = ax + cw + 36
    c.rect(nx, ny, nw, nh, fill=DEEP, rx=14)
    c.text(nx + 18, ny + 20, nw - 36, note["text"], "dn", CREAM, "left", (nx, ny, nw, nh))
    if note.get("sub"):
        c.text(nx + 18, ny + 20 + c.lines(note["text"], nw - 36, 34) * 44.2 + 6, nw - 36, note["sub"], "ds", LIGHT, "left", (nx, ny, nw, nh))
    c.arrow(nx - 6, ny + nh / 2, ax + cw + 6, ny + nh / 2, GOLD, 6, 18)
    return y0 + total


# ------------------------------------------------------------------ Claude Code 系列（2026-10-28）：視窗風格的六種示意圖
DESC = {      # 給審查者與人看的「畫面」描述（build_package 輸出）：文字以外，圖上畫了什麼
    "ring": "幾個圓圈排成一圈，相鄰的兩個之間各一條箭頭，順時針繞回起點（每個圓恰好送出一條、接到一條箭頭）；箭頭旁可有標籤，金色的圓與箭頭是要注意的那個；圈中央可有一句說明",
    "transcript": "一個終端機視窗，一列一個動作（提示符號、工具呼叫、失敗、通過）；有標 feeds 的列，金色箭頭從那一列繞到下一列並寫上標籤；金色菱形的列是 Hook 在這個節點介入",
    "oneloop": "中間一個圈，圈裡是兩個框（規劃、執行）；兩側各一個被打叉的虛線框（規劃模組、執行模組）；圈下一行說明",
    "intercept": "上下兩條路：上面是一句話直接通到檔案；下面是工具呼叫先過一道金框的關卡（關卡裡列出檢查項目）才到檔案",
    "dial": "一條有刻度的軌道，金色旋鈕停在其中一格；左上的人伸手轉旋鈕（金色箭頭），右上的模型要伸手但被打叉；軌道下一行說明",
    "lanes": "最上面一個問題，分成兩欄：左欄是兩個項目，一個向下的箭頭指向金色的「自動核准」；右欄是一個深色框，寫另一種動作的處理方式",
    "turn": "左上是「模型給出回應」，金色箭頭指向右邊金色的「最終答案：結束」；往下的箭頭通向金框的「權限檢查」，再分成打勾（同意）與打叉（拒絕）兩個結果；兩個結果各有箭頭，指向右邊一張「對話紀錄」紙上各自新增的一行；最下面一個虛線框說明回到下一輪",
    "sockets": "上方一條深色橫條，下緣三個插孔，各接一根金色插頭到下面三張卡（名稱加一句它解決什麼）",
    "lazy": "左邊一個終端機視窗列出三行（名稱加一句描述），其中一行金色框起來；金色箭頭指向右邊展開的一整份文件",
    "hub": "上面一個被叉掉的虛線框（各接各的客製程式）；下面左邊 Claude Code，金色箭頭通向一條金色直條（共通介面），再各畫一條線連到右邊幾個外部服務",
    "pinned": "並排三個終端機視窗，每個視窗最上面都釘著同一個金色方塊，下面的灰條內容各不相同；底下一句說明",
    "combo": "上面：左邊一個框，金色箭頭指向右邊視窗，視窗裡也有一個同名的金邊框；下面：左邊兩個來源框各連一條線，匯到右邊同一個金色方塊",
    "compact": "左邊視窗很多行灰條（亮色是保留的，暗色是丟掉的），金色箭頭通向右邊視窗：只剩兩個框和一個游標；底下一個虛線框提醒",
    "sidecar": "左邊主視窗只有兩行（派出任務、收到摘要）；右邊側視窗滿是灰條；上面一條箭頭送出任務，下面一條金色箭頭只把摘要帶回來",
    "grain": "上段一條深色膠捲（整部影片），只有中間一小段是金色（真正需要的那一段，寬度不按比例）；膠捲下一行說明、一個被打叉的下場。下段一段文字（五行淡灰條），只有中間一行是深色（只抓到這一句），右邊一行說明與一個被打叉的下場",
    "ballot": "一張答案卡：深色抬頭，下面一列一個選項，每列左邊一個方格；打勾的格子是金色、整列墊淡金色；上方可有一個問題框，箭頭指向答案卡",
    "thresh": "每個選項一條橫條（長度與分數成正比，軸 0 到 1），一條直的虛線標出門檻；超過門檻的橫條是金色，其餘是半透明藍綠；每條右邊寫分數",
    "murky": "左邊一頁報告：上下是文字灰條、中間夾一張小表格，表格角落一個金色問號；右邊一句問話，箭頭往下指向兩個被打叉的下場",
    "layers": "兩排各一道防線：上排是指令先經過一道關卡；下排是指令在一個虛線容器裡，容器裡有金色的工作目錄，指令想往外走被叉掉、碰不到容器外的框",
}


def _win(c: Canvas, x, y, w, h, title="") -> None:
    c.rect(x, y, w, h, fill=DEEP, rx=22)
    c.raw(f'<path class="bg" d="M{x} {y + 60} V{y + 22} Q{x} {y} {x + 22} {y} H{x + w - 22} Q{x + w} {y} {x + w} {y + 22} V{y + 60} Z" fill="{ABYSS}"/>')
    for i in range(3):
        c.circle(x + 36 + 34 * i, y + 30, 9, fill=CREAM, op=.35)
    if title:
        if w >= 700:
            c.text(x + 150, y + 10, w - 300, title, "ds", CREAM, "center")
        else:                                              # 窄視窗：標題放在三顆點的右邊
            c.text(x + 130, y + 10, w - 150, title, "ds", CREAM, "left")


def _tick(c: Canvas, x, y, color=LIGHT, sw=6) -> None:
    c.poly([(x - 12, y), (x - 3, y + 11), (x + 13, y - 11)], stroke=color, sw=sw)


def _cross2(c: Canvas, x, y, r=11, color=CREAM, sw=6) -> None:
    c.line(x - r, y - r, x + r, y + r, color, sw)
    c.line(x + r, y - r, x - r, y + r, color, sw)


def _tw(s: str, size: int = 34) -> float:
    return sum(size if ord(ch) > 127 else size * .62 for ch in s)


def transcript(c: Canvas, spec: dict, y0: float) -> float:
    """heads[0] = 視窗標題（例：假設的例子）；nodes = 一列一個動作 [{text, tone}]，tone = prompt／tool／fail／ok／hook（金色菱形，Hook 在這一行介入）；
    text 裡的全形空白「　」把工具名（淺藍綠粗體）和內容分開；有 feeds: true 的列（通常是 fail）會畫金色箭頭繞到下一列，
    outcomes[0].text 是箭頭的標籤（下一輪的輸入）。純示意，圖上要標假設。"""
    rows = spec["nodes"]
    n = len(rows)
    if not 3 <= n <= 7:
        raise ValueError(f"transcript 的 nodes 要 3～7 列，現在是 {n}")
    w, bar = X1 - X0, 60
    _fit(bar + 40 + n * 66, BOTTOM - y0, "transcript")
    pitch = min(84.0, (BOTTOM - y0 - bar - 40) / n)
    H = bar + 24 + n * pitch + 16
    _win(c, X0, y0, w, H, (spec.get("heads") or [""])[0])
    cys = [y0 + bar + 24 + i * pitch + pitch / 2 for i in range(n)]
    tx, tw = X0 + 96, 500
    for r, cy in zip(rows, cys):
        tone = r.get("tone", "tool")
        ix = X0 + 44
        if tone == "prompt":
            c.poly([(ix - 8, cy - 14), (ix + 10, cy), (ix - 8, cy + 14)], stroke=CREAM, sw=6)
        elif tone == "tool":
            c.circle(ix + 2, cy, 11, fill=LIGHT)
        elif tone == "fail":
            _cross2(c, ix + 2, cy)
        elif tone == "ok":
            _tick(c, ix + 2, cy)
        elif tone == "hook":
            c.poly([(ix + 2, cy - 14), (ix + 16, cy), (ix + 2, cy + 14), (ix - 12, cy)], fill=GOLD, closed=True)
        txt = r["text"]
        if "　" in txt:
            lab, rest = txt.split("　", 1)
            lw = _tw(lab) + 14
            c.text(tx, cy - 22, lw, lab, "dn", GOLD if tone == "hook" else LIGHT, "left", (X0, y0, w, H))
            c.text(tx + lw + 12, cy - 22, tw - lw - 12, rest, "dt", CREAM, "left", (X0, y0, w, H))
        else:
            c.text(tx, cy - 22, tw, txt, "dn" if tone in ("prompt", "ok") else "dt", CREAM, "left", (X0, y0, w, H))
    for i, r in enumerate(rows):
        if r.get("feeds") and i + 1 < n:
            ax, bx = X0 + tx - X0 + tw + 20, X0 + 700
            c.line(ax, cys[i], bx, cys[i], GOLD, 6)
            c.line(bx, cys[i], bx, cys[i + 1], GOLD, 6)
            c.arrow(bx, cys[i + 1], ax + 14, cys[i + 1], GOLD, 6, 18)
            lab = spec["outcomes"][0]["text"]
            lw_ = X1 - (bx + 22) - 16
            lh = c.lines(lab, lw_, 28) * 39.2
            c.text(bx + 22, (cys[i] + cys[i + 1]) / 2 - lh / 2, lw_, lab, "dl", GOLD, "left", (X0, y0, w, H))
    return y0 + H


def _arc_arrow(c: Canvas, cx, cy, r, a0, a1, color=TEAL, sw=8) -> None:
    """順時針的圓弧（角度，度；0 在右邊、90 在下面），末端畫箭頭。"""
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    c.raw(f'<path class="bg" d="M{p0[0]:.1f} {p0[1]:.1f} A{r} {r} 0 {large} 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
    a = math.radians(a1)
    tx, ty = -math.sin(a), math.cos(a)           # 順時針的切線方向
    nx, ny = math.cos(a), math.sin(a)
    tip = (p1[0] + tx * 30, p1[1] + ty * 30)
    c.poly([(p1[0] + nx * 22, p1[1] + ny * 22), (p1[0] - nx * 22, p1[1] - ny * 22), tip], fill=color, closed=True)


def oneloop(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = 圈裡的兩個框 [{text}（規劃）, {text}（執行）]；outcomes = 兩側被打叉的虛線框 [{text}, {text}]；heads[0] = 圈下面的一行說明。"""
    chips, ghosts, cap = spec["nodes"], spec["outcomes"], spec["heads"][0]
    caph = c.lines(cap, 760, 34) * 44.2
    _fit(30 + 2 * 150 + 30 + caph, BOTTOM - y0, "oneloop")
    R = min(200, (BOTTOM - y0 - 60 - caph) / 2)
    cx, cy = 540, y0 + 30 + R
    _arc_arrow(c, cx, cy, R, -62, 268, TEAL)
    gx, gy = cx + R * math.cos(math.radians(100)), cy + R * math.sin(math.radians(100))
    c.circle(gx, gy, 17, fill=GOLD)
    for k, ch in enumerate(chips):
        c.textbox(cx - 115, cy - 36 - 44 + k * 88, 230, ch["text"], None, h=64, align="center", pad=10)
    for k, gh in enumerate(ghosts):
        gx0 = X0 if k == 0 else X1 - 220
        gy0 = cy - 55
        c.rect(gx0, gy0, 220, 110, fill="none", stroke=TEAL, sw=3, dash="10 8", rx=16)
        c.text(gx0 + 10, gy0 + 33, 200, gh["text"], "dt", TEAL, "center", (gx0, gy0, 220, 110))
        c.circle(gx0 + 220 - 6, gy0 + 6, 22, fill=CREAM, stroke=TEAL, sw=4)
        _cross2(c, gx0 + 214, gy0 + 6, 9, TEAL, 5)
    c.text(X0 + 80, cy + R + 28, 760, cap, "dt", DEEP, "center")
    return cy + R + 28 + caph


def _doc(c: Canvas, x, y, w, h, label: str) -> None:
    fold = 28
    c.poly([(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h)], fill=CREAM, stroke=DEEP, sw=4, closed=True)
    c.poly([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)], stroke=DEEP, sw=4)
    c.text(x + 6, y + h / 2 - 22, w - 12, label, "dn", DEEP, "center", (x, y, w, h))


def intercept(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [上排標籤, 下排標籤, 關卡標籤, 檔案]；nodes = [{text}（只用文字說的那句話）, {text}（工具呼叫）]；outcomes = 關卡裡的檢查項目 2～3 個 [{text}]。"""
    h0, h1, hg, hf = spec["heads"][:4]
    say, call = spec["nodes"][0], spec["nodes"][1]
    checks = spec["outcomes"]
    if not 2 <= len(checks) <= 3:
        raise ValueError("intercept 的 outcomes 要 2～3 個檢查項目")
    gh = 70 + 56 * len(checks)
    total = 44 + 130 + 40 + 44 + max(gh, 130)
    _fit(total, BOTTOM - y0, "intercept")
    ex = min(70.0, (BOTTOM - y0 - total) / 3)
    fx, fw = X1 - 170, 170
    c.text(X0, y0, min(600.0, _tw(h0, 28) + 16), h0, "dl", TEAL)
    ry = y0 + 44
    c.rect(X0, ry, 440, 130 + ex, fill="none", stroke=TEAL, sw=3, dash="10 8", rx=18)
    c.text(X0 + 22, ry + (130 + ex - c.lines(say["text"], 396, 34) * 44.2) / 2, 396, say["text"], "dt", DEEP, "left", (X0, ry, 440, 130 + ex))
    c.arrow(X0 + 456, ry + (130 + ex) / 2, fx - 14, ry + (130 + ex) / 2, TEAL, 5, 16)
    _doc(c, fx, ry + ex / 2, fw, 130, hf)
    y2 = ry + 130 + ex + 40 + ex
    c.text(X0, y2, min(600.0, _tw(h1, 28) + 16), h1, "dl", TEAL)
    ry2 = y2 + 44
    rh = max(gh, 130) + ex
    c.textbox(X0, ry2 + (rh - 130) / 2, 300, call["text"], None, h=130, align="center", pad=14)
    gx = X0 + 380
    c.arrow(X0 + 316, ry2 + rh / 2, gx - 12, ry2 + rh / 2, TEAL, 5, 16)
    c.rect(gx, ry2, 300, rh, fill="none", stroke=GOLD, sw=7, rx=18)
    c.text(gx + 14, ry2 + 12, 272, hg, "dl", DEEP, "center")
    for k, ck in enumerate(checks):
        yy = ry2 + 66 + k * 56
        _tick(c, gx + 40, yy + 20, TEAL, 6)
        c.text(gx + 70, yy, 214, ck["text"], "dt", DEEP, "left", (gx, ry2, 300, rh))
    c.arrow(gx + 316, ry2 + rh / 2, fx - 14, ry2 + rh / 2, TEAL, 5, 16)
    _doc(c, fx, ry2 + (rh - 130) / 2, fw, 130, hf)
    return ry2 + rh


def dial(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = [{text}（人）, {text}（模型）]；heads[0] = 軌道下面的一行說明；選用 heads[1]、heads[2] = 軌道左、右端的標籤。人伸手轉旋鈕（金色箭頭），模型的箭頭被打叉。"""
    me, model = spec["nodes"][0], spec["nodes"][1]
    cap = spec["heads"][0]
    ends = spec["heads"][1:3] if len(spec["heads"]) >= 3 else None
    caph = c.lines(cap, 760, 34) * 44.2
    gap = 58 + (46 if ends else 0)
    _fit(250 + gap - 8 + caph + 20, BOTTOM - y0, "dial")
    ty = y0 + 250 + min(90.0, (BOTTOM - y0 - 250 - gap - caph - 12) / 2)
    xs = [X0 + 40 + k * (X1 - X0 - 80) / 7 for k in range(8)]
    kx = xs[2]
    c.line(xs[0], ty, xs[-1], ty, DEEP, 8)
    for x in xs:
        c.line(x, ty - 18, x, ty + 18, DEEP, 4)
    c.circle(kx, ty, 32, fill=GOLD, stroke=DEEP, sw=5)
    px = X0 + 120
    c.circle(px, y0 + 38, 28, fill=TEAL)
    c.raw(f'<path class="bg" d="M{px - 56} {y0 + 128} Q{px - 56} {y0 + 76} {px} {y0 + 76} Q{px + 56} {y0 + 76} {px + 56} {y0 + 128} Z" fill="{TEAL}"/>')
    c.text(px - 80, y0 + 134, 160, me["text"], "dn", DEEP, "center")
    c.arrow(px + 66, y0 + 100, kx - 26, ty - 40, GOLD, 7, 20)
    mx = X1 - 190
    c.textbox(mx - 80, y0 + 30, 220, model["text"], None, h=76, align="center", pad=10)
    sx, sy, ex, ey = mx - 20, y0 + 118, kx + 34, ty - 40
    c.line(sx, sy, ex, ey, TEAL, 5, dash="12 10")
    mxp, myp = (sx + ex) / 2, (sy + ey) / 2
    c.circle(mxp, myp, 24, fill=CREAM, stroke=TEAL, sw=4)
    _cross2(c, mxp, myp, 10, TEAL, 5)
    cy = ty + 58
    if ends:
        c.text(xs[0] - 30, ty + 34, 300, ends[0], "dl", TEAL, "left")
        c.text(xs[-1] - 270, ty + 34, 300, ends[1], "dl", TEAL, "right")
        cy = ty + 104
    c.text(X0 + 80, cy, 760, cap, "dt", DEEP, "center")
    return cy + caph


def lanes(c: Canvas, spec: dict, y0: float) -> float:
    """nodes = [{text}（最上面的問題）, 左欄的項目…（1～3 個 {text}）]；heads = [左欄標題, 右欄標題]；outcomes = [{text}（左欄結果，金色，項目下方有箭頭指向它）, {text}（右欄結果，深色大框）]。"""
    q, items = spec["nodes"][0], spec["nodes"][1:]
    hl, hr = spec["heads"][:2]
    left, right = spec["outcomes"][:2]
    cw = 430
    qh = c.lines(q["text"], 620 - 44, 34) * 44.2 + 36
    ih, rh, ag = 66, 100, 40
    stack = len(items) * (ih + 14) + ag + rh
    total = qh + 70 + 54 + stack
    _fit(total, BOTTOM - y0, "lanes")
    ex = min(34.0, (BOTTOM - y0 - total) / (len(items) + 2))
    ih, rh = ih + ex, rh + ex
    stack = len(items) * (ih + 14) + ag + rh
    qx = 540 - 310
    c.textbox(qx, y0, 620, q["text"], None, h=qh, align="center", pad=22)
    lx, rx = X0, X1 - cw
    top = y0 + qh + 70
    c.arrow(540 - 120, y0 + qh + 4, lx + cw / 2, top - 6, TEAL, 5, 16)
    c.arrow(540 + 120, y0 + qh + 4, rx + cw / 2, top - 6, TEAL, 5, 16)
    c.text(lx, top, cw, hl, "dl", TEAL, "center")
    c.text(rx, top, cw, hr, "dl", TEAL, "center")
    y = top + 54
    for it in items:
        c.rect(lx, y, cw, ih, fill=CREAM, stroke=DEEP, sw=3, rx=14)
        c.text(lx + 20, y + (ih - 44) / 2, cw - 40, it["text"], "dt", DEEP, "center", (lx, y, cw, ih))
        y += ih + 14
    c.arrow(lx + cw / 2, y - 10, lx + cw / 2, y + ag - 4, DEEP, 5, 16)
    y += ag
    c.rect(lx, y, cw, rh, fill=GOLD, rx=16)
    c.text(lx + 20, y + (rh - 44) / 2, cw - 40, left["text"], "dn", DEEP, "center", (lx, y, cw, rh))
    rbh = len(items) * (ih + 14) - 14
    c.rect(rx, top + 54, cw, rbh, fill=DEEP, rx=16)
    c.text(rx + 24, top + 54 + (rbh - c.lines(right["text"], cw - 48, 34) * 44.2) / 2, cw - 48, right["text"], "dn", CREAM, "center", (rx, top + 54, cw, rbh))
    return top + 54 + stack


def layers(c: Canvas, spec: dict, y0: float) -> float:
    """heads = [上排標籤, 下排標籤, 容器外的框]；nodes = [{text}（工作目錄，金色）, {text}（錯誤的指令）]；outcomes[0] = {text}（關卡旁的字）。
    上排：指令 → 關卡；下排：指令在虛線容器裡，往外走被叉掉。"""
    ha, hb, hout = spec["heads"][:3]
    wd, cmd = spec["nodes"][0], spec["nodes"][1]
    gate = spec["outcomes"][0]
    total = 44 + 90 + 56 + 54 + 140
    _fit(total, BOTTOM - y0, "layers")
    c.text(X0, y0, 700, ha, "dl", TEAL)
    ay = y0 + 44
    c.textbox(X0, ay, 400, cmd["text"], None, h=90, align="center", pad=10)
    c.arrow(X0 + 416, ay + 45, X0 + 492, ay + 45, TEAL, 5, 16)
    gx = X0 + 510
    c.rect(gx, ay - 12, 26, 114, fill=TEAL, rx=6)
    c.rect(gx + 100, ay - 12, 26, 114, fill=TEAL, rx=6)
    c.line(gx + 26, ay + 45, gx + 100, ay + 45, TEAL, 5, dash="8 8")
    c.text(gx + 146, ay + 45 - 22, X1 - (gx + 146), gate["text"], "dn", DEEP, "left")
    by = ay + 90 + 56
    c.text(X0, by, 700, hb, "dl", TEAL)
    cy0 = by + 54
    cwid, ch_ = 640, 140
    c.rect(X0, cy0, cwid, ch_, fill="none", stroke=TEAL, sw=5, dash="12 9", rx=20)
    c.rect(X0 + 16, cy0 + 20, 220, ch_ - 40, fill=GOLD, rx=14)
    c.text(X0 + 22, cy0 + (ch_ - 44) / 2, 208, wd["text"], "dn", DEEP, "center", (X0 + 16, cy0 + 20, 220, ch_ - 40))
    c.textbox(X0 + 252, cy0 + 25, 356, cmd["text"], None, h=ch_ - 50, align="center", pad=6)
    ox = X0 + cwid + 40
    c.line(X0 + 608, cy0 + ch_ / 2, X0 + cwid, cy0 + ch_ / 2, TEAL, 5)
    c.line(X0 + cwid, cy0 + ch_ / 2, ox - 6, cy0 + ch_ / 2, TEAL, 5, dash="8 8")
    c.circle(X0 + cwid, cy0 + ch_ / 2, 24, fill=CREAM, stroke=TEAL, sw=4)
    _cross2(c, X0 + cwid, cy0 + ch_ / 2, 10, TEAL, 5)
    c.rect(ox, cy0 + 20, X1 - ox, ch_ - 40, fill="none", stroke=TEAL, sw=3, dash="8 8", rx=14)
    c.text(ox + 6, cy0 + (ch_ - c.lines(hout, X1 - ox - 12, 28) * 39.2) / 2, X1 - ox - 12, hout, "ds", TEAL, "center", (ox + 8, cy0 + 28, X1 - ox - 16, ch_ - 56))
    return cy0 + ch_


def turn(c: Canvas, spec: dict, y0: float) -> float:
    """一輪怎麼走（2026-10-28，Claude Code 第 1 則）：nodes = [{text, sub?}（模型給出回應）, {text, sub?}（權限檢查）, {text}（對話紀錄裡的第一行）, {text}（第二行）]；
    heads = [走向權限檢查的箭頭標籤, 對話紀錄的標題]；outcomes = [{text}（最終答案，金色，直接結束）, {text}（同意，打勾）, {text}（拒絕，打叉）]；loop = 底部虛線框的說明（選用）。
    同意與拒絕的結果各寫進對話紀錄一行；金色是結束。"""
    resp, gate, l1, l2 = spec["nodes"][:4]
    h_arrow, h_paper = spec["heads"][:2]
    fin, yes, no = spec["outcomes"][:3]
    loop = spec.get("loop")
    bw, gap = 420, 80
    bh = 110
    lh = (c.lines(loop, X1 - X0 - 44, 28) * 39.2 + 36) if loop else 0
    rh, rg = 76, 16
    ah = 54                                              # 回應 → 權限檢查 的箭頭段
    gi = bw - 40
    gh = max(100.0, c.lines(gate["text"], gi, 34) * 44.2 + ((c.lines(gate["sub"], gi, 28) * 39.2 + 6) if gate.get("sub") else 0) + 36)
    total = bh + ah + gh + 46 + 2 * rh + rg + (24 + lh if loop else 0)
    _fit(total, BOTTOM - y0, "turn")
    X2 = X0 + bw + gap
    c.textbox(X0, y0, bw, resp["text"], resp.get("sub"), h=bh)
    c.arrow(X0 + bw + 8, y0 + bh / 2, X2 - 8, y0 + bh / 2, GOLD, 7, 20)
    c.textbox(X2, y0, bw, fin["text"], None, fill=GOLD, tcolor=DEEP, h=bh, align="center")
    gy = y0 + bh + ah
    c.arrow(X0 + 60, y0 + bh + 6, X0 + 60, gy - 6, TEAL, 5, 16)
    c.text(X0 + 84, y0 + bh + 6, 330, h_arrow, "dl", TEAL, "left")
    c.rect(X0, gy, bw, gh, fill="none", stroke=GOLD, sw=7, rx=18)
    iw = bw - 40
    t1 = c.lines(gate["text"], iw, 34) * 44.2
    t2 = (c.lines(gate["sub"], iw, 28) * 39.2 + 6) if gate.get("sub") else 0
    gty = gy + (gh - t1 - t2) / 2
    c.text(X0 + 20, gty, iw, gate["text"], "dn", DEEP, "center", (X0, gy, bw, gh))
    if gate.get("sub"):
        c.text(X0 + 20, gty + t1 + 6, iw, gate["sub"], "ds", DEEP, "center", (X0, gy, bw, gh))
    ry = gy + gh + 46
    sx = X0 + 20                                         # 左邊的脊線，由權限檢查往下接到兩個結果
    c.line(sx, gy + gh, sx, ry + rh + rg + rh / 2, TEAL, 5)
    rows = [(yes, True), (no, False)]
    mids = []
    for k, (o, ok) in enumerate(rows):
        yy = ry + k * (rh + rg)
        mid = yy + rh / 2
        mids.append(mid)
        c.arrow(sx, mid, X0 + 62, mid, TEAL, 5, 14)
        c.rect(X0 + 66, yy, bw - 66, rh, fill="none", stroke=TEAL, sw=4, rx=16)
        if ok:
            _tick(c, X0 + 98, mid, TEAL, 6)
        else:
            _cross2(c, X0 + 98, mid, 10, TEAL, 5)
        c.text(X0 + 124, mid - 22, bw - 66 - 70, o["text"], "dn", DEEP, "left", (X0 + 66, yy, bw - 66, rh))
    py, ph = gy, ry + 2 * rh + rg - gy
    c.rect(X2, py, bw, ph, fill=CREAM, stroke=DEEP, sw=4, rx=10)
    c.text(X2 + 20, py + 12, bw - 40, h_paper, "dl", TEAL, "left")
    for k, (ln, m) in enumerate(zip((l1, l2), mids)):
        c.arrow(X0 + bw + 6, m, X2 + 22, m, TEAL, 5, 14)
        c.text(X2 + 36, m - 22, bw - 56, "＋ " + ln["text"], "dn", DEEP, "left", (X2, py, bw, ph))
    y = ry + 2 * rh + rg
    if loop:
        y += 24
        c.rect(X0, y, X1 - X0, lh, fill="none", stroke=TEAL, sw=3, dash="10 8", rx=16)
        c.text(X0 + 22, y + 18, X1 - X0 - 44, loop, "dt", TEAL, "left", (X0, y, X1 - X0, lh))
        y += lh
    return y


def _ghost(c: Canvas, x: float, y: float, w: float, color=CREAM, op=.3) -> None:
    """視窗裡一行看不清字的灰條（示意「有一行紀錄」）。"""
    c.rect(x, y, w, 12, fill=color, rx=6, op=op)


def sockets(c: Canvas, spec: dict, y0: float) -> float:
    """三個擴充點（2026-10-28，Claude Code 第 2 則）：heads[0] = 上方深色橫條的字；nodes = 3 個 [{text（名稱）, sub（解決什麼問題）}]。
    橫條下緣有三個插孔，各自一根金色插頭接到下面的卡。"""
    cap, items = spec["heads"][0], spec["nodes"]
    if len(items) != 3:
        raise ValueError(f"sockets 的 nodes 要剛好 3 個擴充點，現在是 {len(items)}")
    cw, gap, pad = 296, 16, 16
    inner = cw - 2 * pad
    ch = max(c.lines(n["text"], inner, 34) * 44.2 + c.lines(n["sub"], inner, 28) * 39.2 + 6 for n in items) + 2 * pad + 8
    caph = c.lines(cap, X1 - X0 - 60, 34) * 44.2
    bar_h = 22 + caph + 14 + 52
    stem = 54
    _fit(bar_h + stem + ch, BOTTOM - y0, "sockets")
    ex = min(70.0, (BOTTOM - y0 - (bar_h + stem + ch)) / 2)
    stem += ex / 2
    ch += ex
    ex = 0.0
    c.rect(X0, y0, X1 - X0, bar_h, fill=DEEP, rx=22)
    c.text(X0 + 30, y0 + 22, X1 - X0 - 60, cap, "dn", CREAM, "center", (X0, y0, X1 - X0, bar_h))
    for k, n in enumerate(items):
        cx = X0 + cw / 2 + k * (cw + gap)
        sy = y0 + bar_h - 36
        c.circle(cx, sy, 22, fill=ABYSS, stroke=LIGHT, sw=4)
        c.line(cx, sy + 6, cx, y0 + bar_h + stem + ex, GOLD, 12)
        c.rect(cx - 20, y0 + bar_h + stem + ex - 26, 40, 26, fill=GOLD, rx=8)
        c.textbox(cx - cw / 2, y0 + bar_h + stem + ex, cw, n["text"], n["sub"], h=ch, align="center", pad=pad)
    return y0 + bar_h + stem + ex + ch


def lazy(c: Canvas, spec: dict, y0: float) -> float:
    """平常一行、用到才全讀進來（2026-10-28）：heads[0] = 左窗標題；nodes = 3 個 [{text（名稱）, sub（一行描述）, emph?（被用到的那個，剛好一個）}]；
    outcomes[0] = {text（文件標題）, sub?（文件裡的說明）}。左窗的每一行平常都在，被用到的那一行用金色箭頭指向右邊展開的整份文件。"""
    items, doc = spec["nodes"], spec["outcomes"][0]
    if len(items) != 3 or sum(1 for n in items if n.get("emph")) != 1:
        raise ValueError("lazy 的 nodes 要 3 個，且剛好 1 個 emph（被用到的那個）")
    ww, dw, bar = 520, 330, 60
    iw = ww - 2 * 34
    pitch = max(c.lines(n["text"], iw, 34) * 44.2 + c.lines(n["sub"], iw, 28) * 39.2 + 6 for n in items) + 22
    pitch = min(pitch + max(0.0, (BOTTOM - y0 - (bar + 12 + 3 * pitch + 6)) / 3), 140.0)
    H = bar + 12 + 3 * pitch + 6
    _fit(H, BOTTOM - y0, "lazy")
    ty = y0
    DX = X1 - dw
    _win(c, X0, ty, ww, H, spec["heads"][0])
    c.rect(DX, ty, dw, H, fill=CREAM, stroke=DEEP, sw=4, rx=10)
    c.text(DX + 16, ty + 16, dw - 32, doc["text"], "dn", DEEP, "center", (DX, ty, dw, H))
    sub_h = (c.lines(doc["sub"], dw - 40, 28) * 39.2 + 18) if doc.get("sub") else 0
    n_gh = int((H - 16 - 60 - sub_h) // 34)
    for k in range(n_gh):
        _ghost(c, DX + 30, ty + 76 + k * 34, dw - 60 - (50 if k % 3 == 2 else 0), DEEP, .22)
    if doc.get("sub"):
        c.text(DX + 20, ty + H - sub_h - 4, dw - 40, doc["sub"], "ds", TEAL, "center", (DX, ty, dw, H))
    for k, n in enumerate(items):
        ry = ty + bar + 12 + k * pitch
        used = bool(n.get("emph"))
        if used:
            c.rect(X0 + 12, ry - 6, ww - 24, pitch - 4, fill=ABYSS, stroke=GOLD, sw=5, rx=14)
        l1 = c.lines(n["text"], iw, 34) * 44.2
        c.text(X0 + 34, ry + 4, iw, n["text"], "dn", GOLD if used else LIGHT, "left", (X0, ty, ww, H))
        c.text(X0 + 34, ry + 4 + l1 + 2, iw, n["sub"], "ds", CREAM, "left", (X0, ty, ww, H))
        if used:
            my = ry - 6 + (pitch - 4) / 2
            c.line(X0 + ww - 12, my, DX - 28, my, GOLD, 7)
            c.arrow(DX - 60, my, DX - 6, my, GOLD, 7, 20)
    return ty + H


def hub(c: Canvas, spec: dict, y0: float) -> float:
    """共通介面接外部服務（2026-10-28）：heads = [中間共通介面的標籤, 上方被叉掉的虛線框說明]；nodes[0] = {text, sub?}（Claude Code）；
    outcomes = 2～4 個外部服務 [{text, sub?}]。Claude Code 經一條金色共通介面接到所有服務，不必各接一條客製的線。"""
    hub_lab, no_lab = spec["heads"][:2]
    me, svcs = spec["nodes"][0], spec["outcomes"]
    if not 2 <= len(svcs) <= 4:
        raise ValueError("hub 的 outcomes 要 2～4 個外部服務")
    nh = c.lines(no_lab, X1 - X0 - 150, 34) * 44.2 + 40
    sw_, sh, sg = 330, 88, 16
    labh = c.lines(hub_lab, 330, 28) * 39.2 + 12
    _fit(nh + 40 + max(len(svcs) * sh + (len(svcs) - 1) * sg, 260) + labh, BOTTOM - y0, "hub")
    sh = min(130.0, sh + (BOTTOM - y0 - nh - 40 - labh - max(len(svcs) * sh + (len(svcs) - 1) * sg, 260)) / len(svcs))
    area = len(svcs) * sh + (len(svcs) - 1) * sg
    c.rect(X0, y0, X1 - X0, nh, fill="none", stroke=TEAL, sw=3, dash="10 8", rx=16)
    c.text(X0 + 30, y0 + 20, X1 - X0 - 150, no_lab, "dt", TEAL, "left", (X0, y0, X1 - X0, nh))
    c.circle(X1 - 52, y0 + nh / 2, 30, fill=CREAM, stroke=TEAL, sw=4)
    _cross2(c, X1 - 52, y0 + nh / 2, 11, TEAL, 6)
    top = y0 + nh + 40 + labh
    H = max(area, 260)
    mid = top + H / 2
    bx = X0 + 330                                           # 共通介面的金色直條
    c.text(bx - 130, top - labh, 330, hub_lab, "dl", TEAL, "center")
    c.textbox(X0, mid - 90, 250, me["text"], me.get("sub"), h=180, align="center", pad=14)
    c.arrow(X0 + 258, mid, bx - 6, mid, GOLD, 9, 22)
    c.rect(bx, top, 70, H, fill=GOLD, rx=20)
    ty0 = top + (H - area) / 2
    for k, s in enumerate(svcs):
        sy = ty0 + k * (sh + sg)
        c.arrow(bx + 76, sy + sh / 2, X1 - sw_ - 8, sy + sh / 2, TEAL, 5, 16)
        c.textbox(X1 - sw_, sy, sw_, s["text"], s.get("sub"), h=sh, pad=18)
    return top + H


def pinned(c: Canvas, spec: dict, y0: float) -> float:
    """每場對話開頭都釘著同一份（2026-10-28）：heads = 3 個對話視窗的標題；nodes[0] = {text}（被釘在最上面的金色那行）；outcomes[0] = {text}（底下一句說明，選用）。
    三個視窗的內容各不相同（灰條），只有最上面那一行一模一樣。"""
    titles, pin = spec["heads"], spec["nodes"][0]
    if len(titles) != 3:
        raise ValueError(f"pinned 的 heads 要剛好 3 個視窗標題，現在是 {len(titles)}")
    note = spec["outcomes"][0]["text"] if spec.get("outcomes") else None
    wd, gap, bar = 280, 40, 60
    noteh = (c.lines(note, X1 - X0, 34) * 44.2 + 24) if note else 0
    H = min(470.0, BOTTOM - y0 - noteh - 10)
    _fit(bar + 250 + noteh, BOTTOM - y0, "pinned")
    pats = [[220, 150, 200, 90, 180, 130], [160, 230, 110, 200, 140, 210], [200, 120, 230, 170, 100, 190]]
    for k, ttl in enumerate(titles):
        x = X0 + k * (wd + gap)
        _win(c, x, y0, wd, H, ttl)
        c.rect(x + 16, y0 + bar + 14, wd - 32, 70, fill=GOLD, rx=12)
        c.text(x + 16, y0 + bar + 14 + 13, wd - 32, pin["text"], "dn", DEEP, "center", (x, y0, wd, H))
        for j, lw in enumerate(pats[k]):
            yy = y0 + bar + 112 + j * 44
            if yy + 12 < y0 + H - 14:
                _ghost(c, x + 26, yy, lw)
    if note:
        c.text(X0, y0 + H + 18, X1 - X0, note, "dn", DEEP, "center")
    return y0 + H + 18 + (noteh - 24 if note else -18)


def compact(c: Canvas, spec: dict, y0: float) -> float:
    """快滿的對話壓成摘要（2026-10-28）：heads = [左窗標題, 右窗標題]；nodes = [{text（箭頭上的標籤）}, {text（摘要裡保留的一項）}, {text（摘要裡保留的另一項）}]；
    outcomes[0] = {text（底下虛線框的提醒）}。左窗很多行（保留的亮色、其餘暗色），右窗只剩兩個框和一個游標。"""
    h_l, h_r = spec["heads"][:2]
    arrow_lab, k1, k2 = spec["nodes"][:3]
    foot = spec["outcomes"][0]["text"]
    ww, bar = 330, 60
    fh = c.lines(foot, X1 - X0 - 44, 28) * 39.2 + 36
    avail = BOTTOM - y0 - fh - 26
    rows = 7 if avail >= 60 + 16 + 7 * 40 + 8 else 6
    pitch = min(44.0, (avail - bar - 24) / rows)
    H = bar + 16 + rows * pitch + 8
    _fit(H + 26 + fh, BOTTOM - y0, "compact")
    RX = X1 - ww
    _win(c, X0, y0, ww, H, h_l)
    keep = {1, 4} if rows == 6 else {1, 3, 5}
    lens = [250, 190, 230, 170, 250, 150, 220]
    for j in range(rows):
        _ghost(c, X0 + 28, y0 + bar + 22 + j * pitch, lens[j], LIGHT if j in keep else CREAM, .85 if j in keep else .28)
    _win(c, RX, y0, ww, H, h_r)
    bh = 72
    by = y0 + bar + 18
    for k, n in enumerate((k1, k2)):
        c.textbox(RX + 18, by + k * (bh + 16), ww - 36, n["text"], None, fill=ABYSS, stroke=LIGHT, h=bh, align="center", pad=8)
    cy = by + 2 * (bh + 16) + 6
    if cy + 36 < y0 + H - 6:
        c.rect(RX + 30, cy, 24, 36, fill=GOLD, rx=4)
    ax0, ax1 = X0 + ww + 20, RX - 20
    my = y0 + H / 2
    c.arrow(ax0, my, ax1, my, GOLD, 8, 22)
    lw_ = ax1 - ax0
    c.text(ax0, my - 14 - c.lines(arrow_lab["text"], lw_, 28) * 39.2, lw_, arrow_lab["text"], "dl", TEAL, "center")
    fy = y0 + H + 26
    c.rect(X0, fy, X1 - X0, fh, fill="none", stroke=TEAL, sw=3, dash="10 8", rx=16)
    c.text(X0 + 22, fy + 18, X1 - X0 - 44, foot, "ds", TEAL, "left", (X0, fy, X1 - X0, fh))
    return fy + fh


def combo(c: Canvas, spec: dict, y0: float) -> float:
    """兩個機制自動組合的兩個例子（2026-10-29）：heads = [上標, 下標]；
    上：nodes = [{text（被收進去的框）}, {text（右邊視窗標題）}, {text（箭頭上的標籤）}]，左邊一個框、金色箭頭指向右邊視窗，視窗裡也有一個同名的金邊框；
    下：outcomes = [{text, sub?（來源一）}, {text, sub?（來源二）}, {text, sub?（金色的那一份）}]，兩個來源各一條線，匯到同一個金色方塊。"""
    h1, h2 = spec["heads"][:2]
    if len(spec["nodes"]) < 3 or len(spec["outcomes"]) < 3:
        raise ValueError("combo 的 nodes 與 outcomes 都要有 3 項")
    box, win_t, lab = spec["nodes"][:3]
    s1, s2, gold = spec["outcomes"][:3]
    bw, ww, hd = 350, 430, 44
    wh, sh, gap = 176, 116, 18
    gh = 2 * sh + gap
    total = hd + wh + 36 + hd + gh
    _fit(total, BOTTOM - y0, "combo")
    RX = X1 - ww
    c.text(X0, y0, X1 - X0, h1, "ds", TEAL, "left")
    ry = y0 + hd
    c.textbox(X0, ry + (wh - 76) / 2, bw, box["text"], None, fill=DEEP, h=76, align="center", pad=10)
    _win(c, RX, ry, ww, wh, win_t["text"])
    c.textbox(RX + 24, ry + 76, ww - 48, box["text"], None, fill=ABYSS, stroke=GOLD, h=wh - 76 - 22, align="center", pad=8)
    ax0, ax1 = X0 + bw + 16, RX - 16
    my = ry + wh / 2
    c.arrow(ax0, my, ax1, my, GOLD, 8, 22)
    c.text(ax0 - 10, my - 14 - c.lines(lab["text"], ax1 - ax0 + 20, 28) * 39.2, ax1 - ax0 + 20, lab["text"], "dl", TEAL, "center")
    y2 = ry + wh + 36
    c.text(X0, y2, X1 - X0, h2, "ds", TEAL, "left")
    sy = y2 + hd
    for k, n in enumerate((s1, s2)):
        c.textbox(X0, sy + k * (sh + gap), bw, n["text"], n.get("sub"), fill=DEEP, h=sh, align="left", pad=12)
    c.rect(RX, sy, ww, gh, fill=GOLD, rx=18)
    c.textbox(RX, sy, ww, gold["text"], gold.get("sub"), fill=GOLD, tcolor=DEEP, scolor=DEEP, h=gh, align="center", pad=14)
    for k, f in enumerate((.3, .7)):
        c.arrow(X0 + bw, sy + k * (sh + gap) + sh / 2, RX - 14, sy + gh * f, TEAL, 6, 20)
    return sy + gh


def sidecar(c: Canvas, spec: dict, y0: float) -> float:
    """另開一扇窗做雜事，只有摘要回來（2026-10-28）：heads = [主視窗標題, 側視窗標題]；nodes = [{text（主視窗：派出任務那一行）}, {text（主視窗：收到摘要那一行）}]；
    outcomes = [{text（側視窗裡的標籤：中間做了很多事）}, {text（回傳箭頭的標籤）}]。側視窗滿是灰條，主視窗只多一行。"""
    h_m, h_s = spec["heads"][:2]
    send, got = spec["nodes"][:2]
    busy, back = spec["outcomes"][:2]
    ww, bar = 360, 60
    H = bar + 24 + 7 * 52 + 10
    _fit(H, BOTTOM - y0, "sidecar")
    RX = X1 - ww
    _win(c, X0, y0, ww, H, h_m)
    iw = ww - 90
    y1, y2 = y0 + bar + 34, y0 + H - 90
    for j, (yy, row, tone) in enumerate(((y1, send, "tool"), (y2, got, "ok"))):
        c.circle(X0 + 40, yy + 22, 11, fill=LIGHT) if tone == "tool" else _tick(c, X0 + 42, yy + 22)
        c.text(X0 + 74, yy, iw, row["text"], "dn", CREAM, "left", (X0, y0, ww, H))
    for j, lw in enumerate((230, 170, 250, 200)):
        _ghost(c, X0 + 74, y1 + 70 + j * 30 + (0 if j < 2 else 40), lw)
    _win(c, RX, y0, ww, H, h_s)
    c.text(RX + 24, y0 + bar + 16, ww - 48, busy["text"], "dt", LIGHT, "left", (RX, y0, ww, H))
    ly = y0 + bar + 16 + c.lines(busy["text"], ww - 48, 34) * 44.2 + 14
    j = 0
    while ly + 12 < y0 + H - 16:
        _ghost(c, RX + 28, ly, [300, 220, 290, 180, 310, 250][j % 6], CREAM, .3)
        ly += 34
        j += 1
    ax0, ax1 = X0 + ww + 20, RX - 20
    c.arrow(ax0, y1 + 22, ax1, y1 + 22, TEAL, 6, 18)
    c.arrow(ax1, y2 + 22, ax0, y2 + 22, GOLD, 9, 24)
    lw_ = ax1 - ax0 + 30
    c.text(ax0 - 15, y2 + 22 - 12 - c.lines(back["text"], lw_, 28) * 39.2, lw_, back["text"], "dl", DEEP, "center")
    return y0 + H


# ------------------------------------------------------------------ 2026-10-31（Cerebras RAG 第 1 則）：waist／schema／branch／gates
WAIST_CELLS = 5          # 窄帶永遠畫五格（系列哲學：窄到一眼數得完）
WAIST_GOLD = 2           # 金色給中間那一格，與封面的小沙漏一致


def _waist_bar(c: Canvas, cx: float, y: float, bw: float = 460, h: float = 72) -> None:
    """一條只有五格的深海色窄帶，第三格金色。"""
    x0, cw = cx - bw / 2, bw / WAIST_CELLS
    c.rect(x0, y, bw, h, fill=DEEP, rx=10)
    for i in range(WAIST_CELLS):
        on = i == WAIST_GOLD
        c.rect(x0 + i * cw + 7, y + 14, cw - 14, h - 28, fill=GOLD if on else CREAM, rx=4,
               op=None if on else .24)


def waist(c: Canvas, spec: dict, y0: float) -> float:
    """沙漏：上段的異質來源各一個框，收斂到中間一條只有五格的窄帶，再重新展開成下段幾條路。
    heads = [上段標籤, 窄帶標籤, 下段標籤]；nodes = 上段的來源 2～5 個 [{text}]；outcomes = 下段展開的東西 2～5 個 [{text}]。純示意。"""
    hu, hw, hd = spec["heads"]
    ups, dns = spec["nodes"], spec["outcomes"]
    if not (2 <= len(ups) <= 5 and 2 <= len(dns) <= 5):
        raise ValueError("waist 的 nodes 與 outcomes 各要 2～5 個")
    w = X1 - X0
    cx = (X0 + X1) / 2

    def row(ns):
        cw = (w - (len(ns) - 1) * 16) / len(ns)
        return cw, 20 + max(c.lines(n["text"], cw - 24, 28) for n in ns) * 39.2
    ucw, uh = row(ups)
    dcw, dh = row(dns)
    lab, bar, conv = 46, 72, 70
    wlab = c.lines(hw, w, 28) * 39.2 + 10          # 窄帶的標籤：整幅居中放在帶子下面（放在帶子旁邊會塞不下而溢出）
    total = lab + uh + conv + bar + wlab + conv + lab + dh
    _fit(total, BOTTOM - y0, "waist")
    conv += min((BOTTOM - y0 - total) / 2, 30)
    y = y0
    c.text(X0, y, w, hu, "dl", TEAL, "left")
    y += lab
    for i, n in enumerate(ups):                    # 上段：還沒被整理的東西，只有細外框
        x = X0 + i * (ucw + 16)
        c.rect(x, y, ucw, uh, fill="none", stroke=MID, sw=3, rx=10)
        c.text(x + 12, y + 10, ucw - 24, n["text"], "ds", DEEP, "center", (x, y, ucw, uh))
        c.line(x + ucw / 2, y + uh + 4, cx, y + uh + conv - 4, MID, 2, op=.6)
    y += uh + conv
    _waist_bar(c, cx, y)
    y += bar
    c.text(X0, y + 5, w, hw, "ds", DEEP, "center")
    y += wlab
    for i, n in enumerate(dns):                    # 下段：重新展開，淺藍綠的細線與小圓點
        x = X0 + i * (dcw + 16)
        c.line(cx, y + 4, x + dcw / 2, y + conv + lab - 4, LIGHT, 2, op=.85)
        c.circle(x + dcw / 2, y + conv + lab - 4, 7, fill=LIGHT)
    y += conv
    c.text(X0, y, w, hd, "dl", TEAL, "left")
    y += lab
    for i, n in enumerate(dns):
        x = X0 + i * (dcw + 16)
        c.rect(x, y, dcw, dh, fill=LIGHT, rx=10, op=.20)
        c.text(x + 12, y + 10, dcw - 24, n["text"], "ds", DEEP, "center", (x, y, dcw, dh))
    return y + dh


def schema(c: Canvas, spec: dict, y0: float) -> float:
    """一張只有幾個欄位的表：表頭一列深色格子（emph 的那一格金色），每格下面一句「這一欄存什麼」。
    heads = [表名]；nodes = 欄位 3～5 個 [{text, sub, emph?}]；選用 outcomes[0] = {text}（底下一條金色橫框）。"""
    cols = spec["nodes"]
    if not 3 <= len(cols) <= 5:
        raise ValueError("schema 的 nodes 要 3～5 個欄位")
    if sum(1 for n in cols if n.get("emph")) > 1:
        raise ValueError("schema 的 emph 只能有一個（金色只給一個元素）")
    w = X1 - X0
    g = 10
    cw = (w - (len(cols) - 1) * g) / len(cols)
    iw = cw - 10                                   # 欄位名是拉丁字，欄窄，留白要小一點才不會溢出
    lab, hh = 46, 58
    dh = 18 + max(c.lines(n["sub"], iw, 28) for n in cols) * 39.2
    out = spec.get("outcomes", [])
    oh = (20 + c.lines(out[0]["text"], w - 44, 34) * 44.2) if out else 0
    gap = 46 if out else 0
    total = lab + hh + 8 + dh + gap + oh
    _fit(total, BOTTOM - y0, "schema")
    extra = min(BOTTOM - y0 - total, 60)
    dh += extra * .5
    y = y0
    c.text(X0, y, w, spec["heads"][0], "dl", TEAL, "left")
    y += lab
    for i, n in enumerate(cols):
        x = X0 + i * (cw + g)
        on = n.get("emph")
        c.rect(x, y, cw, hh, fill=GOLD if on else DEEP, rx=8)
        c.text(x + 5, y + (hh - 39.2) / 2, iw, n["text"], "ds", DEEP if on else CREAM, "center", (x, y, cw, hh))
        c.rect(x, y + hh + 8, cw, dh, fill="none", stroke=MID, sw=3, rx=8)
        c.text(x + 5, y + hh + 8 + 9, iw, n["sub"], "ds", DEEP, "center", (x, y + hh + 8, cw, dh))
    y += hh + 8 + dh
    if out:
        y += gap
        c.rect(X0, y, w, oh, fill=GOLD, op=.30, stroke=GOLD, sw=4, rx=16)
        c.text(X0 + 22, y + (oh - c.lines(out[0]["text"], w - 44, 34) * 44.2) / 2, w - 44,
               out[0]["text"], "dn", DEEP, "left", (X0, y, w, oh))
        y += oh
    return y


def branch(c: Canvas, spec: dict, y0: float) -> float:
    """形式統一但語意分裂：窄帶右邊硬接上幾個來源專屬欄位，它們各拉一條線下來，下游就得針對來源寫分支。
    heads = [上段標籤, 下段標籤]；nodes = [{text, sub?}（上段說明）, {text, sub?}（下游的檢索邏輯）]；outcomes = 額外欄位 2～3 個 [{text}]。純示意。"""
    hu, hd = spec["heads"]
    top, low = spec["nodes"]
    adds = spec["outcomes"]
    if not 2 <= len(adds) <= 3:
        raise ValueError("branch 的 outcomes 要 2～3 個額外欄位")
    w = X1 - X0
    bw, aw = 420, 400                              # 左邊的窄帶、右邊的額外欄位欄寬
    ax = X1 - aw
    ah, agap = 58, 12                              # 框要比字高一截，文字框外緣四角才不會落在虛線框線上（對比度檢查會擋）
    stack = len(adds) * ah + (len(adds) - 1) * agap
    band = max(stack, 72)
    th = c.lines(top["text"], w, 28) * 39.2
    lh = 20 + _th(c, low, w - 44)
    lab, arr = 46, 86
    total = lab + band + 8 + th + arr + lab + lh
    _fit(total, BOTTOM - y0, "branch")
    arr += min(BOTTOM - y0 - total, 40)
    y = y0
    c.text(X0, y, w, hu, "dl", TEAL, "left")
    y += lab
    _waist_bar(c, X0 + bw / 2, y + (band - 72) / 2, bw=bw)
    px = X0 + bw + 36                              # 窄帶與額外欄位之間一個「＋」
    c.line(px - 14, y + band / 2, px + 14, y + band / 2, DEEP, 5)
    c.line(px, y + band / 2 - 14, px, y + band / 2 + 14, DEEP, 5)
    ay = y + (band - stack) / 2
    xs = []
    for i, n in enumerate(adds):                   # 遷就來源硬加上去的欄位：虛線框
        yy = ay + i * (ah + agap)
        c.rect(ax, yy, aw, ah, fill="none", stroke=DEEP, sw=3, rx=8, dash="9 7")
        c.text(ax + 12, yy + (ah - 39.2) / 2, aw - 24, n["text"], "ds", DEEP, "center", (ax, yy, aw, ah))
        xs.append(ax + aw * (i + 1) / (len(adds) + 1))
    y += band + 8
    c.text(X0, y, w, top["text"], "ds", DEEP, "left")
    y += th
    for x in xs:                                   # 每個額外欄位都往下長出一條分支
        c.arrow(x, y + 6, X0 + w / 2 + (x - (ax + aw / 2)) * .25, y + arr + lab - 6, DEEP, 4, 14)
    _cross(c, X1 - 30, y + arr / 2, 15, DEEP, 5)
    y += arr
    c.text(X0, y, w, hd, "dl", TEAL, "left")
    y += lab
    c.rect(X0, y, w, lh, fill=DEEP, rx=16)
    ty = y + (lh - _th(c, low, w - 44)) / 2
    c.text(X0 + 22, ty, w - 44, low["text"], "dn", CREAM, "left", (X0, y, w, lh))
    if low.get("sub"):
        c.text(X0 + 22, ty + c.lines(low["text"], w - 44, 34) * 44.2 + 6, w - 44, low["sub"], "ds", LIGHT, "left", (X0, y, w, lh))
    return y + lh


def gates(c: Canvas, spec: dict, y0: float) -> float:
    """幾道門檻排成一排：一條金色的路一路通過（每道打勾），另一條在第一道就被叉掉擋下。
    heads = [通過那一條的標籤, 被擋那一條的標籤]；nodes = 門檻 2～4 個 [{text, sub?}]；outcomes = [{text}（通過之後）, {text}（沒過的下場）]。純示意。"""
    hp, hs = spec["heads"]
    gs = spec["nodes"]
    if not 2 <= len(gs) <= 4:
        raise ValueError("gates 的 nodes 要 2～4 道門檻")
    if len(spec["outcomes"]) != 2:
        raise ValueError("gates 的 outcomes 要 2 個（通過之後、沒過的下場）")
    ok, no = spec["outcomes"]
    lw = 220                                       # 左邊兩條路的標籤寬
    x_first, x_last = X0 + 320, X1 - 120
    xs = [x_first + i * (x_last - x_first) / max(len(gs) - 1, 1) for i in range(len(gs))]
    gw = min(240, (xs[1] - xs[0]) - 12 if len(gs) > 1 else 240)      # 每道門檻的標籤寬（相鄰兩道不重疊）
    nh = max(c.lines(n["text"], gw, 28) for n in gs) * 39.2 + 12
    sh = max((c.lines(n["sub"], gw, 28) * 39.2 for n in gs if n.get("sub")), default=0)
    rw = (X1 - X0 - 40) / 2                        # 兩條路的下場：柱子下面一列，左右各一半（柱子之間放字會壓到柱子）
    rh = max(c.lines(ok["text"], rw, 28), c.lines(no["text"], rw, 28)) * 39.2
    gh = 186
    total = nh + gh + 14 + rh + (sh + 16 if sh else 0)
    _fit(total, BOTTOM - y0, "gates")
    gh += min(BOTTOM - y0 - total, 50)
    y = y0
    for i, n in enumerate(gs):
        c.text(xs[i] - gw / 2, y, gw, n["text"], "ds", DEEP, "center")
    gy = y + nh
    ya, yb = gy + gh * .34, gy + gh * .78
    for x in xs:                                   # 門檻本身：一根深海色柱子
        c.rect(x - 9, gy, 18, gh, fill=DEEP, rx=6)
    th = c.lines(hp, lw, 28) * 39.2
    c.text(X0, ya - th / 2, lw, hp, "ds", DEEP, "left")
    th = c.lines(hs, lw, 28) * 39.2
    c.text(X0, yb - th / 2, lw, hs, "ds", TEAL, "left")
    c.arrow(X0 + lw + 20, ya, X1 - 6, ya, GOLD, 7, 20)        # 一路通過
    for x in xs:
        _tick(c, x, ya, GOLD, 7)
    c.arrow(X0 + lw + 20, yb, xs[0] - 36, yb, TEAL, 5, 18)    # 第一道就被擋下
    _cross(c, xs[0], yb, 16, TEAL, 6)
    y = gy + gh + 14
    c.text(X0, y, rw, no["text"], "ds", TEAL, "left")
    c.text(X1 - rw, y, rw, ok["text"], "ds", DEEP, "right")
    y += rh
    if sh:                                         # 每道門檻為什麼要設：放在最下面，一欄一段
        for i, n in enumerate(gs):
            if n.get("sub"):
                c.text(xs[i] - gw / 2, y + 16, gw, n["sub"], "ds", TEAL, "center")
        y += sh + 16
    return y


def route(c: Canvas, spec: dict, y0: float) -> float:
    """路線圖：一條金色的路由上往下走，路上幾站，每站一個編號圓與一句「這一站要回答什麼」；
    這一則不走的那一段接在最後一站下面，畫成虛線與空心的終點。
    heads = [最上面的標籤]（選用 heads[1] = 虛線那一段的說明）；nodes = 站 2～4 個 [{text, sub?}]。"""
    stops = spec["nodes"]
    if not 2 <= len(stops) <= 4:
        raise ValueError("route 的 nodes 要 2～4 站")
    heads = spec.get("heads", [])
    w = X1 - X0
    sx, r = X0 + 54, 38                            # 路（也是編號圓）的 x、圓的半徑
    tx = X0 + 142
    tw = X1 - tx
    lab = 56 if heads else 0
    pad = r - 22                                   # 編號圓比文字高，上緣會超出文字頂端，先留這段才不會壓到上面
    hs = [c.lines(n["text"], tw, 34) * 44.2 + (c.lines(n["sub"], tw, 28) * 39.2 + 8 if n.get("sub") else 0) for n in stops]
    th = c.lines(heads[1], tw, 28) * 39.2 if len(heads) > 1 else 0
    tail = th + 60 if th else 0                    # 虛線尾巴：ey 最多 y+70，字置中在 ey，所以 th/2 之外留 60 就夠
    gap = 44
    total = lab + pad + sum(hs) + gap * (len(stops) - 1) + tail
    _fit(total, BOTTOM - y0, "route")
    gap += min((BOTTOM - y0 - total) / max(len(stops) - 1 + (1 if tail else 0), 1), 90)
    y = y0
    if heads:
        c.text(X0, y, w, heads[0], "dl", TEAL, "left")
        y += lab
    y += pad
    cys = [y + 22 + sum(hs[:i]) + gap * i for i in range(len(stops))]
    c.line(sx, cys[0], sx, cys[-1], GOLD, 10)      # 走完的那一段：一條金色的路
    for i, n in enumerate(stops):
        cy, top = cys[i], cys[i] - 22
        c.circle(sx, cy, r, fill=DEEP)
        c.text(sx - 26, cy - 20, 52, str(i + 1), "dl", CREAM, "center", (sx - 26, cy - 26, 52, 52))
        c.text(tx, top, tw, n["text"], "dn", DEEP, "left")
        if n.get("sub"):
            c.text(tx, top + c.lines(n["text"], tw, 34) * 44.2 + 8, tw, n["sub"], "ds", TEAL, "left")
    y += sum(hs) + gap * (len(stops) - 1)
    if tail:                                       # 這一則不走的那一段：虛線接到一個空心的終點
        ey = y + min(gap, 70)
        c.line(sx, cys[-1] + r + 8, sx, ey - 18, TEAL, 5, dash="12 10")
        c.circle(sx, ey, 14, fill=CREAM, stroke=TEAL, sw=4)
        c.text(tx, ey - th / 2, tw, heads[1], "ds", TEAL, "left")
        y = ey + max(th / 2, 22)
    return y


# ------------------------------------------------------------------ depend（B 要等 A 的結果：平行做不到，固定兩步可包成一個工具）
def depend(c: Canvas, spec: dict, y0: float) -> float:
    """序列依賴（2026-11-01，Cerebras 第 3 則）：heads = [上段標籤, 下段標籤]；nodes = [{text}（工具 A）, {text}（工具 B，要用 A 的結果）]；
    outcomes = [{text}（A 查到的結果）, {text}（斷掉的虛線旁的字）, {text}（金色框底下的說明）]。
    上段：A、B 從同一條起跑線同時出發，A 的結果用虛線送不到 B（打叉）；下段：金色框把 A → B 包成一個工具。純示意。"""
    ha, hb = spec["heads"][:2]
    a, b = spec["nodes"][:2]
    if len(spec.get("outcomes", [])) < 3:
        raise ValueError("depend 的 outcomes 要 3 項：A 的結果、斷線旁的字、金色框的說明")
    res, brk, wrap = spec["outcomes"][:3]
    w = X1 - X0
    bw, bh, lg = 380, 80, 56
    rx0 = X0 + 40 + bw + 90
    rw = X1 - rx0
    wraph = c.lines(wrap["text"], w - 60, 28) * 39.2
    top = 44 + 2 * bh + lg
    bot = 56 + 30 + bh + 16 + wraph + 26
    total = top + 40 + bot
    _fit(total, BOTTOM - y0, "depend")
    ex = min(36.0, (BOTTOM - y0 - total) / 3)
    lg += ex
    # 上段：同一條起跑線
    c.text(X0, y0, w, ha, "dl", TEAL)
    ly = y0 + 44
    c.rect(X0, ly - 8, 12, 2 * bh + lg + 16, fill=TEAL, rx=6)
    ya, yb = ly, ly + bh + lg
    for yy, n in ((ya, a), (yb, b)):
        c.line(X0 + 12, yy + bh / 2, X0 + 40, yy + bh / 2, TEAL, 5)
        c.textbox(X0 + 40, yy, bw, n["text"], None, h=bh, align="center", pad=10)
    c.arrow(X0 + 40 + bw + 10, ya + bh / 2, rx0 - 10, ya + bh / 2, TEAL, 5, 16)
    c.textbox(rx0, ya, rw, res["text"], None, fill=CREAM, tcolor=DEEP, stroke=DEEP, h=bh, align="center", pad=10)
    sx, sy = rx0 + rw / 2, ya + bh + 6
    tx, ty = X0 + 40 + bw + 8, yb + bh / 2
    c.line(sx, sy, sx, ty, TEAL, 4, dash="10 8")
    c.line(sx, ty, tx + 14, ty, TEAL, 4, dash="10 8")
    mx = (sx + tx) / 2 + 20
    c.circle(mx, ty, 22, fill=CREAM, stroke=TEAL, sw=4)
    _cross2(c, mx, ty, 9, TEAL, 5)
    c.text(tx + 30, ty - 72, sx - tx - 50, brk["text"], "ds", TEAL, "center")   # 斷線上方，避開叉
    # 下段：金色框包成一個工具
    y = yb + bh + 40
    c.text(X0, y, w, hb, "dl", TEAL)
    gy = y + 56
    gh = 30 + bh + 16 + wraph + 26 - 30
    c.rect(X0, gy, w, gh, fill=GOLD, stroke=GOLD, sw=4, rx=20, op=.30)
    c.rect(X0, gy, w, gh, fill="none", stroke=GOLD, sw=5, rx=20)
    iy = gy + 20
    iw = (w - 60 - 80) / 2
    c.textbox(X0 + 30, iy, iw, a["text"], None, h=bh, align="center", pad=10)
    c.arrow(X0 + 30 + iw + 10, iy + bh / 2, X0 + 30 + iw + 70, iy + bh / 2, DEEP, 5, 16)
    c.textbox(X0 + 30 + iw + 80, iy, iw, b["text"], None, h=bh, align="center", pad=10)
    c.text(X0 + 30, iy + bh + 16, w - 60, wrap["text"], "ds", DEEP, "left")
    return gy + gh


def pick(c: Canvas, spec: dict, y0: float) -> float:
    """勾選單 vs 寫一整段（2026-11-01，Cerebras 第 3 則「planner 只做分類」）：heads = [左標, 右標]；
    nodes = 左邊勾選單的選項 2～5 個 [{text, on?}]（on 的格子打勾）；outcomes[0] = {text}（底下金色橫框）。
    左邊是一張短短的勾選單，右邊同樣大的紙上寫滿一行行的字（灰條，示意「要從頭寫出一段文字」）。純示意。"""
    hl, hr = spec["heads"][:2]
    opts = spec["nodes"]
    if not 2 <= len(opts) <= 5:
        raise ValueError(f"pick 的 nodes（選項）要 2～5 個，現在是 {len(opts)}")
    if not spec.get("outcomes"):
        raise ValueError("pick 要有 outcomes[0]（底下金色橫框）")
    foot = spec["outcomes"][0]
    w, pw, gap = X1 - X0, 440, 40
    rx = X0 + pw + gap
    fh = c.lines(foot["text"], w - 44, 34) * 44.2 + 44
    rh = 66
    total = 56 + 40 + len(opts) * rh + 30 + fh
    _fit(total, BOTTOM - y0, "pick")
    rh += min((BOTTOM - y0 - total) / len(opts), 24)
    ph = 40 + len(opts) * rh
    c.text(X0, y0, pw, hl, "dl", TEAL)
    c.text(rx, y0, pw, hr, "dl", TEAL)
    y = y0 + 56
    c.rect(X0, y, pw, ph, fill="none", stroke=DEEP, sw=4, rx=18)
    for i, o in enumerate(opts):
        cy = y + 20 + i * rh + rh / 2
        c.rect(X0 + 30, cy - 18, 36, 36, fill=TEAL if o.get("on") else "none", stroke=TEAL, sw=4, rx=6)
        if o.get("on"):
            _tick(c, X0 + 48, cy, CREAM, 5)
        c.text(X0 + 86, cy - 23, pw - 110, o["text"], "dt", DEEP if o.get("on") else TEAL, "left", (X0, y, pw, ph))
    c.rect(rx, y, pw, ph, fill="none", stroke=DEEP, sw=4, rx=18)
    n = int((ph - 40) // 34)
    for i in range(n):
        lw = (pw - 60) * (0.55 if i == n - 1 else (0.92, 0.84, 0.97, 0.78)[i % 4])
        c.rect(rx + 30, y + 26 + i * 34, lw, 12, fill=DEEP, rx=6, op=.28)
    y += ph + 30
    c.textbox(X0, y, w, foot["text"], None, fill=GOLD, tcolor=DEEP, align="center", h=fh)
    return y + fh


def pile(c: Canvas, spec: dict, y0: float) -> float:
    """證據堆原樣交給最後一步（2026-11-01，Cerebras 第 3 則「推理放最後」）：heads = [左欄標籤, 金框上方標籤]；
    nodes = [{text, sub?}（左欄底下的說明）, {text, sub?}（金框：最後一步）]；outcomes = 證據卡片 2～5 張 [{text}]（每張的來源標籤）。
    左邊一疊證據卡（標籤加兩條灰條，示意原始內容），每張各一條箭頭匯進右邊同一個金框。純示意。"""
    hl, hr = spec["heads"][:2]
    note, gold = spec["nodes"][:2]
    cards = spec.get("outcomes", [])
    if not 2 <= len(cards) <= 5:
        raise ValueError(f"pile 的 outcomes（證據卡）要 2～5 張，現在是 {len(cards)}")
    lw, gx = 400, X0 + 400 + 120
    gw = X1 - gx
    ch, cg = 70, 18
    nh = c.lines(note["text"], lw, 34) * 44.2 + (c.lines(note["sub"], lw, 28) * 39.2 + 6 if note.get("sub") else 0)
    total = 56 + len(cards) * (ch + cg) - cg + 24 + nh
    _fit(total, BOTTOM - y0, "pile")
    ex = BOTTOM - y0 - total
    ch += min(ex * 0.5 / len(cards), 20)
    cg += min(ex * 0.3 / max(len(cards) - 1, 1), 24)
    c.text(X0, y0, lw, hl, "dl", TEAL)
    y = y0 + 56
    ys = []
    for k in cards:
        c.rect(X0, y, lw, ch, fill="none", stroke=DEEP, sw=3, rx=12)
        c.text(X0 + 22, y + (ch - 44) / 2, 170, k["text"], "dn", DEEP, "left", (X0, y, lw, ch))
        c.rect(X0 + 210, y + ch / 2 - 16, 160, 11, fill=DEEP, rx=5, op=.28)
        c.rect(X0 + 210, y + ch / 2 + 6, 110, 11, fill=DEEP, rx=5, op=.28)
        ys.append(y + ch / 2)
        y += ch + cg
    stack_bot = y - cg
    c.text(X0, stack_bot + 24, lw, note["text"], "dn", DEEP, "left")
    if note.get("sub"):
        c.text(X0, stack_bot + 24 + c.lines(note["text"], lw, 34) * 44.2 + 6, lw, note["sub"], "ds", TEAL, "left")
    mid = (y0 + 56 + stack_bot) / 2
    gh = c.lines(gold["text"], gw - 44, 34) * 44.2 + (c.lines(gold["sub"], gw - 44, 28) * 39.2 + 6 if gold.get("sub") else 0) + 60
    gy = mid - gh / 2
    c.text(gx, gy - 50, gw, hr, "dl", TEAL)
    for i, cy in enumerate(ys):
        ty = gy + 30 + (gh - 60) * (i + .5) / len(ys)
        c.arrow(X0 + lw + 8, cy, gx - 10, ty, TEAL, 4, 14)
    c.textbox(gx, gy, gw, gold["text"], gold.get("sub"), fill=GOLD, tcolor=DEEP, scolor=DEEP, h=gh)
    return max(stack_bot + 24 + nh, gy + gh)


def addlane(c: Canvas, spec: dict, y0: float) -> float:
    """多接一種資料要做多少（2026-11-01，Cerebras 第 3 則「多一種資料只要加一個工具」）：heads = [上段標籤, 下段標籤]；
    nodes = 上段每一路的格子 2～3 個 [{text}]（例：搜尋、推理、摘要；下段每一路只有第一格）；
    outcomes = [{text}（上段新增那一路的說明）, {text}（上段右邊的框）, {text}（下段新增那一路的說明）, {text}（下段右邊的框）]。
    兩段各三路：前兩路是現有的，第三路是新接的；上段新的一路整排虛線格子，下段新的一路只有一個金色格子。純示意。"""
    ht, hb = spec["heads"][:2]
    parts = spec["nodes"]
    if not 2 <= len(parts) <= 3:
        raise ValueError(f"addlane 的 nodes（每一路的格子）要 2～3 個，現在是 {len(parts)}")
    if len(spec.get("outcomes", [])) < 4:
        raise ValueError("addlane 的 outcomes 要 4 項：上段新的一路、上段右框、下段新的一路、下段右框")
    new_t, box_t, new_b, box_b = spec["outcomes"][:4]
    bw = 200
    bx = X1 - bw
    lane_w = bx - 50 - X0
    cg = 20
    cw = (lane_w - cg * (len(parts) - 1)) / len(parts)
    rh, rg = 52, 10          # 格子的 pad 要大於圓角（程式 B 取字框外緣四角的背景色算對比）
    nt = c.lines(new_t["text"], lane_w, 28) * 39.2
    sec = 46 + 3 * rh + 2 * rg
    nb = c.lines(new_b["text"], lane_w, 28) * 39.2
    total = sec + 6 + nt + 30 + sec + 6 + nb
    _fit(total, BOTTOM - y0, "addlane")
    ex = BOTTOM - y0 - total
    rh += min(ex * 0.5 / 6, 14)
    rg += min(ex * 0.2 / 4, 10)
    sec = 46 + 3 * rh + 2 * rg

    def lanes(y, full):
        c.text(X0, y, X1 - X0, ht if full else hb, "dl", TEAL)
        ry = y + 46
        cys = []
        for r in range(3):
            new = r == 2
            n = len(parts) if full else 1
            for k in range(n):
                x = X0 + k * (cw + cg)
                if new and not full:
                    fill, tc, st, da = GOLD, DEEP, None, None
                elif new:
                    fill, tc, st, da = "none", TEAL, TEAL, "10 8"
                else:
                    fill, tc, st, da = DEEP, CREAM, None, None
                c.cell(x, ry, cw, rh, parts[k]["text"], fill=fill, stroke=st, dash=da, color=tc)
                if k < n - 1:
                    c.line(x + cw + 3, ry + rh / 2, x + cw + cg - 3, ry + rh / 2, TEAL if new else DEEP, 4, dash="6 6" if new and full else None)
            end = X0 + n * cw + (n - 1) * cg
            cys.append((end, ry + rh / 2, new))
            ry += rh + rg
        top, bot = y + 46, ry - rg
        c.textbox(bx, top, bw, box_t["text"] if full else box_b["text"], None, fill=CREAM, tcolor=DEEP, stroke=DEEP, h=bot - top, align="center", pad=12)
        for end, cy, new in cys:
            c.arrow(end + 8, cy, bx - 10, cy, TEAL, 4, 14) if not (full and new) else c.line(end + 8, cy, bx - 10, cy, TEAL, 4, dash="6 6")
        return bot, cys

    bot, _ = lanes(y0, True)
    c.text(X0, bot + 6, lane_w, new_t["text"], "ds", TEAL, "left")
    y = bot + 6 + nt + 30 + min(ex * 0.3, 40)
    bot2, _ = lanes(y, False)
    c.text(X0, bot2 + 6, lane_w, new_b["text"], "ds", DEEP, "left")
    return bot2 + 6 + nb


# ------------------------------------------------------------------ 2026-11-03 新增（LLM-as-a-Verifier 第 1 則）：dist／snap／stack／target
def dist_ev(nodes) -> float:
    """dist 的期望值：第 k 根（從 1 起）的分數就是 k。"""
    return sum((k + 1) * n["p"] for k, n in enumerate(nodes))


def dist(c: Canvas, spec: dict, y0: float) -> float:
    """機率分佈直條：一個分數一根，高度＝模型給這個分數的機率（從 0 起、與機率成正比，class vbar 由程式 B 檢查）。
    nodes = 每個分數一根 [{text（分數，依序是 1、2、3…）, p（機率）}]（3～6 根，p 加總要是 1）；
    pick = "argmax"：機率最高的那根金色、其餘畫成虛線空框（被丟掉）；
           "ev"：全部實心，金色的針停在期望值（由程式算，標籤＝heads[1] + 兩位小數）；
    heads = [圖上方的標籤, （ev 時）針的標籤前綴]；選用 outcomes[0] = {text}（底下一條橫框）。純示意時圖註要標「假設的例子」。"""
    nodes = spec["nodes"]
    if not 3 <= len(nodes) <= 6:
        raise ValueError(f"dist 的 nodes（分數）要 3～6 根，現在是 {len(nodes)}")
    ps = [float(n["p"]) for n in nodes]
    if abs(sum(ps) - 1) > 0.011:
        raise ValueError(f"dist 的機率加總要是 1，現在是 {sum(ps):.3f}")
    if [n["text"] for n in nodes] != [str(k + 1) for k in range(len(nodes))]:
        raise ValueError("dist 的分數要依序是 1、2、3…（期望值的位置由這個算）")
    pick = spec.get("pick", "ev")
    if pick not in ("argmax", "ev"):
        raise ValueError("dist 的 pick 只能是 argmax 或 ev")
    heads = list(spec.get("heads", [])) + ["", ""]
    out = (spec.get("outcomes") or [None])[0]
    n = len(nodes)
    xa, xb = X0 + 90, X1 - 90
    step = (xb - xa) / (n - 1)
    bw = min(120, step * .6)
    xs = [xa + k * step for k in range(n)]
    oh = (c.lines(out["text"], X1 - X0 - 44, 34) * 44.2 + 44) if out else 0
    lab = 50 if heads[0] else 0
    top_room = 110 if pick == "ev" else 56          # 機率標籤（＋針的標籤）
    fixed = lab + top_room + 14 + 54 + (30 + oh if out else 0)
    H = min(440, BOTTOM - y0 - fixed)
    if H < 180:
        raise ValueError(f"示意圖（dist）放不下：直條只剩 {H:.0f}px 高；請縮短補充或底下橫框的字")
    if heads[0]:
        c.text(X0, y0, X1 - X0, heads[0], "dl", TEAL, "left")
    base = y0 + lab + top_room + H
    s = H / max(ps)
    imax = max(range(n), key=lambda k: ps[k])
    for k, (x, p) in enumerate(zip(xs, ps)):
        h = p * s
        gold = pick == "argmax" and k == imax
        if pick == "argmax" and not gold:
            c.svg.append(f'<rect class="bg vbar" x="{x - bw / 2:.1f}" y="{base - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="6" fill="none" '
                         f'stroke="{DEEP}" stroke-width="3" stroke-dasharray="10 8" data-p="{p}" data-s="{s}" data-base="{base}"/>')
        else:
            c.svg.append(f'<rect class="bg vbar" x="{x - bw / 2:.1f}" y="{base - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="6" '
                         f'fill="{GOLD if gold else MID}" data-p="{p}" data-s="{s}" data-base="{base}"/>')
        c.text(x - 80, base - h - 46, 160, f"{p:g}", "dl", DEEP, "center")
        c.text(x - 60, base + 14, 120, nodes[k]["text"], "dn", DEEP, "center")
    c.line(X0, base, X1, base, DEEP, 3)
    if pick == "ev":
        ev = dist_ev(nodes)
        nx = xa + (ev - 1) * step
        c.circle(nx, base, 0.01, cls="bg dpt", extra=f' data-v="{ev}" data-x0="{xa - step}" data-s="{step}"')
        c.rect(nx - 4, base - H - 40, 8, H + 54, fill=GOLD, rx=3)
        lw = 300
        lx = min(max(nx - lw / 2, X0), X1 - lw)
        c.text(lx, base - H - 98, lw, f"{heads[1]} {ev:.2f}".strip(), "dl", DEEP, "center")
    y = base + 14 + 54
    if out:
        y += 30
        c.textbox(X0, y, X1 - X0, out["text"], None, fill=DEEP, tcolor=CREAM, h=oh)
        y += oh
    return y


def snap(c: Canvas, spec: dict, y0: float) -> float:
    """刻度上的點（分數落在哪裡、會不會疊在一起）：一列一條刻度尺，點的位置與數值成正比（class dpt 由程式 B 檢查）。
    nodes = 每列 [{text（這一列是什麼）, sub?, lo（刻度起點，預設 1）, hi（刻度終點）, marks: [{v, text}]（1～3 個點）, tie?（點疊在一起時旁邊的金色小牌）}]（2～3 列）；
    同一列數值相同的點往上疊；點的顏色依序深海、金、中藍綠。純示意時圖註要標。"""
    rows = spec["nodes"]
    if not 2 <= len(rows) <= 3:
        raise ValueError(f"snap 的 nodes（刻度尺）要 2～3 列，現在是 {len(rows)}")
    cols = [DEEP, GOLD, MID]
    xa, xb = X0 + 40, X1 - 40
    hs = []
    for r in rows:
        if not 1 <= len(r["marks"]) <= 3:
            raise ValueError("snap 每列的 marks 要 1～3 個")
        lo, hi = r.get("lo", 1), r["hi"]
        if not all(lo <= m["v"] <= hi for m in r["marks"]):
            raise ValueError(f"snap 的點超出刻度範圍 {lo}～{hi}")
        stack = max(sum(1 for m2 in r["marks"] if abs(m2["v"] - m["v"]) < 1e-9) for m in r["marks"])
        hs.append(c.lines(r["text"], X1 - X0, 34) * 44.2 + (c.lines(r["sub"], X1 - X0, 28) * 39.2 + 4 if r.get("sub") else 0)
                  + 60 + 44 * (stack - 1) + 40 + 62)
    gap = 20
    total = sum(hs) + gap * (len(rows) - 1)
    _fit(total, BOTTOM - y0, "snap")
    gap += min((BOTTOM - y0 - total) / max(len(rows) - 1, 1), 70)
    y = y0
    for r, rh in zip(rows, hs):
        lo, hi = r.get("lo", 1), r["hi"]
        s = (xb - xa) / (hi - lo)
        c.text(X0, y, X1 - X0, r["text"], "dn", DEEP, "left")
        ty = y + c.lines(r["text"], X1 - X0, 34) * 44.2
        if r.get("sub"):
            c.text(X0, ty + 4, X1 - X0, r["sub"], "ds", TEAL, "left")
            ty += c.lines(r["sub"], X1 - X0, 28) * 39.2 + 4
        stack = max(sum(1 for m2 in r["marks"] if abs(m2["v"] - m["v"]) < 1e-9) for m in r["marks"])
        ly = ty + 60 + 44 * (stack - 1) + 40                       # 刻度線的 y
        c.line(xa, ly, xb, ly, DEEP, 4)
        every = 1 if hi - lo <= 10 else 5
        for v in range(int(lo), int(hi) + 1):
            x = xa + (v - lo) * s
            major = v in (lo, hi) or (v - lo) % every == 0 or (every > 1 and v % every == 0)
            c.line(x, ly, x, ly + (14 if major else 8), DEEP, 3)
            if major and (every == 1 or v % every == 0 or v in (lo, hi)):
                c.text(x - 40, ly + 18, 80, f"{v:g}", "ds", DEEP, "center")
        groups = {}
        for k, m in enumerate(r["marks"]):
            groups.setdefault(round(m["v"], 9), []).append((k, m))
        gl = sorted(groups.items())
        for gi, (v, ms) in enumerate(gl):
            x = xa + (v - lo) * s
            for j, (k, m) in enumerate(ms):
                c.circle(x, ly - 22 - 44 * j, 18, fill=cols[k % 3], cls="bg dpt", extra=f' data-v="{v}" data-x0="{xa - lo * s}" data-s="{s}"')
            lab = "、".join(m["text"] for _, m in ms)
            yt = ly - 22 - 44 * (len(ms) - 1) - 62
            w = min(400, sum(17 if ord(ch) < 128 else 29 for ch in lab) + 12)     # 字框只比字寬一點，相鄰兩個點的標籤才不會互相重疊
            if len(gl) == 1:
                lx, al = min(max(x - w / 2, X0), X1 - w), "center"
            elif gi == 0:
                lx, al = max(x + 8 - w, X0), "right"
            else:
                lx, al = min(x - 8, X1 - w), "left"
            c.text(lx, yt, w, lab, "ds", DEEP, al)
            if len(ms) > 1 and r.get("tie"):
                tw = len(r["tie"]) * 28 + 40
                tx = x - 40 - tw if x + 40 + tw > X1 else x + 40
                c.cell(tx, ly - 22 - 44 * (len(ms) - 1) / 2 - 26, tw, 52, r["tie"], fill=GOLD, color=DEEP)
        y += rh + gap
    return y - gap


def stack(c: Canvas, spec: dict, y0: float) -> float:
    """100 次的結果切成三段：一列一個方法，一條橫條依序是三種結果的次數（長度與次數成正比，class rbar 由程式 B 檢查）。
    heads = 三種結果的圖例（例：排對／平手／排錯）；nodes = 每列 [{text, sub?, parts: [a, b, c]}]（2～4 列，加總＝total）；選用 total（預設 100）。
    橫條下面一行寫出三個次數。"""
    heads = spec["heads"]
    rows = spec["nodes"]
    total = spec.get("total", 100)
    if len(heads) != 3:
        raise ValueError("stack 的 heads（圖例）要剛好 3 個")
    if not 2 <= len(rows) <= 4:
        raise ValueError(f"stack 的 nodes（方法）要 2～4 列，現在是 {len(rows)}")
    for r in rows:
        if len(r["parts"]) != 3 or sum(r["parts"]) != total:
            raise ValueError(f"stack 的 parts 要 3 個數、加總 {total}：{r['text']} 是 {r['parts']}")
    fills = [dict(fill=MID), dict(fill=CREAM, stroke=DEEP, dash="8 6"), dict(fill=DEEP)]
    xa, xb = X0, X1
    s = (xb - xa) / total
    bh = 46
    hs = [c.lines(r["text"], X1 - X0, 34) * 44.2 + (c.lines(r["sub"], X1 - X0, 28) * 39.2 + 4 if r.get("sub") else 0) + 10 + bh + 6 + 38 for r in rows]
    leg = 60
    gap = 24
    tot = leg + sum(hs) + gap * (len(rows) - 1)
    _fit(tot, BOTTOM - y0, "stack")
    gap += min((BOTTOM - y0 - tot) / max(len(rows) - 1, 1), 60)
    lx = X0
    for k, h in enumerate(heads):
        f = fills[k]
        c.rect(lx, y0 + 6, 36, 36, fill=f["fill"], stroke=f.get("stroke"), dash=f.get("dash"), rx=6)
        w = len(h) * 28 + 30
        c.text(lx + 48, y0 + 4, w, h, "ds", DEEP, "left")
        lx += 48 + w + 30
    y = y0 + leg
    for r, rh in zip(rows, hs):
        c.text(X0, y, X1 - X0, r["text"], "dn", DEEP, "left")
        by = y + c.lines(r["text"], X1 - X0, 34) * 44.2
        if r.get("sub"):
            c.text(X0, by + 4, X1 - X0, r["sub"], "ds", TEAL, "left")
            by += c.lines(r["sub"], X1 - X0, 28) * 39.2 + 4
        by += 10
        cum = 0
        for k, part in enumerate(r["parts"]):
            if part:
                f = fills[k]
                st = f' stroke="{f["stroke"]}" stroke-width="3" stroke-dasharray="{f["dash"]}"' if f.get("stroke") else ""
                c.svg.append(f'<rect class="bg rbar" x="{xa + cum * s:.1f}" y="{by:.1f}" width="{part * s:.1f}" height="{bh}" rx="0" fill="{f["fill"]}"{st} '
                             f'data-lo="{cum}" data-hi="{cum + part}" data-s="{s}" data-x0="{xa}"/>')
            cum += part
        c.text(X0, by + bh + 6, X1 - X0, "・".join(f"{h} {p}" for h, p in zip(heads, r["parts"])), "ds", DEEP, "left")
        y += rh + gap
    return y - gap


TARGET_SPREAD = [(.9, .3), (-.7, .8), (.2, -1.0), (-1.0, -.35), (.65, -.75), (-.25, .95), (1.0, .55), (-.55, -.9)]


def target(c: Canvas, spec: dict, y0: float) -> float:
    """打靶：兩個靶，落點的中心都偏離靶心同一個方向；左靶散得開、右靶擠成一團（變異小了，偏差還在）。
    heads = [左靶標籤, 右靶標籤]；nodes = [{text}（靶心代表什麼）, {text}（金色 ✕：落點平均代表什麼）]；選用 outcomes[0] = {text}（底下一條橫框）。
    落點是固定示意，圖註要標「示意」。"""
    hl, hr = spec["heads"][:2]
    bull, avg = spec["nodes"][:2]
    out = (spec.get("outcomes") or [None])[0]
    w = X1 - X0
    leg_h = [c.lines(n["text"], w - 70, 34) * 44.2 for n in (bull, avg)]
    oh = (c.lines(out["text"], w - 44, 34) * 44.2 + 44) if out else 0
    lab = 50
    fixed = lab + 30 + sum(leg_h) + 20 + (30 + oh if out else 0)
    R = min(200, (BOTTOM - y0 - fixed) / 2, (w - 60) / 4)
    if R < 110:
        raise ValueError(f"示意圖（target）放不下：靶只剩半徑 {R:.0f}px；請縮短補充或圖上的字")
    cy = y0 + lab + R
    for k, (cx, label, spread) in enumerate(((X0 + w / 4, hl, .55), (X0 + 3 * w / 4, hr, .17))):
        c.text(cx - w / 4, y0, w / 2, label, "dl", TEAL, "center")
        for f in (1, .66, .33):
            c.circle(cx, cy, R * f, fill="none", stroke=TEAL, sw=3)
        c.circle(cx, cy, 12, fill=DEEP)
        ox, oy = cx + .38 * R, cy - .3 * R
        for dx, dy in TARGET_SPREAD:
            c.circle(ox + dx * spread * R, oy + dy * spread * R, 11, fill=MID)
        c.line(ox - 16, oy - 16, ox + 16, oy + 16, GOLD, 8)
        c.line(ox - 16, oy + 16, ox + 16, oy - 16, GOLD, 8)
    y = cy + R + 30
    c.circle(X0 + 22, y + 22, 12, fill=DEEP)
    c.text(X0 + 70, y, w - 70, bull["text"], "dn", DEEP, "left")
    y += leg_h[0] + 20
    c.line(X0 + 8, y + 8, X0 + 36, y + 36, GOLD, 8)
    c.line(X0 + 8, y + 36, X0 + 36, y + 8, GOLD, 8)
    c.text(X0 + 70, y, w - 70, avg["text"], "dn", DEEP, "left")
    y += leg_h[1]
    if out:
        y += 30
        c.textbox(X0, y, w, out["text"], None, fill=DEEP, tcolor=CREAM, h=oh)
        y += oh
    return y


# ------------------------------------------------------------------ ring（環狀比較：只比相鄰的，每個節點恰好當一次起點、一次終點）
def ring(c: Canvas, spec: dict, y0: float) -> float:
    """2026-11-05 新增（LLM-as-a-Verifier 第 2 則：PPT 的 ring pass）。
    nodes = 3～8 個 [{text, emph?}]，從正上方起順時針排成一圈；第 i 條邊是 nodes[i] → nodes[i+1]（最後一條接回第一個）。
    labels（選用）= 每條邊的標籤，數量要等於節點數；hot（選用）= 畫成金色的邊序號（0 起）；
    heads（選用）= [圈中央的一句說明]；outcomes[0]（選用）= 底下一條橫框 {text, sub?}。節點裡只放短字（約 3 字）。"""
    nodes, labels, hot = spec["nodes"], spec.get("labels"), set(spec.get("hot", []))
    n = len(nodes)
    if not 3 <= n <= 8:
        raise ValueError(f"ring 要 3～8 個節點，現在是 {n} 個")
    if labels is not None and len(labels) != n:
        raise ValueError(f"ring 的 labels 數量（{len(labels)}）要等於節點數（{n}）：每條邊一個標籤")
    if any(not isinstance(h, int) or not 0 <= h < n for h in hot):
        raise ValueError(f"ring 的 hot 要是 0～{n - 1} 的邊序號：{sorted(hot, key=str)}")
    center = (spec.get("heads") or [None])[0]
    foot = (spec.get("outcomes") or [None])[0]
    w, rn = X1 - X0, 58
    fh = (c.lines(foot["text"], w - 44, 34) * 44.2 + (c.lines(foot["sub"], w - 44, 28) * 39.2 + 6 if foot.get("sub") else 0) + 44) if foot else 0
    lab = 56 if labels else 0                            # 標籤往圈外推的距離
    avail = BOTTOM - y0 - (28 + fh if foot else 0)
    Rx = min(360.0, (w - 2 * rn - (2 * 170 if labels else 0)) / 2)   # 橫向半徑：左右要留邊標籤的位置
    R = min(Rx, 300.0, (avail - 2 * rn - 2 * lab) / 2)               # 縱向半徑：高度不夠時壓成橢圓
    if R < 130:
        raise ValueError(f"示意圖（ring）放不下：圈的高只剩半徑 {R:.0f}px；請縮短補充、拿掉底下的橫框或邊的標籤")
    cx, cy = X0 + w / 2, y0 + lab + rn + R
    pts = [(cx + Rx * math.sin(2 * math.pi * i / n), cy - R * math.cos(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]; d = math.hypot(dx, dy)
        s_ = (p[0] + dx / d * (rn + 8), p[1] + dy / d * (rn + 8))
        e_ = (q[0] - dx / d * (rn + 14), q[1] - dy / d * (rn + 14))
        g = i in hot
        c.arrow(s_[0], s_[1], e_[0], e_[1], color=GOLD if g else DEEP, sw=9 if g else 6, head=26 if g else 22)
        if labels and labels[i]:
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            ox, oy = mx - cx, my - cy; od = math.hypot(ox, oy) or 1
            lx, ly = mx + ox / od * lab, my + oy / od * lab
            lw = 170
            al = "left" if ox / od > 0.35 else "right" if ox / od < -0.35 else "center"
            bx = lx - (0 if al == "left" else lw if al == "right" else lw / 2)
            c.text(bx, ly - 20, lw, labels[i], "dl", DEEP if g else TEAL, al)   # 金色字在米色底上對比不夠，金色只給箭頭
    for p, nd in zip(pts, nodes):
        emph = nd.get("emph")
        c.circle(p[0], p[1], rn, fill=GOLD if emph else DEEP)
        c.text(p[0] - rn, p[1] - 22, 2 * rn, nd["text"], "dl", DEEP if emph else CREAM, "center", (p[0] - rn, p[1] - rn, 2 * rn, 2 * rn))
    if center:
        iw = 2 * (min(Rx, R * 1.6) - rn) * 0.8
        ch = c.lines(center, iw, 34) * 44.2
        c.text(cx - iw / 2, cy - ch / 2, iw, center, "dn", DEEP, "center")
    y = cy + R + rn + lab
    if foot:
        y += 28
        c.textbox(X0, y, w, foot["text"], foot.get("sub"), fill=DEEP, tcolor=CREAM, scolor=LIGHT, align="center")
        y += fh
    return y


# ------------------------------------------------------------------ UniversalRAG（2026-11-09）
def _docs(c, x, y, w, n=3, col=DEEP):
    for i in range(n):
        c.rect(x, y + i * 26, w, 14, fill=col, rx=4, op=.75 if i else 1)


def _picture(c, x, y, w, h, gold=True):
    c.rect(x, y, w, h, fill="none", stroke=DEEP, sw=5, rx=10)
    b = y + h - 8
    c.poly([(x + 10, b), (x + w * .34, y + h * .42), (x + w * .55, y + h * .72), (x + w * .72, y + h * .5), (x + w - 10, b)], fill=TEAL, closed=True, op=.55)
    c.circle(x + w * .76, y + h * .28, min(w, h) * .13, fill=GOLD if gold else TEAL)


def magnet(c: Canvas, spec: dict, y0: float) -> float:
    """上面一個問題；粗箭頭吸到左邊的文字，右邊有答案的圖片只連到一條被叉掉的細虛線。"""
    q, (A, B) = spec["nodes"][0], spec["outcomes"][:2]
    heads, w = spec.get("heads", ["", ""]), X1 - X0
    pw = (w - 40) / 2
    qh = c.lines(q["text"], w - 44, 34) * 44.2 + 40
    lab = 39.2
    ph = 260
    th = max(c.lines(n["text"], pw - 44, 34) * 44.2 + (c.lines(n["sub"], pw - 44, 28) * 39.2 + 6 if n.get("sub") else 0) for n in (A, B))
    total = qh + 110 + ph
    _fit(total, BOTTOM - y0, "magnet")
    ph = min(ph + (BOTTOM - y0 - total) * .6, 340)
    gap = 110 + min((BOTTOM - y0 - qh - 110 - ph) * .6, 40)
    y = y0
    c.textbox(X0, y, w, q["text"], fill=DEEP, h=qh, align="center")
    y += qh
    xa, xb = X0 + pw / 2, X0 + pw + 40 + pw / 2
    c.arrow(X0 + w / 2 - 60, y + 6, xa, y + gap - 8, DEEP, 12, head=30)
    c.line(X0 + w / 2 + 60, y + 6, xb, y + gap - 12, TEAL, 4, dash="10 10")
    mx, my = (X0 + w / 2 + 60 + xb) / 2, y + gap / 2
    c.line(mx - 15, my - 15, mx + 15, my + 15, DEEP, 7); c.line(mx - 15, my + 15, mx + 15, my - 15, DEEP, 7)
    if heads[0]:
        c.text(X0, y + 14, pw * .62, heads[0], "ds", DEEP, "left")
    if len(heads) > 1 and heads[1]:
        c.text(X0 + w - pw * .62, y + 14, pw * .62, heads[1], "ds", TEAL, "right")
    y += gap
    c.rect(X0, y, pw, ph, fill=CREAM, stroke=DEEP, sw=4)
    c.rect(X0 + pw + 40, y, pw, ph, fill=CREAM, stroke=GOLD, sw=8)
    ih = max(ph - th - 66, 70)
    _docs(c, X0 + 80, y + 24, pw - 160, min(int(ih // 26), 4))
    _picture(c, X0 + pw + 40 + (pw - ih * 1.3) / 2, y + 22, ih * 1.3, ih)
    for x, n in ((X0, A), (X0 + pw + 40, B)):
        ty = y + 22 + ih + 18
        c.text(x + 22, ty, pw - 44, n["text"], "dn", DEEP, "center", (x, y, pw, ph))
        if n.get("sub"):
            c.text(x + 22, ty + c.lines(n["text"], pw - 44, 34) * 44.2 + 6, pw - 44, n["sub"], "ds", TEAL, "center", (x, y, pw, ph))
    return y + ph


def puzzle(c: Canvas, spec: dict, y0: float) -> float:
    """一個問題要兩塊：左邊實心的拿得到，右邊虛線的「？」拿不到；底下金色框是結果。"""
    q, a, b = spec["nodes"][:3]
    out, w = spec["outcomes"][0], X1 - X0
    qh, rh = c.lines(q["text"], w - 44, 34) * 44.2 + 40, c.lines(out["text"], w - 44, 34) * 44.2 + 40
    piece = 230
    total = qh + 60 + piece + 50 + rh
    _fit(total, BOTTOM - y0, "puzzle")
    piece = min(piece + (BOTTOM - y0 - total) * .7, 300)
    y = y0
    c.textbox(X0, y, w, q["text"], h=qh, align="center")
    y += qh
    pw, knob = 340, 34
    xl = X0 + w / 2 - pw
    c.arrow(X0 + w / 2 - pw / 2, y + 6, X0 + w / 2 - pw / 2, y + 54, DEEP, 6)
    c.arrow(X0 + w / 2 + pw / 2, y + 6, X0 + w / 2 + pw / 2, y + 54, TEAL, 4)
    y += 60
    c.rect(xl, y, pw, piece, fill=TEAL, rx=8)
    c.circle(xl + pw, y + piece / 2, knob, fill=TEAL)
    c.rect(xl + pw + 6, y, pw - 6, piece, fill="none", stroke=DEEP, sw=4, dash="12 10", rx=8)
    c.circle(xl + pw + 6, y + piece / 2, knob + 6, fill="none", stroke=DEEP, sw=4, dash="10 8")
    c.text(xl + 22, y + piece / 2 - c.lines(a["text"], pw - 44 - knob, 34) * 22, pw - 44 - knob, a["text"], "dn", CREAM, "center", (xl, y, pw, piece))
    c.text(xl + pw + 50, y + 26, pw - 74, "？", "dv", DEEP, "center")
    c.text(xl + pw + 50, y + piece / 2 + 16, pw - 74, b["text"], "dn", DEEP, "center", (xl + pw, y, pw, piece))
    y += piece + 50
    c.textbox(X0, y, w, out["text"], fill=GOLD, tcolor=DEEP, h=rh, align="center")
    return y + rh


def merge(c: Canvas, spec: dict, y0: float) -> float:
    """左邊幾種資料，箭頭匯入中間的編碼器，再全部進右邊同一個大圓。"""
    src, (enc, sp) = spec["outcomes"], spec["nodes"][:2]
    if not 2 <= len(src) <= 4:
        raise ValueError("merge 的 outcomes 要 2～4 個來源")
    h = BOTTOM - y0
    _fit(420, h, "merge")
    h = min(h, 560)
    y, sw, sh = y0, 180, min(96, (h - 20 * (len(src) - 1)) / len(src))
    gap = (h - sh * len(src)) / max(len(src) - 1, 1) if len(src) > 1 else 0
    ew = 250
    ex, ey, eh = X0 + sw + 60, y + h / 2 - 110, 220
    r = (X1 - (ex + ew + 50)) / 2
    r = min(r, h / 2)
    cx, cy = X1 - r, y + h / 2
    pal = (DEEP, TEAL, MID, LIGHT)      # 第 k 個來源 = 圓裡第 k 種點（2026-11-10 編輯：方塊兩種顏色、點三種顏色，讀者對不起來）
    for i, n in enumerate(src):
        sy = y + i * (sh + gap)
        c.rect(X0, sy, sw, sh, fill=CREAM, stroke=DEEP, sw=4, rx=12)
        c.circle(X0 + 30, sy + sh / 2, 13, fill=pal[i])
        c.text(X0 + 50, sy + (sh - 44.2) / 2, sw - 60, n["text"], "dn", DEEP, "center", (X0, sy, sw, sh))
        c.arrow(X0 + sw + 4, sy + sh / 2, ex - 6, y + h / 2, DEEP, 5)
    c.textbox(ex, ey, ew, enc["text"], enc.get("sub"), fill=CREAM, tcolor=DEEP, scolor=TEAL, stroke=DEEP, h=eh, align="center", pad=14)
    c.arrow(ex + ew + 4, y + h / 2, cx - r - 4, y + h / 2, DEEP, 10, head=26)
    c.circle(cx, cy, r, fill=LIGHT, op=.35, stroke=DEEP, sw=4)
    dots = [(-.5, -.45, 0), (-.2, -.62, 1), (.15, -.55, 2), (.48, -.4, 0), (.62, -.08, 1), (-.65, -.05, 2), (-.4, .42, 1), (.05, .62, 0), (.45, .42, 2), (.1, -.25, 1), (-.22, -.3, 2)]
    for dx, dy, k in dots:
        if k < len(src):
            c.circle(cx + dx * r, cy + dy * r, 13, fill=pal[k])
    tw = r * 1.5
    c.text(cx - tw / 2, cy - c.lines(sp["text"], tw, 34) * 22 + 34, tw, sp["text"], "dn", DEEP, "center")
    return y + h


CL_PTS = ((.50, .17, .22, .12), (.17, .74, .13, .12), (.74, .68, .21, .15))     # 三群的中心與半徑（相對座標）


def clusters(c: Canvas, spec: dict, y0: float) -> float:
    """向量空間的方框裡三群點，各自一種形式；問題（金星）落在文字那一群旁邊，到圖片那群是一條長虛線。"""
    heads, q, out = spec["heads"], spec["nodes"][0], spec["outcomes"][0]
    if len(heads) != 3:
        raise ValueError("clusters 的 heads 要三個（上、左下、右下）")
    _fit(420, BOTTOM - y0, "clusters")
    y, w, h = y0, X1 - X0, BOTTOM - y0
    c.rect(X0, y, w, h, fill="none", stroke=DEEP, sw=4, rx=10)
    cols = (TEAL, MID, DEEP)
    for k, (fx, fy, rx, ry) in enumerate(CL_PTS):
        cx, cy = X0 + fx * w, y + fy * h
        n = 46
        for i in range(n):                # 黃金角螺旋：點的位置固定，重渲不會變
            a, f = i * 2.39996, math.sqrt((i + .5) / n)
            c.circle(cx + math.cos(a) * f * rx * w, cy + math.sin(a) * f * ry * h, 8, fill=cols[k], op=.75)
    # 群的標籤放在群的外側，不壓在點上
    c.text(X0 + 40, y + 24, 300, heads[0], "dn", TEAL, "left")
    c.text(X0 + 24, y + h - 62, 300, heads[1], "dn", TEAL, "left")
    c.text(X1 - 324, y + h - 62, 300, heads[2], "dn", DEEP, "right")
    qx, qy = X0 + (CL_PTS[2][0] - CL_PTS[2][2] + .05) * w, y + (CL_PTS[2][1] - .03) * h
    ix, iy = X0 + CL_PTS[0][0] * w, y + (CL_PTS[0][1] + CL_PTS[0][3] + .03) * h
    c.line(qx, qy, ix, iy, DEEP, 4, dash="10 10")
    c.circle(qx, qy, 24, fill=GOLD, stroke=DEEP, sw=4)
    c.text(qx - 240, qy - 20, 200, q["text"], "dl", DEEP, "right")
    mx, my = (qx + ix) / 2, (qy + iy) / 2
    c.text(mx - 330, my - 62, 300, out["text"], "ds", DEEP, "right")
    return y + h


def shelves(c: Canvas, spec: dict, y0: float) -> float:
    """一列一種資料，左邊深色標籤，右邊 1～2 個抽屜（每個抽屜有把手）。"""
    cols = spec["columns"]
    if not 2 <= len(cols) <= 5:
        raise ValueError("shelves 的 columns 要 2～5 列")
    gap, lw, w = 18, 136, X1 - X0
    rw = w - lw - 14
    need = []
    for col in cols:
        iw = (rw - 14 * (len(col["items"]) - 1)) / len(col["items"]) - 90
        need.append(max(c.lines(it["text"], iw, 34) * 44.2 + (c.lines(it["sub"], iw, 28) * 39.2 + 6 if it.get("sub") else 0) for it in col["items"]) + 36)
    total = sum(need) + gap * (len(cols) - 1)
    _fit(total, BOTTOM - y0, "shelves")
    add = min((BOTTOM - y0 - total) / len(cols), 34)
    y = y0
    for col, h in zip(cols, need):
        h += add
        c.textbox(X0, y, lw, col["head"], h=h, align="center", pad=8)
        n = len(col["items"])
        dw = (rw - 14 * (n - 1)) / n
        for j, it in enumerate(col["items"]):
            x = X0 + lw + 14 + j * (dw + 14)
            c.rect(x, y, dw, h, fill=CREAM, stroke=DEEP, sw=4, rx=10)
            c.rect(x + 22, y + h / 2 - 24, 14, 48, fill=TEAL, rx=6)
            iw = dw - 90
            th = c.lines(it["text"], iw, 34) * 44.2 + (c.lines(it["sub"], iw, 28) * 39.2 + 6 if it.get("sub") else 0)
            ty = y + (h - th) / 2
            c.text(x + 62, ty, iw, it["text"], "dn", DEEP, "left", (x, y, dw, h))
            if it.get("sub"):
                c.text(x + 62, ty + c.lines(it["text"], iw, 34) * 44.2 + 6, iw, it["sub"], "ds", TEAL, "left", (x, y, dw, h))
        y += h + gap
    return y - gap


def switch(c: Canvas, spec: dict, y0: float) -> float:
    """問題 → Router → 一排庫：只有 on 的那條軌道是金色粗線，其他是淡虛線、庫上打叉。"""
    q, r_ = spec["nodes"][:2]
    libs, heads, w = spec["outcomes"], spec.get("heads", [""]), X1 - X0
    if not 3 <= len(libs) <= 5 or sum(1 for n in libs if n.get("on")) != 1:
        raise ValueError("switch 的 outcomes 要 3～5 個，且剛好一個 on")
    qh = c.lines(q["text"], w - 44, 34) * 44.2 + 36
    rw = 380
    rh = c.lines(r_["text"], rw - 44, 34) * 44.2 + (c.lines(r_["sub"], rw - 44, 28) * 39.2 + 6 if r_.get("sub") else 0) + 36
    lh, arr, fan_h = 112, 46, 150
    total = qh + arr + rh + fan_h + lh
    _fit(total, BOTTOM - y0, "switch")
    fan_h = min(fan_h + BOTTOM - y0 - total, 250)
    y = y0
    c.textbox(X0, y, w, q["text"], fill=CREAM, tcolor=DEEP, stroke=DEEP, h=qh, align="center")
    y += qh
    cx = X0 + w / 2
    c.arrow(cx, y + 4, cx, y + arr - 4, DEEP, 6)
    y += arr
    c.textbox(cx - rw / 2, y, rw, r_["text"], r_.get("sub"), h=rh, align="center")
    if heads and heads[0]:
        c.text(cx + rw / 2 + 24, y + (rh - 39.2 * c.lines(heads[0], X1 - cx - rw / 2 - 24, 28)) / 2, X1 - cx - rw / 2 - 24, heads[0], "ds", DEEP, "left")
    y += rh
    n = len(libs)
    lw = (w - 18 * (n - 1)) / n
    y2 = y + fan_h
    for off_first in (True, False):
        for i, l in enumerate(libs):
            if bool(l.get("on")) == off_first:
                continue
            x = X0 + i * (lw + 18) + lw / 2
            d = f"M{cx:.1f} {y:.1f} C{cx:.1f} {y + fan_h * .55:.1f},{x:.1f} {y + fan_h * .45:.1f},{x:.1f} {y2:.1f}"
            if l.get("on"):
                c.raw(f'<path class="bg" d="{d}" fill="none" stroke="{GOLD}" stroke-width="16" stroke-linecap="round"/>')
            else:
                c.raw(f'<path class="bg" d="{d}" fill="none" stroke="{TEAL}" stroke-width="4" stroke-dasharray="10 12" stroke-opacity=".6"/>')
    for i, l in enumerate(libs):
        x = X0 + i * (lw + 18)
        on = l.get("on")
        c.rect(x, y2, lw, lh, fill=GOLD if on else CREAM, stroke=None if on else TEAL, sw=3, dash=None if on else "10 8", rx=10)
        c.text(x + 8, y2 + (lh - 44.2) / 2, lw - 16, l["text"], "dn", DEEP, "center", (x, y2, lw, lh))
    return y2 + lh


def _lib(c, x, y, w, h, s, gold=False, dash=None):
    c.rect(x, y, w, h, fill=GOLD if gold else CREAM, stroke=None if gold else DEEP, sw=4, dash=dash, rx=10)
    c.text(x + 10, y + (h - 44.2) / 2, w - 20, s, "dn", DEEP, "center", (x, y, w, h))


def duel(c: Canvas, spec: dict, y0: float) -> float:
    """上段：問題用距離比，粗線連文字庫、細虛線連影像庫。下段：先判斷，金線直達影像庫，文字庫被打叉。"""
    heads, (txt, img), out = spec["heads"], spec["nodes"][:2], spec["outcomes"][0]
    lab, row = 56, 2 * 60 + 24            # 每段兩個庫上下排，框最矮 60（34px 字放得下），中間至少留 8
    h = BOTTOM - y0
    _fit(2 * (lab + row) + 44, h, "duel")
    row = min((h - 2 * lab - 44) / 2, 220)
    sx, lw = X0 + 50, 260
    lh = min(92, (row - 24) / 2)          # 2026-11-10：空間不夠時兩個框會疊在一起（讀者：文字資料壓在虛線框上），框高跟著縮
    lx = X1 - lw
    y = y0
    c.text(X0, y, X1 - X0, heads[0], "dl", TEAL, "left")
    y += lab
    ty, iy = y + 8, y + row - lh - 8
    cy = y + row / 2
    c.circle(sx, cy, 34, fill=DEEP)
    c.text(sx - 30, cy - 20, 60, "問", "dl", CREAM, "center", (sx - 30, cy - 26, 60, 52))
    c.line(sx + 36, cy, lx - 6, ty + lh / 2, DEEP, 12)
    c.line(sx + 36, cy, lx - 6, iy + lh / 2, TEAL, 4, dash="10 10")
    _lib(c, lx, ty, lw, lh, txt["text"])
    _lib(c, lx, iy, lw, lh, img["text"], dash="10 8")
    y += row + 44
    c.text(X0, y, X1 - X0, heads[1], "dl", TEAL, "left")
    y += lab
    ty, iy = y + 8, y + row - lh - 8
    cy = y + row / 2
    c.circle(sx, cy, 34, fill=DEEP)
    c.text(sx - 30, cy - 20, 60, "問", "dl", CREAM, "center", (sx - 30, cy - 26, 60, 52))
    jw, jh = 270, c.lines(out["text"], 270 - 28, 34) * 44.2 + 30
    jx = sx + 70
    c.line(sx + 36, cy, jx, cy, DEEP, 6)
    c.line(jx + jw, cy, lx - 6, iy + lh / 2, GOLD, 14)
    c.line(jx + jw, cy, lx - 6, ty + lh / 2, TEAL, 4, dash="10 10", op=.6)
    mx, my = (jx + jw + lx) / 2, (cy + ty + lh / 2) / 2
    c.line(mx - 14, my - 14, mx + 14, my + 14, DEEP, 7); c.line(mx - 14, my + 14, mx + 14, my - 14, DEEP, 7)
    c.textbox(jx, cy - jh / 2, jw, out["text"], fill=DEEP, h=jh, align="center", pad=14)
    _lib(c, lx, ty, lw, lh, txt["text"], dash="10 8")
    _lib(c, lx, iy, lw, lh, img["text"], gold=True)
    return y + row


def matrix(c: Canvas, spec: dict, y0: float) -> float:
    """列是系統、欄是情況。hot 的列塗金色。"""
    heads, rows, cells, hot, w = spec["heads"], spec["nodes"], spec["cells"], spec.get("hot"), X1 - X0
    if len(cells) != len(rows) or any(len(r) != len(heads) for r in cells):
        raise ValueError("matrix 的 cells 要和列、欄數一致")
    kw_, gap = 300, 16
    cw = (w - kw_ - gap * len(heads)) / len(heads)
    hh = max(c.lines(h_, cw - 20, 28) * 39.2 for h_ in heads) + 24
    rh = [max(c.lines(r["text"], kw_ - 36, 34) * 44.2 + (c.lines(r["sub"], kw_ - 36, 28) * 39.2 + 6 if r.get("sub") else 0),
              max(c.lines(x[0], cw - 28, 34) * 44.2 for x in row)) + 44 for r, row in zip(rows, cells)]
    total = hh + sum(rh) + gap * len(rows)
    _fit(total, BOTTOM - y0, "matrix")
    add = min((BOTTOM - y0 - total) / len(rows), 90)
    y = y0
    for j, h_ in enumerate(heads):
        c.text(X0 + kw_ + gap + j * (cw + gap) + 10, y, cw - 20, h_, "ds", TEAL, "center")
    y += hh
    for i, (r, row, h) in enumerate(zip(rows, cells, rh)):
        h += add
        is_hot = i == hot
        c.textbox(X0, y, kw_, r["text"], r.get("sub"), h=h, align="center", pad=18)
        for j, x in enumerate(row):
            cx_ = X0 + kw_ + gap + j * (cw + gap)
            c.rect(cx_, y, cw, h, fill=GOLD if is_hot else CREAM, stroke=None if is_hot else DEEP, sw=4, rx=10)
            c.text(cx_ + 14, y + (h - c.lines(x[0], cw - 28, 34) * 44.2) / 2, cw - 28, x[0], "dn", DEEP, "center", (cx_, y, cw, h))
        y += h + gap
    return y - gap


def race(c: Canvas, spec: dict, y0: float) -> float:
    """兩條路到同一個答案：對照那條繞來繞去、主角那條是一段金色直線。不帶數字，路的長短只是示意，圖註要標。"""
    heads, w = spec["heads"], X1 - X0
    if len(heads) != 2 or len(spec["nodes"]) != 1:
        raise ValueError("race 的 heads 要兩個、nodes 要一個（規模）")
    lab, lane = 50, 120
    total = lab + 30 + 2 * (lab + lane) + 30
    _fit(total, BOTTOM - y0, "race")
    lane = min(lane + (BOTTOM - y0 - total) / 2, 190)
    y = y0
    c.text(X0, y, w, spec["nodes"][0]["text"], "dn", DEEP, "left")
    y += lab + 30
    gx = X1 - 50
    c.text(X0, y, w, heads[0], "dl", TEAL, "left")
    y += lab
    cy, n, sx, ex = y + lane / 2, 7, X0 + 24, gx - 40
    pts = [(sx + (ex - sx) * i / (n * 8), cy + (lane / 2 - 16) * math.sin(i / 8 * math.pi)) for i in range(n * 8 + 1)]
    c.poly(pts, stroke=TEAL, sw=10)
    c.circle(sx, cy, 18, fill=DEEP); c.circle(gx, cy, 34, fill=TEAL)
    y += lane + 30
    c.text(X0, y, w, heads[1], "dl", TEAL, "left")
    y += lab
    cy = y + lane / 2
    gate = (spec.get("outcomes") or [None])[0]       # 選用（2026-11-10）：直線那條路上多畫一道關卡，標籤是 outcomes[0]
    if gate:
        gw, gx0 = max(160, len(gate["text"]) * 22 + 48), sx + 60
        c.line(sx, cy, gx0, cy, GOLD, 16)
        c.textbox(gx0, cy - 36, gw, gate["text"], fill=DEEP, h=72, align="center", pad=10)
        c.line(gx0 + gw, cy, gx - 34, cy, GOLD, 16)
    else:
        c.line(sx, cy, gx - 34, cy, GOLD, 16)
    c.circle(sx, cy, 18, fill=DEEP); c.circle(gx, cy, 34, fill=GOLD)
    return y + lane


# ------------------------------------------------------------------ UniversalRAG 第 2 則（2026-11-10）
def _miss(c: Canvas, x: float, y: float, w: float, s: str) -> float:
    """一個被打叉的下場：深色圓裡一個米色叉，右邊一句話（34px）。回傳高度。"""
    h = c.lines(s, w - 64, 34) * 44.2
    c.circle(x + 22, y + h / 2, 22, fill=DEEP)
    _cross(c, x + 22, y + h / 2, 9, CREAM, 4)
    c.text(x + 60, y, w - 60, s, "dn", DEEP, "left")
    return h


def grain(c: Canvas, spec: dict, y0: float) -> float:
    """粒度抓錯的兩種下場：上段一條整部影片的膠捲，只有一小段金色是真正需要的；下段一段文字只抓到中間一行。
    heads = [上段標籤, 下段標籤]、nodes = [{text}（膠捲下的說明）, {text}（文字段右邊的說明）]、outcomes = [{text}（上段的下場）, {text}（下段的下場）]。
    金色那段的寬度不按比例（真的按比例會細到看不見），圖註要標「示意」。"""
    heads, nodes, outs = spec["heads"], spec["nodes"], spec["outcomes"]
    if len(heads) != 2 or len(nodes) != 2 or len(outs) != 2:
        raise ValueError("grain 的 heads、nodes、outcomes 都要剛好兩個")
    w, lab, film = X1 - X0, 44, 84
    cap = c.lines(nodes[0]["text"], w, 28) * 39.2
    o1 = c.lines(outs[0]["text"], w - 64, 34) * 44.2
    bw = 430
    rw = w - bw - 44
    para = 5 * 30 + 34
    right = c.lines(nodes[1]["text"], rw, 28) * 39.2 + 16 + c.lines(outs[1]["text"], rw - 64, 34) * 44.2
    blk = max(para, right)
    gap = 40
    total = lab + 12 + film + 14 + cap + 16 + o1 + gap + lab + 12 + blk
    _fit(total, BOTTOM - y0, "grain")
    gap += min(BOTTOM - y0 - total, 80)
    y = y0
    c.text(X0, y, w, heads[0], "dl", TEAL, "left")
    y += lab + 12
    c.rect(X0, y, w, film, fill=DEEP, rx=8)
    for k in range(int((w - 24) // 36)):          # 膠捲上下緣的齒孔
        fx = X0 + 14 + k * 36
        c.rect(fx, y + 9, 18, 11, fill=CREAM, rx=3, op=.5)
        c.rect(fx, y + film - 20, 18, 11, fill=CREAM, rx=3, op=.5)
    c.rect(X0 + w * .62, y - 12, 14, film + 24, fill=GOLD, rx=4)
    y += film + 14
    c.text(X0, y, w, nodes[0]["text"], "ds", DEEP, "left")
    y += cap + 16
    _miss(c, X0, y, w, outs[0]["text"])
    y += o1 + gap
    c.text(X0, y, w, heads[1], "dl", TEAL, "left")
    y += lab + 12
    py = y + (blk - para) / 2
    c.rect(X0, py, bw, para, fill="none", stroke=TEAL, sw=3, dash="8 8", rx=12)
    for k in range(5):
        on = k == 2
        c.rect(X0 + 24, py + 20 + k * 30, (bw - 48) * (.94, .82, .9, .86, .6)[k], 14, fill=DEEP, rx=6, op=None if on else .22)
    rx_ = X0 + bw + 44
    ry = y + (blk - right) / 2
    c.text(rx_, ry, rw, nodes[1]["text"], "ds", DEEP, "left")
    _miss(c, rx_, ry + c.lines(nodes[1]["text"], rw, 28) * 39.2 + 16, rw, outs[1]["text"])
    return y + blk


def ballot(c: Canvas, spec: dict, y0: float) -> float:
    """答案卡：heads = [卡片抬頭, 選用：抬頭右邊的小字]；選用 nodes[0] = {text}（上方的問題，箭頭指向答案卡）；
    outcomes = 選項 3～8 個 [{text, sub?, on?}]（on 的格子打勾、整列墊淡金色）。純示意。"""
    opts, heads = spec["outcomes"], spec.get("heads", [])
    if not 3 <= len(opts) <= 8:
        raise ValueError(f"ballot 的 outcomes（選項）要 3～8 個，現在 {len(opts)} 個")
    if not heads:
        raise ValueError("ballot 要有 heads[0]（答案卡抬頭）")
    q = (spec.get("nodes") or [None])[0]
    w = X1 - X0
    qh = c.lines(q["text"], w - 44, 34) * 44.2 + 40 if q else 0
    qgap = 56 if q else 0
    hh, rh, nw = 60, 58, 230
    total = qh + qgap + hh + 12 + len(opts) * rh + 12
    _fit(total, BOTTOM - y0, "ballot")
    rh = min(rh + (BOTTOM - y0 - total) / len(opts), 72)
    y = y0
    if q:
        c.textbox(X0, y, w, q["text"], fill=DEEP, h=qh, align="center")
        y += qh
        c.arrow(X0 + w / 2, y + 8, X0 + w / 2, y + qgap - 6, DEEP, 6, head=18)
        y += qgap
    ch = hh + 12 + len(opts) * rh + 12
    c.rect(X0, y, w, ch, fill=CREAM, stroke=DEEP, sw=4, rx=18)
    c.rect(X0, y, w, hh, fill=DEEP, rx=18)
    c.rect(X0, y + hh - 20, w, 20, fill=DEEP, rx=0)
    c.text(X0 + 28, y + (hh - 39.2) / 2, w * .62, heads[0], "dl", CREAM, "left", (X0, y, w, hh))
    if len(heads) > 1 and heads[1]:
        c.text(X0 + w * .62, y + (hh - 39.2) / 2, w * .38 - 28, heads[1], "dl", GOLD, "right", (X0, y, w, hh))
    yy = y + hh + 12
    for o in opts:
        on = o.get("on")
        cy = yy + rh / 2
        if on:
            c.rect(X0 + 14, yy + 4, w - 28, rh - 8, fill=GOLD, rx=10, op=.38)
        c.rect(X0 + 36, cy - 18, 36, 36, fill=GOLD if on else "none", stroke=DEEP if on else TEAL, sw=4, rx=6)
        if on:
            _tick(c, X0 + 54, cy, DEEP, 5)
        c.text(X0 + 94, cy - 22, nw - 10, o["text"], "dn", DEEP, "left")
        if o.get("sub"):
            c.text(X0 + 94 + nw, cy - 19.6, w - 94 - nw - 28, o["sub"], "ds", DEEP if on else TEAL, "left")
        yy += rh
    return y + ch


def thresh(c: Canvas, spec: dict, y0: float) -> float:
    """每個選項各自打分、超過門檻才啟動：nodes = 選項 [{text, p}]（p 在 0～1，通常是假設的分數）、ref = {name, value}（門檻）、
    heads = [上方標籤]。分數超過門檻的橫條金色，其餘半透明藍綠；長度與分數成正比（軸 0～1），一條直虛線標門檻。圖註要說明分數是假設的。"""
    nodes, ref, heads = spec["nodes"], spec["ref"], spec.get("heads", [""])
    tau = ref["value"]
    if not 0 < tau < 1 or any(not 0 <= n["p"] <= 1 for n in nodes):
        raise ValueError("thresh 的門檻與分數都要在 0～1 之間")
    w, nw, vw = X1 - X0, 210, 96
    bx0, bx1 = X0 + nw, X1 - vw
    bl = bx1 - bx0
    hh, rh = 52, 48
    total = hh + 26 + len(nodes) * rh
    _fit(total, BOTTOM - y0, "thresh")
    rh = min(rh + (BOTTOM - y0 - total) / len(nodes), 74)
    y = y0
    xt = bx0 + bl * tau
    if heads[0]:
        c.text(X0, y, xt - X0 - 160, heads[0], "dl", TEAL, "left")
    c.text(xt - 150, y, 300, f"{ref['name']} {tau:g}", "dl", DEEP, "center")
    y += hh + 26
    top = y
    for n in nodes:
        on = n["p"] > tau
        cy = y + rh / 2
        c.text(X0, cy - 22, nw - 16, n["text"], "dn", DEEP if on else TEAL, "left")
        c.rect(bx0, cy - 15, bl, 30, fill=DEEP, rx=6, op=.07)
        if n["p"] > 0:
            c.rect(bx0, cy - 15, max(bl * n["p"], 12), 30, fill=GOLD if on else TEAL, rx=6, op=None if on else .5)
        c.text(bx1 + 12, cy - 19.6, vw - 12, f"{n['p']:g}", "dl", DEEP if on else TEAL, "left")
        y += rh
    c.line(xt, top - 18, xt, y + 4, DEEP, 4, dash="10 8")
    return y


def murky(c: Canvas, spec: dict, y0: float) -> float:
    """企業文件裡表格和文字混在一起、分不清：左邊一頁報告（上下是文字灰條、中間夾一張小表格，表格角落一個金色問號）；
    右邊一句問話，箭頭往下指向兩個被打叉的下場。heads = [文件上方標籤, 右邊的問話]、nodes[0] = {text}（箭頭旁的話）、outcomes = 兩個下場 [{text}]。純示意。"""
    heads, al, outs = spec["heads"], spec["nodes"][0], spec["outcomes"]
    if len(heads) != 2 or len(outs) != 2:
        raise ValueError("murky 的 heads 要兩個、outcomes 要兩個")
    w, pw, lab = X1 - X0, 400, 44
    rx = X0 + pw + 60
    rw = X1 - rx
    qh = c.lines(heads[1], rw, 34) * 44.2
    ah = c.lines(al["text"], rw - 40, 28) * 39.2
    oh = [c.lines(o["text"], rw - 64, 34) * 44.2 for o in outs]
    arr = max(ah + 24, 96)
    right = qh + 20 + arr + 20 + oh[0] + 26 + oh[1]
    ph = 430
    total = lab + 12 + max(ph, right)
    _fit(total, BOTTOM - y0, "murky")
    ph = min(max(ph, right) + (BOTTOM - y0 - total) * .5, 520)
    y = y0
    c.text(X0, y, pw, heads[0], "dl", TEAL, "left")
    y += lab + 12
    c.rect(X0, y, pw, ph, fill=CREAM, stroke=DEEP, sw=4, rx=12)
    ty = y + 32
    for k in range(3):
        c.rect(X0 + 30, ty + k * 30, (pw - 60) * (.95, .82, .58)[k], 12, fill=DEEP, rx=6, op=.25)
    tby, tbw = ty + 3 * 30 + 18, pw - 60
    tbh = ph - 2 * (3 * 30 + 18 + 32) - 6
    c.rect(X0 + 30, tby, tbw, tbh, fill="none", stroke=TEAL, sw=3, rx=4)
    c.rect(X0 + 30, tby, tbw, tbh / 4, fill=TEAL, rx=4, op=.3)
    for i in range(1, 4):
        c.line(X0 + 30, tby + tbh * i / 4, X0 + 30 + tbw, tby + tbh * i / 4, TEAL, 2)
    for j in range(1, 3):
        c.line(X0 + 30 + tbw * j / 3, tby, X0 + 30 + tbw * j / 3, tby + tbh, TEAL, 2)
    by = tby + tbh + 22
    for k in range(3):
        c.rect(X0 + 30, by + k * 30, (pw - 60) * (.9, .97, .7)[k], 12, fill=DEEP, rx=6, op=.25)
    qx, qy = X0 + 30 + tbw, tby
    c.circle(qx, qy, 34, fill=GOLD)
    c.text(qx - 34, qy - 22.1, 68, "?", "dn", DEEP, "center")
    ry = y + (ph - right) / 2
    c.text(rx, ry, rw, heads[1], "dn", DEEP, "left")
    ry += qh + 20
    c.arrow(rx + 16, ry, rx + 16, ry + arr, DEEP, 6, head=18)
    c.text(rx + 40, ry + (arr - ah) / 2, rw - 40, al["text"], "ds", DEEP, "left")
    ry += arr + 20
    _miss(c, rx, ry, rw, outs[0]["text"])
    _miss(c, rx, ry + oh[0] + 26, rw, outs[1]["text"])
    return y + ph


KINDS = {"flow": flow, "compare": compare, "pairs": pairs, "samples": samples, "paths": paths, "epochs": epochs,
         "dotgrid": dotgrid, "dumbbell": dumbbell, "range": range_chart, "funnel": funnel,
         "batches": batches, "decay": decay, "stops": stops, "fan": fan, "peaks": peaks, "quad": quad, "locked": locked, "equation": equation, "tokens": tokens,
         "seesaw": seesaw, "hidden": hidden, "cycle": cycle, "links": links, "hops": hops, "bubble": bubble, "drift": drift, "ingest": ingest,
         "roles": roles, "embed": embed, "online": online, "gate": gate, "concat": concat, "joint": joint, "rails": rails, "scoreboard": scoreboard, "leak": leak, "amplify": amplify,
         "receipt": receipt, "squeeze": squeeze, "alias": alias, "handoff": handoff, "mismatch": mismatch, "ledger": ledger,
         "transcript": transcript, "oneloop": oneloop, "intercept": intercept, "dial": dial, "lanes": lanes, "layers": layers, "turn": turn,
         "sockets": sockets, "lazy": lazy, "hub": hub, "pinned": pinned, "compact": compact, "sidecar": sidecar, "combo": combo,
         "waist": waist, "schema": schema, "branch": branch, "gates": gates, "route": route, "depend": depend,
         "pick": pick, "pile": pile, "addlane": addlane,
         "dist": dist, "snap": snap, "stack": stack, "target": target, "ring": ring,
         "magnet": magnet, "puzzle": puzzle, "merge": merge, "clusters": clusters, "shelves": shelves, "switch": switch, "duel": duel, "matrix": matrix, "race": race,
         "grain": grain, "ballot": ballot, "thresh": thresh, "murky": murky}


def build(spec: dict, y0: float, ctx: Ctx) -> tuple[str, str, float]:
    global BOTTOM
    BOTTOM = 1180 if spec.get("note") else 1235       # 有圖註（y=1196）時，圖要在它上面結束
    c = Canvas(ctx)
    bottom = KINDS[spec["kind"]](c, spec, y0)
    return "".join(c.svg), "".join(c.html), bottom


def texts(sl: dict) -> list[str]:
    """示意圖上的所有文字與數字（逐欄位，給 check_a 的數字／名稱檢查與 build_package 的審查文字用）。"""
    out = []
    for st in sl.get("steps", []):
        out.append(st["label"])
        for cell in st["cells"]:
            out.append(cell["text"]); out += [cell["sub"]] if cell.get("sub") else []
    for n in sl.get("nodes", []) + sl.get("outcomes", []):
        out.append(n["text"]); out += [n["sub"]] if n.get("sub") else []; out += [n["sub2"]] if n.get("sub2") else []; out += [n["win"]] if n.get("win") else []
    for row in sl.get("cells", []):
        for pair in row:
            out += list(pair)
    if sl.get("loop"):
        out.append(sl["loop"])
    for col in sl.get("columns", []):
        out.append(col["head"])
        for it in col["items"]:
            out.append(it["text"]); out += [it["sub"]] if it.get("sub") else []
    out += list(sl.get("heads", []))
    for l, r in sl.get("pairs", []):
        out += [l, r]
    if "count" in sl:
        out.append(f"{sl['count']}")
    if "on" in sl:
        out.append(f"{sl['on']}")
    if sl.get("kind") == "thresh":      # 每條橫條旁的分數（通常是假設的例子），審查者與程式 A 都要看得到
        out += [f"{n['p']:g}" for n in sl.get("nodes", [])]
    if sl.get("kind") == "dist":
        out += [f"{n['p']:g}" for n in sl.get("nodes", [])]
        if sl.get("pick", "ev") == "ev":
            out.append(f"{(list(sl.get('heads', [])) + ['', ''])[1]} {dist_ev(sl['nodes']):.2f}".strip())
    for r in sl.get("nodes", []) if sl.get("kind") in ("snap", "stack") else []:
        out += [m["text"] for m in r.get("marks", [])] + ([r["tie"]] if r.get("tie") else [])
        if r.get("parts"):
            out.append("・".join(f"{h} {p}" for h, p in zip(sl.get("heads", []), r["parts"])))   # 和圖上那一行一字不差（讀者引用才對得上）
    if sl.get("kind") == "ring":
        out += [x for x in sl.get("labels") or [] if x]
    if sl.get("kind") == "equation" and sl.get("ops"):      # 運算符號是內容（+ 和 × 意思不同），審查者要看得到整條算式
        ns, ops = sl.get("nodes", []), sl["ops"]
        out.append("算式：" + " ".join(x for pair in zip([n["text"] for n in ns], list(ops) + [""]) for x in pair if x))
    if "group" in sl:
        out.append(f"{sl['group']}")
    u = sl.get("unit", "")
    if "start" in sl:
        out += [f"{sl['start']:g}{u}", f"{sl['end']:g}{u}"]
    for p in sl.get("points", []):
        out += [p["name"], f"{p['value']:g}{u}"]
    if sl.get("ref"):
        out += [sl["ref"]["name"], f"{sl['ref']['value']:g}{u}"]
    for r in sl.get("ranges", []):
        out.append(r["name"]); out += [r["sub"]] if r.get("sub") else []
        out += [f"{r['lo']:g}{u}", f"{r['hi']:g}{u}"]
    return out
