# 즉시 게시용 홍보 콘텐츠 팩 (복붙 전용)

자동화가 불가능한 채널(레딧·네이버블로그·인스타·X·Quora·한국 카페)을 위해
**복사-붙여넣기만 하면 되는** 완성된 홍보 글 모음. 닉네임: **austriano**.

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
