"""
Checker for Version 3 BOM objects.

Coordinates value-level and logic-level checks across complete BOMs (boards, headers, rows) and returns accumulated diagnostics in a printable, uniform format without performing any direct I/O.

Example Usage:
    # Preferred usage via public package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.checkers import _bom as cb
    issues = cb.check_bom(...)
    print(issues)

Dependencies:
    - Python >= 3.10
    - Internal:
        - src.common.ChangeLog (IssueLog)
        - src.review.interfaces (field and logic checks)
        - src.models.interfaces (Bom, Board, Header, Row)

Notes:
    - Returns a tuple of diagnostic strings; does not raise on validation errors or perform logging/printing.
    - Separates header/row value checks from cross-field logic checks while sharing a common IssueLog accumulator.
    - Intended for internal use only; public callers should go through src.checkers.interfaces to preserve API boundaries.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

from src.common import ChangeLog as IssueLog
from src.review import interfaces as review

from src.models.interfaces import (
    BomV3,
    HeaderV3,
    RowV3,
)


def check_v3_bom(bom: BomV3) -> tuple[str, ...]:
    """
    Run all checks on a Version 3 BOM and return rendered diagnostic messages.

    Traverses all boards, headers, and rows in the BOM, applies field-level and logic-level check functions, and accumulates issues as printable diagnostic strings in the format "module, file, sheet, section, message".

    Args:
        bom (BomV3): Structured BOM instance containing boards, headers, and rows to check.

    Returns:
        tuple[str, ...]: Tuple of rendered diagnostic messages; empty if no issues are found.

    Raises:
        None: All issues are recorded in the IssueLog instead of raising exceptions.
    """
    issue_log: IssueLog = IssueLog()
    issue_log.set_module_name("Checker")
    issue_log.set_file_name(bom.file_name)

    # Check each board in the BOM
    for bom_board in bom.boards:
        issue_log.set_sheet_name(bom_board.sheet_name)

        # Row-level field and logic checks
        for row_index, row in enumerate(bom_board.rows, start=1):
            issue_log.set_section_name(f"{RowV3.__name__}: {row_index}")
            _check_row_value(issue_log, row)
            _check_row_logic(issue_log, row, bom.is_cost_bom)

        # Header-level checks
        issue_log.set_section_name(HeaderV3.__name__)
        _check_header_logic(issue_log, bom_board.header, bom_board.rows)
        _check_header_value(issue_log, bom_board.header)

    # Convert all accumulated issues to printable strings
    return issue_log.render()


def _check_header_value(issue_log: IssueLog, header: HeaderV3) -> None:
    """
    Run field-level checks on header values.

    Applies each field-specific check function to the header and records any returned issues in the shared IssueLog.

    Args:
        issue_log (IssueLog): Log used to record header check results.
        header (HeaderV3): Header instance whose field values are checked.

    Returns:
        None: Issues are recorded in the IssueLog.

    Raises:
        None: Check functions return issues; no exceptions are raised here.
    """
    # Map each header field to its corresponding check function
    field_checks = [
        (review.model_number, header.model_no),
        (review.board_name, header.board_name),
        (review.board_supplier, header.board_supplier),
        (review.build_stage, header.build_stage),
        (review.bom_date, header.bom_date),
        (review.material_cost, header.material_cost),
        (review.overhead_cost, header.overhead_cost),
        (review.total_cost, header.total_cost),
    ]

    # Execute each check and record any returned issue
    for check, field_value in field_checks:
        issue_log.add_entry(check(field_value))


def _check_header_logic(issue_log: IssueLog, header: HeaderV3, rows: tuple[RowV3, ...]) -> None:
    """
    Run logic-level checks between header values and row data.

    Evaluates cross-field rules, such as verifying material cost and total cost
    against derived row calculations, and records any issues in the IssueLog.

    Args:
        issue_log (IssueLog): Log used to record header logic issues.
        header (HeaderV3): Header containing the summary values being checked.
        rows (tuple[RowV3, ...]): Rows used to compute derived totals.

    Returns:
        None: All issues are captured in the IssueLog.

    Raises:
        None
    """
    # Check that header material cost matches row-derived totals
    issue_log.add_entry(review.material_cost_calculation(rows, header))

    # Check that total cost matches expected calculation
    issue_log.add_entry(review.total_cost_calculation(header))


def _check_row_value(issue_log: IssueLog, row: RowV3) -> None:
    """
    Run field-level checks on a single BOM row.

    Applies per-field check functions to the row and records any issues in the shared IssueLog.

    Args:
        issue_log (IssueLog): Log used to record field-level row issues.
        row (RowV3): Row instance whose individual fields are checked.

    Returns:
        None: Issues are recorded in the IssueLog.

    Raises:
        None
    """
    # Map each row field to the associated check function
    field_checks = [
        (review.item, row.item),
        (review.component_type, row.component_type),
        (review.device_package, row.device_package),
        (review.description, row.description),
        (review.units, row.units),
        (review.classification, row.classification),
        (review.mfg_name, row.mfg_name),
        (review.mfg_part_no, row.mfg_part_number),
        (review.ul_vde_number, row.ul_vde_number),
        (review.validated_at, row.validated_at),
        (review.quantity, row.qty),
        (review.designator, row.designators),
        (review.unit_price, row.unit_price),
        (review.sub_total, row.sub_total),
    ]

    # Execute each check and record its result
    for check, field_value in field_checks:
        issue_log.add_entry(check(field_value))


def _check_row_logic(issue_log: IssueLog, row: RowV3, is_cost_bom: bool) -> None:
    """
    Run logic-level checks on a single BOM row.

    Applies cross-field check functions (e.g., designator rules, subtotal calculations)
    and records all issues in the IssueLog.

    Args:
        issue_log (IssueLog): Log used to record logic-level row issues.
        row (RowV3): Row instance to check for logic consistency.
        is_cost_bom (bool): Whether the BOM includes cost data, used to determine which cost-related checks to enforce.

    Returns:
        None: Issues are recorded in the IssueLog.

    Raises:
        None
    """
    # Row-level logic checks involving multiple fields
    logic_checks = [
        review.designator_required,
        review.designator_count,
        review.quantity_zero,
        review.unit_price_specified,
        review.subtotal_zero,
        review.sub_total_calculation,
    ]

    # Unit price specified check is only applicable for costed BOMs
    if not is_cost_bom:
        logic_checks.remove(review.unit_price_specified)

    # Run all logic checks and capture their results
    for check_fn in logic_checks:
        issue_log.add_entry(check_fn(row))
