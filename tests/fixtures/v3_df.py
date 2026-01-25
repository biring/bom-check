"""
Fixtures for version 3 dataframe-shaped BOM outputs.

This module defines static, ordered, list-based fixtures that represent the expected spreadsheet-like layout produced when canonical BOM data is rendered into the version 3 output format. The data is structured to mirror final tabular exports, including header sections, table titles, and item rows, enabling deterministic assertions in tests without relying on external dataframe or spreadsheet libraries.

Key responsibilities
	- Define immutable header rows representing document metadata and titles.
	- Provide ordered tabular row data representing primary and alternate BOM line items.
	- Assemble complete board-level and BOM-level structures as nested list and dictionary literals.
	- Support repeatable and deterministic test assertions for version 3 BOM rendering logic.

Example usage
	# Preferred usage via public package interface:
	from tests.fixtures import v3_df
	data = v3_df.BOM_A

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from tests.fixtures import v3_df
	data = v3_df.BOM_A

Dependencies
	- Python 3.x
	- Standard Library: typing

Notes
	- All fixtures are declared as Final and are intended to be treated as read-only.
	- Primitive list-based structures are used intentionally to match the final rendered template shape.
	- Row and column ordering is significant and relied upon by downstream test assertions.
	- The module contains no executable logic and produces no side effects.

License
	- Internal Use Only
"""


__all__ = []  # Internal-only test fixtures; star import exports nothing.

from typing import Final

HEADER_TITLE: Final[list[str]] = ["PCBA BOM LIST", "", "", "", "", "", "", "", "", "", "", "", "", ""]

TABLE_TITLE: Final[list[str]] = ["Item", "Component", "Device Package", "Description", "Unit", "Classification",
                                 "Manufacturer", "Manufacturer P/N", "UL/VDE Number", "Validated at", "Qty",
                                 "Designator", "U/P (RMB W/ VAT)", "Sub-Total (RMB W/ VAT)"]

# =============================================================================
# BOM A
# =============================================================================

ROW_A_1_PRIMARY: Final[list[str]] = ["1", "Resistor", "0603", "2k,1%,0603", "PCS", "A", "Delta", "RES002K0A0603",
                                     "UL569", "EB0", "2.0", "R1,R2", "0.1", "0.2", ]

ROW_A_1_ALT1: Final[list[str]] = ["", "ALT1", "0603", "2k,1%,0603", "PCS", "A", "Yageo", "RC0603FR-072KL", "UL123",
                                  "EB0", "0", "", "0", "0", ]

ROW_A_1_ALT2: Final[list[str]] = ["", "ALT2", "0603", "2k,1%,0603", "PCS", "A", "Vishay", "CRCW06032K00FKEAC", "UL124",
                                  "EB0/EB1", "0", "", "0", "0", ]

ROW_A_2_PRIMARY: Final[list[str]] = ["2", "Capacitor", "0805", "10uF,10%,50V,0805", "PCS", "B", "Sigma",
                                     "CC106050100805", "UL102", "P1/MP", "3.0", "C1,C2,C3", "0.2", "0.6", ]

ROW_A_2_ALT: Final[list[str]] = ["", "ALT1", "0805", "10uF,20%,25V,0805", "PCS", "B", "Murata", "GRM21BR61C106KE15L",
                                 "UL202", "MP", "0", "", "0", "0", ]

ROW_A_3_PRIMARY: Final[list[str]] = ["3", "Relay", "SPST-4", "Relay,250VAC,5A,12V,100mA", "PCS", "A", "Panasonic",
                                     "REL2505-12100", "UL000", "MP", "0.0", "RL1", "0.5", "0.0", ]

ROW_A_4_PRIMARY: Final[list[str]] = ["4", "IC", "QFN-8", "Op-Amp,10MHz,RRIO,5V,1mA", "PCS", "A", "Gamma", "LM335",
                                     "VDE1123", "MP", "1.0", "U1", "1.2", "1.2", ]

HEADER_A: Final[list[list[str]]] = [
    ["Model No: ", "AB100", "", "", "", "", "", "Manufacturer:", "Delta", "", "Rev:", "MB", "Total", "2.4"],
    ["Description:", "Power PCBA", "", "", "", "", "", "Prepared by: ", "", "", "Date:", "2025-01-12", "OHP", "0.4"],
    ["HSF Status: ", "", "", "", "", "", "", "Approved by: ", "", "", "Schematic Rev:", "", "Material", "2.0"],
]

TABLE_A: Final[list[list[str]]] = [
    ROW_A_1_PRIMARY,
    ROW_A_1_ALT1,
    ROW_A_1_ALT2,
    ROW_A_2_PRIMARY,
    ROW_A_2_ALT,
    ROW_A_3_PRIMARY,
    ROW_A_4_PRIMARY,
]

BOARD_A: Final[list[list[str]]] = [
    HEADER_TITLE,
    *HEADER_A,
    TABLE_TITLE,
    *TABLE_A,
]

