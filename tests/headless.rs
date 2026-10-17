//! Plays complete deals through the real game flow without a window. Headless
//! runs let the computer play the human's seat too, so its decisions take
//! every branch of the flow.

use openflek::app::{DealSummary, Options, block_on, play, run};
use openflek::game::round::Contract;

fn options(seed: u32, iq: u8, deals: u32) -> Options {
    Options {
        headless: true,
        skip_intro: true,
        deals: Some(deals),
        seed: Some(seed),
        iq: Some(iq),
        ..Default::default()
    }
}

#[test]
fn deals_play_to_settlement_at_various_strengths() {
    for (seed, iq) in [(1, 1), (2, 60), (3, 150), (4, 255), (5, 30)] {
        block_on(run(options(seed, iq, 3)));
    }
}

#[test]
fn human_seat_takes_every_kind_of_decision() {
    let deals: Vec<DealSummary> = (26..=35)
        .flat_map(|seed| block_on(play(options(seed, 60, 8))))
        .collect();
    // Seat 0 as declarer / as defender, matching `what`.
    let yours =
        |what: &dyn Fn(&DealSummary) -> bool| deals.iter().any(|d| d.declarer == 0 && what(d));
    let theirs =
        |what: &dyn Fn(&DealSummary) -> bool| deals.iter().any(|d| d.declarer != 0 && what(d));
    // If the AI changes, these seeds may need replacing to keep each case covered.
    assert!(yours(&|d| d.contract == Contract::Betl), "betl");
    assert!(yours(&|d| d.contract == Contract::Durch), "durch");
    assert!(yours(&|d| d.contract.has_seven()), "seven");
    assert!(yours(&|d| d.raises[0] > 0), "re");
    assert!(theirs(&|d| d.raises[0] > 0), "flek");
}
