"""
Board supplier code lookup loader for BOM cleaning and normalization.

This module provides internal, read-only access to a board supplier codes lookup resource used during BOM cleaning, correction, and normalization workflows. The lookup data is resolved from project runtime resources, loaded lazily on first access, cached for the lifetime of the process, and always returned as a defensive copy to preserve immutability and prevent shared state mutation.

Key Responsibilities:
	- Resolve the project resource folder containing the board supplier codes lookup data.
	- Lazily load and cache a JSON-based lookup resource exactly once per interpreter lifetime.
	- Normalize cache construction failures into a runtime-level error for callers.
	- Return a defensive copy of the lookup mapping to all callers.

Example Usage:
	# Preferred usage via public package interface.
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only).
	from src.lookups import _board_supplier_codes as bsc
	codes = bsc.get_board_supplier_codes_lookup_table()

Dependencies:
	- Python version: 3.10+
	- Standard Library: typing

Notes:
	- This module is internal-only and intentionally exports no public symbols.
	- Lookup data is treated as immutable runtime configuration and cached after the first successful load.
	- Structural schema validation is intentionally disabled; successful loading is considered sufficient for this lookup.
	- All callers receive a defensive copy to avoid accidental mutation of shared cached data.
	- Cache initialization is not synchronized and assumes single-threaded first access or benign duplicate initialization.

License:
	Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.


from typing import Final, Any

from src.common import CacheReadOnly
from src.utils import folder_path

# MODULE CONSTANTS

# Relative folder components locating the lookup JSON resource within the project.
# This is intentionally a tuple to guarantee immutability and safe reuse across calls.
BOARD_SUPPLIER_CODES_FOLDER_PARTS: tuple[str, ...] = ("src", "resources", "lookups",)

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
        RuntimeError: When the underlying lookup resource cannot be resolved, loaded, or validated during initial cache construction.
    """
    global _cache

    # Perform lazy initialization to avoid filesystem access and JSON parsing unless the lookup is actually needed at runtime.
    if _cache is None:
        # Resolve the absolute resource folder path at call time to respect the active project root and any environment-specific resolution logic.
        resource_folder = folder_path.construct_folder_path(
            base_path=folder_path.resolve_project_folder(),
            subfolders=BOARD_SUPPLIER_CODES_FOLDER_PARTS,
        )

        try:
            # CacheReadOnly enforces immutability guarantees and performs schema checks.
            # Any exception here indicates either a missing resource, invalid JSON, or a violation of required_keys constraints.
            _cache = CacheReadOnly(
                resource_folder=resource_folder,
                resource_name=BOARD_SUPPLIER_CODES_RESOURCE_NAME,
                required_keys=_REQUIRED_KEYS,
            )
        except Exception as original_exception:
            # Normalize all cache-construction failures into a RuntimeError
            raise RuntimeError(
                f"Failed to load board supplier codes lookup '{BOARD_SUPPLIER_CODES_RESOURCE_NAME}' from resource folder '{resource_folder}'."
                f"\n{original_exception}"
            ) from original_exception

    # Always return a defensive copy to ensure callers cannot mutate shared cached state.
    return _cache.get_data_map_copy()
