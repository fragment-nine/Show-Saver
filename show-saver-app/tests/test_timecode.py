"""Tests for timecode parsing and conversion."""

from showsaver.core.timecode import int_to_stamp, stamp_to_int


class TestStampToInt:
    def test_full_format(self):
        assert stamp_to_int("01:02:03:04") == 1 * 3600 + 2 * 60 + 3

    def test_zero(self):
        assert stamp_to_int("0:00:00") == 0

    def test_hours_only(self):
        assert stamp_to_int("1:00:00:00") == 3600

    def test_ten_minutes(self):
        assert stamp_to_int("0:10:00") == 600

    def test_semicolon_separator(self):
        assert stamp_to_int("01;02;03;04") == 3723

    def test_two_parts(self):
        # MM:SS
        assert stamp_to_int("05:30") == 5 * 60 + 30

    def test_single_value(self):
        assert stamp_to_int("45") == 45

    def test_large_timecode(self):
        # 4:20:00 from TrackMaster
        assert stamp_to_int("4:20:00") == 4 * 3600 + 20 * 60

    def test_string_cast(self):
        assert stamp_to_int(600) == 600


class TestIntToStamp:
    def test_zero(self):
        assert int_to_stamp(0) == "00:00:00:00"

    def test_one_hour(self):
        assert int_to_stamp(3600) == "01:00:00:00"

    def test_mixed(self):
        assert int_to_stamp(3723) == "01:02:03:00"
