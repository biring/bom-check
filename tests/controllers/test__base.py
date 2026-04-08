"""
Validate initialization, subclass registration, execution contract enforcement, folder selection caching behavior, and immutable specification storage for a controller abstraction.

This module contains unit tests that verify initialization assigns externally provided dependencies by identity, that initialization failures are surfaced as runtime errors with preserved context, that subclass registration occurs exactly once and enforces required metadata, that the execution entry point raises an error when not implemented, that folder selection updates cached values only when changed, and that an immutable specification object stores provided metadata and class references accurately. :contentReference[oaicite:0]{index=0}

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__base.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses unittest.mock.patch to replace external dependency functions and attributes with controlled return values and exceptions.
	- Constructs in-memory objects and mock instances to simulate caches and lookup data.
	- Instantiates objects directly and, where needed, bypasses initialization to inject controlled state.
	- Relies on context-managed patching to ensure automatic restoration after each test.

Dependencies:
	- Python 3.10+
	- Standard Library: unittest, unittest.mock

Notes:
	- Assertions verify object identity for injected dependencies, ensuring no copying or transformation occurs.
	- Failure scenarios validate exception type and that error messages are non-empty and include the originating reason when provided.
	- Subclass registration tests confirm idempotent registration and enforce presence of required metadata at class definition time.
	- Folder selection behavior is validated by comparing cached and selected values and asserting conditional cache updates.
	- Tests are deterministic and hermetic through use of mocking and in-memory constructs without filesystem or network interaction.

License:
	Internal Use Only
"""

import unittest
from unittest.mock import patch, Mock

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
        actual_type = type(actual).__name__ # noqa
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

        if expected_reason is not None:
            actual_message = str(actual)
            with self.subTest("Message contains reason"):
                self.assertIn(expected_reason, actual_message)

    def test_duplicate_registration(self) -> None:
        """
        Should not register subclass more than once.
        """
        # ARRANGE
        with patch.object(bc.BaseController, "registry", []):
            class ValidController(bc.BaseController):
                name = "valid"
                description = "valid controller"

        # ACT
        ValidController.__init_subclass__()
        occurrences = bc.BaseController.registry.count(ValidController)

        # ASSERT
        with self.subTest("Single registration"):
            self.assertEqual(occurrences, 1)

    def test_missing_metadata(self) -> None:
        """
        Should raise when metadata is missing.
        """
        # ARRANGE
        expected_type = TypeError.__name__

        # ACT
        try:
            class InvalidController(bc.BaseController): # noqa
                name = None
                description = None
            actual = ""
        except Exception as exc:
            actual = exc

        # ASSERT
        actual_type = type(actual).__name__ # noqa
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

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
        except Exception as exc:
            actual = exc

        # ASSERT
        actual_type = type(actual).__name__ # noqa
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

    def test_get_folder_with_cache_update(self) -> None:
        """
        Should return selected folder and update cache when value changes.
        """
        # ARRANGE
        controller = bc.BaseController.__new__(bc.BaseController)
        old_value = "/old"
        new_value = "/new"

        mock_cache = Mock()
        mock_cache.get_value.return_value = old_value
        mock_cache.update_value = Mock()

        controller.temp_settings_cache = mock_cache

        patch_file_menu = bc.menu
        patch_function_menu = patch_file_menu.folder_selector.__name__

        with patch.object(patch_file_menu, patch_function_menu, return_value=new_value):
            # ACT
            result = controller.get_folder(
                settings_key="key",
                dialog_title="title",
                dialog_prompt="prompt",
            )

            # ASSERT
            with self.subTest("Return value"):
                self.assertEqual(result, new_value)

            with self.subTest("Update called"):
                self.assertTrue(mock_cache.update_value.called)

    def test_get_folder_with_no_cache_update(self) -> None:
        """
        Should not update cache when selected folder matches cached value.
        """
        # ARRANGE
        controller = bc.BaseController.__new__(bc.BaseController)
        cached_value = "/same"

        mock_cache = Mock()
        mock_cache.get_value.return_value = cached_value
        mock_cache.update_value = Mock()

        controller.temp_settings_cache = mock_cache

        patch_file_menu = bc.menu
        patch_function_menu = patch_file_menu.folder_selector.__name__

        with patch.object(patch_file_menu, patch_function_menu, return_value=cached_value):
            # ACT
            result = controller.get_folder(
                settings_key="key",
                dialog_title=None,
                dialog_prompt=None,
            )

            # ASSERT
            with self.subTest("Return value"):
                self.assertEqual(result, cached_value)

            with self.subTest("Update not called"):
                self.assertFalse(mock_cache.update_value.called)

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
