"""
Value string validation helpers for BOM row data.

This module defines assertion-style validators that enforce formatting and value rules for Bill of Materials (BOM) row cell values. Each validator raises a `ValueError` with descriptive guidance if the input does not meet the required specification.

Example Usage:
    # Preferred usage via package interface:
    from src.approve import interfaces as approve
    approve.quantity("2.75")

    # Direct usage (internal scripts or unit tests only):
    from src.rules.approve import _row as approve
    approve.quantity("2.75")

Dependencies:
    - Python >= 3.9
    - Standard Library: re

Notes:
    - Each validator succeeds silently (returns None) if the input is valid.
    - On failure, a ValueError is raised with both generic and field-specific error text for debugging or user feedback.
    - Regex patterns and rule strings are centralized in `_constants` for consistency and reuse.
    - Intended for internal use within the BOM parsing pipeline.

License:
    - Internal Use Only
"""

from src.schemas.interfaces import (
    TableLabelsV3,
)

from src.approve import _common as common
from src.approve import _constants as constants


def item(value: str) -> None:
    """
    Validate that the input string is a valid item.

    A valid item format is either empty or positive integer. (e.g., "", "1", "45" , "123").

    Args:
        value (str): The item string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the item string pattern.
    """
    common.approve_or_raise(
        value,
        constants.ITEM_PATTERN,
        TableLabelsV3.ITEM,
        constants.ITEM_RULE,
    )


def component_type(value: str) -> None:
    """
    Validate that the input string is a valid component type.

    A valid component type is a string of alphabets with optional spaces or '/' characters (e.g., 'Fuse', 'BJT', 'Diode/SCR', 'Battery Terminal') or the keyword 'ALT' optionally followed by digits (e.g., 'ALT', 'ALT1', 'ALT2').

    Args:
        value (str): The component type string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the component string pattern.
    """
    common.approve_or_raise(
        value,
        constants.COMPONENT_TYPE_PATTERN,
        TableLabelsV3.COMPONENT_TYPE,
        constants.COMPONENT_TYPE_RULE,
    )


def device_package(value: str) -> None:
    """
    Validate that the input string is a valid device package.

    A valid device package is empty or string of alphabets and numbers with optional '-' character (e.g., '0603', 'QFN-32', 'SMA').

    Args:
        value (str): The device package string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the device package string pattern.
    """
    common.approve_or_raise(
        value,
        constants.DEVICE_PACKAGE_PATTERN,
        TableLabelsV3.DEVICE_PACKAGE,
        constants.DEVICE_PACKAGE_RULE,
    )


def description(value: str) -> None:
    """
    Validate that the input string is a valid description.

    A valid description is non-empty and contains no whitespaces. (e.g., '1k,1%,0.5W', '1uF,10%,50V', 'Rectifier,1A,50V').

    Args:
        value (str): The description string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the description string pattern.
    """
    common.approve_or_raise(
        value,
        constants.DESCRIPTION_PATTERN,
        TableLabelsV3.DESCRIPTION,
        constants.DESCRIPTION_RULE,
    )


def units(value: str) -> None:
    """
    Validate that the input string is a valid units.

    Valid units are either empty or a string of alphabets with an optional dot at the end (e.g., '', 'PCS', 'Each', 'grams', 'lb.').

    Args:
        value (str): The units string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the units string pattern.
    """
    common.approve_or_raise(
        value,
        constants.UNITS_PATTERN,
        TableLabelsV3.UNITS,
        constants.UNITS_RULE,
    )


def classification(value: str) -> None:
    """
    Validate that the input string is a valid classification.

    Valid classification is A, B, or C.

    Args:
        value (str): The classification string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the item format string pattern.
    """
    common.approve_or_raise(
        value,
        constants.CLASSIFICATION_PATTERN,
        TableLabelsV3.CLASSIFICATION,
        constants.CLASSIFICATION_RULE,
    )


def mfg_name(value: str) -> None:
    """
    Validate that the input string is a valid manufacturer name.

    Valid manufacturer name is a non-empty string containing alphabets, spaces, and optionally '.', '-', '&', or digits (e.g., 'ST Microelectronics', 'Delta Pvt. Ltd', 'Hewlett-Packard', 'Procter & Gamble', '3M').

    Args:
        value (str): The manufacturer name string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the item format string pattern.
    """
    common.approve_or_raise(
        value,
        constants.MFG_NAME_PATTERN,
        TableLabelsV3.MFG_NAME,
        constants.MFG_NAME_RULE,
    )


