"""
Fixer for Version 3 Bill of Materials (BOM) Excel sheets.

This module applies both manual and automatic field corrections across the BOM hierarchy — boards, headers, and rows — using rule functions from `src.correction.interfaces`. It rebuilds the BOM with corrected dataclass instances and aggregates contextual change logs (file → sheet → section) for audit traceability.

Example Usage:
    # Preferred usage via package interface:
    from src.fixer import interfaces as fix
    fixed_bom, log = fix.bom(raw_bom)

    # Direct internal usage (unit tests or internal scripts only):
    from src.fixer import _v3_bom as v3
    fixed_bom, log = v3.fix_v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses
    - Internal Packages: src.models, src.correction, src.fixer._types

Notes:
    - Designed exclusively for structured Version 3 BOMs with valid model hierarchy.
    - ChangeLog accumulates human-readable audit messages, grouped by contextual scope.
    - Manual fixers rely on user-provided corrections; auto fixers apply deterministic rules.
    - External callers should invoke through `src.fixer.interfaces` to preserve API boundaries.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from dataclasses import replace

from src.models.interfaces import (
    BomV3,
    BoardV3,
    HeaderV3,
    HeaderV3AttrNames,
    RowV3,
    RowV3AttrNames,
)

from src.correction import interfaces as correct

from src.common import ChangeLog


def fix_v3_bom(bom: BomV3) -> tuple[BomV3, tuple[str, ...]]:
    """
    Apply manual and automatic field corrections across all boards, headers, and rows in a Version 3 BOM.

    Traverses every `Board` in the provided `Bom`, invokes field-level fixers for each `Row` and `Header`, and rebuilds corrected dataclass instances. Collects a contextual `ChangeLog` keyed by file, sheet, and section for full audit traceability.

    Args:
        bom (BomV3): Input BOM object containing nested boards, headers, and rows to fix.

    Returns:
        tuple[BomV3, tuple[str, ...]]: A tuple containing the corrected BOM and a tuple of formatted log entries (one per detected or applied change).

    Raises:
        ValueError: If reconstruction of any row, header, or board fails due to invalid mappings.
    """
    # Initialize contextual change log scoped by file → sheet → section
    change_log = ChangeLog()
    change_log.set_module_name("fixer")
    change_log.set_file_name(bom.file_name)

    fixed_boards: list[BoardV3] = []

    # --- For each board in the BOM ---
    for board in bom.boards:
        # Set current sheet context for accurate log grouping
        change_log.set_sheet_name(board.sheet_name)

        # --- Fix rows ---
        fixed_rows: list[RowV3] = []
        for idx, raw_row in enumerate(board.rows, start=1):
            change_log.set_section_name(RowV3.__name__ + ": " + str(idx))

            # Apply manual fixers first (user-dependent), then automatic fixers
            fixed_row_manual = _fix_row_manual(change_log, raw_row)
            fixed_row_auto = _fix_row_auto(change_log, fixed_row_manual)
            fixed_rows.append(fixed_row_auto)

        # --- Fix header ---
        change_log.set_section_name(HeaderV3.__name__)

        # Apply manual header fixes before auto-calculated fields like cost
        fixed_header_manual = _fix_header_manual(change_log, board.header)
        fixed_board_manual: BoardV3 = BoardV3(header=fixed_header_manual, rows=tuple(fixed_rows),
                                              sheet_name=board.sheet_name)
        fixed_header_auto = _fix_header_auto(change_log, fixed_board_manual)
        fixed_board_auto: BoardV3 = BoardV3(header=fixed_header_auto, rows=tuple(fixed_rows),
                                            sheet_name=board.sheet_name)
        fixed_boards.append(fixed_board_auto)

    # Collect all cleaned boards and reconstruct final BOM
    fixed_bom: BomV3 = BomV3(boards=tuple(fixed_boards), file_name=bom.file_name, is_cost_bom=bom.is_cost_bom)

    # Extract full log snapshot for external reporting
    frozen_change_log = change_log.render()

    return fixed_bom, frozen_change_log


def _fix_header_manual(change_log: ChangeLog, header: HeaderV3) -> HeaderV3:
    """
    Apply manual header corrections in a defined order and append any resulting messages to the change-log.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        header (HeaderV3): Header instance to correct.

    Returns:
        HeaderV3: A new header with manual fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to header fields.
    """
    # Define ordered header cleaning sequence (function, attribute name)
    cases = [
        (correct.model_number, HeaderV3AttrNames.MODEL_NO),
        (correct.board_name, HeaderV3AttrNames.BOARD_NAME),
        (correct.board_supplier, HeaderV3AttrNames.BOARD_SUPPLIER),
        (correct.build_stage, HeaderV3AttrNames.BUILD_STAGE),
        (correct.bom_date, HeaderV3AttrNames.BOM_DATE),
        (correct.overhead_cost, HeaderV3AttrNames.OVERHEAD_COST),
    ]

    attr_name = None

    # Apply fix for each field and collect logs
    for fn, attr_name in cases:
        try:
            original_value = getattr(header, attr_name)
            result_value, result_log = fn(header)

            if result_value != original_value:
                header = replace(header, **{attr_name: result_value})
            change_log.add_entry(result_log)
        except Exception as e:
            raise ValueError(
                f"{type(header).__name__} correction failed on '{attr_name}'. Latest partial row:\n{header!r}"
            ) from e
    return header


def _fix_header_auto(change_log: ChangeLog, board: BoardV3) -> HeaderV3:
    """
    Apply automatic header corrections (e.g., computed costs) based on board context and append messages to the change-log.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        board (BoardV3): Board providing header and row context for computed fields.

    Returns:
        HeaderV3: A new header with automatic fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to header fields.
    """
    header = board.header
    attr_name = None

    # 1. Fix material cost math
    try:
        attr_name = HeaderV3AttrNames.MATERIAL_COST
        original_value = getattr(header, attr_name)
        result_value, result_log = correct.material_cost(board)

        if result_value != original_value:
            header = replace(header, **{attr_name: result_value})
        change_log.add_entry(result_log)
    except Exception as e:
        raise ValueError(
            f"{type(header).__name__} correction failed on '{attr_name}'. Latest partial row:\n{header!r}"
        ) from e

    # 2. Fix total cost math
    try:
        attr_name = HeaderV3AttrNames.TOTAL_COST
        original_value = getattr(header, attr_name)
        result_value, result_log = correct.total_cost(header)

        if result_value != original_value:
            header = replace(header, **{attr_name: result_value})
        change_log.add_entry(result_log)
    except Exception as e:
        raise ValueError(
            f"{type(header).__name__} correction failed on '{attr_name}'. Latest partial row:\n{header!r}"
        ) from e
    return header


def _fix_row_manual(change_log: ChangeLog, row: RowV3) -> RowV3:
    """
    Apply manual row corrections in a defined order and append messages for any detected or applied changes.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        row (RowV3): Row instance to correct.

    Returns:
        RowV3: A new row with manual fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to row fields.
    """
    # Define ordered header cleaning sequence (function, attribute name)
    cases = [
        (correct.item, RowV3AttrNames.ITEM),
        (correct.component_type, RowV3AttrNames.COMPONENT_TYPE),
        (correct.device_package, RowV3AttrNames.DEVICE_PACKAGE),
        (correct.description, RowV3AttrNames.DESCRIPTION),
        (correct.unit, RowV3AttrNames.UNITS),
        (correct.classification, RowV3AttrNames.CLASSIFICATION),
        (correct.manufacturer, RowV3AttrNames.MFG_NAME),
        (correct.mfg_part_number, RowV3AttrNames.MFG_PART_NO),
        (correct.ul_vde_number, RowV3AttrNames.UL_VDE_NO),
        (correct.validated_at, RowV3AttrNames.VALIDATED_AT),
        (correct.qty, RowV3AttrNames.QTY),
        (correct.designator, RowV3AttrNames.DESIGNATORS),
        (correct.unit_price, RowV3AttrNames.UNIT_PRICE),
    ]

    attr_name = None

    # Apply fix for each field and collect logs
    for fn, attr_name in cases:
        try:
            original_value = getattr(row, attr_name)
            result_value, result_log = fn(row)

            if result_value != original_value:
                row = replace(row, **{attr_name: result_value})
            change_log.add_entry(result_log)
        except Exception as e:
            raise ValueError(
                f"{type(row).__name__} correction failed on '{attr_name}'. Latest partial row:\n{row!r}"
            ) from e
    return row


def _fix_row_auto(change_log: ChangeLog, row: RowV3) -> RowV3:
    """
    Apply automatic row corrections (e.g., lookups, expansions, and computed totals) and append messages to the change-log.

    Args:
        change_log (ChangeLog): Context-aware collector for change messages.
        row (RowV3): Row instance to correct.

    Returns:
        RowV3: A new row with automatic fixes applied.

    Raises:
        ValueError: If corrected values cannot be mapped back to row fields.
    """
    # Define ordered header cleaning sequence (function, attribute name)
    cases = [
        (correct.component_type_lookup, RowV3AttrNames.COMPONENT_TYPE),
        (correct.expand_designators, RowV3AttrNames.DESIGNATORS),
        (correct.sub_total, RowV3AttrNames.SUB_TOTAL),
    ]

    attr_name = None

    # Apply fix for each field and collect logs
    for fn, attr_name in cases:
        try:
            original_value = getattr(row, attr_name)
            result_value, result_log = fn(row)

            if result_value != original_value:
                row = replace(row, **{attr_name: result_value})
            change_log.add_entry(result_log)
        except Exception as e:
            raise ValueError(
                f"{type(row).__name__} correction failed on '{attr_name}'. Latest partial row:\n{row!r}"
            ) from e
    return row
