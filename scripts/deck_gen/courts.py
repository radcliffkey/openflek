"""Court cards (Spodek/Unter, Svršek/Ober, Král/King) for all 4 suits."""

import math
from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    LIGHT_BLUE,
    LIGHT_CYAN,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_MAGENTA,
    LIGHT_RED,
    MAGENTA,
    RED,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.symbols import draw_suit


# Hand-crafted 20x21 head & hat/crown sprites (y=4..24) for all 12 court figures.
# Every head is rendered in a true side-profile or 3/4 view with:
# - Pure WHITE ('f') skin and warm BROWN/YELLOW ('6'/'e') hair/beards (zero grey '7' next to skin!)
# - A single profile eye (or off-center 3/4 pair) and a bold projecting L-shaped nose jutting
#   out into the open background on the facing side.

# Acorn Unter: Side profile facing RIGHT (green huntsman hat with red plume swept left,
# thick brown hair on left, single profile eye, nose & chin jutting right).
HEAD_UNTER_ACORN = [
    '.44ccc4.............',
    '44cccceee...........',
    '.88222aaa22888......',
    '..82222aaa2222288...',
    '..82226e2222222228..',
    '.82266e66e666e62228.',
    '8888888888888888888.',
    '..8666666fffffff8...',
    '.8666666fffffffff8..',
    '.866666fffff666ff8..',
    '.866666fffff899ff8..',
    '.866666ffffffffff88.',
    '..86666ffffffffffff8',
    '..86666fffffffff88f8',
    '...8666ffffffffff88.',
    '...8666fffff66668...',
    '....866fffff444f8...',
    '....88ffffffffff8...',
    '......88fffffff88...',
    '........88fff88.....',
    '..........888.......',
]

# Leaf Unter: Side profile facing RIGHT (playing transverse flute, feathered cap,
# golden-brown hair on left, single profile eye, nose & lips jutting right).
HEAD_UNTER_LEAF = [
    '.ffbb...............',
    'ffbb991111111.......',
    '.b91199333339911....',
    '..1933bbbbbbb3391...',
    '..199333333333991...',
    '..1199e6e6e6e9911...',
    '..888888888888888...',
    '..8eeeeeffffffff8...',
    '.8eeeeeefffffffff8..',
    '.8eeeeefffff666ff8..',
    '.86eeeefffff833ff8..',
    '.866eeeffffffffff88.',
    '..866eeffffffffffff8',
    '..866eefffffffff88f8',
    '...866effffffffff88.',
    '...866ffffff444ff8..',
    '....88fffffffffff8..',
    '......8fffffffff88..',
    '.......88ffffff88...',
    '........88fff88.....',
    '..........888.......',
]

# Bell Unter: Side profile facing RIGHT (golden-trimmed helmet with red plume swept left,
# thick brown hair on left, single profile eye, nose & mustache jutting right).
HEAD_UNTER_BELL = [
    '.44cccc4............',
    '4cccccccc4..........',
    '..88eefffffee88.....',
    '.8eefffffffffee8....',
    '8eefffffffffffee8...',
    '86eeeeeeeeeeeee68...',
    '88888888888888888...',
    '.8666666fffffff8....',
    '.866666fffffffff8...',
    '.866666ffff888ff8...',
    '.866666ffff899ff8...',
    '.86666ffffffffff88..',
    '..8666ffffffffffff8.',
    '..8666fffffffff88f8.',
    '...866ffffffffff88..',
    '...866ffff666668....',
    '....86fffff444f8....',
    '....88ffffffffff8...',
    '......88fffffff88...',
    '........88fff88.....',
    '..........888.......',
]

# Heart Unter: Side profile facing LEFT (crimson beret with white plume swept right,
# golden hair on right, single profile eye & nose jutting left).
HEAD_UNTER_HEART = [
    '.............fffc...',
    '.....4444cccc4ffc...',
    '....4ccccccccc4fc...',
    '...4cccccccccc44....',
    '...4ccc6e6e6ccc4....',
    '....444888888444....',
    '...8fffffffffeeee8..',
    '..8fffffffffffeeee8.',
    '..8ff666ffffffeeee8.',
    '..8ff998ffffffeee68.',
    '.88ffffffffffffee68.',
    '8fffffffffffffee668.',
    '8f88ffffffffffe668..',
    '.88fffffffffffe68...',
    '..8ff444ffffff668...',
    '..8fffffffffff88....',
    '..88fffffffff8......',
    '...88ffffff88.......',
    '.....88fff88........',
    '.......888..........',
    '....................',
]

# Acorn Ober: Side profile facing LEFT (feathered hunting hat, brown beard & nose
# projecting to the left).
HEAD_OBER_ACORN = [
    '...............2a2..',
    '.....4cccc444..2aa2.',
    '....4cccccc6666822..',
    '...4cccc666686668...',
    '..866866e66e668668..',
    '..8666eeeeeeee6668..',
    '..8888888888888888..',
    '..8ffffffff666668...',
    '.8fffffffff6666668..',
    '.8ff888fffff666668..',
    '.8ff998fffff666668..',
    '88ffffffffff666668..',
    '8fffffffffff66668...',
    '8f88ffffffff66668...',
    '.88ffffffff66668....',
    '..86666ffff66668....',
    '.866444ff666668.....',
    '.8666ffff666668.....',
    '..866666666668......',
    '...8866e66688.......',
    '.....886688.........',
]

