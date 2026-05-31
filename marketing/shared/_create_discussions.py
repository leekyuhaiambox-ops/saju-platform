"""awesome-saju repo에 Q&A Discussions 자동 양산 — 영구 백링크 + SEO."""
import os, json, urllib.request, time

TOKEN = os.environ['GH_TOKEN']
REPO_ID = "R_kgDOSszBQw"
QA = "DIC_kwDOSszBQ84C-Mo3"
SHOWANDTELL = "DIC_kwDOSszBQ84C-Mo5"
GENERAL = "DIC_kwDOSszBQ84C-Mo2"


def gql(query, variables=None):
    body = {"query": query, "variables": variables or {}}
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Claude",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def create_discussion(title, body, category_id):
    mutation = """
    mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repoId, categoryId: $catId, title: $title, body: $body}) {
        discussion { id url number }
      }
    }
    """
    return gql(mutation, {
        "repoId": REPO_ID, "catId": category_id,
        "title": title, "body": body,
    })


DISCUSSIONS = [
    (QA, "How do I find my Korean Day Pillar (일주) for free?",
     "The Day Pillar is the heavenly stem + earthly branch of your birth day. 60 valid combinations in the sexagenary cycle.\n\n**Free calculator** (no signup): https://tarofortune.pythonanywhere.com/en\n\nKorean: https://tarofortune.pythonanywhere.com\n\nUses Meeus astronomical algorithms so solar-term boundaries are correct.\n\nLook up your Day Pillar #1~#60 at https://tarofortune.pythonanywhere.com/en/sixty-pillars\n\nSee also: [60 Day Pillars reference](https://github.com/leekyuhaiambox-ops/awesome-saju/blob/main/docs/60-day-pillars-reference.md)"),

    (QA, "What's the difference between BaZi and Saju?",
     "Same system, different names.\n\n- **BaZi (八字)** — Chinese name, literally 'eight characters'\n- **Saju (사주)** — Korean name, literally 'four pillars'\n\nSame underlying calculation: year/month/day/hour pillars × heavenly stem + earthly branch.\n\nKorean tradition emphasizes Day Pillar archetype more. Both use the same 60-cycle.\n\nFree EN+KR calculator: https://tarofortune.pythonanywhere.com\n\nWiki: https://en.wikipedia.org/wiki/Bazi"),

    (QA, "Saju vs MBTI — which is more accurate for personality?",
     "Different bases, both useful.\n\n| Aspect | MBTI | Saju Day Pillar |\n|---|---|---|\n| Types | 16 | 60 |\n| Foundation | Self-report | Birth date+time math |\n| Change over time | Can change | Permanent |\n\nMBTI = current preferences. Saju = lifelong temperament. Best used together.\n\nFree saju: https://tarofortune.pythonanywhere.com\n\nGuide: https://tarofortune.pythonanywhere.com/guide/saju-vs-mbti\nCheatsheet: https://github.com/leekyuhaiambox-ops/awesome-saju/blob/main/docs/saju-vs-mbti-comparison.md"),

    (QA, "Why are there only 60 day pillars instead of 120?",
     "10 heavenly stems × 12 earthly branches = 120 possible combinations.\n\nBut only **60 are valid** because stem and branch must share yin-yang polarity.\n\n- 5 yang stems × 6 yang branches = 30\n- 5 yin stems × 6 yin branches = 30\n- Total: **60**\n\nThis is the **sexagenary cycle** (六十甲子). Used in East Asian calendars 2000+ years.\n\nEach day rotates one position. 60 days = one cycle.\n\nFree calculator: https://tarofortune.pythonanywhere.com\nReference: https://github.com/leekyuhaiambox-ops/awesome-saju/blob/main/docs/60-day-pillars-reference.md"),

    (QA, "What are the Ten Gods (십신) in Korean saju?",
     "10 relational roles that other chart elements play toward your **day master**.\n\nDefined by: (1) element relation, (2) polarity match.\n\n- 비견 (peer)\n- 겁재 (rival)\n- 식신 (calm creative)\n- 상관 (bold expression)\n- 정재 (stable wealth)\n- 편재 (flexible wealth)\n- 정관 (formal authority)\n- 편관 (transformative pressure)\n- 정인 (mother, formal learning)\n- 편인 (niche knowledge)\n\nFull EN explanation: https://github.com/leekyuhaiambox-ops/awesome-saju/blob/main/docs/saju-ten-gods-explained.md\nFree reading with ten gods: https://tarofortune.pythonanywhere.com"),

    (QA, "How accurate is a free online saju calculator?",
     "**Calculation**: 100% accurate (it's astronomical math).\n\n**Interpretation**: free tools give standard textbook readings. Personal nuance requires a human master.\n\nWorkflow:\n1. Get math right with free tool: https://tarofortune.pythonanywhere.com\n2. Read standard interpretation\n3. (Optional) consult human for nuance\n\nMost free calcs use day-of-month boundaries which is **wrong** ~12 times/year (solar-term boundaries shift mid-month). Correct ones use Meeus astronomical algorithms.\n\nThe linked tool uses correct Meeus algorithms."),

    (SHOWANDTELL, "Built a free saju calculator on PythonAnywhere free tier",
     "Sharing a side project: https://tarofortune.pythonanywhere.com\n\nStack:\n- Flask + Pillow for dynamic OG cards\n- Meeus astronomical algorithms\n- No database — pure computation\n- Korean + English interpretations\n\nFeatures: 60 day-pillars, five elements, ten gods, twelve life stages, daily luck, compatibility.\n\nOpen to feedback. Repo: https://github.com/leekyuhaiambox-ops/saju-platform\n\nThis curated list: https://github.com/leekyuhaiambox-ops/awesome-saju"),

    (SHOWANDTELL, "Created an Awesome Saju curated list",
     "Just published https://github.com/leekyuhaiambox-ops/awesome-saju — curated list of free saju resources.\n\nSections:\n- Free calculators (EN+KR)\n- 60 day-pillar references\n- Daily luck (일진)\n- Theory (ten gods, twelve life stages, five elements)\n- Compatibility\n- Beginner guides\n\nPRs welcome."),

    (GENERAL, "What sections would you want added to this list?",
     "Currently focused on free calculators, day-pillar references, and theory.\n\nConsidering adding:\n- Compatibility tools (궁합)\n- Daily luck tools\n- Books on saju in English\n- Online communities\n- Mobile apps\n\nWhat would be most useful? Reply or PR directly.\n\nList: https://github.com/leekyuhaiambox-ops/awesome-saju"),

    (GENERAL, "Resources for learning saju in English?",
     "English-language saju resources are limited. Some I found:\n\n- [Saju Fortune (English)](https://tarofortune.pythonanywhere.com/en) — Free calculator with EN interpretations\n- [What is a Day Pillar?](https://tarofortune.pythonanywhere.com/guide/what-is-day-pillar)\n- [Saju for Beginners](https://tarofortune.pythonanywhere.com/guide/saju-for-beginners)\n- [Wikipedia: BaZi](https://en.wikipedia.org/wiki/Bazi)\n\nReply or PR to add more."),
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
    for u in created:
        print(f"  {u}")


if __name__ == "__main__":
    main()
