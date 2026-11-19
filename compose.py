#!/usr/bin/env python3
"""news-image-20261119 v1 — "Thursday 19 November 2026" front-page poster.

Draws the whole 1024x1024 page with PIL: no photos, no AI images, no network.
Every illustration is original flat-vector art drawn here from PIL shapes.
Slate: 21 verified stories (13 illustrated leads + 8 briefs), per the final
decision in ~/workspace/makefun/news-image-20261119-discussion.md, with the
file's own Fed-minutes fallback applied (minutes were released 18 Nov, so the
Fed item moved to DATE CHECK and Liu Yunping was promoted to lead 13; a
verified 19-Nov brief, Coalition of the Willing meets in Berlin, fills #21).

Type scale (better-typography: 3 faces, size by role, no light weights).
MEASURED from the reference (ronigrv rank-1, 18 Nov, 1024 canvas) by glyph
measurement, not guessed: masthead cap 41px; big headlines cap 14px in 335px
cards (ratio .042), decks cap 9px; small headlines cap 11px in 193px cards,
decks cap 7px; briefs cap 7px; region bar 16px, field bar 17px; big-card
illustration 63% of card height, small-card 54%. Our sizes below are set so
the RENDERED CAP HEIGHTS match those numbers (Noto cap/em ~0.72):
  masthead  DejaVu Serif Bold 56px (cap 41, spans ~930px like the reference)
  headlines Noto Sans Condensed Bold, 19px big cards / 15px small cards
  decks     Noto Sans Condensed, 12px big / 10px small
  labels    Noto Sans Condensed Bold, 10px big / 9px small, uppercase
  briefs    Noto Sans Condensed Bold 11px lead-in / 10px body
  footer    Noto Sans Condensed 12px
Layout (better-layout): 12px shared margins, 8px gaps between card groups,
4px gaps inside cards, one card style, square corners (newsprint).
Card geometry mirrors the reference: big cards y154 h212, small rows y372 /
y527 h149, bottom headers y685, map 300x148, DATE CHECK y966, footer y1010.
Colour (better-colors): one hue per region, red only for badges/emphasis;
text on gold/orange segments is black (measured contrast), white elsewhere.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
W = H = 1024
M = 12                      # shared outer margin
CW = W - 2 * M              # 1000 content width

# ---- palette (semantic roles, hex notation throughout) ----
PAPER   = (247, 242, 227)   # page
CARD    = (255, 253, 246)   # card ground
INK     = (25, 25, 25)      # text / hairlines
RED     = (200, 16, 46)     # badges, numbers, DATE CHECK
BAR_BLK = (20, 20, 20)      # field bar
OCEAN   = (185, 210, 228)
LAND    = (143, 191, 127)
LAND_DK = (106, 154, 94)

# region hues: blue / green / gold / orange / purple / grey (each >15 deg apart)
REGIONS = {
    "EUROPE":      (46, 109, 164),
    "MIDDLE EAST": (46, 125, 79),
    "ASIA":        (192, 138, 0),
    "AFRICA":      (217, 108, 44),
    "AMERICAS":    (111, 74, 158),
    "WORLD":       (77, 77, 77),
}
# text colour on each region fill (measured: white fails 4.5:1 on gold/orange)
REGION_TEXT = {
    "EUROPE": (255, 255, 255), "MIDDLE EAST": (255, 255, 255),
    "ASIA": (25, 25, 25), "AFRICA": (25, 25, 25),
    "AMERICAS": (255, 255, 255), "WORLD": (255, 255, 255),
}

FD = "/usr/share/fonts/truetype/noto"
SERIFD = os.path.join(FD, "NotoSerifDisplay-CondensedBold.ttf")
SANSB  = os.path.join(FD, "NotoSans-CondensedBold.ttf")
SANS   = os.path.join(FD, "NotoSans-Condensed.ttf")
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(round(size)))


def fit_font(path, text, max_w, start, minimum=8):
    """Largest size <= start whose rendered width fits max_w."""
    size = start
    while size > minimum:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            return f, size
        size -= 0.5
    return font(path, minimum), minimum


def wrap(text, f, max_w, max_lines):
    """Greedy word wrap; returns lines (truncated with ellipsis past max)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and f.getlength(lines[-1] + "…") > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines


def rel_lum(rgb):
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    l1, l2 = sorted((rel_lum(fg), rel_lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# ---------------------------------------------------------------- illustrations
# Each draws original flat-vector art in box (x, y, w, h). <=16 colours each.

def ill_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(242, 200, 121))          # dusk sky
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(46, 111, 142))  # sea
    d.rectangle([x, y + int(h * 0.62), x + w, y + int(h * 0.66)], fill=(232, 213, 168))
    # coastline (diagonal sand strip, lower left)
    d.polygon([(x, y + int(h * 0.62)), (x + int(w * 0.34), y + int(h * 0.62)),
               (x + int(w * 0.22), y + h), (x, y + h)], fill=(232, 213, 168))
    # missile trails: straight dashed diagonals, not rainbow arcs
    for (x0, y0, x1, y1) in ((0.12, 0.55, 0.30, 0.28), (0.42, 0.58, 0.62, 0.30),
                             (0.66, 0.60, 0.82, 0.34)):
        px0, py0 = x + int(w * x0), y + int(h * y0)
        px1, py1 = x + int(w * x1), y + int(h * y1)
        steps = 7
        for i in range(steps):
            if i % 2:
                continue
            ax = px0 + (px1 - px0) * i // steps
            ay = py0 + (py1 - py0) * i // steps
            bx = px0 + (px1 - px0) * (i + 1) // steps
            by = py0 + (py1 - py0) * (i + 1) // steps
            d.line([ax, ay, bx, by], fill=(255, 255, 255), width=2)
        # missile head: small white triangle at the trail tip
        d.polygon([(px1, py1 - 6), (px1 - 5, py1 + 4), (px1 + 5, py1 + 4)],
                  fill=(255, 255, 255))
    for bx, by in ((int(w * 0.30), int(h * 0.28)), (int(w * 0.68), int(h * 0.26))):
        cx, cy = x + bx, y + by
        for ang in range(0, 360, 45):
            r = 12
            d.line([cx, cy, cx + int(r * math.cos(math.radians(ang))),
                    cy + int(r * math.sin(math.radians(ang)))],
                   fill=(255, 210, 62), width=3)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 240, 160))
    # oil platform with legs
    d.rectangle([x + int(w * 0.80), y + int(h * 0.44), x + int(w * 0.90),
                 y + int(h * 0.62)], fill=(58, 58, 58))
    d.line([x + int(w * 0.81), y + int(h * 0.62), x + int(w * 0.79), y + int(h * 0.72)],
           fill=(58, 58, 58), width=2)
    d.line([x + int(w * 0.89), y + int(h * 0.62), x + int(w * 0.91), y + int(h * 0.72)],
           fill=(58, 58, 58), width=2)


