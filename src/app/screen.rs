//! The window: presents the 640x480 framebuffer scaled to fit, collects
//! keyboard and mouse input, and plays PC-speaker style tunes. A headless
//! variant with a simulated clock runs the same game without a window.

use crate::gfx::Canvas;
use crate::sound::Tone;
#[cfg(feature = "sound")]
use crate::sound::render_wav;
#[cfg(feature = "sound")]
use macroquad::audio::{PlaySoundParams, Sound, load_sound_from_bytes, play_sound};
use macroquad::prelude::*;
#[cfg(feature = "sound")]
use std::collections::HashMap;
use std::collections::VecDeque;

pub const WIDTH: i32 = 640;
pub const HEIGHT: i32 = 480;

/// Simulated frame length of the headless backend.
const HEADLESS_FRAME: f64 = 1.0 / 60.0;

/// Shortest frame in the window: caps the loop at 60 frames per second.
const MIN_FRAME: f64 = 1.0 / 60.0;

#[cfg(not(target_arch = "wasm32"))]
fn sleep(secs: f64) {
    std::thread::sleep(std::time::Duration::from_secs_f64(secs));
}

/// The browser paces frames itself.
#[cfg(target_arch = "wasm32")]
fn sleep(_secs: f64) {}

/// A key press, as the game understands it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Key {
    Left,
    Right,
    Up,
    Down,
    Enter,
    Esc,
    Home,
    End,
    PageUp,
    PageDown,
    F1,
    F10,
    Char(char),
    /// Left mouse button at a framebuffer position.
    Click(i32, i32),
}

enum Backend {
    Window {
        texture: Texture2D,
        /// Canvas generation last uploaded to the texture.
        uploaded: Option<u64>,
        last_mouse: (f32, f32),
        /// Decoded tunes, so each is rendered and loaded only once.
        #[cfg(feature = "sound")]
        sounds: HashMap<Vec<Tone>, Sound>,
        /// When the previous frame was presented, for the frame cap.
        last_frame: f64,
    },
    Headless {
        time: f64,
    },
}

pub struct Screen {
    pub canvas: Canvas,
    backend: Backend,
    rgba: Vec<u8>,
    keys: VecDeque<Key>,
    pub sound_on: bool,
    /// Last mouse position in framebuffer coordinates, if it moved.
    mouse: Option<(i32, i32)>,
    /// Testing aid: shorten waits.
    pub autoplay: bool,
    /// Testing aid: directory for periodic screenshots.
    pub shots: Option<String>,
    shot_no: u32,
    next_shot: f64,
    /// Testing aid: a key to press once the clock reaches the given time.
    scheduled_key: Option<(f64, Key)>,
}

impl Screen {
    fn with_backend(backend: Backend) -> Screen {
        Screen {
            canvas: Canvas::new(WIDTH, HEIGHT),
            backend,
            rgba: Vec::new(),
            keys: VecDeque::new(),
            sound_on: true,
            mouse: None,
            autoplay: false,
            shots: None,
            shot_no: 0,
            next_shot: 0.0,
            scheduled_key: None,
        }
    }

    /// A screen shown in the macroquad window.
    pub fn window() -> Screen {
        let texture = Texture2D::from_rgba8(
            WIDTH as u16,
            HEIGHT as u16,
            &vec![0; (WIDTH * HEIGHT * 4) as usize],
        );
        texture.set_filter(FilterMode::Nearest);
        Screen::with_backend(Backend::Window {
            texture,
            uploaded: None,
            last_mouse: (-1.0, -1.0),
            #[cfg(feature = "sound")]
            sounds: HashMap::new(),
            last_frame: 0.0,
        })
    }

    /// A screen without a window; time advances one frame per `frame` call.
    pub fn headless() -> Screen {
        Screen::with_backend(Backend::Headless { time: 0.0 })
    }

    /// Seconds since start (simulated when headless).
    pub fn now(&self) -> f64 {
        match &self.backend {
            Backend::Window { .. } => get_time(),
            Backend::Headless { time } => *time,
        }
    }

    fn viewport() -> (f32, f32, f32) {
        let scale = (screen_width() / WIDTH as f32).min(screen_height() / HEIGHT as f32);
        let (w, h) = (WIDTH as f32 * scale, HEIGHT as f32 * scale);
        (
            (screen_width() - w) / 2.0,
            (screen_height() - h) / 2.0,
            scale,
        )
    }

    fn to_canvas((mx, my): (f32, f32)) -> (i32, i32) {
        let (ox, oy, s) = Screen::viewport();
        (((mx - ox) / s) as i32, ((my - oy) / s) as i32)
    }

