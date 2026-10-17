//! One deal of volený mariáš: the deck, dealing, the contract state and the
//! trick-play rules.

use super::analysis::{Order, all_suits_safe, betl_safe_suits, higher_than, highest};
use super::cards::{Card, CardSet, Rank, Suit};
use super::rng::Rng;

/// Seat index: 0 is the human, 1 and 2 the computer players. Play goes 0 → 1 → 2.
pub type Player = usize;

pub fn next(p: Player) -> Player {
    (p + 1) % 3
}

pub fn prev(p: Player) -> Player {
    (p + 2) % 3
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Contract {
    Game,
    Seven,
    Hundred,
    HundredSeven,
    Betl,
    Durch,
}

impl Contract {
    /// Betl and durch are played without trumps in natural rank order.
    pub fn no_trumps(self) -> bool {
        matches!(self, Contract::Betl | Contract::Durch)
    }

    pub fn has_seven(self) -> bool {
        matches!(self, Contract::Seven | Contract::HundredSeven)
    }

    pub fn has_hundred(self) -> bool {
        matches!(self, Contract::Hundred | Contract::HundredSeven)
    }
}

/// The deck between deals. It is only cut, not shuffled, so card sequences
/// survive from one deal to the next as at a real table.
#[derive(Clone, Debug)]
pub struct Deck {
    cards: Vec<Card>,
}

impl Deck {
    /// A fresh deck, cut 32 times.
    pub fn fresh(rng: &mut Rng) -> Deck {
        let mut d = Deck {
            cards: (0..32).map(Card::from_id).collect(),
        };
        d.cut(32, rng);
        d
    }

    pub fn from_cards(cards: Vec<Card>) -> Deck {
        Deck { cards }
    }

    pub fn cards(&self) -> &[Card] {
        &self.cards
    }

    /// Each cut moves 10..29 top cards, reversed, to the bottom.
    pub fn cut(&mut self, times: usize, rng: &mut Rng) {
        for _ in 0..times {
            let k = rng.below(20) as usize + 10;
            self.cards[..k].reverse();
            self.cards.rotate_left(k);
        }
    }

    fn is_complete(&self) -> bool {
        self.cards.len() == 32 && self.cards.iter().copied().collect::<CardSet>() == CardSet::FULL
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Trick {
    pub leader: Player,
    pub winner: Player,
    /// Cards in play order: leader, next, prev.
    pub cards: [Card; 3],
}

impl Trick {
    pub fn player_of(&self, i: usize) -> Player {
        (self.leader + i) % 3
    }
}

/// What happened when a card completed a trick.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TrickEnd {
    Normal,
    /// Betl or durch failed for the declarer.
    ContractLost,
    /// The betl declarer can no longer be forced to take a trick.
    BetlWon,
    /// The trick winner holds every remaining suit; the rest is played out.
    Claimed,
}

/// How the player on turn stands in the trick; decides which cards he may play.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Situation {
    Lead,
    /// Second player: can beat the led card.
    SecondBeat,
    /// Second player: follows suit without beating.
    SecondFollow,
    /// Second player: void, must trump.
    SecondTrump,
    /// Second player: void and without trumps.
    SecondDiscard,
    /// Third player, second followed: can beat both cards.
    ThirdBeatBoth,
    /// Third player, second followed: follows without beating.
    ThirdFollow,
    /// Third player follows suit after the second player trumped.
    ThirdFollowAfterTrump,
    /// Third player, second discarded: can beat the led card.
    ThirdBeatAfterDiscard,
    /// Third player, second discarded: follows without beating.
    ThirdFollowAfterDiscard,
    /// Third player: void and without trumps.
    ThirdDiscard,
    /// Third player: void, second trumped, can over-trump.
    ThirdOvertrump,
    /// Third player: void, second trumped, cannot over-trump.
    ThirdUndertrump,
    /// Third player: void, second did not trump.
    ThirdTrumpIn,
}

/// Why a card may not be played.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Illegal {
    /// The king of a held marriage: the queen comes first.
    QueenFirst,
    /// The announced trump seven is kept for the last trick.
    KeepSeven,
    /// A card of the led suit that does not beat the trick.
    MustBeat,
    /// The led suit must be followed.
    MustFollow(Suit),
    /// The player is void in the led suit and must trump.
    MustTrump,
    /// Another restriction, such as the forced play-out of a decided game.
    Other,
}

