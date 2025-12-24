"""
Public interface for the `models` package.

This module acts as a stable façade that re-exports selected dataclasses and field definitions from internal model implementations. External consumers must import from this module instead of referencing internal files directly, allowing internal structure to evolve without breaking API contracts.

Exposed capabilities:
    - Raw Version 3 BOM models (Board, Bom, Header, Row)
    - Canonical BOM models used for export and downstream processing
    - Header and row field enumerations for schema-aware logic

Example Usage:
    # Preferred usage via public package interface:
    from src.models import interfaces as models
    bom = models.CanonicalBom(boards=(board,), is_cost_bom=True)

    # Direct internal usage (acceptable in tests only):
    # Not applicable. Use public package interface.

Dependencies:
    - Python >= 3.10

Notes:
    - Only symbols listed in __all__ are considered part of the public API.
    - Internal modules (_v3_raw, _canonical, _v3_fields) must not be imported directly.
    - This module contains no logic; it exists solely to define API boundaries.
    - Canonical models are immutable and assume prior validation upstream.

License:
    - Internal Use Only
"""

# Re-export selected API from internal modules to expose as public API
# noinspection PyProtectedMember
from ._v3_fields import (
    HeaderFields,
    RowFields,
)
# noinspection PyProtectedMember
from ._v3_raw import (
    Board,
    Bom,
    Header,
    Row
)
# noinspection PyProtectedMember
from ._canonical import (
    CanonicalBom,
    CanonicalBoard,
    CanonicalHeader,
    CanonicalPart,
    CanonicalComponent,
)

__all__ = [
    'HeaderFields',
    'RowFields',

    'CanonicalBom',
    'CanonicalBoard',
    'CanonicalHeader',
    'CanonicalPart',
    'CanonicalComponent',

    'Board',
    'Bom',
    'Header',
    'Row',
]
