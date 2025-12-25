"""
Centralized dependency imports for the mapper package.

This module exists solely to provide a stable patch seam for non-stdlib dependencies used by mapper modules. All external imports are re-exported here to simplify interface-level testing and patching.

Example Usage:
    # Patched indirectly via interface tests:
    from src.mappers import _dependencies as dep
    patch.object(dep.verify, "v3_bom", side_effect=RuntimeError("Verify failed")):

Dependencies:
    - Python >= 3.10
    - Internal Packages:
        - src.models.interfaces
        - src.utils.timestamp

Notes:
    - This module must contain imports only.
    - No logic or behavior should be added.
    - Changes here affect patch paths used by interface tests.

License:
    - Internal Use Only
"""

from src.utils import parser
from src.verifiers import interfaces as verify

