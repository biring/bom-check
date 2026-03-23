"""
Unit tests for the public interfaces of the `fixer` package.

This module provides smoke tests for `src.fixer.interfaces`, ensuring:
    - Public functions (e.g., v3_bom) are callable and return correct types
    - Clean inputs produce empty logs
    - Dirty inputs trigger coercion and non-empty logs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/fixer/test_interface.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - Internal Packages: src.fixer.interfaces, tests.fixtures.v3_bom

Notes:
    - Focused on API surface verification, not detailed fixer logic.
    - Uses known-clean and minimally-dirty BOM fixtures for deterministic behavior.
    - Ensures interface stability across package-level refactors.

License:
    - Internal Use Only

"""
import importlib
import unittest
from dataclasses import replace
from unittest.mock import patch

from tests.fixtures import v3_bom as fx
from src.fixer import interfaces as fixer


class TestV3Bom(unittest.TestCase):
    """
    Tests for `v3_Bom`.
    """

    def test_valid(self):
        """
        Should keep BOM values unchanged and produce an empty log.
        """
        # ARRANGE
        src = fx.BOM_A  # Clean fixture

        # ACT
        out_bom, log = fixer.fix_v3_bom(src)

        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=0):
            self.assertEqual(len(log), 0, log)
        with self.subTest("Type contract"):
            self.assertIsInstance(out_bom, type(src))
            self.assertIsInstance(log, tuple)

    def test_invalid(self):
        """
        Should fix values for a minimally dirty BOM and produce a non-empty log.
        """
        # ARRANGE (start clean and change total cost to trigger auto fix)
        bom_in = replace(
            fx.BOM_A, boards=(
                replace(
                    fx.BOARD_A, header=replace(
                        fx.BOARD_A.header, total_cost="999"
                    ),
                ),
            ),
        )

        # ACT
        bom_out, log = fixer.fix_v3_bom(bom_in)

        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=">0"):
            self.assertGreater(len(log), 0)


if __name__ == "__main__":
    unittest.main()
