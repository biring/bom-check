"""
Canonical data models for BOM processing.

This module defines immutable, normalized dataclasses representing the final canonical form of BOM data after parsing, validation, and approval. These models serve as the strict data contract consumed by exporters and downstream systems.

The canonical layer assumes all structural, semantic, and cost validations have already been enforced upstream.

Example Usage:
    # Preferred usage via package interface:
    # Not applicable; this module is internal.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.models import _canonical_models as cm
    bom = cm.CanonicalBom(boards=(board,), is_cost_bom=True)

Dependencies:
    - Python >= 3.10
    - Standard Library: dataclasses, datetime

Notes:
    - All models are frozen dataclasses to guarantee immutability and traceability.
    - Canonical models must not perform parsing, coercion, or validation logic.
    - Designed to be serialization-ready for exporters.

License:
    - Internal Use Only
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
        manufacturer (str): Manufacturer name.
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
    manufacturer: str
    mfg_part_number: str
    ul_vde_number: str
    validated_at: tuple[str, ...]
    unit_price: float


@dataclass(frozen=True)
class CanonicalPart:
    """
    Canonical representation of a BOM line item with primary and alternate component options.

    Args:
        item (int): BOM line item number.
        designators (tuple[str, ...]): Reference designators for placement (e.g., ("R1", "R2")).
        qty (float): Quantity per board.
        unit (str): Unit of measure (e.g., "pcs").
        classification (str): Classification code (e.g., "A", "B", "C").
        primary_component (CanonicalComponent): Selected primary component.
        alternate_components (tuple[Component, ...]): Approved alternates.
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


@dataclass(frozen=True)
class CanonicalHeader:
    """
    Canonical board-level metadata for a Version 3 BOM.

    Args:
        model_no (str): Product model number.
        board_name (str): Board name (e.g., "MAIN-PCB-A").
        manufacturer (str): Board supplier/manufacturer.
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
    manufacturer: str
    build_stage: str
    date: datetime
    material_cost: float
    overhead_cost: float
    total_cost: float


@dataclass(frozen=True)
class CanonicalBoard:
    """
    Canonical BOM for a single board, containing header metadata and line items.

    Args:
        header (CanonicalHeader): Board metadata.
        parts (tuple[Part, ...]): BOM line items for the board.

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
        boards (tuple[Board, ...]): Parsed board BOMs extracted from the file.
        is_cost_bom (bool): True when the BOM includes cost fields that are intended to be used; defaults to True.

    Returns:
        None: Dataclass container.
    """
    boards: tuple[CanonicalBoard, ...]
    is_cost_bom: bool = True
