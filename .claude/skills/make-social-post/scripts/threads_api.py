"""Threads 官方 API 的最小客戶端（Meta 官方，host: graph.threads.net 或 graph.threads.com）。

沿用 ig_api.IGClient 的底層（重試只限暫時性錯誤、token 清除、transport 可注入）；只換主機、端點與 token 續期方式。
文件依據：references/threads-publish.md（官方文件的整理與還沒驗證的事項）。
"""
from __future__ import annotations

import os
import time

import ig_api
from ig_api import IGError, scrub

API_HOST = os.environ.get("THREADS_API_HOST", "https://graph.threads.net")
API_VERSION = os.environ.get("THREADS_API_VERSION", "v1.0")

INITIAL_WAIT_S = 30        # 官方：建好 container 後平均約等 30 秒再發佈
POLL_INTERVAL_S = 10
POLL_MAX_ATTEMPTS = 12
TEXT_MAX = 500


class ThreadsClient(ig_api.IGClient):
    def __init__(self, token: str, user_id: str | None = None, version: str = API_VERSION, host: str = API_HOST,
                 transport=ig_api.default_transport, sleep=time.sleep):
        super().__init__(token, user_id, version=version, host=host, transport=transport, sleep=sleep)

    def _uid(self) -> str:
        return self.user_id or "me"

    def me(self) -> dict:
        return self._call("GET", "me", {"fields": "id,username"})

    def publishing_limit(self) -> dict:
        """端點與欄位官方頁沒有寫清楚（還沒驗證）；失敗時呼叫端要容錯。"""
        return self._call("GET", f"{self._uid()}/threads_publishing_limit",
                          {"fields": "quota_usage,config,reply_quota_usage,reply_config"})

    def create_post(self, media_type: str, text: str | None = None, image_url: str | None = None,
                    link_attachment: str | None = None, reply_to_id: str | None = None) -> str:
        p: dict = {"media_type": media_type}
        if text:
            p["text"] = text
        if image_url:
            p["image_url"] = image_url
        if link_attachment and media_type == "TEXT":      # link_attachment 只限純文字貼文
            p["link_attachment"] = link_attachment
        if reply_to_id:
            p["reply_to_id"] = reply_to_id
        return self._call("POST", f"{self._uid()}/threads", p)["id"]

    def container_status(self, container_id: str) -> str:
        return self._call("GET", container_id, {"fields": "status,error_message"}).get("status", "")

    def wait_ready(self, container_id: str, initial_wait: int = INITIAL_WAIT_S, interval: int = POLL_INTERVAL_S,
                   max_attempts: int = POLL_MAX_ATTEMPTS) -> str:
        """先等官方建議的約 30 秒，再輪詢 status。狀態值官方沒列全：FINISHED／PUBLISHED 視為好了，ERROR／EXPIRED 失敗，其餘繼續等。"""
        self.sleep(initial_wait)
        for i in range(1, max_attempts + 1):
            st = self.container_status(container_id)
            if st in ("FINISHED", "PUBLISHED"):
                return st
            if st in ("ERROR", "EXPIRED"):
                raise IGError(f"container {container_id} 狀態 {st}")
            if i < max_attempts:
                self.sleep(interval)
        raise IGError(f"container {container_id} 在 {max_attempts} 次查詢內沒有完成（最後狀態 {st!r}）")

    def publish(self, container_id: str) -> str:
        return self._call("POST", f"{self._uid()}/threads_publish", {"creation_id": container_id}, retry=False)["id"]

    def media_info(self, media_id: str) -> dict:
        return self._call("GET", media_id, {"fields": "permalink,timestamp"})

    def delete(self, media_id: str) -> dict:
        """DELETE /{threads-media-id}；需要 threads_delete 權限，每天 100 次。"""
        return self._call("DELETE", media_id, {}, retry=False)

    # ---- token ----
    def debug_token(self) -> dict:
        """GET /debug_token：查 token 實際被授予的權限（scopes）、是否有效、到期時間（unixtime）。
        官方：access_token 要是「同一個 App 的 Threads tester 的 user token」，用同一顆 token 檢查自己即可。"""
        body = self._call("GET", "debug_token", {"input_token": self.token})
        return body.get("data", body)

    def refresh_token(self) -> dict:
        """GET /refresh_access_token?grant_type=th_refresh_token；token 存在滿 24 小時、未過期才能 refresh。"""
        status, body = self.transport("GET", f"{self.host}/refresh_access_token",
                                      {"grant_type": "th_refresh_token", "access_token": self.token})
        if status >= 400 or "error" in body:
            e = body.get("error", {})
            raise IGError(scrub(f"refresh 失敗：HTTP {status}｜{e.get('message', '')}", self.token), code=e.get("code"), http=status)
        return body

    def exchange_token(self, app_secret: str) -> dict:
        """短效（1 小時）token 換成長效（60 天）token；需要 app secret，只在本機執行。"""
        status, body = self.transport("GET", f"{self.host}/access_token",
                                      {"grant_type": "th_exchange_token", "client_secret": app_secret, "access_token": self.token})
        if status >= 400 or "error" in body:
            e = body.get("error", {})
            raise IGError(scrub(f"換長效 token 失敗：HTTP {status}｜{e.get('message', '')}", self.token, app_secret), code=e.get("code"), http=status)
        return body
