"""
자동 KPI 수집 — 매일 GitHub Actions가 실행해서 일별 성과 dashboard 갱신.

수집 데이터:
  1. tarofortune /api/analytics/daily — referral·email capture 카운트
  2. Mastodon @tarosaju 최근 toot 통계 (favs, boosts, replies)
  3. Lemmy 게시물 점수 (votes·comments)
  4. Dev.to article 통계
  5. GitHub Actions 봇 실행 이력
  6. IndexNow 누적 제출 수 (state 파일)

결과:
  marketing/shared/state/daily_kpi/YYYY-MM-DD.json
  marketing/shared/state/daily_kpi/_latest.json  (symlink 또는 copy)

실행:
  python analytics_collector.py
  python analytics_collector.py --json-only   # stdout으로 JSON만

환경변수:
  CRON_SECRET — tarofortune /api/analytics/daily 인증
  MASTODON_INSTANCE, MASTODON_ACCESS_TOKEN
  LEMMY_INSTANCE, LEMMY_USERNAME, LEMMY_PASSWORD (또는 그냥 익명 조회)
  DEVTO_API_KEY (선택)
  GITHUB_TOKEN (선택, 봇 실행 이력용)
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, date, timedelta
from pathlib import Path


UA = "Mozilla/5.0 (X11; Linux x86_64) Marketing-KPI-Collector"


def _req(url: str, headers: dict | None = None, timeout: int = 30) -> dict | list | str:
    headers = {"User-Agent": UA, **(headers or {})}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except Exception as e:
        return {"_error": str(e)[:120]}


def collect_tarofortune_analytics() -> dict:
    """tarofortune /api/analytics/daily 호출."""
    secret = os.environ.get("CRON_SECRET", "")
    if not secret:
        return {"_error": "CRON_SECRET env missing — set on PA WSGI"}
    url = "https://tarofortune.pythonanywhere.com/api/analytics/daily"
    return _req(url, headers={"X-Cron-Secret": secret})


def collect_mastodon() -> dict:
    """@tarosaju 최근 toot 10건 통계."""
    instance = os.environ.get("MASTODON_INSTANCE", "mastodon.social")
    acct = _req(f"https://{instance}/api/v1/accounts/lookup?acct=tarosaju")
    if not isinstance(acct, dict) or "id" not in acct:
        return {"_error": "account lookup failed", "_raw": acct}
    statuses = _req(f"https://{instance}/api/v1/accounts/{acct['id']}/statuses?limit=20")
    if not isinstance(statuses, list):
        return {"_error": "statuses fetch failed"}
    out = {
        "followers": acct.get("followers_count", 0),
        "total_statuses": acct.get("statuses_count", 0),
        "recent_count": len(statuses),
        "total_favs": sum(s.get("favourites_count", 0) for s in statuses),
        "total_boosts": sum(s.get("reblogs_count", 0) for s in statuses),
        "total_replies": sum(s.get("replies_count", 0) for s in statuses),
        "top_toot": None,
    }
    if statuses:
        top = max(statuses, key=lambda s: s.get("favourites_count", 0) + s.get("reblogs_count", 0) * 2)
        out["top_toot"] = {
            "url": top.get("url"),
            "favs": top.get("favourites_count", 0),
            "boosts": top.get("reblogs_count", 0),
            "snippet": (top.get("content", "") or "")[:160],
        }
    return out


def collect_lemmy() -> dict:
    """u/tarofortune 최근 게시 점수."""
    instance = os.environ.get("LEMMY_INSTANCE", "lemmy.world")
    user_data = _req(f"https://{instance}/api/v3/user?username=tarofortune&sort=New&limit=20")
    if not isinstance(user_data, dict) or "posts" not in user_data:
        return {"_error": "user lookup failed"}
    posts = user_data["posts"]
    out = {
        "post_count": len(posts),
        "total_score": sum(p.get("counts", {}).get("score", 0) for p in posts),
        "total_comments": sum(p.get("counts", {}).get("comments", 0) for p in posts),
        "recent_posts": [],
    }
    for p in posts[:10]:
        out["recent_posts"].append({
            "url": f"https://{instance}/post/{p['post']['id']}",
            "title": p["post"]["name"][:100],
            "score": p.get("counts", {}).get("score", 0),
            "comments": p.get("counts", {}).get("comments", 0),
            "community": p.get("community", {}).get("name", ""),
            "published": p["post"].get("published", "")[:10],
        })
    return out


def collect_devto() -> dict:
    """@tarofortune 공개 article 통계."""
    data = _req("https://dev.to/api/articles?username=tarofortune&per_page=20")
    if not isinstance(data, list):
        return {"_error": "devto fetch failed"}
    out = {
        "article_count": len(data),
        "total_reactions": sum(a.get("positive_reactions_count", 0) for a in data),
        "total_comments": sum(a.get("comments_count", 0) for a in data),
        "total_reading_time": sum(a.get("reading_time_minutes", 0) for a in data),
        "recent": [],
    }
    for a in data[:10]:
        out["recent"].append({
            "title": a.get("title", "")[:100],
            "url": a.get("url"),
            "reactions": a.get("positive_reactions_count", 0),
            "comments": a.get("comments_count", 0),
            "published": a.get("published_at", "")[:10],
        })
    return out


def collect_github_actions() -> dict:
    """multi-site-bot workflow 최근 실행."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return {"_skip": "no GITHUB_TOKEN"}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    runs = _req(
        "https://api.github.com/repos/leekyuhaiambox-ops/saju-platform/actions/runs?per_page=10",
        headers=headers,
    )
    if not isinstance(runs, dict):
        return {"_error": "fetch failed"}
    out = {
        "total": runs.get("total_count", 0),
        "recent": [],
    }
    for r in runs.get("workflow_runs", [])[:10]:
        out["recent"].append({
            "name": r.get("name"),
            "status": r.get("status"),
            "conclusion": r.get("conclusion"),
            "created_at": r.get("created_at"),
            "html_url": r.get("html_url"),
        })
    return out


