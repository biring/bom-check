"""
Unit tests for the `utils.parser` module.

This test suite validates parsing and validation helpers for primitive data types (dates, integers, floats, and strings). It ensures both the boolean-style `is_*` functions and strict `parse_to_*` functions behave consistently.

Example Usage (from project root):
    # Run test suite:
    python -m unittest tests.utils.test_parser

Dependencies:
    - Python >= 3.9
    - Standard Library: unittest
    - Internal: src.utils.parser

Notes:
    - Tests use `subTest` blocks for clearer reporting of multiple inputs.
    - Valid and invalid inputs cover normal cases, edge cases (e.g., leap years, zero padding), and invalid conditions (NaN, infinities, malformed strings).
    - Keeps alignment with `parser`’s design: validation (`is_*`) never raises, strict parsing (`parse_to_*`) raises `ValueError` on invalid input.

License:
    - Internal Use Only
"""

import unittest
from datetime import datetime

# noinspection PyProtectedMember
import src.utils._parser as parser


class TestIsValidDateString(unittest.TestCase):
    """
    Unit tests for the `is_valid_date_string` function.
    """

    def test_valid_iso(self):
        """
        Should return True for ISO "YYYY-MM-DD" dates with or without padding, and with trailing time.
        """
        # ARRANGE
        valid_inputs = [
            "2025-8-6",
            "2025-08-06",
            "2025-08-06T12:00",
            "2025-08-06 23:59",
        ]
        for s in valid_inputs:
            # ACT
            result = parser.is_valid_date_string(s)
            # ASSERT
            with self.subTest(In=s, Out=result, Exp=True):
                self.assertTrue(result)

    def test_valid_eu_dd_mm_yyyy(self):
        """
        Should return True for 'DD/MM/YYYY' dates with or without padding, and with trailing time.
        """
        # ARRANGE
        valid_inputs = [
            "6/8/2025",
            "06/08/2025",
            "6/8/2025 12:00",
        ]
        for s in valid_inputs:
            # ACT
            result = parser.is_valid_date_string(s)
            # ASSERT
            with self.subTest(In=s, Out=result, Exp=True):
                self.assertTrue(result)

    def test_valid_us_mm_dd_yyyy(self):
        """
        Should return True for 'MM/DD/YYYY' dates with or without padding, and with trailing time.
        """
        # ARRANGE
        valid_inputs = [
            "8/6/2025",
            "08/06/2025",
            "8/6/2025T23:59",
        ]
        for s in valid_inputs:
            # ACT
            result = parser.is_valid_date_string(s)
            # ASSERT
            with self.subTest(In=s, Out=result, Exp=True):
                self.assertTrue(result)

    def test_valid_edge_cases(self):
        """
        Should return True for edge-case valid dates (e.g., leap day).
        """
        # ARRANGE
        valid_inputs = [
            "2024-02-29",  # leap year ISO
            "29/02/2024",  # leap day DD/MM/YYYY
            "02/29/2024",  # leap day MM/DD/YYYY
            "01/02/2025",  # ambiguous but valid in both supported orders → still True
        ]
        for s in valid_inputs:
            # ACT
            result = parser.is_valid_date_string(s)
            # ASSERT
            with self.subTest(In=s, Out=result, Exp=True):
                self.assertTrue(result)

    def test_invalid_inputs(self):
        """
        Should return False for invalid or unsupported date strings.
        """
        # ARRANGE
        invalid_inputs = [
            "2025-13-01",  # invalid month
            "2025-02-30",  # invalid day
            "31/31/2025",  # invalid day/month
            "2025/08/06",  # unsupported separator for ISO
            "08-06-2025",  # unsupported separator for slashed formats
            "not-a-date",  # nonsensical
            "",  # empty
            " ",  # whitespace only
            "2025-02-29",  # non-leap-year Feb 29
        ]
        for s in invalid_inputs:
            # ACT
            result = parser.is_valid_date_string(s)
            # ASSERT
            with self.subTest(In=s, Out=result, Exp=False):
                self.assertFalse(result)


class TestIsStrictEmptyString(unittest.TestCase):
    """
    Unit tests for the `is_strict_empty_string` function.
    """

    def test_empty(self):
        """
        Should return True for an empty string.
        """
        # ARRANGE
        valid_inputs = [""]

        for val in valid_inputs:
            # ACT
            result = parser.is_strict_empty_string(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=True):
                self.assertTrue(result)

    def test_non_empty(self):
        """
        Should return False for any non-empty strings.
        """
        # ARRANGE
        invalid_inputs = [" ", "\t", "\n", "\r", "abc", None, {}, object()]

        for val in invalid_inputs:
            # ACT
            result = parser.is_strict_empty_string(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=False):
                self.assertFalse(result)


