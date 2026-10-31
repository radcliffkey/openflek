//! The game itself: one deal from shuffling to settlement, with the human
//! in seat 0 and two computer players.

use super::table::{self, Label, Scene, back_color, place_card, redraw, select_card, sorted_hand};
use super::ui::{self, MAX_X, MAX_Y, Menu, TextBox, say, yes_no};
use super::{Ctx, text};
use crate::game::ai;
use crate::game::cards::{Card, CardSet, Rank};
use crate::game::round::{Contract, Illegal, Player, Round, TrickEnd, next, prev};
use crate::game::settle::{GameItem, Settlement, SevenItem, settle};
use crate::gfx::color;

const MENU_X: i32 = MAX_X / 3;
const MENU_Y: i32 = MAX_Y / 2 - 30;

/// The seat whose cards are shown face up at the bottom of the screen; the
/// only one a human can play.
const VIEWER: Player = 0;

/// Who makes the decisions of a seat.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Seat {
    /// Menus and card selection on the screen.
    Human,
    /// The computer players' logic in `ai`.
    Computer,
}

/// Flek, re, tutti, ...: the call for raising the game to `level` doublings.
fn raise_call(level: u32) -> &'static str {
    match level {
        0 | 1 => text::FLEK_SAID,
        2 => text::RE_SAID,
        3 => text::TUTTI_SAID,
        n => text::HIGHER_SAID[(n as usize - 4).min(text::HIGHER_SAID.len() - 1)],
    }
}

/// Mutable state of the bidding that the original keeps in locals.
#[derive(Default)]
struct Raises {
    /// The game / the seven was raised in the current step.
    game: bool,
    seven: bool,
}

/// A defender's answer to "Jaký betl?".
#[derive(Clone, Copy, PartialEq, Eq)]
enum BetlAnswer {
    Good,
    Flek,
    /// "Špatný": he takes over with durch.
    Durch,
}

/// How one deal went, for the log and for tests.
#[derive(Clone, Debug)]
pub struct DealSummary {
    pub declarer: Player,
    pub contract: Contract,
    pub flek_game: u32,
    pub flek_seven: u32,
    /// How many times each seat doubled or redoubled.
    pub raises: [u32; 3],
    /// Settled without being played.
    pub not_played: bool,
}

struct Deal<'a> {
    ctx: &'a mut Ctx,
    r: Round,
    scene: Scene,
    seats: [Seat; 3],
    /// How many times each seat doubled or redoubled.
    raised_by: [u32; 3],
}

