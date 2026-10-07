"""IG 發文（ig_api.py、ig_publish.py、hosting.py）的回歸測試。全部用假的 transport 與假的網址檢查，**不連網、不發文**。

「故意做壞」：非 JPEG、尺寸或比例超出限制、容器永遠不 FINISHED、錯誤訊息夾帶 token、已發布過又發、dry-run 卻送出請求，都必須被擋下。
用法（repo 根目錄）：uv run python tests/test_ig_publish.py
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
import ig_publish as P  # noqa: E402

TOKEN = "IGAAsecretTOKEN123"
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  {detail}"))
    if not ok:
        FAILS.append(name)


def jpeg(path, size=(1080, 1350)):
    Image.new("RGB", size, (240, 224, 192)).save(path, "JPEG", quality=90)


class Fake:
    """假的 Meta API：記錄每個請求，依路徑回應。"""
    def __init__(self, statuses=None, fail_media=None, fail_times=0):
        self.calls, self.n = [], 0
        self.statuses = list(statuses or [])
        self.fail_media, self.fail_times = fail_media, fail_times

    def __call__(self, method, url, params):
        self.calls.append((method, url, dict(params)))
        path = url.split("/v25.0/", 1)[-1]
        if path.endswith("/media_publish"):
            return 200, {"id": "MEDIA1"}
        if path.endswith("/media"):
            if self.fail_media and self.fail_times > 0:
                self.fail_times -= 1
                return self.fail_media
            self.n += 1
            return 200, {"id": f"C{self.n}"}
        if path.startswith("MEDIA1"):
            return 200, {"permalink": "https://www.instagram.com/p/XYZ/", "timestamp": "2026-10-07T10:00:00+0000"}
        if path.endswith("content_publishing_limit"):
            return 200, {"data": [{"quota_usage": 1, "config": {"quota_total": 50, "quota_duration": 86400}}]}
        if path.startswith("C") or path.startswith("CAR"):
            return 200, {"status_code": self.statuses.pop(0) if self.statuses else "FINISHED"}
        return 200, {}


def fake_pack(tmp: Path, n=3):
    pack = tmp / "out" / "s" / "fake-concept"
    (pack / "_build").mkdir(parents=True)
    (pack / "ig" / "jpg").mkdir(parents=True)
    slides = [{"layout": "cover", "title": "封面", "body": "副標"}] + \
             [{"layout": "text", "title": f"第 {i} 張", "body": "補充"} for i in range(2, n + 1)]
    spec = {"concept": "fake-concept", "series": "s", "lang": "zh-TW", "hook": {"style": "反直覺斷言"}, "slides": slides,
            "caption": {"first": "第一句", "nav": "導流行", "hashtags": ["DSO_X"]}}
    (pack / "_build" / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    (pack / "_build" / "alt-text.json").write_text(json.dumps({f"{i:02d}.png": f"替代文字{i}" for i in range(1, n + 1)}, ensure_ascii=False), encoding="utf-8")
    for i in range(1, n + 1):
        jpeg(pack / "ig" / "jpg" / f"{i:02d}.jpg")
        Image.new("RGB", (1080, 1350)).save(pack / "ig" / f"{i:02d}.png")
    return pack


class H(hosting.Host):
    def upload(self, p):
        return f"https://example.test/{Path(p).name}"


def opener_ok(req, timeout=0):
    class R:
        headers = {"Content-Type": "image/jpeg"}
        def __enter__(s): return s
        def __exit__(s, *a): return False
        def read(s, n=-1): return b"\xff\xd8\xff" + b"0" * 100
    return R()


def main():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        # ---- 圖片驗證
        jpeg(tmp / "ok.jpg")
        check("好的 1080x1350 JPEG 通過", P.validate_jpeg(tmp / "ok.jpg") == [])
        Image.new("RGB", (1080, 1350)).save(tmp / "x.jpg", "PNG")
        check("抓得到：PNG 內容冒充 .jpg", any("不是 JPEG" in e for e in P.validate_jpeg(tmp / "x.jpg")))
        jpeg(tmp / "wide.jpg", (2000, 1500))
        check("抓得到：寬度超過 1440", any("寬" in e for e in P.validate_jpeg(tmp / "wide.jpg")))
        jpeg(tmp / "tall.jpg", (800, 2400))
        check("抓得到：比例超出 4:5～1.91:1", any("比例" in e for e in P.validate_jpeg(tmp / "tall.jpg")))
        old = P.MAX_BYTES
        P.MAX_BYTES = 100
        check("抓得到：超過 8 MiB（門檻暫時調小）", any("MiB" in e for e in P.validate_jpeg(tmp / "ok.jpg")))
        P.MAX_BYTES = old
        pack0 = tmp / "prep"
        (pack0 / "ig").mkdir(parents=True)
        Image.new("RGB", (1080, 1350), (10, 100, 120)).save(pack0 / "ig" / "01.png")
        r = P.prepare_images(pack0)
        check("prepare：PNG 轉成通過驗證的 JPEG", r["ok"] and (pack0 / "ig/jpg/01.jpg").exists(), r)

        # ---- 託管與網址檢查
        h = hosting.GitHubRawHost(ROOT, remote_url="https://github.com/johnnyhwu/datasciocean-social-media.git")
        u = h.upload(ROOT / "out/a/b/ig/jpg/01.jpg")
        check("GitHub raw 網址乾淨（無 query）", u == "https://raw.githubusercontent.com/johnnyhwu/datasciocean-social-media/main/out/a/b/ig/jpg/01.jpg", u)
        check("抓得到：網址帶 query", hosting.check_public("https://x.test/a.jpg?x=1")[0] is False)
        check("網址檢查：JPEG 通過", hosting.check_public("https://x.test/a.jpg", opener=opener_ok)[0])
        def opener_png(req, timeout=0):
            r = opener_ok(req); r.read = lambda n=-1: b"\x89PNG..."; return r
        check("抓得到：網址內容不是 JPEG", hosting.check_public("https://x.test/a.jpg", opener=opener_png)[0] is False)

        # ---- API 客戶端
        c = ig_api.IGClient(TOKEN, "U1", transport=Fake(), sleep=lambda s: None)
        fk = Fake(statuses=["IN_PROGRESS", "IN_PROGRESS", "FINISHED"]); sleeps = []
        c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=sleeps.append)
        check("輪詢：IN_PROGRESS 兩次後 FINISHED", c.wait_finished("C1") == "FINISHED" and sleeps == [60, 60], sleeps)
        c = ig_api.IGClient(TOKEN, "U1", transport=Fake(statuses=["IN_PROGRESS"] * 9), sleep=lambda s: None)
        try:
            c.wait_finished("C1"); caught = False
        except ig_api.IGError as e:
            caught = e.code == 9007
        check("抓得到：容器一直不 FINISHED（上限 5 次）", caught)
        bad = lambda m, u, p: (400, {"error": {"code": 9004, "error_subcode": 2207052, "message": f"fetch failed access_token={TOKEN} {TOKEN}"}})
        c = ig_api.IGClient(TOKEN, "U1", transport=bad, sleep=lambda s: None)
        try:
            c.create_container(image_url="https://x.test/a.jpg"); msg = ""
        except ig_api.IGError as e:
            msg = str(e)
        check("錯誤訊息不含 token", msg and TOKEN not in msg, msg)
        fk = Fake(fail_media=(500, {"error": {"code": 2, "message": "temp"}}), fail_times=2)
        c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        c.create_container(image_url="https://x.test/a.jpg")
        check("暫時性錯誤（5xx）重試後成功，共 3 次呼叫", len([x for x in fk.calls if x[1].endswith("/media")]) == 3)
        fk = Fake(fail_media=(400, {"error": {"code": 9004, "message": "no"}}), fail_times=5)
        c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        try:
            c.create_container(image_url="https://x.test/a.jpg")
        except ig_api.IGError:
            pass
        check("9004 不重試（只 1 次呼叫）", len(fk.calls) == 1, len(fk.calls))
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        c.create_container(image_url="https://x.test/a.jpg", caption="cap", carousel_item=True, is_ai_generated=True, alt_text="alt")
        child = fk.calls[-1][2]
        check("輪播子項不帶 caption 與 is_ai_generated", "caption" not in child and "is_ai_generated" not in child and child["is_carousel_item"] == "true")
        c.create_container(children=["C1", "C2"], caption="cap", is_ai_generated=True)
        top = fk.calls[-1][2]
        check("carousel container 帶 caption、children、is_ai_generated", top["media_type"] == "CAROUSEL" and top["children"] == "C1,C2" and top["caption"] == "cap" and top["is_ai_generated"] == "true")

        # ---- 發文流程
        pack = fake_pack(tmp)
        env = {"IG_API_VERSION": "v25.0"}
        logs = []
        recs = []
        P.log_publish = lambda e, path=None: logs.append(e)
        P.ST.record = lambda *a: recs.append(a)
        orig_load = P.ST.load
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pack, False, env, c, H(), fetch=opener_ok)
        posts = [x for x in fk.calls if x[0] == "POST"]
        check("dry-run：沒有任何 POST 請求，且 ok", r["ok"] and not posts and r["mode"] == "dry-run", (r.get("problems"), len(posts)))
        check("dry-run 印出的請求不含 token", TOKEN not in json.dumps(r, ensure_ascii=False))
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pack, True, env, c, H(), fetch=opener_ok)
        posts = [x for x in fk.calls if x[0] == "POST"]
        kinds = [("child" if x[2].get("is_carousel_item") else "carousel" if x[2].get("media_type") else "publish") for x in posts]
        check("--confirm：3 個子項 → carousel → publish，依序", r["ok"] and kinds == ["child"] * 3 + ["carousel", "publish"], (kinds, r.get("error")))
        check("每個子項帶 alt_text", all(x[2].get("alt_text") for x in posts[:3]))
        check("發佈後寫回 state 與紀錄（含 permalink）", len(recs) == 1 and recs[0][1] == "ig_carousel" and "instagram.com/p/XYZ" in recs[0][2] and logs and "media_id" in logs[0])
        check("紀錄不含 token", TOKEN not in json.dumps(logs, ensure_ascii=False))
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        n0 = len(recs)
        r = P.publish_carousel(pack, True, env, c, H(), fetch=opener_ok, record=False)
        check("--no-record：發佈成功但不寫回 state", r["ok"] and len(recs) == n0, (r.get("error"), len(recs)))
        P.ST.load = lambda c: {"formats": {"ig_carousel": {"status": "published"}}, "posts": []}
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pack, True, env, c, H(), fetch=opener_ok)
        check("抓得到：已發布過又發 → 不發", not r["ok"] and not [x for x in fk.calls if x[0] == "POST"], r.get("problems"))
        P.ST.load = orig_load
        def opener_404(req, timeout=0):
            raise hosting.urllib.error.HTTPError(req.full_url, 404, "nf", {}, io.BytesIO(b""))
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pack, True, env, c, H(), fetch=opener_404)
        check("抓得到：圖片網址抓不到（還沒 push）→ 不發", not r["ok"] and not [x for x in fk.calls if x[0] == "POST"])
        (pack / "ig/jpg/03.jpg").unlink()
        r = P.publish_carousel(pack, True, env, ig_api.IGClient(TOKEN, "U1", transport=Fake(), sleep=lambda s: None), H(), fetch=opener_ok)
        check("抓得到：JPEG 張數與投影片不符 → 不發", not r["ok"] and any("先執行 prepare" in p for p in r["problems"]))

        # ---- 預檢（preflight）與沿用
        T0 = dt.datetime(2026, 10, 7, 10, 0, tzinfo=dt.timezone.utc)
        H1 = dt.timedelta(hours=1)
        kind = lambda x: ("child" if x[2].get("is_carousel_item") else "carousel" if x[2].get("media_type") else "publish")
        posts_of = lambda fk_: [kind(x) for x in fk_.calls if x[0] == "POST"]

        def prepared_pack(name):
            pk = fake_pack(tmp / name)
            fkp = Fake(); cp = ig_api.IGClient(TOKEN, "U1", transport=fkp, sleep=lambda s: None)
            rp = P.preflight_carousel(pk, env, cp, H(), fetch=opener_ok, now=T0)
            return pk, fkp, rp

        pk, fkp, rp = prepared_pack("pf1")
        check("預檢：建 3 個子項與 carousel container，沒有 media_publish", rp["ok"] and posts_of(fkp) == ["child"] * 3 + ["carousel"], (posts_of(fkp), rp.get("error")))
        pf = pk / "_build" / P.PREPARED_NAME
        check("預檢結果寫進 _build/ig-prepared.json，且不含 token", pf.exists() and TOKEN not in pf.read_text(encoding="utf-8"))
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pk, False, env, c, H(), fetch=opener_ok, now=T0 + H1)
        check("dry-run 會報告預檢可沿用，且沒有 POST", r["prepared"]["reusable"] and not posts_of(fk), r["prepared"])
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pk, True, env, c, H(), fetch=opener_ok, now=T0 + 2 * H1)
        check("沿用預檢：只送 media_publish 一個 POST", r["ok"] and r["reused_preflight"] and posts_of(fk) == ["publish"], (posts_of(fk), r.get("error")))
        check("發佈後預檢檔被刪除，紀錄標示沿用", not pf.exists() and logs[-1]["reused_preflight"] is True)

        pk, _, _ = prepared_pack("pf2")
        spec_f = pk / "_build" / "spec.json"
        sp = json.loads(spec_f.read_text(encoding="utf-8")); sp["caption"]["first"] = "改過的第一句"
        spec_f.write_text(json.dumps(sp, ensure_ascii=False), encoding="utf-8")
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pk, True, env, c, H(), fetch=opener_ok, now=T0 + H1)
        check("抓得到：預檢後 caption 改了 → 不沿用，重建後才發", r["ok"] and not r["reused_preflight"] and posts_of(fk) == ["child"] * 3 + ["carousel", "publish"], posts_of(fk))
        pk, _, _ = prepared_pack("pf3")
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pk, True, env, c, H(), fetch=opener_ok, now=T0 + 24 * H1)
        check("抓得到：預檢超過 23 小時 → 不沿用，重建", r["ok"] and not r["reused_preflight"] and posts_of(fk) == ["child"] * 3 + ["carousel", "publish"], posts_of(fk))
        pk, _, _ = prepared_pack("pf4")
        fk = Fake(statuses=["EXPIRED"]); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pk, True, env, c, H(), fetch=opener_ok, now=T0 + H1)
        check("抓得到：預檢的 container 已 EXPIRED → 不沿用，重建", r["ok"] and not r["reused_preflight"] and posts_of(fk) == ["child"] * 3 + ["carousel", "publish"], posts_of(fk))
        pk, _, _ = prepared_pack("pf5")
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.publish_carousel(pk, True, env, c, H(), fetch=opener_ok, now=T0 + H1, reuse=False)
        check("--no-reuse：即使預檢有效也重建", r["ok"] and not r["reused_preflight"] and len(posts_of(fk)) == 5)
        pk = fake_pack(tmp / "pf6")
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.preflight_carousel(pk, env, c, H(), fetch=opener_404, now=T0)
        check("抓得到：預檢時圖片網址抓不到 → 不建 container", not r["ok"] and not posts_of(fk) and not (pk / "_build" / P.PREPARED_NAME).exists())
        P.ST.load = lambda c_: {"formats": {"ig_carousel": {"status": "published"}}, "posts": []}
        fk = Fake(); c = ig_api.IGClient(TOKEN, "U1", transport=fk, sleep=lambda s: None)
        r = P.preflight_carousel(pk, env, c, H(), fetch=opener_ok, now=T0)
        check("抓得到：已發布過的貼文不預檢", not r["ok"] and not posts_of(fk))
        P.ST.load = orig_load
        r = P.preflight_carousel(pk, env, None, H(), fetch=opener_ok, now=T0)
        check("沒有 token → 預檢不送請求，也不當機", not r["ok"] and "沒有 token" in r.get("error", ""))

        # ---- .env 與 token 效期
        envf = tmp / ".env"
        envf.write_text("IG_USER_ID=U1\nIG_ACCESS_TOKEN=old\n# note\n", encoding="utf-8")
        P.set_env("IG_ACCESS_TOKEN", "new", envf)
        P.set_env("IG_TOKEN_REFRESHED_AT", "2026-01-01T00:00:00+00:00", envf)
        e = P.load_env(envf)
        check(".env 更新保留其他行", e["IG_ACCESS_TOKEN"] == "new" and e["IG_USER_ID"] == "U1" and "# note" in envf.read_text())
        now = dt.datetime(2026, 10, 7, tzinfo=dt.timezone.utc)
        check("token 效期：50 天前 refresh → 剩約 10 天", abs(P.token_days_left({"IG_TOKEN_REFRESHED_AT": "2026-08-18T00:00:00+00:00"}, now) - 10) < 0.1)
        class RT(Fake):
            def __call__(s, m, u, p):
                s.calls.append((m, u, p))
                return 200, {"access_token": "BRANDNEW", "expires_in": 5184000}
        rt = RT(); c = ig_api.IGClient("old", "U1", transport=rt)
        w = P.ensure_token_fresh(c, {"IG_TOKEN_REFRESHED_AT": "2026-08-18T00:00:00+00:00"}, now, envf)
        e2 = P.load_env(envf)
        check("剩餘效期過短 → 警告並自動 refresh，新 token 寫進 .env", any("少於" in x for x in w) and e2["IG_ACCESS_TOKEN"] == "BRANDNEW" and all("BRANDNEW" not in x for x in w), w)
        rt = RT(); c = ig_api.IGClient("old", "U1", transport=rt)
        w = P.ensure_token_fresh(c, {"IG_TOKEN_REFRESHED_AT": "2026-10-06T00:00:00+00:00"}, now, envf)
        check("效期充足 → 不 refresh", not rt.calls and not w)
    print(f"\n{'全部通過' if not FAILS else f'{len(FAILS)} 項失敗'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
