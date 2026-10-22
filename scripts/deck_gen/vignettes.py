"""Number cards (7, 8, 9, 10) and their 16 large, high-detail EGA pixel-art vignettes."""

import math

from scripts.deck_gen import animals, people
from scripts.deck_gen.palette import (
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
    checker,
    fill_terrain,
)
from scripts.deck_gen.rig import Rig
from scripts.deck_gen.symbols import (
    draw_floret,
    draw_roman_x,
    draw_shrub,
    draw_suit,
    draw_tree_trunk,
)

# The vignettes are drawn from shapes: people and animals by `people` and
# `animals`, buildings and garden pieces by the helpers below. Only the
# heart target on Cupid's post and the small obelisk beside the peacock are
# hand-pixelled sprites: at their size a shape outline would eat the detail.

# Heart 9 left: gilded obelisk with a heart finial on a stone plinth (11x27),
# lit from the left; it stays below the lowest left pip.
SPRITE_OBELISK = [
    '...44.44...',
    '..4fc4cc4..',
    '..4ccccc4..',
    '...4ccc4...',
    '....4c4....',
    '.....4.....',
    '.....6.....',
    '....6e6....',
    '....6e6....',
    '...6fe66...',
    '...6fe66...',
    '...6fe66...',
    '...6fe66...',
    '...6fe66...',
    '...6fe66...',
    '..6ffee66..',
    '..6ffee66..',
    '..6ffee66..',
    '..6ffee66..',
    '..6ffee66..',
    '..6ffee66..',
    '.888888888.',
    '.8fffff778.',
    '88888888888',
    '8ffffff7778',
    '8ffffff7778',
    '88888888888',
]

# Heart 10 left: Heart target on a post for Cupid to aim at (9x18)
SPRITE_HEART_POST = [
    '.44...44.',
    '4cc4.4cc4',
    '4fcccccc4',
    '4ccccccc4',
    '.4ccccc4.',
    '..4ccc4..',
    '...4c4...',
    '....4....',
    '...6e6...',
    '...6e6...',
    '...6e6...',
    '...6e6...',
    '...6e6...',
    '...6e6...',
    '...6e6...',
    '...6e6...',
    '..86e68..',
    '..88888..',
]


def draw_ground(c, suit, rank):
    """Draws rolling turf at the bottom (y=80..97) with a path or clearing for each suit."""

    def colour(x, y, crest):
        if suit == 0:  # Acorns: a golden forest path winding down
            if abs(x - (29 + (y - 86))) <= 10 and y >= 88:
                return checker(x, y, YELLOW, BROWN)
        elif suit == 1:  # Leaves: a sunlit meadow clearing
            if y >= 89 and abs(x - 31) <= 14:
                return checker(x, y, YELLOW, LIGHT_GREEN)
        elif suit == 2:  # Bells: a golden road
            if y >= 88 and abs(x - 30) <= 16:
                return checker(x, y, YELLOW, BROWN)
        elif y >= 90:  # Hearts: a golden parterre
            return checker(x, y, YELLOW, LIGHT_GREEN)
        return checker(x, y, GREEN, LIGHT_GREEN)

    fill_terrain(c, 80, lambda x: 84 + int(round(math.sin((x + suit * 7 + rank * 5) * 0.22) * 2.0)), colour)


def draw_bush_or_flowers(c, cx, base_y, col):
    """Draws a flowering bush rooted into the turf at base_y..base_y+1."""
    blooms = [(dx, dy, col) for dx, dy in [(-3, -3), (0, -5), (3, -3), (-1, -2), (2, -4)]]
    draw_shrub(c, cx, base_y + 1, 6, 4, blooms + [(0, -3, YELLOW)])


def _draw_obelisk(c, cx, base_y):
    """A slender gilded garden obelisk on a stepped plinth, topped by a small heart."""
    c.blit_sprite(SPRITE_OBELISK, cx - 5, base_y - len(SPRITE_OBELISK) + 1)


