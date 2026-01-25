"""
Unit tests validating canonical BOM model structural invariants.

This module verifies that string-based attribute name constants remain exactly aligned with the corresponding dataclass field definitions at the model boundary and that explicit default values are applied when optional inputs are omitted. The tests operate without parsing, file I/O, or external system interaction and focus solely on structural consistency and default construction behavior.

Test scope
	- Verification that component attribute name constants exactly match the set of dataclass field names.
	- Verification that part attribute name constants exactly match the set of dataclass field names.
	- Verification that header attribute name constants exactly match the set of dataclass field names.
	- Verification of an explicit default value applied during canonical BOM construction when an optional field is omitted.
	- Happy-path structural alignment tests with no negative-path scenarios.

Execution
	Preferred execution via project-root invocation
		python -m unittest tests/models/test__canonical.py

	Test discovery (runs broader suite)
		python -m unittest discover

Test data and fixtures
	- Dataclass field metadata introspected directly at runtime.
	- Constant values read from in-memory class attributes.
	- Canonical BOM instance constructed with minimal in-memory inputs.
	- No temporary files, directories, or external resources are created.
	- No explicit cleanup is required.

Dependencies
	- Python 3.x
	- Standard Library: unittest, dataclasses

Notes
	- Tests are deterministic and hermetic, relying only on in-process reflection.
	- Structural mismatches between constants and dataclass fields will fail equality assertions.
	- The tests assume that all user-defined constants are uppercase string values.
	- Behavior beyond attribute alignment and explicit defaults is intentionally not exercised.

License
	Internal Use Only
"""

import unittest
from dataclasses import FrozenInstanceError, fields
from datetime import datetime

# noinspection PyProtectedMember
from src.models import _canonical as model


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


class TestCanonicalComponentAttrNames(unittest.TestCase):
    """
    Tests for CanonicalComponentAttrNames constants matching CanonicalComponent dataclass fields.
    """

    def test_attr_names_match_component_fields(self):
        """
        Should match CanonicalComponentAttrNames string constants to CanonicalComponent field names exactly.
        """
        # ARRANGE
        component_fields = {f.name for f in fields(model.CanonicalComponent)}
        const_values = _const_str_values_only(model.CanonicalComponentAttrNames)

        # ACT
        actual = const_values
        expected = component_fields

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_constants_are_uppercase_string_attributes(self):
        """
        Should expose only ALL_CAPS string constants that map to CanonicalComponent fields.
        """
        # ARRANGE
        component_fields = {f.name for f in fields(model.CanonicalComponent)}
        attrs = vars(model.CanonicalComponentAttrNames).items()

        # ACT / ASSERT
        for name, value in attrs:
            if not name.isupper():
                continue
            with self.subTest("const_name", Act=name, Exp="ALL_CAPS"):
                self.assertTrue(name.isupper())
            with self.subTest("const_value_type", Act=type(value), Exp=str):
                self.assertIsInstance(value, str)
            with self.subTest("const_value_is_field", Act=value, Exp=component_fields):
                self.assertIn(value, component_fields)


class TestCanonicalPartAttrNames(unittest.TestCase):
    """
    Tests for CanonicalPartAttrNames constants matching CanonicalPart dataclass fields.
    """

    def test_attr_names_match_part_fields(self):
        """
        Should match CanonicalPartAttrNames string constants to CanonicalPart field names exactly.
        """
        # ARRANGE
        part_fields = {f.name for f in fields(model.CanonicalPart)}
        const_values = _const_str_values_only(model.CanonicalPartAttrNames)

        # ACT
        actual = const_values
        expected = part_fields

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_constants_are_uppercase_string_attributes(self):
        """
        Should expose only ALL_CAPS string constants that map to CanonicalPart fields.
        """
        # ARRANGE
        part_fields = {f.name for f in fields(model.CanonicalPart)}
        attrs = vars(model.CanonicalPartAttrNames).items()

        # ACT / ASSERT
        for name, value in attrs:
            if not name.isupper():
                continue
            with self.subTest("const_name", Act=name, Exp="ALL_CAPS"):
                self.assertTrue(name.isupper())
            with self.subTest("const_value_type", Act=type(value), Exp=str):
                self.assertIsInstance(value, str)
            with self.subTest("const_value_is_field", Act=value, Exp=part_fields):
                self.assertIn(value, part_fields)


class TestCanonicalHeaderAttrNames(unittest.TestCase):
    """
    Tests for CanonicalHeaderAttrNames constants matching CanonicalHeader dataclass fields.
    """

    def test_attr_names_match_header_fields(self):
        """
        Should match CanonicalHeaderAttrNames string constants to CanonicalHeader field names exactly.
        """
        # ARRANGE
        header_fields = {f.name for f in fields(model.CanonicalHeader)}
        const_values = _const_str_values_only(model.CanonicalHeaderAttrNames)

        # ACT
        actual = const_values
        expected = header_fields

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_constants_are_uppercase_string_attributes(self):
        """
        Should expose only ALL_CAPS string constants that map to CanonicalHeader fields.
        """
        # ARRANGE
        header_fields = {f.name for f in fields(model.CanonicalHeader)}
        attrs = vars(model.CanonicalHeaderAttrNames).items()

        # ACT / ASSERT
        for name, value in attrs:
            if not name.isupper():
                continue
            with self.subTest("const_name", Act=name, Exp="ALL_CAPS"):
                self.assertTrue(name.isupper())
            with self.subTest("const_value_type", Act=type(value), Exp=str):
                self.assertIsInstance(value, str)
            with self.subTest("const_value_is_field", Act=value, Exp=header_fields):
                self.assertIn(value, header_fields)


class TestCanonicalBoard(unittest.TestCase):
    """
    Tests for CanonicalBoard dataclass invariants.
    """

    def test_fields_match_expected_names(self):
        """
        Should define exactly the 'header' and 'parts' fields.
        """
        # ARRANGE
        actual = {f.name for f in fields(model.CanonicalBoard)}
        expected = {"header", "parts"}

        # ACT / ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)


class TestCanonicalBom(unittest.TestCase):
    """
    Tests for CanonicalBom defaults and immutability.
    """

    def test_explicit_defaults(self):
        """
        Should default is_cost_bom to True when omitted.
        """
        # ARRANGE
        boards = tuple()

        # ACT
        bom = model.CanonicalBom(boards=boards)

        # ASSERT
        with self.subTest(Field="is_cost_bom", Act=bom.is_cost_bom, Exp=True):
            self.assertTrue(bom.is_cost_bom)


if __name__ == "__main__":
    unittest.main()