/// The full state of one deal.
#[derive(Clone, Debug)]
pub struct Round {
    pub dealer: Player,
    /// Leads the first trick: the player after the dealer, or the declarer in betl/durch.
    pub forehand: Player,
    pub declarer: Player,
    pub hands: [CardSet; 3],
    /// The forehand's first seven cards, from which he chooses trumps.
    pub first_seven: CardSet,
    pub trump_card: Option<Card>,
    /// The trump card lies face down beside the forehand, in nobody's hand.
    pub trump_card_aside: bool,
    /// Bidding is open: a defender may still take the talon over.
    pub bidding: bool,
    pub trump: Option<Suit>,
    /// The two discarded cards, in discard order.
    pub talon: Vec<Card>,
    pub contract: Contract,
    pub seven_announced: bool,
    /// The hundred declarer lacks the trump marriage ("na cizí hlášku").
    pub no_trump_marriage: bool,
    /// All queen/king pairs held at the start of play.
    pub marriages: CardSet,
    pub marriage_points: [u32; 3],
    pub flek_game: u32,
    pub flek_seven: u32,
    /// A plain game nobody doubled is paid without being played.
    pub not_played: bool,
    pub decided: bool,
    /// Betl or durch lost.
    pub lost: bool,
    /// Points for tens and aces won, per player (last trick not included).
    pub sharp_points: [u32; 3],
    pub tricks: Vec<Trick>,
    /// Cards of the trick in progress, in play order.
    pub table: Vec<Card>,
    pub leader: Player,
    /// Cards out of play: the talon and every played card.
    pub played: CardSet,
    /// The real deal shown to the user (false inside AI simulations).
    pub real: bool,
    /// Search horizon in plies for the computer players (see `ai`).
    pub horizon: i32,
    /// Per player: other players' cards that beat one of his cards.
    pub threats: [CardSet; 3],
    /// Per player: other players' cards that one of his cards beats.
    pub victims: [CardSet; 3],
}

impl Round {
    /// Deals a new round: 7 cards to the forehand, then packets of 5.
    pub fn deal(deck: &mut Deck, dealer: Player, rng: &mut Rng) -> Round {
        if !deck.is_complete() {
            *deck = Deck::fresh(rng);
        }
        let forehand = next(dealer);
        let mut hands = [CardSet::EMPTY; 3];
        let mut pos = 0;
        let mut first_seven = CardSet::EMPTY;
        let packets = [
            (forehand, 7),
            (next(forehand), 5),
            (prev(forehand), 5),
            (forehand, 5),
            (next(forehand), 5),
            (prev(forehand), 5),
        ];
        for (i, &(p, n)) in packets.iter().enumerate() {
            for &c in &deck.cards()[pos..pos + n] {
                hands[p].insert(c);
                if i == 0 {
                    first_seven.insert(c);
                }
            }
            pos += n;
        }
        Round {
            dealer,
            forehand,
            declarer: forehand,
            hands,
            first_seven,
            trump_card: None,
            trump_card_aside: false,
            bidding: true,
            trump: None,
            talon: Vec::new(),
            contract: Contract::Game,
            seven_announced: false,
            no_trump_marriage: false,
            marriages: CardSet::EMPTY,
            marriage_points: [0; 3],
            flek_game: 0,
            flek_seven: 0,
            not_played: false,
            decided: false,
            lost: false,
            sharp_points: [0; 3],
            tricks: Vec::new(),
            table: Vec::new(),
            leader: forehand,
            played: CardSet::EMPTY,
            real: true,
            horizon: 0,
            threats: [CardSet::EMPTY; 3],
            victims: [CardSet::EMPTY; 3],
        }
    }

    pub fn order(&self) -> Order {
        if self.contract.no_trumps() {
            Order::Natural
        } else {
            Order::Mariage
        }
    }

