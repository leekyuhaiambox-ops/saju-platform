"""
매일 daily_report를 운영자 이메일로 직접 발송.

GitHub Issue + 이메일 둘 다 발송 = 운영자가 어디서든 받음.

운영자 1번 셋업 (5분):
  1. Gmail 2단계 인증 켜기 (https://myaccount.google.com/security)
  2. App Password 발급 (https://myaccount.google.com/apppasswords)
     - 앱: "Mail", 기기: "Other (Daily Marketing Report)"
     - 16자리 비밀번호 받음
  3. GitHub Secrets에 추가 (https://github.com/leekyuhaiambox-ops/saju-platform/settings/secrets/actions):
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=geostaticss@gmail.com
     SMTP_PASS=<16자리 app password>
     REPORT_TO=geostaticss@gmail.com
     REPORT_FROM=geostaticss@gmail.com

실행:
  python send_daily_report_email.py             # 발송
  python send_daily_report_email.py --dry-run   # 미리보기

기존 daily_report.py 의 _latest.json을 본문으로 사용.
"""
from __future__ import annotations
import argparse
import json
import os
import smtplib
import ssl
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# daily_report 본문 렌더러 재사용
sys.path.insert(0, str(Path(__file__).parent))
from daily_report import render_issue_body, collect_pa_traffic_yesterday, \
    collect_mastodon, collect_lemmy, collect_devto, collect_pa_referrals, \
    collect_awesome_prs, collect_sitemap_count
import datetime as _dt


def md_to_html(md: str) -> str:
    """매우 단순한 markdown → HTML 변환 (이메일용)."""
    lines = []
    for raw in md.split("\n"):
        line = raw
        if line.startswith("# "):
            lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2 style='color:#5e2da6'>{line[3:]}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("- "):
            lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("| "):
            # 표 행
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                continue
            tag = "th" if "---" not in raw else "td"
            cells_html = "".join(f"<{tag} style='padding:6px 10px;border:1px solid #ddd'>{c}</{tag}>" for c in cells)
            lines.append(f"<tr>{cells_html}</tr>")
        elif line.startswith(">"):
            lines.append(f"<blockquote style='border-left:3px solid #5e2da6;padding-left:10px;color:#555'>{line[1:].strip()}</blockquote>")
        elif line.startswith("```"):
            continue
        elif line.strip() == "":
            lines.append("<br>")
        else:
            # bold, links
            import re
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            line = re.sub(r"\[(.+?)\]\((.+?)\)", r"<a href='\2'>\1</a>", line)
            line = re.sub(r"`([^`]+)`", r"<code style='background:#f0f0f0;padding:2px 5px;border-radius:3px'>\1</code>", line)
            lines.append(f"<p>{line}</p>")
    body = "\n".join(lines)
    # <li> 묶기
    body = body.replace("<li>", "<li style='margin:4px 0'>")
    return f"""<!DOCTYPE html><html><body style='font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:760px;margin:20px auto;padding:20px;line-height:1.7;color:#1a0f2e'>
<table style='width:100%;border-collapse:collapse;margin:14px 0'>{body}</table>
</body></html>"""


def send_email(subject: str, html: str, plain: str) -> bool:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    pw = os.environ.get("SMTP_PASS", "")
    to = os.environ.get("REPORT_TO", user)
    sender = os.environ.get("REPORT_FROM", user)

    if not (user and pw and to):
        print("⚠️ SMTP_USER, SMTP_PASS, REPORT_TO 환경변수 필요")
        print("   GitHub Secrets 또는 .env에 추가 후 다시 실행")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=30) as srv:
            srv.starttls(context=ctx)
            srv.login(user, pw)
            srv.send_message(msg)
        print(f"✅ Email sent to {to} ({len(plain)} bytes)")
        return True
    except Exception as e:
        print(f"❌ SMTP error: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # KPI 수집 (daily_report에서 import)
    print("Collecting KPI...")
    kpi = {
        "date": date.today().isoformat(),
        "collected_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "pa_traffic": collect_pa_traffic_yesterday(),
        "mastodon": collect_mastodon(),
        "lemmy": collect_lemmy(),
        "devto": collect_devto(),
        "pa_referrals": collect_pa_referrals(),
        "awesome_prs": collect_awesome_prs(),
        "sitemap_urls": collect_sitemap_count(),
    }

    plain = render_issue_body(kpi)
    html = md_to_html(plain)
    subject = f"📊 마케팅 일일 보고 — {kpi['date']}"

    if args.dry_run:
        print("=== Subject ===")
        print(subject)
        print("=== Plain (first 1000 chars) ===")
        print(plain[:1000])
        print("\n=== HTML length ===")
        print(len(html))
        return 0

    return 0 if send_email(subject, html, plain) else 1


if __name__ == "__main__":
    sys.exit(main())
