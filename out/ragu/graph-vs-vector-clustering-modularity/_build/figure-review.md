# 重製圖審查材料：graph-vs-vector-clustering-modularity

原圖是 blog 從論文截來的參考圖；圖說（caption）是 blog 的圖說原文，**不是主張**。重製圖要和「原圖」與「主張文字」對得上（見 figure-prompt.md）。

## 第 6 張

- 重製後的圖：/Users/johnnyhwu/Desktop/datasciocean-social-media/out/ragu/graph-vs-vector-clustering-modularity/ig/06.png
- 重製圖上的文字（貼文最終文字）：
  - 版型：diagram
  - 小標籤：切成兩群
  - 主標：Ritchie 的圖
從唯一的橋切成兩群
  - 補充：論文自己的例子：Dennis Ritchie 和父親 Alistair 之間只有一條線。剪斷這條橋，換來兩邊各自連得很緊。
  - 示意圖（netgraph）上的文字與數字：Dennis Ritchie｜C 語言｜Unix｜Oct 12, 2011｜70｜Alistair E. Ritchie｜Bell Labs｜Murray Hill｜New Jersey｜Ritchie 這個主題｜貝爾實驗室這個地點｜被剪斷的橋
  - 示意圖的連線：Dennis Ritchie—C 語言｜Dennis Ritchie—Unix｜Dennis Ritchie—Oct 12, 2011｜Dennis Ritchie—70｜Dennis Ritchie—Alistair E. Ritchie（金色虛線：被切斷）｜Alistair E. Ritchie—Bell Labs｜Bell Labs—Murray Hill｜Murray Hill—New Jersey
  - 示意圖的第 1 群（Ritchie 這個主題）：Dennis Ritchie、C 語言、Unix、Oct 12, 2011、70
  - 示意圖的第 2 群（貝爾實驗室這個地點）：Alistair E. Ritchie、Bell Labs、Murray Hill、New Jersey
  - 圖註：節點位置照論文的圖擺，只是示意

### 原圖 ragu/figure4.png
- 檔案：/Users/johnnyhwu/Desktop/datasciocean-social-media/concept-wiki/wiki/figures/ragu/figure4.png
- blog 圖說原文（不是主張）：圖三 — 從 Ritchie 段落建出的知識圖，Leiden 把它切成兩個社群：Ritchie 的專業成就，以及貝爾實驗室的地理叢集。（來源：原始論文 Figure 4）
- 附這張圖的主張：c6, c11

### 這張引用的主張（圖要以它們為準）
- **c6**（部落格考證）：blog 拿論文自己的 demo 實算：一段關於 Dennis Ritchie 的文字建出的圖，Dennis Ritchie 連向 C 語言、Unix、過世日期 Oct 12, 2011 與 70（過世時的年齡），並經由唯一的橋連到父親 Alistair E. Ritchie，再串成 Alistair → Bell Laboratories → Murray Hill → New Jersey 的鏈；總邊數 m = 8，度數是 Dennis 5、Alistair 2、Bell Labs 2、Murray Hill 2、其餘各 1
- **c8**（數學推導）：0.367 大於 0，所以切成兩群比不切好；Alistair 跟 Dennis 之間那條橋被犧牲成跨社群的邊，換來兩邊各自的內聚度，這就是演算法在做的權衡
- **c11**（部落格舉例）：同一張 Ritchie 圖用兩種分法：向量分群按語意會得到 {Dennis Ritchie, Alistair E. Ritchie}（都是人）、{C 語言, Unix}（都是軟體）、{Murray Hill, New Jersey}（都是地名）、{Oct 12 2011, 70}（都是數值）；圖分群按結構會得到 {Dennis, C 語言, Unix, Oct12, 70}（都跟 Ritchie 這個主題有關）與 {Alistair, Bell Labs, Murray Hill, NJ}（都跟貝爾實驗室這個地點有關）
