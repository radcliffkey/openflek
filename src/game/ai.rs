//! The computer players, following the original program's logic: hand
//! evaluation, contract and flek decisions, talon discards, per-contract card
//! heuristics and a Monte-Carlo search whose depth and budget grow with IQ.
//!
//! Like the 1992 original, the computer players look at the real cards of
//! everybody (heuristics and simulations are double-dummy).

use super::analysis::{
    Order, betl_danger, count_safe_suits, higher_than, highest, lowest, random_card, run,
    suit_safe, sure_tricks,
};
use super::cards::{Card, CardSet, Rank, Suit};
use super::rng::Rng;
use super::round::{Contract, Player, Round, Situation, next, prev};
use super::settle::settle;

/// Seconds on a monotonic clock; the search deadline uses it.
pub type Clock = fn() -> f64;

/// Playing strength and search budget of the computer players.
#[derive(Clone, Debug)]
pub struct Brain {
    /// 0..=255, as set on the IQ slider.
    pub iq: u8,
    pub clock: Clock,
    nodes: u32,
    deadline: f64,
}

impl Brain {
    pub fn new(iq: u8, clock: Clock) -> Brain {
        Brain {
            iq,
            clock,
            nodes: 0,
            deadline: 0.0,
        }
    }

    /// Plies searched ahead before a real move: 1..=6.
    pub fn depth(&self) -> i32 {
        (self.iq as i32 + 50) / 50
    }

    /// Thinking-time budget per real move, in seconds.
    pub fn time_budget(&self) -> f64 {
        (self.iq as u32 / 100 + 2) as f64
    }

    /// Resets the search budget before a move in the real game.
    pub fn start_move(&mut self, r: &mut Round) {
        r.horizon = (r.trick_no() * 3 + r.table.len()) as i32 - 1 + self.depth();
        self.nodes = 1;
        self.deadline = (self.clock)() + self.time_budget();
    }
}

fn count_suit(set: CardSet, s: Suit) -> usize {
    set.of_suit(s).len() as usize
}

fn pairs(set: CardSet) -> Vec<(Card, Card)> {
    let cards: Vec<Card> = set.iter().collect();
    let mut v = Vec::new();
    for i in 0..cards.len() {
        for j in i + 1..cards.len() {
            v.push((cards[i], cards[j]));
        }
    }
    v
}

/// Union of the candidates sharing the best score; one is picked at random.
fn best_ties(scored: impl IntoIterator<Item = (CardSet, i64)>) -> CardSet {
    let mut best = i64::MIN;
    let mut out = CardSet::EMPTY;
    for (set, v) in scored {
        if v > best {
            best = v;
            out = set;
        } else if v == best {
            out = out.union(set);
        }
    }
    out
}

/// The card whose loss leaves the safest betl hand (the last of equal risks).
fn least_risky(hand: CardSet, played: CardSet, cards: impl Iterator<Item = Card>) -> Option<Card> {
    let mut best = 999;
    let mut result = None;
    for c in cards {
        let v = betl_risk(hand.minus(c.into()), played.union(c.into()), false);
        if v <= best {
            best = v;
            result = Some(c);
        }
    }
    result
}

// ---------------------------------------------------------------- evaluation

/// Per-suit strength of a hand. Mode 0 values trump-game potential, mode 1
/// the hundred; `trump` matters only for mode 1.
pub fn suit_strength(hand: CardSet, mode: u8, trump: Option<Suit>) -> [i32; 4] {
    const BASE: [i32; 8] = [3, 2, 2, 0, 2, 0, 15, 18];
    let mut arr = [0i32; 4];
    for c in hand.iter() {
        let s = c.suit() as usize;
        let v = if mode == 0 {
            match c.rank() {
                Rank::Ten => 11,
                Rank::Over if hand.contains(Card::new(c.suit(), Rank::King)) => 25,
                Rank::Over => 15,
                r => BASE[r as usize],
            }
        } else {
            match c.rank() {
                Rank::Ace => 10,
                Rank::Ten if hand.contains(Card::new(c.suit(), Rank::Ace)) => 10,
                Rank::Ten if count_suit(hand, c.suit()) > 4 => 10,
                Rank::Ten => -10,
                _ if Some(c.suit()) == trump => count_suit(hand, c.suit()) as i32 + 2,
                _ => 2,
            }
        };
        arr[s] += v;
    }
    arr
}

