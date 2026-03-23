"""
Public interface for the `cleaners` package.

This module exposes stable entry points for BOM cleaning workflows by re-exporting curated helpers from internal modules. It defines the external API boundary for higher-level packages (parsers, validators, reports).

Example Usage:
    # Preferred usage via package interface:
    from src.cleaners import interfaces as cleaners
    cleaned_bom, change_log = cleaners.v3_bom(raw_bom)

    # Direct internal usage (acceptable in tests only):
    from src.cleaners import interfaces as cleaners
    cleaned_bom, change_log = cleaners.v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None (re-export only)
    - External Packages: None

Notes:
    - Serves as the public façade; internal module layout may change without breaking imports.
    - Only a curated subset is exported via __all__; private symbols remain internal.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from ._v3_bom import (
    clean_v3_bom,
)

__all__ = [
    "clean_v3_bom",
]
