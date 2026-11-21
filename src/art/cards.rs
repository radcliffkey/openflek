//! Card sprites: faces from a bundled 16-colour bitmap of the deck, backs and
//! the octagonal frame drawn at runtime.

use crate::game::cards::Card;
use crate::gfx::{Canvas, Fill, color};

/// Size of the face artwork; it sits inside the card frame at (2, 2).
pub const FACE_W: i32 = 61;
pub const FACE_H: i32 = 100;
/// Nominal card size (outer octagon).
pub const CARD_W: i32 = 64;
pub const CARD_H: i32 = 103;
/// Sprite size including the drop shadow.
pub const SPRITE_W: i32 = CARD_W + 3;
pub const SPRITE_H: i32 = CARD_H + 3;

/// Colour index of sprite pixels that are not part of the card.
pub const TRANSPARENT: u8 = 255;

const OUTER: [(i32, i32); 8] = [
    (3, 0),
    (61, 0),
    (64, 3),
    (64, 100),
    (61, 103),
    (3, 103),
    (0, 100),
    (0, 3),
];
const INNER: [(i32, i32); 8] = [
    (4, 3),
    (60, 3),
    (61, 4),
    (61, 99),
    (60, 100),
    (4, 100),
    (3, 99),
    (3, 4),
];
const SHADOW: [(i32, i32); 8] = [
    (65, 4),
    (64, 101),
    (62, 103),
    (4, 104),
    (5, 105),
    (63, 105),
    (66, 102),
    (66, 5),
];

/// Paints the white ring between the outer and inner octagon plus both outlines.
fn draw_frame(c: &mut Canvas) {
    // Use the bounding box of `INNER` (3..=61, 3..=100) as the cutout so
    // `fill_poly`'s pixel-centre rounding on the (61, 99)->(60, 100) diagonal
    // cannot paint a white pinhole at interior pixel (60, 99). The four corner
    // pixels of that box lie outside `INNER` and are set white explicitly.
    const CUTOUT: [(i32, i32); 4] = [(3, 3), (61, 3), (61, 100), (3, 100)];
    let ring: Vec<(i32, i32)> = OUTER
        .iter()
        .chain([&OUTER[0]])
        .chain(CUTOUT.iter())
        .chain([&CUTOUT[0]])
        .copied()
        .collect();
    c.fill_poly(&ring, Fill::solid(color::WHITE));
    for (x, y) in CUTOUT {
        c.put_pixel(x, y, color::WHITE);
    }
    c.poly(&OUTER, color::DARK_GRAY);
    c.poly(&INNER, color::DARK_GRAY);
    c.fill_poly(&SHADOW, Fill::solid(color::DARK_GRAY));
    c.poly(&SHADOW, color::DARK_GRAY);
}

fn empty_sprite() -> Canvas {
    let mut c = Canvas::new(SPRITE_W, SPRITE_H);
    c.clear(TRANSPARENT);
    c.fill_poly(&OUTER, Fill::solid(color::WHITE));
    c
}

/// A complete face-up card: frame, shadow and artwork.
pub fn render_card_sprite(card: Card) -> Canvas {
    let mut c = empty_sprite();
    c.blit(&render_face(card), 2, 2, None);
    draw_frame(&mut c);
    c
}

/// The card back in `line_color`, laid out like a face so it sits in the frame
/// the same way.
pub fn render_back_sprite(line_color: u8) -> Canvas {
    let mut c = empty_sprite();
    c.blit(&render_back_face(line_color), 2, 2, None);
    draw_frame(&mut c);
    c
}

/// The 61x100 back artwork: the dark-grey inner border every face has, then
/// the pattern from `back_pixel`.
fn render_back_face(line_color: u8) -> Canvas {
    let mut c = Canvas::new(FACE_W, FACE_H);
    c.clear(color::WHITE);
    c.line(2, 1, FACE_W - 3, 1, color::DARK_GRAY);
    c.line(2, FACE_H - 2, FACE_W - 3, FACE_H - 2, color::DARK_GRAY);
    c.line(1, 2, 1, FACE_H - 3, color::DARK_GRAY);
    c.line(FACE_W - 2, 2, FACE_W - 2, FACE_H - 3, color::DARK_GRAY);
    for y in 2..FACE_H - 2 {
        for x in 2..FACE_W - 2 {
            c.put_pixel(x, y, back_pixel(line_color, x, y));
        }
    }
    c
}

