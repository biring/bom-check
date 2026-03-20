"""
Base controller providing shared state initialization and execution contract for application workflows.

This module defines a foundational controller that centralizes access to temporary settings storage and component type lookup data, ensuring consistent initialization and reuse of shared resources across higher-level workflow implementations.

Key Responsibilities:
	- Initialize and cache access to temporary settings storage for persisted user state
	- Expose a consistent set of keys for interacting with temporary settings
	- Load and retain a reusable lookup table for component type resolution
	- Define a required execution entry point for subclasses

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.controllers._base import BaseController
	controller = BaseController()

Dependencies:
	- Python version: >= 3.8
	- Standard Library: None

Notes:
	- Intended to be subclassed by concrete controllers implementing specific workflows
	- Assumes availability and stability of external settings storage and lookup providers
	- Wraps initialization failures to enforce a consistent error boundary

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.
from src.settings import temporary
from src.lookups import interfaces as lookup

class BaseController:

    def __init__(self):
        """
        Initialize controller-level shared caches and lookup tables.

        This constructor establishes access to temporary settings storage and component type lookup data
        that are expected to be reused across all subclasses. These values are fetched once at initialization
        and stored on the instance to avoid repeated lookup or recomputation.

        Invariants:
            - temp_settings_cache provides get_value and update_value interfaces for persisted temporary state.
            - temp_setting_keys contains the valid keys used with temp_settings_cache.
            - component_type_cache is assumed to be a stable lookup table for component type resolution.

        Returns:
            None

        Raises:
            RuntimeError: If initialization of any dependency fails.
        """
        try:
            # Retrieve a shared temporary settings cache used for persisting user selections such as folders.
            # This must succeed because all controllers depend on cached user state for default paths.
            self.temp_settings_cache = temporary.get_temp_settings()

            # Store the set of valid keys used to access values within the temp cache.
            # This avoids repeated imports and ensures consistent key usage across subclasses.
            self.temp_setting_keys = temporary.KEYS

            # Load a lookup table used for resolving component types.
            # This is expected to be relatively static and reused frequently, so it is cached at initialization.
            self.component_type_cache = lookup.get_component_type_lookup_table()

        except Exception as exc:
            # Wrap all initialization failures to enforce a consistent controller boundary error.
            # The original exception is preserved to retain root cause visibility.
            raise RuntimeError(
                f"Failed to initialize BaseController."
                f"\n{exc}"
            ) from exc

    def run(self) -> None:
        """
        Execute the controller workflow.

        This method defines the required execution entry point for all subclasses.
        Subclasses must implement this method to provide their specific workflow logic.

        Returns:
            None

        Raises:
            NotImplementedError: Always raised if the subclass does not override this method.
        """
        # Enforce that subclasses provide their own implementation.
        # Raising a RuntimeError instead of NotImplementedError creates a consistent controller boundary error type.
        raise NotImplementedError(
            "BaseController run() is not implemented. "
            "Subclasses must override this method to provide specific workflow logic."
        )