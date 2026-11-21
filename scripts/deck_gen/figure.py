"""Jointed court figures: a skeleton pose dressed in garments, with a 3/4 head.

Poses are written facing right in card coordinates; `Rig(flip=True)`
mirrors them. A figure is about seven heads tall: the face is 11 pixels from
brow to chin, arms reach mid-thigh, and every limb bends at a real joint.

Heads and hats are hand-pixelled templates with placeholder letters:
H/h hair and its shade, e the hair's edge against the skin, L a gloss on
the crown, w eyebrows, J/j beard, C/c hat cloth, T/t trim (feather or
jewel), B/b hat band.
"""

import math

from scripts.deck_gen.palette import (
    BROWN,
    DARK_GRAY,
    LIGHT_CYAN,
    LIGHT_GRAY,
    WHITE,
    YELLOW,
    bresenham,
)
from scripts.deck_gen.rig import AUTO, darker

SKIN = WHITE

# Skin is white, the same index as the card, so the far cheek and the chin of
# a 3/4 face are closed with dark grey. A missing pixel there lets the mouth
# or the chin bleed into the paper. Where the jaw lies against the neck a
# light grey line is enough.
#
# Every head is anchored at column 8, row 7, which lands on the figure's
# head joint. Unters and Obers are turned three quarters to the right: the
# near cheek is broad and ends in an ear, each eye sits under its own brow,
# the nose is a shaded bridge towards the far eye with a dark underside, and
# the face narrows from the cheekbone to the chin. Hair is glossed on the
# crown and meets the skin without a dark seam, which made it a hood.
FACE_YOUNG = [
    '......hhhhhh.....',
    '....hHHHHHHHHh...',
    '...hHHLLHHHHHHh..',
    '..hHHLHHHHHHHHh..',
    '..hHHHeHfHffff8..',
    '.hHHHeffwwffwwf8.',
    '.hHHHeff0ffff0f8.',
    '.hHHHf7ffff7fff8.',
    '.hHHH7fffff7ffc8.',
    '..hHHefffff78f8..',
    '..hHHe7fffffff8..',
    '..hHHHe7ff44f8...',
    '...hHHh.7ffff8...',
    '....hh...7778....',
]

FACE_BEARD = [
    '......hhhhhh.....',
    '....hHHHHHHHHh...',
    '...hHHLLHHHHHHh..',
    '..hHHLHHHHHHHHh..',
    '..hHHHefffffff8..',
    '.hHHHefwwwffwwf8.',
    '.hHHHeff0ffff0f8.',
    '.hHHHf7ffff7fff8.',
    '..hHH7fffff7ffc8.',
    '..hHJJfffff78fJ8.',
    '...jJJJfJJJJJJJj.',
    '...jJJJJJJ44JJj..',
    '....jJJJJJJJJJj..',
    '.....jJJJJJJJj...',
    '.......jjjjj.....',
]

# The wild man on the Acorn Ace: compact 11x11 head proportioned to his
# 0.72-scale body, anchored at (8, 7) like the court heads.
FACE_OLD = [
    '.................',
    '.................',
    '.....hhhhhhh.....',
    '....hHHHHHHHh....',
    '...hHHfffffHh....',
    '...hHfwwfwwf8....',
    '...hHff0ff0f8....',
    '...hHfffffff8....',
    '...hHJJff78Jj....',
    '....jJJJJ44Jj....',
    '....jJJJJJJJj....',
    '.....jJJJJJj.....',
    '......jjjjj......',
]

FACE_MOUSTACHE = [
    '......hhhhhh.....',
    '....hHHHHHHHHh...',
    '...hHHLLHHHHHHh..',
    '..hHHLHHHHHHHHh..',
    '..hHHHefffffff8..',
    '.hHHHefwwwffwwf8.',
    '.hHHHeff0ffff0f8.',
    '.hHHHf7ffff7fff8.',
    '.hHHH7fffff7ffc8.',
    '..hHHefffff78f8..',
    '..hHHe7fJJJJJJ8..',
    '..hHHHe7jJ44Jj8..',
    '...hHHh.7ffff8...',
    '....hh...7778....',
]

