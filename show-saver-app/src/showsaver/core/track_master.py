"""TrackMaster CSV parser and song detection.

Ported from:
  - lib/project1/start_stop/startLTC.py (song lookup logic)
  - lib/project1/track_master/process_cell_update.py (CSV processing)
  - lib/project1/track_master/reloadLTCExecute.py (CSV loading)
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from .timecode import stamp_to_int

# Characters illegal in file/folder names
_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')


def clean_song_name(name: str) -> str:
    """Remove filesystem-illegal characters from a song name."""
    return _ILLEGAL_CHARS.sub("_", name)


@dataclass
class Track:
    """A single track/song entry from the TrackMaster CSV."""

    number: int
    name: str
    tc_stamp: str
    tc_seconds: int
    show_order: int = 0
    in_show: bool = True
    status: str = ""
    file_folder_name: str = ""
    bpm: str = ""


@dataclass
class TrackMaster:
    """Manages the setlist / track master table.

    Loads from CSV, provides song lookup by timecode position.
    """

    tracks: list[Track] = field(default_factory=list)

    def load_csv(self, path: str | Path) -> None:
        """Load tracks from a TrackMaster CSV file.

        Expected columns (by header name): NAME, TC.
        Optional columns: TRACK #, SHOW ORDER, IN SHOW, STATUS,
        FILE/FOLDER NAME, BPM.
        """
        path = Path(path)
        self.tracks.clear()

        with open(path, newline="", encoding="utf-8-sig") as f:
            # Sniff delimiter
            sample = f.read(2048)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
            except csv.Error:
                dialect = csv.excel  # type: ignore[assignment]

            reader = csv.DictReader(f, dialect=dialect)
            for i, row in enumerate(reader):
                name_raw = row.get("NAME", "").strip()
                tc_raw = row.get("TC", "0:00:00").strip()
                if not name_raw:
                    continue

                name = clean_song_name(name_raw)
                tc_seconds = stamp_to_int(tc_raw)

                track = Track(
                    number=int(row.get("TRACK #", i)),
                    name=name,
                    tc_stamp=tc_raw,
                    tc_seconds=tc_seconds,
                    show_order=int(row.get("SHOW ORDER", i) or i),
                    in_show=row.get("IN SHOW", "TRUE").strip().upper() == "TRUE",
                    status=row.get("STATUS", "").strip(),
                    file_folder_name=row.get("FILE/FOLDER NAME", "").strip(),
                    bpm=row.get("BPM", "").strip(),
                )
                self.tracks.append(track)

        # Sort by timecode for correct boundary detection
        self.tracks.sort(key=lambda t: t.tc_seconds)

    def save_csv(self, path: str | Path) -> None:
        """Save tracks back to CSV."""
        path = Path(path)
        fieldnames = [
            "TRACK #", "SHOW ORDER", "IN SHOW", "STATUS",
            "NAME", "FILE/FOLDER NAME", "BPM", "TC",
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for t in self.tracks:
                writer.writerow({
                    "TRACK #": t.number,
                    "SHOW ORDER": t.show_order,
                    "IN SHOW": str(t.in_show).upper(),
                    "STATUS": t.status,
                    "NAME": t.name,
                    "FILE/FOLDER NAME": t.file_folder_name,
                    "BPM": t.bpm,
                    "TC": t.tc_stamp,
                })

    def get_current_song(self, total_seconds: float) -> Track | None:
        """Determine which song is playing based on current LTC position.

        Mirrors the logic from startLTC.py:
            for i in range(trackMaster.numRows):
                if ltcTotal < int(trackMaster[i,2]):
                    song = trackMaster[i-1, 1]
                    break

        Returns the track whose timecode boundary we've passed but
        haven't yet reached the next one.
        """
        if not self.tracks:
            return None

        for i, track in enumerate(self.tracks):
            if total_seconds < track.tc_seconds:
                if i == 0:
                    return None
                return self.tracks[i - 1]

        # Past all boundaries — we're in the last song
        return self.tracks[-1]
