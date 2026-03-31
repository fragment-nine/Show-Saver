"""Tests for the recording state machine."""

import tempfile
from pathlib import Path

from showsaver.core.file_manager import FileManager
from showsaver.core.recording_fsm import RecordingFSM, RecordingState
from showsaver.core.track_master import TrackMaster


def _make_track_master() -> TrackMaster:
    tm = TrackMaster()
    csv_content = (
        "TRACK #,SHOW ORDER,IN SHOW,STATUS,NAME,FILE/FOLDER NAME,BPM,TC\n"
        "0,0,TRUE,,Intro,,,0:00:00\n"
        "1,1,TRUE,,Song A,,,0:10:00\n"
        "2,2,TRUE,,Song B,,,0:20:00\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        f.flush()
        tm.load_csv(f.name)
    return tm


class TestRecordingFSM:
    def test_initial_state(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())
        fsm = RecordingFSM(tm, fm)
        assert fsm.state == RecordingState.IDLE

    def test_arm(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())
        fsm = RecordingFSM(tm, fm)
        fsm.arm()
        assert fsm.state == RecordingState.ARMED

    def test_arm_and_receive_tc(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())

        started_songs = []

        def on_start(track, paths):
            started_songs.append(track.name)

        fsm = RecordingFSM(tm, fm, on_song_start=on_start)
        fsm.arm()
        fsm.update(300)  # 5 minutes — should be in "Intro"

        assert fsm.state == RecordingState.RECORDING
        assert len(started_songs) == 1
        assert started_songs[0] == "Intro"

    def test_song_change(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())

        started = []
        stopped = []

        def on_start(track, paths):
            started.append(track.name)

        def on_stop():
            stopped.append(True)

        fsm = RecordingFSM(tm, fm, on_song_start=on_start, on_song_stop=on_stop)
        fsm.arm()
        fsm.update(300)   # In "Intro"
        fsm.update(601)   # Now in "Song A"

        assert len(started) == 2
        assert started[1] == "Song A"
        assert len(stopped) == 1

    def test_tc_jump(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())

        stopped = []

        def on_stop():
            stopped.append(True)

        fsm = RecordingFSM(tm, fm, on_song_stop=on_stop)
        fsm.arm()
        fsm.update(300)    # In Intro
        fsm.update(3000)   # Jump > 240s

        assert len(stopped) >= 1

    def test_manual_start(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())
        fsm = RecordingFSM(tm, fm)
        fsm.manual_start()

        assert fsm.state == RecordingState.RECORDING
        assert fsm.current_song_name == "Manual Start"

    def test_stop(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())
        fsm = RecordingFSM(tm, fm)
        fsm.arm()
        fsm.update(300)
        fsm.stop()

        assert fsm.state == RecordingState.STOPPED

    def test_idle_ignores_update(self):
        tm = _make_track_master()
        fm = FileManager(tempfile.mkdtemp())
        fsm = RecordingFSM(tm, fm)
        # Should not crash or change state
        fsm.update(300)
        assert fsm.state == RecordingState.IDLE
