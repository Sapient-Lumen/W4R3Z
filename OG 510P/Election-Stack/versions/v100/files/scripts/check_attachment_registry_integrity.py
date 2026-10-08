#!/usr/bin/env python3
"""scripts/check_attachment_registry_integrity.py

Drift firewall for artifacts/registries/envelope-attachment-requirements.csv.

Checks:
- Each row's `kind` exists in artifacts/registries/envelope-kinds.csv.
- attachment_schema exists and lives under schemas/.
- required is yes/no.
- No duplicate (kind, rel) rows.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQS = ROOT / "artifacts" / "registries" / "envelope-attachment-requirements.csv"
KINDS = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
SCHEMAS = ROOT / "schemas"


def load_kinds() -> set[str]:
    if not KINDS.exists():
        raise SystemExit(f"Missing envelope kinds registry: {KINDS}")
    with KINDS.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required = {"kind", "track", "payload_schema", "stability", "description"}
        if set(r.fieldnames or []) != required:
            raise SystemExit(f"envelope-kinds.csv columns must be exactly {sorted(required)}; got {r.fieldnames}")
        out = set()
        for row in r:
            k = (row.get("kind") or "").strip()
            if not k:
                raise SystemExit("Empty kind in envelope-kinds.csv")
            out.add(k)
        return out


def main() -> int:
    if not REQS.exists():
        print(f"ERROR: missing requirements registry: {REQS}", file=sys.stderr)
        return 2

    kinds = load_kinds()
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    with REQS.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required_cols = {"kind", "rel", "required", "media_type", "attachment_schema", "description"}
        if set(r.fieldnames or []) != required_cols:
            print(
                f"ERROR: envelope-attachment-requirements.csv columns must be exactly {sorted(required_cols)}; got {r.fieldnames}",
                file=sys.stderr,
            )
            return 2

        for i, row in enumerate(r, start=2):  # header is line 1
            kind = (row.get("kind") or "").strip()
            rel = (row.get("rel") or "").strip()
            req = (row.get("required") or "").strip().lower()
            mt = (row.get("media_type") or "").strip()
            schema_rel = (row.get("attachment_schema") or "").strip()

            if not kind or not rel:
                errors.append(f"line {i}: kind and rel must be non-empty")
                continue

            if kind not in kinds:
                errors.append(f"line {i}: unknown kind in attachment requirements: {kind}")

            if req not in {"yes", "no"}:
                errors.append(f"line {i}: required must be yes/no (got {row.get('required')})")

            if not mt:
                errors.append(f"line {i}: media_type must be non-empty for {kind}:{rel}")

            if not schema_rel:
                errors.append(f"line {i}: attachment_schema must be non-empty for {kind}:{rel}")
            else:
                schema_path = ROOT / schema_rel
                if not schema_path.exists():
                    errors.append(f"line {i}: attachment_schema missing: {schema_rel}")
                else:
                    if not str(schema_path.resolve()).startswith(str(SCHEMAS.resolve())):
                        errors.append(f"line {i}: attachment_schema must live under schemas/: {schema_rel}")

            key = (kind, rel)
            if key in seen:
                errors.append(f"line {i}: duplicate (kind, rel) row: {kind}, {rel}")
            seen.add(key)

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
