"""
Unit tests validating version 3 BOM data model invariants at the model boundary.

The tests exercise dataclass defaults and constant definitions without involving parsing, I/O, or external systems.

The purpose of this module is to assert that string-based attribute name constants remain exactly aligned with dataclass field definitions and that default values are applied consistently when instances are constructed with omitted optional inputs. Behavior beyond default values and structural alignment, such as validation, parsing, or business rules, is intentionally out of scope.

Test scope
- Verification that attribute name constants for row-level data exactly match the corresponding dataclass field names.
- Verification that attribute name constants for header-level data exactly match the corresponding dataclass field names.
- Verification that all row-level dataclass fields default to empty strings.
- Verification that all header-level dataclass fields default to empty strings.
- Verification of explicit default values applied at the top-level BOM aggregate when optional arguments are omitted.
- Coverage includes happy-path assertions only; no negative-path or error-condition tests are present.

Execution
	Preferred execution via project-root invocation
	python -m unittest tests.models.test__bom_v3

	Test discovery (runs broader suite)
	python -m unittest discover

Test data and fixtures
	- Test data is created inline using direct dataclass construction.
	- No temporary files, directories, or external resources are used.
	- No mocks, patches, or stubs are applied.
	- Cleanup is not required due to absence of side effects.

Dependencies
	- Python 3.x
	- Standard Library: unittest, dataclasses

Notes
	- Tests rely on dataclass field introspection to remain deterministic and hermetic.
	- Assertions assume immutability and absence of runtime mutation.
	- Constant extraction filters attributes by uppercase naming convention, which is relied upon implicitly by the tests.

License
	Internal Use Only
"""

import unittest
from dataclasses import fields

# noinspection PyProtectedMember
from src.models import _bom_v3 as model


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
