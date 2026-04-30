# This file has functions to manipulate both rows and columns in a data frame
from typing import Type

import pandas as pd

from src import columns
from src import header
from src import rows
from src import strings

from src.enumeration import SourceFileType, OutputFileType, BomTempVer

# Standardized header names used across eBOM, cBOM and cost walk. They are based off the bom template v2.0 and v3.0
itemHdr = "Item"
componentHdr = "Component"
descriptionHdr = "Description"
typeHdr = "Type"
pkgHdr = "Device Package"
criticalHdr = "Critical Component"
classHdr = "Classification"
manufacturerHdr = "Manufacturer"
partNoHdr = "Manufacturer P/N"
qtyHdr = "Qty"
designatorHdr = "Designator"
unitPriceHdr = "U/P RMB W/O VAT"
featureHdr = "Feature"
boardHdr = "Board"

# strings to look for when searching for the bom header
header_search_string_list = [designatorHdr, manufacturerHdr, qtyHdr]

cost_walk_header_list_v2 = [itemHdr, designatorHdr, componentHdr, descriptionHdr,
                            manufacturerHdr, partNoHdr, qtyHdr, unitPriceHdr, typeHdr]

cost_walk_header_list_v3 = [itemHdr, designatorHdr, componentHdr, descriptionHdr,
                            manufacturerHdr, partNoHdr, qtyHdr, unitPriceHdr, pkgHdr]

cbom_header_list_v2 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       criticalHdr, manufacturerHdr, partNoHdr, unitPriceHdr, typeHdr]

ebom_header_list_v2 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       criticalHdr, manufacturerHdr, partNoHdr, typeHdr]

cbom_header_list_v3 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       classHdr, manufacturerHdr, partNoHdr, unitPriceHdr, pkgHdr]

ebom_header_list_v3 = [itemHdr, componentHdr, descriptionHdr, qtyHdr, designatorHdr,
                       classHdr, manufacturerHdr, partNoHdr, pkgHdr]

# Dictionary of component type reference strings (case-insensitive) and normalized stella component type names.
# Perfect match should be listed last
component_dict = {
    # list based on db template
    "Battery Terminals": [
        "Battery Terminals"],
    "Buzzer": [
        "Speaker",
        "Buzzer"],
    "Cable": [
        "Cable"],
    "Capacitor": [
        "Electrolytic Capacitor", "Disc Ceramic Capacitor", "Capartion", "Ceramic capacitor",
        "X1 Cap", "X1 Capacitor", "X1 Capacitance",
        "X2 Cap", "X2 Capacitor", "X2 Capacitance",
        "Y1 Cap", "Y1 Capacitor", "Y1 Capacitance",
        "Y2 Cap", "Y2 Capacitor", "Y2 Capacitance",
        "Capacitor"],
    "Connector": [
        "PCB Tab", "Quick fit terminal", "Plug piece terminal",
        "Connector"],
    "Crystal": [
        "Crystal"],
    "Diode": [
        "Switching diode", "Rectifier Bridge", "Bridge Rectifiers", "FRD", "ESD", "Rectifier",
        "TVS", "Zener", "Zener Diode", "Bridge Rectifier", "Rectifier Diode", "Schottky", "Schottky Diode",
        "IR Receiver",
        "Diode"],
    "Electromagnet": [
        "Electromagnet"],
    "Foam": [
        "Foam"],
    "FUSE": [
        "FUSE"],
    "Heatsink": [
        "Heat Sink",
        "Heatsink"],
    "IC": [
        "Operational amplifier",
        "IC"],
    "Inductor": [
        "Common mode choke", "Choke", "Ferrite", "Magnetic Bead",
        "Inductor"],
    "Jumper": [
        "Jumper"],
    "LCD": [
        "LCD"],
    "LED": [
        "LED Module",
        "LED"],
    "MCU": [
        "MCU"],
    "MOV/Varistor": [
        "MOV", "Varistor",
        "MOV/Varistor" ],
    "Optocoupler": [
        "Optocoupler"],
    "PCB": [
        "PCB"],
    "Relay": [
        "Relay"],
    "Resistor": [
        "Resistance", "Wire wound resistor", "Wire wound non flame resistor",
        "Resistor", "Metal film resistor"],
    "Sensor": [
        "Sensor"],
    "Spring": [
        "Touch spring",
        "Spring"],
    "Switch": [
        "Tactile Switch", "Tact Switch", "Slide Switch",
        "Switch"],
    "TCO": [
        "TCO"],
    "Thermistors": [
        "NTC",
        "Thermistors"],
    "Transformer": [
        "Transformer"],
    "Transistor": [
        "BJT", "MOS", "Mosfet", "N-CH", "P-CH",
        # Don't add "PNP Transistor" and "NPN Transistor" as both are a perfect match for Jaccard similarity
        # and cause issues. Instead, if left out, both wil match correctly to Transistor
        "Transistor"],
    "Triac/SCR": [
        "Triac", "SCR",
        "Triac/SCR"],
    "Unknown/Misc": [
        "Unknown", "Misc",
        "Unknown/Misc"],
    "Voltage Regulator": [
        "Regulator", "LDO", "three-terminal adjustable regulator",
        "Three-terminal Voltage Regulator", "SMT voltage regulator tube",
        "Voltage Regulator"],
    "Wire": [
        "Wire"],
    # list based on test data
    "Chimney": [
        "Chimney"],
    "Heat Shrink": [
        "Heat Shrink Tubing",
        "Heat Shrink"],
    "Lens": [
        "Lens"],
    "Screw": [
        "Screw"]
}

