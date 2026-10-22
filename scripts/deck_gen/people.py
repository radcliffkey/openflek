"""Small people for the number-card vignettes, drawn with the court-figure rig.

They use the same jointed poses as the courts, scaled down to the room left
under the pips and painted on a thin rig: one dark silhouette outline instead
of an outline per part, which would swallow limbs two pixels wide. The
smallest, the forester and the hornblower, are pixelled by hand on the same
thin rig with the `figure` vignette heads, since the rig's garments turn to
grey mud at a third of court size.
"""

from scripts.deck_gen import figure as F
from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.rig import Rig, darker


def _rig(c, scale, x, flip=False):
    """A thin rig whose figure stands centred on card column `x`."""
    return Rig(c, flip=flip, dx=x - 30, scale=scale, thin=True)


def _pixel_head(r, hx, hy, face, hair, hat):
    """A vignette-size head from the `figure` templates, centred on card pixel (hx, hy) of an unscaled rig."""
    r.sprite(F.SMALL_FACES[face], hx, hy, {'H': hair, 'h': darker(hair), 'J': hair, 'j': darker(hair)}, anchor=(3, 3))
    kind, cloth, trim, band = hat
    top, rows = F.SMALL_HATS[kind]
    subst = {'C': cloth, 'c': darker(cloth), 'T': trim, 't': darker(trim), 'B': band, 'b': darker(band)}
    r.sprite(rows, hx, hy, subst, anchor=(3, 3 - top))


# The forester is too small for the rig's garments, whose pleats and seams
# turn to grey mud at a third of court size, so his body is pixelled by hand:
# fill colours only, the silhouette outline goes round the union afterwards.
# Columns start at the staff; the back hand grips it, the front arm hangs.
FORESTER_BODY = [
    '6.............',
    '6.............',
    '6.............',
    '6.............',
    '6.............',
    '6.............',
    '6.....aaaa....',
    '6...2a2222a2..',
    '6..22a2e22a2..',
    '6.22.a2222a2..',
    '6aa..a2e22a2..',
    'ff...a2222a2..',
    'ff...a2e22a2..',
    '6....666666662',
    '6....a2222aa2.',
    '6...a2222ffa2.',
    '6...a2222ff22.',
    '6...a22222222.',
    '6...a222222222',
    '6...a222222222',
    '6..a2222222222',
    '6..a2222222222',
    '6....ee...ee..',
    '6....ee...ee..',
    '6....66...66..',
    '6....66...66..',
    '6....666..666.',
]


def draw_forester(c, x=19, foot_y=88):
    """A forester in a long green coat, pipe in his mouth, his staff planted beside him.

    `x` is the column of his face; his boots stand on row `foot_y`.
    """
    r = Rig(c, thin=True)
    top = foot_y - len(FORESTER_BODY) + 1
    r.sprite(FORESTER_BODY, x - 8, top)
    hy = top + 3
    _pixel_head(r, x, hy, 'young', BROWN, ('brim', GREEN, LIGHT_RED, BROWN))
    # The pipe: a stem from the lips and the bowl turned up.
    for px, py in ((x + 2, hy + 2), (x + 3, hy + 2), (x + 4, hy + 1), (x + 4, hy + 2)):
        r.plot(px, py, BROWN)
    r.silhouette()
    # Smoke curling from the pipe bowl.
    for px, py in ((x + 4, hy - 1), (x + 5, hy - 2), (x + 5, hy - 3)):
        c.put(px, py, LIGHT_GRAY)


# The sitting huntsman, pixelled by hand like the forester: fill colours only.
# He leans back on his far arm, his near knee drawn up over the far leg; the
# hand under his chin holds the horn, drawn separately as `HORN`.
HORNBLOWER_BODY = [
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '...........ff.........',
    '....cccccc4ff.........',
    '...cccccc4cc..........',
    '...ccccce4c...........',
    '..cc.cccc4c...........',
    '..cc.cccce4..a........',
    '..cc.cccc4c.aa2.......',
    '..cc.22222a2a22.......',
    '.cc.cccccca22.22......',
    '.cc.ccccca22...22.....',
    '.cc.cccccc2.....666...',
    '.cc.cccccc......6666..',
    '.ff.ccccccaa22222666..',
    '.ff.......a2222226666.',
]


# A long straight hunting horn held level from the lips, as in the 1992 deck:
# gold with a brown underside and a hand round the middle; it passes in front
# of the tree trunk and its flared bell stops short of the dog. The
# mouthpiece is row 1, column 0.
HORN = [
    '............6e',
    'eeeeffeeeeeeee',
    '.666ff666666ee',
    '............6e',
]


