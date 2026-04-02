"""
Provides static fixtures representing version 3 BOM tabular outputs.

This module defines deterministic, list-based data structures that mirror spreadsheet-like BOM layouts, including header metadata, table titles, and ordered row data for multiple board configurations. The fixtures are intended to support tests that validate rendering or transformation logic by supplying stable, preconstructed inputs and expected shapes without requiring external file or spreadsheet dependencies.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/fixtures/test_v3_df.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Static in-memory lists represent header rows, table schemas, and BOM line items.
	- Composite board structures are assembled as ordered nested lists to reflect final tabular layout.
	- Dictionary mappings group board-level data under descriptive names for multi-board BOM scenarios.
	- Additional dataframe representations are derived from list-based fixtures using in-memory construction.
	- No temporary files or external resources are used; all data is defined inline and requires no cleanup.

Dependencies:
	- Python 3.x
	- Standard Library: typing
	- Third-party: pandas

Notes:
	- All fixtures are declared as immutable constants and are intended to be treated as read-only.
	- Row and column ordering is significant and preserved to enable deterministic comparisons in tests.
	- Data structures intentionally mirror rendered output shape rather than normalized data models.
	- The module contains no executable test logic and serves only as a data provider for tests.

License:
	- Internal Use Only
"""

__all__ = []  # Internal-only test fixtures; star import exports nothing.

from typing import Final

import pandas as pd

_HEADER_TITLE: Final[list[str]] = ["PCBA BOM LIST", "", "", "", "", "", "", "", "", "", "", "", "", ""]

_TABLE_TITLE: Final[list[str]] = ["Item", "Component", "Device Package", "Description", "Unit", "Classification",
                                 "Manufacturer", "Manufacturer P/N", "UL/VDE Number", "Validated at", "Qty",
                                 "Designator", "U/P (RMB W/ VAT)", "Sub-Total (RMB W/ VAT)"]

# =============================================================================
# BOM A
# =============================================================================

_ROW_A_1_PRIMARY: Final[list[str]] = ["1", "Resistor", "0603", "2k,1%,0603", "PCS", "A", "Delta", "RES002K0A0603",
                                     "UL569", "EB0", "2.0", "R1,R2", "0.1", "0.2", ]

_ROW_A_1_ALT1: Final[list[str]] = ["", "ALT1", "0603", "2k,1%,0603", "PCS", "A", "Yageo", "RC0603FR-072KL", "UL123",
                                  "EB0", "0", "", "0", "0", ]

_ROW_A_1_ALT2: Final[list[str]] = ["", "ALT2", "0603", "2k,1%,0603", "PCS", "A", "Vishay", "CRCW06032K00FKEAC", "UL124",
                                  "EB0/EB1", "0", "", "0", "0", ]

_ROW_A_2_PRIMARY: Final[list[str]] = ["2", "Capacitor", "0805", "10uF,10%,50V,0805", "PCS", "B", "Sigma",
                                     "CC106050100805", "UL102", "P1/MP", "3.0", "C1,C2,C3", "0.2", "0.6", ]

_ROW_A_2_ALT: Final[list[str]] = ["", "ALT1", "0805", "10uF,20%,25V,0805", "PCS", "B", "Murata", "GRM21BR61C106KE15L",
                                 "UL202", "MP", "0", "", "0", "0", ]

_ROW_A_3_PRIMARY: Final[list[str]] = ["3", "Relay", "SPST-4", "Relay,250VAC,5A,12V,100mA", "PCS", "A", "Panasonic",
                                     "REL2505-12100", "UL000", "MP", "0.0", "RL1", "0.5", "0.0", ]

_ROW_A_4_PRIMARY: Final[list[str]] = ["4", "IC", "QFN-8", "Op-Amp,10MHz,RRIO,5V,1mA", "PCS", "A", "Gamma", "LM335",
                                     "VDE1123", "MP", "1.0", "U1", "1.2", "1.2", ]

_HEADER_A: Final[list[list[str]]] = [
    ["Model No: ", "AB100", "", "", "", "", "", "Manufacturer:", "Delta", "", "Rev:", "MB", "Total", "2.4"],
    ["Description:", "Power PCBA", "", "", "", "", "", "Prepared by: ", "", "", "Date:", "2025-01-12", "OHP", "0.4"],
    ["HSF Status: ", "", "", "", "", "", "", "Approved by: ", "", "", "Schematic Rev:", "", "Material", "2.0"],
]

_TABLE_A: Final[list[list[str]]] = [
    _ROW_A_1_PRIMARY,
    _ROW_A_1_ALT1,
    _ROW_A_1_ALT2,
    _ROW_A_2_PRIMARY,
    _ROW_A_2_ALT,
    _ROW_A_3_PRIMARY,
    _ROW_A_4_PRIMARY,
]

BOARD_A: Final[list[list[str]]] = [
    _HEADER_TITLE,
    *_HEADER_A,
    _TABLE_TITLE,
    *_TABLE_A,
]

BOM_A: Final[dict[str, list[list[str]]]] = {"Power PCBA": BOARD_A}

