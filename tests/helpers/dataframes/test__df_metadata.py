"""
Unit tests validating offset-based metadata access against a labeled tabular template.

This test module exercises read and write behavior for a metadata-oriented DataFrame wrapper that relies on labeled anchor cells and relative offsets. The tests verify correct resolution of anchors, handling of duplicate labels, strict versus non-strict error behavior, bounds checking, and row extension when writing values beyond the current table height, using an in-memory tabular fixture.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/helpers/dataframes/test__df_metadata.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- An in-memory tabular dataset is constructed during setup and reused across tests.
	- Required template identifiers and label-to-offset mappings are defined as shared test inputs.
	- Some tests copy the backing table to isolate mutations caused by write operations.
	- No filesystem access, temporary directories, or external resources are used, and no explicit cleanup is required.

Dependencies
	- Python 3.x
	- Standard Library: unittest

Notes
	- Tests rely on deterministic first-occurrence resolution of labeled anchor cells using a full table scan.
	- Both strict and non-strict modes are exercised to validate raising and non-raising behavior for missing labels and out-of-bounds offsets.
	- Assertions compare string values directly and assume string-based cell contents in the fixture.
	- Some expectations depend on concrete row counts or preservation of the backing table object, which may be sensitive to internal implementation changes.

License
	- Internal Use Only
"""

from __future__ import annotations

import unittest
import pandas as pd

# noinspection PyProtectedMember
from src.helpers.dataframes._df_metadata import Metadata  # module under test


