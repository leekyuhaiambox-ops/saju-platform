"""
Email Nurturing 시스템 — Brevo (formerly Sendinblue) 통합
========================================================

수집된 이메일(.email_capture.jsonl)을 Brevo로 자동 동기화 + 무료→Pro 전환 funnel 발송.

운영자 셋업
-----------
1. https://brevo.com 가입 (무료 300건/일)
2. API 키 발급: Settings → SMTP & API → API Keys
3. List 생성: Contacts → Lists → "marketing" 만들기
4. 환경변수 추가:
   BREVO_API_KEY=xkeysib-...
   BREVO_LIST_ID=2  (생성한 list의 ID)
   BREVO_SENDER_EMAIL=leekyuha.iambox@gmail.com
   BREVO_SENDER_NAME=austriano

발송 시나리오
------------
- Day 0: 환영 메일 (사이트 가족 소개)
- Day 3: 사주 풀이 사용 팁
- Day 7: currency-map 소개 + 사용법
- Day 14: geoinfomatic Pro 30% off 코드 (수익 funnel)
- Day 30: 인플루언서·블로거이면 협업 제안

실행
----
# .email_capture.jsonl을 읽어 Brevo로 sync
python email_nurture_brevo.py --sync

# 시나리오별 발송 (cron 권장)
python email_nurture_brevo.py --send welcome

비용
----
무료 plan: 300건/일, 9,000건/월. 시작 단계엔 충분.
유료: 월 $25 (10K건) — 1,000명 이메일 모은 후 검토.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_LIST_ID = int(os.environ.get("BREVO_LIST_ID", "0"))
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "")
BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "austriano")

EMAIL_LOG_LOCAL = Path("C:/Users/master/CEO/saju_platform/.email_capture.jsonl")
SYNC_STATE = Path(__file__).parent / "state" / "brevo_sync_state.json"


# ---------------------------------------------------------------------------
# Brevo API helpers
# ---------------------------------------------------------------------------

def _api(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    if not BREVO_API_KEY:
        raise RuntimeError("BREVO_API_KEY env missing")
    url = f"https://api.brevo.com/v3{path}"
    headers = {
        "api-key": BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:400]}


def create_contact(email: str, attributes: dict | None = None) -> bool:
    body = {
        "email": email,
        "listIds": [BREVO_LIST_ID] if BREVO_LIST_ID else [],
        "attributes": attributes or {},
        "updateEnabled": True,
    }
    code, _ = _api("POST", "/contacts", body)
    return code in (200, 201, 204)


def send_transactional(to_email: str, subject: str, html: str,
                       params: dict | None = None) -> bool:
    """단발 transactional 메일."""
    body = {
        "sender": {"email": BREVO_SENDER_EMAIL, "name": BREVO_SENDER_NAME},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
    }
    if params:
        body["params"] = params
    code, _ = _api("POST", "/smtp/email", body)
    return code in (200, 201)


# ---------------------------------------------------------------------------
# Email templates (HTML)
# ---------------------------------------------------------------------------

WELCOME_HTML = """\
<!DOCTYPE html>
<html><body style="font-family:'Apple SD Gothic Neo',sans-serif;color:#1a0f2e;padding:24px;max-width:560px;margin:0 auto;line-height:1.6">
  <h2 style="color:#5e2da6">구독해 주셔서 감사합니다 ✨</h2>
  <p>안녕하세요, austriano입니다. 새 도구·풀이 콘텐츠 알림에 함께해 주셔서 감사해요.</p>

  <p>혹시 저의 다른 도구를 모르신다면 한번 확인해 보세요. 모두 무료(또는 freemium)에 광고만으로 운영합니다.</p>

  <table cellpadding="14" style="background:#f6f0ff;border-radius:12px;border-collapse:collapse;width:100%;margin:18px 0;">
    <tr>
      <td style="font-size:24px;width:48px;">🔮</td>
      <td>
        <strong><a href="https://tarofortune.pythonanywhere.com/?utm_source=email&utm_campaign=welcome">사주명리 풀이</a></strong><br>
        <span style="font-size:13px;color:#666">60갑자 일주 + 오행 + 십신 + 일진. 무료, EN+KR.</span>
      </td>
    </tr>
    <tr>
      <td style="font-size:24px;">🗺</td>
      <td>
        <strong><a href="https://gyeonggi-currency-map.web.app/?utm_source=email&utm_campaign=welcome">경기지역화폐 가맹점 지도</a></strong><br>
        <span style="font-size:13px;color:#666">31개 시·군 통합. 영업중 필터 + PWA.</span>
      </td>
    </tr>
    <tr>
      <td style="font-size:24px;">🏘</td>
      <td>
        <strong><a href="https://geoinfomatic.pythonanywhere.com/?utm_source=email&utm_campaign=welcome">생활권 접근성 분석</a></strong><br>
        <span style="font-size:13px;color:#666">이사·임장 도보 30분 동네 점수.</span>
      </td>
    </tr>
  </table>

  <p>새 풀이·도구 출시 시 한 달에 1~2번만 이런 메일을 보냅니다. 스팸 X.</p>

  <p style="font-size:12px;color:#888;margin-top:30px;border-top:1px solid #eee;padding-top:12px;">
    이 메일은 {{params.source}} 경로로 가입하셨습니다. 구독 해지: <a href="{{ unsubscribe }}">여기 클릭</a>
  </p>
