//! User settings, stored as `key=value` lines in the platform config directory
//! (in `localStorage` in the browser).

use crate::gfx::Pattern;
#[cfg(not(target_arch = "wasm32"))]
use std::path::PathBuf;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Config {
    pub sound: bool,
    /// Table colour, EGA index 0..=8.
    pub table_color: u8,
    /// Table fill pattern, 1..=11 (see [`table_pattern`]).
    pub table_pattern: u8,
    /// Colour of menus and prompts, EGA index 0..=8.
    pub menu_color: u8,
    /// Playing strength of the computer players, 0..=255; 0 asks at start-up.
    pub iq: u8,
}

impl Default for Config {
    fn default() -> Config {
        Config {
            sound: true,
            table_color: 2,
            table_pattern: 1,
            menu_color: 3,
            iq: 0,
        }
    }
}

pub const PATTERN_COUNT: u8 = 11;

/// The table fill patterns selectable with "Vzor".
pub fn table_pattern(i: u8) -> Pattern {
    match i {
        2 => Pattern::HORIZONTAL,
        3 => Pattern::SLASH,
        4 => Pattern([0x07, 0x0E, 0x1C, 0x38, 0x70, 0xE0, 0xC1, 0x83]),
        5 => Pattern([0xE0, 0x70, 0x38, 0x1C, 0x0E, 0x07, 0x83, 0xC1]),
        6 => Pattern::BACKSLASH,
        7 => Pattern::HATCH,
        8 => Pattern::CROSS_HATCH,
        9 => Pattern::INTERLEAVE,
        10 => Pattern::WIDE_DOTS,
        11 => Pattern::CLOSE_DOTS,
        _ => Pattern::SOLID,
    }
}

impl Config {
    /// Restores the standard colours ("Standard" in the options).
    pub fn standard_colors(&mut self) {
        self.table_color = 2;
        self.table_pattern = 1;
        self.menu_color = 3;
    }

    pub fn to_text(&self) -> String {
        format!(
            "sound={}\ntable_color={}\ntable_pattern={}\nmenu_color={}\niq={}\n",
            self.sound as u8, self.table_color, self.table_pattern, self.menu_color, self.iq
        )
    }

    /// Parses settings; unknown keys and out-of-range values are ignored.
    pub fn from_text(text: &str) -> Config {
        let mut c = Config::default();
        for line in text.lines() {
            let Some((k, v)) = line.split_once('=') else {
                continue;
            };
            let Ok(v) = v.trim().parse::<u32>() else {
                continue;
            };
            match k.trim() {
                "sound" => c.sound = v != 0,
                "table_color" if v <= 8 => c.table_color = v as u8,
                "table_pattern" if (1..=PATTERN_COUNT as u32).contains(&v) => {
                    c.table_pattern = v as u8
                }
                "menu_color" if v <= 8 => c.menu_color = v as u8,
                "iq" if v <= 255 => c.iq = v as u8,
                _ => {}
            }
        }
        c
    }

    #[cfg(not(target_arch = "wasm32"))]
    fn path() -> Option<PathBuf> {
        let base = if cfg!(target_os = "windows") {
            std::env::var_os("APPDATA").map(PathBuf::from)
        } else if cfg!(target_os = "macos") {
            std::env::var_os("HOME").map(|h| PathBuf::from(h).join("Library/Application Support"))
        } else {
            std::env::var_os("XDG_CONFIG_HOME")
                .map(PathBuf::from)
                .or_else(|| std::env::var_os("HOME").map(|h| PathBuf::from(h).join(".config")))
        };
        base.map(|b| b.join("openflek").join("openflek.cfg"))
    }

    pub fn load() -> Config {
        Config::read().map_or_else(Config::default, |text| Config::from_text(&text))
    }

    pub fn save(&self) {
        Config::write(&self.to_text());
    }

    /// The stored settings text, if there is any.
    #[cfg(not(target_arch = "wasm32"))]
    fn read() -> Option<String> {
        std::fs::read_to_string(Config::path()?).ok()
    }

    #[cfg(not(target_arch = "wasm32"))]
    fn write(text: &str) {
        let Some(path) = Config::path() else { return };
        let result = path
            .parent()
            .map_or(Ok(()), std::fs::create_dir_all)
            .and_then(|_| std::fs::write(&path, text));
        match result {
            Ok(()) => log::info!("settings saved to {}", path.display()),
            Err(e) => log::warn!("cannot save settings to {}: {e}", path.display()),
        }
    }

    #[cfg(target_arch = "wasm32")]
    fn read() -> Option<String> {
        crate::web::storage_get(STORAGE_KEY)
    }

    #[cfg(target_arch = "wasm32")]
    fn write(text: &str) {
        crate::web::storage_set(STORAGE_KEY, text);
    }
}

/// The `localStorage` entry holding the settings in the browser.
#[cfg(target_arch = "wasm32")]
const STORAGE_KEY: &str = "openflek.cfg";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trips_through_text() {
        let c = Config {
            sound: false,
            table_color: 5,
            table_pattern: 7,
            menu_color: 1,
            iq: 200,
        };
        assert_eq!(Config::from_text(&c.to_text()), c);
    }

    #[test]
    fn rejects_out_of_range_values() {
        let c = Config::from_text("table_color=12\ntable_pattern=0\niq=999\nbogus\nsound=x");
        assert_eq!(c, Config::default());
    }

    #[test]
    fn patterns_are_distinct() {
        let all: Vec<Pattern> = (1..=PATTERN_COUNT).map(table_pattern).collect();
        for i in 0..all.len() {
            for j in i + 1..all.len() {
                assert_ne!(all[i], all[j]);
            }
        }
    }
}
