"""
Unit tests validating row-oriented record reading and writing against a pandas DataFrame with an irregular title layout.

This test module exercises record-style access over a DataFrame where the title row is discovered by matching identifying titles rather than fixed position, and where data rows may be sparse or separated by blank rows. The tests verify schema resolution, deterministic read bounds, value normalization to strings, and append behavior relative to the resolved title row.

Example Usage
	# Preferred usage via project-root invocation:
	python -m unittest tests/helpers/dataframes/test__df_records.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test data and fixtures
	- In-memory pandas DataFrame fixtures constructed inline with intentionally irregular layouts including noise rows, blank columns, trailing blank rows, and title only cases.
	- No filesystem interaction, temporary directories, or external resources are used.
	- Each test constructs a fresh DataFrame or uses a defensive copy to avoid shared state.

Dependencies
	- Python 3.x
	- Standard Library: unittest, typing

Notes
	- Tests rely on deterministic schema resolution based on normalized titles located at construction time.
	- Record indexing is asserted to be 0-based and strictly relative to the resolved title row.
	- Tests assume string coercion for all returned cell values.
	- Several assertions access internal schema state to validate resolved mappings and title ordering.
	- The underlying DataFrame is mutated during append tests and re-read via explicit reset calls.

License
	- Internal Use Only
"""
from typing import Tuple, Any

import unittest
import pandas as pd

# noinspection PyProtectedMember
from src.helpers.dataframes._df_records import Record  # Implementation under test