class TestIsFloat(unittest.TestCase):
    """
    Unit tests for the `is_float` function.
    """

    def test_valid(self):
        """
        Should return True for finite floats.
        """
        # ARRANGE
        valid_inputs = [
            "-3.14",
            "-1",
            "-0.0001",
            "-0.00",
            "-0",
            "0",
            "+0.0",
            "1",
            "3.14",
            "0.0001",
            "1000000",
        ]
        for val in valid_inputs:
            # ACT
            result = parser.is_float(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=True):
                self.assertTrue(result)

    def test_invalid(self):
        """
        Should return False for non-numeric strings and non-finite values (inf, -inf, NaN).
        """
        # ARRANGE
        invalid_inputs = ["abc", "1..2", " ", "", "NaN", "inf", "-inf", None, {}, object()]

        for val in invalid_inputs:
            # ACT
            result = parser.is_float(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=False):
                self.assertFalse(result)


class TestIsInteger(unittest.TestCase):
    """
    Unit tests for the `is_integer` function.
    """

    def test_valid(self):
        """
        Should return True for integers.
        """
        # ARRANGE
        valid_inputs = ["-999", "-1", "0", "1", "42", "999999"]
        for val in valid_inputs:
            # ACT
            result = parser.is_integer(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=True):
                self.assertTrue(result)

    def test_invalid(self):
        """
        Should return False for floats or non-numeric strings.
        """
        # ARRANGE
        invalid_inputs = ["3.14", "-2.5", "abc", "", " ", "NaN", "inf", None, {}, object()]

        for val in invalid_inputs:
            # ACT
            result = parser.is_integer(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=False):
                self.assertFalse(result)


class TestIsNonEmptyString(unittest.TestCase):
    """
    Unit tests for the `is_non_empty_string` function.
    """

    def test_empty(self):
        """
        Should return False for an empty string.
        """
        # ARRANGE
        empty_inputs = [""]

        for val in empty_inputs:
            # ACT
            result = parser.is_non_empty_string(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=False):
                self.assertFalse(result)

    def test_non_empty(self):
        """
        Should return True for any non-empty strings.
        """
        # ARRANGE
        non_empty_inputs = [" ", "\t", "\v", "abc", "0", None, {}, object()]

        for val in non_empty_inputs:
            # ACT
            result = parser.is_non_empty_string(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=True):
                self.assertTrue(result)


