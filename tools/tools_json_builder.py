"""
Build JSON file metadata for use by the application.

This tool:
  - Discovers target JSON source files within the project
  - Validates that each JSON file contains a well-formed key/value mapping payload
  - Wraps the payload with metadata, including SHA-256 checksum
  - Produces exit codes suitable for CI/build and packaging pipelines

Typical uses:
  - Regenerating metadata and checksums after manual edits
  - Verifying structural validity of JSON assets before release

Behavior:
  - Input files must be valid JSON. Invalid JSON will raise during load.
  - JSON directory must already exist; this tool does not create directories.
  - If existing JSON file payload checksum is valid, updates to the file are skipped.
  - If existing JSON file is unreadable/invalid, an error is generated and script aborted

Exit codes:
  -  0  — all files processed successfully
  - -1  — one or more files failed to generate

Example Usage:
    # Preferred usage via package/module import:
    Not applicable. Not for use with other modules.

    # Direct CLI usage from the repository root:
    python tools/tools_json_builder.py

Dependencies:
  - Python >= 3.10
  - Standard Library: sys, dataclasses, pathlib, json, hashlib
  - Internal Modules: project utilities for file discovery and JSON I/O

Notes:
  - Intended for internal build-time use only; not part of the public application API.
  - Input JSON files must already exist; this tool does not create directories.
  - Payloads must be JSON objects. Other values are rejected.
  - If an existing JSON file already contains a valid checksum and unchanged payload, regeneration is skipped.
  - Console output is optimized for CI logs and developer visibility.


License:
 - Internal Use Only
"""

import sys
from dataclasses import dataclass

from src.utils import folder_path as folder
from src.utils import file_path as file
from src.utils import json_io as json

from src.lookups.interfaces import (
    BOARD_SUPPLIER_CODES_FOLDER_PARTS,
    BOARD_SUPPLIER_CODES_RESOURCE_NAME,
    COMPONENT_TYPE_FOLDER_PARTS,
    COMPONENT_TYPE_RESOURCE_NAME,
)
from src.settings import application as app_settings


@dataclass(frozen=True)
class FileLocation:
    """
    Immutable descriptor for a JSON lookup file location.

    Defines the folder path, filename components, and extension needed to resolve the full file path relative to the project root.

    Args:
        folder_parts (tuple[str, ...]): Folder path segments under the project root.
        file_stem (str): Core filename without prefix or extension.
        file_extension (str): File extension including the leading dot.

    Returns:
        FileLocation: A frozen dataclass describing a JSON lookup file.

    Raises:
        None
    """
    folder_parts: tuple[str, ...]
    file_stem: str
    file_extension: str


# CONSTANTS
SUCCESS: int = 0
FAILURE: int = -1
TARGET_JSON_FILES: tuple[FileLocation, ...] = (
    FileLocation(app_settings.FOLDER_PARTS, app_settings.RESOURCE_NAME, json.JSON_FILE_EXT),
    FileLocation(BOARD_SUPPLIER_CODES_FOLDER_PARTS, BOARD_SUPPLIER_CODES_RESOURCE_NAME, json.JSON_FILE_EXT),
    FileLocation(COMPONENT_TYPE_FOLDER_PARTS, COMPONENT_TYPE_RESOURCE_NAME, json.JSON_FILE_EXT),
)


def main() -> int:
    """
    Generate JSON metadata for all configured lookup files.

    Resolves the project root, iterates over the configured file locations, validates existing JSON files, regenerates checksum metadata when needed, and reports overall success via a process-friendly exit code.


    Returns:
        int: SUCCESS (0) if all files are processed successfully, FAILURE (-1) if any file fails.

    Raises:
        None: All exceptions are handled internally and reflected in the returned status code.
    """
    project_root = folder.resolve_project_folder()

    overall_success = True

    print(f"🛠️ Generating JSON files from project location {project_root}")

    for target in TARGET_JSON_FILES:

        print(f"- - 🧪 Processing {target.file_stem}")
        try:
            # Compose full path for the configured JSON target
            file_name = target.file_stem + target.file_extension
            folder_path = folder.construct_folder_path(project_root, target.folder_parts)
            file_path = file.construct_file_path(folder_path, file_name)

            # Verify file name
            file.assert_file_name(file_path, (json.JSON_FILE_EXT,))

            # Verify file folder exists
            if not folder.is_folder_path(folder_path):
                # Do not auto-create folders; this is a build-time invariant
                raise RuntimeError(f"File folder missing: {folder_path}. This tool does not create directories.")

            # Verify source file exists
            file.assert_file_path(file_path)

            # Try to load existing package; skip regeneration when checksum matches
            payload_map = None
            try:
                json_package = json.load_json_file(file_path)
                payload_map = json.extract_payload(json_package)
                if json.verify_json_payload_checksum(json_package):
                    print(f"- - ⏭️ Skipping {target.file_stem}. No change detected.")
                    continue
            except FileNotFoundError:
                # No prior file: proceed to create
                pass
            except RuntimeError as ex:
                # Can not load file
                raise RuntimeError(f"Invalid JSON. Reason: {ex}")
            except Exception as ex:
                # Corrupt/unexpected JSON
                raise RuntimeError(f"JSON invalid at {file_path}. {type(ex).__name__}: {ex}")

            # Persist the new JSON package with metadata and checksum
            payload = json.create_json_packet(payload_map, file_name)
            try:
                json.save_json_file(file_path, payload, indent_spaces=4)
                print(f"- - ✅ Updated {target.file_stem}.")
            except Exception as ex:
                raise RuntimeError(f"JSON write failed at {file_path}. {type(ex).__name__}: {ex}")

        except Exception as ex:
            print(f'- - ⚠️ Error processing {target.file_stem}. {type(ex).__name__}: {ex}', file=sys.stderr)
            overall_success = False

    if overall_success:
        print("🎉 All runtime JSON files generated successfully.")
    else:
        print("❌ Some files failed to generate. See errors above.", file=sys.stderr)

    return SUCCESS if overall_success else FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