/// Lighter partner of each back colour (1..=7) for petals and tinted cells.
fn back_light(line_color: u8) -> u8 {
    match line_color {
        color::BLUE => color::LIGHT_BLUE,
        color::GREEN => color::LIGHT_GREEN,
        color::CYAN => color::LIGHT_CYAN,
        color::RED => color::LIGHT_RED,
        color::MAGENTA => color::LIGHT_MAGENTA,
        color::BROWN => color::YELLOW,
        color::LIGHT_GRAY => color::LIGHT_GRAY,
        _ => color::WHITE,
    }
}

/// Quadrant of face pixel `(x, y)`. Rows 49 and 50 share a quadrant row, so a
/// pattern built from these coordinates mirrors exactly either way up.
fn back_quadrant(x: i32, y: i32) -> (i32, i32) {
    let qx = (x - 30).abs();
    let qy = ((2 * y - 99).abs() - 1) / 2;
    (qx, qy)
}

/// True when `(x, y)` lies inside the ellipse of radii `(rx, ry)` centred on
/// the card. The vertical radius is measured from the shared middle row.
fn in_back_oval(x: i32, y: i32, rx: f64, ry: f64) -> bool {
    let (qx, qy) = back_quadrant(x, y);
    let mx = f64::from(qx) / rx;
    let my = (f64::from(qy) + 0.5) / ry;
    mx * mx + my * my <= 1.0
}

fn touches8(x: i32, y: i32, pred: impl Fn(i32, i32) -> bool) -> bool {
    for dy in -1..=1 {
        for dx in -1..=1 {
            if (dx != 0 || dy != 0) && pred(x + dx, y + dy) {
                return true;
            }
        }
    }
    false
}

/// True when an orthogonal neighbour of `(x, y)` satisfies `pred`.
fn touches4(x: i32, y: i32, pred: impl Fn(i32, i32) -> bool) -> bool {
    [(-1, 0), (1, 0), (0, -1), (0, 1)]
        .into_iter()
        .any(|(dx, dy)| pred(x + dx, y + dy))
}

/// A pixel of `inside` with an orthogonal neighbour outside it: a one-pixel rim.
fn on_shape_edge(x: i32, y: i32, inside: impl Fn(i32, i32) -> bool) -> bool {
    inside(x, y) && touches4(x, y, |px, py| !inside(px, py))
}

/// The corner of each quadrant a fan opens from, in quadrant pixels, and
/// the square of the fan's radius.
const FAN_CORNER: (i32, i32) = (23, 42);
const FAN_RADIUS_SQ: i32 = 81;

/// Offset of face pixel `(x, y)` from the corner of its quadrant's fan,
/// measured toward the middle of the card.
fn fan_offset(x: i32, y: i32) -> (i32, i32) {
    let (qx, qy) = back_quadrant(x, y);
    (FAN_CORNER.0 - qx, FAN_CORNER.1 - qy)
}

/// True when the fan offset `(fx, fy)` lies on the fan's quarter disc.
fn in_fan_disc(fx: i32, fy: i32) -> bool {
    fx >= 0 && fy >= 0 && fx * fx + fy * fy <= FAN_RADIUS_SQ
}

/// For an offset on the fan's disc: true on its curved rim.
fn on_disc_edge(fx: i32, fy: i32) -> bool {
    !in_fan_disc(fx + 1, fy) || !in_fan_disc(fx, fy + 1)
}

/// Interior of the three-lobed corner palmette inside `(fx, fy)`.
fn fan_lobe_fill(fx: i32, fy: i32) -> bool {
    if fx < 0 || fy < 0 || fx + fy <= 2 {
        return false;
    }
    if fy <= 1 && (2..=6).contains(&fx) && !(fx == 6 && fy == 1) {
        return true;
    }
    if fx <= 1 && (2..=6).contains(&fy) && !(fy == 6 && fx == 1) {
        return true;
    }
    matches!(
        (fx, fy),
        (2, 2) | (3, 3) | (3, 4) | (4, 3) | (4, 4) | (4, 5) | (5, 4) | (5, 5)
    )
}

/// Interior of one of the eight rosette petals at face pixel `(x, y)`.
/// Defining the fill first and deriving the one-pixel dark rim from 4-neighbours
/// keeps all eight petals attached to the hub with an unbroken outline.
fn petal_interior(x: i32, y: i32) -> bool {
    let (qx, qy) = back_quadrant(x, y);
    if (2..=12).contains(&qy) && qx <= i32::from(!(qy == 2 || qy == 12)) {
        return true;
    }
    if (2..=9).contains(&qx) && qy <= i32::from(!(qx == 2 || qx == 9)) {
        return true;
    }
    matches!(
        (qx, qy),
        (2, 2) | (3, 3) | (3, 4) | (4, 4) | (4, 5) | (5, 5) | (5, 6) | (6, 6) | (5, 7) | (6, 7)
    )
}

