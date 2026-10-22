"""Heraldic Aces (Esa / Daus) for all 4 suits."""

import math
from scripts.deck_gen.palette import (
    BLACK,
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_BLUE,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen import animals, people
from scripts.deck_gen.palette import checker, fill_terrain
from scripts.deck_gen.rig import Rig, darker
from scripts.deck_gen.symbols import draw_suit


# Small gold bell (7x7) charged on the Bell Ace shield.
MINI_BELL = [
    '...8...',
    '..8e8..',
    '.8efe8.',
    '.8eee8.',
    '8eeeee8',
    '8444448',
    '.88688.',
]


def _fill_ace_ground(c, top_y=52, water=True):
    """Fills the lower background with rolling green hills and optional river bank."""
    fill_terrain(c, top_y, lambda x: top_y + 2 + (x - 30) ** 2 // 120, lambda x, y, crest: checker(x, y, GREEN, LIGHT_GREEN))
    if water:
        for y in range(90, 98):
            for x in range(2, 59):
                if abs(x - 30) <= 12 + (y - 90) * 2:
                    c.put(x, y, checker(x, y, CYAN, LIGHT_CYAN))


def _overlap_foreground_turf(c, base_y=79):
    """Draws overlapping foreground hillock, mossy shadow, and bushes over a crest base."""

    def colour(x, y, crest):
        dx = abs(x - 30)
        if y <= crest + 2 and dx < 18:
            return checker(x, y, GREEN, DARK_GRAY)
        if y >= 91 and dx <= 12 + (y - 91) * 2:
            return checker(x, y, CYAN, LIGHT_CYAN)
        return checker(x, y, GREEN, LIGHT_GREEN)

    fill_terrain(c, base_y - 3, lambda x: int(round(base_y + (x - 30) ** 2 / 140.0 + math.sin(x * 0.45) * 1.2)), colour)

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

    # Acanthus mantling flowing from the helm down both sides of the shield:
    # cyan cloth with a gold lining, its edge cut into curling leaves.
    for flip in (False, True):
        r = Rig(c, flip=flip)
        stem = [(26, 30), (17, 31), (10, 38), (7, 48), (10, 57), (7, 66), (11, 74)]
        mant = r.part().chain(stem, [3.0, 3.6, 3.8, 3.6, 3.2, 2.8, 2.2])
        for (ax, ay), (bx, by) in zip(stem[1:], stem[2:]):
            mant.ellipse((ax + bx) / 2 - 3, (ay + by) / 2, 3.2, 2.4, angle=-30)
        mant.paint(CYAN, shade=BLUE, outline=BLUE)
        r.part().chain(stem[1:-1], [1.3, 1.5, 1.5, 1.3, 1.1]).paint(YELLOW, None, outline=None)

    # Heater shield quartered azure and gules, with a gold rim.
    rim = [(12, 34), (48, 34), (48, 58), (45, 68), (38, 76), (30, 81), (22, 76), (15, 68), (12, 58)]
    field = [(15, 37), (45, 37), (45, 58), (42, 67), (36, 73), (30, 77), (24, 73), (18, 67), (15, 58)]
    plain = Rig(c)
    plain.part().poly(rim).paint(YELLOW, outline=DARK_GRAY)
    shield = plain.part().poly(field)

    def quarters(x, y):
        return LIGHT_RED if (x < 30) == (y < 56) else CYAN

    shield.paint(CYAN, None, outline=DARK_GRAY, pattern=quarters)
    c.line(30, 37, 30, 77, YELLOW)
    c.line(15, 56, 45, 56, YELLOW)
    for qx, qy in [(22, 46), (38, 46), (22, 64), (38, 64)]:
        c.blit_centered(MINI_BELL, qx, qy)

    # Barred tournament helm above the shield, crowned and plumed.
    for tip, mid, col in (((19, 4), (24, 6), LIGHT_RED), ((41, 4), (36, 6), LIGHT_RED), ((30, 1), (30, 5), LIGHT_CYAN)):
        plain.part().chain([(30, 12), mid, tip], [1.6, 2.8, 1.8]).paint(col, outline=darker(col))
    helm = plain.part().ellipse(30, 22, 7.5, 8).rect(23, 22, 37, 30)
    helm.paint(LIGHT_GRAY, light=WHITE, outline=DARK_GRAY)
    plain.part().rect(25, 21, 35, 28).paint(DARK_GRAY, None, outline=BLACK)
    for vx in range(26, 35, 2):
        c.line(vx, 21, vx, 28, YELLOW if vx == 30 else LIGHT_GRAY)
    plain.part().rect(22, 30, 38, 32).paint(YELLOW)
    crown = plain.part().rect(24, 12, 36, 15)
    for px in (24, 30, 36):
        crown.poly([(px - 2, 13), (px, 8), (px + 2, 13)])
    crown.paint(YELLOW)
    for px, col in ((27, RED), (30, LIGHT_CYAN), (33, RED)):
        c.put(px, 14, col)

    _overlap_foreground_turf(c, base_y=82)


def draw_ace_heart(c):
    """Draws the Heart Ace: Golden Arch, Rose Wreath & Crowned Chalice Monument."""
    _fill_ace_ground(c, top_y=54, water=True)

    # Top-left and top-right hearts
    draw_suit(c, 3, 12, 12)
    draw_suit(c, 3, 48, 12)

    r = Rig(c)
    # Golden arch over the wreath, studded with garnets.
    arch = r.part()
    for x in range(4, 57):
        dx = abs(x - 30)
        arch.rect(x, 22 + (dx * dx) // 65, x, 27 + (dx * dx) // 65)
    arch.paint(YELLOW, outline=DARK_GRAY)
    for x in range(8, 54, 6):
        dx = abs(x - 30)
        c.put(x, 24 + (dx * dx) // 65, RED)

    # Wreath of leaves around an oval of sky, roses set at intervals.
    for k in range(36):
        a = math.radians(k * 10)
        lx, ly = 30 + 21 * math.cos(a), 56 + 22 * math.sin(a)
        col = GREEN if k % 2 else LIGHT_GREEN
        r.part().ellipse(lx, ly, 4.2, 2.2, angle=k * 10 + 90 + (25 if k % 2 else -25)).paint(col, outline=DARK_GRAY)
    r.part().ellipse(30, 56, 17, 18).paint(LIGHT_CYAN, None, outline=BLUE, pattern=lambda x, y: WHITE if y < 46 and (x + y) % 4 == 0 else None)
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        rx, ry = 30 + 21 * math.cos(a), 56 + 22 * math.sin(a)
        r.part().ellipse(rx, ry, 3.2, 3.0).paint(LIGHT_RED, outline=RED)
        c.put(round(rx), round(ry), RED)
        c.put(round(rx) - 1, round(ry) - 1, WHITE)

    # Rays of light behind the heart.
    for k in range(9):
        a = math.radians(200 + k * 17.5)
        c.line(30 + 6 * math.cos(a), 46 + 6 * math.sin(a), 30 + 13 * math.cos(a), 46 + 13 * math.sin(a), YELLOW)
    draw_suit(c, 3, 30, 46)

    # Golden chalice: wide cup, knopped stem and a broad foot.
    cup = r.part().poly([(21, 55), (39, 55), (36, 63), (31, 66), (29, 66), (24, 63)]).ellipse(30, 55, 9, 1.6)
    cup.paint(YELLOW, light=WHITE, outline=BROWN, pattern=lambda x, y: RED if y == 59 and x % 3 == 0 else None)
    r.part().ellipse(30, 55, 8, 1.2).fill(BROWN)
    r.part().rect(29, 66, 31, 71).ellipse(30, 68.5, 2.4, 1.4).paint(YELLOW, outline=BROWN)
    r.part().poly([(24, 75), (36, 75), (33, 71), (27, 71)]).ellipse(30, 75, 6.5, 1.5).paint(YELLOW, outline=BROWN)

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
