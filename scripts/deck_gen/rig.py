"""Shape rig: unioned masks painted with a pixel outline and edge shading.

Figures and animals are built from capsules, ellipses and polygons. Each
`Part` collects shapes into one mask, so a limb made of an upper and a lower
segment gets a single outline instead of a seam at the joint. Parts are
painted in back-to-front order; their outlines separate overlapping parts.

A `Rig` can be mirrored about a vertical axis, so a pose is written once
facing right and reused facing left. Shading is computed after mirroring,
which keeps the light on the upper left for every card.

Outlines default to the darker partner of the fill colour, as in the 1992
deck, where a red sleeve is edged in dark red rather than grey.
"""

import math

from scripts.deck_gen.palette import (
    BLUE,
    BROWN,
    CYAN,
    DARK_GRAY,
    GREEN,
    HEX_CHAR_MAP,
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

# Darker partner of each colour: used for shading and the default outline.
DARKER = {
    LIGHT_RED: RED,
    YELLOW: BROWN,
    WHITE: LIGHT_GRAY,
    LIGHT_CYAN: CYAN,
    LIGHT_GREEN: GREEN,
    CYAN: BLUE,
    LIGHT_BLUE: BLUE,
    LIGHT_MAGENTA: MAGENTA,
    GREEN: DARK_GRAY,
    RED: DARK_GRAY,
    BROWN: DARK_GRAY,
    BLUE: DARK_GRAY,
    MAGENTA: DARK_GRAY,
    LIGHT_GRAY: DARK_GRAY,
}

AUTO = object()


def darker(col):
    return DARKER.get(col, DARK_GRAY)


class Rig:
    """Maps pose coordinates to card coordinates.

    The pose is scaled by `scale` about the point (`axis`, `ground`), so a
    scaled figure keeps its feet on the turf, then mirrored about `axis`
    when `flip` is set and shifted by (`dx`, `dy`).

    A `thin` rig is for figures a few pixels wide, where a per-part outline
    would swallow a two-pixel limb: parts are painted without outlines and
    `silhouette` then draws one outline around everything painted.
    """

    def __init__(self, c, flip=False, axis=30, dx=0, dy=0, scale=1.0, ground=86, thin=False):
        self.c = c
        self.flip = flip
        self.axis = axis
        self.dx = dx
        self.dy = dy
        self.s = scale
        self.ground = ground
        self.thin = thin
        self.painted = set()

    def plot(self, x, y, col):
        """Puts a pixel at card coordinates and remembers it for `silhouette`."""
        x, y = int(round(x)), int(round(y))
        self.c.put(x, y, col)
        self.painted.add((x, y))

    def silhouette(self, col=DARK_GRAY):
        """Outlines the union of everything this rig has painted."""
        ring = set()
        for x, y in self.painted:
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if (nx, ny) not in self.painted:
                    ring.add((nx, ny))
        for x, y in ring:
            self.c.put(x, y, col)

    def tx(self, x, y):
        if self.s != 1.0:
            x = self.axis + (x - self.axis) * self.s
            y = self.ground + (y - self.ground) * self.s
        if self.flip:
            x = 2 * self.axis - x
        return x + self.dx, y + self.dy

    def radius(self, r):
        """A pose radius in card pixels; never so thin that the shape vanishes."""
        return max(r * self.s, 0.7) if self.s != 1.0 else r

    def part(self):
        return Part(self)

    def line(self, x0, y0, x1, y1, col):
        ax, ay = (int(round(v)) for v in self.tx(x0, y0))
        bx, by = (int(round(v)) for v in self.tx(x1, y1))
        dx, dy = abs(bx - ax), -abs(by - ay)
        sx, sy = (1 if ax < bx else -1), (1 if ay < by else -1)
        err = dx + dy
        while True:
            self.plot(ax, ay, col)
            if ax == bx and ay == by:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                ax += sx
            if e2 <= dx:
                err += dx
                ay += sy

    def put(self, x, y, col):
        self.plot(*self.tx(x, y), col)

    def sprite(self, rows, x0, y0, subst=None, anchor=(0, 0)):
        """Blits a hex sprite pixel for pixel, never scaled.

        The sprite pixel at `anchor` (column, row) lands on the pose point
        (x0, y0); a flipped rig mirrors the sprite about that pixel. `subst`
        maps placeholder characters to colours (hair, beard, cloth).
        """
        cx, cy = self.tx(x0, y0)
        cx, cy = int(round(cx)), int(round(cy))
        ax, ay = anchor
        for sy, row in enumerate(rows):
            for sx, ch in enumerate(row):
                col = subst.get(ch) if subst and ch in subst else HEX_CHAR_MAP.get(ch)
                if col is not None:
                    px = cx - (sx - ax) if self.flip else cx + (sx - ax)
                    self.plot(px, cy + sy - ay, col)


def _seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    ll = vx * vx + vy * vy
    t = 0.0 if ll == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / ll))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy), t


