//! The interactive game: screens, dialogs and the flow of play.

mod flow;
mod options;
mod screen;
mod table;
mod text;
mod title;
mod ui;

use crate::config::Config;
use crate::game::ai::Brain;
use crate::game::rng::Rng;
use crate::game::round::{Deck, next};
pub use flow::DealSummary;
use flow::Seat;
use screen::{Key, Screen};
use table::Art;

/// Command-line switches.
#[derive(Clone, Debug, Default)]
pub struct Options {
    /// Skip the waits after tricks and auto-play forced cards.
    pub quick: bool,
    pub no_sound: bool,
    /// Skip the title screen and the credits.
    pub skip_intro: bool,
    pub iq: Option<u8>,
    pub seed: Option<u32>,
    /// Let the computer play the human's seat too (for testing).
    pub autoplay: bool,
    /// Save a screenshot into this directory every second.
    pub shots: Option<String>,
    /// Run without a window (implies autoplay).
    pub headless: bool,
    /// Stop after this many deals.
    pub deals: Option<u32>,
}

impl Options {
    pub fn parse(args: &[String]) -> Result<Options, String> {
        let mut o = Options::default();
        let mut it = args.iter();
        while let Some(a) = it.next() {
            let mut value = |name: &str| {
                it.next()
                    .cloned()
                    .ok_or_else(|| format!("{name} needs a value"))
            };
            match a.as_str() {
                "-q" | "--quick" => o.quick = true,
                "-s" | "--silent" => o.no_sound = true,
                "--skip-intro" => o.skip_intro = true,
                "--autoplay" => o.autoplay = true,
                "--iq" => o.iq = Some(value("--iq")?.parse().map_err(|_| "--iq takes 0..255")?),
                "--seed" => {
                    o.seed = Some(
                        value("--seed")?
                            .parse()
                            .map_err(|_| "--seed takes a number")?,
                    )
                }
                "--shots" => o.shots = Some(value("--shots")?),
                "--headless" => o.headless = true,
                "--deals" => {
                    o.deals = Some(
                        value("--deals")?
                            .parse()
                            .map_err(|_| "--deals takes a number")?,
                    )
                }
                other => return Err(format!("unknown option {other}")),
            }
        }
        Ok(o)
    }

    /// Reads the switches from a URL query string such as `?quick&iq=60`,
    /// which stands in for the command line in the browser.
    pub fn from_query(query: &str) -> Result<Options, String> {
        let mut args = Vec::new();
        for pair in query.trim_start_matches('?').split('&') {
            let (name, value) = pair.split_once('=').unwrap_or((pair, ""));
            if name.is_empty() {
                continue;
            }
            args.push(format!("--{name}"));
            if !value.is_empty() {
                args.push(value.to_owned());
            }
        }
        Options::parse(&args)
    }
}

/// Everything the game needs while it runs.
pub struct Ctx {
    pub scr: Screen,
    pub cfg: Config,
    pub rng: Rng,
    pub brain: Brain,
    pub art: Art,
    pub deck: Deck,
    /// The human's balance in units of 0.10 Kč.
    pub money: i64,
    pub quick: bool,
    /// The table image for the current colour and pattern settings.
    pub table_bg: Option<((u8, u8), crate::gfx::Canvas)>,
    /// Card index the selection cursor starts from.
    pub last_card_index: usize,
}

fn window_clock() -> f64 {
    macroquad::time::get_time()
}

fn std_clock() -> f64 {
    static START: std::sync::OnceLock<std::time::Instant> = std::sync::OnceLock::new();
    START
        .get_or_init(std::time::Instant::now)
        .elapsed()
        .as_secs_f64()
}

/// Runs a future to completion without an event loop; the headless screen
/// never suspends, so a single poll loop suffices.
pub fn block_on<F: std::future::Future>(f: F) -> F::Output {
    use std::task::{Context, Poll, Waker};
    let mut cx = Context::from_waker(Waker::noop());
    let mut f = std::pin::pin!(f);
    loop {
        if let Poll::Ready(v) = f.as_mut().poll(&mut cx) {
            return v;
        }
    }
}

pub async fn run(opts: Options) {
    play(opts).await;
}

