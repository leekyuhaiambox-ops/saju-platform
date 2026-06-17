"""GitHub Secrets 원클릭 등록 — Bluesky/Telegram/Pinterest 자격증명만 채우고 실행.

사용법:
  1) 아래 CREDS 에 본인 값 채우기 (빈 값은 자동 건너뜀)
     - Bluesky: bsky.app → Settings → Privacy and Security → App Passwords → 생성
     - Telegram: 텔레그램에서 @BotFather → /newbot → 토큰 받기 / 채널은 @채널아이디
     - Pinterest: developers.pinterest.com → 앱 생성 → access token
  2) 터미널에서:  python SET_SECRETS.py
     → GitHub 레포 Secrets 에 자동 등록됨. 다음 cron(매일 UTC16:00)부터 봇이 자동 게시.

PAT는 git remote URL 또는 환경변수 GH_TOKEN 에서 자동으로 읽음(하드코딩 안 함).
PyNaCl 필요: 없으면 자동 설치 시도.
"""
import os
import re
import sys
import json
import base64
import subprocess
from urllib import request

# ─── 여기에 본인 값만 채우세요 (빈 값은 건너뜀) ───────────────
CREDS = {
    "BLUESKY_HANDLE": "",          # 예: tarofortune.bsky.social
    "BLUESKY_APP_PASSWORD": "",    # 예: xxxx-xxxx-xxxx-xxxx
    "TELEGRAM_BOT_TOKEN": "",      # 예: 123456:ABC-DEF...
    "TELEGRAM_CHANNEL": "",        # 예: @tarofortune_kr
    "PINTEREST_ACCESS_TOKEN": "",
    "PINTEREST_BOARD_ID": "",
}
# ──────────────────────────────────────────────────────────

REPO = "leekyuhaiambox-ops/saju-platform"
API = f"https://api.github.com/repos/{REPO}"


def get_token() -> str:
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
        ).decode().strip()
    except Exception:
        url = ""
    m = re.search(r"://([^:@/]+):([^@/]+)@github", url) or re.search(r"://([^@/]+)@github", url)
    if m:
        return m.groups()[-1]
    sys.exit("GitHub 토큰을 찾을 수 없습니다. 환경변수 GH_TOKEN 을 설정하거나 git remote 에 토큰이 포함돼야 합니다.")


def _api(method, path, token, body=None):
    req = request.Request(f"{API}{path}", method=method,
                          data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with request.urlopen(req) as r:
        raw = r.read().decode()
        return r.status, (json.loads(raw) if raw else {})


def ensure_pynacl():
    try:
        import nacl  # noqa
        return
    except ImportError:
        print("PyNaCl 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pynacl"])


def main():
    todo = {k: v.strip() for k, v in CREDS.items() if v.strip()}
    if not todo:
        print("채워진 값이 없습니다. 파일 상단 CREDS 에 본인 자격증명을 입력한 뒤 다시 실행하세요.")
        print("현재 등록 대상 후보:", ", ".join(CREDS.keys()))
        return

    ensure_pynacl()
    from nacl import encoding, public

    token = get_token()
    # 레포 공개키 (Secrets 암호화용)
    _, key = _api("GET", "/actions/secrets/public-key", token)
    pk = public.PublicKey(key["key"].encode(), encoding.Base64Encoder())
    box = public.SealedBox(pk)

    for name, value in todo.items():
        enc = base64.b64encode(box.encrypt(value.encode())).decode()
        st, _ = _api("PUT", f"/actions/secrets/{name}", token,
                     {"encrypted_value": enc, "key_id": key["key_id"]})
        print(f"  {'✅ 등록' if st in (201, 204) else '⚠ ' + str(st)}  {name}")

    print("\n완료! 다음 자동 실행(매일 UTC 16:00 = KST 새벽 1시)부터 해당 채널 봇이 게시합니다.")
    print("지금 바로 테스트하려면 GitHub → Actions → 'Daily Bot' → Run workflow 를 눌러보세요.")


if __name__ == "__main__":
    main()