# List of strings to determine which rows to delete based on string match with description header
unwanted_db_ebom_description_list = [
    "Glue", "Solder", "Compound", "Conformal", "Coating", "Screw"]

# List of strings to determine which rows to delete based on string match with description header
unwanted_db_cbom_description_list = [
    "Glue", "Solder", "Compound", "Conformal", "Coating", "Screw"]

# List of strings to determine which rows to delete based on string match with component type
unwanted_db_ebom_component_list = [
    "PCB", "Wire", "Lens", "Chimney", "Heat Shrink", "Screw", "Jumper"]

# List of strings to determine which rows to delete based on string match with component type
unwanted_db_cbom_component_list = [
    "Wire", "Lens", "Chimney", "Heat Shrink", "Screw", "Jumper"]


def search_and_set_bom_header(df: pd.DataFrame) -> pd.DataFrame:
    """
    Search and set header for bom.

    Args:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The modified DataFrame with rows dropped.
    """

    # user interface message
    print()
    print("Searching for bom header row... ")

    # search for header row
    header_row = header.search_row_matching_header(df, header_search_string_list)

    # drop rows above the row containing the match
    df.drop(index=df.index[:header_row], inplace=True)

    # reset the row index
    df = df.reset_index(drop=True)

    # set top row as header
    df = header.set_top_row_as_header(df)

    # user interface message
    print(f'Bom header data found in row {header_row + 1}.')

    return df


def get_bom_template_version(df: pd.DataFrame, enum_bom_temp_version: Type[BomTempVer]) -> BomTempVer:
    # user interface message
    print()
    print("Determining BOM template version... ")

    # determine the BOM template version
    if criticalHdr in df.columns:
        bom_temp_ver = enum_bom_temp_version.v2
    elif classHdr in df.columns:
        bom_temp_ver = enum_bom_temp_version.v3
    else:
        raise ValueError("This application can only process data for BOM template version 2.0 and 3.0")

    # user interface message
    print(f"BOM template version = {bom_temp_ver}")

    return bom_temp_ver


def get_source_bom_header_labels(
        bom_temp_ver: BomTempVer,
        enum_bom_temp_version: Type[BomTempVer],
        source_file_type: SourceFileType,
        enum_source_file_type: Type[SourceFileType]) -> list[str]:
    # user interface message
    print()
    print("Determining source file BOM header format... ")

    source_bom_header_labels = []

    # Determine the BOM template version
    if bom_temp_ver == enum_bom_temp_version.v2:
        if source_file_type == enum_source_file_type.EB:
            source_bom_header_labels = ebom_header_list_v2
        elif source_file_type == enum_source_file_type.CB:
            source_bom_header_labels = cbom_header_list_v2
    elif bom_temp_ver == enum_bom_temp_version.v3:
        if source_file_type == enum_source_file_type.EB:
            source_bom_header_labels = ebom_header_list_v3
        elif source_file_type == enum_source_file_type.CB:
            source_bom_header_labels = cbom_header_list_v3

    if not source_bom_header_labels:
        raise ValueError(f"Application was not able to determine the source bom header. "
                         f"BOM template = {bom_temp_ver}. Source BOM type = {source_file_type}")

    # User interface message
    print(f"Source file BOM header format = {source_bom_header_labels}")

    return source_bom_header_labels


def get_output_bom_header_labels(
        bom_temp_ver: BomTempVer,
        enum_bom_temp_version: Type[BomTempVer],
        output_file_type: OutputFileType,
        enum_output_file_type: Type[OutputFileType]) -> list[str]:
    # user interface message
    print()
    print("Determining output file BOM header labels... ")

    output_bom_header_labels = []

    if bom_temp_ver == enum_bom_temp_version.v2:
        if output_file_type == enum_output_file_type.CW:
            output_bom_header_labels = cost_walk_header_list_v2
        elif output_file_type == enum_output_file_type.dB_CB:
            output_bom_header_labels = cbom_header_list_v2
        elif output_file_type == enum_output_file_type.db_EB:
            output_bom_header_labels = ebom_header_list_v2

    elif bom_temp_ver == enum_bom_temp_version.v3:
        if output_file_type == enum_output_file_type.CW:
            output_bom_header_labels = cost_walk_header_list_v3
        elif output_file_type == enum_output_file_type.dB_CB:
            output_bom_header_labels = cbom_header_list_v3
        elif output_file_type == enum_output_file_type.db_EB:
            output_bom_header_labels = ebom_header_list_v3

    if not output_bom_header_labels:
        raise ValueError(f"Application was not able to determine the source bom header. "
                         f"BOM template = '{bom_temp_ver}'. Output data format = '{output_file_type}'")

    # user interface message
    print(f"Output BOM header = {output_bom_header_labels}")

    return output_bom_header_labels