/// Runs the game like `run` and returns how each deal went.
pub async fn play(opts: Options) -> Vec<DealSummary> {
    // Headless runs are for testing: they ignore the user's saved settings.
    let mut cfg = if opts.headless {
        Config {
            iq: 100,
            ..Config::default()
        }
    } else {
        Config::load()
    };
    if let Some(iq) = opts.iq {
        cfg.iq = iq;
    }
    if opts.no_sound {
        cfg.sound = false;
    }
    // Milliseconds since 1970 overflow u32: keep the low bits, which change
    // every run (a plain `as u32` would saturate to the same seed each time).
    let seed = opts
        .seed
        .unwrap_or_else(|| (macroquad::miniquad::date::now() * 1000.0) as u64 as u32);
    let mut rng = Rng::new(seed);
    let deck = Deck::fresh(&mut rng);
    let mut scr = if opts.headless {
        Screen::headless()
    } else {
        Screen::window()
    };
    let autoplay = opts.autoplay || opts.headless;
    let you = if autoplay {
        Seat::Computer
    } else {
        Seat::Human
    };
    let seats = [you, Seat::Computer, Seat::Computer];
    scr.sound_on = cfg.sound && !opts.headless;
    scr.autoplay = autoplay;
    scr.shots = opts.shots.clone();
    let brain = Brain::new(
        cfg.iq,
        if opts.headless {
            std_clock
        } else {
            window_clock
        },
    );
    let mut ctx = Ctx {
        scr,
        cfg,
        rng,
        brain,
        art: Art::new(),
        deck,
        money: 1000,
        quick: opts.quick || autoplay,
        table_bg: None,
        last_card_index: 0,
    };
    log::info!("starting with seed {seed}");
    if !opts.skip_intro {
        if autoplay {
            // Leaves time for a screenshot of the title.
            ctx.scr.press_after(2.5, Key::Enter);
        }
        title::title_screen(&mut ctx).await;
    }
    if ctx.cfg.iq == 0 {
        if autoplay {
            ctx.scr.press_after(1.0, Key::Enter);
        }
        options::iq_slider(&mut ctx).await;
    }
    if !opts.headless {
        ctx.cfg.save();
    }
    let mut dealer = ctx.rng.below(3) as usize;
    let mut deals = Vec::new();
    loop {
        dealer = next(dealer);
        table::clear_table(&mut ctx);
        deals.push(flow::play_deal(&mut ctx, dealer, seats).await);
        let played = deals.len() as u32;
        log::info!("deal {played} finished, balance {}", text::money(ctx.money));
        if ctx.money <= 0 || opts.deals.is_some_and(|n| played >= n) {
            break;
        }
        if autoplay {
            continue;
        }
        let q = text::pick(&mut ctx.rng, text::ANOTHER_GAME);
        if !ui::yes_no(&mut ctx, 0, 0, q, true).await {
            break;
        }
    }
    if !opts.skip_intro {
        title::credits(&mut ctx).await;
    }
    deals
}

#[cfg(test)]
mod tests {
    use super::*;

    fn args(s: &str) -> Vec<String> {
        s.split_whitespace().map(String::from).collect()
    }

    #[test]
    fn parses_switches() {
        let o = Options::parse(&args(
            "-q --iq 120 --seed 7 --skip-intro --headless --deals 3",
        ))
        .unwrap();
        assert!(o.headless && o.deals == Some(3));
        assert!(o.quick && o.skip_intro && !o.no_sound);
        assert_eq!((o.iq, o.seed), (Some(120), Some(7)));
        assert!(Options::parse(&args("--iq 300")).is_err());
        assert!(Options::parse(&args("--bogus")).is_err());
    }

    #[test]
    fn parses_query_string() {
        let o = Options::from_query("?quick&iq=60&seed=7&skip-intro=").unwrap();
        assert!(o.quick && o.skip_intro && !o.no_sound);
        assert_eq!((o.iq, o.seed), (Some(60), Some(7)));
        assert!(Options::from_query("").is_ok_and(|o| !o.quick && o.iq.is_none()));
        assert!(Options::from_query("?iq=300").is_err());
        assert!(Options::from_query("?bogus").is_err());
    }
}
