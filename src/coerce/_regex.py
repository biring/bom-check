"""
Predefined regex-based coercion rules for BOM field normalization.

This module defines reusable `Rule` instances that clean and standardize text fields such as
manufacturer names, model numbers, and cost headers. Each `Rule` specifies a regex pattern,
replacement, and human-readable message for logging or review output.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    import re
    from src.coerce import _regex as rx
    text = "A  B   C"
    cleaned = re.sub(rx.REMOVE_SPACES_ONLY.pattern, "", text)  # pattern is r" +"
    print(cleaned)  # ABC

Dependencies:
    - Python >= 3.10
    - Standard Library: re
    - Internal: src.coerce._types.Rule

Notes:
    - Each `Rule` object encapsulates a regex pattern and replacement for idempotent, composable cleanup.
    - These rules are internal constants; they are grouped or sequenced by higher-level coercer functions, not executed here.
    - Public APIs should never import this module directly.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from . import _types as types

# General transformations
TO_UPPER = types.Rule(
    r"(.*)",
    lambda m: m.group(0).upper(),
    "Converted to uppercase."
)

# Handle Chinese punctuation variants
CHINESE_COMMA = types.Rule(
    r"[，]",
    ",",
    "Converted Chinese comma to ASCII comma."
)
CHINESE_LEFT_PAREN = types.Rule(
    r"[（]",
    "(",
    "Converted Chinese left parenthesis to ASCII (."
)
CHINESE_RIGHT_PAREN = types.Rule(
    r"[）]",
    ")",
    "Converted Chinese right parenthesis to ASCII )."
)
CHINESE_SEMICOLON = types.Rule(
    r"[；]",
    ";",
    "Converted Chinese semicolon to ASCII ;."
)
CHINESE_COLON = types.Rule(
    r"[：]",
    ":",
    "Converted Chinese colon to ASCII :."
)

# Remove known manufacturer prefixes
REMOVE_PREFIX_MANUFACTURER = types.Rule(
    r"(?i)^MANUFACTURER",
    " ",
    "Removed MANUFACTURER prefix (case-insensitive)."
)
REMOVE_PREFIX_MANU = types.Rule(
    r"(?i)^MANU",
    " ",
    "Removed MANU prefix (case-insensitive)."
)
REMOVE_PREFIX_MFG = types.Rule(
    r"(?i)^MFG",
    " ",
    "Removed MFG prefix (case-insensitive)."
)

# Whitespace normalization
REMOVE_WHITESPACES_EXCEPT_SPACE = types.Rule(
    r"[\t\n\r\f\v]+",
    "",
    "Removed whitespace characters (tabs, newlines, form feeds, etc.) but preserved spaces.")
REMOVE_WHITESPACES = types.Rule(
    r"\s+",
    "",
    "Removed whitespace characters (spaces, tabs, newlines, etc.)."
)
REMOVE_SPACES_ONLY = types.Rule(
    r" +",
    "",
    "Removed space characters."
)
REMOVE_EXCEL_XML_CONTROL_CHARS = types.Rule(
    r"(?i)_x000[9A-D]_",
    "",
    "Removed Excel XML control-character artifacts (CR, LF, TAB, FF, VT)."
)
UNICODE_SPACES_TO_SPACE = types.Rule(
    r"[\u00A0\u202F\u2007\u2009]",
    " ",
    "Replaced Unicode space characters with normal space."
)
REMOVE_STANDALONE_FORWARD_SLASH = types.Rule(
    r"^/$",
    "",
    "Removed standalone forward slash."
)

# Punctuation to comma
NEWLINE_TO_COMMA = types.Rule(
    r"\n",
    ",",
    "Replaced newline with comma."
)
COLON_TO_COMMA = types.Rule(
    r"[:]",
    ",",
    "Replaced colon with comma."
)
SEMICOLON_TO_COMMA = types.Rule(
    r"[;]",
    ",",
    "Replaced semicolon with comma."
)
SPACE_TO_COMMA = types.Rule(
    r"[ ]",
    ",",
    "Replaced space with comma."
)
STRIP_LEADING_COMMA = types.Rule(
    r"^,+",
    "",
    "Removed leading commas."
)
STRIP_TRAILING_COMMA = types.Rule(
    r",+$",
    "",
    "Removed trailing commas."
)
COLLAPSE_MULTIPLE_COMMAS = types.Rule(
    r",{2,}",
    ",",
    "Collapsed multiple commas into one."
)

# Punctuation to space
COLON_TO_SPACE = types.Rule(
    r"[:]",
    " ",
    "Replaced colon with space."
)
DOT_TO_SPACE = types.Rule(
    r"[.]",
    " ",
    "Replaced dot '.' with space."
)
DOT_COMMA_TO_SPACE = types.Rule(
    r"\.,",
    " ",
    "Replaced '.,' with space (e.g., 'Co.,Ltd' → 'Co Ltd')."
)
STRIP_EDGE_SPACES = types.Rule(
    r"^ +| +$",
    "",
    "Removed leading and trailing spaces."
)
COLLAPSE_MULTIPLE_SPACES = types.Rule(
    r" {2,}",
    " ",
    "Collapsed multiple spaces into one."
)

EMPTY_TO_ZERO = types.Rule(
    r"^\s*$",
    "0",
    "Replaced empty or whitespace-only field with zero."
)

DIMENSION_SEPARATOR_STAR = types.Rule(
    r"(?<=[0-9a-zA-Z])\*(?=[0-9])",
    "x",
    "Replaced '*' with 'x' in dimension notation."
)