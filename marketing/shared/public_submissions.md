# Public Platform Submissions — Drafts for 3 Sites

> 운영자가 직접 로그인해서 제출해야 하는 플랫폼들의 완성 카피.
> 모든 텍스트는 복붙 가능. 가입 절차도 함께 정리.

---

## A. Hacker News — Show HN

### tarofortune (사주)

**Title** (80 char limit):
```
Show HN: Free Korean four-pillars (saju) astrology calculator, no signup
```

**URL**: `https://tarofortune.pythonanywhere.com/en`

**First comment** (선택 — 작성자가 직접 단 첫 댓글이 알고리즘에 중요):
```
Built this solo over a couple months. Saju is the Korean four-pillars astrology system — given a birth date+time, it computes a 4×2 grid (year/month/day/hour × heavenly stem/earthly branch). The day-pillar is the personality archetype, like a 60-fold zodiac.

Stack is Flask + Pillow for dynamic OG card generation, no DB. Calculator uses Meeus astronomical algorithms for solar terms (절기 boundaries shift the month-pillar). Free, no signup, no email collection.

Korean version at /, English at /en. Same engine, different interpretation data.

Happy to answer questions about the algorithm or the data model.
```

### currency-map

**Title**:
```
Show HN: Interactive map of 31-city local-currency merchants in Korea (PWA)
```

**URL**: `https://gyeonggi-currency-map.web.app/`

**First comment**:
```
Korea has municipal local currencies that pay 6–10% top-up bonus. Gyeonggi Province (14M residents) issues one across 31 cities. The official merchant search is a per-city list, no map, no business filter.

Solved it with a React+Vite+Leaflet PWA on Firebase Hosting. Public open data from the province's API, no backend. PWA installable, KakaoTalk share with dynamic OG cards.

The interesting bit was Naver SEO — Korea's dominant search engine still has limited JS rendering, so I'm planning Vite SSG for 31 pre-rendered city pages.

Source: closed for now, will open-source the rewrite.
```

### geoinfomatic

**Title**:
```
Show HN: Isochrone-based neighborhood analyzer for Korea, no real estate
```

**URL**: `https://geoinfomatic.pythonanywhere.com/`

**First comment**:
```
Every Korean real-estate site pushes property listings. I built the inverse: pick an address, draw a 10/20/30/45-minute walking or transit isochrone, see reachable subway stations + 8 facility types (school, hospital, mart, park, gym, pharmacy, library, cafe) inside the polygon, get a 100-point composite score and an AI one-sentence summary.

For transit, the result is split by transfer count (0/1/2+ transfers) — the most useful UI decision in the project.

Stack: Flask + Leaflet + OSRM walking graph + custom Korean subway graph. PythonAnywhere free tier. Freemium: 5 analyses/day free, 9,900 KRW/month Pro for unlimited + PDF reports.

No listings, no agents. Pure accessibility.
```

### 제출 절차
1. https://news.ycombinator.com/submit (계정 필요 — karma 50+ 권장)
2. 제목 그대로 붙여넣기 → submit
3. 본인 글에 즉시 1번 댓글 달기 (위 first comment)
4. 첫 1시간이 모든 것 — 댓글 빠른 응답 시 front page 가능성 ↑

---

## B. Product Hunt

### tarofortune

**Name**: Saju Astrology — Free Korean Four-Pillars Calculator
**Tagline** (60 char): Free, accurate Korean four-pillars astrology, in EN + KR
**Description** (260 char):
```
A free, no-signup Korean four-pillars (saju) astrology calculator. Computes your day-pillar (one of 60 personality archetypes), five elements balance, ten gods, and twelve life stages. Daily luck check. Korean + English. Open data, no email needed.
```
**Topics**: Astrology · Productivity · Self-improvement · Free Tools

### currency-map

