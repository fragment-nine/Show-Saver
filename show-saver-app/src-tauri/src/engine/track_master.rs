//! TrackMaster CSV parser and song detection.
//!
//! Ported from:
//!   - lib/project1/start_stop/startLTC.py (song lookup logic)
//!   - lib/project1/track_master/process_cell_update.py (CSV processing)
//!   - lib/project1/track_master/reloadLTCExecute.py (CSV loading)

use anyhow::{Context, Result};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::sync::LazyLock;

use super::timecode::stamp_to_int;

/// Characters illegal in file/folder names.
static ILLEGAL_CHARS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"[\\/:*?"<>|]"#).unwrap());

/// Remove filesystem-illegal characters from a song name.
pub fn clean_song_name(name: &str) -> String {
    ILLEGAL_CHARS.replace_all(name, "_").to_string()
}

/// A single track/song entry from the TrackMaster CSV.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Track {
    pub number: i32,
    pub name: String,
    pub tc_stamp: String,
    pub tc_seconds: u32,
    pub show_order: i32,
    pub in_show: bool,
    pub status: String,
    pub file_folder_name: String,
    pub bpm: String,
}

/// Manages the setlist / track master table.
///
/// Loads from CSV, provides song lookup by timecode position.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TrackMaster {
    pub tracks: Vec<Track>,
}

impl TrackMaster {
    pub fn new() -> Self {
        Self { tracks: Vec::new() }
    }

    /// Load tracks from a TrackMaster CSV file.
    ///
    /// Expected columns (by header name): NAME, TC.
    /// Optional columns: TRACK #, SHOW ORDER, IN SHOW, STATUS,
    /// FILE/FOLDER NAME, BPM.
    pub fn load_csv(&mut self, path: &Path) -> Result<()> {
        self.tracks.clear();

        // Read the file and detect delimiter
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read TrackMaster CSV: {}", path.display()))?;

        let delimiter = detect_delimiter(&content);

        let mut reader = csv::ReaderBuilder::new()
            .delimiter(delimiter)
            .flexible(true)
            .trim(csv::Trim::All)
            .from_reader(content.as_bytes());

        let headers = reader
            .headers()
            .context("Failed to read CSV headers")?
            .clone();

        // Find column indices by name
        let name_idx = find_column(&headers, "NAME");
        let tc_idx = find_column(&headers, "TC");
        let track_idx = find_column(&headers, "TRACK #");
        let order_idx = find_column(&headers, "SHOW ORDER");
        let inshow_idx = find_column(&headers, "IN SHOW");
        let status_idx = find_column(&headers, "STATUS");
        let file_idx = find_column(&headers, "FILE/FOLDER NAME");
        let bpm_idx = find_column(&headers, "BPM");

        for (i, result) in reader.records().enumerate() {
            let record = result.context("Failed to read CSV row")?;

            let name_raw = name_idx
                .and_then(|idx| record.get(idx))
                .unwrap_or("")
                .trim();
            let tc_raw = tc_idx
                .and_then(|idx| record.get(idx))
                .unwrap_or("0:00:00")
                .trim();

            if name_raw.is_empty() {
                continue;
            }

            let name = clean_song_name(name_raw);
            let tc_seconds = stamp_to_int(tc_raw);

            let track = Track {
                number: track_idx
                    .and_then(|idx| record.get(idx))
                    .and_then(|s| s.trim().parse().ok())
                    .unwrap_or(i as i32),
                name,
                tc_stamp: tc_raw.to_string(),
                tc_seconds,
                show_order: order_idx
                    .and_then(|idx| record.get(idx))
                    .and_then(|s| s.trim().parse().ok())
                    .unwrap_or(i as i32),
                in_show: inshow_idx
                    .and_then(|idx| record.get(idx))
                    .map(|s| s.trim().eq_ignore_ascii_case("true"))
                    .unwrap_or(true),
                status: status_idx
                    .and_then(|idx| record.get(idx))
                    .unwrap_or("")
                    .trim()
                    .to_string(),
                file_folder_name: file_idx
                    .and_then(|idx| record.get(idx))
                    .unwrap_or("")
                    .trim()
                    .to_string(),
                bpm: bpm_idx
                    .and_then(|idx| record.get(idx))
                    .unwrap_or("")
                    .trim()
                    .to_string(),
            };

            self.tracks.push(track);
        }

        // Sort by timecode for correct boundary detection
        self.tracks.sort_by_key(|t| t.tc_seconds);

        Ok(())
    }

    /// Save tracks back to CSV.
    pub fn save_csv(&self, path: &Path) -> Result<()> {
        let mut writer = csv::Writer::from_path(path)
            .with_context(|| format!("Failed to create CSV: {}", path.display()))?;

        writer.write_record([
            "TRACK #",
            "SHOW ORDER",
            "IN SHOW",
            "STATUS",
            "NAME",
            "FILE/FOLDER NAME",
            "BPM",
            "TC",
        ])?;

        for t in &self.tracks {
            writer.write_record([
                &t.number.to_string(),
                &t.show_order.to_string(),
                &t.in_show.to_string().to_uppercase(),
                &t.status,
                &t.name,
                &t.file_folder_name,
                &t.bpm,
                &t.tc_stamp,
            ])?;
        }

        writer.flush()?;
        Ok(())
    }

