"""
Helper utilities for colorized command-line interface output.

This module provides a consistent set of routines for rendering styled terminal messages using color semantics for different message types such as errors, warnings, and informational output, as well as generating formatted prompts for user input.

Key Responsibilities:
	- Render error, warning, success, informational, and log messages with distinct color formatting
	- Ensure terminal styling is reset after each output to prevent unintended color propagation
	- Provide a formatted prompt string suitable for interactive input workflows
	- Initialize terminal color handling for cross-platform compatibility
	- Offer a diagnostic routine to validate color rendering behavior

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
    import src.cli._show as show
	show.show_error("Something went wrong")

Dependencies:
	- Python version: >= 3.9
	- Standard Library: None

Notes:
	- Designed for internal CLI usage and not intended as a public interface
	- All display functions write directly to standard output except prompt generation which returns a string
	- Relies on terminal support for ANSI color codes via an external compatibility layer

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

from colorama import init, Fore, Style

# Initialize colorama to auto-reset styles after each print
init(autoreset=True)


def show_error(msg: str) -> None:
    """
    Print an error message in red.

    Applies a red foreground color to the provided message and ensures that terminal styling is reset afterward to avoid color bleed into subsequent output.

    Args:
        msg (str): The error message to display.

    Returns:
        None
    """
    # Apply red foreground color to signal error severity; reset styling explicitly to prevent bleed
    print(f"{Fore.RED}{msg}{Style.RESET_ALL}")


def show_header(msg: str) -> None:
    """
    Print a header message in bright white.

    Prepends a newline to visually separate sections and applies a bright white foreground color for emphasis. Styling is reset after printing to maintain terminal consistency.

    Args:
        msg (str): The header text to display.

    Returns:
        None
    """
    # Prepend newline to visually separate header from prior output; use bright white for emphasis
    print(f"\n{Fore.LIGHTWHITE_EX}{msg}{Style.RESET_ALL}")


def show_info(msg: str) -> None:
    """
    Print an informational message in the default terminal color.

    Explicitly resets styling before and after the message to neutralize any previously applied color state and ensure consistent rendering.

    Args:
        msg (str): The informational message to display.

    Returns:
        None
    """
    # Reset style before and after to guarantee neutral color regardless of prior state
    print(f"{Style.RESET_ALL}{msg}{Style.RESET_ALL}")


def show_log(msg: str) -> None:
    """
    Print a log message in gray.

    Uses a light black (gray) foreground color to indicate low-priority or diagnostic output. Styling is reset after printing.

    Args:
        msg (str): The log message to display.

    Returns:
        None
    """
    # Use subdued gray color for low-importance logs; reset to prevent affecting subsequent output
    print(f"{Fore.LIGHTBLACK_EX}{msg}{Style.RESET_ALL}")


def show_prompt(msg: str) -> str:
    """
    Return a prompt string formatted in cyan.

    Does not print directly; returns a colorized string intended for use with input() so that the prompt retains styling when displayed.

    Args:
        msg (str): The prompt text to display.

    Returns:
        str: The formatted prompt string with cyan color applied.
    """
    # Return colored string instead of printing to preserve formatting when used with input()
    return f"{Fore.CYAN}{msg}{Style.RESET_ALL}"


def show_success(msg: str) -> None:
    """
    Print a success message in green.

    Applies a green foreground color to indicate successful operations and resets styling afterward.

    Args:
        msg (str): The success message to display.

    Returns:
        None
    """
    # Use green to signal success state; ensure reset to avoid color bleed
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")


def show_warning(msg: str) -> None:
    """
    Print a warning message in yellow.

    Applies a yellow foreground color to indicate cautionary output and resets styling afterward.

    Args:
        msg (str): The warning message to display.

    Returns:
        None
    """
    # Use yellow to signal warnings; reset styling to prevent unintended propagation
    print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")


def test_colors() -> None:
    """
    Execute a demonstration of CLI color output using helper functions and raw Colorama foreground colors.

    Exercises semantic helper functions followed by direct Colorama color constants to validate rendering and ensure styling resets correctly between outputs. Writes directly to stdout.

    Returns:
        None
    """
    # Delineate start of helper-based output test for readability
    show_header("=== TEST: CLI COLOR OUTPUT ===")

    # Validate each semantic output helper renders correctly and resets styling
    show_info("This is an info message")
    show_success("This is a success message")
    show_warning("This is a warning message")
    show_error("This is an error message")
    show_log("This is a log message")

    # Begin raw Colorama constant test section to validate direct usage outside helpers
    show_header("=== TEST: RAW COLORAMA FORE COLORS ===")

    # Explicit ordered mapping ensures deterministic output across runs
    color_pairs = [
        ("BLACK", Fore.BLACK),
        ("RED", Fore.RED),
        ("GREEN", Fore.GREEN),
        ("YELLOW", Fore.YELLOW),
        ("BLUE", Fore.BLUE),
        ("MAGENTA", Fore.MAGENTA),
        ("CYAN", Fore.CYAN),
        ("WHITE", Fore.WHITE),
        ("LIGHTBLACK_EX", Fore.LIGHTBLACK_EX),
        ("LIGHTRED_EX", Fore.LIGHTRED_EX),
        ("LIGHTGREEN_EX", Fore.LIGHTGREEN_EX),
        ("LIGHTYELLOW_EX", Fore.LIGHTYELLOW_EX),
        ("LIGHTBLUE_EX", Fore.LIGHTBLUE_EX),
        ("LIGHTMAGENTA_EX", Fore.LIGHTMAGENTA_EX),
        ("LIGHTCYAN_EX", Fore.LIGHTCYAN_EX),
        ("LIGHTWHITE_EX", Fore.LIGHTWHITE_EX),
    ]

    # Iterate deterministically and print each color name using its foreground code
    # Reset after each print is critical to prevent cascading color effects
    for color_name, color_code in color_pairs:
        print(f"{color_code}{color_name}{Style.RESET_ALL}")

    # Signal completion of the test routine
    show_header("=== TEST COMPLETE ===")