impl Deal<'_> {
    fn show_hand(&mut self) {
        self.show_cards(self.r.hands[VIEWER]);
    }

    /// Shows the hand as if `card` had already left it.
    fn show_hand_without(&mut self, card: Card) {
        self.show_cards(self.r.hands[VIEWER].minus(card.into()));
    }

    fn show_cards(&mut self, cards: CardSet) {
        self.scene.hand = sorted_hand(cards, self.scene.hidden);
        redraw(self.ctx, &self.scene);
    }

    /// Says one variant of `line1` (and of `line2`, if any).
    async fn say(&mut self, who: Player, line1: &'static str, line2: &'static str) {
        let l1 = text::pick(&mut self.ctx.rng, line1);
        let l2 = if line2.is_empty() {
            ""
        } else {
            text::pick(&mut self.ctx.rng, line2)
        };
        say(self.ctx, who, l1, l2, 0.5).await;
    }

    // ------------------------------------------------------------ decisions
    //
    // Each decision is asked of the seat that makes it: a human answers in
    // menus and by picking cards, a computer through `ai`.

    /// The forehand picks the trump card from his first seven, or blindly.
    async fn pick_trump_card(&mut self) -> Card {
        match self.seats[self.r.forehand] {
            Seat::Human => {
                self.scene.hidden = self.r.hands[VIEWER].minus(self.r.first_seven);
                self.show_hand();
                let prompt = text::pick(&mut self.ctx.rng, text::CHOOSE_TRUMPS);
                let all = self.r.hands[VIEWER];
                select_card(self.ctx, &self.scene, all, Some(prompt), &|_, _| {
                    (String::new(), String::new())
                })
                .await
            }
            Seat::Computer => ai::choose_trump_card(&self.r, &mut self.ctx.rng),
        }
    }

    /// The forehand's contract before discarding. A human decides only
    /// between a suit game and betl here.
    async fn pick_forehand_contract(&mut self) -> Contract {
        match self.seats[self.r.forehand] {
            Seat::Human => {
                let choice = Menu {
                    cx: MENU_X,
                    cy: MENU_Y,
                    title: text::DISCARD_KIND,
                    width: 36,
                    items: &[text::DISCARD_FOR_SUIT_GAME, text::DISCARD_FOR_BETL],
                    item_width: 12,
                    default: 0,
                }
                .run(self.ctx)
                .await;
                if choice == 1 {
                    Contract::Betl
                } else {
                    Contract::Game
                }
            }
            Seat::Computer => {
                self.r.compute_marriages();
                let iq = self.ctx.brain.iq;
                ai::forehand_contract(&self.r, &mut self.ctx.rng, iq)
            }
        }
    }

    /// The two cards the declarer discards to the talon.
    async fn pick_discard(&mut self) -> [Card; 2] {
        match self.seats[self.r.declarer] {
            Seat::Human => {
                let mut allowed = self.r.discardable(VIEWER);
                let rebuke = |ctx: &mut Ctx, _c: Card| {
                    (
                        text::pick(&mut ctx.rng, text::REBUKE).to_string(),
                        text::SHARP_TO_TALON.to_string(),
                    )
                };
                let p1 = text::pick(&mut self.ctx.rng, text::DISCARD_FIRST);
                let first = select_card(self.ctx, &self.scene, allowed, Some(p1), &rebuke).await;
                allowed.remove(first);
                self.show_hand_without(first);
                let p2 = text::pick(&mut self.ctx.rng, text::DISCARD_SECOND);
                let second = select_card(self.ctx, &self.scene, allowed, Some(p2), &rebuke).await;
                [first, second]
            }
            Seat::Computer => ai::choose_discard(&self.r, &mut self.ctx.rng),
        }
    }

    /// "Barva?" – `None` if `p` lets the suit game stand, else the contract
    /// he takes over with. A human always takes over with betl.
    async fn answer_colour(&mut self, p: Player) -> Option<Contract> {
        match self.seats[p] {
            Seat::Human => {
                let title = text::pick(&mut self.ctx.rng, text::YOUR_SAY);
                let menu = Menu {
                    cx: 0,
                    cy: MENU_Y,
                    title,
                    width: 19,
                    items: &[text::GOOD, text::BAD],
                    item_width: 6,
                    default: 0,
                };
                (menu.run(self.ctx).await != 0).then_some(Contract::Betl)
            }
            Seat::Computer => {
                let betl = ai::wants_betl(&self.r, p, &mut self.ctx.rng);
                let durch = ai::wants_durch(&self.r, p);
                match (betl, durch) {
                    (_, true) => Some(Contract::Durch),
                    (true, false) => Some(Contract::Betl),
                    (false, false) => None,
                }
            }
        }
    }

    /// "Jaký betl?" – the answer of defender `p`, who may double if `can_flek`.
    async fn answer_betl(&mut self, p: Player, can_flek: bool) -> BetlAnswer {
        match self.seats[p] {
            Seat::Human => {
                let mut items = vec![text::BETL_GOOD, text::BETL_BAD];
                if can_flek {
                    items.push(text::FLEK);
                }
                let title = text::pick(&mut self.ctx.rng, text::YOUR_SAY);
                let menu = Menu {
                    cx: 0,
                    cy: MENU_Y,
                    title,
                    width: 29,
                    items: &items,
                    item_width: 6,
                    default: 0,
                };
                match menu.run(self.ctx).await {
                    0 => BetlAnswer::Good,
                    1 => BetlAnswer::Durch,
                    _ => BetlAnswer::Flek,
                }
            }
            Seat::Computer => {
                if ai::wants_durch(&self.r, p) {
                    BetlAnswer::Durch
                } else if can_flek
                    && ai::defender_flek(&self.r, p, &mut self.ctx.rng, &mut self.ctx.brain).0
                {
                    BetlAnswer::Flek
                } else {
                    BetlAnswer::Good
                }
            }
        }
    }

    /// "Co teď?" – a betl declarer may raise to durch; a computer never does.
    async fn pick_betl_or_durch(&mut self) -> Contract {
        match self.seats[self.r.declarer] {
            Seat::Human => {
                let title = format!("{} ?", text::pick(&mut self.ctx.rng, text::WHAT_NOW));
                let i = Menu {
                    cx: MENU_X,
                    cy: MENU_Y,
                    title: &title,
                    width: 20,
                    items: &[text::BETL, text::DURCH],
                    item_width: 6,
                    default: 0,
                }
                .run(self.ctx)
                .await;
                if i == 1 {
                    Contract::Durch
                } else {
                    Contract::Betl
                }
            }
            Seat::Computer => self.r.contract,
        }
    }

    /// The suit-game declarer's final contract, chosen with the whole hand
    /// in view; a computer announced his already as forehand.
    async fn pick_final_contract(&mut self) -> Contract {
        match self.seats[self.r.declarer] {
            Seat::Human => {
                self.update_label();
                let i = Menu {
                    cx: MENU_X,
                    cy: MENU_Y,
                    title: text::FINAL_CONTRACT,
                    width: 37,
                    items: &text::CONTRACT_BUTTONS[self.r.contract as usize..],
                    item_width: 6,
                    default: 0,
                }
                .run(self.ctx)
                .await;
                [
                    Contract::Game,
                    Contract::Seven,
                    Contract::Hundred,
                    Contract::HundredSeven,
                ][self.r.contract as usize + i]
            }
            Seat::Computer => self.r.contract,
        }
    }

    /// Defender `p`'s doubles: (on the game, on the seven), limited to what
    /// he may still double. `None` if a human has nothing to choose from.
    async fn answer_flek(
        &mut self,
        p: Player,
        can_game: bool,
        can_seven: bool,
    ) -> Option<(bool, bool)> {
        match self.seats[p] {
            Seat::Human => {
                if !can_game && !can_seven {
                    return None;
                }
                let r = &self.r;
                let game_label = match r.contract {
                    Contract::Seven => text::ON_GAME,
                    Contract::HundredSeven => text::ON_HUNDRED,
                    _ => text::FLEK,
                };
                let seven_label = if r.seven_announced {
                    text::ON_SEVEN
                } else {
                    text::SEVEN_AGAINST
                };
                let mut items = vec![(text::OK, (false, false))];
                if can_game {
                    items.push((game_label, (true, false)));
                }
                if can_seven {
                    items.push((seven_label, (false, true)));
                }
                if can_game && can_seven {
                    items.push((text::BOTH, (true, true)));
                }
                let labels: Vec<&str> = items.iter().map(|i| i.0).collect();
                let title = text::pick(&mut self.ctx.rng, text::YOUR_SAY);
                let width = (labels.len() as i32 * 9 + 4).max(19);
                let menu = Menu {
                    cx: 0,
                    cy: MENU_Y,
                    title,
                    width,
                    items: &labels,
                    item_width: 7,
                    default: 0,
                };
                let i = menu.run(self.ctx).await;
                Some(items[i].1)
            }
            Seat::Computer => {
                let (g, s) = ai::defender_flek(&self.r, p, &mut self.ctx.rng, &mut self.ctx.brain);
                Some((g && can_game, s && can_seven))
            }
        }
    }

    /// The declarer's re: (on the game, on the seven), given what was doubled.
    async fn answer_re(&mut self, raised_game: bool, raised_seven: bool) -> (bool, bool) {
        match self.seats[self.r.declarer] {
            Seat::Human => match (raised_game, raised_seven) {
                (true, false) => (
                    yes_no(self.ctx, 1, 999, text::RAISE_GAME, false).await,
                    false,
                ),
                (false, true) => (
                    false,
                    yes_no(self.ctx, 1, 999, text::RAISE_SEVEN, false).await,
                ),
                _ => {
                    let i = Menu {
                        cx: 1,
                        cy: 999,
                        title: text::RAISE_GAME,
                        width: 42,
                        items: &text::RAISE_BUTTONS,
                        item_width: 7,
                        default: 0,
                    }
                    .run(self.ctx)
                    .await;
                    (i == 1 || i == 3, i == 2 || i == 3)
                }
            },
            Seat::Computer => {
                ai::declarer_re(&self.r, raised_game, &mut self.ctx.rng, &mut self.ctx.brain)
            }
        }
    }

    /// The card `p` plays to the current trick.
    async fn pick_card(&mut self, p: Player) -> Card {
        match self.seats[p] {
            Seat::Human => {
                let allowed = self.r.legal(p);
                let prompt = if self.r.table.is_empty() {
                    Some(text::pick(&mut self.ctx.rng, text::LEAD))
                } else {
                    None
                };
                let r = &self.r;
                let rebuke = |ctx: &mut Ctx, c: Card| rebuke(r, ctx, p, c);
                select_card(self.ctx, &self.scene, allowed, prompt, &rebuke).await
            }
            Seat::Computer => self.computer_card(p).await,
        }
    }

    async fn computer_card(&mut self, p: Player) -> Card {
        let start = self.ctx.scr.now();
        let searches = self.ctx.brain.depth() >= 2 || self.r.trick_no() > 8;
        let thinking = searches && self.r.trick_no() < 9 && !self.ctx.quick;
        let bubble = if thinking {
            let s = format!("{}...", text::pick(&mut self.ctx.rng, text::THINKING));
            Some(ui::bubble(self.ctx, p, &s, "", true).await)
        } else {
            None
        };
        self.ctx.brain.start_move(&mut self.r);
        let card = ai::choose_card(&self.r, &mut self.ctx.rng, &mut self.ctx.brain);
        let min = if self.ctx.brain.iq <= 100 { 0.5 } else { 1.0 };
        if !self.ctx.quick && (thinking || (self.r.trick_no() < 6 && self.ctx.rng.below(3) > 1)) {
            let left = min - (self.ctx.scr.now() - start);
            if left > 0.0 {
                self.ctx.scr.pause(left).await;
            }
        } else if !self.ctx.quick {
            self.ctx.scr.pause(0.2).await;
        }
        if let Some(b) = bubble {
            b.close(self.ctx);
        }
        card
    }

    // ---------------------------------------------------------------- bidding

    async fn choose_trump(&mut self) {
        let fh = self.r.forehand;
        let card = self.pick_trump_card().await;
        let blind = !self.r.first_seven.contains(card);
        self.r.choose_trump(card);
        self.scene.hidden = CardSet::EMPTY;
        if fh == VIEWER {
            // The forehand knows his trump card; nobody else sees it yet.
            self.show_trump(fh);
            if blind {
                let name = text::card_name(card);
                say(self.ctx, fh, text::FROM_THE_PEOPLE, &name, 0.5).await;
            }
        } else {
            self.show_hand();
        }
    }

    /// Shows the laid-aside trump card next to `player` while bidding, face
    /// up only to its owner.
    fn show_trump(&mut self, player: Player) {
        self.scene.label = Some(Label {
            player,
            contract: None,
            trump_card: self.r.trump_card,
            trump_face_down: player != VIEWER,
            flek_game: 0,
            flek_seven: 0,
        });
        self.show_hand();
    }

    async fn discard(&mut self) {
        let talon = self.pick_discard().await;
        self.r.discard(talon);
        self.show_hand();
    }

    /// The forehand decides between a suit game and betl/durch and discards.
    async fn forehand_phase(&mut self) {
        let contract = self.pick_forehand_contract().await;
        self.r.declare(contract);
        if contract.no_trumps() && self.r.forehand == VIEWER {
            // The trump card is back in the hand.
            self.scene.label = None;
            self.show_hand();
        }
        self.discard().await;
        // The trump card stays face down through "Barva?"; it is turned up
        // once the bidding is over.
        if self.r.contract.no_trumps() {
            self.scene.label = None;
            self.show_hand();
        } else {
            self.show_trump(self.r.declarer);
        }
    }

    /// A defender takes over with betl or durch: picks up the talon and discards.
    async fn take_over(&mut self, p: Player, contract: Contract) {
        self.r.take_over(p, contract);
        self.scene.label = None;
        self.show_hand();
        self.discard().await;
    }

    /// "Barva?" – true if `p` lets the suit game stand.
    async fn ask_colour(&mut self, p: Player) -> bool {
        let take_over = self.answer_colour(p).await;
        let line = if take_over.is_none() {
            text::GOOD_SAID
        } else {
            text::BAD_SAID
        };
        self.say(p, line, "").await;
        if let Some(contract) = take_over {
            self.take_over(p, contract).await;
        }
        take_over.is_none()
    }

    /// "Jaký betl?" – true if `p` lets the betl stand (possibly doubling it).
    async fn ask_betl(&mut self, p: Player, raises: &mut Raises) -> bool {
        let answer = self.answer_betl(p, !raises.game).await;
        match answer {
            BetlAnswer::Flek => {
                raises.game = true;
                self.raised_by[p] += 1;
                self.say(p, raise_call(self.r.flek_game + 1), "").await;
            }
            BetlAnswer::Good => self.say(p, text::BETL_GOOD, "").await,
            BetlAnswer::Durch => {
                self.say(p, text::BETL_BAD, "").await;
                self.take_over(p, Contract::Durch).await;
                raises.game = false;
            }
        }
        answer != BetlAnswer::Durch
    }

    fn update_label(&mut self) {
        self.scene.label = Some(Label {
            player: self.r.declarer,
            contract: Some(self.r.contract),
            trump_card: self.r.trump_card,
            trump_face_down: false,
            flek_game: self.r.flek_game,
            flek_seven: self.r.flek_seven,
        });
        redraw(self.ctx, &self.scene);
    }

    async fn bidding(&mut self) -> Raises {
        let mut raises = Raises::default();
        self.forehand_phase().await;
        loop {
            let d = self.r.declarer;
            let ok = match self.r.contract {
                Contract::Durch => false,
                Contract::Betl => {
                    let contract = self.pick_betl_or_durch().await;
                    self.r.raise_contract(contract);
                    if contract == Contract::Betl {
                        self.say(d, text::ASK_BETL, "").await;
                        self.ask_betl(next(d), &mut raises).await
                            && self.ask_betl(prev(d), &mut raises).await
                    } else {
                        false
                    }
                }
                _ => {
                    self.say(d, text::ASK_SUIT, "").await;
                    self.ask_colour(next(d)).await && self.ask_colour(prev(d)).await
                }
            };
            if ok || self.r.contract == Contract::Durch {
                break;
            }
        }
        let d = self.r.declarer;
        self.r.finish_bidding();
        if !self.r.contract.no_trumps() {
            self.show_hand();
            let contract = self.pick_final_contract().await;
            self.r.raise_contract(contract);
        }
        self.update_label();
        if self.r.contract != Contract::Betl {
            self.say(d, text::ASK_ALL, text::ADDRESS).await;
        }
        raises
    }

    /// A defender may double the game and/or the seven.
    async fn defender_flek(&mut self, p: Player, raises: &mut Raises) -> bool {
        let r = &self.r;
        let can_game = !raises.game;
        let holds_t7 = r.trump_seven().is_some_and(|c| r.hands[p].contains(c));
        let can_seven = !r.contract.no_trumps() && !raises.seven && (r.seven_announced || holds_t7);
        let Some((game, seven)) = self.answer_flek(p, can_game, can_seven).await else {
            return false;
        };
        let seven_text = if self.r.seven_announced {
            text::FLEK_SEVEN_SAID
        } else {
            text::SEVEN_AGAINST_SAID
        };
        match (game, seven) {
            (true, true) => {
                let s = if self.r.seven_announced {
                    text::BOTH_SAID
                } else {
                    text::BOTH_SEVEN_AGAINST_SAID
                };
                self.say(p, s, "").await;
            }
            (true, false) if self.r.contract.has_seven() => {
                self.say(p, text::FLEK_GAME_SAID, "").await
            }
            (true, false) => self.say(p, raise_call(self.r.flek_game + 1), "").await,
            (false, true) => self.say(p, seven_text, "").await,
            (false, false) => self.say(p, text::SILENT, "").await,
        }
        raises.game |= game;
        raises.seven |= seven;
        // A defender's seven becomes the announced one ("sedma proti").
        self.r.seven_announced |= seven;
        if game || seven {
            self.raised_by[p] += 1;
        }
        game || seven
    }

    /// The declarer answers the doubles of this step with "re" or silence.
    async fn declarer_response(&mut self, raises: &mut Raises) -> bool {
        let (raised_game, raised_seven) = (raises.game, raises.seven);
        if raised_game {
            self.r.flek_game += 1;
        }
        if raised_seven && self.r.contract.has_seven() {
            self.r.flek_seven += 1;
        }
        *raises = Raises::default();
        self.update_label();
        if !raised_game && !raised_seven {
            return false;
        }
        let d = self.r.declarer;
        let (re_game, re_seven) = self.answer_re(raised_game, raised_seven).await;
        match (re_game, re_seven) {
            (true, true) => self.say(d, text::RE_BOTH_SAID, "").await,
            (false, true) => self.say(d, text::RE_SEVEN_SAID, "").await,
            (true, false) => self.say(d, raise_call(self.r.flek_game + 1), "").await,
            (false, false) => {
                let s = if self.r.flek_game >= 3 {
                    text::STOP_SAID
                } else {
                    text::NO_RE_SAID
                };
                self.say(d, s, "").await;
            }
        }
        if re_game {
            self.r.flek_game += 1;
        }
        if re_seven {
            self.r.flek_seven += 1;
        }
        if re_game || re_seven {
            self.raised_by[d] += 1;
        }
        self.update_label();
        re_game || re_seven
    }

    async fn flek_rounds(&mut self, mut raises: Raises) {
        // In betl the defenders already had their say in "Jaký betl?".
        let mut defenders_asked = self.r.contract == Contract::Betl;
        loop {
            if !defenders_asked {
                let d = self.r.declarer;
                let a = self.defender_flek(next(d), &mut raises).await;
                let b = self.defender_flek(prev(d), &mut raises).await;
                if !(a || b) {
                    break;
                }
            }
            defenders_asked = false;
            if !self.declarer_response(&mut raises).await {
                break;
            }
        }
    }

    // ------------------------------------------------------------------- play

    fn reveal(&mut self, players: &[Player]) {
        for &p in players {
            if p != VIEWER {
                self.scene.revealed[p] = sorted_hand(self.r.hands[p], CardSet::EMPTY);
            }
        }
        redraw(self.ctx, &self.scene);
    }

    async fn play_tricks(&mut self) {
        self.r.start_play();
        self.show_hand();
        while !self.r.is_over() {
            let p = self.r.to_play();
            let card = self.pick_card(p).await;
            let marriage = card.rank() == Rank::Over
                && self.r.marriages.contains(card)
                && self.r.hands[p].contains(Card::new(card.suit(), Rank::King));
            if p == VIEWER {
                self.show_hand_without(card);
            }
            place_card(self.ctx, &mut self.scene, p, card).await;
            if marriage {
                let pts = self.r.marriage_value(card.suit()).to_string();
                say(self.ctx, p, &pts, "", 1.5).await;
            }
            let Some(end) = self.r.play(card) else {
                continue;
            };
            let winner = self.r.tricks.last().map(|t| t.winner).unwrap_or(0);
            if !self.ctx.quick {
                ui::press_any_key(self.ctx, 20.0).await;
            }
            table::collect_trick(self.ctx, &mut self.scene, winner);
            match end {
                TrickEnd::ContractLost => {
                    let d = self.r.declarer;
                    let who = if winner == d { next(d) } else { winner };
                    let s = if self.r.contract == Contract::Betl {
                        text::BETL_LOST
                    } else {
                        text::DURCH_LOST
                    };
                    self.say(who, s, "").await;
                }
                TrickEnd::BetlWon => {
                    let d = self.r.declarer;
                    self.reveal(&[d]);
                    self.say(d, text::BETL_WON, "").await;
                }
                TrickEnd::Claimed => {
                    self.reveal(&[1, 2]);
                    self.say(winner, text::CLAIM, "").await;
                    self.finish_silently();
                }
                TrickEnd::Normal => {}
            }
        }
    }

    /// Plays out a claimed deal without showing it.
    fn finish_silently(&mut self) {
        while !self.r.is_over() {
            let p = self.r.to_play();
            let c = self.r.legal(p).first().expect("player has a legal card");
            self.r.play(c);
        }
    }

    async fn settlement(&mut self) {
        let s = settle(&self.r);
        let d = self.r.declarer;
        let mut lines: Vec<(String, String)> = Vec::new();
        if let Some(p) = s.points {
            lines.push((
                format!(
                    "{}: {}+{} / {}+{}",
                    text::POINTS,
                    p.declarer,
                    p.declarer_marriages,
                    p.defenders,
                    p.defender_marriages
                ),
                String::new(),
            ));
        }
        let side = |amount: i64| text::money(for_viewer(amount, d));
        if s.game != 0 {
            lines.push((game_line(&s), side(s.game)));
        }
        if s.seven_money != 0
            && let Some(l) = seven_line(&s)
        {
            lines.push((l, side(s.seven_money)));
        }
        if s.seven_money != 0 || s.hearts {
            let total = if s.hearts {
                text::pick(&mut self.ctx.rng, text::TOTAL_HEARTS)
            } else {
                text::TOTAL
            };
            lines.push((total.to_string(), side(s.per_defender)));
        }
        let net = s.net(VIEWER, d);
        if s.per_defender == 0 {
            lines.push((
                text::pick(&mut self.ctx.rng, text::FREE).to_string(),
                String::new(),
            ));
        } else {
            let l = text::pick(
                &mut self.ctx.rng,
                if net > 0 {
                    text::YOU_WON
                } else {
                    text::YOU_LOST
                },
            );
            lines.push((l.to_string(), text::money(net.abs())));
            self.ctx.money += net;
        }
        lines.push((text::YOU_HAVE_NOW.to_string(), text::money(self.ctx.money)));
        let title = if s.not_played {
            text::AS_IF_PLAYED
        } else {
            text::SETTLEMENT
        };
        let tb = TextBox::open(
            self.ctx,
            MAX_X / 2,
            MAX_Y / 3,
            title,
            color::BLUE,
            lines.len() as i32,
            40,
        )
        .await;
        for (i, (l, m)) in lines.iter().enumerate() {
            tb.line(&mut self.ctx.scr.canvas, i as i32, l, ui::Justify::Left);
            if !m.is_empty() {
                tb.line(&mut self.ctx.scr.canvas, i as i32, m, ui::Justify::Right);
            }
        }
        self.ctx.scr.wait_for_key(20.0).await;
        if self.ctx.money < 0 {
            self.ctx.scr.play(&ui::buzz()).await;
            self.say(VIEWER, text::BROKE, text::BROKE_2).await;
        }
        let offer = !s.not_played
            && !(self.r.contract.no_trumps() && self.r.decided)
            && self.seats[VIEWER] == Seat::Human;
        let show = offer && {
            let q = text::pick(&mut self.ctx.rng, text::SHOW_TRICKS);
            yes_no(self.ctx, 999, 999, q, false).await
        };
        tb.close(self.ctx);
        if show {
            self.replay().await;
        }
    }

    /// Lays out the talon and all ten tricks.
    async fn replay(&mut self) {
        table::clear_table(self.ctx);
        for (i, &c) in self.r.talon.iter().enumerate() {
            table::draw_face(self.ctx, c, MAX_X - 80 - 80 * i as i32, 300);
        }
        for (i, t) in self.r.tricks.iter().enumerate() {
            let (col, row) = (i as i32 % 5, i as i32 / 5);
            let (x0, y0) = (12 + col * 124, 12 + row * 136);
            for k in 0..3 {
                let p = t.player_of(k);
                let (x, y) = (x0 + k as i32 * 26, y0 + k as i32 * 4);
                table::draw_face(self.ctx, t.cards[k], x, y);
                if p == VIEWER {
                    self.ctx.scr.canvas.rect(
                        x + 27,
                        y + 108,
                        x + 37,
                        y + 116,
                        color::LIGHT_MAGENTA,
                    );
                }
                if p == t.winner {
                    self.ctx.scr.canvas.bar(
                        x + 4,
                        y + 107,
                        x + 22,
                        y + 109,
                        crate::gfx::Fill::solid(color::YELLOW),
                    );
                }
            }
            let tc = table::table_text_color(self.ctx);
            ui::text_left(
                &mut self.ctx.scr.canvas,
                x0,
                y0 + 122,
                &format!("{}.", i + 1),
                tc,
            );
            self.ctx.scr.pause(0.1).await;
        }
        self.ctx.scr.wait_for_key(10.0).await;
        ui::press_any_key(self.ctx, 30.0).await;
    }
}

