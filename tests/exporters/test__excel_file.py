"""
Unit tests for validating Excel workbook generation from multiple tabular datasets.

This test module exercises the behavior of writing multiple named tabular datasets into a single Excel workbook, focusing on input validation, file overwrite handling, error propagation, and basic round-trip integrity when reading the generated file back into memory.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/exporters/test__excel_file.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- Temporary directories are created per test case using the standard library to isolate filesystem side effects.
	- Excel file paths are constructed within the temporary directory using a configured file extension constant.
	- Real pandas DataFrame instances are used to represent sheet data.
	- Empty placeholder files are created explicitly to simulate pre-existing output files.
	- Mocking is applied to force unexpected write-time exceptions from the Excel I/O layer.
	- Temporary directories are removed during test teardown to ensure cleanup.

Dependencies
	- Python 3.x
	- Standard Library: os, shutil, tempfile, unittest, unittest.mock
	- Third-party: pandas

Notes
	- Tests rely on filesystem access and actual Excel file creation.
	- Error handling is validated by asserting raised RuntimeError types rather than message contents.
	- Round-trip validation relaxes dtype checking to account for pandas Excel read inference.

License
	Internal Use Only
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import pandas.testing as pdt

# noinspection PyProtectedMember
from src.exporters import _excel_file as ef
from src.utils import excel_io


class TestWriteExcelSheets(unittest.TestCase):
    """
    Unit tests to verify writing multiple tabular datasets to an Excel workbook with consistent orchestration.
    """

    def setUp(self) -> None:
        """
        Create a temporary directory for each test case.
        """
        # ARRANGE
        self.folder_path = tempfile.mkdtemp(prefix="bom_check_test_excel_file_")
        self.file_name: str | None = None
        self.file_path: str | None = None
        self.sheets: dict[str, pd.DataFrame] | None = None

    def tearDown(self) -> None:
        """
        Remove the temporary directory after each test case.
        """
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)

    def generate_excel_file_path(self) -> None:
        self.file_path = os.path.join(self.folder_path, self.file_name + excel_io.EXCEL_FILE_TYPE)

    def touch_excel_file(self) -> None:
        with open(self.file_path, "wb") as f:
            f.write(b"")

    def test_happy_path(self) -> None:
        """
        Should write an Excel file to the destination folder for non-empty sheets.
        """
        # ARRANGE
        self.file_name = "output"
        self.generate_excel_file_path()
        self.sheets = {
            "Sheet1": pd.DataFrame([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]),
            "Sheet2": pd.DataFrame([{"sku": "ABC-001", "qty": 10}]),
        }
        expected_exists = True

        # ACT
        ef.write_excel_sheets(
            self.folder_path,
            self.file_name,
            self.sheets,
            overwrite=False,
            top_row_is_header=True,
        )
        actual_exists = os.path.exists(self.file_path)

        # ASSERT
        with self.subTest(Act=actual_exists, Exp=expected_exists):
            self.assertEqual(actual_exists, expected_exists)

    def test_non_dict_sheets(self) -> None:
        """
        Should raise RuntimeError when sheets is not a dict.
        """
        # ARRANGE
        self.file_name = "bad_sheets"
        expected_exc = RuntimeError.__name__
        non_dict_sheets = [("Sheet1", pd.DataFrame([{"a": 1}]))]

        # ACT
        with self.assertRaises(RuntimeError) as ctx:
            ef.write_excel_sheets(
                self.folder_path,
                self.file_name,
                non_dict_sheets,  # type: ignore[arg-type]
            )
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_invalid_sheet_name(self) -> None:
        """
        Should raise RuntimeError when any sheet name is missing or not a string.
        """
        # ARRANGE
        self.file_name = "bad_sheet_name"
        expected_exc = RuntimeError.__name__
        sheets = {
            "": pd.DataFrame([{"a": 1}]),
        }

        # ACT
        with self.assertRaises(RuntimeError) as ctx:
            ef.write_excel_sheets(
                self.folder_path,
                self.file_name,
                sheets,
            )
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_non_dataframe_value(self) -> None:
        """
        Should raise RuntimeError when any sheet value is not a pandas DataFrame.
        """
        # ARRANGE
        self.file_name = "bad_sheet_value"
        expected_exc = RuntimeError.__name__
        sheets = {
            "Sheet1": "not-a-dataframe",
        }

        # ACT
        with self.assertRaises(RuntimeError) as ctx:
            ef.write_excel_sheets(
                self.folder_path,
                self.file_name,
                sheets,  # type: ignore[arg-type]
            )
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_empty_dataframe(self) -> None:
        """
        Should raise RuntimeError when any sheet DataFrame is empty.
        """
        # ARRANGE
        self.file_name = "empty_sheet"
        expected_exc = RuntimeError.__name__
        sheets = {
            "Sheet1": pd.DataFrame(),
        }

        # ACT
        with self.assertRaises(RuntimeError) as ctx:
            ef.write_excel_sheets(
                self.folder_path,
                self.file_name,
                sheets,
            )
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_overwrite_false_existing_file(self) -> None:
        """
        Should raise RuntimeError when overwrite is False and the target file already exists.
        """
        # ARRANGE
        self.file_name = "existing"
        self.generate_excel_file_path()
        self.touch_excel_file()
        expected_exc = RuntimeError.__name__
        sheets = {
            "Sheet1": pd.DataFrame([{"a": 1}]),
        }

        # ACT
        with self.assertRaises(RuntimeError) as ctx:
            ef.write_excel_sheets(
                self.folder_path,
                self.file_name,
                sheets,
                overwrite=False,
                top_row_is_header=True,
            )
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_overwrite_true_existing_file(self) -> None:
        """
        Should overwrite an existing file when overwrite is True.
        """
        # ARRANGE
        self.file_name = "overwrite_me"
        self.generate_excel_file_path()
        self.touch_excel_file()
        sheets = {
            "Sheet1": pd.DataFrame([{"a": 1}]),
        }
        expected_exists = True

        # ACT
        ef.write_excel_sheets(
            self.folder_path,
            self.file_name,
            sheets,
            overwrite=True,
            top_row_is_header=True,
        )
        actual_exists = os.path.exists(self.file_path)

        # ASSERT
        with self.subTest(Act=actual_exists, Exp=expected_exists):
            self.assertEqual(actual_exists, expected_exists)

    def test_unexpected_exception(self) -> None:
        """
        Should raise RuntimeError when an unexpected error occurs during file write.
        """
        # ARRANGE
        self.file_name = "boom"
        expected_exc = RuntimeError.__name__
        sheets = {
            "Sheet1": pd.DataFrame([{"a": 1}]),
        }

        # ACT
        patch_file = ef.excel_io
        patch_function = patch_file.write_sheets_to_excel.__name__
        with patch.object(
                patch_file, patch_function, side_effect=Exception("boom"),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                ef.write_excel_sheets(
                    self.folder_path,
                    self.file_name,
                    sheets,
                    overwrite=True,
                    top_row_is_header=True,
                )
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_round_trip(self) -> None:
        """
        Should write an Excel file and allow reading back equivalent sheet data.
        """
        # ARRANGE
        self.file_name = "round_trip"
        self.generate_excel_file_path()
        self.sheets = {
            "People": pd.DataFrame(
                [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
                columns=["id", "name"],
            ),
            "Inventory": pd.DataFrame(
                [{"sku": "ABC-001", "qty": 10}, {"sku": "XYZ-777", "qty": 0}],
                columns=["sku", "qty"],
            ),
        }

        # ACT
        ef.write_excel_sheets(
            self.folder_path,
            self.file_name,
            self.sheets,
            overwrite=True,
            top_row_is_header=True,
        )
        actual_by_sheet = pd.read_excel(self.file_path, sheet_name=None)

        # ASSERT
        with self.subTest("sheet_names", Act=set(actual_by_sheet.keys()), Exp=set(self.sheets.keys())):
            self.assertEqual(set(actual_by_sheet.keys()), set(self.sheets.keys()))

        for sheet_name, expected_df in self.sheets.items():
            actual_df = actual_by_sheet[sheet_name]
            with self.subTest("dataframe_type", Sheet=sheet_name, Act=type(actual_df), Exp=pd.DataFrame):
                self.assertIsInstance(actual_df, pd.DataFrame)

            # pandas will often infer slightly different dtypes on round-trip; keep equality focused on values/labels.
            with self.subTest("dataframe_values", Sheet=sheet_name):
                pdt.assert_frame_equal(
                    actual_df,
                    expected_df,
                    check_dtype=False,
                    check_like=False,
                )


if __name__ == '__main__':
    unittest.main()
