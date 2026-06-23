"""스크래퍼 소스 정의 (B: 분야특화 / C: 지역·타깃).

각 dict 가 범용 스크래퍼 1개를 만든다. 추출 모드는 3가지(generic_scraper 참고):

  ▸ link_re 모드(권장·저유지보수): 상세페이지 href 정규식만 주면 매칭 <a> 수확
  ▸ onclick_re + url_tpl 모드: href 없이 JS(onclick)로만 여는 게시판용
  ▸ row 모드: row/link/date CSS 셀렉터로 행 순회 (정적·안정적 표)

공통 키
  name   : 메일에 표시될 소스명
  region : 서울/경기/전북/전국
  url    : 공고 목록 페이지
  base   : 상대링크 합칠 기준 (생략 시 url)
  js     : True 면 headless 브라우저로 렌더링 후 파싱 (JS 게시판)
  limit  : 수확 최대 개수 (기본 40)

⚠ 사이트 개편 시 해당 줄의 link_re/onclick_re/url 한 줄만 고치면 된다.
   링크 URL 패턴 기반이라 표/리스트 마크업 변경에는 잘 안 깨진다.
   수집 실패 시 0건 → 예외 → 메일 하단 '유지보수 필요'로 자진신고.
   (2026-06: 전 소스 셀렉터→링크패턴 방식으로 교정)
"""

SCRAPER_SOURCES: list[dict] = [
    # --- B. 분야 특화 -----------------------------------------------------
    {
        "name": "KOCCA(콘텐츠진흥원)", "region": "전국",
        "url": "https://www.kocca.kr/kocca/pims/list.do?menuNo=204104",
        "base": "https://www.kocca.kr",
        "row": "table tbody tr", "link": "a", "date": "td.date, td:last-child",
    },
    {
        # 상세는 href 없이 onclick="fnEdit('<id>')" → ID로 URL 조립
        "name": "welcon", "region": "전국", "js": True,
        "url": "https://welcon.kocca.kr/ko/info/business",
        "base": "https://welcon.kocca.kr",
        "onclick_re": r"fnEdit\('(\d+)'\)",
        "url_tpl": "/ko/info/business/{id}",
    },
    {
        # 상세는 onclick="submitForm(this,'view',<id>)" → GET view URL 조립
        "name": "한국디자인진흥원", "region": "전국",
        "url": "https://www.kidp.or.kr/?menuno=1202",
        "base": "https://www.kidp.or.kr",
        "onclick_re": r"submitForm\(this,'view',(\d+)\)",
        "url_tpl": "https://www.kidp.or.kr/index.html?menuno=1202&mode=view&no={id}",
    },
    # 소상공인마당(sbiz.or.kr)은 소상공인24(sbiz24.kr) 인증형 SPA로 이전되어
    # 정적 스크래핑 불가. 소상공인 공고는 기업마당(api_bizinfo)·K-Startup API로
    # 이미 커버되므로 별도 스크래퍼 제거. (재도입 시 sbiz24 인증토큰 필요)

    # --- C. 지역·타깃 -----------------------------------------------------
    {
        # 목록 페이지는 AJAX라 메인의 상세링크(bizNewDetail.do)를 수확
        "name": "여성기업종합지원센터", "region": "전국",
        "url": "https://www.wbiz.or.kr/",
        "base": "https://www.wbiz.or.kr",
        "link_re": r"bizNewDetail\.do", "min_title": 8,
    },
    {
        # 사업공고 목록(sbcu31l1)은 리다이렉트되어 메인의 지원사업 상세링크 수확
        "name": "서울경제진흥원(SBA)", "region": "서울",
        "url": "https://www.sba.seoul.kr/",
        "base": "https://www.sba.seoul.kr/",
        "link_re": r"Company_Support_Detail\.aspx",
    },
    {
        "name": "경기콘텐츠진흥원(GCON)", "region": "경기", "js": True,
        "url": "https://www.gcon.or.kr/gcon/business/gconNotice/list.do?menuNo=200061",
        "base": "https://www.gcon.or.kr/gcon/business/gconNotice/list.do",
        "link_re": r"view\.do",
    },
    {
        "name": "전북콘텐츠융합진흥원", "region": "전북",
        "url": "https://www.jcon.or.kr/board/list.php?pageId=C000000016",
        "base": "https://www.jcon.or.kr/board/",
        "link_re": r"view\.php",
    },
    {
        # SSL 중간 CA 누락 → core.http 가 verify=False 로 재시도
        "name": "전주정보문화산업진흥원(JICA)", "region": "전북",
        "url": "https://www.jica.or.kr/2025/inner.php?sMenu=A1000",
        "base": "https://www.jica.or.kr/2025/",
        "link_re": r"mode=view",
    },
    {
        "name": "전북창조경제혁신센터", "region": "전북",
        "url": "https://www.jbci.or.kr/sub/business_1.html",
        "base": "https://www.jbci.or.kr/sub/",
        "link_re": r"business_1_view\.html",
    },
    # --- 공모전 (캐릭터·굿즈 디자인) --------------------------------------
    {
        "name": "위비티(공모전)", "region": "전국",
        "url": "https://www.wevity.com/?c=find&s=1&gbn=list&gp=1&sw=캐릭터",
        "base": "https://www.wevity.com",
        "row": "ul.list li, table tbody tr", "link": "a", "date": ".day, .date",
    },
]
