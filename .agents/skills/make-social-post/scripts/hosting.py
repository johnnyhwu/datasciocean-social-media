"""圖片託管介面：Meta 要從「公開、不需登入、可直接下載、不帶 query 參數」的網址抓圖。

介面：Host.upload(local_path) -> public_url。換託管只改這裡（例如 Cloudflare R2、自己的網站）。
目前實作：GitHubRawHost——用這個公開 repo 的 raw 網址。它**不會**自動 commit 或 push；
圖要先 commit 並 push，網址才會有東西（發文前 check_public() 會確認抓得到）。
"""
from __future__ import annotations

import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024    # 8 MiB


class Host:
    def upload(self, local_path: Path) -> str:
        raise NotImplementedError


class GitHubRawHost(Host):
    def __init__(self, repo_root: Path, remote_url: str | None = None, branch: str = "main"):
        self.root = Path(repo_root).resolve()
        remote = remote_url or subprocess.run(["git", "remote", "get-url", "origin"], cwd=self.root, capture_output=True,
                                              text=True, check=True).stdout.strip()
        m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote)
        if not m:
            raise ValueError(f"不是 GitHub 的 remote：{remote}")
        self.owner, self.repo, self.branch = m.group(1), m.group(2), branch

    def upload(self, local_path: Path) -> str:
        rel = Path(local_path).resolve().relative_to(self.root).as_posix()
        if re.search(r"[\s?#%]", rel):
            raise ValueError(f"路徑含空白或特殊字元，網址會不乾淨：{rel}")
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{rel}"


def check_public(url: str, opener=urllib.request.urlopen) -> tuple[bool, str]:
    """確認網址公開可抓、是 JPEG、不到 8 MiB、不帶 query。回傳 (ok, 說明)。"""
    if "?" in url:
        return False, "網址不得帶 query 參數"
    try:
        with opener(urllib.request.Request(url, method="GET"), timeout=30) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            data = r.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}（還沒 commit 並 push，或 repo 不是公開的？）"
    except (urllib.error.URLError, TimeoutError) as e:
        return False, f"連不上：{e}"
    if len(data) > MAX_BYTES:
        return False, "檔案超過 8 MiB"
    if data[:3] != b"\xff\xd8\xff":
        return False, f"內容不是 JPEG（Content-Type: {ctype}）"
    return True, f"OK（{ctype}，{len(data) // 1024} KB）"
