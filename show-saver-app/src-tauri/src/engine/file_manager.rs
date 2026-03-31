//! File and folder management for recordings.
//!
//! Ported from lib/project1/start_stop/startLTC.py (makeFolders, naming)
//! and lib/SS_UI_v2/.../split_tc_pgm/chopexec1.py (file path routing).

use anyhow::Result;
use chrono::Local;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

/// Get current date as YYYYMMDD string.
pub fn get_date_str() -> String {
    Local::now().format("%Y%m%d").to_string()
}

/// Get current time as HHMMSS string.
pub fn get_time_str() -> String {
    Local::now().format("%H%M%S").to_string()
}

/// Create date-based output folders and Long Recordings subfolders.
///
/// Mirrors `makeFolders()` from `startLTC.py`:
/// For each base path, creates:
///   - `{base}/{date}/`
///   - `{base}/Long Recordings/{date}/`
pub fn make_folders(base_paths: &[&Path], date_str: &str) -> Result<()> {
    for base in base_paths {
        let day_dir = base.join(date_str);
        let long_dir = base.join("Long Recordings").join(date_str);

        fs::create_dir_all(&day_dir)?;
        fs::create_dir_all(&long_dir)?;
    }
    Ok(())
}

/// Build a recording file name.
///
/// Returns: `"{date}/{song_name}_{date}_{time}_{suffix}.wav"`
pub fn build_file_name(song_name: &str, date: &str, time: &str, suffix: &str, ext: &str) -> String {
    format!("{date}/{song_name}_{date}_{time}_{suffix}{ext}")
}

/// Build a long-recording file name.
///
/// Returns: `"Long Recordings/{date}/Long_{date}_{time}_{suffix}.wav"`
pub fn build_long_file_name(date: &str, time: &str, suffix: &str, ext: &str) -> String {
    format!("Long Recordings/{date}/Long_{date}_{time}_{suffix}{ext}")
}

/// Manages output folders and file paths for all 4 recording streams.
#[derive(Debug, Clone)]
pub struct FileManager {
    output_folder: PathBuf,
}

/// The 4 file paths for a recording session.
pub type RecordingPaths = HashMap<String, PathBuf>;

impl FileManager {
    pub fn new(output_folder: PathBuf) -> Self {
        Self { output_folder }
    }

    /// Set the output folder.
    pub fn set_output_folder(&mut self, path: PathBuf) {
        self.output_folder = path;
    }

    /// Create folders and return file paths for a new song recording.
    ///
    /// Returns a map with keys: `pgm`, `ltc`, `long_pgm`, `long_ltc`
    pub fn prepare_song_recording(&self, song_name: &str) -> Result<RecordingPaths> {
        let date = get_date_str();
        let time = get_time_str();
        let ext = ".wav";

        make_folders(&[self.output_folder.as_path()], &date)?;

        let mut paths = HashMap::new();

        paths.insert(
            "pgm".to_string(),
            self.output_folder
                .join(build_file_name(song_name, &date, &time, "pgm", ext)),
        );
        paths.insert(
            "ltc".to_string(),
            self.output_folder
                .join(build_file_name(song_name, &date, &time, "ltc", ext)),
        );
        paths.insert(
            "long_pgm".to_string(),
            self.output_folder
                .join(build_long_file_name(&date, &time, "pgm", ext)),
        );
        paths.insert(
            "long_ltc".to_string(),
            self.output_folder
                .join(build_long_file_name(&date, &time, "ltc", ext)),
        );

        Ok(paths)
    }

    pub fn output_folder(&self) -> &Path {
        &self.output_folder
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_build_file_name() {
        let name = build_file_name("Song_1", "20240315", "143022", "pgm", ".wav");
        assert_eq!(name, "20240315/Song_1_20240315_143022_pgm.wav");
    }

    #[test]
    fn test_build_long_file_name() {
        let name = build_long_file_name("20240315", "143022", "pgm", ".wav");
        assert_eq!(
            name,
            "Long Recordings/20240315/Long_20240315_143022_pgm.wav"
        );
    }

    #[test]
    fn test_make_folders() {
        let tmp = TempDir::new().unwrap();
        make_folders(&[tmp.path()], "20240315").unwrap();

        assert!(tmp.path().join("20240315").is_dir());
        assert!(tmp.path().join("Long Recordings/20240315").is_dir());
    }

    #[test]
    fn test_make_folders_idempotent() {
        let tmp = TempDir::new().unwrap();
        make_folders(&[tmp.path()], "20240315").unwrap();
        make_folders(&[tmp.path()], "20240315").unwrap(); // should not panic
        assert!(tmp.path().join("20240315").is_dir());
    }

    #[test]
    fn test_prepare_song_recording() {
        let tmp = TempDir::new().unwrap();
        let fm = FileManager::new(tmp.path().to_path_buf());
        let paths = fm.prepare_song_recording("Song_1").unwrap();

        assert!(paths.contains_key("pgm"));
        assert!(paths.contains_key("ltc"));
        assert!(paths.contains_key("long_pgm"));
        assert!(paths.contains_key("long_ltc"));

        let pgm = paths["pgm"].to_string_lossy();
        assert!(pgm.contains("Song_1"));
        assert!(pgm.ends_with("_pgm.wav"));

        let long = paths["long_pgm"].to_string_lossy();
        assert!(long.contains("Long Recordings"));
    }
}
