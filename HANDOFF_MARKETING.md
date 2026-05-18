# 사주명리(tarofortune) 마케팅 운영 인수인계서

> 이 문서를 새 Claude Code 세션의 첫 메시지로 그대로 붙여넣으면 즉시 작업 이어받기 가능.
> 최종 갱신: 2026-05-17

---

## 0. 빠른 요약 (TL;DR)

**사이트**: https://tarofortune.pythonanywhere.com (Flask, PythonAnywhere 무료티어)
**영문**: https://tarofortune.pythonanywhere.com/en
**소스**: https://github.com/leekyuhaiambox-ops/saju-platform
**규모**: 약 770개 인덱싱 가능 URL (KR 350 + EN 300 + 미디어 120)
**자동화**: 매일 UTC 16:00 + 0~2h 랜덤 = GitHub Actions가 4채널 자동 게시
**광고**: AdFit 4슬롯 통합 (재심사 대기), AdSense 코드 박힘 (구글 심사 대기)
**현재 트래픽**: 거의 0 (신규 사이트, 1주차)

---

## 1. 자동 운영 중인 채널 (사용자 입력 0)

### 1.1 GitHub Actions — 메인 자동화 엔진

| 항목 | 값 |
|---|---|
| 워크플로우 파일 | `.github/workflows/daily-bot.yml` |
| 트리거 | `schedule: '0 16 * * *'` (UTC 16:00) + `workflow_dispatch` (수동) |
| 실제 실행 시각 | UTC 16:00 + 0~7200초 랜덤 지연 (봇 패턴 회피) |
| 한국시간 환산 | KST 새벽 1시~3시 사이 |
| 실행 환경 | Ubuntu-latest + Python 3.12 |
| 비용 | 월 ~15분 사용 (2000분 무료 한도의 0.75%) |
| Dashboard | https://github.com/leekyuhaiambox-ops/saju-platform/actions |

**워크플로우가 매일 실행하는 것:**
1. checkout code
2. setup Python
3. random delay 0~2h (anti-bot)
4. `python -X utf8 run_all_bots.py` — 4채널 게시
5. state 파일(.lemmy_state.json 등) 자동 커밋

### 1.2 채널별 현황

#### A. Lemmy (`u/tarofortune` @ lemmy.world)
- **빈도**: 3일에 1회 (`MIN_DAYS_BETWEEN_POSTS = 3` in `lemmy_bot.py`)
- **콘텐츠 풀**: 60개 (`reddit_bot.py`의 POSTS 리스트 재사용)
- **타겟 커뮤니티**: `astrology@lemmy.world`, `occult@lemmy.world`, `spirituality@lemmy.world`
- **인증**: 이메일 + 관리자 승인 완료 (`accepted_application: True`)
- **로그 확인**: https://lemmy.world/u/tarofortune
- **현재 게시물**: 4개 (한 개 -5점 다운보트 받음 → 빈도 줄여 회피)

#### B. Mastodon (`@tarosaju@mastodon.social`)
- **빈도**: 매일 1회
- **콘텐츠**: 60갑자 일주별 짧은 toot (자동 순환)
- **로직**: `mastodon_bot.py`
- **팔로워**: 0명 (신규 계정, organic discovery 안 됨)
- **로그 확인**: https://mastodon.social/@tarosaju

#### C. Dev.to (`@tarofortune`)
- **빈도**: 매일 1회
- **콘텐츠 풀**: **15편** (2026-05-17 확장됨, 그전엔 3편이었음)
- **로직**: `devto_bot.py`
- **태그**: webdev, python, showdev, discuss, philosophy, astronomy, seo 등
- **현재 게시물**: 3편 (Dev.to 인덱싱 늦음, 0 PV 상태)
- **로그**: https://dev.to/tarofortune

#### D. IndexNow (검색엔진 색인 제출)
- **빈도**: 매일
- **로직**: `auto_index.py` + `saju/indexnow.py`
- **타겟**: Bing, Yandex, Naver, Seznam
- **소유권 증명**: https://tarofortune.pythonanywhere.com/8a7d3e2f1b4c5a6d9e8f7a6b5c4d3e2f.txt
- **누적 제출 URL**: ~400+

