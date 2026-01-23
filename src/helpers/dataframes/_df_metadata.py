"""
Metadata-oriented DataFrame wrapper enforcing template structure and offset-based access.

This module provides a specialized wrapper around a tabular data structure to validate the presence of required identifying labels and to support reading and writing of metadata values at positions defined relative to those labels. It is intended for scenarios where spreadsheets or similar grid-based data act as loosely structured templates, and where positional consistency must be enforced before interacting with metadata values.

Key responsibilities
	- Validate that a tabular dataset contains a required set of identifying labels using normalized comparison.
	- Locate the first occurrence of each identifying label and treat it as the authoritative anchor.
	- Read metadata values using row and column offsets relative to labeled anchor cells.
	- Write metadata values using row and column offsets, extending rows as needed while preserving column structure.

Example usage
	# Preferred usage via public package interface
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from src.helpers.dataframes._df_metadata import Metadata
	meta = Metadata(df, ("Part Number", "Revision"))
	values = meta.read_metadata({"Part Number": (0, 1)})

Dependencies
	- Python 3.x
	- Standard Library: None

Notes
	- Template identifiers must be non-empty and are validated eagerly during initialization.
	- Normalized matching is used to tolerate superficial formatting differences in labels.
	- Only the first occurrence of a label is used; subsequent duplicates are ignored.
	- Column growth is intentionally disallowed to preserve template integrity.

License
	- Internal Use Only
"""

from __future__ import annotations

import pandas as pd

from ._df_base import DataFrameBase


