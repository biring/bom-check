"""
Unit tests for the Version 3 BOM checker.

Covers row, header, and BOM-level validations, ensuring value checks and cross-field logic integrate correctly.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/checkers/test__bom.py

    # Direct discovery (runs all tests in the tree):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.9

Design Notes & Assumptions:
    - Valid BOMs must yield an empty string.
    - Invalid BOMs must yield a non-empty diagnostics string.
    - Tests assert surface behavior only, not internal ErrorLog details.

License:
 - Internal Use Only
"""

import unittest
from dataclasses import replace

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

from src.common import ChangeLog as IssueLog
# noinspection PyProtectedMember
from src.checkers import _v3_bom as bck
from tests.fixtures import v3_bom as bfx
from tests.fixtures import v3_value as vfx

# Constants
MODULE_NAME = "TestModule"
FILE_NAME = "TestDataFile"
SHEET_NAME = "TestSheet"
SECTION_NAME = "TestSection"


class TestCheckRowValue(unittest.TestCase):
    """
    Unit tests for `_check_row_value` (cell-level validations only).
    """

    def setUp(self):
        self.issues = IssueLog()
        self.issues.set_module_name(MODULE_NAME)
        self.issues.set_file_name(FILE_NAME)
        self.issues.set_sheet_name(SHEET_NAME)
        self.issues.set_section_name(SECTION_NAME)

    def test_valid_rows(self):
        """
        Should return no errors when all row cell values are valid.
        """
        # ARRANGE
        rows = bfx.BOARD_A.rows
        expected = 0  # No errors

        for row in rows:
            # ACT
            bck._check_row_value(self.issues, row)
            result = len(self.issues.render())
            # ASSERT
            with self.subTest("Number of issues", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_row(self):
        """
        Should return one error per invalid field when a row contains multiple invalid cell values.
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
        expected_errors = (
            TableLabelsV3.ITEM,
            TableLabelsV3.COMPONENT_TYPE,
            TableLabelsV3.DEVICE_PACKAGE,
            TableLabelsV3.DESCRIPTION,
            TableLabelsV3.UNITS,
            TableLabelsV3.CLASSIFICATION,
            TableLabelsV3.MFG_NAME,
            TableLabelsV3.MFG_PART_NO,
            TableLabelsV3.UL_VDE_NO,
            TableLabelsV3.VALIDATED_AT,
            TableLabelsV3.QUANTITY,
            TableLabelsV3.DESIGNATORS,
            TableLabelsV3.UNIT_PRICE,
            TableLabelsV3.SUB_TOTAL,
        )

        for row, expected in zip(rows, expected_errors):
            self.setUp()  # reset error logs

            # ACT
            bck._check_row_value(self.issues, row)
            issues = self.issues.render()

            # ASSERT
            with self.subTest("Number of issues", Out=len(issues), Exp="!=0"):
                self.assertNotEqual(len(issues), 0)

            for issue in issues:
                with self.subTest("Issue string contains", Out=issue, Exp=expected):
                    self.assertIn(expected, issue)


class TestCheckRowLogic(unittest.TestCase):
    """
    Unit tests for `_check_row_logic` (cross-field validations).
    """

    def setUp(self):
        self.issues = IssueLog()
        self.issues.set_module_name(MODULE_NAME)
        self.issues.set_file_name(FILE_NAME)
        self.issues.set_sheet_name(SHEET_NAME)
        self.issues.set_section_name(SECTION_NAME)

    def test_valid_rows(self):
        """
        Should return no errors when all row cross-field relationships are valid.
        """
        # ARRANGE
        rows = bfx.BOARD_A.rows
        expected = 0  # No errors

        for row in rows:
            # ACT
            bck._check_row_logic(self.issues, row, is_cost_bom=True)
            result = len(self.issues.render())
            # ASSERT
            with self.subTest("Number of issues", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_rows_costed_bom(self):
        """
        Should return errors when rows violate cross-field rules (e.g., subtotal mismatch, missing designator).
        """
        # ARRANGE
        rows = (
            # quantity is zero when item is blank.
            replace(bfx.ROW_A_1, item="", qty="2"),
            # designator is specified when quantity is an integer more than zero.
            replace(bfx.ROW_A_1, qty="2", designators=""),
            # designator count equals quantity when quantity is a greater than zero integer
            replace(bfx.ROW_A_1, qty="2", designators="R1"),
            # unit price is greater than zero when quantity is greater than zero.
            replace(bfx.ROW_A_1, qty="2", unit_price="0"),
            # sub-total is zero when quantity is zero.
            replace(bfx.ROW_A_1, qty="0", sub_total="1"),
            # sub-total is the product of quantity and unit price.
            replace(bfx.ROW_A_1, qty="2", unit_price="0.1", sub_total="3")
        )
        expected_errors = (
            TableLabelsV3.QUANTITY,
            TableLabelsV3.DESIGNATORS,
            TableLabelsV3.DESIGNATORS,
            TableLabelsV3.UNIT_PRICE,
            TableLabelsV3.SUB_TOTAL,
            TableLabelsV3.SUB_TOTAL
        )

        for row, expected in zip(rows, expected_errors):
            self.setUp()  # reset error logs
            # ACT
            bck._check_row_logic(self.issues, row, is_cost_bom=True)
            issues = self.issues.render()

            # ASSERT
            with self.subTest("Number of issues", Out=len(issues), Exp="!=0"):
                self.assertNotEqual(len(issues), 0)

            for issue in issues:
                with self.subTest("Issue string contains", Out=issue, Exp=expected):
                    self.assertIn(expected, issue)

    def test_invalid_rows_not_costed_bom(self):
        """
        Should skip unit price specified rule for not a costed bom while keeping other cross-field checks.
        """
        # ARRANGE
        rows = (
            # quantity is zero when item is blank.
            replace(bfx.ROW_A_1, item="", qty="2"),
            # designator is specified when quantity is an integer more than zero.
            replace(bfx.ROW_A_1, qty="2", designators=""),
            # designator count equals quantity when quantity is a greater than zero integer
            replace(bfx.ROW_A_1, qty="2", designators="R1"),
            # sub-total is zero when quantity is zero.
            replace(bfx.ROW_A_1, qty="0", sub_total="1"),
            # sub-total is the product of quantity and unit price.
            replace(bfx.ROW_A_1, qty="2", unit_price="0.1", sub_total="3")
        )
        expected_errors = (
            TableLabelsV3.QUANTITY,
            TableLabelsV3.DESIGNATORS,
            TableLabelsV3.DESIGNATORS,
            TableLabelsV3.SUB_TOTAL,
            TableLabelsV3.SUB_TOTAL
        )

        for row, expected in zip(rows, expected_errors):
            self.setUp()  # reset error logs
            # ACT
            bck._check_row_logic(self.issues, row, is_cost_bom=False)
            issues = self.issues.render()

            # ASSERT
            with self.subTest("Number of issues", Out=len(issues), Exp="!=0"):
                self.assertNotEqual(len(issues), 0)

            for issue in issues:
                with self.subTest("Issue string contains", Out=issue, Exp=expected):
                    self.assertIn(expected, issue)

    def test_unit_price_not_required_for_not_costed_bom(self):
        """
        Should not report unit price errors for not costed bom when quantity is greater than zero.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, qty="2", unit_price="0", sub_total="0")

        # ACT
        bck._check_row_logic(self.issues, row, False)
        issues = self.issues.render()

        # ASSERT
        with self.subTest("Number of issues", Out=len(issues), Exp=0):
            self.assertEqual(len(issues), 0)


