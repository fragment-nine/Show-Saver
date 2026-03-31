//! ShowSaver — Cross-platform live show recording app driven by LTC timecode.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod engine;
mod settings;

use commands::AppState;
use engine::track_master::TrackMaster;
use parking_lot::Mutex;
use settings::Settings;

fn main() {
    env_logger::init();

    // Load settings
    let settings_path = Settings::default_path();
    let settings = Settings::load(&settings_path).unwrap_or_default();

    // Load track master if configured
    let mut track_master = TrackMaster::new();
    if !settings.track_master_csv.is_empty() {
        let path = std::path::Path::new(&settings.track_master_csv);
        if path.exists() {
            if let Err(e) = track_master.load_csv(path) {
                log::error!("Failed to load TrackMaster on startup: {e}");
            }
        }
    }

    let app_state = AppState {
        settings: Mutex::new(settings),
        track_master: Mutex::new(track_master),
    };

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            commands::get_audio_devices,
            commands::load_track_master,
            commands::get_tracks,
            commands::save_track_master,
            commands::update_tracks,
            commands::get_settings,
            commands::update_settings,
            commands::get_status,
        ])
        .run(tauri::generate_context!())
        .expect("error while running ShowSaver");
}
