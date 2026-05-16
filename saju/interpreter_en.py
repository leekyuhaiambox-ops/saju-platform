"""English interpretations of the 60 day-pillars and related concepts.

Mirrors `interpreter.py` but provides English translations for international visitors.
Naming uses Pinyin romanization for Heavenly Stems and Earthly Branches, which is the
standard scholarly convention in English-language texts on Chinese astrology.
"""

# Pinyin romanization of 60 pillar names (stem + branch)
# Index = stem_index * 6 + branch_offset (computed via i % 10, i % 12)

DAY_PILLAR_INTERPRETATIONS_EN = {
    0: ("Jiazi (甲子)", "Great tree finding a deep well — scholar of wisdom and patience",
        "Brilliant intellect with deep academic drive and sharp intuition. High self-respect with the willpower to follow through once decisions are made. "
        "May feel lonely and emotionally sensitive — practicing emotional expression helps. "
        "Thrives in education, research, and planning fields. Recognition tends to come later in life, but is lasting."),
    1: ("Yichou (乙丑)", "Flower on cold earth — quiet endurance and patient strength",
        "Gentle outside, firm inside, with deep responsibility. Quietly endures hardship and ultimately earns recognition in their field. "
        "Wealth accumulates steadily over a lifetime; strong ties to family and real estate. "
        "Emotional expression can feel awkward — keeping trusted people close brings peace."),
    2: ("Bingyin (丙寅)", "Noon sun on a great mountain — leadership and honor",
        "Natural charisma and drive that pulls people forward. Energetic and adventurous with strong social ambition. "
        "Watch for impatience and mood swings — training to finish what you start matters. "
        "Excels in politics, media, art, and entrepreneurship."),
    3: ("Dingmao (丁卯)", "Candle beside spring blossoms — delicate and artistic",
        "Rich in emotion with refined aesthetic sense. Magnetic personality and strong people skills. "
        "Indecisiveness can let opportunities slip — practice making and keeping decisions. "
        "Fits design, culture, counseling, and education; many romantic connections."),
    4: ("Wuchen (戊辰)", "Rich earth holding hidden treasure — the trusted leader",
        "Steady and embracing; trust is the core asset. Once you commit, you keep it; suited for big responsibilities. "
        "Strong-willed and slow to change — building flexibility is the growth edge. "
        "Stable success in organizations, finance, real estate, and religion."),
    5: ("Jisi (己巳)", "Dry field under bright sun — quietly capable and shrewd",
        "Handles work calmly with practical results. Sharp intuition and analytical power — fit for academia and specialized professions. "
        "Sensitive and suspicious of strangers — opening the heart takes practice. "
        "Medicine, education, and law all suit this pillar well."),
    6: ("Gengwu (庚午)", "Steel forged in fire — decisive will and loyalty",
        "Strong decisiveness, drive, and a clear sense of honor. Once committed, the work gets done. "
        "Direct and quick-tempered — friction in relationships is common. "
        "Fits military, police, sports, business, and technical fields."),
    7: ("Xinwei (辛未)", "Jewel buried in dry soil — proud and refined",
        "Delicate yet proud, with outstanding aesthetic taste. Soft surface conceals real strength. "
        "Moody and slow to forgive hurts. "
        "Excels in art, culture, design, and finance; should be careful in romantic affairs."),
    8: ("Renshen (壬申)", "Great river crashing on rocks — wisdom through change",
        "Brilliant, adaptable, and fast on their feet; also strong in scholarship. Welcomes new environments. "
        "Emotional shifts run deep, and settling in one place is hard. "
        "Shines in diplomacy, trade, journalism, and research."),
    9: ("Guiyou (癸酉)", "Clear spring meeting jewel — clarity of intellect",
        "Bright mind and pristine character. Strong literary ability with keen insight. "
        "Selective in friendships, which can narrow the social circle. "
        "Suits scholarship, law, and the arts; recognition typically arrives later."),
    10: ("Jiaxu (甲戌)", "Great tree rooted on dry mountain — self-made independence",
         "Proud and independent — the self-made type. Heavy responsibility brings authority in your field. "
         "Tends toward solitude, which can read as cold to others. "
         "Earns respect in law, education, religion, and research."),
    11: ("Yihai (乙亥)", "Flower drinking water — abundant feeling and intuition",
         "Warm, imaginative, and emotionally rich. Mixes well with others and carries a kind heart. "
         "Lack of decisiveness and dependency on others can become weak points. "
         "Suits literature, art, education, and service; a good partner can unlock major growth."),
    12: ("Bingzi (丙子)", "Moonlight at midnight — soft outside, sharp inside",
         "Gentle on the surface, firm within, with sharp wit. Adapts well and is broadly popular. "
         "Emotions and decisions can shift often. "
         "Active in broadcasting, the arts, and education; charm is the asset."),
    13: ("Dingchou (丁丑)", "Spark in cold soil — quiet endurance",
         "Introverted, hardworking, and methodical. The artisan's mindset — deep focus in one field. "
         "Slow to express inner thoughts, which can cause misunderstanding. "
         "Solid success in craftsmanship, research, art, and religious vocations."),
    14: ("Wuyin (戊寅)", "Great mountain meeting spring — leadership and growth",
         "Embracing yet driven — a leader who gathers people and builds. "
         "Stubbornness and strong opinions can spark conflict. "
         "Excels in politics, administration, business, and education."),
    15: ("Jimao (己卯)", "Soft earth with spring flowers — gentle diligence",
         "Mild, dependable, and detail-oriented. Makes people at ease and excels at fine work. "
         "Lacks decisiveness and rarely pushes their own view. "
         "Finds their place in education, counseling, service, and culture."),
    16: ("Gengchen (庚辰)", "Ore inside great earth — vast potential",
         "Big ambition and drive with the ability to see large pictures. Once a path is chosen, it is pursued forcefully. "
         "Stubborn and committed only to their own method. "
         "Achieves great things in business, finance, politics, and technology."),
    17: ("Xinsi (辛巳)", "Jewel tempered by fire — change and challenge",
         "Quick-minded with sharp intuition and strong in unfamiliar terrain. Shines in fresh environments. "
         "Mood swings make settling in one place difficult. "
         "Excels in art, design, trade, and technology."),
    18: ("Renwu (壬午)", "Sun rising over a great river — activity and honor",
         "Active, sociable, and ambitious for recognition. Loves the stage and expresses well. "
         "Restless and sometimes impulsive. "
         "Strong in journalism, broadcasting, art, and diplomacy."),
    19: ("Guiwei (癸未)", "Sweet rain on dry earth — virtue and patience",
         "Quiet outside, strong and thoughtful within. Values people and gives generously. "
         "Reluctant to show emotion, which can frustrate others. "
         "Steady success in education, research, religion, and the arts."),
    20: ("Jiashen (甲申)", "Great tree meeting axe — the path of self-examination",
         "Sharp and discerning. Constantly refines self and grows. "
         "Sensitive and self-critical — building self-esteem is the work. "
         "Suits law, technology, research, and education."),
    21: ("Yiyou (乙酉)", "Autumn maple in cool wind — clean precision",
         "Refined, organized, and aesthetically driven. Demands clean relationships and high standards. "
         "Emotional expression can read as cold; flexibility is needed. "
         "Excels in design, finance, culture, and law."),
    22: ("Bingxu (丙戌)", "Sunset on a dry mountain — honor and loyalty",
         "Deep loyalty, honor, and responsibility. Keeps promises absolutely — earns lasting trust. "
         "Stubbornness and pride can create conflict. "
         "Wins respect in politics, religion, education, and the arts."),
    23: ("Dinghai (丁亥)", "Lantern over a great river — warm intelligence",
         "Gentle, thoughtful, and deeply human. Sharp in scholarship and arts with magnetic appeal. "
         "Decisions can waver; the heart is easily moved. "
         "Shines in literature, art, education, and counseling."),
    24: ("Wuzi (戊子)", "Mountain over flowing water — stability with motion",
         "Trustworthy, embracing, and calm. Capable of guiding large projects steadily. "
         "Internal conflict and slow decisions can delay action. "
         "Suits administration, finance, education, and religion."),
    25: ("Jichou (己丑)", "Cold rich field — crystallized patience",
         "Quietly responsible and reliable. Stays in one field long and builds true expertise. "
         "Slow to change and reserved in expression. "
         "Fits agriculture, real estate, education, and research."),
    26: ("Gengyin (庚寅)", "Steel and spring tree — decision and drive",
         "Decisive, driven, and hungry for honor. The self-made type who carves their own road. "
         "Direct and quick to anger, which causes friction. "
         "Achieves much in business, politics, military, and technology."),
    27: ("Xinmao (辛卯)", "Jewel in flower field — refinement and pride",
         "Refined aesthetic sense and high self-respect. Careful in friendships, with a private inner world. "
         "Sensitive — holds onto hurts for a long time. "
         "Excels in art, design, culture, and finance."),
    28: ("Renchen (壬辰)", "Dragon rising from sea — vast capacity",
         "Big-hearted, wise, and unafraid of change. Shines on the largest stages. "
         "Emotional volatility and inconsistency can be weak points. "
         "Achieves greatness in politics, diplomacy, journalism, and business."),
    29: ("Guisi (癸巳)", "Clear spring at noon — wisdom and insight",
         "Brilliant, with sharp intuition and analytical power. Suits scholarship and specialized fields. "
         "Sensitive and sometimes suspicious. "
         "Wins recognition in research, law, medicine, and religion."),
    30: ("Jiawu (甲午)", "Red flower on a great tree — honor and expression",
         "Lively, ambitious, and expressive. Strong charisma that draws followers. "
         "Hasty decisions and mood swings are real risks. "
         "Shines in journalism, broadcasting, education, and the arts."),
    31: ("Yiwei (乙未)", "Grass on sunlit hill — softness with firmness",
         "Mild, thoughtful, and family-oriented. Strong people-luck and rich emotional life. "
         "Indecisiveness and emotional pulls can be issues. "
         "Suits education, art, service, and culture."),
    32: ("Bingshen (丙申)", "Sun meeting steel — decision and honor",
         "Bright mind, decisive will, and honor-driven. Strong sense of responsibility — finishes what's begun. "
         "Quick-tempered, with changeable moods. "
         "Excels in law, politics, business, and journalism."),
    33: ("Dingyou (丁酉)", "Candle and jewel — elegant intelligence",
         "Refined and aesthetically attuned, with strong scholarship. Clean relationships and trustworthy presence. "
         "Sensitive and slow to decide. "
         "Earns recognition in art, culture, education, and finance."),
    34: ("Wuxu (戊戌)", "Solid earth of dry mountain — trust and honor",
         "Heavy with responsibility and loyal in spirit. Keeps relationships for a lifetime. "
         "Stubborn and slow to change. "
         "Steady success in religion, education, real estate, and business."),
    35: ("Jihai (己亥)", "Rich soil with flowing water — abundance and virtue",
         "Mild, embracing, and lucky with people. Mixes well with others and attracts wealth. "
         "Indecisive and somewhat dependent. "
         "Fits education, service, culture, and finance."),
    36: ("Gengzi (庚子)", "Steel and great river — wisdom and decision",
         "Bright, decisive, and analytical. Builds expertise in one field. "
         "Emotional expression can read as cold. "
         "Excels in law, finance, technology, and research."),
    37: ("Xinchou (辛丑)", "Jewel in cold soil — patience and pride",
         "Delicate, patient, and self-respecting. Quietly walks their own path. "
         "Inner loneliness can read as frustration. "
         "Finds their place in art, finance, religion, and research."),
    38: ("Renyin (壬寅)", "Great river and spring tree — wisdom and growth",
         "Bright, forward-thinking, and adaptable. Creates new work and new worlds. "
         "Restless — settling is difficult, and the heart shifts often. "
         "Shines in education, journalism, art, and technology."),
    39: ("Guimao (癸卯)", "Spring rain on new buds — fresh feeling",
         "Tender, emotional, and aesthetically attuned. Connects well with others. "
         "Lacks decisiveness and can be swept by feeling. "
         "Suits literature, art, education, and counseling."),
    40: ("Jiachen (甲辰)", "Great tree meeting dragon — vast capacity",
         "Ambitious, principled, and responsible. Leads big projects and gathers people. "
         "Stubborn pride can create conflict. "
         "Achieves great things in politics, business, education, and religion."),
    41: ("Yisi (乙巳)", "Summer flower in sun — vivid expression",
         "Rich in feeling and expression — sociable. Reads people's hearts intuitively. "
         "Moody and changeable. "
         "Excels in broadcasting, art, culture, and service."),
    42: ("Bingwu (丙午)", "Noon sun at peak — peak of charisma",
         "Charisma and drive at their fullest, dominating any room. Strong ambition reaches the peak of one's field. "
         "Hasty temper and over-confidence can be traps. "
         "Shines in politics, journalism, art, and business."),
    43: ("Dingwei (丁未)", "Summer field lantern — warm virtue",
         "Mild, thoughtful, and loving. Trusted by others and finds good connections. "
         "Decision-making can drag. "
         "Suits education, counseling, religion, and culture."),
    44: ("Wushen (戊申)", "Great mountain and steel — firm will",
         "Trustworthy, decisive, and resolute. Walks a chosen path without wavering. "
         "Stubborn and tied to one method. "
         "Steady success in administration, finance, technology, and law."),
    45: ("Jiyou (己酉)", "Jewel in rich soil — refined pragmatist",
         "Thorough, refined, and aesthetically aware. The artisan-type building expertise in one field. "
         "Pride and resistance to change can be issues. "
         "Excels in art, finance, research, and design."),
    46: ("Gengxu (庚戌)", "Steel axe on great mountain — authority and loyalty",
         "Upright, loyal, and authoritative. Strong responsibility earns trust. "
         "Direct and inflexible. "
         "Excels in military, police, law, business, and religion."),
    47: ("Xinhai (辛亥)", "Jewel in great river — clear intellect",
         "Bright, eager to learn, and expressive. Pristine character earns trust. "
         "Emotionally sensitive — lonely by nature. "
         "Shines in scholarship, art, journalism, and diplomacy."),
    48: ("Renzi (壬子)", "Peak of great river — wisdom and change",
         "Brilliantly quick and adaptive. Connects widely; fast on information. "
         "Emotional shifts run deep — settling is hard. "
         "Suits journalism, diplomacy, trade, and research."),
    49: ("Guichou (癸丑)", "Winter rain on frozen earth — crystallized patience",
         "Endures silently and bears fruit through grit. Deep focus in one field builds real expertise. "
         "Quiet and introverted, sometimes misread by others. "
         "Steady success in research, technology, art, and religion."),
    50: ("Jiayin (甲寅)", "Tiger of the great forest — ambition and drive",
         "Big-hearted, driven, and honor-hungry. The leader who carves their own road. "
         "Stubborn and slow to compromise. "
         "Achieves much in politics, business, education, and culture."),
    51: ("Yimao (乙卯)", "Spring flower and rabbit — softness and magnetism",
         "Gentle, magnetic, and warm in friendships. Naturally attracts goodwill. "
         "Lacks decisiveness and rarely asserts own view. "
         "Suits art, culture, education, and service."),
    52: ("Bingchen (丙辰)", "Noon sun and dragon — honor and authority",
         "Big ambition, charisma, and leadership. Pursues honor and high position. "
         "Hasty temper and pride can be traps. "
         "Shines in politics, business, journalism, and education."),
    53: ("Dingsi (丁巳)", "Summer lantern — passion and intuition",
         "Sensitive, intuitive, and passionate. Dives deep into chosen work. "
         "Mood swings can be large; impulsive. "
         "Excels in art, religion, research, and journalism."),
    54: ("Wuwu (戊午)", "Sun on the noon mountain — will and honor",
         "Trustworthy, resolute, and honor-driven. Strong responsibility earns wide trust. "
         "Stubborn and inflexible. "
         "Steady success in administration, politics, religion, and education."),
    55: ("Jiwei (己未)", "Rich field in summer — virtue and abundance",
         "Mild, embracing, and rich in people-luck. Attracts gatherings and wealth. "
         "Indecisive, sometimes dependent. "
         "Fits education, service, culture, and religion."),
    56: ("Gengshen (庚申)", "Steel ore — decision and loyalty",
         "Strong willpower and decisive action with deep loyalty. Once committed, the work gets done. "
         "Direct and inflexible. "
         "Excels in military, police, law, technology, and business."),
    57: ("Xinyou (辛酉)", "Essence of jewel — pure pride",
         "Refined, immaculate, and proud. Sharp aesthetic sense and analytical power. "
         "Sensitive and inflexible. "
         "Shines in art, finance, law, and culture."),
    58: ("Renxu (壬戌)", "Great river and dry mountain — wisdom and loyalty",
         "Bright, loyal, and responsible. Keeps promises and earns trust. "
         "Mood swings and stubbornness exist. "
         "Suits journalism, education, religion, and diplomacy."),
    59: ("Guihai (癸亥)", "Raindrop in the great sea — deep wisdom",
         "Thoughtful, sharply intuitive, and academically inclined. The scholar who loves deep contemplation. "
         "Emotionally sensitive — lonely by nature. "
         "Wins recognition in research, art, religion, and literature."),
}


