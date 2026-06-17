"""타로 78장 덱 — 메이저 22 + 마이너 56. 한국어·영어 의미 (정·역방향).

사이트 명칭이 '타로사주'인데 타로 기능이 없던 핵심 공백을 채운다.
검색량 거대("타로카드 의미", "오늘의 타로"), 한·영 양쪽, 봇 콘텐츠로도 활용.
표준 라이더-웨이트(RWS) 의미 기반.

날짜 기반 결정론적 '오늘의 카드' 추첨(daily_card) 포함 — 하루 동안 동일 → 공유 가능.
"""
from __future__ import annotations
import hashlib
from datetime import date

# ─── 메이저 아르카나 22장 ────────────────────────────────
# (slug, 번호, 한글명, 영문명, 키워드ko, 키워드en, 정방향ko, 역방향ko, 정방향en, 역방향en)
MAJOR = [
    ("fool", 0, "바보", "The Fool",
     "새로운 시작·순수·모험", "new beginnings, innocence, adventure",
     "절벽 끝에 선 바보는 두려움 없이 새로운 여정을 시작합니다. 백지 상태의 가능성, 순수한 믿음, 자유로운 모험을 뜻합니다. 계산보다 직관을 따를 때입니다.",
     "무모함, 무계획, 위험을 보지 못함. 준비 없이 뛰어들었다 낭패를 보거나, 두려워 한 발도 못 떼는 상태입니다.",
     "Poised at the cliff's edge, the Fool begins a journey without fear. Pure potential, faith, and free-spirited adventure — a time to trust intuition over calculation.",
     "Recklessness, naivety, blindness to risk. Leaping without preparation, or freezing in fear and never starting."),
    ("magician", 1, "마법사", "The Magician",
     "의지·창조·실현력", "manifestation, willpower, skill",
     "마법사는 위는 하늘, 아래는 땅을 가리키며 뜻한 바를 현실로 만듭니다. 필요한 모든 재능과 자원이 이미 손안에 있다는 신호입니다. 집중과 행동의 때.",
     "조작, 기만, 재능의 낭비. 능력을 잘못된 곳에 쓰거나, 자신감 부족으로 잠재력을 펼치지 못합니다.",
     "The Magician channels heaven and earth to make will into reality. Every talent and resource you need is already in hand. A time for focus and action.",
     "Manipulation, deception, wasted talent. Power misused, or potential blocked by self-doubt."),
    ("high-priestess", 2, "여사제", "The High Priestess",
     "직관·신비·내면의 지혜", "intuition, mystery, inner voice",
     "여사제는 베일 뒤의 비밀과 무의식의 지혜를 지킵니다. 답은 바깥이 아니라 내면에 있습니다. 조용히 귀 기울이고 직관을 신뢰하세요.",
     "비밀의 은폐, 직관 무시, 표면에 휘둘림. 내면의 목소리를 외면해 길을 잃습니다.",
     "The High Priestess guards secrets behind the veil and the wisdom of the unconscious. The answer lies within, not without. Listen quietly and trust intuition.",
     "Hidden agendas, ignored intuition, surface distractions. Losing your way by silencing the inner voice."),
    ("empress", 3, "여황제", "The Empress",
     "풍요·모성·창조성", "abundance, nurturing, fertility",
     "여황제는 풍요와 생명력, 보살핌의 상징입니다. 사랑·창작·결실이 무르익는 시기. 자신과 주변을 따뜻하게 돌보고 감각을 즐기세요.",
     "과보호·의존·창조성 정체. 자기 돌봄을 잃거나 풍요가 막혀 공허해집니다.",
     "The Empress embodies abundance, vitality, and care. Love, creativity, and fruition ripen now. Nurture yourself and others, and enjoy the senses.",
     "Smothering, dependency, creative block. Neglected self-care or stalled abundance leaving you empty."),
    ("emperor", 4, "황제", "The Emperor",
     "권위·안정·질서", "authority, structure, control",
     "황제는 질서·규율·든든한 토대를 세웁니다. 리더십과 책임으로 상황을 장악할 때. 명확한 규칙과 구조가 성공을 만듭니다.",
     "독재·경직·통제 상실. 고집과 권위주의로 반발을 사거나, 책임을 회피합니다.",
     "The Emperor builds order, discipline, and solid foundations. A time to take charge through leadership and responsibility. Clear structure breeds success.",
     "Tyranny, rigidity, loss of control. Stubborn authoritarianism breeding resistance, or shirking responsibility."),
    ("hierophant", 5, "교황", "The Hierophant",
     "전통·가르침·신념", "tradition, guidance, belief",
     "교황은 전통·교육·정신적 가르침을 상징합니다. 멘토나 제도, 검증된 방식에서 답을 찾을 때. 공동체의 가치와 배움을 존중하세요.",
     "독단·맹신·관습의 굴레. 틀에 갇히거나 반대로 모든 규범을 거부합니다.",
     "The Hierophant represents tradition, education, and spiritual teaching. Seek answers in a mentor, institution, or proven path. Honor shared values and learning.",
     "Dogma, blind faith, the cage of convention. Trapped in rules, or rejecting all norms outright."),
    ("lovers", 6, "연인", "The Lovers",
     "사랑·선택·조화", "love, choice, union",
     "연인 카드는 깊은 결합과 중요한 선택을 뜻합니다. 가치관이 맞는 관계, 진심에서 비롯된 결정. 사랑과 조화가 무르익습니다.",
     "불화·갈등·잘못된 선택. 가치관 충돌이나 유혹으로 관계가 흔들립니다.",
     "The Lovers signify deep union and a meaningful choice. A values-aligned relationship, a decision from the heart. Love and harmony ripen.",
     "Discord, conflict, poor choices. Clashing values or temptation shaking a relationship."),
    ("chariot", 7, "전차", "The Chariot",
     "의지·승리·전진", "willpower, victory, drive",
     "전차는 상반된 힘을 통제해 앞으로 나아가는 의지와 승리를 뜻합니다. 결단력과 자제력으로 목표를 향해 돌진할 때.",
     "통제 상실·방향 상실·좌절. 충동에 휘둘리거나 추진력을 잃고 멈춥니다.",
     "The Chariot is willpower and victory — mastering opposing forces to surge forward. A time to charge toward your goal with resolve and self-control.",
     "Loss of control, lost direction, frustration. Driven by impulse, or stalled and out of momentum."),
    ("strength", 8, "힘", "Strength",
     "용기·인내·내면의 힘", "courage, patience, inner strength",
     "힘 카드는 완력이 아닌 부드러운 용기로 사자를 다스립니다. 인내·연민·자기 통제로 어려움을 이겨냅니다. 진정한 힘은 내면에서 나옵니다.",
     "자기 의심·나약함·감정 폭주. 두려움에 굴복하거나 분노를 다스리지 못합니다.",
     "Strength tames the lion not by force but gentle courage. Patience, compassion, and self-mastery overcome hardship. True power comes from within.",
     "Self-doubt, weakness, raw emotion. Surrendering to fear or failing to master anger."),
    ("hermit", 9, "은둔자", "The Hermit",
     "성찰·고독·내면 탐구", "introspection, solitude, guidance",
     "은둔자는 등불을 들고 홀로 진리를 찾습니다. 잠시 물러나 성찰하고 내면의 빛을 따를 때. 고독 속에서 답을 얻습니다.",
     "고립·외로움·도피. 지나친 칩거로 단절되거나 성찰을 회피합니다.",
     "The Hermit walks alone with a lantern, seeking truth. A time to withdraw, reflect, and follow your inner light. Answers come in solitude.",
     "Isolation, loneliness, escapism. Excessive withdrawal cutting you off, or avoiding reflection."),
    ("wheel-of-fortune", 10, "운명의 수레바퀴", "Wheel of Fortune",
     "운명·전환점·순환", "destiny, turning point, cycles",
     "수레바퀴가 돌며 운명의 전환점이 찾아옵니다. 행운과 변화의 흐름. 통제할 수 없는 큰 흐름을 받아들이고 기회를 잡으세요.",
     "불운·정체·악순환. 흐름에 저항하거나 같은 실수를 반복합니다.",
     "The Wheel turns and a turning point of destiny arrives. A flow of luck and change. Accept the larger current beyond your control and seize the moment.",
     "Bad luck, stagnation, vicious cycles. Resisting the flow or repeating the same mistakes."),
    ("justice", 11, "정의", "Justice",
     "공정·진실·인과", "fairness, truth, cause and effect",
     "정의는 저울과 검으로 진실과 균형을 가립니다. 뿌린 대로 거두는 인과의 때. 공정한 판단과 책임 있는 결정이 필요합니다.",
     "불공정·편견·책임 회피. 진실을 외면하거나 부당한 결과를 마주합니다.",
     "Justice weighs truth and balance with scales and sword. You reap what you sow. Fair judgment and accountable decisions are called for.",
     "Injustice, bias, evasion of responsibility. Ignoring truth or facing an unfair outcome."),
    ("hanged-man", 12, "매달린 사람", "The Hanged Man",
     "전환·내려놓음·새 관점", "surrender, new perspective, pause",
     "거꾸로 매달린 사람은 멈춰서 세상을 다르게 봅니다. 내려놓음과 기다림 속에 깨달음이 옵니다. 통제를 포기할 때 길이 열립니다.",
     "정체·희생만 하기·고집. 무의미한 기다림이나 변화 거부로 갇힙니다.",
     "Hanging upside down, the figure pauses to see the world anew. Insight comes through surrender and patience. Letting go of control opens the way.",
     "Stagnation, needless sacrifice, stubbornness. Stuck in pointless waiting or refusing to change."),
    ("death", 13, "죽음", "Death",
     "끝과 시작·변형·재생", "endings, transformation, rebirth",
     "죽음 카드는 실제 죽음이 아니라 한 시기의 끝과 변형을 뜻합니다. 낡은 것을 떠나보내야 새것이 옵니다. 피할 수 없는 변화를 받아들이세요.",
     "변화 거부·집착·정체. 끝내야 할 것을 붙잡아 고통이 길어집니다.",
     "Death means not literal death but the end of a chapter and transformation. The old must go for the new to come. Embrace inevitable change.",
     "Resistance to change, clinging, stagnation. Holding on to what must end prolongs the pain."),
    ("temperance", 14, "절제", "Temperance",
     "균형·조화·중용", "balance, moderation, harmony",
     "절제는 두 잔의 물을 섞으며 완벽한 균형을 만듭니다. 인내와 조율, 중용의 미덕. 서두르지 말고 알맞게 어우러질 때입니다.",
     "불균형·과잉·조급함. 극단으로 치우치거나 인내를 잃습니다.",
     "Temperance blends two cups into perfect balance. The virtue of patience, blending, and moderation. Don't rush — find the right mix.",
     "Imbalance, excess, impatience. Swinging to extremes or losing patience."),
    ("devil", 15, "악마", "The Devil",
     "속박·욕망·집착", "bondage, addiction, materialism",
     "악마는 느슨한 사슬에 묶인 사람들을 보여줍니다. 욕망·중독·물질에 스스로 매인 상태. 그 사슬은 사실 마음만 먹으면 벗을 수 있습니다.",
     "해방·각성·사슬 끊기. 속박을 자각하고 벗어나기 시작합니다(역방향이 긍정).",
     "The Devil shows figures in loose chains — self-bound by desire, addiction, or materialism. The chains can be removed the moment you choose.",
     "Liberation, awakening, breaking free. Recognizing the bondage and beginning to escape (reversed is positive here)."),
    ("tower", 16, "탑", "The Tower",
     "급변·붕괴·각성", "sudden change, upheaval, revelation",
     "벼락 맞은 탑이 무너집니다. 거짓된 토대의 급작스러운 붕괴, 충격적 진실. 고통스럽지만 잘못 세운 것을 허물어 진짜를 세웁니다.",
     "붕괴의 회피·내적 격변·재난의 지연. 무너짐을 미루며 불안이 길어집니다.",
     "Lightning strikes the Tower and it falls. The sudden collapse of false foundations, a shocking truth. Painful, but it clears what was wrongly built.",
     "Averted disaster, inner upheaval, delayed collapse. Postponing the fall prolongs the anxiety."),
    ("star", 17, "별", "The Star",
     "희망·치유·영감", "hope, healing, inspiration",
     "탑의 혼돈 뒤 별이 빛나며 희망과 치유를 가져옵니다. 평온, 영감, 회복의 시기. 다시 믿음을 갖고 꿈을 향해 나아가세요.",
     "희망 상실·낙담·믿음 부족. 잠시 빛을 잃었지만 곧 회복됩니다.",
     "After the Tower's chaos, the Star shines with hope and healing. A time of serenity, inspiration, and recovery. Have faith again and move toward your dream.",
     "Loss of hope, discouragement, lack of faith. The light is dimmed for now but recovery is near."),
    ("moon", 18, "달", "The Moon",
     "불안·환상·무의식", "illusion, fear, the subconscious",
     "달빛 아래 모든 것이 흐릿합니다. 불안·혼란·무의식의 두려움. 보이는 것이 전부가 아니니 직관에 의지하되 환상에 속지 마세요.",
     "혼란의 해소·진실 드러남·두려움 극복. 안개가 걷히기 시작합니다.",
     "Under moonlight everything is blurred — anxiety, confusion, subconscious fears. Things aren't as they seem; trust intuition but beware illusions.",
     "Confusion lifting, truth emerging, fear overcome. The fog begins to clear."),
    ("sun", 19, "태양", "The Sun",
     "기쁨·성공·활력", "joy, success, vitality",
     "태양은 타로에서 가장 밝은 카드입니다. 기쁨·성공·활력·명료함. 모든 것이 잘 풀리고 진심이 빛을 발합니다. 마음껏 누리세요.",
     "일시적 흐림·과신·기쁨의 지연. 행복이 잠시 가려지나 본질은 밝습니다.",
     "The Sun is the brightest card in tarot — joy, success, vitality, clarity. Everything goes well and your true self shines. Bask in it.",
     "Temporary clouds, overconfidence, delayed joy. Happiness briefly veiled, but the essence stays bright."),
    ("judgement", 20, "심판", "Judgement",
     "각성·재생·소명", "awakening, reckoning, calling",
     "천사의 나팔에 죽은 자들이 깨어납니다. 인생의 결산과 부활, 더 높은 소명에 응답하는 때. 과거를 정리하고 새 삶으로 거듭나세요.",
     "자기 비판·소명 회피·과거에 갇힘. 깨달음을 외면하거나 자책에 빠집니다.",
     "At the angel's trumpet the dead awaken. A reckoning and rebirth, a time to answer a higher calling. Settle the past and rise into a new life.",
     "Self-criticism, ignored calling, stuck in the past. Avoiding the awakening or drowning in self-blame."),
    ("world", 21, "세계", "The World",
     "완성·성취·통합", "completion, fulfillment, wholeness",
     "세계 카드는 여정의 완성과 성취를 뜻합니다. 한 주기가 충만하게 마무리되고 통합을 이룹니다. 마땅한 보상과 새로운 시작이 함께 옵니다.",
     "미완성·정체·마무리 부족. 거의 다 왔지만 마지막 단계가 막혀 있습니다.",
     "The World signifies the completion and fulfillment of a journey. A cycle closes fully and wholeness is achieved. Well-earned reward and a fresh start arrive together.",
     "Incompletion, stagnation, unfinished business. So close, yet the final step is blocked."),
]

