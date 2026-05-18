# 토스 미니앱 — 사주명리 (tarofortune) 인수인계서

> 다른 Claude Code 세션에서 이 문서를 그대로 첫 메시지로 붙여넣으면 즉시 작업 시작 가능합니다.

---

## 0. 프로젝트 컨텍스트 (반드시 먼저 읽기)

### 무엇을 만드나
**한국 사주명리학을 토스 미니앱**으로. 기존 Flask 백엔드(API)를 **재사용**하고 React 프론트엔드만 새로 작성.

### 무엇이 이미 만들어져 있나
- ✅ **백엔드 라이브**: https://tarofortune.pythonanywhere.com
- ✅ **5개 JSON API** + CORS 헤더 모두 활성
- ✅ 사주 계산 (Meeus 천문 알고리즘, 24절기 분 단위)
- ✅ 60갑자 일주별 풀이 60개 (한·영)
- ✅ 십신·십이운성·오행 해설
- ✅ 일진·띠별 운세·궁합 분석
- ✅ Lemmy·Mastodon·Dev.to 자동 게시 봇 (참고용)

### 토스 미니앱이 할 일
1. 기존 백엔드 API를 호출해 사주 결과 가져오기
2. 토스 디자인 시스템(TDS)에 맞는 React UI로 표시
3. AdSense/AdFit **금지** (토스 정책)
4. Toss Pay로 프리미엄 풀이 결제 가능
5. 푸시 알림으로 일일 운세 발송

### 작업 범위
- ✅ 만들 것: 토스 React 프론트엔드 (~10시간 작업)
- ❌ 만들지 말 것: 사주 계산 로직 재구현, 별도 백엔드

---

## 1. 시작 3단계 (사용자 명령어)

### Step 1 — Apps in Toss MCP 추가
```bash
claude mcp add --transport stdio apps-in-toss ax mcp start
```
이걸로 Claude Code가 토스 공식 문서를 실시간 참조.

### Step 2 — 프로젝트 생성
```bash
cd C:\Users\master\CEO
npx create-ait-app tarofortune-toss
cd tarofortune-toss
```

### Step 3 — Claude에 이 문서 + 첫 요청
> "C:\Users\master\CEO\saju_platform\HANDOFF_TOSS_MINIAPP.md 파일을 먼저 읽고, 그 내용에 따라 토스 미니앱 사주명리 MVP를 만들어줘."

---

## 2. 백엔드 API 명세 (그대로 호출하면 됨)

**Base URL**: `https://tarofortune.pythonanywhere.com`

CORS: `Access-Control-Allow-Origin: *` (모든 origin 허용 — 토스 미니앱에서 직접 fetch 가능)

### 2.1 POST `/api/saju` — 사주 풀이

**Request** (JSON body):
```json
{
  "year": 1990,
  "month": 5,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "gender": "남",            // 또는 "여"
  "unknown_hour": false,     // true면 시주 제외
  "lang": "ko"               // 또는 "en"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "name": "",
    "gender": "남",
    "year": 1990, "month": 5, "day": 15, "hour": 14, "minute": 30,
    "year_pillar":  { "stem": 6, "branch": 6,  "name": "경오", "hanja": "庚午" },
    "month_pillar": { "stem": 7, "branch": 5,  "name": "신사", "hanja": "辛巳" },
    "day_pillar":   { "stem": 6, "branch": 4,  "name": "경진", "hanja": "庚辰" },
    "hour_pillar":  { "stem": 9, "branch": 7,  "name": "계미", "hanja": "癸未" },
    "ten_gods":     { "year_stem": "비견", ... },
    "twelve_stages":{ "year": "쇠", "month": "장생", "day": "양", "hour": "묘" },
    "element_counts": { "목": 0, "화": 2, "토": 2, "금": 3, "수": 1 },
    "hidden_stems": { "year": ["병", "기", "정"], ... },
    "day_master": "경",
    "day_master_element": "금"
  },
  "interpretation": {
    "day_pillar_name": "경진(庚辰)",
    "day_pillar_headline": "큰 흙더미 속의 광석, 잠재력 큰 인재",
    "day_pillar_detail": "야망과 추진력이 강하고 ...",
    "summary_line": "경진(庚辰) 일주 — ...",
    "ten_god_counts": { "비견": 1, "정관": 2, ... },
    "ten_god_meanings": { "비견": "독립심·자존심·동료...", ... },
    "element_pct": { "목": 0.0, "화": 25.0, "토": 25.0, "금": 37.5, "수": 12.5 },
    "max_element": "금",
    "min_element": "목",
    "element_meaning": { "금": ["결단·의리(義)", "단단한 광물의 기운..."], ... },
    "day_twelve_stage": "양",
    "twelve_stage_meaning": { "양": "태아가 자라는 단계...", ... }
  },
  "daewoons": [
    { "age": 10, "stem": 8, "branch": 6, "name": "임오", "ten_god_stem": "식신", "twelve_stage": "목욕" },
    ... (10개)
  ],
  "day_pillar_index": 16
}
```

