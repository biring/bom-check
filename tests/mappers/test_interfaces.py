"""
Integration tests for the mappers public interface façade.

This module validates the behavior of the mappers.interfaces boundary, ensuring that canonical BOM mapping is correctly delegated to internal implementation modules and that errors are surfaced consistently to callers.

Example Usage:
    # Preferred usage via unittest runner:
    python -m unittest tests/mappers/test_interfaces.py

    # Direct discovery (runs all tests, including this module):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, dataclasses
    - Internal Packages: src.mappers.interfaces, src.models.interfaces, tests.fixtures

Notes:
    - Tests are integration-style and exercise the public façade only.
    - Internal mapper helpers are not patched; real implementations are invoked.
    - Success cases validate returned canonical model types.
    - Failure cases assert that mapping errors are surfaced as RuntimeError.
    - This module defines the behavioral contract for the mappers interface layer.

License:
    - Internal Use Only
"""

import unittest
from dataclasses import replace

from src.models import interfaces as model

# noinspection PyProtectedMember
from src.mappers import (
    interfaces as mapper,
)

from tests.fixtures import (
    v3_bom as fx_v3,
)


class TestInterfaces(unittest.TestCase):
    """
    Integration-style tests for the `mappers` public interface.
    """

    def test_map_v3_to_canonical_bom(self):
        """
        Should ...
        """
        # ARRANGE
        source_bom = fx_v3.BOM_A
        expected = model.CanonicalBom.__name__

        # ACT
        result = mapper.map_v3_to_canonical_bom(source_bom)
        actual = type(result).__name__

        # ASSERT
        with self.subTest("Output type", Out=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_map_v3_to_canonical_bom_raise(self):
        """
        Should raise an error when .....
        """
        # ARRANGE
        # Make board with bad material cost.
        bom = replace(
            fx_v3.BOM_A,
            boards=(
                replace(
                    fx_v3.BOARD_A,
                    header=replace(fx_v3.BOARD_A.header, material_cost="-99.99"),
                ),
            ),
        )
        expected = RuntimeError.__name__

        # ACT
        try:
            mapper.map_v3_to_canonical_bom(bom)
            actual = ""
        except Exception as ex:
            actual = type(ex).__name__

        # ASSERT
        with self.subTest("Raise type", Out=actual, Expected=expected):
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
