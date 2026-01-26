"""
Canonical data models for BOM processing.

This module defines immutable, normalized data structures representing the final canonical form of bill of materials data after parsing, validation, and approval. These models act as a strict data contract consumed by exporters and downstream systems and assume that all structural, semantic, and cost validation has already been enforced upstream.

Key responsibilities
	- Represent approved bill of materials data in an immutable and normalized form
	- Provide canonical structures for components, parts, boards, and complete bills of materials
	- Serve as a stable data contract for downstream exporters and integrations
	- Centralize refactor-safe attribute name constants for mapping and adapter layers

Example usage
	Preferred usage via public package interface
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	Direct module usage (acceptable in unit tests or internal scripts only)
	from src.models import _canonical as canonical
	bom = canonical.CanonicalBom(boards=(board,), is_cost_bom=True)

Dependencies
	- Python 3.10
	- Standard Library: dataclasses, datetime

Notes
	- All data models are frozen to guarantee immutability and traceability
	- No parsing, coercion, or validation logic is performed in this layer
	- Intended to be serialization-ready for exporters and downstream consumers

License
	Internal Use Only
"""

__all__ = []  # Internal-only; canonical models are not part of the public API.

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CanonicalComponent:
    """
    Canonical representation of a physical component option for a BOM line.

    Args:
        component_type (str): Component type (e.g., resistor, capacitor).
        device_package (str): Package name (e.g., 0402, SOT-23).
        description (str): Component description.
        mfg_name (str): Manufacturer name.
        mfg_part_number (str): Manufacturer part number.
        ul_vde_number (str): Safety certification identifier, if applicable.
        validated_at (tuple[str, ...]): Build identifiers where this component is approved (e.g., ("EB0", "MP")).
        unit_price (float): Unit price in RMB (VAT included).

    Returns:
        None: Dataclass container.
    """
    component_type: str
    device_package: str
    description: str
    mfg_name: str
    mfg_part_number: str
    ul_vde_number: str
    validated_at: tuple[str, ...]
    unit_price: float


class CanonicalComponentAttrNames:
    """
    Attribute name constants for CanonicalComponent-related fields.

    These constants provide a refactor-safe contract for adapter or mapping modules that need to reference canonical field names without duplicating string literals.
    """

    COMPONENT_TYPE = "component_type"
    DEVICE_PACKAGE = "device_package"
    DESCRIPTION = "description"
    MFG_NAME = "mfg_name"
    MFG_PART_NO = "mfg_part_number"
    UL_VDE_NUMBER = "ul_vde_number"
    VALIDATED_AT = "validated_at"
    UNIT_PRICE = "unit_price"


@dataclass(frozen=True)
class CanonicalPart:
    """
    Canonical representation of a BOM line item with primary and alternate component options.

    Source-to-canonical convention: The transformer maps the first component option to primary_component and remaining options to alternate_components.

    Args:
        item (int): BOM line item number.
        designators (tuple[str, ...]): Reference designators for placement (e.g., ("R1", "R2")).
        qty (float): Quantity per board.
        unit (str): Unit of measure (e.g., "pcs").
        classification (str): Classification code (e.g., "A", "B", "C").
        primary_component (CanonicalComponent): Selected primary component.
        alternate_components (tuple[CanonicalComponent, ...]): Approved alternates.
        sub_total (float): Extended cost in RMB (VAT included), typically qty * unit_price.

    Returns:
        None: Dataclass container.
    """
    item: int
    designators: tuple[str, ...]
    qty: float
    unit: str
    classification: str
    primary_component: CanonicalComponent
    alternate_components: tuple[CanonicalComponent, ...]
    sub_total: float


class CanonicalPartAttrNames:
    """
    Attribute name constants for CanonicalPart fields.

    These constants provide a refactor-safe contract for adapter or mapping modules that need to reference canonical field names without duplicating string literals.
    """

    ITEM = "item"
    DESIGNATORS = "designators"
    QTY = "qty"
    UNITS = "unit"
    CLASSIFICATION = "classification"
    PRIMARY_COMPONENT = "primary_component"
    ALTERNATE_COMPONENTS = "alternate_components"
    SUB_TOTAL = "sub_total"


@dataclass(frozen=True)
class CanonicalHeader:
    """
    Canonical board-level metadata for a Version 3 BOM.

    Args:
        model_no (str): Product model number.
        board_name (str): Board name (e.g., "MAIN-PCB-A").
        board_supplier (str): Board supplier.
        build_stage (str): Build stage identifier (e.g., "EB0", "MP").
        date (datetime): BOM release or creation date.
        material_cost (float): Material cost in RMB.
        overhead_cost (float): Overhead/handling cost in RMB.
        total_cost (float): Total cost in RMB.

    Returns:
        None: Dataclass container.
    """
    model_no: str
    board_name: str
    board_supplier: str
    build_stage: str
    date: datetime
    material_cost: float
    overhead_cost: float
    total_cost: float


class CanonicalHeaderAttrNames:
    """
    Attribute name constants for CanonicalHeader fields.

    These constants provide a refactor-safe contract for adapter or mapping modules that need to reference canonical field names without duplicating string literals.
    """

    MODEL_NUMBER = "model_no"
    BOARD_NAME = "board_name"
    BOARD_SUPPLIER = "board_supplier"
    BUILD_STAGE = "build_stage"
    BOM_DATE = "date"
    MATERIAL_COST = "material_cost"
    OVERHEAD_COST = "overhead_cost"
    TOTAL_COST = "total_cost"


@dataclass(frozen=True)
class CanonicalBoard:
    """
    Canonical BOM for a single board, containing header metadata and line items.

    Args:
        header (CanonicalHeader): Board metadata.
        parts (tuple[CanonicalPart, ...]): BOM line items for the board.

    Returns:
        None: Dataclass container.
    """
    header: CanonicalHeader
    parts: tuple[CanonicalPart, ...]


@dataclass(frozen=True)
class CanonicalBom:
    """
    Canonical top-level model for a Version 3 BOM file.

    Args:
        boards (tuple[CanonicalBoard, ...]): Parsed board BOMs extracted from the file.
        is_cost_bom (bool): True when the BOM includes cost fields that are intended to be used; defaults to True.

    Returns:
        None: Dataclass container.
    """
    boards: tuple[CanonicalBoard, ...]
    is_cost_bom: bool = True
