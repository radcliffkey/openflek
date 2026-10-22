"""Jointed court figures: a skeleton pose dressed in garments, with a 3/4 head.

Poses are written facing right in card coordinates; `Rig(flip=True)`
mirrors them. A figure is about seven heads tall: the face is 11 pixels from
brow to chin, arms reach mid-thigh, and every limb bends at a real joint.

Heads and hats are hand-pixelled templates with placeholder letters:
H/h hair and its shade, J/j beard, C/c hat cloth, T/t trim (feather or
jewel), B/b hat band.
"""

from scripts.deck_gen.palette import (
    BROWN,
    LIGHT_CYAN,
    LIGHT_GRAY,
    WHITE,
    YELLOW,
)
from scripts.deck_gen.rig import darker

SKIN = WHITE

FACE_YOUNG = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHffffff7..',
    '.hHHHff8fff87..',
    '.hHHHff0ff0f7..',
    '.hHHHfffffff87.',
    '.hHHHcfffffff7.',
    '.hHHHHfffff877.',
    '.hHHHHffff447..',
    '..hHHH8ffff8...',
    '..hHHHh8888....',
    '...hHh.........',
]

FACE_BEARD = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHffffff7..',
    '.hHHHff8fff87..',
    '.hHHHff0ff0f7..',
    '.hHHHfffffff87.',
    '.hHHHJfffffff7.',
    '.hHHHJffJJJ877.',
    '.hHHHJJJJ44J...',
    '..hHHJJJJJJj...',
    '..hHHjJJJJj....',
    '...hh.jJJj.....',
]

FACE_OLD = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHf7ffff7..',
    '.hHHHf88ff887..',
    '.hHHHff0ff0f7..',
    '.hHHHff7ffff87.',
    '.hHHHJfffffff7.',
    '.hHHJJJJJJJJ77.',
    '.hHHJJJJJ44J...',
    '..hHJJJJJJJJ...',
    '..hHJJJJJJJj...',
    '...hjJJJJJj....',
    '.....jJJJj.....',
    '.......jj......',
]

FACE_MOUSTACHE = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHffffff7..',
    '.hHHHff8fff87..',
    '.hHHHff0ff0f7..',
    '.hHHHfffffff87.',
    '.hHHHcJffffff7.',
    '.hHHHHfJJJJ8J7.',
    '.hHHHHffff44...',
    '..hHHH8ffff8...',
    '..hHHHh8888....',
    '...hHh.........',
]

FACE_GOATEE = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHffffff7..',
    '.hHHHff8fff87..',
    '.hHHHff0ff0f7..',
    '.hHHHfffffff87.',
    '.hHHHcfffffff7.',
    '.hHHHHffJJJ877.',
    '.hHHHHfff447...',
    '..hHHH8fJJJ8...',
    '..hHHHh.JJj....',
    '...hHh...j.....',
]

FACE_FORKED = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHf7ffff7..',
    '.hHHHff8ff887..',
    '.hHHHff0ff0f7..',
    '.hHHHfffffff87.',
    '.hHHHJfffffff7.',
    '.hHHHJJJJJJJ77.',
    '.hHHHJJJJ44J...',
    '..hHHJJJJJJj...',
    '..hHHjJJjJJj...',
    '...hh.JJ.JJ....',
    '......Jj.jJ....',
    '......j...j....',
]

FACES = {
    'young': FACE_YOUNG,
    'beard': FACE_BEARD,
    'old': FACE_OLD,
    'moustache': FACE_MOUSTACHE,
    'goatee': FACE_GOATEE,
    'forked': FACE_FORKED,
}

