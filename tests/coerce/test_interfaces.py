"""
Smoke tests for the public `coerce` interface façade.

These tests validate that all exposed coercer functions in `src.coerce.interfaces`:
    - Return expected normalized values for valid BOM inputs
    - Produce no log entries when input data is already clean
    - Generate exactly one log entry when a change occurs (e.g., whitespace cleanup)

Example Usage:
    # Run this test module directly:
    python -m unittest tests/coerce/test_interfaces.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest
    - Internal: src.coerce.interfaces, tests.fixtures.v3_bom

Notes:
    - These are high-level smoke tests for API surface validation, not rule-level checks.
    - Verifies public import integrity and ensures consistent façade behavior across fields.
    - Each test iterates over all header and row coercers re-exported by `interfaces`.

License:
    - Internal Use Only
"""

import unittest

from tests.fixtures import v3_bom as bfx

from src.coerce import interfaces as coerce


class TestInterface(unittest.TestCase):
    """
    Smoke tests for coerce public interface.
    """
    cases = (
        (coerce.model_number, bfx.HEADER_A.model_no),
        (coerce.board_name, bfx.HEADER_A.board_name),
        (coerce.board_supplier, bfx.HEADER_A.board_supplier),
        (coerce.build_stage, bfx.HEADER_A.build_stage),
        (coerce.bom_date, bfx.HEADER_A.bom_date),
        (coerce.material_cost, bfx.HEADER_A.material_cost),
        (coerce.overhead_cost, bfx.HEADER_A.overhead_cost),
        (coerce.total_cost, bfx.HEADER_A.total_cost),
        (coerce.item, bfx.ROW_A_1.item),
        (coerce.component_type, bfx.ROW_A_1.component_type),
        (coerce.device_package, bfx.ROW_A_1.device_package),
        (coerce.description, bfx.ROW_A_1.description),
        (coerce.units, bfx.ROW_A_1.units),
        (coerce.classification, bfx.ROW_A_1.classification),
        (coerce.manufacturer, bfx.ROW_A_1.mfg_name),
        (coerce.mfg_part_number, bfx.ROW_A_1.mfg_part_number),
        (coerce.ul_vde_number, bfx.ROW_A_1.ul_vde_number),
        (coerce.validated_at, bfx.ROW_A_1.validated_at),
        (coerce.quantity, bfx.ROW_A_1.qty),
        (coerce.designator, bfx.ROW_A_1.designators),
        (coerce.unit_price, bfx.ROW_A_1.unit_price),
        (coerce.sub_total, bfx.ROW_A_1.sub_total),
    )

    def test_unchanged(self):
        """
        Should return the same value and not generate any logs.
        """
        # ARRANGE
        cases = self.cases

        for func, expected in cases:
            # ACT
            str_in = expected  # We do not expect any changes
            result, log = func(str_in)

            # ASSERT
            with self.subTest(func.__name__, Out=result, Exp=expected):
                self.assertEqual(result, expected, str_in)
            with self.subTest("Log size", Out=len(log), Exp=0):
                self.assertEqual(len(log), 0, log)

    def test_changed(self):
        """
        Should return coerced value and generate log.
        """
        # ARRANGE
        cases = self.cases

        for func, expected in cases:
            # ACT
            str_in = "\t" + expected + "\n"  # tab and new line is cleaned out during coercion
            result, log = func(str_in)

            # ASSERT
            with self.subTest(func.__name__, Out=result, Exp=expected):
                self.assertEqual(expected, result, str_in)
            with self.subTest("Log size", Out=len(log), Exp=1):
                self.assertEqual(len(log), 1, log)


if __name__ == "__main__":
    unittest.main()
