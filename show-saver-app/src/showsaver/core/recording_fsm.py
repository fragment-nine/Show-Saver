"""Recording state machine.

Ported from lib/project1/start_stop/trigExecute.py.

Manages the lifecycle of recordings: detecting song changes,
timecode jumps, and coordinating start/stop of file writers.
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum, auto
from typing import Callable

from .file_manager import FileManager
from .track_master import Track, TrackMaster

logger = logging.getLogger(__name__)

# Timecode jump threshold in seconds (from trigExecute.py: current+240 < old)
TC_JUMP_THRESHOLD = 240


class RecordingState(Enum):
    IDLE = auto()
    ARMED = auto()
    RECORDING = auto()
    STOPPED = auto()


class RecordingFSM:
    """Finite state machine controlling recording start/stop/song changes.

    Mirrors the logic in trigExecute.py:
      - Detects timecode jumps (>240s difference)
      - Detects song changes via TrackMaster lookup
      - Triggers stop/start on transitions
    """

    def __init__(
        self,
        track_master: TrackMaster,
        file_manager: FileManager,
        on_song_start: Callable[[Track, dict], None] | None = None,
        on_song_stop: Callable[[], None] | None = None,
        on_long_start: Callable[[dict], None] | None = None,
    ) -> None:
        self.track_master = track_master
        self.file_manager = file_manager
        self.state = RecordingState.IDLE

        # Callbacks for the audio engine to wire up
        self._on_song_start = on_song_start
        self._on_song_stop = on_song_stop
        self._on_long_start = on_long_start

        self._current_song: Track | None = None
        self._prev_tc_seconds: float = 0.0
        self._first_tc_received = False
        self._is_armed = False

    def arm(self) -> None:
        """Arm the recorder — will start on first timecode received."""
        self.state = RecordingState.ARMED
        self._is_armed = True
        self._first_tc_received = False
        logger.info("Recording armed")

    def disarm(self) -> None:
        """Disarm without stopping an active recording."""
        self._is_armed = False
        if self.state == RecordingState.ARMED:
            self.state = RecordingState.IDLE
        logger.info("Recording disarmed")

    def stop(self) -> None:
        """Stop all recording."""
        if self.state == RecordingState.RECORDING:
            if self._on_song_stop:
                self._on_song_stop()
            self._current_song = None
            logger.info("Recording stopped")
        self.state = RecordingState.STOPPED
        self._is_armed = False

    def manual_start(self) -> None:
        """Start a manual recording (no timecode trigger)."""
        dt = datetime.now()
        paths = self.file_manager.prepare_song_recording("Manual_Start", dt)

        # Create a synthetic track for manual mode
        manual_track = Track(
            number=-1,
            name="Manual Start",
            tc_stamp="00:00:00:00",
            tc_seconds=0,
        )

        self._current_song = manual_track
        self.state = RecordingState.RECORDING

        if self._on_song_start:
            self._on_song_start(manual_track, paths)

        logger.info("Manual recording started")

    def update(self, total_seconds: float) -> None:
        """Process a new timecode reading.

        Called each time the LTC decoder produces a frame.
        This is the core logic ported from trigExecute.py.
        """
        if self.state == RecordingState.IDLE or self.state == RecordingState.STOPPED:
            return

        current_tc = total_seconds

        # First timecode after arming — start recording
        if self.state == RecordingState.ARMED and not self._first_tc_received:
            self._first_tc_received = True
            self._prev_tc_seconds = current_tc
            self._start_for_tc(current_tc)
            return

        # Detect timecode jump (mirrors: current+240 < old or current-240 > old)
        tc_diff = abs(current_tc - self._prev_tc_seconds)
        if tc_diff > TC_JUMP_THRESHOLD:
            logger.info(
                "Timecode jump detected: %.1f -> %.1f (diff=%.1f)",
                self._prev_tc_seconds, current_tc, tc_diff,
            )
            # Stop current song, will restart on next update
            if self._on_song_stop:
                self._on_song_stop()
            self._prev_tc_seconds = current_tc
            self._start_for_tc(current_tc)
            return

        # Detect song change
        new_song = self.track_master.get_current_song(current_tc)
        if new_song and self._current_song and new_song.name != self._current_song.name:
            logger.info(
                "Song changed: '%s' -> '%s'",
                self._current_song.name, new_song.name,
            )
            if self._on_song_stop:
                self._on_song_stop()
            self._start_song(new_song)

        self._prev_tc_seconds = current_tc

    def _start_for_tc(self, total_seconds: float) -> None:
        """Start recording based on current timecode position."""
        song = self.track_master.get_current_song(total_seconds)
        if song:
            self._start_song(song)
        else:
            logger.warning(
                "No track found for TC position %.1f seconds", total_seconds,
            )

    def _start_song(self, track: Track) -> None:
        """Start recording a specific song."""
        dt = datetime.now()
        paths = self.file_manager.prepare_song_recording(track.name, dt)

        self._current_song = track
        self.state = RecordingState.RECORDING

        if self._on_song_start:
            self._on_song_start(track, paths)

        logger.info("Recording song: '%s'", track.name)

    @property
    def current_song_name(self) -> str:
        if self._current_song:
            return self._current_song.name
        return ""

    @property
    def is_recording(self) -> bool:
        return self.state == RecordingState.RECORDING
