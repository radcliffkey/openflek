"""Animals for the number-card vignettes, built from rig shapes.

Each animal is posed facing right with its feet on the turf at y=86 and
spans roughly x=10..50; `flip` mirrors it and `dx` shifts it. Body, neck and
head share one outline so the silhouette reads as a single animal; the near
legs get their own outline, and the far legs are drawn first in the shade
colour to give the body depth. The pheasant and boar are drawn at full scale
in card coordinates with hand-pixelled heads, and the small hound is pixelled
whole, where scaled shapes lost their features.
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
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.rig import Rig, darker


# Below this scale an animal is drawn on a thin rig, with one outline around
# its silhouette instead of one per part, which would swallow its legs.
THIN_SCALE = 0.75


def _rig(c, flip, dx, scale, shadow=None, dy=0, thin=None):
    """Starts an animal; `shadow` is (centre x, half length) of its shadow on the turf, in pose coordinates.

    `thin` defaults to drawing small animals with one silhouette outline;
    pass True for one that needs it at any size.
    """
    if thin is None:
        thin = scale < THIN_SCALE
    r = Rig(c, flip=flip, dx=dx, dy=dy, scale=scale, thin=thin)
    if shadow is not None:
        _ground_shadow(r, *shadow)
    return r


def _done(r, feet=()):
    """Finishes an animal: on a thin rig, outlines its whole silhouette; grass then grows over `feet`."""
    if r.thin:
        r.silhouette()
    for fx, fy in feet:
        x, y = r.tx(fx, fy)
        for k in (-2, 0, 2):
            r.c.put(x + k, y, GREEN)
            r.c.put(x + k + 1, y - 1, LIGHT_GREEN)
    return r


def _ground_shadow(r, cx, half, gy=87):
    """A flat dithered shadow on the ground under an animal so it doesn't float on the turf.

    Drawn straight on the card, outside the rig, so a thin rig's silhouette
    doesn't outline it. It stays on the ground when the animal is raised
    with `dy`, as for a leap.
    """
    x0, y0 = r.tx(cx, gy)
    y0 -= r.dy
    rx, ry = max(half * r.s, 2.0), 1.9
    for y in range(int(y0 - ry), int(y0 + ry) + 2):
        for x in range(int(x0 - rx), int(x0 + rx) + 2):
            d = ((x - x0) / rx) ** 2 + ((y - y0) / ry) ** 2
            # A solid core fading to a dithered rim.
            if d <= 0.45 or (d <= 1 and (x + y) % 2):
                r.c.put(x, y, DARK_GRAY)


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
    """A saddled dapple-grey horse standing at rest, one hind hoof cocked.

    The horse is painted on a thin rig and outlined once as a silhouette: an
    outline per part turns its slim legs and belly into solid dark grey.
    The tack goes on afterwards with its own outlines.
    """
    r = _rig(c, flip, dx, scale, shadow=(29, 14), thin=True)
    far = darker(coat)
    _legs(r, [[(36, 72), (35, 79), (36, 85)], [(24, 71), (27, 77), (24, 80), (25, 85)]], far, hoof=DARK_GRAY)
    r.part().chain([(17, 66), (14, 71), (14, 79)], [1.8, 1.8, 1.2]).paint(mane)
    body = r.part().ellipse(29, 69, 11, 5.5).ellipse(38, 69, 5, 5.5).ellipse(21, 68, 5.5, 5.5)
    body.capsule(38, 67, 43, 58, 3.6, 2.6)
    body.capsule(43, 57, 49, 62, 2.5, 1.7)
    body.paint(coat, pattern=lambda x, y: WHITE if (x * 3 + y * 5) % 11 == 0 else None)
    r.part().chain([(40, 55), (37, 60), (36, 65)], [1.3, 1.6, 1.0]).paint(mane)
    r.part().poly([(42, 52), (44, 56), (41, 56)]).paint(coat)
    _legs(r, [[(39, 72), (40, 79), (40, 85)], [(21, 71), (22, 77), (18, 80), (19, 85)]], coat, hoof=DARK_GRAY)
    _done(r, feet=[(36, 86), (25, 86), (40, 86), (19, 86)])
    # Bridle, then the eye just in front of the cheek strap, saddle cloth and saddle.
    tack = Rig(c, flip=flip, dx=dx, scale=scale)
    tack.put(49, 62, DARK_GRAY)
    tack.line(43, 59, 48, 61, BROWN)
    tack.line(45, 58, 45, 62, BROWN)
    _eye(tack, 46.5, 57.5)
    tack.part().poly([(24, 64), (34, 64), (33, 73), (25, 73)]).paint(cloth, pattern=lambda x, y: YELLOW if y % 4 == 0 else None)
    tack.part().ellipse(29, 64, 5, 1.8).paint(BROWN)
    tack.line(29, 66, 29, 76, BROWN)
    return r


def draw_hound(c, flip=False, dx=0, scale=1.0, coat=WHITE, spots=LIGHT_GRAY, collar=RED):
    """A lean coursing hound in full gallop: forelegs reaching, hind legs driving.

    A white coat on the white card needs an unbroken outline, so the tail,
    body, head and far legs are painted on a thin rig and outlined once as a
    silhouette; the near legs then go on top with their own outline, which
    parts them from the belly.
    """
    r = _rig(c, flip, dx, scale, shadow=(30, 15), thin=True)
    _legs(r, [[(36, 73), (43, 77), (49, 78)], [(20, 72), (14, 76), (8, 79)]], darker(coat), upper=2.2, lower=1.2)
    r.part().chain([(17, 70), (12, 67), (7, 67)], [1.2, 0.9, 0.6]).paint(coat, None)
    # Deep chest, tucked waist and a long narrow head.
    body = r.part().ellipse(29, 71, 9.5, 3.2, angle=-4).ellipse(37, 71, 4.6, 5.0).ellipse(20, 70, 4.4, 3.9)
    body.capsule(38, 69, 42, 64, 2.6, 2.1)
    body.ellipse(44, 63, 3.2, 2.6).capsule(45, 63, 52, 65.5, 2.0, 1.1)
    # One grey saddle patch rather than a scatter of spots, which reads as dirt.
    sx, sy = r.tx(26, 68)

    def saddle(x, y):
        return spots if ((x - sx) / 5.5) ** 2 + ((y - sy) / 2.2) ** 2 <= 1 else None

    body.paint(coat, None, pattern=saddle)
    r.part().poly([(41, 61), (44, 60), (42.5, 65)]).paint(spots, None)
    _eye(r, 45.5, 62)
    r.put(52, 65.5, BLACK)
    r.part().capsule(39, 65, 41, 68.5, 1.1).fill(collar)
    _done(r)
    near = Rig(c, flip=flip, dx=dx, scale=scale)
    _legs(near, [[(39, 74), (46, 76), (53, 74)], [(19, 73), (13, 78), (8, 82)]], coat, upper=2.4, lower=1.4, outline=DARK_GRAY)
    return r


# A white hound with a liver head, ear and saddle, red collar, tail up
# (20x15, facing right). Fill colours only: at this size shapes painted with
# outlines leave a white dog as nothing but grey lines, so it is pixelled by
# hand and gets one silhouette outline.
DOG = [
    '.............666....',
    '............66606...',
    '..6.........66666ff0',
    '...6........6666fff.',
    '...6........666cf...',
    '....f.......6fcff...',
    '....fff66666fffff...',
    '....fff666666ffff...',
    '....ffff66666fff....',
    '....fffffffffff7....',
    '.....f7.......f7....',
    '.....f7.......f7....',
    '.....f7.......f7....',
    '.....f7.......f7....',
    '....ff7......ff77...',
]


def draw_dog(c, flip=False, dx=0):
    """A hound standing alert, tail up, in the box x=34..53 with its paws on row 86; `flip` turns it round in place."""
    r = Rig(c, flip=flip, axis=43.5, dx=dx, thin=True)
    r.sprite(DOG, 34, 72)
    return _done(r)


def draw_boar(c, flip=False, dx=0, scale=1.0):
    """A wild boar trotting, head low, bristled crest and white tusks.

    Posed in card coordinates at full scale, so every part keeps its own
    outline, and low enough that the crest stays under the Ten's lowest pips.
    """
    r = _rig(c, flip, dx, scale)
    hide = BROWN
    # Far legs in shadow, then the tail with its tuft.
    _legs(r, [[(36, 80), (36, 86)], [(25, 80), (25, 86)]], RED, upper=1.5, lower=1.5, outline=DARK_GRAY, hoof=BLACK)
    r.line(17, 76, 14, 78, DARK_GRAY)
    r.line(14, 78, 14, 80, DARK_GRAY)
    r.put(13, 81, DARK_GRAY)
    r.put(15, 81, DARK_GRAY)
    # Body rising to a heavy hump over the shoulders, rump lower, flecked with dark bristles.
    body = r.part().ellipse(26, 78.5, 10, 3.8).ellipse(34, 76.5, 7, 5.0)
    body.paint(hide, shade=None, outline=DARK_GRAY, pattern=lambda x, y: DARK_GRAY if (x * 3 + y * 5) % 13 == 0 and y > 74 else None)
    # A crest of bristles along the spine, rising over the shoulders.
    for x, y in ((21, 73), (24, 72), (27, 72), (30, 71), (33, 71), (36, 71)):
        r.put(x, y, DARK_GRAY)
        r.put(x + 1, y + 1, DARK_GRAY)
    # Head in profile, hand-pixelled: pointed ear, small eye under a brow, the
    # snout running down to a pink disc and a white tusk curling up from the jaw.
    r.sprite(
        [
            '..88..........',
            '.8e68.........',
            '.8e6688.......',
            '.6666668......',
            '.68666668.....',
            '.666066668....',
            '.6666666668...',
            '.66666666668..',
            '.666666666688.',
            '.6666666f68c8.',
            '.666666ff68c8.',
            '.8666668888888',
            '..88888.......',
        ],
        38,
        71,
    )
    # Near legs, black hooves.
    _legs(r, [[(40, 80), (40, 86)], [(20, 80), (20, 86)]], hide, upper=1.5, lower=1.5, outline=DARK_GRAY, hoof=BLACK)
    return _done(r, feet=[(36, 87), (26, 87), (41, 87), (20, 87)])


def draw_stag(c, flip=False, dx=0, dy=0, scale=1.0):
    """A red stag leaping, forelegs reaching forward and hind legs stretched behind, antlers swept back.

    Forelegs folded under the chest, as a real stag jumps, shrink to stubs at
    this card's scale, so they reach out ahead instead.
    """
    r = _rig(c, flip, dx, scale, shadow=(28, 13), dy=dy)
    hide = BROWN
    belly = YELLOW
    _legs(r, [[(36, 71), (42, 75), (46, 79)], [(20, 71), (14, 75), (7, 79)]], darker(hide), upper=2.0, lower=1.2)
    body = r.part().ellipse(28, 69, 10.5, 4.5, angle=-10).ellipse(36, 67, 4.5, 4.8).ellipse(20, 70, 4.5, 4.5)
    body.capsule(37, 65, 42, 60, 2.8, 2.0).ellipse(45, 59, 2.6, 2.2).capsule(46, 60, 50, 62, 1.6, 1.0)

    def belly_patch(x, y):
        _, by = r.tx(0, 72)
        return belly if y >= by - 1 else None

    body.paint(hide, shade=DARK_GRAY, outline=DARK_GRAY, pattern=belly_patch)
    # White rump patch and a flick of tail.
    r.part().ellipse(17, 69, 2.0, 2.2).paint(WHITE, outline=None)
    r.part().poly([(42, 56), (44, 57), (41, 59)]).paint(hide, outline=DARK_GRAY)
    _eye(r, 46, 59)
    r.put(50, 62, BLACK)
    _legs(r, [[(38, 71), (45, 72), (51, 75)], [(19, 72), (12, 74), (5, 76)]], hide, upper=2.1, lower=1.2, outline=DARK_GRAY, hoof=BLACK)
    _done(r)
    # Antlers swept back along the neck, pixelled at card size after the
    # silhouette so the thin tines aren't swallowed by an outline.
    r.sprite(['6.6.6...', '6.6.6.6.', '.66666.6', '.....666', '......6.'], 45, 57, anchor=(6, 4))
    return r


def draw_elephant(c, flip=False, dx=0, scale=1.0):
    """An elephant walking, trunk curled down, tusk and a fan-shaped ear."""
    r = _rig(c, flip, dx, scale, shadow=(30, 18))
    hide = LIGHT_GRAY
    _legs(r, [[(37, 75), (37, 86)], [(19, 75), (21, 86)]], DARK_GRAY, upper=3.2, lower=2.8)
    r.part().chain([(12, 68), (9, 72), (9, 76)], [0.9, 0.7, 0.6]).paint(hide, outline=DARK_GRAY)
    body = r.part().ellipse(26, 70, 14, 9).ellipse(40, 66, 7, 7.5)
    body.chain([(45, 68), (48, 74), (48, 80), (46, 84)], [3.0, 2.2, 1.6, 1.3])
    body.paint(hide, shade=DARK_GRAY, outline=DARK_GRAY)
    r.part().ellipse(36, 67, 4.5, 6.5, angle=-10).paint(hide, shade=DARK_GRAY, outline=DARK_GRAY)
    _eye(r, 43, 64)
    # Ivory tusk, outlined dark so it stands out against the grey trunk.
    r.part().chain([(44, 71), (48, 73), (51, 70)], [1.3, 1.0, 0.6]).paint(WHITE, None, outline=DARK_GRAY)
    # Saddle blanket of a royal menagerie elephant, draped over the curve of
    # the back inside the body's outline, with a gold fringe along its hem.
    blanket = r.part().poly([(19, 55), (31, 55), (30, 72), (20, 72)])
    blanket.mask &= body.interior()
    blanket.paint(LIGHT_RED, pattern=lambda x, y: YELLOW if y % 3 == 0 else None)
    hem = {}
    for x, y in blanket.mask:
        hem[x] = max(hem.get(x, y), y)
    for x, y in hem.items():
        if x % 2 == 0:
            c.put(x, y + 1, YELLOW)
    _legs(r, [[(33, 75), (34, 86)], [(16, 75), (16, 86)]], hide, upper=3.4, lower=3.0, outline=DARK_GRAY)
    # Toenails along the front of each near foot.
    for fx in (34, 16):
        for nx in (fx - 1.5, fx + 1):
            r.put(nx, 85, WHITE)
    return _done(r, feet=[(37, 87), (21, 87), (34, 87), (16, 87)])


def draw_lion(c, flip=False, dx=0, scale=1.0):
    """A lion couchant: lying with forepaws stretched out, head raised, tail curled over the haunch."""
    # Posed at full size: it lies in the 16 rows left under the Ten's lowest pips.
    r = _rig(c, flip, dx, scale, shadow=(31, 20))
    hide = YELLOW
    mane = BROWN
    # Tail curled up over the haunch, ending in a dark tuft.
    for a, b in (((12, 80), (8, 78)), ((8, 78), (8, 74)), ((8, 74), (10, 72)), ((10, 72), (15, 72))):
        r.line(*a, *b, BROWN)
    r.part().ellipse(17, 72, 1.8, 1.3).paint(mane, None, outline=DARK_GRAY)
    # Long low body, the haunch rounded up at the back; shaded only along the belly.
    body = r.part().ellipse(26, 80, 13, 5).ellipse(17, 79, 6.5, 6)
    body.paint(hide, shade=None, outline=DARK_GRAY, pattern=lambda x, y: BROWN if y == 84 and x % 2 else None)
    # The folded hind leg: a thigh crease round the haunch and the paw on the turf.
    for x, y in ((15, 77), (14, 78), (14, 79), (15, 80), (16, 81), (17, 81)):
        r.put(x, y, BROWN)
    r.part().ellipse(21, 83.5, 4, 1.6).paint(hide, None, outline=DARK_GRAY)
    # Forelegs stretched out in front, paws together, claws marked.
    r.part().capsule(34, 82.5, 50, 83.5, 2.2, 2.0).paint(hide, shade=None, outline=DARK_GRAY)
    r.line(36, 83, 48, 83, BROWN)
    for x in (50, 52):
        r.put(x, 84, BROWN)
    # Mane in jagged locks round the head and over the shoulders.
    m = r.part().ellipse(37, 77, 5.5, 6.5)
    for k in range(9):
        a = math.radians(150 + k * 30)
        m.ellipse(37 + math.cos(a) * 5.5, 77 + math.sin(a) * 6.5, 1.6, 1.6)
    m.ellipse(42, 80, 2.5, 1.8)
    m.paint(mane, shade=None, outline=DARK_GRAY, pattern=lambda x, y: RED if (x * 2 + y) % 7 == 0 else None)
    # Head in profile with a squared muzzle, the round ear tucked into the mane.
    r.part().ellipse(40, 72.5, 1.4, 1.4).paint(hide, None, outline=DARK_GRAY)
    head = r.part().ellipse(42, 76, 3.5, 3.3).rect(44, 74, 47, 78)
    head.paint(hide, shade=None, outline=DARK_GRAY)
    r.line(41, 74, 42, 74, BROWN)
    _eye(r, 43, 75)
    r.put(46, 75, BLACK)
    r.line(45, 77, 46, 77, BROWN)
    return _done(r)


# An ear of ripe wheat on its stalk: plump golden grains edged in brown with
# whiskers above. The top row is the whiskers; the stalk hangs from the bottom.
WHEAT_EAR = [
    '6.6',
    '.6.',
    'e6e',
    '6e6',
    'e6e',
    '6e6',
    '.6.',
]


def _wheat(c, x, ear_y, ground_y=87):
    """One stalk of wheat rooted at (x, ground_y), its ear's whiskers at row `ear_y`."""
    c.line(x, ear_y + len(WHEAT_EAR), x, ground_y, BROWN)
    c.blit_sprite(WHEAT_EAR, x - 1, ear_y)


