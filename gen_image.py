#!/usr/bin/env python3
"""Render the v2 entry image: a TV news broadcast frame, 1024x576.

Drawn entirely with PIL primitives (no photos, no network). All six
stories are the verified 17 November 2026 facts from the brief.
Layout (percent of 576 height): masthead 8%, breaking banner 7%,
middle 63% (schematic panel 66% + headline rail 34%), lead
lower-third 14%, ticker 8%. Safe margin 4% left/right.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 576
MARGIN = 41  # 4% safe margin
RIGHT = W - MARGIN

NAVY = (8, 21, 37)
PANEL = (13, 33, 56)
PANEL2 = (11, 29, 49)
RED = (200, 16, 46)
RED_DARK = (150, 10, 32)
WHITE = (255, 255, 255)
MIST = (215, 227, 244)
GREY = (169, 192, 222)
FAINT = (120, 145, 175)
YELLOW = (255, 213, 74)
LINE = (30, 58, 86)
SEA = (10, 32, 54)
SKY_TOP = (14, 42, 74)
SKY_BOT = (18, 54, 92)
STEEL = (216, 226, 238)
CABLE = (143, 166, 192)

BOLD_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
MED_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSans-CondensedMedium.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(size, bold=True):
    for p in (BOLD_PATHS if bold else MED_PATHS):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap, returns list of lines (max 2 expected by caller)."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def shrink_to_fit(draw, s, f, max_w, min_size, bold=True):
    """Reduce font size until the string fits max_w (never below min_size)."""
    size = f.size
    while size > min_size and text_w(draw, s, f) > max_w:
        size -= 1
        f = font(size, bold)
    return f


def draw_bridge(d, x0, y0, x1, y1):
    """Schematic Kerch-style suspension bridge inside (x0,y0)-(x1,y1)."""
    # Sky bands.
    d.rectangle([x0, y0, x1, y0 + (y1 - y0) * 2 // 5], fill=SKY_TOP)
    d.rectangle([x0, y0 + (y1 - y0) * 2 // 5, x1, y1], fill=SKY_BOT)
    # Sea.
    sea_y = y0 + int((y1 - y0) * 0.72)
    d.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for i, wy in enumerate((sea_y + 18, sea_y + 42, sea_y + 66)):
        d.line([x0 + 20 + i * 30, wy, x1 - 30 - i * 20, wy],
               fill=(38, 78, 120), width=2)
    # Bridge deck.
    deck_y = sea_y - 118
    d.rectangle([x0 + 8, deck_y, x1 - 8, deck_y + 10], fill=STEEL)
    # Towers.
    for tx in (x0 + 150, x0 + 400):
        d.rectangle([tx, deck_y - 108, tx + 14, deck_y + 10], fill=STEEL)
        d.rectangle([tx - 6, deck_y - 118, tx + 20, deck_y - 108], fill=STEEL)
    # Suspension cables: tower tops to deck.
    for tx in (x0 + 157, x0 + 407):
        for dx in range(x0 + 20, x1 - 10, 34):
            d.line([tx, deck_y - 108, dx, deck_y], fill=CABLE, width=2)
    # Vertical suspenders.
    for dx in range(x0 + 60, x1 - 20, 44):
        d.line([dx, deck_y - 46, dx, deck_y], fill=CABLE, width=1)
    # Explosion burst ON the deck, right of centre: a jagged star (not a
    # sun disc), small, with dark smoke rising above it.
    ex, ey = x0 + 470, deck_y + 4
    import math
    pts = []
    for k in range(24):
        r = 34 if k % 2 == 0 else 16
        a = math.radians(k * 15)
        pts.append((ex + int(r * math.cos(a)), ey + int(r * math.sin(a))))
    d.polygon(pts, fill=(255, 138, 0))
    pts2 = []
    for k in range(16):
        r = 20 if k % 2 == 0 else 9
        a = math.radians(k * 22.5 + 11)
        pts2.append((ex + int(r * math.cos(a)), ey + int(r * math.sin(a))))
    d.polygon(pts2, fill=(255, 213, 74))
    d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=(255, 255, 255))
    # Smoke puffs above the burst.
    for cx, cy, cr in ((ex - 26, ey - 44, 15), (ex + 4, ey - 62, 19),
                       (ex + 32, ey - 42, 13)):
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(90, 104, 122))
    # Small boat under the bridge, left.
    bx, by = x0 + 90, sea_y + 26
    d.polygon([(bx, by), (bx + 52, by), (bx + 42, by + 12), (bx + 10, by + 12)],
              fill=(120, 140, 165))
    d.line([bx + 26, by, bx + 26, by - 18], fill=(120, 140, 165), width=2)


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # ---------- Masthead: 8% (0-46) ----------
    f_word = font(25)
    d.rectangle([MARGIN, 11, MARGIN + 30, 35], fill=RED)
    d.text((MARGIN + 6, 12), "G", font=font(20), fill=WHITE)
    d.text((MARGIN + 38, 11), "GLOBAL 17", font=f_word, fill=WHITE)
    f_center = font(26)
    t = "WORLD TONIGHT"
    d.text(((W - text_w(d, t, f_center)) / 2, 9), t, font=f_center, fill=WHITE)
    f_date = font(22)
    t = "17 NOV 2026"
    d.text((RIGHT - text_w(d, t, f_date), 12), t, font=f_date, fill=WHITE)
    d.line([0, 46, W, 46], fill=LINE, width=1)

    # ---------- Breaking banner: 7% (46-86) ----------
    d.rectangle([0, 46, W, 86], fill=RED)
    f_brk = font(24)
    d.text((MARGIN, 53), "BREAKING", font=f_brk, fill=WHITE)
    bx = MARGIN + text_w(d, "BREAKING  ", f_brk)
    d.text((bx, 53), "•  KERCH BRIDGE HIT AGAIN", font=f_brk, fill=WHITE)

    # ---------- Middle: 63% (86-449) ----------
    mid_y0, mid_y1 = 86, 449
    panel_x1 = MARGIN + 622
    rail_x0 = panel_x1 + 12

    # Main schematic panel.
    d.rectangle([MARGIN, mid_y0, panel_x1, mid_y1], fill=PANEL)
    draw_bridge(d, MARGIN + 2, mid_y0 + 2, panel_x1 - 2, mid_y1 - 2)
    # Locator tab (yellow) + FILE bug (still image, not a live feed).
    d.rectangle([MARGIN + 14, mid_y0 + 12, MARGIN + 118, mid_y0 + 42], fill=YELLOW)
    d.text((MARGIN + 24, mid_y0 + 15), "CRIMEA", font=font(19), fill=(0, 0, 0))
    d.rectangle([panel_x1 - 74, mid_y0 + 12, panel_x1 - 14, mid_y0 + 42],
                fill=(20, 20, 20))
    d.rectangle([panel_x1 - 74, mid_y0 + 12, panel_x1 - 14, mid_y0 + 42],
                outline=(150, 150, 150), width=1)
    d.text((panel_x1 - 64, mid_y0 + 15), "FILE", font=font(19), fill=WHITE)
    # Caption strip inside the panel bottom.
    d.rectangle([MARGIN, mid_y1 - 28, panel_x1, mid_y1], fill=(5, 13, 24))
    d.text((MARGIN + 14, mid_y1 - 24), "KERCH STRAIT  •  SCHEMATIC ILLUSTRATION",
           font=font(14, bold=False), fill=GREY)

    # Headline rail: stories 02-06.
    stories = [
        ("02", "TANKERS STRUCK NEAR HORMUZ",
         "Mine hits tankers; third US carrier arrives"),
        ("03", "XI, TRUMP, PUTIN SUMMIT SET",
         "First three-way summit, Thursday in Shenzhen"),
        ("04", "JPMORGAN OUTAGE HITS ONLINE BANKING",
         "Glitch hits online banking; Zelle affected"),
        ("05", "PENTAGON FAILS NINTH STRAIGHT AUDIT",
         "Ninth straight year; $4.8 trillion unverified"),
        ("06", "EUROPEAN COUNTRIES PLAN RWANDA RETURN HUB",
         "Five European states plan hub for rejected seekers"),
    ]
    rail_w = RIGHT - rail_x0
    item_h = (mid_y1 - mid_y0) / 5.0
    f_num = font(18)
    for i, (num, head, sub) in enumerate(stories):
        iy = mid_y0 + int(i * item_h)
        if i:
            d.line([rail_x0, iy, RIGHT, iy], fill=LINE, width=1)
        # Number + headline (max 2 lines), supporting line full rail width.
        d.text((rail_x0, iy + 8), num, font=f_num, fill=RED)
        hx = rail_x0 + 34
        hw = RIGHT - hx
        f_head = font(21)
        lines = wrap(d, head, f_head, hw)
        while len(lines) > 2 and f_head.size > 17:
            f_head = font(f_head.size - 1)
            lines = wrap(d, head, f_head, hw)
        y = iy + 5
        for ln in lines[:2]:
            d.text((hx, y), ln, font=f_head, fill=WHITE)
            y += f_head.size + 3
        f_sub = font(16, bold=False)
        f_sub = shrink_to_fit(d, sub, f_sub, rail_w, 13, bold=False)
        d.text((rail_x0, iy + int(item_h) - 22), sub, font=f_sub, fill=GREY)

    # ---------- Lead lower-third: 14% (449-530) ----------
    d.rectangle([0, 449, W, 530], fill=PANEL2)
    d.rectangle([0, 449, 8, 530], fill=RED)
    d.text((MARGIN + 16, 452), "RUSSIA–UKRAINE WAR", font=font(15),
           fill=YELLOW)
    f_lead = font(37)
    d.text((MARGIN + 16, 466), "KERCH BRIDGE HIT AGAIN", font=f_lead,
           fill=WHITE)
    f_leadsub = font(17, bold=False)
    d.text((MARGIN + 16, 506), "Ukraine strikes Crimea bridge; Russia strikes Kyiv bridges",
           font=f_leadsub, fill=MIST)

    # ---------- Ticker: 8% (530-576) ----------
    d.rectangle([0, 530, W, 576], fill=(5, 13, 24))
    d.line([0, 530, W, 530], fill=RED, width=3)
    d.rectangle([MARGIN, 537, MARGIN + 168, 569], fill=RED)
    f_tab = font(17)
    t = "WORLD UPDATE"
    d.text((MARGIN + (168 - text_w(d, t, f_tab)) / 2, 541), t,
           font=f_tab, fill=WHITE)
    f_tick = font(17, bold=False)
    tick = "Xi, Trump and Putin meet Thursday in Shenzhen in the first three-way summit."
    f_tick = shrink_to_fit(d, tick, f_tick, RIGHT - (MARGIN + 184), 14,
                           bold=False)
    d.text((MARGIN + 184, 542), tick, font=f_tick, fill=WHITE)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")
    # Thumbnail check artefact (not part of the submission).
    img.resize((480, 270)).save("/tmp/news-v2-thumb.png")
    print("thumbnail saved /tmp/news-v2-thumb.png")


if __name__ == "__main__":
    main()