/// Risk of a betl hand (lower is safer); `known` cards are out of play.
pub fn betl_risk(a: CardSet, known: CardSet, flag: bool) -> i32 {
    let k_all = a.union(known);
    let max_rank = a
        .iter()
        .map(|c| c.rank().natural_strength())
        .max()
        .unwrap_or(0);
    let mut risk = 0;
    let mut seen_67 = false;
    for s in Suit::ALL {
        let k = k_all.of_suit(s);
        let n = k.len();
        let card = |r: Rank| Card::new(s, r);
        let others = CardSet::FULL.minus(k);
        let hi_a = highest(a, s, Order::Natural);
        let lo_out = lowest(others, s, Order::Natural);
        let (mut fatal, mut safe) = (false, false);
        match n {
            0 | 8 => safe = true,
            7 => {
                safe = flag;
                seen_67 = true;
                fatal = !k.contains(card(Rank::Seven));
            }
            6 => {
                safe = flag;
                seen_67 = true;
                fatal = !(k.contains(card(Rank::Seven)) && k.contains(card(Rank::Eight)));
            }
            5 => fatal = matches!((hi_a, lo_out), (Some(h), Some(l)) if Order::Natural.beats(h, l)),
            _ => {
                safe = match (hi_a, lo_out) {
                    (None, _) | (_, None) => true,
                    (Some(h), Some(l)) => Order::Natural.beats(l, h),
                };
                fatal = [Rank::Over, Rank::King, Rank::Ace]
                    .iter()
                    .filter(|&&r| a.contains(card(r)))
                    .count()
                    > 1;
            }
        }
        if fatal {
            risk += 32;
        } else if !safe {
            risk += Rank::ALL
                .iter()
                .map(|&r| card(r))
                .filter(|&c| !k_all.contains(c) && c.rank().natural_strength() <= max_rank)
                .count() as i32;
            if !k.contains(card(Rank::Eight)) {
                risk += 1;
            }
            if !k.contains(card(Rank::Seven)) {
                risk += 2;
            }
            if k.contains(card(Rank::King)) {
                risk += 1;
            }
            if k.contains(card(Rank::Ace)) {
                risk += 2;
            }
        }
    }
    if flag && !seen_67 && risk > 0 {
        risk -= 1;
    }
    risk
}

/// Number of outside cards that can beat a durch hand (lower is better).
pub fn durch_losers(hand: CardSet) -> i32 {
    let mut losers = 0;
    for s in Suit::ALL {
        let h = hand.of_suit(s);
        let n = h.len();
        let has = |r: Rank| h.contains(Card::new(s, r));
        let others = CardSet::suit(s).minus(h);
        let ok = match n {
            0 | 8 => true,
            7 => has(Rank::Ace),
            6 => has(Rank::King) && has(Rank::Ace),
            5 => has(Rank::Over) && has(Rank::King) && has(Rank::Ace),
            _ => match (
                lowest(h, s, Order::Natural),
                highest(others, s, Order::Natural),
            ) {
                (Some(lo), Some(hi)) => Order::Natural.beats(lo, hi),
                _ => true,
            },
        };
        if !ok {
            losers += others
                .iter()
                .filter(|&o| h.iter().any(|c| Order::Natural.beats(o, c)))
                .count() as i32;
        }
    }
    losers
}

/// Overall value of a hand for a contract (higher is better).
pub fn hand_value(
    trump_card: Option<Card>,
    hand: CardSet,
    contract: Contract,
    trump: Option<Suit>,
) -> i32 {
    match contract {
        Contract::Hundred | Contract::HundredSeven => suit_strength(hand, 1, trump)
            .iter()
            .map(|&v| if v == 0 { 20 } else { v })
            .sum(),
        Contract::Betl => 32 - betl_risk(hand, CardSet::EMPTY, true),
        Contract::Durch => 32 - durch_losers(hand),
        Contract::Game | Contract::Seven => {
            let arr = suit_strength(hand, 0, trump);
            let trump_value = trump_card.map(|c| arr[c.suit() as usize]).unwrap_or(0);
            arr.iter()
                .map(|&v| if v == 0 { trump_value } else { v })
                .sum()
        }
    }
}

// ----------------------------------------------------------------- bidding

/// The forehand picks the trump card; it may come from the five cards he has
/// not looked at yet ("z lidu").
pub fn choose_trump_card(r: &Round, rng: &mut Rng) -> Card {
    let hand = r.hands[r.forehand];
    let mut arr = suit_strength(r.first_seven, 0, None);
    if arr.iter().all(|&v| v <= 5)
        && let Some(c) = random_card(hand.minus(r.first_seven), rng)
    {
        return c;
    }
    let mut best = 0;
    for s in 0..4 {
        if arr[s] >= arr[best] {
            best = s;
        }
    }
    let top = arr[best];
    for v in arr.iter_mut() {
        if *v <= top / 2 {
            *v = 0;
        }
    }
    let total: i32 = arr.iter().sum();
    let mut x = rng.below(total.max(1) as u32) as i32;
    let mut s = 0;
    while s < 3 && arr[s] <= x {
        x -= arr[s];
        s += 1;
    }
    let suit = Suit::from_index(s as u8);
    let qk = CardSet::rank(Rank::Over).union(CardSet::rank(Rank::King));
    let sevens = CardSet::rank(Rank::Seven);
    [
        hand.minus(CardSet::SHARP).minus(qk).minus(sevens),
        hand.minus(CardSet::SHARP).minus(sevens),
        hand.minus(CardSet::SHARP),
        hand.minus(CardSet::TENS),
        hand,
    ]
    .iter()
    .find_map(|&set| lowest(set, suit, Order::Mariage))
    .unwrap_or_else(|| hand.iter().next().expect("forehand holds cards"))
}

