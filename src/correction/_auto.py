"""
Autocorrection helpers for BOM numeric and reference fields.

Provides pure functions that compute corrected values from existing fields and return both the corrected string and a one-line change log suitable for audit trails. Parsing is delegated to shared utilities.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    import src.correction._auto as auto
    value, log = auto.material_cost(header, rows)

Dependencies:
    - Python >= 3.10
    - Standard Library: re
    - Project Modules: src.models.interfaces, src.utils.parser.parse_to_float, src.approve._common.floats_equal

Notes:
    - Empty change_log indicates no correction was applied
    - Internal-only module; API may change without notice

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)
from src.models.interfaces import (
    BoardV3,
    HeaderV3,
    RowV3,
)

from src.lookups import interfaces as lookup
from src.settings import application as app_settings
from src.utils import parser

# TODO : Reorganize to one shared folder for all rules or make math a utility
from . import _helper as helper

# Strict range pattern: no spaces around the dash, same alpha prefix on both sides
DESIGNATOR_RANGE_RE = re.compile(r"^([A-Za-z]+)(\d+)-\1(\d+)$")

TEMPLATE_AUTOCORRECT_MSG = "'{field}' changed from '{before}' to '{after}'. {reason}"

LOG_DESIGNATOR_EXPAND = "Designator range expanded to remove '-' dash."
LOG_SUBTOTAL_CHANGE = "Sub-total set to the product of Quantity and Designator."
LOG_MATERIAL_COST_CHANGE = "Material cost set to the sum of sub totals."
LOG_TOTAL_COST_CHANGE = "Total cost set to the product of material and overhead cost."

ERR_FLOAT_PARSE = "{field} value '{value}' is not a valid floating point number: {reason}"


def component_type_lookup(row: RowV3) -> tuple[str, str]:
    """
    Perform fuzzy lookup to map a raw component type string to a standardized type key.

    This function compares the input string against all known component type variants using both Jaccard and Levenshtein similarity. It ignores specific substrings (e.g., "SMD", "DIP"), and if both metrics produce the same best match above the given threshold, the corresponding canonical component key is returned. If no match passes the threshold, the original input is returned.

    Args:
        row (RowV3): Bom row containing the component type to autocorrect.

    Returns:
        tuple[str, str]:
            - Normalized component type (canonical key or original input if no match).
            - Audit log message (empty string if no change).

    Raises:
        None

    """
    str_in = row.component_type
    str_out = str_in
    change_log = ""

    ignore_str: tuple[str, ...] = (
        tuple(app_settings.get_settings().get_value(app_settings.KEYS.COMPONENT_TYPE_STRING_IGNORE_MASK, list))
    )
    lookup_dict: dict[str, list[str]] = lookup.get_component_type_lookup_table()

    # ignore strings such as SMD and DIP if found in component type name as they add not value
    str_test = str_in
    for remove_str in ignore_str:
        str_test = str_test.replace(remove_str, '')

    # Get all values from the component dict
    value_list = []
    for value in lookup_dict.values():
        if isinstance(value, str):
            value_list.append(value)
        elif isinstance(value, list):
            value_list.extend(value)
    value_list = tuple(value_list)

    # Get the best matched value
    value1, level1 = helper.jaccard_match(str_test, value_list)
    value2, level2 = helper.levenshtein_match(str_test, value_list)

    key_matches: list[str] = []
    if value1 != "" and value2 != "" and value1 == value2:
        # Get the key of the matched value
        for key, values in lookup_dict.items():
            if value1 in values:
                key_matches.append(key)

    if len(key_matches) == 1 and str_in != key_matches[0]:
        str_out = key_matches[0]

        reason = "{Value1} = {Level1:1.2f}. {Value2} = {Level2:1.2f}. ".format(
            Value1=value1, Level1=level1, Value2=value2, Level2=level2
        )
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=TableLabelsV3.COMPONENT_TYPE,
            before=str_in,
            after=str_out,
            reason=reason
        )
    elif len(key_matches) > 1:
        # TODO: log ambiguity with match list example ("For '{str_in}' component type found multiple keys: {key_matches}. Expected only one match")
        pass

    return str_out, change_log


def expand_designators(row: RowV3) -> tuple[str, str]:
    """
    Expands designator ranges within the string.

    This function processes a string containing comma-separated reference designators and expands any ranges written in the form "PrefixStart-PrefixEnd". Each expanded value is preserved with its original prefix, while non-range values remain unchanged. The result is returned as a comma-separated string. For example if input is "R1, R3-R6, R12, R45-R43" output will be "R1,R3,R4,R5,R6,R12,R45,R44,R43"

    Notes:
        - The input must be a valid string; no NaN or non-string checks are performed.
        - Ranges must not contain spaces around the dash (e.g., "R3-R6" is valid, "R3 - R6" is not).
        - Both sides of the range must share the same alphabetic prefix.
        - Descending ranges (e.g., "R6-R3") are supported and expanded in reverse order.

    Args:
        row (RowV3): Bom row containing the designator string, possibly with ranges, to autocorrect.  .

    Returns:
        tuple[str, str]: Range expanded designator string, change log string.
    """
    str_in = row.designators
    change_log = ""

    parts = [p.strip() for p in str_in.split(",") if p.strip()]
    expanded_designators: list[str] = []

    for part in parts:
        # Match "PREFIX<start>-PREFIX<end>" with same alpha prefix
        m = DESIGNATOR_RANGE_RE.fullmatch(part)
        if m:
            prefix, start_str, end_str = m.groups()
            start_idx, end_idx = int(start_str), int(end_str)
            # Support both ascending and descending ranges
            step = 1 if end_idx >= start_idx else -1
            expanded_designators.extend(f"{prefix}{i}" for i in range(start_idx, end_idx + step, step))
        else:
            expanded_designators.append(part)

    str_out = ",".join(expanded_designators)

    # Emit audit message only when the output differs
    if str_out != str_in:
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=TableLabelsV3.DESIGNATORS,
            before=str_in,
            after=str_out,
            reason=LOG_DESIGNATOR_EXPAND)

    return str_out, change_log


def material_cost(board: BoardV3) -> tuple[str, str]:
    """
    Autocorrect the material cost to sum of the sub-total.

    Base fields of sub-total and material cost must be float parse compatible.

    Args:
        board (BoardV3): Bom board containing the header with material cost to autocorrect.

    Returns:
     tuple[str, str]: correct material cost string, change log string.

    Raises:
        ValueError: If base fields cannot be parsed as float.
    """
    header: HeaderV3 = board.header
    rows: tuple[RowV3, ...] = board.rows
    str_out = header.material_cost
    change_log = ""
    material_cost_out = 0

    # Get float values for base fields
    for row in rows:
        try:
            sub_total_in = parser.parse_to_float(row.sub_total)
            material_cost_out += sub_total_in
        except ValueError as err:
            raise ValueError(ERR_FLOAT_PARSE.format(
                field=TableLabelsV3.SUB_TOTAL,
                value=row.sub_total,
                reason=err)
            )

    try:
        material_cost_in = parser.parse_to_float(header.material_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=HeaderLabelsV3.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )

    # Compare with tolerance to avoid float noise
    if not helper.floats_equal(material_cost_in, material_cost_out):
        str_out = str(material_cost_out)
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=HeaderLabelsV3.MATERIAL_COST,
            before=material_cost_in,
            after=material_cost_out,
            reason=LOG_MATERIAL_COST_CHANGE
        )

    return str_out, change_log


def sub_total(row: RowV3) -> tuple[str, str]:
    """
    Autocorrect the sub-total to the product of quantity and unit price.

    Base fields of quantity, unit price and sub-total must be float parse compatible.

    Args:
        row (Row): BOM row containing the sub-total to autocorrect.

    Returns:
     tuple[str, str]: correct sub-total string, change log string.

    Raises:
        ValueError: If base fields cannot be parsed as float.
    """
    str_out = row.sub_total
    change_log = ""

    # Get float values for base fields
    try:
        qty_in = parser.parse_to_float(row.qty)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=TableLabelsV3.QUANTITY,
            value=row.qty,
            reason=err)
        )

    try:
        unit_price_in = parser.parse_to_float(row.unit_price)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=TableLabelsV3.UNIT_PRICE,
            value=row.unit_price,
            reason=err)
        )
    try:
        sub_total_in = parser.parse_to_float(row.sub_total)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=TableLabelsV3.SUB_TOTAL,
            value=row.sub_total,
            reason=err)
        )

    sub_total_out = round(qty_in * unit_price_in, 6)

    # Compare with tolerance to avoid float noise
    if not helper.floats_equal(sub_total_in, sub_total_out):
        str_out = str(sub_total_out)
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=TableLabelsV3.SUB_TOTAL,
            before=sub_total_in,
            after=sub_total_out,
            reason=LOG_SUBTOTAL_CHANGE
        )

    return str_out, change_log


def total_cost(header: HeaderV3) -> tuple[str, str]:
    """
    Autocorrect the total cost to the sum of material cost and overhead cost.

    Base fields of material overhead and total cost must be float parse compatible.

    Args:
        header (Header): BOM header containing the total cost to autocorrect.

    Returns:
        tuple[str, str]: correct total cost string, change log string.

    Raises:
        ValueError: If base fields cannot be parsed as float.
    """
    str_out = header.total_cost
    change_log = ""

    # Get float values for base fields
    try:
        material_cost_in = parser.parse_to_float(header.material_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=HeaderLabelsV3.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )

    try:
        overhead_cost_in = parser.parse_to_float(header.overhead_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=HeaderLabelsV3.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )
    try:
        total_cost_in = parser.parse_to_float(header.total_cost)
    except ValueError as err:
        raise ValueError(ERR_FLOAT_PARSE.format(
            field=HeaderLabelsV3.MATERIAL_COST,
            value=header.material_cost,
            reason=err)
        )

    total_cost_out = round(material_cost_in + overhead_cost_in, 6)

    # Compare with tolerance to avoid float noise
    if not helper.floats_equal(total_cost_in, total_cost_out):
        str_out = str(total_cost_out)
        change_log = TEMPLATE_AUTOCORRECT_MSG.format(
            field=HeaderLabelsV3.TOTAL_COST,
            before=total_cost_in,
            after=total_cost_out,
            reason=LOG_TOTAL_COST_CHANGE
        )

    return str_out, change_log
