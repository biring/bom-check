"""
Tests for verifying the public interface façade exposes canonical BOM export to version 3 template sheets.

This module validates the public contract of the transformation interface by asserting that an approved canonical-to-template export entry point is exposed, callable, and returns a mapping whose values are pandas DataFrame objects when provided with canonical BOM input and a version 3 template. The tests intentionally limit scope to interface exposure and return-type guarantees and do not assert on transformation behavior or data correctness.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/transformers/test_interfaces.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- Canonical BOM input is provided by a shared fixture containing a predefined canonical representation.
	- The version 3 BOM template is loaded via an importer utility returning a pandas DataFrame.
	- No temporary files or directories are created and no explicit cleanup is performed.

Dependencies
	- Python 3.x
	- Standard Library:
		- unittest

Notes
	- The test enforces the public interface contract only and treats the system under test as an external dependency.
	- Assertions are limited to callability and return types and deliberately avoid validating DataFrame contents.
	- Determinism relies on the stability of the canonical fixture and the template loader.

License
	Internal Use Only
"""


import unittest

import pandas as pd

from src.transformers import interfaces
from src.importers.interfaces import load_version3_bom_template
from tests.fixtures import canonical as fx_canonical


class TestInterfaces(unittest.TestCase):
    """
    Unit tests to verify the public façade exposes canonical BOM export to V3 template sheets.
    """

    def test_canonical_to_v3_template_sheets(self) -> None:
        """
        Should expose the function via the public interface and return a dict on the happy path.
        """
        # ARRANGE
        fn = getattr(interfaces, "canonical_to_v3_template_sheets", None)
        canonical_bom = fx_canonical.BOM_A_CANONICAL
        template_df = load_version3_bom_template()

        # ACT
        result = fn(canonical_bom, template_df)

        # ASSERT
        with self.subTest("callable_exists", Act=callable(fn), Exp=True):
            self.assertTrue(callable(fn))

        with self.subTest("return_type", Act=type(result), Exp=dict):
            self.assertIsInstance(result, dict)

        # The public contract promises DataFrame values, not content correctness
        for key, value in result.items():
            with self.subTest("sheet_value_type", Act=type(value), Exp=pd.DataFrame):
                self.assertIsInstance(value, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()
