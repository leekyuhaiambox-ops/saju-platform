"""GitHub Actions 자동 셋업 스크립트.

전제: 사용자가 Personal Access Token (PAT) 발급해서 환경변수 GH_TOKEN으로 제공.
이 스크립트는 다음을 모두 자동 처리:
  1. GitHub 레포지토리 생성 (없으면)
  2. 로컬 git 초기화 + 첫 커밋 + 푸시
  3. GitHub Secrets 4개 자동 등록 (libsodium 없이 PyNaCl 우회)
  4. 첫 워크플로우 수동 실행 트리거

사용법:
  python _github_setup.py <github_username> <repo_name> <PAT_token>

예:
  python _github_setup.py kyuha-lee saju-platform ghp_xxxxxxxxxx
"""
import os
import sys
import json
import base64
import subprocess
from urllib import request

if len(sys.argv) < 4:
    print("Usage: python _github_setup.py <username> <repo> <PAT>")
    sys.exit(1)

GH_USER = sys.argv[1]
GH_REPO = sys.argv[2]
GH_TOKEN = sys.argv[3]
API = "https://api.github.com"


def gh(method, path, body=None):
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    req = request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tarofortune-bot-setup/1.0",
    })
    try:
        with request.urlopen(req) as r:
            return r.status, json.loads(r.read()) if r.status != 204 else None
    except Exception as e:
        body_e = ""
        if hasattr(e, "read"):
            try:
                body_e = e.read().decode()
            except Exception:
                pass
        return getattr(e, "code", 0), {"error": str(e), "body": body_e}


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    """Encrypt secret value using repo's public key (libsodium-compatible)."""
    try:
        from nacl import encoding, public
    except ImportError:
        print("[setup] Installing PyNaCl...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pynacl"])
        from nacl import encoding, public
    pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def main():
    print(f"[1/5] Checking repo {GH_USER}/{GH_REPO}...")
    code, r = gh("GET", f"/repos/{GH_USER}/{GH_REPO}")
    if code == 404:
        print("  → 레포 없음. 생성 중...")
        code, r = gh("POST", "/user/repos", {
            "name": GH_REPO,
            "description": "Korean Saju (4-pillar astrology) calculator + auto-post bots",
            "private": False,
            "auto_init": False,
        })
        if code not in (200, 201):
            print(f"  ❌ Repo 생성 실패: {code} {r}")
            return
        print(f"  ✓ Repo 생성: {r.get('html_url')}")
    elif code == 200:
        print(f"  ✓ Repo 존재: {r.get('html_url')}")
    else:
        print(f"  ❌ Repo 조회 실패: {code} {r}")
        return

    print("[2/5] 로컬 git 초기화 + push...")
    # 토큰 포함 URL로 푸시
    push_url = f"https://{GH_USER}:{GH_TOKEN}@github.com/{GH_USER}/{GH_REPO}.git"
    cmds = [
        ["git", "init", "-b", "main"],
        ["git", "config", "user.email", f"{GH_USER}@users.noreply.github.com"],
        ["git", "config", "user.name", GH_USER],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit: Korean Saju calculator + auto-post bots"],
        ["git", "remote", "remove", "origin"],
        ["git", "remote", "add", "origin", push_url],
        ["git", "push", "-u", "origin", "main", "--force"],
    ]
    for cmd in cmds:
        # remote remove는 실패해도 무시
        ignore = (cmd[:3] == ["git", "remote", "remove"])
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               cwd=os.path.dirname(os.path.abspath(__file__)))
            if r.returncode == 0:
                print(f"  ✓ {' '.join(cmd[:3])} ...")
            elif not ignore:
                # git commit "nothing to commit" 은 무시
                if "nothing to commit" in (r.stdout + r.stderr).lower():
                    print(f"  ✓ {' '.join(cmd[:3])} (이미 커밋됨)")
                else:
                    print(f"  ⚠ {' '.join(cmd[:3])} → {r.stdout[-200:]} {r.stderr[-200:]}")
        except Exception as e:
            if not ignore:
                print(f"  ⚠ {cmd[:3]}: {e}")

    print("[3/5] Public key 조회 (시크릿 암호화용)...")
    code, key_data = gh("GET", f"/repos/{GH_USER}/{GH_REPO}/actions/secrets/public-key")
    if code != 200:
        print(f"  ❌ public key 실패: {code} {key_data}")
        return
    pub_key = key_data["key"]
    key_id = key_data["key_id"]
    print(f"  ✓ key_id={key_id}")

    print("[4/5] Secrets 등록 (.env 읽어서 4개 시크릿)...")
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")

    secrets_to_set = [
        "LEMMY_USERNAME", "LEMMY_PASSWORD",
        "MASTODON_ACCESS_TOKEN", "DEVTO_API_KEY",
    ]
    for name in secrets_to_set:
        val = env_vars.get(name, "")
        if not val:
            print(f"  ⚠ {name}: .env에 없음 - 건너뜀")
            continue
        encrypted = encrypt_secret(pub_key, val)
        code, r = gh("PUT", f"/repos/{GH_USER}/{GH_REPO}/actions/secrets/{name}", {
            "encrypted_value": encrypted,
            "key_id": key_id,
        })
        if code in (201, 204):
            print(f"  ✓ Secret 등록: {name}")
        else:
            print(f"  ❌ Secret 실패 {name}: {code} {r}")

    print("[5/5] 워크플로우 수동 첫 실행 트리거...")
    code, r = gh("POST",
                 f"/repos/{GH_USER}/{GH_REPO}/actions/workflows/daily-bot.yml/dispatches",
                 {"ref": "main"})
    if code == 204:
        print("  ✓ 첫 실행 트리거됨!")
    else:
        print(f"  ⚠ Trigger 응답: {code} {r}")

    print()
    print("=" * 60)
    print(f"✅ 셋업 완료!")
    print(f"  Repo:     https://github.com/{GH_USER}/{GH_REPO}")
    print(f"  Actions:  https://github.com/{GH_USER}/{GH_REPO}/actions")
    print(f"  Settings: https://github.com/{GH_USER}/{GH_REPO}/settings/secrets/actions")
    print("=" * 60)
    print()
    print("이후 매일 UTC 16:00 (KST 01:00)에 자동 실행됩니다.")
    print("PC가 꺼져 있어도 GitHub 서버에서 실행되므로 영향 없음.")


if __name__ == "__main__":
    main()
