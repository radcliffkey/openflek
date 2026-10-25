"""Builds the release archives into dist/.

Run it on Linux, from anywhere, on a committed tree:

    python3 scripts/release.py

It needs the MinGW toolchain and these rustup targets:

    rustup target add x86_64-pc-windows-gnu wasm32-unknown-unknown

The version comes from Cargo.toml, and the dependencies are the ones in
Cargo.lock (cargo runs with --locked). The script replaces the files in dist/
with three archives, and only after every build has succeeded:

* openflek-<version>-linux-x86_64.tar.gz — the Linux binary
* openflek-<version>-windows-x86_64.zip — the Windows binary
* openflek-<version>-web.zip — the browser build, the files from target/web

Each archive unpacks into a folder of the same name, which also holds LICENSE
and README.md. The release profile strips the binaries. The Linux binary is
checked with one headless deal before it is packed; the others are not run.
The web folder is meant to be served over HTTP.
"""

import argparse
import logging
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_web

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST = REPO_ROOT / 'dist'
WINDOWS = 'x86_64-pc-windows-gnu'
LINUX_BIN = REPO_ROOT / 'target' / 'release' / 'openflek'
WINDOWS_BIN = REPO_ROOT / 'target' / WINDOWS / 'release' / 'openflek.exe'
WEB_FILES = ('index.html', 'gl.js', 'audio.js', 'openflek.js', 'openflek.wasm')
# Shipped in every archive; the licence has to travel with the binaries.
DOCS = ('LICENSE', 'README.md')

LOG = logging.getLogger('release')


def crate_version() -> str:
    """The version of the package in Cargo.toml."""
    text = (REPO_ROOT / 'Cargo.toml').read_text(encoding='utf-8')
    package = re.search(r'(?m)^\[package\]\s*(.*?)^\[', text, re.DOTALL)
    block = package.group(1) if package else text
    found = re.search(r'(?m)^version\s*=\s*"([^"]+)"', block)
    if not found:
        raise SystemExit('Cargo.toml has no package version')
    return found.group(1)


def run(cmd: list[str]) -> None:
    """Runs a command; a non-zero status stops the release."""
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(f'{" ".join(cmd)} failed')


def check_clean_tree() -> None:
    """Stops unless every tracked file is committed, so a release matches a commit."""
    status = subprocess.run(
        ['git', 'status', '--porcelain', '--untracked-files=no'],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        text=True,
    )
    if status.returncode != 0:
        raise SystemExit('git status failed')
    if status.stdout.strip():
        raise SystemExit(f'commit these first, or pass --allow-dirty:\n{status.stdout.rstrip()}')


def with_docs(files: Sequence[tuple[Path, str]]) -> list[tuple[Path, str]]:
    """`files` as (path, name in the archive), followed by the documents."""
    return [*files, *((REPO_ROOT / name, name) for name in DOCS)]


def pack_tar(dest: Path, stem: str, files: Sequence[tuple[Path, str]]) -> Path:
    """Packs `files` as (path, name) into `stem`/ inside `stem`.tar.gz."""
    archive = dest / f'{stem}.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for path, name in files:
            tar.add(path, arcname=f'{stem}/{name}')
    with tarfile.open(archive) as tar:
        names = tar.getnames()
    check_names(archive, names, stem, files)
    return archive


def pack_zip(dest: Path, stem: str, files: Sequence[tuple[Path, str]]) -> Path:
    """Packs `files` as (path, name) into `stem`/ inside `stem`.zip."""
    archive = dest / f'{stem}.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
        for path, name in files:
            zipped.write(path, f'{stem}/{name}')
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
    check_names(archive, names, stem, files)
    return archive


def check_names(archive: Path, names: list[str], stem: str, files: Sequence[tuple[Path, str]]) -> None:
    expected = [f'{stem}/{name}' for _, name in files]
    if names != expected:
        raise SystemExit(f'{archive.name} should contain {", ".join(expected)}')


def replace_dist(archives: list[Path]) -> None:
    """Puts the finished archives into dist/, removing whatever files were there."""
    DIST.mkdir(parents=True, exist_ok=True)
    for old in DIST.iterdir():
        if old.is_file():
            old.unlink()
    for archive in archives:
        shutil.move(archive, DIST / archive.name)
        LOG.info(f'{archive.name}')


def main():
    argparser = argparse.ArgumentParser(description='Builds the release archives into dist/.')
    argparser.add_argument(
        '--allow-dirty',
        action='store_true',
        help='build even though tracked files have uncommitted changes',
    )
    args = argparser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    if sys.platform != 'linux':
        raise SystemExit('release.py builds the Linux and Windows archives, so it runs on Linux')
    if not args.allow_dirty:
        check_clean_tree()
    version = crate_version()
    build_web.cargo('build', '--release', '--locked')
    build_web.cargo('build', '--release', '--locked', '--target', WINDOWS)
    build_web.main()
    for binary in (LINUX_BIN, WINDOWS_BIN):
        if not binary.is_file():
            raise SystemExit(f'missing {binary}')
    web = [(build_web.OUT_DIR / name, name) for name in WEB_FILES]
    missing = [str(path) for path, _ in web if not path.is_file()]
    if missing:
        raise SystemExit(f'missing {", ".join(missing)}')

    # dist/ is replaced only once every archive is packed and checked.
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        run([str(LINUX_BIN), '--headless', '--deals', '1', '--seed', '1', '--iq', '60', '--silent'])
        archives = [
            pack_tar(dest, f'openflek-{version}-linux-x86_64', with_docs([(LINUX_BIN, 'openflek')])),
            pack_zip(dest, f'openflek-{version}-windows-x86_64', with_docs([(WINDOWS_BIN, 'openflek.exe')])),
            pack_zip(dest, f'openflek-{version}-web', with_docs(web)),
        ]
        replace_dist(archives)


if __name__ == '__main__':
    main()
