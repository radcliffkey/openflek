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
)
from scripts.deck_gen.rig import Rig, darker
from scripts.deck_gen.symbols import draw_suit


def draw_pedestal(c, suit, is_king=False):
    """Draws the rolling turf under a standing figure, or a tiled floor under a throne."""
    for y in range(80, 98):
        for x in range(2, 59):
            if not c.in_interior(x, y):
                continue
            wave = int(round(math.sin((x + suit * 9) * 0.22) * 2.0))
            hill_y = (84 if is_king else 82) + wave
            if y < hill_y:
                continue
            if y == hill_y:
                col = DARK_GRAY
            elif is_king and y >= 88:
                tile = ((x // 5) + ((y - 88) // 3)) & 1
                col = [(CYAN, DARK_GRAY), (GREEN, YELLOW), (YELLOW, CYAN), (LIGHT_CYAN, CYAN)][suit][tile]
            elif y <= hill_y + 3:
                col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            elif 12 <= x <= 48:
                col = YELLOW if ((x + y) & 1) == 0 else LIGHT_GREEN
            else:
                col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            c.put(x, y, col)


def _tufts(c, xs, y=87):
    """Grass tufts over the boot soles so the feet stand in the turf rather than on it."""
    for bx in xs:
        for dx in range(-4, 5, 2):
            c.put(bx + dx, y, GREEN)
            c.put(bx + dx + 1, y - 1, LIGHT_GREEN)


def _ermine(x, y):
    """Ermine fur: white with a scatter of black tail tips."""
    return DARK_GRAY if (x % 4 == 0 and y % 3 == 0) or (x % 4 == 2 and y % 3 == 1 and x % 8 == 2) else None


def _stripes(col, step=3):
    return lambda x, y: col if y % step == 0 else None


def _quarters(col):
    return lambda x, y: col if (x + y) % 4 == 0 else None


# Obers wear a longer, fuller coat skirt than the Unters' short doublet.
OBER_COAT = dict(hem=61, flare=10)


def _standing(c, flip, look, arms, legs, back_props=None, front_props=None, pose=None):
    r = Rig(c, flip=flip)
    F.draw_standing(r, look, arms, legs, back_props=back_props, front_props=front_props, pose=pose)
    return r


def draw_unter(c, suit):
    """Spodek: young huntsmen and musicians in caps, the suit sign low beside the legs."""
    draw_pedestal(c, suit)
    if suit == 0:  # Acorn: swinging a sword up over his head, striding right
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

        _standing(c, False, look, arms, legs, back_props=blade)
        _tufts(c, [16, 45])
        draw_suit(c, 0, 50, 72, 'v')

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
        arms = (((23, 26), (31, 34), (39, 24), 'grip'), ((36, 26), (43, 33), (47, 24), 'grip'))
        legs = (((28, 52), (27, 68), (25, 84), (30, 87)), ((34, 52), (36, 68), (38, 84), (44, 87)))

        def flute(r):
            r.part().capsule(34, 22, 54, 22, 1.0).paint(YELLOW, None, outline=BROWN)
            for x in (44, 47, 50):
                r.put(x, 22, BROWN)

        _standing(c, True, look, arms, legs, front_props=flute)
        _tufts(c, [21, 33])
        draw_suit(c, 1, 48, 72, 'v')

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
            hair=BROWN,
            hat=('cap', LIGHT_RED, YELLOW, CYAN),
        )
        arms = (((23, 26), (16, 36), (23, 44), 'open'), ((36, 26), (40, 38), (45, 47), 'grip'))
        legs = (((26, 52), (23, 68), (20, 84), (25, 87)), ((34, 52), (38, 68), (40, 84), (46, 87)))

        def planted(r):
            F.sword(r, (45, 47), (47, 85))

        _standing(c, False, look, arms, legs, front_props=planted)
        _tufts(c, [22, 43])
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
        arms = (((23, 26), (21, 38), (27, 46), 'open'), ((36, 26), (41, 33), (40, 23), 'grip'))
        legs = (((26, 52), (22, 68), (17, 83), (22, 87)), ((34, 52), (40, 67), (43, 83), (49, 87)))

        def halberd(r):
            F.pole(r, (24, 52), (52, 2))
            r.part().poly([(46, 6), (50, 4), (55, 10), (52, 13)]).paint(LIGHT_CYAN, None, outline=BLUE)
            r.part().poly([(50, 3), (53, 0), (52, 6)]).paint(LIGHT_CYAN, None, outline=BLUE)

        _standing(c, True, look, arms, legs, back_props=halberd)
        _tufts(c, [17, 40])
        draw_suit(c, 3, 50, 72)


def draw_ober(c, suit):
    """Svršek: bearded men in broad plumed hats, the suit sign high in a corner."""
    draw_pedestal(c, suit)
    if suit == 0:  # Acorn: raising a sword forward, fist on hip, facing left
        look = dict(
            cape=GREEN,
            swing=-9,
            lining=LIGHT_GREEN,
            sleeve_b=LIGHT_RED,
            sleeve_f=LIGHT_RED,
            cuff=WHITE,
            puff=YELLOW,
            hose=GREEN,
            boot=YELLOW,
            tunic=LIGHT_RED,
            skirt=LIGHT_RED,
            belt=YELLOW,
            pattern=_stripes(YELLOW, 4),
            face='beard',
            hair=BROWN,
            hat=('brim', LIGHT_RED, WHITE, YELLOW),
        )
        arms = (((23, 26), (17, 35), (24, 43), 'grip'), ((36, 26), (43, 22), (49, 14), 'grip'))
        legs = (((26, 52), (22, 68), (19, 84), (24, 87)), ((34, 52), (40, 67), (42, 84), (48, 87)))

        def blade(r):
            F.sword(r, (49, 14), (37, 1))

        _standing(c, True, look, arms, legs, front_props=blade, pose=OBER_COAT)
        _tufts(c, [19, 42])
        draw_suit(c, 0, 47, 12, 'v')

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
            face='beard',
            hair=BROWN,
            hat=('brim', LIGHT_RED, YELLOW, GREEN),
        )
        arms = (((23, 26), (24, 39), (34, 41), 'grip'), ((36, 26), (44, 34), (50, 30), 'grip'))
        legs = (((26, 52), (23, 68), (20, 84), (25, 87)), ((34, 52), (38, 68), (40, 84), (46, 87)))

        def drum(r):
            d = r.part().ellipse(41, 52, 8, 3).rect(33, 52, 49, 63).ellipse(41, 63, 8, 2.5)
            d.paint(YELLOW, pattern=lambda x, y: RED if (x + y) % 5 == 0 else None)
            r.part().rect(33, 51, 49, 53).paint(LIGHT_RED)
            r.part().rect(33, 62, 49, 64).paint(LIGHT_RED)
            r.part().ellipse(41, 50, 7.5, 2.4).paint(WHITE, None, outline=LIGHT_GRAY)
            F.pole(r, (34, 41), (39, 49))
            F.pole(r, (50, 30), (45, 48))

        _standing(c, False, look, arms, legs, front_props=drum, pose=OBER_COAT)
        _tufts(c, [21, 43])
        draw_suit(c, 1, 12, 12, 'v')

    elif suit == 2:  # Bell: hand on sword hilt at his side, the other open in greeting, facing left
        look = dict(
            cape=CYAN,
            swing=-9,
            lining=LIGHT_CYAN,
            sleeve_b=LIGHT_RED,
            sleeve_f=LIGHT_RED,
            cuff=WHITE,
            puff=YELLOW,
            hose=YELLOW,
            boot=LIGHT_RED,
            tunic=YELLOW,
            skirt=LIGHT_RED,
            belt=CYAN,
            pattern=_quarters(LIGHT_RED),
            face='beard',
            hair=YELLOW,
            beard=YELLOW,
            hat=('brim', CYAN, LIGHT_RED, YELLOW),
        )
        arms = (((23, 26), (19, 37), (22, 47), 'grip'), ((36, 26), (43, 30), (50, 25), 'open'))
        legs = (((26, 52), (24, 68), (21, 84), (26, 87)), ((34, 52), (37, 68), (39, 84), (45, 87)))

        def scabbard(r):
            r.part().capsule(21, 49, 9, 71, 1.4).paint(BROWN)
            r.part().capsule(22, 47, 23, 42, 0.7).fill(BROWN)
            r.part().capsule(19, 48, 25, 46, 0.7).fill(YELLOW)

        _standing(c, True, look, arms, legs, back_props=scabbard, pose=OBER_COAT)
        _tufts(c, [22, 41])
        draw_suit(c, 2, 47, 12)

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
            F.pole(r, (47, 86), (47, 5))
            r.part().poly([(47, -1), (49, 5), (47, 8), (45, 5)]).paint(LIGHT_CYAN, None, outline=BLUE)

        _standing(c, False, look, arms, legs, back_props=spear, pose=OBER_COAT)
        _tufts(c, [21, 44])
        draw_suit(c, 3, 12, 12)


