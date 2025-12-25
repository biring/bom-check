"""
Package initializer for the mappers package.

This package provides the public façade for BOM mapping workflows. All supported mapping operations are exposed through the interfaces module, while internal implementation modules remain private and free to evolve.

Example Usage:
    # Preferred usage via package-level façade:
    from src.mappers import interfaces as mapper
    canonical_bom = mapper.map_v3_to_canonical_bom(fixed_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Only symbols re-exported by this package are considered part of the supported API.
    - Callers must import mapping functions via src.mappers.interfaces.
    - Internal modules may change without notice.
    - Mapping assumes validated and normalized BOM inputs from prior pipeline stages.

License:
    - Internal Use Only
"""

__all__ = ["interfaces"]