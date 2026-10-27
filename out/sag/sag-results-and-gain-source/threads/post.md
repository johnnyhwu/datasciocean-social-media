# Threads：SAG 的成績從哪來？

- 發文方式：**一則輪播貼文**（正文＋全部 14 張圖，順序與 IG 相同），再用一則回覆放連結與系列（連結只放那則回覆）
- 圖檔在 `../ig/`（與 IG 輪播共用同一套）

## 貼文正文（附下方全部圖片）

```text
SAG 這篇 RAG 論文最響亮的招牌是「超邊」，但成績的大頭，其實來自它的 SQL 檢索管線。

在最難的 MuSiQue 上，SAG 的 Recall 比 HippoRAG 2 高出近 15 個百分點（兩邊用同一個 BGE-Large embedding）。作者把 SAG 硬拆成三元組、拿掉超邊，Recall@5（前 5 筆結果抓到答案所需資料的比例）從 80.0% 掉到 77.1%，還是大幅贏過 HippoRAG 2 的 65.1%。

另一個實驗換成更強的 embedding（向量模型）：HippoRAG 2 進步 9.5 個百分點，SAG 只進步 1.7 個百分點，用比較弱的 embedding 也撐得住。不過 SAG 並不是不用向量，別名對齊（同一個東西不同寫法）、候選太多時的排序，還是靠向量。以上都是 MuSiQue 上的實驗。

論文：arxiv.org/abs/2606.15971
```

## 附圖（依序）

![第 1 頁](../ig/01.png)
![第 2 頁](../ig/02.png)
![第 3 頁](../ig/03.png)
![第 4 頁](../ig/04.png)
![第 5 頁](../ig/05.png)
![第 6 頁](../ig/06.png)
![第 7 頁](../ig/07.png)
![第 8 頁](../ig/08.png)
![第 9 頁](../ig/09.png)
![第 10 頁](../ig/10.png)
![第 11 頁](../ig/11.png)
![第 12 頁](../ig/12.png)
![第 13 頁](../ig/13.png)
![第 14 頁](../ig/14.png)

## 回覆：連結與系列

```text
SAG 的成績從哪來？招牌是超邊，績效的大頭卻來自 SQL 檢索管線。它付出了什麼代價，之後的貼文會講。
文章：datasciocean.com/paper-intro/sag
同系列：Multi-Hop 推理，一定要先建知識圖譜嗎？
https://www.threads.com/@datasciocean/post/De5vTr5E64N
同系列：SQL、向量、LLM 怎麼分工？
https://www.threads.com/@datasciocean/post/De8MzobmMZi
同系列：SAG 付出了什麼代價？（尚未發布）
```
