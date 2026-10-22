"""Heraldic Aces (Esa / Daus) for all 4 suits."""

import math
from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_BLUE,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_MAGENTA,
    LIGHT_RED,
    MAGENTA,
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen import animals, people
from scripts.deck_gen.symbols import draw_suit


def _fill_ace_ground(c, top_y=52, water=True):
    """Fills the lower background with rolling green hills and optional river bank."""
    for y in range(top_y, 98):
        for x in range(2, 59):
            if not c.in_interior(x, y):
                continue
            dx = abs(x - 30)
            hill_y = top_y + 2 + (dx * dx) // 120
            if y < hill_y:
                continue
            if y == hill_y:
                col = DARK_GRAY
            else:
                col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            c.put(x, y, col)

    if water:
        for y in range(90, 98):
            for x in range(2, 59):
                if not c.in_interior(x, y):
                    continue
                dx = abs(x - 30)
                if dx <= 12 + (y - 90) * 2:
                    c.put(x, y, CYAN if ((x + y) & 1) == 0 else LIGHT_CYAN)


def _overlap_foreground_turf(c, base_y=79):
    """Draws overlapping foreground hillock, mossy shadow, and bushes over a crest base."""
    for y in range(base_y - 3, 98):
        for x in range(2, 59):
            if not c.in_interior(x, y):
                continue
            dx = abs(x - 30)
            hill_y = int(round(base_y + (dx * dx) / 140.0 + math.sin(x * 0.45) * 1.2))
            if y < hill_y:
                continue
            if y == hill_y:
                col = DARK_GRAY
            elif y <= hill_y + 2 and dx < 18:
                col = GREEN if ((x + y) & 1) == 0 else DARK_GRAY
            elif y >= 91 and dx <= 12 + (y - 91) * 2:
                col = CYAN if ((x + y) & 1) == 0 else LIGHT_CYAN
            else:
                col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            c.put(x, y, col)

    for cx, cy in [(15, base_y), (23, base_y - 1), (30, base_y - 2), (37, base_y - 1), (45, base_y)]:
        c.fill_ellipse(cx, cy, 4, 2, GREEN, LIGHT_GREEN, outline=DARK_GRAY, mode='checker')
        c.put(cx, cy - 1, YELLOW if cx % 2 == 0 else LIGHT_RED)


def draw_ace_acorn(c):
    """Draws the Acorn Ace with arched OPENFLEK ribbon, top acorns & woodland crest."""
    _fill_ace_ground(c, top_y=54, water=True)

    # Top left & right acorns with oak-leaf garlands
    draw_suit(c, 0, 10, 12, 'v')
    draw_suit(c, 0, 50, 12, 'v')

    # Top central floral jewel & oak sprigs (x=23..37, y=4..19)
    c.fill_ellipse(30, 9, 4, 4, LIGHT_RED, RED, outline=DARK_GRAY)
    c.fill_ellipse(30, 9, 2, 2, YELLOW, BROWN)
    c.line(23, 7, 27, 9, GREEN)
    c.line(37, 7, 33, 9, GREEN)
    c.line(30, 13, 30, 19, DARK_GRAY)

    # Arched golden ribbon (x=3..57, y=19..34) with OPENFLEK lettering
    for x in range(3, 58):
        dx = abs(x - 30)
        arch_y = 20 + (dx * dx) // 75
        c.put(x, arch_y - 1, DARK_GRAY)
        for ry in range(arch_y, arch_y + 7):
            c.put(x, ry, YELLOW)
        c.put(x, arch_y + 7, DARK_GRAY)
    c.line(3, 28, 3, 34, DARK_GRAY)
    c.line(57, 28, 57, 34, DARK_GRAY)

    glyphs = {
        'O': ['888', '8.8', '8.8', '8.8', '888'],
        'P': ['888', '8.8', '888', '8..', '8..'],
        'E': ['888', '8..', '88.', '8..', '888'],
        'N': ['8.8', '888', '888', '8.8', '8.8'],
        'F': ['888', '8..', '88.', '8..', '8..'],
        'L': ['8..', '8..', '8..', '8..', '888'],
        'K': ['8.8', '8.8', '88.', '8.8', '8.8'],
    }
    for idx, ch in enumerate('OPENFLEK'):
        lx0 = 8 + idx * 6
        dx = abs((lx0 + 1) - 30)
        ly0 = 21 + (dx * dx) // 75
        for gy, row in enumerate(glyphs[ch]):
            for gx, p in enumerate(row):
                if p == '8':
                    c.put(lx0 + gx, ly0 + gy, DARK_GRAY)

    # An oak behind him: trunk and a round crown of leaves dotted with acorns.
    c.fill_rect(27, 60, 33, 84, BROWN, DARK_GRAY, mode='vstripe')
    c.fill_ellipse(30, 55, 25, 19, GREEN, LIGHT_GREEN, outline=DARK_GRAY, mode='sparse')
    acorn = ['.6.', '666', 'eee', 'eee', '.e.']
    for ax, ay in ((11, 48), (19, 40), (41, 40), (49, 48), (8, 60), (52, 60), (15, 67), (45, 67)):
        c.blit_centered(acorn, ax, ay)

    # The wild man of Czech heraldry standing before the oak.
    people.draw_wild_man(c)

    _overlap_foreground_turf(c, base_y=84)

    # Twin O / F golden medallions nestled in the foreground turf (y=75..87)
    c.fill_ellipse(11, 81, 6, 6, YELLOW, BROWN, outline=DARK_GRAY)
    c.fill_ellipse(49, 81, 6, 6, YELLOW, BROWN, outline=DARK_GRAY)
    c.rect(9, 79, 13, 83, RED)
    c.line(47, 79, 47, 83, RED)
    c.line(47, 79, 51, 79, RED)
    c.line(47, 81, 50, 81, RED)


