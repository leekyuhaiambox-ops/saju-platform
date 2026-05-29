"""사주 명리학 광고 수익형 플랫폼 — Flask 메인 앱.

PythonAnywhere 무료 티어 배포 기준으로 설계되었다.
- /        : 입력 폼
- /result  : POST/GET으로 받은 생년월일시 → 사주 결과
- /basics  : 사주 기초 가이드
- /ten-gods, /twelve-stages, /five-elements : 콘텐츠 페이지
- /sixty-pillars : 60갑자 일주별 풀이 인덱스
- /sixty-pillars/<idx> : 특정 일주 상세
- /about, /privacy, /terms : 정책 페이지
- /ads.txt, /robots.txt   : SEO/광고 인프라
"""
import os
from datetime import datetime, date, timedelta
from flask import (Flask, render_template, request, redirect, url_for,
                   abort, Response, jsonify, g)

from saju import compute_saju, compute_daewoon, interpret
from saju.interpreter import (
    DAY_PILLAR_INTERPRETATIONS, TEN_GOD_MEANING,
    TWELVE_STAGE_MEANING, ELEMENT_MEANING
)
from saju.interpreter_en import (
    DAY_PILLAR_INTERPRETATIONS_EN, TEN_GOD_EN,
    TWELVE_STAGE_EN, ELEMENT_EN, ZODIAC_TRAITS_EN
)
from saju.daily import (
    daily_fortune, zodiac_yearly_fortune, compatibility,
    ZODIAC_TRAITS, ZODIAC_BRANCH_INDEX
)
from saju.glossary import GLOSSARY
from saju.glossary_en import GLOSSARY_EN
from saju.i18n import t, LANGS, DEFAULT_LANG, STEM_EN, BRANCH_EN, ELEMENT_EN as ELEMENT_NAMES_EN
from saju import data as D
from saju.cache import cached, get_cache, stats as cache_stats
from saju.indexnow import INDEXNOW_KEY, INDEXNOW_KEY_LOCATION
from saju.long_tail import CAREER_HEADLINES, LOVE_HEADLINES
from saju.solar_terms_data import SOLAR_TERM_DETAIL
from saju.detail_pages import (
    TEN_GODS_DETAIL, TWELVE_STAGES_DETAIL,
    HIDDEN_STEMS_DETAIL, HEAVENLY_STEMS_DETAIL,
)
import threading
import subprocess

# ─── 외부 cron용 웹훅 시크릿 ─────────────────────────
CRON_SECRET = os.environ.get("CRON_SECRET", "")


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.url_defaults
def _add_lang_to_url(endpoint, values):
    if hasattr(g, "lang") and "lang" not in values and g.lang != DEFAULT_LANG:
        # Only auto-pass lang for endpoints that have <lang> in route, but we keep manual handling
        pass


@app.before_request
def _detect_lang():
    """Detect language from URL prefix `/en/`. Default = Korean."""
    p = request.path
    if p == "/en" or p.startswith("/en/"):
        g.lang = "en"
    else:
        g.lang = "ko"


@app.after_request
def _cors_headers(resp):
    """Toss 미니앱·외부 클라이언트가 /api/* 호출 가능하도록 CORS 허용."""
    if request.path.startswith("/api/"):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Max-Age"] = "86400"
    return resp


# ─────────────────────────────────────────────────────────────────
# Referral / Affiliate tracking — 다른 사이트로 트래픽 송출 + 추적
# ?ref=austriano / ?ref=mastodon / ?ref=lemmy / ?utm_source=...
# ─────────────────────────────────────────────────────────────────
REFERRAL_LOG = os.path.join(os.path.dirname(__file__), ".referral_log.jsonl")


@app.before_request
def _track_referral():
    """랜딩 시 referrer / ref / utm_source 추적 → 쿠키 + JSONL log."""
    if request.path.startswith(("/static/", "/api/", "/og/")):
        return  # 정적·API는 무시
    ref = (
        request.args.get("ref")
        or request.args.get("utm_source")
        or request.cookies.get("_ref")
    )
    if ref:
        g._set_ref = ref[:64]
    # 로그는 첫 방문만 (cookie 없을 때)
    if request.args.get("ref") or request.args.get("utm_source"):
        try:
            import json as _json
            entry = {
                "ts": datetime.utcnow().isoformat(),
                "path": request.path,
                "ref": (request.args.get("ref") or request.args.get("utm_source"))[:64],
                "utm_medium": request.args.get("utm_medium", "")[:32],
                "utm_campaign": request.args.get("utm_campaign", "")[:64],
                "referer": request.headers.get("Referer", "")[:200],
                "ua": request.headers.get("User-Agent", "")[:200],
            }
            with open(REFERRAL_LOG, "a", encoding="utf-8") as f:
                f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass


@app.after_request
def _set_ref_cookie(resp):
    """referral 30일 쿠키 설정."""
    ref = getattr(g, "_set_ref", None)
    if ref:
        resp.set_cookie("_ref", ref, max_age=30 * 86400, samesite="Lax")
    return resp


# ─────────────────────────────────────────────────────────────────
# Email capture — newsletter / Pro 알림용
# /api/email-capture: POST {email, source}
# ─────────────────────────────────────────────────────────────────
EMAIL_LOG = os.path.join(os.path.dirname(__file__), ".email_capture.jsonl")


@app.route("/api/email-capture", methods=["POST", "OPTIONS"])
def email_capture():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(silent=True) or request.form.to_dict()
    email = (data.get("email") or "").strip().lower()
    source = (data.get("source") or "site")[:32]
    if "@" not in email or "." not in email or len(email) > 120:
        return jsonify({"ok": False, "error": "invalid_email"}), 400
    try:
        import json as _json
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "email": email,
            "source": source,
            "ref": request.cookies.get("_ref", ""),
            "ua": request.headers.get("User-Agent", "")[:160],
        }
        with open(EMAIL_LOG, "a", encoding="utf-8") as f:
            f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        return jsonify({"ok": False, "error": "log_failed", "msg": str(e)[:60]}), 500
    return jsonify({"ok": True, "msg": "subscribed"})


# ─────────────────────────────────────────────────────────────────
# Cross-promotion API — 3사이트 가족 노출
# 모든 사이트에서 동일 JSON 호출해 footer cross-promote 가능
# ─────────────────────────────────────────────────────────────────
@app.route("/api/family", methods=["GET", "OPTIONS"])
def family_sites():
    if request.method == "OPTIONS":
        return ("", 204)
    sites = [
        {
            "key": "tarofortune", "kr_name": "사주명리 풀이",
            "en_name": "Saju Astrology",
            "url": "https://tarofortune.pythonanywhere.com",
            "desc_kr": "60갑자 사주 풀이 무료 — 일주·오행·십신·일진",
            "desc_en": "Korean four-pillars astrology, free, EN+KR",
            "emoji": "🔮",
        },
        {
            "key": "currency-map", "kr_name": "경기지역화폐 가맹점 지도",
            "en_name": "Gyeonggi Currency Map",
            "url": "https://gyeonggi-currency-map.web.app",
            "desc_kr": "31개 시·군 경기페이 가맹점 통합 지도",
            "desc_en": "31-city local currency merchant map (Korea)",
            "emoji": "🗺",
        },
        {
            "key": "geoinfomatic", "kr_name": "생활권 접근성 분석",
            "en_name": "Living Zone Accessibility",
            "url": "https://geoinfomatic.pythonanywhere.com",
            "desc_kr": "이사·임장 도보 30분 생활권 점수",
            "desc_en": "Isochrone neighborhood analyzer (Korea)",
            "emoji": "🏘",
        },
    ]
    return jsonify({"sites": sites, "self_key": "tarofortune"})


