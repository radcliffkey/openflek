//! The window toolkit: bevelled frames, buttons, text boxes, button menus,
//! yes/no questions, speech bubbles and the "press any key" prompt.

use super::Ctx;
use super::screen::Key;
use super::text;
use crate::game::rng::Rng;
use crate::gfx::font::{draw_text_shadowed, draw_text_smooth, smooth_width, text_width};
use crate::gfx::{Canvas, Fill, color};
use crate::sound::Tone;

pub const MAX_X: i32 = super::screen::WIDTH - 1;
pub const MAX_Y: i32 = super::screen::HEIGHT - 1;
/// The whole screen.
pub const SCREEN: Rect = Rect {
    x1: 0,
    y1: 0,
    x2: MAX_X,
    y2: MAX_Y,
};
/// Character cell of the 8x8 font.
const TW: i32 = 8;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Rect {
    pub x1: i32,
    pub y1: i32,
    pub x2: i32,
    pub y2: i32,
}

impl Rect {
    pub fn centered(cx: i32, cy: i32, hw: i32, hh: i32) -> Rect {
        Rect {
            x1: cx - hw,
            y1: cy - hh,
            x2: cx + hw,
            y2: cy + hh,
        }
    }

    pub fn cx(&self) -> i32 {
        (self.x1 + self.x2) / 2
    }

    pub fn cy(&self) -> i32 {
        (self.y1 + self.y2) / 2
    }

    pub fn contains(&self, x: i32, y: i32) -> bool {
        x >= self.x1 && x <= self.x2 && y >= self.y1 && y <= self.y2
    }
}

/// A saved screen area, restored when a window closes.
pub struct Saved {
    x: i32,
    y: i32,
    img: Canvas,
}

pub fn save(c: &Canvas, r: Rect) -> Saved {
    Saved {
        x: r.x1,
        y: r.y1,
        img: c.crop(r.x1, r.y1, r.x2 - r.x1 + 1, r.y2 - r.y1 + 1),
    }
}

pub fn restore(c: &mut Canvas, s: &Saved) {
    c.blit(&s.img, s.x, s.y, None);
}

/// Places a centre so the box stays 16 px inside the screen; 0 means centred.
fn clamp_center(c: i32, half: i32, max: i32) -> i32 {
    let mut c = if c <= 0 { max / 2 } else { c };
    if c - half <= 0 {
        c = half + 16;
    }
    if c + half >= max {
        c = max - half - 16;
    }
    c
}

/// Readable text colour on a background colour.
pub fn text_color_for(bg: u8) -> u8 {
    match bg {
        0..=8 | 13 => color::WHITE,
        9 | 12 => color::YELLOW,
        _ => color::DARK_GRAY,
    }
}

fn shadowed(c: &mut Canvas, x: i32, y: i32, s: &str, col: u8, big: bool) {
    let levels = big as u32;
    if col > 8 {
        draw_text_shadowed(c, x, y, s, col, color::BLACK, levels);
    } else {
        draw_text_smooth(c, x, y, s, col, levels);
    }
}

/// Text centred on (cx, cy); bright colours get a drop shadow.
pub fn text_centered(c: &mut Canvas, cx: i32, cy: i32, s: &str, col: u8) {
    shadowed(c, cx - text_width(s) / 2, cy - 4, s, col, false);
}

/// Large text centred on (cx, cy).
pub fn big_text_centered(c: &mut Canvas, cx: i32, cy: i32, s: &str, col: u8) {
    shadowed(c, cx - smooth_width(s, 1) / 2, cy - 8, s, col, true);
}

/// Text starting at x, vertically centred on cy.
pub fn text_left(c: &mut Canvas, x: i32, cy: i32, s: &str, col: u8) {
    shadowed(c, x, cy - 4, s, col, false);
}

