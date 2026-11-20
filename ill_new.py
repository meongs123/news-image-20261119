#!/usr/bin/env python3
"""news-image-20261119 v2 — NEW lead illustrations (art module only).

Standalone art module for the layout engineer to import into compose.py.
Seven flat-vector PIL illustrations for the new evening-refresh leads,
following the v1 conventions in
~/workspace/makefun/news-image-20261119-entry/compose.py exactly:

- Signature: ill_*(d, x, y, w, h) where d is an ImageDraw on the page.
- Every coordinate is computed from (x, y, w, h) only — no absolute page
  coordinates, no reused x-variable as a y (the ill_nvidia bug: a reused
  x-var drew 3 stray lime lines into the briefs area).
- NOTHING draws outside the passed box: background fills stop at
  (x + w - 1, y + h - 1), every shape is checked to stay inside, and
  test_ill_new.py renders each illustration on a magenta canvas and
  fails if any non-magenta pixel appears outside the box.
- PIL primitives only, flat vectors, <=16 colours per illustration.
- 100% original procedural art — no photos, no AI images, no copied art.
- Text inside illustrations is limited to short motif labels ("ANT",
  "$83", "$446M", "FOSSIL FUELS", "DRAFT") — all verified facts, spelled
  correctly, sized by measurement (fit_text shrinks until the label fits
  its allotted width). No invented numbers: B2 uses only the verified
  $83 pricing, no first-trade price, no chart line implying a move.

Usage (layout engineer):
    from ill_new import ill_crimea_bridge, ill_icj, ill_musk, ...
    card["ill"](d, x + 1, y + 1, w - 2, ill_h)   # same call as v1
"""
import math
import os

from PIL import ImageFont

FD = "/usr/share/fonts/truetype/noto"
SANSB = os.path.join(FD, "NotoSans-CondensedBold.ttf")
SANS = os.path.join(FD, "NotoSans-Condensed.ttf")

INK = (25, 25, 25)
RED = (200, 16, 46)
WHITE = (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, int(round(size)))


def fit_text(d, text, cx, cy, max_w, start, fill, path=SANSB):
    """Draw text centred at (cx, cy), shrinking from `start` until it fits
    max_w. Returns (font, size) so callers can measure the drawn width."""
    size = int(round(start))
    while size > 8:
        f = font(path, size)
        if f.getlength(text) <= max_w:
            break
        size -= 1
    f = font(path, size)
    d.text((cx, cy), text, font=f, fill=fill, anchor="mm")
    return f, size


# ---------------------------------------------------------------- illustrations
# Each draws original flat-vector art in box (x, y, w, h). <=16 colours each.

