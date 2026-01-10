"""
Unit tests for BOM header field coercers.

These tests validate that each coercer (model number, board name/supplier, build stage, BOM date, and cost fields):
    - Produces the expected normalized output string
    - Emits log messages only for effective rule applications
    - Applies its rule set deterministically via the shared coercion engine

Example Usage:
    # Run this module directly:
    python -m unittest tests/coerce/test__header.py

    # Discover and execute all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses, typing
    - Internal: src.coerce._header, src.coerce._helper, src.coerce._rules, src.coerce._regex, src.models.interfaces
    - External Packages: None

Notes:
    - Each test class targets one field coercer and uses `CoercionCase` fixtures for deterministic assertions.
    - Assertions confirm both transformed values and corresponding log descriptions.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import dataclass

from src.schemas.interfaces import (
    HeaderLabelsV3,
)

from tests.fixtures import v3_value as vfx
# noinspection PyProtectedMember
from src.coerce import _header as header  # Direct internal import — acceptable in tests
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


class TestModelNumber(Assert):
    """
    Unit tests for `model_number` function.
    """
    attr = HeaderLabelsV3.MODEL_NO

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("BA400ul", "BA400UL", regex.TO_UPPER.description),
            CoercionCase("BA400\tUL\n", "BA400UL", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.model_number(case.value_in)
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
        for model_number in vfx.MODEL_NO_GOOD:
            cases.append(CoercionCase(model_number, model_number, ""))
        # ACT
        for case in cases:
            result, logs = header.model_number(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestBoardName(Assert):
    """
    Unit tests for `board_name` function.
    """
    attr = HeaderLabelsV3.BOARD_NAME

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("Power\t \nPCBA", "Power PCBA", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
            CoercionCase("Power  PCBA", "Power PCBA", regex.COLLAPSE_MULTIPLE_SPACES.description),
            CoercionCase(" Power PCBA ", "Power PCBA", regex.STRIP_EDGE_SPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.board_name(case.value_in)
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
        for board_name in vfx.BOARD_NAME_GOOD:
            cases.append(CoercionCase(board_name, board_name, ""))
        # ACT
        for case in cases:
            result, logs = header.board_name(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestBoardSupplier(Assert):
    """
    Unit tests for `board_supplier` function.
    """
    attr = HeaderLabelsV3.BOARD_SUPPLIER

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("General \tElectric\n", "General Electric", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
            CoercionCase("General  Electric", "General Electric", regex.COLLAPSE_MULTIPLE_SPACES.description),
            CoercionCase(" General Electric ", "General Electric", regex.STRIP_EDGE_SPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.board_supplier(case.value_in)
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
        for board_supplier in vfx.BOARD_SUPPLIER_GOOD:
            cases.append(CoercionCase(board_supplier, board_supplier, ""))
        # ACT
        for case in cases:
            result, logs = header.board_supplier(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestBuildStage(Assert):
    """
    Unit tests for `build_stage` function.
    """
    attr = HeaderLabelsV3.BUILD_STAGE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("EB 1\n", "EB1", regex.REMOVE_WHITESPACES.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.build_stage(case.value_in)
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
        for build_stage in vfx.BUILD_STAGE_GOOD:
            cases.append(CoercionCase(build_stage, build_stage, ""))
        # ACT
        for case in cases:
            result, logs = header.build_stage(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestBomDate(Assert):
    """
    Unit tests for `bom_date` function.
    """
    attr = HeaderLabelsV3.BOM_DATE

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase("\t1/1/2025\n", "1/1/2025", regex.REMOVE_WHITESPACES_EXCEPT_SPACE.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.bom_date(case.value_in)
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
        for bom_date in vfx.BOM_DATE_GOOD:
            cases.append(CoercionCase(bom_date, bom_date, ""))
        # ACT
        for case in cases:
            result, logs = header.bom_date(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestMaterialCost(Assert):
    """
    Unit tests for `material_cost` function.
    """
    attr = HeaderLabelsV3.MATERIAL_COST

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" 1.25 \n", "1.25", regex.REMOVE_WHITESPACES.description),
            CoercionCase("", "0", regex.EMPTY_TO_ZERO.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.material_cost(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = []
        for cost in vfx.COST_GOOD:
            cases.append(CoercionCase(cost, cost, ""))
        # ACT
        for case in cases:
            result, logs = header.material_cost(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestOverheadCost(Assert):
    """
    Unit tests for `overhead_cost` function.
    """
    attr = HeaderLabelsV3.OVERHEAD_COST

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" 1.25 \n", "1.25", regex.REMOVE_WHITESPACES.description),
            CoercionCase("", "0", regex.EMPTY_TO_ZERO.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.overhead_cost(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = []
        for cost in vfx.COST_GOOD:
            cases.append(CoercionCase(cost, cost, ""))
        # ACT
        for case in cases:
            result, logs = header.overhead_cost(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


class TestTotalCost(Assert):
    """
    Unit tests for `overhead_cost` function.
    """
    attr = HeaderLabelsV3.TOTAL_COST

    def test_change(self):
        """
        Should apply the rule and record rule log entry.
        """
        # ARRANGE
        cases = [
            CoercionCase(" 1.25 \n", "1.25", regex.REMOVE_WHITESPACES.description),
            CoercionCase("", "0", regex.EMPTY_TO_ZERO.description),
        ]
        # ACT
        for case in cases:
            result, logs = header.total_cost(case.value_in)
            # ASSERT
            self.assert_change(case=case, result=result, logs=logs)

    def test_no_change(self):
        """
        Should return the input text unchanged and an empty log when there is no rule match.
        """
        # ARRANGE
        cases = []
        for cost in vfx.COST_GOOD:
            cases.append(CoercionCase(cost, cost, ""))
        # ACT
        for case in cases:
            result, logs = header.total_cost(case.value_in)
            # ASSERT
            self.assert_no_change(case=case, result=result, logs=logs)


if __name__ == "__main__":
    unittest.main()