/// The three-pixel raised bevel shared by every window and button.
pub fn bevel(c: &mut Canvas, r: Rect) {
    let Rect { x1, y1, x2, y2 } = r;
    let w = color::WHITE;
    c.line(x1 + 2, y1 + 1, x2 - 2, y1 + 1, w);
    c.line(x1 + 3, y1 + 2, x2 - 3, y1 + 2, w);
    c.line(x1 + 1, y1 + 2, x1 + 1, y2 - 2, w);
    c.line(x1 + 2, y1 + 3, x1 + 2, y2 - 3, w);
    c.line(x1 + 3, y1 + 4, x1 + 3, y2 - 4, w);
    let d = color::DARK_GRAY;
    c.rect(x1, y1, x2, y2, d);
    c.line(x1 + 2, y2 - 1, x2 - 2, y2 - 1, d);
    c.line(x1 + 3, y2 - 2, x2 - 3, y2 - 2, d);
    c.line(x2 - 1, y1 + 2, x2 - 1, y2 - 2, d);
    c.line(x2 - 2, y1 + 3, x2 - 2, y2 - 3, d);
    let l = color::LIGHT_GRAY;
    c.line(x1 + 1, y1 + 1, x1 + 3, y1 + 3, l);
    c.line(x2 - 1, y2 - 1, x2 - 3, y2 - 3, l);
    c.rect(x1 + 3, y1 + 3, x2 - 3, y2 - 3, l);
}

/// Fills and bevels a window instantly.
pub fn frame_window(c: &mut Canvas, r: Rect, fill: Fill) {
    c.bar(r.x1 + 4, r.y1 + 4, r.x2 - 4, r.y2 - 4, fill);
    bevel(c, r);
}

/// Opens a window with the "exploding" fill animation.
pub async fn open_window(ctx: &mut Ctx, r: Rect, col: u8) {
    let (cx, cy) = (r.cx(), r.cy());
    let (hw, hh) = ((r.x2 - r.x1 - 8) / 2, (r.y2 - r.y1 - 8) / 2);
    for k in [4, 8, 12] {
        ctx.scr.canvas.bar(
            cx - k * hw / 16,
            cy - k * hh / 16,
            cx + k * hw / 16,
            cy + k * hh / 16,
            Fill::solid(col),
        );
        ctx.scr.frame().await;
    }
    frame_window(&mut ctx.scr.canvas, r, Fill::solid(col));
}

// ------------------------------------------------------------------ sounds

pub fn click() -> Vec<Tone> {
    vec![Tone { hz: 100, ms: 30 }]
}

pub fn buzz() -> Vec<Tone> {
    (20..=80).rev().map(|hz| Tone { hz, ms: 25 }).collect()
}

/// Number of prepared variants of each random tune; a small fixed set lets
/// the sounds be cached.
const TUNE_VARIANTS: u32 = 8;

/// Four random notes and a held C: the jingle of a confirmed menu choice.
pub fn confirm_tune(ctx: &mut Ctx) -> Vec<Tone> {
    const NOTES: [u32; 5] = [587, 659, 698, 784, 880];
    let mut r = Rng::new(ctx.rng.below(TUNE_VARIANTS));
    let mut t: Vec<Tone> = (0..4)
        .map(|_| Tone {
            hz: NOTES[r.below(5) as usize],
            ms: 125,
        })
        .collect();
    t.push(Tone { hz: 523, ms: 150 });
    t
}

/// Thirty random chirps while a speech bubble puffs up.
pub fn puff_tune(ctx: &mut Ctx) -> Vec<Tone> {
    let mut r = Rng::new(ctx.rng.below(TUNE_VARIANTS) + 100);
    (0..30)
        .map(|_| Tone {
            hz: 440 + r.below(880),
            ms: 8,
        })
        .collect()
}

pub fn card_thud() -> Vec<Tone> {
    (20..=40).map(|hz| Tone { hz, ms: 5 }).collect()
}

// ----------------------------------------------------------------- widgets

/// Half width and height of a one-line button with the given padding (in characters).
fn button_half_size(pad_x: i32, pad_y: i32, s: &str) -> (i32, i32) {
    (
        (TW * (pad_x + 2) + text_width(s)) / 2,
        (TW * (pad_y + 2) + TW) / 2,
    )
}

/// A one-line label or button centred on (cx, cy).
pub fn button_rect(cx: i32, cy: i32, pad_x: i32, pad_y: i32, s: &str) -> Rect {
    let (hw, hh) = button_half_size(pad_x, pad_y, s);
    Rect::centered(
        clamp_center(cx, hw, MAX_X),
        clamp_center(cy, hh, MAX_Y),
        hw,
        hh,
    )
}

pub fn draw_button(c: &mut Canvas, r: Rect, s: &str, col: u8) {
    frame_window(c, r, Fill::solid(col));
    text_centered(c, r.cx(), r.cy() + 1, s, text_color_for(col));
}

