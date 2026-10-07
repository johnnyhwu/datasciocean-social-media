"""IG 與 Threads 發佈共用的小工具：.env 讀寫、token 效期與自動 refresh、圖片（JPEG）驗證。

只放「兩個平台都用」的東西；平台專屬的在 ig_publish.py、threads_publish.py。
憑證只放 .env（已在 .gitignore）或環境變數（IG_*、THREADS_*）；這裡的函式不會把 token 印出來。
"""
from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path

import cardlib as W
import hosting
import ig_api

ENV_PATH = W.ROOT / ".env"
TOKEN_LIFETIME_DAYS = 60
WARN_DAYS = 14                 # 剩餘效期少於這個天數就警告，並在 token 存在滿 24 小時時自動 refresh
MIN_WIDTH, MAX_WIDTH = 320, 1440
RATIO_MIN, RATIO_MAX = 4 / 5, 1.91
MAX_BYTES = hosting.MAX_BYTES


def load_env(path: Path = ENV_PATH) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$", line)
            if m and not line.lstrip().startswith("#"):
                env[m.group(1)] = m.group(2).strip("\"'")
    for k, v in os.environ.items():       # 環境變數優先於 .env（IG_*、THREADS_*）
        if k.startswith(("IG_", "THREADS_")) and v:
            env[k] = v
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


def token_days_left(env: dict, now: dt.datetime | None = None, ts_key: str = "IG_TOKEN_REFRESHED_AT") -> float | None:
    ts = env.get(ts_key)
    if not ts:
        return None
    now = now or dt.datetime.now(dt.timezone.utc)
    t0 = dt.datetime.fromisoformat(ts)
    if t0.tzinfo is None:
        t0 = t0.replace(tzinfo=dt.timezone.utc)
    return TOKEN_LIFETIME_DAYS - (now - t0).total_seconds() / 86400


def ensure_token_fresh(client: ig_api.IGClient, env: dict, now: dt.datetime | None = None, env_path: Path = ENV_PATH,
                       token_key: str = "IG_ACCESS_TOKEN", ts_key: str = "IG_TOKEN_REFRESHED_AT") -> list[str]:
    """剩餘效期過短時警告；token 存在滿 24 小時才會自動 refresh。回傳警告訊息（不含 token）。"""
    warns = []
    left = token_days_left(env, now, ts_key)
    if left is None:
        warns.append(f"{ts_key} 未設定，無法追蹤 token 效期（whoami 成功後會自動補上）")
        return warns
    if left < WARN_DAYS:
        warns.append(f"token 剩餘約 {left:.0f} 天，少於 {WARN_DAYS} 天")
        age_days = TOKEN_LIFETIME_DAYS - left
        if age_days >= 1 and left > 0:
            try:
                body = client.refresh_token()
                set_env(token_key, body["access_token"], env_path)
                set_env(ts_key, (now or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"), env_path)
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