def draw_pheasant(c, flip=False, dx=0, scale=1.0):
    """A cock pheasant standing in ripe wheat: copper body, green head, red wattle, long barred tail.

    Posed right of the tree trunk with its head below the lowest pips; the
    tail sweeps back across the trunk. A taller row of wheat stands behind
    it and a shorter one in front of its legs, every ear below the pips.
    """
    r = _rig(c, flip, dx, scale)
    for wx, wy in ((24, 72), (27, 75), (33, 71), (47, 72), (51, 74), (54, 76)):
        _wheat(c, r.tx(wx, 0)[0], wy)
    # Long golden tail crossed by brown bars, wide enough at the trunk not to read as part of it.
    tail = r.part().chain([(35, 79), (21, 75), (6, 71)], [2.8, 2.0, 0.7])
    tail.paint(YELLOW, shade=None, outline=DARK_GRAY, pattern=lambda x, y: BROWN if (4 * x + y) % 9 < 2 else None)
    # Copper body scalloped with dark feather tips.
    body = r.part().ellipse(39, 79, 6.5, 3.8, angle=-12).capsule(43, 77, 44, 74, 2.4, 1.8)
    body.paint(LIGHT_RED, shade=RED, outline=DARK_GRAY, pattern=lambda x, y: RED if (x + 2 * y) % 5 == 0 and y > 76 else None)
    # Buff wing coverts with a chevron of brown feather edges.
    r.part().ellipse(37, 78, 4.2, 2.2, angle=-12).paint(
        YELLOW, shade=None, outline=BROWN, pattern=lambda x, y: BROWN if (x + abs(y - 78)) % 3 == 0 else None
    )
    # Dark green head, a red wattle round the eye, a yellow bill and a white collar,
    # kept a pixel clear of the pip above.
    r.sprite(
        [
            '..8228...',
            '.822cc8..',
            '.82cc0c88',
            '.822cc2ee',
            '.8228888.',
            '8ff8.....',
        ],
        43,
        68,
    )
    # Legs down to the ground, toes spread.
    for fx in (38, 41):
        r.line(fx, 82, fx, 86, DARK_GRAY)
        r.put(fx + 1, 86, DARK_GRAY)
    _done(r)
    for wx, wy in ((31, 81), (36, 82), (46, 82), (50, 81)):
        _wheat(c, r.tx(wx, 0)[0], wy)
    return r


