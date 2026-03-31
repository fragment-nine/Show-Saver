//! Audio engine — multi-device input management via cpal.
//!
//! Manages up to 3 audio input devices simultaneously, routes audio
//! to the LTC decoder and recording writers, and computes levels for
//! VU meters.

use anyhow::{Context, Result};
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{Device, Stream, StreamConfig};
use crossbeam_channel::{bounded, Receiver, Sender};
use parking_lot::Mutex;
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use super::audio_writer::RecordingSession;
use super::ltc_decoder::LtcDecoder;
use super::state_machine::{RecordingEvent, RecordingFSM};
use super::timecode::Timecode;

/// Info about an available audio input device.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioDeviceInfo {
    pub name: String,
    pub max_input_channels: u16,
    pub default_sample_rate: u32,
}

/// RMS and peak levels for VU meter display.
#[derive(Debug, Clone, Copy, Default, Serialize, Deserialize)]
pub struct AudioLevels {
    pub rms: f32,
    pub peak: f32,
}

/// Audio buffer message sent from cpal callbacks to the processing thread.
struct AudioBuffer {
    device_id: usize,
    samples: Vec<f32>,
    channels: u16,
}

/// Enumerate available audio input devices.
pub fn list_input_devices() -> Vec<AudioDeviceInfo> {
    let host = cpal::default_host();
    let mut devices = Vec::new();

    if let Ok(input_devices) = host.input_devices() {
        for dev in input_devices {
            let name = dev.name().unwrap_or_else(|_| "Unknown".to_string());
            let config = dev.default_input_config();

            if let Ok(cfg) = config {
                devices.push(AudioDeviceInfo {
                    name,
                    max_input_channels: cfg.channels(),
                    default_sample_rate: cfg.sample_rate().0,
                });
            }
        }
    }

    devices
}

/// Find a device by name.
fn find_device_by_name(name: &str) -> Result<Device> {
    let host = cpal::default_host();
    let devices = host.input_devices().context("Failed to enumerate devices")?;

    for dev in devices {
        if let Ok(dev_name) = dev.name() {
            if dev_name == name {
                return Ok(dev);
            }
        }
    }

    anyhow::bail!("Audio device not found: {name}")
}

/// Multi-device audio input engine.
///
/// Captures audio from configured devices, decodes LTC from the
/// timecode channel, and writes audio to recording files.
pub struct AudioEngine {
    sample_rate: u32,
    block_size: u32,

    // Device configuration
    tc_device_name: Option<String>,
    tc_channel: usize,
    pgm_device_name: Option<String>,
    pgm_channel: usize,

    // Running state
    streams: Vec<Stream>,
    processing_handle: Option<std::thread::JoinHandle<()>>,
    shutdown_tx: Option<Sender<()>>,

    // Shared state
    shared: Arc<SharedState>,
}

struct SharedState {
    current_tc: Mutex<Timecode>,
    tc_levels: Mutex<AudioLevels>,
    pgm_levels: Mutex<AudioLevels>,
    current_song: Mutex<String>,
    is_recording: Mutex<bool>,
}

impl AudioEngine {
    pub fn new(sample_rate: u32, block_size: u32) -> Self {
        Self {
            sample_rate,
            block_size,
            tc_device_name: None,
            tc_channel: 0,
            pgm_device_name: None,
            pgm_channel: 0,
            streams: Vec::new(),
            processing_handle: None,
            shutdown_tx: None,
            shared: Arc::new(SharedState {
                current_tc: Mutex::new(Timecode::default()),
                tc_levels: Mutex::new(AudioLevels::default()),
                pgm_levels: Mutex::new(AudioLevels::default()),
                current_song: Mutex::new(String::new()),
                is_recording: Mutex::new(false),
            }),
        }
    }

    /// Configure audio device routing.
    pub fn configure(
        &mut self,
        tc_device: &str,
        tc_channel: usize,
        pgm_device: Option<&str>,
        pgm_channel: usize,
    ) {
        self.tc_device_name = Some(tc_device.to_string());
        self.tc_channel = tc_channel;
        self.pgm_device_name = Some(pgm_device.unwrap_or(tc_device).to_string());
        self.pgm_channel = pgm_channel;
    }

