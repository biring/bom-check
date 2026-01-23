"""
Unit tests for a low-level DataFrame wrapper validating safe cell access and normalization behavior.

This test module verifies observable behaviors when interacting with a wrapped tabular data structure, including constructor input validation, value normalization rules, and explicit in-bounds and out-of-bounds read and write operations. The tests assert returned values, raised exceptions, and direct mutation of the provided data container without inferring or relying on higher-level semantics.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/helpers/dataframes/test__df_base.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- In-memory tabular data instances are constructed inline within individual test cases.
	- Test values include strings with surrounding whitespace, numeric values, and None.
	- No filesystem interaction, shared fixtures, or explicit cleanup logic is present.

Dependencies
	- Python 3.x
	- Standard Library: unittest

Notes
	- Tests depend on index-based access semantics and explicit IndexError propagation for invalid indices.
	- Normalization behavior is validated only through input and output assertions, not through internal implementation details.
	- All tests are deterministic and hermetic, relying solely on in-memory state.

License
	- Internal Use Only
"""

import unittest

import pandas as pd

# noinspection PyProtectedMember
from src.helpers.dataframes._df_base import DataFrameBase  # module under test


class TestDataFrameBase(unittest.TestCase):
    """
    Unit tests to verify low-level, safe read/write and normalization behavior for DataFrame cells.
    """

    def test_constructor_dataframe(self) -> None:
        """
        Should store the provided pandas DataFrame instance.
        """
        # ARRANGE
        df = pd.DataFrame([[1, 2]])

        # ACT
        base = DataFrameBase(df)

        # ASSERT
        with self.subTest("dataframe_identity", Act=base.df, Exp=df):
            self.assertIs(base.df, df)

    def test_constructor_non_dataframe(self) -> None:
        """
        Should raise a TypeError when input is not a pandas DataFrame.
        """
        # ARRANGE
        invalid_df = "not-a-dataframe"
        expected_exc = "TypeError"

        # ACT
        with self.assertRaises(TypeError) as ctx:
            DataFrameBase(invalid_df)  # type: ignore[arg-type]
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_normalize_string_with_whitespace(self) -> None:
        """
        Should remove all whitespace and lowercase the normalized string.
        """
        # ARRANGE
        value = "  Model  Number  "
        expected = "modelnumber"

        # ACT
        actual = DataFrameBase.normalize(value)

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_normalize_non_string_value(self) -> None:
        """
        Should convert non-string values into a normalized string.
        """
        # ARRANGE
        cases = [
            ("int", 123, "123"),
            ("float", 12.5, "12.5"),
            ("bool_true", True, "true"),
            ("bool_false", False, "false"),
        ]

        for case_name, value, expected in cases:
            with self.subTest("case_name", case_name=case_name):
                # ACT
                actual = DataFrameBase.normalize(value)

                # ASSERT
                with self.subTest(Act=actual, Exp=expected):
                    self.assertEqual(actual, expected)

    def test_get_cell_str_value_in_bounds(self) -> None:
        """
        Should return a stripped string value from the specified cell.
        """
        # ARRANGE
        df = pd.DataFrame([["  hello  "]])
        base = DataFrameBase(df)
        expected = "hello"

        # ACT
        actual = base.get_cell_str_value(0, 0)

        # ASSERT
        with self.subTest(Act=actual, Exp=expected):
            self.assertEqual(actual, expected)

    def test_get_cell_str_value_none(self) -> None:
        """
        Should return a string when the cell value is None.
        """
        # ARRANGE
        df = pd.DataFrame([[None]])
        base = DataFrameBase(df)

        # ACT
        actual = base.get_cell_str_value(0, 0)

        # ASSERT
        with self.subTest("return_type", Act=type(actual), Exp=str):
            self.assertIsInstance(actual, str)

    def test_get_cell_str_value_out_of_bounds(self) -> None:
        """
        Should raise IndexError when accessing a cell outside DataFrame bounds.
        """
        # ARRANGE
        df = pd.DataFrame([[1]])
        base = DataFrameBase(df)
        expected_exc = IndexError.__name__

        # ACT
        with self.assertRaises(IndexError) as ctx:
            base.get_cell_str_value(1, 0)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_set_cell_value_in_bounds(self) -> None:
        """
        Should write the provided value directly into the specified cell.
        """
        # ARRANGE
        df = pd.DataFrame([["a"]])
        base = DataFrameBase(df)
        value = "b"

        # ACT
        base.set_cell_value(0, 0, value)

        # ASSERT
        with self.subTest(Act=df.iat[0, 0], Exp=value):
            self.assertEqual(df.iat[0, 0], value)

    def test_set_cell_value_out_of_bounds(self) -> None:
        """
        Should raise IndexError when writing to a cell outside DataFrame bounds.
        """
        # ARRANGE
        df = pd.DataFrame([[1]])
        base = DataFrameBase(df)
        expected_exc = IndexError.__name__

        # ACT
        with self.assertRaises(IndexError) as ctx:
            base.set_cell_value(0, 1, 42)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)


if __name__ == "__main__":
    unittest.main()
