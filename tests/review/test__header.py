"""
Unit tests for BOM header reviewers.

This module validates that each reviewer in `src.rules.review.header`:
 - Returns "" for valid inputs
 - Returns a descriptive message containing the field name for invalid inputs
 - Covers regex-driven fields (model number, board name, build stage), dates, and numeric costs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/review/test__header.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests


Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - External Packages: None

Notes:
    - Reviewers are pure functions: success -> "", failure -> descriptive error text.
    - Fixtures provide representative good/bad values for comprehensive coverage.
    - Tests validate reviewer behavior, not internal validator implementation.

License:
    - Internal Use Only
"""

import unittest

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)
# noinspection PyProtectedMember
from src.review import _header as review  # Direct internal import — acceptable in tests
from tests.fixtures import v3_value as vfx


class TestModelNumber(unittest.TestCase):
    """
    Unit tests for the `model_number` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid model numbers.
        """
        # ARRANGE
        valid_values = vfx.MODEL_NO_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.model_number(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid model numbers.
        """
        # ARRANGE
        invalid_values = vfx.MODEL_NO_BAD
        expected = HeaderLabelsV3.MODEL_NO
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.model_number(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBoardName(unittest.TestCase):
    """
    Unit tests for the `board_name` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid board names.
        """
        # ARRANGE
        valid_values = vfx.BOARD_NAME_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.board_name(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid board names.
        """
        # ARRANGE
        invalid_values = vfx.BOARD_NAME_BAD
        expected = HeaderLabelsV3.BOARD_NAME
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.board_name(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBoardSupplier(unittest.TestCase):
    """
    Unit tests for the `board_supplier` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid board supplier names.
        """
        # ARRANGE
        valid_values = vfx.BOARD_SUPPLIER_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.board_supplier(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid board supplier names.
        """
        # ARRANGE
        invalid_values = vfx.BOARD_SUPPLIER_BAD
        expected = HeaderLabelsV3.BOARD_SUPPLIER
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.board_supplier(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBuildStage(unittest.TestCase):
    """
    Unit tests for the `build_stage` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid build stages.
        """
        # ARRANGE
        valid_values = vfx.BUILD_STAGE_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.build_stage(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid build stages.
        """
        # ARRANGE
        invalid_values = vfx.BUILD_STAGE_BAD
        expected = HeaderLabelsV3.BUILD_STAGE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.build_stage(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestBomDate(unittest.TestCase):
    """
    Unit tests for the `bom_date` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid BOM dates.
        """
        # ARRANGE
        valid_values = vfx.BOM_DATE_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.bom_date(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid BOM dates.
        """
        # ARRANGE
        invalid_values = vfx.BOM_DATE_BAD
        expected = HeaderLabelsV3.BOM_DATE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.bom_date(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestMaterialCost(unittest.TestCase):
    """
    Unit tests for the `material_cost` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid material costs.
        """
        # ARRANGE
        valid_values = vfx.COST_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.material_cost(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid material costs.
        """
        # ARRANGE
        invalid_values = vfx.COST_BAD
        expected = HeaderLabelsV3.MATERIAL_COST
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.material_cost(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestOverheadCost(unittest.TestCase):
    """
    Unit tests for the `overhead_cost` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid overhead costs.
        """
        # ARRANGE
        valid_values = vfx.COST_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.overhead_cost(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid overhead costs.
        """
        # ARRANGE
        invalid_values = vfx.COST_BAD
        expected = HeaderLabelsV3.OVERHEAD_COST
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.overhead_cost(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestTotalCost(unittest.TestCase):
    """
    Unit tests for the `total_cost` reviewer.
    """

    def test_valid(self):
        """
        Should return "" for valid total costs.
        """
        # ARRANGE
        valid_values = vfx.COST_GOOD
        expected = ""  # No message

        for value in valid_values:
            # ACT
            result = review.total_cost(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid total costs.
        """
        # ARRANGE
        invalid_values = vfx.COST_BAD
        expected = HeaderLabelsV3.TOTAL_COST
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.total_cost(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertTrue(expected in result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


if __name__ == "__main__":
    unittest.main()
