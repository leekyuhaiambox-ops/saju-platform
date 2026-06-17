# 🚀 여기부터 시작 — 운영 가이드 (austriano 전용)

> 이 파일 하나만 보면 됩니다. **당신이 할 일**과 **자동으로 돌아가는 것**을 나눠서 정리했습니다.
> 사이트: https://tarofortune.pythonanywhere.com

---

# 1부. 당신(austriano)이 할 일

## ✅ A. 매일 5분 루틴 — 글 발행 (제일 중요)

가장 쉬운 방법 하나만 쓰면 됩니다:

1. 이 파일을 더블클릭으로 엽니다 →
   `C:\Users\master\CEO\saju_platform\marketing\ready_to_post\PUBLISH_CENTER.html`
2. 브라우저에 발행 센터가 열립니다 (글 20개가 카드로 보임).
3. **하루에 1~2개**만 고릅니다. (한꺼번에 다 올리면 스팸으로 차단됨)
4. 글 아래 버튼을 누릅니다:
   - **𝕏 게시 / @ Threads / r/○○ 작성창 열기** → 내용이 **자동으로 채워진 채** 작성창이 열림 → 내용 확인 후 **「게시」 클릭** → 끝.
   - **블로그 / Quora / 카페** → **「📋 복사」** 누름 → 작성창 열고 **붙여넣기(Ctrl+V)** → 게시.
5. 다음 날 다른 글로 반복.

> ⚠️ 처음 게시할 때 해당 플랫폼에 **로그인**돼 있어야 합니다. (로그인은 한 번만)
> ⚠️ 같은 글을 여러 곳에 도배하지 마세요. 채널마다 다른 글, 하루 1~2개.

**추천 1주일 순서 (예시):**
| 요일 | 채널 | PUBLISH_CENTER에서 고를 글 |
|---|---|---|
| 월 | X + Threads | "오늘의 타로" |
| 화 | 레딧 r/tarot | 타로 사이트 소개 |
| 수 | 네이버블로그 | "타로 78장 의미 총정리" |
| 목 | X + Threads | "별자리 궁합" |
| 금 | 레딧 r/astrology | "Sun sign is 1 of 4" |
| 토 | 티스토리 | "별자리 성격·궁합 총정리" |
| 일 | 카페/Quora | "타로 무료 공유" |

---

## ✅ B. 한 번만 하면 되는 세팅 — 자동봇 채널 늘리기 (선택, 강력 추천)

지금 자동봇은 Mastodon·Lemmy·Dev.to만 돕니다. **도달력이 가장 큰 Bluesky**를 켜면 효과가 큽니다.
계정 만들기는 본인만 할 수 있어서, 아래 단계만 해주세요. (10분, 평생 1회)

### B-1. Bluesky (최우선)
1. https://bsky.app 가입 (이메일 인증)
2. 로그인 → Settings → **Privacy and Security** → **App Passwords** → **Add App Password** → 생성된 비밀번호 복사 (xxxx-xxxx-xxxx-xxxx)
3. 파일 열기: `marketing/ready_to_post/SET_SECRETS.py`
4. 상단에 값 입력:
   ```python
   "BLUESKY_HANDLE": "본인핸들.bsky.social",
   "BLUESKY_APP_PASSWORD": "xxxx-xxxx-xxxx-xxxx",
   ```
5. 터미널에서 실행: `python SET_SECRETS.py`
6. 끝. 다음 날 새벽부터 타로·별자리 글이 #해시태그 달려 **자동 게시**됩니다.

### B-2. 텔레그램 채널 (선택)
1. 텔레그램에서 **@BotFather** 검색 → `/newbot` → 봇 이름 정하고 **토큰** 받기
2. 채널 만들고(@아이디 공개), 그 봇을 채널 **관리자로 추가**
3. SET_SECRETS.py 에 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL`(@아이디) 입력 → 실행

### B-3. Pinterest (선택, 장기 트래픽)
1. https://developers.pinterest.com → 앱 생성 → access token, 보드 ID 확보
2. SET_SECRETS.py 에 `PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID` 입력 → 실행

> SET_SECRETS.py 는 빈 값은 건너뛰므로, **채운 채널만** 등록됩니다. 나중에 하나씩 추가해도 됩니다.

---

## ✅ C. 효과 확인 (주 1회면 충분)

- **방문자 통계**: https://tarofortune.pythonanywhere.com/admin/stats?key=saju2026admin
  (최근 14일 방문자·유입경로. `&days=30` 붙이면 30일)
- **Mastodon 글 확인**: https://mastodon.social/@tarosaju
- **광고 수익**: Google AdSense 대시보드 / 카카오 AdFit 대시보드 (본인 계정)

> 솔직한 현실: 지금 방문자가 거의 0이라 수익도 0입니다. 위 A(발행)를 꾸준히 하고 B(Bluesky)를 켜야 방문자가 생깁니다. **콘텐츠·자동화는 다 깔려있고, 남은 변수는 "도달"뿐**입니다.

---

# 2부. 자동으로 돌아가는 것 (당신이 안 해도 됨)

이 부분은 이미 코드로 만들어져 GitHub Actions에서 **매일 자동 실행**됩니다. 확인용으로만 읽으세요.

| 무엇 | 언제 | 상태 |
|---|---|---|
| **Mastodon·Lemmy·Dev.to 자동 게시** | 매일 새벽 1시(KST) | ✅ 작동 중 (실제 게시 확인됨) |
| 일주↔별자리↔타로 **3종 순환 게시** | 매일 | ✅ (Bluesky 켜면 더 커짐) |
| 신규 페이지 **검색엔진 자동 색인**(IndexNow→빙·네이버) | 매일 | ✅ |
| 3개 사이트 회전 홍보(타로·지역화폐·생활권) | 매일 | ✅ |

### 이번에 새로 만들어 둔 콘텐츠 (사람이 안 만들어도 됨)
- 🔮 **타로 78장** 의미(정·역방향) 한·영 + 오늘의 타로 — `/tarot`
- ♈ **별자리** 12종 한·영 — `/horoscope`, `/en/horoscope`
- 🩸 혈액형 · 🧩 MBTI · 🌙 꿈해몽 (한국어)
- 사이트맵 총 **1,387페이지** → 검색 유입 자산

### 내가(시스템이) 고친 핵심 버그
- 자동 게시 워크플로우가 **매일 취소되던 치명적 버그** 수정 → 이제 안 끊김
- 홍보 링크가 깨지던 버그(경로가 잘리던 것) 수정

---

# 3부. 요약 — 역할 분담 한 장

| | 당신(austriano) | 자동(시스템) |
|---|---|---|
| 글 작성 | ❌ 안 해도 됨 | ✅ 23편 완성 |
| 계정 만들기 | ✅ 본인만 가능 (Bluesky 등) | ❌ |
| 발행 「게시」 클릭 | ✅ 본인 (PUBLISH_CENTER로 1클릭) | 자동봇 채널은 ✅ 자동 |
| Secrets 등록 | ✅ 값만 채워 실행 | (스크립트가 자동 처리) |
| Mastodon/Lemmy/Devto 게시 | ❌ | ✅ 매일 자동 |
| 검색엔진 색인 | ❌ | ✅ 매일 자동 |
| 콘텐츠 페이지 | ❌ | ✅ 1,387개 |

**결론: 당신이 매일 할 일은 "PUBLISH_CENTER.html 열고 글 1~2개 발행"뿐. 나머지는 자동입니다.**
한 번만 Bluesky 켜두면(B-1) 그 발행조차 일부 자동화됩니다.
