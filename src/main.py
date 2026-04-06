"""
Main module for the Electrical BOM (Bill of Materials) Processor.

This module provides the main entry point for interacting with the Electrical BOM
processing system. It includes a menu interface that allows users to select various
options for processing both cBOM and eBOM.

Usage:
    - Run this file to interact with the system. The user will be prompted with a menu
      to select one of the available options for processing the BOMs.
"""

import application
import console
import version

from controllers import interfaces as controller


def run_menu() -> bool:
    """
    Displays the main menu and processes the user's selection.

    This function presents a list of options to the user. The user selects an option
    by entering the corresponding number. Based on the user's selection, the appropriate
    function is called to process either the cBOM or eBOM for different tasks.

    If the user selects an invalid option, a warning message is displayed. In the event
    of an unexpected error, an error message is shown, and the function returns False.

    Returns:
        bool: True if the menu was executed successfully and a valid option selected,
              False if an error occurred or an invalid option selected.
    """
    options, actions = controller.build_controller_menu()

    legacy_options = ['Process cBOM for cost walk',
                      'Process cBOM for database upload',
                      'Process eBOM for database upload']

    try:
        # list of main menu option
        menu_options = legacy_options + list(options)
        # get user to make a selection
        header_msg = 'main menu'
        select_msg = 'Enter the number of the menu option to execute'
        user_selection = console.get_user_selection(menu_options, header_msg=header_msg, select_msg=select_msg)
        # run user selection
        if user_selection < len(legacy_options):
            if user_selection == 0:
                application.sequence_cbom_for_cost_walk()
            elif user_selection == 1:
                application.sequence_cbom_for_db_upload()
            elif user_selection == 2:
                application.sequence_ebom_for_db_upload()
        elif user_selection < len(menu_options):
            action_index = user_selection - len(legacy_options)
            actions[action_index]().run()
        else:
            print("WARNING! Invalid selection. Please select a valid option.")
    except KeyboardInterrupt:
        print("\nUser selected to exit the application.")
        return False
    except Exception as e:
        print('*** ERROR ***')
        print(f"An error occurred: {e}")
        return False

    return True


def show_title():
    """
    Displays the version and build information of the application.

    This function prints the version and build information of the application as defined
    in the version module.

    Example:
        Version 1.0.0
        Build 12345
    """
    print(f'Version {version.__version__} ')
    print(f'Build {version.__build__} ')


def main():
    """
    Main function to run the application.

    This function displays the application title and enters a loop that displays
    and handles the main menu options. The loop continues to run until the user exits
    the application. After exiting, a message is printed to indicate the application is closing.
    """
    # Menu title
    show_title()

    # Forever loop
    while run_menu():
        pass

    # Exit message
    print()
    print("Exiting application.")


if __name__ == "__main__":
    main()
