//! 8x8 bitmap font with Czech letters.
//!
//! Base glyphs come from the `font8x8` crate (public-domain derived, MIT).
//! Czech letters missing there (č ď ě ň ř š ť ů ž and their capitals) are
//! composed here: lowercase letters get the accent in the two empty top rows,
//! capitals are squashed to five rows first, the same way `font8x8` draws É.

use super::canvas::Canvas;
use font8x8::{BASIC_FONTS, LATIN_FONTS, UnicodeFonts};

pub const GLYPH_SIZE: i32 = 8;

/// One glyph: eight rows, bit 0 of each row is the leftmost pixel.
pub type Glyph = [u8; 8];

enum Accent {
    Caron,
    Ring,
    Apostrophe,
}

pub fn glyph(ch: char) -> Glyph {
    if let Some(g) = BASIC_FONTS.get(ch).or_else(|| LATIN_FONTS.get(ch)) {
        return g;
    }
    let (base, accent) = match ch {
        'č' => ('c', Accent::Caron),
        'ě' => ('e', Accent::Caron),
        'ň' => ('n', Accent::Caron),
        'ř' => ('r', Accent::Caron),
        'š' => ('s', Accent::Caron),
        'ž' => ('z', Accent::Caron),
        'ů' => ('u', Accent::Ring),
        'ď' => ('d', Accent::Apostrophe),
        'ť' => ('t', Accent::Apostrophe),
        'Č' => ('C', Accent::Caron),
        'Ď' => ('D', Accent::Caron),
        'Ě' => ('E', Accent::Caron),
        'Ň' => ('N', Accent::Caron),
        'Ř' => ('R', Accent::Caron),
        'Š' => ('S', Accent::Caron),
        'Ť' => ('T', Accent::Caron),
        'Ž' => ('Z', Accent::Caron),
        'Ů' => ('U', Accent::Ring),
        _ => return BASIC_FONTS.get('?').unwrap_or([0; 8]),
    };
    compose(base, accent)
}

fn compose(base: char, accent: Accent) -> Glyph {
    let mut g = BASIC_FONTS.get(base).unwrap_or([0; 8]);
    if base.is_ascii_uppercase() {
        g = squash_capital(base, g);
    }
    let used = g.iter().fold(0u8, |acc, row| acc | row);
    let (lo, hi) = (
        used.trailing_zeros() as i32,
        7 - used.leading_zeros() as i32,
    );
    let center = (lo + hi) / 2;
    let bit = |col: i32| if (0..8).contains(&col) { 1u8 << col } else { 0 };
    match accent {
        Accent::Caron => {
            g[0] |= bit(center - 2) | bit(center + 2);
            g[1] |= bit(center - 1) | bit(center) | bit(center + 1);
        }
        Accent::Ring => {
            g[0] |= bit(center) | bit(center + 1);
            g[1] |= bit(center) | bit(center + 1);
        }
        Accent::Apostrophe => {
            let col = (hi + 2).min(7);
            g[0] |= bit(col);
            g[1] |= bit(col);
        }
    }
    g
}

/// Moves a capital into rows 2..=6 by dropping two of its seven rows.
fn squash_capital(base: char, g: Glyph) -> Glyph {
    let rows: [usize; 5] = if base == 'S' {
        [0, 2, 3, 4, 6]
    } else {
        [0, 1, 3, 5, 6]
    };
    let mut out = [0u8; 8];
    for (i, &r) in rows.iter().enumerate() {
        out[2 + i] = g[r];
    }
    out
}

/// Width in pixels of `text` in the 8x8 font.
pub fn text_width(text: &str) -> i32 {
    text.chars().count() as i32 * GLYPH_SIZE
}

/// Draws `text` with its top-left corner at (x, y); only set bits are painted.
pub fn draw_text(canvas: &mut Canvas, x: i32, y: i32, text: &str, color: u8) {
    for (i, ch) in text.chars().enumerate() {
        let cx = x + i as i32 * GLYPH_SIZE;
        for (row, bits) in glyph(ch).iter().enumerate() {
            for col in 0..8 {
                if bits >> col & 1 == 1 {
                    canvas.put_pixel(cx + col, y + row as i32, color);
                }
            }
        }
    }
}

/// Text with a one-pixel drop shadow down and right; `levels` > 0 draws the
/// large smooth letters of [`draw_text_smooth`].
pub fn draw_text_shadowed(
    canvas: &mut Canvas,
    x: i32,
    y: i32,
    text: &str,
    color: u8,
    shadow: u8,
    levels: u32,
) {
    for (d, col) in [(1, shadow), (0, color)] {
        draw_text_smooth(canvas, x + d, y + d, text, col, levels);
    }
}

