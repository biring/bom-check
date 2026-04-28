"""
Unit tests for the internal regex-based coercion engine (_helper module).

Example Usage:
    # Run this specific module:
    python -m unittest tests/coerce/test__helper.py

    # Discover and run all tests:
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: unittest, typing
    - External Packages: None

Notes:
    - Each test validates both functional output (`coerced_value`) and side effects (log count and descriptions).
    - Tests treat rules as pure transformations and assert both value_out and logs.
    - Emphasis is on public behavior, not internal regex implementation details.

License:
    - Internal Use Only
"""

import unittest
from typing import Match

# noinspection PyProtectedMember
from src.coerce import _helper as common  # Direct internal import — acceptable in tests


class TestApplyRule(unittest.TestCase):
    """
    Unit tests for the `apply_rule` function.
    """

    def test_pre_rules(self):
        """
        Should apply each pre-rule transformation before field-specific rules.
        """
        # ARRANGE
        attr = "AnyField"
        rules = []
        cases = [
            ("Non-breaking space", "A\u00A0B", "A B", 1),
            ("Narrow no-break space", "A\u202FB", "A B", 1),
            ("Figure space", "A\u2007B", "A B", 1),
            ("Thin space", "A\u2009B", "A B", 1),
            ("Multiple unicode spaces", "A\u00A0\u2009B", "A B", 2),
            ("Excel XML control chars", "A_x0009_B_x000B_C_x000C_D_x000A_E_x000D_", "ABCDE", 1),
            ("Chinese comma", "A，B", "A,B", 1),
            ("Chinese left parenthesis", "A（B", "A(B", 1),
            ("Chinese right parenthesis", "A）B", "A)B", 1),
            ("Chinese semicolon", "A；B", "A;B", 1),
            ("Chinese colon", "A：B", "A:B", 1),
        ]

        # ACT
        for case_name, actual_in, expected_out, log_length in cases:
            result = common.apply_rule(actual_in, rules, attr)

            # ASSERT
            # ASSERT
            with self.subTest(case=case_name, field="Result", Exp=expected_out, Act=result.coerced_value):
                self.assertEqual(result.coerced_value, expected_out)
            with self.subTest(case=case_name, field="Log Count", Exp=log_length, Act=len(result.changes)):
                self.assertEqual(len(result.changes), log_length)

    def test_post_rules(self):
        """
        Should apply each post-rule transformation after field-specific rules.
        """
        # ARRANGE
        attr = "AnyField"
        rules = []
        cases = [
            ("Collapse double spaces", "A  B", "A B", 1),
            ("Collapse multiple spaces", "A   B", "A B", 1),
            ("Strip starting edge spaces", " A B", "A B", 1),
            ("Strip ending edge spaces", "A B ", "A B", 1),
            ("Strip edge spaces", " A B ", "A B", 1),
            ("Collapse double spaces and strip edge spaces", "  A B ", "A B", 2),

        ]

        # ACT & ASSERT
        for case_name, actual_in, expected_out, log_length in cases:
            result = common.apply_rule(actual_in, rules, attr)

            with self.subTest(case=case_name, field="Result", Exp=expected_out, Act=result.coerced_value):
                self.assertEqual(result.coerced_value, expected_out)

            with self.subTest(case=case_name, field="Log Count", Exp=log_length, Act=len(result.changes)):
                self.assertEqual(len(result.changes), log_length)

    def test_pattern_change(self):
        """
        Should apply a simple string replacement rule and record exactly one log entry.
        """
        # ARRANGE
        attr = "Serial Number"
        text = "abc-123-xyz"
        rules = [common.Rule(pattern=r"\d+", replacement="###", description="mask digits")]
        expected_out = "abc-###-xyz"
        expected_logs = 1

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.original_value, Exp=text):
            self.assertEqual(result.original_value, text)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("Log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)
        with self.subTest("Msg", Out=result.changes[0].description, Exp=rules[0].description):
            self.assertEqual(result.changes[0].description, rules[0].description)

    def test_pattern_no_change(self):
        """
        Should return the original text and an empty log when no rules match.
        """
        # ARRANGE
        attr = "Description"
        text = "will not change"
        rules = [common.Rule(pattern=r"\d+", replacement="x", description="digits masked")]
        expected_out = text
        expected_logs = 0

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.original_value, Exp=text):
            self.assertEqual(result.original_value, text)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)

    def test_pattern_empty(self):
        """
        Should return the original empty text and an empty log when no rules match.
        """
        # ARRANGE
        attr = "Stage"
        text = ""
        rules = [common.Rule(pattern=r"\d+", replacement="x", description="digits masked")]
        expected_out = text
        expected_logs = 0

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.original_value, Exp=text):
            self.assertEqual(result.original_value, text)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)

    def test_callable_change(self):
        """
        Should support a callable replacement and log when at least one substitution occurs.
        """
        # ARRANGE
        attr = "Description"
        text = "alpha beta gamma"

        def up_case_char(m: Match[str]) -> str:
            # Replace each matched vowel with its uppercase form
            return m.group(0).upper()

        rules = [common.Rule(pattern=r"[aeiou]", replacement=up_case_char, description="uppercase vowels")]
        expected_out = "AlphA bEtA gAmmA"
        expected_logs = len(rules)

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.original_value, Exp=text):
            self.assertEqual(result.original_value, text)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("Log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)
        with self.subTest("Msg", Out=result.changes[0].description, Exp=rules[0].description):
            self.assertEqual(result.changes[0].description, rules[0].description)

    def test_callable_no_change(self):
        """
        Should return the original text and an empty log when no substitution occurs.
        """
        # ARRANGE
        attr = "Phone number"
        text = "1234567890"

        def up_case_char(m: Match[str]) -> str:
            # Replace each matched vowel with its uppercase form
            return m.group(0).upper()

        rules = [common.Rule(pattern=r"[aeiou]", replacement=up_case_char, description="uppercase vowels")]
        expected_out = "1234567890"
        expected_logs = 0

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.original_value, Exp=text):
            self.assertEqual(result.original_value, text)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("Log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)

    def test_callable_empty(self):
        """
        Should return the original empty text and an empty log when no substitution occurs.
        """
        # ARRANGE
        attr = "Phone number"
        text = ""

        def up_case_char(m: Match[str]) -> str:
            # Replace each matched vowel with its uppercase form
            return m.group(0).upper()

        rules = [common.Rule(pattern=r"[aeiou]", replacement=up_case_char, description="uppercase vowels")]
        expected_out = ""
        expected_logs = 0

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value In", Out=result.original_value, Exp=text):
            self.assertEqual(result.original_value, text)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("Log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)

    def test_multiple(self):
        """
        Should apply multiple rules sequentially and log only the rules that matched.
        """
        # ARRANGE
        attr = "Info log"
        text = "  id: 007  \nname: bond\t"
        rules = [
            # Trim leading/trailing whitespace lines (affects the overall string)
            common.Rule(pattern=r"^\s+|\s+$", replacement="", description="trim ends"),
            # Collapse internal whitespace to single spaces
            common.Rule(pattern=r"[ \t]+", replacement=" ", description="collapse spaces"),
            # Mask numbers
            common.Rule(pattern=r"\d+", replacement="<num>", description="mask digits"),
            # Replace 'name:' label once
            common.Rule(pattern=r"\bname:", replacement="agent:", description="rename label"),
            # A rule that won't match anymore (e.g., tabs already collapsed)
            common.Rule(pattern=r"\t", replacement=" ", description="tabs to spaces"),
        ]
        # Work through the expected transformation step-by-step:
        # 1) trim ends -> "id: 007  \nname: bond"
        # 2) collapse spaces -> "id: 007 \nname: bond"
        # 3) mask digits -> "id: <num> \nname: bond"
        # 4) rename label -> "id: <num> \nagent: bond"
        # 5) tabs to spaces -> no-op
        expected_out = "id: <num> \nagent: bond"
        # 4 rules should have matched (last one no-ops)
        expected_logs = 4

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Attribute Name", Out=result.attr_name, Exp=attr):
            self.assertEqual(result.attr_name, attr)
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("Log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)
        # Verify that messages correspond to matched rules in order
        matched_msgs = [entry.description for entry in result.changes]
        expected_msgs = [rules[0].description, rules[1].description, rules[2].description, rules[3].description]
        with self.subTest("Messages", Out=matched_msgs, Exp=expected_msgs):
            self.assertEqual(matched_msgs, expected_msgs)

    def test_multiple_substitutions(self):
        """
        Should create exactly one log entry with multiple messages for multiple rule substitutions.
        """
        # ARRANGE
        attr = "ID"
        text = "a1 b2 c3"
        rules = [common.Rule(pattern=r"\d", replacement="#", description="mask each digit")]
        expected_out = "a# b# c#"
        expected_logs = 1  # one rule matched, many subs, single log

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)
        with self.subTest("Log Count", Out=len(result.changes), Exp=expected_logs):
            self.assertEqual(len(result.changes), expected_logs)
        with self.subTest("Log Msg", Out=result.changes[0].description, Exp=rules[0].description):
            self.assertEqual(result.changes[0].description, rules[0].description)

    def test_trace(self):
        """

        Should log `before` and `after` using visibility rules of `_show` (\\n, \\t shown).
        """
        # ARRANGE
        attr = "Notes"
        text = "rowA\t123\nrowB"  # contains tab and newline
        rules = [
            common.Rule(pattern=r"\t", replacement=" ", description="tab to space"),  # change 1
            common.Rule(pattern=r"\d+", replacement="<num>", description="mask digits"),  # change 2
        ]

        # Expected visible forms come from _show
        after_first = text.replace("\t", " ")
        after_second = after_first.replace("123", "<num>")
        expected_before_vis = common._show(text)
        expected_after_vis = common._show(after_second)

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        # Two rules matched → two logs, first.before is _show(original), last.after is _show(final)
        with self.subTest("Log Count", Out=len(result.changes), Exp=2):
            self.assertEqual(len(result.changes), 2)

        with self.subTest("First Log BEFORE visible", Out=result.changes[0].before, Exp=expected_before_vis):
            self.assertEqual(result.changes[0].before, expected_before_vis)

        with self.subTest("Last Log AFTER visible", Out=result.changes[-1].after, Exp=expected_after_vis):
            self.assertEqual(result.changes[-1].after, expected_after_vis)

    def test_pre_rules_remove_excel_xml_control_artifacts(self):
        """
        Should remove Excel XML artifacts for TAB, VT, FF, LF, CR via PRE_RULES.
        """
        # ARRANGE
        attr = "AnyField"
        text = "A_x0009_B_x000B_C_x000C_D_x000A_E_x000D_"

        # Field rules are intentionally irrelevant here; pre-rules should do the work.
        rules = [
            common.Rule(pattern=r"\s+", replacement="", description="strip whitespace"),
        ]

        expected_out = "ABCDE"

        # ACT
        result = common.apply_rule(text, rules, attr)

        # ASSERT
        with self.subTest("Value Out", Out=result.coerced_value, Exp=expected_out):
            self.assertEqual(result.coerced_value, expected_out)

        # Only PRE_RULES should have matched (whitespace rule should no-op after artifacts removed).
        with self.subTest("Log Count", Out=len(result.changes), Exp=1):
            self.assertEqual(len(result.changes), 1)

        with self.subTest("Log Msg", Out=result.changes[0].description):
            self.assertIn("Excel XML", result.changes[0].description)



class TestShow(unittest.TestCase):
    """
    Unit tests for the `_show` helper.

    Ensures control characters are made visible (`\n` -> "\\n", `\t` -> "\\t")
    and that long strings are truncated with a single ellipsis character
    when exceeding `max_len`.
    """

    def test_valid(self):
        """
        Should replace newline and tab with visible escape sequences.
        """
        # ARRANGE
        text = "line1\nline2\tend"
        expected = r"line1\nline2\tend"  # literal backslashes

        # ACT
        result = common._show(text)

        # ASSERT
        with self.subTest("Visible", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_small(self):
        """
        Should return the original (visibility-adjusted) text when length <= max_len (default 32).
        """
        # ARRANGE
        text = "short_text"
        expected = "short_text"

        # ACT
        result = common._show(text)  # default max_len=32

        # ASSERT
        with self.subTest("No Truncate", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_truncates(self):
        """
        Should truncate to max_len-1 characters and append a single ellipsis '…' when length > max_len.
        """
        # ARRANGE
        text = "abcdefghijklmnopqrstuvwxyz0123456789"  # 36 chars
        max_len = 10
        # Expect first 9 characters + '…'
        expected = "abcdefghi" + "…"

        # ACT
        result = common._show(text, max_len=max_len)

        # ASSERT
        with self.subTest("Truncate", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest("Length Check", Out=len(result), Exp=max_len):
            self.assertEqual(len(result), max_len)

    def test_truncation_counts(self):
        """
        Should apply truncation logic to the visibility-adjusted string (i.e., after '\\n' and '\\t' expansion increases length).
        """
        # ARRANGE
        # Input of length 4 becomes length 5 after visibility.
        text = "A\nBC"
        # max_len forces truncation after visibility; max_len=4 means keep 4 chars + '…'
        max_len = 4
        visible = r"A\nB"  # "A\\nB"
        expected = visible[: max_len - 1] + "…"

        # ACT
        result = common._show(text, max_len=max_len)

        # ASSERT
        with self.subTest("Truncate Visible", Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_max_size(self):
        """
        Should not truncate when visibility-adjusted length equals max_len - 1 exactly.
        """
        # ARRANGE
        # Visible version has exactly 8 characters: "A\\nB\\tCD" -> A(1) \ (2) n(3) B(4) \ (5) t(6) C(7) D(8)
        text = "A\nB\tCD"
        max_len = 8
        expected = r"A\nB\tCD"

        # ACT
        result = common._show(text, max_len=max_len)

        # ASSERT
        with self.subTest("Exact Limit", Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest("length Check", Out=len(result), Exp=max_len):
            self.assertEqual(len(result), max_len)

    def test_small_length(self):
        """
        Should handle very small max_len values (e.g., 1 or 2) by truncating to max_len-1 + '…' when needed.
        """
        # ARRANGE
        cases = [
            # text, max_len, expected
            ("abc", 1, "…"),  # keep 0 chars + '…'
            ("abc", 2, "a" + "…"),  # keep 1 char + '…'
        ]

        # ACT & ASSERT
        for text, max_len, expected in cases:
            result = common._show(text, max_len=max_len)
            with self.subTest(f"Max Length = {max_len}", Out=result, Exp=expected):
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
