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
        base + "/compatibility",
        base + f"/yearly/{today.year}",
        base + "/en/",
        base + "/en/today",
        base + f"/en/today/{today.isoformat()}",
        base + "/feed.xml",
        base + "/en/feed.xml",
    ]
    # 띠별 운세 12개 (고볼륨 한국어 키워드) 매일 색인 갱신
    for z in ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]:
        urls.append(base + "/zodiac/" + parse.quote(z))
    # 꿈해몽 인덱스 + 고볼륨 꿈 (돼지/똥/용 등)
    urls.append(base + "/dream")
    for slug in ["pig", "feces", "dragon", "snake", "teeth", "poo_lottery",
                 "poop_step", "money", "death", "blood"]:
        urls.append(base + "/dream/" + slug)
    # 별자리·혈액형·MBTI (고볼륨 한국어 검색)
    urls += [base + "/horoscope", base + "/blood", base + "/blood-compat", base + "/mbti"]
    urls.append(base + "/en/horoscope")
    try:
        from saju.horoscope import SIGNS as _SIGNS
        for _s in _SIGNS:
            urls.append(base + "/horoscope/" + _s[0])
            urls.append(base + "/en/horoscope/" + _s[0])
    except Exception:
        pass
    for _bt in ["A", "B", "O", "AB"]:
        urls.append(base + "/blood/" + _bt)
    for _mt in ["INFP", "ENFP", "INFJ", "INTJ", "ISTP", "ISFJ", "ESFP",
                "ENTP", "ISTJ", "ESTJ", "ESFJ", "ENFJ", "ENTJ", "INTP",
                "ISFP", "ESTP"]:
        urls.append(base + "/mbti/" + _mt)
    # 타로 — 인덱스·오늘의카드(매일 갱신)·메이저22 한·영
    urls += [base + "/tarot", base + "/en/tarot",
             base + "/tarot/today", base + "/en/tarot/today"]
    try:
        from saju.tarot import all_major as _maj
        for _c in _maj():
            urls.append(base + "/tarot/" + _c["slug"])
            urls.append(base + "/en/tarot/" + _c["slug"])
    except Exception:
        pass
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