def delete_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete rows containing either NaN values or empty strings from a pandas DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame from which to delete empty rows.

    Returns:
    pandas.DataFrame: DataFrame with rows containing NaN values or empty strings removed.
    """

    # user interface message
    print()
    print('Deleting empty rows... ')

    # Drop rows with all NaN values
    mdf = df.dropna(axis=0, how='all')

    # Drop rows with all empty strings
    mdf = mdf.replace('', pd.NA).dropna(axis=0, how='all')

    rows_before = df.shape[0]
    rows_after = mdf.shape[0]
    print(f"Number of rows reduced from {rows_before} to {rows_after}")

    return mdf


def delete_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Delete columns containing either NaN values or empty strings from a pandas DataFrame.

    Parameters:
    dataframe (pandas.DataFrame): The DataFrame from which to delete empty columns.

    Returns:
    pandas.DataFrame: DataFrame with columns containing NaN values or empty strings removed.
    """
    # message
    print()
    print('Deleting empty columns... ')

    # Drop columns with all NaN values
    mdf = df.dropna(axis=1, how='all')

    # Drop columns with all empty strings
    mdf = mdf.replace('', pd.NA).dropna(axis=1, how='all')

    # user interface message
    columns_before = df.shape[1]
    columns_after = mdf.shape[1]
    print(f"Number of columns reduced from {columns_before} to {columns_after}")

    return df


def set_bom_column_datatype(df: pd.DataFrame) -> pd.DataFrame:
    # By default, all columns of data are treated as string
    df = df.astype(str)

    # panda dataframe places a 'nan' for empty cells. When converted to string we end up with 'nan' string
    # this should be removed and replaced with an empty cell
    df = df.replace("nan", "")

    # items column data contains numbers. It may be decimal data so convert to float.
    # df[itemHdr] = df[itemHdr].replace("", 0)  # empty cells are treated as zeros
    # df[itemHdr] = df[itemHdr].replace("ALT", 0)  # ALT cells are treated as zeros
    # df[itemHdr] = df[itemHdr].astype(float)

    # qty column data contains numbers. It will contain some decimal data (like glue qty) so convert to float.
    df[qtyHdr] = df[qtyHdr].replace("", 0)  # empty cells are treated as zeros
    df[qtyHdr] = df[qtyHdr].astype(float)

    # EBOMs do not contain unit price data
    if unitPriceHdr in df.columns:
        # unit price column data contains numbers. It will be decimal data so convert to float.
        df[unitPriceHdr] = df[unitPriceHdr].replace("", 0)  # empty cells are treated as zeros
        df[unitPriceHdr] = df[unitPriceHdr].astype(float)

    return df


