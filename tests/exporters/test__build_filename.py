"""
Unit tests for BOM-derived filename construction utilities.

This module validates extraction of BOM header metadata and the composition of deterministic, whitespace-free filenames for logging purposes, including conditional inclusion of board names, timestamp integration, and error handling for invalid or missing inputs.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/exporters/test__build_filename.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Uses predefined BOM fixtures representing single-board and multi-board scenarios sourced from a shared fixtures module.
	- Constructs empty BOM instances inline to validate error handling paths for missing data.
	- Patches timestamp providers to supply deterministic date and time values for reproducible filename assertions.
	- No filesystem interaction; all data is in-memory and requires no cleanup.

Dependencies:
	- Python >= 3.10
	- Standard Library: unittest, unittest.mock

Notes:
	- Helper extraction behaviors are validated independently to ensure correct handling of edge cases such as empty or multi-board inputs.
	- Filename construction is treated as deterministic given patched timestamp inputs and controlled fixture data.
	- Whitespace removal is explicitly validated to ensure filesystem-safe output.
	- Error handling tests primarily assert exception types, with limited validation of message content.
	- Timestamp functions are patched via a dependency module to maintain a stable and consistent test seam.

License:
	- Internal Use Only
"""

import unittest
from unittest.mock import patch

from tests.fixtures import v3_bom as fixture

# noinspection PyProtectedMember
from src.exporters import _build_filename as builder, _dependencies as dep