# ─────────────────────────────────────────────────────────────────
# Analytics aggregator — 외부에서 일일 KPI 조회용 (CRON_SECRET 인증)
# ─────────────────────────────────────────────────────────────────
@app.route("/api/analytics/daily", methods=["GET"])
def analytics_daily():
    """일일 referral·email capture KPI. CRON_SECRET 헤더 필요."""
    if request.headers.get("X-Cron-Secret") != CRON_SECRET or not CRON_SECRET:
        return jsonify({"ok": False, "error": "auth"}), 403
    import json as _json
    today = date.today().isoformat()
    out = {"date": today, "referral_count": 0, "email_count": 0,
           "by_ref": {}, "by_email_source": {}}
    try:
        if os.path.exists(REFERRAL_LOG):
            with open(REFERRAL_LOG, encoding="utf-8") as f:
                for line in f:
                    try:
                        e = _json.loads(line)
                        if not e["ts"].startswith(today):
                            continue
                        out["referral_count"] += 1
                        ref = e.get("ref", "?")
                        out["by_ref"][ref] = out["by_ref"].get(ref, 0) + 1
                    except Exception:
                        pass
    except Exception:
        pass
    try:
        if os.path.exists(EMAIL_LOG):
            with open(EMAIL_LOG, encoding="utf-8") as f:
                for line in f:
                    try:
                        e = _json.loads(line)
                        if not e["ts"].startswith(today):
                            continue
                        out["email_count"] += 1
                        src = e.get("source", "?")
                        out["by_email_source"][src] = out["by_email_source"].get(src, 0) + 1
                    except Exception:
                        pass
    except Exception:
        pass
    return jsonify({"ok": True, **out})


@app.route("/api/<path:any>", methods=["OPTIONS"])
def _cors_preflight(any):
    return ("", 204)

# ─────────────────────────────────────────────────────────────────
# 광고/추적 ID — 환경변수로 외부 주입 (배포 시 .env 또는 webapp 환경변수)
# ─────────────────────────────────────────────────────────────────
ADSENSE_CLIENT_ID = os.environ.get("ADSENSE_CLIENT_ID", "")     # 예: ca-pub-1234567890123456
ADSENSE_SLOT_TOP = os.environ.get("ADSENSE_SLOT_TOP", "")
ADSENSE_SLOT_INLINE = os.environ.get("ADSENSE_SLOT_INLINE", "")
ADSENSE_SLOT_BOTTOM = os.environ.get("ADSENSE_SLOT_BOTTOM", "")

# 카카오 AdFit — 즉시 활성 (AdSense 승인 대기 동안 수익화)
ADFIT_SLOT_LEADERBOARD = os.environ.get("ADFIT_SLOT_LEADERBOARD", "DAN-n0PoylDwx5yW9h6m")  # 728×90
ADFIT_SLOT_MEDIUM = os.environ.get("ADFIT_SLOT_MEDIUM", "DAN-6igVlxF0jtfGAy7k")            # 300×250
ADFIT_SLOT_SQUARE = os.environ.get("ADFIT_SLOT_SQUARE", "DAN-R1f0lIsOhUpSLRxI")            # 250×250
ADFIT_SLOT_SKYSCRAPER = os.environ.get("ADFIT_SLOT_SKYSCRAPER", "DAN-oS7GuVEpbyNDjHBF")    # 160×600
META_PIXEL_ID = os.environ.get("META_PIXEL_ID", "")             # 예: 1234567890
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "")     # 예: G-XXXXXXXX

# 검색엔진 소유권 인증 — 가입 후 환경변수만 채우면 활성화
GOOGLE_SITE_VERIFICATION = os.environ.get("GOOGLE_SITE_VERIFICATION", "")  # google-site-verification 메타 값
NAVER_SITE_VERIFICATION = os.environ.get("NAVER_SITE_VERIFICATION", "")    # 네이버 서치어드바이저
BING_SITE_VERIFICATION = os.environ.get("BING_SITE_VERIFICATION", "")      # Bing Webmaster
YANDEX_SITE_VERIFICATION = os.environ.get("YANDEX_SITE_VERIFICATION", "")  # Yandex
PINTEREST_VERIFICATION = os.environ.get("PINTEREST_VERIFICATION", "")      # Pinterest
SITE_NAME = "사주명리 — 운명의 설계도"
SITE_TAGLINE = "1,800년 동양철학의 지혜로 당신의 사주를 풀어드립니다"


@app.context_processor
def inject_globals():
    lang = getattr(g, "lang", DEFAULT_LANG)
    return {
        "ADSENSE_CLIENT_ID": ADSENSE_CLIENT_ID,
        "ADSENSE_SLOT_TOP": ADSENSE_SLOT_TOP,
        "ADSENSE_SLOT_INLINE": ADSENSE_SLOT_INLINE,
        "ADSENSE_SLOT_BOTTOM": ADSENSE_SLOT_BOTTOM,
        "ADFIT_SLOT_LEADERBOARD": ADFIT_SLOT_LEADERBOARD,
        "ADFIT_SLOT_MEDIUM": ADFIT_SLOT_MEDIUM,
        "ADFIT_SLOT_SQUARE": ADFIT_SLOT_SQUARE,
        "ADFIT_SLOT_SKYSCRAPER": ADFIT_SLOT_SKYSCRAPER,
        "META_PIXEL_ID": META_PIXEL_ID,
        "GA_MEASUREMENT_ID": GA_MEASUREMENT_ID,
        "GOOGLE_SITE_VERIFICATION": GOOGLE_SITE_VERIFICATION,
        "NAVER_SITE_VERIFICATION": NAVER_SITE_VERIFICATION,
        "BING_SITE_VERIFICATION": BING_SITE_VERIFICATION,
        "YANDEX_SITE_VERIFICATION": YANDEX_SITE_VERIFICATION,
        "PINTEREST_VERIFICATION": PINTEREST_VERIFICATION,
        "SITE_NAME": t("site_name", lang),
        "SITE_TAGLINE": t("site_tagline", lang),
        "current_year": datetime.now().year,
        "lang": lang,
        "t": t,
        "STEM_EN": STEM_EN,
        "BRANCH_EN": BRANCH_EN,
        "ELEMENT_NAMES_EN": ELEMENT_NAMES_EN,
    }


# ─────────────────────────────────────────────────────────────────
# 메인 / 입력  (한국어 + 영문 동시 지원)
# ─────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/en/")
def index():
    return render_template("index.html",
                           today=date.today().isoformat(),
                           min_date="1900-01-01",
                           max_date=date.today().isoformat())


