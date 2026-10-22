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
    '.hHHH7f0ff0f7..',
    '.hHHH7ffffff87.',
    '.hHHHcfffffff7.',
    '.hHHHHfffff877.',
    '.hHHHHffff447..',
    '..hHHH7ffff7...',
    '..hHHHh7777....',
    '...hHh.........',
]

FACE_BEARD = [
    '.....hHHHh.....',
    '...hHHHHHHHh...',
    '..hHHHHHHHHHh..',
    '..hHHHffffff7..',
    '.hHHHff8fff87..',
    '.hHHH7f0ff0f7..',
    '.hHHH7ffffff87.',
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
    '.hHHH7f0ff0f7..',
    '.hHHH7f7ffff87.',
    '.hHHHJfffffff7.',
    '.hHHJJJJJJJJ77.',
    '.hHHJJJJJ44J...',
    '..hHJJJJJJJJ...',
    '..hHJJJJJJJj...',
    '...hjJJJJJj....',
    '.....jJJJj.....',
    '.......jj......',
]

FACES = {'young': FACE_YOUNG, 'beard': FACE_BEARD, 'old': FACE_OLD}

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
    'crown': (
        -4,
        [
            '..T....T....T..',
            '.BB...BTB...BB.',
            '.BBB.BBBBB.BBBb',
            '.BCBBBCCCBBBCBb',
            '.BBBBBBBBBBBBBb',
            '.BTBBBBTBBBBTBb',
            '.bbbbbbbbbbbbb.',
        ],
    ),
}


def draw_head(rig, hx, hy, face='young', hair=BROWN, beard=None, hat=None):
    """Draws a head in 3/4 view facing right with its face centred near (hx, hy).

    `hat` is (kind, cloth, trim, band) with kind from `HATS`.
    """
    x0, y0 = hx - 8, hy - 6
    beard = beard if beard is not None else hair
    subst = {'H': hair, 'h': darker(hair), 'J': beard, 'j': darker(beard)}
    rig.sprite(FACES[face], x0, y0, subst)
    if hat is not None:
        kind, cloth, trim, band = hat
        top, rows = HATS[kind]
        subst = {'C': cloth, 'c': darker(cloth), 'T': trim, 't': darker(trim), 'B': band, 'b': darker(band)}
        rig.sprite(rows, x0, y0 + top, subst)


def draw_hand(rig, x, y, grip=False):
    """A hand at the end of an arm; `grip` draws a closed fist."""
    if grip:
        rig.part().ellipse(x, y, 2.1, 1.9).paint(SKIN, None)
    else:
        rig.part().ellipse(x, y + 0.5, 2.0, 2.6).paint(SKIN, None)
        rig.put(x - 1, y + 1, LIGHT_GRAY)


def arm(rig, sh, el, wr, sleeve, cuff=None, upper_r=2.7, puff=None):
    """A sleeved arm through shoulder, elbow and wrist.

    `cuff` adds a turned-back cuff at the wrist, `puff` a slashed puffed
    upper sleeve in that colour.
    """
    rig.part().chain([sh, el, wr], [upper_r, 2.2, 1.8]).paint(sleeve)
    ex, ey = el
    wx, wy = wr
    if puff is not None:
        sx, sy = sh
        rig.part().capsule(sx, sy, sx + (ex - sx) * 0.45, sy + (ey - sy) * 0.45, upper_r + 0.6, upper_r).paint(puff)
    if cuff is not None:
        rig.part().capsule(wx + (ex - wx) * 0.22, wy + (ey - wy) * 0.22, wx + (ex - wx) * 0.05, wy + (ey - wy) * 0.05, 2.2).paint(
            cuff
        )


def leg(rig, hip, kn, an, toe, hose, boot, boot_top=0.4, thigh_r=3.4, cuff=None):
    """A leg through hip, knee and ankle, booted from `boot_top` of the shin, the foot pointing at `toe`."""
    rig.part().chain([hip, kn, an], [thigh_r, 2.5, 2.0]).paint(hose)
    kx, ky = kn
    ax, ay = an
    bx, by = kx + (ax - kx) * boot_top, ky + (ay - ky) * boot_top
    tx, ty = toe
    b = rig.part().chain([(bx, by), an], [2.8, 2.3]).capsule(ax, ay + 0.5, tx, ty, 2.2, 1.3)
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
    body.ellipse((sbx + sfx) / 2 + 1.5, sby + 6, 6.2, 6.0)
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


def pole(rig, a, b, col=BROWN):
    """A staff or shaft from `a` to `b`."""
    rig.part().capsule(*a, *b, 0.8).fill(col)

