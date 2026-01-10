"""
Unit tests for the `_assist` module functions that interactively validate and correct BOM header fields.

This module verifies that:
    - Validators accept or reject user inputs correctly
    - CLI prompts simulate user correction loops
    - Change-log text reflects value updates accurately

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/correction/test__assist.py

    # Direct discovery:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, unittest.mock, dataclasses, typing
    - External Packages: None

Notes:
    - CLI prompts are patched to simulate user input.
    - Functions are treated as pure behavioral wrappers for validation and logging.
    - Tests confirm log message formatting and value propagation.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace
from unittest.mock import patch
from typing import Callable, Any

from src.cli import interfaces as cli

# noinspection PyProtectedMember
import src.correction._assist as assist  # Direct internal import — acceptable in tests

import tests.fixtures.v3_bom as bfx


def _act_with_patch(fn: Callable, value: Any, prompt_return: str) -> tuple[str, str]:
    """
    Execute a function under patched CLI prompts and message calls.

    Temporarily replaces CLI interactions (`prompt_for_string_value`, `show_info`, `show_warning`)
    with mocks to simulate user input and suppress console output during testing.

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


class _Assert(unittest.TestCase):
    """
    Helper assertion methods for verifying output values and change-log content in assist-function tests.

    These reusable assertions simplify repetitive checks across tests for corrected field values and
    audit-log consistency, ensuring clear subtest labeling for granular failure reporting.
    """

    def assertValueOut(self, actual, expected):
        """
        Assert that the actual output value matches the expected value.

        Uses a subtest to clearly label the output comparison for better test diagnostics.
        """
        with self.subTest("Value Out", Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def assertLogEmpty(self, log):
        """
        Assert that the generated change log is empty.

        Typically used when no corrections are applied and no audit entry should be emitted.
        """
        with self.subTest("Log empty", Out=""):
            self.assertEqual(log, "")

    def assertLogContains(self, log: str, values: list[str]):
        """
        Assert that the change log contains all specified substrings.

        Iterates through each expected value and checks for inclusion in the log using subtests
        for clearer failure localization when multiple tokens are missing.
        """
        for value in values:
            with self.subTest("Log contains", Out=log, Exp=value):
                self.assertIn(value, log)


class TestModelNumber(_Assert):
    """
    Unit tests for the `model_number` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the model number or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        header_in = bfx.BOARD_A.header
        expected_out = bfx.BOARD_A.header.model_no

        # ACT
        actual_out, log = _act_with_patch(assist.model_number, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the model number and include both the old and new values in the generated change log.
        """
        # ARRANGE
        header_in = replace(
            bfx.BOARD_A.header,
            model_no="*" + bfx.BOARD_A.header.model_no,  # invalid token to force correction
        )
        expected_out = bfx.BOARD_A.header.model_no

        # ACT
        actual_out, log = _act_with_patch(assist.model_number, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogContains(log, [header_in.model_no, expected_out])


class TestBoardName(_Assert):
    """
    Unit tests for the `board_name` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the board name or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        header_in = bfx.BOARD_A.header
        expected_out = bfx.BOARD_A.header.board_name

        # ACT
        actual_out, log = _act_with_patch(assist.board_name, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the board name and include both the old and new values in the generated change log.
        """
        # ARRANGE
        header_in = replace(
            bfx.BOARD_A.header,
            board_name="*" + bfx.BOARD_A.header.board_name,  # invalid token to force correction
        )
        expected_out = bfx.BOARD_A.header.board_name

        # ACT
        actual_out, log = _act_with_patch(assist.board_name, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogContains(log, [header_in.board_name, expected_out])


class TestBoardSupplier(_Assert):
    """
    Unit tests for the `board_supplier` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the board supplier or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        header_in = bfx.BOARD_A.header
        expected_out = bfx.BOARD_A.header.board_supplier

        # ACT
        actual_out, log = _act_with_patch(assist.board_supplier, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the board supplier and include both the old and new values in the generated change log.
        """
        # ARRANGE
        header_in = replace(
            bfx.BOARD_A.header,
            board_supplier="*" + bfx.BOARD_A.header.board_supplier,  # invalid token to force correction
        )
        expected_out = bfx.BOARD_A.header.board_supplier

        # ACT
        actual_out, log = _act_with_patch(assist.board_supplier, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogContains(log, [header_in.board_supplier, expected_out])


class TestBuildStage(_Assert):
    """
    Unit tests for the `build_stage` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the build stage or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        header_in = bfx.BOARD_A.header
        expected_out = bfx.BOARD_A.header.build_stage

        # ACT
        actual_out, log = _act_with_patch(assist.build_stage, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the build stage and include both the old and new values in the generated change log.
        """
        # ARRANGE
        header_in = replace(
            bfx.BOARD_A.header,
            build_stage="*" + bfx.BOARD_A.header.build_stage,  # invalid token to force correction
        )
        expected_out = bfx.BOARD_A.header.build_stage

        # ACT
        actual_out, log = _act_with_patch(assist.build_stage, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogContains(log, [header_in.build_stage, expected_out])


class TestBomDate(_Assert):
    """
    Unit tests for the `bom_date` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the date or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        header_in = bfx.BOARD_A.header
        expected_out = bfx.BOARD_A.header.bom_date

        # ACT
        actual_out, log = _act_with_patch(assist.bom_date, header_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the date and include both the old and new values in the generated change log.
        """
        # ARRANGE
        header_in = replace(
            bfx.BOARD_A.header,
            bom_date="*" + str(bfx.BOARD_A.header.bom_date),  # invalid token to force correction
        )
        expected_out = bfx.BOARD_A.header.bom_date

        # ACT
        actual_out, log = _act_with_patch(assist.bom_date, header_in, str(expected_out))

        # ASSERT
        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(header_in.bom_date), str(expected_out)])


class TestOverheadCost(_Assert):
    """
    Unit tests for the `overhead_cost` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the overhead cost or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        header_in = bfx.BOARD_A.header
        expected_out = bfx.BOARD_A.header.overhead_cost

        # ACT
        actual_out, log = _act_with_patch(assist.overhead_cost, header_in, str(expected_out))

        # ASSERT
        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the overhead cost and include both the old and new values in the generated change log.
        """
        # ARRANGE
        header_in = replace(
            bfx.BOARD_A.header,
            overhead_cost="*" + str(bfx.BOARD_A.header.overhead_cost),  # invalid token to force correction
        )
        expected_out = bfx.BOARD_A.header.overhead_cost

        # ACT
        actual_out, log = _act_with_patch(assist.overhead_cost, header_in, str(expected_out))

        # ASSERT
        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(header_in.overhead_cost), str(expected_out)])


class TestItem(_Assert):
    """
    Unit tests for the `item` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the item or generate a log entry when the initial value is already valid.
        """
        # ARRANGE
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.item

        # ACT
        actual_out, log = _act_with_patch(assist.item, row_in, expected_out)

        # ASSERT
        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the item and include both the old and new values in the generated change log.
        """
        # ARRANGE
        row_in = replace(bfx.BOARD_A.rows[0], item="*" + str(bfx.BOARD_A.rows[0].item))
        expected_out = bfx.BOARD_A.rows[0].item

        # ACT
        actual_out, log = _act_with_patch(assist.item, row_in, str(expected_out))

        # ASSERT
        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.item), str(expected_out)])


class TestComponentType(_Assert):
    """
    Unit tests for the `component_type` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the component type or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.component_type

        actual_out, log = _act_with_patch(assist.component_type, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the component type and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], component_type="*" + str(bfx.BOARD_A.rows[0].component_type))
        expected_out = bfx.BOARD_A.rows[0].component_type

        actual_out, log = _act_with_patch(assist.component_type, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.component_type), str(expected_out)])


