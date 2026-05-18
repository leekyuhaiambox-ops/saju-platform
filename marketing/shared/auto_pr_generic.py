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
