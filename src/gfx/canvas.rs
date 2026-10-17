//! Indexed-colour software framebuffer with BGI-style drawing primitives.
//!
//! All coordinates are inclusive, like Borland's Graph unit, so `bar(0, 0, 9, 9)`
//! fills a 10x10 square. Drawing outside the canvas is silently clipped.

/// The standard 16-colour EGA/VGA palette as RGB.
pub const EGA_PALETTE: [[u8; 3]; 16] = [
    [0x00, 0x00, 0x00],
    [0x00, 0x00, 0xAA],
    [0x00, 0xAA, 0x00],
    [0x00, 0xAA, 0xAA],
    [0xAA, 0x00, 0x00],
    [0xAA, 0x00, 0xAA],
    [0xAA, 0x55, 0x00],
    [0xAA, 0xAA, 0xAA],
    [0x55, 0x55, 0x55],
    [0x55, 0x55, 0xFF],
    [0x55, 0xFF, 0x55],
    [0x55, 0xFF, 0xFF],
    [0xFF, 0x55, 0x55],
    [0xFF, 0x55, 0xFF],
    [0xFF, 0xFF, 0x55],
    [0xFF, 0xFF, 0xFF],
];

/// EGA colour indices by their conventional names.
pub mod color {
    pub const BLACK: u8 = 0;
    pub const BLUE: u8 = 1;
    pub const GREEN: u8 = 2;
    pub const CYAN: u8 = 3;
    pub const RED: u8 = 4;
    pub const MAGENTA: u8 = 5;
    pub const BROWN: u8 = 6;
    pub const LIGHT_GRAY: u8 = 7;
    pub const DARK_GRAY: u8 = 8;
    pub const LIGHT_BLUE: u8 = 9;
    pub const LIGHT_GREEN: u8 = 10;
    pub const LIGHT_CYAN: u8 = 11;
    pub const LIGHT_RED: u8 = 12;
    pub const LIGHT_MAGENTA: u8 = 13;
    pub const YELLOW: u8 = 14;
    pub const WHITE: u8 = 15;
}

/// An 8x8 one-bit fill pattern; bit 7 of each row is the leftmost pixel.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Pattern(pub [u8; 8]);

impl Pattern {
    pub const SOLID: Pattern = Pattern([0xFF; 8]);
    pub const HORIZONTAL: Pattern = Pattern([0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00]);
    pub const SLASH: Pattern = Pattern([0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]);
    pub const BACKSLASH: Pattern = Pattern([0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]);
    pub const HATCH: Pattern = Pattern([0xFF, 0x88, 0x88, 0x88, 0xFF, 0x88, 0x88, 0x88]);
    pub const CROSS_HATCH: Pattern = Pattern([0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81]);
    pub const CHECKER: Pattern = Pattern([0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55]);
    pub const INTERLEAVE: Pattern = Pattern([0xCC, 0x33, 0xCC, 0x33, 0xCC, 0x33, 0xCC, 0x33]);
    pub const WIDE_DOTS: Pattern = Pattern([0x80, 0x00, 0x08, 0x00, 0x80, 0x00, 0x08, 0x00]);
    pub const CLOSE_DOTS: Pattern = Pattern([0x88, 0x00, 0x22, 0x00, 0x88, 0x00, 0x22, 0x00]);
}

/// How an area is filled: pattern bits in `fg`, cleared bits in `bg`
/// (or left untouched when `bg` is `None`).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Fill {
    pub pattern: Pattern,
    pub fg: u8,
    pub bg: Option<u8>,
}

impl Fill {
    pub const fn solid(c: u8) -> Fill {
        Fill {
            pattern: Pattern::SOLID,
            fg: c,
            bg: None,
        }
    }

    pub const fn pattern(pattern: Pattern, fg: u8, bg: u8) -> Fill {
        Fill {
            pattern,
            fg,
            bg: Some(bg),
        }
    }

    fn color_at(&self, x: i32, row: u8) -> Option<u8> {
        if row & (0x80 >> (x & 7)) != 0 {
            Some(self.fg)
        } else {
            self.bg
        }
    }
}

/// A rectangular indexed-colour image; used both for the screen and for sprites.
#[derive(Clone, Debug)]
pub struct Canvas {
    width: i32,
    height: i32,
    pixels: Vec<u8>,
    /// Bumped on every change, so presenters can skip unchanged frames.
    generation: u64,
}

impl PartialEq for Canvas {
    fn eq(&self, other: &Canvas) -> bool {
        self.width == other.width && self.height == other.height && self.pixels == other.pixels
    }
}

impl Eq for Canvas {}

