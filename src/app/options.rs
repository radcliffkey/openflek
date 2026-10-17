//! The options dialog (F10) and the IQ slider.

use super::screen::Key;
use super::ui::{
    self, MAX_X, MAX_Y, Rect, TextBox, draw_button, restore, save, text_centered, text_left,
};
use super::{Ctx, text};
use crate::config::PATTERN_COUNT;
use crate::gfx::{Fill, color};
use crate::sound::Tone;

const ROW_H: i32 = 24;

fn row_rect(i: usize) -> Rect {
    let cy = 28 + i as i32 * ROW_H;
    Rect {
        x1: 16,
        y1: cy - 12,
        x2: 120,
        y2: cy + 11,
    }
}

fn draw_preview(ctx: &mut Ctx) {
    let r = Rect {
        x1: 121,
        y1: 40,
        x2: MAX_X / 2,
        y2: 136,
    };
    let fill = super::table::table_fill(ctx);
    ctx.scr.canvas.bar(r.x1, r.y1, r.x2, r.y2, fill);
    let label = ui::button_rect(MAX_X / 2 - 50, 100, 2, 0, "Menu");
    let mc = ctx.cfg.menu_color;
    draw_button(&mut ctx.scr.canvas, label, "Menu", mc);
    let c = &mut ctx.scr.canvas;
    c.bar(124, 144, MAX_X / 2, 186, Fill::solid(color::DARK_GRAY));
    let sound = format!(
        "{}: {}",
        text::OPTIONS[0],
        if ctx.cfg.sound { "ano" } else { "ne" }
    );
    text_left(c, 132, 152, &sound, color::WHITE);
    text_left(c, 132, 170, &format!("IQ: {}", ctx.cfg.iq), color::WHITE);
}

/// Settings: sound, table colour and pattern, menu colour, IQ, save.
pub async fn options_dialog(ctx: &mut Ctx) {
    let panel = Rect {
        x1: 8,
        y1: 8,
        x2: MAX_X / 2 + 8,
        y2: 192,
    };
    let saved = save(&ctx.scr.canvas, panel);
    ui::frame_window(&mut ctx.scr.canvas, panel, Fill::solid(color::DARK_GRAY));
    for (i, item) in text::OPTIONS.iter().enumerate() {
        draw_button(&mut ctx.scr.canvas, row_rect(i), item, color::BROWN);
    }
    draw_preview(ctx);
    let mut cur = 0;
    draw_button(
        &mut ctx.scr.canvas,
        row_rect(cur),
        text::OPTIONS[cur],
        color::YELLOW,
    );
    ctx.scr.flush_keys();
    loop {
        ctx.scr.frame().await;
        let mut sel = cur;
        let mut act = false;
        if let Some((mx, my)) = ctx.scr.take_mouse()
            && let Some(i) = (0..text::OPTIONS.len()).find(|&i| row_rect(i).contains(mx, my))
        {
            sel = i;
        }
        match ctx.scr.take_key() {
            Some(Key::Up | Key::Left) => {
                sel = (cur + text::OPTIONS.len() - 1) % text::OPTIONS.len()
            }
            Some(Key::Down | Key::Right) => sel = (cur + 1) % text::OPTIONS.len(),
            Some(Key::Enter) => act = true,
            Some(Key::Esc) => break,
            Some(Key::Click(x, y)) => {
                if let Some(i) = (0..text::OPTIONS.len()).find(|&i| row_rect(i).contains(x, y)) {
                    sel = i;
                    act = true;
                } else if !panel.contains(x, y) {
                    break;
                }
            }
            Some(Key::Char(ch)) => {
                let up = ch.to_ascii_uppercase();
                if let Some(i) = text::OPTIONS.iter().position(|o| o.starts_with(up)) {
                    sel = i;
                    act = true;
                }
            }
            _ => {}
        }
        if sel != cur {
            ctx.scr.play(&ui::click()).await;
            draw_button(
                &mut ctx.scr.canvas,
                row_rect(cur),
                text::OPTIONS[cur],
                color::BROWN,
            );
            cur = sel;
            draw_button(
                &mut ctx.scr.canvas,
                row_rect(cur),
                text::OPTIONS[cur],
                color::YELLOW,
            );
        }
        if !act {
            continue;
        }
        match cur {
            0 => {
                ctx.cfg.sound = !ctx.cfg.sound;
                ctx.scr.sound_on = ctx.cfg.sound;
            }
            1 => ctx.cfg.table_color = (ctx.cfg.table_color + 1) % 9,
            2 => ctx.cfg.table_pattern = ctx.cfg.table_pattern % PATTERN_COUNT + 1,
            3 => ctx.cfg.menu_color = (ctx.cfg.menu_color + 1) % 9,
            4 => ctx.cfg.standard_colors(),
            5 => {
                iq_slider(ctx).await;
            }
            _ => {
                ctx.cfg.save();
                break;
            }
        }
        draw_preview(ctx);
    }
    restore(&mut ctx.scr.canvas, &saved);
}

