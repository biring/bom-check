"""
Validate alignment and default behaviors of a version 3 BOM data model at the model boundary.

This module verifies that string-based attribute name constants exactly match corresponding dataclass field names and that default values are consistently applied when instances are constructed with omitted optional inputs. It also checks that string representations of instances produce multi-line, human-readable output without trailing newline characters. The tests operate purely at the data structure level and avoid parsing, I/O, or external integrations.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/models/test__bom_v3.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Test data is primarily created inline via direct dataclass instantiation.
	- A shared fixture object is imported and used to validate string output behavior.
	- No temporary files, directories, or external resources are used.
	- No mocks, patches, or stubs are applied.
	- No cleanup is required due to absence of side effects.

Dependencies:
	- Python 3.x (dataclasses and modern type hint syntax usage).
	- Standard Library: unittest, dataclasses

Notes:
	- Field-to-constant alignment is verified via dataclass field introspection and filtering of uppercase attributes.
	- Tests assume deterministic ordering is not required by comparing sets of field names and constant values.
	- String representation checks validate formatting characteristics such as label transformation, multi-line output, and absence of trailing newline.
	- Fixture-based string tests rely on preconstructed instances and do not validate field-level defaults in those cases.
	- Coverage is limited to happy-path assertions; no negative or error-condition scenarios are exercised.

License:
	Internal Use Only
"""

import unittest
from dataclasses import fields

# noinspection PyProtectedMember
from src.models import _bom_v3 as model

from tests.fixtures import v3_bom as bfx  # noqa: F401  # Imported for potential future use; not currently referenced in tests


def _const_str_values_only(cls) -> set[str]:
    """
    Return only the string values of user-defined constant attributes.

    Filters out dunder attributes like __module__ and __doc__ by requiring ALL_CAPS names.
    """
    return {
        value
        for name, value in vars(cls).items()
        if name.isupper() and isinstance(value, str)
    }


class TestRowV3AttrNames(unittest.TestCase):
    """
    Tests for RowV3AttrNames constants matching RowV3 dataclass fields.
    """

    def test_attr_names_match_row_v3_fields(self):
        """
        RowV3AttrNames string constants match RowV3 field names exactly.
        """
        # ARRANGE
        row_fields = {f.name for f in fields(model.RowV3)}
        const_values = _const_str_values_only(model.RowV3AttrNames)

        # ACT
        actual = const_values
        expected = row_fields

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)


class TestHeaderV3AttrNames(unittest.TestCase):
    """
    Tests for HeaderV3AttrNames constants matching HeaderV3 dataclass fields.
    """

    def test_attr_names_match_header_v3_fields(self):
        """
        HeaderV3AttrNames string constants match HeaderV3 field names exactly.
        """
        # ARRANGE
        header_fields = {f.name for f in fields(model.HeaderV3)}
        const_values = _const_str_values_only(model.HeaderV3AttrNames)

        # ACT
        actual = const_values
        expected = header_fields

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)

class TestBomV3Base(unittest.TestCase):
    """
    Unit tests verifying formatted string representation of instance attributes.
    """

    def test_happy_path(self) -> None:
        """
        Should return a formatted string containing attribute labels and values.
        """
        # ARRANGE
        class Dummy(model._BomV3Base):
            def __init__(self):
                self.first_field = 200 # int value to test string conversion
                self.second_field = 2.50 #`float value to test string conversion
                self.third_field = "ABC123" # string value to test normal case
                self.fourth_field = "2025-12-12" # string value to test date-like formatting
                self.fifth_field = "Main PCB" # string value to test normal case
                self.sixth_field = "value6" # need six fields to test multiple lines and not end with newline

        instance = Dummy()

        # ACT
        result = str(instance)

        # ASSERT
        with self.subTest("Type check"):
            self.assertIsInstance(result, str)

        with self.subTest("Is multiple lines"):
            self.assertIn("\n", result)

        with self.subTest("No trailing newline"):
            self.assertFalse(result.endswith("\n"))

        with self.subTest("Normalized label"):
            self.assertIn("First Field:", result) # derived from first_field with underscore replaced by space and title-cased

        with self.subTest("Value correct"):
            self.assertIn("ABC123", result)

class TestRowV3(unittest.TestCase):
    """
    Tests for RowV3 defaults.
    """

    def test_defaults_are_empty_strings(self):
        """
        RowV3 defaults every field to the empty string.
        """
        # ARRANGE
        row = model.RowV3()

        # ACT / ASSERT
        for f in fields(model.RowV3):
            actual = getattr(row, f.name)
            expected = ""
            with self.subTest(Field=f.name, Act=actual, Exp=expected):
                self.assertEqual(actual, expected)

    def test_printout_string(self):
        """
        Should provide a non-empty string over multiple lines without error.
        """
        # ARRANGE
        row = bfx.ROW_A_1

        # ACT
        actual = str(row)

        # ASSERT
        with self.subTest("Is Not Empty"):
            self.assertTrue(actual)  # non-empty string
        with self.subTest("Is Multi-Line"):
            self.assertIn("\n", actual)  # multi-line string


class TestHeaderV3(unittest.TestCase):
    """
    Tests for HeaderV3 defaults.
    """

    def test_defaults_are_empty_strings(self):
        """
        HeaderV3 defaults every field to the empty string.
        """
        # ARRANGE
        header = model.HeaderV3()

        # ACT / ASSERT
        for f in fields(model.HeaderV3):
            actual = getattr(header, f.name)
            expected = ""
            with self.subTest(Field=f.name, Act=actual, Exp=expected):
                self.assertEqual(actual, expected)

    def test_printout_string(self):
        """
        Should provide a non-empty string over multiple lines without error.
        """
        # ARRANGE
        row = bfx.ROW_A_1

        # ACT
        actual = str(row)

        # ASSERT
        with self.subTest("Is Not Empty"):
            self.assertTrue(actual)  # non-empty string
        with self.subTest("Is Multi-Line"):
            self.assertIn("\n", actual)  # multi-line string



class TestBomV3(unittest.TestCase):
    """
    Tests for BomV3 explicit defaults.
    """

    def test_explicit_defaults(self):
        """
        BomV3 defaults file_name to '' and is_cost_bom to True when omitted.
        """
        # ARRANGE
        boards = tuple()

        # ACT
        bom = model.BomV3(boards=boards)

        # ASSERT
        with self.subTest(Field="file_name", Act=bom.file_name, Exp=""):
            self.assertEqual(bom.file_name, "")
        with self.subTest(Field="is_cost_bom", Act=bom.is_cost_bom, Exp=True):
            self.assertTrue(bom.is_cost_bom)


if __name__ == "__main__":
    unittest.main()
