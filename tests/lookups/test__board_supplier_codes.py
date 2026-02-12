"""
Unit tests for validating retrieval, error handling, and caching behavior of the board supplier codes lookup table.

This module verifies that the lookup table loader returns the expected mapping when a valid runtime JSON resource is present, raises a RuntimeError when underlying cache construction fails, and protects internal cached state by returning a defensive copy to callers. Tests simulate the runtime resource layout using a temporary project root and controlled patching to isolate filesystem and cache behavior.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/lookups/test__board_supplier_codes.py
	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- Creates an isolated temporary project root directory for each test case using a unique temporary folder.
	- Constructs the expected runtime directory structure beneath the temporary root.
	- Writes a single JSON resource file containing a wrapped data packet representing lookup contents.
	- Patches project root resolution to redirect filesystem lookups into the temporary directory.
	- Reloads the module under test before each test to reset module-level cached state.
	- Removes the temporary project root and all generated files during teardown using recursive deletion.

Dependencies:
	- Python 3.10+ (uses PEP 604 union type syntax for annotations).
	- Standard Library: importlib, shutil, tempfile, unittest, unittest.mock

Notes:
	- Tests rely on real filesystem I/O within temporary directories to emulate the runtime resource layout.
	- Module-level caching behavior is reset between tests via explicit module reload to maintain isolation.
	- Error handling is validated by asserting the raised exception type name rather than its message content.
	- Defensive copy behavior is verified by mutating a returned mapping and asserting subsequent calls return the original data.

License:
	Internal Use Only
"""


import importlib
import shutil
import tempfile
import unittest
from unittest.mock import patch

from src.utils import (
    file_path,
    folder_path,
    json_io,
)

# noinspection PyProtectedMember
from src.lookups import _board_supplier_codes as bsc  # Module under test


class TestGetBoardSupplierCodesLookupTable(unittest.TestCase):
    """
    Unit tests verifying retrieval and caching behavior of the board supplier codes lookup table.
    """

    TEST_JSON_DATA = {
        "Boolean": True,
        "Number": -100,
        "Float": 99.99,
        "String": "Hello",
        "List": ["1", "2"],
    }

    tmp_project_root: str | None = None

    def setUp(self):
        """
        Prepare a temporary project root and write a single component-type JSON packet.
        """
        # Reload module to reset the module-level cache to None
        importlib.reload(bsc)

        # Create an isolated project root; removed in tearDown()
        self.tmp_project_root = tempfile.mkdtemp(prefix="bom_check_board_supplier_lookup_test_")

        # Mirror the on-disk runtime layout used by production code
        runtime_dir = folder_path.construct_folder_path(
            self.tmp_project_root,
            bsc.BOARD_SUPPLIER_CODES_FOLDER_PARTS,
        )
        folder_path.create_folder_if_missing(runtime_dir)

        # Build resource file paths and names
        resource_filename = bsc.BOARD_SUPPLIER_CODES_RESOURCE_NAME + json_io.JSON_FILE_EXT
        resource_path = file_path.construct_file_path(runtime_dir, resource_filename)

        # Wrap the payload in the standard packet envelope expected by the loader
        resource_packet = json_io.create_json_packet(
            self.TEST_JSON_DATA,
            source_file=resource_filename,
        )

        # Persist the packet where CacheReadOnly will look for it
        json_io.save_json_file(resource_path, resource_packet)

    def tearDown(self):
        """
        Remove the temporary project root and all generated files.
        """
        # Best-effort cleanup to avoid leaking temp files on test failures
        if self.tmp_project_root is not None:
            shutil.rmtree(self.tmp_project_root, ignore_errors=True)

    def test_happy_path(self):
        """
        Should return a dictionary of board supplier code mappings when the runtime resource is valid.
        """
        # ARRANGE
        expected_map = self.TEST_JSON_DATA

        # Force CacheReadOnly to resolve its root under the temporary project root
        patch_target = bsc.folder_path
        patch_attribute = patch_target.resolve_project_folder.__name__
        with patch.object(patch_target, patch_attribute) as p_root:
            p_root.return_value = self.tmp_project_root

            # ACT
            actual_map = bsc.get_board_supplier_codes_lookup_table()

        # ASSERT
        with self.subTest(Out=actual_map, Exp=expected_map):
            self.assertDictEqual(actual_map, expected_map)

    def test_raise(self):
        """
        Should raise RuntimeError when the underlying lookup cache construction fails.
        """
        # ARRANGE
        expected_error = RuntimeError.__name__

        # Replace CacheReadOnly with a stub that always raises an error
        patch_target = bsc
        patch_attribute = patch_target.CacheReadOnly.__name__
        with patch.object(patch_target, patch_attribute) as mock_cache_ctor:
            mock_cache_ctor.side_effect = ValueError("boom")

            # ACT
            try:
                _ = bsc.get_board_supplier_codes_lookup_table()
                actual_error = ""
            except Exception as exc:  # noqa: BLE001
                actual_error = type(exc).__name__

        # ASSERT
        with self.subTest(Out=actual_error, Exp=expected_error):
            self.assertEqual(actual_error, expected_error)

    def test_defensive_copy(self):
        """
        Should return a defensive copy so caller mutation does not affect cached data.
        """
        # ARRANGE
        expected_map = self.TEST_JSON_DATA

        patch_target = bsc.folder_path
        patch_attribute = patch_target.resolve_project_folder.__name__
        with patch.object(patch_target, patch_attribute) as p_root:
            p_root.return_value = self.tmp_project_root

            # ACT
            first_map = bsc.get_board_supplier_codes_lookup_table()
            # Mutate the returned mapping
            first_map["Injected"] = "X"
            second_map = bsc.get_board_supplier_codes_lookup_table()

        # ASSERT
        with self.subTest(Out=second_map, Exp=expected_map):
            self.assertDictEqual(second_map, expected_map)


if __name__ == "__main__":
    unittest.main()
