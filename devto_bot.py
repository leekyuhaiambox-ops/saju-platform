"""Dev.to (Forem) 자동 게시 봇 — 영문 콘텐츠 시장.

Dev.to API:
- https://dev.to/settings/extensions → API Key 발급 (즉시, 무료)
- POST https://dev.to/api/articles  Authorization: API key

환경변수:
- DEVTO_API_KEY
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
from datetime import date
from pathlib import Path
from urllib import request

API_KEY = os.environ.get("DEVTO_API_KEY", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")

STATE_FILE = Path(os.environ.get(
    "DEVTO_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".devto_state.json"),
))


def _site_en(path=""):
    return f"{SITE_URL}/en{path}"


# Dev.to는 개발/기술 중심 커뮤니티 — 사주 X 코드 스토리텔링 위주로 콘텐츠 작성
POSTS = [
    {
        "title": "Building a Saju (Korean Astrology) Calculator from Scratch in Python",
        "tags": ["python", "webdev", "showdev", "astronomy"],
        "body_markdown": f"""I built a free Korean astrology (Saju) calculator and wanted to share what makes the math interesting.

## What's Saju?

Saju is the Korean tradition of Chinese 4-pillar astrology (BaZi). Your birth year, month, day, and hour each get encoded as a Heavenly Stem + Earthly Branch pair, giving you 8 characters that describe your "energetic signature."

## The interesting parts

### 1. Solar terms via Meeus algorithm

The year boundary isn't January 1 — it's the solar term **Ipchun (立春, ~Feb 4)**, the moment the sun reaches 315° ecliptic longitude. To compute this precisely, I implemented the Meeus astronomical algorithm:

```python
def apparent_solar_longitude(jd):
    t = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360
    m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360)
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    return (l0 + c) % 360
```

Then Newton-style iteration to find the exact JD when longitude crosses 315°.

### 2. Late-Zi hour rule

The day pillar transitions at 23:00 local time, not midnight. If you're born between 23:00 and 24:00, your day pillar rolls forward to the next day. Common bug in online calculators.

### 3. Sixty-pillar cycle (六十甲子)

Ten Heavenly Stems × Twelve Earthly Branches, but they pair only on matching parity (Yang-Yang or Yin-Yin), so you get LCM(10, 12) / 2 = 30 paired combos × 2 polarities = 60 pillars.

```python
def get_pillar_index(stem, branch):
    for i in range(60):
        if i % 10 == stem and i % 12 == branch:
            return i
```

## Try it

[Free Saju reader →]({_site_en()})

No signup, no email. Pure Python on Flask, hosted on PythonAnywhere free tier.

Open to feedback on the math or interpretation logic.
""",
        "canonical_url": _site_en(),
    },
    {
        "title": "Day Master Theory: Why 60 Personality Archetypes Beat 12 Sun Signs",
        "tags": ["personality", "philosophy", "discuss", "showdev"],
        "body_markdown": f"""Coming from Western astrology and curious about Asian systems? The biggest practical shift is resolution.

## Sun signs: 12 archetypes
## Day Pillars: 60 archetypes

In Korean Saju (and Chinese BaZi), your "core type" isn't your sun sign — it's your **Day Pillar**, the Heavenly Stem + Earthly Branch pair of your birth day. With 10 stems × 12 branches × parity-pairing, you get 60 distinct types.

## Examples

A Western Leo could be one of these very different Day Pillars:
- **Bingwu (丙午)** — fire + fire branch = maximum charisma
- **Renxu (壬戌)** — water + earth branch = contemplative depth
- **Jiawu (甲午)** — wood + fire branch = ambitious expressive

Same Sun, three different people.

## How to find yours

Free calculator: {_site_en()}

Enter birth date and time. The site computes your Day Master (stem) and Day Pillar (stem-branch), then shows the archetype reading for that specific combination.

## Why this matters for self-understanding

I'm not arguing Saju "predicts" anything. But as a vocabulary for self-reflection, 60 archetypes give you much more nuanced language than 12.

Same logic that makes MBTI's 16 types more useful than introvert/extravert binary.

What's your Day Pillar? Drop yours below.
""",
        "canonical_url": _site_en("/sixty-pillars"),
    },
    {
        "title": "I Built a Free Korean Astrology Site — Tech Stack and Lessons",
        "tags": ["webdev", "showdev", "python", "flask"],
        "body_markdown": f"""Side project: built a free Korean Saju (4-pillar astrology) calculator. Sharing the tech stack and a few non-obvious gotchas.

## Stack

- **Backend**: Python 3.13, Flask
- **Hosting**: PythonAnywhere free tier
- **Astronomy**: Custom Meeus algorithm (no external library, 100s/day CPU limit)
- **No database**: Charts are pure functions of input

## Live site

[{SITE_URL}/en]({_site_en()})

## Non-obvious lessons

### 1. Free tier CPU is precious

PythonAnywhere free tier gives 100 CPU seconds per day. Each Saju calculation iterates a Newton-style solver for solar term timing. Without caching, ~30 chart computations would burn through the limit.

```python
from functools import lru_cache

@lru_cache(maxsize=4096)
def solar_term_jd(year: int, term_idx: int) -> float:
    # ...
```

Solar terms repeat for the same `(year, term)` pair, so caching is essentially free.

### 2. Korean text on Windows console is hell

Default code page on Windows is cp949. Add `python -X utf8 script.py` or `os.environ["PYTHONIOENCODING"] = "utf-8"` to avoid `UnicodeEncodeError` on every print of Korean characters.

### 3. PythonAnywhere whitelist for outbound HTTPS

Free tier blocks outgoing HTTPS except to whitelisted domains. Plan for this if your app needs to call external APIs.

### 4. i18n the right way

I added `/en/` prefix routing rather than per-template translation logic. Cleaner separation, easier SEO with hreflang.

## What's next

- Multi-language expansion (Japanese, Chinese)
- Service Worker for offline support (done)
- IndexNow integration for instant Bing/Naver indexing (done)

Open to feedback on the math or UX. Try the [chart reader]({_site_en()}) and let me know what's off.
""",
        "canonical_url": SITE_URL,
    },
]


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_indices": [], "last_date": None}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def post_to_devto(post: dict) -> dict:
    if not API_KEY:
        return {"ok": False, "error": "DEVTO_API_KEY missing"}
    article = {
        "article": {
            "title": post["title"],
            "body_markdown": post["body_markdown"],
            "tags": post["tags"],
            "published": True,
            "canonical_url": post.get("canonical_url"),
        }
    }
    body = json.dumps(article).encode("utf-8")
    req = request.Request(
        "https://dev.to/api/articles",
        data=body, method="POST",
        headers={"api-key": API_KEY,
                 "Content-Type": "application/json",
                 "User-Agent": "tarofortune-bot/0.1"},
    )
    try:
        with request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
            return {"ok": True, "url": data.get("url"), "id": data.get("id")}
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode()
            except Exception:
                pass
        return {"ok": False, "error": f"{e}: {b}"}


def run_daily():
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("Already posted today.")
        return

    posted = set(state.get("posted_indices", []))
    available = [i for i in range(len(POSTS)) if i not in posted]
    if not available:
        state["posted_indices"] = []
        available = list(range(len(POSTS)))

    idx = random.choice(available)
    result = post_to_devto(POSTS[idx])
    print(f"[devto] idx={idx} {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted_indices", []).append(idx)
        state["last_date"] = today
        save_state(state)


if __name__ == "__main__":
    run_daily()
