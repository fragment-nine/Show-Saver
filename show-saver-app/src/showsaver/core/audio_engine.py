"""Audio engine — multi-device input management via sounddevice.

Manages up to 3 audio input devices simultaneously, routes audio
to the LTC decoder and recording writers, and computes levels for
VU meters.
"""

from __future__ import annotations

import logging
import queue
import threading
from dataclasses import dataclass
from typing import Callable

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None  # type: ignore[assignment]

from .audio_writer import RecordingSession
from .ltc_decoder import LTCFrame, create_decoder
from .recording_fsm import RecordingFSM

logger = logging.getLogger(__name__)


@dataclass
class AudioDeviceInfo:
    """Info about an available audio input device."""

    index: int
    name: str
    max_input_channels: int
    default_samplerate: float


@dataclass
class AudioLevels:
    """RMS and peak levels for VU meter display."""

    rms: float = 0.0
    peak: float = 0.0


def list_input_devices() -> list[AudioDeviceInfo]:
    """Enumerate available audio input devices."""
    if sd is None:
        return []

    devices = []
    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:  # type: ignore[index]
            devices.append(AudioDeviceInfo(
                index=i,
                name=dev["name"],  # type: ignore[index]
                max_input_channels=dev["max_input_channels"],  # type: ignore[index]
                default_samplerate=dev["default_samplerate"],  # type: ignore[index]
            ))
    return devices


class AudioEngine:
    """Multi-device audio input engine.

    Captures audio from up to 3 devices, decodes LTC from the
    timecode channel, and writes audio to recording files.

    Configuration:
      - tc_device: Device index for timecode input
      - tc_channel: Which channel on that device carries LTC (0-based)
      - pgm_device: Device index for program audio
      - pgm_channel: Which channel carries program audio (0-based)
      - These can be the same device with different channels.
    """

    def __init__(
        self,
        sample_rate: int = 48000,
        block_size: int = 1024,
        fps: int = 30,
    ) -> None:
        if sd is None:
            raise RuntimeError("sounddevice is required")

        self._sample_rate = sample_rate
        self._block_size = block_size
        self._fps = fps

        # Device configuration
        self._tc_device: int | None = None
        self._tc_channel: int = 0
        self._pgm_device: int | None = None
        self._pgm_channel: int = 0

        # Streams
        self._streams: list[sd.InputStream] = []

        # Processing components
        self._ltc_decoder = create_decoder(sample_rate, fps)
        self._recording: RecordingSession | None = None
        self._fsm: RecordingFSM | None = None

        # Audio buffer queue for processing off the audio callback thread
        self._audio_queue: queue.Queue = queue.Queue(maxsize=256)
        self._processing_thread: threading.Thread | None = None
        self._running = False

        # Level callbacks
        self._on_levels: Callable[[AudioLevels, AudioLevels], None] | None = None
        self._on_timecode: Callable[[LTCFrame], None] | None = None

        # Buffer storage for combining data from different devices
        self._tc_buffer: np.ndarray | None = None
        self._pgm_buffer: np.ndarray | None = None

    def configure(
        self,
        tc_device: int,
        tc_channel: int = 0,
        pgm_device: int | None = None,
        pgm_channel: int = 0,
    ) -> None:
        """Set up audio device routing.

        If pgm_device is None, program audio comes from the same
        device as timecode.
        """
        self._tc_device = tc_device
        self._tc_channel = tc_channel
        self._pgm_device = pgm_device if pgm_device is not None else tc_device
        self._pgm_channel = pgm_channel

    def set_recording_session(self, session: RecordingSession) -> None:
        self._recording = session

    def set_fsm(self, fsm: RecordingFSM) -> None:
        self._fsm = fsm

    def set_level_callback(
        self, callback: Callable[[AudioLevels, AudioLevels], None],
    ) -> None:
        """Set callback for VU meter updates: callback(tc_levels, pgm_levels)."""
        self._on_levels = callback

    def set_timecode_callback(self, callback: Callable[[LTCFrame], None]) -> None:
        """Set callback for decoded timecode frames."""
        self._on_timecode = callback

    def start(self) -> None:
        """Start audio capture and processing."""
        if self._tc_device is None:
            raise RuntimeError("No timecode device configured")

        self._running = True

        # Start processing thread
        self._processing_thread = threading.Thread(
            target=self._process_loop, daemon=True,
        )
        self._processing_thread.start()

        # Open streams for unique devices
        devices_needed = {self._tc_device}
        if self._pgm_device is not None:
            devices_needed.add(self._pgm_device)

        for dev_idx in devices_needed:
            dev_info = sd.query_devices(dev_idx)
            channels = dev_info["max_input_channels"]  # type: ignore[index]

            stream = sd.InputStream(
                device=dev_idx,
                channels=channels,
                samplerate=self._sample_rate,
                blocksize=self._block_size,
                dtype="float32",
                callback=self._make_callback(dev_idx),
            )
            self._streams.append(stream)
            stream.start()
            logger.info("Started audio stream for device %d: %s", dev_idx, dev_info["name"])  # type: ignore[index]

    def stop(self) -> None:
        """Stop audio capture."""
        self._running = False

        for stream in self._streams:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass
        self._streams.clear()

        if self._processing_thread:
            self._processing_thread.join(timeout=2.0)
            self._processing_thread = None

    def _make_callback(self, device_idx: int) -> Callable:
        """Create an audio callback for a specific device."""
        def callback(
            indata: np.ndarray,
            frames: int,
            time_info: object,
            status: sd.CallbackFlags,
        ) -> None:
            if status:
                logger.warning("Audio callback status: %s", status)

            try:
                self._audio_queue.put_nowait((device_idx, indata.copy()))
            except queue.Full:
                logger.warning("Audio queue full, dropping buffer")

        return callback

    def _process_loop(self) -> None:
        """Background thread that processes audio buffers."""
        while self._running:
            try:
                device_idx, data = self._audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            tc_audio = None
            pgm_audio = None

            # Extract relevant channels
            if device_idx == self._tc_device:
                ch = min(self._tc_channel, data.shape[1] - 1)
                tc_audio = data[:, ch]

            if device_idx == self._pgm_device:
                ch = min(self._pgm_channel, data.shape[1] - 1)
                pgm_audio = data[:, ch]

            # Decode LTC from timecode channel
            if tc_audio is not None:
                # Convert float32 to unsigned 8-bit for libltc
                u8_samples = ((tc_audio * 127) + 128).clip(0, 255).astype(np.uint8)
                self._ltc_decoder.write(u8_samples.tobytes(), len(u8_samples))

                frames = self._ltc_decoder.read()
                for frame in frames:
                    if self._on_timecode:
                        self._on_timecode(frame)
                    if self._fsm:
                        self._fsm.update(frame.total_seconds)

            # Compute levels for VU meters
            if self._on_levels:
                tc_levels = AudioLevels()
                pgm_levels = AudioLevels()

                if tc_audio is not None:
                    tc_levels.rms = float(np.sqrt(np.mean(tc_audio ** 2)))
                    tc_levels.peak = float(np.max(np.abs(tc_audio)))

                if pgm_audio is not None:
                    pgm_levels.rms = float(np.sqrt(np.mean(pgm_audio ** 2)))
                    pgm_levels.peak = float(np.max(np.abs(pgm_audio)))

                self._on_levels(tc_levels, pgm_levels)

            # Write to recording session
            if self._recording and pgm_audio is not None:
                self._recording.write(pgm_audio, tc_audio)

    @property
    def sample_rate(self) -> int:
        return self._sample_rate
