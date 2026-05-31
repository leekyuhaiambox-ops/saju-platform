"""실패한 PR 진단 + section 키워드 정확히 찾기."""
import os, json, base64, re, urllib.request

TOKEN = os.environ['GH_TOKEN']
H = {'Authorization': f'Bearer {TOKEN}', 'User-Agent': 'Claude', 'Accept': 'application/vnd.github+json'}

def gh(path):
    req = urllib.request.Request(f'https://api.github.com{path}', headers=H)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# 1. johackim/awesome-indiehackers — fork 상태 확인
print("=== johackim/awesome-indiehackers fork 상태 ===")
try:
    fork = gh('/repos/leekyuhaiambox-ops/awesome-indiehackers')
    print(f"  fork default_branch: {fork['default_branch']}")
    print(f"  parent default_branch: {fork['parent']['default_branch']}")
    # 우리 fork에 commit 있나?
    commits = gh('/repos/leekyuhaiambox-ops/awesome-indiehackers/commits?per_page=2')
    for c in commits[:2]:
        print(f"  recent: {c['sha'][:7]} {c['commit']['author']['date']} — {c['commit']['message'][:60]}")
except Exception as e:
    print(f"  ERR: {e}")

print()

# 2. xcomptek README 진짜 sections
print("=== xcomptek/awesome-saas-boilerplates README sections ===")
try:
    data = gh('/repos/xcomptek/awesome-saas-boilerplates/contents/README.md')
    content = base64.b64decode(data['content']).decode('utf-8', errors='replace')
    print(f"  README length: {len(content)}")
    for i, line in enumerate(content.split('\n')[:200]):
        if re.match(r'^##+\s', line):
            print(f"    L{i+1}: {line.strip()}")
except Exception as e:
    print(f"  ERR: {e}")