def draw_peacock(c, flip=False, dx=0, scale=1.0):
    """A peacock in display, its train raised behind it in a wedge of radiating, eyed feathers."""
    r = _rig(c, flip, dx, scale, shadow=(31, 7))
    ox, oy = 30, 80
    lo, hi, reach = 198, 278, 21

    def polar(deg, rad):
        a = math.radians(deg)
        return ox + math.cos(a) * rad, oy + math.sin(a) * rad

    def card(deg, rad):
        x, y = r.tx(*polar(deg, rad))
        return round(x), round(y)

    # The wedge, its rim scalloped by the feather tips.
    fan = r.part().poly([(ox, oy)] + [polar(lo + (hi - lo) * k / 12, reach) for k in range(13)])
    feathers = 9
    for k in range(feathers):
        fan.ellipse(*polar(lo + (hi - lo) * (k + 0.5) / feathers, reach - 0.5), 2.4, 2.4)
    fan.paint(GREEN, shade=None, outline=DARK_GRAY)
    # Shafts and eyes are kept off the outline so the train keeps a clean edge.
    inside = fan.interior()
    for k in range(feathers):
        deg = lo + (hi - lo) * (k + 0.5) / feathers
        for rad in range(7, reach - 3):
            if card(deg, rad) in inside:
                r.plot(*card(deg, rad), LIGHT_GREEN)
    # Eyes in two staggered rows, spaced so each reads on its own: a blue
    # centre in a cyan ring, with a gold fleck towards the feather tip.
    for row, (count, rad) in enumerate(((feathers, reach - 2), (feathers - 1, reach - 8))):
        for k in range(count):
            deg = lo + (hi - lo) * (k + 0.5 + row * 0.5) / feathers
            x, y = card(deg, rad)
            for px, py, col in ((x - 1, y, CYAN), (x + 1, y, CYAN), (x, y - 1, CYAN), (x, y + 1, CYAN), (*card(deg, rad + 1.6), YELLOW), (x, y, BLUE)):
                if (px, py) in inside:
                    r.plot(px, py, col)
    body = r.part().ellipse(30, 80, 4, 4.5).capsule(31, 77, 34, 68, 1.8, 1.4).ellipse(34.5, 66.5, 2.2, 2.0)
    body.paint(BLUE, shade=None, outline=DARK_GRAY, light=LIGHT_BLUE, pattern=lambda x, y: LIGHT_BLUE if (x * 5 + y * 3) % 7 == 0 else None)
    # Head: a black eye over a white cheek stripe, and a horn-coloured beak.
    r.put(35, 66, BLACK)
    r.put(34, 67, WHITE)
    r.put(37, 66, LIGHT_GRAY)
    r.line(37, 67, 38, 67, DARK_GRAY)
    # Crest: three bare shafts ending in dark blue tufts, clear of the train.
    for tx, ty in ((35, 61), (37, 60), (39, 61)):
        r.line(35, 64, tx, ty + 1, DARK_GRAY)
        r.put(tx, ty, BLUE)
    r.line(29, 84, 28, 87, BROWN)
    r.line(32, 84, 33, 87, BROWN)
    return _done(r, feet=[(28, 88), (33, 88)])


