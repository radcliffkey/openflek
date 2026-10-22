"""EGA 16-colour canvas, pixel-art primitives, and card-sheet compositor."""

import math
from PIL import Image

FACE_W = 61
FACE_H = 100
SPRITE_W = 67
SPRITE_H = 106

BLACK = 0
BLUE = 1
GREEN = 2
CYAN = 3
RED = 4
MAGENTA = 5
BROWN = 6
LIGHT_GRAY = 7
DARK_GRAY = 8
LIGHT_BLUE = 9
LIGHT_GREEN = 10
LIGHT_CYAN = 11
LIGHT_RED = 12
LIGHT_MAGENTA = 13
YELLOW = 14
WHITE = 15

EGA_PALETTE = [
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0xAA),
    (0x00, 0xAA, 0x00),
    (0x00, 0xAA, 0xAA),
    (0xAA, 0x00, 0x00),
    (0xAA, 0x00, 0xAA),
    (0xAA, 0x55, 0x00),
    (0xAA, 0xAA, 0xAA),
    (0x55, 0x55, 0x55),
    (0x55, 0x55, 0xFF),
    (0x55, 0xFF, 0x55),
    (0x55, 0xFF, 0xFF),
    (0xFF, 0x55, 0x55),
    (0xFF, 0x55, 0xFF),
    (0xFF, 0xFF, 0x55),
    (0xFF, 0xFF, 0xFF),
]

CHAR_MAP = {
    '0': BLACK,
    'k': BLACK,
    '1': BLUE,
    'b': BLUE,
    '2': GREEN,
    'G': GREEN,
    '3': CYAN,
    'c': CYAN,
    '4': RED,
    'R': RED,
    '5': MAGENTA,
    'm': MAGENTA,
    '6': BROWN,
    'B': BROWN,
    '7': LIGHT_GRAY,
    'l': LIGHT_GRAY,
    '8': DARK_GRAY,
    'K': DARK_GRAY,
    '9': LIGHT_BLUE,
    'L': LIGHT_BLUE,
    'a': LIGHT_GREEN,
    'g': LIGHT_GREEN,
    'b_': LIGHT_CYAN,
    'C': LIGHT_CYAN,
    'r': LIGHT_RED,
    'M': LIGHT_MAGENTA,
    'd': LIGHT_MAGENTA,
    'e': YELLOW,
    'Y': YELLOW,
    'f': WHITE,
    'W': WHITE,
}

HEX_CHAR_MAP = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'a': 10,
    'b': 11,
    'c': 12,
    'd': 13,
    'e': 14,
    'f': 15,
    'W': 15,
    'K': 8,
    'R': 4,
    'r': 12,
    'Y': 14,
    'B': 6,
    'G': 2,
    'g': 10,
    'L': 9,
    'C': 11,
    'M': 13,
    'm': 5,
    'l': 7,
}


