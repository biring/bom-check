"""
JSON resource cache for shared runtime settings and configuration.

This module centralizes loading of JSON-backed resources (settings, configuration files, message catalogs) from project runtime folders, verifies checksums and required keys, and exposes type-safe cached access to their values.

Example Usage:
    # Preferred usage via package interface:
    from src.common import CacheReadOnly
    cache = CacheReadOnly(
        resource_folder="C://runtime/config",
        resource_name="settings",
        required_keys=("app_version", "log_level"),
    )
    log_level = cache.get_value("log_level", str)

    # Direct internal usage (tests or internal tooling only):
    from src.common._cache_read_only import CacheReadOnly
    cache = CacheReadOnly(
        resource_folder="D://runtime/messages",
        resource_name="log_msg",
        required_keys=("E001",),
    )
    message = cache.get_value("E001", str)

Dependencies:
    - Python >= 3.10
    - Standard Library: copy, typing
    - Internal Packages: src.utils (JSON file I/O, path and checksum helpers)

Notes:
    - Internal-only module; CacheReadOnly is re-exported from src.common for shared settings, configuration, and message catalogs.
    - Intended for read-only JSON resources that are loaded once at startup and reused across the application.
    - get_value enforces the expected type for each key and exposes keys and data via defensive copies.

License:
    - Internal Use Only
"""

__all__ = []  # Internal-only; not part of the public API.

import copy
from typing import Any, TypeVar, Type

from src.utils import file_path
from src.utils import json_io

T = TypeVar("T")  # dictionary value type


def _resolve_json_resource_path(resource_folder: str, resource_name: str) -> str:
    """
    Resolve the absolute path to a JSON resource file.

    Constructs the JSON filename from the logical resource name, enumerates JSON files in the given folder, verifies that the target file exists, and returns its absolute path.

    Args:
        resource_folder (str): Absolute path to the folder containing JSON resource files.
        resource_name (str): Logical file stem without extension (for example, "log_msg").

    Returns:
        str: Absolute filesystem path to the JSON resource file.

    Raises:
        FileNotFoundError: If the folder cannot be inspected or the target resource file does not exist.
    """
    # Build the expected JSON filename from the logical resource name.
    target_filename = resource_name + json_io.JSON_FILE_EXT

    # Discover all JSON files in the target folder.
    available_filenames = file_path.get_files_in_folder(resource_folder, [json_io.JSON_FILE_EXT])

    # Fail fast if the requested resource file is not present.
    if target_filename not in available_filenames:
        raise FileNotFoundError(
            f"JSON resource file '{target_filename}' was not found in folder '{resource_folder}'.")

    # Construct and return the absolute file path
    return file_path.construct_file_path(resource_folder, target_filename)


def _load_json_resource(resource_name: str, resource_path: str) -> dict[str, Any]:
    """
    Load, validate, and extract the payload from a shared JSON resource file.

    Reads the JSON document from disk, verifies the payload checksum stored in metadata, extracts the payload mapping, and ensures that it is not empty.

    Args:
        resource_name (str): Logical resource name used for error reporting.
        resource_path (str): Absolute path to the JSON resource file on disk.

    Returns:
        dict[str, Any]: Mapping of keys to values extracted from the resource payload.

    Raises:
        ValueError: If checksum validation fails or the payload mapping is empty.
    """
    # Load the JSON package
    json_package = json_io.load_json_file(resource_path)

    # Verify integrity of the payload via checksum in meta
    if not json_io.verify_json_payload_checksum(json_package):
        raise ValueError(f"Checksum verification failed for JSON resource '{resource_name}' at '{resource_path}'.")

    # Extract the payload (shallow copy)
    payload = json_io.extract_payload(json_package)

    # Make sure data is not empty
    if not payload:
        raise ValueError(f"JSON resource '{resource_name}' at '{resource_path}' contains an empty payload.")

    return payload


def _assert_required_keys(key_value_map: dict[str, Any], required_keys: tuple[str, ...]) -> None:
    """
    Verify that all required keys are present in a resource payload mapping.

    Compares the expected `required_keys` against the keys in `key_value_map` and raises an error if any required key is missing.

    Args:
        key_value_map (dict[str, Any]): Mapping of payload keys to their values.
        required_keys (tuple[str, ...]): Tuple of keys that must be present in the payload.

    Returns:
        None: This function performs validation only and does not return a value.

    Raises:
        KeyError: If one or more required keys are not present in the mapping.
    """
    # Short-circuit if there is no schema constraint.
    if required_keys:
        # Identify any required keys that are missing from the dictionary
        missing_keys = [key for key in required_keys if key not in key_value_map]

        # If any required keys are missing, raise a KeyError with details
        if missing_keys:
            raise KeyError(f"JSON resource is missing required keys: {missing_keys}.")


