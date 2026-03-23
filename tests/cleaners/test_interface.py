"""
Unit tests for the public interfaces of the `cleaners` package.

This module provides smoke tests for `src.cleaners.interfaces`, ensuring:
    - Public functions (e.g., v3_bom) are callable and return correct types
    - Clean inputs produce empty logs
    - Dirty inputs trigger coercion and non-empty logs

Example Usage:
    # Preferred usage via project-root invocation:
    python -m unittest tests/cleaners/test_interface.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - Internal Packages: src.cleaners.interfaces, tests.fixtures.v3_bom

Notes:
    - Focused on API surface verification, not detailed coercion logic.
    - Uses known-clean and minimally-dirty BOM fixtures for deterministic behavior.
    - Ensures interface stability across package-level refactors.

License:
    - Internal Use Only

"""

import unittest
from dataclasses import replace

from tests.fixtures import v3_bom as fx
from src.cleaners import interfaces as clean


class TestV3Bom(unittest.TestCase):
    """
    Tests for `v3_Bom`.
    """

    def test_valid(self):
        """
        Should keep BOM values unchanged and produce an empty log.
        """
        # ARRANGE
        src = fx.BOM_B  # Clean fixture
        # ACT
        out_bom, log = clean.clean_v3_bom(src)
        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=0):
            self.assertEqual(len(log), 0, log)
        with self.subTest("Type contract"):
            self.assertIsInstance(out_bom, type(src))
            self.assertIsInstance(log, tuple)

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
        out_bom, log = clean.clean_v3_bom(src_dirty)

        # ASSERT
        with self.subTest("Log size", Out=len(log), Exp=">0"):
            self.assertGreater(len(log), 0)


if __name__ == "__main__":
    unittest.main()
