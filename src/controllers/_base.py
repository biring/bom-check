"""
Base controller providing shared state initialization and execution contract for application workflows.

This module defines a foundational controller that centralizes access to temporary settings storage and component type lookup data, ensuring consistent initialization and reuse of shared resources across higher-level workflow implementations.

Key Responsibilities:
	- Initialize and cache access to temporary settings storage for persisted state
	- Expose a consistent set of keys for interacting with temporary settings
	- Load and retain a reusable lookup table for component type resolution
	- Enforce subclass metadata requirements and automatic registration
	- Provide a standardized execution entry point for workflow implementations
	- Encapsulate controller metadata into immutable specifications for transport and usage

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.controllers._base import BaseController
	controller = BaseController()

Dependencies:
	- Python version: >= 3.10
	- Standard Library: dataclasses

Notes:
	- Intended to be subclassed by concrete workflow controllers
	- Assumes availability of external temporary settings storage and lookup providers
	- Enforces metadata presence at class definition time for discoverability
	- Wraps initialization failures to provide a consistent error boundary

License:
	- Internal Use Only
"""
from __future__ import annotations

__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

from dataclasses import dataclass
from src.settings import temporary
from src.lookups import interfaces as lookup

class BaseController:
    """
    Provide a base implementation for workflow controllers with shared initialization and registration behavior.

    This class centralizes access to temporary settings storage and component type lookup data so subclasses
    can rely on consistent, cached state. It also enforces subclass metadata requirements and maintains a registry
    of all concrete controller implementations.

    Invariants:
        - Subclasses must define NAME and DESCRIPTION at class definition time.
        - REGISTRY contains all non-abstract subclasses that satisfy metadata requirements.
        - Instance attributes temp_settings_cache, temp_setting_keys, and component_type_cache are initialized successfully or construction fails.

    Attributes:
        registry (list[type[BaseController]]): Collection of all registered subclasses.
        name (str | None): Human-readable name for the controller; required for subclasses.
        description (str | None): Description of the controller; required for subclasses.
        temp_settings_cache: Cached interface to temporary settings storage.
        temp_setting_keys: Valid keys for interacting with the temporary settings cache.
        component_type_cache: Cached lookup table for component type resolution.
    """

    registry: list[type["BaseController"]] = []
    name: str | None = None
    description: str | None = None

    def __init_subclass__(cls, **kwargs):
        """
        Register subclasses and enforce required metadata attributes.

        This hook runs automatically when a subclass is defined. It ensures that all concrete subclasses define
        NAME and DESCRIPTION, and registers them in the global REGISTRY for later discovery.

        Args:
            **kwargs: Arbitrary keyword arguments passed to superclass implementation.

        Returns:
            None

        Raises:
            TypeError: If a subclass does not define NAME or DESCRIPTION.
        """
        # Delegate to parent implementation to preserve Python's subclass initialization chain
        super().__init_subclass__(**kwargs)

        # Skip validation for the base class itself to avoid self-registration and incomplete metadata enforcement
        if cls is BaseController:
            return

        # Enforce invariant: all concrete subclasses must define identifying metadata
        # This guarantees discoverability and consistent external representation
        if not cls.name or not cls.description:
            raise TypeError(f"{cls.__name__} must define 'name' and 'description'")

        # Register the validated subclass for later lookup or enumeration
        # Assumes subclasses are defined once and not dynamically redefined
        BaseController.registry.append(cls)

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

@dataclass(frozen=True)
class ControllerSpec:
    """
    Represent an immutable specification describing a controller.

    This data structure encapsulates identifying metadata and the controller class itself,
    enabling consistent transport and usage of controller definitions across the system.

    Invariants:
        - Instances are immutable due to frozen=True.
        - name and description correspond to the associated controller metadata.
        - controller must be a subclass of BaseController.

    Attributes:
        name (str): Human-readable name of the controller.
        description (str): Description of the controller's purpose or behavior.
        cls (type[BaseController]): Reference to the controller class.
    """

    name: str
    description: str
    cls: type[BaseController]