class TestDevicePackage(_Assert):
    """
    Unit tests for the `device_package` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the device package or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.device_package

        actual_out, log = _act_with_patch(assist.device_package, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the device package and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], device_package="*" + str(bfx.BOARD_A.rows[0].device_package))
        expected_out = bfx.BOARD_A.rows[0].device_package

        actual_out, log = _act_with_patch(assist.device_package, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.device_package), str(expected_out)])


class TestDescription(_Assert):
    """
    Unit tests for the `description` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the description or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.description

        actual_out, log = _act_with_patch(assist.description, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the description and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], description="\n" + str(bfx.BOARD_A.rows[0].description))
        expected_out = bfx.BOARD_A.rows[0].description

        actual_out, log = _act_with_patch(assist.description, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.description), str(expected_out)])


class TestUnit(_Assert):
    """
    Unit tests for the `unit` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the units or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.units

        actual_out, log = _act_with_patch(assist.unit, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the unit and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], units="*" + str(bfx.BOARD_A.rows[0].units))
        expected_out = bfx.BOARD_A.rows[0].units

        actual_out, log = _act_with_patch(assist.unit, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.units), str(expected_out)])


class TestClassification(_Assert):
    """
    Unit tests for the `classification` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the classification or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.classification

        actual_out, log = _act_with_patch(assist.classification, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the classification and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], classification="*" + str(bfx.BOARD_A.rows[0].classification))
        expected_out = bfx.BOARD_A.rows[0].classification

        actual_out, log = _act_with_patch(assist.classification, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.classification), str(expected_out)])


