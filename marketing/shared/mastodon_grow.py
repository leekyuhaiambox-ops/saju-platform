"""Mastodon organic 성장 — 관련 해시태그 활동 계정 팔로우로 팔로우백·알고리즘 노출 유도.

봇이 혼잣말만 하던 문제(followers 0) 대응. 매일 소량(15~20) 팔로우 →
- 팔로우백으로 followers 증가
- 활동성 시그널로 알고리즘 노출 개선
- 관심사 매칭 계정이라 실제 상호작용 가능성

과도한 팔로우는 스팸 판정 → 일 20 상한. 이미 팔로우한 계정 재팔로우 안 함(API가 무시).

⚠️ 운영자 액션 필요 (2026-07 확인):
   현재 MASTODON_ACCESS_TOKEN 은 write:statuses scope 만 있어 팔로우가 403
   ("This action is outside the authorized scopes"). 팔로우 자동화를 켜려면:
   1. https://mastodon.social/settings/applications 에서 앱 편집
   2. write:follows (또는 write, follow) scope 추가 후 토큰 재발급
   3. GitHub Secrets + .env 의 MASTODON_ACCESS_TOKEN 교체
   그때까지 이 스크립트는 조회만 하고 팔로우는 skip 로그를 남김.

실행: python mastodon_grow.py [--max 20]
환경변수: MASTODON_ACCESS_TOKEN, MASTODON_INSTANCE
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

TOKEN = os.environ.get("MASTODON_ACCESS_TOKEN", "")
INSTANCE = os.environ.get("MASTODON_INSTANCE", "mastodon.social")
TAGS = ["astrology", "tarot", "bazi", "divination", "zodiac", "horoscope", "spirituality"]


def api(method, path, data=None, auth=True):
    """auth=False면 공개 API로 조회 (토큰 read scope 없을 때 우회)."""
    url = f"https://{INSTANCE}/api/v1{path}"
    body = urllib.parse.urlencode(data).encode() if data else None
    headers = {}
    if auth:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=20)
    args = ap.parse_args()

    if not TOKEN:
        print("MASTODON_ACCESS_TOKEN 필요")
        return 1

    me = api("GET", "/accounts/verify_credentials")
    my_id = me["id"]
    print(f"현재: following={me['following_count']} followers={me['followers_count']} toots={me['statuses_count']}")

    followed = 0
    seen = set()
    for tag in TAGS:
        if followed >= args.max:
            break
        try:
            # 태그 타임라인은 공개 API — read scope 없이 조회 (auth=False)
            statuses = api("GET", f"/timelines/tag/{tag}?limit=10", auth=False)
        except Exception as e:
            print(f"  {tag}: {e}")
            continue
        for s in statuses:
            if followed >= args.max:
                break
            acct = s.get("account", {})
            aid = acct.get("id")
            if not aid or aid in seen or aid == me["id"]:
                continue
            seen.add(aid)
            if acct.get("followers_count", 0) < 5 or acct.get("bot"):
                continue
            try:
                api("POST", f"/accounts/{aid}/follow")
                followed += 1
                print(f"  팔로우: @{acct.get('acct')} (followers {acct.get('followers_count')})")
                time.sleep(1.5)
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    print("⚠️ 팔로우 권한 없음 (write:follows scope 필요) — 토큰 재발급 필요. 중단.")
                    print("   docstring 참고: mastodon.social/settings/applications")
                    return 2
                time.sleep(0.5)
            except Exception:
                pass
    print(f"\n총 {followed}개 팔로우")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
