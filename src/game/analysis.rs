//! Card-set analysis shared by the rules and the computer players:
//! rank orders, highest/lowest cards, safe suits, sure tricks and betl danger.

use super::cards::{Card, CardSet, Rank, Suit};
use super::rng::Rng;

/// Which rank order applies: suit games (10 above K) or natural (betl, durch).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Order {
    Mariage,
    Natural,
}

const MARIAGE_RANKS: [Rank; 8] = [
    Rank::Seven,
    Rank::Eight,
    Rank::Nine,
    Rank::Under,
    Rank::Over,
    Rank::King,
    Rank::Ten,
    Rank::Ace,
];

/// Per order and rank index: rank bits of the same suit that beat it.
const HIGHER: [[u8; 8]; 2] = {
    let mut t = [[0u8; 8]; 2];
    let mut r = 0;
    while r < 8 {
        let mut o = 0;
        while o < 8 {
            if Rank::ALL[o].strength() > Rank::ALL[r].strength() {
                t[0][r] |= 1 << o;
            }
            if o > r {
                t[1][r] |= 1 << o;
            }
            o += 1;
        }
        r += 1;
    }
    t
};

impl Order {
    pub fn value(self, card: Card) -> u8 {
        match self {
            Order::Mariage => card.rank().strength(),
            Order::Natural => card.rank().natural_strength(),
        }
    }

    /// Ranks from lowest to highest.
    pub fn ranks(self) -> &'static [Rank; 8] {
        match self {
            Order::Mariage => &MARIAGE_RANKS,
            Order::Natural => &Rank::ALL,
        }
    }

    pub fn beats(self, a: Card, b: Card) -> bool {
        self.value(a) > self.value(b)
    }
}

/// Cards of `suit` in `set`, lowest first.
pub fn ascending(set: CardSet, suit: Suit, order: Order) -> impl DoubleEndedIterator<Item = Card> {
    order
        .ranks()
        .iter()
        .map(move |&r| Card::new(suit, r))
        .filter(move |&c| set.contains(c))
}

pub fn lowest(set: CardSet, suit: Suit, order: Order) -> Option<Card> {
    ascending(set, suit, order).next()
}

pub fn highest(set: CardSet, suit: Suit, order: Order) -> Option<Card> {
    ascending(set, suit, order).next_back()
}

/// Cards of the same suit that rank above `card`.
pub fn higher_than(card: Card, order: Order) -> CardSet {
    let table = &HIGHER[order as usize];
    CardSet::from_suit_bits(card.suit(), table[card.rank().index() as usize])
}

/// A uniformly random member of `set`.
pub fn random_card(set: CardSet, rng: &mut Rng) -> Option<Card> {
    if set.is_empty() {
        return None;
    }
    set.iter().nth(rng.below(set.len()) as usize)
}

/// `mine`'s cards in the unbroken run along `ranks` of `suit`: cards in
/// `gone` are skipped, the first card in neither set ends the run.
pub fn run<'a>(
    suit: Suit,
    ranks: impl Iterator<Item = &'a Rank>,
    mine: CardSet,
    gone: CardSet,
) -> impl Iterator<Item = Card> {
    ranks
        .map(move |&r| Card::new(suit, r))
        .take_while(move |&c| mine.contains(c) || gone.contains(c))
        .filter(move |&c| mine.contains(c))
}

/// Whether `a` controls `suit` against `b`: a's top cards beat b's highest card
/// at least as many times as b holds cards there. Running out of cards first
/// is fine except in the trump suit.
pub fn suit_safe(suit: Suit, a: CardSet, b: CardSet, order: Order, trump: Option<Suit>) -> bool {
    let Some(their_top) = highest(b, suit, order) else {
        return true;
    };
    let mut mine = ascending(a, suit, order).rev();
    for _ in 0..b.of_suit(suit).len() {
        match mine.next() {
            None => return Some(suit) != trump,
            Some(c) if order.beats(their_top, c) => return false,
            Some(_) => {}
        }
    }
    true
}

