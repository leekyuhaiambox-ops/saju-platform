"""
범용 awesome-list 자동 PR 생성기
================================

지정한 awesome-list repo에 fork + commit + PR을 자동 생성.

실행:
  python auto_pr_generic.py --owner hemanth --repo awesome-pwa --section "Examples" --token <ghp>

설정:
  PRESETS dict의 각 entry가 한 awesome-list 대상.
  사이트별 카피는 ADDITIONS dict에서 가져옴.
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request


OUR_USER = "leekyuhaiambox-ops"


PRESETS = {
    "hemanth/awesome-pwa": {
        "section": "##",
        "section_keywords": ["Examples", "Apps", "Showcase"],
        "additions": [
            "- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) - Interactive PWA mapping municipal local-currency merchant locations across 31 cities of Gyeonggi Province, South Korea. Real-time \"open now\" filter, KakaoTalk share, public open data. React + Vite + Leaflet on Firebase Hosting.",
        ],
        "pr_title": "Add Gyeonggi Currency Map (PWA showcase)",
        "pr_body": """Adds **Gyeonggi Currency Map** — a real-world Progressive Web App used by Gyeonggi Province (14M residents, Korea).

- URL: https://gyeonggi-currency-map.web.app
- Stack: React + Vite + Leaflet + Firebase Hosting, public open data
- PWA-installable (manifest + service worker), KakaoTalk share via JS SDK
- 31-city merchant search with real-time \"open now\" filter

Solo-built, freemium ad-supported. Happy to revise the section if a different placement is preferred.
""",
    },

    "mjhea0/awesome-flask": {
        "section": "##",
        "section_keywords": ["Open Source Projects", "Open-Source", "Showcase", "Projects", "Apps"],
        "additions": [
            "- [Saju Fortune](https://tarofortune.pythonanywhere.com) - Free Korean four-pillars (saju) astrology calculator with EN+KR interpretations. 60 day-pillar archetypes, five elements, ten gods, twelve life stages, daily luck, compatibility. Flask + Pillow for dynamic OG cards, no DB, deployed on PythonAnywhere free tier.",
            "- [GeoInfomatic — Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com) - Isochrone-based neighborhood accessibility analyzer for Korea. Walk or transit, 10-45 min radius, 8 facility types, AI summary, 100-point composite score. Flask + Leaflet + OSRM walking graph + custom transit graph.",
        ],
        "pr_title": "Add two production Flask apps: Saju Fortune + GeoInfomatic",
        "pr_body": """Adds two real-world Flask applications running on the PythonAnywhere free tier.

1. **Saju Fortune** — https://tarofortune.pythonanywhere.com
   Korean four-pillars astrology calculator (EN+KR). Uses Meeus astronomical algorithms for solar-term boundary calculations. Dynamic OG card generation with Pillow. No database — pure computation.

2. **GeoInfomatic — Living Zone Accessibility** — https://geoinfomatic.pythonanywhere.com
   Isochrone-based neighborhood analyzer. Walking/transit isochrones drawn with Leaflet polygons. Custom Korean subway+bus graph traversal with transfer penalties. Freemium model.

Both are solo-built and demonstrate what's possible on Flask + PA's free tier. Happy to revise placement.
""",
    },

    "osmlab/awesome-openstreetmap": {
        "section": "##",
        "section_keywords": ["Map", "Application", "Showcase", "Projects", "Use Cases", "Examples"],
        "additions": [
            "- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) - PWA mapping local-currency merchant locations across 31 cities of Gyeonggi Province (South Korea, 14M residents). OSM tiles via Leaflet, public open data, real-time \"open now\" filter.",
            "- [GeoInfomatic — Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com) - Isochrone-based neighborhood accessibility analyzer for Korea. OSM-based walking graph (OSRM), isochrones rendered as Leaflet polygons, multi-facility analysis (school/hospital/mart/park/etc).",
        ],
        "pr_title": "Add two OSM-powered apps from Korea (currency map + isochrone analyzer)",
        "pr_body": """Two real-world OSM consumers in production in South Korea:

1. **Gyeonggi Currency Map** — https://gyeonggi-currency-map.web.app
   31-city merchant search PWA over OSM tiles via Leaflet. Used by residents who get 6-10% cashback on top-ups but struggle to find participating merchants.

2. **GeoInfomatic** — https://geoinfomatic.pythonanywhere.com
   Walking isochrones generated from an OSRM walking-graph mesh, overlaid as Leaflet polygons. Multi-facility analysis (school, hospital, mart, park, gym, pharmacy, library, cafe) within reach.