# ─────────────────────────────────────────────────────────────────
# 사주 풀이 결과
# ─────────────────────────────────────────────────────────────────
@app.route("/result", methods=["GET", "POST"])
@app.route("/en/result", methods=["GET", "POST"])
def result():
    is_en = (g.lang == "en")
    if request.method == "POST":
        form = request.form
    else:
        form = request.args

    try:
        name = (form.get("name") or "").strip()[:30]
        gender = form.get("gender", form.get("g", "남" if not is_en else "M"))
        birth_date_str = form.get("birth_date", "")
        birth_time_str = form.get("birth_time", "")
        unknown_hour = form.get("unknown_hour") == "on" or form.get("uh") == "1"
        is_lunar = False

        # ─── BACKWARD COMPATIBLE: sitemap·OG URL (y/m/d/h/min) 도 지원 ───
        # OG image URL과 sitemap의 60 sample URLs가 y/m/d 쓰기 때문에
        # 결과 페이지가 indexable 되려면 두 포맷 모두 받아야 함.
        if not birth_date_str:
            y = form.get("y")
            mo = form.get("m")
            d = form.get("d")
            if y and mo and d:
                try:
                    birth_date_str = f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
                except (ValueError, TypeError):
                    pass
                h = form.get("h")
                mi = form.get("min")
                if h is not None and mi is not None:
                    try:
                        birth_time_str = f"{int(h):02d}:{int(mi):02d}"
                    except (ValueError, TypeError):
                        pass

        if not birth_date_str:
            return redirect(url_for("index"))

        bd = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        if unknown_hour or not birth_time_str:
            hour, minute = 12, 0
            unknown_hour = True
        else:
            bt = datetime.strptime(birth_time_str, "%H:%M").time()
            hour, minute = bt.hour, bt.minute

        if not (1900 <= bd.year <= date.today().year):
            err = ("Only birth dates from 1900 onward are supported for precise analysis."
                   if is_en else "1900년 이후 출생만 정밀 분석이 가능합니다.")
            return render_template("result.html", error=err)

        # gender normalization
        if is_en:
            gender_internal = "남" if gender in ("M", "male", "Male", "남", "남자") else "여"
        else:
            gender_internal = gender

        saju = compute_saju(bd.year, bd.month, bd.day, hour, minute,
                            gender=gender_internal, name=name,
                            is_lunar=is_lunar, unknown_hour=unknown_hour)
        daewoons = compute_daewoon(saju)
        interp = interpret(saju)

        # English overrides for interpretation when lang=en
        if is_en:
            day_idx = _find_pillar_idx(saju.day_pillar.stem, saju.day_pillar.branch)
            en_info = DAY_PILLAR_INTERPRETATIONS_EN.get(day_idx)
            if en_info:
                interp["day_pillar_name"] = en_info[0]
                interp["day_pillar_headline"] = en_info[1]
                interp["day_pillar_detail"] = en_info[2]
            interp["ten_god_meanings"] = {k: v[1] for k, v in TEN_GOD_EN.items()}
            interp["twelve_stage_meaning"] = TWELVE_STAGE_EN
            interp["element_meaning"] = ELEMENT_EN
            # day master + element labels
            interp["summary_line"] = (
                f"{en_info[0] if en_info else ''} — {en_info[1] if en_info else ''}. "
                f"Day stem {STEM_EN[saju.day_pillar.stem]} ({ELEMENT_NAMES_EN[D.STEM_ELEMENT[saju.day_pillar.stem]]}) "
                f"is in '{TWELVE_STAGE_EN.get(saju.twelve_stages['day'], '')[:30]}…' state at the day branch."
            )

        return render_template("result.html",
                               saju=saju,
                               interp=interp,
                               daewoons=daewoons,
                               unknown_hour=unknown_hour,
                               stems_kr=D.HEAVENLY_STEMS_KR,
                               branches_kr=D.EARTHLY_BRANCHES_KR,
                               stems_hanja=D.HEAVENLY_STEMS,
                               branches_hanja=D.EARTHLY_BRANCHES)
    except (ValueError, KeyError) as e:
        err = f"Invalid input: {e}" if is_en else f"입력 형식이 올바르지 않습니다: {e}"
        return render_template("result.html", error=err)


def _find_pillar_idx(stem: int, branch: int) -> int:
    for i in range(60):
        if i % 10 == stem and i % 12 == branch:
            return i
    return 0


# ─────────────────────────────────────────────────────────────────
# 콘텐츠 페이지
# ─────────────────────────────────────────────────────────────────
@app.route("/basics")
@app.route("/en/basics")
def basics():
    return render_template("basics.html")


@app.route("/ten-gods")
@app.route("/en/ten-gods")
def ten_gods_page():
    if g.lang == "en":
        meanings = {k: v[1] for k, v in TEN_GOD_EN.items()}
    else:
        meanings = TEN_GOD_MEANING
    return render_template("ten_gods.html", meanings=meanings)


@app.route("/twelve-stages")
@app.route("/en/twelve-stages")
def twelve_stages_page():
    meanings = TWELVE_STAGE_EN if g.lang == "en" else TWELVE_STAGE_MEANING
    return render_template("twelve_stages.html", meanings=meanings)


@app.route("/five-elements")
@app.route("/en/five-elements")
def five_elements_page():
    meanings = ELEMENT_EN if g.lang == "en" else ELEMENT_MEANING
    return render_template("five_elements.html", meanings=meanings)


# ─────────────────────────────────────────────────────────────────
# 오늘의 운세
# ─────────────────────────────────────────────────────────────────
@app.route("/today")
@app.route("/today/<date_str>")
@app.route("/en/today")
@app.route("/en/today/<date_str>")
def today_fortune(date_str=None):
    try:
        if date_str:
            target = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            target = date.today()
    except ValueError:
        target = date.today()

    fortune = daily_fortune(target)
    yesterday = target - timedelta(days=1)
    tomorrow = target + timedelta(days=1)
    # 띠별 일일 키워드 12개 (간략)
    return render_template("today.html",
                           fortune=fortune,
                           target=target,
                           yesterday=yesterday.isoformat(),
                           tomorrow=tomorrow.isoformat(),
                           zodiac_traits=ZODIAC_TRAITS)


# ─────────────────────────────────────────────────────────────────
# 띠별 운세 12개
# ─────────────────────────────────────────────────────────────────
@app.route("/zodiac")
@app.route("/en/zodiac")
def zodiac_index():
    if g.lang == "en":
        # ZODIAC_TRAITS_EN is keyed by Korean name; we expose both KR key + EN data
        zodiacs = {k: ZODIAC_TRAITS_EN[k] for k in ZODIAC_TRAITS}
    else:
        zodiacs = ZODIAC_TRAITS
    return render_template("zodiac_index.html", zodiacs=zodiacs)


@app.route("/zodiac/<name>")
@app.route("/en/zodiac/<name>")
def zodiac_detail(name):
    # English path supports both EN slugs (rat, ox, ...) and KR names
    en_to_kr = {
        "rat": "쥐", "ox": "소", "tiger": "호랑이", "rabbit": "토끼",
        "dragon": "용", "snake": "뱀", "horse": "말", "goat": "양",
        "monkey": "원숭이", "rooster": "닭", "dog": "개", "pig": "돼지",
    }
    kr_name = en_to_kr.get(name.lower(), name)
    if kr_name not in ZODIAC_TRAITS:
        abort(404)
    fortune = zodiac_yearly_fortune(kr_name)
    if g.lang == "en":
        en_info = ZODIAC_TRAITS_EN[kr_name]
        fortune["name"] = en_info[0].split(" (")[1].rstrip(")")  # "Rat" extracted from "Zi (Rat)"
        fortune["trait"] = en_info
    return render_template("zodiac_detail.html",
                           zodiac=fortune,
                           zodiacs=ZODIAC_TRAITS_EN if g.lang == "en" else ZODIAC_TRAITS,
                           kr_name=kr_name)


