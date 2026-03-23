"""
Public interface façade for the `fixer` package.

This module re-exports curated BOM field-fixer functions for BOM fix workflows while keeping underlying logic encapsulated. It defines the public entry points for BOM correction workflows while keeping underlying logic encapsulated.

Example Usage:
    # Preferred usage via package interface:
    from src.fixer import interfaces as fixer
    fixed_bom, change_log = fixer.v3_bom(raw_bom)

    # Direct internal usage (acceptable in tests only):
    from src.fixer import interfaces as fixer
    fixed_bom, change_log = fixer.v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - External Packages: None

Notes:
    - Provides a stable import target; internal module layout may evolve without breaking callers.
    - Internal modules remain non-public to callers; this façade re-exports approved functions.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API

# noinspection PyProtectedMember
from ._v3_bom import (
    fix_v3_bom,
)

__all__ = [
    "fix_v3_bom",
]
