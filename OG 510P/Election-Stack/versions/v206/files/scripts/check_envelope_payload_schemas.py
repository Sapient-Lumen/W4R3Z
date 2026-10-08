#!/usr/bin/env python3
"""Drift firewall: envelope payload schemas must follow strict conventions.

Rationale:
EvidenceEnvelope.kind surfaces are curated (artifacts/registries/envelope-kinds.csv).
To keep verifier behavior predictable and reduce ambiguous parsing, every *envelope
payload schema* referenced by that registry MUST:

- be valid JSON
- declare $schema and $id
- use type=object and additionalProperties=false
- ensure required[] keys exist in properties{}

This check is intentionally narrow (only schemas referenced by envelope-kinds.csv),
so it does not impose repo-wide schema policy.
"""

from __future__ import annotations

from pathlib import Path
import csv
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"

ID_RE = re.compile(r"^https?://.+/.+\.json$")

def load_registry_schema_paths() -> list[Path]:
    if not REGISTRY.exists():
        raise SystemExit(f"Missing registry: {REGISTRY}")
    schemas: list[Path] = []
    with REGISTRY.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = (row.get("payload_schema") or "").strip()
            if not rel:
                raise SystemExit("Empty payload_schema in envelope-kinds.csv")
            schemas.append(ROOT / rel)
    return schemas

def main() -> int:
    errors: list[str] = []
    for p in load_registry_schema_paths():
        rel = p.relative_to(ROOT)
        if not p.exists():
            errors.append(f"Missing schema referenced by registry: {rel}")
            continue
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Invalid JSON in schema {rel}: {e}")
            continue

        if not isinstance(obj, dict):
            errors.append(f"Schema {rel} must be a JSON object")
            continue

        if obj.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"Schema {rel} must set $schema to draft 2020-12")
        sid = obj.get("$id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"Schema {rel} must declare non-empty $id")
        elif not ID_RE.match(sid):
            errors.append(f"Schema {rel} has suspicious $id (expected URL ending in .json): {sid}")
        else:
            if not sid.endswith("/" + p.name) and not sid.endswith(p.name):
                errors.append(f"Schema {rel} $id must end with {p.name}: {sid}")

        if obj.get("type") != "object":
            errors.append(f"Schema {rel} must have type=object")
        if obj.get("additionalProperties") is not False:
            errors.append(f"Schema {rel} must set additionalProperties=false")

        props = obj.get("properties")
        if not isinstance(props, dict):
            errors.append(f"Schema {rel} must declare properties as an object")
            props = {}

        required = obj.get("required", [])
        if required is None:
            required = []
        if not isinstance(required, list) or any(not isinstance(x, str) for x in required):
            errors.append(f"Schema {rel} required must be an array of strings")
            required = []
        for k in required:
            if k not in props:
                errors.append(f"Schema {rel} required key missing from properties: {k}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
