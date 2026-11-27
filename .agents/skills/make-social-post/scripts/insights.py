#!/usr/bin/env python3
"""流量追蹤：用 IG 與 Threads 官方 API（唯讀）抓每則已發布貼文的成效與帳號追蹤數，存成快照。

只讀不寫：只呼叫 GET /{id}/insights、GET /{user}（追蹤數）、GET /{user}/threads_insights。
憑證只從 .env 讀；**輸出（螢幕、檔案）一律先拿掉 token**：API 回傳的 paging 網址會夾帶 access_token
（2026-11-21 實測外洩過一次），所以回應只取需要的欄位、丟掉 paging，寫出前再用 token 字串與格式各掃一次。

用法（repo 根目錄）：
  uv run python .agents/skills/make-social-post/scripts/insights.py pull            # 抓全部、寫 growth/snapshots/<今天>.json、印表
  uv run python .agents/skills/make-social-post/scripts/insights.py pull --no-write # 只印表
  uv run python .agents/skills/make-social-post/scripts/insights.py table [快照]     # 印某個快照（預設最新）
流程（什麼時候跑、怎麼變成 insight 與 action）：references/growth-loop.md。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish_common as pc  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
STATE = ROOT / "state"
GROWTH = ROOT / "growth"
SNAP = GROWTH / "snapshots"
EXPERIMENTS = GROWTH / "experiments.md"

IG_METRICS = "views,reach,likes,comments,saved,shares,follows,profile_visits,total_interactions"
TH_METRICS = "views,likes,replies,reposts,quotes,shares"
TOKEN_RE = re.compile(r"(IGAA|IGQV|THAA|EAA)[A-Za-z0-9_\-]{20,}")


def scrub(text: str, tokens: list[str]) -> str:
    for t in tokens:
        if t:
            text = text.replace(t, "***")
    return TOKEN_RE.sub("***", text)


def metric_values(body: dict) -> dict:
    """insights 回應 → {指標: 數值}；只取 data，丟掉 paging（paging 網址含 token）。"""
    out = {}
    for m in body.get("data", []) or []:
        v = None
        if m.get("values"):
            v = m["values"][0].get("value")
        elif isinstance(m.get("total_value"), dict):
            v = m["total_value"].get("value")
        out[m.get("name")] = v
    return out


def load_published() -> list[dict]:
    """state/*.yaml → 每個觀念一筆：系列、hook 樣態、兩個平台的發布時間與網址。"""
    import yaml
    rows = []
    for f in sorted(STATE.glob("*.yaml")):
        st = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        posts = [p for p in st.get("posts", []) or [] if isinstance(p, dict)]
        if not posts:
            continue
        r = {"concept": st.get("concept", f.stem)}
        for p in posts:
            k = "ig" if p.get("format") == "ig_carousel" else "th" if p.get("format") == "threads_thread" else None
            if not k:
                continue
            r["series"] = p.get("series_id")
            r["hook_type"] = p.get("hook_type")
            r[f"{k}_url"] = p.get("url")
            r[f"{k}_published_at"] = p.get("published_at")
        rows.append(r)
    return rows


def media_ids() -> tuple[dict, dict]:
    """發佈紀錄 → {觀念: IG media_id}、{觀念: Threads root_id}（後寫的蓋前面；--no-record 的測試發文沒有觀念，不列入）。"""
    ig, th = {}, {}
    for path, key, d in ((STATE / "ig-publish-log.jsonl", "media_id", ig), (STATE / "threads-publish-log.jsonl", "root_id", th)):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                x = json.loads(line)
            except json.JSONDecodeError:
                continue
            if x.get("concept") and x.get(key):
                d[x["concept"]] = x[key]
    return ig, th


def experiment_tags() -> dict:
    """growth/experiments.md 的「套用紀錄」表 → {觀念: [action id…]}。第一欄是觀念 id、第三欄是 action id（逗號分隔）。"""
    tags = {}
    if not EXPERIMENTS.exists():
        return tags
    sec = None
    for line in EXPERIMENTS.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            sec = line[3:].strip()
            continue
        if not sec or not sec.startswith("套用紀錄") or not line.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"[a-z0-9\-]+", cells[0] or ""):
            tags[cells[0]] = [a.strip() for a in cells[2].split(",") if re.fullmatch(r"[A-Z]\d+", a.strip())]
    return tags


def spec_meta(concept: str) -> dict:
    hits = list((ROOT / "out").glob(f"*/{concept}/_build/spec.json"))
    if not hits:
        return {}
    try:
        s = json.loads(hits[0].read_text(encoding="utf-8"))
    except Exception:
        return {}
    cover = (s.get("slides") or [{}])[0]
    return {"slides": len(s.get("slides") or []),
            "cover": re.sub(r"\[\[|\]\]", "", (cover.get("title") or "")).replace("\n", ""),
            "threads_mode": (s.get("threads") or {}).get("mode")}


