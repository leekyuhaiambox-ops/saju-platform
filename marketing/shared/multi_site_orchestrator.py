"""
Multi-Site Bot Orchestrator
============================

기존 saju_platform 봇 인프라(lemmy_bot / mastodon_bot / devto_bot)를 재활용하여
3개 사이트(tarofortune / gyeonggi-currency-map / geoinfomatic)를 통합 운영.

설계 원칙
---------
1. 같은 봇 계정(@tarosaju, tarofortune)을 다중 주제로 회전 게시 → 계정 1개로 3사이트 커버
2. 일일 1회전 (Lemmy 3일 주기 / Mastodon 매일 / Dev.to 매일)
3. site_index = (epoch_day % len(SITES))로 사이트 자동 선택 → 봇 패턴 회피
4. 각 사이트의 콘텐츠 풀은 별도 JSON으로 관리 (코드와 분리)

실행 방법
---------
# 자동 모드 (오늘 사이트 자동 선택)
python multi_site_orchestrator.py

# 특정 사이트 강제
python multi_site_orchestrator.py --site currency-map

# 특정 채널만
python multi_site_orchestrator.py --site geoinfomatic --channel mastodon

# 드라이런 (게시 안 함)
python multi_site_orchestrator.py --dry-run

CI 연동
-------
기존 saju_platform/.github/workflows/daily-bot.yml의 run_all_bots.py 호출 라인을
이 스크립트로 교체:
  python -X utf8 multi_site_orchestrator.py

또는 추가 작업으로 별도 cron 실행.

자격증명
--------
saju_platform/.env 또는 GitHub Secrets에서 다음을 읽음:
  LEMMY_USERNAME, LEMMY_PASSWORD
  MASTODON_ACCESS_TOKEN
  DEVTO_API_KEY
  INDEXNOW_KEY
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------
# SITE REGISTRY
# ---------------------------------------------------------------------------

@dataclass
class Site:
    key: str
    name_en: str
    name_kr: str
    url: str
    description_en: str
    description_kr: str
    primary_tags: list[str]   # 영문 (Dev.to·Mastodon용)
    primary_tags_kr: list[str]  # 한국어 (한국어 채널용)
    lemmy_communities: list[str]  # ["community@instance"]


SITES: dict[str, Site] = {
    "tarofortune": Site(
        key="tarofortune",
        name_en="Saju Astrology",
        name_kr="사주명리 풀이",
        url="https://tarofortune.pythonanywhere.com",
        description_en="Korean four-pillars astrology calculator with full birth-chart analysis, 60-pillar interpretations in Korean and English, daily luck, compatibility check.",
        description_kr="한국 사주명리 계산기. 일주·월주·년주·시주 자동 산출, 60갑자 풀이 한·영, 오늘의 일진, 띠별 운세, 궁합 분석.",
        primary_tags=["astrology", "korea", "philosophy", "fortunetelling", "showdev"],
        primary_tags_kr=["사주", "명리", "운세", "일주", "60갑자"],
        lemmy_communities=["astrology@lemmy.world", "spirituality@lemmy.world"],
    ),
    "currency-map": Site(
        key="currency-map",
        name_en="Gyeonggi Local Currency Map",
        name_kr="경기지역화폐 가맹점 지도",
        url="https://gyeonggi-currency-map.web.app",
        description_en="Interactive map of Gyeonggi Province (South Korea) local currency merchant locations across 31 cities, with business-type filter and 'open now' real-time filter. Built with React + Vite + Leaflet, hosted on Firebase. PWA-installable.",
        description_kr="경기도 31개 시·군의 지역화폐·경기페이 가맹점을 지도에서 한눈에. 음식점·카페·미용실 등 업종별 필터와 '영업중' 필터로 지금 당장 갈 수 있는 가맹점을 검색.",
        primary_tags=["reactjs", "leaflet", "pwa", "openstreetmap", "showdev"],
        primary_tags_kr=["경기지역화폐", "경기페이", "지역화폐", "가맹점", "지도"],
        lemmy_communities=["southkorea@lemmy.world", "openstreetmap@lemmy.ml"],
    ),
    "geoinfomatic": Site(
        key="geoinfomatic",
        name_en="Living Zone Accessibility Analyzer",
        name_kr="생활권 접근성 분석",
        url="https://geoinfomatic.pythonanywhere.com",
        description_en="Isochrone-based neighborhood accessibility analyzer for South Korea. Walk or transit, 10-45 min radius, multi-facility (subway/school/hospital/mart/park/gym/pharmacy/library/cafe). AI summary, 100-point composite score. No real-estate listings — pure accessibility analysis.",
        description_kr="이사·청약·임장 전 도보·대중교통 기준 10~45분 내 도달 가능한 지하철·학교·병원·마트·공원을 지도에서 분석. 매물 광고 없는 순수 생활권 분석 도구. 100점 만점 종합 점수 + AI 요약.",
        primary_tags=["gis", "leaflet", "urbanplanning", "flask", "showdev"],
        primary_tags_kr=["생활권", "접근성", "이사", "학군", "임장", "부동산"],
        lemmy_communities=["urbanism@lemmy.world", "korea@lemmy.world"],
    ),
}


# ---------------------------------------------------------------------------
# CONTENT POOLS (제목 + 본문 템플릿)
# ---------------------------------------------------------------------------

def _load_post_pool(site_key: str) -> list[dict]:
    """JSON에서 사이트별 콘텐츠 풀 로드. 없으면 내장 디폴트 사용."""
    pool_path = Path(__file__).parent / "content_pools" / f"{site_key}.json"
    if pool_path.exists():
        return json.loads(pool_path.read_text(encoding="utf-8"))
    return _builtin_pool(site_key)


def _builtin_pool(site_key: str) -> list[dict]:
    """JSON 없을 때 사용하는 최소 내장 풀."""
    site = SITES[site_key]
    return [
        {
            "lang": "en",
            "title": f"{site.name_en} — {site.description_en[:80]}",
            "body": f"{site.description_en}\n\nTry it: {site.url}",
            "tags": site.primary_tags,
        },
        {
            "lang": "kr",
            "title": site.name_kr,
            "body": f"{site.description_kr}\n\n링크: {site.url}",
            "tags": site.primary_tags_kr,
        },
    ]


# ---------------------------------------------------------------------------
# SITE ROTATION LOGIC
# ---------------------------------------------------------------------------

def pick_site_for_today(force: str | None = None) -> Site:
    """오늘 게시할 사이트 선택. force 인자 우선, 없으면 epoch 일자 회전."""
    if force:
        if force not in SITES:
            raise ValueError(f"Unknown site: {force}. Available: {list(SITES)}")
        return SITES[force]
    epoch_day = int(time.time() // 86400)
    keys = sorted(SITES.keys())
    return SITES[keys[epoch_day % len(keys)]]


def pick_post(site: Site, channel: str) -> dict:
    """사이트 + 채널에 맞는 콘텐츠 선택. state 파일로 중복 방지."""
    pool = _load_post_pool(site.key)
    state_path = Path(__file__).parent / "state" / f"{site.key}_{channel}.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    used = set(state.get("used_indices", []))
    available = [i for i in range(len(pool)) if i not in used]
    if not available:
        used = set()
        available = list(range(len(pool)))

    # 채널 언어 매칭: Mastodon/Dev.to/Lemmy는 영문, 카카오·네이버는 한국어
    lang_pref = "en" if channel in ("mastodon", "devto", "lemmy") else "kr"
    matching = [i for i in available if pool[i].get("lang") == lang_pref]
    chosen_idx = matching[0] if matching else available[0]

    used.add(chosen_idx)
    state["used_indices"] = sorted(used)
    state["last_picked_at"] = datetime.now(timezone.utc).isoformat()
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return pool[chosen_idx]


# ---------------------------------------------------------------------------
# CHANNEL ADAPTERS (saju_platform 봇 import)
# ---------------------------------------------------------------------------

def _import_saju_bots():
    """saju_platform 경로를 sys.path에 추가하고 봇 모듈 import.

    두 레이아웃 모두 지원:
      A) marketing/이 saju_platform의 sibling (CEO/marketing, CEO/saju_platform)
      B) marketing/이 saju_platform 내부 (saju_platform/marketing/) — GitHub Actions 권장
    """
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent.parent / "saju_platform",   # sibling layout
        here.parent.parent.parent,                     # inside layout (marketing/ in saju_platform)
        here.parent.parent.parent.parent / "saju_platform",
    ]
    for saju_path in candidates:
        if (saju_path / "lemmy_bot.py").exists() and (saju_path / "mastodon_bot.py").exists():
            if str(saju_path) not in sys.path:
                sys.path.insert(0, str(saju_path))
            try:
                import lemmy_bot, mastodon_bot, devto_bot  # type: ignore
                return lemmy_bot, mastodon_bot, devto_bot
            except ImportError as e:
                print(f"[WARN] {saju_path} 에서 import 실패: {e}")
    print("[WARN] saju_platform 봇 모듈을 찾지 못함 — direct API 호출로 폴백")
    return None, None, None


def post_to_mastodon(site: Site, post: dict, dry_run: bool = False) -> bool:
    """Mastodon 게시. 기존 mastodon_bot.post() 함수 재활용."""
    text = _format_mastodon(site, post)
    print(f"\n[MASTODON · {site.key}]\n{text}\n")
    if dry_run:
        return True
    _, mastodon_bot, _ = _import_saju_bots()
    if mastodon_bot is None:
        return False
    # mastodon_bot에 generic post 함수가 있다고 가정. 없으면 직접 API 호출:
    return _direct_mastodon_post(text)


def post_to_lemmy(site: Site, post: dict, dry_run: bool = False) -> bool:
    text = _format_lemmy(site, post)
    print(f"\n[LEMMY · {site.key}]\n{text}\n")
    if dry_run:
        return True
    return _direct_lemmy_post(post["title"], text, site.lemmy_communities)


def post_to_devto(site: Site, post: dict, dry_run: bool = False) -> bool:
    text = _format_devto(site, post)
    print(f"\n[DEV.TO · {site.key}]\nTitle: {post['title']}\n\n{text}\n")
    if dry_run:
        return True
    return _direct_devto_post(post["title"], text, post.get("tags", site.primary_tags))


# ---------------------------------------------------------------------------
# CHANNEL-SPECIFIC FORMATTERS
# ---------------------------------------------------------------------------

def _format_mastodon(site: Site, post: dict) -> str:
    tags = " ".join(f"#{t}" for t in post.get("tags", site.primary_tags))
    body = post["body"]
    if site.url not in body:
        body += f"\n\n{site.url}"
    if tags not in body:
        body += f"\n\n{tags}"
    return body[:500]  # Mastodon 기본 500자


def _format_lemmy(site: Site, post: dict) -> str:
    body = post["body"]
    if site.url not in body:
        body += f"\n\n**Try it:** {site.url}"
    return body


def _format_devto(site: Site, post: dict) -> str:
    tags = post.get("tags", site.primary_tags)
    front_matter = (
        f"---\ntitle: {post['title']}\npublished: true\ntags: {', '.join(tags)}\n---\n\n"
    )
    body = post["body"]
    if site.url not in body:
        body += f"\n\n**Live demo:** {site.url}\n"
    return front_matter + body


# ---------------------------------------------------------------------------
# DIRECT POST FALLBACKS (saju 봇 없을 때 사용)
# ---------------------------------------------------------------------------

def _direct_mastodon_post(text: str) -> bool:
    token = os.environ.get("MASTODON_ACCESS_TOKEN")
    instance = os.environ.get("MASTODON_INSTANCE", "mastodon.social")
    if not token:
        print("[ERROR] MASTODON_ACCESS_TOKEN 환경변수 없음")
        return False
    import urllib.request, urllib.parse
    data = urllib.parse.urlencode({"status": text}).encode("utf-8")
    req = urllib.request.Request(
        f"https://{instance}/api/v1/statuses",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[ERROR] Mastodon: {e}")
        return False


def _direct_lemmy_post(title: str, body: str, communities: list[str]) -> bool:
    """Lemmy 실제 게시 — saju_platform/lemmy_bot.py 의 login/post helpers 재활용."""
    user = os.environ.get("LEMMY_USERNAME")
    pwd = os.environ.get("LEMMY_PASSWORD")
    instance = os.environ.get("LEMMY_INSTANCE", "lemmy.world")
    if not (user and pwd):
        print("[ERROR] LEMMY 자격증명 환경변수 없음")
        return False

    lemmy_bot, _, _ = _import_saju_bots()
    if lemmy_bot is None:
        return _lemmy_direct_api_post(title, body, communities[0] if communities else None,
                                       instance, user, pwd)

    # saju lemmy_bot 활용: login → community lookup → post
    try:
        jwt = lemmy_bot.login()
    except Exception as e:
        print(f"[ERROR] Lemmy login 실패: {e}")
        return False

    target = communities[0] if communities else "asia@lemmy.world"
    try:
        cname, cinst = target.split("@", 1)
    except ValueError:
        print(f"[ERROR] 잘못된 community 형식: {target}")
        return False

    try:
        community_id = lemmy_bot.get_community_id(cname, cinst, jwt)
    except Exception as e:
        print(f"[ERROR] Lemmy community lookup 실패 ({target}): {e}")
        return False

    if not community_id:
        print(f"[ERROR] community_id None for {target}")
        return False

    try:
        ok = lemmy_bot.post_to_community(title=title, body=body,
                                         community_id=community_id, jwt=jwt)
        print(f"[Lemmy] {target} 게시 결과: {ok}")
        return bool(ok)
    except AttributeError:
        # 함수명이 다를 수 있음 — fallback
        return _lemmy_direct_api_post(title, body, target, instance, user, pwd, jwt=jwt)
    except Exception as e:
        print(f"[ERROR] Lemmy post 실패: {e}")
        return False


def _lemmy_direct_api_post(title: str, body: str, community: str | None,
                            instance: str, user: str, pwd: str,
                            jwt: str | None = None) -> bool:
    """순수 urllib 기반 Lemmy 게시 — saju_platform 봇 없을 때 폴백."""
    import urllib.request, json as _json
    if not jwt:
        login_body = _json.dumps({"username_or_email": user, "password": pwd}).encode()
        req = urllib.request.Request(
            f"https://{instance}/api/v3/user/login",
            data=login_body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                jwt = _json.loads(r.read()).get("jwt")
        except Exception as e:
            print(f"[ERROR] Lemmy login: {e}")
            return False

    if not community:
        print("[ERROR] Lemmy community 없음")
        return False
    cname, cinst = community.split("@", 1)

    # community lookup
    lookup_url = f"https://{instance}/api/v3/community?name={cname}@{cinst}&auth={jwt}"
    try:
        with urllib.request.urlopen(lookup_url, timeout=30) as r:
            data = _json.loads(r.read())
            community_id = data.get("community_view", {}).get("community", {}).get("id")
    except Exception as e:
        print(f"[ERROR] Lemmy community lookup: {e}")
        return False

    if not community_id:
        print(f"[ERROR] community_id missing for {community}")
        return False

    post_body = _json.dumps({
        "name": title[:200], "body": body, "community_id": community_id, "auth": jwt,
    }).encode()
    req = urllib.request.Request(
        f"https://{instance}/api/v3/post",
        data=post_body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status in (200, 201)
    except Exception as e:
        print(f"[ERROR] Lemmy post: {e}")
        return False


def _direct_devto_post(title: str, body: str, tags: list[str]) -> bool:
    key = os.environ.get("DEVTO_API_KEY")
    if not key:
        print("[ERROR] DEVTO_API_KEY 환경변수 없음")
        return False
    import urllib.request, json as _json
    payload = {
        "article": {
            "title": title,
            "body_markdown": body,
            "published": True,
            "tags": tags[:4],  # Dev.to는 4개 제한
        }
    }
    req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=_json.dumps(payload).encode("utf-8"),
        headers={"api-key": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[ERROR] Dev.to: {e}")
        return False


# ---------------------------------------------------------------------------
# INDEXNOW (모든 사이트에 적용)
# ---------------------------------------------------------------------------

def submit_indexnow(site: Site, paths: list[str] | None = None) -> bool:
    key = os.environ.get("INDEXNOW_KEY", "8a7d3e2f1b4c5a6d9e8f7a6b5c4d3e2f")
    host = site.url.replace("https://", "").replace("http://", "").rstrip("/")
    paths = paths or ["/"]
    urls = [f"{site.url.rstrip('/')}{p}" for p in paths]
    import urllib.request, json as _json
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{site.url.rstrip('/')}/{key}.txt",
        "urlList": urls,
    }
    print(f"[INDEXNOW · {site.key}] Submitting {len(urls)} URLs")
    for endpoint in ("https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"):
        try:
            req = urllib.request.Request(
                endpoint,
                data=_json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                print(f"  {endpoint} → {resp.status}")
        except Exception as e:
            print(f"  {endpoint} ERROR: {e}")
    return True


# ---------------------------------------------------------------------------
# CLI ENTRY
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=list(SITES.keys()), help="특정 사이트 강제 선택")
    parser.add_argument("--channel", choices=["mastodon", "lemmy", "devto", "indexnow", "all"],
                        default="all", help="특정 채널만 실행")
    parser.add_argument("--dry-run", action="store_true", help="실제 게시 안 하고 출력만")
    args = parser.parse_args()

    site = pick_site_for_today(args.site)
    print(f"\n=== 오늘의 사이트: {site.key} ({site.name_kr}) ===\n")

    results = {}

    if args.channel in ("mastodon", "all"):
        post = pick_post(site, "mastodon")
        results["mastodon"] = post_to_mastodon(site, post, args.dry_run)

    if args.channel in ("devto", "all"):
        post = pick_post(site, "devto")
        results["devto"] = post_to_devto(site, post, args.dry_run)

    if args.channel in ("lemmy", "all"):
        # Lemmy는 3일 주기 (state 파일로 추적)
        last_lemmy = _last_lemmy_at(site.key)
        if last_lemmy and (time.time() - last_lemmy) < 3 * 86400:
            print(f"[LEMMY · {site.key}] 마지막 게시 후 3일 미경과 → 건너뜀")
            results["lemmy"] = "skipped"
        else:
            post = pick_post(site, "lemmy")
            results["lemmy"] = post_to_lemmy(site, post, args.dry_run)
            if not args.dry_run and results["lemmy"]:
                _mark_lemmy_posted(site.key)

    if args.channel in ("indexnow", "all"):
        results["indexnow"] = submit_indexnow(site)

    print("\n=== 실행 결과 ===")
    for ch, ok in results.items():
        print(f"  {ch}: {ok}")


def _last_lemmy_at(site_key: str) -> float | None:
    p = Path(__file__).parent / "state" / f"{site_key}_lemmy_last.txt"
    if not p.exists():
        return None
    try:
        return float(p.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def _mark_lemmy_posted(site_key: str) -> None:
    p = Path(__file__).parent / "state" / f"{site_key}_lemmy_last.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(time.time()), encoding="utf-8")


if __name__ == "__main__":
    main()
