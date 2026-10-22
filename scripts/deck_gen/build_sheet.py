"""Builds the complete 32-card custom EGA deck preview sheet."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.deck_gen.aces import draw_ace_card
from scripts.deck_gen.courts import draw_court_card
from scripts.deck_gen.palette import FaceCanvas, save_sheet
from scripts.deck_gen.vignettes import draw_number_card


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
        flat = [col & 0x0F for row in face.px for col in row]
        for i in range(0, len(flat), 2):
            out.append((flat[i] << 4) | flat[i + 1])
    assert len(out) == 97600
    return bytes(out)


def main():
    faces = build_all_faces()
    # Verify all 32 faces are distinct and use only 0..15
    seen = set()
    for cid, f in enumerate(faces):
        flat = tuple(col for row in f.px for col in row)
        assert all(0 <= col <= 15 for col in flat), f'Invalid colour in card {cid}'
        assert flat not in seen, f'Duplicate card face at {cid}'
        seen.add(flat)
    save_sheet(faces, 'docs/new_card_sheet.png', 'docs/card_sheet.png')
    if '--write-bin' in sys.argv:
        with open('src/art/deck_data.bin', 'wb') as fp:
            fp.write(pack_deck_bytes(faces))
        print('Updated src/art/deck_data.bin')
    print('Successfully generated docs/new_card_sheet.png')


if __name__ == '__main__':
    main()
