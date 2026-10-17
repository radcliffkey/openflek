//! Small scenery pieces shared by the card faces: ground, buildings,
//! animals, tiny people and plants.

use super::figure::dark;
use super::paint::{Shade, arc_points, blob, dot, limb, line, path, shape, thick_line};
use super::symbols::draw_symbol;
use crate::game::cards::Suit;
use crate::gfx::{Canvas, Fill, Pattern, color::*};

/// Top of the ground strip on card faces.
pub const GROUND: i32 = 87;

/// Grassy ground with sunny patches; `seed` varies the patch layout.
/// Fills the ground strip at the foot of a card face.
pub fn ground(c: &mut Canvas, fill: Fill) {
    c.bar(2, GROUND, 58, 97, fill);
}

/// Two suit pips in the top corners of court cards and aces.
pub fn corner_pips(c: &mut Canvas, suit: Suit) {
    draw_symbol(c, suit, 10, 10, 1);
    draw_symbol(c, suit, 50, 10, 1);
}

pub fn meadow(c: &mut Canvas, seed: u8) {
    ground(c, Fill::solid(GREEN));
    let s = seed as f32 * 7.0;
    let patches = [
        (8.0 + s % 9.0, 7.0),
        (32.0 - s % 6.0, 6.0),
        (50.0 + s % 5.0, 5.0),
    ];
    for (i, &(x, rx)) in patches.iter().enumerate() {
        let shade = if i % 2 == 0 {
            Shade::Dither(YELLOW, GREEN)
        } else {
            Shade::Solid(YELLOW)
        };
        blob(c, x, 95.0, rx * 1.6, 5.0 + (i % 2) as f32, shade, None);
        blob(c, x + rx * 0.6, 92.0, rx * 0.7, 2.0, shade, None);
    }
    // The ground strip must not spill past the face border.
    c.line(1, 98, 59, 98, DARK_GRAY);
    for x in [6, 19, 37, 53] {
        grass(c, (x + s as i32) % 54 + 3, GROUND);
    }
}

pub fn grass(c: &mut Canvas, x: i32, y: i32) {
    c.line(x, y - 2, x - 1, y, LIGHT_GREEN);
    c.line(x + 1, y - 3, x + 1, y, GREEN);
    c.line(x + 2, y - 2, x + 3, y, LIGHT_GREEN);
}

/// A tiled floor.
pub fn floor(c: &mut Canvas, a: u8, b: u8) {
    ground(c, Fill::pattern(Pattern::SLASH, a, b));
    c.line(2, GROUND, 58, GROUND, dark(a));
}

/// A small cottage standing on `y`, left edge at `x`.
pub fn cottage(c: &mut Canvas, x: i32, y: i32) {
    let (xf, yf) = (x as f32, y as f32);
    shape(
        c,
        &[
            (xf, yf - 11.0),
            (xf + 15.0, yf - 11.0),
            (xf + 15.0, yf),
            (xf, yf),
        ],
        Shade::Dither(WHITE, LIGHT_GRAY),
        Some(DARK_GRAY),
    );
    shape(
        c,
        &[
            (xf - 2.0, yf - 10.0),
            (xf + 7.5, yf - 19.0),
            (xf + 17.0, yf - 10.0),
        ],
        Shade::Pattern(Pattern::HORIZONTAL, RED, LIGHT_RED),
        Some(RED),
    );
    c.bar(x + 10, y - 19, x + 12, y - 14, Fill::solid(RED));
    for (i, p) in arc_points(xf + 14.0, yf - 23.0, 3.0, 2.0, 180.0, 400.0, 5)
        .iter()
        .enumerate()
    {
        dot(c, (p.0 + i as f32, p.1 - i as f32), LIGHT_GRAY);
    }
    c.bar(x + 3, y - 7, x + 6, y - 1, Fill::solid(BROWN));
    c.bar(x + 9, y - 8, x + 12, y - 5, Fill::solid(LIGHT_CYAN));
    c.rect(x + 9, y - 8, x + 12, y - 5, BROWN);
}

