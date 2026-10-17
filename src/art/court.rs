//! The court cards: spodek (Under), svršek (Over) and král (King) of each suit.

use super::figure::{Beard, Costume, Figure, Hat, Pose, Prop, dark, draw_figure};
use super::paint::{Pt, Shade, arc_points, blob, dot, limb, line, outline, shape, thick_path};
use super::scenery::{self, GROUND};
use super::symbols::draw_symbol;
use crate::game::cards::{Rank, Suit};
use crate::gfx::{Canvas, Pattern, color::*};

fn pose(
    head: Pt,
    shoulders: [Pt; 2],
    elbows: [Pt; 2],
    hands: [Pt; 2],
    hips: [Pt; 2],
    knees: [Pt; 2],
    feet: [Pt; 2],
) -> Pose {
    Pose {
        head,
        shoulders,
        elbows,
        hands,
        hips,
        knees,
        feet,
        seated: false,
    }
}

#[allow(clippy::too_many_arguments)]
fn costume(
    hair: u8,
    beard: Beard,
    hat: Hat,
    doublet: u8,
    trim: u8,
    sleeves: u8,
    tunic: Option<u8>,
    breeches: u8,
    stockings: u8,
    shoes: u8,
    belt: u8,
) -> Costume {
    Costume {
        hair,
        beard,
        hat,
        doublet,
        trim,
        sleeves,
        tunic,
        breeches,
        stockings,
        shoes,
        belt,
    }
}

fn throne(c: &mut Canvas, wood: u8, cushion: u8) {
    let back = [
        (12.0, 16.0),
        (19.0, 9.0),
        (30.0, 6.0),
        (41.0, 9.0),
        (48.0, 16.0),
        (48.0, 70.0),
        (12.0, 70.0),
    ];
    shape(c, &back, Shade::Dither(wood, dark(wood)), Some(dark(wood)));
    shape(
        c,
        &[
            (16.0, 18.0),
            (30.0, 11.0),
            (44.0, 18.0),
            (44.0, 66.0),
            (16.0, 66.0),
        ],
        Shade::Pattern(Pattern::CROSS_HATCH, dark(cushion), cushion),
        Some(dark(wood)),
    );
    blob(c, 30.0, 8.0, 3.0, 3.0, Shade::Solid(YELLOW), Some(BROWN));
    // Carved armrests with scrolls and legs.
    for (x, dir) in [(10.0, -1.0), (50.0, 1.0)] {
        limb(
            c,
            (x, 56.0),
            (x, GROUND as f32 + 4.0),
            4.0,
            4.0,
            Shade::Solid(wood),
            Some(dark(wood)),
        );
        blob(
            c,
            x + dir,
            54.0,
            4.0,
            4.0,
            Shade::Solid(wood),
            Some(dark(wood)),
        );
        blob(c, x + dir, 54.0, 1.5, 1.5, Shade::Solid(dark(wood)), None);
        for y in [64.0, 72.0, 80.0] {
            line(c, (x - 2.0, y), (x + 2.0, y + 2.0), dark(wood));
        }
    }
}

