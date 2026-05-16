"""다국어 지원 — 한국어(ko, default) / 영어(en).

- URL prefix `/en/...` 으로 영어 페이지 접근
- Flask request.endpoint + g.lang 로 현재 언어 추적
- t(key) 함수 또는 templates 의 {{ t('key') }} 로 번역 호출
- HTTP Accept-Language 헤더 기반 첫 방문자 자동 리다이렉트
"""
from __future__ import annotations
from flask import g, request, url_for

LANGS = ("ko", "en")
DEFAULT_LANG = "ko"


# ─── UI 문자열 번역 사전 ─────────────────────────────────────
UI = {
    # ── 사이트 메타 ──
    "site_name": ("사주명리 — 운명의 설계도", "Saju Myeongri — Blueprint of Destiny"),
    "site_tagline": (
        "1,800년 동양철학의 지혜로 당신의 사주를 풀어드립니다",
        "Unfolding your destiny through 1,800 years of East Asian wisdom"
    ),
    "site_description_default": (
        "정확한 사주 사기둥, 십신, 십이운성, 오행 분석을 무료로 제공합니다.",
        "Free, accurate analysis of Saju Four Pillars, Ten Gods, Twelve Life Stages, and Five Elements.",
    ),

    # ── 네비게이션 ──
    "nav_saju": ("사주 보기", "Read My Saju"),
    "nav_today": ("오늘의 운세", "Today's Fortune"),
    "nav_zodiac": ("띠별 운세", "Zodiac Fortune"),
    "nav_compatibility": ("궁합", "Compatibility"),
    "nav_pillars": ("60갑자", "60 Pillars"),
    "nav_basics": ("사주 기초", "Saju Basics"),
    "nav_glossary": ("용어 사전", "Glossary"),

    # ── Hero ──
    "hero_title": ("당신의 사주, 운명의 설계도", "Your Saju — The Blueprint of Destiny"),
    "hero_subtitle": (
        "생년월일시 하나로 펼쳐지는 1,800년 동양철학의 통찰",
        "Insight from 1,800 years of East Asian philosophy, unfolded from your birth date and time",
    ),
    "hero_meta": (
        "정통 명리학 알고리즘 · 24절기 자동 보정 · 완전 무료",
        "Authentic Myeongri algorithm · 24 solar-term auto-correction · 100% free",
    ),

    # ── 폼 ──
    "form_title": ("사주 입력", "Enter Your Birth Info"),
    "form_name": ("이름", "Name"),
    "form_name_placeholder": ("이름 또는 별명", "Name or nickname"),
    "form_optional": ("선택", "optional"),
    "form_gender": ("성별", "Gender"),
    "form_male": ("남자", "Male"),
    "form_female": ("여자", "Female"),
    "form_birth_date": ("생년월일", "Date of Birth"),
    "form_solar": ("양력", "Gregorian"),
    "form_birth_time": ("출생 시각", "Time of Birth"),
    "form_time_note": ("24시간제, 한국 표준시", "24-hour format, Korea Standard Time"),
    "form_unknown_hour": (
        "출생 시간을 모릅니다 (시주 제외 분석)",
        "I don't know my birth hour (3-pillar analysis)",
    ),
    "cta_main": ("내 사주 보기", "Read My Saju"),
    "cta_sub": (
        "사기둥 · 십신 · 십이운성 · 오행 분석",
        "Four Pillars · Ten Gods · Twelve Stages · Five Elements",
    ),
    "form_note": (
        "입력값은 서버에 저장되지 않으며, 분석 결과 페이지에서만 사용됩니다.",
        "Your input is never stored on the server; it is used only to compute the result page.",
    ),

    # ── 특징 섹션 ──
    "feature_title": ("왜 이 사주가 정확한가", "Why this reading is accurate"),
    "feature_1_title": ("천문 알고리즘 기반 24절기", "24 solar terms via astronomy"),
    "feature_1_body": (
        "Meeus 천문공식으로 매년 입춘·경칩·청명 등 24절기 시점을 분 단위로 계산합니다. 연주·월주 경계 오차가 없습니다.",
        "Solar-term timings (Ipchun, Gyeongchip, etc.) are computed via Meeus astronomical formulas to the minute. The year and month pillar boundaries are exact.",
    ),
    "feature_2_title": ("야자시 / 조자시 보정", "Late-Zi hour correction"),
    "feature_2_body": (
        "23시 이후 출생의 일주 변경 규칙을 정확히 반영합니다. 한국 표준시(KST) 기준으로 시주를 산출합니다.",
        "The day-pillar shift rule for births after 23:00 (Ya-Ja-Si) is correctly applied. The hour pillar uses KST.",
    ),
    "feature_3_title": ("일주 중심 통변 해석", "Day-pillar-centered interpretation"),
    "feature_3_body": (
        "고전 명리학의 일간 중심 십신 분석과 12운성·지장간 본기 로직을 적용해 단순 띠 풀이가 아닌 사주 본연의 해석을 제공합니다.",
        "Classical Myeongri readings centered on the day stem, with Ten Gods, Twelve Life Stages, and primary hidden stems — not the shallow zodiac-only reading.",
    ),

    # ── 정보 카드 ──
    "info_title": ("사주, 무엇을 보는가", "What does Saju reveal?"),
    "info_pillars_title": ("사기둥(四柱)", "The Four Pillars"),
    "info_pillars_body": (
        "연주·월주·일주·시주 네 기둥으로 구성된 사주의 기본 골격입니다. 각 기둥은 천간 1자와 지지 1자, 총 8글자의 명식(命式)을 이룹니다.",
        "Four pillars — Year, Month, Day, Hour — each made of one Heavenly Stem and one Earthly Branch, forming the 8-character chart of your life.",
    ),
    "info_tengods_title": ("십신(十神)", "Ten Gods"),
    "info_tengods_body": (
        "나(일간)를 기준으로 한 사회적 관계의 별. 비견·겁재·식신·상관·편재·정재·편관·정관·편인·정인이 자아·재물·명예·인덕 같은 삶의 영역을 보여줍니다.",
        "Ten relational archetypes centered on your day stem — the lenses for self, wealth, status, recognition, and learning in your life.",
    ),
    "info_stages_title": ("십이운성(十二運星)", "Twelve Life Stages"),
    "info_stages_body": (
        "일간의 에너지가 어느 단계인지 — 장생부터 절·태·양까지 — 12단계 생애 흐름으로 표현합니다. 사주의 강약과 시기적 운세 분석의 핵심입니다.",
        "Twelve stages from Birth to Tomb that show the strength and life-rhythm of your day stem — the spine of timing analysis.",
    ),
    "info_elements_title": ("오행(五行)", "Five Elements"),
    "info_elements_body": (
        "목·화·토·금·수 다섯 기운의 균형으로 성격과 건강·진로 적성을 분석합니다. 어떤 오행이 강하고 약한지가 인생의 키워드를 결정합니다.",
        "Balance of Wood, Fire, Earth, Metal, Water — the elemental signature that shapes personality, vitality, and career.",
    ),

    # ── 결과 페이지 ──
    "result_birth_label": ("님의 사주명식", "'s Saju Chart"),
    "day_master_label": ("일간(나)", "Day Master (Self)"),
    "myeongsik_title": ("명식(命式) — 사기둥", "The Myeongsik — Four Pillars"),
    "myeongsik_sub": (
        "하늘과 땅의 글자가 짝을 이루어 당신의 인생 청사진을 그립니다.",
        "Stems above and Branches below pair to draw the blueprint of your life.",
    ),
    "pillar_hour": ("시주(時)", "Hour Pillar"),
    "pillar_day": ("일주(日) · 나", "Day Pillar · Self"),
    "pillar_month": ("월주(月)", "Month Pillar"),
    "pillar_year": ("연주(年)", "Year Pillar"),
    "pillar_unknown_hour": ("시간 미상", "Hour unknown"),
    "hidden_stems_label": ("지장간", "Hidden Stems"),
    "tengod_table_stem": ("천간 십신", "Stem Ten Gods"),
    "tengod_table_branch": ("지지 십신", "Branch Ten Gods"),
    "me_label": ("나(일간)", "Self (Day Stem)"),
    "elements_section_title": ("오행 균형", "Five Element Balance"),
    "elements_section_sub": (
        "사주에 등장하는 천간·지지의 오행 분포입니다. 가장 강한 기운과 약한 기운이 인생의 키워드를 만듭니다.",
        "Distribution of the five elements across your stems and branches. The strongest and weakest forces shape your life themes.",
    ),
    "elem_count_unit": ("자", " char"),
    "strongest_label": ("가장 강한 기운", "Strongest force"),
    "weakest_label": ("가장 약한 기운", "Weakest force"),
    "tengod_section_title": ("십신(十神) 분포", "Ten Gods Distribution"),
    "tengod_section_sub": (
        "일간을 중심으로 다른 일곱 글자가 각각 어떤 사회적 별이 되는가를 봅니다.",
        "How each of the other seven characters maps to a relational star centered on your day stem.",
    ),
    "daewoon_title": ("대운(大運) — 10년 단위 인생 흐름", "Daewoon — Decadal Life Flow"),
    "daewoon_sub": (
        "출생 시점 절기에서 산출한 대운 시작 나이와 향후 100년의 큰 흐름입니다.",
        "Your decadal flow over the next century, starting from the age computed from the nearest solar term to birth.",
    ),
    "daewoon_age_unit": ("세~", " yrs+"),
    "share_title": ("결과 공유하기", "Share Your Result"),
    "share_kakao": ("카카오톡으로 공유", "Share via KakaoTalk"),
    "share_twitter": ("X(트위터) 공유", "Share on X"),
    "share_facebook": ("페이스북 공유", "Share on Facebook"),
    "share_copylink": ("링크 복사", "Copy Link"),
    "share_copied": ("링크 복사됨 ✓", "Link copied ✓"),
    "deeper_title": ("사주 일주 더 깊이 보기", "Explore Your Day Pillar Deeper"),
    "btn_pillar_detail": ("일주 자세히", "Day Pillar Detail"),
    "btn_compatibility": ("사주 궁합 보기", "Saju Compatibility"),
    "btn_today_fortune": ("오늘의 운세", "Today's Fortune"),
    "btn_other_saju": ("다른 사주 보기", "Another Reading"),
    "disclaimer_title": ("면책 안내", "Disclaimer"),
    "disclaimer_body": (
        "본 풀이는 사주명리학 고전 이론에 기반한 자기이해 도구이며, 의료·법률·재정적 의사결정의 근거가 될 수 없습니다. 인생의 모든 선택과 책임은 본인에게 있습니다.",
        "This reading is a tool for self-understanding rooted in classical East Asian philosophy. It is not a substitute for medical, legal, or financial advice. All life choices remain your own.",
    ),
    "ad_label": ("광고", "Sponsored"),

    # ── Footer ──
    "footer_section_learn": ("학습 가이드", "Learn"),
    "footer_section_info": ("안내", "About"),
    "footer_link_about": ("서비스 소개", "About this service"),
    "footer_link_privacy": ("개인정보 처리방침", "Privacy Policy"),
    "footer_link_terms": ("이용약관 및 면책", "Terms & Disclaimer"),
    "footer_copyright": (
        "사주명리는 문화·심리·통계적 자기이해 도구로 제공됩니다.",
        "Saju is offered as a cultural, psychological, and statistical tool for self-understanding.",
    ),

    # ── 페이지 제목들 ──
    "page_today_h1": ("오늘의 운세", "Today's Fortune"),
    "page_zodiac_h1": ("12지 띠별 운세", "Zodiac Fortune"),
    "page_compat_h1": ("사주 궁합 보기", "Saju Compatibility"),
    "page_glossary_h1": ("사주 용어 사전", "Saju Glossary"),
    "page_pillars_h1": ("60갑자 일주별 풀이", "Sixty Pillars — Day-Pillar Readings"),
    "page_basics_h1": ("사주 기초 — 사주명리학 입문", "Saju Basics — Introduction"),
    "page_tengods_h1": ("십신(十神) — 일간 중심의 열 가지 별", "Ten Gods — Ten Relational Stars"),
    "page_stages_h1": ("십이운성(十二運星)", "Twelve Life Stages"),
    "page_elements_h1": ("오행(五行) — 우주를 움직이는 다섯 기운", "Five Elements — The Five Cosmic Forces"),

    # ── 공통 ──
    "free": ("무료", "Free"),
    "back_home": ("처음으로 돌아가기", "Back to Home"),
    "english": ("English", "English"),
    "korean": ("한국어", "한국어"),
    "lang_switch": ("English version", "한국어로 보기"),

    # ── 오늘의 운세 ──
    "today_keyword": ("오늘의 키워드", "Today's Keyword"),
    "lucky_color": ("행운의 색", "Lucky Color"),
    "lucky_direction": ("행운의 방위", "Lucky Direction"),
    "lucky_number": ("행운의 숫자", "Lucky Number"),
    "yesterday": ("← 어제", "← Yesterday"),
    "today": ("오늘로", "Today"),
    "tomorrow": ("내일 →", "Tomorrow →"),

    # ── 궁합 ──
    "compat_score_advice_label": ("궁합 종합 평가", "Overall Reading"),
    "person_1": ("첫 번째 사람", "First Person"),
    "person_2": ("두 번째 사람", "Second Person"),
    "compat_cta": ("궁합 분석하기", "Analyze Compatibility"),
    "compat_cta_sub": (
        "천간합 · 지지합 · 충 점수 분석",
        "Stem unions, branch unions/clashes — scored analysis",
    ),
    "compat_relations_title": ("관계 포인트 분석", "Relationship Highlights"),
    "compat_neutral": (
        "특별히 강한 합·충 관계는 발견되지 않습니다. 평이한 흐름의 인연입니다.",
        "No particularly strong unions or clashes were found — a steady, average connection.",
    ),

    # ── 띠 ──
    "zodiac_rat": ("쥐", "Rat"),
    "zodiac_ox": ("소", "Ox"),
    "zodiac_tiger": ("호랑이", "Tiger"),
    "zodiac_rabbit": ("토끼", "Rabbit"),
    "zodiac_dragon": ("용", "Dragon"),
    "zodiac_snake": ("뱀", "Snake"),
    "zodiac_horse": ("말", "Horse"),
    "zodiac_goat": ("양", "Goat"),
    "zodiac_monkey": ("원숭이", "Monkey"),
    "zodiac_rooster": ("닭", "Rooster"),
    "zodiac_dog": ("개", "Dog"),
    "zodiac_pig": ("돼지", "Pig"),

    # ── 오행 (영어 별칭) ──
    "elem_wood": ("목", "Wood"),
    "elem_fire": ("화", "Fire"),
    "elem_earth": ("토", "Earth"),
    "elem_metal": ("금", "Metal"),
    "elem_water": ("수", "Water"),

    # ── 천간 영문 음역 ──
    "stem_jia": ("갑", "Jia"),
    "stem_yi": ("을", "Yi"),
    "stem_bing": ("병", "Bing"),
    "stem_ding": ("정", "Ding"),
    "stem_wu": ("무", "Wu"),
    "stem_ji": ("기", "Ji"),
    "stem_geng": ("경", "Geng"),
    "stem_xin": ("신", "Xin"),
    "stem_ren": ("임", "Ren"),
    "stem_gui": ("계", "Gui"),
}

# 영문 음역 — 천간/지지
STEM_EN = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
BRANCH_EN = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
ELEMENT_EN = ["Wood", "Fire", "Earth", "Metal", "Water"]
ZODIAC_EN = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
             "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]


def t(key: str, lang: str = None) -> str:
    """현재 언어에서 key의 번역 반환. 키 없으면 key 자체."""
    if lang is None:
        try:
            lang = g.lang
        except Exception:
            lang = DEFAULT_LANG
    pair = UI.get(key)
    if not pair:
        return key
    return pair[1] if lang == "en" else pair[0]


def detect_lang_from_request() -> str:
    """URL prefix 우선, 그 다음 Accept-Language."""
    if request.path.startswith("/en/") or request.path == "/en":
        return "en"
    if request.path.startswith("/ko/") or request.path == "/ko":
        return "ko"
    # 그 외 = ko (한국어 기본 + Accept-Language로 영어 추정 시 리디렉트는 라우트 측에서)
    return DEFAULT_LANG


def accept_prefers_english() -> bool:
    al = request.headers.get("Accept-Language", "").lower()
    # 첫 언어가 영어인지
    if not al:
        return False
    first = al.split(",")[0].strip()
    return first.startswith("en")
