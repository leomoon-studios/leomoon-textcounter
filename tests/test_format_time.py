"""Unit tests for `textcounter.core.format_time`."""

from __future__ import annotations

import importlib.util
import os
import unittest

_MODULE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "textcounter",
        "core",
        "format_time.py",
    )
)
_spec = importlib.util.spec_from_file_location("format_time", _MODULE_PATH)
assert _spec and _spec.loader
_format_time_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_format_time_mod)
format_time = _format_time_mod.format_time


class TestFormatTime(unittest.TestCase):
    # --- separators=0 (just the value) ---------------------------------
    def test_zero_separators_zero(self) -> None:
        self.assertEqual(format_time(0, separators=0), "00")

    def test_zero_separators_pad(self) -> None:
        self.assertEqual(format_time(7, separators=0, lead_zeroes=4), "0007")

    def test_zero_separators_large(self) -> None:
        self.assertEqual(format_time(123456, separators=0, lead_zeroes=2), "123456")

    # --- separators=1 (MM:SS style with modulo) ------------------------
    def test_one_separator_24fps(self) -> None:
        # 50 ticks @ 24 modulo -> 02:02
        self.assertEqual(
            format_time(50, separators=1, modulo=24, lead_zeroes=2, trail_zeroes=2),
            "02:02",
        )

    def test_one_separator_30fps(self) -> None:
        # 95 ticks @ 30 modulo -> 03:05
        self.assertEqual(
            format_time(95, separators=1, modulo=30, lead_zeroes=2, trail_zeroes=2),
            "03:05",
        )

    def test_one_separator_60_seconds(self) -> None:
        # 125 seconds -> 02:05 (modulo=60)
        self.assertEqual(
            format_time(125, separators=1, modulo=60), "02:05"
        )

    def test_one_separator_zero(self) -> None:
        self.assertEqual(format_time(0, separators=1, modulo=24), "00:00")

    # --- separators=2 (HH:MM:SS) --------------------------------------
    def test_two_separators(self) -> None:
        # 1h 2m 3s at modulo=60 ->  3600+120+3 = 3723
        self.assertEqual(
            format_time(3723, separators=2, modulo=60), "01:02:03"
        )

    def test_two_separators_lead_trail(self) -> None:
        # Trail width 4 on the hours field
        self.assertEqual(
            format_time(
                3723, separators=2, modulo=60, lead_zeroes=2, trail_zeroes=4
            ),
            "0001:02:03",
        )

    # --- separators=3 (DD:HH:MM:SS) -----------------------------------
    def test_three_separators(self) -> None:
        # All boundaries divide by 60 in this mode, matching legacy behavior.
        # 1*60^3 + 2*60^2 + 3*60 + 4 = 223384
        total = ((1 * 60 + 2) * 60 + 3) * 60 + 4
        self.assertEqual(
            format_time(total, separators=3, modulo=60), "01:02:03:04"
        )

    # --- negatives -----------------------------------------------------
    def test_negative_zero_separators(self) -> None:
        self.assertEqual(format_time(-7, separators=0, lead_zeroes=4), "-0007")

    def test_negative_with_separators(self) -> None:
        self.assertEqual(
            format_time(-125, separators=1, modulo=60), "-02:05"
        )

    # --- large values --------------------------------------------------
    def test_large_value_two_separators(self) -> None:
        # 12:34:56 -> 12*3600 + 34*60 + 56 = 45296
        self.assertEqual(
            format_time(45296, separators=2, modulo=60), "12:34:56"
        )

    # --- prefix / suffix ----------------------------------------------
    def test_prefix_suffix(self) -> None:
        self.assertEqual(
            format_time(
                65, separators=1, modulo=60, prefix="T-", suffix=" left"
            ),
            "T-01:05 left",
        )

    def test_prefix_suffix_with_negative(self) -> None:
        self.assertEqual(
            format_time(
                -65, separators=1, modulo=60, prefix="T-", suffix=" left"
            ),
            "T--01:05 left",
        )

    # --- input validation ---------------------------------------------
    def test_invalid_separators(self) -> None:
        with self.assertRaises(ValueError):
            format_time(0, separators=4)

    def test_invalid_modulo(self) -> None:
        with self.assertRaises(ValueError):
            format_time(0, separators=1, modulo=0)


if __name__ == "__main__":
    unittest.main()