/// Why `p` may not play `card`: the two lines of the reprimand.
fn rebuke(r: &Round, ctx: &mut Ctx, p: Player, card: Card) -> (String, String) {
    let l1 = text::pick(&mut ctx.rng, text::REBUKE).to_string();
    let reason = r.illegal_reason(p, card);
    let you_have = match reason {
        Illegal::QueenFirst => {
            return (
                text::pick(&mut ctx.rng, text::REBUKE_KING).to_string(),
                String::new(),
            );
        }
        Illegal::KeepSeven => return (l1, text::KEEP_SEVEN.to_string()),
        _ => text::pick(&mut ctx.rng, text::YOU_HAVE),
    };
    let l2 = match reason {
        Illegal::MustBeat => format!("{you_have} {}", text::HIGHER),
        Illegal::MustFollow(suit) => format!("{you_have} {}", text::SUIT_NAMES[suit as usize]),
        Illegal::MustTrump => format!("{you_have} {}", text::TRUMPS),
        _ => text::pick(&mut ctx.rng, text::NOT_ALLOWED).to_string(),
    };
    (l1, l2)
}

/// A settlement amount, signed from the declarer's side, turned to the
/// viewer's: what the viewer loses shows with a minus.
fn for_viewer(amount: i64, declarer: Player) -> i64 {
    if declarer == VIEWER { amount } else { -amount }
}