FACE_GOATEE = [
    '......hhhhhh.....',
    '....hHHHHHHHHh...',
    '...hHHLLHHHHHHh..',
    '..hHHLHHHHHHHHh..',
    '..hHHHefffffff8..',
    '.hHHHefwwwffwwf8.',
    '.hHHHeff0ffff0f8.',
    '.hHHHf7ffff7fff8.',
    '.hHHH7fffff7ffc8.',
    '..hHHefffff78f8..',
    '..hHHe7fJJJJJJ8..',
    '..hHHHe7jj44jj8..',
    '...hHHh.7jJJj8...',
    '....hh...7jj8....',
    '..........jj.....',
]

# Kings sit facing the viewer, so their heads are turned only a little to the
# right: both sides of the face show, hair falls on either side, and the nose
# sits just right of the middle. A full beard gets a moustache drooping past
# the mouth and a few strands in the shade colour: in flat yellow it reads
# as a clean-shaven chin. The forked beard is long enough for its notch to
# show against the ermine below. The crown hides the top of the head.
KING_CROWN_OF_HEAD = [
    '......hHHHh....',
    '....hHHHHHh....',
    '..hHHHHHHHHHh..',
    '.hHHHHHHHHHHHh.',
]

FACE_KING = KING_CROWN_OF_HEAD + [
    '.hHHffffffffHh.',
    '.hHfwwwffwwwHh.',
    '.hHff0ffff0fHh.',
    '.hHcffff7ffcHh.',
    '.hHfffff78ffHh.',
    '.hHJfJJJJJJJHh.',
    '.hHJJJJ444JJHh.',
    '.hHJJJJJJJJJHh.',
    '..hHJJJJJJJHh..',
    '...hhjjJJjjhh..',
]

# Older kings: clean brow and cheeks, distinguished by fuller sculpted beards.
FACE_KING_OLD = KING_CROWN_OF_HEAD + [
    '.hHHffffffffHh.',
    '.hHfwwwffwwwHh.',
    '.hHff0ffff0fHh.',
    '.hHcffff7ffcHh.',
    '.hHJffff78fJHh.',
    '.hJJjjjjfjjjJh.',
    '.hJjJJ444JJjJh.',
    '.hJjJJJJJJJjJh.',
    '..jJJJjJJJjJj..',
    '..jJJjJJJjJjj..',
    '...jJJJjJjjj...',
    '.....jJJjj.....',
]

FACE_KING_FORKED = KING_CROWN_OF_HEAD + [
    '.hHHffffffffHh.',
    '.hHfwwwffwwwHh.',
    '.hHff0ffff0fHh.',
    '.hHcffff7ffcHh.',
    '.hHJffff78fJHh.',
    '.hJJjjjjfjjjJh.',
    '.hJjJJ444JJjJh.',
    '.hJjJJJJJJJjJh.',
    '..jJJJJjJJJjj..',
    '..jJJjJJJjJjj..',
    '...jJJj.jJJj...',
    '...jJj...jJj...',
    '....jj...jj....',
]

FACES = {
    'young': FACE_YOUNG,
    'beard': FACE_BEARD,
    'old': FACE_OLD,
    'moustache': FACE_MOUSTACHE,
    'goatee': FACE_GOATEE,
    'king': FACE_KING,
    'king_old': FACE_KING_OLD,
    'king_forked': FACE_KING_FORKED,
}

# Hats share the face template's columns; the first row sits `top` rows above
# the face's first row. A hat comes down over the crown of the head to the
# fringe, so the brow still shows under it.
HATS = {
    'cap': (
        -2,
        [
            '..TT...cCCCCc....',
            '...TTtcCCCCCCCc..',
            '....tcCCCCCCCCCc.',
            '...cCCCCCCCCCCCc.',
            '..cCCCCCCCCCCCCc.',
            '..bBBBBBBBBBBBBb.',
        ],
    ),
    'brim': (
        -4,
        [
            '......cCCCCc.....',
            '.....cCCCCCCc....',
            'TTt..cCCCCCCCc...',
            'TTTTtcCCCCCCCc...',
            '.tTTTBBBBBBBBb...',
            '.....cCCCCCCCc...',
            'cCCCCCCCCCCCCCCCc',
            '.ccCCCCCCCCCCCcc.',
        ],
    ),
    'wide_beret': (  # a feather pinned at the brow curls back over the crown
        -4,
        [
            '...TTt...........',
            '....tTTTt........',
            '....ccCCtTTtcc...',
            '..cCCCCCCCCtTtCc.',
            '.cCCCCCCCCCCtTCCc',
            'cCCCCCCCCCCCCtCCc',
            '.ccCCCCccccCCCCc.',
            '...ccbBBBBBBBBb..',
        ],
    ),
    'wreath': (  # oak leaves with acorns, sitting high on the wild man's brow
        0,
        [
            '....cC.T.Cc......',
            '...cCCcCcCCc.....',
            '..cCCcCCcCCc.....',
            '...cc.cc.cc......',
        ],
    ),
    'crown': (
        -3,
        [
            '..T....T....T..',
            '.bBb..bBb..bBb.',
            '.bBBbbBBBbbBBb.',
            'bBCBBBCCCBBBCBb',
            'bBBBBBBBBBBBBBb',
            'bBTBBBBTBBBBTBb',
            '.bbbbbbbbbbbbb.',
        ],
    ),
}


