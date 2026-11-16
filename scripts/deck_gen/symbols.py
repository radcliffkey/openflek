"""Hand-crafted 16-colour EGA suit symbols and floral ornaments."""

import math

from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_BLUE,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    YELLOW,
    bresenham,
)
from scripts.deck_gen.rig import Rig

# Vertical Acorn (13x19): cylindrical tri-banded Bohemian nut (lit yellow left,
# vermilion middle, deep crimson right), scalloped green cupule and oak leaflets.
ACORN_V = [
    '.....644.....',
    '....6ec44....',
    '...6eecc44...',
    '...6eecc44...',
    '...6eecc44...',
    '...6eecc44...',
    '...6eecc44...',
    '...6eecc44...',
    '...44ccc44...',
    '..884444488..',
    '.8a28a2a82a8.',
    '8a2a82a28a2a8',
    '88282a2a28288',
    '.82a82828a28.',
    '..882868288..',
    '..2a86e68a2..',
    '.2a2.6e6.2a2.',
    '.....6e6.....',
    '......6......',
]

# Horizontal Acorn pointing LEFT (19x11): cylindrical tri-banded nut (yellow top,
# vermilion middle, crimson bottom), green scalloped cupule, leaflets and stem.
ACORN_H_LEFT = [
    '..........888..2...',
    '.........8a2282a...',
    '..666666682aa8a2...',
    '.6eeeeeee48a228....',
    '6eeeeeeee482a28666.',
    '4cccccccc48a228eee4',
    '4cccccccc482828444.',
    '.44444444482828....',
    '..444444488282a2...',
    '.........828282a...',
    '..........888..2...',
]

# Vertical linden leaf (15x17). Tip at the top, yellow midrib, light-green
# left half and green right half. Side veins slant up from the midrib toward
# the tip; the red stem curves away at the bottom.
LEAF_V = [
    '.......8.......',
    '......8a8......',
    '.....8ae28.....',
    '....8aae228....',
    '...8a2ae2828...',
    '..82aa2e82288..',
    '.8aa2aae228228.',
    '8a2aa2ae2822828',
    '8aa2aa2e8228228',
    '8aaa2aae2282228',
    '.8aaa2ae282228.',
    '..8aaa2e82228..',
    '...888888888...',
    '.....44c44.....',
    '......4c4......',
    '.....4c4.......',
    '....44.........',
]

# Horizontal linden leaf pointing left (19x13). Sharp tip at column 0, full
# cordate lobes around a deep notch, red/coral stem in columns 15..18. The lit
# upper half is light green with green veins; the shaded lower half is green
# with dark-grey veins. Both sets slant toward the tip. 13 rows match the
# vertical spacing of the eights and tens.
LEAF_H_LEFT = [
    '.........88888.....',
    '.......88aaaaa88...',
    '.....88aa2aaaaaa8..',
    '...88aa2aaaa2aaaa8.',
    '..8aaaaaaa2aaaa8a8.',
    '.8aaaa2aaaa2aaa88..',
    '8eeeeeeeeeeeee84c44',
    '.8222282222822284..',
    '..8222222822222828.',
    '...882282222822228.',
    '.....882282222228..',
    '.......882222288...',
    '.........88888.....',
]

# Bell (15x13): Prague half-red hawk-bell (Kule). Ribbed crimson upper dome,
# curved crimson equatorial girdle, and a golden lower hemisphere divided by
# three converging ribs down to the bottom slot.
BELL_SYM = [
    '.....48884.....',
    '...44cc4cc44...',
    '..4c4cc4cc4c4..',
    '.4cc4ccccc4cc4.',
    '.4ccc44444ccc4.',
    '444444444444444',
    '444eeeeeeeee444',
    '6eee8ee8ee8eee6',
    '.6ee8ee8ee8ee6.',
    '.6eee8e8e8eee6.',
    '..6eee888eee6..',
    '...66ee8ee66...',
    '.....66866.....',
]

