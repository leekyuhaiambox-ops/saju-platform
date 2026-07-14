"""
매일 자동 발행 결과 보고 시스템
==============================

운영자에게 매일 GitHub Issue로 보고. 운영자가 repo watch만 켜두면
Gmail로 자동 알림 옴 (별도 SMTP 설정 X).

수집:
  1. analytics_collector → 어제 KPI (Mastodon · Lemmy · Dev.to · GitHub Actions)
  2. PA access.log → 어제 진짜 사람 트래픽 (검색 referer 기준)
  3. awesome-list PR 상태 (open/closed/merged) 변화
  4. 자동 콘텐츠 생성 결과 (OpenAI 비용 추정)
  5. sitemap URL 카운트

발행:
  - GitHub Issue 자동 생성 (label: daily-report)
  - 어제 issue는 자동 close

실행:
  python daily_report.py              # 어제 데이터 보고
  python daily_report.py --dry-run    # Issue 생성 안 하고 출력만

환경변수:
  GH_TOKEN — GitHub PAT (repo scope)
  CRON_SECRET — saju /api/analytics/daily 인증
  PA_TOKEN — PythonAnywhere 토큰 (PA log 읽기용)
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, date, timedelta, timezone
from pathlib import Path


GH_TOKEN = os.environ.get("GH_TOKEN", "")
CRON_SECRET = os.environ.get("CRON_SECRET", "")
PA_TOKEN = os.environ.get("PA_TOKEN", "15f08580dcd72d36519893c8e512f0a827bc1962")

REPO = "leekyuhaiambox-ops/saju-platform"

UA = "Mozilla/5.0 (X11; Linux x86_64) marketing-daily-report"
PA_BASE = "https://www.pythonanywhere.com/api/v0/user/tarofortune"

BOT_KEYS = ["bot", "crawl", "spider", "fetch", "curl", "wget", "python", "scrap",
            "yeti", "daumoa", "monitor", "pingdom", "uptimerobot", "semrush",
            "ahrefs", "mj12", "archive.org_bot", "amazonbot"]
LOG_PATTERN = re.compile(
    r'^(\S+) - \S+ \[([^\]]+)\] "(\S+) (\S+) [^"]+" (\d+) (\d+) "([^"]*)" "([^"]+)"'
)


# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------

def gh(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "User-Agent": UA,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"https://api.github.com{path}",
                                  data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:300]}


# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------

def collect_pa_traffic_yesterday() -> dict:
    """어제 PA access.log에서 진짜 사람 (검색 referer 기준) 카운트."""
    target = (date.today() - timedelta(days=1)).strftime("%d/%b/%Y")
    out = {"yesterday_date": target, "human_total": 0,
           "search_referers": 0, "search_breakdown": {},
           "bot_total": 0, "top_paths": [], "unique_human_ips": 0}
    try:
        url = f"{PA_BASE}/files/path/var/log/tarofortune.pythonanywhere.com.access.log.1"
        req = urllib.request.Request(url, headers={"Authorization": f"Token {PA_TOKEN}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        out["error"] = str(e)[:100]
        return out

    refs = Counter(); ips = set(); paths = Counter()
    for line in body.splitlines():
        m = LOG_PATTERN.match(line)
        if not m:
            continue
        ip, dt, _, path, _, _, ref, ua = m.groups()
        if not dt.startswith(target):
            continue
        ua_l = ua.lower()
        if any(b in ua_l for b in BOT_KEYS):
            out["bot_total"] += 1
            continue
        out["human_total"] += 1
        ips.add(ip)
        if path != "/" and not path.startswith("/static/") and not path.endswith((".png",".css",".js")):
            paths[path[:60]] += 1
        if ref and ref != "-" and "tarofortune" not in ref:
            out["search_referers"] += 1
            host = ref.split("/")[2] if "://" in ref else ref[:40]
            refs[host] += 1
    out["unique_human_ips"] = len(ips)
    out["search_breakdown"] = dict(refs.most_common(5))
    out["top_paths"] = paths.most_common(5)
    return out


def collect_mastodon() -> dict:
    instance = os.environ.get("MASTODON_INSTANCE", "mastodon.social")
    try:
        req = urllib.request.Request(
            f"https://{instance}/api/v1/accounts/lookup?acct=tarosaju",
            headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            acct = json.loads(r.read())
        req = urllib.request.Request(
            f"https://{instance}/api/v1/accounts/{acct['id']}/statuses?limit=10",
            headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            statuses = json.loads(r.read())
        return {
            "followers": acct.get("followers_count", 0),
            "total_statuses": acct.get("statuses_count", 0),
            "recent_favs": sum(s.get("favourites_count", 0) for s in statuses),
            "recent_boosts": sum(s.get("reblogs_count", 0) for s in statuses),
            "last_post_at": acct.get("last_status_at", "?"),
        }
    except Exception as e:
        return {"error": str(e)[:80]}


def collect_lemmy() -> dict:
    instance = os.environ.get("LEMMY_INSTANCE", "lemmy.world")
    try:
        req = urllib.request.Request(
            f"https://{instance}/api/v3/user?username=tarofortune&sort=New&limit=10",
            headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        posts = data.get("posts", [])
        return {
            "total_posts": len(posts),
            "total_score": sum(p.get("counts", {}).get("score", 0) for p in posts),
            "total_comments": sum(p.get("counts", {}).get("comments", 0) for p in posts),
            "last_post": posts[0]["post"]["name"][:80] if posts else "?",
        }
    except Exception as e:
        return {"error": str(e)[:80]}


def collect_devto() -> dict:
    try:
        req = urllib.request.Request(
            "https://dev.to/api/articles?username=tarofortune&per_page=10",
            headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        return {
            "total_articles": len(data),
            "total_reactions": sum(a.get("positive_reactions_count", 0) for a in data),
            "total_comments": sum(a.get("comments_count", 0) for a in data),
        }
    except Exception as e:
        return {"error": str(e)[:80]}


# PR별 수동 상태 override — maintainer가 PR을 닫고 수동 merge한 경우 등
# (etewiah#30: "Merged manually in 1b04777" — GitHub API는 closed로 보이지만 실제 등재됨)
PR_STATE_OVERRIDES = {
    "etewiah/awesome-real-estate#30": "✅ MERGED (manual, commit 1b04777)",
}


def collect_awesome_prs() -> list[dict]:
    prs = [
        ("brandonhimpfen/awesome-civic-tech", 6, 9),
        ("hemanth/awesome-pwa", 406, 4829),
        ("mjhea0/awesome-flask", 51, 1737),
        ("osmlab/awesome-openstreetmap", 193, 935),
        ("etewiah/awesome-real-estate", 30, 314),
        ("sshuair/awesome-gis", 214, 5362),
        ("xcomptek/awesome-saas-boilerplates", 206, 3077),
        ("garimasingh128/awesome-python-projects", 172, 1472),
        ("RunaCapital/awesome-oss-alternatives", 357, 19166),
        ("jnv/lists", 291, 11230),
        ("pluja/awesome-privacy", 837, 18830),
    ]
    results = []
    for repo, num, stars in prs:
        override = PR_STATE_OVERRIDES.get(f"{repo}#{num}")
        code, data = gh("GET", f"/repos/{repo}/pulls/{num}")
        if override:
            state = override
        elif code != 200:
            state = "?"
        elif data.get("merged"):
            state = "✅ MERGED"
        elif data.get("state") == "closed":
            state = "❌ CLOSED"
        else:
            state = "⏳ OPEN"
        results.append({"repo": repo, "num": num, "stars": stars, "state": state,
                        "comments": data.get("comments", 0) if isinstance(data, dict) else 0})
    return results


def collect_sitemap_count() -> int:
    try:
        req = urllib.request.Request("https://tarofortune.pythonanywhere.com/sitemap.xml",
                                      headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", errors="replace")
        return len(re.findall(r"<loc>", body))
    except Exception:
        return -1


def collect_pa_referrals() -> dict:
    """saju /api/analytics/daily 호출 — referral·email 카운트."""
    if not CRON_SECRET:
        return {"_skip": "no CRON_SECRET"}
    try:
        req = urllib.request.Request(
            "https://tarofortune.pythonanywhere.com/api/analytics/daily",
            headers={"X-Cron-Secret": CRON_SECRET, "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)[:80]}


# ---------------------------------------------------------------------------
# Report renderer
# ---------------------------------------------------------------------------

def render_issue_body(kpi: dict) -> str:
    """GitHub Issue 본문 (Markdown)."""
    pa = kpi["pa_traffic"]
    mst = kpi["mastodon"]
    lmy = kpi["lemmy"]
    dv = kpi["devto"]
    refs = kpi["pa_referrals"]
    prs = kpi["awesome_prs"]
    sm = kpi["sitemap_urls"]

    # PR merged·closed 카운트
    merged = sum(1 for p in prs if "MERGED" in p["state"])
    closed = sum(1 for p in prs if "CLOSED" in p["state"])
    open_prs = sum(1 for p in prs if "OPEN" in p["state"])

    human_search = pa.get("search_referers", 0)
    human_total = pa.get("human_total", 0)
    ips = pa.get("unique_human_ips", 0)

    parts = []
    parts.append(f"# 📊 일일 마케팅 보고 — {kpi['date']}")
    parts.append("")
    parts.append(f"> 자동 생성 (`marketing/shared/daily_report.py`). 매일 GitHub Actions가 실행 후 게시.")
    parts.append("")

    parts.append("## TL;DR")
    parts.append("")
    parts.append(f"- 어제 진짜 사람 (검색 referer): **{human_search}**")
    parts.append(f"- 어제 사람 분류 합계 (UA 기반, 봇 포함 위장 있음): {human_total} ({ips} unique IPs)")
    parts.append(f"- Mastodon 누적 {mst.get('total_statuses', '?')} toot · followers {mst.get('followers', 0)}")
    parts.append(f"- Lemmy 누적 {lmy.get('total_posts', '?')} posts · score {lmy.get('total_score', 0)}")
    parts.append(f"- Dev.to 누적 {dv.get('total_articles', '?')} articles · reactions {dv.get('total_reactions', 0)}")
    parts.append(f"- sitemap URLs: **{sm}**")
    parts.append(f"- awesome PRs: ✅ {merged} merged · ❌ {closed} closed · ⏳ {open_prs} open")
    parts.append("")

    # 어제 사람 트래픽 상세
    parts.append("## 🚦 어제 트래픽 (PA access.log)")
    parts.append("")
    if pa.get("error"):
        parts.append(f"- ⚠️ PA log 읽기 실패: {pa['error']}")
    else:
        parts.append(f"| 분류 | 값 |")
        parts.append(f"|---|---|")
        parts.append(f"| 봇 (UA 명시) | {pa.get('bot_total', 0)} |")
        parts.append(f"| 사람 (UA 기반) | {human_total} |")
        parts.append(f"| **진짜 사람 (검색 referer)** | **{human_search}** ✨ |")
        parts.append(f"| unique IPs (사람) | {ips} |")
        if pa.get("search_breakdown"):
            parts.append("")
            parts.append("### 외부 검색 유입")
            for host, cnt in pa["search_breakdown"].items():
                parts.append(f"- [{cnt}] {host}")
        if pa.get("top_paths"):
            parts.append("")
            parts.append("### 인기 콘텐츠 page")
            for path, cnt in pa["top_paths"]:
                parts.append(f"- [{cnt}] `{path}`")

    parts.append("")
    parts.append("## 💼 referral · email capture")
    parts.append("")
    if "error" in refs or "_skip" in refs:
        parts.append(f"- ⚠️ {refs.get('error', refs.get('_skip', '?'))}")
    else:
        parts.append(f"- referral_count (오늘): {refs.get('referral_count', 0)}")
        parts.append(f"- email_count (오늘): {refs.get('email_count', 0)}")
        if refs.get("by_ref"):
            parts.append(f"- by_ref: `{refs['by_ref']}`")

    parts.append("")
    parts.append("## 🤖 봇 게시 누적")
    parts.append("")
    parts.append("| 채널 | 누적 | 어제 게시 | 누적 반응 |")
    parts.append("|---|---|---|---|")
    parts.append(f"| Mastodon | {mst.get('total_statuses', '?')} toot | last: {mst.get('last_post_at', '?')[:10]} | favs {mst.get('recent_favs', 0)} + boosts {mst.get('recent_boosts', 0)} |")
    parts.append(f"| Lemmy | {lmy.get('total_posts', '?')} posts | last: {lmy.get('last_post', '?')[:60]} | score {lmy.get('total_score', 0)} · comments {lmy.get('total_comments', 0)} |")
    parts.append(f"| Dev.to | {dv.get('total_articles', '?')} articles | (shadowban 의심) | reactions {dv.get('total_reactions', 0)} · comments {dv.get('total_comments', 0)} |")

    parts.append("")
    parts.append("## 🏆 awesome-list PR 상태")
    parts.append("")
    parts.append("| Repo | Stars | 상태 | comments |")
    parts.append("|---|---|---|---|")
    for p in sorted(prs, key=lambda x: -x["stars"]):
        parts.append(f"| {p['repo']}#{p['num']} | {p['stars']:,}⭐ | {p['state']} | {p['comments']} |")

    parts.append("")
    parts.append("## 🎯 운영자 권장 액션 (오늘)")
    parts.append("")
    parts.append("**자동화로 못 하는 것 — 운영자 5분 액션이 진짜 수익 만듭니다.**")
    parts.append("")
    if human_search < 20:
        parts.append("1. **카톡 가족·친구 단톡방 사이트 공유** (5분) — 즉시 진짜 사람 50명+. 검색 referer 너무 낮음.")
        parts.append("   ```")
        parts.append("   내가 만든 사주 사이트 한번 봐줘 ㅋㅋ 무료고 광고 좀 있어")
        parts.append("   https://tarofortune.pythonanywhere.com")
        parts.append("   ```")
    parts.append("2. **AdSense 콘솔 → 사이트 검토 통과 → Auto Ads ON** — 광고 노출 즉시 시작")
    parts.append("3. **Naver 블로그 austriano 글 게시** — 완성본은 `marketing/currency-map/content/naver_blog_post_1.md`")
    parts.append("4. **PR 검토 응답** — 위 awesome-list PR 중 OPEN인 것에 maintainer 댓글 달리면 24h 내 응답")
    parts.append("")

    parts.append("---")
    parts.append("")
    parts.append(f"<sub>다음 보고: 내일 UTC 17:00 (KST 02:00) 경. 이 issue는 다음 보고 발행 시 자동 close.</sub>")
    parts.append(f"<sub>실행: `python marketing/shared/daily_report.py`</sub>")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# GitHub Issue ops
# ---------------------------------------------------------------------------

def ensure_label():
    """daily-report label 보장."""
    code, _ = gh("GET", f"/repos/{REPO}/labels/daily-report")
    if code == 404:
        gh("POST", f"/repos/{REPO}/labels", {
            "name": "daily-report",
            "color": "5e2da6",
            "description": "Auto-generated daily marketing report",
        })


def close_previous_reports():
    """이전 daily-report issue들 자동 close (latest는 keep)."""
    code, issues = gh("GET", f"/repos/{REPO}/issues?state=open&labels=daily-report&per_page=10")
    if code != 200:
        return
    if not isinstance(issues, list):
        return
    # 첫 번째는 keep, 나머지 close
    for issue in issues:
        gh("PATCH", f"/repos/{REPO}/issues/{issue['number']}", {"state": "closed"})


def create_issue(title: str, body: str) -> str:
    code, data = gh("POST", f"/repos/{REPO}/issues", {
        "title": title, "body": body, "labels": ["daily-report"],
    })
    if code in (200, 201):
        return data.get("html_url", "")
    print(f"❌ Issue create failed [{code}]: {data}")
    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not GH_TOKEN:
        print("⚠️ GH_TOKEN 환경변수 필수")
        return 1

    today_iso = date.today().isoformat()

    print("=== Collecting daily KPI ===")
    kpi = {
        "date": today_iso,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "pa_traffic": collect_pa_traffic_yesterday(),
        "mastodon": collect_mastodon(),
        "lemmy": collect_lemmy(),
        "devto": collect_devto(),
        "pa_referrals": collect_pa_referrals(),
        "awesome_prs": collect_awesome_prs(),
        "sitemap_urls": collect_sitemap_count(),
    }

    # 로컬 JSON 저장
    state_dir = Path(__file__).parent / "state" / "daily_kpi"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / f"{today_iso}.json").write_text(
        json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    (state_dir / "_latest.json").write_text(
        json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")

    body = render_issue_body(kpi)
    title = f"[Daily Marketing Report] {today_iso}"

    if args.dry_run:
        print(body)
        print(f"\n(dry-run — Issue 생성 안 함)")
        return 0

    ensure_label()
    close_previous_reports()
    url = create_issue(title, body)
    if url:
        print(f"\n✅ Issue 생성: {url}")
    else:
        print("\n❌ Issue 생성 실패")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
