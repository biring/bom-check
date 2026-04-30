from src import strings

import re
import pandas as pd


def search_row_matching_header(df: pd.DataFrame, str_list: list) -> int:

    is_header_found = False
    header_row_idx = -1

    # iterate over rows of the DataFrame
    for index, row in df.iterrows():
        # stop search after first header row is found
        if is_header_found:
            break
        else:
            # reset count of string match
            count = 0
        # iterate over each string that needs to be in the header row
        for element in str_list:
            # check if the string is partially matched in any cell of the current row
            if any(row.astype(str).str.contains(element)):
                count += 1
                # when all strings are found in a row we stop
                if count == len(str_list):
                    header_row_idx = index
                    is_header_found = True
                    break

    # If no match is found, raise an error
    if not is_header_found:
        header_search_strings = ", ".join(str_list)
        raise ValueError(f'Header row not found.\nSearching for strings [{header_search_strings}].')

    return header_row_idx


def set_top_row_as_header(df: pd.DataFrame) -> pd.DataFrame:

    # Extract the top row as header and ensure it is string type
    header = df.iloc[0].astype(str)
    # Remove the top row and reset index
    mdf = df.iloc[1:].reset_index(drop=True)
    # Set the header
    mdf.columns = header

    return mdf


def standardize_header_names(df: pd.DataFrame, new_str_list: list) -> pd.DataFrame:

    # Replace NaN values in column names with an empty string or string replace below will not work
    df.columns = df.columns.fillna('')

    # get each header string one at a time
    for old_string in df.columns:
        # Special case for comparison and debug message, so we don't get new line in debug message
        ref_string = re.sub(r'\n', '', old_string)  # Using re.sub() instead of str.replace()

        # Get the best matched string to the header string
        match_1 = strings.find_best_match_jaccard(ref_string, new_str_list)
        match_2 = strings.find_best_match_levenshtein(ref_string, new_str_list)
        # when all match search are the same
        if match_1 == match_2:
            # change the header string
            new_string = match_1
            df = df.rename(columns={old_string: new_string})
        else:
            new_string = ""
        # debug message
        print(f' {ref_string:30} -> {new_string:30} [{match_1},{match_2}]')

    return df