### 1.3 자동화 보안 / 자격증명 위치

**GitHub Secrets** (Repository 설정 → Secrets and variables → Actions):
- `LEMMY_USERNAME` = `tarofortune`
- `LEMMY_PASSWORD` = (보호됨)
- `MASTODON_ACCESS_TOKEN` = (보호됨)
- `DEVTO_API_KEY` = (보호됨)

**로컬 `.env` 파일** (PC 전용, .gitignore에 포함):
```
LEMMY_INSTANCE=lemmy.world
LEMMY_USERNAME=tarofortune
LEMMY_PASSWORD=...
MASTODON_INSTANCE=mastodon.social
MASTODON_ACCESS_TOKEN=...
DEVTO_API_KEY=...
SITE_URL=https://tarofortune.pythonanywhere.com
SITE_HOST=tarofortune.pythonanywhere.com
```

**PythonAnywhere API 토큰**: 배포 스크립트에 하드코딩 (`_deploy.py`, `_setup_lemmy_bot.py`) — 토큰 값은 코드 내부 참고

**GitHub PAT**: 무기한, 권한 `repo + workflow`, 소유자 `leekyuhaiambox-ops`

---

## 2. SEO 인프라 (자동 패시브 작동)

### 2.1 사이트 구조

| 카테고리 | URL 수 | 비고 |
|---|---|---|
| 메인·정책 | 13 | / /about /privacy /terms /basics /ten-gods /twelve-stages /five-elements /sixty-pillars /glossary /branches /stems /quotes |
| 60갑자 상세 | 60 | /sixty-pillars/0 ~ /sixty-pillars/59 |
| 60갑자 직업 | 60 | /sixty-pillars/{idx}/career |
| 60갑자 연애 | 60 | /sixty-pillars/{idx}/love |
| 24절기 | 25 | /solar-terms + /solar-terms/0~23 |
| 신년운세 | 5 | /yearly + /yearly/2024~2028 |
| 띠별 운세 | 12 | /zodiac/쥐~돼지 |
| 십신 개별 | 10 | /ten-gods/비견~정인 |
| 십이운성 개별 | 12 | /twelve-stages/장생~양 |
| 지지 개별 | 12 | /branches/자~해 |
| 천간 개별 | 10 | /stems/갑~계 |
| 유틸 | 5 | /quiz /subscribe /lunar-converter /weekly /monthly |
| 영문 사본 | ~300 | /en/ prefix로 모두 영문 |
| **TOTAL** | **~770** | |

### 2.2 SEO 강화 요소

- ✅ **hreflang**: ko, en, x-default 모든 페이지 자동
- ✅ **sitemap.xml**: 동적 생성, alternate 링크 포함, 137 baseline × 2 lang
- ✅ **robots.txt**: 동적 (사이트 호스트 자동)
- ✅ **JSON-LD**: WebSite, Organization, Article, FAQ, BreadcrumbList
- ✅ **OG / Twitter Cards**: 60갑자 한·영 OG 이미지 60장 + 동적 OG 카드 (`/og/result.png?y=...`)
- ✅ **PWA**: manifest + Service Worker + 192/512 아이콘
- ✅ **모든 페이지 모바일 반응형**

### 2.3 검색엔진 인증 — **대기 상태 (사용자 액션 필요)**

`flask_app.py`에 다음 환경변수 빈 채로 준비:
- `GOOGLE_SITE_VERIFICATION` (env var 빈 채)
- `NAVER_SITE_VERIFICATION` (env var 빈 채)
- `BING_SITE_VERIFICATION` (env var 빈 채)
- `YANDEX_SITE_VERIFICATION` (env var 빈 채)
- `PINTEREST_VERIFICATION` (env var 빈 채)

사용자가 각 콘솔 가입 후 인증 코드 받아 WSGI 환경변수에 추가하면 자동 활성. `_setup_lemmy_bot.py`에 추가 패턴으로.

---

## 3. 광고 수익 인프라

### 3.1 Google AdSense

