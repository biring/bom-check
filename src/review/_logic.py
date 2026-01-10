"""
Review helpers that convert cross-field BOM validators into non-raising string-returning checks.

This module wraps validators from `src.approve.interfaces` and captures their ValueError text via `src.review._common.review_and_capture_by_args`, returning "" on success or the error message on failure. Intended for batch review/reporting where execution must not stop.

Example Usage:
    # Preferred usage via public package interface:
    from src.models import interfaces as model
    from src.review import interfaces as review
    row = model.Row(item="", qty="2", designator="", unit_price="0.25", sub_total="0.50")
    msg = review.logic.quantity_zero(row)

    # Direct internal usage (acceptable in unit tests or internal scripts):
    from src.models import interfaces as model
    from src.review import _logic as review
    msg = review.designator_required(model.Row(item="R1", qty="1", designator="", unit_price="0.10", sub_total="0.10"))

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: None

Notes:
    - Each function mirrors a validator in `src.approve.interfaces` but returns a string instead of raising.
    - Uses `src.review._common.review_and_capture_by_args` to normalize error capture and messaging.
    - Designed for report-generation pipelines; functions are pure with respect to inputs and do not mutate models.
    - Internal module; not part of the public API surface.

License:
    - Internal Use Only
"""
__all__: list[str] = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.models.interfaces import (
    HeaderV3,
    RowV3,
)
from src.approve import interfaces as approve
from src.review import _common as common  # kept for parity with header/row review modules


def quantity_zero(row: RowV3) -> str:
    """
    Validate quantity is zero when item is blank.

    Args:
        row (RowV3): BOM row to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.quantity_zero, row)


def designator_required(row: RowV3) -> str:
    """
    Validate designator is specified when quantity is an integer more than zero.

    Args:
        row (RowV3): BOM row to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.designator_required, row)


def designator_count(row: RowV3) -> str:
    """
    Validate the comma-separated designator count equals the integer quantity.

    Args:
        row (RowV3): BOM row to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.designator_count, row)


def unit_price_specified(row: RowV3) -> str:
    """
    Validate unit price is greater than zero when quantity is greater than zero.

    Args:
        row (RowV3): BOM row to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.unit_price_specified, row)


def subtotal_zero(row: RowV3) -> str:
    """
    Validate sub-total is zero when quantity is zero.

    Args:
        row (RowV3): BOM row to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.subtotal_zero, row)


def sub_total_calculation(row: RowV3) -> str:
    """
    Validate sub-total equals (quantity * unit price).

    Args:
        row (RowV3): BOM row to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.sub_total_calculation, row)


def material_cost_calculation(rows: tuple[RowV3, ...], header: HeaderV3) -> str:
    """
    Validate header.material_cost equals the aggregate of row sub_totals.

    Args:
        rows (tuple[Row, ...]): Collection of BOM rows.
        header (HeaderV3): BOM header containing the material_cost to validate.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.material_cost_calculation, rows, header)


def total_cost_calculation(header: HeaderV3) -> str:
    """
    Validate header.total_cost equals (material_cost + overhead_cost).

    Args:
        header (HeaderV3): BOM header with cost fields.

    Returns:
        str: "" if valid; otherwise a descriptive error message.
    """
    return common.review_and_capture_by_args(approve.total_cost_calculation, header)
