"""
Unit tests for the public interfaces of the `review` package.

This module exercises representative valid and invalid paths across the validators exposed via `src.review.interfaces`. It provides smoke coverage for the public API and ensures consistent exception behavior on malformed inputs.

Example Usage:
    # Preferred run from project root:
    python -m unittest tests/review/test_interfaces.py

    # Discover all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - Internal: src.review.interfaces, src.models.interfaces
    - External Packages: None

Notes:
    - Focus on availability, basic callability, and minimal behavioral checks; deep logic is covered in module-specific tests.
    - Valid-case tests confirm silent acceptance of clearly correct examples.
    - Invalid-case tests cover common malformed or out-of-range inputs, expecting `ValueError`.
    - This module treats `src.review.interfaces` as the public API surface.
"""

import unittest

import src.review.interfaces as review
from src.models.interfaces import (
    RowV3,
    HeaderV3,
)


class TestRowV3(unittest.TestCase):
    """
    Smoke and negative tests for Row validators in the public interface.
    """

    def test_valid_inputs(self):
        """
        Should return a empty string on valid Row values.
        """
        # ARRANGE
        cases = [
            (review.item, "23"),
            (review.component_type, "Diode/SCR"),
            (review.device_package, "0603"),
            (review.description, "1k,1%,0.5W"),  # no spaces
            (review.units, "PCS"),
            (review.classification, "A"),
            (review.mfg_name, "ST Microelectronics"),
            (review.mfg_part_no, "SN74HC595N-TR"),
            (review.ul_vde_number, "E1234"),
            (review.validated_at, "P1/EB0/MP"),
            (review.quantity, "3.5"),
            (review.designator, "R12"),
            (review.unit_price, "0.05"),
            (review.sub_total, "1.25"),
        ]
        expected = ""  # no return message

        for func, value in cases:
            # ACT
            result = func(value)

            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        Should return a non-empty string on invalid Row values.
        """
        # ARRANGE
        cases = [
            (review.item, "-1"),  # negative not allowed
            (review.component_type, "123"),  # not alphabetic style / ALT*
            (review.device_package, "QFN 32"),  # space likely invalid (expects alnum / dash)
            (review.description, ""),  # empty not allowed
            (review.units, "pcs.."),  # trailing punctuation invalid form
            (review.classification, "Z"),  # only A/B/C
            (review.mfg_name, ""),  # empty not allowed
            (review.mfg_part_no, ""),  # empty not allowed
            (review.ul_vde_number, "12AB"),  # must start letters then digits
            (review.validated_at, "X1"),  # not in allowed tokens
            (review.quantity, "-0.1"),  # non-negative only
            (review.designator, "1R"),  # must start with letters
            (review.unit_price, "-5"),  # non-negative only
            (review.sub_total, "-0.01"),  # non-negative only
        ]

        for func, value in cases:
            # ACT
            result = func(value)

            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result):
                self.assertIsNot(result, "")


class TestHeaderV3(unittest.TestCase):
    """
    Smoke and negative tests for header validators in the public interface.

    """

    def test_valid_inputs(self):
        """
        Should return an empty string on valid header values.
        """
        # ARRANGE
        cases = [
            (review.model_number, "AB123"),
            (review.board_name, "Main Control PCBA"),
            (review.board_supplier, "ACME Boards"),
            (review.build_stage, "EB1"),
            (review.bom_date, "2025-08-06"),
            (review.material_cost, "12.50"),
            (review.overhead_cost, "0.50"),
            (review.total_cost, "13.00"),
        ]
        expected = ""  # empty return message

        # ACT / ASSERT
        for func, value in cases:
            result = func(value)

            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        Should return a non-empty string on invalid header values.
        """
        # ARRANGE
        cases = [
            (review.model_number, "1A"),  # must start with 2–3 letters then digits
            (review.board_name, "Main Control PCB"),  # must end with "PCBA"
            (review.board_supplier, "ac"),  # too short / must start capital
            (review.build_stage, "ALPHA"),  # not an allowed token
            (review.bom_date, "2025.08.06"),  # unsupported format
            (review.material_cost, "-1.0"),  # non-negative only
            (review.overhead_cost, "-0.01"),  # non-negative only
            (review.total_cost, "-2.0"),  # non-negative only
        ]

        # ACT / ASSERT
        for func, value in cases:
            result = func(value)

            with self.subTest(func=func.__name__, In=value, Out=result):
                self.assertIsNot(result, "")


