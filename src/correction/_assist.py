"""
Interactive helpers for validating and correcting BOM header and row fields.

This module provides wrappers that:
 - Prompt users for corrected values until validation passes
 - Delegate checks to `review` validators
 - Return corrected values with one-line change-log entries

Example Usage:
    # Preferred usage via package workflow:
    from src.correction import _assist as assist
    value, log = assist.part_number(header)

    # Direct module usage (acceptable in tests only):
    import src.correction._assist as assist
    value, log = assist.model_number(header)

Dependencies:
 - Python >= 3.10
 - Standard Library: typing
 - Internal Packages: src.models, src.review, src.cli, src.correction._helper

Notes:
 - Each function returns (corrected_value, change_log).
 - Designed for use within correction workflows; not a public API.
 - Relies on CLI interaction to capture user-supplied corrections.

License:
 - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API.

from src.models.interfaces import (
    HeaderV3,
    RowV3,
)

from src.review import interfaces as review

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

import src.correction._helper as helper

LOG_MANUAL_CHANGE = "Manual change by user."


def model_number(header: HeaderV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the header's model number, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.model_number` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        header (HeaderV3): The BOM header object containing the `model_no` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_model_number, change_log_line).
    """

    model_number_in = header.model_no

    # Loop: prompt user until `review.model_number` accepts the value
    model_number_out = helper.prompt_until_valid(
        data=str(header),
        fn=review.model_number,
        value=model_number_in,
        field=HeaderLabelsV3.MODEL_NO
    )

    # Emit a single, one-line audit trail entry (Field, Before, After, Reason)
    change_log = helper.generate_log_entry(
        field=HeaderLabelsV3.MODEL_NO,
        before=model_number_in,
        after=model_number_out,
        reason=LOG_MANUAL_CHANGE
    )

    return model_number_out, change_log


