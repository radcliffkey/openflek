//! The title screen with its circle of cards, and the closing credits.

use super::table::{back_color, draw_back, draw_face};
use super::ui::{MAX_X, MAX_Y, TextBox, button_rect, draw_button, restore, save};
use super::{Ctx, text};
use crate::art::cards::{CARD_H, CARD_W};
use crate::gfx::font::{draw_text_smooth, smooth_width};
use crate::gfx::{Fill, color};

fn circle_position(i: usize) -> (i32, i32) {
    let (cx, cy) = ((MAX_X - CARD_W) / 2, (MAX_Y - CARD_H) / 2 - 18);
    let (rx, ry) = ((cx - 10) as f64, (cy - 20) as f64);
    let a = i as f64 * std::f64::consts::PI / 15.0;
    (
        cx + (a.sin() * rx).round() as i32,
        cy - (a.cos() * ry).round() as i32,
    )
}

fn black(ctx: &mut Ctx) {
    ctx.scr
        .canvas
        .bar(0, 0, MAX_X, MAX_Y, Fill::solid(color::BLACK));
}

/// Draws card `i` of the circle (face or back); returns true if a key ended it.
async fn circle_card(ctx: &mut Ctx, i: usize, face_up: bool, interruptible: bool) -> bool {
    let (x, y) = circle_position(i);
    if face_up {
        let card = ctx.deck.cards()[(i - 1) % 32];
        draw_face(ctx, card, x, y);
    } else {
        let c = back_color(ctx);
        draw_back(ctx, x, y, c);
    }
    ctx.scr.pause(0.05).await;
    interruptible && ctx.scr.has_key()
}

pub async fn title_screen(ctx: &mut Ctx) {
    black(ctx);
    ctx.scr.flush_keys();
    let mut pass = 0;
    let mut tb: Option<TextBox> = None;
    'outer: loop {
        pass += 1;
        for i in 1..=30 {
            if circle_card(ctx, i, pass % 2 == 1, pass > 1).await {
                break 'outer;
            }
            if pass == 1 && i == 1 {
                let col = ctx.rng.below(15) as u8 + 1;
                tb = Some(TextBox::open(ctx, 0, MAX_Y / 2 - 16, text::TITLE_BY, col, 5, 22).await);
            }
            if pass == 1
                && i == 10
                && let Some(b) = &tb
            {
                b.line(
                    &mut ctx.scr.canvas,
                    0,
                    text::TITLE_PRESENTS,
                    super::ui::Justify::Center,
                );
            }
        }
        if pass == 1
            && let Some(b) = &tb
        {
            let (cx, cy) = (b.rect.cx(), b.rect.cy());
            let w = smooth_width(text::TITLE, 2);
            let c = &mut ctx.scr.canvas;
            draw_text_smooth(c, cx - w / 2 + 2, cy - 12 + 2, text::TITLE, color::BLACK, 2);
            draw_text_smooth(c, cx - w / 2, cy - 12, text::TITLE, color::YELLOW, 2);
            b.line(c, 5, text::VERSION, super::ui::Justify::Center);
        }
        ctx.deck.cut(10, &mut ctx.rng);
        ctx.scr.wait(10.0).await;
        if ctx.scr.has_key() {
            break;
        }
        let r = button_rect(999, 999, 2, 1, text::PRESS_ANYTHING);
        let saved = save(&ctx.scr.canvas, r);
        let col = ctx.rng.below(15) as u8 + 1;
        draw_button(&mut ctx.scr.canvas, r, text::PRESS_ANYTHING, col);
        ctx.scr.wait(3.0).await;
        restore(&mut ctx.scr.canvas, &saved);
        if ctx.scr.has_key() {
            break;
        }
    }
    if let Some(b) = tb {
        b.close(ctx);
    }
    ctx.scr.flush_keys();
}

/// The goodbye screen shown when quitting.
pub async fn credits(ctx: &mut Ctx) {
    black(ctx);
    ctx.scr.flush_keys();
    for i in 1..=30 {
        if circle_card(ctx, i, true, true).await {
            break;
        }
    }
    let table = ctx.cfg.table_color;
    let col = super::ui::random_color(ctx, 15, &[table]);
    let thanks = text::pick(&mut ctx.rng, text::CREDITS);
    let tb = TextBox::open(ctx, 0, MAX_Y / 2 - 16, thanks, col, 3, 52).await;
    tb.line(
        &mut ctx.scr.canvas,
        1,
        text::CREDITS_LINE,
        super::ui::Justify::Center,
    );
    tb.line(
        &mut ctx.scr.canvas,
        2,
        "Původní hra: J. Pivoňka, 1991-1992",
        super::ui::Justify::Center,
    );
    ctx.scr.wait_for_key(10.0).await;
}
