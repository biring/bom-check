"""
Public interface façade for canonical model export transformations package.

This module defines the stable, approved import surface for converting canonical domain models into export-ready formats. It re-exports transformation functions implemented in private modules so that callers are insulated from internal file structure, implementation details, and future refactors as additional output formats are introduced.

Key responsibilities:
	- Expose a stable public API for canonical-to-output format transformations.
	- Re-export approved transformation functions from internal implementation modules.
	- Act as a contract boundary between callers and evolving internal exporters.

Example usage:
	# Preferred usage via public package interface
	from src.transformers import interfaces as transformers
	output = transformers.canonical_to_v3_template_sheets(canonical_bom, template_df)

	# Direct module usage (acceptable in unit tests or internal scripts only)
    # Not applicable. Use public package interface.


Dependencies:
    - Python >= 3.10
    - Standard Library: None

Notes:
    - This module contains no business logic.
    - All implementation details live in private modules prefixed with an underscore.
    - Callers should import mapping functions exclusively through this interface to preserve API stability.
    - Internal modules may change without notice; this interface is the contract boundary.

License:
    - Internal Use Only
"""

# Re-export approved API functions from internal implementation modules.
# The protected-member import is intentional and constrained: this module acts as the contract boundary, and only explicitly approved symbols are surfaced to callers to preserve long-term API stability.

# noinspection PyProtectedMember
from ._canonical_to_v3_template import (
    canonical_to_v3_template_sheets,
)

# __all__ explicitly defines the supported public API surface.
# Any symbol not listed here is considered private and may change or be removed without notice.
__all__ = [
    "canonical_to_v3_template_sheets",
]