def draw_ace_leaf(c):
    """Draws the Leaf Ace: Crowned Bohemian Double-Tailed Lion inside a Linden Wreath."""
    _fill_ace_ground(c, top_y=52, water=True)

    # Top-left and top-right leaves
    draw_suit(c, 1, 10, 11, 'v')
    draw_suit(c, 1, 50, 11, 'v')

    # Lush linden & oak wreath wrapping around the shield (center=(30, 50), rx=27, ry=29)
    c.fill_ellipse(30, 50, 27, 29, GREEN, LIGHT_GREEN, outline=DARK_GRAY, mode='checker')
    for angle_deg in range(0, 360, 22):
        rad = math.radians(angle_deg)
        bx = int(round(30 + 24.5 * math.cos(rad)))
        by = int(round(50 + 26.5 * math.sin(rad)))
        c.put(bx, by, YELLOW)
        c.put(bx + 1, by, LIGHT_RED)

    # Grand Gothic/Baroque Heraldic Shield (x=6..54, y=21..85)
    shield_outer = [(6, 21), (54, 21), (53, 58), (45, 74), (30, 85), (15, 74), (7, 58)]
    shield_inner = [(9, 24), (51, 24), (50, 57), (43, 72), (30, 82), (17, 72), (10, 57)]
    c.fill_poly(shield_outer, YELLOW, BROWN, outline=DARK_GRAY)
    c.fill_poly(shield_inner, RED, RED, outline=DARK_GRAY, mode='solid')
    for y in range(25, 81):
        for x in range(10, 51):
            if c.get(x, y) == RED and ((x + y * 2) % 7 == 0):
                c.put(x, y, LIGHT_RED)

    # Royal St. Wenceslas Crown perched on top rim of shield (y=9..21)
    c.fill_poly([(18, 21), (16, 12), (23, 16), (30, 9), (37, 16), (44, 12), (42, 21)], YELLOW, BROWN, outline=DARK_GRAY)
    c.fill_rect(18, 18, 42, 21, YELLOW, RED, mode='hstripe')
    c.rect(18, 18, 42, 21, DARK_GRAY)
    c.line(30, 5, 30, 9, YELLOW)
    c.line(28, 7, 32, 7, YELLOW)
    for jx, jcol in [(22, LIGHT_BLUE), (26, RED), (30, LIGHT_GREEN), (34, RED), (38, LIGHT_BLUE)]:
        c.put(jx, 19, jcol)

    # Rampant double-tailed Bohemian lion centered inside the crimson shield
    animals.draw_lion_rampant(c)

    # Overlapping foreground hillock & bushes cradling the lower shield
    _overlap_foreground_turf(c, base_y=79)