class TestParseToIsoDateString(unittest.TestCase):
    """
    Unit tests for the `parse_to_iso_date_string` function.
    """

    def test_valid_iso_format(self):
        """
        Should correctly parse ISO "YYYY-MM-DD" dates with or without padding.
        """
        # ARRANGE
        valid_cases = {
            "2025-8-6": "2025-08-06",  # no padding
            "2025-08-06": "2025-08-06",  # already padded
            "2025-08-06T12:00": "2025-08-06",  # with trailing time
            "2025-08-06 23:59": "2025-08-06",  # with space and time
        }

        for value, expected in valid_cases.items():
            # ACT
            result = parser.parse_to_iso_date_string(value)
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_eu_format(self):
        """
        Should correctly parse "DD/MM/YYYY" format with or without padding.
        """
        # ARRANGE
        valid_cases = {
            "6/8/2025": "2025-08-06",
            "06/08/2025": "2025-08-06",
            "6/8/2025 12:00": "2025-08-06",
        }

        for value, expected in valid_cases.items():
            # ACT
            result = parser.parse_to_iso_date_string(value)
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_us_format(self):
        """
        Should correctly parse "MM/DD/YYYY" format with or without padding.
        """
        # ARRANGE
        valid_cases = {
            "8/6/2025": "2025-06-08",
            "08/06/2025": "2025-06-08",
            "8/6/2025T23:59": "2025-06-08",
        }

        for value, expected in valid_cases.items():
            # ACT
            result = parser.parse_to_iso_date_string(value)
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_dates(self):
        """
        Should raise ValueError for invalid or unsupported date strings.
        """
        # ARRANGE
        invalid_inputs = [
            "2025-13-01",  # invalid month
            "2025-02-30",  # invalid day
            "31/31/2025",  # invalid day and month
            "2025/08/06",  # unsupported separator
            "08-06-2025",  # unsupported separator
            "not-a-date",  # nonsensical string
            "",  # empty string
            " ",  # whitespace only
        ]
        expected = ValueError.__name__

        for value in invalid_inputs:
            # ACT
            try:
                parser.parse_to_iso_date_string(value)
                result = None
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestParseToDatetime(unittest.TestCase):
    """
    Unit tests for the `parse_to_datetime` function.
    """

    def test_valid_dates(self):
        """
        Should return a datetime object at midnight (00:00:00) for valid date strings.
        """
        # ARRANGE
        valid_cases = {
            "2025-08-06": datetime(2025, 8, 6, 0, 0, 0),
            "2025-8-6": datetime(2025, 8, 6, 0, 0, 0),
            "6/8/2025": datetime(2025, 8, 6, 0, 0, 0),
            "08/06/2025": datetime(2025, 6, 8, 0, 0, 0),
            "2025-08-06T12:34": datetime(2025, 8, 6, 0, 0, 0),
            "2025-08-06 23:59": datetime(2025, 8, 6, 0, 0, 0),
        }

        for value, expected in valid_cases.items():
            # ACT
            result = parser.parse_to_datetime(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_dates(self):
        """
        Should raise ValueError for invalid or unsupported date strings.
        """
        # ARRANGE
        invalid_inputs = [
            "2025-13-01",  # invalid month
            "2025-02-30",  # invalid day
            "31/31/2025",  # invalid day/month
            "2025/08/06",  # unsupported separator
            "08-06-2025",  # unsupported separator
            "not-a-date",  # nonsensical string
            "",  # empty string
            " ",  # whitespace only
        ]
        expected = ValueError.__name__

        for value in invalid_inputs:
            # ACT
            try:
                parser.parse_to_datetime(value)
                result = None
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestParseToEmptyString(unittest.TestCase):
    """
    Unit tests for the `parse_to_empty_string` function.
    """

    def test_empty(self):
        """
        Should return "" for the empty string.
        """
        # ARRANGE
        valid_input = ""
        expected = ""

        # ACT
        result = parser.parse_to_empty_string(valid_input)
        # ASSERT
        with self.subTest(In=valid_input, Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_not_empty(self):
        """
        Should raise ValueError for not empty strings.
        """
        # ARRANGE
        invalid_inputs = [
            " ",  # whitespace
            "a",  # character
            "abc",  # string
        ]
        expected = ValueError.__name__

        for value in invalid_inputs:
            # ACT
            try:
                parser.parse_to_empty_string(value)
                result = None
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_not_string(self):
        """
        Should raise ValueError for non-string inputs (they get coerced to str, which is non-empty).
        """
        # ARRANGE
        invalid_inputs = [0, None, [], {}, object()]
        expected = ValueError.__name__

        for value in invalid_inputs:
            # ACT
            try:
                parser.parse_to_empty_string(value)  # type: ignore[arg-type]
                result = None
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestParseToNonEmptyString(unittest.TestCase):
    """
    Unit tests for the `parse_to_non_empty_string` function.
    """

    def test_not_empty(self):
        """
        Should return the string itself for not empty values.
        """
        # ARRANGE
        valid_inputs = ["a", "abc", " ", "0", "None"]

        for value in valid_inputs:
            expected = str(value)
            # ACT
            result = parser.parse_to_non_empty_string(value)
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_empty(self):
        """
        Should raise ValueError for the empty string.
        """
        # ARRANGE
        invalid_input = ""
        expected = ValueError.__name__

        try:
            # ACT
            parser.parse_to_non_empty_string(invalid_input)
            result = None
        except Exception as e:
            result = type(e).__name__
        # ASSERT
        with self.subTest(In=invalid_input, Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_string_inputs(self):
        """
        Should return string value for non-string inputs, unless they stringify to empty (which practically only happens for '').
        """
        # ARRANGE
        valid_inputs = [0, -1, 3.14, None, [1, 2], {"a": 1}]

        for value in valid_inputs:
            expected = str(value)
            # ACT
            result = parser.parse_to_non_empty_string(value)  # type: ignore[arg-type]
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestParseToFiniteFloat(unittest.TestCase):
    """
    Unit tests for the `parse_to_float` function.
    """

    def test_finite_float(self):
        """
        Should return the float value for finite float strings.
        """
        # ARRANGE
        valid_cases = {
            "-1e3": -1000.0,
            "-2.5": -2.5,
            "0": 0.0,
            "0e3": 0.0,
            "1": 1.0,
            "3.14": 3.14,
            "+25.8": 25.8,
            "1e3": 1000.0,
        }

        for val, expected in valid_cases.items():
            # ACT
            result = parser.parse_to_float(val)
            # ASSERT
            with self.subTest(In=val, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_not_finite_float(self):
        """
        Should raise ValueError for not finite float strings.
        """
        # ARRANGE
        invalid_inputs = [
            "abc",  # non-numeric string
            "1..2",  # malformed numeric string
            "",  # empty
            " ",  # whitespace only
            None,  # non-string input
            [],  # non-string input
            {},  # non-string input
            object(),  # non-string input
            "NaN",  # NaN
            "nan",  # NaN
            "inf",  # +Inf
            "-inf",  # -Inf
            "1e5000",  # overflows to Inf
        ]
        expected = ValueError.__name__

        for value in invalid_inputs:
            # ACT
            try:
                parser.parse_to_float(value)
                result = None
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestParseToInteger(unittest.TestCase):
    """
    Unit tests for the `parse_to_integer` function.
    """

    def test_integer_string(self):
        """
        Should return integer value for valid integer strings.
        """
        # ARRANGE
        valid_cases = {
            "-999": -999,
            "-1": -1,
            "0": 0,
            "0007": 7,  # leading zeros
            "42": 42,
            "+107": 107,
        }

        for value, expected in valid_cases.items():
            # ACT
            result = parser.parse_to_integer(value)
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_not_integer_string(self):
        """
        Should raise ValueError for non-integer strings.
        """
        # ARRANGE
        invalid_inputs = [
            "3.14",
            "-2.5",
            "abc",
            "",
            " ",
            "1..2",
            None,
            [],
            {},
            object(),
        ]
        expected = ValueError.__name__

        for value in invalid_inputs:
            # ACT
            try:
                parser.parse_to_integer(value)
                result = None
            except Exception as e:
                result = type(e).__name__
            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
