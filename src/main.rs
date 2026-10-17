use macroquad::window::Conf;
use openflek::app::{self, Options};

fn window_conf() -> Conf {
    Conf {
        window_title: "OpenFlek".to_owned(),
        window_width: 1280,
        window_height: 960,
        high_dpi: false,
        ..Default::default()
    }
}

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
