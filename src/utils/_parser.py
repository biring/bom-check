"""
Utilities for parsing and validating common primitive data types.

This module provides strict parsing helpers and boolean-style "is_*" wrappers for quick validation without raising exceptions. All parse functions either return the expected typed value or raise a `ValueError` with context.

Example Usage:
    # Preferred usage via public package interface:
    from src.utils import parser
    if parser.is_integer("42"):
        value =parser.parse_to_integer("42")

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils._parser as parser
    iso_date = parse_to_iso_date_string("6/8/2025")

Dependencies:
 - Python >= 3.9
 - Standard Library: datetime, math, typing

Notes:
    - This module enforces strict parsing rules to avoid ambiguous cases (e.g., '1.0' is not treated as an integer).
    - Date parsing normalizes inputs to ISO format and ignores trailing time parts.
    - Designed to be used in BOM parsing, field validation, and data cleaning pipelines where type consistency is critical.
    - Use `is_*` functions for fast validation; use `parse_to_*` functions when a typed value is required.

License:
 - Internal Use Only
"""

__all__ = [
    # parser
    "is_float",
    "is_integer",
    "is_non_empty_string",
    "is_strict_empty_string",
    "is_valid_date_string",
    "parse_to_datetime",
    "parse_to_empty_string",
    "parse_to_float",
    "parse_to_integer",
    "parse_to_iso_date_string",
    "parse_to_non_empty_string",
]

import math
from datetime import datetime
from typing import Final


def is_valid_date_string(date_str: str) -> bool:
    """
    Check if the input string can be parsed to a valid date string.

    Args:
        date_str (str): The string to check.

    Returns:
        bool: True if the string can be parsed to a valid date string, False otherwise.
    """
    try:
        parse_to_iso_date_string(date_str)
        return True
    except ValueError:
        return False


def is_strict_empty_string(input_str: str) -> bool:
    """
    Check if the input string can be parsed to an empty string.

    Args:
        input_str (str): The string to check.

    Returns:
        bool: True if the string can be parsed to an empty string, False otherwise.
    """
    try:
        parse_to_empty_string(input_str)
        return True
    except ValueError:
        return False


def is_float(input_str: str) -> bool:
    """
    Check if the input string can be parsed to a float.

    Args:
        input_str (str): The string to check.

    Returns:
        bool: True if the string can be parsed to a float, False otherwise.
    """
    try:
        parse_to_float(input_str)
        return True
    except ValueError:
        return False


def is_integer(input_str: str) -> bool:
    """
    Check if the input string can be parsed to an integer.

    Args:
        input_str (str): The string to check.

    Returns:
        bool: True if the string can be parsed to an integer, False otherwise.
    """
    try:
        parse_to_integer(input_str)
        return True
    except ValueError:
        return False


def is_non_empty_string(input_str: str) -> bool:
    """
    Check if the input string can be parsed to a not empty string.

    Args:
        input_str (str): The string to check.

    Returns:
        bool: True if the string can be parsed to a not empty string, False otherwise.
    """
    try:
        parse_to_non_empty_string(input_str)
        return True
    except ValueError:
        return False


def parse_to_datetime(date_str: str) -> datetime:
    """
    Parse an input string into a datetime object using strict date rules.

    This function first normalizes the input using parse_to_iso_date_string(), which enforces:
        - valid formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
        - optional trailing time component (ignored)
        - mandatory successful conversion to canonical ISO 'YYYY-MM-DD'

    After normalization, it converts the canonical ISO string into a datetime.datetime object at midnight (00:00:00).

    Args:
        date_str (str): Raw date-like input string.

    Returns:
        datetime: Parsed datetime object (YYYY-MM-DD 00:00:00).

    Raises:
        ValueError: If the input cannot be parsed as a supported date format.
    """
    iso_str = parse_to_iso_date_string(date_str)
    try:
        return datetime.strptime(iso_str, "%Y-%m-%d")
    except ValueError as err:
        raise ValueError(f"'{date_str}' could not be parsed into a datetime. \n{err}") from err


