"""사주 결과 공유용 동적 OG 카드 생성 (1200×630)."""
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from . import data as D
from .interpreter import DAY_PILLAR_INTERPRETATIONS
from .interpreter_en import DAY_PILLAR_INTERPRETATIONS_EN

# 폰트 경로 — PythonAnywhere(리눅스)에서도 동작하도록 폴백
FONT_KR_SERIF_LINUX = "/usr/share/fonts/truetype/nanum/NanumMyeongjoBold.ttf"
FONT_KR_SANS_LINUX = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"
FONT_LATIN_BOLD_LINUX = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_LATIN_REG_LINUX = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Windows 폴백
FONT_KR_SERIF_WIN = r"C:\Windows\Fonts\HMKMRHD.TTF"
FONT_KR_SANS_WIN = r"C:\Windows\Fonts\malgunbd.ttf"
FONT_LATIN_BOLD_WIN = r"C:\Windows\Fonts\arialbd.ttf"
FONT_LATIN_REG_WIN = r"C:\Windows\Fonts\arial.ttf"


def _f(size: int, want="kr_serif"):
    candidates = {
        "kr_serif": [FONT_KR_SERIF_LINUX, FONT_KR_SERIF_WIN],
        "kr_sans": [FONT_KR_SANS_LINUX, FONT_KR_SANS_WIN],
        "latin_bold": [FONT_LATIN_BOLD_LINUX, FONT_LATIN_BOLD_WIN],
        "latin_reg": [FONT_LATIN_REG_LINUX, FONT_LATIN_REG_WIN],
    }
    for p in candidates.get(want, []):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


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


def _gradient_bg(w, h, c1, c2):
    img = Image.new("RGB", (w, h), c1)
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / w) * 0.3 + (y / h) * 0.7
            r = int(c1[0] * (1 - t) + c2[0] * t)
            g = int(c1[1] * (1 - t) + c2[1] * t)
            b = int(c1[2] * (1 - t) + c2[2] * t)
            px[x, y] = (r, g, b)
    return img


def render_result_card(year_pillar, month_pillar, day_pillar, hour_pillar,
                       day_idx: int, lang: str = "ko", name: str = "") -> bytes:
    """사주 결과 카드 PNG 바이트 반환. 1200×630."""
    is_en = (lang == "en")
    if is_en:
        info = DAY_PILLAR_INTERPRETATIONS_EN.get(day_idx)
    else:
        info = DAY_PILLAR_INTERPRETATIONS.get(day_idx)
    if not info:
        info = ("?", "Unknown", "")
    headline_text = info[1]
    pillar_name = info[0]

    element_ko = D.ELEMENTS_KR[D.STEM_ELEMENT[day_idx % 10]]
    fg, fg_dark = ELEMENT_COLORS[element_ko]
    img = _gradient_bg(1200, 630, BG_DARK, fg_dark)
    draw = ImageDraw.Draw(img)

    # 상단 좌측 — 사이트 마크
    draw.text((50, 40), "命" if is_en else "사주명리",
              font=_f(40, "kr_serif"), fill=ACCENT)
    if name:
        draw.text((50, 90), (f"{name}'s reading" if is_en else f"{name}님의 사주"),
                  font=_f(26, "kr_sans"), fill=MUTED)

    # 좌측 — 4 기둥
    pillars = [(year_pillar, "Y" if is_en else "년"),
               (month_pillar, "M" if is_en else "월"),
               (day_pillar, "D" if is_en else "일"),
               (hour_pillar, "H" if is_en else "시")]
    x0 = 50
    y0 = 170
    box_w = 110
    box_h = 130
    gap = 20
    for i, (p, label) in enumerate(pillars):
        if p is None:
            continue
        x = x0 + i * (box_w + gap)
        # 박스 외곽
        draw.rounded_rectangle([x, y0, x + box_w, y0 + box_h], radius=12,
                               outline=fg, width=3)
        # 라벨
        draw.text((x + box_w // 2, y0 + 18), label, font=_f(20, "latin_reg"),
                  fill=MUTED, anchor="mm")
        # 한자
        hanja = D.HEAVENLY_STEMS[p["stem"]] + D.EARTHLY_BRANCHES[p["branch"]]
        draw.text((x + box_w // 2, y0 + 80), hanja, font=_f(54, "kr_serif"),
                  fill=LIGHT, anchor="mm")

    # 우측 — 일주 메인
    rx = 660
    draw.text((rx, 170), ("Day Pillar" if is_en else "일주"),
              font=_f(28, "latin_reg"), fill=MUTED)
    # 일주명
    draw.text((rx, 220), pillar_name, font=_f(48, "kr_serif" if not is_en else "latin_bold"),
              fill=ACCENT)
    # 헤드라인 wrap
    f_head = _f(26, "kr_sans" if not is_en else "latin_reg")
    words = headline_text.split()
    lines = []
    cur = ""
    max_w = 1200 - rx - 30
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=f_head)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    y = 290
    for line in lines[:5]:
        draw.text((rx, y), line, font=f_head, fill=LIGHT)
        y += 38

    # 하단 — URL
    url_text = "tarofortune.pythonanywhere.com" + ("/en" if is_en else "")
    draw.text((600, 580), url_text, font=_f(22, "latin_reg"), fill=MUTED, anchor="mm")
    draw.text((1130, 580), "命", font=_f(60, "kr_serif"), fill=ACCENT, anchor="mm")

    buf = BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()
