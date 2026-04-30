from src import files
from src import strings
from src import frames
from src.enumeration import SourceFileType, OutputFileType, BomTempVer


# noinspection PyProtectedMember
from src.controllers import _base as base # migrating to controller to deprecating paths.py

from src.menus import interfaces as menu
from src.importers import interfaces as importer

# module constants
ctrl = base.BaseController()

def sequence_cbom_for_cost_walk() -> None:

    source_file_type = SourceFileType.CB
    output_file_type = OutputFileType.CW

    # *** read Excel data file ***
    # get path to input data folder
    folder_path = ctrl.get_folder(
        settings_key=ctrl.temp_setting_keys.SOURCE_FILES_FOLDER,
        dialog_title="Select source file data folder",
        dialog_prompt=None,
    )

    # get Excel file name to process
    file_name = menu.file_selector(
        folder_path_in=folder_path,
        extensions=importer.EXCEL_FILE_TYPES,
        menu_title="Select source file: ",
        menu_prompt=None,
    )

    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract cbom sheet to process ***
    # extract user selected Excel file sheet
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)

    # *** Extract cbom table ***
    # drop rows above BOM header and set top row as header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    bom_temp_ver = frames.get_bom_template_version(df, BomTempVer)
    # get source BOM header labels as they are different depending upon BOM template version and source BOM type
    source_bom_header = frames.get_source_bom_header_labels(bom_temp_ver, BomTempVer, source_file_type, SourceFileType)
    # extract columns from source data
    df = frames.get_bom_columns(df, source_bom_header)

    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)
    # primary component should be first
    df = frames.primary_above_alternative(df, bom_temp_ver, BomTempVer)
    # merge alternative components to one row
    df = frames.merge_alternative(df)

    # *** Clean up data ***
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # unpack designator series
    df = frames.unpack_ref_des_series(df)
    # check reference designator format
    df = strings.check_ref_des_name(df)
    # check for duplicate reference designators
    strings.check_duplicate_ref_des(df)
    # check qty matches reference designator count
    frames.check_qty_matched_ref_des_count(df)

    # split multiple quantity to separate rows
    df = frames.split_multiple_quantity(df)

    # *** write cBOM data to file ***
    # get output BOM header labels as they are different depending upon BOM template version and output file format
    output_bom_header = frames.get_output_bom_header_labels(bom_temp_ver, BomTempVer, output_file_type, OutputFileType)
    # keep only the columns needed based on cBOM cost walk
    df = frames.get_bom_columns(df, output_bom_header)
    # get path to output data folder
    folder_path = ctrl.get_folder(
        settings_key=ctrl.temp_setting_keys.DESTINATION_FILES_FOLDER,
        dialog_title="Select destination file data folder",
        dialog_prompt=None,
    )
    # Set Excel file name
    file_name = OutputFileType.CW.value + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)

    return None


def sequence_cbom_for_db_upload() -> None:

    source_file_type = SourceFileType.CB
    output_file_type = OutputFileType.dB_CB

    # *** read cBOM Excel data file ***
    # get path to input data folder
    folder_path = ctrl.get_folder(
        settings_key=ctrl.temp_setting_keys.SOURCE_FILES_FOLDER,
        dialog_title="Select source file data folder",
        dialog_prompt=None,
    )
    # get Excel file name to process
    file_name = menu.file_selector(
        folder_path_in=folder_path,
        extensions=importer.EXCEL_FILE_TYPES,
        menu_title="Select source file: ",
        menu_prompt=None,
    )
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract sheet to process ***
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)

    # *** Extract cbom data ***
    # drop rows above BOM header and set top row as header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    bom_temp_ver = frames.get_bom_template_version(df, BomTempVer)
    # get source BOM header labels as they are different depending upon BOM template version and source BOM type
    source_bom_header = frames.get_source_bom_header_labels(bom_temp_ver, BomTempVer, source_file_type, SourceFileType)
    # extract columns from source data
    df = frames.get_bom_columns(df, source_bom_header)
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)

    # fill empty item cells.
    df = frames.fill_empty_item_cells(df)
    # fill empty cells with data using alternative of the same components
    df = frames.fill_empty_cell_using_data_from_above_alternative(df)
    # replace alternative with data
    df = frames.replace_alternative_label_with_data_from_above_alternative(df)

    # primary component should be first
    df = frames.primary_above_alternative(df, bom_temp_ver, BomTempVer)
    # merge alternative components to one row
    df = frames.merge_alternative(df)

    # *** Clean up cbom data ***
    # remove empty designator data
    df = frames.drop_items_with_empty_designator(df)
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove less than one quantity
    df = frames.drop_item_with_quantity_less_than_one(df)

    # clean up description column data
    df = frames.cleanup_description(df)
    # remove rows that have unwanted description items
    df = frames.drop_unwanted_db_cbom_description(df)

    # normalize component type labels
    df = frames.normalize_component_type_label(df)
    # remove rows that have unwanted component type items
    df = frames.drop_unwanted_db_cbom_component(df)

    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # unpack designator series
    df = frames.unpack_ref_des_series(df)
    # check reference designator format
    df = strings.check_ref_des_name(df)
    # check for duplicate reference designators
    strings.check_duplicate_ref_des(df)
    # check qty matches reference designator count
    frames.check_qty_matched_ref_des_count(df)

    # separate manufacturers to separate rows
    df = frames.split_manufacturers_to_separate_rows(df, bom_temp_ver, BomTempVer, source_file_type, SourceFileType)
    # clean up manufacturer name
    df = frames.cleanup_manufacturer(df)

    # clean up part number
    df = frames.cleanup_part_number(df)

    # add type information to description. Note do this before removing P/N from description or nan cell causes issue
    # df = frames.merge_type_data_with_description(df, bom_temp_ver)
    # remove part number from description
    # df = frames.remove_part_number_from_description(df)

    # *** write scrubbed cBOM data to file ***
    # get output BOM header labels as they are different depending upon BOM template version and output file format
    output_bom_header = frames.get_output_bom_header_labels(bom_temp_ver, BomTempVer, output_file_type, OutputFileType)
    # keep only the columns needed based on cBOM upload to dB
    df = frames.get_bom_columns(df, output_bom_header)
    # get path to output data folder
    folder_path = ctrl.get_folder(
        settings_key=ctrl.temp_setting_keys.DESTINATION_FILES_FOLDER,
        dialog_title="Select destination file data folder",
        dialog_prompt=None,
    )
    # Set Excel file name
    file_name = OutputFileType.dB_CB.value + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)

    return None


