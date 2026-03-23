"""
Validate initialization and end-to-end workflow behavior of a controller that processes structured spreadsheet data.

This module verifies that the controller initializes with a clean default state and that a full execution path correctly orchestrates external dependencies, updates internal state, and handles error propagation when a dependency fails.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__clean_bom.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- External dependencies are fully mocked using patching to simulate user input, file I/O, parsing, transformation, and export steps.
	- No real files or directories are created; all inputs such as folder paths, filenames, and sheet data are synthetic.
	- Cleanup is implicit as mocks are scoped to context managers and automatically reverted after each test.

Dependencies:
	- Python 3.10+
	- Standard Library: unittest, unittest.mock

Notes:
	- The tests assert only state changes and outputs that are explicitly set or returned during execution, avoiding assumptions about underlying implementation.
	- Workflow execution is validated through controlled mock return values to ensure deterministic behavior.
	- Error handling is verified by forcing a dependency to raise an exception and asserting that a runtime error with a non-empty message is propagated.
	- The module relies entirely on mocked integrations, so it does not validate real filesystem, spreadsheet parsing, or data transformation behavior.

License:
	Internal Use Only
"""

import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.controllers import _clean_bom as cb


class TestCleanBomController(unittest.TestCase):
    """
    Unit tests for CleanBomController class.
    """
    def test_init(self) -> None:
        """
        Should initialize all attributes to their default state.
        """
        # ARRANGE
        patch_file = cb.base.BaseController
        patch_function = patch_file.__init__.__name__

        # ACT
        with patch.object(patch_file, patch_function, return_value=None):
            controller = cb.CleanBomController()

        # ASSERT
        with self.subTest("Instance type"):
            self.assertIsInstance(controller, cb.CleanBomController)

        with self.subTest("Source attributes"):
            self.assertIsNone(controller.source_folder)
            self.assertIsNone(controller.source_file)

        with self.subTest("Destination attributes"):
            self.assertIsNone(controller.destination_folder)
            self.assertIsNone(controller.destination_file)

        with self.subTest("Pipeline state"):
            self.assertIsNone(controller.raw_sheets)
            self.assertIsNone(controller.parsed_bom)
            self.assertIsNone(controller.cleaned_bom)
            self.assertIsNone(controller.fixed_bom)
            self.assertIsNone(controller.canonical_bom)
            self.assertIsNone(controller.output_sheets)

        with self.subTest("Logs"):
            self.assertIsNone(controller.cleaner_log)
            self.assertIsNone(controller.fixer_log)
            self.assertIsNone(controller.checker_log)

        with self.subTest("Template type"):
            self.assertIsInstance(controller.v3_bom_template, cb.pd.DataFrame)

    def test_happy_path(self) -> None:
        """
        Should execute the workflow and populate controller state.
        """
        # ARRANGE
        controller = cb.CleanBomController()

        patch_menu = cb.menu
        patch_importer = cb.importer
        patch_parser = cb.parser
        patch_cleaner = cb.cleaner
        patch_fixer = cb.fixer
        patch_checker = cb.checker
        patch_mapper = cb.mapper
        patch_transformer = cb.transformer
        patch_exporter = cb.exporter

        with patch.object(patch_menu, patch_menu.folder_selector.__name__, side_effect=["C:\\Code", "C:\\Code"]), \
             patch.object(patch_menu, patch_menu.file_selector.__name__, return_value="file.xlsx"), \
             patch.object(patch_importer, patch_importer.read_excel_as_dict.__name__, return_value={"S": {}}), \
             patch.object(patch_parser, patch_parser.is_v3_bom.__name__, return_value=True), \
             patch.object(patch_parser, patch_parser.parse_v3_bom.__name__, return_value={}), \
             patch.object(patch_cleaner, patch_cleaner.clean_v3_bom.__name__, return_value=({}, ("clean",))), \
             patch.object(patch_fixer, patch_fixer.fix_v3_bom.__name__, return_value=({}, ("fix",))), \
             patch.object(patch_checker, patch_checker.check_v3_bom.__name__, return_value=("check",)), \
             patch.object(patch_mapper, patch_mapper.map_v3_to_canonical_bom.__name__, return_value={}), \
             patch.object(patch_importer, patch_importer.load_version3_bom_template.__name__, return_value={}), \
             patch.object(patch_transformer, patch_transformer.canonical_to_v3_template_sheets.__name__, return_value={"S": {}}), \
             patch.object(patch_exporter, patch_exporter.build_checker_log_filename.__name__, return_value="out.xlsx"), \
             patch.object(patch_exporter, patch_exporter.write_excel_sheets.__name__, return_value=None):

            # ACT
            result = controller.run() # noqa

        # ASSERT
        with self.subTest("Return type"):
            self.assertIsNone(result)

        with self.subTest("Source and destination state"):
            self.assertEqual(controller.source_folder, "C:\\Code")
            self.assertEqual(controller.destination_folder, "C:\\Code")
            self.assertEqual(controller.source_file, "file.xlsx")
            self.assertEqual(controller.destination_file, "out.xlsx")

        with self.subTest("Logs types"):
            self.assertIsInstance(controller.cleaner_log, tuple)
            self.assertIsInstance(controller.fixer_log, tuple)
            self.assertIsInstance(controller.checker_log, tuple)

        with self.subTest("Output sheets type"):
            self.assertIsInstance(controller.output_sheets, dict)

    def test_raise(self) -> None:
        """
        Should raise RuntimeError when a dependency fails.
        """
        # ARRANGE
        controller = cb.CleanBomController()

        patch_file = cb.menu
        patch_function = patch_file.folder_selector.__name__

        expected_type = RuntimeError.__name__
        expected_reason = "failure"

        # ACT
        try:
            with patch.object(patch_file, patch_function, side_effect=Exception("failure")):
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

        actual_message = str(actual)
        with self.subTest("Message contains reason"):
            self.assertIn(expected_reason, actual_message)


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("\n*** ERROR ***")
        print(e)