class Metadata(DataFrameBase):
    """
    Enforce and interact with a metadata-oriented DataFrame template.

    This class validates that a backing DataFrame contains a required set
    of identifying labels and provides offset-based read and write access
    to metadata values relative to those labels.

    Invariants:
    - At least one template identifier must be provided.
    - Template identifiers are matched using normalized comparison.
    - The first occurrence of a label is authoritative and later duplicates are ignored.

    Attributes:
        template_identifiers (tuple[str, ...]): Required labels identifying the template.
    """

    def __init__(self, df: pd.DataFrame, template_identifiers: tuple[str, ...]) -> None:
        """
        Initialize the metadata wrapper and validate the expected template.

        This constructor fails fast if the provided identifiers are empty or
        if the DataFrame does not structurally match the expected template.

        Args:
            df (pd.DataFrame): Backing DataFrame containing metadata.
            template_identifiers (tuple[str, ...]): Required template labels.

        Raises:
            ValueError: If template_identifiers is empty.
            ValueError: If the DataFrame does not contain all required identifiers.
        """
        # A metadata template with no identifiers cannot be validated and would
        # silently accept arbitrary DataFrames, which is considered unsafe
        if not template_identifiers:
            raise ValueError("template_identifiers must be a non-empty tuple")

        # Intentionally bypass super() to avoid incompatible initialization
        # paths in subclasses that may assume record-oriented semantics
        DataFrameBase.__init__(self, df)

        # Preserve the original identifiers exactly as provided so downstream
        # error messages reflect user-facing terminology
        self.template_identifiers: tuple[str, ...] = template_identifiers

        # Validate immediately so all subsequent operations can assume
        # the presence of required template anchors
        self._validate_expected_template()

    def _validate_expected_template(self) -> None:
        """
        Verify that all required template identifiers exist in the DataFrame.

        The DataFrame grid is scanned in full because identifiers may appear
        anywhere. Matching is performed using normalized comparison, and
        scanning exits early once all required identifiers are found.

        Raises:
            ValueError: If one or more required identifiers are missing.
        """
        # Normalize identifiers once to ensure consistent comparison semantics
        required = {self.normalize(identifier) for identifier in self.template_identifiers}
        found: set[str] = set()

        row_count, col_count = self.df.shape

        # Full grid scan is required because no positional guarantees exist
        for row in range(row_count):
            for col in range(col_count):
                cell = self.get_cell_str_value(row, col)
                if not cell:
                    # Empty or non-string cells cannot satisfy identifier requirements
                    continue

                key = self.normalize(cell)
                if key in required:
                    found.add(key)

                    # Exit early once all required identifiers are located to
                    # avoid unnecessary additional scanning
                    if len(found) == len(required):
                        return

        # Determine which identifiers were never observed using original labels
        missing = [
            identifier
            for identifier in self.template_identifiers
            if self.normalize(identifier) not in found
        ]

        # Missing identifiers indicate a structural mismatch that would
        # invalidate all offset-based access assumptions
        raise ValueError(
            f"Sheet does not match expected template. Missing identifiers: {missing}"
        )

    def _ensure_row_exists(self, row_idx: int) -> None:
        """
        Ensure the DataFrame has at least row_idx + 1 rows.

        Rows are appended as needed and initialized with empty strings so
        string-based metadata handling remains consistent.

        Args:
            row_idx (int): Target row index that must exist.
        """
        current_rows = self.df.shape[0]

        # No mutation is required if the requested row already exists
        if row_idx < current_rows:
            return

        # Calculate how many rows must be appended to reach the desired index
        rows_to_add = row_idx - current_rows + 1

        # Initialize new rows with empty strings to avoid NaN propagation
        empty_rows = pd.DataFrame(
            [[""] * self.df.shape[1]] * rows_to_add,
            columns=self.df.columns,
        )

        # Concatenate and reset the index to preserve positional semantics
        self.df = pd.concat([self.df, empty_rows], ignore_index=True)

    def _find_label_positions(self) -> dict[str, tuple[int, int]]:
        """
        Locate the first occurrence of each normalized label in the DataFrame.

        If a normalized label appears multiple times, only the first
        occurrence (top-to-bottom, left-to-right) is recorded.

        Returns:
            dict[str, tuple[int, int]]: Mapping of normalized label to (row, col).
        """
        positions: dict[str, tuple[int, int]] = {}
        row_count, col_count = self.df.shape

        # Deterministic scan order ensures "first occurrence" is well-defined
        for row in range(row_count):
            for col in range(col_count):
                cell = self.get_cell_str_value(row, col)
                if not cell:
                    # Empty cells cannot act as metadata anchors
                    continue

                # setdefault preserves the earliest occurrence encountered
                positions.setdefault(self.normalize(cell), (row, col))

        return positions

    def read_metadata(
            self,
            label_offsets: dict[str, tuple[int, int]],
            *,
            strict: bool = True,
    ) -> dict[str, str]:
        """
        Read metadata values relative to labeled cells.

        Labels are resolved using normalized matching, and offsets are applied
        relative to the first occurrence of each label.

        Args:
            label_offsets (dict[str, tuple[int, int]]): Mapping of label to (row, col) offsets.
            strict (bool, optional): Whether to raise on missing labels or bounds errors. Defaults to True.

        Returns:
            dict[str, str]: Mapping of label to resolved metadata value.

        Raises:
            KeyError: If a label is not found and strict is True.
            IndexError: If an offset resolves outside bounds and strict is True.
        """
        # Build the label position map once to avoid repeated grid scans
        label_positions = self._find_label_positions()
        result: dict[str, str] = {}

        for label, (dr, dc) in label_offsets.items():
            pos = label_positions.get(self.normalize(label))
            if pos is None:
                # Missing labels are tolerated only in non-strict mode
                if strict:
                    raise KeyError(f"Metadata label not found: {label!r}")
                result[label] = ""
                continue

            label_row, label_col = pos
            value_row = label_row + dr
            value_col = label_col + dc

            # Explicit bounds checks prevent accidental wraparound behavior
            if (
                    value_row < 0
                    or value_col < 0
                    or value_row >= self.df.shape[0]
                    or value_col >= self.df.shape[1]
            ):
                if strict:
                    raise IndexError(
                        f"Metadata offset {(dr, dc)} out of bounds for label {label!r} "
                        f"at position {(label_row, label_col)}"
                    )
                result[label] = ""
                continue

            result[label] = self.get_cell_str_value(value_row, value_col)

        return result

    def write_metadata(
            self,
            label_offsets: dict[str, tuple[int, int]],
            label_values: dict[str, str],
            *,
            strict: bool = True,
    ) -> None:
        """
        Write metadata values relative to labeled cells.

        Rows may be extended to satisfy offsets, but columns are assumed to be
        fixed and must already exist.

        Args:
            label_offsets (dict[str, tuple[int, int]]): Mapping of label to (row, col) offsets.
            label_values (dict[str, str]): Mapping of label to value to write.
            strict (bool, optional): Whether to raise on missing labels, offsets, or bounds errors. Defaults to True.

        Raises:
            KeyError: If an offset or label is missing and strict is True.
            IndexError: If an offset resolves outside column bounds and strict is True.
        """
        # Resolve label positions once so all writes in this call are consistent
        label_positions = self._find_label_positions()

        for label, value in label_values.items():
            offset = label_offsets.get(label)
            if offset is None:
                # Offsets are mandatory because write targets cannot be inferred
                if strict:
                    raise KeyError(f"No offset provided for metadata label: {label!r}")
                continue

            pos = label_positions.get(self.normalize(label))
            if pos is None:
                if strict:
                    raise KeyError(f"Metadata label not found: {label!r}")
                continue

            dr, dc = offset
            label_row, label_col = pos
            target_row = label_row + dr
            target_col = label_col + dc

            # Column bounds are enforced strictly because extending columns
            # would violate the assumed template structure
            if target_row < 0 or target_col < 0 or target_col >= self.df.shape[1]:
                if strict:
                    raise IndexError(
                        f"Metadata offset {(dr, dc)} out of bounds for label {label!r} "
                        f"at position {(label_row, label_col)}"
                    )
                continue

            # Row extension is allowed and performed lazily
            self._ensure_row_exists(target_row)

            # Funnel writes through the shared setter to preserve invariants
            self.set_cell_value(target_row, target_col, value)
