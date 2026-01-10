"""
Unit tests for the public interfaces of the `approve` package.

This module exercises representative valid and invalid paths across the validators exposed via `src.approve.interfaces`. It provides smoke coverage for the public API and ensures consistent exception behavior on malformed inputs.

Example Usage:
    # Preferred run from project root:
    python -m unittest tests/approve/test_interfaces.py

    # Discover all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - Internal: src.approve.interfaces, src.models.interfaces
    - External Packages: None

Notes:
    - Focus on availability, basic callability, and minimal behavioral checks; deep logic is covered in module-specific tests.
    - Valid-case tests confirm silent acceptance of clearly correct examples.
    - Invalid-case tests cover common malformed or out-of-range inputs, expecting `ValueError`.
    - This module treats `src.approve.interfaces` as the public API surface.
"""

import unittest

import src.approve.interfaces as approve
from src.models.interfaces import (
    HeaderV3,
    RowV3,
)


class TestRowV3(unittest.TestCase):
    """
    Smoke and negative tests for Row validators in the public interface.
    """

    def test_valid_inputs(self):
        """
        Should run without raising on valid Row values.
        """
        # ARRANGE
        cases = [
            (approve.item, "23"),
            (approve.component_type, "Diode/SCR"),
            (approve.device_package, "0603"),
            (approve.description, "1k,1%,0.5W"),  # no spaces
            (approve.units, "PCS"),
            (approve.classification, "A"),
            (approve.mfg_name, "ST Microelectronics"),
            (approve.mfg_part_no, "SN74HC595N-TR"),
            (approve.ul_vde_number, "E1234"),
            (approve.validated_at, "P1/EB0/MP"),
            (approve.quantity, "3.5"),
            (approve.designator, "R12"),
            (approve.unit_price, "0.05"),
            (approve.sub_total, "1.25"),
        ]
        expected = ""  # no error

        for func, value in cases:
            # ACT
            try:
                func(value)  # should not raise
                result = ""  # No error
            except Exception as e:  # noqa: BLE001 - explicit failure for any exception
                result = e.__class__.__name__

            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        Should raise ValueError on invalid Row values.
        """
        # ARRANGE
        cases = [
            (approve.item, "-1"),  # negative not allowed
            (approve.component_type, "123"),  # not alphabetic style / ALT*
            (approve.device_package, "QFN 32"),  # space likely invalid (expects alnum / dash)
            (approve.description, ""),  # empty not allowed
            (approve.units, "pcs.."),  # trailing punctuation invalid form
            (approve.classification, "Z"),  # only A/B/C
            (approve.mfg_name, ""),  # empty not allowed
            (approve.mfg_part_no, ""),  # empty not allowed
            (approve.ul_vde_number, "12AB"),  # must start letters then digits
            (approve.validated_at, "X1"),  # not in allowed tokens
            (approve.quantity, "-0.1"),  # non-negative only
            (approve.designator, "1R"),  # must start with letters
            (approve.unit_price, "-5"),  # non-negative only
            (approve.sub_total, "-0.01"),  # non-negative only
        ]
        expected = ValueError.__name__

        for func, value in cases:
            # ACT
            try:
                func(value)  # should raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            # ASSERT
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestHeaderV3(unittest.TestCase):
    """
    Smoke and negative tests for header validators in the public interface.

    """

    def test_valid_inputs(self):
        """
        Should run without raising on representative valid values.
        """
        # ARRANGE
        cases = [
            (approve.model_number, "AB123"),
            (approve.board_name, "Main Control PCBA"),
            (approve.board_supplier, "ACME Boards"),
            (approve.build_stage, "EB1"),
            (approve.bom_date, "2025-08-06"),
            (approve.material_cost, "12.50"),
            (approve.overhead_cost, "0.50"),
            (approve.total_cost, "13.00"),
        ]
        expected = ""  # no error

        # ACT / ASSERT
        for func, value in cases:
            try:
                func(value)  # should not raise
                result = ""  # No error
            except Exception as e:  # noqa: BLE001 - explicit failure for any exception
                result = e.__class__.__name__

            # ASSERT with PyCharm-friendly subTest output labels
            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_inputs(self):
        """
        Should raise ValueError on representative invalid values.
        """
        # ARRANGE
        cases = [
            (approve.model_number, "1A"),  # must start with 2–3 letters then digits
            (approve.board_name, "Main Control PCB"),  # must end with "PCBA"
            (approve.board_supplier, "ac"),  # too short / must start capital
            (approve.build_stage, "ALPHA"),  # not an allowed token
            (approve.bom_date, "2025.08.06"),  # unsupported format
            (approve.material_cost, "-1.0"),  # non-negative only
            (approve.overhead_cost, "-0.01"),  # non-negative only
            (approve.total_cost, "-2.0"),  # non-negative only
        ]
        expected = ValueError.__name__

        # ACT / ASSERT
        for func, value in cases:
            try:
                func(value)  # should raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            with self.subTest(func=func.__name__, In=value, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestApproveInterfacesCellLogic(unittest.TestCase):
    """
    Smoke and negative tests for cross-field logic validators in the public interface.

    Valid cases must run without raising exceptions. Invalid cases must raise ValueError.
    """

    def test_valid_row_logic(self):
        """
        Should run without raising for representative valid rows.
        """
        # ARRANGE
        row_cases = [
            # quantity_zero: qty == 0 when item is blank
            (approve.quantity_zero, RowV3(item="", qty="0")),

            # designator_required: designator non-empty when qty is integer >= 1
            (approve.designator_required, RowV3(qty="2", designators="R1,R2")),

            # designator_count: count(designators) == integer qty
            (approve.designator_count, RowV3(qty="3", designators="C1, C2, C3")),

            # unit_price_specified: unit_price > 0 when qty > 0
            (approve.unit_price_specified, RowV3(qty="0.5", unit_price="0.01")),

            # subtotal_zero: sub_total == 0 when qty == 0
            (approve.subtotal_zero, RowV3(qty="0", sub_total="0")),

            # sub_total_calculation: sub_total == qty * unit_price
            (approve.sub_total_calculation, RowV3(qty="2", unit_price="3.25", sub_total="6.50")),
        ]
        expected = ""  # no error

        # ACT / ASSERT
        for func, row in row_cases:
            try:
                func(row)  # should not raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            with self.subTest(func=func.__name__, In=row, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_row_logic(self):
        """
        Should raise ValueError for representative invalid rows.
        """
        # ARRANGE
        row_cases = [
            # quantity_zero: invalid when item is blank and qty != 0
            (approve.quantity_zero, RowV3(item="", qty="1")),

            # designator_required: invalid when qty integer >= 1 and designator is blank
            (approve.designator_required, RowV3(qty="1", designators="")),

            # designator_count: invalid when count(designators) != integer qty
            (approve.designator_count, RowV3(qty="3", designators="C1,C2")),

            # unit_price_specified: invalid when qty > 0 and unit_price <= 0
            (approve.unit_price_specified, RowV3(qty="1", unit_price="0")),

            # subtotal_zero: invalid when qty == 0 and sub_total != 0
            (approve.subtotal_zero, RowV3(qty="0", sub_total="0.01")),

            # sub_total_calculation: invalid when sub_total != qty * unit_price
            (approve.sub_total_calculation, RowV3(qty="2", unit_price="0.2", sub_total="0.5")),
        ]
        expected = ValueError.__name__

        # ACT / ASSERT
        for func, row in row_cases:
            try:
                func(row)  # should raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            with self.subTest(func=func.__name__, In=row, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_header_logic(self):
        """
        Should run without raising for representative valid header calculations.
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
            (approve.material_cost_calculation, (rows, header)),
            # total_cost == material_cost + overhead_cost
            (approve.total_cost_calculation, (header,)),
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
        Should raise ValueError for representative invalid header calculations.
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
            (approve.material_cost_calculation, (rows, header_wrong_material)),
            # total_cost != material_cost + overhead_cost
            (approve.total_cost_calculation, (header_wrong_total,)),
        ]
        expected = ValueError.__name__

        for func, args in invalid_cases:
            # ACT
            try:
                func(*args)  # should raise
                result = ""  # no error
            except Exception as e:  # noqa: BLE001
                result = e.__class__.__name__

            # ASSERT
            with self.subTest(func=func.__name__, In=args, Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
