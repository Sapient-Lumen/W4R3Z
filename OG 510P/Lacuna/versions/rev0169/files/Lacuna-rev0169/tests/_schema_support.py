from __future__ import annotations

import os
from typing import Any

Draft202012Validator: Any
ValidationError: Any

if os.environ.get("LACUNA_SCHEMA_TESTS") == "1":
    try:
        from jsonschema import Draft202012Validator, ValidationError
    except ImportError:  # Optional acceptance dependency; runtime remains stdlib-only.
        Draft202012Validator = None  # type: ignore[assignment]
        ValidationError = Exception  # type: ignore[assignment]
else:
    Draft202012Validator = None  # type: ignore[assignment]
    ValidationError = Exception  # type: ignore[assignment]
