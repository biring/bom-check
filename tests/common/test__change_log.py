"""
Validates logging entry collection, context handling, and deterministic rendering behavior.

This module tests that log entries are recorded only when non-empty, that contextual metadata is correctly applied to each entry at insertion time, and that rendered output preserves insertion order with stable formatting. The tests focus on observable output and state rather than internal implementation, including verification of initialization defaults, filtering of invalid messages, and independence of entries from subsequent context changes.

Example Usage:
	# Preferred usage via project-root invocation:
	python -m unittest tests/common/test__change_log.py

	# Direct discovery (runs all tests, including this module):
	python -m unittest discover -s tests

Test Data and Fixtures:
	- In-memory strings are used to represent messages and contextual fields.
	- No filesystem or external resources are involved.
	- Test instances are created per test to ensure isolation with no shared state.
	- No explicit cleanup is required due to purely in-memory operations.

Dependencies:
	- Python >= 3.8
	- Standard Library: unittest

Notes:
	- Tests directly access internal attributes to verify initialization state, which couples tests to internal structure.
	- Rendering output is validated for ordering and formatting consistency using a shared separator constant.
	- Behavior is deterministic with no reliance on external state or timing.
	- Context is expected to be captured at insertion time, and later mutations must not affect previously recorded entries.

License:
	- Internal Use Only
"""

import unittest
# noinspection PyProtectedMember
from src.common._change_log import ChangeLog, LOG_RENDER_SEPARATOR  # Direct internal import — acceptable in tests


class TestChangeLog(unittest.TestCase):
    """
    Unit test for the `ChangeLog` class.
    """

    def test_init(self):
        """
        Should initialize all context fields as empty strings and entries as empty list.
        """
        # ARRANGE

        # ACT
        log = ChangeLog()

        # ASSERT
        with self.subTest("Module name"):
            self.assertEqual(log._module_name, "")
        with self.subTest("File name"):
            self.assertEqual(log._file_name, "")
        with self.subTest("Sheet name"):
            self.assertEqual(log._sheet_name, "")
        with self.subTest("Section name"):
            self.assertEqual(log._section_name, "")
        with self.subTest("Entries"):
            self.assertEqual(log._entries, [])

    def test_add_entry(self):
        """
        Should return tuple of formatted rows in insertion order.
        """
        # ARRANGE
        sep = LOG_RENDER_SEPARATOR
        log = ChangeLog()
        log.set_module_name("test")
        log.set_file_name("bom.xlsx")
        log.set_sheet_name("P3")
        log.set_section_name("Header")
        log.add_entry("Normalized manufacturer names")
        log.add_entry("Collapsed internal whitespace")

        expected = (
            "test"+sep+"bom.xlsx"+sep+"P3"+sep+"Header"+sep+"Normalized manufacturer names",
            "test"+sep+"bom.xlsx"+sep+"P3"+sep+"Header"+sep+"Collapsed internal whitespace",
        )

        # ACT
        rows = log.render()

        # ASSERT
        with self.subTest("Row Count", Out=len(rows), Exp=len(expected)):
            self.assertEqual(len(rows), len(expected))
        for out_row, exp_row in zip(rows, expected):
            with self.subTest("Row", Out=out_row, Exp=exp_row):
                self.assertEqual(out_row, exp_row)

    def test_empty_message(self):
        """
        Should skip blank or whitespace-only messages and keep only valid entries.
        """
        # ARRANGE
        sample_log_entry = "Applied masks"
        log = ChangeLog()
        log.set_module_name("test")
        log.set_file_name("a.xlsx")
        log.set_sheet_name("S1")
        log.set_section_name("Items")
        log.add_entry("")  # empty should be ignored
        log.add_entry(" ")  # white space should be ignored
        log.add_entry("\t")  # white space should be ignored
        log.add_entry(sample_log_entry)  # kept

        expected_len = 1

        # ACT
        log_list = log.render()

        # ASSERT
        with self.subTest("Entries", Out=len(log_list), Exp=expected_len):
            self.assertEqual(len(log_list), expected_len)
        with self.subTest("Log Entry", Out=log_list[0], Exp=sample_log_entry):
            self.assertIn(sample_log_entry, log_list[0])

    def test_context_change(self):
        """
        Should preserve context at insertion time across multiple entries.
        """
        # ARRANGE
        sep = LOG_RENDER_SEPARATOR
        log = ChangeLog()
        log.set_module_name("test_context")
        log.set_file_name("v1.xlsx")
        log.set_sheet_name("EB0")
        log.set_section_name("Meta")
        log.add_entry("Rule A")

        # Change context and add an entry
        log.set_file_name("v2.xlsx")
        log.set_sheet_name("MP")
        log.set_section_name("Table")
        log.add_entry("Rule B")

        expected = (
            "test_context"+sep+"v1.xlsx"+sep+"EB0"+sep+"Meta"+sep+"Rule A",
            "test_context"+sep+"v2.xlsx"+sep+"MP"+sep+"Table"+sep+"Rule B",
        )

        # ACT
        rows = log.render()

        # ASSERT
        for out_row, exp_row in zip(rows, expected):
            with self.subTest("Context Change", Out=out_row, Exp=exp_row):
                self.assertEqual(out_row, exp_row)


if __name__ == "__main__":
    unittest.main()
