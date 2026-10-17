//! The card table: background, the human's hand, cards in play, won-trick
//! piles, the contract label, and choosing a card with the arrow cursor.

use super::screen::Key;
use super::ui::{self, MAX_X, MAX_Y, Rect, draw_button, restore, save, text_color_for};
use super::{Ctx, text};
use crate::art::cards::{
    CARD_H, CARD_W, SPRITE_H, SPRITE_W, TRANSPARENT, render_back_sprite, render_card_sprite,
};
use crate::config::table_pattern;
use crate::game::cards::{Card, CardSet};
use crate::game::round::{Contract, Player};
use crate::gfx::{Canvas, Fill, color};

/// Pre-rendered card sprites.
pub struct Art {
    faces: Vec<Canvas>,
    backs: Vec<Canvas>,
}

impl Art {
    pub fn new() -> Art {
        Art {
            faces: (0..32)
                .map(|id| render_card_sprite(Card::from_id(id)))
                .collect(),
            // Backs only ever use colours 1..=7 (see `back_color`).
            backs: (0..8).map(render_back_sprite).collect(),
        }
    }

    pub fn face(&self, c: Card) -> &Canvas {
        &self.faces[c.id() as usize]
    }

    pub fn back(&self, line_color: u8) -> &Canvas {
        &self.backs[line_color as usize & 7]
    }
}

/// A random back colour that differs from the table.
pub fn back_color(ctx: &mut Ctx) -> u8 {
    let table = ctx.cfg.table_color;
    ui::random_color(ctx, 7, &[table])
}

pub fn draw_face(ctx: &mut Ctx, c: Card, x: i32, y: i32) {
    ctx.scr
        .canvas
        .blit(ctx.art.face(c), x, y, Some(TRANSPARENT));
}

pub fn draw_back(ctx: &mut Ctx, x: i32, y: i32, line_color: u8) {
    ctx.scr
        .canvas
        .blit(ctx.art.back(line_color), x, y, Some(TRANSPARENT));
}

pub fn table_fill(ctx: &Ctx) -> Fill {
    Fill::pattern(
        table_pattern(ctx.cfg.table_pattern),
        ctx.cfg.table_color,
        color::BLACK,
    )
}

/// What lies on the table besides the human's hand.
#[derive(Clone, Default)]
pub struct Scene {
    /// Cards of the trick in play: card and position.
    pub trick: Vec<(Card, i32, i32)>,
    /// Face-down cards on each player's won-trick pile.
    pub piles: [Vec<(i32, i32, u8)>; 3],
    pub label: Option<Label>,
    /// The human's cards in display order.
    pub hand: Vec<Card>,
    /// Cards of the hand shown face down (not yet looked at).
    pub hidden: CardSet,
    /// Cards shown face up in front of a computer player (claims, revealed hands).
    pub revealed: [Vec<Card>; 3],
}

#[derive(Clone)]
pub struct Label {
    pub player: Player,
    /// `None` while bidding: only the trump card is on show.
    pub contract: Option<Contract>,
    pub trump_card: Option<Card>,
    /// The trump card is shown face down: the defenders must not see the
    /// suit until the bidding is over.
    pub trump_face_down: bool,
    pub flek_game: u32,
    pub flek_seven: u32,
}

/// Hand positions on an arc at the bottom of the screen, left to right.
pub fn hand_positions(n: usize) -> Vec<(i32, i32)> {
    if n == 0 {
        return Vec::new();
    }
    let n_i = n as i32;
    let mut step = (MAX_X - CARD_W) / n_i;
    if step > 61 && step < 65 {
        step = 61;
    }
    step = step.min(79);
    let x0 = (MAX_X - (n_i - 1) * step - CARD_W) / 2;
    let base = MAX_Y - 5 - CARD_H;
    let lift = ((MAX_Y - CARD_H) / 4) as f64;
    let mut out: Vec<(i32, i32)> = Vec::new();
    for i in 1..=n_i {
        let mut y =
            base - ((i as f64 * std::f64::consts::PI / (n_i + 1) as f64).sin() * lift) as i32;
        if let Some(&(_, py)) = out.last()
            && step < CARD_W
            && py == y
        {
            y += 2;
        }
        out.push((x0 + (i - 1) * step, y));
    }
    out
}