    /// The trump suit, if the contract has trumps.
    pub fn trump_suit(&self) -> Option<Suit> {
        self.trump.filter(|_| !self.contract.no_trumps())
    }

    pub fn trump_cards(&self) -> CardSet {
        self.trump_suit().map_or(CardSet::EMPTY, CardSet::suit)
    }

    /// The trump card of `rank`, if the contract has trumps.
    pub fn trump_card_of(&self, rank: Rank) -> Option<Card> {
        self.trump_suit().map(|s| Card::new(s, rank))
    }

    pub fn trump_seven(&self) -> Option<Card> {
        self.trump_card_of(Rank::Seven)
    }

    pub fn talon_set(&self) -> CardSet {
        CardSet::of(&self.talon)
    }

    /// Cards `p` may put into the talon: no tens or aces in a trump game.
    pub fn discardable(&self, p: Player) -> CardSet {
        if self.contract.no_trumps() {
            self.hands[p]
        } else {
            self.hands[p].minus(CardSet::SHARP)
        }
    }

    /// Lays the trump card aside (the forehand chose it from his first seven).
    pub fn choose_trump(&mut self, card: Card) {
        self.hands[self.forehand].remove(card);
        self.trump_card = Some(card);
        self.trump = Some(card.suit());
        self.trump_card_aside = true;
    }

    /// Puts the laid-aside trump card, if it still lies aside, into `p`'s hand.
    fn pick_up_trump_card(&mut self, p: Player) {
        if self.trump_card_aside
            && let Some(tc) = self.trump_card
        {
            self.hands[p].insert(tc);
            self.trump_card_aside = false;
        }
    }

    /// The forehand's contract before he discards; betl and durch take the
    /// trump card back into his hand.
    pub fn declare(&mut self, contract: Contract) {
        self.contract = contract;
        if contract.no_trumps() {
            self.pick_up_trump_card(self.declarer);
        }
    }

    /// A defender takes over with betl or durch: a laid-aside trump card goes
    /// back to the previous declarer, and `p` picks up the talon.
    pub fn take_over(&mut self, p: Player, contract: Contract) {
        debug_assert!(contract.no_trumps(), "taking over with {contract:?}");
        self.pick_up_trump_card(self.declarer);
        self.declarer = p;
        self.contract = contract;
        for c in std::mem::take(&mut self.talon) {
            self.hands[p].insert(c);
        }
    }

    /// The declarer raises his contract: betl to durch, or after the bidding
    /// a suit game to a seven and/or hundred.
    pub fn raise_contract(&mut self, contract: Contract) {
        debug_assert!(
            contract >= self.contract && contract.no_trumps() == self.contract.no_trumps(),
            "{:?} raised to {contract:?}",
            self.contract
        );
        self.contract = contract;
        self.seven_announced = contract.has_seven();
    }

    /// Moves two cards from the declarer's hand to the talon.
    pub fn discard(&mut self, cards: [Card; 2]) {
        for c in cards {
            self.hands[self.declarer].remove(c);
        }
        self.talon = cards.to_vec();
    }

    /// Records all queen/king pairs; 40 in trumps, 20 otherwise.
    pub fn compute_marriages(&mut self) {
        self.marriages = CardSet::EMPTY;
        self.marriage_points = [0; 3];
        if self.contract.no_trumps() {
            return;
        }
        for s in Suit::ALL {
            let pair = CardSet::marriage(s);
            for p in 0..3 {
                if self.hands[p].intersect(pair) == pair {
                    self.marriages = self.marriages.union(pair);
                    self.marriage_points[p] += self.marriage_value(s);
                }
            }
        }
    }

    /// A marriage is worth 40 in trumps, 20 otherwise.
    pub fn marriage_value(&self, suit: Suit) -> u32 {
        if Some(suit) == self.trump { 40 } else { 20 }
    }

