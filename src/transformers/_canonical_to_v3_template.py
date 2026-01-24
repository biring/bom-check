"""
Transform canonical BOM data into Version 3 Excel template sheets.

This module provides the transformation layer that renders canonical bill-of-materials data into a Version 3 Excel-compatible tabular format using a predefined template. It bridges canonical domain models with a strict template schema by normalizing header metadata, flattening part and component relationships into rows, and enforcing template validation rules during rendering.

Key responsibilities
	- Normalize canonical header data into a flat attribute mapping suitable for template metadata regions.
	- Convert canonical parts and components into table row mappings with explicit handling of alternate components.
	- Validate and populate a Version 3 template DataFrame with header and table data.
	- Render multiple boards from a canonical BOM into isolated template-backed DataFrames.

Example usage
	# Preferred usage via public package interface
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only)
	from src.transformers._canonical_to_v3_template import canonical_to_v3_template_sheets
	sheets = canonical_to_v3_template_sheets(canonical_bom, template_df)

Dependencies
	- Python 3.x
	- Standard Library: typing

Notes
	- Rendering is strict and fails fast if required template labels or table schema elements are missing.
	- Alternate components are rendered as additional rows with suppressed quantity and cost values to prevent double counting.
	- Each board is rendered using an independent copy of the template to avoid cross-board state leakage.
	- This module assumes that upstream canonical models and template mappers are already validated and well-formed.

License
	- Internal Use Only
"""

from typing import Any

import pandas as pd

from src.adapters.interfaces import (
    map_canonical_to_template_v3_header,
    map_canonical_to_template_v3_table,
)

from src.helpers.interfaces import (
    Metadata,
    Record,
)

from src.models.interfaces import (
    CanonicalBom,
    CanonicalBoard,
    CanonicalHeader,
    CanonicalHeaderAttrNames,
    CanonicalPart,
    CanonicalComponent,
    CanonicalPartAttrNames,
    CanonicalComponentAttrNames,
)

from src.schemas.interfaces import (
    TABLE_TITLE_ROW_IDENTIFIERS_V3,
    TEMPLATE_IDENTIFIERS_V3,
)

from src.utils import timestamp


def _canonical_header_to_dict(header: CanonicalHeader) -> dict[str, Any]:
    """
    Normalize a canonical header model into a flat attribute dictionary.

    This function performs lossy normalization by coercing most header fields to string form while preserving numeric cost fields as-is. The resulting mapping is designed to be consumed by a template-specific header mapper.

    Args:
        header (CanonicalHeader): Canonical header model for a single board.

    Returns:
        dict[str, Any]: Mapping of canonical header attribute names to values.
    """
    return {
        CanonicalHeaderAttrNames.MODEL_NUMBER: str(header.model_no),
        CanonicalHeaderAttrNames.BOARD_NAME: str(header.board_name),
        CanonicalHeaderAttrNames.BOARD_SUPPLIER: str(header.manufacturer),
        CanonicalHeaderAttrNames.BUILD_STAGE: str(header.build_stage),
        CanonicalHeaderAttrNames.BOM_DATE: timestamp.format_date_iso(header.date),
        CanonicalHeaderAttrNames.MATERIAL_COST: header.material_cost,
        CanonicalHeaderAttrNames.OVERHEAD_COST: header.overhead_cost,
        CanonicalHeaderAttrNames.TOTAL_COST: header.total_cost,
    }