/// Cards sorted for display by descending id; `hidden` cards go last.
pub fn sorted_hand(set: CardSet, hidden: CardSet) -> Vec<Card> {
    let mut v: Vec<Card> = set.iter().collect();
    v.sort_by_key(|&c| (hidden.contains(c), std::cmp::Reverse(c.id())));
    v
}

pub fn trick_position(ctx: &mut Ctx, p: Player) -> (i32, i32) {
    let x = MAX_X / 3 + [30, -30, 90][p] + ctx.rng.below(10) as i32;
    let y = [70, 50, 50][p] + ctx.rng.below(10) as i32;
    (x, y)
}

fn pile_origin(p: Player) -> (i32, i32) {
    match p {
        0 => (2 * MAX_X / 3, MAX_Y / 4 + 30),
        1 => (40, 30),
        _ => (MAX_X - 104, 30),
    }
}

fn label_origin(p: Player) -> (i32, i32) {
    match p {
        0 => (2 * MAX_X / 3 + 90, 160),
        1 => (20, 160),
        _ => (MAX_X - 160, 160),
    }
}

fn draw_label(ctx: &mut Ctx, l: &Label) {
    let (x, y) = label_origin(l.player);
    let mut title = l
        .contract
        .map_or(text::TRUMPS, text::contract_label)
        .to_string();
    if l.flek_game > 0 {
        title = format!("{title} {}x", 1u32 << l.flek_game.min(12));
    }
    let r = Rect {
        x1: x,
        y1: y,
        x2: x + 72,
        y2: y + 30,
    };
    let col = ctx.cfg.menu_color;
    draw_button(&mut ctx.scr.canvas, r, &title, col);
    if l.flek_seven > 0 {
        let r2 = Rect {
            x1: x,
            y1: y + 32,
            x2: x + 72,
            y2: y + 52,
        };
        draw_button(
            &mut ctx.scr.canvas,
            r2,
            &format!("7 {}x", 1u32 << l.flek_seven.min(12)),
            col,
        );
    }
    if let Some(tc) = l
        .trump_card
        .filter(|_| !l.contract.is_some_and(Contract::no_trumps))
    {
        // The human's label sits beside his pile, so its card goes underneath.
        let (cx, cy) = if l.player == 0 {
            (x, y + 56)
        } else {
            (x + 76, y)
        };
        if l.trump_face_down {
            // A fixed back colour: `back_color` would draw from the game's RNG.
            let line = if ctx.cfg.table_color == 1 { 2 } else { 1 };
            draw_back(ctx, cx, cy, line);
        } else {
            draw_face(ctx, tc, cx, cy);
        }
    }
}

/// Redraws the whole table from the scene description.
pub fn redraw(ctx: &mut Ctx, scene: &Scene) {
    clear_table(ctx);
    for p in 0..3 {
        for &(x, y, c) in &scene.piles[p] {
            draw_back(ctx, x, y, c);
        }
    }
    if let Some(l) = &scene.label {
        draw_label(ctx, l);
    }
    for p in [1, 2] {
        let cards = &scene.revealed[p];
        let (x0, y0) = if p == 1 { (20, 20) } else { (MAX_X - 84, 20) };
        let n = cards.len().max(1) as i32;
        let (dx, dy) = ((250 / n).min(54), (125 / n).min(51));
        for (i, &c) in cards.iter().enumerate() {
            let i = i as i32;
            draw_face(
                ctx,
                c,
                if p == 1 { x0 + i * dx } else { x0 - i * dx },
                y0 + i * dy,
            );
        }
    }
    for &(c, x, y) in &scene.trick {
        draw_face(ctx, c, x, y);
    }
    draw_hand(ctx, scene);
}

