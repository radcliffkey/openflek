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
from scripts.deck_gen.symbols import draw_shrub, draw_suit


# Small round hawk-bell (7x8) charged on the Bell Ace shield: a loop on top,
# a red band round the middle and the slot underneath, like the suit sign.
MINI_BELL = [
    '...8...',
    '..888..',
    '.8efe8.',
    '8eeeee8',
    '8444448',
    '8eeeee8',
    '.8e8e8.',
    '..888..',
]


def _fill_ace_ground(c, top_y=52, water=True):
    """Fills the lower background with rolling green hills and optional river bank."""
    fill_terrain(c, top_y, lambda x: top_y + 2 + (x - 30) ** 2 // 120, lambda x, y, crest: checker(x, y, GREEN, LIGHT_GREEN))
    if water:
        for y in range(90, 98):
            for x in range(2, 59):
                if abs(x - 30) <= 12 + (y - 90) * 2:
                    c.put(x, y, checker(x, y, CYAN, LIGHT_CYAN))


def _overlap_foreground_turf(c, base_y=79, water=True):
    """Draws the foreground hillock over the bottom of a crest, with a row of flowering shrubs.

    `water` matches the ground's: an ace without a river gets no water here either.
    """

    def colour(x, y, crest):
        dx = abs(x - 30)
        if y <= crest + 1 and dx < 18:
            return GREEN
        if water and y >= 91 and dx <= 12 + (y - 91) * 2:
            return checker(x, y, CYAN, LIGHT_CYAN)
        return checker(x, y, GREEN, LIGHT_GREEN)

    fill_terrain(c, base_y - 3, lambda x: int(round(base_y + (x - 30) ** 2 / 140.0 + math.sin(x * 0.45) * 1.2)), colour)

    for cx, cy in [(15, base_y), (23, base_y - 1), (30, base_y - 2), (37, base_y - 1), (45, base_y)]:
        draw_shrub(c, cx, cy + 1, 4, 2.5, [(0, -2, YELLOW if cx % 2 == 0 else LIGHT_RED)])


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

    # Arched golden ribbon (x=3..57, y=19..37) with OPENFLEK lettering. It is
    # eight rows deep so a letter spanning a step of the arch still clears
    # both edges; its ends are closed off by full-height outlines.
    def arch(x):
        return 20 + (x - 30) ** 2 // 75

    for x in range(3, 58):
        arch_y = arch(x)
        c.put(x, arch_y - 1, DARK_GRAY)
        for ry in range(arch_y, arch_y + 8):
            c.put(x, ry, YELLOW)
        c.put(x, arch_y + 8, DARK_GRAY)
    for ex in (3, 57):
        c.line(ex, arch(ex) - 1, ex, arch(ex) + 8, DARK_GRAY)

    glyphs = {
        'O': ['888', '8.8', '8.8', '8.8', '888'],
        'P': ['888', '8.8', '888', '8..', '8..'],
        'E': ['888', '8..', '88.', '8..', '888'],
        # Four wide: in three columns an N reads as an M or an H.
        'N': ['8..8', '88.8', '8.88', '8..8', '8..8'],
        'F': ['888', '8..', '88.', '8..', '8..'],
        'L': ['8..', '8..', '8..', '8..', '888'],
        'K': ['8.8', '88.', '8..', '88.', '8.8'],
    }
    # Each letter sits a row under the lowest point of the ribbon's top edge
    # above it, so it never touches either outline.
    for idx, ch in enumerate('OPENFLEK'):
        lx0 = 8 + idx * 6
        ly0 = max(arch(lx0 + gx) for gx in range(len(glyphs[ch][0]))) + 1
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
    # A plain gold rim, shaded brown down its right side rather than hatched.
    Rig(c).part().poly(shield_outer).paint(YELLOW, shade=None, outline=DARK_GRAY)
    c.fill_poly(shield_inner, RED, RED, outline=DARK_GRAY, mode='solid')
    for x in range(30, 56):
        for y in range(21, 86):
            if c.get(x, y) == YELLOW and c.get(x + 1, y) == DARK_GRAY and c.get(x - 1, y) == YELLOW:
                c.put(x, y, BROWN)
    for y in range(25, 81):
        for x in range(10, 51):
            if c.get(x, y) == RED and ((x + y * 2) % 7 == 0):
                c.put(x, y, LIGHT_RED)

    # Royal St. Wenceslas Crown perched on top rim of shield (y=9..21)
    # Plain gold shaded to the lower right, not hatched, with its points kept
    # clear of the corner leaves.
    crown = Rig(c)
    crown.part().poly([(19, 21), (18, 12), (24, 16), (30, 9), (36, 16), (42, 12), (41, 21)]).paint(YELLOW, outline=DARK_GRAY)
    crown.part().rect(18, 18, 42, 21).paint(YELLOW, shade=None, outline=DARK_GRAY)
    # Cross on top, edged so the thin gold reads against the white card.
    cross = {(30, y) for y in range(4, 9)} | {(x, 6) for x in range(28, 33)}
    for x, y in cross:
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (nx, ny) not in cross and ny < 9:
                c.put(nx, ny, DARK_GRAY)
    for x, y in cross:
        c.put(x, y, YELLOW)
    for jx, jcol in [(22, LIGHT_BLUE), (26, RED), (30, LIGHT_GREEN), (34, RED), (38, LIGHT_BLUE)]:
        c.put(jx, 19, jcol)
        c.put(jx, 20, darker(jcol))

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
    # The middle plume's tip stays a row inside the frame rather than being cut flat by it.
    for tip, mid, col, end in (
        ((19, 4), (24, 6), LIGHT_RED, 1.8),
        ((41, 4), (36, 6), LIGHT_RED, 1.8),
        ((30, 4), (30, 7), LIGHT_CYAN, 1.5),
    ):
        plain.part().chain([(30, 12), mid, tip], [1.6, 2.8, end]).paint(col, outline=darker(col))
    # The steel is lit by a short glint on the dome; a white rim all down the
    # left side would read as a gap between the outline and the visor.
    helm = plain.part().ellipse(30, 22, 7.5, 8).rect(23, 22, 37, 30)
    helm.paint(LIGHT_GRAY, outline=DARK_GRAY)
    for gx, gy in ((25, 19), (26, 18), (27, 18)):
        c.put(gx, gy, WHITE)
    plain.part().rect(25, 21, 35, 28).paint(DARK_GRAY, None, outline=BLACK)
    for vx in range(26, 35, 2):
        c.line(vx, 21, vx, 28, YELLOW if vx == 30 else LIGHT_GRAY)
    # A plain gilt neck band: the shade dither would spot a band one pixel deep.
    plain.part().rect(22, 30, 38, 32).paint(YELLOW, None, outline=BROWN)
    # The crown sits down on the dome, with no white seam under its band.
    crown = plain.part().rect(24, 13, 36, 16)
    for px in (24, 30, 36):
        crown.poly([(px - 2, 14), (px, 9), (px + 2, 14)])
    crown.paint(YELLOW)
    for px, col in ((27, RED), (30, LIGHT_CYAN), (33, RED)):
        c.put(px, 15, col)

    _overlap_foreground_turf(c, base_y=82, water=False)


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
    # A solid brown line along the underside shades it without a dotted dither.
    arch_rim = arch.edge()
    arch.paint(YELLOW, shade=None, outline=DARK_GRAY, pattern=lambda x, y: BROWN if (x, y + 1) in arch_rim and (x, y + 1) not in arch.mask - arch_rim and y > 24 else None)
    for x in range(8, 54, 6):
        dx = abs(x - 30)
        c.put(x, 24 + (dx * dx) // 65, RED)

    # Wreath of leaves framing an oval of sky, roses set at intervals. The
    # sky goes first so the wreath overlaps its rim and no white gap shows.
    # The leaves share one outline; lit leaves are laid over the dark ones
    # without their own, so the ring reads as foliage, not a tangle of grey.
    sky = r.part().ellipse(30, 56, 18.5, 19.5)
    sky.paint(LIGHT_CYAN, None, outline=BLUE, pattern=lambda x, y: WHITE if y < 46 and (x + y) % 4 == 0 else None)
    leaves = [(30 + 21 * math.cos(math.radians(k * 10)), 56 + 22 * math.sin(math.radians(k * 10)), k * 10 + 90 + (25 if k % 2 else -25)) for k in range(36)]
    wreath = r.part()
    for lx, ly, ang in leaves:
        wreath.ellipse(lx, ly, 4.2, 2.2, angle=ang)
    wreath.paint(GREEN, shade=None, outline=DARK_GRAY)
    rim = wreath.edge()
    for k, (lx, ly, ang) in enumerate(leaves):
        if k % 2 == 0:
            for x, y in r.part().ellipse(lx, ly, 3.0, 1.2, angle=ang).mask - rim:
                c.put(x, y, LIGHT_GREEN)
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        rx, ry = 30 + 21 * math.cos(a), 56 + 22 * math.sin(a)
        r.part().ellipse(rx, ry, 3.2, 3.0).paint(LIGHT_RED, outline=RED)
        c.put(round(rx), round(ry), RED)
        c.put(round(rx) - 1, round(ry) - 1, WHITE)

    # Rays of light behind the heart, kept inside the sky so they don't
    # streak across the wreath.
    inside = sky.mask - sky.edge()
    for k in range(9):
        a = math.radians(200 + k * 17.5)
        for t in range(6, 14):
            x, y = round(30 + t * math.cos(a)), round(46 + t * math.sin(a))
            if (x, y) in inside:
                c.put(x, y, YELLOW)
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
