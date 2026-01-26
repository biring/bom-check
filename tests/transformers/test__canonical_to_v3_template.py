"""
Unit tests for rendering canonical BOM data into a version 3 template-backed tabular format.

This module validates the transformation of canonical header, part, and component data into flat attribute mappings and their placement into a version 3 BOM template represented as a pandas DataFrame. The tests assert correct value coercion, suppression rules for alternate components, preservation of template labels, non-mutation of the input template, and the production of one or more rendered sheets keyed by board name.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/transformers/test__canonical_to_v3_template.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- Canonical BOM, board, header, part, and component objects provided by shared in-memory test fixtures.
	- A version 3 BOM template loaded as a pandas DataFrame via a loader interface.
	- Expected rendered outputs represented as lists and mappings derived from fixture DataFrames.
	- No temporary files or directories are created.
	- No explicit teardown or cleanup is required.

Dependencies
	- Python 3.x
	- Standard Library: unittest
	- Third-party: pandas

Notes
	- Rendering assertions validate values by searching rendered DataFrame contents rather than relying on fixed cell coordinates.
	- Alternate component handling is verified by checking suppression of identifying, quantity, and cost-related fields at non-zero levels.
	- Determinism depends on stable fixture data and consistent template loading behavior.
	- Input template immutability is asserted by deep comparison before and after rendering.

License
	Internal Use Only
"""

import unittest

import pandas as pd

import pandas.testing as pdt

from src.importers.interfaces import (
    load_version3_bom_template,
)

from src.models.interfaces import (
    CanonicalHeaderAttrNames,
    CanonicalPartAttrNames,
    CanonicalComponentAttrNames,
)

# noinspection PyProtectedMember
from src.transformers import _canonical_to_v3_template as canon_to_v3  # module under test

from tests.fixtures import canonical as fx_canonical
from tests.fixtures import v3_df as fx_v3_template


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
            CanonicalHeaderAttrNames.BOARD_SUPPLIER: str(header.board_supplier),
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
            CanonicalComponentAttrNames.MFG_NAME: str(component.mfg_name),
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
            CanonicalComponentAttrNames.MFG_NAME: str(component.mfg_name),
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

        cases = (
            (fx_canonical.BOARD_A_CANONICAL, fx_v3_template.BOARD_A),
            (fx_canonical.BOARD_B1_CANONICAL, fx_v3_template.BOARD_B1),
            (fx_canonical.BOARD_B2_CANONICAL, fx_v3_template.BOARD_B2),
        )

        for board, expected in cases:
            # ACT
            actual_df = canon_to_v3._V3TemplateSheet(template_df).render_board(board)

            # ASSERT
            actual_type = type(actual_df).__name__
            expected_type = pd.DataFrame.__name__
            with self.subTest("Return type", Act=actual_type, Exp=expected_type):
                self.assertEqual(actual_type, expected_type)

            actual = actual_df.astype(str).values.tolist()

            with self.subTest("Cell Value"):
                self.assertEqual(actual, expected)

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
        expected = fx_v3_template.BOM_A

        # ACT
        actual = canon_to_v3.canonical_to_v3_template_sheets(bom, template_df)

        # ASSERT
        with self.subTest("return_type", Act=type(actual).__name__, Exp=dict.__name__):
            self.assertIsInstance(actual, dict)

        with self.subTest("sheet_count", Act=len(actual), Exp=len(expected)):
            self.assertEqual(len(actual), len(expected))

    def test_multiple_sheets(self) -> None:
        """
        Should return a dict mapping multiple board names to DataFrames.
        """
        # ARRANGE
        template_df = load_version3_bom_template()
        bom = fx_canonical.BOM_B_CANONICAL
        expected = fx_v3_template.BOM_B

        # ACT
        actual = canon_to_v3.canonical_to_v3_template_sheets(bom, template_df)

        # ASSERT
        with self.subTest("return_type", Act=type(actual).__name__, Exp=dict.__name__):
            self.assertIsInstance(actual, dict)

        with self.subTest("sheet_count", Act=len(actual), Exp=len(expected)):
            self.assertEqual(len(actual), len(expected))


if __name__ == "__main__":
    unittest.main()
