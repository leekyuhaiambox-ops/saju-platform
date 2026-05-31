"""saju-platform repo에 dev·tech 주제 Discussions 자동 생성."""
import os, json, urllib.request, time

TOKEN = os.environ['GH_TOKEN']
REPO_ID = "R_kgDOSfMJKQ"
QA = "DIC_kwDOSfMJKc4C-Mo9"
SHOWANDTELL = "DIC_kwDOSfMJKc4C-Mo_"
GENERAL = "DIC_kwDOSfMJKc4C-Mo8"


def create_discussion(title, body, cat_id):
    mutation = """
    mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repoId, categoryId: $catId, title: $title, body: $body}) {
        discussion { id url number }
      }
    }
    """
    body_json = {"query": mutation, "variables": {
        "repoId": REPO_ID, "catId": cat_id, "title": title, "body": body,
    }}
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(body_json).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json", "User-Agent": "Claude"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


DISCUSSIONS = [
    (QA, "Why does the saju calculator use Meeus astronomical algorithms?",
     "Solar-term boundaries shift the **month pillar** mid-month, not on the 1st. A naive day-of-month boundary calculator gets the month pillar wrong about 12 times per year.\n\nMeeus algorithms compute the exact astronomical moment of each solar term (24 per year), giving the correct month pillar always.\n\nThe live site uses Meeus: https://tarofortune.pythonanywhere.com\n\nBackground: [Solar terms on Wikipedia](https://en.wikipedia.org/wiki/Solar_term)\n\nMore: [Awesome Saju](https://github.com/leekyuhaiambox-ops/awesome-saju)"),

    (QA, "How do I run the multi-site bot orchestrator locally?",
     "```bash\ncd marketing/shared\npython multi_site_orchestrator.py --dry-run\n```\n\nRequires environment variables:\n- `MASTODON_ACCESS_TOKEN`\n- `LEMMY_USERNAME` + `LEMMY_PASSWORD`\n- `DEVTO_API_KEY` (optional)\n\nFull docs: https://github.com/leekyuhaiambox-ops/saju-platform/blob/main/marketing/MASTER_HANDOFF.md\n\nGitHub Actions runs it daily at UTC 16:00."),

    (QA, "What's the cost breakdown for running this whole stack?",
     "Roughly:\n\n| Service | Monthly cost |\n|---|---|\n| PythonAnywhere free tier | ₩0 |\n| Firebase Hosting | ₩0 (within free quota) |\n| GitHub Actions | ₩0 (within 2000 min/month) |\n| OpenAI gpt-4o-mini (content gen, 6/day) | ~₩440 |\n| Brevo email (optional) | ₩0 (free tier 300/day) |\n| Total | **~₩440/month** |\n\nIf you skip OpenAI auto-content: **₩0/month total**.\n\nMain repo: https://github.com/leekyuhaiambox-ops/saju-platform"),

    (SHOWANDTELL, "Multi-site bot orchestrator: one Python script, 3 live sites",
     "Sharing the marketing orchestration script that rotates posts across 3 production sites:\n\n- https://tarofortune.pythonanywhere.com (Korean saju astrology)\n- https://gyeonggi-currency-map.web.app (currency merchant map)\n- https://geoinfomatic.pythonanywhere.com (neighborhood accessibility)\n\nSource: [multi_site_orchestrator.py](https://github.com/leekyuhaiambox-ops/saju-platform/blob/main/marketing/shared/multi_site_orchestrator.py)\n\nFeatures:\n- Site rotation by epoch_day mod 3\n- Per-site content pools (JSON)\n- Channel adapters: Mastodon · Lemmy · Dev.to · IndexNow\n- Daily cron via GitHub Actions\n- Auto-commit state files\n\nOpen to feedback and PRs."),

    (SHOWANDTELL, "Daily KPI collector for 3 sites + multi-channel bots",
     "Open-sourced the analytics collector: [analytics_collector.py](https://github.com/leekyuhaiambox-ops/saju-platform/blob/main/marketing/shared/analytics_collector.py)\n\nCollects daily KPIs from:\n- PythonAnywhere access.log (real human vs bot classification)\n- Mastodon API (favs, boosts, replies)\n- Lemmy API (post scores, comments)\n- Dev.to API (article reactions)\n- GitHub Actions API (workflow run history)\n\nOutputs JSON to `marketing/shared/state/daily_kpi/YYYY-MM-DD.json` for trend tracking."),

    (GENERAL, "Roadmap: what to add next?",
     "Current state of the marketing infrastructure:\n\n✅ Multi-site bot (Mastodon · Lemmy · Dev.to · IndexNow) — daily auto\n✅ Auto content gen (OpenAI gpt-4o-mini) — daily 6 posts\n✅ KPI collector — daily auto\n✅ Sitemap with 1,116 URLs — Bing/Yandex/api.indexnow submitted\n✅ 8-channel viral share buttons on result pages\n✅ awesome-saju curated list (영구 백링크)\n✅ 11 awesome-list PRs (61K+ stars 노출 잠재력)\n\n다음 후보:\n- Bluesky integration\n- Telegram channel\n- WikiData entity edit\n- More language translations (Japanese, Chinese)\n\nIdeas welcome."),
]


def main():
    created = []
    for cat_id, title, body in DISCUSSIONS:
        try:
            result = create_discussion(title, body, cat_id)
            if "errors" in result:
                print(f"  E {title[:50]} - {result['errors'][0].get('message', '?')[:80]}")
            else:
                d = result["data"]["createDiscussion"]["discussion"]
                print(f"  OK #{d['number']} {title[:60]}")
                created.append(d["url"])
        except Exception as e:
            print(f"  X {title[:50]} - {e}")
        time.sleep(1.5)
    print(f"\nCreated: {len(created)} / {len(DISCUSSIONS)}")
    for u in created: print(f"  {u}")


if __name__ == "__main__":
    main()
