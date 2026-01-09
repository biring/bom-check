"""
Adapter module mapping Version 3 Excel BOM template labels to BOM V3 raw model fields.

This module provides a deterministic translation layer that adapts a Version 3 Excel BOM template schema into BOM V3 model-ready data structures. It defines strict, one-way mappings from template header and table labels to corresponding model attribute names and constructs populated model instances from pre-parsed label-to-value dictionaries. The module deliberately excludes Excel I/O, data normalization, and higher-level business rules, focusing solely on schema adaptation.

Key responsibilities
	- Define explicit one-way mappings between Version 3 template header labels and header model fields.
	- Define explicit one-way mappings between Version 3 template table labels and row model fields.
	- Enforce that input data is dictionary-based and structurally complete.
	- Construct populated header and row model instances from validated label-value mappings.

Example usage
	# Preferred usage via public package interface
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from src.adapters._template_v3_to_bom_v3 import map_template_v3_header_to_bom_v3_header
	header = map_template_v3_header_to_bom_v3_header(parsed_header_values)

Dependencies
	- Python 3.10+
	- Standard Library: None

Notes
	- Mappings are strict and one-way; unexpected or missing labels result in immediate errors.
	- Duplicate mappings to the same model field are treated as programming errors and fail fast.
	- All values are assumed to be pre-extracted and untyped; no coercion or validation is performed.
	- Intended to isolate template schema concerns from model construction without creating circular dependencies.

License
	Internal Use Only
"""
from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

from src.models.interfaces import (
    HeaderV3,
    HeaderV3AttrNames,
    RowV3,
    RowV3AttrNames,
)

# One-way mapping; keys are template labels, values are dataclass attribute names.
_TEMPLATE_V3_HEADER_LABEL_TO_HEADER_V3_ATTR_NAME: dict[str, str] = {
    HeaderLabelsV3.MODEL_NO: HeaderV3AttrNames.MODEL_NO,
    HeaderLabelsV3.BOARD_NAME: HeaderV3AttrNames.BOARD_NAME,
    HeaderLabelsV3.BOARD_SUPPLIER: HeaderV3AttrNames.BOARD_SUPPLIER,
    HeaderLabelsV3.BUILD_STAGE: HeaderV3AttrNames.BUILD_STAGE,
    HeaderLabelsV3.BOM_DATE: HeaderV3AttrNames.BOM_DATE,
    HeaderLabelsV3.MATERIAL_COST: HeaderV3AttrNames.MATERIAL_COST,
    HeaderLabelsV3.OVERHEAD_COST: HeaderV3AttrNames.OVERHEAD_COST,
    HeaderLabelsV3.TOTAL_COST: HeaderV3AttrNames.TOTAL_COST,
}

# One-way mapping; keys are template labels, values are dataclass attribute names.
_TEMPLATE_V3_TABLE_LABEL_TO_ROW_V3_ATTR_NAME: dict[str, str] = {
    TableLabelsV3.ITEM: RowV3AttrNames.ITEM,
    TableLabelsV3.COMPONENT_TYPE: RowV3AttrNames.COMPONENT_TYPE,
    TableLabelsV3.DEVICE_PACKAGE: RowV3AttrNames.DEVICE_PACKAGE,
    TableLabelsV3.DESCRIPTION: RowV3AttrNames.DESCRIPTION,
    TableLabelsV3.UNITS: RowV3AttrNames.UNITS,
    TableLabelsV3.CLASSIFICATION: RowV3AttrNames.CLASSIFICATION,
    TableLabelsV3.MFG_NAME: RowV3AttrNames.MFG_NAME,
    TableLabelsV3.MFG_PART_NO: RowV3AttrNames.MFG_PART_NO,
    TableLabelsV3.UL_VDE_NO: RowV3AttrNames.UL_VDE_NO,
    TableLabelsV3.VALIDATED_AT: RowV3AttrNames.VALIDATED_AT,
    TableLabelsV3.QUANTITY: RowV3AttrNames.QTY,
    TableLabelsV3.DESIGNATORS: RowV3AttrNames.DESIGNATORS,
    TableLabelsV3.UNIT_PRICE: RowV3AttrNames.UNIT_PRICE,
    TableLabelsV3.SUB_TOTAL: RowV3AttrNames.SUB_TOTAL,
}


