//! The 32-card German-suited Mariáš deck and compact card sets.

use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Suit {
    Acorns,
    Leaves,
    Bells,
    Hearts,
}

impl Suit {
    pub const ALL: [Suit; 4] = [Suit::Acorns, Suit::Leaves, Suit::Bells, Suit::Hearts];

    pub const fn index(self) -> u8 {
        self as u8
    }

    pub fn from_index(i: u8) -> Suit {
        Suit::ALL[(i & 3) as usize]
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Rank {
    Seven,
    Eight,
    Nine,
    Ten,
    /// Unter ("spodek").
    Under,
    /// Ober ("svršek").
    Over,
    King,
    Ace,
}

impl Rank {
    pub const ALL: [Rank; 8] = [
        Rank::Seven,
        Rank::Eight,
        Rank::Nine,
        Rank::Ten,
        Rank::Under,
        Rank::Over,
        Rank::King,
        Rank::Ace,
    ];

    pub const fn index(self) -> u8 {
        self as u8
    }

    pub fn from_index(i: u8) -> Rank {
        Rank::ALL[(i & 7) as usize]
    }

    /// Trick-taking strength in suit games: 7 8 9 U O K 10 A.
    pub const fn strength(self) -> u8 {
        match self {
            Rank::Seven => 0,
            Rank::Eight => 1,
            Rank::Nine => 2,
            Rank::Under => 3,
            Rank::Over => 4,
            Rank::King => 5,
            Rank::Ten => 6,
            Rank::Ace => 7,
        }
    }

    /// Trick-taking strength in no-trump contracts (betl, durch): 7 8 9 10 U O K A.
    pub const fn natural_strength(self) -> u8 {
        self.index()
    }

    /// Whether this is an "ostrá" (sharp) card: ten or ace, worth 10 points.
    pub fn is_sharp(self) -> bool {
        matches!(self, Rank::Ten | Rank::Ace)
    }
}

/// A card; its id (0..32) is `suit * 8 + rank`.
#[derive(Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct Card(u8);

impl Card {
    pub fn new(suit: Suit, rank: Rank) -> Card {
        Card(suit.index() * 8 + rank.index())
    }

    pub fn from_id(id: u8) -> Card {
        assert!(id < 32, "card id {id} out of range");
        Card(id)
    }

    pub fn id(self) -> u8 {
        self.0
    }

    pub fn suit(self) -> Suit {
        Suit::from_index(self.0 / 8)
    }

    pub fn rank(self) -> Rank {
        Rank::from_index(self.0 % 8)
    }
}

impl fmt::Debug for Card {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let suit = ['A', 'L', 'B', 'H'][self.suit() as usize];
        let rank = ['7', '8', '9', 'X', 'U', 'O', 'K', 'A'][self.rank() as usize];
        write!(f, "{rank}{suit}")
    }
}

/// A set of cards stored as a 32-bit mask indexed by card id.
#[derive(Clone, Copy, Default, PartialEq, Eq, Hash)]
pub struct CardSet(u32);

impl CardSet {
    pub const EMPTY: CardSet = CardSet(0);
    pub const FULL: CardSet = CardSet(u32::MAX);
    pub const TENS: CardSet = CardSet::rank(Rank::Ten);
    pub const ACES: CardSet = CardSet::rank(Rank::Ace);
    /// Tens and aces ("ostré"), the cards that score points.
    pub const SHARP: CardSet = CardSet::TENS.union(CardSet::ACES);

    pub const fn suit(suit: Suit) -> CardSet {
        CardSet(0xFF << (suit.index() * 8))
    }

    pub const fn rank(rank: Rank) -> CardSet {
        CardSet(0x0101_0101 << rank.index())
    }

    /// A set of the given cards.
    pub fn of(cards: &[Card]) -> CardSet {
        cards.iter().copied().collect()
    }

    /// The queen/king pair ("hláška") of a suit.
    pub fn marriage(suit: Suit) -> CardSet {
        CardSet::of(&[Card::new(suit, Rank::Over), Card::new(suit, Rank::King)])
    }

