"""
awesome-civic-tech 자동 PR 생성 스크립트
========================================

brandonhimpfen/awesome-civic-tech 에 currency-map + geoinfomatic 추가하는 PR을
fork + commit + open PR 전 과정 자동 실행.

필요: GITHUB_TOKEN 환경변수 또는 인자
실행: python auto_pr_awesome_civic_tech.py <token>
"""
from __future__ import annotations
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request


ORIG_OWNER = "brandonhimpfen"
REPO = "awesome-civic-tech"
OUR_USER = "leekyuhaiambox-ops"

ADDITIONS = """- [Gyeonggi Currency Map](https://gyeonggi-currency-map.web.app) - Interactive PWA mapping municipal local-currency merchant locations across all 31 cities of Gyeonggi Province, South Korea. Built on public open data with business-type filters, real-time "open now" toggle, and KakaoTalk share. Installable PWA, React + Vite + Leaflet on Firebase Hosting.
- [GeoInfomatic - Living Zone Accessibility](https://geoinfomatic.pythonanywhere.com) - Isochrone-based neighborhood accessibility analyzer for South Korea. Walking or transit isochrones (10/20/30/45 min) overlaid with 8 facility types (subway, school, hospital, mart, park, gym, pharmacy, library, cafe). 100-point composite score with AI summary. No real-estate listings."""

PR_BODY = """Adds two civic-tech projects from Korea to the **Civic Apps & Tools** section.

1. **Gyeonggi Currency Map** — https://gyeonggi-currency-map.web.app
   Interactive PWA mapping merchants that accept Gyeonggi Province's municipal local currency across 31 cities (14M residents). Uses the province's public open API. React + Vite + Leaflet on Firebase Hosting, installable PWA.

2. **GeoInfomatic — Living Zone Accessibility** — https://geoinfomatic.pythonanywhere.com
   Isochrone-based neighborhood accessibility analyzer for moving / urban-planning decisions. Walking or transit isochrones (10–45 min) overlaid with 8 facility types. No real-estate listings — pure accessibility.

Both are solo-developed, freemium / ad-supported (no investor money), and use only open data + free infrastructure tiers. They fit the spirit of the list.

Happy to revise if a different section is preferred.
"""


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
        return e.code, {"error": e.read().decode(errors="replace")[:600]}


def main(token: str):
    # 1. Fork
    print("1. Fork repo...")
    code, data = gh(token, "POST", f"https://api.github.com/repos/{ORIG_OWNER}/{REPO}/forks")
    if code not in (200, 202):
        print(f"   ❌ Fork failed [{code}]: {data}")
        return 1
    fork_full = data.get("full_name", f"{OUR_USER}/{REPO}")
    print(f"   ✓ Fork: {fork_full} ({code})")
    print("   Waiting 6s for fork to settle...")
    time.sleep(6)

    # 2. Get README from fork
    print("\n2. Get README from fork...")
    code, data = gh(token, "GET", f"https://api.github.com/repos/{fork_full}/contents/README.md")
    if code != 200:
        print(f"   ❌ Get README failed: {data}")
        return 1
    sha = data["sha"]
    content = base64.b64decode(data["content"]).decode("utf-8")
    print(f"   ✓ SHA: {sha}, length: {len(content)}")

    # 3. Modify
    print("\n3. Modify content...")
    lines = content.split("\n")
    new_lines: list[str] = []
    inserted = False
    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and line.strip() == "## Civic Apps & Tools":
            # 다음 줄이 빈 줄이면 그 다음 (intro 텍스트 가능성)에 우리 항목 추가
            # 가장 안전: section 헤더 직후에 한 빈 줄 + 우리 항목들 추가
            new_lines.append("")
            new_lines.append(ADDITIONS)
            inserted = True

    if not inserted:
        # Maybe pure h3 instead of h2; try alternatives
        print("   ⚠️ '## Civic Apps & Tools' 미발견, fallback section 시도")
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if not inserted and "Civic Apps" in line and line.startswith("#"):
                new_lines.append("")
                new_lines.append(ADDITIONS)
                inserted = True

    if not inserted:
        print("   ❌ section not found at all")
        return 1

    new_content = "\n".join(new_lines)
    print(f"   ✓ New length: {len(new_content)} (+{len(new_content) - len(content)} chars)")

    # 4. Commit to fork
    print("\n4. Commit to fork...")
    b64 = base64.b64encode(new_content.encode("utf-8")).decode()
    body = {
        "message": "Add Gyeonggi Currency Map and GeoInfomatic to Civic Apps & Tools",
        "content": b64,
        "sha": sha,
    }
    code, data = gh(token, "PUT", f"https://api.github.com/repos/{fork_full}/contents/README.md", body)
    if code not in (200, 201):
        print(f"   ❌ Commit failed [{code}]: {data}")
        return 1
    new_sha = data["commit"]["sha"]
    print(f"   ✓ Commit SHA: {new_sha[:10]}")

    # 5. Open PR
    print("\n5. Open PR...")
    pr = {
        "title": "Add Gyeonggi Currency Map and GeoInfomatic to Civic Apps & Tools",
        "head": f"{OUR_USER}:main",
        "base": "main",
        "body": PR_BODY,
    }
    code, data = gh(token, "POST", f"https://api.github.com/repos/{ORIG_OWNER}/{REPO}/pulls", pr)
    if code in (200, 201):
        print(f"   ✅ PR opened: {data['html_url']}")
        return 0
    else:
        print(f"   ❌ PR failed [{code}]: {data}")
        return 1


if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("Usage: python auto_pr_awesome_civic_tech.py <token>")
        sys.exit(1)
    sys.exit(main(token))
