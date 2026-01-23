"""
Package initializer for the helpers package.

This module defines the public package boundary for helper-related functionality by exposing only a single façade submodule. It enforces a clean separation between public imports and internal implementation details so that internal helpers can evolve without breaking dependent code.

Key responsibilities
	- Define the public API surface of the helpers package.
	- Restrict package-level exports to a single façade module.
	- Prevent accidental reliance on internal helper modules.

Example usage
	# Preferred usage via public package interface:
	from src.helpers.interfaces import Metadata
	meta = Metadata(df, ("Part Number", "Revision"))

	# Direct module usage (acceptable in unit tests or internal scripts only):
	# Not applicable. This package should be accessed through its façade.

Dependencies
	- Python 3.x
	- Standard Library: None

Notes
	- This module contains no executable logic beyond defining exported symbols.
	- The restricted __all__ list documents and enforces the supported public API.
	- Internal helper modules are considered non-public and may change without notice.

License
	- Internal Use Only
"""

__all__ = ["interfaces"]
