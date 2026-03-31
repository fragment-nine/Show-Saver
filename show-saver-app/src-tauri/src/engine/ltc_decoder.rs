//! LTC (Linear Timecode) decoder.
//!
//! Pure-Rust biphase-mark decoder that extracts SMPTE timecode from raw audio.
//! Replaces TouchDesigner's `ltcin1` CHOP.
//!
//! LTC encodes timecode as a biphase-modulated audio signal.
//! Each LTC frame is 80 bits containing BCD-encoded time values.

use super::timecode::Timecode;

/// LTC sync word: 0011 1111 1111 1101 (bits 64-79 of each frame).
const LTC_SYNC_WORD: u16 = 0x3FFD;

/// Number of bits in one LTC frame.
const BITS_PER_FRAME: usize = 80;

/// Decodes LTC timecode from raw audio samples.
pub struct LtcDecoder {
    sample_rate: u32,
    fps: u32,
    samples_per_bit: f32,

    // Biphase decoding state
    prev_sample: f32,
    sample_count: u32,
    half_bit: bool,
    bit_buffer: Vec<u8>,
    pending_frames: Vec<Timecode>,
}

impl LtcDecoder {
    pub fn new(sample_rate: u32, fps: u32) -> Self {
        let samples_per_bit = sample_rate as f32 / (fps as f32 * BITS_PER_FRAME as f32);
        Self {
            sample_rate,
            fps,
            samples_per_bit,
            prev_sample: 0.0,
            sample_count: 0,
            half_bit: false,
            bit_buffer: Vec::with_capacity(BITS_PER_FRAME * 3),
            pending_frames: Vec::new(),
        }
    }

    /// Feed float32 audio samples to the decoder.
    ///
    /// Samples should be mono, normalized to [-1.0, 1.0].
    pub fn write_samples(&mut self, samples: &[f32]) {
        let threshold = self.samples_per_bit * 0.75;

        for &sample in samples {
            self.sample_count += 1;

            // Detect zero crossings (biphase transitions)
            let current_positive = sample >= 0.0;
            let prev_positive = self.prev_sample >= 0.0;

            if current_positive != prev_positive {
                let period = self.sample_count;

                if (period as f32) < threshold {
                    // Short period = two transitions per bit = '1' bit
                    if self.half_bit {
                        self.bit_buffer.push(1);
                        self.half_bit = false;
                    } else {
                        self.half_bit = true;
                    }
                } else {
                    // Long period = one transition per bit = '0' bit
                    self.bit_buffer.push(0);
                    self.half_bit = false;
                }

                self.sample_count = 0;

                // Try to decode when we have enough bits
                if self.bit_buffer.len() >= BITS_PER_FRAME {
                    self.try_decode_frame();
                }
            }

            self.prev_sample = sample;
        }
    }

    /// Read all decoded frames and clear the queue.
    pub fn read_frames(&mut self) -> Vec<Timecode> {
        std::mem::take(&mut self.pending_frames)
    }

    /// Reset decoder state (call when switching devices or restarting).
    pub fn reset(&mut self) {
        self.prev_sample = 0.0;
        self.sample_count = 0;
        self.half_bit = false;
        self.bit_buffer.clear();
        self.pending_frames.clear();
    }

    fn try_decode_frame(&mut self) {
        let bits = &self.bit_buffer;
        if bits.len() < BITS_PER_FRAME {
            return;
        }

        // Check last 16 bits for LTC sync word
        let sync_start = bits.len() - 16;
        let mut sync_word: u16 = 0;
        for &b in &bits[sync_start..] {
            sync_word = (sync_word << 1) | b as u16;
        }

        if sync_word != LTC_SYNC_WORD {
            // No sync — trim buffer to avoid unbounded growth
            if bits.len() > BITS_PER_FRAME * 3 {
                let trim_to = bits.len() - BITS_PER_FRAME;
                self.bit_buffer = self.bit_buffer[trim_to..].to_vec();
            }
            return;
        }

        // Extract the 80-bit frame
        let frame_start = bits.len() - BITS_PER_FRAME;
        let frame_bits: Vec<u8> = bits[frame_start..].to_vec();
        self.bit_buffer.clear();

        // Decode BCD time fields from LTC bit positions:
        //   Frames:  bits 0-3 (units), bits 8-9 (tens)
        //   Seconds: bits 16-19 (units), bits 24-26 (tens)
        //   Minutes: bits 32-35 (units), bits 40-42 (tens)
        //   Hours:   bits 48-51 (units), bits 56-57 (tens)
        let bcd = |positions: &[usize]| -> u32 {
            positions
                .iter()
                .enumerate()
                .map(|(i, &pos)| {
                    if pos < frame_bits.len() {
                        (frame_bits[pos] as u32) << i
                    } else {
                        0
                    }
                })
                .sum()
        };

        let frame_units = bcd(&[0, 1, 2, 3]);
        let frame_tens = bcd(&[8, 9]);
        let sec_units = bcd(&[16, 17, 18, 19]);
        let sec_tens = bcd(&[24, 25, 26]);
        let min_units = bcd(&[32, 33, 34, 35]);
        let min_tens = bcd(&[40, 41, 42]);
        let hr_units = bcd(&[48, 49, 50, 51]);
        let hr_tens = bcd(&[56, 57]);

        let tc = Timecode::new(
            hr_tens * 10 + hr_units,
            min_tens * 10 + min_units,
            sec_tens * 10 + sec_units,
            frame_tens * 10 + frame_units,
        );

        self.pending_frames.push(tc);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_decoder_creation() {
        let dec = LtcDecoder::new(48000, 30);
        assert_eq!(dec.sample_rate, 48000);
        assert_eq!(dec.fps, 30);
    }

    #[test]
    fn test_decoder_silence() {
        let mut dec = LtcDecoder::new(48000, 30);
        let silence = vec![0.0f32; 4800];
        dec.write_samples(&silence);
        let frames = dec.read_frames();
        assert!(frames.is_empty(), "Silence should not produce frames");
    }

    #[test]
    fn test_decoder_reset() {
        let mut dec = LtcDecoder::new(48000, 30);
        dec.bit_buffer.push(1);
        dec.bit_buffer.push(0);
        dec.reset();
        assert!(dec.bit_buffer.is_empty());
        assert!(dec.pending_frames.is_empty());
    }

    #[test]
    fn test_samples_per_bit() {
        let dec = LtcDecoder::new(48000, 30);
        // 48000 / (30 * 80) = 20 samples per bit
        assert!((dec.samples_per_bit - 20.0).abs() < 0.01);
    }
}
