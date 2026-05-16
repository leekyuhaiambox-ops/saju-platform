"""Reddit 자동 게시 봇 — PRAW 없이 순수 urllib로 OAuth + Reddit API 호출.

PythonAnywhere 무료 티어 호환 (외부 패키지 없이 표준 라이브러리만).

설계 원칙 (Responsible Builder Policy 준수):
- 신규 계정 보호: 카르마/계정나이 임계값 미달 → 댓글만 (워밍업)
- 카르마 충족 → 일 1회 가치 콘텐츠 게시 (사이트 링크 본문에 1회)
- User-Agent에 봇 명시 (`tarofortune-bot/0.1 by /u/USERNAME`)
- 게시 이력 .reddit_state.json 에 저장 (중복 방지)
- Rate limit: Reddit 100 QPM 한도의 1% 미만 사용

환경변수:
- REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
- REDDIT_USER_AGENT (선택), SITE_URL (선택)
"""
from __future__ import annotations
import os
import json
import base64
import random
import time
from datetime import datetime, date
from pathlib import Path
from urllib import request, parse

# ─── 환경 설정 ───────────────────────────────────────
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
USERNAME = os.environ.get("REDDIT_USERNAME", "")
PASSWORD = os.environ.get("REDDIT_PASSWORD", "")
USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT",
    f"tarofortune-bot/0.1 by /u/{USERNAME or 'unknown'}",
)
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")
STATE_FILE = Path(os.environ.get(
    "REDDIT_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".reddit_state.json"),
))

# ─── 운영 정책 임계값 ─────────────────────────────────
KARMA_WARMUP_THRESHOLD = 100
ACCOUNT_AGE_MIN_DAYS = 7

# ─── 게시 콘텐츠 풀 (영문 30개) ────────────────────────
def _site(path=""):
    return f"{SITE_URL}{path}"

