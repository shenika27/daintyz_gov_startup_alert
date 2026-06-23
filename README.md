# 창업지원 공고 알리미 🚀

캐릭터 디자인 · 캐릭터/3D프린팅 굿즈 제조 분야에 맞는 **정부·지자체·진흥원 창업지원 공고**를
주기적으로 수집해 **네이버 메일**로 보내주는 GitHub Actions 봇.

- 수집은 GitHub Actions(cron)가 돌린다. 내 PC/서버 불필요.
- 소스 하나가 깨져도 나머지는 정상 동작하고, **깨진 소스는 메일에 "⚠ 유지보수 필요"로 자진신고**한다.

## 소스 구성

| 구분 | 소스 | 수집 방식 |
|---|---|---|
| A 종합 | 기업마당(bizinfo), K-Startup | 오픈 API (안정) |
| B 분야 | KOCCA, welcon, 한국디자인진흥원, 소상공인마당 | 스크래핑 |
| C 지역·타깃 | 여성기업센터, 서울SBA, 경기GCON, 전북(jcon/JICA/jbci), 위비티 | 스크래핑 |

> 스크래퍼 셀렉터는 `connectors/sources.py` 의 초기 추정값이다. 첫 메일의 "유지보수 필요"
> 목록을 보고 해당 소스 셀렉터만 실제 DOM에 맞게 한 줄씩 교정하면 된다.

## 분야 키워드

`core/config.py` 의 `CATEGORIES` 에서 조정. 4개 묶음(캐릭터/IP, 굿즈/제조, 3D/메이커, 창업/타깃).
공고가 너무 많거나(노이즈) 누락되면 여기 키워드만 손보면 된다.

## 셋업 (GitHub repo 만든 뒤)

### 1. repo Secrets 등록
`Settings → Secrets and variables → Actions → New repository secret`

| 시크릿 | 값 | 발급처 |
|---|---|---|
| `BIZINFO_KEY` | 기업마당 인증키(crtfcKey) | bizinfo.go.kr → 활용정보 → 정책정보 개방(API 신청) |
| `KSTARTUP_KEY` | data.go.kr serviceKey(**디코딩** 원본) | data.go.kr → "창업진흥원 K-Startup 조회서비스" 활용신청 |
| `NAVER_USER` | 네이버 아이디(또는 전체 메일주소) | — |
| `NAVER_PASS` | 네이버 메일 SMTP 비밀번호 | 네이버 메일 → 환경설정 → POP3/SMTP **사용 ON** (2단계인증 시 앱비밀번호) |
| `MAIL_TO` | 받는 주소 (기본 seungtk@eco.co.kr) | 쉼표로 여러 명 가능 |

> 네이버: 메일 환경설정에서 **"POP3/IMAP" 사용**을 켜야 SMTP 발송이 됩니다.
> 2단계 인증을 쓰면 일반 비번이 아니라 **애플리케이션 비밀번호**를 `NAVER_PASS`에 넣으세요.

### 2. 동작 확인
`Actions` 탭 → "창업지원 공고 알림" → **Run workflow**(수동 실행)로 즉시 테스트.

### 3. 주기
`.github/workflows/alert.yml` 의 `cron` 수정 (기본: 매주 월·목 09:00 KST).

## 로컬 테스트
```bash
pip install -r requirements.txt
export BIZINFO_KEY=... KSTARTUP_KEY=... NAVER_USER=... NAVER_PASS=...
python main.py
```

## 구조
```
main.py                  오케스트레이터
core/                    config·필터·중복제거·렌더·메일·http
connectors/
  api_bizinfo.py         기업마당 API
  api_kstartup.py        K-Startup API
  generic_scraper.py     셀렉터 기반 범용 스크래퍼
  sources.py             스크래퍼 소스 목록(여기만 고치면 됨)
state/seen.json          발송기록(중복방지) — Actions가 자동 커밋
```
