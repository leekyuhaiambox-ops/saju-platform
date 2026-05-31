"""5/29 PA access.log 정확한 분석 + 사람 신호 강도 검증."""
import re
import urllib.request
from collections import Counter, defaultdict

TOKEN = '15f08580dcd72d36519893c8e512f0a827bc1962'
BASE = 'https://www.pythonanywhere.com/api/v0/user/tarofortune'

BOT_KEYS = ['bot', 'crawl', 'spider', 'fetch', 'curl', 'wget', 'python', 'scrap',
            'yeti', 'daumoa', 'monitor', 'pingdom', 'uptimerobot', 'semrush',
            'ahrefs', 'mj12', 'archive.org_bot', 'amazonbot']

LINE = re.compile(
    r'^(\S+) - \S+ \[([^\]]+)\] "(\S+) (\S+) [^"]+" (\d+) (\d+) "([^"]*)" "([^"]+)"'
)


def fetch_log(path):
    url = f'{BASE}/files/path/var/log/tarofortune.pythonanywhere.com.{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'Token {TOKEN}'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', errors='replace')


def analyze(body, label):
    print(f"\n{'='*70}")
    print(f"  {label}  —  {len(body.splitlines())} 라인")
    print('='*70)

    by_date = defaultdict(lambda: {
        'bot': 0, 'human': 0, 'humans_set': set(), 'human_ips': set(),
        'human_uas': Counter(), 'human_refs': Counter(), 'human_paths': Counter(),
        'human_hours': Counter(),
    })

    for line in body.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        ip, dt, method, path, status, size, ref, ua = m.groups()
        # date 추출: 27/May/2026:13:45:01 +0000
        date_part = dt[:11]
        hour = dt[12:14] if len(dt) > 14 else '?'

        ua_l = ua.lower()
        is_bot = any(b in ua_l for b in BOT_KEYS)

        d = by_date[date_part]
        if is_bot:
            d['bot'] += 1
        else:
            d['human'] += 1
            d['human_ips'].add(ip)
            # UA를 간단하게 (브라우저 + OS만)
            ua_brief = ua[:80]
            d['human_uas'][ua_brief] += 1
            d['human_hours'][hour] += 1
            if path != '/' and not path.startswith('/static/') and not path.endswith('.png') and not path.endswith('.css') and not path.endswith('.js'):
                d['human_paths'][path[:50]] += 1
            if ref and ref != '-' and 'tarofortune' not in ref:
                d['human_refs'][ref[:80]] += 1

    for date in sorted(by_date.keys()):
        d = by_date[date]
        print(f"\n  📅 {date}")
        print(f"    bot 분류: {d['bot']}  /  human 분류: {d['human']}  /  unique IP: {len(d['human_ips'])}")
        if d['human_refs']:
            print(f"    외부 검색 유입 (진짜 사람 강한 증거):")
            for ref, cnt in d['human_refs'].most_common(8):
                print(f"      [{cnt}] {ref}")
        if d['human_uas']:
            print(f"    human UA top 5 (실제 브라우저인지 확인):")
            for ua, cnt in d['human_uas'].most_common(5):
                print(f"      [{cnt}] {ua}")
        if d['human_hours']:
            print(f"    시간대 분포: ", end="")
            for h in sorted(d['human_hours'].keys()):
                print(f"{h}:{d['human_hours'][h]} ", end="")
            print()


if __name__ == '__main__':
    for path, label in [
        ('access.log', 'TODAY (UTC)'),
        ('access.log.1', 'YESTERDAY (UTC)'),
    ]:
        try:
            body = fetch_log(path)
            analyze(body, label)
        except Exception as e:
            print(f"{label}: {e}")
