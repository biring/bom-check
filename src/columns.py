import pandas as pd


def get_single_header_index(df, reference_string, full_match=True):
    """
    Retrieve the index of a single header in the DataFrame based on a reference string.
    Search is case-insensitive

    Parameters:
    - df (DataFrame): The pandas DataFrame containing the headers.
    - reference_string (str): The string to match against the column headers.
    - full_match (bool): If True, perform a full string match against the header names.
                          If False, allow partial matches.

    Returns:
    - header_index (int): The index of the matched header.

    Raises:
    - ValueError: If no header matches the reference string or if more than one header matches.
    """
    # Get a list of header indices that match the string
    matched_headers_list = []
    for header_index, header_name in enumerate(list(df.columns)):
        if full_match:
            # compare is case-insensitive
            if reference_string.lower() == header_name.lower():
                matched_headers_list.append(header_index)
        else:
            # compare is case-insensitive
            if reference_string.lower() in header_name.lower():
                matched_headers_list.append(header_index)

    # We only expect one match
    if len(matched_headers_list) == 1:
        header_index = matched_headers_list[0]
    # Raise an error if more than one column matches
    elif len(matched_headers_list) > 1:
        raise ValueError("More than one header matched the reference string.")
    # Raise an error if no partial match is found
    else:
        raise ValueError("No header matched the reference string.")

    return header_index


def refactor_string_if_matched(df, string_column, match_column):
    count = 0

    # Get one pattern at a time
    for _, row_pattern in df.iterrows():
        pattern = row_pattern.iloc[string_column]
        for index, row_data in df.iterrows():
            data = row_data.iloc[match_column]
            result = data.replace(pattern, "")

            # when data has been updated
            if result != data:
                # for debug keep track of number of items changed
                count += 1
                # print(f"In row {index} found {pattern} in {data} so changed it to {result}")
                # replace the data string
                df.at[index, df.columns[match_column]] = result

    # message for how many rows changed
    print(f"{count} rows updated")

    return df


