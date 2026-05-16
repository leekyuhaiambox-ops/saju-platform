# 검색엔진 등록 가이드 (Google · Naver · Bing)

검색 트래픽이 풀로 들어오게 만드는 마지막 한 단계.

배포는 끝났지만 검색엔진이 자동으로 우리 사이트를 발견하기까지는 수 주가 걸립니다. **수동 등록하면 1~3일로 단축**됩니다.

---

## A. Google Search Console (5분, 가장 중요)

전 세계 검색 시장의 70% 이상을 책임집니다. 한국에서도 모바일 검색의 50%+가 구글.

### 등록 절차

1. **Google Search Console 접속**
   - https://search.google.com/search-console
   - 본인 구글 계정으로 로그인

2. **속성 추가**
   - 좌측 상단 드롭다운 → `+ 속성 추가`
   - `URL 접두어` 선택 (도메인 옵션은 DNS 권한 필요해서 패스)
   - 입력값: `https://tarofortune.pythonanywhere.com`

3. **소유권 확인**
   - 권장 방법: **HTML 태그** 선택
   - 표시되는 메타 태그 복사 (예시: `<meta name="google-site-verification" content="abc123xyz..." />`)
   - **content 값(abc123xyz... 부분)을 저에게 알려주세요** → 제가 코드에 박고 재배포
   - 또는 GUI에서 직접: PythonAnywhere에 base.html을 직접 수정해서 head에 붙여넣어도 됨

4. **확인 클릭**
   - 사이트 재배포 후 Search Console로 돌아가 `확인` 클릭

5. **사이트맵 제출** (소유권 확인 후 즉시)
   - 좌측 메뉴 → `Sitemaps` → 입력란에 `sitemap.xml` 입력 → 제출
   - 우리 사이트는 이미 `/sitemap.xml` 자동 제공 (60+개 URL)

### 등록 후 일주일

- `Coverage` 메뉴에서 인덱싱 진행 확인 (60+개 페이지 모두 인덱싱되는지)
- `Performance` 메뉴에서 검색 노출 시작 확인
- `Enhancements`에서 구조화 데이터(JSON-LD) 인식 확인

---

## B. Naver Search Advisor (가장 중요, 한국 트래픽 핵심)

한국 검색 시장 30~50%. **반드시 등록**.

### 등록 절차

1. **Naver Search Advisor 접속**
   - https://searchadvisor.naver.com/
   - 본인 네이버 계정으로 로그인

2. **사이트 추가**
   - 메인 화면 상단 입력란에 `https://tarofortune.pythonanywhere.com` 입력 → `등록`

3. **사이트 소유 확인**
   - 권장 방법: **HTML 태그** 선택
   - 메타 태그 복사 (예: `<meta name="naver-site-verification" content="abc123..." />`)
   - **content 값을 저에게 알려주세요** → 즉시 코드에 박고 재배포 (`base.html`에 이미 빈 슬롯 있음)

4. **확인 클릭**
   - 재배포 후 Naver Search Advisor에서 `확인` 클릭

5. **사이트맵 제출**
   - 등록된 사이트 → 좌측 `요청` → `사이트맵 제출`
   - 입력값: `https://tarofortune.pythonanywhere.com/sitemap.xml`

6. **RSS 제출 (선택)**
   - RSS는 아직 미구현 — 필요시 알려주세요. 추가 가능.

### 등록 후

- `진단` 메뉴에서 사이트 상태 점검
- `요청` → `웹페이지 수집` 으로 핵심 페이지 우선 색인 요청 가능 (홈/오늘의운세/궁합 등)
- 매주 `리포트` 확인

---

## C. Bing Webmaster Tools (보너스, 한국 영향 적음)

전 세계 시장 점유율 3~5%. 한국은 더 적음. 시간 남으면.

### 등록 절차

1. https://www.bing.com/webmasters/ 접속
2. **Sign in** → Microsoft 계정 (또는 구글 계정 연동)
3. **Add a site** 클릭
4. URL 입력: `https://tarofortune.pythonanywhere.com`
5. **Import from Google Search Console** 선택 (가장 빠름)
   - 이미 Google Search Console에 등록되어 있으면 자동 동기화
6. 또는 HTML 태그 인증 → `BingSiteAuth.xml` 파일 업로드

---

## D. 다음 (Daum)

다음은 Naver Search Advisor 자동 색인을 따라가는 경향이 있어 별도 등록 불필요. Naver 등록만 잘 되어 있으면 다음에서도 자연스럽게 노출.

---

## E. 등록 후 체크리스트 (4주간)

### 1주 후

- [ ] Google Search Console: 인덱싱된 페이지 5개 이상
- [ ] Naver: 사이트 상태 "정상" 표시
- [ ] 검색창에 `site:tarofortune.pythonanywhere.com` 검색 → 우리 페이지 노출 확인

### 2주 후

- [ ] Google: 인덱싱 30+ 페이지
- [ ] 첫 검색 노출 발생 ("갑자 일주" 등 롱테일)
- [ ] Search Console `Performance` 에서 평균 노출 위치 확인

### 4주 후

- [ ] Google: 인덱싱 70+ 페이지 (전체)
- [ ] 일평균 검색 노출 50회 이상
- [ ] 클릭률(CTR) 5% 이상

---

## F. 색인이 잘 안 될 때 점검 사항

1. **robots.txt** 가 크롤링 차단 안 하는지
   - 확인: https://tarofortune.pythonanywhere.com/robots.txt
   - 우리 사이트는 `User-agent: * / Allow: /` 로 모든 봇 허용 중 ✓

2. **사이트맵 형식 정확한지**
   - 확인: https://tarofortune.pythonanywhere.com/sitemap.xml
   - 60+개 URL 다 들어있는지 ✓

3. **외부 백링크 없음**
   - 새 사이트는 외부 링크가 없으면 인덱싱 느림
   - 해결: SNS·블로그에 사이트 링크 1~2개 게시 → 봇이 따라옴

4. **콘텐츠 품질 의심**
   - AI 자동 생성 콘텐츠로 의심받으면 색인 지연
   - 해결: 본문 충실, 자체 작성

5. **PythonAnywhere 무료 티어 응답 속도**
   - 가끔 봇 크롤링 중 타르핏 걸려 지연
   - 해결: 캐싱 강화 (이미 구현됨), 페이지 속도 개선

---

## G. 진행 순서 정리

1. **지금 즉시**: Google Search Console 사이트 추가 → 메타 태그 값 받기
2. **2분 뒤**: 메타 태그 값을 저에게 전달 → 제가 코드 박고 재배포
3. **3분 뒤**: Google Search Console에서 확인 클릭 → 인증 성공
4. **5분 뒤**: 사이트맵 제출
5. **같은 흐름으로 Naver Search Advisor도 진행**
6. **다음 날**: 색인 시작 확인
7. **1주 후**: 첫 검색 노출 확인

지금 시작하시겠어요? Google/Naver 각각 메타 태그를 받으시면 즉시 처리해 드리겠습니다.