**Name**: Gyeonggi Currency Map
**Tagline**: 31-city Korean local-currency merchant map, real-time open filter
**Description**:
```
Interactive PWA showing all participating merchants for Gyeonggi Province's municipal currencies, across 31 cities. Business-type filter, real-time "open now" toggle, KakaoTalk share. PWA installable. Built on open data with React + Vite + Leaflet on Firebase Hosting.
```
**Topics**: Maps · Korea · Open data · PWA · Civic tech

### geoinfomatic

**Name**: GeoInfomatic — Korean Living Zone Analyzer
**Tagline**: Isochrone neighborhood scoring, no real-estate listings
**Description**:
```
Pick an address, see the 10–45 min walking or transit isochrone, plus all subway stations and 8 facility types inside it. 100-point accessibility score, AI summary, transfer-count breakdown (0/1/2+). Built for moving-decision, urban planning, real-estate due diligence — without any listings clutter.
```
**Topics**: Productivity · Real estate · Maps · Korea · Urban planning

### 제출 절차
1. https://www.producthunt.com (계정 필요)
2. Submit a product → 사이트별 따로 3개 등록 (한 번에 1개씩, 1~2주 간격)
3. Hunt scheduling: 화·수·목 09:00 PST (한국 시간 23:00 화·수·목) — 새 product 가장 많이 노출되는 시간대
4. 첫 24시간 친구·팔로워에게 upvote 부탁 (게이밍 X — 진짜 사용자만)

---

## C. awesome-list PR 후보

### awesome-civic-tech (PR 작성용)

**Repo**: https://github.com/datafire/awesome-civic-tech

**PR 변경 라인** (해당 섹션):
```markdown
### Maps / Visualization

- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app/) — Interactive PWA mapping municipal local-currency merchant locations across all 31 cities in Gyeonggi Province, South Korea. Built on public open data. React + Leaflet + Firebase.

### Urban Planning / Accessibility

- [GeoInfomatic — Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com/) — Isochrone-based neighborhood accessibility analyzer for South Korea. Walking or transit, 10–45 min radius, 8 facility types, AI-generated summary.
```

**PR 메시지**:
```
Add two Korean civic-tech projects: Gyeonggi Currency Map (PWA) and GeoInfomatic accessibility analyzer.

Both are solo-developed, open-data based, free to use.
```

### awesome-korea (한국 관련 모음 list)

**검색**: https://github.com/search?q=awesome+korea — best fit:
- https://github.com/keon/awesome-korea-tech
- https://github.com/PracticalKorean/awesome-korea

**추가 라인**:
```markdown
- [TaroFortune (사주명리 풀이)](https://tarofortune.pythonanywhere.com) — Free Korean four-pillars (saju) astrology calculator with Korean + English interpretations.
- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) — 31-city local-currency merchant map for Gyeonggi Province.
- [GeoInfomatic](https://geoinfomatic.pythonanywhere.com) — Korean isochrone-based neighborhood accessibility analyzer.
```

### awesome-pwa

**Repo**: https://github.com/hemanth/awesome-pwa 또는 류

**라인**:
```markdown
- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) — Real-world Korean municipal-currency merchant search, installable PWA with KakaoTalk share integration.
```

### awesome-leaflet

**Repo**: https://github.com/aitorzaldua/awesome-leaflet

**라인**:
```markdown
- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) — Interactive merchant search PWA for 31 Korean cities.
- [GeoInfomatic](https://geoinfomatic.pythonanywhere.com) — Isochrone accessibility analyzer with multi-facility overlay.
```

---

## D. Reddit (각 서브레딧, 운영자 직접 게시)

### r/SideProject

**Title**: I built 3 free tools for Korean life (saju astrology, currency map, neighborhood analyzer)