def _draw_cottage(c, cx, base_y):
    """A Czech log cottage (roubenka) gable-on: dark logs with white chinking, a boarded gable,
    a red tiled roof with a smoking chimney, a window with a flower box and a plank door."""
    r = Rig(c)
    left, right, eave = cx - 9, cx + 9, base_y - 12
    # A wisp of smoke blown to the right, short enough to stay clear of the pip above.
    for sx, sy in ((5, -13), (6, -14), (7, -14), (8, -15), (9, -16), (10, -16)):
        c.put(cx + sx, eave + sy, LIGHT_GRAY)
    # Log walls: brown logs, each with a white band of chinking beneath it.
    walls = r.part().rect(left, eave, right, base_y - 1)
    walls.paint(BROWN, shade=None, outline=DARK_GRAY, pattern=lambda x, y: WHITE if (y - eave) % 3 == 2 else (YELLOW if (x + y) % 7 == 0 else None))
    # Log ends sticking out at the corners.
    for y in range(eave + 1, base_y - 1, 3):
        for x in (left - 1, right + 1):
            c.put(x, y, YELLOW)
            c.put(x, y + 1, BROWN)
    # Boarded gable and the roof over it.
    gable = r.part().poly([(left + 1, eave), (right - 1, eave), (cx, eave - 9)])
    gable.paint(YELLOW, shade=None, outline=BROWN, pattern=lambda x, y: BROWN if (x - cx) % 2 == 0 else None)
    r.part().ellipse(cx, eave - 4, 1.5, 1.5).paint(LIGHT_CYAN, None, outline=DARK_GRAY)
    for side in (-1, 1):
        slope = r.part().chain([(cx, eave - 11), (cx + side * 12, eave + 1)], [1.6, 1.6])
        slope.paint(LIGHT_RED, outline=RED, pattern=lambda x, y: RED if (x + y) % 3 == 0 else None)
    r.part().rect(cx + 4, eave - 12, cx + 6, eave - 6).paint(LIGHT_RED, outline=DARK_GRAY, pattern=lambda x, y: RED if y % 2 else None)
    # Window with a cross of glazing bars and a box of flowers; plank door.
    r.part().rect(left + 2, eave + 3, left + 7, eave + 7).paint(WHITE, None, outline=DARK_GRAY)
    r.part().rect(left + 3, eave + 4, left + 6, eave + 6).fill(LIGHT_CYAN)
    c.line(left + 3, eave + 5, left + 6, eave + 5, WHITE)
    c.line(left + 4, eave + 4, left + 4, eave + 6, WHITE)
    c.line(left + 2, eave + 8, left + 7, eave + 8, GREEN)
    for fx in (left + 3, left + 5, left + 7):
        c.put(fx, eave + 7, LIGHT_RED)
    r.part().rect(right - 6, eave + 4, right - 2, base_y - 1).paint(YELLOW, None, outline=DARK_GRAY, pattern=lambda x, y: BROWN if x % 2 else None)
    c.put(right - 3, eave + 8, DARK_GRAY)
    # Stone step and a path of beaten earth.
    c.line(right - 7, base_y, right - 1, base_y, LIGHT_GRAY)


def _water_arc(c, x0, y0, x1, y1):
    """A stream leaving a lip sideways and falling ever more steeply to (x1, y1), with a splash.

    Drawn in cyan, not white or light cyan, so it still shows on the white card.
    """
    steps = (abs(x1 - x0) + abs(y1 - y0)) * 3
    for k in range(steps + 1):
        t = k / steps
        c.put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t * t, CYAN)
    side = 1 if x1 > x0 else -1
    c.put(x1 + side, y1 - 1, CYAN)
    c.put(x1 - side, y1 - 1, CYAN)


