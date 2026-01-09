"""
Unit tests validating mapping of Version 3 template label dictionaries into BOM V3 model instances.

This module verifies the in-memory transformation boundary where template-derived label-to-value dictionaries are converted into BOM V3 header and row model objects. The tests assert correct population of expected fields for valid inputs and confirm that invalid inputs are rejected using defined exception types. The scope is limited to mapping behavior and excludes persistence, file I/O, calculations, or downstream validation.

Test scope
	- Successful conversion of complete header label dictionaries into populated header model instances.
	- Successful conversion of complete table label dictionaries into populated row model instances.
	- Rejection of inputs missing required labels for both header and table mappings.
	- Rejection of inputs containing unexpected extra labels for both header and table mappings.
	- Rejection of non-dictionary inputs for both header and table mappings.
	- Coverage includes both happy-path and negative-path scenarios.

Execution
	Preferred execution via project-root invocation
	python -m unittest tests\adapters\test_template_v3_to_bom_v3.py

	Test discovery (runs broader suite)
	python -m unittest

Test data and fixtures
	- Test values are sourced from in-memory fixture constants.
	- No temporary files or directories are created.
	- No cleanup steps are required because all tests are hermetic and memory-only.

Dependencies
	- Python 3.x
	- Standard Library: unittest

Notes
	- Assertions validate individual attributes on returned objects rather than full object equality.
	- Exception checks assert exception type only and do not validate message content.
	- Tests assume deterministic behavior with no reliance on external systems or resources.

License
	Internal Use Only
"""

import unittest

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

from src.models.interfaces import (
    HeaderV3,
    RowV3,
    HeaderV3AttrNames,
    RowV3AttrNames,
)

# noinspection PyProtectedMember
from src.adapters._template_v3_to_bom_v3 import (
    map_template_v3_header_to_bom_v3_header,
    map_template_v3_table_to_bom_v3_row,
)

from tests.fixtures import v3_value as vfx


