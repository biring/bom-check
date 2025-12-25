"""
Mapper from version 3 BOM model to canonical BOM model.

This module maps verified and fixed version 3 BOM domain models into canonical BOM models used by downstream validation, comparison, and export stages.

Primary parts are identified by rows where `item` parses as an integer >= 1. Alternate parts are subsequent rows with empty or non-integer `item` values and are grouped under the most recent primary part.

Example Usage:
    # Preferred usage via package interface:
    # Not applicable; this is an internal module.

    # Direct module usage (unit tests or internal scripts only):
    from src.mappers import _v3_to_canonical as vc
    canonical = vc.map_bom(fixed_bom)

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Internal Packages: src.models.interfaces, src.mappers._dependencies

Notes:
    - This module is intentionally pure and side effect free.
    - Input BOMs must be verified and fixed before mapping.
    - Row order is assumed to be BOM-order correct as produced by the v3 parser.
    - Designators are sourced only from the primary row by domain assumption.
    - Mapping errors are surfaced as RuntimeError to preserve pipeline integrity.

License:
    - Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

from src.models.interfaces import (
    CanonicalBom,
    CanonicalBoard,
    CanonicalHeader,
    CanonicalPart,
    CanonicalComponent,

    Bom as V3Bom,
    Board as V3Board,
    Header as V3Header,
    Row as V3Row,
)

from . import _dependencies as dep


def _group_rows_to_parts(rows: tuple[V3Row, ...]) -> tuple[CanonicalPart, ...]:
    """
    Group ordered version 3 rows into canonical parts.

    Args:
        rows (tuple[V3Row, ...]): Ordered rows from a version 3 board.

    Returns:
        tuple[CanonicalPart, ...]: Canonical parts built from grouped rows.
    """
    # Row order is assumed to be BOM-order correct as produced by the version 3 parser
    parts: list[CanonicalPart] = []
    i = 0
    n = len(rows)

    while i < n:
        row = rows[i]
        item_str = row.item

        # A primary row is one where item is an integer >= 1
        if dep.parser.is_integer(item_str):
            item_int = dep.parser.parse_to_integer(item_str)
            if item_int >= 1:
                primary_row = row
                alt_rows: list[V3Row] = []

                j = i + 1
                # Any following row whose item is NOT an integer is an alternate
                while j < n and not dep.parser.is_integer(rows[j].item.strip()):
                    alt_rows.append(rows[j])
                    j += 1

                part = _map_rows_to_part(primary_row, tuple(alt_rows))
                parts.append(part)
                i = j
                continue

        # If not a valid primary, just move on
        i += 1

    return tuple(parts)


def _map_board(raw_board: V3Board) -> CanonicalBoard:
    """
    Map a version 3 board into a canonical board.

    Args:
        raw_board (V3Board): Verified version 3 board model.

    Returns:
        CanonicalBoard: Canonical board with mapped header and parts.
    """
    header = _map_header(raw_board.header)
    parts = _group_rows_to_parts(raw_board.rows)

    return CanonicalBoard(
        header=header,
        parts=parts,
    )


def _map_header(raw_header: V3Header) -> CanonicalHeader:
    """
    Map a version 3 header model to a canonical header model.

    Args:
        raw_header (V3Header): Verified version 3 header model.

    Returns:
        CanonicalHeader: Canonical representation of the header.
    """
    return CanonicalHeader(
        model_no=raw_header.model_no,
        board_name=raw_header.board_name,
        manufacturer=raw_header.manufacturer,
        build_stage=raw_header.build_stage,
        date=dep.parser.parse_to_datetime(raw_header.date),
        material_cost=dep.parser.parse_to_float(raw_header.material_cost),
        overhead_cost=dep.parser.parse_to_float(raw_header.overhead_cost),
        total_cost=dep.parser.parse_to_float(raw_header.total_cost),
    )


def _map_row_to_component(row: V3Row) -> CanonicalComponent:
    """
    Map version 3 row model into a canonical component model.

    The row may represent either a primary or alternate component.

    Args:
        row (V3Row): verified version 3 row.

    Returns:
        CanonicalComponent: canonical component built from row fields.
    """
    return CanonicalComponent(
        component_type=row.component_type.strip(),
        device_package=row.device_package.strip(),
        description=row.description.strip(),
        manufacturer=row.manufacturer.strip(),
        mfg_part_number=row.mfg_part_number.strip(),
        ul_vde_number=row.ul_vde_number.strip(),
        validated_at=tuple(row.validated_at.replace("/", ",").split(",")),
        unit_price=dep.parser.parse_to_float(row.unit_price),
    )


def _map_rows_to_part(primary: V3Row, alternates: tuple[V3Row, ...]) -> CanonicalPart:
    """
    Map a canonical Part model from a primary version 3 row and its alternates.

    Args:
        primary (V3Row): Primary version 3 row with a valid item number.
        alternates (tuple[V3Row, ...]): Alternate rows associated with the primary.

    Returns:
        CanonicalPart: canonical part with primary and alternate components.
    """
    primary_component = _map_row_to_component(primary)
    alt_components = tuple(_map_row_to_component(r) for r in alternates)

    return CanonicalPart(
        item=dep.parser.parse_to_integer(primary.item),
        designators=tuple(primary.designator.split(",")),
        # Designators are taken only from the primary row by domain assumption
        qty=dep.parser.parse_to_float(primary.qty),
        unit=primary.unit.strip(),
        classification=primary.classification.strip(),
        primary_component=primary_component,
        alternate_components=alt_components,
        sub_total=dep.parser.parse_to_float(primary.sub_total),
    )


def map_bom(fixed_bom: V3Bom) -> CanonicalBom:
    """
    Map a verified version 3 BOM into a canonical BOM.

    Args:
        fixed_bom (V3Bom): Verified and fixed version 3 BOM.

    Returns:
        CanonicalBom: Canonical BOM representation.

    Raises:
        RuntimeError: If verification or mapping fails.
    """
    try:
        # Mapping is only permitted for clean/fixed bom that pass verification
        dep.verify.v3_bom(fixed_bom)

        # Generate the boards
        boards = tuple(_map_board(b) for b in fixed_bom.boards)

        # Generate the bom
        canonical_bom = CanonicalBom(
            boards=boards,
            is_cost_bom=fixed_bom.is_cost_bom,
        )
    except (ValueError, RuntimeError) as error:
        raise RuntimeError(
            f"Canonical mapping failed for version 3 BOM '{fixed_bom.file_name}'. \n{error}"
        ) from error
    except Exception as ex:
        raise RuntimeError(
            f"Unexpected error during canonical mapping for version 3 BOM '{fixed_bom.file_name}'. \n{ex}"
        ) from ex

    return canonical_bom
