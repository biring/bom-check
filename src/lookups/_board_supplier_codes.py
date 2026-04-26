"""
Board supplier code lookup loader for BOM cleaning and normalization.

This module provides internal, read-only access to a board supplier codes lookup resource used during BOM cleaning, correction, and normalization workflows. The lookup data is resolved from project runtime resources, loaded lazily on first access, cached for the lifetime of the process, and always returned as a defensive copy to preserve immutability and prevent shared state mutation.

Key Responsibilities:
	- Resolve the project resource folder containing the board supplier codes lookup data
	- Lazily load and cache a JSON-based lookup resource for reuse across the process lifetime
	- Normalize initialization failures into runtime-level errors for consistent caller handling
	- Provide callers with a defensive copy of the lookup mapping

Example Usage:
	# Preferred usage via public package interface:
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.lookups import _board_supplier_codes as bsc
	codes = bsc.get_board_supplier_codes_lookup_table()

Dependencies:
	- Python version: 3.10+
	- Standard Library: typing

Notes:
	- Intended for internal use within lookup and normalization workflows
	- Lookup data is treated as immutable runtime configuration and cached after initial load
	- Structural validation is intentionally disabled; successful loading is considered sufficient
	- Cache initialization is not synchronized and may execute more than once under concurrent access
	- All returned data is a defensive copy to prevent shared state mutation

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.


from typing import Final, Any

from src.common import CacheReadOnly
from src.utils import app_mode
from src.utils import folder_path

# MODULE CONSTANTS

# Relative folder components locating the lookup JSON resource in non-executable mode.
# This is intentionally a tuple to guarantee immutability and safe reuse across calls.
BOARD_SUPPLIER_CODES_FOLDER_PARTS: tuple[str, ...] = ("src", "resources", "lookups",)

# Relative folder components locating the lookup JSON resource in executable.
# This is intentionally a tuple to guarantee immutability and safe reuse across calls.
_BOARD_SUPPLIER_CODES_FOLDER_PARTS_EXE: tuple[str, ...] = ("resources", "lookups",)

# Logical resource name passed to CacheReadOnly for JSON resolution.
# The absence of a file extension implies that CacheReadOnly owns extension resolution semantics.
BOARD_SUPPLIER_CODES_RESOURCE_NAME: Final[str] = "board_supplier_codes"

# Required schema keys for validation.
# An empty tuple explicitly documents that structural validation is intentionally disabled and that mere loadability is considered sufficient for this lookup.
_REQUIRED_KEYS: tuple[str, ...] = ()

# MODULE STATE

# Lazily initialized, process-wide cache instance.
# This is intentionally module-scoped to guarantee a single load per interpreter lifetime.
_cache: CacheReadOnly | None = None


def get_board_supplier_codes_lookup_table() -> dict[str, Any]:
    """
    Return a defensive copy of the board supplier codes lookup table.

    Lazily initializes a process-wide read-only cache for the board supplier codes JSON resource on first access. The cache is constructed exactly once per interpreter lifetime and reused for subsequent calls. All callers receive a defensive copy of the cached mapping to enforce immutability boundaries and prevent mutation of shared runtime configuration.

    Returns:
        dict[str, Any]: Mapping of board supplier codes as loaded from the JSON resource.

    Raises:
        RuntimeError: When the underlying lookup resource cannot be resolved, loaded, or validated during initial cache construction, or when the application mode is unsupported.
    """
    global _cache  # Explicitly reference module-level cache to enforce single shared instance

    # Perform lazy initialization to defer filesystem access and JSON parsing until first actual use
    if _cache is None:

        # Determine runtime mode to resolve correct resource base path and subfolder structure
        # Invariant: Exactly one supported mode must match; otherwise fail fast
        if app_mode.APP_MODE == app_mode.APP_MODE.DEVELOPMENT or app_mode.APP_MODE == app_mode.APP_MODE.UNITTEST:
            # Development mode resolves resources relative to project root
            base_path = folder_path.resolve_project_folder()
            subfolders = BOARD_SUPPLIER_CODES_FOLDER_PARTS

        elif app_mode.APP_MODE == app_mode.APP_MODE.EXECUTABLE:
            # Executable mode resolves resources relative to packaged executable location
            base_path = folder_path.resolve_exe_folder()
            subfolders = _BOARD_SUPPLIER_CODES_FOLDER_PARTS_EXE

        else:
            # Explicitly reject unsupported modes to avoid silent misconfiguration
            raise RuntimeError(f"Application mode {app_mode.APP_MODE} not supported")

        # Construct absolute path to the resource folder using resolved base path and subfolder components
        # Assumption: folder_path.construct_folder_path enforces correct path joining semantics
        resource_folder = folder_path.construct_folder_path(
            base_path=base_path,
            subfolders=subfolders,
        )

        try:
            # Initialize read-only cache which:
            # - Loads JSON resource
            # - Optionally validates schema (disabled here via empty required_keys)
            # - Stores immutable internal representation
            _cache = CacheReadOnly(
                resource_folder=resource_folder,
                resource_name=BOARD_SUPPLIER_CODES_RESOURCE_NAME,
                required_keys=_REQUIRED_KEYS,
            )
        except Exception as original_exception:
            # Normalize all initialization failures into a RuntimeError for consistent caller handling
            # This includes file not found, invalid JSON, or schema violations
            raise RuntimeError(
                f"Failed to load board supplier codes lookup '{BOARD_SUPPLIER_CODES_RESOURCE_NAME}' from resource folder '{resource_folder}'."
                f"\n{original_exception}"
            ) from original_exception

    # Always return a defensive copy to prevent mutation of shared cached state
    # Invariant: Callers must never receive a direct reference to internal cache data
    return _cache.get_data_map_copy()
