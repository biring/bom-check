"""
Validate controller initialization and end-to-end BOM cleaning workflow behavior.

This module tests that the controller initializes with a clean default state and that executing the workflow processes spreadsheet inputs, produces expected outputs, writes log files, and handles failure scenarios by raising a runtime error with a propagated message.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/controllers/test__clean_bom.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Temporary directories are created using filesystem utilities to store input and output files during tests.
	- Excel files are generated from in-memory tabular data and written to disk for realistic workflow execution.
	- Synthetic datasets are used to represent both clean and intentionally modified spreadsheet inputs.
	- External interactions such as user prompts and configuration retrieval are mocked to control execution flow.
	- Cleanup is performed by removing temporary directories after each test.

Dependencies:
	- Python 3.10+
	- Standard Library: unittest, unittest.mock, temp file, shutil, os, io

Notes:
	- Tests verify only observable state changes, returned data, and filesystem side effects such as file creation.
	- Workflow behavior is exercised end-to-end using real file I/O combined with selective mocking for user interaction.
	- Deterministic behavior is enforced through controlled inputs and patched dependencies.
	- Error handling is validated by simulating a dependency failure and asserting that a runtime error is raised with a non-empty message containing the original cause.

License:
	Internal Use Only
"""

import io
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

# noinspection PyProtectedMember
from src.controllers import _clean_bom as cb
from src.utils import excel_io as eio
from tests.fixtures import v3_df as bfx

