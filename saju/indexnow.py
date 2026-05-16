"""IndexNow 프로토콜 구현 — Bing·Yandex·Seznam에 새/갱신 URL 즉시 색인 요청.

https://www.indexnow.org/documentation
- 사이트 루트에 {key}.txt 파일 노출 (소유권 증명)
- POST /indexnow 로 URL 목록 전송
"""
from __future__ import annotations
import json
import secrets
from urllib import request
from pathlib import Path


# 사이트 루트에 고정된 키 (32자, 변경 시 새 키 파일 필요)
INDEXNOW_KEY = "8a7d3e2f1b4c5a6d9e8f7a6b5c4d3e2f"  # 32-char hex
INDEXNOW_KEY_LOCATION = "/" + INDEXNOW_KEY + ".txt"

# IndexNow API 엔드포인트 (모든 참여 검색엔진에 자동 fan-out)
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"


def submit_urls(host: str, urls: list[str], key: str = INDEXNOW_KEY) -> dict:
    """URL 목록을 IndexNow에 제출. host = 'tarofortune.pythonanywhere.com'.

    Returns dict with status_code and response body.
    """
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}{INDEXNOW_KEY_LOCATION}",
        "urlList": urls[:10000],  # API 최대 10,000 URL/request
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(INDEXNOW_ENDPOINT, data=body, method="POST",
                          headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with request.urlopen(req, timeout=30) as r:
            return {"status": r.status, "body": r.read().decode("utf-8", errors="replace")}
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        return {"status": getattr(e, "code", 0), "body": f"{e}: {b}"}


def submit_single(host: str, url: str, key: str = INDEXNOW_KEY) -> dict:
    """단일 URL용 GET 방식 IndexNow 제출."""
    from urllib.parse import urlencode
    params = urlencode({
        "url": url,
        "key": key,
        "keyLocation": f"https://{host}{INDEXNOW_KEY_LOCATION}",
    })
    try:
        with request.urlopen(f"{INDEXNOW_ENDPOINT}?{params}", timeout=30) as r:
            return {"status": r.status, "body": r.read().decode()}
    except Exception as e:
        return {"status": getattr(e, "code", 0), "body": str(e)}


def submit_all_urls(host: str) -> dict:
    """사이트의 모든 주요 URL을 IndexNow에 제출. 일일 배치용."""
    urls = []
    base = f"https://{host}"
    # 정적 페이지
    for p in ["/", "/today", "/zodiac", "/compatibility", "/sixty-pillars",
              "/basics", "/ten-gods", "/twelve-stages", "/five-elements",
              "/glossary", "/about", "/privacy", "/terms"]:
        urls.append(base + p)
        urls.append(base + "/en" + (p if p != "/" else "/"))
    # 60갑자 페이지
    for i in range(60):
        urls.append(f"{base}/sixty-pillars/{i}")
        urls.append(f"{base}/en/sixty-pillars/{i}")
    # 띠별 (한글 + 영문)
    zodiacs_kr = ["쥐", "소", "호랑이", "토끼", "용", "뱀",
                  "말", "양", "원숭이", "닭", "개", "돼지"]
    zodiacs_en = ["rat", "ox", "tiger", "rabbit", "dragon", "snake",
                  "horse", "goat", "monkey", "rooster", "dog", "pig"]
    from urllib.parse import quote
    for z in zodiacs_kr:
        urls.append(f"{base}/zodiac/{quote(z)}")
    for z in zodiacs_en:
        urls.append(f"{base}/en/zodiac/{z}")

    return submit_urls(host, urls)


if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "tarofortune.pythonanywhere.com"
    print(submit_all_urls(host))
