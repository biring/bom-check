"""
Unit tests for Version 3 BOM parser functions.

This module provides comprehensive test coverage for the `src.parsers._v3_bom_parser`
module, which is responsible for parsing Version 3 Excel-based Bill of Materials (BOM)
files into structured data models (`Bom`, `Board`, `Header`, `Row`).

Main test capabilities:
 - Detect whether a sheet conforms to the V3 BOM format
 - Parse board-level metadata (header block)
 - Parse row-level component tables with messy or normalized headers
 - Verify full BOM file parsing across multi-board Excel files

Example Usage:
    python -m unittest tests.test_v3_bom_parser

Dependencies:
 - Python >= 3.9
 - Standard Library: os, unittest
 - External: pandas, openpyxl (via pandas.read_excel)

Notes:
 - Relies on test Excel files in `test_data/` for integration-style validation.
 - Tests use direct access to `_`-prefixed internal parsing functions (acceptable in unit scope).
 - Designed to ensure robustness against format inconsistencies like whitespace, newline/tab characters in headers.

License:
 - Internal Use Only
"""

import os
import unittest
import pandas as pd

from src.models.interfaces import (
    BomV3,
    BoardV3,
    HeaderV3,
    RowV3,
)

from src.schemas.interfaces import (
    TEMPLATE_IDENTIFIERS_V3,
    TABLE_TITLE_ROW_IDENTIFIERS_V3,
)
# noinspection PyProtectedMember
import src.parsers._v3_bom_parser as v3_parser


class TestIsCostBom(unittest.TestCase):
    """
    Unit tests for the `_is_cost_bom` function.
    """

    @staticmethod
    def _make_board(material_cost: str, total_cost: str) -> BoardV3:
        header = HeaderV3(
            model_no="X",
            board_name="Y",
            board_supplier="Z",
            build_stage="EB0",
            bom_date="2025-01-01 00:00:00",
            material_cost=material_cost,
            overhead_cost="",
            total_cost=total_cost,
        )
        return BoardV3(header=header, rows=tuple(), sheet_name="S1")

    def test_not_costed_bom_both_empty(self):
        """
        Should not classify BOM as costed BOM when both cost fields are empty.
        """
        # ARRANGE
        boards = [self._make_board("", "")]
        expected = False

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_both_zero(self):
        """
        Should not classify BOM as costed BOM when both cost fields are zero.
        """
        # ARRANGE
        boards = [self._make_board("0", "0")]
        expected = False

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_both_numeric_values(self):
        """
        Should classify BOM as costed BOM when both cost fields are number.
        """
        # ARRANGE
        boards = [self._make_board("12.34", "56.78")]
        expected = True

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_both_comma_formatted_numbers(self):
        """
        Should classify BOM as costed BOM when cost fields are numbers but comma formatted.
        """
        # ARRANGE (comma unlikely but supported)
        boards = [self._make_board("1,234.50", "2,345.60")]
        expected = True

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_unparseable_non_empty(self):
        """
        Should classify BOM as costed BOM when cost fields are non-empty, non-zero and not parsable to number.
        """
        # ARRANGE
        boards = [self._make_board("$12O.34", "$56.78")]  # "O" not zero
        expected = True

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_one_empty_other_number(self):
        """
        Should classify BOM as costed BOM when one cost fields is empty and other is a number.
        """
        # ARRANGE
        boards = [self._make_board("", "10.00")]
        expected = True

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_one_zero_other_number(self):
        """
        Should classify BOM as costed BOM when one cost fields is zero and other is a number.
        """
        # ARRANGE
        boards = [self._make_board("0", "10.00")]
        expected = True

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)

    def test_multi_board_with_one_not_costed_bom(self):
        """
        Should NOT classify BOM as costed BOM when one or more boards is classified as a not costed BOM.
        """
        # ARRANGE
        boards = [
            self._make_board("12.34", "56.78"),  # costed BOM
            self._make_board("", ""),  # NOT costed BOM
        ]
        expected = False

        # ACT
        result = v3_parser._is_cost_bom(boards)

        # ASSERT
        self.assertEqual(result, expected)


