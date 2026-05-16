"""오늘의 운세 / 띠별 운세 / 궁합 분석 로직."""
from __future__ import annotations
from datetime import date, datetime, timedelta
from functools import lru_cache

from .calculator import (
    compute_saju, gregorian_to_jd, solar_term_jd,
    MONTH_BUILDING_TERMS, MONTH_TERM_TO_BRANCH
)
from . import data as D


@lru_cache(maxsize=400)
def get_day_pillar(year: int, month: int, day: int) -> tuple:
    """양력 날짜의 일주(stem, branch) 반환."""
    import math
    jd = gregorian_to_jd(year, month, day)
    idx = (int(math.floor(jd)) + 50) % 60
    return idx % 10, idx % 12, idx


@lru_cache(maxsize=200)
def get_today_year_pillar(year: int, month: int, day: int) -> tuple:
    """입춘 보정 후 연주 산출."""
    birth_jd = gregorian_to_jd(year, month, day, 12, 0)
    ipchun_jd = solar_term_jd(year, 0) + 9 / 24
    saju_year = year - 1 if birth_jd < ipchun_jd else year
    return (saju_year - 4) % 10, (saju_year - 4) % 12, saju_year


@lru_cache(maxsize=200)
def get_today_month_pillar(year: int, month: int, day: int, year_stem: int) -> tuple:
    """절기 기준 월주."""
    birth_jd = gregorian_to_jd(year, month, day, 12, 0)
    candidates = []
    for y_off in (-1, 0, 1):
        for t_idx, branch in zip(MONTH_BUILDING_TERMS, MONTH_TERM_TO_BRANCH):
            jd = solar_term_jd(year + y_off, t_idx) + 9 / 24
            if jd <= birth_jd:
                candidates.append((jd, branch))
    candidates.sort(key=lambda x: x[0], reverse=True)
    mb = candidates[0][1]
    ms = ((year_stem % 5) * 2 + mb) % 10
    return ms, mb


def daily_fortune(target_date: date) -> dict:
    """해당 날짜의 일주/오행 키워드 풀이."""
    y, m, d = target_date.year, target_date.month, target_date.day
    d_stem, d_branch, d_idx = get_day_pillar(y, m, d)
    y_stem, y_branch, _ = get_today_year_pillar(y, m, d)
    m_stem, m_branch = get_today_month_pillar(y, m, d, y_stem)

    day_pillar_name = D.HEAVENLY_STEMS_KR[d_stem] + D.EARTHLY_BRANCHES_KR[d_branch]
    day_element = D.ELEMENTS_KR[D.STEM_ELEMENT[d_stem]]
    month_element = D.ELEMENTS_KR[D.STEM_ELEMENT[m_stem]]

    # 일진 기반 키워드 (간략)
    keywords_by_element = {
        "목": ("성장·시작", "새로 시작하기 좋은 날입니다. 계획을 펼치고 가지를 뻗는 활동에 어울립니다."),
        "화": ("표현·확장", "사람을 만나고 자기 생각을 펼치기 좋은 날입니다. 활동량을 늘려보세요."),
        "토": ("안정·중재", "신뢰를 쌓고 관계를 다지기 좋은 날입니다. 무리한 변동보다 안정을 택하세요."),
        "금": ("결단·정리", "결정과 마무리에 적합한 날입니다. 흐트러진 것들을 정돈하세요."),
        "수": ("지혜·휴식", "사색과 학습, 충전에 좋은 날입니다. 결정은 한 박자 늦추는 것이 유리합니다."),
    }
    kw_title, kw_body = keywords_by_element[day_element]

    return {
        "date": target_date,
        "day_pillar_index": d_idx,
        "day_pillar_name": day_pillar_name,
        "day_pillar_hanja": D.HEAVENLY_STEMS[d_stem] + D.EARTHLY_BRANCHES[d_branch],
        "day_element": day_element,
        "month_pillar_name": D.HEAVENLY_STEMS_KR[m_stem] + D.EARTHLY_BRANCHES_KR[m_branch],
        "month_element": month_element,
        "year_pillar_name": D.HEAVENLY_STEMS_KR[y_stem] + D.EARTHLY_BRANCHES_KR[y_branch],
        "keyword_title": kw_title,
        "keyword_body": kw_body,
        "lucky_color": _lucky_color(day_element),
        "lucky_direction": _lucky_direction(day_element),
        "lucky_number": _lucky_number(d_idx),
    }


def _lucky_color(element):
    return {"목": "녹색·청색", "화": "붉은색·자주색", "토": "황색·갈색",
            "금": "흰색·은색", "수": "검정·남색"}[element]


