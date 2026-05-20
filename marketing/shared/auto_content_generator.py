"""
자동 콘텐츠 생성기 — OpenAI 또는 Anthropic Claude API 활용 (dual provider)
=========================================================================

매일 1회 실행 → 사이트별 새 봇 콘텐츠를 자동 생성 → content_pools/*.json에 추가.
정적 풀(현재 5포스트)이 회전 끝나면 새 콘텐츠 자동 보충 = 사람 입력 0.

Provider 자동 선택 로직
-----------------------
1. OPENAI_API_KEY 있으면 → OpenAI (GPT-4o-mini, 가장 저렴)
2. 없고 ANTHROPIC_API_KEY 있으면 → Anthropic (Claude Haiku)
3. 둘 다 없으면 → 에러
4. --provider 인자로 강제 선택 가능

운영자 셋업 (둘 중 하나만 박으면 됨)
------------------------------------
OpenAI:
  1. https://platform.openai.com/api-keys 에서 키 발급
  2. GitHub Secrets에 OPENAI_API_KEY 추가
  3. 로컬엔 .env 에 OPENAI_API_KEY=sk-...

Anthropic:
  1. https://console.anthropic.com 에서 키 발급
  2. GitHub Secrets에 ANTHROPIC_API_KEY 추가
  3. 로컬엔 .env 에 ANTHROPIC_API_KEY=sk-ant-...

실행
----
python auto_content_generator.py                   # 자동 provider 감지
python auto_content_generator.py --provider openai
python auto_content_generator.py --provider anthropic
python auto_content_generator.py --site geoinfomatic
python auto_content_generator.py --dry-run

비용 비교 (사이트당 1콘텐츠 ≈ input 1.5K + output 0.5K 토큰)
---------------------------------------------------------
- OpenAI GPT-4o-mini ($0.15/1M in, $0.60/1M out)  → $0.00053/콘텐츠 ★ 추천
- Anthropic Claude Haiku ($0.25/1M in, $1.25/1M out) → $0.00100/콘텐츠
- 3사이트 매주 운영 시:
    OpenAI    : 월 $0.046 (≈ ₩63)
    Anthropic : 월 $0.090 (≈ ₩125)
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")  # cheap + fast

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")


def _detect_provider(forced: str | None = None) -> str:
    """provider 자동 감지 또는 강제 선택."""
    if forced:
        return forced
    if OPENAI_API_KEY:
        return "openai"
    if ANTHROPIC_API_KEY:
        return "anthropic"
    return ""

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
        "model": ANTHROPIC_MODEL,
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
    blocks = data.get("content", [])
    if blocks and blocks[0].get("type") == "text":
        return blocks[0]["text"]
    return ""


def _call_openai(prompt: str, max_tokens: int = 800) -> str:
    """OpenAI Chat Completions API 호출 → text 반환.

    GPT-4o-mini 기본. JSON 강제는 response_format={"type":"json_object"}로 가능하지만,
    프롬프트가 이미 JSON 출력을 명시하므로 호환성 위해 미적용 (구 모델도 작동).
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY 환경변수 없음")
    payload = {
        "model": OPENAI_MODEL,
        "max_tokens": max_tokens,
        "temperature": 0.85,
        "messages": [
            {"role": "system", "content": "You output STRICTLY valid JSON, no other text. No code fences."},
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        OPENAI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    choices = data.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "") or ""
    return ""


def _call_llm(prompt: str, provider: str, max_tokens: int = 800) -> str:
    """provider에 따라 적절한 LLM 호출."""
    if provider == "openai":
        return _call_openai(prompt, max_tokens)
    elif provider == "anthropic":
        return _call_anthropic(prompt, max_tokens)
    else:
        raise RuntimeError(f"Unknown provider: {provider}")


def _existing_titles(site_key: str) -> list[str]:
    p = POOLS_DIR / f"{site_key}.json"
    if not p.exists():
        return []
    try:
        pool = json.loads(p.read_text(encoding="utf-8"))
        return [item.get("title", "") for item in pool]
    except Exception:
        return []


def generate_for_site(site_key: str, lang: str = "en", provider: str = "openai") -> dict | None:
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
        text = _call_llm(prompt, provider)
    except Exception as e:
        print(f"[{site_key}/{lang}] {provider} API call failed: {e}")
        return None

    # JSON 파싱 (코드 펜스 떼기)
    text = text.strip()
    if text.startswith("```"):
        text = "\n".join(line for line in text.split("\n") if not line.startswith("```"))
    # 일부 모델이 leading prose 붙임 — { 시작점 찾기
    if not text.startswith("{"):
        i = text.find("{")
        if i != -1:
            text = text[i:]
    # trailing prose 제거
    if "}" in text:
        text = text[:text.rfind("}") + 1]

    try:
        item = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[{site_key}/{lang}] JSON parse failed: {e}")
        print(f"   Raw: {text[:300]}")
        return None

    if not all(k in item for k in ("title", "body", "tags")):
        print(f"[{site_key}/{lang}] Missing fields")
        return None
    item["lang"] = lang
    return item


def append_to_pool(site_key: str, item: dict, max_size: int = 60) -> bool:
    """content_pools/<site>.json에 추가. max_size 초과 시 가장 오래된 항목 제거.

    매일 6개씩 누적되면 한 달에 180개까지 부풀 수 있음.
    max_size=60으로 자동 정리 → 약 10일치 풀 유지 (한국어 30 + 영문 30).
    오래된 항목이 먼저 제거되므로 항상 신선한 콘텐츠만 회전.
    """
    p = POOLS_DIR / f"{site_key}.json"
    pool = []
    if p.exists():
        try:
            pool = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pool = []
    pool.append(item)

    # 같은 lang끼리 grouped 잘라내기 — 영문과 한국어 균형 유지
    if len(pool) > max_size:
        per_lang_limit = max_size // 2  # lang당 절반씩
        kept_en = [p for p in pool if p.get("lang") == "en"][-per_lang_limit:]
        kept_kr = [p for p in pool if p.get("lang") == "kr"][-per_lang_limit:]
        # lang 미정 항목은 끝부분만
        kept_other = [p for p in pool if p.get("lang") not in ("en", "kr")][-5:]
        pool = kept_other + kept_en + kept_kr

    p.write_text(json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=list(SITES_CONFIG.keys()))
    ap.add_argument("--lang", default="both", choices=["en", "kr", "both"])
    ap.add_argument("--dry-run", action="store_true", help="생성만, 풀에 추가 안 함")
    ap.add_argument("--provider", choices=["openai", "anthropic"], default=None,
                    help="강제 provider 선택. 비우면 자동(OpenAI 우선).")
    args = ap.parse_args()

    provider = _detect_provider(args.provider)
    if not provider:
        print("⚠️ OPENAI_API_KEY 또는 ANTHROPIC_API_KEY 환경변수가 필요합니다.")
        print("")
        print("OpenAI (추천 — 더 저렴, ₩63/월):")
        print("   1. https://platform.openai.com/api-keys 에서 키 발급")
        print("   2. GitHub Secrets 또는 .env 에 OPENAI_API_KEY=sk-... 추가")
        print("")
        print("Anthropic:")
        print("   1. https://console.anthropic.com 에서 키 발급")
        print("   2. ANTHROPIC_API_KEY=sk-ant-... 추가")
        return 1

    model_name = OPENAI_MODEL if provider == "openai" else ANTHROPIC_MODEL
    print(f"Provider: {provider} ({model_name})")

    sites = [args.site] if args.site else list(SITES_CONFIG.keys())
    langs = ["en", "kr"] if args.lang == "both" else [args.lang]

    results = {}
    for site in sites:
        for lang in langs:
            print(f"\n=== {site} / {lang} ===")
            item = generate_for_site(site, lang, provider)
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