class TestIsV3BoardSheet(unittest.TestCase):
    """
    Unit tests for the `_is_v3_board_sheet` function in the v3_parser module.

    This test suite verifies whether a given DataFrame corresponds to a valid
    V3 board sheet by checking for the presence of required header identifiers.
    """

    def test_no_identifiers_present(self):
        """
        Should return False when none of the identifiers are present.
        """
        # ARRANGE
        # Prepare a DataFrame that mimics a non-V3 sheet (no matching headers)
        test_df = pd.DataFrame([["Foo", "Bar", "Baz"], ["1", "2", "3"]])
        expected = False

        # ACT
        # Run the detection function
        result = v3_parser._is_v3_board_sheet("Sheet3", test_df)

        # ASSERT
        # Verify the result is False when no required headers are present
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_some_identifiers_missing(self):
        """
        Should return False when only some identifiers are present.
        """
        # ARRANGE
        # Prepare a DataFrame with only some of the required identifiers (incomplete)
        partial_identifiers = list(TEMPLATE_IDENTIFIERS_V3)[:-1] + ["Other"]
        sheet_data = [partial_identifiers] + [[None] * len(partial_identifiers)]
        test_df = pd.DataFrame(sheet_data)
        expected = False

        # ACT
        # Run the detection function
        result = v3_parser._is_v3_board_sheet("Sheet2", test_df)

        # ASSERT
        # Verify the result is False when only some identifiers are present
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_all_identifiers_present(self):
        """
        Should return True when all identifiers are present.
        """
        # ARRANGE
        # Prepare a DataFrame that includes all required identifiers plus extras
        all_identifiers = list(TEMPLATE_IDENTIFIERS_V3) + ["Extra Column"]
        sheet_data = [all_identifiers] + [[None] * len(all_identifiers)]
        test_df = pd.DataFrame(sheet_data)
        expected = True

        # ACT
        # Run the detection function
        result = v3_parser._is_v3_board_sheet("Sheet1", test_df)

        # ASSERT
        # Verify the result is True when all required identifiers are present
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestIsV3Bom(unittest.TestCase):
    """
    Unit tests for the `is_v3_bom` function in the v3_parser module.

    This suite verifies whether a workbook (dict of DataFrames) conforms to
    the Version 3 BOM template by verifying required sheet identifiers.
    """

    def test_no_identifiers_present(self):
        """
        Should return False when none of the identifiers are present.
        """
        # ARRANGE
        # Load Excel file that does not match V3 BOM format
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'test_data', 'IsNotBomTemplate.xlsx')
        # Read Excel file as pandas data frame
        with pd.ExcelFile(file_path, engine="openpyxl") as xls:
            sheet_names = xls.sheet_names  # Get all sheet names
            # Read all sheets into a dict {sheet_name: DataFrame}
            sheets = {}
            for name in sheet_names:
                sheets[name] = pd.read_excel(xls, sheet_name=name, dtype=str, header=None)
        expected = False

        # ACT
        # Run the detection function
        result = v3_parser.is_v3_bom(sheets)

        # ASSERT
        # Verify the result is False when no identifiers are present
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_some_identifiers_missing(self):
        """
        Should return False when some of the identifiers are present.
        """
        # ARRANGE
        # Load Excel file with partial identifiers (e.g., V2 BOM format)
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'test_data', 'IsVersion2BomTemplate.xlsx')
        # Read Excel file as pandas data frame
        with pd.ExcelFile(file_path, engine="openpyxl") as xls:
            sheet_names = xls.sheet_names  # Get all sheet names
            # Read all sheets into a dict {sheet_name: DataFrame}
            sheets = {}
            for name in sheet_names:
                sheets[name] = pd.read_excel(xls, sheet_name=name, dtype=str, header=None)
        expected = False

        # ACT
        # Run the detection function
        result = v3_parser.is_v3_bom(sheets)

        # ASSERT
        # Verify the result is False when some identifiers are present
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_all_identifiers_present(self):
        """
        Should return True when all identifiers are present.
        """
        # ARRANGE
        # Load Excel file that includes all required V3 BOM identifiers
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'test_data', 'IsVersion3BomTemplate.xlsx')
        # Read Excel file as pandas data frame
        with pd.ExcelFile(file_path, engine="openpyxl") as xls:
            sheet_names = xls.sheet_names  # Get all sheet names
            # Read all sheets into a dict {sheet_name: DataFrame}
            sheets = {}
            for name in sheet_names:
                sheets[name] = pd.read_excel(xls, sheet_name=name, dtype=str, header=None)
        expected = True

        # ACT
        # Run the detection function
        result = v3_parser.is_v3_bom(sheets)

        # ASSERT
        # Verify the result is True when some identifiers are present
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestParseBoardHeader(unittest.TestCase):
    """
    Unit test for the `_parse_board_header` function in the v3_parser module.

    This test verifies whether the parser correctly extracts all board-level
    metadata fields from the top portion of a Version 3 BOM sheet.
    """

    def test_full_header_match(self):
        """
        Should parse all board-level metadata fields from a V3 BOM header section.
        """
        # ARRANGE
        # Load test Excel sheet containing a known V3 BOM header
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "test_data", "IsVersion3BomTemplate.xlsx")
        with pd.ExcelFile(file_path, engine="openpyxl") as xls:
            sheet_name = xls.sheet_names[0]  # first/only sheet
            full_sheet_df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str, header=None)
        # Use the top N rows as the header block for parsing. Adjust as needed.
        header_block_df = full_sheet_df.iloc[:10]

        # Expected Header instance from test data
        expected = HeaderV3(
            model_no="FD100US",
            board_name="POWER PCBA",
            board_supplier="Kimball",
            build_stage="EB2",
            bom_date="2020-08-10 00:00:00",
            material_cost="139.64",
            overhead_cost="2.34",
            total_cost="141.98"
        )

        # ACT
        # Run header parser on the extracted top rows
        result = v3_parser._parse_board_header(header_block_df)

        # ASSERT
        self.assertIsNotNone(result, "Parser returned None")
        # Assert: All fields match
        for field_name in expected.__dict__:
            expected_value = getattr(expected, field_name)
            result_value = getattr(result, field_name)
            with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                self.assertEqual(result_value, expected_value)


