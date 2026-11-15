# 進度：prompt-repetition-causal-bottleneck-and-fix（系列第 1 則）

## 現況（2026-11-15）
- 人 review：第 2、3 則沒問題；第 1 則改第 2 張（「回頭拿到」說清楚）與第 8 張（CoT／雙向注意力也修得好但各有代價，表頭改好處／代價），Threads 正文同步改。程式 A、B 過；忠實者 r5（slide02、slide08、threads.body）與讀者 r3（第 2、8 張）都通過，已 --mark。人 2026-11-15 確認「都沒問題了」：已 state.py ready --hook-accepted（兩格式），series.md 已 members_locked。2026-11-15 已發布 IG 與 Threads（網址在 state/）。這則完成。

## 前次現況（2026-11-11）
- spec 12 張；程式 A、B 通過；審查全過：忠實者 r1→r4（r4 只審第 8 張）、讀者 r1→r2、編輯 r1；`spec_diff.py --mark` 已記通過版本。
- hook A（反直覺斷言）。新圖型：ambig、peek、blend、repeat、catchup、variants（tests/test_diagrams.py 有正案與壞案）。
- 未採用的建議：編輯說封面「不是 X，是 Y」像 AI 句型——hook 是反差來源，保留；路線圖頁保留（人的回饋要求有路線圖）。
- 等人決定：無。下一步：等第 3 則審查完，三則一起交成品。

## 歷史
- 2026-11-11：建系列檔、哲學、模板；render.py 加 echo 風格；寫 spec；排版調整（第 8 張由 table 改 matrix、拿掉 c10 與 Claude 例外以免放不下）。