fn standing(suit: Suit, over: bool) -> (Figure, Pt) {
    match (suit, over) {
        (Suit::Acorns, false) => (
            Figure {
                pose: pose(
                    (30.0, 16.0),
                    [(22.0, 27.0), (38.0, 27.0)],
                    [(17.0, 39.0), (43.0, 37.0)],
                    [(23.0, 45.0), (38.0, 41.0)],
                    [(25.0, 54.0), (35.0, 54.0)],
                    [(21.0, 70.0), (40.0, 70.0)],
                    [(17.0, 92.0), (44.0, 92.0)],
                ),
                costume: costume(
                    YELLOW,
                    Beard::Mustache,
                    Hat::Feathered {
                        color: GREEN,
                        feather: LIGHT_RED,
                    },
                    LIGHT_RED,
                    YELLOW,
                    YELLOW,
                    Some(LIGHT_RED),
                    CYAN,
                    YELLOW,
                    MAGENTA,
                    LIGHT_GREEN,
                ),
                props_behind: vec![],
                props_front: vec![Prop::Crossbow {
                    center: (31.0, 42.0),
                }],
            },
            (30.0, 80.0),
        ),
        (Suit::Acorns, true) => (
            Figure {
                pose: pose(
                    (28.0, 16.0),
                    [(20.0, 27.0), (36.0, 27.0)],
                    [(13.0, 39.0), (42.0, 36.0)],
                    [(20.0, 49.0), (46.0, 30.0)],
                    [(23.0, 55.0), (33.0, 55.0)],
                    [(20.0, 72.0), (37.0, 71.0)],
                    [(17.0, 92.0), (41.0, 92.0)],
                ),
                costume: costume(
                    BROWN,
                    Beard::Full,
                    Hat::Beret(RED),
                    GREEN,
                    YELLOW,
                    LIGHT_GREEN,
                    None,
                    YELLOW,
                    LIGHT_RED,
                    BROWN,
                    RED,
                ),
                props_behind: vec![Prop::Halberd {
                    butt: (47.0, 93.0),
                    tip: (47.0, 4.0),
                }],
                props_front: vec![],
            },
            (10.0, 11.0),
        ),
        (Suit::Leaves, false) => (
            Figure {
                pose: pose(
                    (30.0, 17.0),
                    [(22.0, 28.0), (38.0, 28.0)],
                    [(17.0, 41.0), (45.0, 31.0)],
                    [(23.0, 49.0), (40.0, 20.0)],
                    [(25.0, 56.0), (35.0, 56.0)],
                    [(23.0, 73.0), (40.0, 72.0)],
                    [(21.0, 92.0), (45.0, 92.0)],
                ),
                costume: costume(
                    YELLOW,
                    Beard::None,
                    Hat::Cap(RED),
                    YELLOW,
                    RED,
                    GREEN,
                    Some(GREEN),
                    LIGHT_RED,
                    CYAN,
                    MAGENTA,
                    RED,
                ),
                props_behind: vec![],
                props_front: vec![Prop::Horn { end: (50.0, 9.0) }],
            },
            (10.0, 76.0),
        ),
        (Suit::Leaves, true) => (
            Figure {
                pose: pose(
                    (30.0, 18.0),
                    [(22.0, 28.0), (38.0, 28.0)],
                    [(15.0, 21.0), (44.0, 38.0)],
                    [(21.0, 11.0), (41.0, 49.0)],
                    [(25.0, 56.0), (35.0, 56.0)],
                    [(17.0, 71.0), (44.0, 69.0)],
                    [(10.0, 92.0), (51.0, 92.0)],
                ),
                costume: costume(
                    BROWN,
                    Beard::Mustache,
                    Hat::Feathered {
                        color: RED,
                        feather: YELLOW,
                    },
                    LIGHT_RED,
                    YELLOW,
                    LIGHT_RED,
                    None,
                    GREEN,
                    YELLOW,
                    BROWN,
                    GREEN,
                ),
                props_behind: vec![],
                props_front: vec![Prop::Sword {
                    hilt: (21.0, 11.0),
                    tip: (4.0, -4.0),
                }],
            },
            (50.0, 11.0),
        ),
        (Suit::Bells, false) => (
            Figure {
                pose: pose(
                    (29.0, 16.0),
                    [(21.0, 27.0), (37.0, 27.0)],
                    [(15.0, 39.0), (43.0, 37.0)],
                    [(22.0, 48.0), (39.0, 46.0)],
                    [(24.0, 55.0), (34.0, 55.0)],
                    [(21.0, 73.0), (38.0, 72.0)],
                    [(18.0, 92.0), (42.0, 92.0)],
                ),
                costume: costume(
                    YELLOW,
                    Beard::None,
                    Hat::Beret(BLUE),
                    LIGHT_CYAN,
                    BLUE,
                    CYAN,
                    Some(LIGHT_CYAN),
                    RED,
                    YELLOW,
                    BLUE,
                    RED,
                ),
                props_behind: vec![],
                props_front: vec![Prop::Drum {
                    center: (31.0, 60.0),
                }],
            },
            (50.0, 78.0),
        ),
        (Suit::Bells, true) => (
            Figure {
                pose: pose(
                    (34.0, 20.0),
                    [(26.0, 30.0), (42.0, 30.0)],
                    [(19.0, 34.0), (47.0, 42.0)],
                    [(14.0, 27.0), (42.0, 52.0)],
                    [(29.0, 58.0), (39.0, 58.0)],
                    [(27.0, 74.0), (44.0, 74.0)],
                    [(25.0, 92.0), (48.0, 92.0)],
                ),
                costume: costume(
                    BROWN,
                    Beard::Mustache,
                    Hat::Feathered {
                        color: YELLOW,
                        feather: RED,
                    },
                    RED,
                    YELLOW,
                    LIGHT_RED,
                    Some(RED),
                    YELLOW,
                    LIGHT_RED,
                    DARK_GRAY,
                    YELLOW,
                ),
                props_behind: vec![Prop::Flag {
                    butt: (13.0, 93.0),
                    tip: (13.0, 3.0),
                    cloth: LIGHT_GREEN,
                }],
                props_front: vec![],
            },
            (51.0, 11.0),
        ),
        (Suit::Hearts, false) => (
            Figure {
                pose: pose(
                    (31.0, 16.0),
                    [(23.0, 27.0), (39.0, 27.0)],
                    [(16.0, 38.0), (46.0, 38.0)],
                    [(24.0, 48.0), (44.0, 50.0)],
                    [(26.0, 55.0), (36.0, 55.0)],
                    [(23.0, 72.0), (39.0, 72.0)],
                    [(20.0, 92.0), (43.0, 92.0)],
                ),
                costume: costume(
                    YELLOW,
                    Beard::None,
                    Hat::Cap(GREEN),
                    YELLOW,
                    GREEN,
                    LIGHT_RED,
                    Some(LIGHT_RED),
                    CYAN,
                    YELLOW,
                    MAGENTA,
                    GREEN,
                ),
                props_behind: vec![Prop::Sword {
                    hilt: (45.0, 49.0),
                    tip: (50.0, 90.0),
                }],
                props_front: vec![],
            },
            (10.0, 78.0),
        ),
        (Suit::Hearts, true) => (
            Figure {
                pose: pose(
                    (29.0, 17.0),
                    [(21.0, 28.0), (37.0, 28.0)],
                    [(14.0, 37.0), (43.0, 39.0)],
                    [(19.0, 30.0), (37.0, 49.0)],
                    [(24.0, 56.0), (34.0, 56.0)],
                    [(19.0, 72.0), (40.0, 71.0)],
                    [(15.0, 92.0), (45.0, 92.0)],
                ),
                costume: costume(
                    BROWN,
                    Beard::Mustache,
                    Hat::Feathered {
                        color: GREEN,
                        feather: LIGHT_CYAN,
                    },
                    GREEN,
                    LIGHT_GREEN,
                    GREEN,
                    Some(GREEN),
                    LIGHT_RED,
                    YELLOW,
                    BROWN,
                    RED,
                ),
                props_behind: vec![Prop::Halberd {
                    butt: (52.0, 93.0),
                    tip: (7.0, 3.0),
                }],
                props_front: vec![],
            },
            (50.0, 11.0),
        ),
    }
}

