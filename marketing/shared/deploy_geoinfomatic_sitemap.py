"""
geoinfomatic sitemap 버그 수정 자동 배포 스크립트
==================================================

현재 sitemap.xml에 메인 페이지 `/` 가 누락된 SEO 버그를 자동 수정.

작동 방식 (두 가지 경로)
-----------------------
1. **PA API 자동 배포** (geoinfomatic PA 토큰 필요)
   환경변수 `GEOINFOMATIC_PA_TOKEN` 설정 후 실행하면
   sitemap.py 또는 routes.py를 자동 패치 + Web 앱 reload.

2. **패치 스니펫만 출력** (토큰 없을 때)
   PA Files 탭에서 직접 붙여넣기 할 수 있는 패치 코드를 출력.

PA API 토큰 발급
---------------
1. https://www.pythonanywhere.com 로그인 (geoinfomatic 계정)
2. Account → API token → "Create new token" 클릭
3. 토큰 복사 → 환경변수 설정:
   Windows PowerShell: $env:GEOINFOMATIC_PA_TOKEN = "abc123..."
   Linux/Mac: export GEOINFOMATIC_PA_TOKEN="abc123..."

실행
----
python -X utf8 deploy_geoinfomatic_sitemap.py
"""
from __future__ import annotations
import json
import os
import sys
from urllib import request, error

PA_USER = os.environ.get("GEOINFOMATIC_PA_USER", "geoinfomatic")
PA_TOKEN = os.environ.get("GEOINFOMATIC_PA_TOKEN", "")
PA_DOMAIN = os.environ.get("GEOINFOMATIC_PA_DOMAIN", "geoinfomatic.pythonanywhere.com")

PA_API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{PA_USER}"


# ---------------------------------------------------------------------------
# 패치 스니펫 — 사용자가 직접 적용할 수도 있는 코드
# ---------------------------------------------------------------------------

SITEMAP_FIX_INSTRUCTIONS = """
==================================================================
geoinfomatic sitemap 버그 수정 가이드 (수동 적용)
==================================================================

현재 sitemap.xml은 /profile/* URL 28개만 있고 메인 페이지 /가 누락됨.
이로 인해 Google·Naver가 메인 서비스를 색인하지 못함.

수정 방법 (세 가지 옵션)
------------------------

[옵션 1] sitemap 생성 함수 직접 패치
- Flask 앱에서 sitemap.xml을 동적 생성하는 함수를 찾아서 다음을 추가:

```python
@app.route('/sitemap.xml')
def sitemap():
    urls = [
        # === FIX: 메인 페이지 ===
        ('/', '1.0', 'weekly'),
        # === 권장 추가 ===
        ('/pro', '0.9', 'monthly'),
        ('/about', '0.7', 'monthly'),
        ('/faq', '0.6', 'monthly'),
        # === 기존 /profile/* URL은 유지 ===
        ('/profile', '0.8', 'weekly'),
        ('/profile/project/1', '0.6', 'monthly'),
        # ... (기존 코드 계속)
    ]
    # ...
```

[옵션 2] 정적 파일 교체
- `static/sitemap.xml` 파일을 다음 위치의 수정안으로 교체:
  marketing/shared/sitemap_geoinfomatic_fixed.xml

[옵션 3] 본 스크립트로 자동 배포
- PA 토큰 환경변수 설정 후 실행:
  $env:GEOINFOMATIC_PA_TOKEN = "..."
  python deploy_geoinfomatic_sitemap.py

==================================================================
적용 후 검증
==================================================================

1. 명령어 확인:
   curl https://geoinfomatic.pythonanywhere.com/sitemap.xml | head

   첫 번째 <url>이 https://geoinfomatic.pythonanywhere.com/ 이어야 함.

2. Google Search Console 재제출:
   - https://search.google.com/search-console
   - 사이트 선택 → 사이트맵 → 새 사이트맵 추가 → sitemap.xml

3. Naver 서치어드바이저 재제출:
   - https://searchadvisor.naver.com
   - 사이트 → 요청 → 사이트맵 제출

4. IndexNow 즉시 색인 (3분 내 처리):
   python multi_site_orchestrator.py --site geoinfomatic --channel indexnow

==================================================================
"""


