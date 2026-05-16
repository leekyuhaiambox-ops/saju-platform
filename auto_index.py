"""일일 자동 색인 제출 — IndexNow (Bing·Yandex·Naver·Seznam) + Google sitemap ping.

PythonAnywhere Scheduled Tasks 또는 외부 cron에서 매일 호출.
"""
from __future__ import annotations
import os
import sys
from urllib import request, parse
from datetime import date, timedelta

HOST = os.environ.get("SITE_HOST", "tarofortune.pythonanywhere.com")
SITEMAP = f"https://{HOST}/sitemap.xml"


def submit_indexnow():
    """IndexNow에 오늘/내일 일진 페이지 + 핵심 페이지 제출."""
    from saju.indexnow import submit_urls
    base = f"https://{HOST}"
    today = date.today()
    urls = [
        base + "/",
        base + "/today",
        base + f"/today/{today.isoformat()}",
        base + f"/today/{(today + timedelta(days=1)).isoformat()}",
        base + "/weekly",
        base + "/monthly",
        base + "/en/",
        base + "/en/today",
        base + f"/en/today/{today.isoformat()}",
        base + "/feed.xml",
        base + "/en/feed.xml",
    ]
    return submit_urls(HOST, urls)


def ping_google_sitemap():
    """Google sitemap ping. 2023년 deprecated 됐지만 일부 서비스가 아직 응답."""
    url = "https://www.google.com/ping?sitemap=" + parse.quote(SITEMAP)
    try:
        with request.urlopen(url, timeout=15) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", 0)


def ping_bing_sitemap():
    """Bing sitemap ping."""
    url = "https://www.bing.com/ping?sitemap=" + parse.quote(SITEMAP)
    try:
        with request.urlopen(url, timeout=15) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", 0)


def main():
    print("=== Auto-index submission ===")
    r1 = submit_indexnow()
    print(f"IndexNow: {r1}")
    r2 = ping_google_sitemap()
    print(f"Google ping: {r2}")
    r3 = ping_bing_sitemap()
    print(f"Bing ping: {r3}")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