# ─────────────────────────────────────────────────────────────────
# 궁합
# ─────────────────────────────────────────────────────────────────
@app.route("/compatibility", methods=["GET", "POST"])
@app.route("/en/compatibility", methods=["GET", "POST"])
def compatibility_page():
    if request.method == "GET":
        return render_template("compatibility.html",
                               today=date.today().isoformat(),
                               max_date=date.today().isoformat())
    try:
        p1 = {
            "name": request.form.get("p1_name", "").strip()[:30],
            "gender": request.form.get("p1_gender", "남"),
        }
        p2 = {
            "name": request.form.get("p2_name", "").strip()[:30],
            "gender": request.form.get("p2_gender", "여"),
        }
        for key, prefix in [(p1, "p1"), (p2, "p2")]:
            bd = datetime.strptime(request.form[f"{prefix}_birth_date"], "%Y-%m-%d").date()
            bt_str = request.form.get(f"{prefix}_birth_time", "")
            if bt_str:
                bt = datetime.strptime(bt_str, "%H:%M").time()
                h, m = bt.hour, bt.minute
            else:
                h, m = 12, 0
            key.update({"year": bd.year, "month": bd.month, "day": bd.day,
                        "hour": h, "minute": m})
        result = compatibility(p1, p2)
        return render_template("compatibility_result.html",
                               result=result,
                               stems_kr=D.HEAVENLY_STEMS_KR,
                               branches_kr=D.EARTHLY_BRANCHES_KR)
    except (KeyError, ValueError) as e:
        return render_template("compatibility.html",
                               error=f"입력값을 확인해 주세요: {e}",
                               today=date.today().isoformat(),
                               max_date=date.today().isoformat())


# ─────────────────────────────────────────────────────────────────
# 용어 사전
# ─────────────────────────────────────────────────────────────────
@app.route("/glossary")
@app.route("/en/glossary")
def glossary_page():
    grouped = {}
    src = GLOSSARY_EN if g.lang == "en" else GLOSSARY
    for term, cat, desc in src:
        grouped.setdefault(cat, []).append({"term": term, "desc": desc})
    return render_template("glossary.html", grouped=grouped, total=len(src))


@app.route("/sixty-pillars")
@app.route("/en/sixty-pillars")
def sixty_pillars_index():
    pillars = []
    src = DAY_PILLAR_INTERPRETATIONS_EN if g.lang == "en" else DAY_PILLAR_INTERPRETATIONS
    for i in range(60):
        info = src.get(i)
        if info:
            pillars.append({
                "index": i,
                "name": info[0],
                "headline": info[1],
                "stem_kr": D.HEAVENLY_STEMS_KR[i % 10] if g.lang != "en" else STEM_EN[i % 10],
                "branch_kr": D.EARTHLY_BRANCHES_KR[i % 12] if g.lang != "en" else BRANCH_EN[i % 12],
                "element": D.ELEMENTS_KR[D.STEM_ELEMENT[i % 10]] if g.lang != "en" else ELEMENT_NAMES_EN[D.STEM_ELEMENT[i % 10]],
            })
    return render_template("sixty_pillars.html", pillars=pillars)


@app.route("/sixty-pillars/<int:idx>")
@app.route("/en/sixty-pillars/<int:idx>")
def sixty_pillar_detail(idx):
    if not (0 <= idx < 60):
        abort(404)
    src = DAY_PILLAR_INTERPRETATIONS_EN if g.lang == "en" else DAY_PILLAR_INTERPRETATIONS
    info = src.get(idx)
    if not info:
        abort(404)
    if g.lang == "en":
        stem_label = STEM_EN[idx % 10]
        branch_label = BRANCH_EN[idx % 12]
        elem_label = ELEMENT_NAMES_EN[D.STEM_ELEMENT[idx % 10]]
    else:
        stem_label = D.HEAVENLY_STEMS_KR[idx % 10]
        branch_label = D.EARTHLY_BRANCHES_KR[idx % 12]
        elem_label = D.ELEMENTS_KR[D.STEM_ELEMENT[idx % 10]]
    return render_template("pillar_detail.html",
                           idx=idx,
                           name=info[0],
                           headline=info[1],
                           detail=info[2],
                           stem_kr=stem_label,
                           branch_kr=branch_label,
                           stem_hanja=D.HEAVENLY_STEMS[idx % 10],
                           branch_hanja=D.EARTHLY_BRANCHES[idx % 12],
                           element=elem_label,
                           prev_idx=(idx - 1) % 60,
                           next_idx=(idx + 1) % 60)


# ─────────────────────────────────────────────────────────────────
# 정책 페이지 (AdSense 승인 필수)
# ─────────────────────────────────────────────────────────────────
@app.route("/about")
@app.route("/en/about")
def about():
    return render_template("about.html")