class TestMapTemplateV3HeaderToBomV3Header(unittest.TestCase):
    """
    Unit tests for map_template_v3_header_to_bom_v3_header().
    """

    def test_happy_path(self):
        """
        Maps a complete set of valid template header labels to a populated HeaderV3 instance.
        """
        # ARRANGE
        values = {
            HeaderLabelsV3.MODEL_NO: vfx.MODEL_NO_GOOD[0],
            HeaderLabelsV3.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            HeaderLabelsV3.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            HeaderLabelsV3.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            HeaderLabelsV3.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            HeaderLabelsV3.MATERIAL_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.TOTAL_COST: vfx.PRICE_GOOD[0],
        }

        expected = {
            HeaderV3AttrNames.MODEL_NO: vfx.MODEL_NO_GOOD[0],
            HeaderV3AttrNames.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            HeaderV3AttrNames.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            HeaderV3AttrNames.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            HeaderV3AttrNames.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            HeaderV3AttrNames.MATERIAL_COST: vfx.PRICE_GOOD[0],
            HeaderV3AttrNames.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            HeaderV3AttrNames.TOTAL_COST: vfx.PRICE_GOOD[0],
        }

        # ACT
        actual = map_template_v3_header_to_bom_v3_header(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=HeaderV3.__name__):
            self.assertIsInstance(actual, HeaderV3)

        for attr_name, expected_value in expected.items():
            actual_value = getattr(actual, attr_name)
            with self.subTest(Field=attr_name, Act=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)

    def test_missing_label(self):
        """
        Should raise KeyError when any required header label is missing.
        """
        # ARRANGE
        values = {
            HeaderLabelsV3.MODEL_NO: vfx.MODEL_NO_GOOD[0],
            HeaderLabelsV3.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            HeaderLabelsV3.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            HeaderLabelsV3.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            # Missing: HeaderLabelsV3.BOM_DATE
            HeaderLabelsV3.MATERIAL_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.TOTAL_COST: vfx.PRICE_GOOD[0],
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_template_v3_header_to_bom_v3_header(values)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_extra_label(self):
        """
        Should raise KeyError when any unexpected header label is provided.
        """
        # ARRANGE
        values = {
            HeaderLabelsV3.MODEL_NO: vfx.MODEL_NO_GOOD[0],
            HeaderLabelsV3.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            HeaderLabelsV3.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            HeaderLabelsV3.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            HeaderLabelsV3.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            HeaderLabelsV3.MATERIAL_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.TOTAL_COST: vfx.PRICE_GOOD[0],
            "EXTRA_HEADER_LABEL": "value",
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_template_v3_header_to_bom_v3_header(values)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_non_dict_value(self):
        """
        Should raise TypeError when values is not a dict.
        """
        # ARRANGE
        values = ["not", "a", "dict"]
        expected_exc = TypeError.__name__

        # ACT
        with self.assertRaises(TypeError) as ctx:
            map_template_v3_header_to_bom_v3_header(values)  # type: ignore[arg-type]
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)


class TestMapTemplateV3TableToBomV3Row(unittest.TestCase):
    """
    Unit tests for map_template_v3_table_to_bom_v3_row().
    """

    def test_happy_path(self):
        """
        Maps a complete set of valid template table labels to a populated RowV3 instance.
        """
        # ARRANGE
        values = {
            TableLabelsV3.ITEM: vfx.ITEM_GOOD[0],
            TableLabelsV3.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            TableLabelsV3.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            TableLabelsV3.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            TableLabelsV3.UNITS: vfx.UNITS_GOOD[0],
            TableLabelsV3.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            TableLabelsV3.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            TableLabelsV3.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            TableLabelsV3.UL_VDE_NO: vfx.UL_VDE_NO_GOOD[0],
            TableLabelsV3.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            TableLabelsV3.QUANTITY: vfx.QUANTITY_GOOD[0],
            TableLabelsV3.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            TableLabelsV3.UNIT_PRICE: vfx.PRICE_GOOD[0],
            TableLabelsV3.SUB_TOTAL: vfx.PRICE_GOOD[0],
        }

        expected = {
            RowV3AttrNames.ITEM: vfx.ITEM_GOOD[0],
            RowV3AttrNames.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            RowV3AttrNames.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            RowV3AttrNames.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            RowV3AttrNames.UNITS: vfx.UNITS_GOOD[0],
            RowV3AttrNames.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            RowV3AttrNames.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            RowV3AttrNames.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            RowV3AttrNames.UL_VDE_NO: vfx.UL_VDE_NO_GOOD[0],
            RowV3AttrNames.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            RowV3AttrNames.QTY: vfx.QUANTITY_GOOD[0],
            RowV3AttrNames.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            RowV3AttrNames.UNIT_PRICE: vfx.PRICE_GOOD[0],
            RowV3AttrNames.SUB_TOTAL: vfx.PRICE_GOOD[0],
        }

        # ACT
        actual = map_template_v3_table_to_bom_v3_row(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=RowV3.__name__):
            self.assertIsInstance(actual, RowV3)

        for attr_name, expected_value in expected.items():
            actual_value = getattr(actual, attr_name)
            with self.subTest(Field=attr_name, Act=actual_value, Exp=expected_value):
                self.assertEqual(actual_value, expected_value)

    def test_missing_required_label(self):
        """
        Should raise KeyError when any required table label is missing.
        """
        # ARRANGE
        values = {
            TableLabelsV3.ITEM: vfx.ITEM_GOOD[0],
            TableLabelsV3.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            TableLabelsV3.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            TableLabelsV3.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            TableLabelsV3.UNITS: vfx.UNITS_GOOD[0],
            TableLabelsV3.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            TableLabelsV3.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            TableLabelsV3.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            TableLabelsV3.UL_VDE_NO: vfx.UL_VDE_NO_GOOD[0],
            TableLabelsV3.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            TableLabelsV3.QUANTITY: vfx.QUANTITY_GOOD[0],
            TableLabelsV3.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            TableLabelsV3.UNIT_PRICE: vfx.PRICE_GOOD[0],
            # Missing: TableLabelsV3.SUB_TOTAL
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_template_v3_table_to_bom_v3_row(values)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_extra_label(self):
        """
        Should raise KeyError when any unexpected table label is provided.
        """
        # ARRANGE
        values = {
            TableLabelsV3.ITEM: vfx.ITEM_GOOD[0],
            TableLabelsV3.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            TableLabelsV3.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            TableLabelsV3.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            TableLabelsV3.UNITS: vfx.UNITS_GOOD[0],
            TableLabelsV3.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            TableLabelsV3.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            TableLabelsV3.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            TableLabelsV3.UL_VDE_NO: vfx.UL_VDE_NO_GOOD[0],
            TableLabelsV3.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            TableLabelsV3.QUANTITY: vfx.QUANTITY_GOOD[0],
            TableLabelsV3.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            TableLabelsV3.UNIT_PRICE: vfx.PRICE_GOOD[0],
            TableLabelsV3.SUB_TOTAL: vfx.PRICE_GOOD[0],
            "EXTRA_TABLE_LABEL": "value",
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_template_v3_table_to_bom_v3_row(values)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_non_dict_values(self):
        """
        Should raise TypeError when values is not a dict.
        """
        # ARRANGE
        values = "not a dict"
        expected_exc = TypeError.__name__

        # ACT
        with self.assertRaises(TypeError) as ctx:
            map_template_v3_table_to_bom_v3_row(values)  # type: ignore[arg-type]
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)


if __name__ == "__main__":
    unittest.main()
