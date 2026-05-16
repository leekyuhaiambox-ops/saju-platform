"""English glossary of Saju/Korean astrology terms."""

GLOSSARY_EN = [
    # ─── Core concepts ───
    ("Saju (四柱)", "Core", "Literally 'four pillars' — the chart of birth year, month, day, and hour, each encoded as one Heavenly Stem and one Earthly Branch. Eight characters total, often called 'Sajupalja' (四柱八字)."),
    ("Myeongsik (命式)", "Core", "The formatted Saju chart: four pillars laid out horizontally with stems above and branches below."),
    ("Heavenly Stems (天干)", "Core", "Ten celestial signs of heavenly energy: Jia, Yi, Bing, Ding, Wu, Ji, Geng, Xin, Ren, Gui."),
    ("Earthly Branches (地支)", "Core", "Twelve terrestrial signs of earthly energy: Zi, Chou, Yin, Mao, Chen, Si, Wu, Wei, Shen, You, Xu, Hai — also marking hours, seasons, and zodiac animals."),
    ("60 Pillars (六十甲子)", "Core", "Sixty cyclic combinations formed by pairing the 10 stems with the 12 branches, starting from Jiazi and ending with Guihai."),
    ("Yin-Yang (陰陽)", "Core", "Two opposing primal forces of all phenomena. Yang is active/outward; Yin is receptive/inward."),
    ("Five Elements (五行)", "Core", "The five fundamental motions of the cosmos: Wood (growth), Fire (spread), Earth (mediate), Metal (contract), Water (store)."),
    ("Mutual Generation (相生)", "Core", "Productive cycle: Wood feeds Fire, Fire enriches Earth, Earth bears Metal, Metal nourishes Water, Water grows Wood."),
    ("Mutual Restraint (相剋)", "Core", "Controlling cycle: Wood pierces Earth, Earth dams Water, Water quenches Fire, Fire melts Metal, Metal cuts Wood."),

    # ─── Pillars ───
    ("Year Pillar (年柱)", "Pillars", "Stem-Branch of birth year. Reveals lineage, early life, and external environment. The boundary is the solar term Ipchun (around February 4)."),
    ("Month Pillar (月柱)", "Pillars", "Stem-Branch of birth month. Reveals parents, youth, and career entry. Boundaries are set by 12 of the 24 solar terms."),
    ("Day Pillar (日柱)", "Pillars", "Stem-Branch of birth day. Represents the self and spouse — the most important pillar in modern Saju."),
    ("Hour Pillar (時柱)", "Pillars", "Stem-Branch of birth hour. Reveals children, late life, and old age."),
    ("Day Master (日干)", "Pillars", "The Heavenly Stem of the Day Pillar — the 'self' anchoring all Saju interpretation."),
    ("Day Branch (日支)", "Pillars", "The Earthly Branch of the Day Pillar — called the 'spouse palace,' it shows daily-life rhythms."),

    # ─── Ten Gods ───
    ("Ten Gods (十神)", "Ten Gods", "Ten relational labels assigned to the other seven characters based on their Five-Element relationship to the day stem."),
    ("Bijian (比肩)", "Ten Gods", "Same element + same polarity. Self, peers, independence."),
    ("Geopjae (劫財)", "Ten Gods", "Same element + opposite polarity. Rival, drive — watch for wealth loss."),
    ("Sikshin (食神)", "Ten Gods", "Day stem produces, same polarity. Comfort, output, gentle creativity."),
    ("Sanggwan (傷官)", "Ten Gods", "Day stem produces, opposite polarity. Sharp talent, art, rebellion."),
    ("Pyeonjae (偏財)", "Ten Gods", "Day stem controls, same polarity. Business, active wealth, opportunity."),
    ("Jeongjae (正財)", "Ten Gods", "Day stem controls, opposite polarity. Stable wealth, spouse (for men)."),
    ("Pyeongwan (偏官)", "Ten Gods", "Controls day stem, same polarity (Seven Killings). Power, trial, military aptitude."),
    ("Jeonggwan (正官)", "Ten Gods", "Controls day stem, opposite polarity. Career, honor, husband (for women)."),
    ("Pyeonin (偏印)", "Ten Gods", "Produces day stem, same polarity. Inspiration, religion, solitary scholarship."),
    ("Jeongin (正印)", "Ten Gods", "Produces day stem, opposite polarity. Mother, documents, study, kindness."),

    # ─── Twelve Life Stages ───
    ("Twelve Life Stages (十二運星)", "Stages", "Twelve life-stage gauges from Birth to Tomb, measuring the energy of the day stem at each branch position."),
    ("Birth (長生)", "Stages", "Newborn vitality. Fresh, pure, strong at beginnings."),
    ("Bathing (沐浴)", "Stages", "Washing and growing. Style, change, many romantic encounters."),
    ("Capping (冠帶)", "Stages", "Coming of age. Drive and self-respect."),
    ("Establishing (建祿)", "Stages", "Peak adult activity. Independence and stability."),
    ("Empire (帝旺)", "Stages", "Apex of energy. Strong drive and charisma, possible arrogance."),
    ("Decline (衰)", "Stages", "Just past peak. Calm and reflective."),
    ("Sickness (病)", "Stages", "Weakening. Sensitivity, emotion, artistry."),
    ("Death (死)", "Stages", "Halted activity. Introspection, spirituality."),
    ("Tomb (墓)", "Stages", "Buried. Patience, storage, research."),
    ("Cut-off (絶)", "Stages", "Severance. Change and decisions frequent."),
    ("Womb (胎)", "Stages", "Newly conceived. Latent potential."),
    ("Nurture (養)", "Stages", "Fetus growing. Development under protection."),

    # ─── Unions and clashes ───
    ("Stem Union (天干合)", "Unions", "Five pairs of Heavenly Stems that fuse into a new element: Jia-Ji → Earth, Yi-Geng → Metal, Bing-Xin → Water, Ding-Ren → Wood, Wu-Gui → Fire."),
    ("Six Unions (六合)", "Unions", "Six pairs of Earthly Branches that pair into one element: Zi-Chou, Yin-Hai, Mao-Xu, Chen-You, Si-Shen, Wu-Wei."),
    ("Three Combinations (三合)", "Unions", "Four triads forming powerful elemental forces: Shen-Zi-Chen (Water), Hai-Mao-Wei (Wood), Yin-Wu-Xu (Fire), Si-You-Chou (Metal)."),
    ("Directional Combination (方合)", "Unions", "Three branches of the same season combining: Yin-Mao-Chen (Spring Wood), Si-Wu-Wei (Summer Fire), Shen-You-Xu (Autumn Metal), Hai-Zi-Chou (Winter Water)."),
    ("Clash (沖)", "Unions", "Diagonally-opposed branch pairs that clash: Zi-Wu, Chou-Wei, Yin-Shen, Mao-You, Chen-Xu, Si-Hai. Indicate change and conflict."),
    ("Penalty (刑)", "Unions", "Branch frictions causing conflict — three-way penalties like Yin-Si-Shen, Chou-Xu-Wei, and the self-penalty Zi-Mao."),
    ("Damage (破)", "Unions", "Minor branch misalignments, weaker than penalties."),
    ("Harm (害)", "Unions", "Subtle branch harms — petty disturbances, envy."),

    # ─── Luck ───
    ("Daewoon (大運)", "Luck", "The Great Luck cycle — a stem-branch period lasting 10 years that overlays the chart. Forward for Yang-Male/Yin-Female, reverse for Yin-Male/Yang-Female."),
    ("Sewoon (歲運)", "Luck", "The yearly luck — interaction between the annual stem-branch and the natal chart."),
    ("Wolwoon (月運)", "Luck", "The monthly luck — changes by solar term."),
    ("Iljin (日辰)", "Luck", "The daily stem-branch — used for daily fortune readings."),

    # ─── 24 Solar Terms (selected) ───
    ("24 Solar Terms", "Solar Terms", "An East Asian astronomical calendar dividing the year into 24 segments, each set by the sun's ecliptic position at 15-degree intervals."),
    ("Ipchun (立春)", "Solar Terms", "~February 4 — start of spring and start of the Saju year."),
    ("Usu (雨水)", "Solar Terms", "~February 19 — snow turns to rain."),
    ("Gyeongchip (驚蟄)", "Solar Terms", "~March 6 — start of Mao month."),
    ("Chunbun (春分)", "Solar Terms", "~March 21 — spring equinox."),
    ("Cheongmyeong (淸明)", "Solar Terms", "~April 5 — start of Chen month."),
    ("Gogu (穀雨)", "Solar Terms", "~April 20 — grain rains."),
    ("Ipha (立夏)", "Solar Terms", "~May 6 — start of summer and Si month."),
    ("Soman (小滿)", "Solar Terms", "~May 21 — grain is full."),
    ("Mangjong (芒種)", "Solar Terms", "~June 6 — start of Wu month."),
    ("Haji (夏至)", "Solar Terms", "~June 21 — summer solstice."),
    ("Soseo (小暑)", "Solar Terms", "~July 7 — start of Wei month."),
    ("Daeseo (大暑)", "Solar Terms", "~July 23 — greatest heat."),
    ("Ipchu (立秋)", "Solar Terms", "~August 8 — start of autumn and Shen month."),
    ("Cheoseo (處暑)", "Solar Terms", "~August 23 — heat ends."),
    ("Baekro (白露)", "Solar Terms", "~September 8 — start of You month."),
    ("Chubun (秋分)", "Solar Terms", "~September 23 — autumn equinox."),
    ("Hanro (寒露)", "Solar Terms", "~October 8 — start of Xu month."),
    ("Sanggang (霜降)", "Solar Terms", "~October 23 — first frost."),
    ("Ipdong (立冬)", "Solar Terms", "~November 7 — start of winter and Hai month."),
    ("Soseol (小雪)", "Solar Terms", "~November 22 — first snow."),
    ("Daeseol (大雪)", "Solar Terms", "~December 7 — start of Zi month."),
    ("Dongji (冬至)", "Solar Terms", "~December 22 — winter solstice."),
    ("Sohan (小寒)", "Solar Terms", "~January 6 — start of Chou month."),
    ("Daehan (大寒)", "Solar Terms", "~January 20 — greatest cold."),

    # ─── Spirits / Special Stars ───
    ("Hidden Stems (地藏干)", "Advanced", "Stems hidden inside each branch — each branch carries multiple secondary stems."),
    ("Gongmang (空亡)", "Spirits", "An empty position in the 60-pillar table — weakens the affected domain."),
    ("Dohwa-sal (桃花殺)", "Spirits", "The Peach Blossom star — strong romantic magnetism."),
    ("Yeokma-sal (驛馬殺)", "Spirits", "The Horse star — movement, travel, frequent change."),
    ("Hwagae-sal (華蓋殺)", "Spirits", "The Canopy star — art, religion, scholarship, solitude."),
    ("Cheonul-gwiin (天乙貴人)", "Spirits", "The Heavenly Noble — helpers in times of crisis."),
    ("Munchang-gwiin (文昌貴人)", "Spirits", "Scholarly Noble — luck in study and exams."),
    ("Baekho-sal (白虎殺)", "Spirits", "The White Tiger — sudden accidents or violent changes."),
    ("Goegang-sal (魁罡殺)", "Spirits", "Strong charisma and stubborn pride — major figure or major hardship."),
    ("Yangin-sal (羊刃殺)", "Spirits", "Sharp Blade — excessive strength of the day stem with potential for both decision and recklessness."),

    # ─── Schools ───
    ("Ziping Myeongri", "Schools", "Day-stem-centered school of Chinese fortune-telling codified in the Song Dynasty by Xu Ziping. The mainstream method today."),
    ("Qiongtong Baojian (窮通寶鑑)", "Schools", "A classical text emphasizing 'climate adjustment' — taking the day stem's seasonal weather as the starting point of interpretation."),
    ("Ziwei Doushu (紫微斗數)", "Schools", "A separate East Asian astrological system based on star placements, distinct from Saju."),
    ("Qimen Dunjia (奇門遁甲)", "Schools", "A divination system using direction and time grids."),
    ("Dangsaju (唐四柱)", "Schools", "A Tang-Dynasty-style folk Saju reading using picture cards — more popular than scholarly."),

    # ─── Time / Late-Zi ───
    ("Late-Zi Hour (夜子時)", "Advanced", "The Zi hour between 23:00 and 00:00 — by one school, a birth here uses the next day's day pillar."),
    ("Early-Zi Hour (朝子時)", "Advanced", "The Zi hour between 00:00 and 01:00 — the day pillar stays the same."),
    ("True Solar Time", "Advanced", "Actual sun-position time corrected for longitude. Seoul and Busan differ by about two minutes."),

    # ─── Pattern ───
    ("Gyeokguk (格局)", "Advanced", "The overall pattern of a Saju, named by the strongest Ten God in the month branch (e.g., Direct Officer pattern)."),
    ("Yongshin (用神)", "Advanced", "The 'useful element' — the single most important character balancing the chart, used to judge luck."),
    ("Gisin (忌神)", "Advanced", "Enemy element — what weakens Yongshin. Bad-luck times bring this in."),
    ("Huishin (喜神)", "Advanced", "Helper element — supports Yongshin. Good-luck times bring this in."),
    ("Joohu (調候)", "Advanced", "Climate adjustment — balancing the cold or hot tendency of a chart with the opposite element."),
]

CATEGORIES_EN = []
for _, cat, _ in GLOSSARY_EN:
    if cat not in CATEGORIES_EN:
        CATEGORIES_EN.append(cat)
