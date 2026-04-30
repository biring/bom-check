"""
Helpers for interactive console input handling.

This module provides controlled wrappers around user input operations to ensure consistent prompt formatting, centralized validation, and normalized exception messaging for command-line interfaces.

Key Responsibilities:
	- Render user prompts with consistent formatting and colorization
	- Capture raw string input from standard input without modification
	- Normalize EOF and interruption exceptions with deterministic messages
	- Repeatedly prompt for integer input until valid numeric data is provided
	- Delegate integer parsing to a centralized validation utility
	- Display warning messages for invalid input without terminating execution

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	import src.cli._request as request
	value = request.integer_input("Enter a number: ")

Dependencies:
	- Python version: >= 3.9
	- Standard Library: builtins, exceptions
	- Internal: src.utils, src.cli._show

Notes:
	- Intended for interactive CLI workflows requiring consistent user experience
	- Input parsing relies on an external utility to enforce uniform validation rules
	- Exception messages are normalized to improve testability and cross-environment consistency
	- Integer input loop continues indefinitely until valid input or interruption occurs

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

import src.utils as utils

# noinspection PyProtectedMember
from . import _show as show

_ERR_INTEGER_INPUT = "Invalid user input. "
_ERR_EOF = "Input stream closed unexpectedly. No input could be read."
_ERR_CTRL_ABORT = "Input was interrupted by the user (Ctrl+C)."


def string_input(prompt: str) -> str:
    """
    Prompt the user for a string value.

    Displays a colorized prompt and returns the user’s raw input. Wraps the built-in input function to enforce consistent prompt formatting and to normalize exception messages for EOF and user interruption events.

    Args:
        prompt (str): The text prompt to display to the user.

    Returns:
        str: The user’s entered string exactly as provided.

    Raises:
        EOFError: If the input stream is closed before reading any input.
        KeyboardInterrupt: If the user aborts input with Ctrl+C.
    """
    try:
        # Delegate prompt rendering to the internal show utility to ensure consistent CLI formatting and colorization
        formatted_prompt = show.show_prompt(prompt)

        # Read raw user input without modification to preserve exact user-provided value
        return input(formatted_prompt)

    except EOFError:
        # Normalize EOFError message to provide deterministic and testable error output across environments
        raise EOFError(_ERR_EOF)

    except KeyboardInterrupt:
        # Normalize interrupt message to provide consistent handling for Ctrl+C across CLI workflows
        raise KeyboardInterrupt(_ERR_CTRL_ABORT)


def integer_input(prompt: str) -> int:
    """
    Prompt the user until a valid integer is entered.

    Continuously prompts the user using the string_input wrapper and attempts to parse the result into an integer using a centralized parser. Invalid numeric input triggers a warning message and retries indefinitely until valid input is received or the input stream is interrupted.

    Args:
        prompt (str): The text prompt to display to the user.

    Returns:
        int: The validated integer parsed from user input.

    Raises:
        EOFError: If the input stream is closed before reading input.
        KeyboardInterrupt: If the user aborts input with Ctrl+C.
    """
    while True:
        try:
            # Obtain raw user input through the controlled string_input wrapper to ensure consistent prompt behavior and exception normalization
            user_input = string_input(prompt)

            # Delegate numeric parsing to centralized utility to enforce consistent validation rules across the codebase
            # Assumes parser raises ValueError for invalid integer representations
            parsed_integer = utils.parser.parse_to_integer(user_input)

            # Successful parse is considered authoritative; exit loop immediately
            return parsed_integer

        except ValueError:
            # Invalid numeric input is treated as a recoverable error; notify user and retry without exiting
            # No mutation of state occurs between retries; loop invariant remains unchanged
            show.show_warning(_ERR_INTEGER_INPUT)