def split_manufacturers_to_separate_rows(
        original_df: pd.DataFrame,
        bom_template_version: BomTempVer,
        enum_bom_temp_version: Type[BomTempVer],
        source_file_type: SourceFileType,
        enum_source_file_type: Type[SourceFileType]) -> pd.DataFrame:
    """
    Split manufacturer names and corresponding part numbers to separate rows in the DataFrame.

    Args:
    original_df (DataFrame): The original DataFrame containing manufacturer names and part numbers.

    Returns:
    DataFrame: Updated DataFrame with each manufacturer name and part number in separate rows.

    Raises:
    ValueError: If there are multiple or no columns matching the reference strings for manufacturer name or part number.
                If the number of manufacturer names does not match the number of part numbers.
                If an error is detected in the data during processing.
    """
    # message
    print()
    print('Separating manufacturer names to separate rows...')

    # local variables
    exception_list = []

    # List of component type that do not need to be split
    if bom_template_version == enum_bom_temp_version.v2:
        exception_list = ["Res", "Cap", "Ind"]
    elif bom_template_version == enum_bom_temp_version.v3:
        exception_list = []  # for version 3.0 we separate all alternatives

    # Get the index of manufacturer name column
    name_index = columns.get_single_header_index(original_df, 'Manufacturer', True)

    # Get the index of component header
    component_index = columns.get_single_header_index(original_df, 'Component', True)

    # Get the index of the part number column
    part_number_index = columns.get_single_header_index(original_df, 'P/N', False)

    # Get the index of the quantity column
    qty_index = columns.get_single_header_index(original_df, 'Qty', False)

    # Get the index of the price column
    if source_file_type == enum_source_file_type.CB:
        price_index = columns.get_single_header_index(original_df, 'U/P RMB W/O VAT', False)
    else:
        price_index = 0

    # Get the index of the description column
    description_index = columns.get_single_header_index(original_df, 'Description', False)

    # Create an empty data frame with same header
    updated_df = pd.DataFrame(columns=original_df.columns)

    # read each row on at a time
    for index, row in original_df.iterrows():
        # get values we need
        component_string = row.iloc[component_index]
        name_string = row.iloc[name_index]
        description_string = row.iloc[description_index]
        # part number may be all numbers so force data to string
        part_number_string = str(row.iloc[part_number_index])
        name_list = name_string.split('\n')
        part_number_list = part_number_string.split('\n')
        description_list = description_string.split('\n')
        # remove any "" items from the list.
        name_list = [item for item in name_list if item != ""]
        part_number_list = [item for item in part_number_list if item != ""]
        description_list = [item for item in description_list if item != ""]

        # number of manufacturer names must be the same as manufacturer part numbers
        if len(name_list) != len(part_number_list):
            if len(part_number_list) == 1:
                for i in range(len(name_list)):
                    part_number_list.append(part_number_list[0])
            else:
                print("*** ERROR *** ")
                print("Number of part numbers must be one or the same as number of manufacturers")
                print(f"{len(name_list)} Manufacturer names {name_list}")
                print(f"{len(part_number_list)} Manufacturer part numbers {part_number_list}")
                print("Please fix the source data file and retry")
                exit()

        # when component name is exception list we don't split the row
        split_flag = True
        for reference_string in exception_list:
            if reference_string.lower() in component_string.lower():
                split_flag = False

        # When we want to split, split the manufacturer names and part numbers into separate rows
        if not split_flag:
            updated_df.loc[len(updated_df)] = row
        else:
            for i in range(len(name_list)):
                new_row = row.copy()
                new_row.iloc[name_index] = name_list[i]
                new_row.iloc[part_number_index] = part_number_list[i]
                new_row.iloc[description_index] = description_list[i]
                # Except for first occurrence, all other rows have zero quantity
                if i != 0:
                    new_row.iloc[qty_index] = 0
                # If version 3.0, set price to 0 for all rows except the first
                if bom_template_version == enum_bom_temp_version.v3 and i != 0:
                    new_row.iloc[price_index] = 0
                if bom_template_version == enum_bom_temp_version.v3:
                    new_row.iloc[description_index] = description_list[i]
                # add row to updated data frame
                updated_df.loc[len(updated_df)] = new_row

    # user interface message
    original_row_count = original_df.shape[0]
    updated_row_count = updated_df.shape[0]

    print(f"Number of row in the BOM increased from {original_row_count} to {updated_row_count}")

    return updated_df


def check_qty_matched_ref_des_count(df):
    """
    Check if the quantity matches the number of reference designators for each item in the DataFrame.

    Parameters:
    - df: pandas DataFrame
        The DataFrame containing the data to be checked.

    Raises:
    - ValueError: If the quantity does not match the number of reference designators for any item.
        This can occur if:
        - More than one column matches the reference string 'Qty'.
        - No column matches the reference string 'Qty'.
        - More than one column matches the designator column search string 'Designator'.
        - No column matches the designator column search string 'Designator'.
        - Quantity does not match the number of reference designators for any item.

    Returns:
    - None: If all checks pass successfully, prints a message indicating that the quantity count matches the number
      of reference designators in all rows of the DataFrame.
    """

    # message
    print()
    print('Checking quantity matches number of reference designators... ')

    # Get quantity column index
    quantity_columns = []
    for index, name in enumerate(list(df.columns)):
        # Looking for an exact match
        if "Qty" == name:
            quantity_columns.append(index)
    # We only expect one match
    if len(quantity_columns) == 1:
        qty_index = quantity_columns[0]  # Select the first matching column
        # print(f"Quantity data found in column ", qty_index)
    elif len(quantity_columns) > 1:
        # Raise an error if more than one column matches
        raise ValueError("More than one column matched the reference string.")
    else:
        # Raise an error if no column match
        raise ValueError("No partial match found in the header.")

    # Get reference designator column index
    designator_columns = []
    for index, name in enumerate(list(df.columns)):
        # looking for partial match
        if "Designator" in name:
            designator_columns.append(index)
    # We only expect one match
    if len(designator_columns) == 1:
        designator_index = designator_columns[0]  # Select the first matching column
        # print(f"Designator data found in column ", designator_index)
    elif len(designator_columns) > 1:
        # Raise an error if more than one column matches
        raise ValueError("More than one column matched the designator column search.")
    else:
        # Raise an error if no partial match is found
        raise ValueError("Designator column not found.")

    # Get one row at a time
    for _, row in df.iterrows():
        # get the quantity
        count_of_quantity = row.iloc[qty_index]
        # Count the number of reference designators
        designator_string = row.iloc[designator_index]
        count_of_designator = len(designator_string.split(','))
        # raise an error when counts is integer and does not match
        if count_of_designator != count_of_quantity and int(count_of_quantity) == float(count_of_quantity):
            print(f"Quantity does not match number of designators for item {row.iloc[0]}")
            print('Fix input data file and try again')
            exit()

    # Message
    print(f'Quantity count matches number of reference designators in all {df.shape[0]} rows')


