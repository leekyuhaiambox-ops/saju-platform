"""Wikipedia 한국어 + 나무위키에 사이트 외부 링크 자동 등재 시도.

한국 사주 검색 시 Wikipedia·나무위키가 상위 노출 → 외부 링크 클릭 = 한국 트래픽 직격.
"""
import json
import urllib.request
import urllib.parse
import sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"


def wiki_api(params: dict, method="GET", data=None, cookies=None):
    """Wikipedia 한국어 API 호출."""
    url = "https://ko.wikipedia.org/w/api.php"
    headers = {"User-Agent": UA}
    if cookies:
        headers["Cookie"] = cookies
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers)
    else:
        body = urllib.parse.urlencode(data or params).encode()
        req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8"), r.headers


def check_article(title: str):
    """문서 존재 + 내용 + 기존 외부 링크 확인."""
    params = {
        "action": "query", "format": "json",
        "titles": title, "prop": "info|extlinks|revisions",
        "rvprop": "content|timestamp", "rvslots": "main",
        "ellimit": 30, "rvlimit": 1,
    }
    code, body, _ = wiki_api(params)
    if code != 200:
        return None
    data = json.loads(body)
    pages = data.get("query", {}).get("pages", {})
    for pid, p in pages.items():
        if "missing" in p:
            return {"exists": False, "title": title}
        ext = [e.get("*", "") for e in p.get("extlinks", [])]
        content = ""
        if p.get("revisions"):
            content = p["revisions"][0].get("slots", {}).get("main", {}).get("*", "")
        return {
            "exists": True, "pageid": pid, "title": p["title"],
            "length": p.get("length", 0),
            "extlinks": ext,
            "content_len": len(content),
            "content_tail": content[-2000:] if content else "",
            "has_tarofortune": "tarofortune" in content.lower(),
            "has_geoinfomatic": "geoinfomatic" in content.lower(),
            "has_currency_map": "gyeonggi-currency-map" in content.lower() or "currency-map" in content.lower(),
        }


def main():
    titles = ["사주", "사주명리학", "사주팔자", "명리학",
              "지역화폐", "경기지역화폐",
              "Saju", "BaZi", "Four Pillars of Destiny",
              "위키:사용자 메뉴얼"]  # 마지막은 익명 편집 정책 확인용
    print("=== Wikipedia 한국어 문서 진단 ===")
    for t in titles:
        result = check_article(t)
        if result is None:
            print(f"  {t}: ERR")
        elif not result["exists"]:
            print(f"  ✗ '{t}' — 없음")
        else:
            print(f"  ✓ '{result['title']}' — {result['length']} bytes / extlinks {len(result['extlinks'])}")
            already = []
            if result.get("has_tarofortune"): already.append("tarofortune")
            if result.get("has_geoinfomatic"): already.append("geoinfomatic")
            if result.get("has_currency_map"): already.append("currency-map")
            if already:
                print(f"      → 이미 등재된 사이트: {already}")


if __name__ == "__main__":
    main()
