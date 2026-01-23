"""
Row-oriented record access layer over a pandas DataFrame with schema resolution.

This module provides an abstraction for working with record-style tables embedded within pandas DataFrames where column titles may appear on arbitrary rows and records are defined as rows beneath that title row. It resolves a stable schema at construction time based on identifying titles and exposes deterministic read and append semantics relative to that title row.

Key responsibilities
	- Resolve a title row using required identifying titles.
	- Capture an immutable schema mapping record field titles to DataFrame columns.
	- Provide title-relative, row-oriented read access to record data.
	- Append new records immediately after the last non-blank record row.
	- Enforce deterministic bounds for reads after schema resolution and caching.

Example usage
	# Preferred usage via public package interface
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from package.subpackage import Record
	record = Record(df, title_identifiers=("Part Number", "Quantity"))
	row = record.read_record(0)

Dependencies
	- Python 3.x
	- Standard Library:
		- dataclasses
		- typing

Notes
	- The title row is fixed at construction time and never re-evaluated.
	- Title matching is performed using normalized string comparison.
	- The first occurrence of a normalized title is treated as authoritative.
	- Blank record rows are defined as rows where all mapped record fields are empty strings.
	- This module mutates the underlying DataFrame when appending records.

License
	- Internal Use Only
"""



from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ._df_base import _DataFrameBase


@dataclass(frozen=True, slots=True)
class _RecordSchema:
    """
    Capture resolved schema information for row-oriented record access.

    This object is immutable once constructed and represents a stable interpretation of a title row within a DataFrame.

    Attributes:
        title_row (int): DataFrame row index containing the record field titles.
        title_to_col (dict[str, int]): Mapping of normalized title to column index.
        titles_original (list[str]): Original, display-form titles in left-to-right order.
    """

    title_row: int
    title_to_col: dict[str, int]
    titles_original: list[str]


