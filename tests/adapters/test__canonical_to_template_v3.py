"""
Unit tests validating strict mapping of canonical attribute dictionaries to Version 3 BOM template label dictionaries.

This module verifies that canonical header, part, and component attribute mappings are transformed into ordered dictionaries keyed by Version 3 BOM template labels. The tests assert correct behavior for valid inputs and enforce defensive failure modes when inputs are malformed, incomplete, excessive, or result in ambiguous template label collisions.

Test scope
	- Validation of successful canonical header to template header mapping with preserved output order.
	- Validation of successful canonical part and component attribute to template table row mapping with preserved output order.
	- Negative-path coverage for missing required canonical attributes in both header and table mappings.
	- Negative-path coverage for unexpected extra canonical attributes in both header and table mappings.
	- Type validation ensuring non-dictionary inputs are rejected.
	- Detection of duplicate template label collisions via patched canonical-to-template mappings.

Execution
	Preferred execution via project-root invocation
	python -m unittest tests\test__canonical_to_template_v3.py

	Test discovery (runs broader suite)
	python -m unittest

Test data and fixtures
	- Canonical and template label values are sourced from shared test fixtures providing known-good values.
	- Mapping collision scenarios are created using temporary patching of module-level mapping dictionaries.
	- No filesystem resources are created or persisted during test execution.

Dependencies
	- Python 3.x
	- Standard Library: unittest, unittest.mock

Notes
	- Tests assert deterministic ordering by comparing ordered dictionary items sequentially.
	- Module-level mapping dictionaries are patched in isolation to simulate invalid configurations.
	- The system under test is treated as a pure transformation layer with no external side effects.

License
	Internal Use Only
"""

import unittest
from unittest.mock import patch

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

from src.models.interfaces import (
    CanonicalHeaderAttrNames,
    CanonicalComponentAttrNames,
    CanonicalPartAttrNames,
)

# noinspection PyProtectedMember
from src.adapters._canonical_to_template_v3 import (
    _CANON_HEADER_ATTR_NAME_TO_TEMPLATE_V3_HEADER_LABEL,
    map_canonical_to_template_v3_header,
    _CANON_TABLE_ATTR_NAME_TO_TEMPLATE_V3_ROW_LABEL,
    map_canonical_to_template_v3_table,
)

from tests.fixtures import v3_value as vfx


