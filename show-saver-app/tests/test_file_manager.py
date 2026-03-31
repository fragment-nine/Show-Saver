"""Tests for file management and naming."""

import tempfile
from datetime import datetime
from pathlib import Path

from showsaver.core.file_manager import (
    FileManager,
    build_file_name,
    build_long_file_name,
    get_date_str,
    get_time_str,
    make_folders,
)


class TestDateTimeStrings:
    def test_date_str(self):
        dt = datetime(2024, 3, 15, 14, 30, 22)
        assert get_date_str(dt) == "20240315"

    def test_time_str(self):
        dt = datetime(2024, 3, 15, 14, 30, 22)
        assert get_time_str(dt) == "143022"


class TestBuildFileName:
    def test_pgm(self):
        name = build_file_name("Song_1", "20240315", "143022", "pgm")
        assert name == "20240315/Song_1_20240315_143022_pgm.wav"

    def test_ltc(self):
        name = build_file_name("Song_1", "20240315", "143022", "ltc")
        assert name == "20240315/Song_1_20240315_143022_ltc.wav"

    def test_custom_ext(self):
        name = build_file_name("Song_1", "20240315", "143022", "pgm", ext=".mov")
        assert name == "20240315/Song_1_20240315_143022_pgm.mov"


class TestBuildLongFileName:
    def test_long_pgm(self):
        name = build_long_file_name("20240315", "143022", "pgm")
        assert name == "Long Recordings/20240315/Long_20240315_143022_pgm.wav"


class TestMakeFolders:
    def test_creates_folders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_folders([tmpdir], "20240315")
            assert (Path(tmpdir) / "20240315").is_dir()
            assert (Path(tmpdir) / "Long Recordings" / "20240315").is_dir()

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            make_folders([tmpdir], "20240315")
            make_folders([tmpdir], "20240315")  # Should not raise
            assert (Path(tmpdir) / "20240315").is_dir()


class TestFileManager:
    def test_prepare_song_recording(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(tmpdir)
            dt = datetime(2024, 3, 15, 14, 30, 22)
            paths = fm.prepare_song_recording("Song_1", dt)

            assert "pgm" in paths
            assert "ltc" in paths
            assert "long_pgm" in paths
            assert "long_ltc" in paths

            assert "Song_1" in str(paths["pgm"])
            assert "_pgm.wav" in str(paths["pgm"])
            assert "_ltc.wav" in str(paths["ltc"])
            assert "Long Recordings" in str(paths["long_pgm"])

            # Folders should exist
            assert (Path(tmpdir) / "20240315").is_dir()