@app.route("/privacy")
@app.route("/en/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
@app.route("/en/terms")
def terms():
    return render_template("terms.html")


# ─────────────────────────────────────────────────────────────────
# SEO / 광고 인프라 파일
# ─────────────────────────────────────────────────────────────────
@app.route("/ads.txt")
def ads_txt():
    """Google AdSense 인증용 ads.txt. ADSENSE_CLIENT_ID(ca-pub-XXXX) 사용."""
    pub_id = ADSENSE_CLIENT_ID.replace("ca-pub-", "").strip()
    if not pub_id:
        return Response("# AdSense not yet configured.\n", mimetype="text/plain")
    body = f"google.com, pub-{pub_id}, DIRECT, f08c47fec0942fa0\n"
    return Response(body, mimetype="text/plain")


@app.route("/robots.txt")
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        # /result는 SEO indexable로 개방 — long-tail traffic 폭발 기대
        # 각 사주 결과 URL이 unique 컨텐츠
        "Allow: /result\n"
        "Allow: /en/result\n"
        f"Sitemap: {request.url_root}sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


# ─────────────────────────────────────────────────────────────────
# llms.txt — LLM 크롤러용 사이트 인덱스 (llmstxt.org 표준)
# ─────────────────────────────────────────────────────────────────
@app.route("/llms.txt")
def llms_txt():
    body = """# Saju Fortune — Korean Four-Pillars Astrology

> Free, no-signup Korean four-pillars (saju) astrology calculator with Korean and English interpretations. Day-pillar archetype, five elements, ten gods, twelve life stages, daily luck, compatibility check.

## Calculators
- [Main calculator](/): birth date+time -> 4x2 four-pillars grid
- [Today's luck](/today): current-day pillar reading
- [Compatibility](/compatibility): two-person saju matching
- [Yearly fortune](/yearly): annual outlook

## Reference (60 day-pillars)
- [60 day-pillars index](/sixty-pillars): personality archetype directory
- [60 pillars x career](/sixty-pillars/0/career): career fit by day-pillar
- [60 pillars x love](/sixty-pillars/0/love): romantic compatibility patterns

## Theory
- [Ten Gods](/ten-gods): relational roles framework
- [Twelve Life Stages](/twelve-stages): life-cycle energy
- [Five Elements](/five-elements): elemental balance
- [Heavenly Stems](/stems): 10 heavenly stems
- [Earthly Branches](/branches): 12 earthly branches
- [Glossary](/glossary): saju terminology

## English version
- [/en](/en): full English interpretation
"""
    return Response(body, mimetype="text/plain; charset=utf-8")


# ─────────────────────────────────────────────────────────────────
# security.txt — RFC 9116 책임감 있는 취약점 보고
# ─────────────────────────────────────────────────────────────────
@app.route("/.well-known/security.txt")
def security_txt():
    body = """Contact: mailto:leekyuha.iambox@gmail.com
Expires: 2027-12-31T23:59:59.000Z
Preferred-Languages: ko, en
Canonical: https://tarofortune.pythonanywhere.com/.well-known/security.txt
Policy: We welcome responsible disclosure. Please contact via email with proof-of-concept and we will respond within 7 business days.
"""
    return Response(body, mimetype="text/plain; charset=utf-8")


# RSS feed는 line 868~의 기존 구현 사용 (/feed.xml + /en/feed.xml).
# 추가 alias /rss.xml 만 제공 — 어그리게이터 호환성.
@app.route("/rss.xml")
def rss_alias():
    return redirect(url_for("rss_feed"), code=301)


# ─────────────────────────────────────────────────────────────────
# IndexNow 키 파일 (Bing·Yandex·Naver 소유권 증명)
# ─────────────────────────────────────────────────────────────────
@app.route("/" + INDEXNOW_KEY + ".txt")
def indexnow_key_file():
    return Response(INDEXNOW_KEY, mimetype="text/plain")


# ─────────────────────────────────────────────────────────────────
# 사주 결과 동적 OG 이미지 (PNG) — 공유 시 본인 사주가 박힌 카드
# /og/result.png?y=1990&m=5&d=15&h=14&min=30&g=남&n=홍길동&lang=ko
# ─────────────────────────────────────────────────────────────────
@app.route("/og/result.png")
def og_result_card():
    try:
        from saju.og_card import render_result_card
        from saju.calculator import compute_saju
        y = int(request.args.get("y", 1990))
        m = int(request.args.get("m", 1))
        d = int(request.args.get("d", 1))
        h = int(request.args.get("h", 12))
        mi = int(request.args.get("min", 0))
        gender = request.args.get("g", "남")
        name = request.args.get("n", "")[:20]
        lang = request.args.get("lang", "ko")
        unknown_hour = request.args.get("uh", "0") == "1"

        saju = compute_saju(y, m, d, h, mi, gender=gender, name=name,
                            unknown_hour=unknown_hour)

        def p_dict(p):
            return None if p is None else {"stem": p.stem, "branch": p.branch}

        # 일주 인덱스
        day_idx = 0
        for i in range(60):
            if i % 10 == saju.day_pillar.stem and i % 12 == saju.day_pillar.branch:
                day_idx = i; break

        png = render_result_card(
            year_pillar=p_dict(saju.year_pillar),
            month_pillar=p_dict(saju.month_pillar),
            day_pillar=p_dict(saju.day_pillar),
            hour_pillar=p_dict(saju.hour_pillar),
            day_idx=day_idx, lang=lang, name=name,
        )
        return Response(png, mimetype="image/png",
                        headers={"Cache-Control": "public, max-age=86400"})
    except Exception as e:
        # 실패 시 기본 OG 반환
        return redirect(url_for("static",
                                filename=("img/og-default-en.png" if request.args.get("lang") == "en"
                                          else "img/og-default.png")))


# ─────────────────────────────────────────────────────────────────
# 웹훅 — 외부 cron이 매일 호출해서 봇·색인 작업 트리거
# 인증: ?key=<CRON_SECRET>
# ?task=lemmy | mastodon | indexnow
# ─────────────────────────────────────────────────────────────────
def _run_in_thread(target):
    """봇 작업을 백그라운드 스레드로 실행 (요청 응답 막지 않게)."""
    t = threading.Thread(target=target, daemon=True)
    t.start()


@app.route("/api/cron/<task>")
def cron_webhook(task):
    if not CRON_SECRET or request.args.get("key", "") != CRON_SECRET:
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    task = task.lower()
    if task == "lemmy":
        from lemmy_bot import run_daily as lemmy_daily
        _run_in_thread(lemmy_daily)
        return jsonify({"ok": True, "task": "lemmy", "scheduled": True})
    elif task == "mastodon":
        from mastodon_bot import run_daily as mast_daily
        _run_in_thread(mast_daily)
        return jsonify({"ok": True, "task": "mastodon", "scheduled": True})
    elif task == "indexnow":
        from auto_index import submit_indexnow, ping_google_sitemap, ping_bing_sitemap
        def _all():
            submit_indexnow()
            ping_google_sitemap()
            ping_bing_sitemap()
        _run_in_thread(_all)
        return jsonify({"ok": True, "task": "indexnow", "scheduled": True})
    elif task == "all":
        from lemmy_bot import run_daily as lemmy_daily
        from mastodon_bot import run_daily as mast_daily
        from auto_index import submit_indexnow
        def _all():
            try:
                lemmy_daily()
            except Exception:
                pass
            try:
                mast_daily()
            except Exception:
                pass
            try:
                submit_indexnow()
            except Exception:
                pass
        _run_in_thread(_all)
        return jsonify({"ok": True, "task": "all", "scheduled": True})
    return jsonify({"ok": False, "error": f"Unknown task: {task}"}), 400


# ─────────────────────────────────────────────────────────────────
# RSS 피드 — 일일 운세 + 60갑자 일주별 풀이
# 외부 어그리게이터/리더에 노출 → 자연 트래픽 유입
# ─────────────────────────────────────────────────────────────────
@app.route("/feed.xml")
@app.route("/en/feed.xml")
def rss_feed():
    base = request.url_root.rstrip("/")
    is_en = (g.lang == "en")
    lang_prefix = "/en" if is_en else ""

    title = "Saju Myeongri Daily — Day Pillar Reading Feed" if is_en else "사주명리 데일리 — 일주 풀이 피드"
    description = ("Daily fortune by Day Pillar and 60-Gapja archetype readings."
                   if is_en else "오늘의 일진과 60갑자 일주별 풀이를 매일 안내합니다.")

    items = []
    today = date.today()
    # 최근 일주일 일진
    for i in range(7):
        d = today - timedelta(days=i)
        fortune = daily_fortune(d)
        item_title = (f"Today's fortune {d.isoformat()} — {fortune['day_pillar_name']}" if is_en
                      else f"오늘의 일진 {d.isoformat()} — {fortune['day_pillar_name']}")
        item_link = f"{base}{lang_prefix}/today/{d.isoformat()}"
        item_desc = fortune.get("keyword_body", "")
        items.append(
            f"<item><title>{_xml_esc(item_title)}</title>"
            f"<link>{item_link}</link>"
            f"<guid>{item_link}</guid>"
            f"<pubDate>{d.strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>"
            f"<description>{_xml_esc(item_desc)}</description></item>"
        )
    # 60갑자 일주별 풀이 (정적이므로 회전 표시)
    src = DAY_PILLAR_INTERPRETATIONS_EN if is_en else DAY_PILLAR_INTERPRETATIONS
    rotation_start = (today.toordinal() * 7) % 60
    for offset in range(7):
        idx = (rotation_start + offset) % 60
        info = src.get(idx)
        if not info:
            continue
        item_title = (f"Day Pillar Reading: {info[0]}" if is_en
                      else f"60갑자 일주 풀이: {info[0]}")
        item_link = f"{base}{lang_prefix}/sixty-pillars/{idx}"
        items.append(
            f"<item><title>{_xml_esc(item_title)}</title>"
            f"<link>{item_link}</link>"
            f"<guid>{item_link}</guid>"
            f"<description>{_xml_esc(info[1])}</description></item>"
        )

    body = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
        f"<channel>"
        f"<title>{_xml_esc(title)}</title>"
        f"<link>{base}{lang_prefix}/</link>"
        f'<atom:link href="{base}{lang_prefix}/feed.xml" rel="self" type="application/rss+xml"/>'
        f"<description>{_xml_esc(description)}</description>"
        f"<language>{'en' if is_en else 'ko'}</language>"
        f"<lastBuildDate>{today.strftime('%a, %d %b %Y 00:00:00 +0000')}</lastBuildDate>"
        + "".join(items)
        + "</channel></rss>"
    )
    return Response(body, mimetype="application/rss+xml")


