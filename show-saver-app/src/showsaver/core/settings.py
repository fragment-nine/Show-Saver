"""Settings persistence via JSON.

Stores user configuration (device selections, output folders, etc.)
in a JSON file that's loaded on startup and saved on exit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_SETTINGS = {
    "tc_device": None,
    "tc_channel": 0,
    "pgm_device": None,
    "pgm_channel": 0,
    "output_folder": "",
    "track_master_csv": "",
    "sample_rate": 48000,
    "fps": 30,
    "auto_arm": False,
}


class Settings:
    """Application settings backed by a JSON file."""

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            path = Path.home() / ".showsaver" / "settings.json"
        self._path = Path(path)
        self._data: dict[str, Any] = dict(DEFAULT_SETTINGS)

    def load(self) -> None:
        """Load settings from disk. Missing keys get defaults."""
        if self._path.exists():
            with open(self._path, encoding="utf-8") as f:
                saved = json.load(f)
            # Merge with defaults so new keys are always present
            for key, default in DEFAULT_SETTINGS.items():
                self._data[key] = saved.get(key, default)
            # Keep any extra keys the user may have added
            for key in saved:
                if key not in self._data:
                    self._data[key] = saved[key]

    def save(self) -> None:
        """Write settings to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    @property
    def path(self) -> Path:
        return self._path
