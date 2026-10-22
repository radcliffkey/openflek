"""Animals for the number-card vignettes, built from rig shapes.

Each animal is posed facing right with its feet on the turf at y=86 and
spans roughly x=10..50; `flip` mirrors it and `dx` shifts it. Body, neck and
head share one outline so the silhouette reads as a single animal; the near
legs get their own outline, and the far legs are drawn first in the shade
colour to give the body depth.
"""

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
from scripts.deck_gen.rig import Rig, darker


def _legs(r, legs, col, upper=2.2, lower=1.2, hoof=None, outline=None):
    """Jointed legs, each a list of points from the body down to the foot."""
    for pts in legs:
        radii = [upper] + [lower] * (len(pts) - 1)
        if len(pts) > 2:
            radii[1] = (upper + lower) / 2 + 0.2
        p = r.part().chain(pts, radii)
        p.paint(col, outline=outline if outline is not None else darker(col))
        if hoof is not None:
            r.put(*pts[-1], hoof)
            r.put(pts[-1][0] + 1, pts[-1][1], hoof)


def _eye(r, x, y, col=BLACK):
    r.put(x, y, col)


def draw_horse(c, flip=False, dx=0, scale=1.0, coat=LIGHT_GRAY, mane=DARK_GRAY, cloth=LIGHT_RED):
    """A saddled dapple-grey horse standing at rest, one hind hoof cocked."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    far = darker(coat)
    _legs(r, [[(36, 72), (35, 79), (36, 85)], [(24, 71), (27, 77), (24, 80), (25, 85)]], far, hoof=DARK_GRAY)
    r.part().chain([(17, 66), (14, 71), (14, 79)], [1.8, 1.8, 1.2]).paint(mane)
    body = r.part().ellipse(29, 69, 11, 5.5).ellipse(38, 69, 5, 5.5).ellipse(21, 68, 5.5, 5.5)
    body.capsule(38, 67, 43, 58, 3.6, 2.6)
    body.capsule(43, 57, 49, 62, 2.5, 1.7)
    body.paint(coat, outline=DARK_GRAY, pattern=lambda x, y: WHITE if (x * 3 + y * 5) % 11 == 0 else None)
    r.part().chain([(40, 55), (37, 60), (36, 65)], [1.3, 1.6, 1.0]).paint(mane)
    r.part().poly([(42, 52), (44, 56), (41, 56)]).paint(coat, outline=DARK_GRAY)
    _eye(r, 45, 58)
    r.put(49, 62, DARK_GRAY)
    # Bridle, saddle cloth and saddle.
    r.line(43, 59, 48, 61, BROWN)
    r.line(45, 58, 45, 62, BROWN)
    r.part().poly([(24, 64), (34, 64), (33, 73), (25, 73)]).paint(cloth, pattern=lambda x, y: YELLOW if y % 4 == 0 else None)
    r.part().ellipse(29, 64, 5, 1.8).paint(BROWN)
    r.line(29, 66, 29, 76, BROWN)
    _legs(r, [[(39, 72), (40, 79), (40, 85)], [(21, 71), (22, 77), (18, 80), (19, 85)]], coat, outline=DARK_GRAY, hoof=DARK_GRAY)
    return r


def draw_hound(c, flip=False, dx=0, scale=1.0, coat=WHITE, spots=LIGHT_GRAY, collar=RED):
    """A lean coursing hound in full gallop: forelegs reaching, hind legs driving."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    far = darker(coat)
    _legs(r, [[(37, 74), (43, 77), (48, 79)], [(20, 73), (14, 76), (9, 80)]], far, upper=1.8, lower=1.0)
    r.part().chain([(17, 71), (12, 67), (8, 66)], [1.2, 0.9, 0.6]).paint(coat, outline=DARK_GRAY)
    body = r.part().ellipse(29, 72, 10, 3.6, angle=-4).ellipse(37, 72, 4.2, 4.6).ellipse(20, 71, 4, 3.6)
    body.capsule(38, 70, 42, 65, 2.4, 2.0)
    body.ellipse(44, 64, 3, 2.4).capsule(45, 64, 51, 66, 1.8, 1.0)

    def coat_spots(x, y):
        fx, _ = r.tx(29, 0)
        return spots if ((x - fx) // 4 + y // 3) % 3 == 0 and y < 74 else None

    body.paint(coat, outline=DARK_GRAY, pattern=coat_spots)
    r.part().poly([(41, 62), (44, 61), (42, 66)]).paint(spots, outline=DARK_GRAY)
    _eye(r, 45, 63)
    r.put(51, 66, BLACK)
    r.part().capsule(39, 66, 41, 69, 1.0).fill(collar)
    _legs(r, [[(39, 74), (46, 75), (52, 73)], [(19, 74), (16, 79), (11, 83)]], coat, upper=1.9, lower=1.0, outline=DARK_GRAY)
    return r


def draw_dog(c, flip=False, dx=0, scale=1.0, coat=WHITE, patch=BROWN):
    """A small spaniel standing alert, tail up."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    _legs(r, [[(43, 81), (43, 86)], [(36, 81), (35, 86)]], LIGHT_GRAY, upper=1.3, lower=1.0)
    r.part().chain([(34, 78), (32, 74), (33, 71)], [1.0, 0.9, 0.6]).paint(coat, outline=DARK_GRAY)
    body = r.part().ellipse(40, 79, 6, 3).capsule(44, 78, 46, 74, 2.0).ellipse(47, 73, 2.4, 2.2).capsule(48, 74, 51, 75, 1.2)
    body.paint(coat, outline=DARK_GRAY, pattern=lambda x, y: patch if y < 79 and (x + y) % 5 < 2 else None)
    r.part().ellipse(46, 75, 1.2, 2.2).paint(patch, outline=DARK_GRAY)
    _eye(r, 48, 72)
    r.put(51, 75, BLACK)
    _legs(r, [[(44, 81), (45, 86)], [(37, 81), (37, 86)]], coat, upper=1.3, lower=1.0, outline=DARK_GRAY)
    return r


def draw_boar(c, flip=False, dx=0, scale=1.0):
    """A wild boar trotting, head low, bristled crest and white tusks."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    hide = BROWN
    far = RED
    _legs(r, [[(36, 76), (38, 81), (38, 86)], [(19, 76), (17, 81), (18, 86)]], far, upper=2.4, lower=1.5, outline=DARK_GRAY)
    r.part().chain([(13, 70), (10, 72), (11, 75)], [1.0, 0.8, 0.6]).paint(hide, outline=DARK_GRAY)
    # Body rising to a heavy hump over the shoulders, rump lower.
    body = r.part().ellipse(25, 72, 12, 6.5, angle=-6).ellipse(35, 70, 7.5, 7.5)
    body.paint(hide, shade=DARK_GRAY, outline=DARK_GRAY, pattern=lambda x, y: DARK_GRAY if (x * 3 + y * 7) % 11 == 0 else None)
    # Crest of bristles along the spine.
    for k in range(10):
        x = 16 + k * 2.5
        y = 66.5 - k * 0.45
        r.line(x, y, x - 1.5, y - 2.5, DARK_GRAY)
    # Wedge-shaped head with its own outline so the jaw shows against the shoulder.
    head = r.part().poly([(38, 64), (43, 65), (51, 73), (51, 78), (46, 79), (39, 75)])
    head.paint(hide, shade=DARK_GRAY, outline=DARK_GRAY)
    r.part().poly([(39, 62), (43, 63), (41, 67)]).paint(hide, outline=DARK_GRAY)
    _eye(r, 44, 69, BLACK)
    r.put(45, 68, LIGHT_RED)
    r.part().ellipse(51, 75.5, 1.2, 2.2).paint(LIGHT_RED, None, outline=DARK_GRAY)
    r.part().chain([(46, 77), (48, 75), (48, 72)], [0.8, 0.7, 0.5]).fill(WHITE)
    _legs(r, [[(40, 76), (41, 81), (42, 86)], [(23, 76), (22, 81), (23, 86)]], hide, upper=2.6, lower=1.6, outline=DARK_GRAY, hoof=BLACK)
    return r


def draw_stag(c, flip=False, dx=0, scale=1.0):
    """A red stag leaping, forelegs tucked and hind legs stretched behind, antlers swept back."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    hide = BROWN
    belly = YELLOW
    _legs(r, [[(36, 70), (40, 74), (37, 77)], [(20, 71), (14, 75), (7, 79)]], darker(hide), upper=2.0, lower=1.0)
    body = r.part().ellipse(28, 69, 10.5, 4.5, angle=-10).ellipse(36, 67, 4.5, 4.8).ellipse(20, 70, 4.5, 4.5)
    body.capsule(37, 65, 41, 58, 2.8, 2.0).ellipse(43, 56, 2.6, 2.2).capsule(44, 57, 48, 59, 1.6, 1.0)

    def belly_patch(x, y):
        _, by = r.tx(0, 72)
        return belly if y >= by - 1 else None

    body.paint(hide, shade=DARK_GRAY, outline=DARK_GRAY, pattern=belly_patch)
    # White rump patch and a flick of tail.
    r.part().ellipse(17, 69, 2.0, 2.2).paint(WHITE, outline=None)
    r.part().poly([(41, 53), (43, 54), (40, 56)]).paint(hide, outline=DARK_GRAY)
    _eye(r, 44, 56)
    r.put(48, 59, BLACK)
    # Antlers: two beams swept back with tines.
    for bx in (42, 44):
        pts = [(bx, 54), (bx - 2, 50), (bx - 4, 46), (bx - 7, 43)]
        for i in range(len(pts) - 1):
            r.line(*pts[i], *pts[i + 1], YELLOW if bx == 44 else BROWN)
        for tx, ty in pts[1:]:
            r.line(tx, ty, tx + 2, ty - 2, YELLOW if bx == 44 else BROWN)
    _legs(r, [[(38, 71), (43, 73), (41, 77)], [(19, 72), (12, 74), (5, 76)]], hide, upper=2.1, lower=1.0, outline=DARK_GRAY, hoof=BLACK)
    return r


def draw_elephant(c, flip=False, dx=0, scale=1.0):
    """An elephant walking, trunk curled down, tusk and a fan-shaped ear."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    hide = LIGHT_GRAY
    _legs(r, [[(37, 75), (37, 86)], [(19, 75), (21, 86)]], DARK_GRAY, upper=3.2, lower=2.8)
    r.part().chain([(12, 68), (9, 72), (9, 76)], [0.9, 0.7, 0.6]).paint(hide, outline=DARK_GRAY)
    body = r.part().ellipse(26, 70, 14, 9).ellipse(40, 66, 7, 7.5)
    body.chain([(45, 68), (48, 74), (48, 80), (46, 84)], [3.0, 2.2, 1.6, 1.3])
    body.paint(hide, shade=DARK_GRAY, outline=DARK_GRAY, pattern=lambda x, y: WHITE if (x + 2 * y) % 9 == 0 and y < 68 else None)
    r.part().ellipse(36, 67, 4.5, 6.5, angle=-10).paint(hide, shade=DARK_GRAY, outline=DARK_GRAY)
    _eye(r, 43, 64)
    r.part().chain([(44, 71), (48, 73), (50, 71)], [1.2, 0.9, 0.6]).paint(WHITE, None, outline=LIGHT_GRAY)
    # Saddle blanket of a royal menagerie elephant.
    r.part().poly([(19, 61), (31, 61), (30, 72), (20, 72)]).paint(LIGHT_RED, pattern=lambda x, y: YELLOW if y % 3 == 0 else None)
    _legs(r, [[(33, 75), (34, 86)], [(16, 75), (16, 86)]], hide, upper=3.4, lower=3.0, outline=DARK_GRAY)
    for fx in (34, 16):
        r.line(fx - 2, 85, fx + 2, 85, WHITE)
    return r


def draw_lion(c, flip=False, dx=0, scale=1.0):
    """A lion couchant: lying with forepaws stretched out, head raised, tail curled over the haunch."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    hide = YELLOW
    mane = BROWN
    r.part().chain([(12, 80), (8, 76), (11, 71), (15, 70)], [1.1, 1.0, 0.9, 0.8]).paint(hide)
    r.part().ellipse(16, 70, 1.8, 1.8).paint(mane)
    body = r.part().ellipse(27, 80, 13, 5).ellipse(16, 78, 6, 6.5)
    body.chain([(36, 83), (44, 84), (50, 84)], [2.2, 1.8, 1.6])
    body.paint(hide, outline=BROWN)
    m = r.part().ellipse(37, 74, 7, 8.5)
    for k in range(8):
        a = math.radians(100 + k * 25)
        m.ellipse(37 + math.cos(a) * 7, 74 + math.sin(a) * 8, 1.8, 1.8)
    m.paint(mane, outline=DARK_GRAY, pattern=lambda x, y: RED if (x - y) % 4 == 0 else None)
    head = r.part().ellipse(41, 74, 3.8, 4.2).capsule(43, 76, 46, 77, 2.2, 1.6)
    head.paint(hide, outline=BROWN)
    r.line(40, 71, 42, 71, BROWN)
    _eye(r, 42, 72)
    r.put(46, 76, BLACK)
    r.put(44, 79, RED)
    r.put(45, 79, RED)
    for x in (47, 49, 51):
        r.put(x, 85, BROWN)
    r.part().ellipse(17, 82, 4, 2.2).paint(hide, outline=BROWN)
    return r


def draw_pheasant(c, flip=False, dx=0, scale=1.0):
    """A cock pheasant on a bough: copper body, green head, red wattle, long barred tail."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    r.part().capsule(12, 84, 50, 82, 1.8, 1.4).paint(BROWN, outline=DARK_GRAY)
    r.part().chain([(28, 74), (17, 70), (6, 66)], [2.8, 2.0, 0.8]).paint(YELLOW, pattern=lambda x, y: BROWN if x % 3 == 0 else None)
    body = r.part().ellipse(33, 76, 7, 5, angle=-15).capsule(37, 73, 41, 67, 2.6, 2.0)
    body.paint(BROWN, shade=RED, outline=DARK_GRAY, pattern=lambda x, y: YELLOW if (x + y) % 4 == 0 else None)
    r.part().ellipse(31, 75, 5, 3, angle=-15).paint(YELLOW, pattern=lambda x, y: BROWN if (x * 2 + y) % 5 == 0 else None)
    r.part().ellipse(42, 65, 2.6, 2.4).capsule(43, 65, 46, 66, 1.0, 0.5).paint(GREEN, outline=DARK_GRAY)
    r.part().ellipse(43, 64, 1.2, 1.4).fill(LIGHT_RED)
    r.put(43, 64, BLACK)
    r.put(46, 66, YELLOW)
    r.part().rect(39, 69, 42, 70).paint(WHITE, None, outline=None)
    for fx in (32, 36):
        r.line(fx, 80, fx + 1, 83, YELLOW)
    return r


def draw_peacock(c, flip=False, dx=0, scale=1.0):
    """A peacock in display, the train fanned behind it with eyed feathers."""
    r = Rig(c, flip=flip, dx=dx, scale=scale)
    fan = r.part().ellipse(26, 76, 15, 11).clip(y1=int(r.tx(0, 80)[1]))
    fan.paint(GREEN, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GREEN if (x + y) % 3 == 0 else None)
    for k in range(9):
        a = math.radians(200 + k * 17.5)
        ex, ey = 26 + math.cos(a) * 11.5, 76 + math.sin(a) * 8.5
        r.part().ellipse(ex, ey, 1.8, 1.8).paint(YELLOW, None, outline=BLUE)
        r.put(ex, ey, BLUE)
    for k in range(5):
        a = math.radians(215 + k * 27)
        ex, ey = 26 + math.cos(a) * 6.5, 76 + math.sin(a) * 4.5
        r.part().ellipse(ex, ey, 1.4, 1.4).paint(LIGHT_CYAN, None, outline=BLUE)
    body = r.part().ellipse(30, 80, 4, 4.5).capsule(31, 77, 34, 68, 1.8, 1.3).ellipse(34, 67, 1.8, 1.6)
    body.paint(BLUE, shade=DARK_GRAY, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_BLUE if (x + y) % 3 == 0 else None)
    r.put(36, 67, YELLOW)
    r.put(34, 66, WHITE)
    for k in (-1, 0, 1):
        r.line(34, 65, 34 + k * 2, 62, CYAN)
        r.put(34 + k * 2, 62, LIGHT_CYAN)
    r.line(29, 84, 28, 87, BROWN)
    r.line(32, 84, 33, 87, BROWN)
    return r
