"""
Unit tests for rendering canonical BOM data into a version 3 template-backed tabular format.

This module verifies the transformation of canonical header, part, and component data into flat mappings and their placement into a version 3 BOM template represented as a pandas DataFrame. The tests focus on value coercion, suppression rules for alternate components, preservation of template labels, non-mutation of the input template, and the generation of one or more rendered sheets keyed by board name.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/transformers/test__canonical_to_v3_template.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- Canonical BOM, board, header, part, and component objects provided by shared test fixtures.
	- A version 3 BOM template loaded as a pandas DataFrame from an external loader.
	- Derived row dictionaries extracted from rendered DataFrames using a local helper.
	- No temporary files or directories are created; all data is in-memory.
	- No explicit teardown or cleanup is required.

Dependencies
	- Python 3.x
	- Standard Library: unittest
	- Third-party: pandas

Notes
	- Assertions avoid hard-coded cell coordinates and instead search rendered output for expected values and row mappings.
	- Tests rely on fixture content to include both primary and alternate components.
	- Rendering behavior is validated through DataFrame equality, membership checks, and row-dictionary comparisons.
	- The template DataFrame is expected to remain unchanged after rendering operations.

License
	Internal Use Only
"""

import unittest

import pandas as pd

import pandas.testing as pdt

from src.adapters.interfaces import (
    map_canonical_to_template_v3_table,
)

from src.importers.interfaces import (
    load_version3_bom_template,
)

from src.models.interfaces import (
    CanonicalHeaderAttrNames,
    CanonicalPartAttrNames,
    CanonicalComponentAttrNames,
)

from src.schemas.interfaces import (
    TABLE_TITLE_ROW_IDENTIFIERS_V3,
)

# noinspection PyProtectedMember
from src.transformers import _canonical_to_v3_template as canon_to_v3  # module under test

from tests.fixtures import canonical as fx_canonical


def _extract_table_row_dicts(rendered_df: pd.DataFrame) -> list[dict]:
    """
    Extract data rows as dicts keyed by the table header labels discovered in the DataFrame.
    Returns only rows that contain at least one non-blank cell.
    """
    # Find title/header row using schema identifiers
    title_row = -1
    required = {str(x).strip().lower() for x in TABLE_TITLE_ROW_IDENTIFIERS_V3}
    for r in range(rendered_df.shape[0]):
        present = {
            str(rendered_df.iat[r, c]).strip().lower()
            for c in range(rendered_df.shape[1])
            if rendered_df.iat[r, c] is not None and str(rendered_df.iat[r, c]).strip() != ""
        }
        if required.issubset(present):
            title_row = r
            break

    if title_row < 0:
        # fallback: try to find a row with many non-empty string cells
        for r in range(rendered_df.shape[0]):
            present = {
                str(rendered_df.iat[r, c]).strip().lower()
                for c in range(rendered_df.shape[1])
                if rendered_df.iat[r, c] is not None and str(rendered_df.iat[r, c]).strip() != ""
            }
            if len(present) >= 3:  # heuristic fallback
                title_row = r
                break

    # Build column index map from discovered header row
    col_index: dict[str, int] = {}
    if title_row >= 0:
        for c in range(rendered_df.shape[1]):
            cell = rendered_df.iat[title_row, c]
            if cell is None:
                continue
            label = str(cell).strip()
            if label == "":
                continue
            col_index[label] = c

    # Extract data rows (rows after header) as dicts keyed by header labels
    row_dicts: list[dict] = []
    start_row = title_row + 1 if title_row >= 0 else 0
    for r in range(start_row, rendered_df.shape[0]):
        row = {}
        any_non_blank = False
        for label, c in col_index.items():
            val = rendered_df.iat[r, c]
            # treat pandas NaN as blank
            if val is not None and not (isinstance(val, float) and pd.isna(val)):
                any_non_blank = True
            row[label] = val
        if any_non_blank:
            row_dicts.append(row)
    return row_dicts