Both solo-built. Sharing because both are non-toy real-world OSM use cases. Happy to revise sections.
""",
    },

    "etewiah/awesome-real-estate": {
        "section": "##",
        "section_keywords": ["Tools", "Apps", "Resources", "Useful", "Analytics"],
        "additions": [
            "- [GeoInfomatic — Living Zone Accessibility (Korea)](https://geoinfomatic.pythonanywhere.com) - Isochrone-based neighborhood accessibility analyzer for South Korea. Pick any address, see 10/20/30/45-min walking or transit reachability with 8 facility types overlaid. 100-point composite score with AI summary. No real-estate listings — pure accessibility analysis for moving / due-diligence decisions. Freemium.",
        ],
        "pr_title": "Add GeoInfomatic (Korean neighborhood accessibility analyzer, no listings)",
        "pr_body": """Adds **GeoInfomatic** — a real-estate decision-support tool specifically built without property listings.

- URL: https://geoinfomatic.pythonanywhere.com
- Use case: moving / relocation / urban-planning / school-district comparison
- Output: 100-point composite accessibility score + AI natural-language summary
- Transit mode breaks results down by transfer count (0/1/2+) which most tools skip

Solo-built. Freemium model (5 free analyses/day, $7/month Pro for unlimited + PDF reports). Open to feedback / different placement.
""",
    },

    "sshuair/awesome-gis": {
        "section": "##",
        "section_keywords": ["Application", "Apps", "Web", "Showcase", "Examples", "Map", "Project"],
        "additions": [
            "- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) - PWA mapping merchants accepting Gyeonggi Province's municipal local-currency across 31 cities (Korea, 14M residents). OSM tiles via Leaflet, public open data, real-time \"open now\" filter, KakaoTalk share. React + Vite + Firebase Hosting.",
            "- [GeoInfomatic — Living Zone Accessibility (Korea)](https://geoinfomatic.pythonanywhere.com) - Isochrone-based neighborhood accessibility analyzer. Walking/transit reachability with 8 facility types overlaid. Custom Korean subway+bus graph + OSRM walking mesh. Flask + Leaflet on PythonAnywhere free tier.",
        ],
        "pr_title": "Add two real-world GIS apps from Korea (currency map + isochrone analyzer)",
        "pr_body": """Two production GIS web apps used in South Korea:

1. **Gyeonggi Currency Map** — https://gyeonggi-currency-map.web.app
   31-city merchant search PWA on Leaflet + OSM. Public open data (province API).

2. **GeoInfomatic** — https://geoinfomatic.pythonanywhere.com
   Isochrone-based accessibility analyzer with multi-facility overlay (school/hospital/mart/park/etc). Walking via OSRM mesh, transit via custom Korean graph.

Both solo-developed and demonstrate practical GIS deployment on free-tier infrastructure. Happy to revise placement.
""",
    },

    "johackim/awesome-indiehackers": {
        "section": "##",
        "section_keywords": ["Project", "Products", "Showcase", "Indie", "SaaS", "Startup", "Example", "Apps"],
        "additions": [
            "- [Saju Fortune](https://tarofortune.pythonanywhere.com) - Korean four-pillars astrology calculator (EN+KR). Ad-supported, no signup. Solo-built on Flask + PythonAnywhere free tier. ~700 daily organic visits.",
            "- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) - 31-city local-currency merchant map PWA (Korea). Ad-supported. React + Firebase Hosting.",
            "- [GeoInfomatic — Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com) - Korean neighborhood isochrone analyzer. Freemium ($7/mo Pro). Flask + Leaflet.",
        ],
        "pr_title": "Add 3 solo-built Korean indie projects (saju + map + accessibility)",
        "pr_body": """Three indie projects from a solo Korean dev, all running on free-tier infrastructure with ad-supported or freemium monetization:

1. **Saju Fortune** — https://tarofortune.pythonanywhere.com
2. **Gyeonggi Currency Map** — https://gyeonggi-currency-map.web.app
3. **GeoInfomatic** — https://geoinfomatic.pythonanywhere.com

All built solo, no investor money, demonstrating what's possible on PythonAnywhere + Firebase free tiers with Korean public open data. Happy to revise placement / section.
""",
    },

    "xcomptek/awesome-saas-boilerplates": {
        "section": "##",
        "section_keywords": ["FastAPI", "Other"],  # Python framework section
        "additions": [
            "- [GeoInfomatic — Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com) - Production Flask SaaS (Korean neighborhood isochrone analyzer). Freemium model: 5 free analyses/day, $7/month Pro for unlimited + PDF reports + multi-point comparison. Flask + Leaflet + Toss Payments. Solo-built on PythonAnywhere free tier.",
        ],
        "pr_title": "Add GeoInfomatic (production Flask freemium example)",
        "pr_body": """Adds **GeoInfomatic** — a Flask-based bootstrapped SaaS in production.

