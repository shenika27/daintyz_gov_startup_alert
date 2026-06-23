"""K-Startup(창업진흥원) 사업공고 오픈 API 커넥터 — data.go.kr.

데이터셋: 창업진흥원_K-Startup 조회서비스 (data.go.kr/data/15125364).
응답 XML 구조는 <item> 아래에 <col name="필드명">값</col> 형태다.
(과거 <필드명>값</필드명> 구조에서 개편됨 → 2026-06 교정)
필드/엔드포인트가 또 바뀌면 0건 → 예외로 자진신고된다.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from core import config
from core.http import get
from core.models import Item

SOURCE = "K-Startup"

# col name 후보 (버전별 차이 대비, 순서대로 시도)
_TITLE_KEYS = ("biz_pbanc_nm", "intg_pbanc_biz_nm", "pbanc_nm", "title")
_ORG_KEYS = ("pbanc_ntrp_nm", "sprv_inst", "spnsr_organ_nm", "organ")
_URL_KEYS = ("detl_pg_url", "biz_aply_url", "biz_gdnc_url", "pbancUrl")
_BGN_KEYS = ("pbanc_rcpt_bgng_dt",)
_END_KEYS = ("pbanc_rcpt_end_dt",)
_REGION_KEYS = ("supt_regin",)


def _cols(node: ET.Element) -> dict[str, str]:
    """<item> 의 <col name=..> 들을 {name: text} 로 평탄화."""
    out: dict[str, str] = {}
    for col in node.findall("col"):
        name = col.get("name")
        if name:
            out[name] = (col.text or "").strip()
    return out


def _first(cols: dict[str, str], keys) -> str:
    for k in keys:
        v = cols.get(k)
        if v:
            return v
    return ""


def _ymd(s: str) -> str:
    """20260629 -> 2026-06-29 (그 외 형식은 원문 유지)."""
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 and s.isdigit() else s


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
        cols = _cols(node)
        title = _first(cols, _TITLE_KEYS)
        if not title:
            continue
        bgn, end = _first(cols, _BGN_KEYS), _first(cols, _END_KEYS)
        period = " ~ ".join(filter(None, (_ymd(bgn), _ymd(end))))
        items.append(Item(
            source=SOURCE, category="", title=title,
            url=_first(cols, _URL_KEYS) or "https://www.k-startup.go.kr/",
            org=_first(cols, _ORG_KEYS), period=period,
            region=_first(cols, _REGION_KEYS) or "전국",
        ))
    if not items:
        raise RuntimeError("응답에서 item 0건 (엔드포인트/serviceKey/필드명 확인 필요)")
    return items