# Heart (15x13): Bohemian heart with clean V-cleft and horizontal woodcut
# hatching down the left lobe against a glowing vermilion right lobe.
HEART_SYM = [
    '..4444...4444..',
    '.4cccc4.4cccc4.',
    '44444cc4cccccc4',
    '4ccccccccccccc4',
    '444444cccccccc4',
    '.4ccccccccccc4.',
    '.44444ccccccc4.',
    '..4ccccccccc4..',
    '...4444cccc4...',
    '....4ccccc4....',
    '.....44cc4.....',
    '......4c4......',
    '.......4.......',
]

# Monumental corner emblems for the Aces (Esa), matching the oversized suit
# signs of printed Prague decks and 1992 FLEK!.
ACE_ACORN_LEFT = [
    '..66444..........',
    '.6eecc444........',
    '6eeeeccc44.......',
    '6eeeeccc444......',
    '.6eeeccc444......',
    '.6eeeeccc444.....',
    '..6eeeccc444.....',
    '..6eeeeccc4488...',
    '...44eeccc48a28..',
    '....444cc48a2a28.',
    '...88844482a82a8.',
    '..8a2a8882a28288.',
    '..82a2a828a2828..',
    '...88282a28288...',
    '....82a8286882a..',
    '.....88868ee62a2.',
    '.....2a2.6ee6.2..',
    '....2a2...6ee6...',
    '...........6e6...',
]

ACE_BELL = [
    '......4488844......',
    '....44cc888cc44....',
    '...44c4c888c4c44...',
    '..4cc4c4c4c4c4cc4..',
    '.4c4cc4c4c4c4cc4c4.',
    '.44c4ccccccccc4c44.',
    '4ccccc4444444ccccc4',
    '4cc4444444444444cc4',
    '444444eeeeeee444444',
    '444eeeeee8eeeeee444',
    '6eeeee8ee8ee8eeeee6',
    '.6e8ee88e8e88ee8e6.',
    '.6ee8ee8e8e8ee8ee6.',
    '..6ee8eee8eee8ee6..',
    '...6ee88e8e88ee6...',
    '....66eee8eee66....',
    '......6648466......',
    '........313........',
    '........333........',
]

ACE_HEART = [
    '..444444.....444444..',
    '.4cccccc4...4cccccc4.',
    '4444444cc4.4cccccccc4',
    '4ccccccccc4ccccccccc4',
    '444444444ccccccccccc4',
    '4ccccccccccccccccccc4',
    '444444444ccccccccccc4',
    '.4ccccccccccccccccc4.',
    '.44444444cccccccccc4.',
    '..4ccccccccccccccc4..',
    '...444444cccccccc4...',
    '....4ccccccccccc4....',
    '.....44444ccccc4.....',
    '......4ccccccc4......',
    '.......4444cc4.......',
    '........4ccc4........',
    '.........4c4.........',
    '..........4..........',
]

# Roman numeral X (11x9) for the 10 cards: black, a thick stroke falling to the
# right crossed by a thin one, with serifs top and bottom
ROMAN_X = [
    '0000...000.',
    '.00.....0..',
    '..00...0...',
    '...00.0....',
    '....00.....',
    '...0.00....',
    '..0...00...',
    '.0.....00..',
    '000...0000.',
]


def draw_suit(c, suit, cx, cy, orientation='v'):
    """Draws a suit symbol centered at (cx, cy).
    orientation: 'v' (vertical), 'left' (pointing left), 'right' (pointing right)
    """
    if suit == 0:  # Acorns
        if orientation == 'left':
            c.blit_centered(ACORN_H_LEFT, cx, cy, flip_x=False)
        elif orientation == 'right':
            c.blit_centered(ACORN_H_LEFT, cx, cy, flip_x=True)
        else:
            c.blit_centered(ACORN_V, cx, cy)
    elif suit == 1:  # Leaves
        if orientation == 'left':
            c.blit_centered(LEAF_H_LEFT, cx, cy, flip_x=False)
        elif orientation == 'right':
            c.blit_centered(LEAF_H_LEFT, cx, cy, flip_x=True)
        else:
            c.blit_centered(LEAF_V, cx, cy)
    elif suit == 2:  # Bells
        c.blit_centered(BELL_SYM, cx, cy)
    else:  # Hearts
        c.blit_centered(HEART_SYM, cx, cy)


