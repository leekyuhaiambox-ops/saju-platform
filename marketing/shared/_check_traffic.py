"""실제 PA access log 파싱해서 봇 vs 사람 트래픽 분석."""
import urllib.request, re, sys
from collections import Counter

TOKEN = '15f08580dcd72d36519893c8e512f0a827bc1962'
BASE = 'https://www.pythonanywhere.com/api/v0/user/tarofortune'

UA_BOT_KEYS = ['bot', 'crawl', 'spider', 'curl', 'wget', 'python', 'scrap',
               'yeti', 'daumoa', 'fetch', 'semrush', 'ahrefs', 'mj12', 'monitor']

LOG_PATTERN = re.compile(
    r'^(\S+) - \S+ \[([^\]]+)\] "\S+ (\S+) [^"]+" (\d+) \d+ "([^"]*)" "([^"]+)"'
)

def parse(path, label):
    url = f'{BASE}/files/path/var/log/tarofortune.pythonanywhere.com.{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'Token {TOKEN}'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'{path}: {e}')
        return 0, 0, Counter(), Counter()
    lines = body.splitlines()
    print(f'\n=== {label}: {path} ({len(lines)} lines, {len(body)//1024}KB) ===')
    bot = 0; human = 0
    bots = Counter(); paths = Counter(); referers = Counter(); humans_dates = Counter()
    for line in lines:
        m = LOG_PATTERN.match(line)
        if not m:
            continue
        ip, dt, p, status, ref, ua = m.groups()
        paths[p[:60]] += 1
        ua_l = ua.lower()
        if any(b in ua_l for b in UA_BOT_KEYS):
            bot += 1
            for b in ['googlebot', 'bingbot', 'yandex', 'yeti', 'naverbot', 'daumoa',
                      'duckduckbot', 'applebot', 'petalbot', 'semrush', 'ahrefs',
                      'mj12', 'gptbot', 'claudebot', 'bytespider', 'amazonbot',
                      'facebookexternalhit', 'pingdom', 'uptimerobot']:
                if b in ua_l:
                    bots[b] += 1
                    break
            else:
                bots['other-bot'] += 1
        else:
            human += 1
            humans_dates[dt[:11]] += 1
            if ref and ref != '-' and 'tarofortune' not in ref:
                referers[ref[:80]] += 1
    print(f'  봇: {bot}, 사람: {human}')
    print(f'  봇 종류 top 8:')
    for k, v in bots.most_common(8):
        print(f'    {k}: {v}')
    if humans_dates:
        print(f'  사람 일자별 (최근 7):')
        for k, v in sorted(humans_dates.items())[-7:]:
            print(f'    {k}: {v}')
    if referers:
        print(f'  사람 referer (외부 유입):')
        for k, v in referers.most_common(8):
            print(f'    {k}: {v}')
    print(f'  인기 path top 6:')
    for k, v in paths.most_common(6):
        print(f'    {k}: {v}')
    return bot, human, bots, referers


if __name__ == '__main__':
    total_b = 0; total_h = 0
    for p, l in [('access.log', '오늘'), ('access.log.1', '어제')]:
        b, h, _, _ = parse(p, l)
        total_b += b; total_h += h
    print(f'\n========== 합계 (2일) ==========')
    print(f'  봇:  {total_b}')
    print(f'  사람: {total_h}')
