//! Recording state machine.
//!
//! Ported from lib/project1/start_stop/trigExecute.py.
//!
//! Manages the lifecycle of recordings: detecting song changes,
//! timecode jumps, and coordinating start/stop of file writers.

use serde::{Deserialize, Serialize};
use super::file_manager::{FileManager, RecordingPaths};
use super::track_master::{Track, TrackMaster};

/// Timecode jump threshold in seconds (from trigExecute.py: current+240 < old).
const TC_JUMP_THRESHOLD: u32 = 240;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum RecordingState {
    Idle,
    Armed,
    Recording,
    Stopped,
}

/// Events emitted by the state machine for the audio engine to act on.
#[derive(Debug, Clone)]
pub enum RecordingEvent {
    /// Start recording a song — open per-song file writers.
    SongStart {
        track_name: String,
        paths: RecordingPaths,
    },
    /// Stop the current per-song recording.
    SongStop,
    /// Start the long (full-run) recording.
    LongStart { paths: RecordingPaths },
}

/// Finite state machine controlling recording start/stop/song changes.
///
/// Mirrors the logic in `trigExecute.py`:
///   - Detects timecode jumps (>240s difference)
///   - Detects song changes via TrackMaster lookup
///   - Triggers stop/start on transitions
pub struct RecordingFSM {
    track_master: TrackMaster,
    file_manager: FileManager,
    state: RecordingState,
    current_song: Option<Track>,
    prev_tc_seconds: u32,
    first_tc_received: bool,
}

impl RecordingFSM {
    pub fn new(track_master: TrackMaster, file_manager: FileManager) -> Self {
        Self {
            track_master,
            file_manager,
            state: RecordingState::Idle,
            current_song: None,
            prev_tc_seconds: 0,
            first_tc_received: false,
        }
    }

    pub fn state(&self) -> RecordingState {
        self.state
    }

    pub fn current_song_name(&self) -> Option<&str> {
        self.current_song.as_ref().map(|t| t.name.as_str())
    }

    pub fn is_recording(&self) -> bool {
        self.state == RecordingState::Recording
    }

    pub fn track_master(&self) -> &TrackMaster {
        &self.track_master
    }

    pub fn track_master_mut(&mut self) -> &mut TrackMaster {
        &mut self.track_master
    }

    pub fn file_manager(&self) -> &FileManager {
        &self.file_manager
    }

    pub fn file_manager_mut(&mut self) -> &mut FileManager {
        &mut self.file_manager
    }

    /// Arm the recorder — will start on first timecode received.
    pub fn arm(&mut self) -> Vec<RecordingEvent> {
        self.state = RecordingState::Armed;
        self.first_tc_received = false;
        log::info!("Recording armed");
        vec![]
    }

    /// Disarm without stopping an active recording.
    pub fn disarm(&mut self) {
        if self.state == RecordingState::Armed {
            self.state = RecordingState::Idle;
        }
        log::info!("Recording disarmed");
    }

    /// Stop all recording.
    pub fn stop(&mut self) -> Vec<RecordingEvent> {
        let mut events = vec![];
        if self.state == RecordingState::Recording {
            events.push(RecordingEvent::SongStop);
            self.current_song = None;
            log::info!("Recording stopped");
        }
        self.state = RecordingState::Stopped;
        events
    }

    /// Start a manual recording (no timecode trigger).
    pub fn manual_start(&mut self) -> Vec<RecordingEvent> {
        let song_name = "Manual_Start";
        let paths = match self.file_manager.prepare_song_recording(song_name) {
            Ok(p) => p,
            Err(e) => {
                log::error!("Failed to prepare manual recording: {e}");
                return vec![];
            }
        };

        let track = Track {
            number: -1,
            name: "Manual Start".to_string(),
            tc_stamp: "00:00:00:00".to_string(),
            tc_seconds: 0,
            show_order: -1,
            in_show: false,
            status: String::new(),
            file_folder_name: String::new(),
            bpm: String::new(),
        };

        self.current_song = Some(track);
        self.state = RecordingState::Recording;
        log::info!("Manual recording started");

        vec![RecordingEvent::SongStart {
            track_name: song_name.to_string(),
            paths,
        }]
    }

