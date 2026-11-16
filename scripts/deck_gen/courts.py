"""Court cards (Spodek/Unter, Svršek/Ober, Král/King) for all 4 suits.

Each figure is a jointed pose from `figure`, written facing right and
mirrored for the cards whose figure faces left. Unters are young huntsmen
and musicians, bare-headed or in a cap or beret, Obers wear broad plumed
hats and beards, Kings sit crowned on carved thrones.
"""

import math

from scripts.deck_gen import figure as F
from scripts.deck_gen.grounds import draw_footing, draw_suit_ground
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
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.rig import Rig, darker
from scripts.deck_gen.symbols import draw_suit


def _speckle(x, y):
    """A fixed pseudo-random value in 0..96 per pixel, for scattering knots in wood and flecks in a hedge.

    A mixed integer hash: a plain linear formula repeats down some columns
    and draws stripes.
    """
    h = (x * 73856093 ^ y * 19349663) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h ^ (h >> 16)) % 97


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


# The skyline under a standing figure lies a little higher than on the number
# cards, so the boots, their soles on SOLE_ROW, stand well inside the ground.
COURT_GROUND = 82
SOLE_ROW = 87

# The ground variants of the two standing ranks, following the number cards' 0..3.
UNTER, OBER = 4, 5


def _draw_ground(c, suit, variant):
    """Draws the ground under a standing figure: its suit's, the same as on the number cards.

    `variant` tells the Unter's from the Ober's. A few small things grow or
    lie at its edges.
    """
    skyline = draw_suit_ground(c, suit, variant, COURT_GROUND)
    if suit == 0:  # a toadstool at the right edge, clear of the Unter's suit sign
        c.blit_sprite(['.8888.', '84c4c48', '8f4f4f8', '8888888', '..8f8..', '..8f8..', '.8fff8.'], 51, 77)
    elif suit == 1:  # tall grass blades along the meadow's edge
        for x in range(3, 58, 3):
            y = skyline(x)
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


def _leaf_brocade(x, y):
    """Brown lozenge lattice with crimson centres on the Leaf King's gold cloth.

    The hanging is yellow, like the crown and the sceptre. A flat fill turned
    them into one gold block; the weave leaves the gold ground but breaks it
    so the regalia read against brown and red.
    """
    row = y // 6
    lx = (x + (3 if row & 1 else 0)) % 6
    ly = y % 6
    d = abs(lx - 2.5) / 2.5 + abs(ly - 2.5) / 2.5
    if d < 0.45:
        return RED
    if 0.70 <= d <= 1.12:
        return BROWN
    return None


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

# Obers wear a longer, fuller coat than the Unters' short doublet, and their
# shoulders sit a pixel wider. Arm tuples use the same shoulder pixels.
OBER_COAT = dict(hem=61, flare=10, sh_b=(22, 26), sh_f=(37, 26))


def _standing(c, suit, flip, look, arms, legs, dx=0, **options):
    """Draws a standing court figure and sets its boots into the suit's ground.

    `options` go to `figure.draw_standing`.
    """
    r = Rig(c, flip=flip, dx=dx)
    F.draw_standing(r, look, arms, legs, **options)
    # The middle of each sole, halfway from ankle to toe, wherever mirroring put it.
    draw_footing(c, suit, [round(r.tx((ankle[0] + toe[0]) / 2, 0)[0]) for _, _, ankle, toe in legs], SOLE_ROW)
    return r