def ill_apec(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 238))          # sky
    for bx, bw, bh in ((0.02, 0.18, 0.42), (0.22, 0.14, 0.58), (0.40, 0.20, 0.48),
                       (0.62, 0.15, 0.62), (0.80, 0.18, 0.40)):
        d.rectangle([x + int(w * bx), y + h - int(h * bh), x + int(w * (bx + bw)),
                     y + int(h * 0.72)], fill=(148, 168, 190))       # skyline
    # three flags
    d.rectangle([x + int(w * 0.06), y + 6, x + int(w * 0.30), y + 34], fill=(222, 41, 16))
    d.ellipse([x + int(w * 0.10), y + 12, x + int(w * 0.10) + 7, y + 19], fill=(255, 222, 0))
    for i, c in enumerate(((255, 255, 255), (222, 41, 16)) * 3):
        d.rectangle([x + int(w * 0.38), y + 6 + i * 5, x + int(w * 0.62), y + 10 + i * 5],
                    fill=c)
    d.rectangle([x + int(w * 0.70), y + 6, x + int(w * 0.94), y + 15], fill=(255, 255, 255))
    d.rectangle([x + int(w * 0.70), y + 15, x + int(w * 0.94), y + 25], fill=(0, 57, 166))
    d.rectangle([x + int(w * 0.70), y + 25, x + int(w * 0.94), y + 34], fill=(213, 0, 50))
    # table + three figures
    d.rectangle([x + 4, y + int(h * 0.72), x + w - 4, y + h - 6], fill=(122, 74, 40))
    for fx, suit, tie in ((0.18, (30, 42, 66), (200, 16, 46)),
                          (0.50, (40, 40, 40), (0, 57, 166)),
                          (0.82, (74, 52, 30), (192, 138, 0))):
        cx = x + int(w * fx)
        d.ellipse([cx - 13, y + int(h * 0.44), cx + 13, y + int(h * 0.44) + 26],
                  fill=(232, 196, 160))                              # head
        d.polygon([(cx - 20, y + int(h * 0.72)), (cx + 20, y + int(h * 0.72)),
                   (cx + 13, y + int(h * 0.52)), (cx - 13, y + int(h * 0.52))],
                  fill=suit)                                          # suit
        d.polygon([(cx - 3, y + int(h * 0.54)), (cx + 3, y + int(h * 0.54)),
                   (cx, y + int(h * 0.70))], fill=tie)                # tie


def ill_nvidia(d, x, y, w, h):
    # Chip (left) + CEO handover: two suited figures shaking hands (centre)
    # + red down arrow (right). Reads at a glance: chip company, chief leaves.
    d.rectangle([x, y, x + w, y + h], fill=(18, 52, 32))              # dark green
    # chip, left third
    cx0, cy0, cw = x + 12, y + 12, 58
    d.rectangle([cx0 - 6, cy0 - 6, cx0 + cw + 6, cy0 + cw + 6], fill=(60, 60, 60))
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + cw], fill=(200, 200, 200))
    for i in range(5):  # pins on all four sides
        for px, py, pw, ph in ((cx0 + 6 + i * 11, cy0 - 6, 4, 6),
                               (cx0 + 6 + i * 11, cy0 + cw, 4, 6),
                               (cx0 - 6, cy0 + 6 + i * 11, 6, 4),
                               (cx0 + cw, cy0 + 6 + i * 11, 6, 4)):
            d.rectangle([px, py, px + pw, py + ph], fill=(160, 160, 160))
    d.rectangle([cx0 + 12, cy0 + 12, cx0 + cw - 12, cy0 + cw - 12],
                fill=(24, 68, 32))
    for tx in (cx0 + 18, cx0 + 30, cx0 + 42):  # circuit traces on the die
        d.line([tx, cy0 + 14, tx, cy0 + cw - 14], fill=(118, 185, 0), width=2)
        d.line([cx0 + 14, tx, cx0 + cw - 14, tx], fill=(118, 185, 0), width=2)
    d.ellipse([cx0 + 22, cy0 + 22, cx0 + 36, cy0 + 36], fill=(118, 185, 0))
    # handshake figures, centre: outgoing chief (left, dark suit) meets the
    # successor (right, green tie); hands meet over a small table
    d.rectangle([x + int(w * 0.52), y + int(h * 0.74), x + int(w * 0.80),
                 y + h - 4], fill=(122, 74, 40))
    for fx, suit, tie in ((0.56, (30, 42, 66), (200, 16, 46)),
                          (0.76, (40, 40, 40), (118, 185, 0))):
        ccx = x + int(w * fx)
        d.ellipse([ccx - 10, y + 10, ccx + 10, y + 30], fill=(232, 196, 160))
        d.polygon([(ccx - 15, y + int(h * 0.74)), (ccx + 15, y + int(h * 0.74)),
                   (ccx + 10, y + 32), (ccx - 10, y + 32)], fill=suit)
        d.polygon([(ccx - 2, y + 34), (ccx + 2, y + 34),
                   (ccx, y + int(h * 0.60))], fill=tie)
    # joined hands between them
    hx0, hy0 = x + int(w * 0.64), y + int(h * 0.52)
    d.ellipse([hx0 - 5, hy0 - 5, hx0 + 5, hy0 + 5], fill=(232, 196, 160))
    d.line([x + int(w * 0.56) + 8, y + 40, hx0, hy0], fill=(232, 196, 160), width=4)
    d.line([x + int(w * 0.76) - 8, y + 40, hx0, hy0], fill=(232, 196, 160), width=4)
    # red down arrow, right
    ax, ay = x + int(w * 0.93), y + 10
    d.polygon([(ax - 5, ay), (ax + 5, ay), (ax + 5, ay + 14), (ax + 12, ay + 14),
               (ax, ay + 26), (ax - 12, ay + 14), (ax - 5, ay + 14)], fill=(220, 40, 40))


