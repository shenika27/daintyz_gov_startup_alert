"""HTTP 공통 (User-Agent 고정, 타임아웃).

UA 는 실제 브라우저로 위장한다. 다수 공공기관 사이트가 봇 UA(이름에
crawler/bot 류)를 403 으로 차단하기 때문이다(위비티·일부 data.go.kr 등).
SSL 인증서 체인이 불완전한 사이트(중간 CA 누락)는 검증 실패 시
verify=False 로 1회 재시도한다.
"""
from __future__ import annotations

import requests
import urllib3

from .config import HTTP_TIMEOUT

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}


def get(url: str, params: dict | None = None) -> requests.Response:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=HTTP_TIMEOUT)
    except requests.exceptions.SSLError:
        # 중간 CA 누락 사이트(예: JICA) 대응 — 검증 끄고 1회 재시도
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(url, params=params, headers=HEADERS,
                         timeout=HTTP_TIMEOUT, verify=False)
    r.raise_for_status()
    return r


def get_rendered(url: str, wait_selector: str | None = None) -> str:
    """JS 렌더링 후 HTML 반환 (Playwright headless Chromium).

    정적 요청으로 목록이 안 나오는 JS/SPA 게시판용. playwright 는
    선택 의존성이라 여기서만 지연 import 한다(미설치 시 명확한 안내).
    wait_selector 가 있으면 그 요소가 뜰 때까지 대기(목록 로딩 보장).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "playwright 미설치 — `pip install playwright && playwright install chromium`"
        ) from e

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(user_agent=UA, extra_http_headers={
            "Accept-Language": HEADERS["Accept-Language"],
        })
        try:
            page.goto(url, wait_until="networkidle", timeout=HTTP_TIMEOUT * 1000 + 15000)
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=10000)
            return page.content()
        finally:
            browser.close()