    /// Closes the bidding: a laid-aside trump card joins the declarer's hand,
    /// and the marriages, the announced seven and whether a hundred is built
    /// on the declarer's own marriage are fixed. A suit-game declarer may
    /// still `raise_contract` afterwards.
    pub fn finish_bidding(&mut self) {
        self.pick_up_trump_card(self.declarer);
        self.bidding = false;
        self.compute_marriages();
        self.seven_announced = self.contract.has_seven();
        if let Some(t) = self.trump {
            let qk = CardSet::marriage(t);
            self.no_trump_marriage = self.hands[self.declarer].intersect(qk) != qk;
        }
    }

    /// A plain game nobody doubled (or a seven whose game alone was doubled
    /// once) is settled without being played.
    pub fn settles_unplayed(&self) -> bool {
        (self.contract == Contract::Game && self.flek_game == 0 && !self.seven_announced)
            || (self.contract == Contract::Seven && self.flek_game == 1 && self.flek_seven == 0)
    }

    /// Prepares the state for trick play once bidding is over.
    pub fn start_play(&mut self) {
        if self.contract.no_trumps() {
            self.forehand = self.declarer;
            self.trump = None;
        }
        self.leader = self.forehand;
        self.played = self.talon_set();
        self.tricks.clear();
        self.table.clear();
        self.init_threats();
    }

    fn init_threats(&mut self) {
        let order = self.order();
        let trumps = self.trump_cards();
        for p in 0..3 {
            let hand = self.hands[p];
            let (mut threats, mut victims) = (CardSet::EMPTY, CardSet::EMPTY);
            for c in hand.iter() {
                let higher = higher_than(c, order);
                threats = threats.union(higher.minus(hand));
                victims = victims.union(CardSet::suit(c.suit()).minus(higher).minus(hand));
                if trumps.contains(c) {
                    victims = victims.union(CardSet::FULL.minus(trumps).minus(hand));
                } else {
                    threats = threats.union(trumps.minus(hand));
                }
            }
            self.threats[p] = threats;
            self.victims[p] = victims;
        }
    }

    pub fn trick_no(&self) -> usize {
        self.tricks.len() + 1
    }

    pub fn is_over(&self) -> bool {
        self.tricks.len() == 10 || (self.decided && self.contract.no_trumps())
    }

    pub fn to_play(&self) -> Player {
        (self.leader + self.table.len()) % 3
    }

    /// The player currently winning the trick on the table.
    pub fn current_winner(&self) -> Player {
        let mut best = 0;
        for i in 1..self.table.len() {
            if self.beats(self.table[i], self.table[best]) {
                best = i;
            }
        }
        (self.leader + best) % 3
    }

    /// Whether `a` beats `b` given the led suit is `b`'s suit or a trump.
    fn beats(&self, a: Card, b: Card) -> bool {
        let trumps = self.trump_cards();
        if trumps.contains(a) && !trumps.contains(b) {
            return true;
        }
        a.suit() == b.suit() && self.order().beats(a, b)
    }

    /// The situation of `p` in the current trick and the cards the basic
    /// rules allow: follow suit, beat if possible, else trump, and the third
    /// player must over-trump a trump if he can.
    pub fn classify(&self, p: Player) -> (Situation, CardSet) {
        use Situation::*;
        let hand = self.hands[p];
        let Some(&lead) = self.table.first() else {
            return (Lead, hand);
        };
        let order = self.order();
        let trumps = self.trump_cards();
        let in_suit = hand.of_suit(lead.suit());
        let my_trumps = hand.intersect(trumps);
        let beating = |c: Card| in_suit.intersect(higher_than(c, order));
        if self.table.len() == 1 {
            return if !beating(lead).is_empty() {
                (SecondBeat, beating(lead))
            } else if !in_suit.is_empty() {
                (SecondFollow, in_suit)
            } else if !my_trumps.is_empty() {
                (SecondTrump, my_trumps)
            } else {
                (SecondDiscard, hand)
            };
        }
        let second = self.table[1];
        if !in_suit.is_empty() {
            if second.suit() == lead.suit() {
                let top = if order.beats(second, lead) {
                    second
                } else {
                    lead
                };
                let higher = beating(top);
                return if higher.is_empty() {
                    (ThirdFollow, in_suit)
                } else {
                    (ThirdBeatBoth, higher)
                };
            }
            if trumps.contains(second) {
                return (ThirdFollowAfterTrump, in_suit);
            }
            let higher = beating(lead);
            return if higher.is_empty() {
                (ThirdFollowAfterDiscard, in_suit)
            } else {
                (ThirdBeatAfterDiscard, higher)
            };
        }
        if my_trumps.is_empty() {
            return (ThirdDiscard, hand);
        }
        if !trumps.contains(second) {
            return (ThirdTrumpIn, my_trumps);
        }
        let over = my_trumps.intersect(higher_than(second, order));
        if over.is_empty() {
            (ThirdUndertrump, my_trumps)
        } else {
            (ThirdOvertrump, over)
        }
    }

