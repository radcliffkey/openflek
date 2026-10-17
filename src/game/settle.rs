//! Settlement of a finished deal. Money is in units of 0.10 Kč; amounts are
//! from the declarer's point of view and paid by each defender.

use super::cards::{CardSet, Suit};
use super::round::{Contract, Player, Round, next, prev};

/// Base prices per contract, in units.
const PRICE_GAME: i64 = 1;
const PRICE_SEVEN: i64 = 2;
const PRICE_HUNDRED: i64 = 4;
const PRICE_BETL: i64 = 5;
const PRICE_DURCH: i64 = 10;

/// What the game part of the settlement was.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GameItem {
    /// Unplayed plain game, paid as won.
    Plain,
    /// Unplayed game doubled once: the declarer gives it up.
    PlainDoubled,
    Game,
    /// One side reached 100 without announcing it.
    SilentHundred {
        points: u32,
        against: bool,
    },
    Hundred {
        points: u32,
    },
    HundredLost,
    Betl,
    Durch,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SevenItem {
    Won,
    Lost,
    /// The trump seven took the last trick without being announced.
    Silent,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SevenResult {
    pub item: SevenItem,
    /// Announced by a defender ("sedma proti"), or a defender's silent seven.
    pub against: bool,
    /// Played in the last trick but the trick was lost.
    pub killed: bool,
}

/// Card points of a played suit game.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Points {
    pub declarer: u32,
    pub declarer_marriages: u32,
    pub defenders: u32,
    pub defender_marriages: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Settlement {
    pub game_item: GameItem,
    pub game: i64,
    pub seven: Option<SevenResult>,
    pub seven_money: i64,
    pub flek_game: u32,
    pub flek_seven: u32,
    /// Hearts as trumps double everything.
    pub hearts: bool,
    pub points: Option<Points>,
    /// What each defender pays the declarer (negative: the declarer pays).
    pub per_defender: i64,
    pub not_played: bool,
}

impl Settlement {
    /// Net money of player `p`.
    pub fn net(&self, p: Player, declarer: Player) -> i64 {
        if p == declarer {
            2 * self.per_defender
        } else {
            -self.per_defender
        }
    }

    /// The value the computer players optimise: like `net`, but the
    /// declarer's side counts three times the stake.
    pub fn ai_value(&self, p: Player, declarer: Player) -> i64 {
        if p == declarer {
            3 * self.per_defender
        } else {
            -self.per_defender
        }
    }
}

fn shl(v: i64, n: u32) -> i64 {
    v * (1i64 << n.min(40))
}

fn count_points(r: &Round) -> Points {
    let d = r.declarer;
    let mut declarer = r.sharp_points[d];
    let mut defenders = 80u32.saturating_sub(declarer);
    if r.tricks.last().map(|t| t.winner) == Some(d) {
        declarer += 10;
    } else {
        defenders += 10;
    }
    Points {
        declarer,
        declarer_marriages: r.marriage_points[d],
        defenders,
        defender_marriages: r.marriage_points[next(d)] + r.marriage_points[prev(d)],
    }
}

fn eval_game(p: &Points) -> (GameItem, i64) {
    let (dsum, osum) = (
        p.declarer + p.declarer_marriages,
        p.defenders + p.defender_marriages,
    );
    let (lead, money) = if dsum > osum {
        (dsum, PRICE_GAME)
    } else {
        (osum, -PRICE_GAME)
    };
    if lead < 100 {
        return (GameItem::Game, money);
    }
    // Doubles for every ten points over 100 (lead >= 100 here).
    let v = shl(PRICE_HUNDRED / 2, lead / 10 - 10);
    let against = osum == lead;
    (
        GameItem::SilentHundred {
            points: lead,
            against,
        },
        if against { -v } else { v },
    )
}

fn eval_hundred(r: &Round, p: &Points) -> (GameItem, i64) {
    let needed_marriage = if r.no_trump_marriage { 20 } else { 40 };
    let dsum = p.declarer + p.declarer_marriages;
    let (item, money, steps) = if p.defenders >= needed_marriage || dsum < 100 {
        let lc = (p.defenders as i64 + p.defender_marriages as i64 - needed_marriage as i64) / 10;
        (GameItem::HundredLost, -PRICE_HUNDRED, lc)
    } else {
        (
            GameItem::Hundred { points: dsum },
            PRICE_HUNDRED,
            (dsum as i64 - 100) / 10,
        )
    };
    (item, shl(money, steps.max(0) as u32))
}

fn eval_seven(r: &Round) -> Option<(SevenResult, i64)> {
    let t7 = r.trump_seven()?;
    let last = r.tricks.get(9)?;
    let own = r.contract.has_seven();
    let player = (0..3)
        .find(|&i| last.cards[i] == t7)
        .map(|i| last.player_of(i));
    let signed = |own: bool, v: i64| if own { v } else { -v };
    match player {
        None => r.seven_announced.then(|| {
            (
                SevenResult {
                    item: SevenItem::Lost,
                    against: !own,
                    killed: false,
                },
                signed(own, -PRICE_SEVEN),
            )
        }),
        Some(s) => {
            let (item, against, mut money) = if r.seven_announced {
                (SevenItem::Won, !own, signed(own, PRICE_SEVEN))
            } else {
                let mine = s == r.declarer;
                (SevenItem::Silent, !mine, signed(mine, PRICE_SEVEN / 2))
            };
            let killed = last.winner != s;
            if killed {
                money = -money;
            }
            Some((
                SevenResult {
                    item,
                    against,
                    killed,
                },
                money,
            ))
        }
    }
}

/// Settles a finished (or unplayed) deal.
pub fn settle(r: &Round) -> Settlement {
    let hearts = r.trump_cards() == CardSet::suit(Suit::Hearts);
    let mut s = Settlement {
        game_item: GameItem::Game,
        game: 0,
        seven: None,
        seven_money: 0,
        flek_game: r.flek_game,
        flek_seven: r.flek_seven,
        hearts,
        points: None,
        per_defender: 0,
        not_played: r.not_played,
    };
    match r.contract {
        Contract::Betl | Contract::Durch => {
            let price;
            (price, s.game_item) = if r.contract == Contract::Betl {
                (PRICE_BETL, GameItem::Betl)
            } else {
                (PRICE_DURCH, GameItem::Durch)
            };
            s.game = shl(price, r.flek_game) * if r.lost { -1 } else { 1 };
        }
        _ if r.not_played => {
            (s.game_item, s.game) = if r.flek_game == 1 {
                (GameItem::PlainDoubled, -2 * PRICE_GAME)
            } else {
                (GameItem::Plain, PRICE_GAME)
            };
            if r.contract == Contract::Seven {
                s.seven = Some(SevenResult {
                    item: SevenItem::Won,
                    against: false,
                    killed: false,
                });
                s.seven_money = PRICE_SEVEN;
            }
        }
        _ => {
            let p = count_points(r);
            (s.game_item, s.game) = if r.contract.has_hundred() {
                eval_hundred(r, &p)
            } else {
                eval_game(&p)
            };
            s.game = shl(s.game, r.flek_game);
            if let Some((res, money)) = eval_seven(r) {
                s.seven = Some(res);
                s.seven_money = shl(money, r.flek_seven);
            }
            s.points = Some(p);
        }
    }
    s.per_defender = s.game + s.seven_money;
    // `trump_cards` is empty in betl and durch, so they are never doubled.
    if hearts {
        s.per_defender *= 2;
    }
    s
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::cards::{Card, Rank};
    use crate::game::rng::Rng;
    use crate::game::round::{Deck, Trick};

    fn round(contract: Contract, trump: Suit) -> Round {
        let mut rng = Rng::new(3);
        let mut deck = Deck::fresh(&mut rng);
        let mut r = Round::deal(&mut deck, 2, &mut rng);
        r.declarer = 0;
        r.contract = contract;
        r.trump = Some(trump);
        r
    }

    fn last_trick(r: &mut Round, leader: Player, winner: Player, cards: [Card; 3]) {
        let filler = Trick {
            leader: 0,
            winner: 1,
            cards: [Card::from_id(0), Card::from_id(1), Card::from_id(2)],
        };
        r.tricks = vec![filler; 9];
        r.tricks.push(Trick {
            leader,
            winner,
            cards,
        });
    }

    #[test]
    fn plain_game_won_pays_one_unit() {
        let mut r = round(Contract::Game, Suit::Acorns);
        r.sharp_points = [60, 20, 0];
        r.marriage_points = [20, 0, 0];
        last_trick(
            &mut r,
            1,
            1,
            [Card::from_id(8), Card::from_id(9), Card::from_id(10)],
        );
        let s = settle(&r);
        assert_eq!(s.game_item, GameItem::Game);
        assert_eq!(s.per_defender, 1);
        assert_eq!(s.net(0, 0), 2);
    }

    #[test]
    fn hearts_seven_with_doubled_seven() {
        let mut r = round(Contract::Seven, Suit::Hearts);
        r.seven_announced = true;
        r.flek_seven = 1;
        r.sharp_points = [60, 20, 0];
        let t7 = Card::new(Suit::Hearts, Rank::Seven);
        last_trick(&mut r, 0, 0, [t7, Card::from_id(9), Card::from_id(10)]);
        let s = settle(&r);
        // 2 × (game 1 + seven 2·2).
        assert_eq!(s.per_defender, 10);
    }

    #[test]
    fn hundred_seven_example() {
        let mut r = round(Contract::HundredSeven, Suit::Acorns);
        r.seven_announced = true;
        r.sharp_points = [80, 0, 0];
        r.marriage_points = [40, 0, 0];
        let t7 = Card::new(Suit::Acorns, Rank::Seven);
        last_trick(&mut r, 0, 0, [t7, Card::from_id(9), Card::from_id(10)]);
        let s = settle(&r);
        // 90 + 40 = 130: 4 · 2^3 = 32, plus the seven 2.
        assert_eq!(s.game_item, GameItem::Hundred { points: 130 });
        assert_eq!(s.per_defender, 34);
    }

    #[test]
    fn hundred_lost_doubles_per_ten_over_marriage() {
        let mut r = round(Contract::Hundred, Suit::Acorns);
        r.sharp_points = [30, 40, 0];
        r.marriage_points = [40, 20, 0];
        last_trick(
            &mut r,
            0,
            0,
            [Card::from_id(8), Card::from_id(9), Card::from_id(10)],
        );
        let s = settle(&r);
        // Defenders 50 + 20 marriage, built on 40: (70 - 40) / 10 = 3 doublings.
        assert_eq!(s.per_defender, -32);
    }

    #[test]
    fn silent_hundred_against() {
        let mut r = round(Contract::Game, Suit::Acorns);
        r.sharp_points = [0, 80, 0];
        r.marriage_points = [0, 20, 0];
        last_trick(
            &mut r,
            1,
            1,
            [Card::from_id(8), Card::from_id(9), Card::from_id(10)],
        );
        let s = settle(&r);
        assert_eq!(
            s.game_item,
            GameItem::SilentHundred {
                points: 110,
                against: true
            }
        );
        assert_eq!(s.per_defender, -4);
    }

    #[test]
    fn killed_seven_counts_as_lost() {
        let mut r = round(Contract::Seven, Suit::Bells);
        r.seven_announced = true;
        r.sharp_points = [60, 20, 0];
        let t7 = Card::new(Suit::Bells, Rank::Seven);
        last_trick(
            &mut r,
            0,
            1,
            [t7, Card::new(Suit::Bells, Rank::Ace), Card::from_id(10)],
        );
        let s = settle(&r);
        assert!(s.seven.unwrap().killed);
        assert_eq!(s.seven_money, -2);
    }

    #[test]
    fn betl_and_unplayed_games() {
        let mut r = round(Contract::Betl, Suit::Bells);
        r.flek_game = 2;
        r.lost = true;
        assert_eq!(settle(&r).per_defender, -20);

        let mut r = round(Contract::Seven, Suit::Bells);
        r.not_played = true;
        r.flek_game = 1;
        assert_eq!(settle(&r).per_defender, 0);

        let mut r = round(Contract::Game, Suit::Hearts);
        r.not_played = true;
        assert_eq!(settle(&r).per_defender, 2);
    }
}