def draw_leaf_leaning(c, sx, sy, angle, size=1.0, width=1.0):
    """Draws a Leaf sign leaning `angle` degrees from upright, the end of its stem at (sx, sy).

    `size` scales it about the end of the stem; `width` stretches it across as well.

    The Leaf Ace's corner signs lean outwards like a spray, as on printed
    decks. A pixel sprite loses its veins and outline when rotated, so the
    leaf is built from shapes on a rig, after the outline of `LEAF_V`.
    """
    a = math.radians(angle)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux

    def at(u, v):
        u, v = u * size, v * size * width
        return sx + ux * u + nx * v, sy + uy * u + ny * v

    r = Rig(c)
    # A linden leaf: rounded lobes either side of a notch at the stem,
    # broadest low down, tapering gradually to a long pointed tip. The
    # upright sign's diamond would turn into a square when leant over.
    half = ((3.6, 2.6), (3.8, 5), (5.2, 6.6), (7.4, 7), (10, 6.2), (13, 4.4), (16, 2.4), (18.5, 0.8))
    blade = r.part().poly([at(5, 0)] + [at(u, v) for u, v in half] + [at(20, 0)] + [at(u, -v) for u, v in reversed(half)])

    # As on printed decks, the half away from the middle of the card is
    # in shadow and the half towards it lit.
    def outer(x, y):
        return ((x - sx) * nx + (y - sy) * ny) * angle > 0

    blade.paint(LIGHT_GREEN, None, outline=DARK_GRAY, pattern=lambda x, y: GREEN if outer(x, y) else None)
    inner = blade.interior()

    def vein(p, q, colour):
        for x, y in bresenham(*at(*p), *at(*q)):
            if (x, y) in inner:
                c.put(x, y, colour(x, y))

    # Side veins slant up towards the tip: dark on the shaded half, mid green on the lit one.
    for u0, reach in ((6, 5.5), (9.5, 5), (13, 3.5)):
        for side in (1, -1):
            vein((u0, 0), (u0 + reach, side * reach), lambda x, y: DARK_GRAY if outer(x, y) else GREEN)
    vein((5, 0), (18, 0), lambda x, y: YELLOW)
    r.line(*at(0.5, 0), *at(5, 0), RED)
    c.put(*at(2.5, 0.7), LIGHT_RED)


def draw_ace_corner_pips(c, suit):
    """Draws the oversized corner suit emblems on an Ace card."""
    if suit == 0:
        c.blit_sprite(ACE_ACORN_LEFT, 3, 4, flip_x=False)
        c.blit_sprite(ACE_ACORN_LEFT, 41, 4, flip_x=True)
    elif suit == 1:
        draw_leaf_leaning(c, 14.5, 23, -35, size=1.14, width=1.2)
        draw_leaf_leaning(c, 45.5, 23, 35, size=1.14, width=1.2)
    elif suit == 2:
        c.blit_centered(ACE_BELL, 11, 12)
        c.blit_centered(ACE_BELL, 49, 12)
    else:
        c.blit_centered(ACE_HEART, 13, 12)
        c.blit_centered(ACE_HEART, 47, 12)


def draw_roman_x(c, cx=30, y0=3):
    c.blit_sprite(ROMAN_X, cx - 5, y0)


def draw_floret(c, cx, cy, suit):
    """Draws a small ornamental divider between pips on Bell and Heart number cards."""
    if suit == 2:  # Bells: blue forget-me-not blossom with gold center & green leaves
        c.line(cx - 5, cy, cx + 5, cy, GREEN)
        c.put(cx - 4, cy - 1, LIGHT_GREEN)
        c.put(cx + 4, cy - 1, LIGHT_GREEN)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            c.put(cx + dx, cy + dy, LIGHT_BLUE if (dx + dy) % 2 == 0 else CYAN)
        c.put(cx, cy, YELLOW)
        c.put(cx - 3, cy, BLUE)
        c.put(cx + 3, cy, BLUE)
    else:  # Hearts: crimson rosebud with green sepals & golden stem
        c.line(cx, cy - 4, cx, cy + 4, GREEN)
        c.line(cx - 4, cy + 1, cx + 4, cy + 1, GREEN)
        c.put(cx - 3, cy, LIGHT_GREEN)
        c.put(cx + 3, cy, LIGHT_GREEN)
        for dx, dy in [(-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, -2)]:
            c.put(cx + dx, cy + dy, LIGHT_RED)
        c.put(cx, cy - 1, YELLOW)
        c.put(cx, cy, RED)