class TestManufacturer(_Assert):
    """
    Unit tests for the `manufacturer` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the manufacturer or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.mfg_name

        actual_out, log = _act_with_patch(assist.manufacturer, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the manufacturer and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], mfg_name="*" + str(bfx.BOARD_A.rows[0].mfg_name))
        expected_out = bfx.BOARD_A.rows[0].mfg_name

        actual_out, log = _act_with_patch(assist.manufacturer, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.mfg_name), str(expected_out)])


class TestMfgPartNumber(_Assert):
    """
    Unit tests for the `mfg_part_number` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the manufacturer part number or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.mfg_part_number

        actual_out, log = _act_with_patch(assist.mfg_part_number, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the manufacturer part number and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], mfg_part_number="*" + str(bfx.BOARD_A.rows[0].mfg_part_number))
        expected_out = bfx.BOARD_A.rows[0].mfg_part_number

        actual_out, log = _act_with_patch(assist.mfg_part_number, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.mfg_part_number), str(expected_out)])


class TestUlVdeNumber(_Assert):
    """
    Unit tests for the `ul_vde_number` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the ul vde number or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.ul_vde_number

        actual_out, log = _act_with_patch(assist.ul_vde_number, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the ul vde number and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], ul_vde_number="*" + str(bfx.BOARD_A.rows[0].ul_vde_number))
        expected_out = bfx.BOARD_A.rows[0].ul_vde_number

        actual_out, log = _act_with_patch(assist.ul_vde_number, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.ul_vde_number), str(expected_out)])


class TestValidatedAt(_Assert):
    """
    Unit tests for the `validated_at` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the validated at or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.validated_at

        actual_out, log = _act_with_patch(assist.validated_at, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the validated at and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], validated_at="*" + str(bfx.BOARD_A.rows[0].validated_at))
        expected_out = bfx.BOARD_A.rows[0].validated_at

        actual_out, log = _act_with_patch(assist.validated_at, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.validated_at), str(expected_out)])


class TestQty(_Assert):
    """
    Unit tests for the `qty` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the qty or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.qty

        actual_out, log = _act_with_patch(assist.qty, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the qty and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], qty="*" + str(bfx.BOARD_A.rows[0].qty))
        expected_out = bfx.BOARD_A.rows[0].qty

        actual_out, log = _act_with_patch(assist.qty, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.qty), str(expected_out)])


class TestDesignator(_Assert):
    """
    Unit tests for the `designator` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the designator or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.designators

        actual_out, log = _act_with_patch(assist.designator, row_in, expected_out)

        self.assertValueOut(actual_out, expected_out)
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the designator and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], designators="*" + str(bfx.BOARD_A.rows[0].designators))
        expected_out = bfx.BOARD_A.rows[0].designators

        actual_out, log = _act_with_patch(assist.designator, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.designators), str(expected_out)])


class TestUnitPrice(_Assert):
    """
    Unit tests for the `unit_price` interactive correction helper.
    """

    def test_no_change(self):
        """
        Should NOT modify the unit price or generate a log entry when the initial value is already valid.
        """
        row_in = bfx.BOARD_A.rows[0]
        expected_out = row_in.unit_price

        actual_out, log = _act_with_patch(assist.unit_price, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogEmpty(log)

    def test_change(self):
        """
        Should update the unit price and include both the old and new values in the generated change log.
        """
        row_in = replace(bfx.BOARD_A.rows[0], unit_price="*" + str(bfx.BOARD_A.rows[0].unit_price))
        expected_out = bfx.BOARD_A.rows[0].unit_price

        actual_out, log = _act_with_patch(assist.unit_price, row_in, str(expected_out))

        self.assertValueOut(actual_out, str(expected_out))
        self.assertLogContains(log, [str(row_in.unit_price), str(expected_out)])


if __name__ == "__main__":
    unittest.main()
