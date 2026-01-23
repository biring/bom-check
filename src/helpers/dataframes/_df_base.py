"""
Shared base utilities for working with pandas DataFrames at the cell and label level.

This module provides a thin wrapper around a pandas DataFrame to centralize low-level behaviors that are reused across higher-level DataFrame helpers. Its focus is on consistent label normalization and safe, explicit access to individual cell values without introducing any schema, record, or structural semantics.

Key responsibilities
	- Normalize arbitrary values into comparable string labels using shared sanitization rules.
	- Enforce explicit bounds checking when reading from or writing to DataFrame cells.
	- Provide minimal, predictable primitives for reading and writing individual cell values.

Example usage
	# Preferred usage via public package interface
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from src.helpers.dataframes._df_base import DataFrameBase
	df = pd.DataFrame([["A", "B"]])
	base = DataFrameBase(df)
	value = base.get_cell_str_value(0, 0)

Dependencies
	- Python 3.x
	- Standard Library: typing

Notes
	- This module intentionally avoids any notion of rows, records, schemas, or implicit resizing.
	- All bounds enforcement is explicit and raises immediately on invalid access.
	- Normalization behavior is centralized here to ensure consistent label comparison across the codebase.

License
	- Internal Use Only
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils import sanitizer


class DataFrameBase:
    """
    Shared, low-level DataFrame utilities.

    Scope:
    - Centralize normalization rules for label comparison
    - Provide minimal read/write primitives for individual cells

    Non-goals:
    - No record/sheet semantics (no cursors, no title discovery, no schema logic)
    - No implicit resizing or row/column creation
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize the DataFrameBase wrapper.

        Args:
            df (pd.DataFrame): DataFrame instance to wrap.

        Raises:
            TypeError: If df is not a pandas DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas.DataFrame")

        self.df: pd.DataFrame = df

    def _assert_in_bounds(self, row: int, col: int) -> None:
        """
        Assert that the given row and column indices are within DataFrame bounds.

        Args:
            row (int): Row index.
            col (int): Column index.

        Raises:
            IndexError: If row or column is out of DataFrame bounds.
        """
        max_rows, max_cols = self.df.shape

        if row < 0 or row >= max_rows:
            raise IndexError(f"Row index out of range: {row}")

        if col < 0 or col >= max_cols:
            raise IndexError(f"Column index out of range: {col}")

    @staticmethod
    def normalize(value: Any) -> str:
        """
        Normalize a value for label comparison.

        Rules:
        - Convert to string
        - Unicode normalize
        - Remove all whitespace
        - Lowercase

        Args:
            value (Any): Input value to normalize.

        Returns:
            str: Normalized string value.
        """
        normalized_value = sanitizer.normalize_to_string(value)
        no_whitespace_value = sanitizer.remove_all_whitespace(normalized_value)
        return no_whitespace_value.lower()

    def get_cell_str_value(self, row: int, col: int) -> str:
        """
        Read a DataFrame cell and return a safe, stripped string.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            str: Normalized string value of the cell.

        Raises:
            IndexError: If row or column is out of DataFrame bounds.
        """
        self._assert_in_bounds(row, col)
        cell_value = self.df.iat[row, col]
        string_value = sanitizer.normalize_to_string(cell_value)
        return string_value.strip()

    def set_cell_value(self, row: int, col: int, value: Any) -> None:
        """
        Write a value to a DataFrame cell.

        Intentionally minimal:
        - No normalization
        - No bounds correction
        - No row/column creation

        Args:
            row (int): Row index.
            col (int): Column index.
            value (Any): Value to assign.

        Raises:
            IndexError: If row or column is out of DataFrame bounds.
        """
        self._assert_in_bounds(row, col)
        self.df.iat[row, col] = value
