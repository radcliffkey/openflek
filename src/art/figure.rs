//! Paper-doll figures for the court cards: a jointed pose, a costume and props,
//! painted with outlined, dither-shaded shapes.

use super::paint::{
    Pt, Shade, arc_points, blob, direction, dot, limb, limb_quad, line, mid, outline, path, shape,
    thick_line, thick_path,
};
use crate::gfx::{Canvas, Pattern, color};

/// Skin is drawn white, as on the classic EGA cards.
const WHITE_SKIN: u8 = color::WHITE;

/// The darker companion of a colour, used for outlines and shading.
pub fn dark(c: u8) -> u8 {
    match c {
        color::WHITE => color::LIGHT_GRAY,
        color::LIGHT_GRAY => color::DARK_GRAY,
        color::YELLOW => color::BROWN,
        color::LIGHT_RED => color::RED,
        color::RED => color::BROWN,
        color::LIGHT_GREEN => color::GREEN,
        color::LIGHT_CYAN => color::CYAN,
        color::CYAN => color::BLUE,
        color::LIGHT_BLUE => color::BLUE,
        color::LIGHT_MAGENTA => color::MAGENTA,
        color::MAGENTA => color::BLUE,
        color::DARK_GRAY => color::BLACK,
        _ => color::DARK_GRAY,
    }
}

/// Outline colour for a region filled with `c`.
fn edge(c: u8) -> u8 {
    match c {
        color::WHITE | color::LIGHT_GRAY => color::DARK_GRAY,
        color::YELLOW => color::BROWN,
        color::LIGHT_RED | color::LIGHT_MAGENTA => color::RED,
        _ => color::DARK_GRAY,
    }
}