class TestCanonicalHeaderToDict(unittest.TestCase):
    """
    Unit tests to verify normalization of canonical header data into a flat attribute mapping.
    """

    def test_happy_path(self) -> None:
        """
        Should coerce string-like fields to str and preserve numeric cost fields.
        """
        # ARRANGE
        header = fx_canonical.HEADER_A_CANONICAL
        expected_dict = {
            CanonicalHeaderAttrNames.MODEL_NUMBER: str(header.model_no),
            CanonicalHeaderAttrNames.BOARD_NAME: str(header.board_name),
            CanonicalHeaderAttrNames.BOARD_SUPPLIER: str(header.manufacturer),
            CanonicalHeaderAttrNames.BUILD_STAGE: str(header.build_stage),
            CanonicalHeaderAttrNames.BOM_DATE: fx_canonical.HEADER_A_CANONICAL.date.date().isoformat(),
            CanonicalHeaderAttrNames.MATERIAL_COST: header.material_cost,
            CanonicalHeaderAttrNames.OVERHEAD_COST: header.overhead_cost,
            CanonicalHeaderAttrNames.TOTAL_COST: header.total_cost,
        }

        # ACT
        actual_dict = canon_to_v3._canonical_header_to_dict(header)

        # ASSERT
        with self.subTest("Return type", Act=type(actual_dict), Exp=dict):
            self.assertIsInstance(actual_dict, dict)

        for key in expected_dict.keys():
            actual_value = actual_dict.get(key)
            expected_value = expected_dict.get(key)
            with self.subTest(key, Act=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)


class TestCanonicalRowToDict(unittest.TestCase):
    """
    Unit tests to verify flattening of canonical part and component data into table row mappings.
    """

    def test_primary_level(self) -> None:
        """
        Should return a populated row mapping when level is zero.
        """
        # ARRANGE
        part = fx_canonical.PART_A_1
        component = fx_canonical.COMP_A_1_PRIMARY
        level = 0
        expected_dict = {
            CanonicalPartAttrNames.ITEM: part.item,
            CanonicalPartAttrNames.UNITS: str(part.unit),
            CanonicalPartAttrNames.CLASSIFICATION: str(part.classification),
            CanonicalPartAttrNames.QTY: part.qty,
            CanonicalPartAttrNames.DESIGNATORS: ",".join(part.designators),
            CanonicalPartAttrNames.SUB_TOTAL: part.sub_total,
            CanonicalComponentAttrNames.COMPONENT_TYPE: str(component.component_type),
            CanonicalComponentAttrNames.DEVICE_PACKAGE: str(component.device_package),
            CanonicalComponentAttrNames.DESCRIPTION: str(component.description),
            CanonicalComponentAttrNames.MANUFACTURER: str(component.manufacturer),
            CanonicalComponentAttrNames.MFG_PART_NO: str(component.mfg_part_number),
            CanonicalComponentAttrNames.UL_VDE_NUMBER: str(component.ul_vde_number),
            CanonicalComponentAttrNames.VALIDATED_AT: "/".join(component.validated_at),
            CanonicalComponentAttrNames.UNIT_PRICE: component.unit_price,
        }

        # ACT
        actual_dict = canon_to_v3._canonical_row_to_dict(part, component, level=level)

        # ASSERT
        with self.subTest("Return type", Act=type(actual_dict), Exp=dict):
            self.assertIsInstance(actual_dict, dict)

        for key in expected_dict.keys():
            actual_value = actual_dict.get(key)
            expected_value = expected_dict.get(key)
            with self.subTest(key, Act=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)

    def test_alternate_level(self) -> None:
        """
        Should suppress identifying, quantity, and cost fields when level is greater than zero.
        """
        # ARRANGE
        part = fx_canonical.PART_A_1
        component = fx_canonical.COMP_A_1_ALT2
        level = 2
        expected_dict = {
            CanonicalPartAttrNames.ITEM: "",
            CanonicalComponentAttrNames.COMPONENT_TYPE: "ALT2",
            CanonicalPartAttrNames.UNITS: str(part.unit),
            CanonicalPartAttrNames.CLASSIFICATION: str(part.classification),
            CanonicalPartAttrNames.QTY: 0,
            CanonicalPartAttrNames.DESIGNATORS: "",
            CanonicalPartAttrNames.SUB_TOTAL: 0,
            CanonicalComponentAttrNames.DEVICE_PACKAGE: str(component.device_package),
            CanonicalComponentAttrNames.DESCRIPTION: str(component.description),
            CanonicalComponentAttrNames.MANUFACTURER: str(component.manufacturer),
            CanonicalComponentAttrNames.MFG_PART_NO: str(component.mfg_part_number),
            CanonicalComponentAttrNames.UL_VDE_NUMBER: str(component.ul_vde_number),
            CanonicalComponentAttrNames.VALIDATED_AT: "/".join(component.validated_at),
            CanonicalComponentAttrNames.UNIT_PRICE: 0,
        }

        # ACT
        actual_dict = canon_to_v3._canonical_row_to_dict(part, component, level=level)

        # ASSERT
        with self.subTest("Return type", Act=type(actual_dict), Exp=dict):
            self.assertIsInstance(actual_dict, dict)

        for key in expected_dict.keys():
            actual_value = actual_dict.get(key)
            expected_value = expected_dict.get(key)
            with self.subTest(key, Act=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)

    def test_negative_level(self) -> None:
        """
        Should raise ValueError when level is negative.
        """
        # ARRANGE
        part = fx_canonical.PART_A_1
        component = fx_canonical.COMP_A_1_PRIMARY
        level = -1
        expected_type = ValueError.__name__

        # ACT
        try:
            canon_to_v3._canonical_row_to_dict(part, component, level=level)
            actual = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")


