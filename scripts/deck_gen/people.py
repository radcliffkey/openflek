"""Small people for the number-card vignettes and the wild man of the Acorn Ace.

The vignette people are drawn on a thin rig: one dark silhouette outline
instead of an outline per part, which would swallow limbs two pixels wide.
The forester, the horn-blower, the jester, the village band and Cupid are
pixelled by hand with the `figure` vignette heads where a face is wanted.
Scaled court garments turn to grey mud at a third of court size, and a
white cherub scaled down vanishes into the card. The wild man is a full
pose at two-thirds size, in a tawny pelt rather than a white one.
"""

from scripts.deck_gen import figure as F
from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    DARK_GRAY,
    GREEN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.rig import Rig


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
    F.draw_head(r, x, hy, 'young', BROWN, hat=('brim', GREEN, LIGHT_RED, BROWN), small=True)
    # The pipe: a stem from the lips and the bowl turned up.
    for px, py in ((x + 2, hy + 2), (x + 3, hy + 2), (x + 4, hy + 1), (x + 4, hy + 2)):
        r.plot(px, py, BROWN)
    r.silhouette()
    # Smoke curling from the pipe bowl.
    for px, py in ((x + 4, hy - 1), (x + 5, hy - 2), (x + 5, hy - 3)):
        c.put(px, py, LIGHT_GRAY)


# The sitting huntsman, pixelled by hand like the forester: fill colours only.
# He leans back on his far arm, his near knee drawn up over the far leg. His
# near sleeve rises to the hand gripping the horn, drawn separately as
# `HORN`. A belt breaks up the red coat, and the buckskin breeches are
# yellow: green ones made the raised knee read as a bush in the grass. The
# gap under the knee lets the silhouette outline the thigh and shin.
HORNBLOWER_BODY = [
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '......................',
    '....cccccc4cc.........',
    '...cccccc4cccc........',
    '...ccccce4cc..........',
    '..cc.cccc4c...........',
    '..cc.666e66...ee......',
    '..cc.cccc4c..eeee.....',
    '..cc.cccc4c.eee.ee....',
    '.cc.ccccc4.eee..eee...',
    '.cc.cccc4.eee....ee...',
    '.cc.cccc.eee....666...',
    '.cc.ccccceee....6666..',
    '.ff.ccccceeeeee66666..',
    '.ff.......eeeee666666.',
]


# A long straight hunting horn held level from the lips, as in the 1992 deck:
# gold with a brown underside; it passes in front of the tree trunk and its
# flared bell stops short of the dog. His fist grips it from below, a few
# pixels from his mouth, with the sleeve cuff behind it: a hand laid over the
# tube reads as a gap in the horn. The mouthpiece is row 1, column 0.
HORN = [
    '............6e',
    'eeeeeeeeeeeeee',
    '.666ff666666ee',
    '...cff7.....6e',
]


def draw_hornblower(c, x=16, seat_y=85):
    """A huntsman sitting in the grass, leaning back on one arm and blowing a long horn.

    `x` is the column of his face; he sits on row `seat_y`.
    """
    r = Rig(c, thin=True)
    top = seat_y - len(HORNBLOWER_BODY) + 1
    r.sprite(HORNBLOWER_BODY, x - 8, top)
    F.draw_head(r, x, top + 5, 'young', BROWN, hat=('cap', GREEN, LIGHT_RED, YELLOW), small=True)
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
    F.draw_head(r, x, hy, 'young', YELLOW, small=True)
    r.sprite(JESTER_CAP, x, hy, anchor=(4, 7))
    r.silhouette()


# The village band is pixelled at card size using fill colours only, so
# `Rig(thin=True).silhouette()` wraps one crisp dark-grey outline around each
# figure and its arms without doubling an inner outline. Hats start on row 68
# and boots stand on row 87, clear of the Ten's lowest bells at row 63.
TRUMPETER_BODY = [
    '..ccccc..ff.',
    '.cccccccccc.',
    '.cc4cccc....',
    '..eeeee.....',
    '.ccccccc....',
    '..99..99....',
    '..99..99....',
    '..99..99....',
    '..66..66....',
    '..66..66....',
    '..666.666...',
]

TRUMPET = [
    '........e',
    'eeeeeeeee',
    '....ff.6e',
    '........6',
]

DRUMMER_BODY = [
    '..2aaa2.....',
    '.2aaaaa2ff..',
    '.22aaa22....',
    '..ee6ee.....',
    '.2aaaaa2....',
    '..ee..ee....',
    '..ee..ee....',
    '..ee..ee....',
    '..66..66....',
    '..66..66....',
    '..666.666...',
]

DRUM_BODY = [
    'ffffff',
    'cccccc',
    'e4ee4e',
    'ee4eee',
    'cccccc',
]

FIDDLER_BODY = [
    '..99999.....',
    '.99999999ff.',
    '.991999ff...',
    '..eeeee.....',
    '.9999999....',
    '..cc..cc....',
    '..cc..cc....',
    '..cc..cc....',
    '..66..66....',
    '..66..66....',
    '..666.666...',
]

FIDDLE_BODY = [
    '.6ee6...',
    '6eeee666',
    '.666....',
]