class TestLogic(unittest.TestCase):
    """
    Smoke and negative tests for cross-field logic validators in the public interface.
    """

    def test_valid_row_logic(self):
        """
        Should return an empty string when cross-field logic is valid on row values.
        """
        # ARRANGE
        row_cases = [
            # quantity_zero: qty == 0 when item is blank
            (review.quantity_zero, RowV3(item="", qty="0")),

            # designator_required: designator non-empty when qty is integer >= 1
            (review.designator_required, RowV3(qty="2", designators="R1,R2")),

            # designator_count: count(designators) == integer qty
            (review.designator_count, RowV3(qty="3", designators="C1, C2, C3")),

            # unit_price_specified: unit_price > 0 when qty > 0
            (review.unit_price_specified, RowV3(qty="0.5", unit_price="0.01")),

            # subtotal_zero: sub_total == 0 when qty == 0
            (review.subtotal_zero, RowV3(qty="0", sub_total="0")),

            # sub_total_calculation: sub_total == qty * unit_price
            (review.sub_total_calculation, RowV3(qty="2", unit_price="3.25", sub_total="6.50")),
        ]
        expected = ""

        # ACT / ASSERT
        for func, row in row_cases:
            result = func(row)

            with self.subTest(func=func.__name__, In=row, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_row_logic(self):
        """
        Should return a non-empty string when cross-field logic is not valid on row values.
        """
        # ARRANGE
        row_cases = [
            # quantity_zero: invalid when item is blank and qty != 0
            (review.quantity_zero, RowV3(item="", qty="1")),

            # designator_required: invalid when qty integer >= 1 and designator is blank
            (review.designator_required, RowV3(qty="1", designators="")),

            # designator_count: invalid when count(designators) != integer qty
            (review.designator_count, RowV3(qty="3", designators="C1,C2")),

            # unit_price_specified: invalid when qty > 0 and unit_price <= 0
            (review.unit_price_specified, RowV3(qty="1", unit_price="0")),

            # subtotal_zero: invalid when qty == 0 and sub_total != 0
            (review.subtotal_zero, RowV3(qty="0", sub_total="0.01")),

            # sub_total_calculation: invalid when sub_total != qty * unit_price
            (review.sub_total_calculation, RowV3(qty="2", unit_price="0.2", sub_total="0.5")),
        ]

        # ACT / ASSERT
        for func, row in row_cases:
            result = func(row)

            with self.subTest(func=func.__name__, In=row, Out=result):
                self.assertIsNot(result, "")

    def test_valid_header_logic(self):
        """
        Should return a non-empty string when cross-cell logic fails on row and header values.
        """
        # ARRANGE
        rows = [
            RowV3(sub_total="0.50"),
            RowV3(sub_total="0.50"),
            RowV3(sub_total="0.00"),  # include a zero to ensure aggregation works
        ]
        header = HeaderV3(material_cost="1.00", overhead_cost="0.25", total_cost="1.25")

        valid_cases = [
            # material_cost == sum(sub_totals)
            (review.material_cost_calculation, (rows, header)),
            # total_cost == material_cost + overhead_cost
            (review.total_cost_calculation, (header,)),
        ]
        expected = ""  # no error

        # ACT / ASSERT
        for func, args in valid_cases:
            try:
                func(*args)  # should not raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            with self.subTest(func=func.__name__, In=args, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_header_logic(self):
        """
        Should return a non-empty string when cross-field logic is not valid on header values.
        """
        # ARRANGE
        rows = [
            RowV3(sub_total="0.50"),
            RowV3(sub_total="0.50"),
        ]
        header_wrong_material = HeaderV3(material_cost="1.10", overhead_cost="0.25", total_cost="1.25")
        header_wrong_total = HeaderV3(material_cost="1.00", overhead_cost="0.25", total_cost="1.20")

        invalid_cases = [
            # material_cost != sum(sub_totals)
            (review.material_cost_calculation, (rows, header_wrong_material)),
            # total_cost != material_cost + overhead_cost
            (review.total_cost_calculation, (header_wrong_total,)),
        ]

        for func, args in invalid_cases:
            # ACT
            result = func(*args)

            # ASSERT
            with self.subTest(func=func.__name__, In=args, Out=result):
                self.assertIsNot(result, "")


if __name__ == "__main__":
    unittest.main()