class TestV3TemplateSheet(unittest.TestCase):
    """
    Unit tests to verify rendering of a canonical board into a V3 template-backed DataFrame.
    """

    def test_happy_path(self) -> None:
        """
        Should render header and table values into the output DataFrame.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        board = fx_canonical.BOARD_A_CANONICAL

        # ACT
        rendered_df = canon_to_v3._V3TemplateSheet(template_df).render_board(board)

        # ASSERT
        with self.subTest("return_type", Act=type(rendered_df), Exp=pd.DataFrame):
            self.assertIsInstance(rendered_df, pd.DataFrame)

        # Assert key tokens exist somewhere in the rendered sheet (avoid hardcoding coordinates)
        sheet_text = " ".join(
            str(x)
            for x in rendered_df.to_numpy().ravel()
            if x is not None and str(x).strip() != ""
        )

        tokens = (
            str(board.header.model_no),
            str(board.header.board_name),
            str(board.header.build_stage),
            str(board.header.manufacturer),
            # Table tokens (from fixtures)
            fx_canonical.COMP_A_1_PRIMARY.mfg_part_number,
            fx_canonical.COMP_A_2_PRIMARY.mfg_part_number,
            fx_canonical.COMP_A_4_PRIMARY.mfg_part_number,
            # Alternate markers should appear because PART_A_1 has two alternates
            "ALT1",
            "ALT2",
        )

        for token in tokens:
            with self.subTest("token_present", Act=token in sheet_text, Exp=True):
                self.assertIn(token, sheet_text)

    def test_template_labels_present(self) -> None:
        """
        Should preserve all non-empty string labels from the template in the rendered DataFrame.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        board = fx_canonical.BOARD_A_CANONICAL

        # ACT
        rendered_df = canon_to_v3._V3TemplateSheet(template_df).render_board(board)

        # ASSERT
        # Flatten template into a set of non-empty string labels
        template_labels = {
            cell.strip()
            for cell in template_df.to_numpy().ravel()
            if isinstance(cell, str)
               and cell.strip() != ""
               and not cell.strip().isdigit()
        }

        rendered_values = {
            str(cell).strip()
            for cell in rendered_df.to_numpy().ravel()
            if cell is not None
               and isinstance(cell, str)
               and str(cell).strip() != ""
        }

        for label in template_labels:
            with self.subTest("template_label_present", Label=label):
                self.assertIn(label, rendered_values)

    def test_primary_row_dict_written(self) -> None:
        """
        Should write the primary component mapped values as a complete table row (dict) in the rendered sheet.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        board = fx_canonical.BOARD_A_CANONICAL

        part = fx_canonical.PART_A_1
        component = part.primary_component

        expected_row = map_canonical_to_template_v3_table(
            canon_to_v3._canonical_row_to_dict(part, component, level=0)
        )

        # ACT
        rendered_df = canon_to_v3._V3TemplateSheet(template_df).render_board(board)

        # ASSERT
        # Convert rendered DF table area into a list of row-dicts keyed by discovered header labels.
        row_dicts = _extract_table_row_dicts(rendered_df)

        # Use subTest for clearer failure reporting
        with self.subTest("expected_row_is_dict", Act=type(expected_row), Exp=dict):
            self.assertIsInstance(expected_row, dict)

        with self.subTest("row_dicts_non_empty", Act=len(row_dicts) > 0, Exp=True):
            self.assertTrue(len(row_dicts) > 0)

        # Assert exact dict membership (one of the written rows matches exactly the mapped dict)
        found = False
        for rd in row_dicts:
            if rd == expected_row:
                found = True
                break

        with self.subTest("expected_row_written", Act=found, Exp=True):
            self.assertTrue(found)

    def test_alternate_rows_written(self) -> None:
        """
        Should write mapped alternate component rows (ALT1, ALT2, ...) and their suppressed fields into the rendered sheet.
        """
        # ARRANGE
        from src.adapters.interfaces import map_canonical_to_template_v3_table

        template_df = load_version3_bom_template()
        board = fx_canonical.BOARD_A_CANONICAL

        # Build expected mapped rows for all alternates across the board
        expected_alternates: list[dict] = []
        for part in board.parts:
            for level, alt in enumerate(part.alternate_components, start=1):
                alt_values = canon_to_v3._canonical_row_to_dict(part, alt, level=level)
                expected_alternates.append(map_canonical_to_template_v3_table(alt_values))

        # Sanity: there should be at least one alternate in the fixture used by this test
        with self.subTest("has_alternates_in_fixture", Act=len(expected_alternates), Exp=">0"):
            self.assertGreater(len(expected_alternates), 0)

        # ACT
        rendered_df = canon_to_v3._V3TemplateSheet(template_df).render_board(board)

        # ASSERT
        row_dicts = _extract_table_row_dicts(rendered_df)

        with self.subTest("row_dicts_non_empty", Act=len(row_dicts) > 0, Exp=True):
            self.assertTrue(len(row_dicts) > 0)

        # For each expected alternate mapped dict, assert it appears exactly as a written row.
        for idx, exp_alt in enumerate(expected_alternates, start=1):
            case_name = f"alt_row_{idx}"
            with self.subTest(case_name, Act=exp_alt, Exp="present"):
                self.assertIn(exp_alt, row_dicts)

    def test_template_not_mutated(self) -> None:
        """
        Should not mutate the input template DataFrame when rendering a board.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        template_before = template_df.copy(deep=True)
        board = fx_canonical.BOARD_A_CANONICAL

        # ACT
        _ = canon_to_v3._V3TemplateSheet(template_df).render_board(board)

        # ASSERT
        with self.subTest("template_unchanged", Act=True, Exp=True):
            pdt.assert_frame_equal(template_df, template_before)