def ill_crimea_bridge(d, x, y, w, h):
    """A1 — Kerch/Crimean Bridge struck a third time, traffic suspended.
    A bridge deck snapped in the middle: the right span has dropped, a
    span section falls into the gap, a yellow burst marks the strike
    point, and a red no-entry disc (top right, clear of the number
    badge) says the crossing is closed. Reads at small size as:
    bridge + break + burst."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(214, 226, 238))  # sky
    d.rectangle([x, y + int(h * 0.62), x + w - 1, y + h - 1],
                fill=(46, 111, 142))                                 # sea
    # bridge deck: left span level, right span dropped, gap in the middle
    d.rectangle([x + int(w * 0.03), y + int(h * 0.40), x + int(w * 0.44),
                 y + int(h * 0.48)], fill=(70, 70, 70))
    d.rectangle([x + int(w * 0.56), y + int(h * 0.46), x + int(w * 0.97),
                 y + int(h * 0.54)], fill=(70, 70, 70))
    # falling span section, tipped into the gap
    d.polygon([(x + int(w * 0.45), y + int(h * 0.48)),
               (x + int(w * 0.55), y + int(h * 0.52)),
               (x + int(w * 0.53), y + int(h * 0.58)),
               (x + int(w * 0.46), y + int(h * 0.55))], fill=(90, 90, 90))
    # support pylons down to the water
    d.rectangle([x + int(w * 0.10), y + int(h * 0.48), x + int(w * 0.10) + 6,
                 y + int(h * 0.72)], fill=(50, 50, 50))
    d.rectangle([x + int(w * 0.85), y + int(h * 0.54), x + int(w * 0.85) + 6,
                 y + int(h * 0.72)], fill=(50, 50, 50))
    # strike burst above the gap (rays + hot centre)
    bx, by = x + int(w * 0.50), y + int(h * 0.34)
    br = int(h * 0.13)
    for ang in range(0, 360, 45):
        d.line([bx, by,
                bx + int(br * math.cos(math.radians(ang))),
                by + int(br * math.sin(math.radians(ang)))],
               fill=(255, 210, 62), width=3)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 240, 160))
    # smoke puffs, left of the burst
    d.ellipse([x + int(w * 0.40), y + int(h * 0.20), x + int(w * 0.40) + 12,
               y + int(h * 0.20) + 12], fill=(150, 150, 150))
    d.ellipse([x + int(w * 0.44), y + int(h * 0.15), x + int(w * 0.44) + 9,
               y + int(h * 0.15) + 9], fill=(170, 170, 170))
    # waves, sized to the box height (fixed 10px arcs + 12px step escaped
    # 5px below the box at v2's h=55)
    ah = max(5, int(h * 0.12))
    for i in range(2):
        yy = y + int(h * 0.70) + i * (ah + 2)
        d.arc([x + 8 + i * 10, yy, x + 46 + i * 10, yy + ah], 0, 180,
              fill=(180, 220, 240), width=2)
        d.arc([x + w - 52 - i * 8, yy, x + w - 14 - i * 8, yy + ah], 0, 180,
              fill=(180, 220, 240), width=2)
    # no-entry disc, top right (traffic suspended)
    cx, cy = x + int(w * 0.88), y + int(h * 0.16)
    r = min(int(w * 0.07), int(h * 0.16))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.rectangle([cx - r + 3, cy - 2, cx + r - 3, cy + 2], fill=WHITE)


def ill_icj(d, x, y, w, h):
    """A5 — ICJ final judgment: Myanmar responsible for the Rohingya
    genocide, Peace Palace, The Hague. A classical courthouse (stepped
    red roof, columns, dark door) with the scales of justice in gold
    above the roofline. Reads at small size as: courthouse + scales."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(206, 224, 238))  # sky
    d.rectangle([x, y + int(h * 0.88), x + w - 1, y + h - 1],
                fill=(200, 196, 184))                                # plaza
    # scales of justice, gold, centred above the roof
    sx = x + w // 2
    # finial kept inside the box: at h=55 the 5% offset put the gold knob
    # 1px above the box edge
    stop, sbot = y + max(3, int(h * 0.05)), y + int(h * 0.24)
    d.line([sx, stop, sx, sbot], fill=(192, 138, 0), width=3)
    d.line([x + int(w * 0.40), y + int(h * 0.09),
            x + int(w * 0.60), y + int(h * 0.09)], fill=(192, 138, 0), width=3)
    d.ellipse([sx - 3, stop - 3, sx + 3, stop + 3], fill=(192, 138, 0))
    for px in (0.40, 0.60):
        cx = x + int(w * px)
        py = y + int(h * 0.09)
        d.line([cx, py, cx - int(w * 0.045), y + int(h * 0.17)],
               fill=(192, 138, 0), width=2)
        d.line([cx, py, cx + int(w * 0.045), y + int(h * 0.17)],
               fill=(192, 138, 0), width=2)
        d.polygon([(cx - int(w * 0.05), y + int(h * 0.17)),
                   (cx + int(w * 0.05), y + int(h * 0.17)),
                   (cx, y + int(h * 0.23))], fill=(192, 138, 0))
    # Peace Palace: stepped red roof over a cream hall
    d.polygon([(x + int(w * 0.08), y + int(h * 0.34)),
               (x + int(w * 0.92), y + int(h * 0.34)),
               (x + int(w * 0.86), y + int(h * 0.26)),
               (x + int(w * 0.14), y + int(h * 0.26))], fill=(150, 90, 70))
    d.rectangle([x + int(w * 0.08), y + int(h * 0.34), x + int(w * 0.92),
                 y + int(h * 0.88)], fill=(240, 238, 230))
    for fx in (0.16, 0.32, 0.48, 0.64, 0.80):  # columns
        d.rectangle([x + int(w * fx) - int(w * 0.025), y + int(h * 0.44),
                     x + int(w * fx) + int(w * 0.025), y + int(h * 0.80)],
                    fill=(200, 196, 184))
    d.rectangle([x + int(w * 0.08), y + int(h * 0.80), x + int(w * 0.92),
                 y + int(h * 0.84)], fill=(200, 196, 184))           # entablature
    # arched dark door, centre
    dx0, dx1 = x + int(w * 0.46), x + int(w * 0.54)
    d.rectangle([dx0, y + int(h * 0.70), dx1, y + int(h * 0.88)],
                fill=(60, 60, 60))
    d.pieslice([dx0, y + int(h * 0.62), dx1, y + int(h * 0.72)], 180, 360,
               fill=(60, 60, 60))


