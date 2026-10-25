use macroquad::window::Conf;
use openflek::app::{self, Options};

fn window_conf() -> Conf {
    Conf {
        window_title: "OpenFlek".to_owned(),
        window_width: 1280,
        window_height: 960,
        // The page fills the browser window, so the framebuffer has to match
        // the device pixels or the browser blurs the nearest-neighbour scale.
        // The desktop window stays at a fixed size.
        high_dpi: cfg!(target_arch = "wasm32"),
        ..Default::default()
    }
}

#[cfg(not(target_arch = "wasm32"))]
fn main() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();
    let args: Vec<String> = std::env::args().skip(1).collect();
    let opts = match Options::parse(&args) {
        Ok(opts) => opts,
        Err(e) => {
            log::error!("{e}");
            log::error!(
                "usage: openflek [--quick] [--silent] [--skip-intro] [--iq 0..255] [--seed N] \
                 [--autoplay] [--headless] [--deals N] [--shots DIR]"
            );
            std::process::exit(2);
        }
    };
    if opts.headless {
        app::block_on(app::run(opts));
    } else {
        macroquad::Window::from_config(window_conf(), app::run(opts));
    }
}

/// In the browser the switches come from the query string, e.g. `?quick&iq=60`.
#[cfg(target_arch = "wasm32")]
fn main() {
    use openflek::web;
    web::init_logger();
    let mut opts = Options::from_query(&web::query());
    // A page has no headless mode and no directory to save screenshots in.
    opts.headless = false;
    opts.shots = None;
    macroquad::Window::from_config(window_conf(), async move {
        app::run(opts).await;
        web::reload();
    });
}
