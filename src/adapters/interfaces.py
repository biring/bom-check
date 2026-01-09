"""
Public interface façade for the adapters package.

This module exposes the approved, stable import API for callers by re-exporting supported adapter-layer transformations implemented in internal modules. It provides a consistent import location so internal module structure may evolve without breaking external imports.

Key responsibilities
	- Provide a stable public import surface for adapter-layer transformations.
	- Re-export supported mapping capabilities from internal implementation modules.
	- Reduce caller coupling to internal module layout.

Example usage
	# Preferred usage via public package interface:
	from src.adapters import interfaces as adapters
	bom_header = adapters.map_template_v3_header_to_bom_v3_header(template_header)

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.adapters._template_v3_to_bom_v3 import map_template_v3_table_to_bom_v3_row
	bom_row = map_template_v3_table_to_bom_v3_row(template_row)

Dependencies
	- Python >= 3.10
	- Standard Library: None

Notes
	- This module performs no work directly beyond re-exporting supported capabilities.
	- Internal modules are treated as private and may change without notice.
	- Callers should prefer importing from this module rather than internal modules.

License
	- Internal Use Only
"""

# Re-export approved API functions from internal modules

# noinspection PyProtectedMember
from ._template_v3_to_bom_v3 import (
    map_template_v3_header_to_bom_v3_header,
    map_template_v3_table_to_bom_v3_row,
)

__all__ = [
    "map_template_v3_header_to_bom_v3_header",
    "map_template_v3_table_to_bom_v3_row",
]