def draw_musicians(c):
    """A village band: a trumpeter, a bearded drummer and a fiddler."""
    # Trumpeter, facing right: crimson doublet, raised sleeve and herald's trumpet.
    r1 = Rig(c, thin=True)
    r1.sprite(TRUMPETER_BODY, 8, 77)
    F.draw_head(r1, 11, 74, 'young', BROWN, hat=('cap', GREEN, YELLOW, LIGHT_RED), small=True)
    r1.sprite(TRUMPET, 14, 74)
    r1.silhouette()

    # Bearded drummer: green coat, red plumed brimmed hat, side drum outlined
    # against his hip, and crisp one-pixel drumsticks drawn after the silhouette.
    r2 = Rig(c, thin=True)
    r2.sprite(DRUMMER_BODY, 26, 77)
    F.draw_head(r2, 30, 74, 'beard', BROWN, beard=BROWN, hat=('brim', LIGHT_RED, YELLOW, GREEN), small=True)
    r2.silhouette()
    rd = Rig(c, thin=True)
    rd.sprite(DRUM_BODY, 34, 81)
    rd.silhouette()
    c.line(35, 77, 38, 80, BROWN)
    c.line(32, 80, 36, 81, BROWN)

    # Fiddler, mirrored about column 50 to face into the band, bow across strings.
    r3 = Rig(c, flip=True, axis=50, thin=True)
    r3.sprite(FIDDLER_BODY, 46, 77)
    F.draw_head(r3, 50, 74, 'young', YELLOW, hat=('beret', BLUE, LIGHT_RED, YELLOW), small=True)
    r3.sprite(FIDDLE_BODY, 52, 75)
    r3.silhouette()
    c.line(44, 73, 47, 79, LIGHT_GRAY)
    # Footing shadows on the town square paving under all three pairs of boots.
    for x0, x1 in ((9, 17), (27, 35), (45, 53)):
        c.line(x0, 88, x1, 88, DARK_GRAY)


def draw_wild_man(c, x=28, scale=0.66):
    """The wild man of Czech heraldry: tawny pelt, oak-leaf girdle, club on his shoulder.

    Consistent brown-and-tawny fur across chest, arms and legs so he stands out
    warmly against the dark green oak, with bare ankles tucked into the turf.
    """
    r = Rig(c, dx=x - 30, scale=scale)

    def fur(px, py):
        if (px + py * 2) % 5 == 0 or (px * 3 + py) % 11 == 0:
            return YELLOW
        return None

    def girdle(px, py):
        n = (px * 13 + py * 7) % 17
        if n <= 5:
            return LIGHT_GREEN
        if n == 7:
            return YELLOW
        if n == 8:
            return RED
        return None

    look = dict(
        sleeve_b=BROWN,
        sleeve_f=BROWN,
        hose=BROWN,
        boot=WHITE,
        boot_top=0.88,
        tunic=BROWN,
        skirt=GREEN,
        belt=YELLOW,
        collar=BROWN,
        skirt_pattern=girdle,
        pattern=fur,
        face='old',
        hair=BROWN,
        beard=BROWN,
        hat=('wreath', LIGHT_GREEN, YELLOW, GREEN),
    )
    arms = (((23, 26), (15, 36), (18, 46), 'open'), ((36, 26), (45, 34), (50, 27), 'grip'))
    legs = (((26, 52), (22, 68), (19, 84), (14, 87)), ((34, 52), (39, 68), (41, 84), (46, 87)))

    def club(rr):
        rr.part().chain([(49, 32), (53, 19), (56, 8)], [1.4, 2.4, 3.4]).paint(BROWN, outline=DARK_GRAY)
        for kx, ky in ((52, 21), (54, 16), (55, 12), (56, 7), (57, 9)):
            rr.put(kx, ky, YELLOW)

    F.draw_standing(r, look, arms, legs, back_props=club, pose=dict(hem=60, flare=7))


# Cupid facing left: golden curls, cyan-shaded white wings, outstretched bow
# arm and fluttering crimson sash. Drawn in fill colours first and outlined
# once; the bow, string and one-pixel arrow go on afterwards so `silhouette`
# does not thicken the arrow into a three-pixel grey bar.
CUPID_BODY = [
    '.......eee6e.......',
    '......e6eeee6......',
    '......ee0efec......',
    '.......eefff..bbb..',
    '......fffffffbfffb.',
    '.fffffffffffbfff3b.',
    '......fff7fffbff3b.',
    '.......fffffffbbb..',
    '.......ffffcccc....',
    '.......cc4ccc.cc...',
    '.......ffffff..c...',
    '......fff..fff.....',
    '......fff..fff.....',
    '......ff....ff.....',
    '.....fff....fff....',
    '....fff......fff...',
]


def draw_cupid(c, x=44):
    """A winged cupid facing left, drawing his bow at the heart on the post."""
    r = Rig(c, thin=True)
    eye = CUPID_BODY[2].index('0')
    top = 70
    r.sprite(CUPID_BODY, x - eye, top)
    r.silhouette()

    # Recurve wooden bow, taut bowstring, and crisp 1px heart-tipped arrow.
    for dx, dy, col in (
        (-6, 0, BROWN),
        (-7, 1, BROWN),
        (-8, 2, BROWN),
        (-8, 3, YELLOW),
        (-9, 4, BROWN),
        (-9, 5, YELLOW),
        (-9, 6, BROWN),
        (-9, 7, YELLOW),
        (-9, 8, BROWN),
        (-8, 9, YELLOW),
        (-8, 10, BROWN),
        (-7, 11, BROWN),
        (-6, 12, BROWN),
    ):
        c.put(x + dx, top + dy, col)
    c.line(x - 6, top + 1, x - 3, top + 6, LIGHT_GRAY)
    c.line(x - 3, top + 6, x - 6, top + 11, LIGHT_GRAY)
    c.line(x - 16, top + 6, x - 3, top + 6, BROWN)
    c.put(x - 4, top + 5, LIGHT_RED)
    c.put(x - 4, top + 7, LIGHT_RED)
    for dx, dy, col in ((-17, 6, RED), (-16, 5, RED), (-16, 7, RED), (-18, 6, DARK_GRAY)):
        c.put(x + dx, top + dy, col)