def draw_hornblower(c, x=16, seat_y=85):
    """A huntsman sitting in the grass, leaning back on one arm and blowing a long horn.

    `x` is the column of his face; he sits on row `seat_y`.
    """
    r = Rig(c, thin=True)
    top = seat_y - len(HORNBLOWER_BODY) + 1
    r.sprite(HORNBLOWER_BODY, x - 8, top)
    _pixel_head(r, x, top + 5, 'young', BROWN, ('cap', GREEN, LIGHT_RED, YELLOW))
    r.sprite(HORN, x + 2, top + 6, anchor=(0, 1))
    r.silhouette()


# The jester, pixelled by hand so every mark of the fool reads at card size:
# motley split down the middle, red on his right and yellow on his left with
# the legs the other way round, a dagged green collar and hem, pointed shoes
# with bells, and a marotte (a fool's sceptre: a stick topped by a little
# capped head) held up in his hand. He hops on one foot, the other kicked out.
JESTER_BODY = [
    '..................',
    '................c.',
    '...............ccc',
    '...............fff',
    '................e.',
    '................6.',
    '.....2a2a2a2....6.',
    '....cccccceeeeeff.',
    'ff.cccccccceeeeff.',
    '.ccccccccceeee..6.',
    '....cccccceeee..6.',
    '....cccccceeee..6.',
    '....cccccceeee....',
    '....2a2a2a2a2a....',
    '...cccccceeeeee...',
    '...c.c.c.e.e.e....',
    '.....ee....cc.....',
    '.....ee.....ccc...',
    '.....ee......ccc..',
    '.....ee.......ccc.',
    '.....ee........c2e',
    '.....ee.........2.',
    '.....ee...........',
    '.....ee...........',
    '.....ee...........',
    '....222...........',
    '..e2222...........',
]

# A three-pointed fool's cap, red, yellow and green, each point tipped with a
# bell; the band sits on the brow.
JESTER_CAP = [
    'e.......e',
    'cc..e..ee',
    '.cc.2.ee.',
    '..cc2ee..',
    '.2a2a2a2.',
]


def draw_jester(c, x=30, foot_y=88):
    """A jester dancing on one foot, his marotte held high.

    `x` is the column of his face; his standing foot is on row `foot_y`.
    """
    r = Rig(c, thin=True)
    top = foot_y - len(JESTER_BODY) + 1
    r.sprite(JESTER_BODY, x - 8, top)
    hy = top + 3
    r.sprite(F.SMALL_FACES['young'], x, hy, {'H': YELLOW, 'h': BROWN}, anchor=(3, 3))
    r.sprite(JESTER_CAP, x, hy, anchor=(4, 7))
    r.silhouette()


def _musician(c, x, scale, flip, look, arms, legs):
    r = _rig(c, scale, x, flip)
    F.draw_standing(r, look, arms, legs)
    r.silhouette()


# The band's instruments, pixelled at card size: at a quarter scale, shapes
# built on the rig shrink to blobs. Each is placed beside its player's hands.
TRUMPET = ['........e', '.......ee', 'eeeeeeeee', '.......e6', '........6']
DRUM = ['.fffff.', '4444444', 'e4e4e4e', 'eeeeeee', '4444444']
FIDDLE = ['6......', '.6.....', '..6.66.', '...6ee6', '....66.', '...6666']
FIDDLE_BOW = ['....7', '...7.', '..7..', '.7...', '7....']


def _instrument(c, rows, x0, y0):
    """Blits a sprite with its top-left at (x0, y0), edged in dark grey wherever it meets the white card."""
    c.blit_sprite(rows, x0, y0)
    pix = {(x0 + dx, y0 + dy) for dy, row in enumerate(rows) for dx, ch in enumerate(row) if ch != '.'}
    for x, y in pix:
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (nx, ny) not in pix and c.get(nx, ny) == WHITE:
                c.put(nx, ny, DARK_GRAY)


def draw_musicians(c):
    """A village band: a trumpeter, a drummer and a fiddler."""
    s = 0.22
    stand = (((27, 52), (25, 68), (24, 84), (29, 87)), ((33, 52), (37, 68), (38, 84), (44, 87)))

    _musician(
        c,
        13,
        s,
        False,
        dict(sleeve_b=LIGHT_RED, sleeve_f=LIGHT_RED, hose=BLUE, boot=BROWN, tunic=LIGHT_RED, skirt=LIGHT_RED,
             belt=YELLOW, hair=BROWN, hat=('cap', GREEN, WHITE, YELLOW)),
        (((23, 26), (30, 34), (38, 24), 'grip'), ((36, 26), (43, 28), (46, 14), 'grip')),
        stand,
    )
    _musician(
        c,
        30,
        s,
        False,
        dict(sleeve_b=GREEN, sleeve_f=GREEN, hose=YELLOW, boot=BROWN, tunic=GREEN, skirt=GREEN, belt=LIGHT_RED,
             face='beard', hair=BROWN, hat=('brim', LIGHT_RED, YELLOW, GREEN)),
        (((23, 26), (30, 36), (40, 34), 'grip'), ((36, 26), (44, 32), (48, 34), 'grip')),
        stand,
    )
    _musician(
        c,
        47,
        s,
        True,
        dict(sleeve_b=CYAN, sleeve_f=CYAN, hose=LIGHT_RED, boot=BROWN, tunic=CYAN, skirt=CYAN, belt=YELLOW,
             hair=YELLOW, hat=('beret', BLUE, LIGHT_RED, YELLOW)),
        (((23, 26), (34, 32), (44, 33), 'grip'), ((36, 26), (36, 38), (40, 30), 'grip')),
        stand,
    )
    # A straight herald's trumpet level from the lips, a drum slung at the hip
    # with one stick raised and one on the skin, and a fiddle under the chin
    # with the bow across its strings.
    _instrument(c, TRUMPET, 15, 68)
    _instrument(c, DRUM, 31, 75)
    for x, y in ((31, 72), (30, 71), (35, 74)):
        c.put(x, y, BROWN)
    _instrument(c, FIDDLE_BOW, 40, 71)
    _instrument(c, FIDDLE, 39, 68)


