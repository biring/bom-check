"""
Unit tests for timestamp helpers in `src.utils._timestamp`.

This module verifies:
    - Local date format and accuracy (`YYMMDD`)
    - Local time format and accuracy (`HHMMSS`)
    - UTC ISO timestamp correctness (`YYYY-MM-DDTHH:MM:SSZ`)
    - Second-level precision with no microseconds
    - Consistency against trusted NTP/HTTP reference time sources

Example Usage:
    # Preferred usage from project root:
    python -m unittest tests/utils/test__timestamp.py

    # Run all tests via discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest, datetime, re
    - External Packages: ntplib, requests

Notes:
    - Accuracy tests are skipped when reference clocks are unavailable.
    - Reference time is validated using NTP (pool.ntp.org) or fallback HTTPS.
    - Functions under test are treated as pure helpers with no I/O side effects.

License:
    - Internal Use Only
"""

import ntplib
import re
import requests
import unittest
from datetime import datetime, timezone

# noinspection PyProtectedMember
import src.utils._timestamp as timestamp

class Reference:
    """
    Helper to obtain a trusted reference UTC time using both NTP and HTTP sources.

    Attributes:
        valid (bool): True if both sources are available and agree within tolerance.
        dt (datetime | None): Reference time from testing when valid is True; otherwise None.
        msg (str): Explanation of any failure or drift reason (empty on success).
    """

    ntp_server = "pool.ntp.org"
    http_api = "https://worldtimeapi.org/api/ip"

    def __init__(self) -> None:
        self.dt: datetime | None = None
        self.valid: bool = False
        self.msg: str = ""

        # --- Get UTC time from pool.ntp.org (NTP) ---
        try:
            client = ntplib.NTPClient()
            response = client.request(self.ntp_server, version=3)
            self.dt = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
            self.valid = True
            return
        except Exception as e:
            self.msg = f"\nNTP time unavailable. {e}"

        # --- Get UTC time from HTTPS worldtimeapi.org (HTTP) ---
        try:
            r = requests.get(self.http_api, timeout=5)
            data = r.json()
            self.dt = datetime.fromisoformat(data["datetime"]).astimezone(timezone.utc)
            self.valid = True
            return
        except Exception as e:
            self.msg += f"\nHTTP time unavailable. {e}"

        return

# Module varaible with reference time
reference = Reference()


class TestFormatDateIso(unittest.TestCase):
    """
    Unit tests to verify formatting of datetime values as ISO date strings.
    """

    def test_happy_path(self):
        """
        Should return the date portion of the datetime in 'YYYY-MM-DD' format.
        """
        # ARRANGE
        value = datetime(2024, 3, 15, 10, 45, 30)
        expected = "2024-03-15"

        # ACT
        result = timestamp.format_date_iso(value)

        # ASSERT
        with self.subTest(Act=result, Exp=expected):
            self.assertEqual(result, expected)


class TestNowLocalDate(unittest.TestCase):
    """
    Unit tests for the `now_local_date` function.
    """

    def test_accuracy(self):
        """
        Should match the trusted local date derived from NTP/HTTP reference time,
        formatted as 'YYMMDD'. If reference time is not available or not reliable,
        the test is skipped.
        """
        # ARRANGE
        if not reference.valid:
            # Skip this accuracy test when we cannot trust the reference clock
            self.skipTest(reference.msg)

        # Convert reference UTC time to local time, then to YYMMDD
        reference_local = reference.dt.astimezone()  # system local timezone
        expected = reference_local.strftime("%y%m%d")

        # ACT
        result = timestamp.now_local_date()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_format(self):
        """
        Should return a YYMMDD string with exactly 6 numeric characters.
        """
        # ARRANGE
        expected_length = 6

        # ACT
        result = timestamp.now_local_date()

        # ASSERT
        with self.subTest(Out=len(result), Exp=expected_length):
            self.assertEqual(len(result), expected_length)

        with self.subTest(Out=result.isdigit(), Exp=True):
            self.assertTrue(result.isdigit())

    def test_is_parsable(self):
        """
        Should return a date string that is parsable using '%y%m%d'.
        """
        # ARRANGE
        expected_format = "%y%m%d"

        # ACT
        result = timestamp.now_local_date()

        # ASSERT
        try:
            datetime.strptime(result, expected_format)
            parse_ok = True
        except ValueError:
            parse_ok = False

        with self.subTest(Out=parse_ok, Exp=True):
            self.assertTrue(parse_ok)


