"""
Internal utilities for building standardized filenames from BOM metadata.

This module provides internal helpers for composing deterministic, filesystem-safe filenames derived from BOM header fields. It is intended to centralize filename construction logic used across logging, auditing, and pipeline outputs.

Filename composition may include:
    - Local date
    - Model number
    - Build stage
    - Optional board name (single-board BOMs only)
    - Fixed context-specific suffixes

All whitespace is removed to ensure portability across filesystems.

Example Usage:
    # Preferred usage via public interfaces:
    # Not applicable; this is an internal module.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.exporters import _build_filename as builder
    name = builder.build_checker_log_filename(bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: None
    - Internal Packages: src.models.interfaces, src.utils.timestamp

Notes:
    - Assumes BOMs contain at least one board.
    - Header-derived fields are taken from the first board by convention.
    - Board names are omitted for multi-board BOMs.
    - New builders must remain deterministic and whitespace-free.

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
