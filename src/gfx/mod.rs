//! Software rendering: an indexed-colour framebuffer and an 8x8 font.

pub mod canvas;
pub mod font;
pub mod png;

pub use canvas::{Canvas, Fill, Pattern, color};
