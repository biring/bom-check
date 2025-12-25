"""
Happy-path integration tests for the importers interfaces façade.

Example Usage:
    # Via unittest runner (preferred):
    python -m unittest tests/importers/test_interfaces.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, tempfile, shutil, os
    - External Packages: pandas

Notes:
    - Tests treat the importer façade as an integration boundary, ensuring internal helpers are invoked correctly.
    - Temporary folders and real files are created to validate end-to-end behavior.
    - Negative-path or exception scenarios are intentionally excluded to keep scope limited to interface happy-path validation.

License:
    - Internal Use Only
"""

import os
import shutil
import tempfile
import unittest

import pandas as pd

from src.importers import interfaces as importer


class TestInterface(unittest.TestCase):
    """
    Integration-style tests for the `importers` public interface.
    """

    def setUp(self):
        """
        Create a temporary folder with real data for integration testing.
        """
        # ARRANGE (common for tests)
        self.file_name = "interface_workbook.xlsx"

        # Create a temporary directory to hold the test Excel file
        self.temp_dir = tempfile.mkdtemp(prefix="importer_interface_test_")

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

    def test_read_excel_as_dict(self):
        """
        Should load a valid Excel file via the public interface and return a dict of DataFrames.
        """
        # ARRANGE
        folder_path = self.temp_dir
        file_name = self.file_name
        expected_sheet_names = sorted(self.expected_sheets.keys())

        # ACT
        # Call the public façade, exercising the integration with internal helpers.
        result = importer.read_excel_as_dict(folder_path, file_name)

        # ASSERT
        # Verify type of the result
        with self.subTest("Result type", Out=type(result).__name__, Exp="dict"):
            self.assertIsInstance(result, dict)

        # Verify sheet name keys
        actual_sheet_names = sorted(result.keys())
        with self.subTest("Sheet names", Out=actual_sheet_names, Exp=expected_sheet_names):
            self.assertEqual(actual_sheet_names, expected_sheet_names)

        # Verify each sheet is a DataFrame with the expected shape
        for sheet_name, expected_df in self.expected_sheets.items():
            result_df = result[sheet_name]

            with self.subTest(
                    f"{sheet_name} type", Out=type(result_df).__name__, Exp=pd.DataFrame.__name__
            ):
                self.assertIsInstance(result_df, pd.DataFrame)

            with self.subTest(
                    f"{sheet_name} shape", Out=result_df.shape, Exp=expected_df.shape
            ):
                self.assertEqual(result_df.shape, expected_df.shape)

    def test_load_version3_bom_template(self):
        """
        Should load the bundled Version 3 BOM template and return a non-empty DataFrame.
        """
        # ARRANGE
        # Nothing to arrange the template ia located in the resource folder

        # ACT
        result = importer.load_version3_bom_template()

        # ASSERT
        with self.subTest("Data type", Out=type(result).__name__, Exp=pd.DataFrame.__name__):
            self.assertIsInstance(result, pd.DataFrame)

        with self.subTest("Size", Out=result.shape, Exp=">0"):
            self.assertGreater(result.shape[0], 0)
            self.assertGreater(result.shape[1], 0)



if __name__ == "__main__":
    unittest.main()
