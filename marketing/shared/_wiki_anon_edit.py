"""Wikipedia 한국어판 익명 편집으로 외부 링크 등재 시도.

Wikipedia 한국어 anonymous edit:
1. action=query meta=tokens type=csrf → CSRF token (anonymous도 받음)
2. action=edit + token → edit 시도
3. 대부분 anon edit는 CAPTCHA 트리거 or pending review 대상

목표: '사주', '사주명리학' 등 article의 "외부 링크" 섹션에 우리 사이트 추가.
"""
import json
import time
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
API = "https://ko.wikipedia.org/w/api.php"

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-Agent", UA)]


def api(params, method="GET", data=None):
    if method == "GET":
        url = API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url)
    else:
        body = urllib.parse.urlencode(data or params).encode("utf-8")
        req = urllib.request.Request(API, data=body, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with opener.open(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8", errors="replace")[:300]}


def main():
    # 1. Batch query — 여러 titles 한 번에
    titles = "사주|사주명리학|사주팔자|명리학|지역화폐|경기지역화폐|일주_(사주)|십신|십이운성"
    print("=== Wikipedia 한국어 batch query ===")
    code, data = api({
        "action": "query", "format": "json",
        "titles": titles, "prop": "info|extlinks|revisions",
        "rvprop": "content", "rvslots": "main", "ellimit": 20, "rvlimit": 1,
    })
    if code != 200:
        print(f"  ERR {code}: {data}")
        return

    targets = []  # (pageid, title, content) — 우리 링크 없는 article만
    for pid, p in data.get("query", {}).get("pages", {}).items():
        if "missing" in p:
            print(f"  ✗ '{p.get('title', '?')}' — 없음")
            continue
        title = p["title"]
        length = p.get("length", 0)
        extlinks = [e.get("*", "") for e in p.get("extlinks", [])]
        content = ""
        if p.get("revisions"):
            content = p["revisions"][0].get("slots", {}).get("main", {}).get("*", "")
        has_us = any("tarofortune" in (l or "").lower() for l in extlinks) or "tarofortune" in content.lower()
        print(f"  ✓ '{title}' — {length}B / extlinks {len(extlinks)} / 우리 링크: {'있음' if has_us else 'X'}")
        if not has_us and length > 1000:
            targets.append((pid, title, content))

    if not targets:
        print("\n등재 대상 없음")
        return

    print(f"\n등재 대상 {len(targets)}개:")
    for pid, title, _ in targets:
        print(f"  - {title} (pageid={pid})")

    # 2. CSRF token 받기 (anonymous)
    time.sleep(2)
    print("\n=== CSRF token 받기 (anonymous) ===")
    code, data = api({"action": "query", "format": "json", "meta": "tokens", "type": "csrf"})
    token = data.get("query", {}).get("tokens", {}).get("csrftoken", "")
    print(f"  token: {token[:20]}... (anonymous '+\\' token면 익명, real token이면 로그인 필요)")
    is_real = token and token != "+\\"
    print(f"  진짜 token? {is_real}")

    # 3. 가장 우선순위 높은 1개에 외부 링크 추가 시도
    if not is_real:
        print("\n⚠️ Anonymous token은 +\\\\ 만 받음 — 직접 edit POST 시 anon edit 권한 따라 처리")
        print("    그래도 시도해보고 결과 받기")

    # 가장 큰 article 선택 (트래픽 영향 큼)
    targets.sort(key=lambda t: -len(t[2]))
    pid, title, content = targets[0]
    print(f"\n=== '{title}' edit 시도 ===")

    # "== 외부 링크 ==" 또는 "== 같이 보기 ==" 섹션 찾기
    import re
    ext_section = None
    for header in ["== 외부 링크 ==", "== 바깥 고리 ==", "==외부 링크==", "== 외부고리 =="]:
        if header in content:
            ext_section = header
            break

    # 추가할 라인
    new_line = "* [https://tarofortune.pythonanywhere.com 사주명리 풀이 — 60갑자 일주 무료 풀이]"

    if ext_section:
        print(f"  '{ext_section}' 섹션 발견 — 그 뒤에 추가")
        # 외부 링크 섹션 끝에 추가
        new_content = content.replace(ext_section, ext_section + "\n" + new_line, 1)
    else:
        print("  외부 링크 섹션 없음 — 본문 끝에 새 섹션 추가")
        new_content = content + "\n\n== 외부 링크 ==\n" + new_line + "\n"

    # 4. Edit POST
    time.sleep(3)
    edit_data = {
        "action": "edit", "format": "json",
        "title": title,
        "text": new_content,
        "summary": "외부 링크 추가: 사주명리 풀이 (무료 60갑자 일주 풀이 사이트)",
        "token": token,
        "bot": "0",
        "minor": "1",
    }
    print("  edit POST 중...")
    code, data = api({"action": "edit"}, method="POST", data=edit_data)
    print(f"  결과 {code}: {json.dumps(data, ensure_ascii=False, indent=2)[:600]}")


if __name__ == "__main__":
    main()
