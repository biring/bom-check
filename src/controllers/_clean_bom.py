"""
Controller for orchestrating a structured Version 3 Bill of Material cleaning workflow.

This module provides an interactive, stateful workflow that guides a user through selecting input data, processing it through multiple transformation stages, and exporting both cleaned outputs and audit logs. It coordinates the full lifecycle from raw spreadsheet ingestion to validated and formatted export artifacts.

Key Responsibilities:
	- Prompt for source and destination locations with cached state support
	- Import spreadsheet data as raw sheet collections without structural assumptions
	- Detect and parse Version 3 Bill of Material structures into a domain representation
	- Execute staged cleaning, correction, and validation with audit logging
	- Transform processed data into a canonical representation for consistency
	- Render canonical data into a structured template format for export
	- Export processed data and logs to output files with overwrite handling

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.controllers import _clean_bom as cb
	cb.CleanBomController().run()

Dependencies:
	- Python version: >= 3.10
	- Standard Library: None

Notes:
	- Designed as a stateful controller where each processing stage stores intermediate results
	- Assumes input data conforms to the expected Version 3 structure prior to transformation
	- Enforces a linear pipeline where each stage depends on outputs from previous stages
	- Wraps all workflow errors into a single runtime exception for consistent error handling
	- Intended for interactive execution with user-driven file selection

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
_EMPTY_CHECKER_LOG_MESSAGE: tuple[str, ...] = ("No BOM issues found during validation.",)
_EMPTY_CLEANER_LOG_MESSAGE: tuple[str, ...] = ("No BOM data required cleaning.",)
_EMPTY_FIXER_LOG_MESSAGE: tuple[str, ...] = ("No BOM data required fixes.",)

class CleanBomController(base.BaseController):
    """
    Orchestrate the Version 3 BOM cleaning workflow.

    This controller coordinates user-driven file selection and executes a fixed pipeline over BOM data. The pipeline imports raw Excel sheets, parses V3 structure, cleans and fixes the model, checks it, maps it into a canonical representation, renders the canonical model back into a V3 template shape, and writes an Excel output.

    Invariants:
        - Workflow stage attributes remain None until their corresponding stage completes.
        - Pipeline stages execute in a fixed order and later stages depend on earlier outputs.
        - Source and destination folder selections are resolved through BaseController cache-backed prompts.
        - Checker findings are treated as a hard failure after export-log generation if unresolved issues remain.

    Attributes:
        source_folder (str | None): Selected folder containing the source BOM workbook.
        source_file (str | None): Selected BOM workbook filename within source_folder.
        destination_folder (str | None): Selected folder for output workbook and log files.
        destination_file (str | None): Most recently generated output filename.
        raw_sheets (dict[str, pd.DataFrame] | None): Imported workbook sheets keyed by sheet name.
        parsed_bom (model.BomV3 | None): Parsed Version 3 BOM model produced from raw_sheets.
        cleaned_bom (model.BomV3 | None): Cleaned BOM after normalization and cleanup rules run.
        fixed_bom (model.BomV3 | None): Fixed BOM after correction logic runs.
        canonical_bom (model.CanonicalBom | None): Canonical representation mapped from fixed_bom.
        output_sheets (dict[str, pd.DataFrame] | None): Rendered export sheets derived from canonical_bom.
        v3_bom_template (pd.DataFrame): Template DataFrame used to render Version 3 output sheets.
        cleaner_log (tuple[str, ...] | None): Audit log returned by the cleaner stage.
        fixer_log (tuple[str, ...] | None): Audit log returned by the fixer stage.
        checker_log (tuple[str, ...] | None): Validation findings returned by the checker stage.
    """

    name = "Repair BOM"
    description = "Clean, correct, validate, and generate a repaired BOM file."

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

        Orchestrates a strict linear pipeline that:
        - Prompts user for source and destination locations
        - Imports raw Excel sheets
        - Parses, cleans, fixes, and validates BOM data
        - Maps to canonical representation and renders output
        - Exports results and audit logs

        All stage outputs are stored on the instance and must be produced in order.
        Any failure in downstream stages is wrapped into a RuntimeError to enforce a consistent controller boundary.

        Returns:
            None

        Raises:
            RuntimeError: If any stage of the workflow fails or if post-processing validation fails.
        """
        try:
            # Resolve source data folder using cached setting if available.
            # This enforces consistency across runs and reduces repeated user input.
            self.source_folder = self.get_folder(
                settings_key=self.temp_setting_keys.SOURCE_FILES_FOLDER,
                dialog_title=_INPUT_DATA_FOLDER,
                dialog_prompt=None,
            )

            # Prompt user to select a valid Excel file from the chosen folder.
            # Restricts selection to supported Excel file types defined by importer.
            self.source_file = menu.file_selector(
                folder_path_in=self.source_folder,
                extensions=importer.EXCEL_FILE_TYPES,
                menu_title=_INPUT_FILE_SELECTOR,
                menu_prompt=None,
            )

            # Import all sheets without assuming headers.
            # Structural interpretation is deferred to the parser to centralize format logic.
            self.raw_sheets = importer.read_excel_as_dict(
                folder=self.source_folder,
                file_name=self.source_file,
                top_row_is_header=False,
            )

            # Parse raw sheets into a structured V3 BOM domain model.
            # This is the first stage that enforces schema expectations.
            self.parsed_bom = parser.parse_v3_bom(
                file_name=self.source_file,
                sheets=self.raw_sheets,
            )

            # Clean parsed BOM and capture audit log.
            # Cleaning normalizes and removes inconsistencies without altering intent.
            self.cleaned_bom, self.cleaner_log = cleaner.clean_v3_bom(bom=self.parsed_bom)

            # Apply structural and semantic fixes to cleaned BOM.
            # Fixes may modify data to enforce correctness.
            self.fixed_bom, self.fixer_log = fixer.fix_v3_bom(bom=self.cleaned_bom)

            # Validate fixed BOM and collect findings.
            # Checker does not mutate data; it only reports issues.
            self.checker_log = checker.check_v3_bom(bom=self.fixed_bom)

            # Map V3 BOM into canonical representation for consistent downstream processing.
            self.canonical_bom = mapper.map_v3_to_canonical_bom(fixed_bom=self.fixed_bom)

            # Load template used to render canonical BOM into V3-compatible output format.
            self.v3_bom_template = importer.load_version3_bom_template()

            # Render canonical BOM into structured output sheets using template.
            self.output_sheets = transformer.canonical_to_v3_template_sheets(
                canonical_bom=self.canonical_bom,
                template_df=self.v3_bom_template,
            )

            # Resolve destination folder for output artifacts.
            self.destination_folder = self.get_folder(
                settings_key=self.temp_setting_keys.DESTINATION_FILES_FOLDER,
                dialog_title=_OUTPUT_DATA_FOLDER,
                dialog_prompt=None,
            )

            # Build output filename based on parsed BOM metadata.
            # Assumes parsed_bom is valid and present at this stage.
            self.destination_file = exporter.build_checker_log_filename(bom=self.parsed_bom)

            # Write transformed sheets to Excel, overwriting existing files if necessary.
            exporter.write_excel_sheets(
                folder=self.destination_folder,
                file_name=self.destination_file,
                sheets=self.output_sheets,
                overwrite=True,
                top_row_is_header=False,
            )

            # --- Cleaner Log Export ---
            self.destination_file = exporter.generate_log_filename(exporter.LogTypes.CLEANER)

            # Ensure log is never empty to avoid ambiguity in downstream consumption.
            if self.cleaner_log is None or len(self.cleaner_log) == 0:
                self.cleaner_log = _EMPTY_CLEANER_LOG_MESSAGE

            # Persist cleaner log to disk.
            exporter.write_text_file_lines(
                folder=self.destination_folder,
                file_name=self.destination_file,
                lines=self.cleaner_log,
                overwrite=True,
            )

            # --- Fixer Log Export ---
            self.destination_file = exporter.generate_log_filename(exporter.LogTypes.FIXER)

            # Ensure log is never empty.
            if self.fixer_log is None or len(self.fixer_log) == 0:
                self.fixer_log = _EMPTY_FIXER_LOG_MESSAGE

            # Persist fixer log.
            exporter.write_text_file_lines(
                folder=self.destination_folder,
                file_name=self.destination_file,
                lines=self.fixer_log,
                overwrite=True,
            )

            # --- Checker Log Export ---
            self.destination_file = exporter.generate_log_filename(exporter.LogTypes.CHECKER)

            # Ensure log is never empty.
            if self.checker_log is None or len(self.checker_log) == 0:
                self.checker_log = _EMPTY_CHECKER_LOG_MESSAGE

            # Persist checker log.
            exporter.write_text_file_lines(
                folder=self.destination_folder,
                file_name=self.destination_file,
                lines=self.checker_log,
                overwrite=True,
            )

            # Enforce invariant: checker log must be empty after processing.
            # Any remaining issues indicate unresolved validation failures.
            if self.checker_log != _EMPTY_CHECKER_LOG_MESSAGE:
                raise RuntimeError("Post processing checker log is not empty.")

        except Exception as exc:
            # Wrap any failure to provide a single high-level workflow error while preserving the original exception chain.
            raise RuntimeError(
                f"Bom clean workflow failed."
                f"\n{exc}"
            ) from exc
