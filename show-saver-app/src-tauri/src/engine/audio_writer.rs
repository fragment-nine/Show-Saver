//! Audio file writers with channel routing.
//!
//! Handles writing program-only (pgm) and timecode+program (ltc) audio files.
//! Uses the `hound` crate for WAV output.

use anyhow::{Context, Result};
use hound::{SampleFormat, WavSpec, WavWriter};
use std::fs;
use std::io::BufWriter;
use std::path::{Path, PathBuf};

/// Channel routing mode for output files.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ChannelMode {
    /// Program audio on both channels (stereo).
    Program,
    /// Timecode on left channel, program on right channel.
    TimecodeProgram,
}

/// Writes audio samples to a WAV file with specific channel routing.
pub struct AudioWriter {
    writer: WavWriter<BufWriter<fs::File>>,
    mode: ChannelMode,
    path: PathBuf,
}

impl AudioWriter {
    /// Create a new WAV writer.
    ///
    /// Creates parent directories if they don't exist.
    pub fn new(path: &Path, sample_rate: u32, mode: ChannelMode) -> Result<Self> {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)
                .with_context(|| format!("Failed to create directory: {}", parent.display()))?;
        }

        let spec = WavSpec {
            channels: 2,
            sample_rate,
            bits_per_sample: 24,
            sample_format: SampleFormat::Int,
        };

        let writer = WavWriter::create(path, spec)
            .with_context(|| format!("Failed to create WAV file: {}", path.display()))?;

        Ok(Self {
            writer,
            mode,
            path: path.to_path_buf(),
        })
    }

    /// Write audio samples.
    ///
    /// - `program`: program audio (mono float32 slice)
    /// - `timecode`: timecode audio (mono float32 slice, used only in TimecodeProgram mode)
    pub fn write(&mut self, program: &[f32], timecode: Option<&[f32]>) -> Result<()> {
        let n = program.len();

        match self.mode {
            ChannelMode::Program => {
                // Program on both channels
                for &s in program {
                    let sample = float_to_i32_24bit(s);
                    self.writer.write_sample(sample)?;
                    self.writer.write_sample(sample)?;
                }
            }
            ChannelMode::TimecodeProgram => {
                let tc = timecode.unwrap_or(&[]);
                for i in 0..n {
                    let tc_sample = if i < tc.len() {
                        float_to_i32_24bit(tc[i])
                    } else {
                        0
                    };
                    let pgm_sample = float_to_i32_24bit(program[i]);
                    self.writer.write_sample(tc_sample)?; // Left = TC
                    self.writer.write_sample(pgm_sample)?; // Right = PGM
                }
            }
        }

        Ok(())
    }

    /// Finalize and close the file.
    pub fn finalize(self) -> Result<()> {
        self.writer
            .finalize()
            .with_context(|| format!("Failed to finalize WAV: {}", self.path.display()))?;
        Ok(())
    }
}

/// Convert float32 [-1.0, 1.0] to 24-bit signed integer.
fn float_to_i32_24bit(sample: f32) -> i32 {
    let clamped = sample.clamp(-1.0, 1.0);
    (clamped * 8_388_607.0) as i32 // 2^23 - 1
}

/// Manages all 4 audio writers for a recording session.
///
/// Writers:
///   - `song_pgm`: Per-song program audio (both channels)
///   - `song_ltc`: Per-song TC+program audio
///   - `long_pgm`: Full-run program audio
///   - `long_ltc`: Full-run TC+program audio
pub struct RecordingSession {
    sample_rate: u32,
    song_pgm: Option<AudioWriter>,
    song_ltc: Option<AudioWriter>,
    long_pgm: Option<AudioWriter>,
    long_ltc: Option<AudioWriter>,
}

impl RecordingSession {
    pub fn new(sample_rate: u32) -> Self {
        Self {
            sample_rate,
            song_pgm: None,
            song_ltc: None,
            long_pgm: None,
            long_ltc: None,
        }
    }