TEN_GOD_EN = {
    "비견": ("Bijian (Friend Star)",
             "Independence, self-respect, and peers. Same element + same polarity — your colleagues and rivals."),
    "겁재": ("Geopjae (Rival Star)",
             "Drive and competitive spirit. Same element + opposite polarity — strong activity, but watch wealth losses."),
    "식신": ("Sikshin (Output Star)",
             "Self-expression, growth, and a comfortable life. Soft, steady creative output."),
    "상관": ("Sanggwan (Hurting Officer)",
             "Talent, creativity, rebellion. Brilliant ideas, but resists authority."),
    "편재": ("Pyeonjae (Indirect Wealth)",
             "Business, wealth flow, and partnerships. Active money that moves big in and out."),
    "정재": ("Jeongjae (Direct Wealth)",
             "Stable wealth and a settled life. The steady fortune of patient labor and partnership."),
    "편관": ("Pyeongwan (Seven Killings)",
             "Pressure, authority, and trial. Strong tension that, well-handled, becomes power and honor."),
    "정관": ("Jeonggwan (Direct Officer)",
             "Honor, profession, and order. Stable career and clear social position."),
    "편인": ("Pyeonin (Indirect Resource)",
             "Inspiration, religion, and solitary scholarship. Unique mind and intuition, somewhat isolated."),
    "정인": ("Jeongin (Direct Resource)",
             "Wisdom, documents, and mother-figure. Learning, paperwork, and supportive relationships."),
}


