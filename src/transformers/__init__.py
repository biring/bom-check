"""
Package initializer for the transformers package.

This module defines the public surface of the transformers package by restricting exports to a single approved façade module. It establishes a stable import boundary so callers interact only with supported transformation-layer functionality while internal modules remain private and free to evolve.

Key responsibilities
	- Define the public API of the transformers package.
	- Constrain star-import behavior to an explicitly approved façade.
	- Isolate callers from internal module layout and implementation changes.

Example usage
	# Preferred usage via public package interface:
	from src.transformers import interfaces as transformers
	output = transformers.canonical_to_v3_template_sheets(canonical_bom, template_df)

	# Direct module usage (acceptable in unit tests or internal scripts only):
	# Not applicable. This module should be accessed through the package-level façade.

Dependencies
	- Python 3.x
	- Standard Library: None

Notes
	- This module contains no executable logic.
	- All transformation functionality is accessed through the exposed façade module.
	- Internal modules are intentionally excluded from the public API and may change without notice.

License
	- Internal Use Only
"""

__all__ = ["interfaces"]