/// Joint positions in face-art coordinates (61x100). "Left" and "right" are
/// as seen by the viewer.
#[derive(Clone, Copy, Debug)]
pub struct Pose {
    pub head: Pt,
    pub shoulders: [Pt; 2],
    pub elbows: [Pt; 2],
    pub hands: [Pt; 2],
    pub hips: [Pt; 2],
    pub knees: [Pt; 2],
    pub feet: [Pt; 2],
    /// Seated figures wear a long robe over the legs.
    pub seated: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Hat {
    /// Wide-brimmed hat with a feather of the given colour.
    Feathered {
        color: u8,
        feather: u8,
    },
    /// Soft flat cap tilted to one side.
    Beret(u8),
    /// Tall pointed cap.
    Cap(u8),
    Crown,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Beard {
    None,
    Mustache,
    Full,
}

#[derive(Clone, Copy, Debug)]
pub struct Costume {
    pub hair: u8,
    pub beard: Beard,
    pub hat: Hat,
    /// Doublet (torso) colour and its trim.
    pub doublet: u8,
    pub trim: u8,
    pub sleeves: u8,
    /// Skirt of the tunic below the belt, if any.
    pub tunic: Option<u8>,
    pub breeches: u8,
    pub stockings: u8,
    pub shoes: u8,
    pub belt: u8,
}

#[derive(Clone, Copy, Debug)]
pub enum Prop {
    /// A long weapon held by `hand`, running from `butt` to `tip`.
    Halberd {
        butt: Pt,
        tip: Pt,
    },
    Sword {
        hilt: Pt,
        tip: Pt,
    },
    /// A spear or staff with a flag at the top.
    Flag {
        butt: Pt,
        tip: Pt,
        cloth: u8,
    },
    /// A drum hanging at `center`.
    Drum {
        center: Pt,
    },
    /// A horn or flute from the mouth to `end`.
    Horn {
        end: Pt,
    },
    Crossbow {
        center: Pt,
    },
    Sceptre {
        bottom: Pt,
        top: Pt,
    },
    Orb {
        center: Pt,
    },
}

pub struct Figure {
    pub pose: Pose,
    pub costume: Costume,
    /// Drawn before the body.
    pub props_behind: Vec<Prop>,
    /// Drawn after the body.
    pub props_front: Vec<Prop>,
}

/// A limb with an outline and a dithered shade stripe along one side.
fn shaded_limb(c: &mut Canvas, a: Pt, b: Pt, wa: f32, wb: f32, base: u8) {
    limb(c, a, b, wa, wb, Shade::Solid(base), None);
    let (_, (nx, ny)) = direction(a, b);
    let (sa, sb) = (wa * 0.28, wb * 0.28);
    limb(
        c,
        (a.0 + nx * sa, a.1 + ny * sa),
        (b.0 + nx * sb, b.1 + ny * sb),
        wa * 0.4,
        wb * 0.4,
        Shade::Dither(base, dark(base)),
        None,
    );
    // Outline the long sides only, so joints stay open.
    let [a1, b1, b2, a2] = limb_quad(a, b, wa, wb);
    line(c, a1, b1, edge(base));
    line(c, a2, b2, edge(base));
}

fn draw_leg(c: &mut Canvas, f: &Figure, i: usize) {
    let p = &f.pose;
    let k = &f.costume;
    let (hip, knee, foot) = (p.hips[i], p.knees[i], p.feet[i]);
    // Stocking from knee to ankle, breeches from hip to just below the knee.
    let ankle = (foot.0, foot.1 - 3.0);
    shaded_limb(c, knee, ankle, 7.0, 5.0, k.stockings);
    shaded_limb(c, hip, mid(hip, knee, 1.08), 11.0, 8.0, k.breeches);
    // Garter band under the knee.
    let g = mid(knee, ankle, 0.12);
    line(c, (g.0 - 3.0, g.1), (g.0 + 3.0, g.1), k.trim);
    // Shoe pointing outward.
    let dir = if i == 0 { -1.0 } else { 1.0 };
    shape(
        c,
        &[
            (foot.0 - 3.0, foot.1 - 3.0),
            (foot.0 + 3.0, foot.1 - 3.0),
            (foot.0 + 4.0 * dir + 1.5, foot.1),
            (foot.0 - 3.0 * dir, foot.1),
        ],
        Shade::Solid(k.shoes),
        Some(dark(k.shoes)),
    );
    dot(c, (foot.0, foot.1 - 2.0), color::YELLOW);
}

fn draw_arm(c: &mut Canvas, f: &Figure, i: usize) {
    let p = &f.pose;
    let k = &f.costume;
    shaded_limb(c, p.shoulders[i], p.elbows[i], 9.0, 7.0, k.sleeves);
    blob(
        c,
        p.elbows[i].0,
        p.elbows[i].1,
        3.0,
        3.0,
        Shade::Solid(k.sleeves),
        None,
    );
    shaded_limb(c, p.elbows[i], p.hands[i], 7.0, 5.0, k.sleeves);
    // Slashed-sleeve stripes and cuff.
    let s = mid(p.shoulders[i], p.elbows[i], 0.5);
    blob(c, s.0, s.1, 1.0, 2.0, Shade::Solid(k.trim), None);
    let cuff = mid(p.elbows[i], p.hands[i], 0.85);
    blob(
        c,
        cuff.0,
        cuff.1,
        2.5,
        2.0,
        Shade::Solid(color::WHITE),
        Some(color::LIGHT_GRAY),
    );
    blob(
        c,
        p.hands[i].0,
        p.hands[i].1,
        2.0,
        2.0,
        Shade::Solid(color::WHITE),
        Some(color::DARK_GRAY),
    );
}

fn draw_torso(c: &mut Canvas, f: &Figure) {
    let p = &f.pose;
    let k = &f.costume;
    let [sl, sr] = p.shoulders;
    let [hl, hr] = p.hips;
    let waist_l = (hl.0 + 1.0, hl.1 - 4.0);
    let waist_r = (hr.0 - 1.0, hr.1 - 4.0);
    if let Some(tunic) = k.tunic {
        let len = if p.seated { 26.0 } else { 15.0 };
        let skirt = [
            waist_l,
            waist_r,
            (hr.0 + 5.0, hr.1 + len - 2.0),
            ((hl.0 + hr.0) / 2.0 + 2.0, hr.1 + len),
            (hl.0 - 5.0, hl.1 + len - 2.0),
        ];
        shape(c, &skirt, Shade::Solid(tunic), Some(edge(tunic)));
        let hem: Vec<Pt> = vec![skirt[2], skirt[3], skirt[4]];
        path(c, &hem, k.trim);
        path(
            c,
            &[
                (skirt[4].0 + 1.0, skirt[4].1 - 2.0),
                (skirt[3].0, skirt[3].1 - 2.0),
                (skirt[2].0 - 1.0, skirt[2].1 - 2.0),
            ],
            dark(k.trim),
        );
        // Folds.
        for t in [0.3, 0.55, 0.8] {
            let top = mid(waist_l, waist_r, t);
            let bottom = mid(skirt[4], skirt[2], t);
            line(
                c,
                (top.0, top.1 + 3.0),
                (bottom.0, bottom.1 - 3.0),
                dark(tunic),
            );
        }
    }
    let body = [
        (sl.0 - 3.0, sl.1 + 1.0),
        (sl.0, sl.1 - 1.0),
        (sr.0, sr.1 - 1.0),
        (sr.0 + 3.0, sr.1 + 1.0),
        (waist_r.0 + 1.0, waist_r.1),
        (waist_l.0 - 1.0, waist_l.1),
    ];
    shape(c, &body, Shade::Solid(k.doublet), None);
    // Shade the right half.
    let right = [
        mid(sl, sr, 0.62),
        (sr.0, sr.1 - 1.0),
        (sr.0 + 3.0, sr.1 + 1.0),
        (waist_r.0 + 1.0, waist_r.1),
        mid(waist_l, waist_r, 0.62),
    ];
    shape(c, &right, Shade::Dither(k.doublet, dark(k.doublet)), None);
    outline(c, &body, edge(k.doublet));
    // Placket with buttons.
    let neck = mid(sl, sr, 0.5);
    let belt = mid(waist_l, waist_r, 0.5);
    line(c, neck, belt, k.trim);
    let mut t = 0.15;
    while t < 0.95 {
        dot(c, mid(neck, belt, t), dark(k.trim));
        t += 0.2;
    }
    // Belt with buckle.
    limb(
        c,
        (waist_l.0 - 1.0, waist_l.1),
        (waist_r.0 + 1.0, waist_r.1),
        3.0,
        3.0,
        Shade::Solid(k.belt),
        None,
    );
    blob(
        c,
        belt.0,
        belt.1,
        1.5,
        1.0,
        Shade::Solid(color::YELLOW),
        None,
    );
    // Ruff collar.
    blob(
        c,
        neck.0,
        neck.1 + 0.5,
        5.0,
        2.0,
        Shade::Dither(color::WHITE, color::LIGHT_GRAY),
        Some(color::DARK_GRAY),
    );
}

fn draw_head(c: &mut Canvas, f: &Figure) {
    let (hx, hy) = f.pose.head;
    let k = &f.costume;
    // Hair falls to the shoulders behind the face.
    let hair = [
        (hx - 6.0, hy - 4.0),
        (hx + 6.0, hy - 4.0),
        (hx + 7.0, hy + 7.0),
        (hx + 4.0, hy + 9.0),
        (hx - 4.0, hy + 9.0),
        (hx - 7.0, hy + 7.0),
    ];
    shape(c, &hair, Shade::Solid(k.hair), Some(dark(k.hair)));
    for dx in [-5.0, 5.0] {
        line(c, (hx + dx, hy), (hx + dx * 1.1, hy + 7.0), dark(k.hair));
    }
    blob(
        c,
        hx,
        hy,
        5.0,
        6.0,
        Shade::Solid(WHITE_SKIN),
        Some(color::RED),
    );
    // Fringe under the hat.
    line(c, (hx - 4.0, hy - 5.0), (hx + 4.0, hy - 5.0), k.hair);
    // Eyes, brows, nose, mouth.
    for dx in [-2.0, 2.0] {
        dot(c, (hx + dx, hy - 1.0), color::BLACK);
        line(
            c,
            (hx + dx - 1.0, hy - 3.0),
            (hx + dx + 1.0, hy - 3.0),
            dark(k.hair),
        );
    }
    path(
        c,
        &[(hx, hy - 1.0), (hx + 1.0, hy + 2.0), (hx, hy + 2.0)],
        color::RED,
    );
    match k.beard {
        Beard::None => line(c, (hx - 1.0, hy + 4.0), (hx + 1.0, hy + 4.0), color::RED),
        Beard::Mustache => {
            path(
                c,
                &[(hx - 3.0, hy + 4.0), (hx, hy + 3.0), (hx + 3.0, hy + 4.0)],
                dark(k.hair),
            );
            dot(c, (hx, hy + 5.0), color::RED);
        }
        Beard::Full => {
            shape(
                c,
                &[
                    (hx - 5.0, hy + 1.0),
                    (hx + 5.0, hy + 1.0),
                    (hx + 4.0, hy + 8.0),
                    (hx, hy + 11.0),
                    (hx - 4.0, hy + 8.0),
                ],
                Shade::Solid(k.hair),
                Some(dark(k.hair)),
            );
            line(c, (hx - 1.0, hy + 6.0), (hx - 1.0, hy + 9.0), dark(k.hair));
            line(c, (hx + 2.0, hy + 6.0), (hx + 2.0, hy + 8.0), dark(k.hair));
            path(
                c,
                &[(hx - 3.0, hy + 3.0), (hx, hy + 2.0), (hx + 3.0, hy + 3.0)],
                dark(k.hair),
            );
            dot(c, (hx, hy + 4.0), color::RED);
        }
    }
    match k.hat {
        Hat::Feathered { color: hc, feather } => {
            let fe = arc_points(hx + 3.0, hy - 11.0, 8.0, 6.0, 200.0, 330.0, 6);
            thick_path(c, &fe, 2.0, feather);
            shape(
                c,
                &[
                    (hx - 5.0, hy - 6.0),
                    (hx - 3.0, hy - 12.0),
                    (hx + 4.0, hy - 12.0),
                    (hx + 5.0, hy - 6.0),
                ],
                Shade::Solid(hc),
                Some(edge(hc)),
            );
            blob(
                c,
                hx,
                hy - 6.0,
                10.0,
                2.0,
                Shade::Dither(hc, dark(hc)),
                Some(edge(hc)),
            );
            line(c, (hx - 4.0, hy - 8.0), (hx + 4.0, hy - 8.0), feather);
        }
        Hat::Beret(hc) => {
            blob(
                c,
                hx - 1.0,
                hy - 6.0,
                8.0,
                3.0,
                Shade::Solid(hc),
                Some(edge(hc)),
            );
            blob(
                c,
                hx + 3.0,
                hy - 8.0,
                4.0,
                2.0,
                Shade::Dither(hc, dark(hc)),
                None,
            );
            dot(c, (hx + 4.0, hy - 10.0), color::YELLOW);
        }
        Hat::Cap(hc) => {
            shape(
                c,
                &[
                    (hx - 6.0, hy - 4.0),
                    (hx + 6.0, hy - 4.0),
                    (hx + 2.0, hy - 15.0),
                    (hx - 2.0, hy - 13.0),
                ],
                Shade::Dither(hc, dark(hc)),
                Some(edge(hc)),
            );
            limb(
                c,
                (hx - 6.0, hy - 4.5),
                (hx + 6.0, hy - 4.5),
                2.0,
                2.0,
                Shade::Solid(color::WHITE),
                None,
            );
        }
        Hat::Crown => {
            let base = hy - 5.0;
            shape(
                c,
                &[
                    (hx - 6.0, base),
                    (hx - 6.0, base - 8.0),
                    (hx - 3.0, base - 4.0),
                    (hx, base - 10.0),
                    (hx + 3.0, base - 4.0),
                    (hx + 6.0, base - 8.0),
                    (hx + 6.0, base),
                ],
                Shade::Solid(color::YELLOW),
                Some(color::BROWN),
            );
            limb(
                c,
                (hx - 6.0, base - 1.0),
                (hx + 6.0, base - 1.0),
                2.0,
                2.0,
                Shade::Solid(color::RED),
                None,
            );
            for (dx, j) in [
                (-3.0, color::LIGHT_CYAN),
                (0.0, color::LIGHT_GREEN),
                (3.0, color::LIGHT_CYAN),
            ] {
                dot(c, (hx + dx, base - 1.0), j);
            }
            dot(c, (hx, base - 10.0), color::LIGHT_RED);
        }
    }
}

fn draw_robe(c: &mut Canvas, f: &Figure) {
    let p = &f.pose;
    let k = &f.costume;
    let robe = k.tunic.unwrap_or(k.doublet);
    let [hl, hr] = p.hips;
    let [kl, kr] = p.knees;
    let [fl, fr] = p.feet;
    // Lap and the robe falling down to the ankles.
    let pts = [
        (hl.0 - 2.0, hl.1 - 3.0),
        (hr.0 + 2.0, hr.1 - 3.0),
        (kr.0 + 5.0, kr.1),
        (fr.0 + 6.0, fr.1 - 6.0),
        (fl.0 - 6.0, fl.1 - 6.0),
        (kl.0 - 5.0, kl.1),
    ];
    shape(c, &pts, Shade::Solid(robe), None);
    let shadow = [
        mid(pts[0], pts[1], 0.6),
        pts[1],
        pts[2],
        pts[3],
        mid(pts[4], pts[3], 0.6),
    ];
    shape(c, &shadow, Shade::Dither(robe, dark(robe)), None);
    outline(c, &pts, edge(robe));
    // Ermine hem.
    limb(
        c,
        pts[4],
        pts[3],
        3.0,
        3.0,
        Shade::Pattern(Pattern::WIDE_DOTS, color::BLACK, color::WHITE),
        Some(color::LIGHT_GRAY),
    );
    for t in [0.25, 0.5, 0.75] {
        let a = mid(pts[0], pts[1], t);
        let b = mid(pts[4], pts[3], t);
        line(c, (a.0, a.1 + 6.0), (b.0, b.1 - 3.0), dark(robe));
    }
    // Boots peeking out.
    for foot in [fl, fr] {
        shape(
            c,
            &[
                (foot.0 - 3.0, foot.1 - 5.0),
                (foot.0 + 3.0, foot.1 - 5.0),
                (foot.0 + 3.0, foot.1),
                (foot.0 - 4.0, foot.1),
            ],
            Shade::Solid(k.shoes),
            Some(dark(k.shoes)),
        );
    }
}

fn draw_prop(c: &mut Canvas, f: &Figure, prop: &Prop) {
    match *prop {
        Prop::Halberd { butt, tip } => {
            thick_line(c, butt, tip, 2.0, color::BROWN);
            let ((ux, uy), (nx, ny)) = direction(butt, tip);
            let p = |a: f32, b: f32| (tip.0 + ux * a + nx * b, tip.1 + uy * a + ny * b);
            shape(
                c,
                &[p(-10.0, 0.0), p(-10.0, 6.0), p(-6.0, 7.0), p(-3.0, 1.0)],
                Shade::Solid(color::LIGHT_CYAN),
                Some(color::BLUE),
            );
            shape(
                c,
                &[p(-9.0, 0.0), p(-8.0, -4.0), p(-6.0, 0.0)],
                Shade::Solid(color::LIGHT_CYAN),
                Some(color::BLUE),
            );
            shape(
                c,
                &[p(-3.0, -1.0), p(4.0, 0.0), p(-3.0, 1.0)],
                Shade::Solid(color::LIGHT_CYAN),
                Some(color::BLUE),
            );
            dot(c, p(-11.0, 0.0), color::RED);
        }
        Prop::Sword { hilt, tip } => {
            limb(
                c,
                hilt,
                tip,
                3.0,
                1.5,
                Shade::Solid(color::LIGHT_CYAN),
                Some(color::BLUE),
            );
            let ((ux, uy), (nx, ny)) = direction(hilt, tip);
            let (nx, ny) = (nx * 4.0, ny * 4.0);
            thick_line(
                c,
                (hilt.0 + nx, hilt.1 + ny),
                (hilt.0 - nx, hilt.1 - ny),
                2.0,
                color::YELLOW,
            );
            let pommel = (hilt.0 - ux * 4.0, hilt.1 - uy * 4.0);
            thick_line(c, hilt, pommel, 2.0, color::BROWN);
            blob(
                c,
                pommel.0,
                pommel.1,
                1.0,
                1.0,
                Shade::Solid(color::YELLOW),
                None,
            );
        }
        Prop::Flag { butt, tip, cloth } => {
            thick_line(c, butt, tip, 2.0, color::BROWN);
            let wave = [
                tip,
                (tip.0 + 9.0, tip.1 - 2.0),
                (tip.0 + 18.0, tip.1 + 2.0),
                (tip.0 + 17.0, tip.1 + 13.0),
                (tip.0 + 8.0, tip.1 + 10.0),
                (tip.0, tip.1 + 13.0),
            ];
            shape(c, &wave, Shade::Solid(cloth), Some(edge(cloth)));
            shape(
                c,
                &[
                    wave[0],
                    wave[1],
                    (wave[1].0, wave[1].1 + 5.0),
                    (tip.0, tip.1 + 6.0),
                ],
                Shade::Solid(color::WHITE),
                None,
            );
            path(
                c,
                &[
                    (tip.0, tip.1 + 6.0),
                    (tip.0 + 9.0, tip.1 + 4.0),
                    (tip.0 + 17.0, tip.1 + 7.0),
                ],
                dark(cloth),
            );
            blob(
                c,
                tip.0,
                tip.1 - 1.0,
                1.0,
                1.0,
                Shade::Solid(color::YELLOW),
                None,
            );
        }
        Prop::Drum { center: (x, y) } => {
            let body = [
                (x - 8.0, y - 4.0),
                (x + 8.0, y - 4.0),
                (x + 8.0, y + 7.0),
                (x - 8.0, y + 7.0),
            ];
            shape(c, &body, Shade::Solid(color::LIGHT_RED), Some(color::RED));
            for i in 0..4 {
                let x0 = x - 8.0 + i as f32 * 5.0;
                path(
                    c,
                    &[(x0, y - 3.0), (x0 + 3.0, y + 6.0), (x0 + 5.0, y - 3.0)],
                    color::YELLOW,
                );
            }
            blob(
                c,
                x,
                y + 7.0,
                8.0,
                2.0,
                Shade::Solid(color::YELLOW),
                Some(color::BROWN),
            );
            blob(
                c,
                x,
                y - 4.0,
                8.0,
                3.0,
                Shade::Dither(color::WHITE, color::LIGHT_GRAY),
                Some(color::DARK_GRAY),
            );
            let (hx, hy) = f.pose.hands[1];
            thick_line(c, (hx, hy), (hx - 6.0, hy - 6.0), 1.0, color::BROWN);
            dot(c, (hx - 6.0, hy - 6.0), color::WHITE);
        }
        Prop::Horn { end } => {
            let mouth = (f.pose.head.0 + 1.0, f.pose.head.1 + 4.0);
            limb(
                c,
                mouth,
                end,
                1.5,
                4.0,
                Shade::Solid(color::YELLOW),
                Some(color::BROWN),
            );
            blob(
                c,
                end.0,
                end.1,
                2.5,
                3.5,
                Shade::Solid(color::YELLOW),
                Some(color::BROWN),
            );
            dot(c, end, color::BROWN);
        }
        Prop::Crossbow { center: (x, y) } => {
            thick_line(
                c,
                (x - 10.0, y + 3.0),
                (x + 10.0, y - 3.0),
                3.0,
                color::BROWN,
            );
            let bow = arc_points(x + 9.0, y - 3.0, 3.0, 9.0, -90.0, 90.0, 6);
            thick_path(c, &bow, 2.0, color::DARK_GRAY);
            line(c, bow[0], bow[bow.len() - 1], color::LIGHT_GRAY);
            dot(c, (x - 2.0, y), color::YELLOW);
        }
        Prop::Sceptre { bottom, top } => {
            thick_line(c, bottom, top, 2.0, color::YELLOW);
            line(c, bottom, top, color::BROWN);
            blob(
                c,
                top.0,
                top.1 - 2.0,
                2.0,
                2.0,
                Shade::Solid(color::YELLOW),
                Some(color::BROWN),
            );
            dot(c, (top.0, top.1 - 5.0), color::LIGHT_RED);
            let m = mid(bottom, top, 0.6);
            blob(c, m.0, m.1, 2.0, 1.0, Shade::Solid(color::RED), None);
        }
        Prop::Orb { center: (x, y) } => {
            blob(
                c,
                x,
                y,
                4.0,
                4.0,
                Shade::Dither(color::YELLOW, color::WHITE),
                Some(color::BROWN),
            );
            line(c, (x - 4.0, y), (x + 4.0, y), color::RED);
            line(c, (x, y - 4.0), (x, y - 8.0), color::BROWN);
            line(c, (x - 2.0, y - 6.0), (x + 2.0, y - 6.0), color::BROWN);
        }
    }
}

/// Paints the whole figure.
pub fn draw_figure(c: &mut Canvas, f: &Figure) {
    for prop in &f.props_behind {
        draw_prop(c, f, prop);
    }
    if f.pose.seated {
        draw_robe(c, f);
    } else {
        let [hl, hr] = f.pose.hips;
        let pelvis = [
            (hl.0 - 4.0, hl.1 - 5.0),
            (hr.0 + 4.0, hr.1 - 5.0),
            (hr.0 + 4.0, hr.1 + 3.0),
            ((hl.0 + hr.0) / 2.0, hr.1 + 6.0),
            (hl.0 - 4.0, hl.1 + 3.0),
        ];
        shape(
            c,
            &pelvis,
            Shade::Solid(f.costume.breeches),
            Some(edge(f.costume.breeches)),
        );
        draw_leg(c, f, 0);
        draw_leg(c, f, 1);
    }
    draw_torso(c, f);
    draw_arm(c, f, 0);
    draw_arm(c, f, 1);
    draw_head(c, f);
    for prop in &f.props_front {
        draw_prop(c, f, prop);
    }
}