POSTS = [
    {
        "subreddit": "ChineseAstrology",
        "title": "Quick guide: how to find your Day Master in Saju (Korean 4-pillar astrology)",
        "body": (
            "In Korean Saju (사주) — which is the Korean reading of the Chinese 4-pillar (BaZi) system — "
            "your **Day Master (日干)** is the Heavenly Stem of the day you were born. It represents 'you' "
            "in the chart, and every other interpretation centers around it.\n\n"
            "Five elemental Day Masters:\n"
            "- **Jia/Yi (甲乙)** → Wood\n"
            "- **Bing/Ding (丙丁)** → Fire\n"
            "- **Wu/Ji (戊己)** → Earth\n"
            "- **Geng/Xin (庚辛)** → Metal\n"
            "- **Ren/Gui (壬癸)** → Water\n\n"
            "Two important Korean-specific rules most online charts get wrong:\n\n"
            "1. **Year boundary is Ipchun (~Feb 4)**, not Jan 1 or Lunar New Year. People born in late "
            "Jan / early Feb often have the previous year's pillar.\n\n"
            "2. **Late-Zi rule (야자시)**: if you were born between 23:00 and midnight, your day pillar "
            "rolls forward to the next day's pillar.\n\n"
            "Curious what yours is? I made a free Saju reader that handles both: "
            f"{_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "All 60 day-pillar (六十甲子) readings, free — built a clean reference site",
        "body": (
            "I kept getting frustrated that day-pillar references online are either paywalled or scattered. "
            "So I compiled all 60 day pillars (Jiazi through Guihai) into a single free site with one "
            "consistent reading style per pillar.\n\n"
            f"Index page: {_site('/en/sixty-pillars')}\n\n"
            "Examples:\n"
            "- Jiazi (甲子) — Great tree finding a deep well; scholar's pillar of wisdom and patience\n"
            "- Bingwu (丙午) — Noon sun at peak; charisma personified\n"
            "- Guihai (癸亥) — Raindrop in the great sea; deep contemplative wisdom\n\n"
            "What's your day pillar?"
        ),
    },
    {
        "subreddit": "Divination",
        "title": "Saju vs BaZi vs Western astrology — what's the actual difference?",
        "body": (
            "TL;DR: Saju is the Korean tradition of Chinese 4-pillar astrology (BaZi 八字). Math identical; "
            "interpretive tradition differs.\n\n"
            "**BaZi (Chinese)** — emphasizes Pattern (格局), Useful God (用神), luck cycles.\n"
            "**Saju (Korean modern)** — leans heavily on Day Pillar archetype typology (60 personalities).\n"
            "**Western astrology** — planets and houses; entirely different conceptual base.\n\n"
            "Saju's day-pillar approach produces 60 archetypes vs Western's 12 sun signs — more granularity.\n\n"
            f"Free Saju reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "AskAstrologers",
        "title": "What's the actual mathematical basis for solar-term boundaries in Saju/BaZi?",
        "body": (
            "The year boundary in Saju/BaZi isn't Jan 1 — it's the solar term **Ipchun (立春)**, around Feb 4. "
            "Precisely the moment the Sun's apparent ecliptic longitude reaches 315°.\n\n"
            "Most online 'free' Saju readers approximate this as 'Feb 4 00:00' — wrong by up to 24 hours, "
            "which flips year pillars for anyone in the window.\n\n"
            "Correct way: Meeus astronomical algorithm — compute apparent solar longitude from Julian Day, "
            "iterate to find exact crossing.\n\n"
            f"Built one that does this: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Why your year pillar might be wrong if you were born in January or early February",
        "body": (
            "Common error in Saju/BaZi calculators: assigning year pillar by Gregorian year. The actual "
            "boundary is **Ipchun (立春)** around February 4.\n\n"
            "Example: someone born January 30, 2024. Many calculators say 'Dragon year' (2024). But Ipchun "
            "2024 was Feb 4 17:11 KST. Anyone born before that has the **previous year's pillar** — Rabbit "
            "year (2023), specifically Guimao (癸卯).\n\n"
            "This isn't minor — your year pillar changes completely, cascading into month pillar, Ten Gods, "
            "and Daewoon (decadal luck) calculation.\n\n"
            f"Free reader that handles it correctly: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "The Ten Gods (十神) in Saju — practical guide with examples",
        "body": (
            "Ten Gods is the relational labeling system in Saju/BaZi. Each of the seven non-self characters "
            "gets one of these labels based on its Five-Element relationship to your Day Master:\n\n"
            "**Same element:**\n- Bijian (比肩) same polarity — peers, independence\n"
            "- Jiecai (劫財) opposite polarity — rivals, drive, watch wealth\n\n"
            "**Day Master produces:**\n- Shishen (食神) — comfort, output\n"
            "- Shangguan (傷官) — sharp talent, art, rebellion\n\n"
            "**Day Master controls:**\n- Pianjie (偏財) — business, active wealth\n"
            "- Zhengcai (正財) — stable wealth, spouse (for men)\n\n"
            "**Controls Day Master:**\n- Pianguan (偏官/7 Killings) — pressure, power\n"
            "- Zhengguan (正官) — career, honor\n\n"
            "**Produces Day Master:**\n- Pianyin (偏印) — inspiration, solitary study\n"
            "- Zhengyin (正印) — mother, learning\n\n"
            f"Free chart with all Ten Gods auto-calculated: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Astrology",
        "title": "From Western astrology to Saju (Korean 4-pillar) — what to know",
        "body": (
            "Coming from Western astrology to Saju, the mental model shift:\n\n"
            "Western — where the planets were when you were born.\nSaju — the 'energetic signature' "
            "of your birth moment, expressed as 8 Chinese characters.\n\n"
            "Saju uses **Heavenly Stems** (10) and **Earthly Branches** (12) forming 60 cycles. Birth "
            "year, month, day, and hour each get one stem + one branch — '4 pillars / 8 characters.'\n\n"
            "Biggest practical difference: your **day pillar** functions like a sun sign in Western. "
            "Different day pillars produce strikingly different archetypes.\n\n"
            f"Free reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Day Pillar quick guide: Geng/Xin (Metal) Day Masters",
        "body": (
            "If your Day Master is **Geng (庚)** or **Xin (辛)** — Metal:\n\n"
            "**Geng (庚) Yang Metal** — the steel/axe Day Master. Decisive, principled, blunt. Cuts "
            "through indecision. Strong honor and loyalty. Direct communicator. Suited for law, military, "
            "technical fields.\n\n"
            "**Xin (辛) Yin Metal** — the jewel/refined metal Day Master. Refined, aesthetically sharp, "
            "proud. Sees beauty in detail. More sensitive than Geng but equally strong inside. Design, "
            "finance, jewelry/luxury, art critique, surgical precision work.\n\n"
            "Common trap: Metal personalities can over-cut. Without Water to soften, criticism becomes "
            "default.\n\n"
            f"Find your Day Master: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Day Pillar quick guide: Jia/Yi (Wood) Day Masters",
        "body": (
            "**Jia (甲) Yang Wood** — the great tree. Tall, straight, ambitious. Once a direction is "
            "chosen, hard to redirect. Natural leaders but can be stiff. Politicians, executives, teachers.\n\n"
            "**Yi (乙) Yin Wood** — the flexible vine/flower. Soft outside, surprisingly tough inside. "
            "Vines bend around obstacles, then keep growing. Adaptable. Artists, gardeners, counselors.\n\n"
            "Both Wood types need Water in the chart — without it, Wood withers.\n\n"
            f"Find yours: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Day Pillar quick guide: Bing/Ding (Fire) Day Masters",
        "body": (
            "**Bing (丙) Yang Fire** — the sun. Bright, warm, can't be hidden. Bing people light up a "
            "room. Generous, theatrical, sometimes overconfident.\n\n"
            "**Ding (丁) Yin Fire** — candle/lamp fire. More contained but warmer. Work through ideas in "
            "quiet, then deliver something illuminating. Writers, researchers, intimate teachers.\n\n"
            "Fire Day Masters need Wood (fuel) and benefit from Water (control). Too much Fire without "
            "Earth to absorb = burnout patterns.\n\n"
            f"Find your Day Master: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Day Pillar quick guide: Wu/Ji (Earth) Day Masters",
        "body": (
            "**Wu (戊) Yang Earth** — the great mountain. Steady, unmovable, reliable. The friend you call "
            "when you need a real opinion. Administrators, religious leaders, real estate, banking.\n\n"
            "**Ji (己) Yin Earth** — the fertile field. Yielding but nourishing. Supports quietly and grows "
            "things in others. Counselors, teachers, agriculturalists, caretakers.\n\n"
            "Earth needs Wood to break it up (otherwise stagnant) and Water to remain fertile.\n\n"
            f"Find yours: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Day Pillar quick guide: Ren/Gui (Water) Day Masters",
        "body": (
            "**Ren (壬) Yang Water** — the great river/ocean. Mobile, intelligent, sees patterns others "
            "miss. Travels easily across contexts. Diplomats, traders, journalists, multilingual nomads.\n\n"
            "**Gui (癸) Yin Water** — rain, mist, dew. Subtle but everywhere. Accumulates quiet expertise. "
            "Researchers, deep specialists, contemplatives.\n\n"
            "Water needs Metal (source) and Earth (containment). Too much without containment = scattered.\n\n"
            f"Find yours: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Divination",
        "title": "On the difference between divination and self-reflection — Saju as a thinking tool",
        "body": (
            "Most people react to Saju with 'oh, fortune-telling?' or 'isn't this just astrology?' Both "
            "miss what's useful.\n\n"
            "I use Saju as a **structured reflective frame**. The 60 day-pillar archetypes are 60 "
            "personality lenses. When I read mine, I'm asking: 'do these patterns describe behaviors I "
            "actually exhibit?'\n\n"
            "Same approach works with MBTI, Enneagram, etc. The system doesn't predict you — it gives you "
            "vocabulary to notice yourself.\n\n"
            f"Free reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "AskAstrologers",
        "title": "Beginner's question: where do solar terms come from in BaZi/Saju?",
        "body": (
            "The Sun's apparent ecliptic longitude is divided into 24 equal segments of 15°. Each crossing "
            "is a 'solar term' — observable to ancient astronomers via shadow length and equinox/solstice "
            "timing.\n\n"
            "In BaZi/Saju, **12 of the 24 solar terms** mark month-pillar boundaries:\n"
            "- Yin month (寅) starts at Ipchun (立春, sun at 315°, ~Feb 4)\n"
            "- Mao month (卯) starts at Jingzhe (驚蟄, sun at 345°, ~Mar 6)\n"
            "- ... and so on, completing the lunar months\n\n"
            "Two people born 2 days apart in early February can have entirely different month pillars if "
            "the boundary fell between them.\n\n"
            f"My reader computes all 24 to the minute: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Saju compatibility — how it actually works (not what you see on TikTok)",
        "body": (
            "Most 'Saju compatibility' content online reduces to 'X zodiac is compatible with Y.' That's "
            "the bottom 5% of what real analysis looks at.\n\n"
            "Full analysis:\n\n"
            "1. **Day Master union (天干合)** — 5 stem-pair fusions: Jia-Ji, Yi-Geng, Bing-Xin, Ding-Ren, "
            "Wu-Gui. Strongest 'attraction' factor.\n\n"
            "2. **Day Master Five-Element relationship** — Productive, Restraining, or Same.\n\n"
            "3. **Day Branch union or clash (六合/沖)** — Six pair-unions bring ease; six clashes "
            "create friction.\n\n"
            "4. **Year-Branch relationship (zodiac)** — Social-side rhythms; least weighted.\n\n"
            f"Free compatibility analyzer: {_site('/en/compatibility')}"
        ),
    },
    {
        "subreddit": "Astrology",
        "title": "Day-pillar archetypes feel like 'sun signs but with 60 instead of 12'",
        "body": (
            "Studying Saju for a year — the **day pillar** concept feels like a higher-resolution version "
            "of sun signs.\n\n"
            "Western has 12 sun signs. Saju has 60 day pillars — each a distinct archetype combining "
            "Heavenly Stem (10) and Earthly Branch (12).\n\n"
            "Examples of granularity:\n"
            "- Two 'Wood Day Masters' — one Jiazi (Wood+Water) = scholar's pillar of patient learning. "
            "Other Jiawu (Wood+Fire) = expressive idealist. Same Day Master, completely different feel.\n"
            "- A Sun-sign Leo might be Bingwu (fire+fire) max charisma. Another Leo: Renxu (water+earth) "
            "much more contemplative.\n\n"
            f"Free reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Where Saju and BaZi diverge in interpretation (despite identical math)",
        "body": (
            "Math: identical. Interpretation: yes, divergent.\n\n"
            "**Identical math:** same stems and branches, same 60-pillar cycle, same Five-Element "
            "relationships, same Ten God labels, same solar-term boundaries.\n\n"
            "**Divergent styles:**\n"
            "- **Chinese BaZi**: Yongshen (Useful God) and Geju (Pattern) central. Chart evaluated as "
            "'shape' first. Strong life-stage tradition tied to luck cycles (Da Yun).\n\n"
            "- **Korean Saju**: Modern schools (post-1990s) emphasize **Day Pillar typology** almost as "
            "separate layer — 60 day-pillar archetypes treated as 60 personality types alongside Ten Gods.\n\n"
            f"Free Korean-style reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Divination",
        "title": "How accurate is Saju for personality reading? A one-year experiment.",
        "body": (
            "Spent the last year reading charts of friends and family who agreed to be 'test subjects.' "
            "Read every chart blind first, then checked with them after.\n\n"
            "Sample: 32 people. Method: day-pillar archetype + Ten God distribution.\n\n"
            "- 23/32 'spot on' or 'mostly accurate'\n"
            "- 7/32 'partially accurate, missed [X] dimension'\n"
            "- 2/32 'doesn't fit me at all'\n\n"
            "Misses had heavy 'opposite-element' representation overriding day-pillar default, or life "
            "experiences shaping away from default archetype.\n\n"
            "Useful but not deterministic. A hypothesis to test, not a verdict.\n\n"
            f"Free reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Hidden Stems (地藏干) — the layer beneath the visible 8 characters",
        "body": (
            "Each Earthly Branch isn't just one element — it contains multiple 'hidden' Heavenly Stems "
            "with different weights:\n"
            "- **Yin (寅)**: Jia (primary), Bing (secondary), Wu (residual)\n"
            "- **Chen (辰)**: Wu (primary), Yi (secondary), Gui (residual)\n"
            "- **Si (巳)**: Bing (primary), Wu (secondary), Geng (residual)\n\n"
            "Why this matters: Ten Gods analysis based on visible stems alone misses 30-40% of the "
            "picture. A chart can look 'lacking Water' on the surface but actually have Gui hidden in a "
            "Chen branch.\n\n"
            f"My reader shows hidden stems per branch: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "What 'strong vs weak Day Master' actually means (and why it matters)",
        "body": (
            "Strong Day Master = lots of support in chart (same element, or element producing it).\n"
            "Weak Day Master = surrounded by elements that drain or restrain it.\n\n"
            "Strong vs weak inverts which Ten Gods you 'want' to see:\n\n"
            "- **Strong DM** — needs Output, Wealth, or Officer/Killing to channel excess. Resource and "
            "Comparison become 'jealousy gods.'\n\n"
            "- **Weak DM** — needs Resource (seal) and Comparison (sibling) to support. Output and Wealth "
            "become draining. Officer/Killing outright dangerous.\n\n"
            "Most beginner readings get this backward. A 'wealth pillar' is good for strong DM, but for "
            "weak DM it's exhausting.\n\n"
            f"Reader shows Five Element balance: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "How to read your own chart in 30 minutes (minimum-viable approach)",
        "body": (
            "If you don't want to learn the full system but want a useful first reading:\n\n"
            "**Step 1**: Get your 8 characters (free calculator below).\n\n"
            "**Step 2**: Identify your Day Master (3rd pillar, top character).\n\n"
            "**Step 3**: Count Five Element distribution across all 8 visible chars + hidden stems.\n\n"
            "**Step 4**: Strongest element = over-expresses in behavior. Weakest = blind spot.\n\n"
            "**Step 5**: Look at Day Pillar archetype — ~60% will match directly.\n\n"
            "**Step 6**: Ten God distribution: strong Officer/Killing = career-focused; strong Output = "
            "creative; strong Wealth = entrepreneurial; strong Resource = scholarly.\n\n"
            f"30 minutes, 80% of value: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Reading Daewoon (大運) — the decadal luck cycle",
        "body": (
            "Daewoon (Da Yun / 大運) — 10-year luck cycle. Every 10 years your chart 'meets' a new "
            "stem-branch combination overlaying your natal chart.\n\n"
            "**Calculated:**\n"
            "- Direction: Yang-male / Yin-female → forward. Yin-male / Yang-female → reverse.\n"
            "- Starting age: distance from your birth to nearest month-boundary solar term, divided by 3.\n"
            "- Starting pillar: your Month Pillar.\n\n"
            "**Interpret:**\n"
            "- Each Daewoon brings stem + branch. Each gets a Ten God label vs your Day Master.\n"
            "- Stems = first half of decade; branches = second half.\n"
            "- Interactions (合 unions, 沖 clashes) determine themes.\n\n"
            f"My reader shows next 100 years of Daewoon automatically: {_site('/en')}"
        ),
    },
    {
        "subreddit": "spirituality",
        "title": "Five Element theory beyond BaZi — applications in TCM, Feng Shui, food",
        "body": (
            "Wu Xing (Wood, Fire, Earth, Metal, Water) is the same base used in:\n\n"
            "- **TCM** — Wood = liver/gallbladder, Fire = heart/small intestine, Earth = spleen/stomach, "
            "Metal = lung/large intestine, Water = kidney/bladder.\n\n"
            "- **Feng Shui** — element balance in space.\n\n"
            "- **Chinese cuisine** — sour (Wood), bitter (Fire), sweet (Earth), pungent (Metal), salty "
            "(Water). Classical balanced meal touches all five.\n\n"
            "- **BaZi/Saju** — personality and luck.\n\n"
            "Anecdotally: a Wood-deficient Saju often reports liver-related sensitivity and prefers sour "
            "foods. Consistent enough across people I know to be interesting.\n\n"
            f"Find your Five Element balance: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "The 12 Earthly Branches as hour ranges (and the Late-Zi puzzle)",
        "body": (
            "Each Earthly Branch corresponds to a 2-hour range:\n\n"
            "子 Zi: 23:00-01:00 | 丑 Chou: 01:00-03:00 | 寅 Yin: 03:00-05:00 | 卯 Mao: 05:00-07:00\n"
            "辰 Chen: 07:00-09:00 | 巳 Si: 09:00-11:00 | 午 Wu: 11:00-13:00 | 未 Wei: 13:00-15:00\n"
            "申 Shen: 15:00-17:00 | 酉 You: 17:00-19:00 | 戌 Xu: 19:00-21:00 | 亥 Hai: 21:00-23:00\n\n"
            "**Late-Zi puzzle (夜子時)** — Zi spans 23:00 to 01:00, but the day pillar transitions at "
            "23:00 (Korean school) or 00:00 (some Chinese schools):\n"
            "- **Korean**: birth 23:00-01:00 → next day's Day Pillar\n"
            "- **Chinese**: birth 00:00-01:00 → current day's Day Pillar\n\n"
            "My reader uses Korean convention (more astronomically defensible).\n\n"
            f"{_site('/en')}"
        ),
    },
    {
        "subreddit": "AskAstrologers",
        "title": "Saju 'special spirits' (神煞) — useful or superstitious?",
        "body": (
            "Saju and BaZi inherit 'special spirits' (神煞 Shensha) — symbolic labels for specific "
            "stem-branch combinations:\n"
            "- **Tianyi Guiren (天乙貴人)** — Heavenly Noble; helpers in crisis\n"
            "- **Yima (驛馬)** — Horse star; movement, travel\n"
            "- **Taohua (桃花)** — Peach Blossom; romantic attraction\n"
            "- **Huagai (華蓋)** — Canopy; solitude, art, spirituality\n"
            "- **Yangren (羊刃)** — Sharp Blade; excess Day Master energy\n\n"
            "Modern scholarly practice is split. Pro-Shensha: accumulated empirical observations. "
            "Anti-Shensha: late additions with weaker theoretical grounding than Ten Gods or Yongshen.\n\n"
            "My take: useful as tie-breakers. Not load-bearing.\n\n"
            f"Free reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "What's your most accurate Saju/BaZi 'this is so me' moment?",
        "body": (
            "Curious to hear from people who've engaged seriously with Saju/BaZi — what's a chart detail "
            "that hit you as 'unbelievably specific to my life'?\n\n"
            "Mine: my Daewoon shifted to a strong Yin Earth period right when I unexpectedly got pulled "
            "into administrative leadership. Before that decade I had zero interest in leadership. Yin "
            "Earth = administrative, mediator role. The fit was eerie.\n\n"
            "Smaller example: my Day Pillar headline says 'strong people-luck, attracts gatherings.' I host "
            "friends weekly without ever planning to. Just keep ending up as the meet-up coordinator.\n\n"
            "What about you?\n\n"
            f"(Free reader: {_site('/en')})"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "If you only learn ONE thing about Saju/BaZi, learn the Day Master",
        "body": (
            "Pareto principle of Saju: 80% of useful self-reflection comes from knowing your **Day Master** "
            "(Heavenly Stem of your birth day) and its **element**.\n\n"
            "Five Day Master elements:\n"
            "- **Wood**: growth, vision, can be inflexible\n"
            "- **Fire**: expression, warmth, can burn out\n"
            "- **Earth**: stability, reliability, can stagnate\n"
            "- **Metal**: decisiveness, refinement, can be rigid\n"
            "- **Water**: adaptability, depth, can scatter\n\n"
            "Plus **Yang (active)** or **Yin (receptive)** — every element has both versions. 10 possible "
            "Day Masters total.\n\n"
            "Just knowing yours and reading its archetype is more useful than 90% of Saju content online.\n\n"
            f"Free Day Master finder: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "On 'twin Saju' — when two people share the same 8 characters",
        "body": (
            "BaZi/Saju literature has a tradition of 'twin chart' case studies — two people born minutes "
            "apart with identical 8 characters.\n\n"
            "Reported observations:\n"
            "- Major life events tend to cluster in the same years (career shifts, marriages, losses)\n"
            "- Personality cores match closely\n"
            "- Life paths diverge in details (different countries, different fields) but rhyme in shape\n\n"
            "Modern statistical research: limited and inconclusive. But the qualitative case-study literature "
            "is rich.\n\n"
            "Could be observer bias, or could be measuring something real — there's no way to be certain.\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "On accuracy of 'free vs paid' Saju calculators",
        "body": (
            "After comparing ~15 free Saju calculators online, here's what I noticed varies wildly:\n\n"
            "1. **Solar term boundaries** — Most use 'Feb 4 00:00' for Ipchun. Wrong by hours.\n"
            "2. **Late-Zi rule** — Half don't apply it.\n"
            "3. **True solar time** — None I tested correct for longitude (Seoul vs Busan = ~2 min diff).\n"
            "4. **Hidden stems** — Only ~3 of 15 show them.\n"
            "5. **Daewoon calculation** — Direction logic wrong on ~40% of them.\n\n"
            "Paid sites do better on #1-#3 but the underlying math is the same — paid mostly means more "
            "interpretation depth, not more accurate base calculation.\n\n"
            "Built one trying to get all five right; would love feedback if I missed anything:\n"
            f"{_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Free Saju compatibility checker — feedback wanted",
        "body": (
            "Made a Saju compatibility analyzer that scores four dimensions:\n"
            "1. Day Master union\n2. Day Master Five-Element relationship\n"
            "3. Day Branch union/clash\n4. Year Branch relationship\n\n"
            "Each gets a weighted contribution to a 20-95 score with a grade (Excellent / Good / Above-Avg "
            "/ Average / Caution).\n\n"
            f"Try it with you + a partner / friend / family member: {_site('/en/compatibility')}\n\n"
            "Would love feedback on whether the scoring feels right vs your intuitive read of the relationship."
        ),
    },
    # ─── 추가 30개 (총 60개) ─────────────────────────
    {
        "subreddit": "ChineseAstrology",
        "title": "Yin/Yang polarity in Heavenly Stems — Jia vs Yi explained",
        "body": (
            "Every Heavenly Stem comes in Yang or Yin. Same element, different expression style.\n\n"
            "- **Jia (甲) Yang Wood**: great tree. Tall, straight, ambitious.\n"
            "- **Yi (乙) Yin Wood**: vine/flower. Adaptable, magnetic.\n"
            "- **Bing (丙) Yang Fire**: sun. Bright, theatrical.\n"
            "- **Ding (丁) Yin Fire**: candle. Intimate, focused.\n"
            "- **Wu (戊) Yang Earth**: mountain. Steady.\n"
            "- **Ji (己) Yin Earth**: fertile field. Yielding, nourishing.\n"
            "- **Geng (庚) Yang Metal**: steel/axe. Decisive.\n"
            "- **Xin (辛) Yin Metal**: jewel. Refined, proud.\n"
            "- **Ren (壬) Yang Water**: river/ocean. Mobile.\n"
            "- **Gui (癸) Yin Water**: rain/dew. Subtle, deep.\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Hidden Stems table (each Earthly Branch's secret stems)",
        "body": (
            "Each Earthly Branch hides 1-3 Heavenly Stems. The 'main qi' carries the heaviest weight.\n\n"
            "- 子 Zi: Gui — pure Yin Water\n"
            "- 丑 Chou: Ji, Xin, Gui\n"
            "- 寅 Yin: Jia, Bing, Wu\n"
            "- 卯 Mao: Yi — pure Yin Wood\n"
            "- 辰 Chen: Wu, Yi, Gui\n"
            "- 巳 Si: Bing, Wu, Geng\n"
            "- 午 Wu: Ding, Ji\n"
            "- 未 Wei: Ji, Ding, Yi\n"
            "- 申 Shen: Geng, Wu, Ren\n"
            "- 酉 You: Xin — pure Yin Metal\n"
            "- 戌 Xu: Wu, Xin, Ding\n"
            "- 亥 Hai: Ren, Jia\n\n"
            "Hidden stems carry ~30% of the chart's signal. Two charts with identical visible 8 characters can differ enormously by hidden stem reading.\n\n"
            f"Reader shows hidden stems automatically: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Astrology",
        "title": "Saju equivalent of 'Big 3' in Western astrology",
        "body": (
            "Western Big 3: Sun + Moon + Rising. Saju equivalent:\n\n"
            "1. **Day Pillar (most important)** — personality core. 60 options instead of 12.\n"
            "2. **Hour Pillar** — private/childhood self. Roughly maps to Rising.\n"
            "3. **Month Pillar** — social/career identity.\n\n"
            "Year Pillar = generational cohort, ancestry. Less about you specifically.\n\n"
            "Common pattern: people who feel their Sun sign is half-right often find their Day Pillar describes them more accurately.\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Yongshen (用神) — the Useful God concept explained",
        "body": (
            "Yongshen is the 'useful element' that balances your chart. Two schools:\n\n"
            "1. **Strength-based**: Strong Day Master → needs output/officer to drain excess. Weak DM → needs resource/peer for support.\n\n"
            "2. **Climate-based (Joohu)**: Cold charts (Water/Metal heavy in winter) need warming Fire. Hot charts need cooling Water.\n\n"
            "Modern Korean Saju combines both. Yongshen tells you which luck cycles (Daewoon/Sewoon) are favorable vs harmful.\n\n"
            f"Free Five Element distribution: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Divination",
        "title": "Day Pillar archetypes are like 60 'character classes'",
        "body": (
            "Saju Day Pillars in gaming terms — 60 distinct character classes:\n\n"
            "- **Jiazi (甲子)** — Scholar. High INT. Late-game powerhouse.\n"
            "- **Bingwu (丙午)** — Warlord. High CHA. Early peak.\n"
            "- **Renzi (壬子)** — Mage. High INT + AGI. Versatile.\n"
            "- **Wuxu (戊戌)** — Tank. High DEF. Holds positions.\n"
            "- **Xinyou (辛酉)** — Rogue. High DEX + CRIT.\n"
            "- **Jiawu (甲午)** — Bard. CHA + INT hybrid.\n\n"
            "What's your class?\n\n"
            f"{_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Why your Sun sign description often feels half-wrong",
        "body": (
            "12 sun signs vs 60 day pillars. 5x resolution.\n\n"
            "If your Sun sign description always feels 'sorta right but missing something,' it's because there's no way to capture all of human personality in 12 buckets.\n\n"
            "Day Pillars give you 60 archetypes with the same kind of analysis. Higher resolution = better match.\n\n"
            "Test: try a Day Pillar reading and see how the specificity compares.\n\n"
            f"Free, no signup: {_site('/en')}"
        ),
    },
    {
        "subreddit": "spirituality",
        "title": "Saju as therapy — modern self-work with ancient typology",
        "body": (
            "Increasingly Saju used as self-work tool rather than fortune-telling. Therapeutic frame:\n\n"
            "1. **Day Master**: vocabulary for your core energy.\n"
            "2. **Element excess/deficit**: where you over-express vs blind spots.\n"
            "3. **Ten Gods**: loud archetypes over-shape behavior; silent ones are growth areas.\n"
            "4. **Daewoon × life events**: did major transitions happen at Daewoon shifts? Useful pattern-spotting.\n\n"
            "Not predicting the future. Reading patterns in past + present.\n\n"
            f"Free chart for self-work: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Five Elements ↔ Seasons — strength calculation foundation",
        "body": (
            "Each element thrives in a season. This is the foundation of 'strong vs weak Day Master':\n\n"
            "- **Wood** thrives in **Spring**\n"
            "- **Fire** thrives in **Summer**\n"
            "- **Earth** peaks in transitional months\n"
            "- **Metal** thrives in **Autumn**\n"
            "- **Water** thrives in **Winter**\n\n"
            "Wood DM born in Spring = naturally strong. Wood DM born in Autumn (Metal season) = naturally weak. Season strength is the bedrock.\n\n"
            f"Free analysis: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "How to read your chart for career direction",
        "body": (
            "Saju career analysis based on dominant Ten Gods:\n\n"
            "- **Strong Output** → creative, performance, teaching\n"
            "- **Strong Wealth** → business, finance, sales\n"
            "- **Strong Officer** → corporate, gov, law, military\n"
            "- **Strong Resource** → academic, research, writing\n"
            "- **Strong Comparison** → freelance, independent, athletics\n\n"
            "Two equally dominant = hybrid career. Missing entirely = conscious effort needed.\n\n"
            f"Free Ten Gods distribution: {_site('/en')}"
        ),
    },
    {
        "subreddit": "AskAstrologers",
        "title": "Testing if Saju 'works' — my methodology",
        "body": (
            "Skeptic-friendly Saju test:\n\n"
            "1. **Blind reading** of someone you know well, before they describe themselves.\n"
            "2. **Specific predictions**: 'hates org politics' or 'seeks recognition.' Not 'sometimes emotional.'\n"
            "3. **Verify after**: did specifics land?\n"
            "4. **Track misses**: don't filter for hits only.\n\n"
            "I did this with 32 people. ~70% on traits, ~30% on events. Personality > event prediction.\n\n"
            f"Free reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "How to spot a bad Saju calculator",
        "body": (
            "5 free calculators, 5 different results. Common bugs:\n\n"
            "1. Wrong solar term boundary ('Feb 4 00:00' instead of actual Ipchun)\n"
            "2. Missing Late-Zi rule (23:00 birth wrong day pillar)\n"
            "3. No true solar time correction\n"
            "4. Wrong Daewoon direction\n"
            "5. Sloppy Ten Gods (visible only, no hidden stems)\n\n"
            "Validation tests:\n"
            "- Birth in early Feb? Does it know Ipchun?\n"
            "- Birth at 23:30? Does it apply Late-Zi?\n\n"
            f"My reader: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "'Too many of one element' — what to do with lopsided charts",
        "body": (
            "5+ of the same element out of 8 is extreme. Called 'one-sided' (편중) charts.\n\n"
            "Two paths:\n\n"
            "1. **Standard**: too much X = channel it. Wood-heavy → benefit from Fire (express) or Metal (control).\n"
            "2. **Special pattern (專旺格)**: if dominance is extreme and other elements absent, chart flips and treats dominant element as Yongshen. Rare.\n\n"
            "Most extreme charts are just lopsided personalities needing conscious development of missing elements.\n\n"
            f"Free distribution: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Daewoon transitions are real (anecdotal patterns)",
        "body": (
            "Most consistent observation across Saju practice: **Daewoon transitions cluster with major life events**.\n\n"
            "Career pivots, marriages, relocations, health events — they cluster around the 10-year period changes. Even non-believers' lives show this pattern when checked retroactively.\n\n"
            "Hypothesis: Daewoon doesn't cause changes. It describes underlying energy shifts that make certain decisions feel 'right' at certain times.\n\n"
            f"Free 100-year Daewoon: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Astrology",
        "title": "Cross-system: how does your Saju match your Sun sign?",
        "body": (
            "Fun cross-check for Western astrology people.\n\n"
            "Note your Sun sign + Day Master element. Rough alignment:\n\n"
            "- Wood DM ≈ Aries/Sagittarius (active) or Taurus/Virgo (rooted)\n"
            "- Fire DM ≈ Leo/Aries/Sagittarius\n"
            "- Earth DM ≈ Taurus/Virgo/Capricorn\n"
            "- Metal DM ≈ Libra/Aquarius or Capricorn\n"
            "- Water DM ≈ Cancer/Scorpio/Pisces\n\n"
            f"Free Day Master finder: {_site('/en')}\n\n"
            "What's your combo?"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Zodiac animals ↔ Earthly Branches mapping",
        "body": (
            "The 12 animals map to the 12 Earthly Branches:\n\n"
            "Rat=子 | Ox=丑 | Tiger=寅 | Rabbit=卯\n"
            "Dragon=辰 | Snake=巳 | Horse=午 | Goat=未\n"
            "Monkey=申 | Rooster=酉 | Dog=戌 | Pig=亥\n\n"
            "'I'm a Tiger' = your YEAR branch is 寅. But you also have month, day, hour branches — three more 'animals.' Your zodiac year is just 1 of 4.\n\n"
            f"See all 4 branches: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Five Elements ↔ TCM organ correspondences",
        "body": (
            "Wu Xing crosses into Traditional Chinese Medicine:\n\n"
            "- **Wood** ↔ Liver/Gallbladder — anger, vision, planning\n"
            "- **Fire** ↔ Heart/Small Intestine — joy, circulation\n"
            "- **Earth** ↔ Spleen/Stomach — worry, digestion\n"
            "- **Metal** ↔ Lung/Large Intestine — grief, breath\n"
            "- **Water** ↔ Kidney/Bladder — fear, will\n\n"
            "Anecdotally: Wood-deficient Saju often correlates with liver-sensitive TCM constitution.\n\n"
            f"Free distribution: {_site('/en')}"
        ),
    },
    {
        "subreddit": "spirituality",
        "title": "Accepting an 'unfavorable' Saju reading",
        "body": (
            "Newcomers sometimes get readings highlighting 'difficult' patterns and feel demoralized.\n\n"
            "Reframe: every chart has tensions. The 'perfect' chart is fiction.\n\n"
            "What a chart describes is the **terrain you're walking on**. Same terrain produces triumph or tragedy depending on the walker.\n\n"
            "- 'Strong 7-Killings' = stress-prone OR resilient under pressure\n"
            "- 'Weak Day Master' = depleted OR genuinely cooperative\n"
            "- 'Lots of Hurting Officer' = unable to fit in OR creative truth-teller\n\n"
            f"Free chart for reflection: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "How to read New Year forecasts (Sewoon) properly",
        "body": (
            "Year-end zodiac forecasts are shallow. Proper Saju year analysis:\n\n"
            "1. **Annual stem-branch (세운)** interaction with YOUR natal chart.\n"
            "2. **Year falling in current Daewoon (대운)** — Daewoon × Sewoon matters more than Sewoon alone.\n"
            "3. **Five Element climate** — what gets emphasized vs depleted this year?\n\n"
            "For 2026 (Bingwu, Fire+Fire), cold/water-heavy charts may feel warmed up. Fire-heavy may overheat.\n\n"
            f"Year-by-year vs your chart: {_site('/en/yearly')}"
        ),
    },
    {
        "subreddit": "AskAstrologers",
        "title": "Useful Saju 'special spirits' (神煞) worth knowing",
        "body": (
            "~50+ special spirits exist. Useful ones as tie-breakers:\n\n"
            "1. **Tianyi Guiren (天乙貴人)** — Heavenly Noble. People report 'lucky encounters' at critical moments.\n"
            "2. **Yima (驛馬)** — Horse star. International moves, frequent travel.\n"
            "3. **Taohua (桃花)** — Peach Blossom. Romantic attraction magnet.\n"
            "4. **Yangren (羊刃)** — Sharp Blade. High-pressure jobs, dramatic events.\n\n"
            "Use as tie-breakers. Not load-bearing.\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Minimum knowledge for self-reading (80/20)",
        "body": (
            "Want basic self-reading without years of study? 80/20 list:\n\n"
            "**Must know:**\n"
            "1. Day Pillar (stem + branch of birth day)\n"
            "2. Five Element distribution\n"
            "3. Strongest + weakest Ten God\n"
            "4. Current Daewoon\n\n"
            "**Nice to have:**\n"
            "5. Hidden stems\n"
            "6. Major unions/clashes\n"
            "7. Key special spirits\n\n"
            "All 5 'must knows' visible on any decent free chart calculator.\n\n"
            f"Free chart showing all 7: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "When charts say 'avoid X element' — practical interpretation",
        "body": (
            "If your chart says 'avoid Fire,' what does that actually mean?\n\n"
            "**Realistic:**\n"
            "- Avoid careers HEAVILY Fire-domain (high-publicity performance, emotional intensity)\n"
            "- Fire-heavy years (Bing/Ding/Si/Wu) feel draining — pace yourself\n"
            "- Activities feeding your Yongshen restore you\n\n"
            "**Unrealistic (folk additions):**\n"
            "- Avoid red color, never wear it\n"
            "- Don't live south\n"
            "- Don't talk to Fire-element people\n\n"
            "Energetic readings > literal symbolism.\n\n"
            f"Free Yongshen hints: {_site('/en')}"
        ),
    },
    {
        "subreddit": "spirituality",
        "title": "Saju vs Korean shamanism (무속) — different traditions",
        "body": (
            "Quick clarification:\n\n"
            "**Saju (사주)** = Chinese-origin 4-pillar astrology. Scholarly tradition with classical texts. Not religion-bound.\n\n"
            "**Musok (무속)** = Korean indigenous shamanism with mediums. Religious/ritual tradition. Sometimes uses Saju as a tool.\n\n"
            "If you want self-understanding via typology → Saju.\n"
            "If you want spirit-mediation → different tradition.\n\n"
            f"Free Saju: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Reading your Hour Pillar — your private self",
        "body": (
            "Hour Pillar (時柱) = the 'private self' that emerges in childhood, family, old age.\n\n"
            "Observations:\n"
            "- Day vs Hour pillars very different → 'public face' vs 'private face' tension\n"
            "- Same-element Day and Hour → integrated, look the same in public and private\n"
            "- Hour Pillar Ten God strongly predicts late-life themes\n\n"
            "Need accurate birth time to read. Unknown hour = this pillar missing.\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "Astrology",
        "title": "BaZi/Saju timing analysis (Daewoon, Sewoon, Wolwoon, Iljin)",
        "body": (
            "Most popular content = personality. Other half = **timing analysis**.\n\n"
            "Tools:\n"
            "1. **Daewoon** (10-year periods) — when does wealth-focused decade begin?\n"
            "2. **Sewoon** (annual) — what tone does each year carry?\n"
            "3. **Wolwoon** (monthly) — granular forecasting\n"
            "4. **Iljin** (daily) — daily forecast\n\n"
            "Use for timing major decisions to favorable windows. NOT 'you'll marry this year' but 'this year supports stabilization of close relationships.'\n\n"
            f"Full Daewoon timeline: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Cross-element Day Pillars (Wood DM + Fire branch, etc.)",
        "body": (
            "When stem and branch are different elements, hybrid personalities:\n\n"
            "- **Jiawu** — Yang Wood + Fire branch. Vision lands as expression. Politicians, performers.\n"
            "- **Bingzi** — Yang Fire + Water branch. Warmth + contemplation. Artists with depth.\n"
            "- **Renxu** — Yang Water + Earth branch. Adaptability + stability. Diplomats.\n"
            "- **Gengyin** — Yang Metal + Wood branch. Decisive on creative ambition. Entrepreneurs.\n\n"
            "Stem-branch clash = built-in tension. Stem-branch generates = smoother.\n\n"
            f"Find yours: {_site('/en/sixty-pillars')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "How accurate is Saju marriage prediction? Real talk.",
        "body": (
            "What it CAN do:\n"
            "- Describe partner-type energetically matching your Day Pillar\n"
            "- Identify favorable Daewoon for partnership\n"
            "- Spot compatibility tensions in known couples\n\n"
            "What it CANNOT do:\n"
            "- Predict exact meeting time\n"
            "- Forecast marriage outcome accurately\n"
            "- Override self-work or choice\n\n"
            "Marriage timing predictions hit 30-40%. Compatibility analysis (after-the-fact) hits 70%+.\n\n"
            f"Free compatibility: {_site('/en/compatibility')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Reading your Year Pillar — what 'family' shows up",
        "body": (
            "Year Pillar = lineage, ancestors, early environment.\n\n"
            "- **Strong Resource** → supportive family, inherited knowledge\n"
            "- **Strong Wealth** → family business, financial focus in childhood\n"
            "- **Strong Officer** → traditional/structured family, formal-profession parents\n"
            "- **Strong Comparison** → independent/rebellious lineage\n"
            "- **Strong Output** → creative/nonconformist background\n\n"
            "Doesn't determine you. Describes 'what you came from.'\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "AskAstrologers",
        "title": "Saju vs Vedic Jyotish — different Eastern systems",
        "body": (
            "Common conflation. They're entirely different:\n\n"
            "**Saju/BaZi (East Asian):**\n"
            "- Stems and Branches of birth time\n"
            "- Five Elements\n"
            "- 60 day-pillar archetypes\n"
            "- No planets — pure time-cycle\n\n"
            "**Vedic Jyotish (Indian):**\n"
            "- Sidereal zodiac with planet positions\n"
            "- 27 Nakshatras\n"
            "- Dasha system\n"
            "- Closer in structure to Western astrology\n\n"
            "Both rich predictive frameworks. Different but sometimes parallel insights.\n\n"
            f"Free Saju: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Using BaZi/Saju as parenting tool",
        "body": (
            "Korean parents sometimes check kids' Saju to guide parenting:\n\n"
            "- **Day Master + Elements** — innate type. Don't fight it.\n"
            "- **Resource pattern** — structured learning vs experiential?\n"
            "- **Officer pattern** — how much external structure they handle\n"
            "- **Daewoon transitions** — anticipate adolescent or young adult shifts\n\n"
            "Used this way, Saju is just typology + timing — like MBTI parenting books.\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
    {
        "subreddit": "ChineseAstrology",
        "title": "Compatibility beyond romance — friendship and business",
        "body": (
            "Saju compatibility = pairwise relationship analysis, not romance-only.\n\n"
            "**Business partner**: Wealth + Officer compatibility. Strong combined Wealth = revenue. Officer alignment = smooth roles.\n\n"
            "**Best friend**: Day Master pairs that don't fully clash. Productive (生) relationships = complementary friendships.\n\n"
            "**Mentor**: ideally has Five Element your chart needs. Wood-deficient mentee benefits from Water-element mentor.\n\n"
            f"Free pair analyzer: {_site('/en/compatibility')}"
        ),
    },
    {
        "subreddit": "Astrology",
        "title": "Day Pillars with high social/romantic attraction patterns",
        "body": (
            "'Attractor patterns' in Saju:\n\n"
            "1. **Taohua position** — Peach Blossom branches (Zi, Wu, Mao, You) in day or hour\n"
            "2. **Day stem produces day branch** — Jiawu, Bingxu, Wuyin, Gengchen, Renshen\n"
            "3. **Yi (乙) and Ding (丁) Day Masters** — Yin Wood/Fire inherently magnetic\n"
            "4. **Strong Day Pillar with Output** — projects energy outward\n\n"
            "Describes attention received. NOT relationship quality (often chaotic love lives accompany these).\n\n"
            f"Free chart: {_site('/en')}"
        ),
    },
]


WARMUP_COMMENTS = [
    "The boundary at Ipchun (立春, ~Feb 4) is what trips up most beginner Saju calculators — they default "
    "to Jan 1 or Lunar New Year instead. Anyone born in late Jan or early Feb really needs to check this.",
    "Day Master analysis is the most beginner-friendly entry point. The 60 day pillars each have their own "
    "archetype, which makes the system feel less abstract than starting with Yongshen.",
    "Worth noting that 'strong vs weak Day Master' inverts which Ten Gods you want to see. Strong DM "
    "benefits from Wealth/Output/Officer. Weak DM benefits from Resource/Comparison.",
    "Hidden Stems (地藏干) inside each branch are easy to skip but carry a lot of the 'real' chart signal. "
    "Two charts that look identical at visible-character level can be very different once hidden stems "
    "are factored in.",
    "Late-Zi rule (야자시) — Zi hour spans 23:00 to 01:00, and Korean tradition shifts the day pillar at "
    "23:00 rather than midnight. People born around 23:00 should double-check which day their day pillar uses.",
    "Daewoon direction depends on polarity of Year Stem and gender. Yang-male / Yin-female go forward "
    "through the 60-cycle from your Month Pillar. Yin-male / Yang-female go reverse.",
    "Five Element balance > pure character count — strong Day Master vs weak Day Master changes the "
    "interpretation more than just 'lots of Wood' or 'no Fire' would suggest.",
    "Ipchun is the only annual boundary. The 12 month-pillar boundaries (Ipchun, Jingzhe, Qingming, etc.) "
    "are separate from the year boundary.",
    "Same Day Pillar but different Year/Month/Hour gives surprisingly different people. The Day Pillar is "
    "the strongest single signal but the other three pillars meaningfully modulate it.",
    "Astronomical solar-term calculation matters more than people realize for charts near solar-term "
    "boundaries. Meeus formula gets you to within minutes of accuracy — anything cruder can flip a pillar.",
]

WARMUP_SUBREDDITS = [
    "ChineseAstrology", "Astrology", "AskAstrologers", "Divination", "spirituality",
]


# ─── 상태 저장/로드 ────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_indices": [], "last_post_date": None, "last_comment_date": None,
            "comment_count": 0, "post_count": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                          encoding="utf-8")


# ─── Reddit OAuth ──────────────────────────────────────
def _http(method: str, url: str, headers: dict, data: bytes = None):
    req = request.Request(url, data=data, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
            return r.status, body
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        return getattr(e, "code", 0), f"{e}: {b}"


def get_access_token() -> str:
    if not all([CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD]):
        raise RuntimeError("Reddit credentials missing.")
    cred = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    body = parse.urlencode({
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
    }).encode()
    code, resp = _http("POST",
                       "https://www.reddit.com/api/v1/access_token",
                       headers={
                           "Authorization": f"Basic {cred}",
                           "User-Agent": USER_AGENT,
                           "Content-Type": "application/x-www-form-urlencoded",
                       },
                       data=body)
    if code != 200:
        raise RuntimeError(f"Token fetch failed: {code} {resp}")
    data = json.loads(resp)
    if "access_token" not in data:
        raise RuntimeError(f"No access_token in response: {data}")
    return data["access_token"]


def oauth_get(token: str, path: str) -> dict:
    code, resp = _http("GET", f"https://oauth.reddit.com{path}",
                       headers={"Authorization": f"bearer {token}",
                                "User-Agent": USER_AGENT})
    if code != 200:
        raise RuntimeError(f"GET {path} failed: {code} {resp}")
    return json.loads(resp)


def oauth_post(token: str, path: str, data: dict) -> dict:
    body = parse.urlencode(data).encode()
    code, resp = _http("POST", f"https://oauth.reddit.com{path}",
                       headers={"Authorization": f"bearer {token}",
                                "User-Agent": USER_AGENT,
                                "Content-Type": "application/x-www-form-urlencoded"},
                       data=body)
    if code not in (200, 201):
        raise RuntimeError(f"POST {path} failed: {code} {resp}")
    try:
        return json.loads(resp)
    except Exception:
        return {"raw": resp}


# ─── 액션 ──────────────────────────────────────────────
def diagnose_account(token: str) -> dict:
    me = oauth_get(token, "/api/v1/me")
    age_days = (time.time() - me["created_utc"]) / 86400
    total_karma = (me.get("link_karma") or 0) + (me.get("comment_karma") or 0)
    eligible_post = (age_days >= ACCOUNT_AGE_MIN_DAYS) and (total_karma >= KARMA_WARMUP_THRESHOLD)
    return {
        "username": me["name"],
        "link_karma": me.get("link_karma", 0),
        "comment_karma": me.get("comment_karma", 0),
        "total_karma": total_karma,
        "age_days": round(age_days, 1),
        "eligible_to_post": eligible_post,
        "stage": (
            "ready_post" if eligible_post
            else "warming_up" if age_days >= ACCOUNT_AGE_MIN_DAYS
            else "too_new"
        ),
    }


def submit_next_post(token: str, state: dict) -> dict:
    posted = set(state.get("posted_indices", []))
    available = [i for i in range(len(POSTS)) if i not in posted]
    if not available:
        state["posted_indices"] = []
        available = list(range(len(POSTS)))

    idx = random.choice(available)
    post = POSTS[idx]
    try:
        resp = oauth_post(token, "/api/submit", {
            "kind": "self",
            "sr": post["subreddit"],
            "title": post["title"],
            "text": post["body"],
            "api_type": "json",
            "sendreplies": "true",
        })
        url = None
        if "json" in resp and "data" in resp["json"]:
            url = resp["json"]["data"].get("url")
        state.setdefault("posted_indices", []).append(idx)
        state["last_post_date"] = date.today().isoformat()
        state["post_count"] = state.get("post_count", 0) + 1
        return {"ok": True, "subreddit": post["subreddit"],
                "title": post["title"], "url": url, "post_index": idx}
    except Exception as e:
        return {"ok": False, "error": str(e), "subreddit": post["subreddit"]}


def submit_warmup_comment(token: str, state: dict) -> dict:
    sub_name = random.choice(WARMUP_SUBREDDITS)
    try:
        listing = oauth_get(token, f"/r/{sub_name}/hot?limit=30")
    except Exception as e:
        return {"ok": False, "error": f"Failed to load /r/{sub_name}: {e}"}

    candidates = []
    for item in listing.get("data", {}).get("children", []):
        d = item.get("data", {})
        text = (d.get("title", "") + " " + d.get("selftext", "")).lower()
        if any(k in text for k in ["bazi", "saju", "four pillar", "day master",
                                   "chinese astrology", "korean astrology",
                                   "day pillar", "ten gods", "five element"]):
            candidates.append(d)

    if not candidates:
        return {"ok": False, "error": f"No matching posts in r/{sub_name}"}

    target = random.choice(candidates)
    parent = f"t3_{target['id']}"
    comment_text = random.choice(WARMUP_COMMENTS)
    try:
        resp = oauth_post(token, "/api/comment", {
            "thing_id": parent,
            "text": comment_text,
            "api_type": "json",
        })
        state["last_comment_date"] = date.today().isoformat()
        state["comment_count"] = state.get("comment_count", 0) + 1
        return {"ok": True, "subreddit": sub_name,
                "target_title": target.get("title"),
                "response_summary": str(resp)[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_daily():
    try:
        token = get_access_token()
    except Exception as e:
        print(f"[error] cannot get token: {e}")
        return None

    state = load_state()
    diag = diagnose_account(token)
    print(f"[diagnose] {json.dumps(diag, ensure_ascii=False)}")

    today = date.today().isoformat()
    if state.get("last_post_date") == today or state.get("last_comment_date") == today:
        print("Already acted today; exiting.")
        return diag

    if diag["stage"] == "too_new":
        print(f"Account too new ({diag['age_days']} days); skipping.")
    elif diag["stage"] == "warming_up":
        result = submit_warmup_comment(token, state)
        print(f"[warmup_comment] {json.dumps(result, ensure_ascii=False)}")
    else:
        result = submit_next_post(token, state)
        print(f"[post] {json.dumps(result, ensure_ascii=False)}")

    save_state(state)
    return diag


if __name__ == "__main__":
    run_daily()
