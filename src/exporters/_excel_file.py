"""
Internal helpers for writing Excel workbooks to disk.

This module provides exporter-side orchestration for writing one or more tabular datasets to an Excel file with consistent validation and error handling. It centralizes folder and file path validation, enforces Excel file naming conventions, validates sheet data integrity, and delegates actual I/O operations to shared utilities. The module is designed to sit between higher-level exporters and low-level filesystem and Excel I/O helpers.

Key responsibilities
	- Validate destination folder paths before performing any write operations
	- Validate Excel file names and enforce the expected Excel file extension
	- Validate mappings of worksheet names to non-empty tabular data
	- Prevent accidental overwrites unless explicitly allowed
	- Delegate Excel workbook creation to shared Excel I/O utilities while adding contextual error messages

Example usage
	# Preferred usage via public package interface
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from src.exporters import _excel_file as ef
	ef.write_excel_sheets("C:/Projects/BomCheck", "bom_export_2026_01_25", sheets=sheets)

Dependencies
	- Python 3.x
	- Standard Library: typing

Notes
	- This module is internal to the exporters layer and is not part of a public API.
	- All low-level Excel engine handling and file writing logic is delegated to shared utilities.
	- Callers are expected to provide validated, non-empty tabular data structures per worksheet.

License
	- Internal Use Only
"""

__all__ = []  # Internal-only; not exported publicly.

from typing import Dict

import pandas as pd

from src.utils import excel_io
from src.utils import file_path
from src.utils import folder_path


def write_excel_sheets(
        folder: str,
        file_name: str,
        sheets: Dict[str, pd.DataFrame],
        *,
        overwrite: bool = False,
        top_row_is_header: bool = False,
) -> None:
    """
    Write multiple pandas DataFrames to an Excel workbook with validation and contextual errors.

    This function validates the provided mapping of sheet names to DataFrames, validates
    the destination folder, constructs a normalized `.xlsx` file path, prevents accidental
    overwrites when configured, and delegates the actual write to the shared excel I/O utility.

    Args:
        folder (str): Absolute path to the destination folder.
        file_name (str): File name without extension.
        sheets (Dict[str, pd.DataFrame]): Mapping of sheet name -> DataFrame to write.
        overwrite (bool): If True, allow overwriting an existing file. Defaults to False.
        top_row_is_header (bool): If True, column names are written as the top row. Defaults to False.

    Returns:
        None: Writes an Excel file to disk and returns nothing.

    Raises:
        RuntimeError: On validation failures or if the underlying IO fails. The raised message
            includes the file name and folder for diagnosability.
    """
    try:
        # Validate mapping keys (sheet names) exist and are non-empty strings.
        # This prevents silent creation of unnamed worksheets that complicate downstream consumers.
        if not isinstance(sheets, dict):
            raise TypeError(
                f"Expected type for sheets must be a dict[str, pandas.DataFrame]; got {type(sheets).__name__}.")

        for sheet_name in sheets.keys():
            if not sheet_name or not isinstance(sheet_name, str):
                # Fail fast if any sheet name is missing or not a string so the caller can fix the source data.
                raise ValueError(
                    f"Invalid sheet name '{repr(sheet_name)}'. Sheet names must be non-empty strings. Found names: {tuple(sheets.keys())}.")

        # Validate DataFrame values are non-empty.
        # Excel writer utilities in other modules expect sheets to contain at least one row and one column.
        for sheet_name, sheet_frame in sheets.items():
            # Dense comment: enforce type contract and non-empty constraint before touching disk.
            if not isinstance(sheet_frame, pd.DataFrame):
                raise TypeError(
                    f"Sheet '{sheet_name}' value must be a pandas.DataFrame; got {type(sheet_frame).__name__}.")

            if sheet_frame.empty or sheet_frame.shape[1] == 0:
                # Surface which sheet is invalid to make debugging immediate.
                raise ValueError(
                    f"Sheet '{sheet_name}' is empty (shape='{sheet_frame.shape}'). Provide a non-empty DataFrame or omit this sheet.")

        # Ensure target folder exists and is a directory. This centralizes folder validation policy.
        folder_path.assert_folder_path(folder)

        # Build and validate final file path with enforced Excel extension.
        file_path_excel = file_path.construct_file_path(folder, file_name + excel_io.EXCEL_FILE_TYPE)

        # Validate the computed file name ends with the allowed Excel extension.
        file_path.assert_file_name(file_path_excel, (excel_io.EXCEL_FILE_TYPE,))

        # Prevent accidental overwrites unless caller explicitly allows it.
        if not overwrite and file_path.is_file_path(file_path_excel):
            raise ValueError(f"File exists '{file_path_excel}'. Overwrite not allowed.")

        # Delegate writing to the shared, tested utility that handles sheet sanitization and openpyxl context.
        excel_io.write_sheets_to_excel(
            file_path=file_path_excel,
            frames_by_sheet=sheets,
            overwrite=overwrite,
            add_header_to_top_row=top_row_is_header,
        )

        return

    except (TypeError, ValueError, RuntimeError) as exc:
        # Wrap expected validation errors with context about destination for clearer logs/traces.
        raise RuntimeError(
            f"Failed to write excel file '{file_name}' to folder '{folder}'.\n{exc}"
        ) from exc

    except Exception as exc:
        # Catch-all to ensure callers always receive RuntimeError with context rather than raw library exceptions.
        raise RuntimeError(
            f"Unexpected error during excel file '{file_name}' write to '{folder}'.\n{exc}"
        ) from exc