    /// Cards `p` may play to the current trick, before the extra restrictions.
    pub fn legal_basic(&self, p: Player) -> CardSet {
        self.classify(p).1
    }

    /// Cards `p` may play, with the marriage and seven restrictions and the
    /// forced play-out of a decided game.
    pub fn legal(&self, p: Player) -> CardSet {
        let mut allowed = self.legal_basic(p);
        // A held marriage is announced with the queen first.
        for s in Suit::ALL {
            let q = Card::new(s, Rank::Over);
            if self.marriages.contains(q) && allowed.contains(q) {
                allowed.remove(Card::new(s, Rank::King));
            }
        }
        // An announced trump seven must be kept for the last trick.
        if self.seven_announced
            && let Some(t7) = self.trump_seven()
            && allowed.contains(t7)
            && allowed.len() > 1
        {
            allowed.remove(t7);
        }
        if self.decided
            && self.trick_no() >= 2
            && let Some(c) = self.forced_card(allowed)
        {
            return c.into();
        }
        allowed
    }

    /// Why `p` may not play `card`, which `legal` does not allow.
    pub fn illegal_reason(&self, p: Player, card: Card) -> Illegal {
        debug_assert!(!self.legal(p).contains(card), "{card:?} is legal");
        let q = Card::new(card.suit(), Rank::Over);
        if card.rank() == Rank::King && self.marriages.contains(q) && self.hands[p].contains(q) {
            return Illegal::QueenFirst;
        }
        if self.trump_seven() == Some(card) && self.seven_announced {
            return Illegal::KeepSeven;
        }
        let allowed = self.legal_basic(p);
        if let Some(&lead) = self.table.first() {
            let suit = lead.suit();
            if allowed.iter().all(|c| c.suit() == suit) {
                let higher = allowed
                    .iter()
                    .all(|c| higher_than(lead, self.order()).contains(c) || self.table.len() == 2);
                return if card.suit() == suit && higher {
                    Illegal::MustBeat
                } else {
                    Illegal::MustFollow(suit)
                };
            }
            if allowed.iter().all(|c| Some(c.suit()) == self.trump) {
                return Illegal::MustTrump;
            }
        }
        Illegal::Other
    }

    /// In a decided game every player plays his highest trump, else the
    /// highest card of his highest suit.
    fn forced_card(&self, allowed: CardSet) -> Option<Card> {
        let order = self.order();
        if let Some(t) = self.trump_suit()
            && let Some(c) = highest(allowed, t, order)
        {
            return Some(c);
        }
        Suit::ALL
            .iter()
            .rev()
            .find_map(|&s| highest(allowed, s, order))
    }

    /// Plays a card for the player on turn. Returns how the trick ended when
    /// this card completed it.
    pub fn play(&mut self, card: Card) -> Option<TrickEnd> {
        let p = self.to_play();
        debug_assert!(
            self.hands[p].contains(card),
            "player {p} does not hold {card:?}"
        );
        self.hands[p].remove(card);
        self.played.insert(card);
        self.table.push(card);
        if self.table.len() < 3 {
            return None;
        }
        let winner = self.current_winner();
        let trick = Trick {
            leader: self.leader,
            winner,
            cards: [self.table[0], self.table[1], self.table[2]],
        };
        self.tricks.push(trick);
        self.table.clear();
        self.leader = winner;
        Some(self.finish_trick(trick))
    }