/// While bidding is open, a defender's hand includes the talon he could take over.
fn full_hand(r: &Round, p: Player) -> CardSet {
    let h = r.hands[p];
    if r.bidding && p != r.declarer {
        h.union(r.talon_set())
    } else {
        h
    }
}

pub fn wants_durch(r: &Round, p: Player) -> bool {
    let h = full_hand(r, p);
    let safe = count_safe_suits(h, CardSet::EMPTY, Order::Natural, None);
    let sure = sure_tricks(h, CardSet::EMPTY, Order::Natural, None);
    match safe {
        0 | 1 => false,
        2 => sure >= 9,
        3 => {
            if sure <= 6 {
                return false;
            }
            if sure >= 9 {
                return true;
            }
            let mut res = false;
            for s in Suit::ALL {
                if suit_safe(s, h, CardSet::FULL.minus(h), Order::Natural, None) {
                    continue;
                }
                let has = |r: Rank| h.contains(Card::new(s, r));
                match count_suit(h, s) {
                    6 | 7 => res = has(Rank::Ace),
                    5 => res = has(Rank::Ace) && has(Rank::King),
                    _ => {}
                }
            }
            res
        }
        _ => true,
    }
}

pub fn wants_betl(r: &Round, p: Player, rng: &mut Rng) -> bool {
    let h = r.hands[p];
    let mut best = betl_risk(h, CardSet::EMPTY, true);
    if h.len() == 12 {
        for (a, b) in pairs(h) {
            best = best.min(betl_risk(
                h.minus(CardSet::of(&[a, b])),
                CardSet::of(&[a, b]),
                true,
            ));
        }
    }
    match best {
        0..=2 => true,
        3..=7 => rng.below(best as u32) <= 2,
        _ => false,
    }
}

pub fn wants_seven(r: &Round, p: Player, iq: u8) -> bool {
    let h = r.hands[p];
    let Some(t7) = r.trump_card_of(Rank::Seven) else {
        return false;
    };
    if iq == 0 || !h.contains(t7) {
        return false;
    }
    let t = r.trump.map(|s| count_suit(h, s)).unwrap_or(0);
    let v = || hand_value(r.trump_card, h, Contract::Hundred, r.trump);
    match t {
        6.. => true,
        5 => v() > 50,
        4 => v() > 70,
        _ => false,
    }
}

pub fn wants_hundred(r: &Round, p: Player, iq: u8) -> bool {
    let h = r.hands[p];
    let (Some(q), Some(k)) = (r.trump_card_of(Rank::Over), r.trump_card_of(Rank::King)) else {
        return false;
    };
    if iq < 20 || !h.contains(q) || !h.contains(k) {
        return false;
    }
    let v = if h.len() <= 10 {
        hand_value(r.trump_card, h, Contract::Hundred, r.trump)
    } else {
        pairs(h.minus(CardSet::SHARP).minus(CardSet::of(&[q, k])))
            .into_iter()
            .map(|(a, b)| {
                hand_value(
                    r.trump_card,
                    h.minus(CardSet::of(&[a, b])),
                    Contract::Hundred,
                    r.trump,
                )
            })
            .max()
            .unwrap_or(-9999)
    };
    v > 90
}

/// The computer forehand's contract.
pub fn forehand_contract(r: &Round, rng: &mut Rng, iq: u8) -> Contract {
    let p = r.forehand;
    if wants_durch(r, p) {
        Contract::Durch
    } else if wants_betl(r, p, rng) {
        Contract::Betl
    } else {
        match (wants_hundred(r, p, iq), wants_seven(r, p, iq)) {
            (true, true) => Contract::HundredSeven,
            (true, false) => Contract::Hundred,
            (false, true) => Contract::Seven,
            (false, false) => Contract::Game,
        }
    }
}

