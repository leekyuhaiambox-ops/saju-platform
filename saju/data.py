"""사주 명리학 정적 데이터: 천간, 지지, 60갑자, 십신, 십이운성, 오행."""

# 천간(天干) 10개: 인덱스 0~9
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
HEAVENLY_STEMS_KR = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]

# 지지(地支) 12개: 인덱스 0~11
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
EARTHLY_BRANCHES_KR = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

# 천간 음양: 0=양, 1=음
STEM_YIN_YANG = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
BRANCH_YIN_YANG = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

# 오행 매핑 (0=목, 1=화, 2=토, 3=금, 4=수)
STEM_ELEMENT = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
BRANCH_ELEMENT = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]

ELEMENTS = ["木", "火", "土", "金", "水"]
ELEMENTS_KR = ["목", "화", "토", "금", "수"]
ELEMENTS_COLOR = ["#2E8B57", "#DC143C", "#DAA520", "#C0C0C0", "#1E3A8A"]

# 띠 (12지 동물)
ZODIAC_ANIMALS = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]

# 12지 시간대 (지지: 시작시, 끝시)
BRANCH_HOUR_RANGE = [
    (23, 1), (1, 3), (3, 5), (5, 7), (7, 9), (9, 11),
    (11, 13), (13, 15), (15, 17), (17, 19), (19, 21), (21, 23)
]

# 지장간 (지지 안에 숨은 천간들) — (천간 인덱스, 비율)
HIDDEN_STEMS = {
    0:  [(9, 1.0)],                              # 子: 癸
    1:  [(5, 0.6), (3, 0.2), (9, 0.2)],          # 丑: 己 丁 癸
    2:  [(0, 0.6), (2, 0.2), (4, 0.2)],          # 寅: 甲 丙 戊
    3:  [(1, 1.0)],                              # 卯: 乙
    4:  [(4, 0.6), (1, 0.2), (9, 0.2)],          # 辰: 戊 乙 癸
    5:  [(2, 0.6), (4, 0.2), (6, 0.2)],          # 巳: 丙 戊 庚
    6:  [(3, 0.7), (5, 0.3)],                    # 午: 丁 己
    7:  [(5, 0.6), (3, 0.2), (1, 0.2)],          # 未: 己 丁 乙
    8:  [(6, 0.6), (4, 0.2), (8, 0.2)],          # 申: 庚 戊 壬
    9:  [(7, 1.0)],                              # 酉: 辛
    10: [(4, 0.6), (7, 0.2), (3, 0.2)],          # 戌: 戊 辛 丁
    11: [(8, 0.7), (0, 0.3)],                    # 亥: 壬 甲
}

# 12지 띠/계절
BRANCH_SEASON = ["冬", "冬", "春", "春", "春", "夏", "夏", "夏", "秋", "秋", "秋", "冬"]

# 60갑자 이름 (한글)
def sixty_pillar_name(idx):
    """0..59 인덱스 → 한글 60갑자 이름. (예: 0 → '갑자')"""
    return HEAVENLY_STEMS_KR[idx % 10] + EARTHLY_BRANCHES_KR[idx % 12]

def sixty_pillar_hanja(idx):
    return HEAVENLY_STEMS[idx % 10] + EARTHLY_BRANCHES[idx % 12]

# 십신(十神) 이름
TEN_GODS = [
    "비견", "겁재",   # 0,1: 비화자 (양/음)
    "식신", "상관",   # 2,3: 아생자
    "편재", "정재",   # 4,5: 아극자
    "편관", "정관",   # 6,7: 극아자
    "편인", "정인",   # 8,9: 생아자
]

# 십이운성 이름
TWELVE_STAGES = [
    "장생", "목욕", "관대", "건록", "제왕", "쇠",
    "병", "사", "묘", "절", "태", "양"
]

# 천간별 십이운성 시작 지지 인덱스 (장생이 시작되는 지지)
# 甲: 亥(11), 乙: 午(6), 丙: 寅(2), 丁: 酉(9), 戊: 寅(2),
# 己: 酉(9), 庚: 巳(5), 辛: 子(0), 壬: 申(8), 癸: 卯(3)
STEM_LIFE_START_BRANCH = [11, 6, 2, 9, 2, 9, 5, 0, 8, 3]
# 음간은 역행, 양간은 순행
STEM_LIFE_DIRECTION = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1]

# 오행 상생: 목→화→토→금→수→목
ELEMENT_GENERATES = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
# 오행 상극: 목→토, 토→수, 수→화, 화→금, 금→목
ELEMENT_CONTROLS = {0: 2, 2: 4, 4: 1, 1: 3, 3: 0}

# 천간합
STEM_COMBINATIONS = {
    (0, 5): ("土", "갑기합토"),
    (1, 6): ("金", "을경합금"),
    (2, 7): ("水", "병신합수"),
    (3, 8): ("木", "정임합목"),
    (4, 9): ("火", "무계합화"),
}

# 지지 육합
BRANCH_LIU_HE = {
    (0, 1): ("土", "자축합토"),
    (2, 11): ("木", "인해합목"),
    (3, 10): ("火", "묘술합화"),
    (4, 9): ("金", "진유합금"),
    (5, 8): ("水", "사신합수"),
    (6, 7): ("火", "오미합화"),
}

# 지지 삼합 (3개 지지가 합쳐 변하는 오행)
BRANCH_SAN_HE = [
    ((8, 0, 4), "水", "신자진수국"),  # 申子辰 水
    ((11, 3, 7), "木", "해묘미목국"), # 亥卯未 木
    ((2, 6, 10), "火", "인오술화국"), # 寅午戌 火
    ((5, 9, 1), "金", "사유축금국"),  # 巳酉丑 金
]

# 지지 충 (대각선 6개 쌍)
BRANCH_CHONG = {
    (0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)
}


def get_ten_god(day_stem, other_stem):
    """일간(day_stem) 기준으로 other_stem이 십신 중 무엇인지 반환."""
    if other_stem is None:
        return None
    day_el = STEM_ELEMENT[day_stem]
    other_el = STEM_ELEMENT[other_stem]
    day_yy = STEM_YIN_YANG[day_stem]
    other_yy = STEM_YIN_YANG[other_stem]
    same_yy = (day_yy == other_yy)

    if other_el == day_el:
        return TEN_GODS[0] if same_yy else TEN_GODS[1]
    if ELEMENT_GENERATES.get(day_el) == other_el:
        return TEN_GODS[2] if same_yy else TEN_GODS[3]
    if ELEMENT_CONTROLS.get(day_el) == other_el:
        return TEN_GODS[4] if same_yy else TEN_GODS[5]
    if ELEMENT_CONTROLS.get(other_el) == day_el:
        return TEN_GODS[6] if same_yy else TEN_GODS[7]
    if ELEMENT_GENERATES.get(other_el) == day_el:
        return TEN_GODS[8] if same_yy else TEN_GODS[9]
    return None


def get_twelve_stage(day_stem, branch):
    """일간이 지지를 만났을 때의 십이운성."""
    start = STEM_LIFE_START_BRANCH[day_stem]
    direction = STEM_LIFE_DIRECTION[day_stem]
    diff = (branch - start) * direction
    return TWELVE_STAGES[diff % 12]
