"""
Smoke tests for the public `src.correction.interfaces` façade.

Example Usage:
    # Run this test module directly:
    python -m unittest tests/correction/test_interfaces.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock, dataclasses
    - Internal: src.cli.interfaces, src.correction.interfaces, tests.fixtures.v3_bom

Notes:
    - High-level smoke tests for API surface validation; not rule-level checks.
    - Verifies import integrity and consistent façade behavior across fields.

License:
    - Internal Use Only
"""
import unittest
from dataclasses import replace
from typing import Any, Callable
from unittest.mock import patch
from src.lookups import interfaces as lookup  # for patch
from src.cli import interfaces as cli # for patch at interface
from src.correction import interfaces as correct # Module under test
from tests.fixtures import v3_bom as bfx # Fixtures for module test


def _act_with_patch(fn: Callable, value: Any, prompt_return: str) -> tuple[str, str]:
    """
    Execute a function under patched CLI prompts and message calls.

    Temporarily replaces CLI interactions (`prompt_for_string_value`, `show_info`, `show_warning`) with mocks to simulate user input and suppress console output during testing.

    Args:
        fn (Callable): The target function under test (usually an interactive assist function).
        value (Any): The input object or value to pass into the target function.
        prompt_return (str): The simulated user input to return from the patched CLI prompt.

    Returns:
        tuple[str, str]: The function's return tuple (value_out, log_entry) captured after mock execution.

    Raises:
        None
    """
    with (
        patch.object(cli, "prompt_for_string_value") as p_prompt,
        patch.object(cli, "show_info"),
        patch.object(cli, "show_warning"),
    ):
        p_prompt.return_value = prompt_return
        return fn(value)


class _Asserts(unittest.TestCase):
    """
    Common assertion helpers for unit tests.
    """

    def assert_equal(self, *, actual: Any, expected: Any, msg: str) -> None:
        """
        Assert that two values are equal when compared as strings.
        """
        val_out = str(actual)
        val_exp = str(expected)
        with self.subTest(msg, Actual=val_out, Expected=val_exp):
            self.assertEqual(val_out, val_exp)

    def assert_empty(self, *, actual: Any) -> None:
        """
        Assert that the given value is an empty string.
        """
        val_out = str(actual)
        with self.subTest("Empty", Actual=val_out):
            self.assertEqual(val_out, "")

    def assert_contains(self, *, container: Any, member: Any) -> None:
        """
        Assert that the given value contains the member string.
        """
        container_str = str(container)
        member_str = str(member)
        with self.subTest("Log contains", Out=container_str, Exp=member_str):
            self.assertIn(member_str, container_str)