pub fn all_suits_safe(a: CardSet, b: CardSet, order: Order, trump: Option<Suit>) -> bool {
    Suit::ALL.iter().all(|&s| suit_safe(s, a, b, order, trump))
}

/// Number of suits `a` controls against all cards neither in `a` nor `known`.
pub fn count_safe_suits(a: CardSet, known: CardSet, order: Order, trump: Option<Suit>) -> usize {
    let rest = CardSet::FULL.minus(a).minus(known);
    Suit::ALL
        .iter()
        .filter(|&&s| suit_safe(s, a, rest, order, trump))
        .count()
}

/// Tricks `a` takes for sure in `suit`; `known` are cards already gone.
pub fn sure_tricks_suit(
    suit: Suit,
    a: CardSet,
    known: CardSet,
    order: Order,
    trump: Option<Suit>,
) -> usize {
    let rest = CardSet::FULL.minus(a).minus(known);
    if suit_safe(suit, a, rest, order, trump) {
        return a.of_suit(suit).len() as usize;
    }
    run(suit, order.ranks().iter().rev(), a, known).count()
}

pub fn sure_tricks(a: CardSet, known: CardSet, order: Order, trump: Option<Suit>) -> usize {
    Suit::ALL
        .iter()
        .map(|&s| sure_tricks_suit(s, a, known, order, trump))
        .sum()
}

/// Number of `a`'s cards in the unbroken run from the seven upwards through `a ∪ known`.
pub fn low_run(suit: Suit, a: CardSet, known: CardSet) -> usize {
    run(suit, Rank::ALL.iter(), a, known).count()
}

/// In betl, `a` can never be forced to take a trick in `suit`.
pub fn betl_suit_safe(suit: Suit, a: CardSet, known: CardSet) -> bool {
    a.of_suit(suit).len() as usize <= low_run(suit, a, known)
}

pub fn betl_safe_suits(a: CardSet, known: CardSet) -> usize {
    Suit::ALL
        .iter()
        .filter(|&&s| betl_suit_safe(s, a, known))
        .count()
}

/// Holes below `a`'s highest card in `suit` that leave it exposed in betl;
/// the exposed cards of `a` are added to `out`.
pub fn betl_danger_suit(suit: Suit, a: CardSet, known: CardSet, out: &mut CardSet) -> usize {
    let k = a.union(known);
    let Some(top) = highest(a, suit, Order::Natural) else {
        return 0;
    };
    let below_top = &Rank::ALL[..=top.rank().index() as usize];
    // Cards in the unbroken bottom run are safe; look above it.
    let safe = below_top
        .iter()
        .take_while(|&&r| k.contains(Card::new(suit, r)))
        .count();
    let mut holes = 0;
    for &r in &below_top[safe..] {
        let c = Card::new(suit, r);
        if !k.contains(c) {
            holes += 1;
        } else if a.contains(c) {
            out.insert(c);
        }
    }
    holes
}

