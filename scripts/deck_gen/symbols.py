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
    WHITE,
    YELLOW,
    bresenham,
)
from scripts.deck_gen.rig import Rig

# Vertical Acorn (13x19): pointed nut at top, diamond-scaled cupule + oak leaflets below
ACORN_V = [
    '......6......',
    '.....6e6.....',
    '....6efe6....',
    '...6eefee6...',
    '...6eeeee6...',
    '...6eceee6...',
    '...4cc6ee4...',
    '...44c6644...',
    '..884444488..',
    '.82a82a28a28.',
    '82a28a2a82a28',
    '88282a2a28288',
    '.82a82828a28.',
    '..882868288..',
    '..2a86e68a2..',
    '.2a2.6e6.2a2.',
    '.....6e6.....',
    '.....4c4.....',
    '......4......',
]

# Horizontal Acorn pointing LEFT (19x13): nut on left, cupule + stem on right
ACORN_H_LEFT = [
    '.........8822......',
    '........82a282a....',
    '...666682a28.2a2...',
    '..6efee8a28........',
    '.6eefee82a28.......',
    '6eeeeec8a2a86eeeeee',
    '6eceeec82a284cccccc',
    '.4cc6648a28..4444..',
    '..4444482a28.2a2...',
    '........82a282a....',
    '.........8822......',
]

# Vertical Leaf (15x17): serrated linden leaf with yellow-green midrib & dual-tone halves
LEAF_V = [
    '.......8.......',
    '......8a8......',
    '.....8a228.....',
    '....8aa8228....',
    '...8aa2e8228...',
    '..8aaa8e28228..',
    '.8aa2a8e228228.',
    '8aaa8a8e2822228',
    '8aa2a8ae2288228',
    '8aaaa8e22228228',
    '.8aa28e2822228.',
    '..8aa8e228228..',
    '...8888e8888...',
    '.....44c44.....',
    '......4c4......',
    '.....4c4.......',
    '....44.........',
]

# Horizontal Leaf pointing LEFT (19x13): tip on left, stem on right
LEAF_H_LEFT = [
    '.......882288......',
    '.....88aa2a2288....',
    '...88aa8aaa8a228...',
    '..8aa2a8aa28aa228..',
    '.8aaaa2a8aa28aa28..',
    '8eeeeeeeeeeeee44c44',
    '.822822822822822844',
    '..82228222822228...',
    '...882228222288....',
    '.....88222288......',
    '.......8888........',
]

# Bell (15x15): golden hawk-bell with crimson-and-gold jewelled band and keyhole slit
BELL_SYM = [
    '......6e6......',
    '.....68.86.....',
    '....6eeeee6....',
    '..66eefeeee66..',
    '.6eeffeeeeeee6.',
    '.444c4c4c4c444.',
    '4ce4ce4ce4ce4c4',
    '444c4c4c4c4c444',
    '6eeeee888eeeee6',
    '6eee8e888e8eee6',
    '.6ee8ee8ee8ee6.',
    '.6eee8e8e8eee6.',
    '..6eee888eee6..',
    '....66eee66....',
    '......666......',
]

