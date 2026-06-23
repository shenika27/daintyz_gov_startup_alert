"""범용 스크래퍼 — 셀렉터를 config(sources.py)로 받아 게시판을 긁는다.

스크래퍼 8개를 따로 만들지 않고 이 하나 + config 로 처리한다.
사이트가 개편돼 셀렉터가 안 맞으면 '0건' → 예외 → 자진신고(메일 점검필요).
고칠 땐 sources.py 의 셀렉터 한 줄만 수정.
"""
from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from core.http import get
from core.models import Item


def make_fetch(spec: dict):
    """sources.py 의 스펙(dict) -> fetch() 함수 생성."""

    def fetch() -> list[Item]:
        r = get(spec["url"])
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select(spec["row"])
        if not rows:
            raise RuntimeError(f"목록 셀렉터 '{spec['row']}' 매칭 0건 (개편 추정)")

        base = spec.get("base") or spec["url"]
        items: list[Item] = []
        for row in rows[: spec.get("limit", 40)]:
            a = row.select_one(spec.get("link", "a"))
            if not a:
                continue
            title = (a.get_text(strip=True) or "").strip()
            href = a.get("href", "").strip()
            if not title or not href:
                continue
            url = urljoin(base, href)
            date_el = row.select_one(spec["date"]) if spec.get("date") else None
            posted = date_el.get_text(strip=True) if date_el else ""
            items.append(Item(
                source=spec["name"], category="", title=title, url=url,
                org=spec.get("org", spec["name"]), posted=posted,
                region=spec.get("region", "전국"),
            ))
        if not items:
            raise RuntimeError("행은 찾았으나 제목/링크 추출 0건 (셀렉터 점검)")
        return items

    return fetch