/// Picks the two talon cards for the declarer.
pub fn choose_discard(r: &Round, rng: &mut Rng) -> [Card; 2] {
    let d = r.declarer;
    let mut cand = r.discardable(d);
    let hand = cand;
    let trumps = r.trump.map(CardSet::suit).unwrap_or(CardSet::EMPTY);
    let eval = |rest: CardSet, gone: CardSet, cards: CardSet| -> i64 {
        let mut v = match r.contract {
            Contract::Durch => sure_tricks(rest, gone, Order::Natural, None) as i32,
            Contract::Betl => {
                let (_, danger) = betl_danger(rest, gone);
                -(danger.len() as i32) * (danger.len() as i32)
            }
            c => hand_value(r.trump_card, rest, c, r.trump),
        };
        v -= 10 * cards.intersect(trumps).len() as i32;
        v as i64
    };
    let mut first_cand = cand;
    if r.contract.has_hundred() {
        first_cand = first_cand.minus(r.marriages.intersect(trumps));
    }
    let list = best_ties(pairs(first_cand).into_iter().map(|(a, b)| {
        let ps = CardSet::of(&[a, b]);
        (ps, eval(hand.minus(ps), ps, ps))
    }));
    let first = random_card(list, rng)
        .or_else(|| random_card(cand, rng))
        .expect("declarer has cards to discard");
    cand.remove(first);
    let rest = hand.minus(first.into());
    let list = best_ties(cand.iter().map(|c| {
        let single = CardSet::from(c);
        (
            single,
            eval(rest.minus(single), CardSet::of(&[c, first]), single),
        )
    }));
    let second = random_card(list, rng)
        .or_else(|| random_card(cand, rng))
        .expect("declarer has a second card to discard");
    [first, second]
}

/// Average money result for `p` over 13 simulated play-outs of the deal.
pub fn simulated_ev(r: &Round, p: Player, rng: &mut Rng, brain: &mut Brain) -> bool {
    let mut sum = 0i64;
    for _ in 0..13 {
        let mut sim = r.clone();
        sim.start_play();
        sim.real = false;
        sim.horizon = 0;
        play_out(&mut sim, rng, brain);
        sum += settle(&sim).ai_value(p, sim.declarer);
    }
    sum / 13 > 0
}

/// A defender's wish to double: (on the game, on the seven).
pub fn defender_flek(r: &Round, p: Player, rng: &mut Rng, brain: &mut Brain) -> (bool, bool) {
    let h = r.hands[p];
    let mut wish = match r.contract {
        Contract::Durch => {
            let strong = count_safe_suits(h, CardSet::EMPTY, Order::Natural, None) > 2
                || h.intersect(CardSet::ACES).len() >= 2;
            (strong && simulated_ev(r, p, rng, brain), false)
        }
        Contract::Betl => (simulated_ev(r, p, rng, brain), false),
        _ => flek_wish(r, p, rng, brain),
    };
    // "Moudřejší ustoupí": the wiser one gives in after many doubles.
    if rng.below(r.flek_game) > 2
        || r.flek_game > 8
        || r.flek_seven > 8
        || (r.contract.no_trumps() && r.flek_game > 2)
    {
        wish = (false, false);
    }
    wish
}

fn flek_wish(r: &Round, p: Player, rng: &mut Rng, brain: &mut Brain) -> (bool, bool) {
    let h = r.hands[p];
    let o = h.intersect(CardSet::SHARP).len();
    let t = r.trump.map(|s| count_suit(h, s)).unwrap_or(0);
    let t7 = r.trump_card_of(Rank::Seven);
    let holds_t7 = t7.is_some_and(|c| h.contains(c));
    let seven = if r.contract.has_seven() {
        (r.flek_seven < 1 && ((o > 2 && t >= 3) || (o > 1 && t >= 4))) || holds_t7
    } else {
        t > 4 && o > 3 && holds_t7
    };
    let qk = [r.trump_card_of(Rank::Over), r.trump_card_of(Rank::King)];
    let mut game = qk.iter().flatten().any(|&c| h.contains(c))
        && r.contract < Contract::Hundred
        && r.flek_game < 2;
    if !game && t > r.contract as usize && simulated_ev(r, p, rng, brain) {
        game = true;
    }
    (game, seven)
}

/// The declarer's answer to doubles raised in this step: (re on the game, re on the seven).
pub fn declarer_re(r: &Round, game_raised: bool, rng: &mut Rng, brain: &mut Brain) -> (bool, bool) {
    let d = r.declarer;
    let game = match r.contract {
        Contract::Durch => sure_tricks(r.hands[d], r.talon_set(), Order::Natural, None) >= 10,
        Contract::Betl => false,
        _ => game_raised && simulated_ev(r, d, rng, brain),
    };
    (game && r.flek_game < 8, false)
}

// --------------------------------------------------------------- card play

/// Working state of one card decision.
struct Choice<'a> {
    r: &'a Round,
    me: Player,
    cand: CardSet,
    result: Option<Card>,
}

impl Choice<'_> {
    fn exclude(&mut self, s: CardSet) {
        let hit = self.cand.intersect(s);
        if hit.is_empty() || hit == self.cand {
            return;
        }
        self.cand = self.cand.minus(s);
    }

    fn low_or_random(&mut self, k: usize, rng: &mut Rng) {
        if rng.below(10) > 1 {
            if let Some(&c) = self.r.table.get(k - 1) {
                self.result = lowest(self.cand, c.suit(), Order::Mariage);
            }
        } else {
            self.result = random_card(self.cand, rng);
        }
    }

    fn hand(&self, p: Player) -> CardSet {
        self.r.hands[p]
    }
}

