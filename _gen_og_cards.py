"""60갑자 일주별 OG 공유 카드 PNG + 기본 OG 1장 생성 (PIL).

Windows의 시스템 폰트(맑은고딕/굴림)를 사용해 한글·한자를 직접 그린다.
출력: static/img/og/pillar-{0..59}.png + static/img/og-default.png (1200x630)
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw, ImageFont
from saju import data as D
from saju.interpreter import DAY_PILLAR_INTERPRETATIONS

OUT_DIR = os.path.join(ROOT, "static", "img", "og")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOT, "static", "img"), exist_ok=True)

# Windows 한글/한자 폰트 후보들
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgunbd.ttf",  # 맑은고딕 Bold
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\NanumGothicExtraBold.ttf",
    r"C:\Windows\Fonts\BatangChe.ttc",
    r"C:\Windows\Fonts\gulim.ttc",
]
SERIF_CANDIDATES = [
    r"C:\Windows\Fonts\HMKMRHD.TTF",   # 한양해서
    r"C:\Windows\Fonts\batang.ttc",
    r"C:\Windows\Fonts\malgunbd.ttf",
]


def find_font(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


FONT_SANS = find_font(FONT_CANDIDATES)
FONT_SERIF = find_font(SERIF_CANDIDATES) or FONT_SANS

if not FONT_SANS:
    print("WARNING: 한글 폰트를 찾을 수 없습니다. 일부 글자가 깨질 수 있습니다.")
    FONT_SANS = "arial.ttf"
    FONT_SERIF = "arial.ttf"

print(f"Sans font:  {FONT_SANS}")
print(f"Serif font: {FONT_SERIF}")

ELEMENT_COLORS = {
    "목": ((74, 155, 110), (44, 93, 66)),
    "화": ((208, 74, 74), (124, 44, 44)),
    "토": ((195, 152, 69), (116, 89, 43)),
    "금": ((198, 205, 212), (121, 127, 134)),
    "수": ((74, 120, 200), (44, 72, 120)),
}

BG_DARK = (26, 15, 46)
ACCENT = (218, 165, 32)
LIGHT = (243, 238, 232)
MUTED = (185, 173, 196)


def gradient_bg(w, h, c1, c2):
    """대각선 그라데이션 배경."""
    img = Image.new("RGB", (w, h), c1)
    px = img.load()
    for y in range(h):
        t = y / h
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        for x in range(w):
            # 약간 대각선 효과
            t2 = (x / w) * 0.3 + t * 0.7
            r2 = int(c1[0] * (1 - t2) + c2[0] * t2)
            g2 = int(c1[1] * (1 - t2) + c2[1] * t2)
            b2 = int(c1[2] * (1 - t2) + c2[2] * t2)
            px[x, y] = (r2, g2, b2)
    return img


def gen_pillar_card(idx):
    info = DAY_PILLAR_INTERPRETATIONS.get(idx)
    if not info:
        return None
    name_kr = D.HEAVENLY_STEMS_KR[idx % 10] + D.EARTHLY_BRANCHES_KR[idx % 12]
    name_hanja = D.HEAVENLY_STEMS[idx % 10] + D.EARTHLY_BRANCHES[idx % 12]
    element = D.ELEMENTS_KR[D.STEM_ELEMENT[idx % 10]]
    headline = info[1]

    fg, fg_dark = ELEMENT_COLORS[element]
    img = gradient_bg(1200, 630, BG_DARK, fg_dark)
    draw = ImageDraw.Draw(img)

    # 폰트 로딩
    f_sub = ImageFont.truetype(FONT_SANS, 28)
    f_num = ImageFont.truetype(FONT_SERIF, 42)
    f_huge = ImageFont.truetype(FONT_SERIF, 200)
    f_big = ImageFont.truetype(FONT_SERIF, 64)
    f_med = ImageFont.truetype(FONT_SANS, 32)
    f_small = ImageFont.truetype(FONT_SANS, 22)
    f_mark = ImageFont.truetype(FONT_SERIF, 56)

    draw.text((80, 80), "사주명리 · 60갑자 일주", font=f_sub, fill=(LIGHT[0], LIGHT[1], LIGHT[2], 180))
    draw.text((80, 130), f"#{idx + 1:02d}", font=f_num, fill=ACCENT)
    draw.text((80, 195), name_hanja, font=f_huge, fill=fg)
    draw.text((80, 425), f"{name_kr} 일주", font=f_big, fill=LIGHT)
    # headline은 길 수 있어 줄바꿈
    head = headline if len(headline) <= 32 else headline[:30] + "..."
    draw.text((80, 510), head, font=f_med, fill=LIGHT)
    draw.text((80, 580), "tarofortune.pythonanywhere.com", font=f_small, fill=MUTED)
    draw.text((1075, 95), "命", font=f_mark, fill=ACCENT)

    return img


def gen_default_card():
    img = gradient_bg(1200, 630, BG_DARK, (61, 46, 94))
    draw = ImageDraw.Draw(img)
    f_mark = ImageFont.truetype(FONT_SERIF, 240)
    f_title = ImageFont.truetype(FONT_SERIF, 84)
    f_sub = ImageFont.truetype(FONT_SANS, 36)
    f_lead = ImageFont.truetype(FONT_SANS, 26)
    f_url = ImageFont.truetype(FONT_SANS, 22)

    # 命 가운데
    draw.text((600, 200), "命", font=f_mark, fill=ACCENT, anchor="mm")
    draw.text((600, 380), "사주명리", font=f_title, fill=LIGHT, anchor="mm")
    draw.text((600, 460), "운명의 설계도", font=f_sub, fill=LIGHT, anchor="mm")
    draw.text((600, 525), "1,800년 동양철학으로 풀어드리는 무료 정통 사주",
              font=f_lead, fill=MUTED, anchor="mm")
    draw.text((600, 590), "tarofortune.pythonanywhere.com", font=f_url, fill=ACCENT, anchor="mm")
    return img


def main():
    # 기본 OG
    img = gen_default_card()
    path = os.path.join(ROOT, "static", "img", "og-default.png")
    img.save(path, "PNG", optimize=True)
    print(f"OK default → {path}")

    # 60갑자 일주별
    ok = 0
    for i in range(60):
        img = gen_pillar_card(i)
        if img is None:
            continue
        path = os.path.join(OUT_DIR, f"pillar-{i}.png")
        img.save(path, "PNG", optimize=True)
        ok += 1
    print(f"OK 일주별 카드 {ok}장 생성")

    # 기존 SVG 파일 정리
    for f in os.listdir(OUT_DIR):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT_DIR, f))
    default_svg = os.path.join(ROOT, "static", "img", "og-default.svg")
    if os.path.exists(default_svg):
        os.remove(default_svg)


if __name__ == "__main__":
    main()