# Open hands for full-size figures, drawn for a forearm pointing forwards
# (right) and mirrored for one pointing back, each with the pixel that sits on
# the wrist. Light grey parts the fingers; the thumb stands off on its own.
OPEN_HANDS = {
    # Raised, palm out, as in greeting.
    'up': (
        [
            '.888..',
            '8f7f8.',
            '8f7f88',
            '8fff8f8',
            '8ffff8.',
            '.8ff8..',
        ],
        (2, 4),
    ),
    # Held out, fingers forward and the thumb on top.
    'out': (
        [
            '.88.....',
            '8ff8888.',
            '8fff7778',
            '8ffffff8',
            '8fff7778',
            '.888888.',
        ],
        (1, 3),
    ),
    # Hanging, or resting on the hip.
    'down': (
        [
            '.888..',
            '8fff8.',
            '8fff88',
            '8f7f8f8',
            '8f7f88.',
            '.888...',
        ],
        (2, 1),
    ),
}


# Heads for figures pixelled by hand at vignette size, on the same
# placeholders; the face centre is column 3, row 3.
SMALL_FACES = {
    'young': [
        '.hHHHh.',
        'hHHHHHH',
        'hHHf0f.',
        'hHfffff',
        '.hffcf.',
        '..fff..',
    ],
    'beard': [
        '.hHHHh.',
        'hHHHHHH',
        'hHHf0f.',
        'hHfffff',
        '.hJJ4J.',
        '..JJJ..',
    ],
}

SMALL_HATS = {
    'cap': (-2, ['T.cCCc..', '.cCCCCCc', '.bBBBBBb']),
    'brim': (-3, ['..cCCc...', 'TcCCCCc..', 'cCCCCCCCc']),
    'beret': (-2, ['..cCCCT.', '.cCCCCCc', '..bBBBb.']),
}


def draw_head(rig, hx, hy, face='young', hair=BROWN, beard=None, hat=None, small=False):
    """Draws a head in 3/4 view facing right with its face centred near (hx, hy).

    `hat` is (kind, cloth, trim, band) with kind from `HATS`. `small` picks
    the small templates, for figures pixelled by hand at vignette size.
    """
    faces, hats, anchor = (SMALL_FACES, SMALL_HATS, (3, 3)) if small else (FACES, HATS, (8, 7))
    beard = beard if beard is not None else hair
    shade = darker(hair)
    subst = {
        'H': hair,
        'h': shade,
        # Dark hair lies straight against the skin; fair hair needs its shade there to show at all.
        'e': hair if shade == DARK_GRAY else shade,
        # A soft white sheen on silver hair; canary yellow on brown hair reads as a patch.
        'L': WHITE if hair == LIGHT_GRAY else hair,
        'w': DARK_GRAY if hair in (LIGHT_GRAY, WHITE) else BROWN,
        'J': beard,
        'j': darker(beard),
    }
    rig.sprite(faces[face], hx, hy, subst, anchor=anchor)
    if hat is not None:
        kind, cloth, trim, band = hat
        top, rows = hats[kind]
        subst = {'C': cloth, 'c': darker(cloth), 'T': trim, 't': darker(trim), 'B': band, 'b': darker(band)}
        rig.sprite(rows, hx, hy, subst, anchor=(anchor[0], anchor[1] - top))


