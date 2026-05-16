"""Tistory 자동 게시 봇 — 카카오 OpenAPI 기반.

Tistory API:
- 카카오 디벨로퍼스에서 OAuth 앱 등록 → APP_KEY 발급
- OAuth 인증 → access_token 획득 (1회만)
- POST https://www.tistory.com/apis/post/write 로 글 게시

환경변수:
- TISTORY_ACCESS_TOKEN
- TISTORY_BLOG_NAME (예: "issuemoamoa")
- SITE_URL
"""
from __future__ import annotations
import os
import json
import random
from datetime import date
from pathlib import Path
from urllib import request, parse

TOKEN = os.environ.get("TISTORY_ACCESS_TOKEN", "")
BLOG_NAME = os.environ.get("TISTORY_BLOG_NAME", "")
SITE_URL = os.environ.get("SITE_URL", "https://tarofortune.pythonanywhere.com")

STATE_FILE = Path(os.environ.get(
    "TISTORY_STATE_FILE",
    os.path.join(os.path.dirname(__file__), ".tistory_state.json"),
))


# 한국어 사주 콘텐츠 — Tistory는 한국 검색 최적화
POSTS = [
    {
        "title": "내 사주 일주 5분 만에 정확히 보는 법 — 무료 사주 풀이 가이드",
        "tag": "사주,일주,사주풀이,무료사주,60갑자,명리학,입춘,야자시",
        "content": """<p>‘내 사주가 뭐지?’ 한번쯤 검색해 본 적 있다면, 결과가 사이트마다 다른 경험 하셨을 겁니다. 어떤 곳은 갑자년, 다른 곳은 계해년. 왜 그런지 이 글에서 정리합니다.</p>

<h2>1. 사주의 한 해는 1월 1일이 아니라 ‘입춘’부터</h2>
<p>사주의 연주(年柱) 경계는 양력으로 매년 2월 4일경의 <strong>입춘(立春)</strong>입니다. 정확히는 태양 황경 315°를 지나는 순간으로, 분 단위로 매년 다릅니다. 2024년의 경우 2월 4일 17시 11분(KST).</p>
<p>1월 30일 출생자와 2월 5일 출생자는 같은 ‘2024년 출생’이지만 사주 연주는 다릅니다. 전자는 2023년 계묘년, 후자는 2024년 갑진년.</p>

<h2>2. 야자시 — 23시 이후 출생자의 일주 보정</h2>
<p>사주에서 하루의 경계는 자정이 아니라 자시(子時)의 시작인 23시입니다. 23시 이후 출생자는 그날이 아니라 ‘다음날의 일주’를 사용해야 합니다(야자시 규칙).</p>

<h2>3. 진태양시 — 지역별 경도 보정</h2>
<p>한국 표준시는 일본 중부 자오선 기준입니다. 실제 한국 진태양시는 표준시보다 약 30분 늦습니다.</p>

<h2>4. 무료지만 정밀한 사주</h2>
<p>위 3가지를 모두 적용하는 무료 사주: <a href="{site}">사주명리 — 운명의 설계도</a></p>
<p>회원가입 없이, 이메일 입력 없이, 양력 생년월일시만으로 정확한 사기둥과 60갑자 일주별 풀이까지 즉시 산출됩니다.</p>

<h2>마무리</h2>
<p>사주는 운명을 결정하는 답안이 아닙니다. 자기 자신을 동양철학의 언어로 이해하는 도구입니다. 정확한 계산 위에서 본 사주가 어떤 메시지를 주는지 직접 확인해 보시기 바랍니다.</p>""",
    },
    {
        "title": "60갑자 일주별 풀이 완전 정리 — 본인 일주 본질 찾기",
        "tag": "60갑자,일주,사주,일주풀이,갑자일주,을축일주",
        "content": """<p>사주에서 ‘일주(日柱)’는 태어난 날의 두 글자로, 본인의 본질적 기질을 가장 강하게 드러냅니다. 60갑자는 천간 10 × 지지 12의 최소공배수인 60가지 조합으로, 각 조합이 고유한 archetype을 이룹니다.</p>

<h2>오행별 그룹</h2>
<ul>
  <li><strong>목(木) 일간</strong> — 갑·을. 성장과 의(義)의 인재.</li>
  <li><strong>화(火) 일간</strong> — 병·정. 표현과 예(禮)의 인재.</li>
  <li><strong>토(土) 일간</strong> — 무·기. 신뢰와 신(信)의 인재.</li>
  <li><strong>금(金) 일간</strong> — 경·신. 결단과 의(義)의 인재.</li>
  <li><strong>수(水) 일간</strong> — 임·계. 지혜와 지(智)의 인재.</li>
</ul>

<h2>대표 일주 5개</h2>
<p><strong>갑자(甲子)</strong> — 큰 나무가 깊은 우물물을 만난 격. 지성과 인내의 학자형.</p>
<p><strong>병오(丙午)</strong> — 한낮의 태양이 정점에 선 격. 카리스마의 정수.</p>
<p><strong>무진(戊辰)</strong> — 넓은 옥토에 단단한 광물. 신뢰의 리더형.</p>
<p><strong>임진(壬辰)</strong> — 용이 바다에서 승천하는 격. 큰 그릇의 인재.</p>
<p><strong>계해(癸亥)</strong> — 큰 바다의 빗방울. 깊은 지혜의 학자형.</p>

<h2>본인 일주 확인</h2>
<p>본인 일주가 60개 중 어떤 것인지 확인하려면 <a href="{site}">무료 사주 풀이</a>를 이용하세요. 60갑자 전체 풀이도 함께 제공됩니다.</p>""",
    },
    {
        "title": "사주 십신(十神) 완전 정리 — 일간 중심의 열 가지 관계",
        "tag": "십신,사주,비견,정인,정관,편관,식신,재성",
        "content": """<p>사주의 십신(十神)은 일간(나)을 기준으로 다른 일곱 글자가 어떤 오행 관계인지에 따라 부여되는 열 가지 이름입니다. 사주 해석의 핵심 개념입니다.</p>

<h2>오행 관계 5쌍</h2>
<p><strong>나와 같은 오행</strong> — 비견(같은 음양)·겁재(다른 음양). 자아와 동료, 경쟁자.</p>
<p><strong>내가 생하는 오행</strong> — 식신(같은 음양)·상관(다른 음양). 표현·재능·자식.</p>
<p><strong>내가 극하는 오행</strong> — 편재(같은 음양)·정재(다른 음양). 재물·배우자(남).</p>
<p><strong>나를 극하는 오행</strong> — 편관(같은 음양)·정관(다른 음양). 명예·권위·배우자(여).</p>
<p><strong>나를 생하는 오행</strong> — 편인(같은 음양)·정인(다른 음양). 인덕·학문·어머니.</p>

<h2>각 십신의 진로 의미</h2>
<ul>
  <li>식신 강함 → 안정 풍요, 창작</li>
  <li>상관 강함 → 자기 능력 인정 받는 직업</li>
  <li>편재 강함 → 사업·투자</li>
  <li>정관 강함 → 조직·공무원</li>
  <li>편인 강함 → 종교·연구·예술</li>
</ul>

<h2>본인 십신 확인</h2>
<p><a href="{site}">무료 사주 풀이</a>에서 본인 사주의 십신 분포를 그래프로 한눈에 볼 수 있습니다.</p>""",
    },
    {
        "title": "사주 궁합 진짜 보는 법 — 네 가지 핵심 변수",
        "tag": "사주궁합,궁합,연애,결혼,사주",
        "content": """<p>‘너랑 나 사주 궁합 보러 갈래?’ 사람들이 흔히 보는 사주 궁합. 실제로 명리학에서 궁합을 본다는 건 두 사람의 사주가 어떻게 상호작용하는지를 네 가지 변수로 분석하는 것입니다.</p>

<h2>1. 일간 천간합</h2>
<p>두 사람 일간의 천간이 천간합 5조 중 하나를 이루면 자연스러운 끌림이 발생합니다. 갑기·을경·병신·정임·무계 — 이 5쌍이 천간합입니다.</p>

<h2>2. 일간 오행 상생/상극</h2>
<p>한쪽 일간이 다른 쪽을 생(生)하면 ‘서로 살리는 관계’, 극(剋)하면 ‘긴장과 갈등의 관계’입니다.</p>

<h2>3. 일지 합·충</h2>
<p>두 사람 일지(태어난 날의 지지)가 육합 관계면 일상이 편안하고, 충 관계면 생활 리듬이 어긋납니다.</p>

<h2>4. 연지 관계 (띠 궁합)</h2>
<p>흔히 ‘띠 궁합’이라 부르는 것이 이것. 사회적 외부 관계의 결을 봅니다. 가장 가중치가 낮은 변수입니다.</p>

<h2>점수 계산</h2>
<p>위 네 가지를 종합해 20~95점으로 점수화합니다. 85점 이상은 최상, 45점 이하는 노력 필요.</p>

<p><a href="{site}/compatibility">무료 사주 궁합 분석</a>에서 두 사람 생년월일만 입력하면 즉시 점수와 분석을 받아볼 수 있습니다.</p>""",
    },
    {
        "title": "음력 생일을 양력으로 변환하는 법 — 사주 풀이 전 필수",
        "tag": "음력,양력,음력변환,사주,생일",
        "content": """<p>사주를 보려면 양력 생년월일이 필요합니다. 음력으로만 생일을 알고 계신 분들을 위한 가이드입니다.</p>

<h2>왜 양력인가?</h2>
<p>사주의 시간 체계는 ‘태양 황경 기반 24절기’가 표준입니다. 음력은 달의 위상 기반이라 사주 계산에 직접 쓰지 않습니다. 음력 생일은 양력으로 변환한 뒤 사주를 봐야 합니다.</p>

<h2>변환 방법</h2>
<p><a href="{site}/lunar-converter">음력→양력 무료 변환기</a>를 이용하세요. 1900년부터 2049년까지의 한국 음력 데이터로 정확히 변환합니다. 윤달도 지원합니다.</p>

<h2>변환 예시</h2>
<ul>
  <li>음력 1990-01-01 → 양력 1990-01-27</li>
  <li>음력 2024-01-01 → 양력 2024-02-10</li>
  <li>음력 2000-05-05 (단오) → 양력 2000-06-06</li>
</ul>

<p>양력 날짜를 확인한 뒤 <a href="{site}">사주 풀이</a>를 받으시면 됩니다.</p>""",
    },
]


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"posted_indices": [], "last_date": None, "count": 0}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