class TestRecord(unittest.TestCase):
    """
    Unit tests verifying row-oriented record read/write behavior over a pandas DataFrame.
    """

    def setUp(self) -> None:
        # ARRANGE
        # Common DataFrame fixture used by multiple tests. Intentionally irregular layout:
        # Row 0: noise
        # Row 1: title row (non-adjacent titles, blank columns)
        # Row 2: record 0
        # Row 3: record 1
        # Row 4: trailing blank row (should not count as a record)
        self.df = pd.DataFrame(
            [
                ["noise", "", "junk", None, "ignore", ""],
                ["", " Name ", "", "City", " AGE ", ""],
                ["", "Alice", "", "NYC", 30, ""],
                ["", "Bob", "", "LA", 25, ""],
                ["", "", "", "", "", ""],
            ]
        )
        self.title_identifiers_happy: Tuple[str, ...] = ("age", "name")  # deliberately out of order
        self.title_identifiers_empty: Tuple[str, ...] = ()
        self.title_identifiers_missing: Tuple[str, ...] = ("City", "missing")

    def test_happy_path(self) -> None:
        """
        Should construct Record and derive schema for non-sequential titles with blank columns.
        """
        # ARRANGE
        df = self.df
        ids = self.title_identifiers_happy

        # ACT
        rec = Record(df=df, title_identifiers=ids)

        # ASSERT
        with self.subTest("title_row", Act=rec._schema.title_row, Exp=1):
            self.assertEqual(rec._schema.title_row, 1)

        expected_title_to_col = {"name": 1, "age": 4, "city": 3}
        for key, expected_col in expected_title_to_col.items():
            with self.subTest(f"title_to_col[{key}]", Act=rec._schema.title_to_col.get(key), Exp=expected_col):
                self.assertEqual(rec._schema.title_to_col.get(key), expected_col)

        with self.subTest("titles_original", Act=rec._schema.titles_original, Exp=["Name", "City", "AGE"]):
            self.assertEqual(rec._schema.titles_original, ["Name", "City", "AGE"])

    def test_empty_identifiers(self) -> None:
        """
        Should raise an error when title identifiers is empty.
        """
        # ARRANGE
        df = self.df
        ids: Tuple[str, ...] = self.title_identifiers_empty
        expected_type = ValueError.__name__

        # ACT
        try:
            Record(df=df, title_identifiers=ids)
            actual: Any = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

    def test_non_dataframe(self) -> None:
        """
        Should raise an error when df is not a pandas.DataFrame.
        """
        # ARRANGE
        not_a_df: Any = "not-a-dataframe"
        ids = self.title_identifiers_happy
        expected_type = TypeError.__name__

        # ACT
        try:
            Record(df=not_a_df, title_identifiers=ids)  # type: ignore[arg-type]
            actual: Any = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

    def test_missing_identifiers(self) -> None:
        """
        Should raise an error when required title identifiers cannot be located.
        """
        # ARRANGE
        df = self.df
        ids = self.title_identifiers_missing
        expected_type = ValueError.__name__

        # ACT
        try:
            Record(df=df, title_identifiers=ids)
            actual: Any = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

    def test_reset_read_returns_number_of_available_records(self) -> None:
        """
        Should return the count of populated record rows below the title row when reset_read() is called.
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)

        # ACT
        count = rec.reset_read()

        # ASSERT
        with self.subTest(Act=count, Exp=2):
            self.assertEqual(count, 2)

    def test_read_record_is_relative_to_title_row(self) -> None:
        """
        Should read records using a 0-based index relative to the title row and coerce values to strings.
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)
        rec.reset_read()

        # ACT
        r0 = rec.read_record(0, labels=("name", "age", "city"), strict=True)
        r1 = rec.read_record(1, labels=("name", "age", "city"), strict=True)

        # ASSERT
        with self.subTest("r0_name", Act=r0["name"], Exp="Alice"):
            self.assertEqual(r0["name"], "Alice")
        with self.subTest("r0_age", Act=r0["age"], Exp="30"):
            self.assertEqual(r0["age"], "30")
        with self.subTest("r0_city", Act=r0["city"], Exp="NYC"):
            self.assertEqual(r0["city"], "NYC")

        with self.subTest("r1_name", Act=r1["name"], Exp="Bob"):
            self.assertEqual(r1["name"], "Bob")
        with self.subTest("r1_age", Act=r1["age"], Exp="25"):
            self.assertEqual(r1["age"], "25")
        with self.subTest("r1_city", Act=r1["city"], Exp="LA"):
            self.assertEqual(r1["city"], "LA")

    def test_read_record_out_of_bounds_after_reset_read(self) -> None:
        """
        Should raise an error when attempting to read past the cached record count after reset_read().
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)
        count = rec.reset_read()
        expected_type = IndexError.__name__
        with self.subTest("initial_count", Act=count, Exp=2):
            self.assertEqual(count, 2)

        # ACT
        try:
            rec.read_record(2)
            actual: Any = ""
        except Exception as e:
            actual = e

        # ASSERT
        actual_type = type(actual).__name__
        with self.subTest("Error", Exp=expected_type, Act=actual_type):
            self.assertEqual(expected_type, actual_type)

        actual_args = getattr(actual, "args", ())
        with self.subTest("Message string is not empty"):
            self.assertTrue(bool(actual_args) and str(actual_args[0]) != "")

    def test_write_record_appends_under_last_filled_row(self) -> None:
        """
        Should append a new record under the last non-blank record row and return its record-relative index.
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)

        # ACT
        new_idx = rec.write_record({"name": "Cara", "age": 41, "city": "Boston"})
        total = rec.reset_read()
        r2 = rec.read_record(2, labels=("name", "age", "city"), strict=True)

        # ASSERT
        with self.subTest("new_idx", Act=new_idx, Exp=2):
            self.assertEqual(new_idx, 2)
        with self.subTest("total_after_append", Act=total, Exp=3):
            self.assertEqual(total, 3)
        with self.subTest("name", Act=r2["name"], Exp="Cara"):
            self.assertEqual(r2["name"], "Cara")
        with self.subTest("age", Act=r2["age"], Exp="41"):
            self.assertEqual(r2["age"], "41")
        with self.subTest("city", Act=r2["city"], Exp="Boston"):
            self.assertEqual(r2["city"], "Boston")

    def test_labels_none_returns_all_fields(self) -> None:
        """
        Should return all fields using titles_original when labels is None.
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)
        rec.reset_read()

        # ACT
        full = rec.read_record(0, labels=None)

        # ASSERT
        expected_keys = rec._schema.titles_original
        with self.subTest("keys", Act=list(full.keys()), Exp=expected_keys):
            self.assertEqual(list(full.keys()), expected_keys)
        for k, v in full.items():
            with self.subTest(f"value_type_for_{k}", Act=type(v), Exp=str):
                self.assertIsInstance(v, str)

    def test_missing_label_non_strict_returns_empty_string(self) -> None:
        """
        Should return empty string for unknown labels when strict=False.
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)
        rec.reset_read()

        # ACT
        out = rec.read_record(0, labels=("name", "nonexistent"), strict=False)

        # ASSERT
        with self.subTest("known_label", Act=out["name"], Exp="Alice"):
            self.assertEqual(out["name"], "Alice")
        with self.subTest("unknown_label_empty", Act=out["nonexistent"], Exp=""):
            self.assertEqual(out["nonexistent"], "")

    def test_write_non_strict_skips_unknown_labels(self) -> None:
        """
        Should skip unknown labels when write_record is called with strict=False and still write known fields.
        """
        # ARRANGE
        rec = Record(df=self.df.copy(), title_identifiers=self.title_identifiers_happy)

        # ACT
        new_idx = rec.write_record({"name": "Dara", "age": 29, "extra_field": "ignored"}, strict=False)
        rec.reset_read()
        row = rec.read_record(2, labels=("name", "age", "city"), strict=True)

        # ASSERT
        with self.subTest("new_idx", Act=new_idx, Exp=2):
            self.assertEqual(new_idx, 2)
        with self.subTest("name_written", Act=row["name"], Exp="Dara"):
            self.assertEqual(row["name"], "Dara")
        with self.subTest("age_written", Act=row["age"], Exp="29"):
            self.assertEqual(row["age"], "29")

    def test_title_only_no_data_rows_returns_zero(self) -> None:
        """
        Should return zero records when the title row is the last DataFrame row (no data rows exist).
        """
        # ARRANGE
        df_title_only = pd.DataFrame([["", "PN", "Qty"]])
        df_title_only.iloc[0, 1] = "Part Number"
        df_title_only.iloc[0, 2] = "Quantity"
        rec = Record(df=df_title_only, title_identifiers=("part number", "quantity"))

        # ACT
        count = rec.reset_read()

        # ASSERT
        with self.subTest("no_data_rows_count", Act=count, Exp=0):
            self.assertEqual(count, 0)

    def test_ensure_row_exists_grows_dataframe_on_append(self) -> None:
        """
        Should grow the underlying DataFrame when appending beyond current bounds.
        """
        # ARRANGE
        df_title_only = pd.DataFrame([["", " Name ", " AGE "]])
        rec = Record(df=df_title_only, title_identifiers=("name", "age"))

        # ACT
        new_idx = rec.write_record({"name": "Eve", "age": 22})
        rec.reset_read()
        row = rec.read_record(0, labels=("name", "age"), strict=True)

        # ASSERT
        with self.subTest("new_idx_after_grow", Act=new_idx, Exp=0):
            self.assertEqual(new_idx, 0)
        with self.subTest("name_after_grow", Act=row["name"], Exp="Eve"):
            self.assertEqual(row["name"], "Eve")
        with self.subTest("age_after_grow", Act=row["age"], Exp="22"):
            self.assertEqual(row["age"], "22")


if __name__ == "__main__":
    unittest.main()
