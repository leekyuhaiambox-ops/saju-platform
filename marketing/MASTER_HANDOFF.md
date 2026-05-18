# 멀티사이트 마케팅 운영 인수인계서

> 새 Claude Code 세션 첫 메시지에 이 파일 경로만 주면 즉시 이어받기 가능.
> 최종 갱신: 2026-05-18

---

## 0. 30초 요약

운영자는 현재 **3개의 라이브 웹사이트**를 운영하며 각각 별개의 도메인·타깃·수익모델을 가짐:

| # | 사이트 | URL | 타깃 | 상태 | 수익모델 |
|---|---|---|---|---|---|
| 1 | 사주명리 | tarofortune.pythonanywhere.com | 사주 사용자 | 마케팅 활발 (1주차) | AdFit·AdSense (심사 대기) |
| 2 | 경기지역화폐 지도 | gyeonggi-currency-map.web.app | 경기도민·자영업자 | **신규 마케팅** | AdFit·AdSense + GA `G-GP53D8Q7R6` |
| 3 | 생활권 접근성 분석 | geoinfomatic.pythonanywhere.com | 이사·임장·청약자 | **신규 마케팅** | 일 5회 무료 + Pro ₩9,900/월 |

이 인수인계서는 **#2와 #3의 마케팅 확장**을 위해 작성됨. #1의 인수인계는 `saju_platform/HANDOFF_MARKETING.md` 참조.

---

## 1. 본 인수인계서의 산출물 (2026-05-18 풀 구현 후)

```
C:\Users\master\CEO\marketing\
├── MASTER_HANDOFF.md                         ← 이 문서
├── currency-map\
│   ├── PLAYBOOK.md                           ← 전략·SEO·8채널 (350줄)
│   └── content\
│       ├── naver_blog_post_1.md              ← 성남 지역화폐 Naver 블로그 완성본 (1,800자)
│       ├── tistory_post_1.md                 ← 구글 SEO용 Tistory 완성본
│       ├── jisikin_answers.md                ← 지식인 답변 10개 완성본
│       ├── press_release_final.md            ← 보도자료 2버전 + 송부 주소록
│       ├── mom_cafe_posts.md                 ← 31개 시·군 맘카페 카피 (3톤 + 변형 가이드)
│       └── youtube_shorts_scripts.md         ← Shorts 대본 7편
├── geoinfomatic\
│   ├── PLAYBOOK.md                           ← 전략·SEO·8채널 + Pro funnel (380줄)
│   ├── pro_payment_implementation.py         ← Pro 결제 Flask Blueprint (Toss Payments 연동)
│   ├── templates\
│   │   ├── pro.html                          ← Pro 랜딩 페이지 (SEO + JSON-LD Product)
│   │   └── checkout.html                     ← Toss 결제위젯 통합 페이지
│   └── content\
│       ├── naver_blog_post_1.md              ← 이사 동네 점수 Naver 블로그 완성본 (2,000자)
│       ├── tistory_post_1.md                 ← 구글 SEO용 Tistory 완성본
│       ├── jisikin_answers.md                ← 지식인 답변 10개 완성본
│       ├── press_release_final.md            ← 보도자료 2버전 + 부동산 매체 주소록
│       ├── realestate_cafe_posts.md          ← 부동산스터디·신혼·학군·청약 카페 카피 (4톤)
│       └── youtube_shorts_scripts.md         ← Shorts 대본 7편
└── shared\
    ├── multi_site_orchestrator.py            ← 3사이트 통합 봇 (실제 작동 검증 완료)
    ├── sitemap_currency_map_proposed.xml     ← currency-map: 38 URL 확장안
    ├── sitemap_geoinfomatic_fixed.xml        ← geoinfomatic: 메인 / 추가 버그 수정
    ├── deploy_geoinfomatic_sitemap.py        ← PA API 자동 배포 헬퍼 (토큰 필요)
    ├── setup_search_verification.py          ← GSC/Naver/Bing/Yandex 메타 일괄 적용
    ├── instagram_reels_scripts.md            ← 양 사이트 Reels 10편
    └── content_pools\
        ├── currency-map.json                  ← 봇 영문 3 + 한국어 2
        └── geoinfomatic.json                  ← 봇 영문 3 + 한국어 2

C:\Users\master\CEO\saju_platform\
└── .github\workflows\
    └── multi-site-bot.yml                    ← GitHub Actions 신규: 3사이트 회전 자동
```

---

## 2. 핵심 발견 (정찰 결과)

