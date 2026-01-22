"""
Utility functions for working with date and time.

Example Usage:
    # Preferred usage via public package interface:
    from src.utils import timestamp
    ts = timestamp.now_utc_iso()

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils._timestamp as timestamp
    ts = timestamp.now_utc_iso()

Dependencies:
    - Python >= 3.9
    - Standard Library: datetime

Notes:
    - Intended as an internal implementation module backing src.utils.timestamp.
    - Output formats are stable and optimized for filenames, logs, and lightweight identifiers.
    - All functions are pure helpers; they read the system clock but perform no I/O or stateful operations.

License:
    - Internal Use Only
"""

__all__ = [
    "format_date_iso",
    "now_local_date",
    "now_local_time",
    "now_utc_iso",
]

from datetime import datetime, timezone


def format_date_iso(value: datetime) -> str:
    """
    Format a datetime as an ISO 8601 date string (YYYY-MM-DD).

    Args:
        value (datetime): Datetime value to format.

    Returns:
        str: Date formatted as 'YYYY-MM-DD'.
    """
    return value.date().isoformat()


def now_local_date() -> str:
    """
    Return the current local date in YYMMDD format.

    Uses the system local time to format the date as a compact six-character string for logging, filenames, or lightweight identifiers.

    Args:
        None

    Returns:
        str: Local date formatted as 'YYMMDD'.

    Raises:
        None
    """
    # Get current local date and format as YYMMDD
    return datetime.now().strftime("%y%m%d")


def now_local_time() -> str:
    """
    Return the current local time in 24-hour HHMMSS format.

    Uses the system local time to format the time as a compact four-character string suitable for logging, filenames, or lightweight identifiers.

    Args:
        None

    Returns:
        str: Local time formatted as 'HHMMSS' in 24-hour format.

    Raises:
        None
    """
    # Get current local time in 24-hour format HHMMSS
    return datetime.now().strftime("%H%M%S")


def now_utc_iso() -> str:
    """
    Get the current UTC time in ISO 8601 format with a 'Z' suffix.

    The output is accurate to the second (microseconds are removed) and uses the 'Z' suffix to indicate UTC, instead of an explicit offset.

    Returns:
        str: Current UTC timestamp in the form 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    return (
        datetime.now(timezone.utc)  # Get current time in UTC
        .replace(microsecond=0)  # Remove microseconds for second precision
        .isoformat()  # Convert to ISO 8601
        .replace("+00:00", "Z")  # Replace '+00:00' with 'Z' for UTC
    )
