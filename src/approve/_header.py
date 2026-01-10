"""
Field validation helpers for BOM headers and metadata.

This module defines assertion-style validators that enforce formatting and value rules for Bill of Materials (BOM) header fields. Each validator raises a `ValueError` with descriptive guidance if the input does not
meet the required specification.

Example Usage:
    # Preferred usage via package interface:
    from src.approve import interfaces as approve
    approve.model_number("ABC1234X")

    # Direct usage (internal scripts or unit tests only):
    from src.approve import header as approve
    approve.bom_date("2025-08-06")

Dependencies:
    - Python >= 3.9
    - Standard Library: re, datetime


Notes:
    - Each validator succeeds silently (returns None) if the input is valid.
    - On failure, a ValueError is raised with both generic and field-specific error text for debugging or user feedback.
    - Regex patterns and rule strings are centralized in `_constants` for consistency and reuse.
    - Intended for internal use within the BOM parsing pipeline.

License:
 - Internal Use Only
"""

__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing

import src.utils as utils

from src.schemas.interfaces import (
    HeaderLabelsV3,
)

from . import _constants as constants


def model_number(value: str) -> None:
    """
    Validate that the input string is a valid model number.

    A valid model number starts with 2–3 uppercase letters, followed by 3–4 digits, and may optionally end with up 0-3 capital letters. (e.g., "AB123", "ABC1234XYX").

    Args:
        value (str): The candidate model number string.

    Returns:
        None: Validation succeeds silently if the input matches the required format.

    Raises:
        ValueError: If the input does not match the model-number pattern.
    """
    # Ensure value matches the precompiled regex pattern
    if not constants.MODEL_NUMBER_PATTERN.fullmatch(value):
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.MODEL_NO, b=value)
            + constants.MODEL_NUMBER_RULE.format(a=HeaderLabelsV3.MODEL_NO)
        )


def board_name(value: str) -> None:
    """
    Validate that the input string is a valid board name.

    A valid board name starts with a letter, may contain letters, digits, and spaces, and must end exactly with "PCBA" (uppercase), e.g., "Main Control PCBA".

    Args:
        value (str): The candidate board name string.

    Returns:
        None: Validation succeeds silently if the input matches the required format.

    Raises:
        ValueError: If the input does not match the board-name pattern.
    """
    # Ensure value matches the precompiled regex pattern
    if not constants.BOARD_NAME_PATTERN.fullmatch(value):
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.BOARD_NAME, b=value)
            + constants.BOARD_NAME_RULE.format(a=HeaderLabelsV3.BOARD_NAME)
        )


def board_supplier(value: str) -> None:
    """
    Validate that the input string is a valid board supplier name.

    A valid supplier name starts with a capital letter, may include letters, digits, and spaces, and must be at least 3 characters long.

    Args:
        value (str): The candidate supplier name string.

    Returns:
        None: Validation succeeds silently if the input matches the required format.

    Raises:
        ValueError: If the input does not match the board-supplier pattern.
    """
    # Ensure value matches the precompiled regex pattern
    if not constants.BOARD_SUPPLIER_PATTERN.fullmatch(value):
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.BOARD_SUPPLIER, b=value)
            + constants.BOARD_SUPPLIER_RULE.format(a=HeaderLabelsV3.BOARD_SUPPLIER)
        )


def build_stage(value: str) -> None:
    """
    Validate that the input string is a valid build stage label.

    Accepted formats include (case-sensitive):
      - "Pn" or "Pn.n" (e.g., "P1", "P2.1")
      - "EBn" or "EBn.n" (e.g., "EB0", "EB1.2")
      - "ECN" or "ECNn" (e.g., "ECN", "ECN2")
      - "MB", "MP", or "FOT"

    Args:
        value (str): The candidate build stage string.

    Returns:
        None: Validation succeeds silently if the input matches the required format.

    Raises:
        ValueError: If the input does not match the build-stage pattern.
    """
    # Ensure value matches the precompiled regex pattern
    if not constants.BUILD_STAGE_PATTERN.fullmatch(value):
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.BUILD_STAGE, b=value)
            + constants.BUILD_STAGE_RULE.format(a=HeaderLabelsV3.BUILD_STAGE)
        )


