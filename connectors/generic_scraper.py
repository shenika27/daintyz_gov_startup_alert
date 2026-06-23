"""범용 스크래퍼 — 셀렉터/링크패턴을 config(sources.py)로 받아 게시판을 긁는다.

스크래퍼를 따로 만들지 않고 이 하나 + config 로 처리한다.
두 가지 추출 모드를 지원(둘 다 실패 시 0건 → 예외 → 자진신고):

  1) link_re 모드 (권장·저유지보수)
       상세페이지 href 정규식만 주면, 페이지의 모든 <a> 중 매칭되는 것을
       공고로 수확한다. 사이트가 표/리스트 마크업을 바꿔도 링크 URL 패턴만
       유지되면 계속 동작한다. (CSS 셀렉터보다 훨씬 덜 깨짐)
  2) row 모드 (기존)
       row/link/date CSS 셀렉터로 행을 순회. 정적이고 표가 안정적인 곳용.

js:true 면 정적 요청 대신 headless 브라우저로 렌더링 후 파싱(JS 게시판용).
"""
from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.http import get, get_rendered
from core.models import Item


def _load_html(spec: dict) -> str:
    if spec.get("js"):
        return get_rendered(spec["url"], wait_selector=spec.get("wait"))
    return get(spec["url"]).text


def _by_link_re(spec: dict, soup: BeautifulSoup, base: str) -> list[Item]:
    """href 정규식으로 공고 링크 수확 (저유지보수 모드)."""
    pat = re.compile(spec["link_re"])
    min_len = spec.get("min_title", 6)
    items: list[Item] = []
    seen: set[str] = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        if not href or not pat.search(href):
            continue
        title = a.get_text(strip=True)
        if len(title) < min_len:
            continue
        url = urljoin(base, href)
        if url in seen:
            continue
        seen.add(url)
        items.append(Item(
            source=spec["name"], category="", title=title, url=url,
            org=spec.get("org", spec["name"]), region=spec.get("region", "전국"),
        ))
        if len(items) >= spec.get("limit", 40):
            break
    return items


def _by_onclick(spec: dict, soup: BeautifulSoup, base: str) -> list[Item]:
    """onclick 의 ID 로 상세 URL 을 조립 (JS 게시판용·저유지보수 모드).

    예) onclick="fnEdit('1957926')" + url_tpl="/ko/info/business/{id}"
    href 가 없고 자바스크립트로만 상세를 여는 한국 공공 게시판에 대응.
    """
    pat = re.compile(spec["onclick_re"])
    tpl = spec["url_tpl"]
    min_len = spec.get("min_title", 6)
    items: list[Item] = []
    seen: set[str] = set()
    for el in soup.select("[onclick]"):
        m = pat.search(el.get("onclick", ""))
        if not m:
            continue
        title = el.get_text(strip=True)
        if len(title) < min_len:
            continue
        url = urljoin(base, tpl.format(id=m.group(1)))
        if url in seen:
            continue
        seen.add(url)
        items.append(Item(
            source=spec["name"], category="", title=title, url=url,
            org=spec.get("org", spec["name"]), region=spec.get("region", "전국"),
        ))
        if len(items) >= spec.get("limit", 40):
            break
    return items


def _by_rows(spec: dict, soup: BeautifulSoup, base: str) -> list[Item]:
    """row/link/date CSS 셀렉터로 행 순회 (기존 모드)."""
    rows = soup.select(spec["row"])
    if not rows:
        raise RuntimeError(f"목록 셀렉터 '{spec['row']}' 매칭 0건 (개편 추정)")
    items: list[Item] = []
    for row in rows[: spec.get("limit", 40)]:
        a = row.select_one(spec.get("link", "a"))
        if not a:
            continue
        title = (a.get_text(strip=True) or "").strip()
        href = a.get("href", "").strip()
        if not title or not href:
            continue
        date_el = row.select_one(spec["date"]) if spec.get("date") else None
        posted = date_el.get_text(strip=True) if date_el else ""
        items.append(Item(
            source=spec["name"], category="", title=title, url=urljoin(base, href),
            org=spec.get("org", spec["name"]), posted=posted,
            region=spec.get("region", "전국"),
        ))
    return items


def make_fetch(spec: dict):
    """sources.py 의 스펙(dict) -> fetch() 함수 생성."""

    def fetch() -> list[Item]:
        soup = BeautifulSoup(_load_html(spec), "html.parser")
        base = spec.get("base") or spec["url"]
        if spec.get("onclick_re"):
            items = _by_onclick(spec, soup, base)
        elif spec.get("link_re"):
            items = _by_link_re(spec, soup, base)
        else:
            items = _by_rows(spec, soup, base)
        if not items:
            raise RuntimeError("행/링크 추출 0건 (셀렉터·link_re 점검)")
        return items

    return fetch