def _xml_esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


# ─────────────────────────────────────────────────────────────────
# 일주별 직업 / 연애운 페이지 (롱테일 SEO — 120 추가 페이지)
# ─────────────────────────────────────────────────────────────────
@app.route("/sixty-pillars/<int:idx>/career")
@app.route("/en/sixty-pillars/<int:idx>/career")
def pillar_career(idx):
    return _pillar_topic_page(idx, "career")


@app.route("/sixty-pillars/<int:idx>/love")
@app.route("/en/sixty-pillars/<int:idx>/love")
def pillar_love(idx):
    return _pillar_topic_page(idx, "love")


def _pillar_topic_page(idx, topic):
    if not (0 <= idx < 60):
        abort(404)
    src = DAY_PILLAR_INTERPRETATIONS_EN if g.lang == "en" else DAY_PILLAR_INTERPRETATIONS
    info = src.get(idx)
    if not info:
        abort(404)
    pillar_name = info[0]
    headlines = CAREER_HEADLINES if topic == "career" else LOVE_HEADLINES
    topic_body = headlines.get(idx, ("", ""))
    return render_template("pillar_topic.html",
                           idx=idx,
                           pillar_name=pillar_name,
                           headline=info[1],
                           topic=topic,
                           topic_title=topic_body[0],
                           topic_body=topic_body[1],
                           prev_idx=(idx - 1) % 60,
                           next_idx=(idx + 1) % 60)


# ─────────────────────────────────────────────────────────────────
# 주간/월간 운세 (시즌 키워드 점령)
# ─────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────
# 십신 개별 상세 페이지
# ─────────────────────────────────────────────────────────────────
@app.route("/ten-gods/<name>")
def ten_god_detail(name):
    info = TEN_GODS_DETAIL.get(name)
    if not info:
        abort(404)
    return render_template("god_detail.html", name=name, info=info,
                           all_names=list(TEN_GODS_DETAIL.keys()))


# ─────────────────────────────────────────────────────────────────
# 십이운성 개별 상세 페이지
# ─────────────────────────────────────────────────────────────────
@app.route("/twelve-stages/<name>")
def twelve_stage_detail(name):
    info = TWELVE_STAGES_DETAIL.get(name)
    if not info:
        abort(404)
    return render_template("stage_detail.html", name=name, info=info,
                           all_names=list(TWELVE_STAGES_DETAIL.keys()))


# ─────────────────────────────────────────────────────────────────
# 12지지 / 지장간 개별 상세
# ─────────────────────────────────────────────────────────────────
@app.route("/branches/<name>")
def branch_detail(name):
    info = HIDDEN_STEMS_DETAIL.get(name)
    if not info:
        abort(404)
    return render_template("branch_detail.html", name=name, info=info,
                           all_names=list(HIDDEN_STEMS_DETAIL.keys()))


@app.route("/branches")
def branch_index():
    items = [(n, v) for n, v in HIDDEN_STEMS_DETAIL.items()]
    return render_template("branch_index.html", items=items)


# ─────────────────────────────────────────────────────────────────
# 천간 개별 상세 페이지
# ─────────────────────────────────────────────────────────────────
@app.route("/stems/<name>")
def stem_detail(name):
    info = HEAVENLY_STEMS_DETAIL.get(name)
    if not info:
        abort(404)
    return render_template("stem_detail.html", name=name, info=info,
                           all_names=list(HEAVENLY_STEMS_DETAIL.keys()))


@app.route("/stems")
def stem_index():
    items = [(n, v) for n, v in HEAVENLY_STEMS_DETAIL.items()]
    return render_template("stem_index.html", items=items)


# ─────────────────────────────────────────────────────────────────
# 사주 퀴즈 (인터랙티브 — 일주 맞히기)
# ─────────────────────────────────────────────────────────────────
@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")


# ─────────────────────────────────────────────────────────────────
# 일일 운세 이메일 구독 신청 (리드 수집)
# ─────────────────────────────────────────────────────────────────
@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        if not email or "@" not in email:
            return render_template("subscribe.html", error="올바른 이메일을 입력해 주세요.")
        # 파일로 저장 (DB 없이 간단히)
        import os as _os
        sub_file = _os.path.join(_os.path.dirname(__file__), ".subscribers.txt")
        try:
            with open(sub_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()}\t{email}\n")
        except Exception:
            pass
        return render_template("subscribe.html", success=True, email=email)
    return render_template("subscribe.html")


# ─────────────────────────────────────────────────────────────────
# 명문장 모음 (인용 검색 트래픽)
# ─────────────────────────────────────────────────────────────────
@app.route("/quotes")
def quotes_page():
    return render_template("quotes.html")


# ─────────────────────────────────────────────────────────────────
# 24절기 페이지 (한국 검색 키워드 점령)
# ─────────────────────────────────────────────────────────────────
@app.route("/solar-terms")
@app.route("/en/solar-terms")
def solar_terms_index():
    terms = []
    for i, info in SOLAR_TERM_DETAIL.items():
        terms.append({"idx": i, **info})
    return render_template("solar_terms.html", terms=terms)


@app.route("/solar-terms/<int:idx>")
@app.route("/en/solar-terms/<int:idx>")
def solar_term_detail(idx):
    if not (0 <= idx <= 23):
        abort(404)
    info = SOLAR_TERM_DETAIL.get(idx)
    if not info:
        abort(404)
    # 올해 이 절기의 정확한 시점 계산
    from saju.calculator import solar_term_jd, jd_to_gregorian
    today = date.today()
    jd_this_year = solar_term_jd(today.year, idx) + 9 / 24  # KST
    y, mo, d, hh, mm, _ = jd_to_gregorian(jd_this_year)
    actual_time = f"{y}-{mo:02d}-{d:02d} {hh:02d}:{mm:02d} KST"
    return render_template("solar_term_detail.html",
                           idx=idx, info=info, actual_time=actual_time,
                           prev_idx=(idx - 1) % 24, next_idx=(idx + 1) % 24)


# ─────────────────────────────────────────────────────────────────
# 신년 운세 (시즌 키워드 - "2026년 운세")
# ─────────────────────────────────────────────────────────────────
@app.route("/yearly")
@app.route("/yearly/<int:year>")
@app.route("/en/yearly")
@app.route("/en/yearly/<int:year>")
def yearly_fortune(year=None):
    target_year = year or date.today().year
    if not (1900 <= target_year <= 2100):
        abort(404)
    # 연도의 갑자 산출 (입춘 기준)
    year_stem = (target_year - 4) % 10
    year_branch = (target_year - 4) % 12
    year_pillar_name = D.HEAVENLY_STEMS_KR[year_stem] + D.EARTHLY_BRANCHES_KR[year_branch]
    year_hanja = D.HEAVENLY_STEMS[year_stem] + D.EARTHLY_BRANCHES[year_branch]
    year_element = D.ELEMENTS_KR[D.STEM_ELEMENT[year_stem]]
    year_animal = D.ZODIAC_ANIMALS[year_branch]

    # 12띠별 그 해 운세
    zodiacs = []
    for zname in ZODIAC_TRAITS:
        fortune = zodiac_yearly_fortune(zname, today=date(target_year, 6, 15))
        zodiacs.append({"name": zname, **fortune})

    return render_template("yearly.html",
                           year=target_year,
                           year_pillar=year_pillar_name,
                           year_hanja=year_hanja,
                           year_element=year_element,
                           year_animal=year_animal,
                           zodiacs=zodiacs)


