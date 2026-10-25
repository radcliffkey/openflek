// OpenFlek's browser glue, a miniquad plugin: settings in localStorage, the
// query string and page reload. The Rust side is src/web.rs. Load it after
// gl.js, whose UTF8ToString and wasm_memory it uses, and before load().
"use strict";

(function () {
    const encoder = new TextEncoder();

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
        version: 2,
        register_plugin: function (importObject) {
            const env = importObject.env;

            // localStorage throws when the browser blocks site data.
            env.openflek_storage_get = function (keyPtr, keyLen, ptr, cap) {
                let value = null;
                try {
                    value = localStorage.getItem(UTF8ToString(keyPtr, keyLen));
                } catch (e) {
                    console.warn("cannot read settings:", e);
                }
                return value === null ? -1 : writeString(value, ptr, cap);
            };

            env.openflek_storage_set = function (keyPtr, keyLen, valuePtr, valueLen) {
                try {
                    localStorage.setItem(UTF8ToString(keyPtr, keyLen), UTF8ToString(valuePtr, valueLen));
                } catch (e) {
                    console.warn("cannot save settings:", e);
                }
            };

            // Decoded by the browser, one name=value per line.
            env.openflek_query = function (ptr, cap) {
                const params = new URLSearchParams(window.location.search);
                const lines = Array.from(params, ([name, value]) => name + "=" + value);
                return writeString(lines.join("\n"), ptr, cap);
            };

            env.openflek_reload = function () {
                window.location.reload();
            };
        },
    });
})();