def ill_musk(d, x, y, w, h):
    """A7 — Musk at the DealBook Summit: "$446M" / "I feel pretty
    foolish". No portrait. A gold dollar disc behind a podium with a
    mic; the verified "$446M" sits on the podium front in white bold.
    Reads at small size as: big $ + podium + $446M label."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(30, 42, 66))     # stage
    d.rectangle([x, y + int(h * 0.88), x + w - 1, y + h - 1],
                fill=(20, 28, 48))                                   # floor
    # gold dollar disc, top centre
    cx, cy = x + w // 2, y + int(h * 0.28)
    r = int(min(w, h) * 0.24)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 210, 62))
    df = font(SANSB, int(r * 1.3))
    d.text((cx, cy), "$", font=df, fill=(30, 42, 66), anchor="mm")
    # podium with top slab
    d.polygon([(x + int(w * 0.30), y + int(h * 0.95)),
               (x + int(w * 0.70), y + int(h * 0.95)),
               (x + int(w * 0.64), y + int(h * 0.62)),
               (x + int(w * 0.36), y + int(h * 0.62))], fill=(122, 74, 40))
    d.rectangle([x + int(w * 0.28), y + int(h * 0.60), x + int(w * 0.72),
                 y + int(h * 0.64)], fill=(90, 52, 26))
    # mic on a stand, left of the disc so it never overlaps it
    mx = x + int(w * 0.40)
    d.line([mx, y + int(h * 0.62), mx, y + int(h * 0.52)],
           fill=(20, 20, 20), width=3)
    d.ellipse([mx - 4, y + int(h * 0.48), mx + 4, y + int(h * 0.54)],
              fill=(20, 20, 20))
    # verified figure on the podium front
    fit_text(d, "$446M", cx, y + int(h * 0.80), int(w * 0.34),
             int(h * 0.22), WHITE)


def ill_pif_tower(d, x, y, w, h):
    """A8 — PIF Tower, Riyadh: debris damage, windows blown out across
    floors. A tall glass tower with a slanted crown, floor lines, three
    cracked floors (dark blown-out panes + white zigzag cracks), a bent
    facade strip, and debris at the base; a low neighbour building
    gives the height scale. Reads at small size as: tall tower + cracks."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(214, 226, 238))  # sky
    d.rectangle([x, y + int(h * 0.90), x + w - 1, y + h - 1],
                fill=(120, 120, 120))                                # ground
    # low neighbour building, left (scale)
    d.rectangle([x + int(w * 0.05), y + int(h * 0.62), x + int(w * 0.24),
                 y + int(h * 0.90)], fill=(150, 165, 180))
    for wy in (0.68, 0.76, 0.84):
        d.rectangle([x + int(w * 0.09), y + int(h * wy),
                     x + int(w * 0.13), y + int(h * wy) + 4], fill=(60, 70, 80))
        d.rectangle([x + int(w * 0.16), y + int(h * wy),
                     x + int(w * 0.20), y + int(h * wy) + 4], fill=(60, 70, 80))
    # tower: slanted crown, left face lighter than the right
    d.polygon([(x + int(w * 0.42), y + int(h * 0.92)),
               (x + int(w * 0.42), y + int(h * 0.10)),
               (x + int(w * 0.58), y + int(h * 0.04)),
               (x + int(w * 0.62), y + int(h * 0.92))], fill=(120, 150, 180))
    d.polygon([(x + int(w * 0.42), y + int(h * 0.10)),
               (x + int(w * 0.52), y + int(h * 0.07)),
               (x + int(w * 0.52), y + int(h * 0.92)),
               (x + int(w * 0.42), y + int(h * 0.92))], fill=(150, 180, 205))
    # floor lines (staying inside the tower's tapering right edge)
    for fy in range(14, 90, 8):
        d.line([x + int(w * 0.42), y + int(h * fy / 100.0),
                x + int(w * 0.60), y + int(h * fy / 100.0)],
               fill=(90, 120, 150), width=1)
    # three cracked floors: dark blown-out pane + white zigzag crack
    for cyf in (0.30, 0.48, 0.66):
        py = y + int(h * cyf)
        d.rectangle([x + int(w * 0.46), py, x + int(w * 0.54),
                     py + int(h * 0.05)], fill=(40, 40, 40))
        d.line([(x + int(w * 0.46), py),
                (x + int(w * 0.44), py + int(h * 0.02)),
                (x + int(w * 0.47), py + int(h * 0.04)),
                (x + int(w * 0.44), py + int(h * 0.06))],
               fill=WHITE, width=2)
        d.line([(x + int(w * 0.54), py + int(h * 0.05)),
                (x + int(w * 0.56), py + int(h * 0.03)),
                (x + int(w * 0.53), py + int(h * 0.01))],
               fill=WHITE, width=2)
    # bent facade strip sticking out at the middle cracked floor
    d.polygon([(x + int(w * 0.58), y + int(h * 0.48)),
               (x + int(w * 0.66), y + int(h * 0.50)),
               (x + int(w * 0.64), y + int(h * 0.54)),
               (x + int(w * 0.58), y + int(h * 0.52))], fill=(90, 120, 150))
    # debris at the base
    for dx, dy, s in ((0.66, 0.86, 3), (0.70, 0.90, 4), (0.64, 0.93, 3),
                      (0.68, 0.70, 3)):
        d.rectangle([x + int(w * dx), y + int(h * dy),
                     x + int(w * dx) + s, y + int(h * dy) + s],
                    fill=(90, 90, 90))