def sequence_ebom_for_db_upload():

    source_file_type = SourceFileType.EB
    output_file_type = OutputFileType.db_EB

    # *** read Excel data file ***
    # get path to input data folder
    folder_path = ctrl.get_folder(
        settings_key=ctrl.temp_setting_keys.SOURCE_FILES_FOLDER,
        dialog_title="Select source file data folder",
        dialog_prompt=None,
    )
    # get Excel file name to process
    file_name = menu.file_selector(
        folder_path_in=folder_path,
        extensions=importer.EXCEL_FILE_TYPES,
        menu_title="Select source file: ",
        menu_prompt=None,
    )
    # read excel file data
    excel_data = files.read_raw_excel_file_data(folder_path, file_name)

    # *** Extract cbom sheet to process ***
    df = files.get_user_selected_excel_file_sheet(excel_data)
    # only keep cost data for build on interest
    df = frames.select_build(df)

    # *** Extract ebom table ***
    # drop rows above BOM header and set top row as header
    df = frames.search_and_set_bom_header(df)
    # determine version of BOM template as it will determine how BOM cleanup will happen
    bom_temp_ver = frames.get_bom_template_version(df, BomTempVer)
    # get source BOM header labels as they are different depending upon BOM template version and source BOM type
    source_bom_header = frames.get_source_bom_header_labels(bom_temp_ver, BomTempVer, source_file_type, SourceFileType)
    df = frames.get_bom_columns(df, source_bom_header)
    # delete empty rows and columns
    df = frames.delete_empty_rows(df)
    df = frames.delete_empty_columns(df)
    # set datatype for columns
    df = frames.set_bom_column_datatype(df)

    # fill empty cells with data from above cell.
    df = frames.fill_empty_item_cells(df)
    # fill empty cells with data using alternative of the same components
    df = frames.fill_empty_cell_using_data_from_above_alternative(df)
    # replace alternative with data
    df = frames.replace_alternative_label_with_data_from_above_alternative(df)

    # fill in designators when designator cells are merged
    # df = frames.fill_merged_designators(df, bom_temp_ver, BomTempVer)

    # primary component should be first
    df = frames.primary_above_alternative(df, bom_temp_ver, BomTempVer)
    # merge alternative components to one row
    df = frames.merge_alternative(df)

    # *** Clean up ebom table ***
    # remove empty designator data
    df = frames.drop_items_with_empty_designator(df)
    # remove zero quantity data
    df = frames.drop_item_with_zero_quantity(df)
    # remove less than one quantity
    df = frames.drop_item_with_quantity_less_than_one(df)

    # clean up description column data
    df = frames.cleanup_description(df)
    # remove rows that have unwanted description items
    df = frames.drop_unwanted_db_ebom_description(df)

    # normalize component type labels
    df = frames.normalize_component_type_label(df)
    # remove rows that have unwanted component type items
    df = frames.drop_unwanted_db_ebom_component(df)

    # remove unwanted characters from designators
    df = frames.cleanup_designators(df)
    # unpack designator series
    df = frames.unpack_ref_des_series(df)
    # check reference designator format
    df = strings.check_ref_des_name(df)
    # check for duplicate reference designators
    strings.check_duplicate_ref_des(df)
    # check qty matches reference designator count
    frames.check_qty_matched_ref_des_count(df)

    # remove rows that have unwanted items
    df = frames.drop_rows_with_unwanted_ebom_items(df)

    # separate manufacturers to separate rows
    df = frames.split_manufacturers_to_separate_rows(df, bom_temp_ver, BomTempVer, source_file_type, SourceFileType)
    # clean up manufacturer name
    df = frames.cleanup_manufacturer(df)

    # clean up part number
    df = frames.cleanup_part_number(df)

    # add type information to description. Note do this before removing P/N from description or nan cell causes issue
    # df = frames.merge_type_data_with_description(df, bom_temp_ver)
    # remove part number from description
    # df = frames.remove_part_number_from_description(df)

    # *** write eBOM data to file ***
    # get output BOM header labels as they are different depending upon BOM template version and output file format
    output_bom_header = frames.get_output_bom_header_labels(bom_temp_ver, BomTempVer, output_file_type, OutputFileType)
    # keep only the columns needed based on eBOM upload to dB
    df = frames.get_bom_columns(df, output_bom_header)
    # get path to output data folder
    folder_path = ctrl.get_folder(
        settings_key=ctrl.temp_setting_keys.DESTINATION_FILES_FOLDER,
        dialog_title="Select destination file data folder",
        dialog_prompt=None,
    )
    # Set Excel file name
    file_name = OutputFileType.db_EB.value + file_name
    # write Excel file data
    files.write_single_sheet_excel_file_data(folder_path, file_name, df)

    return None
