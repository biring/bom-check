"""
Canonical BOM fixtures corresponding to tests.fixtures.v3_bom.

This module defines fully-typed Canonical* objects that represent the expected output of the BOM mapper. Fixtures are used to assert correctness of canonicalization and downstream exporter behavior.

Example Usage:
    # Preferred usage within tests:
    from tests.fixtures import canonical as fx
    assert fx.BOM_A_CANONICAL.is_cost_bom is True

Dependencies:
    - Python >= 3.10
    - Standard Library: datetime, typing
    - Project: src.models.interfaces (CanonicalComponent, CanonicalPart, CanonicalHeader, CanonicalBoard, CanonicalBom)

Notes:
    - All fixtures are declared as Final[...] and must not be mutated.
    - Objects represent post-mapping, fully-normalized canonical state.
    - Naming aligns one-to-one with source fixtures in tests.fixtures.v3_bom.
    - Intended for mapper, exporter, and integration-level tests only.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only test fixtures; star import exports nothing.

from datetime import datetime
from typing import Final

# Adjust this import to your actual canonical model module
from src.models.interfaces import (
    CanonicalComponent,
    CanonicalPart,
    CanonicalHeader,
    CanonicalBoard,
    CanonicalBom,
)

# =============================================================================
# Canonical BOM A (from BOM_A)
# =============================================================================

# ---  CanonicalComponents for BOM_A ---

COMP_A_1_PRIMARY: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Resistor",
    device_package="0603",
    description="2k,1%,0603",
    mfg_name="Delta",
    mfg_part_number="RES002K0A0603",
    ul_vde_number="UL569",
    validated_at=("EB0",),
    unit_price=0.10,
)

COMP_A_1_ALT1: Final[CanonicalComponent] = CanonicalComponent(
    component_type="ALT1",
    device_package="0603",
    description="2k,1%,0603",
    mfg_name="Yageo",
    mfg_part_number="RC0603FR-072KL",
    ul_vde_number="UL123",
    validated_at=("EB0",),
    unit_price=0.09,
)

COMP_A_1_ALT2: Final[CanonicalComponent] = CanonicalComponent(
    component_type="ALT2",
    device_package="0603",
    description="2k,1%,0603",
    mfg_name="Vishay",
    mfg_part_number="CRCW06032K00FKEAC",
    ul_vde_number="UL124",
    validated_at=("EB0", "EB1"),
    unit_price=0.11,
)

COMP_A_2_PRIMARY: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Capacitor",
    device_package="0805",
    description="10uF,10%,50V,0805",
    mfg_name="Sigma",
    mfg_part_number="CC106050100805",
    ul_vde_number="UL102",
    validated_at=("P1", "MP"),
    unit_price=0.20,
)

COMP_A_2_ALT: Final[CanonicalComponent] = CanonicalComponent(
    component_type="ALT",
    device_package="0805",
    description="10uF,20%,25V,0805",
    mfg_name="Murata",
    mfg_part_number="GRM21BR61C106KE15L",
    ul_vde_number="UL202",
    validated_at=("MP",),
    unit_price=0.25,
)

COMP_A_3_PRIMARY: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Relay",
    device_package="SPST-4",
    description="Relay,250VAC,5A,12V,100mA",
    mfg_name="Panasonic",
    mfg_part_number="REL2505-12100",
    ul_vde_number="UL000",
    validated_at=("MP",),
    unit_price=0.50,
)

COMP_A_4_PRIMARY: Final[CanonicalComponent] = CanonicalComponent(
    component_type="IC",
    device_package="QFN-8",
    description="Op-Amp,10MHz,RRIO,5V,1mA",
    mfg_name="Gamma",
    mfg_part_number="LM335",
    ul_vde_number="VDE1123",
    validated_at=("MP",),
    unit_price=1.20,
)

# --- CanonicalParts for BOM_A ---

PART_A_1: Final[CanonicalPart] = CanonicalPart(
    item=1,
    designators=("R1", "R2"),
    qty=2.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_A_1_PRIMARY,
    alternate_components=(COMP_A_1_ALT1, COMP_A_1_ALT2),
    sub_total=0.20,
)

PART_A_2: Final[CanonicalPart] = CanonicalPart(
    item=2,
    designators=("C1", "C2", "C3"),
    qty=3.0,
    unit="PCS",
    classification="B",
    primary_component=COMP_A_2_PRIMARY,
    alternate_components=(COMP_A_2_ALT,),
    sub_total=0.60,
)

PART_A_3: Final[CanonicalPart] = CanonicalPart(
    item=3,
    designators=("RL1",),
    qty=0.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_A_3_PRIMARY,
    alternate_components=(),
    sub_total=0.0,
)

PART_A_4: Final[CanonicalPart] = CanonicalPart(
    item=4,
    designators=("U1",),
    qty=1.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_A_4_PRIMARY,
    alternate_components=(),
    sub_total=1.20,
)

# --- CanonicalHeader, CanonicalBoard, CanonicalBom for BOM_A ---

HEADER_A_CANONICAL: Final[CanonicalHeader] = CanonicalHeader(
    model_no="AB100",
    board_name="Power PCBA",
    board_supplier="Delta",
    build_stage="MB",
    date=datetime(2025, 1, 12),
    material_cost=2.0,
    overhead_cost=0.4,
    total_cost=2.4,
)

BOARD_A_CANONICAL: Final[CanonicalBoard] = CanonicalBoard(
    header=HEADER_A_CANONICAL,
    parts=(PART_A_1, PART_A_2, PART_A_3, PART_A_4),
)

BOM_A_CANONICAL: Final[CanonicalBom] = CanonicalBom(
    boards=(BOARD_A_CANONICAL,),
    is_cost_bom=True,
)

# =============================================================================
# Canonical BOM B (from BOM_B)
# =============================================================================

# ---  CanonicalComponents for BOARD_B1 ---

COMP_B1_1: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Resistor",
    device_package="0402",
    description="1k,5%,0402",
    mfg_name="Ohmite",
    mfg_part_number="RES001K0A0402",
    ul_vde_number="UL100",
    validated_at=("P1",),
    unit_price=0.05,
)

COMP_B1_2: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Capacitor",
    device_package="0603",
    description="47nF,10%,50V,0603",
    mfg_name="TDK",
    mfg_part_number="C0603X7R50047",
    ul_vde_number="UL200",
    validated_at=("P1",),
    unit_price=0.08,
)

COMP_B1_3: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Inductor",
    device_package="0805",
    description="10uH,20%,0805",
    mfg_name="Coilcraft",
    mfg_part_number="L080510UH",
    ul_vde_number="UL300",
    validated_at=("P1",),
    unit_price=0.30,
)

COMP_B1_4: Final[CanonicalComponent] = CanonicalComponent(
    component_type="IC",
    device_package="SOIC-8",
    description="LDO,5V,1A",
    mfg_name="Texas Instruments",
    mfg_part_number="LM7805SOIC",
    ul_vde_number="VDE500",
    validated_at=("P1",),
    unit_price=0.50,
)

# --- CanonicalParts for BOARD_B1 ---

PART_B1_1: Final[CanonicalPart] = CanonicalPart(
    item=1,
    designators=("R1", "R2", "R3", "R4"),
    qty=4.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_B1_1,
    alternate_components=(),
    sub_total=0.20,
)

PART_B1_2: Final[CanonicalPart] = CanonicalPart(
    item=2,
    designators=("C1", "C2"),
    qty=2.0,
    unit="PCS",
    classification="B",
    primary_component=COMP_B1_2,
    alternate_components=(),
    sub_total=0.16,
)

PART_B1_3: Final[CanonicalPart] = CanonicalPart(
    item=3,
    designators=("L1",),
    qty=1.0,
    unit="PCS",
    classification="B",
    primary_component=COMP_B1_3,
    alternate_components=(),
    sub_total=0.30,
)

PART_B1_4: Final[CanonicalPart] = CanonicalPart(
    item=4,
    designators=("U1",),
    qty=1.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_B1_4,
    alternate_components=(),
    sub_total=0.50,
)

HEADER_B1_CANONICAL: Final[CanonicalHeader] = CanonicalHeader(
    model_no="BB200",
    board_name="Control PCBA",
    board_supplier="Ohmite",
    build_stage="P1",
    date=datetime(2025, 2, 10),
    material_cost=1.16,
    overhead_cost=0.24,
    total_cost=1.40,
)

BOARD_B1_CANONICAL: Final[CanonicalBoard] = CanonicalBoard(
    header=HEADER_B1_CANONICAL,
    parts=(PART_B1_1, PART_B1_2, PART_B1_3, PART_B1_4),
)

# ---  CanonicalComponents for BOARD_B2 ---

COMP_B2_1: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Resistor",
    device_package="0603",
    description="4.7k,1%,0603",
    mfg_name="Yageo",
    mfg_part_number="RC0603FR-074K7L",
    ul_vde_number="UL101",
    validated_at=("MP",),
    unit_price=0.02,
)

COMP_B2_2: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Capacitor",
    device_package="0805",
    description="1uF,10%,25V,0805",
    mfg_name="Murata",
    mfg_part_number="GRM21BR71C105KA01L",
    ul_vde_number="UL202",
    validated_at=("MP",),
    unit_price=0.05,
)

COMP_B2_3: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Diode",
    device_package="SMA",
    description="Schottky,1A,40V",
    mfg_name="OnSemi",
    mfg_part_number="SS14",
    ul_vde_number="UL303",
    validated_at=("MP",),
    unit_price=0.15,
)

COMP_B2_4: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Connector",
    device_package="2x5",
    description="Header,10-pin,2.54mm",
    mfg_name="Samtec",
    mfg_part_number="FTSH-105-01",
    ul_vde_number="UL404",
    validated_at=("MP",),
    unit_price=0.25,
)

COMP_B2_5: Final[CanonicalComponent] = CanonicalComponent(
    component_type="MCU",
    device_package="QFP-32",
    description="ARM,Cortex-M0,32-bit,32-pin",
    mfg_name="STMicro",
    mfg_part_number="STM32F030K6T6",
    ul_vde_number="VDE789",
    validated_at=("MP",),
    unit_price=1.50,
)

COMP_B2_6: Final[CanonicalComponent] = CanonicalComponent(
    component_type="Crystal",
    device_package="HC-49S",
    description="16MHz,±20ppm",
    mfg_name="Epson",
    mfg_part_number="Q16.000MHZHC49",
    ul_vde_number="UL505",
    validated_at=("MP",),
    unit_price=0.10,
)

# --- CanonicalParts for BOARD_B2 ---

PART_B2_1: Final[CanonicalPart] = CanonicalPart(
    item=1,
    designators=("R5", "R6", "R7", "R8", "R9", "R10"),
    qty=6.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_B2_1,
    alternate_components=(),
    sub_total=0.12,
)

PART_B2_2: Final[CanonicalPart] = CanonicalPart(
    item=2,
    designators=("C3", "C4", "C5", "C6"),
    qty=4.0,
    unit="PCS",
    classification="B",
    primary_component=COMP_B2_2,
    alternate_components=(),
    sub_total=0.20,
)

PART_B2_3: Final[CanonicalPart] = CanonicalPart(
    item=3,
    designators=("D1", "D2"),
    qty=2.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_B2_3,
    alternate_components=(),
    sub_total=0.30,
)

PART_B2_4: Final[CanonicalPart] = CanonicalPart(
    item=4,
    designators=("J1",),
    qty=1.0,
    unit="PCS",
    classification="C",
    primary_component=COMP_B2_4,
    alternate_components=(),
    sub_total=0.25,
)

PART_B2_5: Final[CanonicalPart] = CanonicalPart(
    item=5,
    designators=("U2",),
    qty=1.0,
    unit="PCS",
    classification="A",
    primary_component=COMP_B2_5,
    alternate_components=(),
    sub_total=1.50,
)

PART_B2_6: Final[CanonicalPart] = CanonicalPart(
    item=6,
    designators=("Y1",),
    qty=1.0,
    unit="PCS",
    classification="B",
    primary_component=COMP_B2_6,
    alternate_components=(),
    sub_total=0.10,
)

HEADER_B2_CANONICAL: Final[CanonicalHeader] = CanonicalHeader(
    model_no="BB300",
    board_name="Interface PCBA",
    board_supplier="Murata",
    build_stage="MP",
    date=datetime(2025, 3, 5),
    material_cost=2.47,
    overhead_cost=0.53,
    total_cost=3.0,
)

BOARD_B2_CANONICAL: Final[CanonicalBoard] = CanonicalBoard(
    header=HEADER_B2_CANONICAL,
    parts=(PART_B2_1, PART_B2_2, PART_B2_3, PART_B2_4, PART_B2_5, PART_B2_6),
)

BOM_B_CANONICAL: Final[CanonicalBom] = CanonicalBom(
    boards=(BOARD_B1_CANONICAL, BOARD_B2_CANONICAL),
    is_cost_bom=True,
)
