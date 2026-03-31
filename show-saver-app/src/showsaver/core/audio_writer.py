"""Audio file writers with channel routing.

Handles writing program-only (pgm) and timecode+program (ltc) audio files
simultaneously. Supports WAV output via soundfile.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Literal

import numpy as np

try:
    import soundfile as sf
except ImportError:
    sf = None  # type: ignore[assignment]


class AudioWriter:
    """Writes audio samples to a WAV file in a background thread.

    Channel routing modes:
      - "pgm": Program audio on both channels (stereo)
      - "ltc": Timecode on left channel, program on right channel
    """

    def __init__(
        self,
        path: str | Path,
        sample_rate: int,
        mode: Literal["pgm", "ltc"] = "pgm",
        channels: int = 2,
    ) -> None:
        if sf is None:
            raise RuntimeError("soundfile is required for audio writing")

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._sample_rate = sample_rate
        self._mode = mode
        self._channels = channels
        self._lock = threading.Lock()

        self._file = sf.SoundFile(
            str(self.path),
            mode="w",
            samplerate=sample_rate,
            channels=channels,
            format="WAV",
            subtype="PCM_24",
        )
        self._closed = False

    def write(
        self,
        program_audio: np.ndarray,
        timecode_audio: np.ndarray | None = None,
    ) -> None:
        """Write audio samples to the file.

        Args:
            program_audio: Program audio samples (mono float32 array).
            timecode_audio: Timecode audio samples (mono float32 array).
                Only used in "ltc" mode.
        """
        with self._lock:
            if self._closed:
                return

            n = len(program_audio)

            if self._mode == "pgm":
                # Program on both channels
                stereo = np.column_stack([program_audio, program_audio])
            elif self._mode == "ltc":
                # TC on left, program on right
                if timecode_audio is None:
                    timecode_audio = np.zeros(n, dtype=np.float32)
                stereo = np.column_stack([
                    timecode_audio[:n],
                    program_audio[:n],
                ])
            else:
                stereo = np.column_stack([program_audio, program_audio])

            self._file.write(stereo)

    def close(self) -> None:
        """Flush and close the file."""
        with self._lock:
            if not self._closed:
                self._file.close()
                self._closed = True

    def __enter__(self) -> AudioWriter:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class RecordingSession:
    """Manages all 4 audio writers for a recording session.

    Writers:
      - pgm: Per-song program audio (both channels)
      - ltc: Per-song TC+program audio
      - long_pgm: Full-run program audio
      - long_ltc: Full-run TC+program audio
    """

    def __init__(self, sample_rate: int) -> None:
        self._sample_rate = sample_rate
        self._song_pgm: AudioWriter | None = None
        self._song_ltc: AudioWriter | None = None
        self._long_pgm: AudioWriter | None = None
        self._long_ltc: AudioWriter | None = None

    def start_long_recording(self, paths: dict[str, Path]) -> None:
        """Start the long recording writers."""
        self._long_pgm = AudioWriter(
            paths["long_pgm"], self._sample_rate, mode="pgm",
        )
        self._long_ltc = AudioWriter(
            paths["long_ltc"], self._sample_rate, mode="ltc",
        )

    def start_song(self, paths: dict[str, Path]) -> None:
        """Start per-song writers (closing any previous song)."""
        self.stop_song()
        self._song_pgm = AudioWriter(
            paths["pgm"], self._sample_rate, mode="pgm",
        )
        self._song_ltc = AudioWriter(
            paths["ltc"], self._sample_rate, mode="ltc",
        )

    def stop_song(self) -> None:
        """Close per-song writers."""
        if self._song_pgm:
            self._song_pgm.close()
            self._song_pgm = None
        if self._song_ltc:
            self._song_ltc.close()
            self._song_ltc = None

    def stop_all(self) -> None:
        """Close all writers."""
        self.stop_song()
        if self._long_pgm:
            self._long_pgm.close()
            self._long_pgm = None
        if self._long_ltc:
            self._long_ltc.close()
            self._long_ltc = None

    def write(
        self,
        program_audio: np.ndarray,
        timecode_audio: np.ndarray | None = None,
    ) -> None:
        """Write samples to all active writers."""
        if self._song_pgm:
            self._song_pgm.write(program_audio, timecode_audio)
        if self._song_ltc:
            self._song_ltc.write(program_audio, timecode_audio)
        if self._long_pgm:
            self._long_pgm.write(program_audio, timecode_audio)
        if self._long_ltc:
            self._long_ltc.write(program_audio, timecode_audio)

    @property
    def is_recording_song(self) -> bool:
        return self._song_pgm is not None

    @property
    def is_recording_long(self) -> bool:
        return self._long_pgm is not None
