"""
Public interface façade for the helpers package.

This module defines a stable, curated public API for helper functionality by re-exporting approved helper types while encapsulating internal module structure. It exists to provide a consistent import surface so that internal organization can evolve without impacting callers.

Key responsibilities
	- Expose a stable public façade for helper-related functionality.
	- Re-export approved helper types from internal modules.
	- Prevent direct dependency on internal helper module paths.

Example usage
	# Preferred usage via public package interface:
	from src.helpers.interfaces import Metadata
	meta = Metadata(df, ("Part Number", "Revision"))

	# Direct module usage (acceptable in unit tests or internal scripts only):
	# Not applicable. This module is intended to be accessed via the package interface.

Dependencies
	- Python 3.x
	- Standard Library: None

Notes
	- This module contains no executable logic and serves only as an import façade.
	- The public API surface is explicitly defined and intentionally minimal.
	- Internal helper modules are considered non-public and may change without notice.

License
	- Internal Use Only
"""

# This module intentionally contains no executable logic.
# Its sole responsibility is to act as a stable façade so callers do not depend on internal module paths.
# All imports below are deliberate re-exports that define the supported public API surface.

# noinspection PyProtectedMember
# Importing from a protected internal module is intentional here.
# The façade pattern centralizes and freezes the public contract while allowing internal refactors.
from .dataframes._df_metadata import Metadata

# noinspection PyProtectedMember
# Same rationale as above; Record is an approved public type despite its internal location.
from .dataframes._df_records import Record

# __all__ explicitly defines the public symbols exported by this module.
# This prevents accidental exposure of internal names and documents the supported API for consumers.
__all__ = [
    "Metadata",
    "Record",
]