fn rosette_pixel(x: i32, y: i32, dark: u8, light: u8) -> u8 {
    let (qx, qy) = back_quadrant(x, y);
    if qx + qy <= 1 {
        return dark;
    }
    if petal_interior(x, y) {
        return light;
    }
    if (qx == 1 && qy == 1) || touches4(x, y, petal_interior) {
        return dark;
    }
    color::WHITE
}

fn lattice_pixel(qx: i32, qy: i32, dark: u8, light: u8, gold: bool) -> u8 {
    let a = (qx + qy).rem_euclid(8);
    let b = (qx - qy).rem_euclid(8);
    if a == 0 || b == 0 || (a == 4 && b == 4) {
        return dark;
    }
    let plus = (a == 4 && (b == 3 || b == 5)) || (b == 4 && (a == 3 || a == 5));
    if plus {
        // Yellow flowers vanish on the white cells of the gold back.
        return if gold { dark } else { light };
    }
    let cell = (qx + qy).div_euclid(8) + (qx - qy).div_euclid(8);
    // Gold fills the whole diamond; the other backs keep a light chequer.
    if cell.rem_euclid(2) == 1 && (gold || (qx + qy).rem_euclid(2) == 1) {
        return light;
    }
    color::WHITE
}

/// The back pattern at face pixel (x, y), for x in 2..=58 and y in 2..=97:
/// a double border, fans in the corners, a diamond lattice with a flower in
/// each cell and alternate cells tinted, and a medallion holding an
/// eight-petalled rosette.
///
/// A one-pixel white halo keeps the lattice off the medallion and the fans.
/// Petals and fan ribs are stepped in whole pixels so the outline does not
/// sprout single-pixel jags. The gold back fills its tinted diamonds solid
/// yellow and draws its flowers in brown; yellow on white would wash out.
///
/// Everything is measured from the centre, so the back is mirror symmetric
/// both ways and looks the same either way up.
fn back_pixel(line_color: u8, x: i32, y: i32) -> u8 {
    let dark = if line_color == color::LIGHT_GRAY {
        color::DARK_GRAY
    } else {
        line_color
    };
    let light = back_light(line_color);
    let gold = line_color == color::BROWN;
    let (qx, qy) = back_quadrant(x, y);

    // Border: a dark rule, a light band, another dark rule.
    let edge = (x - 2).min(58 - x).min(y - 2).min(97 - y);
    match edge {
        0 => return color::WHITE,
        1 | 4 => return dark,
        2 | 3 => return if (qx + qy) % 4 != 0 { light } else { dark },
        _ => {}
    }

    let (fx, fy) = fan_offset(x, y);
    if in_fan_disc(fx, fy) {
        if on_disc_edge(fx, fy) || fx + fy <= 1 {
            return dark;
        }
        if fan_lobe_fill(fx, fy) {
            return light;
        }
        if touches4(fx, fy, fan_lobe_fill) {
            return dark;
        }
        return color::WHITE;
    }
    // Only a pixel within one of the disc's straight sides can touch it.
    if fx >= -1
        && fy >= -1
        && touches8(x, y, |px, py| {
            let (nx, ny) = fan_offset(px, py);
            in_fan_disc(nx, ny)
        })
    {
        return color::WHITE;
    }

    let outer = |px, py| in_back_oval(px, py, 15.0, 19.0);
    if outer(x, y) {
        if on_shape_edge(x, y, outer) {
            return dark;
        }
        let inner = |px, py| in_back_oval(px, py, 12.6, 16.2);
        if on_shape_edge(x, y, inner) {
            // Brown reads on yellow; the other backs use their light colour.
            return if gold { dark } else { light };
        }
        if !inner(x, y) {
            return color::WHITE;
        }
        return rosette_pixel(x, y, dark, light);
    }
    if touches8(x, y, outer) {
        return color::WHITE;
    }

    lattice_pixel(qx, qy, dark, light, gold)
}

/// The 32 faces in card-id order, row-major, two pixels per byte (high nibble first).
const DECK_BYTES: &[u8] = include_bytes!("deck_data.bin");
const FACE_BYTES: usize = (FACE_W * FACE_H) as usize / 2;
const _: () = assert!(DECK_BYTES.len() == 32 * FACE_BYTES);