    /// Cards of `suit` whose rank bits are set in `bits`.
    pub(crate) fn from_suit_bits(suit: Suit, bits: u8) -> CardSet {
        CardSet((bits as u32) << (suit.index() * 8))
    }

    pub fn contains(self, card: Card) -> bool {
        self.0 >> card.id() & 1 == 1
    }

    pub fn insert(&mut self, card: Card) {
        self.0 |= 1 << card.id();
    }

    pub fn remove(&mut self, card: Card) {
        self.0 &= !(1 << card.id());
    }

    pub fn len(self) -> u32 {
        self.0.count_ones()
    }

    pub fn is_empty(self) -> bool {
        self.0 == 0
    }

    pub const fn union(self, other: CardSet) -> CardSet {
        CardSet(self.0 | other.0)
    }

    pub fn intersect(self, other: CardSet) -> CardSet {
        CardSet(self.0 & other.0)
    }

    pub fn minus(self, other: CardSet) -> CardSet {
        CardSet(self.0 & !other.0)
    }

    pub fn of_suit(self, suit: Suit) -> CardSet {
        self.intersect(CardSet::suit(suit))
    }

    /// The card with the lowest id.
    pub fn first(self) -> Option<Card> {
        (self.0 != 0).then(|| Card(self.0.trailing_zeros() as u8))
    }

    /// Cards in ascending id order.
    pub fn iter(self) -> Cards {
        Cards(self.0)
    }
}

/// Iterator over a [`CardSet`] in ascending id order.
#[derive(Clone)]
pub struct Cards(u32);

impl Iterator for Cards {
    type Item = Card;

    fn next(&mut self) -> Option<Card> {
        if self.0 == 0 {
            return None;
        }
        let id = self.0.trailing_zeros() as u8;
        self.0 &= self.0 - 1;
        Some(Card(id))
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let n = self.0.count_ones() as usize;
        (n, Some(n))
    }
}

impl ExactSizeIterator for Cards {}

impl From<Card> for CardSet {
    fn from(card: Card) -> CardSet {
        CardSet(1 << card.id())
    }
}

impl FromIterator<Card> for CardSet {
    fn from_iter<I: IntoIterator<Item = Card>>(iter: I) -> CardSet {
        let mut s = CardSet::EMPTY;
        for c in iter {
            s.insert(c);
        }
        s
    }
}

impl fmt::Debug for CardSet {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_set().entries(self.iter()).finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn card_id_round_trips_suit_and_rank() {
        for id in 0..32 {
            let c = Card::from_id(id);
            assert_eq!(Card::new(c.suit(), c.rank()), c);
        }
        assert_eq!(Card::new(Suit::Hearts, Rank::Seven).id(), 24);
    }

    #[test]
    fn ten_ranks_between_king_and_ace_in_suit_games() {
        assert!(Rank::Ten.strength() > Rank::King.strength());
        assert!(Rank::Ten.strength() < Rank::Ace.strength());
        assert!(Rank::Ten.natural_strength() < Rank::Under.natural_strength());
    }

    #[test]
    fn set_operations() {
        let hearts = CardSet::suit(Suit::Hearts);
        assert_eq!(hearts.len(), 8);
        assert!(hearts.contains(Card::new(Suit::Hearts, Rank::Ace)));
        let aces = CardSet::rank(Rank::Ace);
        assert_eq!(aces.len(), 4);
        assert_eq!(
            hearts.intersect(aces).iter().collect::<Vec<_>>(),
            vec![Card::new(Suit::Hearts, Rank::Ace)]
        );
        assert_eq!(CardSet::FULL.minus(hearts).len(), 24);
        assert_eq!(CardSet::SHARP.len(), 8);
        assert_eq!(hearts.first(), Some(Card::new(Suit::Hearts, Rank::Seven)));
        assert_eq!(CardSet::EMPTY.first(), None);
        assert_eq!(
            CardSet::from(Card::from_id(5)),
            CardSet::of(&[Card::from_id(5)])
        );
        assert_eq!(hearts.iter().len(), 8);
        assert_eq!(CardSet::marriage(Suit::Bells).len(), 2);
    }
}