def normalize_component_type_label(df):
    import strings

    # message
    print()
    print('Refactoring component column data... ')

    # Get component type column
    matching_columns = []
    for index, name in enumerate(list(df.columns)):
        if "Component" in name:
            matching_columns.append(index)
            break  # pick the first one

    # We only expect one match
    if len(matching_columns) == 1:
        type_index = matching_columns[0]  # Select the first matching column
        # print(f"Manufacturer name found in column =", type_index)
    elif len(matching_columns) > 1:
        raise ValueError(
            "More than one column matched the reference string.")  # Raise an error if more than one column matches
    else:
        raise ValueError("No partial match found in the header.")  # Raise an error if no partial match is found

    # Create an empty DataFrame to store the updated rows
    updated_df = pd.DataFrame(columns=df.columns)

    # Get one row at a time
    count = 0
    key_count = 0
    for _, row in df.iterrows():
        # Get component type
        component_type_name = row.iloc[type_index]
        # ignore SMD, DIP if found in component type name as they add not value
        component_string = component_type_name.replace("SMD", "").replace("DIP", "").replace("ALT", "").replace("SMT", "")
        # Get all values from the component dict
        value_list = [value for sublist in component_dict.values() for value in sublist]
        # Get the best matched value
        value_match1 = strings.find_best_match_jaccard(component_string, value_list)
        value_match2 = strings.find_best_match_levenshtein(component_string, value_list)
        key_match = "*" + component_type_name
        if value_match1 == value_match2:
            # for debug keep track of number of items changed
            count += 1
            # Get the key of the matched value
            for key, values in component_dict.items():
                if value_match1 in values:
                    key_match = key
                    key_count += 1
                    # raise exception when multiple keys are found
                    try:
                        key_count > 1
                    except Exception as e:
                        raise ValueError(f"Multiple component match found for {component_type_name}.", e)
        # replace the component type name in the row
        row.iloc[type_index] = key_match

        # add row to updated data frame
        updated_df.loc[len(updated_df)] = row
        # debug message
        print(f'{component_type_name:30} -> {key_match:30} [{value_match1}/{value_match2}]')

    # message for how many rows changed
    print(f"{count} rows updated")

    return updated_df


def drop_rows_with_unwanted_ebom_items(df):
    # message
    print()
    print('Removing unwanted electrical bill of material rows... ')

    # List of strings to determine which rows to delete based on string match with description header
    unwanted_description_strings_list = ["Glue", "Solder", "Compound", "Conformal", "Coating", "Screw", "Wire", "AWG"]

    # Get the index of description column
    description_index = columns.get_single_header_index(df, 'Description', True)

    # Remove unwanted description rows
    updated_df = rows.delete_row_when_element_contains_string(df, description_index, unwanted_description_strings_list)

    # List of strings to determine which rows to delete based on string match with component header
    unwanted_component_strings_list = ["PCB", "Wire"]

    # Get the index of component column
    component_index = columns.get_single_header_index(updated_df, 'Component', True)

    # Remove unwanted description rows
    updated_df = rows.delete_row_when_element_contains_string(updated_df,
                                                              component_index, unwanted_component_strings_list)

    return updated_df


def remove_part_number_from_description(data_frame):
    # message
    print()
    print('Removing part numbers from description... ')

    mdf = strings.strip_match_from_string(data_frame, partNoHdr, descriptionHdr)

    # remove duplicate, starting and trailing comma that may be left after part number is removed from description
    mdf[descriptionHdr] = mdf[descriptionHdr].str.replace(r',{2,}', ',', regex=True) # Do this before strip
    mdf[descriptionHdr] = mdf[descriptionHdr].str.lstrip(',')
    mdf[descriptionHdr] = mdf[descriptionHdr].str.rstrip(',')

    print('Done.')


    return data_frame


