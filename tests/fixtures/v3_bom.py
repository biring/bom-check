"""
Typed fixtures for V3 BOM models (Row, Header, Board, Bom).

Provides small, realistic objects for smoke tests and parser/validator checks.

Example Usage:
    # Preferred within tests:
    from tests.fixtures import v3_bom as fx
    assert fx.BOARD_A.header.model_no == "AB100"

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Project: src.models.interfaces (Row, Header, Board, Bom)

Notes:
    - Constants are Final[...] and should not be mutated.
    - Values are representative and stable to keep tests deterministic.
    - Keep names and shapes aligned with the V3 template and model fields.

License:
    - Internal Use Only
"""

from typing import Final
from src.models.interfaces import RowV3, HeaderV3, BoardV3, BomV3

# =============================
# Bom A
# Board 1 with 3 valid rows plus alternatives and unused items
# =============================
ROW_A_1: Final[RowV3] = RowV3(
    item="1", component_type="Resistor", device_package="0603",
    description="2k,1%,0603", units="PCS", classification="A",
    mfg_name="Delta", mfg_part_number="RES002K0A0603", ul_vde_number="UL569",
    validated_at="EB0", qty="2", designators="R1,R2", unit_price="0.1", sub_total="0.2"
)

ROW_A_1_ALT1: Final[RowV3] = RowV3(
    item="", component_type="ALT1", device_package="0603",
    description="2k,1%,0603", units="PCS", classification="A",
    mfg_name="Yageo", mfg_part_number="RC0603FR-072KL", ul_vde_number="UL123",
    validated_at="EB0", qty="0", designators="R1,R2", unit_price="0.09", sub_total="0.0"
)

ROW_A_1_ALT2: Final[RowV3] = RowV3(
    item="", component_type="ALT2", device_package="0603",
    description="2k,1%,0603", units="PCS", classification="A",
    mfg_name="Vishay", mfg_part_number="CRCW06032K00FKEAC", ul_vde_number="UL124",
    validated_at="EB0/EB1", qty="0", designators="R1,R2", unit_price="0.11", sub_total="0.0"
)

ROW_A_2: Final[RowV3] = RowV3(
    item="2", component_type="Capacitor", device_package="0805",
    description="10uF,10%,50V,0805", units="PCS", classification="B", mfg_name="Sigma",
    mfg_part_number="CC106050100805", ul_vde_number="UL102", validated_at="P1/MP",
    qty="3", designators="C1,C2,C3", unit_price="0.2", sub_total="0.6"
)

ROW_A_2_ALT: Final[RowV3] = RowV3(
    item="", component_type="ALT", device_package="0805",
    description="10uF,20%,25V,0805", units="PCS", classification="B",
    mfg_name="Murata", mfg_part_number="GRM21BR61C106KE15L", ul_vde_number="UL202",
    validated_at="MP", qty="0", designators="C1,C2,C3", unit_price="0.25", sub_total="0.0"
)

ROW_A_3: Final[RowV3] = RowV3(
    item="3", component_type="Relay", device_package="SPST-4",
    description="Relay,250VAC,5A,12V,100mA", units="PCS", classification="A",
    mfg_name="Panasonic", mfg_part_number="REL2505-12100", ul_vde_number="UL000",
    validated_at="MP", qty="0", designators="RL1", unit_price="0.5", sub_total="0.0"
)

ROW_A_4: Final[RowV3] = RowV3(
    item="4", component_type="IC", device_package="QFN-8",
    description="Op-Amp,10MHz,RRIO,5V,1mA", units="PCS", classification="A", mfg_name="Gamma",
    mfg_part_number="LM335", ul_vde_number="VDE1123", validated_at="MP",
    qty="1", designators="U1", unit_price="1.2", sub_total="1.2"
)

HEADER_A: Final[HeaderV3] = HeaderV3(
    model_no="AB100", board_name="Power PCBA", board_supplier="Delta",
    build_stage="MB", bom_date="2025-01-12", material_cost="2.0",
    overhead_cost="0.4", total_cost="2.4"
)

BOARD_A: Final[BoardV3] = BoardV3(
    header=HEADER_A,
    rows=(ROW_A_1, ROW_A_1_ALT1, ROW_A_1_ALT2, ROW_A_2, ROW_A_2_ALT, ROW_A_3, ROW_A_4),
    sheet_name=HEADER_A.board_name,
)

BOM_A: Final[BomV3] = BomV3(
    boards=(BOARD_A,),
    file_name="bom_A.xlsx",
)

# =============================
# Bom A - BAD FORMATTING
# Board 1 with 3 valid rows plus alternatives and unused items
# Field values contain "\t" which is not allowed and should be fixed automatically by cleaner module)
# =============================
ROW_A_1_BAD_FORMATTING: Final[RowV3] = RowV3(
    item="\t1", component_type="\tResistor", device_package="\t0603",
    description="\t2k,1%,0603", units="\tPCS", classification="\tA",
    mfg_name="\tDelta", mfg_part_number="\tRES002K0A0603", ul_vde_number="\tUL569",
    validated_at="\tEB0", qty="\t2", designators="\tR1,R2", unit_price="\t0.1", sub_total="\t0.2"
)

