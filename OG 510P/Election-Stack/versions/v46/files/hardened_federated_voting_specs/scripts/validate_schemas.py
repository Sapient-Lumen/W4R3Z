#!/usr/bin/env python3
"""Template schema validator.

This repo includes JSON Schemas under `schemas/`. In a full implementation,
this script should:

- load all schemas
- validate that each schema is itself valid JSON Schema (meta-schema)
- optionally run example objects through their schemas

Kept as a template because schema-validation libraries/pinning is a policy choice.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def main() -> None:
    for p in sorted(SCHEMAS.glob("*.json")):
        json.loads(p.read_text())
    print(f"Loaded {len(list(SCHEMAS.glob('*.json')))} schemas OK.")


if __name__ == "__main__":
    main()