def _throne(r, wood, velvet):
    """A throne seen from the front: arched back with finials framing the king, velvet panel inside."""
    back = r.part().rect(12, 26, 48, 66).ellipse(30, 26, 18, 7)
    back.paint(wood, pattern=lambda x, y: darker(wood) if (x + y) % 7 == 0 else None)
    panel = r.part().rect(16, 28, 44, 66).ellipse(30, 28, 14, 5)
    panel.paint(velvet, pattern=lambda x, y: darker(velvet) if x % 4 == 0 and y % 4 == 0 else None)
    for fx in (12, 48):
        r.part().rect(fx - 2, 20, fx + 2, 70).paint(wood)
        r.part().ellipse(fx, 18, 2.6, 2.6).paint(YELLOW)
    # Seat front and legs below the robe.
    r.part().rect(11, 66, 49, 70).paint(wood)
    r.part().rect(11, 70, 14, 86).paint(wood)


def _seated(c, flip, look, front_arm, back_arm, props_back=None, props_front=None):
    """A crowned king on a throne, robe over the knees and an ermine stole.

    Arms are (shoulder, elbow, wrist, hand) as for standing figures; the
    king faces right before mirroring.
    """
    r = Rig(c, flip=flip)
    j = dict(head=(30, 16), neck=(30, 22), sh_b=(24, 27), sh_f=(35, 27), waist=(30, 46))
    _throne(r, look['throne'], look['cushion'])
    if props_back:
        props_back(r)
    F.cape(r, j, look['mantle'], length=78, swing=-5)
    bsh, bel, bwr, bhand = back_arm
    F.arm(r, bsh, bel, bwr, look['sleeve'], cuff=WHITE)
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
    # Ermine stole over the shoulders and down the front edge of the robe.
    stole = r.part().ellipse(30, 25, 8.5, 3).capsule(36, 26, 38, 46, 1.8).capsule(38, 46, 46, 56, 1.8)
    stole.paint(WHITE, None, outline=LIGHT_GRAY, pattern=_ermine)
    F.draw_head(r, 30, 16, face=look.get('face', 'old'), hair=look['hair'], beard=look.get('beard'), hat=look['hat'])
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
            cushion=LIGHT_RED,
            mantle=GREEN,
            sleeve=LIGHT_RED,
            robe=LIGHT_RED,
            shoe=BROWN,
            tunic=GREEN,
            pattern=_quarters(YELLOW),
            hair=LIGHT_GRAY,
            beard=LIGHT_GRAY,
            hat=('crown', LIGHT_RED, LIGHT_RED, YELLOW),
        )

        def sceptre(r):
            F.pole(r, (46, 50), (48, 22), YELLOW)
            r.part().ellipse(48, 21, 2, 2).paint(LIGHT_GREEN)

        def orb(r):
            r.part().ellipse(38, 52, 2.6, 2.6).paint(YELLOW)
            r.put(38, 48, YELLOW)
            r.put(38, 47, YELLOW)

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
            cushion=GREEN,
            mantle=LIGHT_RED,
            sleeve=GREEN,
            robe=GREEN,
            shoe=LIGHT_RED,
            tunic=LIGHT_RED,
            pattern=_stripes(YELLOW, 4),
            hair=BROWN,
            beard=BROWN,
            face='beard',
            hat=('crown', GREEN, LIGHT_RED, YELLOW),
        )

        def sceptre(r):
            F.pole(r, (44, 46), (34, 20), YELLOW)
            r.part().poly([(33, 16), (36, 19), (33, 22), (30, 19)]).paint(YELLOW)

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
            cushion=CYAN,
            mantle=CYAN,
            sleeve=LIGHT_RED,
            robe=LIGHT_RED,
            shoe=CYAN,
            tunic=CYAN,
            pattern=_quarters(YELLOW),
            hair=YELLOW,
            beard=YELLOW,
            face='old',
            hat=('crown', LIGHT_RED, CYAN, YELLOW),
        )

        def blade(r):
            F.sword(r, (46, 44), (49, 9))

        _seated(
            c,
            False,
            look,
            ((35, 27), (41, 39), (46, 44), 'grip'),
            ((24, 27), (24, 41), (35, 51), 'open'),
            props_front=blade,
        )

    else:  # Heart: raising a golden chalice, facing left
        look = dict(
            throne=BROWN,
            cushion=LIGHT_RED,
            mantle=LIGHT_RED,
            sleeve=CYAN,
            robe=CYAN,
            shoe=LIGHT_RED,
            tunic=YELLOW,
            pattern=_stripes(LIGHT_RED, 4),
            robe_pattern=_quarters(LIGHT_CYAN),
            face='beard',
            hair=YELLOW,
            beard=YELLOW,
            hat=('crown', LIGHT_RED, LIGHT_MAGENTA, YELLOW),
        )

        def chalice(r):
            r.part().poly([(44, 27), (52, 27), (50, 32), (46, 32)]).ellipse(48, 27, 4, 1.2).paint(YELLOW)
            r.part().rect(47, 32, 48, 36).paint(YELLOW, None, outline=BROWN)
            r.part().ellipse(48, 37, 2.5, 1).paint(YELLOW, None)

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