# Leaf Ober: Side profile facing LEFT (tall red Landsknecht shako with green plume,
# gazing left down at his side-drum).
HEAD_OBER_LEAF = [
    '...........aaa22....',
    '.........aa222ee6...',
    '...44444cccccccc4...',
    '..4cccccccccccccc4..',
    '.4cccccccccccccccc4.',
    '..4446e6e6e6e6e444..',
    '..8888888888888888..',
    '..8ffffffff666668...',
    '.8fffffffff6666668..',
    '.8ff888fffff666668..',
    '.8ff338fffff666668..',
    '88ffffffffff666668..',
    '8fffffffffff66668...',
    '8f88ffffffff66668...',
    '.88ffffffff66668....',
    '..86666ffff66668....',
    '.866444ff666668.....',
    '..8666ffff6668......',
    '..88666666688.......',
    '....886eee68........',
    '......88688.........',
]

# Bell Ober: Side profile facing LEFT (crested golden-steel helmet, golden-brown beard jutting left).
HEAD_OBER_BELL = [
    '.....6eee4cc44......',
    '....6eeecccccc4.....',
    '...88eefffffee88....',
    '..8eefffffffffee8...',
    '.8eeeffffffffeee8...',
    '88eeeeeeeeeeeeee88..',
    '888888888888888888..',
    '..8ffffffff66eee8...',
    '.8fffffffff6eeee8...',
    '.8ff888fffff6eee8...',
    '.8ff998fffff6eee8...',
    '88ffffffffff6ee68...',
    '8fffffffffff6668....',
    '8f88ffffffff6668....',
    '.88ffffffff66668....',
    '..86666ffffee668....',
    '.866444ff6eee68.....',
    '..8eeefffffee68.....',
    '..88eeeeeeee88......',
    '....886eee688.......',
    '......88688.........',
]

# Heart Ober: Side profile facing RIGHT (magenta/crimson velvet hat on left, golden hair
# on left, single profile eye, nose & golden beard jutting right toward his raised chalice).
HEAD_OBER_HEART = [
    '..6e6..44444........',
    '.55d5d44ccccc4......',
    '5dddd5cccccccc4.....',
    '.55d55cccccccce4....',
    '..5558f8f8f8f84.....',
    '..88888888888888....',
    '..8eee66ffffffff8...',
    '.8eeee66fffffffff8..',
    '.8eeee66fffff66ff8..',
    '.8eeee66fffff89ff8..',
    '.86eee6ffffffffff88.',
    '..8666fffffffffffff8',
    '..8666ffffffffff88f8',
    '...866fffffffffff88.',
    '...866effff6666f68..',
    '....86ee66ffff44e8..',
    '....86eeefffffffeee8',
    '.....88eeeeeeeeeee88',
    '.......8866eeeee688.',
    '.........88866688...',
    '....................',
]

# Acorn King: Side/3/4 profile facing RIGHT (gold/red crown, golden-brown hair & beard
# swept back on left, nose & royal beard jutting right).
HEAD_KING_ACORN = [
    '...6e6...6e6...6e6..',
    '..86eee66eee66eee68.',
    '..8ee44ee222ee44ee8.',
    '..8eeeeeeeeeeeeeee8.',
    '..864e62e4e4e26e468.',
    '..88888888888888888.',
    '..866eeefffffffff8..',
    '.866eeeeffffffffff8.',
    '.866eeefffff666ff8..',
    '.866eeefffff899ff8..',
    '.866eeeffffffffff88.',
    '.866eeeffffffffffff8',
    '.866eeefffffffff88f8',
    '.866eeeefffffffff88.',
    '..866eef888fff8888..',
    '..866ee8fffffff448..',
    '..866eeeffffffffe8..',
    '..86eeeeeeeeeeeee8..',
    '...866eee666eee668..',
    '....8866eeeee6688...',
    '.....88666666688....',
]

# Leaf King: Side/3/4 profile facing LEFT (emerald-and-gold crown, warm brown-gold hair on
# right, single profile eye, nose & beard jutting left).
HEAD_KING_LEAF = [
    '........6e6.........',
    '....6e66eee66e6.....',
    '...8ee44eee44ee8....',
    '...8ceee222eeec8....',
    '...8eeeeeeeeeee8....',
    '...869e64e46e968....',
    '...8888888888888....',
    '...8fffffffff66668..',
    '..8ffffffffff666668.',
    '..8ff888fffff666668.',
    '..8ff338fffff666668.',
    '.88ffffffffff666668.',
    '8ffffffffffff666668.',
    '8f88fffffffff66668..',
    '.88ffffffffff66668..',
    '..8888fff888f66668..',
    '..844fffffff8eee68..',
    '..8efffffffffeee68..',
    '..86eeeeeeeeeee68...',
    '...8866eeeee6688....',
    '.....886666688......',
]