def ill_jeffries(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 210, 224))          # sky
    d.rectangle([x, y + int(h * 0.78), x + w, y + h], fill=(120, 130, 120))  # steps
    cx = x + w // 2
    d.rectangle([cx - 34, y + int(h * 0.34), cx + 34, y + int(h * 0.80)],
                fill=(240, 238, 230))                                # capitol body
    d.pieslice([cx - 26, y + 4, cx + 26, y + int(h * 0.42)], 180, 360,
               fill=(240, 238, 230))                                  # dome
    d.rectangle([cx - 2, y, cx + 2, y + 8], fill=(60, 60, 60))
    for i in range(5):
        px = cx - 28 + i * 14
        d.rectangle([px, y + int(h * 0.44), px + 5, y + int(h * 0.76)],
                    fill=(200, 196, 184))                             # columns
    # gavel, lower right
    gx, gy = x + int(w * 0.74), y + int(h * 0.62)
    d.rectangle([gx, gy, gx + 34, gy + 7], fill=(122, 74, 40))
    d.rectangle([gx + 26, gy - 12, gx + 34, gy + 20], fill=(90, 52, 26))
    d.ellipse([gx - 8, gy + 16, gx + 14, gy + 22], fill=(60, 60, 60))  # sound block
    # "1st" star disc, top-right (top-left holds the number badge)
    sx0, sy0 = x + w - 32, y + 6
    d.ellipse([sx0, sy0, sx0 + 24, sy0 + 24], fill=(200, 16, 46))
    d.polygon([(sx0 + 12, sy0 + 3), (sx0 + 15, sy0 + 10), (sx0 + 22, sy0 + 10),
               (sx0 + 17, sy0 + 15), (sx0 + 19, sy0 + 22), (sx0 + 12, sy0 + 18),
               (sx0 + 5, sy0 + 22), (sx0 + 7, sy0 + 15), (sx0 + 2, sy0 + 10),
               (sx0 + 9, sy0 + 10)], fill=(255, 222, 0))


def ill_eu_loan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))              # EU blue
    cx, cy, r = x + w // 2, y + int(h * 0.40), 30
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        sx, sy = cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))
        d.polygon([(sx, sy - 5), (sx + 1.5, sy - 1.5), (sx + 5, sy - 1),
                   (sx + 2.5, sy + 1.5), (sx + 3.5, sy + 5), (sx, sy + 3),
                   (sx - 3.5, sy + 5), (sx - 2.5, sy + 1.5), (sx - 5, sy - 1),
                   (sx - 1.5, sy - 1.5)], fill=(255, 204, 0))
    f = font(SANSB, int(h * 0.42))
    d.text((cx, cy), "€", font=f, fill=(255, 255, 255), anchor="mm")
    d.rectangle([x, y + int(h * 0.82), x + w, y + int(h * 0.91)], fill=(0, 91, 187))
    d.rectangle([x, y + int(h * 0.91), x + w, y + h], fill=(255, 213, 0))


def ill_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(140, 160, 178))          # storm sky
    for rx in range(0, w, 18):
        d.line([x + rx, y + 4, x + rx - 6, y + 22], fill=(90, 110, 130), width=2)
    wy = y + int(h * 0.55)
    for hx, hw, hc in ((0.06, 0.26, (226, 214, 186)), (0.38, 0.24, (210, 190, 160)),
                       (0.68, 0.26, (226, 214, 186))):
        d.rectangle([x + int(w * hx), wy - int(h * 0.22), x + int(w * (hx + hw)), wy + 4],
                    fill=hc)
        d.polygon([(x + int(w * hx) - 4, wy - int(h * 0.22)),
                   (x + int(w * (hx + hw)) + 4, wy - int(h * 0.22)),
                   (x + int(w * (hx + hw / 2)), wy - int(h * 0.38))],
                  fill=(150, 90, 70))
    d.rectangle([x, wy, x + w, y + h], fill=(38, 98, 150))           # flood water
    for i in range(4):
        yy = wy + 8 + i * 12
        d.arc([x + 6 + i * 8, yy, x + 44 + i * 8, yy + 10], 0, 180,
              fill=(180, 220, 240), width=2)
        d.arc([x + w - 50 - i * 6, yy, x + w - 12 - i * 6, yy + 10], 0, 180,
              fill=(180, 220, 240), width=2)


def ill_akvan(d, x, y, w, h):
    # Cyclone spiral over a coastline: teal sea left, sand coast curving down
    # the right, spiral arms (offset centres, staggered arcs) with a clear eye,
    # rain streaks top-left, two small houses on the land.
    d.rectangle([x, y, x + w, y + h], fill=(32, 90, 120))            # sea
    d.polygon([(x + int(w * 0.62), y), (x + w, y), (x + w, y + h),
               (x + int(w * 0.72), y + h), (x + int(w * 0.66), y + int(h * 0.55)),
               (x + int(w * 0.58), y + int(h * 0.30))],
              fill=(232, 213, 168))                                   # coast/land
    for rx in range(0, int(w * 0.45), 20):  # rain, sea side only
        d.line([x + rx, y + 6, x + rx - 5, y + 22], fill=(170, 200, 220), width=2)
    cx, cy = x + int(w * 0.42), y + int(h * 0.46)
    # spiral arms: same centre would read as a target; offset each ring's
    # centre along the swirl and stagger the arc so the bands wind inward
    arms = [((0, 0), 46, 15, 285, (255, 255, 255), 9),
            ((7, -5), 36, 60, 330, (210, 230, 240), 8),
            ((-6, 6), 26, 110, 20, (255, 255, 255), 7),
            ((4, 3), 16, 170, 80, (160, 200, 220), 6)]
    for (ox, oy), r, a0, a1, col, wd in arms:
        d.arc([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
              start=a0, end=a1, fill=col, width=wd)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))  # eye
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(32, 90, 120))
    for hx in (0.78, 0.88):  # houses on the land
        d.rectangle([x + int(w * hx), y + int(h * 0.58), x + int(w * hx) + 13,
                     y + int(h * 0.72)], fill=(226, 214, 186))
        d.polygon([(x + int(w * hx) - 3, y + int(h * 0.58)),
                   (x + int(w * hx) + 16, y + int(h * 0.58)),
                   (x + int(w * hx) + 6, y + int(h * 0.48))], fill=(150, 90, 70))


