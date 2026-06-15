# 🤖 매일 자동 SNS 게시 — 채널별 셋업 가이드

> 한 번만 계정 만들고 토큰 받아서 GitHub Secrets에 넣으면, **매일 자동 게시 영구 작동** (PC 꺼져도 GitHub 서버에서 실행).

---

## 현재 자동 가동 중 (이미 작동)

| 채널 | 상태 | 한국 트래픽 |
|---|---|---|
| Lemmy | ✅ 3일마다 자동 | 낮음 |
| Mastodon | ✅ 매일 자동 | 낮음 |
| Dev.to | ✅ 매일 자동 | 낮음 |
| IndexNow (검색색인) | ✅ 매일 자동 | — |

## 새로 추가됨 (토큰만 넣으면 즉시 가동)

| 채널 | 자동화 | 한국 트래픽 | 셋업 난이도 |
|---|---|---|---|
| 🟢 Bluesky | 코드 완성 | 낮음(영어권) | ★ 쉬움 (5분) |
| 🟢 텔레그램 채널 | 코드 완성 | 중 | ★ 쉬움 (5분) |
| 🟡 Pinterest | 코드 완성 | 중(시각·장기) | ★★★ 보통 (앱승인) |
| 🟡 Reddit | 코드 완성 | 낮음 | ★★ (계정 숙성) |

---

## 🟢 1. Bluesky (가장 쉬움, 5분)

**왜**: 봇을 공식 허용. 승인 불필요. 트위터 대안으로 빠르게 성장.

**셋업**:
1. https://bsky.app 가입 (핸들 예: `tarofortune.bsky.social`)
2. Settings → Privacy and Security → **App Passwords** → 생성
3. 받은 비밀번호(`xxxx-xxxx-xxxx-xxxx`) 복사

**GitHub Secrets 등록**:
```
BLUESKY_HANDLE = tarofortune.bsky.social
BLUESKY_APP_PASSWORD = xxxx-xxxx-xxxx-xxxx
```
→ https://github.com/leekyuhaiambox-ops/saju-platform/settings/secrets/actions

---

## 🟢 2. 텔레그램 채널 (5분, 한국 사용자 가능)

**왜**: 공식 봇 API, 무제한 무료. 한국어 채널로 구독자 누적.

**셋업**:
1. 텔레그램에서 **@BotFather** 검색 → `/newbot` → 봇 이름 정하기 → **TOKEN** 받기
2. 텔레그램에서 **새 채널** 생성 (공개, 예: `@tarofortune_saju`)
3. 채널 설정 → 관리자 → 위에서 만든 봇 추가 (게시 권한)

**GitHub Secrets**:
```
TELEGRAM_BOT_TOKEN = 1234567890:ABCdef...
TELEGRAM_CHANNEL = @tarofortune_saju
```

매일 "오늘의 일진"이 채널에 자동 게시됨. 구독자가 매일 보게 됨.

---

## 🟡 3. Pinterest (시각적, 장기 트래픽 — 진짜 효자)

**왜**: 핀은 한 번 올리면 수개월~수년 검색 유입. 사주 카드 120장 이미 준비됨. 여성 사용자 많아 운세 콘텐츠와 궁합.

**셋업** (조금 번거로움):
1. https://www.pinterest.com 가입 → 비즈니스 계정 전환 (무료)
2. 보드 1개 생성 (예: "사주 60갑자 일주")
3. https://developers.pinterest.com → 앱 생성 → Access Token 발급
   - Trial access로도 **본인 보드 핀 게시 가능**
4. 보드 ID 확인 (보드 URL 또는 API로)

**GitHub Secrets**:
```
PINTEREST_ACCESS_TOKEN = pina_...
PINTEREST_BOARD_ID = 1234567890
```

---

## 🟡 4. Reddit (계정 숙성 후)

**왜**: 영어권 트래픽. 이전에 신규 계정이라 막혔지만, 계정이 한 달 이상 숙성됐으면 가능.

**셋업**:
1. https://www.reddit.com/prefs/apps → script 타입 앱 생성 (이전 시도 참고)
2. client_id, secret 확보

**GitHub Secrets**:
```
REDDIT_CLIENT_ID = ...
REDDIT_CLIENT_SECRET = ...
REDDIT_USERNAME = ...
REDDIT_PASSWORD = ...
```

---

## ❌ 자동화 불가 (봇 즉시 밴 — 수동만)

| 채널 | 이유 | 대안 |
|---|---|---|
| 인스타그램 | 비즈니스 API도 게시 제한 + 봇 탐지 | `01_instagram_captions.md` 수동 |
| 네이버 블로그 | 공식 게시 API 폐지, 자동화=밴 | 수동 (네이버 SEO 핵심) |
| 카카오스토리 | 게시 API 일반 비공개 | 수동 |
| 네이버 카페 | 봇 금지 | 수동 |
| X(트위터) | 무료 API 월 50건 쓰기 제한 | `02_twitter_threads.md` 수동 |

---

## 우선순위 추천

**지금 당장 (각 5분)**:
1. ✅ Bluesky — 가장 쉽고 즉시 작동
2. ✅ 텔레그램 채널 — 한국어 구독자 누적

**여유 될 때**:
3. Pinterest — 셋업 번거롭지만 장기 트래픽 최고 (사주 카드 활용)

**나중에**:
4. Reddit — 계정 숙성 확인 후

---

## 작동 방식 (다시 정리)

```
매일 KST 새벽 1~3시 (UTC 16:00 + 랜덤지연)
   ↓
GitHub Actions 자동 실행 (PC 무관)
   ↓
run_all_bots.py 가 환경변수 확인
   ↓
토큰 있는 채널만 자동 게시:
   IndexNow + Lemmy + Mastodon + Dev.to
   + (토큰 추가시) Bluesky + 텔레그램 + Pinterest + Reddit
   ↓
state 파일 자동 커밋 (중복 방지)
```

**토큰을 GitHub Secrets에 넣는 순간 그 채널이 다음 날부터 자동 합류.**

---

## 솔직한 기대치

- 자동 채널들은 대부분 **영어권**이라 한국 트래픽은 제한적
- **텔레그램·Pinterest**가 그나마 한국 유입 가능
- **진짜 한국 트래픽은 `08_traffic_playbook_KR.md`의 수동 커뮤니티 시딩**에서 나옴
- 자동화는 "씨앗을 여러 곳에 매일 뿌리는" 역할 — 누적되면 SEO·백링크로 효과

작성: 2026-05