# Heraldic lion's head facing right (15x13): ear, heavy brow, open jaws with
# white fangs and a red tongue curling out.
# The jaws and tongue are edged in black so they stand out on the red shield.
LION_HEAD = [
    '..888..........',
    '.8ff7888.......',
    '.8f7fff788.....',
    '8ff8887ff88....',
    '8ff80788fff88..',
    '8ffffffffffff88',
    '87ffffffffffff8',
    '877fff0000000f0',
    '.877f0f4cccc0f0',
    '.877ff04cccc40.',
    '..877fff0f0cc40',
    '...8877ff0.0cc0',
    '.....8888...00.',
]


def draw_lion_rampant(c, flip=True, dx=0, dy=3, scale=1.0):
    """The silver double-tailed lion of Bohemia, rampant and crowned, for the Leaf Ace shield.

    Posed facing right and mirrored by default, as heraldic beasts face the
    shield's dexter side (the viewer's left). It fills roughly x=8..50,
    y=24..82 of a card before the `dy` shift.
    """
    r = Rig(c, flip=flip, dx=dx, dy=dy, scale=scale)
    hide, claw = WHITE, YELLOW

    def paw(x, y):
        for k in (-1, 0, 1):
            r.put(x + 2, y + k * 1.5, claw)

    # Forked double tail rising behind the back, each end in a flame-shaped tuft.
    tail = r.part().chain([(20, 62), (14, 56), (12, 48), (15, 42)], [2.2, 2.0, 1.8, 1.6])
    tail.chain([(12, 49), (7, 45), (7, 38)], [1.8, 1.6, 1.5])
    for tx, ty, ang in ((16, 37, 20), (8, 33, -15)):
        tail.ellipse(tx, ty, 2.4, 4.0, angle=ang)
    tail.paint(hide, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GRAY if (x + y) % 3 == 0 and y < 40 + dy else None)
    # Far legs, shaded.
    _legs(r, [[(30, 64), (38, 66), (35, 72), (40, 74)]], LIGHT_GRAY, upper=3.4, lower=2.0, outline=DARK_GRAY)
    _legs(r, [[(33, 46), (40, 51), (46, 48)]], LIGHT_GRAY, upper=2.8, lower=2.0, outline=DARK_GRAY)
    paw(40, 74)
    paw(46, 48)
    # Body: haunch, a narrow waist and a deep chest, rearing on the hind leg.
    body = r.part().ellipse(24, 62, 6.5, 7.5, angle=-20).capsule(25, 58, 31, 47, 4.6, 5.2).ellipse(33, 43, 7, 7.5)
    body.paint(hide, outline=DARK_GRAY)
    # A full mane in jagged locks, flowing from behind the head down onto the shoulders.
    mane = r.part().ellipse(33, 36, 8.5, 9.5)
    for k in range(11):
        a = math.radians(95 + k * 26)
        mane.ellipse(33 + math.cos(a) * 8.5, 36 + math.sin(a) * 9.5, 2.4, 2.4)
    # Short slanting strokes for the locks rather than an even speckle.
    mane.paint(hide, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GRAY if (x - y) % 4 == 0 and (x + y) % 6 < 3 else None)
    # Head in profile, hand-pixelled: brow over the eye, open jaws, tongue out.
    r.sprite(LION_HEAD, 38, 32, anchor=(5, 6))
    # Near legs: the standing hind leg and the raised foreleg, claws out.
    _legs(r, [[(23, 66), (27, 73), (21, 77), (24, 82)]], hide, upper=3.6, lower=2.0, outline=DARK_GRAY)
    _legs(r, [[(36, 45), (44, 45), (49, 39)]], hide, upper=3.0, lower=2.0, outline=DARK_GRAY)
    paw(24, 82)
    paw(49, 39)
    # Crown.
    crown = r.part().rect(33, 25, 41, 27)
    for px in (33, 37, 41):
        crown.poly([(px - 1.5, 26), (px, 21), (px + 1.5, 26)])
    crown.paint(YELLOW)
    r.put(37, 26, RED)
    return _done(r)
