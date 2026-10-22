"""Number cards (7, 8, 9, 10) and their 16 large, high-detail EGA pixel-art vignettes."""

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
)
from scripts.deck_gen.rig import Rig
from scripts.deck_gen.symbols import (
    draw_floret,
    draw_roman_x,
    draw_suit,
    draw_tree_trunk,
)

# The vignettes are drawn from shapes: people and animals by `people` and
# `animals`, buildings and garden pieces by the helpers below. Only the
# heart target on Cupid's post is a hand-pixelled sprite.

# Heart 10 left: Heart target on a post for Cupid to aim at (9x16)
SPRITE_HEART_POST = [
    '....66...',
    '...6ee6..',
    '..44ee44.',
    '.4cccccc4',
    '.4cccccc4',
    '..4cccc4.',
    '...4cc4..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '..86ee68.',
    '..888888.',
]


def draw_ground(c, suit, rank):
    """Draws rich, multi-layered organic landscape terrain at the bottom (y=80..97)."""
    import math
    for y in range(80, 98):
        for x in range(2, 59):
            if not c.in_interior(x, y):
                continue
            # Rolling multi-hill contour so terrain looks natural rather than a flat stage line
            wave = int(round(math.sin((x + suit * 7 + rank * 5) * 0.22) * 2.0))
            hill_y = 84 + wave
            if y < hill_y:
                continue
            if y == hill_y:
                col = DARK_GRAY
            elif suit == 0:  # Acorns: mossy woodland hills & winding golden forest path
                if abs(x - (29 + (y - 86))) <= 10 and y >= 88:
                    col = YELLOW if ((x + y) & 1) == 0 else BROWN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            elif suit == 1:  # Leaves: lush emerald hills & sunlit meadow clearing
                if y >= 89 and abs(x - 31) <= 14:
                    col = YELLOW if ((x + y) & 1) == 0 else LIGHT_GREEN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            elif suit == 2:  # Bells: rolling green turf & golden road
                if y >= 88 and abs(x - 30) <= 16:
                    col = YELLOW if ((x + y) & 1) == 0 else BROWN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            else:  # Hearts: terraced garden hills & golden parterre
                if y >= 90:
                    col = YELLOW if ((x + y) & 1) == 0 else LIGHT_GREEN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            c.put(x, y, col)


