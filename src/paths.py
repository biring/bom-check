# manage paths to files and folders

import os
import re

from cli import interfaces as cli

def set_path_to_excel_file(folder, file):
    path = os.path.join(folder, file)
    # Good practice to make path OS independent
    path = os.path.normpath(path)
    return path


def get_path_to_input_file_folder():
    """
    Retrieve the path to the input data folder within the project directory structure.

    Returns:
        str: Path to the input data folder.
    """

    import os

    # Get path to current directory
    path = os.path.dirname(__file__)  # Get the directory of the current script

    # Split path to get to project folder. Based on project folder structure this is once level above 'src'
    if "src" in path:  # If "src" directory exists in the path
        path = os.path.split(path)[0]  # Move up one level to get to the project folder
    # Build path to input data folder. Based on project folder structure, this will be $project\data\input
    path = os.path.join(path, "data")  # Append "data" to the path
    path = os.path.join(path, "inputs")  # Append "input" to the path

    # Good practice to make path OS independent
    path = os.path.normpath(path)  # Normalize the path to ensure consistency across different operating systems

    # Ensure that the folder exists, if not, create it
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def get_path_to_excel_file_in_folder(folder_path):
    """
    Prompts the user to select an Excel file from the specified folder.

    Args:
    - folder_path (str): The path to the folder containing the Excel files.

    Returns:
    - str: The full path to the selected Excel file as a raw string.

    Raises:
    - FileNotFoundError: If no Excel files are found in the specified folder.
    """
    # get the list of files in the folder
    files = os.listdir(folder_path)

    # filter only Excel files
    excel_files = [file for file in files if re.match(r'.*\.xlsx$', file, re.IGNORECASE)]

    if not excel_files:
        raise FileNotFoundError(f'No Excel file found in the folder "{folder_path}"')

    # get user to make a selection
    header_msg = 'Available Excel files'
    select_msg = 'Enter the number of the file to open: '
    user_selection = cli.prompt_menu_selection(
        menu_items=excel_files,
        header_msg=header_msg,
        select_msg=select_msg,
    )
    # get the file name user selected
    selected_file = excel_files[user_selection]
    # build a path to the file
    full_path = os.path.join(folder_path, selected_file)
    # return full path as a raw string
    return rf"{full_path}"


def get_path_to_outputs_folder():
    """
    Retrieve the path to the output data folder within the project directory structure.
    If the folder does not exist, it will be created.

    This function assumes a specific project directory structure where the script is located
    within a directory named "src", and the project folder contains a "data" directory with an
    "outputs" subdirectory.

    Returns:
        str: Path to the output data folder.
    """

    import os

    # Get path to current directory
    path = os.path.dirname(__file__)  # Get the directory of the current script

    # Split path to get to project folder. Based on project folder structure this is once level above 'src'
    if "src" in path:  # If "src" directory exists in the path
        path = os.path.split(path)[0]  # Move up one level to get to the project folder

    # Build path to output data folder. Based on project folder structure, this will be $project/data/outputs
    path = os.path.join(path, "data", "outputs")

    # Ensure that the folder exists, if not, create it
    if not os.path.exists(path):
        os.makedirs(path)

    # Good practice to make path OS independent
    path = os.path.normpath(path)  # Normalize the path to ensure consistency across different operating systems

    return path


def get_selected_excel_file_name(folder_path):
    """
    Prompts the user to select an Excel file from the specified folder.

    Args:
    - folder_path (str): The path to the folder containing the Excel files.

    Returns:
    - str: The selected Excel file name.

    Raises:
    - FileNotFoundError: If no Excel files are found in the specified folder.
    """
    # get the list of files in the folder
    files = os.listdir(folder_path)

    # filter only Excel files
    excel_files = [file for file in files if re.match(r'.*\.xlsx$', file, re.IGNORECASE)]

    if not excel_files:
        raise FileNotFoundError(f'No Excel file found in the folder "{folder_path}"')

    # get user to make a selection
    header_msg = 'Available Excel files'
    select_msg = 'Enter the number of the file to open: '
    user_selection = cli.prompt_menu_selection(
        menu_items=excel_files,
        header_msg=header_msg,
        select_msg=select_msg,
    )
    # get the file name user selected
    selected_file = excel_files[user_selection]

    return selected_file