def _fountain_basin(c, cx, top, half, depth):
    """A stone dish seen slightly from above: back rim, a line of water, a lit lip and a shaded underside."""
    c.line(cx - half + 2, top, cx + half - 2, top, DARK_GRAY)
    c.put(cx - half + 1, top + 1, DARK_GRAY)
    c.put(cx + half - 1, top + 1, DARK_GRAY)
    for x in range(cx - half + 2, cx + half - 1):
        c.put(x, top + 1, CYAN if (x - cx) % 4 == 1 or x >= cx + half - 4 else LIGHT_CYAN)
    bowl = Rig(c).part().poly([(cx - half, top + 2), (cx + half, top + 2), (cx + 2, top + 2 + depth), (cx - 2, top + 2 + depth)])
    bowl.paint(
        LIGHT_GRAY,
        shade=None,
        outline=DARK_GRAY,
        light=WHITE,
        pattern=lambda x, y: (WHITE if x < cx + half // 2 else LIGHT_GRAY) if y == top + 3 else None,
    )


def _draw_fountain(c, cx, base_y):
    """A two-tiered stone fountain in a red brick pool, water spilling from tier to tier."""
    # Pool: back coping, two rows of water, front coping and a brick wall.
    pool = base_y - 11
    c.line(cx - 16, pool, cx + 16, pool, DARK_GRAY)
    for x in range(cx - 17, cx + 18):
        c.put(x, pool + 1, DARK_GRAY if abs(x - cx) == 17 else (LIGHT_GRAY if x > cx + 10 else WHITE))
    for h, y in ((18, pool + 2), (19, pool + 3)):
        for x in range(cx - h, cx + h + 1):
            if abs(x - cx) == h:
                col = DARK_GRAY
            elif x == cx - h + 1:
                col = WHITE
            elif x == cx + h - 1:
                col = LIGHT_GRAY
            else:
                col = CYAN if (x * 3 + y * 5) % 7 == 0 or x > cx + h - 4 else LIGHT_CYAN
            c.put(x, y, col)
    # Pedestal standing in the water, flared at its foot.
    for y in range(base_y - 18, pool + 4):
        flare = 3 if y >= pool + 2 else 2
        for x in range(cx - flare, cx + flare + 1):
            c.put(x, y, DARK_GRAY if abs(x - cx) == flare else (LIGHT_GRAY if x > cx else WHITE))
    c.line(cx - 3, pool + 1, cx + 3, pool + 1, DARK_GRAY)
    c.line(cx - 19, pool + 4, cx + 19, pool + 4, DARK_GRAY)
    for x in range(cx - 19, cx + 20):
        c.put(x, pool + 5, DARK_GRAY if abs(x - cx) == 19 else (LIGHT_GRAY if x > cx + 12 else WHITE))
    c.line(cx - 19, pool + 6, cx + 19, pool + 6, DARK_GRAY)
    for y in range(pool + 7, base_y + 1):
        course = y - pool - 7
        for x in range(cx - 19, cx + 20):
            if abs(x - cx) == 19 or y == base_y:
                col = DARK_GRAY
            elif course == 2 or (x - cx + (3 if course > 2 else 0)) % 6 == 0:
                col = RED
            else:
                col = LIGHT_RED
            c.put(x, y, col)
    # Lower basin, then the upper bowl on a slim stem.
    low = base_y - 22
    _fountain_basin(c, cx, low, 12, 4)
    up = base_y - 29
    for y in range(up + 4, low + 1):
        c.put(cx - 1, y, DARK_GRAY)
        c.put(cx, y, WHITE)
        c.put(cx + 1, y, DARK_GRAY)
    _fountain_basin(c, cx, up, 6, 3)
    # Water: a short plume into the upper bowl, which spills over its lip
    # into the basin, which spills in turn into the pool.
    for y in range(up - 3, up + 1):
        c.put(cx, y, CYAN)
    for side in (-1, 1):
        c.put(cx + side, up - 3, CYAN)
        c.put(cx + side * 2, up - 2, CYAN)
        c.put(cx + side * 2, up - 1, CYAN)
        _water_arc(c, cx + side * 7, up + 2, cx + side * 9, low + 1)
        _water_arc(c, cx + side * 13, low + 2, cx + side * 16, pool + 2)


def _draw_urn(c, cx, base_y):
    """A gilded garden urn with scrolled handles, planted with a flowering rose bush."""
    r = Rig(c)
    # The bush first, so the urn's rim sits in front of it.
    bush = r.part().ellipse(cx, base_y - 19, 10, 5.5).ellipse(cx - 6, base_y - 16, 5, 3.5).ellipse(cx + 6, base_y - 16, 5, 3.5)
    bush.paint(GREEN, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GREEN if (x * 2 + y) % 5 == 0 else None)
    roses = {LIGHT_RED: ['.cc.', 'c4cc', '.cc.'], YELLOW: ['.ee.', 'e6ee', '.ee.']}
    # The roses at the sides sit inside the bush's outline, never yellow straight on the white card.
    for rx, ry, col in ((-6, -20, LIGHT_RED), (0, -23, YELLOW), (6, -20, LIGHT_RED), (-3, -16, YELLOW), (4, -16, LIGHT_RED), (-7, -17, YELLOW), (8, -17, YELLOW)):
        c.blit_centered(roses[col], cx + rx, base_y + ry)
    for side in (-1, 1):
        r.part().chain([(cx + side * 6, base_y - 11), (cx + side * 10, base_y - 11), (cx + side * 9, base_y - 7), (cx + side * 6, base_y - 7)], [0.8] * 4).fill(BROWN)
    # Gilt lit by a glint at the upper left, not a white rim that would read
    # as a gap inside the outline; bands a pixel deep get no shade dither.
    body = r.part().ellipse(cx, base_y - 9, 7, 5).rect(cx - 7, base_y - 13, cx + 7, base_y - 11)
    body.paint(YELLOW, outline=BROWN, pattern=lambda x, y: RED if y == base_y - 9 and x % 3 == 0 else None)
    for gy in (base_y - 11, base_y - 10):
        c.put(cx - 4, gy, WHITE)
    r.part().ellipse(cx, base_y - 13, 8, 1.5).paint(YELLOW, None, outline=BROWN)
    r.part().rect(cx - 2, base_y - 5, cx + 2, base_y - 3).paint(YELLOW, None, outline=BROWN)
    foot = r.part().poly([(cx - 3, base_y - 2.5), (cx + 3, base_y - 2.5), (cx + 6, base_y + 0.5), (cx - 6, base_y + 0.5)])
    foot.paint(YELLOW, None, outline=BROWN)


def _draw_heart_tub(c, cx, base_y):
    """A hooped wooden tub holding a box tree clipped into a heart, studded with roses."""
    r = Rig(c)
    # Stem: a brown core between dark edges, so it reads against the white card.
    rim = base_y - 10
    top = base_y - 27
    for y in range(top + 13, rim):
        c.put(cx - 1, y, DARK_GRAY)
        c.put(cx, y, BROWN)
        c.put(cx + 1, y, DARK_GRAY)
    # The clipped heart: a lit crescent on the upper left of each lobe, and a
    # few leaf tips scattered by a hash rather than a regular dither.
    lobes = ((cx - 4.5, top + 5), (cx + 4.5, top + 5))
    heart = r.part()
    for lx, ly in lobes:
        heart.ellipse(lx, ly, 5.2, 4.8)
    heart.poly([(cx - 9.7, top + 6), (cx + 9.7, top + 6), (cx, top + 15)])
    outline = heart.edge()

    def leaves(x, y):
        for lx, ly in lobes:
            d2 = (x - lx) ** 2 + (y - ly) ** 2
            if 6 < d2 <= 16 and (x - lx) + (y - ly) <= -2:
                return LIGHT_GREEN
        h = (x * 37 + y * 91) % 11
        if h == 0:
            return LIGHT_GREEN
        if h == 5 and (x - cx) + (y - top) > 9 and not {(x + 1, y), (x, y + 1)} & outline:
            return DARK_GRAY
        return None

    heart.paint(GREEN, shade=None, outline=DARK_GRAY, pattern=leaves)
    # Roses: a light petal face over a dark red lower right, kept off the outline.
    inside = heart.mask - heart.edge()
    for rx, ry in ((-6, 4), (3, 3), (-1, 7), (5, 7), (-5, 9), (0, 11)):
        x, y = cx + rx, top + ry
        if {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)} <= inside:
            c.put(x, y, LIGHT_RED)
            c.put(x + 1, y, LIGHT_RED)
            c.put(x, y + 1, LIGHT_RED)
            c.put(x + 1, y + 1, RED)
    # Tub: a lipped rim, then staves narrowing to the foot, bound by two iron hoops.
    c.line(cx - 10, rim, cx + 10, rim, DARK_GRAY)
    c.line(cx - 10, rim + 2, cx + 10, rim + 2, DARK_GRAY)
    c.put(cx - 10, rim + 1, DARK_GRAY)
    c.put(cx + 10, rim + 1, DARK_GRAY)
    c.line(cx - 9, rim + 1, cx + 9, rim + 1, YELLOW)
    c.line(cx + 5, rim + 1, cx + 9, rim + 1, BROWN)
    bottom = base_y - 1
    for y in range(rim + 3, bottom + 1):
        # The staves step in under the upper hoop and again at the foot.
        half = 9 if y <= rim + 4 else (7 if y == bottom else 8)
        for x in range(cx - half, cx + half + 1):
            if x in (cx - half, cx + half) or y == bottom:
                col = DARK_GRAY
            elif y in (rim + 4, bottom - 2):
                col = LIGHT_GRAY if x == cx - half + 2 else DARK_GRAY
            elif (x - cx) % 3 == 1:
                col = BROWN
            else:
                col = YELLOW if x < cx + 3 else BROWN
            c.put(x, y, col)