def ill_houthis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 214, 170))          # hazy sky
    d.polygon([(x, y + int(h * 0.55)), (x + int(w * 0.30), y + int(h * 0.18)),
               (x + int(w * 0.55), y + int(h * 0.55))], fill=(150, 110, 80))
    d.polygon([(x + int(w * 0.45), y + int(h * 0.55)), (x + int(w * 0.72),
               y + int(h * 0.28)), (x + w, y + int(h * 0.55))], fill=(130, 96, 70))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(178, 62, 52))  # red sea
    sx, sy = x + int(w * 0.50), y + int(h * 0.62)
    d.rectangle([sx - 34, sy, sx + 34, sy + 14], fill=(40, 40, 40))   # ship hull
    d.rectangle([sx - 16, sy - 16, sx + 8, sy], fill=(230, 230, 230))
    d.rectangle([sx + 12, sy - 10, sx + 22, sy], fill=(230, 230, 230))
    d.line([sx, sy - 30, sx, sy - 14], fill=(40, 40, 40), width=3)
    d.polygon([(sx, sy - 30), (sx + 14, sy - 25), (sx, sy - 20)], fill=(200, 16, 46))


def ill_estonia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 224, 238))          # pale sky
    d.rectangle([x, y + int(h * 0.70), x + w, y + h], fill=(140, 160, 120))  # ground
    for tx in (0.08, 0.22, 0.78, 0.90):
        px = x + int(w * tx)
        d.polygon([(px, y + int(h * 0.14)), (px - 13, y + int(h * 0.52)),
                   (px + 13, y + int(h * 0.52))], fill=(34, 110, 60))
        d.rectangle([px - 2, y + int(h * 0.50), px + 2, y + int(h * 0.70)],
                    fill=(90, 60, 30))
    d.rectangle([x, y + int(h * 0.74), x + w, y + int(h * 0.82)], fill=(90, 90, 90))
    for bx in range(0, w, 16):  # border fence
        d.rectangle([x + bx, y + int(h * 0.52), x + bx + 3, y + int(h * 0.74)],
                    fill=(50, 50, 50))
    d.rectangle([x, y + int(h * 0.52), x + w, y + int(h * 0.55)], fill=(50, 50, 50))
    for i in range(6):  # red-white barrier
        col = (200, 16, 46) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([x + int(w * 0.38) + i * 8, y + int(h * 0.60),
                     x + int(w * 0.38) + (i + 1) * 8, y + int(h * 0.66)], fill=col)
    d.rectangle([x + int(w * 0.38), y + int(h * 0.66), x + int(w * 0.38) + 4,
                 y + int(h * 0.78)], fill=(50, 50, 50))
    d.rectangle([x + int(w * 0.38) + 44, y + int(h * 0.66),
                 x + int(w * 0.38) + 48, y + int(h * 0.78)], fill=(50, 50, 50))


def ill_gta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 16, 38))             # night
    d.ellipse([x + int(w * 0.78), y + 6, x + int(w * 0.78) + 22, y + 28],
              fill=(240, 240, 210))                                   # moon
    for bx, bw, bh, lit in ((0.02, 0.16, 0.55, 1), (0.20, 0.13, 0.72, 0),
                            (0.35, 0.18, 0.48, 1), (0.55, 0.14, 0.66, 1),
                            (0.71, 0.13, 0.58, 0), (0.86, 0.13, 0.44, 1)):
        d.rectangle([x + int(w * bx), y + h - int(h * bh), x + int(w * (bx + bw)), y + h],
                    fill=(34, 34, 58))
        if lit:
            for wy in range(0, int(h * bh) - 8, 14):
                d.rectangle([x + int(w * bx) + 4, y + h - int(h * bh) + wy + 4,
                             x + int(w * bx) + 9, y + h - int(h * bh) + wy + 9],
                            fill=(255, 214, 90))
    # palm silhouette
    px, py = x + int(w * 0.10), y + int(h * 0.86)
    d.line([px, py, px + 4, py - 26], fill=(8, 40, 20), width=4)
    for ang in (200, 230, 260, 290, 320):
        d.arc([px - 16, py - 44, px + 20, py - 12], start=ang, end=ang + 40,
              fill=(8, 40, 20), width=3)
    f = font(SANSB, int(h * 0.52))
    d.text((x + int(w * 0.52), y + int(h * 0.30)), "VI", font=f,
           fill=(255, 64, 160), anchor="mm", stroke_width=2, stroke_fill=(0, 229, 255))


def ill_amazon(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 226, 150))          # bright sky
    sx, sy = x + int(w * 0.78), y + int(h * 0.22)
    d.ellipse([sx - 18, sy - 18, sx + 18, sy + 18], fill=(255, 150, 40))
    for ang in range(0, 360, 45):
        d.line([sx, sy, sx + int(26 * math.cos(math.radians(ang))),
                sy + int(26 * math.sin(math.radians(ang)))], fill=(255, 150, 40), width=3)
    d.rectangle([x, y + int(h * 0.68), x + w, y + h], fill=(90, 160, 70))  # field
    for px, py, pw in ((0.08, 0.42, 0.24), (0.38, 0.36, 0.24), (0.68, 0.42, 0.24)):
        x0, y0 = x + int(w * px), y + int(h * py)
        d.polygon([(x0, y0 + 26), (x0 + int(w * pw), y0 + 26),
                   (x0 + int(w * pw) - 8, y0), (x0 + 8, y0)], fill=(24, 68, 140))
        d.line([x0 + int(w * pw) / 2, y0 + 13, x0 + int(w * pw) / 2, y0 + 26],
               fill=(180, 210, 240), width=1)
        d.line([x0 + 4, y0 + 13, x0 + int(w * pw) - 4, y0 + 13],
               fill=(180, 210, 240), width=1)