def _assert_is_dict(values: object) -> None:
    """
    Ensure the provided values object is a dict.

    Args:
        values (object): Value to validate.

    Raises:
        TypeError: If values is not a dict.
    """
    if not isinstance(values, dict):
        raise TypeError(f"Expected 'values' to be a dict, got '{type(values).__name__}'.")


def _assert_no_extra_or_missing_keys(*, values: dict[str, str], allowed_keys: set[str], context: str) -> None:
    """
    Ensure the provided mapping contains exactly the allowed keys.

    Args:
        values (dict[str, str]): Mapping of label to value.
        allowed_keys (set[str]): Allowed label keys.
        context (str): Human-readable context for error messages.

    Raises:
        KeyError: If extra or missing keys are detected.
    """
    extra = set(values.keys()) - allowed_keys
    if extra:
        raise KeyError(f"Unexpected {context} labels encountered: {sorted(extra)!r}")

    missing = allowed_keys - set(values.keys())
    if missing:
        raise KeyError(f"Missing required {context} labels: {sorted(missing)!r}")


def map_template_v3_header_to_bom_v3_header(values: dict[str, str]) -> HeaderV3:
    """
    Convert a dict of {template v3 label: value} into a HeaderV3 instance.

    Args:
        values (dict[str, str]): Mapping of template header labels to cell values.

    Returns:
        HeaderV3: Populated HeaderV3 instance.

    Raises:
        KeyError: If a template label cannot be mapped to a HeaderV3 attribute, or if extra/missing labels are present.
        ValueError: If multiple template labels map to the same HeaderV3 attribute.
        TypeError: If values is not a dict.
    """
    _assert_is_dict(values)

    _assert_no_extra_or_missing_keys(
        values=values,
        allowed_keys=set(_TEMPLATE_V3_HEADER_LABEL_TO_HEADER_V3_ATTR_NAME.keys()),
        context="version 3 BOM template header",
    )

    header_kwargs: dict[str, str] = {}

    for template_label, cell_value in values.items():
        header_attr_name = _TEMPLATE_V3_HEADER_LABEL_TO_HEADER_V3_ATTR_NAME.get(template_label)

        if header_attr_name is None:
            raise KeyError(f"Unmapped version 3 BOM template header label encountered: {template_label!r}")

        if header_attr_name in header_kwargs:
            raise ValueError(f"Duplicate header attribute mapping detected for attribute '{header_attr_name}'.")

        header_kwargs[header_attr_name] = cell_value

    return HeaderV3(**header_kwargs)


def map_template_v3_table_to_bom_v3_row(values: dict[str, str]) -> RowV3:
    """
    Convert a dict of {template_label: value} into a RowV3 instance.

    Args:
        values (dict[str, str]): Mapping of template table labels to cell values.

    Returns:
        RowV3: Populated RowV3 instance.

    Raises:
        KeyError: If a template label cannot be mapped to a RowV3 attribute, or if extra/missing labels are present.
        ValueError: If multiple template labels map to the same RowV3 attribute.
        TypeError: If values is not a dict.
    """
    _assert_is_dict(values)

    _assert_no_extra_or_missing_keys(
        values=values,
        allowed_keys=set(_TEMPLATE_V3_TABLE_LABEL_TO_ROW_V3_ATTR_NAME.keys()),
        context="version 3 BOM template table",
    )

    row_kwargs: dict[str, str] = {}

    for template_label, cell_value in values.items():
        row_attr_name = _TEMPLATE_V3_TABLE_LABEL_TO_ROW_V3_ATTR_NAME.get(template_label)

        if row_attr_name is None:
            raise KeyError(f"Unmapped version 3 BOM template table title label encountered: {template_label!r}")

        if row_attr_name in row_kwargs:
            raise ValueError(f"Duplicate row attribute mapping detected for attribute '{row_attr_name}'.")

        row_kwargs[row_attr_name] = cell_value

    return RowV3(**row_kwargs)