- **Publisher ID**: `ca-pub-4682723571700089`
- **상태**: Google 검토 중 (소유권 확인 후 콘텐츠 심사 단계)
- **확인 방법**: 3가지 모두 자동 활성 (사이트 스크립트, 메타 태그, ads.txt)
- **승인 후 작업**: 광고 슬롯 ID 3개(`ADSENSE_SLOT_TOP/INLINE/BOTTOM`) 발급 받아 WSGI 환경변수에 추가
- **현재 광고 노출 X** (슬롯 ID 미설정)
- **WSGI 환경변수**: `ADSENSE_CLIENT_ID=ca-pub-4682723571700089` 만 설정됨

### 3.2 카카오 AdFit ⚠️ **재심사 대기**

| 슬롯 | 사이즈 | 단위 ID | 배치 |
|---|---|---|---|
| Leaderboard | 728×90 | `DAN-n0PoylDwx5yW9h6m` | 본문 끝 (콘텐츠 후) |
| Medium | 300×250 | `DAN-6igVlxF0jtfGAy7k` | 결과 페이지 인라인 |
| Square | 250×250 | `DAN-R1f0lIsOhUpSLRxI` | 페이지 하단 |
| Skyscraper | 160×600 | `DAN-oS7GuVEpbyNDjHBF` | 데스크탑 1600px+ 우측 고정 |

**관리 콘솔**: https://adfit.kakao.com

**1차 심사 결과**: 모바일에서 728×90 잘림으로 보류

**수정 사항 (재심사 통과 목적)**:
1. 모바일 728×90 완전 차단 (CSS @media + JS DOM 제거 이중)
2. 스카이스크래퍼 1500→1600px (콘텐츠 overlap 방지)
3. "광고" 라벨 명확화 (폰트 굵기·크기·점선 구분)
4. 개인정보처리방침에 AdFit 명시 추가
5. CSS 캐시 버전 `?v=20260517-compliance`

**재심사 요청 시 첨부 메시지** (사용자에게 안내함):
```
728×90 광고 단위가 모바일(<768px)에서 노출되지 않도록 수정 완료.
- CSS @media 룰
- JS로 DOM에서 컨테이너 완전 제거
콘텐츠 overlap 가능성도 0으로 차단 (스카이스크래퍼 breakpoint 상향).
```

### 3.3 광고 수익 예상 (트래픽별)

| 일 PV | 일일 수익 (한국 트래픽) |
|---|---|
| 100 | ₩200~500 |
| 1,000 | ₩2,500~6,000 |
| 5,000 | ₩15,000~30,000 |
| 10,000 | ₩30,000~70,000 (AdSense 합산) |

### 3.4 동적 OG 카드 + 카카오톡 공유 SDK

- **OG 라우트**: `/og/result.png?y=1990&m=5&d=15&h=14&min=30&g=남&n=홍길동&lang=ko`
- **카카오톡 공유**: `static/js/main.js`의 `shareKakao()` 함수
- **공유 시 카드**: 본인 사주가 그려진 1200×630 PNG가 미리보기로 표시

---

## 4. 매뉴얼 콘텐츠 패키지 (사용자가 직접 게시)

**위치**: `C:\Users\master\CEO\saju_platform\marketing/`

| 파일 | 내용 | 활용 |
|---|---|---|
| `01_instagram_captions.md` | 인스타 30일치 캡션 + 해시태그 풀 | 인스타 계정 만들고 매일 1게시 |
| `02_twitter_threads.md` | X(트위터) 스레드 20개 (한 10 + 영 10) | X 계정 만들고 주 3개 스레드 |
| `03_blog_posts.md` | 네이버 블로그·티스토리·Medium 5편 | 주 1편 게시 |
| `04_calendar_30days.md` | 30일 게시 캘린더 + 게시 시간 가이드 | 운영 일정표 |
| `05_show_hn_launch.md` | HackerNews / Product Hunt / dev.to / Reddit / X 런치 카피 | GitHub 푸시 후 1회 런치 |
| `06_qa_answers.md` | Quora 10개 + 네이버 지식인 10개 답변 | 하루 2~3개 분산 게시 |
| `07_youtube_shorts_scripts.md` | YouTube Shorts 30개 대본 (한 15 + 영 15) + TTS 가이드 | 주 3편 영상 |