def draw_vignette_scene(c, suit, rank):
    """Draws one of the 16 large, grounded bottom scenes (y=60..91).

    Animals are scaled so they stay below the lowest pips of their card.
    """
    draw_ground(c, suit, rank)
    gy = 88

    if (suit, rank) == (0, 0):  # Acorn 7: Forester smoking a pipe beside a timbered cottage
        _draw_cottage(c, 46, gy - 1)
        people.draw_forester(c)
    elif (suit, rank) == (0, 1):  # Acorn 8: Huntsman sitting in the grass playing a pipe, his dog by him
        people.draw_hornblower(c)
        animals.draw_dog(c, flip=True)
    elif (suit, rank) == (0, 2):  # Acorn 9: Cock pheasant perched on an oak bough
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        animals.draw_pheasant(c)
    elif (suit, rank) == (0, 3):  # Acorn 10: Wild boar trotting across a forest clearing
        draw_bush_or_flowers(c, 9, gy, YELLOW)
        draw_bush_or_flowers(c, 52, gy, LIGHT_RED)
        animals.draw_boar(c)

    elif (suit, rank) == (1, 0):  # Leaf 7: Jester dancing with a sword raised overhead
        draw_bush_or_flowers(c, 10, gy, YELLOW)
        draw_bush_or_flowers(c, 50, gy, LIGHT_RED)
        people.draw_sword_dancer(c)
    elif (suit, rank) == (1, 1):  # Leaf 8: Elephant walking, trunk curled
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 52, gy, YELLOW)
        animals.draw_elephant(c, scale=0.8)
    elif (suit, rank) == (1, 2):  # Leaf 9: Red stag in mid-leap
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 51, gy, YELLOW)
        animals.draw_stag(c, dx=2, scale=0.62)
    elif (suit, rank) == (1, 3):  # Leaf 10: Lion couchant facing right
        animals.draw_lion(c)

    elif (suit, rank) == (2, 0):  # Bell 7: Large ornate potted rose bush on mound
        draw_bush_or_flowers(c, 10, gy, YELLOW)
        draw_bush_or_flowers(c, 50, gy, YELLOW)
        _draw_urn(c, 30, gy)
    elif (suit, rank) == (2, 1):  # Bell 8: Coursing hound with red collar
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 52, gy, YELLOW)
        animals.draw_hound(c, scale=0.85)
    elif (suit, rank) == (2, 2):  # Bell 9: Saddled dapple-grey horse tethered to a post
        c.fill_rect(6, 66, 8, gy - 1, BROWN, YELLOW, mode='vstripe')
        c.rect(5, 66, 9, gy - 1, DARK_GRAY)
        c.fill_rect(4, 64, 10, 65, YELLOW)
        c.rect(4, 64, 10, 65, BROWN)
        c.line(10, 67, 19, 68, BROWN)
        animals.draw_horse(c, flip=True, dx=4, scale=0.75)
    elif (suit, rank) == (2, 3):  # Bell 10: Village band of trumpeter, drummer and fiddler
        people.draw_musicians(c)

    elif (suit, rank) == (3, 0):  # Heart 7: Large coopered rose-tub with heart bloom
        draw_bush_or_flowers(c, 9, gy, YELLOW)
        draw_bush_or_flowers(c, 51, gy, YELLOW)
        _draw_heart_tub(c, 30, gy)
    elif (suit, rank) == (3, 1):  # Heart 8: Grand tiered Baroque fountain spraying water
        draw_bush_or_flowers(c, 8, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 52, gy, LIGHT_RED)
        _draw_fountain(c, 30, gy)
    elif (suit, rank) == (3, 2):  # Heart 9: Peacock in display beside a garden obelisk
        _draw_obelisk(c, 10, gy - 2)
        animals.draw_peacock(c, dx=10)
    elif (suit, rank) == (3, 3):  # Heart 10: Winged Cupid aiming his bow at a heart on a post
        c.blit_sprite(SPRITE_HEART_POST, 9, gy - 17)
        people.draw_cupid(c)


