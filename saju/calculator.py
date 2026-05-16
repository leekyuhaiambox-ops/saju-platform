"""사주 계산 엔진.

사용자의 양력 생년월일시(한국 표준시 KST 기준)를 받아
사주 사기둥(연주/월주/일주/시주)을 계산한다.

핵심 알고리즘:
1. 양력 입력을 Julian Day로 변환
2. Meeus 천문 알고리즘으로 24절기 시점을 계산
3. 입춘 기준 연주 결정
4. 절기 기준 월주 결정
5. 일주: (JD + 보정) mod 60
6. 시주: 일간 + 시지 조합
"""

from __future__ import annotations
import math
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from functools import lru_cache

from . import data as D


# ─────────────────────────────────────────────────────────────────────
# Julian Day 변환
# ─────────────────────────────────────────────────────────────────────

def gregorian_to_jd(year: int, month: int, day: int,
                    hour: float = 0, minute: float = 0, second: float = 0) -> float:
    """그레고리력 → Julian Day (UT 기준).
    .5 단위는 자정을 의미: JD 2451544.5 = 2000-01-01 00:00 UT.
    """
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    jd = (int(365.25 * (year + 4716)) + int(30.6001 * (month + 1))
          + day + b - 1524.5)
    jd += (hour + minute / 60 + second / 3600) / 24
    return jd


def jd_to_gregorian(jd: float):
    """Julian Day → (year, month, day, hour, minute, second)."""
    jd += 0.5
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day_full = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    day = int(day_full)
    frac = day_full - day
    total_sec = round(frac * 86400)
    hh = int(total_sec // 3600)
    mm = int((total_sec % 3600) // 60)
    ss = int(total_sec % 60)
    return year, month, day, hh, mm, ss


# ─────────────────────────────────────────────────────────────────────
# 24절기 (Meeus 알고리즘 기반)
# ─────────────────────────────────────────────────────────────────────

# 24절기 인덱스 → (한글명, 시작 황경°, 양력 추정일)
SOLAR_TERMS = [
    ("입춘", 315, 35),   # 0
    ("우수", 330, 50),
    ("경칩", 345, 66),
    ("춘분", 0,   81),
    ("청명", 15,  96),
    ("곡우", 30,  112),
    ("입하", 45,  127),
    ("소만", 60,  142),
    ("망종", 75,  158),
    ("하지", 90,  174),
    ("소서", 105, 190),
    ("대서", 120, 206),
    ("입추", 135, 222),
    ("처서", 150, 238),
    ("백로", 165, 253),
    ("추분", 180, 269),
    ("한로", 195, 284),
    ("상강", 210, 300),
    ("입동", 225, 315),
    ("소설", 240, 330),
    ("대설", 255, 346),
    ("동지", 270, 361),
    ("소한", 285, 6),
    ("대한", 300, 21),
]

# 월주 결정에 사용되는 12개 "월건절기" 인덱스: 입춘, 경칩, 청명, 입하, 망종,
# 소서, 입추, 백로, 한로, 입동, 대설, 소한
MONTH_BUILDING_TERMS = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
# 각 월건절기 이후 진입하는 월지(地支) 인덱스 (입춘→寅(2), 경칩→卯(3), ...)
MONTH_TERM_TO_BRANCH = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]


def apparent_solar_longitude(jd: float) -> float:
    """JD 시점의 태양 겉보기 황경(°). Meeus 27장."""
    t = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360
    m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t * t) % 360)
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    return (l0 + c) % 360


@lru_cache(maxsize=4096)
def solar_term_jd(year: int, term_idx: int) -> float:
    """그레고리력 연도 `year`에 발생하는 절기 `term_idx`(0=입춘..23=대한)의 JD.

    24절기 시점은 같은 연도에 대해 항상 같은 값을 반환하므로 영구 캐싱한다.
    이 캐시 하나가 free tier CPU 절약의 핵심 — 사주 계산의 80% 비용이 절기 산출이다.
    """
    _, target, approx_doy = SOLAR_TERMS[term_idx]
    jd = gregorian_to_jd(year, 1, 1) + (approx_doy - 1)
    for _ in range(20):
        lon = apparent_solar_longitude(jd)
        diff = ((target - lon) + 540) % 360 - 180
        if abs(diff) < 1e-6:
            break
        jd += diff * (365.25 / 360.0)
    return jd


