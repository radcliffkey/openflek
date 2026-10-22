"""Builds the 32 card faces and writes them to src/art/deck_data.bin.

Run it from anywhere:

    python3 scripts/deck_gen/build_sheet.py

then look at the result in the game's own rendering with
`cargo run --example card_sheet -- docs/card_sheet.png 2`.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, REPO_ROOT)

from scripts.deck_gen.aces import draw_ace_card
from scripts.deck_gen.courts import draw_court_card
from scripts.deck_gen.palette import FaceCanvas
from scripts.deck_gen.vignettes import draw_number_card

DECK_PATH = os.path.join(REPO_ROOT, 'src', 'art', 'deck_data.bin')
DECK_BYTES = 32 * 61 * 100 // 2


def build_all_faces():
    faces = []
    for cid in range(32):
        suit = cid // 8
        rank = cid % 8
        c = FaceCanvas()
        if rank < 4:
            draw_number_card(c, suit, rank)
        elif rank < 7:
            draw_court_card(c, suit, rank)
        else:
            draw_ace_card(c, suit)
        faces.append(c)
    return faces


def pack_deck_bytes(faces):
    """Packs 32 61x100 FaceCanvas objects into the 97,600-byte 4-bit format of deck_data.bin."""
    out = bytearray()
    for face in faces:
        flat = [col for row in face.px for col in row]
        for i in range(0, len(flat), 2):
            out.append((flat[i] << 4) | flat[i + 1])
    # Checked explicitly rather than with assert, which `python -O` skips.
    if len(out) != DECK_BYTES:
        raise ValueError(f'deck packs to {len(out)} bytes, the game expects {DECK_BYTES}')
    return bytes(out)


def main():
    faces = build_all_faces()
    # Every face must be distinct and use only the 16 EGA colours.
    seen = set()
    for cid, f in enumerate(faces):
        flat = tuple(col for row in f.px for col in row)
        if not all(0 <= col <= 15 for col in flat):
            raise ValueError(f'invalid colour in card {cid}')
        if flat in seen:
            raise ValueError(f'card {cid} duplicates an earlier face')
        seen.add(flat)
    with open(DECK_PATH, 'wb') as fp:
        fp.write(pack_deck_bytes(faces))
    print(f'Wrote {DECK_PATH}')


if __name__ == '__main__':
    main()
