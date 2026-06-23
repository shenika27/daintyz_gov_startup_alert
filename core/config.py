"""설정값 + 키워드 분류 + 시크릿(환경변수) 로딩.

비밀값은 코드에 두지 않는다. GitHub Actions의 repo secrets -> env 로 주입.
"""
from __future__ import annotations

import os

# --- 시크릿 (GitHub repo secrets로 주입) ---------------------------------
BIZINFO_KEY = os.getenv("BIZINFO_KEY", "")          # 기업마당 crtfcKey
KSTARTUP_KEY = os.getenv("KSTARTUP_KEY", "")        # data.go.kr serviceKey (디코딩된 원본)

NAVER_USER = os.getenv("NAVER_USER", "")            # 네이버 아이디 (메일 발송 계정)
NAVER_PASS = os.getenv("NAVER_PASS", "")            # SMTP 비밀번호(또는 앱 비밀번호)
MAIL_FROM = os.getenv("MAIL_FROM", "") or (
    f"{NAVER_USER}@naver.com" if NAVER_USER and "@" not in NAVER_USER else NAVER_USER
)
MAIL_TO = os.getenv("MAIL_TO", "seungtk@eco.co.kr")  # 받는 사람 (쉼표로 여러 명 가능)

# 엔드포인트는 깨질 때를 대비해 env로 override 가능
BIZINFO_URL = os.getenv("BIZINFO_URL", "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do")
KSTARTUP_URL = os.getenv(
    "KSTARTUP_URL",
    "https://apis.data.go.kr/B552735/kisedKstartupService01/getAnnouncementInformation01",
)

# --- 동작 파라미터 -------------------------------------------------------
SEEN_PATH = os.getenv("SEEN_PATH", "state/seen.json")
SEEN_TTL_DAYS = int(os.getenv("SEEN_TTL_DAYS", "180"))   # 이 기간 지난 uid는 정리
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "20"))
# 첫 실행 시 과거 공고 폭탄 방지 (seen 비었을 때 신규로 보낼 최대 건수)
FIRST_RUN_CAP = int(os.getenv("FIRST_RUN_CAP", "40"))

# --- 분야 키워드 (이게 노이즈/커버리지를 좌우한다) ------------------------
# 카테고리명 -> 키워드 목록. 제목/기관/내용에 하나라도 걸리면 매칭.
CATEGORIES: dict[str, list[str]] = {
    "캐릭터/IP": [
        "캐릭터", "IP", "지식재산", "라이선싱", "라이선스", "콘텐츠",
        "일러스트", "이모티콘", "웹툰", "아트", "브랜드",
    ],
    "굿즈/제조": [
        "굿즈", "팬시", "문구", "디자인상품", "디자인 상품", "머천다이징",
        "상품화", "제품화", "시제품", "제조혁신", "제조 창업", "공예", "소상공인 제조",
    ],
    "3D/메이커": [
        "3D프린팅", "3D 프린팅", "3D프린터", "3D 프린터", "메이커", "메이커스페이스",
        "목업", "모형", "디지털제조", "스마트제조",
    ],
    "창업/타깃": [
        "예비창업", "초기창업", "창업패키지", "도약패키지", "1인 창조기업",
        "1인창조기업", "여성창업", "여성기업", "디자인", "콘텐츠 스타트업",
    ],
}

# 명백한 노이즈 제외어 (제목에 있으면 버림)
EXCLUDE = [
    "채용", "정규직", "계약직", "입찰공고", "낙찰", "용역", "납품업체",
    "청렴", "부패", "회의록", "정기총회",
]
