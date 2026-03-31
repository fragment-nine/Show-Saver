"""ShowSaver CLI — command-line interface for recording.

Usage:
    showsaver --list-devices
    showsaver --tc-device 3 --pgm-device 5 --csv TrackMaster.csv --output ./recordings
    showsaver --tc-device 3 --tc-channel 0 --pgm-device 3 --pgm-channel 1 --csv TrackMaster.csv --output ./recordings
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from pathlib import Path

from .core.audio_engine import AudioEngine, AudioLevels, list_input_devices
from .core.audio_writer import RecordingSession
from .core.file_manager import FileManager
from .core.ltc_decoder import LTCFrame
from .core.recording_fsm import RecordingFSM, RecordingState
from .core.settings import Settings
from .core.track_master import TrackMaster

logger = logging.getLogger("showsaver")


def print_devices() -> None:
    """Print available audio input devices."""
    devices = list_input_devices()
    if not devices:
        print("No audio input devices found.")
        return

    print("\nAvailable audio input devices:")
    print(f"{'Index':<8} {'Channels':<10} {'Sample Rate':<14} {'Name'}")
    print("-" * 60)
    for dev in devices:
        print(
            f"{dev.index:<8} {dev.max_input_channels:<10} "
            f"{dev.default_samplerate:<14.0f} {dev.name}"
        )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ShowSaver — Live show recording driven by LTC timecode",
    )
    parser.add_argument(
        "--list-devices", action="store_true",
        help="List available audio input devices and exit",
    )
    parser.add_argument("--tc-device", type=int, help="Timecode input device index")
    parser.add_argument("--tc-channel", type=int, default=0, help="Timecode channel (0-based)")
    parser.add_argument("--pgm-device", type=int, help="Program audio device index (default: same as TC)")
    parser.add_argument("--pgm-channel", type=int, default=0, help="Program audio channel (0-based)")
    parser.add_argument("--csv", type=str, help="Path to TrackMaster CSV file")
    parser.add_argument("--output", type=str, help="Output folder for recordings")
    parser.add_argument("--sample-rate", type=int, default=48000, help="Sample rate (default: 48000)")
    parser.add_argument("--fps", type=int, default=30, help="Timecode frame rate (default: 30)")
    parser.add_argument("--manual", action="store_true", help="Start manual recording immediately")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.list_devices:
        print_devices()
        return

    if args.tc_device is None:
        print("Error: --tc-device is required. Use --list-devices to see available devices.")
        sys.exit(1)

    if not args.output:
        print("Error: --output is required.")
        sys.exit(1)

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load track master
    track_master = TrackMaster()
    if args.csv:
        csv_path = Path(args.csv)
        if not csv_path.exists():
            print(f"Error: CSV file not found: {csv_path}")
            sys.exit(1)
        track_master.load_csv(csv_path)
        print(f"Loaded {len(track_master.tracks)} tracks from {csv_path}")
        for t in track_master.tracks:
            print(f"  [{t.tc_stamp}] {t.name}")

    # Set up components
    file_manager = FileManager(output_path)
    recording = RecordingSession(args.sample_rate)
    engine = AudioEngine(
        sample_rate=args.sample_rate,
        fps=args.fps,
    )

    # Configure device routing
    engine.configure(
        tc_device=args.tc_device,
        tc_channel=args.tc_channel,
        pgm_device=args.pgm_device,
        pgm_channel=args.pgm_channel,
    )

    # Set up FSM with callbacks
    def on_song_start(track, paths):
        recording.start_song(paths)
        print(f"\n>> Recording: {track.name}")

    def on_song_stop():
        recording.stop_song()
        print("\n>> Song recording stopped")

    def on_long_start(paths):
        recording.start_long_recording(paths)

    fsm = RecordingFSM(
        track_master=track_master,
        file_manager=file_manager,
        on_song_start=on_song_start,
        on_song_stop=on_song_stop,
        on_long_start=on_long_start,
    )

    engine.set_recording_session(recording)
    engine.set_fsm(fsm)

    # Timecode display callback
    last_tc_display = [0.0]

    def on_timecode(frame: LTCFrame) -> None:
        now = time.time()
        if now - last_tc_display[0] > 0.5:  # Update display twice per second
            print(f"\r  TC: {frame.stamp}  Song: {fsm.current_song_name or '---'}", end="", flush=True)
            last_tc_display[0] = now

    engine.set_timecode_callback(on_timecode)

    # Start long recording
    from datetime import datetime
    dt = datetime.now()
    long_paths = file_manager.prepare_song_recording("Long", dt)
    recording.start_long_recording(long_paths)

    # Handle shutdown
    shutdown = [False]

    def signal_handler(sig, frame):
        shutdown[0] = True
        print("\n\nShutting down...")

    signal.signal(signal.SIGINT, signal_handler)

    # Start
    print(f"\nShowSaver starting...")
    print(f"  TC Device: {args.tc_device} (channel {args.tc_channel})")
    print(f"  PGM Device: {args.pgm_device or args.tc_device} (channel {args.pgm_channel})")
    print(f"  Output: {output_path}")
    print(f"  Sample Rate: {args.sample_rate} Hz")
    print(f"\nPress Ctrl+C to stop.\n")

    engine.start()

    if args.manual:
        fsm.manual_start()
    else:
        fsm.arm()
        print("Armed — waiting for timecode...\n")

    # Main loop
    while not shutdown[0]:
        time.sleep(0.1)

    # Clean shutdown
    engine.stop()
    recording.stop_all()
    print("Recording stopped. Files saved to:", output_path)


if __name__ == "__main__":
    main()