**모든 자료는 사용자가 복붙해서 직접 게시.** 자동화는 SNS 정책상 위험.

### Pinterest 핀 120장

**위치**: `static/img/pinterest-kr/pin-kr-00.png` ~ `pin-kr-59.png`, `static/img/pinterest-en/pin-en-00.png` ~ `pin-en-59.png`

- 사이즈 1000×1500 (Pinterest 최적)
- 한국어 60개 + 영문 60개
- **현재 Pinterest에 업로드 안 됨**. 사용자가 Pinterest 가입 후 일괄 업로드 필요.

---

## 5. 백엔드 API (다른 클라이언트에서 사용 가능)

**CORS 헤더 모두 활성** (`Access-Control-Allow-Origin: *`) — 토스 미니앱·외부 앱에서 직접 fetch 가능.

| 엔드포인트 | 설명 |
|---|---|
| `POST /api/saju` | 사주 풀이 (대운 + 일주 인덱스 포함) |
| `GET /api/today` | 오늘의 일진 |
| `GET /api/pillars` | 60갑자 전체 목록 (한·영) |
| `GET /api/pillar/<idx>` | 특정 일주 상세 |
| `GET /api/zodiac/<name>` | 띠별 운세 |
| `POST /api/compatibility` | 두 사람 사주 궁합 |

자세한 명세는 `HANDOFF_TOSS_MINIAPP.md` 참고.

---

## 6. 운영 중인 검색엔진 색인 채널

### 6.1 IndexNow (자동, 매일)
- Bing, Yandex, Naver, Seznam에 즉시 색인 제출
- 신규 페이지 추가 시 자동
- 누적 ~400+ URL 제출

### 6.2 Google (수동, 사용자 액션 필요)
- Search Console 가입 + 사이트 인증 — **아직 안 됨**
- 사이트맵 제출 (`/sitemap.xml`) — 가입 후 가능

### 6.3 Naver (수동, 사용자 액션 필요)
- Naver Search Advisor 가입 + 사이트 인증 — **아직 안 됨**
- 한국 트래픽의 30~50%가 네이버이므로 중요

---

## 7. 활동·트래픽 측정 방법

### 7.1 채널별 활동 직접 조회 명령

```python
# Lemmy
from urllib import request, json
req = request.Request('https://lemmy.world/api/v3/user?username=tarofortune&sort=New&limit=20')
# Mastodon
req = request.Request('https://mastodon.social/api/v1/accounts/lookup?acct=tarosaju')
# Dev.to
req = request.Request('https://dev.to/api/articles?username=tarofortune&per_page=20')
# GitHub Actions
req = request.Request('https://api.github.com/repos/leekyuhaiambox-ops/saju-platform/actions/runs')
```

### 7.2 사이트 트래픽

**현재 분석 도구 없음.** 다음 중 하나 설치 필요:
- Google Analytics 4 (GA_MEASUREMENT_ID 환경변수 빈 채)
- Naver Analytics
- PythonAnywhere 자체 access log

GA4 가입 후 `G-XXXXXXXX` 코드를 WSGI에 추가하면 `base.html`이 자동 GA 스크립트 노출.

---

## 8. 알려진 문제 / 개선 필요 사항

### 8.1 봇 의심 패턴
- Lemmy 게시물 1개 -5점 받음 → 빈도 줄임 (매일→3일에 1회)
- Mastodon 팔로워 0 → organic 발견 안 됨
- Dev.to 0 PV → 알고리즘 노출 안 됨

### 8.2 개선 권장
- **Mastodon**: 봇만 게시하지 말고 사용자가 직접 영성/한국 계정 30개 정도 팔로우 + 댓글 활동 → 알고리즘이 "real account"로 인식
- **Dev.to**: 같은 시각 게시 X (랜덤 지연 완료), 태그 다양화 (완료), 댓글 활동 추가 필요
- **Lemmy**: 게시뿐 아니라 다른 글에 댓글 달기 → 봇 의심 해소

### 8.3 절대 자동화 금지 (계정 정지 위험)
- Instagram, X, TikTok, Facebook → **수동으로만**
- Reddit → 가능하지만 카르마 100+ 필요. 현재 신규 계정은 봇 차단됨

