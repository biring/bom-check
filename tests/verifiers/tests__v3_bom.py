"""
Unit tests for Version 3 BOM verification orchestrator.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/verifiers/tests__v3_bom.py

    # Direct discovery (runs all tests):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses, unittest.mock
    - Internal Modules: src.verifiers._v3_bom, src.approve.interfaces, test fixtures

Notes:
    - Tests rely on static fixtures to represent valid and invalid BOM structures.
    - Tests assert fail-fast behavior and wrapped exception types.
    - Only error type is asserted; full message text is not validated.
    - Internal-only test suite for the BOM parsing and approval pipeline.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace
from unittest.mock import patch
from src.approve import interfaces as approve  # for patch
# noinspection PyProtectedMember
from src.verifiers import _v3_bom as verify  # Module under test
from tests.fixtures import v3_bom as bfx  # Fixtures for test
from tests.fixtures import v3_value as vfx  # Fixtures for test


def _raise_type_error():
    raise TypeError("Raise an error for testing. ")


class TestVerifyHeaderValue(unittest.TestCase):
    """
    Unit tests for `_verify_header_value`.
    """

    def test_happy_path(self):
        """
        Should NOT raise any exception when all header fields are valid.
        """
        # ARRANGE
        header = bfx.BOARD_A.header

        # ACT
        try:
            verify._verify_header_value(header)
            actual = ""
        except Exception as ex:
            actual = type(ex).__name__

        # ASSERT
        with self.subTest("No exception", Out=actual):
            self.assertEqual(actual, "")

    def test_incorrect_value(self):
        """
        Should raise ValueError when any header field contains an invalid value.
        """
        # ARRANGE
        headers = (
            replace(bfx.HEADER_A, model_no=vfx.MODEL_NO_BAD[0]),
            replace(bfx.HEADER_A, board_name=vfx.BOARD_NAME_BAD[0]),
            replace(bfx.HEADER_A, board_supplier=vfx.BOARD_SUPPLIER_BAD[0]),
            replace(bfx.HEADER_A, build_stage=vfx.BUILD_STAGE_BAD[0]),
            replace(bfx.HEADER_A, bom_date=vfx.BOM_DATE_BAD[0]),
            replace(bfx.HEADER_A, material_cost=vfx.COST_BAD[0]),
            replace(bfx.HEADER_A, overhead_cost=vfx.COST_BAD[1]),
            replace(bfx.HEADER_A, total_cost=vfx.COST_BAD[2]),
        )

        expected = ValueError.__name__

        for header in headers:
            # ACT
            try:
                verify._verify_header_value(header)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)

    def test_unexpected_error(self):
        """
        Should raise RuntimeError when a header check function raises an unexpected exception.
        """

        # ARRANGE
        header = bfx.BOARD_A.header
        expected = RuntimeError.__name__

        with patch.object(approve, "model_number", new=_raise_type_error):

            # ACT
            try:
                verify._verify_header_value(header)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)


class TestVerifyHeaderLogic(unittest.TestCase):
    """
    Unit tests for `_verify_header_logic`.
    """

    def test_happy_path(self):
        """
        Should NOT raise any exception when header totals match row data.
        """
        # ARRANGE
        bom = bfx.BOM_B

        for board in bom.boards:

            # ACT
            try:
                verify._verify_header_logic(board.header, board.rows)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("No exception", Out=actual):
                self.assertEqual(actual, "")

    def test_incorrect_value(self):
        """
        Should raise ValueError when header logic rules fail.
        """
        # ARRANGE
        bom = replace(
            bfx.BOM_B,
            boards=(
                replace(
                    bfx.BOARD_B1,
                    header=replace(
                        bfx.BOARD_B1.header,
                        material_cost="99.99",
                    ),
                ),
                replace(
                    bfx.BOARD_B2,
                    header=replace(
                        bfx.BOARD_B2.header,
                        total_cost="9.90",
                    ),
                ),
            ),
        )

        expected = ValueError.__name__

        for board in bom.boards:
            # ACT
            try:
                verify._verify_header_logic(board.header, board.rows)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)

    def test_unexpected_error(self):
        """
        Should raise RuntimeError when a logic-check function raises an unexpected exception.
        """
        # ARRANGE
        board = bfx.BOARD_A
        expected = RuntimeError.__name__

        with patch.object(approve, "material_cost_calculation", new=_raise_type_error):

            # ACT
            try:
                verify._verify_header_logic(board.header, board.rows)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)


class TestVerifyRowValue(unittest.TestCase):
    """
    Unit tests for `_verify_row_value`.
    """

    def test_happy_path(self):
        """
        Should NOT raise any exception when all row fields are valid.
        """
        # ARRANGE
        rows = bfx.BOARD_A.rows

        for row in rows:
            # ACT
            try:
                verify._verify_row_value(row)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("No exception", Out=actual):
                self.assertEqual(actual, "")

    def test_incorrect_value(self):
        """
        Should raise ValueError when any row field contains an invalid value.
        """
        # ARRANGE
        rows = (
            replace(bfx.ROW_A_1, item=vfx.ITEM_BAD[0]),
            replace(bfx.ROW_A_1, component_type=vfx.COMP_TYPE_BAD[0]),
            replace(bfx.ROW_A_1, device_package=vfx.DEVICE_PACKAGE_BAD[0]),
            replace(bfx.ROW_A_1, description=vfx.DESCRIPTION_BAD[0]),
            replace(bfx.ROW_A_1, units=vfx.UNITS_BAD[0]),
            replace(bfx.ROW_A_1, classification=vfx.CLASSIFICATION_BAD[0]),
            replace(bfx.ROW_A_1, mfg_name=vfx.MFG_NAME_BAD[0]),
            replace(bfx.ROW_A_1, mfg_part_number=vfx.MFG_PART_NO_BAD[0]),
            replace(bfx.ROW_A_1, ul_vde_number=vfx.UL_VDE_NO_BAD[0]),
            replace(bfx.ROW_A_1, validated_at=vfx.VALIDATED_AT_BAD[0]),
            replace(bfx.ROW_A_1, qty=vfx.QUANTITY_BAD[0]),
            replace(bfx.ROW_A_1, designators=vfx.DESIGNATOR_BAD[0]),
            replace(bfx.ROW_A_1, unit_price=vfx.PRICE_BAD[0]),
            replace(bfx.ROW_A_1, sub_total=vfx.PRICE_BAD[0]),
        )
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                verify._verify_row_value(row)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)

    def test_unexpected_error(self):
        """
        Should raise RuntimeError when a row field check function raises an unexpected exception.
        """
        # ARRANGE
        row = bfx.ROW_A_1
        expected = RuntimeError.__name__

        with patch.object(approve, "classification", new=_raise_type_error):
            # ACT
            try:
                verify._verify_row_value(row)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)


class TestVerifyRowLogic(unittest.TestCase):
    """
    Unit tests for `_verify_row_logic`.
    """

    def test_happy_path(self):
        """
        Should NOT raise any exception when row logic rules pass.
        """
        # ARRANGE
        cases = (
            # test for costed bom
            (bfx.ROW_A_1, True),
            (bfx.ROW_A_1_ALT1, True),
            (bfx.ROW_A_1_ALT2, True),
            (bfx.ROW_A_2, True),
            (bfx.ROW_A_2_ALT, True),
            (bfx.ROW_A_3, True),
            (bfx.ROW_A_4, True),
            # test for not cost bom
            (bfx.ROW_A_1, False),
            (bfx.ROW_A_1_ALT1, False),
            (bfx.ROW_A_1_ALT2, False),
            (bfx.ROW_A_2, False),
            (bfx.ROW_A_2_ALT, False),
            (bfx.ROW_A_3, False),
            (bfx.ROW_A_4, False),
            # unit price not required for not costed bom
            (replace(bfx.ROW_A_1, unit_price="0", sub_total="0"), False),
        )

        for row, is_costed_bom in cases:
            # ACT
            try:
                verify._verify_row_logic(row, is_costed_bom)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("No exception", Out=actual):
                self.assertEqual(actual, "")

    def test_incorrect_value(self):
        """
        Should raise ValueError when row logic rules are violated.
        """
        # ARRANGE
        cases = (
            # --- cost bom cases ---
            # quantity is zero when item is blank.
            (replace(bfx.ROW_A_1, item="", qty="2"), True),
            # designator is specified when quantity is an integer more than zero.
            (replace(bfx.ROW_A_1, qty="2", designators=""), True),
            # designator count equals quantity when quantity is a greater than zero integer
            (replace(bfx.ROW_A_1, qty="2", designators="R1"), True),
            # unit price is greater than zero when quantity is greater than zero.
            (replace(bfx.ROW_A_1, qty="2", unit_price="0"), True),
            # sub-total is zero when quantity is zero.
            (replace(bfx.ROW_A_1, qty="0", sub_total="1"), True),
            # sub-total is the product of quantity and unit price.
            (replace(bfx.ROW_A_1, qty="2", unit_price="0.1", sub_total="3"), True),

            # --- not cost bom cases ---
            # quantity is zero when item is blank.
            (replace(bfx.ROW_A_1, item="", qty="2"), False),
            # designator is specified when quantity is an integer more than zero.
            (replace(bfx.ROW_A_1, qty="2", designators=""), False),
            # designator count equals quantity when quantity is a greater than zero integer
            (replace(bfx.ROW_A_1, qty="2", designators="R1"), False),
            # sub-total is zero when quantity is zero.
            (replace(bfx.ROW_A_1, qty="0", sub_total="1"), False),
            # sub-total is the product of quantity and unit price.
            (replace(bfx.ROW_A_1, qty="2", unit_price="0.1", sub_total="3"), False),
        )
        expected = ValueError.__name__

        for row, is_costed_bom in cases:
            # ACT
            try:
                verify._verify_row_logic(row, is_costed_bom)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)

    def test_unexpected_error(self):
        """
        Should raise RuntimeError when a row-logic function raises an unexpected exception.
        """
        # ARRANGE
        row = bfx.ROW_A_1
        expected = RuntimeError.__name__

        with patch.object(approve, "designator_count", new=_raise_type_error):
            # ACT
            try:
                verify._verify_row_logic(row, is_cost_bom=True)
                actual = ""
            except Exception as ex:
                actual = type(ex).__name__

            # ASSERT
            with self.subTest("Raise exception", Out=actual, Expected=expected):
                self.assertEqual(actual, expected)


class TestVerifyV3Bom(unittest.TestCase):
    """
    Unit tests for `verify_v3_bom`.
    """

    def test_happy_path(self):
        """
        Should NOT raise any exception when the BOM is valid.
        """
        # ARRANGE
        bom = bfx.BOM_A

        # ACT
        try:
            verify.verify_v3_bom(bom)
            actual = ""
        except Exception as ex:
            actual = type(ex).__name__

        # ASSERT
        with self.subTest("No exception", Out=actual):
            self.assertEqual(actual, "")

    def test_incorrect_value(self):
        """
        Should raise ValueError when any board violates a BOM-level rule.
        """
        # ARRANGE
        # Make board material cost incorrect.
        bom = replace(
            bfx.BOM_A,
            boards=(
                replace(
                    bfx.BOARD_A,
                    header=replace(bfx.BOARD_A.header, material_cost="99.99"),
                ),
            ),
        )
        expected = ValueError.__name__

        # ACT
        try:
            verify.verify_v3_bom(bom)
            actual = ""
        except Exception as ex:
            actual = type(ex).__name__

        # ASSERT
        with self.subTest("Raise exception", Out=actual, Expected=expected):
            self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