def _canonical_row_to_dict(
        part: CanonicalPart,
        component: CanonicalComponent,
        *,
        level: int,
) -> dict[str, Any]:
    """
    Convert a canonical part and component pair into a flat table row mapping.

    The level parameter controls whether the row represents a primary component (level == 0) or an alternate component (level > 0). Alternate rows follow a strict convention that suppresses quantity, pricing, and identifying fields while encoding the alternate index into the component type.

    Args:
        part (CanonicalPart): Canonical part owning the component relationship.
        component (CanonicalComponent): Component instance for this row.
        level (int): Alternate depth where 0 indicates the primary component.

    Returns:
        dict[str, Any]: Mapping of canonical part and component attributes.

    Raises:
        ValueError: If level is negative, which would violate row semantics.
    """
    # Negative levels would imply an invalid or undefined row classification, so this is explicitly rejected rather than silently normalized.
    if level < 0:
        raise ValueError(f"level must be >= 0, got {level}")

    # Base row values are populated identically for primary and alternate rows before alternate-specific suppression is applied.
    values: dict[str, Any] = {
        CanonicalPartAttrNames.ITEM: part.item,
        CanonicalComponentAttrNames.COMPONENT_TYPE: str(component.component_type),
        CanonicalComponentAttrNames.DEVICE_PACKAGE: str(component.device_package),
        CanonicalComponentAttrNames.DESCRIPTION: str(component.description),
        CanonicalPartAttrNames.UNITS: str(part.unit),
        CanonicalPartAttrNames.CLASSIFICATION: str(part.classification),
        CanonicalComponentAttrNames.MANUFACTURER: str(component.manufacturer),
        CanonicalComponentAttrNames.MFG_PART_NO: str(component.mfg_part_number),
        CanonicalComponentAttrNames.UL_VDE_NUMBER: str(component.ul_vde_number),
        CanonicalComponentAttrNames.VALIDATED_AT: "/".join(component.validated_at),
        CanonicalPartAttrNames.QTY: part.qty,
        CanonicalPartAttrNames.DESIGNATORS: ",".join(part.designators),
        CanonicalComponentAttrNames.UNIT_PRICE: component.unit_price,
        CanonicalPartAttrNames.SUB_TOTAL: part.sub_total,
    }

    # Alternate-row conventions intentionally blank or zero out fields that would otherwise double-count quantities or costs. The ALT{level} marker encodes ordering while preserving template compatibility.
    if level > 0:
        values[CanonicalPartAttrNames.ITEM] = ""
        values[CanonicalPartAttrNames.DESIGNATORS] = ""
        values[CanonicalPartAttrNames.QTY] = 0
        values[CanonicalComponentAttrNames.UNIT_PRICE] = 0
        values[CanonicalPartAttrNames.SUB_TOTAL] = 0
        values[CanonicalComponentAttrNames.COMPONENT_TYPE] = f"ALT{level}"

    return values