fn is_safe_winner(r: &Round, me: Player, c: Card) -> bool {
    let (n, p) = (next(me), prev(me));
    let others = r.hands[n].union(r.hands[p]);
    let trumps = r.trump_cards();
    let higher = higher_than(c, Order::Mariage);
    if trumps.contains(c) {
        return others.intersect(higher).is_empty();
    }
    let ruffs = |x: Player| {
        r.hands[x].of_suit(c.suit()).is_empty() && !r.hands[x].intersect(trumps).is_empty()
    };
    others.intersect(higher).is_empty() && !ruffs(n) && !ruffs(p)
}

fn normal_heuristic(ch: &mut Choice, sit: Situation, rng: &mut Rng) {
    use Situation::*;
    let r = ch.r;
    let me = ch.me;
    let d = r.declarer;
    let (n, p) = (next(me), prev(me));
    let trumps = r.trump_cards();
    let ost = CardSet::SHARP;
    let card1 = r.table.first().copied();
    let ls = card1.map(|c| c.suit());
    let suit_of = |set: CardSet| ls.map(|s| set.of_suit(s)).unwrap_or(CardSet::EMPTY);
    match sit {
        Lead => {
            let order_list = Suit::ALL.map(|s| [Card::new(s, Rank::Ace), Card::new(s, Rank::Ten)]);
            for c in order_list.into_iter().flatten() {
                if ch.cand.contains(c) && Some(c.suit()) != r.trump && is_safe_winner(r, me, c) {
                    ch.result = Some(c);
                    return;
                }
            }
            ch.exclude(CardSet::TENS);
        }
        SecondBeat => {
            if n == d {
                let dh = ch.hand(d);
                if !suit_of(dh).intersect(CardSet::ACES).is_empty()
                    || (suit_of(dh).is_empty() && !dh.intersect(trumps).is_empty())
                {
                    ch.exclude(ost);
                }
            } else if p == d
                && suit_of(ch.hand(d)).is_empty()
                && !suit_of(ch.cand).intersect(ost).is_empty()
            {
                ch.result = random_card(suit_of(ch.cand).intersect(ost), rng);
            } else if ch.cand.intersect(ost).is_empty() {
                ch.low_or_random(1, rng);
            }
        }
        SecondFollow => {
            if p == d
                && card1.is_some_and(|c| CardSet::ACES.contains(c))
                && !suit_of(ch.hand(n)).is_empty()
            {
                ch.exclude(CardSet::TENS);
            }
            if ch.cand.intersect(ost).is_empty() {
                ch.low_or_random(1, rng);
            }
        }
        SecondTrump => {
            let dh = ch.hand(d);
            if n == d
                && suit_of(dh).is_empty()
                && !dh.intersect(trumps).intersect(CardSet::ACES).is_empty()
            {
                ch.exclude(ost);
            }
            if ch.cand.intersect(ost).is_empty() {
                ch.low_or_random(1, rng);
            }
        }
        SecondDiscard => {
            if ch.cand.intersect(ost).is_empty() {
                return;
            }
            if me == d {
                ch.exclude(ost);
                return;
            }
            let higher0 = card1
                .map(|c| higher_than(c, Order::Mariage))
                .unwrap_or(CardSet::EMPTY);
            let is_trump_suit = ls.is_some() && ls == r.trump;
            if p == d {
                let nh = ch.hand(n);
                if !suit_of(nh).is_empty() {
                    if suit_of(nh).intersect(higher0).is_empty() {
                        ch.exclude(ost);
                    }
                } else if !is_trump_suit && nh.intersect(trumps).is_empty() {
                    ch.exclude(ost);
                }
            } else {
                let dh = ch.hand(d);
                let declarer_wins = !suit_of(dh).intersect(higher0).is_empty();
                let declarer_stuck =
                    suit_of(dh).is_empty() && !is_trump_suit && dh.intersect(trumps).is_empty();
                if declarer_wins || declarer_stuck {
                    ch.exclude(ost);
                }
            }
        }
        ThirdBeatBoth => {
            if n == d
                && suit_of(ch.hand(d)).is_empty()
                && !suit_of(ch.cand).intersect(ost).is_empty()
            {
                ch.result = random_card(suit_of(ch.cand).intersect(ost), rng);
                return;
            }
            if ch.cand.intersect(ost.union(trumps)).is_empty() {
                ch.low_or_random(1, rng);
            }
        }
        ThirdFollow => {
            if ch.cand.intersect(ost.union(trumps)).is_empty() {
                ch.low_or_random(1, rng);
                return;
            }
            let card2 = r.table[1];
            let a1 = card1.is_some_and(|c| CardSet::ACES.contains(c));
            if !ch.cand.intersect(CardSet::TENS).is_empty()
                && ((a1 && p != d) || (CardSet::ACES.contains(card2) && n != d))
            {
                ch.exclude(CardSet::TENS);
            }
        }
        ThirdFollowAfterTrump => {
            if ch.cand.intersect(ost.union(trumps)).is_empty() {
                ch.low_or_random(1, rng);
                return;
            }
            if n != d {
                ch.exclude(ost);
                ch.low_or_random(1, rng);
            } else if !ch.cand.intersect(ost).is_empty() {
                ch.result = random_card(ch.cand.intersect(ost), rng);
            }
        }
        ThirdBeatAfterDiscard | ThirdTrumpIn => {}
        ThirdFollowAfterDiscard => {
            if ch.cand.intersect(ost.union(trumps)).is_empty() {
                ch.low_or_random(1, rng);
                return;
            }
            if p != d {
                ch.exclude(ost);
                ch.low_or_random(2, rng);
            } else if !ch.cand.intersect(CardSet::TENS).is_empty() {
                ch.result = random_card(ch.cand.intersect(CardSet::TENS), rng);
            }
        }
        ThirdDiscard => {
            if r.current_winner() == d {
                ch.exclude(ost);
            } else if !ch.cand.intersect(ost).is_empty() {
                ch.cand = ch.cand.intersect(ost);
            }
        }
        ThirdOvertrump => {
            if ch.cand.intersect(ost).is_empty() {
                ch.low_or_random(2, rng);
            }
        }
        ThirdUndertrump => {
            if n != d {
                ch.exclude(ost);
                ch.low_or_random(2, rng);
            } else if ch.cand.intersect(ost).is_empty() {
                ch.low_or_random(2, rng);
            }
        }
    }
}