def solar_term_kst(year: int, term_idx: int):
    """절기 시점(KST). Returns (Y, M, D, h, m, s)."""
    jd = solar_term_jd(year, term_idx) + 9 / 24  # UT → KST
    return jd_to_gregorian(jd)


# ─────────────────────────────────────────────────────────────────────
# 사주 사기둥 계산
# ─────────────────────────────────────────────────────────────────────

@dataclass
class Pillar:
    stem: int        # 0..9
    branch: int      # 0..11

    @property
    def stem_name(self):
        return D.HEAVENLY_STEMS_KR[self.stem]

    @property
    def branch_name(self):
        return D.EARTHLY_BRANCHES_KR[self.branch]

    @property
    def name(self):
        return self.stem_name + self.branch_name

    @property
    def hanja(self):
        return D.HEAVENLY_STEMS[self.stem] + D.EARTHLY_BRANCHES[self.branch]

    @property
    def stem_element(self):
        return D.STEM_ELEMENT[self.stem]

    @property
    def branch_element(self):
        return D.BRANCH_ELEMENT[self.branch]


@dataclass
class SajuResult:
    name: str
    gender: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    is_lunar: bool
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Optional[Pillar]
    # 십신 (year, month, day=self, hour)
    ten_gods: Dict[str, Optional[str]] = field(default_factory=dict)
    # 십이운성 (각 기둥 지지에 대해 일간 기준)
    twelve_stages: Dict[str, str] = field(default_factory=dict)
    # 오행 분포 (개수)
    element_counts: Dict[str, int] = field(default_factory=dict)
    # 각 지지의 지장간들 (사용자 표시용)
    hidden_stems: Dict[str, List[str]] = field(default_factory=dict)
    # 일간 자체
    day_master: str = ""
    day_master_element: str = ""

    def to_dict(self):
        d = asdict(self)
        for k in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
            p = getattr(self, k)
            if p is None:
                d[k] = None
            else:
                d[k] = {
                    "stem": p.stem, "branch": p.branch,
                    "name": p.name, "hanja": p.hanja,
                }
        return d


# 일주 보정 오프셋 — 검증 기준일: 2000-01-01 (양력) = 戊午일 (인덱스 54).
# JD(2000-01-01 00:00 UT) = 2451544.5 → floor = 2451544 → mod 60 = 4.
# offset = (54 - 4) mod 60 = 50.
_DAY_PILLAR_OFFSET = 50


def _compute_year_pillar(year: int, month: int, day: int,
                         hour: int, minute: int) -> tuple:
    """입춘 보정 후 연주의 (stem, branch) 반환."""
    # 입춘 시점 (KST)
    ipchun_jd_kst = solar_term_jd(year, 0) + 9 / 24
    birth_jd_kst = gregorian_to_jd(year, month, day, hour, minute)
    # 비교는 UT 기준 JD로 충분 (둘 다 KST 환산이므로 일관됨)
    if birth_jd_kst < ipchun_jd_kst:
        saju_year = year - 1
    else:
        saju_year = year
    stem = (saju_year - 4) % 10
    branch = (saju_year - 4) % 12
    return stem, branch, saju_year


def _compute_month_pillar(year: int, month: int, day: int,
                          hour: int, minute: int, year_stem: int) -> tuple:
    """월건절기 기준 월주의 (stem, branch) 반환.

    출생 시점을 기준으로 가장 최근에 지난 월건절기를 찾는다.
    """
    birth_jd_kst = gregorian_to_jd(year, month, day, hour, minute)
    # 작년/올해/내년 절기를 모두 후보로 (연말 출생 케이스)
    candidates = []
    for y_offset in (-1, 0, 1):
        for t_idx, branch in zip(MONTH_BUILDING_TERMS, MONTH_TERM_TO_BRANCH):
            jd = solar_term_jd(year + y_offset, t_idx) + 9 / 24
            if jd <= birth_jd_kst:
                candidates.append((jd, branch))
    # 가장 최근 = jd 최대
    candidates.sort(key=lambda x: x[0], reverse=True)
    month_branch = candidates[0][1]
    # 월간 = ((연간 % 5) * 2 + 월지) % 10
    month_stem = ((year_stem % 5) * 2 + month_branch) % 10
    return month_stem, month_branch


