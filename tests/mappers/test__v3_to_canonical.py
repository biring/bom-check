"""
Unit tests for the version 3 to canonical BOM mapper.

This module validates that the V3 → Canonical mapping logic produces correct canonical models from verified and fixed version 3 BOM inputs.


Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/mappers/test__v3_to_canonical.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock
    - Internal Packages:
        - src.mappers._v3_to_canonical
        - src.mappers._dependencies
        - tests.fixtures.v3_bom
        - tests.fixtures.canonical

Notes:
    - Tests assume fixtures represent verified and fixed V3 BOM inputs.
    - Mapping functions are treated as pure functions with no side effects.
    - Assertions compare canonical fixtures field-by-field for strict correctness.
    - Verification failures are injected via dependency patching to test error paths.

License:
    - Internal Use Only
"""

import unittest
from unittest.mock import patch

from tests.fixtures import (
    v3_bom as fx_v3,
    canonical as fx_canon,
)

# noinspection PyProtectedMember
from src.mappers import (
    _v3_to_canonical as mapper,
    _dependencies as dep
)


class TestGroupRowsAsPart(unittest.TestCase):
    """
    Unit tests for the internal `_group_rows_to_parts` helper.
    """

    def test_happy_path(self):
        """
        Should group rows into canonical part field-by-field.
        """
        # ARRANGE
        cases = (
            (fx_v3.BOARD_A.rows, fx_canon.BOARD_A_CANONICAL.parts),
            (fx_v3.BOARD_B1.rows, fx_canon.BOARD_B1_CANONICAL.parts),
            (fx_v3.BOARD_B2.rows, fx_canon.BOARD_B2_CANONICAL.parts),
        )

        # ACT
        for case, expected in cases:
            actual = mapper._group_rows_to_parts(case)

            # ASSERT
            with self.subTest("Part count", Out=len(actual), Exp=len(expected)):
                self.assertEqual(len(actual), len(expected))
            with self.subTest("Class match"):
                self.assertEqual(actual, expected)

            for idx, (exp_part, act_part) in enumerate(zip(expected, actual), start=1):
                for field_name in exp_part.__dict__.keys():
                    exp_value = getattr(exp_part, field_name)
                    act_value = getattr(act_part, field_name)
                    with self.subTest(
                            PartIndex=idx,
                            Field=field_name,
                            Out=act_value,
                            Exp=exp_value,
                    ):
                        self.assertEqual(act_value, exp_value)


class TestMapBoard(unittest.TestCase):
    """
    Unit tests for the `map_board` mapping function.
    """

    def test_happy_path(self):
        """
        Should map version 3 bom board to canonical bom board field-by-field.
        """
        # ARRANGE
        cases = (
            (fx_v3.BOARD_A, fx_canon.BOARD_A_CANONICAL),
            (fx_v3.BOARD_B1, fx_canon.BOARD_B1_CANONICAL),
            (fx_v3.BOARD_B2, fx_canon.BOARD_B2_CANONICAL),
        )

        # ACT
        for case, expected in cases:
            actual = mapper._map_board(case)

            # ASSERT: header
            for field_name in expected.header.__dict__.keys():
                exp_value = getattr(expected.header, field_name)
                act_value = getattr(actual.header, field_name)
                with self.subTest(
                        Section="Header",
                        Field=field_name,
                        Out=act_value,
                        Exp=exp_value,
                ):
                    self.assertEqual(act_value, exp_value)

            # ASSERT: parts
            expected_parts = expected.parts
            actual_parts = actual.parts
            with self.subTest("Part count", Out=len(actual_parts), Exp=len(expected_parts)):
                self.assertEqual(len(actual_parts), len(expected_parts))

            for idx, (exp_part, act_part) in enumerate(zip(expected_parts, actual_parts), start=1):
                for field_name in exp_part.__dict__.keys():
                    exp_value = getattr(exp_part, field_name)
                    act_value = getattr(act_part, field_name)
                    with self.subTest(
                            Section="Part",
                            PartIndex=idx,
                            Field=field_name,
                            Out=act_value,
                            Exp=exp_value,
                    ):
                        self.assertEqual(act_value, exp_value)