def draw_ace_bell(c):
    """Draws the Bell Ace: Tournament Helm, Acanthus Mantling & Quartered Coat of Arms."""
    _fill_ace_ground(c, top_y=52, water=False)

    # Top-left and top-right bells
    draw_suit(c, 2, 11, 12)
    draw_suit(c, 2, 49, 12)

    # Crested Knight's Tournament Helm at top center (y=10..33, x=21..39)
    c.fill_ellipse(25, 14, 5, 3, LIGHT_RED, RED, outline=RED)
    c.fill_ellipse(35, 14, 5, 3, YELLOW, BROWN, outline=BROWN)
    c.fill_ellipse(30, 12, 4, 4, LIGHT_CYAN, CYAN, outline=BLUE)
    c.fill_ellipse(30, 24, 8, 8, LIGHT_GRAY, WHITE, outline=DARK_GRAY)
    for vx in range(25, 36, 2):
        c.line(vx, 20, vx, 28, YELLOW if vx == 30 else DARK_GRAY)
    # Flowing crimson/magenta & gold mantling scrolls flanking helm and shield
    c.fill_ellipse(15, 30, 7, 6, LIGHT_MAGENTA, MAGENTA, outline=DARK_GRAY)
    c.fill_ellipse(45, 30, 7, 6, LIGHT_MAGENTA, MAGENTA, outline=DARK_GRAY)
    c.fill_ellipse(30, 55, 26, 26, GREEN, LIGHT_GREEN, outline=DARK_GRAY, mode='checker')

    # Golden baroque cartouche border reaching down to y=84
    c.fill_poly([(9, 32), (51, 32), (52, 62), (30, 84), (8, 62)], YELLOW, BROWN, outline=DARK_GRAY)
    # Inner quartered shield (x=13..47, y=35..76)
    c.fill_rect(13, 35, 30, 55, CYAN, BLUE, mode='drape')
    c.fill_rect(30, 55, 47, 76, CYAN, BLUE, mode='drape')
    c.fill_rect(30, 35, 47, 55, LIGHT_RED, RED, mode='drape')
    c.fill_rect(13, 55, 30, 76, LIGHT_RED, RED, mode='drape')
    c.rect(13, 35, 47, 76, DARK_GRAY)
    c.line(30, 35, 30, 76, YELLOW)
    c.line(13, 55, 47, 55, YELLOW)

    # Heraldic charges in the 4 quarters
    for qx, qy in [(21, 45), (39, 45), (21, 65), (39, 65)]:
        c.fill_ellipse(qx, qy, 4, 4, YELLOW, WHITE, outline=BROWN)
        c.line(qx - 2, qy, qx + 2, qy, RED)

    # Central Bell escutcheon at (30, 55)
    c.fill_ellipse(30, 55, 6, 6, WHITE, LIGHT_GRAY, outline=DARK_GRAY)
    c.fill_ellipse(30, 55, 4, 4, YELLOW, BROWN, outline=BROWN)
    c.line(27, 55, 33, 55, RED)

    _overlap_foreground_turf(c, base_y=80)


def draw_ace_heart(c):
    """Draws the Heart Ace: Golden Arch, Rose Wreath & Crowned Chalice Monument."""
    _fill_ace_ground(c, top_y=54, water=True)

    # Top-left and top-right hearts
    draw_suit(c, 3, 12, 12)
    draw_suit(c, 3, 48, 12)

    # Overarching golden baroque scroll arch (y=21..35, x=4..56)
    for x in range(4, 57):
        dx = abs(x - 30)
        ay = 22 + (dx * dx) // 65
        c.put(x, ay - 1, DARK_GRAY)
        for ry in range(ay, ay + 6):
            c.put(x, ry, YELLOW if ((x + ry) & 1) == 0 else BROWN)
        c.put(x, ay + 6, DARK_GRAY)

    # Lush rose-and-leaf oval wreath (center=(30, 56), rx=25, ry=26, reaching y=30..82)
    c.fill_ellipse(30, 56, 25, 26, GREEN, LIGHT_GREEN, outline=DARK_GRAY, mode='checker')
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        rx = int(round(30 + 21 * math.cos(rad)))
        ry = int(round(56 + 22 * math.sin(rad)))
        c.fill_ellipse(rx, ry, 3, 3, LIGHT_RED, RED, outline=DARK_GRAY)
        c.put(rx, ry, YELLOW)

    # Inner golden & azure cartouche shield
    c.fill_ellipse(30, 56, 17, 19, YELLOW, BROWN, outline=DARK_GRAY)
    c.fill_ellipse(30, 56, 14, 16, LIGHT_CYAN, CYAN, outline=BLUE)

    # Golden royal chalice & glowing crowned heart inside the cartouche
    c.fill_poly([(22, 53), (38, 53), (34, 62), (26, 62)], YELLOW, WHITE, outline=BROWN)
    c.fill_rect(28, 62, 32, 68, YELLOW, BROWN, mode='vstripe')
    c.rect(28, 62, 32, 68, DARK_GRAY)
    c.fill_rect(22, 68, 38, 72, YELLOW, BROWN, mode='hstripe')
    c.rect(22, 68, 38, 72, DARK_GRAY)
    # Heart rising above the chalice
    draw_suit(c, 3, 30, 46)

    _overlap_foreground_turf(c, base_y=80)


def draw_ace_card(c, suit):
    """Draws an Ace card for the given suit (0=Acorns, 1=Leaves, 2=Bells, 3=Hearts)."""
    if suit == 0:
        draw_ace_acorn(c)
    elif suit == 1:
        draw_ace_leaf(c)
    elif suit == 2:
        draw_ace_bell(c)
    else:
        draw_ace_heart(c)
