"""
Version-3 Bill-of-Materials (BOM) verification orchestrator.

This module coordinates all field-level and logic-level verification for a V3 BOM. It delegates verification to the public `approve` interfaces and raises context-rich errors that include the failing function name and the underlying rule violation. It is used by the BOM ingestion pipeline to guarantee row and header integrity before normalization or persistence.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.verifiers import _v3_bom as verify
    verify.verify_v3_bom(bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - Internal Modules:
        * src.approve.interfaces  (field + logic verification)
        * src.models.interfaces   (BOM, Board, Row, Header models)

Notes:
    - Fail-fast: the first ValueError halts verification with contextual details.
    - Unexpected exceptions are wrapped in RuntimeError with function context.

License:
    Internal Use Only.
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

from src.approve import interfaces as approve
from src.models.interfaces import (
    BomV3,
    HeaderV3,
    RowV3,
)


def verify_v3_bom(bom: BomV3) -> None:
    """
    Run all Version 3 BOM verification on the given BOM instance.

    Iterates through all boards, headers, and rows and delegates both field-level
    and logic-level verification to the `approve` interfaces. Stops on the first
    rule violation and wraps the error with BOM filename context.

    Args:
        bom (BomV3): Parsed BOM object containing boards, headers, and rows
            to be verified.

    Returns:
        None: All verifications completed successfully without raising an exception.

    Raises:
        ValueError: If any rule-based verification fails for a header or row.
        RuntimeError: If an unexpected exception occurs during verification.
    """
    # Iterate through all boards and rows and run field-level and logic-level verifications.
    try:
        for board in bom.boards:
            # Row-level verifications (field + logic) for each row on the board.
            for row in board.rows:
                _verify_row_value(row)
                _verify_row_logic(row)
            # Header verifications that depend on the full set of rows.
            _verify_header_logic(board.header, board.rows)
            _verify_header_value(board.header)
    except ValueError as error:
        raise ValueError(
            f"Verification failed of file '{bom.file_name}'"
            f"\n{error}"
        ) from error
    except Exception as ex:
        raise RuntimeError(
            f"Unexpected error during verification of file '{bom.file_name}'"
            f"\n{ex}"
        ) from ex

    return


def _verify_header_value(header: HeaderV3) -> None:
    """
    Run field-level verification on BOM header values.

    Delegates each header field to the corresponding `approve` verification
    function and re-raises failures with function-name context for easier debugging.

    Args:
        header (HeaderV3): Header instance whose fields are being verified.

    Returns:
        None: All header field verifications passed without raising an exception.

    Raises:
        ValueError: If a header field fails a rule-based verification.
        RuntimeError: If an unexpected exception occurs inside a header
            verification function.
    """
    # Pair each header field with its corresponding verification function.
    cases = [
        (approve.model_number, header.model_no),
        (approve.board_name, header.board_name),
        (approve.board_supplier, header.board_supplier),
        (approve.build_stage, header.build_stage),
        (approve.bom_date, header.bom_date),
        (approve.material_cost, header.material_cost),
        (approve.overhead_cost, header.overhead_cost),
        (approve.total_cost, header.total_cost),
    ]
    # Run each field-level verification and wrap failures with function context.
    for fn, value in cases:
        try:
            fn(value)
        except ValueError as error:
            raise ValueError(
                f"Header verification failed at '{fn.__name__}'"
                f"\n{error}"
            ) from error
        except Exception as ex:
            raise RuntimeError(
                f"Unexpected error during header verification at '{fn.__name__}'"
                f"\n{ex}"
            ) from ex
    return


def _verify_header_logic(header: HeaderV3, rows: tuple[RowV3, ...]) -> None:
    """
    Run logic-level verification between header totals and row-level cost data.

    Uses the `approve` interfaces to confirm that material and total cost values
    in the header are consistent with the row data.

    Args:
        header (HeaderV3): BOM header whose computed totals are being verified.
        rows (tuple[RowV3, ...]): BOM rows used to derive material-cost
            calculations.

    Returns:
        None: All header logic verifications passed without raising an exception.

    Raises:
        ValueError: If a header-level logic rule fails.
        RuntimeError: If an unexpected exception occurs inside a header logic
            verification function.
    """
    # Track the currently executing verification function for clearer error messages.
    fn = None
    try:
        fn = approve.material_cost_calculation
        approve.material_cost_calculation(rows, header)
        fn = approve.total_cost_calculation
        approve.total_cost_calculation(header)
    except ValueError as error:
        raise ValueError(
            f"Header verification failed at '{fn.__name__}'"
            f"\n{error}"
        ) from error
    except Exception as ex:
        raise RuntimeError(
            f"Unexpected error during header verification at '{fn.__name__}'"
            f"\n{ex}"
        ) from ex

    return


def _verify_row_value(row: RowV3) -> None:
    """
    Run field-level verification on a single BOM row.

    Delegates each row field to the corresponding `approve` verification
    function and re-raises failures with function-name context for easier debugging.

    Args:
        row (RowV3): Row instance whose fields are being verified.

    Returns:
        None: All row field verifications passed without raising an exception.

    Raises:
        ValueError: If a row field fails a rule-based verification.
        RuntimeError: If an unexpected exception occurs inside a row field
            verification function.
    """
    cases = [
        (approve.item, row.item),
        (approve.component_type, row.component_type),
        (approve.device_package, row.device_package),
        (approve.description, row.description),
        (approve.units, row.units),
        (approve.classification, row.classification),
        (approve.mfg_name, row.mfg_name),
        (approve.mfg_part_no, row.mfg_part_number),
        (approve.ul_vde_number, row.ul_vde_number),
        (approve.validated_at, row.validated_at),
        (approve.quantity, row.qty),
        (approve.designator, row.designators),
        (approve.unit_price, row.unit_price),
        (approve.sub_total, row.sub_total),
    ]

    # Run each row-level field verification and wrap failures with function context.
    for fn, value in cases:
        try:
            fn(value)
        except ValueError as error:
            raise ValueError(
                f"Row verification failed at '{fn.__name__}'"
                f"\n{error}"
            ) from error
        except Exception as ex:
            raise RuntimeError(
                f"Unexpected error during row verification at '{fn.__name__}'"
                f"\n{ex}"
            ) from ex

    return


def _verify_row_logic(row: RowV3) -> None:
    """
    Run logic-level verification on a single BOM row.

    Applies row-level business rules (e.g., designator requirements, quantity and
    price consistency) through the `approve` interfaces.

    Args:
        row (RowV3): Row instance whose aggregate logic and relationships
            are being verified.

    Returns:
        None: All row logic verifications passed without raising an exception.

    Raises:
        ValueError: If a row-level logic rule fails.
        RuntimeError: If an unexpected exception occurs inside a row logic
            verification function.
    """
    cases = [
        approve.designator_required,
        approve.designator_count,
        approve.quantity_zero,
        approve.unit_price_specified,
        approve.subtotal_zero,
        approve.sub_total_calculation,
    ]

    # Run each row-level logic verification and wrap failures with function context.
    for fn in cases:
        try:
            fn(row)
        except ValueError as error:
            raise ValueError(
                f"Row verification failed at '{fn.__name__}'"
                f"\n{error}"
            ) from error
        except Exception as ex:
            raise RuntimeError(
                f"Unexpected error during row verification at '{fn.__name__}'"
                f"\n{ex}"
            ) from ex

    return
