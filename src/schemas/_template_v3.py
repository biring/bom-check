"""
Schema definitions for the version 3 Excel BOM template.

This module defines immutable string labels and identifier collections used to recognize, classify, and validate a specific version of an Excel-based bill of materials template. It contains no parsing, validation execution, or file I/O behavior and exists solely as a declarative description of the expected template structure.

Key responsibilities
	- Define canonical header label strings expected in the template metadata section.
	- Define canonical table column label strings expected in the BOM item rows.
	- Provide minimal identifier sets used to detect and distinguish the template version.
	- Expose the template major version identifier as a constant.

Example usage
	Preferred usage via public package interface
	Not Applicable. This is an internal module.

	Direct module usage (acceptable in unit tests or internal scripts only)
	from src.schemas import _template_v3 as template
	required_labels = template.TEMPLATE_IDENTIFIERS

Dependencies
	- Python 3.10
	- Standard Library: typing

Notes
	- This module is schema-only and intentionally side-effect free.
	- All defined string values must exactly match the labels present in the corresponding Excel template.
	- The module is internal and not intended for direct use by external callers.

License
	Internal Use Only
"""

__all__ = []  # Explicitly prevents star-import from exposing any symbols; internal module only.


class HeaderLabelsV3:
    """
    String constants for header labels in the version 3 BOM Excel template.

    Each class attribute value must exactly match the corresponding label text used in the Excel header section.
    """
    MODEL_NO = "Model No:"  # Product model identifier
    BUILD_STAGE = "Rev:"  # Build stage or revision (e.g., EB0, MP)
    BOARD_NAME = "Description:"  # Board or BOM description
    BOARD_SUPPLIER = "Manufacturer:"  # Board supplier or manufacturer name
    BOM_DATE = "Date:"  # BOM creation or approval date
    MATERIAL_COST = "Material"  # Material cost subtotal
    OVERHEAD_COST = "OHP"  # Overhead or handling cost
    TOTAL_COST = "Total"  # Total cost (material + overhead)

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """
        Return all header label strings defined on the class.

        Returns:
            tuple[str, ...]: Header label strings.
        """
        return tuple(
            value
            for name, value in vars(cls).items()
            if not name.startswith("__")
            and isinstance(value, str)
            and not callable(value)
        )


class TableLabelsV3:
    """
    String constants for component table labels rows in the version 3 BOM sheets.

    Each class attribute represents a label found in the title row of the BOM table of the version 3 BOM Excel template. Attribute values must exactly match the label strings used in the template.
    """
    ITEM = "Item"  # Line number in the BOM
    COMPONENT_TYPE = "Component"  # Component name or ID
    DEVICE_PACKAGE = "Device Package"  # Physical package type (e.g., QFN-8)
    DESCRIPTION = "Description"  # Part description
    UNITS = "Unit"  # Unit of measure (e.g., pcs)
    CLASSIFICATION = "Classification"  # Component class (e.g., A, B, C)
    MFG_NAME = "Manufacturer"  # Part manufacturer
    MFG_PART_NO = "Manufacturer P/N"  # Manufacturer part number
    UL_VDE_NO = "UL/VDE Number"  # Certification reference (if applicable)
    VALIDATED_AT = "Validated at"  # Validation build stage
    QUANTITY = "Qty"  # Quantity used
    DESIGNATORS = "Designator"  # Reference designators (e.g., R1, C4)
    UNIT_PRICE = "U/P (RMB W/ VAT)"  # Unit price (incl. VAT) in RMB
    SUB_TOTAL = "Sub-Total (RMB W/ VAT)"  # Line subtotal cost

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """
        Return all table label strings defined on the class.

        Returns:
            tuple[str, ...]: Table label strings.
        """
        return tuple(
            value
            for name, value in vars(cls).items()
            if not name.startswith("__")
            and isinstance(value, str)
            and not callable(value)
        )


### CONSTANTS ###
# BOM Excel template version identifier; must match the expected template major version.
TEMPLATE_VERSION_V3: str = "3"

# Minimum set of table header labels required to uniquely identify a version 3 BOM table title row.
TABLE_TITLE_ROW_IDENTIFIERS_V3: tuple[str, ...] = (
    TableLabelsV3.DESIGNATORS,
    TableLabelsV3.MFG_NAME,
    TableLabelsV3.MFG_PART_NO,
    TableLabelsV3.QUANTITY,
    TableLabelsV3.COMPONENT_TYPE,  # Required to disambiguate the version 3 BOM table from earlier template versions.
    TableLabelsV3.CLASSIFICATION,  # Required to disambiguate the version 3 BOM table from earlier template versions.
)

# Minimum set of combined header and table labels required to detect a version 3 BOM template.
TEMPLATE_IDENTIFIERS_V3: tuple[str, ...] = (
    HeaderLabelsV3.MODEL_NO,
    HeaderLabelsV3.BUILD_STAGE,
    TableLabelsV3.COMPONENT_TYPE,
    TableLabelsV3.DESIGNATORS,
    TableLabelsV3.CLASSIFICATION,
    TableLabelsV3.MFG_NAME,
    TableLabelsV3.MFG_PART_NO,
    TableLabelsV3.DEVICE_PACKAGE,
    TableLabelsV3.QUANTITY,
)
