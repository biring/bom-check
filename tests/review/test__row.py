"""
Unit tests for BOM row reviewers.

This module validates that each reviewer in `src.review._row`:
 - Returns "" for valid inputs
 - Returns a descriptive message containing the field name for invalid inputs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/review/test__row.py

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
    TableLabelsV3,
)
# noinspection PyProtectedMember
from src.review import _row as review  # Direct internal import — acceptable in tests
from tests.fixtures import v3_value as vfx


class TestItem(unittest.TestCase):
    """
    Unit tests for the `item` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid item values.
        """
        # ARRANGE
        valid_values = list(vfx.ITEM_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.item(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid item values.
        """
        # ARRANGE
        invalid_values = list(vfx.ITEM_BAD)
        expected = TableLabelsV3.ITEM
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.item(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestComponentType(unittest.TestCase):
    """
    Unit tests for the `component_type` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid component type values.
        """
        # ARRANGE
        valid_values = list(vfx.COMP_TYPE_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.component_type(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid component type values.
        """
        # ARRANGE
        invalid_values = list(vfx.COMP_TYPE_BAD)
        expected = TableLabelsV3.COMPONENT_TYPE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.component_type(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestDevicePackage(unittest.TestCase):
    """
    Unit tests for the `device_package` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid device package values.
        """
        # ARRANGE
        valid_values = list(vfx.DEVICE_PACKAGE_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.device_package(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid device package values.
        """
        # ARRANGE
        invalid_values = list(vfx.DEVICE_PACKAGE_BAD)
        expected = TableLabelsV3.DEVICE_PACKAGE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.device_package(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestDescription(unittest.TestCase):
    """
    Unit tests for the `description` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid description values.
        """
        # ARRANGE
        valid_values = list(vfx.DESCRIPTION_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.description(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid description values.
        """
        # ARRANGE
        invalid_values = list(vfx.DESCRIPTION_BAD)
        expected = TableLabelsV3.DESCRIPTION
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.description(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestUnits(unittest.TestCase):
    """
    Unit tests for the `units` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid units values.
        """
        # ARRANGE
        valid_values = list(vfx.UNITS_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.units(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid units values.
        """
        # ARRANGE
        invalid_values = list(vfx.UNITS_BAD)
        expected = TableLabelsV3.UNITS
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.units(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestClassification(unittest.TestCase):
    """
    Unit tests for the `classification` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid classification values.
        """
        # ARRANGE
        valid_values = list(vfx.CLASSIFICATION_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.classification(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid classification values.
        """
        # ARRANGE
        invalid_values = list(vfx.CLASSIFICATION_BAD)
        expected = TableLabelsV3.CLASSIFICATION
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.classification(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestManufacturerName(unittest.TestCase):
    """
    Unit tests for the `mfg_name` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid manufacturer names.
        """
        # ARRANGE
        valid_values = list(vfx.MFG_NAME_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.mfg_name(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid manufacturer names.
        """
        # ARRANGE
        invalid_values = list(vfx.MFG_NAME_BAD)
        expected = TableLabelsV3.MFG_NAME
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.mfg_name(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestMfgPartNumber(unittest.TestCase):
    """
    Unit tests for the `mfg_part_no` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid manufacturer part numbers.
        """
        # ARRANGE
        valid_values = list(vfx.MFG_PART_NO_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.mfg_part_no(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid manufacturer part numbers.
        """
        # ARRANGE
        invalid_values = list(vfx.MFG_PART_NO_BAD)
        expected = TableLabelsV3.MFG_PART_NO
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.mfg_part_no(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestUlVdeNumber(unittest.TestCase):
    """
    Unit tests for the `ul_vde_number` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid UL/VDE numbers.
        """
        # ARRANGE
        valid_values = list(vfx.UL_VDE_NO_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.ul_vde_number(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid UL/VDE numbers.
        """
        # ARRANGE
        invalid_values = list(vfx.UL_VDE_NO_BAD)
        expected = TableLabelsV3.UL_VDE_NO
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.ul_vde_number(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestValidatedAt(unittest.TestCase):
    """
    Unit tests for the `validated_at` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid validated-at tokens.
        """
        # ARRANGE
        valid_values = list(vfx.VALIDATED_AT_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.validated_at(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid validated-at tokens.
        """
        # ARRANGE
        invalid_values = list(vfx.VALIDATED_AT_BAD)
        expected = TableLabelsV3.VALIDATED_AT
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.validated_at(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestQuantity(unittest.TestCase):
    """
    Unit tests for the `quantity` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid quantity values.
        """
        # ARRANGE
        valid_values = list(vfx.QUANTITY_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.quantity(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid quantity values.
        """
        # ARRANGE
        invalid_values = list(vfx.QUANTITY_BAD)
        expected = TableLabelsV3.QUANTITY
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.quantity(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestDesignator(unittest.TestCase):
    """
    Unit tests for the `designator` reviewer.
    """

    def test_valid(self):
        """Should return empty string for valid designator values."""
        # ARRANGE
        valid_values = list(vfx.DESIGNATOR_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.designator(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid designator values.
        """
        # ARRANGE
        invalid_values = list(vfx.DESIGNATOR_BAD)
        expected = TableLabelsV3.DESIGNATORS
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.designator(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestUnitPrice(unittest.TestCase):
    """
    Unit tests for the `unit_price` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid unit price values.
        """
        # ARRANGE
        valid_values = list(vfx.PRICE_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.unit_price(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid unit price values.
        """
        # ARRANGE
        invalid_values = list(vfx.PRICE_BAD)
        expected = TableLabelsV3.UNIT_PRICE
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.unit_price(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


class TestSubTotal(unittest.TestCase):
    """
    Unit tests for the `sub_total` reviewer.
    """

    def test_valid(self):
        """
        Should return empty string for valid sub-total values.
        """
        # ARRANGE
        valid_values = list(vfx.PRICE_GOOD)
        expected = ""

        for value in valid_values:
            # ACT
            result = review.sub_total(value)

            # ASSERT
            with self.subTest(In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return a non-empty message containing the field name for invalid sub-total values.
        """
        # ARRANGE
        invalid_values = list(vfx.PRICE_BAD)
        expected = TableLabelsV3.SUB_TOTAL
        expected_size = len(expected)

        for value in invalid_values:
            # ACT
            result = review.sub_total(value)
            result_size = len(result)

            # ASSERT
            with self.subTest("Contains", Exp=expected):
                self.assertIn(expected, result)
            with self.subTest("Size greater than", Exp=expected_size):
                self.assertLess(expected_size, result_size)


if __name__ == "__main__":
    unittest.main()