class TestParseBoardSheet(unittest.TestCase):
    """
    Unit test for the `_parse_board_sheet` function in the v3_parser module.

    This test verifies that a complete Version 3 BOM sheet can be parsed into a
    structured `Board` object with valid `Header` and multiple `Row` entries.
    """

    def test_of_bom_with_four_rows(self):
        """
        Should parse a full Version 3 BOM containing 4 row entries and a valid header.
        """
        # ARRANGE
        # Load BOM sheet from test Excel file. Excel file is expected to only have one sheet.
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "test_data", "Version3BomSample.xlsx")
        with pd.ExcelFile(file_path, engine="openpyxl") as xls:
            df = pd.read_excel(xls, dtype=str, header=None)
            sheet_name = xls.sheet_names[0]

        expected = BoardV3(
            header=HeaderV3(
                model_no="BM250",
                board_name="POWER PCBA",
                board_supplier="Kimball",
                build_stage="PP1",
                bom_date="2025-08-10 00:00:00",
                material_cost="1.5",
                overhead_cost="2.34",
                total_cost="3.84"
            ),
            sheet_name="POWER PCBA",
            rows=(
                RowV3(
                    item="1",
                    component_type="PCB",
                    device_package="",
                    description="FR-4, double layer, 1OZ, 1.6mm, 213mm*70mm",
                    units="PCS",
                    classification="A",
                    mfg_name="Quick PCB",
                    mfg_part_number="1670A_V1.1_A",
                    ul_vde_number="E351308",
                    validated_at="EB0",
                    qty="1",
                    designators="PCB",
                    unit_price="0.5",
                    sub_total="0.5"
                ),
                RowV3(
                    item="",
                    component_type="ALT1",
                    device_package="",
                    description="FR-4, double layer, 1OZ, 1.6mm, 213mm*70mm",
                    units="PCS",
                    classification="A",
                    mfg_name="Fast Turn",
                    mfg_part_number="3694AC",
                    ul_vde_number="E314919",
                    validated_at="EB1",
                    qty="0",
                    designators="",
                    unit_price="0.7",
                    sub_total="0"
                ),
                RowV3(
                    item="2",
                    component_type="Relay",
                    device_package="DIP",
                    description="12VDC 17A/250VAC SPST -40~105℃ 21*16*21.8mm",
                    units="PCS",
                    classification="A",
                    mfg_name="Sanyou",
                    mfg_part_number="SRG-S-112DM-F",
                    ul_vde_number="VDE 40037165",
                    validated_at="FOT/EB0",
                    qty="1",
                    designators="RY1",
                    unit_price="1",
                    sub_total="1"
                ),
                RowV3(
                    item="",
                    component_type="ALT1",
                    device_package="DIP",
                    description="12VDC 17A/250VAC SPST -40~105℃ 21*16*21.8mm",
                    units="PCS",
                    classification="A",
                    mfg_name="Panasonic",
                    mfg_part_number="Y3U-SS-112LMF",
                    ul_vde_number="TUV R50446369",
                    validated_at="EB1/MP",
                    qty="0",
                    designators="",
                    unit_price="1.2",
                    sub_total="0"
                )
            )
        )

        # ACT
        # Parse the BOM sheet
        result = v3_parser._parse_board_sheet(sheet_name, df)

        # ASSERT
        # Verify sheet name match expected value
        expected_sheet_name = expected.sheet_name
        result_sheet_name = result.sheet_name
        with self.subTest("Sheet Name", Out=result_sheet_name, Exp=expected_sheet_name):
            self.assertEqual(result_sheet_name, expected_sheet_name)

        # Verify all header fields match expected values
        expected_header = expected.header
        result_header = result.header
        for field_name in expected_header.__dict__:
            expected_value = getattr(expected_header, field_name)
            result_value = getattr(result_header, field_name)
            with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                self.assertEqual(result_value, expected_value)
        # Verify each row field matches expected values
        expected_rows = expected.rows
        result_rows = result.rows
        for expected_row, result_row in zip(expected_rows, result_rows):
            for field_name in expected_row.__dict__:
                expected_value = getattr(expected_row, field_name)
                result_value = getattr(result_row, field_name)
                with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                    self.assertEqual(result_value, expected_value)