def draw_unter(c, suit):
    """Spodek: young huntsmen and musicians, the suit sign low on the left.

    The sign sits in the white mid-left margin, around y=56: clearly in the
    lower half, well under an Ober's corner pip at y=12, and clear of the turf.
    """
    _draw_ground(c, suit, UNTER)
    # The suit sign sits on the left, where it still shows when the hand fans the cards.
    if suit == 0:  # Acorn: forward fencing lunge facing right, matching blue sleeves & twin blades
        look = dict(
            cape=GREEN,
            swing=-5,
            cape_len=55,
            sleeve_b=LIGHT_BLUE,
            sleeve_f=LIGHT_BLUE,
            cuff=YELLOW,
            hose=LIGHT_RED,
            boot=YELLOW,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=GREEN,
            pattern=lambda x, y: YELLOW if abs(x - 32) <= 2 else None,
            buttons=GREEN,
            hair=BROWN,
            hat=None,
        )
        # The back fist is drawn with the parrying blade, so the arm ends bare.
        arms = (((22, 27), (16, 35), (22, 43), None), ((35, 24), (43, 14), (50, 9), 'grip'))
        legs = (((26, 52), (21, 68), (17, 84), (22, 87)), ((35, 52), (43, 66), (43, 84), (49, 87)))

        def high_blade(r):
            F.sword(r, (50, 9), (55, 36))
            r.line(51, 13, 55, 34, LIGHT_CYAN)

        def parrying_blade(r):
            # Drawn before the back fist so the hand closes over the hilt.
            F.sword(r, (22, 43), (44, 37))
            r.line(25, 42, 42, 38, LIGHT_CYAN)
            F.draw_hand(r, 22, 43, grip=True, toward=(16, 35))

        _standing(
            c,
            suit,
            False,
            look,
            arms,
            legs,
            back_props=high_blade,
            front_props=parrying_blade,
            back_over=True,
            dx=1,
            pose=dict(head=(29, 15), neck=(28, 21), sh_b=(22, 27), sh_f=(35, 24), waist=(29, 44), flare=8, lean=2),
        )
        draw_suit(c, 0, 9, 58, 'v')

    elif suit == 1:  # Leaf: playing a transverse flute in a wide rose-red beret, hanger at his hip
        look = dict(
            cape=RED,
            lining=YELLOW,
            swing=-6,
            sleeve_b=GREEN,
            sleeve_f=GREEN,
            cuff=LIGHT_RED,
            puff=LIGHT_RED,
            hose=LIGHT_GREEN,
            boot=LIGHT_BLUE,
            boot_cuff=CYAN,
            tunic=GREEN,
            skirt=GREEN,
            belt=YELLOW,
            buttons=YELLOW,
            pattern=_stripes(YELLOW, 4),
            hair=BROWN,
            hat=('wide_beret', LIGHT_RED, LIGHT_GREEN, YELLOW),
        )
        arms = (((23, 26), (32, 27), (40, 21), None), ((36, 26), (44, 24), (49, 22), None))
        legs = (((28, 52), (27, 68), (25, 84), (30, 87)), ((34, 52), (36, 68), (38, 84), (44, 87)))

        def hanger(r):
            # Curved hunting-sword hilt and chape peeking behind the coat, as on Prague cards.
            r.part().capsule(22, 43, 14, 35, 1.3).paint(BROWN, None, outline=DARK_GRAY)
            r.part().capsule(16, 37, 13, 39, 0.9).fill(YELLOW)
            r.part().ellipse(13.5, 34.5, 1.4, 1.4).paint(YELLOW, None, outline=BROWN)

        def flute(r):
            r.part().capsule(34, 18.5, 55, 21.7, 1.5).paint(YELLOW, None, outline=BROWN)
            for x in (44, 52, 54):
                r.put(x, 18.5 + (x - 34) * 3.2 / 21, BROWN)
            F.draw_hand(r, 39.5, 21.5, grip=True, toward=(32, 27))
            F.draw_hand(r, 48.5, 23, grip=True, toward=(44, 24))

        _standing(c, suit, True, look, arms, legs, back_props=hanger, front_props=flute, pose=dict(flare=7, lean=-1))
        draw_suit(c, 1, 11, 56, 'v')

    elif suit == 2:  # Bell: bare-headed wide lunge, swinging a two-handed greatsword overhead
        look = dict(
            cape=BLUE,
            swing=-4,
            cape_len=50,
            sleeve_b=LIGHT_RED,
            sleeve_f=LIGHT_RED,
            puff=LIGHT_BLUE,
            cuff=YELLOW,
            hose=YELLOW,
            boot=RED,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=BLUE,
            buttons=YELLOW,
            face='young',
            hair=BROWN,
            hat=None,
        )
        # Elbows frame the head on either side and hands meet above the crown,
        # with `head_over=True` so no sleeve ever obscures the face.
        arms = (((23, 26), (15, 15), (21, 7), 'grip'), ((35, 26), (43, 15), (26, 7), 'grip'))
        legs = (((26, 52), (18, 67), (13, 84), (18, 87)), ((34, 52), (42, 66), (45, 84), (51, 87)))

        def greatsword(r):
            F.sword(r, (23, 7), (4, 25))
            r.line(20, 10, 6, 23, LIGHT_CYAN)
            r.line(20, 11, 6, 24, LIGHT_CYAN)

        _standing(
            c,
            suit,
            True,
            look,
            arms,
            legs,
            back_props=greatsword,
            head_over=True,
            pose=dict(head=(31, 18), neck=(30, 23), sh_b=(23, 26), sh_f=(35, 26), waist=(30, 45), flare=7, lean=1),
        )
        draw_suit(c, 2, 10, 56)

    else:  # Heart: halberd over the shoulder, walking left
        look = dict(
            cape=RED,
            lining=YELLOW,
            swing=-6,
            sleeve_b=YELLOW,
            sleeve_f=YELLOW,
            cuff=LIGHT_RED,
            hose=LIGHT_CYAN,
            boot=RED,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=YELLOW,
            pattern=_stripes(YELLOW, 4),
            hair=YELLOW,
            hat=('cap', LIGHT_RED, WHITE, YELLOW),
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

        _standing(
            c,
            suit,
            True,
            look,
            arms,
            legs,
            back_props=halberd,
            back_over=True,
            # Leans back in pose space. He is mirrored, so the skirt opens
            # away from the low heart pip instead of onto it.
            pose=dict(head=(30, 16), neck=(30, 22), lean=-1),
        )
        draw_suit(c, 3, 11, 56)


def draw_ober(c, suit):
    """Svršek: bearded men in broad plumed hats, the suit sign high in a corner."""
    _draw_ground(c, suit, OBER)
    # The suit sign sits top left, where it still shows when the hand fans the cards.
    if suit == 0:  # Acorn: twin blades — one angled across the chest, one level at the hip
        look = dict(
            cape=GREEN,
            swing=-8,
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
        arms = (((22, 26), (16, 37), (21, 46), 'grip'), ((37, 26), (45, 25), (47, 17), 'grip'))
        legs = (((26, 52), (22, 68), (19, 84), (24, 87)), ((34, 52), (40, 67), (42, 84), (48, 87)))

        def twin_blades(r):
            F.sword(r, (21, 46), (53, 47))
            r.line(25, 46, 50, 47, LIGHT_CYAN)
            F.sword(r, (47, 17), (23, 35))
            r.line(44, 19, 25, 33, LIGHT_CYAN)

        _standing(
            c,
            suit,
            False,
            look,
            arms,
            legs,
            front_props=twin_blades,
            pose=dict(OBER_COAT, lean=1, head=(31, 15), neck=(31, 21)),
            back_over=True,
        )
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
        arms = (((22, 26), (22, 38), (32, 42), None), ((37, 26), (44, 34), (50, 30), 'grip'))
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

        _standing(
            c,
            suit,
            False,
            look,
            arms,
            legs,
            front_props=drum,
            pose=dict(OBER_COAT, lean=-1),
            back_over=True,
        )
        draw_suit(c, 1, 12, 12, 'v')

    elif suit == 2:  # Bell: hand on sword hilt at his side, the other open in greeting, facing left
        look = dict(
            cape=BLUE,
            swing=-9,
            lining=YELLOW,
            sleeve_b=YELLOW,
            sleeve_f=YELLOW,
            # Crimson cuffs: white ones merge with the raised hand into one big white blob.
            cuff=RED,
            puff=LIGHT_BLUE,
            hose=LIGHT_BLUE,
            boot=RED,
            tunic=YELLOW,
            skirt=BLUE,
            belt=RED,
            pattern=_stripes(BLUE, 4),
            face='goatee',
            hair=YELLOW,
            beard=YELLOW,
            hat=('brim', BLUE, YELLOW, RED),
        )
        # The greeting forearm is raised and the wrist set between pixels, so
        # the open palm is four pixels wide and covers the end of the sleeve.
        arms = (((22, 26), (19, 37), (22, 47), 'grip'), ((37, 26), (44, 33), (49.5, 24.5), 'open'))
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

        _standing(
            c,
            suit,
            True,
            look,
            arms,
            legs,
            back_props=scabbard,
            front_props=hilt,
            pose=dict(OBER_COAT, lean=1, head=(31, 15), neck=(31, 21)),
        )
        draw_suit(c, 2, 12, 12)

    else:  # Heart: spear upright in one hand, the other on his hip
        look = dict(
            cape=RED,
            lining=YELLOW,
            swing=-8,
            sleeve_b=YELLOW,
            sleeve_f=YELLOW,
            cuff=RED,
            hose=BLUE,
            boot=RED,
            tunic=LIGHT_RED,
            skirt=RED,
            belt=YELLOW,
            buttons=YELLOW,
            pattern=_stripes(YELLOW, 4),
            face='beard',
            hair=BROWN,
            hat=('brim', LIGHT_RED, YELLOW, RED),
        )
        # Shoulders, neck and head a pixel higher than the other Obers: an
        # upright stance. Elbows and hands stay, so the spear grip does not move.
        arms = (((22, 25), (16, 35), (22, 44), 'open'), ((37, 25), (42, 35), (46, 30), 'grip'))
        legs = (((26, 52), (22, 68), (19, 84), (24, 87)), ((34, 52), (38, 68), (41, 84), (47, 87)))

        def spear(r):
            F.pole(r, (47, 86), (47, 11))
            # A leaf-shaped blade whose point stays clear of the card border.
            r.c.blit_sprite(['..1..', '.1b1.', '.1b1.', '1bb31', '1bb31', '1b331', '.131.', '..1..'], 45, 3)

        _standing(
            c,
            suit,
            False,
            look,
            arms,
            legs,
            back_props=spear,
            pose=dict(OBER_COAT, sh_b=(22, 25), sh_f=(37, 25), head=(30, 14), neck=(30, 20), lean=-1),
            back_over=True,
        )
        draw_suit(c, 3, 12, 12)


def _throne(r, wood, velvet, style, cloth=None):
    """A throne seen from the front, framing the king, in one of four styles.

    'round' has an arched back and gold ball finials, 'gothic' a pointed back
    and spires, 'canopy' a fringed valance with curtains falling to either
    side, 'baroque' a low rounded back between scroll volutes (a crest
    there would hide behind the king's head). The parts beside the corner
    pips (posts, finials, valance ends) stay at y>=23, so a band of white
    card separates them from the pips, which reach about y=21. Only the
    middle, behind the king's head, rises higher.

    `cloth(x, y)`, when given, weaves the cloth of honour instead of a plain
    nap, so a gold hanging is not one flat block behind a gold crown.
    """

    def grain(x, y):
        return darker(wood) if (x + y) % 7 == 0 else None

    # The weave, when there is one, replaces the plain nap wherever the velvet shows.
    nap = cloth or (lambda x, y: darker(velvet) if x % 4 == 0 and y % 4 == 0 else None)
    hanging = cloth or (lambda x, y: darker(velvet) if x % 3 == 0 else None)

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
            # Peak at y=23: the corner acorn's stem ends on y=21, and a peak
            # on that row touches it.
            r.part().poly([(fx - 2.5, 28), (fx, 23), (fx + 2.5, 28)]).paint(YELLOW)
    elif style == 'canopy':
        r.part().rect(12, 26, 48, 66).paint(wood, pattern=grain)
        r.part().rect(16, 28, 44, 66).paint(velvet, pattern=nap)
        for fx, sway in ((12, -1), (48, 1)):
            r.part().poly([(fx - 3, 27), (fx + 3, 27), (fx + 2 - sway, 66), (fx - 2 - sway, 66)]).paint(
                velvet, pattern=hanging
            )
        # Valance top at y=23, two rows under the corner leaves (they end near y=20).
        valance = r.part().rect(9, 23, 51, 27)
        for sx in range(11, 51, 5):
            valance.ellipse(sx + 1.5, 27, 2.6, 2)
        # Gold braid and tassels, in brown on gold hangings so they still show.
        trim = BROWN if velvet == YELLOW else YELLOW
        valance.paint(velvet, pattern=lambda x, y: trim if y == 24 else (cloth(x, y) if cloth else None))
        for sx in range(11, 51, 5):
            r.put(sx + 1.5, 30, trim)
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
            # Ball centre one row above the post, both dropped so the heart
            # pip (it ends near y=18) keeps white card above the finial.
            r.part().rect(fx - 2, 24, fx + 2, 70).paint(wood)
            r.part().ellipse(fx, 23, 2.4, 2.4).paint(YELLOW)
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
    _throne(r, look['throne'], look['cushion'], look['style'], cloth=look.get('cloth'))
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
    _draw_throne_floor(c, suit)
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
            # A gold cloth of honour, woven with a brown and crimson lattice:
            # a flat yellow field swallowed the crown and the sceptre, and pale
            # green hangings left the green robe and the corner leaves one mass.
            cushion=YELLOW,
            cloth=_leaf_brocade,
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
            # outlined dark so the gold doesn't melt into the brown hair or
            # the gold hangings.
            F.pole(r, (44, 46), (39, 19), YELLOW, outline=DARK_GRAY)
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
            # A blue robe over a red tunic: in the Acorn King's red robe he
            # read as the same card at game size.
            sleeve=LIGHT_BLUE,
            robe=LIGHT_BLUE,
            shoe=LIGHT_RED,
            tunic=LIGHT_RED,
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