impl Canvas {
    pub fn new(width: i32, height: i32) -> Canvas {
        Canvas {
            width,
            height,
            pixels: vec![0; (width * height) as usize],
            generation: 0,
        }
    }

    pub fn width(&self) -> i32 {
        self.width
    }

    pub fn height(&self) -> i32 {
        self.height
    }

    pub fn pixels(&self) -> &[u8] {
        &self.pixels
    }

    /// Changes whenever the pixels may have changed.
    pub fn generation(&self) -> u64 {
        self.generation
    }

    pub fn clear(&mut self, c: u8) {
        if self.pixels.iter().any(|&p| p != c) {
            self.generation += 1;
            self.pixels.fill(c);
        }
    }

    /// Colour at a position, or `None` outside the canvas.
    pub fn pixel(&self, x: i32, y: i32) -> Option<u8> {
        self.in_bounds(x, y)
            .then(|| self.pixels[(y * self.width + x) as usize])
    }

    pub fn put_pixel(&mut self, x: i32, y: i32, c: u8) {
        if self.in_bounds(x, y) {
            let p = &mut self.pixels[(y * self.width + x) as usize];
            if *p != c {
                *p = c;
                self.generation += 1;
            }
        }
    }

    fn in_bounds(&self, x: i32, y: i32) -> bool {
        x >= 0 && y >= 0 && x < self.width && y < self.height
    }

    fn fill_span(&mut self, x1: i32, x2: i32, y: i32, fill: &Fill) {
        if y < 0 || y >= self.height {
            return;
        }
        let (a, b) = (x1.min(x2).max(0), x1.max(x2).min(self.width - 1));
        if a > b {
            return;
        }
        let start = (y * self.width) as usize;
        let span = &mut self.pixels[start + a as usize..=start + b as usize];
        let row = fill.pattern.0[y.rem_euclid(8) as usize];
        let mut changed = false;
        if row == 0xFF {
            changed = span.iter().any(|&p| p != fill.fg);
            span.fill(fill.fg);
        } else {
            for (x, p) in (a..).zip(span.iter_mut()) {
                if let Some(c) = fill.color_at(x, row) {
                    changed |= *p != c;
                    *p = c;
                }
            }
        }
        if changed {
            self.generation += 1;
        }
    }

    /// Bresenham line, endpoints included.
    pub fn line(&mut self, x1: i32, y1: i32, x2: i32, y2: i32, c: u8) {
        let (dx, dy) = ((x2 - x1).abs(), -(y2 - y1).abs());
        let (sx, sy) = ((x2 - x1).signum(), (y2 - y1).signum());
        let (mut x, mut y, mut err) = (x1, y1, dx + dy);
        loop {
            self.put_pixel(x, y, c);
            if x == x2 && y == y2 {
                break;
            }
            let e2 = 2 * err;
            if e2 >= dy {
                err += dy;
                x += sx;
            }
            if e2 <= dx {
                err += dx;
                y += sy;
            }
        }
    }

    /// Rectangle outline.
    pub fn rect(&mut self, x1: i32, y1: i32, x2: i32, y2: i32, c: u8) {
        self.line(x1, y1, x2, y1, c);
        self.line(x1, y2, x2, y2, c);
        self.line(x1, y1, x1, y2, c);
        self.line(x2, y1, x2, y2, c);
    }

    /// Filled rectangle without outline (BGI `Bar`).
    pub fn bar(&mut self, x1: i32, y1: i32, x2: i32, y2: i32, fill: Fill) {
        for y in y1.min(y2)..=y1.max(y2) {
            self.fill_span(x1, x2, y, &fill);
        }
    }

    /// Ellipse outline using the midpoint algorithm.
    pub fn ellipse(&mut self, cx: i32, cy: i32, rx: i32, ry: i32, c: u8) {
        for (x, y) in ellipse_quadrant(rx, ry) {
            self.put_pixel(cx + x, cy + y, c);
            self.put_pixel(cx - x, cy + y, c);
            self.put_pixel(cx + x, cy - y, c);
            self.put_pixel(cx - x, cy - y, c);
        }
    }

    pub fn fill_ellipse(&mut self, cx: i32, cy: i32, rx: i32, ry: i32, fill: Fill) {
        let mut half_width = vec![-1; ry.max(0) as usize + 1];
        for (x, y) in ellipse_quadrant(rx, ry) {
            let w = &mut half_width[y as usize];
            *w = (*w).max(x);
        }
        for (y, &w) in half_width.iter().enumerate() {
            if w >= 0 {
                let y = y as i32;
                self.fill_span(cx - w, cx + w, cy + y, &fill);
                if y != 0 {
                    self.fill_span(cx - w, cx + w, cy - y, &fill);
                }
            }
        }
    }