class TestParseBoardTable(unittest.TestCase):
    """
    Unit tests for the `_parse_board_table` function in the v3_parser module.

    This test verifies whether the function can correctly extract a list of Row
    instances from a BOM table with messy column headers and multiple rows.
    """

    def test_with_two_rows_and_messy_header(self):
        """
        Should parse a BOM table with two rows and messy headers into Row instances.
        """
        # ARRANGE
        # Simulated BOM table with inconsistent spacing, newline, and tab characters in headers
        table_df = pd.DataFrame([
            {
                " Item ": 1,
                "Component\n": "Relay",
                "Device Package": "DIP",
                " Description ": "12VDC Relay",
                "Unit": "PCS",
                "Classification ": "A",
                "Manufacturer": "PANASONIC",
                "Manufacturer P/N": "SRG-S-112DM-F",
                "UL/VDE \tNumber": "VDE 40037165",
                "Validated at": "EB0",
                "Qty": 1,
                "Designator": "RY1",
                "U/P \n(RMB W/ VAT)": "1.000",
                "Sub-Total \n(RMB W/ VAT)": "1.000"
            },
            {
                " Item ": 2,
                "Component\n": "Capacitor",
                "Device Package": "0805",
                " Description ": "10uF 25V X7R",
                "Unit": "PCS",
                "Classification ": "B",
                "Manufacturer": "TDK",
                "Manufacturer P/N": "C2012X7R1E106K",
                "UL/VDE \tNumber": "",
                "Validated at": "EB0",
                "Qty": 2,
                "Designator": "C1,C2",
                "U/P \n(RMB W/ VAT)": "0.100",
                "Sub-Total \n(RMB W/ VAT)": "0.200"
            }
        ])

        expected = [
            RowV3(
                item="1",
                component_type="Relay",
                device_package="DIP",
                description="12VDC Relay",
                units="PCS",
                classification="A",
                mfg_name="PANASONIC",
                mfg_part_number="SRG-S-112DM-F",
                ul_vde_number="VDE 40037165",
                validated_at="EB0",
                qty="1",
                designators="RY1",
                unit_price="1.000",
                sub_total="1.000"
            ),
            RowV3(
                item="2",
                component_type="Capacitor",
                device_package="0805",
                description="10uF 25V X7R",
                units="PCS",
                classification="B",
                mfg_name="TDK",
                mfg_part_number="C2012X7R1E106K",
                ul_vde_number="",
                validated_at="EB0",
                qty="2",
                designators="C1,C2",
                unit_price="0.100",
                sub_total="0.200"
            )
        ]

        # ACT
        # Run the parser
        result = v3_parser._parse_board_table(table_df)

        # ASSERT
        for result_row, expected_row in zip(result, expected):
            # All fields match
            for field_name in expected_row.__dict__:
                expected_value = getattr(expected_row, field_name)
                result_value = getattr(result_row, field_name)
                with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                    self.assertEqual(result_value, expected_value)


