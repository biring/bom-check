"""
Build automation utilities for producing a standalone executable.

This module orchestrates cleanup of previous build artifacts, execution of a packaging process to generate a single-file executable, and post-build cleanup to remove intermediate files while preserving the final distributable.

Key Responsibilities:
	- Remove pre-existing build directories and specification files to ensure clean builds
	- Handle read-only filesystem artifacts during recursive deletion
	- Invoke an external packaging tool to generate a standalone executable
	- Report build progress and final artifact location
	- Perform post-build cleanup of temporary artifacts while preserving output

Expected Project Layout:
    bom-check/
    ├── scripts/
    │   └── build_exe.py    ← this file
    ├── src/
    │   └── main.py
    ├── build/              (created by PyInstaller, cleaned by this script)
    ├── dist/
    └── bom-check.spec      (created by PyInstaller, cleaned by this script)

Example Usage:
	from scripts import build_exe
	build_exe.main()

Dependencies:
	- Python version: >= 3.8
	- Standard Library: os, shutil, stat, subprocess, sys, pathlib

Notes:
	- Designed for repeatable execution with idempotent cleanup behavior
	- Assumes a fixed project layout with source and build directories
	- Relies on an external packaging tool being available in the runtime environment
	- Emits console output for traceability rather than structured logging

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only module; explicitly exports nothing to prevent accidental public use.

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

# This script lives in <project_root>/scripts/, so go one level up.
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

CLEAN_FOLDERS = [
    PROJECT_ROOT / "build",
    PROJECT_ROOT / "dist",
]

CLEAN_FILES = [
    PROJECT_ROOT / "bom-check.spec",
]

PYINSTALLER_ARGS = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--name", "bom-check",
    "--paths", str(PROJECT_ROOT / "src"),
    str(PROJECT_ROOT / "src" / "main.py"),
]


def _clear_read_only_flag(retry_func, target_path: str, _exception_info: tuple) -> None:
    """
    Clear the read-only flag on a filesystem path and retry a failed operation.

    This function is designed to be used as an error handler for shutil.rmtree.
    It assumes the failure was caused by insufficient write permissions (commonly
    seen on Windows or synced directories like OneDrive). It modifies the file
    mode to writable and retries the original operation.

    Args:
        retry_func (Callable): The function that raised the exception (e.g., os.remove or os.rmdir).
        target_path (str): The path to the file or directory that caused the failure.
        _exception_info (tuple): Exception information provided by shutil.rmtree; unused.

    Returns:
        None

    Raises:
        RuntimeError: If the permission fix or retry operation fails.
    """
    try:
        # Force the target path to be writable to recover from permission-related deletion failures
        os.chmod(target_path, stat.S_IWRITE)

        # Retry the original failing operation after adjusting permissions
        retry_func(target_path)
    except Exception as exc:
        # Wrap any failure to ensure consistent error propagation and context visibility
        raise RuntimeError(
            f"Failed to clear read-only flag for path: {target_path}. "
            f"\n{exc}"
        ) from exc


def _remove_folder_if_exists(folder_path: Path) -> None:
    """
    Remove a folder tree if it exists and is a directory.

    This function ensures cleanup remains idempotent by skipping paths that do not exist
    or are not directories. It uses a custom error handler to recover from read-only
    permission issues during recursive deletion.

    Args:
        folder_path (Path): Folder path to remove.

    Returns:
        None

    Raises:
        RuntimeError: If directory removal fails after retry handling.
    """
    try:
        # Only proceed if the path exists and is explicitly a directory
        # This prevents accidental deletion attempts on files or invalid paths
        if folder_path.exists() and folder_path.is_dir():
            # Use a custom error handler to recover from permission-related failures
            shutil.rmtree(folder_path, onerror=_clear_read_only_flag)

            # Emit confirmation for visibility in build logs
            print(f"  Removed directory: {folder_path}")
        else:
            # Treat missing or non-directory paths as safe no-ops for repeatable execution
            print(f"  Skipped (not found): {folder_path}")
    except Exception as exc:
        # Normalize all failures into a consistent RuntimeError for upstream handling
        raise RuntimeError(
            f"Failed to remove folder: {folder_path}."
            f"\n{exc}"
        ) from exc


def _remove_file_if_exists(file_path: Path) -> None:
    """
    Remove a file if it exists and is a regular file.

    This function ensures safe repeated execution by skipping paths that do not exist
    or are not files. It performs direct deletion without retry logic.

    Args:
        file_path (Path): File path to remove.

    Returns:
        None

    Raises:
        RuntimeError: If file deletion fails.
    """
    try:
        # Only proceed if the path exists and is explicitly a file
        # This prevents incorrect deletion attempts on directories or invalid paths
        if file_path.exists() and file_path.is_file():
            # Directly delete the file since no custom retry behavior is implemented
            file_path.unlink()

            # Emit confirmation for visibility in build logs
            print(f"  Removed file:      {file_path}")
        else:
            # Treat missing or non-file paths as safe no-ops for repeatable execution
            print(f"  Skipped (not found): {file_path}")
    except Exception as exc:
        # Normalize failure into a consistent RuntimeError for upstream handling
        raise RuntimeError(
            f"Failed to remove file: {file_path}."
            f"\n{exc}"
        ) from exc


def _clean_build_artifacts() -> None:
    """
    Remove configured build folders and files before a build.

    This function iterates over predefined global cleanup targets and delegates
    deletion to helper functions. Missing artifacts are intentionally skipped
    to ensure idempotent cleanup behavior.

    Returns:
        None

    Raises:
        RuntimeError: If any cleanup step fails.
    """
    try:
        # Remove directories first because they contain the bulk of generated artifacts
        for folder_path in CLEAN_FOLDERS:
            _remove_folder_if_exists(folder_path)

        # Remove standalone files after directories to complete artifact cleanup
        for file_path in CLEAN_FILES:
            _remove_file_if_exists(file_path)
    except Exception as exc:
        # Wrap failures to provide consistent context at the workflow level
        raise RuntimeError(
            f"Failed while cleaning build artifacts. "
            f"\n{exc}"
        ) from exc


def _build() -> None:
    """
    Run PyInstaller to generate the bom-check executable.

    Executes the configured PyInstaller command from the project root directory.
    If PyInstaller exits with a non-zero status, the process terminates immediately.
    On success, the function resolves and reports the generated executable path.

    Returns:
        None

    Raises:
        SystemExit: If PyInstaller returns a non-zero exit code.
        RuntimeError: If subprocess execution or path resolution fails.
    """
    return_code = 0
    try:
        # Print the exact command for reproducibility and debugging
        print(f"  Running: {' '.join(PYINSTALLER_ARGS)}\n")

        # Execute PyInstaller from the project root to ensure correct path resolution
        result = subprocess.run(PYINSTALLER_ARGS, cwd=PROJECT_ROOT)

        # Immediately exit if PyInstaller fails to avoid masking errors
        if result.returncode != 0:
            return_code = result.returncode
            print("\n[ERROR] PyInstaller failed with exit code", result.returncode)
            sys.exit(result.returncode)

        # Define expected output paths for cross-platform compatibility
        exe_path = PROJECT_ROOT / "dist" / "bom-check"
        exe_win = PROJECT_ROOT / "dist" / "bom-check.exe"

        # Prefer Windows executable if present; fallback to extensionless binary otherwise
        final_executable_path = exe_win if exe_win.exists() else exe_path

        # Report successful build output location
        print(f"\n[OK] Executable ready: {final_executable_path}")
    except Exception as exc:
        # Wrap unexpected failures with preserved return code context
        raise RuntimeError(
            f"PyInstaller failed with exit code {return_code}. "
            f"\n{exc}"
        ) from exc


def _post_build_clean() -> None:
    """
    Remove intermediate PyInstaller artifacts after a successful build.

    This function deletes temporary build directories and generated spec files
    while preserving the final distributable located in the dist directory.

    Returns:
        None

    Raises:
        RuntimeError: If cleanup fails.
    """
    try:
        # Remove temporary build directory since it is not needed after successful build
        _remove_folder_if_exists(PROJECT_ROOT / "build")

        # Remove generated spec file to avoid committing transient artifacts
        _remove_file_if_exists(PROJECT_ROOT / "bom-check.spec")
    except Exception as exc:
        # Normalize cleanup failure into a consistent RuntimeError
        raise RuntimeError(
            f"Failed during post-build cleanup"
            f"\n{exc}"
        ) from exc


def main() -> None:
    """
    Execute the full build workflow.

    This function orchestrates pre-build cleanup, execution of the build process,
    and post-build cleanup. If the build step fails, the process exits and
    post-build cleanup is not executed.

    Returns:
        None

    Raises:
        RuntimeError: If any stage of the workflow fails unexpectedly.
    """
    print("\n=== Build Executable Script ========================================")
    try:
        # Perform pre-build cleanup to ensure no stale artifacts influence the build
        print("\n--- Pre Build Clean ----------------------------------------------")
        _clean_build_artifacts()

        # Execute the build step; this will terminate the process on failure
        print("\n--- Build --------------------------------------------------------")
        _build()

        # Perform post-build cleanup only if build succeeded
        print("\n--- Post Build Clean ---------------------------------------------")
        _post_build_clean()

        # Indicate successful completion of the workflow
        print("\n=== Done =========================================================")
    except Exception as exc:
        # Wrap any unexpected failure in a RuntimeError for consistent error reporting
        raise RuntimeError(
            f"Build workflow failed"
            f"\n{exc}"
        ) from exc


if __name__ == "__main__":
    main()