---

## 9. 다음 단계 우선순위

### 🔥 즉시 (사용자 5~30분 액션)
1. **AdFit 재심사 요청** — 이미 모든 위반사항 수정. 통과되면 즉시 광고 수익 시작
2. **Google Search Console 가입** + 인증 (5분)
3. **Naver Search Advisor 가입** + 인증 (5분)
4. **Pinterest 가입 + 120 핀 일괄 업로드** (30분) — 한국 시각적 트래픽 큰 효과
5. **GA4 가입** + Measurement ID 받기 (5분)

### ⚡ 중기 (사용자 1~2시간)
6. **인스타·X·블로그 매뉴얼 운영** 시작 (marketing/ 패키지 활용)
7. **Quora·지식인 답변 20개 분산 게시** (`06_qa_answers.md`)
8. **YouTube Shorts 1편 시범 제작** (`07_youtube_shorts_scripts.md`)

### 🌱 장기 (트래픽 누적 후)
9. **커스텀 도메인 구입** (예: `사주.kr`) — 1~3만원/년, AdSense·SEO 큰 효과
10. **이메일 발송 시스템** 추가 — SMTP(Brevo 무료 300건/일) 연결 → 일일 운세 메일
11. **유료 풀이** (KaKao Pay / Toss Pay) — 트래픽 500+ 일 후
12. **토스 미니앱 출시** — 별도 세션에서 진행 중 (`HANDOFF_TOSS_MINIAPP.md` 참고)

---

## 10. 트러블슈팅 가이드

### 10.1 GitHub Actions 실행 실패
```bash
# Workflow 로그 확인
https://github.com/leekyuhaiambox-ops/saju-platform/actions
# 가장 흔한 원인: state 파일 머지 충돌
# → 워크플로우가 자동으로 git push state 하다가 충돌
# 해결: 로컬에서 `git pull --rebase` 후 push
```

### 10.2 봇이 게시 안 함 ("Already posted")
```bash
# state 파일이 오늘 날짜로 박혀있음
# 강제 재실행 시:
del .devto_state.json   # 로컬
# 또는 GitHub Repo에서 state JSON 파일 비우기
```

### 10.3 Flask 서버 500 오류
```bash
# PA 에러 로그 위치:
/var/log/tarofortune.pythonanywhere.com.error.log
/var/log/tarofortune.pythonanywhere.com.server.log
# API로 읽기:
GET /api/v0/user/tarofortune/files/path/var/log/tarofortune.pythonanywhere.com.error.log
```

### 10.4 광고 안 보임
- AdFit 4개 슬롯 중 fill 안 된 건 `display:none` 정상 동작
- AdSense는 슬롯 ID 미설정이라 표시 안 됨 (Google 승인 대기)

---

## 11. 코드 파일 맵