### 2.1 currency-map (gyeonggi-currency-map.web.app)
- **기술**: React + Vite + Leaflet, Firebase Hosting, PWA
- **SEO 인프라**: ✅ JSON-LD `WebApplication` (areaServed 10개 도시) / ✅ OG·Twitter / ✅ AdSense `ca-pub-4682723571700089` / ✅ AdFit 4슬롯 / ✅ GA `G-GP53D8Q7R6` / ✅ PWA manifest
- **결함**: ⚠️ Sitemap에 루트 URL **1개만** → 31개 시·군 deep route 색인 불가
- **차별점**: 31개 시·군 통합 + 영업중 필터 + 카카오톡 공유 SDK

### 2.2 geoinfomatic (geoinfomatic.pythonanywhere.com)
- **기술**: Flask + Leaflet (PA 무료티어)
- **SEO 인프라**: ✅ JSON-LD `WebApplication` + featureList + audience / ✅ OG·Twitter / ✅ 정교한 robots.txt (AI 봇 차단·검색엔진 허용) / ✅ AdFit 3슬롯
- **결함**: ❌ **Sitemap 버그** — 메인 `/`가 누락, `/profile/*`만 28개 / ❌ Pro 결제 페이지 미구현 (modal만 + "준비 중" alert)
- **차별점**: 매물 없는 순수 생활권 분석 + AI 요약 + 환승 0/1/2회 분리 + Pro ₩9,900/월

### 2.3 공통
- 같은 운영자: leekyuhaiambox-ops / leekyuha.iambox@gmail.com / blog nickname **austriano**
- 같은 AdSense Publisher (3사이트 공유) — 한 운영자 일관 정책
- 같은 광고 정책 (재심사 대기 / AdFit 4슬롯 패턴)

---

## 3. 이미 실행된 것 / 즉시 실행 가능한 것

### ✅ 본 세션에서 자동 실행 완료
| # | 액션 | 사이트 | 결과 |
|---|---|---|---|
| ✅ | **Mastodon 실제 게시** (`@tarosaju`) | currency-map | 글 1편 라이브 |
| ✅ | **IndexNow 색인 제출** | currency-map + geoinfomatic | Bing/api.indexnow `202` |
| ✅ | **Pro 결제 페이지 코드 + 템플릿 작성** | geoinfomatic | 보일러플레이트 완성 (PA 업로드만 남음) |
| ✅ | **GitHub Actions multi-site workflow YAML 작성** | 모두 | `.github/workflows/multi-site-bot.yml` |
| ✅ | **Naver 블로그 글 2편 완성본** | 양쪽 | 복붙해서 게시만 하면 됨 |
| ✅ | **지식인 답변 20개 완성본** | 양쪽 | 분산 게시 가능 |
| ✅ | **보도자료 + 송부 주소록** | 양쪽 | 이메일 송부만 |

### 🔥 운영자만 할 수 있는 것 (인증 필요)

| # | 액션 | 소요 | 비고 |
|---|---|---|---|
| 1 | **geoinfomatic PA 토큰 발급 → 자동 sitemap 배포** | 5분 + 자동 실행 | `deploy_geoinfomatic_sitemap.py` 실행 |
| 2 | **GSC/Naver/Bing/Yandex 사이트 등록 (4개 × 3사이트 = 12회)** | 30분 | 메타코드는 `setup_search_verification.py` |
| 3 | **Naver 블로그 austriano 글 게시** | 30분 (×2편) | 완성본 그대로 복붙 |
| 4 | **부동산 카페·맘카페 가입·등업** | 카페별 가입 + 1주 활동 후 게시 | 카피는 완성본 사용 |
| 5 | **Toss Payments 가입 + 키 발급** | 30분 | Pro 결제 페이지에 키 박기 |
| 6 | **보도자료 이메일 송부 (양쪽 사이트 5~10건)** | 30분 | 주소록 + 템플릿 완성 |
| 7 | **GitHub Actions 새 workflow 활성화** | 5분 | repo Settings → Actions → enable |

### ⚡ 중기 (1~2주)

| # | 액션 | 비고 |
|---|---|---|
| 6 | **부동산스터디 다음카페 가입·등업·첫 게시** | geoinfomatic 핵심 채널 |
| 7 | **31개 시·군 맘카페 가입 시작 (수원맘부터)** | currency-map 핵심 채널 |
| 8 | **보도자료 송부** | 경기일보·중부일보 (currency-map) + 매경·한경 (geoinfomatic) |
| 9 | **multi_site_orchestrator.py 실행 시작** | 3사이트 통합 자동 봇 |
| 10 | **부동산 유튜브 댓글 마케팅** (geoinfomatic) | 월 10개 댓글 |

