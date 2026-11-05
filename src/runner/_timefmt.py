"""Parse and format durations such as ``"20m"``, ``"90s"`` or ``1200``."""

from __future__ import annotations

import math
import re

_UNITS = {
    "ms": 0.001,
    "s": 1.0,
    "sec": 1.0,
    "secs": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "m": 60.0,
    "min": 60.0,
    "mins": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "h": 3600.0,
    "hr": 3600.0,
    "hrs": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
}
_PART = re.compile(r"(\d+(?:\.\d+)?)\s*([a-z]*)")


def parse_duration(value: float | int | str | None) -> float | None:
    """Turn a user-friendly duration into seconds.

    Accepts a number of seconds (``90``), a string with units (``"90s"``,
    ``"20m"``, ``"1h30m"``, ``"1.5h"``) or ``None`` / ``"none"`` for "no limit".

    >>> parse_duration("20m")
    1200.0
    >>> parse_duration("1h30m")
    5400.0
    >>> parse_duration(None) is None
    True
    """
    if value is None:
        return None
    if isinstance(value, bool):  # bool is an int subclass; True seconds is surely a mistake
        raise TypeError(
            f"timeout must be a number of seconds or a string like '20m', not {value!r}."
        )
    if isinstance(value, (int, float)):
        if math.isnan(value) or value <= 0:
            raise ValueError(f"timeout must be a positive number of seconds, got {value!r}.")
        return None if math.isinf(value) else float(value)
    if not isinstance(value, str):
        raise TypeError(
            f"timeout must be a number of seconds or a string like '20m', not {type(value).__name__}."
        )

    text = value.strip().lower().replace(" ", "")
    if text in {"none", "never", "off", "inf", "infinite", "unlimited"}:
        return None

    total = 0.0
    position = 0
    for match in _PART.finditer(text):
        if match.start() != position or not match.group(0):
            break
        number, unit = match.groups()
        unit = unit or "s"
        if unit not in _UNITS:
            raise ValueError(
                f"Unknown time unit {unit!r} in timeout {value!r}. "
                "Use s, m or h, e.g. '90s', '20m' or '1h'."
            )
        total += float(number) * _UNITS[unit]
        position = match.end()
    if position != len(text) or not text:
        raise ValueError(
            f"Could not understand timeout {value!r}. "
            "Use a number of seconds (1200) or a string like '90s', '20m', '1h30m'."
        )
    if total <= 0:
        raise ValueError(f"timeout must be positive, got {value!r}.")
    return total


def format_duration(seconds: float | None) -> str:
    """Short human-readable duration: ``0.003s``, ``1.25s``, ``3m 05s``, ``1h 02m``."""
    if seconds is None:
        return "no limit"
    if seconds < 0.0001:
        return "<0.1ms"
    if seconds < 0.01:
        return f"{seconds * 1000:.1f}ms"
    if seconds < 10:
        return f"{seconds:.2f}s"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(round(seconds), 60)
    if minutes < 60:
        return f"{minutes}m" if secs == 0 else f"{minutes}m {secs:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h" if minutes == 0 else f"{hours}h {minutes:02d}m"
