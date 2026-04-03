"""
Controller discovery and menu construction utilities for command-line workflows.

This module centralizes registration, validation, and presentation of available controllers by aggregating subclasses discovered via import side effects, transforming them into user-facing menu options, and aligning them with executable controller classes.

Key Responsibilities:
	- Import controller modules to trigger subclass registration via side effects
	- Retrieve and validate the global registry of available controllers
	- Enforce uniqueness of controller identifiers across the registry
	- Construct structured representations pairing metadata with callable classes
	- Sort controllers deterministically for stable menu presentation
	- Generate formatted menu options aligned with executable controller classes
	- Provide a command-line execution entry point for interactive selection

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	import src.controllers._menu_builder as mb
	menu, actions = mb.get_controllers()
	selection = get_menu_selection(menu_items)
    actions[selection]().run()

Dependencies:
	- Python version: >= 3.9
	- Standard Library:

Notes:
	- Relies on import side effects to populate the controller registry before invocation
	- Assumes all registered controllers expose consistent metadata attributes required for menu construction
	- Maintains deterministic ordering to ensure stable CLI behavior across executions
	- Couples menu display strings with execution classes via positional alignment

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

from . import _base as bc

# IMPORTANT! All controller modules must be imported here to ensure subclass discovery and menu creation
from . import _check_bom # noqa: F401
from . import _clean_bom # noqa: F401


def build_controller_menu() -> tuple[tuple[str, ...], tuple[type[bc.BaseController], ...]]:
    """
    Build sorted controller menu options and corresponding controller classes.

    Iterates over the registered BaseController subclasses, validates uniqueness of controller names,
    constructs ControllerSpec objects, and returns sorted menu display strings alongside their
    corresponding controller classes. Sorting is performed lexicographically by controller name to
    ensure deterministic menu ordering.

    Returns:
        tuple[tuple[str, ...], tuple[type[base.BaseController], ...]]:
            A tuple containing:
            - menu_options: Tuple of formatted menu strings ("name: description").
            - controller_calls: Tuple of controller classes aligned with menu_options order.

    Raises:
        ValueError: If duplicate controller names are detected in the registry.
        RuntimeError: If ControllerSpec construction fails for any controller.
    """
    # Retrieve the global registry of controller subclasses; assumed to be populated via import side effects
    controller_registry: list[type[bc.BaseController]] = bc.BaseController.registry

    # Accumulate validated and constructed ControllerSpec objects prior to sorting
    controller_specs: list[bc.ControllerSpec] = []

    # Track seen controller names to enforce uniqueness invariant across the registry
    seen_names: set[str] = set()

    # Iterate through all registered controller classes
    for controller_cls in controller_registry:
        # Enforce invariant: each controller must have a unique name; duplicates indicate misconfiguration
        if controller_cls.name in seen_names:
            raise ValueError(f"Duplicate controller name detected: '{controller_cls.name}' must be unique across all registered controllers.")

        # Record the name as seen after passing uniqueness validation
        seen_names.add(controller_cls.name)

        try:
            # Construct a specification object capturing metadata and callable reference
            # This centralizes controller metadata and ensures consistent downstream usage
            spec = bc.ControllerSpec(
                name=controller_cls.name,
                description=controller_cls.description,
                cls=controller_cls,
            )

            # Append successfully constructed spec for later sorting and transformation
            controller_specs.append(spec)

        except Exception as exc:
            # Wrap any exception during spec construction to provide context about the failing controller
            # This avoids silent failures and preserves the original traceback via exception chaining
            raise RuntimeError(
                f"Failed to construct controller {controller_cls!r}\n{exc}"
            ) from exc

    # Sort controller specifications deterministically by name to ensure stable menu ordering
    sorted_specs: list[bc.ControllerSpec] = sorted(controller_specs, key=lambda controller_spec: controller_spec.name)

    # Build user-facing menu strings; format couples name and description for CLI display
    menu_options: tuple[str, ...] = tuple(
        f"{spec.name}: {spec.description}" for spec in sorted_specs
    )

    # Extract controller classes in the same order as menu options to preserve index alignment
    controller_calls: tuple[type[bc.BaseController], ...] = tuple(
        spec.cls for spec in sorted_specs
    )

    # Return both menu display strings and corresponding controller classes as parallel tuples
    return menu_options, controller_calls