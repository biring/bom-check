"""
Adapter module mapping canonical model data to a Version 3 Excel BOM template.

This module provides strict, one-way transformations from canonical header, part, and component attribute identifiers into the exact label schema required by the Version 3 BOM Excel template. It enforces structural correctness by validating input mappings for completeness and exclusivity, preserving a deterministic output order aligned with the template specification, and rejecting ambiguous or duplicate mappings to ensure safe downstream export.

Key responsibilities
	- Validate that provided canonical data structures are dictionaries with exactly the expected attribute keys.
	- Enforce strict one-to-one mappings between canonical attributes and Version 3 template header labels.
	- Enforce strict one-to-one mappings between canonical part and component attributes and Version 3 table row labels.
	- Preserve template-defined ordering of header and table fields in the generated output mappings.
	- Detect and fail fast on missing, extra, or duplicate attribute mappings to prevent invalid BOM exports.

Example usage
	# Preferred usage via public package interface
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from src.adapters import _canonical_to_template_v3 as adapter
	template_header = adapter.map_canonical_header_to_template_v3_header(canonical_header_values)
	template_row = adapter.map_canonical_to_template_v3_table(canonical_row_values)

Dependencies
	- Python 3.x
	- Standard Library: typing

Notes
	- This module assumes canonical input data is already normalized and type-correct before mapping.
	- All mappings are intentionally one-way and exact; partial or flexible mappings are explicitly rejected.
	- Output dictionaries are ordered to match the Version 3 Excel template layout and should not be reordered by callers.
	- Intended strictly for internal adapter-layer use within the BOM export pipeline.

License
	Internal Use Only
"""

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

from src.models.interfaces import (
    CanonicalHeaderAttrNames,
    CanonicalPartAttrNames,
    CanonicalComponentAttrNames,
)

# Exact one-way mapping from canonical header attribute identifiers to Version 3 template header labels.
_CANON_HEADER_ATTR_NAME_TO_TEMPLATE_V3_HEADER_LABEL: dict[str, str] = {
    CanonicalHeaderAttrNames.MODEL_NUMBER: HeaderLabelsV3.MODEL_NO,
    CanonicalHeaderAttrNames.BOARD_NAME: HeaderLabelsV3.BOARD_NAME,
    CanonicalHeaderAttrNames.BOARD_SUPPLIER: HeaderLabelsV3.BOARD_SUPPLIER,
    CanonicalHeaderAttrNames.BUILD_STAGE: HeaderLabelsV3.BUILD_STAGE,
    CanonicalHeaderAttrNames.BOM_DATE: HeaderLabelsV3.BOM_DATE,
    CanonicalHeaderAttrNames.MATERIAL_COST: HeaderLabelsV3.MATERIAL_COST,
    CanonicalHeaderAttrNames.OVERHEAD_COST: HeaderLabelsV3.OVERHEAD_COST,
    CanonicalHeaderAttrNames.TOTAL_COST: HeaderLabelsV3.TOTAL_COST,
}

# Exact one-way mapping from canonical part/component attribute identifiers to Version 3 template table row labels.
_CANON_TABLE_ATTR_NAME_TO_TEMPLATE_V3_ROW_LABEL: dict[str, str] = {
    CanonicalPartAttrNames.ITEM: TableLabelsV3.ITEM,
    CanonicalComponentAttrNames.COMPONENT_TYPE: TableLabelsV3.COMPONENT_TYPE,
    CanonicalComponentAttrNames.DEVICE_PACKAGE: TableLabelsV3.DEVICE_PACKAGE,
    CanonicalComponentAttrNames.DESCRIPTION: TableLabelsV3.DESCRIPTION,
    CanonicalPartAttrNames.UNITS: TableLabelsV3.UNITS,
    CanonicalPartAttrNames.CLASSIFICATION: TableLabelsV3.CLASSIFICATION,
    CanonicalComponentAttrNames.MFG_NAME: TableLabelsV3.MFG_NAME,
    CanonicalComponentAttrNames.MFG_PART_NO: TableLabelsV3.MFG_PART_NO,
    CanonicalComponentAttrNames.UL_VDE_NUMBER: TableLabelsV3.UL_VDE_NO,
    CanonicalComponentAttrNames.VALIDATED_AT: TableLabelsV3.VALIDATED_AT,
    CanonicalPartAttrNames.QTY: TableLabelsV3.QUANTITY,
    CanonicalPartAttrNames.DESIGNATORS: TableLabelsV3.DESIGNATORS,
    CanonicalComponentAttrNames.UNIT_PRICE: TableLabelsV3.UNIT_PRICE,
    CanonicalPartAttrNames.SUB_TOTAL: TableLabelsV3.SUB_TOTAL,
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
    value_keys = set(values.keys())

    extra = value_keys - allowed_keys
    if extra:
        raise KeyError(f"Unexpected {context} labels encountered: {sorted(extra)!r}")

    missing = allowed_keys - value_keys
    if missing:
        raise KeyError(f"Missing required {context} labels: {sorted(missing)!r}")


def map_canonical_to_template_v3_header(values: dict[str, str]) -> dict[str, str]:
    """
    Map canonical header values to a Version 3 template header object.

    Args:
        values (dict[str, str]): Mapping of canonical header attribute names to cell values.

    Returns:
        dict[str, str]: Mapping of template header labels to cell values.

    Raises:
        TypeError: If values is not a dict.
        KeyError: If required keys are missing or unexpected keys are present.
        ValueError: If duplicate template attribute mappings occur.
    """
    _assert_is_dict(values)

    allowed_keys = set(_CANON_HEADER_ATTR_NAME_TO_TEMPLATE_V3_HEADER_LABEL.keys())

    _assert_no_extra_or_missing_keys(
        values=values,
        allowed_keys=allowed_keys,
        context="canonical header",
    )

    template_header_values: dict[str, str] = {}

    # Preserve output order exactly as defined in the mapping constant.
    for canonical_attr_name, header_attr_name in _CANON_HEADER_ATTR_NAME_TO_TEMPLATE_V3_HEADER_LABEL.items():
        cell_value = values[canonical_attr_name]

        if header_attr_name in template_header_values:
            raise ValueError(f"Duplicate header attribute mapping detected for attribute '{header_attr_name}'.")

        template_header_values[header_attr_name] = cell_value

    return template_header_values


def map_canonical_to_template_v3_table(values: dict[str, str]) -> dict[str, str]:
    """
    Map canonical part and component values to a Version 3 BOM row string dictionary.

    Args:
        values (dict[str, str]): Mapping of canonical part or component attribute names to cell values.

    Returns:
        dict[str, str]: Mapping of template row labels to cell values.

    Raises:
        TypeError: If values is not a dict.
        KeyError: If required keys are missing or unexpected keys are present.
        ValueError: If duplicate row attribute mappings occur.
    """
    _assert_is_dict(values)

    allowed_keys = set(_CANON_TABLE_ATTR_NAME_TO_TEMPLATE_V3_ROW_LABEL.keys())

    _assert_no_extra_or_missing_keys(
        values=values,
        allowed_keys=allowed_keys,
        context="canonical part/component",
    )

    template_row_values: dict[str, str] = {}

    # Preserve output order exactly as defined in the mapping constant.
    for canonical_attr_name, row_attr_name in _CANON_TABLE_ATTR_NAME_TO_TEMPLATE_V3_ROW_LABEL.items():
        cell_value = values[canonical_attr_name]

        if row_attr_name in template_row_values:
            raise ValueError(
                f"Duplicate canonical part/component mapping detected for attribute '{row_attr_name}'."
            )

        template_row_values[row_attr_name] = cell_value

    return template_row_values
