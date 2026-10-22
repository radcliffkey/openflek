"""Number cards (7, 8, 9, 10) and their 16 large, high-detail EGA pixel-art vignettes."""

from scripts.deck_gen import animals, people
from scripts.deck_gen.palette import (
    BROWN,
    DARK_GRAY,
    GREEN,
    LIGHT_GREEN,
    LIGHT_RED,
    YELLOW,
)
from scripts.deck_gen.symbols import (
    draw_floret,
    draw_roman_x,
    draw_suit,
    draw_tree_trunk,
)

# Large, richly detailed EGA vignette sprites (width 22..44, height 18..31)
# modelled on the scale and craft of the 1992 deck_data.bin pip scenes.
# People and animals are drawn by `people` and `animals` instead, from jointed shapes.

# Acorn 7 right side: Timbered hillside cottage (roubenka) with smoking chimney (23x23)
SPRITE_COTTAGE = [
    '...............77......',
    '........444444.87......',
    '......44cccccc4868.....',
    '....44cccc44ccc468.....',
    '..44cccc44cccc44c44....',
    '.4cccccc44cccc44cccc4..',
    '84444444444444444444448',
    '.866e66e66e66e66e66ee8.',
    '.8ee66e66e66e66e66eee8.',
    '.866888886e668888866e8.',
    '.8ee8b9b86e668eee8eee8.',
    '.86689b986e668e6e866e8.',
    '.8ee888886e668e688eee8.',
    '.866e66e66e668e6e866e8.',
    '.8ee66e66e66e8e6e8eee8.',
    '8866e66e66e668e6e866e88',
    '87777777777778666877778',
    '8f77877f77877866687f778',
    '87777777777778888877778',
]

# Bell 7: Ornate crimson-and-gold Renaissance garden urn with blooming rose bush (26x26)
SPRITE_POTTED_ROSE = [
    '...........4cc4...........',
    '..........4cccc4..........',
    '.........4ccfecc4.........',
    '....2a2...4cccc4...2a2....',
    '...2aaa2...8228...2aaa2...',
    '....828..882aa288..828....',
    '..4c4828822aaaa2288284c4..',
    '.4ccc48222aa22aa22284ccc4.',
    '..4c4..822a2882a228..4c4..',
    '........8822882288........',
    '......88eeeeeeeeee88......',
    '.....8eeeeeeeeeeeeee8.....',
    '....8844cccccccccc4488....',
    '...8e4cccccccccccccc4e8...',
    '...8e4cc44ee44ee44cc4e8...',
    '....84cc4eee44eee4cc48....',
    '.....84cc44cccc44cc48.....',
    '......84cccccccccc48......',
    '.......884cccccc488.......',
    '.........88eeee88.........',
    '........88eeeeee88........',
    '.......84cccccccc48.......',
    '......84cccccccccc48......',
    '......88888888888888......',
]

# Heart 7: Large coopered wooden barrel/tub overflowing with rose foliage & heart bloom (28x27)
SPRITE_HEART_TUB = [
    '...........44..44...........',
    '.........44cc44cc44.........',
    '........4cccccccccc4........',
    '........4cccccccccc4........',
    '.........4cccccccc4.........',
    '....2a2...4cccccc4...2a2....',
    '...2aaa2...4cccc4...2aaa2...',
    '..22aaa22...4444...22aaa22..',
    '.8222a2228888228888222a2228.',
    '822aaaaaaa22aaaa22aaaaaaa228',
    '.8222aaa222aaaaaaa222aaa2228',
    '..8822222aaaaaaaaaa2222288..',
    '....88888888888888888888....',
    '...866ee668ee66ee866ee668...',
    '...8888888888888888888888...',
    '...8e66e668ee66ee866e66e8...',
    '....866e668ee66ee866e668....',
    '....8e66e68ee66ee86e66e8....',
    '....88888888888888888888....',
    '.....866e68ee66ee86e668.....',
    '.....8e66e8ee66ee8e66e8.....',
    '.....866e68ee66ee86e668.....',
    '.....888888888888888888.....',
]

