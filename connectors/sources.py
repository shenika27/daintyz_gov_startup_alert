"""스크래퍼 소스 정의 (B: 분야특화 / C: 지역·타깃).

각 dict 가 범용 스크래퍼 1개를 만든다.
  name   : 메일에 표시될 소스명
  region : 서울/경기/전북/전국
  url    : 공고 목록 페이지
  base   : 상대링크 합칠 기준 (생략 시 url)
  row    : 목록의 각 행(공고 1건) CSS 셀렉터
  link   : 행 안의 <a> 셀렉터 (제목+링크). 기본 "a"
  date   : 행 안의 게시일 셀렉터 (선택)
  limit  : 행 최대 개수

⚠ 아래 셀렉터는 "초기 추정값"이다. 사이트 실제 DOM에 맞춰
   첫 메일의 '유지보수 필요' 보고를 보고 한 줄씩 교정하면 된다.
   (이 자진신고 구조가 본 프로젝트의 핵심)
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
        "name": "welcon", "region": "전국",
        "url": "https://welcon.kocca.kr/ko/businessList",
        "base": "https://welcon.kocca.kr",
        "row": "ul.list li, table tbody tr", "link": "a", "date": ".date",
    },
    {
        "name": "한국디자인진흥원", "region": "전국",
        "url": "https://www.kidp.or.kr/?menuno=1116",
        "base": "https://www.kidp.or.kr",
        "row": "table tbody tr", "link": "a", "date": "td:last-child",
    },
    {
        "name": "소상공인마당", "region": "전국",
        "url": "https://www.sbiz.or.kr/sup/info/supportList.do",
        "base": "https://www.sbiz.or.kr",
        "row": "table tbody tr, ul.list li", "link": "a", "date": ".date, td:last-child",
    },
    # --- C. 지역·타깃 -----------------------------------------------------
    {
        "name": "여성기업종합지원센터", "region": "전국",
        "url": "https://www.wbiz.or.kr/board/notice/list.do",
        "base": "https://www.wbiz.or.kr",
        "row": "table tbody tr", "link": "a", "date": "td:last-child",
    },
    {
        "name": "서울산업진흥원(SBA)", "region": "서울",
        "url": "https://www.sba.seoul.kr/Pages/Apply/ApplyList.aspx",
        "base": "https://www.sba.seoul.kr",
        "row": "ul.list li, table tbody tr", "link": "a", "date": ".date",
    },
    {
        "name": "경기콘텐츠진흥원(GCON)", "region": "경기",
        "url": "https://www.gcon.or.kr/user/board/list.do?boardId=notice",
        "base": "https://www.gcon.or.kr",
        "row": "table tbody tr, ul.board_list li", "link": "a", "date": ".date, td:last-child",
    },
    {
        "name": "전북콘텐츠융합진흥원", "region": "전북",
        "url": "https://www.jcon.or.kr/board/index.php?pageId=C000000007",
        "base": "https://www.jcon.or.kr",
        "row": "table tbody tr, .board_list li", "link": "a", "date": ".date, td:last-child",
    },
    {
        "name": "전주정보문화산업진흥원(JICA)", "region": "전북",
        "url": "https://www.jica.or.kr/main/inc/sub.php?menu=business",
        "base": "https://www.jica.or.kr",
        "row": "table tbody tr, ul.list li", "link": "a", "date": ".date",
    },
    {
        "name": "전북창조경제혁신센터", "region": "전북",
        "url": "https://www.jbci.or.kr/board/notice",
        "base": "https://www.jbci.or.kr",
        "row": "table tbody tr, .list li", "link": "a", "date": ".date, td:last-child",
    },
    # --- 공모전 (캐릭터·굿즈 디자인) --------------------------------------
    {
        "name": "위비티(공모전)", "region": "전국",
        "url": "https://www.wevity.com/?c=find&s=1&gbn=list&gp=1&sw=캐릭터",
        "base": "https://www.wevity.com",
        "row": "ul.list li, table tbody tr", "link": "a", "date": ".day, .date",
    },
]
