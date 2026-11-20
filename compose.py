#!/usr/bin/env python3
"""news-image-20261119 v2 — "Thursday 19 November 2026" front-page poster.

Draws the whole 1024x1024 page with PIL: no photos, no AI images, no network.
Every illustration is original flat-vector art drawn here from PIL shapes
(v1 art for the 6 kept leads) or in ill_new.py (the 7 evening-refresh leads).
Slate: 36 verified stories (13 illustrated leads + 23 briefs), per the
binding story sheet in
~/workspace/makefun/news-image-20261119-concept-v2/story-sheet.md.
v1 lead 1 (Iran strikes on US bases) is struck: an 18-Nov event, now a
DATE CHECK item. A9+A10 combine into one illustrated Iran lead (lead 3).

Type scale (better-typography: 3 faces, size by role, no light weights).
MEASURED from the reference (ronigrv rank-1, 18 Nov, 1024 canvas) by glyph
measurement, not guessed: masthead cap 41px; big headlines cap 14px in 335px
cards (ratio .042), decks cap 9px; small headlines cap 11px in 193px cards,
decks cap 7px; briefs cap 7px; region bar 16px, field bar 17px; big-card
illustration 63% of card height, small-card 54%. Our sizes below are set so
the RENDERED CAP HEIGHTS match those numbers (Noto cap/em ~0.72):
  masthead  DejaVu Serif Bold 56px (cap 41, spans ~930px like the reference)
  headlines Noto Sans Condensed Bold, 19px big cards / 15px small cards
    (two cards need a smaller headline so the verbatim 2-line headline
    fits: card 4 at 14.5px, card 7 at 13px — see fit_headline)
  decks     Noto Sans Condensed, 12px big / 10px small, WRAPPED to 2-4
    lines: the sheet's decks are verbatim full sentences (86-160 chars),
    which cannot fit one line at the type floor, so the illustration
    height is computed per row from the longest deck (big ~95px, small
    ~51px) instead of the reference's 63%/54% — a forced deviation,
    verbatim decks win over illustration height
  labels    Noto Sans Condensed Bold, 10px big / 9px small, uppercase
  briefs    Noto Sans Condensed Bold 11px lead-in / 10px body, 1 line each
    (wording shortened from the sheet's full briefs to fit; facts kept)
  footer    Noto Sans Condensed 12px
Layout (better-layout): 12px shared margins, 8px gaps between card groups,
4px gaps inside cards, one card style, square corners (newsprint).
Card geometry mirrors the reference: big cards y154 h212, small rows y372 /
y541 h163 (taller than v1's 149 to hold the wrapped decks), bottom headers
y713, map 270x130, DATE CHECK y896 (6 lines), footer y1010.
Colour (better-colors): one hue per region, red only for badges/emphasis;
text on gold/orange segments is black (measured contrast), white elsewhere.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

from ill_new import (ill_crimea_bridge, ill_icj, ill_musk, ill_pif_tower,
                     ill_anthropic, ill_iran_talks, ill_cop31)

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

# region hues: blue / green / gold / orange / purple / teal / grey (each >15 deg apart)
REGIONS = {
    "EUROPE":      (46, 109, 164),
    "MIDDLE EAST": (46, 125, 79),
    "ASIA":        (192, 138, 0),
    "AFRICA":      (217, 108, 44),
    "AMERICAS":    (111, 74, 158),
    "OCEANIA":     (0, 128, 128),
    "WORLD":       (77, 77, 77),
}
# text colour on each region fill (measured: white fails 4.5:1 on gold/orange)
REGION_TEXT = {
    "EUROPE": (255, 255, 255), "MIDDLE EAST": (255, 255, 255),
    "ASIA": (25, 25, 25), "AFRICA": (25, 25, 25),
    "AMERICAS": (255, 255, 255), "OCEANIA": (255, 255, 255),
    "WORLD": (255, 255, 255),
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
    # chip, left third — scaled to the box height (v1's fixed 58px chip
    # overflowed the box when h < 70: at v2's h=58 its bottom pins landed
    # in the tag zone, 24px below the illustration)
    s = min(1.0, (h - 16) / 70.0)
    cw = max(24, int(58 * s))
    cx0, cy0 = x + 12, y + 8
    b = max(3, int(6 * s))
    d.rectangle([cx0 - b, cy0 - b, cx0 + cw + b, cy0 + cw + b], fill=(60, 60, 60))
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + cw], fill=(200, 200, 200))
    step = max(5, cw // 5)
    for i in range(5):  # pins on all four sides
        for px, py, pw, ph in ((cx0 + 4 + i * step, cy0 - b, 4, b),
                               (cx0 + 4 + i * step, cy0 + cw, 4, b),
                               (cx0 - b, cy0 + 4 + i * step, b, 4),
                               (cx0 + cw, cy0 + 4 + i * step, b, 4)):
            d.rectangle([px, py, px + pw, py + ph], fill=(160, 160, 160))
    m = max(6, int(12 * s))
    d.rectangle([cx0 + m, cy0 + m, cx0 + cw - m, cy0 + cw - m],
                fill=(24, 68, 32))
    for off in (int(cw * 0.31), int(cw * 0.52), int(cw * 0.72)):  # circuit traces on the die
        d.line([cx0 + off, cy0 + m + 2, cx0 + off, cy0 + cw - m - 2],
               fill=(118, 185, 0), width=2)
        d.line([cx0 + m + 2, cy0 + off, cx0 + cw - m - 2, cy0 + off],
               fill=(118, 185, 0), width=2)
    er = max(4, int(7 * s))
    d.ellipse([cx0 + cw // 2 - er, cy0 + cw // 2 - er,
               cx0 + cw // 2 + er, cy0 + cw // 2 + er], fill=(118, 185, 0))
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
    # star circle scaled to the box height (v1's fixed r=30 escaped up to
    # 12px above the box at v2's h=58 — and 4px even at v1's h=78)
    cx, cy = x + w // 2, y + int(h * 0.44)
    r = int(h * 0.30)
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
    for rx in range(0, w - 6, 18):  # rain (leans left as it falls, but
        # never past either box edge)
        d.line([x + rx + 6, y + 4, x + rx, y + 22], fill=(90, 110, 130), width=2)
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
    # wave arcs, sized to the water depth (v1's fixed 4 rows x 12px step
    # ran up to 27px below the box at v2's h=58 — and 18px at v1's h=78)
    wh = h - int(h * 0.55)
    nrows = 3 if wh >= 30 else 2
    step = max(8, (wh - 8) // nrows)
    ah = min(10, step - 2)
    for i in range(nrows):
        yy = wy + 4 + i * step
        d.arc([x + 6 + i * 8, yy, x + 44 + i * 8, yy + ah], 0, 180,
              fill=(180, 220, 240), width=2)
        d.arc([x + w - 50 - i * 6, yy, x + w - 12 - i * 6, yy + ah], 0, 180,
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
    for rx in range(0, int(w * 0.45), 20):  # rain, sea side only (leans
        # left as it falls, but never past the box's left edge)
        d.line([x + rx + 5, y + 6, x + rx, y + 22], fill=(170, 200, 220), width=2)
    cx, cy = x + int(w * 0.42), y + int(h * 0.50)
    # spiral arms: same centre would read as a target; offset each ring's
    # centre along the swirl and stagger the arc so the bands wind inward.
    # Radii are scaled to the box height (v1's fixed 46px outer arm escaped
    # up to 20px above the box at v2's h=58 — and 10px even at v1's h=78,
    # white on cream, unnoticed until the containment probe).
    k = (int(h * 0.50) - 2) / 46.0
    arms = [((0, 0), 46, 15, 285, (255, 255, 255), 9),
            ((7, -5), 36, 60, 330, (210, 230, 240), 8),
            ((-6, 6), 26, 110, 20, (255, 255, 255), 7),
            ((4, 3), 16, 170, 80, (160, 200, 220), 6)]
    for (ox, oy), r, a0, a1, col, wd in arms:
        rr = max(6, int(r * k))
        d.arc([cx + int(ox * k) - rr, cy + int(oy * k) - rr,
               cx + int(ox * k) + rr, cy + int(oy * k) + rr],
              start=a0, end=a1, fill=col, width=max(3, int(wd * k)))
    er = max(3, int(7 * k))
    d.ellipse([cx - er, cy - er, cx + er, cy + er], fill=(255, 255, 255))  # eye
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(32, 90, 120))
    for hx in (0.78, 0.88):  # houses on the land
        d.rectangle([x + int(w * hx), y + int(h * 0.58), x + int(w * hx) + 13,
                     y + int(h * 0.72)], fill=(226, 214, 186))
        d.polygon([(x + int(w * hx) - 3, y + int(h * 0.58)),
                   (x + int(w * hx) + 16, y + int(h * 0.58)),
                   (x + int(w * hx) + 6, y + int(h * 0.48))], fill=(150, 90, 70))


# ---------------------------------------------------------------- data
# Headlines and decks are VERBATIM from the binding story sheet
# (~/workspace/makefun/news-image-20261119-concept-v2/story-sheet.md):
# straight quotes/apostrophes, em/en dashes exactly as in the sheet.
LEADS = [
    dict(n=1, region="ASIA", field="POLITICS & DIPLOMACY", ill=ill_apec,
         headline="Trump, Xi and Putin sign first-ever joint declaration",
         deck="\"Declaration Towards Peace\": four points, incl. \"a nuclear war cannot be won\" \u2014 but no deal on Ukraine, Iran or a new nuclear treaty; US\u2013China trade truce extended."),
    dict(n=2, region="WORLD", field="JUSTICE", ill=ill_icj,
         headline="ICJ: Myanmar committed genocide against the Rohingya",
         deck="9\u20136, the court's first-ever state genocide verdict: ~10,000 killed, 730,000+ fled; Myanmar ordered to allow safe return \u2014 final and binding."),
    dict(n=3, region="MIDDLE EAST", field="WAR & SECURITY", ill=ill_iran_talks,
         headline="Netanyahu presses Trump on Iran; Trump: \"we'll see after Jan 1\"",
         deck="Reports say Israel seeks a 4\u20137-day joint air campaign; Trump tells Fox Iran is \"looking at gas/bio\" \u2014 Rubio: no imminent threat; Israel disputes \"pressuring\"."),
    dict(n=4, region="EUROPE", field="WAR & SECURITY", ill=ill_crimea_bridge,
         headline="Ukraine hits Crimean Bridge a third time this week",
         deck="Early-hours strike on 19 Nov, confirmed by Crimea's Russian-installed head; traffic suspended as damage is assessed."),
    dict(n=5, region="MIDDLE EAST", field="WAR & SECURITY", ill=ill_pif_tower,
         headline="Missile debris damages Riyadh's PIF Tower",
         deck="Suspected Houthi missile intercepted early 19 Nov; windows blown out across 7\u20138 floors, no casualties; Houthis had not claimed the tower hit."),
    dict(n=6, region="AMERICAS", field="ECONOMY & LABOUR", ill=ill_anthropic,
         headline="Anthropic debuts in record $81B IPO",
         deck="Priced $83 a share, above the $70\u2013$78 range; 980M shares, $81.3B primary sale \u2014 largest IPO on record; trades as ANT."),
    dict(n=7, region="AMERICAS", field="POLITICS & DIPLOMACY", ill=ill_musk,
         headline="Musk: \"I feel pretty foolish\" over $446M midterm spending",
         deck="Speaking at DealBook \u2014 reported 19 Nov \u2014 the largest individual donor distances himself: \"not MAGA\"; Democrats won both chambers."),
    dict(n=8, region="WORLD", field="CLIMATE", ill=ill_cop31,
         headline="COP31 second draft drops all fossil-fuel references",
         deck="Slimmed-down text published 19 Nov acknowledges warming could pass 1.5C and urges deep emissions cuts; talks due to end Friday."),
    dict(n=9, region="AMERICAS", field="TECH", ill=ill_nvidia,
         headline="Nvidia chief Huang steps down; Kress interim CEO",
         deck="Board accepted his resignation 11 Nov, SEC filing shows; interim chief Colette Kress; reports say Huang has discussed a comeback \u2014 neither side confirms."),
    dict(n=10, region="EUROPE", field="ECONOMY & LABOUR", ill=ill_eu_loan,
         headline="EU proposes \u20ac45B for Ukraine in 2027",
         deck="Commission plan: \u20ac25B defence + \u20ac20B budget support, with a \u20ac25B gap still open \u2014 a proposal, announced as allies met in Berlin."),
    dict(n=11, region="MIDDLE EAST", field="DISASTERS", ill=ill_gaza,
         headline="Gaza flooding displaces 46,000+ households",
         deck="Heavy rain damages 40,000+ shelters, reports say, as families already displaced face rising water."),
    dict(n=12, region="ASIA", field="DISASTERS", ill=ill_akvan,
         headline="Cyclone Akvan nears India's east coast",
         deck="Nears landfall Friday; schools shut in six districts; 21 cm+ rain expected on the coast."),
    dict(n=13, region="AMERICAS", field="POLITICS & DIPLOMACY", ill=ill_jeffries,
         headline="Jeffries nominated as first Black House Speaker",
         deck="House Democrats nominate Hakeem Jeffries; the gavel vote is scheduled for 3 January."),
]
BRIEFS = [  # (number, lead-in, body, region)
    # Wording shortened from the sheet's full briefs so each fits ONE line
    # at the 11/10px type floor in a 233px column (measured); every fact
    # kept, attributions kept where they fit (see build-log-v2.md for drops).
    (14, "Houthis seize Red Sea", "\u2014 Bab el-Mandeb taken", "MIDDLE EAST"),
    (15, "Estonia shuts Russia border", "\u2014 GRU alleged", "EUROPE"),
    (16, "GTA VI rolls out worldwide", "\u2014 no sales figures", "AMERICAS"),
    (17, "Amazon pledges $7B", "\u2014 India renewables by 2030", "ASIA"),
    (18, "Libya drug haul", "\u2014 cocaine, millions of pills", "AFRICA"),
    (19, "Liu Yunping, caucus chair", "\u2014 first Taiwanese", "AMERICAS"),
    (20, "Denmark ratifies deal", "\u2014 Greenland\u2013US, 109\u20130", "EUROPE"),
    (21, "IMF: inflation 4.7%", "\u2014 growth 3.1%; 4.1% in 2027", "WORLD"),
    (22, "Bangladesh lockdown", "\u2014 2 killed, 565 arrested", "ASIA"),
    (23, "Garcia: 12 notices", "\u2014 Epstein files", "AMERICAS"),
    (24, "Outage week: prepping", "\u2014 officials: no attack", "AMERICAS"),
    (25, "Colombia strike", "\u2014 Bogot\u00e1, Medell\u00edn, Cali", "AMERICAS"),
    (26, "Litton Das record", "\u2014 8 dismissals, century", "ASIA"),
    (27, "Congress presses Modi", "\u2014 inflation 6.09%", "ASIA"),
    (28, "NZ 243/5 after 70/5", "\u2014 Nicholls 113*, Phillips 94*", "OCEANIA"),
    (29, "Willing meets in Berlin", "\u2014 \u00a3260M; no statement", "WORLD"),
    (30, "Voyager 1 one light-day out", "\u2014 NASA confirms", "WORLD"),
    (31, "Zelensky urges lift", "\u2014 Starshield, Kyiv asks", "EUROPE"),
    (32, "NSA outage", "\u2014 CNN reports; no cause given", "AMERICAS"),
    (33, "Carney resets China ties", "\u2014 seeks right US deal", "AMERICAS"),
    (34, "M\u00e9lenchon could win", "\u2014 minister's prediction", "EUROPE"),
    (35, "Saudi: danger passed", "\u2014 three southern cities", "MIDDLE EAST"),
    (36, "Earth's missing billion years", "\u2014 Nature proposes", "WORLD"),
]
REGION_COUNTS = {"EUROPE": 6, "MIDDLE EAST": 5, "ASIA": 6, "AFRICA": 1,
                 "AMERICAS": 11, "OCEANIA": 1, "WORLD": 6}
FIELD_COUNTS = [("War & security", 8), ("Politics & diplomacy", 10),
                ("Economy & labour", 4), ("Society & culture", 3),
                ("Disasters & weather", 2), ("Tech", 3),
                ("Climate & space", 4), ("Justice", 2)]
# Region tally, counted from the 36 stories themselves (judge-checkable):
#   Europe 6 = leads 4, 10; briefs 15, 20, 31, 34
#   Middle East 5 = leads 3, 5, 11; briefs 14, 35
#   Asia 6 = leads 1, 12; briefs 17, 22, 26, 27
#   Africa 1 = brief 18; Oceania 1 = brief 28
#   Americas 11 = leads 6, 7, 9, 13; briefs 16, 19, 23, 24, 25, 32, 33
#   World 6 = leads 2, 8; briefs 21, 29, 30, 36. Total 36.
# Field tally, counted from the 36 stories themselves (judge-checkable):
#   War 8 = leads 3, 4, 5; briefs 14, 15, 29, 31, 35
#   Politics 10 = leads 1, 7, 13; briefs 19, 20, 22, 23, 27, 33, 34
#   Economy 4 = leads 6, 10; briefs 21, 25
#   Society 3 = briefs 16, 26, 28; Disasters 2 = leads 11, 12
#   Tech 3 = lead 9; briefs 24, 32
#   Climate & space 4 = lead 8; briefs 17, 30, 36
#   Justice 2 = lead 2; brief 18. Total 36.
NUMBERS = [("$83", "Anthropic IPO price"),
           ("109\u20130", "Greenland\u2013US deal ratified"),
           ("9\u20136", "ICJ genocide verdict"),
           ("$446M", "Musk's midterm spending"),
           ("46,000+", "households displaced"),
           ("1,000+", "drones for Ukraine")]
# DATE CHECK: 6 verified 18-Nov events, verbatim from the story sheet,
# one line each (measured: longest line 806px at 12px, box fits 909px).
DATE_CHECK = [
    "Ali Al Salem attack, overnight 18 Nov \u2014 Iranian drones/missiles hit Ali Al Salem Air Base, Kuwait (and Bahrain); reported 19 Nov, but the event was 18 Nov. NOT a 19-Nov story.",
    "Fed minutes, released 18 Nov 14:00 ET \u2014 the \"more hikes expected\" discussion is 18 Nov, not 19 Nov.",
    "Pew projection that Muslims could outnumber Christians by 2035 \u2014 reported 18 Nov; the underlying projection is older, not 19-Nov news.",
    "Arab League condemns Israeli incursions in southern Syria \u2014 statement issued Wed 18 Nov; 19-Nov pieces are follow-ups.",
    "Tanker hit off Khasab, Oman \u2014 UKMTO: unknown projectile hit a tanker's engine room ~6 nm north of Khasab, 16:45 UTC Wed 18 Nov.",
    "Van Gogh \"Blossoming Chestnut Trees\" sold for $190.4M at Sotheby's New York \u2014 Wed 18 Nov evening, not 19 Nov.",
]
FOOTER = ("Every story here happened or was first reported on Thursday 19 November 2026. "
          "Contested claims are attributed. Sources: Reuters, AP, AFP, Al Jazeera, "
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


def fit_headline(text, max_w, start):
    """Largest headline size <= start whose 2-line balanced split fits
    max_w. Steps down 15 -> 14.5 -> ... -> 12. The verbatim headline is
    fixed; only the size may give, never the words. Returns (font, size,
    lines). Measured: card 4 needs 14.5px, card 7 needs 13px at 15px start."""
    size = start
    while size >= 12:
        f = font(SANSB, size)
        lines = balance2(text, f, max_w)
        if len(lines) <= 2 and not any("\u2026" in ln for ln in lines):
            return f, size, lines
        size -= 0.5
    f = font(SANSB, 12)
    return f, 12, balance2(text, f, max_w)


def deck_lines(deck, big, hw):
    """Greedy wrap of the verbatim deck at the type floor (12px big /
    10px small). The type never shrinks and the text is never cut: the
    caller sizes the illustration from the returned line count."""
    df = font(SANS, 12 if big else 10)
    return wrap(deck, df, hw, 6)


def text_block_h(card, big, hw):
    """Minimum height (px) of everything below the illustration in a card:
    5px gap + tag + headline ink (2 lines, ink top 5px below the tag)
    + 4px gap + deck ink (wrapped lines at the type floor) + 4px bottom
    margin. Measured from the fonts' real ink boxes (cap height, descent
    only when the line actually has descenders)."""
    th = 13 if big else 12
    hf, _hs, hlines = fit_headline(card["headline"], hw, 19 if big else 15)
    lh = 21 if big else 16
    ascent, descent = hf.getmetrics()
    cap = hf.getbbox("H")[3] - hf.getbbox("H")[1]
    hdesc = descent if any(c in "gjpqy" for ln in hlines for c in ln) else 0
    head_ink = (len(hlines) - 1) * lh + cap + hdesc
    dlines = deck_lines(card["deck"], big, hw)
    df = font(SANS, 12 if big else 10)
    dasc, ddesc = df.getmetrics()
    dcap = df.getbbox("H")[3] - df.getbbox("H")[1]
    pitch = 14 if big else 12
    ddesc_last = ddesc if any(c in "gjpqy" for c in dlines[-1]) else 0
    deck_ink = (len(dlines) - 1) * pitch + dcap + ddesc_last
    return 5 + th + 5 + head_ink + 4 + deck_ink + 4


def draw_card(d, card, x, y, w, h, big, ill_h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=1)
    # illustration height is computed by the caller from the longest deck
    # in the row (text_block_h), NOT the reference's 63%/54%: the verbatim
    # decks need 2-4 wrapped lines at the type floor, so the art is shorter
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
    tag = f"{card['region']} \u00b7 {card['field']}"
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
    hf, hsize, lines = fit_headline(card["headline"], hw, 19 if big else 15)
    lh = 21 if big else 16
    ascent, descent = hf.getmetrics()
    cap = hf.getbbox("H")[3] - hf.getbbox("H")[1]
    hy = ty + th + 5 - (ascent - cap)
    for i, line in enumerate(lines):
        d.text((hx, hy + i * lh), line, font=hf, fill=INK)
    if hsize < (19 if big else 15):
        print(f"  headline shrunk card {card['n']} to {hsize}px")
    if any("\u2026" in ln for ln in lines):
        print(f"  WARNING truncated headline card {card['n']}: {card['headline']!r}")
    head_ink_bottom = (hy + (len(lines) - 1) * lh + ascent
                       + (descent if any(c in "gjpqy" for ln in lines for c in ln) else 0))
    # deck: verbatim, wrapped to as many lines as it takes at the type floor
    # (12px big / 10px small); bottom-anchored, ink bottom 4px above the
    # card edge. ill_h was computed from the longest deck in the row, so
    # the first deck line clears the headline ink by >= 4px by construction.
    df = font(SANS, 12 if big else 10)
    dlines = deck_lines(card["deck"], big, hw)
    if any("\u2026" in ln for ln in dlines):
        print(f"  WARNING truncated deck card {card['n']}: {card['deck']!r}")
    dasc, ddesc = df.getmetrics()
    dcap = df.getbbox("H")[3] - df.getbbox("H")[1]
    pitch = 14 if big else 12
    n = len(dlines)
    deff_last = ddesc if any(c in "gjpqy" for c in dlines[-1]) else 0
    dy_last = (y + h - 4) - (dasc + deff_last)
    dy_first = dy_last - (n - 1) * pitch
    deck_ink_top = dy_first + (dasc - dcap)
    gap = deck_ink_top - head_ink_bottom
    if gap < 2:
        print(f"  WARNING deck/headline gap card {card['n']}: {gap:.1f}px")
    for i, line in enumerate(dlines):
        d.text((hx, dy_first + i * pitch), line, font=df, fill=(60, 60, 60))


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
    # pins 1-13 (numbered) and brief dots 14-36 (fractions of the 300x138 box).
    # Repulsion pass: no two pins closer than 19px, pin-dot 13px, dot-dot 11px,
    # so the Gulf/Europe clusters stay readable instead of merging into a blob.
    # Pin 8 (COP31) sits on Turkey: the sheet does not name the venue, so the
    # pin marks the talks' region only (no text claim on the image).
    pins = {1: (.83, .36), 2: (.47, .15), 3: (.60, .37), 4: (.55, .19),
            5: (.63, .42), 6: (.225, .28), 7: (.245, .31), 8: (.565, .26),
            9: (.085, .30), 10: (.475, .14), 11: (.605, .40), 12: (.745, .46),
            13: (.235, .29)}
    dots = {14: (.64, .47), 15: (.52, .10), 16: (.15, .35), 17: (.73, .42),
            18: (.51, .33), 19: (.22, .30), 20: (.44, .07), 21: (.835, .38),
            22: (.76, .40), 23: (.18, .28), 24: (.13, .28), 25: (.27, .55),
            26: (.755, .42), 27: (.72, .40), 28: (.93, .80), 29: (.485, .16),
            30: (.06, .72), 31: (.54, .17), 32: (.20, .27), 33: (.14, .18),
            34: (.465, .20), 35: (.625, .44), 36: (.38, .62)}
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
    right = "36 STORIES \u00b7 7 REGIONS \u00b7 8 FIELDS \u00b7 13 ILLUSTRATED \u00b7 ALL FROM THURSDAY"
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

    # region bar: 7 equal segments, counts = region totals
    # reference: y=98, height 16px
    ry, rh = 98, 16
    seg = CW / 7
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
    # geometry: big y154 h212; small rows y372 / y541 h163 (taller than v1's
    # 149 so the wrapped verbatim decks fit). The illustration height of
    # each row is computed from its longest deck (text_block_h): the deck
    # text is fixed, so the art gives, never the type.
    big_w, gap = 328, 8
    big_ill = int(212 - max(text_block_h(c, True, big_w - 16) for c in LEADS[:3]))
    if big_ill < 40:
        print(f"  WARNING big ill_h too small: {big_ill}")
    log.append(f"big ill_h {big_ill}")
    for i, card in enumerate(LEADS[:3]):
        draw_card(d, card, M + i * (big_w + gap), 154, big_w, 212,
                  big=True, ill_h=big_ill)
    sm_w = (CW - 4 * gap) // 5
    for row, cards in enumerate((LEADS[3:8], LEADS[8:13])):
        y0 = 372 + row * 169
        sm_ill = int(163 - max(text_block_h(c, False, sm_w - 16) for c in cards))
        if sm_ill < 40:
            print(f"  WARNING small row {row + 1} ill_h too small: {sm_ill}")
        log.append(f"small row {row + 1} ill_h {sm_ill} "
                   f"(deck lines {[len(deck_lines(c['deck'], False, sm_w - 16)) for c in cards]})")
        for i, card in enumerate(cards):
            draw_card(d, card, M + i * (sm_w + gap), y0, sm_w, 163,
                      big=False, ill_h=sm_ill)

    # bottom: map left, briefs right (reference: headers y685, rule y699,
    # map 300x148 from y704, legend ~y857). v2: small cards are taller, so
    # the bottom starts at y713; the map is 270x130 to fund 233px brief
    # columns; the legend runs to two lines now that Oceania joins it.
    by = 713
    tf = font(SANSB, 14)
    d.text((M, by), "WHERE IT HAPPENED", font=tf, fill=INK)
    d.text((296, by), "ALSO ON THURSDAY 19 NOVEMBER", font=tf, fill=INK)
    d.line([M, by + 14, M + CW, by + 14], fill=INK, width=1)
    draw_map(d, M, by + 19, 270, 130)
    # map legend (two lines: 7 regions no longer fit on one)
    lf = font(SANS, 11)
    for li, names in enumerate((("EUROPE", "MIDDLE EAST", "ASIA", "AFRICA"),
                                ("AMERICAS", "OCEANIA", "WORLD"))):
        ly = by + 154 + li * 14
        lx = M
        for name in names:
            d.ellipse([lx, ly + 2, lx + 8, ly + 10], fill=REGIONS[name])
            lab = name.title()
            d.text((lx + 11, ly), lab, font=lf, fill=INK)
            lx += 11 + lf.getlength(lab) + 8
        if li == 1:
            d.text((lx + 2, ly), "Pins = cards \u00b7 dots = briefs", font=lf,
                   fill=(90, 90, 90))

    # briefs: 3 columns (8 + 8 + 7), one line each, bold lead-in + region
    # bullet. Reference: cap 7px -> 10px type, ~13px line pitch. The
    # wording was shortened in BRIEFS to fit at the 11/10px floor; the
    # shrink ladder below is a tripwire only — a shrink means the wording
    # must be shortened instead (see build-log-v2.md).
    bx0, bw = 296, 233
    cols = [BRIEFS[0:8], BRIEFS[8:16], BRIEFS[16:23]]
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
            if total > bw:
                print(f"  WARNING brief {n} overflows at 10/9: {total:.0f}px > {bw}px")
            xx = bx0 + ci * (bw + 8)
            d.text((xx, yy), f"{n} ", font=lf2, fill=INK)
            xx += lf2.getlength(f"{n} ")
            d.rectangle([xx, yy + 2, xx + 6, yy + 8], fill=REGIONS[region])
            xx += 9
            d.text((xx, yy), lead, font=lf2, fill=INK)
            xx += lf2.getlength(lead)
            d.text((xx, yy), " " + body, font=bf2, fill=(60, 60, 60))

    # DATE CHECK: red border, prominent, 6 items, one line each (reference:
    # ~y970, 2 lines ~12px; v2 needs 6 lines for the 6 verified 18-Nov
    # exclusions). First line carries the red label; the rest align under
    # the first item. Longest item measured 806px at 12px (box fits 909px).
    dy, dh = 896, 98
    d.rectangle([M, dy, M + CW, dy + dh], outline=RED, width=2)
    df = font(SANS, 12)
    dfb = font(SANSB, 12)
    label = "DATE CHECK \u2014 "
    lw = dfb.getlength(label)
    d.text((M + 8, dy + 4), label, font=dfb, fill=RED)
    for i, item in enumerate(DATE_CHECK):
        d.text((M + 8 + lw, dy + 4 + i * 15), item, font=df, fill=INK)
    log.append(f"date-check lines {len(DATE_CHECK)}")

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
