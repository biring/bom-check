"""
Unit tests for the internal Excel loader helper `read_excel_as_dict`.

This module validates that the loader:
    - Successfully reads a real .xlsx workbook into a dict[str, DataFrame]
    - Preserves sheet names and DataFrame shapes
    - Raises RuntimeError for missing files, wrong extensions, or invalid filenames
    - Ensures filename structure rules (exactly one dot before extension)

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/importers/test__excel_file.py

    # Direct discovery (runs all tests):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, shutil, os
    - External Packages: pandas, openpyxl

Notes:
    - Tests use real temporary Excel files to validate end-to-end behavior.
    - Content validation is intentionally minimal; shape and structure are the contract.
    - Project-root resolution is patched to keep tests hermetic and deterministic.
    - Errors are asserted by exception type, not message text.

License:
    - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

# noinspection PyProtectedMember
from src.importers import _excel_file as excel_file


class TestReadExcelAsDict(unittest.TestCase):
    """
    Unit tests for the `read_excel_as_dict` Excel loader helper.
    """

    def setUp(self):
        """
        Create a temporary folder and a real Excel workbook for testing.
        """
        # ARRANGE (common for tests)
        self.file_name = "sample_workbook.xlsx"
        # Create a temporary directory to hold the test Excel file
        self.temp_dir = tempfile.mkdtemp(prefix="excel_load_test_")

        # Full path to the temporary Excel file
        self.excel_path = os.path.join(self.temp_dir, self.file_name)

        # Build realistic sample DataFrames for multiple sheets.
        sheet1_df = pd.DataFrame(
            {
                "Item": [1, 2, 3],
                "Description": ["Resistor", "Capacitor", "Inductor"],
                "Qty": [10, 20, 30],
                "Price": [1.56, 0.67, 99.89],
            }
        )
        sheet2_df = pd.DataFrame(
            {
                "PartNumber": ["R1", "C1", "L1"],
                "Value": ["10k", "1uF", "10uH"],
            }
        )

        # Store expected sheet data for later comparison in tests
        self.expected_sheets: dict[str, pd.DataFrame] = {
            "BOM": sheet1_df,
            "Details": sheet2_df,
        }

        # Create a real Excel workbook on disk
        with pd.ExcelWriter(self.excel_path) as writer:
            sheet1_df.to_excel(writer, sheet_name="BOM", index=False)
            sheet2_df.to_excel(writer, sheet_name="Details", index=False)

    def tearDown(self):
        """
        Remove the temporary directory and all created files.
        """
        if os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_happy_path(self):
        """
        Should load a valid Excel file and return a dict of DataFrames keyed by sheet name.
        """
        # ARRANGE
        folder_path = self.temp_dir
        file_name = self.file_name
        expected_result = set(self.expected_sheets.keys())

        # ACT
        actual_result = excel_file.read_excel_as_dict(folder_path, file_name)
        actual_sheet_names = set(actual_result.keys())

        # ASSERT
        with self.subTest("Result type", Out=type(actual_result).__name__, Exp="dict"):
            self.assertIsInstance(actual_result, dict)

        with self.subTest("Sheet name", Out=actual_sheet_names, Exp=expected_result, ):
            self.assertEqual(actual_sheet_names, expected_result)

        for sheet_name, expected_df in self.expected_sheets.items():
            result_df = actual_result[sheet_name]

            with self.subTest("Data type", Out=type(result_df).__name__, Exp=pd.DataFrame.__name__):
                self.assertIsInstance(result_df, pd.DataFrame)

            with self.subTest("Data size", Out=result_df.shape, Exp=expected_df.shape):
                self.assertEqual(result_df.shape, expected_df.shape)

    def test_raise_for_missing_file(self):
        """
        Should raise an error when the file is missing.
        """
        # ARRANGE
        folder_path = self.temp_dir
        missing_file_name = "does_not_exist.xlsx"
        expected = RuntimeError.__name__

        # ACT
        try:
            excel_file.read_excel_as_dict(folder_path, missing_file_name)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_raise_for_wrong_extension(self):
        """
        Should raise an error when the file does not have .xlsx extension.
        """
        # ARRANGE
        folder_path = self.temp_dir
        bad_file_name_extension = "not_excel.txt"
        bad_path = os.path.join(folder_path, bad_file_name_extension)
        with open(bad_path, "w") as f:
            f.write("not an excel file")

        expected = RuntimeError.__name__

        # ACT
        try:
            excel_file.read_excel_as_dict(folder_path, bad_file_name_extension)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_raise_for_multiple_dots_in_filename(self):
        """
        Should raise an error when the filename contains more than one dot.
        """
        # ARRANGE
        folder_path = self.temp_dir
        bad_file_name = "two.dot.name.xlsx"
        bad_path = os.path.join(folder_path, bad_file_name)

        # Create a valid Excel file but with invalid filename structure
        df = pd.DataFrame({"A": [1, 2, 3]})
        with pd.ExcelWriter(bad_path) as writer:
            df.to_excel(writer, index=False)

        expected = RuntimeError.__name__

        # ACT
        try:
            excel_file.read_excel_as_dict(folder_path, bad_file_name)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


class TestLoadVersion3BomTemplate(unittest.TestCase):
    """
    Unit tests for the `load_version3_bom_template` Excel template loader helper.
    """

    def setUp(self):
        """
        Create a temporary "project root" folder with a resources/templates structure.
        """
        # ARRANGE (common for tests)
        self.temp_root = tempfile.mkdtemp(prefix="v3_template_test_")
        self.templates_dir = os.path.join(self.temp_root, "src", "resources", "templates")
        os.makedirs(self.templates_dir, exist_ok=True)

        # This must match the module constants used by the function under test.
        self.template_file_name = excel_file.TEMPLATE_NAME + excel_file.excel_io.EXCEL_FILE_TYPE
        self.template_path = os.path.join(self.templates_dir, self.template_file_name)

    def tearDown(self):
        """
        Clean up temp folders created during tests.
        """
        if os.path.isdir(self.temp_root):
            shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_happy_path(self):
        """
        Should load a single-worksheet template into a non-empty DataFrame.
        """
        # ARRANGE
        # Create a realistic, non-empty template worksheet.
        template_df = pd.DataFrame(
            [
                ["Item", "Part Number", "Description", "Qty"],
                [1, "PN-1001", "Resistor 10k", 10],
                [2, "PN-1002", "Capacitor 1uF", 5],
            ]
        )
        with pd.ExcelWriter(self.template_path, engine="openpyxl") as writer:
            template_df.to_excel(writer, sheet_name="Template", index=False, header=False)

        # Patch project-root resolution so the function finds our temp template.
        with patch.object(excel_file.folder_path, "resolve_project_folder", return_value=self.temp_root):
            # ACT
            result = excel_file.load_version3_bom_template()

        # ASSERT
        with self.subTest("Result type", Out=type(result).__name__, Exp=pd.DataFrame.__name__):
            self.assertIsInstance(result, pd.DataFrame)

        with self.subTest("Not empty", Out=result.empty, Exp=False):
            self.assertFalse(result.empty)

        with self.subTest("Shape", Out=result.shape, Exp=template_df.shape):
            self.assertEqual(result.shape, template_df.shape)

        with self.subTest("Columns", Out=list(result.columns), Exp=list(template_df.columns)):
            self.assertEqual(list(result.columns), list(template_df.columns))

    def test_raises_on_multiple_worksheets(self):
        """
        Should raise RuntimeError when the template workbook contains more than one worksheet.
        """
        # ARRANGE
        df1 = pd.DataFrame({"A": [1]})
        df2 = pd.DataFrame({"B": [2]})
        with pd.ExcelWriter(self.template_path, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="Sheet1", index=False)
            df2.to_excel(writer, sheet_name="Sheet2", index=False)

        expected = RuntimeError.__name__

        # ACT
        with patch.object(excel_file.folder_path, "resolve_project_folder", return_value=self.temp_root):
            try:
                excel_file.load_version3_bom_template()
                actual = ""  # No exception raised
            except Exception as exc:
                actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_raises_on_empty(self):
        """
        Should raise RuntimeError when the template workbook has a single worksheet, but it is empty.
        """
        # ARRANGE
        empty_df = pd.DataFrame()
        with pd.ExcelWriter(self.template_path, engine="openpyxl") as writer:
            empty_df.to_excel(writer, sheet_name="Template", index=False)

        expected = RuntimeError.__name__

        # ACT
        with patch.object(excel_file.folder_path, "resolve_project_folder", return_value=self.temp_root):
            try:
                excel_file.load_version3_bom_template()
                actual = ""  # No exception raised
            except Exception as exc:
                actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
