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

/// Every switch by its long name, and whether a value follows it. `parse`
/// and `from_query` both look names up here.
const SWITCHES: &[(&str, bool)] = &[
    ("quick", false),
    ("silent", false),
    ("skip-intro", false),
    ("autoplay", false),
    ("headless", false),
    ("iq", true),
    ("seed", true),
    ("shots", true),
    ("deals", true),
];

impl Options {
    pub fn parse(args: &[String]) -> Result<Options, String> {
        let mut o = Options::default();
        let mut it = args.iter();
        while let Some(a) = it.next() {
            let name = match a.as_str() {
                "-q" => "quick",
                "-s" => "silent",
                _ => a.strip_prefix("--").unwrap_or_default(),
            };
            let Some(takes_value) = takes_value(name) else {
                return Err(format!("unknown option {a}"));
            };
            let value = if takes_value {
                it.next().ok_or_else(|| format!("--{name} needs a value"))?
            } else {
                ""
            };
            o.set(name, value)?;
        }
        Ok(o)
    }

    /// Applies one switch from [`SWITCHES`]; flags ignore `value`.
    fn set(&mut self, name: &str, value: &str) -> Result<(), String> {
        match name {
            "quick" => self.quick = true,
            "silent" => self.no_sound = true,
            "skip-intro" => self.skip_intro = true,
            "autoplay" => self.autoplay = true,
            "headless" => self.headless = true,
            "iq" => self.iq = Some(value.parse().map_err(|_| "--iq takes 0..255")?),
            "seed" => self.seed = Some(value.parse().map_err(|_| "--seed takes a number")?),
            "shots" => self.shots = Some(value.to_owned()),
            "deals" => self.deals = Some(value.parse().map_err(|_| "--deals takes a number")?),
            other => return Err(format!("unknown option --{other}")),
        }
        Ok(())
    }

    /// Reads the switches from a URL query string such as `?quick&iq=60`,
    /// which stands in for the command line in the browser.
    ///
    /// Names and values are percent-decoded. A flag may be written `quick`
    /// or `quick=1`; `quick=0` leaves it off. Unknown names are ignored, so
    /// a link can carry extra parameters, and a bad pair is logged and
    /// skipped without dropping the switches next to it.
    pub fn from_query(query: &str) -> Options {
        let mut o = Options::default();
        for pair in query.trim_start_matches('?').split('&') {
            let (name, value) = pair.split_once('=').unwrap_or((pair, ""));
            let (name, value) = (query_decode(name), query_decode(value));
            let result = match takes_value(&name) {
                None => continue,
                Some(true) if value.is_empty() => Err(format!("--{name} needs a value")),
                Some(true) => o.set(&name, &value),
                Some(false) => match value.to_ascii_lowercase().as_str() {
                    "" | "1" | "true" | "yes" | "on" => o.set(&name, ""),
                    "0" | "false" | "no" | "off" => Ok(()),
                    _ => Err(format!("--{name} takes no value")),
                },
            };
            if let Err(e) = result {
                log::warn!("ignoring {pair:?} in the query: {e}");
            }
        }
        o
    }
}

/// Whether switch `name` takes a value, or `None` if there is no such switch.
fn takes_value(name: &str) -> Option<bool> {
    SWITCHES
        .iter()
        .find(|&&(n, _)| n == name)
        .map(|&(_, value)| value)
}

/// Percent-decodes one query component. `+` is a space, as in a form query.
fn query_decode(raw: &str) -> String {
    let spaced = raw.replace('+', " ");
    let bytes = spaced.as_bytes();
    let mut out = Vec::with_capacity(bytes.len());
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' && i + 2 < bytes.len() {
            let hex = std::str::from_utf8(&bytes[i + 1..i + 3]).unwrap_or("");
            if let Ok(v) = u8::from_str_radix(hex, 16) {
                out.push(v);
                i += 3;
                continue;
            }
        }
        out.push(bytes[i]);
        i += 1;
    }
    String::from_utf8_lossy(&out).into_owned()
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
    fn every_switch_is_handled() {
        for &(name, _) in SWITCHES {
            assert!(Options::default().set(name, "1").is_ok(), "--{name}");
        }
        assert!(Options::parse(&args("quick")).is_err());
    }

    #[test]
    fn parses_query_string() {
        let o = Options::from_query("?quick&iq=60&seed=7&skip-intro=");
        assert!(o.quick && o.skip_intro && !o.no_sound);
        assert_eq!((o.iq, o.seed), (Some(60), Some(7)));
        let o = Options::from_query("");
        assert!(!o.quick && o.iq.is_none());
        // Tracking parameters and bad pairs leave the other switches alone.
        let o = Options::from_query("?quick=1&fbclid=abc&iq=%36%30&silent=0&seed");
        assert!(o.quick && !o.no_sound && o.seed.is_none());
        assert_eq!(o.iq, Some(60));
        let o = Options::from_query("?iq=300&quick=TRUE&silent=banana&shots");
        assert!(o.quick && !o.no_sound && o.iq.is_none() && o.shots.is_none());
    }

    #[test]
    fn decodes_query_components() {
        assert_eq!(query_decode("a+b%20c"), "a b c");
        assert_eq!(query_decode("%C4%9B"), "ě");
        assert_eq!(query_decode("%2B%3D%26"), "+=&");
        // Malformed escapes stay as they are.
        assert_eq!(query_decode("%"), "%");
        assert_eq!(query_decode("%4"), "%4");
        assert_eq!(query_decode("%zz%4"), "%zz%4");
        assert_eq!(query_decode("%C4"), "\u{FFFD}");
    }
}