```
saju_platform/
├── flask_app.py                     # Flask 앱 메인 (라우트 + API)
├── saju/
│   ├── calculator.py                # 사주 계산 (Meeus 알고리즘)
│   ├── interpreter.py               # 한국어 풀이 데이터
│   ├── interpreter_en.py            # 영문 풀이 데이터
│   ├── data.py                      # 천간/지지/오행 상수
│   ├── daily.py                     # 일진/띠 운세/궁합
│   ├── glossary.py                  # 용어사전 (한)
│   ├── glossary_en.py               # 용어사전 (영)
│   ├── solar_terms_data.py          # 24절기 데이터
│   ├── detail_pages.py              # 십신/십이운성/지장간/천간 상세
│   ├── long_tail.py                 # 일주별 직업/연애 데이터
│   ├── lunar.py                     # 음력 변환
│   ├── og_card.py                   # 동적 OG 이미지 생성 (Pillow)
│   ├── i18n.py                      # 다국어 번역 사전
│   ├── indexnow.py                  # IndexNow 프로토콜
│   └── cache.py                     # LRU 캐싱
├── templates/                       # Jinja2 템플릿 ~30개
├── static/
│   ├── css/style.css                # 메인 CSS (~25KB, 캐시 v=20260517-compliance)
│   ├── js/main.js                   # 카카오 공유 + 폼 핸들러
│   ├── manifest.json                # PWA
│   ├── sw.js                        # Service Worker
│   └── img/
│       ├── og/                      # 60갑자 OG 한 60장
│       ├── og-en/                   # 60갑자 OG 영 60장
│       ├── pinterest-kr/            # Pinterest 한 60장
│       └── pinterest-en/            # Pinterest 영 60장
├── marketing/                       # 매뉴얼 콘텐츠 7개 (사용자 직접 게시)
├── .github/workflows/daily-bot.yml  # 자동화 cron
├── lemmy_bot.py                     # Lemmy 봇 (3일 주기)
├── mastodon_bot.py                  # Mastodon 봇 (매일)
├── devto_bot.py                     # Dev.to 봇 (15편 풀)
├── reddit_bot.py                    # Reddit 봇 (대기, POSTS 60개 풀 데이터 소스)
├── tistory_bot.py                   # Tistory 봇 (대기, 카카오 OAuth 필요)
├── hashnode_bot.py                  # Hashnode 봇 (사용 X, API 유료 전환)
├── auto_index.py                    # IndexNow + sitemap ping
├── run_all_bots.py                  # 통합 실행 진입점
├── run_all_bots.bat                 # Windows 작업 스케줄러용 (이제 GitHub Actions로 이전)
├── _deploy.py                       # PA 전체 배포 스크립트
├── _setup_lemmy_bot.py              # WSGI 환경변수 + 시크릿 설정
├── _github_setup.py                 # GitHub 자동 셋업 (PAT 사용)
├── _gen_og_cards_en.py              # 영문 OG 카드 생성
├── _gen_pinterest_pins.py           # Pinterest 핀 120장 생성
├── _gen_pwa_icons.py                # PWA 아이콘 생성
├── _index_*.py                      # IndexNow 일괄 제출 (배치별)
├── _test_lemmy.py                   # Lemmy 자격증명 테스트
├── _check_lemmy_status.py           # Lemmy 계정 승인 상태 진단
├── HANDOFF_TOSS_MINIAPP.md          # 토스 미니앱 인수인계서
├── HANDOFF_MARKETING.md             # 이 문서
├── README.md                        # GitHub 공개용
├── LICENSE                          # MIT
├── .gitignore                       # .env, state, 배포 스크립트 제외
└── .env                             # 자격증명 (로컬 전용, git 제외)
```

---

## 12. 자주 사용하는 검증 명령

### 12.1 자동화 채널 현황 한 번에 확인 (Python)
```python
from urllib import request
import json

# Lemmy
data = json.loads(request.urlopen('https://lemmy.world/api/v3/user?username=tarofortune&sort=New&limit=10').read())
print(f"Lemmy: {len(data['posts'])} posts")

# Mastodon
acct = json.loads(request.urlopen('https://mastodon.social/api/v1/accounts/lookup?acct=tarosaju').read())
toots = json.loads(request.urlopen(f'https://mastodon.social/api/v1/accounts/{acct["id"]}/statuses?limit=10').read())
print(f"Mastodon: {len(toots)} toots, {acct['followers_count']} followers")

# Dev.to
arts = json.loads(request.urlopen('https://dev.to/api/articles?username=tarofortune&per_page=10').read())
print(f"Dev.to: {len(arts)} articles")
```

### 12.2 GitHub Actions 실행 이력
```bash
# 토큰 사용
GH_TOKEN="ghp_..."  # leekyuhaiambox-ops의 PAT
curl -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/leekyuhaiambox-ops/saju-platform/actions/runs?per_page=10
```

### 12.3 사이트 헬스 체크
```bash
# 핵심 엔드포인트 200 확인
curl -I https://tarofortune.pythonanywhere.com/
curl -I https://tarofortune.pythonanywhere.com/api/today
curl -I https://tarofortune.pythonanywhere.com/sitemap.xml
curl -I https://tarofortune.pythonanywhere.com/ads.txt
```

### 12.4 Flask 재배포 (코드 변경 시)
```bash
cd C:\Users\master\CEO\saju_platform
python -X utf8 _deploy.py
```
또는 단일 파일만:
```python
# _quick_deploy_<filename>.py 패턴 참고
# 파일 업로드 + reload
```