class TestNowLocalTime(unittest.TestCase):
    """
    Unit tests for the `now_local_time`.
    """

    def test_accuracy(self):
        """
        Should match the trusted local time derived from NTP/HTTP reference
        time, formatted as 'HHMMSS'. If reference time is not available or
        not reliable, the test is skipped.
        """
        # ARRANGE
        tolerance = 10 #seconds
        if not reference.valid:
            # Skip this accuracy test when we cannot trust the reference clock
            self.skipTest(reference.msg)

        # Reference local time
        reference_local = reference.dt.astimezone()
        ref_seconds = (
            reference_local.hour * 3600
            + reference_local.minute * 60
            + reference_local.second
        )

        # ACT
        text_result = timestamp.now_local_time()

        # Assume format has been validated by other tests: "HHMMSS"
        hour = int(text_result[0:2])
        minute = int(text_result[2:4])
        second = int(text_result[4:6])
        result_seconds = hour * 3600 + minute * 60 + second

        # Compute wrap-around-aware absolute difference in seconds
        seconds_in_day = 24 * 3600
        raw_diff = abs(ref_seconds - result_seconds)
        wrapped_diff = seconds_in_day - raw_diff
        delta = min(raw_diff, wrapped_diff)

        # ASSERT
        with self.subTest(Out=delta, Exp=tolerance):
            self.assertLessEqual(
                delta,
                tolerance,
                msg=(
                    f"Local time differs from reference by {delta}s, "
                    f"which exceeds tolerance of {tolerance}s. "
                    f"(ref={reference_local.strftime('%H:%M:%S')}, "
                    f"result={text_result})"
                ),
            )


    def test_format(self):
        """
        Should return an HHMMSS string with exactly 6 numeric characters.
        """
        # ARRANGE
        expected_length = 6

        # ACT
        result = timestamp.now_local_time()

        # ASSERT
        with self.subTest(Out=len(result), Exp=expected_length):
            self.assertEqual(len(result), expected_length)

        with self.subTest(Out=result.isdigit(), Exp=True):
            self.assertTrue(result.isdigit())

    def test_is_parsable(self):
        """
        Should return a time string that can be parsed using '%H%M%S'.
        """
        # ARRANGE
        expected_format = "%H%M%S"

        # ACT
        result = timestamp.now_local_time()

        # ASSERT
        try:
            datetime.strptime(result, expected_format)
            parse_ok = True
        except ValueError:
            parse_ok = False

        with self.subTest(Out=parse_ok, Exp=True):
            self.assertTrue(parse_ok)


class TestNowUtcIso(unittest.TestCase):
    """
    Unit tests for the `now_utc_iso` function in `src.utils.json`.

    This suite verifies that the function:
      - Returns an ISO 8601 timestamp string with a 'Z' UTC suffix.
      - Is precise to the second (no microseconds present).
      - Produces a time value consistent with the current UTC time at call.
    """

    def test_format_and_suffix(self):
        """
        Should return a string in the exact 'YYYY-MM-DDTHH:MM:SSZ' format with 'Z' suffix.
        """
        # ARRANGE
        iso_regex = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        # ACT
        result = timestamp.now_utc_iso()

        # ASSERT
        # Type check
        with self.subTest(Out=type(result).__name__, Exp=str.__name__):
            self.assertIsInstance(result, str)

        # Ends with 'Z'
        with self.subTest(Out=result.endswith("Z"), Exp=True):
            self.assertTrue(result.endswith("Z"))

        # Exact length "YYYY-MM-DDTHH:MM:SSZ" == 20 chars
        with self.subTest(Out=len(result), Exp=20):
            self.assertEqual(len(result), 20)

        # 'T' separator at the expected index (10)
        with self.subTest(Out=result[10], Exp="T"):
            self.assertEqual(result[10], "T")

        # Matches strict ISO pattern with Z suffix
        with self.subTest(Out=bool(iso_regex.match(result)), Exp=True):
            self.assertTrue(iso_regex.match(result) is not None)

        # No microseconds or explicit offset in the string
        with self.subTest(Out=("." in result), Exp=False):
            self.assertNotIn(".", result)
        with self.subTest(Out=("+00:00" in result), Exp=False):
            self.assertNotIn("+00:00", result)

    def test_value_within_current_utc_bounds(self):
        """
        Should produce a timestamp that falls between the UTC instants captured
        immediately before and after the call (inclusive), at second precision.
        """
        # ARRANGE
        # Capture lower bound (truncate to seconds)
        lower = datetime.now(timezone.utc).replace(microsecond=0)

        # ACT
        text_ts = timestamp.now_utc_iso()

        # Capture upper bound (truncate to seconds)
        upper = datetime.now(timezone.utc).replace(microsecond=0)

        # Convert back to aware UTC datetime for comparison
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        # Ensure parsed time is between lower and upper (inclusive)
        with self.subTest(Out=parsed.isoformat(),
                          Exp=f"[{lower.isoformat()} .. {upper.isoformat()}]"):
            self.assertLessEqual(lower, parsed)
            self.assertLessEqual(parsed, upper)

    def test_second_precision_no_microseconds(self):
        """
        Should represent time with second-level precision only (no microseconds).
        """
        # ARRANGE & ACT
        text_ts = timestamp.now_utc_iso()
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        with self.subTest(Out=parsed.microsecond, Exp=0):
            self.assertEqual(parsed.microsecond, 0)


if __name__ == '__main__':
    unittest.main()