def collect_indexnow() -> dict:
    """state 파일 기반 누적 IndexNow 제출 수."""
    state_dir = Path(__file__).parent / "state"
    indexnow_log = state_dir / "indexnow_submissions.json"
    if not indexnow_log.exists():
        return {"cumulative_urls": 0, "last_submission": None}
    try:
        data = json.loads(indexnow_log.read_text(encoding="utf-8"))
        return {
            "cumulative_urls": sum(data.get("counts", {}).values()),
            "last_submission": data.get("last_submission"),
            "by_site": data.get("counts", {}),
        }
    except Exception as e:
        return {"_error": str(e)}


def collect_all() -> dict:
    """전체 KPI 한 번에 수집."""
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "date": date.today().isoformat(),
        "tarofortune": collect_tarofortune_analytics(),
        "mastodon": collect_mastodon(),
        "lemmy": collect_lemmy(),
        "devto": collect_devto(),
        "github_actions": collect_github_actions(),
        "indexnow": collect_indexnow(),
    }


def save_daily(kpi: dict) -> Path:
    """daily KPI JSON 저장 + _latest.json 갱신."""
    state_dir = Path(__file__).parent / "state" / "daily_kpi"
    state_dir.mkdir(parents=True, exist_ok=True)
    today_path = state_dir / f"{kpi['date']}.json"
    today_path.write_text(json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = state_dir / "_latest.json"
    latest.write_text(json.dumps(kpi, ensure_ascii=False, indent=2), encoding="utf-8")
    return today_path


def render_summary(kpi: dict) -> str:
    """사람이 읽기 좋은 요약."""
    lines = [f"=== Daily KPI · {kpi['date']} ===", ""]
    m = kpi.get("mastodon", {})
    if "_error" not in m:
        lines.append(f"Mastodon @tarosaju: {m.get('total_statuses', 0)} toots, "
                     f"{m.get('followers', 0)} followers, "
                     f"recent 20: {m.get('total_favs', 0)} favs / "
                     f"{m.get('total_boosts', 0)} boosts")
    L = kpi.get("lemmy", {})
    if "_error" not in L:
        lines.append(f"Lemmy: {L.get('post_count', 0)} posts, "
                     f"total score {L.get('total_score', 0)}, "
                     f"comments {L.get('total_comments', 0)}")
    d = kpi.get("devto", {})
    if "_error" not in d:
        lines.append(f"Dev.to: {d.get('article_count', 0)} articles, "
                     f"{d.get('total_reactions', 0)} reactions")
    t = kpi.get("tarofortune", {})
    if "_error" not in t and "_skip" not in t:
        lines.append(f"tarofortune: {t.get('referral_count', 0)} referrals, "
                     f"{t.get('email_count', 0)} emails today")
        if t.get("by_ref"):
            lines.append(f"  by ref: {dict(list(t['by_ref'].items())[:5])}")
    ga = kpi.get("github_actions", {})
    if "recent" in ga:
        last_runs = ga["recent"][:3]
        lines.append(f"GitHub Actions: {len(last_runs)} recent runs")
        for r in last_runs:
            lines.append(f"  [{r.get('conclusion')}] {r.get('name')} @ {r.get('created_at', '')[:16]}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-only", action="store_true", help="stdout으로 JSON만")
    ap.add_argument("--no-save", action="store_true", help="파일 저장 안 함")
    args = ap.parse_args()

    kpi = collect_all()

    if not args.no_save:
        path = save_daily(kpi)
        if not args.json_only:
            print(f"Saved: {path}")

    if args.json_only:
        print(json.dumps(kpi, ensure_ascii=False, indent=2))
    else:
        print()
        print(render_summary(kpi))


if __name__ == "__main__":
    main()
