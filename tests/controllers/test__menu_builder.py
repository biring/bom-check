"""
Validate construction of sorted menu options and aligned controller classes from a registry.

This module tests that a registry of controller-like classes is transformed into deterministic, user-facing menu strings paired with corresponding callable classes, while enforcing uniqueness constraints and handling construction failures by raising appropriate exceptions.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__menu_builder.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Defines in-test dummy subclasses with required metadata attributes to simulate registry entries.
	- Directly overrides a global registry list to control test scenarios.
	- Restores the original registry state in teardown to prevent cross-test contamination.
	- Uses mocking to simulate construction failures by forcing exceptions during specification creation.

Dependencies:
	- Python version: >= 3.9
	- Standard Library: unittest, unittest.mock

Notes:
	- Relies on mutation of a shared global registry, requiring careful setup and teardown for isolation.
	- Verifies deterministic ordering by asserting lexicographic sorting of menu output.
	- Confirms alignment between display strings and callable classes via positional equality.
	- Asserts error handling for duplicate identifiers and for failures during intermediate object construction.

License:
	- Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.controllers import _menu_builder as ctrl


class TestGetControllers(unittest.TestCase):
    """
    Unit tests verifying construction of controller menu options and aligned controller classes.
    """

    def setUp(self) -> None:
        self._original_registry = list(ctrl.bc.BaseController.registry)

    def tearDown(self) -> None:
        ctrl.bc.BaseController.registry = self._original_registry


    def test_happy_path(self) -> None:
        """
        Should return sorted menu options and corresponding controller classes.
        """
        # ARRANGE
        class DummyControllerA(ctrl.bc.BaseController):
            name = "A"
            description = "desc A"

            def run(self) -> None:
                pass

        class DummyControllerB(ctrl.bc.BaseController):
            name = "B"
            description = "desc B"

            def run(self) -> None:
                pass

        ctrl.bc.BaseController.registry = [DummyControllerA, DummyControllerB]

        # ACT
        menu_options, controller_calls = ctrl.build_controller_menu()

        # ASSERT
        with self.subTest("Return type menu_options"):
            self.assertIsInstance(menu_options, tuple)

        with self.subTest("Return type controller_calls"):
            self.assertIsInstance(controller_calls, tuple)

        with self.subTest("Menu options ordering"):
            self.assertEqual(menu_options, ("A: desc A", "B: desc B"))

        with self.subTest("Controller ordering"):
            self.assertEqual(controller_calls, (DummyControllerA, DummyControllerB))

    def test_duplicate_names(self) -> None:
        """
        Should raise ValueError when duplicate controller names are present.
        """
        # ARRANGE
        class DummyControllerA(ctrl.bc.BaseController):
            name = "A"
            description = "desc A"

            def run(self) -> None:
                pass

        class DummyControllerB(ctrl.bc.BaseController):
            name = "A"
            description = "desc B"

            def run(self) -> None:
                pass

        ctrl.bc.BaseController.registry = [DummyControllerA, DummyControllerB]

        expected_type = ValueError.__name__
        expected_reason = "Duplicate controller name"

        # ACT
        try:
            ctrl.build_controller_menu()
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
        with self.subTest("Message contains reason"):
            self.assertIn(expected_reason, actual_message)

    def test_spec_build_failure(self) -> None:
        """
        Should raise RuntimeError when ControllerSpec construction fails.
        """
        # ARRANGE
        class DummyControllerA(ctrl.bc.BaseController):
            name = "A"
            description = "desc A"

            def run(self) -> None:
                pass

        class DummyControllerB(ctrl.bc.BaseController):
            name = "B"
            description = "desc B"

            def run(self) -> None:
                pass

        ctrl.bc.BaseController.registry = [DummyControllerA, DummyControllerB]

        def raise_error(*args, **kwargs):
            raise Exception("boom")

        patch_file = ctrl.bc
        patch_function = patch_file.ControllerSpec.__name__

        expected_type = RuntimeError.__name__
        expected_reason = "boom"

        with patch.object(patch_file, patch_function, side_effect=raise_error):
            # ACT
            try:
                ctrl.build_controller_menu()
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
        with self.subTest("Message contains reason"):
            self.assertIn(expected_reason, actual_message)

if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("\n*** ERROR ***")
        print(e)