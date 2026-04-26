"""
Component type lookup loader for BOM parsing and normalization.

This module provides internal, read-only access to a component type lookup resource used during BOM parsing, correction, and validation workflows. The lookup data is resolved from runtime resources, loaded lazily on first access, cached for the lifetime of the process, and returned as a defensive copy to preserve immutability and prevent shared state mutation.

Key Responsibilities:
	- Resolve runtime resource paths for component type lookup data based on execution mode
	- Lazily load and cache a JSON-based lookup resource for process-wide reuse
	- Normalize initialization and loading failures into runtime-level errors
	- Provide defensive copies of lookup data to prevent mutation of shared state

Example Usage:
	# Preferred usage via public package interface:
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.lookups import _component_type as ct
	table = ct.get_component_type_lookup_table()

Dependencies:
	- Python version: 3.10+
	- Standard Library: typing

Notes:
	- This module is internal-only and not part of the public API surface
	- Lookup data is treated as immutable runtime configuration and cached after initial load
	- Structural validation is intentionally disabled; successful loading is considered sufficient
	- Cache initialization is not synchronized and may execute multiple times under concurrent access
	- All callers receive a defensive copy to avoid mutation of shared cached data

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

from typing import Final, Any

from src.common import CacheReadOnly
from src.utils import app_mode
from src.utils import folder_path

# MODULE CONSTANTS
# Relative folder components locating the lookup JSON resource in non-executable mode
COMPONENT_TYPE_FOLDER_PARTS: Final[tuple[str, ...]] = ("src", "resources", "lookups",)
# Relative folder components locating the lookup JSON resource in executable mode.
_COMPONENT_TYPE_FOLDER_PARTS_EXE: Final[tuple[str, ...]] = ("resources", "lookups",)

# Name of the JSON resource file
COMPONENT_TYPE_RESOURCE_NAME: Final[str] = "component_type"
# Define required schema keys for settings validation
_REQUIRED_KEYS: Final[tuple[str, ...]] = ()

# MODULE VARIABLES
# Lazily initialized cache for the shared application settings instance.
_cache: CacheReadOnly | None = None


def get_component_type_lookup_table() -> dict[str, Any]:
    """
    Return a defensive copy of the component type lookup table.

    Lazily initializes a process-wide read-only cache for the component type JSON resource on first access. The cache is constructed once per interpreter lifetime and reused for subsequent calls. All callers receive a defensive copy to prevent mutation of shared runtime configuration.

    Returns:
        dict[str, Any]: Component type lookup mapping.

    Raises:
        RuntimeError: If the lookup resource cannot be loaded or validated, or if the application mode is unsupported.
    """
    global _cache  # Ensure mutation of module-level cache shared across all callers

    # Lazily initialize cache to avoid unnecessary filesystem access and JSON parsing
    if _cache is None:

        # Determine runtime mode and resolve correct base path and subfolder structure
        # Invariant: APP_MODE must match a supported mode; fail fast otherwise
        if app_mode.APP_MODE == app_mode.APP_MODE.DEVELOPMENT or app_mode.APP_MODE == app_mode.APP_MODE.UNITTEST:
            # Development mode resolves resources relative to project root
            resource_base_path = folder_path.resolve_project_folder()
            resource_subfolders = COMPONENT_TYPE_FOLDER_PARTS

        elif app_mode.APP_MODE == app_mode.APP_MODE.EXECUTABLE:
            # Executable mode resolves resources relative to packaged executable location
            resource_base_path = folder_path.resolve_exe_folder()
            resource_subfolders = _COMPONENT_TYPE_FOLDER_PARTS_EXE

        else:
            # Explicitly reject unsupported modes to prevent silent misconfiguration
            raise RuntimeError(f"Application mode {app_mode.APP_MODE} not supported")

        # Construct absolute resource folder path using resolved base path and subfolders
        # Assumption: construct_folder_path handles correct path joining and normalization
        resource_folder_path = folder_path.construct_folder_path(
            base_path=resource_base_path,
            subfolders=resource_subfolders,
        )

        try:
            # Initialize read-only cache:
            # - Loads JSON resource
            # - Applies schema validation if required (disabled via empty required_keys)
            # - Maintains immutable internal state
            _cache = CacheReadOnly(
                resource_folder=resource_folder_path,
                resource_name=COMPONENT_TYPE_RESOURCE_NAME,
                required_keys=_REQUIRED_KEYS,
            )
        except Exception as load_exception:
            # Normalize all initialization failures into RuntimeError for consistent caller handling
            raise RuntimeError(
                f"Failed to load component type lookup '{COMPONENT_TYPE_RESOURCE_NAME}' from resource folder '{resource_folder_path}'."
                f"\n{load_exception}"
            ) from load_exception

    # Always return a defensive copy to ensure callers cannot mutate shared cached state
    return _cache.get_data_map_copy()
