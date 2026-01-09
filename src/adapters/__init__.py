"""
Package initializer for the adapters package.

This module defines the public surface of the adapters package by restricting exports to the supported façade module. It exists to provide a stable, intentional import boundary so callers interact only with approved adapter-layer functionality while internal modules remain private and free to change.

Key responsibilities
	- Define the public API of the adapters package.
	- Limit star-import behavior to explicitly approved façade modules.
	- Shield callers from internal module structure.

Example usage
	# Preferred usage via public package interface:
	from src.adapters import interfaces as adapter
	bom_header = adapter.map_template_v3_header_to_bom_v3_header(template_header)

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.adapters import interfaces as adapter
	bom_header = adapter.map_template_v3_header_to_bom_v3_header(template_header)

Dependencies
	- Python 3.x
	- Standard Library: None

Notes
	- This module contains no executable logic.
	- All adapter functionality is accessed through the exposed façade module.
	- Internal modules should not be imported directly by external callers.

License
	- Internal Use Only
"""

__all__ = ["interfaces"]
