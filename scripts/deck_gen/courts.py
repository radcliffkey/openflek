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
    """A fixed pseudo-random value per pixel for scattering leaves, flowers and pebbles."""
    return (x * 73 + y * 151 + x * y * 7) % 97


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
        if d <= 2:
            return GREEN if dither else DARK_GRAY
        if h < 5:
            return YELLOW
        if h < 8:
            return RED
        if h < 10:
            return LIGHT_RED
        return BROWN if dither or h > 60 else DARK_GRAY
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
    if 14 <= x <= 46:
        return YELLOW if dither else BROWN
    if h < 12:
        return LIGHT_RED if h < 8 else RED
    return GREEN if dither else LIGHT_GREEN


def _floor_colour(suit, x, y):
    """The throne-room floor in front of the dais, one kind per suit.

    Acorns get oak parquet, Leaves green and gold lozenges, Bells a black and
    white marble chequer, Hearts a red carpet runner on stone.
    """
    d = y - 90
    if suit == 0:
        plank = (x + (d // 2) * 3) // 6
        if d % 2 == 1 and (x + (d // 2) * 3) % 6 == 0:
            return DARK_GRAY
        return YELLOW if plank % 2 else BROWN
    if suit == 1:
        # Lozenges eight wide and four tall, each row offset by half a lozenge.
        lx = (x + 4 * ((d // 4) % 2)) % 8 - 3.5
        ly = d % 4 - 1.5
        return YELLOW if abs(lx) / 4 + abs(ly) / 2 <= 1 else GREEN
    if suit == 2:
        return DARK_GRAY if ((x - 2) // 5 + d // 3) % 2 else WHITE
    if abs(x - 30) <= 9:
        return YELLOW if y == 97 and x % 2 else (LIGHT_RED if (x + y) % 4 else RED)
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
    if suit == 0:  # a toadstool and a fern on the forest floor
        c.blit_sprite(['.8888.', '84c4c48', '8f4f4f8', '8888888', '..8f8..', '..8f8..', '.8fff8.'], 4, 77)
        for k in range(4):
            c.line(53, 83, 50 + k * 2, 76 + k, GREEN if k & 1 else LIGHT_GREEN)
    elif suit == 1:  # tall grass blades along the meadow's edge
        for x in range(3, 58, 3):
            y = 82 + int(round(math.sin((x + 9) * 0.22) * 2.0))
            c.line(x, y, x + (1 if x % 2 else -1), y - 3 - x % 2, GREEN if x % 2 else LIGHT_GREEN)
    elif suit == 3:  # clipped box hedges at the corners of the rose beds
        for hx in (6, 54):
            c.fill_ellipse(hx, 81, 4, 3, GREEN, LIGHT_GREEN, outline=DARK_GRAY, mode='checker')


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


def _quarters(col):
    return lambda x, y: col if (x + y) % 4 == 0 else None


# Obers wear a longer, fuller coat skirt than the Unters' short doublet.
OBER_COAT = dict(hem=61, flare=10)


def _standing(c, suit, flip, look, arms, legs, back_props=None, front_props=None, pose=None):
    """Draws a standing court figure and grounds it: grass (or a shadow on cobbles) under each boot sole."""
    r = Rig(c, flip=flip)
    F.draw_standing(r, look, arms, legs, back_props=back_props, front_props=front_props, pose=pose)
    # The middle of each sole, halfway from ankle to toe, wherever mirroring put it.
    _tufts(c, suit, [round(r.tx((ankle[0] + toe[0]) / 2, 0)[0]) for _, _, ankle, toe in legs])
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

        _standing(c, suit, False, look, arms, legs, back_props=blade)
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
        # Both elbows raised, hands on the flute; the hands are drawn with the flute.
        arms = (((23, 26), (32, 27), (40, 21), None), ((36, 26), (45, 27), (49, 22), None))
        legs = (((28, 52), (27, 68), (25, 84), (30, 87)), ((34, 52), (36, 68), (38, 84), (44, 87)))

        def flute(r):
            # Mouthpiece at the lips, the tube running sideways and a little down.
            r.part().capsule(34, 18.5, 57, 22, 1.5).paint(YELLOW, None, outline=BROWN)
            for x in (44, 54):
                r.put(x, 18.5 + (x - 34) * 3.5 / 23, BROWN)
            F.draw_hand(r, 40, 20, grip=True)
            F.draw_hand(r, 49, 21, grip=True)

        _standing(c, suit, True, look, arms, legs, front_props=flute)
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
            face='moustache',
            hair=BROWN,
            hat=('cap', LIGHT_RED, YELLOW, CYAN),
        )
        arms = (((23, 26), (16, 36), (23, 44), 'open'), ((36, 26), (40, 38), (45, 47), 'grip'))
        legs = (((26, 52), (23, 68), (20, 84), (25, 87)), ((34, 52), (38, 68), (40, 84), (46, 87)))

        def planted(r):
            F.sword(r, (45, 47), (47, 85))

        _standing(c, suit, False, look, arms, legs, front_props=planted)
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

        _standing(c, suit, True, look, arms, legs, back_props=halberd)
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

        _standing(c, suit, True, look, arms, legs, front_props=blade, pose=OBER_COAT)
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
            face='moustache',
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

        _standing(c, suit, False, look, arms, legs, front_props=drum, pose=OBER_COAT)
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
            face='goatee',
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

        _standing(c, suit, True, look, arms, legs, back_props=scabbard, pose=OBER_COAT)
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

        _standing(c, suit, False, look, arms, legs, back_props=spear, pose=OBER_COAT)
        draw_suit(c, 3, 12, 12)


def _throne(r, wood, velvet, style):
    """A throne seen from the front, framing the king, in one of four styles.

    'round' has an arched back and gold ball finials, 'gothic' a pointed back
    and spires, 'canopy' a fringed valance with curtains falling to either
    side, 'baroque' scroll volutes and a shell crest. Tops stay below y=21,
    clear of the corner pips.
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
        # A scallop shell on the crest, its ribs fanning from the hinge.
        r.part().ellipse(30, 22, 5, 3.5).rect(25, 22, 35, 24).paint(YELLOW)
        for k in (-4, -2, 0, 2, 4):
            r.line(30, 25, 30 + k, 20 + abs(k) // 2, BROWN)
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
    _throne(r, look['throne'], look['cushion'], look['style'])
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
            style='gothic',
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
            # Angled across the gilded throne post so the two don't merge.
            F.pole(r, (43, 53), (53, 29), YELLOW, outline=BROWN)
            r.part().ellipse(54, 27, 2.2, 2.2).paint(LIGHT_GREEN)

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
            style='canopy',
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
            F.pole(r, (44, 46), (34, 20), YELLOW, outline=BROWN)
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
            style='round',
            cushion=LIGHT_RED,
            mantle=LIGHT_RED,
            sleeve=CYAN,
            robe=CYAN,
            shoe=LIGHT_RED,
            tunic=YELLOW,
            pattern=_stripes(LIGHT_RED, 4),
            robe_pattern=_quarters(LIGHT_CYAN),
            face='forked',
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
