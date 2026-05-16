"""음력 → 양력 변환 — 1900~2049 한국 음력 데이터 기반.

LUNAR_INFO[year] 비트 인코딩 (HKO/KASI 표준):
- bits 0-3   : 윤달 위치 (0 = 윤달 없음, 1-12 = 그 달이 윤달)
- bits 4-15  : 12개 월(정월~12월)의 일수 (1=30일, 0=29일)
                bit 15 = 정월, bit 14 = 2월, ..., bit 4 = 12월
- bit  16    : 윤달이 있을 때 그 윤달의 일수 (1=30일, 0=29일)
"""
from datetime import date, timedelta

# 1900-01-31 = 음력 1900-01-01
BASE_DATE = date(1900, 1, 31)

LUNAR_INFO = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,  # 1900-1909
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
    0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,  # 1950-1959
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,  # 1990-1999
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
    0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,  # 2040-2049
]


def _leap_month(year_idx: int) -> int:
    """해당 연도의 윤달 위치 반환 (0 = 윤달 없음)."""
    return LUNAR_INFO[year_idx] & 0xF


def _month_days(year_idx: int, month: int) -> int:
    """해당 연도의 normal month(1~12)의 일수."""
    info = LUNAR_INFO[year_idx]
    return 30 if (info >> (16 - month)) & 1 else 29


def _leap_days(year_idx: int) -> int:
    """해당 연도 윤달의 일수 (윤달 없으면 0)."""
    if not _leap_month(year_idx):
        return 0
    return 30 if (LUNAR_INFO[year_idx] >> 16) & 1 else 29


def _year_days(year_idx: int) -> int:
    """해당 음력년 총 일수."""
    total = sum(_month_days(year_idx, m) for m in range(1, 13))
    total += _leap_days(year_idx)
    return total


def lunar_to_solar(ly: int, lm: int, ld: int, is_leap: bool = False) -> date:
    """음력(년, 월, 일, 윤달 여부) → 양력 date."""
    if ly < 1900 or ly > 2049:
        raise ValueError("Lunar year out of supported range (1900-2049)")
    if not (1 <= lm <= 12):
        raise ValueError("Lunar month must be 1-12")
    if not (1 <= ld <= 30):
        raise ValueError("Lunar day must be 1-30")

    year_idx = ly - 1900

    # 이전 연도들의 총 일수
    offset = 0
    for y in range(year_idx):
        offset += _year_days(y)

    leap_m = _leap_month(year_idx)

    if is_leap:
        if lm != leap_m:
            raise ValueError(f"{ly}년에는 윤{lm}월이 없습니다 (윤달은 {leap_m or '없음'}월)")
        # 정월 ~ lm월 (normal) 전부 + 윤달 내 ld일
        for m in range(1, lm + 1):
            offset += _month_days(year_idx, m)
        offset += ld - 1
    else:
        # 정월 ~ (lm-1)월 normal
        for m in range(1, lm):
            offset += _month_days(year_idx, m)
        # 윤달을 이미 지난 경우 윤달 일수 추가
        if leap_m and lm > leap_m:
            offset += _leap_days(year_idx)
        offset += ld - 1

    # 일수 검증
    target_day_count = _month_days(year_idx, lm)
    if is_leap:
        target_day_count = _leap_days(year_idx)
    if ld > target_day_count:
        raise ValueError(
            f"{ly}년 {'윤' if is_leap else ''}{lm}월은 {target_day_count}일까지만 있습니다"
        )

    return BASE_DATE + timedelta(days=offset)


if __name__ == "__main__":
    # 검증: 알려진 한국 음력 ↔ 양력 매칭
    cases = [
        (1990, 1, 1, False, date(1990, 1, 27)),   # 1990 음력 정월 1일 = 양력 1990-01-27
        (2024, 1, 1, False, date(2024, 2, 10)),   # 2024 음력 정월 1일 = 양력 2024-02-10
        (1900, 1, 1, False, date(1900, 1, 31)),   # base
        (2000, 5, 5, False, date(2000, 6, 6)),    # 단오
    ]
    for ly, lm, ld, leap, expected in cases:
        got = lunar_to_solar(ly, lm, ld, leap)
        ok = "OK" if got == expected else "FAIL"
        print(f"{ok} 음력 {ly}-{lm:02d}-{ld:02d}{'(윤)' if leap else ''} → got {got}, expected {expected}")