# Heart 8: Grand tiered Baroque fountain with triple cyan water jets & carved basin (36x28)
SPRITE_FOUNTAIN = [
    '..........3b3....3b3....3b3.........',
    '.........3b9b3..3b9b3..3b9b3........',
    '........3b3.3b3..3b3..3b3.3b3.......',
    '........3b3..3b3.3b3.3b3..3b3.......',
    '........3b3...3b33b33b3...3b3.......',
    '........3b3..887fffff788..3b3.......',
    '........3b3.87fffffffff78.3b3.......',
    '.........3b8877fffffff7788b3........',
    '............88877fff77888...........',
    '...............87fff78..............',
    '...............87fff78..............',
    '......888......87fff78......888.....',
    '.....8fff8....887fff788....8fff8....',
    '....8e8ff8..8833bbbbb3388..8ff8e8...',
    '.....8ff888833bbbbbbbbb338888ff8....',
    '....8ffffffffb3b3b3b3b3bffffffff8...',
    '....87ffffff73b3b3b3b3b37ffffff78...',
    '....88777777883333333338877777788...',
    '.....8844ccccccccccccccccccc4488....',
    '....84ccccccccccccccccccccccccc48...',
    '....84cc44ee44ee44ee44ee44ee4cc48...',
    '...84ccc4eee44eee44eee44eee4ccc48...',
    '..84cccc44444444444444444444cccc48..',
    '..88888888888888888888888888888888..',
]

# Heart 9 left: Golden garden obelisk beside the peacock (14x15)
SPRITE_OBELISK = [
    '.....6e6......',
    '....8eee8.....',
    '....8e4e8.....',
    '...8ee4ee8....',
    '...8e4c4e8....',
    '..8ee4c4ee8...',
    '..8e4ccc4e8...',
    '.8ee4ccc4ee8..',
    '.8e4ccccc4e8..',
    '8ee4ccccc4ee8.',
    '8eeeeeeeeeee8.',
    '8444444444448.',
    '877fffffff778.',
    '87fffffffff78.',
    '8888888888888.',
]

# Heart 10 left: Heart target on a post for Cupid to aim at (9x16)
SPRITE_HEART_POST = [
    '....66...',
    '...6ee6..',
    '..44ee44.',
    '.4cccccc4',
    '.4cccccc4',
    '..4cccc4.',
    '...4cc4..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '...6ee6..',
    '..86ee68.',
    '..888888.',
]


def draw_ground(c, suit, rank):
    """Draws rich, multi-layered organic landscape terrain at the bottom (y=80..97)."""
    import math
    for y in range(80, 98):
        for x in range(2, 59):
            if not c.in_interior(x, y):
                continue
            # Rolling multi-hill contour so terrain looks natural rather than a flat stage line
            wave = int(round(math.sin((x + suit * 7 + rank * 5) * 0.22) * 2.0))
            hill_y = 84 + wave
            if y < hill_y:
                continue
            if y == hill_y:
                col = DARK_GRAY
            elif suit == 0:  # Acorns: mossy woodland hills & winding golden forest path
                if abs(x - (29 + (y - 86))) <= 10 and y >= 88:
                    col = YELLOW if ((x + y) & 1) == 0 else BROWN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            elif suit == 1:  # Leaves: lush emerald hills & sunlit meadow clearing
                if y >= 89 and abs(x - 31) <= 14:
                    col = YELLOW if ((x + y) & 1) == 0 else LIGHT_GREEN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            elif suit == 2:  # Bells: rolling green turf & golden road
                if y >= 88 and abs(x - 30) <= 16:
                    col = YELLOW if ((x + y) & 1) == 0 else BROWN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            else:  # Hearts: terraced garden hills & golden parterre
                if y >= 90:
                    col = YELLOW if ((x + y) & 1) == 0 else LIGHT_GREEN
                else:
                    col = GREEN if ((x + y) & 1) == 0 else LIGHT_GREEN
            c.put(x, y, col)


