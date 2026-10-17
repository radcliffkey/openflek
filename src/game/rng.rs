//! A small deterministic random generator (the linear congruential generator
//! used by Turbo Pascal), so games can be replayed from a seed in tests.

#[derive(Clone, Debug)]
pub struct Rng {
    seed: u32,
}

impl Rng {
    pub fn new(seed: u32) -> Rng {
        Rng { seed }
    }

    fn step(&mut self) -> u32 {
        self.seed = self.seed.wrapping_mul(0x0808_8405).wrapping_add(1);
        self.seed
    }

    /// Uniform integer in `0..n` (0 when `n` is 0).
    pub fn below(&mut self, n: u32) -> u32 {
        let hi = self.step() >> 16;
        if n <= 0xFFFF {
            (hi * n) >> 16
        } else {
            ((self.step() as u64 * n as u64) >> 32) as u32
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn below_stays_in_range_and_covers_it() {
        let mut r = Rng::new(42);
        let mut seen = [false; 7];
        for _ in 0..1000 {
            let v = r.below(7) as usize;
            assert!(v < 7);
            seen[v] = true;
        }
        assert!(seen.iter().all(|&s| s));
        assert_eq!(r.below(0), 0);
    }

    #[test]
    fn same_seed_same_sequence() {
        let (mut a, mut b) = (Rng::new(7), Rng::new(7));
        for _ in 0..20 {
            assert_eq!(a.below(100), b.below(100));
        }
    }
}
