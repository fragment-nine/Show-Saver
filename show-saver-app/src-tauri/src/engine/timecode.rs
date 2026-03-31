//! Timecode parsing and conversion utilities.
//!
//! Ported from scripts/tools.py and lib/project1/track_master/tools.py.

use regex::Regex;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::sync::LazyLock;

static TC_SPLIT: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[:;]").unwrap());

/// A decoded timecode value.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct Timecode {
    pub hours: u32,
    pub minutes: u32,
    pub seconds: u32,
    pub frames: u32,
}

impl Timecode {
    pub fn new(hours: u32, minutes: u32, seconds: u32, frames: u32) -> Self {
        Self {
            hours,
            minutes,
            seconds,
            frames,
        }
    }

    /// Total time in integer seconds (frames are ignored).
    /// Matches the original TouchDesigner `stampToInt` behavior.
    pub fn total_seconds(&self) -> u32 {
        self.hours * 3600 + self.minutes * 60 + self.seconds
    }

    /// Create a Timecode from total seconds (frames = 0).
    pub fn from_total_seconds(total: u32) -> Self {
        Self {
            hours: total / 3600,
            minutes: (total % 3600) / 60,
            seconds: total % 60,
            frames: 0,
        }
    }
}

impl fmt::Display for Timecode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{:02}:{:02}:{:02}:{:02}",
            self.hours, self.minutes, self.seconds, self.frames
        )
    }
}

/// Parse a timecode stamp string into total seconds.
///
/// Supports variable formats:
///   - `"HH:MM:SS:FF"` → hours*3600 + minutes*60 + seconds
///   - `"HH:MM:SS"` → same (frames = 0)
///   - `"MM:SS"` → minutes*60 + seconds
///   - `"SS"` → seconds
///
/// Separators can be colons or semicolons.
/// Frames are parsed but not included in the total (integer seconds).
pub fn stamp_to_int(stamp: &str) -> u32 {
    let stamp = stamp.trim();
    let parts: Vec<&str> = TC_SPLIT.split(stamp).filter(|s| !s.is_empty()).collect();

    let (h, m, s) = match parts.len() {
        4.. => (parts[0], parts[1], parts[2]),
        3 => (parts[0], parts[1], parts[2]),
        2 => ("0", parts[0], parts[1]),
        1 => ("0", "0", parts[0]),
        _ => ("0", "0", "0"),
    };

    let h: u32 = h.parse().unwrap_or(0);
    let m: u32 = m.parse().unwrap_or(0);
    let s: u32 = s.parse().unwrap_or(0);

    h * 3600 + m * 60 + s
}

/// Parse a timecode stamp string into a full Timecode struct.
pub fn parse_stamp(stamp: &str) -> Timecode {
    let stamp = stamp.trim();
    let parts: Vec<&str> = TC_SPLIT.split(stamp).filter(|s| !s.is_empty()).collect();

    let (h, m, s, f) = match parts.len() {
        4.. => (parts[0], parts[1], parts[2], parts[3]),
        3 => (parts[0], parts[1], parts[2], "0"),
        2 => ("0", parts[0], parts[1], "0"),
        1 => ("0", "0", parts[0], "0"),
        _ => ("0", "0", "0", "0"),
    };

    Timecode {
        hours: h.parse().unwrap_or(0),
        minutes: m.parse().unwrap_or(0),
        seconds: s.parse().unwrap_or(0),
        frames: f.parse().unwrap_or(0),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_stamp_to_int_full() {
        assert_eq!(stamp_to_int("01:02:03:04"), 3723);
    }

    #[test]
    fn test_stamp_to_int_zero() {
        assert_eq!(stamp_to_int("0:00:00"), 0);
    }

    #[test]
    fn test_stamp_to_int_hours() {
        assert_eq!(stamp_to_int("1:00:00:00"), 3600);
    }

    #[test]
    fn test_stamp_to_int_ten_minutes() {
        assert_eq!(stamp_to_int("0:10:00"), 600);
    }

    #[test]
    fn test_stamp_to_int_semicolons() {
        assert_eq!(stamp_to_int("01;02;03;04"), 3723);
    }

    #[test]
    fn test_stamp_to_int_two_parts() {
        assert_eq!(stamp_to_int("05:30"), 330);
    }

    #[test]
    fn test_stamp_to_int_single() {
        assert_eq!(stamp_to_int("45"), 45);
    }

    #[test]
    fn test_stamp_to_int_large_tc() {
        // 4:20:00 from TrackMaster
        assert_eq!(stamp_to_int("4:20:00"), 15600);
    }

    #[test]
    fn test_timecode_display() {
        let tc = Timecode::new(1, 2, 3, 4);
        assert_eq!(tc.to_string(), "01:02:03:04");
    }

    #[test]
    fn test_timecode_total_seconds() {
        let tc = Timecode::new(1, 2, 3, 4);
        assert_eq!(tc.total_seconds(), 3723);
    }

    #[test]
    fn test_from_total_seconds() {
        let tc = Timecode::from_total_seconds(3723);
        assert_eq!(tc.hours, 1);
        assert_eq!(tc.minutes, 2);
        assert_eq!(tc.seconds, 3);
        assert_eq!(tc.frames, 0);
    }

    #[test]
    fn test_parse_stamp() {
        let tc = parse_stamp("01:02:03:15");
        assert_eq!(tc.hours, 1);
        assert_eq!(tc.minutes, 2);
        assert_eq!(tc.seconds, 3);
        assert_eq!(tc.frames, 15);
    }
}