- URL: https://geoinfomatic.pythonanywhere.com
- Model: Freemium (5 free/day, $7/mo Pro)
- Stack: Flask + Leaflet on PythonAnywhere free tier, Toss Payments for Korean subscriptions

Flask isn't FastAPI but Python SaaS — happy to revise placement (perhaps a Flask section, or Other).
""",
    },

    "garimasingh128/awesome-python-projects": {
        "section": "##",
        "section_keywords": ["Web", "Application", "Project", "Apps", "App", "Productivity"],
        "additions": [
            "- [Saju Fortune](https://tarofortune.pythonanywhere.com) - Korean four-pillars (saju) astrology calculator. Flask + Pillow for dynamic OG cards, Meeus astronomical algorithms for solar-term boundary detection, no database. EN+KR. Solo-built, ad-supported, deployed on PythonAnywhere free tier.",
            "- [GeoInfomatic — Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com) - Isochrone-based Korean neighborhood analyzer. Walking/transit reachability, multi-facility overlay, AI summary. Flask + Leaflet + OSRM. Freemium model.",
        ],
        "pr_title": "Add two production Python (Flask) projects: Saju + GeoInfomatic",
        "pr_body": """Two Flask-based projects in production:

1. **Saju Fortune** — https://tarofortune.pythonanywhere.com
   Korean astrology calculator. Meeus astronomical algorithms, Pillow OG cards, no DB.

2. **GeoInfomatic** — https://geoinfomatic.pythonanywhere.com
   Isochrone neighborhood analyzer. Flask + Leaflet + OSRM walking graph.

Both solo-built on PythonAnywhere free tier. Happy to revise section placement.
""",
    },

    "pluja/awesome-privacy": {
        "section": "##",
        "section_keywords": ["Other", "Tools", "Misc", "Web", "Productivity", "Lifestyle"],
        "additions": [
            "- [Saju Fortune (사주명리 풀이)](https://tarofortune.pythonanywhere.com) — Korean four-pillars astrology calculator. **No signup, no email, no tracking pixels** beyond standard GA. All computation done server-side without storing birth data. Useful as a privacy-respecting alternative to commercial astrology apps that profile users.",
        ],
        "pr_title": "Add Saju Fortune (privacy-respecting Korean astrology calculator)",
        "pr_body": """Adds **Saju Fortune** — a free Korean four-pillars astrology calculator that respects user privacy:

- URL: https://tarofortune.pythonanywhere.com
- **No signup or email** required to use the calculator
- **Birth data not stored** server-side (pure stateless computation)
- No tracking pixels beyond standard Google Analytics
- Alternative to commercial astrology apps that profile users and resell birth data

Solo-built, ad-supported. Happy to revise placement.
""",
    },

    "yudataguy/Awesome-Japanese": {
        "section": "##",
        "section_keywords": ["Culture", "Lifestyle", "Other", "Tools", "Astrology", "Spiritual"],
        "additions": [
            "- [Saju Fortune (사주명리 풀이)](https://tarofortune.pythonanywhere.com) — Korean four-pillars (saju, 사주) astrology — closely related to Japanese **shichu-suimei** (四柱推命). Same 60-day-pillar (六十干支) cycle and same five-element framework as Japanese tradition. Free English + Korean readings.",
        ],
        "pr_title": "Add Saju Fortune — Korean four-pillars (related to Japanese 四柱推命)",
        "pr_body": """Adds **Saju Fortune** — a Korean four-pillars astrology calculator. The Korean tradition (saju, 사주) shares its underlying system with Japanese **shichu-suimei** (四柱推命) and Chinese BaZi (八字) — same 60-day-pillar cycle (六十干支), same five-element framework.

- URL: https://tarofortune.pythonanywhere.com
- Free, no signup
- English + Korean (Japanese translation not yet, but core concepts overlap with shichu-suimei)