fn betl_discard(ch: &mut Choice, rng: &mut Rng) {
    let r = ch.r;
    let hand = ch.hand(ch.me);
    let (_, danger) = betl_danger(hand, r.played);
    let pool = danger.intersect(ch.cand);
    if pool.is_empty() {
        ch.result = random_card(ch.cand, rng);
        return;
    }
    // Rank-major order: lower ranks are tried first.
    let by_rank = Rank::ALL
        .into_iter()
        .flat_map(|rank| Suit::ALL.map(|s| Card::new(s, rank)));
    ch.result = least_risky(hand, r.played, by_rank.filter(|&c| pool.contains(c)));
}

fn betl_heuristic(ch: &mut Choice, sit: Situation, rng: &mut Rng, iq: u8) {
    use Situation::*;
    let r = ch.r;
    let me = ch.me;
    let d = r.declarer;
    let (n, p) = (next(me), prev(me));
    match sit {
        Lead if me == d => {
            let counts = Suit::ALL.map(|s| count_suit(ch.cand, s));
            let max = *counts.iter().max().unwrap_or(&0);
            let s = Suit::from_index(counts.iter().position(|&c| c == max).unwrap_or(0) as u8);
            let has = |rank: Rank| ch.cand.contains(Card::new(s, rank));
            let drop_suit = |ch: &mut Choice| {
                let rest = ch.cand.minus(CardSet::suit(s));
                if !rest.is_empty() {
                    ch.cand = rest;
                }
            };
            match max {
                8 => drop_suit(ch),
                7 if !has(Rank::Ace) => drop_suit(ch),
                7 => ch.result = lowest(ch.cand, s, Order::Natural),
                6 if !has(Rank::King) && !has(Rank::Ace) => drop_suit(ch),
                6 => ch.result = lowest(ch.cand, s, Order::Natural),
                _ => {
                    let hand = ch.hand(me);
                    let (_, danger) = betl_danger(hand, r.played);
                    let pool = danger.intersect(ch.cand);
                    if pool.is_empty() {
                        ch.result = random_card(ch.cand, rng);
                        return;
                    }
                    let unknown = CardSet::FULL.minus(hand).minus(r.played);
                    let catchable = |c: &Card| {
                        !unknown
                            .intersect(higher_than(*c, Order::Natural))
                            .is_empty()
                    };
                    ch.result = least_risky(hand, r.played, pool.iter().filter(catchable));
                }
            }
        }
        Lead => {
            let (dh, partner) = if n == d {
                (ch.hand(n), ch.hand(p))
            } else {
                (ch.hand(p), ch.hand(n))
            };
            let catch: CardSet = ch
                .cand
                .iter()
                .filter(|&c| {
                    !dh.intersect(higher_than(c, Order::Natural)).is_empty()
                        && partner.of_suit(c.suit()).is_empty()
                })
                .collect();
            if !catch.is_empty() && (!r.real || rng.below(100) < iq as u32) {
                ch.result = random_card(catch, rng);
            }
        }
        SecondDiscard => {
            if me == d {
                betl_discard(ch, rng);
            } else if r.trick_no() == 1 {
                ch.result = random_card(ch.cand, rng);
            }
        }
        ThirdDiscard => {
            if me == d {
                betl_discard(ch, rng);
            } else if r.current_winner() == d {
                ch.result = random_card(ch.cand, rng);
            }
        }
        SecondFollow
        | ThirdBeatBoth
        | ThirdFollow
        | ThirdBeatAfterDiscard
        | ThirdFollowAfterDiscard => {
            if let Some(c) = r.table.first() {
                ch.result = highest(ch.cand, c.suit(), Order::Natural);
            }
        }
        _ => {}
    }
}