def post_to_tistory(title: str, content: str, tag: str) -> dict:
    """Tistory Open API로 글 게시.

    https://tistory.github.io/document-tistory-apis/apis/v1/post/write.html
    """
    if not TOKEN or not BLOG_NAME:
        return {"ok": False, "error": "TISTORY_ACCESS_TOKEN or TISTORY_BLOG_NAME missing"}
    data = parse.urlencode({
        "access_token": TOKEN,
        "output": "json",
        "blogName": BLOG_NAME,
        "title": title,
        "content": content,
        "visibility": "3",   # 0=비공개, 3=공개
        "category": "0",     # 카테고리 미지정
        "tag": tag,
        "acceptComment": "1",
    }).encode("utf-8")
    req = request.Request(
        "https://www.tistory.com/apis/post/write",
        data=data, method="POST",
        headers={"User-Agent": "tarofortune-bot/0.1",
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8")
            data = json.loads(body)
            ts_resp = data.get("tistory", {})
            if ts_resp.get("status") == "200":
                return {"ok": True, "post_id": ts_resp.get("postId"),
                        "url": ts_resp.get("url")}
            return {"ok": False, "error": ts_resp.get("error_message", body)}
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try:
                b = e.read().decode()
            except Exception:
                pass
        return {"ok": False, "error": f"{e}: {b}"}


def run_daily():
    state = load_state()
    today = date.today().isoformat()
    if state.get("last_date") == today:
        print("Already posted today.")
        return

    posted = set(state.get("posted_indices", []))
    available = [i for i in range(len(POSTS)) if i not in posted]
    if not available:
        state["posted_indices"] = []
        available = list(range(len(POSTS)))

    idx = random.choice(available)
    post = POSTS[idx]
    content = post["content"].format(site=SITE_URL)
    result = post_to_tistory(post["title"], content, post["tag"])
    print(f"[tistory] idx={idx} {json.dumps(result, ensure_ascii=False)}")
    if result.get("ok"):
        state.setdefault("posted_indices", []).append(idx)
        state["last_date"] = today
        state["count"] = state.get("count", 0) + 1
        save_state(state)


if __name__ == "__main__":
    run_daily()