BOM_A: Final[dict[str, list[list[str]]]] = {"Power PCBA": BOARD_A}

# =============================================================================
# BOM B — BOARD_B1
# =============================================================================
ROW_B1_1: Final[list[str]] = ["1", "Resistor", "0402", "1k,5%,0402", "PCS", "A", "Ohmite", "RES001K0A0402", "UL100",
                              "P1", "4.0", "R1,R2,R3,R4", "0.05", "0.2"]
ROW_B1_2: Final[list[str]] = ["2", "Capacitor", "0603", "47nF,10%,50V,0603", "PCS", "B", "TDK", "C0603X7R50047",
                              "UL200", "P1", "2.0", "C1,C2", "0.08", "0.16"]
ROW_B1_3: Final[list[str]] = ["3", "Inductor", "0805", "10uH,20%,0805", "PCS", "B", "Coilcraft", "L080510UH", "UL300",
                              "P1", "1.0", "L1", "0.3", "0.3"]
ROW_B1_4: Final[list[str]] = ["4", "IC", "SOIC-8", "LDO,5V,1A", "PCS", "A", "Texas Instruments", "LM7805SOIC", "VDE500",
                              "P1", "1.0", "U1", "0.5", "0.5"]

HEADER_B1: Final[list[list[str]]] = [
    ["Model No: ", "BB200", "", "", "", "", "", "Manufacturer:", "Ohmite", "", "Rev:", "P1", "Total", "1.4"],
    ["Description:", "Control PCBA", "", "", "", "", "", "Prepared by: ", "", "", "Date:", "2025-02-10", "OHP", "0.24"],
    ["HSF Status: ", "", "", "", "", "", "", "Approved by: ", "", "", "Schematic Rev:", "", "Material", "1.16"],
]

TABLE_B1: Final[list[list[str]]] = [
    ROW_B1_1,
    ROW_B1_2,
    ROW_B1_3,
    ROW_B1_4,
]

BOARD_B1: Final[list[list[str]]] = [
    HEADER_TITLE,
    *HEADER_B1,
    TABLE_TITLE,
    *TABLE_B1,
]

# =============================================================================
# BOM B — BOARD_B2
# =============================================================================
ROW_B2_1: Final[list[str]] = ["1", "Resistor", "0603", "4.7k,1%,0603", "PCS", "A", "Yageo", "RC0603FR-074K7L", "UL101",
                              "MP", "6.0", "R5,R6,R7,R8,R9,R10", "0.02", "0.12"]
ROW_B2_2: Final[list[str]] = ["2", "Capacitor", "0805", "1uF,10%,25V,0805", "PCS", "B", "Murata", "GRM21BR71C105KA01L",
                              "UL202", "MP", "4.0", "C3,C4,C5,C6", "0.05", "0.2"]
ROW_B2_3: Final[list[str]] = ["3", "Diode", "SMA", "Schottky,1A,40V", "PCS", "A", "OnSemi", "SS14", "UL303", "MP", "2.0",
                              "D1,D2", "0.15", "0.3"]
ROW_B2_4: Final[list[str]] = ["4", "Connector", "2x5", "Header,10-pin,2.54mm", "PCS", "C", "Samtec", "FTSH-105-01",
                              "UL404", "MP", "1.0", "J1", "0.25", "0.25"]
ROW_B2_5: Final[list[str]] = ["5", "MCU", "QFP-32", "ARM,Cortex-M0,32-bit,32-pin", "PCS", "A", "STMicro",
                              "STM32F030K6T6", "VDE789", "MP", "1.0", "U2", "1.5", "1.5"]
ROW_B2_6: Final[list[str]] = ["6", "Crystal", "HC-49S", "16MHz,±20ppm", "PCS", "B", "Epson", "Q16.000MHZHC49", "UL505",
                              "MP", "1.0", "Y1", "0.1", "0.1"]

HEADER_B2: Final[list[list[str]]] = [
    ["Model No: ", "BB300", "", "", "", "", "", "Manufacturer:", "Murata", "", "Rev:", "MP", "Total", "3.0"],
    ["Description:", "Interface PCBA", "", "", "", "", "", "Prepared by: ", "", "", "Date:", "2025-03-05", "OHP",
     "0.53"],
    ["HSF Status: ", "", "", "", "", "", "", "Approved by: ", "", "", "Schematic Rev:", "", "Material", "2.47"],
]

TABLE_B2: Final[list[list[str]]] = [
    ROW_B2_1,
    ROW_B2_2,
    ROW_B2_3,
    ROW_B2_4,
    ROW_B2_5,
    ROW_B2_6,
]

BOARD_B2: Final[list[list[str]]] = [
    HEADER_TITLE,
    *HEADER_B2,
    TABLE_TITLE,
    *TABLE_B2,
]

BOM_B: Final[dict[str, list[list[str]]]] = {
    "Control PCBA": BOARD_B1,
    "Interface PCBA": BOARD_B2,
}
