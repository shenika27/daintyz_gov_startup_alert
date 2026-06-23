"""키워드 매칭 / 노이즈 제거 / 분야 태깅."""
from __future__ import annotations

from .config import CATEGORIES, EXCLUDE
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
