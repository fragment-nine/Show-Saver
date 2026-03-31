"""Timecode parsing and conversion utilities.

Ported from scripts/tools.py and lib/project1/track_master/tools.py.
"""

from __future__ import annotations

import re


def stamp_to_int(stamp: str) -> int:
    """Convert a timecode stamp (HH:MM:SS:FF) to total seconds.

    Supports variable-length formats:
      - "HH:MM:SS:FF" -> hours*3600 + minutes*60 + seconds
      - "MM:SS:FF"    -> minutes*60 + seconds
      - "MM:SS"       -> minutes*60 + seconds
      - "SS"          -> seconds

    Separators can be colons or semicolons.  Frames are parsed but
    not added to the total (integer seconds only, matching the
    original TouchDesigner implementation).
    """
    stamp = str(stamp).strip()
    parts = [p for p in re.split(r"[:;]", stamp) if p != ""]

    if len(parts) >= 4:
        h, m, s = parts[0], parts[1], parts[2]
    elif len(parts) == 3:
        h, m, s = parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        h, m, s = "0", parts[0], parts[1]
    else:
        h, m, s = "0", "0", parts[0] if parts else "0"

    return int(h or 0) * 3600 + int(m or 0) * 60 + int(s or 0)


def int_to_stamp(total_seconds: int, fps: int = 30) -> str:
    """Convert total seconds back to HH:MM:SS:00 timecode string."""
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}:00"