/// The settlement line of the game part, e.g. "Hra, 2x flek:".
fn game_line(s: &Settlement) -> String {
    let name = match s.game_item {
        GameItem::Plain => return format!("{}:", text::PLAIN_GAME),
        GameItem::PlainDoubled => return format!("{}:", text::DOUBLED_GAME),
        GameItem::Game => text::GAME.to_string(),
        GameItem::SilentHundred { points, against } => {
            format!(
                "{} {points}{}",
                text::SILENT_HUNDRED,
                if against { text::AGAINST } else { "" }
            )
        }
        GameItem::Hundred { points } if points > 100 => points.to_string(),
        GameItem::Hundred { .. } => text::HUNDRED.to_string(),
        GameItem::HundredLost => text::HUNDRED_LOST.to_string(),
        GameItem::Betl => text::BETL.to_string(),
        GameItem::Durch => text::DURCH.to_string(),
    };
    match s.flek_game {
        0 => format!("{name}:"),
        1 => format!("{name}, flek:"),
        n => format!("{name}, {n}x flek:"),
    }
}

/// The settlement line of the seven, e.g. "Sedma, zabitá proti:".
fn seven_line(s: &Settlement) -> Option<String> {
    let res = s.seven?;
    let mut line = match res.item {
        SevenItem::Won => text::SEVEN,
        SevenItem::Lost => text::SEVEN_LOST,
        SevenItem::Silent => text::SILENT_SEVEN,
    }
    .to_string();
    if res.killed {
        line += text::KILLED;
    }
    if res.against {
        line += text::AGAINST;
    }
    line += if s.flek_seven > 0 { ", flek:" } else { ":" };
    Some(line)
}

