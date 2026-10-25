//! OpenFlek: an open-source remake of the Czech DOS card game Flek! (1992).

pub mod app;
pub mod art;
pub mod config;
pub mod game;
pub mod gfx;
pub mod sound;
#[cfg(target_arch = "wasm32")]
pub mod web;