def mfg_part_no(value: str) -> None:
    """
    Validate that the input string is a valid manufacturer part number.

    Valid manufacturer part number must contain at least one character and consist of alphabets and numbers, with optional '-', '_', or '.' characters. Whitespace and '*' are not allowed (e.g., 'LM358N.3B', 'SN74HC595N-TR', 'AT328P_U', 'BC547B').

    Args:
        value (str): The manufacturer part number string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the item format string pattern.
    """
    common.approve_or_raise(
        value,
        constants.MFG_PART_NO_PATTERN,
        TableLabelsV3.MFG_PART_NO,
        constants.MFG_PART_NO_RULE,
    )


def ul_vde_number(value: str) -> None:
    """
    Validate that the input string is a valid UL/VDE number.

    Valid UL/VDE number starts with 1–4 alphabets followed by 1–8 digits, optionally separated by a single '-' or space (e.g., 'E1234', 'UL 567890', 'VDE-12345678').

    Args:
        value (str): The UL/VDE number string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the UL/VDE number string pattern.
    """
    common.approve_or_raise(
        value,
        constants.UL_VDE_NO_PATTERN,
        TableLabelsV3.UL_VDE_NO,
        constants.UL_VDE_NO_RULE,
    )


def validated_at(value: str) -> None:
    """
    Validate that the input string is a valid validated-at string.

    Valid validated-at string is either empty or a list of tokens separated by '/' or ',' where each token is one of the following formats (case-sensitive): 'Pn', 'Pn.n', 'EBn', 'EBn.n', 'ECN', 'ECNn', 'MB', 'MP', or 'FOT' (e.g., '', 'P1/EB0/MP').

    Args:
        value (str): The validated-at string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the validated-at string pattern.
    """
    common.approve_or_raise(
        value,
        constants.VALIDATED_AT_PATTERN,
        TableLabelsV3.VALIDATED_AT,
        constants.VALIDATED_AT_RULE,
    )


def quantity(value: str) -> None:
    """
    Validate that the input string is a valid quantity string.

    Valid quantity string is a non-negative number (greater than or equal to zero), which may be an integer or a decimal with digits after the dot (e.g., '0', '2', '0.34').

    Args:
        value (str): The quantity string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the quantity string pattern.
    """
    common.approve_or_raise(
        value,
        constants.QUANTITY_PATTERN,
        TableLabelsV3.QUANTITY,
        constants.QUANTITY_RULE,
    )


def designator(value: str) -> None:
    """
    Validate that the input string is a valid designator string.

    Valid designator is either empty or a string that starts with 1–5 alphabets followed by either 1–5 digits or a single '+' or '-' (e.g., '', 'R1', 'ACL+', 'MP').

    Args:
        value (str): The designator string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the designator string pattern.
    """
    common.approve_or_raise(
        value,
        constants.DESIGNATOR_PATTERN,
        TableLabelsV3.DESIGNATORS,
        constants.DESIGNATOR_RULE,
    )


def unit_price(value: str) -> None:
    """
    Validate that the input string is a valid unit price.

    Valid unit price string is a non-negative number (>= 0). It may be an integer or a decimal number with digits after the dot (e.g., '0', '2', '0.34').

    Args:
        value (str): The unit price string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the unit price string pattern.
    """
    common.approve_or_raise(
        value,
        constants.PRICE_PATTERN,
        TableLabelsV3.UNIT_PRICE,
        constants.PRICE_RULE,
    )


def sub_total(value: str) -> None:
    """
    Validate that the input string is a valid sub-total price.

    Valid sub-total price string is a non-negative number (>= 0). It may be an integer or a decimal number with digits after the dot (e.g., '0', '2', '0.34').

    Args:
        value (str): The sub-total price string.

    Returns:
        None: Validation succeeds silently if the input string matches the required string pattern.

    Raises:
        ValueError: If the input does not match the sub-total string pattern.
    """
    common.approve_or_raise(
        value,
        constants.PRICE_PATTERN,
        TableLabelsV3.SUB_TOTAL,
        constants.PRICE_RULE,
    )