# Bell King: Side profile facing LEFT (like Original Card 22: imperial crown,
# golden curls on right, profile nose & beard pointing left).
HEAD_KING_BELL = [
    '..6..6e6..6e6..6....',
    '..86ee4eee4eee4e68..',
    '..8eee22c8c222eee8..',
    '..8eeeeeeeeeeeeee8..',
    '..864e69e4e4e96e48..',
    '..8888888888888888..',
    '..8fffffffffeeee8...',
    '.8fffffffffffeeee8..',
    '.8ff888ffffffeeee8..',
    '.8ff998ffffffeeee8..',
    '88fffffffffffee668..',
    '8ffffffffffff66668..',
    '8f88fffffffff66668..',
    '.88ffffffffff66668..',
    '.8888fff888f6eee68..',
    '.844fffffff6eeee68..',
    '.8eeefffffffffee68..',
    '..86eeeeeeeeeee668..',
    '...86ee6eeeee6ee8...',
    '....8866eeeee6688...',
    '......886666688.....',
]

# Heart King: Side/3/4 profile facing RIGHT (crimson velvet & gold crown, golden-brown
# beard & hair on left, projecting nose & beard jutting right toward his raised chalice).
HEAD_KING_HEART = [
    '...6e6...6e6...6e6..',
    '..8eee44eeeee44eee8.',
    '..8e4ccc44444ccc4e8.',
    '..8e2ccccccccccc2e8.',
    '..86eeeeeeeeeeeee68.',
    '..88888888888888888.',
    '..866eeeffffffffff8.',
    '.866eeeefffffffffff8',
    '.866eeeffffff666ff8.',
    '.866eeeffffff899ff8.',
    '.866eeeffffffffff88.',
    '.866eeeffffffffffff8',
    '.866eeefffffffff88f8',
    '.866eeeefffffffff88.',
    '..866eef888fff8888..',
    '..866ee8fffffff448..',
    '..866eeeffffffffe8..',
    '..86eeeeeeeeeeeee8..',
    '...866eee666eee668..',
    '...8866eeeee6688....',
    '....88666666688.....',
]


def draw_pedestal(c, suit, is_king=False):
    """Draws an organic multi-layered landscape hillock or throne floor at y=80..97."""
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
                if suit == 0:
                    col = CYAN if tile == 0 else DARK_GRAY
                elif suit == 1:
                    col = GREEN if tile == 0 else YELLOW
                elif suit == 2:
                    col = YELLOW if tile == 0 else CYAN
                else:
                    col = LIGHT_CYAN if tile == 0 else CYAN
            else:
                if y <= hill_y + 3:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
                elif 12 <= x <= 48:
                    col = YELLOW if ((x + y) & 1) == 0 else LIGHT_GREEN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            c.put(x, y, col)


def _bury_boots_in_turf(c, boot_xs):
    """Draws overlapping grass tufts and flowers across boot soles at y=86..91 so feet are deeply grounded."""
    for bx in boot_xs:
        c.fill_ellipse(bx, 89, 6, 2, GREEN, LIGHT_GREEN, outline= None, mode='checker')
        for dx in range(-5, 6, 2):
            if c.in_interior(bx + dx, 87):
                c.put(bx + dx, 87, GREEN)
            if c.in_interior(bx + dx + 1, 88):
                c.put(bx + dx + 1, 88, LIGHT_GREEN)


