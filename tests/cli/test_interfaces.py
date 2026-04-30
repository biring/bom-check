"""
Smoke tests for the public command-line interface surface.

This module validates basic happy-path interactions for user prompts and display helpers by asserting returned values and minimal I/O behavior. It verifies that prompting functions delegate to input once and return the provided value, and that display helpers call print once and include the provided message without asserting formatting details.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/cli/test_interfaces.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses unittest.mock.patch to replace builtins.input with predefined return values to simulate user input.
	- Uses unittest.mock.patch to replace builtins.print to capture and inspect calls without writing to the console.
	- No filesystem or external resources are used; no explicit cleanup is required beyond context manager scope.

Dependencies:
	- Python >= 3.10
	- Standard Library: unittest, unittest.mock

Notes:
	- Tests assert delegation to input and print via call counts and do not validate output formatting or side effects beyond message inclusion.
	- Input prompts are checked for containing the provided prompt text without enforcing exact equality to avoid brittleness.
	- Display helpers are expected to return None and emit exactly one print call containing the input message.
	- Tests are deterministic and hermetic due to patching of I/O functions.

License:
	- Internal Use Only
"""

import unittest
from unittest.mock import patch

from src.cli import interfaces as cli


class TestInterfaces(unittest.TestCase):
    """
    Unit tests for the `interfaces.py` public API façade.
    """

    def test_prompt_for_string_value(self):
        """
        Should return the exact string entered by the user and call input() once.
        """
        # ARRANGE
        prompt_text = "Enter board name: "
        expected = "Main PCBA"

        # Patch builtins.input to simulate a single, valid user entry.
        with patch("builtins.input", return_value=expected) as mock_input:
            # ACT
            result = cli.prompt_for_string_value(prompt_text)

            # ASSERT
            with self.subTest("Value", Out=result, Exp=expected):
                self.assertEqual(result, expected)

            with self.subTest("Calls", Out=mock_input.call_count, Exp=1):
                self.assertEqual(mock_input.call_count, 1)

            # Optional: verify the prompt text was passed to input() (non-brittle)
            called_with_prompt = mock_input.call_args[0][0] if mock_input.call_args else ""
            with self.subTest("Prompt",
                              Out=called_with_prompt, Contains=prompt_text):
                self.assertIn(prompt_text, called_with_prompt)

    def test_prompt_menu_selection(self):
        """
        Should return the user's choice (valid option) and call input() once.
        """
        # ARRANGE
        menu_options = ["Scan", "Parse", "Report"]
        selection = 2

        with (
            patch("builtins.input", return_value=selection) as mock_input,
            patch("builtins.print"),
        ):
            # ACT
            result = cli.prompt_menu_selection(menu_options)

            # ASSERT
            with self.subTest("Value", Out=result, Exp=selection):
                self.assertEqual(result, selection)

            with self.subTest("Calls", Out=mock_input.call_count, Exp=1):
                self.assertEqual(mock_input.call_count, 1)

    def test_show_functions(self):
        """
        Should call builtins print exactly once and include the input message.
        """
        # ARRANGE
        cases = [
            (cli.show_header, "BOM Buddy — Start"),
            (cli.show_info, "Scanning worksheets..."),
            (cli.show_warning, "No Item rows detected; using fallback."),
            (cli.show_error, "Failed to parse header row."),
            (cli.show_success, "Parse complete."),
            (cli.show_log, "Rows=128, Items=117, Skipped=11"),
        ]

        for func, message in cases:
            # Patch print so we can observe calls without touching the console.
            with patch("builtins.print") as mock_print:
                # ACT
                result = func(message)

                # ASSERT
                # Return value (these are UI helpers; expected to return None)
                with self.subTest(Func=func.__name__, Field="Value", Out=result, Exp=None):
                    self.assertIsNone(result)

                # Ensure print was called once
                with self.subTest(Func=func.__name__, Field="Calls",
                                  Out=mock_print.call_count, Exp=1):
                    self.assertEqual(mock_print.call_count, 1)

                # Verify printed text contains the user's message
                printed_arg = mock_print.call_args[0][0] if mock_print.call_args else ""
                with self.subTest(Func=func.__name__, Field="Message",
                                  Out=printed_arg, Contains=message):
                    self.assertIn(message, printed_arg)


if __name__ == "__main__":
    unittest.main()
