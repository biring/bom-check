"""
Tests for the public helper interfaces that expose metadata and record access.

This module verifies that the public façade provides callable entry points for metadata and record handling, and that these interfaces can be instantiated and exercised on a happy path using tabular data. The tests focus on construction, basic read operations, and basic write operations, asserting only return types and successful invocation without errors.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/helpers/test_interfaces.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- In-memory pandas DataFrame instances are created in setUp to represent metadata tables and record tables.
	- DataFrames are copied before being passed to the system under test to avoid shared state across tests.
	- No temporary files or directories are created.
	- No explicit cleanup is required beyond test case teardown.

Dependencies
	- Python 3.x
	- Standard Library: unittest

Notes
	- Tests validate only the public façade surface by resolving attributes dynamically and asserting basic callability and return types.
	- Assertions do not validate the contents of returned data structures, only their types.
	- Tests rely on pandas DataFrame behavior and assume in-memory operations without filesystem or external service interaction.

License
	Internal Use Only
"""

import unittest
import pandas as pd

from src.helpers import interfaces


class TestInterfaces(unittest.TestCase):
    """
    Unit tests verifying the public façade exposes and allows using Metadata and Record.
    """

    def setUp(self) -> None:
        # ARRANGE
        self.metadata_df = pd.DataFrame(
            [
                ["Project", "Apollo"],
                ["Owner", "Engineering"],
                ["Release Date", "2026-03-15"],
            ]
        )
        self.template_identifiers = ("Project",)
        self.label_offsets = {
            "Project": (0, 1),
            "Owner": (0, 1),
            "Release Date": (0, 1),
        }

        self.records_df = pd.DataFrame(
            [
                ["ID", "Name", "Country"],
                [1, "Jane", "USA"],
                [2, "Lars", "SE"],
            ]
        )
        self.title_identifiers = ("id", "name")

    def test_metadata_instantiation(self) -> None:
        """
        Should construct Metadata via the public façade.
        """
        # ARRANGE
        metadata_cls = getattr(interfaces, "Metadata", None)

        # ACT
        instance = metadata_cls(
            df=self.metadata_df.copy(),
            template_identifiers=self.template_identifiers,
        )  # type: ignore[misc,operator]

        # ASSERT
        with self.subTest("callable_exists", Act=callable(metadata_cls), Exp=True):
            self.assertTrue(callable(metadata_cls))
        with self.subTest("instance_type", Act=type(instance), Exp=metadata_cls):
            self.assertIsInstance(instance, metadata_cls)

    def test_metadata_read(self) -> None:
        """
        Should read metadata via the public façade and return a dict on the happy path.
        """
        # ARRANGE
        metadata_cls = getattr(interfaces, "Metadata", None)
        meta = metadata_cls(
            df=self.metadata_df.copy(),
            template_identifiers=self.template_identifiers,
        )  # type: ignore[misc,operator]

        # ACT
        result = meta.read_metadata(dict(self.label_offsets))

        # ASSERT
        with self.subTest("read_return_type", Act=type(result), Exp=dict):
            self.assertIsInstance(result, dict)

    def test_metadata_write(self) -> None:
        """
        Should write metadata via the public façade and return None on the happy path.
        """
        # ARRANGE
        metadata_cls = getattr(interfaces, "Metadata", None)
        meta = metadata_cls(
            df=self.metadata_df.copy(),
            template_identifiers=self.template_identifiers,
        )  # type: ignore[misc,operator]
        new_values = {
            "Project": "Zeus",
            "Owner": "Platform",
            "Release Date": "2027-01-01",
        }

        # ACT
        result = meta.write_metadata(dict(self.label_offsets), new_values)

        # ASSERT
        with self.subTest("write_return_type", Act=result, Exp=None):
            self.assertIsNone(result)

    def test_record_instantiation(self) -> None:
        """
        Should construct Record via the public façade.
        """
        # ARRANGE
        record_cls = getattr(interfaces, "Record", None)

        # ACT
        instance = record_cls(
            df=self.records_df.copy(),
            title_identifiers=self.title_identifiers,
        )  # type: ignore[misc,operator]

        # ASSERT
        with self.subTest("callable_exists", Act=callable(record_cls), Exp=True):
            self.assertTrue(callable(record_cls))
        with self.subTest("instance_type", Act=type(instance), Exp=record_cls):
            self.assertIsInstance(instance, record_cls)

    def test_record_read(self) -> None:
        """
        Should read a record via the public façade and return a dict on the happy path.
        """
        # ARRANGE
        record_cls = getattr(interfaces, "Record", None)
        rec = record_cls(
            df=self.records_df.copy(),
            title_identifiers=self.title_identifiers,
        )  # type: ignore[misc,operator]
        rec.reset_read()

        # ACT
        result = rec.read_record(0, labels=("id", "name", "country"), strict=True)

        # ASSERT
        with self.subTest("read_return_type", Act=type(result), Exp=dict):
            self.assertIsInstance(result, dict)

    def test_record_write(self) -> None:
        """
        Should write a record via the public façade and return an int on the happy path.
        """
        # ARRANGE
        record_cls = getattr(interfaces, "Record", None)
        rec = record_cls(
            df=self.records_df.copy(),
            title_identifiers=self.title_identifiers,
        )  # type: ignore[misc,operator]
        new_record = {"id": 3, "name": "Mika", "country": "FI"}

        # ACT
        result = rec.write_record(new_record)

        # ASSERT
        with self.subTest("write_return_type", Act=type(result), Exp=int):
            self.assertIsInstance(result, int)


if __name__ == "__main__":
    unittest.main()