class _V3TemplateSheet(Metadata, Record):
    """
    Render a canonical board into a version 3 template DataFrame.

    This class binds template validation, header writing, and table population into a single workflow object. It owns and mutates a working DataFrame copy and enforces the discovery of table schema prior to record insertion.

    Invariants:
    - The backing DataFrame is a deep copy of the provided template.
    - Header labels must be present; missing labels are treated as errors.
    - Table records are written strictly to enforce schema correctness.

    Attributes:
        df (pd.DataFrame): Working DataFrame mutated during rendering.
        _table_start_row (int): First row index after the table title row.
    """

    def __init__(self, template_df: pd.DataFrame) -> None:
        """
        Initialize a renderer bound to a specific v3 template DataFrame.

        The template is validated for required identifiers and scanned for the table schema immediately so subsequent writes can assume a consistent structure.

        Args:
            template_df (pd.DataFrame): Raw template DataFrame to render into.
        """
        # Metadata initialization validates the template structure and produces a working DataFrame copy to avoid mutating the caller's instance.
        Metadata.__init__(
            self,
            df=template_df.copy(deep=True),
            template_identifiers=TEMPLATE_IDENTIFIERS_V3,
        )

        # Record initialization discovers table headers and column ordering on the same DataFrame instance produced by Metadata.
        Record.__init__(
            self,
            df=self.df,
            title_identifiers=TABLE_TITLE_ROW_IDENTIFIERS_V3,
        )

        # The table is expected to begin immediately after the title row; this invariant is relied upon when appending records.
        self._table_start_row: int = self._schema.title_row + 1

    def render_board(self, board: CanonicalBoard) -> pd.DataFrame:
        """
        Render a single canonical board into the template DataFrame.

        Header metadata is written first, followed by strict table population for all parts and their alternates.

        Args:
            board (CanonicalBoard): Canonical board model to render.

        Returns:
            pd.DataFrame: Fully rendered DataFrame for the board.
        """
        self._write_header(board.header)
        self._write_table(board)
        return self.df

    def _write_header(self, header: CanonicalHeader) -> None:
        """
        Write canonical header values into the template metadata area.

        Header writes are strict: if a required label is missing from the template, the write fails rather than silently skipping. This enforces that templates used for rendering contain the expected metadata surface area.

        Args:
            header (CanonicalHeader): Canonical header to render.
        """
        canonical_header_values = _canonical_header_to_dict(header)
        header_label_map = map_canonical_to_template_v3_header(canonical_header_values)

        # By convention, template values appear one column to the right of their labels; this offset is applied uniformly.
        label_offsets = {label: (0, 1) for label in header_label_map}

        # Strict mode ensures missing labels are treated as template violations, preventing partially written headers that might be mistaken as complete.
        self.write_metadata(
            label_offsets=label_offsets,
            label_values=header_label_map,
            strict=True,
        )

    def _write_table(self, board: CanonicalBoard) -> None:
        """
        Populate the template table with all parts and components for a board.

        Primary component rows are written first, followed immediately by any alternate component rows in ascending level order.

        Args:
            board (CanonicalBoard): Canonical board containing parts to render.
        """
        # The append cursor is aligned to the last filled row to support templates that may include pre-existing data.
        self._last_filled_df_row = self._find_last_filled_record_df_row()

        for part in board.parts:
            # Primary rows are written with level 0 semantics and must conform exactly to the discovered table schema.
            primary_values = _canonical_row_to_dict(
                part,
                part.primary_component,
                level=0,
            )
            primary_mapped = map_canonical_to_template_v3_table(primary_values)
            self.write_record(primary_mapped, strict=True)

            # Alternate components are rendered as additional rows that share the same part context but suppress quantity and cost fields.
            for level, alt in enumerate(part.alternate_components, start=1):
                alt_values = _canonical_row_to_dict(part, alt, level=level)
                alt_mapped = map_canonical_to_template_v3_table(alt_values)
                self.write_record(alt_mapped, strict=True)


def canonical_to_v3_template_sheets(
        canonical_bom: CanonicalBom,
        template_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Render all boards in a canonical BOM into v3 template sheets.

    Each board is rendered independently using a fresh copy of the template to avoid cross-board state leakage.

    Args:
        canonical_bom (CanonicalBom): Canonical BOM containing one or more boards.
        template_df (pd.DataFrame): Base v3 template DataFrame.

    Returns:
        dict[str, pd.DataFrame]: Mapping of sheet name to rendered DataFrame.
    """
    sheets: dict[str, pd.DataFrame] = {}
    for board in canonical_bom.boards:
        # Board names are stripped to avoid Excel sheet naming issues caused by accidental whitespace in upstream data.
        sheet_name = board.header.board_name.strip()
        sheets[sheet_name] = _V3TemplateSheet(template_df).render_board(board)
    return sheets


if __name__ == "__main__":
    from tests.fixtures import canonical as fx_canonical
    from src.importers import interfaces as importer
    from src.settings import temporary
    from src.utils import excel_io
    from src.utils import file_path

    template = importer.load_version3_bom_template()
    bom = fx_canonical.BOM_A_CANONICAL

    export_sheets = canonical_to_v3_template_sheets(bom, template)

    folder_path = temporary.get_temp_settings().get_value(
        temporary.KEYS.DESTINATION_FILES_FOLDER,
        str,
    )
    export_file_path = file_path.construct_file_path(folder_path, "testing.xlsx")

    excel_io.write_sheets_to_excel(export_file_path, export_sheets, True, False)
