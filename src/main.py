"""
Application entry point and CLI orchestration layer for the electrical BOM processing system.

This module coordinates application startup, interactive menu presentation, workflow dispatching, and graceful termination by combining static options with dynamically provided controller actions.

Key Responsibilities:
	- Initialize and display application version and build metadata
	- Present and manage an interactive command-line menu
	- Route user selections to predefined processing workflows
	- Integrate dynamically generated controller actions into the menu
	- Handle user input validation, errors, and controlled termination scenarios

Example Usage:
    # Using command line interface (from project root context)
    python -m src.main

    # Called within a script (from project root context)
    from src.main import run_application
    run_application()

Dependencies:
	- Python version: >= 3.10

Notes:
	- Designed for interactive CLI execution rather than automated workflows
	- Relies on positional alignment between menu options and corresponding actions
	- Assumes external modules provide processing sequences and dynamic menu entries
	- Handles keyboard interrupts and unexpected errors without crashing

License:
	- Internal Use Only
"""
__all__ = [
    'run_application',
]

import application
import version
from cli import interfaces as cli
from controllers import interfaces as controller


def run_menu() -> bool | None:
    """
    Display the main menu, resolve the user's selection, and execute the corresponding action.

    Builds a composite menu consisting of legacy options followed by dynamically provided
    controller options. The user's selection is resolved by index:
    - Indices within the legacy range map to hardcoded application sequences.
    - Indices beyond the legacy range map to dynamically provided controller actions.
    - A selection of index 0 is treated as a normal exit signal and returns None.

    The function enforces safe bounds checking on the selection index and provides
    user-facing feedback for invalid selections. Keyboard interrupts are treated as
    a controlled exit, while unexpected exceptions are caught and reported.

    Returns:
        bool | None:
            True if a valid option was executed successfully,
            None if the user selected a normal exit,
            False if an error occurred or the user interrupted execution.

    Raises:
        Exception: Propagated only if not caught internally (all are currently caught).
    """
    # Build dynamic menu components from the controller layer; assumes positional alignment
    options, actions = controller.build_controller_menu()

    # Legacy options must remain ordered and aligned with hardcoded branching below
    legacy_options = [
        'Exit',
        'Process cBOM for cost walk',
        'Process cBOM for database upload',
        'Process eBOM for database upload'
    ]

    try:
        # Combine legacy and dynamic options into a single linear menu representation
        # Invariant: menu_options index directly maps to execution logic below
        menu_options = legacy_options + list(options)

        # Define prompt messages separately to keep UI concerns explicit and modifiable
        header_msg = 'main menu'
        select_msg = 'Enter the number of the menu option to execute: '

        # Delegate user input handling to CLI layer; assumes integer index is returned
        user_selection = cli.prompt_menu_selection(
            menu_items=menu_options,
            header_msg=header_msg,
            select_msg=select_msg,
        )

        # Branch 1: Selection falls within legacy options
        if user_selection < len(legacy_options):
            # Explicit index-based dispatch preserves backward compatibility
            if user_selection == 0:
                # Index 0 is reserved for graceful exit without error
                return None
            elif user_selection == 1:
                application.sequence_cbom_for_cost_walk()
            elif user_selection == 2:
                application.sequence_cbom_for_db_upload()
            elif user_selection == 3:
                application.sequence_ebom_for_db_upload()

        # Branch 2: Selection falls within dynamically generated options
        elif user_selection < len(menu_options):
            # Normalize index into actions list by removing legacy offset
            action_index = user_selection - len(legacy_options)

            # Invariant: actions list must align 1:1 with dynamic options
            # Assumes each action exposes a .run() method
            actions[action_index]().run()

        else:
            # Defensive guard: selection exceeds available options
            # This should only occur if CLI layer returns an invalid index
            print("WARNING! Invalid selection. Please select a valid option.")

    except KeyboardInterrupt:
        # Treat user interrupt as intentional termination, not an error
        print("\nUser selected to exit the application.")
        return False

    except Exception as e:
        # Catch-all for unexpected failures; prevents crash and surfaces error context
        print('*** ERROR ***')
        print(f"An error occurred: {e}")
        return False

    # Successful execution path
    return True


def show_title():
    """
    Display the application's version and build information.

    Retrieves version metadata from the version module and prints it to stdout.
    Assumes that the version module exposes __version__ and __build__ attributes.

    Returns:
        None: This function performs output only and does not return a value.
    """
    # Output version string; assumes attribute exists and is properly formatted
    print(f'Version {version.__version__} ')

    # Output build identifier; trailing space preserved for consistency with original behavior
    print(f'Build {version.__build__} ')


def run_application():
    """
    Execute the application entry point and manage the main menu loop lifecycle.

    Displays the application title once, then repeatedly invokes the menu handler
    until a termination condition is met. The loop behavior is controlled by the
    return value of run_menu():
    - True: Continue looping and display menu again.
    - None: Normal exit without error; terminate immediately.
    - False: Error or interrupt; allow user to acknowledge before exiting.

    Returns:
        None: This function controls program flow and does not return a value.
    """
    # Display application metadata before entering interactive loop
    show_title()

    # Infinite loop delegates exit control to run_menu return contract
    while True:
        result = run_menu()

        if result:
            # Successful execution; continue presenting menu
            continue

        elif result is None:
            # Graceful exit path; no user prompt required
            break

        elif not result:
            # Error or interrupt path; provide pause so user can read output
            print()
            input("\nPress Enter to close application...")
            break


if __name__ == "__main__":
    run_application()
