"""
Internal utilities for constructing deterministic, filesystem-safe filenames from structured metadata.

This module centralizes logic for composing standardized filenames derived from structured data and timestamp components, ensuring consistency across logging, auditing, and pipeline outputs.

Key Responsibilities:
	- Construct deterministic filenames using structured metadata fields
	- Extract identifying attributes from structured input data for naming purposes
	- Generate timestamp-based filenames for log artifacts
	- Enforce whitespace-free and filesystem-safe naming conventions
	- Normalize error handling into a consistent runtime exception model

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.exporters import _build_filename as builder
	name = builder.generate_timestamped_log_filename(DebugLog)

Dependencies:
	- Python version: >= 3.10
	- Standard Library: None

Notes:
	- Assumes structured input contains at least one data element for metadata extraction
	- Uses the first available element as the canonical source for shared attributes
	- Omits optional attributes when multiple elements are present
	- Enforces deterministic output to support reproducibility and traceability
	- All generated filenames are stripped of whitespace for portability

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from ._dependencies import model
from ._dependencies import timestamp

FILE_NAME_SEPARATOR = "-"
SUFFIX_CHECKER_LOG = 'CheckerLog'


def _extract_board_name(bom: model.BomV3) -> str | None:
    """
    Extract the board name if the BOM contains exactly one board.

    Args:
        bom (Bom): Parsed BOM.

    Returns:
        str | None: Board name if exactly one board exists, otherwise None.
    """
    if len(bom.boards) > 1:
        return None  # Board name omitted for multi-board BOMs
    else:
        return bom.boards[0].header.board_name


def _extract_build_stage(bom: model.BomV3) -> str:
    """
    Extract the build stage from the first board header in a BOM.

    Args:
        bom (Bom): Parsed BOM containing at least one board.

    Returns:
        str: Build stage identifier.

    Raises:
        ValueError: If the BOM contains no boards.
    """
    # Return build stage from the first available board
    for board in bom.boards:
        return board.header.build_stage

    # Defensive failure: BOM exists but contains no boards
    raise ValueError("Build stage not found in BOM headers")


def _extract_model_number(bom: model.BomV3) -> str:
    """
    Extract the model number from the first board header in a BOM.

    Args:
        bom (Bom): Parsed BOM containing at least one board.

    Returns:
        str: Model number from the BOM header.

    Raises:
        ValueError: If the BOM contains no boards.
    """
    # Return model number from the first available board
    for board in bom.boards:
        return board.header.model_no  # First board defines the model number

    # Defensive failure: BOM exists but contains no boards
    raise ValueError("Model number not found in BOM header")


def build_checker_log_filename(bom: model.BomV3) -> str:
    """
    Build a standardized checker log filename from BOM header metadata.

    The filename is composed of local date, model number, build stage,
    optional board name (only for single-board BOMs), and a fixed suffix.
    All whitespace is removed from the final filename.

    Args:
        bom (Bom): Parsed BOM containing one or more boards.

    Returns:
        str: Checker log filename suitable for filesystem use.

    Raises:
        RuntimeError: If required BOM metadata cannot be extracted.
    """

    try:
        filename = timestamp.now_local_date()

        filename += FILE_NAME_SEPARATOR + _extract_model_number(bom)

        filename += FILE_NAME_SEPARATOR + _extract_build_stage(bom)

        board_name = _extract_board_name(bom)
        if board_name:
            filename += FILE_NAME_SEPARATOR + board_name

        filename += FILE_NAME_SEPARATOR + SUFFIX_CHECKER_LOG

        return filename.replace(" ", "")  # Enforce whitespace-free filenames

    except ValueError as ve:
        raise RuntimeError(
            f"Failed to build checker log filename."
            f"\n{ve!r}"
        ) from ve
    except Exception as ex:
        raise RuntimeError(
            f"Unexpected error when building checker log filename."
            f"\n{ex!r}"
        ) from ex

def generate_timestamped_log_filename(log_type_suffix: str) -> str:
    """
    Build a standardized log filename using timestamp components and a log type suffix.

    This function enforces a minimum length requirement for the log type to ensure
    filenames remain meaningful and distinguishable.

    Args:
        log_type_suffix (str): Identifier describing the log type.

    Returns:
        str: A timestamp-based log filename.

    Raises:
        RuntimeError: If validation fails or an unexpected error occurs.
    """
    try:
        # Enforce minimum length invariant to avoid trivial or meaningless filenames
        minimum_log_type_length = 3
        if len(log_type_suffix) <= minimum_log_type_length:
            # Validation failure: log type must be sufficiently descriptive
            raise ValueError(f"Log file type must be longer than {minimum_log_type_length} characters.")

        # Compose filename using date and time to ensure uniqueness
        return (
                timestamp.now_local_date()
                + FILE_NAME_SEPARATOR
                + timestamp.now_local_time()
                + FILE_NAME_SEPARATOR
                + log_type_suffix
        )

    except ValueError as ve:
        # Normalize validation errors into consistent RuntimeError for callers
        raise RuntimeError(
            f"Failed to build '{log_type_suffix}' log filename."
            f"\n{ve!r}"
        ) from ve
    except Exception as ex:
        # Catch-all for unexpected issues to maintain stable API contract
        raise RuntimeError(
            f"Unexpected error when building '{log_type_suffix}' log filename."
            f"\n{ex!r}"
        ) from ex
