//! Settings persistence via JSON.
//!
//! Stores user configuration (device selections, output folders, etc.)
//! in a JSON file loaded on startup and saved on exit.

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

/// Application settings.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct Settings {
    pub tc_device: Option<String>,
    pub tc_channel: usize,
    pub pgm_device: Option<String>,
    pub pgm_channel: usize,
    pub output_folder: String,
    pub track_master_csv: String,
    pub sample_rate: u32,
    pub fps: u32,
    pub auto_arm: bool,
    /// Enable per-song TC recording.
    pub enable_tc: bool,
    /// Enable per-song PGM recording.
    pub enable_pgm: bool,
    /// Enable long TC recording.
    pub enable_tc_long: bool,
    /// Enable long PGM recording.
    pub enable_pgm_long: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            tc_device: None,
            tc_channel: 0,
            pgm_device: None,
            pgm_channel: 0,
            output_folder: String::new(),
            track_master_csv: String::new(),
            sample_rate: 48000,
            fps: 30,
            auto_arm: false,
            enable_tc: true,
            enable_pgm: true,
            enable_tc_long: true,
            enable_pgm_long: true,
        }
    }
}

impl Settings {
    /// Default settings file path: `~/.showsaver/settings.json`.
    pub fn default_path() -> PathBuf {
        dirs::home_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join(".showsaver")
            .join("settings.json")
    }

    /// Load settings from a JSON file. Returns defaults if file doesn't exist.
    pub fn load(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }

        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read settings: {}", path.display()))?;

        let settings: Self = serde_json::from_str(&content)
            .with_context(|| format!("Failed to parse settings: {}", path.display()))?;

        Ok(settings)
    }

    /// Save settings to a JSON file.
    pub fn save(&self, path: &Path) -> Result<()> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }

        let json = serde_json::to_string_pretty(self)?;
        std::fs::write(path, json)
            .with_context(|| format!("Failed to write settings: {}", path.display()))?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_defaults() {
        let s = Settings::default();
        assert_eq!(s.sample_rate, 48000);
        assert_eq!(s.fps, 30);
        assert!(s.tc_device.is_none());
    }

    #[test]
    fn test_save_and_load() {
        let tmp = TempDir::new().unwrap();
        let path = tmp.path().join("settings.json");

        let mut s = Settings::default();
        s.output_folder = "/tmp/recordings".to_string();
        s.tc_channel = 1;
        s.save(&path).unwrap();

        let loaded = Settings::load(&path).unwrap();
        assert_eq!(loaded.output_folder, "/tmp/recordings");
        assert_eq!(loaded.tc_channel, 1);
    }

    #[test]
    fn test_load_nonexistent() {
        let path = Path::new("/tmp/nonexistent_showsaver_settings.json");
        let s = Settings::load(path).unwrap();
        assert_eq!(s.sample_rate, 48000); // defaults
    }

    #[test]
    fn test_serialization_roundtrip() {
        let s = Settings::default();
        let json = serde_json::to_string(&s).unwrap();
        let parsed: Settings = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed.sample_rate, s.sample_rate);
        assert_eq!(parsed.fps, s.fps);
    }
}
