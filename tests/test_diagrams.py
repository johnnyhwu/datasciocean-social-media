"""示意圖版型（layout: diagram）的回歸測試：正確的圖要通過程式 B；故意做壞的（文字塞不進框、放不下）必須被抓到。
用法（repo 根目錄）：uv run python tests/test_diagrams.py
用 series/skillopt 的模板（真實系列），spec 放暫存資料夾，不碰 out/。
"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / ".claude/skills/make-social-post/scripts/render.py"
fails = []


def render(slide):
    doc = {"series": "skillopt", "concept": "skillopt-overview", "slides": [slide]}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "spec.json"
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["uv", "run", "python", str(RENDER), str(p), "--force"], capture_output=True, text=True, cwd=ROOT)   # --force：測試借用的 concept 之後可能已發布（render 預設拒絕已發布的貼文），這裡只渲染暫存資料夾，不碰真貼文
        return r.returncode, r.stdout + r.stderr


def expect(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail[:200]}]" if not ok else ""))
    if not ok:
        fails.append(name)


D = lambda kind, **kw: {"layout": "diagram", "kind": kind, "title": "測試標題", "body": "測試補充。", **kw}

code, out = render(D("flow", nodes=[{"text": "第一步", "sub": "說明"}, {"text": "第二步"}],
                     outcomes=[{"text": "收下", "tone": "good"}, {"text": "丟掉"}], loop="每一輪再檢查一次"))
expect("正確的流程圖通過程式 B", code == 0, out)

code, out = render(D("range", ranges=[{"name": "甲", "lo": 100, "hi": 100}, {"name": "乙", "lo": 56, "hi": 74, "emph": True}], unit="%", axis_max=100))
expect("正確的區間條通過程式 B（含比例檢查）", code == 0 and "PASS" in out, out)

code, out = render(D("dumbbell", points=[{"name": "前", "value": 22.1}, {"name": "後", "value": 81.8}], ref={"name": "參考", "value": 80.4}, unit="分", axis_max=100))
expect("正確的前後對比圖通過程式 B（含位置檢查）", code == 0, out)

code, out = render(D("funnel", nodes=[{"text": "上"}, {"text": "中"}, {"text": "這是一段沒有任何標點而且非常非常長的底層文字讓它塞不進漏斗的最後一層"}]))
expect("故意做壞：文字塞不進框 → 抓得到", code != 0 and "框內文字不超出框" in out, out)

code, out = render(D("compare", columns=[{"head": "甲", "items": [{"text": "很長的項目" * 6, "sub": "很長的說明" * 8} for _ in range(8)]}, {"head": "乙", "items": [{"text": "x"}]}]))
expect("故意做壞：圖太高放不下 → 報錯", code != 0 and "放不下" in out, out)

code, out = render(D("batches", count=20, group=8, nodes=[{"text": "一個池子"}, {"text": "每組各自診斷"}]))
expect("正確的切組圖通過程式 B", code == 0, out)
code, out = render(D("decay", start=4, end=2, unit="處", axis_max=5, nodes=[{"text": "初期"}, {"text": "後期"}]))
expect("正確的遞減曲線通過程式 B", code == 0, out)
code, out = render(D("stops", heads=["太小", "太大"], nodes=[{"text": "甲", "sub": "說明"}, {"text": "乙", "emph": True}, {"text": "丙"}]))
expect("正確的三個停靠點通過程式 B", code == 0, out)
code, out = render(D("stops", nodes=[{"text": "很長的項目" * 12, "sub": "很長的說明" * 14} for _ in range(3)]))
expect("故意做壞：停靠點的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("batches", count=20, group=8, nodes=[{"text": "很長的池子說明" * 20}, {"text": "很長的每組說明" * 20}]))
expect("故意做壞：切組圖的標籤太長放不下 → 報錯", code != 0 and "放不下" in out, out)

code, out = render(D("fan", heads=["第 1 組", "第 2 組", "第 3 組"], nodes=[{"text": "各組同時診斷"}, {"text": "彙整成一份", "sub": "再往下走"}]))
expect("正確的匯整圖通過程式 B", code == 0, out)
code, out = render(D("fan", heads=["很長的組名" * 6, "乙", "丙"], nodes=[{"text": "很長的說明" * 40}, {"text": "很長的結果" * 30, "sub": "很長的小字" * 30}]))
expect("故意做壞：匯整圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

code, out = render(D("peaks", nodes=[{"text": "甲線"}, {"text": "乙線"}, {"text": "重合"}]))
expect("正確的最高點重合圖通過程式 B", code == 0, out)
code, out = render(D("quad", nodes=[{"text": "進步"}, {"text": "退步", "sub": "重點", "emph": True}, {"text": "持續失敗"}, {"text": "穩定成功"}]))
expect("正確的四格圖通過程式 B", code == 0, out)
code, out = render(D("dotgrid", count=80, cols=20, nodes=[{"text": "一個點是一筆訓練樣本：一篇論文的一種配置"}]))
expect("正確的點陣（指定每列 20 個點、80 個點）通過程式 B", code == 0, out)
code, out = render(D("dotgrid", count=80, cols=20, nodes=[{"text": "很長的圖例" * 60}]))
expect("故意做壞：點陣圖例是沒有標點的超長字串 → 程式 B 抓得到", code != 0, out)
code, out = render(D("quad", nodes=[{"text": "專家 × 長版", "bars": 5}, {"text": "專家 × 短版", "bars": 2}, {"text": "非專家 × 長版", "bars": 5}, {"text": "非專家 × 短版", "bars": 3}]))
expect("正確的四格圖（格子上方有小投影片）通過程式 B", code == 0, out)
code, out = render(D("quad", nodes=[{"text": "很長的格子" * 12, "sub": "很長的說明" * 15, "bars": 3} for _ in range(4)]))
expect("故意做壞：有小投影片的四格圖字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("equation", nodes=[{"text": "20", "sub": "篇論文", "sub2": "訓練資料集"}, {"text": "4", "sub": "種 persona"}, {"text": "80", "sub": "筆訓練樣本", "sub2": "拿去微調模型", "emph": True}], outcomes=[{"text": "驗證資料集：僅 5 篇論文"}]))
expect("正確的算式圖通過程式 B", code == 0, out)
code, out = render(D("equation", nodes=[{"text": "20", "sub": "很長的單位" * 20, "sub2": "很長的說明" * 30}, {"text": "4", "sub": "乙"}, {"text": "80", "sub": "丙"}], outcomes=[{"text": "很長的底欄" * 40}]))
expect("故意做壞：算式圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("locked", heads=["步驟級修改", "Epoch 邊界的流程"], nodes=[{"text": "best_skill.md"}, {"text": "受保護區塊：戰略筆記"}]))
expect("正確的受保護區塊圖通過程式 B", code == 0, out)
code, out = render(D("quad", nodes=[{"text": "很長的格子" * 12, "sub": "很長的說明" * 15} for _ in range(4)]))
expect("故意做壞：四格圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("locked", heads=["很長的來源" * 10, "乙"], nodes=[{"text": "文件" * 30}, {"text": "很長的區塊說明" * 30}]))
expect("故意做壞：受保護區塊圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

T3 = [{"text": "return-to-go", "sub": "還想拿多少分", "tone": "rtg"}, {"text": "state", "sub": "目前在哪", "tone": "state"}, {"text": "action", "sub": "往哪走", "tone": "action"}]
code, out = render(D("tokens", steps=[{"label": "第一步", "cells": T3}, {"label": "第二步", "cells": T3}, {"label": "第三步", "cells": T3}], more=True))
expect("正確的符號序列圖（三步加省略點）通過程式 B", code == 0, out)
code, out = render(D("tokens", steps=[{"label": "第一步", "cells": T3}, {"label": "第二步", "cells": T3[:2] + [{"text": "action", "sub": "蓋住", "tone": "mask"}]}],
                     outcomes=[{"text": "學到：還想拿到某個分數、在位置 A → 往右走"}]))
expect("正確的符號序列圖（蓋住一格＋底欄）通過程式 B", code == 0, out)
code, out = render(D("tokens", steps=[{"label": "第一步", "cells": [{"text": "很長的符號名稱" * 8, "sub": "很長的說明" * 12, "tone": "state"}] * 3} for _ in range(4)], more=True))
expect("故意做壞：符號序列圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("tokens", steps=[{"label": "第一步", "cells": [{"text": "這是一段沒有任何標點而且非常非常長的符號文字塞不進格子", "tone": "state"}] * 3}]))
expect("故意做壞：符號格的文字塞不進框 → 程式 B 抓得到", code != 0, out)

# links（左右兩排節點之間的連線）與 hops（幾跳才到答案），2026-10-24
LL = [{"text": "一個事件", "sub": "一句保留完整語意的話"}]
LR = [{"text": n} for n in ("實體甲", "實體乙", "實體丙", "實體丁", "實體戊")]
code, out = render(D("links", heads=["事件", "實體"], nodes=LL, outcomes=LR, edges=[[0, i] for i in range(5)]))
expect("正確的連線圖（一個事件連五個實體）通過程式 B", code == 0, out)
code, out = render(D("links", heads=["事件", "實體"], nodes=[{"text": "事件一"}, {"text": "事件二", "emph": True}, {"text": "事件三"}], outcomes=[{"text": "實體甲"}, {"text": "實體乙", "emph": True}, {"text": "實體丙"}],
                     edges=[[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]], hot=[[0, 1], [1, 1]]))
expect("正確的連線圖（多對多、共用實體畫金線）通過程式 B", code == 0, out)
code, out = render(D("links", nodes=LL, outcomes=LR, edges=[[0, 9]]))
expect("故意做壞：連線指到不存在的節點 → 報錯", code != 0 and "超出節點範圍" in out, out)
code, out = render(D("links", nodes=LL, outcomes=LR, edges=[[0, 0]], hot=[[0, 1]]))
expect("故意做壞：hot 不是 edges 的子集 → 報錯", code != 0 and "子集" in out, out)
code, out = render(D("links", nodes=[{"text": "很長的事件" * 20, "sub": "很長的說明" * 20}], outcomes=[{"text": "很長的實體" * 20, "sub": "很長的說明" * 20}] * 6, edges=[[0, 0]]))
expect("故意做壞：連線圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("hops", heads=["問題", "答案"], nodes=[{"text": "二元圖譜要跳 4 次", "hops": 4}, {"text": "SAG 只跳 1 次", "hops": 1}]))
expect("正確的幾跳圖（4 跳對 1 跳）通過程式 B", code == 0, out)
code, out = render(D("hops", nodes=[{"text": "二元圖譜要跳 4 次", "hops": 3}, {"text": "SAG 只跳 1 次", "hops": 1}]))
expect("故意做壞：圖上寫的跳數與箭頭數不符 → 報錯", code != 0 and "箭頭數" in out, out)
code, out = render(D("hops", nodes=[{"text": "很長的說明" * 30, "sub": "很長的小字" * 30, "hops": 4}] * 3))
expect("故意做壞：幾跳圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

# bubble（一個大泡泡圈住好幾個東西）與 drift（一路偏掉的路徑），2026-10-24
BI = [{"text": n} for n in ("Facebook", "2014年", "WhatsApp", "馬克·祖克柏", "揚·庫姆")]
code, out = render(D("bubble", heads=["一般的邊", "超邊"], nodes=[{"text": "只連兩個節點"}, {"text": "一條就圈住任意數量的節點", "sub": "例：一個事件綁五個實體"}], outcomes=BI))
expect("正確的泡泡圖（一個泡泡圈五個實體）通過程式 B", code == 0, out)
code, out = render(D("bubble", heads=["左", "右"], nodes=[{"text": "甲"}, {"text": "乙"}], outcomes=[{"text": "只有一個"}]))
expect("故意做壞：泡泡裡只有 1 個項目 → 報錯", code != 0 and "2～8" in out, out)
code, out = render(D("bubble", heads=["左", "右"], nodes=[{"text": "甲"}, {"text": "乙"}], outcomes=[{"text": "很長的實體名稱" * 6}, {"text": "乙"}]))
expect("故意做壞：泡泡裡的項目太長放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("bubble", heads=["左", "右"], nodes=[{"text": "很長的說明" * 40, "sub": "很長的小字" * 40}, {"text": "乙" * 200}], outcomes=BI))
expect("故意做壞：泡泡圖的說明太長放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("drift", heads=["問題", "第一步", "第二步", "第三步", "答案"], nodes=[{"text": "正確的推理鏈"}, {"text": "第一步偏一點", "sub": "後面每一步都在錯的基礎上繼續"}]))
expect("正確的偏移路徑圖通過程式 B", code == 0, out)
code, out = render(D("drift", heads=["問題", "答案"], nodes=[{"text": "正確"}, {"text": "實際"}]))
expect("故意做壞：偏移路徑只有 2 站 → 報錯", code != 0 and "3～6" in out, out)
code, out = render(D("drift", heads=["問題", "第一步", "答案"], nodes=[{"text": "很長的說明" * 60}, {"text": "很長的說明" * 60, "sub": "很長的小字" * 60}]))
expect("故意做壞：偏移路徑圖的說明太長放不下 → 報錯", code != 0 and "放不下" in out, out)
# ingest（兩段式架構圖），2026-10-24
ING = dict(heads=["線下：上傳文件時", "線上：使用者發問時"], nodes=[{"text": "chunk"}, {"text": "事件：一對一"}, {"text": "實體：多對多"}, {"text": "資料庫"}],
           outcomes=[{"text": "使用者發問"}, {"text": "配對", "sub": "把共用實體的，事件配起來"}, {"text": "局部的圖", "sub": "查完就丟"}])
code, out = render(D("ingest", **ING))
expect("正確的兩段式架構圖通過程式 B", code == 0, out)
code, out = render(D("ingest", **{**ING, "nodes": ING["nodes"][:3]}))
expect("故意做壞：架構圖上段只有 3 欄 → 報錯", code != 0 and "4 個" in out, out)
code, out = render(D("ingest", **{**ING, "outcomes": [{"text": "很長的步驟說明" * 12, "sub": "很長的小字" * 30}] * 3}))
expect("故意做壞：架構圖下段的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

# 2026-10-25 新增（SAG 第 2 則）：roles／embed／online／gate／concat／joint／rails
ROLES = [{"text": "資料庫", "sub": "確定", "sub2": "精確比對，一步接一步串下去。", "icon": "db"}, {"text": "向量庫", "sub": "模糊", "sub2": "別名、錯字也找得到。", "icon": "vec"}, {"text": "大模型", "sub": "判斷", "sub2": "只看縮小後的候選。", "icon": "llm"}]
code, out = render(D("roles", nodes=ROLES))
expect("正確的三列角色卡通過程式 B", code == 0, out)
code, out = render(D("roles", nodes=[{**n, "sub2": "很長的說明" * 40} for n in ROLES]))
expect("故意做壞：角色卡的說明太長放不下 → 報錯", code != 0 and "放不下" in out, out)
EMB = dict(heads=["精確", "向量"], nodes=[{"text": "甲＝甲", "sub": "確定相等", "ok": True}, {"text": "甲＝乙？", "sub": "沒辦法判斷", "ok": False}],
           outcomes=[{"text": "甲"}, {"text": "乙", "sub": "別名也找得到"}, {"text": "丙", "sub": "錯字也找得到"}])
code, out = render(D("embed", **EMB))
expect("正確的精確比對 vs 向量空間圖通過程式 B", code == 0, out)
code, out = render(D("embed", **{**EMB, "outcomes": EMB["outcomes"][:2]}))
expect("故意做壞：向量空間只有 2 個點 → 報錯", code != 0 and "3 個點" in out, out)
code, out = render(D("embed", **{**EMB, "nodes": [{"text": "很長的比對說明" * 20, "sub": "很長的小字" * 20, "ok": True}] * 2}))
expect("故意做壞：比對列的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
ONL = dict(heads=["發問", "10 個結果"], nodes=[{"text": "第一路", "sub": "先抽"}, {"text": "第二路", "sub": "整句"}],
           outcomes=[{"text": "擴展", "sub": "沿著實體撈"}, {"text": "精選", "sub": "挑 5 個"}, {"text": "直接", "sub": "挑 5 個"}])
code, out = render(D("online", **ONL))
expect("正確的線上檢索路線圖通過程式 B", code == 0, out)
code, out = render(D("online", **{**ONL, "outcomes": [{"text": "很長的步驟說明" * 12, "sub": "很長的小字" * 30}] * 3}))
expect("故意做壞：路線圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("gate", count=50, nodes=[{"text": "上游", "sub": "來多少先排在這裡"}, {"text": "只留前 50 名", "sub": "下游控制得住"}]))
expect("正確的水庫閘門圖通過程式 B（名額數字在閘門上）", code == 0, out)
code, out = render(D("gate", count=50, nodes=[{"text": "很長的上游說明" * 20, "sub": "很長的小字" * 20}, {"text": "下游"}]))
expect("故意做壞：閘門圖的標題太長放不下 → 報錯", code != 0 and "放不下" in out, out)
CAT = dict(heads=["左路", "右路"], nodes=[{"text": "兩路各挑 5 個"}, {"text": "合成 10 個", "sub": "交給下一步"}])
code, out = render(D("concat", **CAT))
expect("正確的兩路合成一排圖通過程式 B", code == 0, out)
code, out = render(D("concat", **{**CAT, "nodes": [{"text": "很長的說明" * 60}, {"text": "很長的結果" * 60, "sub": "很長的小字" * 60}]}))
expect("故意做壞：合成圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
JNT = dict(heads=["逐一", "一起"], nodes=[{"text": "一個一個打分", "sub": "例：各拿一個分數", "sub2": "看不到互補"}, {"text": "一起評估", "sub": "例：合起來才答得出", "sub2": "看得到互補"}])
code, out = render(D("joint", **JNT))
expect("正確的逐一打分 vs 一起評估圖通過程式 B", code == 0, out)
code, out = render(D("joint", **{**JNT, "nodes": [{"text": "很長的說明" * 30, "sub": "很長的例子" * 30, "sub2": "很長的結論" * 30}] * 2}))
expect("故意做壞：打分圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
RAI = dict(heads=["A 路", "B 路"], nodes=[{"text": "用實體", "sub": "先抽再撈"}, {"text": "用整句", "sub": "直接撈"}], outcomes=[{"text": "取聯集、去重"}])
code, out = render(D("rails", **RAI))
expect("正確的兩條軌道合併圖通過程式 B", code == 0, out)
code, out = render(D("rails", **{**RAI, "nodes": [{"text": "很長的做法" * 20, "sub": "很長的小字" * 30}] * 2}))
expect("故意做壞：軌道圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

# 2026-10-26 新增（SAG 第 3 則）：scoreboard／leak／amplify，以及 hops 的 fade 與 shortcut
SCO = dict(heads=["R@2", "R@5"], outcomes=[{"text": "甲"}, {"text": "乙"}], nodes=[{"text": "資料一", "sub": "說明", "emph": True}, {"text": "資料二"}],
           cells=[[["64.1", "49.5"], ["80.0", "65.1"]], [["82.3", "76.6"], ["88.0", "90.4"]]])
code, out = render(D("scoreboard", **SCO))
expect("正確的戰績表通過程式 B（含深色值小於淺色值的虛線格）", code == 0, out)
code, out = render(D("scoreboard", **{**SCO, "cells": SCO["cells"][:1]}))
expect("故意做壞：戰績表的 cells 列數與 nodes 不符 → 報錯", code != 0 and "cells" in out, out)
code, out = render(D("scoreboard", **{**SCO, "outcomes": SCO["outcomes"][:1]}))
expect("故意做壞：戰績表的圖例只有 1 個 → 報錯", code != 0 and "圖例" in out, out)
code, out = render(D("scoreboard", **{**SCO, "nodes": [{"text": "很長的資料集名稱" * 8, "sub": "很長的說明" * 20}] * 2}))
expect("故意做壞：戰績表的列標籤太長放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("bubble", chain=True, heads=["拆開", "原本"], nodes=[{"text": "只連兩個點"}, {"text": "一次綁住三個"}], outcomes=[{"text": "甲"}, {"text": "乙"}, {"text": "丙"}]))
expect("正確的泡泡圖（chain：左邊畫一串只連兩點的邊並標名字）通過程式 B", code == 0, out)
LEK = dict(heads=["剪枝"], nodes=[{"text": "走很多跳", "sub": "每跳都剪"}, {"text": "一次到位", "sub": "少剪"}])
code, out = render(D("leak", **LEK))
expect("正確的每跳都漏一些圖通過程式 B", code == 0, out)
code, out = render(D("leak", **{**LEK, "nodes": [{"text": "很長的說明" * 40, "sub": "很長的小字" * 40}] * 2}))
expect("故意做壞：漏斗式圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
AMP = dict(heads=["起點", "終點"], nodes=[{"text": "甲", "sub": "乙"}, {"text": "丙", "sub": "丁"}], outcomes=[{"text": "精確比對"}])
code, out = render(D("amplify", **AMP))
expect("正確的誤差放大圖通過程式 B", code == 0, out)
code, out = render(D("amplify", **{**AMP, "nodes": [{"text": "很長的說明" * 40, "sub": "很長的小字" * 40}] * 2}))
expect("故意做壞：誤差放大圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
HOP = dict(fade=True, heads=["問題", "答案"], nodes=[{"text": "長的", "sub": "說明", "sub2": "被擋掉的捷徑", "shortcut": True, "hops": 4}, {"text": "短的", "hops": 2}])
code, out = render(D("hops", **HOP))
expect("正確的跳數圖（漸淡箭頭與被叉掉的捷徑）通過程式 B", code == 0, out)
code, out = render(D("hops", **{**HOP, "nodes": [{**HOP["nodes"][0], "sub2": ""}, HOP["nodes"][1]]}))
expect("故意做壞：捷徑沒有標籤 → 報錯", code != 0 and "sub2" in out, out)
code, out = render(D("hops", **{**HOP, "nodes": [{**HOP["nodes"][0], "text": "共 5 跳"}, HOP["nodes"][1]]}))
expect("故意做壞：圖上寫 5 跳、箭頭畫 4 條 → 報錯", code != 0 and "不符" in out, out)

# 2026-10-27 新增（SAG 第 4 則）：receipt／squeeze／alias／handoff／mismatch／ledger
REC = dict(heads=["帳單", "換來的"], nodes=[{"text": "甲", "sub": "說明"}, {"text": "乙"}, {"text": "丙"}], outcomes=[{"text": "簡潔"}, {"text": "快"}])
code, out = render(D("receipt", **REC))
expect("正確的帳單圖通過程式 B", code == 0, out)
code, out = render(D("receipt", **{**REC, "nodes": REC["nodes"][:1]}))
expect("故意做壞：帳單只有 1 個品項 → 報錯", code != 0 and "receipt" in out, out)
code, out = render(D("receipt", **{**REC, "nodes": [{"text": "很長的品項" * 20, "sub": "很長的小字" * 30}] * 4}))
expect("故意做壞：帳單字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
SQZ = dict(heads=["越像", "越不像", "名額線"], nodes=[{"text": "排隊"}, {"text": "橋樑", "sub": "說明"}], outcomes=[{"text": "問題"}, {"text": "答案"}])
code, out = render(D("squeeze", **SQZ))
expect("正確的名額線圖通過程式 B", code == 0, out)
code, out = render(D("squeeze", **{**SQZ, "nodes": [{"text": "很長的說明" * 40}, {"text": "橋樑", "sub": "很長的小字" * 40}]}))
expect("故意做壞：名額線圖字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
ALI = dict(heads=["傳統", "SAG"], outcomes=[{"text": "甲"}, {"text": "乙"}, {"text": "丙"}], nodes=[{"text": "合成一個", "sub": "說明"}, {"text": "各算各的", "sub": "說明"}])
code, out = render(D("alias", **ALI))
expect("正確的別名對齊圖通過程式 B", code == 0, out)
code, out = render(D("alias", **{**ALI, "outcomes": ALI["outcomes"][:2]}))
expect("故意做壞：別名對齊圖只有 2 種寫法 → 報錯", code != 0 and "alias" in out, out)
HAN = dict(heads=["線下", "線上", "推遲"], nodes=[{"text": "對齊", "sub": "線下不做"}, {"text": "模糊匹配"}], outcomes=[{"text": "寫入快"}])
code, out = render(D("handoff", **HAN))
expect("正確的線下搬到線上圖通過程式 B", code == 0, out)
code, out = render(D("handoff", **{**HAN, "outcomes": [{"text": "很長的好處" * 60}]}))
expect("故意做壞：搬家圖的好處太長放不下 → 報錯", code != 0 and "放不下" in out, out)
MIS = dict(heads=["一樣", "不同", "沒到門檻"], nodes=[{"text": "Meta", "sub": "共用"}, {"text": "Facebook", "sub": "斷開"}], outcomes=[{"text": "事件 A", "sub": "文件 1"}, {"text": "事件 B", "sub": "文件 2"}])
code, out = render(D("mismatch", **MIS))
expect("正確的寫法不同圖通過程式 B", code == 0, out)
code, out = render(D("mismatch", **{**MIS, "nodes": [{"text": "Meta", "sub": "很長的說明" * 40}, {"text": "Facebook", "sub": "很長的說明" * 40}]}))
expect("故意做壞：寫法不同圖的字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
LED = dict(heads=["時間"], nodes=[{"text": "舊的"}, {"text": "新的", "new": True}], outcomes=[{"text": "舊的改不了"}])
code, out = render(D("ledger", **LED))
expect("正確的記錄簿圖通過程式 B", code == 0, out)
LEDQ = {**LED, "nodes": [{"text": "舊的", "ask": True}, {"text": "中間的"}, {"text": "新的", "new": True, "ask": True}]}
code, out = render(D("ledger", **LEDQ))
expect("正確的記錄簿圖（有 ask 的「？」標記）通過程式 B", code == 0, out)
code, out = render(D("ledger", **{**LEDQ, "nodes": [{"text": "很長的紀錄" * 12, "ask": True}] * 4}))
expect("故意做壞：有 ask 的記錄簿字太多放不下 → 報錯", code != 0 and "放不下" in out, out)
code, out = render(D("ledger", **{**LED, "nodes": LED["nodes"][:1]}))
expect("故意做壞：記錄簿只有 1 筆 → 報錯", code != 0 and "ledger" in out, out)
code, out = render(D("ledger", **{**LED, "nodes": [{"text": "很長的紀錄" * 20}] * 5}))
expect("故意做壞：記錄簿字太多放不下 → 報錯", code != 0 and "放不下" in out, out)

# 2026-10-28 新增（Claude Code 第 1 則）：transcript／oneloop／intercept／dial／lanes／layers
TR = dict(heads=["假設的例子"], nodes=[{"text": "修好測試", "tone": "prompt"}, {"text": "Bash　跑測試", "tone": "tool"}, {"text": "stderr：沒過", "tone": "fail", "feeds": True}, {"text": "Edit　改程式", "tone": "tool"}, {"text": "通過", "tone": "ok"}], outcomes=[{"text": "下一輪的輸入"}])
code, out = render(D("transcript", **TR))
expect("正確的對話紀錄圖通過程式 B", code == 0, out)
code, out = render(D("transcript", **{**TR, "nodes": TR["nodes"][:2]}))
expect("故意做壞：對話紀錄只有 2 列 → 報錯", code != 0 and "transcript" in out, out)
code, out = render(D("transcript", **{**TR, "nodes": [{"text": "很長的一列" * 30, "tone": "tool"}] * 7}))
expect("故意做壞：對話紀錄字太多（超出視窗）→ 抓得到", code != 0, out)
OL = dict(heads=["模型自己推理，驅動每一輪"], nodes=[{"text": "規劃"}, {"text": "執行"}], outcomes=[{"text": "規劃模組"}, {"text": "執行模組"}])
code, out = render(D("oneloop", **OL))
expect("正確的單一迴圈圖通過程式 B", code == 0, out)
code, out = render(D("oneloop", **{**OL, "outcomes": [{"text": "很長很長很長很長的模組名稱" * 3}, {"text": "執行模組"}]}))
expect("故意做壞：單一迴圈圖的虛線框字太長 → 抓得到", code != 0, out)
IC = dict(heads=["只用文字說", "發出工具呼叫", "攔截點", "檔案"], nodes=[{"text": "「我要改檔案了」"}, {"text": "Edit　改檔案"}], outcomes=[{"text": "權限檢查"}, {"text": "記錄 log"}])
code, out = render(D("intercept", **IC))
expect("正確的攔截點圖通過程式 B", code == 0, out)
code, out = render(D("intercept", **{**IC, "outcomes": IC["outcomes"][:1]}))
expect("故意做壞：攔截點只有 1 個檢查項目 → 報錯", code != 0 and "intercept" in out, out)
DL = dict(heads=["一路可調的刻度"], nodes=[{"text": "你"}, {"text": "模型"}])
code, out = render(D("dial", **DL))
expect("正確的刻度盤圖通過程式 B", code == 0, out)
code, out = render(D("dial", **{**DL, "heads": ["一路可調的刻度", "管得嚴", "放得寬"]}))
expect("正確的刻度盤圖（兩端有標籤）通過程式 B", code == 0, out)
code, out = render(D("dial", **{**DL, "heads": ["很長的說明" * 80]}))
expect("故意做壞：刻度盤說明太長放不下 → 報錯", code != 0 and "放不下" in out, out)
LN = dict(heads=["代價低", "較難復原"], nodes=[{"text": "做錯了能救回來嗎？"}, {"text": "讀取檔案"}, {"text": "執行測試"}], outcomes=[{"text": "自動核准"}, {"text": "先問你"}])
code, out = render(D("lanes", **LN))
expect("正確的兩條通道圖通過程式 B", code == 0, out)
code, out = render(D("lanes", **{**LN, "nodes": [{"text": "問題"}] + [{"text": "項目"}] * 12}))
expect("故意做壞：兩條通道的項目太多放不下 → 報錯", code != 0 and "放不下" in out, out)
LY = dict(heads=["防線一", "防線二", "容器外"], nodes=[{"text": "工作目錄"}, {"text": "錯誤的指令"}], outcomes=[{"text": "先問你"}])
code, out = render(D("layers", **LY))
expect("正確的兩道防線圖通過程式 B", code == 0, out)
code, out = render(D("layers", **{**LY, "heads": ["防線一", "防線二", "很長很長很長很長很長很長的容器外說明" * 3]}))
expect("故意做壞：兩道防線的容器外說明太長 → 抓得到", code != 0, out)

TN = dict(heads=["工具呼叫", "對話紀錄"], nodes=[{"text": "模型給出回應", "sub": "最終答案或工具呼叫"}, {"text": "權限檢查", "sub": "需要確認的先問你"}, {"text": "執行的結果"}, {"text": "拒絕的回饋"}], outcomes=[{"text": "最終答案：結束"}, {"text": "你同意：執行"}, {"text": "你拒絕：不執行"}], loop="紀錄帶進下一輪")
code, out = render(D("turn", **TN))
expect("正確的一輪流程圖通過程式 B", code == 0, out)
code, out = render(D("turn", **{**TN, "outcomes": TN["outcomes"][:2]}))
expect("故意做壞：一輪流程圖少一個結果 → 報錯", code != 0, out)
code, out = render(D("turn", **{**TN, "loop": "很長的說明" * 60}))
expect("故意做壞：一輪流程圖底部說明太長放不下 → 報錯", code != 0 and "放不下" in out, out)

import sys
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))
import diagrams as DG
o = DG.drift_offsets(5, 200)
expect("drift_offsets：起點 0、單調遞增、終點 = dmax", o[0] == 0 and all(b > a for a, b in zip(o, o[1:])) and abs(o[-1] - 200) < 1e-9, str(o))

print("\n全部通過" if not fails else f"\n{len(fails)} 項失敗")
raise SystemExit(1 if fails else 0)
