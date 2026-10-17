//! The aces: ornamental heraldic compositions instead of figures.

use super::figure::dark;
use super::paint::{
    Pt, Shade, arc_points, blob, dot, limb, line, mirror, path, shape, thick_line, thick_path,
};
use super::scenery;
use super::symbols::draw_symbol;
use crate::game::cards::Suit;
use crate::gfx::font::{draw_text_shadowed, text_width};
use crate::gfx::{Canvas, Pattern, color::*};

const M: f32 = 30.0;

fn crown(c: &mut Canvas, x: f32, y: f32, w: f32) {
    shape(
        c,
        &[
            (x - w, y),
            (x - w - 2.0, y - 8.0),
            (x - w / 2.0, y - 4.0),
            (x, y - 11.0),
            (x + w / 2.0, y - 4.0),
            (x + w + 2.0, y - 8.0),
            (x + w, y),
        ],
        Shade::Dither(YELLOW, WHITE),
        Some(BROWN),
    );
    limb(
        c,
        (x - w, y - 1.0),
        (x + w, y - 1.0),
        3.0,
        3.0,
        Shade::Solid(RED),
        Some(BROWN),
    );
    for dx in [-w / 2.0, 0.0, w / 2.0] {
        dot(c, (x + dx, y - 1.0), LIGHT_CYAN);
    }
    for p in [
        (x - w - 2.0, y - 9.0),
        (x, y - 12.0),
        (x + w + 2.0, y - 9.0),
    ] {
        blob(c, p.0, p.1, 1.0, 1.0, Shade::Solid(WHITE), Some(BROWN));
    }
}

fn shield(c: &mut Canvas, cx: f32, top: f32, w: f32, h: f32, a: u8, b: u8) -> Vec<Pt> {
    let pts = vec![
        (cx - w, top),
        (cx + w, top),
        (cx + w, top + h * 0.55),
        (cx + w * 0.6, top + h * 0.85),
        (cx, top + h),
        (cx - w * 0.6, top + h * 0.85),
        (cx - w, top + h * 0.55),
    ];
    shape(c, &pts, Shade::Solid(a), None);
    shape(
        c,
        &[
            (cx, top),
            (cx + w, top),
            (cx + w, top + h * 0.55),
            (cx + w * 0.6, top + h * 0.85),
            (cx, top + h),
        ],
        Shade::Dither(a, b),
        None,
    );
    thick_path(c, &pts, 2.0, YELLOW);
    thick_line(c, pts[pts.len() - 1], pts[0], 2.0, YELLOW);
    pts
}

fn ribbon(c: &mut Canvas, y: f32, text: &str, cloth: u8) {
    let pts = [
        (4.0, y),
        (56.0, y),
        (52.0, y + 5.0),
        (56.0, y + 10.0),
        (4.0, y + 10.0),
        (8.0, y + 5.0),
    ];
    shape(c, &pts, Shade::Solid(cloth), Some(dark(cloth)));
    line(c, (9.0, y + 9.0), (51.0, y + 9.0), dark(cloth));
    draw_text_shadowed(
        c,
        30 - text_width(text) / 2,
        y as i32 + 1,
        text,
        YELLOW,
        BROWN,
        0,
    );
}

/// A C-shaped scroll ornament opening towards the centre.
fn scroll(c: &mut Canvas, x: f32, y: f32, left: bool, col: u8) {
    let (from, to) = if left { (60.0, 330.0) } else { (210.0, 480.0) };
    let outer = arc_points(x, y, 7.0, 9.0, from, to, 10);
    thick_path(c, &outer, 3.0, col);
    path(c, &outer, dark(col));
    blob(
        c,
        outer[outer.len() - 1].0,
        outer[outer.len() - 1].1,
        2.0,
        2.0,
        Shade::Solid(col),
        Some(dark(col)),
    );
}

fn acorn_ace(c: &mut Canvas) {
    scenery::meadow(c, 3);
    thick_line(c, (8.0, 84.0), (50.0, 22.0), 2.0, BROWN);
    thick_line(c, (52.0, 84.0), (10.0, 22.0), 2.0, BROWN);
    for (tip, dir) in [((50.0, 22.0), 1.0), ((10.0, 22.0), -1.0)] {
        shape(
            c,
            &[
                tip,
                (tip.0 + dir * 3.0, tip.1 - 7.0),
                (tip.0 - dir * 2.0, tip.1 - 2.0),
            ],
            Shade::Solid(LIGHT_CYAN),
            Some(BLUE),
        );
        shape(
            c,
            &[
                (tip.0 - dir, tip.1 + 2.0),
                (tip.0 - dir * 6.0, tip.1 + 1.0),
                (tip.0 - dir * 5.0, tip.1 + 7.0),
            ],
            Shade::Solid(LIGHT_CYAN),
            Some(BLUE),
        );
    }
    shield(c, M, 34.0, 14.0, 40.0, GREEN, LIGHT_GREEN);
    draw_symbol(c, Suit::Acorns, 30, 52, 2);
    crown(c, M, 32.0, 9.0);
    ribbon(c, 74.0, "FLEK", LIGHT_RED);
}