    /// Start audio capture and processing.
    pub fn start(&mut self, mut fsm: RecordingFSM, mut session: RecordingSession) -> Result<()> {
        let tc_device_name = self.tc_device_name.as_ref().context("No TC device set")?;
        let pgm_device_name = self
            .pgm_device_name
            .as_ref()
            .unwrap_or(tc_device_name);

        // Channel for audio buffers from callbacks -> processing thread
        let (audio_tx, audio_rx): (Sender<AudioBuffer>, Receiver<AudioBuffer>) = bounded(256);

        // Channel for shutdown signal
        let (shutdown_tx, shutdown_rx) = bounded(1);
        self.shutdown_tx = Some(shutdown_tx);

        // Open streams for unique devices
        let tc_dev = find_device_by_name(tc_device_name)?;
        let tc_config = tc_dev.default_input_config()?;
        let tc_channels = tc_config.channels();

        let tc_tx = audio_tx.clone();
        let tc_stream = tc_dev.build_input_stream(
            &StreamConfig {
                channels: tc_channels,
                sample_rate: cpal::SampleRate(self.sample_rate),
                buffer_size: cpal::BufferSize::Fixed(self.block_size),
            },
            move |data: &[f32], _: &cpal::InputCallbackInfo| {
                let _ = tc_tx.try_send(AudioBuffer {
                    device_id: 0,
                    samples: data.to_vec(),
                    channels: tc_channels,
                });
            },
            |err| log::error!("TC audio stream error: {err}"),
            None,
        )?;

        self.streams.push(tc_stream);

        // Open PGM device if different from TC
        if pgm_device_name != tc_device_name {
            let pgm_dev = find_device_by_name(pgm_device_name)?;
            let pgm_config = pgm_dev.default_input_config()?;
            let pgm_channels = pgm_config.channels();

            let pgm_tx = audio_tx;
            let pgm_stream = pgm_dev.build_input_stream(
                &StreamConfig {
                    channels: pgm_channels,
                    sample_rate: cpal::SampleRate(self.sample_rate),
                    buffer_size: cpal::BufferSize::Fixed(self.block_size),
                },
                move |data: &[f32], _: &cpal::InputCallbackInfo| {
                    let _ = pgm_tx.try_send(AudioBuffer {
                        device_id: 1,
                        samples: data.to_vec(),
                        channels: pgm_channels,
                    });
                },
                |err| log::error!("PGM audio stream error: {err}"),
                None,
            )?;

            self.streams.push(pgm_stream);
        }

        // Start all streams
        for stream in &self.streams {
            stream.play()?;
        }

        // Spawn processing thread
        let shared = Arc::clone(&self.shared);
        let sample_rate = self.sample_rate;
        let tc_ch = self.tc_channel;
        let pgm_ch = self.pgm_channel;
        let same_device = self.tc_device_name == self.pgm_device_name;

        self.processing_handle = Some(std::thread::spawn(move || {
            let mut decoder = LtcDecoder::new(sample_rate, 30);

            loop {
                // Check for shutdown
                if shutdown_rx.try_recv().is_ok() {
                    break;
                }

                match audio_rx.recv_timeout(std::time::Duration::from_millis(100)) {
                    Ok(buf) => {
                        let channels = buf.channels as usize;

                        // Extract TC channel
                        if buf.device_id == 0 {
                            let tc_audio: Vec<f32> = buf
                                .samples
                                .iter()
                                .skip(tc_ch.min(channels - 1))
                                .step_by(channels)
                                .copied()
                                .collect();

                            // Compute TC levels
                            let levels = compute_levels(&tc_audio);
                            *shared.tc_levels.lock() = levels;

                            // Decode LTC
                            decoder.write_samples(&tc_audio);
                            let frames = decoder.read_frames();

                            for frame in &frames {
                                *shared.current_tc.lock() = *frame;
                                let events = fsm.update(frame.total_seconds());
                                handle_events(&events, &mut session, &shared);
                            }
                        }

                        // Extract PGM channel
                        let pgm_device_id = if same_device { 0 } else { 1 };
                        if buf.device_id == pgm_device_id {
                            let pgm_audio: Vec<f32> = buf
                                .samples
                                .iter()
                                .skip(pgm_ch.min(channels - 1))
                                .step_by(channels)
                                .copied()
                                .collect();

                            // Compute PGM levels
                            let levels = compute_levels(&pgm_audio);
                            *shared.pgm_levels.lock() = levels;

                            // Extract TC from same buffer if same device
                            let tc_for_write = if same_device {
                                let tc_audio: Vec<f32> = buf
                                    .samples
                                    .iter()
                                    .skip(tc_ch.min(channels - 1))
                                    .step_by(channels)
                                    .copied()
                                    .collect();
                                Some(tc_audio)
                            } else {
                                None
                            };

                            // Write to recording session
                            if let Err(e) = session.write(
                                &pgm_audio,
                                tc_for_write.as_deref(),
                            ) {
                                log::error!("Recording write error: {e}");
                            }
                        }
                    }
                    Err(crossbeam_channel::RecvTimeoutError::Timeout) => continue,
                    Err(crossbeam_channel::RecvTimeoutError::Disconnected) => break,
                }
            }

            if let Err(e) = session.stop_all() {
                log::error!("Error stopping recording session: {e}");
            }
        }));

        Ok(())
    }