def primary_above_alternative(df: pd.DataFrame,
                              bom_template_version: BomTempVer,
                              enum_bom_temp_version: Type[BomTempVer]) -> pd.DataFrame:
    """
    Reorder each component group so the primary component (qty != 0) is first, followed by alternatives (qty == 0).
    For template v2: return the input unchanged.
    For template v3: while scanning rows in order, whenever a primary appears in a group that already has
    alternative rows, insert the primary at the top of the group's buffer, then swap the values of
    [pkgHdr, itemHdr, componentHdr] between the first and second rows of that group to preserve primary
    metadata if it was carried by the first alternative row.

    Grouping keys: (itemHdr, designatorHdr).

    Args:
        df: Input DataFrame.
        bom_template_version: Active BOM template version (Enum value).
        enum_bom_temp_version: Enum class for template versions (e.g., BomTempVer). Redundant if BomTempVer is importable.

    Returns:
        A new DataFrame with primary components placed above alternatives for template v3; unchanged for v2.
    """
    print()
    print('Moving primary item above alternative items...')

    # Not required for template version 2.0
    if bom_template_version == enum_bom_temp_version.v2:
        return df.copy()

    # Only needed for template version 3.0
    if bom_template_version == enum_bom_temp_version.v3:

        # Initialize an empty DataFrame to collect rows (df_temp)
        df_group = pd.DataFrame(columns=df.columns)
        df_mod = pd.DataFrame(columns=df.columns)

        # Read each row one at a time
        for idx, row in df.iterrows():

            # Convert current row label -> position
            n_row = df.index.get_loc(idx)

            # for first physical row → start a new group
            if n_row == 0:
                df_group = pd.DataFrame([row], columns=df.columns)  # copy row to group
                continue  # no need to do anything else

            # Previous row label (by sequence, not label math)
            prev_idx = df.index[n_row - 1] # get previous row index label
            
            # Detect group change by label
            same_group = (
                    df.loc[idx, itemHdr] == df.loc[prev_idx, itemHdr] and
                    df.loc[idx, designatorHdr] == df.loc[prev_idx, designatorHdr]
            )

            # When component changes
            if not same_group:
                # add group to mdf
                df_mod = pd.concat([df_mod, df_group], axis=0, ignore_index=True)
                # Start new group with current row
                df_group = pd.DataFrame([row], columns=df.columns)
                continue  # no need to do anything else

            # Within the same group
            # When we come across an alternative part
            if row[qtyHdr] == 0:
                # add current row to the bottom of the group
                df_group = pd.concat([df_group, pd.DataFrame(row).T], axis=0, ignore_index=True)
            # When we come across the primary
            else:
                # add current row to the top of the group
                df_group = pd.concat([pd.DataFrame(row).T, df_group], axis=0, ignore_index=True)

                # Primary information may be in the alternative row, so
                # after adding to the top, if we have at least two rows
                if len(df_group) > 1:
                    # Select columns to swap
                    cols_to_swap = [pkgHdr, itemHdr, componentHdr]
                    # Swap values between the first and second rows for the selected columns
                    # Take copies to avoid chained assignment pitfalls
                    r0 = df_group.loc[0, cols_to_swap].copy()
                    r1 = df_group.loc[1, cols_to_swap].copy()
                    df_group.loc[0, cols_to_swap] = r1.values
                    df_group.loc[1, cols_to_swap] = r0.values

        # After the last group, merge the remaining df_temp into mdf
        if not df_group.empty:
            df_mod = pd.concat([df_mod, df_group], axis=0, ignore_index=True)

        # User interface message
        print("Done")

        return df_mod

    # Unknown version
    raise ValueError("BOM template version not supported by primary_above_alternative")


def fill_merged_designators(df: pd.DataFrame,
                              bom_template_version: BomTempVer,
                              enum_bom_temp_version: Type[BomTempVer]) -> pd.DataFrame:
    print()
    print('Fill in designators when designator cells are merged in excel BOM... ')

    # Not required for template version 2.0
    if bom_template_version == enum_bom_temp_version.v2:
        pass

    # Only needed for template version 3.0
    elif bom_template_version == enum_bom_temp_version.v3:
        # Iterate over the rows of the DataFrame
        for n in range(1, len(df)):  # Start from index 1 to avoid IndexError on n-1
            # Check if the designator is empty in the current row
            if not df.loc[n, designatorHdr]:
                # Check if the description matches with the previous row
                if df.loc[n, descriptionHdr] == df.loc[n - 1, descriptionHdr]:
                    # Copy the designator from the previous row
                    df.loc[n, designatorHdr] = df.loc[n - 1, designatorHdr]

    # User interface message
    print("Done")
    return df


def merge_alternative(df_in):
    """
    Merge alternative items into the group's primary row by joining selected fields with the newline delimiter "\n".

    Purpose:
      - Allow CBOM v3.0 (primary + alternatives on separate rows) to appear like CBOM v2.0 (single row),
        by merging alternative-row values into the primary row. A later step can split them back.

    Grouping keys: (itemHdr, designatorHdr).
    Merged columns: descriptionHdr, manufacturerHdr, partNoHdr.
    """

    # message
    print()
    print('Merging alternatives items with primary item...')

    # Early exit
    if df_in.empty:
        print("Number of rows in the BOM changed from 0 to 0")
        return df_in.copy()


    # Initialize variables to store previous primary item values
    prev_desc = ''
    prev_mfg = ''
    prev_pn = ''

    # Create an empty data frame with same header
    df_out = pd.DataFrame(columns=df_in.columns)
    df_group = pd.DataFrame(columns=df_in.columns)

    # read each row on at a time
    for idx, row in df_in.iterrows():

        # Convert current row label -> position
        n_row = (df_in.index.get_loc(idx))

        # for first physical row → start a new group
        if n_row == 0:
            df_group = row.copy()
            prev_desc = row[descriptionHdr]
            prev_mfg = row[manufacturerHdr]
            prev_pn = row[partNoHdr]
            continue  # no need to do anything else

        # Previous row label (by sequence, not label math)
        prev_idx = df_in.index[n_row - 1]  # get previous row index label

        # Detect group change by label
        group_change = not (
                df_in.loc[idx, itemHdr] == df_in.loc[prev_idx, itemHdr] and
                df_in.loc[idx, designatorHdr] == df_in.loc[prev_idx, designatorHdr]
        )

        if group_change:
            # add group to output
            df_out = pd.concat([df_out, pd.DataFrame(df_group).T], axis=0, ignore_index=True)
            df_group = row.copy()
            prev_desc = row[descriptionHdr]
            prev_mfg = row[manufacturerHdr]
            prev_pn = row[partNoHdr]
        else:
            if row[descriptionHdr]:
                df_group[descriptionHdr] += "\n" + row[descriptionHdr]
            else:
                df_group[descriptionHdr] += "\n" + prev_desc
            if row[manufacturerHdr]:
                df_group[manufacturerHdr] += "\n" + row[manufacturerHdr]
            else:
                df_group[manufacturerHdr] += "\n" + prev_mfg

            if row[partNoHdr]:
                df_group[partNoHdr] += "\n" + row[partNoHdr]
            else:
                df_group[partNoHdr] += "\n" + prev_pn

    # last row merger needs to be done outside the for loop
    df_out = pd.concat([df_out, pd.DataFrame(df_group).T], axis=0, ignore_index=True)

    # user interface message
    print(f"Number of row in the BOM changed from {df_in.shape[0]} to {df_out.shape[0]}")

    return df_out


