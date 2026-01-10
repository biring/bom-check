"""
Public interface façade for the models package.

This module defines the stable, supported API surface for model objects used throughout the application. It re-exports selected data models and field definitions from internal implementations so that external callers can depend on a consistent interface while allowing internal structure to evolve without breaking consumers.

Key responsibilities
	- Expose versioned and canonical bill of materials models for external use.
	- Provide schema-related field enumerations for header and row data.
	- Act as a boundary layer that prevents direct dependency on internal model modules.

Example usage
	# Preferred usage via public package interface:
	from src.models import interfaces as models
	bom = models.CanonicalBom(boards=(board,), is_cost_bom=True)

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.models.interfaces import CanonicalBom
	bom = CanonicalBom(boards=(board,), is_cost_bom=True)

Dependencies
	- Python 3.x
	- Standard Library: None

Notes
	- Only explicitly re-exported symbols are intended for external consumption.
	- Internal model modules are treated as implementation details and may change without notice.
	- This module contains no business logic and exists solely to define and stabilize API boundaries.

License
	- Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from ._bom_v3 import (
    BoardV3,
    BomV3,
    HeaderV3,
    HeaderV3AttrNames,
    RowV3,
    RowV3AttrNames,
)

# noinspection PyProtectedMember
from ._canonical import (
    CanonicalBoard,
    CanonicalBom,
    CanonicalComponent,
    CanonicalHeader,
    CanonicalPart,
)

# Public API surface for this package
__all__ = [
    "BoardV3",
    "BomV3",
    "HeaderV3",
    "HeaderV3AttrNames",
    "RowV3",
    "RowV3AttrNames",
    "CanonicalBoard",
    "CanonicalBom",
    "CanonicalComponent",
    "CanonicalHeader",
    "CanonicalPart",
]
