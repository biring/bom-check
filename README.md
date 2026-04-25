# BOM Check Project

## Overview

This project processes and validates BOM (Bill of Materials) data using Python.
It includes parsing, transformation, and validation utilities with a comprehensive test suite.

## Prerequisites

* **Python**: 3.12.x
* **pip**: Latest version recommended
* **Git**: Installed and available in PATH
* **PyInstaller**: Required to build the standalone executable (`pip install pyinstaller`)

## Setup 

```
git clone <repo-url>
cd bom-check
python -m pip install -r requirements.txt
```

## Running Tests

Run the full test suite:

```
python -m unittest discover -s tests
```

## Building the Executable

The `scripts/build_exe.py` script produces a standalone single-file executable using PyInstaller.

### Usage

Run from the project root:

```
python scripts/build_exe.py
```

### What It Does

The build script runs three stages automatically:

1. **Pre-build clean** — Removes any existing `build/`, `dist/`, and `bom-check.spec` artifacts to ensure a fresh build.
2. **Build** — Invokes PyInstaller with `--onefile` to bundle `src/main.py` and its dependencies into a single executable.
3. **Post-build clean** — Removes the intermediate `build/` directory and `.spec` file, leaving only the final distributable in `dist/`.

### Output

On success, the executable is written to:

```
dist/bom-check.exe
```

### Notes

- The script is idempotent — it can be run multiple times safely; missing artifacts are skipped without error.
- If PyInstaller fails, the process exits immediately and post-build cleanup is skipped.
- Read-only filesystem artifacts (e.g. from OneDrive-synced folders) are handled automatically during cleanup.

## Project Structure (Simplified)

```
dist/       # Build output (contains the generated bom-check.exe)
docs/       # Design documentation
scripts/    # Build and automation scripts
src/        # Application source code
tests/      # Unit and integration tests
tools/      # Runtime artifact utilities
```

## Notes

- Requires pandas==2.2.0 (3.x is not compatible)