</body></html>
"""


# ---------------------------------------------------------------------------
# Sync .email_capture.jsonl -> Brevo
# ---------------------------------------------------------------------------

def sync_to_brevo() -> tuple[int, int]:
    """로컬 .email_capture.jsonl을 Brevo contacts로 sync. 이미 동기화된 항목은 skip."""
    state = {}
    if SYNC_STATE.exists():
        state = json.loads(SYNC_STATE.read_text(encoding="utf-8"))
    synced = set(state.get("synced_emails", []))
    new_synced = []
    failed = 0

    if not EMAIL_LOG_LOCAL.exists():
        print(f"⚠️ {EMAIL_LOG_LOCAL} 없음 — PA에서 다운로드 필요")
        return 0, 0

    with open(EMAIL_LOG_LOCAL, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
                email = e["email"]
                if email in synced:
                    continue
                attrs = {
                    "SOURCE": e.get("source", ""),
                    "REF": e.get("ref", ""),
                    "SUBSCRIBED_AT": e.get("ts", ""),
                }
                if create_contact(email, attrs):
                    new_synced.append(email)
                else:
                    failed += 1
            except Exception:
                failed += 1

    if new_synced:
        state["synced_emails"] = sorted(synced | set(new_synced))
        state["last_sync"] = datetime.now(timezone.utc).isoformat()
        SYNC_STATE.parent.mkdir(parents=True, exist_ok=True)
        SYNC_STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    return len(new_synced), failed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", action="store_true", help="JSONL → Brevo sync")
    ap.add_argument("--send", choices=["welcome"], help="발송 시나리오")
    ap.add_argument("--to", help="단일 발송 대상 이메일")
    args = ap.parse_args()

    if not BREVO_API_KEY:
        print("⚠️ BREVO_API_KEY 환경변수가 없습니다.")
        print("   https://brevo.com 가입 → Settings → API Keys")
        return 1

    if args.sync:
        synced, failed = sync_to_brevo()
        print(f"Synced: {synced} new, {failed} failed")

    if args.send == "welcome" and args.to:
        ok = send_transactional(args.to, "구독 감사합니다 — 다른 도구도 소개해 드려요",
                                WELCOME_HTML, params={"source": "manual"})
        print(f"Welcome to {args.to}: {ok}")


if __name__ == "__main__":
    sys.exit(main() or 0)
