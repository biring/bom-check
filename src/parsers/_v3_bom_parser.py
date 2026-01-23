"""
Parser for Version 3 Bill of Materials (BOM) Excel sheets.

This module identifies and parses Excel workbooks that follow the Version 3 BOM template.
It extracts board-level metadata and BOM tables from sheets that match expected structure and headers.

Main capabilities:
 - Detects whether an Excel workbook uses the v3 BOM format (`is_v3_bom`)
 - Extracts and parses board-level BOM data (`parse_v3_bom`)
 - Converts sheet content into structured `Board`, `Header`, and `Row` models
 - Handles malformed or non-matching sheets gracefully

Example Usage:
    # Usage via public package interface:
    Not allowed. This is an internal module. interfaces.py lists public package interfaces

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.parsers._v3_bom_parser import is_v3_bom, parse_v3_bom
    if is_v3_bom(sheets):
        bom = parse_v3_bom(sheets)

Dependencies:
 - Python >= 3.10
 - pandas
 - src.models.interfaces: BomV3, BoardV3, HeaderV3, RowV3
 - src.parsers._common: utility functions for flattening, extraction, and normalization

Notes:
 - Assumes a workbook may contain multiple sheets, only some of which are board BOMs.
 - Uses label-to-field mapping for robust extraction across inconsistent formatting.
 - Raises ValueError if no valid board sheets are parsed, to prevent silent failure.
 - Designed for incremental extension (e.g., summary sheet parsing).

License:
 - Internal Use Only
"""

import pandas as pd

import src.parsers._common as common

from src.adapters.interfaces import (
    map_template_v3_header_to_bom_v3_header,
    map_template_v3_table_to_bom_v3_row,
)

from src.models.interfaces import (
    BomV3,
    BoardV3,
    HeaderV3,
    RowV3,
)

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
    TEMPLATE_IDENTIFIERS_V3,
    TABLE_TITLE_ROW_IDENTIFIERS_V3,
)


def _is_cost_bom(boards: list[BoardV3]) -> bool:
    """
    Determine whether the parsed BOM represents a costed BOM.

    Classification rule:
    - If ANY board has both material_cost and total_cost blank or zero, the BOM is classified as NOT costed BOM.
    - Otherwise, the BOM is classified as costed BOM (fail-safe default).

    Args:
        boards (list[BoardV3]): Parsed board BOMs.

    Returns:
        bool: True if the BOM is classified as a costed BOM, otherwise False.
    """

    def _is_empty_or_zero(s: str) -> bool:
        s = (s or "").strip().replace(",", "")
        if s == "":
            return True
        try:
            return float(s) == 0.0
        except ValueError:
            return False  # not empty/zero; could be badly formatted number

    for board in boards:
        material_cost_raw = (board.header.material_cost or "").strip().replace(",", "")
        total_cost_raw = (board.header.total_cost or "").strip().replace(",", "")

        # Strong not a cost BOM signature: both cost fields are empty or zero
        if _is_empty_or_zero(material_cost_raw) and _is_empty_or_zero(total_cost_raw):
            return False

    # If we never saw the strong not a cost BOM signature, assume cost BOM
    return True


def _is_v3_board_sheet(sheet_name: str, sheet_data: pd.DataFrame) -> bool:
    """
    Checks whether a sheet contains required identifiers for a Version 3 board BOM.

    Evaluates whether the sheet includes all required board-level identifiers to qualify
    as a Version 3 BOM. This is used to selectively parse valid board sheets.

    Args:
        sheet_name (str): Name of the sheet (for logging/diagnostic purposes).
        sheet_data (pd.DataFrame): The DataFrame representing the Excel sheet.

    Returns:
        bool: True if all required identifiers are found, False otherwise.
    """
    # Check for all required identifiers in a single row to qualify as a Version 3 board BOM
    if common.has_all_identifiers_in_single_row(sheet_name, sheet_data, TABLE_TITLE_ROW_IDENTIFIERS_V3):
        # TODO: logger.info(f"✅ Sheet '{name}' is version 3 board BOM.")
        # when match found, exit
        return True
    else:
        # TODO: logger.debug(f"⚠️ Sheet '{name}' is not version 3 board BOM.")
        # If not ignore the sheet
        pass

    return False


def _parse_board_sheet(sheet_name: str, sheet_data: pd.DataFrame) -> BoardV3:
    """
    Parses a board BOM sheet into a structured Board object.

    Separates the sheet into header and component sections and converts both into
    structured dataclass instances.

    Args:
        sheet_name (str): Name of the Excel sheet being parsed.
        sheet_data (pd.DataFrame): The board BOM sheet to be parsed.

    Returns:
        BoardV3: A structured Board object containing parsed header and component rows.
    """
    # Extract board-level metadata block from the top of the sheet
    header_block = common.extract_header_block(sheet_data, TEMPLATE_IDENTIFIERS_V3)
    # Parse and assign header metadata
    header = _parse_board_header(header_block)

    # Extract the BOM component table from the lower part of the sheet
    table_block = common.extract_table_block(sheet_data, TABLE_TITLE_ROW_IDENTIFIERS_V3)
    # Parse and assign the BOM rows
    rows = _parse_board_table(table_block)

    # Create Board object
    board: BoardV3 = BoardV3(header=header, rows=rows, sheet_name=sheet_name)

    return board