class TestMetadata(unittest.TestCase):
    """
    Unit tests verifying offset-based read/write behavior for the Metadata wrapper.
    """

    def setUp(self) -> None:
        # ARRANGE: Shared fixture for tests
        self.df = pd.DataFrame(
            [
                ["TEMPLATE ID", "", ""],
                ["", "", ""],
                ["Model Number", "SN-12345", ""],
                ["Build Stage", "", "EVT"],
                ["Build Date", "", ""],
                ["2025-01-10", "", ""],
            ]
        )
        self.template_identifiers = ("templateid",)
        self.label_offsets = {
            "Model Number": (0, 1),
            "Build Stage": (0, 2),
            "Build Date": (1, 0),
        }

    def test_happy_path(self):
        """
        Should initialize when required template identifiers are present in the DataFrame.
        """
        # ARRANGE
        df = self.df
        identifiers = self.template_identifiers

        # ACT
        meta = Metadata(df=df, template_identifiers=identifiers)

        # ASSERT
        with self.subTest("df_identity", Act=meta.df, Exp=df):
            self.assertIs(meta.df, df)
        with self.subTest("template_identifiers", Act=meta.template_identifiers, Exp=identifiers):
            self.assertEqual(meta.template_identifiers, identifiers)

    def test_empty_identifiers(self):
        """
        Should raise ValueError when no template identifiers are provided.
        """
        # ARRANGE
        df = self.df
        identifiers: tuple[str, ...] = ()

        # ACT
        with self.assertRaises(ValueError) as cm:
            Metadata(df=df, template_identifiers=identifiers)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=ValueError):
            self.assertIs(type(cm.exception), ValueError)

    def test_missing_identifier(self):
        """
        Should raise ValueError when any required template identifier is missing from the DataFrame.
        """
        # ARRANGE
        df = self.df
        identifiers = ("missing_template_identifier",)

        # ACT
        with self.assertRaises(ValueError) as cm:
            Metadata(df=df, template_identifiers=identifiers)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=ValueError):
            self.assertIs(type(cm.exception), ValueError)

    def test_normalized_identifier_match(self):
        """
        Should accept identifiers that match DataFrame labels via normalized comparison.
        """
        # ARRANGE
        df = self.df
        identifiers = ("  template id  ",)

        # ACT
        meta = Metadata(df=df, template_identifiers=identifiers)

        # ASSERT
        with self.subTest("normalized_identifiers", Act=meta.template_identifiers, Exp=identifiers):
            self.assertEqual(meta.template_identifiers, identifiers)

    def test_read_metadata_happy_path(self):
        """
        Should read expected values using offsets relative to the first occurrence of each label.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)

        # ACT
        result = meta.read_metadata(label_offsets)

        # ASSERT
        expected = {"Model Number": "SN-12345", "Build Stage": "EVT", "Build Date": "2025-01-10"}
        with self.subTest(Act=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_read_metadata_missing_label_lenient(self):
        """
        Should return empty strings for missing labels when strict is False.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = {**self.label_offsets, "Does Not Exist": (0, 1)}

        # ACT
        result = meta.read_metadata(label_offsets, strict=False)

        # ASSERT
        with self.subTest("present_label", Act=result["Model Number"], Exp="SN-12345"):
            self.assertEqual(result["Model Number"], "SN-12345")
        with self.subTest("missing_label", Act=result["Does Not Exist"], Exp=""):
            self.assertEqual(result["Does Not Exist"], "")

    def test_read_metadata_missing_label_strict(self):
        """
        Should raise KeyError for missing labels when strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = {"Does Not Exist": (0, 1)}

        # ACT
        with self.assertRaises(KeyError) as cm:
            meta.read_metadata(label_offsets)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=KeyError):
            self.assertIs(type(cm.exception), KeyError)

    def test_read_metadata_out_of_bounds_positive_lenient(self):
        """
        Should return empty strings for out-of-bounds offsets when strict is False.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = {"Model Number": (0, 99), "Build Stage": (0, 2)}

        # ACT
        result = meta.read_metadata(label_offsets, strict=False)

        # ASSERT
        with self.subTest("out_of_bounds_label", Act=result["Model Number"], Exp=""):
            self.assertEqual(result["Model Number"], "")
        with self.subTest("in_bounds_label", Act=result["Build Stage"], Exp="EVT"):
            self.assertEqual(result["Build Stage"], "EVT")

    def test_read_metadata_out_of_bounds_positive_strict(self):
        """
        Should raise IndexError for out-of-bounds offsets when strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = {"Build Date": (99, 0)}

        # ACT
        with self.assertRaises(IndexError) as cm:
            meta.read_metadata(label_offsets)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=IndexError):
            self.assertIs(type(cm.exception), IndexError)

    def test_read_metadata_out_of_bounds_negative_lenient(self):
        """
        Should return empty strings for negative out-of-bounds offsets when strict is False.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = {"Model Number": (0, -1)}

        # ACT
        result = meta.read_metadata(label_offsets, strict=False)

        # ASSERT
        with self.subTest(Act=result["Model Number"], Exp=""):
            self.assertEqual(result["Model Number"], "")

    def test_read_metadata_out_of_bounds_negative_strict(self):
        """
        Should raise IndexError for negative out-of-bounds offsets when strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df, template_identifiers=self.template_identifiers)
        label_offsets = {"Model Number": (0, -1)}

        # ACT
        with self.assertRaises(IndexError) as cm:
            meta.read_metadata(label_offsets)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=IndexError):
            self.assertIs(type(cm.exception), IndexError)

    def test_read_metadata_duplicate_label_first_occurrence(self):
        """
        Should use the first occurrence of a duplicated label as the anchor.
        """
        # ARRANGE
        df = pd.DataFrame([["TEMPLATE ID", "", ""], ["Model Number", "FIRST", ""], ["Model Number", "SECOND", ""]])
        meta = Metadata(df=df, template_identifiers=self.template_identifiers)
        label_offsets = {"Model Number": (0, 1)}

        # ACT
        result = meta.read_metadata(label_offsets)

        # ASSERT
        with self.subTest(Act=result["Model Number"], Exp="FIRST"):
            self.assertEqual(result["Model Number"], "FIRST")

    def test_write_metadata_happy_path(self):
        """
        Should write values to the resolved target cells when labels and offsets are provided.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_values = {"Model Number": "SN-99999", "Build Stage": "DVT", "Build Date": "2026-01-14"}

        # ACT
        meta.write_metadata(label_offsets, label_values)

        # ASSERT
        with self.subTest("model_number", Act=meta.df.iat[2, 1], Exp="SN-99999"):
            self.assertEqual(meta.df.iat[2, 1], "SN-99999")
        with self.subTest("build_stage", Act=meta.df.iat[3, 2], Exp="DVT"):
            self.assertEqual(meta.df.iat[3, 2], "DVT")
        with self.subTest("build_date", Act=meta.df.iat[5, 0], Exp="2026-01-14"):
            self.assertEqual(meta.df.iat[5, 0], "2026-01-14")

    def test_write_metadata_missing_label_lenient(self):
        """
        Should skip writes for missing labels when strict is False.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = {**self.label_offsets, "Does Not Exist": (0, 1)}
        label_values = {"Does Not Exist": "X", "Build Stage": "PVT"}

        # ACT
        meta.write_metadata(label_offsets, label_values, strict=False)

        # ASSERT
        with self.subTest("present_label_written", Act=meta.df.iat[3, 2], Exp="PVT"):
            self.assertEqual(meta.df.iat[3, 2], "PVT")
        with self.subTest("shape_unchanged", Act=meta.df.shape, Exp=self.df.shape):
            self.assertEqual(meta.df.shape, self.df.shape)

    def test_write_metadata_missing_label_strict(self):
        """
        Should raise KeyError for missing labels when strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = {**self.label_offsets, "Does Not Exist": (0, 1)}
        label_values = {"Does Not Exist": "X"}

        # ACT
        with self.assertRaises(KeyError) as cm:
            meta.write_metadata(label_offsets, label_values)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=KeyError):
            self.assertIs(type(cm.exception), KeyError)

    def test_write_metadata_no_offset_lenient(self):
        """
        Should skip writes when no offset is provided and strict is False.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_values = {"Model Number": "SN-00000"}
        del label_offsets["Model Number"]

        # ACT
        meta.write_metadata(label_offsets, label_values, strict=False)

        # ASSERT
        with self.subTest(Act=meta.df.iat[2, 1], Exp="SN-12345"):
            self.assertEqual(meta.df.iat[2, 1], "SN-12345")

    def test_write_metadata_no_offset_strict(self):
        """
        Should raise KeyError when no offset is provided and strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_values = {"Model Number": "SN-00000"}
        del label_offsets["Model Number"]

        # ACT
        with self.assertRaises(KeyError) as cm:
            meta.write_metadata(label_offsets, label_values)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=KeyError):
            self.assertIs(type(cm.exception), KeyError)

    def test_write_metadata_out_of_bounds_column_lenient(self):
        """
        Should skip writes for out-of-bounds column targets when strict is False.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_offsets["Model Number"] = (0, 99)
        label_values = {"Model Number": "SN-00000", "Build Stage": "DVT"}

        # ACT
        meta.write_metadata(label_offsets, label_values, strict=False)

        # ASSERT
        with self.subTest("skipped_out_of_bounds", Act=meta.df.iat[2, 1], Exp="SN-12345"):
            self.assertEqual(meta.df.iat[2, 1], "SN-12345")
        with self.subTest("in_bounds_written", Act=meta.df.iat[3, 2], Exp="DVT"):
            self.assertEqual(meta.df.iat[3, 2], "DVT")

    def test_write_metadata_out_of_bounds_column_strict(self):
        """
        Should raise IndexError for out-of-bounds column targets when strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_offsets["Model Number"] = (0, 99)
        label_values = {"Model Number": "SN-00000"}

        # ACT
        with self.assertRaises(IndexError) as cm:
            meta.write_metadata(label_offsets, label_values)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=IndexError):
            self.assertIs(type(cm.exception), IndexError)

    def test_write_metadata_out_of_bounds_negative_strict(self):
        """
        Should raise IndexError for negative out-of-bounds targets when strict is True.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_offsets["Model Number"] = (0, -1)
        label_values = {"Model Number": "SN-00000"}

        # ACT
        with self.assertRaises(IndexError) as cm:
            meta.write_metadata(label_offsets, label_values)

        # ASSERT
        with self.subTest("exception_type", Act=type(cm.exception), Exp=IndexError):
            self.assertIs(type(cm.exception), IndexError)

    def test_write_metadata_row_expansion_strict_true(self):
        """
        Should extend rows as needed to satisfy target row indexes.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        original_cols = meta.df.shape[1]
        label_offsets = dict(self.label_offsets)
        # Make target row far past end to force expansion
        label_offsets["Build Date"] = (10, 0)
        label_values = {"Build Date": "2099-12-31"}

        # ACT
        meta.write_metadata(label_offsets, label_values)

        # ASSERT
        # Expected final written row index = original anchor row + 10.
        with self.subTest("row_count_grows", Act=meta.df.shape[0] >= 15, Exp=True):
            self.assertTrue(meta.df.shape[0] >= 15)
        with self.subTest("column_count_preserved", Act=meta.df.shape[1], Exp=original_cols):
            self.assertEqual(meta.df.shape[1], original_cols)
        with self.subTest("written_value", Act=meta.df.iat[14, 0], Exp="2099-12-31"):
            self.assertEqual(meta.df.iat[14, 0], "2099-12-31")

    def test_round_trip_write_then_read(self):
        """
        Should return written values when reading back using the same offsets.
        """
        # ARRANGE
        meta = Metadata(df=self.df.copy(), template_identifiers=self.template_identifiers)
        label_offsets = dict(self.label_offsets)
        label_values = {"Model Number": "SN-ABCDE", "Build Stage": "PVT", "Build Date": "2030-06-01"}

        # ACT
        meta.write_metadata(label_offsets, label_values)
        read_back = meta.read_metadata(label_offsets)

        # ASSERT
        with self.subTest(Act=read_back, Exp=label_values):
            self.assertEqual(read_back, label_values)


if __name__ == "__main__":
    unittest.main()
