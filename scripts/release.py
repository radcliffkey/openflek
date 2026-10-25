"""Builds the release archives into dist/.

Run it on x86-64 Linux, from anywhere, on a committed tree:

    python3 scripts/release.py

It needs the MinGW toolchain and these rustup targets:

    rustup target add x86_64-pc-windows-gnu wasm32-unknown-unknown

The version comes from Cargo.toml, and the dependencies are the ones in
Cargo.lock (cargo runs with --locked). Once every build has succeeded, three
archives go into dist/ and replace any older openflek archives there:

* openflek-<version>-linux-x86_64.tar.gz — the Linux binary
* openflek-<version>-windows-x86_64.zip — the Windows binary
* openflek-<version>-web.zip — the browser build, the files from target/web

Each archive unpacks into a folder of the same name, which also holds LICENSE
and README.md. Files in them belong to root, have mode 755 or 644 and carry
the time of the commit, not the builder's account or clock. The release
profile strips the binaries. The Linux binary is checked with one headless
deal before it is packed; the others are not run. The web folder is meant to
be served over HTTP.
"""

import argparse
import gzip
import logging
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import time
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


def git(*args: str) -> str:
    """Runs git in the repository and returns its output."""
    result = subprocess.run(['git', *args], cwd=REPO_ROOT, stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise SystemExit(f'git {args[0]} failed')
    return result.stdout


def run(cmd: list[str]) -> None:
    """Runs a command; a non-zero status stops the release."""
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(f'{" ".join(cmd)} failed')


def check_clean_tree() -> None:
    """Stops unless every tracked file is committed, so a release matches a commit."""
    status = git('status', '--porcelain', '--untracked-files=no')
    if status.strip():
        raise SystemExit(f'commit these first, or pass --allow-dirty:\n{status.rstrip()}')


def glibc_floor(binary: Path) -> str | None:
    """The newest glibc symbol version `binary` asks for: the oldest glibc it runs on."""
    versions = re.findall(rb'GLIBC_(\d+(?:\.\d+)+)', binary.read_bytes())
    if not versions:
        return None
    return max(versions, key=lambda v: tuple(int(n) for n in v.split(b'.'))).decode()


def with_docs(files: Sequence[tuple[Path, str]]) -> list[tuple[Path, str]]:
    """`files` as (path, name in the archive), followed by the documents."""
    return [*files, *((REPO_ROOT / name, name) for name in DOCS)]


def file_mode(path: Path) -> int:
    """
    755 for programs, 644 for everything else, whatever the builder's umask.
    A program is a file with an execute bit; `os.access` would also say no
    on a noexec mount.
    """
    return 0o755 if path.stat().st_mode & 0o111 else 0o644


def pack_tar(dest: Path, stem: str, files: Sequence[tuple[Path, str]], mtime: int) -> Path:
    """Packs `files` as (path, name) into `stem`/ inside `stem`.tar.gz."""
    archive = dest / f'{stem}.tar.gz'
    # The gzip header carries a time of its own, so the file is opened here.
    with (
        open(archive, 'wb') as raw,
        gzip.GzipFile(fileobj=raw, mode='wb', mtime=mtime) as compressed,
        tarfile.open(fileobj=compressed, mode='w') as tar,
    ):
        for path, name in files:
            info = tar.gettarinfo(path, arcname=f'{stem}/{name}')
            info.uid = info.gid = 0
            info.uname = info.gname = 'root'
            info.mode = file_mode(path)
            info.mtime = mtime
            with open(path, 'rb') as content:
                tar.addfile(info, content)
    root = (0, 0, 'root', 'root')
    expected = [(f'{stem}/{name}', path.stat().st_size, file_mode(path), mtime, root) for path, name in files]
    with tarfile.open(archive) as tar:
        packed = [
            (member.name, member.size, member.mode, member.mtime, (member.uid, member.gid, member.uname, member.gname))
            for member in tar.getmembers()
        ]
    check_contents(archive, packed, expected)
    return archive


def pack_zip(dest: Path, stem: str, files: Sequence[tuple[Path, str]], mtime: int) -> Path:
    """Packs `files` as (path, name) into `stem`/ inside `stem`.zip."""
    archive = dest / f'{stem}.zip'
    # Zip stores a local date and time without a zone, to even seconds; UTC
    # keeps it stable, and rounding makes the stored time the expected one.
    date_time = time.gmtime(mtime - mtime % 2)[:6]
    with zipfile.ZipFile(archive, 'w') as zipped:
        for path, name in files:
            info = zipfile.ZipInfo(f'{stem}/{name}', date_time=date_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100000 | file_mode(path)) << 16
            zipped.writestr(info, path.read_bytes())
    expected = [(f'{stem}/{name}', path.stat().st_size, file_mode(path), date_time) for path, name in files]
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise SystemExit(f'{archive.name} is corrupt')
        packed = [
            (info.filename, info.file_size, info.external_attr >> 16 & 0o777, info.date_time)
            for info in zipped.infolist()
        ]
    check_contents(archive, packed, expected)
    return archive


def check_contents(archive: Path, packed: list[tuple], expected: list[tuple]) -> None:
    """
    Stops unless `archive`, read back, holds exactly the expected entries in
    order: name, full size, mode, time, and for a tar also the root owner.
    """
    if packed != expected:
        raise SystemExit(f'{archive.name} holds {packed}, expected {expected}')


def replace_dist(archives: list[Path]) -> None:
    """
    Moves the finished archives into dist/, then removes older openflek
    archives. The archives are built inside dist/, so each move is a rename:
    dist/ never holds a half-written file. Other files stay.
    """
    names = {archive.name for archive in archives}
    for archive in archives:
        archive.replace(DIST / archive.name)
        LOG.info(f'dist/{archive.name}')
    for old in sorted(DIST.glob('openflek-*')):
        if old.name not in names and old.name.endswith(('.tar.gz', '.zip')):
            old.unlink()
            LOG.info(f'removed dist/{old.name}')


def main():
    argparser = argparse.ArgumentParser(description='Builds the release archives into dist/.')
    argparser.add_argument(
        '--allow-dirty',
        action='store_true',
        help='build even though tracked files have uncommitted changes',
    )
    args = argparser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    # The Linux archive is named x86_64 and holds a binary built for the host.
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise SystemExit('release.py runs on x86-64 Linux, which it builds the Linux binary for')
    if not args.allow_dirty:
        check_clean_tree()
    version = crate_version()
    mtime = int(git('log', '-1', '--format=%ct').strip())
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
    run([str(LINUX_BIN), '--headless', '--deals', '1', '--seed', '1', '--iq', '60', '--silent'])
    LOG.info(f'the Linux binary needs ALSA (libasound2) and glibc {glibc_floor(LINUX_BIN) or "(any)"} or newer')

    # Packed in a hidden folder inside dist/, so the final moves are renames;
    # the archives appear in dist/ only once every one is packed and checked.
    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DIST, prefix='.packing-') as tmp:
        dest = Path(tmp)
        archives = [
            pack_tar(dest, f'openflek-{version}-linux-x86_64', with_docs([(LINUX_BIN, 'openflek')]), mtime),
            pack_zip(dest, f'openflek-{version}-windows-x86_64', with_docs([(WINDOWS_BIN, 'openflek.exe')]), mtime),
            pack_zip(dest, f'openflek-{version}-web', with_docs(web), mtime),
        ]
        replace_dist(archives)


if __name__ == '__main__':
    main()