def draw_ermine_collar(c, cx, y0, w, h):
    """Draws a royal white ermine collar/trim with dark tail spots."""
    c.fill_ellipse(cx, y0 + h // 2, w // 2, h // 2, WHITE, WHITE, outline=DARK_GRAY)
    for dx in range(-w // 2 + 3, w // 2 - 2, 4):
        c.put(cx + dx, y0 + h // 2, DARK_GRAY)
        c.put(cx + dx, y0 + h // 2 + 1, YELLOW)


def draw_unter(c, suit):
    """Draws the 4 Spodek (Unter) cards in side-profile walking/lunging stances with both feet pointing the same way!"""
    draw_pedestal(c, suit, is_king=False)

    if suit == 0:  # Acorn Unter: Walking/lunging RIGHT in side profile (both boots pointing RIGHT)
        # Green cloak streaming left behind back (x=5..23, y=24..56)
        c.fill_poly([(17, 24), (27, 25), (19, 56), (5, 50)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        # Back arm raised holding steel broadsword overhead
        c.fill_poly([(14, 25), (20, 24), (13, 13), (8, 16)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(10, 13, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_poly([(9, 11), (41, 5), (42, 8), (10, 14)], LIGHT_CYAN, WHITE, outline=BLUE)
        c.line(10, 9, 12, 16, YELLOW)
        # Narrow side-profile torso at x=16..31, y=24..52
        c.fill_poly([(16, 24), (30, 25), (33, 52), (16, 52)], YELLOW, BROWN, outline=BROWN)
        c.thick_line(18, 25, 31, 48, RED, 2)
        c.fill_rect(16, 48, 33, 51, CYAN, BLUE, mode='hstripe')
        # Forward right arm thrusting hunting sword to the right (x=29..55, y=27..44)
        c.fill_poly([(28, 26), (33, 26), (44, 39), (38, 42)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(42, 41, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_poly([(43, 40), (55, 34), (56, 37), (44, 43)], LIGHT_CYAN, WHITE, outline=BLUE)
        c.line(42, 38, 44, 44, YELLOW)
        # Side-profile walking legs (back leg x=14..22, front leg stepping right x=27..38) - BOTH boots point RIGHT!
        c.fill_poly([(16, 52), (24, 52), (21, 72), (13, 72)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(24, 52), (33, 52), (39, 70), (30, 70)], LIGHT_RED, RED, outline=RED)
        # Back boot (x=13..20, toe pointing RIGHT to x=24) & front boot (x=31..39, toe pointing RIGHT to x=44)
        c.fill_poly([(13, 71), (20, 71), (19, 89), (12, 89)], YELLOW, BROWN, outline=BROWN)
        c.fill_ellipse(18, 88, 5, 2, YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(31, 69), (39, 69), (39, 89), (31, 89)], YELLOW, BROWN, outline=BROWN)
        c.fill_ellipse(38, 88, 5, 2, YELLOW, BROWN, outline=BROWN)
        _bury_boots_in_turf(c, [17, 37])
        # Collar & profile head looking right
        c.fill_rect(18, 22, 29, 25, WHITE)
        c.rect(18, 22, 29, 25, DARK_GRAY)
        c.blit_sprite(HEAD_UNTER_ACORN, 14, 4)
        # Grounded oak stem & lower Acorn pip growing directly out of the turf at x=50, y=75..88
        c.thick_line(50, 79, 50, 88, BROWN, 2)
        c.line(50, 84, 46, 81, GREEN)
        c.line(50, 84, 54, 81, LIGHT_GREEN)
        draw_suit(c, 0, 50, 75, 'v')

    elif suit == 1:  # Leaf Unter: Side profile facing RIGHT, playing transverse flute (both boots pointing RIGHT)
        c.fill_poly([(15, 24), (26, 25), (21, 64), (7, 58)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(16, 24), (31, 25), (33, 54), (15, 54)], GREEN, LIGHT_GREEN, outline=DARK_GRAY)
        c.fill_poly([(23, 25), (31, 25), (33, 54), (24, 54)], LIGHT_RED, RED, outline=RED)
        c.fill_rect(15, 49, 33, 52, YELLOW, BROWN, mode='hstripe')
        c.fill_poly([(20, 26), (26, 26), (38, 21), (34, 17)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(28, 26), (33, 26), (48, 22), (44, 18)], GREEN, LIGHT_GREEN, outline=DARK_GRAY)
        c.fill_rect(18, 22, 29, 25, WHITE)
        c.rect(18, 22, 29, 25, DARK_GRAY)
        c.blit_sprite(HEAD_UNTER_LEAF, 14, 4)
        c.fill_rect(28, 18, 55, 20, YELLOW, BROWN, mode='hstripe')
        c.rect(28, 18, 55, 20, DARK_GRAY)
        c.fill_ellipse(37, 20, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(46, 20, 2, 2, WHITE, outline=DARK_GRAY)
        # Side-profile walking legs stepping right (both boots pointing RIGHT)
        c.fill_poly([(16, 54), (24, 54), (23, 73), (15, 73)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(24, 54), (33, 54), (39, 73), (30, 73)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(15, 72), (23, 72), (22, 89), (15, 89)], CYAN, BLUE, outline=BLUE)
        c.fill_ellipse(21, 88, 5, 2, CYAN, BLUE, outline=BLUE)
        c.fill_poly([(31, 72), (39, 72), (40, 89), (32, 89)], CYAN, BLUE, outline=BLUE)
        c.fill_ellipse(39, 88, 5, 2, CYAN, BLUE, outline=BLUE)
        _bury_boots_in_turf(c, [20, 38])
        c.thick_line(9, 79, 9, 88, BROWN, 2)
        c.line(9, 84, 6, 81, GREEN)
        c.line(9, 84, 13, 81, LIGHT_GREEN)
        draw_suit(c, 1, 9, 75, 'v')

    elif suit == 2:  # Bell Unter: True side-profile marching RIGHT, holding halberd/sword forward in front of chest!
        # Flowing blue cape streaming behind back on left (x=5..21, y=24..60)
        c.fill_poly([(14, 24), (24, 25), (18, 60), (5, 54)], CYAN, BLUE, outline=BLUE)
        # Narrow side-profile torso at x=15..29, y=24..52 (facing RIGHT)
        c.fill_poly([(15, 24), (29, 25), (31, 52), (15, 52)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(22, 25), (29, 25), (31, 52), (23, 52)], YELLOW, BROWN, outline=BROWN)
        c.fill_rect(15, 48, 31, 51, CYAN, BLUE, mode='hstripe')
        # Both arms reaching forward to the RIGHT (x=24..44, y=26..40) holding a greatsword diagonally in front!
        c.fill_poly([(22, 26), (28, 26), (41, 33), (37, 37)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(25, 31), (30, 31), (43, 39), (38, 43)], YELLOW, BROWN, outline=BROWN)
        c.fill_ellipse(40, 35, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(42, 41, 2, 2, WHITE, outline=DARK_GRAY)
        # Diagonal steel greatsword held in front of body on the right (from x=36, y=46 up-right to x=55, y=8)
        c.fill_poly([(37, 45), (53, 8), (56, 9), (40, 46)], LIGHT_CYAN, WHITE, outline=BLUE)
        c.line(36, 37, 45, 41, YELLOW)
        # Side-profile walking legs stepping right (x=15..39, y=52..89) - BOTH boots point RIGHT!
        c.fill_poly([(15, 52), (23, 52), (21, 72), (13, 72)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(23, 52), (31, 52), (38, 72), (29, 72)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(13, 71), (21, 71), (20, 89), (13, 89)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(19, 88, 5, 2, LIGHT_RED, RED, outline=RED)
        c.fill_poly([(30, 71), (38, 71), (39, 89), (31, 89)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(38, 88, 5, 2, LIGHT_RED, RED, outline=RED)
        _bury_boots_in_turf(c, [18, 37])
        # Collar & profile head at x=13..33 looking right
        c.fill_rect(17, 22, 28, 25, YELLOW)
        c.rect(17, 22, 28, 25, DARK_GRAY)
        c.blit_sprite(HEAD_UNTER_BELL, 13, 4)
        # Lower Bell pip nestled directly in the grass on the right at x=50, y=80
        draw_suit(c, 2, 50, 80)
        _bury_boots_in_turf(c, [50])

    else:  # Heart Unter: Side profile walking LEFT, holding falcon in front on left & staff behind (BOTH boots point LEFT!)
        # Scarlet cloak streaming right behind back (x=36..56, y=24..62)
        c.fill_poly([(32, 24), (45, 24), (56, 58), (39, 62)], LIGHT_RED, RED, outline=RED)
        # Narrow side-profile azure & gold tunic at x=28..44, y=24..52 (facing LEFT)
        c.fill_poly([(29, 25), (44, 24), (44, 52), (27, 52)], CYAN, BLUE, outline=BLUE)
        for ty in range(28, 48, 5):
            c.line(29, ty, 41, ty, YELLOW)
        c.fill_rect(27, 48, 44, 51, YELLOW, BROWN, mode='hstripe')
        # Forward arms reaching LEFT holding perched falcon on gauntlet (x=10..29, y=22..40)
        c.fill_poly([(29, 26), (35, 26), (21, 38), (16, 35)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(12, 24), (19, 22), (20, 34), (13, 35)], BROWN, YELLOW, outline=DARK_GRAY)
        c.fill_ellipse(16, 21, 2, 2, WHITE, YELLOW, outline=DARK_GRAY)
        c.put(13, 21, YELLOW)
        c.fill_ellipse(18, 36, 2, 2, YELLOW, outline=BROWN)
        # Side-profile walking legs stepping LEFT (front leg x=21..30, back leg x=35..44) - BOTH boots point LEFT!
        c.fill_poly([(27, 52), (36, 52), (29, 72), (20, 72)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(35, 52), (44, 52), (45, 72), (37, 72)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(20, 71), (28, 71), (27, 89), (19, 89)], CYAN, BLUE, outline=BLUE)
        c.fill_ellipse(20, 88, 5, 2, CYAN, BLUE, outline=BLUE)
        c.fill_poly([(37, 71), (45, 71), (44, 89), (36, 89)], CYAN, BLUE, outline=BLUE)
        c.fill_ellipse(37, 88, 5, 2, CYAN, BLUE, outline=BLUE)
        _bury_boots_in_turf(c, [21, 38])
        # Collar & profile head at x=25..45 looking left
        c.fill_rect(30, 22, 41, 25, WHITE)
        c.rect(30, 22, 41, 25, DARK_GRAY)
        c.blit_sprite(HEAD_UNTER_HEART, 25, 4)
        # Lower Heart pip nestled directly in the grass on the left at x=10, y=80
        draw_suit(c, 3, 10, 80)
        _bury_boots_in_turf(c, [10])


def draw_ober(c, suit):
    """Draws the 4 Svršek (Ober) cards in side-profile / 3/4 striding poses with both feet pointing in the walking direction."""
    draw_pedestal(c, suit, is_king=False)
    draw_suit(c, suit, 11, 12, 'v')

    if suit == 0:  # Acorn Ober: Striding LEFT in 3/4 profile, greatsword held diagonally across chest (both boots point LEFT)
        c.fill_poly([(31, 24), (48, 24), (56, 64), (36, 68)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        c.fill_poly([(25, 25), (43, 24), (42, 58), (22, 58)], LIGHT_RED, RED, outline=RED)
        for ty in range(28, 50, 5):
            c.line(25, ty, 39, ty, YELLOW)
        c.fill_ellipse(46, 38, 6, 6, YELLOW, BROWN, outline=BROWN)
        c.fill_ellipse(46, 38, 3, 3, GREEN, DARK_GRAY, outline=BROWN)
        c.fill_poly([(21, 26), (27, 25), (17, 41), (12, 38)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(39, 25), (45, 26), (47, 45), (41, 47)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(7, 23), (44, 48), (43, 51), (6, 26)], LIGHT_CYAN, WHITE, outline=BLUE)
        c.line(37, 41, 42, 49, YELLOW)
        # Both legs & riding boots striding LEFT
        c.fill_poly([(22, 58), (31, 58), (26, 73), (17, 73)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        c.fill_poly([(32, 58), (42, 58), (43, 73), (34, 73)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        c.fill_poly([(17, 72), (25, 72), (24, 89), (16, 89)], YELLOW, BROWN, outline=BROWN)
        c.fill_ellipse(17, 88, 5, 2, YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(34, 72), (42, 72), (42, 89), (34, 89)], YELLOW, BROWN, outline=BROWN)
        c.fill_ellipse(35, 88, 5, 2, YELLOW, BROWN, outline=BROWN)
        _bury_boots_in_turf(c, [18, 36])
        c.fill_ellipse(15, 38, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(42, 46, 2, 2, WHITE, outline=DARK_GRAY)
        draw_ermine_collar(c, 34, 22, 14, 4)
        c.blit_sprite(HEAD_OBER_ACORN, 24, 4)

    elif suit == 1:  # Leaf Ober: Side profile facing LEFT, beating side-drum (both boots point LEFT)
        c.fill_poly([(31, 24), (48, 24), (56, 64), (36, 68)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(25, 25), (44, 24), (43, 58), (22, 58)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        c.fill_poly([(26, 26), (36, 26), (35, 48), (25, 48)], YELLOW, BROWN, outline=BROWN)
        c.fill_rect(5, 44, 24, 66, YELLOW, BROWN, mode='vstripe')
        c.rect(5, 44, 24, 66, DARK_GRAY)
        c.fill_rect(5, 43, 24, 46, LIGHT_RED, RED, mode='hstripe')
        c.fill_rect(5, 64, 24, 67, LIGHT_RED, RED, mode='hstripe')
        c.line(6, 46, 12, 64, WHITE)
        c.line(12, 64, 18, 46, WHITE)
        c.line(18, 46, 23, 64, WHITE)
        c.fill_poly([(21, 26), (26, 25), (16, 39), (11, 37)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(39, 25), (45, 26), (36, 41), (31, 39)], LIGHT_RED, RED, outline=RED)
        c.line(13, 38, 11, 43, BROWN)
        c.line(32, 40, 17, 43, BROWN)
        c.fill_poly([(23, 58), (32, 58), (28, 73), (19, 73)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(33, 58), (42, 58), (44, 73), (35, 73)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(19, 72), (27, 72), (26, 89), (18, 89)], CYAN, BLUE, outline=BLUE)
        c.fill_ellipse(19, 88, 5, 2, CYAN, BLUE, outline=BLUE)
        c.fill_poly([(35, 72), (43, 72), (43, 89), (35, 89)], CYAN, BLUE, outline=BLUE)
        c.fill_ellipse(36, 88, 5, 2, CYAN, BLUE, outline=BLUE)
        _bury_boots_in_turf(c, [20, 37])
        c.fill_ellipse(13, 38, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(32, 40, 2, 2, WHITE, outline=DARK_GRAY)
        draw_ermine_collar(c, 35, 22, 14, 4)
        c.blit_sprite(HEAD_OBER_LEAF, 25, 4)

    elif suit == 2:  # Bell Ober: Side profile facing LEFT, rounded breastplate & horizontal sword (both boots point LEFT)
        c.fill_poly([(30, 24), (49, 24), (56, 64), (35, 68)], CYAN, BLUE, outline=BLUE)
        # Curved side-profile breastplate (rounded chest on left at x=21..39, NOT a flat rectangle!)
        c.fill_poly([(25, 25), (41, 24), (40, 48), (22, 48), (19, 36)], YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_poly([(26, 26), (38, 26), (37, 46), (23, 46), (21, 36)], LIGHT_CYAN, CYAN, outline=BLUE)
        c.fill_poly([(21, 48), (42, 48), (44, 62), (18, 62)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(6, 45), (41, 51), (41, 54), (6, 48)], LIGHT_CYAN, WHITE, outline=BLUE)
        c.line(35, 48, 35, 56, YELLOW)
        c.fill_poly([(28, 26), (34, 26), (22, 43), (17, 40)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(40, 25), (46, 25), (52, 40), (46, 42)], LIGHT_RED, RED, outline=RED)
        c.line(51, 16, 51, 44, BROWN)
        c.fill_poly([(47, 16), (51, 11), (55, 16), (51, 22)], LIGHT_CYAN, BLUE, outline=BLUE)
        # Both legs & boots stepping LEFT
        c.fill_poly([(20, 62), (29, 62), (25, 73), (16, 73)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(32, 62), (41, 62), (43, 73), (34, 73)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(16, 72), (24, 72), (23, 89), (15, 89)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(16, 88, 5, 2, LIGHT_RED, RED, outline=RED)
        c.fill_poly([(34, 72), (42, 72), (42, 89), (34, 89)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(35, 88, 5, 2, LIGHT_RED, RED, outline=RED)
        _bury_boots_in_turf(c, [17, 36])
        c.fill_ellipse(19, 41, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(49, 39, 2, 2, WHITE, outline=DARK_GRAY)
        draw_ermine_collar(c, 34, 22, 14, 4)
        c.blit_sprite(HEAD_OBER_BELL, 24, 4)

    else:  # Heart Ober: Side profile walking RIGHT, raising golden chalice in front on right (both boots point RIGHT!)
        # Crimson mantle streaming back-left (x=5..26, y=24..68)
        c.fill_poly([(14, 24), (29, 24), (23, 68), (5, 64)], LIGHT_RED, RED, outline=RED)
        # Diagonal spear held behind back from lower-left (x=10, y=86) to upper-right (x=53, y=8)
        c.thick_line(10, 86, 51, 14, BROWN, 2)
        c.fill_poly([(51, 14), (55, 6), (53, 16), (48, 13)], LIGHT_CYAN, WHITE, outline=BLUE)
        # Narrow side-profile gold & emerald dalmatic angled RIGHT (x=17..35, y=24..62)
        c.fill_poly([(17, 24), (34, 25), (37, 62), (17, 62)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(24, 26), (34, 26), (36, 62), (26, 62)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        # Forward right arm extended right raising golden chalice at x=45..55, y=28..41
        c.fill_poly([(28, 26), (34, 26), (48, 38), (42, 41)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(45, 28), (53, 28), (51, 35), (47, 35)], YELLOW, WHITE, outline=BROWN)
        c.line(49, 35, 49, 40, YELLOW)
        # Side-profile legs & red boots stepping RIGHT (both boots point RIGHT!)
        c.fill_poly([(17, 62), (25, 62), (24, 74), (16, 74)], LIGHT_CYAN, CYAN, outline=BLUE)
        c.fill_poly([(27, 62), (36, 62), (41, 74), (32, 74)], LIGHT_CYAN, CYAN, outline=BLUE)
        c.fill_poly([(16, 73), (24, 73), (24, 89), (16, 89)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(22, 88, 5, 2, LIGHT_RED, RED, outline=RED)
        c.fill_poly([(32, 73), (40, 73), (41, 89), (33, 89)], LIGHT_RED, RED, outline=RED)
        c.fill_ellipse(39, 88, 5, 2, LIGHT_RED, RED, outline=RED)
        _bury_boots_in_turf(c, [21, 38])
        c.fill_ellipse(47, 39, 2, 2, WHITE, outline=DARK_GRAY)
        draw_ermine_collar(c, 25, 22, 14, 4)
        c.blit_sprite(HEAD_OBER_HEART, 15, 4)


def draw_king(c, suit):
    """Draws the 4 Enthroned Král (King) cards in side-seated profile/3/4 view with carved wooden thrones."""
    draw_pedestal(c, suit, is_king=True)
    draw_suit(c, suit, 11, 12, 'v')
    draw_suit(c, suit, 49, 12, 'v')

    if suit == 0:  # Acorn King: Seated on carved wooden throne at LEFT, body & knees in profile facing RIGHT
        # Carved golden-oak throne post on left (x=6..18, y=22..86)
        c.fill_poly([(6, 23), (18, 26), (18, 86), (6, 86)], YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_ellipse(10, 22, 3, 3, YELLOW, BROWN, outline=DARK_GRAY)
        # Side-profile torso seated on left (x=14..33, y=24..55), leaning right
        c.fill_poly([(14, 25), (32, 26), (35, 55), (13, 55)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        draw_ermine_collar(c, 24, 22, 16, 4)
        # Seated thighs & lower legs bent at knee (thighs horizontal x=15..46, y=52..64; calves vertical x=34..48, y=62..86)
        c.fill_poly([(14, 52), (45, 54), (47, 66), (15, 64)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(32, 60), (47, 60), (46, 86), (30, 86)], YELLOW, BROWN, outline=BROWN)
        c.thick_line(22, 53, 44, 62, WHITE, 2)
        # Forward arms reaching right holding Acorn sceptre & orb
        c.fill_poly([(24, 28), (31, 28), (44, 42), (38, 45)], LIGHT_RED, RED, outline=RED)
        c.thick_line(40, 48, 53, 25, YELLOW, 2)
        c.fill_ellipse(53, 24, 3, 3, GREEN, LIGHT_GREEN, outline=DARK_GRAY)
        c.fill_ellipse(42, 43, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(41, 86, 5, 2, RED, LIGHT_RED, outline=RED)
        _bury_boots_in_turf(c, [40])
        c.blit_sprite(HEAD_KING_ACORN, 15, 4)

    elif suit == 1:  # Leaf King: Seated on carved wooden throne at RIGHT, body & knees in profile facing LEFT
        c.fill_poly([(42, 26), (54, 23), (54, 86), (42, 86)], YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_ellipse(50, 22, 3, 3, YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_poly([(28, 26), (46, 25), (47, 55), (25, 55)], LIGHT_RED, RED, outline=RED)
        draw_ermine_collar(c, 36, 22, 16, 4)
        # Seated thighs extending left to knee at x=14, then vertical calves down at x=13..28
        c.fill_poly([(15, 54), (46, 52), (45, 64), (13, 66)], GREEN, DARK_GRAY, outline=DARK_GRAY)
        c.fill_poly([(13, 60), (28, 60), (30, 86), (14, 86)], CYAN, BLUE, outline=BLUE)
        c.thick_line(38, 53, 16, 62, YELLOW, 2)
        c.fill_poly([(29, 28), (36, 28), (22, 45), (16, 42)], YELLOW, BROWN, outline=BROWN)
        c.thick_line(20, 48, 7, 25, YELLOW, 2)
        c.fill_poly([(7, 21), (11, 25), (7, 27), (3, 25)], YELLOW, WHITE, outline=BROWN)
        c.fill_ellipse(18, 43, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(19, 86, 5, 2, YELLOW, BROWN, outline=BROWN)
        _bury_boots_in_turf(c, [20])
        c.blit_sprite(HEAD_KING_LEAF, 25, 4)

    elif suit == 2:  # Bell King: Seated on carved golden throne at RIGHT, side-profile facing LEFT (like Original Card 22)
        c.fill_poly([(42, 26), (54, 23), (54, 86), (42, 86)], YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_ellipse(50, 22, 3, 3, YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_poly([(28, 26), (45, 25), (46, 54), (24, 54)], CYAN, BLUE, outline=BLUE)
        draw_ermine_collar(c, 36, 22, 16, 4)
        # Seated thighs extending left to knee at x=13, calves down to x=13..28
        c.fill_poly([(14, 54), (45, 52), (44, 64), (12, 66)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(13, 60), (28, 60), (29, 86), (14, 86)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(28, 28), (35, 28), (20, 45), (14, 42)], LIGHT_RED, RED, outline=RED)
        c.fill_rect(10, 22, 12, 50, LIGHT_CYAN, WHITE, mode='vstripe')
        c.rect(10, 22, 12, 50, BLUE)
        c.fill_rect(7, 48, 15, 50, YELLOW)
        c.fill_ellipse(15, 44, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(19, 86, 5, 2, LIGHT_RED, RED, outline=RED)
        _bury_boots_in_turf(c, [20])
        c.blit_sprite(HEAD_KING_BELL, 25, 4)

    else:  # Heart King: Seated on carved wooden throne at LEFT, side-profile facing RIGHT, raising golden chalice
        c.fill_poly([(6, 23), (18, 26), (18, 86), (6, 86)], YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_ellipse(10, 22, 3, 3, YELLOW, BROWN, outline=DARK_GRAY)
        c.fill_poly([(14, 25), (32, 26), (35, 55), (13, 55)], CYAN, BLUE, outline=BLUE)
        draw_ermine_collar(c, 24, 22, 16, 4)
        # Seated thighs extending right to knee at x=47, calves down to x=31..46
        c.fill_poly([(14, 52), (45, 54), (47, 66), (15, 64)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(32, 60), (47, 60), (46, 86), (30, 86)], YELLOW, BROWN, outline=BROWN)
        c.fill_poly([(25, 28), (32, 28), (47, 40), (41, 43)], LIGHT_RED, RED, outline=RED)
        c.fill_poly([(45, 29), (53, 29), (51, 36), (47, 36)], YELLOW, WHITE, outline=BROWN)
        c.line(49, 36, 49, 41, YELLOW)
        c.line(46, 41, 52, 41, BROWN)
        c.fill_ellipse(46, 41, 2, 2, WHITE, outline=DARK_GRAY)
        c.fill_ellipse(41, 86, 5, 2, LIGHT_RED, RED, outline=RED)
        _bury_boots_in_turf(c, [40])
        c.blit_sprite(HEAD_KING_HEART, 15, 4)


def draw_court_card(c, suit, rank):
    """Draws a court card: rank 4=Under, 5=Over, 6=King."""
    if rank == 4:
        draw_unter(c, suit)
    elif rank == 5:
        draw_ober(c, suit)
    else:
        draw_king(c, suit)
