//! Small vector-to-pixel painting helpers used by the card artwork:
//! filled shapes with optional outline and two-colour dithered shading.

use crate::gfx::{Canvas, Fill, Pattern};

/// How a shape is filled.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Shade {
    Solid(u8),
    /// 50 % checkerboard of two colours.
    Dither(u8, u8),
    /// An arbitrary 8x8 pattern: set bits in the first colour.
    Pattern(Pattern, u8, u8),
}

impl Shade {
    pub fn fill(self) -> Fill {
        match self {
            Shade::Solid(c) => Fill::solid(c),
            Shade::Dither(a, b) => Fill::pattern(Pattern::CHECKER, a, b),
            Shade::Pattern(p, a, b) => Fill::pattern(p, a, b),
        }
    }
}

pub type Pt = (f32, f32);

fn to_px(points: &[Pt]) -> Vec<(i32, i32)> {
    points
        .iter()
        .map(|&(x, y)| (x.round() as i32, y.round() as i32))
        .collect()
}

/// A filled polygon with an optional outline.
pub fn shape(c: &mut Canvas, points: &[Pt], shade: Shade, outline: Option<u8>) {
    let px = to_px(points);
    c.fill_poly(&px, shade.fill());
    if let Some(o) = outline {
        c.poly(&px, o);
    }
}

/// A closed polygon outline.
pub fn outline(c: &mut Canvas, points: &[Pt], color: u8) {
    c.poly(&to_px(points), color);
}

/// An open polyline.
pub fn path(c: &mut Canvas, points: &[Pt], color: u8) {
    let px = to_px(points);
    for w in px.windows(2) {
        c.line(w[0].0, w[0].1, w[1].0, w[1].1, color);
    }
}

pub fn line(c: &mut Canvas, a: Pt, b: Pt, color: u8) {
    path(c, &[a, b], color);
}

/// The unit direction from `a` to `b` and its left-hand normal.
pub fn direction(a: Pt, b: Pt) -> (Pt, Pt) {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len = (dx * dx + dy * dy).sqrt().max(0.001);
    ((dx / len, dy / len), (-dy / len, dx / len))
}

/// The point `t` of the way from `a` to `b`.
pub fn mid(a: Pt, b: Pt, t: f32) -> Pt {
    (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
}

/// Corners of the tapered quad from `a` (width `wa`) to `b` (width `wb`):
/// left side a→b, then right side b→a.
pub fn limb_quad(a: Pt, b: Pt, wa: f32, wb: f32) -> [Pt; 4] {
    let (_, (nx, ny)) = direction(a, b);
    [
        (a.0 + nx * wa / 2.0, a.1 + ny * wa / 2.0),
        (b.0 + nx * wb / 2.0, b.1 + ny * wb / 2.0),
        (b.0 - nx * wb / 2.0, b.1 - ny * wb / 2.0),
        (a.0 - nx * wa / 2.0, a.1 - ny * wa / 2.0),
    ]
}

/// A polyline `width` pixels thick.
pub fn thick_path(c: &mut Canvas, points: &[Pt], width: f32, color: u8) {
    for w in points.windows(2) {
        thick_line(c, w[0], w[1], width, color);
    }
}

/// A line `width` pixels thick (drawn as a quad).
pub fn thick_line(c: &mut Canvas, a: Pt, b: Pt, width: f32, color: u8) {
    limb(c, a, b, width, width, Shade::Solid(color), None);
}

/// A tapered quad from `a` (width `wa`) to `b` (width `wb`); used for limbs,
/// staffs and blades.
pub fn limb(c: &mut Canvas, a: Pt, b: Pt, wa: f32, wb: f32, shade: Shade, outline: Option<u8>) {
    shape(c, &limb_quad(a, b, wa, wb), shade, outline);
}

/// A filled ellipse with optional outline.
pub fn blob(c: &mut Canvas, cx: f32, cy: f32, rx: f32, ry: f32, shade: Shade, outline: Option<u8>) {
    let (x, y, rx, ry) = (
        cx.round() as i32,
        cy.round() as i32,
        rx.round() as i32,
        ry.round() as i32,
    );
    c.fill_ellipse(x, y, rx, ry, shade.fill());
    if let Some(o) = outline {
        c.ellipse(x, y, rx, ry, o);
    }
}

/// Points along an elliptical arc; angles in degrees, 0 = right, 90 = down.
pub fn arc_points(cx: f32, cy: f32, rx: f32, ry: f32, from: f32, to: f32, steps: usize) -> Vec<Pt> {
    (0..=steps)
        .map(|i| {
            let a = (from + (to - from) * i as f32 / steps as f32).to_radians();
            (cx + rx * a.cos(), cy + ry * a.sin())
        })
        .collect()
}

pub fn dot(c: &mut Canvas, p: Pt, color: u8) {
    c.put_pixel(p.0.round() as i32, p.1.round() as i32, color);
}

/// Mirrors x around the vertical axis `axis`.
pub fn mirror(points: &[Pt], axis: f32) -> Vec<Pt> {
    points.iter().map(|&(x, y)| (2.0 * axis - x, y)).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn limb_covers_its_axis() {
        let mut c = Canvas::new(20, 20);
        limb(
            &mut c,
            (2.0, 10.0),
            (17.0, 10.0),
            4.0,
            2.0,
            Shade::Solid(3),
            None,
        );
        for x in 3..16 {
            assert_eq!(c.pixel(x, 10), Some(3), "x={x}");
        }
        assert_eq!(c.pixel(10, 2), Some(0));
    }

    #[test]
    fn dither_alternates_colours() {
        let mut c = Canvas::new(4, 4);
        shape(
            &mut c,
            &[(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)],
            Shade::Dither(1, 2),
            None,
        );
        assert_ne!(c.pixel(1, 1), c.pixel(2, 1));
        assert_eq!(c.pixel(1, 1), c.pixel(2, 2));
    }

    #[test]
    fn mirror_and_mid() {
        assert_eq!(mirror(&[(1.0, 2.0)], 5.0), vec![(9.0, 2.0)]);
        assert_eq!(mid((0.0, 0.0), (4.0, 2.0), 0.5), (2.0, 1.0));
    }
}