def parse_to_iso_date_string(date_str: str) -> str:
    """
    Convert a string into a canonical ISO date string.

    The function attempts to parse the input against multiple date formats, optionally ignoring a trailing time component (separated by "T" or space). On success, it normalizes the output into a zero-padded ISO date string ("YYYY-MM-DD"). Non-zero-padded input is accepted.

    Supported formats:
        - YYYY-MM-DD (e.g., "2025-8-6", "2025-08-06")
        - DD/MM/YYYY (e.g., "6/8/2025", "06/08/2025")
        - MM/DD/YYYY (e.g., "8/6/2025", "08/06/2025")

    Args:
        date_str (str): Input string to parse.

    Returns:
        str: Canonical ISO date string in "YYYY-MM-DD" format.

    Raises:
        ValueError: If the input cannot be parsed as a valid date in the supported formats.
    """
    _ISO_DATE_FORMAT: Final[str] = "%Y-%m-%d"  # Always return canonical ISO date
    _SUPPORTED_DATE_FORMATS: Final[tuple[str, ...]] = ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y")

    raw_input: str = str(date_str)

    # Remove trailing time part if present (e.g., "2025-08-06T12:00" → "2025-08-06")
    date_component: str = raw_input
    for separator in ("T", " "):
        if separator in raw_input:
            date_component = raw_input.split(separator, 1)[0]
            break

    # Attempt parsing, accept non-zero-padded input
    for fmt in _SUPPORTED_DATE_FORMATS:
        try:
            dt = datetime.strptime(date_component, fmt)
            # Return canonical zero-padded string to normalize output
            return dt.strftime(_ISO_DATE_FORMAT)
        except ValueError:
            continue

    raise ValueError(
        f"'{date_str}' is not a valid date format. "
        f"Supported formats are YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY. "
    )


def parse_to_empty_string(input_str: str) -> str:
    """
    Parse a string to an empty ("") string.

    Converts the given input to a string and validates that it is empty. Useful when an empty field is required or used as a sentinel value.

    Args:
        input_str (str): Value to validate as an empty string.

    Returns:
        str: The validated empty string.

    Raises:
        ValueError: If the string is not empty.
    """
    s = str(input_str)

    # Empty string check: only "" passes, whitespace like " " is considered non-empty
    if s == "":
        return s

    raise ValueError("Input string is empty; a non-empty string is required.")


def parse_to_integer(input_str: str) -> int:
    """
    Parse a string to an integer.

    Converts the given input string to an integer without allowing float-like representations (e.g., '1.0' will raise). Use when a true integer type is required.

    Args:
        input_str (str): String to parse as an integer.

    Returns:
        int: The parsed integer value.

    Raises:
        ValueError: If the string is not a valid integer representation.
    """
    try:
        # int() naturally rejects float-like strings such as "1.0"
        return int(input_str)
    except (ValueError, TypeError) as err:
        raise ValueError(
            f"'{input_str}' is not a valid integer. "
            f"({type(err).__name__}: {err})"
        ) from err


def parse_to_float(input_str: str) -> float:
    """
    Parse a string to a float.

    Converts the given string to a Python float and rejects NaN or infinity explicitly. This function is suitable when downstream logic requires a numeric float that is guaranteed to be finite.

    Args:
        input_str (str): String to parse as a float.

    Returns:
        float: The parsed finite float value.

    Raises:
        ValueError: If the string is not a valid float representation or if the parsed value is NaN or infinite.
    """
    try:
        # Attempt parsing (captures bad syntax like "1.2.3" or non-numeric)
        value = float(input_str)
    except (ValueError, TypeError) as err:
        raise ValueError(
            f"'{input_str}' is not a valid float. "
            f"({type(err).__name__}: {err})"
        ) from err

    # Explicitly reject NaN and infinity to ensure downstream logic gets only finite values
    if math.isnan(value) or math.isinf(value):
        raise ValueError(F"'{input_str}' is not a finite float (NaN/Inf rejected). ")

    return value


def parse_to_non_empty_string(input_str: str) -> str:
    """
    Parse a string to a not empty string.

    Converts the input to a string and validates that it is non-empty string. Use when a string value is mandatory and blank values must be rejected.

    Args:
        input_str (str): Value to validate as a non-empty string.

    Returns:
        str: The validated non-empty string.

    Raises:
        ValueError: If the string is empty.
    """
    s = str(input_str)

    # Validate non-empty (strict: ' ' passes, '' fails)
    if s != "":
        return s

    raise ValueError(f"'{input_str} is an empty string. ")
