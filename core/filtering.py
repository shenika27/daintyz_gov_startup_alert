"""키워드 매칭 / 노이즈 제거 / 분야 태깅."""
from __future__ import annotations

from .config import CATEGORIES, EXCLUDE, KEEP_SIGNALS, OFF_TOPIC_FIELDS
from .models import Item


def _norm(s: str) -> str:
    return (s or "").replace(" ", "").lower()


def classify(text: str) -> list[str]:
    """텍스트에 걸리는 분야 카테고리들을 반환 (없으면 빈 리스트)."""
    n = _norm(text)
    hits = []
    for cat, kws in CATEGORIES.items():
        if any(_norm(kw) in n for kw in kws):
            hits.append(cat)
    return hits


def is_excluded(title: str) -> bool:
    n = _norm(title)
    return any(_norm(x) in n for x in EXCLUDE)


def keep(item: Item) -> bool:
    """이 공고를 메일에 넣을지 판단하고, 통과 시 item.category 를 보정한다."""
    if is_excluded(item.title):
        return False
    haystack = f"{item.title} {item.org}"
    cats = classify(haystack)
    if not cats:
        return False
    # 커넥터가 category 를 안 줬으면 매칭된 분야로 채움
    item.category = item.category or " · ".join(cats)
    return True


def filter_items(items: list[Item]) -> list[Item]:
    out, seen = [], set()
    for it in items:
        if it.uid in seen:
            continue
        if keep(it):
            seen.add(it.uid)
            out.append(it)
    return out


def is_off_topic(item: Item) -> bool:
    """제목이 명백히 다른 분야를 가리키고, 캐릭터/디자인 신호가 전혀 없는가.

    여성·일반 창업지원처럼 분야 특정이 없는 공고는 False(=유지). 제목에
    타분야 키워드가 있어도 KEEP_SIGNALS(캐릭터·디자인 등)가 함께 있으면 유지.
    """
    n = _norm(item.title)
    if not any(_norm(k) in n for k in OFF_TOPIC_FIELDS):
        return False
    if any(_norm(s) in n for s in KEEP_SIGNALS):
        return False
    return True


def refilter_offtopic(items: list[Item]) -> list[Item]:
    """발송 직전 2차 필터 — 캐릭터/디자인과 무관한 타분야 공고만 제외한다."""
    return [it for it in items if not is_off_topic(it)]
