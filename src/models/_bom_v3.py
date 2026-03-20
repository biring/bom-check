"""
Raw data model for the version 3 BOM template.

This module defines immutable Python dataclasses that mirror the layout of a version 3 Excel-based Bill of Materials. It captures board-level metadata, component rows, and file-level grouping as represented in the source workbook, with all values stored as plain strings to tolerate missing or partially populated input.

Key Responsibilities:
	- Represent component-level BOM entries using string-based fields
	- Represent board-level metadata and associated component collections
	- Aggregate multiple boards into a single file-level structure
	- Provide immutable, parser-friendly data containers without side effects
	- Provide formatted string output for debugging and inspection

Example usage
	Preferred usage via public package interface
	Not Applicable. This is an internal module.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.models import _bom_v3 as models
	bom = models.BomV3(boards=tuple(), file_name="example.xlsx", is_cost_bom=True)

Dependencies
	- Python 3.10
	- Standard Library: dataclasses

Notes:
	- All data fields default to empty strings to tolerate missing or partial input
	- Data structures are immutable to preserve integrity of parsed input
	- No validation, normalization, or type coercion is performed
	- Attribute name constants provide stable references for mapping layers
	- String formatting utility provides column-aligned debug output

License
	Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

from dataclasses import dataclass

class _BomV3Base:

    def __str__(self) -> str:
        """
        Build a formatted string representation of instance attributes.

        Iterates over the instance __dict__ in insertion order and formats key-value pairs into fixed-width columns.
        Attribute names are normalized to human-readable labels by replacing underscores and applying title case.
        Values exceeding the configured column width are truncated with an ellipsis to preserve alignment.

        Returns:
            str: A formatted multi-line string representing the instance state.
        """
        no_columns = 3  # Fixed number of columns per row; invariant for layout consistency
        column_width = 50  # Hard constraint to enforce column alignment regardless of content variability
        ending_dots = "..."  # Suffix used to indicate truncation; must fit within column_width
        count = 0  # Tracks processed attributes to enforce row breaks deterministically
        print_out = "" # Accumulates the final output string; built incrementally to maintain control over formatting and layout

        # Iterate over instance attributes; relies on dict insertion order for stable output
        for name, value in self.__dict__.items():
            # Normalize attribute name into display label; assumes snake_case input
            label = name.replace("_", " ").title()

            # Construct full display string prior to enforcing width constraints
            label_and_value = f"{label}: {value}"

            # Enforce fixed-width invariant by truncating overly long entries
            if len(label_and_value) > column_width:
                # Ensure truncation leaves space for ellipsis; prevents overflow beyond column boundary
                label_and_value = label_and_value[:column_width - len(ending_dots)] + ending_dots

            # Left-align within column width to maintain grid-like structure across rows
            print_out += f"{label_and_value:<{column_width}}"

            # Insert newline after every N columns to form consistent rows
            if count % no_columns == no_columns - 1:
                print_out += "\n"

            # Increment after processing to maintain correct modulo grouping behavior
            count += 1

        # Remove trailing newline to avoid unintended blank line at output end
        if print_out.endswith("\n"):
            print_out = print_out[:-1]

        return print_out

class RowV3AttrNames:
    """
    Canonical attribute names for RowV3.

    These constants provide a refactor-safe contract for adapter or mapping modules that need to reference RowV3 field names without duplicating string literals.
    """
    ITEM = "item"
    COMPONENT_TYPE = "component_type"
    DEVICE_PACKAGE = "device_package"
    DESCRIPTION = "description"
    UNITS = "units"
    CLASSIFICATION = "classification"
    MFG_NAME = "mfg_name"
    MFG_PART_NO = "mfg_part_number"
    UL_VDE_NO = "ul_vde_number"
    VALIDATED_AT = "validated_at"
    QTY = "qty"
    DESIGNATORS = "designators"
    UNIT_PRICE = "unit_price"
    SUB_TOTAL = "sub_total"


@dataclass(frozen=True)
class RowV3(_BomV3Base):
    """
    Represents a single row in the BOM table.

    All fields are stored as strings and default to the empty string to simplify parsing and tolerate missing or partially populated input.

    Args:
        item (str): Line item number.
        component_type (str): Component type description.
        device_package (str): Package type such as 0402 or SOT-23.
        description (str): Part description.
        units (str): Unit of measure such as pcs.
        classification (str): Part classification code.
        mfg_name (str): Part manufacturer name.
        mfg_part_number (str): Part manufacturer part number.
        ul_vde_number (str): Part UL or VDE safety certification number.
        validated_at (str): Part validation build reference.
        qty (str): Quantity per board.
        designators (str): Reference designators such as R1 or C2.
        unit_price (str): Unit price including VAT.
        sub_total (str): Extended price including VAT.
    """
    item: str = ""
    component_type: str = ""
    device_package: str = ""
    description: str = ""
    units: str = ""
    classification: str = ""
    mfg_name: str = ""
    mfg_part_number: str = ""
    ul_vde_number: str = ""
    validated_at: str = ""
    qty: str = ""
    designators: str = ""
    unit_price: str = ""
    sub_total: str = ""


class HeaderV3AttrNames:
    """
    Canonical attribute names for HeaderV3.

    These constants provide a refactor-safe contract for adapter or mapping modules that need to reference HeaderV3 field names without duplicating string literals.
    """
    MODEL_NO = "model_no"
    BOARD_NAME = "board_name"
    BOARD_SUPPLIER = "board_supplier"
    BUILD_STAGE = "build_stage"
    BOM_DATE = "bom_date"
    MATERIAL_COST = "material_cost"
    OVERHEAD_COST = "overhead_cost"
    TOTAL_COST = "total_cost"


@dataclass(frozen=True)
class HeaderV3(_BomV3Base):
    """
    Represents the header metadata for a single board BOM.

    All fields are stored as strings and default to the empty string to simplify parsing and tolerate missing values.

    Args:
        model_no (str): Product model number.
        board_name (str): Board name such as "Power PCBA".
        board_supplier (str): Board supplier name.
        build_stage (str): Build stage such as EB0 or MP.
        bom_date (str): Date the BOM was created.
        material_cost (str): Total raw material cost.
        overhead_cost (str): Total overhead cost.
        total_cost (str): Combined material and overhead cost.
    """
    model_no: str = ""
    board_name: str = ""
    board_supplier: str = ""
    build_stage: str = ""
    bom_date: str = ""
    material_cost: str = ""
    overhead_cost: str = ""
    total_cost: str = ""


@dataclass(frozen=True)
class BoardV3:
    """
    Represents a BOM for a single board, including header metadata and component rows.

    Args:
        header (HeaderV3): Board-level metadata.
        rows (tuple[RowV3, ...]): Component rows associated with the board.
        sheet_name (str): Name of the Excel sheet from which the board was read.
    """
    header: HeaderV3  # no default, assigned when created
    rows: tuple[RowV3, ...]  # Any length, No default, assigned when created
    sheet_name: str = ""


@dataclass(frozen=True)
class BomV3:
    """
    Top-level model representing a Version 3 BOM file.

    Args:
        boards (tuple[BoardV3, ...]): All board BOMs extracted from the file.
        file_name (str): Original file name of the BOM workbook.
        is_cost_bom (bool): Indicates whether the BOM includes cost data.
    """
    boards: tuple[BoardV3, ...]  # Any length. No default, assigned when created
    file_name: str = ""
    is_cost_bom: bool = True  # Fail-safe default; parser sets False only when confidently detected
