"""
Public interface façade for the `exporters` package.

This module exposes the approved, stable import API for callers. It re-exports file import implemented in internal modules, ensuring that internal structure may evolve without breaking imports.

Example Usage:
    # Preferred usage via package interface:
    from src.exporters import interfaces as export
    file_name = export.build_checker_log_file_name(Bom)

    # Direct internal usage (acceptable in tests only):
    # Not applicable. Use public package interface.

Dependencies:
    - Python >= 3.10
    - Standard Library: None

Notes:
	- This module contains no business logic and exists solely as a façade over internal exporter modules.
	- Only the names re-exported here should be considered part of the supported public API.
	- Internal modules may change without notice as long as this façade contract is preserved.
	- Import-time failures will surface directly if internal modules or their dependencies are missing or renamed.


License:
    - Internal Use Only
"""

# Re-export approved API functions from internal modules

# noinspection PyProtectedMember
from ._build_filename import (
    LogTypes,
    build_checker_log_filename,
    generate_log_filename,
)

# noinspection PyProtectedMember
from ._text_file import (
    write_text_file_lines,
)

# noinspection PyProtectedMember
from ._excel_file import (
    write_excel_sheets,
)

__all__ = [
    LogTypes,
    "build_checker_log_filename",
    generate_log_filename,
    "write_text_file_lines",
    "write_excel_sheets",
]
