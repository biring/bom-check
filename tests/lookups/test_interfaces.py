"""
Integration tests validating the public lookup interfaces for JSON-backed resources.

This module verifies that the publicly exposed lookup access functions return dictionary-based lookup tables under normal conditions and raise a RuntimeError with a non-empty, informative message when cache initialization fails. The tests treat the interfaces as stable entry points and avoid asserting internal loading, parsing, or caching implementation details beyond observable behavior.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/lookups/test_interfaces.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- No external test data files are created; tests rely on existing packaged lookup resources.
	- Internal cache state is reset before and after each test by explicitly clearing module-level cache variables.
	- Failure scenarios are simulated using unittest.mock.patch to force exceptions during cache initialization.

Dependencies:
	- Python >= 3.10
	- Standard Library: unittest, unittest.mock

Notes:
	- Tests are integration-style and validate only observable contract behavior of the public lookup accessors.
	- Successful calls are asserted to return dictionary instances without validating specific contents.
	- Error-path tests assert that unexpected initialization failures are surfaced as RuntimeError instances containing a non-empty message that includes the triggering reason.
	- Private modules are accessed only to reset cache state and simulate initialization failures.

License:
	Internal Use Only
"""

import unittest

from unittest.mock import patch

from src.lookups import interfaces as lookup

# noinspection PyProtectedMember
from src.lookups import _board_supplier_codes as bsc  # For patch

# noinspection PyProtectedMember
from src.lookups import _component_type as ct  # For patch


class TestGetBoardSupplierCodesLookupTable(unittest.TestCase):
    """
    Unit tests verifying the public interface for retrieving the board supplier codes lookup table.
    """

    def setUp(self) -> None:
        bsc._cache = None  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        bsc._cache = None  # type: ignore[attr-defined]

    def test_happy_path(self) -> None:
        """
        Should return a dictionary lookup table on successful invocation.
        """
        # ARRANGE

        # ACT
        result = lookup.get_board_supplier_codes_lookup_table()

        # ASSERT
        with self.subTest("Return value type"):
            self.assertIsInstance(result, dict)

        with self.subTest("Return value is not empty"):
            self.assertNotEqual(result, {})

    def test_raises(self) -> None:
        """
        Should raise RuntimeError when cache initialization fails.
        """
        # ARRANGE
        expected_type = RuntimeError.__name__
        expected_reason = "Unexpected error"

        patch_file = bsc
        patch_function = patch_file.CacheReadOnly.__name__

        # ACT
        try:
            with patch.object(
                    patch_file,
                    patch_function,
                    side_effect=Exception(expected_reason),
            ):
                bsc.get_board_supplier_codes_lookup_table()
            actual = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

        actual_message = str(actual)
        with self.subTest("Message contains reason", Exp=expected_reason, Act=actual_message):
            self.assertIn(expected_reason, actual_message)


class TestGetComponentTypeLookupTable(unittest.TestCase):
    """
    Unit tests verifying the public interface for retrieving the component type lookup table.
    """

    def setUp(self) -> None:
        ct._cache = None  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        ct._cache = None  # type: ignore[attr-defined]

    def test_happy_path(self) -> None:
        """
        Should return a dictionary lookup table on successful invocation.
        """
        # ARRANGE

        # ACT
        result = lookup.get_component_type_lookup_table()

        # ASSERT
        with self.subTest("Return value type"):
            self.assertIsInstance(result, dict)

        with self.subTest("Return value is not empty"):
            self.assertNotEqual(result, {})

    def test_raises(self) -> None:
        """
        Should raise RuntimeError when cache initialization fails.
        """
        # ARRANGE
        expected_type = RuntimeError.__name__
        expected_reason = "Unexpected error"

        patch_file = ct
        patch_function = patch_file.CacheReadOnly.__name__

        # ACT
        try:
            with patch.object(
                    patch_file,
                    patch_function,
                    side_effect=Exception(expected_reason),
            ):
                ct.get_component_type_lookup_table()
            actual = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

        actual_message = str(actual)
        with self.subTest("Message contains reason", Exp=expected_reason, Act=actual_message):
            self.assertIn(expected_reason, actual_message)


if __name__ == '__main__':
    unittest.main()