### 2.2 GET `/api/today` — 오늘의 일진
선택 파라미터: `?date=2026-05-17`

**Response**:
```json
{
  "ok": true,
  "date": "2026-05-17",
  "day_pillar_name": "경인",
  "day_pillar_hanja": "庚寅",
  "day_pillar_index": 26,
  "day_element": "금",
  "month_pillar_name": "계사",
  "year_pillar_name": "병오",
  "keyword_title": "결단·정리",
  "keyword_body": "결정과 마무리에 적합한 날입니다...",
  "lucky_color": "흰색·은색",
  "lucky_direction": "서쪽",
  "lucky_number": 7
}
```

### 2.3 GET `/api/pillars` — 60갑자 전체 목록
`?lang=en` 지원.

**Response**:
```json
{
  "ok": true,
  "pillars": [
    { "index": 0, "name": "갑자(甲子)", "headline": "큰 나무가...", "detail": "총명하고..." },
    ... (60개)
  ]
}
```

### 2.4 GET `/api/pillar/<idx>` — 특정 일주 상세
`idx`: 0~59 정수. `?lang=en` 지원.

**Response**:
```json
{
  "ok": true,
  "index": 0,
  "name": "갑자(甲子)",
  "headline": "큰 나무가 깊은 우물물을 만난 격, 지성과 인내의 학자형",
  "detail": "총명하고 학구열이 강하며 ...",
  "stem_kr": "갑",  "branch_kr": "자",
  "stem_hanja": "甲", "branch_hanja": "子",
  "element": "목"
}
```

### 2.5 GET `/api/zodiac/<name>` — 띠별 운세
`name`: 한글 (쥐·소·호랑이·...) 또는 영문 (rat·ox·tiger·...)

**Response**:
```json
{
  "ok": true,
  "name": "용",
  "trait": ["辰", "야망·이상·창조성", "큰 그림을 그리는 비전형..."],
  "this_year": "병오",
  "this_year_number": 2026,
  "relations": [["평운", "안정된 흐름..."]],
  "today": { /* /api/today 와 동일 구조 */ }
}
```

### 2.6 POST `/api/compatibility` — 두 사람 사주 궁합

**Request**:
```json
{
  "p1": { "year": 1990, "month": 5, "day": 15, "hour": 14, "minute": 30, "gender": "남" },
  "p2": { "year": 1992, "month": 8, "day": 20, "hour": 10, "minute": 0,  "gender": "여" }
}
```

**Response**:
```json
{
  "ok": true,
  "score": 75,
  "grade": "상",
  "advice": "함께 있을 때 편안함과 안정이 큰 관계입니다...",
  "notes": [
    ["일간 천간합", "을경합금 — 마음이 자연스럽게 끌리는 인연입니다.", "+20"],
    ...
  ],
  "p1": { /* /api/saju result와 동일 구조 */ },
  "p2": { ... }
}
```

---

## 3. 디자인 시스템 (기존 웹과 톤 맞추기)

### 3.1 색상 팔레트

```css
/* 다크 테마 (기본) */
--bg:        #0f0817;   /* 가장 어두운 배경 */
--bg-2:      #1a0f2e;   /* 카드/섹션 배경 */
--bg-3:      #251943;   /* 강조 배경 */
--bg-card:   #1e1535;   /* 카드 표면 */
--border:    #3d2e5e;   /* 경계선 */
--text:      #f3eee8;   /* 본문 */
--text-dim:  #b9adc4;   /* 약한 본문 */
--text-mute: #8b7e98;   /* 가장 약한 텍스트 */
--accent:    #daa520;   /* 황금색 — 메인 강조 */
--accent-2:  #f4cf6b;   /* 밝은 황금 */
--accent-3:  #c9914a;   /* 따뜻한 황금 */

/* 오행 5색 */
--elem-목: #4a9b6e;  /* Wood — 녹색 */
--elem-화: #d04a4a;  /* Fire — 적색 */
--elem-토: #c39845;  /* Earth — 황갈색 */
--elem-금: #c6cdd4;  /* Metal — 은색 */
--elem-수: #4a78c8;  /* Water — 청색 */
```