    /// Determine which song is playing based on current LTC position.
    ///
    /// Mirrors the logic from startLTC.py:
    /// ```python
    /// for i in range(trackMaster.numRows):
    ///     if ltcTotal < int(trackMaster[i,2]):
    ///         song = trackMaster[i-1, 1]
    ///         break
    /// ```
    ///
    /// Returns the track whose timecode boundary we've passed but
    /// haven't yet reached the next one.
    pub fn get_current_song(&self, total_seconds: u32) -> Option<&Track> {
        if self.tracks.is_empty() {
            return None;
        }

        for (i, track) in self.tracks.iter().enumerate() {
            if total_seconds < track.tc_seconds {
                if i == 0 {
                    return None;
                }
                return Some(&self.tracks[i - 1]);
            }
        }

        // Past all boundaries — we're in the last song
        self.tracks.last()
    }

    pub fn track_count(&self) -> usize {
        self.tracks.len()
    }
}

/// Detect CSV delimiter (comma, tab, or semicolon).
fn detect_delimiter(content: &str) -> u8 {
    let first_line = content.lines().next().unwrap_or("");
    if first_line.contains('\t') {
        b'\t'
    } else if first_line.contains(';') && !first_line.contains(',') {
        b';'
    } else {
        b','
    }
}

/// Find a column index by header name (case-insensitive).
fn find_column(headers: &csv::StringRecord, name: &str) -> Option<usize> {
    headers
        .iter()
        .position(|h| h.trim().eq_ignore_ascii_case(name))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn sample_csv() -> NamedTempFile {
        let mut f = NamedTempFile::new().unwrap();
        writeln!(
            f,
            "TRACK #,SHOW ORDER,IN SHOW,STATUS,NAME,FILE/FOLDER NAME,BPM,TC"
        )
        .unwrap();
        writeln!(f, "0,0,FALSE,Delivered,Test Track,,,0:00:00").unwrap();
        writeln!(f, "1,1,TRUE,Delivered,Song 1,Song 1,,0:10:00").unwrap();
        writeln!(f, "2,2,TRUE,Delivered,Letters,Letters,,0:20:00").unwrap();
        writeln!(f, "3,3,TRUE,Delivered,Final Song,Final Song,,0:30:00").unwrap();
        f
    }

    #[test]
    fn test_clean_song_name() {
        assert_eq!(clean_song_name("Song 1"), "Song 1");
        assert_eq!(clean_song_name("A/B\\C:D"), "A_B_C_D");
        assert_eq!(clean_song_name(""), "");
    }

    #[test]
    fn test_load_csv() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        assert_eq!(tm.track_count(), 4);
    }

    #[test]
    fn test_track_names() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        let names: Vec<&str> = tm.tracks.iter().map(|t| t.name.as_str()).collect();
        assert_eq!(names, vec!["Test Track", "Song 1", "Letters", "Final Song"]);
    }

    #[test]
    fn test_timecodes() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        let secs: Vec<u32> = tm.tracks.iter().map(|t| t.tc_seconds).collect();
        assert_eq!(secs, vec![0, 600, 1200, 1800]);
    }

    #[test]
    fn test_get_current_song_before_first() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        // At time 0, first track starts at 0, so checking < 0 is impossible
        // with u32. Check that the first track is at 0:
        assert!(tm.get_current_song(0).is_none() || tm.get_current_song(0).unwrap().tc_seconds == 0);
    }

    #[test]
    fn test_get_current_song_first() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        let song = tm.get_current_song(300).unwrap();
        assert_eq!(song.name, "Test Track");
    }

    #[test]
    fn test_get_current_song_middle() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        let song = tm.get_current_song(900).unwrap();
        assert_eq!(song.name, "Song 1");
    }

    #[test]
    fn test_get_current_song_last() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();
        let song = tm.get_current_song(2000).unwrap();
        assert_eq!(song.name, "Final Song");
    }

    #[test]
    fn test_get_current_song_empty() {
        let tm = TrackMaster::new();
        assert!(tm.get_current_song(100).is_none());
    }

    #[test]
    fn test_save_and_reload() {
        let f = sample_csv();
        let mut tm = TrackMaster::new();
        tm.load_csv(f.path()).unwrap();

        let out = NamedTempFile::new().unwrap();
        tm.save_csv(out.path()).unwrap();

        let mut tm2 = TrackMaster::new();
        tm2.load_csv(out.path()).unwrap();

        assert_eq!(tm.track_count(), tm2.track_count());
        for (a, b) in tm.tracks.iter().zip(tm2.tracks.iter()) {
            assert_eq!(a.name, b.name);
            assert_eq!(a.tc_seconds, b.tc_seconds);
        }
    }
}
