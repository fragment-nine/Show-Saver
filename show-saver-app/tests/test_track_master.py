"""Tests for TrackMaster CSV parsing and song detection."""

import tempfile
from pathlib import Path

from showsaver.core.track_master import TrackMaster, clean_song_name


class TestCleanSongName:
    def test_normal_name(self):
        assert clean_song_name("Song 1") == "Song 1"

    def test_illegal_chars(self):
        assert clean_song_name('Song/Name\\Test:Bad*"<>|') == "Song_Name_Test_Bad_____"

    def test_empty(self):
        assert clean_song_name("") == ""


class TestTrackMaster:
    SAMPLE_CSV = (
        "TRACK #,SHOW ORDER,IN SHOW,STATUS,NAME,FILE/FOLDER NAME,BPM,TC\n"
        "0,0,FALSE,Delivered,Test Track,,,0:00:00\n"
        "1,1,TRUE,Delivered,Song 1,Song 1,,0:10:00\n"
        "2,2,TRUE,Delivered,Letters,Letters,,0:20:00\n"
        "3,3,TRUE,Delivered,Final Song,Final Song,,0:30:00\n"
    )

    def _load_sample(self) -> TrackMaster:
        tm = TrackMaster()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False,
        ) as f:
            f.write(self.SAMPLE_CSV)
            f.flush()
            tm.load_csv(f.name)
        return tm

    def test_load_csv(self):
        tm = self._load_sample()
        assert len(tm.tracks) == 4

    def test_track_names(self):
        tm = self._load_sample()
        names = [t.name for t in tm.tracks]
        assert names == ["Test Track", "Song 1", "Letters", "Final Song"]

    def test_timecodes(self):
        tm = self._load_sample()
        secs = [t.tc_seconds for t in tm.tracks]
        assert secs == [0, 600, 1200, 1800]

    def test_get_current_song_before_first(self):
        tm = self._load_sample()
        # At TC 0:00:00 we're before the first boundary
        # Since first track is at 0, and -1 would be out of range,
        # we should get None (no track before time 0)
        song = tm.get_current_song(-1)
        assert song is None

    def test_get_current_song_first(self):
        tm = self._load_sample()
        song = tm.get_current_song(300)  # 5 minutes in
        assert song is not None
        assert song.name == "Test Track"

    def test_get_current_song_middle(self):
        tm = self._load_sample()
        song = tm.get_current_song(900)  # 15 minutes in
        assert song is not None
        assert song.name == "Song 1"

    def test_get_current_song_last(self):
        tm = self._load_sample()
        song = tm.get_current_song(2000)  # Past all boundaries
        assert song is not None
        assert song.name == "Final Song"

    def test_save_and_reload(self):
        tm = self._load_sample()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False,
        ) as f:
            save_path = f.name
        tm.save_csv(save_path)

        tm2 = TrackMaster()
        tm2.load_csv(save_path)
        assert len(tm2.tracks) == len(tm.tracks)
        for a, b in zip(tm.tracks, tm2.tracks):
            assert a.name == b.name
            assert a.tc_seconds == b.tc_seconds


class TestTrackMasterEdgeCases:
    def test_empty_csv(self):
        tm = TrackMaster()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False,
        ) as f:
            f.write("TRACK #,SHOW ORDER,IN SHOW,STATUS,NAME,FILE/FOLDER NAME,BPM,TC\n")
            f.flush()
            tm.load_csv(f.name)
        assert len(tm.tracks) == 0
        assert tm.get_current_song(100) is None

    def test_single_track(self):
        tm = TrackMaster()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False,
        ) as f:
            f.write(
                "TRACK #,SHOW ORDER,IN SHOW,STATUS,NAME,FILE/FOLDER NAME,BPM,TC\n"
                "0,0,TRUE,,Solo Song,,,1:00:00\n"
            )
            f.flush()
            tm.load_csv(f.name)
        assert len(tm.tracks) == 1
        assert tm.get_current_song(3700) is not None
        assert tm.get_current_song(3700).name == "Solo Song"
