//! Number cards (7, 8, 9, 10): pips on a tree or in a grid, plus a small scene.

use super::paint::{Shade, blob, dot, line, thick_line};
use super::scenery::{self, Beast, GROUND};
use super::symbols::{draw_symbol, symbol_size};
use crate::game::cards::{Rank, Suit};
use crate::gfx::font::draw_text_centered;
use crate::gfx::{Canvas, color::*};

const L: i32 = 11;
const M: i32 = 30;
const R: i32 = 49;

/// Pip centres for a number card.
fn layout(suit: Suit, rank: Rank) -> Vec<(i32, i32)> {
    let tree = matches!(suit, Suit::Acorns | Suit::Leaves);
    let pairs = |ys: &[i32]| {
        ys.iter()
            .flat_map(|&y| [(L, y), (R, y)])
            .collect::<Vec<_>>()
    };
    let mut v = match (rank, tree) {
        (Rank::Seven, _) => pairs(&[28, 45, 62]),
        (Rank::Eight, _) => pairs(&[11, 28, 45, 62]),
        (Rank::Nine, true) => pairs(&[24, 39, 54, 69]),
        (Rank::Nine, false) => [11, 28, 45]
            .iter()
            .flat_map(|&y| [(L, y), (M, y), (R, y)])
            .collect(),
        (_, true) => pairs(&[18, 33, 48, 63, 78]),
        (_, false) => {
            let mut v: Vec<_> = [19, 35, 51, 67].iter().map(|&y| (M, y)).collect();
            v.extend([27, 45, 63].iter().flat_map(|&y| [(L, y), (R, y)]));
            v
        }
    };
    if rank == Rank::Seven || (rank == Rank::Nine && tree) {
        v.push((M, 10));
    }
    v
}

/// The central tree trunk with a twig to every pip.
fn tree(c: &mut Canvas, pips: &[(i32, i32)], suit: Suit) {
    let top = pips
        .iter()
        .filter(|p| p.0 == M)
        .map(|p| p.1)
        .min()
        .unwrap_or(10)
        + 4;
    for y in top..GROUND {
        let stripe = if (y / 3) % 2 == 0 { YELLOW } else { LIGHT_RED };
        c.line(M - 1, y, M + 1, y, stripe);
        c.put_pixel(M + 1, y, BROWN);
        c.put_pixel(M - 2, y, RED);
        c.put_pixel(M + 2, y, BROWN);
    }
    let (w, _) = symbol_size(suit);
    for &(x, y) in pips.iter().filter(|p| p.0 != M) {
        let dir = (x - M).signum();
        let end = x - dir * (w / 2 - 1);
        let start = (M as f32 + dir as f32 * 2.0, y as f32 + 6.0);
        thick_line(c, start, (end as f32, y as f32), 1.0, RED);
        line(c, start, (end as f32, y as f32), RED);
        let mid = ((start.0 + end as f32) / 2.0, (start.1 + y as f32) / 2.0);
        blob(
            c,
            mid.0,
            mid.1 - 2.0,
            2.0,
            1.0,
            Shade::Solid(LIGHT_GREEN),
            None,
        );
        dot(c, (mid.0, mid.1 - 2.0), GREEN);
    }
    // A sprouting crown.
    for dx in [-3.0, 0.0, 3.0] {
        line(
            c,
            (M as f32, top as f32),
            (M as f32 + dx, top as f32 - 4.0),
            GREEN,
        );
    }
}

/// A tiny floret between pips on bell and heart cards.
fn floret(c: &mut Canvas, x: i32, y: i32, petal: u8) {
    for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
        c.put_pixel(x + dx, y + dy, petal);
    }
    c.put_pixel(x, y, YELLOW);
    c.line(x - 3, y + 2, x - 2, y + 2, GREEN);
    c.line(x + 2, y + 2, x + 3, y + 2, GREEN);
}

