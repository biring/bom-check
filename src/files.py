# manage file data

from src.cli import interfaces as cli
import os
import pandas as pd


def read_excel_file_data(file_path):
    """
    Read an Excel file and return its contents as a DataFrame if the file has only one tab.
    If the file has multiple tabs, prompt the user to select a tab.

    Parameters:
        file_path (str): The full path to the Excel file.

    Returns:
        pandas.DataFrame: The DataFrame containing the contents of the selected tab from the Excel file.

    Raises:
        ValueError: If reading the file fails.

    Example:
        # Example usage:
        excel_path = input("Enter the full path to the Excel file: ")
        data_frame = get_excel_file_data(excel_path)
        print(data_frame.head())  # Just an example to show the first few rows of the DataFrame
    """

    print()
    print('Reading excel file...')

    # Open the Excel file
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
    except Exception as e:
        raise FileExistsError(f'Excel file read from "{file_path}" FAILED.', e)

    print(f'Read of excel file from "{file_path}" successful.')

    # Check the number of tabs
    sheet_names = xls.sheet_names

    # Get which tab to read
    header_msg = 'available excel sheets'
    select_msg = 'Enter the number of the sheet to make a selection: '
    user_selection = cli.prompt_menu_selection(
        menu_items=sheet_names,
        header_msg=header_msg, select_msg=select_msg
    )
    sheet_name = sheet_names[user_selection]

    print()
    print(f'Reading sheet... ')

    # get tab as dataframe
    try:
        df = pd.read_excel(xls, sheet_name, header=None)
    except Exception as e:
        raise FileNotFoundError("Excel file read failed.", e)

    print(f'Sheet "{sheet_name}" read successful.')

    return df


def read_raw_excel_file_data(folder, file):
    """
    Read an Excel file and return its contents.

    Parameters:
        folder (str): The full path to the Excel file.
        file (str): The file name of the Excel file.

    Returns:
        Excel file data.

    Raises:
        ValueError: If reading the file fails.
    """

    print()
    print('Reading excel file...')

    # build a path to the file
    file_path = os.path.join(folder, file)
    # return full path as a raw string
    file_path = rf"{file_path}"

    # Open the Excel file
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
    except Exception as e:
        raise FileExistsError(f'Excel file read from "{file_path}" FAILED.', e)

    print(f'Read of excel file from "{file_path}" successful.')

    return xls


def get_user_selected_excel_file_sheet(xls) -> pd.DataFrame:

    # get a list of sheet names
    sheet_names = xls.sheet_names

    # Get which tab to read
    header_msg = 'available excel sheets'
    select_msg = 'Enter the number of the sheet to make a selection: '
    user_selection = cli.prompt_menu_selection(
        menu_items=sheet_names,
        header_msg=header_msg,
        select_msg=select_msg
    )
    sheet_name = sheet_names[user_selection]

    print()
    print(f'Reading sheet... ')

    # get tab as dataframe
    try:
        df = pd.read_excel(xls, sheet_name, header=None)
    except Exception as e:
        raise FileNotFoundError("Excel file read failed.", e)

    print(f'Sheet "{sheet_name}" read successful.')

    return df


def write_single_sheet_excel_file_data(folder, file, df) -> None:

    print()
    print(f'Writing excel file... ')

    # Force the file extension to lowercase to avoid case sensitivity issues.
    # For excel write using 'openpyxl', '.XLSX' does not work and the extention should be '.xlsx'.
    base_name, ext = os.path.splitext(file)
    file = base_name + ext.lower()  # Convert the extension to lowercase

    # Ensure that the file extension is '.xlsx' (in lowercase)
    if not file.endswith('.xlsx'):
        raise ValueError(f"The file extension is incorrect for {file}. Expected '.xlsx' for excel file write.")

    file_path = os.path.join(folder, file)
    # Good practice to make path OS independent
    file_path = os.path.normpath(file_path)

    try:
        df.to_excel(file_path, index=False, engine="openpyxl")  # Set index=False to exclude the DataFrame index from being written
    except Exception as e:
        raise FileExistsError(f'Excel file write to "{file_path}" FAILED.', e)

    print(f'Write of excel file to "{file_path}" successful.')

    return None