/// A text box: `lines` text lines below a title, `width` characters wide.
pub struct TextBox {
    pub rect: Rect,
    pub color: u8,
    saved: Saved,
}

impl TextBox {
    pub async fn open(
        ctx: &mut Ctx,
        cx: i32,
        cy: i32,
        title: &str,
        col: u8,
        lines: i32,
        width: i32,
    ) -> TextBox {
        let (hw, hh) = (TW * (width + 4) / 2, (TW + 4) * (lines + 5) / 2);
        let rect = Rect::centered(
            clamp_center(cx, hw, MAX_X),
            clamp_center(cy, hh, MAX_Y),
            hw,
            hh,
        );
        let saved = save(&ctx.scr.canvas, rect);
        open_window(ctx, rect, col).await;
        let tb = TextBox {
            rect,
            color: col,
            saved,
        };
        tb.line(&mut ctx.scr.canvas, -1, title, Justify::Center);
        tb
    }

    /// Writes line `n` (−1 is the title row).
    pub fn line(&self, c: &mut Canvas, n: i32, s: &str, just: Justify) {
        let y = self.rect.y1 + (TW + 4) * (n + 3);
        let col = text_color_for(self.color);
        match just {
            Justify::Left => text_left(c, self.rect.x1 + 16, y, s, col),
            Justify::Center => text_centered(c, self.rect.cx(), y, s, col),
            Justify::Right => text_left(c, self.rect.x2 - 16 - text_width(s), y, s, col),
        }
    }

    pub fn close(self, ctx: &mut Ctx) {
        restore(&mut ctx.scr.canvas, &self.saved);
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Justify {
    Left,
    Center,
    Right,
}

/// Blinks the focus frame of a highlighted button for one frame.
fn blink(c: &mut Canvas, r: Rect, t: f64) {
    let phase = (t / 0.8) as i64 % 2 == 0;
    let (outer, inner) = if phase {
        (color::LIGHT_GRAY, color::YELLOW)
    } else {
        (color::LIGHT_RED, color::LIGHT_RED)
    };
    c.rect(r.x1 + 3, r.y1 + 3, r.x2 - 3, r.y2 - 3, outer);
    c.rect(r.x1 + 4, r.y1 + 4, r.x2 - 4, r.y2 - 4, inner);
}

/// Uppercase ASCII hotkey of a caption: its first character.
fn hotkey(caption: &str) -> char {
    caption.chars().next().unwrap_or(' ').to_ascii_uppercase()
}

/// What a menu does with keys outside its own items.
#[derive(Clone, Copy, PartialEq, Eq)]
enum MenuMode {
    /// Esc asks to quit, F10 opens the options, other keys are complained about.
    Strict,
    /// Used inside the quit prompt itself: stray keys are ignored.
    Lenient,
}

/// A question box with a row of up to four buttons.
pub struct Menu<'a> {
    /// Centre of the box; 0 centres it, 1 / 999 push it to the top-left / bottom-right.
    pub cx: i32,
    pub cy: i32,
    pub title: &'a str,
    /// Box width in characters.
    pub width: i32,
    pub items: &'a [&'a str],
    /// Button width in characters.
    pub item_width: i32,
    pub default: usize,
}

impl Menu<'_> {
    /// Shows the menu in the menu colour and returns the chosen index.
    pub async fn run(&self, ctx: &mut Ctx) -> usize {
        let col = ctx.cfg.menu_color;
        run_menu(ctx, self, col, MenuMode::Strict).await
    }
}

