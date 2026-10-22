"""Small people for the number-card vignettes, drawn with the court-figure rig.

They use the same jointed poses as the courts, scaled down to the room left
under the pips and painted on a thin rig: one dark silhouette outline instead
of an outline per part, which would swallow limbs two pixels wide.
"""

from scripts.deck_gen import figure as F
from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_CYAN,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.rig import Rig


def _rig(c, scale, x, flip=False):
    """A thin rig whose figure stands centred on card column `x`."""
    return Rig(c, flip=flip, dx=x - 30, scale=scale, thin=True)


def draw_forester(c, x=22, scale=0.34):
    """A forester in a long green coat, pipe in his mouth, leaning on a staff."""
    r = _rig(c, scale, x)
    look = dict(
        sleeve_b=GREEN,
        sleeve_f=GREEN,
        cuff=LIGHT_GREEN,
        hose=BROWN,
        boot=BROWN,
        tunic=GREEN,
        skirt=GREEN,
        belt=BROWN,
        buttons=YELLOW,
        face='beard',
        hair=BROWN,
        hat=('brim', GREEN, LIGHT_RED, BROWN),
    )
    arms = (((23, 26), (17, 35), (23, 44), 'open'), ((36, 26), (42, 37), (47, 43), 'grip'))
    legs = (((27, 52), (26, 68), (25, 84), (30, 87)), ((33, 52), (36, 68), (38, 84), (44, 87)))

    def staff(rr):
        F.pole(rr, (49, 86), (46, 14), BROWN)

    def pipe(rr):
        rr.line(36, 19, 41, 25, BROWN)
        rr.part().rect(40, 23, 43, 27).fill(BROWN)

    F.draw_standing(r, look, arms, legs, back_props=staff, front_props=pipe, pose=dict(hem=64, flare=10))
    r.silhouette()
    # Smoke curling from the pipe bowl.
    for k, (sx, sy) in enumerate(((1, -2), (0, -4), (1, -6))):
        px, py = r.tx(42, 23)
        c.put(px + sx, py + sy, 7 if k else WHITE)


def draw_hornblower(c, x=19, scale=0.42):
    """A huntsman sitting in the grass, leaning back on one arm and blowing a long horn."""
    r = _rig(c, scale, x)
    hose, boot = YELLOW, BROWN
    # Legs stretched out along the ground, the near knee drawn up.
    F.leg(r, (30, 78), (44, 80), (58, 82), (61, 78), hose, boot, boot_top=0.3)
    F.leg(r, (33, 79), (44, 68), (52, 82), (58, 80), hose, boot, boot_top=0.45)
    # Back arm propping him up on the grass.
    F.arm(r, (20, 52), (14, 64), (12, 78), LIGHT_RED)
    F.draw_hand(r, 12, 80)
    j = dict(head=(27, 38), neck=(26, 44), sh_b=(20, 49), sh_f=(31, 49), waist=(28, 70), hem=80, flare=9, lean=3)
    F.torso(r, j, LIGHT_RED, LIGHT_RED, GREEN, buttons=YELLOW)
    F.draw_head(r, 27, 38, hair=BROWN, hat=('cap', GREEN, LIGHT_RED, YELLOW))
    # The horn: mouthpiece at the lips, bell raised to the right.
    horn = r.part().chain([(33, 41), (44, 37), (56, 30)], [1.2, 1.6, 2.2]).ellipse(58, 29, 3.2, 3.8, angle=-30)
    horn.paint(YELLOW)
    r.part().ellipse(59, 28, 1.6, 2.4, angle=-30).fill(BROWN)
    F.arm(r, (31, 49), (40, 51), (43, 39), LIGHT_RED)
    F.draw_hand(r, 43, 39, grip=True)
    r.silhouette()


def draw_sword_dancer(c, x=30, scale=0.32):
    """A jester in parti-coloured motley dancing on one foot, brandishing a sword."""
    r = _rig(c, scale, x)

    def motley(x, y):
        fx, _ = r.tx(30, 0)
        return LIGHT_RED if x < fx else None

    look = dict(
        sleeve_b=LIGHT_RED,
        sleeve_f=YELLOW,
        cuff=GREEN,
        hose=YELLOW,
        boot=GREEN,
        tunic=YELLOW,
        skirt=YELLOW,
        belt=GREEN,
        pattern=motley,
        skirt_pattern=motley,
        hair=YELLOW,
        hat=('jester', LIGHT_RED, YELLOW, GREEN),
    )
    arms = (((23, 26), (14, 30), (6, 26), 'open'), ((36, 26), (43, 22), (49, 16), 'grip'))
    # Standing on the back leg, the front knee lifted high.
    legs = (((27, 52), (27, 68), (28, 84), (33, 87)), ((33, 52), (44, 58), (40, 72), (45, 74)))

    def blade(rr):
        F.sword(rr, (49, 16), (68, 6))

    F.draw_standing(r, look, arms, legs, front_props=blade)
    r.silhouette()


def _musician(c, x, scale, flip, look, arms, legs, prop):
    r = _rig(c, scale, x, flip)
    F.draw_standing(r, look, arms, legs, front_props=prop)
    r.silhouette()