BOM_A_DATAFRAME: Final[dict[str, pd.DataFrame]] = {
    name: pd.DataFrame(board)
    for name, board in BOM_A.items()
}
# =============================================================================
# BOM B — BOARD_B1
# =============================================================================
_ROW_B1_1: Final[list[str]] = ["1", "Resistor", "0402", "1k,5%,0402", "PCS", "A", "Ohmite", "RES001K0A0402", "UL100",
                              "P1", "4.0", "R1,R2,R3,R4", "0.05", "0.2"]
_ROW_B1_2: Final[list[str]] = ["2", "Capacitor", "0603", "47nF,10%,50V,0603", "PCS", "B", "TDK", "C0603X7R50047",
                              "UL200", "P1", "2.0", "C1,C2", "0.08", "0.16"]
_ROW_B1_3: Final[list[str]] = ["3", "Inductor", "0805", "10uH,20%,0805", "PCS", "B", "Coilcraft", "L080510UH", "UL300",
                              "P1", "1.0", "L1", "0.3", "0.3"]
_ROW_B1_4: Final[list[str]] = ["4", "IC", "SOIC-8", "LDO,5V,1A", "PCS", "A", "Texas Instruments", "LM7805SOIC", "VDE500",
                              "P1", "1.0", "U1", "0.5", "0.5"]

_HEADER_B1: Final[list[list[str]]] = [
    ["Model No: ", "BB200", "", "", "", "", "", "Manufacturer:", "Ohmite", "", "Rev:", "P1", "Total", "1.4"],
    ["Description:", "Control PCBA", "", "", "", "", "", "Prepared by: ", "", "", "Date:", "2025-02-10", "OHP", "0.24"],
    ["HSF Status: ", "", "", "", "", "", "", "Approved by: ", "", "", "Schematic Rev:", "", "Material", "1.16"],
]

_TABLE_B1: Final[list[list[str]]] = [
    _ROW_B1_1,
    _ROW_B1_2,
    _ROW_B1_3,
    _ROW_B1_4,
]

BOARD_B1: Final[list[list[str]]] = [
    _HEADER_TITLE,
    *_HEADER_B1,
    _TABLE_TITLE,
    *_TABLE_B1,
]

# =============================================================================
# BOM B — BOARD_B2
# =============================================================================
_ROW_B2_1: Final[list[str]] = ["1", "Resistor", "0603", "4.7k,1%,0603", "PCS", "A", "Yageo", "RC0603FR-074K7L", "UL101",
                              "MP", "6.0", "R5,R6,R7,R8,R9,R10", "0.02", "0.12"]
_ROW_B2_2: Final[list[str]] = ["2", "Capacitor", "0805", "1uF,10%,25V,0805", "PCS", "B", "Murata", "GRM21BR71C105KA01L",
                              "UL202", "MP", "4.0", "C3,C4,C5,C6", "0.05", "0.2"]
_ROW_B2_3: Final[list[str]] = ["3", "Diode", "SMA", "Schottky,1A,40V", "PCS", "A", "OnSemi", "SS14", "UL303", "MP", "2.0",
                              "D1,D2", "0.15", "0.3"]
_ROW_B2_4: Final[list[str]] = ["4", "Connector", "2x5", "Header,10-pin,2.54mm", "PCS", "C", "Samtec", "FTSH-105-01",
                              "UL404", "MP", "1.0", "J1", "0.25", "0.25"]
_ROW_B2_5: Final[list[str]] = ["5", "MCU", "QFP-32", "ARM,Cortex-M0,32-bit,32-pin", "PCS", "A", "STMicro",
                              "STM32F030K6T6", "VDE789", "MP", "1.0", "U2", "1.5", "1.5"]
_ROW_B2_6: Final[list[str]] = ["6", "Crystal", "HC-49S", "16MHz,±20ppm", "PCS", "B", "Epson", "Q16.000MHZHC49", "UL505",
                              "MP", "1.0", "Y1", "0.1", "0.1"]

_HEADER_B2: Final[list[list[str]]] = [
    ["Model No: ", "BB300", "", "", "", "", "", "Manufacturer:", "Murata", "", "Rev:", "MP", "Total", "3.0"],
    ["Description:", "Interface PCBA", "", "", "", "", "", "Prepared by: ", "", "", "Date:", "2025-03-05", "OHP",
     "0.53"],
    ["HSF Status: ", "", "", "", "", "", "", "Approved by: ", "", "", "Schematic Rev:", "", "Material", "2.47"],
]

_TABLE_B2: Final[list[list[str]]] = [
    _ROW_B2_1,
    _ROW_B2_2,
    _ROW_B2_3,
    _ROW_B2_4,
    _ROW_B2_5,
    _ROW_B2_6,
]

BOARD_B2: Final[list[list[str]]] = [
    _HEADER_TITLE,
    *_HEADER_B2,
    _TABLE_TITLE,
    *_TABLE_B2,
]

BOM_B: Final[dict[str, list[list[str]]]] = {
    "Control PCBA": BOARD_B1,
    "Interface PCBA": BOARD_B2,
}

BOM_B_DATAFRAME: Final[dict[str, pd.DataFrame]] = {
    name: pd.DataFrame(board)
    for name, board in BOM_B.items()
}