class TestExtractBoardName(unittest.TestCase):
    """
    Unit tests for the `_extract_board_name` helper.
    """

    def test_single_board_returns_board_name(self):
        """
        Should return board name when BOM contains exactly one board.
        """
        # ARRANGE
        bom = fixture.BOM_A
        expected = bom.boards[0].header.board_name

        # ACT
        actual = builder._extract_board_name(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_multi_board_returns_none(self):
        """
        Should return None when BOM contains multiple boards.
        """
        # ARRANGE
        bom = fixture.BOM_B
        expected = None

        # ACT
        actual = builder._extract_board_name(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


class TestExtractBuildStage(unittest.TestCase):
    """
    Unit tests for the `_extract_build_stage` helper.
    """

    def test_happy_path(self):
        """
        Should return build stage from the first board header.
        """
        # ARRANGE
        bom = fixture.BOM_B
        expected = bom.boards[0].header.build_stage

        # ACT
        actual = builder._extract_build_stage(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_empty_bom(self):
        """
        Should raise ValueError when BOM contains no boards.
        """
        # ARRANGE
        empty_bom = dep.model.BomV3(boards=())
        expected = ValueError.__name__

        # ACT
        try:
            builder._extract_build_stage(empty_bom)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


class TestExtractModelNumber(unittest.TestCase):
    """
    Unit tests for the `_extract_model_number` helper.
    """

    def test_happy_path(self):
        """
        Should return model number from the first board header.
        """
        # ARRANGE
        bom = fixture.BOM_B
        expected = bom.boards[0].header.model_no

        # ACT
        actual = builder._extract_model_number(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_empty_bom(self):
        """
        Should raise ValueError when BOM contains no boards.
        """
        # ARRANGE
        empty_bom = dep.model.BomV3(boards=())
        expected = ValueError.__name__

        # ACT
        try:
            builder._extract_model_number(empty_bom)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)


class TestBuildCheckerLogFilename(unittest.TestCase):
    """
    Unit tests for the `build_checker_log_filename` function.
    """

    def test_single_board(self):
        """
        Should include board name in filename when BOM has exactly one board.
        """
        # ARRANGE
        datestamp = "251231"
        bom = fixture.BOM_A
        expected = (
            f"{datestamp}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_A.boards[0].header.model_no}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_A.boards[0].header.build_stage}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_A.boards[0].header.board_name}{builder.FILE_NAME_SEPARATOR}"
            f"{builder.SUFFIX_CHECKER_LOG}"
        ).replace(" ", "")

        patch_fn = dep.timestamp.now_local_date.__name__
        with patch.object(dep.timestamp, patch_fn, return_value=datestamp):
            # ACT
            actual = builder.build_checker_log_filename(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_multi_board(self):
        """
        Should omit board name when BOM contains multiple boards.
        """
        # ARRANGE
        datestamp = "301025"
        bom = fixture.BOM_B
        expected = (
            f"{datestamp}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_B.boards[0].header.model_no}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_B.boards[0].header.build_stage}{builder.FILE_NAME_SEPARATOR}"
            f"{builder.SUFFIX_CHECKER_LOG}"
        ).replace(" ", "")

        patch_fn = dep.timestamp.now_local_date.__name__
        with patch.object(dep.timestamp, patch_fn, return_value=datestamp):
            # ACT
            actual = builder.build_checker_log_filename(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_whitespace_is_removed(self):
        """
        Should remove all whitespace from the final filename.
        """
        # ARRANGE
        datestamp = "2020 10 15"  # with whitespace
        bom = fixture.BOM_B
        expected = (
            f"{datestamp}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_B.boards[0].header.model_no}{builder.FILE_NAME_SEPARATOR}"
            f"{fixture.BOM_B.boards[0].header.build_stage}{builder.FILE_NAME_SEPARATOR}"
            f"{builder.SUFFIX_CHECKER_LOG}"
        ).replace(" ", "")

        patch_fn = dep.timestamp.now_local_date.__name__
        with patch.object(dep.timestamp, patch_fn, return_value=datestamp):
            # ACT
            actual = builder.build_checker_log_filename(bom)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_empty_bom(self):
        """
        Should raise an error when required BOM metadata cannot be extracted.
        """
        # ARRANGE
        empty_bom = builder.model.BomV3(boards=())
        expected = RuntimeError.__name__

        # ACT
        try:
            builder.build_checker_log_filename(empty_bom)
            actual = ""
        except Exception as exc:
            actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_unknown_issue(self):
        """
        Should raise an error when an unexpected issue is detected.
        """
        # ARRANGE
        bom = fixture.BOM_A
        expected = RuntimeError.__name__

        patch_fn = dep.timestamp.now_local_date.__name__
        with patch.object(dep.timestamp, patch_fn, side_effect=RuntimeError):

            # ACT
            try:
                builder.build_checker_log_filename(bom)
                actual = ""
            except Exception as exc:
                actual = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

class TestGenerateTimestampedLogFilename(unittest.TestCase):
    """
    Unit tests verify constructing timestamped log filenames.
    """

    def test_patched_happy_path(self):
        """
        Should return timestamped filename with valid suffix.
        """
        # ARRANGE
        date = "250101"
        time = "124526"
        suffix = "AuditLog"
        expected = f"{date}{builder.FILE_NAME_SEPARATOR}{time}{builder.FILE_NAME_SEPARATOR}{suffix}"

        patch_file = dep.timestamp
        patch_date = patch_file.now_local_date.__name__
        patch_time = patch_file.now_local_time.__name__

        # ACT
        with patch.object(patch_file, patch_date, return_value=date):
            with patch.object(patch_file, patch_time, return_value=time):
                actual = builder.generate_timestamped_log_filename(suffix)

        # ASSERT
        with self.subTest(Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_short_suffix(self):
        """
        Should raise RuntimeError when suffix is too short.
        """
        # ARRANGE
        suffix = "ab"
        expected_type = RuntimeError.__name__
        expected_reason = "characters"

        # ACT
        try:
            builder.generate_timestamped_log_filename(suffix)
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
        with self.subTest("Message contains reason", Act=actual_message):
            self.assertIn(expected_reason, actual_message)


    def test_integration_happy_path(self):
        """
        Should return timestamped filename with valid suffix.
        """
        # ARRANGE
        minimum_length = 14 # 6 for date, 6 for time, plus 2 dash
        suffix = "TestLog"
        expected_length = minimum_length + len(suffix)

        # ACT
        actual = builder.generate_timestamped_log_filename(suffix)

        # ASSERT
        actual_length = len(actual)
        with self.subTest("File name length", Act=actual_length, Exp=expected_length):
            self.assertEqual(actual_length, expected_length)


if __name__ == "__main__":
    unittest.main()
