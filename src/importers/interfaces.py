"""
Public interface façade for the `importers` package.

This module exposes the approved, stable import API for callers. It re-exports file import implemented in internal modules, ensuring that internal structure may evolve without breaking imports.

Example Usage:
    # Preferred usage via package interface:
    from src.importers import interfaces as import
    excel_dict = importer.read_excel_as_dict("C:\\Data\\Inputs.xlsx")


    # Direct internal usage (acceptable in tests only):
    import src.importers._excel_file.py as excel # not recommended for production use
    excel_dict = excel.read_excel_as_dict("C:\\Data\\Inputs.xlsx")

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - Internal Modules: ._excel_file.py

Notes:
    - Serves as the single public import location for all menu interactions.
    - Internal modules remain non-public and may change without notice.


License:
    - Internal Use Only
"""

# Re-export approved API functions from internal modules
# noinspection PyProtectedMember
from ._excel_file import (
    EXCEL_FILE_TYPES,
    read_excel_as_dict,
    load_version3_bom_template,
)

__all__ = [
    "EXCEL_FILE_TYPES",
    "load_version3_bom_template",
    "read_excel_as_dict",
]
