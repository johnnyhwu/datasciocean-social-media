"""Threads 發佈（threads_api.py、threads_publish.py）的回歸測試。全部用假的 transport，**不連網、不發文**。

「故意做壞」：超過 500 字、圖片網址抓不到、已發布過、沒有 token、串文發到一半失敗（必須能從下一則繼續、不重複發）、
內容在發到一半後被改、錯誤訊息夾帶 token 或 app secret，都必須被擋下或正確處理。
用法（repo 根目錄）：uv run python tests/test_threads_publish.py
"""
import datetime as dt
import io
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/make-social-post/scripts"))

from PIL import Image  # noqa: E402

import hosting  # noqa: E402
import ig_api  # noqa: E402
import threads_api as TA  # noqa: E402
import threads_publish as TP  # noqa: E402

TOKEN, SECRET = "THAAsecretTOKEN123", "appSECRET456"
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        FAILS.append(name)


class Fake:
    def __init__(self, fail_on_create=None, statuses=None):
        self.calls, self.c, self.p = [], 0, 0
        self.fail_on_create, self.statuses = fail_on_create, list(statuses or [])
        self.creates = 0

    def __call__(self, method, url, params):
        self.calls.append((method, url, dict(params)))
        path = url.split("/v1.0/", 1)[-1]
        if method == "DELETE":
            return 200, {"success": True, "deleted_id": path}
        if path.endswith("/threads_publish"):
            self.p += 1
            return 200, {"id": f"P{self.p}"}
        if path.endswith("/threads"):
            self.creates += 1
            if self.fail_on_create == self.creates:
                return 400, {"error": {"code": 100, "message": f"bad request access_token={TOKEN}"}}
            self.c += 1
            return 200, {"id": f"C{self.c}"}
        if path.startswith("C"):
            return 200, {"status": self.statuses.pop(0) if self.statuses else "FINISHED"}
        if path.startswith("P"):
            return 200, {"permalink": "https://www.threads.net/@x/post/ABC", "timestamp": "2026-10-07T08:00:00+0000"}
        if path.endswith("threads_publishing_limit"):
            return 200, {"data": [{"quota_usage": 1, "config": {"quota_total": 250}}]}
        return 200, {}


class H(hosting.Host):
    def upload(self, p):
        return f"https://example.test/{Path(p).parent.parent.parent.name}/{Path(p).name}"


def opener_ok(req, timeout=0):
    class R:
        headers = {"Content-Type": "image/jpeg"}
        def __enter__(s): return s
        def __exit__(s, *a): return False
        def read(s, n=-1): return b"\xff\xd8\xff" + b"0" * 50
    return R()


def opener_404(req, timeout=0):
    raise hosting.urllib.error.HTTPError(req.full_url, 404, "nf", {}, io.BytesIO(b""))


