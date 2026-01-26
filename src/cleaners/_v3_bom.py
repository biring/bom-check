"""
Cleaner for Version 3 Bill of Materials (BOM) Excel sheets.

This module orchestrates field-level coercion across the BOM hierarchy (boards, headers, and rows). It rebuilds the BOM with normalized values and accumulates a contextual change log (file → sheet → section) for traceable audit output.

Example Usage:
    # Preferred usage via package interface:
    from src.cleaners import interfaces as clean
    clean_bom, log = clean.bom(raw_bom)

    # Direct internal usage (unit tests or internal scripts only):
    from src.cleaners import _v3_bom as _v3
    result_bom, result_log = _v3.clean_v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses
    - Internal Packages: src.models, src.coerce, src.cleaners._types

Notes:
    - Designed for structured Version 3 BOMs only; assumes valid model hierarchy.
    - `ChangeLog` records all coercion steps with contextual grouping.
    - Intended for internal use; external callers should use `src.cleaners.interfaces`.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.common import ChangeLog

from src.coerce import interfaces as coerce

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
)


def clean_v3_bom(bom: BomV3) -> tuple[BomV3, tuple[str, ...]]:
    """
    Clean a Version 3 BOM by coercing all board headers and rows and collecting a change log.

    Traverses each board in the BOM, normalizes row fields and header fields using the `src.coerce.interfaces` functions, and rebuilds the BOM with coerced values. A contextual change log (file → sheet → section) is returned for auditability.

    Args:
        bom (BomV3): Input BOM containing boards, headers, and rows to be coerced.

    Returns:
        tuple[BomV3, tuple[str, ...]]: A 2-tuple of (coerced_bom, change_log_messages).

    Raises:
        ValueError: If reconstruction of any board, header, or row fails due to an invalid field mapping.
    """
    # Initialize contextual log (file, sheet, section tracking)
    change_log = ChangeLog()
    change_log.set_module_name("Cleaner")
    change_log.set_file_name(bom.file_name)

    clean_boards: list[BoardV3] = []

    # Iterate through each board in the BOM
    for board in bom.boards:
        # Set sheet context for current board
        change_log.set_sheet_name(board.sheet_name)

        # Coerce all rows within current board
        clean_rows: list[RowV3] = []
        for idx, raw_row in enumerate(board.rows, start=1):
            change_log.set_section_name(RowV3.__name__ + ": " + str(idx))
            clean_row = _clean_row(change_log, raw_row)
            clean_rows.append(clean_row)

        # Coerce header fields for the current board
        change_log.set_section_name(HeaderV3.__name__)
        clean_header = _clean_header(change_log, board.header)

        ## Reconstruct the Board object with coerced fields
        clean_board: BoardV3 = BoardV3(header=clean_header, rows=tuple(clean_rows), sheet_name=board.sheet_name)
        clean_boards.append(clean_board)

    # Collect all cleaned boards and reconstruct final BOM
    clean_bom: BomV3 = BomV3(boards=tuple(clean_boards), file_name=bom.file_name, is_cost_bom=bom.is_cost_bom)

    # Extract full log snapshot for external reporting
    frozen_change_log = change_log.render()

    return clean_bom, frozen_change_log


def _clean_header(change_log: ChangeLog, header: HeaderV3) -> HeaderV3:
    """
    Coerce and normalize all row fields and append emitted messages to the shared log.

    Applies field-specific coercers in a defined order, maps label-based fields to dataclass attributes, and rebuilds a normalized `RowV3`.

    Args:
        change_log (ChangeLog): Shared context-aware change log collector.
        header (HeaderV3): Raw header instance.

    Returns:
        HeaderV3: New header with normalized values.

    Raises:
        ValueError: If any coerced values cannot be mapped back to `RowV3` fields during reconstruction.
    """
    field_map = {}

    # Define ordered header cleaning sequence (function, value, attribute)
    cases = [
        (coerce.model_number, header.model_no, HeaderLabelsV3.MODEL_NO),
        (coerce.board_name, header.board_name, HeaderLabelsV3.BOARD_NAME),
        (coerce.board_supplier, header.board_supplier, HeaderLabelsV3.BOARD_SUPPLIER),
        (coerce.build_stage, header.build_stage, HeaderLabelsV3.BUILD_STAGE),
        (coerce.bom_date, header.bom_date, HeaderLabelsV3.BOM_DATE),
        (coerce.material_cost, header.material_cost, HeaderLabelsV3.MATERIAL_COST),
        (coerce.overhead_cost, header.overhead_cost, HeaderLabelsV3.OVERHEAD_COST),
        (coerce.total_cost, header.total_cost, HeaderLabelsV3.TOTAL_COST),
    ]

    # Apply coercion for each field and collect logs
    for fn, val, label in cases:
        result_value, result_logs = fn(val)
        field_map[label] = result_value

        # Record each formatted message in the shared coercion log
        for result_log in result_logs:
            change_log.add_entry(result_log)

    # Rebuild header object with coerced values
    try:
        return map_template_v3_header_to_bom_v3_header(field_map)
    except Exception as e:
        # Raise detailed error if any field mapping fails
        raise ValueError(
            f"Header coercion failed: invalid field mapping. Keys processed: {field_map.keys()}."
        ) from e


def _clean_row(change_log: ChangeLog, row: RowV3) -> RowV3:
    """
    Clean (coerce and normalize) all row-level fields.

    Invokes field-specific coercers for each BOM row attribute and logs any transformations that result in a changed value.

    Args:
        change_log (help.CleanLog): Shared log collector for contextual tracking.
        row (RowV3): Input row object with raw field values.

    Returns:
        RowV3: New row instance with normalized field values.

    Raises:
        ValueError: If field mapping fails during row reconstruction.
    """

    field_map = {}

    # Define ordered row coercion sequence (function, value, attribute)
    cases = [
        (coerce.item, row.item, TableLabelsV3.ITEM),
        (coerce.component_type, row.component_type, TableLabelsV3.COMPONENT_TYPE),
        (coerce.device_package, row.device_package, TableLabelsV3.DEVICE_PACKAGE),
        (coerce.description, row.description, TableLabelsV3.DESCRIPTION),
        (coerce.units, row.units, TableLabelsV3.UNITS),
        (coerce.classification, row.classification, TableLabelsV3.CLASSIFICATION),
        (coerce.manufacturer, row.mfg_name, TableLabelsV3.MFG_NAME),
        (coerce.mfg_part_number, row.mfg_part_number, TableLabelsV3.MFG_PART_NO),
        (coerce.ul_vde_number, row.ul_vde_number, TableLabelsV3.UL_VDE_NO),
        (coerce.validated_at, row.validated_at, TableLabelsV3.VALIDATED_AT),
        (coerce.quantity, row.qty, TableLabelsV3.QUANTITY),
        (coerce.designator, row.designators, TableLabelsV3.DESIGNATORS),
        (coerce.unit_price, row.unit_price, TableLabelsV3.UNIT_PRICE),
        (coerce.sub_total, row.sub_total, TableLabelsV3.SUB_TOTAL),
    ]

    # Apply coercion for each field and collect logs
    for fn, val, label in cases:
        result_value, result_logs = fn(val)
        field_map[label] = result_value

        # Append each formatted message to the shared coercion log
        for result_log in result_logs:
            change_log.add_entry(result_log)

    # Rebuild the row object with coerced values
    try:
        return map_template_v3_table_to_bom_v3_row(field_map)
    except Exception as e:
        raise ValueError(
            # Raise detailed error if mapping fails
            f"Row coercion failed: invalid field mapping. Keys processed: {field_map.keys()}."
        ) from e
