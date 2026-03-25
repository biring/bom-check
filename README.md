# BOM Check Project

## Overview

This project processes and validates BOM (Bill of Materials) data using Python.
It includes parsing, transformation, and validation utilities with a comprehensive test suite.

## Prerequisites

* **Python**: 3.12.x
* **pip**: Latest version recommended
* **Git**: Installed and available in PATH

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

## Project Structure (Simplified)

```
docs/       # Design documentation
scripts/    # Build and automation scripts
src/        # Application source code
tests/      # Unit and integration tests
tools/      # Runtime artifact utilities
```

## Notes

- Requires pandas==2.2.0 (3.x is not compatible)