def fake_pack(base: Path, slides=(3, 4), text="正文"):
    pack = base / "out" / "s" / "fake-thread"
    (pack / "_build").mkdir(parents=True)
    (pack / "ig" / "jpg").mkdir(parents=True)
    spec = {"concept": "fake-thread", "series": "s", "lang": "zh-TW", "hook": {"style": "反直覺斷言"}, "slides": [],
            "threads": {"body": {"text": text, "refs": ["結構"]},
                        "items": [{"slide": n, "text": f"第 {n} 張的串文", "refs": ["結構"]} for n in slides],
                        "last": {"text": "最後一則\n文章：example.com", "refs": ["結構"], "link": "https://example.com/post/"}},
            "caption": {"first": "x", "nav": "y", "hashtags": []}}
    (pack / "_build" / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    for n in slides:
        Image.new("RGB", (1080, 1350), (240, 224, 192)).save(pack / "ig" / "jpg" / f"{n:02d}.jpg", "JPEG", quality=90)
    return pack


def kinds(fk):
    return [("create" if x[1].endswith("/threads") else "publish") for x in fk.calls if x[0] == "POST"]


def client(fk, sleeps=None):
    return TA.ThreadsClient(TOKEN, "U1", transport=fk, sleep=(sleeps.append if sleeps is not None else (lambda s: None)))


def main():
    env = {}
    recs, logs = [], []
    TP.ST.record = lambda *a: recs.append(a)
    TP.log_publish = lambda e, path=None: logs.append(e)
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        check("emoji 以 UTF-8 位元組計、一般字元算 1", TP.threads_len("好") == 1 and TP.threads_len("😀") == 4)
        pack = fake_pack(tmp / "a")
        plan = TP.plan_thread(pack, H())
        check("計畫：正文(TEXT) → 2 則附圖(IMAGE) → 最後一則(TEXT 附連結)",
              [p["media_type"] for p in plan["posts"]] == ["TEXT", "IMAGE", "IMAGE", "TEXT"] and plan["posts"][-1]["link_attachment"] == "https://example.com/post/" and not plan["problems"], plan["problems"])
        fk = Fake()
        r = TP.publish_thread(pack, False, env, client(fk), H(), fetch=opener_ok)
        check("dry-run：沒有任何 POST，且 ok", r["ok"] and not [x for x in fk.calls if x[0] == "POST"], r.get("problems"))
        check("dry-run 輸出不含 token", TOKEN not in json.dumps(r, ensure_ascii=False))

        fk, sl = Fake(), []
        r = TP.publish_thread(pack, True, env, client(fk, sl), H(), fetch=opener_ok)
        creates = [x for x in fk.calls if x[0] == "POST" and x[1].endswith("/threads")]
        check("--confirm：4 則依序 create→publish", r["ok"] and kinds(fk) == ["create", "publish"] * 4, (kinds(fk), r.get("error")))
        check("第一則沒有 reply_to_id；之後每則回覆前一則的 id", "reply_to_id" not in creates[0][2] and [c[2]["reply_to_id"] for c in creates[1:]] == ["P1", "P2", "P3"], [c[2].get("reply_to_id") for c in creates])
        check("附圖的是 IMAGE + image_url；最後一則是 TEXT + link_attachment、沒有圖",
              creates[1][2]["media_type"] == "IMAGE" and creates[1][2]["image_url"].endswith("03.jpg") and creates[3][2]["link_attachment"] == "https://example.com/post/" and "image_url" not in creates[3][2])
        check("link_attachment 只出現在純文字貼文", all("link_attachment" not in c[2] for c in creates[:3]))
        check("每則發佈前先等約 30 秒", sl.count(30) == 4, sl)
        check("寫回 state（threads_thread）與紀錄，進度檔已刪除", len(recs) == 1 and recs[0][1] == "threads_thread" and logs and logs[-1]["post_ids"] == ["P1", "P2", "P3", "P4"] and not (pack / "_build" / TP.PROGRESS_NAME).exists())
        check("紀錄與 state 不含 token", TOKEN not in json.dumps(logs, ensure_ascii=False) + json.dumps(recs, ensure_ascii=False))

        # 發到一半失敗 → 從下一則繼續，不重複
        pack = fake_pack(tmp / "b")
        fk = Fake(fail_on_create=3)
        r = TP.publish_thread(pack, True, env, client(fk), H(), fetch=opener_ok)
        prog = TP.load_progress(pack)
        check("抓得到：第 3 則失敗 → 已發 2 則、進度檔留著、錯誤訊息不含 token",
              not r["ok"] and prog and prog["published"] == ["P1", "P2"] and TOKEN not in json.dumps(r, ensure_ascii=False), r.get("error"))
        fk2 = Fake(); fk2.p = 2; fk2.c = 2
        r2 = TP.publish_thread(pack, True, env, client(fk2), H(), fetch=opener_ok)
        creates2 = [x for x in fk2.calls if x[0] == "POST" and x[1].endswith("/threads")]
        check("重跑：只補第 3、4 則，第 3 則回覆 P2（不重複發前兩則）", r2["ok"] and len(creates2) == 2 and creates2[0][2]["reply_to_id"] == "P2", [c[2].get("reply_to_id") for c in creates2])

        # 發到一半內容被改 → 擋
        pack = fake_pack(tmp / "c")
        TP.publish_thread(pack, True, env, client(Fake(fail_on_create=3)), H(), fetch=opener_ok)
        sp = json.loads((pack / "_build" / "spec.json").read_text(encoding="utf-8"))
        sp["threads"]["body"]["text"] = "改過的正文"
        (pack / "_build" / "spec.json").write_text(json.dumps(sp, ensure_ascii=False), encoding="utf-8")
        fk = Fake()
        r = TP.publish_thread(pack, True, env, client(fk), H(), fetch=opener_ok)
        check("抓得到：發到一半後內容被改 → 不續發", not r["ok"] and not [x for x in fk.calls if x[0] == "POST"] and any("不一致" in p for p in r["problems"]))

        # rollback
        pack = fake_pack(tmp / "d")
        TP.publish_thread(pack, True, env, client(Fake(fail_on_create=3)), H(), fetch=opener_ok)
        fk = Fake()
        r = TP.rollback(pack, False, client(fk))
        check("rollback dry-run：列出由後往前要刪的 id，沒有 DELETE", r["will_delete"] == ["P2", "P1"] and not fk.calls)
        r = TP.rollback(pack, True, client(fk))
        check("rollback --confirm：由後往前 DELETE，並刪掉進度檔", r["ok"] and [x[1].rsplit("/", 1)[-1] for x in fk.calls if x[0] == "DELETE"] == ["P2", "P1"] and not (pack / "_build" / TP.PROGRESS_NAME).exists())

        # 整串發完後（進度檔已刪除）rollback 改讀發佈紀錄
        pack = fake_pack(tmp / "g")
        lg = tmp / "log.jsonl"
        lg.write_text(json.dumps({"concept": "other", "post_ids": ["X1"]}) + "\n" + json.dumps({"concept": "fake-thread", "post_ids": ["A1", "A2", "A3"]}) + "\n", encoding="utf-8")
        fk = Fake()
        r = TP.rollback(pack, False, client(fk), log_path=lg)
        check("rollback：沒有進度檔時讀發佈紀錄，只列該貼文的 id（由後往前）", r["ok"] and r["will_delete"] == ["A3", "A2", "A1"] and "發佈紀錄" in r["source"], r)
        r = TP.rollback(pack, True, client(fk), log_path=lg)
        check("rollback --confirm（紀錄來源）：由後往前 DELETE", r["ok"] and [x[1].rsplit("/", 1)[-1] for x in fk.calls if x[0] == "DELETE"] == ["A3", "A2", "A1"])
        r = TP.rollback(fake_pack(tmp / "h"), False, client(Fake()), log_path=tmp / "none.jsonl")
        check("rollback：進度檔與紀錄都沒有 → 說明沒有東西可撤回，不當機", r["ok"] and "沒有可撤回" in r["note"])
        # 沒有 threads_delete 權限
        def deny(m, u, p): return 403, {"error": {"code": 10, "message": "Application does not have permission for this action"}}
        r = TP.rollback(fake_pack(tmp / "i"), True, TA.ThreadsClient(TOKEN, "U1", transport=deny), log_path=lg)
        check("抓得到：沒有 threads_delete 權限 → 回報錯誤與提示，不假裝成功", not r["ok"] and r["deleted"] == [] and "threads_delete" in r["hint"])

        # 各種擋下
        pack = fake_pack(tmp / "e", text="字" * 501)
        fk = Fake()
        r = TP.publish_thread(pack, True, env, client(fk), H(), fetch=opener_ok)
        check("抓得到：正文超過 500 字 → 不發", not r["ok"] and not [x for x in fk.calls if x[0] == "POST"] and any("超過 500" in p for p in r["problems"]))
        pack = fake_pack(tmp / "f")
        fk = Fake()
        r = TP.publish_thread(pack, True, env, client(fk), H(), fetch=opener_404)
        check("抓得到：圖片網址抓不到 → 不發", not r["ok"] and not [x for x in fk.calls if x[0] == "POST"])
        orig = TP.ST.load
        TP.ST.load = lambda c: {"formats": {"threads_thread": {"status": "published"}}, "posts": []}
        r = TP.publish_thread(pack, True, env, client(Fake()), H(), fetch=opener_ok)
        check("抓得到：已發布過 → 不再發", not r["ok"] and any("已發布過" in p for p in r["problems"]))
        TP.ST.load = orig
        r = TP.publish_thread(pack, True, env, None, H(), fetch=opener_ok)
        check("沒有 token → 不發、不當機", not r["ok"] and "沒有 token" in r.get("error", ""))
        (pack / "ig" / "jpg" / "04.jpg").unlink()
        r = TP.publish_thread(pack, False, env, None, H(), fetch=opener_ok)
        check("抓得到：缺少某張 JPEG → 列為問題", not r["ok"] and any("JPEG 不存在" in p for p in r["problems"]))

        # 客戶端
        c = client(Fake(statuses=["IN_PROGRESS", "FINISHED"]), [])
        check("wait_ready：IN_PROGRESS 之後 FINISHED 通過", c.wait_ready("C1") == "FINISHED")
        c = client(Fake(statuses=["ERROR"]), [])
        try:
            c.wait_ready("C1"); caught = False
        except ig_api.IGError:
            caught = True
        check("抓得到：container 狀態 ERROR → 失敗", caught)
        calls = []
        def tr(m, u, p):
            calls.append((m, u, p)); return 400, {"error": {"message": f"x {SECRET} {TOKEN} client_secret={SECRET}", "code": 190}}
        c = TA.ThreadsClient(TOKEN, "U1", transport=tr)
        try:
            c.exchange_token(SECRET); msg = ""
        except ig_api.IGError as e:
            msg = str(e)
        check("換長效 token 失敗的訊息不含 token 與 app secret，且用 th_exchange_token", msg and TOKEN not in msg and SECRET not in msg and calls[0][2]["grant_type"] == "th_exchange_token", msg)
        calls.clear()
        c = TA.ThreadsClient(TOKEN, "U1", transport=lambda m, u, p: (calls.append((m, u, p)) or (200, {"access_token": "NEW", "expires_in": 5184000})))
        body = c.refresh_token()
        check("refresh 用 th_refresh_token", body["access_token"] == "NEW" and calls[0][2]["grant_type"] == "th_refresh_token")
        dbg = lambda m, u, p: (200, {"data": {"is_valid": True, "scopes": ["threads_basic", "threads_content_publish"], "expires_at": 1792000000}}) if "/debug_token" in u and p.get("input_token") == TOKEN else (400, {"error": {"message": "x"}})
        info = TA.ThreadsClient(TOKEN, "U1", transport=dbg).debug_token()
        check("debug_token：回傳 scopes 與到期時間（用同一顆 token 檢查自己）", info["scopes"] == ["threads_basic", "threads_content_publish"] and info["expires_at"] == 1792000000)
        c = TA.ThreadsClient(TOKEN, None, transport=Fake())
        check("沒有 user id 時用 /me 的別名", c._uid() == "me")
    print(f"\n{'全部通過' if not FAILS else f'{len(FAILS)} 項失敗'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
