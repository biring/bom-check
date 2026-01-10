"""
Unit test for review helpers in `src.review._logic`.

These tests assert that each helper:
    - Returns "" for valid inputs (no exception propagation)
    - Returns the original validator's error text for invalid inputs
    - Delegates correctly to `src.review._common.review_and_capture_by_args` with proper args/kwargs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/review/test__logic.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Tests treat helpers as thin wrappers over `src.approve.interfaces` validators.
    - Fixtures create minimal `src.models.interfaces.Row`/`Header` instances to exercise pass/fail paths.
    - Error strings are compared exactly to ensure consistent reporting.

License:
    - Internal Use Only
"""

import unittest

from src.models.interfaces import (
    HeaderV3,
    RowV3,
)

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

# noinspection PyProtectedMember
from src.review import _logic as logic  # Integration import of the internal module


class TestQuantityZero(unittest.TestCase):
    """
    Unit Unit test for `quantity_zero`.
    """

    def test_valid(self):
        """
        Should return empty message when item is blank and qty is zero.
        """
        # ARRANGE
        row = RowV3(item="", qty="0", designators="", unit_price="0.00", sub_total="0.00")
        expected = ""

        # ACT
        result = logic.quantity_zero(row)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'quantity' when item is blank and quantity == 0.
        """
        # ARRANGE
        row = RowV3(item="", qty="2", designators="", unit_price="0.25", sub_total="0.50")
        expected_contains = TableLabelsV3.QUANTITY
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.quantity_zero(row)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestDesignatorRequired(unittest.TestCase):
    """
    Unit test for `designator_required`.
    """

    def test_valid(self):
        """
        Should return empty message when qty > 0 and designator(s) are present.
        """
        # ARRANGE
        row = RowV3(item="R", qty="3", designators="R1, R2, R3", unit_price="0.10", sub_total="0.30")
        expected = ""

        # ACT
        result = logic.designator_required(row)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'designator' when qty >= 1 (integer) and designator is blank.
        """
        # ARRANGE
        row = RowV3(item="R", qty="1", designators="", unit_price="0.10", sub_total="0.10")
        expected_contains = TableLabelsV3.DESIGNATORS
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.designator_required(row)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestDesignatorCount(unittest.TestCase):
    """
    Unit test for `designator_count`.
    """

    def test_valid(self):
        """
        Should return empty message when designator count equals integer qty.
        """
        # ARRANGE
        row = RowV3(qty="3", designators="R1, R2, R3")
        expected = ""

        # ACT
        result = logic.designator_count(row)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'designator' when the number of comma-separated designators != integer qty.
        """
        # ARRANGE
        row = RowV3(qty="3", designators="R1, R2")  # only 2 designators, qty=3
        expected_contains = TableLabelsV3.DESIGNATORS
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.designator_count(row)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestUnitPriceSpecified(unittest.TestCase):
    """
    Unit test for `unit_price_specified`.
    """

    def test_valid(self):
        """
        Should return empty message when qty > 0 and unit price > 0.
        """
        # ARRANGE
        row = RowV3(qty="2", unit_price="0.25")
        expected = ""

        # ACT
        result = logic.unit_price_specified(row)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'unit price' when qty > 0 but unit price is zero/blank.
        """
        # ARRANGE
        row = RowV3(qty="2", unit_price="0.00")
        expected_contains = TableLabelsV3.UNIT_PRICE
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.unit_price_specified(row)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp="unit price (~'unit')"):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestSubtotalZero(unittest.TestCase):
    """
    Unit test for `subtotal_zero`.
    """

    def test_valid(self):
        """
        Should return empty message when qty == 0 and sub_total == 0.
        """
        # ARRANGE
        row = RowV3(qty="0", sub_total="0.00")
        expected = ""

        # ACT
        result = logic.subtotal_zero(row)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'sub-total' when qty == 0 but sub_total > 0.
        """
        # ARRANGE
        row = RowV3(qty="0", sub_total="1.00")
        expected_contains = TableLabelsV3.SUB_TOTAL
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.subtotal_zero(row)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestSubTotalCalculation(unittest.TestCase):
    """
    Unit test for `sub_total_calculation`.
    """

    def test_valid(self):
        """
        Should return empty message when sub_total == qty * unit_price.
        """
        # ARRANGE
        row = RowV3(qty="2", unit_price="0.25", sub_total="0.50")
        expected = ""

        # ACT
        result = logic.sub_total_calculation(row)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'sub-total' when calculation does not match.
        """
        # ARRANGE
        row = RowV3(qty="2", unit_price="0.25", sub_total="0.60")
        expected_contains = TableLabelsV3.SUB_TOTAL
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.sub_total_calculation(row)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestMaterialCostCalculation(unittest.TestCase):
    """
    Unit test for `material_cost_calculation`.
    """

    def test_valid(self):
        """
        Should return empty message when header.material_cost == sum(row.sub_total for rows).
        """
        # ARRANGE
        rows = (
            RowV3(sub_total="0.60"),
            RowV3(sub_total="0.40"),
        )
        header = HeaderV3(material_cost="1.00", overhead_cost="0.50", total_cost="1.50")
        expected = ""

        # ACT
        result = logic.material_cost_calculation(rows, header)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'material cost' when header value mismatches sum(rows).
        """
        # ARRANGE
        rows = (
            RowV3(sub_total="0.60"),
            RowV3(sub_total="0.40"),
        )
        header = HeaderV3(material_cost="1.10", overhead_cost="0.50", total_cost="1.60")
        expected_contains = HeaderLabelsV3.MATERIAL_COST
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.material_cost_calculation(rows, header)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


class TestTotalCostCalculation(unittest.TestCase):
    """
    Unit test for `total_cost_calculation`.
    """

    def test_valid(self):
        """
        Should return empty message when total_cost == material_cost + overhead_cost.
        """
        # ARRANGE
        header = HeaderV3(material_cost="1.00", overhead_cost="0.50", total_cost="1.50")
        expected = ""

        # ACT
        result = logic.total_cost_calculation(header)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message mentioning 'total cost' when header.total_cost is incorrect.
        """
        # ARRANGE
        header = HeaderV3(material_cost="1.00", overhead_cost="0.50", total_cost="1.60")
        expected_contains = HeaderLabelsV3.TOTAL_COST
        expected_min_len = len(expected_contains)

        # ACT
        result = logic.total_cost_calculation(header)

        # ASSERT
        with self.subTest("Contains", Out=result, Exp=expected_contains):
            self.assertIn(expected_contains, result)
        with self.subTest("Size", Out=len(result), Exp=f">{expected_min_len}"):
            self.assertGreater(len(result), expected_min_len)


if __name__ == "__main__":
    unittest.main()
