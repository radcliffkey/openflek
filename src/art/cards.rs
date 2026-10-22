//! Card sprites: faces from a bundled 16-colour bitmap of the deck, backs and
//! the octagonal frame drawn at runtime.

use crate::game::cards::Card;
use crate::gfx::{Canvas, Fill, color};

/// Size of the face artwork; it sits inside the card frame at (2, 2).
pub const FACE_W: i32 = 61;
pub const FACE_H: i32 = 100;
/// Nominal card size (outer octagon).
pub const CARD_W: i32 = 64;
pub const CARD_H: i32 = 103;
/// Sprite size including the drop shadow.
pub const SPRITE_W: i32 = CARD_W + 3;
pub const SPRITE_H: i32 = CARD_H + 3;

/// Colour index of sprite pixels that are not part of the card.
pub const TRANSPARENT: u8 = 255;

const OUTER: [(i32, i32); 8] = [
    (3, 0),
    (61, 0),
    (64, 3),
    (64, 100),
    (61, 103),
    (3, 103),
    (0, 100),
    (0, 3),
];
const INNER: [(i32, i32); 8] = [
    (4, 3),
    (60, 3),
    (61, 4),
    (61, 99),
    (60, 100),
    (4, 100),
    (3, 99),
    (3, 4),
];
const SHADOW: [(i32, i32); 8] = [
    (65, 4),
    (64, 101),
    (62, 103),
    (4, 104),
    (5, 105),
    (63, 105),
    (66, 102),
    (66, 5),
];

/// Paints the white ring between the outer and inner octagon plus both outlines.
fn draw_frame(c: &mut Canvas) {
    let ring: Vec<(i32, i32)> = OUTER
        .iter()
        .chain([&OUTER[0]])
        .chain(INNER.iter())
        .chain([&INNER[0]])
        .copied()
        .collect();
    c.fill_poly(&ring, Fill::solid(color::WHITE));
    c.poly(&OUTER, color::DARK_GRAY);
    c.poly(&INNER, color::DARK_GRAY);
    c.fill_poly(&SHADOW, Fill::solid(color::DARK_GRAY));
    c.poly(&SHADOW, color::DARK_GRAY);
}

fn empty_sprite() -> Canvas {
    let mut c = Canvas::new(SPRITE_W, SPRITE_H);
    c.clear(TRANSPARENT);
    c.fill_poly(&OUTER, Fill::solid(color::WHITE));
    c
}

/// A complete face-up card: frame, shadow and artwork.
pub fn render_card_sprite(card: Card) -> Canvas {
    let mut c = empty_sprite();
    c.blit(&render_face(card), 2, 2, None);
    draw_frame(&mut c);
    c
}

/// The card back in `line_color`, laid out like a face so it sits in the frame
/// the same way.
pub fn render_back_sprite(line_color: u8) -> Canvas {
    let mut c = empty_sprite();
    c.blit(&render_back_face(line_color), 2, 2, None);
    draw_frame(&mut c);
    c
}

/// The 61x100 back artwork: the dark-grey inner border every face has, then
/// the pattern from `back_pixel`.
fn render_back_face(line_color: u8) -> Canvas {
    let mut c = Canvas::new(FACE_W, FACE_H);
    c.clear(color::WHITE);
    c.line(2, 1, FACE_W - 3, 1, color::DARK_GRAY);
    c.line(2, FACE_H - 2, FACE_W - 3, FACE_H - 2, color::DARK_GRAY);
    c.line(1, 2, 1, FACE_H - 3, color::DARK_GRAY);
    c.line(FACE_W - 2, 2, FACE_W - 2, FACE_H - 3, color::DARK_GRAY);
    for y in 2..FACE_H - 2 {
        for x in 2..FACE_W - 2 {
            c.put_pixel(x, y, back_pixel(line_color, x, y));
        }
    }
    c
}

/// Lighter partner of each back colour (1..=7) for petals and tinted cells.
fn back_light(line_color: u8) -> u8 {
    match line_color {
        color::BLUE => color::LIGHT_BLUE,
        color::GREEN => color::LIGHT_GREEN,
        color::CYAN => color::LIGHT_CYAN,
        color::RED => color::LIGHT_RED,
        color::MAGENTA => color::LIGHT_MAGENTA,
        color::BROWN => color::YELLOW,
        color::LIGHT_GRAY => color::LIGHT_GRAY,
        _ => color::WHITE,
    }
}