For Japanese readers familiar with shichu-suimei, this provides instant access to the same calculation engine. Happy to revise placement.
""",
    },

    "jnv/lists": {
        "section": "##",
        "section_keywords": ["Non-technical"],
        "additions": [
            "- [Awesome Saju](https://github.com/leekyuhaiambox-ops/awesome-saju) — Korean four-pillars (saju, 사주) astrology — calculators, day-pillar references, theory, in Korean and English.",
        ],
        "pr_title": "Add Awesome Saju (Korean four-pillars astrology)",
        "pr_body": """Adds [Awesome Saju](https://github.com/leekyuhaiambox-ops/awesome-saju) — a curated list of resources for Korean four-pillars astrology (사주, saju), an East Asian system also known as BaZi (八字) in Chinese.

The list covers free calculators, 60 day-pillar references, theory (ten gods, twelve life stages, five elements), compatibility tools, and beginner guides — in both Korean and English.

Fits under Non-technical. Happy to revise placement or wording.
""",
    },

    "RunaCapital/awesome-oss-alternatives": {
        "section": "##",
        "section_keywords": ["Useful Links", "Startup List"],
        "additions": [
            "- [GeoInfomatic](https://geoinfomatic.pythonanywhere.com) — Korean isochrone-based neighborhood accessibility analyzer. Bootstrapped freemium alternative to commercial Walk Score / location intelligence tools.",
        ],
        "pr_title": "Add GeoInfomatic to Useful Links (bootstrapped accessibility analyzer)",
        "pr_body": """Adds **GeoInfomatic** to the Useful Links section.

- URL: https://geoinfomatic.pythonanywhere.com
- Acts as a bootstrapped alternative to paid Walk Score / location intelligence APIs for the Korean market
- 100% open data (OSM + Korean public transit)
- Solo-built, freemium model ($7/mo Pro)

Not a traditional startup — happy to revise placement.
""",
    },
}


def gh(token: str, method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Claude",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:800]}


def find_section_index(lines: list[str], keywords: list[str], level_marker: str = "##") -> int | None:
    """level_marker + keyword 포함하는 첫 줄의 다음 위치."""
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith(level_marker + " "):
            continue
        for kw in keywords:
            if kw.lower() in s.lower():
                return i + 1
    return None


def auto_pr(token: str, target: str) -> int:
    if target not in PRESETS:
        print(f"Unknown target: {target}. Known: {list(PRESETS)}")
        return 1
    preset = PRESETS[target]
    owner, repo = target.split("/", 1)

    # 1. Fork
    print(f"1. Fork {target}...")
    code, data = gh(token, "POST", f"https://api.github.com/repos/{owner}/{repo}/forks")
    if code not in (200, 202):
        print(f"   ❌ Fork failed [{code}]: {data}")
        return 1
    fork_full = data.get("full_name", f"{OUR_USER}/{repo}")
    default_branch = data.get("default_branch", "main")
    print(f"   ✓ Fork: {fork_full} (branch: {default_branch})")
    time.sleep(6)

    # 2. Get README
    print("\n2. Get README from fork...")
    code, data = gh(token, "GET", f"https://api.github.com/repos/{fork_full}/contents/README.md")
    if code != 200:
        print(f"   ❌ Get README failed: {data}")
        return 1
    sha = data["sha"]
    content = base64.b64decode(data["content"]).decode("utf-8")
    print(f"   ✓ SHA: {sha[:10]}, length: {len(content)}")

    # 3. Find section + insert
    print("\n3. Find section + insert...")
    lines = content.split("\n")
    insert_at = find_section_index(lines, preset["section_keywords"], preset.get("section", "##"))
    if insert_at is None:
        # h3 폴백
        insert_at = find_section_index(lines, preset["section_keywords"], "###")
    if insert_at is None:
        print(f"   ❌ section {preset['section_keywords']} 미발견")
        return 1
    print(f"   ✓ Insert at line {insert_at + 1}")

    # insert 직후 첫 빈 줄까지 skip (intro 텍스트가 있을 경우)
    j = insert_at
    while j < len(lines) and not lines[j].strip():
        j += 1
    insert_at = j

    new_lines = lines[:insert_at] + [""] + list(preset["additions"]) + lines[insert_at:]
    new_content = "\n".join(new_lines)
    print(f"   ✓ New length: {len(new_content)} (+{len(new_content) - len(content)} chars)")

    # 4. Commit
    print("\n4. Commit to fork...")
    b64 = base64.b64encode(new_content.encode("utf-8")).decode()
    body = {
        "message": preset["pr_title"],
        "content": b64,
        "sha": sha,
        "branch": default_branch,
    }
    code, data = gh(token, "PUT", f"https://api.github.com/repos/{fork_full}/contents/README.md", body)
    if code not in (200, 201):
        print(f"   ❌ Commit failed [{code}]: {data}")
        return 1
    print(f"   ✓ Commit SHA: {data['commit']['sha'][:10]}")

    # 5. Open PR
    print("\n5. Open PR...")
    pr = {
        "title": preset["pr_title"],
        "head": f"{OUR_USER}:{default_branch}",
        "base": default_branch,
        "body": preset["pr_body"],
    }
    code, data = gh(token, "POST", f"https://api.github.com/repos/{owner}/{repo}/pulls", pr)
    if code in (200, 201):
        print(f"   ✅ PR opened: {data['html_url']}")
        return 0
    else:
        print(f"   ❌ PR failed [{code}]: {data}")
        return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="hemanth/awesome-pwa")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    args = ap.parse_args()
    if not args.token:
        print("Need --token <ghp> or GITHUB_TOKEN env")
        sys.exit(1)
    sys.exit(auto_pr(args.token, args.target))
