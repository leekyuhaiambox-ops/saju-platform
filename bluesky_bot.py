"""Bluesky 자동 게시 봇 — AT Protocol 공식 API (순수 urllib).

Bluesky는 봇을 공식 허용. 승인 불필요, 무료, app password 인증.
- https://bsky.app 가입 → Settings → App Passwords → 생성
- 핸들(예: tarofortune.bsky.social) + app password

환경변수:
- BLUESKY_HANDLE (예: tarofortune.bsky.social)
- BLUESKY_APP_PASSWORD (xxxx-xxxx-xxxx-xxxx)
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib import request

HANDLE = os.environ.get("BLUESKY_HANDLE", "")
APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")
PDS = "https://bsky.social"

STATE_FILE = Path(os.environ.get(
    "BLUESKY_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".bluesky_state.json"),
))


def _site_en(path=""):
    return f"{SITE_URL}/en{path}"


# 60갑자 영문 풀이 재사용 (interpreter_en)
try:
    from saju.interpreter_en import DAY_PILLAR_INTERPRETATIONS_EN
except ImportError:
    DAY_PILLAR_INTERPRETATIONS_EN = {}

HASHTAGS = "#Saju #BaZi #ChineseAstrology #Astrology #DayPillar"


def _http(method, url, headers=None, data=None):
    req = request.Request(url, data=data, method=method, headers=headers or {})
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


def login() -> tuple:
    """returns (accessJwt, did)."""
    if not HANDLE or not APP_PASSWORD:
        raise RuntimeError("BLUESKY_HANDLE / BLUESKY_APP_PASSWORD missing")
    body = json.dumps({"identifier": HANDLE, "password": APP_PASSWORD}).encode()
    code, resp = _http("POST", f"{PDS}/xrpc/com.atproto.server.createSession",
                       {"Content-Type": "application/json"}, body)
    if code != 200:
        raise RuntimeError(f"Login failed: {code} {resp}")
    data = json.loads(resp)
    return data["accessJwt"], data["did"]


def _build_facets(text: str) -> list:
    """링크·해시태그를 facet(rich text)으로 변환 — 클릭 가능하게."""
    facets = []
    btext = text.encode("utf-8")
    # URL facets
    for m in re.finditer(r"https?://[^\s]+", text):
        start = len(text[:m.start()].encode("utf-8"))
        end = len(text[:m.end()].encode("utf-8"))
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}],
        })
    # Hashtag facets
    for m in re.finditer(r"#(\w+)", text):
        start = len(text[:m.start()].encode("utf-8"))
        end = len(text[:m.end()].encode("utf-8"))
        facets.append({
            "index": {"byteStart": start, "byteEnd": end},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}],
        })
    return facets


def post(jwt: str, did: str, text: str) -> dict:
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "langs": ["en"],
    }
    facets = _build_facets(text)
    if facets:
        record["facets"] = facets
    body = json.dumps({
        "repo": did, "collection": "app.bsky.feed.post", "record": record,
    }).encode()
    code, resp = _http("POST", f"{PDS}/xrpc/com.atproto.repo.createRecord",
                       {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}, body)
    if code != 200:
        return {"ok": False, "error": f"{code} {resp[:200]}"}
    return {"ok": True, "uri": json.loads(resp).get("uri")}


def compose(idx: int) -> str:
    info = DAY_PILLAR_INTERPRETATIONS_EN.get(idx)
    if not info:
        return ""
    name, headline, _ = info
    # 300자 제한
    text = f"Day Pillar #{idx + 1:02d}: {name}\n{headline}\n\nFree Korean astrology reading → {_site_en()}\n\n{HASHTAGS}"
    if len(text) > 295:
        text = f"Day Pillar: {name} — {headline[:80]}\n{_site_en()}\n{HASHTAGS}"
    return text[:300]


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted": [], "last_date": None}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def run_daily():
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("[bluesky] already posted today")
        return
    try:
        jwt, did = login()
    except Exception as e:
        print(f"[bluesky] login failed: {e}")
        return
    posted = set(state.get("posted", []))
    available = [i for i in range(60) if i not in posted]
    if not available:
        state["posted"] = []
        available = list(range(60))
    idx = random.choice(available)
    text = compose(idx)
    if not text:
        print(f"[bluesky] no content for {idx}")
        return
    result = post(jwt, did, text)
    print(f"[bluesky] idx={idx} {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted", []).append(idx)
        state["last_date"] = today
        save_state(state)


if __name__ == "__main__":
    run_daily()
