"""중복발송 방지: 이미 보낸 공고 uid를 state/seen.json 에 기록.

GitHub Actions 워크플로가 매 실행 후 seen.json 변경분을 커밋한다.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta

from .config import SEEN_PATH, SEEN_TTL_DAYS
from .models import Item


def load_seen() -> dict[str, str]:
    if not os.path.exists(SEEN_PATH):
        return {}
    try:
        with open(SEEN_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_seen(seen: dict[str, str]) -> None:
    os.makedirs(os.path.dirname(SEEN_PATH) or ".", exist_ok=True)
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=0, sort_keys=True)


def _prune(seen: dict[str, str]) -> dict[str, str]:
    cutoff = date.today() - timedelta(days=SEEN_TTL_DAYS)
    out = {}
    for uid, d in seen.items():
        try:
            if datetime.strptime(d, "%Y-%m-%d").date() >= cutoff:
                out[uid] = d
        except (ValueError, TypeError):
            out[uid] = d  # 형식 이상하면 보존
    return out


def split_new(items: list[Item], seen: dict[str, str]) -> list[Item]:
    """seen 에 없는 신규만 반환. (seen 갱신은 commit() 에서)"""
    return [it for it in items if it.uid not in seen]


def commit(seen: dict[str, str], items: list[Item]) -> dict[str, str]:
    """보낸 공고를 seen 에 추가하고 오래된 항목 정리 후 반환."""
    today = date.today().isoformat()
    for it in items:
        seen[it.uid] = today
    return _prune(seen)
