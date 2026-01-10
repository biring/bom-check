"""
Cross-field logic validators for BOM rows and header fields.

This module enforces multi-cell constraints within `Row` and `Header` field.. Validators raise ValueError on violation; otherwise they return None.

Example Usage:
    # Preferred usage via public package interface:
    from src.models import interfaces as model
    from src.approve import interfaces as approve
    row = model.Row(item="", qty="2", designator="C1, C2", unit_price="0.25", sub_total="0.50")
    approve.quantity_zero(row)

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.models import interfaces as model
    from src.approve import _logic as logic
    row = model.Row(item="2", qty="2", designator="C1, C2", unit_price="0.25", sub_total="0.50")
    logic.sub_total_calculation(row)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Fail-fast: raises ValueError with clear, field-referenced messages.
    - Skip-on-invalid: if a base field cannot be parsed by `src.utils.parser.parse_to_*`, the check is skipped.
    - Equality: uses `src.rules.approve._common.floats_equal` for monetary products/sums; provide normalized inputs.
    - Designators: simple comma-split; upstream normalization (trim, dedupe) is expected.
    - Scope: internal-only validators used by the BOM approval/review pipeline.

License:
 - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API

_VALUE_ERROR: str = "'{a}' = '{b}' is not correct. "

_QTY_ZERO_RULE: str = "'{a}' must be more than zero when '{b}' is blank. "
_DESIGNATOR_REQUIRED_RULE: str = "'{a}' must be listed when '{b}' is '{c}' (an integer more than zero). "
_DESIGNATOR_COUNT_RULE: str = "'{a}' count of '{b}' must match '{c}' value of '{d}'. "
_UNIT_PRICE_SPECIFIED_RULE: str = "'{a}' must be more than zero when '{b}' is '{c}' (more than zero)."
_SUB_TOTAL_ZERO_RULE: str = "'{a}' must be zero when '{b}' is '{c}' (zero). "
_SUB_TOTAL_CALC_RULE: str = "'{a}' must be equal to the product of '{b}' = '{c}' and '{d}' = '{e}'. "
_MATERIAL_COST_CALC_RULE: str = "'{a}' must be equal to the aggregate of '{b}'. "
_TOTAL_COST_CALC_RULE: str = "'{a}' must be equal to the sum of '{b}' = '{c}' and '{d}' = '{e}'. "

import src.utils as utils

from src.approve import _common as common

from src.models.interfaces import (
    RowV3,
    HeaderV3,
)

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)


def quantity_zero(row: RowV3) -> None:
    """
    Validate quantity is zero when item is blank.

    If base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing the quantity to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If item is blank and quantity is more than zero.
    """
    # Validate cell values
    try:
        qty = utils.parser.parse_to_float(row.qty)
    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: if item is blank, quantity must be exactly zero
    if row.item == "" and qty != 0.0:
        raise ValueError(
            _VALUE_ERROR.format(
                a=TableLabelsV3.QUANTITY,
                b=row.qty,
            )
            + _QTY_ZERO_RULE.format(
                a=TableLabelsV3.QUANTITY,
                b=TableLabelsV3.ITEM,
            )
        )


def designator_required(row: RowV3) -> None:
    """
    Validate designator is specified when quantity is an integer more than zero.

    If base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing the designator to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If designator is blank when quantity is an integer more than zero.
    """
    # Validate cell values
    try:
        qty = utils.parser.parse_to_integer(row.qty)
    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: if integer quantity > 0, designator must be specified (non-empty)
    if qty >= 1 and row.designators == "":
        raise ValueError(
            _VALUE_ERROR.format(
                a=TableLabelsV3.DESIGNATORS,
                b=row.designators,
            )
            + _DESIGNATOR_REQUIRED_RULE.format(
                a=TableLabelsV3.DESIGNATORS,
                b=TableLabelsV3.QUANTITY,
                c=row.qty,
            )
        )


def designator_count(row: RowV3) -> None:
    """
    Validate the comma-separated designator count equals quantity when quantity is a greater than zero integer.

    If base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing the designator to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If designator count does not match integer quantity.
    """
    # Validate cell values
    try:
        integer_qty = utils.parser.parse_to_integer(row.qty)
        designators = [d.strip() for d in row.designators.split(",") if d.strip()]
        designator_count = len(designators)

    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: For integer quantity, designator count must equal quantity
    if integer_qty > 0 and integer_qty != designator_count:
        raise ValueError(
            _VALUE_ERROR.format(
                a=TableLabelsV3.DESIGNATORS,
                b=row.designators,
            )
            + _DESIGNATOR_COUNT_RULE.format(
                a=TableLabelsV3.DESIGNATORS,
                b=row.designators,
                c=TableLabelsV3.QUANTITY,
                d=row.qty,
            )
        )


def unit_price_specified(row: RowV3):
    """
    Validate the unit price is greater than zero when quantity is greater than zero.

    If base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing the unit price to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If unit price is not more than zero when quantity is more than zero.
    """
    # Validate cell values
    try:
        qty = utils.parser.parse_to_float(row.qty)
        unit_price = utils.parser.parse_to_float(row.unit_price)
    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: When quantity > 0, unit price > 0
    if qty > 0.0 >= unit_price:
        raise ValueError(
            _VALUE_ERROR.format(
                a=TableLabelsV3.UNIT_PRICE,
                b=row.unit_price,
            )
            + _UNIT_PRICE_SPECIFIED_RULE.format(
                a=TableLabelsV3.UNIT_PRICE,
                b=TableLabelsV3.QUANTITY,
                c=row.qty,
            )
        )


def subtotal_zero(row: RowV3):
    """
    Validate the sub-total is zero when quantity is zero.

    If base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing the sub-total to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If sub-total is not zero when quantity is zero.
    """
    # Validate cell values
    try:
        qty = utils.parser.parse_to_float(row.qty)
        sub_total = utils.parser.parse_to_float(row.sub_total)
    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: When quantity is zero, sub-total must be zero
    if qty == 0.0 and sub_total != 0.0:
        raise ValueError(
            _VALUE_ERROR.format(
                a=TableLabelsV3.SUB_TOTAL,
                b=row.sub_total,
            )
            + _SUB_TOTAL_ZERO_RULE.format(
                a=TableLabelsV3.SUB_TOTAL,
                b=TableLabelsV3.QUANTITY,
                c=row.qty,
            )
        )


def sub_total_calculation(row: RowV3) -> None:
    """
    Validate the sub-total is the product of quantity and unit price.

    If base fields are invalid, the check is skipped.

    Args:
        row (Row): BOM row containing the sub-total to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If sub-total is not the product of quantity and unit price.
    """
    # Validate cell values
    try:
        qty = utils.parser.parse_to_float(row.qty)
        unit_price = utils.parser.parse_to_float(row.unit_price)
        sub_total = utils.parser.parse_to_float(row.sub_total)
    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: sub-total must be the product of quantity and unit price
    if not common.floats_equal(sub_total, qty * unit_price):
        raise ValueError(
            _VALUE_ERROR.format(
                a=TableLabelsV3.SUB_TOTAL,
                b=row.sub_total,
            )
            + _SUB_TOTAL_CALC_RULE.format(
                a=TableLabelsV3.SUB_TOTAL,
                b=TableLabelsV3.QUANTITY,
                c=row.qty,
                d=TableLabelsV3.UNIT_PRICE,
                e=row.unit_price,
            )
        )


def material_cost_calculation(rows: list[RowV3], header: HeaderV3) -> None:
    """
    Validate the material cost is the aggregate of all sub-totals.

    If base fields are invalid, the check is skipped.

    Args:
        rows (list[Row]): BOM rows containing the sub-total.
        header (Header): BOM header containing the material cost to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If material cost is not the aggregate of sub-totals.
    """
    aggregate_sub_totals: float = 0.0
    parsed: bool = False
    for row in rows:
        try:
            sub_total = utils.parser.parse_to_float(row.sub_total)
            aggregate_sub_totals += sub_total
            parsed = True
        except ValueError:
            continue

    if not parsed:
        return  # Skip logic validation if cell validation fails

    # Validate cell value
    try:
        material_cost = utils.parser.parse_to_float(header.material_cost)
    except ValueError:
        return  # Skip logic validation if cell validation fails

    # Rule: material cost must add up to the aggregate of sub-totals
    if not common.floats_equal(material_cost, aggregate_sub_totals):
        raise ValueError(
            _VALUE_ERROR.format(
                a=HeaderLabelsV3.MATERIAL_COST,
                b=header.material_cost,
            )
            + _MATERIAL_COST_CALC_RULE.format(
                a=HeaderLabelsV3.MATERIAL_COST,
                b=TableLabelsV3.SUB_TOTAL,
            )
        )


def total_cost_calculation(header: HeaderV3) -> None:
    """
    Validate the total cost is the sum of material cost and overhead cost.

    If base fields are invalid, the check is skipped.

    Args:
        header (Header): BOM header to validate.

    Returns:
        None: Validation succeeds silently if the rule is satisfied.

    Raises:
        ValueError: If total cost is not the sum of material cost and overhead cost.
    """
    # Validate cell values
    try:
        material_cost = utils.parser.parse_to_float(header.material_cost)
        overhead_cost = utils.parser.parse_to_float(header.overhead_cost)
        total_cost = utils.parser.parse_to_float(header.total_cost)
    except ValueError:
        # Skip validation if base fields are invalid
        return

    # Rule: total cost must be the sum of material cost and overhead cost
    if not common.floats_equal(total_cost, material_cost + overhead_cost):
        raise ValueError(
            _VALUE_ERROR.format(
                a=HeaderLabelsV3.TOTAL_COST,
                b=header.total_cost,
            )
            + _TOTAL_COST_CALC_RULE.format(
                a=HeaderLabelsV3.TOTAL_COST,
                b=HeaderLabelsV3.MATERIAL_COST,
                c=header.material_cost,
                d=HeaderLabelsV3.OVERHEAD_COST,
                e=header.overhead_cost,
            )
        )
