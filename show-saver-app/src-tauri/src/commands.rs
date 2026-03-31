//! Tauri IPC command handlers.
//!
//! These commands are called from the React frontend via `@tauri-apps/api`.

use crate::engine::audio_engine::{AudioDeviceInfo, AudioLevels, list_input_devices};
use crate::engine::timecode::Timecode;
use crate::engine::track_master::{Track, TrackMaster};
use crate::settings::Settings;
use std::path::Path;
use tauri::State;
use parking_lot::Mutex;

/// Shared app state accessible from commands.
pub struct AppState {
    pub settings: Mutex<Settings>,
    pub track_master: Mutex<TrackMaster>,
}

// -- Device commands --

#[tauri::command]
pub fn get_audio_devices() -> Vec<AudioDeviceInfo> {
    list_input_devices()
}

// -- TrackMaster commands --

#[tauri::command]
pub fn load_track_master(path: String, state: State<AppState>) -> Result<Vec<Track>, String> {
    let mut tm = state.track_master.lock();
    tm.load_csv(Path::new(&path)).map_err(|e| e.to_string())?;
    Ok(tm.tracks.clone())
}

#[tauri::command]
pub fn get_tracks(state: State<AppState>) -> Vec<Track> {
    state.track_master.lock().tracks.clone()
}

#[tauri::command]
pub fn save_track_master(path: String, state: State<AppState>) -> Result<(), String> {
    state
        .track_master
        .lock()
        .save_csv(Path::new(&path))
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn update_tracks(tracks: Vec<Track>, state: State<AppState>) {
    state.track_master.lock().tracks = tracks;
}

// -- Settings commands --

#[tauri::command]
pub fn get_settings(state: State<AppState>) -> Settings {
    state.settings.lock().clone()
}

#[tauri::command]
pub fn update_settings(settings: Settings, state: State<AppState>) -> Result<(), String> {
    let path = Settings::default_path();
    settings.save(&path).map_err(|e| e.to_string())?;
    *state.settings.lock() = settings;
    Ok(())
}

// -- Status commands (polled by frontend at ~30Hz) --

#[tauri::command]
pub fn get_status() -> EngineStatus {
    // In a full implementation, this reads from the shared AudioEngine state.
    // For now, return a placeholder.
    EngineStatus {
        timecode: Timecode::default(),
        tc_levels: AudioLevels::default(),
        pgm_levels: AudioLevels::default(),
        current_song: String::new(),
        is_recording: false,
        state: "idle".to_string(),
    }
}

#[derive(serde::Serialize)]
pub struct EngineStatus {
    pub timecode: Timecode,
    pub tc_levels: AudioLevels,
    pub pgm_levels: AudioLevels,
    pub current_song: String,
    pub is_recording: bool,
    pub state: String,
}