class TestCleanBomController(unittest.TestCase):
    """
    Unit tests verifying CleanBomController initialization and workflow execution.
    """

    def setUp(self) -> None:
        """
        Create temporary directory for test data.
        """
        self.test_folder_path = tempfile.mkdtemp(prefix="bom_clean_test_")
        self.test_file_name = "sample_bom"
        self.test_file_path = os.path.join(self.test_folder_path, self.test_file_name + ".xlsx")

    def tearDown(self) -> None:
        """
        Clean up temporary directory.
        """
        if os.path.exists(self.test_folder_path):
            shutil.rmtree(self.test_folder_path)

    def file_name_has_tag(self, tag: str) -> bool:
        for file_name in os.listdir(self.test_folder_path):
            if tag in file_name:
                return True
        return False


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
        clean_bom_sheets = bfx.BOM_B_DATAFRAME
        eio.write_sheets_to_excel(
            file_path=self.test_file_path,
            frames_by_sheet=clean_bom_sheets,
            overwrite=True,
            add_header_to_top_row=False,
        )

        controller = cb.CleanBomController()

        patch_cache = controller.temp_settings_cache
        patch_menu = cb.menu

        with (
            patch.object(
                target=patch_cache,
                attribute=patch_cache.get_value.__name__,
                return_value=self.test_folder_path
            ),
            patch.object(
                target=patch_menu,
                attribute=patch_menu.folder_selector.__name__,
                return_value=self.test_folder_path
            ),
            patch.object(
                target=patch_menu,
                attribute=patch_menu.file_selector.__name__,
                return_value=self.test_file_name + ".xlsx"
            ),
            patch("builtins.print"),
        ):

            # ACT
            actual = controller.run() # noqa


        # ASSERT
        with self.subTest("Empty checker log"):
            self.assertEqual(controller.checker_log, cb._EMPTY_CHECKER_LOG_MESSAGE)

        with self.subTest("Checkers log file write"):
            self.assertTrue(self.file_name_has_tag(cb.exporter.LogTypes.CHECKER.value))

        with self.subTest("Empty fixer log"):
            self.assertEqual(controller.fixer_log, cb._EMPTY_FIXER_LOG_MESSAGE)

        with self.subTest("Fixer log file write"):
            self.assertTrue(self.file_name_has_tag(cb.exporter.LogTypes.FIXER.value))

        with self.subTest("Empty cleaner log"):
            self.assertEqual(controller.cleaner_log, cb._EMPTY_CLEANER_LOG_MESSAGE)

        with self.subTest("Cleaner log file write"):
            self.assertTrue(self.file_name_has_tag(cb.exporter.LogTypes.CLEANER.value))

        with self.subTest("Bom file write"):
            self.assertTrue(self.file_name_has_tag("BB200"))

        # Verify bom
        expected = clean_bom_sheets # noqa
        actual = controller.output_sheets

        with self.subTest("Bom count", Exp=len(expected), Act=len(actual)):
            self.assertEqual(len(expected), len(actual))

        for ((expected_name, expected_df), (actual_name, actual_df)) in zip(expected.items(), actual.items()):
            with self.subTest(f"Sheet: {expected_name}"):
                self.assertEqual(expected_name, actual_name)

            expected_df_as_lists = expected_df.fillna("").astype(str).values.tolist()
            actual_df_as_lists = actual_df.fillna("").astype(str).values.tolist()

            with self.subTest(f"Board: {expected_name}"):
                self.assertEqual(expected_df_as_lists, actual_df_as_lists)

    def test_cleaning(self) -> None:
        """
        Should clean BOM data and generate non-empty logs.
        """
        # ARRANGE
        clean_bom_sheets = bfx.BOM_A_DATAFRAME

        replacements = {
            r"\b2025-01-12\b": "TBD", # will require manual correction in the header
            r"\bQFN-8\b": "*QFN-8*", # will require manual correction in the table
            r"\b2\.4\b": "2.5", # will be autocorrected in the header
            r"R1,R2": "R1 , R2", # will be autocorrected in the table
        }

        dirty_bom_sheets = {
            name: df.replace(replacements, regex=True)
            for name, df in clean_bom_sheets.items()
        }

        eio.write_sheets_to_excel(
            file_path=self.test_file_path,
            frames_by_sheet=dirty_bom_sheets,
            overwrite=True,
            add_header_to_top_row=False,
        )

        controller = cb.CleanBomController()

        patch_cache = controller.temp_settings_cache
        patch_menu = cb.menu

        with (
            patch(
                target="sys.stdout",
                new=io.StringIO()
            ),
            patch(
                target="builtins.input",
                side_effect=["QFN-8", "2025-01-12"]
            ) as mock_input,
            patch.object(
                target=patch_cache,
                attribute=patch_cache.get_value.__name__,
                return_value=self.test_folder_path
            ),
            patch.object(
                target=patch_menu,
                attribute=patch_menu.folder_selector.__name__,
                return_value=self.test_folder_path
            ),
            patch.object(
                target=patch_menu,
                attribute=patch_menu.file_selector.__name__,
                return_value=self.test_file_name + ".xlsx"
            ),
        ):

            # ACT
            actual = controller.run() # noqa
            print(mock_input.call_args_list)


        # ASSERT
        with self.subTest("Two manual correction promotes"):
            self.assertEqual(mock_input.call_count, 2)

        with self.subTest("Cleaner log size"):
            self.assertEqual(len(controller.cleaner_log), 1) # Only Ref des is logged

        with self.subTest("Cleaner log file write"):
            self.assertTrue(self.file_name_has_tag(cb.exporter.LogTypes.CLEANER.value))

        with self.subTest("Fixer log size"):
            self.assertEqual(len(controller.fixer_log), 3) # Other 3 changes are logged here

        with self.subTest("Fixer log file write"):
            self.assertTrue(self.file_name_has_tag(cb.exporter.LogTypes.FIXER.value))

        with self.subTest("Checker log is empty post cleaning"):
            self.assertEqual(controller.checker_log, cb._EMPTY_CHECKER_LOG_MESSAGE)

        with self.subTest("Checkers log file write"):
            self.assertTrue(self.file_name_has_tag(cb.exporter.LogTypes.CHECKER.value))

        with self.subTest("Bom file write"):
            self.assertTrue(self.file_name_has_tag("AB100"))

        # Verify bom
        expected = clean_bom_sheets # noqa
        actual = controller.output_sheets

        with self.subTest("Bom count", Exp=len(expected), Act=len(actual)):
            self.assertEqual(len(expected), len(actual))

        for ((expected_name, expected_df), (actual_name, actual_df)) in zip(expected.items(), actual.items()):
            with self.subTest(f"Sheet: {expected_name}"):
                self.assertEqual(expected_name, actual_name)

            expected_df_as_lists = expected_df.fillna("").astype(str).values.tolist()
            actual_df_as_lists = actual_df.fillna("").astype(str).values.tolist()

            with self.subTest(f"Board: {expected_name}"):
                self.assertEqual(expected_df_as_lists, actual_df_as_lists)


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
            with patch.object(patch_file, patch_function, side_effect=Exception(expected_reason)):
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

        actual_message = str(actual)
        with self.subTest("Message contains reason"):
            self.assertIn(expected_reason, actual_message)


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print("\n*** ERROR ***")
        print(e)