class TestParseBoardTableRow(unittest.TestCase):
    """
    Unit test for the `_parse_board_table_row` function in the v3_parser module.

    This test ensures a single BOM row with messy or irregular header formatting
    is correctly parsed into an `Row` instance.
    """

    def test_with_messy_header(self):
        """
        Should parse a BOM row with inconsistent column formatting into an Row instance.
        """
        # ARRANGE
        # Simulated single BOM row with headers containing whitespace, newline, and tab characters
        row = pd.Series({
            " Item ": 1,
            "Component\n": "Relay",
            "Device Package": "DIP",
            " Description ": "12VDC Relay",
            "Unit": "PCS",
            "Classification ": "A",
            "Manufacturer": "PANASONIC",
            "Manufacturer P/N": "SRG-S-112DM-F",
            "UL/VDE \tNumber": "VDE 40037165",
            "Validated at": "EB0",
            "Qty": 1,
            "Designator": "RY1",
            "U/P \n(RMB W/ VAT)": "1.000",
            "Sub-Total \n(RMB W/ VAT)": "1.000"
        })

        # Expected result from cleaned header and values
        expected = RowV3(
            item="1",
            component_type="Relay",
            device_package="DIP",
            description="12VDC Relay",
            units="PCS",
            classification="A",
            mfg_name="PANASONIC",
            mfg_part_number="SRG-S-112DM-F",
            ul_vde_number="VDE 40037165",
            validated_at="EB0",
            qty="1",
            designators="RY1",
            unit_price="1.000",
            sub_total="1.000"
        )

        # ACT
        # Run the parser
        result = v3_parser._parse_board_table_row(row)

        # ASSERT
        # All row field must match
        for field_name in expected.__dict__:
            expected_value = getattr(expected, field_name)
            result_value = getattr(result, field_name)
            with self.subTest(Field=field_name, Out=result_value, Exp=expected_value):
                self.assertEqual(result_value, expected_value)


