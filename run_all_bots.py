"""모든 채널 봇 + 색인 작업을 한 번에 실행 — 매일 1회 호출 용도.

Windows 작업 스케줄러 또는 cron에서 매일 1회 호출.
환경변수에서 각 채널 자격증명을 읽어 작동.
"""
import os
import sys
import traceback
from datetime import datetime

# .env 파일 로딩 (있으면)
env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_file):
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def run_safely(label: str, fn):
    print(f"\n=== {label} ===")
    try:
        fn()
    except Exception as e:
        print(f"[{label}] ERROR: {e}")
        traceback.print_exc()


def main():
    print(f"=== run_all_bots @ {datetime.now().isoformat()} ===")

    # 1. IndexNow 색인 제출
    run_safely("IndexNow", lambda: __import__("auto_index").main())

    # 2. Lemmy
    if os.environ.get("LEMMY_USERNAME") and os.environ.get("LEMMY_PASSWORD"):
        run_safely("Lemmy", lambda: __import__("lemmy_bot").run_daily())

    # 3. Mastodon
    if os.environ.get("MASTODON_ACCESS_TOKEN"):
        run_safely("Mastodon", lambda: __import__("mastodon_bot").run_daily())

    # 4. Dev.to
    if os.environ.get("DEVTO_API_KEY"):
        run_safely("Dev.to", lambda: __import__("devto_bot").run_daily())

    # 5. Hashnode
    if os.environ.get("HASHNODE_TOKEN"):
        run_safely("Hashnode", lambda: __import__("hashnode_bot").run_daily())

    # 6. Tistory
    if os.environ.get("TISTORY_ACCESS_TOKEN") and os.environ.get("TISTORY_BLOG_NAME"):
        run_safely("Tistory", lambda: __import__("tistory_bot").run_daily())

    # 7. Bluesky (AT Protocol, 봇 공식 허용)
    if os.environ.get("BLUESKY_HANDLE") and os.environ.get("BLUESKY_APP_PASSWORD"):
        run_safely("Bluesky", lambda: __import__("bluesky_bot").run_daily())

    # 8. 텔레그램 채널
    if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHANNEL"):
        run_safely("Telegram", lambda: __import__("telegram_bot").run_daily())

    # 9. Pinterest (에버그린 시각 트래픽)
    if os.environ.get("PINTEREST_ACCESS_TOKEN") and os.environ.get("PINTEREST_BOARD_ID"):
        run_safely("Pinterest", lambda: __import__("pinterest_bot").run_daily())

    # 10. Reddit (계정 숙성 후)
    if os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_USERNAME"):
        run_safely("Reddit", lambda: __import__("reddit_bot").run_daily())

    print("\n=== done ===")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
