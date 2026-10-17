//! Procedurally drawn card faces and backs, in the spirit of the classic
//! Czech "William Tell" Mariáš deck at EGA resolution.

use super::aces::draw_ace;
use super::court::draw_court;
use super::numbers::draw_number;
use crate::game::cards::{Card, Rank};
use crate::gfx::font::draw_text_shadowed;
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

/// White face with a thin grey border one pixel in, matching the inner frame.
fn blank() -> Canvas {
    let mut c = Canvas::new(FACE_W, FACE_H);
    c.clear(color::WHITE);
    c.rect(1, 1, FACE_W - 2, FACE_H - 2, color::DARK_GRAY);
    c
}

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

/// The card back: a sunburst of thin lines in `line_color` with a monogram.
pub fn render_back_sprite(line_color: u8) -> Canvas {
    let mut c = empty_sprite();
    for x in (0..=CARD_W).step_by(4) {
        c.line(x, 2, CARD_W - x, 101, line_color);
    }
    for y in (10..=95).step_by(4) {
        c.line(2, y, 62, 103 - y, line_color);
    }
    // Clip the line ends to the card shape before painting the frame.
    for y in 0..SPRITE_H {
        for x in 0..SPRITE_W {
            if !inside_outer(x, y) {
                c.put_pixel(x, y, TRANSPARENT);
            }
        }
    }
    draw_frame(&mut c);
    draw_text_shadowed(&mut c, 25, 43, "O", color::WHITE, color::BLACK, 0);
    draw_text_shadowed(&mut c, 30, 52, "F", color::WHITE, color::BLACK, 0);
    c
}

fn inside_outer(x: i32, y: i32) -> bool {
    (0..=CARD_W).contains(&x)
        && (0..=CARD_H).contains(&y)
        && x + y >= 3
        && (CARD_W - x) + y >= 3
        && x + (CARD_H - y) >= 3
        && (CARD_W - x) + (CARD_H - y) >= 3
}

/// The bare 61x100 face artwork of a card.
pub fn render_face(card: Card) -> Canvas {
    let mut c = blank();
    match card.rank() {
        Rank::Seven | Rank::Eight | Rank::Nine | Rank::Ten => {
            draw_number(&mut c, card.suit(), card.rank())
        }
        Rank::Under | Rank::Over | Rank::King => draw_court(&mut c, card.suit(), card.rank()),
        Rank::Ace => draw_ace(&mut c, card.suit()),
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
        assert_eq!(c.pixel(0, 0), Some(TRANSPARENT));
        assert_eq!(c.pixel(66, 50), Some(color::DARK_GRAY));
    }
}
