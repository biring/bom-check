"""
Validate ANSI-formatted CLI output helpers for correct color usage and formatting.

This module exercises the CLI display helpers by asserting that each function produces the expected ANSI-colored output or return value for a given input message. It verifies that printed messages include the correct color codes and reset sequences, and that prompt generation returns a properly formatted string. It also checks that the diagnostic routine emits output without validating specific content.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/cli/test__show.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Static string inputs are defined inline within each test case
	- Output is captured by patching the built-in print function to intercept calls
	- No filesystem or external resources are used and no cleanup is required

Dependencies:
	- Python version: >= 3.9
	- Standard Library: unittest, unittest.mock, builtins
	- External Packages: colorama

Notes:
	- Tests assert exact string equality including ANSI escape sequences provided by the color library
	- Print-based functions are validated via call count and captured arguments to ensure deterministic output
	- The prompt helper is validated via direct return value comparison rather than print interception
	- The diagnostic routine is only checked for producing output, not for specific formatting or completeness

License:
	- Internal Use Only
"""

import builtins
import unittest

from unittest.mock import patch
from colorama import Fore, Style

# noinspection PyProtectedMember
import src.cli._show as show


class TestShowError(unittest.TestCase):
    """
    Unit tests verify error message rendering with red color.
    """

    def test_happy_path(self):
        """
        Should print the message in red with trailing reset.
        """
        # ARRANGE
        msg = "Failure"
        expected = f"{Fore.RED}{msg}{Style.RESET_ALL}"

        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.show_error(msg)

            # ASSERT
            with self.subTest("Call count", Exp=1, Act=mock_print.call_count):
                self.assertEqual(mock_print.call_count, 1)

            actual = mock_print.call_args[0][0]
            with self.subTest("Output match", Exp=expected, Act=actual):
                self.assertEqual(actual, expected)


class TestShowHeader(unittest.TestCase):
    """
    Unit tests verify header message rendering with leading newline and bright white color.
    """

    def test_happy_path(self):
        """
        Should print the message with newline prefix and bright white color.
        """
        # ARRANGE
        msg = "Header"
        expected = f"\n{Fore.LIGHTWHITE_EX}{msg}{Style.RESET_ALL}"

        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.show_header(msg)

            # ASSERT
            with self.subTest("Call count", Exp=1, Act=mock_print.call_count):
                self.assertEqual(mock_print.call_count, 1)

            actual = mock_print.call_args[0][0]
            with self.subTest("Output match", Exp=expected, Act=actual):
                self.assertEqual(actual, expected)


class TestShowInfo(unittest.TestCase):
    """
    Unit tests verify informational message rendering with reset styling.
    """

    def test_happy_path(self):
        """
        Should print the message wrapped with reset styling.
        """
        # ARRANGE
        msg = "Info"
        expected = f"{Style.RESET_ALL}{msg}{Style.RESET_ALL}"

        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.show_info(msg)

            # ASSERT
            with self.subTest("Call count", Exp=1, Act=mock_print.call_count):
                self.assertEqual(mock_print.call_count, 1)

            actual = mock_print.call_args[0][0]
            with self.subTest("Output match", Exp=expected, Act=actual):
                self.assertEqual(actual, expected)


class TestShowLog(unittest.TestCase):
    """
    Unit tests verify log message rendering with gray color.
    """

    def test_happy_path(self):
        """
        Should print the message in light black with trailing reset.
        """
        # ARRANGE
        msg = "Log"
        expected = f"{Fore.LIGHTBLACK_EX}{msg}{Style.RESET_ALL}"

        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.show_log(msg)

            # ASSERT
            with self.subTest("Call count", Exp=1, Act=mock_print.call_count):
                self.assertEqual(mock_print.call_count, 1)

            actual = mock_print.call_args[0][0]
            with self.subTest("Output match", Exp=expected, Act=actual):
                self.assertEqual(actual, expected)


class TestShowPrompt(unittest.TestCase):
    """
    Unit tests verify prompt string formatting in cyan.
    """

    def test_happy_path(self):
        """
        Should return the prompt string wrapped in cyan with trailing reset.
        """
        # ARRANGE
        msg = "Enter:"
        expected = f"{Fore.CYAN}{msg}{Style.RESET_ALL}"

        # ACT
        result = show.show_prompt(msg)

        # ASSERT
        with self.subTest("Type", Exp=str, Act=type(result)):
            self.assertIsInstance(result, str)

        with self.subTest("Output match", Exp=expected, Act=result):
            self.assertEqual(result, expected)


class TestShowSuccess(unittest.TestCase):
    """
    Unit tests verify success message rendering with green color.
    """

    def test_happy_path(self):
        """
        Should print the message in green with trailing reset.
        """
        # ARRANGE
        msg = "Success"
        expected = f"{Fore.GREEN}{msg}{Style.RESET_ALL}"

        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.show_success(msg)
            actual = mock_print.call_args[0][0]

            # ASSERT
            with self.subTest("Call count", Exp=1, Act=mock_print.call_count):
                self.assertEqual(mock_print.call_count, 1)

            with self.subTest("Output match", Exp=expected, Act=actual):
                self.assertEqual(actual, expected)


class TestShowWarning(unittest.TestCase):
    """
    Unit tests verify warning message rendering with yellow color.
    """

    def test_happy_path(self):
        """
        Should print the message in yellow with trailing reset.
        """
        # ARRANGE
        msg = "Warning"
        expected = f"{Fore.YELLOW}{msg}{Style.RESET_ALL}"

        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.show_warning(msg)
            actual = mock_print.call_args[0][0]

            # ASSERT
            with self.subTest("Call count", Exp=1, Act=mock_print.call_count):
                self.assertEqual(mock_print.call_count, 1)

            with self.subTest("Output match", Exp=expected, Act=actual):
                self.assertEqual(actual, expected)


class TestTestColors(unittest.TestCase):
    """
    Unit tests verify diagnostic color test routine produces output.
    """

    def test_happy_path(self):
        """
        Should execute and produce multiple print calls.
        """
        # ARRANGE
        patch_file = builtins
        patch_function = patch_file.print.__name__

        with patch.object(patch_file, patch_function) as mock_print:
            # ACT
            show.test_colors()

            # ASSERT
            with self.subTest("Print calls exist", Exp=True, Act=mock_print.call_count > 0):
                self.assertTrue(mock_print.call_count > 0)


if __name__ == "__main__":
    unittest.main()