def draw_hand(rig, x, y, grip=False, toward=None):
    """A hand at the end of an arm; `grip` draws a closed fist.

    A little wider than the sleeve end so the cuff doesn't show past it, and
    edged in dark grey: light grey skin shading vanishes on the white card.

    `toward` is the elbow. Given, on a full-size figure, the hand follows
    the forearm rather than being a plain oval: a fist sits a little past the
    wrist with the crease of its curled fingers across the front, and an
    open hand is raised, held out or hanging, fingers and thumb apart.
    """
    if toward is None or rig.s != 1.0:
        if grip:
            rig.part().ellipse(x, y, 2.5, 2.2).paint(SKIN, None, outline=DARK_GRAY)
        else:
            rig.part().ellipse(x, y + 0.5, 2.4, 2.9).paint(SKIN, None, outline=DARK_GRAY)
            rig.put(x - 1, y + 1, LIGHT_GRAY)
        return
    ex, ey = toward
    ln = max(math.hypot(x - ex, y - ey), 1)
    ux, uy = (x - ex) / ln, (y - ey) / ln
    if grip:
        cx, cy = x + ux * 0.8, y + uy * 0.8
        rig.part().ellipse(cx, cy, 2.6, 2.3, angle=math.degrees(math.atan2(uy, ux))).paint(SKIN, None, outline=DARK_GRAY)
        for k in (-1, 0, 1):
            rig.put(cx + ux * 0.8 - uy * k, cy + uy * 0.8 + ux * k, LIGHT_GRAY)
        return
    # An open hand is too small to shape from ellipses, so it is pixelled by
    # hand and picked by the forearm's slope, mirrored when it points backwards.
    slope = math.degrees(math.atan2(uy, abs(ux)))
    rows, anchor = OPEN_HANDS['up' if slope < -30 else 'down' if slope > 45 else 'out']
    if ux < 0:
        width = max(len(row) for row in rows)
        rows = [''.join(reversed(row.ljust(width, '.'))) for row in rows]
        anchor = (width - 1 - anchor[0], anchor[1])
    rig.sprite(rows, x, y, anchor=anchor)


def arm(rig, sh, el, wr, sleeve, cuff=None, upper_r=3.1, puff=None, outline=AUTO):
    """A sleeved arm through shoulder, elbow and wrist.

    `cuff` adds a turned-back cuff at the wrist, `puff` a slashed puffed
    upper sleeve in that colour.
    """
    rig.part().chain([sh, el, wr], [upper_r, 2.5, 2.0]).paint(sleeve, outline=outline)
    ex, ey = el
    wx, wy = wr
    if puff is not None:
        sx, sy = sh
        rig.part().capsule(sx, sy, sx + (ex - sx) * 0.45, sy + (ey - sy) * 0.45, upper_r + 0.6, upper_r).paint(puff)
    if cuff is not None:
        rig.part().capsule(wx + (ex - wx) * 0.22, wy + (ey - wy) * 0.22, wx + (ex - wx) * 0.05, wy + (ey - wy) * 0.05, 2.2).paint(
            cuff
        )


def leg(rig, hip, kn, an, toe, hose, boot, boot_top=0.4, thigh_r=3.8, cuff=None):
    """A leg through hip, knee and ankle, booted from `boot_top` of the shin, the foot pointing at `toe`."""
    rig.part().chain([hip, kn, an], [thigh_r, 2.8, 2.1]).paint(hose)
    kx, ky = kn
    ax, ay = an
    bx, by = kx + (ax - kx) * boot_top, ky + (ay - ky) * boot_top
    tx, ty = toe
    b = rig.part().chain([(bx, by), an], [3.1, 2.5]).capsule(ax, ay + 0.5, tx, ty, 2.3, 1.4)
    b.paint(boot)
    rig.part().ellipse(bx, by, 3.3, 1.4).paint(cuff if cuff is not None else boot)


