//! Browser glue for the WebAssembly build: settings in `localStorage`, the
//! page's query string, logging to the console and reloading the page. The
//! JavaScript side is the miniquad plugin in `web/openflek.js`.

use log::{Level, LevelFilter, Log, Metadata, Record};

/// Version of the JavaScript plugin this build expects.
const PLUGIN_VERSION: u32 = 1;

// Implemented in web/openflek.js. Strings cross as pointer and length into
// wasm memory; a reader returns the full UTF-8 length (copying only if it
// fits) or -1 when there is nothing to read.
#[link(wasm_import_module = "env")]
unsafe extern "C" {
    fn openflek_storage_get(key: *const u8, key_len: usize, buf: *mut u8, cap: usize) -> i32;
    fn openflek_storage_set(key: *const u8, key_len: usize, value: *const u8, value_len: usize);
    fn openflek_query(buf: *mut u8, cap: usize) -> i32;
    fn openflek_console_log(level: u32, msg: *const u8, len: usize);
    fn openflek_reload();
}

/// Lets the JavaScript loader check that `openflek.js` matches this build.
#[unsafe(no_mangle)]
pub extern "C" fn openflek_crate_version() -> u32 {
    PLUGIN_VERSION
}

/// Calls a reader, growing the buffer until the whole string fits.
fn read_string(read: impl Fn(*mut u8, usize) -> i32) -> Option<String> {
    let mut buf = vec![0u8; 256];
    loop {
        let len = usize::try_from(read(buf.as_mut_ptr(), buf.len())).ok()?;
        if len <= buf.len() {
            buf.truncate(len);
            return String::from_utf8(buf).ok();
        }
        buf.resize(len, 0);
    }
}

pub fn storage_get(key: &str) -> Option<String> {
    // SAFETY: the JavaScript side writes at most `cap` bytes into `buf`.
    read_string(|buf, cap| unsafe { openflek_storage_get(key.as_ptr(), key.len(), buf, cap) })
}

pub fn storage_set(key: &str, value: &str) {
    // SAFETY: both slices stay alive for the call, which only reads them.
    unsafe { openflek_storage_set(key.as_ptr(), key.len(), value.as_ptr(), value.len()) }
}

/// The page's query string, including the leading `?`, if any.
pub fn query() -> String {
    // SAFETY: the JavaScript side writes at most `cap` bytes into `buf`.
    read_string(|buf, cap| unsafe { openflek_query(buf, cap) }).unwrap_or_default()
}

/// A page cannot close itself; reloading starts over at the title screen.
pub fn reload() {
    // SAFETY: takes no arguments.
    unsafe { openflek_reload() }
}

/// Sends `log` records to the browser console.
struct ConsoleLogger;

impl Log for ConsoleLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= Level::Info
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            let msg = record.args().to_string();
            // SAFETY: `msg` stays alive for the call, which only reads it.
            unsafe { openflek_console_log(record.level() as u32, msg.as_ptr(), msg.len()) }
        }
    }

    fn flush(&self) {}
}

pub fn init_logger() {
    static LOGGER: ConsoleLogger = ConsoleLogger;
    if log::set_logger(&LOGGER).is_ok() {
        log::set_max_level(LevelFilter::Info);
    }
}