TWELVE_STAGE_EN = {
    "장생": "Birth — Newborn energy. Fresh, pure, strong at beginnings.",
    "목욕": "Bathing — Growing and changing. Style, transformation, frequent romantic encounters.",
    "관대": "Capping — Coming of age. Strong ambition and self-respect.",
    "건록": "Establishing — Peak activity. Career independence and stability.",
    "제왕": "Empire — Apex of energy. Strong drive and charisma; can grow arrogant.",
    "쇠": "Decline — Past the peak, moving toward stability. Calm and reflective.",
    "병": "Sickness — Energy weakens. Sensitive, emotionally rich, artistic.",
    "사": "Death — Activity halts. Deep introspection, spiritual interests.",
    "묘": "Tomb — Buried in earth. Patience, storage, research.",
    "절": "Cut-off — Severance and new beginning. Change and decisions are frequent.",
    "태": "Womb — New life conceived. Latent potential and possibility.",
    "양": "Nurture — Fetus growing. Development under stability and protection.",
}


ELEMENT_EN = {
    "목": ("Wood — Growth, Benevolence (仁)",
           "Wood rises and reaches outward, like a tree in spring. Drive, vision, and forward-thinking. "
           "Too little: weak ambition and decision. Too much: stubbornness and inflexibility."),
    "화": ("Fire — Expression, Propriety (禮)",
           "Fire spreads, like the noon sun. Expression, passion, sociability. "
           "Too little: weak self-confidence and expression. Too much: impulse and scattered focus."),
    "토": ("Earth — Trust, Faithfulness (信)",
           "Earth supports and mediates, like vast soil. Embracing, mediating, stable. "
           "Too little: lacking center. Too much: stubbornness and resistance to change."),
    "금": ("Metal — Decision, Righteousness (義)",
           "Metal contracts and refines, like ore. Decisiveness, judgment, justice. "
           "Too little: indecision. Too much: rigidity and harsh criticism."),
    "수": ("Water — Wisdom, Knowledge (智)",
           "Water flows and stores. Intelligence, adaptability, quick wit. "
           "Too little: poor flexibility and intuition. Too much: moodiness and melancholy."),
}


