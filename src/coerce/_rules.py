"""
Field-specific rule sets that apply predefined regex-based coercion patterns.

This module groups reusable `Rule` objects (from `_regex`) by BOM field name. Each list defines
the sequence of text-cleanup steps applied when coercing a given field, such as removing
whitespace or collapsing spaces.

Example Usage:
    # Preferred usage via package interface:
    # Not exposed publicly; this is an internal module.

    # Direct internal access (for tests or internal scripts only):
    from src.coerce import _rules
    import re
    text = "ac 100"
    for rule in _rules.MODEL_NUMBER:
        text = re.sub(rule.pattern, rule.repl, text)
    print(text)  # "AC100"

Dependencies:
    - Python >= 3.10
    - Standard Library: re
    - Internal: src.coerce._regex

Notes:
    - Each list defines a deterministic sequence of `Rule` applications for a BOM field.
    - Rules are idempotent and composable—repeated application should yield the same result.
    - This module is internal; higher-level coercer functions determine which rule set to use.
    - Public API calls should access coercion through `src.coerce.interfaces`, not here.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from . import _regex as rx

# This rule is always run before attribute specific rule is run
PRE_RULES = [
    rx.REMOVE_EXCEL_XML_CONTROL_CHARS,
    rx.CHINESE_COMMA,
    rx.CHINESE_LEFT_PAREN,
    rx.CHINESE_RIGHT_PAREN,
    rx.CHINESE_SEMICOLON,
    rx.CHINESE_COLON,
]

# This rule is always run after attribute specific rule is run
POST_RULES = [
    rx.COLLAPSE_MULTIPLE_SPACES,
    rx.STRIP_EDGE_SPACES,
]

# model_no
MODEL_NUMBER: list = [
    rx.TO_UPPER,
    rx.REMOVE_WHITESPACES,
]
# board_name
BOARD_NAME: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
    rx.COLLAPSE_MULTIPLE_SPACES,
    rx.STRIP_EDGE_SPACES,
]
# manufacturer
BOARD_SUPPLIER: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
    rx.COLLAPSE_MULTIPLE_SPACES,
    rx.STRIP_EDGE_SPACES,
]
# build_stage
BUILD_STAGE: list = [
    rx.REMOVE_WHITESPACES,
]
# date
BOM_DATE: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
]
# material_cost
MATERIAL_COST: list = [
    rx.REMOVE_WHITESPACES,
    rx.EMPTY_TO_ZERO,
]
# overhead_cost
OVERHEAD_COST: list = [
    rx.REMOVE_WHITESPACES,
    rx.EMPTY_TO_ZERO,
]
# total_cost
TOTAL_COST: list = [
    rx.REMOVE_WHITESPACES,
    rx.EMPTY_TO_ZERO,
]
# item
ITEM: list = [
    rx.REMOVE_WHITESPACES,
]
# component_type
COMPONENT_TYPE: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
]
# device_package
DEVICE_PACKAGE: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
    rx.DIMENSION_SEPARATOR_STAR,
]
# description
DESCRIPTION: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
]
# unit
UNITS: list = [
    rx.REMOVE_WHITESPACES,
]
# classification
CLASSIFICATION: list = [
    rx.REMOVE_WHITESPACES,
]
# manufacturer
MANUFACTURER: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
]
# mfg_part_number
MFG_PART_NUMBER: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
]
# ul_vde_number
UL_VDE_NUMBER: list = [
    rx.REMOVE_WHITESPACES_EXCEPT_SPACE,
]
# validated_at
VALIDATED_AT: list = [
    rx.REMOVE_WHITESPACES,
    rx.REMOVE_STANDALONE_FORWARD_SLASH,
]
# qty
QTY: list = [
    rx.REMOVE_WHITESPACES,
]
# designator
DESIGNATOR: list = [
    rx.REMOVE_WHITESPACES,
]
# unit_price
UNIT_PRICE: list = [
    rx.REMOVE_WHITESPACES,
    rx.EMPTY_TO_ZERO,
]
# sub_total
SUB_TOTAL: list = [
    rx.REMOVE_WHITESPACES,
    rx.EMPTY_TO_ZERO,
]