    /// Shows the framebuffer and waits for the next frame, gathering input.
    pub async fn frame(&mut self) {
        let generation = self.canvas.generation();
        let stale = match &self.backend {
            Backend::Window { uploaded, .. } => *uploaded != Some(generation),
            Backend::Headless { .. } => false,
        };
        let shot_due = self.shots.is_some() && self.now() >= self.next_shot;
        if stale || shot_due {
            self.canvas.to_rgba(&mut self.rgba);
        }
        if let Some(dir) = self.shots.clone()
            && shot_due
        {
            self.next_shot = self.now() + 1.0;
            self.shot_no += 1;
            self.save_png(&format!("{dir}/shot_{:04}.png", self.shot_no));
        }
        match &mut self.backend {
            Backend::Window {
                texture,
                uploaded,
                last_frame,
                ..
            } => {
                if stale {
                    texture.update_from_bytes(WIDTH as u32, HEIGHT as u32, &self.rgba);
                    *uploaded = Some(generation);
                }
                clear_background(BLACK);
                let (ox, oy, s) = Screen::viewport();
                draw_texture_ex(
                    texture,
                    ox,
                    oy,
                    WHITE,
                    DrawTextureParams {
                        dest_size: Some(vec2(WIDTH as f32 * s, HEIGHT as f32 * s)),
                        ..Default::default()
                    },
                );
                next_frame().await;
                // Without working vsync the loop would spin a whole core.
                let spent = get_time() - *last_frame;
                if spent < MIN_FRAME {
                    sleep(MIN_FRAME - spent);
                }
                *last_frame = get_time();
                self.poll();
            }
            Backend::Headless { time } => *time += HEADLESS_FRAME,
        }
        if let Some((at, key)) = self.scheduled_key
            && self.now() >= at
        {
            self.scheduled_key = None;
            self.keys.push_back(key);
        }
    }

    /// Testing aid: presses `key` once `secs` seconds have passed.
    pub fn press_after(&mut self, secs: f64, key: Key) {
        self.scheduled_key = Some((self.now() + secs, key));
    }

    fn poll(&mut self) {
        let mapping = [
            (KeyCode::Left, Key::Left),
            (KeyCode::Right, Key::Right),
            (KeyCode::Up, Key::Up),
            (KeyCode::Down, Key::Down),
            (KeyCode::Enter, Key::Enter),
            (KeyCode::KpEnter, Key::Enter),
            (KeyCode::Escape, Key::Esc),
            (KeyCode::Home, Key::Home),
            (KeyCode::End, Key::End),
            (KeyCode::PageUp, Key::PageUp),
            (KeyCode::PageDown, Key::PageDown),
            (KeyCode::F1, Key::F1),
            (KeyCode::F10, Key::F10),
        ];
        for (code, key) in mapping {
            if is_key_pressed(code) {
                self.keys.push_back(key);
            }
        }
        while let Some(ch) = get_char_pressed() {
            if ch == ' ' || ch.is_alphanumeric() {
                self.keys.push_back(Key::Char(ch));
            }
        }
        let pos = mouse_position();
        if let Backend::Window { last_mouse, .. } = &mut self.backend
            && pos != *last_mouse
        {
            *last_mouse = pos;
            self.mouse = Some(Screen::to_canvas(pos));
        }
        if is_mouse_button_pressed(MouseButton::Left) {
            let (x, y) = Screen::to_canvas(pos);
            self.keys.push_back(Key::Click(x, y));
        }
    }

    /// Whether the left mouse button is held (always false headless).
    pub fn mouse_down(&self) -> bool {
        matches!(self.backend, Backend::Window { .. }) && is_mouse_button_down(MouseButton::Left)
    }

    pub fn take_key(&mut self) -> Option<Key> {
        self.keys.pop_front()
    }

    pub fn has_key(&self) -> bool {
        !self.keys.is_empty()
    }

    pub fn flush_keys(&mut self) {
        self.keys.clear();
    }

    /// Takes the last mouse movement, if any.
    pub fn take_mouse(&mut self) -> Option<(i32, i32)> {
        self.mouse.take()
    }

    /// Waits up to `secs` seconds or until a key arrives; the key is not consumed.
    pub async fn wait(&mut self, secs: f64) {
        let secs = if self.autoplay { secs.min(0.2) } else { secs };
        let end = self.now() + secs;
        while self.now() < end && !self.has_key() {
            self.frame().await;
        }
    }

    /// Waits for a key or `secs` seconds, swallowing keys pressed before and during the wait.
    pub async fn wait_for_key(&mut self, secs: f64) {
        self.flush_keys();
        self.wait(secs).await;
        self.flush_keys();
    }

    /// Waits `secs` seconds regardless of input.
    pub async fn pause(&mut self, secs: f64) {
        let secs = if self.autoplay { secs.min(0.05) } else { secs };
        let end = self.now() + secs;
        while self.now() < end {
            self.frame().await;
        }
    }

    /// Ends the program. A page cannot close itself, so in the browser this
    /// reloads it and keeps the last screen up until the page goes away.
    pub async fn exit(&mut self) {
        #[cfg(not(target_arch = "wasm32"))]
        std::process::exit(0);
        #[cfg(target_arch = "wasm32")]
        {
            crate::web::reload();
            loop {
                self.frame().await;
            }
        }
    }

    /// Plays a tune without waiting for it to finish.
    #[cfg(feature = "sound")]
    pub async fn play(&mut self, tune: &[Tone]) {
        if !self.sound_on || tune.is_empty() {
            return;
        }
        let Backend::Window { sounds, .. } = &mut self.backend else {
            return;
        };
        if !sounds.contains_key(tune) {
            // Tunes come from small fixed sets; the cap only guards against growth.
            if sounds.len() >= 256 {
                sounds.clear();
            }
            let Ok(sound) = load_sound_from_bytes(&render_wav(tune)).await else {
                return;
            };
            sounds.insert(tune.to_vec(), sound);
        }
        play_sound(
            &sounds[tune],
            PlaySoundParams {
                looped: false,
                volume: 0.35,
            },
        );
    }

    /// Built without sound: tunes are ignored.
    #[cfg(not(feature = "sound"))]
    pub async fn play(&mut self, _tune: &[Tone]) {}

    fn save_png(&self, path: &str) {
        crate::gfx::png::save(&self.canvas, 1, path);
    }
}