class TestMapBom(unittest.TestCase):
    """
    Unit tests for the `map_bom` mapping function.
    """

    def test_happy_path(self):
        """
        Should map version 3 bom to canonical bom field-by-field.
        """
        # ARRANGE
        cases = (
            (fx_v3.BOM_A, fx_canon.BOM_A_CANONICAL),
            (fx_v3.BOM_B, fx_canon.BOM_B_CANONICAL),
        )

        for case, expected in cases:
            # ACT
            actual_bom = mapper.map_bom(case)

            # ASSERT: is_cost_bom
            with self.subTest("is_cost_bom", Out=actual_bom.is_cost_bom, Exp=expected.is_cost_bom):
                self.assertEqual(actual_bom.is_cost_bom, expected.is_cost_bom)

            # ASSERT: board count
            exp_boards = expected.boards
            act_boards = actual_bom.boards
            with self.subTest("Board count", Out=len(act_boards), Exp=len(exp_boards)):
                self.assertEqual(len(act_boards), len(exp_boards))

            # ASSERT: each board header + parts matches canonical fixture
            for b_idx, (exp_board, act_board) in enumerate(zip(exp_boards, act_boards), start=1):
                # Header
                for field_name in exp_board.header.__dict__.keys():
                    exp_value = getattr(exp_board.header, field_name)
                    act_value = getattr(act_board.header, field_name)
                    with self.subTest(
                            BoardIndex=b_idx,
                            Section="Header",
                            Field=field_name,
                            Out=act_value,
                            Exp=exp_value,
                    ):
                        self.assertEqual(act_value, exp_value)

                # Parts
                exp_parts = exp_board.parts
                act_parts = act_board.parts
                with self.subTest(
                        BoardIndex=b_idx,
                        Section="Part count",
                        Out=len(act_parts),
                        Exp=len(exp_parts),
                ):
                    self.assertEqual(len(act_parts), len(exp_parts))

                for p_idx, (exp_part, act_part) in enumerate(zip(exp_parts, act_parts), start=1):
                    for field_name in exp_part.__dict__.keys():
                        exp_value = getattr(exp_part, field_name)
                        act_value = getattr(act_part, field_name)
                        with self.subTest(
                                BoardIndex=b_idx,
                                Section="Part",
                                PartIndex=p_idx,
                                Field=field_name,
                                Out=act_value,
                                Exp=exp_value,
                        ):
                            self.assertEqual(act_value, exp_value)

    def test_raise(self):
        """
        Should raise an error when an exception is raised.
        """
        # ARRANGE
        cases = (
            (fx_v3.BOM_A, RuntimeError("Verify failed"), RuntimeError),
            (fx_v3.BOM_A, KeyError("boom"), RuntimeError),
        )

        # ACT
        for case, injected_error, expected in cases:
            expected_msg_fragment = str(injected_error)
            with patch.object(dep.verify, "v3_bom", side_effect=injected_error):
                try:
                    mapper.map_bom(case)
                    actual = ""
                except Exception as ex:
                    actual = type(ex)
                    msg = str(ex)

                # ASSERT: type
                with self.subTest("Raise exception", Out=actual, Expected=expected):
                    self.assertEqual(actual, expected)

                # ASSERT: message contains original error message
                with self.subTest("Raise msg", Out=msg, Expected=expected_msg_fragment):
                    self.assertIn(expected_msg_fragment, msg)


class TestMapComponent(unittest.TestCase):
    """
    Unit tests for the `map_component` mapping helper.
    """

    def test_happy_path(self):
        """
        Should map a version 3 row to a canonical component field-by-field.
        """
        # ARRANGE
        cases = (
            (fx_v3.BOARD_A.rows[0], fx_canon.BOARD_A_CANONICAL.parts[0].primary_component),
            (fx_v3.BOARD_B1.rows[1], fx_canon.BOARD_B1_CANONICAL.parts[1].primary_component),
            (fx_v3.BOARD_B2.rows[2], fx_canon.BOARD_B2_CANONICAL.parts[2].primary_component),
        )

        for raw_row, expected_component in cases:
            # ACT
            actual_component = mapper._map_row_to_component(raw_row)

            # ASSERT
            for field_name in expected_component.__dict__.keys():
                exp_value = getattr(expected_component, field_name)
                act_value = getattr(actual_component, field_name)
                with self.subTest(
                        Row=raw_row,
                        Field=field_name,
                        Out=act_value,
                        Exp=exp_value,
                ):
                    self.assertEqual(act_value, exp_value)