pub fn draw_hand(ctx: &mut Ctx, scene: &Scene) {
    let positions = hand_positions(scene.hand.len());
    let back = back_color(ctx);
    for (&c, &(x, y)) in scene.hand.iter().zip(&positions) {
        if scene.hidden.contains(c) {
            draw_back(ctx, x, y, back);
        } else {
            draw_face(ctx, c, x, y);
        }
    }
}

/// Puts a played card on the table with a thud.
pub async fn place_card(ctx: &mut Ctx, scene: &mut Scene, p: Player, c: Card) {
    let (x, y) = trick_position(ctx, p);
    scene.trick.push((c, x, y));
    draw_face(ctx, c, x, y);
    ctx.scr.play(&ui::card_thud()).await;
    ctx.scr.frame().await;
}

/// Moves the trick to the winner's pile (face down).
pub fn collect_trick(ctx: &mut Ctx, scene: &mut Scene, winner: Player) {
    let (ox, oy) = pile_origin(winner);
    for _ in 0..scene.trick.len() {
        let pos = (
            ox + ctx.rng.below(20) as i32,
            oy + ctx.rng.below(10) as i32 + 5,
            back_color(ctx),
        );
        scene.piles[winner].push(pos);
    }
    scene.trick.clear();
    redraw(ctx, scene);
}

// ----------------------------------------------------------- choosing a card

fn arrow_area(x: i32, y: i32) -> Rect {
    let (cx, cy) = (x + 32, y - 6);
    Rect {
        x1: cx - 8,
        y1: cy - 16,
        x2: cx + 8,
        y2: cy + 4,
    }
}

fn draw_arrow(c: &mut Canvas, x: i32, y: i32) {
    let (cx, cy) = (x + 32, y - 6);
    for (dx, dy, col) in [(1, 3, color::DARK_GRAY), (0, 0, color::YELLOW)] {
        let (cx, cy) = (cx + dx, cy + dy);
        for t in -1..=1 {
            c.line(cx - 1 + t, cy - 1, cx - 1 + t, cy - 13, col);
            c.line(cx + 1 + t, cy - 1, cx + 1 + t, cy - 13, col);
            c.line(cx + t, cy, cx - 6 + t, cy - 6, col);
            c.line(cx + t, cy, cx + 6 + t, cy - 6, col);
        }
        c.line(cx - 6, cy - 6, cx + 6, cy - 6, col);
    }
}

/// Why a card may not be played: the reprimand's two lines.
pub type Rebuke<'a> = &'a dyn Fn(&mut Ctx, Card) -> (String, String);

