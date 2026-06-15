"""후원/팁 + 프리미엄 리포트 — 사업자 등록 없이 즉시 수익화 가능한 채널.

수익화 사다리:
1. 디스플레이 광고 (AdFit/AdSense) — 트래픽 필요
2. 쿠팡 파트너스 — 제휴, 전환당 수익
3. 후원/팁 (toss.me, BuyMeaCoffee) — 사업자 등록 X, 트래픽 적어도 가능 ← 이것
4. 프리미엄 PG 결제 — 사업자 등록 필요 (나중)

toss.me: 토스 앱에서 개인 송금 링크 무료 생성 (사업자 X). toss.me/<id>
BuyMeaCoffee: buymeacoffee.com/<id> (해외 후원, 카드 결제)

환경변수:
- TOSS_ME_ID (예: "abc123" → https://toss.me/abc123)
- BUYMEACOFFEE_ID (예: "tarofortune")
- KAKAOPAY_LINK (카카오페이 송금 QR 링크 전체 URL)
"""
from __future__ import annotations
import os


def get_support_links() -> dict:
    toss = os.environ.get("TOSS_ME_ID", "")
    bmc = os.environ.get("BUYMEACOFFEE_ID", "")
    kakao = os.environ.get("KAKAOPAY_LINK", "")
    links = []
    if toss:
        links.append({
            "label": "토스로 후원하기",
            "url": f"https://toss.me/{toss}",
            "color": "#0064ff", "emoji": "💙",
            "desc": "토스 앱으로 간편하게",
        })
    if kakao:
        links.append({
            "label": "카카오페이 후원",
            "url": kakao,
            "color": "#ffeb00", "color_text": "#3c1e1e", "emoji": "💛",
            "desc": "카카오페이로 간편하게",
        })
    if bmc:
        links.append({
            "label": "Buy me a coffee",
            "url": f"https://www.buymeacoffee.com/{bmc}",
            "color": "#ffdd00", "color_text": "#000", "emoji": "☕",
            "desc": "Support with a coffee (card)",
        })
    return {"active": bool(links), "links": links}


# 프리미엄 리포트 구성 (PG 결제 붙이면 활성, 지금은 알림 신청)
PREMIUM_FEATURES = [
    {"icon": "📅", "title": "12개월 월별 상세 운세",
     "desc": "올해 1월부터 12월까지, 매달의 흐름을 월별로 풀어드립니다."},
    {"icon": "💕", "title": "연애·결혼 심층 분석",
     "desc": "배우자궁·도화·홍염 등 인연 관련 모든 요소를 종합 분석."},
    {"icon": "💼", "title": "직업·재물운 리포트",
     "desc": "재성·관성·식상 흐름으로 본 적성 직업과 재물 시기."},
    {"icon": "⭐", "title": "신살(神煞) 전체 분석",
     "desc": "천을귀인·역마·화개 등 12신살을 모두 짚어드립니다."},
    {"icon": "📄", "title": "PDF 소장본",
     "desc": "분석 결과를 깔끔한 PDF로 받아 영구 소장."},
]
PREMIUM_PRICE = os.environ.get("PREMIUM_PRICE", "9,900")
