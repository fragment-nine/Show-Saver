"""File and folder management for recordings.

Ported from lib/project1/start_stop/startLTC.py (makeFolders, naming)
and lib/SS_UI_v2/.../split_tc_pgm/chopexec1.py (file path routing).
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


def get_date_str(dt: datetime | None = None) -> str:
    """Return YYYYMMDD date string."""
    dt = dt or datetime.now()
    return dt.strftime("%Y%m%d")


def get_time_str(dt: datetime | None = None) -> str:
    """Return HHMMSS time string."""
    dt = dt or datetime.now()
    return dt.strftime("%H%M%S")


def make_folders(base_paths: list[str | Path], date_str: str) -> None:
    """Create date-based output folders and Long Recordings subfolders.

    Mirrors makeFolders() from startLTC.py — for each base path,
    creates:
      - {base}/{date}/
      - {base}/Long Recordings/{date}/
    """
    for base in base_paths:
        base = Path(base)
        day_dir = base / date_str
        long_dir = base / "Long Recordings" / date_str

        day_dir.mkdir(parents=True, exist_ok=True)
        long_dir.mkdir(parents=True, exist_ok=True)


def build_file_name(
    song_name: str,
    date_str: str,
    time_str: str,
    suffix: str,
    ext: str = ".wav",
) -> str:
    """Build a recording file name.

    Returns: "{date}/{song_name}_{date}_{time}_{suffix}{ext}"
    e.g. "20240315/Song_1_20240315_143022_pgm.wav"
    """
    return f"{date_str}/{song_name}_{date_str}_{time_str}_{suffix}{ext}"


def build_long_file_name(
    date_str: str,
    time_str: str,
    suffix: str,
    ext: str = ".wav",
) -> str:
    """Build a long-recording file name.

    Returns: "Long Recordings/{date}/Long_{date}_{time}_{suffix}{ext}"
    """
    return f"Long Recordings/{date_str}/Long_{date_str}_{time_str}_{suffix}{ext}"


class FileManager:
    """Manages output folders and file paths for all 4 recording streams."""

    def __init__(self, output_folder: str | Path) -> None:
        self.output_folder = Path(output_folder)

    def prepare_song_recording(
        self,
        song_name: str,
        dt: datetime | None = None,
    ) -> dict[str, Path]:
        """Create folders and return file paths for a new song recording.

        Returns a dict with keys: pgm, ltc, long_pgm, long_ltc
        """
        dt = dt or datetime.now()
        date_str = get_date_str(dt)
        time_str = get_time_str(dt)

        make_folders([self.output_folder], date_str)

        return {
            "pgm": self.output_folder / build_file_name(
                song_name, date_str, time_str, "pgm",
            ),
            "ltc": self.output_folder / build_file_name(
                song_name, date_str, time_str, "ltc",
            ),
            "long_pgm": self.output_folder / build_long_file_name(
                date_str, time_str, "pgm",
            ),
            "long_ltc": self.output_folder / build_long_file_name(
                date_str, time_str, "ltc",
            ),
        }
