"""Mastodon 자동 게시 봇 — 사이트 콘텐츠를 요약해 매일 1회 게시.

Mastodon API:
- 사용자 액세스 토큰 1개로 작동 (개인 토큰 발급 — 가입 직후 가능)
- POST /api/v1/statuses  Authorization: Bearer <token>

환경변수:
- MASTODON_INSTANCE (예: "mastodon.social")
- MASTODON_ACCESS_TOKEN
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
from datetime import date
from pathlib import Path
from urllib import request, parse

from saju.interpreter_en import DAY_PILLAR_INTERPRETATIONS_EN

INSTANCE = os.environ.get("MASTODON_INSTANCE", "mastodon.social")
TOKEN = os.environ.get("MASTODON_ACCESS_TOKEN", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")

STATE_FILE = Path(os.environ.get(
    "MASTODON_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".mastodon_state.json"),
))


def post_status(text: str, visibility: str = "public") -> dict:
    if not TOKEN:
        return {"ok": False, "error": "MASTODON_ACCESS_TOKEN missing"}
    body = parse.urlencode({"status": text, "visibility": visibility}).encode()
    req = request.Request(f"https://{INSTANCE}/api/v1/statuses",
                          data=body, method="POST",
                          headers={"Authorization": f"Bearer {TOKEN}",
                                   "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return {"ok": True, "url": data.get("url"), "id": data.get("id")}
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        return {"ok": False, "error": f"{e}: {b}"}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_pillars": [], "last_date": None, "count": 0}


def save_state(s: dict):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False),
                          encoding="utf-8")


HASHTAGS = "#Saju #BaZi #ChineseAstrology #KoreanAstrology #FourPillars #DayMaster #Divination"


def compose_pillar_toot(idx: int) -> str:
    info = DAY_PILLAR_INTERPRETATIONS_EN.get(idx)
    if not info:
        return ""
    name, headline, _detail = info
    url = f"{SITE_URL}/en/sixty-pillars/{idx}"
    # Mastodon 글자 한도: 보통 500자
    text = f"Day Pillar #{idx + 1:02d}: {name} — {headline}\n\nFull free reading: {url}\n\n{HASHTAGS}"
    if len(text) > 490:
        text = text[:487] + "..."
    return text


def run_daily():
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("Already posted today; exiting.")
        return

    posted = set(state.get("posted_pillars", []))
    available = [i for i in range(60) if i not in posted]
    if not available:
        state["posted_pillars"] = []
        available = list(range(60))

    idx = random.choice(available)
    text = compose_pillar_toot(idx)
    if not text:
        print(f"Could not compose toot for pillar {idx}")
        return

    result = post_status(text)
    print(f"[mastodon] pillar={idx} {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted_pillars", []).append(idx)
        state["last_date"] = today
        state["count"] = state.get("count", 0) + 1
        save_state(state)


if __name__ == "__main__":
    run_daily()