def age_days(ts: str | None, now: dt.datetime) -> float | None:
    if not ts:
        return None
    try:
        t = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return None
    return round((now - t).total_seconds() / 86400, 1)


def pull(ig_client, th_client, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    igm, thm = media_ids()
    tags = experiment_tags()
    posts = []
    for r in load_published():
        c = r["concept"]
        row = {**r, **spec_meta(c), "experiments": tags.get(c, [])}
        row["ig_age_days"] = age_days(r.get("ig_published_at"), now)
        row["th_age_days"] = age_days(r.get("th_published_at"), now)
        if c in igm:
            try:
                row["ig"] = metric_values(ig_client._call("GET", f"{igm[c]}/insights", {"metric": IG_METRICS}, retry=False))
            except Exception as e:
                row["ig_error"] = str(e)[:160]
        if c in thm:
            try:
                row["th"] = metric_values(th_client._call("GET", f"{thm[c]}/insights", {"metric": TH_METRICS}, retry=False))
            except Exception as e:
                row["th_error"] = str(e)[:160]
        posts.append(row)
    account = {}
    try:
        b = ig_client._call("GET", ig_client._uid(), {"fields": "followers_count,media_count"}, retry=False)
        account["ig_followers"] = b.get("followers_count")
    except Exception as e:
        account["ig_error"] = str(e)[:160]
    try:
        account["th_followers"] = metric_values(th_client._call("GET", f"{th_client._uid()}/threads_insights", {"metric": "followers_count"}, retry=False)).get("followers_count")
    except Exception as e:
        account["th_error"] = str(e)[:160]
    return {"taken_at": now.strftime("%Y-%m-%dT%H:%M:%S%z"), "account": account, "posts": posts}


def table(snap: dict) -> str:
    a = snap.get("account", {})
    lines = [f"快照 {snap.get('taken_at')}｜IG 追蹤 {a.get('ig_followers')}｜Threads 追蹤 {a.get('th_followers')}",
             f"{'發布日':10} {'觀念':40} {'天':>4} | {'IG看':>5} {'觸及':>4} {'讚':>3} {'藏':>3} {'享':>3} {'追':>3} {'訪':>3} | {'TH看':>5} {'讚':>3} {'回':>3} {'享':>3} | 實驗"]
    for p in sorted(snap.get("posts", []), key=lambda p: p.get("ig_published_at") or p.get("th_published_at") or ""):
        i, t = p.get("ig") or {}, p.get("th") or {}
        if not i and not t:
            continue
        g = lambda d, k: "" if d.get(k) is None else d.get(k)
        lines.append(f"{(p.get('ig_published_at') or p.get('th_published_at') or '')[:10]:10} {p['concept'][:40]:40} {g(p, 'ig_age_days'):>4} | "
                     f"{g(i, 'views'):>5} {g(i, 'reach'):>4} {g(i, 'likes'):>3} {g(i, 'saved'):>3} {g(i, 'shares'):>3} {g(i, 'follows'):>3} {g(i, 'profile_visits'):>3} | "
                     f"{g(t, 'views'):>5} {g(t, 'likes'):>3} {g(t, 'replies'):>3} {g(t, 'shares'):>3} | {','.join(p.get('experiments') or [])}")
    return "\n".join(lines)


def clients():
    import ig_api
    import threads_api as TA
    env = pc.load_env()
    ig = ig_api.IGClient(env["IG_ACCESS_TOKEN"], env.get("IG_USER_ID"), version=env.get("IG_API_VERSION") or ig_api.API_VERSION)
    th = TA.ThreadsClient(env["THREADS_ACCESS_TOKEN"], env.get("THREADS_USER_ID"), version=env.get("THREADS_API_VERSION") or TA.API_VERSION)
    return ig, th, [env.get("IG_ACCESS_TOKEN", ""), env.get("THREADS_ACCESS_TOKEN", "")]


def safe_dump(obj, tokens: list[str]) -> str:
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    s = scrub(s, tokens)
    if TOKEN_RE.search(s) or any(t and t in s for t in tokens):
        raise RuntimeError("輸出裡還有 token 的樣子，不寫出")
    return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pull")
    p.add_argument("--no-write", action="store_true")
    t = sub.add_parser("table")
    t.add_argument("snapshot", nargs="?")
    a = ap.parse_args(argv)
    if a.cmd == "table":
        f = Path(a.snapshot) if a.snapshot else max(SNAP.glob("*.json"))
        print(table(json.loads(f.read_text(encoding="utf-8"))))
        return 0
    ig, th, toks = clients()
    snap = pull(ig, th)
    text = safe_dump(snap, toks)
    if not a.no_write:
        SNAP.mkdir(parents=True, exist_ok=True)
        out = SNAP / f"{snap['taken_at'][:10]}.json"
        out.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")
    print(scrub(table(json.loads(text)), toks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