/// The back pattern at face pixel (x, y), for x in 2..=58 and y in 2..=97:
/// a double border, fans in the corners, a diamond lattice with a flower in
/// each cell and alternate cells tinted, and a medallion holding an
/// eight-petalled rosette.
///
/// Everything is measured from the centre, so the back is mirror symmetric
/// both ways and looks the same either way up. Mirrors
/// `scripts/deck_gen/palette.py::back_colour`.
fn back_pixel(line_color: u8, x: i32, y: i32) -> u8 {
    let dark = if line_color == color::LIGHT_GRAY {
        color::DARK_GRAY
    } else {
        line_color
    };
    let light = back_light(line_color);
    // Quadrant coordinates: rows 49 and 50 are both the middle row.
    let qx = (x - 30).abs();
    let qy = ((2 * y - 99).abs() - 1) / 2;

    // Border: a dark rule, a light band, another dark rule.
    let edge = (x - 2).min(58 - x).min(y - 2).min(97 - y);
    match edge {
        0 => return color::WHITE,
        1 | 4 => return dark,
        2 | 3 => return if (qx + qy) % 4 != 0 { light } else { dark },
        _ => {}
    }

    // Fans in the four corners of the field.
    let (fx, fy) = (f64::from(23 - qx), f64::from(42 - qy));
    let fr = fx.hypot(fy);
    if fx >= 0.0 && fy >= 0.0 && fr <= 9.0 {
        if fr > 8.0 || (fr as i32) % 3 == 0 {
            return dark;
        }
        let ray = (fy.atan2(fx).to_degrees() / 15.0) as i32;
        return if ray % 2 != 0 { light } else { color::WHITE };
    }

    // Central medallion with a rosette.
    let (mx, my) = (f64::from(qx), f64::from(qy) + 0.5);
    let mr = (mx / 15.0).hypot(my / 19.0);
    if mr <= 1.0 {
        if mr > 0.92 {
            return dark;
        }
        if mr > 0.84 {
            return if (qx + qy) % 2 != 0 {
                light
            } else {
                color::WHITE
            };
        }
        let petal = 0.25 + 0.55 * (4.0 * my.atan2(mx)).cos().abs();
        if mr < 0.14 {
            return dark;
        }
        if mr < petal {
            return if mr > petal - 0.08 { dark } else { light };
        }
        return color::WHITE;
    }

    // Diamond lattice with a flower in each cell.
    let (a, b) = ((qx + qy).rem_euclid(8), (qx - qy).rem_euclid(8));
    if a == 0 || b == 0 || (a == 4 && b == 4) {
        return dark;
    }
    if (a == 4 && (b == 3 || b == 5)) || (b == 4 && (a == 3 || a == 5)) {
        return light;
    }
    // Every other cell is tinted, so the lattice reads as a chequer of diamonds.
    let cell = (qx + qy).div_euclid(8) + (qx - qy).div_euclid(8);
    if cell.rem_euclid(2) == 1 && (qx + qy) % 2 == 1 {
        return light;
    }
    color::WHITE
}

/// The 32 faces in card-id order, row-major, two pixels per byte (high nibble first).
const DECK_BYTES: &[u8] = include_bytes!("deck_data.bin");
const FACE_BYTES: usize = (FACE_W * FACE_H) as usize / 2;
const _: () = assert!(DECK_BYTES.len() == 32 * FACE_BYTES);

/// The bare 61x100 face artwork of a card.
pub fn render_face(card: Card) -> Canvas {
    let mut c = Canvas::new(FACE_W, FACE_H);
    let offset = card.id() as usize * FACE_BYTES;
    for y in 0..FACE_H {
        for x in 0..FACE_W {
            let idx = (y * FACE_W + x) as usize;
            let byte = DECK_BYTES[offset + idx / 2];
            let col = if (idx & 1) == 0 {
                byte >> 4
            } else {
                byte & 0x0f
            };
            c.put_pixel(x, y, col);
        }
    }
    c
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sprites_have_card_size_and_transparent_outside() {
        for id in 0..32 {
            let c = render_card_sprite(Card::from_id(id));
            assert_eq!((c.width(), c.height()), (SPRITE_W, SPRITE_H));
            assert_eq!(c.pixel(0, 0), Some(TRANSPARENT));
            assert_eq!(c.pixel(SPRITE_W - 1, 0), Some(TRANSPARENT));
            assert_eq!(c.pixel(3, 0), Some(color::DARK_GRAY));
            assert_eq!(c.pixel(1, 1), Some(color::WHITE));
        }
    }

    #[test]
    fn all_faces_look_different() {
        let faces: Vec<Canvas> = (0..32).map(|id| render_face(Card::from_id(id))).collect();
        for i in 0..faces.len() {
            for j in i + 1..faces.len() {
                assert_ne!(faces[i], faces[j], "cards {i} and {j} render identically");
            }
        }
    }

    #[test]
    fn back_uses_requested_line_colour_and_keeps_frame() {
        let c = render_back_sprite(color::MAGENTA);
        assert!(c.pixels().contains(&color::MAGENTA));
        assert!(c.pixels().contains(&color::LIGHT_MAGENTA));
        assert_eq!(c.pixel(0, 0), Some(TRANSPARENT));
        assert_eq!(c.pixel(66, 50), Some(color::DARK_GRAY));
    }

    #[test]
    fn back_looks_the_same_either_way_up() {
        // Backs only ever use colours 1..=7 (see `app::table::back_color`).
        for line in 1..=7 {
            let f = render_back_face(line);
            for y in 0..FACE_H {
                for x in 0..FACE_W {
                    let p = f.pixel(x, y);
                    assert_eq!(
                        p,
                        f.pixel(x, FACE_H - 1 - y),
                        "colour {line}: ({x}, {y}) vs its mirror below"
                    );
                    assert_eq!(
                        p,
                        f.pixel(FACE_W - 1 - x, y),
                        "colour {line}: ({x}, {y}) vs its mirror across"
                    );
                }
            }
        }
    }

    #[test]
    fn back_border_matches_the_faces() {
        // The back sits in the frame like a face: same dark-grey inner border.
        let back = render_back_face(color::BLUE);
        let face = render_face(Card::from_id(0));
        for (x, y) in [(1, 50), (59, 50), (30, 1), (30, 98), (0, 50), (1, 1)] {
            assert_eq!(back.pixel(x, y), face.pixel(x, y), "({x}, {y})");
        }
    }

    #[test]
    fn back_has_rosette_lattice_and_no_lettering() {
        let f = render_back_face(color::RED);
        // The rosette's centre and a petal on the vertical axis.
        assert_eq!(f.pixel(30, 49), Some(color::RED));
        assert_eq!(f.pixel(30, 44), Some(color::LIGHT_RED));
        // Black only ever came from the old monogram's shadow.
        assert!(!f.pixels().contains(&color::BLACK));
        // A grey back draws its lines in dark grey so they show on white.
        assert!(
            render_back_face(color::LIGHT_GRAY)
                .pixels()
                .contains(&color::DARK_GRAY)
        );
    }
}
