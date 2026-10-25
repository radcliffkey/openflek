#!/bin/sh
# Builds the browser version into target/web: the game as WebAssembly, the
# page from web/, and the JavaScript loaders of miniquad (window, input) and
# quad-snd (sound). Serve the directory over HTTP, e.g.
# `python3 -m http.server -d target/web`.
set -eu
cd "$(dirname "$0")/.."

cargo build --release --target wasm32-unknown-unknown

# The loaders have to match the crate versions in Cargo.lock, so they are
# taken from the crate sources. macroquad's prebuilt mq_js_bundle.js is not
# used: its quad-net part throws in strict mode, and we need neither that
# nor sapp-jsutils.
crate_dirs=$(cargo metadata --format-version 1 --filter-platform wasm32-unknown-unknown | python3 -c '
import json, os, sys
meta = json.load(sys.stdin)
dirs = {p["name"]: os.path.dirname(p["manifest_path"]) for p in meta["packages"]}
print(dirs["miniquad"], dirs["quad-snd"])
')
set -- $crate_dirs

out=target/web
mkdir -p "$out"
cp web/index.html web/openflek.js "$out/"
cp "$1/js/gl.js" "$2/js/audio.js" "$out/"
cp target/wasm32-unknown-unknown/release/openflek.wasm "$out/"
echo "built $out"