class Record(_DataFrameBase):
    """
    Provide row-oriented record read and write access over a pandas DataFrame.

    Responsibility:
    - Locate a title row using identifying titles.
    - Expose record-relative read access below that title row.
    - Append new records immediately after the last non-blank record row.

    Invariants:
    - The title row is fixed at construction time.
    - Column resolution is performed via normalized title matching.
    - The first occurrence of a normalized title is authoritative.

    Attributes:
        df (pd.DataFrame): Backing DataFrame inherited from DataFrameBase.
        title_identifiers (tuple[str, ...]): Required titles used to locate the title row.
        _schema (_RecordSchema): Resolved schema derived from the title row.
        _record_count (int | None): Cached count of readable records after reset_read().
        _last_filled_df_row (int | None): Cached last filled DataFrame row for record data.
    """

    def __init__(self, df: pd.DataFrame, *, title_identifiers: tuple[str, ...]) -> None:
        """
        Initialize the Record wrapper and resolve the record schema.

        Args:
            df (pd.DataFrame): DataFrame containing a record-style table.
            title_identifiers (tuple[str, ...]): Non-empty tuple of titles identifying the title row.

        Raises:
            ValueError: If title_identifiers is empty.
            ValueError: If no suitable title row can be located.
        """
        # Enforce that at least one identifier is provided, otherwise title row resolution is undefined.
        if not title_identifiers:
            raise ValueError("title identifiers must be a non-empty tuple")

        # Bypass cooperative MRO to avoid unintended Metadata initialization.
        _DataFrameBase.__init__(self, df)

        # Persist identifiers exactly as provided; normalization is applied only during lookup.
        self.title_identifiers: tuple[str, ...] = title_identifiers

        # Resolve the title row and construct a schema snapshot immediately.
        title_row = self._find_title_row_from_identifiers(self.title_identifiers)
        self._schema: _RecordSchema = self._build_schema_from_title_row(title_row)

        # Initialize caches used to enforce deterministic bounds after reads and writes.
        self._record_count: int | None = None
        self._last_filled_df_row: int | None = None

    def reset_read(self) -> int:
        """
        Recompute and return the number of available record rows.

        Data rows are defined as those starting immediately below the title row and extending through the last row that contains at least one non-blank mapped record field.

        Returns:
            int: Number of readable record rows.
        """
        schema = self._schema
        start_row = schema.title_row + 1

        # Scan from the bottom to determine the authoritative end of record data.
        last_filled = self._find_last_filled_record_df_row()
        self._last_filled_df_row = last_filled

        # If no data rows contain values, expose zero records.
        if last_filled < start_row:
            self._record_count = 0
            return 0

        # Record count is derived strictly from title row relative indexing.
        self._record_count = (last_filled - start_row) + 1
        return self._record_count

    def read_record(
            self,
            index: int,
            *,
            labels: tuple[str, ...] | None = None,
            strict: bool = False,
    ) -> dict[str, str]:
        """
        Read a single record using a 0-based index relative to the title row.

        Args:
            index (int): Record-relative index where 0 is the first data row.
            labels (tuple[str, ...] | None): Optional subset of labels to read.
            strict (bool): Whether missing labels raise KeyError. Defaults to False.

        Returns:
            dict[str, str]: Mapping of label to string cell value.

        Raises:
            IndexError: If the index is negative or out of bounds.
            KeyError: If strict is True and a requested label is not present.
        """
        # Negative indices are explicitly disallowed to avoid ambiguity.
        if index < 0:
            raise IndexError(f"Record index out of bounds: {index}")

        schema = self._schema
        start_row = schema.title_row + 1
        df_row = start_row + index

        # If reset_read() has been called, enforce its cached bounds deterministically.
        if self._record_count is not None and index >= self._record_count:
            raise IndexError(f"Record index out of bounds: {index}")

        # Always enforce physical DataFrame bounds regardless of cache state.
        if df_row >= self.df.shape[0]:
            raise IndexError(f"Record index out of bounds: {index}")

        title_to_col = schema.title_to_col

        # When no labels are specified, expose all fields using original display titles.
        if labels is None:
            out: dict[str, str] = {}
            for original_label in schema.titles_original:
                col = title_to_col.get(self.normalize(original_label))
                # Missing columns are silently skipped to preserve forward compatibility.
                if col is None:
                    continue
                out[original_label] = self.get_cell_str_value(df_row, col)
            return out

        # Otherwise, resolve and return only the requested labels.
        out_subset: dict[str, str] = {}
        for label in labels:
            col = title_to_col.get(self.normalize(label))
            if col is None:
                # Strict mode enforces schema fidelity for callers expecting exact templates.
                if strict:
                    raise KeyError(f"Template record title missing field: {label!r}")
                out_subset[label] = ""
                continue

            out_subset[label] = self.get_cell_str_value(df_row, col)

        return out_subset

    def write_record(self, label_value_map: dict[str, Any], *, strict: bool = True) -> int:
        """
        Append a new record row directly under the last filled record row.

        Args:
            label_value_map (dict[str, Any]): Mapping of field label to value.
            strict (bool): Whether unknown labels raise KeyError. Defaults to True.

        Returns:
            int: Record-relative index of the newly written record.

        Raises:
            KeyError: If strict is True and a provided label does not exist.
        """
        schema = self._schema
        start_row = schema.title_row + 1

        # Prefer cached position to avoid rescanning when performing multiple writes.
        last_filled = self._last_filled_df_row
        if last_filled is None:
            last_filled = self._find_last_filled_record_df_row()

        # Target row is always immediately after the last non-blank record row.
        target_df_row = max(start_row, last_filled + 1)

        # Grow the DataFrame if the append position exceeds current bounds.
        self._ensure_row_exists(target_df_row)

        title_to_col = schema.title_to_col

        for label, value in label_value_map.items():
            col = title_to_col.get(self.normalize(label))
            if col is None:
                # Strict mode treats schema mismatch as a hard failure.
                if strict:
                    raise KeyError(f"Template record title missing required field: {label!r}")
                continue

            self.set_cell_value(target_df_row, col, value)

        # Update caches so subsequent reads and writes remain consistent.
        self._last_filled_df_row = target_df_row
        if self._record_count is not None:
            self._record_count = (target_df_row - start_row) + 1

        return target_df_row - start_row

    def _find_title_row_from_identifiers(self, identifiers: tuple[str, ...]) -> int:
        """
        Locate the DataFrame row that best matches the required title identifiers.

        The first row containing all identifiers is returned immediately. Otherwise, the closest partial match is tracked to produce a useful error.

        Args:
            identifiers (tuple[str, ...]): Required titles.

        Returns:
            int: DataFrame row index of the resolved title row.

        Raises:
            ValueError: If no row contains all required identifiers.
        """
        required_norm = {self.normalize(x) for x in identifiers}

        best_row: int | None = None
        best_missing_norm: set[str] | None = None

        n_rows, n_cols = self.df.shape

        for r in range(n_rows):
            present_norm: set[str] = set()

            for c in range(n_cols):
                cell_str = self.get_cell_str_value(r, c)
                if not cell_str:
                    continue

                key = self.normalize(cell_str)
                if key in required_norm:
                    present_norm.add(key)
                    # Exit early once all identifiers are found to avoid unnecessary scanning.
                    if len(present_norm) == len(required_norm):
                        return r

            # Track the closest partial match for diagnostic purposes.
            missing_norm = required_norm - present_norm
            if best_missing_norm is None or len(missing_norm) < len(best_missing_norm):
                best_missing_norm = missing_norm
                best_row = r

        # Convert missing normalized identifiers back to original display strings.
        missing_original = (
            [x for x in identifiers if self.normalize(x) in (best_missing_norm or set())]
            if best_missing_norm is not None
            else list(identifiers)
        )

        raise ValueError(
            "Could not locate a record title row matching all identifiers. "
            f"Best candidate row index={best_row}, missing identifiers={missing_original}"
        )

    def _build_schema_from_title_row(self, title_row: int) -> _RecordSchema:
        """
        Construct a RecordSchema from the resolved title row.

        Args:
            title_row (int): DataFrame row index containing the titles.

        Returns:
            _RecordSchema: Immutable schema describing column mappings.
        """
        title_to_col: dict[str, int] = {}
        titles_original: list[str] = []

        for col_idx in range(self.df.shape[1]):
            label = self.get_cell_str_value(title_row, col_idx)
            if not label:
                continue

            titles_original.append(label)
            # First occurrence wins to ensure deterministic resolution.
            title_to_col.setdefault(self.normalize(label), col_idx)

        return _RecordSchema(
            title_row=title_row,
            title_to_col=title_to_col,
            titles_original=titles_original,
        )

    def _find_last_filled_record_df_row(self) -> int:
        """
        Return the last DataFrame row index containing any record field data.

        Rows are considered blank only if all mapped record field columns are empty. If no such data rows exist, the title row index is returned.

        Returns:
            int: DataFrame row index of the last filled record row.
        """
        schema = self._schema
        start_row = schema.title_row + 1
        cols = list(schema.title_to_col.values())

        # If the DataFrame ends before data could begin, treat as empty.
        if start_row >= self.df.shape[0]:
            return schema.title_row

        # Scan bottom-up to find the last non-blank record row.
        for r in range(self.df.shape[0] - 1, start_row - 1, -1):
            if not self._is_record_row_blank(r, cols):
                return r

        return schema.title_row

    def _is_record_row_blank(self, row: int, cols: list[int]) -> bool:
        """
        Determine whether a given row is blank across all record field columns.

        Args:
            row (int): DataFrame row index to inspect.
            cols (list[int]): Column indices corresponding to record fields.

        Returns:
            bool: True if all inspected cells are empty strings.
        """
        for c in cols:
            if self.get_cell_str_value(row, c) != "":
                return False
        return True

    def _ensure_row_exists(self, row_idx: int) -> None:
        """
        Ensure that the DataFrame has at least row_idx + 1 rows.

        This method mutates the underlying DataFrame by appending empty rows when required.

        Args:
            row_idx (int): Required DataFrame row index.
        """
        current_rows = self.df.shape[0]
        if row_idx < current_rows:
            return

        rows_to_add = row_idx - current_rows + 1
        empty = pd.DataFrame(
            [[""] * self.df.shape[1]] * rows_to_add,
            columns=self.df.columns,
        )
        self.df = pd.concat([self.df, empty], ignore_index=True)
