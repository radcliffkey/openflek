//! All texts shown by the game. A `|` separates alternatives; one is picked at
//! random each time, so the computer players do not repeat themselves.

use crate::game::cards::{Card, Rank, Suit};
use crate::game::rng::Rng;

pub fn pick(rng: &mut Rng, s: &'static str) -> &'static str {
    let n = s.matches('|').count() as u32 + 1;
    s.split('|').nth(rng.below(n) as usize).unwrap_or(s)
}

pub const TITLE_BY: &str = "AI Slop software";
pub const TITLE_PRESENTS: &str = "uvádí";
pub const TITLE: &str = "FLEK!";
pub const VERSION: &str = "verze 0.2.0";
pub const PRESS_ANY_KEY: &str = "Stiskni libovolnou klávesu";
pub const PRESS_ANYTHING: &str = "Stiskni cokoli";
pub const NOT_UNDERSTOOD: &str = "Nerozumím";
pub const QUIT: &str = "Skončit";
pub const YES: &str = "Ano";
pub const NO: &str = " Ne ";
pub const OK: &str = " OK ";
pub const ANOTHER_GAME: &str = "Ještě jednu|Další kolo|Hrajeme dál|Rozdáme znovu|Pokračujeme";
pub const CREDITS: &str = "Díky za hru!|Zase někdy u karet!|Ať vám to příště padá!";
pub const CREDITS_LINE: &str = "OpenFlek - otevřená předělávka hry FLEK! (1992)";

pub const CHOOSE_TRUMPS: &str = "Zvol trumfy|Vyber trumf|Trumfy jsou na tobě";
pub const DISCARD_FIRST: &str = "Odhoď do talonu|Dvě karty do talonu|Zahoď dvě karty";
pub const DISCARD_SECOND: &str = "A ještě jednu|Ještě jednu kartu|Ještě jednu";
pub const LEAD: &str = "Vynášíš|Jsi na tahu|Prosím, vynášej";

pub const DISCARD_KIND: &str = "Na co budeš odhazovat ?";
pub const DISCARD_FOR_SUIT_GAME: &str = "Hra,100,107";
pub const DISCARD_FOR_BETL: &str = "Betl,Durch";
pub const WHAT_NOW: &str = "Co budeš hrát|Tak co to bude|Co si vezmeš";
pub const FINAL_CONTRACT: &str = "Co tedy hraješ ?";
pub const CONTRACT_BUTTONS: [&str; 4] = ["hra", " 7 ", "100", "107"];
pub const BETL: &str = "Betl";
pub const DURCH: &str = "Durch";

pub const ASK_SUIT: &str = "BARVA ?|Jak barva ?|Barva ?";
pub const YOUR_SAY: &str = "Co ty na to ?|Tvůj názor ?|Co říkáš ?";
pub const GOOD: &str = "Dobrá";
pub const BAD: &str = "Špatná";
pub const GOOD_SAID: &str = "Dobrá|Barva dobrá|Nemám námitek|Mlčím|Ať je|Platí";
pub const BAD_SAID: &str = "Špatná|Barva špatná|To nepůjde";
pub const ASK_BETL: &str = "Jaký betl ?|Co betl ?|A betl ?";
pub const BETL_GOOD: &str = "Dobrý";
pub const BETL_BAD: &str = "Špatný";
pub const FLEK: &str = "Flek";
pub const ASK_ALL: &str = "Tak co|Poslouchám|Nu|Čekám|Ozvěte se";
pub const ADDRESS: &str = "pánové|přátelé|kolegové|vážení|hoši";

pub const ON_GAME: &str = "Na hru";
pub const ON_HUNDRED: &str = "Na 100";
pub const ON_SEVEN: &str = "Na 7";
pub const SEVEN_AGAINST: &str = "7 proti";
pub const BOTH: &str = "Obojí";
pub const RAISE_GAME: &str = "Dáš si víc";
pub const RAISE_SEVEN: &str = "Sedmu víc";
pub const RAISE_BUTTONS: [&str; 4] = ["Ne", "Hra výš", "7 výš", "Obojí"];

pub const SILENT: &str = "Mlčím|Já nic|Nic|Bez flekování|Pass|Ani slovo|Nechám to být";
pub const FLEK_SAID: &str = "FLEK !";
pub const FLEK_GAME_SAID: &str = "Flek na hru|Na hru";
pub const FLEK_SEVEN_SAID: &str = "Flek na sedmu|Na sedmu";
pub const SEVEN_AGAINST_SAID: &str = "Sedma proti|Sedmu proti";
pub const BOTH_SAID: &str = "Obojí|Na všechno|Hru i sedmu";
pub const BOTH_SEVEN_AGAINST_SAID: &str = "Flek a sedma proti";
pub const RE_SAID: &str = "RE !";
pub const TUTTI_SAID: &str = "TUTTI !";
/// Calls for doubling beyond tutti, in the traditional order.
pub const HIGHER_SAID: [&str; 5] = ["BOTY !", "KALHOTY !", "KABÁT !", "KLOBOUK !", "KAPUT !"];
pub const RE_SEVEN_SAID: &str = "Sedma výš|Na sedmu znovu";
pub const RE_BOTH_SAID: &str = "Obojí výš|Všechno výš";
pub const NO_RE_SAID: &str = "Dobře|Beru na vědomí|Nechám to tak";
pub const STOP_SAID: &str = "Chytřejší ustoupí|Už dost|Nebudu se hádat";

pub const THINKING: &str = "Moment|Okamžik|Hmm|Přemýšlím|Počkej chvilku|Jak to jen je";

pub const BETL_LOST: &str = "A je po betlu !|Konec !|Hotovo !";
pub const DURCH_LOST: &str = "Durch padl !|Konec !|Hotovo !";
pub const BETL_WON: &str = "Už nic neberu|Betl je doma|Nic víc mě nechytí";
pub const CLAIM: &str = "Zbytek je můj|Ostatní beru|Karty na stůl|Zbytek sedí";

pub const REBUKE: &str =
    "To nejde|Tahle ne|Pozor, to by byl renonc|Tudy cesta nevede|Ale ale|Kdepak";
pub const REBUKE_KING: &str = "Nejdřív svrška|Hláška se hlásí svrškem";
pub const SHARP_TO_TALON: &str = "desítku ani eso do talonu!";
pub const NOT_ALLOWED: &str = "to se nesmí|to nepovolím";
pub const YOU_HAVE: &str = "máš přece|vždyť máš|zkus";
pub const HIGHER: &str = "výš";
pub const KEEP_SEVEN: &str = "sedmu si nech na konec";

pub const SETTLEMENT: &str = "Vyúčtování:";
pub const AS_IF_PLAYED: &str = "Jako by se hrálo:";
pub const GAME: &str = "Hra";
pub const PLAIN_GAME: &str = "Obyčejná hra";
pub const DOUBLED_GAME: &str = "Flekovaná hra";
pub const SEVEN: &str = "Sedma";
pub const SEVEN_LOST: &str = "Prohraná sedma";
pub const SILENT_SEVEN: &str = "Tichá sedma";
pub const KILLED: &str = ", zabitá";
pub const AGAINST: &str = " proti";
pub const HUNDRED: &str = "Stovka";
pub const HUNDRED_LOST: &str = "Prohraná stovka";
pub const SILENT_HUNDRED: &str = "Tichá";
pub const TOTAL: &str = "Celkem:";
pub const TOTAL_HEARTS: &str = "V červených dvojnásob:|Červená je dražší:";
pub const FREE: &str = "Nikdo nic|Je to zadarmo";
pub const YOU_WON: &str = "Vyhrál jsi|Získal jsi";
pub const YOU_LOST: &str = "Prohrál jsi|Stálo tě to|Přišel jsi o";
pub const YOU_HAVE_NOW: &str = "Máš celkem";
pub const CURRENCY: &str = "Kč";
pub const BROKE: &str = "Jsi na mizině!|Peníze došly!";
pub const BROKE_2: &str = "Zkus raději šachy|Příště to vyjde|Karty dnes nepřály";
pub const SHOW_TRICKS: &str = "Ukázat průběh hry|Chceš vidět štychy";
pub const POINTS: &str = "body";

pub const OPTIONS: [&str; 7] = ["Zvuky", "Barva", "Vzor", "Menu", "Standard", "IQ", "Uložit"];
pub const IQ_TITLE: &str = "Jak chytří mají být soupeři ?";
pub const IQ_SCALE: &str = "hloupí . . . . . . . . . chytří";

pub const SUIT_NAMES: [&str; 4] = ["žaludy", "zelené", "kule", "červené"];
pub const TRUMPS: &str = "trumfy";
/// A trump card picked blind from the five unseen cards.
pub const FROM_THE_PEOPLE: &str = "Z lidu";

/// Contract label shown next to the declarer.
pub fn contract_label(c: crate::game::round::Contract) -> &'static str {
    use crate::game::round::Contract::*;
    match c {
        Game => "hra",
        Seven => "7",
        Hundred => "100",
        HundredSeven => "107",
        Betl => "BETL",
        Durch => "DURCH",
    }
}

