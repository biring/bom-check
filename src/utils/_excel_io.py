"""
Utilities for reading and writing Excel workbooks with consistent string typing and safe worksheet naming.

This module supports:
 - Loading all worksheets from a `.xlsx` file into string-typed pandas DataFrames
 - Writing a DataFrame to an Excel file without an index
 - Writing multiple DataFrames into a single workbook with sanitized sheet names
 - Enforcing Excel naming constraints (invalid characters removed, max length 31)

Example Usage:
    # Preferred usage via public package interface:
    from src.utils import excel_io
    sheets = excel_io.read_excel_file("input.xlsx")

    # Direct module usage (acceptable in unit tests or internal scripts):
    import src.utils._excel_io as excel_io
    excel_io.write_frame_to_excel("out.xlsx", df)

Dependencies:
 - Python >= 3.9
 - Standard Library: re
 - External Packages: pandas (>= 2.x), openpyxl

Notes:
 - All cells are coerced to strings; blanks are preserved as "".
 - Sheet reading is isolated per-worksheet for clearer debugging and error context.
 - Sheet names are sanitized to satisfy Excel constraints before writing.
 - Empty DataFrames are not written; writing an empty sheet raises ValueError.
 - Designed for use across BOM parsing, export utilities, and intermediate report generation.
 - Workbooks are opened via context managers to ensure file handles close cleanly on Windows.

License:
 - Internal Use Only
"""

__all__ = [
    "EXCEL_FILE_TYPE",
    "map_excel_sheets_to_string_dataframes",
    "read_excel_file",
    "sanitize_sheet_name_for_excel",
    "write_sheets_to_excel",
    "write_frame_to_excel",
]

import re

import pandas as pd

# CONSTANTS
EXCEL_FILE_TYPE = ".xlsx"

# REGULAR EXPRESSIONS
EXCEL_NAME_CONSTRAINTS = re.compile(r'[:\\/?*\[\]]')


def map_excel_sheets_to_string_dataframes(
        workbook: pd.ExcelFile,
        top_row_is_header: bool = True,
) -> dict[str, pd.DataFrame]:
    """
    Maps an open pandas ExcelFile into a dict of DataFrames with all values preserved as strings.

    Each worksheet is read independently so failures are isolated and clearly attributed to the offending sheet. Blank cells are retained as empty strings (not NaN). This function does not open or close the workbook; the caller owns the lifetime of `excel_file`.

    Args:
        workbook (pd.ExcelFile): An already-open pandas ExcelFile instance (e.g., via `pd.ExcelFile(path, engine="openpyxl")`). Must remain valid for the duration of the call.
        top_row_is_header (bool): If True, the top row is treated as column headers. If False, the top row is treated as data.

    Returns:
        dict[str, pd.DataFrame]: Mapping of sheet name to DataFrame, with every column typed as `str` and blanks represented as "".

    Raises:
        RuntimeError: If a specific sheet fails to load. The error message includes the sheet name and the workbook source (path or stream description) when available.
    """
    # Accumulate DataFrames keyed by sheet name; all cells will be string-typed
    sheet_frames: dict[str, pd.DataFrame] = {}

    # Read worksheets independently so a single bad sheet doesn't mask others
    for sheet_name in workbook.sheet_names:
        try:
            # Force string dtype and suppress NaN creation so blanks remain ""
            df = pd.read_excel(
                workbook,
                sheet_name=sheet_name,
                header=0 if top_row_is_header else None,
                dtype=str,  # Force all cells to be strings
                na_filter=False  # Keep blanks as empty strings instead of NaN
            )
            # Store the successfully read sheet
            sheet_frames[sheet_name] = df
        except Exception as exc:
            # Wrap with context (sheet + source) to make test failures and logs actionable
            raise RuntimeError(
                f"Failed to read sheet '{sheet_name}' from Excel file."
                f"\n{exc}"
            ) from exc

    return sheet_frames


def read_excel_file(
        file_path: str,
        top_row_is_header: bool = True,
) -> dict[str, pd.DataFrame]:
    """
    Open an Excel `.xlsx` file, read every worksheet into string-typed DataFrames, then close it.

    The workbook is opened with the `openpyxl` engine and disposed via a context manager. All cells are loaded as strings and blank cells remain empty strings (not NaN). This function delegates sheet parsing to `map_excel_sheets_to_string_dataframes` and ensures the file handle is always closed.

    Args:
        file_path (str): Path to the `.xlsx` workbook to load.
        top_row_is_header (bool): If True, the top row is treated as column headers. If False, the top row is treated as data.

    Returns:
        dict[str, pd.DataFrame]: Mapping of sheet name -> DataFrame, with all columns typed as `str`.

    Raises:
        RuntimeError: If the workbook cannot be opened or any sheet fails to load; the message includes the file path and the original error type and message.
    """

    try:
        # Open and auto-close the workbook; ensures no lingering file locks on Windows
        with pd.ExcelFile(file_path, engine="openpyxl") as excel_file:
            # Delegate per-sheet parsing; enforces str dtype and keeps blanks as ""
            return map_excel_sheets_to_string_dataframes(
                excel_file,
                top_row_is_header=top_row_is_header,
            )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to read Excel file at '{file_path}'."
            f"\n{exc}"
        ) from exc


