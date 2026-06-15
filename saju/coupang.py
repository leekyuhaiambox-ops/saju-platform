"""쿠팡 파트너스 제휴 — 오행/일주별 맞춤 상품 추천.

전략: 디스플레이 광고는 CPM(노출당)이라 트래픽 적으면 수익 0에 가까움.
제휴(쿠팡 파트너스)는 CPS(판매당 ~3% 수수료)라 한 명만 사도 수익.
사주 결과에 맞춘 추천 = 클릭률·전환율 높음.

작동:
- COUPANG_PARTNERS_ID 환경변수 설정 시 활성
- 오행별 관련 상품 키워드 → 쿠팡 검색 딥링크 (파트너 태그 포함)
- 법적 필수: 쿠팡 파트너스 고지 문구 자동 노출

가입: https://partners.coupang.com → 채널(웹사이트) 등록 → 파트너스 ID(tag) 발급
환경변수 COUPANG_PARTNERS_ID 에 넣으면 즉시 작동.
"""
from __future__ import annotations
from urllib.parse import quote

# 법적 필수 고지 (한국 공정위 — 대가성 표시)
DISCLOSURE_KO = "이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."
DISCLOSURE_EN = "As a Coupang Partners affiliate, this page may earn a commission from qualifying purchases."

# 오행별 추천 상품 테마 (키워드 + 설명)
ELEMENT_PRODUCTS = {
    "목": [
        {"kw": "그린 아벤츄린 팔찌", "label": "녹색 천연석 팔찌", "why": "목(木) 기운을 북돋는 녹색 계열 아이템"},
        {"kw": "공기정화식물 화분", "label": "공기정화 식물", "why": "성장·생명력의 목 기운을 채우는 식물"},
        {"kw": "명리학 입문서", "label": "사주 명리학 책", "why": "지식과 성장을 상징하는 목 기운"},
    ],
    "화": [
        {"kw": "레드 가넷 팔찌", "label": "붉은 천연석 팔찌", "why": "화(火) 기운을 살리는 붉은 계열 아이템"},
        {"kw": "아로마 캔들 세트", "label": "아로마 캔들", "why": "불의 기운, 화 에너지를 더하는 캔들"},
        {"kw": "햇빛 무드등", "label": "따뜻한 조명", "why": "밝음과 표현의 화 기운"},
    ],
    "토": [
        {"kw": "황호안석 팔찌", "label": "황색 천연석 팔찌", "why": "토(土) 기운을 안정시키는 황색 아이템"},
        {"kw": "도자기 다기 세트", "label": "도자기 찻잔", "why": "흙의 기운, 안정과 중재의 토 에너지"},
        {"kw": "원목 트레이", "label": "원목 소품", "why": "땅의 안정감을 더하는 자연 소재"},
    ],
    "금": [
        {"kw": "실버 925 팔찌", "label": "은 액세서리", "why": "금(金) 기운을 살리는 은·금속 아이템"},
        {"kw": "스테인리스 텀블러", "label": "메탈 텀블러", "why": "결단과 정리의 금 기운"},
        {"kw": "만년필 선물세트", "label": "고급 만년필", "why": "정교함과 의리의 금 에너지"},
    ],
    "수": [
        {"kw": "블랙 오닉스 팔찌", "label": "검정 천연석 팔찌", "why": "수(水) 기운을 채우는 흑·청 계열 아이템"},
        {"kw": "가습기 무드등", "label": "가습기", "why": "물의 기운, 지혜와 흐름의 수 에너지"},
        {"kw": "디퓨저 세트", "label": "디퓨저", "why": "흐르는 물의 차분함, 수 기운"},
    ],
}

# 범용 추천 (오행 무관 — 사주/운세 관심층 타겟)
GENERAL_PRODUCTS = [
    {"kw": "타로카드 입문 세트", "label": "타로카드 세트", "why": "운세에 관심 있다면 타로도 함께"},
    {"kw": "명리학 사주 책 베스트셀러", "label": "사주 명리학 도서", "why": "사주를 더 깊이 공부하고 싶다면"},
    {"kw": "행운의 부적 카드", "label": "행운 아이템", "why": "한 해의 행운을 비는 아이템"},
    {"kw": "오늘의 운세 다이어리", "label": "운세 다이어리", "why": "매일의 운세를 기록하는 다이어리"},
]


def coupang_search_url(keyword: str, partners_id: str, sub_id: str = "saju") -> str:
    """쿠팡 검색 딥링크 (파트너스 추적 파라미터 포함).

    파트너스 ID가 있으면 추적 가능한 형태로, 없으면 일반 검색 링크.
    실제 수수료 추적은 쿠팡 파트너스 대시보드에서 생성한 딥링크가 가장 정확하나,
    검색 URL + subId 방식도 채널 등록 시 작동.
    """
    base = f"https://www.coupang.com/np/search?q={quote(keyword)}"
    if partners_id:
        # 쿠팡 파트너스 채널 추적: lptag(파트너스 ID) + subId(유입 위치)
        return f"{base}&lptag={partners_id}&subId={sub_id}"
    return base


def get_element_recommendations(element_kr: str, partners_id: str, sub_id: str = "result") -> dict:
    """오행 기준 추천 상품 3개 + 고지문 반환. partners_id 없으면 active=False."""
    products = ELEMENT_PRODUCTS.get(element_kr, GENERAL_PRODUCTS)
    items = [{
        "label": p["label"],
        "why": p["why"],
        "url": coupang_search_url(p["kw"], partners_id, sub_id),
    } for p in products]
    return {
        "active": bool(partners_id),
        "element": element_kr,
        "items": items,
        "disclosure": DISCLOSURE_KO,
    }


def get_general_recommendations(partners_id: str, sub_id: str = "general") -> dict:
    items = [{
        "label": p["label"],
        "why": p["why"],
        "url": coupang_search_url(p["kw"], partners_id, sub_id),
    } for p in GENERAL_PRODUCTS]
    return {
        "active": bool(partners_id),
        "items": items,
        "disclosure": DISCLOSURE_KO,
    }
