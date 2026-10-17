//! PC-speaker style sound: square-wave tunes rendered to in-memory WAV files.

/// One step of a tune: frequency in Hz (0 = silence) and duration in milliseconds.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Tone {
    pub hz: u32,
    pub ms: u32,
}

/// The output rate of common audio devices, so playback needs no resampling.
pub const SAMPLE_RATE: u32 = 44_100;
const AMPLITUDE: i16 = 6_000;

/// Renders a tune as a mono 16-bit PCM WAV file.
pub fn render_wav(tune: &[Tone]) -> Vec<u8> {
    let mut samples: Vec<i16> = Vec::new();
    for tone in tune {
        let n = (SAMPLE_RATE as u64 * tone.ms as u64 / 1000) as usize;
        if tone.hz == 0 {
            samples.extend(std::iter::repeat_n(0, n));
            continue;
        }
        let period = SAMPLE_RATE as f64 / tone.hz as f64;
        for i in 0..n {
            let phase = (i as f64 % period) / period;
            samples.push(if phase < 0.5 { AMPLITUDE } else { -AMPLITUDE });
        }
    }
    let data_len = (samples.len() * 2) as u32;
    let mut wav = Vec::with_capacity(44 + data_len as usize);
    wav.extend_from_slice(b"RIFF");
    wav.extend_from_slice(&(36 + data_len).to_le_bytes());
    wav.extend_from_slice(b"WAVEfmt ");
    wav.extend_from_slice(&16u32.to_le_bytes());
    wav.extend_from_slice(&1u16.to_le_bytes());
    wav.extend_from_slice(&1u16.to_le_bytes());
    wav.extend_from_slice(&SAMPLE_RATE.to_le_bytes());
    wav.extend_from_slice(&(SAMPLE_RATE * 2).to_le_bytes());
    wav.extend_from_slice(&2u16.to_le_bytes());
    wav.extend_from_slice(&16u16.to_le_bytes());
    wav.extend_from_slice(b"data");
    wav.extend_from_slice(&data_len.to_le_bytes());
    for s in samples {
        wav.extend_from_slice(&s.to_le_bytes());
    }
    wav
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wav_header_and_length_match_tune() {
        let wav = render_wav(&[Tone { hz: 440, ms: 100 }, Tone { hz: 0, ms: 50 }]);
        assert_eq!(&wav[0..4], b"RIFF");
        assert_eq!(&wav[8..12], b"WAVE");
        let samples = (SAMPLE_RATE as usize * 150) / 1000;
        assert_eq!(wav.len(), 44 + samples * 2);
        let data_len = u32::from_le_bytes(wav[40..44].try_into().unwrap()) as usize;
        assert_eq!(data_len, samples * 2);
    }

    #[test]
    fn silence_is_zero_and_tone_is_square() {
        let wav = render_wav(&[Tone { hz: 0, ms: 10 }, Tone { hz: 1000, ms: 10 }]);
        let samples: Vec<i16> = wav[44..]
            .as_chunks::<2>()
            .0
            .iter()
            .map(|&b| i16::from_le_bytes(b))
            .collect();
        let silent = SAMPLE_RATE as usize / 100;
        assert!(samples[..silent].iter().all(|&s| s == 0));
        assert!(samples[silent..].iter().all(|&s| s.abs() == AMPLITUDE));
    }
}