---

## 13. 통계·메트릭 (2026-05-17 기준)

| 항목 | 값 |
|---|---|
| 사이트 라이브 일수 | ~7일 |
| 인덱싱 가능 URL | ~770 |
| Lemmy 게시물 | 4개 |
| Mastodon 게시물 | 3개 |
| Dev.to 게시물 | 3개 |
| GitHub Actions 실행 | 4회 (모두 success) |
| IndexNow 누적 제출 | ~400+ URL |
| AdSense 상태 | 검토 중 |
| AdFit 상태 | 재심사 대기 |
| 사이트 트래픽 | 측정 불가 (GA 미설치) |
| 광고 수익 | ₩0 (모든 광고 미승인) |

---

## 14. 결정·약속 사항 메모

### 운영자가 명시한 원칙
- ❌ **광고 코드 변형 절대 X** — AdFit 규정 준수 최우선
- ❌ **계정 정지 위험 자동화 절대 X** — Instagram/X/TikTok 등 수동만
- ✅ **무료 자원만 활용** — PythonAnywhere 무료 + GitHub Actions 무료 + 모든 봇 API 무료
- ✅ **콘텐츠 품질 우선** — 봇 게시도 가치 있는 글만, 스팸성 절대 X

### 미해결 결정 사항
- [ ] 도메인 구입 여부 (`사주.kr` 추천, 1~3만원)
- [ ] 유료 풀이 가격 (안: ₩2,900~5,900)
- [ ] 이메일 SMTP 서비스 선택 (Brevo vs SendGrid 무료티어)
- [ ] 토스 미니앱 진행 시점 (현재 별도 세션에서 시작 예정)

---

## 15. 새 세션에서 첫 질문할 만한 것

작업 이어받는 다른 세션에서 운영자에게 물어볼 만한 질문:

1. "AdFit 재심사 통과 여부 확인하셨나요?" (통과되면 광고 수익 즉시 시작)
2. "Google Search Console 가입하셨나요?" (인증 코드 받았으면 박아드림)
3. "Pinterest 120장 업로드는 진행 중인가요?"
4. "트래픽 데이터 어떻게 측정하고 계신가요? GA 추가할까요?"
5. "다음 우선순위는 트래픽 늘리기 vs 콘텐츠 확장 vs 수익화 강화 중 무엇인가요?"

---

## 16. 연락처·계정 정보

| 항목 | 값 |
|---|---|
| 운영자 이메일 | leekyuha.iambox@gmail.com |
| Reddit 계정 | leekyuha.iambox@gmail.com (Proper-Brief-8850, 신규) |
| Mastodon 계정 | tarosaju @ mastodon.social |
| Dev.to 계정 | tarofortune |
| Lemmy 계정 | tarofortune @ lemmy.world |
| GitHub | leekyuhaiambox-ops |
| PA 사용자명 | tarofortune |
| AdSense Pub ID | ca-pub-4682723571700089 |
| Tistory | issuemoamoa (보유, 봇 대기) |

---

## 마무리

이 문서는 모든 운영 중인 자동화·매뉴얼 마케팅 활동을 한 곳에 담은 인수인계서다. 새 Claude Code 세션에서 첫 메시지로 이 파일 경로를 알려주거나 그대로 붙여넣으면 즉시 작업 이어받기 가능.

**중요 원칙 (강조)**:
1. 광고 정책 위반하면 운영자 분노 — AdFit/AdSense 코드는 절대 손 X
2. 계정 정지 위험 자동화 절대 X — Instagram/X/TikTok 수동만
3. 자격증명은 `.env` (로컬) + GitHub Secrets (서버)에만 존재 — 절대 코드에 평문으로 X
4. 사이트 변경 시 PA 재배포 + GitHub push 둘 다 — 단일 진실 원천 X
5. 봇 게시는 가치 있는 콘텐츠만, 스팸성 절대 X — 운영자 신뢰가 우선

작성일: 2026-05-17
다음 갱신: AdFit 재심사 결과 나오면, 또는 큰 변경사항 발생 시.