def torso(rig, j, tunic, skirt, belt, collar=WHITE, pattern=None, skirt_pattern=None, buttons=None):
    """Doublet from shoulders to waist, a pleated skirt to the hem, belt and collar."""
    (sbx, sby), (sfx, sfy) = j['sh_b'], j['sh_f']
    wx, wy = j['waist']
    hem_y = j['hem']
    lean = j.get('lean', 0)
    flare = j.get('flare', 8)
    sk = rig.part().poly([(wx - 5, wy - 1), (wx + 5, wy - 1), (wx + flare + 1 + lean, hem_y), (wx - flare + lean, hem_y)])
    sk.ellipse(wx + lean + 0.5, hem_y, flare + 0.5, 1.6)
    skirt_shade = darker(skirt)

    def pleats(x, y):
        if skirt_pattern is not None:
            p = skirt_pattern(x, y)
            if p is not None:
                return p
        if (x - int(wx)) % 4 == 0 and y > wy + 3:
            return skirt_shade
        return None

    sk.paint(skirt, pattern=pleats)
    # Chest: broad at the shoulders, narrowing to the waist, the breast pushed forward.
    body = rig.part().poly([(sbx - 1, sby - 1), (sfx + 1, sfy - 1), (wx + 4, wy), (wx - 4, wy)])
    body.ellipse((sbx + sfx) / 2 + 1.5, sby + 6, 6.8, 6.4)
    body.paint(tunic, pattern=pattern)
    if buttons is not None:
        bx = (sbx + sfx) / 2 + 3
        for y in range(int(sby + 3), int(wy - 1), 3):
            rig.put(bx + (y - sby) * 0.05, y, buttons)
    rig.part().rect(int(wx - 4), int(wy - 1), int(wx + 5), int(wy + 1)).paint(belt)
    nx, ny = j['neck']
    rig.part().capsule(nx - 1, ny - 2, nx, ny + 1, 1.8).paint(SKIN)
    rig.part().ellipse(nx + 0.5, ny + 1.5, 4.5, 1.8).paint(collar)


def cape(rig, j, col, length=62, swing=-6, lining=None):
    """A cape hanging from the shoulders, flaring backwards by `swing` pixels.

    A fold runs from the shoulder down the flared hem, in the darker colour
    of the cloth, kept off the outline. A wide flare gets a second seam.
    """
    (sbx, sby), (sfx, sfy) = j['sh_b'], j['sh_f']
    p = rig.part().poly(
        [
            (sbx - 1, sby - 2),
            (sfx - 1, sfy - 2),
            (sfx - 2, length - 6),
            (sbx + swing + 7, length),
            (sbx + swing, length - 2),
        ]
    )
    p.ellipse(sbx + swing + 3.5, length - 1.5, 4.5, 2.0)
    p.paint(col)
    fold = darker(col)
    # Interior only: the outline stays a clean rim, and the lines sit on cloth.
    inset = p.interior()
    # The body covers the middle of the cape, so the seams run down the
    # flared back edge, the cloth that actually shows. A wide flare gets
    # a second seam further out; a narrow one would merge the two.
    outer = sbx + swing
    span = abs(swing)
    seams = ((sbx + 1.5, sby + 3, outer + span * 0.62, length - 6),)
    if span >= 8:
        seams = seams + ((sbx - 0.5, sby + 6, outer + 3.0, length - 9),)
    for x0, y0, x1, y1 in seams:
        ax, ay = rig.tx(x0, y0)
        bx, by = rig.tx(x1, y1)
        for x, y in bresenham(ax, ay, bx, by):
            if (x, y) in inset:
                rig.plot(x, y, fold)
    if lining is not None:
        rig.part().poly([(sbx + swing, length - 2), (sbx + swing + 1, length - 10), (sbx + swing + 7, length)]).paint(lining)


def sword(rig, hilt, tip, blade=LIGHT_CYAN, guard=YELLOW):
    """A sword gripped at `hilt` and pointing at `tip`, the crossguard square to the blade."""
    hx, hy = hilt
    tx, ty = tip
    dx, dy = tx - hx, ty - hy
    ln = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / ln, dy / ln
    gx, gy = hx + ux * 2.5, hy + uy * 2.5
    # Keep the dark-blue border unbroken: taper cleanly to the tip and restrict
    # any steel glint strictly to interior pixels that still leave cyan beside them.
    steel = rig.part().capsule(gx, gy, tx, ty, 1.9, 1.15)
    steel.paint(blade, None, outline=darker(darker(blade)))
    inside = steel.interior()
    for x, y in bresenham(*rig.tx(gx + ux, gy + uy), *rig.tx(tx - ux * 2, ty - uy * 2)):
        if (x, y) in inside and ((x + 1, y) in inside or (x, y + 1) in inside):
            rig.plot(x, y, WHITE)
    # Grip, crossguard and pommel: outline the thin gold parts on their outer
    # halo in brown so they stay golden yet read crisply against the white card.
    rig.part().capsule(hx - ux * 2, hy - uy * 2, gx, gy, 0.9).fill(BROWN)
    gilt = rig.part()
    gilt.capsule(gx - uy * 3.5, gy + ux * 3.5, gx + uy * 3.5, gy - ux * 3.5, 0.8)
    gilt.ellipse(hx - ux * 3, hy - uy * 3, 1.1, 1.1)
    edge = darker(guard)
    for x, y in gilt.halo():
        rig.plot(x, y, edge)
    gilt.fill(guard)