def draw_number_card(c, suit, rank):
    """Draws a complete number card (rank 0=Seven, 1=Eight, 2=Nine, 3=Ten)."""
    is_tree = suit in (0, 1)
    if is_tree:
        if rank == 0:  # Seven: 1 vertical top + 3 pairs
            bys = [24, 38, 52]
            draw_tree_trunk(c, 17, 88, bys, suit)
            draw_suit(c, suit, 30, 11, 'v')
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
        elif rank == 1:  # Eight: 4 pairs + top crown shoot
            bys = [15, 29, 43, 56]
            draw_tree_trunk(c, 10, 88, bys, suit)
            c.line(30, 10, 27, 6, GREEN)
            c.line(30, 10, 30, 5, LIGHT_GREEN)
            c.line(30, 10, 33, 6, GREEN)
            c.put(27, 5, LIGHT_RED)
            c.put(33, 5, LIGHT_RED)
            c.put(30, 4, YELLOW)
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
        elif rank == 2:  # Nine: 1 vertical top + 4 pairs
            bys = [23, 36, 49, 61]
            draw_tree_trunk(c, 16, 88, bys, suit)
            draw_suit(c, suit, 30, 10, 'v')
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
        else:  # Ten: Roman X + 5 pairs
            bys = [16, 28, 40, 52, 64]
            draw_tree_trunk(c, 13, 88, bys, suit)
            draw_roman_x(c, 30, 3)
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
    else:
        if rank == 0:  # Seven: 1 center top + 3 pairs
            ys = [24, 39, 54]
            draw_floret(c, 30, 31, suit)
            draw_floret(c, 30, 46, suit)
            draw_suit(c, suit, 30, 12)
            for y in ys:
                draw_suit(c, suit, 13, y)
                draw_suit(c, suit, 47, y)
        elif rank == 1:  # Eight: 4 pairs + central garland
            ys = [13, 27, 41, 55]
            draw_floret(c, 30, 20, suit)
            draw_floret(c, 30, 34, suit)
            draw_floret(c, 30, 48, suit)
            for y in ys:
                draw_suit(c, suit, 13, y)
                draw_suit(c, suit, 47, y)
        elif rank == 2:  # Nine: 3 center + 3 pairs
            for y in [12, 28, 44]:
                draw_suit(c, suit, 30, y)
            for y in [20, 36, 52]:
                draw_suit(c, suit, 12, y)
                draw_suit(c, suit, 48, y)
        else:  # Ten: Roman X + 2 center + 4 pairs
            draw_roman_x(c, 30, 3)
            for y in [21, 41]:
                draw_suit(c, suit, 30, y)
            draw_floret(c, 30, 31, suit)
            draw_floret(c, 30, 51, suit)
            for y in [14, 28, 42, 56]:
                draw_suit(c, suit, 12, y)
                draw_suit(c, suit, 48, y)

    # Draw the bottom vignette scene LAST so large figures/animals sit cleanly in front of tree trunks!
    draw_vignette_scene(c, suit, rank)
