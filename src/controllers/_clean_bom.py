"""
Controller for executing the Version 3 BOM cleaning workflow.

This module defines an interactive controller that orchestrates the end-to-end cleaning, validation, transformation, and export of Version 3 Bill of Material (BOM) Excel workbooks. It coordinates user-driven file selection, structured parsing, staged normalization and correction, canonical mapping, template rendering, and final Excel export within a linear pipeline.

Key Responsibilities:
	- Prompt for source and destination folders and manage cached path state
	- Import Excel workbooks as raw sheet collections without header assumptions
	- Detect and parse Version 3 BOM structures into a domain model
	- Execute staged cleaning, fixing, and validation with audit log capture
	- Map the processed BOM into a canonical representation
	- Render canonical data into a Version 3 template format
	- Export rendered sheets to an Excel workbook with overwrite support

Example Usage:
	# Preferred usage via public package interface.
	# Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.controllers._v3_clean_bom import CleanBomController
	CleanBomController().run()

Dependencies:
	- Python version: >= 3.10
	- Standard Library: None
	- Third-Party: pandas

Notes:
	- Designed as a stateful controller where each pipeline stage stores its output on the instance
	- Assumes the input workbook conforms to Version 3 structure before downstream stages execute
	- Wraps all workflow failures in a RuntimeError to enforce a consistent controller boundary
	- Intended for interactive use with user-driven file system selection

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

import pandas as pd

from src.checkers import interfaces as checker
from src.cleaners import interfaces as cleaner
from src.exporters import interfaces as exporter
from src.fixers import interfaces as fixer
from src.importers import interfaces as importer
from src.mappers import interfaces as mapper
from src.menus import interfaces as menu
from src.models import interfaces as model
from src.parsers import interfaces as parser
from src.transformers import interfaces as transformer

from . import _base as base

_INPUT_DATA_FOLDER: str = "Select source data folder"
_INPUT_FILE_SELECTOR: str = "Select source Bill of Material excel file to clean"
_OUTPUT_DATA_FOLDER: str = "Select destination data folder"


class CleanBomController(base.BaseController):
    """
    Orchestrate the Version 3 BOM cleaning workflow.

    This controller coordinates user-driven file selection and executes a fixed pipeline over BOM data. The pipeline imports raw Excel sheets, parses V3 structure, cleans and fixes the model, checks it, maps it into a canonical representation, renders the canonical model back into a V3 template shape, and writes an Excel output.

    Invariants:
        - Workflow state is stored on the instance and is None until the corresponding stage completes.
        - The pipeline ordering is linear and stage outputs are used as inputs to later stages.
        - Cached folder paths are read from and written to the BaseController temp cache keys.

    Attributes:
        source_folder (str | None): User-selected directory containing the source BOM file.
        source_file (str | None): User-selected Excel BOM filename within source_folder.
        destination_folder (str | None): User-selected directory to receive the exported workbook.
        destination_file (str | None): Generated export filename derived from parsed BOM metadata.
        raw_sheets (dict[str, pd.DataFrame] | None): Raw imported workbook sheets keyed by sheet name.
        parsed_bom (model.BomV3 | None): Parsed V3 BOM domain model produced from input_bom.
        cleaned_bom (model.BomV3 | None): Cleaned V3 BOM after applying normalization and cleanup rules.
        fixed_bom (model.BomV3 | None): Fixed V3 BOM after applying structural and semantic corrections.
        canonical_bom (model.CanonicalBom | None): Canonical BOM mapped from the fixed V3 BOM.
        output_sheets (dict[str, pd.DataFrame] | None): Rendered sheets matching the V3 export template.
        v3_bom_template (pd.DataFrame | None): Template DataFrame used to render V3-formatted output sheets.
        cleaner_log (tuple[str, ...] | None): Cleaning stage audit log returned by the cleaner.
        fixer_log (tuple[str, ...] | None): Fixing stage audit log returned by the fixer.
        checker_log (tuple[str, ...] | None): Checker stage findings returned by the checker.
    """

    name = "Repair BOM"
    description = "Process BOM through automatic and manual error correction."

    def __init__(self):
        """
        Initialize controller-owned workflow state.

        All workflow artifacts are initialized to None to avoid accidental reuse of stale state across runs. This method also initializes the BaseController layer to ensure temp cache infrastructure exists.

        Returns:
            None
        """
        # Initialize BaseController first so temp cache and temp keys are available before any workflow use.
        super().__init__()

        # Source selection state is user-driven, so initialize as unset.
        self.source_folder: str | None = None
        self.source_file: str | None = None

        # Destination selection state is user-driven, so initialize as unset.
        self.destination_folder: str | None = None
        self.destination_file: str | None = None

        # Raw imported workbook sheets keyed by sheet name; populated immediately after file selection.
        self.raw_sheets: dict[str, pd.DataFrame] | None = None

        # Stage outputs are stored separately to preserve a linear pipeline and aid debugging.
        self.parsed_bom: model.BomV3 | None = None
        self.cleaned_bom: model.BomV3 | None = None
        self.fixed_bom: model.BomV3 | None = None
        self.canonical_bom: model.CanonicalBom | None = None

        # Output sheets rendered for export; populated after canonical mapping and template rendering.
        self.output_sheets: dict[str, pd.DataFrame] | None = None

        # Template used to render canonical content back into V3-shaped sheets.
        self.v3_bom_template: pd.DataFrame = pd.DataFrame()

        # Logs are stored independently to keep stage-specific audit trails.
        self.cleaner_log: tuple[str, ...] | None = None
        self.fixer_log: tuple[str, ...] | None = None
        self.checker_log: tuple[str, ...] | None = None

    def run(self) -> None:
        """
        Execute the interactive V3 BOM clean workflow end-to-end.

        Prompts the user for a source folder and file, imports the workbook, and conditionally runs the V3 pipeline. The V3 pipeline parses, cleans, fixes, checks, maps to canonical, renders to a V3 template, and exports results. Any exception raised by downstream components is wrapped to provide a consistent controller boundary error.

        Returns:
            None

        Raises:
            RuntimeError: If any stage of the workflow fails.
        """
        try:
            # Resolve source data folder
            self.source_folder = self.get_folder(
                settings_key=self.temp_setting_keys.SOURCE_FILES_FOLDER,
                dialog_title=_INPUT_DATA_FOLDER,
                dialog_prompt=None,
            )

            # Prompt user to select the source BOM Excel file within the chosen folder.
            self.source_file = menu.file_selector(
                folder_path_in=self.source_folder,
                extensions=importer.EXCEL_FILE_TYPES,
                menu_title=_INPUT_FILE_SELECTOR,
                menu_prompt=None,
            )

            # Import every sheet as a DataFrame without assuming a header row.
            # Downstream parsing logic is responsible for interpreting structure and headers.
            self.raw_sheets = importer.read_excel_as_dict(
                folder=self.source_folder,
                file_name=self.source_file,
                top_row_is_header=False,
            )

            # Only run the V3 pipeline when the imported workbook matches the expected V3 structure.
            # If this condition is false, the method continues and may later fail when required state is missing.
            if parser.is_v3_bom(self.raw_sheets):
                # Parse V3 workbook into the V3 domain model that all subsequent stages expect.
                self.parsed_bom = parser.parse_v3_bom(
                    file_name=self.source_file,
                    sheets=self.raw_sheets,
                )

                # Clean the parsed BOM and capture the cleaner log for auditability.
                self.cleaned_bom, self.cleaner_log = cleaner.clean_v3_bom(bom=self.parsed_bom)

                # Fix the cleaned BOM and capture the fixers log for auditability.
                self.fixed_bom, self.fixer_log = fixer.fix_v3_bom(bom=self.cleaned_bom)

                # Run the checker to record validation findings against the fixed BOM.
                self.checker_log = checker.check_v3_bom(bom=self.fixed_bom)

                # Map the fixed V3 BOM to a canonical representation for consistent transformation and export.
                self.canonical_bom = mapper.map_v3_to_canonical_bom(fixed_bom=self.fixed_bom)

                # Load the V3 template used to produce a workbook in the expected downstream format.
                self.v3_bom_template = importer.load_version3_bom_template()

                # Render the canonical BOM into V3 template sheets.
                self.output_sheets = transformer.canonical_to_v3_template_sheets(
                    canonical_bom=self.canonical_bom,
                    template_df=self.v3_bom_template,
                )

            # Resolve destination folder
            self.destination_folder = self.get_folder(
                settings_key=self.temp_setting_keys.DESTINATION_FILES_FOLDER,
                dialog_title=_OUTPUT_DATA_FOLDER,
                dialog_prompt=None,
            )

            # Build the destination filename from parsed BOM metadata.
            # This assumes self.parsed_bom exists, which is only guaranteed if the V3 branch executed successfully.
            self.destination_file = exporter.build_checker_log_filename(bom=self.parsed_bom)

            # Render output sheets again before export, preserving the original redundancy and output determinism.
            self.output_sheets = transformer.canonical_to_v3_template_sheets(
                canonical_bom=self.canonical_bom,
                template_df=self.v3_bom_template,
            )

            # Write the output workbook, overwriting any existing file of the same name.
            exporter.write_excel_sheets(
                folder=self.destination_folder,
                file_name=self.destination_file,
                sheets=self.output_sheets,
                overwrite=True,
                top_row_is_header=False,
            )

        except Exception as exc:
            # Wrap any failure to provide a single high-level workflow error while preserving the original exception chain.
            raise RuntimeError(
                f"Bom clean workflow failed."
                f"\n{exc}"
            ) from exc