class TestCheckHeaderValue(unittest.TestCase):
    """
    Unit tests for `_check_header_value` (header-level validations).
    """

    def setUp(self):
        self.issues = IssueLog()
        self.issues.set_module_name(MODULE_NAME)
        self.issues.set_file_name(FILE_NAME)
        self.issues.set_sheet_name(SHEET_NAME)
        self.issues.set_section_name(SECTION_NAME)

    def test_valid_header(self):
        """
        Should return no errors when all header fields are valid.
        """
        # ARRANGE
        header = bfx.BOARD_A.header
        expected = 0  # No errors

        # ACT
        bck._check_header_value(self.issues, header)
        result = len(self.issues.render())
        # ASSERT
        with self.subTest("Number of issues", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_header(self):
        """
        Should return one error per invalid header field when cell values are invalid.
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
        expected_errors = (
            HeaderLabelsV3.MODEL_NO,
            HeaderLabelsV3.BOARD_NAME,
            HeaderLabelsV3.BOARD_SUPPLIER,
            HeaderLabelsV3.BUILD_STAGE,
            HeaderLabelsV3.BOM_DATE,
            HeaderLabelsV3.MATERIAL_COST,
            HeaderLabelsV3.OVERHEAD_COST,
            HeaderLabelsV3.TOTAL_COST,
        )

        for header, expected in zip(headers, expected_errors):
            self.setUp()  # reset error logs

            # ACT
            bck._check_header_value(self.issues, header)
            issues = self.issues.render()

            # ASSERT
            with self.subTest("Number of issues", Out=len(issues), Exp="!=0"):
                self.assertNotEqual(len(issues), 0)

            for issue in issues:
                with self.subTest("Issue string contains", Out=issue, Exp=expected):
                    self.assertIn(expected, issue)


class TestCheckHeaderLogic(unittest.TestCase):
    """
    Unit tests for `_check_header_logic` (cross-field header validations).
    """

    def setUp(self):
        self.issues = IssueLog()
        self.issues.set_module_name(MODULE_NAME)
        self.issues.set_file_name(FILE_NAME)
        self.issues.set_sheet_name(SHEET_NAME)
        self.issues.set_section_name(SECTION_NAME)

    def test_valid(self):
        """
        Should return no errors when header cross-field relationships are valid.
        """
        # ARRANGE
        bom = bfx.BOM_B
        expected = 0  # No errors

        for board in bom.boards:
            # ACT
            bck._check_header_logic(self.issues, board.header, board.rows)
            result = len(self.issues.render())

            # ASSERT
            with self.subTest("Number of issues", Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid(self):
        """
        Should return at least one error when a header violates a cross-field rule.
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
        expected_errors = [
            HeaderLabelsV3.MATERIAL_COST,
            HeaderLabelsV3.TOTAL_COST,
        ]

        for board, expected in zip(bom.boards, expected_errors):
            self.setUp()  # reset error logs

            # ACT
            bck._check_header_logic(self.issues, board.header, board.rows)
            issues = self.issues.render()

            # ASSERT
            with self.subTest("Number of issues", Out=len(issues), Exp="!=0"):
                self.assertNotEqual(len(issues), 0)

            for issue in issues:
                with self.subTest("Issue string contains", Out=issue, Exp=expected):
                    self.assertIn(expected, issue)


class TestCheckBom(unittest.TestCase):
    """
    Unit tests for `check_bom` (BOM-level aggregation).
    """

    def test_valid_bom(self):
        """
        Should return an empty diagnostics string when all boards (headers and rows) are valid.
        """
        # ARRANGE
        bom = bfx.BOM_A
        expected = 0  # No errors => empty diagnostics

        # ACT
        issues = bck.check_v3_bom(bom)
        result = len(issues)

        # ASSERT
        with self.subTest("Number of issues", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_bom(self):
        """
        Should return a non-empty diagnostics string when any board has invalid header or row values.
        """
        # ARRANGE
        # Make board material_cost and total_cost inconsistent.
        bom = replace(
            bfx.BOM_A,
            boards=(
                replace(
                    bfx.BOARD_A,
                    header=replace(bfx.BOARD_A.header, material_cost="99.99", total_cost="9.90"),
                ),
            ),
        )
        expected_errors = [
            HeaderLabelsV3.MATERIAL_COST,
            HeaderLabelsV3.TOTAL_COST,
        ]

        # ACT
        issues = bck.check_v3_bom(bom)

        # ASSERT
        with self.subTest("Number of issues", Out=len(issues), Exp="!=0"):
            self.assertNotEqual(len(issues), 0)

        for issue, expected in zip(issues, expected_errors):
            with self.subTest("Issue string contains", Out=issue, Exp=expected):
                self.assertIn(expected, issue)


if __name__ == "__main__":
    unittest.main()
