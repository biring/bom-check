"""
Validate initialization behavior, dependency failure handling, execution contract enforcement, and immutable specification storage for a controller abstraction.

This module contains unit tests that verify that controller initialization correctly assigns externally provided resources without transformation, that initialization failures are surfaced as runtime errors with preserved context, that the execution entry point enforces an abstract contract by raising an error when not implemented, and that a separate immutable specification object stores provided metadata and class references accurately.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__base.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses unittest.mock.patch to replace external dependency functions and attributes with controlled return values and exceptions.
	- Constructs in-memory objects and dictionaries to simulate caches, key sets, and lookup tables.
	- Instantiates objects directly without filesystem or network interaction.
	- Relies on context-managed patching to ensure automatic restoration of original state after each test.

Dependencies:
	- Python 3.10+
	- Standard Library: unittest, unittest.mock

Notes:
	- Assertions verify object identity for injected dependencies, ensuring direct assignment rather than copying or transformation.
	- Failure scenarios validate both exception type and that the resulting message is non-empty and includes the original error reason.
	- Execution contract enforcement is validated by confirming an error is raised when the entry point is invoked without an override.
	- Tests are deterministic and hermetic due to complete control over external dependencies via mocking.

License:
	Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.controllers import _base as bc


class TestBaseController(unittest.TestCase):
    """
    Unit tests verifying base controller class.
    """

    def test_init(self) -> None:
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

    def test_run(self) -> None:
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

class TestControllerSpec(unittest.TestCase):
    """
    Unit tests verifying immutable specification stores controller metadata.
    """

    def test_happy_path(self) -> None:
        """
        Should create immutable spec with provided values.
        """
        # ARRANGE
        name = "base"
        description = "shared workflow controller"
        cls = bc.BaseController

        # ACT
        spec = bc.ControllerSpec(name=name, description=description, cls=cls)

        # ASSERT
        with self.subTest("Type"):
            self.assertIsInstance(spec, bc.ControllerSpec)

        with self.subTest("name field"):
            self.assertEqual(spec.name, name)

        with self.subTest("description field"):
            self.assertEqual(spec.description, description)

        with self.subTest("cls field"):
            self.assertIs(spec.cls, cls)

if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("\n*** ERROR ***")
        print(e)