async fn run_menu(ctx: &mut Ctx, m: &Menu<'_>, col: u8, mode: MenuMode) -> usize {
    let tb = TextBox::open(ctx, m.cx, m.cy, m.title, col, 2, m.width).await;
    let items = m.items;
    let n = items.len() as i32;
    let rects: Vec<Rect> = (0..n)
        .map(|i| {
            let x = tb.rect.cx() + TW * (2 * m.item_width + 7) * (2 * (i + 1) - n - 1) / 4;
            let pad = m.item_width - items[i as usize].chars().count() as i32;
            let (hw, hh) = button_half_size(pad, 0, items[i as usize]);
            Rect::centered(x, tb.rect.y2 - TW * 7 / 2, hw, hh)
        })
        .collect();
    for (i, r) in rects.iter().enumerate() {
        draw_button(&mut ctx.scr.canvas, *r, items[i], color::BROWN);
    }
    let mut cur = m.default.min(items.len() - 1);
    draw_button(&mut ctx.scr.canvas, rects[cur], items[cur], color::YELLOW);
    ctx.scr.flush_keys();
    let start = ctx.scr.now();
    loop {
        let t = ctx.scr.now() - start;
        blink(&mut ctx.scr.canvas, rects[cur], t);
        ctx.scr.frame().await;
        let mut sel = cur;
        let mut chosen = false;
        if let Some((mx, my)) = ctx.scr.take_mouse()
            && let Some(i) = rects.iter().position(|r| r.contains(mx, my))
        {
            sel = i;
        }
        if let Some(key) = ctx.scr.take_key() {
            match key {
                Key::Left | Key::Up => sel = if sel == 0 { items.len() - 1 } else { sel - 1 },
                Key::Right | Key::Down => sel = (sel + 1) % items.len(),
                Key::Enter => chosen = true,
                Key::Click(x, y) => {
                    if let Some(i) = rects.iter().position(|r| r.contains(x, y)) {
                        sel = i;
                        chosen = true;
                    }
                }
                Key::Char(ch) => {
                    let up = ch.to_ascii_uppercase();
                    if let Some(i) = items.iter().rposition(|it| hotkey(it) == up) {
                        sel = i;
                        chosen = true;
                    } else if mode == MenuMode::Strict {
                        not_understood(ctx, tb.rect.x1, tb.rect.y1).await;
                    }
                }
                Key::Esc if mode == MenuMode::Strict => Box::pin(quit_prompt(ctx)).await,
                Key::F10 if mode == MenuMode::Strict => {
                    Box::pin(super::options::options_dialog(ctx)).await
                }
                Key::F1 => {}
                _ if mode == MenuMode::Strict => not_understood(ctx, tb.rect.x1, tb.rect.y1).await,
                _ => {}
            }
        }
        if sel != cur {
            ctx.scr.play(&click()).await;
            draw_button(&mut ctx.scr.canvas, rects[cur], items[cur], color::BROWN);
            cur = sel;
            draw_button(&mut ctx.scr.canvas, rects[cur], items[cur], color::YELLOW);
        }
        if chosen {
            break;
        }
    }
    let tune = confirm_tune(ctx);
    ctx.scr.play(&tune).await;
    draw_button(
        &mut ctx.scr.canvas,
        rects[cur],
        items[cur],
        color::LIGHT_RED,
    );
    ctx.scr.pause(0.25).await;
    draw_button(&mut ctx.scr.canvas, rects[cur], items[cur], color::YELLOW);
    ctx.scr.pause(0.25).await;
    tb.close(ctx);
    cur
}

fn yes_no_menu(cx: i32, cy: i32, title: &str, default_yes: bool) -> Menu<'_> {
    Menu {
        cx,
        cy,
        title,
        width: (title.chars().count() as i32 + 2).max(16),
        items: &[text::YES, text::NO],
        item_width: 4,
        default: if default_yes { 0 } else { 1 },
    }
}

/// Asks a yes/no question; returns true for "Ano".
pub async fn yes_no(ctx: &mut Ctx, cx: i32, cy: i32, question: &str, default_yes: bool) -> bool {
    let title = format!("{question} ?");
    yes_no_menu(cx, cy, &title, default_yes).run(ctx).await == 0
}

/// The red "Nerozumím" box with a growl, for keys that mean nothing here.
pub async fn not_understood(ctx: &mut Ctx, cx: i32, cy: i32) {
    let tb = TextBox::open(ctx, cx, cy, text::NOT_UNDERSTOOD, color::LIGHT_RED, 1, 32).await;
    let ok = button_rect(
        (tb.rect.x2 + tb.rect.cx()) / 2,
        tb.rect.y2 - 24,
        1,
        0,
        text::OK,
    );
    draw_button(&mut ctx.scr.canvas, ok, text::OK, color::YELLOW);
    ctx.scr.play(&buzz()).await;
    ctx.scr.wait_for_key(15.0).await;
    tb.close(ctx);
}

/// "Skončit ?" – ends the program after the credits when confirmed.
pub async fn quit_prompt(ctx: &mut Ctx) {
    ctx.scr.play(&buzz()).await;
    let title = format!("{} ?", text::QUIT);
    let menu = yes_no_menu(1, 1, &title, false);
    if run_menu(ctx, &menu, color::LIGHT_RED, MenuMode::Lenient).await == 0 {
        Box::pin(super::title::credits(ctx)).await;
        std::process::exit(0);
    }
}

