"""
Public interface façade for schema definitions.

This module defines the stable, supported import surface for schema-related constants and label groupings. It re-exports selected identifiers from internal schema modules so callers can rely on a consistent API while allowing internal implementation details to evolve without breaking external imports.

Key responsibilities
	- Expose schema version identifiers intended for external consumption.
	- Re-export canonical header and table label groupings for a specific schema version.
	- Provide a single supported entry point for schema-related constants.

Example usage
	Preferred usage via public package interface
	from src.schemas import interfaces as schema
	identifiers = schema.V3_TEMPLATE_IDENTIFIERS

	Direct module usage (acceptable in unit tests or internal scripts only)
	from src.schemas import interfaces as schema
	labels = schema.V3HeaderLabels

Dependencies
	- Python 3.10
	- Standard Library: None

Notes
	- This module is declarative and contains no business logic.
	- Only the symbols explicitly re-exported here are considered part of the supported API.
	- Internal schema modules are not part of the public contract and may change without notice.

License
	Internal Use Only
"""

# Re-export approved API functions from internal modules
# noinspection PyProtectedMember
from ._template_v3 import (
    HeaderLabelsV3,
    TableLabelsV3,
    TEMPLATE_VERSION_V3,
    TEMPLATE_IDENTIFIERS_V3,
    TABLE_TITLE_ROW_IDENTIFIERS_V3,
)

__all__ = [
    "TableLabelsV3",
    "HeaderLabelsV3",
    "TEMPLATE_VERSION_V3",
    "TEMPLATE_IDENTIFIERS_V3",
    "TABLE_TITLE_ROW_IDENTIFIERS_V3",
]
