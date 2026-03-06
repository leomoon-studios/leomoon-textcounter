"""Unit tests for `textcounter.core.format_number`."""

from __future__ import annotations

import importlib.util
import os
import unittest

# Load the module by file path so we don't trigger `textcounter/__init__.py`,
# which imports `bpy`.
_MODULE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "textcounter",
        "core",
        "format_number.py",
    )
)
_spec = importlib.util.spec_from_file_location("format_number", _MODULE_PATH)
assert _spec and _spec.loader
_format_number_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_format_number_mod)
format_number = _format_number_mod.format_number


class TestFormatNumber(unittest.TestCase):
    def test_zero_default(self) -> None:
        self.assertEqual(format_number(0), "0")

    def test_integer_basic(self) -> None:
        self.assertEqual(format_number(42), "42")

    def test_padding(self) -> None:
        self.assertEqual(format_number(7, padding=4), "0007")
        self.assertEqual(format_number(1234, padding=2), "1234")

    def test_negative_sign_outside_padding(self) -> None:
        # Sign should sit before the zero padding, not be counted in `padding`.
        self.assertEqual(format_number(-7, padding=4), "-0007")

    def test_negative_zero(self) -> None:
        self.assertEqual(format_number(-0.0), "0")

    def test_decimals(self) -> None:
        self.assertEqual(format_number(3.14159, use_decimal=True, decimals=2), "3.14")
        self.assertEqual(
            format_number(-3.14159, use_decimal=True, decimals=3), "-3.142"
        )

    def test_decimal_separator_comma(self) -> None:
        self.assertEqual(
            format_number(3.14, use_decimal=True, decimals=2, decimal_sep=","),
            "3,14",
        )

    def test_grouping_default_comma(self) -> None:
        self.assertEqual(
            format_number(1234567, use_grouping=True), "1,234,567"
        )

    def test_grouping_dot(self) -> None:
        self.assertEqual(
            format_number(1234567, use_grouping=True, digit_sep="."),
            "1.234.567",
        )

    def test_grouping_space(self) -> None:
        self.assertEqual(
            format_number(1234567, use_grouping=True, digit_sep=" "),
            "1 234 567",
        )

    def test_grouping_apostrophe(self) -> None:
        self.assertEqual(
            format_number(1234567, use_grouping=True, digit_sep="'"),
            "1'234'567",
        )

    def test_grouping_with_decimal_sep(self) -> None:
        # European style: dot grouping + comma decimal.
        self.assertEqual(
            format_number(
                1234567.89,
                use_decimal=True,
                decimals=2,
                use_grouping=True,
                digit_sep=".",
                decimal_sep=",",
            ),
            "1.234.567,89",
        )

    def test_abbreviation_thresholds(self) -> None:
        self.assertEqual(format_number(999, use_abbreviation=True), "999")
        self.assertEqual(format_number(1000, use_abbreviation=True), "1K")
        self.assertEqual(format_number(1_500_000, use_abbreviation=True), "2M")  # rounded floor at 0 decimals
        self.assertEqual(
            format_number(
                1_500_000, use_abbreviation=True, use_decimal=True, decimals=1
            ),
            "1.5M",
        )
        self.assertEqual(
            format_number(2_500_000_000, use_abbreviation=True), "2B"
        )

    def test_abbreviation_lowercase(self) -> None:
        self.assertEqual(
            format_number(
                1_500_000,
                use_abbreviation=True,
                abbreviation_lower=True,
                use_decimal=True,
                decimals=1,
            ),
            "1.5m",
        )

    def test_abbreviation_negative(self) -> None:
        self.assertEqual(
            format_number(
                -1_500_000,
                use_abbreviation=True,
                use_decimal=True,
                decimals=1,
            ),
            "-1.5M",
        )

    def test_abbreviation_overflow_caps_at_q(self) -> None:
        # 10**18 is well past Q (10**15); should still cap and not crash.
        self.assertEqual(
            format_number(10**18, use_abbreviation=True), "1000Q"
        )

    def test_prefix_suffix(self) -> None:
        self.assertEqual(
            format_number(99, prefix="$", suffix=" USD"),
            "$99 USD",
        )

    def test_prefix_suffix_with_negative(self) -> None:
        # Sign goes between prefix and number.
        self.assertEqual(
            format_number(-5, prefix="$", suffix=" USD"),
            "$-5 USD",
        )


if __name__ == "__main__":
    unittest.main()
