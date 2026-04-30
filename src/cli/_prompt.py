"""
CLI helpers for prompting the user for values and menu selections.

Example Usage:
    # Preferred usage via package interface:
    from src.cli import interfaces as cli
    choice = cli.menu_selection(["alpha", "bravo", "charlie"])

    # Direct module usage in internal scripts or tests:
    from src.cli import _prompt as prompt
    text = prompt.string_value("Enter new value: ")

Dependencies:
 - Python >= 3.10
 - Standard Library: None
 - External Packages: None

Notes:

License:
 - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from . import _request as request
from . import _show as show

_DEFAULT_MENU_HEADER = "Menu options"
_DEFAULT_MENU_PROMPT = "Enter a number to make menu selection: "
_DEFAULT_STRING_VALUE_PROMPT = "Enter new value: "

_ERR_MENU_EMPTY = "Empty menu provided for user selection. "
_ERR_MENU_SELECTION = "Invalid menu selection. "
_ERR_CLI_MODULE = "Unexpected problem with Command Line Interface. "


def prompt_for_string_value(select_msg: str = _DEFAULT_STRING_VALUE_PROMPT) -> str:
    """
    Prompt the user for a string value via the CLI request interface.

    Delegates input collection to the request.string_input helper and preserves
    user-triggered termination signals. Any unexpected exception is treated as
    an internal CLI failure and wrapped in a RuntimeError.

    Args:
        select_msg (str, optional): Prompt message displayed to the user. Defaults to _DEFAULT_STRING_VALUE_PROMPT.

    Returns:
        str: The string value entered by the user.

    Raises:
        EOFError: Propagated if the user signals end-of-file during input.
        KeyboardInterrupt: Propagated if the user interrupts input (e.g., Ctrl+C).
        RuntimeError: Raised if an unexpected error occurs within the CLI subsystem.
    """
    try:
        # Delegate to request layer to centralize input handling and formatting logic
        # Assumes request.string_input enforces its own validation and user messaging
        return request.string_input(select_msg)
    except (EOFError, KeyboardInterrupt):
        # Preserve exact user-exit semantics; upstream callers may rely on these signals
        raise
    except Exception as error:
        # Catch-all for unexpected failures (e.g., formatting issues, dependency bugs)
        # Original exception is chained for debugging purposes
        raise RuntimeError(
            f"{_ERR_CLI_MODULE}"
            f"\n{error}"
        ) from error


def prompt_menu_selection(menu_items: list[str], header_msg: str = _DEFAULT_MENU_HEADER,
                          select_msg: str = _DEFAULT_MENU_PROMPT) -> int:
    """
    Prompt the user to select an option from a menu and return the selected index.

    Displays a numbered menu, validates user input against bounds, and repeatedly
    prompts until a valid selection is made. A single-item menu short-circuits to
    avoid unnecessary prompting. User-triggered termination signals are preserved.

    Args:
        menu_items (list[str]): List of menu option labels; index position defines selection value.
        header_msg (str, optional): Header text displayed above the menu. Defaults to _DEFAULT_MENU_HEADER.
        select_msg (str, optional): Prompt message requesting user input. Defaults to _DEFAULT_MENU_PROMPT.

    Returns:
        int: Zero-based index of the selected menu item.

    Raises:
        ValueError: If menu_items is empty.
        EOFError: Propagated if the user signals end-of-file during input.
        KeyboardInterrupt: Propagated if the user interrupts input (e.g., Ctrl+C).
        RuntimeError: Raised if an unexpected error occurs within the CLI subsystem.
    """
    # Determine number of selectable items; invariant: menu_size >= 0
    menu_size = len(menu_items)

    # Enforce invariant: menu must contain at least one item to be meaningful
    if menu_size == 0:
        raise ValueError(_ERR_MENU_EMPTY)

    # Optimization and UX decision: avoid prompting when only one valid choice exists
    # Always return index 0 (menu_size - 1 when size == 1)
    if menu_size == 1:
        return menu_size - 1

    # Render menu header in a normalized uppercase format for visual emphasis
    show.show_header(f'*** {header_msg.upper()} ***')

    # Enumerate menu items with explicit indices to define valid selection bounds
    for index, label in enumerate(menu_items):
        # Display each option; invariant: index maps directly to return value
        show.show_info(f"[{index}] {label}")

    # Loop until valid input is received or user exits explicitly
    while True:
        try:
            # Delegate integer parsing and input handling to request layer
            user_selection = request.integer_input(select_msg)

            # Validate selection against inclusive bounds [0, menu_size - 1]
            # Explicit bounds check prevents reliance on downstream errors
            if 0 <= user_selection <= menu_size - 1:
                return user_selection

            # Invalid but well-formed integer; notify user and continue loop
            show.show_warning(_ERR_MENU_SELECTION)
        except (EOFError, KeyboardInterrupt):
            # Preserve user intent to exit; do not intercept or transform
            raise
        except Exception as error:
            # Catch-all for unexpected failures (e.g., request layer bugs, formatting issues)
            # Original exception is chained for debugging purposes
            raise RuntimeError(
                f"{_ERR_CLI_MODULE}"
                f"\n{error}"
            ) from error