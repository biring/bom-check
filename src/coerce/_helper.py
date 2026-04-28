"""
Regex-based coercion engine with traceable change logs.

This module implements the internal engine that applies ordered regex-based `Rule` transformations and records human-readable logs for each change. It powers BOM field coercion within the coerce package.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    from src.coerce import _helper
    from src.coerce._types import Rule
    text = "A\tB  C"
    rules = [Rule(r"\t+", " ", "Replace tabs with spaces"), Rule(r" {2,}", " ", "Collapse multiple spaces")]
    result = _helper.apply_rule(text, rules, attr_name="description")
    print(result.coerced_value)  # "A B C"

Dependencies:
    - Python >= 3.10
    - Standard Library: re, dataclasses, typing
    - Internal: src.coerce._types.Rule, Result, Log

Notes:
    - This module is an internal implementation detail; all external access should go through `src.coerce.interfaces`.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re
from ._types import Rule, Result, Log
from ._rules import PRE_RULES, POST_RULES


def _show(text: str, max_len: int = 32) -> str:
    """
    Render control characters visibly and truncate long strings.

    Replaces newline and tab with their visible escape sequences and shortens overly long strings with a single ellipsis to produce safe, human-readable log snippets.

    Args:
        text (str): The input string to render.
        max_len (int, optional): Maximum length of the returned preview. Defaults to 32.

    Returns:
        str: A readable preview with control characters escaped and length limited.

    Raises:
        None
    """
    visible = text.replace("\n", "\\n").replace("\t", "\\t")
    if len(visible) > max_len:
        return visible[: max_len - 1] + "…"
    return visible


def apply_rule(str_in: str, rules: list[Rule], attr_name: str) -> Result:
    """
    Apply ordered regex coercion rules and collect per-rule change logs.

    Runs a fixed set of pre-rules to remove known artifacts (e.g., Excel XML escapes, control characters), then applies caller rules. Each rule runs sequentially; the output of one becomes the input to the next. A change log entry is recorded only when a rule makes a substitution.

    Args:
        str_in (str): Raw input string to transform.
        rules (list[Rule]): Ordered list of coercion rules with pattern, replacement, and description.
        attr_name (str): Name of the attribute/field associated with this coercion.

    Returns:
        Result: Result object containing original, coerced value, and per-rule change logs.

    Raises:
        re.error: If any rule contains an invalid regex pattern.
    """
    result = Result(attr_name=attr_name, original_value=str_in, coerced_value="", changes=[])
    text_in = str_in
    text_out = str_in

    # Apply pre-rules first to normalize known artifacts before field-specific coercion rules run.
    for rule in PRE_RULES:
        # Apply the regex substitution
        text_out = re.sub(rule.pattern, rule.replacement, text_in)

        # Log only on change to avoid noisy, redundant entries.
        if text_out != text_in:
            log = Log(before=_show(text_in), after=_show(text_out), description=rule.description)
            result.changes.append(log)

        # Carry forward the output as the next input to preserve deterministic sequencing.
        text_in = text_out

    # Process rules in order; stable transformations depend on deterministic sequencing.
    for rule in rules:
        # Apply the regex substitution
        text_out = re.sub(rule.pattern, rule.replacement, text_in)

        # Log only on change to avoid noisy, redundant entries.
        if text_out != text_in:
            log = Log(before=_show(text_in), after=_show(text_out), description=rule.description)
            result.changes.append(log)

        # Carry forward output as input for next rule
        text_in = text_out

    # Apply post-rules to normalize known artifacts after field-specific coercion rules run.
    for rule in POST_RULES:
        # Apply the regex substitution
        text_out = re.sub(rule.pattern, rule.replacement, text_in)

        # Log only on change to avoid noisy, redundant entries.
        if text_out != text_in:
            log = Log(before=_show(text_in), after=_show(text_out), description=rule.description)
            result.changes.append(log)

        # Carry forward the output as the next input to preserve deterministic sequencing.
        text_in = text_out

    # Finalize coerced value and return immutable record.
    result.coerced_value = text_out

    return result