def _parse_board_header(sheet_header: pd.DataFrame) -> HeaderV3:
    """
    Parses the board-level metadata block into a Header object.

    Flattens the input sheet block and maps known labels to the `Header` dataclass fields.

    Args:
        sheet_header (pd.DataFrame): Metadata section of the sheet.

    Returns:
        HeaderV3: A populated Header object with string values.
    """
    field_map = {}

    # Flatten the metadata block into a list of strings
    header_as_list = common.flatten_dataframe(sheet_header)

    for label in HeaderLabelsV3.values():
        value = common.extract_value_after_identifier(header_as_list, label)
        field_map[label] = value

    try:
        return map_template_v3_header_to_bom_v3_header(field_map)
    except Exception as e:
        raise ValueError(
            f"Header mapping issue during header parsing. Provided keys: {field_map.keys()}"
        ) from e


def _parse_board_table(sheet_table: pd.DataFrame) -> tuple[RowV3, ...]:
    """
    Parses the component table into a tuple of Row instances.

    Iterates through each row and converts it to a structured Row object.

    Args:
        sheet_table (pd.DataFrame): The component table section of the BOM.

    Returns:
        tuple[RowV3, ...]: Parsed BOM component rows.
    """
    rows: list[RowV3] = []

    for _, row in sheet_table.iterrows():
        # Convert each row of the table into an Row object
        row = _parse_board_table_row(row)
        # Append parsed row to the result list
        rows.append(row)

    return tuple(rows)


def _parse_board_table_row(row: pd.Series) -> RowV3:
    """
    Parses a single component row into a Row instance.

    Uses fuzzy label matching to extract values and maps them to the Row dataclass fields.

    Args:
        row (pd.Series): One row of the BOM table.

    Returns:
        RowV3: The parsed BOM component with mapped field values.
    """
    field_map = {}

    for label in TableLabelsV3.values():
        value = common.extract_cell_value_by_fuzzy_header(row, label)
        field_map[label] = value

    try:
        return map_template_v3_table_to_bom_v3_row(field_map)
    except Exception as e:
        raise ValueError(
            f"Row mapping issue during row parsing. Provided keys: {field_map.keys()}"
        ) from e


def is_v3_bom(sheets: dict[str, pd.DataFrame]) -> bool:
    """
    Check whether any sheet in the workbook appears to use the Version 3 BOM template.

    A workbook is treated as v3 if at least one sheet contains all required v3 template
    identifiers in a single row.

    Args:
        sheets (dict[str, pd.DataFrame]): Workbook sheets keyed by sheet name.

    Returns:
        bool: True if any sheet matches the v3 template identifiers, otherwise False.
    """
    # Iterate through all sheets and check for required identifiers
    for sheet_name, sheet_data in sheets.items():
        # If it contains the labels that identify it as version 3 template
        if common.has_all_identifiers_in_single_row(sheet_name, sheet_data, TABLE_TITLE_ROW_IDENTIFIERS_V3):
            # TODO: logger.info(f"✅ Sheet '{name}' is using version 3 BOM template.")
            # TODO: logger.info(f"✅ BOM is using version 3 template.")
            # Return True on first match
            return True
        else:
            # TODO: logger.debug(f"⚠️ Sheet '{name}' is not using version 3 BOM Template.")
            # Skip non-matching sheets
            pass

    # TODO: logger.debug(f"⚠️ BOM is not using version 3 template.")
    return False


def parse_v3_bom(file_name: str, sheets: dict[str, pd.DataFrame]) -> BomV3:
    """
    Parses Version 3 BOM sheets into a structured Bom object.

    Iterates through all sheets, identifies valid board BOMs, and converts them into
    structured Board instances. Raises an exception if none are valid.

    Args:
        file_name (str): The name of the file to parse.
        sheets (dict[str, pd.DataFrame]): Workbook sheets keyed by sheet name.

    Returns:
        BomV3: Parsed BOM with one or more structured boards.

    Raises:
        ValueError: If no valid board sheets are found.
    """

    boards: list[BoardV3] = []

    # Loop through each sheet
    for sheet_name, sheet_data in sheets.items():
        # Check if sheet is a valid board BOM
        if _is_v3_board_sheet(sheet_name, sheet_data):
            # Parse and append valid boards to the BOM
            boards.append(_parse_board_sheet(sheet_name, sheet_data))
            # TODO: logger.info(f"✅ Sheet '{name}' was parsed..")
        else:
            # TODO: logger.debug(f"⚠️ Sheet '{name}' was not parsed.")
            # If not ignore the sheet
            pass

    bom = BomV3(
        file_name=file_name,
        is_cost_bom=_is_cost_bom(boards),
        boards=tuple(boards)
    )

    # Raise an error if the BOM remains empty after parsing
    if not bom.boards:
        raise ValueError("Parsed version 3 bom is empty.")

    return bom