# ---------------------------------------------------------------------------
# PA API 헬퍼
# ---------------------------------------------------------------------------

def _pa_request(method: str, path: str, body: bytes | None = None, content_type: str | None = None) -> bytes:
    """PA REST API 호출."""
    if not PA_TOKEN:
        raise RuntimeError("GEOINFOMATIC_PA_TOKEN 환경변수 없음")
    headers = {"Authorization": f"Token {PA_TOKEN}"}
    if content_type:
        headers["Content-Type"] = content_type
    url = f"{PA_API_BASE}{path}"
    req = request.Request(url, data=body, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PA API {method} {path} → {e.code}: {body_text}") from e


def pa_list_files(remote_path: str) -> dict:
    """PA 원격 파일/폴더 목록."""
    return json.loads(_pa_request("GET", f"/files/tree/?path={remote_path}"))


def pa_read_file(remote_path: str) -> bytes:
    """PA 원격 파일 읽기."""
    return _pa_request("GET", f"/files/path{remote_path}")


def pa_write_file(remote_path: str, content: bytes) -> None:
    """PA 원격 파일 덮어쓰기 (multipart upload)."""
    # PA Files API multipart 업로드
    boundary = "----PADeployBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="content"; filename="upload"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    headers_extra = f"multipart/form-data; boundary={boundary}"
    _pa_request("POST", f"/files/path{remote_path}", body=body, content_type=headers_extra)


def pa_reload_webapp() -> None:
    """PA Web 앱 reload."""
    _pa_request("POST", f"/webapps/{PA_DOMAIN}/reload/", body=b"")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if not PA_TOKEN:
        print(SITEMAP_FIX_INSTRUCTIONS)
        print("\n⚠️ GEOINFOMATIC_PA_TOKEN 환경변수가 없어 자동 배포를 건너뜁니다.")
        print("   위 가이드 따라 수동 적용하시거나, 토큰 설정 후 재실행하세요.")
        return 1

    print(f"[Deploy] PA user: {PA_USER}")
    print(f"[Deploy] Domain: {PA_DOMAIN}")
    print(f"[Deploy] API token: ...{PA_TOKEN[-4:]}")

    # 1. 현재 sitemap 파일 위치 탐색
    candidates = [
        "/home/geoinfomatic/static/sitemap.xml",
        "/home/geoinfomatic/sitemap.xml",
        "/home/geoinfomatic/geoinfomatic/static/sitemap.xml",
    ]

    target_path = None
    for path in candidates:
        try:
            current = pa_read_file(path)
            print(f"\n[Found] {path} ({len(current)} bytes)")
            target_path = path
            break
        except RuntimeError as e:
            if "404" in str(e):
                continue
            raise

    if not target_path:
        print("\n⚠️ sitemap.xml을 찾지 못했습니다. 후보 경로:")
        for p in candidates:
            print(f"   {p}")
        print("\n수동으로 sitemap 생성 함수를 찾아서 패치하세요.")
        print(SITEMAP_FIX_INSTRUCTIONS)
        return 1

    # 2. 수정안 로딩
    fixed_path = os.path.join(os.path.dirname(__file__), "sitemap_geoinfomatic_fixed.xml")
    if not os.path.exists(fixed_path):
        print(f"\n⚠️ 수정안 파일 없음: {fixed_path}")
        return 1

    with open(fixed_path, "rb") as f:
        fixed_content = f.read()

    # 3. 백업 + 업로드
    backup_path = target_path + ".bak"
    print(f"\n[Backup] Writing backup to {backup_path}")
    pa_write_file(backup_path, current)

    print(f"[Deploy] Uploading fixed sitemap to {target_path}")
    pa_write_file(target_path, fixed_content)

    # 4. Reload
    print(f"[Reload] Triggering webapp reload...")
    pa_reload_webapp()

    print("\n✅ Sitemap 수정 배포 완료!")
    print(f"   검증: curl https://{PA_DOMAIN}/sitemap.xml | head")
    print("   Google Search Console에서 sitemap 재제출 권장.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
