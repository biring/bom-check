"""
Facade module exposing the public command-line interface surface.

This module provides a stable import boundary for command-line interactions by re-exporting selected functionality from internal components, allowing internal structure changes without impacting external consumers.

Key Responsibilities:
	- Re-export user interaction and display functions from internal modules
	- Define and enforce the public API surface via explicit export declarations
	- Serve as a stable facade to decouple external usage from internal structure

Example Usage:
	# Preferred usage via public package interface:
	from src.cli import interfaces as console
	choice = console.prompt_menu_selection(["Scan", "Parse", "Report"])

	# Direct module usage (acceptable in unit tests or internal scripts only):
	Not applicable. Use public package interface

Dependencies:
	- Python version: >= 3.10
	- Standard Library:

Notes:
	- Acts as the public API boundary for command-line interactions
	- Internal modules may change without notice as long as this interface remains stable
	- Designed to remain thin and avoid embedding business or formatting logic

License:
	- Internal Use Only
"""

# noinspection PyProtectedMember
from ._show import (
    show_error,
    show_header,
    show_info,
    show_log,
    show_success,
    show_warning,
)
# noinspection PyProtectedMember
from ._prompt import (
    prompt_menu_selection,
    prompt_for_string_value,
)

# Define exactly what is public interface.
__all__ = [
    # from prompt module
    "prompt_menu_selection",
    "prompt_for_string_value",
    # from show module
    "show_error",
    "show_header",
    "show_info",
    "show_log",
    "show_success",
    "show_warning",
]