fn king(suit: Suit) -> Figure {
    let seated = Pose {
        head: (30.0, 23.0),
        shoulders: [(21.0, 33.0), (39.0, 33.0)],
        elbows: [(15.0, 45.0), (45.0, 45.0)],
        hands: [(20.0, 55.0), (44.0, 56.0)],
        hips: [(23.0, 60.0), (37.0, 60.0)],
        knees: [(19.0, 72.0), (41.0, 72.0)],
        feet: [(21.0, 92.0), (39.0, 92.0)],
        seated: true,
    };
    let (hair, robe, doublet, props) = match suit {
        Suit::Acorns => (
            WHITE,
            GREEN,
            LIGHT_RED,
            vec![
                Prop::Sceptre {
                    bottom: (44.0, 60.0),
                    top: (47.0, 24.0),
                },
                Prop::Orb {
                    center: (20.0, 53.0),
                },
            ],
        ),
        Suit::Leaves => (
            BROWN,
            RED,
            YELLOW,
            vec![Prop::Sword {
                hilt: (44.0, 56.0),
                tip: (11.0, 79.0),
            }],
        ),
        Suit::Bells => (
            YELLOW,
            BLUE,
            LIGHT_CYAN,
            vec![Prop::Sceptre {
                bottom: (20.0, 60.0),
                top: (13.0, 25.0),
            }],
        ),
        Suit::Hearts => (
            LIGHT_GRAY,
            LIGHT_RED,
            GREEN,
            vec![
                Prop::Sceptre {
                    bottom: (20.0, 60.0),
                    top: (15.0, 25.0),
                },
                Prop::Orb {
                    center: (44.0, 53.0),
                },
            ],
        ),
    };
    Figure {
        pose: seated,
        costume: Costume {
            hair,
            beard: Beard::Full,
            hat: Hat::Crown,
            doublet,
            trim: YELLOW,
            sleeves: doublet,
            tunic: Some(robe),
            breeches: robe,
            stockings: robe,
            shoes: BROWN,
            belt: YELLOW,
        },
        props_behind: vec![],
        props_front: props,
    }
}