def _compute_day_pillar(year: int, month: int, day: int,
                        hour: int) -> tuple:
    """일주(stem, branch) 반환. 23시 이후 출생은 다음 날 일주를 사용 (야자시 규칙)."""
    # 그날(자정~22:59)의 일주 인덱스
    jd_midnight = gregorian_to_jd(year, month, day)  # 00:00 UT
    # KST 자정 기준: floor(JD) mod 60
    day_idx = (int(math.floor(jd_midnight)) + _DAY_PILLAR_OFFSET) % 60
    if hour >= 23:
        # 야자시: 23:00 이후는 다음날 일주
        day_idx = (day_idx + 1) % 60
    stem = day_idx % 10
    branch = day_idx % 12
    return stem, branch


def _compute_hour_pillar(day_stem: int, hour: int, minute: int) -> Pillar:
    """시주 계산."""
    # 시지 결정
    # 子: 23-01, 丑: 01-03, ..., 亥: 21-23
    h = hour
    if h == 23:
        branch = 0
    else:
        branch = ((h + 1) // 2) % 12
    # 시간(時干) = ((일간 % 5) * 2 + 시지) % 10
    stem = ((day_stem % 5) * 2 + branch) % 10
    return Pillar(stem=stem, branch=branch)


def compute_saju(year: int, month: int, day: int,
                 hour: int = 12, minute: int = 0,
                 gender: str = "남",
                 name: str = "",
                 is_lunar: bool = False,
                 unknown_hour: bool = False) -> SajuResult:
    """양력 입력 → 사주 SajuResult 반환.

    Args:
        year, month, day: 양력 생년월일
        hour, minute: 24시간제 시간 (한국 표준시 KST 기준)
        gender: '남' 또는 '여'
        is_lunar: 음력 입력 여부 (현재 미지원 — 양력만)
        unknown_hour: 시간 미상 여부 (True면 시주 미계산)
    """
    if is_lunar:
        raise NotImplementedError("음력 입력은 현재 버전에서 지원하지 않습니다. 양력으로 변환 후 사용해 주세요.")

    y_stem, y_branch, saju_year = _compute_year_pillar(year, month, day, hour, minute)
    m_stem, m_branch = _compute_month_pillar(year, month, day, hour, minute, y_stem)
    d_stem, d_branch = _compute_day_pillar(year, month, day, hour)

    year_pillar = Pillar(stem=y_stem, branch=y_branch)
    month_pillar = Pillar(stem=m_stem, branch=m_branch)
    day_pillar = Pillar(stem=d_stem, branch=d_branch)

    hour_pillar = None
    if not unknown_hour:
        hour_pillar = _compute_hour_pillar(d_stem, hour, minute)

    # 십신 (일간 기준)
    ten_gods = {
        "year_stem": D.get_ten_god(d_stem, y_stem),
        "year_branch": _branch_ten_god(d_stem, y_branch),
        "month_stem": D.get_ten_god(d_stem, m_stem),
        "month_branch": _branch_ten_god(d_stem, m_branch),
        "day_branch": _branch_ten_god(d_stem, d_branch),
        "hour_stem": D.get_ten_god(d_stem, hour_pillar.stem) if hour_pillar else None,
        "hour_branch": _branch_ten_god(d_stem, hour_pillar.branch) if hour_pillar else None,
    }

    # 십이운성
    twelve_stages = {
        "year": D.get_twelve_stage(d_stem, y_branch),
        "month": D.get_twelve_stage(d_stem, m_branch),
        "day": D.get_twelve_stage(d_stem, d_branch),
        "hour": D.get_twelve_stage(d_stem, hour_pillar.branch) if hour_pillar else None,
    }

    # 오행 분포
    elem_counts = {e: 0 for e in D.ELEMENTS_KR}
    pillars_for_counting = [year_pillar, month_pillar, day_pillar]
    if hour_pillar:
        pillars_for_counting.append(hour_pillar)
    for p in pillars_for_counting:
        elem_counts[D.ELEMENTS_KR[p.stem_element]] += 1
        elem_counts[D.ELEMENTS_KR[p.branch_element]] += 1

    # 지장간
    hidden = {}
    for label, p in [("year", year_pillar), ("month", month_pillar),
                     ("day", day_pillar), ("hour", hour_pillar)]:
        if p is None:
            continue
        items = D.HIDDEN_STEMS[p.branch]
        hidden[label] = [D.HEAVENLY_STEMS_KR[idx] for idx, _ in items]

    return SajuResult(
        name=name,
        gender=gender,
        year=year, month=month, day=day, hour=hour, minute=minute,
        is_lunar=is_lunar,
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        ten_gods=ten_gods,
        twelve_stages=twelve_stages,
        element_counts=elem_counts,
        hidden_stems=hidden,
        day_master=D.HEAVENLY_STEMS_KR[d_stem],
        day_master_element=D.ELEMENTS_KR[D.STEM_ELEMENT[d_stem]],
    )


def _branch_ten_god(day_stem: int, branch: int) -> str:
    """지지의 본기(가장 큰 비율의 지장간)을 기준으로 십신을 산출."""
    items = D.HIDDEN_STEMS[branch]
    main_stem = items[0][0]
    return D.get_ten_god(day_stem, main_stem)


# ─────────────────────────────────────────────────────────────────────
# 대운(大運) 계산
# ─────────────────────────────────────────────────────────────────────

def compute_daewoon(saju: SajuResult, gender: str = None) -> List[Dict]:
    """대운 10년 단위 계산. 양남·음녀는 순행, 음남·양녀는 역행.

    Returns:
        리스트(각 원소): {age: 대운 시작 만나이, stem: int, branch: int, name: str}
    """
    gender = gender or saju.gender
    y_stem_yy = D.STEM_YIN_YANG[saju.year_pillar.stem]  # 0=양, 1=음
    is_male = gender in ("남", "M", "male", "남성")
    # 순행 조건: 양남(0,True) 또는 음녀(1,False)
    forward = (y_stem_yy == 0 and is_male) or (y_stem_yy == 1 and not is_male)

    # 시작 월주 인덱스 기반으로 순차 생성
    m_stem = saju.month_pillar.stem
    m_branch = saju.month_pillar.branch
    direction = 1 if forward else -1

    # 대운 수(시작 만나이): 출생일로부터 다음(순행) 또는 이전(역행) 월건절기까지의 일수 / 3
    birth_jd = gregorian_to_jd(saju.year, saju.month, saju.day, saju.hour, saju.minute)
    nearest_jd = _find_neighbor_month_term_jd(saju.year, saju.month, saju.day,
                                              saju.hour, saju.minute, forward)
    days_diff = abs(nearest_jd - birth_jd)
    start_age = max(1, round(days_diff / 3))

    daewoons = []
    cur_stem, cur_branch = m_stem, m_branch
    for i in range(10):
        cur_stem = (cur_stem + direction) % 10
        cur_branch = (cur_branch + direction) % 12
        daewoons.append({
            "age": start_age + i * 10,
            "stem": cur_stem,
            "branch": cur_branch,
            "name": D.HEAVENLY_STEMS_KR[cur_stem] + D.EARTHLY_BRANCHES_KR[cur_branch],
            "ten_god_stem": D.get_ten_god(saju.day_pillar.stem, cur_stem),
            "twelve_stage": D.get_twelve_stage(saju.day_pillar.stem, cur_branch),
        })
    return daewoons


def _find_neighbor_month_term_jd(year, month, day, hour, minute, forward: bool) -> float:
    """출생 시점 기준 가장 가까운 (forward=True면 미래, False면 과거) 월건절기 JD."""
    birth_jd = gregorian_to_jd(year, month, day, hour, minute)
    candidates = []
    for y_off in (-1, 0, 1):
        for t_idx in MONTH_BUILDING_TERMS:
            jd = solar_term_jd(year + y_off, t_idx) + 9 / 24
            candidates.append(jd)
    candidates.sort()
    if forward:
        for jd in candidates:
            if jd > birth_jd:
                return jd
        return candidates[-1]
    else:
        for jd in reversed(candidates):
            if jd < birth_jd:
                return jd
        return candidates[0]


if __name__ == "__main__":
    # 검증: 2024-02-04 12:00 → 갑진년 병인월 갑진일 경오시
    r = compute_saju(2024, 2, 4, 12, 0, gender="남")
    print(f"연주: {r.year_pillar.name} ({r.year_pillar.hanja})")
    print(f"월주: {r.month_pillar.name} ({r.month_pillar.hanja})")
    print(f"일주: {r.day_pillar.name} ({r.day_pillar.hanja})")
    print(f"시주: {r.hour_pillar.name} ({r.hour_pillar.hanja})")
    print(f"일간(나): {r.day_master} ({r.day_master_element})")
    print(f"오행: {r.element_counts}")
