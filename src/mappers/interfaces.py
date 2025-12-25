"""
Public interface façade for the mappers package.

This module defines the stable, approved import surface for BOM mapping operations. It re-exports mapping functions implemented in internal modules so that callers are insulated from internal file structure and refactors.

Example Usage:
    # Preferred usage via public package interface:
    from src.mappers import interfaces as mapper
    canonical_bom = mapper.map_v3_to_canonical_bom(fixed_bom)

    # Direct module usage (acceptable in unit tests only):
    # Not applicable. Use public package interface.

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - Internal Packages: src.mappers._v3_to_canonical

Notes:
    - This module contains no business logic.
    - All implementation details live in private modules prefixed with an underscore.
    - Callers should import mapping functions exclusively through this interface to preserve API stability.
    - Internal modules may change without notice; this interface is the contract boundary.

License:
    - Internal Use Only
"""

# Re-export approved API functions from internal modules
# noinspection PyProtectedMember
from ._v3_to_canonical import map_v3_to_canonical_bom

__all__ = [
    "map_v3_to_canonical_bom",
]