class Part:
    """A union of shapes painted as one outlined, shaded region."""

    def __init__(self, rig):
        self.rig = rig
        self.mask = set()

    def capsule(self, x0, y0, x1, y1, r0, r1=None):
        """A segment swept by a disc whose radius tapers from r0 to r1."""
        if r1 is None:
            r1 = r0
        r0, r1 = self.rig.radius(r0), self.rig.radius(r1)
        ax, ay = self.rig.tx(x0, y0)
        bx, by = self.rig.tx(x1, y1)
        r = max(r0, r1)
        for y in range(int(min(ay, by) - r - 1), int(max(ay, by) + r + 2)):
            for x in range(int(min(ax, bx) - r - 1), int(max(ax, bx) + r + 2)):
                d, t = _seg_dist(x, y, ax, ay, bx, by)
                if d <= r0 + (r1 - r0) * t:
                    self.mask.add((x, y))
        return self

    def chain(self, pts, radii):
        """Capsules through consecutive points, radii given per point."""
        for i in range(len(pts) - 1):
            self.capsule(*pts[i], *pts[i + 1], radii[i], radii[i + 1])
        return self

    def ellipse(self, cx, cy, rx, ry, angle=0.0):
        """An ellipse rotated by `angle` degrees (clockwise on screen) in pose coordinates."""
        rig = self.rig
        if rig.s == 1.0:
            # Sample in pose space so unscaled shapes mirror pixel for pixel.
            pts = self._ellipse_pts(cx, cy, rx, ry, angle)
            self.mask.update(rig.tx(x, y) for x, y in pts)
            return self
        cx, cy = rig.tx(cx, cy)
        if rig.flip:
            angle = -angle
        self.mask.update(self._ellipse_pts(cx, cy, rig.radius(rx), rig.radius(ry), angle))
        return self

    @staticmethod
    def _ellipse_pts(cx, cy, rx, ry, angle):
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)
        r = max(rx, ry) + 1
        out = []
        for y in range(int(cy - r), int(cy + r + 2)):
            for x in range(int(cx - r), int(cx + r + 2)):
                u = (x - cx) * ca + (y - cy) * sa
                v = -(x - cx) * sa + (y - cy) * ca
                if (u / rx) ** 2 + (v / ry) ** 2 <= 1.0:
                    out.append((x, y))
        return out

    def poly(self, pts):
        pts = [self.rig.tx(x, y) for x, y in pts]
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
            xs = []
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if (ay <= y < by) or (by <= y < ay):
                    xs.append(ax + (y - ay) / (by - ay) * (bx - ax))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(math.ceil(xs[i] - 0.4)), int(math.floor(xs[i + 1] + 0.4)) + 1):
                    self.mask.add((x, y))
        return self

    def rect(self, x0, y0, x1, y1):
        ax, ay = self.rig.tx(x0, y0)
        bx, by = self.rig.tx(x1, y1)
        for y in range(round(min(ay, by)), round(max(ay, by)) + 1):
            for x in range(round(min(ax, bx)), round(max(ax, bx)) + 1):
                self.mask.add((x, y))
        return self

    def cut(self, other):
        """Removes another part's pixels from this one."""
        self.mask -= other.mask
        return self

    def clip(self, x0=None, y0=None, x1=None, y1=None):
        """Keeps pixels inside the box, given in card coordinates."""
        self.mask = {
            (x, y)
            for x, y in self.mask
            if (x0 is None or x >= x0) and (x1 is None or x <= x1) and (y0 is None or y >= y0) and (y1 is None or y <= y1)
        }
        return self

    def edge(self):
        """Mask pixels with a 4-neighbour outside the mask."""
        m = self.mask
        return {
            (x, y) for x, y in m if (x - 1, y) not in m or (x + 1, y) not in m or (x, y - 1) not in m or (x, y + 1) not in m
        }

    def paint(self, base, shade=AUTO, outline=AUTO, light=None, pattern=None):
        """Fills the mask with `base`, dithers `shade` along the lower right and draws `outline` on the rim.

        `shade` and `outline` default to the darker partner of `base`; pass
        None to leave either out. `light` brightens the upper-left rim.
        `pattern(x, y)` may return a colour to override the fill (stripes,
        embroidery); it does not touch the outline.
        """
        if shade is AUTO:
            shade = darker(base)
        if outline is AUTO:
            outline = darker(base)
        thin = self.rig.thin
        if thin:
            outline = None
        plot = self.rig.plot
        m = self.mask
        rim = self.edge() if outline is not None else set()
        for x, y in m:
            if (x, y) in rim:
                plot(x, y, outline)
                continue
            col = base
            if shade is not None and thin:
                # Only parts at least three pixels wide get a shaded right edge.
                if (x + 1, y) not in m and (x - 2, y) in m:
                    col = shade
            elif shade is not None:
                near_right = (x + 2, y) not in m
                near_bottom = (x, y + 2) not in m
                if near_right and near_bottom:
                    col = shade
                elif (near_right or near_bottom) and (x + y) & 1:
                    col = shade
            if light is not None and ((x - 2, y) not in m or (x, y - 2) not in m) and (x + 2, y) in m:
                col = light
            if pattern is not None:
                p = pattern(x, y)
                if p is not None:
                    col = p
            plot(x, y, col)
        return self

    def fill(self, col):
        for x, y in self.mask:
            self.rig.plot(x, y, col)
        return self