def merge_type_data_with_description(df: pd.DataFrame, bom_template_version: BomTempVer):
    # message
    print()
    print('Merging type column data with description column data... ')

    # local variables
    part_number_index = -1

    # Get the index of the type column
    if bom_template_version == BomTempVer.v2:
        part_number_index = columns.get_single_header_index(df, typeHdr, True)
    elif bom_template_version == BomTempVer.v3:
        part_number_index = columns.get_single_header_index(df, pkgHdr, True)

    # Get the index of description column
    description_index = columns.get_single_header_index(df, descriptionHdr, True)

    df = rows.merge_row_data_when_no_found(df, part_number_index, description_index)

    return df


def select_build(df: pd.DataFrame) -> pd.DataFrame:
    # get all the build names for which data is available in the dataframe
    build_dict = rows.get_build_name_and_column(df)

    # delete column when it has unwanted build data
    df = columns.delete_columns_with_unwanted_build_data(df, build_dict)

    return df


def split_multiple_quantity(data_frame: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Splitting multiple quantity to separate rows... ')

    # keep tack of total rows before clean up
    original_row_count = data_frame.shape[0]

    # duplicate rows till qty is less than one while splitting ref des
    data_frame = rows.duplicate_row_for_multiple_quantity(data_frame)

    # user interface message
    updated_row_count = data_frame.shape[0]
    print(f"Number of rows increased from {original_row_count} to {updated_row_count}")

    return data_frame


def get_bom_columns(df: pd.DataFrame, source_bom_header: list[str]) -> pd.DataFrame:
    # user interface message
    print()
    print('Extracting BOM columns... ')

    mdf = header.standardize_header_names(df, source_bom_header)

    # Reorder header based on list and drop remaining columns
    mdf = mdf[source_bom_header]

    # user interface message
    header_strings = ", ".join(mdf.columns)
    print(f'Columns are [{header_strings}]')

    return mdf


def cleanup_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up description column data... ')

    # remove duplicate spaces
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[^\S\r\n]+', ' ', regex=True)

    # special 'characters' cases...
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[，]', ',', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[（]', '(', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[）]', ')', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[；]', ';', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[：]', ':', regex=True)

    # sometimes data is semi-colon separated
    df[descriptionHdr] = df[descriptionHdr].str.replace(r'[;]', ',', regex=True)

    # multiple comma, space before and after a comma are replaced by just a comma
    df[descriptionHdr] = df[descriptionHdr].str.replace(r',{2,}', ',', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r' ,', ',', regex=True)
    df[descriptionHdr] = df[descriptionHdr].str.replace(r', ', ',', regex=True)

    # remove starting and trailing comma
    df[descriptionHdr] = df[descriptionHdr].str.lstrip(',')
    df[descriptionHdr] = df[descriptionHdr].str.rstrip(',')

    # remove starting and trailing space
    df[descriptionHdr] = df[descriptionHdr].str.lstrip(' ')
    df[descriptionHdr] = df[descriptionHdr].str.rstrip(' ')

    print('Done.')

    return df


def cleanup_designators(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up designator column data... ')

    # remove spaces
    df[designatorHdr] = df[designatorHdr].str.replace(r'\s+', '', regex=True)

    # replace special characters used to separate designators by comma
    df[designatorHdr] = df[designatorHdr].str.replace(r'[:;、\'，]', ',', regex=True)

    # replace duplicate commas by one comma
    df[designatorHdr] = df[designatorHdr].str.replace(r',{2,}', ',', regex=True)

    # remove starting and trailing comma
    df[designatorHdr] = df[designatorHdr].str.lstrip(',')
    df[designatorHdr] = df[designatorHdr].str.rstrip(',')

    print('Done.')

    return df


def cleanup_manufacturer(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up manufacturer column data... ')

    # special case when start is with MFG or Manufacturer case-insensitive
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'(?i)^MANUFACTURER', ' ', regex=True)
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'(?i)^MANU', ' ', regex=True)
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'(?i)^MFG', ' ', regex=True)

    # replace ".," with space. Special case for "Co.,Ltd" to "Co Ltd"
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'.,', ' ', regex=True)
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'.，', ' ', regex=True)

    # replace colon and dot with space
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'[:.]', ' ', regex=True)

    # remove starting and trailing space
    df[manufacturerHdr] = df[manufacturerHdr].str.lstrip(' ')
    df[manufacturerHdr] = df[manufacturerHdr].str.rstrip(' ')

    # elements are comma separated
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r'\n', ',', regex=True)

    # remove duplicate spaces
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r' {2,}', ' ', regex=True)
    # replace duplicate commas by one comma
    df[manufacturerHdr] = df[manufacturerHdr].str.replace(r',{2,}', ',', regex=True)

    print('Done.')

    return df