fn durch_heuristic(ch: &mut Choice, sit: Situation, rng: &mut Rng) {
    use Situation::*;
    let r = ch.r;
    let unplayed = CardSet::FULL.minus(r.played);
    // The suits in random order: each draw takes one of the remaining suits.
    let random_suits = |rng: &mut Rng| {
        let (mut rest, mut out) = (Suit::ALL, Suit::ALL);
        for (k, slot) in out.iter_mut().enumerate() {
            let n = 4 - k;
            let i = rng.below(n as u32) as usize;
            *slot = rest[i];
            rest.copy_within(i + 1..n, i);
        }
        out
    };
    match sit {
        Lead => {
            for s in random_suits(rng) {
                if count_suit(ch.cand, s) == 0 {
                    continue;
                }
                let rest = CardSet::FULL.minus(ch.cand).minus(r.played);
                if suit_safe(s, ch.cand, rest, Order::Natural, None) {
                    ch.result = highest(ch.cand, s, Order::Natural);
                    return;
                }
                // The top card of the run down from the ace, played cards bridging gaps.
                if let Some(c) = run(s, Rank::ALL.iter().rev(), ch.cand, r.played).next() {
                    ch.result = Some(c);
                    return;
                }
            }
        }
        SecondBeat | ThirdBeatBoth | ThirdBeatAfterDiscard => ch.result = random_card(ch.cand, rng),
        SecondFollow | ThirdFollow | ThirdFollowAfterDiscard => {
            if let Some(c) = r.table.first() {
                ch.result = lowest(ch.cand, c.suit(), Order::Natural);
            }
        }
        SecondDiscard | ThirdDiscard => {
            for s in random_suits(rng) {
                if count_suit(ch.cand, s) == 0 {
                    continue;
                }
                if suit_safe(s, unplayed, ch.cand, Order::Natural, None) {
                    ch.result = lowest(ch.cand, s, Order::Natural);
                } else if let Some(c) = lowest(ch.cand, s, Order::Natural)
                    && !suit_safe(
                        s,
                        unplayed,
                        ch.cand.minus(CardSet::from(c)),
                        Order::Natural,
                        None,
                    )
                {
                    ch.result = Some(c);
                }
                if ch.result.is_some() {
                    return;
                }
            }
        }
        _ => {}
    }
}

/// Splits the candidates into groups of equivalent cards for the search.
/// `None` means searching is pointless.
fn groups(r: &Round, cand: CardSet, me: Player) -> Option<Vec<CardSet>> {
    let threats = |p: Player| r.threats[p].minus(r.played);
    let victims = |p: Player| r.victims[p].minus(r.played);
    if (0..3).any(|p| threats(p).is_empty()) {
        return None;
    }
    let t7 = r.trump_seven();
    if victims(me).is_empty() || threats(me).is_empty() {
        return match t7 {
            Some(c) if r.seven_announced && cand.contains(c) && cand.len() > 1 => {
                Some(vec![CardSet::from(c), cand.minus(CardSet::from(c))])
            }
            _ => Some(Vec::new()),
        };
    }
    let order = r.order();
    let mut out = Vec::new();
    for s in Suit::ALL {
        let mut cards = cand.of_suit(s);
        if order == Order::Mariage {
            let sharp_cards = cards.intersect(CardSet::SHARP);
            if !sharp_cards.is_empty() {
                out.push(sharp_cards);
                cards = cards.minus(sharp_cards);
            }
            if let Some(c) = t7.filter(|c| cards.contains(*c)) {
                out.push(CardSet::from(c));
                cards.remove(c);
            }
        }
        let ranks = order.ranks();
        while let Some(start) = cards.first() {
            let i = ranks.iter().position(|&rk| rk == start.rank()).unwrap_or(0);
            let group: CardSet = run(s, ranks[i + 1..].iter(), cards, r.played)
                .chain([start])
                .collect();
            cards = cards.minus(group);
            out.push(group);
        }
    }
    Some(out)
}

fn search(
    r: &Round,
    me: Player,
    groups: &[CardSet],
    rng: &mut Rng,
    brain: &mut Brain,
) -> Option<Card> {
    let mut scored = Vec::with_capacity(groups.len());
    for &g in groups {
        let card = random_card(g, rng)?;
        let mut sim = r.clone();
        sim.real = false;
        sim.play(card);
        if brain.nodes.is_multiple_of(16)
            && (brain.nodes > 2 * brain.iq as u32 || (brain.clock)() > brain.deadline)
        {
            sim.horizon = 0;
        }
        play_out(&mut sim, rng, brain);
        brain.nodes += 1;
        scored.push((g, settle(&sim).ai_value(me, sim.declarer)));
    }
    random_card(best_ties(scored), rng)
}