class FaceCanvas:
    """A 61x100 16-colour EGA card face."""

    def __init__(self):
        self.w = FACE_W
        self.h = FACE_H
        self.px = [[WHITE for _ in range(FACE_W)] for _ in range(FACE_H)]
        self.rect(1, 1, FACE_W - 2, FACE_H - 2, DARK_GRAY)

    def in_interior(self, x, y):
        if x < 2 or x > 58 or y < 2 or y > 97:
            return False
        if (x in (2, 58)) and (y in (2, 97)):
            return False
        return True

    def put(self, x, y, col):
        x = int(round(x))
        y = int(round(y))
        if self.in_interior(x, y):
            self.px[y][x] = col & 0x0F

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[y][x]
        return WHITE

    def line(self, x0, y0, x1, y1, col):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, col, thickness=2):
        self.line(x0, y0, x1, y1, col)
        if thickness >= 2:
            if abs(x1 - x0) >= abs(y1 - y0):
                self.line(x0, y0 + 1, x1, y1 + 1, col)
            else:
                self.line(x0 + 1, y0, x1 + 1, y1, col)
        if thickness >= 3:
            if abs(x1 - x0) >= abs(y1 - y0):
                self.line(x0, y0 - 1, x1, y1 - 1, col)
            else:
                self.line(x0 - 1, y0, x1 - 1, y1, col)

    def rect(self, x0, y0, x1, y1, col):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            if 0 <= y0 < self.h and 0 <= x < self.w:
                self.px[y0][x] = col
            if 0 <= y1 < self.h and 0 <= x < self.w:
                self.px[y1][x] = col
        for y in range(min(y0, y1), max(y0, y1) + 1):
            if 0 <= y < self.h and 0 <= x0 < self.w:
                self.px[y][x0] = col
            if 0 <= y < self.h and 0 <= x1 < self.w:
                self.px[y][x1] = col

    def fill_rect(self, x0, y0, x1, y1, c1, c2=None, mode='solid'):
        if c2 is None:
            c2 = c1
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.put(x, y, self._shade(x, y, c1, c2, mode))

    def _shade(self, x, y, c1, c2, mode):
        if mode == 'solid' or c1 == c2:
            return c1
        if mode == 'drape':
            # Classic 1992 EGA cloth shading: mostly solid c1 with diagonal fold ribs in c2
            v = (x + y * 2) % 7
            if v == 0:
                return c2
            if v == 1 and ((x + y) & 1) == 0:
                return c2
            return c1
        if mode == 'checker':
            return c1 if ((x + y) & 1) == 0 else c2
        if mode == 'sparse':
            return c2 if ((x & 1) == 0 and (y & 1) == 0) else c1
        if mode == 'vstripe':
            return c1 if (x & 1) == 0 else c2
        if mode == 'hstripe':
            return c1 if (y & 1) == 0 else c2
        if mode == 'diag':
            return c1 if ((x - y) % 3) != 0 else c2
        return c1

    def fill_ellipse(self, cx, cy, rx, ry, c1, c2=None, outline=None, mode='drape'):
        if c2 is None:
            c2 = c1
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                nx = (x - cx) / max(rx, 0.5)
                ny = (y - cy) / max(ry, 0.5)
                d = nx * nx + ny * ny
                if d <= 1.0:
                    if mode == 'drape' and c1 != c2:
                        # Shade right/lower crescent with checker dither, main body solid c1
                        if nx + 0.5 * ny > 0.35:
                            col = c2 if nx + 0.5 * ny > 0.7 else (c1 if ((x + y) & 1) == 0 else c2)
                        else:
                            col = c1
                    else:
                        col = self._shade(x, y, c1, c2, mode)
                    self.put(x, y, col)
        if outline is not None:
            steps = int(max(rx, ry) * 8) + 16
            for i in range(steps):
                a = 2.0 * math.pi * i / steps
                ox = int(round(cx + rx * math.cos(a)))
                oy = int(round(cy + ry * math.sin(a)))
                self.put(ox, oy, outline)

    def fill_poly(self, pts, c1, c2=None, outline=None, mode='drape'):
        if len(pts) < 3:
            return
        if c2 is None:
            c2 = c1
        ys = [p[1] for p in pts]
        y_min = int(math.floor(min(ys)))
        y_max = int(math.ceil(max(ys)))
        n = len(pts)
        for y in range(y_min, y_max + 1):
            yc = y + 0.5
            xs = []
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if (ay <= yc < by) or (by <= yc < ay):
                    xs.append(ax + (yc - ay) / (by - ay) * (bx - ax))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                x_start = int(math.ceil(xs[i] - 0.5))
                x_end = int(math.floor(xs[i + 1] - 0.5))
                span = max(1, x_end - x_start + 1)
                for x in range(x_start, x_end + 1):
                    if mode == 'drape' and c1 != c2:
                        rel = (x - x_start) / span
                        if rel > 0.78:
                            col = c2 if ((x + y) & 1) == 0 else c1
                        elif ((x - x_start + (y - y_min) // 2) % 6) == 0 and rel > 0.25:
                            col = c2
                        else:
                            col = c1
                    else:
                        col = self._shade(x, y, c1, c2, mode)
                    self.put(x, y, col)
        if outline is not None:
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                self.line(ax, ay, bx, by, outline)

    def blit_sprite(self, rows, x0, y0, flip_x=False, flip_y=False):
        """Draws a list of strings using HEX_CHAR_MAP, where '.' or ' ' is transparent."""
        src = list(reversed(rows)) if flip_y else rows
        for dy, row in enumerate(src):
            line = ''.join(reversed(row)) if flip_x else row
            for dx, ch in enumerate(line):
                if ch in ('.', ' '):
                    continue
                col = HEX_CHAR_MAP.get(ch)
                if col is not None:
                    self.put(x0 + dx, y0 + dy, col)

    def blit_centered(self, rows, cx, cy, flip_x=False, flip_y=False):
        h = len(rows)
        w = len(rows[0]) if h > 0 else 0
        self.blit_sprite(rows, cx - w // 2, cy - h // 2, flip_x=flip_x, flip_y=flip_y)


def draw_back_face(line_col):
    """Draws an ornate diamond-lattice and rosette card-back face in line_col."""
    f = FaceCanvas()
    # Outer ornamental double border
    f.rect(3, 3, FACE_W - 4, FACE_H - 4, line_col)
    f.rect(5, 5, FACE_W - 6, FACE_H - 6, line_col)
    # Diamond lattice across the interior (x=6..54, y=6..93)
    for k in range(-90, 150, 8):
        f.line(6, 6 + k, 54, 6 + k + 48, line_col)
        f.line(6, 6 + k + 48, 54, 6 + k, line_col)
    # Clip lattice outside (6..54, 6..93) and restore border
    for y in range(FACE_H):
        for x in range(FACE_W):
            if not (6 <= x <= 54 and 6 <= y <= 93):
                if f.in_interior(x, y):
                    f.px[y][x] = WHITE
    f.rect(1, 1, FACE_W - 2, FACE_H - 2, DARK_GRAY)
    f.rect(3, 3, FACE_W - 4, FACE_H - 4, line_col)
    f.rect(5, 5, FACE_W - 6, FACE_H - 6, line_col)
    # Corner diamond studs
    for cx, cy in [(9, 9), (51, 9), (9, 90), (51, 90)]:
        f.fill_poly([(cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)], line_col, WHITE, outline=line_col)
    # Central medallion framing 'O' and 'F'
    f.fill_poly([(30, 32), (46, 49), (30, 66), (14, 49)], WHITE, WHITE, outline=line_col)
    f.fill_poly([(30, 35), (43, 49), (30, 63), (17, 49)], line_col, WHITE, outline=DARK_GRAY, mode='checker')
    # Shadowed 'O' and 'F' monogram
    o_glyph = [
        '.88888.',
        '88fff88',
        '8ff8ff8',
        '8ff.ff8',
        '8ff.ff8',
        '8ff.ff8',
        '8fffff8',
        '.88888.',
    ]
    f_glyph = [
        '8888888',
        '8fffff8',
        '8ff888.',
        '8ffff8.',
        '8ff888.',
        '8ff8...',
        '8ff8...',
        '8888...',
    ]
    f.blit_sprite(o_glyph, 23, 40)
    f.blit_sprite(f_glyph, 29, 49)
    return f


def save_sheet(faces, out_path='docs/new_card_sheet.png', ref_sheet='docs/card_sheet.png'):
    """Composites 32 FaceCanvas objects into the exact 8x5 sheet layout with frames and backs."""
    ref = Image.open(ref_sheet).convert('RGB')
    out = ref.copy()
    px = out.load()

    scale = 2
    gap = 4
    all_faces = list(faces) + [
        draw_back_face(BLUE),
        draw_back_face(RED),
        draw_back_face(MAGENTA),
        draw_back_face(BROWN),
    ]
    for cid, face in enumerate(all_faces):
        col_idx = cid % 8
        row_idx = cid // 8
        sx0 = gap + col_idx * (SPRITE_W + gap) + 2
        sy0 = gap + row_idx * (SPRITE_H + gap) + 2
        for fy in range(FACE_H):
            for fx in range(FACE_W):
                if not face.in_interior(fx, fy):
                    continue
                rgb = EGA_PALETTE[face.px[fy][fx] & 0x0F]
                for dy in range(scale):
                    for dx in range(scale):
                        px[(sx0 + fx) * scale + dx, (sy0 + fy) * scale + dy] = rgb

    out.save(out_path)