class TestMapCanonicalToTemplateV3Header(unittest.TestCase):
    """
    Unit tests for map_canonical_to_template_v3_header().
    """

    def test_happy_path(self):
        """
        Maps a complete set of canonical header to version 3 BOM template header labels.
        """
        # ARRANGE
        values = {
            CanonicalHeaderAttrNames.MODEL_NUMBER: vfx.MODEL_NO_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            CanonicalHeaderAttrNames.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            CanonicalHeaderAttrNames.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            CanonicalHeaderAttrNames.MATERIAL_COST: vfx.PRICE_GOOD[0],
            CanonicalHeaderAttrNames.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            CanonicalHeaderAttrNames.TOTAL_COST: vfx.PRICE_GOOD[0],
        }

        expected = {
            HeaderLabelsV3.MODEL_NO: vfx.MODEL_NO_GOOD[0],
            HeaderLabelsV3.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            HeaderLabelsV3.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            HeaderLabelsV3.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            HeaderLabelsV3.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            HeaderLabelsV3.MATERIAL_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            HeaderLabelsV3.TOTAL_COST: vfx.PRICE_GOOD[0],
        }

        # ACT
        actual = map_canonical_to_template_v3_header(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=dict.__name__):
            self.assertIsInstance(actual, dict)

        for actual_item, expected_item in zip(actual.items(), expected.items()):
            with self.subTest(Act=actual_item, Exp=expected_item):
                self.assertEqual(actual_item, expected_item)

    def test_missing_label(self):
        """
        Should raise KeyError when any required header label is missing.
        """
        # ARRANGE
        values = {
            CanonicalHeaderAttrNames.MODEL_NUMBER: vfx.MODEL_NO_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            # Missing: CanonicalHeaderAttrNames.BUILD_STAGE
            CanonicalHeaderAttrNames.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            CanonicalHeaderAttrNames.MATERIAL_COST: vfx.PRICE_GOOD[0],
            CanonicalHeaderAttrNames.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            CanonicalHeaderAttrNames.TOTAL_COST: vfx.PRICE_GOOD[0],
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_canonical_to_template_v3_header(values)
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
            CanonicalHeaderAttrNames.MODEL_NUMBER: vfx.MODEL_NO_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_SUPPLIER: vfx.BOARD_SUPPLIER_GOOD[0],
            CanonicalHeaderAttrNames.BUILD_STAGE: vfx.BUILD_STAGE_GOOD[0],
            CanonicalHeaderAttrNames.BOM_DATE: vfx.BOM_DATE_GOOD[0],
            CanonicalHeaderAttrNames.MATERIAL_COST: vfx.PRICE_GOOD[0],
            CanonicalHeaderAttrNames.OVERHEAD_COST: vfx.PRICE_GOOD[0],
            CanonicalHeaderAttrNames.TOTAL_COST: vfx.PRICE_GOOD[0],
            "EXTRA_HEADER_LABEL": "value",
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_canonical_to_template_v3_header(values)
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
            map_canonical_to_template_v3_header(values)  # type: ignore[arg-type]
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_duplicate_template_header_mapping(self):
        """
        Should raises ValueError when canonical mapping results in duplicate template header labels.
        """
        # ARRANGE
        patched_mapping = {
            CanonicalHeaderAttrNames.MODEL_NUMBER: HeaderLabelsV3.MODEL_NO,
            CanonicalHeaderAttrNames.BOARD_NAME: HeaderLabelsV3.MODEL_NO,  # duplicate target label
        }
        values = {
            CanonicalHeaderAttrNames.MODEL_NUMBER: vfx.MODEL_NO_GOOD[0],
            CanonicalHeaderAttrNames.BOARD_NAME: vfx.BOARD_NAME_GOOD[0],
        }
        expected_exc = ValueError.__name__

        # ACT
        with patch.dict(
                _CANON_HEADER_ATTR_NAME_TO_TEMPLATE_V3_HEADER_LABEL,
                patched_mapping,
                clear=True,
        ):
            with self.assertRaises(ValueError) as ctx:
                map_canonical_to_template_v3_header(values)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)


