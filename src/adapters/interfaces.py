"""
Public interface façade for the adapters package.

This module defines the stable, supported import surface for adapter-layer transformations by re-exporting approved mapping capabilities from internal implementation modules. It exists to decouple callers from the internal module layout while providing a consistent and explicit API for schema adaptation workflows.

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
from ._canonical_to_template_v3 import (
    map_canonical_to_template_v3_header,
    map_canonical_to_template_v3_table,
)

# noinspection PyProtectedMember
from ._template_v3_to_bom_v3 import (
    map_template_v3_header_to_bom_v3_header,
    map_template_v3_table_to_bom_v3_row,
)

__all__ = [
    "map_canonical_to_template_v3_header",
    "map_canonical_to_template_v3_table",
    "map_template_v3_header_to_bom_v3_header",
    "map_template_v3_table_to_bom_v3_row",
]