def draw_fir(c, cx, base_y, h):
    """Draws a layered pixel-art conifer tree rooted into the ground at base_y..base_y+2."""
    c.fill_rect(cx - 2, base_y - 3, cx + 2, base_y + 1, BROWN, DARK_GRAY, mode='vstripe')
    c.fill_poly(
        [(cx - 6, base_y + 1), (cx - 4, base_y - 2), (cx + 4, base_y - 2), (cx + 6, base_y + 1)],
        GREEN,
        DARK_GRAY,
        outline=DARK_GRAY,
        mode='checker',
    )
    tiers = 3
    for t in range(tiers):
        ty0 = base_y - h + t * (h // 4)
        ty1 = base_y - 1 - (tiers - 1 - t) * (h // 5)
        w = 2 + t * 2
        pts = [(cx, ty0), (cx - w - 2, ty1), (cx + w + 2, ty1)]
        c.fill_poly(pts, GREEN, DARK_GRAY, outline=DARK_GRAY, mode='checker')
        c.line(cx, ty0 + 1, cx - w, ty1 - 1, LIGHT_GREEN)


def draw_bush_or_flowers(c, cx, base_y, col):
    """Draws a flat-bottomed flowering bush rooted directly into base_y..base_y+1."""
    pts = [
        (cx - 6, base_y + 1),
        (cx - 5, base_y - 3),
        (cx - 2, base_y - 6),
        (cx + 2, base_y - 6),
        (cx + 5, base_y - 3),
        (cx + 6, base_y + 1),
    ]
    c.fill_poly(pts, GREEN, DARK_GRAY, outline=DARK_GRAY, mode='checker')
    for dx, dy in [(-3, -3), (0, -5), (3, -3), (-1, -2), (2, -4)]:
        c.put(cx + dx, base_y + dy, col)
    c.put(cx, base_y - 3, YELLOW)


def draw_vignette_scene(c, suit, rank):
    """Draws one of the 16 large, grounded bottom scenes (y=60..91).

    Animals are scaled so they stay below the lowest pips of their card.
    """
    draw_ground(c, suit, rank)
    gy = 88

    if (suit, rank) == (0, 0):  # Acorn 7: Forester smoking a pipe beside a timbered cottage
        draw_bush_or_flowers(c, 8, gy, LIGHT_RED)
        c.blit_sprite(SPRITE_COTTAGE, 35, gy - 16)
        people.draw_forester(c)
    elif (suit, rank) == (0, 1):  # Acorn 8: Huntsman sitting in the grass blowing his horn, his dog by him
        people.draw_hornblower(c)
        animals.draw_dog(c, dx=3)
    elif (suit, rank) == (0, 2):  # Acorn 9: Cock pheasant perched on an oak bough
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 51, gy, YELLOW)
        animals.draw_pheasant(c, scale=0.75)
    elif (suit, rank) == (0, 3):  # Acorn 10: Wild boar trotting across a forest clearing
        draw_bush_or_flowers(c, 9, gy, YELLOW)
        draw_bush_or_flowers(c, 52, gy, LIGHT_RED)
        animals.draw_boar(c, scale=0.7)

    elif (suit, rank) == (1, 0):  # Leaf 7: Jester dancing with a sword raised overhead
        draw_bush_or_flowers(c, 10, gy, YELLOW)
        draw_bush_or_flowers(c, 50, gy, LIGHT_RED)
        people.draw_sword_dancer(c)
    elif (suit, rank) == (1, 1):  # Leaf 8: Elephant walking, trunk curled
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 52, gy, YELLOW)
        animals.draw_elephant(c, scale=0.8)
    elif (suit, rank) == (1, 2):  # Leaf 9: Red stag in mid-leap
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 51, gy, YELLOW)
        animals.draw_stag(c, dx=2, scale=0.62)
    elif (suit, rank) == (1, 3):  # Leaf 10: Lion couchant facing right
        animals.draw_lion(c, scale=0.72)

    elif (suit, rank) == (2, 0):  # Bell 7: Large ornate potted rose bush on mound
        draw_bush_or_flowers(c, 10, gy, YELLOW)
        draw_bush_or_flowers(c, 50, gy, YELLOW)
        c.blit_sprite(SPRITE_POTTED_ROSE, 17, gy - 21)
    elif (suit, rank) == (2, 1):  # Bell 8: Coursing hound with red collar
        draw_bush_or_flowers(c, 9, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 52, gy, YELLOW)
        animals.draw_hound(c, scale=0.85)
    elif (suit, rank) == (2, 2):  # Bell 9: Saddled dapple-grey horse tethered to a post
        c.fill_rect(6, 66, 8, gy - 1, BROWN, YELLOW, mode='vstripe')
        c.rect(5, 66, 9, gy - 1, DARK_GRAY)
        c.fill_rect(4, 64, 10, 65, YELLOW)
        c.rect(4, 64, 10, 65, BROWN)
        c.line(10, 67, 19, 68, BROWN)
        animals.draw_horse(c, flip=True, dx=4, scale=0.75)
    elif (suit, rank) == (2, 3):  # Bell 10: Village band of trumpeter, drummer and fiddler
        people.draw_musicians(c)

    elif (suit, rank) == (3, 0):  # Heart 7: Large coopered rose-tub with heart bloom
        draw_bush_or_flowers(c, 9, gy, YELLOW)
        draw_bush_or_flowers(c, 51, gy, YELLOW)
        c.blit_sprite(SPRITE_HEART_TUB, 16, gy - 20)
    elif (suit, rank) == (3, 1):  # Heart 8: Grand tiered Baroque fountain spraying water
        draw_bush_or_flowers(c, 8, gy, LIGHT_RED)
        draw_bush_or_flowers(c, 52, gy, LIGHT_RED)
        c.blit_sprite(SPRITE_FOUNTAIN, 12, gy - 21)
    elif (suit, rank) == (3, 2):  # Heart 9: Peacock in display beside a garden obelisk
        c.blit_sprite(SPRITE_OBELISK, 4, gy - 13)
        animals.draw_peacock(c, dx=10)
    elif (suit, rank) == (3, 3):  # Heart 10: Winged Cupid aiming his bow at a heart on a post
        c.blit_sprite(SPRITE_HEART_POST, 9, gy - 14)
        people.draw_cupid(c)


