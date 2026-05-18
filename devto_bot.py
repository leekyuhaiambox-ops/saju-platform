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
    # ─── 추가 12편 (총 15편으로 확장 — 다양성·연속 노출 회피) ─────
    {
        "title": "Solar Term Boundaries in Saju: The Meeus Algorithm Approach",
        "tags": ["python", "astronomy", "algorithms", "discuss"],
        "body_markdown": f"""When building a Saju (Korean 4-pillar astrology) calculator, the **trickiest part isn't the 60-cycle counting** — it's getting the solar term boundaries right.

## The Problem

Most online Saju calculators silently miscalculate year boundaries. They hardcode `Feb 4, 00:00` for Ipchun (立春, start of Saju year). But Ipchun is when the sun reaches **315° ecliptic longitude**, which varies by up to **±24 hours** depending on the year.

So a person born Feb 4, 2024 at 3am gets one chart from a bad calculator and a completely different chart (year pillar shifted by an entire year) from a correct one.

## The Fix

Implement the Meeus astronomical algorithm. Solar longitude at Julian Day:

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

Newton-iterate from a rough date estimate to find the exact JD when longitude crosses your target solar term.

## Performance

Each calculation is ~5ms. PythonAnywhere free tier has 100 CPU sec/day, so cache aggressively:

```python
@lru_cache(maxsize=4096)
def solar_term_jd(year, term_idx):
    ...
```

Solar terms repeat per `(year, term_idx)` pair, so caching is essentially free.

## Live site

[{_site_en()}]({_site_en()})

Open source on GitHub. Any Saju power user spotted bugs would love to hear.
""",
        "canonical_url": _site_en(),
    },
    {
        "title": "Korean Astrology vs Chinese BaZi: Same Math, Different Tradition",
        "tags": ["discuss", "philosophy", "asia", "personality"],
        "body_markdown": f"""Common question: "Is Korean Saju the same as Chinese BaZi?"

**Math: identical.**
**Interpretation: different schools.**

## What's identical
- Heavenly Stems (天干): Jia, Yi, Bing, Ding, Wu, Ji, Geng, Xin, Ren, Gui
- Earthly Branches (地支): Zi, Chou, Yin, Mao, Chen, Si, Wu, Wei, Shen, You, Xu, Hai
- 60-pillar cycle (六十甲子) from Jiazi to Guihai
- Five Elements + Yin-Yang foundation
- Ten Gods (十神) labels

## What's different
**Chinese BaZi** emphasizes:
- Pattern recognition (Geju, 格局)
- Useful God theory (Yongshen, 用神)
- Detailed timing predictions

**Korean Saju** (modern schools) emphasizes:
- **Day Pillar typology** — each of 60 day pillars is a distinct personality archetype
- Less prediction-focused, more self-understanding
- Cleaner integration with modern psychology

## Why it matters

If you're new to East Asian astrology, **Korean Day Pillar typology is the most beginner-friendly entry point**. You don't need to master the full BaZi predictive framework — just learn your one Day Pillar archetype.

## Try it

[{_site_en()}/sixty-pillars]({_site_en()}/sixty-pillars) — all 60 Day Pillar archetypes free, no signup.

What's your Day Pillar? Drop yours.
""",
        "canonical_url": _site_en("/sixty-pillars"),
    },
    {
        "title": "Why I Built a Free Saju Calculator Instead of Joining Existing Korean Astrology Sites",
        "tags": ["webdev", "showdev", "discuss"],
        "body_markdown": f"""Quick story on why I built [{_site_en()}]({_site_en()}) from scratch instead of just contributing to existing Korean Saju sites.

## The state of the field

Korean Saju sites in 2026 fall into three groups:

1. **Paid services** — accurate but ₩30,000+ per chart. Optimized for revenue extraction.
2. **Free aggregators** — riddled with ads, charts often miscalculated, optimized for SEO not accuracy.
3. **DIY scripts** — academically correct but no UI, only for developers.

None hit the sweet spot of **free + accurate + usable**.

## What I prioritized

Building from scratch let me:

1. **Get the math right** — Meeus solar terms (most free sites don't), Korean Late-Zi rule (most don't), no shortcuts
2. **Skip the dark patterns** — no email harvesting, no upsell modals, no "premium" gates
3. **Open source it** — anyone can verify the algorithm, fork, improve

## Tech choices

- **Backend**: Flask + Python 3.13 (free tier on PythonAnywhere)
- **No DB**: charts are pure functions of input — no persistence needed
- **No frontend framework**: ~20KB vanilla CSS, fast on mobile
- **i18n**: Korean default + English `/en/` prefix

## What I learned

Building public utility software is way more rewarding than I expected. The "soft" rewards (someone DMing "your site got my year pillar right when 4 others got it wrong") matter more than I thought.

[Try it]({_site_en()}) | [GitHub](https://github.com/leekyuhaiambox-ops/saju-platform)
""",
        "canonical_url": SITE_URL,
    },
    {
        "title": "5 Bugs I Found in Free BaZi Calculators (and Why They Matter)",
        "tags": ["showdev", "discuss", "javascript", "python"],
        "body_markdown": f"""Compared 15 free BaZi calculators while building my own. Here are the 5 most common bugs.

## Bug 1: Hardcoded "Feb 4" for Ipchun

The Saju year boundary (Ipchun, 立春) is the moment sun reaches 315° ecliptic longitude. Varies by ±24h yearly. Hardcoding "Feb 4 00:00" is wrong.

**Impact**: People born in late Jan to early Feb get wrong year pillar.

## Bug 2: Missing Late-Zi rule

In Korean tradition, day pillar transitions at 23:00 local, not midnight. Birth between 23:00 and 24:00 → next day's pillar.

**Impact**: People born at midnight get wrong day pillar.

## Bug 3: No true solar time correction

Korea uses Japan's time meridian. True solar time in Seoul is ~30 minutes behind clock time.

**Impact**: For births within 30 min of an hour boundary, hour pillar can flip.

## Bug 4: Wrong Daewoon direction logic

Decadal luck direction depends on Year Stem polarity × gender. Most calculators get the polarity rule backward for half the population.

**Impact**: Entire 100-year luck timeline shifts by one decade direction.

## Bug 5: Visible-only Ten Gods

Each Earthly Branch contains 1-3 hidden Heavenly Stems. Ten Gods analysis ignoring hidden stems misses 30-40% of the chart signal.

**Impact**: Personality reading shallow and often wrong.

## Test your calculator

If your tool fails any of these 5, find a better one.

[Free reference that handles 1-3 correctly]({_site_en()}).
""",
        "canonical_url": SITE_URL,
    },
    {
        "title": "Hidden Stems (地藏干): The Layer Beneath Your BaZi Chart",
        "tags": ["discuss", "philosophy", "asia"],
        "body_markdown": f"""If you've only worked with the visible 8 characters in your BaZi chart, there's a deeper layer: **Hidden Stems (Dizanggan, 地藏干)**.

## The concept

Each Earthly Branch isn't just one element. It contains 1-3 hidden Heavenly Stems with different weights.

| Branch | Hidden Stems |
|---|---|
| 子 Zi | Gui (癸) — pure Yin Water |
| 丑 Chou | Ji (己), Xin (辛), Gui (癸) |
| 寅 Yin | Jia (甲), Bing (丙), Wu (戊) |
| 卯 Mao | Yi (乙) — pure Yin Wood |
| 辰 Chen | Wu (戊), Yi (乙), Gui (癸) |
| 巳 Si | Bing (丙), Wu (戊), Geng (庚) |
| 午 Wu | Ding (丁), Ji (己) |
| 未 Wei | Ji (己), Ding (丁), Yi (乙) |
| 申 Shen | Geng (庚), Wu (戊), Ren (壬) |
| 酉 You | Xin (辛) — pure Yin Metal |
| 戌 Xu | Wu (戊), Xin (辛), Ding (丁) |
| 亥 Hai | Ren (壬), Jia (甲) |

## Why it matters

Two charts with identical visible 8 characters can be **very different people** once hidden stems are factored in.

Example: Chart that looks "lacking Water" (no visible Ren/Gui) might actually have Gui hidden in a Chen branch — strong Water presence, just hidden.

## The 30% rule

Ten Gods analysis based on visible stems alone captures ~70% of the chart. Hidden stems give the missing 30%.

## See yours

[{_site_en()}]({_site_en()}) — shows hidden stems for each pillar automatically.
""",
        "canonical_url": _site_en(),
    },
    {
        "title": "Day Master Strength in BaZi: The Counterintuitive Truth",
        "tags": ["discuss", "philosophy"],
        "body_markdown": f"""Common BaZi misconception: "Strong Day Master = good chart".

Actually it's more nuanced. Let me explain.

## What "strong" means

**Strong Day Master** = your DM element has lots of support in the chart (same element + element that produces it).

**Weak Day Master** = surrounded by elements that drain or restrain it.

## The inversion

Strong vs weak inverts which Ten Gods you "want":

**Strong DM needs to channel excess.** Wants:
- Output (Food/Hurt) — creative expression
- Wealth — productive use
- Officer — disciplined direction

**Weak DM needs support.** Wants:
- Resource (Seal) — nourishment
- Comparison (Sibling) — peer support

## The counterintuitive part

A "Wealth period" (lots of Wealth element in luck cycle) is:
- **Good for strong DM** — channels excess productively
- **Bad for weak DM** — drains already-depleted DM

Most beginner readings get this exactly backward.

## Real-world impact

Someone with weak DM who hits a "Wealth-heavy decade" often experiences burnout, financial stress, or health issues — the opposite of "Wealth = money".

[Check your Day Master strength]({_site_en()}) (Five Element distribution chart).
""",
        "canonical_url": _site_en(),
    },
    {
        "title": "The Twelve Life Stages in BaZi (十二運星) — Decoding Energy Phases",
        "tags": ["discuss", "philosophy"],
        "body_markdown": f"""Twelve Life Stages (Sipi-yunsung, 十二運星) gauge the energy of your Day Master at each branch position.

## The 12 stages

Birth → Bathing → Capping → Establishing → Empire → Decline → Sickness → Death → Tomb → Cut-off → Womb → Nurture

Each represents an "energy phase" of your Day Master:

| Stage | Hanja | Energy Phase |
|---|---|---|
| Birth | 長生 | Newborn vitality. Fresh, pure. |
| Bathing | 沐浴 | Growing, changing. Style, frequent romance. |
| Capping | 冠帶 | Coming-of-age. Drive, self-respect. |
| Establishing | 建祿 | Peak adult activity. Independence. |
| Empire | 帝旺 | Apex. Charisma; possible arrogance. |
| Decline | 衰 | Past peak. Calm, reflective. |
| Sickness | 病 | Weakening. Sensitivity, art. |
| Death | 死 | Halted activity. Introspection. |
| Tomb | 墓 | Buried. Patience, research. |
| Cut-off | 絶 | Severance. Frequent change. |
| Womb | 胎 | Conceived. Latent potential. |
| Nurture | 養 | Fetus growing. Development. |

## Practical use

Look at your Day Master's stage in each of the 4 pillars (Year/Month/Day/Hour). The pattern tells you when your energy peaks in life.

**Example**: Day Master in Empire (帝旺) at hour pillar = late-life peak. Day Master in Birth (長生) at year pillar = strong childhood foundation.

## Free chart

[{_site_en()}]({_site_en()}) — automatic Twelve Life Stage analysis for each of your 4 pillars.
""",
        "canonical_url": _site_en(),
    },
    {
        "title": "Daewoon (大運) Calculation: The Step-by-Step Algorithm",
        "tags": ["python", "algorithms", "discuss"],
        "body_markdown": f"""Daewoon (Da Yun, 大運) is the 10-year luck cycle in BaZi. Here's how it's calculated.

## Step 1: Determine direction

- **Yang-Year-Stem + Male** OR **Yin-Year-Stem + Female**: forward
- **Yin-Year-Stem + Male** OR **Yang-Year-Stem + Female**: reverse

## Step 2: Starting age

Distance from birth to nearest month-boundary solar term, divided by 3, rounded.

```python
def find_neighbor_month_term_jd(year, month, day, hour, minute, forward):
    birth_jd = gregorian_to_jd(year, month, day, hour, minute)
    candidates = []
    for y_off in (-1, 0, 1):
        for t_idx in MONTH_BUILDING_TERMS:  # 입춘, 경칩, 청명, 입하, ...
            jd = solar_term_jd(year + y_off, t_idx) + 9/24  # KST
            candidates.append(jd)
    candidates.sort()
    if forward:
        for jd in candidates:
            if jd > birth_jd:
                return jd
    else:
        for jd in reversed(candidates):
            if jd < birth_jd:
                return jd
    return candidates[-1] if forward else candidates[0]

days_diff = abs(neighbor_jd - birth_jd)
start_age = max(1, round(days_diff / 3))
```

## Step 3: Generate 10 pillars

Starting from Month Pillar, move forward (or reverse) through 60-cycle, one step per decade.

```python
cur_stem, cur_branch = month_pillar.stem, month_pillar.branch
direction = 1 if forward else -1
daewoons = []
for i in range(10):
    cur_stem = (cur_stem + direction) % 10
    cur_branch = (cur_branch + direction) % 12
    daewoons.append({{
        'age': start_age + i * 10,
        'pillar': (cur_stem, cur_branch),
    }})
```

## Step 4: Interpret

Each Daewoon brings a stem-branch combination. Compute its Ten God relative to your natal Day Master + Twelve Life Stage. That's how you read the decade's themes.

## Full implementation

[GitHub](https://github.com/leekyuhaiambox-ops/saju-platform) | [Live demo]({_site_en()}) — automatic 100-year Daewoon timeline.
""",
        "canonical_url": _site_en(),
    },
    {
        "title": "Building i18n for a Korean-First Web App: My /en/ Prefix Approach",
        "tags": ["webdev", "showdev", "python", "flask"],
        "body_markdown": f"""When building [{_site_en()}]({_site_en()}) (Korean Saju calculator), I needed bilingual support without bloat. Here's the i18n approach I used.

## Architecture decision

Two routing options were on the table:

**A. Query string**: `/result?lang=en`
- ❌ Bad SEO (Google sees one URL)
- ❌ No hreflang clean mapping

**B. URL prefix**: `/en/result`
- ✓ Clean hreflang
- ✓ One URL per (page, language)
- ✓ Easy CDN caching

Went with B.

## Flask implementation

```python
@app.before_request
def _detect_lang():
    p = request.path
    if p == "/en" or p.startswith("/en/"):
        g.lang = "en"
    else:
        g.lang = "ko"

@app.route("/")
@app.route("/en/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST", "GET"])
@app.route("/en/result", methods=["POST", "GET"])
def result():
    # g.lang automatically set by before_request
    is_en = (g.lang == "en")
    ...
```

## Translation dict

No Flask-Babel — just a dict for simplicity:

```python
UI = {{
    "site_name": ("사주명리 — 운명의 설계도", "Saju Myeongri — Blueprint of Destiny"),
    "hero_title": ("당신의 사주, 운명의 설계도", "Your Saju — The Blueprint of Destiny"),
    ...
}}

def t(key, lang=None):
    lang = lang or g.lang
    pair = UI.get(key)
    if not pair:
        return key
    return pair[1] if lang == "en" else pair[0]
```

In templates: `{{{{ t('hero_title') }}}}`

## hreflang in templates

```html
{{% set cur_path = request.path %}}
{{% if cur_path.startswith('/en') %}}
  {{% set ko_path = cur_path[3:] or '/' %}}
  {{% set en_path = cur_path %}}
{{% else %}}
  {{% set ko_path = cur_path %}}
  {{% set en_path = '/en' + cur_path %}}
{{% endif %}}
<link rel="alternate" hreflang="ko" href="{{{{ ko_path }}}}">
<link rel="alternate" hreflang="en" href="{{{{ en_path }}}}">
<link rel="alternate" hreflang="x-default" href="{{{{ ko_path }}}}">
```

## Result

770+ URLs indexed (350 KR + 300 EN + media). Clean SEO. ~30KB code overhead.

[Try it]({_site_en()}) | [Korean]({SITE_URL}) — same content, different language.
""",
        "canonical_url": SITE_URL,
    },
    {
        "title": "OG Card Generation: Dynamic PNG per User Result with Flask + Pillow",
        "tags": ["webdev", "showdev", "python"],
        "body_markdown": f"""Wanted each user's Saju result to have a **unique shareable card** when posted to KakaoTalk / Twitter / Discord. Built dynamic OG image generation.

## The architecture

```
[User shares /result URL]
     ↓
[Social platform fetches og:image]
     ↓
[/og/result.png?y=1990&m=5&d=15...]
     ↓
[Flask + Pillow renders 1200×630 PNG with user's chart]
```

## Pillow rendering

```python
from PIL import Image, ImageDraw, ImageFont

def render_result_card(year_pillar, month_pillar, day_pillar, hour_pillar,
                       day_idx, lang="ko", name=""):
    img = gradient_bg(1200, 630, BG_DARK, ELEMENT_COLORS[element_ko][1])
    draw = ImageDraw.Draw(img)

    # Mark
    draw.text((50, 40), "사주명리", font=_f(40, "kr_serif"), fill=ACCENT)

    # 4 Pillars as boxes
    for i, (p, label) in enumerate(pillars):
        x = 50 + i * 130
        draw.rounded_rectangle([x, 170, x + 110, 300], radius=12, outline=fg, width=3)
        hanja = HEAVENLY_STEMS[p["stem"]] + EARTHLY_BRANCHES[p["branch"]]
        draw.text((x + 55, 250), hanja, font=_f(54, "kr_serif"), fill=LIGHT, anchor="mm")

    # Day Pillar headline (right side)
    draw.text((660, 220), pillar_name, font=_f(48, "kr_serif"), fill=ACCENT)

    buf = BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()
```

## Performance

PythonAnywhere free tier: 100 CPU sec/day. Each render ~80ms → ~1250 cards/day max.

With aggressive `Cache-Control: max-age=86400` header, repeat shares cost 0 CPU.

## Linux font fallbacks

```python
FONT_KR_SERIF_LINUX = "/usr/share/fonts/truetype/nanum/NanumMyeongjoBold.ttf"
FONT_KR_SERIF_WIN = r"C:\\Windows\\Fonts\\HMKMRHD.TTF"

def _f(size, want="kr_serif"):
    for p in [FONT_KR_SERIF_LINUX, FONT_KR_SERIF_WIN]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()
```

## Result

KakaoTalk share previews now show user's actual Day Pillar in the card. Average share → 5-10 viewer clicks (vs static card ~1-2).

[Live demo]({_site_en()}) | [Source](https://github.com/leekyuhaiambox-ops/saju-platform/blob/main/saju/og_card.py)
""",
        "canonical_url": SITE_URL,
    },
    {
        "title": "IndexNow Protocol: Free Instant Indexing for Small Sites",
        "tags": ["seo", "webdev", "showdev"],
        "body_markdown": f"""**Problem**: Google deprecated their sitemap ping endpoint in 2023. New small sites take weeks/months to get indexed.

**Solution**: IndexNow protocol. Push URLs directly to Bing, Yandex, Naver, Seznam in one API call.

## Setup (3 steps)

### 1. Generate a key

Any 32-char hex string. Stays constant for your site.

```python
INDEXNOW_KEY = "8a7d3e2f1b4c5a6d9e8f7a6b5c4d3e2f"
```

### 2. Serve key at root

```python
@app.route("/" + INDEXNOW_KEY + ".txt")
def indexnow_key_file():
    return Response(INDEXNOW_KEY, mimetype="text/plain")
```

This proves you own the domain.

### 3. Push URLs

```python
def submit_urls(host: str, urls: list[str]) -> dict:
    payload = {{
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{{host}}/{{INDEXNOW_KEY}}.txt",
        "urlList": urls[:10000],
    }}
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        "https://api.indexnow.org/IndexNow",
        data=body, method="POST",
        headers={{"Content-Type": "application/json; charset=utf-8"}}
    )
    with request.urlopen(req, timeout=30) as r:
        return {{"status": r.status, "body": r.read().decode()}}
```

## Daily automation

I run this nightly via GitHub Actions:

```yaml
- name: Submit URLs to IndexNow
  run: |
    python auto_index.py
```

## Result

Bing indexing time: **dropped from 2 weeks to ~48 hours** for new pages. Yandex similar. Google still uses its own sitemap discovery (no IndexNow support).

## Note for Google

Google explicitly didn't join IndexNow. For Google, still need:
- Submit sitemap.xml to Search Console
- Internal linking from existing indexed pages
- Time

## Source

[auto_index.py](https://github.com/leekyuhaiambox-ops/saju-platform/blob/main/saju/indexnow.py) — full implementation, 50 lines.

[{_site_en()}]({_site_en()})
""",
        "canonical_url": SITE_URL,
    },
    {
        "title": "GitHub Actions for Free 24/7 Cron: Migrating Windows Task Scheduler",
        "tags": ["devops", "github", "showdev", "webdev"],
        "body_markdown": f"""**Problem**: I had a daily bot running on my PC via Windows Task Scheduler. But the bot didn't fire when my PC was off.

**Solution**: Migrate to GitHub Actions. Free 2000 min/month for public repos.

## The workflow

```yaml
name: Daily Bot
on:
  schedule:
    - cron: '0 16 * * *'   # UTC 16:00 = KST 01:00
  workflow_dispatch:

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run bots
        env:
          API_TOKEN: ${{{{ secrets.API_TOKEN }}}}
        run: python run_bots.py
      - name: Commit state
        run: |
          git config user.name "bot"
          git config user.email "bot@example.com"
          git add .state.json
          git diff --cached --quiet || git commit -m "state update"
          git push
```

## Anti-bot pattern: random delay

GitHub Actions cron has a known "exactly on the hour" issue, making your bot look like a bot. Add randomization:

```yaml
- name: Random delay
  if: github.event_name == 'schedule'
  run: |
    DELAY=$((RANDOM % 7200))
    echo "Sleeping ${{DELAY}}s"
    sleep ${{DELAY}}
```

## Secrets setup via API

I automated secret setup with PyNaCl:

```python
from nacl import encoding, public

def encrypt_secret(public_key_b64, value):
    pk = public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    return base64.b64encode(sealed_box.encrypt(value.encode())).decode()

# PUT /repos/{{owner}}/{{repo}}/actions/secrets/{{name}}
```

## Result

- PC powered off → bot still runs ✓
- 4-channel posting daily (Lemmy, Mastodon, Dev.to, IndexNow)
- ~30 seconds per run × 30 days = 15 min/month (0.7% of free quota)

## Caveat

GitHub Actions cron has 5-15 min schedule drift. Don't rely on it for precise timing.

[Workflow source](https://github.com/leekyuhaiambox-ops/saju-platform/blob/main/.github/workflows/daily-bot.yml)

[{_site_en()}]({_site_en()})
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