# Heart (15x14): Bohemian heart with top golden pearl, specular highlight & ribbed left lobe
HEART_SYM = [
    ' ..444.6.444.. ',
    '.44ccc4e4ccc44.',
    '4ccffcccccccccc',
    '4cfeecccccccccc',
    '4cc4c4ccccccccc',
    '4c4cc4ccccccccc',
    '.4cc4ccccccccc.',
    '.44c4cccccccc4.',
    '..4c4ccccccc4..',
    '...4c4ccccc4...',
    '....4c4ccc4....',
    '.....4c4c4.....',
    '......4c4......',
    '.......4.......',
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


def draw_suit_leaning(c, suit, sx, sy, angle, size=1.0, width=1.0):
    """Draws an Acorn or Leaf sign leaning `angle` degrees from upright, the end of its stem at (sx, sy).

    `size` scales it about the end of the stem; `width` stretches it across as well.

    The Aces' corner signs lean outwards like a spray, as on printed decks.
    Pixel sprites lose their veins and outlines when rotated, so these are
    built from shapes on a rig: the leaf from the outline of `LEAF_V`, the
    acorn from the nut, cupule, oak-leaf collar and stem of `ACORN_V`.
    """
    a = math.radians(angle)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux

    def at(u, v):
        u, v = u * size, v * size * width
        return sx + ux * u + nx * v, sy + uy * u + ny * v

    def line(p, q, col, inside):
        for x, y in bresenham(*at(*p), *at(*q)):
            if (x, y) in inside:
                c.put(x, y, col)

    r = Rig(c)
    if suit == 1:
        # A linden leaf: rounded lobes either side of a notch at the stem,
        # broadest low down, tapering gradually to a long pointed tip. The
        # upright sign's diamond would turn into a square when leant over.
        half = ((3.6, 2.6), (3.8, 5), (5.2, 6.6), (7.4, 7), (10, 6.2), (13, 4.4), (16, 2.4), (18.5, 0.8))
        blade = r.part().poly(
            [at(5, 0)] + [at(u, v) for u, v in half] + [at(20, 0)] + [at(u, -v) for u, v in reversed(half)]
        )

        # As on printed decks, the half away from the middle of the card is
        # in shadow and the half towards it lit.
        def outer(x, y):
            return ((x - sx) * nx + (y - sy) * ny) * angle > 0

        blade.paint(LIGHT_GREEN, None, outline=DARK_GRAY, pattern=lambda x, y: GREEN if outer(x, y) else None)
        inner = blade.interior()
        # Side veins slant up towards the tip: dark on the shaded half, mid green on the lit one.
        for u0, reach in ((6, 5.5), (9.5, 5), (13, 3.5)):
            for side in (1, -1):
                for x, y in bresenham(*at(u0, 0), *at(u0 + reach, side * reach)):
                    if (x, y) in inner:
                        c.put(x, y, DARK_GRAY if outer(x, y) else GREEN)
        line((5, 0), (18, 0), YELLOW, inner)
        r.line(*at(0.5, 0), *at(5, 0), RED)
        c.put(*at(2.5, 0.7), LIGHT_RED)
    else:
        r.part().capsule(*at(1, 0), *at(7, 0), 1.2).paint(YELLOW, None, outline=BROWN)
        c.put(*at(1, 0), RED)
        for side in (-1, 1):
            r.part().ellipse(*at(4.5, side * 2.6), 1.8, 1.0, angle=angle + 90 - side * 35).paint(GREEN, None, outline=DARK_GRAY)
        # The oak-leaf collar under the cupule: four lobes, a dark vein down the inner two.
        collar = r.part()
        for v, du in ((-4.2, 0.6), (-1.5, -0.4), (1.5, -0.4), (4.2, 0.6)):
            collar.ellipse(*at(8.5 + du, v), 2.0, 3.0, angle=angle + v * 6)
        collar.paint(GREEN, None, outline=DARK_GRAY, pattern=lambda x, y: LIGHT_GREEN if (x + 2 * y) % 4 == 0 else None)
        inner = collar.interior()
        for v in (-1.5, 1.5):
            line((7.5, v), (9.5, v), DARK_GRAY, inner)
        r.part().ellipse(*at(11.3, 0), 3.8, 1.8, angle=angle + 90).paint(LIGHT_RED, RED, outline=RED)
        nut = r.part().poly([at(*p) for p in ((11.5, 3.4), (14.5, 3.6), (17.5, 1.8), (19.5, 0), (17.5, -1.8), (14.5, -3.6), (11.5, -3.4))])
        nut.paint(YELLOW, outline=BROWN)
        c.put(*at(16, -1.2), WHITE)
        c.put(*at(15, -1.6), WHITE)


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
    # Roots flaring at bottom
    c.line(cx - 1, bottom_y - 3, cx - 4, bottom_y, BROWN)
    c.line(cx + 1, bottom_y - 3, cx + 4, bottom_y, BROWN)
    c.put(cx, bottom_y - 1, YELLOW)

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