def draw_number_card(c, suit, rank):
    """Draws a complete number card (rank 0=Seven, 1=Eight, 2=Nine, 3=Ten)."""
    is_tree = suit in (0, 1)
    if is_tree:
        if rank == 0:  # Seven: 1 vertical top + 3 pairs
            bys = [24, 38, 52]
            draw_tree_trunk(c, 17, 88, bys, suit)
            draw_suit(c, suit, 30, 11, 'v')
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
        elif rank == 1:  # Eight: 4 pairs + top crown shoot
            bys = [15, 29, 43, 56]
            draw_tree_trunk(c, 10, 88, bys, suit)
            c.line(30, 10, 27, 6, GREEN)
            c.line(30, 10, 30, 5, LIGHT_GREEN)
            c.line(30, 10, 33, 6, GREEN)
            c.put(27, 5, LIGHT_RED)
            c.put(33, 5, LIGHT_RED)
            c.put(30, 4, YELLOW)
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
        elif rank == 2:  # Nine: 1 vertical top + 4 pairs
            bys = [23, 36, 49, 61]
            draw_tree_trunk(c, 16, 88, bys, suit)
            draw_suit(c, suit, 30, 10, 'v')
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
        else:  # Ten: Roman X + 5 pairs
            bys = [16, 28, 40, 52, 64]
            draw_tree_trunk(c, 13, 88, bys, suit)
            draw_roman_x(c, 30, 3)
            for y in bys:
                draw_suit(c, suit, 13, y, 'left')
                draw_suit(c, suit, 47, y, 'right')
    else:
        if rank == 0:  # Seven: 1 center top + 3 pairs
            ys = [24, 39, 54]
            draw_floret(c, 30, 31, suit)
            draw_floret(c, 30, 46, suit)
            draw_suit(c, suit, 30, 12)
            for y in ys:
                draw_suit(c, suit, 13, y)
                draw_suit(c, suit, 47, y)
        elif rank == 1:  # Eight: 4 pairs + central garland
            ys = [13, 27, 41, 55]
            draw_floret(c, 30, 20, suit)
            draw_floret(c, 30, 34, suit)
            draw_floret(c, 30, 48, suit)
            for y in ys:
                draw_suit(c, suit, 13, y)
                draw_suit(c, suit, 47, y)
        elif rank == 2:  # Nine: 3 center + 3 pairs
            for y in [12, 28, 44]:
                draw_suit(c, suit, 30, y)
            for y in [20, 36, 52]:
                draw_suit(c, suit, 12, y)
                draw_suit(c, suit, 48, y)
        else:  # Ten: Roman X + 2 center + 4 pairs
            draw_roman_x(c, 30, 3)
            for y in [21, 41]:
                draw_suit(c, suit, 30, y)
            draw_floret(c, 30, 31, suit)
            draw_floret(c, 30, 51, suit)
            for y in [14, 28, 42, 56]:
                draw_suit(c, suit, 12, y)
                draw_suit(c, suit, 48, y)

    # Draw the bottom vignette scene LAST so large figures/animals sit cleanly in front of tree trunks!
    draw_vignette_scene(c, suit, rank)