# ─── 마이너 아르카나 56장 ────────────────────────────────
SUITS = [
    ("wands", "완드", "Wands", "불", "열정·에너지·일/창조"),
    ("cups", "컵", "Cups", "물", "감정·사랑·관계"),
    ("swords", "소드", "Swords", "공기", "생각·갈등·진실"),
    ("pentacles", "펜타클", "Pentacles", "흙", "물질·일·돈/건강"),
]
RANKS = [
    ("ace", "에이스", "Ace"), ("2", "2", "Two"), ("3", "3", "Three"),
    ("4", "4", "Four"), ("5", "5", "Five"), ("6", "6", "Six"),
    ("7", "7", "Seven"), ("8", "8", "Eight"), ("9", "9", "Nine"),
    ("10", "10", "Ten"), ("page", "페이지", "Page"),
    ("knight", "나이트", "Knight"), ("queen", "퀸", "Queen"), ("king", "킹", "King"),
]

# 카드별 (정방향ko, 역방향ko, 정방향en, 역방향en)
MINOR_MEANINGS = {
    "wands": {
        "ace": ("새로운 열정·영감·시작의 불꽃", "추진력 상실·지연·아이디어 고갈", "spark of inspiration, new venture", "delays, lack of drive, false start"),
        "2": ("계획·선택·미래 구상", "우유부단·계획 어긋남·두려움", "planning, choices, future vision", "indecision, fear, plans gone awry"),
        "3": ("확장·전망·기다림의 결실", "지연·예상 빗나감·근시안", "expansion, foresight, progress", "delays, setbacks, lack of foresight"),
        "4": ("축하·안정·이정표", "불안정·축하의 연기·갈등", "celebration, harmony, milestone", "instability, tension at home"),
        "5": ("경쟁·갈등·의견 충돌", "갈등 회피·합의·긴장 완화", "competition, conflict, struggle", "avoiding conflict, resolution"),
        "6": ("승리·인정·성취", "자만·인정 부족·승리 지연", "victory, recognition, success", "ego, lack of recognition, delay"),
        "7": ("방어·도전 응전·소신", "압도당함·포기·자신감 상실", "defense, standing your ground", "overwhelm, giving up, yielding"),
        "8": ("빠른 전개·진전·소식", "지연·서두름·혼란", "swift action, momentum, news", "delays, haste, scattered energy"),
        "9": ("끈기·경계·마지막 고비", "탈진·방어 과잉·완고함", "resilience, persistence, last stand", "exhaustion, paranoia, rigidity"),
        "10": ("과중한 부담·책임", "짐 내려놓기·위임·해방", "burden, heavy responsibility", "releasing the load, delegation"),
        "page": ("열정적 소식·탐험·호기심", "방향 상실·미성숙·지연", "enthusiasm, exploration, news", "lack of direction, immaturity"),
        "knight": ("모험·돌진·열정적 행동", "성급함·무모함·좌절", "adventure, bold action, passion", "haste, recklessness, frustration"),
        "queen": ("자신감·활력·매력적 리더", "질투·요구과다·자기 의심", "confidence, vitality, charisma", "jealousy, demanding, self-doubt"),
        "king": ("비전·리더십·결단의 카리스마", "독선·성급함·무자비", "vision, leadership, charisma", "impulsiveness, tyranny"),
    },
    "cups": {
        "ace": ("새로운 사랑·감정의 충만·영적 시작", "막힌 감정·공허·관계 지연", "new love, overflowing emotion", "blocked feelings, emptiness"),
        "2": ("결합·상호 사랑·동반자", "불화·관계 불균형·이별", "partnership, mutual love, union", "discord, imbalance, breakup"),
        "3": ("우정·축하·공동체", "과음·소문·고립", "friendship, celebration, community", "excess, gossip, isolation"),
        "4": ("권태·무관심·재평가", "새 기회 포착·각성·수용", "apathy, contemplation, boredom", "seizing a new chance, awakening"),
        "5": ("상실·후회·슬픔", "회복·용서·앞으로 나아감", "loss, regret, grief", "recovery, forgiveness, moving on"),
        "6": ("향수·순수·옛 인연", "과거에 갇힘·미성숙", "nostalgia, innocence, reunion", "stuck in the past, immaturity"),
        "7": ("환상·선택지 과잉·공상", "명료함·현실적 선택·집중", "fantasy, too many choices", "clarity, focus, realistic choice"),
        "8": ("떠남·더 깊은 의미 찾기", "표류·떠나지 못함·두려움", "walking away, seeking meaning", "drifting, fear of leaving"),
        "9": ("만족·소원 성취·행복", "자만·과욕·표면적 만족", "contentment, wish fulfilled", "smugness, greed, shallow joy"),
        "10": ("가정의 행복·완성된 사랑", "관계 불화·이상과 현실 괴리", "harmony, family happiness", "broken harmony, misaligned values"),
        "page": ("감성적 소식·창의·직관", "감정 미성숙·현실 도피", "creative, intuitive message", "emotional immaturity, escapism"),
        "knight": ("로맨스 제안·이상주의·매력", "변덕·과장·실망", "romance, idealism, charm", "moodiness, exaggeration"),
        "queen": ("공감·따뜻함·정서적 안정", "감정 의존·과민·경계 부족", "compassion, warmth, intuition", "dependency, over-sensitivity"),
        "king": ("감정의 균형·관대함·지혜", "감정 억압·조종·변덕", "emotional balance, generosity", "repression, manipulation"),
    },
    "swords": {
        "ace": ("돌파구·명료함·진실의 통찰", "혼란·잘못된 판단·정보 부족", "breakthrough, clarity, truth", "confusion, misjudgment"),
        "2": ("교착·결정 회피·균형", "결단·진실 직시·교착 해소", "stalemate, avoidance, balance", "decision made, facing truth"),
        "3": ("상심·이별·고통스러운 진실", "회복·용서·슬픔의 끝", "heartbreak, painful truth", "recovery, forgiveness, healing"),
        "4": ("휴식·회복·재충전", "재기·정체·휴식 거부", "rest, recovery, contemplation", "restlessness, burnout, stagnation"),
        "5": ("갈등·승패·자존심 다툼", "화해·후회·긴장 완화", "conflict, defeat, hollow win", "reconciliation, regret, release"),
        "6": ("전환·이동·평온으로의 항해", "정체·떠나지 못함·미해결", "transition, moving on, calmer waters", "stuck, unable to move on"),
        "7": ("전략·기만·홀로서기", "발각·양심·전략 수정", "strategy, deception, going solo", "exposure, conscience, rethink"),
        "8": ("자기 제약·무력감·갇힘", "해방·자각·속박에서 벗어남", "self-imposed limits, feeling trapped", "liberation, new perspective"),
        "9": ("불안·악몽·근심", "희망의 빛·회복·과장된 두려움", "anxiety, worry, nightmares", "hope returning, fears overcome"),
        "10": ("바닥·끝·고통의 종결", "회복·재생·최악은 지났음", "rock bottom, painful ending", "recovery, the worst is over"),
        "page": ("호기심·경계·새 아이디어", "험담·성급한 말·산만", "curiosity, vigilance, new ideas", "gossip, hasty words, scattered"),
        "knight": ("돌진·논리·거침없는 행동", "무모함·공격성·충동", "drive, logic, bold action", "recklessness, aggression"),
        "queen": ("명석함·독립·솔직함", "냉정함·신랄함·고립", "clarity, independence, honesty", "coldness, bitterness, isolation"),
        "king": ("이성·권위·공정한 판단", "독단·냉혹·권력 남용", "intellect, authority, fairness", "tyranny, cruelty, manipulation"),
    },
    "pentacles": {
        "ace": ("새 기회·풍요의 씨앗·번영", "기회 상실·계획 지연·탐욕", "new opportunity, prosperity seed", "missed chance, delay, greed"),
        "2": ("균형 잡기·다중 작업·적응", "과부하·불균형·우선순위 혼란", "balance, juggling, adaptability", "overwhelm, imbalance"),
        "3": ("협업·기술·인정받는 성과", "부조화·기술 부족·태만", "teamwork, skill, recognition", "discord, mediocrity, lack of teamwork"),
        "4": ("안정·소유·절약", "인색·집착·통제 과잉", "stability, security, saving", "greed, clinging, over-control"),
        "5": ("결핍·어려움·소외감", "회복·도움 발견·역경 극복", "hardship, want, isolation", "recovery, help found, turning point"),
        "6": ("나눔·관대함·균형 잡힌 주고받기", "불공정·빚·일방적 관계", "generosity, giving and receiving", "inequality, debt, strings attached"),
        "7": ("인내·장기 투자·평가", "조급함·노력 대비 부진·포기", "patience, long-term view, assessment", "impatience, poor return, giving up"),
        "8": ("숙련·근면·기술 연마", "완벽주의·태만·질 저하", "mastery, diligence, skill-building", "perfectionism, no ambition"),
        "9": ("자립·풍요·결실의 향유", "과시·자립 부족·금전 불안", "self-sufficiency, luxury, reward", "showiness, financial insecurity"),
        "10": ("부·가문의 안정·유산", "재정 불안·가족 갈등·상실", "wealth, legacy, family stability", "financial loss, family conflict"),
        "page": ("학습·기회 포착·실용적 꿈", "미루기·비현실·기회 놓침", "study, opportunity, practical goals", "procrastination, missed chance"),
        "knight": ("성실·꾸준함·책임감", "지루함·정체·완고함", "diligence, routine, reliability", "boredom, stagnation, stubbornness"),
        "queen": ("실용·풍요·따뜻한 보살핌", "일과 삶 불균형·물질 집착", "practical, nurturing, abundance", "work-life imbalance, materialism"),
        "king": ("성공·풍요·안정된 리더", "물질주의·완고함·탐욕", "success, abundance, secure leader", "materialism, stubbornness, greed"),
    },
}


