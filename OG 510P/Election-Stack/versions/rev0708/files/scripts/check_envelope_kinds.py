#!/usr/bin/env python3
"""Check EvidenceEnvelope.kind values against the registry.

- Registry: artifacts/registries/envelope-kinds.csv
- Applies to example packets and example envelopes under artifacts/examples/

This is a drift firewall: it keeps the verifier surface small and prevents
near-duplicate kind strings from accumulating over time.
"""

from __future__ import annotations

from pathlib import Path
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
SCHEMAS_DIR = ROOT / "schemas"
EXAMPLES_DIR = ROOT / "artifacts" / "examples"

def load_registry() -> dict[str, dict[str, str]]:
    if not REGISTRY.exists():
        raise SystemExit(f"Missing registry: {REGISTRY}")
    kinds: dict[str, dict[str, str]] = {}
    with REGISTRY.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"kind", "track", "payload_schema", "stability", "description"}
        if set(reader.fieldnames or []) != required:
            raise SystemExit(f"Registry columns must be exactly {sorted(required)}; got {reader.fieldnames}")
        for row in reader:
            k = row["kind"].strip()
            if not k:
                raise SystemExit("Empty kind in registry")
            if k in kinds:
                raise SystemExit(f"Duplicate kind in registry: {k}")
            kinds[k] = row
    return kinds

def is_envelope(obj: object) -> bool:
    return (
        isinstance(obj, dict)
        and "envelope_version" in obj
        and "kind" in obj
        and "payload_schema" in obj
        and "payload_digest" in obj
    )

def iter_json_files(root: Path):
    for p in root.rglob("*.json"):
        # Skip extremely large or clearly non-example artifacts if needed in the future.
        yield p

def main() -> int:
    kinds = load_registry()

    errors: list[str] = []

    # Validate schema paths exist
    for k, row in kinds.items():
        schema_rel = row["payload_schema"].strip()
        schema_path = ROOT / schema_rel
        if not schema_path.exists():
            errors.append(f"Registry kind {k} references missing schema: {schema_rel}")
        else:
            # sanity: schema should be under schemas/
            if not str(schema_path).startswith(str(SCHEMAS_DIR)):
                errors.append(f"Registry kind {k} payload_schema must live under schemas/: {schema_rel}")

    # Scan example JSONs for envelopes
    for p in iter_json_files(EXAMPLES_DIR):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Failed to parse JSON: {p.relative_to(ROOT)} ({e})")
            continue

        if not is_envelope(obj):
            continue

        kind = str(obj.get("kind", "")).strip()
        ps = str(obj.get("payload_schema", "")).strip()

        if kind not in kinds:
            errors.append(f"Unregistered envelope kind in {p.relative_to(ROOT)}: {kind}")
            continue

        expected = kinds[kind]["payload_schema"].strip()
        if ps and ps != expected:
            errors.append(
                f"Envelope payload_schema mismatch in {p.relative_to(ROOT)}: kind={kind} payload_schema={ps} expected={expected}"
            )

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
