"""서버 사이드 방문자 분석 — GA 없이 자체 로깅.

SQLite 없이 일별 JSONL append 방식 (PythonAnywhere 무료티어 디스크 절약).
- 페이지뷰, 유입 경로(referer), UTM, 디바이스, 국가추정(언어), 봇 필터
- /admin/stats?key=SECRET 로 대시보드 조회

설계 원칙: 가볍게. 요청당 파일 1줄 append (CPU 거의 0).
"""
from __future__ import annotations
import os
import json
import re
from datetime import datetime, date, timedelta
from collections import Counter, defaultdict
from threading import Lock

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_analytics")
os.makedirs(_LOG_DIR, exist_ok=True)
_lock = Lock()

# 봇 User-Agent 패턴 (분석에서 제외)
_BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|whatsapp|telegram|"
    r"headless|python-urllib|curl|wget|monitor|uptime|pingdom|lighthouse|"
    r"googlebot|yeti|daum|naver|adsbot|mediapartners",
    re.IGNORECASE,
)

# 봇이지만 추적하고 싶은 검색엔진 크롤러 (별도 집계)
_SEARCH_CRAWLER_RE = re.compile(
    r"googlebot|yeti|naver|daumoa|bingbot|yandexbot|applebot|duckduckbot|baiduspider",
    re.IGNORECASE,
)


def _today_file(d: date = None) -> str:
    d = d or date.today()
    return os.path.join(_LOG_DIR, f"{d.isoformat()}.jsonl")


def _classify_referer(ref: str) -> str:
    """유입 경로 분류."""
    if not ref or ref == "-":
        return "direct"
    r = ref.lower()
    sources = {
        "naver": "naver", "google": "google", "daum": "daum", "bing": "bing",
        "yahoo": "yahoo", "yandex": "yandex", "duckduckgo": "duckduckgo",
        "kakao": "kakaotalk", "instagram": "instagram", "facebook": "facebook",
        "twitter": "twitter/x", "t.co": "twitter/x", "x.com": "twitter/x",
        "lemmy": "lemmy", "mastodon": "mastodon", "dev.to": "dev.to",
        "pinterest": "pinterest", "youtube": "youtube", "reddit": "reddit",
        "tistory": "tistory", "dcinside": "dcinside", "theqoo": "theqoo",
        "instiz": "instiz", "clien": "clien", "ppomppu": "ppomppu",
        "fmkorea": "fmkorea", "ruliweb": "ruliweb", "blind": "blind",
        "band.us": "band", "linkedin": "linkedin", "hashnode": "hashnode",
    }
    for needle, label in sources.items():
        if needle in r:
            return label
    if "tarofortune.pythonanywhere.com" in r:
        return "internal"
    return "other:" + (r.split("/")[2] if "//" in r else r)[:40]


def record(path: str, referer: str, user_agent: str, lang: str,
           query_string: str = "") -> None:
    """요청 1건 기록. flask before_request에서 호출."""
    ua = user_agent or ""
    is_search_crawler = bool(_SEARCH_CRAWLER_RE.search(ua))
    is_bot = bool(_BOT_RE.search(ua))

    # 정적 파일·분석 자체·favicon은 기록 안 함
    if path.startswith("/static/") or path.startswith("/admin/") or \
       path in ("/favicon.ico", "/robots.txt", "/ads.txt", "/sitemap.xml") or \
       path.endswith(".txt") or path.startswith("/api/"):
        return

    # UTM 파싱
    utm = ""
    if "utm_source=" in query_string:
        m = re.search(r"utm_source=([^&]+)", query_string)
        if m:
            utm = m.group(1)[:40]

    entry = {
        "t": datetime.now().strftime("%H:%M:%S"),
        "p": path[:120],
        "r": _classify_referer(referer),
        "lang": lang,
        "crawler": is_search_crawler,
        "bot": is_bot and not is_search_crawler,
    }
    if utm:
        entry["utm"] = utm

    try:
        with _lock:
            with open(_today_file(), "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 분석 실패가 서비스 막으면 안 됨


def _read_day(d: date) -> list:
    fp = _today_file(d)
    if not os.path.exists(fp):
        return []
    out = []
    try:
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
    except Exception:
        pass
    return out


def summary(days: int = 14) -> dict:
    """최근 N일 통계 집계."""
    today = date.today()
    daily_human = {}
    daily_crawler = {}
    referers = Counter()
    pages = Counter()
    langs = Counter()
    utms = Counter()
    crawler_breakdown = Counter()
    total_human = 0
    total_crawler = 0
    total_bot = 0

    for i in range(days):
        d = today - timedelta(days=i)
        entries = _read_day(d)
        h = c = 0
        for e in entries:
            if e.get("crawler"):
                c += 1
                total_crawler += 1
                crawler_breakdown[e.get("r", "?")] += 1
            elif e.get("bot"):
                total_bot += 1
            else:
                h += 1
                total_human += 1
                referers[e.get("r", "direct")] += 1
                pages[e.get("p", "/")] += 1
                langs[e.get("lang", "ko")] += 1
                if e.get("utm"):
                    utms[e["utm"]] += 1
        daily_human[d.isoformat()] = h
        daily_crawler[d.isoformat()] = c

    return {
        "period_days": days,
        "total_human_pageviews": total_human,
        "total_search_crawler_hits": total_crawler,
        "total_bot_hits": total_bot,
        "daily_human": dict(sorted(daily_human.items())),
        "daily_crawler": dict(sorted(daily_crawler.items())),
        "top_referers": referers.most_common(15),
        "top_pages": pages.most_common(20),
        "lang_split": dict(langs),
        "utm_sources": utms.most_common(10),
        "search_crawler_breakdown": crawler_breakdown.most_common(10),
        "generated_at": datetime.now().isoformat(),
    }
