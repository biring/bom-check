"""
Unit tests for BOM row field coercers.

These tests validate that each coercer (e.g., item, component type, device package, description, quantity, designator, unit price, etc.):
    - Produces the expected normalized output string
    - Emits exactly one log entry per effective rule match
    - Applies regex-based rules in a deterministic order via the shared coercion engine

Example Usage:
    # Run this module directly:
    python -m unittest tests/coerce/test__row.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses, typing
    - Internal: src.coerce._row, src.coerce._helper, src.coerce._regex, src.models.interfaces

Notes:
    - Each test class targets one field coercer and uses `CoercionCase` fixtures for deterministic validation.
    - Assertions confirm both output normalization and expected log message consistency.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import dataclass

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)
from src.models import interfaces as mdl
from tests.fixtures import v3_value as vfx
# noinspection PyProtectedMember
from src.coerce import _helper as common  # Direct internal import — acceptable in tests
# noinspection PyProtectedMember
from src.coerce import _row as row  # Direct internal import — acceptable in tests
# noinspection PyProtectedMember
from src.coerce import _regex as regex  # Direct internal import — acceptable in tests


@dataclass
class CoercionCase:
    """
    Test fixture container for a single coercion scenario.

    Holds the input value, the expected normalized output, and the
    expected log message (if any) produced during coercion. Used by
    shared assertion helpers to verify deterministic behavior.

    Args:
        value_in (str): The raw input value before coercion.
        value_out (str): The expected normalized output value after coercion.
        expected_log (str): The expected log message describing the applied rule.
    """
    value_in: str = ""
    value_out: str = ""
    expected_log: str = ""


class Assert(unittest.TestCase):
    """
    Abstract base class providing common assertions for row coercer tests.
    """

    def assert_change(self, case: CoercionCase, result: str, logs: tuple[str, ...]):
        """
        Assert that a coercion changed the value and produced exactly one expected log entry.

        Args:
            case (CoercionCase): Input/output fixture holding value_in, value_out, and expected_log.
            result (common.Result): Coercion result to validate.
            logs: tuple[str, ...]: list of log strings.

        Returns:
            None: Raises on assertion failure.
        """
        # Single-log invariant: result.logs must contain exactly one entry.
        # We still join to keep the comparer stable if multi-log support returns later.
        log_list = ",".join(log for log in logs)

        with self.subTest("Value Out", Out=result, Exp=case.value_out):
            self.assertEqual(result, case.value_out)
        with self.subTest("Log Count", Out=len(logs), Exp=1):
            self.assertEqual(len(logs), 1)
        with self.subTest("Log message", Out=log_list, Exp=case.expected_log):
            self.assertIn(case.expected_log, log_list)

    def assert_no_change(self, case: CoercionCase, result: str, logs: tuple[str, ...]):
        """
        Assert that no coercion was applied and no logs were produced.

        Args:
            case (CoercionCase): Input/output fixture holding value_in and value_out.
            result (common.Result): Coercion result to validate.
            logs: tuple[str, ...]: list of log strings.

        Returns:
            None: Raises on assertion failure.
        """
        with self.subTest("Value Out", Out=result, Exp=case.value_in):
            self.assertEqual(result, case.value_in)
        with self.subTest("Log Count", Out=len(logs), Exp=0):
            self.assertEqual(len(logs), 0)


class TestItem(Assert):
    """
    Unit tests for `item` function.
    """
    attr = TableLabelsV3.ITEM

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" \t1\n", "1", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.item(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.ITEM_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.item(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestComponentType(Assert):
    """
    Unit tests for `component_type` function.
    """
    attr = TableLabelsV3.COMPONENT_TYPE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\tSilicon Diode\n", "Silicon Diode", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.component_type(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.COMP_TYPE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.component_type(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestDevicePackage(Assert):
    """
    Unit tests for `device_package` function.
    """
    attr = TableLabelsV3.DEVICE_PACKAGE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\tSOIC \n8", "SOIC 8", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
            CoercionCase("99*54mm", "99x54mm", regex.DIMENSION_SEPARATOR_STAR.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.device_package(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.DEVICE_PACKAGE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.device_package(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestDescription(Assert):
    """
    Unit tests for `description` function.
    """
    attr = TableLabelsV3.DESCRIPTION

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nRes, 1k,\t 0603", "Res, 1k, 0603", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.description(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.DESCRIPTION_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.description(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestUnits(Assert):
    """
    Unit tests for `units` function.
    """
    attr = TableLabelsV3.UNITS

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" \nPCS\t. ", "PCS.", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.units(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.UNITS_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.units(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestClassification(Assert):
    """
    Unit tests for `classification` function.
    """
    attr = TableLabelsV3.CLASSIFICATION

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" \nZ\t ", "Z", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.classification(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.CLASSIFICATION_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.classification(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestManufacturer(Assert):
    """
    Unit tests for `manufacturer` function.
    """
    attr = TableLabelsV3.MFG_NAME

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nDelta\t Systems Inc.", "Delta Systems Inc.",
                         regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.manufacturer(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.MFG_NAME_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.manufacturer(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestManufacturerPartNumber(Assert):
    """
    Unit tests for `manufacturer_part_number` function.
    """
    attr = TableLabelsV3.MFG_PART_NO

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nTCS-34\t ACS", "TCS-34 ACS", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.mfg_part_number(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.MFG_PART_NO_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.mfg_part_number(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestUlVdeNumber(Assert):
    """
    Unit tests for `ul_vde_number` function.
    """
    attr = TableLabelsV3.UL_VDE_NO

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nABC:\t 123", "ABC: 123", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.ul_vde_number(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.UL_VDE_NO_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.ul_vde_number(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestValidationAt(Assert):
    """
    Unit tests for `validated_at` function.
    """
    attr = TableLabelsV3.VALIDATED_AT

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" EB1,\nEB2,\tMP ", "EB1,EB2,MP", regex.REMOVE_WHITESPACES.description),
            CoercionCase("/", "", regex.REMOVE_STANDALONE_FORWARD_SLASH.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.validated_at(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.VALIDATED_AT_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.validated_at(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestQuantity(Assert):
    """
    Unit tests for `quantity` function.
    """
    attr = TableLabelsV3.QUANTITY

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\n1 \t", "1", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.quantity(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.QUANTITY_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.quantity(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestDesignator(Assert):
    """
    Unit tests for `designator` function.
    """
    attr = TableLabelsV3.DESIGNATORS

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\nR1, \tR2, ", "R1,R2,", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.designator(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
            CoercionCase("", "", ""),
        ]
        for value in vfx.DESIGNATOR_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.designator(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestUnitPrice(Assert):
    """
    Unit tests for `unit_price` function.
    """
    attr = TableLabelsV3.UNIT_PRICE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\n1.24\t ", "1.24", regex.REMOVE_WHITESPACES.description),
            CoercionCase("", "0", regex.EMPTY_TO_ZERO.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.unit_price(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = []
        for value in vfx.PRICE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.unit_price(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestSubTotal(Assert):
    """
    Unit tests for `sub_total` function.
    """
    attr = TableLabelsV3.SUB_TOTAL

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\n1.24\t ", "1.24", regex.REMOVE_WHITESPACES.description),
            CoercionCase("", "0", regex.EMPTY_TO_ZERO.description),
        ]
        # ACT
        for case in cases:
            result, logs = row.sub_total(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = [
        ]
        for value in vfx.PRICE_GOOD:
            cases.append(CoercionCase(value, value, ""))
        # ACT
        for case in cases:
            result, logs = row.sub_total(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


if __name__ == "__main__":
    unittest.main()
