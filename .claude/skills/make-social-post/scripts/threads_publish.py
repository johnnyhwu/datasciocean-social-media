"""把發布包用 Threads 官方 API 發成一串（正文 → 每則附圖的串文 → 最後一則附連結）。

**預設是 dry-run**：只驗證並印出將送出的請求，不發文。要實際發佈必須加 --confirm，而且要先經人確認。
憑證只放 .env：THREADS_ACCESS_TOKEN、THREADS_USER_ID（可由 whoami 取得）；token 不會出現在任何輸出。
設定與限制見 references/threads-publish.md。

串文做法：正文是根貼文，之後每一則都用 reply_to_id 回覆**前一則**（就是 app 裡的「新增到串文」）。
每一則發完就把 id 寫進 _build/threads-progress.json；中途失敗，修好後再執行同一個指令會從下一則繼續，
不會重複發。想整串撤掉：rollback --confirm（用 DELETE /{id}，需要 threads_delete 權限）。

用法（repo 根目錄）：
  uv run python .claude/skills/make-social-post/scripts/threads_publish.py whoami [--no-write]
  uv run python .claude/skills/make-social-post/scripts/threads_publish.py limit
  uv run python .claude/skills/make-social-post/scripts/threads_publish.py token-status | token-info [--write] | refresh-token | exchange-token
  uv run python .claude/skills/make-social-post/scripts/threads_publish.py publish out/<series>/<concept> [--confirm] [--no-record]
  uv run python .claude/skills/make-social-post/scripts/threads_publish.py rollback out/<series>/<concept> [--confirm]
  uv run python .claude/skills/make-social-post/scripts/threads_publish.py delete <media_id> ... [--confirm]
輸出一律是 JSON。
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import cardlib as W
import hosting
import ig_api
import publish_common as PC
import state as ST
import threads_api as TA

PROGRESS_NAME = "threads-progress.json"       # 已發佈的各則 id（在 _build/，不進 git）
PUBLISH_LOG = W.ROOT / "state" / "threads-publish-log.jsonl"
WARN_DAYS = PC.WARN_DAYS


def threads_len(text: str) -> int:
    """官方：500 字元上限，emoji 以 UTF-8 位元組數計。其餘字元算 1。"""
    return sum(len(ch.encode("utf-8")) if ord(ch) >= 0x1F000 else 1 for ch in text)


def plan_thread(pack: Path, host: hosting.Host) -> dict:
    d = json.loads((pack / "_build" / "spec.json").read_text(encoding="utf-8"))
    th = d["threads"]
    posts = [{"kind": "root", "media_type": "TEXT", "text": th["body"]["text"]}]
    problems = []
    for it in th["items"]:
        n = it["slide"]
        jpg = pack / "ig" / "jpg" / f"{n:02d}.jpg"
        if not jpg.exists():
            problems.append(f"第 {n} 張的 JPEG 不存在：先對這個發布包執行 ig_publish.py prepare 並 push")
            continue
        problems += PC.validate_jpeg(jpg)
        posts.append({"kind": f"item-slide{n}", "media_type": "IMAGE", "text": it["text"], "image_url": host.upload(jpg), "jpg": str(jpg)})
    last = th["last"]
    posts.append({"kind": "last", "media_type": "TEXT", "text": last["text"], "link_attachment": last.get("link")})
    for i, p in enumerate(posts, 1):
        n = threads_len(p["text"])
        if n > TA.TEXT_MAX:
            problems.append(f"第 {i} 則（{p['kind']}）{n} 字，超過 {TA.TEXT_MAX}")
        if not p["text"].strip():
            problems.append(f"第 {i} 則（{p['kind']}）沒有文字")
    return {"concept": d["concept"], "series": d.get("series"), "hook_style": d["hook"]["style"], "posts": posts, "problems": problems}


def fingerprint(plan: dict, version: str, user_id: str | None) -> str:
    h = hashlib.sha256()
    for p in plan["posts"]:
        if p.get("jpg"):
            h.update(Path(p["jpg"]).read_bytes())
    h.update(json.dumps([[p["kind"], p["media_type"], p["text"], p.get("image_url"), p.get("link_attachment")] for p in plan["posts"]],
                        ensure_ascii=False).encode())
    h.update(json.dumps([version, user_id]).encode())
    return h.hexdigest()[:16]


def load_progress(pack: Path) -> dict | None:
    f = pack / "_build" / PROGRESS_NAME
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def save_progress(pack: Path, prog: dict) -> None:
    (pack / "_build" / PROGRESS_NAME).write_text(json.dumps(prog, ensure_ascii=False, indent=2), encoding="utf-8")


def describe(plan: dict, version: str) -> list[dict]:
    out = []
    for i, p in enumerate(plan["posts"], 1):
        params = {"media_type": p["media_type"], "text": p["text"]}
        if p.get("image_url"):
            params["image_url"] = p["image_url"]
        if p.get("link_attachment"):
            params["link_attachment"] = p["link_attachment"]
        if i > 1:
            params["reply_to_id"] = "<前一則的 id>"
        out.append({"step": f"第 {i} 則（{p['kind']}）", "chars": threads_len(p["text"]),
                    "POST": f"/{version}/<THREADS_ID>/threads", "params": params,
                    "then": "等約 30 秒、確認 container 完成，再 POST threads_publish"})
    return out


def log_publish(entry: dict, path: Path = PUBLISH_LOG) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def publish_thread(pack: Path, confirm: bool, env: dict, client: TA.ThreadsClient | None, host: hosting.Host,
                   fetch=hosting.urllib.request.urlopen, now=None, record: bool = True) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    plan = plan_thread(pack, host)
    version = env.get("THREADS_API_VERSION") or TA.API_VERSION
    problems = list(plan["problems"])
    url_checks = []
    for p in plan["posts"]:
        if p.get("image_url"):
            ok, why = hosting.check_public(p["image_url"], opener=fetch)
            url_checks.append({"url": p["image_url"], "ok": ok, "detail": why})
            if not ok:
                problems.append(f"圖片網址不能用：{p['image_url']}｜{why}")
    if ST.load(plan["concept"])["formats"].get("threads_thread", {}).get("status") == "published":
        problems.append("state 顯示這則的 Threads 串文已發布過；不重複發佈")
    fp = fingerprint(plan, version, client.user_id if client else env.get("THREADS_USER_ID"))
    prog = load_progress(pack)
    resume_from = 0
    if prog:
        if prog.get("fingerprint") != fp:
            problems.append("_build/threads-progress.json 的內容與目前的發布包不一致（上次發到一半、之後內容又改了）："
                            "先 rollback 刪掉已發的幾則，或確認後手動處理")
        else:
            resume_from = len(prog["published"])
    result = {"ok": False, "mode": "publish" if confirm else "dry-run", "concept": plan["concept"], "post_count": len(plan["posts"]),
              "problems": problems, "requests": describe(plan, version), "url_checks": url_checks,
              "resume_from": resume_from, "already_published_ids": (prog or {}).get("published", [])}
    if client:
        try:
            result["publishing_limit"] = client.publishing_limit()
        except ig_api.IGError as e:
            result["limit_note"] = f"額度查詢失敗（端點官方頁沒寫清楚，不影響發佈）：{e}"
    if not confirm:
        result["note"] = "dry-run：沒有送出任何發文請求。要實際發佈請先經人確認，再加 --confirm。"
        result["ok"] = not problems
        return result
    if problems:
        result["error"] = "有問題，沒有發佈"
        return result
    if not client:
        result["error"] = "沒有 token，無法發佈"
        return result
    prog = prog or {"fingerprint": fp, "started_at": now.isoformat(timespec="seconds"), "published": []}
    try:
        for i in range(len(prog["published"]), len(plan["posts"])):
            p = plan["posts"][i]
            prev = prog["published"][-1] if prog["published"] else None
            cid = client.create_post(p["media_type"], text=p["text"], image_url=p.get("image_url"),
                                     link_attachment=p.get("link_attachment"), reply_to_id=prev)
            client.wait_ready(cid)
            prog["published"].append(client.publish(cid))
            save_progress(pack, prog)
    except ig_api.IGError as e:
        result.update(error=str(e), published_so_far=len(prog["published"]), published_ids=prog["published"],
                      hint=f"已發佈 {len(prog['published'])}/{len(plan['posts'])} 則。修好問題後再執行同一個指令會從下一則繼續；"
                           "或用 rollback --confirm 把已發的刪掉。")
        return result
    root_id = prog["published"][0]
    info = client.media_info(root_id)
    when = info.get("timestamp") or now.isoformat(timespec="seconds")
    if record:
        with contextlib.redirect_stdout(sys.stderr):      # record 會印訊息；stdout 只留 JSON
            ST.record(plan["concept"], "threads_thread", info.get("permalink", ""), when, plan["series"], plan["hook_style"], [])
    log_publish({"time": when, "concept": plan["concept"], "format": "threads_thread", "root_id": root_id,
                 "permalink": info.get("permalink"), "post_ids": prog["published"]})
    (pack / "_build" / PROGRESS_NAME).unlink(missing_ok=True)
    result.update(ok=True, root_id=root_id, permalink=info.get("permalink"), published_at=when, post_ids=prog["published"])
    return result


def last_logged_ids(concept: str, path: Path | None = None) -> list[str]:
    """整串發完後進度檔會刪除；這時改讀發佈紀錄裡該貼文最近一次的各則 id。"""
    path = path or PUBLISH_LOG
    if not path.exists():
        return []
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        e = json.loads(line)
        if e.get("concept") == concept and e.get("post_ids"):
            ids = e["post_ids"]
    return ids


def rollback(pack: Path, confirm: bool, client: TA.ThreadsClient | None, log_path: Path | None = None) -> dict:
    prog = load_progress(pack)
    source = "進度檔"
    if not prog or not prog.get("published"):
        concept = json.loads((pack / "_build" / "spec.json").read_text(encoding="utf-8"))["concept"]
        logged = last_logged_ids(concept, log_path)
        if not logged:
            return {"ok": True, "note": "沒有可撤回的串文（沒有進度檔，發佈紀錄裡也沒有這則）"}
        prog, source = {"published": logged}, "發佈紀錄 state/threads-publish-log.jsonl"
    ids = list(reversed(prog["published"]))
    result = {"ok": False, "mode": "rollback" if confirm else "dry-run", "will_delete": ids, "source": source}
    if not confirm:
        result["note"] = "dry-run：沒有刪除任何東西。加 --confirm 才會用 DELETE 刪除（需要 threads_delete 權限）。"
        result["ok"] = True
        return result
    if not client:
        result["error"] = "沒有 token"
        return result
    deleted = []
    try:
        for i in ids:
            client.delete(i)
            deleted.append(i)
    except ig_api.IGError as e:
        result.update(error=str(e), deleted=deleted, hint="可能沒有 threads_delete 權限；已刪除的不會重複刪")
        if source == "進度檔":
            prog["published"] = [x for x in prog["published"] if x not in deleted]
            save_progress(pack, prog)
        return result
    (pack / "_build" / PROGRESS_NAME).unlink(missing_ok=True)
    result.update(ok=True, deleted=deleted)
    return result


# ---------------------------------------------------------------- CLI
def emit(obj: dict) -> int:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return 0 if obj.get("ok", True) else 1


def make_client(env: dict) -> TA.ThreadsClient:
    if not env.get("THREADS_ACCESS_TOKEN"):
        raise SystemExit(json.dumps({"ok": False, "error": "沒有 THREADS_ACCESS_TOKEN：請照 references/threads-publish.md 把 token 放進 .env（不要貼進聊天）"}, ensure_ascii=False))
    return TA.ThreadsClient(env["THREADS_ACCESS_TOKEN"], env.get("THREADS_USER_ID"), version=env.get("THREADS_API_VERSION") or TA.API_VERSION,
                            host=env.get("THREADS_API_HOST") or TA.API_HOST)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("whoami")
    w.add_argument("--no-write", action="store_true")
    for name in ("limit", "token-status", "refresh-token", "exchange-token"):
        sub.add_parser(name)
    ti = sub.add_parser("token-info")
    ti.add_argument("--write", action="store_true", help="把 THREADS_TOKEN_REFRESHED_AT 校正成「到期時間減 60 天」（長效 token 才適用）")
    pp = sub.add_parser("publish")
    pp.add_argument("pack"); pp.add_argument("--confirm", action="store_true"); pp.add_argument("--no-record", action="store_true")
    rb = sub.add_parser("rollback")
    rb.add_argument("pack"); rb.add_argument("--confirm", action="store_true")
    dl = sub.add_parser("delete")
    dl.add_argument("ids", nargs="+"); dl.add_argument("--confirm", action="store_true")
    a = ap.parse_args(argv)

    env = PC.load_env()
    host = hosting.GitHubRawHost(W.ROOT)
    confirm = getattr(a, "confirm", False)
    needs_token = a.cmd in ("whoami", "limit", "token-status", "token-info", "refresh-token", "exchange-token") or confirm
    client = make_client(env) if (env.get("THREADS_ACCESS_TOKEN") or needs_token) else None
    warns = []
    if client and a.cmd not in ("token-status", "exchange-token") and (a.cmd != "publish" or confirm):
        warns = PC.ensure_token_fresh(client, env, token_key="THREADS_ACCESS_TOKEN", ts_key="THREADS_TOKEN_REFRESHED_AT")
        env = PC.load_env()
        client.token = env["THREADS_ACCESS_TOKEN"]

    if a.cmd == "whoami":
        try:
            me = client.me()
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e), "hint": "沒有成功？檢查：帳號是否已加為 Threads Tester 並在 Threads 接受邀請、token 是否過期、THREADS_API_HOST 可試 graph.threads.com"})
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        if not a.no_write:
            if not env.get("THREADS_USER_ID") and me.get("id"):
                PC.set_env("THREADS_USER_ID", str(me["id"]))
            if not env.get("THREADS_TOKEN_REFRESHED_AT"):
                PC.set_env("THREADS_TOKEN_REFRESHED_AT", now_iso)
        out = {"ok": True, "user_id": me.get("id"), "username": me.get("username"), "warnings": warns}
        if a.no_write:
            out["suggested_THREADS_TOKEN_REFRESHED_AT"] = now_iso
            out["note"] = "--no-write：沒有修改 .env"
        return emit(out)
    if a.cmd == "limit":
        try:
            return emit({"ok": True, "limit": client.publishing_limit(), "warnings": warns})
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e), "note": "額度查詢端點官方頁沒寫清楚；失敗不影響發佈"})
    if a.cmd == "token-info":
        try:
            info = client.debug_token()
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e)})
        exp = info.get("expires_at")
        now = dt.datetime.now(dt.timezone.utc)
        days = None if not exp else round((dt.datetime.fromtimestamp(exp, dt.timezone.utc) - now).total_seconds() / 86400, 2)
        scopes = info.get("scopes") or []
        out = {"ok": True, "is_valid": info.get("is_valid"), "scopes": scopes, "days_left": days,
               "expires_at": None if not exp else dt.datetime.fromtimestamp(exp, dt.timezone.utc).isoformat(timespec="seconds"),
               "can_publish": "threads_content_publish" in scopes, "can_delete": "threads_delete" in scopes}
        if days is not None and days < 2:
            out["warning"] = "這是短效 token（不到 2 天就到期）；需要 THREADS_APP_SECRET 再執行 exchange-token 換成 60 天長效 token"
        elif days is not None and a.write:
            PC.set_env("THREADS_TOKEN_REFRESHED_AT", (dt.datetime.fromtimestamp(exp, dt.timezone.utc) - dt.timedelta(days=60)).isoformat(timespec="seconds"))
            out["note"] = "已把 THREADS_TOKEN_REFRESHED_AT 校正成到期時間減 60 天"
        return emit(out)
    if a.cmd == "token-status":
        left = PC.token_days_left(env, ts_key="THREADS_TOKEN_REFRESHED_AT")
        return emit({"ok": True, "days_left": None if left is None else round(left, 1),
                     "warning": None if left is None or left >= WARN_DAYS else f"剩餘效期少於 {WARN_DAYS} 天，請 refresh-token"})
    if a.cmd == "refresh-token":
        try:
            body = client.refresh_token()
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e)})
        PC.set_env("THREADS_ACCESS_TOKEN", body["access_token"])
        PC.set_env("THREADS_TOKEN_REFRESHED_AT", dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        return emit({"ok": True, "expires_in_s": body.get("expires_in"), "note": "新 token 已寫入 .env（不會顯示）"})
    if a.cmd == "exchange-token":
        secret = env.get("THREADS_APP_SECRET")
        if not secret:
            return emit({"ok": False, "error": "沒有 THREADS_APP_SECRET：短效 token 換長效 token 需要 Threads 的 App Secret（只放 .env）"})
        try:
            body = client.exchange_token(secret)
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e)})
        PC.set_env("THREADS_ACCESS_TOKEN", body["access_token"])
        PC.set_env("THREADS_TOKEN_REFRESHED_AT", dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        return emit({"ok": True, "expires_in_s": body.get("expires_in"), "note": "長效 token 已寫入 .env（不會顯示）"})
    if a.cmd == "publish":
        return emit(publish_thread(Path(a.pack).resolve(), a.confirm, env, client, host, record=not a.no_record) | {"warnings": warns})
    if a.cmd == "rollback":
        return emit(rollback(Path(a.pack).resolve(), a.confirm, client))
    if a.cmd == "delete":
        res = {"ok": True, "mode": "delete" if a.confirm else "dry-run", "ids": a.ids, "deleted": []}
        if not a.confirm:
            res["note"] = "dry-run：沒有刪除。加 --confirm（需要 threads_delete 權限；每天 100 次）"
            return emit(res)
        try:
            for i in a.ids:
                client.delete(i)
                res["deleted"].append(i)
        except ig_api.IGError as e:
            res.update(ok=False, error=str(e))
        return emit(res)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
