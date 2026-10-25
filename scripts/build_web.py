"""Builds the browser version of OpenFlek into target/web.

Run it from anywhere:

    python3 scripts/build_web.py

The result is the game as WebAssembly, the page from web/, and the
JavaScript loaders of miniquad (window, input) and quad-snd (sound). Serve
the directory over HTTP, e.g. `python3 -m http.server -d target/web`.
"""

import hashlib
import json
import logging
import re
import subprocess
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = 'wasm32-unknown-unknown'
WASM_PATH = REPO_ROOT / 'target' / TARGET / 'release' / 'openflek.wasm'
WEB_DIR = REPO_ROOT / 'web'
OUT_DIR = REPO_ROOT / 'target' / 'web'

LOG = logging.getLogger('build_web')


def cargo(*args: str) -> str:
    """
    Runs cargo in the repository; its progress goes to the terminal.

    :return: what cargo wrote to standard output
    """
    result = subprocess.run(['cargo', *args], cwd=REPO_ROOT, stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise SystemExit(f'cargo {args[0]} failed')
    return result.stdout


def crate_dirs(names: Sequence[str]) -> list[Path]:
    """
    Finds the sources of dependencies at the versions in Cargo.lock.

    The JavaScript loaders have to match the Rust side, so they are taken from
    there. macroquad's prebuilt mq_js_bundle.js is not used: its quad-net part
    throws in strict mode, and the game needs neither that nor sapp-jsutils.
    """
    meta = json.loads(cargo('metadata', '--locked', '--format-version', '1', '--filter-platform', TARGET))
    dirs = {p['name']: Path(p['manifest_path']).parent for p in meta['packages']}
    return [dirs[name] for name in names]


def without_debug_log(audio_js: str) -> str:
    """Drops the line of quad-snd's audio.js that logs "fix" on the first key press or click."""
    text, count = re.subn(r'^[ \t]*console\.log\("fix"\);\r?\n', '', audio_js, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit('audio.js no longer has the "fix" debug log; update without_debug_log')
    return text


def versioned(page: str, name: str, content: bytes) -> str:
    """
    Appends a hash of `content` to the page's one reference to `name`, so a
    browser does not mix a new build with cached files of an older one.
    """
    quoted = f'"{name}"'
    if page.count(quoted) != 1:
        raise SystemExit(f'web/index.html has to refer to {quoted} exactly once')
    digest = hashlib.sha256(content).hexdigest()[:12]
    return page.replace(quoted, f'"{name}?v={digest}"')


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    # --locked: build with the dependencies in Cargo.lock, never re-resolve them.
    cargo('build', '--release', '--locked', '--target', TARGET)
    miniquad, quad_snd = crate_dirs(['miniquad', 'quad-snd'])
    audio_js = (quad_snd / 'js' / 'audio.js').read_text(encoding='utf-8')
    files = {
        'gl.js': (miniquad / 'js' / 'gl.js').read_bytes(),
        'audio.js': without_debug_log(audio_js).encode('utf-8'),
        'openflek.js': (WEB_DIR / 'openflek.js').read_bytes(),
        'openflek.wasm': WASM_PATH.read_bytes(),
    }
    page = (WEB_DIR / 'index.html').read_text(encoding='utf-8')
    for name, content in files.items():
        page = versioned(page, name, content)

    # Everything is checked by now, so a failed build leaves no partial output.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (OUT_DIR / name).write_bytes(content)
    (OUT_DIR / 'index.html').write_text(page, encoding='utf-8')
    LOG.info(f'built {OUT_DIR}')


if __name__ == '__main__':
    main()
