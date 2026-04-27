"""
Regular expression rules and error message templates for validating BOM fields.

This module centralizes compiled regex patterns and descriptive rule strings for Bill of Materials (BOM) fields.

Main capabilities:
    - Provide compiled regex patterns for BOM fields (MODEL_NUMBER, BOARD_NAME, etc.)
    - Provide descriptive rule strings for user-facing validation errors
    - Serve as a single source of truth for validation across parsers and checkers

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct usage (internal scripts or unit tests only):
    from src.approve import _constants as constants
    if not constants.MODEL_NUMBER_PATTERN.fullmatch("AB1234C"):
        print(constants.MODEL_NUMBER_RULE.format(a="Model No", b="AB1234C"))

Dependencies:
    - Python >= 3.9
    - Standard Library: re

Notes:
    - Intended for internal use within the `rules` package as a shared validation layer.
    - Patterns are compiled once and treated as constants; do not mutate at runtime.
    - Rule strings are templates meant to be formatted with `{a}` = field name, `{b}` = value.
    - Business logic (which field uses which rule) should remain in higher-level code.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import gets nothing.

import re

GENERIC_VALUE_ERROR_MSG: str = "Invalid '{a}' = '{b}' does not match expected format. "
ERR_INVALID_REGEX: str = "Regex error while validating '{a}' = '{b}': {c} "
ERR_COMPILED_REGEX: str = "Expected compiled regex pattern for '{a}', but got '{b}'. "

MODEL_NUMBER_RULE: str = (
    "Correct '{a}' starts with 2–3 capital letters, followed by 3–4 digits, "
    "and may optionally end with up 0-3 capital letters."
)

MODEL_NUMBER_PATTERN = re.compile(r'^[A-Z]{2,3}[0-9]{3,4}[A-Z]{0,3}$')

BOARD_NAME_RULE: str = (
    "Correct '{a}' starts with a letter, contains only letters, digits, and spaces, "
    "and ends with 'PCBA' (uppercase, exact)."
)

BOARD_NAME_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9 ]*PCBA$')

BOARD_SUPPLIER_RULE: str = (
    "Correct '{a}' starts with a capital letter, may contain letters, digits, and spaces, "
    "and should be at least 3 characters long."
)

BOARD_SUPPLIER_PATTERN = re.compile(r'^[A-Z][A-Za-z0-9 ]{2,}$')

BUILD_STAGE_RULE: str = "Correct '{a}' formats are Pn, Pn.n, EBn, EBn.n, MB, MP, ECN, ECNn, TRA, or FOT."

BUILD_STAGE_PATTERN = re.compile(r'^(?:P\d+(?:\.\d+)?|EB\d+(?:\.\d+)?|ECN\d*|MP|MB|TRA|FOT)$')

COST_RULE: str = "Correct '{a}' is a positive number"

COST_PATTERN = re.compile(r'^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$')

ITEM_RULE: str = "Correct '{a}' is either empty or a positive integer (e.g., '', '1', '45'). "

ITEM_PATTERN = re.compile(r'^(?:[1-9][0-9]*)?$')

COMPONENT_TYPE_RULE: str = (
    "Correct '{a}' is a string of alphabets with optional spaces "
    "or '/' characters (e.g., 'Fuse', 'BJT', 'Diode/SCR', 'Battery Terminal') "
    "or the keyword 'ALT' optionally followed by a positive integer "
    "(e.g., 'ALT', 'ALT1', 'ALT2'). Values like 'ALT0' or 'ALTXYZ' are not allowed."
)

COMPONENT_TYPE_PATTERN = re.compile(
    r'^(?:ALT(?:[1-9][0-9]*)?|(?!ALT[A-Za-z])[A-Za-z]+(?:[ /][A-Za-z]+)*)$')

DEVICE_PACKAGE_RULE: str = (
    "Valid '{a}' is either empty or a string that starts and ends with a letter or digit, "
    "contains only letters, digits, '.', '=', ',', and '-' characters, "
    "and does not contain two consecutive characters from the set ('.', '=', ',', '-') "
    "(e.g., '0603', 'QFN-32', 'SMA', '10.5x25.6mm', 'D=12mm,L=5mm')."
)

DEVICE_PACKAGE_PATTERN = re.compile(
    r'^(?:'
    r'[A-Za-z0-9]'                       # must start with letter or digit
    r'(?!.*[.=,\-]{2})'                  # no repeated symbols
    r'[A-Za-z0-9.=,\-]*'                 # allowed characters
    r'[A-Za-z0-9]'                       # must end with letter or digit
    r'|$)'                               # or empty
)

DESCRIPTION_RULE: str = (
    "Valid '{a}' must be non-empty and may contain single spaces between comma-separated values. "
    "No other whitespace allowed. (e.g., '1k,1%,0.5W', 'Silicon Rectifier Diode,1A,50V,SOD-123')."
)

DESCRIPTION_PATTERN = re.compile(r'^\S+( \S+)*,\S+(,\S+)*$')

UNITS_RULE: str = (
    "Valid '{a}' is either empty or a string of alphabets with an optional dot "
    "at the end (e.g., '', 'PCS', 'Each', 'grams', 'lb.')."
)

UNITS_PATTERN = re.compile(r'^[A-Za-z]+\.?$|^$')

CLASSIFICATION_RULE: str = (
    "Valid '{a}' is a single character: 'A', 'B', or 'C'."
)

CLASSIFICATION_PATTERN = re.compile(r'^[ABC]$')

MFG_NAME_RULE: str = (
    "Valid '{a}' is a non-empty string starting with a letter or digit. "
    "It may contain letters, digits, single spaces, and the symbols '.', '-', '&', "
    "',' Examples: 'ST Microelectronics', 'Delta Pvt. Ltd', 'Hewlett-Packard', "
    "'Procter & Gamble', '3M', 'TI-89'."
)

MFG_NAME_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9 ,.&-]*[A-Za-z0-9.]$')

MFG_PART_NO_RULE: str = (
    "Valid '{a}' must contain at least one character and "
    "consist of alphanumeric characters with optional '-', '_', '#', or '.' characters. "
    "Whitespace and '*' are not allowed "
    "(e.g., 'LM358N', 'SN74HC595N-TR', 'AT328P_U', 'BC547#B')."
)

MFG_PART_NO_PATTERN = re.compile(r'^[A-Za-z0-9._#-]+$')

UL_VDE_NO_RULE: str = (
    "Valid '{a}' may be empty, or start with 1–4 alphabets followed by 1–8 digits, "
    "optionally separated by a single '-' or space "
    "(e.g., '', 'E1234', 'UL 567890', 'VDE-12345678')."
)

UL_VDE_NO_PATTERN = re.compile(r'^$|^[A-Za-z]{1,4}[- ]?[0-9]{1,8}$')

VALIDATED_AT_RULE: str = (
    "Valid '{a}' is either empty or a list of tokens separated "
    "by '/' or ',' where each token is one of the following formats (case-sensitive): "
    "'Pn', 'Pn.n', 'EBn', 'EBn.n', 'ECN', 'ECNn', 'MB', 'MP', or 'FOT' "
    "(e.g., '', 'P1/EB0/MP')."
)
TOKEN = r'(?:P[0-9]+(?:\.[0-9]+)?|EB[0-9]+(?:\.[0-9]+)?|ECN[0-9]*|MB|MP|FOT)'
VALIDATED_AT_PATTERN = re.compile(rf'^(?:{TOKEN}(?:[\/,]{TOKEN})*)?$')

QUANTITY_RULE: str = (
    "Valid '{a}' is a non-negative number (greater than or equal to zero), "
    "which may be an integer or a decimal with digits after the dot "
    "(e.g., '0', '2', '0.34')."
)

QUANTITY_PATTERN = re.compile(r'^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$')

DESIGNATOR_RULE: str = (
    "Valid '{a}' is either empty or a list of tokens separated by ',' "
    "where each token starts with 1–5 uppercase alphabets optionally followed by either "
    "1–5 digits or a single '+' or '-' (e.g., '', 'ACN', 'R1', 'R1,C1,M+')."
)
DESIGNATOR_TOKEN = r'[A-Z]{1,5}(?:[0-9]{1,5}|[+-])?'
DESIGNATOR_PATTERN = re.compile(rf'^(?:{DESIGNATOR_TOKEN}(?:,{DESIGNATOR_TOKEN})*)?$')

PRICE_RULE: str = (
    "Valid '{a}' is a non-negative number (>= 0). "
    "It may be an integer or a decimal number with digits after the dot "
    "(e.g., '0', '2', '0.34')."
)

PRICE_PATTERN = re.compile(r'^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$')

# TODO - add pattern compile guard
# try:
#     PATTERN: re.Pattern = re.compile(r'... ')
# except re.error as e:
#     raise RuntimeError(f"Invalid regex for PATTERN: {e}")