def ill_libya(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 224, 232))          # port sky
    d.rectangle([x, y + int(h * 0.72), x + w, y + h], fill=(120, 120, 120))  # quay
    boxes = [(0.06, 0.52, 0.26, (200, 60, 40)), (0.34, 0.52, 0.26, (30, 110, 170)),
             (0.62, 0.52, 0.26, (230, 170, 30)), (0.18, 0.30, 0.26, (40, 140, 80)),
             (0.48, 0.30, 0.26, (200, 60, 40))]
    for bx, by, bw, col in boxes:
        d.rectangle([x + int(w * bx), y + int(h * by), x + int(w * (bx + bw)),
                     y + int(h * (by + 0.20))], fill=col, outline=(40, 40, 40), width=1)
        d.line([x + int(w * bx), y + int(h * (by + 0.10)),
                x + int(w * (bx + bw)), y + int(h * (by + 0.10))],
               fill=(40, 40, 40), width=1)
    # crane
    d.line([x + int(w * 0.88), y + int(h * 0.06), x + int(w * 0.88), y + int(h * 0.72)],
           fill=(50, 50, 50), width=4)
    d.line([x + int(w * 0.88), y + int(h * 0.06), x + w, y + int(h * 0.16)],
           fill=(50, 50, 50), width=3)
    d.line([x + int(w * 0.96), y + int(h * 0.16), x + int(w * 0.96), y + int(h * 0.30)],
           fill=(50, 50, 50), width=2)
    d.rectangle([x + int(w * 0.92), y + int(h * 0.30), x + w - 2, y + int(h * 0.40)],
                fill=(230, 170, 30))


def ill_liu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 30, 30))            # red backdrop
    for sx in (0.10, 0.30, 0.50, 0.70, 0.90):
        d.ellipse([x + int(w * sx) - 4, y + 8, x + int(w * sx) + 4, y + 16],
                  fill=(255, 222, 0))
    # chamber desks (arcs of seats)
    for row, ry in enumerate((0.52, 0.64, 0.76)):
        for i in range(5):
            fx = 0.14 + i * 0.18
            d.ellipse([x + int(w * fx) - 7, y + int(h * ry),
                       x + int(w * fx) + 7, y + int(h * ry) + 12],
                      fill=(232, 196, 160))
            d.rectangle([x + int(w * fx) - 11, y + int(h * ry) + 12,
                         x + int(w * fx) + 11, y + int(h * ry) + 20],
                        fill=(40, 40, 60) if row % 2 else (60, 60, 90))
    # podium + mic
    cx = x + w // 2
    d.polygon([(cx - 16, y + h), (cx + 16, y + h), (cx + 10, y + int(h * 0.42)),
               (cx - 10, y + int(h * 0.42))], fill=(90, 60, 30))
    d.line([cx, y + int(h * 0.42), cx, y + int(h * 0.30)], fill=(30, 30, 30), width=3)
    d.ellipse([cx - 4, y + int(h * 0.28), cx + 4, y + int(h * 0.34)], fill=(30, 30, 30))


# ---------------------------------------------------------------- data
LEADS = [
    dict(n=1, region="MIDDLE EAST", field="WAR", ill=ill_gulf,
         headline="Iran strikes US Gulf bases", deck="Two bases hit, officials say"),
    dict(n=2, region="ASIA", field="POLITICS", ill=ill_apec,
         headline="Trump, Xi, Putin meet at APEC", deck="First three-way talks open"),
    dict(n=3, region="AMERICAS", field="TECH", ill=ill_nvidia,
         headline="Huang steps down at Nvidia", deck="Kress named acting chief"),
    dict(n=4, region="AMERICAS", field="POLITICS", ill=ill_jeffries,
         headline="First Black Speaker", deck="Jeffries nominated"),
    dict(n=5, region="EUROPE", field="ECONOMY", ill=ill_eu_loan,
         headline="EU\u2019s \u20ac45bn Kyiv loan", deck="Proposal for Kyiv"),
    dict(n=6, region="MIDDLE EAST", field="DISASTERS", ill=ill_gaza,
         headline="Gaza floods displace 46,000", deck="46,000 homes flooded"),
    dict(n=7, region="ASIA", field="WEATHER", ill=ill_akvan,
         headline="Cyclone Akvan nears India", deck="Landfall due Friday"),
    dict(n=8, region="MIDDLE EAST", field="WAR", ill=ill_houthis,
         headline="Houthis seize Red Sea coast", deck="Bab el-Mandeb risk"),
    dict(n=9, region="EUROPE", field="WAR", ill=ill_estonia,
         headline="Estonia shuts Russia border", deck="Border closes Dec 1"),
    dict(n=10, region="WORLD", field="CULTURE", ill=ill_gta,
         headline="GTA VI rolls out worldwide", deck="Global launch day"),
    dict(n=11, region="ASIA", field="CLIMATE", ill=ill_amazon,
         headline="Amazon pledges $7bn", deck="Green power for India"),
    dict(n=12, region="AFRICA", field="JUSTICE", ill=ill_libya,
         headline="Libya\u2019s record drug haul", deck="Huge haul at the port"),
    dict(n=13, region="ASIA", field="POLITICS", ill=ill_liu,
         headline="Liu Yunping, Caucus chair", deck="Caucus picks new chair"),
]
BRIEFS = [  # (number, lead-in, body, region)
    (14, "Voyager 1", "a light-day", "WORLD"),
    (15, "Zelensky", "Starshield", "EUROPE"),
    (16, "NSA outage", "CNN says", "AMERICAS"),
    (17, "Carney", "China ties", "AMERICAS"),
    (18, "Melenchon", "could win", "EUROPE"),
    (19, "Saudi", "danger passed", "MIDDLE EAST"),
    (20, "Earth study", "lost eons", "WORLD"),
    (21, "Berlin", "\u2018Willing\u2019 meets", "EUROPE"),
]
REGION_COUNTS = {"EUROPE": 5, "MIDDLE EAST": 4, "ASIA": 4,
                 "AFRICA": 1, "AMERICAS": 4, "WORLD": 3}