def pole(rig, a, b, col=BROWN, outline=None):
    """A staff or shaft from `a` to `b`.

    A wooden shaft is a plain two-pixel line; pass `outline` for a pale one,
    such as a gilded sceptre, so it gets a thicker shaft edged against the
    white card.
    """
    if outline is None:
        rig.part().capsule(*a, *b, 0.8).fill(col)
    else:
        rig.part().capsule(*a, *b, 1.4).paint(col, None, outline=outline)


# Standing pose shared by Unters, Obers and the wild man; each figure
# overrides arms and legs, and may override these joints through `pose`.
BASE = dict(head=(30, 15), neck=(30, 21), sh_b=(23, 26), sh_f=(36, 26), waist=(30, 44), hem=56)


def draw_standing(rig, look, arms, legs, back_props=None, front_props=None, pose=None, back_over=False, head_over=False):
    """Draws a standing figure back to front.

    `look` names the colours (sleeve_b, sleeve_f, hose, boot, tunic, skirt,
    belt, hair, hat and optional extras); `arms` is ((sh, el, wr, hand),
    (sh, el, wr, hand)) for the back and the front arm, where hand is
    'open', 'grip' or None; `legs` is ((hip, knee, ankle, toe), ...) back
    then front. Props are callbacks taking the rig.

    `back_over` draws the back arm over the body instead of behind it, for
    a hand resting on the hip or reaching across the belly, which the body
    would otherwise hide. `head_over` draws the head after both arms, so
    overhead two-handed swings never cover the face.
    """
    j = dict(BASE, **(pose or {}))
    if look.get('cape') is not None:
        cape(rig, j, look['cape'], length=look.get('cape_len', 64), swing=look.get('swing', -7), lining=look.get('lining'))
    if back_props:
        back_props(rig)
    (bsh, bel, bwr, bhand), (fsh, fel, fwr, fhand) = arms

    sleeve_outline = look.get('sleeve_outline', AUTO)

    def back_arm():
        arm(rig, bsh, bel, bwr, look['sleeve_b'], cuff=look.get('cuff'), puff=look.get('puff'), outline=sleeve_outline)
        if bhand:
            draw_hand(rig, *bwr, grip=bhand == 'grip', toward=bel)

    if not back_over:
        back_arm()
    for hip, kn, an, toe in legs:
        leg(
            rig,
            hip,
            kn,
            an,
            toe,
            look['hose'],
            look['boot'],
            boot_top=look.get('boot_top', 0.4),
            cuff=look.get('boot_cuff'),
        )
    torso(
        rig,
        j,
        look['tunic'],
        look['skirt'],
        look['belt'],
        collar=look.get('collar', WHITE),
        pattern=look.get('pattern'),
        skirt_pattern=look.get('skirt_pattern'),
        buttons=look.get('buttons'),
    )
    if back_over:
        back_arm()

    def head():
        draw_head(rig, *j['head'], face=look.get('face', 'young'), hair=look['hair'], beard=look.get('beard'), hat=look['hat'])

    if not head_over:
        head()
    arm(rig, fsh, fel, fwr, look['sleeve_f'], cuff=look.get('cuff'), puff=look.get('puff'), outline=sleeve_outline)
    # Props before the hand, so a fist closes over the grip of whatever it holds.
    if front_props:
        front_props(rig)
    if fhand:
        draw_hand(rig, *fwr, grip=fhand == 'grip', toward=fel)
    if head_over:
        head()
    return rig