/// Lets the human pick a card from the hand on the table.
pub async fn select_card(
    ctx: &mut Ctx,
    scene: &Scene,
    allowed: CardSet,
    prompt: Option<&str>,
    rebuke: Rebuke<'_>,
) -> Card {
    if ctx.quick && allowed.len() == 1 {
        return allowed.first().expect("one card allowed");
    }
    let positions = hand_positions(scene.hand.len());
    let prompt_box = prompt.map(|s| {
        let pad = (16 - s.chars().count() as i32).max(3);
        let r = ui::button_rect(MAX_X / 3, 3 * MAX_Y / 7, pad, 1, s);
        let col = ctx.cfg.menu_color;
        ui::temp_button(ctx, r, s, col)
    });
    let mut cur = ctx.last_card_index.min(scene.hand.len().saturating_sub(1));
    while cur > 0 && !allowed.contains(scene.hand[cur]) {
        cur -= 1;
    }
    if !allowed.contains(scene.hand[cur]) {
        cur = scene
            .hand
            .iter()
            .position(|&c| allowed.contains(c))
            .unwrap_or(0);
    }
    ctx.scr.flush_keys();
    let chosen = loop {
        let (x, y) = positions[cur];
        let saved = save(&ctx.scr.canvas, arrow_area(x, y));
        draw_arrow(&mut ctx.scr.canvas, x, y);
        let mut next = cur;
        let mut pick = None;
        while next == cur && pick.is_none() {
            ctx.scr.frame().await;
            let hit = |mx: i32, my: i32| {
                positions.iter().rposition(|&(px, py)| {
                    mx >= px && mx < px + SPRITE_W && my >= py && my < py + SPRITE_H
                })
            };
            if let Some((mx, my)) = ctx.scr.take_mouse()
                && let Some(i) = hit(mx, my)
            {
                next = i;
            }
            match ctx.scr.take_key() {
                Some(Key::Left) => {
                    next = if cur == 0 {
                        scene.hand.len() - 1
                    } else {
                        cur - 1
                    }
                }
                Some(Key::Right) => next = (cur + 1) % scene.hand.len(),
                Some(Key::Enter) => pick = Some(cur),
                Some(Key::Click(mx, my)) => pick = hit(mx, my),
                Some(Key::Esc) => {
                    restore(&mut ctx.scr.canvas, &saved);
                    Box::pin(ui::quit_prompt(ctx)).await;
                    draw_arrow(&mut ctx.scr.canvas, x, y);
                }
                Some(Key::F10) => {
                    restore(&mut ctx.scr.canvas, &saved);
                    Box::pin(super::options::options_dialog(ctx)).await;
                    draw_arrow(&mut ctx.scr.canvas, x, y);
                }
                _ => {}
            }
        }
        restore(&mut ctx.scr.canvas, &saved);
        if let Some(i) = pick {
            let card = scene.hand[i];
            if allowed.contains(card) {
                ctx.last_card_index = i;
                break card;
            }
            let (l1, mut l2) = rebuke(ctx, card);
            if allowed.len() == 1 {
                let only = allowed.first().expect("one card allowed");
                l2 = format!(
                    "{} {} ?",
                    text::pick(&mut ctx.rng, "co třeba|a co"),
                    text::card_name(only)
                );
                next = scene.hand.iter().position(|&c| c == only).unwrap_or(cur);
            }
            ui::say(ctx, 0, &l1, &l2, 15.0).await;
        }
        cur = next;
    };
    if let Some(saved) = prompt_box {
        restore(&mut ctx.scr.canvas, &saved);
    }
    chosen
}

/// Paints the bevelled, patterned table; the image is cached until the
/// table colour or pattern changes.
pub fn clear_table(ctx: &mut Ctx) {
    let key = (ctx.cfg.table_color, ctx.cfg.table_pattern);
    if ctx.table_bg.as_ref().is_none_or(|(k, _)| *k != key) {
        let mut bg = Canvas::new(MAX_X + 1, MAX_Y + 1);
        ui::frame_window(&mut bg, ui::SCREEN, table_fill(ctx));
        ctx.table_bg = Some((key, bg));
    }
    if let Some((_, bg)) = &ctx.table_bg {
        ctx.scr.canvas.blit(bg, 0, 0, None);
    }
}

/// Colour for text drawn straight on the table.
pub fn table_text_color(ctx: &Ctx) -> u8 {
    text_color_for(ctx.cfg.table_color)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hand_fits_on_screen_and_arches() {
        for n in 1..=12 {
            let pos = hand_positions(n);
            assert_eq!(pos.len(), n);
            for &(x, y) in &pos {
                assert!(x >= 0 && x + CARD_W <= MAX_X, "n={n} x={x}");
                assert!(y + SPRITE_H <= MAX_Y + 1, "n={n} y={y}");
            }
            if n >= 3 {
                assert!(pos[n / 2].1 < pos[0].1, "middle card is higher");
            }
        }
    }
}
