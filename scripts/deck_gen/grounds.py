"""The ground each suit stands on, shared by the number cards and the standing court figures.

Acorns grow on a forest floor, Leaves in a meadow, Bells hang over a paved
town square and Hearts over a formal garden. The four are told apart at a
glance by colour and by skyline; within a suit only small details move from
card to card, so a suit's cards belong together.

The grounds are flat colour with a few placed details. Speckle and one-pixel
chequers turn to static under the small scenes that stand on them.
"""

import math

from scripts.deck_gen.palette import (
    BROWN,
    DARK_GRAY,
    GREEN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_RED,
    RED,
    WHITE,
    YELLOW,
    fill_terrain,
)

# The row a number card's scenery stands on. The features low in each ground
# (the forest bank, the near meadow hill, the parterre) keep just below it,
# whatever the height of the skyline.
STAND_ROW = 88

# The row the Hearts' gravel parterre starts on, and its half-width as it
# widens towards the viewer.
PARTERRE_TOP = STAND_ROW + 2


def _parterre_half(y):
    return 13 + max(y - PARTERRE_TOP, 0) * 2 // 3


def _lattice_mark(x, y, cell_w, cell_h, salt):
    """Places at most one mark in each cell of a jittered lattice.

    Returns (kind, dx, dy): a small number picking what the cell holds and
    the pixel's offset from the mark's top-left corner. Marks set out this
    way stay evenly spread, where a per-pixel hash clumps them into static.
    """
    cx, cy = x // cell_w, y // cell_h
    h = (cx * 7919 + cy * 104729 + salt * 31) % 1009
    mx = cx * cell_w + h % (cell_w - 1)
    my = cy * cell_h + (h // 7) % (cell_h - 1)
    return (h // 53) % 8, x - mx, y - my


def _forest_floor(variant, x, y, crest):
    """Acorns: a mossy bank over bare woodland earth strewn with fallen leaves."""
    if y - crest == 1:
        return LIGHT_GREEN
    # The turf ends in a wavy cut bank; grass tips hang over its edge.
    bank = STAND_ROW + 2 + int(round(math.sin((x + variant * 9) * 0.45)))
    tip = (x + variant) % 4 == 0
    if y < bank:
        return GREEN
    if y == bank:
        return GREEN if tip else DARK_GRAY
    if y == bank + 1 and tip:
        return GREEN
    kind, dx, dy = _lattice_mark(x, y, 8, 3, variant)
    if dy == 0 and 0 <= dx <= 1 and y > bank + 1:
        if kind < 2:
            return YELLOW
        if kind < 4:
            return LIGHT_RED
        if kind == 4 and dx == 0:
            return DARK_GRAY
    return BROWN


def _meadow(variant, x, y, crest):
    """Leaves: a sunlit meadow, a near hill rolling in front of a lighter far one, dotted with flowers."""
    near = STAND_ROW + 1 + int(round(math.sin((x + variant * 11) * 0.16 + 2.0) * 2.5))
    if y <= near or y - crest == 1:
        return LIGHT_GREEN
    kind, dx, dy = _lattice_mark(x, y, 7, 3, variant + 4)
    if dx == 0 and dy == 0 and y > near + 1:
        if kind < 2:
            return WHITE
        if kind < 4:
            return YELLOW
        if kind == 4:
            return LIGHT_RED
    return GREEN


def _town_square(variant, x, y, crest):
    """Bells: a town square paved in courses of bevelled limestone and grey flagstones."""
    d = y - crest
    # Each course is a row deeper and two pixels wider than the one behind
    # it, closed by a horizontal mortar joint (`d == top + depth`) and offset
    # from its neighbours by half a stone. Every stone has a light-grey body
    # so none merges with the white card background.
    top, depth, width, course = 1, 3, 8, 0
    while d > top + depth:
        top += depth + 1
        depth += 1
        width += 2
        course += 1
    if d == top + depth:
        return DARK_GRAY
    sx = x - 30 + variant * 3 + (width // 2 if course % 2 else 0)
    u = sx % width
    if u == 0:
        return DARK_GRAY
    if (sx // width + course) % 2:
        return LIGHT_GRAY
    # Alternate stones carry a chiselled white top-and-left bevel, kept inside
    # the mortar and off the card border so the edge stays framed.
    if 3 <= x <= 57 and ((d == top and u < width - 1) or (u == 1 and d < top + depth - 1)):
        return WHITE
    return LIGHT_GRAY


def _garden(variant, x, y, crest):
    """Hearts: a formal garden, a flared gravel parterre in a clipped lawn between staggered rose beds."""
    d = y - crest
    if d == 1:
        return LIGHT_GREEN
    off = abs(x - 30)
    half = _parterre_half(y)
    if y >= PARTERRE_TOP and off <= half + 1:
        if y == PARTERRE_TOP or off == half + 1:
            return LIGHT_GREEN
        if y == PARTERRE_TOP + 1 and off < half:
            return BROWN
        return YELLOW
    # Staggered 2x2 roses with a lit leaf beside each bloom, placed only where
    # the whole cluster clears the crest, the card border and the boxwood kerb.
    band = (y - STAND_ROW + 4) // 4
    ry = (y - STAND_ROW + 4) % 4
    rx = (x + variant * 2 + (3 if band % 2 else 0)) % 6
    x0, y0 = x - rx, y - ry
    if rx <= 2 and ry <= 1 and y0 >= crest + 3 and y0 + 1 <= 97:
        if all(2 < px < 58 and abs(px - 30) >= _parterre_half(py) + 3 for px in (x0, x0 + 2) for py in (y0, y0 + 1)):
            if rx == 2:
                return LIGHT_GREEN if ry == 1 else GREEN
            return RED if (rx, ry) == (1, 1) else LIGHT_RED
    return GREEN


GROUNDS = (_forest_floor, _meadow, _town_square, _garden)


def _crest(suit, variant, x, base):
    """The top of the ground in column x: woodland humps, a long meadow swell or a level terrace.

    `base` is the row the skyline lies around.
    """
    if suit == 0:
        return base + int(round(math.sin((x + variant * 5) * 0.3) * 1.6 + math.sin((x + variant * 5) * 0.11)))
    if suit == 1:
        return base + int(round(math.sin((x + 7 + variant * 5) * 0.13) * 2.4))
    return base + 1


def draw_suit_ground(c, suit, variant, base=84):
    """Fills the bottom of a card with the suit's ground, its skyline around row `base`.

    `variant` tells the cards of a suit apart: it shifts the humps, the
    flowers and the joints, never the kind of ground.

    Returns the skyline as a function of the column, for whatever is to
    grow along it.
    """
    ground = GROUNDS[suit]

    def skyline(x):
        return _crest(suit, variant, x, base)

    fill_terrain(c, skyline, lambda x, y, top: ground(variant, x, y, top))
    return skyline


def draw_footing(c, suit, xs, y):
    """Sets feet whose soles are at row `y`, centred on the columns `xs`, into the suit's ground.

    Grass grows over the soles so they stand in the turf; on the Bells'
    paving a shadow lies under them instead.
    """
    for bx in xs:
        for dx in range(-4, 5, 2):
            if suit == 2:
                c.put(bx + dx, y + 1, DARK_GRAY)
                c.put(bx + dx + 1, y + 1, DARK_GRAY)
            else:
                c.put(bx + dx, y, GREEN)
                c.put(bx + dx + 1, y - 1, LIGHT_GREEN if suit != 0 else GREEN)