def draw_musicians(c):
    """A village band: a trumpeter, a drummer and a fiddler."""
    s = 0.24
    stand = (((27, 52), (25, 68), (24, 84), (29, 87)), ((33, 52), (37, 68), (38, 84), (44, 87)))

    def trumpet(r):
        r.part().chain([(36, 19), (48, 12), (54, 8)], [1.0, 1.2, 1.4]).ellipse(57, 6, 3, 3.6, angle=-35).paint(YELLOW)
        r.part().capsule(42, 15, 50, 4, 1.2).paint(LIGHT_RED, None)

    _musician(
        c,
        13,
        s,
        False,
        dict(sleeve_b=LIGHT_RED, sleeve_f=LIGHT_RED, hose=BLUE, boot=BROWN, tunic=LIGHT_RED, skirt=LIGHT_RED,
             belt=YELLOW, hair=BROWN, hat=('cap', GREEN, WHITE, YELLOW)),
        (((23, 26), (30, 34), (38, 24), 'grip'), ((36, 26), (43, 28), (46, 14), 'grip')),
        stand,
        trumpet,
    )

    def drum(r):
        d = r.part().ellipse(42, 50, 8, 3).rect(34, 50, 50, 62).ellipse(42, 62, 8, 2.5)
        d.paint(YELLOW, pattern=lambda x, y: RED if (x + y) % 4 == 0 else None)
        r.part().ellipse(42, 49, 7.5, 2.4).fill(WHITE)
        F.pole(r, (40, 34), (44, 46))
        F.pole(r, (48, 34), (45, 46))

    _musician(
        c,
        30,
        s,
        False,
        dict(sleeve_b=GREEN, sleeve_f=GREEN, hose=YELLOW, boot=BROWN, tunic=GREEN, skirt=GREEN, belt=LIGHT_RED,
             face='beard', hair=BROWN, hat=('brim', LIGHT_RED, YELLOW, GREEN)),
        (((23, 26), (30, 36), (40, 34), 'grip'), ((36, 26), (44, 32), (48, 34), 'grip')),
        stand,
        drum,
    )

    def fiddle(r):
        r.part().ellipse(39, 30, 3.5, 5, angle=-60).paint(BROWN, None)
        r.line(32, 26, 47, 34, BROWN)
        r.line(30, 34, 50, 20, WHITE)

    _musician(
        c,
        47,
        s,
        True,
        dict(sleeve_b=CYAN, sleeve_f=CYAN, hose=LIGHT_RED, boot=BROWN, tunic=CYAN, skirt=CYAN, belt=YELLOW,
             hair=YELLOW, hat=('beret', BLUE, LIGHT_RED, YELLOW)),
        (((23, 26), (34, 32), (44, 33), 'grip'), ((36, 26), (36, 38), (40, 30), 'grip')),
        stand,
        fiddle,
    )


def draw_wild_man(c, x=28, scale=0.66):
    """The wild man of Czech heraldry: bearded, girdled and crowned with oak, a club on his shoulder."""
    r = Rig(c, dx=x - 30, scale=scale)
    look = dict(
        sleeve_b=WHITE,
        sleeve_f=WHITE,
        hose=WHITE,
        boot=WHITE,
        tunic=WHITE,
        skirt=GREEN,
        belt=BROWN,
        collar=WHITE,
        skirt_pattern=lambda x, y: LIGHT_GREEN if (x * 2 + y) % 5 == 0 else (YELLOW if (x * 3 + y) % 11 == 0 else None),
        # Body hair in short strokes over the chest.
        pattern=lambda x, y: 7 if (x + 2 * y) % 7 == 0 else None,
        face='old',
        hair=BROWN,
        beard=BROWN,
        hat=('wreath', GREEN, YELLOW, GREEN),
    )
    arms = (((23, 26), (15, 36), (18, 46), 'open'), ((36, 26), (45, 34), (50, 27), 'grip'))
    legs = (((26, 52), (22, 68), (19, 84), (14, 87)), ((34, 52), (39, 68), (41, 84), (46, 87)))

    def club(rr):
        rr.part().chain([(49, 32), (54, 16), (58, 2)], [1.4, 2.4, 3.4]).paint(BROWN, outline=DARK_GRAY)
        for kx, ky in ((53, 18), (56, 9), (57, 3)):
            rr.put(kx, ky, YELLOW)

    F.draw_standing(r, look, arms, legs, back_props=club, pose=dict(hem=60, flare=7))


def draw_cupid(c, x=44, scale=0.27):
    """A winged cupid facing left, drawing his bow."""
    r = _rig(c, scale, x, flip=True)
    # Wings behind the shoulders.
    for ang, col in ((-30, WHITE), (-60, LIGHT_CYAN)):
        r.part().ellipse(17, 26, 11, 5, angle=ang).paint(col, None)
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

    def bow(r):
        r.part().chain([(52, 4), (56, 14), (56, 34), (52, 44)], [0.9, 0.9, 0.9, 0.9]).fill(BROWN)
        r.line(52, 4, 42, 26, WHITE)
        r.line(42, 26, 52, 44, WHITE)
        r.line(36, 26, 66, 25, YELLOW)
        r.put(67, 25, LIGHT_CYAN)
        r.put(66, 24, LIGHT_CYAN)

    F.draw_standing(r, look, arms, legs, front_props=bow, pose=dict(hem=50, flare=6))
    r.silhouette()