/// Plays one complete deal with `dealer` dealing; `seats` says who decides
/// for each player.
pub async fn play_deal(ctx: &mut Ctx, dealer: Player, seats: [Seat; 3]) -> DealSummary {
    debug_assert!(
        (0..3).all(|p| p == VIEWER || seats[p] == Seat::Computer),
        "only the viewer's seat can be human"
    );
    let r = Round::deal(&mut ctx.deck, dealer, &mut ctx.rng);
    let scene = Scene {
        back: back_color(ctx),
        ..Scene::default()
    };
    let mut deal = Deal {
        ctx,
        r,
        scene,
        seats,
        raised_by: [0; 3],
    };
    deal.show_hand();
    deal.choose_trump().await;
    let raises = deal.bidding().await;
    deal.flek_rounds(raises).await;
    let r = &mut deal.r;
    log::debug!(
        "contract {:?} by {} (forehand {}), hands {:?}, talon {:?}, trump card {:?}",
        r.contract,
        r.declarer,
        r.forehand,
        r.hands.map(|h| h.len()),
        r.talon,
        r.trump_card
    );
    r.not_played = r.settles_unplayed();
    if !deal.r.not_played {
        deal.play_tricks().await;
    }
    deal.settlement().await;
    let next_deck = deal.r.next_deck(&mut deal.ctx.rng);
    deal.ctx.deck = next_deck;
    let r = &deal.r;
    DealSummary {
        declarer: r.declarer,
        contract: r.contract,
        flek_game: r.flek_game,
        flek_seven: r.flek_seven,
        raises: deal.raised_by,
        not_played: r.not_played,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn amounts_are_signed_from_the_viewers_side() {
        assert_eq!(for_viewer(-4, VIEWER), -4);
        assert_eq!(for_viewer(2, VIEWER), 2);
        assert_eq!(for_viewer(-4, 1), 4);
        assert_eq!(for_viewer(2, 2), -2);
    }
}