def draw_tree_trunk(c, top_y, bottom_y, branch_ys, suit):
    """Draws the central gnarled trunk and twigs for Acorn and Leaf number cards."""
    cx = 30
    # Main trunk: 3px wide with brown/yellow bark and dark grey/red edge
    for y in range(top_y, bottom_y):
        c.put(cx - 1, y, BROWN)
        c.put(cx, y, YELLOW if (y % 3) != 0 else BROWN)
        c.put(cx + 1, y, BROWN if (y % 2) == 0 else RED)
    # Roots flaring into the foreground turf, dark-edged against the grass
    c.line(cx - 2, bottom_y - 3, cx - 5, bottom_y, DARK_GRAY)
    c.line(cx + 2, bottom_y - 3, cx + 5, bottom_y, DARK_GRAY)
    c.line(cx - 1, bottom_y - 3, cx - 4, bottom_y, BROWN)
    c.line(cx + 1, bottom_y - 3, cx + 4, bottom_y, BROWN)
    c.line(cx - 2, bottom_y, cx + 2, bottom_y, BROWN)
    c.put(cx, bottom_y - 1, YELLOW)
    for gx in (cx - 4, cx - 2, cx + 1, cx + 4):
        c.put(gx, bottom_y, GREEN)
        c.put(gx + 1, bottom_y, LIGHT_GREEN if suit == 1 else GREEN)

    # Curved twigs & small shoots to each branch pair
    for by in branch_ys:
        # Left and right red/pink twigs connecting trunk to horizontal pips
        c.line(cx - 2, by + 3, cx - 7, by, RED)
        c.line(cx - 2, by + 2, cx - 6, by, LIGHT_RED)
        c.line(cx + 2, by + 3, cx + 7, by, RED)
        c.line(cx + 2, by + 2, cx + 6, by, LIGHT_RED)
        # Small green leaflet shoot on each twig
        leaf_col = LIGHT_GREEN if suit == 1 else GREEN
        c.put(cx - 4, by + 4, GREEN)
        c.put(cx - 5, by + 5, leaf_col)
        c.put(cx + 4, by + 4, GREEN)
        c.put(cx + 5, by + 5, leaf_col)
        # Tiny berry/bud above twig junction
        c.put(cx - 3, by - 2, LIGHT_RED)
        c.put(cx + 3, by - 2, LIGHT_RED)
        c.put(cx, by, DARK_GRAY)


def draw_shrub(c, cx, base_y, rx, ry, flowers=()):
    """A rounded shrub standing on row `base_y`: solid green, lit on the upper left, dark-edged.

    Its flat bottom has no outline, so it grows out of the turf. `flowers`
    lists blooms as (dx, dy, colour) relative to (cx, base_y).
    """
    cy = base_y - ry + 1
    lx, ly = cx - rx * 0.35, cy - ry * 0.35

    def inside(x, y):
        return y <= base_y and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1

    for y in range(int(cy - ry) - 1, base_y + 1):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if not inside(x, y):
                continue
            if not (inside(x - 1, y) and inside(x + 1, y) and inside(x, y - 1)):
                col = DARK_GRAY
            elif ((x - lx) / (rx * 0.5)) ** 2 + ((y - ly) / (ry * 0.5)) ** 2 <= 1:
                col = LIGHT_GREEN
            elif (x * 3 + y * 5) % 11 == 0:
                col = LIGHT_GREEN
            else:
                col = GREEN
            c.put(x, y, col)
    for dx, dy, col in flowers:
        c.put(cx + dx, base_y + dy, col)