class TestCanonicalToV3TemplateSheets(unittest.TestCase):
    """
    Unit tests to verify rendering of canonical BOMs into a mapping of V3 template sheets.
    """

    def test_single_sheet(self) -> None:
        """
        Should return a dict mapping a single board name to a DataFrame.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        bom = fx_canonical.BOM_A_CANONICAL
        expected_key = fx_canonical.HEADER_A_CANONICAL.board_name.strip()

        # ACT
        sheets = canon_to_v3.canonical_to_v3_template_sheets(bom, template_df)

        # ASSERT
        with self.subTest("return_type", Act=type(sheets), Exp=dict):
            self.assertIsInstance(sheets, dict)

        with self.subTest("sheet_count", Act=len(sheets), Exp=1):
            self.assertEqual(len(sheets), 1)

        with self.subTest("sheet_key", Act=list(sheets.keys()), Exp=[expected_key]):
            self.assertIn(expected_key, sheets)

        with self.subTest("sheet_value_type", Act=type(sheets[expected_key]), Exp=pd.DataFrame):
            self.assertIsInstance(sheets[expected_key], pd.DataFrame)

    def test_multiple_sheets(self) -> None:
        """
        Should return a dict mapping multiple board names to DataFrames.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        bom = fx_canonical.BOM_B_CANONICAL
        expected_keys = [b.header.board_name.strip() for b in bom.boards]

        # ACT
        sheets = canon_to_v3.canonical_to_v3_template_sheets(bom, template_df)

        # ASSERT
        with self.subTest("return_type", Act=type(sheets), Exp=dict):
            self.assertIsInstance(sheets, dict)

        with self.subTest("sheet_count", Act=len(sheets), Exp=len(expected_keys)):
            self.assertEqual(len(sheets), len(expected_keys))

        for key in expected_keys:
            with self.subTest("sheet_key_present", Act=key in sheets, Exp=True):
                self.assertIn(key, sheets)
            with self.subTest("sheet_value_type", Key=key, Act=type(sheets[key]), Exp=pd.DataFrame):
                self.assertIsInstance(sheets[key], pd.DataFrame)


if __name__ == "__main__":
    unittest.main()
