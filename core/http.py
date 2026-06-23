"""HTTP 공통 (User-Agent 고정, 타임아웃)."""
from __future__ import annotations

import requests

from .config import HTTP_TIMEOUT

UA = "Mozilla/5.0 (compatible; gov-startup-alert/1.0; +https://github.com)"


def get(url: str, params: dict | None = None) -> requests.Response:
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r
