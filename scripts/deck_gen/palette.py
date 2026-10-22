"""EGA 16-colour palette, the card-face canvas and pixel-art primitives."""

import math

FACE_W = 61
FACE_H = 100

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

# RGB of each colour index, for scripts that render faces to an image while
# working on them; the game itself draws the bitmap with its own palette.
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

# Sprite rows spell colours as hex digits; any other character is transparent.
HEX_CHAR_MAP = {ch: i for i, ch in enumerate('0123456789abcdef')}


def bresenham(x0, y0, x1, y1):
    """The pixels of a line between two points, rounded to the pixel grid."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def checker(x, y, c1, c2):
    """A one-pixel chequer of two colours, as used for turf and water."""
    return c1 if ((x + y) & 1) == 0 else c2


def fill_terrain(c, top, hill_y, colour):
    """Fills ground from row `top` to the bottom of the face.

    `hill_y(x)` gives the crest of the ground in each column; the crest is
    drawn dark grey, the rows above it are left alone and the rows below it
    take `colour(x, y, crest)`.
    """
    for x in range(2, FACE_W - 2):
        crest = hill_y(x)
        for y in range(max(top, crest), FACE_H - 2):
            c.put(x, y, DARK_GRAY if y == crest else colour(x, y, crest))


class FaceCanvas:
    """A 61x100 16-colour EGA card face."""

    def __init__(self):
        self.w = FACE_W
        self.h = FACE_H
        self.px = [[WHITE for _ in range(FACE_W)] for _ in range(FACE_H)]
        # Dark-grey inner border with its corner pixels left white, as on the 1992 faces.
        for x in range(2, FACE_W - 2):
            self.px[1][x] = DARK_GRAY
            self.px[FACE_H - 2][x] = DARK_GRAY
        for y in range(2, FACE_H - 2):
            self.px[y][1] = DARK_GRAY
            self.px[y][FACE_W - 2] = DARK_GRAY

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
        for x, y in bresenham(x0, y0, x1, y1):
            self.put(x, y, col)

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
        if mode == 'checker':
            return checker(x, y, c1, c2)
        if mode == 'sparse':
            return c2 if ((x & 1) == 0 and (y & 1) == 0) else c1
        if mode == 'vstripe':
            return c1 if (x & 1) == 0 else c2
        if mode == 'hstripe':
            return c1 if (y & 1) == 0 else c2
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

    def blit_sprite(self, rows, x0, y0, flip_x=False):
        """Draws a list of hex-digit strings; any other character is transparent."""
        for dy, row in enumerate(rows):
            line = ''.join(reversed(row)) if flip_x else row
            for dx, ch in enumerate(line):
                col = HEX_CHAR_MAP.get(ch)
                if col is not None:
                    self.put(x0 + dx, y0 + dy, col)

    def blit_centered(self, rows, cx, cy, flip_x=False):
        h = len(rows)
        w = len(rows[0]) if h > 0 else 0
        self.blit_sprite(rows, cx - w // 2, cy - h // 2, flip_x=flip_x)