def draw_fir(c, cx, base_y, h):
    """Draws a layered pixel-art conifer tree rooted into the ground at base_y..base_y+2."""
    c.fill_rect(cx - 2, base_y - 3, cx + 2, base_y + 1, BROWN, DARK_GRAY, mode='vstripe')
    c.fill_poly(
        [(cx - 6, base_y + 1), (cx - 4, base_y - 2), (cx + 4, base_y - 2), (cx + 6, base_y + 1)],
        GREEN,
        DARK_GRAY,
        outline=DARK_GRAY,
        mode='checker',
    )
    tiers = 3
    for t in range(tiers):
        ty0 = base_y - h + t * (h // 4)
        ty1 = base_y - 1 - (tiers - 1 - t) * (h // 5)
        w = 2 + t * 2
        pts = [(cx, ty0), (cx - w - 2, ty1), (cx + w + 2, ty1)]
        c.fill_poly(pts, GREEN, DARK_GRAY, outline=DARK_GRAY, mode='checker')
        c.line(cx, ty0 + 1, cx - w, ty1 - 1, LIGHT_GREEN)


def draw_bush_or_flowers(c, cx, base_y, col):
    """Draws a flat-bottomed flowering bush rooted directly into base_y..base_y+1."""
    pts = [
        (cx - 6, base_y + 1),
        (cx - 5, base_y - 3),
        (cx - 2, base_y - 6),
        (cx + 2, base_y - 6),
        (cx + 5, base_y - 3),
        (cx + 6, base_y + 1),
    ]
    c.fill_poly(pts, GREEN, DARK_GRAY, outline=DARK_GRAY, mode='checker')
    for dx, dy in [(-3, -3), (0, -5), (3, -3), (-1, -2), (2, -4)]:
        c.put(cx + dx, base_y + dy, col)
    c.put(cx, base_y - 3, YELLOW)


def _draw_obelisk(c, cx, base_y):
    """A slender gilded garden obelisk on a stepped plinth, topped by a small heart."""
    r = Rig(c)
    r.part().rect(cx - 5, base_y - 3, cx + 5, base_y).paint(LIGHT_GRAY, light=WHITE, outline=DARK_GRAY)
    r.part().rect(cx - 4, base_y - 5, cx + 4, base_y - 4).paint(LIGHT_GRAY, outline=DARK_GRAY)
    shaft = r.part().poly([(cx - 3, base_y - 5), (cx + 3, base_y - 5), (cx + 1.5, base_y - 17), (cx - 1.5, base_y - 17)])
    shaft.poly([(cx - 1.5, base_y - 17), (cx + 1.5, base_y - 17), (cx, base_y - 20)])
    shaft.paint(YELLOW, light=WHITE, outline=BROWN)
    c.blit_centered(['.4.4.', '4cc44', '4ccc4', '.4c4.', '..4..'], cx, base_y - 23)


def _draw_cottage(c, cx, base_y):
    """A Czech log cottage (roubenka) gable-on: dark logs with white chinking, a boarded gable,
    a red tiled roof with a smoking chimney, a window with a flower box and a plank door."""
    r = Rig(c)
    left, right, eave = cx - 9, cx + 9, base_y - 12
    # Smoke drifting up and away from the chimney.
    for k, (sx, sy) in enumerate(((5, -13), (4, -15), (2, -17), (1, -19), (-1, -21))):
        r.part().ellipse(cx + sx, eave + sy, 1.4 + k * 0.2, 1.1).fill(WHITE if k % 2 else LIGHT_GRAY)
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


def _water_arc(c, x0, y0, x1, y1, rise):
    """A jet of water: a parabola from (x0, y0) up by `rise` and down to (x1, y1), with droplets."""
    steps = int(abs(x1 - x0) * 2) + 8
    for k in range(steps + 1):
        t = k / steps
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t - rise * 4 * t * (1 - t)
        c.put(x, y, WHITE if k % 3 else LIGHT_CYAN)
        c.put(x, y + 1, LIGHT_CYAN)
    c.put(x1 + (1 if x1 > x0 else -1), y1 - 2, LIGHT_CYAN)


def _draw_fountain(c, cx, base_y):
    """A two-tiered stone fountain in a red brick pool, water arching from tier to tier."""
    r = Rig(c)
    # Brick pool wall and the water inside it.
    r.part().rect(cx - 19, base_y - 6, cx + 19, base_y).paint(
        LIGHT_RED, outline=DARK_GRAY, pattern=lambda x, y: RED if (y - base_y) % 3 == 0 or (x + ((y - base_y) // 3) * 3) % 6 == 0 else None
    )
    r.part().ellipse(cx, base_y - 7, 18, 2.2).paint(LIGHT_CYAN, None, outline=CYAN, pattern=lambda x, y: WHITE if (x + y) % 5 == 0 else None)
    # Pedestal and the wide lower basin.
    r.part().rect(cx - 2, base_y - 16, cx + 2, base_y - 7).paint(WHITE, LIGHT_GRAY, outline=DARK_GRAY)
    r.part().poly([(cx - 12, base_y - 16), (cx + 12, base_y - 16), (cx + 7, base_y - 10), (cx - 7, base_y - 10)]).paint(
        WHITE, LIGHT_GRAY, outline=DARK_GRAY
    )
    r.part().ellipse(cx, base_y - 16, 12, 1.6).paint(LIGHT_CYAN, None, outline=DARK_GRAY)
    # Upper tier on a slimmer stem.
    r.part().rect(cx - 1, base_y - 22, cx + 1, base_y - 16).paint(WHITE, LIGHT_GRAY, outline=DARK_GRAY)
    r.part().poly([(cx - 6, base_y - 22), (cx + 6, base_y - 22), (cx + 3, base_y - 18), (cx - 3, base_y - 18)]).paint(
        WHITE, LIGHT_GRAY, outline=DARK_GRAY
    )
    r.part().ellipse(cx, base_y - 22, 6, 1.2).paint(LIGHT_CYAN, None, outline=DARK_GRAY)
    # Water: a jet from the top falling to the upper tier, then over its rim to the basin and pool.
    c.line(cx, base_y - 23, cx, base_y - 25, WHITE)
    for side in (-1, 1):
        _water_arc(c, cx, base_y - 25, cx + side * 5, base_y - 22, 2)
        _water_arc(c, cx + side * 6, base_y - 22, cx + side * 11, base_y - 16, 1.5)
        _water_arc(c, cx + side * 12, base_y - 16, cx + side * 16, base_y - 8, 1.5)


def _draw_urn(c, cx, base_y):
    """A gilded garden urn with scrolled handles, planted with a flowering rose bush."""
    r = Rig(c)
    # The bush first, so the urn's rim sits in front of it.
    bush = r.part().ellipse(cx, base_y - 19, 10, 5.5).ellipse(cx - 6, base_y - 16, 5, 3.5).ellipse(cx + 6, base_y - 16, 5, 3.5)
    bush.paint(GREEN, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GREEN if (x * 2 + y) % 5 == 0 else None)
    roses = {LIGHT_RED: ['.cc.', 'c4cc', '.cc.'], YELLOW: ['.ee.', 'e6ee', '.ee.']}
    for rx, ry, col in ((-6, -20, LIGHT_RED), (0, -23, YELLOW), (6, -20, LIGHT_RED), (-3, -16, YELLOW), (4, -16, LIGHT_RED), (-9, -15, YELLOW), (9, -15, YELLOW)):
        c.blit_centered(roses[col], cx + rx, base_y + ry)
    for side in (-1, 1):
        r.part().chain([(cx + side * 6, base_y - 11), (cx + side * 10, base_y - 11), (cx + side * 9, base_y - 7), (cx + side * 6, base_y - 7)], [0.8] * 4).fill(BROWN)
    body = r.part().ellipse(cx, base_y - 9, 7, 5).rect(cx - 7, base_y - 13, cx + 7, base_y - 11)
    body.paint(YELLOW, light=WHITE, outline=BROWN, pattern=lambda x, y: RED if y == base_y - 9 and x % 3 == 0 else None)
    r.part().ellipse(cx, base_y - 13, 8, 1.5).paint(YELLOW, outline=BROWN)
    r.part().rect(cx - 2, base_y - 5, cx + 2, base_y - 3).paint(YELLOW, outline=BROWN)
    r.part().rect(cx - 5, base_y - 2, cx + 5, base_y).paint(YELLOW, light=WHITE, outline=BROWN)


def _draw_heart_tub(c, cx, base_y):
    """A hooped wooden tub holding a box tree clipped into a heart, studded with roses."""
    r = Rig(c)
    r.part().rect(cx - 1, base_y - 14, cx + 1, base_y - 9).paint(BROWN, outline=DARK_GRAY)
    heart = r.part().ellipse(cx - 4.5, base_y - 20, 5, 4.5).ellipse(cx + 4.5, base_y - 20, 5, 4.5)
    heart.poly([(cx - 9.5, base_y - 19), (cx + 9.5, base_y - 19), (cx, base_y - 11)])
    heart.paint(GREEN, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GREEN if (x + 2 * y) % 4 == 0 else None)
    for rx, ry in ((-5, -21), (4, -22), (0, -17), (-6, -17), (6, -18), (1, -13)):
        c.put(cx + rx, base_y + ry, LIGHT_RED)
        c.put(cx + rx + 1, base_y + ry, RED)
    tub = r.part().poly([(cx - 9, base_y - 9), (cx + 9, base_y - 9), (cx + 7, base_y), (cx - 7, base_y)])
    tub.paint(BROWN, shade=None, outline=DARK_GRAY, pattern=lambda x, y: YELLOW if (x - cx) % 3 == 0 else None)
    for hy in (base_y - 7, base_y - 2):
        c.line(cx - 8, hy, cx + 8, hy, DARK_GRAY)
    r.part().ellipse(cx, base_y - 9, 9, 1.3).paint(BROWN, outline=DARK_GRAY)


def draw_vignette_scene(c, suit, rank):
    """Draws one of the 16 large, grounded bottom scenes (y=60..91).

    Animals are scaled so they stay below the lowest pips of their card.
    """
    draw_ground(c, suit, rank)
    gy = 88

    if (suit, rank) == (0, 0):  # Acorn 7: Forester smoking a pipe beside a timbered cottage
        draw_bush_or_flowers(c, 8, gy, LIGHT_RED)
        _draw_cottage(c, 46, gy - 1)
        people.draw_forester(c)
    elif (suit, rank) == (0, 1):  # Acorn 8: Huntsman sitting in the grass blowing his horn, his dog by him
        people.draw_hornblower(c)
        animals.draw_dog(c, dx=3)
    elif (suit, rank) == (0, 2):  # Acorn 9: Cock pheasant perched on an oak bough
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 51, gy, YELLOW)
        animals.draw_pheasant(c, scale=0.75)
    elif (suit, rank) == (0, 3):  # Acorn 10: Wild boar trotting across a forest clearing
        draw_bush_or_flowers(c, 9, gy, YELLOW)
        draw_bush_or_flowers(c, 52, gy, LIGHT_RED)
        animals.draw_boar(c, scale=0.7)

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
        animals.draw_lion(c, scale=0.72)

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
        c.blit_sprite(SPRITE_HEART_POST, 9, gy - 14)
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
