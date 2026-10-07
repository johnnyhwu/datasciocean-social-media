"""把發布包用 Instagram 官方 API 發到 IG（Instagram Login，graph.instagram.com）。

**預設是 dry-run**：只驗證並印出將送出的請求，不發文。要實際發佈必須加 --confirm，而且要先經人確認。
憑證只放 .env（已在 .gitignore）或環境變數：IG_ACCESS_TOKEN、IG_USER_ID（可由 whoami 取得）、IG_API_VERSION。
token、錯誤訊息、log 都不會出現 token。設定與限制見 references/instagram-publish.md。

用法（repo 根目錄）：
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py whoami
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py limit
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py token-status
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py refresh-token
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py prepare out/<series>/<concept>
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py publish out/<series>/<concept> [--confirm] [--no-record]
  uv run python .claude/skills/make-social-post/scripts/ig_publish.py publish-image <jpeg 路徑> --caption "…" [--alt "…"] [--confirm]
輸出一律是 JSON（給 Agent 讀）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import build_package as BP
import cardlib as W
import hosting
import ig_api
import state as ST

ENV_PATH = W.ROOT / ".env"
TOKEN_LIFETIME_DAYS = 60
WARN_DAYS = 14                 # 剩餘效期少於這個天數就警告，並在 token 存在滿 24 小時時自動 refresh
MIN_WIDTH, MAX_WIDTH = 320, 1440
RATIO_MIN, RATIO_MAX = 4 / 5, 1.91
MAX_BYTES = hosting.MAX_BYTES
PUBLISH_LOG = W.ROOT / "state" / "ig-publish-log.jsonl"


# ---------------------------------------------------------------- .env 與 token
def load_env(path: Path = ENV_PATH) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$", line)
            if m and not line.lstrip().startswith("#"):
                env[m.group(1)] = m.group(2).strip("\"'")
    for k in ("IG_ACCESS_TOKEN", "IG_USER_ID", "IG_API_VERSION", "IG_TOKEN_REFRESHED_AT", "IG_AI_GENERATED"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def set_env(key: str, value: str, path: Path = ENV_PATH) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out, done = [], False
    for line in lines:
        if re.match(rf"^\s*{key}\s*=", line):
            out.append(f"{key}={value}"); done = True
        else:
            out.append(line)
    if not done:
        out.append(f"{key}={value}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def token_days_left(env: dict, now: dt.datetime | None = None) -> float | None:
    ts = env.get("IG_TOKEN_REFRESHED_AT")
    if not ts:
        return None
    now = now or dt.datetime.now(dt.timezone.utc)
    t0 = dt.datetime.fromisoformat(ts)
    if t0.tzinfo is None:
        t0 = t0.replace(tzinfo=dt.timezone.utc)
    return TOKEN_LIFETIME_DAYS - (now - t0).total_seconds() / 86400


def make_client(env: dict, **kw) -> ig_api.IGClient:
    if not env.get("IG_ACCESS_TOKEN"):
        raise SystemExit(json.dumps({"ok": False, "error": "沒有 IG_ACCESS_TOKEN：請照 references/instagram-publish.md 把 token 放進 .env（不要貼進聊天）"}, ensure_ascii=False))
    return ig_api.IGClient(env["IG_ACCESS_TOKEN"], env.get("IG_USER_ID"), version=env.get("IG_API_VERSION") or ig_api.API_VERSION, **kw)


def ensure_token_fresh(client: ig_api.IGClient, env: dict, now: dt.datetime | None = None, env_path: Path = ENV_PATH) -> list[str]:
    """剩餘效期過短時警告；token 存在滿 24 小時才會自動 refresh。回傳警告訊息（不含 token）。"""
    warns = []
    left = token_days_left(env, now)
    if left is None:
        warns.append("IG_TOKEN_REFRESHED_AT 未設定，無法追蹤 token 效期（whoami 成功後會自動補上）")
        return warns
    if left < WARN_DAYS:
        warns.append(f"token 剩餘約 {left:.0f} 天，少於 {WARN_DAYS} 天")
        age_days = TOKEN_LIFETIME_DAYS - left
        if age_days >= 1 and left > 0:
            try:
                body = client.refresh_token()
                set_env("IG_ACCESS_TOKEN", body["access_token"], env_path)
                set_env("IG_TOKEN_REFRESHED_AT", (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"), env_path)
                client.token = body["access_token"]
                warns.append("已自動 refresh token（新 token 已寫入 .env）")
            except ig_api.IGError as e:
                warns.append(f"自動 refresh 失敗：{e}")
    return warns


# ---------------------------------------------------------------- 圖片
def validate_jpeg(path: Path) -> list[str]:
    """回傳違反官方限制的清單（空 = 通過）。"""
    from PIL import Image
    errs = []
    data = path.read_bytes()
    if data[:3] != b"\xff\xd8\xff":
        return [f"{path.name}: 不是 JPEG（IG 只支援 JPEG）"]
    if len(data) >= MAX_BYTES:
        errs.append(f"{path.name}: {len(data) / 1048576:.1f} MiB，需小於 8 MiB")
    im = Image.open(path)
    if im.format != "JPEG":
        errs.append(f"{path.name}: 格式 {im.format}（MPO、JPS 等延伸 JPEG 不支援）")
    w, h = im.size
    if not (MIN_WIDTH <= w <= MAX_WIDTH):
        errs.append(f"{path.name}: 寬 {w}px，需在 {MIN_WIDTH} 到 {MAX_WIDTH}")
    r = w / h
    if not (RATIO_MIN - 1e-9 <= r <= RATIO_MAX + 1e-9):
        errs.append(f"{path.name}: 比例 {r:.3f}，需在 4:5 到 1.91:1")
    return errs


def prepare_images(pack: Path) -> dict:
    """ig/NN.png -> ig/jpg/NN.jpg（sRGB、品質 95、不降色度取樣）並驗證官方限制。"""
    from PIL import Image
    pngs = sorted((pack / "ig").glob("[0-9][0-9].png"))
    if not pngs:
        raise SystemExit(json.dumps({"ok": False, "error": f"{pack}/ig 底下沒有投影片 PNG"}, ensure_ascii=False))
    out = pack / "ig" / "jpg"
    out.mkdir(exist_ok=True)
    files, errs = [], []
    for p in pngs:
        dst = out / f"{p.stem}.jpg"
        Image.open(p).convert("RGB").save(dst, "JPEG", quality=95, subsampling=0, optimize=True)
        errs += validate_jpeg(dst)
        files.append(dst)
    return {"ok": not errs, "files": [str(f.relative_to(W.ROOT)) if f.is_relative_to(W.ROOT) else str(f) for f in files], "errors": errs}


# ---------------------------------------------------------------- 發文計畫
def load_pack(pack: Path) -> dict:
    spec_f = pack / "_build" / "spec.json"
    d = json.loads(spec_f.read_text(encoding="utf-8"))
    alt_f = pack / "_build" / "alt-text.json"
    alts = json.loads(alt_f.read_text(encoding="utf-8")) if alt_f.exists() else {}
    return {"spec": d, "alts": alts, "caption": BP.caption_text(d)}


def plan_carousel(pack: Path, host: hosting.Host, env: dict) -> dict:
    pk = load_pack(pack)
    jpgs = sorted((pack / "ig" / "jpg").glob("[0-9][0-9].jpg"))
    n_slides = len(pk["spec"]["slides"])
    problems = []
    if len(jpgs) != n_slides:
        problems.append(f"JPEG {len(jpgs)} 張，投影片 {n_slides} 張：先執行 prepare")
    if not (2 <= len(jpgs) <= 10):
        problems.append(f"輪播需要 2 到 10 張，現在 {len(jpgs)} 張")
    for j in jpgs:
        problems += validate_jpeg(j)
    urls = [host.upload(j) for j in jpgs]
    caption = pk["caption"]
    if len(caption) > 2200:
        problems.append(f"caption {len(caption)} 字，超過 2200")
    if len(re.findall(r"#\w+", caption)) > 30:
        problems.append("hashtag 超過 30 個")
    alts = [pk["alts"].get(f"{j.stem}.png", "") for j in jpgs]
    ai = str(env.get("IG_AI_GENERATED", "")).lower() in ("1", "true", "yes")
    return {"concept": pk["spec"]["concept"], "series": pk["spec"].get("series"), "hook_style": pk["spec"]["hook"]["style"],
            "images": urls, "alt_texts": alts, "caption": caption, "is_ai_generated": ai, "problems": problems}


def describe_requests(plan: dict, version: str) -> list[dict]:
    """dry-run 印出的「將送出的請求」（不含 token）。"""
    reqs = []
    for i, (u, a) in enumerate(zip(plan["images"], plan["alt_texts"]), 1):
        reqs.append({"step": f"建立第 {i} 張的 container", "POST": f"/{version}/<IG_ID>/media",
                     "params": {"image_url": u, "is_carousel_item": "true", "alt_text": a}})
    reqs.append({"step": "每個 container 輪詢 status_code 直到 FINISHED（每 60 秒一次、最多 5 次）", "GET": f"/{version}/<CONTAINER_ID>?fields=status_code"})
    p = {"media_type": "CAROUSEL", "children": "<上面各 container id，逗號分隔>", "caption": plan["caption"]}
    if plan["is_ai_generated"]:
        p["is_ai_generated"] = "true"
    reqs.append({"step": "建立 carousel container", "POST": f"/{version}/<IG_ID>/media", "params": p})
    reqs.append({"step": "輪詢 carousel container 直到 FINISHED", "GET": f"/{version}/<CAROUSEL_ID>?fields=status_code"})
    reqs.append({"step": "發佈", "POST": f"/{version}/<IG_ID>/media_publish", "params": {"creation_id": "<CAROUSEL_ID>"}})
    return reqs


def log_publish(entry: dict, path: Path = PUBLISH_LOG) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def publish_carousel(pack: Path, confirm: bool, env: dict, client: ig_api.IGClient | None, host: hosting.Host,
                     fetch=hosting.urllib.request.urlopen, now=None, record: bool = True) -> dict:
    plan = plan_carousel(pack, host, env)
    version = env.get("IG_API_VERSION") or ig_api.API_VERSION
    result = {"ok": False, "mode": "publish" if confirm else "dry-run", "concept": plan["concept"], "image_count": len(plan["images"]),
              "problems": list(plan["problems"]), "requests": describe_requests(plan, version), "caption": plan["caption"]}
    # 唯讀檢查：網址是否公開可抓
    url_checks = []
    for u in plan["images"]:
        ok, why = hosting.check_public(u, opener=fetch)
        url_checks.append({"url": u, "ok": ok, "detail": why})
        if not ok:
            result["problems"].append(f"圖片網址不能用：{u}｜{why}")
    result["url_checks"] = url_checks
    # 已發布過就不再發
    if ST.load(plan["concept"])["formats"].get("ig_carousel", {}).get("status") == "published":
        result["problems"].append("state 顯示這則的 IG 輪播已發布過；不重複發佈")
    # 額度（唯讀，需要 token）
    if client and client.user_id:
        try:
            lim = client.publishing_limit()
            result["publishing_limit"] = lim
            data = (lim.get("data") or [lim])[0]
            used, total = data.get("quota_usage"), (data.get("config") or {}).get("quota_total")
            if used is not None and total is not None and used >= total:
                result["problems"].append(f"已達發文上限（{used}/{total}）")
        except ig_api.IGError as e:
            result["limit_error"] = str(e)
    if not confirm:
        result["note"] = "dry-run：沒有送出任何發文請求。要實際發佈請先經人確認，再加 --confirm。"
        result["ok"] = not result["problems"]
        return result
    if result["problems"]:
        result["error"] = "有問題，沒有發佈"
        return result
    if not client:
        result["error"] = "沒有 token，無法發佈"
        return result
    try:
        child_ids = []
        for u, a in zip(plan["images"], plan["alt_texts"]):
            child_ids.append(client.create_container(image_url=u, alt_text=a or None, carousel_item=True))
        for cid in child_ids:
            client.wait_finished(cid)
        car = client.create_container(children=child_ids, caption=plan["caption"], is_ai_generated=plan["is_ai_generated"])
        client.wait_finished(car)
        media_id = client.publish(car)
        info = client.media_info(media_id)
    except ig_api.IGError as e:
        result["error"] = str(e)
        result["hint"] = e.hint()
        return result
    when = info.get("timestamp") or (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds")
    if record:     # 實測（之後會手動刪除的測試貼文）用 --no-record，不要把狀態標成 published
        ST.record(plan["concept"], "ig_carousel", info.get("permalink", ""), when, plan["series"], plan["hook_style"], [])
    log_publish({"time": when, "concept": plan["concept"], "format": "ig_carousel", "media_id": media_id,
                 "permalink": info.get("permalink"), "container_id": car})
    result.update(ok=True, media_id=media_id, permalink=info.get("permalink"), published_at=when)
    return result


def publish_image(path: Path, caption: str, alt: str | None, confirm: bool, env: dict, client, host: hosting.Host,
                  fetch=hosting.urllib.request.urlopen) -> dict:
    problems = validate_jpeg(path)
    url = host.upload(path)
    version = env.get("IG_API_VERSION") or ig_api.API_VERSION
    result = {"ok": False, "mode": "publish" if confirm else "dry-run", "image_url": url, "problems": problems,
              "requests": [{"POST": f"/{version}/<IG_ID>/media", "params": {"image_url": url, "caption": caption, "alt_text": alt}},
                           {"GET": f"/{version}/<CONTAINER_ID>?fields=status_code"},
                           {"POST": f"/{version}/<IG_ID>/media_publish", "params": {"creation_id": "<CONTAINER_ID>"}}]}
    ok, why = hosting.check_public(url, opener=fetch)
    result["url_check"] = {"ok": ok, "detail": why}
    if not ok:
        problems.append(f"圖片網址不能用：{url}｜{why}")
    if not confirm:
        result["note"] = "dry-run：沒有送出任何發文請求。"
        result["ok"] = not problems
        return result
    if problems or not client:
        result["error"] = "有問題或沒有 token，沒有發佈"
        return result
    try:
        cid = client.create_container(image_url=url, caption=caption, alt_text=alt)
        client.wait_finished(cid)
        media_id = client.publish(cid)
        info = client.media_info(media_id)
    except ig_api.IGError as e:
        result.update(error=str(e), hint=e.hint())
        return result
    log_publish({"time": info.get("timestamp"), "concept": None, "format": "ig_image", "media_id": media_id, "permalink": info.get("permalink")})
    result.update(ok=True, media_id=media_id, permalink=info.get("permalink"))
    return result


# ---------------------------------------------------------------- CLI
def emit(obj: dict) -> int:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return 0 if obj.get("ok", True) else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("whoami", "limit", "token-status", "refresh-token"):
        sp = sub.add_parser(name)
        if name == "whoami":
            sp.add_argument("--no-write", action="store_true", help="只查詢，不把 IG_USER_ID、IG_TOKEN_REFRESHED_AT 寫進 .env")
    for name in ("prepare", "publish"):
        p = sub.add_parser(name)
        p.add_argument("pack")
        if name == "publish":
            p.add_argument("--confirm", action="store_true", help="實際發佈（沒有這個旗標一律是 dry-run）")
            p.add_argument("--no-record", action="store_true", help="實測用：發佈後不寫回 state（因為測試貼文會被手動刪除）")
    p = sub.add_parser("publish-image")
    p.add_argument("image")
    p.add_argument("--caption", default="")
    p.add_argument("--alt")
    p.add_argument("--confirm", action="store_true")
    a = ap.parse_args(argv)

    env = load_env()
    host = hosting.GitHubRawHost(W.ROOT)
    if a.cmd == "prepare":
        return emit(prepare_images(Path(a.pack).resolve()))
    needs_token = a.cmd in ("whoami", "limit", "token-status", "refresh-token") or getattr(a, "confirm", False)
    client = None
    if env.get("IG_ACCESS_TOKEN"):
        client = make_client(env)
    elif needs_token:
        client = make_client(env)      # 沒有 token 會印出說明並結束
    warns = []
    real_publish = a.cmd not in ("publish", "publish-image") or a.confirm     # dry-run 不自動 refresh，也不寫 .env
    if client and a.cmd != "token-status" and real_publish:
        warns = ensure_token_fresh(client, env)
        env = load_env()
        client.token = env["IG_ACCESS_TOKEN"]

    if a.cmd == "whoami":
        try:
            me = client.me()
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e), "hint": e.hint()})
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        if not a.no_write:
            if not env.get("IG_USER_ID") and me.get("user_id"):
                set_env("IG_USER_ID", str(me["user_id"]))
            if not env.get("IG_TOKEN_REFRESHED_AT"):
                set_env("IG_TOKEN_REFRESHED_AT", now_iso)
        out = {"ok": True, "user_id": me.get("user_id"), "username": me.get("username"), "warnings": warns}
        if a.no_write:
            out["suggested_IG_TOKEN_REFRESHED_AT"] = now_iso      # API 查不到 token 的核發時間；剛產生的 token 就填現在
            out["note"] = "--no-write：沒有修改 .env"
        return emit(out)
    if a.cmd == "limit":
        try:
            return emit({"ok": True, "limit": client.publishing_limit(), "warnings": warns})
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e), "hint": e.hint()})
    if a.cmd == "token-status":
        left = token_days_left(env)
        return emit({"ok": True, "days_left": None if left is None else round(left, 1),
                     "warning": None if left is None or left >= WARN_DAYS else f"剩餘效期少於 {WARN_DAYS} 天，請 refresh-token"})
    if a.cmd == "refresh-token":
        try:
            body = client.refresh_token()
        except ig_api.IGError as e:
            return emit({"ok": False, "error": str(e)})
        set_env("IG_ACCESS_TOKEN", body["access_token"])
        set_env("IG_TOKEN_REFRESHED_AT", dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        return emit({"ok": True, "expires_in_s": body.get("expires_in"), "note": "新 token 已寫入 .env（不會顯示）"})
    if a.cmd == "publish":
        return emit(publish_carousel(Path(a.pack).resolve(), a.confirm, env, client, host, record=not a.no_record) | {"warnings": warns})
    if a.cmd == "publish-image":
        return emit(publish_image(Path(a.image).resolve(), a.caption, a.alt, a.confirm, env, client, host) | {"warnings": warns})
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