def _lucky_direction(element):
    return {"목": "동쪽", "화": "남쪽", "토": "중앙", "금": "서쪽", "수": "북쪽"}[element]


def _lucky_number(pillar_idx):
    base = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    return base[pillar_idx % 10]


# ───────────── 띠별 운세 ─────────────

ZODIAC_TRAITS = {
    "쥐":   ("子", "민첩·총명·재물운", "기지가 뛰어나고 재물 감각이 발달한 성향. 발 빠른 정보 활용이 무기입니다."),
    "소":   ("丑", "성실·인내·신뢰", "묵묵히 일하고 책임감이 강한 성향. 한 분야에서 오래 빛납니다."),
    "호랑이": ("寅", "용기·추진력·리더십", "도전과 모험을 즐기는 카리스마. 무리 앞에 서는 자리에 어울립니다."),
    "토끼": ("卯", "온화·미적감각·인복", "부드러운 매력으로 사람을 끄는 성향. 예술·문화·서비스에 강점."),
    "용":   ("辰", "야망·이상·창조성", "큰 그림을 그리는 비전형. 시작과 변화의 흐름에서 빛납니다."),
    "뱀":   ("巳", "직관·통찰·신중함", "예리한 분석력과 깊은 사고력. 전문성을 살리는 분야에 적합."),
    "말":   ("午", "활동·표현·자유", "활달하고 사교적이며 표현력이 풍부한 성향. 무대 위 인생."),
    "양":   ("未", "포용·예술·정서", "따뜻하고 감성이 풍부한 성향. 예술과 돌봄의 영역에서 빛납니다."),
    "원숭이": ("申", "재치·적응력·기술", "임기응변이 빠르고 다재다능. 변화 많은 환경에서 유리."),
    "닭":   ("酉", "정교함·자존심·미감", "꼼꼼하고 깔끔하며 미적 감각이 뛰어남. 디테일이 자산입니다."),
    "개":   ("戌", "의리·정직·책임감", "신뢰가 두텁고 정의로운 성향. 보호자·중재자 역할에 잘 맞습니다."),
    "돼지": ("亥", "낙천·풍요·인덕", "복록이 따르는 성향. 사람들이 모이고 정이 많습니다."),
}

ZODIAC_BRANCH_INDEX = {
    "쥐": 0, "소": 1, "호랑이": 2, "토끼": 3, "용": 4, "뱀": 5,
    "말": 6, "양": 7, "원숭이": 8, "닭": 9, "개": 10, "돼지": 11,
}


def zodiac_for_year(year: int) -> str:
    """입춘 보정 없이 단순 연도 기준 띠 (개략)."""
    return list(ZODIAC_TRAITS.keys())[(year - 4) % 12]


def zodiac_yearly_fortune(zodiac_name: str, today: date | None = None) -> dict:
    """띠와 해당 연도의 흐름 분석."""
    today = today or date.today()
    branch_idx = ZODIAC_BRANCH_INDEX[zodiac_name]
    yr_stem, yr_branch, _ = get_today_year_pillar(today.year, today.month, today.day)
    year_name = D.HEAVENLY_STEMS_KR[yr_stem] + D.EARTHLY_BRANCHES_KR[yr_branch]

    # 띠 vs 올해 연지 관계
    relations = []
    if yr_branch == branch_idx:
        relations.append(("본명년(本命年)", "자기 띠 해. 변동·전환의 흐름이 강합니다. 큰 결단보다는 내실에 집중하세요."))
    elif (branch_idx, yr_branch) in D.BRANCH_CHONG or (yr_branch, branch_idx) in D.BRANCH_CHONG:
        relations.append(("충(沖)", "올해 띠와 충돌하는 흐름. 변화와 이동이 잦으니 신중한 결정이 필요합니다."))
    else:
        # 삼합 체크
        for combo, elem, name in D.BRANCH_SAN_HE:
            if branch_idx in combo and yr_branch in combo:
                relations.append((f"삼합({name})", f"올해와 {elem} 기운으로 합을 이루는 좋은 흐름입니다."))
                break
        if not relations:
            relations.append(("평운", "안정된 흐름. 차분하게 계획을 이어가시면 결실이 옵니다."))

    return {
        "name": zodiac_name,
        "trait": ZODIAC_TRAITS[zodiac_name],
        "this_year": year_name,
        "this_year_number": today.year,
        "relations": relations,
        "today": daily_fortune(today),
    }


