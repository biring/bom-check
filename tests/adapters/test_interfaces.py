"""
Unit tests validating the public adapter interface for version 3 header and table mappings.

This module provides focused verification that the adapter façade correctly delegates mapping calls and returns populated model objects when supplied with valid label-to-value mappings for version 3 templates. The tests exercise only the observable interface behavior and type of the returned results, without asserting on internal transformation details.

Test scope
	- Validation that header mapping via the adapter interface returns an instance of the expected header model.
	- Validation that table mapping via the adapter interface returns an instance of the expected row model.
	- Coverage of happy-path inputs using known-good fixture values.

Execution
	Preferred execution via project-root invocation
		python -m unittest tests\adapters\test_interfaces.py

	Test discovery (runs broader suite)
		python -m unittest discover

Test data and fixtures
	- Input data constructed as in-memory dictionaries keyed by version 3 label enums.
	- Known-good scalar values sourced from shared test fixtures.
	- No filesystem resources, temporary directories, or explicit cleanup steps are used.

Dependencies
	- Python 3.x
	- Standard Library: unittest

Notes
	- Tests assert only on the returned object type, not on field-level content or value correctness.
	- Behavior is deterministic given static fixture inputs and absence of external side effects.
	- The adapter and model implementations are treated as external dependencies and are not inspected directly.

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
)

from src.adapters import interfaces as adapters

from tests.fixtures import v3_value as vfx


class TestAdaptersInterfaces(unittest.TestCase):
    """
    Unit tests for the public adapters.interfaces façade module.
    """

    def test_header_mapping_delegates_correctly(self):
        """
        Calling the header mapping via the interface returns a populated HeaderV3 instance.
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

    def test_table_mapping_delegates_correctly(self):
        """
        Calling the table mapping via the interface returns a populated RowV3 instance.
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
