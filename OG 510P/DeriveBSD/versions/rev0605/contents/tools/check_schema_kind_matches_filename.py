#!/usr/bin/env python3
"""Check that dotted-kind artifacts keep a stable filename ↔ kind mapping.

Rationale:
- Many DeriveBSD review surfaces key on `kind` names (plan/receipt/diff/etc).
- The archive stores schemas by filename (spec/<kind>.schema.json).
- A mismatch silently creates drift: docs and tooling may refer to one name,
  while the schema declares another.

This check is intentionally conservative:
- It only enforces alignment when the schema root:
    - is an object,
    - requires `kind`, and
    - declares `properties.kind` as a singleton const/enum,
  AND the declared kind contains a dot ('.').

We do NOT try to rename older dashed kinds (e.g. 'platform-report'); those
are legacy surfaces and are left as-is.

Usage:
  python3 tools/check_schema_kind_matches_filename.py

Exit codes:
  0: OK
  1: at least one schema violates the dotted-kind alignment rule

JSON is loaded with duplicate-key rejection so a schema cannot hide a later
properties.kind value behind a duplicate member.
"""

from __future__ import annotations

from pathlib import Path

from cube_digest_lib import load_json_strict_text

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"


def _singleton_kind(kind_schema: object) -> str | None:
    if not isinstance(kind_schema, dict):
        return None
    v = kind_schema.get("const")
    if isinstance(v, str) and v.strip():
        return v.strip()
    enum = kind_schema.get("enum")
    if isinstance(enum, list) and len(enum) == 1 and isinstance(enum[0], str) and enum[0].strip():
        return enum[0].strip()
    return None


def _root_kind(schema: object) -> str | None:
    if not isinstance(schema, dict):
        return None
    if schema.get("type") != "object":
        return None
    req = schema.get("required")
    if not isinstance(req, list) or "kind" not in req:
        return None
    props = schema.get("properties")
    if not isinstance(props, dict) or "kind" not in props:
        return None
    return _singleton_kind(props["kind"])


def main() -> int:
    problems: list[str] = []

    for p in sorted(SPEC.glob("*.schema.json")):
        try:
            schema = load_json_strict_text(p.read_text(encoding="utf-8"))
        except Exception as e:
            problems.append(f"{p.name}: invalid JSON ({e})")
            continue

        k = _root_kind(schema)
        if not k:
            continue

        # Only enforce for dotted kinds (newer naming discipline).
        if "." not in k:
            continue

        expected = p.name[: -len(".schema.json")]
        if expected != k:
            problems.append(f"{p.name}: kind '{k}' does not match filename base '{expected}'")

    if problems:
        print("Schema kind ↔ filename check FAILED:\n")
        for pr in problems:
            print(f"- {pr}")
        print("\nFix by renaming the schema file OR correcting the root properties.kind const/enum.")
        return 1

    print("Schema kind ↔ filename check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