def draw_wild_man(c, x=28, scale=0.66):
    """The wild man of Czech heraldry: bearded, girdled and crowned with oak, a club on his shoulder."""
    r = Rig(c, dx=x - 30, scale=scale)
    look = dict(
        sleeve_b=WHITE,
        sleeve_f=WHITE,
        hose=WHITE,
        boot=WHITE,
        tunic=WHITE,
        # A girdle of autumn oak leaves: a green one vanished into the oak behind him.
        skirt=BROWN,
        belt=GREEN,
        collar=WHITE,
        skirt_pattern=lambda x, y: YELLOW if (x * 2 + y) % 5 == 0 else (LIGHT_RED if (x * 3 + y) % 11 == 0 else None),
        # Body hair in short strokes over the chest.
        pattern=lambda x, y: LIGHT_GRAY if (x + 2 * y) % 7 == 0 else None,
        face='old',
        hair=BROWN,
        beard=BROWN,
        hat=('wreath', GREEN, YELLOW, GREEN),
    )
    arms = (((23, 26), (15, 36), (18, 46), 'open'), ((36, 26), (45, 34), (50, 27), 'grip'))
    legs = (((26, 52), (22, 68), (19, 84), (14, 87)), ((34, 52), (39, 68), (41, 84), (46, 87)))

    def club(rr):
        # Short enough that its head stays clear of the Ace's ribbon.
        rr.part().chain([(49, 32), (53, 19), (56, 8)], [1.4, 2.4, 3.4]).paint(BROWN, outline=DARK_GRAY)
        for kx, ky in ((52, 21), (55, 12), (56, 7)):
            rr.put(kx, ky, YELLOW)

    F.draw_standing(r, look, arms, legs, back_props=club, pose=dict(hem=60, flare=7))


def draw_cupid(c, x=44, scale=0.27):
    """A winged cupid facing left, drawing his bow."""
    r = _rig(c, scale, x, flip=True)
    # Wings behind the shoulders: the far one light cyan, the near one white
    # with cyan feather edges so it doesn't read as a hole in the figure.
    r.part().ellipse(17, 26, 11, 5, angle=-60).paint(LIGHT_CYAN, None)
    r.part().ellipse(17, 26, 11, 5, angle=-30).paint(WHITE, None, pattern=lambda px, py: LIGHT_CYAN if (px + py) % 3 == 0 else None)
    look = dict(
        sleeve_b=WHITE,
        sleeve_f=WHITE,
        hose=WHITE,
        boot=WHITE,
        tunic=WHITE,
        skirt=LIGHT_RED,
        belt=LIGHT_RED,
        collar=WHITE,
        hair=YELLOW,
        hat=None,
    )
    arms = (((23, 26), (34, 30), (42, 26), 'grip'), ((36, 26), (43, 24), (52, 24), 'grip'))
    legs = (((27, 52), (22, 68), (18, 84), (23, 87)), ((33, 52), (40, 66), (42, 84), (48, 87)))

    F.draw_standing(r, look, arms, legs, pose=dict(hem=50, flare=6))
    r.silhouette()
    # Bow, string and arrow go on after the silhouette as crisp one-pixel
    # lines: outlined, they would thicken into a grey tangle at this scale.
    for (x0, y0), (x1, y1) in (((52, 4), (56, 14)), ((56, 14), (56, 34)), ((56, 34), (52, 44))):
        r.line(x0, y0, x1, y1, BROWN)
    r.line(52, 5, 42, 26, LIGHT_GRAY)
    r.line(42, 26, 52, 43, LIGHT_GRAY)
    r.line(38, 26, 64, 25, BROWN)
    for px, py in ((68, 25), (67, 24), (67, 26)):
        r.put(px, py, DARK_GRAY)
