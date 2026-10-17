//! Renders all 32 cards and a few card backs into one PNG for review.

use openflek::art::cards::{
    SPRITE_H, SPRITE_W, TRANSPARENT, render_back_sprite, render_card_sprite,
};
use openflek::game::cards::Card;
use openflek::gfx::{Canvas, Fill, color, png};

fn main() {
    // Usage: card_sheet [out.png] [scale] [card ids...]
    let args: Vec<String> = std::env::args().skip(1).collect();
    let path = args
        .first()
        .cloned()
        .unwrap_or_else(|| "card_sheet.png".into());
    let scale: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(2);
    let ids: Vec<u8> = if args.len() > 2 {
        args[2..].iter().filter_map(|s| s.parse().ok()).collect()
    } else {
        (0..32).collect()
    };
    let all = args.len() <= 2;
    let cols = if all { 8 } else { ids.len() as i32 };
    let rows = if all { 5 } else { 1 };
    let gap = 4;
    let mut sheet = Canvas::new(cols * (SPRITE_W + gap) + gap, rows * (SPRITE_H + gap) + gap);
    sheet.bar(
        0,
        0,
        sheet.width() - 1,
        sheet.height() - 1,
        Fill::solid(color::GREEN),
    );
    let pos = |i: i32| {
        (
            gap + (i % cols) * (SPRITE_W + gap),
            gap + (i / cols) * (SPRITE_H + gap),
        )
    };
    for (i, &id) in ids.iter().enumerate() {
        let (x, y) = pos(i as i32);
        sheet.blit(
            &render_card_sprite(Card::from_id(id)),
            x,
            y,
            Some(TRANSPARENT),
        );
    }
    let backs = if all {
        vec![color::BLUE, color::RED, color::MAGENTA, color::BROWN]
    } else {
        vec![]
    };
    for (i, c) in backs.into_iter().enumerate() {
        let (x, y) = pos(32 + i as i32);
        sheet.blit(&render_back_sprite(c), x, y, Some(TRANSPARENT));
    }
    png::save(&sheet, scale, &path);
}
