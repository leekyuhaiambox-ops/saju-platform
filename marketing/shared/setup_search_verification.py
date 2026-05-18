"""
Search Console 사이트 인증 일괄 설정 헬퍼
==========================================

3사이트(tarofortune / currency-map / geoinfomatic)에
Google · Naver · Bing · Yandex 사이트 인증 메타태그를
자동으로 박는 헬퍼 스크립트.

사용 흐름
---------
1. 각 검색엔진 콘솔에서 사이트 등록 + 메타태그 인증코드 발급
2. 본 스크립트의 VERIFICATION_CODES 딕셔너리에 입력
3. 실행 → 사이트별 적용 명령 출력 (또는 자동 적용)

콘솔 URL
--------
| 엔진 | 가입 URL | 인증 방식 |
|---|---|---|
| Google | https://search.google.com/search-console | HTML 메타 |
| Naver | https://searchadvisor.naver.com | HTML 메타 |
| Bing | https://www.bing.com/webmasters | HTML 메타 |
| Yandex | https://webmaster.yandex.com | HTML 메타 |

각 인증 후 발급 받은 content="..." 값을 다음 표에 입력하세요.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# VERIFICATION CODES — 각 콘솔에서 받은 값으로 채우세요
# ---------------------------------------------------------------------------

VERIFICATION_CODES = {
    "tarofortune": {
        "google": "",   # <meta name="google-site-verification" content="...">
        "naver":  "",   # <meta name="naver-site-verification" content="...">
        "bing":   "",   # <meta name="msvalidate.01" content="...">
        "yandex": "",   # <meta name="yandex-verification" content="...">
    },
    "currency-map": {
        "google": "",
        "naver":  "",
        "bing":   "",
        "yandex": "",
    },
    "geoinfomatic": {
        "google": "",
        "naver":  "",
        "bing":   "",
        "yandex": "",
    },
}


# ---------------------------------------------------------------------------
# 메타 태그 생성
# ---------------------------------------------------------------------------

META_TEMPLATES = {
    "google": '<meta name="google-site-verification" content="{value}" />',
    "naver":  '<meta name="naver-site-verification" content="{value}" />',
    "bing":   '<meta name="msvalidate.01" content="{value}" />',
    "yandex": '<meta name="yandex-verification" content="{value}" />',
}


def render_meta_block(site: str) -> str:
    codes = VERIFICATION_CODES.get(site, {})
    lines = []
    lines.append(f"<!-- Search engine verification (auto-generated) -->")
    for engine, value in codes.items():
        if value:
            lines.append(META_TEMPLATES[engine].format(value=value))
        else:
            lines.append(f"<!-- {engine}: pending -->")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 사이트별 적용 가이드
# ---------------------------------------------------------------------------

SITE_PATCH_GUIDES = {
    "tarofortune": {
        "tech": "Flask + PythonAnywhere",
        "target_file": "saju_platform/templates/base.html",
        "patch_location": "<head> 안, <title> 태그 직후",
        "deploy": "PA Web 탭 → Reload, 또는 `python _deploy.py`",
        "verify_url": "https://tarofortune.pythonanywhere.com/",
    },
    "currency-map": {
        "tech": "React + Vite + Firebase Hosting",
        "target_file": "(repo)/index.html",
        "patch_location": "<head> 안, 기존 <meta name='description'> 직후",
        "deploy": "vite build && firebase deploy",
        "verify_url": "https://gyeonggi-currency-map.web.app/",
    },
    "geoinfomatic": {
        "tech": "Flask + PythonAnywhere",
        "target_file": "(home)/geoinfomatic/templates/base.html (또는 index.html)",
        "patch_location": "<head> 안, <title> 태그 직후",
        "deploy": "PA Web 탭 → Reload, 또는 wsgi.py touch",
        "verify_url": "https://geoinfomatic.pythonanywhere.com/",
    },
}


def print_patch_guide(site: str):
    guide = SITE_PATCH_GUIDES.get(site, {})
    meta_block = render_meta_block(site)
    print(f"\n{'='*72}")
    print(f"  사이트: {site}")
    print(f"  기술: {guide.get('tech', '?')}")
    print(f"  타깃 파일: {guide.get('target_file', '?')}")
    print(f"  패치 위치: {guide.get('patch_location', '?')}")
    print(f"{'='*72}")
    print("\n다음 메타 블록을 위 파일의 <head>에 추가하세요:\n")
    print(meta_block)
    print(f"\n배포: {guide.get('deploy', '?')}")
    print(f"검증: {guide.get('verify_url', '?')}")


# ---------------------------------------------------------------------------
# 자동 패치 (tarofortune Flask 템플릿)
# ---------------------------------------------------------------------------

def auto_patch_tarofortune():
    """tarofortune의 saju_platform/templates/base.html에 메타 블록 자동 추가."""
    base_path = Path(__file__).resolve().parent.parent.parent / "saju_platform" / "templates" / "base.html"
    if not base_path.exists():
        print(f"[WARN] {base_path} 없음 — 자동 패치 스킵")
        return

    content = base_path.read_text(encoding="utf-8")
    meta_block = render_meta_block("tarofortune")

    # 이미 패치되어 있는지 확인
    if "Search engine verification" in content:
        print(f"[SKIP] {base_path} 이미 패치됨 — 메타 블록만 갱신")
        # 기존 블록 교체
        import re
        content = re.sub(
            r"<!-- Search engine verification.*?-->\n.*?(?=\n<|\n\s*<)",
            meta_block,
            content,
            count=1,
            flags=re.DOTALL,
        )
    else:
        # <title> 다음에 삽입
        content = content.replace("</title>", f"</title>\n{meta_block}", 1)

    base_path.write_text(content, encoding="utf-8")
    print(f"[OK] {base_path} 패치 완료")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("="*72)
    print("  Search Console 사이트 인증 메타태그 설정 헬퍼")
    print("="*72)
    print()
    print("이 스크립트는 4개 검색엔진(Google·Naver·Bing·Yandex)에")
    print("3사이트(tarofortune·currency-map·geoinfomatic) 인증코드를")
    print("일괄 적용하는 가이드를 출력합니다.")
    print()

    # 입력 확인
    missing = []
    for site, codes in VERIFICATION_CODES.items():
        for engine, value in codes.items():
            if not value:
                missing.append(f"{site}/{engine}")

    if missing:
        print(f"⚠️ 미입력 인증코드: {len(missing)}개")
        print("   → 각 콘솔 가입 후 메타태그 값을 VERIFICATION_CODES에 추가하세요:")
        for m in missing[:8]:
            print(f"   - {m}")
        if len(missing) > 8:
            print(f"   ... 외 {len(missing) - 8}개")
        print()

    # 사이트별 가이드 출력
    for site in VERIFICATION_CODES:
        print_patch_guide(site)

    # 자동 패치 시도 (tarofortune만)
    print(f"\n{'='*72}")
    print("  자동 패치 시도: tarofortune")
    print(f"{'='*72}")
    auto_patch_tarofortune()

    print(f"\n{'='*72}")
    print("  다음 단계")
    print(f"{'='*72}")
    print("  1. 각 콘솔(GSC·Naver·Bing·Yandex)에서 사이트 등록")
    print("  2. 발급 받은 메타태그 값을 본 파일 VERIFICATION_CODES에 입력")
    print("  3. 다시 실행 → 자동 적용")
    print("  4. 배포 후 각 콘솔에서 '확인' 클릭")


if __name__ == "__main__":
    main()
