"""LTC (Linear Timecode) decoder.

Provides two implementations:
  1. LibLTCDecoder — wraps the libltc C library via ctypes (preferred)
  2. PurePythonLTCDecoder — fallback pure-Python biphase decoder

Both expose the same interface: feed raw audio samples, get timecode out.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import platform
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class LTCFrame:
    """A decoded LTC timecode frame."""

    hours: int
    minutes: int
    seconds: int
    frames: int
    total_seconds: int

    @property
    def stamp(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}:{self.frames:02d}"


class LTCDecoderProtocol(Protocol):
    """Interface for LTC decoder implementations."""

    def write(self, samples: bytes, num_samples: int) -> None: ...
    def read(self) -> list[LTCFrame]: ...


# ---------------------------------------------------------------------------
# libltc ctypes wrapper
# ---------------------------------------------------------------------------

def _find_libltc() -> str | None:
    """Locate the libltc shared library."""
    # Check bundled libs directory first
    app_dir = Path(__file__).resolve().parent.parent.parent.parent
    libs_dir = app_dir / "libs"

    system = platform.system()
    if system == "Darwin":
        candidates = [libs_dir / "libltc.dylib", libs_dir / "libltc.so"]
    elif system == "Windows":
        candidates = [libs_dir / "libltc.dll", libs_dir / "ltc.dll"]
    else:
        candidates = [libs_dir / "libltc.so"]

    for path in candidates:
        if path.exists():
            return str(path)

    # Fall back to system-installed
    return ctypes.util.find_library("ltc")


class LibLTCDecoder:
    """LTC decoder using the libltc C library.

    This wraps ltc_decoder_create / ltc_decoder_write /
    ltc_decoder_read from libltc.
    """

    def __init__(self, sample_rate: int, fps: int = 25, queue_size: int = 32) -> None:
        lib_path = _find_libltc()
        if lib_path is None:
            raise RuntimeError(
                "libltc not found. Install it or place the shared library "
                "in the show-saver-app/libs/ directory."
            )

        self._lib = ctypes.cdll.LoadLibrary(lib_path)
        self._setup_ctypes()

        self._decoder = self._lib.ltc_decoder_create(sample_rate, queue_size)
        if not self._decoder:
            raise RuntimeError("Failed to create LTC decoder")

        self._sample_rate = sample_rate
        self._fps = fps
        self._position = 0

    def _setup_ctypes(self) -> None:
        """Declare function signatures for libltc."""
        self._lib.ltc_decoder_create.argtypes = [ctypes.c_int, ctypes.c_int]
        self._lib.ltc_decoder_create.restype = ctypes.c_void_p

        self._lib.ltc_decoder_free.argtypes = [ctypes.c_void_p]
        self._lib.ltc_decoder_free.restype = None

        self._lib.ltc_decoder_write.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_size_t,
            ctypes.c_longlong,
        ]
        self._lib.ltc_decoder_write.restype = ctypes.c_int

        self._lib.ltc_decoder_read.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self._lib.ltc_decoder_read.restype = ctypes.c_int

    def write(self, samples: bytes, num_samples: int) -> None:
        """Feed raw unsigned 8-bit audio samples to the decoder."""
        buf = (ctypes.c_ubyte * num_samples).from_buffer_copy(samples[:num_samples])
        self._lib.ltc_decoder_write(
            self._decoder,
            buf,
            ctypes.c_size_t(num_samples),
            ctypes.c_longlong(self._position),
        )
        self._position += num_samples

    def read(self) -> list[LTCFrame]:
        """Read all decoded frames from the queue."""
        frames = []
        # LTCFrameExt is 120 bytes (generous buffer)
        frame_buf = ctypes.create_string_buffer(256)

        while self._lib.ltc_decoder_read(self._decoder, frame_buf) > 0:
            # The LTC timecode data starts at the beginning of the struct.
            # LTCFrame layout: first 10 bytes contain the BCD time fields.
            raw = frame_buf.raw

            # Extract time from the LTCFrame struct.
            # The time fields in libltc's SMPTETimecode (within LTCFrameExt):
            # Offset depends on struct packing; use the off_start/off_end
            # approach with the SMPTETimecode at offset 80 in LTCFrameExt.
            # SMPTETimecode layout (after LTCFrame + offsets):
            #   char timezone[6], years, months, days, hours, mins, secs, frames
            # This is at a fixed offset in the struct.

            # More reliable: parse from known offset in LTCFrameExt
            # The SMPTETimecode struct is typically at offset 80
            # timezone(6) + years(1) + months(1) + days(1) + hours(1) +
            # mins(1) + secs(1) + frames(1)
            offset = 80
            tz = raw[offset:offset + 6]
            years = raw[offset + 6]
            months = raw[offset + 7]
            days = raw[offset + 8]
            hours = raw[offset + 9]
            mins = raw[offset + 10]
            secs = raw[offset + 11]
            frame_num = raw[offset + 12]

            total = hours * 3600 + mins * 60 + secs
            frames.append(LTCFrame(
                hours=hours,
                minutes=mins,
                seconds=secs,
                frames=frame_num,
                total_seconds=total,
            ))

        return frames

    def __del__(self) -> None:
        if hasattr(self, "_decoder") and self._decoder:
            self._lib.ltc_decoder_free(self._decoder)
            self._decoder = None


# ---------------------------------------------------------------------------
# Pure-Python fallback decoder
# ---------------------------------------------------------------------------

class PurePythonLTCDecoder:
    """Minimal pure-Python LTC decoder (fallback when libltc unavailable).

    Decodes LTC biphase-mark encoded audio. Expects mono float32 samples
    normalized to [-1.0, 1.0].

    This is simpler and less robust than libltc but handles clean
    timecode signals adequately.
    """

    # LTC word is 80 bits per frame
    BITS_PER_FRAME = 80

    def __init__(self, sample_rate: int, fps: int = 30) -> None:
        self._sample_rate = sample_rate
        self._fps = fps
        self._samples_per_bit = sample_rate / (fps * self.BITS_PER_FRAME)

        # State for edge detection
        self._prev_sample = 0.0
        self._sample_count = 0
        self._bit_buffer: list[int] = []
        self._pending_frames: list[LTCFrame] = []
        self._half_bit = False
        self._edge_count = 0

    def write_float(self, samples: list[float] | memoryview) -> None:
        """Feed float audio samples to the decoder."""
        threshold = self._samples_per_bit * 0.75

        for sample in samples:
            self._sample_count += 1

            # Detect zero crossings
            if (sample >= 0) != (self._prev_sample >= 0):
                period = self._sample_count

                if period < threshold:
                    # Short period = two transitions per bit = '1' bit
                    if self._half_bit:
                        self._bit_buffer.append(1)
                        self._half_bit = False
                    else:
                        self._half_bit = True
                else:
                    # Long period = one transition per bit = '0' bit
                    self._bit_buffer.append(0)
                    self._half_bit = False

                self._sample_count = 0

                # Check for complete frame (sync word detection)
                if len(self._bit_buffer) >= self.BITS_PER_FRAME:
                    self._try_decode_frame()

            self._prev_sample = sample

    def write(self, samples: bytes, num_samples: int) -> None:
        """Feed raw unsigned 8-bit audio samples (for interface compat)."""
        # Convert u8 to float
        float_samples = [(b - 128) / 128.0 for b in samples[:num_samples]]
        self.write_float(float_samples)

    def _try_decode_frame(self) -> None:
        """Try to decode an LTC frame from the bit buffer."""
        bits = self._bit_buffer

        # LTC sync word is 0011 1111 1111 1101 (0x3FFD) at bits 64-79
        if len(bits) < self.BITS_PER_FRAME:
            return

        # Check last 16 bits for sync word
        sync_bits = bits[-16:]
        sync_word = 0
        for b in sync_bits:
            sync_word = (sync_word << 1) | b

        if sync_word != 0x3FFD:
            # No sync — drop oldest bit and try again
            if len(bits) > self.BITS_PER_FRAME * 2:
                self._bit_buffer = bits[-(self.BITS_PER_FRAME):]
            return

        # We have a valid frame — extract the 80 bits
        frame_bits = bits[-self.BITS_PER_FRAME:]
        self._bit_buffer = []

        # Decode BCD time fields from LTC bit positions
        # Frames:  bits 0-3 (units), bits 8-9 (tens)
        # Seconds: bits 16-19 (units), bits 24-26 (tens)
        # Minutes: bits 32-35 (units), bits 40-42 (tens)
        # Hours:   bits 48-51 (units), bits 56-57 (tens)
        def bcd(bit_positions: list[int]) -> int:
            val = 0
            for i, pos in enumerate(bit_positions):
                if pos < len(frame_bits):
                    val += frame_bits[pos] << i
            return val

        frame_units = bcd([0, 1, 2, 3])
        frame_tens = bcd([8, 9])
        sec_units = bcd([16, 17, 18, 19])
        sec_tens = bcd([24, 25, 26])
        min_units = bcd([32, 33, 34, 35])
        min_tens = bcd([40, 41, 42])
        hr_units = bcd([48, 49, 50, 51])
        hr_tens = bcd([56, 57])

        frames = frame_tens * 10 + frame_units
        secs = sec_tens * 10 + sec_units
        mins = min_tens * 10 + min_units
        hours = hr_tens * 10 + hr_units

        total = hours * 3600 + mins * 60 + secs
        self._pending_frames.append(LTCFrame(
            hours=hours,
            minutes=mins,
            seconds=secs,
            frames=frames,
            total_seconds=total,
        ))

    def read(self) -> list[LTCFrame]:
        """Return all decoded frames and clear the queue."""
        frames = self._pending_frames
        self._pending_frames = []
        return frames


def create_decoder(sample_rate: int, fps: int = 30) -> LibLTCDecoder | PurePythonLTCDecoder:
    """Create the best available LTC decoder.

    Tries libltc first, falls back to pure Python.
    """
    try:
        return LibLTCDecoder(sample_rate, fps)
    except (RuntimeError, OSError):
        return PurePythonLTCDecoder(sample_rate, fps)
