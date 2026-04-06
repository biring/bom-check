"""
Validate that the public controller menu interface returns structured tuple data.

This module contains unit tests that exercise the exposed callable for building controller menu data and verify that it returns a tuple containing two tuple elements representing menu options and controller callables, without asserting on their contents.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test_interfaces.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- No external test data is created or managed; tests invoke the callable directly
	- No temporary files or directories are used
	- No cleanup steps are required

Dependencies:
	- Python version: >= 3.8
	- Standard Library: unittest

Notes:
	- Tests validate only the return type and high-level structure, not the contents or semantics of the returned data
	- Relies on the external interface remaining callable without required arguments
	- Uses subtests to isolate type assertions within a single test case

License:
	- Internal Use Only
"""

import unittest

from src.controllers import interfaces as controller


class TestBuildControllerMenu(unittest.TestCase):
    """Unit tests verifying build_controller_menu provides a callable interface returning menu data."""

    def test_happy_path(self) -> None:
        """Should return menu options and controller classes as tuples."""
        # ARRANGE
        func = controller.build_controller_menu

        # ACT
        result = func()
        menu_options, controller_calls = result


        # ASSERT
        with self.subTest("Return type is tuple"):
            self.assertIsInstance(result, tuple)

        with self.subTest("Return length"):
            self.assertEqual(len(result), 2)

        with self.subTest("Menu options type"):
            self.assertIsInstance(menu_options, tuple)

        with self.subTest("Controller calls type"):
            self.assertIsInstance(controller_calls, tuple)


if __name__ == '__main__':
    unittest.main()