class TestInterface(_Asserts):
    """
    Unit tests for the public `src.correction.interfaces` façade.
    """

    def test_model_number_good(self):
        """
        Should return the existing header.model_no unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.model_number
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.model_no

        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_model_number_change(self):
        """
        Should normalize header.model_no and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.model_number
        bad = replace(bfx.HEADER_A, model_no="\t" + bfx.HEADER_A.model_no)
        expected = bfx.HEADER_A.model_no

        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_board_name_good(self):
        """
        Should return the existing header.board_name unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.board_name
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.board_name


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_board_name_change(self):
        """
        Should normalize header.board_name and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.board_name
        bad = replace(bfx.HEADER_A, board_name="\t" + bfx.HEADER_A.board_name)
        expected = bfx.HEADER_A.board_name


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_board_supplier_good(self):
        """
        Should return the existing header.manufacturer unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.board_supplier
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.board_supplier


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_board_supplier_change(self):
        """
        Should normalize header.manufacturer and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.board_supplier
        bad = replace(bfx.HEADER_A, board_supplier="\t" + bfx.HEADER_A.board_supplier)
        expected = bfx.HEADER_A.board_supplier

        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_build_stage_good(self):
        """
        Should return the existing header.build_stage unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.build_stage
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.build_stage


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_build_stage_change(self):
        """
        Should normalize header.build_stage and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.build_stage
        bad = replace(bfx.HEADER_A, build_stage="\t" + bfx.HEADER_A.build_stage)
        expected = bfx.HEADER_A.build_stage


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_bom_date_good(self):
        """
        Should return the existing header.date unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.bom_date
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.bom_date

        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_bom_date_change(self):
        """
        Should normalize header.date and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.bom_date
        bad = replace(bfx.HEADER_A, bom_date="\t" + bfx.HEADER_A.bom_date)
        expected = bfx.HEADER_A.bom_date


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_overhead_cost_good(self):
        """
        Should return the existing header.overhead_cost unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.overhead_cost
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.overhead_cost


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_overhead_cost_change(self):
        """
        Should correct header.overhead_cost and emit a log when recomputed value differs.
        """
        # ARRANGE
        fn = correct.overhead_cost
        bad = replace(bfx.HEADER_A, overhead_cost="\t" + bfx.HEADER_A.overhead_cost)
        expected = bfx.HEADER_A.overhead_cost


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_item_good(self):
        """
        Should return the existing row.item unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.item
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.item


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_item_change(self):
        """
        Should normalize row.item and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.item
        bad = replace(bfx.ROW_A_1, item="\t" + bfx.ROW_A_1.item)
        expected = bfx.ROW_A_1.item


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_component_type_good(self):
        """
        Should return the existing row.component_type unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.component_type
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.component_type


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_component_type_change(self):
        """
        Should normalize row.component_type and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.component_type
        bad = replace(bfx.ROW_A_1, component_type="\t" + bfx.ROW_A_1.component_type)
        expected = bfx.ROW_A_1.component_type


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_device_package_good(self):
        """
        Should return the existing row.device_package unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.device_package
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.device_package


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_device_package_change(self):
        """
        Should normalize row.device_package and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.device_package
        bad = replace(bfx.ROW_A_1, device_package="\t" + bfx.ROW_A_1.device_package)
        expected = bfx.ROW_A_1.device_package


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_description_good(self):
        """
        Should return the existing row.description unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.description
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.description


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_description_change(self):
        """
        Should normalize row.description and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.description
        bad = replace(bfx.ROW_A_1, description="*" + bfx.ROW_A_1.description)
        expected = bfx.ROW_A_1.description


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_unit_good(self):
        """
        Should return the existing row.unit unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.unit
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.units


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_unit_change(self):
        """
        Should normalize row.unit and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.unit
        bad = replace(bfx.ROW_A_1, units="\t" + bfx.ROW_A_1.units)
        expected = bfx.ROW_A_1.units


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_classification_good(self):
        """
        Should return the existing row.classification unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.classification
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.classification


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_classification_change(self):
        """
        Should normalize row.classification and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.classification
        bad = replace(bfx.ROW_A_1, classification="\t" + bfx.ROW_A_1.classification)
        expected = bfx.ROW_A_1.classification


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_manufacturer_good(self):
        """
        Should return the existing row.manufacturer unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.manufacturer
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.mfg_name


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_manufacturer_change(self):
        """
        Should normalize row.manufacturer and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.manufacturer
        bad = replace(bfx.ROW_A_1, mfg_name="*" + bfx.ROW_A_1.mfg_name)
        expected = bfx.ROW_A_1.mfg_name


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_mfg_part_number_good(self):
        """
        Should return the existing row.mfg_part_number unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.mfg_part_number
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.mfg_part_number


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_mfg_part_number_change(self):
        """
        Should normalize row.mfg_part_number and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.mfg_part_number
        bad = replace(bfx.ROW_A_1, mfg_part_number="*" + bfx.ROW_A_1.mfg_part_number)
        expected = bfx.ROW_A_1.mfg_part_number


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_ul_vde_number_good(self):
        """
        Should return the existing row.ul_vde_number unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.ul_vde_number
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.ul_vde_number


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_ul_vde_number_change(self):
        """
        Should normalize row.ul_vde_number and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.ul_vde_number
        bad = replace(bfx.ROW_A_1, ul_vde_number="\t" + bfx.ROW_A_1.ul_vde_number)
        expected = bfx.ROW_A_1.ul_vde_number


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_validated_at_good(self):
        """
        Should return the existing row.validated_at unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.validated_at
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.validated_at


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_validated_at_change(self):
        """
        Should normalize row.validated_at and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.validated_at
        bad = replace(bfx.ROW_A_1, validated_at="\t" + bfx.ROW_A_1.validated_at)
        expected = bfx.ROW_A_1.validated_at


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_qty_good(self):
        """
        Should return the existing row.qty unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.qty
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.qty


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_qty_change(self):
        """
        Should normalize row.qty and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.qty
        bad = replace(bfx.ROW_A_1, qty="\t" + bfx.ROW_A_1.qty)
        expected = bfx.ROW_A_1.qty


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_designator_good(self):
        """
        Should return the existing row.designator unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.designator
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.designators


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_designator_change(self):
        """
        Should expand/normalize row.designator and emit a log when correction is applied.
        """
        # ARRANGE
        fn = correct.designator
        bad = replace(bfx.ROW_A_1, designators="\t" + bfx.ROW_A_1.designators)
        expected = bfx.ROW_A_1.designators


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_unit_price_good(self):
        """
        Should return the existing row.unit_price unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.unit_price
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.unit_price


        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_unit_price_change(self):
        """
        Should normalize row.unit_price and emit a log when user-assisted correction is applied.
        """
        # ARRANGE
        fn = correct.unit_price
        bad = replace(bfx.ROW_A_1, unit_price="\t" + bfx.ROW_A_1.unit_price)
        expected = bfx.ROW_A_1.unit_price


        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_component_type_lookup_match(self):
        """
        Should map row.component_type to a canonical type using lookup_dict and emit a log on match.
        """
        # ARRANGE
        fn = correct.component_type_lookup
        row = replace(bfx.ROW_B2_5, component_type="MCU")
        lookup_dict = {
            "IC": ["Integrated Circuit", "MCU"],
            "Resistor": ["Resistor", "Res", "Resistance"]
        }
        expected = "IC"

        with patch.object(lookup, "get_component_type_lookup_table") as p_data_map:
            p_data_map.return_value = lookup_dict
            # ACT
            result, log = fn(row)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_component_type_lookup_no_match(self):
        """
        Should leave row.component_type unchanged and produce no log when no lookup match is found.
        """
        # ARRANGE
        fn = correct.component_type_lookup
        row = replace(bfx.ROW_B2_5, component_type="Silicon Diode")
        lookup_dict = {
            "IC": ["Integrated Circuit", "MCU"],
            "Resistor": ["Resistor", "Res", "Resistance"]
        }
        expected = "Silicon Diode"


        with patch.object(lookup, "get_component_type_lookup_table") as p_data_map:
            p_data_map.return_value = lookup_dict
            # ACT
            result, log = fn(row)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_expand_designators_change(self):
        """
        Should expand a designator range (e.g., R5-R10) and emit a log when expanded.
        """
        # ARRANGE
        fn = correct.expand_designators
        bad = replace(bfx.ROW_B2_1, designators="R5-R10")
        expected = bfx.ROW_B2_1.designators

        # ACT
        result, log = fn(bad)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_expand_designators_no_change(self):
        """
        Should keep designator unchanged and produce no log when already expanded.
        """
        # ARRANGE
        fn = correct.expand_designators
        good = bfx.ROW_B2_1
        expected = bfx.ROW_B2_1.designators

        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_material_cost_good(self):
        """
        Should compute header.material_cost correctly and produce no log when already consistent.
        """
        # ARRANGE
        fn = correct.material_cost
        board = bfx.BOARD_A
        expected = bfx.BOARD_A.header.material_cost

        # ACT
        result, log = fn(board)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_material_cost_change(self):
        """
        Should recompute header.material_cost and emit a log when the header value is incorrect.
        """
        # ARRANGE
        fn = correct.material_cost
        header = replace(bfx.BOARD_A.header, material_cost="999")
        board = replace(bfx.BOARD_A, header=header)
        expected = bfx.BOARD_A.header.material_cost

        # ACT
        result, log = fn(board)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_sub_total_good(self):
        """
        Should return the existing header.sub_total unchanged and produce no log.
        """
        # ARRANGE
        fn = correct.sub_total
        good = bfx.ROW_A_1
        expected = bfx.ROW_A_1.sub_total

        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_sub_total_change(self):
        """
        Should recompute header.sub_total and emit a log when the value is corrected.
        """
        # ARRANGE
        fn = correct.sub_total
        bad = replace(bfx.ROW_A_1, sub_total="999")
        expected = bfx.ROW_A_1.sub_total

        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)

    def test_total_cost_good(self):
        # ARRANGE
        fn = correct.total_cost
        good = bfx.HEADER_A
        expected = bfx.HEADER_A.total_cost

        # ACT
        result, log = fn(good)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_empty(actual=log)

    def test_total_cost_change(self):
        # ARRANGE
        fn = correct.total_cost
        bad = replace(bfx.HEADER_A, total_cost="2.5")
        expected = bfx.HEADER_A.total_cost

        # ACT
        result, log = _act_with_patch(fn, bad, expected)

        # ASSERT
        self.assert_equal(actual=result, expected=expected, msg=fn.__name__)
        self.assert_contains(container=log, member=expected)


if __name__ == "__main__":
    unittest.main()