def cleanup_part_number(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Cleaning up part number column data... ')

    # remove duplicate spaces
    df[partNoHdr] = df[partNoHdr].str.replace(r' {2,}', ' ', regex=True)

    # elements are comma separated
    df[partNoHdr] = df[partNoHdr].str.replace(r'\n', ',', regex=True)

    print('Done.')

    return df


def drop_unwanted_db_ebom_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted eBOM description items... ')

    # Get the index of description column
    description_index = columns.get_single_header_index(df, descriptionHdr, True)

    # delete row when the description is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, description_index, unwanted_db_ebom_description_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_unwanted_db_cbom_description(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted cbom description...')

    # Get the index of description column
    description_index = columns.get_single_header_index(df, descriptionHdr, True)

    # delete row when the description is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, description_index, unwanted_db_cbom_description_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_unwanted_db_ebom_component(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted ebom component... ')

    # Get the index of component column
    component_index = columns.get_single_header_index(df, componentHdr, True)

    # delete row when the component is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, component_index, unwanted_db_ebom_component_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_unwanted_db_cbom_component(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing unwanted cbom components... ')

    # Get the index of component column
    component_index = columns.get_single_header_index(df, componentHdr, True)

    # delete row when the component is prohibited for dB upload
    mdf = rows.delete_row_when_element_contains_string(df, component_index, unwanted_db_cbom_component_list)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_item_with_zero_quantity(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing items with zero quantity... ')

    # delete row when quantity is zero
    mdf = rows.delete_row_when_element_zero(df, qtyHdr)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_item_with_quantity_less_than_one(df: pd.DataFrame) -> pd.DataFrame:
    threshold = 1

    # user interface message
    print()
    print(f'Removing items with quantity less than {threshold}... ')

    # delete row when quantity is less than one
    mdf = rows.delete_row_when_element_less_than_threshold(df, qtyHdr, threshold)

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf


def drop_items_with_empty_designator(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Removing items with empty designator.... ')

    # delete row when designator is empty
    mdf = df[df[designatorHdr] != ""]

    # user interface message
    print(f"Number of rows reduced from {df.shape[0]} to {mdf.shape[0]}")

    return mdf

def fill_empty_item_cells(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Filling empty item cells.. ')

    df = columns.fill_empty_item_cells(df, itemHdr, componentHdr, designatorHdr)

    print('Done.')

    return df

def fill_empty_cell_using_data_from_above_alternative(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Filling empty cell with data from above alternative component.. ')

    df = columns.fill_empty_cell_using_data_from_above_alternative(df, itemHdr, componentHdr)
    df = columns.fill_empty_cell_using_data_from_above_alternative(df, itemHdr, designatorHdr)

    print('Done.')

    return df

def replace_alternative_label_with_data_from_above_alternative(df: pd.DataFrame) -> pd.DataFrame:
    # user interface message
    print()
    print('Replacing alternative label with data from above alternative component.. ')

    df = columns.replace_alt_label_with_data_from_above_alt(df, itemHdr, componentHdr)

    print('Done.')

    return df

def unpack_ref_des_series(df: pd.DataFrame) -> pd.DataFrame:
    """
    High-level interface to expand reference designator ranges in a DataFrame.

    This function serves as a user-facing wrapper around the lower-level
    `rows.unpack_ref_des_series`. It prints progress messages to the console
    for clarity and expands reference designator ranges (e.g., "R2-R5")
    into individual designators (e.g., "R2,R3,R4,R5") within the designated
    column of the DataFrame.

    The input DataFrame is updated in-place, and the expanded column values
    are returned for downstream processing.

    Example:
    - Input cell: "R1, R3-R6, R12"
    - Output cell: "R1,R3,R4,R5,R6,R12"

    Args:
    - df (pd.DataFrame): The DataFrame containing the reference designator data.

    Returns:
    - pd.DataFrame: The DataFrame with ranges in the reference designator column
      expanded into comma-separated individual values.
    """
    # user interface message
    print()
    print(' Unpacking reference designator series (example: R2-R5 -> R2,R3,R4,R5).. ')

    df = rows.unpack_ref_des_series(df, designatorHdr, verbose=True)

    print(' Done.')

    return df