# ───────────── 궁합 ─────────────

def compatibility(p1: dict, p2: dict) -> dict:
    """두 사람의 사주 일간/일지/연지/월지 비교로 궁합 산출.

    p1, p2: dict with year, month, day, hour, minute, gender, name
    """
    s1 = compute_saju(p1["year"], p1["month"], p1["day"],
                      p1.get("hour", 12), p1.get("minute", 0),
                      gender=p1.get("gender", "남"), name=p1.get("name", ""))
    s2 = compute_saju(p2["year"], p2["month"], p2["day"],
                      p2.get("hour", 12), p2.get("minute", 0),
                      gender=p2.get("gender", "여"), name=p2.get("name", ""))

    score = 50  # 기본
    notes = []

    # 1) 일간 합 — 천간합 5조
    s1_stem = s1.day_pillar.stem
    s2_stem = s2.day_pillar.stem
    pair = tuple(sorted([s1_stem, s2_stem]))
    if pair in D.STEM_COMBINATIONS:
        info = D.STEM_COMBINATIONS[pair]
        score += 20
        notes.append(("일간 천간합", f"{info[1]} — 마음이 자연스럽게 끌리는 인연입니다.", "+20"))

    # 2) 일간 상생/상극
    s1_el = s1.day_pillar.stem_element
    s2_el = s2.day_pillar.stem_element
    if D.ELEMENT_GENERATES.get(s1_el) == s2_el or D.ELEMENT_GENERATES.get(s2_el) == s1_el:
        score += 15
        notes.append(("일간 상생", "한쪽이 다른 쪽을 살리는 상생 관계 — 서로의 부족함을 보완해 줍니다.", "+15"))
    elif D.ELEMENT_CONTROLS.get(s1_el) == s2_el or D.ELEMENT_CONTROLS.get(s2_el) == s1_el:
        score -= 10
        notes.append(("일간 상극", "긴장과 갈등의 흐름. 서로 다른 관점을 어떻게 다루느냐가 관건입니다.", "-10"))
    elif s1_el == s2_el:
        score += 5
        notes.append(("같은 오행", "비슷한 결의 사람들 — 편안하지만 자극이 적을 수 있습니다.", "+5"))

    # 3) 일지 합·충
    s1_b = s1.day_pillar.branch
    s2_b = s2.day_pillar.branch
    bp = tuple(sorted([s1_b, s2_b]))
    if bp in D.BRANCH_LIU_HE:
        score += 15
        info = D.BRANCH_LIU_HE[bp]
        notes.append(("일지 육합", f"{info[1]} — 함께 있을 때 안정감이 큽니다.", "+15"))
    if bp in D.BRANCH_CHONG or (bp[1], bp[0]) in D.BRANCH_CHONG:
        score -= 15
        notes.append(("일지 충", "서로 다른 생활 리듬과 가치관. 충돌이 잦을 수 있으니 거리 두기와 대화가 필요합니다.", "-15"))

    # 4) 연지 띠 관계
    yb1, yb2 = s1.year_pillar.branch, s2.year_pillar.branch
    if (yb1, yb2) in D.BRANCH_CHONG or (yb2, yb1) in D.BRANCH_CHONG:
        score -= 5
        notes.append(("띠 충", "사회·외부 관계에서 의견 차이가 자주 나타날 수 있습니다.", "-5"))
    elif (yb1, yb2) in D.BRANCH_LIU_HE or (yb2, yb1) in D.BRANCH_LIU_HE:
        score += 5
        notes.append(("띠 육합", "사회적으로 잘 어울리는 흐름입니다.", "+5"))

    score = max(20, min(95, score))

    grade = "최상" if score >= 85 else "상" if score >= 70 else "중상" if score >= 60 else "중" if score >= 45 else "주의"
    advice = {
        "최상": "운명적으로 잘 맞는 흐름입니다. 서로의 다름조차 매력으로 작용합니다.",
        "상":   "함께 있을 때 편안함과 안정이 큰 관계입니다. 작은 노력만으로도 오래 갑니다.",
        "중상": "기본 궁합은 좋습니다. 서로의 다른 점을 인정하고 보완하면 길게 갑니다.",
        "중":   "노력이 필요한 흐름. 대화와 거리 조절로 충분히 다듬어집니다.",
        "주의": "기질의 차이가 큽니다. 서로의 영역을 존중하는 것이 핵심입니다.",
    }[grade]

    return {
        "score": score,
        "grade": grade,
        "advice": advice,
        "notes": notes,
        "p1": s1,
        "p2": s2,
    }
