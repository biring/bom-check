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
    app_mode,
    folder_path,
    file_path,
    excel_io,
)

# Module Constants
EXCEL_FILE_TYPES = (excel_io.EXCEL_FILE_TYPE,)
TEMPLATE_FOLDER_PARTS = ("src", "resources", "templates")
_TEMPLATE_FOLDER_PARTS_EXE = ("resources", "templates")
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

    Resolves the template resource folder according to the current application mode, loads the configured template workbook without treating the top row as headers, requires the workbook to contain exactly one worksheet, and rejects an empty template DataFrame.

    Returns:
        pd.DataFrame: Template DataFrame.

    Raises:
        RuntimeError: If the template cannot be loaded or is empty.
    """
    try:
        # Select the resource root according to runtime mode so development, unit test, and executable layouts remain isolated.
        if app_mode.APP_MODE == app_mode.APP_MODE.DEVELOPMENT or app_mode.APP_MODE == app_mode.APP_MODE.UNITTEST:
            # Development and unit test modes resolve resources from the project source tree.
            project_root_path = folder_path.resolve_project_folder()
            sub_folder_list = TEMPLATE_FOLDER_PARTS
        elif app_mode.APP_MODE == app_mode.APP_MODE.EXECUTABLE:
            # Executable mode resolves resources from the packaged application folder layout.
            project_root_path = folder_path.resolve_exe_folder()
            sub_folder_list = _TEMPLATE_FOLDER_PARTS_EXE
        else:
            # Fail fast for unsupported modes so template loading cannot proceed with an undefined folder layout.
            raise RuntimeError(f"Application mode {app_mode.APP_MODE} not supported")

        # Compose the expected workbook file name from the configured template stem and shared Excel file extension.
        template_file_name = TEMPLATE_NAME + excel_io.EXCEL_FILE_TYPE

        # Construct the folder path after mode resolution so the selected resource layout controls where the template is loaded from.
        template_folder_path = folder_path.construct_folder_path(project_root_path, sub_folder_list)

        # Load the template workbook as data rows rather than header-based columns because the template structure is preserved verbatim.
        template_dict = read_excel_as_dict(template_folder_path, template_file_name, top_row_is_header=False)

        # Enforce the template invariant that the Version 3 BOM template workbook owns exactly one worksheet.
        if len(template_dict) != 1:
            raise RuntimeError(
                f"Expected exactly one worksheet in template '{template_file_name}', found {len(template_dict)}."
            )

        # Extract the only worksheet after the one-sheet invariant has been enforced.
        _, template_data_frame = next(iter(template_dict.items()))

        # Reject empty templates because callers require actual template content to export or compare against.
        if template_data_frame.empty:
            raise RuntimeError(
                f"Empty version 3 bom template '{template_file_name}'."
            )

        # Return the validated single-sheet template DataFrame.
        return template_data_frame

    except (FileNotFoundError, TypeError, ValueError, RuntimeError) as err:
        # Wrap expected path, validation, mode, and template-shape failures with consistent resource-loading context.
        raise RuntimeError(
            f"Failed to load version 3 bom template from project resource folder. \n{err}"
        ) from err

    except Exception as exc:
        # Wrap all other failures separately so unexpected conditions remain distinguishable to callers and logs.
        raise RuntimeError(
            f"Unexpected error while loading version 3 bom template from project resource folder. \n{exc}"
        ) from exc