fn scene(c: &mut Canvas, suit: Suit, rank: Rank) {
    let y = GROUND;
    match (suit, rank) {
        (Suit::Acorns, Rank::Seven) => {
            scenery::cottage(c, 38, y);
            scenery::tiny_person(c, 16, y, GREEN, LIGHT_RED, CYAN);
            line(c, (20.0, (y - 12) as f32), (24.0, (y - 17) as f32), BROWN);
        }
        (Suit::Acorns, Rank::Eight) => {
            scenery::tiny_person(c, 14, y, RED, GREEN, YELLOW);
            scenery::beast(c, Beast::Dog, 44, y);
        }
        (Suit::Acorns, Rank::Nine) => scenery::beast(c, Beast::Boar, 17, y),
        (Suit::Leaves, Rank::Seven) => {
            scenery::tiny_person(c, 44, y, YELLOW, LIGHT_CYAN, LIGHT_RED);
            scenery::flower(c, 14, y, 8, LIGHT_RED);
            scenery::flower(c, 19, y, 6, YELLOW);
        }
        (Suit::Leaves, Rank::Eight) => scenery::beast(c, Beast::Deer, 42, y),
        (Suit::Leaves, Rank::Nine) => scenery::bird(c, 19, y - 6, LIGHT_BLUE),
        (Suit::Bells, Rank::Seven) => scenery::flower_pot(c, M, y),
        (Suit::Bells, Rank::Eight) => scenery::beast(c, Beast::Dog, M, y),
        (Suit::Bells, Rank::Nine) => {
            scenery::beast(c, Beast::Horse, 28, y);
            scenery::fir(c, 52, y, 16);
        }
        (Suit::Bells, Rank::Ten) => {
            scenery::bird(c, 18, y - 4, LIGHT_RED);
            scenery::bird(c, 43, y - 4, YELLOW);
        }
        (Suit::Hearts, Rank::Seven) => scenery::tub(c, M, y),
        (Suit::Hearts, Rank::Eight) => scenery::fountain(c, M, y),
        (Suit::Hearts, Rank::Nine) => {
            scenery::cottage(c, 8, y);
            scenery::fir(c, 40, y, 22);
            scenery::fir(c, 51, y, 16);
        }
        (Suit::Hearts, Rank::Ten) => {
            scenery::beast(c, Beast::Sheep, 18, y);
            scenery::beast(c, Beast::Sheep, 42, y);
        }
        _ => {}
    }
}

pub fn draw_number(c: &mut Canvas, suit: Suit, rank: Rank) {
    let pips = layout(suit, rank);
    scenery::meadow(c, suit.index() * 4 + rank.index());
    let tree_suit = matches!(suit, Suit::Acorns | Suit::Leaves);
    if tree_suit {
        tree(c, &pips, suit);
    } else {
        let petal = if suit == Suit::Hearts {
            LIGHT_RED
        } else {
            LIGHT_MAGENTA
        };
        let mut ys: Vec<i32> = pips.iter().map(|p| p.1).collect();
        ys.sort();
        ys.dedup();
        for w in ys.windows(2) {
            if w[1] - w[0] >= 14 {
                let fy = (w[0] + w[1]) / 2;
                if !pips.iter().any(|p| p.0 == M && (p.1 - fy).abs() < 8) {
                    floret(c, M, fy, petal);
                }
            }
        }
    }
    scene(c, suit, rank);
    for &(x, y) in &pips {
        draw_symbol(c, suit, x, y, 1);
    }
    if rank == Rank::Ten {
        draw_text_centered(c, M + 1, 2, "X", BLUE);
        draw_text_centered(c, M, 2, "X", LIGHT_BLUE);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pip_count_matches_rank() {
        for suit in Suit::ALL {
            for (rank, n) in [
                (Rank::Seven, 7),
                (Rank::Eight, 8),
                (Rank::Nine, 9),
                (Rank::Ten, 10),
            ] {
                assert_eq!(layout(suit, rank).len(), n, "{suit:?} {rank:?}");
            }
        }
    }
}