def _build_minor():
    cards = []
    for s_slug, s_ko, s_en, elem, theme in SUITS:
        for r_slug, r_ko, r_en in RANKS:
            m = MINOR_MEANINGS[s_slug][r_slug]
            slug = f"{r_slug}-of-{s_slug}"
            ko_name = f"{s_ko} {r_ko}" if r_slug not in ("ace",) else f"{s_ko} 에이스"
            en_name = f"{r_en} of {s_en}"
            cards.append({
                "slug": slug, "arcana": "minor", "suit": s_slug, "suit_ko": s_ko,
                "element": elem, "num": None,
                "ko_name": ko_name, "en_name": en_name,
                "kw_ko": theme, "kw_en": "",
                "up_ko": m[0], "rev_ko": m[1], "up_en": m[2], "rev_en": m[3],
            })
    return cards


def _build_major():
    out = []
    for slug, num, ko, en, kwko, kwen, upko, revko, upen, reven in MAJOR:
        out.append({
            "slug": slug, "arcana": "major", "suit": None, "suit_ko": None,
            "element": None, "num": num,
            "ko_name": ko, "en_name": en, "kw_ko": kwko, "kw_en": kwen,
            "up_ko": upko, "rev_ko": revko, "up_en": upen, "rev_en": reven,
        })
    return out


DECK = _build_major() + _build_minor()          # 78장
BY_SLUG = {c["slug"]: c for c in DECK}


def get_card(slug: str):
    return BY_SLUG.get(slug)


def all_major():
    return [c for c in DECK if c["arcana"] == "major"]


def all_minor():
    return [c for c in DECK if c["arcana"] == "minor"]


def cards_by_suit(suit: str):
    return [c for c in DECK if c.get("suit") == suit]


def daily_card(d: date | None = None):
    """날짜 기준 결정론적 '오늘의 카드' — 하루 동안 동일(공유 가능). 정/역방향 포함."""
    d = d or date.today()
    h = hashlib.md5(d.isoformat().encode()).hexdigest()
    idx = int(h[:8], 16) % len(DECK)
    reversed_ = (int(h[8:10], 16) % 2 == 1)
    card = DECK[idx]
    return card, reversed_