/// Chooses the card for the computer player on turn.
pub fn choose_card(r: &Round, rng: &mut Rng, brain: &mut Brain) -> Card {
    let me = r.to_play();
    let allowed = r.legal(me);
    let mut ch = Choice {
        r,
        me,
        cand: allowed,
        result: None,
    };
    if allowed.len() == 1 {
        return allowed.first().expect("one legal card");
    }
    let sit = r.classify(me).0;
    match r.contract {
        Contract::Betl => betl_heuristic(&mut ch, sit, rng, brain.iq),
        Contract::Durch => durch_heuristic(&mut ch, sit, rng),
        _ => normal_heuristic(&mut ch, sit, rng),
    }
    if ch.result.is_none() {
        let ply = (r.trick_no() * 3 + r.table.len()) as i32;
        let gate = brain.iq > 0 && (ply < r.horizon || r.trick_no() > 8);
        match groups(r, ch.cand, me) {
            Some(g) if g.len() > 1 && gate => ch.result = search(r, me, &g, rng, brain),
            _ => {}
        }
    }
    ch.result
        .filter(|c| allowed.contains(*c))
        .or_else(|| random_card(ch.cand, rng))
        .expect("player on turn has a legal card")
}

/// Plays the rest of the deal with computer players in every seat.
pub fn play_out(r: &mut Round, rng: &mut Rng, brain: &mut Brain) {
    while !r.is_over() {
        let c = choose_card(r, rng, brain);
        r.play(c);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::round::Deck;

    fn clock() -> f64 {
        0.0
    }

    fn set(cards: &[(Suit, Rank)]) -> CardSet {
        cards.iter().map(|&(s, r)| Card::new(s, r)).collect()
    }

    #[test]
    fn durch_losers_and_betl_risk_rank_hands() {
        let perfect = CardSet::suit(Suit::Hearts).union(set(&[
            (Suit::Acorns, Rank::Ace),
            (Suit::Acorns, Rank::King),
        ]));
        assert_eq!(durch_losers(perfect), 0);
        let low: CardSet = Suit::ALL
            .iter()
            .flat_map(|&s| [Card::new(s, Rank::Seven), Card::new(s, Rank::Eight)])
            .chain([
                Card::new(Suit::Hearts, Rank::Nine),
                Card::new(Suit::Acorns, Rank::Nine),
            ])
            .collect();
        let high: CardSet = Suit::ALL
            .iter()
            .flat_map(|&s| [Card::new(s, Rank::King), Card::new(s, Rank::Ace)])
            .collect();
        assert!(betl_risk(low, CardSet::EMPTY, true) < betl_risk(high, CardSet::EMPTY, true));
    }

    #[test]
    fn computer_deals_play_to_a_legal_finish() {
        for seed in 0..20 {
            let mut rng = Rng::new(seed);
            let mut brain = Brain::new(60, clock);
            let mut deck = Deck::fresh(&mut rng);
            let mut r = Round::deal(&mut deck, (seed % 3) as usize, &mut rng);
            r.real = false;
            let tc = choose_trump_card(&r, &mut rng);
            r.choose_trump(tc);
            r.compute_marriages();
            let contract = forehand_contract(&r, &mut rng, brain.iq);
            r.declare(contract);
            let talon = choose_discard(&r, &mut rng);
            r.discard(talon);
            r.finish_bidding();
            assert!(!r.trump_card_aside && !r.bidding);
            r.start_play();
            for p in 0..3 {
                assert_eq!(r.hands[p].len(), 10, "seed {seed} player {p}");
            }
            while !r.is_over() {
                let p = r.to_play();
                let c = choose_card(&r, &mut rng, &mut brain);
                assert!(r.legal(p).contains(c), "seed {seed}: illegal {c:?}");
                r.play(c);
            }
            let s = settle(&r);
            assert_eq!((0..3).map(|p| s.net(p, r.declarer)).sum::<i64>(), 0);
        }
    }

    #[test]
    fn discard_never_drops_tens_or_aces_in_suit_games() {
        let mut rng = Rng::new(11);
        let mut deck = Deck::fresh(&mut rng);
        let mut r = Round::deal(&mut deck, 0, &mut rng);
        let tc = choose_trump_card(&r, &mut rng);
        r.choose_trump(tc);
        r.contract = Contract::Game;
        let talon = choose_discard(&r, &mut rng);
        assert!(talon.iter().all(|c| !c.rank().is_sharp()));
        assert_ne!(talon[0], talon[1]);
    }
}