---

## 4. 자동화 인프라 (3사이트 통합)

### 4.1 설계 원칙

기존 saju_platform의 봇 인프라(`run_all_bots.py` + GitHub Actions cron)를 **계정 재활용**해서 3사이트에 적용:

- **Lemmy**: `u/tarofortune` 한 계정으로 3사이트 회전 (3일 주기 × 3사이트 = 9일에 1번 같은 사이트)
- **Mastodon**: `@tarosaju@mastodon.social` 한 계정으로 3사이트 매일 회전
- **Dev.to**: `@tarofortune` 한 계정으로 3사이트 회전 게시
- **IndexNow**: 3사이트 모두 매일 색인 제출

**왜 같은 계정?** 별도 계정 만들면 봇 의심·관리 비용 증가. 한 계정에 다양한 주제 = "real account" 시그널 ↑.

### 4.2 실행 방법

```bash
# 자동 (오늘의 사이트 선택)
cd C:\Users\master\CEO\marketing\shared
python multi_site_orchestrator.py

# 특정 사이트만
python multi_site_orchestrator.py --site currency-map

# 드라이런 (게시 안 함, 출력만)
python multi_site_orchestrator.py --dry-run

# 특정 채널만
python multi_site_orchestrator.py --site geoinfomatic --channel mastodon
```

### 4.3 기존 GitHub Actions 통합

`saju_platform/.github/workflows/daily-bot.yml`의 봇 호출 라인을 교체:

```yaml
# 기존:
- run: python -X utf8 run_all_bots.py
# 변경:
- run: python -X utf8 ../marketing/shared/multi_site_orchestrator.py
```

또는 marketing 폴더를 saju_platform 안으로 이동하면 그대로 사용 가능.

### 4.4 자격증명

기존 saju_platform의 GitHub Secrets + `.env`를 그대로 재활용. 추가 필요 없음:
- `LEMMY_USERNAME`, `LEMMY_PASSWORD`
- `MASTODON_ACCESS_TOKEN`
- `DEVTO_API_KEY`
- `INDEXNOW_KEY` (없으면 디폴트 사용)

---

## 5. 채널별 운영 매트릭스 (3사이트 통합 보기)

| 채널 | 자동/수동 | tarofortune | currency-map | geoinfomatic |
|---|---|---|---|---|
| Lemmy | 🤖 자동 | astrology / spirituality | southkorea / openstreetmap | urbanism / korea |
| Mastodon | 🤖 자동 | 60갑자 toot | PWA / Leaflet toot | GIS / 부동산 toot |
| Dev.to | 🤖 자동 | astrology API 글 | React + Leaflet 글 | Flask + isochrone 글 |
| IndexNow | 🤖 자동 | ✅ | ✅ | ✅ |
| Naver 블로그 | 🙋 수동 | 사주 풀이 글 | 시·군별 가맹점 가이드 | 이사·임장 분석 사용기 |
| Naver 지식인 | 🙋 수동 | 사주 질문 답변 | 지역화폐 답변 | 부동산 답변 |
| Naver/Daum 카페 | 🙋 수동 | 영성·운세 카페 | 31개 시·군 맘카페 | 부동산스터디 등 |
| 카카오톡 오픈채팅 | 🙋 수동 | 운세 방 | 지역 정보 방 | 청약·이사 방 |
| YouTube Shorts | 🙋 수동 | 60갑자 풀이 | 시·군 BEST 가맹점 | 동네 점수 비교 |
| 인스타 Reels | 🙋 수동 | 일주 카드 | 가맹점주용 | 도구 사용 30초 |
| 보도자료 | 🙋 수동 | (없음) | 경기일보·중부일보 | 매경·한경·조선비즈 |

---

## 6. 통합 KPI 대시보드 (월 1회 측정)

| 사이트 | 1M Naver 색인 | 1M Google 색인 | 1M 직접 PV | 1M 수익 |
|---|---|---|---|---|
| tarofortune | 30 | 30 | 1,500 | ₩0 (광고 심사) |
| currency-map | 30 | 30 | 1,500 | ₩5,000 (AdFit) |
| geoinfomatic | 5→30 (버그 수정 후) | 10→50 | 1,000 | ₩0 (Pro 미구현) → ₩50K |
| **합계** | **65** | **70** | **4,000** | **₩5K → ₩55K** |