pub fn betl_danger(a: CardSet, known: CardSet) -> (usize, CardSet) {
    let mut out = CardSet::EMPTY;
    let n = Suit::ALL
        .iter()
        .map(|&s| betl_danger_suit(s, a, known, &mut out))
        .sum();
    (n, out)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn set(cards: &[(Suit, Rank)]) -> CardSet {
        cards.iter().map(|&(s, r)| Card::new(s, r)).collect()
    }

    #[test]
    fn higher_table_matches_rank_strengths() {
        for id in 0..32 {
            let c = Card::from_id(id);
            for order in [Order::Mariage, Order::Natural] {
                let slow: CardSet = Rank::ALL
                    .iter()
                    .map(|&r| Card::new(c.suit(), r))
                    .filter(|&o| order.beats(o, c))
                    .collect();
                assert_eq!(higher_than(c, order), slow, "{c:?} {order:?}");
            }
        }
    }

    #[test]
    fn random_card_picks_members_only() {
        let mut rng = Rng::new(3);
        let s = set(&[(Suit::Bells, Rank::Nine), (Suit::Hearts, Rank::Ace)]);
        for _ in 0..20 {
            assert!(s.contains(random_card(s, &mut rng).unwrap()));
        }
        assert_eq!(random_card(CardSet::EMPTY, &mut rng), None);
    }

    #[test]
    fn orders_place_ten_differently() {
        assert_eq!(Order::Mariage.ranks()[6], Rank::Ten);
        assert_eq!(Order::Natural.ranks()[3], Rank::Ten);
        let (ten, king) = (
            Card::new(Suit::Hearts, Rank::Ten),
            Card::new(Suit::Hearts, Rank::King),
        );
        assert!(Order::Mariage.beats(ten, king));
        assert!(!Order::Natural.beats(ten, king));
    }

    #[test]
    fn highest_lowest_and_higher_than() {
        let s = set(&[
            (Suit::Bells, Rank::Ten),
            (Suit::Bells, Rank::King),
            (Suit::Bells, Rank::Seven),
        ]);
        assert_eq!(
            highest(s, Suit::Bells, Order::Mariage),
            Some(Card::new(Suit::Bells, Rank::Ten))
        );
        assert_eq!(
            highest(s, Suit::Bells, Order::Natural),
            Some(Card::new(Suit::Bells, Rank::King))
        );
        assert_eq!(
            lowest(s, Suit::Bells, Order::Natural),
            Some(Card::new(Suit::Bells, Rank::Seven))
        );
        assert_eq!(highest(s, Suit::Hearts, Order::Natural), None);
        assert_eq!(
            higher_than(Card::new(Suit::Bells, Rank::King), Order::Mariage).len(),
            2
        );
    }

    #[test]
    fn suit_safety() {
        let a = set(&[(Suit::Acorns, Rank::Ace), (Suit::Acorns, Rank::Ten)]);
        let b = set(&[(Suit::Acorns, Rank::King), (Suit::Acorns, Rank::Seven)]);
        assert!(suit_safe(Suit::Acorns, a, b, Order::Mariage, None));
        let b3 = b.union(set(&[(Suit::Acorns, Rank::Eight)]));
        // Three opposing cards against two winners: safe outside trumps only.
        assert!(suit_safe(Suit::Acorns, a, b3, Order::Mariage, None));
        assert!(!suit_safe(
            Suit::Acorns,
            a,
            b3,
            Order::Mariage,
            Some(Suit::Acorns)
        ));
        let weak = set(&[(Suit::Acorns, Rank::King)]);
        assert!(!suit_safe(Suit::Acorns, weak, a, Order::Mariage, None));
    }

    #[test]
    fn sure_tricks_count_top_run() {
        let a = set(&[
            (Suit::Leaves, Rank::Ace),
            (Suit::Leaves, Rank::Ten),
            (Suit::Leaves, Rank::Seven),
        ]);
        // The king is still out: ace and ten win, the seven does not.
        assert_eq!(
            sure_tricks_suit(Suit::Leaves, a, CardSet::EMPTY, Order::Mariage, None),
            2
        );
    }

    #[test]
    fn betl_low_run_and_danger() {
        let a = set(&[
            (Suit::Hearts, Rank::Seven),
            (Suit::Hearts, Rank::Eight),
            (Suit::Hearts, Rank::Ten),
        ]);
        assert_eq!(low_run(Suit::Hearts, a, CardSet::EMPTY), 2);
        assert!(!betl_suit_safe(Suit::Hearts, a, CardSet::EMPTY));
        let gone = set(&[(Suit::Hearts, Rank::Nine)]);
        assert!(betl_suit_safe(Suit::Hearts, a, gone));
        let (holes, out) = betl_danger(a, CardSet::EMPTY);
        assert_eq!(holes, 1);
        assert!(out.contains(Card::new(Suit::Hearts, Rank::Ten)));
    }
}