# Hats share the face template's columns; the first row sits `top` rows above it.
HATS = {
    'cap': (
        -4,
        [
            '.TT............',
            '..TTt..........',
            '...TtcCCCCc....',
            '..cCCCCCCCCCc..',
            '.cCCCCCCCCCCCc.',
            '.cCCCCCCCCCCCc.',
            '.bBBBBBBBBBBBb.',
            '..bbbbbbbbbbb..',
        ],
    ),
    'brim': (
        -5,
        [
            '....cCCCCc.....',
            '...cCCCCCCc....',
            'TTtcCCCCCCCc...',
            'TTTTtCCCCCCc...',
            '.tTTBBBBBBBBb..',
            'cCCCCCCCCCCCCCc',
            '.ccCCCCCCCCCCcc',
            '...............',
        ],
    ),
    'beret': (
        -3,
        [
            '.......TT......',
            '...cCCCCTt.....',
            '.cCCCCCCCCCc...',
            'cCCCCCCCCCCCCc.',
            '.ccCCCCCCCCcc..',
            '..bBBBBBBBBBb..',
        ],
    ),
    'wreath': (  # oak leaves with acorns, for the wild man
        -3,
        [
            '..cC.T.cC.T....',
            '.cCCcCcCCcCc...',
            'cCCcCCcCCcCCc..',
            '.cc.cc.cc.cc...',
        ],
    ),
    'crown': (
        -4,
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


# Heads for figures drawn at vignette size (rig scale below SMALL_SCALE), on
# the same placeholders; the face centre is column 3, row 3.
SMALL_SCALE = 0.6

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
SMALL_FACES['old'] = SMALL_FACES['beard']

SMALL_HATS = {
    'cap': (-2, ['T.cCCc..', '.cCCCCCc', '.bBBBBBb']),
    'brim': (-3, ['..cCCc...', 'TcCCCCc..', 'cCCCCCCCc']),
    'beret': (-2, ['..cCCCT.', '.cCCCCCc', '..bBBBb.']),
    'crown': (-3, ['.T.T.T.', 'bBbBbBb', 'bBBTBBb', '.bbbbb.']),
    'jester': (-4, ['T.....T.', 'Cc...cC.', '.CcCcC..', '.bBBBBb.']),
}


def draw_head(rig, hx, hy, face='young', hair=BROWN, beard=None, hat=None):
    """Draws a head in 3/4 view facing right with its face centred near (hx, hy).

    `hat` is (kind, cloth, trim, band) with kind from `HATS`. On a rig scaled
    below `SMALL_SCALE` the small templates are used instead.
    """
    small = rig.s < SMALL_SCALE
    faces, hats, anchor = (SMALL_FACES, SMALL_HATS, (3, 3)) if small else (FACES, HATS, (8, 6))
    beard = beard if beard is not None else hair
    subst = {'H': hair, 'h': darker(hair), 'J': beard, 'j': darker(beard)}
    rig.sprite(faces[face], hx, hy, subst, anchor=anchor)
    if hat is not None:
        kind, cloth, trim, band = hat
        top, rows = hats[kind]
        subst = {'C': cloth, 'c': darker(cloth), 'T': trim, 't': darker(trim), 'B': band, 'b': darker(band)}
        rig.sprite(rows, hx, hy, subst, anchor=(anchor[0], anchor[1] - top))


def draw_hand(rig, x, y, grip=False):
    """A hand at the end of an arm; `grip` draws a closed fist."""
    if grip:
        rig.part().ellipse(x, y, 2.1, 1.9).paint(SKIN, None)
    else:
        rig.part().ellipse(x, y + 0.5, 2.0, 2.6).paint(SKIN, None)
        rig.put(x - 1, y + 1, LIGHT_GRAY)


def arm(rig, sh, el, wr, sleeve, cuff=None, upper_r=3.1, puff=None):
    """A sleeved arm through shoulder, elbow and wrist.

    `cuff` adds a turned-back cuff at the wrist, `puff` a slashed puffed
    upper sleeve in that colour.
    """
    rig.part().chain([sh, el, wr], [upper_r, 2.5, 2.0]).paint(sleeve)
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
    """A cape hanging from the shoulders, flaring backwards by `swing` pixels."""
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
    rig.part().capsule(gx, gy, tx, ty, 1.8, 1.0).paint(blade, None, outline=darker(darker(blade)))
    rig.line(gx + ux, gy + uy, tx - ux * 2, ty - uy * 2, WHITE)
    rig.part().capsule(hx - ux * 2, hy - uy * 2, gx, gy, 0.8).fill(BROWN)
    rig.part().capsule(gx - uy * 3.5, gy + ux * 3.5, gx + uy * 3.5, gy - ux * 3.5, 1.0).paint(guard, None)
    rig.part().ellipse(hx - ux * 3, hy - uy * 3, 1.3, 1.3).paint(guard, None)


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


# Standing pose shared by Unters, Obers and the vignette people; each figure
# overrides arms and legs, and may override these joints through `pose`.
BASE = dict(head=(30, 15), neck=(30, 21), sh_b=(23, 26), sh_f=(36, 26), waist=(30, 44), hem=56)


def draw_standing(rig, look, arms, legs, back_props=None, front_props=None, pose=None):
    """Draws a standing figure back to front.

    `look` names the colours (sleeve_b, sleeve_f, hose, boot, tunic, skirt,
    belt, hair, hat and optional extras); `arms` is ((sh, el, wr, hand),
    (sh, el, wr, hand)) for the back and the front arm, where hand is
    'open', 'grip' or None; `legs` is ((hip, knee, ankle, toe), ...) back
    then front. Props are callbacks taking the rig.
    """
    j = dict(BASE, **(pose or {}))
    if look.get('cape') is not None:
        cape(rig, j, look['cape'], length=look.get('cape_len', 64), swing=look.get('swing', -7), lining=look.get('lining'))
    if back_props:
        back_props(rig)
    (bsh, bel, bwr, bhand), (fsh, fel, fwr, fhand) = arms
    arm(rig, bsh, bel, bwr, look['sleeve_b'], cuff=look.get('cuff'), puff=look.get('puff'))
    if bhand:
        draw_hand(rig, *bwr, grip=bhand == 'grip')
    for hip, kn, an, toe in legs:
        leg(rig, hip, kn, an, toe, look['hose'], look['boot'], cuff=look.get('boot_cuff'))
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
    hx, hy = j['head']
    draw_head(rig, hx, hy, face=look.get('face', 'young'), hair=look['hair'], beard=look.get('beard'), hat=look['hat'])
    arm(rig, fsh, fel, fwr, look['sleeve_f'], cuff=look.get('cuff'), puff=look.get('puff'))
    if fhand:
        draw_hand(rig, *fwr, grip=fhand == 'grip')
    if front_props:
        front_props(rig)
    return rig

