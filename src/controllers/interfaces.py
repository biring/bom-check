"""
Public interface façade for controller menu construction and discovery.

This module exposes a stable and supported import surface for controller-related workflows by re-exporting selected capabilities from internal implementation modules, insulating callers from internal structure while preserving a consistent API.

Key Responsibilities:
	- Provide a stable public import surface for controller menu construction
	- Re-export approved controller discovery and menu-building functionality
	- Decouple external callers from internal module organization

Example Usage:
	# Preferred usage via public package interface:
	from src.controllers import interfaces as controller
	menu_options, actions = controller.build_controller_menu()

	# Direct module usage (acceptable in unit tests or internal scripts only):
	Not applicable. Use public package interface

Dependencies:
	- Python version: >= 3.10
	- Standard Library: None

Notes:
	- Acts as a façade over internal modules to enforce controlled API exposure
	- Limits public access strictly to supported and stable functionality

License:
	- Internal Use Only
"""

# Re-export approved API functions from internal modules

# noinspection PyProtectedMember
from ._menu_builder import build_controller_menu

__all__ = [
    "build_controller_menu",
]