⚠️ 토스 디자인 시스템(TDS)의 라이트 테마가 기본이지만, 사주는 다크 테마가 분위기에 맞음. **토스 가이드 확인 후 결정** — TDS Container Dark Mode 사용하거나, 본문 영역만 다크.

### 3.2 폰트
- 한글 본문: `Noto Sans KR`
- 한글 제목/한자: `Noto Serif KR`
- 영문: 시스템 폰트
- 한자(60갑자 이미지)는 Serif KR로 크게 표시 (시각적 임팩트)

### 3.3 브랜드 마크
- 메인 한자: `命` (운명) — 황금색 굵은 Serif
- 색: `var(--accent)` (#daa520)
- 폰트 사이즈: 페이지 헤로 5rem, 헤더 1.25rem

### 3.4 OG 카드 / 공유 이미지
기존 `static/img/og/pillar-0.png` ~ `pillar-59.png` (60장) 모두 사용 가능. 동적 OG는 `https://tarofortune.pythonanywhere.com/og/result.png?y=1990&m=5&d=15&h=14&min=30&g=남&n=홍길동&lang=ko` 형태 호출.

---

## 4. 최소 필요 페이지 (MVP)

| # | 페이지 | 라우트 | 핵심 호출 |
|---|---|---|---|
| 1 | 사주 입력 | `/` | (없음) |
| 2 | 사주 결과 | `/result` | `POST /api/saju` |
| 3 | 오늘의 운세 | `/today` | `GET /api/today` |
| 4 | 60갑자 일주 목록 | `/pillars` | `GET /api/pillars` |
| 5 | 일주 상세 | `/pillar/:idx` | `GET /api/pillar/:idx` |
| 6 | 띠별 운세 | `/zodiac/:name` | `GET /api/zodiac/:name` |
| 7 | 궁합 | `/compatibility` | `POST /api/compatibility` |

**MVP는 1·2·3·5번 우선**. 나머지는 v1.1 이후.

---

## 5. 토스 미니앱 특별 요구사항

### 5.1 광고 금지
AdSense/AdFit 등 외부 광고 코드 **절대 추가 X**. (토스 미니앱 정책)

### 5.2 Toss Pay 통합 (선택)
프리미엄 풀이 결제: `apps-in-toss` SDK의 `payments.requestPayment()` 사용. 예시는 토스 MCP가 자동으로 가져옴.

### 5.3 푸시 알림 (강력 추천)
일일 운세 푸시는 토스 미니앱의 강력한 무기. 사용자 동의 받으면 매일 아침 8시 푸시. SDK: `apps-in-toss` notifications API.

### 5.4 외부 링크 처리
"더 자세한 풀이는 웹에서" 같은 외부 링크는 `Linking.openURL('https://tarofortune.pythonanywhere.com')` 형태로. 토스 인앱 브라우저로 열림.

### 5.5 백 버튼 / 네비게이션
React Router의 history와 Toss의 시스템 백 버튼 통합 필요. Apps in Toss SDK 가이드 따름.

---

## 6. 개발 흐름 (사용자 가이드)

```
아이디어 → Claude Code에 "내가 만들고 싶은 건 [한 줄]. 모호하면 질문하고, 토스 미니앱으로 시작점부터 순서대로 알려줘."
→ 자동 모드로 기능 구현
→ HTML/시뮬레이터로 UX 확정
→ "앱으로 만들어줘" → 토스 시뮬레이터에서 실제 테스트
→ v1.1, v1.2 점진 개선
```

### 막혔을 때
- **에러 그대로 붙여넣기**: `"[에러 전체] 원인과 해결?"`
- **우회로**: `"A 시도 → B 오류. C 목표인데 다른 방법?"`
- **리스크 체크**: `"이 방법 말고 다른 선택지? 장단점?"`
- **참고 코드 활용**: `"A는 정상 동작. 우리 코드와 구조적 차이?"`

---

## 7. 사용자 정보 (있으면 참고)

- **PythonAnywhere**: tarofortune (token 별도 보관)
- **AdSense**: ca-pub-4682723571700089 (웹용, 토스 미니앱과 무관)
- **소유자 이메일**: leekyuha.iambox@gmail.com

---

## 8. 사주 도메인 핵심 용어 (UI 표기용 참고)

| 한국어 | 한자 | 영문 |
|---|---|---|
| 사주 | 四柱 | Saju / Four Pillars |
| 일주 | 日柱 | Day Pillar |
| 일간 | 日干 | Day Master |
| 십신 | 十神 | Ten Gods |
| 십이운성 | 十二運星 | Twelve Life Stages |
| 오행 | 五行 | Five Elements |
| 60갑자 | 六十甲子 | Sixty Pillars |
| 대운 | 大運 | Daewoon (Decadal Luck) |
| 24절기 | 二十四節氣 | 24 Solar Terms |
| 입춘 | 立春 | Ipchun |
| 야자시 | 夜子時 | Late Zi Hour |

---

## 9. 첫 명령 예시 (다른 세션에서 사용할 프롬프트)

```
이 폴더의 HANDOFF_TOSS_MINIAPP.md를 먼저 읽어줘.
그 다음 토스 미니앱 사주명리 MVP를 만들 거야.

순서:
1. 백엔드 API 5개 동작 확인 (curl로 /api/today 호출해서 응답 확인)
2. create-ait-app 프로젝트 구조 파악
3. 입력 폼 → 결과 페이지 흐름 우선 구현 (P0)
4. 토스 시뮬레이터 실행해서 UX 확인
5. 60갑자 목록 + 오늘의 운세 페이지 추가 (P1)
6. 막히면 토스 MCP로 공식 문서 참조

광고 코드 절대 X. 토스 디자인 가이드 따름. 다크 테마 또는 황금색 강조.
색상 팔레트와 폰트는 HANDOFF 문서 3절 참고.
```

---

## 10. 체크리스트 (배포 전)

- [ ] 광고 코드 (AdSense/AdFit/Meta Pixel/GA) 완전 제거 확인
- [ ] HTTPS 자동 (Apps in Toss는 자동)
- [ ] 백엔드 API 응답 시간 측정 (`/api/saju` 1초 이내)
- [ ] 다크 모드 OR 라이트 모드 통일 (혼합 X)
- [ ] 토스 디자인 가이드라인 검토
- [ ] 시뮬레이터에서 안드로이드 + iOS 양쪽 테스트
- [ ] 사주 풀이 결과 정확도 5건 검증 (알려진 사주와 대조)
- [ ] 면책 조항 노출 ("의료·법률·재정 의사결정 근거 아님")

---

## 11. FAQ

**Q: 사주 계산 코드를 React로 다시 짜야 하나?**
A: ❌ 아니요. 백엔드 API 호출만 하면 됨. 계산은 PythonAnywhere에서.

**Q: API가 느리면?**
A: PythonAnywhere 무료 티어라 첫 호출 1~2초 가능. 캐싱은 백엔드에 이미 적용됨 (LRU). 추가 최적화는 결과 페이지 SSR 처리로 가능.

**Q: 토스 미니앱 심사 통과 기준?**
A: ① 광고 없음 ② 결제 시 Toss Pay 사용 ③ 디자인 가이드 ④ 미성년자 부적절 콘텐츠 X. 사주는 ④번 통과 (자기이해 도구로 분류).

**Q: 푸시 알림은 어떻게?**
A: SDK의 `notifications.scheduleDaily()` 사용. 매일 아침 8시 사용자 사주 기반 일진 푸시.

**Q: 웹 사이트랑 콘텐츠 같으면 토스가 거절하나?**
A: 거절 사유 아님. 토스 미니앱은 동일 콘텐츠를 토스 친화적으로 재구성한 것으로 보면 됨.

**Q: 수익 모델?**
A: ① Toss Pay 프리미엄 풀이 ② 보상형 광고 (Toss 광고 SDK만 가능) ③ 웹사이트 유도 (외부 링크 → 거기서 AdSense)

---

## 12. 연락 / 참고

- 백엔드 코드: `C:\Users\master\CEO\saju_platform\`
- 웹 사이트: https://tarofortune.pythonanywhere.com
- 영문 사이트: https://tarofortune.pythonanywhere.com/en
- GitHub: https://github.com/leekyuhaiambox-ops/saju-platform
- Apps in Toss 공식 문서: MCP가 자동 참조

---

**문서 작성**: 2026-05-17
**프로젝트 위치 (예정)**: `C:\Users\master\CEO\tarofortune-toss\`
**백엔드 변경 시 이 문서 동기화 필요.**
