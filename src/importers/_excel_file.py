"""
Helpers for loading Excel workbooks and project Excel templates into pandas DataFrames.

This module provides importer-layer utilities to:
 - Read an Excel workbook into a dict of {sheet_name: DataFrame} with shared path validation
 - Resolve and load the Version 3 BOM export template from src/resources/templates into a single DataFrame

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.importers import _excel_reader as _excel_reader
    sheets = _excel_reader.read_excel_as_dict("data/sample_workbook.xlsx")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: pandas
    - Internal Modules: src.utils.folder_path, src.utils.file_path, src.utils.excel_io

Notes:
    - This module is intended for internal use within the importers layer, sitting between controllers and src.utils.excel_io.
    - Callers should treat this module as a thin, side-effect-free wrapper that normalizes the path, enforces the Excel file type, and delegates reading to excel_io.
    - All low-level I/O and engine selection remain owned by src.utils.excel_io; this module focuses on path handling and consistent error messages.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star imports from this module export nothing.

import pandas as pd

from src.utils import (
    folder_path,
    file_path,
    excel_io,
)

# Module Constants
EXCEL_FILE_TYPES = (excel_io.EXCEL_FILE_TYPE,)
TEMPLATE_FOLDER_PARTS = ("src", "resources", "templates")
TEMPLATE_NAME = "BomTemplateV3"


def read_excel_as_dict(folder: str, file_name: str, *, top_row_is_header: bool = True) -> dict[str, pd.DataFrame]:
    """
    Read an Excel workbook from disk and return all sheets as a dict of DataFrames.

    This helper normalizes and validates the input path, enforces the expected Excel file extension, and delegates reading to the shared excel_io utilities. All failures are wrapped in a RuntimeError with a consistent message.

    Args:
        folder (str): Path to the folder containing the Excel workbook.
        file_name (str): Name of the Excel workbook.
        top_row_is_header (bool): If True, the top row is treated as column headers. If False, the top row is treated as data.

    Returns:
        dict[str, pd.DataFrame]: Mapping of sheet name to loaded DataFrame.

    Raises:
        RuntimeError: If the path is invalid, the file is not an Excel workbook, or reading the workbook fails for any reason.
    """
    try:
        excel_path = file_path.construct_file_path(folder, file_name)

        # Normalize the given path into a Path object
        normalized_path = file_path.normalize_file_path(excel_path)

        # Enforce the expected Excel file extension (e.g., ".xlsx")
        file_path.assert_file_name(normalized_path, EXCEL_FILE_TYPES)

        # Ensure the path refers to an existing regular file
        file_path.assert_file_path(normalized_path)

        # Delegate the actual read to the shared excel_io helper
        return excel_io.read_excel_file(normalized_path, top_row_is_header=top_row_is_header)

    except (TypeError, ValueError, RuntimeError) as e:
        raise RuntimeError(
            f"Failed to read Excel workbook '{file_name}' from '{folder}'.\n{e}"
        ) from e

    except Exception as e:
        raise RuntimeError(
            f"Unexpected error while reading Excel workbook '{file_name}' from '{folder}'.\n{e}"
        ) from e


def load_version3_bom_template() -> pd.DataFrame:
    """
    Load the Version 3 BOM export template as a DataFrame.

    The template is resolved from the project resources folder and is
    expected to contain exactly one worksheet.

    Returns:
        pd.DataFrame: Template DataFrame.

    Raises:
        RuntimeError: If the template cannot be loaded or is empty.
    """
    try:
        # Resolve project root in development mode
        project_root_path = folder_path.resolve_project_folder()

        # Construct full template path
        template_file_name = TEMPLATE_NAME + excel_io.EXCEL_FILE_TYPE
        template_folder_path = folder_path.construct_folder_path(project_root_path, TEMPLATE_FOLDER_PARTS)

        # Load workbook (expected to contain exactly one sheet)
        template_dict = read_excel_as_dict(template_folder_path, template_file_name, top_row_is_header=False)

        if len(template_dict) != 1:
            raise RuntimeError(
                f"Expected exactly one worksheet in template '{template_file_name}', found {len(template_dict)}."
            )

        # Extract the single template sheet
        _, template_data_frame = next(iter(template_dict.items()))

        if template_data_frame.empty:
            raise RuntimeError(
                f"Empty version 3 bom template '{template_file_name}'."
            )

        return template_data_frame


    except (FileNotFoundError, TypeError, ValueError, RuntimeError) as err:
        raise RuntimeError(
            f"Failed to load version 3 bom template from project resource folder. \n{err}"
        ) from err

    except Exception as exc:
        raise RuntimeError(
            f"Unexpected error while loading version 3 bom template from project resource folder. \n{exc}"
        ) from exc