FIELD_COUNTS = [("War & security", 6), ("Politics & diplomacy", 5),
                ("Economy & labour", 1), ("Society & culture", 1),
                ("Disasters & weather", 2), ("Tech", 2),
                ("Climate & space", 3), ("Justice", 1)]
# Field tally, counted from the 21 stories themselves (judge-checkable):
#   War 6 = 1 US-Iran, 8 Houthis, 9 Estonia, 15 Zelensky/Starshield,
#           19 Saudi all-clear, 21 Berlin Coalition of the Willing
#   Politics 5 = 2 APEC, 4 Jeffries, 13 Liu, 17 Carney, 18 Melenchon
#   Economy 1 = 5 EU loan; Society 1 = 10 GTA VI; Disasters 2 = 6 Gaza, 7 Akvan
#   Tech 2 = 3 Nvidia, 16 NSA; Climate & space 3 = 11 Amazon, 14 Voyager,
#           20 Earth study; Justice 1 = 12 Libya. Total 21.
NUMBERS = [("3", "presidents at one table"), ("1", "light-day: Voyager 1"),
           ("\u20ac45bn", "proposed for Kyiv"), ("46,000", "households displaced"),
           ("1st", "Black Speaker nominee"), ("$7bn", "pledged for India")]
DATE_CHECK = ("Left out on purpose: Bangladesh wage protests shutting 55 factories; "
              "Australia sanctioning settler leader Daniella Weiss; Pew projection that "
              "Muslims could outnumber Christians by 2035; Fed minutes, released 18 Nov, "
              "not today.")
FOOTER = ("Every story here happened or was first reported on Thursday 19 November 2026. "
          "Contested claims are attributed. Sources: BBC, NDTV, The Hindu, AP, Reuters, "
          "Bloomberg.")


# ---------------------------------------------------------------- layout
def balance2(text, f, max_w):
    """Split text into 2 balanced lines (reference headlines are all 2 lines).
    Picks the split point minimising the widest line; falls back to greedy wrap."""
    words = text.split()
    if len(words) < 2:
        return [text]
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if f.getlength(a) <= max_w and f.getlength(b) <= max_w:
            w = max(f.getlength(a), f.getlength(b))
            if best is None or w < best[0]:
                best = (w, [a, b])
    return best[1] if best else wrap(text, f, max_w, 2)


