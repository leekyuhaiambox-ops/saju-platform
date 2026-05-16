# Show HN / Product Hunt / dev.to 런치 카피

## Show HN — Hacker News 게시용

**제목 (80자 이하)**:
```
Show HN: A Korean astrology (Saju) calculator with proper Meeus-algorithm solar terms
```

**본문**:
```
Built a free Saju (Korean 4-pillar astrology, equivalent to Chinese BaZi) calculator from scratch in Python. Most existing online calculators silently miscalculate the year/month boundaries because they hardcode "Feb 4 00:00" for Ipchun (立春) — but the actual moment is when the sun reaches 315° ecliptic longitude, which varies by up to ±24 hours.

The math:

  def apparent_solar_longitude(jd):
      t = (jd - 2451545.0) / 36525.0
      l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360
      m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360)
      c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
           + (0.019993 - 0.000101 * t) * math.sin(2 * m)
           + 0.000289 * math.sin(3 * m))
      return (l0 + c) % 360

Then Newton iteration to find the exact JD when longitude crosses target. Caches per (year, term_idx) so it's free at runtime.

Also implements the Korean Late-Zi hour rule (day pillar rolls forward at 23:00, not midnight) — another silent bug in most free calculators.

Stack: Flask + Pillow + vanilla HTML/CSS. No DB, no auth, no email collection. Hosted on PythonAnywhere free tier.

Live: https://tarofortune.pythonanywhere.com/en

Source: https://github.com/<your-username>/saju-platform

Built it because I kept getting different results from different Saju calculators and wanted to actually understand which one was right.

Curious for feedback if you know your own chart and notice anything off.
```

---

## Product Hunt 런치 카피

**Tagline (40자)**:
```
Free Korean astrology reader with real math
```

**Short description**:
```
Tarofortune is an open-source Korean Saju (4-pillar astrology) calculator that
uses the Meeus astronomical algorithm for accurate solar-term boundaries —
fixing the silent bug that miscalculates year/month pillars in most free
online tools. No signup, no email, just enter your birth date and time.
```

**Long description**:
```
Saju (사주) is the Korean tradition of Chinese 4-pillar astrology. Most
free Saju calculators online have a hidden bug: they use "February 4 00:00"
as the year boundary (입춘, Ipchun), but the actual moment varies by up to
±24 hours depending on Earth's orbital position. People born within that
window routinely get the wrong year pillar.

Tarofortune is the open-source fix:

✦ Meeus astronomical algorithm for 24 solar terms (accurate to minutes)
✦ Korean Late-Zi rule (day pillar rolls forward at 23:00)
✦ 60 day-pillar archetype readings (the Korean equivalent of 60 sun signs)
✦ Ten Gods, Twelve Life Stages, Five Element distribution
✦ 100-year Daewoon (decadal luck) projection
✦ Bilingual (Korean + English)
✦ PWA-installable, offline-capable
✦ MIT licensed, hosted on free tier

Why? Because Saju shouldn't require paywalls or wrong math.
```

---

## dev.to 런치 글

**제목**:
```
I built a Korean astrology calculator and the math is more interesting than I expected
```

**Tags**: `python`, `webdev`, `showdev`, `astronomy`, `flask`

**본문**: (이미 devto_bot.py POSTS[0]에 작성됨 — 그대로 활용)

---

## Reddit r/Korean / r/SideProject 게시용 (계정 워밍 후)

```
Title: I made a free Saju (Korean astrology) calculator that actually does the math right

Body:
Built this because I noticed most free Saju calculators online quietly miscalculate
the year pillar by treating Ipchun (立春) as "Feb 4 midnight" — when the actual
moment varies by up to a full day depending on the year. People born in late
January or early February routinely get the wrong chart.

The site does proper Meeus astronomical calculation for all 24 solar terms,
applies the Korean Late-Zi hour rule, and shows all 60 day-pillar archetypes
in Korean and English.

Completely free, no signup, no ads in your face. Source code on GitHub
(MIT licensed) for the curious.

https://tarofortune.pythonanywhere.com

Open to feedback, especially from anyone who has their chart from a paid
Saju master and wants to verify.
```

---

## Twitter / X 런치 스레드

**Tweet 1/5**:
```
I built a free Korean astrology (Saju) calculator and ended up writing
more astronomy code than expected.

The hard part isn't 60-cycle counting. It's getting the solar-term
boundaries right. Most online tools silently get this wrong.

🔗 https://tarofortune.pythonanywhere.com/en
```

**Tweet 2/5**:
```
Year boundary in Saju isn't Jan 1 — it's the moment the sun reaches 315°
ecliptic longitude (Ipchun / 立春). That moment varies by up to ±24h.

Most calculators hardcode "Feb 4 00:00." Anyone born within that window
gets the wrong year pillar.
```

**Tweet 3/5**:
```
Fixed it with the Meeus algorithm from Astronomical Algorithms:

apparent_solar_longitude(jd):
  t = (jd - 2451545) / 36525
  L0 = mean longitude
  M = mean anomaly
  C = equation of center
  return (L0 + C) % 360

Then Newton-iterate to find exact term crossing.
```

**Tweet 4/5**:
```
Also fixed the Korean Late-Zi rule: day pillar transitions at 23:00 local,
not midnight. Another silent bug in most free tools.

Calibrated day-pillar offset to verified reference: 2000-01-01 = 戊午日 (54).
So: floor(JD) + 50 mod 60 = day index.
```

**Tweet 5/5**:
```
Stack: Flask + Pillow + vanilla HTML/CSS. No DB, no signup. MIT licensed.

If you know your chart and find a bug, open an issue.

Source: github.com/<your-username>/saju-platform
Live: tarofortune.pythonanywhere.com
```
