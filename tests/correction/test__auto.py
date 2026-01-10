"""
Unit tests for autocorrection functions.

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/correction/test__auto.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - Project Modules: src.correction._auto, src.models.interfaces, tests.fixtures.v3_bom, tests.fixtures.v3_value

Notes:
    - Tests use dataclasses.replace for variant creation
    - Fixtures provide stable representative BOM objects
    - Focuses on correctness and deterministic audit log output
    - Internal-only test coverage for private autocorrect utilities

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace
from unittest.mock import patch

from src.models.interfaces import (
    BoardV3,
    HeaderV3,
)

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)
from src.lookups import interfaces as lookup  # for patch

# noinspection PyProtectedMember
from src.correction import _auto as auto  # Direct internal import — acceptable in tests

from tests.fixtures import v3_bom as bfx


class TestComponentTypeLookup(unittest.TestCase):
    """
    Unit tests for the `component_type_lookup` function.
    """

    def setUp(self):
        self.lookup_dict = {
            "Capacitor": ["Ceramic Capacitor"],
            "Diode": ["SMD Diode", "SMD Zener"],
            "Zener": ["SMD Zener"],  # Duplicate alias to create ambiguity
            "IC": ["Integrated Circuit"],
        }
        self.ignore_str = ["SMD", "Surface Mount"]

    def test_match(self):
        """
        Should return the canonical key when both metrics match a known alias above the threshold.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, component_type="SMD Ceramic Capacitor")
        expected_out = "Capacitor"

        with (
            patch.object(lookup, "get_component_type_lookup_table") as p_data_map,
            patch.object(auto.app_settings, "get_settings") as p_get_settings,
        ):
            p_data_map.return_value = self.lookup_dict
            p_get_settings.return_value.get_value.return_value = self.ignore_str
            # ACT
            result, log = auto.component_type_lookup(row)

        # ASSERT
        with self.subTest("Output", Out=result, Exp=expected_out):
            self.assertEqual(result, expected_out)
        with self.subTest("Log", Out=log):
            self.assertIn(row.component_type, log)
            self.assertIn(expected_out, log)
            self.assertIn(TableLabelsV3.COMPONENT_TYPE, log)

    def test_no_match_below_threshold(self):
        """
        Should return the original string and empty log when no matches exceed the threshold.
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, component_type="Unknown Part")

        with (
            patch.object(lookup, "get_component_type_lookup_table") as p_data_map,
            patch.object(auto.app_settings, "get_settings") as p_get_settings,
        ):
            p_data_map.return_value = self.lookup_dict
            p_get_settings.return_value.get_value.return_value = self.ignore_str
            # ACT
            result, log = auto.component_type_lookup(row)

        # ASSERT
        with self.subTest("Output", Out=result, Exp=row.component_type):
            self.assertEqual(result, row.component_type)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")

    def test_multiple_key_matches(self):
        """
        Should return the original input when multiple canonical keys match (ambiguity).
        """
        # ARRANGE
        row = replace(bfx.ROW_A_1, component_type="Zener")

        with (
            patch.object(lookup, "get_component_type_lookup_table") as p_data_map,
            patch.object(auto.app_settings, "get_settings") as p_get_settings,
        ):
            p_data_map.return_value = self.lookup_dict
            p_get_settings.return_value.get_value.return_value = self.ignore_str
            # ACT
            result, log = auto.component_type_lookup(row)

        # ASSERT
        with self.subTest("Output", Out=result, Exp=row.component_type):
            self.assertEqual(result, row.component_type)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")

    def test_no_match_without_ignore_mask(self):
        """
        Should NOT match when ignore mask is empty and noisy token remains.
        """
        row = replace(bfx.ROW_A_1, component_type="Surface Mount MCU Integrated Circuit")

        with (
            patch.object(lookup, "get_component_type_lookup_table") as p_data_map,
            patch.object(auto.app_settings, "get_settings") as p_get_settings,
        ):
            p_data_map.return_value = self.lookup_dict
            p_get_settings.return_value.get_value.return_value = []  # no ignore mask

            result, log = auto.component_type_lookup(row)

        with self.subTest("Output", Out=result, Exp=row.component_type):
            self.assertEqual(result, row.component_type)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")

    def test_match_requires_ignore_mask(self):
        """
        Should match ONLY when ignore mask removes noisy token.
        """
        row = replace(bfx.ROW_A_1, component_type="Surface Mount MCU Integrated Circuit")
        expected = "IC"

        with (
            patch.object(lookup, "get_component_type_lookup_table") as p_data_map,
            patch.object(auto.app_settings, "get_settings") as p_get_settings,
        ):
            p_data_map.return_value = self.lookup_dict
            p_get_settings.return_value.get_value.return_value = self.ignore_str

            result, log = auto.component_type_lookup(row)

        with self.subTest("Output", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest("Log", Out=log):
            self.assertIn(row.component_type, log)
            self.assertIn(expected, log)
            self.assertIn(TableLabelsV3.COMPONENT_TYPE, log)


class TestExpandDesignators(unittest.TestCase):
    """
    Unit tests for the `expand_designators` function.
    """

    def test_no_correction(self):
        """
        Should return the original designator string and an empty change log when no corrections are made.
        """
        # ARRANGE
        cases = (bfx.ROW_A_1, bfx.ROW_A_2, bfx.ROW_A_3)

        for row in cases:
            # ACT
            value_out, log = auto.expand_designators(row)

            # ASSERT
            with self.subTest("Value Out", Out=value_out, Exp=row.designators):
                self.assertEqual(row.designators, value_out)
            with self.subTest("Log", Out=""):
                self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return expanded range designators and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = TableLabelsV3.DESIGNATORS
        cases = (
            (replace(bfx.ROW_A_1, designators="R1-R3"), "R1,R2,R3"),
            (replace(bfx.ROW_A_1, designators="R1, R3-R6, R12, R45-R43"), "R1,R3,R4,R5,R6,R12,R45,R44,R43"),
            (replace(bfx.ROW_A_1, designators="R1-R2, C10-C12"), "R1,R2,C10,C11,C12"),
            (replace(bfx.ROW_A_3, designators="R5-R3"), "R5,R4,R3"),
        )

        for row, value_out in cases:
            # ACT
            out, log = auto.expand_designators(row)

            # ASSERT
            with self.subTest("Value Out", Out=out, Exp=value_out):
                self.assertEqual(out, value_out)
            with self.subTest("Log", Out=log):
                self.assertIn(row.designators, log, row.designators)
                self.assertIn(value_out, log, value_out)
                self.assertIn(field, log, field)


class TestMaterialCost(unittest.TestCase):
    """
    Unit tests for the `material_cost` function.
    """

    def test_no_correction(self):
        """
        Should return the original material cost and an empty change log when no corrections are made.
        """
        # ARRANGE
        board = bfx.BOARD_A
        expected_value = board.header.material_cost

        # ACT
        value_out, log = auto.material_cost(board)

        # ASSERT
        with self.subTest("Value Out", Out=value_out, Exp=expected_value):
            self.assertEqual(value_out, expected_value)
        with self.subTest("Log", Out=log, Exp=""):
            self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return corrected material cost and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = HeaderLabelsV3.MATERIAL_COST
        header_bad_material: HeaderV3 = replace(bfx.HEADER_A, material_cost="99")
        board: BoardV3 = replace(bfx.BOARD_A, header=header_bad_material)
        expected_value = bfx.BOARD_A.header.material_cost

        # ACT
        value_out, log = auto.material_cost(board)

        # ASSERT
        with self.subTest("Value Out", Out=value_out, Exp=expected_value):
            self.assertEqual(value_out, expected_value)

        # Log should mention the field name and both old and new values
        with self.subTest("Log contains", Out=log):
            self.assertIn(field, log)
            self.assertIn(board.header.material_cost, log)
            self.assertIn(expected_value, log)

    def test_raise_on_bad_inputs(self):
        """
        Should raise ValueError when a base field cannot be parsed as float.
        """
        # ARRANGE
        # Case 1: a row with bad sub_total
        rows_bad_sub_total = (replace(bfx.ROW_A_1, sub_total="*"), bfx.ROW_A_2)

        # Case 2: header has bad material_cost (even though rows are OK)
        header_bad_material = replace(bfx.HEADER_B1, material_cost="*")

        cases = (
            replace(bfx.BOARD_A, rows=rows_bad_sub_total),
            replace(bfx.BOARD_A, header=header_bad_material),
        )
        expected = ValueError.__name__

        for board in cases:
            # ACT
            try:
                auto.material_cost(board)
                result = ""  # No exception
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest("Raise", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestSubTotal(unittest.TestCase):
    """
    Unit tests for the `sub_total` function.
    """

    def test_no_correction(self):
        """
        Should return the original sub-total and an empty change log when no corrections are made.
        """
        # ARRANGE
        rows = (
            bfx.ROW_A_1,
            bfx.ROW_A_2,
            bfx.ROW_A_3,
        )

        for row in rows:
            # ACT
            value_out, log = auto.sub_total(row)

            # ASSERT
            value_in = row.sub_total
            with self.subTest("Value Out", Out=value_out, Exp=value_in):
                self.assertEqual(value_in, value_out)
            with self.subTest("Log", Out=""):
                self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return corrected sub-total and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = TableLabelsV3.SUB_TOTAL
        rows = (
            (replace(bfx.ROW_A_1, sub_total="1" + bfx.ROW_A_1.sub_total), bfx.ROW_A_1.sub_total),
            (replace(bfx.ROW_A_2, sub_total="1" + bfx.ROW_A_1.sub_total), bfx.ROW_A_2.sub_total),
            (replace(bfx.ROW_A_3, sub_total="1" + bfx.ROW_A_1.sub_total), bfx.ROW_A_3.sub_total),
        )

        for row, value_out in rows:
            # ACT
            out, log = auto.sub_total(row)

            # ASSERT
            value_in = row.sub_total
            with self.subTest("Value Out", Out=out, Exp=value_out):
                self.assertEqual(out, value_out)
            with self.subTest("Log", Out=log):
                self.assertIn(value_in, log, value_in)
                self.assertIn(value_out, log, value_out)
                self.assertIn(field, log, field)

    def test_raise(self):
        """
        Should return value error when base fields can not be parsed.
        """
        # ARRANGE
        rows = (
            replace(bfx.ROW_A_1, qty="*"),
            replace(bfx.ROW_A_2, unit_price="*"),
            replace(bfx.ROW_A_3, sub_total="*"),
        )
        expected = ValueError.__name__

        for row in rows:
            # ACT
            try:
                _, _ = auto.sub_total(row)
                result = ""
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest("Raise", Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestTotalCost(unittest.TestCase):
    """
    Unit tests for the `total_cost` function.
    """

    def test_no_correction(self):
        """
        Should return the original total cost and an empty change log when no corrections are made.
        """
        # ARRANGE
        headers = (
            bfx.HEADER_B1,
            bfx.HEADER_B2,
        )

        for header in headers:
            # ACT
            value_out, log = auto.total_cost(header)

            # ASSERT
            value_in = header.total_cost
            with self.subTest("Value Out", Out=value_out, Exp=value_in):
                self.assertEqual(value_in, value_out)
            with self.subTest("Log", Out=""):
                self.assertEqual(log, "")

    def test_correction(self):
        """
        Should return corrected total cost and a non-empty change log when corrections are made.
        """
        # ARRANGE
        field = HeaderLabelsV3.TOTAL_COST
        headers = (
            (replace(bfx.HEADER_B1, total_cost="1" + bfx.HEADER_B1.total_cost), bfx.HEADER_B1.total_cost),
            (replace(bfx.HEADER_B2, total_cost="1" + bfx.HEADER_B2.total_cost), bfx.HEADER_B2.total_cost),
        )

        for header, value_exp in headers:
            # ACT
            value_out, log = auto.total_cost(header)

            # ASSERT
            with self.subTest("Value Out", Out=value_out, Exp=value_exp):
                self.assertEqual(value_out, value_exp)
            with self.subTest("Log", Out=log):
                self.assertIn(value_out, log, value_out)
                self.assertIn(value_exp, log, value_exp)
                self.assertIn(field, log, field)

    def test_raise(self):
        """
        Should return value error when base fields can not be parsed.
        """
        # ARRANGE
        headers = (
            replace(bfx.HEADER_B1, material_cost="*"),
            replace(bfx.HEADER_B1, overhead_cost="*"),
            replace(bfx.HEADER_B1, total_cost="*"),
        )
        expected = ValueError.__name__

        for header in headers:
            # ACT
            try:
                _, __ = auto.total_cost(header)
                result = ""
            except ValueError as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest("Raise", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
