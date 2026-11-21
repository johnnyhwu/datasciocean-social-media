#!/usr/bin/env python3
"""insights.py 回歸測試：不連網。用假的 client 確認
1. paging 網址裡的 token 不會進輸出（2026-11-21 實際外洩過一次）
2. 指標解析（values / total_value）
3. experiments.md 的 action id 會帶進快照
4. 故意做壞：輸出裡殘留 token 樣式 → safe_dump 拒絕寫出
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))
import insights as I  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


TOK_IG = "IGAA" + "x" * 40
TOK_TH = "THAA" + "y" * 40


class FakeIG:
    def _uid(self):
        return "111"

    def _call(self, method, path, params, retry=True):
        assert method == "GET"
        if path == "111":
            return {"followers_count": 1700, "id": "111"}
        return {"data": [{"name": "views", "values": [{"value": 99}]}, {"name": "follows", "values": [{"value": 1}]}],
                "paging": {"next": f"https://graph.instagram.com/x?access_token={TOK_IG}"}}


class FakeTH:
    def _uid(self):
        return "222"

    def _call(self, method, path, params, retry=True):
        assert method == "GET"
        if path.endswith("threads_insights"):
            return {"data": [{"name": "followers_count", "total_value": {"value": 600}}],
                    "paging": {"previous": f"https://graph.threads.net/v1.0/222/threads_insights?access_token={TOK_TH}"}}
        return {"data": [{"name": "views", "values": [{"value": 1234}]}, {"name": "shares", "values": [{"value": 7}]}],
                "paging": {"next": f"https://graph.threads.net/x?access_token={TOK_TH}"}}


def main():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "state").mkdir()
        (d / "state" / "demo-concept.yaml").write_text(
            "concept: demo-concept\nposts:\n- format: ig_carousel\n  series_id: demo\n  url: https://ig/p/1\n  published_at: 2026-11-01T00:00:00+0000\n  hook_type: 讀者疑問\n"
            "- format: threads_thread\n  series_id: demo\n  url: https://th/p/1\n  published_at: 2026-11-01T00:05:00+0000\n  hook_type: 讀者疑問\n", encoding="utf-8")
        (d / "state" / "ig-publish-log.jsonl").write_text(json.dumps({"concept": "demo-concept", "media_id": "m1"}) + "\n{bad json\n", encoding="utf-8")
        (d / "state" / "threads-publish-log.jsonl").write_text(json.dumps({"concept": "demo-concept", "root_id": "r1"}) + "\n" + json.dumps({"root_id": "test-no-concept"}) + "\n", encoding="utf-8")
        (d / "growth").mkdir()
        (d / "growth" / "experiments.md").write_text("# x\n\n## 套用紀錄\n\n| 觀念 | 發布日 | actions | 做了什麼 |\n|---|---|---|---|\n| `demo-concept` | 2026-11-01 | A1, A3 | 測試 |\n\n## 判讀紀錄\n\n| 2026-11-21 | x | A9 | 1 | y | z |\n", encoding="utf-8")
        I.ROOT, I.STATE, I.GROWTH, I.SNAP, I.EXPERIMENTS = d, d / "state", d / "growth", d / "growth" / "snapshots", d / "growth" / "experiments.md"
        import datetime as dt
        snap = I.pull(FakeIG(), FakeTH(), now=dt.datetime(2026, 11, 11, tzinfo=dt.timezone.utc))
        text = I.safe_dump(snap, [TOK_IG, TOK_TH])
        check("輸出不含 IG token", TOK_IG not in text)
        check("輸出不含 Threads token", TOK_TH not in text)
        check("輸出沒有 paging", "paging" not in text and "access_token" not in text)
        p = snap["posts"][0]
        check("IG 指標解析", p["ig"] == {"views": 99, "follows": 1})
        check("Threads 指標解析", p["th"] == {"views": 1234, "shares": 7})
        check("帳號追蹤數（IG 欄位、Threads total_value）", snap["account"] == {"ig_followers": 1700, "th_followers": 600})
        check("發布天數", p["ig_age_days"] == 10.0)
        check("action id 帶進快照（判讀紀錄的 A9 不算）", p["experiments"] == ["A1", "A3"])
        check("沒有觀念的測試發文不列入", I.media_ids()[1] == {"demo-concept": "r1"})
        tbl = I.table(json.loads(text))
        check("表格列出貼文與 action", "demo-concept" in tbl and "A1,A3" in tbl)
        # 故意做壞：有 token 樣式但不是已知 token
        bad = {"x": "THAA" + "z" * 30}
        check("scrub 會抹掉未知但像 token 的字串", "THAA" not in I.scrub(json.dumps(bad), []))
        try:
            I.safe_dump({"x": TOK_IG.lower().replace("igaa", "IGAA")}, [])
            check("safe_dump 抹掉格式相符的 token", True)
        except RuntimeError:
            check("safe_dump 抹掉格式相符的 token", False)
    print("全部通過" if not FAILS else f"{len(FAILS)} 項失敗")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
