#!/usr/bin/env python3
"""Validate packaged JSON instances against registered JSON Schemas.

This script is intentionally separate from the large archive linter: the linter
checks archive-specific invariants, while this script checks the advertised JSON
Schema contracts that external readers are likely to trust.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from pathlib import Path
import json

try:
    import jsonschema
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "jsonschema is required for schema-instance validation; "
        "install the 'jsonschema' Python package or run inside the project cloudtainer."
    ) from exc

ROOT = Path(__file__).resolve().parents[1]

STANDALONE_SCHEMA_PAIRS = [
    ("AUTHORITY-DEPENDENCY-GRAPH.json", "schemas/authority-dependency-graph.schema.json"),
    ("LEDGER-FAMILY-REGISTRY.json", "schemas/ledger-family-registry.schema.json"),
    ("DECISION-EXPERIMENT-LEDGER.json", "schemas/decision-experiment-ledger.schema.json"),
    ("DISCRIMINATOR-FORECAST-LEDGER.json", "schemas/discriminator-forecast-ledger.schema.json"),
    ("OBSERVED-SECTOR-RECOVERY-LEDGER.json", "schemas/observed-sector-recovery-ledger.schema.json"),
    ("PROMOTION-GATE-LEDGER.json", "schemas/promotion-gate-ledger.schema.json"),
]


def load_json(rel: str) -> object:
    return json.loads((ROOT / rel).read_text())


def iter_schema_pairs() -> list[tuple[str, str, str]]:
    registry = load_json("LEDGER-FAMILY-REGISTRY.json")
    pairs: list[tuple[str, str, str]] = []
    for row in registry.get("registry_rows", []):
        family_id = row.get("family_id", "<missing-family>")
        ledger_files = row.get("ledger_files", [])
        schema_files = row.get("schema_files", [])
        if len(ledger_files) != len(schema_files):
            pairs.append(("<registry-length-mismatch>", "<registry-length-mismatch>", family_id))
            continue
        for ledger_file, schema_file in zip(ledger_files, schema_files):
            pairs.append((ledger_file, schema_file, family_id))
    for ledger_file, schema_file in STANDALONE_SCHEMA_PAIRS:
        pairs.append((ledger_file, schema_file, "standalone-schema-contract"))
    return pairs


def validate_pair(ledger_file: str, schema_file: str, family_id: str) -> list[str]:
    if ledger_file.startswith("<"):
        return [f"{family_id}: ledger_files/schema_files length mismatch in registry row"]
    errors: list[str] = []
    ledger_path = ROOT / ledger_file
    schema_path = ROOT / schema_file
    if not ledger_path.exists():
        return [f"{family_id}: missing ledger instance {ledger_file}"]
    if not schema_path.exists():
        return [f"{family_id}: missing schema {schema_file}"]
    instance = load_json(ledger_file)
    schema = load_json(schema_file)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        path = "/".join(str(part) for part in err.path) or "<root>"
        schema_path_text = "/".join(str(part) for part in err.schema_path) or "<schema-root>"
        errors.append(f"{ledger_file} @ {path}: {err.message} [schema {schema_path_text}]")
    return errors


def main() -> int:
    errors: list[str] = []
    for ledger_file, schema_file, family_id in iter_schema_pairs():
        errors.extend(validate_pair(ledger_file, schema_file, family_id))
    if errors:
        print("SCHEMA VALIDATION FAILED")
        for item in errors[:200]:
            print(f"- {item}")
        if len(errors) > 200:
            print(f"- ... {len(errors) - 200} more errors omitted")
        return 1
    print("SCHEMA VALIDATION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
