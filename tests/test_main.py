"""
Validate application entry point behavior, including menu routing, title display, and main loop control.

This module tests the CLI entry point orchestration by verifying how the application initializes, presents its menu, routes user selections to actions, and terminates under various conditions. It exercises normal execution, graceful exit, invalid selections, and error handling, along with ensuring that version and build information are displayed and that the main loop responds correctly to control signals.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/test_main.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses mocking to simulate menu construction, user input, and action execution without invoking real dependencies
	- Replaces standard input and output functions to control and observe CLI interactions
	- Configures mock return values and side effects to drive specific control flow paths
	- All test state is transient and managed in-memory with no filesystem interaction

Dependencies:
	- Python version: >= 3.10
	- Standard Library: builtins, unittest, unittest.mock

Notes:
	- Tests isolate entry point logic by patching external dependencies such as menu providers and CLI handlers
	- Control flow is validated through return values and mock interaction assertions rather than full output inspection
	- Error and interrupt scenarios are simulated via injected exceptions to ensure graceful handling
	- Assumes consistent alignment between menu options and corresponding executable actions

License:
	- Internal Use Only
"""

import builtins
import unittest
from unittest.mock import patch, MagicMock

from src import main


class TestRunMenu(unittest.TestCase):
    """
    Unit tests verifying menu selection handling and execution routing.
    """

    def test_happy_path(self) -> None:
        """
        Should execute corresponding action for valid selections.
        """
        # ARRANGE
        patch_file_controller = main.controller
        patch_func_build = patch_file_controller.build_controller_menu.__name__

        patch_file_cli = main.cli
        patch_func_prompt = patch_file_cli.prompt_menu_selection.__name__

        mock_action = MagicMock()
        mock_action_instance = MagicMock()
        mock_action.return_value = mock_action_instance

        # ACT
        with (
            patch.object(
                patch_file_controller,
                patch_func_build,
                return_value=(["Mock Action"], [mock_action])
            ),
            patch.object(patch_file_cli, patch_func_prompt, return_value=4)
        ):
            result = main.run_menu()

        # ASSERT
        with self.subTest("Action executed", Exp=True, Act=result):
            self.assertTrue(result)

        with self.subTest("Action class called"):
            mock_action.assert_called_once()

        with self.subTest("Action run called"):
            mock_action_instance.run.assert_called_once()

    def test_exit_selection(self) -> None:
        """
        Should return None when exit option is selected.
        """
        # ARRANGE
        patch_file_controller = main.controller
        patch_func_build = patch_file_controller.build_controller_menu.__name__

        # ACT
        with (
            patch.object(patch_file_controller, patch_func_build, return_value=([], [])),
            patch.object(main.cli, "prompt_menu_selection", return_value=0),
        ):
            result = main.run_menu()

        # ASSERT
        with self.subTest("Exit returns", Exp=None, Act=result):
            self.assertIsNone(result)

    def test_invalid_selection(self) -> None:
        """
        Should return True when selection is out of range but handled.
        """
        # ARRANGE
        patch_file_controller = main.controller
        patch_func_build = patch_file_controller.build_controller_menu.__name__

        patch_file = builtins
        patch_function = patch_file.print.__name__

        # ACT
        with (
            patch.object(patch_file_controller, patch_func_build, return_value=([], [])),
            patch.object(main.cli, "prompt_menu_selection", return_value=999),
            patch.object(patch_file, patch_function),
        ):
            result = main.run_menu()

        # ASSERT
        with self.subTest("Invalid selection returns", Exp=True, Act=result):
            self.assertTrue(result)

    def test_keyboard_interrupt(self) -> None:
        """
        Should return False when KeyboardInterrupt occurs.
        """
        # ARRANGE
        patch_file_controller = main.controller
        patch_func_build = patch_file_controller.build_controller_menu.__name__

        patch_file = builtins
        patch_function = patch_file.print.__name__

        # ACT
        with (
            patch.object(patch_file_controller, patch_func_build, return_value=([], [])),
            patch.object(main.cli, "prompt_menu_selection", side_effect=KeyboardInterrupt),
            patch.object(patch_file, patch_function),
        ):
            result = main.run_menu()

        # ASSERT
        with self.subTest("KeyboardInterrupt returns", Exp=False, Act=result):
            self.assertFalse(result)

    def test_unexpected_exception(self) -> None:
        """
        Should return False when unexpected exception occurs inside menu handling.
        """
        # ARRANGE
        patch_file_controller = main.controller
        patch_func_build = patch_file_controller.build_controller_menu.__name__

        patch_file = builtins
        patch_function = patch_file.print.__name__

        # ACT
        with (
            patch.object(patch_file_controller, patch_func_build, return_value=([], [])),
            patch.object(main.cli, "prompt_menu_selection", side_effect=Exception("boom")),
            patch.object(patch_file, patch_function),
        ):
            result = main.run_menu()

        # ASSERT
        with self.subTest("Exception returns False", Exp=False, Act=result):
            self.assertFalse(result)


class TestShowTitle(unittest.TestCase):
    """
    Unit tests verifying version and build information display.
    """

    def test_happy_path(self) -> None:
        """
        Should print version and build information.
        """
        # ARRANGE
        patch_file_version = main.version
        patch_file_print = main

        patch_func_print = print.__name__

        # ACT
        with (
            patch.object(patch_file_version, "__version__", "1.0.0"),
            patch.object(patch_file_version, "__build__", "abc123"),
            patch.object(patch_file_print, patch_func_print) as mock_print,
        ):
            result = main.show_title()

        # ASSERT
        with self.subTest("Return is None", Exp=None, Act=result):
            self.assertIsNone(result)

        with self.subTest("Print called twice"):
            self.assertEqual(mock_print.call_count, 2)


class TestMain(unittest.TestCase):
    """
    Unit tests verifying main loop control and termination behavior.
    """

    def test_happy_path(self) -> None:
        """
        Should continue loop on True and exit on None.
        """
        # ARRANGE
        patch_file = main

        patch_func_show = patch_file.show_title.__name__
        patch_func_run = patch_file.run_menu.__name__

        # ACT
        with (
            patch.object(patch_file, patch_func_show),
            patch.object(patch_file, patch_func_run, side_effect=[True, None])
        ):
            result = main.run_application()

        # ASSERT
        with self.subTest("Return is None", Exp=None, Act=result):
            self.assertIsNone(result)

    def test_error_path(self) -> None:
        """
        Should prompt for input and exit when run_menu returns False.
        """
        # ARRANGE
        patch_file = main

        patch_func_show = patch_file.show_title.__name__
        patch_func_run = patch_file.run_menu.__name__
        patch_func_input = input.__name__

        # ACT
        with (
            patch.object(patch_file, patch_func_show),
            patch.object(patch_file, patch_func_run, return_value=False),
            patch.object(patch_file, patch_func_input, return_value="")
        ):
            result = main.run_application()

        # ASSERT
        with self.subTest("Return is None", Exp=None, Act=result):
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
