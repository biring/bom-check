"""
Unit tests for Version 3 BOM cleaner (_v3_bom).

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/cleaners/test__v3_bom.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing, unittest.mock
    - Internal Packages: src.cleaners._v3_bom, src.cleaners._types, src.models.interfaces

Notes:
    - Tests mock internal helpers to isolate orchestration behavior from field-level coercion.
    - Fixtures under `tests.fixtures.v3_bom` provide structured BOM samples for stable expectations.
    - Focus is on sequence integrity, log generation, and correct error propagation rather than coercion rule content.

License:
    - Internal Use Only
"""
import unittest
from dataclasses import replace
from unittest.mock import patch
from src.common import ChangeLog
from tests.fixtures import v3_bom as fx
# noinspection PyProtectedMember
from src.cleaners import _v3_bom as cb  # Direct internal import — acceptable in tests


class TestCoerceBom(unittest.TestCase):
    """
    Tests for `coerce_bom` (BOM-level).
    """

    def test_valid(self):
        """
        Should keep BOM values unchanged and produce an empty log.
        """
        # ARRANGE
        cases = (
            (fx.BOM_B, True),  # Clean fixture
            (replace(fx.BOM_B, is_cost_bom=False), False),
        )
        for bom, expected_is_cost_bom in cases:
            # ACT
            out_bom, log = cb.clean_v3_bom(bom)

            # ASSERT
            with self.subTest("Log size", Out=len(log), Exp=0):
                self.assertEqual(len(log), 0, log)
            with self.subTest("Is Cost Bom", Out=out_bom.is_cost_bom, Exp=expected_is_cost_bom):
                self.assertEqual(out_bom.is_cost_bom, expected_is_cost_bom)
            with self.subTest("File Name", Out=out_bom.file_name, Exp=fx.BOM_B.file_name):
                self.assertEqual(out_bom.file_name, fx.BOM_B.file_name)

    def test_invalid(self):
        """
        Should coerce values for a minimally dirty BOM and produce a non-empty log.
        """
        # ARRANGE (start clean and add space(s) to dirty up a field)
        src_dirty = replace(
            fx.BOM_A,
            boards=(
                replace(
                    fx.BOARD_A,
                    header=replace(fx.BOARD_A.header, board_name=" " + fx.BOARD_A.header.board_name + " "),
                ),
            ),
        )
        # ACT
        out_bom, log = cb.clean_v3_bom(src_dirty)

        # ASSERT (spot-check)
        board_name_in = src_dirty.boards[0].header.board_name
        board_name_out = out_bom.boards[0].header.board_name
        with self.subTest("Coerced cell", In=board_name_in, Out=board_name_out):
            self.assertNotEqual(board_name_in, board_name_out)
        with self.subTest("Log size", Out=len(log), Exp=">0"):
            self.assertGreater(len(log), 0)

    def test_raise(self):
        """
        Should propagate ValueError when internal coercion helper fails (simulated with a mock).
        """
        # ARRANGE
        src = fx.BOM_A
        expected = ValueError.__name__

        # ACT
        with patch("src.cleaners._v3_bom._clean_row", side_effect=ValueError("mapping failed")):
            try:
                _ = cb.clean_v3_bom(src)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestCoerceHeader(unittest.TestCase):
    """
    Tests for `_coerce_header` (Header-level).
    """

    def test_valid(self):
        """
        Should keep header values unchanged and produce no log entries.
        """
        # ARRANGE
        header = fx.BOARD_A.header
        log = ChangeLog()
        # ACT
        out_header = cb._clean_header(log, header)
        # ASSERT
        for k, v in header.__dict__.items():
            with self.subTest(Field=k, Out=out_header.__dict__.get(k), Exp=v):
                self.assertEqual(out_header.__dict__.get(k), v)
        with self.subTest("Log size", Out=len(log.render()), Exp=0):
            self.assertEqual(len(log.render()), 0)

    def test_invalid(self):
        """
        Should coerce values for a minimally dirty BOM header and produce a non-empty log.
        """
        # ARRANGE (start clean and add space to dirty up a field)
        dirty = replace(
            fx.BOM_A,
            boards=(
                replace(
                    fx.BOARD_A,
                    header=replace(fx.BOARD_A.header, board_name=" " + fx.BOARD_A.header.board_name + " "),
                ),
            ),
        )
        log = ChangeLog()
        # ACT
        out_header = cb._clean_header(log, dirty.boards[0].header)
        # ASSERT (spot-check)
        with self.subTest("Coerced cell", In=dirty.boards[0].header.board_name, Out=out_header.board_name):
            self.assertNotEqual(out_header.board_name, dirty.boards[0].header.board_name)
        with self.subTest("Log size", Out=len(log.render()), Exp=0):
            self.assertGreater(len(log.render()), 0)

    def test_raises(self):
        """
        Should raise ValueError when header reconstruction fails (simulated by patching the model constructor).
        """
        # ARRANGE
        header = fx.BOARD_A.header
        log = ChangeLog()
        expected = ValueError.__name__

        # ACT
        with patch("src.cleaners._v3_bom.map_template_v3_header_to_bom_v3_header", side_effect=TypeError("bad mapping")):
            try:
                _ = cb._clean_header(log, header)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise successful"):
                with self.assertRaises(ValueError):
                    _ = cb._clean_header(log, header)
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestCoerceRow(unittest.TestCase):
    """
    Tests for `_coerce_row` (Row-level).
    """

    def test_valid(self):
        """
        Should keep row values unchanged and produce no log entries.
        """
        # ARRANGE
        row = fx.BOARD_A.rows[0]
        log = ChangeLog()
        # ACT
        out_row = cb._clean_row(log, row)
        # ASSERT
        for k, v in row.__dict__.items():
            with self.subTest(Field=k, Out=out_row.__dict__.get(k), Exp=v):
                self.assertEqual(out_row.__dict__.get(k), v)
        with self.subTest("Log size", Out=len(log.render()), Exp=0):
            self.assertEqual(len(log.render()), 0)

    def test_invalid(self):
        """
        Should coerce values for a minimally dirty BOM row and produce a non-empty log.
        """
        # ARRANGE (start clean and add space to dirty up a field)
        dirty = replace(fx.ROW_A_1, classification=" " + fx.ROW_A_1.classification + " ")
        log = ChangeLog()

        # ACT
        out_row = cb._clean_row(log, dirty)

        # ASSERT (spot-check)
        with self.subTest("Coerced cell", In=dirty.classification, Out=out_row.classification):
            self.assertNotEqual(dirty.classification, out_row.classification)
        with self.subTest("Log size", Out=len(log.render()), Exp=0):
            self.assertGreater(len(log.render()), 0)

    def test_raises(self):
        """
        Should raise ValueError when row reconstruction fails (simulated by patching the model constructor).
        """
        # ARRANGE
        row = fx.BOARD_A.rows[0]
        log = ChangeLog()
        expected = ValueError.__name__
        # ACT
        with patch("src.cleaners._v3_bom.map_template_v3_table_to_bom_v3_row", side_effect=TypeError("bad mapping")):
            try:
                _ = cb._clean_row(log, row)
                result = ""
            except ValueError:
                result = ValueError.__name__

            # ASSERT
            with self.subTest("Raise successful"):
                with self.assertRaises(ValueError):
                    _ = cb._clean_row(log, row)
            with self.subTest("Raise type", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
