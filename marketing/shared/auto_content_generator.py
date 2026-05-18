"""
자동 콘텐츠 생성기 — Anthropic Claude API 활용
==============================================

매일 1회 실행 → 사이트별 새 봇 콘텐츠를 자동 생성 → content_pools/*.json에 추가.
정적 풀(현재 5포스트)이 회전 끝나면 새 콘텐츠 자동 보충 = 사람 입력 0.

운영자 필수 셋업
---------------
1. https://console.anthropic.com에서 API 키 발급
2. GitHub Secrets에 ANTHROPIC_API_KEY 추가
3. 로컬에선 .env에 ANTHROPIC_API_KEY=sk-ant-... 추가

실행
----
# 모든 사이트, 사이트당 1개 새 콘텐츠 생성
python auto_content_generator.py

# 특정 사이트만
python auto_content_generator.py --site geoinfomatic

# 드라이런 (생성만, 풀에 추가 안 함)
python auto_content_generator.py --dry-run

GitHub Actions 통합
-------------------
.github/workflows/multi-site-bot.yml에 다음 step 추가:

  - name: Generate new content (weekly)
    if: github.event_name == 'schedule' && contains(github.event.schedule, '0 14 * * 0')
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    run: python -X utf8 marketing/shared/auto_content_generator.py

  - name: Commit new content
    run: |
      git add marketing/shared/content_pools/
      git diff --staged --quiet || git commit -m "chore: auto-generated content"
      git push

비용
----
Claude Haiku ($0.25/1M input, $1.25/1M output)로 생성하면
사이트당 콘텐츠 1개 = 약 1,500 토큰 input + 500 토큰 output = $0.0005
3사이트 매주 = 월 $0.06 (60원)
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"  # Cheap, fast, sufficient

POOLS_DIR = Path(__file__).parent / "content_pools"

SITES_CONFIG = {
    "tarofortune": {
        "name_en": "Saju Astrology",
        "context": "Free Korean four-pillars (saju) astrology calculator. 60 day-pillars, "
                   "five elements, ten gods, twelve life stages. EN + KR interpretations.",
        "url": "https://tarofortune.pythonanywhere.com",
        "tags_en": ["astrology", "korea", "philosophy", "fortunetelling", "showdev"],
        "tags_kr": ["사주", "명리", "운세", "일주", "60갑자"],
    },
    "currency-map": {
        "name_en": "Gyeonggi Currency Map",
        "context": "Interactive PWA mapping 31 Korean cities' local-currency merchants. "
                   "React + Vite + Leaflet + Firebase. Real-time 'open now' filter.",
        "url": "https://gyeonggi-currency-map.web.app",
        "tags_en": ["reactjs", "leaflet", "pwa", "openstreetmap", "showdev"],
        "tags_kr": ["경기지역화폐", "경기페이", "지역화폐", "가맹점", "지도"],
    },
    "geoinfomatic": {
        "name_en": "Living Zone Accessibility",
        "context": "Isochrone-based Korean neighborhood analyzer. Walk or transit, "
                   "10-45 min radius, 8 facility types, AI summary, 100-point score. "
                   "Freemium (9,900 KRW/mo Pro).",
        "url": "https://geoinfomatic.pythonanywhere.com",
        "tags_en": ["gis", "leaflet", "urbanplanning", "flask", "showdev"],
        "tags_kr": ["생활권", "접근성", "이사", "학군", "임장", "부동산"],
    },
}


GEN_PROMPT_TMPL = """You are a marketing content generator for a solo Korean indie developer's projects.

Generate ONE new social media post for the site below, in {lang} ({lang_full}).

Site: {name_en}
URL: {url}
Context: {context}

Requirements:
- Authentic, first-person, no corporate tone
- 300-450 characters (Mastodon-safe length)
- Mention the URL exactly once
- Include 3-5 hashtags at the end
- A specific angle/observation, NOT generic ad copy
- Avoid clichés ("revolutionize", "game-changer", etc.)
- {lang_specific}