**Body**:
```
Solo dev in Korea here. Over the past couple months I shipped three small free tools for everyday Korean life:

🔮 **Saju Astrology** — https://tarofortune.pythonanywhere.com
Free Korean four-pillars calculator (KR + EN). Like a 60-fold zodiac.

🗺 **Gyeonggi Currency Map** — https://gyeonggi-currency-map.web.app
Interactive map of local-currency merchants across all 31 cities in Gyeonggi Province (14M residents).

🏘 **GeoInfomatic** — https://geoinfomatic.pythonanywhere.com
Isochrone-based neighborhood analyzer. Pick an address, see reachable schools/marts/subways in 30 min. No real-estate listings, just accessibility.

All free or freemium, ad-supported, no investor money, no team.

Happy to chat about any of these — particularly the Naver SEO realities and how Korean PWA discovery is genuinely different from the West.
```

### r/IndieDev / r/webdev

같은 본문, 기술 스택 중심으로 살짝 수정.

### r/korea (r/southkorea도)

**Title**: I made some free tools for Korean residents — feedback welcome

**Body**: 
```
거주자 입장에서 막연했던 두 가지를 해결하려고 도구 두 개 만들었습니다.

1. **경기지역화폐 가맹점 통합 지도** — https://gyeonggi-currency-map.web.app
31개 시·군 가맹점을 한 지도에서. 업종 필터 + 영업중 토글.

2. **생활권 접근성 분석** — https://geoinfomatic.pythonanywhere.com
도보 30분 내 학교·마트·지하철 도달 점수.

광고 없고 무료 (지역화폐 지도) / 일 5회 무료 (생활권 분석).

피드백 주시면 우선 반영합니다.
```

⚠️ Reddit 신규 계정은 spam 의심으로 자동 차단됨. 카르마 100+ 운영자 본인 계정으로만 게시 권장.

---

## E. Indie Hackers

**플랫폼**: https://www.indiehackers.com/

**Group**: Building in Public · Side Projects · Bootstrapping

**Post (한 사이트씩 또는 통합)**:
```
Title: Shipped 3 niche freemium tools for Korean life — first revenue thoughts

Body: 
Solo bootstrapper from Korea. Over 2 months I shipped:

1. Korean astrology calculator (ad-supported)
2. Local-currency merchant map (ad-supported)
3. Neighborhood accessibility analyzer (freemium, 9,900 KRW Pro)

All running on free tiers: PythonAnywhere + Firebase Hosting + GitHub Actions for bot automation.

Three observations:
- Korean ad networks (Kakao AdFit) pay way better than AdSense for Korean traffic
- Freemium with low absolute price (~$7/mo) converts better than I expected for niche tools
- Naver SEO is genuinely different from Google — Vite SSG made a measurable difference

What questions would you have about going freemium for a tiny niche?
```

---

## F. Korean Tech 매체 — 자체 카피 (운영자 송부용)

### 디지털타임스 (자세히는 보도자료에 따로 정리)
### 디비투엠 / 디스이즈게임 등 IT 매체 → 운영자 송부

---

## 제출 우선순위

| 우선 | 플랫폼 | 사이트 | 소요 | 효과 추정 |
|---|---|---|---|---|
| 🔥1 | **Show HN** | currency-map (most front-page potential) | 10분 | front page 시 트래픽 1만+ |
| 🔥2 | **Product Hunt** | geoinfomatic (Pro 수익화 funnel) | 30분 | upvote 100+ 시 트래픽 1k+ |
| 🔥3 | **r/SideProject** | 통합 글 | 5분 | 댓글 활발 시 1k+ |
| ⚡4 | **awesome-civic-tech PR** | currency-map | 20분 | 영구 백링크 |
| ⚡5 | **Indie Hackers** | 통합 freemium 글 | 15분 | 비슷한 빌더 네트워크 |
| 🌱6 | **awesome-pwa / awesome-leaflet PR** | currency-map | 20분 | 영구 백링크 |

---

## 절대 금지

❌ 같은 글 여러 서브레딧 동시 게시 (cross-post 정책 위반)  
❌ 가짜 upvote / sock puppet 계정 (Product Hunt·Reddit 모두 영구 ban)  
❌ Show HN에 본인이 댓글로 self-praise (downvote 폭격)  
❌ 너무 잦은 awesome-list PR (스팸 분류)