def bom_date(value: str) -> None:
    """
    Validate that the input string is a BOM date in one of the allowed exact formats.

    Allowed date formats (zero-padded where applicable):
      - "YYYY-MM-DD"
      - "DD/MM/YYYY"
      - "MM/DD/YYYY"

    If a time component is present (e.g., "2025-08-06T12:30" or "2025-08-06 12:30"), only the date portion before the 'T' or space is validated.

    Args:
        value (str): The candidate BOM date string.

    Returns:
        None: Validation succeeds silently if the input parses to an allowed format.

    Raises:
        ValueError: If the input cannot be parsed into any allowed date format.
    """
    # Ensure value parses to an iso date format
    try:
        utils.parser.parse_to_iso_date_string(value)
    except ValueError as err:
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.BOM_DATE, b=value)
            + f"{err}") from err


def material_cost(value: str) -> None:
    """
    Validate that the input string is a valid material cost.

    A valid material cost is a non-negative float and must match the cost pattern (e.g., "0", "0.00", "0.12", "12.5").

    Args:
        value (str): The candidate material cost string.

    Returns:
        None: Validation succeeds silently if the input is a float >= 0.0 and matches the pattern.

    Raises:
        ValueError: If the input is not a float >= 0.0 or does not match the cost pattern.
    """
    # Ensure value parses to a float more than zero and matches the precompiled regex pattern
    try:
        if utils.parser.parse_to_float(value) < 0 or not constants.COST_PATTERN.fullmatch(value):
            raise ValueError
    except ValueError:
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.MATERIAL_COST, b=value)
            + constants.COST_RULE.format(a=HeaderLabelsV3.MATERIAL_COST)
        )


def overhead_cost(value: str) -> None:
    """
    Validate that the input string is a valid overhead cost.

    A valid overhead cost is a non-negative float and must match the cost pattern (e.g., "0", "0.00", "0.12", "12.5").

    Args:
        value (str): The candidate overhead cost string.

    Returns:
        None: Validation succeeds silently if the input is a float >= 0.0 and matches the pattern.

    Raises:
        ValueError: If the input is not a float >= 0.0 or does not match the cost pattern.
    """
    # Ensure value parses to a float more than zero and matches the precompiled regex pattern
    try:
        if utils.parser.parse_to_float(value) < 0 or not constants.COST_PATTERN.fullmatch(value):
            raise ValueError
    except ValueError:
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.OVERHEAD_COST, b=value)
            + constants.COST_RULE.format(a=HeaderLabelsV3.OVERHEAD_COST)
        )


def total_cost(value: str) -> None:
    """
    Validate that the input string is a valid total cost.

    A valid total cost is a non-negative float and must match the cost pattern (e.g., "0", "0.00", "0.12", "12.5").

    Args:
        value (str): The candidate total cost string.

    Returns:
        None: Validation succeeds silently if the input is a float >= 0.0 and matches the pattern.

    Raises:
        ValueError: If the input is not a float >= 0.0 or does not match the cost pattern.
    """
    # Ensure value parses to a float more than zero and matches the precompiled regex pattern
    try:
        if utils.parser.parse_to_float(value) < 0 or not constants.COST_PATTERN.fullmatch(value):
            raise ValueError
    except ValueError:
        # Raise error with both generic and field-specific guidance
        raise ValueError(
            constants.GENERIC_VALUE_ERROR_MSG.format(a=HeaderLabelsV3.TOTAL_COST, b=value)
            + constants.COST_RULE.format(a=HeaderLabelsV3.TOTAL_COST)
        )
