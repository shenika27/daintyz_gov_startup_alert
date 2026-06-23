"""공통 데이터 모델 + 커넥터 격리 래퍼.

설계 핵심: 모든 소스(커넥터)는 ConnectorResult 하나로 정규화된다.
하나가 깨져도 main 루프는 멈추지 않고, 깨진 커넥터는 ok=False + error 로
"자진신고" 한다. (메일 하단에 '유지보수 필요'로 출력)
"""
from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Item:
    """공고 1건."""
    source: str            # 커넥터 이름 (예: "기업마당")
    category: str          # 분야 태그 (캐릭터/IP, 굿즈/제조, 3D/메이커, 창업/타깃)
    title: str
    url: str
    org: str = ""          # 소관/주관 기관
    period: str = ""       # 신청기간
    posted: str = ""       # 게시일
    region: str = "전국"    # 서울/경기/전북/전국

    @property
    def uid(self) -> str:
        """중복발송 방지 키. URL이 가장 안정적."""
        return self.url.strip() or f"{self.source}:{self.title}"


@dataclass
class ConnectorResult:
    source: str
    ok: bool
    items: list[Item] = field(default_factory=list)
    error: str = ""        # ok=False 일 때 사유 (메일에 노출)


def run_connector(name: str, fn: Callable[[], list[Item]]) -> ConnectorResult:
    """커넥터를 격리 실행한다. 어떤 예외도 프로세스를 죽이지 않는다."""
    try:
        items = fn() or []
        return ConnectorResult(source=name, ok=True, items=items)
    except Exception as e:  # noqa: BLE001  (의도적으로 전부 잡는다)
        tb = traceback.format_exc(limit=2).strip().splitlines()
        reason = f"{type(e).__name__}: {e}"
        if tb:
            reason = f"{reason} ({tb[-1].strip()[:120]})"
        return ConnectorResult(source=name, ok=False, error=reason)