def ill_anthropic(d, x, y, w, h):
    """B2 — Anthropic Nasdaq debut, ticker ANT, $83/share pricing,
    record IPO. A stock-exchange hall (pediment + columns) under a
    black ticker tape reading "ANT $83" — green ticker, white price.
    NO chart line and no first-trade price (none exists yet): the art
    states only the verified pricing. Reads at small size as:
    ticker tape + exchange hall."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(20, 32, 64))     # navy
    # ticker tape: black band, "ANT" green + "$83" white, centred
    d.rectangle([x + int(w * 0.04), y + int(h * 0.08), x + int(w * 0.96),
                 y + int(h * 0.30)], fill=(10, 10, 10))
    size = int(h * 0.18)
    while size > 9:
        fa = font(SANSB, size)
        total = (fa.getlength("ANT") + fa.getlength("  ")
                 + fa.getlength("$83"))
        if total <= int(w * 0.86):
            break
        size -= 1
    # Recompute at the final size: at short heights (v2 small cards, h~57)
    # size starts at 9, the loop above never runs, and `total` would be
    # unbound. (Found by the v2 render; the module was tested at h=124/78.)
    fa = font(SANSB, size)
    total = (fa.getlength("ANT") + fa.getlength("  ") + fa.getlength("$83"))
    cy = y + int(h * 0.19)
    tx = x + (w - total) // 2
    d.text((tx, cy), "ANT", font=fa, fill=(118, 185, 0), anchor="lm")
    d.text((tx + fa.getlength("ANT  "), cy), "$83", font=fa,
           fill=WHITE, anchor="lm")
    # exchange hall: pediment, columns, dark door, steps
    d.polygon([(x + int(w * 0.20), y + int(h * 0.52)),
               (x + int(w * 0.80), y + int(h * 0.52)),
               (x + int(w * 0.50), y + int(h * 0.38))], fill=(240, 238, 230))
    d.rectangle([x + int(w * 0.20), y + int(h * 0.52), x + int(w * 0.80),
                 y + int(h * 0.92)], fill=(240, 238, 230))
    for fx in (0.26, 0.38, 0.50, 0.62, 0.74):
        d.rectangle([x + int(w * fx) - int(w * 0.025), y + int(h * 0.58),
                     x + int(w * fx) + int(w * 0.025), y + int(h * 0.88)],
                    fill=(200, 196, 184))
    d.rectangle([x + int(w * 0.46), y + int(h * 0.74), x + int(w * 0.54),
                 y + int(h * 0.92)], fill=(40, 40, 40))
    d.rectangle([x + int(w * 0.16), y + int(h * 0.92), x + int(w * 0.84),
                 y + int(h * 0.97)], fill=(200, 196, 184))


def ill_iran_talks(d, x, y, w, h):
    """A9/A10 combined — Netanyahu–Trump Iran campaign pressure + Fox
    interview. No portraits, no weapons. Two flags (US left, Israel
    right) flanking a podium with a mic and a paper. Reads at small
    size as: two flags + podium = talks/press moment."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(214, 226, 238))  # sky
    d.rectangle([x, y + int(h * 0.88), x + w - 1, y + h - 1],
                fill=(140, 160, 120))                                # ground
    # flag poles
    for px in (0.16, 0.84):
        d.line([x + int(w * px), y + int(h * 0.10), x + int(w * px),
                y + int(h * 0.62)], fill=(50, 50, 50), width=3)
    # US flag: red/white stripes + blue canton with white dots
    fx0, fy0 = x + int(w * 0.18), y + int(h * 0.10)
    fx1, fy1 = x + int(w * 0.38), y + int(h * 0.26)
    stripe_h = (fy1 - fy0) // 4
    for i in range(4):
        col = (200, 16, 46) if i % 2 == 0 else WHITE
        d.rectangle([fx0, fy0 + i * stripe_h, fx1,
                     fy0 + (i + 1) * stripe_h - 1], fill=col)
    d.rectangle([fx0, fy0, x + int(w * 0.26), fy0 + 2 * stripe_h - 1],
                fill=(0, 57, 166))
    for dx, dy in ((0.20, 0.13), (0.23, 0.16), (0.20, 0.19)):
        d.ellipse([x + int(w * dx) - 1, y + int(h * dy) - 1,
                   x + int(w * dx) + 1, y + int(h * dy) + 1], fill=WHITE)
    # Israeli flag: white, two blue stripes, blue six-point star
    gx0, gy0 = x + int(w * 0.62), y + int(h * 0.10)
    gx1, gy1 = x + int(w * 0.82), y + int(h * 0.26)
    d.rectangle([gx0, gy0, gx1, gy1], fill=WHITE)
    d.rectangle([gx0, gy0, gx1, gy0 + int(h * 0.03)], fill=(0, 57, 166))
    d.rectangle([gx0, gy1 - int(h * 0.03), gx1, gy1], fill=(0, 57, 166))
    scx, scy = x + int(w * 0.72), y + int(h * 0.18)
    sr = int(h * 0.05)
    d.polygon([(scx, scy - sr), (scx - int(sr * 0.87), scy + sr // 2),
               (scx + int(sr * 0.87), scy + sr // 2)], fill=(0, 57, 166))
    d.polygon([(scx, scy + sr), (scx - int(sr * 0.87), scy - sr // 2),
               (scx + int(sr * 0.87), scy - sr // 2)], fill=(0, 57, 166))
    # podium with mic and paper
    d.polygon([(x + int(w * 0.36), y + int(h * 0.95)),
               (x + int(w * 0.64), y + int(h * 0.95)),
               (x + int(w * 0.60), y + int(h * 0.62)),
               (x + int(w * 0.40), y + int(h * 0.62))], fill=(122, 74, 40))
    d.rectangle([x + int(w * 0.34), y + int(h * 0.60), x + int(w * 0.66),
                 y + int(h * 0.64)], fill=(90, 52, 26))
    d.line([x + w // 2, y + int(h * 0.60), x + w // 2, y + int(h * 0.50)],
           fill=(30, 30, 30), width=3)
    d.ellipse([x + w // 2 - 4, y + int(h * 0.48), x + w // 2 + 4,
               y + int(h * 0.54)], fill=(30, 30, 30))
    d.rectangle([x + int(w * 0.46), y + int(h * 0.70), x + int(w * 0.54),
                 y + int(h * 0.78)], fill=WHITE)


def ill_cop31(d, x, y, w, h):
    """A6 — COP31 second draft strips ALL fossil-fuel references. A
    white draft document ("DRAFT" label, grey text bars) with the line
    "FOSSIL FUELS" struck through in thick red, and a small green leaf
    at the top corner. Reads at small size as: paper + red strike."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(232, 228, 210))  # desk
    # paper sheet
    px0, py0 = x + int(w * 0.16), y + int(h * 0.05)
    px1, py1 = x + int(w * 0.84), y + int(h * 0.95)
    d.rectangle([px0, py0, px1, py1], fill=WHITE, outline=(180, 180, 180),
                width=1)
    # "DRAFT" label, top left inside the paper
    d.text((px0 + int(w * 0.04), y + int(h * 0.13)), "DRAFT",
           font=font(SANSB, int(h * 0.13)), fill=(30, 90, 60), anchor="lm")
    # small green leaf, top right corner of the paper
    d.polygon([(x + int(w * 0.74), y + int(h * 0.14)),
               (x + int(w * 0.80), y + int(h * 0.08)),
               (x + int(w * 0.82), y + int(h * 0.13)),
               (x + int(w * 0.77), y + int(h * 0.16))], fill=(46, 125, 79))
    d.line([x + int(w * 0.74), y + int(h * 0.14), x + int(w * 0.71),
            y + int(h * 0.17)], fill=(46, 125, 79), width=1)
    # grey text bars (varying lengths, like draft paragraphs)
    for ry, rw in ((0.24, 0.60), (0.32, 0.60), (0.40, 0.48),
                   (0.62, 0.60), (0.70, 0.52), (0.78, 0.60),
                   (0.86, 0.44)):
        d.rectangle([px0 + int(w * 0.04), y + int(h * ry),
                     px0 + int(w * rw), y + int(h * ry) + int(h * 0.04)],
                    fill=(190, 190, 190))
    # the struck line: "FOSSIL FUELS" with a thick red line through it
    cx, cy = x + w // 2, y + int(h * 0.52)
    f, _size = fit_text(d, "FOSSIL FUELS", cx, cy, int(w * 0.56),
                        int(h * 0.16), (60, 60, 60))
    tw = f.getlength("FOSSIL FUELS")
    d.rectangle([cx - tw // 2 - 3, cy - 1, cx + tw // 2 + 3, cy + 1],
                fill=RED)


ILLUSTRATIONS = {
    "ill_crimea_bridge": ill_crimea_bridge,
    "ill_icj": ill_icj,
    "ill_musk": ill_musk,
    "ill_pif_tower": ill_pif_tower,
    "ill_anthropic": ill_anthropic,
    "ill_iran_talks": ill_iran_talks,
    "ill_cop31": ill_cop31,
}
