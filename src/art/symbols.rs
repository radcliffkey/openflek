//! Hand-made pixel art for the four German suit symbols.
//!
//! One character per pixel; `.` is transparent, the rest are EGA colours
//! (see [`palette_char`]).

use crate::game::cards::Suit;
use crate::gfx::{Canvas, Fill, color};

/// Maps a pixel-art character to an EGA colour index.
pub fn palette_char(ch: char) -> Option<u8> {
    Some(match ch {
        'k' => color::BLACK,
        'b' => color::BLUE,
        'G' => color::GREEN,
        'c' => color::CYAN,
        'R' => color::RED,
        'm' => color::MAGENTA,
        'B' => color::BROWN,
        'l' => color::LIGHT_GRAY,
        'K' => color::DARK_GRAY,
        'L' => color::LIGHT_BLUE,
        'g' => color::LIGHT_GREEN,
        'C' => color::LIGHT_CYAN,
        'r' => color::LIGHT_RED,
        'M' => color::LIGHT_MAGENTA,
        'Y' => color::YELLOW,
        'W' => color::WHITE,
        _ => return None,
    })
}

const HEART: &[&str] = &[
    "..RRRR...RRRR..",
    ".RrrrrR.RrrrrR.",
    "RrWWrrrRrrrrrRR",
    "RrWrrrrrrrrrrRR",
    "RrrrrrrrrrrrRrR",
    "RrrrrrrrrrrrrRR",
    ".RrrrrrrrrrrRR.",
    ".RrrrrrrrrrRrR.",
    "..RrrrrrrrrrR..",
    "...RrrrrrrRR...",
    "....RrrrrRR....",
    ".....RrrRR.....",
    "......RrR......",
    ".......R.......",
];

const LEAF: &[&str] = &[
    ".......K.......",
    "......KgK......",
    ".....KggGK.....",
    "....KgggGgK....",
    "...KggggGgGK...",
    "..KgggggGgGGK..",
    ".KggWgggGgGgGK.",
    "KgggWgggGgGGgGK",
    "KggggWggGgGgGGK",
    "KgWggggGGGgGGgK",
    "KggWgggGGgGgGGK",
    ".KggWggGGGgGGK.",
    "..KggggGGgGGK..",
    "...KKggGgGKK...",
    ".....KKRKK.....",
    ".......R.......",
    "......R........",
];

const ACORN: &[&str] = &[
    "......B......",
    ".....BB......",
    "...KKKKKKK...",
    "..KBKBKBKBK..",
    ".KBYBKBYBKBK.",
    "KBKBKBKBKBKBK",
    "KKBYBKBYBKBKK",
    ".KKKKKKKKKKK.",
    ".BYYYYYYYYYB.",
    "BYWYYYYYYYBYB",
    "BYWYYYYYYBYBB",
    "BYYYYYYYYYBYB",
    "BYYYYYYYBYBBB",
    ".BYYYYYYYBYB.",
    "..BYYYYYBYB..",
    "...BYYBYBB...",
    "....BBBBB....",
];

const BELL: &[&str] = &[
    ".......K.......",
    "......KYK......",
    "....RRRRRRR....",
    "..RRrWrRrrrRR..",
    ".RrWrrrRrrrrRR.",
    ".RrrrrrrrrrrRR.",
    "RRRRRRRRRRRRRRR",
    "YYYYYYYYYYYYYYY",
    "BYBYBYBYBYBYBYB",
    "YYYYYYYYYYYYYYY",
    "YYYKKKKKKKKKYYB",
    ".YYYYYYYYYYYYB.",
    "..YYYYYKYYYYB..",
    "...BYYYYYYYB...",
    ".....BBBBB.....",
];

pub fn symbol_map(suit: Suit) -> &'static [&'static str] {
    match suit {
        Suit::Acorns => ACORN,
        Suit::Leaves => LEAF,
        Suit::Bells => BELL,
        Suit::Hearts => HEART,
    }
}

/// Size of the suit symbol in pixels at scale 1.
pub fn symbol_size(suit: Suit) -> (i32, i32) {
    let map = symbol_map(suit);
    (map[0].len() as i32, map.len() as i32)
}

/// Draws a pixel map with its top-left corner at (x0, y0).
fn draw_map(canvas: &mut Canvas, map: &[&str], x0: i32, y0: i32, scale: i32) {
    for (row, line) in map.iter().enumerate() {
        for (col, ch) in line.chars().enumerate() {
            let Some(c) = palette_char(ch) else { continue };
            let (px, py) = (x0 + col as i32 * scale, y0 + row as i32 * scale);
            canvas.bar(px, py, px + scale - 1, py + scale - 1, Fill::solid(c));
        }
    }
}

/// Draws a suit symbol centred on (cx, cy), each map pixel `scale` x `scale`.
pub fn draw_symbol(canvas: &mut Canvas, suit: Suit, cx: i32, cy: i32, scale: i32) {
    let (w, h) = symbol_size(suit);
    draw_map(
        canvas,
        symbol_map(suit),
        cx - w * scale / 2,
        cy - h * scale / 2,
        scale,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn symbol_maps_are_rectangular_and_use_known_colours() {
        for suit in Suit::ALL {
            let map = symbol_map(suit);
            let width = map[0].len();
            for line in map {
                assert_eq!(line.len(), width, "{suit:?} row width");
                assert!(
                    line.chars().all(|c| c == '.' || palette_char(c).is_some()),
                    "{suit:?} unknown colour"
                );
            }
        }
    }

    #[test]
    fn draw_symbol_paints_inside_its_box() {
        let mut c = Canvas::new(40, 40);
        c.clear(color::WHITE);
        draw_symbol(&mut c, Suit::Hearts, 20, 20, 2);
        let (w, h) = symbol_size(Suit::Hearts);
        // Map pixel (2, 0) is red; at scale 2 it starts at (x0 + 4, y0).
        assert_eq!(c.pixel(20 - w + 4, 20 - h), Some(color::RED));
        assert_eq!(c.pixel(0, 0), Some(color::WHITE));
    }
}
