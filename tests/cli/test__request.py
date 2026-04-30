"""
Unit tests for interactive console input handling behaviors.

This module verifies that user input helpers correctly return raw string input, normalize interruption and end-of-file exceptions with non-empty messages, parse integer input through a delegated parser, and retry on invalid numeric input until valid data is received.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/cli/test__request.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses unittest.mock.patch to replace standard input calls with controlled return values and exceptions.
	- Simulates sequential user inputs via side_effect to test retry behavior.
	- No filesystem or external resources are used; all inputs are in-memory.
	- No explicit cleanup required due to context-managed patching.

Dependencies:
	- Python >= 3.9
	- Standard Library: builtins, unittest, unittest.mock

Notes:
	- Tests are non-interactive and avoid real stdin usage by mocking input calls.
	- Exception assertions verify type and presence of a non-empty message rather than exact message content.
	- Integer input behavior is validated through mocked parsing outcomes to isolate control flow.
	- Retry logic is exercised deterministically using ordered side effects.

License:
	- Internal Use Only
"""

import builtins
import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
import src.cli._request as request


class TestStringInput(unittest.TestCase):
    """
    Unit tests verifying string_input returns user-provided input and normalizes input exceptions.
    """

    def test_happy_path(self) -> None:
        """
        Should return the same string provided by input.
        """
        # ARRANGE
        prompt = "Enter value: "
        expected = "sample input"
        patch_file = builtins
        patch_function = patch_file.input.__name__

        with patch.object(patch_file, patch_function, return_value=expected) as mock_input:
            # ACT
            result = request.string_input(prompt)

        # ASSERT
        with self.subTest("Return type", Exp=str, Act=type(result)):
            self.assertIs(type(result), str)
        with self.subTest("Return value", Exp=expected, Act=result):
            self.assertEqual(result, expected)
        with self.subTest("Call count", Out=mock_input.call_count, Exp=1):
            self.assertEqual(mock_input.call_count, 1)

    def test_eof_error(self) -> None:
        """
        Should raise EOFError with a normalized message when input stream closes.
        """
        # ARRANGE
        prompt = "Enter value: "
        patch_file = builtins
        patch_function = patch_file.input.__name__
        expected_type = EOFError.__name__

        with patch.object(patch_file, patch_function, side_effect=EOFError()):
            # ACT
            try:
                request.string_input(prompt)
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

    def test_keyboard_interrupt(self) -> None:
        """
        Should raise KeyboardInterrupt with a normalized message when interrupted.
        """
        # ARRANGE
        prompt = "Enter value: "
        patch_file = builtins
        patch_function = patch_file.input.__name__
        expected_type = KeyboardInterrupt.__name__

        with patch.object(patch_file, patch_function, side_effect=KeyboardInterrupt()):
            # ACT
            try:
                request.string_input(prompt)
                actual = ""
            except BaseException as e:
                actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")


class TestIntegerInput(unittest.TestCase):
    """
    Unit tests verifying integer_input parses valid integers and retries on invalid input until success.
    """

    def test_happy_path(self) -> None:
        """
        Should return parsed integer when input is valid.
        """
        # ARRANGE
        prompt = "Enter number: "
        user_input = "42"
        expected = 42

        patch_file_input = request
        patch_function_input = patch_file_input.string_input.__name__

        patch_file_parser = request.utils.parser
        patch_function_parser = patch_file_parser.parse_to_integer.__name__

        with (
            patch.object(patch_file_input, patch_function_input, return_value=user_input) as mock_input,
            patch.object(patch_file_parser, patch_function_parser, return_value=expected),
        ):
            # ACT
            result = request.integer_input(prompt)

        # ASSERT
        with self.subTest("Return type", Exp=int, Act=type(result)):
            self.assertIs(type(result), int)
        with self.subTest("Return value", Exp=expected, Act=result):
            self.assertEqual(result, expected)
        with self.subTest("Call count", Out=mock_input.call_count, Exp=1):
            self.assertEqual(mock_input.call_count, 1)

    def test_invalid_then_valid(self) -> None:
        """
        Should retry on invalid input and return parsed integer once valid input is provided.
        """
        # ARRANGE
        prompt = "Enter number: "
        inputs = ["abc", "100"]
        parsed_values = [ValueError(), 100]

        patch_file_input = request
        patch_function_input = patch_file_input.string_input.__name__

        patch_file_parser = request.utils.parser
        patch_function_parser = patch_file_parser.parse_to_integer.__name__

        patch_file_print = builtins
        patch_function_print = patch_file_print.print.__name__

        with (
            patch.object(patch_file_input, patch_function_input, side_effect=inputs),
            patch.object(patch_file_parser, patch_function_parser, side_effect=parsed_values),
            patch.object(patch_file_print, patch_function_print),
        ):
            # ACT
            result = request.integer_input(prompt)

        # ASSERT
        with self.subTest("Return type", Exp=int, Act=type(result)):
            self.assertIs(type(result), int)
        with self.subTest("Return value", Exp=100, Act=result):
            self.assertEqual(result, 100)

    def test_eof_error(self) -> None:
        """
        Should propagate EOFError with a normalized message when input stream closes.
        """
        # ARRANGE
        prompt = "Enter number: "
        patch_file = builtins
        patch_function = patch_file.input.__name__
        expected_type = EOFError.__name__

        with patch.object(patch_file, patch_function, side_effect=EOFError()):
            # ACT
            try:
                request.integer_input(prompt)
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

    def test_keyboard_interrupt(self) -> None:
        """
        Should propagate KeyboardInterrupt with a normalized message when interrupted.
        """
        # ARRANGE
        prompt = "Enter number: "
        patch_file = builtins
        patch_function = patch_file.input.__name__
        expected_type = KeyboardInterrupt.__name__

        with patch.object(patch_file, patch_function, side_effect=KeyboardInterrupt()):
            # ACT
            try:
                request.integer_input(prompt)
                actual = ""
            except BaseException as e:
                actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")


if __name__ == "__main__":
    unittest.main()