/// A tiny standing person, feet at (x, y).
pub fn tiny_person(c: &mut Canvas, x: i32, y: i32, hat: u8, coat: u8, legs: u8) {
    let (xf, yf) = (x as f32, y as f32);
    limb(
        c,
        (xf - 1.5, yf - 6.0),
        (xf - 2.0, yf),
        2.0,
        2.0,
        Shade::Solid(legs),
        None,
    );
    limb(
        c,
        (xf + 1.5, yf - 6.0),
        (xf + 2.0, yf),
        2.0,
        2.0,
        Shade::Solid(legs),
        None,
    );
    shape(
        c,
        &[
            (xf - 3.0, yf - 13.0),
            (xf + 3.0, yf - 13.0),
            (xf + 4.0, yf - 5.0),
            (xf - 4.0, yf - 5.0),
        ],
        Shade::Solid(coat),
        Some(dark(coat)),
    );
    limb(
        c,
        (xf + 3.0, yf - 12.0),
        (xf + 5.0, yf - 7.0),
        2.0,
        2.0,
        Shade::Solid(coat),
        None,
    );
    blob(
        c,
        xf,
        yf - 15.0,
        2.0,
        2.0,
        Shade::Solid(WHITE),
        Some(DARK_GRAY),
    );
    shape(
        c,
        &[
            (xf - 3.0, yf - 16.0),
            (xf + 3.0, yf - 16.0),
            (xf + 1.0, yf - 19.0),
            (xf - 1.0, yf - 19.0),
        ],
        Shade::Solid(hat),
        None,
    );
    line(c, (xf - 4.0, yf - 16.0), (xf + 4.0, yf - 16.0), hat);
    dot(c, (xf - 2.0, yf), BLACK);
    dot(c, (xf + 2.0, yf), BLACK);
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Beast {
    Dog,
    Horse,
    Deer,
    Boar,
    Sheep,
}

/// A four-legged animal facing right, standing on `y`, centred on `x`.
pub fn beast(c: &mut Canvas, kind: Beast, x: i32, y: i32) {
    let (xf, yf) = (x as f32, y as f32);
    let (len, height, leg, col) = match kind {
        Beast::Dog => (8.0, 3.0, 5.0, YELLOW),
        Beast::Horse => (11.0, 5.0, 9.0, LIGHT_GRAY),
        Beast::Deer => (9.0, 4.0, 9.0, BROWN),
        Beast::Boar => (9.0, 5.0, 4.0, DARK_GRAY),
        Beast::Sheep => (8.0, 5.0, 4.0, WHITE),
    };
    let body_y = yf - leg - height;
    for (dx, back) in [
        (-len + 2.0, 0.0),
        (-len + 4.0, 1.0),
        (len - 4.0, 0.0),
        (len - 2.0, 1.0),
    ] {
        let knee = (xf + dx + back, body_y + leg * 0.6);
        path(
            c,
            &[(xf + dx, body_y + 2.0), knee, (xf + dx + back * 0.5, yf)],
            dark(col),
        );
    }
    let shade = if kind == Beast::Sheep {
        Shade::Pattern(Pattern::CLOSE_DOTS, LIGHT_GRAY, WHITE)
    } else {
        Shade::Dither(col, dark(col))
    };
    blob(c, xf, body_y, len, height, shade, Some(dark(col)));
    blob(
        c,
        xf - 2.0,
        body_y - 1.0,
        len - 4.0,
        height - 2.0,
        Shade::Solid(col),
        None,
    );
    let neck = (xf + len - 1.0, body_y - 1.0);
    let head = match kind {
        Beast::Horse => (xf + len + 4.0, body_y - height - 2.0),
        Beast::Deer => (xf + len + 3.0, body_y - height - 4.0),
        Beast::Boar | Beast::Sheep => (xf + len + 2.0, body_y),
        Beast::Dog => (xf + len + 2.0, body_y - height - 1.0),
    };
    thick_line(c, neck, head, 3.0, col);
    blob(
        c,
        head.0 + 1.0,
        head.1,
        3.0,
        2.0,
        Shade::Solid(col),
        Some(dark(col)),
    );
    dot(c, (head.0 + 1.0, head.1 - 1.0), BLACK);
    match kind {
        Beast::Horse => {
            blob(
                c,
                head.0 + 3.0,
                head.1 + 1.0,
                3.0,
                2.0,
                Shade::Solid(col),
                Some(dark(col)),
            );
            thick_line(
                c,
                (neck.0 - 2.0, neck.1 - 3.0),
                (head.0 - 1.0, head.1 - 2.0),
                2.0,
                DARK_GRAY,
            );
            path(
                c,
                &[(head.0, head.1 - 2.0), (head.0 - 1.0, head.1 - 4.0)],
                DARK_GRAY,
            );
            path(
                c,
                &[(xf - len, body_y), (xf - len - 3.0, body_y + 6.0)],
                DARK_GRAY,
            );
        }
        Beast::Deer => {
            path(
                c,
                &[
                    (head.0, head.1 - 2.0),
                    (head.0 - 2.0, head.1 - 7.0),
                    (head.0 - 5.0, head.1 - 9.0),
                ],
                BROWN,
            );
            path(
                c,
                &[(head.0 - 2.0, head.1 - 6.0), (head.0 + 1.0, head.1 - 9.0)],
                BROWN,
            );
            dot(c, (xf - len, body_y - 1.0), WHITE);
        }
        Beast::Boar => {
            dot(c, (head.0 + 4.0, head.1 + 1.0), WHITE);
            path(
                c,
                &[(xf - 3.0, body_y - height), (xf + 4.0, body_y - height)],
                BLACK,
            );
        }
        Beast::Dog => {
            path(
                c,
                &[(xf - len, body_y), (xf - len - 3.0, body_y - 4.0)],
                dark(col),
            );
            dot(c, (head.0 - 1.0, head.1 - 2.0), BROWN);
        }
        Beast::Sheep => {}
    }
}

/// A small bird facing right, sitting at (x, y).
pub fn bird(c: &mut Canvas, x: i32, y: i32, body: u8) {
    let (xf, yf) = (x as f32, y as f32);
    shape(
        c,
        &[
            (xf - 7.0, yf - 4.0),
            (xf - 3.0, yf - 2.0),
            (xf - 3.0, yf + 1.0),
        ],
        Shade::Solid(dark(body)),
        None,
    );
    blob(
        c,
        xf,
        yf,
        4.0,
        3.0,
        Shade::Dither(body, WHITE),
        Some(dark(body)),
    );
    blob(
        c,
        xf + 4.0,
        yf - 3.0,
        2.0,
        2.0,
        Shade::Solid(body),
        Some(dark(body)),
    );
    dot(c, (xf + 7.0, yf - 3.0), YELLOW);
    dot(c, (xf + 4.0, yf - 4.0), BLACK);
    path(
        c,
        &[
            (xf - 2.0, yf - 1.0),
            (xf + 1.0, yf + 1.0),
            (xf + 2.0, yf - 1.0),
        ],
        dark(body),
    );
    line(c, (xf, yf + 3.0), (xf, yf + 5.0), RED);
}

/// A flower with petals of `petal` colour on a stem rising from (x, y).
pub fn flower(c: &mut Canvas, x: i32, y: i32, height: i32, petal: u8) {
    let (xf, yf) = (x as f32, y as f32);
    let top = yf - height as f32;
    line(c, (xf, yf), (xf, top), GREEN);
    blob(
        c,
        xf - 2.0,
        yf - height as f32 * 0.5,
        2.0,
        1.0,
        Shade::Solid(LIGHT_GREEN),
        None,
    );
    blob(
        c,
        xf + 2.0,
        yf - height as f32 * 0.35,
        2.0,
        1.0,
        Shade::Solid(LIGHT_GREEN),
        None,
    );
    for (dx, dy) in [(-2.0, 0.0), (2.0, 0.0), (0.0, -2.0), (0.0, 2.0)] {
        blob(c, xf + dx, top + dy, 1.0, 1.0, Shade::Solid(petal), None);
    }
    dot(c, (xf, top), YELLOW);
}

/// A striped flower pot with three flowers, standing on `y`.
pub fn flower_pot(c: &mut Canvas, x: i32, y: i32) {
    let (xf, yf) = (x as f32, y as f32);
    flower(c, x - 4, y - 9, 9, LIGHT_RED);
    flower(c, x, y - 9, 14, LIGHT_MAGENTA);
    flower(c, x + 4, y - 9, 8, YELLOW);
    shape(
        c,
        &[
            (xf - 7.0, yf - 10.0),
            (xf + 7.0, yf - 10.0),
            (xf + 5.0, yf),
            (xf - 5.0, yf),
        ],
        Shade::Pattern(Pattern::HORIZONTAL, RED, YELLOW),
        Some(BROWN),
    );
}

/// A wooden tub with a bush of flowers, standing on `y`.
pub fn tub(c: &mut Canvas, x: i32, y: i32) {
    let (xf, yf) = (x as f32, y as f32);
    blob(
        c,
        xf,
        yf - 16.0,
        8.0,
        6.0,
        Shade::Dither(GREEN, LIGHT_GREEN),
        Some(GREEN),
    );
    for (dx, dy, p) in [
        (-5, -18, LIGHT_RED),
        (0, -21, RED),
        (4, -16, LIGHT_RED),
        (-1, -14, YELLOW),
    ] {
        blob(
            c,
            xf + dx as f32,
            yf + dy as f32,
            1.0,
            1.0,
            Shade::Solid(p),
            None,
        );
    }
    shape(
        c,
        &[
            (xf - 9.0, yf - 10.0),
            (xf + 9.0, yf - 10.0),
            (xf + 8.0, yf),
            (xf - 8.0, yf),
        ],
        Shade::Pattern(Pattern::HATCH, BROWN, YELLOW),
        Some(BROWN),
    );
    line(c, (xf - 9.0, yf - 7.0), (xf + 9.0, yf - 7.0), DARK_GRAY);
    line(c, (xf - 8.0, yf - 3.0), (xf + 8.0, yf - 3.0), DARK_GRAY);
}

/// A fountain with a basin and two water arcs, standing on `y`.
pub fn fountain(c: &mut Canvas, x: i32, y: i32) {
    let (xf, yf) = (x as f32, y as f32);
    for side in [-1.0, 1.0] {
        let arc = arc_points(
            xf + side * 6.0,
            yf - 14.0,
            6.0,
            8.0,
            if side < 0.0 { 180.0 } else { 270.0 },
            if side < 0.0 { 270.0 } else { 360.0 },
            6,
        );
        path(c, &arc, LIGHT_CYAN);
    }
    limb(
        c,
        (xf, yf - 7.0),
        (xf, yf - 21.0),
        3.0,
        2.0,
        Shade::Solid(LIGHT_GRAY),
        Some(DARK_GRAY),
    );
    blob(c, xf, yf - 22.0, 2.0, 1.0, Shade::Solid(LIGHT_CYAN), None);
    shape(
        c,
        &[
            (xf - 11.0, yf - 7.0),
            (xf + 11.0, yf - 7.0),
            (xf + 9.0, yf),
            (xf - 9.0, yf),
        ],
        Shade::Dither(LIGHT_GRAY, WHITE),
        Some(DARK_GRAY),
    );
    blob(c, xf, yf - 7.0, 10.0, 1.0, Shade::Solid(CYAN), None);
}

/// A small fir tree standing on `y`.
pub fn fir(c: &mut Canvas, x: i32, y: i32, height: i32) {
    let (xf, yf, h) = (x as f32, y as f32, height as f32);
    c.bar(x - 1, y - 3, x, y, Fill::solid(BROWN));
    shape(
        c,
        &[
            (xf, yf - h),
            (xf + h * 0.35, yf - 3.0),
            (xf - h * 0.35, yf - 3.0),
        ],
        Shade::Dither(GREEN, LIGHT_GREEN),
        Some(GREEN),
    );
}
