"""
Package initializer for the `fixers` package.

Exposes only the `interfaces` submodule at package level to enforce a clean, stable façade for consumers. This prevents direct imports from internal modules and ensures future refactors do not break external code.

Example Usage:
    # Preferred usage via package interface:
    from src.fixers import interfaces as fixer
    fixed_bom, change_log = fixer.v3_bom(raw_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None

Notes:
    - `__all__` explicitly restricts exports to the `interfaces` façade.
    - Internal modules are not part of the public API and may change without notice.

License:
    - Internal Use Only
"""

__all__ = ["interfaces"]