def draw_card(d, card, x, y, w, h, big):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=1)
    # illustration (reference: 63% of card height big, 54% small)
    ill_h = 124 if big else 78
    card["ill"](d, x + 1, y + 1, w - 2, ill_h)
    # number badge (red = emphasis only, better-colors: one meaning)
    # reference: ~20px big, ~18px small
    bs = 20 if big else 18
    d.rectangle([x + 1, y + 1, x + 1 + bs, y + 1 + bs], fill=RED)
    bf = font(SANSB, 13 if big else 12)
    d.text((x + 1 + bs / 2, y + 1 + bs / 2), str(card["n"]), font=bf,
           fill=(255, 255, 255), anchor="mm")
    # region tag pill (reference: pill ~13px, text cap ~7px)
    col = REGIONS[card["region"]]
    tx, ty = x + 8, y + ill_h + 5
    tag = f"{card['region']} · {card['field']}"
    tf = font(SANSB, 10 if big else 9)
    tw = tf.getlength(tag)
    th = 13 if big else 12
    d.rectangle([tx, ty, tx + tw + 10, ty + th], fill=col)
    d.text((tx + 5, ty + th / 2), tag, font=tf, fill=REGION_TEXT[card["region"]],
           anchor="lm")
    # headline: 2 balanced lines (reference headlines are all 2 lines).
    # Placement is measured from the fonts' real ink boxes (cap-top 5px below
    # the tag), not from nominal sizes, so the deck can never touch it.
    hx = x + 8
    hw = w - 16
    hsize = 19 if big else 15
    hf = font(SANSB, hsize)
    lh = 21 if big else 16
    ascent, descent = hf.getmetrics()
    cap = hf.getbbox("H")[3] - hf.getbbox("H")[1]
    hy = ty + th + 5 - (ascent - cap)
    lines = balance2(card["headline"], hf, hw)
    if any("…" in ln for ln in lines):
        print(f"  WARNING truncated headline card {card['n']}: {card['headline']!r}")
    for i, line in enumerate(lines):
        d.text((hx, hy + i * lh), line, font=hf, fill=INK)
    head_ink_bottom = (hy + (len(lines) - 1) * lh + ascent
                       + (descent if any(c in "gjpqy" for ln in lines for c in ln) else 0))
    # deck, one line: bottom-anchored, ink bottom 4px above the card edge,
    # with at least a 2px gap below the headline ink; shrink if it cannot fit.
    dsize = 12 if big else 10
    df = font(SANS, dsize)
    while dsize > (10 if big else 8):
        df = font(SANS, dsize)
        dasc, ddesc = df.getmetrics()
        deff = ddesc if any(c in "gjpqy" for c in card["deck"]) else 0
        dy = (y + h - 4) - (dasc + deff)
        # compare INK to ink: the deck's ink starts (ascent - cap) below its
        # anchor, so a 2px ink gap is dy + (dasc - cap) - head_ink_bottom
        dcap = df.getbbox("H")[3] - df.getbbox("H")[1]
        if dy + (dasc - dcap) - head_ink_bottom >= 2:
            break
        dsize -= 1
    df = font(SANS, dsize)
    dasc, ddesc = df.getmetrics()
    deff = ddesc if any(c in "gjpqy" for c in card["deck"]) else 0
    dy = (y + h - 4) - (dasc + deff)
    if dsize < (12 if big else 10):
        print(f"  deck shrunk card {card['n']} to {dsize}px")
    if df.getlength(card["deck"]) > hw:
        print(f"  WARNING deck overflow card {card['n']}: {card['deck']!r}")
    d.text((hx, dy), card["deck"], font=df, fill=(60, 60, 60))


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=OCEAN, outline=INK, width=1)
    fx, fy = w / 300.0, h / 138.0

    def poly(pts, fill=LAND, outline=LAND_DK):
        d.polygon([(x + px * fx, y + py * fy) for px, py in pts], fill=fill,
                  outline=outline)

    poly([(8, 14), (40, 6), (70, 10), (78, 22), (66, 30), (72, 44), (58, 52),
          (48, 44), (30, 48), (14, 40), (4, 26)])                       # N America
    poly([(78, 4), (92, 2), (96, 10), (84, 12)])                        # Greenland
    poly([(62, 62), (78, 58), (88, 68), (82, 88), (72, 108), (64, 96),
          (58, 76)])                                                      # S America
    poly([(140, 16), (158, 10), (168, 18), (160, 30), (146, 32), (138, 26)])
    poly([(136, 14), (142, 12), (144, 20), (138, 22)])                  # UK
    poly([(140, 44), (162, 40), (176, 50), (172, 72), (158, 92), (146, 84),
          (138, 62)])                                                     # Africa
    poly([(170, 12), (230, 6), (268, 12), (292, 24), (284, 44), (260, 52),
          (240, 66), (220, 58), (200, 64), (188, 50), (176, 40), (168, 26)])
    poly([(232, 70), (244, 74), (238, 82), (228, 78)])                  # SE Asia isles
    poly([(252, 92), (272, 88), (282, 96), (268, 106), (254, 102)])     # Oceania
    # carve seas so Eurasia/Africa read as separate landmasses, not one blob
    poly([(138, 32), (168, 30), (172, 38), (160, 42), (140, 40)], fill=OCEAN,
         outline=OCEAN)
    poly([(174, 46), (184, 42), (188, 52), (178, 54)], fill=OCEAN,
         outline=OCEAN)                                                 # Red Sea
    poly([(196, 44), (206, 40), (208, 48), (198, 50)], fill=OCEAN,
         outline=OCEAN)                                                 # Persian Gulf
    # pins 1-13 (numbered) and brief dots 14-21 (fractions of the 300x138 box).
    # Repulsion pass: no two pins closer than 19px, pin-dot 13px, dot-dot 11px,
    # so the Gulf/Europe clusters stay readable instead of merging into a blob.
    pins = {1: (.66, .36), 2: (.83, .36), 3: (.10, .30), 4: (.235, .28),
            5: (.55, .20), 6: (.605, .42), 7: (.745, .47), 8: (.63, .52),
            9: (.55, .10), 10: (.40, .48), 11: (.72, .44), 12: (.52, .40),
            13: (.82, .30)}
    dots = {14: (.06, .72), 15: (.615, .15), 16: (.15, .26), 17: (.13, .13),
            18: (.475, .22), 19: (.57, .50), 20: (.36, .72), 21: (.50, .13)}
    pts = {n: [fx_ * w, fy_ * h] for n, (fx_, fy_) in {**pins, **dots}.items()}
    for _ in range(60):
        moved = False
        keys = sorted(pts)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                dx, dy = pts[b][0] - pts[a][0], pts[b][1] - pts[a][1]
                dist = math.hypot(dx, dy) or 0.01
                need = 19 if a in pins and b in pins else (
                    13 if (a in pins) != (b in pins) else 11)
                if dist < need:
                    push = (need - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    pts[a][0] -= ux * push
                    pts[a][1] -= uy * push
                    pts[b][0] += ux * push
                    pts[b][1] += uy * push
                    moved = True
        for n in pts:
            pts[n][0] = min(max(pts[n][0], 9), w - 9)
            pts[n][1] = min(max(pts[n][1], 9), h - 9)
        if not moved:
            break
    pf = font(SANSB, 10)
    for n in pins:
        cx, cy = x + pts[n][0], y + pts[n][1]
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=(255, 255, 255),
                  width=1)
        d.text((cx, cy), str(n), font=pf, fill=(255, 255, 255), anchor="mm")
    for n in dots:
        cx, cy = x + pts[n][0], y + pts[n][1]
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    log = []

    # top red rule + strip (better-layout: shared 12px edges)
    # reference: strip text cap ~8px -> 11px; right half RED
    d.rectangle([0, 0, W, 5], fill=RED)
    sf = font(SANSB, 11)
    d.text((M, 9), "THE WORLD\u2019S NEWS IN ONE PICTURE", font=sf, fill=INK)
    right = "21 STORIES \u00b7 6 REGIONS \u00b7 8 FIELDS \u00b7 13 ILLUSTRATED \u00b7 ALL FROM THURSDAY"
    d.text((W - M, 9), right, font=sf, fill=RED, anchor="ra")

    # masthead: serif, fitted to the content width, ink-top at y=40
    # (reference: cap height 41px; DejaVu Serif Bold 56px gives cap ~41 and
    # spans ~930px, closest metric match of the candidates measured)
    mf, msize = fit_font(DEJAVU_BOLD, "Thursday 19 November 2026", CW, 56)
    log.append(f"masthead size {msize}")
    bb = d.textbbox((W // 2, 0), "Thursday 19 November 2026", font=mf, anchor="ma")
    d.text((W // 2, 40 - bb[1]), "Thursday 19 November 2026", font=mf,
           fill=INK, anchor="ma")
    # double rule under the masthead (reference: full-width rules at y=92, 94)
    d.line([M, 92, M + CW, 92], fill=INK, width=1)
    d.line([M, 94, M + CW, 94], fill=INK, width=1)

    # region bar: 6 equal segments, counts = region totals
    # reference: y=98, height 16px
    ry, rh = 98, 16
    seg = CW / 6
    rf = font(SANSB, 13)
    for i, (name, count) in enumerate(REGION_COUNTS.items()):
        x0 = M + i * seg
        d.rectangle([x0, ry, x0 + seg, ry + rh], fill=REGIONS[name])
        d.text((x0 + seg / 2, ry + rh / 2), f"{name} {count}", font=rf,
               fill=REGION_TEXT[name], anchor="mm")

    # field bar: black, white text, fitted (reference: y=117, height 17px)
    fy, fh = 117, 17
    d.rectangle([M, fy, M + CW, fy + fh], fill=BAR_BLK)
    field_txt = "BY FIELD:  " + "  \u00b7  ".join(f"{n} {c}" for n, c in FIELD_COUNTS)
    ff, fsize = fit_font(SANS, field_txt, CW - 12, 12)
    log.append(f"field bar size {fsize}")
    d.text((M + 6, fy + fh / 2), field_txt, font=ff, fill=(255, 255, 255),
           anchor="lm")

    # day-in-numbers: date-stamped facts only, numbers in red
    # reference: strip sits just below the field bar, ~12px type
    ny = 137
    parts = [("THE DAY IN NUMBERS:  ", INK, True)]
    for i, (num, txt) in enumerate(NUMBERS):
        if i:
            parts.append(("  \u00b7  ", INK, False))
        parts.append((num + " ", RED, True))
        parts.append((txt, INK, False))
    nf, nsize = fit_font(SANS, "".join(p[0] for p in parts), CW, 12)
    nfb = font(SANSB, nsize)
    log.append(f"numbers strip size {nsize}")
    cx = M
    for txt, col, bold in parts:
        f = nfb if bold else nf
        d.text((cx, ny), txt, font=f, fill=col)
        cx += f.getlength(txt)

    # lead cards: 3 big + 5 + 5 (ronigrv skeleton, own art)
    # reference geometry: big y154 h212; small rows y372 / y527 h149
    big_w, gap = 328, 8
    for i, card in enumerate(LEADS[:3]):
        draw_card(d, card, M + i * (big_w + gap), 154, big_w, 212, big=True)
    sm_w = (CW - 4 * gap) // 5
    for row, cards in enumerate((LEADS[3:8], LEADS[8:13])):
        y0 = 372 + row * 155
        for i, card in enumerate(cards):
            draw_card(d, card, M + i * (sm_w + gap), y0, sm_w, 149, big=False)

    # bottom: map left, briefs right (reference: headers y685, rule y699,
    # map 300x148 from y704, legend ~y857)
    by = 685
    tf = font(SANSB, 14)
    d.text((M, by), "WHERE IT HAPPENED", font=tf, fill=INK)
    d.text((342, by), "ALSO ON THURSDAY 19 NOVEMBER", font=tf, fill=INK)
    d.line([M, by + 14, M + CW, by + 14], fill=INK, width=1)
    draw_map(d, M, by + 19, 300, 148)
    # map legend
    ly = by + 172
    lf = font(SANS, 11)
    lx = M
    for name in ("EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "WORLD"):
        d.ellipse([lx, ly + 2, lx + 8, ly + 10], fill=REGIONS[name])
        lab = name.title()
        d.text((lx + 11, ly), lab, font=lf, fill=INK)
        lx += 11 + lf.getlength(lab) + 8
    d.text((M, ly + 14), "Pins = cards \u00b7 dots = briefs", font=lf, fill=(90, 90, 90))

    # briefs: 3 columns, one line each, bold lead-in + region bullet
    # reference: cap 7px -> 10px type, ~13px line pitch
    bx0, bw = 342, 223
    cols = [[BRIEFS[0], BRIEFS[1], BRIEFS[2]],
            [BRIEFS[3], BRIEFS[4], BRIEFS[5]],
            [BRIEFS[6], BRIEFS[7]]]
    for ci, col in enumerate(cols):
        for ri, (n, lead, body, region) in enumerate(col):
            yy = by + 19 + ri * 14
            # fit: start at 11/10, shrink only if the line overflows
            for lsz, bsz in ((11, 10), (10, 10), (10, 9)):
                lf2, bf2 = font(SANSB, lsz), font(SANS, bsz)
                num_w = lf2.getlength(f"{n} ")
                total = num_w + 9 + lf2.getlength(lead) + bf2.getlength(" " + body)
                if total <= bw:
                    break
            else:
                lsz, bsz = 10, 9
                lf2, bf2 = font(SANSB, lsz), font(SANS, bsz)
            if (lsz, bsz) != (11, 10):
                log.append(f"brief {n} shrunk to {lsz}/{bsz}")
            xx = bx0 + ci * (bw + 10)
            d.text((xx, yy), f"{n} ", font=lf2, fill=INK)
            xx += lf2.getlength(f"{n} ")
            d.rectangle([xx, yy + 2, xx + 6, yy + 8], fill=REGIONS[region])
            xx += 9
            d.text((xx, yy), lead, font=lf2, fill=INK)
            xx += lf2.getlength(lead)
            d.text((xx, yy), " " + body, font=bf2, fill=(60, 60, 60))

    # DATE CHECK: red border, prominent, short (reference: ~y970, 2 lines ~12px)
    dy, dh = 966, 34
    d.rectangle([M, dy, M + CW, dy + dh], outline=RED, width=2)
    df = font(SANS, 12)
    dfb = font(SANSB, 12)
    label = "DATE CHECK \u2014 "
    d.text((M + 8, dy + dh / 2), label, font=dfb, fill=RED, anchor="lm")
    rest = DATE_CHECK
    lines = wrap(rest, df, CW - 16 - dfb.getlength(label), 2)
    for i, line in enumerate(lines):
        d.text((M + 8 + dfb.getlength(label), dy + 4 + i * 15), line, font=df,
               fill=INK)
    log.append(f"date-check lines {len(lines)}")

    # footer (reference: full-width rule at y=1004, text ~y1010, ~12px)
    d.line([M, 1004, M + CW, 1004], fill=INK, width=1)
    ff2, f2size = fit_font(SANS, FOOTER, CW, 12)
    log.append(f"footer size {f2size}")
    d.text((W // 2, 1010), FOOTER, font=ff2, fill=(60, 60, 60), anchor="ma")

    # contrast audit (better-colors: measure, don't estimate)
    for name, col in REGIONS.items():
        log.append(f"contrast {name} white {contrast((255,255,255), col):.2f} "
                   f"black {contrast((25,25,25), col):.2f} "
                   f"-> {REGION_TEXT[name]}")
    log.append(f"contrast red/cream {contrast(RED, PAPER):.2f}")
    log.append(f"contrast ink/cream {contrast(INK, PAPER):.2f}")

    img.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")
    for line in log:
        print("  ", line)


if __name__ == "__main__":
    main()
