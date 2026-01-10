"""
Unit tests for internal BOM filename construction utilities.

This module verifies behavior of filename builders and helper extractors used by the exporters layer to generate deterministic, filesystem-safe log filenames
from BOM header metadata.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/exporters/test__build_filename.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock
    - Internal Packages:
        - src.exporters._build_filename
        - src.exporters._dependencies
        - tests.fixtures.v3_bom

Notes:
    - Tests treat filename builders as deterministic pure functions.
    - Time-dependent behavior is patched exclusively through the exporters dependency module to ensure a stable patch seam.
    - Helper functions are tested directly to validate edge cases independently of the public builder.
    - Error assertions validate exception type only, not message content.

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


if __name__ == "__main__":
    unittest.main()