fn leaf_ace(c: &mut Canvas) {
    scenery::ground(c, Shade::Pattern(Pattern::INTERLEAVE, BLUE, CYAN).fill());
    let frame: Vec<Pt> = vec![
        (10.0, 30.0),
        (30.0, 24.0),
        (50.0, 30.0),
        (54.0, 58.0),
        (46.0, 80.0),
        (30.0, 86.0),
        (14.0, 80.0),
        (6.0, 58.0),
    ];
    shape(c, &frame, Shade::Solid(RED), Some(BROWN));
    let inner: Vec<Pt> = frame
        .iter()
        .map(|&(x, y)| (M + (x - M) * 0.78, 56.0 + (y - 56.0) * 0.8))
        .collect();
    shape(c, &inner, Shade::Dither(YELLOW, WHITE), Some(BROWN));
    scroll(c, 8.0, 40.0, true, LIGHT_RED);
    scroll(c, 52.0, 40.0, false, LIGHT_RED);
    scroll(c, 10.0, 74.0, true, YELLOW);
    scroll(c, 50.0, 74.0, false, YELLOW);
    draw_symbol(c, Suit::Leaves, 30, 56, 2);
    // Flowers growing out of the cartouche.
    for (x, h, p) in [
        (22, 12, LIGHT_RED),
        (30, 16, YELLOW),
        (38, 12, LIGHT_MAGENTA),
    ] {
        scenery::flower(c, x, 25, h, p);
    }
    for (x, y) in [(18.0, 64.0), (42.0, 64.0)] {
        blob(c, x, y, 2.0, 2.0, Shade::Solid(LIGHT_BLUE), Some(BLUE));
    }
}

fn bell_ace(c: &mut Canvas) {
    scenery::floor(c, RED, YELLOW);
    // Two rampant beasts as supporters, mirrored.
    let beast: Vec<Pt> = vec![
        (6.0, 84.0),
        (9.0, 60.0),
        (5.0, 50.0),
        (9.0, 40.0),
        (14.0, 38.0),
        (17.0, 46.0),
        (14.0, 56.0),
        (17.0, 70.0),
        (14.0, 84.0),
    ];
    for pts in [beast.clone(), mirror(&beast, M)] {
        shape(c, &pts, Shade::Dither(YELLOW, BROWN), Some(BROWN));
    }
    for x in [10.0, 50.0] {
        blob(c, x, 37.0, 4.0, 4.0, Shade::Solid(YELLOW), Some(BROWN));
        dot(c, (x, 36.0), BLACK);
        path(c, &[(x - 3.0, 41.0), (x, 44.0), (x + 3.0, 41.0)], RED);
    }
    let pts = shield(c, M, 36.0, 13.0, 42.0, LIGHT_RED, RED);
    line(c, (M, 36.0), (M, 78.0), YELLOW);
    line(c, pts[0], (pts[0].0 + 26.0, pts[0].1), YELLOW);
    draw_symbol(c, Suit::Bells, 30, 56, 2);
    crown(c, M, 34.0, 10.0);
}

fn heart_ace(c: &mut Canvas) {
    scenery::meadow(c, 9);
    for side in [-1.0f32, 1.0] {
        let from = if side < 0.0 { 100.0 } else { 80.0 };
        let to = if side < 0.0 { 260.0 } else { -80.0 };
        let arc = arc_points(M, 54.0, 22.0, 28.0, from, to, 9);
        thick_path(c, &arc, 2.0, GREEN);
        for (i, p) in arc.iter().enumerate().skip(1) {
            let lx = p.0 + side * if i % 2 == 0 { 3.0 } else { -3.0 };
            blob(
                c,
                lx,
                p.1,
                2.0,
                1.5,
                Shade::Dither(LIGHT_GREEN, GREEN),
                Some(GREEN),
            );
        }
    }
    // Ribbon bow at the bottom.
    shape(
        c,
        &[(M, 80.0), (M - 9.0, 76.0), (M - 9.0, 85.0)],
        Shade::Solid(LIGHT_RED),
        Some(RED),
    );
    shape(
        c,
        &[(M, 80.0), (M + 9.0, 76.0), (M + 9.0, 85.0)],
        Shade::Solid(LIGHT_RED),
        Some(RED),
    );
    blob(c, M, 80.0, 2.0, 2.0, Shade::Solid(RED), None);
    blob(
        c,
        M,
        54.0,
        15.0,
        19.0,
        Shade::Pattern(Pattern::CLOSE_DOTS, LIGHT_RED, WHITE),
        None,
    );
    draw_symbol(c, Suit::Hearts, 30, 54, 2);
    scenery::bird(c, 30, 24, LIGHT_BLUE);
}

pub fn draw_ace(c: &mut Canvas, suit: Suit) {
    match suit {
        Suit::Acorns => acorn_ace(c),
        Suit::Leaves => leaf_ace(c),
        Suit::Bells => bell_ace(c),
        Suit::Hearts => heart_ace(c),
    }
    scenery::corner_pips(c, suit);
}