class TestMapHeader(unittest.TestCase):
    """
    Unit tests for the `map_header` mapping helper.
    """

    def test_happy_path(self):
        """
        Should map version 3 bom header to canonical bom header field-by-field.
        """
        # ARRANGE
        cases = (
            (fx_v3.HEADER_A, fx_canon.HEADER_A_CANONICAL),
            (fx_v3.HEADER_B1, fx_canon.HEADER_B1_CANONICAL),
            (fx_v3.HEADER_B2, fx_canon.HEADER_B2_CANONICAL),
        )

        # ACT
        for case, expected in cases:
            actual = mapper._map_header(case)

            # ASSERT
            for field_name in expected.__dict__.keys():
                exp_value = getattr(expected, field_name)
                act_value = getattr(actual, field_name)
                with self.subTest(Field=field_name, Out=act_value, Exp=exp_value):
                    self.assertEqual(act_value, exp_value)
            # self.assertEqual(actual, expected)


class TestMapPart(unittest.TestCase):
    """
    Unit tests for the `map_part` mapping helper.
    """

    def test_happy_path_board_a(self):
        """
        Should map primary + alternate rows into canonical parts for BOARD_A.
        """
        # ARRANGE
        rows = fx_v3.BOARD_A.rows
        expected_parts = fx_canon.BOARD_A_CANONICAL.parts

        # (primary_index, alternate_indices_tuple, expected_part_index)
        cases = (
            (0, (1, 2), 0),  # item 1: primary + 2 alternates
            (3, (4,), 1),  # item 2: primary + 1 alternate
            (5, (), 2),  # item 3: primary only
            (6, (), 3),  # item 4: primary only
        )

        for primary_idx, alt_indices, exp_idx in cases:
            primary_row = rows[primary_idx]
            alt_rows = tuple(rows[i] for i in alt_indices)
            expected_part = expected_parts[exp_idx]

            # ACT
            actual_part = mapper._map_rows_to_part(primary_row, alt_rows)

            # ASSERT: part-level fields
            for field_name in expected_part.__dict__.keys():
                exp_value = getattr(expected_part, field_name)
                act_value = getattr(actual_part, field_name)
                with self.subTest(
                        Case=f"BOARD_A part {exp_idx + 1}",
                        Field=field_name,
                        Out=act_value,
                        Exp=exp_value,
                ):
                    self.assertEqual(act_value, exp_value)

    def test_happy_path_boards_b1_b2(self):
        """
        Should map primary-only rows into canonical parts for BOARD_B1 and BOARD_B2.
        """
        # ARRANGE
        cases = (
            # BOARD_B1: all parts are primary-only
            (fx_v3.BOARD_B1.rows, fx_canon.BOARD_B1_CANONICAL.parts),
            # BOARD_B2: all parts are primary-only
            (fx_v3.BOARD_B2.rows, fx_canon.BOARD_B2_CANONICAL.parts),
        )

        for rows, expected_parts in cases:
            for idx, expected_part in enumerate(expected_parts):
                primary_row = rows[idx]
                alt_rows: tuple = ()

                # ACT
                actual_part = mapper._map_rows_to_part(primary_row, alt_rows)

                # ASSERT
                for field_name in expected_part.__dict__.keys():
                    exp_value = getattr(expected_part, field_name)
                    act_value = getattr(actual_part, field_name)
                    with self.subTest(
                            BoardRows=rows,
                            PartIndex=idx + 1,
                            Field=field_name,
                            Out=act_value,
                            Exp=exp_value,
                    ):
                        self.assertEqual(act_value, exp_value)


if __name__ == "__main__":
    unittest.main()