    fn finish_trick(&mut self, trick: Trick) -> TrickEnd {
        let d = self.declarer;
        match self.contract {
            Contract::Betl if trick.winner == d => {
                self.lost = true;
                self.decided = true;
                return TrickEnd::ContractLost;
            }
            Contract::Durch if trick.winner != d => {
                self.lost = true;
                self.decided = true;
                return TrickEnd::ContractLost;
            }
            Contract::Betl | Contract::Durch => {}
            _ => {
                let sharp = trick.cards.iter().filter(|c| c.rank().is_sharp()).count() as u32;
                self.sharp_points[trick.winner] += 10 * sharp;
            }
        }
        if self.decided || self.tricks.len() == 10 {
            return TrickEnd::Normal;
        }
        if self.contract == Contract::Betl && betl_safe_suits(self.hands[d], self.played) == 4 {
            if self.tricks.len() + 1 < 8 {
                self.decided = true;
                return TrickEnd::BetlWon;
            }
            return TrickEnd::Normal;
        }
        let w = trick.winner;
        let mut unknown = CardSet::FULL.minus(self.hands[w]).minus(self.played);
        if self.real && w != d {
            unknown = unknown.union(self.talon_set());
        }
        if all_suits_safe(self.hands[w], unknown, self.order(), self.trump)
            && (!self.real || self.tricks.len() + 1 < 8)
        {
            self.decided = true;
            return TrickEnd::Claimed;
        }
        TrickEnd::Normal
    }

