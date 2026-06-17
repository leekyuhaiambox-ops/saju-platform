"""봇 공용 콘텐츠 풀 — 영어권 디스커버리 피드용 일일 포스트 생성기.

day-pillar(사주 일주)와 zodiac(서양 별자리)를 번갈아 게시한다.
별자리 글은 #horoscope #astrology #zodiac 등 대형 해시태그를 달아
팔로워 0인 신규 봇도 디스커버리/태그 피드에서 노출될 확률을 높인다.

bluesky_bot, mastodon_bot 등이 import 해서 사용.
플랫폼별 글자 한도는 limit 인자로 전달.
"""
from __future__ import annotations

from saju.interpreter_en import DAY_PILLAR_INTERPRETATIONS_EN
from saju.horoscope import SIGNS, get_sign_en

try:
    from saju import tarot as _tarot
except Exception:
    _tarot = None

SIGN_SLUGS = [s[0] for s in SIGNS]

SIGN_EMOJI = {
    "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋",
    "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
    "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓",
}

PILLAR_TAGS = ("#Saju #BaZi #ChineseAstrology #KoreanAstrology "
               "#FourPillars #astrology #divination")


def _zodiac_tags(slug: str, element: str) -> str:
    return (f"#horoscope #astrology #zodiac #{slug} "
            f"#{element.lower()}sign #zodiacsigns #dailyhoroscope")


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def pillar_post(site_url: str, idx: int, limit: int = 300) -> str:
    info = DAY_PILLAR_INTERPRETATIONS_EN.get(idx)
    if not info:
        return ""
    name, headline, _detail = info
    url = f"{site_url}/en/sixty-pillars/{idx}"
    text = (f"Day Pillar #{idx + 1:02d}: {name}\n{headline}\n\n"
            f"Free Korean Saju reading → {url}\n\n{PILLAR_TAGS}")
    if len(text) > limit:
        text = f"Day Pillar: {name} — {headline[:70]}\n{url}\n{PILLAR_TAGS}"
    return _clip(text, limit)


def zodiac_post(site_url: str, slug: str, limit: int = 300) -> str:
    s = get_sign_en(slug)
    if not s:
        return ""
    url = f"{site_url}/en/horoscope/{slug}"
    emoji = SIGN_EMOJI.get(slug, "✨")
    blurb = s["personality"].split(". ")[0].rstrip(".") + "."
    best = ", ".join(s.get("best", [])[:2])
    tags = _zodiac_tags(slug, s.get("element", "fire"))
    text = (f"{emoji} {s['name']} ({s['date_range']})\n{blurb}\n"
            f"Best matches: {best}.\n\n"
            f"Full {s['name']} horoscope → {url}\n\n{tags}")
    if len(text) > limit:
        text = f"{emoji} {s['name']}: {blurb}\n{url}\n\n{tags}"
    return _clip(text, limit)


def tarot_post(site_url: str, limit: int = 300) -> str:
    """오늘의 타로 카드 — 영어권 #tarot 디스커버리 피드용. 날짜 결정론적."""
    if _tarot is None:
        return ""
    card, rev = _tarot.daily_card()
    url = f"{site_url}/en/tarot/today"
    ori = "Reversed" if rev else "Upright"
    meaning = (card["rev_en"] if rev else card["up_en"]).split(". ")[0].rstrip(".") + "."
    tags = "#tarot #tarotreading #tarotcards #dailytarot #cartomancy #divination"
    text = (f"🔮 Card of the day: {card['en_name']} ({ori})\n{meaning}\n\n"
            f"Your free daily tarot → {url}\n\n{tags}")
    if len(text) > limit:
        text = f"🔮 {card['en_name']} ({ori})\n{url}\n\n{tags}"
    return _clip(text, limit)


def next_post(site_url: str, state: dict, limit: int = 300):
    """state['count']에 따라 pillar/zodiac/tarot 3종 순환 + 전체 커버.

    반환: (text, kind, key)  — text가 ""이면 게시 스킵.
    """
    count = int(state.get("count", 0))
    cycle = count % 3
    third = count // 3
    if cycle == 1:
        slug = SIGN_SLUGS[third % len(SIGN_SLUGS)]
        return zodiac_post(site_url, slug, limit), "zodiac", slug
    if cycle == 2:
        text = tarot_post(site_url, limit)
        if text:
            return text, "tarot", "today"
        # 타로 불가 시 pillar로 폴백
    idx = third % 60
    return pillar_post(site_url, idx, limit), "pillar", idx
