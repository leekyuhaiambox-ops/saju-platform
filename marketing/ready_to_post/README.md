# 즉시 게시용 홍보 콘텐츠 팩 (발행만 누르면 됨)

자동화가 불가능한 채널을 위해 **세팅을 끝까지 다 해놓은** 홍보 도구. 닉네임: **austriano**.

## ⭐ 먼저 이 두 개만 쓰면 됨

### 1) `PUBLISH_CENTER.html` — 원클릭 발행 센터 (제일 편함)
파일을 **더블클릭**하면 브라우저에 열립니다. 글마다 버튼:
- **X / Threads / Reddit** → 버튼 누르면 작성창이 **내용 자동입력된 채로** 열림 → 「게시」 한 번이면 끝.
- **블로그 / Quora / 카페** → 「복사」 버튼 → 작성창 열고 붙여넣기 → 게시.
- 상단 필터로 채널별 보기. 휴대폰에서도 파일 열면 동일하게 작동.

### 2) `SET_SECRETS.py` — Bluesky/Telegram/Pinterest 자동 가동
계정·앱 생성(본인만 가능) 후, 파일 상단 `CREDS`에 **값만 채우고** 실행:
```
python SET_SECRETS.py
```
→ GitHub Secrets에 자동 등록 → 다음 cron부터 봇이 알아서 게시. (PAT는 자동 인식, 하드코딩 없음)

---

## 원문 모음 (PUBLISH_CENTER가 이걸 그대로 씀)
**복사-붙여넣기용** 완성 홍보 글.

| 파일 | 채널 | 언어 | 글 수 |
|---|---|---|---|
| `01_reddit_EN.md` | Reddit (r/tarot·astrology·Divination·Korea·learnkorean) | 영문 | 6 |
| `02_naver_tistory_KR.md` | 네이버 블로그 / 티스토리 (SEO 장문) | 한국어 | 3 |
| `03_threads_instagram_X.md` | Threads / Instagram / X | 한·영 | 8 |
| `04_quora_KR_communities.md` | Quora + 한국 카페/게시판 | 한·영 | 6 |

## 운영 팁 (밴/저품질 회피)
1. **하루 1~2개씩**, 채널별로 다른 글. 같은 글 도배 금지.
2. 레딧·커뮤니티는 **가치 먼저** 톤(이미 그렇게 작성됨). 댓글 질문엔 성실히 답.
3. 블로그 글은 도입부 1~2문장만 본인 말투로 바꾸면 중복 저품질 회피.
4. 가능하면 이미지 1장 첨부 → 체류시간·도달↑.
5. 모든 링크에 신규 고볼륨 페이지(/tarot, /horoscope, /today) 사용 — 자동봇과 동일 전략.

## 자동으로 이미 돌고 있는 채널 (직접 안 해도 됨)
- **Mastodon @tarosaju** + **Lemmy /u/tarofortune** + **Dev.to**: multi-site-bot이 매일 자동 게시 중.
- 위 복붙 채널은 자동화가 막힌 곳만 보완하는 용도.

## 도달을 키우는 최우선 무료 레버 (credential만 넣으면 자동화됨)
- **Bluesky**: bsky.app 가입 → App Password → GitHub Secrets에 `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` 등록.
  → 코드는 이미 완성(타로/별자리 #해시태그 교차게시). secret만 넣으면 다음 cron부터 자동.
- Telegram: @BotFather로 봇 생성 → `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL` 등록.
- Pinterest: 개발자 앱 → `PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID` 등록.
