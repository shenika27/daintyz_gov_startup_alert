"""K-Startup(창업진흥원) 사업공고 오픈 API 커넥터 — data.go.kr.

데이터셋: 창업진흥원_K-Startup 조회서비스 (data.go.kr/data/15125364).
응답이 JSON/XML 둘 다 가능 — 여기선 XML(response/body/items/item)을 파싱.
엔드포인트/필드명이 개편될 수 있으므로 실패 시 자진신고된다.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from core import config
from core.http import get
from core.models import Item

SOURCE = "K-Startup"

# 응답 필드명이 버전마다 달라 후보를 순서대로 시도
_TITLE_KEYS = ("biz_pbanc_nm", "pbanc_nm", "intg_pbanc_biz_nm", "title")
_ORG_KEYS = ("pbanc_ntrp_nm", "spnsr_organ_nm", "supt_biz_intrd_nm", "organ")
_PERIOD_KEYS = ("pbanc_rcpt_bgng_dt", "rcrt_prgs_yn", "reqstBeginEndDe")
_URL_KEYS = ("detl_pg_url", "biz_pbanc_url", "pbancUrl")


def _first(node: ET.Element, keys) -> str:
    for k in keys:
        v = node.findtext(k)
        if v and v.strip():
            return v.strip()
    return ""


def fetch() -> list[Item]:
    if not config.KSTARTUP_KEY:
        raise RuntimeError("KSTARTUP_KEY 시크릿이 비어 있습니다.")

    r = get(config.KSTARTUP_URL, params={
        "serviceKey": config.KSTARTUP_KEY,
        "numOfRows": "100",
        "pageNo": "1",
    })
    root = ET.fromstring(r.content)

    # data.go.kr 표준 에러 바디 감지
    err = root.findtext(".//returnReasonCode") or root.findtext(".//errMsg")
    if err and not root.findall(".//item"):
        raise RuntimeError(f"API 에러 응답: {err}")

    items: list[Item] = []
    for node in root.findall(".//item"):
        title = _first(node, _TITLE_KEYS)
        if not title:
            continue
        url = _first(node, _URL_KEYS) or "https://www.k-startup.go.kr/"
        items.append(Item(
            source=SOURCE, category="", title=title, url=url,
            org=_first(node, _ORG_KEYS), period=_first(node, _PERIOD_KEYS),
            region="전국",
        ))
    if not items:
        raise RuntimeError("응답에서 item 0건 (엔드포인트/serviceKey/필드명 확인 필요)")
    return items