def delete_columns_with_unwanted_build_data(df: pd.DataFrame, build_dict: dict) -> pd.DataFrame:

    # Get the value associated with the first key
    first_key = list(build_dict.keys())[0]
    first_value = build_dict[first_key]

    # Create a list of elements that start at zero and go up to the first build colum
    columns_to_keep = list(range(0, first_value))
    # get the key for the build analyse
    selected_index = 0
    if len(build_dict) > 1:
        # prompt user to select a build for analysis
        print()
        print("Data for multiple builds found: ")
        for index, key in enumerate(build_dict, start=1):
            print(f"[{index}]. {key}")
        # Prompt user to select an element by number
        while True:
            try:
                selected_index = int(input("Enter the number corresponding to the build you want to keep: ")) - 1
                # Check if the entered number is within the valid range
                if selected_index < 0 or selected_index >= len(build_dict):
                    print("Invalid element number. Please enter a valid number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    # Get the selected element
    selected_key = list(build_dict.keys())[selected_index]

    start_value = build_dict[selected_key]
    end_value = start_value + 6
    if end_value > len(df.columns):
        end_value = len(df.columns)
    # Generating list with the selected value and the next consecutive five numbers
    columns_to_keep.extend(list(range(start_value, end_value)))

    # Creating a new DataFrame with only the selected columns
    new_df = df[columns_to_keep]

    return new_df


def rename_and_reorder_headers(df: pd.DataFrame, item_list: list) -> pd.DataFrame:

    order_list = []
    for item in item_list:
        ref = item[0]
        match = item[1]
        column_index = get_single_header_index(df, ref, match)
        # New header name
        label = item[2]
        # Change header name by index
        df = df.rename(columns={df.columns[column_index]: label})
        order_list.append(label)

    # Reorder DataFrame by the provided list and drop remaining columns
    df = df[order_list]

    return df


def reorder_header_to_list(df: pd.DataFrame, order: list) -> pd.DataFrame:
    # Reorder DataFrame by the provided list and drop remaining columns
    mdf = df[order]
    return mdf

def fill_empty_item_cells(df: pd.DataFrame, item: str, component: str, designatorHdr: str) -> pd.DataFrame:
    """
    Fills empty cells in the specified item column based on rules using the component column.

    The function processes the DataFrame row by row:
    - If a cell in the `item` column is empty:
      * If the corresponding `component` cell contains "ALT", the value is copied from the previous row in the `item` column.
      * If the corresponding `designator` cell matched above row, the value is copied from the previous row in the `item` column.
      * Otherwise, the cell is filled with the next sequential item number (derived from the maximum existing number).
    - Non-empty cells remain unchanged.

    Args:
        df (pd.DataFrame): Input DataFrame containing the data.
        item (str): The column name where empty values need to be filled.
        component (str): The column name used to determine if a row is an "ALT" case.

    Returns:
        pd.DataFrame: The updated DataFrame with empty `item` cells filled.
    """
    print(f' Filling empty cells in the "{item}" column with values from the row above.')

    # Get the total number of rows in the DataFrame
    num_rows = len(df)

    # Counter to track the number of cells updated
    counter = 0

    # Define what is considered an empty cell
    empty = ""

    # Get the max item number
    s = pd.to_numeric(df[item], errors="coerce")  # blanks -> NaN, numbers stay numeric
    next_item_number = (int(s.max()) if s.notna().any() else 0) + 1
    
    # Loop through the DataFrame starting from the second row (index 1)
    for n in range(1, num_rows):
        # Check if the current cell in the specified column is empty
        if df.iloc[n][item] == empty:
            # When it is an alternative
            if "ALT" in df.iloc[n][component]:
                # Use the number from above
                new_value = df.iloc[n - 1, df.columns.get_loc(item)]
            elif df.iloc[n][designatorHdr] == df.iloc[n-1][designatorHdr]:
                # Use the number from above
                new_value = df.iloc[n - 1, df.columns.get_loc(item)]
            else:
                # Assign the next number
                new_value = next_item_number
                next_item_number += 1
            # Log the change from the previous value to the current one
            print(f'  Changed "{df.iloc[n, df.columns.get_loc(item)]}" to "{new_value}"')
            # Fill the empty cell with the value from the previous row
            df.iloc[n, df.columns.get_loc(item)] = new_value
            counter += 1

    # Print a summary of the number of cells updated
    print(f' {counter} cells updated.')

    return df

def fill_empty_cell_using_data_from_above_alternative(df: pd.DataFrame, item: str, column: str) -> pd.DataFrame:
    """
    Fills empty cells in the specified column with the value from the previous row,
    but only if the value in the 'item' column matches between the current row
    and the previous row.

    This function checks if the 'item' column value in the current row matches the value in
    the previous row. If both the 'item' value matches and the specified column contains
    an empty cell, the empty cell is filled with the value from the previous row.

    Args:
    - df (pd.DataFrame): The DataFrame containing the data to modify.
    - item (str): The column name to check for matching values between consecutive rows.
    - column (str): The column to be updated with the previous row's value if conditions are met.

    Returns:
    - pd.DataFrame: The updated DataFrame after filling matching empty cells with the previous row's value.
    """

    # Print message indicating the operation is starting
    print(f' Filling empty cells in "{column}" column with values from the row above (conditional on matching "{item}" column).')

    # Get the total number of rows in the DataFrame
    num_rows = len(df)

    # Counter to track the number of cells updated
    counter = 0

    # Define what is considered an empty cell
    empty = ""

    # Iterate through the rows starting from index 1 (second row)
    for n in range(1, num_rows):
        # Check if the 'item' value matches between the current and previous row
        is_item_match = df.iloc[n][item] == df.iloc[n - 1][item]

        # Check if the current cell in the specified column is empty
        is_empty = df.iloc[n][column] == empty

        # If both conditions are met, fill the empty cell with the previous row's value
        if is_item_match and is_empty:
            # Log the change from the previous value to the current one
            print(f'  changed "{df.iloc[n, df.columns.get_loc(column)]}" to "{df.iloc[n - 1, df.columns.get_loc(column)]}"')
            # Fill the current empty cell with the value from the previous row
            df.iloc[n, df.columns.get_loc(column)] = df.iloc[n - 1, df.columns.get_loc(column)]
            counter += 1

    # Print a summary of the number of cells updated
    print(f' {counter} cells updated.')

    return df

def replace_alt_label_with_data_from_above_alt(df: pd.DataFrame, item: str, column: str) -> pd.DataFrame:
    """
    Replaces cells in the specified column containing the string "ALT" with the value
    from the previous row in the same column, but only if the value in the 'item' column
    matches the previous row's 'item' column value.

    This function looks for rows where the value in the 'column' contains "ALT" and the
    value in the 'item' column matches the previous row. If both conditions are met,
    the current cell is replaced with the value from the previous row in the same column.

    Args:
    - df (pd.DataFrame): The DataFrame containing the data to modify.
    - item (str): The column name to check for matching values between consecutive rows.
    - column (str): The column to be updated with the previous row's value when conditions are met.

    Returns:
    - pd.DataFrame: The updated DataFrame after replacing cells with the previous row's value.
    """
    # Print message indicating the operation is starting
    print(f' Replacing "ALT" labels in "{column}" column with values from the row above (conditional on matching "{item}" column).')
    # Get the total number of rows in the DataFrame
    num_rows = len(df)
    # Counter to track the number of cells updated
    counter = 0
    # Define the string that identifies an alternative label
    alt = "ALT"
    # Iterate through the rows starting from index 1 (second row)
    for n in range(1, num_rows):
        # Check if the 'item' value matches between the current and previous row
        is_item_match = df.iloc[n][item] == df.iloc[n - 1][item]
        # Check if the current cell in the specified column contains "ALT"
        is_alt = alt in df.iloc[n][column]
        # If both conditions are met, replace the current value with the previous row's value
        if is_item_match and is_alt:
            # Log the change from the previous value to the current one
            print(f'  Changed "{df.iloc[n, df.columns.get_loc(column)]}" to "{df.iloc[n - 1, df.columns.get_loc(column)]}"')
            # Replace the "ALT" label with the value from the previous row
            df.iloc[n, df.columns.get_loc(column)] = df.iloc[n - 1, df.columns.get_loc(column)]
            counter += 1
    # Print a summary of the number of cells updated
    print(f' {counter} cells updated.')

    return df