/// Lets the user set the computer players' IQ (0..=255) on a slider.
pub async fn iq_slider(ctx: &mut Ctx) {
    let scale = text::IQ_SCALE;
    let width = scale.chars().count() as i32 + 2;
    let tb = TextBox::open(
        ctx,
        0,
        (MAX_Y / 17) * 8,
        text::IQ_TITLE,
        color::BROWN,
        6,
        width.max(32),
    )
    .await;
    tb.line(&mut ctx.scr.canvas, 5, scale, ui::Justify::Center);
    let row = |n: i32| tb.rect.y1 + 12 * (n + 3);
    let groove_y = (row(1) + row(2)) / 2;
    let groove = Rect {
        x1: tb.rect.x1 + 15,
        y1: groove_y - 4,
        x2: tb.rect.x2 - 15,
        y2: groove_y + 3,
    };
    let (lo, hi) = (groove.x1 + 13, groove.x2 - 13);
    let start_iq = if ctx.cfg.iq == 0 {
        126
    } else {
        ctx.cfg.iq as i32
    };
    let mut pos = lo + (hi - lo) * start_iq / 256;
    let area = Rect {
        x1: groove.x1 - 2,
        y1: row(0) - 4,
        x2: groove.x2 + 2,
        y2: row(4) + 6,
    };
    let bg = save(&ctx.scr.canvas, area);
    ctx.scr.flush_keys();
    let mut redraw = true;
    loop {
        if redraw {
            redraw = false;
            restore(&mut ctx.scr.canvas, &bg);
            let c = &mut ctx.scr.canvas;
            c.rect(groove.x1, groove.y1, groove.x2, groove.y2, color::DARK_GRAY);
            let knob = Rect {
                x1: pos - 8,
                y1: groove_y - 16,
                x2: pos + 8,
                y2: groove_y + 15,
            };
            ui::frame_window(c, knob, Fill::solid(color::YELLOW));
            let value = (pos - lo) * 255 / (hi - lo);
            text_centered(
                c,
                tb.rect.cx(),
                row(4),
                &format!("IQ {value:3}"),
                color::WHITE,
            );
        }
        ctx.scr.frame().await;
        let old = pos;
        if let Some((mx, _)) = ctx.scr.take_mouse()
            && ctx.scr.mouse_down()
        {
            pos = mx;
        }
        match ctx.scr.take_key() {
            Some(Key::Home) => pos = lo,
            Some(Key::End) => pos = hi,
            Some(Key::Left) => pos -= 3,
            Some(Key::Right) => pos += 3,
            Some(Key::Down | Key::PageDown) => pos -= 20,
            Some(Key::Up | Key::PageUp) => pos += 20,
            Some(Key::Click(x, y)) if area.contains(x, y) => pos = x,
            Some(Key::Enter) => break,
            _ => {}
        }
        pos = pos.clamp(lo, hi);
        if pos != old {
            redraw = true;
            ctx.scr
                .play(&[Tone {
                    hz: 200 + (pos - lo) as u32 * 4,
                    ms: 20,
                }])
                .await;
        }
    }
    ctx.cfg.iq = (((pos - lo) * 255 / (hi - lo)).max(1)) as u8;
    ctx.brain.iq = ctx.cfg.iq;
    tb.close(ctx);
}
