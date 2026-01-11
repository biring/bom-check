"""
Unit tests validating the public adapter interface for version 3 header and table mappings.

This module verifies that the adapter façade exposes callable mapping functions for version 3 templates and that these functions return objects of the expected type when provided with valid, known-good input mappings. The tests focus exclusively on observable interface behavior and returned result types, without asserting on internal transformation logic or field-level correctness.

Test scope
	- Validation that canonical-to-template header mapping returns a dictionary.
	- Validation that canonical-to-template table mapping returns a dictionary.
	- Validation that template-to-BOM header mapping returns a populated header model instance.
	- Validation that template-to-BOM table mapping returns a populated row model instance.
	- Coverage of happy-path inputs using known-good fixture values only.

Execution
	Preferred execution via project-root invocation
	python -m unittest tests\adapters\test_interfaces.py

	Test discovery (runs broader suite)
	python -m unittest discover

Test data and fixtures
	- Input values provided as in-memory dictionaries keyed by canonical or template label enums.
	- Scalar test values sourced from shared version 3 fixture constants.
	- No filesystem usage, temporary directories, or explicit cleanup logic.

Dependencies
	- Python 3.x
	- Standard Library: unittest

Notes
	- Assertions are limited to verifying return types rather than validating mapped content.
	- Tests are deterministic due to static fixture inputs and lack of external side effects.
	- Adapter functions and model classes are treated as external dependencies and are not inspected internally.

License
	Internal Use Only
"""

import unittest

from src.schemas.interfaces import (
    HeaderLabelsV3,
    TableLabelsV3,
)

from src.models.interfaces import (
    CanonicalHeaderAttrNames,
    CanonicalComponentAttrNames,
    CanonicalPartAttrNames,
    HeaderV3,
    RowV3,
)

from src.adapters import interfaces as adapters

from tests.fixtures import v3_value as vfx


class TestInterfaces(unittest.TestCase):
    """
    Unit tests to verify the adapter public interface façade.
    """

    def test_map_canonical_to_template_v3_header(self):
        """
        Should return a dict when the canonical-to-template header mapping is invoked via the public interface.
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

        # ACT
        actual = adapters.map_canonical_to_template_v3_header(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=dict.__name__):
            self.assertIsInstance(actual, dict)

    def test_map_canonical_to_template_v3_table(self):
        """
        Should return a dict when the canonical-to-template table mapping is invoked via the public interface.
        """
        # ARRANGE
        values = {
            CanonicalPartAttrNames.ITEM: vfx.ITEM_GOOD[0],
            CanonicalComponentAttrNames.COMPONENT_TYPE: vfx.COMP_TYPE_GOOD[0],
            CanonicalComponentAttrNames.DEVICE_PACKAGE: vfx.DEVICE_PACKAGE_GOOD[0],
            CanonicalComponentAttrNames.DESCRIPTION: vfx.DESCRIPTION_GOOD[0],
            CanonicalPartAttrNames.UNITS: vfx.UNITS_GOOD[0],
            CanonicalPartAttrNames.CLASSIFICATION: vfx.CLASSIFICATION_GOOD[0],
            CanonicalComponentAttrNames.MANUFACTURER: vfx.MFG_NAME_GOOD[0],
            CanonicalComponentAttrNames.MFG_PART_NO: vfx.MFG_PART_NO_GOOD[0],
            CanonicalComponentAttrNames.UL_VDE_NUMBER: vfx.UL_VDE_NO_GOOD[0],
            CanonicalComponentAttrNames.VALIDATED_AT: vfx.VALIDATED_AT_GOOD[0],
            CanonicalPartAttrNames.QTY: vfx.QUANTITY_GOOD[0],
            CanonicalPartAttrNames.DESIGNATORS: vfx.DESIGNATOR_GOOD[0],
            CanonicalComponentAttrNames.UNIT_PRICE: vfx.PRICE_GOOD[0],
            CanonicalPartAttrNames.SUB_TOTAL: vfx.PRICE_GOOD[0],
        }

        # ACT
        actual = adapters.map_canonical_to_template_v3_table(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=dict.__name__):
            self.assertIsInstance(actual, dict)

    def test_map_template_v3_header_to_bom_v3_header(self):
        """
        Should return a HeaderV3 instance when the template-to-BOM header mapping is invoked via the public interface.
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

        # ACT
        actual = adapters.map_template_v3_header_to_bom_v3_header(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=HeaderV3.__name__):
            self.assertIsInstance(actual, HeaderV3)

    def test_map_template_v3_table_to_bom_v3_row(self):
        """
        Should return a RowV3 instance when the template-to-BOM table mapping is invoked via the public interface.
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

        # ACT
        actual = adapters.map_template_v3_table_to_bom_v3_row(values)

        # ASSERT
        with self.subTest(Act=type(actual).__name__, Exp=RowV3.__name__):
            self.assertIsInstance(actual, RowV3)


if __name__ == "__main__":
    unittest.main()