    /// Stop audio capture.
    pub fn stop(&mut self) {
        // Signal shutdown
        if let Some(tx) = self.shutdown_tx.take() {
            let _ = tx.send(());
        }

        // Drop streams (stops capture)
        self.streams.clear();

        // Wait for processing thread
        if let Some(handle) = self.processing_handle.take() {
            let _ = handle.join();
        }
    }

    // -- Getters for UI polling --

    pub fn current_timecode(&self) -> Timecode {
        *self.shared.current_tc.lock()
    }

    pub fn tc_levels(&self) -> AudioLevels {
        *self.shared.tc_levels.lock()
    }

    pub fn pgm_levels(&self) -> AudioLevels {
        *self.shared.pgm_levels.lock()
    }

    pub fn current_song(&self) -> String {
        self.shared.current_song.lock().clone()
    }

    pub fn is_recording(&self) -> bool {
        *self.shared.is_recording.lock()
    }
}

/// Handle recording events from the FSM.
fn handle_events(
    events: &[RecordingEvent],
    session: &mut RecordingSession,
    shared: &SharedState,
) {
    for event in events {
        match event {
            RecordingEvent::SongStart { track_name, paths } => {
                if let (Some(pgm), Some(ltc)) = (paths.get("pgm"), paths.get("ltc")) {
                    if let Err(e) = session.start_song(pgm, ltc) {
                        log::error!("Failed to start song recording: {e}");
                    }
                }
                *shared.current_song.lock() = track_name.clone();
                *shared.is_recording.lock() = true;
                log::info!("Started recording: {track_name}");
            }
            RecordingEvent::SongStop => {
                if let Err(e) = session.stop_song() {
                    log::error!("Failed to stop song recording: {e}");
                }
                *shared.is_recording.lock() = false;
                log::info!("Stopped song recording");
            }
            RecordingEvent::LongStart { paths } => {
                if let (Some(pgm), Some(ltc)) = (paths.get("long_pgm"), paths.get("long_ltc")) {
                    if let Err(e) = session.start_long(pgm, ltc) {
                        log::error!("Failed to start long recording: {e}");
                    }
                }
            }
        }
    }
}

/// Compute RMS and peak audio levels.
fn compute_levels(samples: &[f32]) -> AudioLevels {
    if samples.is_empty() {
        return AudioLevels::default();
    }

    let mut sum_sq = 0.0f64;
    let mut peak = 0.0f32;

    for &s in samples {
        sum_sq += (s as f64) * (s as f64);
        let abs = s.abs();
        if abs > peak {
            peak = abs;
        }
    }

    AudioLevels {
        rms: (sum_sq / samples.len() as f64).sqrt() as f32,
        peak,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_levels_silence() {
        let samples = vec![0.0f32; 100];
        let levels = compute_levels(&samples);
        assert_eq!(levels.rms, 0.0);
        assert_eq!(levels.peak, 0.0);
    }

    #[test]
    fn test_compute_levels_sine() {
        // A simple test signal
        let samples: Vec<f32> = (0..100)
            .map(|i| (i as f32 * 0.1).sin())
            .collect();
        let levels = compute_levels(&samples);
        assert!(levels.rms > 0.0);
        assert!(levels.peak > 0.0);
        assert!(levels.peak <= 1.0);
        assert!(levels.rms <= levels.peak);
    }

    #[test]
    fn test_compute_levels_empty() {
        let levels = compute_levels(&[]);
        assert_eq!(levels.rms, 0.0);
        assert_eq!(levels.peak, 0.0);
    }
}
