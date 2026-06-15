"""텔레그램 채널 자동 게시 봇 — 공식 Bot API (순수 urllib).

공식, 무료, 무제한. 한국어 콘텐츠로 한국 사용자 채널 운영.
설정:
1. @BotFather 에게 /newbot → 봇 생성 → TOKEN 받기
2. 텔레그램 채널 생성 (공개, 예: @tarofortune_saju)
3. 봇을 채널 관리자로 추가
4. CHANNEL = "@tarofortune_saju"

환경변수:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHANNEL (예: @tarofortune_saju 또는 채널 chat_id)
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
from datetime import date
from pathlib import Path
from urllib import request, parse

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")

STATE_FILE = Path(os.environ.get(
    "TELEGRAM_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".telegram_state.json"),
))

try:
    from saju.interpreter import DAY_PILLAR_INTERPRETATIONS
    from saju.daily import daily_fortune
except ImportError:
    DAY_PILLAR_INTERPRETATIONS = {}
    daily_fortune = None


def send_message(text: str, disable_preview: bool = False) -> dict:
    if not TOKEN or not CHANNEL:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN / TELEGRAM_CHANNEL missing"}
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = parse.urlencode({
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true" if disable_preview else "false",
    }).encode()
    req = request.Request(url, data=data, method="POST")
    try:
        with request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
            return {"ok": resp.get("ok", False), "msg_id": resp.get("result", {}).get("message_id")}
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
    return {"posted_pillars": [], "last_date": None}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def run_daily():
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("[telegram] already posted today")
        return

    # 1) 오늘의 일진 (매일 가치 있는 콘텐츠)
    today_text = ""
    if daily_fortune:
        try:
            f = daily_fortune(date.today())
            today_text = (
                f"🔮 <b>오늘의 일진</b> ({today})\n\n"
                f"일진: <b>{f['day_pillar_name']}</b>({f['day_pillar_hanja']})\n"
                f"키워드: {f['keyword_title']}\n"
                f"{f['keyword_body']}\n\n"
                f"🎨 행운의 색: {f['lucky_color']}\n"
                f"🧭 행운의 방위: {f['lucky_direction']}\n"
                f"🔢 행운의 숫자: {f['lucky_number']}\n\n"
                f"👉 내 사주 전체 풀이: {SITE_URL}"
            )
        except Exception as e:
            print(f"[telegram] daily_fortune error: {e}")

    if today_text:
        result = send_message(today_text)
        print(f"[telegram] daily fortune: {json.dumps(result, ensure_ascii=False)}")
        if result.get("ok"):
            state["last_date"] = today
            save_state(state)
            return

    # 2) 폴백: 60갑자 일주 소개
    posted = set(state.get("posted_pillars", []))
    available = [i for i in range(60) if i not in posted]
    if not available:
        state["posted_pillars"] = []
        available = list(range(60))
    idx = random.choice(available)
    info = DAY_PILLAR_INTERPRETATIONS.get(idx)
    if not info:
        return
    text = (
        f"📜 <b>60갑자 일주 — {info[0]}</b>\n\n"
        f"{info[1]}\n\n{info[2][:200]}\n\n"
        f"👉 내 일주 무료로 보기: {SITE_URL}"
    )
    result = send_message(text)
    print(f"[telegram] pillar {idx}: {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted_pillars", []).append(idx)
        state["last_date"] = today
        save_state(state)


if __name__ == "__main__":
    run_daily()
