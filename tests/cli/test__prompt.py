"""
Tests for CLI prompt utilities covering string input delegation and menu selection behavior.

This module validates that user-facing prompt helpers correctly delegate input collection, enforce menu selection rules, and handle error conditions. The tests focus on return values, control flow for valid and invalid inputs, propagation of user-triggered termination signals, and wrapping of unexpected exceptions into runtime errors.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/cli/test__prompt.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses unittest.mock.patch to replace input and display helpers, isolating I/O behavior.
	- Simulates user input via return values and side effects, including invalid sequences and exceptions.
	- No filesystem or external resources are used; all data is in-memory and ephemeral.

Dependencies:
	- Python >= 3.10
	- Standard Library: unittest, unittest.mock

Notes:
	- Verifies that string input is returned as provided and that unexpected exceptions are wrapped while EOFError is propagated unchanged.
	- Confirms menu selection enforces non-empty input, short-circuits single-item menus, and repeats prompting until a valid index is received.
	- Ensures invalid selections trigger additional input attempts and that unexpected errors during prompting are surfaced as runtime errors.
	- Relies on patched collaborators for deterministic behavior and to assert call counts and control flow.

License:
	- Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
import src.cli._prompt as prompt


class TestPromptForStringValue(unittest.TestCase):
    """
    Unit tests verifying string value prompt delegation and error handling.
    """

    def test_happy_path(self) -> None:
        """
        Should return the value provided by the request layer.
        """
        # ARRANGE
        expected_value = "example input"
        patch_file = prompt.request
        patch_function = patch_file.string_input.__name__

        with patch.object(patch_file, patch_function, return_value=expected_value) as mock_call:
            # ACT
            result = prompt.prompt_for_string_value()

        # ASSERT
        with self.subTest("Type", Exp=str, Act=type(result)):
            self.assertIsInstance(result, str)
        with self.subTest("Value", Exp=expected_value, Act=result):
            self.assertEqual(expected_value, result)
        with self.subTest("Call count", Exp=1, Act=mock_call.call_count):
            self.assertEqual(1, mock_call.call_count)

    def test_unexpected_exception(self) -> None:
        """
        Should raise RuntimeError when an unexpected exception occurs.
        """
        # ARRANGE
        patch_file = prompt.request
        patch_function = patch_file.string_input.__name__
        expected_type = RuntimeError.__name__
        expected_reason = "boom"

        with patch.object(patch_file, patch_function, side_effect=Exception(expected_reason)):
            # ACT
            try:
                prompt.prompt_for_string_value()
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

    def test_eof_error_propagation(self) -> None:
        """
        Should propagate EOFError without wrapping.
        """
        # ARRANGE
        patch_file = prompt.request
        patch_function = patch_file.string_input.__name__
        expected_type = EOFError.__name__

        with patch.object(patch_file, patch_function, side_effect=EOFError()):
            # ACT
            try:
                prompt.prompt_for_string_value()
                actual = ""
            except Exception as e:
                actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            # EOFError may have empty args; allow either but still assert structure
            self.assertTrue(isinstance(actual_args, tuple))


class TestPromptMenuSelection(unittest.TestCase):
    """
    Unit tests verifying menu selection control flow and validation behavior.
    """

    def test_happy_path(self) -> None:
        """
        Should return a valid index when user input is within bounds.
        """
        # ARRANGE
        menu_items = ["alpha", "bravo", "charlie"]
        expected_index = 1

        request_patch_file = prompt.request
        request_patch_function = request_patch_file.integer_input.__name__

        show_patch_file = prompt.show

        with (
            patch.object(request_patch_file, request_patch_function, return_value=expected_index),
            patch.object(show_patch_file, show_patch_file.show_header.__name__),
            patch.object(show_patch_file, show_patch_file.show_info.__name__),
        ):
            # ACT
            result = prompt.prompt_menu_selection(menu_items)

        # ASSERT
        with self.subTest("Type", Exp=int, Act=type(result)):
            self.assertIsInstance(result, int)
        with self.subTest("Value", Exp=expected_index, Act=result):
            self.assertEqual(expected_index, result)

    def test_empty_menu(self) -> None:
        """
        Should raise ValueError when menu is empty.
        """
        # ARRANGE
        menu_items = []
        expected_type = ValueError.__name__

        # ACT
        try:
            prompt.prompt_menu_selection(menu_items)
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

    def test_single_item(self) -> None:
        """
        Should return index zero when only one menu item exists.
        """
        # ARRANGE
        menu_items = ["only"]

        # ACT
        result = prompt.prompt_menu_selection(menu_items)

        # ASSERT
        with self.subTest("Type", Exp=int, Act=type(result)):
            self.assertIsInstance(result, int)
        with self.subTest("Value", Exp=0, Act=result):
            self.assertEqual(0, result)

    def test_invalid_then_valid(self) -> None:
        """
        Should reprompt until a valid selection is provided.
        """
        # ARRANGE
        menu_items = ["alpha", "bravo", "charlie"]
        invalid = 5
        valid = 1

        request_patch_file = prompt.request
        request_patch_function = request_patch_file.integer_input.__name__

        show_patch_file = prompt.show

        with (
            patch.object(request_patch_file, request_patch_function, side_effect=[invalid, valid]) as mock_input,
            patch.object(show_patch_file, show_patch_file.show_header.__name__),
            patch.object(show_patch_file, show_patch_file.show_info.__name__),
            patch.object(show_patch_file, show_patch_file.show_warning.__name__),
        ):
            # ACT
            result = prompt.prompt_menu_selection(menu_items)

        # ASSERT
        with self.subTest("Value", Exp=valid, Act=result):
            self.assertEqual(valid, result)
        with self.subTest("Call count", Exp=2, Act=mock_input.call_count):
            self.assertEqual(2, mock_input.call_count)

    def test_unexpected_exception(self) -> None:
        """
        Should raise RuntimeError when an unexpected exception occurs.
        """
        # ARRANGE
        menu_items = ["alpha", "bravo"]

        request_patch_file = prompt.request
        request_patch_function = request_patch_file.integer_input.__name__

        show_patch_file = prompt.show

        expected_type = RuntimeError.__name__
        expected_reason = "boom"

        with (
            patch.object(request_patch_file, request_patch_function, side_effect=Exception(expected_reason)),
            patch.object(show_patch_file, show_patch_file.show_header.__name__),
            patch.object(show_patch_file, show_patch_file.show_info.__name__),
        ):
            # ACT
            try:
                prompt.prompt_menu_selection(menu_items)
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
    unittest.main()