def sanitize_sheet_name_for_excel(name: str) -> str:
    """
    Return a sanitized Excel worksheet name that meets Excel naming constraints.

    Excel enforces the following restrictions:
        - Maximum length: 31 characters
        - Disallowed characters: ':' '\' '/' '?' '*' '[' ']'

    This function converts the input to a string (if not already), removes any
    invalid characters, and truncates the result to the maximum allowed length.

    Args:
        name (str): Proposed worksheet name to sanitize.

    Returns:
        str: A safe, Excel-compliant sheet name.
    """
    # Convert non-string input to string for consistent processing
    sheet_name = str(name)
    # Remove characters Excel does not permit in sheet names
    sheet_name = EXCEL_NAME_CONSTRAINTS.sub("", sheet_name)
    # Truncate to Excel 31-character maximum length
    sheet_name = sheet_name[:31]
    return sheet_name


def write_frame_to_excel(
        file_path: str,
        dataframe: pd.DataFrame,
        add_header_to_top_row: bool = True,
) -> None:
    """
    Write a pandas DataFrame to an Excel `.xlsx` file using the openpyxl engine.

    The DataFrame index is not written. All exceptions are caught and wrapped with a `RuntimeError` that includes the file path and original exception details.

    Args:
        file_path (str): Destination path for the Excel file. Should end with `.xlsx`.
        dataframe (pd.DataFrame): The DataFrame to be written.
        add_header_to_top_row (bool): If True, write column names as the first row. If False, column names are not written to the first row.

    Returns:
        None

    Raises:
        RuntimeError: If any error occurs during the write process. The message includes the target file path, the original exception type, and the original message.
    """
    try:
        # Write DataFrame to Excel file using openpyxl; omit the index column
        dataframe.to_excel(
            file_path,
            index=False,
            header=add_header_to_top_row,
            engine="openpyxl"
        )
    except Exception as exc:
        # Wrap any exception with context about the file being written
        raise RuntimeError(
            f"Failed to write Excel file to '{file_path}'. "
            f"\n{exc}"
        ) from exc


def write_sheets_to_excel(
        file_path: str,
        frames_by_sheet: dict[str, pd.DataFrame],
        overwrite: bool = False,
        add_header_to_top_row: bool = True,
) -> None:
    """
    Write multiple pandas DataFrames to a single Excel `.xlsx` file, one worksheet per mapping entry.

    All provided DataFrames must contain at least one row and one column; if any DataFrame is empty, the operation is aborted with a `ValueError`. Sheet names are sanitized using `sanitize_sheet_name_for_excel` before writing. The workbook is written with the `openpyxl` engine via a context manager to avoid lingering file locks (especially on Windows).

    Args:
        file_path (str): Destination path for the workbook. Must end with `.xlsx`.
        frames_by_sheet (dict[str, pd.DataFrame]): Mapping of requested sheet name to DataFrame.
        overwrite (bool, optional): If True, overwrite an existing file; otherwise, fail when the target file already exists. Defaults to False.
        add_header_to_top_row: If True, write column names as the first row. If False, column names are not written to the first row.

    Returns:
        None: Writes an Excel file to `file_path` and does not return a value.

    Raises:
        ValueError: If `frames_by_sheet` is empty, or if any DataFrame is empty.
        RuntimeError: If an unexpected error occurs while opening or writing the workbook; the original exception type and message are included for context.
    """
    # Validate each DataFrames is non-empty (has at least one row and one column)
    for name, df in frames_by_sheet.items():
        if df.empty or df.shape[1] == 0:
            raise ValueError(
                "One or more provided sheet data is empty. All sheets must contain data.")

    if not frames_by_sheet:
        raise ValueError("No sheet data provided to write to Excel file.")

    # Decide file open mode based on overwrite flag
    mode = "w" if overwrite else "x"

    try:
        # Use a context manager to ensure the writer is closed and the file handle released
        with pd.ExcelWriter(file_path, engine="openpyxl", mode=mode) as writer:
            for sheet, frame in frames_by_sheet.items():
                # Sanitize sheet names to comply with Excel naming rules
                if sheet:
                    # Let pandas assign default name if given sheet_name is incompatible
                    safe_sheet = sanitize_sheet_name_for_excel(sheet)
                    frame.to_excel(writer, sheet_name=safe_sheet, index=False, header=add_header_to_top_row)
                else:
                    frame.to_excel(writer, index=False, header=add_header_to_top_row)
    except Exception as err:
        # Wrap and re-raise unexpected exceptions with path and original error details
        raise RuntimeError(
            f"Failed to write Excel workbook '{file_path}' using mode '{mode}'."
            f"\n{err}"
        ) from err
