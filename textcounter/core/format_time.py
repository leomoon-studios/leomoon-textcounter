"""Pure time formatting for the TextCounter add-on.

This module has no `bpy` imports so it can be unit-tested standalone.

The behavior mirrors the original LeoMoon TextCounter:

- `separators=0` -> ``"SS"``                       (lead width only)
- `separators=1` -> ``"MM:SS"``                    (trail : lead)
- `separators=2` -> ``"HH:MM:SS"``                 (trail : 02 : lead)
- `separators=3` -> ``"DD:HH:MM:SS"``              (trail : 02 : 02 : lead)

`modulo` is the divisor for the smallest unit (e.g. 24 for ticks-per-second
at 24 fps, 60 for seconds-per-minute on a stopwatch).
"""

from __future__ import annotations


def _pad(n: int, width: int) -> str:
    return format(n, f"0{max(1, width)}d")


def format_time(
    value: float,
    *,
    separators: int = 0,
    modulo: int = 24,
    lead_zeroes: int = 2,
    trail_zeroes: int = 2,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Format `value` as a time-like string.

    Args:
        value: The numeric value (truncated to int) to render.
        separators: Number of ``:`` separators in the output (0..3).
        modulo: Divisor used for the smallest unit (rightmost field).
        lead_zeroes: Padding width of the smallest field (or the only field
            when `separators == 0`).
        trail_zeroes: Padding width of the largest field.
        prefix: String prepended to the final result (before the sign).
        suffix: String appended to the final result.

    Returns:
        The formatted string, e.g. ``"01:23:45"``.
    """
    if separators < 0 or separators > 3:
        raise ValueError("separators must be in 0..3")
    if modulo < 1:
        raise ValueError("modulo must be >= 1")

    sign = "-" if value < 0 else ""
    n = int(abs(value))

    if separators == 0:
        body = _pad(n, lead_zeroes)
    else:
        # Smallest field uses `modulo`; intermediate fields use 60.
        smallest, rest = n % modulo, n // modulo
        parts = [_pad(smallest, lead_zeroes)]

        if separators == 1:
            parts.insert(0, _pad(rest, trail_zeroes))
        else:
            # separators >= 2: insert 02-padded middle field(s)
            mid1, rest = rest % 60, rest // 60
            if separators == 2:
                parts.insert(0, _pad(mid1, 2))
                parts.insert(0, _pad(rest, trail_zeroes))
            else:  # separators == 3
                mid2, rest = rest % 60, rest // 60
                parts.insert(0, _pad(mid1, 2))
                parts.insert(0, _pad(mid2, 2))
                parts.insert(0, _pad(rest, trail_zeroes))

        body = ":".join(parts)

    return f"{prefix}{sign}{body}{suffix}"
