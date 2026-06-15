"""Pinterest 자동 핀 봇 — API v5 (순수 urllib).

Pinterest 핀은 검색 기반이라 수개월~수년간 트래픽 유입 (에버그린).
사주 60갑자 카드 이미지 120장(한·영) 이미 보유 → 매일 1핀 자동 게시.

설정 (다소 번거로움):
1. business.pinterest.com 비즈니스 계정 전환 (무료)
2. developers.pinterest.com → 앱 생성 → access token 발급
   (Standard access 신청 필요할 수 있음. Trial access로도 본인 보드 핀 가능)
3. 보드 1개 생성 → board_id 확인

환경변수:
- PINTEREST_ACCESS_TOKEN
- PINTEREST_BOARD_ID
- SITE_URL

이미지는 공개 URL 필요 → 사이트의 og 카드 이미지 사용:
  https://tarofortune.pythonanywhere.com/static/img/og/pillar-{i}.png
"""
from __future__ import annotations
import os
import json
import random
from datetime import date
from pathlib import Path
from urllib import request

TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
BOARD_ID = os.environ.get("PINTEREST_BOARD_ID", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")
API = "https://api.pinterest.com/v5"

STATE_FILE = Path(os.environ.get(
    "PINTEREST_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".pinterest_state.json"),
))

try:
    from saju.interpreter import DAY_PILLAR_INTERPRETATIONS
except ImportError:
    DAY_PILLAR_INTERPRETATIONS = {}


def create_pin(idx: int) -> dict:
    if not TOKEN or not BOARD_ID:
        return {"ok": False, "error": "PINTEREST_ACCESS_TOKEN / PINTEREST_BOARD_ID missing"}
    info = DAY_PILLAR_INTERPRETATIONS.get(idx, ("?", "사주 일주", ""))
    # 핀 이미지: 세로형 Pinterest 핀 (1000x1500) 사용
    image_url = f"{SITE_URL}/static/img/pinterest-kr/pin-kr-{idx:02d}.png"
    link = f"{SITE_URL}/sixty-pillars/{idx}?utm_source=pinterest"
    body = json.dumps({
        "board_id": BOARD_ID,
        "title": f"{info[0]} 일주 — 사주 60갑자",
        "description": f"{info[1]} | {info[2][:300]} #사주 #일주 #사주풀이 #무료사주 #운세 #60갑자",
        "link": link,
        "media_source": {"source_type": "image_url", "url": image_url},
    }).encode()
    req = request.Request(f"{API}/pins", data=body, method="POST", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    })
    try:
        with request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read())
            return {"ok": True, "pin_id": data.get("id")}
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode()
            except Exception:
                pass
        return {"ok": False, "error": f"{e}: {b}"}


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"pinned": [], "last_date": None}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def run_daily():
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("[pinterest] already pinned today")
        return
    pinned = set(state.get("pinned", []))
    available = [i for i in range(60) if i not in pinned]
    if not available:
        state["pinned"] = []
        available = list(range(60))
    idx = random.choice(available)
    result = create_pin(idx)
    print(f"[pinterest] idx={idx} {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("pinned", []).append(idx)
        state["last_date"] = today
        save_state(state)


if __name__ == "__main__":
    run_daily()
