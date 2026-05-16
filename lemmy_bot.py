"""Lemmy 자동 게시 봇 — 순수 urllib 기반 (Reddit 봇과 동일한 콘텐츠 풀 재사용).

Lemmy 인증 흐름:
1. POST /api/v3/user/login  { username_or_email, password }  → jwt
2. POST /api/v3/post  { name, body, community_id, auth }  → 게시
3. GET  /api/v3/community  { name, auth }  → community_id 조회

환경변수:
- LEMMY_INSTANCE (예: "lemmy.world", 기본값)
- LEMMY_USERNAME
- LEMMY_PASSWORD
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
import time
from datetime import date
from pathlib import Path
from urllib import request, parse

from reddit_bot import POSTS as REDDIT_POSTS  # 동일 콘텐츠 풀 재사용

LEMMY_INSTANCE = os.environ.get("LEMMY_INSTANCE", "lemmy.world")
USERNAME = os.environ.get("LEMMY_USERNAME", "")
PASSWORD = os.environ.get("LEMMY_PASSWORD", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")

STATE_FILE = Path(os.environ.get(
    "LEMMY_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".lemmy_state.json"),
))

# Reddit 서브레딧 → Lemmy 커뮤니티 매핑 (확장)
SUB_TO_COMMUNITY = {
    "ChineseAstrology": "astrology@lemmy.world",
    "Astrology": "astrology@lemmy.world",
    "AskAstrologers": "astrology@lemmy.world",
    "Divination": "occult@lemmy.world",
    "spirituality": "spirituality@lemmy.world",
}

# 추가 커뮤니티 — 사주는 동아시아 문화 / 자기이해 / 무료 도구 관점에서 노출
EXTRA_COMMUNITIES = [
    "asia@lemmy.world",
    "korea@lemmy.world",
    "AsianBeauty@lemmy.world",
    "selfimprovement@lemmy.world",
    "PersonalityTypes@lemmy.world",
]

USER_AGENT = "tarofortune-bot/0.1"


def _http(method, url, headers=None, data=None):
    req = request.Request(url, data=data, method=method,
                          headers=headers or {})
    try:
        with request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        return getattr(e, "code", 0), f"{e}: {b}"


def login() -> str:
    if not USERNAME or not PASSWORD:
        raise RuntimeError("LEMMY_USERNAME / LEMMY_PASSWORD missing")
    body = json.dumps({
        "username_or_email": USERNAME, "password": PASSWORD,
    }).encode()
    code, resp = _http("POST", f"https://{LEMMY_INSTANCE}/api/v3/user/login",
                       headers={"Content-Type": "application/json",
                                "User-Agent": USER_AGENT},
                       data=body)
    if code != 200:
        raise RuntimeError(f"Login failed: {code} {resp}")
    data = json.loads(resp)
    return data["jwt"]


def find_community_id(jwt: str, community_name: str) -> int | None:
    """community_name = 'astrology@lemmy.world' 형식."""
    code, resp = _http("GET",
                       f"https://{LEMMY_INSTANCE}/api/v3/community?name={parse.quote(community_name)}",
                       headers={"Authorization": f"Bearer {jwt}",
                                "User-Agent": USER_AGENT})
    if code != 200:
        return None
    try:
        return json.loads(resp)["community_view"]["community"]["id"]
    except (KeyError, json.JSONDecodeError):
        return None


def submit_post(jwt: str, community_id: int, title: str, body: str) -> dict:
    payload = json.dumps({
        "auth": jwt, "name": title[:200], "body": body,
        "community_id": community_id,
    }).encode()
    code, resp = _http("POST",
                       f"https://{LEMMY_INSTANCE}/api/v3/post",
                       headers={"Authorization": f"Bearer {jwt}",
                                "Content-Type": "application/json",
                                "User-Agent": USER_AGENT},
                       data=payload)
    if code not in (200, 201):
        return {"ok": False, "error": f"{code} {resp[:200]}"}
    try:
        data = json.loads(resp)
        url = f"https://{LEMMY_INSTANCE}/post/{data['post_view']['post']['id']}"
        return {"ok": True, "url": url}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_indices": [], "last_post_date": None, "post_count": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                          encoding="utf-8")


def run_daily():
    try:
        jwt = login()
    except Exception as e:
        print(f"[error] login failed: {e}")
        return

    state = load_state()
    today = date.today().isoformat()
    if state.get("last_post_date") == today:
        print("Already posted today; exiting.")
        return

    posted = set(state.get("posted_indices", []))
    available = [i for i in range(len(REDDIT_POSTS)) if i not in posted]
    if not available:
        state["posted_indices"] = []
        available = list(range(len(REDDIT_POSTS)))

    # Lemmy 커뮤니티 매핑이 있는 게시물만 선택
    available = [i for i in available
                 if REDDIT_POSTS[i]["subreddit"] in SUB_TO_COMMUNITY]
    if not available:
        print("No available posts mapped to Lemmy communities.")
        return

    idx = random.choice(available)
    post = REDDIT_POSTS[idx]
    community = SUB_TO_COMMUNITY[post["subreddit"]]

    community_id = find_community_id(jwt, community)
    if not community_id:
        print(f"Could not find community {community}")
        return

    result = submit_post(jwt, community_id, post["title"], post["body"])
    print(f"[lemmy_post] {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted_indices", []).append(idx)
        state["last_post_date"] = today
        state["post_count"] = state.get("post_count", 0) + 1
        save_state(state)


if __name__ == "__main__":
    run_daily()