    /// Start the long recording writers.
    pub fn start_long(&mut self, pgm_path: &Path, ltc_path: &Path) -> Result<()> {
        self.long_pgm = Some(AudioWriter::new(
            pgm_path,
            self.sample_rate,
            ChannelMode::Program,
        )?);
        self.long_ltc = Some(AudioWriter::new(
            ltc_path,
            self.sample_rate,
            ChannelMode::TimecodeProgram,
        )?);
        Ok(())
    }

    /// Start per-song writers (closing any previous song).
    pub fn start_song(&mut self, pgm_path: &Path, ltc_path: &Path) -> Result<()> {
        self.stop_song()?;

        self.song_pgm = Some(AudioWriter::new(
            pgm_path,
            self.sample_rate,
            ChannelMode::Program,
        )?);
        self.song_ltc = Some(AudioWriter::new(
            ltc_path,
            self.sample_rate,
            ChannelMode::TimecodeProgram,
        )?);

        Ok(())
    }

    /// Close per-song writers.
    pub fn stop_song(&mut self) -> Result<()> {
        if let Some(w) = self.song_pgm.take() {
            w.finalize()?;
        }
        if let Some(w) = self.song_ltc.take() {
            w.finalize()?;
        }
        Ok(())
    }

    /// Close all writers.
    pub fn stop_all(&mut self) -> Result<()> {
        self.stop_song()?;
        if let Some(w) = self.long_pgm.take() {
            w.finalize()?;
        }
        if let Some(w) = self.long_ltc.take() {
            w.finalize()?;
        }
        Ok(())
    }

    /// Write samples to all active writers.
    pub fn write(&mut self, program: &[f32], timecode: Option<&[f32]>) -> Result<()> {
        if let Some(ref mut w) = self.song_pgm {
            w.write(program, timecode)?;
        }
        if let Some(ref mut w) = self.song_ltc {
            w.write(program, timecode)?;
        }
        if let Some(ref mut w) = self.long_pgm {
            w.write(program, timecode)?;
        }
        if let Some(ref mut w) = self.long_ltc {
            w.write(program, timecode)?;
        }
        Ok(())
    }

    pub fn is_recording_song(&self) -> bool {
        self.song_pgm.is_some()
    }

    pub fn is_recording_long(&self) -> bool {
        self.long_pgm.is_some()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_float_to_i32() {
        assert_eq!(float_to_i32_24bit(0.0), 0);
        assert_eq!(float_to_i32_24bit(1.0), 8_388_607);
        assert_eq!(float_to_i32_24bit(-1.0), -8_388_607);
        // Clamping
        assert_eq!(float_to_i32_24bit(1.5), 8_388_607);
        assert_eq!(float_to_i32_24bit(-1.5), -8_388_607);
    }

    #[test]
    fn test_write_pgm() {
        let tmp = TempDir::new().unwrap();
        let path = tmp.path().join("test_pgm.wav");

        let mut writer = AudioWriter::new(&path, 48000, ChannelMode::Program).unwrap();
        let samples = vec![0.0f32, 0.5, -0.5, 1.0];
        writer.write(&samples, None).unwrap();
        writer.finalize().unwrap();

        assert!(path.exists());
    }

    #[test]
    fn test_write_ltc_mode() {
        let tmp = TempDir::new().unwrap();
        let path = tmp.path().join("test_ltc.wav");

        let mut writer = AudioWriter::new(&path, 48000, ChannelMode::TimecodeProgram).unwrap();
        let pgm = vec![0.1f32, 0.2, 0.3];
        let tc = vec![0.9f32, 0.8, 0.7];
        writer.write(&pgm, Some(&tc)).unwrap();
        writer.finalize().unwrap();

        assert!(path.exists());
    }

    #[test]
    fn test_recording_session() {
        let tmp = TempDir::new().unwrap();
        let mut session = RecordingSession::new(48000);

        let pgm_path = tmp.path().join("song_pgm.wav");
        let ltc_path = tmp.path().join("song_ltc.wav");

        session.start_song(&pgm_path, &ltc_path).unwrap();
        assert!(session.is_recording_song());

        let samples = vec![0.0f32; 480];
        session.write(&samples, Some(&samples)).unwrap();

        session.stop_all().unwrap();
        assert!(!session.is_recording_song());
        assert!(pgm_path.exists());
        assert!(ltc_path.exists());
    }
}