HEADER_A_BAD_FORMATTING: Final[HeaderV3] = HeaderV3(
    model_no="\tAB100", board_name="\tPower PCBA", board_supplier="\tDelta",
    build_stage="\tMB", bom_date="\t2025-01-12", material_cost="\t2.0",
    overhead_cost="\t0.4", total_cost="\t2.4"
)

BOARD_A_BAD_FORMATTING: Final[BoardV3] = BoardV3(
    header=HEADER_A_BAD_FORMATTING,
    rows=(ROW_A_1_BAD_FORMATTING, ROW_A_1_ALT1, ROW_A_1_ALT2, ROW_A_2, ROW_A_2_ALT, ROW_A_3, ROW_A_4),
    sheet_name=HEADER_A_BAD_FORMATTING.board_name,
)

BOM_A_BAD_FORMATTING: Final[BomV3] = BomV3(
    boards=(BOARD_A_BAD_FORMATTING,),
    file_name="bom_A_bad_formatting.xlsx",
)

# =============================
# Bom A - BAD MATH
# Board 1 with 3 valid rows plus alternatives and unused items
# Math is incorrect and should be fixed automatically by the fixer module
# =============================
ROW_A_1_BAD_MATH: Final[RowV3] = RowV3(
    item="1", component_type="Resistor", device_package="0603",
    description="2k,1%,0603", units="PCS", classification="A",
    mfg_name="Delta", mfg_part_number="RES002K0A0603", ul_vde_number="UL569",
    validated_at="EB0", qty="2", designators="R1,R2", unit_price="0.1", sub_total="0.4"
)  # sub_total is incorrect

HEADER_A_BAD_MATH: Final[HeaderV3] = HeaderV3(
    model_no="AB100", board_name="Power PCBA", board_supplier="Delta",
    build_stage="MB", bom_date="2025-01-12", material_cost="2.5",
    overhead_cost="0.4", total_cost="9.4"
)  # material_cost and total_cost is incorrect

BOARD_A_BAD_MATH: Final[BoardV3] = BoardV3(
    header=HEADER_A_BAD_MATH,
    rows=(ROW_A_1_BAD_MATH, ROW_A_1_ALT1, ROW_A_1_ALT2, ROW_A_2, ROW_A_2_ALT, ROW_A_3, ROW_A_4),
    sheet_name=HEADER_A_BAD_MATH.board_name,
)

BOM_A_BAD_MATH: Final[BomV3] = BomV3(
    boards=(BOARD_A_BAD_MATH,),
    file_name="bom_A_bad_math.xlsx",
)

# =============================
# Bom A - BAD VALUE
# Board 1 with 3 valid rows plus alternatives and unused items
# Values are not correct and would require manual overwrite by the fixer module.
# =============================
ROW_A_1_BAD_VALUE: Final[RowV3] = RowV3(
    item="#1", component_type="#Resistor", device_package="#0603",
    description="#2k,1%,0603", units="#PCS", classification="#A",
    mfg_name="#Delta", mfg_part_number="#RES002K0A0603", ul_vde_number="#UL569",
    validated_at="#EB0", qty="#2", designators="#R1,R2", unit_price="#0.1", sub_total="#0.4"
)  # added "#" to all values in this row so will require manual overwrite

HEADER_A_BAD_VALUE: Final[HeaderV3] = HeaderV3(
    model_no="#AB100", board_name="#Power PCBA", board_supplier="#Delta",
    build_stage="#MB", bom_date="#2025-01-12", material_cost="#2.5",
    overhead_cost="#0.4", total_cost="#9.4"
)  # added "#" to all values in this header so will require manual overwrite

BOARD_A_BAD_VALUE: Final[BoardV3] = BoardV3(
    header=HEADER_A_BAD_VALUE,
    rows=(ROW_A_1_BAD_VALUE, ROW_A_1_ALT1, ROW_A_1_ALT2, ROW_A_2, ROW_A_2_ALT, ROW_A_3, ROW_A_4),
    sheet_name=HEADER_A_BAD_VALUE.board_name,
)

BOM_A_BAD_VALUE: Final[BomV3] = BomV3(
    boards=(BOARD_A_BAD_VALUE,),
    file_name="bom_A_bad_value.xlsx",
    is_cost_bom=True,
)

# =============================
# Bom B
# Board 1 with 4 rows. No alternatives or unused rows
# Board 2 with 6 rows. No alternatives or unused rows
# =============================
ROW_B1_1: Final[RowV3] = RowV3(
    item="1", component_type="Resistor", device_package="0402",
    description="1k,5%,0402", units="PCS", classification="A",
    mfg_name="Ohmite", mfg_part_number="RES001K0A0402", ul_vde_number="UL100",
    validated_at="P1", qty="4", designators="R1,R2,R3,R4", unit_price="0.05", sub_total="0.2"
)

