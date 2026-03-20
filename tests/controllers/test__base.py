"""
Validates initialization behavior and execution contract enforcement for a base controller.

This module contains unit tests that verify correct initialization of internal state using external dependencies and proper error handling when those dependencies fail, as well as enforcement of an abstract execution contract by ensuring a runtime error is raised when a required method is not implemented.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__base.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses unittest.mock.patch to replace dependency functions and attributes with controlled return values and side effects.
	- Creates in-memory objects and dictionaries to simulate cache data and lookup tables.
	- No filesystem or external resource interaction is present; all data is ephemeral and scoped to individual tests.
	- Relies on context-managed patching to ensure automatic cleanup after each test.

Dependencies:
	- Python 3.10+
	- Standard Library: unittest, unittest.mock

Notes:
	- Tests assert identity (not equality) for injected dependencies, ensuring objects are assigned directly without transformation.
	- Error handling validation checks both exception type and that the message is non-empty and contains the original failure reason.
	- Initialization behavior is sensitive to external dependency failures, which are simulated via exception side effects.
	- Execution contract enforcement is validated by confirming that direct invocation raises a not-implemented error.
	- Tests are deterministic and hermetic due to controlled mocking of all external interactions.

License:
	Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.controllers import _base as bc


class TestBaseController(unittest.TestCase):
    """
    Unit tests verifying initialization of shared caches and lookup table.
    """

    def test_happy_path(self) -> None:
        """
        Should initialize all expected attributes using provided dependencies.
        """
        # ARRANGE
        expected_cache = object()
        expected_keys = {"key1", "key2"}
        expected_lookup = {"type": "value"}

        patch_file_temp = bc.temporary
        patch_function_temp = patch_file_temp.get_temp_settings.__name__

        patch_file_lookup = bc.lookup
        patch_function_lookup = patch_file_lookup.get_component_type_lookup_table.__name__

        with (patch.object(
                patch_file_temp, patch_function_temp, return_value=expected_cache),
            patch.object(patch_file_temp, "KEYS", expected_keys),
            patch.object(patch_file_lookup, patch_function_lookup, return_value=expected_lookup)
        ):
            # ACT
            controller = bc.BaseController()

            # ASSERT
            with self.subTest("temp_settings_cache identity"):
                self.assertIs(controller.temp_settings_cache, expected_cache)

            with self.subTest("temp_setting_keys identity"):
                self.assertIs(controller.temp_setting_keys, expected_keys)

            with self.subTest("component_type_cache identity"):
                self.assertIs(controller.component_type_cache, expected_lookup)

    def test_dependency_failure(self) -> None:
        """
        Should raise RuntimeError when a dependency fails during initialization.
        """
        # ARRANGE
        patch_file_temp = bc.temporary
        patch_function_temp = patch_file_temp.get_temp_settings.__name__

        expected_type = RuntimeError.__name__
        expected_reason = "boom"

        with patch.object(patch_file_temp, patch_function_temp, side_effect=Exception(expected_reason)):

            # ACT
            try:
                bc.BaseController()
                actual = ""
            except Exception as exc:
                actual = exc

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

        if expected_reason is not None:
            actual_message = str(actual)
            with self.subTest("Message contains reason"):
                self.assertIn(expected_reason, actual_message)


class Testrun(unittest.TestCase):
    """
    Unit tests verifying enforcement of subclass execution contract.
    """

    def test_happy_path(self) -> None:
        """
        Should raise NotImplementedError when called directly.
        """
        # ARRANGE
        controller = bc.BaseController()
        expected_type = NotImplementedError.__name__

        # ACT
        try:
            controller.run()
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


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("\n*** ERROR ***")
        print(e)