3개월 목표: 합산 PV 30,000 / 합산 수익 ₩200,000.

---

## 7. 운영자 원칙 (3사이트 공통)

1. ❌ **광고 코드 변형 절대 X** — AdFit/AdSense 규정 준수 최우선
2. ❌ **계정 정지 위험 자동화 절대 X** — Instagram·X·TikTok 수동만
3. ✅ **무료 자원만 활용** — PA 무료티어 + GitHub Actions + Firebase 무료
4. ✅ **콘텐츠 품질 우선** — 봇 게시도 가치 있는 글만, 스팸 X
5. ✅ **3사이트 자격증명 분리** — `.env` + GitHub Secrets만, 코드 평문 X
6. ✅ **사용자 신뢰 우선** — "광고 아니에요" 강조, 솔직한 한계 명시
7. ✅ **블로그 닉네임 austriano** — 운영자 본명 노출 X

---

## 8. 새 세션 첫 질문할 만한 것

작업 이어받는 다른 Claude Code 세션에서 운영자에게 물어볼 만한 것:

1. **"geoinfomatic sitemap 버그 수정 배포하셨나요?"** (가장 시급)
2. **"Google Search Console + Naver 서치어드바이저 등록은 어떤 사이트부터 시작하시겠어요?"**
3. **"Pro 결제 페이지 구현은 Toss Payments / Kakao Pay 중 어느 쪽 선호하세요?"**
4. **"부동산스터디 다음카페 가입은 진행하셨나요? 도움 필요하시면 카피 다듬어드릴게요."**
5. **"multi_site_orchestrator.py 한번 드라이런 돌려보실까요?"** (검증)

---

## 9. 트러블슈팅

### 9.1 multi_site_orchestrator.py import 오류
saju_platform이 같은 부모 폴더에 있어야 함:
```
CEO\
├── saju_platform\        ← 기존 봇 모듈
└── marketing\shared\multi_site_orchestrator.py  ← 새 통합 스크립트
```
경로 확인: `python -c "import sys; print(sys.path)"`

### 9.2 Mastodon 게시 실패
- `MASTODON_ACCESS_TOKEN` 환경변수 확인: `echo $env:MASTODON_ACCESS_TOKEN`
- `mastodon.social` 점검 여부: https://mastodon.social/about

### 9.3 currency-map sitemap 확장 후 색인 안 됨
- Firebase Hosting `firebase.json` rewrites 확인:
  ```json
  "rewrites": [
    {"source": "/sigungu/**", "destination": "/index.html"}
  ]
  ```
- React 라우터(react-router-dom)가 `/sigungu/:cityKey` 패턴 처리 코드 추가 필요
- 처리 안 하면 sitemap이 200이지만 본문은 메인과 동일 → Google이 중복 콘텐츠 처리

### 9.4 geoinfomatic sitemap 수정 후 PA 재배포 명령
- 코드 변경: Flask `sitemap.py` 또는 `routes.py`의 sitemap 핸들러
- 재배포: PA Web 탭 → Reload 버튼, 또는 `touch ~/geoinfomatic/wsgi.py`

---

## 10. 다음 우선순위 (운영자 선택)

이 인수인계서 받은 새 세션이 운영자에게 제시할 만한 다음 액션:

### Path A — "수익화 우선"
1. Pro 결제 페이지 구현 (geoinfomatic) — 1일
2. 부동산 매체 보도자료 송부 — 1시간
3. 부동산 유튜브 댓글 마케팅 시작 — 주 1시간
- **30일 목표 수익**: Pro 가입 5건 = ₩49,500

### Path B — "트래픽 우선"
1. 양쪽 sitemap 수정 + GSC/Naver 등록 — 1시간
2. Naver 블로그 austriano로 양쪽 사이트 4편 작성 — 2일
3. multi_site_orchestrator.py 자동 운영 시작 — 30분
- **30일 목표 PV**: 양 사이트 합산 4,000

### Path C — "기반 인프라 강화"
1. currency-map Vite SSG 도입 — 1주
2. geoinfomatic noscript 보강 + 메타 인증 4개 — 30분
3. 양쪽 사이트 GA4 이벤트 트래킹 추가 — 2시간
- **목표**: 6개월 후 자연 검색 트래픽 압도

---

작성일: 2026-05-18 / 다음 갱신: 양쪽 sitemap 수정·GSC 등록 후, 또는 첫 KPI 측정 후.