/// The card's Czech name, e.g. "žaludský svršek".
pub fn card_name(card: Card) -> String {
    let adjective = match card.suit() {
        Suit::Acorns => "žaludsk",
        Suit::Leaves => "zelen",
        Suit::Bells => "kulov",
        Suit::Hearts => "červen",
    };
    let (ending, noun) = match card.rank() {
        Rank::Seven => ("á", "sedma"),
        Rank::Eight => ("á", "osma"),
        Rank::Nine => ("á", "devítka"),
        Rank::Ten => ("á", "desítka"),
        Rank::Under => ("ý", "spodek"),
        Rank::Over => ("ý", "svršek"),
        Rank::King => ("ý", "král"),
        Rank::Ace => ("é", "eso"),
    };
    format!("{adjective}{ending} {noun}")
}

/// Money in units of 0.10 Kč as "12.30 Kč".
pub fn money(units: i64) -> String {
    let abs = units.unsigned_abs();
    let sign = if units < 0 { "-" } else { "" };
    format!("{sign}{}.{}0 {CURRENCY}", abs / 10, abs % 10)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pick_returns_one_alternative() {
        let mut rng = Rng::new(1);
        for _ in 0..20 {
            let s = pick(&mut rng, "a|b|c");
            assert!(["a", "b", "c"].contains(&s));
        }
        assert_eq!(pick(&mut rng, "single"), "single");
    }

    #[test]
    fn card_names_and_money() {
        assert_eq!(
            card_name(Card::new(Suit::Acorns, Rank::Over)),
            "žaludský svršek"
        );
        assert_eq!(card_name(Card::new(Suit::Hearts, Rank::Ace)), "červené eso");
        assert_eq!(money(1234), "123.40 Kč");
        assert_eq!(money(-5), "-0.50 Kč");
    }
}