class TestParseBom(unittest.TestCase):
    """
    Unit test for the `parse_v3_bom` function in the v3_parser module.

    This test verifies that a multi-board Version 3 BOM Excel file is correctly parsed
    into a Bom object containing multiple Board instances with valid Headers and Rows.
    """

    def test_parse_multiple_boards_from_version3_excel(self):
        """
        Should parse a Version 3 BOM Excel file containing two separate board BOMs.
        """
        # ARRANGE
        base_dir = os.path.dirname(__file__)
        file_name = "Version3BomMultiBoard.xlsx"
        file_path = os.path.join(base_dir, "test_data", file_name)
        with pd.ExcelFile(file_path, engine="openpyxl") as xls:
            # Create an empty dictionary to store (sheet_name, DataFrame) pairs
            sheets = {}
            # Loop through each sheet name in the Excel file
            for name in xls.sheet_names:
                # Parse the sheet into a DataFrame, forcing all cells to string, no header
                df = xls.parse(name, dtype=str, header=None)
                # Add the tuple (sheet_name, DataFrame) to our list
                sheets[name] = df

        expected = BomV3(
            file_name=file_name,
            boards=(
                BoardV3(
                    header=HeaderV3(
                        model_no="BM250",
                        board_name="Power PCBA",
                        board_supplier="Kimball",
                        build_stage="PP1",
                        bom_date="2025-08-10 00:00:00",
                        material_cost="0.9",
                        overhead_cost="1.25",
                        total_cost="2.15"
                    ),
                    sheet_name="Board1",
                    rows=(
                        RowV3(
                            item="1",
                            component_type="Substrate",
                            device_package="—",
                            description="Generic 2-layer, 1OZ, 1.6mm, 210mm × 70mm",
                            units="PCS",
                            classification="A",
                            mfg_name="FabVendor A",
                            mfg_part_number="SUB-01",
                            ul_vde_number="CERT-0001",
                            validated_at="PP1",
                            qty="1",
                            designators="PCB1",
                            unit_price="0.8",
                            sub_total="0.8"
                        ),
                        RowV3("", "ALT1", "—", "Generic 2-layer, 1OZ, 1.6mm, 210mm × 70mm", "PCS", "A",
                            "FabVendor B", "SUB-ALT1", "CERT-0002", "PP0", "0", "", "0.9", "0"),
                        RowV3("2", "Switch", "DIP", "12VDC 15A SPST, 20×15×20mm, -40~105℃", "PCS", "A",
                            "SwitchMfr A", "SW-01", "CERT-1001", "PP0/PP1", "1", "SW1", "0.1", "0.1"),
                        RowV3("", "ALT1", "DIP", "12VDC 15A SPST, 20×15×20mm, -40~105℃", "PCS", "A",
                            "SwitchMfr B", "SW-ALT1", "CERT-1002", "PP0", "0", "", "0.2", "0")
                    )
                ),
                BoardV3(
                    header=HeaderV3(
                        model_no="BM250",
                        board_name="MCU PCBA",
                        board_supplier="Kimball",
                        build_stage="PP1",
                        bom_date="2025-08-15 00:00:00",
                        material_cost="1.8",
                        overhead_cost="2.35",
                        total_cost="4.15"
                    ),
                    sheet_name="Board2",
                    rows=(
                        RowV3(
                            item="1",
                            component_type="Resistor",
                            device_package="603",
                            description="10kΩ ±1%, 1/10W, 0603",
                            units="PCS",
                            classification="A",
                            mfg_name="ResiTech",
                            mfg_part_number="R-10K-0603",
                            ul_vde_number="UL123456",
                            validated_at="EV1",
                            qty="1",
                            designators="R1",
                            unit_price="0.1",
                            sub_total="0.1"
                        ),
                        RowV3("2", "Capacitor", "805", "1uF ±10%, 50V, X7R, 0805", "PCS", "A", "Captek", "C-1U-0805",
                            "UL654321", "EV2", "1", "C1", "0.2", "0.2"),
                        RowV3("", "ALT1", "805", "1uF ±10%, 50V, X7R, 0805", "PCS", "A", "AltCap", "AC-1U-0805",
                            "UL654322", "EV3", "0", "", "0.22", "0"),
                        RowV3("3", "Diode", "SOD-123", "1A, 100V, Fast Recovery, SOD-123", "PCS", "A", "Diotronics",
                            "D-1A-100V", "UL987654", "EV4", "1", "D1", "1.5", "1.5"),
                        RowV3("", "ALT1", "SOD-123", "1A, 100V, Fast Recovery, SOD-123", "PCS", "A", "SemiComp",
                            "SC-D100", "UL987655", "EV5", "0", "", "1.45", "0"),
                        RowV3("", "ALT2", "SOD-123", "1A, 100V, Fast Recovery, SOD-123", "PCS", "A", "FastFlow",
                            "FF-1A100V", "UL987656", "EV6", "0", "", "1.48", "0")
                    )
                )
            )
        )

        # ACT
        # Run the parser
        result = v3_parser.parse_v3_bom(file_name, sheets)

        # ASSERT
        # Verify file name
        result_file_name = result.file_name
        with self.subTest("File Name", Out=result_file_name, Exp=file_name):
            self.assertEqual(result_file_name, file_name)

        # Verify number of boards
        expected_boards = len(expected.boards)
        result_boards = len(result.boards)
        with self.subTest("Board Count", Out=expected_boards, Exp=expected_boards):
            self.assertEqual(result_boards, expected_boards)

        # Verify boards
        expected_boards = expected.boards
        result_boards = result.boards
        for expected, result in zip(expected_boards, result_boards):
            # Verify sheet name match expected value
            expected_sheet_name = expected.sheet_name
            result_sheet_name = result.sheet_name
            with self.subTest("Sheet Name", Out=result_sheet_name, Exp=expected_sheet_name):
                self.assertEqual(result_sheet_name, expected_sheet_name)

            # Verify board header fields
            expected_header = expected.header
            result_header = result.header
            for field_name in expected_header.__dict__:
                expected_value = getattr(expected_header, field_name)
                result_value = getattr(result_header, field_name)
                with self.subTest("Header", Field=field_name, Out=result_value, Exp=expected_value):
                    self.assertEqual(result_value, expected_value)
            # Verify board row fields
            expected_rows = expected.rows
            result_rows = result.rows
            for expected_row, result_row in zip(expected_rows, result_rows):
                for field_name in expected_row.__dict__:
                    expected_value = getattr(expected_row, field_name)
                    result_value = getattr(result_row, field_name)
                    with self.subTest("Row", Field=field_name, Out=result_value, Exp=expected_value):
                        self.assertEqual(result_value, expected_value)


if __name__ == "__main__":
    unittest.main()
