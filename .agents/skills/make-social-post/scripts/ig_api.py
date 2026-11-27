"""Instagram API with Instagram Login 的最小客戶端（Meta 官方 API，host: graph.instagram.com）。

只用標準函式庫（urllib）。不使用任何第三方封裝服務。
文件依據：references/instagram-publish.md（官方文件的整理與還沒驗證的事項）。

安全：access token 只從環境變數或 .env 讀；任何錯誤訊息、log 都經過 scrub()，不得出現 token。
測試：transport 可注入（tests/test_ig_publish.py 用假的 transport，不連網）。
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API_HOST = os.environ.get("IG_API_HOST", "https://graph.instagram.com")
API_VERSION = os.environ.get("IG_API_VERSION", "v25.0")     # 以官方文件目前範例的最新版為準，可用環境變數覆寫

# 官方建議：每分鐘查一次容器狀態，最多 5 分鐘
POLL_INTERVAL_S = 60
POLL_MAX_ATTEMPTS = 5
# 可重試的錯誤：網路錯誤、HTTP 5xx、API 錯誤碼 1、2（未知／服務暫時錯誤）。其餘（含 9004、9、190）不重試
TRANSIENT_CODES = {1, 2}
MAX_RETRIES = 3

HINTS = {
    9004: "Meta 抓不到圖片：檢查網址是否公開、不需登入、不帶 query 參數、確實是 JPEG",
    9007: "容器還沒 FINISHED：等狀態變成 FINISHED 再發佈",
    9: "超過發文上限：用 content_publishing_limit 查用量，明天再試",
    190: "token 無效或已過期：到 App Dashboard 重新產生，或在到期前執行 refresh-token",
    36000: "圖片太大（需小於 8 MiB）",
    36001: "圖片格式不支援（只支援 JPEG）",
}


def scrub(text: str, token: str | None = None, *more: str) -> str:
    """把 token（與其他祕密，例如 app secret）從任何文字裡拿掉。"""
    out = str(text)
    for secret in (token, *more):
        if secret:
            out = out.replace(secret, "***")
    return re.sub(r"((?:access_token|client_secret)=)[^&\s\"']+", r"\1***", out)


class IGError(Exception):
    def __init__(self, message: str, code: int | None = None, subcode: int | None = None, http: int | None = None,
                 transient: bool = False):
        super().__init__(message)
        self.code, self.subcode, self.http, self.transient = code, subcode, http, transient

    def hint(self) -> str:
        return HINTS.get(self.subcode_hint(), "")

    def subcode_hint(self):
        return self.code if self.code in HINTS else None


def default_transport(method: str, url: str, params: dict) -> tuple[int, dict]:
    """GET 把參數放在 query；POST 用 form body。回傳 (HTTP 狀態碼, JSON)。"""
    data = None
    if method in ("GET", "DELETE"):
        url = f"{url}?{urllib.parse.urlencode(params)}"
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": {"message": body[:300]}}


class IGClient:
    def __init__(self, token: str, user_id: str | None = None, version: str = API_VERSION, host: str = API_HOST,
                 transport=default_transport, sleep=time.sleep):
        self.token, self.user_id, self.version, self.host = token, user_id, version, host.rstrip("/")
        self.transport, self.sleep = transport, sleep

    # ---- 底層 ----
    def _url(self, path: str) -> str:
        return f"{self.host}/{self.version}/{path.lstrip('/')}"

    def _call(self, method: str, path: str, params: dict | None = None, retry: bool = True) -> dict:
        p = dict(params or {})
        p["access_token"] = self.token
        attempts = MAX_RETRIES if retry else 1
        for i in range(1, attempts + 1):
            try:
                status, body = self.transport(method, self._url(path), p)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                err = IGError(f"網路錯誤：{scrub(e, self.token)}", transient=True)
            else:
                if status < 400 and "error" not in body:
                    return body
                e = body.get("error", {})
                code = e.get("code")
                err = IGError(scrub(f"HTTP {status}｜code {code}｜subcode {e.get('error_subcode')}｜{e.get('message', '')}", self.token),
                              code=code, subcode=e.get("error_subcode"), http=status,
                              transient=(status >= 500 or code in TRANSIENT_CODES))
            if not err.transient or i == attempts:
                raise err
            self.sleep(2 ** i)       # 可重試的錯誤才重試，有上限
        raise AssertionError("unreachable")

    # ---- 帳號與額度 ----
    def me(self) -> dict:
        return self._call("GET", "me", {"fields": "user_id,username"})

    def publishing_limit(self) -> dict:
        return self._call("GET", f"{self._uid()}/content_publishing_limit", {"fields": "quota_usage,config"})

    def _uid(self) -> str:
        if not self.user_id:
            raise IGError("沒有 IG_USER_ID：先執行 whoami 確認帳號")
        return self.user_id

    # ---- 容器 ----
    def create_container(self, image_url: str | None = None, caption: str | None = None, alt_text: str | None = None,
                         carousel_item: bool = False, children: list[str] | None = None,
                         is_ai_generated: bool = False) -> str:
        p: dict = {}
        if children is not None:
            p.update(media_type="CAROUSEL", children=",".join(children))
        else:
            p["image_url"] = image_url
        if carousel_item:
            p["is_carousel_item"] = "true"
        if caption and not carousel_item:      # 輪播的 caption 只放在 carousel container；子項不支援
            p["caption"] = caption
        if alt_text and children is None:
            p["alt_text"] = alt_text
        if is_ai_generated and not carousel_item:   # 輪播只能設在 carousel container，子項會報錯
            p["is_ai_generated"] = "true"
        return self._call("POST", f"{self._uid()}/media", p)["id"]

    def container_status(self, container_id: str) -> str:
        return self._call("GET", container_id, {"fields": "status_code"}).get("status_code", "")

    def wait_finished(self, container_id: str, interval: int = POLL_INTERVAL_S, max_attempts: int = POLL_MAX_ATTEMPTS) -> str:
        for i in range(1, max_attempts + 1):
            st = self.container_status(container_id)
            if st == "FINISHED":
                return st
            if st in ("ERROR", "EXPIRED"):
                raise IGError(f"容器 {container_id} 狀態 {st}", transient=False)
            if i < max_attempts:
                self.sleep(interval)
        raise IGError(f"容器 {container_id} 在 {max_attempts} 次查詢內沒有 FINISHED（官方建議每分鐘查一次、最多 5 分鐘）", code=9007)

    def publish(self, container_id: str) -> str:
        return self._call("POST", f"{self._uid()}/media_publish", {"creation_id": container_id}, retry=False)["id"]

    def media_info(self, media_id: str) -> dict:
        return self._call("GET", media_id, {"fields": "permalink,timestamp"})

    # ---- token ----
    def refresh_token(self) -> dict:
        """官方：GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token。token 需存在滿 24 小時、未過期。"""
        url = f"{self.host}/refresh_access_token"
        status, body = self.transport("GET", url, {"grant_type": "ig_refresh_token", "access_token": self.token})
        if status >= 400 or "error" in body:
            e = body.get("error", {})
            raise IGError(scrub(f"refresh 失敗：HTTP {status}｜{e.get('message', '')}", self.token), code=e.get("code"), http=status)
        return body    # access_token、token_type、expires_in