class TestMapCanonicalToTemplateV3Table(unittest.TestCase):
    """
    Unit tests for map_canonical_to_template_v3_table().
    """

    def test_happy_path(self):
        """
        Maps a complete set of valid template table labels to a populated RowV3 instance.
        """
        # ARRANGE
        values = {
            CanonicalPartAttrNames.ITEM: vfx.ITEM_GOOD[0],
            CanonicalComponentAttrNames.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            CanonicalComponentAttrNames.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            CanonicalComponentAttrNames.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            CanonicalPartAttrNames.UNITS: vfx.UNITS_GOOD[0],
            CanonicalPartAttrNames.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            CanonicalComponentAttrNames.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            CanonicalComponentAttrNames.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            CanonicalComponentAttrNames.UL_VDE_NUMBER: vfx.UL_VDE_NO_GOOD[0],
            CanonicalComponentAttrNames.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            CanonicalPartAttrNames.QTY: vfx.QUANTITY_GOOD[0],
            CanonicalPartAttrNames.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            CanonicalComponentAttrNames.UNIT_PRICE: vfx.PRICE_GOOD[0],
            CanonicalPartAttrNames.SUB_TOTAL: vfx.PRICE_GOOD[0],
        }

        expected = {

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
            TableLabelsV3.SUB_TOTAL: vfx.PRICE_GOOD[0], }

        # ACT
        actual = map_canonical_to_template_v3_table(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=dict.__name__):
            self.assertIsInstance(actual, dict)

        for actual_item, expected_item in zip(actual.items(), expected.items()):
            with self.subTest(Act=actual_item, Exp=expected_item):
                self.assertEqual(actual_item, expected_item)

    def test_missing_required_label(self):
        """
        Should raise KeyError when any required table label is missing.
        """
        # ARRANGE
        values = {
            CanonicalPartAttrNames.ITEM: vfx.ITEM_GOOD[0],
            CanonicalComponentAttrNames.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            CanonicalComponentAttrNames.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            CanonicalComponentAttrNames.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            CanonicalPartAttrNames.UNITS: vfx.UNITS_GOOD[0],
            CanonicalPartAttrNames.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            CanonicalComponentAttrNames.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            CanonicalComponentAttrNames.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            CanonicalComponentAttrNames.UL_VDE_NUMBER: vfx.UL_VDE_NO_GOOD[0],
            CanonicalComponentAttrNames.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            CanonicalPartAttrNames.QTY: vfx.QUANTITY_GOOD[0],
            CanonicalPartAttrNames.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            CanonicalComponentAttrNames.UNIT_PRICE: vfx.PRICE_GOOD[0],
            # Missing:  CanonicalPartAttrNames.SUB_TOTAL
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_canonical_to_template_v3_table(values)
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
            CanonicalPartAttrNames.ITEM: vfx.ITEM_GOOD[0],
            CanonicalComponentAttrNames.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            CanonicalComponentAttrNames.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            CanonicalComponentAttrNames.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            CanonicalPartAttrNames.UNITS: vfx.UNITS_GOOD[0],
            CanonicalPartAttrNames.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            CanonicalComponentAttrNames.MFG_NAME: vfx.MFG_NAME_GOOD[0],
            CanonicalComponentAttrNames.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            CanonicalComponentAttrNames.UL_VDE_NUMBER: vfx.UL_VDE_NO_GOOD[0],
            CanonicalComponentAttrNames.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            CanonicalPartAttrNames.QTY: vfx.QUANTITY_GOOD[0],
            CanonicalPartAttrNames.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            CanonicalComponentAttrNames.UNIT_PRICE: vfx.PRICE_GOOD[0],
            CanonicalPartAttrNames.SUB_TOTAL: vfx.PRICE_GOOD[0],
            "EXTRA_TABLE_LABEL": "value",
        }
        expected_exc = KeyError.__name__

        # ACT
        with self.assertRaises(KeyError) as ctx:
            map_canonical_to_template_v3_table(values)
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
            map_canonical_to_template_v3_table(values)  # type: ignore[arg-type]
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)

    def test_raises_valueerror_on_duplicate_template_table_mapping(self):
        """
        Raises ValueError when canonical mapping results in duplicate template table labels.
        """
        # ARRANGE
        patched_mapping = {
            CanonicalPartAttrNames.ITEM: TableLabelsV3.ITEM,
            CanonicalPartAttrNames.UNITS: TableLabelsV3.ITEM,  # duplicate target label
        }
        values = {
            CanonicalPartAttrNames.ITEM: vfx.ITEM_GOOD[0],
            CanonicalPartAttrNames.UNITS: vfx.UNITS_GOOD[0],
        }
        expected_exc = ValueError.__name__

        # ACT
        with patch.dict(
                _CANON_TABLE_ATTR_NAME_TO_TEMPLATE_V3_ROW_LABEL,
                patched_mapping,
                clear=True,
        ):
            with self.assertRaises(ValueError) as ctx:
                map_canonical_to_template_v3_table(values)
        actual_exc = type(ctx.exception).__name__

        # ASSERT
        with self.subTest(Act=actual_exc, Exp=expected_exc):
            self.assertEqual(actual_exc, expected_exc)


if __name__ == "__main__":
    unittest.main()
