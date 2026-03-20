"""
Validate controller initialization and end-to-end workflow execution for a BOM checking process.

This module contains unit tests that verify correct default state after controller initialization and validate the orchestration of a multistep workflow that includes folder and file selection, data import, parsing, checking, and exporting results. The tests assert that expected attributes are populated during execution and that failures in the workflow are surfaced as runtime errors with meaningful messages.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__check_bom.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses mocking to simulate external dependencies including menu interactions, file import, parsing, checking, and export operations.
	- Employs MagicMock instances to represent intermediate data structures and configuration storage.
	- No real filesystem or network operations are performed; all I/O is stubbed.
	- Test state is initialized manually for execution flow tests to bypass constructor behavior.

Dependencies:
	- Python 3.8+
	- Standard Library: unittest, unittest.mock

Notes:
	- Tests are deterministic due to full isolation of external dependencies via patching.
	- Workflow validation focuses on attribute assignment and execution flow rather than underlying data correctness.
	- Error handling test confirms that exceptions during early workflow stages are propagated as runtime errors with preserved context.
	- Initialization test bypasses base initialization side effects to isolate attribute defaults.

License:
	Internal Use Only
"""

import unittest
from unittest.mock import patch, MagicMock

# noinspection PyProtectedMember
from src.controllers import _check_bom as cb


class TestCheckBomControllerInit(unittest.TestCase):
    """
    Unit tests verifying initialization establishes default controller state.
    """

    def test_happy_path(self) -> None:
        """
        Should initialize all attributes to None and call base initializer.
        """
        # ARRANGE
        patch_file = cb.base.BaseController
        patch_function = patch_file.__init__.__name__

        with patch.object(patch_file, patch_function, return_value=None):

            # ACT
            controller = cb.CheckBomController()

        # ASSERT
        with self.subTest("Instance type"):
            self.assertIsInstance(controller, cb.CheckBomController)

        with self.subTest("source_folder is None"):
            self.assertIsNone(controller.source_folder)

        with self.subTest("destination_folder is None"):
            self.assertIsNone(controller.destination_folder)

        with self.subTest("source_file is None"):
            self.assertIsNone(controller.source_file)

        with self.subTest("destination_file is None"):
            self.assertIsNone(controller.destination_file)

        with self.subTest("raw_bom is None"):
            self.assertIsNone(controller.raw_bom)

        with self.subTest("parsed_model is None"):
            self.assertIsNone(controller.parsed_model)

        with self.subTest("checkers_log is None"):
            self.assertIsNone(controller.checkers_log)



class TestCheckBomControllerRun(unittest.TestCase):
    """
    Unit tests verifying run orchestrates the BOM validation workflow.
    """

    def setUp(self) -> None:
        # Minimal controller with required base attributes stubbed
        self.controller = cb.CheckBomController.__new__(cb.CheckBomController)
        self.controller.temp_settings_cache = MagicMock()
        self.controller.temp_setting_keys = MagicMock()
        self.controller.temp_setting_keys.SOURCE_FILES_FOLDER = "source_key"
        self.controller.temp_setting_keys.DESTINATION_FILES_FOLDER = "dest_key"

    def test_happy_path(self) -> None:
        """
        Should execute workflow and complete without error.
        """
        # ARRANGE
        self.controller.temp_settings_cache.get_value.side_effect = ["src_folder", "dst_folder"]

        patch_menu = cb.menu
        patch_importer = cb.importer
        patch_parser = cb.parser
        patch_checker = cb.checker
        patch_exporter = cb.exporter

        with patch.object(patch_menu, patch_menu.folder_selector.__name__, side_effect=["src_folder", "dst_folder"]), \
             patch.object(patch_menu, patch_menu.file_selector.__name__, return_value="file.xlsx"), \
             patch.object(patch_importer, patch_importer.read_excel_as_dict.__name__, return_value={"Sheet1": MagicMock()}), \
             patch.object(patch_parser, patch_parser.parse_v3_bom.__name__, return_value=MagicMock()), \
             patch.object(patch_checker, patch_checker.check_v3_bom.__name__, return_value=("a|b", "c|d")), \
             patch.object(patch_exporter, patch_exporter.build_checker_log_filename.__name__, return_value="out.txt"), \
             patch.object(patch_exporter, patch_exporter.write_text_file_lines.__name__, return_value=None), \
             patch.object(patch_exporter, patch_exporter.write_excel_sheets.__name__, return_value=None):

            # ACT
            result = self.controller.run() # noqa

        # ASSERT
        with self.subTest("Return type"):
            self.assertIsNone(result)

        with self.subTest("source_folder set"):
            self.assertEqual(self.controller.source_folder, "src_folder")

        with self.subTest("destination_folder set"):
            self.assertEqual(self.controller.destination_folder, "dst_folder")

        with self.subTest("source_file set"):
            self.assertEqual(self.controller.source_file, "file.xlsx")

        with self.subTest("destination_file set"):
            self.assertEqual(self.controller.destination_file, "out.txt")

        with self.subTest("checkers_log type"):
            self.assertIsInstance(self.controller.checkers_log, tuple)

    def test_exception_during_workflow(self) -> None:
        """
        Should raise RuntimeError when any step fails.
        """
        # ARRANGE
        patch_menu = cb.menu
        expected_type = RuntimeError.__name__
        expected_reason = "failure"

        with patch.object(
            patch_menu,
            patch_menu.folder_selector.__name__,
            side_effect=Exception(expected_reason),
        ):

            # ACT
            try:
                self.controller.run()
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



if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("\n*** ERROR ***")
        print(e)
