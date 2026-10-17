//! Saving a canvas as a PNG file (screenshots, the card sheet example).

use super::Canvas;
use macroquad::texture::Image;

/// Writes `canvas` scaled up `scale` times with square pixels.
pub fn save(canvas: &Canvas, scale: usize, path: &str) {
    let mut rgba = Vec::new();
    canvas.to_rgba(&mut rgba);
    let (w, h) = (canvas.width() as usize, canvas.height() as usize);
    let (sw, sh) = (w * scale, h * scale);
    let mut out = vec![0u8; sw * sh * 4];
    for y in 0..sh {
        // `export_png` writes rows bottom-up, so store them flipped.
        let dst_row = (sh - 1 - y) * sw * 4;
        for x in 0..sw {
            let src = ((y / scale) * w + x / scale) * 4;
            out[dst_row + x * 4..dst_row + x * 4 + 4].copy_from_slice(&rgba[src..src + 4]);
        }
    }
    Image {
        bytes: out,
        width: sw as u16,
        height: sh as u16,
    }
    .export_png(path);
}
