"""
Unit tests for the Version 3 BOM fixer module.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/fixer/test__v3_bom.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing, unittest.mock
    - Internal Packages: src.fixer._v3_bom, src.fixer._types, src.models.interfaces

Notes:
    - Tests mock correction, CLI, and runtime interfaces to isolate orchestration from rule logic.
    - Fixtures under `tests.fixtures.v3_bom` provide deterministic BOM structures for comparison.
    - Focus is on structural integrity, logging accuracy, and controlled exception handling.

License:
    - Internal Use Only
"""
import unittest
from dataclasses import replace
from unittest.mock import patch
from src.common import ChangeLog

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)
from src.models.interfaces import (
    HeaderV3AttrNames,
    RowV3AttrNames,
)
from src.cli import interfaces as cli  # for patch at interface
# noinspection PyProtectedMember
from src.fixer import _v3_bom as fb  # Direct internal import — acceptable in tests
from tests.fixtures import v3_bom as bf


class TestFixV3Bom(unittest.TestCase):
    """
    Unit test for the `fix_v3_bom` function.
    """

    def test_valid(self):
        """
        Should NOT modify valid BOM data and return an empty change-log.
        """
        # ARRANGE
        cases = (
            (bf.BOM_B, True),
            (replace(bf.BOM_B, is_cost_bom=False), False),
        )

        for bom, expected_is_cost_bom in cases:
            # ACT
            out_bom, log = fb.fix_v3_bom(bom)

            # ASSERT
            with self.subTest("Log size", Out=len(log), Exp=0):
                self.assertEqual(len(log), 0, log)
            with self.subTest("Is Cost Bom", Out=out_bom.is_cost_bom, Exp=expected_is_cost_bom):
                self.assertEqual(out_bom.is_cost_bom, expected_is_cost_bom)
            with self.subTest("File Name", Out=out_bom.file_name, Exp=bf.BOM_B.file_name):
                self.assertEqual(out_bom.file_name, bf.BOM_B.file_name)

    def test_invalid(self):
        """
        Should apply corrections to a minimally dirty BOM and produce a non-empty change-log.
        """
        # ARRANGE (start clean and add space(s) to dirty up a field)
        in_bom = replace(
            bf.BOM_A, boards=(
                replace(
                    bf.BOARD_A, header=replace(
                        bf.BOARD_A.header, board_name=" " + bf.BOARD_A.header.board_name + " "
                    ),
                ),
            ),
        )

        with (
            patch.object(cli, "prompt_for_string_value") as p_prompt,
            patch.object(cli, "show_info"),
            patch.object(cli, "show_warning"),
        ):
            p_prompt.return_value = bf.HEADER_A.board_name

            # ACT
            out_bom, log = fb.fix_v3_bom(in_bom)

        # ASSERT (spot-check)
        board_name_in = in_bom.boards[0].header.board_name
        board_name_out = out_bom.boards[0].header.board_name
        with self.subTest("Coerced cell", In=board_name_in, Out=board_name_out):
            self.assertNotEqual(board_name_in, board_name_out)
        with self.subTest("Log size", Out=len(log), Exp=">0"):
            self.assertGreater(len(log), 0)

    def test_raise(self):
        """
        Should raise ValueError when a helper function fails during board reconstruction.
        """
        # ARRANGE
        src = bf.BOM_A
        expected = ValueError.__name__

        with patch.object(fb, "_fix_header_manual") as p_row:
            p_row.side_effect = ValueError("mapping failed")
            # ACT
            try:
                _ = fb.fix_v3_bom(src)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixHeaderManual(unittest.TestCase):
    """
    Unit test for the `_fix_header_manual` function.
    """

    def reset_log(self):
        self.log = ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep header values unchanged and produce no log entries.
        """
        # ARRANGE
        header_in = bf.HEADER_A

        # ACT
        self.reset_log()
        header_out = fb._fix_header_manual(self.log, header_in)
        log_length = len(self.log.render())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(header_out.__dict__.keys(), header_in.__dict__.values(),
                                                   header_out.__dict__.values(), header_in.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid_assisted(self):
        """
        Should prompt user to correct invalid header fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (HeaderLabelsV3.MODEL_NO, HeaderV3AttrNames.MODEL_NO, replace(bf.HEADER_A, model_no="#")),
            (HeaderLabelsV3.BOARD_NAME, HeaderV3AttrNames.BOARD_NAME, replace(bf.HEADER_A, board_name="#")),
        ]

        for label, attr_name, header_in in cases:
            prompt_response = getattr(bf.HEADER_A, attr_name)

            with (
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response

                # ACT
                self.reset_log()
                header_out = fb._fix_header_manual(self.log, header_in)
                str_in = getattr(header_in, attr_name)
                str_out = getattr(header_out, attr_name)
                str_exp = getattr(bf.HEADER_A, attr_name)
                log_list = self.log.render()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when header reconstruction fails due to invalid field mapping.
        """
        # ARRANGE
        header_in = replace(bf.HEADER_A, model_no="#")  # force an update to trigger mapping
        expected = ValueError.__name__

        with (
            patch.object(type(header_in), "__init__") as p_row,
            patch.object(cli, "prompt_for_string_value") as p_prompt,
            patch.object(cli, "show_info"),
            patch.object(cli, "show_warning"),
        ):
            p_prompt.return_value = bf.HEADER_A.model_no
            p_row.side_effect = TypeError("bad mapping")
            # ACT
            self.reset_log()
            try:
                _ = fb._fix_header_manual(self.log, header_in)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixHeaderAuto(unittest.TestCase):
    """
    Unit test for the `_fix_header_auto` function.
    """

    def reset_log(self):
        self.log = ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep header cost fields consistent and produce no log entries.
        """
        # ARRANGE
        board_in = bf.BOARD_A
        header_in = board_in.header

        # ACT
        self.reset_log()
        header_out = fb._fix_header_auto(self.log, board_in)
        log_length = len(self.log.render())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(header_out.__dict__.keys(), header_in.__dict__.values(),
                                                   header_out.__dict__.values(), header_in.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid(self):
        """
        Should automatically correct cost fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (
                HeaderLabelsV3.MATERIAL_COST,
                HeaderV3AttrNames.MATERIAL_COST,
                replace(bf.BOARD_A, header=replace(bf.BOARD_A.header, material_cost="99"))
            ),
            (
                HeaderLabelsV3.TOTAL_COST,
                HeaderV3AttrNames.TOTAL_COST,
                replace(bf.BOARD_A, header=replace(bf.BOARD_A.header, total_cost="99"))
            ),
        ]

        for label, attr_name, board_in in cases:
            header_in = board_in.header
            prompt_response = getattr(header_in, attr_name)

            with (
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response

                # ACT
                self.reset_log()
                header_out = fb._fix_header_auto(self.log, board_in)
                str_in = getattr(header_in, attr_name)
                str_out = getattr(header_out, attr_name)
                str_exp = getattr(bf.HEADER_A, attr_name)
                log_list = self.log.render()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when header reconstruction fails during automatic corrections.
        """
        # ARRANGE
        board_in = replace(
            bf.BOARD_A, header=replace(
                bf.BOARD_A.header, material_cost="99"
            )
        )
        header = board_in.header
        expected = ValueError.__name__

        with patch.object(type(header), "__init__") as p_row:
            p_row.side_effect = TypeError("bad mapping")
            # ACT
            self.reset_log()
            try:
                _ = fb._fix_header_auto(self.log, board_in)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixRowManual(unittest.TestCase):
    """
    Unit test for the `_fix_row_manual` function.
    """

    def setUp(self):
        self.log = ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep row values unchanged and produce no log entries.
        """
        # ARRANGE
        row = bf.ROW_A_1

        # ACT
        out_row = fb._fix_row_manual(self.log, row)
        log_length = len(self.log.render())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(out_row.__dict__.keys(), row.__dict__.values(),
                                                   out_row.__dict__.values(), row.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid_assisted(self):
        """
        Should prompt user to correct invalid row fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (TableLabelsV3.ITEM, RowV3AttrNames.ITEM, replace(bf.ROW_A_1, item="?")),
            (TableLabelsV3.COMPONENT_TYPE, RowV3AttrNames.COMPONENT_TYPE, replace(bf.ROW_A_1, component_type="?")),
            (TableLabelsV3.DEVICE_PACKAGE, RowV3AttrNames.DEVICE_PACKAGE, replace(bf.ROW_A_1, device_package="?")),
            (TableLabelsV3.DESCRIPTION, RowV3AttrNames.DESCRIPTION, replace(bf.ROW_A_1, description="")),
            (TableLabelsV3.UNITS, RowV3AttrNames.UNITS, replace(bf.ROW_A_1, units="?")),
            (TableLabelsV3.CLASSIFICATION, RowV3AttrNames.CLASSIFICATION, replace(bf.ROW_A_1, classification="?")),
            (TableLabelsV3.MFG_NAME, RowV3AttrNames.MFG_NAME, replace(bf.ROW_A_1, mfg_name="?")),
            (TableLabelsV3.MFG_PART_NO, RowV3AttrNames.MFG_PART_NO, replace(bf.ROW_A_1, mfg_part_number="?")),
            (TableLabelsV3.UL_VDE_NO, RowV3AttrNames.UL_VDE_NO, replace(bf.ROW_A_1, ul_vde_number="?")),
            (TableLabelsV3.VALIDATED_AT, RowV3AttrNames.VALIDATED_AT, replace(bf.ROW_A_1, validated_at="?")),
            (TableLabelsV3.QUANTITY, RowV3AttrNames.QTY, replace(bf.ROW_A_1, qty="?")),
            (TableLabelsV3.DESIGNATORS, RowV3AttrNames.DESIGNATORS, replace(bf.ROW_A_1, designators="?")),
            (TableLabelsV3.UNIT_PRICE, RowV3AttrNames.UNIT_PRICE, replace(bf.ROW_A_1, unit_price="?")),
        ]

        for label, attr_name, row_in in cases:
            self.setUp()
            prompt_response = getattr(bf.ROW_A_1, attr_name)

            with (
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response

                # ACT
                row_out = fb._fix_row_manual(self.log, row_in)
                str_in = getattr(row_in, attr_name)
                str_out = getattr(row_out, attr_name)
                str_exp = getattr(bf.ROW_A_1, attr_name)
                log_list = self.log.render()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when row reconstruction fails during manual corrections.
        """
        # ARRANGE
        row = replace(bf.ROW_A_1, item="?")
        attr_name = RowV3AttrNames.ITEM
        prompt_response = getattr(bf.ROW_A_1, attr_name)
        expected = ValueError.__name__

        with (
            patch.object(type(row), "__init__") as p_row,
            patch.object(cli, "prompt_for_string_value") as p_prompt,
            patch.object(cli, "show_info"),
            patch.object(cli, "show_warning"),
        ):
            p_row.side_effect = TypeError("bad mapping")
            p_prompt.return_value = prompt_response
            # ACT
            try:
                _ = fb._fix_row_manual(self.log, row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestFixRowAuto(unittest.TestCase):
    """
    Unit test for the `_fix_row_auto` function.
    """

    def setUp(self):
        self.log = ChangeLog()
        self.log.set_file_name("TestFile")
        self.log.set_sheet_name("TestSheet")
        self.log.set_section_name("TestSection")

    def test_valid(self):
        """
        Should keep row values unchanged and produce no log entries.
        """
        # ARRANGE
        row = bf.ROW_A_1

        # ACT
        out_row = fb._fix_row_auto(self.log, row)
        log_length = len(self.log.render())

        # ASSERT
        for field, str_in, str_out, str_exp in zip(out_row.__dict__.keys(), row.__dict__.values(),
                                                   out_row.__dict__.values(), row.__dict__.values()):
            with self.subTest(field, In=str_in, Out=str_out, Exp=str_exp):
                self.assertEqual(str_out, str_exp)

        with self.subTest("Empty Log", Out=log_length, Exp=0):
            self.assertEqual(log_length, 0)

    def test_invalid(self):
        """
        Should automatically correct invalid row fields and record corresponding log entries.
        """
        # ARRANGE
        cases = [
            (TableLabelsV3.COMPONENT_TYPE, RowV3AttrNames.COMPONENT_TYPE,
             replace(bf.ROW_A_1, component_type="SMD Resistor")),
            (TableLabelsV3.DESIGNATORS, RowV3AttrNames.DESIGNATORS, replace(bf.ROW_A_1, designators="R1-R2")),
            (TableLabelsV3.SUB_TOTAL, RowV3AttrNames.SUB_TOTAL, replace(bf.ROW_A_1, sub_total="999")),
        ]

        for label, attr_name, row_in in cases:
            self.setUp()
            prompt_response = getattr(bf.ROW_A_1, attr_name)

            with (
                patch.object(cli, "prompt_for_string_value") as p_prompt,
                patch.object(cli, "show_info"),
                patch.object(cli, "show_warning"),
            ):
                p_prompt.return_value = prompt_response

                # ACT
                row_out = fb._fix_row_auto(self.log, row_in)
                str_in = getattr(row_in, attr_name)
                str_out = getattr(row_out, attr_name)
                str_exp = getattr(bf.ROW_A_1, attr_name)
                log_list = self.log.render()

                # ASSERT
                with self.subTest(label, In=str_in, Out=str_out, Exp=str_exp):
                    self.assertEqual(str_out, str_exp)
                with self.subTest("Log contains", Out=log_list[0], Exp=label):
                    self.assertIn(label, log_list[0])
                with self.subTest("Log size", Out=len(log_list), Exp=1):
                    self.assertEqual(len(log_list), 1)

    def test_raises(self):
        """
        Should raise ValueError when row reconstruction fails during automatic corrections.
        """
        # ARRANGE
        row = replace(bf.ROW_A_1, sub_total="999")
        expected = ValueError.__name__

        with patch.object(type(row), "__init__") as p_row:
            p_row.side_effect = TypeError("bad mapping")
            # ACT
            try:
                _ = fb._fix_row_auto(self.log, row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