# ─────────────────────────────────────────────────────────────────
# 음력 → 양력 변환기 (유용 유틸리티)
# 정확한 한국 음력 변환은 천문연 데이터 필요 → 여기서는 근사 알고리즘
# ─────────────────────────────────────────────────────────────────
@app.route("/lunar-converter", methods=["GET", "POST"])
@app.route("/en/lunar-converter", methods=["GET", "POST"])
def lunar_converter():
    if request.method == "POST":
        try:
            ly = int(request.form["lunar_year"])
            lm = int(request.form["lunar_month"])
            ld = int(request.form["lunar_day"])
            is_leap = request.form.get("is_leap") == "on"
            from saju.lunar import lunar_to_solar
            sd = lunar_to_solar(ly, lm, ld, is_leap)
            return render_template("lunar_converter.html",
                                   lunar=(ly, lm, ld, is_leap),
                                   solar=sd)
        except (KeyError, ValueError) as e:
            return render_template("lunar_converter.html",
                                   error=f"입력값 오류: {e}")
    return render_template("lunar_converter.html")


@app.route("/weekly")
@app.route("/en/weekly")
def weekly_fortune():
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]
    week_fortunes = [daily_fortune(d) for d in days]
    return render_template("weekly.html", week_fortunes=week_fortunes,
                           week_start=today, week_end=today + timedelta(days=6))


@app.route("/monthly")
@app.route("/en/monthly")
def monthly_fortune():
    today = date.today()
    # 30일치 일진 미리보기
    days = [today + timedelta(days=i) for i in range(30)]
    month_fortunes = [daily_fortune(d) for d in days]
    return render_template("monthly.html",
                           month_fortunes=month_fortunes,
                           month_start=today,
                           month_end=today + timedelta(days=29))


@app.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    today_iso = date.today().isoformat()
    base_pages = [
        ("/", "1.0", "daily"),
        ("/today", "0.9", "daily"),
        ("/compatibility", "0.9", "weekly"),
        ("/zodiac", "0.8", "weekly"),
        ("/sixty-pillars", "0.8", "monthly"),
        ("/basics", "0.7", "monthly"),
        ("/ten-gods", "0.7", "monthly"),
        ("/twelve-stages", "0.7", "monthly"),
        ("/five-elements", "0.7", "monthly"),
        ("/glossary", "0.6", "monthly"),
        ("/about", "0.4", "yearly"),
        ("/privacy", "0.3", "yearly"),
        ("/terms", "0.3", "yearly"),
    ]
    zodiacs_kr = ["쥐", "소", "호랑이", "토끼", "용", "뱀",
                  "말", "양", "원숭이", "닭", "개", "돼지"]
    zodiacs_en = ["rat", "ox", "tiger", "rabbit", "dragon", "snake",
                  "horse", "goat", "monkey", "rooster", "dog", "pig"]

    def emit(path, prio, freq, alt_en=None):
        """hreflang alternate links 포함."""
        ko_url = f"{base}{path}"
        en_url = f"{base}/en{alt_en if alt_en is not None else path}"
        ko_block = (
            f"<url><loc>{ko_url}</loc>"
            f"<lastmod>{today_iso}</lastmod>"
            f"<changefreq>{freq}</changefreq>"
            f"<priority>{prio}</priority>"
            f'<xhtml:link rel="alternate" hreflang="ko" href="{ko_url}"/>'
            f'<xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>'
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{ko_url}"/>'
            f"</url>"
        )
        en_block = (
            f"<url><loc>{en_url}</loc>"
            f"<lastmod>{today_iso}</lastmod>"
            f"<changefreq>{freq}</changefreq>"
            f"<priority>{prio}</priority>"
            f'<xhtml:link rel="alternate" hreflang="ko" href="{ko_url}"/>'
            f'<xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>'
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{ko_url}"/>'
            f"</url>"
        )
        return ko_block + en_block

    items = []
    for u, prio, freq in base_pages:
        items.append(emit(u, prio, freq))
    for z_kr, z_en in zip(zodiacs_kr, zodiacs_en):
        from urllib.parse import quote
        items.append(emit(f"/zodiac/{quote(z_kr)}", "0.7", "weekly",
                          alt_en=f"/zodiac/{z_en}"))
    for i in range(60):
        items.append(emit(f"/sixty-pillars/{i}", "0.6", "monthly"))
        items.append(emit(f"/sixty-pillars/{i}/career", "0.55", "monthly"))
        items.append(emit(f"/sixty-pillars/{i}/love", "0.55", "monthly"))

    # ─── Long-tail SEO: 인기 사주 케이스 60개 sample 결과 URL ───
    # 60갑자 일주를 모두 커버하는 대표 생년월일 60개를 sitemap에 등록.
    # 각 결과 페이지가 unique URL + unique content → Google 색인 가능.
    # 60 sample URLs × 2 lang = 120 추가 indexable pages.
    SAMPLE_BIRTHS = [
        # (year, month, day, hour, minute, gender)
        # 1980s~2000s 대표 케이스 — 사용자가 검색 시 자기 생일과 비슷한 케이스를 찾음
        (1985, 3, 15, 14, 0, "남"),  (1985, 7, 22, 8, 30, "여"),
        (1987, 1, 10, 22, 0, "남"),  (1988, 5, 5, 6, 0, "여"),
        (1989, 9, 17, 11, 30, "남"), (1990, 2, 28, 16, 0, "여"),
        (1990, 6, 6, 9, 0, "남"),    (1990, 11, 11, 18, 30, "여"),
        (1991, 4, 4, 13, 0, "남"),   (1992, 8, 8, 7, 30, "여"),
        (1992, 12, 25, 0, 30, "남"), (1993, 3, 3, 15, 0, "여"),
        (1994, 5, 14, 10, 0, "남"),  (1994, 10, 31, 22, 30, "여"),
        (1995, 1, 1, 12, 0, "남"),   (1995, 8, 15, 17, 0, "여"),
        (1996, 2, 14, 14, 30, "남"), (1996, 6, 30, 8, 0, "여"),
        (1997, 4, 20, 11, 0, "남"),  (1997, 11, 22, 20, 30, "여"),
        (1998, 5, 18, 9, 30, "남"),  (1998, 9, 9, 15, 30, "여"),
        (1999, 1, 31, 13, 0, "남"),  (1999, 7, 7, 19, 0, "여"),
        (2000, 1, 1, 0, 0, "남"),    (2000, 5, 25, 12, 30, "여"),
        (2000, 10, 10, 16, 30, "남"),(2001, 3, 8, 9, 0, "여"),
        (2001, 6, 21, 18, 0, "남"),  (2001, 12, 12, 22, 0, "여"),
        (1980, 4, 17, 10, 30, "남"), (1980, 11, 5, 6, 30, "여"),
        (1981, 7, 14, 14, 0, "남"),  (1982, 2, 22, 21, 0, "여"),
        (1983, 8, 30, 11, 30, "남"), (1984, 12, 4, 17, 30, "여"),
        (1986, 3, 28, 8, 0, "남"),   (1986, 10, 16, 15, 30, "여"),
        (1989, 6, 1, 12, 0, "남"),   (1991, 9, 23, 19, 30, "여"),
        (1993, 11, 11, 7, 0, "남"),  (1995, 4, 4, 14, 30, "여"),
        (1997, 8, 28, 11, 0, "남"),  (1999, 12, 31, 23, 30, "여"),
        (2002, 5, 5, 10, 0, "남"),   (2003, 9, 17, 16, 0, "여"),
        (2004, 1, 28, 19, 0, "남"),  (2005, 7, 13, 8, 30, "여"),
        (1975, 6, 18, 12, 0, "남"),  (1976, 2, 14, 20, 0, "여"),
        (1977, 10, 8, 9, 30, "남"),  (1978, 4, 27, 15, 0, "여"),
        (1979, 11, 30, 17, 0, "남"), (1972, 8, 8, 6, 0, "여"),
        (1973, 12, 1, 22, 30, "남"), (1974, 3, 9, 13, 30, "여"),
        (1970, 5, 5, 11, 0, "남"),   (1971, 9, 19, 18, 30, "여"),
        (1968, 7, 7, 14, 30, "남"),  (1969, 2, 11, 7, 0, "여"),
    ]
    from urllib.parse import urlencode
    for (y, mo, dd, hr, mn, gen) in SAMPLE_BIRTHS[:60]:
        qs = urlencode({"y": y, "m": mo, "d": dd, "h": hr, "min": mn, "g": gen})
        # Sample 결과 URL — 각각 unique 사주 풀이
        items.append(
            f"<url><loc>{base}/result?{qs}</loc>"
            f"<lastmod>{today_iso}</lastmod>"
            f"<changefreq>monthly</changefreq>"
            f"<priority>0.5</priority>"
            f'<xhtml:link rel="alternate" hreflang="ko" href="{base}/result?{qs}"/>'
            f'<xhtml:link rel="alternate" hreflang="en" href="{base}/en/result?{qs}"/>'
            f"</url>"
        )
        items.append(
            f"<url><loc>{base}/en/result?{qs}</loc>"
            f"<lastmod>{today_iso}</lastmod>"
            f"<changefreq>monthly</changefreq>"
            f"<priority>0.5</priority>"
            f'<xhtml:link rel="alternate" hreflang="ko" href="{base}/result?{qs}"/>'
            f'<xhtml:link rel="alternate" hreflang="en" href="{base}/en/result?{qs}"/>'
            f"</url>"
        )

    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">'
            + "".join(items) + "</urlset>")
    return Response(body, mimetype="application/xml")