    /// Fills a polygon (even-odd rule, pixel centres).
    pub fn fill_poly(&mut self, points: &[(i32, i32)], fill: Fill) {
        if points.len() < 3 {
            return;
        }
        let y_min = points.iter().map(|p| p.1).min().unwrap_or(0);
        let y_max = points.iter().map(|p| p.1).max().unwrap_or(0);
        let mut xs = Vec::new();
        for y in y_min..=y_max {
            let yc = y as f32 + 0.5;
            xs.clear();
            for i in 0..points.len() {
                let (ax, ay) = points[i];
                let (bx, by) = points[(i + 1) % points.len()];
                let (ayf, byf) = (ay as f32, by as f32);
                if (ayf <= yc && byf > yc) || (byf <= yc && ayf > yc) {
                    xs.push(ax as f32 + (yc - ayf) / (byf - ayf) * (bx - ax) as f32);
                }
            }
            xs.sort_by(f32::total_cmp);
            for &[left, right] in xs.as_chunks::<2>().0 {
                let (a, b) = ((left - 0.5).ceil() as i32, (right - 0.5).floor() as i32);
                if a <= b {
                    self.fill_span(a, b, y, &fill);
                }
            }
        }
    }

    /// Polygon outline.
    pub fn poly(&mut self, points: &[(i32, i32)], c: u8) {
        for i in 0..points.len() {
            let (a, b) = (points[i], points[(i + 1) % points.len()]);
            self.line(a.0, a.1, b.0, b.1, c);
        }
    }

    /// Copies `src` to (x, y), skipping pixels equal to `transparent`.
    pub fn blit(&mut self, src: &Canvas, x: i32, y: i32, transparent: Option<u8>) {
        let (x0, x1) = (x.max(0), (x + src.width).min(self.width));
        let (y0, y1) = (y.max(0), (y + src.height).min(self.height));
        if x0 >= x1 || y0 >= y1 {
            return;
        }
        let w = (x1 - x0) as usize;
        let mut changed = false;
        for dy in y0..y1 {
            let s0 = ((dy - y) * src.width + (x0 - x)) as usize;
            let d0 = (dy * self.width + x0) as usize;
            let (from, to) = (&src.pixels[s0..s0 + w], &mut self.pixels[d0..d0 + w]);
            match transparent {
                None => {
                    changed |= from != to;
                    to.copy_from_slice(from);
                }
                Some(t) => {
                    for (&c, p) in from.iter().zip(to.iter_mut()) {
                        if c != t && *p != c {
                            *p = c;
                            changed = true;
                        }
                    }
                }
            }
        }
        if changed {
            self.generation += 1;
        }
    }

    /// Copies a region out into a new canvas (like BGI `GetImage`); outside
    /// the canvas reads as colour 0.
    pub fn crop(&self, x: i32, y: i32, width: i32, height: i32) -> Canvas {
        let mut out = Canvas::new(width, height);
        out.blit(self, -x, -y, None);
        out
    }

    /// Converts to RGBA8 using the EGA palette.
    pub fn to_rgba(&self, out: &mut Vec<u8>) {
        const LUT: [[u8; 4]; 16] = {
            let mut t = [[0, 0, 0, 0xFF]; 16];
            let mut i = 0;
            while i < 16 {
                t[i] = [
                    EGA_PALETTE[i][0],
                    EGA_PALETTE[i][1],
                    EGA_PALETTE[i][2],
                    0xFF,
                ];
                i += 1;
            }
            t
        };
        out.resize(self.pixels.len() * 4, 0);
        for (px, &c) in out.as_chunks_mut::<4>().0.iter_mut().zip(&self.pixels) {
            *px = LUT[(c & 0x0F) as usize];
        }
    }
}

/// Points of one quadrant (x, y >= 0) of an axis-aligned ellipse outline.
fn ellipse_quadrant(rx: i32, ry: i32) -> Vec<(i32, i32)> {
    let mut pts = Vec::new();
    if rx <= 0 || ry <= 0 {
        for x in 0..=rx.max(0) {
            pts.push((x, 0));
        }
        for y in 0..=ry.max(0) {
            pts.push((0, y));
        }
        return pts;
    }
    let (rx2, ry2) = ((rx as i64) * (rx as i64), (ry as i64) * (ry as i64));
    let (mut x, mut y) = (0i64, ry as i64);
    let mut d1 = ry2 - rx2 * ry as i64 + rx2 / 4;
    while ry2 * x <= rx2 * y {
        pts.push((x as i32, y as i32));
        x += 1;
        if d1 < 0 {
            d1 += ry2 * (2 * x + 1);
        } else {
            y -= 1;
            d1 += ry2 * (2 * x + 1) - 2 * rx2 * y;
        }
    }
    let mut d2 = ry2 * (2 * x + 1) * (2 * x + 1) / 4 + rx2 * (y - 1) * (y - 1) - rx2 * ry2;
    while y >= 0 {
        pts.push((x as i32, y as i32));
        y -= 1;
        if d2 > 0 {
            d2 += rx2 * (1 - 2 * y);
        } else {
            x += 1;
            d2 += ry2 * 2 * x + rx2 * (1 - 2 * y);
        }
    }
    pts
}