def board_name(header: HeaderV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the header's board name, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.board_name` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        header (HeaderV3): The BOM header object containing the `board_name` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_board_name, change_log_line).
    """

    board_name_in = header.board_name

    # Loop: prompt user until `review.board_name` accepts the value
    board_name_out = helper.prompt_until_valid(
        data=str(header),
        fn=review.board_name,
        value=board_name_in,
        field=HeaderLabelsV3.BOARD_NAME
    )

    # Emit a single, one-line audit trail entry (Field, Before, After, Reason)
    change_log = helper.generate_log_entry(
        field=HeaderLabelsV3.BOARD_NAME,
        before=board_name_in,
        after=board_name_out,
        reason=LOG_MANUAL_CHANGE
    )

    return board_name_out, change_log


def board_supplier(header: HeaderV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the header's board supplier, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.board_supplier` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        header (HeaderV3): The BOM header object containing the `board_supplier` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_board_supplier, change_log_line).
    """

    board_supplier_in = header.board_supplier

    # Loop: prompt user until `review.board_supplier` accepts the value
    board_supplier_out = helper.prompt_until_valid(
        data=str(header),
        fn=review.board_supplier,
        value=board_supplier_in,
        field=HeaderLabelsV3.BOARD_SUPPLIER
    )

    # Emit a single, one-line audit trail entry (Field, Before, After, Reason)
    change_log = helper.generate_log_entry(
        field=HeaderLabelsV3.BOARD_SUPPLIER,
        before=board_supplier_in,
        after=board_supplier_out,
        reason=LOG_MANUAL_CHANGE
    )

    return board_supplier_out, change_log


def build_stage(header: HeaderV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the header's build stage, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.build_stage` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        header (HeaderV3): The BOM header object containing the `build_stage` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_build_stage, change_log_line).
    """

    build_stage_in = header.build_stage

    # Loop: prompt user until `review.build_stage` accepts the value
    build_stage_out = helper.prompt_until_valid(
        data=str(header),
        fn=review.build_stage,
        value=build_stage_in,
        field=HeaderLabelsV3.BUILD_STAGE
    )

    # Emit a single, one-line audit trail entry (Field, Before, After, Reason)
    change_log = helper.generate_log_entry(
        field=HeaderLabelsV3.BUILD_STAGE,
        before=build_stage_in,
        after=build_stage_out,
        reason=LOG_MANUAL_CHANGE
    )

    return build_stage_out, change_log


def bom_date(header: HeaderV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the header's date, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.bom_date` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        header (HeaderV3): The BOM header object containing the `bom_date` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_date, change_log_line).
    """

    date_in = header.bom_date

    # Loop: prompt user until `review.bom_date` accepts the value
    date_out = helper.prompt_until_valid(
        data=str(header),
        fn=review.bom_date,
        value=date_in,
        field=HeaderLabelsV3.BOM_DATE
    )

    # Emit a single, one-line audit trail entry (Field, Before, After, Reason)
    change_log = helper.generate_log_entry(
        field=HeaderLabelsV3.BOM_DATE,
        before=date_in,
        after=date_out,
        reason=LOG_MANUAL_CHANGE
    )

    return date_out, change_log


def overhead_cost(header: HeaderV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the header's overhead cost, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.overhead_cost` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        header (HeaderV3): The BOM header object containing the `overhead_cost` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_overhead_cost, change_log_line).
    """

    overhead_cost_in = header.overhead_cost

    # Loop: prompt user until `review.overhead_cost` accepts the value
    overhead_cost_out = helper.prompt_until_valid(
        data=str(header),
        fn=review.overhead_cost,
        value=overhead_cost_in,
        field=HeaderLabelsV3.OVERHEAD_COST
    )

    # Emit a single, one-line audit trail entry (Field, Before, After, Reason)
    change_log = helper.generate_log_entry(
        field=HeaderLabelsV3.OVERHEAD_COST,
        before=overhead_cost_in,
        after=overhead_cost_out,
        reason=LOG_MANUAL_CHANGE
    )

    return overhead_cost_out, change_log


def item(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's item value, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.item` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `item` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_item, change_log_line).
    """
    item_in = row.item

    item_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.item,
        value=item_in,
        field=TableLabelsV3.ITEM
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.ITEM,
        before=item_in,
        after=item_out,
        reason=LOG_MANUAL_CHANGE
    )

    return item_out, change_log


def component_type(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's component type, returning the chosen value and an audit log entry.

    Uses a prompt-until-valid loop backed by `review.component_type` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `component_type` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_component_type, change_log_line).
    """
    component_type_in = row.component_type

    component_type_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.component_type,
        value=component_type_in,
        field=TableLabelsV3.COMPONENT_TYPE
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.COMPONENT_TYPE,
        before=component_type_in,
        after=component_type_out,
        reason=LOG_MANUAL_CHANGE
    )

    return component_type_out, change_log


def device_package(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's device package information.

    Uses a prompt-until-valid loop backed by `review.device_package` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `device_package` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_device_package, change_log_line).
    """
    device_package_in = row.device_package

    device_package_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.device_package,
        value=device_package_in,
        field=TableLabelsV3.DEVICE_PACKAGE
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.DEVICE_PACKAGE,
        before=device_package_in,
        after=device_package_out,
        reason=LOG_MANUAL_CHANGE
    )

    return device_package_out, change_log


def description(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's part description.

    Uses a prompt-until-valid loop backed by `review.description` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `description` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_description, change_log_line).
    """
    description_in = row.description

    description_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.description,
        value=description_in,
        field=TableLabelsV3.DESCRIPTION
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.DESCRIPTION,
        before=description_in,
        after=description_out,
        reason=LOG_MANUAL_CHANGE
    )

    return description_out, change_log


def unit(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's unit of measure.

    Uses a prompt-until-valid loop backed by `review.unit` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `unit` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_unit, change_log_line).
    """
    unit_in = row.units

    unit_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.units,
        value=unit_in,
        field=TableLabelsV3.UNITS
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.UNITS,
        before=unit_in,
        after=unit_out,
        reason=LOG_MANUAL_CHANGE
    )

    return unit_out, change_log


