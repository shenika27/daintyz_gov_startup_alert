"""기업마당(bizinfo) 오픈 API 커넥터 — RSS(XML) 응답.

엔드포인트: https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do?crtfcKey=KEY
가장 광범위한 수집기. 부처·지자체·진흥원 공고가 여기로 모인다.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from core import config
from core.http import get
from core.models import Item

SOURCE = "기업마당"


def fetch() -> list[Item]:
    if not config.BIZINFO_KEY:
        raise RuntimeError("BIZINFO_KEY 시크릿이 비어 있습니다.")

    # dataType=rss 가 기본. searchCnt 로 넉넉히 받아 클라이언트 필터.
    r = get(config.BIZINFO_URL, params={
        "crtfcKey": config.BIZINFO_KEY,
        "dataType": "rss",
        "searchCnt": "200",
    })
    root = ET.fromstring(r.content)

    items: list[Item] = []
    for node in root.iter("item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        if not title or not link:
            continue
        desc = (node.findtext("description") or "").strip()
        pub = (node.findtext("pubDate") or "").strip()
        # bizinfo RSS는 description 안에 기관/기간이 섞여 옴 → org 자리에 desc 일부 활용
        items.append(Item(
            source=SOURCE, category="", title=title, url=link,
            org=desc[:60], posted=pub[:16], region="전국",
        ))
    if not items:
        # 키가 틀리거나 응답 포맷이 바뀌면 0건 → 자진신고 유도
        raise RuntimeError("응답에서 item 0건 (crtfcKey 또는 응답포맷 확인 필요)")
    return items
