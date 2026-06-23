"""신규 공고 + 커넥터 건강상태를 HTML 메일로 렌더링."""
from __future__ import annotations

import html
from datetime import datetime

from .models import ConnectorResult, Item

_REGION_COLOR = {"서울": "#2563eb", "경기": "#7c3aed", "전북": "#059669", "전국": "#6b7280"}


def _esc(s: str) -> str:
    return html.escape(s or "")


def _item_row(it: Item) -> str:
    rc = _REGION_COLOR.get(it.region, "#6b7280")
    meta = " · ".join(x for x in [it.org, it.period, it.posted] if x)
    return f"""
    <tr>
      <td style="padding:10px 12px;border-bottom:1px solid #eee;">
        <a href="{_esc(it.url)}" style="color:#111;font-weight:600;text-decoration:none;font-size:14px;">
          {_esc(it.title)}</a>
        <div style="margin-top:4px;font-size:12px;color:#666;">
          <span style="background:{rc};color:#fff;border-radius:3px;padding:1px 6px;">{_esc(it.region)}</span>
          <span style="background:#f1f1f1;border-radius:3px;padding:1px 6px;margin-left:4px;">{_esc(it.source)}</span>
          <span style="margin-left:6px;">{_esc(meta)}</span>
        </div>
      </td>
    </tr>"""


def render(new_items: list[Item], results: list[ConnectorResult]) -> tuple[str, str]:
    """(subject, html_body) 반환."""
    today = datetime.now().strftime("%Y-%m-%d")
    broken = [r for r in results if not r.ok]
    healthy = [r for r in results if r.ok]

    # 분야별 그룹 (자르지 않고 전부 노출)
    by_cat: dict[str, list[Item]] = {}
    for it in new_items:
        by_cat.setdefault(it.category, []).append(it)

    subject = f"[창업지원 {today}] 신규 {len(new_items)}건"
    if broken:
        subject += f" · ⚠ 점검필요 {len(broken)}곳"

    parts = [f"""<div style="max-width:680px;margin:0 auto;font-family:'Apple SD Gothic Neo',sans-serif;">
      <h2 style="margin:0 0 4px;">🚀 창업지원 공고 알림</h2>
      <p style="color:#666;margin:0 0 16px;font-size:13px;">{today} · 신규 {len(new_items)}건 ·
      수집 소스 {len(healthy)}/{len(results)} 정상</p>"""]

    if not new_items:
        parts.append('<p style="color:#888;">오늘은 매칭된 신규 공고가 없습니다.</p>')

    for cat, items in by_cat.items():
        parts.append(f"""
        <h3 style="margin:18px 0 6px;border-left:4px solid #2563eb;padding-left:8px;">
          {_esc(cat)} <span style="color:#999;font-size:13px;font-weight:400;">({len(items)})</span></h3>
        <table style="width:100%;border-collapse:collapse;">{''.join(_item_row(i) for i in items)}</table>""")

    # 자진신고: 깨진 커넥터
    if broken:
        rows = "".join(
            f'<li><b>{_esc(r.source)}</b> — <span style="color:#b91c1c;">{_esc(r.error)}</span></li>'
            for r in broken
        )
        parts.append(f"""
        <div style="margin-top:24px;padding:12px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;">
          <b style="color:#b91c1c;">⚠ 유지보수 필요 ({len(broken)}곳)</b>
          <p style="margin:4px 0 8px;font-size:12px;color:#7f1d1d;">
            아래 소스는 수집 실패(사이트 개편/엔드포인트 변경 등). 셀렉터·엔드포인트 점검 필요.</p>
          <ul style="margin:0;padding-left:18px;font-size:12px;color:#7f1d1d;">{rows}</ul>
        </div>""")

    parts.append("""
      <p style="margin-top:24px;color:#bbb;font-size:11px;">
        자동수집 · GitHub Actions · 공고 누락/오탐은 키워드(core/config.py) 조정으로 보정</p>
    </div>""")
    return subject, "".join(parts)