# ─────────────────────────────────────────────────────────────────
# API 엔드포인트 (JSON) — 향후 모바일/외부 연동용
# ─────────────────────────────────────────────────────────────────
@app.route("/api/saju", methods=["POST"])
def api_saju():
    data = request.get_json(silent=True) or {}
    try:
        y = int(data["year"]); m = int(data["month"]); d = int(data["day"])
        h = int(data.get("hour", 12)); mi = int(data.get("minute", 0))
        gender = data.get("gender", "남")
        unknown_hour = bool(data.get("unknown_hour", False))
        lang = data.get("lang", "ko")
        saju = compute_saju(y, m, d, h, mi, gender=gender, unknown_hour=unknown_hour)
        daewoons = compute_daewoon(saju)
        interp = interpret(saju)

        # 일주 인덱스 계산
        day_idx = 0
        for i in range(60):
            if i % 10 == saju.day_pillar.stem and i % 12 == saju.day_pillar.branch:
                day_idx = i
                break

        # 영문 데이터 오버라이드
        if lang == "en":
            en_info = DAY_PILLAR_INTERPRETATIONS_EN.get(day_idx)
            if en_info:
                interp["day_pillar_name"] = en_info[0]
                interp["day_pillar_headline"] = en_info[1]
                interp["day_pillar_detail"] = en_info[2]

        return jsonify({
            "ok": True,
            "result": saju.to_dict(),
            "interpretation": interp,
            "daewoons": daewoons,
            "day_pillar_index": day_idx,
        })
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/today")
def api_today():
    """오늘의 일진 (선택: ?date=YYYY-MM-DD)."""
    try:
        ds = request.args.get("date")
        d = datetime.strptime(ds, "%Y-%m-%d").date() if ds else date.today()
        return jsonify({"ok": True, **{k: (v.isoformat() if isinstance(v, date) else v)
                                       for k, v in daily_fortune(d).items()}})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/pillars")
def api_pillars():
    """60갑자 일주별 핵심 풀이 전체 목록."""
    src = DAY_PILLAR_INTERPRETATIONS_EN if request.args.get("lang") == "en" else DAY_PILLAR_INTERPRETATIONS
    return jsonify({
        "ok": True,
        "pillars": [{"index": i, "name": src[i][0], "headline": src[i][1],
                     "detail": src[i][2]} for i in range(60)],
    })


@app.route("/api/pillar/<int:idx>")
def api_pillar_detail(idx):
    """특정 일주 상세."""
    if not (0 <= idx < 60):
        return jsonify({"ok": False, "error": "index out of range"}), 404
    src = DAY_PILLAR_INTERPRETATIONS_EN if request.args.get("lang") == "en" else DAY_PILLAR_INTERPRETATIONS
    info = src[idx]
    return jsonify({
        "ok": True,
        "index": idx,
        "name": info[0],
        "headline": info[1],
        "detail": info[2],
        "stem_kr": D.HEAVENLY_STEMS_KR[idx % 10],
        "branch_kr": D.EARTHLY_BRANCHES_KR[idx % 12],
        "stem_hanja": D.HEAVENLY_STEMS[idx % 10],
        "branch_hanja": D.EARTHLY_BRANCHES[idx % 12],
        "element": D.ELEMENTS_KR[D.STEM_ELEMENT[idx % 10]],
    })


@app.route("/api/zodiac/<name>")
def api_zodiac(name):
    """띠별 운세 — name = 쥐, 소, 호랑이, ... 또는 영문 rat/ox/tiger/..."""
    en_to_kr = {"rat": "쥐", "ox": "소", "tiger": "호랑이", "rabbit": "토끼",
                "dragon": "용", "snake": "뱀", "horse": "말", "goat": "양",
                "monkey": "원숭이", "rooster": "닭", "dog": "개", "pig": "돼지"}
    kr_name = en_to_kr.get(name.lower(), name)
    if kr_name not in ZODIAC_TRAITS:
        return jsonify({"ok": False, "error": "unknown zodiac"}), 404
    fortune = zodiac_yearly_fortune(kr_name)
    # daily_fortune 안의 date 객체 직렬화
    today_info = {k: (v.isoformat() if isinstance(v, date) else v)
                  for k, v in fortune["today"].items()}
    return jsonify({
        "ok": True,
        "name": kr_name,
        "trait": fortune["trait"],
        "this_year": fortune["this_year"],
        "this_year_number": fortune["this_year_number"],
        "relations": fortune["relations"],
        "today": today_info,
    })


@app.route("/api/compatibility", methods=["POST"])
def api_compatibility():
    """두 사람 사주 궁합 분석."""
    data = request.get_json(silent=True) or {}
    try:
        p1 = data["p1"]; p2 = data["p2"]
        result = compatibility(p1, p2)
        return jsonify({
            "ok": True,
            "score": result["score"],
            "grade": result["grade"],
            "advice": result["advice"],
            "notes": result["notes"],
            "p1": result["p1"].to_dict(),
            "p2": result["p2"].to_dict(),
        })
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ─────────────────────────────────────────────────────────────────
# 에러 핸들러
# ─────────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