ROW_B1_2: Final[RowV3] = RowV3(
    item="2", component_type="Capacitor", device_package="0603",
    description="47nF,10%,50V,0603", units="PCS", classification="B",
    mfg_name="TDK", mfg_part_number="C0603X7R50047", ul_vde_number="UL200",
    validated_at="P1", qty="2", designators="C1,C2", unit_price="0.08", sub_total="0.16"
)

ROW_B1_3: Final[RowV3] = RowV3(
    item="3", component_type="Inductor", device_package="0805",
    description="10uH,20%,0805", units="PCS", classification="B",
    mfg_name="Coilcraft", mfg_part_number="L080510UH", ul_vde_number="UL300",
    validated_at="P1", qty="1", designators="L1", unit_price="0.3", sub_total="0.3"
)

ROW_B1_4: Final[RowV3] = RowV3(
    item="4", component_type="IC", device_package="SOIC-8",
    description="LDO,5V,1A", units="PCS", classification="A",
    mfg_name="Texas Instruments", mfg_part_number="LM7805SOIC", ul_vde_number="VDE500",
    validated_at="P1", qty="1", designators="U1", unit_price="0.5", sub_total="0.5"
)

HEADER_B1: Final[HeaderV3] = HeaderV3(
    model_no="BB200", board_name="Control PCBA", board_supplier="Ohmite",
    build_stage="P1", bom_date="2025-02-10",
    material_cost="1.16", overhead_cost="0.24", total_cost="1.4"
)

BOARD_B1: Final[BoardV3] = BoardV3(
    header=HEADER_B1,
    rows=(ROW_B1_1, ROW_B1_2, ROW_B1_3, ROW_B1_4),
    sheet_name=HEADER_B1.board_name,
)

ROW_B2_1: Final[RowV3] = RowV3(
    item="1", component_type="Resistor", device_package="0603",
    description="4.7k,1%,0603", units="PCS", classification="A",
    mfg_name="Yageo", mfg_part_number="RC0603FR-074K7L", ul_vde_number="UL101",
    validated_at="MP", qty="6", designators="R5,R6,R7,R8,R9,R10", unit_price="0.02", sub_total="0.12"
)

ROW_B2_2: Final[RowV3] = RowV3(
    item="2", component_type="Capacitor", device_package="0805",
    description="1uF,10%,25V,0805", units="PCS", classification="B",
    mfg_name="Murata", mfg_part_number="GRM21BR71C105KA01L", ul_vde_number="UL202",
    validated_at="MP", qty="4", designators="C3,C4,C5,C6", unit_price="0.05", sub_total="0.2"
)

ROW_B2_3: Final[RowV3] = RowV3(
    item="3", component_type="Diode", device_package="SMA",
    description="Schottky,1A,40V", units="PCS", classification="A",
    mfg_name="OnSemi", mfg_part_number="SS14", ul_vde_number="UL303",
    validated_at="MP", qty="2", designators="D1,D2", unit_price="0.15", sub_total="0.3"
)

ROW_B2_4: Final[RowV3] = RowV3(
    item="4", component_type="Connector", device_package="2x5",
    description="Header,10-pin,2.54mm", units="PCS", classification="C",
    mfg_name="Samtec", mfg_part_number="FTSH-105-01", ul_vde_number="UL404",
    validated_at="MP", qty="1", designators="J1", unit_price="0.25", sub_total="0.25"
)

ROW_B2_5: Final[RowV3] = RowV3(
    item="5", component_type="MCU", device_package="QFP-32",
    description="ARM,Cortex-M0,32-bit,32-pin", units="PCS", classification="A",
    mfg_name="STMicro", mfg_part_number="STM32F030K6T6", ul_vde_number="VDE789",
    validated_at="MP", qty="1", designators="U2", unit_price="1.5", sub_total="1.5"
)

ROW_B2_6: Final[RowV3] = RowV3(
    item="6", component_type="Crystal", device_package="HC-49S",
    description="16MHz,±20ppm", units="PCS", classification="B",
    mfg_name="Epson", mfg_part_number="Q16.000MHZHC49", ul_vde_number="UL505",
    validated_at="MP", qty="1", designators="Y1", unit_price="0.1", sub_total="0.1"
)

HEADER_B2: Final[HeaderV3] = HeaderV3(
    model_no="BB300", board_name="Interface PCBA", board_supplier="Murata",
    build_stage="MP", bom_date="2025-03-05",
    material_cost="2.47", overhead_cost="0.53", total_cost="3.0"
)

BOARD_B2: Final[BoardV3] = BoardV3(
    header=HEADER_B2,
    rows=(ROW_B2_1, ROW_B2_2, ROW_B2_3, ROW_B2_4, ROW_B2_5, ROW_B2_6),
    sheet_name=HEADER_B2.board_name,
)

BOM_B: Final[BomV3] = BomV3(
    boards=(BOARD_B1, BOARD_B2),
    file_name="bom_b.xlsx",
    is_cost_bom=True,
)
