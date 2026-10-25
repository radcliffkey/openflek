// OpenFlek's browser glue, a miniquad plugin: settings in localStorage, the
// query string, console logging and page reload. The Rust side is src/web.rs.
// Load it after gl.js and before calling load().
"use strict";

(function () {
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    function readString(ptr, len) {
        return decoder.decode(new Uint8Array(wasm_memory.buffer, ptr, len));
    }

    // Copies `text` into the buffer if it fits and returns its UTF-8 length,
    // so the caller can retry with a bigger buffer.
    function writeString(text, ptr, cap) {
        const bytes = encoder.encode(text);
        if (bytes.length <= cap) {
            new Uint8Array(wasm_memory.buffer, ptr, bytes.length).set(bytes);
        }
        return bytes.length;
    }

    miniquad_add_plugin({
        name: "openflek",
        version: 1,
        register_plugin: function (importObject) {
            const env = importObject.env;

            // localStorage throws when the browser blocks site data.
            env.openflek_storage_get = function (keyPtr, keyLen, ptr, cap) {
                let value = null;
                try {
                    value = localStorage.getItem(readString(keyPtr, keyLen));
                } catch (e) {
                    console.warn("cannot read settings:", e);
                }
                return value === null ? -1 : writeString(value, ptr, cap);
            };

            env.openflek_storage_set = function (keyPtr, keyLen, valuePtr, valueLen) {
                try {
                    localStorage.setItem(readString(keyPtr, keyLen), readString(valuePtr, valueLen));
                } catch (e) {
                    console.warn("cannot save settings:", e);
                }
            };

            env.openflek_query = function (ptr, cap) {
                return writeString(window.location.search, ptr, cap);
            };

            // Levels as in Rust's `log` crate: 1 error, 2 warn, 3 info and below.
            env.openflek_console_log = function (level, ptr, len) {
                const msg = readString(ptr, len);
                if (level <= 1) {
                    console.error(msg);
                } else if (level == 2) {
                    console.warn(msg);
                } else {
                    console.log(msg);
                }
            };

            env.openflek_reload = function () {
                window.location.reload();
            };
        },
    });
})();
