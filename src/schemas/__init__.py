"""
Package initializer for the `schemas` package.

This module defines the public entry point for schema-related constants and label groupings used to identify and reason about supported Excel BOM templates. It exposes a stable façade via the package-level interfaces module while keeping internal schema implementations private and free to evolve.

Key responsibilities
	- Define the supported public import surface for schema-related constants.
	- Restrict access to internal schema modules by exposing only the approved façade.
	- Provide a stable package boundary for schema version identifiers and label groupings.

Example usage
	Preferred usage via public package interface
	from src.schemas import interfaces as schema
	identifiers = schema.TEMPLATE_IDENTIFIERS_V3

	Direct module usage (acceptable in unit tests or internal scripts only)
	Not Applicable. This is an internal module.

Dependencies
	- Python 3.10
	- Standard Library: None

Notes
	- This module contains no schema definitions or business logic.
	- Callers should treat the package-level interfaces module as the sole supported API.
	- Internal module names and layouts are not part of the public contract and may change without notice.

License
	Internal Use Only
"""

__all__ = ["interfaces"]