def classification(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's classification field.

    Uses a prompt-until-valid loop backed by `review.classification` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `classification` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_classification, change_log_line).
    """
    classification_in = row.classification

    classification_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.classification,
        value=classification_in,
        field=TableLabelsV3.CLASSIFICATION
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.CLASSIFICATION,
        before=classification_in,
        after=classification_out,
        reason=LOG_MANUAL_CHANGE
    )

    return classification_out, change_log


def manufacturer(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's manufacturer name.

    Uses a prompt-until-valid loop backed by `review.manufacturer` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `manufacturer` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_manufacturer, change_log_line).
    """
    manufacturer_in = row.mfg_name

    manufacturer_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.mfg_name,
        value=manufacturer_in,
        field=TableLabelsV3.MFG_NAME
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.MFG_NAME,
        before=manufacturer_in,
        after=manufacturer_out,
        reason=LOG_MANUAL_CHANGE
    )

    return manufacturer_out, change_log


def mfg_part_number(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's manufacturer part number (MPN).

    Uses a prompt-until-valid loop backed by `review.mfg.part_number` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `mfg_part_number` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_mfg_part_number, change_log_line).
    """
    mfg_part_number_in = row.mfg_part_number

    mfg_part_number_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.mfg_part_no,
        value=mfg_part_number_in,
        field=TableLabelsV3.MFG_PART_NO
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.MFG_PART_NO,
        before=mfg_part_number_in,
        after=mfg_part_number_out,
        reason=LOG_MANUAL_CHANGE
    )

    return mfg_part_number_out, change_log


def ul_vde_number(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's UL/VDE certification number.

    Uses a prompt-until-valid loop backed by `review.ul_vde_number` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `ul_vde_number` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_ul_vde_number, change_log_line).
    """
    ul_vde_number_in = row.ul_vde_number

    ul_vde_number_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.ul_vde_number,
        value=ul_vde_number_in,
        field=TableLabelsV3.UL_VDE_NO
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.UL_VDE_NO,
        before=ul_vde_number_in,
        after=ul_vde_number_out,
        reason=LOG_MANUAL_CHANGE
    )

    return ul_vde_number_out, change_log


def validated_at(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's validation timestamp or date.

    Uses a prompt-until-valid loop backed by `review.validated_at` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `validated_at` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_validated_at, change_log_line).
    """
    validated_at_in = row.validated_at

    validated_at_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.validated_at,
        value=validated_at_in,
        field=TableLabelsV3.VALIDATED_AT
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.VALIDATED_AT,
        before=validated_at_in,
        after=validated_at_out,
        reason=LOG_MANUAL_CHANGE
    )

    return validated_at_out, change_log


def qty(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's quantity field.

    Uses a prompt-until-valid loop backed by `review.qty` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `qty` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_qty, change_log_line).
    """
    qty_in = row.qty

    qty_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.quantity,
        value=qty_in,
        field=TableLabelsV3.QUANTITY
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.QUANTITY,
        before=qty_in,
        after=qty_out,
        reason=LOG_MANUAL_CHANGE
    )

    return qty_out, change_log


def designator(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's designator field.

    Uses a prompt-until-valid loop backed by `review.designator` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `designator` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_designator, change_log_line).
    """
    designator_in = row.designators

    designator_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.designator,
        value=designator_in,
        field=TableLabelsV3.DESIGNATORS
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.DESIGNATORS,
        before=designator_in,
        after=designator_out,
        reason=LOG_MANUAL_CHANGE
    )

    return designator_out, change_log


def unit_price(row: RowV3) -> tuple[str, str]:
    """
    Interactively validate and (if needed) correct the row's unit price value.

    Uses a prompt-until-valid loop backed by `review.unit_price` to enforce formatting rules, then emits a single-line change log suitable for audit trails.

    Args:
        row (RowV3): The BOM row object containing the `unit_price` field to validate.

    Returns:
        tuple[str, str]: A 2-tuple of (final_unit_price, change_log_line).
    """
    unit_price_in = row.unit_price

    unit_price_out = helper.prompt_until_valid(
        data=str(row),
        fn=review.unit_price,
        value=unit_price_in,
        field=TableLabelsV3.UNIT_PRICE
    )

    change_log = helper.generate_log_entry(
        field=TableLabelsV3.UNIT_PRICE,
        before=unit_price_in,
        after=unit_price_out,
        reason=LOG_MANUAL_CHANGE
    )

    return unit_price_out, change_log
