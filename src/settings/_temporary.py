"""
JSON-backed temporary settings stored in the application temp folder.

This module provides:
    - Strongly typed keys for temporary settings used across workflows
    - A JSON cache–based loader (CacheReadWrite) for reading and persisting the temporary settings file
    - A lazy singleton accessor for internal components that require shared temp state

These settings are intended for short-lived, workflow-level state such as last-used source and destination folders, without touching user-facing configuration files.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable. This module is internal.

    # Direct module usage (allowed in tests or internal scripts):
    from src.settings import _temporary as tmp
    cache = tmp.get_temp_settings()
    cache.update_value(tmp.KEYS.DESTINATION_FILES_FOLDER, "/path/out")

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - External Packages: None
    - Internal Modules: src.common.CacheReadWrite, src.utils.folder_path

Notes:
    - This module is internal to the settings subsystem; it is not part of the public API.
    - Required keys are defined at import time and enforced when creating or loading the JSON file.
    - If the backing JSON is missing or invalid, CacheReadWrite creates a new file populated with the default values defined in _DEFAULT_TEMP_SETTINGS.
    - A singleton cache is exposed via get_temp_settings() to minimize disk I/O.
"""

__all__ = [
    "get_temp_settings",
    "KEYS",
]

from dataclasses import dataclass, asdict
from typing import Any, Final

from src.common import CacheReadWrite
from src.utils import folder_path


@dataclass(frozen=True)
class _TemporarySettingsKeys:
    """
    Strongly-typed container defining JSON key names for temporary settings.

    Each field maps directly to a JSON key stored within the temporary settings payload.

    Args:

    Returns:
        _TemporarySettingsKeys: A dataclass instance containing constant key strings.

    Raises:
        None
    """
    DESTINATION_FILES_FOLDER: str = "DESTINATION_FILES_FOLDER"
    SOURCE_FILES_FOLDER: str = "SOURCE_FILES_FOLDER"


# Single instance used throughout this module
KEYS: Final[_TemporarySettingsKeys] = _TemporarySettingsKeys()

# REQUIRED_KEYS drives cache schema validation; values are the JSON key names.
_REQUIRED_KEYS: Final[tuple[str, ...]] = tuple(sorted(asdict(KEYS).values()))

# Default values for each temporary setting
_DEFAULT_TEMP_SETTINGS: Final[dict[str, Any]] = {
    KEYS.DESTINATION_FILES_FOLDER: folder_path.resolve_drive_letter(),
    KEYS.SOURCE_FILES_FOLDER: folder_path.resolve_drive_letter(),
}

_TEMP_FILE_NAME: Final[str] = "temporary_settings"

# Lazily initialized cache for the shared temporary settings instance. This is intentionally module-global so all callers see a consistent view of temp state.
_temporary_settings_cache: CacheReadWrite | None = None


def get_temp_settings() -> CacheReadWrite:
    """
    Retrieve the singleton temporary settings cache.

    The first call constructs a CacheReadWrite instance for the temporary settings; subsequent calls return the same cached instance.

    Returns:
        CacheReadWrite: The shared singleton instance for temporary settings.

    Raises:
        RuntimeError: If the cache cannot be initialized.
    """

    global _temporary_settings_cache

    if _temporary_settings_cache is None:
        try:
            _temporary_settings_cache = CacheReadWrite(
                resource_folder_path=folder_path.get_temp_folder(),
                resource_name=_TEMP_FILE_NAME,
                required_keys=_REQUIRED_KEYS,
                default_values=_DEFAULT_TEMP_SETTINGS,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize the temporary settings.\n{exc}"
            ) from exc

    return _temporary_settings_cache
