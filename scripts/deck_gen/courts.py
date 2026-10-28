"""Court cards (Spodek/Unter, Svršek/Ober, Král/King) for all 4 suits.

Each figure is a jointed pose from `figure`, written facing right and
mirrored for the cards whose figure faces left. Unters are huntsmen and
musicians in caps, Obers wear broad plumed hats and beards, Kings sit
crowned on carved thrones.
"""

import math

from scripts.deck_gen import figure as F
from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_MAGENTA,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
    fill_terrain,
)
from scripts.deck_gen.rig import Rig, darker
from scripts.deck_gen.symbols import draw_suit


def _speckle(x, y):
    """A fixed pseudo-random value in 0..96 per pixel for scattering leaves, flowers and pebbles.

    A mixed integer hash: a plain linear formula repeats down some columns
    and draws stripes across the ground.
    """
    h = (x * 73856093 ^ y * 19349663) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h ^ (h >> 16)) % 97


def _ground_colour(suit, x, y, hill_y):
    """The ground under a standing figure, one kind per suit.

    Acorns stand on a forest floor strewn with fallen leaves, Leaves in a
    flowering meadow, Bells on the cobbles of a town square and Hearts on a
    garden lawn with a gravel path between rose beds.
    """
    d = y - hill_y
    h = _speckle(x, y)
    dither = (x + y) & 1
    if suit == 0:
        # A mossy edge over bare earth. Fallen leaves are two pixels wide so
        # they read as leaves, not noise; dark clods are scattered singly
        # rather than dithered, which would turn the earth to grey mud.
        if d == 1:
            return LIGHT_GREEN if dither else GREEN
        if d == 2:
            return GREEN if dither or h < 60 else BROWN
        leaf = _speckle(x // 2, y)
        if leaf < 5:
            return YELLOW
        if leaf < 8:
            return LIGHT_RED
        if leaf < 10:
            return RED
        return DARK_GRAY if h < 14 else BROWN
    if suit == 1:
        if h < 4 and d > 1:
            return YELLOW
        if h < 7 and d > 1:
            return WHITE
        if h < 9 and d > 1:
            return LIGHT_RED
        return LIGHT_GREEN if dither else GREEN
    if suit == 2:
        # Rows of cobbles, each row offset by half a stone.
        row, ry = divmod(d - 1, 3)
        sx = (x + (3 if row & 1 else 0)) % 6
        if ry == 2 or sx == 5:
            return DARK_GRAY
        if ry == 0 and sx == 0:
            return WHITE
        return LIGHT_GRAY if (row + (x + (3 if row & 1 else 0)) // 6) % 3 else BROWN
    if d <= 2:
        return GREEN if dither else LIGHT_GREEN
    # A gravel path widening towards the viewer, edged with clipped box.
    half = _heart_path_half(y)
    if abs(x - 30) <= half:
        if h < 4:
            return LIGHT_GRAY
        return BROWN if h < 22 else YELLOW
    if abs(x - 30) == half + 1:
        return GREEN
    # Roses in the beds: at most one per 5x4 cell, two by two pixels, lit on
    # the upper left, and only where the whole bloom fits inside the bed.
    cx, cy = x // 5, y // 4
    k = _speckle(cx, cy + 300)
    rx, ry = cx * 5 + k % 3, cy * 4 + (k // 3) % 2
    if k < 50 and 0 <= x - rx <= 1 and 0 <= y - ry <= 1 and ry - hill_y >= 4:
        if all(abs(px - 30) > _heart_path_half(py) + 2 for px in (rx, rx + 1) for py in (ry, ry + 1)):
            return RED if (x, y) == (rx + 1, ry + 1) else LIGHT_RED
    return GREEN if dither else LIGHT_GREEN


def _heart_path_half(y):
    """Half the width of the Hearts' gravel path at row y."""
    return 13 + max(y - 84, 0) // 3


def _floor_colour(suit, x, y):
    """The throne-room floor in front of the dais, one kind per suit.

    Acorns get oak parquet, Leaves green and gold lozenges, Bells a black and
    white marble chequer, Hearts a red carpet runner on stone.
    """
    d = y - 90
    if suit == 0:
        # Oak boards two rows deep, lit on top and shadowed below, their butt
        # joints staggered from row to row and a few knots in the grain.
        board, r = divmod(d, 2)
        if (x + board * 7) % 13 == 0:
            return DARK_GRAY
        if r:
            return BROWN
        return BROWN if _speckle(x, y) < 6 else YELLOW
    if suit == 1:
        # Lozenges eight wide and four tall, each row offset by half a lozenge.
        lx = (x + 4 * ((d // 4) % 2)) % 8 - 3.5
        ly = d % 4 - 1.5
        return YELLOW if abs(lx) / 4 + abs(ly) / 2 <= 1 else GREEN
    if suit == 2:
        return DARK_GRAY if ((x - 2) // 5 + d // 3) % 2 else WHITE
    if abs(x - 30) <= 9:
        # The runner: a dark red border stripe and a scatter of woven dots, gold fringe at the end.
        if y == 97 and x % 2:
            return YELLOW
        if abs(x - 30) == 8:
            return RED
        dot = (x - 30) % 4 == 0 and d % 4 == 1 or (x - 28) % 4 == 0 and d % 4 == 3
        return RED if dot and abs(x - 30) < 7 else LIGHT_RED
    if abs(x - 30) <= 11:
        return YELLOW
    return LIGHT_GRAY if ((x // 4) + (d // 3)) % 2 else WHITE


def _draw_throne_floor(c, suit):
    """A stone dais under the throne, its top at the king's feet, and the suit's floor below."""
    for y in range(85, 98):
        for x in range(2, 59):
            if y in (85, 89):
                col = DARK_GRAY
            elif y < 89:
                col = WHITE if y == 87 else LIGHT_GRAY
            else:
                col = _floor_colour(suit, x, y)
            c.put(x, y, col)


def draw_pedestal(c, suit, is_king=False):
    """Draws the ground under a standing figure, or a dais and floor under a throne."""
    if is_king:
        _draw_throne_floor(c, suit)
        return
    # The town square is level; the other grounds roll.
    amp = 0.6 if suit == 2 else 2.0
    fill_terrain(
        c,
        80,
        lambda x: 82 + int(round(math.sin((x + suit * 9) * 0.22) * amp)),
        lambda x, y, crest: _ground_colour(suit, x, y, crest),
    )
    _ground_details(c, suit)


def _ground_details(c, suit):
    """Small things growing or lying at the edges of each suit's ground."""
    if suit == 0:  # a toadstool at the right edge, clear of the Unter's suit sign
        c.blit_sprite(['.8888.', '84c4c48', '8f4f4f8', '8888888', '..8f8..', '..8f8..', '.8fff8.'], 51, 77)
    elif suit == 1:  # tall grass blades along the meadow's edge
        for x in range(3, 58, 3):
            y = 82 + int(round(math.sin((x + 9) * 0.22) * 2.0))
            c.line(x, y, x + (1 if x % 2 else -1), y - 3 - x % 2, GREEN if x % 2 else LIGHT_GREEN)
    elif suit == 3:  # clipped box hedges at the corners of the rose beds
        r = Rig(c)
        for hx in (6, 54):
            hedge = r.part().ellipse(hx, 81, 4.4, 3.4)
            hedge.paint(
                GREEN,
                shade=None,
                outline=DARK_GRAY,
                pattern=lambda x, y, hx=hx: LIGHT_GREEN if (x - hx + 1.5) ** 2 + (y - 79.8) ** 2 <= 3 or _speckle(x, y) < 10 else None,
            )


def _tufts(c, suit, xs, y=87):
    """Grass over the boot soles so the feet stand in the turf; on cobbles a shadow instead."""
    for bx in xs:
        for dx in range(-4, 5, 2):
            if suit == 2:
                c.put(bx + dx, y + 1, DARK_GRAY)
                c.put(bx + dx + 1, y + 1, DARK_GRAY)
            else:
                c.put(bx + dx, y, GREEN)
                c.put(bx + dx + 1, y - 1, LIGHT_GREEN if suit != 0 else GREEN)


def _ermine(x, y):
    """Ermine fur: white with a scatter of black tail tips."""
    return DARK_GRAY if (x % 4 == 0 and y % 3 == 0) or (x % 4 == 2 and y % 3 == 1 and x % 8 == 2) else None


def _stripes(col, step=3):
    return lambda x, y: col if y % step == 0 else None


def _brocade(col):
    """Small woven crosses on a staggered six-pixel lattice, leaving room for the folds between them."""

    def motif(x, y):
        sx = (x + (3 if (y // 6) % 2 else 0)) % 6
        sy = y % 6
        return col if (sx, sy) in ((2, 1), (1, 2), (2, 2), (3, 2), (2, 3)) else None

    return motif


def _quarters(col):
    return lambda x, y: col if (x + y) % 4 == 0 else None


# Heart King's chalice as it shows on the card, held up by its foot: a
# jewelled bowl, a knop on the stem and a spreading foot, lit from the left.
HEART_CHALICE = [
    '888888888',
    '8ffeeee68',
    '8feecee68',
    '.8feee68.',
    '..8ee68..',
    '...8e8...',
    '..8ee68..',
    '...8e8...',
    '...8e8...',
    '..8eee8..',
    '.8feee68.',
    '.8888888.',
]

# Obers wear a longer, fuller coat skirt than the Unters' short doublet.
OBER_COAT = dict(hem=61, flare=10)


def _standing(c, suit, flip, look, arms, legs, back_props=None, front_props=None, pose=None, back_over=False):
    """Draws a standing court figure and grounds it: grass (or a shadow on cobbles) under each boot sole."""
    r = Rig(c, flip=flip)
    F.draw_standing(r, look, arms, legs, back_props=back_props, front_props=front_props, pose=pose, back_over=back_over)
    # The middle of each sole, halfway from ankle to toe, wherever mirroring put it.
    _tufts(c, suit, [round(r.tx((ankle[0] + toe[0]) / 2, 0)[0]) for _, _, ankle, toe in legs])
    return r


def draw_unter(c, suit):
    """Spodek: young huntsmen and musicians in caps, the suit sign low beside the legs."""
    draw_pedestal(c, suit)
    # The suit sign sits on the left, where it still shows when the hand fans the cards.
    if suit == 0:  # Acorn: swinging a sword up over his head, striding left
        look = dict(
            cape=GREEN,
            swing=-9,
            sleeve_b=LIGHT_RED,
            sleeve_f=LIGHT_RED,
            cuff=YELLOW,
            hose=LIGHT_RED,
            boot=YELLOW,
            tunic=YELLOW,
            skirt=YELLOW,
            belt=GREEN,
            buttons=RED,
            hair=BROWN,
            hat=('cap', GREEN, LIGHT_RED, YELLOW),
        )
        arms = (((23, 26), (17, 17), (22, 9), 'grip'), ((36, 26), (42, 33), (48, 37), 'open'))
        legs = (((26, 52), (19, 68), (13, 84), (18, 87)), ((34, 52), (41, 67), (42, 84), (48, 87)))

        def blade(r):
            F.sword(r, (22, 9), (5, 24))

        _standing(c, suit, True, look, arms, legs, back_props=blade)
        draw_suit(c, 0, 10, 72, 'v')

    elif suit == 1:  # Leaf: playing a transverse flute, facing left
        look = dict(
            cape=LIGHT_RED,
            swing=-5,
            sleeve_b=GREEN,
            sleeve_f=GREEN,
            cuff=LIGHT_RED,
            puff=YELLOW,
            hose=GREEN,
            boot=CYAN,
            boot_cuff=LIGHT_CYAN,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=YELLOW,
            pattern=_stripes(YELLOW, 4),
            hair=YELLOW,
            hat=('beret', LIGHT_RED, WHITE, YELLOW),
        )
        # Both elbows raised, hands on the flute; the hands are drawn with the flute.
        arms = (((23, 26), (32, 27), (40, 21), None), ((36, 26), (45, 27), (49, 22), None))
        legs = (((28, 52), (27, 68), (25, 84), (30, 87)), ((34, 52), (36, 68), (38, 84), (44, 87)))

        def flute(r):
            # Mouthpiece at the lips, the tube running sideways and a little down.
            # It stops short of the card's border so the end reads as the end.
            r.part().capsule(34, 18.5, 55, 21.7, 1.5).paint(YELLOW, None, outline=BROWN)
            for x in (44, 52, 54):
                r.put(x, 18.5 + (x - 34) * 3.2 / 21, BROWN)
            # The hands hold the tube from below, fingers curled over its near
            # side: drawn under it, they were all but hidden.
            F.draw_hand(r, 39.5, 21.5, grip=True, toward=(32, 27))
            F.draw_hand(r, 48.5, 23, grip=True, toward=(45, 27))

        _standing(c, suit, True, look, arms, legs, front_props=flute)
        draw_suit(c, 1, 10, 72, 'v')

    elif suit == 2:  # Bell: hand on hip, the other resting on a sword planted point-down
        look = dict(
            cape=CYAN,
            swing=-8,
            sleeve_b=YELLOW,
            sleeve_f=YELLOW,
            cuff=LIGHT_RED,
            hose=YELLOW,
            boot=LIGHT_RED,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=CYAN,
            buttons=YELLOW,
            face='moustache',
            hair=BROWN,
            hat=('cap', LIGHT_RED, YELLOW, CYAN),
        )
        arms = (((23, 26), (16, 36), (23, 44), 'open'), ((36, 26), (42, 37), (48, 46), 'grip'))
        legs = (((26, 52), (23, 68), (20, 84), (25, 87)), ((34, 52), (38, 68), (40, 84), (46, 87)))

        def planted(r):
            # Plumb upright, so the long narrow blade keeps straight edges, its
            # point on the cobbles beside the boot; the fist closes over the grip.
            F.sword(r, (48, 46), (48, 87))
            # Steel down the blade's core, leaving a glint under the guard, so
            # it doesn't read as a hollow tube.
            r.line(48, 55, 48, 85, LIGHT_CYAN)

        _standing(c, suit, False, look, arms, legs, front_props=planted, back_over=True)
        draw_suit(c, 2, 13, 72)

    else:  # Heart: halberd over the shoulder, walking left
        look = dict(
            cape=LIGHT_RED,
            swing=-6,
            sleeve_b=CYAN,
            sleeve_f=CYAN,
            cuff=YELLOW,
            hose=YELLOW,
            boot=CYAN,
            tunic=CYAN,
            skirt=CYAN,
            belt=YELLOW,
            pattern=_stripes(YELLOW, 4),
            hair=YELLOW,
            hat=('cap', CYAN, LIGHT_RED, YELLOW),
        )
        # The free hand rests on the hip, over the coat, where the body can't hide it.
        arms = (((23, 26), (16, 36), (23, 44), 'open'), ((36, 26), (41, 33), (40, 23), 'grip'))
        legs = (((26, 52), (22, 68), (17, 83), (22, 87)), ((34, 52), (40, 67), (43, 83), (49, 87)))

        def halberd(r):
            # The head follows the shaft's slant: an upright head on a leaning
            # shaft reads as a flag. Spear point on top, crescent axe blade on
            # the far side, hook on the near side, a red tassel below.
            (bx, by), (tx, ty) = (24, 52), (47, 10)
            ln = math.hypot(tx - bx, ty - by)
            ux, uy = (tx - bx) / ln, (ty - by) / ln
            nx, ny = -uy, ux

            def at(along, side):
                return tx + ux * along + nx * side, ty + uy * along + ny * side

            F.pole(r, (bx, by), (tx, ty), BROWN, outline=DARK_GRAY)
            r.part().capsule(*at(-1, 0), *at(7, 0), 1.6, 0.6).paint(LIGHT_CYAN, None, outline=BLUE)
            blade = r.part().poly([at(0, 1), at(1, 7), at(-3, 8.5), at(-7, 7), at(-6, 1)])
            blade.paint(LIGHT_CYAN, None, outline=BLUE)
            r.line(*at(0, 6.5), *at(-6, 6.5), WHITE)
            r.part().poly([at(-1.5, -1), at(-3, -5), at(-4.5, -1)]).paint(LIGHT_CYAN, None, outline=BLUE)
            r.part().ellipse(*at(-9, 0), 1.6, 1.6).paint(LIGHT_RED)

        _standing(c, suit, True, look, arms, legs, back_props=halberd, back_over=True)
        draw_suit(c, 3, 9, 67)


def draw_ober(c, suit):
    """Svršek: bearded men in broad plumed hats, the suit sign high in a corner."""
    draw_pedestal(c, suit)
    # The suit sign sits top left, where it still shows when the hand fans the cards.
    if suit == 0:  # Acorn: raising a sword forward, fist on hip, facing right
        look = dict(
            cape=GREEN,
            swing=-9,
            lining=LIGHT_GREEN,
            sleeve_b=LIGHT_RED,
            sleeve_f=LIGHT_RED,
            # Gold cuffs, so the bare fists don't merge into white ones.
            cuff=YELLOW,
            puff=YELLOW,
            # Light green hose shade to green; green ones would dither into grey.
            hose=LIGHT_GREEN,
            boot=YELLOW,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=YELLOW,
            pattern=_stripes(YELLOW, 4),
            face='beard',
            hair=BROWN,
            # An oak-green plume: a white one vanishes against the card.
            hat=('brim', LIGHT_RED, GREEN, YELLOW),
        )
        arms = (((23, 26), (17, 35), (24, 43), 'grip'), ((36, 26), (43, 22), (49, 14), 'grip'))
        legs = (((26, 52), (22, 68), (19, 84), (24, 87)), ((34, 52), (40, 67), (42, 84), (48, 87)))

        def blade(r):
            # The point stops short of the frame.
            F.sword(r, (49, 14), (40, 4))

        # Drawn behind the figure so the fist closes over the grip.
        _standing(c, suit, False, look, arms, legs, back_props=blade, pose=OBER_COAT, back_over=True)
        draw_suit(c, 0, 12, 12, 'v')

    elif suit == 1:  # Leaf: drummer with the drum slung at his hip
        look = dict(
            cape=LIGHT_RED,
            swing=-8,
            sleeve_b=GREEN,
            sleeve_f=GREEN,
            cuff=YELLOW,
            hose=YELLOW,
            boot=CYAN,
            tunic=GREEN,
            skirt=GREEN,
            belt=YELLOW,
            buttons=YELLOW,
            face='moustache',
            hair=BROWN,
            hat=('brim', LIGHT_RED, YELLOW, GREEN),
        )
        # The lower stick's arm reaches across the belly to the drumhead; its
        # fist is drawn with the drum, closing over the stick.
        arms = (((23, 26), (22, 38), (32, 42), None), ((36, 26), (44, 34), (50, 30), 'grip'))
        legs = (((26, 52), (23, 68), (20, 84), (25, 87)), ((34, 52), (38, 68), (40, 84), (46, 87)))

        def drum(r):
            d = r.part().ellipse(41, 52, 8, 3).rect(33, 52, 49, 63).ellipse(41, 63, 8, 2.5)
            d.paint(YELLOW)
            # Tension cords zigzagging from hoop to hoop.
            for k in range(4):
                r.line(33 + 4 * k, 62 if k % 2 == 0 else 53, 37 + 4 * k, 53 if k % 2 == 0 else 62, RED)
            r.part().rect(33, 51, 49, 53).paint(LIGHT_RED)
            r.part().rect(33, 62, 49, 64).paint(LIGHT_RED)
            # The drumhead edged dark: a pale rim would vanish on the white card.
            r.part().ellipse(41, 50, 7.5, 2.4).paint(WHITE, None, outline=DARK_GRAY)
            F.pole(r, (31, 40), (38, 49))
            F.draw_hand(r, 32, 42, grip=True, toward=(22, 38))
            # The raised stick's butt shows above the fist.
            F.pole(r, (51, 27), (45, 48))

        _standing(c, suit, False, look, arms, legs, front_props=drum, pose=OBER_COAT, back_over=True)
        draw_suit(c, 1, 12, 12, 'v')

    elif suit == 2:  # Bell: hand on sword hilt at his side, the other open in greeting, facing left
        look = dict(
            cape=CYAN,
            swing=-9,
            lining=LIGHT_CYAN,
            sleeve_b=LIGHT_RED,
            sleeve_f=LIGHT_RED,
            # Gold cuffs: white ones merge with the raised hand into one big white blob.
            cuff=YELLOW,
            puff=YELLOW,
            hose=YELLOW,
            boot=LIGHT_RED,
            tunic=YELLOW,
            skirt=LIGHT_RED,
            belt=CYAN,
            pattern=_quarters(LIGHT_RED),
            face='goatee',
            hair=YELLOW,
            beard=YELLOW,
            hat=('brim', CYAN, LIGHT_RED, YELLOW),
        )
        # The greeting forearm is raised and the wrist set between pixels, so
        # the open palm is four pixels wide and covers the end of the sleeve.
        arms = (((23, 26), (19, 37), (22, 47), 'grip'), ((36, 26), (44, 33), (49.5, 24.5), 'open'))
        legs = (((26, 52), (24, 68), (21, 84), (26, 87)), ((34, 52), (37, 68), (39, 84), (45, 87)))

        def scabbard(r):
            # Plain leather without the dithered shade, which spots a blade this narrow, and a gilt chape.
            r.part().capsule(21, 49, 9, 71, 1.5).paint(BROWN, None, outline=DARK_GRAY)
            r.part().capsule(11, 67.5, 9, 71, 1.5).paint(YELLOW, None, outline=BROWN)

        def hilt(r):
            # Crossguard and pommel in front of the coat, the fist closed on the grip between them.
            r.part().capsule(18.5, 47.5, 23.5, 50.5, 0.9).fill(YELLOW)
            r.part().ellipse(23.5, 44, 1.5, 1.5).paint(YELLOW, None, outline=BROWN)
            F.draw_hand(r, 22, 47, grip=True)

        _standing(c, suit, True, look, arms, legs, back_props=scabbard, front_props=hilt, pose=OBER_COAT)
        draw_suit(c, 2, 12, 12)

    else:  # Heart: spear upright in one hand, the other on his hip
        look = dict(
            cape=LIGHT_RED,
            swing=-8,
            sleeve_b=YELLOW,
            sleeve_f=YELLOW,
            cuff=LIGHT_RED,
            hose=LIGHT_CYAN,
            boot=LIGHT_RED,
            tunic=GREEN,
            skirt=YELLOW,
            belt=LIGHT_RED,
            buttons=YELLOW,
            face='beard',
            hair=BROWN,
            hat=('brim', GREEN, LIGHT_RED, YELLOW),
        )
        arms = (((23, 26), (16, 35), (22, 44), 'open'), ((36, 26), (42, 35), (46, 30), 'grip'))
        legs = (((26, 52), (22, 68), (19, 84), (24, 87)), ((34, 52), (38, 68), (41, 84), (47, 87)))

        def spear(r):
            F.pole(r, (47, 86), (47, 11))
            # A leaf-shaped blade whose point stays clear of the card border.
            r.c.blit_sprite(['..1..', '.1b1.', '.1b1.', '1bb31', '1bb31', '1b331', '.131.', '..1..'], 45, 3)

        _standing(c, suit, False, look, arms, legs, back_props=spear, pose=OBER_COAT, back_over=True)
        draw_suit(c, 3, 12, 12)


def _throne(r, wood, velvet, style):
    """A throne seen from the front, framing the king, in one of four styles.

    'round' has an arched back and gold ball finials, 'gothic' a pointed back
    and spires, 'canopy' a fringed valance with curtains falling to either
    side, 'baroque' a low rounded back between scroll volutes (a crest
    there would hide behind the king's head). The parts beside the corner
    pips (posts, finials, valance ends) stay below y=21; only the middle,
    behind the king's head, rises higher.
    """

    def grain(x, y):
        return darker(wood) if (x + y) % 7 == 0 else None

    def nap(x, y):
        return darker(velvet) if x % 4 == 0 and y % 4 == 0 else None

    if style == 'gothic':
        r.part().poly([(12, 66), (12, 34), (30, 15), (48, 34), (48, 66)]).paint(wood, pattern=grain)
        r.part().poly([(16, 66), (16, 36), (30, 21), (44, 36), (44, 66)]).paint(velvet, pattern=nap)
        # Pointed lancet windows of tracery either side of the king.
        for lx in (19, 41):
            r.part().poly([(lx - 2.5, 60), (lx - 2.5, 42), (lx, 36), (lx + 2.5, 42), (lx + 2.5, 60)]).paint(
                darker(velvet), None, outline=wood
            )
        for fx in (12, 48):
            r.part().rect(fx - 2, 28, fx + 2, 70).paint(wood)
            r.part().poly([(fx - 2.5, 28), (fx, 21), (fx + 2.5, 28)]).paint(YELLOW)
    elif style == 'canopy':
        r.part().rect(12, 26, 48, 66).paint(wood, pattern=grain)
        r.part().rect(16, 28, 44, 66).paint(velvet, pattern=nap)
        for fx, sway in ((12, -1), (48, 1)):
            r.part().poly([(fx - 3, 25), (fx + 3, 25), (fx + 2 - sway, 66), (fx - 2 - sway, 66)]).paint(
                velvet, pattern=lambda x, y: darker(velvet) if x % 3 == 0 else None
            )
        valance = r.part().rect(9, 21, 51, 25)
        for sx in range(11, 51, 5):
            valance.ellipse(sx + 1.5, 25, 2.6, 2)
        valance.paint(velvet, pattern=lambda x, y: YELLOW if y == 22 else None)
        for sx in range(11, 51, 5):
            r.put(sx + 1.5, 28, YELLOW)
    elif style == 'baroque':
        r.part().rect(12, 28, 48, 66).ellipse(30, 28, 15, 6).paint(wood, pattern=grain)
        r.part().rect(16, 30, 44, 66).ellipse(30, 30, 12, 4).paint(velvet, pattern=nap)
        for fx, turn in ((12, 1), (48, -1)):
            r.part().rect(fx - 2, 30, fx + 2, 70).paint(wood)
            r.part().ellipse(fx, 28, 3.4, 3.2).paint(YELLOW)
            r.put(fx + turn, 28, BROWN)
            r.put(fx, 27, BROWN)
    else:
        r.part().rect(12, 26, 48, 66).ellipse(30, 26, 18, 7).paint(wood, pattern=grain)
        r.part().rect(16, 28, 44, 66).ellipse(30, 28, 14, 5).paint(velvet, pattern=nap)
        for fx in (12, 48):
            r.part().rect(fx - 2, 22, fx + 2, 70).paint(wood)
            r.part().ellipse(fx, 21, 2.4, 2.4).paint(YELLOW)
    # A solid carved base under the seat, down to the dais: a lone leg beside the
    # robe would read as a walking stick.
    r.part().rect(10, 66, 50, 84).paint(wood, pattern=grain)
    r.part().rect(10, 69, 50, 70).fill(YELLOW)


def _seated(c, flip, look, front_arm, back_arm, props_front=None):
    """A crowned king on a throne, robe over the knees and an ermine stole.

    Arms are (shoulder, elbow, wrist, hand) as for standing figures; the
    king faces right before mirroring.
    """
    r = Rig(c, flip=flip)
    j = dict(head=(30, 16), neck=(30, 22), sh_b=(24, 27), sh_f=(35, 27), waist=(30, 46))
    _throne(r, look['throne'], look['cushion'], look['style'])
    F.cape(r, j, look['mantle'], length=78, swing=-5)
    bsh, bel, bwr, bhand = back_arm
    # Feet set apart under the hem.
    for an, toe in (((27, 83), (31, 86)), ((40, 83), (45, 86))):
        r.part().capsule(an[0], an[1] - 4, *an, 2.3).capsule(*an, *toe, 2.1, 1.4).paint(look['shoe'])
    # Robe: lap running forward to the knees, then falling in folds to the ankles.
    robe = r.part().poly([(23, 44), (37, 44), (46, 53), (49, 60), (53, 82), (15, 82), (20, 60)])
    robe.ellipse(43, 57, 7, 4.5).ellipse(25, 57, 6, 4.5)
    robe_shade = darker(look['robe'])
    pattern = look.get('robe_pattern')
    knee_y = r.tx(0, 61)[1]
    hem_y = r.tx(0, 79)[1]

    def folds(x, y):
        if y >= hem_y:
            # Gold hem band with a row of jewels.
            return RED if y == hem_y + 1 and x % 4 == 0 else YELLOW
        if pattern is not None and pattern(x, y) is not None:
            return pattern(x, y)
        if y == knee_y or (y == knee_y + 1 and x % 2):
            return robe_shade
        # Folds fall from the knees and fan out towards the hem.
        fx, _ = r.tx(34, 0)
        spread = 1 + (y - knee_y) / 22
        if y > knee_y + 2 and round((x - fx) / spread) % 5 == 0:
            return robe_shade
        return None

    robe.paint(look['robe'], pattern=folds)
    body = r.part().poly([(23, 26), (36, 26), (35, 46), (24, 46)]).ellipse(31, 33, 6.5, 6.5)
    body.paint(look['tunic'], pattern=look.get('pattern'))
    r.part().rect(23, 45, 37, 47).paint(YELLOW)
    # The resting arm lies in front of the body and robe, its forearm across
    # the lap: drawn behind them, only a lone hand would show.
    F.arm(r, bsh, bel, bwr, look['sleeve'], cuff=WHITE)
    # Ermine shoulder cape with a band down the front to the belt; a band running on
    # across the lap would read as a sword blade.
    stole = r.part().ellipse(30, 26.5, 9.5, 4).capsule(36, 27, 37, 45, 1.8)
    stole.paint(WHITE, None, outline=LIGHT_GRAY, pattern=_ermine)
    F.draw_head(r, 30, 16, face=look.get('face', 'king'), hair=look['hair'], beard=look.get('beard'), hat=look['hat'])
    if bhand:
        F.draw_hand(r, *bwr, grip=bhand == 'grip')
    fsh, fel, fwr, fhand = front_arm
    F.arm(r, fsh, fel, fwr, look['sleeve'], cuff=WHITE)
    if props_front:
        props_front(r)
    if fhand:
        F.draw_hand(r, *fwr, grip=fhand == 'grip')
    return r


def draw_king(c, suit):
    """Král: crowned and seated, the suit sign in both top corners."""
    draw_pedestal(c, suit, is_king=True)
    draw_suit(c, suit, 11, 12, 'v')
    draw_suit(c, suit, 49, 12, 'v')

    if suit == 0:  # Acorn: sceptre upright, orb on the knee
        look = dict(
            throne=YELLOW,
            style='gothic',
            cushion=LIGHT_RED,
            mantle=GREEN,
            sleeve=LIGHT_RED,
            robe=LIGHT_RED,
            shoe=BROWN,
            tunic=GREEN,
            pattern=_quarters(YELLOW),
            # A grey beard trimmed short of the cheeks: the full 'old' beard
            # leaves so little skin that the face reads as grey stone.
            face='king',
            hair=LIGHT_GRAY,
            beard=LIGHT_GRAY,
            hat=('crown', LIGHT_RED, LIGHT_RED, YELLOW),
        )

        def sceptre(r):
            # Angled across the gilded throne post so the two don't merge.
            F.pole(r, (43, 53), (53, 29), YELLOW, outline=BROWN)
            r.part().ellipse(54, 27, 2.2, 2.2).paint(LIGHT_GREEN)

        def orb(r):
            # Resting on the open hand: a gold ball girdled in red, a cross on top.
            r.part().ellipse(37, 49, 3.2, 3.0).paint(
                YELLOW, None, outline=BROWN, pattern=lambda x, y: RED if y == 49 else (WHITE if (x, y) == (36, 47) else None)
            )
            r.sprite(['.6.', '6e6', '.e.'], 36, 44, anchor=(1, 0))

        _seated(
            c,
            False,
            look,
            ((35, 27), (41, 39), (46, 43), 'grip'),
            ((24, 27), (24, 41), (34, 50), 'open'),
            props_front=lambda r: (sceptre(r), orb(r)),
        )

    elif suit == 1:  # Leaf: sceptre resting on the shoulder, facing left
        look = dict(
            throne=BROWN,
            style='canopy',
            # Pale green hangings, so the king's dark green robe stands out against them.
            cushion=LIGHT_GREEN,
            mantle=LIGHT_RED,
            sleeve=GREEN,
            robe=GREEN,
            shoe=LIGHT_RED,
            tunic=LIGHT_RED,
            pattern=_stripes(YELLOW, 4),
            hair=BROWN,
            beard=BROWN,
            face='king',
            hat=('crown', GREEN, LIGHT_RED, YELLOW),
        )

        def sceptre(r):
            # Leaning on the shoulder with the finial clear of the hair, and
            # outlined dark so the gold doesn't melt into the brown hair.
            F.pole(r, (44, 46), (39, 19), YELLOW, outline=BROWN)
            r.part().poly([(39, 12), (41.5, 15.5), (39, 19), (36.5, 15.5)]).paint(YELLOW, outline=DARK_GRAY)
            r.put(39, 15.5, LIGHT_RED)

        _seated(
            c,
            True,
            look,
            ((35, 27), (40, 39), (44, 44), 'grip'),
            ((24, 27), (24, 41), (36, 52), 'open'),
            props_front=sceptre,
        )

    elif suit == 2:  # Bell: drawn sword held upright
        look = dict(
            throne=YELLOW,
            style='baroque',
            cushion=CYAN,
            mantle=CYAN,
            sleeve=LIGHT_RED,
            robe=LIGHT_RED,
            shoe=CYAN,
            tunic=CYAN,
            pattern=_quarters(YELLOW),
            hair=YELLOW,
            beard=YELLOW,
            face='king_old',
            hat=('crown', LIGHT_RED, CYAN, YELLOW),
        )

        def blade(r):
            # Plumb, and short enough that the point stays under the corner bell.
            F.sword(r, (46, 45), (46, 23))
            r.line(46, 31, 46, 25, LIGHT_CYAN)

        _seated(
            c,
            False,
            look,
            ((35, 27), (41, 39), (46, 45), 'grip'),
            # Hand on the thigh beside the body, just below where the sleeve
            # shows, so it doesn't float in the middle of the robe.
            ((24, 27), (22, 40), (23, 47), 'open'),
            props_front=blade,
        )

    else:  # Heart: raising a golden chalice, facing left
        look = dict(
            throne=BROWN,
            style='round',
            cushion=LIGHT_RED,
            mantle=LIGHT_RED,
            sleeve=CYAN,
            robe=CYAN,
            shoe=LIGHT_RED,
            tunic=YELLOW,
            pattern=_stripes(LIGHT_RED, 4),
            robe_pattern=_brocade(LIGHT_CYAN),
            face='king_forked',
            hair=YELLOW,
            beard=YELLOW,
            hat=('crown', LIGHT_RED, LIGHT_MAGENTA, YELLOW),
        )

        def chalice(r):
            # Pixelled in card space over the throne post; a dark grey
            # outline keeps the gold apart from the brown wood behind it.
            r.c.blit_sprite(HEART_CHALICE, 8, 26)

        _seated(
            c,
            True,
            look,
            ((35, 27), (42, 42), (48, 38), 'grip'),
            ((24, 27), (24, 41), (35, 51), 'open'),
            props_front=chalice,
        )


def draw_court_card(c, suit, rank):
    """Draws a court card: rank 4=Under, 5=Over, 6=King."""
    if rank == 4:
        draw_unter(c, suit)
    elif rank == 5:
        draw_ober(c, suit)
    else:
        draw_king(c, suit)