/// The bare 61x100 face artwork of a card.
pub fn render_face(card: Card) -> Canvas {
    let mut c = Canvas::new(FACE_W, FACE_H);
    let offset = card.id() as usize * FACE_BYTES;
    for y in 0..FACE_H {
        for x in 0..FACE_W {
            let idx = (y * FACE_W + x) as usize;
            let byte = DECK_BYTES[offset + idx / 2];
            let col = if (idx & 1) == 0 {
                byte >> 4
            } else {
                byte & 0x0f
            };
            c.put_pixel(x, y, col);
        }
    }
    c
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sprites_have_card_size_and_transparent_outside() {
        for id in 0..32 {
            let c = render_card_sprite(Card::from_id(id));
            assert_eq!((c.width(), c.height()), (SPRITE_W, SPRITE_H));
            assert_eq!(c.pixel(0, 0), Some(TRANSPARENT));
            assert_eq!(c.pixel(SPRITE_W - 1, 0), Some(TRANSPARENT));
            assert_eq!(c.pixel(3, 0), Some(color::DARK_GRAY));
            assert_eq!(c.pixel(1, 1), Some(color::WHITE));
            let f = render_face(Card::from_id(id));
            assert_eq!(
                c.pixel(4, 99),
                f.pixel(2, 97),
                "card {id} bottom-left corner"
            );
            assert_eq!(
                c.pixel(60, 99),
                f.pixel(58, 97),
                "card {id} bottom-right corner"
            );
        }
    }

    #[test]
    fn all_faces_look_different() {
        let faces: Vec<Canvas> = (0..32).map(|id| render_face(Card::from_id(id))).collect();
        for i in 0..faces.len() {
            for j in i + 1..faces.len() {
                assert_ne!(faces[i], faces[j], "cards {i} and {j} render identically");
            }
        }
    }

    #[test]
    fn back_uses_requested_line_colour_and_keeps_frame() {
        let c = render_back_sprite(color::MAGENTA);
        assert!(c.pixels().contains(&color::MAGENTA));
        assert!(c.pixels().contains(&color::LIGHT_MAGENTA));
        assert_eq!(c.pixel(0, 0), Some(TRANSPARENT));
        assert_eq!(c.pixel(66, 50), Some(color::DARK_GRAY));
    }

    #[test]
    fn back_looks_the_same_either_way_up() {
        // Backs only ever use colours 1..=7 (see `app::table::back_color`).
        for line in 1..=7 {
            let f = render_back_face(line);
            for y in 0..FACE_H {
                for x in 0..FACE_W {
                    let p = f.pixel(x, y);
                    assert_eq!(
                        p,
                        f.pixel(x, FACE_H - 1 - y),
                        "colour {line}: ({x}, {y}) vs its mirror below"
                    );
                    assert_eq!(
                        p,
                        f.pixel(FACE_W - 1 - x, y),
                        "colour {line}: ({x}, {y}) vs its mirror across"
                    );
                }
            }
        }
    }

    #[test]
    fn back_border_matches_the_faces() {
        // The back sits in the frame like a face: same dark-grey inner border.
        let back = render_back_face(color::BLUE);
        let face = render_face(Card::from_id(0));
        for (x, y) in [(1, 50), (59, 50), (30, 1), (30, 98), (0, 50), (1, 1)] {
            assert_eq!(back.pixel(x, y), face.pixel(x, y), "({x}, {y})");
        }
    }

    #[test]
    fn back_has_rosette_lattice_and_no_lettering() {
        let f = render_back_face(color::RED);
        // The rosette's centre and a petal on the vertical axis.
        assert_eq!(f.pixel(30, 49), Some(color::RED));
        assert_eq!(f.pixel(30, 44), Some(color::LIGHT_RED));
        // Black only ever came from the old monogram's shadow.
        assert!(!f.pixels().contains(&color::BLACK));
        // A grey back draws its lines in dark grey so they show on white.
        assert!(
            render_back_face(color::LIGHT_GRAY)
                .pixels()
                .contains(&color::DARK_GRAY)
        );
    }

    #[test]
    fn gold_back_fills_diamonds_and_ornaments_keep_a_white_halo() {
        let gold = render_back_face(color::BROWN);
        let red = render_back_face(color::RED);
        // The red back dithers this lattice cell; the gold back fills it yellow.
        assert_eq!(red.pixel(47, 61), Some(color::WHITE));
        assert_eq!(gold.pixel(47, 61), Some(color::YELLOW));
        assert!(gold.pixels().iter().all(|&p| {
            matches!(
                p,
                color::BROWN | color::YELLOW | color::WHITE | color::DARK_GRAY
            )
        }));
        // Those two whites sit on lattice lines, just outside the medallion and a fan.
        assert_eq!(red.pixel(27, 30), Some(color::WHITE));
        assert_eq!(red.pixel(16, 11), Some(color::WHITE));
    }
}
