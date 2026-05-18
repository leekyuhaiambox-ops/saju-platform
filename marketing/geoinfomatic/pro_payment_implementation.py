"""
geoinfomatic Pro 결제 페이지 — Flask 구현 보일러플레이트
========================================================

이 파일을 geoinfomatic PA 서버의 Flask 앱에 통합:
  1. 이 모듈을 `pro_routes.py`로 PA에 업로드
  2. main Flask 앱 (`flask_app.py` 또는 `app.py`)에서 다음과 같이 등록:
       from pro_routes import pro_bp
       app.register_blueprint(pro_bp)
  3. templates/pro.html, templates/checkout.html 업로드
  4. PA Web 탭 → Reload

결제 모듈
---------
권장: **Toss Payments** (간편·국내 1위·테스트키 즉시 발급)
  - 가입: https://www.tossPayments.com
  - 결제위젯 JS SDK: <script src="https://js.tosspayments.com/v1/payment-widget"></script>
  - 테스트 클라이언트키: test_ck_... (개발자 콘솔에서 발급)
  - 환경변수: TOSS_CLIENT_KEY, TOSS_SECRET_KEY

대안: **Kakao Pay** (카카오톡 연동), **Naver Pay** (네이버 회원)

DB 스키마 (SQLite·기존 DB에 테이블 추가)
----------------------------------------
CREATE TABLE pro_subscription (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  status TEXT NOT NULL,                  -- 'active', 'cancelled', 'expired'
  plan TEXT DEFAULT 'monthly',
  started_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  toss_billing_key TEXT,                 -- 정기결제용
  toss_payment_key TEXT,                 -- 마지막 결제 키
  amount INTEGER DEFAULT 9900,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pro_payment_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subscription_id INTEGER NOT NULL,
  toss_payment_key TEXT NOT NULL,
  order_id TEXT NOT NULL UNIQUE,
  amount INTEGER NOT NULL,
  status TEXT NOT NULL,                  -- 'DONE', 'CANCELED', 'FAILED'
  raw_response TEXT,                     -- Toss 응답 JSON
  paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
from __future__ import annotations
import json
import os
import uuid
from datetime import datetime, timedelta
from urllib import request, parse, error
import base64

from flask import Blueprint, render_template, request as flask_request, jsonify, session, redirect, url_for, abort

pro_bp = Blueprint("pro", __name__)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

TOSS_CLIENT_KEY = os.environ.get("TOSS_CLIENT_KEY", "test_ck_PLACEHOLDER")
TOSS_SECRET_KEY = os.environ.get("TOSS_SECRET_KEY", "test_sk_PLACEHOLDER")
PRO_PRICE_KRW = int(os.environ.get("PRO_PRICE_KRW", "9900"))
PRO_PLAN_NAME = "생활권 분석 Pro · 월간"

SUCCESS_URL = "/pro/success"
FAIL_URL = "/pro/fail"


# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@pro_bp.route("/pro", methods=["GET"])
def pro_landing():
    """Pro 랜딩 페이지 — SEO + 결제 진입."""
    return render_template(
        "pro.html",
        price=PRO_PRICE_KRW,
        plan_name=PRO_PLAN_NAME,
        client_key=TOSS_CLIENT_KEY,
    )


@pro_bp.route("/pro/checkout", methods=["GET"])
def pro_checkout():
    """결제 위젯 페이지 — Toss Payments 결제위젯 SDK 렌더."""
    user_id = session.get("user_id") or _create_anonymous_user_id()
    session["user_id"] = user_id
    order_id = f"GEO-PRO-{uuid.uuid4().hex[:16].upper()}"
    return render_template(
        "checkout.html",
        client_key=TOSS_CLIENT_KEY,
        order_id=order_id,
        amount=PRO_PRICE_KRW,
        order_name=PRO_PLAN_NAME,
        customer_key=str(user_id),
        success_url=flask_request.host_url.rstrip("/") + SUCCESS_URL,
        fail_url=flask_request.host_url.rstrip("/") + FAIL_URL,
    )


@pro_bp.route("/pro/success", methods=["GET"])
def pro_success():
    """결제 승인 콜백 — Toss가 GET으로 리다이렉트."""
    payment_key = flask_request.args.get("paymentKey")
    order_id = flask_request.args.get("orderId")
    amount = int(flask_request.args.get("amount", "0"))

    if not (payment_key and order_id and amount == PRO_PRICE_KRW):
        return render_template("pro_fail.html", reason="결제 정보 불일치"), 400

    try:
        confirm_resp = _toss_confirm(payment_key, order_id, amount)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return render_template("pro_fail.html", reason=f"Toss 승인 실패: {body}"), 400
    except Exception as e:
        return render_template("pro_fail.html", reason=f"승인 호출 오류: {e}"), 500

    if confirm_resp.get("status") != "DONE":
        return render_template("pro_fail.html", reason="결제 상태 비정상"), 400

    user_id = session.get("user_id")
    sub_id = _activate_subscription(user_id, payment_key, order_id, amount, confirm_resp)
    return render_template("pro_success.html", subscription_id=sub_id, expires_at=_get_expiry(user_id))


@pro_bp.route("/pro/fail", methods=["GET"])
def pro_fail():
    code = flask_request.args.get("code", "")
    message = flask_request.args.get("message", "결제가 취소되었습니다.")
    return render_template("pro_fail.html", reason=f"{code}: {message}")


@pro_bp.route("/api/pro/status", methods=["GET"])
def pro_status_api():
    """현재 사용자의 Pro 상태 — 프론트에서 광고·5회 제한 토글에 사용."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"active": False, "plan": None})
    active, expires = _check_active(user_id)
    return jsonify({
        "active": active,
        "plan": PRO_PLAN_NAME if active else None,
        "expires_at": expires.isoformat() if expires else None,
    })


# ---------------------------------------------------------------------------
# TOSS PAYMENTS HELPERS
# ---------------------------------------------------------------------------

def _toss_confirm(payment_key: str, order_id: str, amount: int) -> dict:
    """Toss Payments 결제 승인 API 호출."""
    url = f"https://api.tosspayments.com/v1/payments/confirm"
    auth = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()
    body = json.dumps({
        "paymentKey": payment_key,
        "orderId": order_id,
        "amount": amount,
    }).encode()
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# DB HELPERS (실제 DB 함수로 교체 필요)
# ---------------------------------------------------------------------------

def _activate_subscription(user_id: int, payment_key: str, order_id: str,
                           amount: int, raw: dict) -> int:
    """결제 성공 시 구독 활성화. 실제 DB 함수로 교체 필요."""
    # TODO: 실제 SQLite 또는 ORM 호출
    expires_at = datetime.utcnow() + timedelta(days=30)
    print(f"[Pro Activated] user_id={user_id} expires={expires_at} payment_key={payment_key}")
    return 1  # placeholder subscription_id


def _check_active(user_id: int) -> tuple[bool, datetime | None]:
    """현재 구독 활성 여부. 실제 DB 조회로 교체 필요."""
    # TODO: SELECT * FROM pro_subscription WHERE user_id=? AND status='active' AND expires_at > NOW()
    return False, None


def _get_expiry(user_id: int) -> datetime:
    return datetime.utcnow() + timedelta(days=30)


def _create_anonymous_user_id() -> int:
    """비회원 결제 지원 — 세션에만 ID 부여."""
    return int(uuid.uuid4().int & 0xFFFFFFFF)