/// Draws a temporary label; restore the returned area to remove it.
pub fn temp_button(ctx: &mut Ctx, r: Rect, s: &str, col: u8) -> Saved {
    let saved = save(&ctx.scr.canvas, r);
    draw_button(&mut ctx.scr.canvas, r, s, col);
    saved
}

/// Waits two seconds, then shows "press any key" until a key or `secs` pass.
pub async fn press_any_key(ctx: &mut Ctx, secs: f64) {
    ctx.scr.wait(2.0).await;
    if !ctx.scr.has_key() {
        let r = button_rect(0, 999, 2, 1, text::PRESS_ANY_KEY);
        let saved = temp_button(ctx, r, text::PRESS_ANY_KEY, color::BLUE);
        ctx.scr.wait(secs - 2.0).await;
        restore(&mut ctx.scr.canvas, &saved);
    }
    ctx.scr.flush_keys();
}

/// A random colour in `1..=max` that differs from `exclude`.
pub fn random_color(ctx: &mut Ctx, max: u32, exclude: &[u8]) -> u8 {
    loop {
        let c = ctx.rng.below(max) as u8 + 1;
        if !exclude.contains(&c) {
            return c;
        }
    }
}

// ----------------------------------------------------------------- bubbles

/// A speech bubble; close it to restore what was underneath.
pub struct Bubble {
    saved: Saved,
}

impl Bubble {
    pub fn close(self, ctx: &mut Ctx) {
        restore(&mut ctx.scr.canvas, &self.saved);
    }
}

/// Opens a speech bubble for player `who` (0 human, 1 left, 2 right).
/// Lines containing '!' are shouted in large letters.
pub async fn bubble(ctx: &mut Ctx, who: usize, line1: &str, line2: &str, silent: bool) -> Bubble {
    let shout = line1.contains('!');
    let width = |s: &str| {
        if shout {
            smooth_width(s, 1)
        } else {
            text_width(s)
        }
    };
    let height = if shout { 16 } else { 8 };
    let c = random_color(ctx, 12, &[ctx.cfg.table_color, ctx.cfg.menu_color]);
    let mut rx = width(&format!("{line1}     ")) / 2;
    if !line2.is_empty() {
        rx = rx.max(text_width(line2) / 2 + 10);
    }
    rx = rx.max(80);
    let ry = (TW / 3 + height * 2 / 3).max(25) + if line2.is_empty() { 0 } else { 6 };
    let (w, h) = (rx + rx / 8, ry + ry / 8);
    let x = match who {
        1 => w + 50,
        2 => MAX_X - w - 50,
        _ => MAX_X / 2,
    };
    let y = if who == 0 { MAX_Y / 3 + 20 } else { ry + 45 };
    let rect = Rect::centered(x, y, w, h);
    let saved = save(&ctx.scr.canvas, rect);
    if !silent {
        let tune = puff_tune(ctx);
        ctx.scr.play(&tune).await;
    }
    let canvas = &mut ctx.scr.canvas;
    canvas.fill_ellipse(x, y, rx, ry, Fill::solid(c));
    for i in 1..=30 {
        let t = i as f64 * std::f64::consts::PI / 15.0;
        let (px, py) = (
            x + (t.cos() * rx as f64).round() as i32,
            y + (t.sin() * ry as f64).round() as i32,
        );
        canvas.fill_ellipse(px, py, rx / 9, ry / 9, Fill::solid(c));
    }
    let col = text_color_for(c);
    if shout {
        big_text_centered(canvas, x + 2, y - 2, line1, col);
    } else if line2.is_empty() {
        text_centered(canvas, x, y, line1, col);
    } else {
        text_centered(canvas, x, y - 7, &format!("{line1},"), col);
        text_centered(canvas, x, y + 7, line2, col);
    }
    ctx.scr.wait(0.5).await;
    Bubble { saved }
}

/// Shows a bubble, waits for a key or `secs`, and closes it.
pub async fn say(ctx: &mut Ctx, who: usize, line1: &str, line2: &str, secs: f64) {
    let b = bubble(ctx, who, line1, line2, false).await;
    if !ctx.quick {
        ctx.scr.wait(secs).await;
    }
    ctx.scr.flush_keys();
    b.close(ctx);
}