#[cfg(test)]
mod tests {
    use super::*;

    fn count(c: &Canvas, color: u8) -> usize {
        c.pixels().iter().filter(|&&p| p == color).count()
    }

    #[test]
    fn bar_is_inclusive_and_clipped() {
        let mut c = Canvas::new(20, 20);
        c.bar(0, 0, 9, 9, Fill::solid(4));
        assert_eq!(count(&c, 4), 100);
        c.bar(15, 15, 30, 30, Fill::solid(5));
        assert_eq!(count(&c, 5), 25);
    }

    #[test]
    fn line_hits_both_endpoints() {
        let mut c = Canvas::new(10, 10);
        c.line(1, 8, 7, 2, 3);
        assert_eq!(c.pixel(1, 8), Some(3));
        assert_eq!(c.pixel(7, 2), Some(3));
        assert_eq!(count(&c, 3), 7);
    }

    #[test]
    fn pattern_fill_uses_background_for_clear_bits() {
        let mut c = Canvas::new(8, 2);
        c.bar(0, 0, 7, 1, Fill::pattern(Pattern::CHECKER, 1, 2));
        assert_eq!(c.pixel(0, 0), Some(1));
        assert_eq!(c.pixel(1, 0), Some(2));
        assert_eq!(c.pixel(0, 1), Some(2));
    }

    #[test]
    fn fill_ellipse_is_symmetric_and_spans_radii() {
        let mut c = Canvas::new(21, 11);
        c.fill_ellipse(10, 5, 10, 5, Fill::solid(1));
        assert_eq!(c.pixel(0, 5), Some(1));
        assert_eq!(c.pixel(20, 5), Some(1));
        assert_eq!(c.pixel(10, 0), Some(1));
        assert_eq!(c.pixel(10, 10), Some(1));
        assert_eq!(c.pixel(0, 0), Some(0));
        for y in 0..11 {
            for x in 0..21 {
                assert_eq!(c.pixel(x, y), c.pixel(20 - x, y));
                assert_eq!(c.pixel(x, y), c.pixel(x, 10 - y));
            }
        }
    }

    #[test]
    fn fill_poly_fills_triangle_interior() {
        let mut c = Canvas::new(10, 10);
        c.fill_poly(&[(0, 0), (9, 0), (0, 9)], Fill::solid(7));
        assert_eq!(c.pixel(1, 1), Some(7));
        assert_eq!(c.pixel(8, 8), Some(0));
    }

    #[test]
    fn generation_tracks_changes() {
        let mut c = Canvas::new(4, 4);
        let g = c.generation();
        assert_eq!(c.pixel(1, 1), Some(0));
        assert_eq!(c.generation(), g);
        c.put_pixel(1, 1, 3);
        assert_ne!(c.generation(), g);
        // Repainting the same colour is not a change.
        let g = c.generation();
        c.put_pixel(1, 1, 3);
        c.bar(1, 1, 1, 1, Fill::solid(3));
        assert_eq!(c.generation(), g);
    }

    #[test]
    fn blit_and_crop_clip_at_edges() {
        let mut c = Canvas::new(4, 4);
        c.bar(0, 0, 3, 3, Fill::solid(2));
        let part = c.crop(2, 2, 4, 4);
        assert_eq!(part.pixel(1, 1), Some(2));
        assert_eq!(part.pixel(2, 2), Some(0));
        let mut d = Canvas::new(4, 4);
        d.blit(&part, -1, -1, None);
        assert_eq!(d.pixel(0, 0), Some(2));
        assert_eq!(d.pixel(1, 1), Some(0));
    }

    #[test]
    fn blit_respects_transparency() {
        let mut sprite = Canvas::new(2, 1);
        sprite.put_pixel(0, 0, 9);
        sprite.put_pixel(1, 0, 255);
        let mut c = Canvas::new(4, 1);
        c.clear(3);
        c.blit(&sprite, 1, 0, Some(255));
        assert_eq!(c.pixels(), &[3, 9, 3, 3]);
    }
}
