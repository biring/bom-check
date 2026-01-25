"""
Integration-style tests covering the public exporter interface behaviors.

This module validates the happy-path and error-path interactions of the exporter façade by asserting return types, raised exceptions, and filesystem side effects when generating filenames and writing output files based on provided inputs.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/exporters/test_interfaces.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- Static bill of materials objects imported from shared test fixtures.
	- Temporary directories created via standard library utilities to isolate filesystem side effects.
	- Real files written to disk within temporary directories and implicitly cleaned up when contexts exit.

Dependencies
	- Python 3.x
	- Standard Library:
		- os
		- tempfile
		- unittest
		- dataclasses
	- External Packages:
		- pandas

Notes
	- Tests exercise the exporter façade as an integration boundary and rely on real filesystem writes for verification.
	- Determinism depends on fixture stability and filesystem availability rather than mocked I/O.
	- Assertions focus on observable outputs such as return values, exceptions, and file existence rather than file contents.

License
	- Internal Use Only
"""

import os
import tempfile
import unittest
import pandas as pd
from dataclasses import replace
from tests.fixtures import v3_bom as fixture
from src.exporters import interfaces as exporter
# noinspection PyProtectedMember
from src.exporters import _dependencies as dep


class TestInterfaces(unittest.TestCase):
    """
    Integration-style tests for the `exporters` public interface.
    """

    def test_build_checker_log_filename(self):
        """
        Should return a filename string with a reasonable minimum length.
        """
        # ARRANGE
        bom = fixture.BOM_A
        expected_type = str
        expected_min_length = 16  # Date (6) + model number (5) + build stage (2) + suffix (3) should be > 16

        # ACT
        actual = exporter.build_checker_log_filename(bom)
        actual_type = type(actual)
        actual_length = len(actual)

        # ASSERT
        with self.subTest("Type", Out=actual_type, Exp=expected_type):
            self.assertEqual(actual_type, expected_type)
        with self.subTest("Minimum length", Out=actual_length, Min=expected_min_length):
            self.assertGreater(actual_length, expected_min_length)

    def test_build_checker_log_filename_raises(self):
        """
        Should raise RuntimeError when the BOM does not contain required header metadata needed to build a checker log filename.
        """
        # ARRANGE
        bom = replace(fixture.BOM_A, boards=())  # No boards in the bom
        expected_exc = RuntimeError

        # ACT
        try:
            exporter.build_checker_log_filename(bom)
            actual = ""  # No exception raised
        except Exception as e:
            actual = type(e)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected_exc):
            self.assertEqual(actual, expected_exc)

    def test_write_excel_sheets(self) -> None:
        """
        Should call write_excel_sheets and return None on the happy path.
        """
        # ARRANGE
        fn = getattr(exporter, "write_excel_sheets", None)
        expected_return = None

        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "bom_export"
            sheets = {
                "Sheet1": pd.DataFrame([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]),
                "Sheet2": pd.DataFrame([{"sku": "ABC-001", "qty": 10}]),
            }
            expected_path = os.path.join(folder, file_name + dep.excel_io.EXCEL_FILE_TYPE)

            # ACT
            result = fn(  # type: ignore[misc]
                folder,
                file_name,
                sheets,
                overwrite=True,
                top_row_is_header=True,
            )
            exists = os.path.isfile(expected_path)

            # ASSERT
            with self.subTest("callable_exists", Act=callable(fn), Exp=True):
                self.assertTrue(callable(fn))
            with self.subTest("return_type", Act=result, Exp=expected_return):
                self.assertIsNone(result)
            with self.subTest("file_exists", Act=exists, Exp=True):
                self.assertTrue(exists)

    def test_write_excel_sheets_raises(self) -> None:
        """
        Should raise RuntimeError when no data is provided.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "bom_export"
            sheets = {
                "Sheet1": pd.DataFrame(),
                "Sheet2": pd.DataFrame(),
            }
            expected_exc = RuntimeError

            # ACT
            try:
                exporter.write_excel_sheets(folder, file_name, sheets)
                actual = ""  # No exception raised
            except Exception as e:
                actual = type(e)

            # ASSERT
            with self.subTest(Out=actual, Exp=expected_exc):
                self.assertEqual(actual, expected_exc)

    def test_write_text_file_lines(self) -> None:
        """
        Should call write_text_file_lines and return None on the happy path.
        """
        # ARRANGE
        fn = getattr(exporter, "write_text_file_lines", None)
        expected_return = None

        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "checker_log"
            lines = ("Line 1", "Line 2")
            expected_path = os.path.join(folder, file_name + dep.text_io.TEXT_FILE_TYPE)

            # ACT
            result = fn(folder, file_name, lines)  # type: ignore[misc]
            exists = os.path.isfile(expected_path)

            # ASSERT
            with self.subTest("callable_exists", Act=callable(fn), Exp=True):
                self.assertTrue(callable(fn))
            with self.subTest("return_type", Act=result, Exp=expected_return):
                self.assertIsNone(result)
            with self.subTest("file_exists", Act=exists, Exp=True):
                self.assertTrue(exists)

    def test_write_text_file_lines_raises(self):
        """
        Should raise RuntimeError when no lines are provided.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = tmp_dir
            file_name = "checker_log"
            lines = ()
            expected_exc = RuntimeError

            # ACT
            try:
                exporter.write_text_file_lines(folder, file_name, lines)
                actual = ""  # No exception raised
            except Exception as e:
                actual = type(e)

            # ASSERT
            with self.subTest(Out=actual, Exp=expected_exc):
                self.assertEqual(actual, expected_exc)


if __name__ == "__main__":
    unittest.main()