    /// Gathers the cards for the next deal: talon first, then each player's
    /// won tricks, then cut twice. Early-decided deals are fully reshuffled.
    pub fn next_deck(&self, rng: &mut Rng) -> Deck {
        if self.decided || rng.below(128) == 3 || self.talon.len() != 2 {
            return Deck::fresh(rng);
        }
        let mut cards = vec![self.talon[1], self.talon[0]];
        for p in 0..3 {
            if self.not_played {
                cards.extend(self.hands[p].iter());
            } else {
                for t in self.tricks.iter().filter(|t| t.winner == p) {
                    cards.extend(t.cards);
                }
            }
        }
        let mut deck = Deck::from_cards(cards);
        if !deck.is_complete() {
            return Deck::fresh(rng);
        }
        deck.cut(2, rng);
        deck
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn c(s: Suit, r: Rank) -> Card {
        Card::new(s, r)
    }

    fn set(cards: &[Card]) -> CardSet {
        cards.iter().copied().collect()
    }

    /// A round in trick play with the given hands and contract.
    fn playing(hands: [CardSet; 3], contract: Contract, trump: Option<Suit>) -> Round {
        let mut rng = Rng::new(1);
        let mut deck = Deck::fresh(&mut rng);
        let mut r = Round::deal(&mut deck, 2, &mut rng);
        r.hands = hands;
        r.contract = contract;
        r.trump = trump;
        r.declarer = 0;
        r.forehand = 0;
        r.real = false;
        r.start_play();
        r
    }

    #[test]
    fn deal_gives_twelve_to_forehand_and_ten_to_others() {
        let mut rng = Rng::new(5);
        let mut deck = Deck::fresh(&mut rng);
        let r = Round::deal(&mut deck, 0, &mut rng);
        assert_eq!(r.forehand, 1);
        assert_eq!(r.hands[1].len(), 12);
        assert_eq!(r.hands[2].len(), 10);
        assert_eq!(r.hands[0].len(), 10);
        assert_eq!(r.first_seven.len(), 7);
        assert_eq!(r.first_seven.intersect(r.hands[1]), r.first_seven);
        assert_eq!(
            r.hands[0].union(r.hands[1]).union(r.hands[2]),
            CardSet::FULL
        );
    }

    #[test]
    fn cut_keeps_all_cards() {
        let mut rng = Rng::new(9);
        let mut deck = Deck::fresh(&mut rng);
        deck.cut(5, &mut rng);
        assert!(deck.is_complete());
    }

    #[test]
    fn second_player_must_beat_then_follow_then_trump() {
        let hands = [
            set(&[c(Suit::Acorns, Rank::Nine)]),
            set(&[
                c(Suit::Acorns, Rank::Seven),
                c(Suit::Acorns, Rank::Ten),
                c(Suit::Hearts, Rank::Seven),
            ]),
            set(&[c(Suit::Leaves, Rank::Seven), c(Suit::Hearts, Rank::Eight)]),
        ];
        let mut r = playing(hands, Contract::Game, Some(Suit::Hearts));
        r.play(c(Suit::Acorns, Rank::Nine));
        assert_eq!(r.legal(1), set(&[c(Suit::Acorns, Rank::Ten)]));
        r.play(c(Suit::Acorns, Rank::Ten));
        // Third player is void in acorns and must trump.
        assert_eq!(r.legal(2), set(&[c(Suit::Hearts, Rank::Eight)]));
    }

    #[test]
    fn illegal_cards_are_explained() {
        let hands = [
            set(&[c(Suit::Acorns, Rank::Nine)]),
            set(&[
                c(Suit::Acorns, Rank::Seven),
                c(Suit::Acorns, Rank::Ten),
                c(Suit::Hearts, Rank::Seven),
            ]),
            set(&[c(Suit::Leaves, Rank::Seven), c(Suit::Hearts, Rank::Eight)]),
        ];
        let mut r = playing(hands, Contract::Game, Some(Suit::Hearts));
        r.play(c(Suit::Acorns, Rank::Nine));
        assert_eq!(
            r.illegal_reason(1, c(Suit::Acorns, Rank::Seven)),
            Illegal::MustBeat
        );
        assert_eq!(
            r.illegal_reason(1, c(Suit::Hearts, Rank::Seven)),
            Illegal::MustFollow(Suit::Acorns)
        );
        r.play(c(Suit::Acorns, Rank::Ten));
        assert_eq!(
            r.illegal_reason(2, c(Suit::Leaves, Rank::Seven)),
            Illegal::MustTrump
        );
    }

    #[test]
    fn trump_card_returns_to_the_declarer_before_a_take_over() {
        let mut rng = Rng::new(3);
        let mut deck = Deck::fresh(&mut rng);
        let mut r = Round::deal(&mut deck, 0, &mut rng);
        let fh = r.forehand;
        let tc = r.first_seven.first().expect("seven cards");
        r.choose_trump(tc);
        assert!(r.trump_card_aside && !r.hands[fh].contains(tc));
        r.declare(Contract::Game);
        assert!(r.trump_card_aside);
        let talon = r.discardable(fh).iter().take(2).collect::<Vec<_>>();
        r.discard([talon[0], talon[1]]);
        let p = next(fh);
        r.take_over(p, Contract::Betl);
        assert!(!r.trump_card_aside && r.hands[fh].contains(tc));
        assert_eq!(
            (r.declarer, r.hands[fh].len(), r.hands[p].len()),
            (p, 10, 12)
        );
        assert!(r.talon.is_empty() && r.bidding);
        r.discard([
            r.hands[p].first().unwrap(),
            r.hands[p].iter().last().unwrap(),
        ]);
        r.finish_bidding();
        assert!(!r.bidding && r.hands.iter().all(|h| h.len() == 10));
    }

    #[test]
    fn trump_card_joins_the_hand_for_no_trumps_or_after_bidding() {
        let mut rng = Rng::new(4);
        let mut deck = Deck::fresh(&mut rng);
        let mut r = Round::deal(&mut deck, 1, &mut rng);
        let tc = r.first_seven.first().expect("seven cards");
        let mut durch = r.clone();
        durch.choose_trump(tc);
        durch.declare(Contract::Durch);
        assert!(!durch.trump_card_aside && durch.hands[durch.forehand].len() == 12);
        r.choose_trump(tc);
        r.declare(Contract::Seven);
        r.finish_bidding();
        assert!(!r.trump_card_aside && r.hands[r.declarer].contains(tc));
        assert!(r.seven_announced);
        r.raise_contract(Contract::HundredSeven);
        assert_eq!(r.contract, Contract::HundredSeven);
    }

    #[test]
    fn third_player_must_overtrump_or_undertrump() {
        let hands = [
            set(&[c(Suit::Acorns, Rank::Nine)]),
            set(&[c(Suit::Hearts, Rank::King)]),
            set(&[
                c(Suit::Hearts, Rank::Seven),
                c(Suit::Hearts, Rank::Ace),
                c(Suit::Leaves, Rank::Ace),
            ]),
        ];
        let mut r = playing(hands, Contract::Game, Some(Suit::Hearts));
        r.play(c(Suit::Acorns, Rank::Nine));
        r.play(c(Suit::Hearts, Rank::King));
        assert_eq!(r.legal(2), set(&[c(Suit::Hearts, Rank::Ace)]));
    }

    #[test]
    fn third_player_following_after_a_trump_need_not_beat() {
        let hands = [
            set(&[c(Suit::Acorns, Rank::Nine)]),
            set(&[c(Suit::Hearts, Rank::King)]),
            set(&[c(Suit::Acorns, Rank::Seven), c(Suit::Acorns, Rank::Ace)]),
        ];
        let mut r = playing(hands, Contract::Game, Some(Suit::Hearts));
        r.play(c(Suit::Acorns, Rank::Nine));
        r.play(c(Suit::Hearts, Rank::King));
        assert_eq!(r.legal(2).len(), 2);
    }

    #[test]
    fn marriage_queen_before_king_and_seven_kept() {
        let q = c(Suit::Leaves, Rank::Over);
        let k = c(Suit::Leaves, Rank::King);
        let t7 = c(Suit::Hearts, Rank::Seven);
        let hands = [
            set(&[q, k, t7, c(Suit::Hearts, Rank::Ace)]),
            set(&[c(Suit::Bells, Rank::Seven)]),
            set(&[c(Suit::Bells, Rank::Eight)]),
        ];
        let mut r = playing(hands, Contract::Seven, Some(Suit::Hearts));
        r.seven_announced = true;
        r.compute_marriages();
        assert_eq!(r.marriage_points[0], 20);
        let legal = r.legal(0);
        assert!(legal.contains(q));
        assert!(!legal.contains(k));
        assert!(!legal.contains(t7));
        assert_eq!(r.illegal_reason(0, k), Illegal::QueenFirst);
        assert_eq!(r.illegal_reason(0, t7), Illegal::KeepSeven);
    }

    #[test]
    fn trick_winner_and_sharp_points() {
        let hands = [
            set(&[c(Suit::Acorns, Rank::Ten), c(Suit::Bells, Rank::Seven)]),
            set(&[c(Suit::Acorns, Rank::Ace), c(Suit::Bells, Rank::Eight)]),
            set(&[c(Suit::Hearts, Rank::Seven), c(Suit::Bells, Rank::Nine)]),
        ];
        let mut r = playing(hands, Contract::Game, Some(Suit::Hearts));
        r.play(c(Suit::Acorns, Rank::Ten));
        r.play(c(Suit::Acorns, Rank::Ace));
        let end = r.play(c(Suit::Hearts, Rank::Seven));
        assert!(end.is_some());
        assert_eq!(r.tricks[0].winner, 2);
        assert_eq!(r.sharp_points[2], 20);
        assert_eq!(r.leader, 2);
    }

    #[test]
    fn betl_is_lost_when_declarer_takes_a_trick() {
        let hands = [
            set(&[c(Suit::Acorns, Rank::Ace), c(Suit::Bells, Rank::Seven)]),
            set(&[c(Suit::Acorns, Rank::Seven), c(Suit::Bells, Rank::Eight)]),
            set(&[c(Suit::Acorns, Rank::Eight), c(Suit::Bells, Rank::Nine)]),
        ];
        let mut r = playing(hands, Contract::Betl, None);
        r.play(c(Suit::Acorns, Rank::Ace));
        r.play(c(Suit::Acorns, Rank::Seven));
        assert_eq!(
            r.play(c(Suit::Acorns, Rank::Eight)),
            Some(TrickEnd::ContractLost)
        );
        assert!(r.lost && r.is_over());
    }
}