/// One Scale2x (EPX) step: doubles a bitmap while smoothing diagonals.
fn scale2x(src: &[Vec<bool>]) -> Vec<Vec<bool>> {
    let (h, w) = (src.len(), src.first().map_or(0, |r| r.len()));
    let at = |x: isize, y: isize| -> bool {
        if x < 0 || y < 0 || x >= w as isize || y >= h as isize {
            false
        } else {
            src[y as usize][x as usize]
        }
    };
    let mut out = vec![vec![false; w * 2]; h * 2];
    for y in 0..h as isize {
        for x in 0..w as isize {
            let (p, a, b, c, d) = (
                at(x, y),
                at(x, y - 1),
                at(x + 1, y),
                at(x - 1, y),
                at(x, y + 1),
            );
            let (ox, oy) = (x as usize * 2, y as usize * 2);
            out[oy][ox] = if c == a && c != d && a != b { a } else { p };
            out[oy][ox + 1] = if a == b && a != c && b != d { b } else { p };
            out[oy + 1][ox] = if d == c && d != b && c != a { c } else { p };
            out[oy + 1][ox + 1] = if b == d && b != a && d != c { d } else { p };
        }
    }
    out
}

/// Width of `text` drawn with [`draw_text_smooth`] at `levels` doublings.
pub fn smooth_width(text: &str, levels: u32) -> i32 {
    text_width(text) << levels
}

/// Draws large text: each glyph is doubled `levels` times with Scale2x,
/// giving rounded letters for titles and shouts (0 levels: plain 8x8).
pub fn draw_text_smooth(canvas: &mut Canvas, x: i32, y: i32, text: &str, color: u8, levels: u32) {
    let mut cx = x;
    for ch in text.chars() {
        let g = glyph(ch);
        let mut bmp: Vec<Vec<bool>> = g
            .iter()
            .map(|row| (0..8).map(|col| row >> col & 1 == 1).collect())
            .collect();
        for _ in 0..levels {
            bmp = scale2x(&bmp);
        }
        for (row, bits) in bmp.iter().enumerate() {
            for (col, &on) in bits.iter().enumerate() {
                if on {
                    canvas.put_pixel(cx + col as i32, y + row as i32, color);
                }
            }
        }
        cx += GLYPH_SIZE << levels;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const CZECH: &str = "áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ";

    #[test]
    fn every_czech_letter_has_a_distinct_glyph() {
        let question = glyph('?');
        for ch in CZECH.chars() {
            let g = glyph(ch);
            assert_ne!(g, question, "{ch} fell back to '?'");
            let base: char = match ch {
                'č' => 'c',
                'Ž' => 'Z',
                _ => continue,
            };
            assert_ne!(g, glyph(base));
        }
    }

    #[test]
    fn accents_stay_above_the_letter_body() {
        for ch in "čěňřšžČĎĚŇŘŠŤŽ".chars() {
            let g = glyph(ch);
            assert_ne!(g[0], 0, "{ch} has no accent row");
            assert_eq!(g[7], 0, "{ch} spills into the last row");
        }
    }

    #[test]
    fn scale2x_keeps_solid_blocks_and_doubles_size() {
        let src = vec![vec![true; 3]; 3];
        let out = scale2x(&src);
        assert_eq!((out.len(), out[0].len()), (6, 6));
        // Interior stays solid, outer corners get rounded off.
        assert!((1..5).all(|y| (1..5).all(|x| out[y][x])));
        assert!(!out[0][0] && !out[5][5]);
        let mut c = Canvas::new(64, 64);
        draw_text_smooth(&mut c, 0, 0, "A", 1, 2);
        assert!(c.pixels().contains(&1));
        assert_eq!(smooth_width("AB", 2), 64);
    }

    #[test]
    fn draw_text_paints_glyph_bits_and_shadow() {
        let mut c = Canvas::new(16, 16);
        draw_text(&mut c, 0, 0, "I", 1);
        let lit = c.pixels().iter().filter(|&&p| p == 1).count() as u32;
        let bits: u32 = glyph('I').iter().map(|r| r.count_ones()).sum();
        assert_eq!(lit, bits);
        assert_eq!(text_width("ab"), 16);
        let mut d = Canvas::new(16, 16);
        draw_text_shadowed(&mut d, 0, 0, "I", 1, 2, 0);
        assert!(d.pixels().contains(&2) && d.pixels().contains(&1));
    }
}
