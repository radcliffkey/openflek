# AGENTS.md

Instructions for coding agents working on OpenFlek. Read [README.md](README.md)
for what the game is, the command-line switches and the rules as implemented;
this file covers what you need to change the code safely.

OpenFlek is a Rust remake of FLEK!, the 1991–1992 Czech DOS *volený mariáš*
game. It is a single crate (library + `openflek` binary) on macroquad.

## Commands

```bash
cargo build                         # debug build (opt-level 1, deps at 2)
cargo test                          # all unit tests + headless integration test, ~1 s
cargo clippy --all-targets          # must stay warning-free
cargo fmt                           # default rustfmt settings, no config file
cargo run -- --headless --deals 5 --seed 1 --iq 60   # play deals without a window
cargo run --example card_sheet -- out.png 2           # render the deck to a PNG
```

- Rust 1.85+, edition 2024.
- The default `sound` feature needs the ALSA dev package on Linux
  (`libasound2-dev`). If it is missing, use `--no-default-features` for
  build, test and clippy.
- `RUST_LOG=debug` shows a summary of every deal in a headless run.
- A windowed run needs a display; you usually cannot use it. Use `--headless`
  to check game flow, and `--autoplay --shots DIR` (windowed) only if a
  display is available and you need screenshots.

Before you hand work back, run `cargo fmt`, `cargo clippy --all-targets` and
`cargo test`.

## Layout

| path | contents |
|---|---|
| `src/game/` | rules engine, no UI: `cards`, `round` (deck, deal, contract state, trick rules), `analysis` (hand evaluation), `settle` (scoring), `ai` (computer players), `rng` |
| `src/gfx/` | indexed-colour `Canvas` (the screen is 640×480) with BGI-like primitives, 8×8 font with Czech letters, PNG writer |
| `src/art/` | card sprites: faces decoded from `deck_data.bin`, backs and frame drawn in code |
| `scripts/deck_gen/` | Python generator for the card faces in `deck_data.bin` |
| `src/app/` | game flow (`flow`), dialogs (`ui`), table drawing, options, title screen, all UI strings (`text`) |
| `src/config.rs`, `src/sound.rs` | settings file; square-wave PC-speaker sounds |
| `tests/headless.rs` | plays full deals through the real flow without a window |

Only `src/app/mod.rs`, `src/app/screen.rs`, `src/gfx/png.rs` and `src/main.rs`
use macroquad. Keep `src/game/` free of macroquad and other UI code.

## How the code fits together

- The game flow is `async`. `Screen` either drives a macroquad window or runs
  headless, where it never suspends and `app::block_on` polls it to the end.
  Anything that waits for input or time must go through `Screen`, so the
  headless path keeps working.
- In a headless run the computer plays seat 0 too. Seat 0 is the human,
  seats 1 and 2 the computer; play goes 0 → 1 → 2.
- Money is an `i64` in units of 0.10 Kč. Use `text::money` to display it.
- All randomness comes from `game::rng::Rng`, the Turbo Pascal LCG, so a seed
  reproduces a whole game. Don't add `rand`, time-based seeds or other
  randomness to game logic.
- The AI plays double-dummy (it sees every hand). This copies the 1992
  original on purpose. Don't "fix" it.
- Headless runs don't read or write `openflek.cfg`. Tests must stay headless
  so they never touch the user's settings.

## Faithfulness to the original

The rules, scoring, AI, screen layout, dialogs and sounds reproduce the 1992
program. When a rule looks odd, assume it is how the original works. Don't
change it to match another mariáš variant unless you are asked to. If you
change behaviour, update the "Rules as implemented" section or the switch
table in the README.

## Assets

- `src/art/deck_data.bin` holds the card faces as a 4-bit bitmap.
  `art::cards` embeds it with `include_bytes!`, and a compile-time check requires
  exactly 97,600 bytes (32 faces of 61×100 pixels, two pixels per byte).
  Don't remove, regenerate or replace it unless you are asked to.
- The faces are drawn by the Python generator in `scripts/deck_gen` (plain
  Python 3). `python3 scripts/deck_gen/build_sheet.py` rewrites
  `deck_data.bin`; check the result with the `card_sheet` example below. The
  card back is drawn by `back_pixel` in `art::cards`, not by the generator.
- After changing card rendering, regenerate the README image:
  `cargo run --example card_sheet -- docs/card_sheet.png 2`.

## Conventions

- Code, comments and identifiers are in English, with British spelling
  (`colour`). Text the player sees is Czech and lives in `src/app/text.rs`.
  `gfx::font` draws a fixed set of Czech letters, so check new characters
  against it.
- Every module starts with a `//!` doc comment saying what it holds. Public
  items get a `///` comment when the name doesn't say enough. Comments
  explain rules and reasons, not the code line by line.
- Unit tests live in a `#[cfg(test)] mod tests` at the bottom of the file
  they test. Rule, scoring and AI changes need a unit test.
- `tests/headless.rs` uses fixed seeds chosen so that seat 0 hits every
  decision (betl, durch, seven, re, flek). If an AI change breaks
  `human_seat_takes_every_kind_of_decision`, pick new seeds that cover every
  case again. Don't weaken the assertions.
- Avoid `unsafe` and avoid `unwrap()` outside tests.
- Commit messages are short, lowercase summaries (see `git log`).
