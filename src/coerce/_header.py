"""
Coercers for BOM header fields using shared regex rule sets.

This module provides per-field coercion functions that normalize BOM header text values (e.g., board name, build stage, material cost) through ordered regex rules. Each function returns the cleaned value and a tuple of human-readable change log lines.

Example Usage:
    # Preferred usage via package interface:
    from src.coerce import interfaces as coerce
    value, log = coerce.board_name("  Power   PCBA  ")
    print(value)  # "Power PCBA"

    # Direct internal access (for tests or internal scripts only):
    from src.coerce import _header
    value, log = _header.model_number("  ab123x  ")
    print(value)  # "AB123X"

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal: src.coerce._helper (apply_rule), src.coerce._rules (field rule sets), src.models.interfaces (HeaderFields)

Notes:
    - Each function applies a deterministic sequence of regex-based `Rule` objects.
    - The shared coercion engine logs only effective changes, keeping transformations traceable.
    - Designed for use behind the package façade (`src.coerce.interfaces`); not intended for direct import.
    - Returns `(coerced_value, tuple_of_log_lines)` to support downstream audit or diff reporting.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.schemas.interfaces import (
    HeaderLabelsV3,
)
from . import _helper as helper
from . import _rules as rule


def model_number(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce model number string.

    Args:
        str_in (str): Raw model-number string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None: This function delegates errors to the common engine; it does not raise on its own.
    """
    # Apply the rule set and collect changes
    result = helper.apply_rule(str_in, rule.MODEL_NUMBER, HeaderLabelsV3.MODEL_NO)

    # Render the final normalized value and any rule-by-rule messages
    return result.coerced_value, result.render_changes()


def board_name(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce board name string.

    Args:
        str_in (str): Raw board-name string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.BOARD_NAME, HeaderLabelsV3.BOARD_NAME)

    return result.coerced_value, result.render_changes()


def board_supplier(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce board supplier string.

    Args:
        str_in (str): Raw supplier string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.BOARD_SUPPLIER, HeaderLabelsV3.BOARD_SUPPLIER)
    return result.coerced_value, result.render_changes()


def build_stage(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce build stage string.

    Args:
        str_in (str): Raw build-stage string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.BUILD_STAGE, HeaderLabelsV3.BUILD_STAGE)
    return result.coerced_value, result.render_changes()


def bom_date(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce BOM date string.

    Args:
        str_in (str): Raw date string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.BOM_DATE, HeaderLabelsV3.BOM_DATE)
    return result.coerced_value, result.render_changes()


def material_cost(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce material cost string.

    Args:
        str_in (str): Raw cost string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.MATERIAL_COST, HeaderLabelsV3.MATERIAL_COST)
    return result.coerced_value, result.render_changes()


def overhead_cost(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce overhead cost string.

    Args:
        str_in (str): Raw cost string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.OVERHEAD_COST, HeaderLabelsV3.OVERHEAD_COST)
    return result.coerced_value, result.render_changes()


def total_cost(str_in: str) -> tuple[str, tuple[str, ...]]:
    """
    Coerce total cost string.

    Args:
        str_in (str): Raw cost string.

    Returns:
        tuple[str, tuple[str, ...]]: (coerced value, change log)

    Raises:
        None
    """
    result = helper.apply_rule(str_in, rule.TOTAL_COST, HeaderLabelsV3.TOTAL_COST)
    return result.coerced_value, result.render_changes()
