"""
Unit tests for BOM cross field logic validators that operate on BOM rows and headers.

This module verifies that each rule:
 - Raises ValueError on contract violations with clear, centralized messages
 - Passes silently for valid inputs and skips when numeric fields are unparsable

Example Usage:
    # Preferred run from project root:
    python -m unittest tests/approve/test__logic.py

    # Discover all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - External Packages: None

Notes:
    - Tests use fixtures for representative good/bad rows and headers.
    - Direct internal import (from src.approve import _logic) is acceptable in tests.
    - Numeric assertions rely on the module’s tolerance semantics rather than raw float equality.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace

# noinspection PyProtectedMember
from src.approve import _logic as logic  # Direct internal import — acceptable in tests
from tests.fixtures import v3_bom as bfx


class TestQuantityZero(unittest.TestCase):
    """
    Unit tests for `quantity_zero`.
    """

    def test_invalid(self):
        """
        Should raise when item is blank and quantity > 0.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, item="", qty="2")
        expected = ValueError.__name__

        # ACT
        try:
            logic.quantity_zero(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid(self):
        """
        Should pass silently when item is blank and quantity == 0.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, item="", qty="0")
        expected = None

        # ACT
        try:
            logic.quantity_zero(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip validation (no error) when qty cannot be parsed.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, item="", qty="")  # qty is unparsable
        expected = None

        # ACT
        try:
            logic.quantity_zero(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=None):
            self.assertEqual(result, expected)


class TestDesignatorRequired(unittest.TestCase):
    """
    Unit tests for `designator_required`.
    """

    def test_invalid(self):
        """
        Should raise when qty >= 1 (integer) and designator is blank.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="3", designators="")
        expected = ValueError.__name__

        # ACT
        try:
            logic.designator_required(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid(self):
        """
        Should pass when qty == 0 regardless of designator content.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="0", designators="")
        expected = None

        # ACT
        try:
            logic.designator_required(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip when qty is not an integer-parsable value.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="1.5", designators="")  # int() would raise
        expected = None

        # ACT
        try:
            logic.designator_required(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestDesignatorCount(unittest.TestCase):
    """
    Unit tests for `designator_count`.
    """

    def test_invalid(self):
        """
        Should raise when the number of comma-separated designators != integer qty.
        """
        # ARRANGE
        rows = (
            replace(bfx.ROW_A_1, qty="3", designators="C1, C2"),  # only 2 designators
            replace(bfx.ROW_A_1, qty="1", designators=""),  # designator missing
        )
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                logic.designator_count(row)
                result = None
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid(self):
        """
        Should pass when designator count equals integer qty.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="3", designators="C1, C2, C3")
        expected = None

        # ACT
        try:
            logic.designator_count(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip validation (no error) when qty cannot be parsed.
        """
        # ARRANGE
        rows = (
            replace(bfx.ROW_A_1, qty="", designators="C1"),  # qty is unparsable to integer
            replace(bfx.ROW_A_1, qty="0", designators="C1, C2, C3"),  # zero is ignored
            replace(bfx.ROW_A_1, qty="1.56", designators=""),  # qty float is ignored
        )
        expected = None

        for row in rows:
            # ACT
            try:
                logic.designator_count(row)
                result = None
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestUnitPriceSpecified(unittest.TestCase):
    """
    Unit tests for `unit_price_specified`.
    """

    def test_invalid(self):
        """
        Should raise when qty > 0 and unit_price <= 0.
        """
        # ARRANGE
        cases = [
            replace(bfx.ROW_A_1, qty="1", unit_price="0"),
            replace(bfx.ROW_A_1, qty="2.5", unit_price="-10.0"),
        ]
        expected = ValueError.__name__

        for row in cases:
            # ACT
            try:
                logic.unit_price_specified(row)
                result = None
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_zero_qty(self):
        """
        Should pass when qty == 0 even if unit_price <= 0.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="0", unit_price="0")
        expected = None

        # ACT
        try:
            logic.unit_price_specified(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid_positive(self):
        """
        Should pass when qty > 0 and unit_price > 0.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="3", unit_price="0.25")
        expected = None

        # ACT
        try:
            logic.unit_price_specified(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip validation (no error) when qty or unit_price is unparsable.
        """
        # ARRANGE
        cases = [
            replace(bfx.ROW_A_1, qty="", unit_price="0.1"),
            replace(bfx.ROW_A_1, qty="1", unit_price=""),
        ]
        expected = None

        for row in cases:
            # ACT
            try:
                logic.unit_price_specified(row)
                result = None
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSubtotalZero(unittest.TestCase):
    """
    Unit tests for `subtotal_zero`.
    """

    def test_invalid(self):
        """
        Should raise when qty == 0 but sub_total != 0.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="0", sub_total="0.50")
        expected = ValueError.__name__

        # ACT
        try:
            logic.subtotal_zero(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid(self):
        """
        Should pass when qty == 0 and sub_total == 0.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="0", sub_total="0")
        expected = None

        # ACT
        try:
            logic.subtotal_zero(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip validation (no error) when qty or sub_total is unparsable.
        """
        # ARRANGE
        cases = [
            replace(bfx.ROW_A_1, qty="", sub_total="0.00"),  # qty unparsable
            replace(bfx.ROW_A_1, qty="0", sub_total=""),  # sub_total unparsable
        ]
        expected = None

        # ACT & ASSERT
        for row in cases:
            try:
                logic.subtotal_zero(row)
                result = None
            except ValueError as e:
                result = type(e).__name__

            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSubTotalCalculation(unittest.TestCase):
    """
    Unit tests for `sub_total_calculation`.
    """

    def test_invalid(self):
        """
        Should raise when sub_total != qty * unit_price (per floats_equal).
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="2", unit_price="0.25", sub_total="0.30")  # should be 0.50
        expected = ValueError.__name__

        # ACT
        try:
            logic.sub_total_calculation(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid(self):
        """
        Should pass when sub_total equals qty * unit_price.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="2", unit_price="0.5", sub_total="1.0")
        expected = None

        # ACT
        try:
            logic.sub_total_calculation(row)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip validation (no error) when any of qty, unit_price, or sub_total is unparsable.
        """
        # ARRANGE
        cases = [
            replace(bfx.ROW_A_1, qty="2", unit_price="", sub_total="0.50"),  # unit_price unparsable
            replace(bfx.ROW_A_1, qty="", unit_price="0.25", sub_total="0.25"),  # qty unparsable
            replace(bfx.ROW_A_1, qty="1", unit_price="0.25", sub_total="")  # sub_total unparsable
        ]
        expected = None

        # ACT & ASSERT
        for row in cases:
            try:
                logic.sub_total_calculation(row)
                result = None
            except ValueError as e:
                result = type(e).__name__

            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestMaterialCostCalculation(unittest.TestCase):
    """
    Unit tests for `material_cost_calculation`.
    """

    def test_invalid(self):
        """
        Should raise when material_cost != sum of sub_totals.
        """
        # ARRANGE
        rows = [
            replace(bfx.ROW_A_1),  # sub_total="0.2"
            replace(bfx.ROW_A_2),  # sub_total="0.6"
        ]  # sum = 0.8
        header = replace(bfx.HEADER_A, material_cost="0.90")  # mismatch
        expected = ValueError.__name__

        # ACT
        try:
            logic.material_cost_calculation(rows, header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid_two_rows(self):
        """
        Should pass when material_cost equals sum of two row sub_totals.
        """
        # ARRANGE
        rows = [
            replace(bfx.ROW_A_1),  # 0.2
            replace(bfx.ROW_A_2),  # 0.6
        ]  # sum = 0.8
        header = replace(bfx.HEADER_A, material_cost="0.80")
        expected = None

        # ACT
        try:
            logic.material_cost_calculation(rows, header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid_three_rows(self):
        """
        Should pass when material_cost equals sum of three row sub_totals.
        """
        # ARRANGE
        rows = [
            replace(bfx.ROW_A_1, sub_total="0.20"),
            replace(bfx.ROW_A_2, sub_total="0.60"),
            replace(bfx.ROW_A_3, sub_total="1.10"),
        ]
        header = replace(bfx.HEADER_A, material_cost="1.90")
        expected = None

        # ACT
        try:
            logic.material_cost_calculation(rows, header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore_all_rows_unparsable(self):
        """
        Should skip validation when *no* row sub_total can be parsed (parsed == False).
        """
        # ARRANGE
        rows = [
            replace(bfx.ROW_A_1, sub_total=""),
            replace(bfx.ROW_A_2, sub_total=""),
        ]  # all unparsable -> parsed stays False
        header = replace(bfx.HEADER_A, material_cost="0.00")
        expected = None

        # ACT
        try:
            logic.material_cost_calculation(rows, header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore_header_unparsable(self):
        """
        Should skip validation when header.material_cost is unparsable (after at least one parsed row).
        """
        # ARRANGE
        rows = [
            replace(bfx.ROW_A_1),  # sub_total parses to 0.2
            replace(bfx.ROW_A_2),  # sub_total parses to 0.6
        ]
        header = replace(bfx.HEADER_A, material_cost="")  # unparsable
        expected = None

        # ACT
        try:
            logic.material_cost_calculation(rows, header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestTotalCostCalculation(unittest.TestCase):
    """
    Unit tests for `total_cost_calculation`.
    """

    def test_invalid(self):
        """
        Should raise when total_cost != material_cost + overhead_cost.
        """
        # ARRANGE
        header = replace(bfx.HEADER_A, material_cost="1.00", overhead_cost="0.25", total_cost="1.10")
        expected = ValueError.__name__

        # ACT
        try:
            logic.total_cost_calculation(header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_valid(self):
        """
        Should pass when total_cost == material_cost + overhead_cost.
        """
        # ARRANGE
        header = bfx.HEADER_A
        expected = None

        # ACT
        try:
            logic.total_cost_calculation(header)
            result = None
        except ValueError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignore(self):
        """
        Should skip validation (no error) when any numeric field is unparsable.
        """
        # ARRANGE
        cases = [
            replace(bfx.HEADER_A, material_cost=""),  # material_cost unparsable
            replace(bfx.HEADER_A, overhead_cost=""),  # overhead_cost unparsable
            replace(bfx.HEADER_A, total_cost=""),  # total_cost unparsable
        ]
        expected = None

        for header in cases:
            # ACT
            try:
                logic.total_cost_calculation(header)
                result = None
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