/// A cape over the king's shoulders, behind the arms.
fn mantle(c: &mut Canvas, color: u8) {
    let pts = [
        (18.0, 31.0),
        (42.0, 31.0),
        (49.0, 60.0),
        (45.0, 64.0),
        (15.0, 64.0),
        (11.0, 60.0),
    ];
    shape(
        c,
        &pts,
        Shade::Dither(color, dark(color)),
        Some(dark(color)),
    );
    let trim = arc_points(30.0, 31.0, 13.0, 4.0, 0.0, 180.0, 8);
    thick_path(c, &trim, 2.0, WHITE);
    for p in trim.iter().step_by(2) {
        dot(c, *p, BLACK);
    }
}

/// Horizontal stretch around the card centre so figures fill the card like
/// the bulky figures of the classic deck.
const WIDEN: f32 = 1.2;

fn wx(p: Pt) -> Pt {
    (30.0 + (p.0 - 30.0) * WIDEN, p.1)
}

fn widen(mut f: Figure) -> Figure {
    let p = &mut f.pose;
    p.head = wx(p.head);
    for pts in [
        &mut p.shoulders,
        &mut p.elbows,
        &mut p.hands,
        &mut p.hips,
        &mut p.knees,
        &mut p.feet,
    ] {
        for q in pts.iter_mut() {
            *q = wx(*q);
        }
    }
    for prop in f.props_behind.iter_mut().chain(f.props_front.iter_mut()) {
        *prop = match *prop {
            Prop::Halberd { butt, tip } => Prop::Halberd {
                butt: wx(butt),
                tip: wx(tip),
            },
            Prop::Sword { hilt, tip } => Prop::Sword {
                hilt: wx(hilt),
                tip: wx(tip),
            },
            Prop::Flag { butt, tip, cloth } => Prop::Flag {
                butt: wx(butt),
                tip: wx(tip),
                cloth,
            },
            Prop::Drum { center } => Prop::Drum { center: wx(center) },
            Prop::Horn { end } => Prop::Horn { end: wx(end) },
            Prop::Crossbow { center } => Prop::Crossbow { center: wx(center) },
            Prop::Sceptre { bottom, top } => Prop::Sceptre {
                bottom: wx(bottom),
                top: wx(top),
            },
            Prop::Orb { center } => Prop::Orb { center: wx(center) },
        };
    }
    f
}

pub fn draw_court(c: &mut Canvas, suit: Suit, rank: Rank) {
    match rank {
        Rank::King => {
            let (wood, cushion, tile) = match suit {
                Suit::Acorns => (YELLOW, RED, CYAN),
                Suit::Leaves => (BROWN, GREEN, LIGHT_GRAY),
                Suit::Bells => (YELLOW, LIGHT_RED, LIGHT_CYAN),
                Suit::Hearts => (YELLOW, BLUE, CYAN),
            };
            scenery::floor(c, tile, WHITE);
            throne(c, wood, cushion);
            let fig = king(suit);
            mantle(
                c,
                if suit == Suit::Hearts {
                    RED
                } else {
                    fig.costume.tunic.unwrap_or(RED)
                },
            );
            draw_figure(c, &fig);
            // Footstool.
            c.bar(
                16,
                90,
                44,
                95,
                Shade::Pattern(Pattern::INTERLEAVE, RED, YELLOW).fill(),
            );
            outline(
                c,
                &[(16.0, 90.0), (44.0, 90.0), (44.0, 95.0), (16.0, 95.0)],
                BROWN,
            );
            scenery::corner_pips(c, suit);
        }
        _ => {
            let over = rank == Rank::Over;
            scenery::meadow(c, suit.index() * 2 + over as u8);
            let (fig, pip) = standing(suit, over);
            draw_figure(c, &widen(fig));
            draw_symbol(c, suit, pip.0 as i32, pip.1 as i32, 1);
        }
    }
}