Forbidden topics for this post (already covered, don't repeat):
{forbidden}

Output STRICTLY in JSON, no other text:
{{
  "lang": "{lang}",
  "title": "<short headline, 60-80 chars>",
  "body": "<full post body with URL and hashtags>",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
"""


def _call_anthropic(prompt: str, max_tokens: int = 800) -> str:
    """Anthropic Messages API 호출 → text 반환."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수 없음")
    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    # Messages API returns content blocks
    blocks = data.get("content", [])
    if blocks and blocks[0].get("type") == "text":
        return blocks[0]["text"]
    return ""


def _existing_titles(site_key: str) -> list[str]:
    p = POOLS_DIR / f"{site_key}.json"
    if not p.exists():
        return []
    try:
        pool = json.loads(p.read_text(encoding="utf-8"))
        return [item.get("title", "") for item in pool]
    except Exception:
        return []


def generate_for_site(site_key: str, lang: str = "en") -> dict | None:
    """단일 사이트에 대해 새 콘텐츠 1개 생성."""
    cfg = SITES_CONFIG[site_key]
    forbidden = _existing_titles(site_key)
    forbidden_str = "\n".join(f"- {t}" for t in forbidden[-8:]) if forbidden else "(none)"

    if lang == "en":
        lang_full = "English"
        lang_specific = "Style: dev-blog tone, observation-driven. Mention tech stack or design lesson if natural."
    else:
        lang_full = "한국어"
        lang_specific = "Style: 자연스러운 한국어, 광고처럼 보이지 X. 1인칭, 구체적 경험."

    prompt = GEN_PROMPT_TMPL.format(
        lang=lang, lang_full=lang_full,
        name_en=cfg["name_en"], url=cfg["url"], context=cfg["context"],
        forbidden=forbidden_str, lang_specific=lang_specific,
    )

    try:
        text = _call_anthropic(prompt)
    except Exception as e:
        print(f"[{site_key}/{lang}] API call failed: {e}")
        return None

    # JSON 파싱 (코드 펜스 떼기)
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(line for line in text.split("\n") if not line.startswith("```"))
    try:
        item = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[{site_key}/{lang}] JSON parse failed: {e}")
        print(f"   Raw: {text[:300]}")
        return None

    # 기본 필드 확인
    if not all(k in item for k in ("title", "body", "tags")):
        print(f"[{site_key}/{lang}] Missing fields")
        return None
    item["lang"] = lang
    return item


def append_to_pool(site_key: str, item: dict) -> bool:
    """content_pools/<site>.json에 추가."""
    p = POOLS_DIR / f"{site_key}.json"
    pool = []
    if p.exists():
        try:
            pool = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pool = []
    pool.append(item)
    p.write_text(json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=list(SITES_CONFIG.keys()))
    ap.add_argument("--lang", default="both", choices=["en", "kr", "both"])
    ap.add_argument("--dry-run", action="store_true", help="생성만, 풀에 추가 안 함")
    args = ap.parse_args()

    if not ANTHROPIC_API_KEY:
        print("⚠️ ANTHROPIC_API_KEY 환경변수가 없습니다.")
        print("   GitHub Secrets 또는 .env 에 추가 후 다시 실행하세요.")
        print("   키 발급: https://console.anthropic.com")
        return 1

    sites = [args.site] if args.site else list(SITES_CONFIG.keys())
    langs = ["en", "kr"] if args.lang == "both" else [args.lang]

    results = {}
    for site in sites:
        for lang in langs:
            print(f"\n=== {site} / {lang} ===")
            item = generate_for_site(site, lang)
            if not item:
                results[f"{site}/{lang}"] = "FAIL"
                continue
            print(f"   Title: {item['title']}")
            print(f"   Tags:  {item.get('tags')}")
            if args.dry_run:
                print("   (dry-run, not appended)")
            else:
                append_to_pool(site, item)
                print("   ✓ Appended to pool")
            results[f"{site}/{lang}"] = "OK"

    print("\n=== Summary ===")
    for k, v in results.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