def extract_uppercase_keys(globals_dict: dict, allowed_value_type: tuple[type, ...]) -> tuple[str, ...]:
    """
    Extract uppercase constant names from a globals mapping.

    Scans the provided mapping and returns all keys that are fully uppercase and whose associated values match at least one of the allowed types. The result is sorted to ensure stable ordering across environments.

    Args:
        globals_dict (dict): A mapping of names to objects, typically a module-level globals().
        allowed_value_type (tuple[type, ...]): Tuple of permitted value types used to filter constants.

    Returns:
        tuple[str, ...]: A sorted tuple containing all valid uppercase constant names.
    """
    exported_names: list[str] = []

    # Iterate through globals as (name, value) pairs
    for name, value in globals_dict.items():
        # Only include all-uppercase names (conventional constants)
        if name.isupper() and isinstance(value, allowed_value_type):
            exported_names.append(name)

    # Return as a sorted tuple for stable ordering and testability
    return tuple(sorted(exported_names))


class CacheReadOnly:
    """
    Shared JSON resource cache for settings, configuration, and other runtime data.

    Loads a single JSON resource file from the project runtime folders, verifies its checksum, enforces required-key presence, and exposes safe, type-checked access to its values. Used across the application wherever read-only JSON resources are needed.
    """

    def __init__(self, resource_folder: str, resource_name: str, required_keys: tuple[str, ...]) -> None:
        """
        Initialize the cache for a JSON runtime resource.

        Resolves the JSON resource path, loads and validates the JSON package, enforces required-key presence, and stores the resulting payload mapping in memory.

        Args:
            resource_folder (str): Absolute path to the folder containing the JSON resource file.
            resource_name (str): Logical file stem without extension for the resource (for example, "log_msg").
            required_keys (tuple[str, ...]): Keys that must be present in the resource payload.

        Returns:
            None: The cache is initialized in place when construction succeeds.

        Raises:
            ImportError: If the resource cannot be resolved, loaded, or validated; the original exception is attached as the cause.
        """

        # Initialize empty state; will be populated once loading succeeds.
        self._resource_name: str | None = None
        self._resource_path: str | None = None
        self._data_map: dict[str, Any] | None = None

        try:
            # Resolve the JSON resource path based on the runtime folder and logical name.
            resource_file_path = _resolve_json_resource_path(resource_folder, resource_name)

            # Load and validate the payload mapping from disk.
            data = _load_json_resource(resource_name, resource_file_path)

            # Enforce required-key presence before exposing the mapping.
            _assert_required_keys(data, required_keys)

            # Cache the validated resource state for future lookups.
            self._resource_name = resource_name
            self._resource_path = resource_file_path
            self._data_map = data

        except Exception as err:
            raise ImportError(
                f"Failed to initialize shared JSON resource cache for '{resource_name}'."
                f"\n{err}"
            ) from err

    def get_data_map_copy(self) -> dict[str, Any]:
        """
        Return a deep copy of the cached payload mapping.

        The returned dictionary is a defensive copy so that callers can freely mutate it without affecting the internal cache state.

        Returns:
            dict[str, Any]: Deep-copied mapping of all keys to their cached values.
        """
        # Return a deep copy so external mutations cannot corrupt the cache.
        return copy.deepcopy(self._data_map)

    def get_keys(self) -> tuple[str, ...]:
        """
        Return a sorted tuple of keys from the loaded JSON data.

        Returns:
            tuple[str, ...]: Tuple of all keys present in the cached payload mapping.
        """
        # Expose keys as an immutable tuple to prevent accidental modification.
        return tuple(sorted(self._data_map.keys()))

    def get_value(self, key: str, expected: Type[T]) -> T:
        """
        Retrieve a value from the cache and enforce its expected type.

        Looks up the given key in the cached payload mapping and verifies that the associated value is an instance of the expected type before returning it.

        Args:
            key (str): Name of the key to look up in the cached payload.
            expected (Type[T]): Type that the retrieved value is expected to conform to.

        Returns:
            T: The value associated with the key, cast to the expected type.

        Raises:
            TypeError: If `key` is not a string or the retrieved value is not an instance of `expected`.
            KeyError: If the requested key is not present in the cached payload.
        """
        # Enforce that the key identifier is always a string.
        if not isinstance(key, str):
            raise TypeError(f"Cache key must be of type 'str', but got '{type(key).__name__}' instead.")

        # Attempt to retrieve the value associated with the key.
        try:
            value = self._data_map[key]
        except KeyError as err:
            raise KeyError(
                f"Key '{key}' not found in JSON resource; available keys are {sorted(self._data_map.keys())}.") from err

        # Enforce value type
        if not isinstance(value, expected):
            raise TypeError(
                f"Expected value of type '{expected.__name__}' for key '{key}', but got '{type(value).__name__}' instead.")

        return value