ZODIAC_TRAITS_EN = {
    "쥐":   ("Zi (Rat)", "Quick · Sharp · Wealth-Sense",
             "Sharp wits with a strong sense for wealth. Fast information is the weapon."),
    "소":   ("Chou (Ox)", "Diligent · Patient · Trusted",
             "Quietly hardworking with deep responsibility. Shines in one field over time."),
    "호랑이": ("Yin (Tiger)", "Brave · Driven · Leader",
             "Charismatic for adventure and challenge. Born for leadership."),
    "토끼": ("Mao (Rabbit)", "Gentle · Aesthetic · People-Luck",
             "Soft magnetism that draws others. Strong in art, culture, and service."),
    "용":   ("Chen (Dragon)", "Ambition · Vision · Creativity",
             "Big-picture vision and creative power. Shines in beginnings and transitions."),
    "뱀":   ("Si (Snake)", "Intuition · Insight · Caution",
             "Sharp analysis and deep thinking. Suited for specialized fields."),
    "말":   ("Wu (Horse)", "Activity · Expression · Freedom",
             "Lively, sociable, and expressive. Born for the stage."),
    "양":   ("Wei (Goat)", "Embrace · Art · Feeling",
             "Warm and emotionally rich. Shines in art and caregiving."),
    "원숭이": ("Shen (Monkey)", "Wit · Adaptability · Skill",
             "Quick thinking and many talents. Strong in changing environments."),
    "닭":   ("You (Rooster)", "Precision · Pride · Beauty",
             "Detailed and refined with sharp aesthetic sense. Detail is the asset."),
    "개":   ("Xu (Dog)", "Loyalty · Honesty · Responsibility",
             "Trustworthy and just. Excels in guardian and mediator roles."),
    "돼지": ("Hai (Pig)", "Optimism · Abundance · Virtue",
             "Fortune-attracting nature. Surrounded by people and warmth."),
}
