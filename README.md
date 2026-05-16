# 사주명리 — Tarofortune

Free, accurate **Korean Saju (4-pillar astrology)** calculator built from scratch in Python.
Authentic algorithm based on the **Meeus astronomical formulas** for 24 solar terms, with full **Late-Zi hour** correction and **day-pillar typology** for all 60 sexagenary archetypes.

**Live site**: [tarofortune.pythonanywhere.com](https://tarofortune.pythonanywhere.com)
**English version**: [tarofortune.pythonanywhere.com/en](https://tarofortune.pythonanywhere.com/en)

---

## What this is

A self-contained Saju (사주) / BaZi (八字) reader for the curious. No signup, no email, no payment.

For users:
- Enter your birth date + time → get full 4-pillar chart (Year/Month/Day/Hour)
- Ten Gods (十神), Twelve Life Stages (十二運星), Five Element distribution
- 100-year Daewoon (decadal luck) projection
- 60 day-pillar archetype readings
- Yearly fortune (2024–2028)
- Lunar↔Solar date converter
- Bilingual (Korean + English)

For developers:
- Pure-Python astronomical calculation (no `pyephem`, no external API)
- Meeus solar-longitude formula with Newton-iteration solar-term finder
- Cached LRU for solar terms (CPU-conscious, runs on free PythonAnywhere tier)
- IndexNow / RSS / PWA / Service Worker / hreflang i18n

---

## The interesting math

The hard part of Saju calculation isn't the 60-cycle counting — it's getting the **boundaries** right.

### 1. Year boundary at Ipchun (立春)

The Saju year doesn't start January 1. It starts the moment the sun reaches **315° ecliptic longitude** — the solar term Ipchun, around February 4 ±24h.

```python
def apparent_solar_longitude(jd: float) -> float:
    """Apparent solar longitude in degrees (Meeus chapter 27)."""
    t = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360
    m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360)
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    return (l0 + c) % 360
```

Then Newton iteration to find the exact JD when longitude crosses 315° for any given year. Accurate to seconds.

### 2. Late-Zi hour rule (야자시)

The day pillar transitions at **23:00 local time**, not midnight. Most online calculators silently get this wrong.

```python
if hour >= 23:
    day_idx = (day_idx + 1) % 60  # roll forward
```

### 3. Day pillar offset calibration

The 60-cycle for days is anchored to a verified reference:

```
2000-01-01 (Gregorian) = 戊午日 (Wuwu day, index 54)
JD floor of 2451544.5 = 2451544
2451544 mod 60 = 4
offset = (54 - 4) mod 60 = 50
```

So: `day_idx = (floor(JD) + 50) mod 60`. Calibrated once, always correct.

---

## Tech stack

- **Backend**: Python 3.13, Flask 3
- **No DB**: all charts are pure functions of input (no persistence needed)
- **Astronomy**: hand-rolled Meeus algorithm
- **Caching**: `functools.lru_cache` for solar terms (free-tier CPU is precious)
- **Frontend**: Vanilla HTML/CSS, ~22KB CSS, no framework
- **i18n**: dict-based translation, `/en/` URL prefix, full hreflang
- **SEO**: JSON-LD (Article, FAQ, BreadcrumbList), sitemap with hreflang `xhtml:link`, IndexNow protocol
- **PWA**: manifest + service worker + offline cache
- **Deployed on**: PythonAnywhere free tier
- **Automation bots**: Lemmy, Mastodon, Dev.to, Hashnode, Tistory (each in its own file)

---

## Local setup

```bash
git clone https://github.com/<your-username>/saju-platform.git
cd saju-platform
pip install flask pillow
python flask_app.py
# → http://127.0.0.1:5000
```

Optional environment variables (for ads/analytics):

```bash
export ADSENSE_CLIENT_ID="ca-pub-..."
export META_PIXEL_ID="..."
export GA_MEASUREMENT_ID="G-..."
```

For automation bots, see `.env.example`.

---

## Algorithm verification

Tests against well-known dates:

```python
assert lunar_to_solar(1990, 1, 1)  == date(1990, 1, 27)   # ✓
assert lunar_to_solar(2024, 1, 1)  == date(2024, 2, 10)   # ✓
assert lunar_to_solar(2000, 5, 5)  == date(2000, 6, 6)    # 단오 ✓
assert compute_saju(1990, 5, 15, 14, 30).year_pillar.name  == "경오"  # ✓
assert compute_saju(2024, 2, 4, 12, 0).year_pillar.name == "계묘"   # Ipchun was 17:11
```

---

## Why I built this

Most online Saju calculators have **silent bugs** in their solar-term boundaries. People born within ±24 hours of Ipchun routinely get the wrong year pillar. Korean-language tools are often paywalled. English-language Saju content is scarce.

Built this as a free reference that does the math right.

The interpretation layer (60 day-pillar archetypes, Ten Gods readings) is rooted in classical Ziping Mingli (자평명리) tradition. It's a **typology framework** for self-reflection, not fortune-telling.

---

## License

MIT — see `LICENSE`.

The 60 day-pillar interpretation text is original writing based on classical Ziping Mingli principles, also MIT-licensed. Free to adapt with attribution.

---

## Acknowledgments

- Jean Meeus, *Astronomical Algorithms* (2nd ed.) — for the solar position formulas
- The Ziping Mingli (子平命理) tradition — for the interpretive framework
- Korean Saju scholars whose 60-pillar typology this draws on

If you have a known-correct chart and find a bug, please open an issue with the input and expected output.