    /// Process a new timecode reading.
    ///
    /// Called each time the LTC decoder produces a frame.
    /// This is the core logic ported from `trigExecute.py`.
    pub fn update(&mut self, total_seconds: u32) -> Vec<RecordingEvent> {
        match self.state {
            RecordingState::Idle | RecordingState::Stopped => return vec![],
            _ => {}
        }

        // First timecode after arming — start recording
        if self.state == RecordingState::Armed && !self.first_tc_received {
            self.first_tc_received = true;
            self.prev_tc_seconds = total_seconds;
            return self.start_for_tc(total_seconds);
        }

        let mut events = vec![];

        // Detect timecode jump (mirrors: current+240 < old or current-240 > old)
        let tc_diff = total_seconds.abs_diff(self.prev_tc_seconds);
        if tc_diff > TC_JUMP_THRESHOLD {
            log::info!(
                "Timecode jump detected: {} -> {} (diff={})",
                self.prev_tc_seconds,
                total_seconds,
                tc_diff
            );
            events.push(RecordingEvent::SongStop);
            self.prev_tc_seconds = total_seconds;
            events.extend(self.start_for_tc(total_seconds));
            return events;
        }

        // Detect song change
        let new_song = self.track_master.get_current_song(total_seconds).cloned();
        if let Some(ref new) = new_song {
            let changed = match &self.current_song {
                Some(current) => current.name != new.name,
                None => true,
            };

            if changed {
                log::info!(
                    "Song changed: '{}' -> '{}'",
                    self.current_song
                        .as_ref()
                        .map(|t| t.name.as_str())
                        .unwrap_or("none"),
                    new.name
                );
                events.push(RecordingEvent::SongStop);
                events.extend(self.start_song(new.clone()));
            }
        }

        self.prev_tc_seconds = total_seconds;
        events
    }

    fn start_for_tc(&mut self, total_seconds: u32) -> Vec<RecordingEvent> {
        if let Some(track) = self.track_master.get_current_song(total_seconds).cloned() {
            self.start_song(track)
        } else {
            log::warn!("No track found for TC position {}s", total_seconds);
            vec![]
        }
    }

    fn start_song(&mut self, track: Track) -> Vec<RecordingEvent> {
        let paths = match self.file_manager.prepare_song_recording(&track.name) {
            Ok(p) => p,
            Err(e) => {
                log::error!("Failed to prepare recording for '{}': {e}", track.name);
                return vec![];
            }
        };

        let name = track.name.clone();
        self.current_song = Some(track);
        self.state = RecordingState::Recording;
        log::info!("Recording song: '{name}'");

        vec![RecordingEvent::SongStart {
            track_name: name,
            paths,
        }]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::{NamedTempFile, TempDir};

    fn make_track_master() -> (TrackMaster, TempDir) {
        let mut f = NamedTempFile::new().unwrap();
        writeln!(
            f,
            "TRACK #,SHOW ORDER,IN SHOW,STATUS,NAME,FILE/FOLDER NAME,BPM,TC"
        )
        .unwrap();
        writeln!(f, "0,0,TRUE,,Intro,,,0:00:00").unwrap();
        writeln!(f, "1,1,TRUE,,Song A,,,0:10:00").unwrap();
        writeln!(f, "2,2,TRUE,,Song B,,,0:20:00").unwrap();

        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();

        let tmp = TempDir::new().unwrap();
        (tm, tmp)
    }

    #[test]
    fn test_initial_state() {
        let (tm, tmp) = make_track_master();
        let fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        assert_eq!(fsm.state(), RecordingState::Idle);
    }

    #[test]
    fn test_arm() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        fsm.arm();
        assert_eq!(fsm.state(), RecordingState::Armed);
    }

    #[test]
    fn test_arm_and_receive_tc() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        fsm.arm();
        let events = fsm.update(300); // 5 minutes — should be in "Intro"

        assert_eq!(fsm.state(), RecordingState::Recording);
        assert!(events.iter().any(|e| matches!(e, RecordingEvent::SongStart { .. })));
        assert_eq!(fsm.current_song_name(), Some("Intro"));
    }

    #[test]
    fn test_song_change() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        fsm.arm();
        fsm.update(300); // In "Intro"
        let events = fsm.update(601); // Now in "Song A"

        assert!(events.iter().any(|e| matches!(e, RecordingEvent::SongStop)));
        assert!(events.iter().any(|e| matches!(e, RecordingEvent::SongStart { ref track_name, .. } if track_name == "Song A")));
    }

    #[test]
    fn test_tc_jump() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        fsm.arm();
        fsm.update(300); // In Intro
        let events = fsm.update(3000); // Jump > 240s

        assert!(events.iter().any(|e| matches!(e, RecordingEvent::SongStop)));
    }

    #[test]
    fn test_manual_start() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        let events = fsm.manual_start();

        assert_eq!(fsm.state(), RecordingState::Recording);
        assert_eq!(fsm.current_song_name(), Some("Manual Start"));
        assert!(!events.is_empty());
    }

    #[test]
    fn test_stop() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        fsm.arm();
        fsm.update(300);
        let events = fsm.stop();

        assert_eq!(fsm.state(), RecordingState::Stopped);
        assert!(events.iter().any(|e| matches!(e, RecordingEvent::SongStop)));
    }

    #[test]
    fn test_idle_ignores_update() {
        let (tm, tmp) = make_track_master();
        let mut fsm = RecordingFSM::new(tm, FileManager::new(tmp.path().to_path_buf()));
        let events = fsm.update(300);
        assert!(events.is_empty());
        assert_eq!(fsm.state(), RecordingState::Idle);
    }
}
