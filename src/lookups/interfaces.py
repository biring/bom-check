"""
Public interface for JSON-backed lookup resources.

This module exposes a stable access surface for loading and retrieving JSON-backed lookup tables while isolating per-resource loading logic within private implementation modules. It centralizes accessors and resource metadata to ensure consistent and supported usage across the codebase.

Key Responsibilities:
	- Provide stable access functions for JSON-backed lookup tables.
	- Re-export resource identifiers and folder metadata required by consumers.
	- Prevent direct external dependence on private lookup implementation modules.

Example Usage:
	Preferred usage via public package interface.
	from src.lookups import interfaces as lookup
	table = lookup.get_component_type_lookup_table()

	Direct module usage (acceptable in unit tests or internal scripts only).
	Not applicable. Use public package interface

Dependencies:
	- Python version: >= 3.10
	- Standard Library: typing

Notes:
	- This module acts as the sole supported entry point for lookup resource access.
	- Direct imports from private lookup modules are discouraged outside unit tests.

License:
	Internal Use Only
"""

# noinspection PyProtectedMember
from ._board_supplier_codes import (
    BOARD_SUPPLIER_CODES_FOLDER_PARTS,
    BOARD_SUPPLIER_CODES_RESOURCE_NAME,
    get_board_supplier_codes_lookup_table,
)

# noinspection PyProtectedMember
from ._component_type import (
    COMPONENT_TYPE_FOLDER_PARTS,
    COMPONENT_TYPE_RESOURCE_NAME,
    get_component_type_lookup_table,
)

__all__ = [
    "BOARD_SUPPLIER_CODES_FOLDER_PARTS",
    "BOARD_SUPPLIER_CODES_RESOURCE_NAME",
    "get_board_supplier_codes_lookup_table",
    "COMPONENT_TYPE_FOLDER_PARTS",
    "COMPONENT_TYPE_RESOURCE_NAME",
    "get_component_type_lookup_table",
]
