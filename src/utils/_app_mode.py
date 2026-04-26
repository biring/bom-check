"""
Application runtime mode detection and classification utilities.

This module determines the current execution context of an application and exposes a stable, enumerated representation of that context for downstream configuration and behavior control.

Key Responsibilities:
	- Define supported runtime modes for application execution contexts
	- Detect execution within packaged binary environments
	- Detect execution within unit testing frameworks
	- Infer execution from source when no other context applies
	- Resolve and expose a single authoritative runtime mode

Example Usage:
	# Preferred usage via public package interface:
	from src.utils import app_mode
	print(app_mode.APP_MODE)

	# Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils._app_mode as am
    if am.APP_MODE is am.AppMode.EXECUTABLE:
        print("Running as packaged binary")

Dependencies:
	- Python version: >= 3.8
	- Standard Library: os, sys, enum, typing

Notes:
	- Detection prioritizes packaged execution over test and development contexts
	- Test detection favors false positives to ensure test-safe behavior
	- Exactly one runtime mode is expected to be active at any given time
	- Module is intended for internal use and centralized environment awareness

License:
	- Internal Use Only
"""
# Public API
__all__ = ["AppMode", "APP_MODE"]  # Restricts exports to enum and constant only

import os
import sys

from enum import Enum, auto
from typing import Final


class AppMode(Enum):
    """
    Define the supported application runtime modes.

    This enumeration represents the distinct execution contexts in which the application may operate. It is used as a stable contract for downstream
    configuration and behavior branching.

    Invariants:
    - Each member is unique and auto-assigned.
    - Exactly one mode is intended to represent the runtime at any given time.

    Attributes:
        DEVELOPMENT (AppMode): Execution directly from source code.
        UNITTEST (AppMode): Execution within a unittest or pytest environment.
        EXECUTABLE (AppMode): Execution as a frozen binary (e.g., PyInstaller).
    """

    # Development mode represents standard execution from source
    DEVELOPMENT = auto()

    # Unit test mode indicates execution under unittest or pytest orchestration
    UNITTEST = auto()

    # Executable mode indicates a frozen/packaged binary runtime
    EXECUTABLE = auto()


def _is_running_as_executable() -> bool:
    """
    Determine whether the application is running as a frozen executable.

    This detects packaging environments such as PyInstaller or cx_Freeze, which inject a `frozen` attribute into the `sys` module at runtime.

    Returns:
        bool: True if running as a frozen executable, False otherwise.
    """
    # Access `sys.frozen` defensively since it is only injected in packaged runtimes.
    # getattr avoids AttributeError and defaults to False when not present.
    return bool(getattr(sys, "frozen", False))


def _is_running_a_unittest() -> bool:
    """
    Detect whether the application is executing within a unittest or pytest context.

    This function uses two independent detection strategies:
    1. Presence of the `PYTEST_CURRENT_TEST` environment variable, which pytest sets.
    2. Inspection of `sys.modules` for loaded unittest modules.

    The detection favors false positives over false negatives to ensure test-specific behavior is activated when there is ambiguity.

    Returns:
        bool: True if running under unittest or pytest, False otherwise.
    """
    # Pytest sets this environment variable during test execution.
    # This is the most reliable indicator for pytest-driven runs.
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True

    # Check if the unittest module is loaded in the current interpreter.
    # Presence alone is not sufficient, so we also verify submodules are loaded,
    # indicating an active test run rather than a passive import.
    if "unittest" in sys.modules:
        # Scan for any unittest submodule, which implies test execution is in progress.
        # This avoids false positives from simple imports of `unittest`.
        for module_name in sys.modules.keys():
            if module_name.startswith("unittest."):
                return True

    # If neither detection strategy succeeds, assume not running tests.
    return False


def _is_running_from_source() -> bool:
    """
    Determine whether the application is running directly from source code.

    This is inferred by the absence of the `sys.frozen` attribute, which is typically injected by packaging tools in executable contexts.

    Returns:
        bool: True if running from source, False otherwise.
    """
    # If `sys.frozen` is not present, the application is assumed to be running
    # from a standard Python interpreter (i.e., not packaged).
    return not hasattr(sys, "frozen")


def _determine_app_mode() -> AppMode:
    """
    Resolve the current application runtime mode based on environment detection.

    Detection follows a strict priority order to avoid ambiguity:
    1. EXECUTABLE: Highest priority to ensure packaged environments are correctly identified.
    2. UNITTEST: Takes precedence over development to enable test-specific behavior.
    3. DEVELOPMENT: Default fallback when no other conditions are met.

    Returns:
        AppMode: The resolved application mode.

    Raises:
        RuntimeError: If no valid runtime mode can be determined due to inconsistent environment state.
    """
    # Priority 1: Detect packaged executable environments first.
    # This must take precedence because frozen apps may still load test modules.
    if _is_running_as_executable():
        return AppMode.EXECUTABLE

    # Priority 2: Detect test environments next.
    # Tests should override development behavior to ensure correct configuration.
    if _is_running_a_unittest():
        return AppMode.UNITTEST

    # Priority 3: Default to development when not frozen.
    # This assumes standard interpreter execution.
    if _is_running_from_source():
        return AppMode.DEVELOPMENT

    # Defensive fallback: reaching this point implies conflicting or unexpected signals.
    # This enforces the invariant that exactly one mode must be determinable.
    raise RuntimeError("Unable to determine application mode.")


# Module-level constant
APP_MODE: Final[AppMode] = _determine_app_mode()
