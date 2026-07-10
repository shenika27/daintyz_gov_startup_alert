"""오케스트레이터: 전 소스 수집 -> 필터 -> 중복제거 -> 네이버 메일 발송.

흐름
  1. API 커넥터(기업마당, K-Startup) + 스크래퍼 커넥터(sources.py) 전부 격리 실행
  2. 키워드 필터(분야 4종) + 노이즈 제거
  3. seen.json 대비 신규만 추출 (첫 실행은 FIRST_RUN_CAP 으로 폭탄 방지)
  4. 신규가 있거나 / 깨진 소스가 있으면 메일 발송 (점검필요 자진신고 포함)
  5. seen.json 갱신 -> 워크플로가 커밋
"""
from __future__ import annotations

import sys

from connectors import api_bizinfo, api_kstartup
from connectors.generic_scraper import make_fetch
from connectors.sources import SCRAPER_SOURCES
from core import config, dedup, mailer
from core.filtering import filter_items, refilter_offtopic
from core.models import ConnectorResult, run_connector
from core.render import render


def collect() -> list[ConnectorResult]:
    results = [
        run_connector(api_bizinfo.SOURCE, api_bizinfo.fetch),
        run_connector(api_kstartup.SOURCE, api_kstartup.fetch),
    ]
    for spec in SCRAPER_SOURCES:
        results.append(run_connector(spec["name"], make_fetch(spec)))
    return results


def main() -> int:
    results = collect()

    all_items = [it for r in results if r.ok for it in r.items]
    matched1 = filter_items(all_items)         # 1차: 분야 커버리지(넓게)
    matched = refilter_offtopic(matched1)      # 2차: 캐릭터/디자인 무관 타분야만 제외

    seen = dedup.load_seen()
    first_run = len(seen) == 0
    new_items = dedup.split_new(matched, seen)
    if first_run and len(new_items) > config.FIRST_RUN_CAP:
        # 최신순 가정이 어려우므로 단순 cap (나머지는 seen 처리되어 다음부터 안 옴)
        new_items = new_items[: config.FIRST_RUN_CAP]

    broken = [r for r in results if not r.ok]

    # 로그 (Actions 콘솔)
    print(f"수집 소스 {len(results)}곳 / 정상 {len(results) - len(broken)} / "
          f"수집 {len(all_items)}건 / 1차매칭 {len(matched1)} / 타분야컷후 {len(matched)} / "
          f"신규 {len(new_items)}")
    for r in broken:
        print(f"  ⚠ 점검필요: {r.source} -> {r.error}")

    if not new_items and not broken:
        print("신규 공고 없음 + 전 소스 정상 → 메일 생략")
    else:
        subject, body = render(new_items, results)
        mailer.send(subject, body)
        print(f"메일 발송 완료: {subject}")

    # seen 갱신 (신규로 보낸 것 + 첫 실행이면 매칭분 전체 기록해 폭탄 방지)
    to_remember = matched if first_run else new_items
    seen = dedup.commit(seen, to_remember)
    dedup.save_seen(seen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
