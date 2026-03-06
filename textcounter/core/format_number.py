"""Pure number formatting for the TextCounter add-on.

This module has no `bpy` imports so it can be imported and unit-tested from a
plain Python interpreter.
"""

from __future__ import annotations

from math import floor, log10

# Suffix table for abbreviation. Index 0 is "no suffix", index N covers the
# range [10**(3N), 10**(3(N+1))).
_ABBREVIATIONS = ("", "K", "M", "B", "T", "Q")


def _abbreviation_index(magnitude: float) -> int:
    """Return the index into `_ABBREVIATIONS` for a non-negative magnitude."""
    if magnitude < 1000:
        return 0
    idx = int(floor(log10(magnitude) / 3))
    return min(idx, len(_ABBREVIATIONS) - 1)


def format_number(
    value: float,
    *,
    decimals: int = 0,
    padding: int = 1,
    use_decimal: bool = False,
    digit_sep: str = ",",
    decimal_sep: str = ".",
    use_grouping: bool = False,
    use_abbreviation: bool = False,
    abbreviation_lower: bool = False,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Format `value` according to the supplied options.

    Args:
        value: The numeric value to format.
        decimals: Number of fractional digits (only used when `use_decimal`).
        padding: Minimum number of integer digits (zero-padded). Always >= 1.
        use_decimal: Whether to render fractional digits.
        digit_sep: Character used to separate digit groups.
        decimal_sep: Character used between integer and fractional parts.
        use_grouping: Whether to insert `digit_sep` every three integer digits.
        use_abbreviation: Whether to abbreviate large numbers (K, M, B, ...).
        abbreviation_lower: Use lowercase abbreviation suffixes.
        prefix: String prepended to the final result (before the sign).
        suffix: String appended to the final result.

    Returns:
        The formatted string.
    """
    decimals = max(0, decimals)
    padding = max(1, padding)

    negative = value < 0
    magnitude = abs(value)

    # Abbreviation collapses the number into [0, 1000) * 10**(3*idx).
    if use_abbreviation:
        idx = _abbreviation_index(magnitude)
        scaled = magnitude / (10 ** (idx * 3)) if idx else magnitude
        suffix_letter = _ABBREVIATIONS[idx]
        if abbreviation_lower:
            suffix_letter = suffix_letter.lower()
    else:
        scaled = magnitude
        suffix_letter = ""

    # Integer vs decimal rendering.
    if use_decimal and decimals > 0:
        rendered_decimals = decimals
    else:
        rendered_decimals = 0
        scaled = floor(scaled) if not use_abbreviation else scaled

    # Build the format spec. Width counts integer digits + decimal point +
    # fractional digits, so add those when needed.
    width = padding
    if rendered_decimals:
        width += 1 + rendered_decimals
    grouping_flag = "," if use_grouping else ""
    spec = f"0{width}{grouping_flag}.{rendered_decimals}f"
    body = format(scaled, spec)

    # Translate the locale-neutral characters produced by Python into the
    # user-chosen separators. Use a sentinel so the two replacements don't
    # collide.
    body = body.replace(".", "\x00").replace(",", digit_sep).replace("\x00", decimal_sep)

    sign = "-" if negative and float(body.replace(digit_sep, "").replace(decimal_sep, ".")) != 0 else ""
    return f"{prefix}{sign}{body}{suffix_letter}{suffix}"
