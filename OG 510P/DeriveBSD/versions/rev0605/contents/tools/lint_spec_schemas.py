#!/usr/bin/env python3
"""Lint spec JSON schemas for common DeriveBSD conventions.

This tool is intentionally lightweight and conservative.

Checks:
  - JSON parses with duplicate-key rejection
  - each schema has $schema and title
  - for *.plan/*.receipt/*.event schemas:
      - a "root" object shape exists that requires `kind` and a version field
      - root `kind` is a single discriminator value (const or single-value enum)

Notes:
  - We only enforce `kind`-singleton on plan/receipt/event schemas because the
    archive also contains helper/base schemas where `kind` is intentionally open.

Usage:
  python3 tools/lint_spec_schemas.py

Exit codes:
  0: ok
  1: violations found
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from cube_digest_lib import load_json_strict_text

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"


def _walk(node: Any) -> Iterable[dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def _is_singleton_kind(kind_schema: Any) -> bool:
    if not isinstance(kind_schema, dict):
        return False
    if "const" in kind_schema and isinstance(kind_schema["const"], str):
        return True
    if "enum" in kind_schema and isinstance(kind_schema["enum"], list):
        vals = kind_schema["enum"]
        return len(vals) == 1 and isinstance(vals[0], str)
    return False


def _object_shapes(schema: dict[str, Any]) -> list[dict[str, Any]]:
    shapes: list[dict[str, Any]] = []
    for n in _walk(schema):
        if not isinstance(n, dict):
            continue
        props = n.get("properties")
        req = n.get("required")
        if isinstance(props, dict) and isinstance(req, list):
            shapes.append(n)
    return shapes


def _find_root_shape(shapes: list[dict[str, Any]], version_keys: set[str]) -> list[dict[str, Any]]:
    """Return object subschemas that look like artifact roots."""
    roots: list[dict[str, Any]] = []
    for s in shapes:
        req = s.get("required")
        if not isinstance(req, list):
            continue
        reqs = set(req)
        if "kind" not in reqs:
            continue
        if not (reqs & version_keys):
            continue
        roots.append(s)
    return roots


def main() -> int:
    issues: list[str] = []

    for p in sorted(SPEC.glob("*.schema.json")):
        try:
            schema = load_json_strict_text(p.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append(f"{p.name}: invalid JSON ({e})")
            continue

        if not isinstance(schema, dict):
            issues.append(f"{p.name}: schema root is not an object")
            continue

        if "$schema" not in schema:
            issues.append(f"{p.name}: missing $schema")
        if "title" not in schema:
            issues.append(f"{p.name}: missing title")

        # Only enforce root-kind conventions for plan/receipt/event schemas.
        if p.name.endswith((".plan.schema.json", ".receipt.schema.json", ".event.schema.json")):
            shapes = _object_shapes(schema)

            if p.name.endswith(".plan.schema.json"):
                roots = _find_root_shape(shapes, {"plan_version", "schema_version"})
            elif p.name.endswith(".receipt.schema.json"):
                roots = _find_root_shape(shapes, {"receipt_version", "schema_version"})
            else:  # event
                roots = _find_root_shape(shapes, {"event_version", "schema_version"})

            if not roots:
                issues.append(f"{p.name}: could not find a root object schema requiring kind + a version field")
                continue

            ok = False
            for r in roots:
                props = r.get("properties")
                if not isinstance(props, dict) or "kind" not in props:
                    continue
                if _is_singleton_kind(props["kind"]):
                    ok = True
                    break

            if not ok:
                issues.append(f"{p.name}: root kind is not a singleton const/enum")

    if issues:
        print("Spec schema lint failed:")
        for line in sorted(set(issues)):
            print("-", line)
        return 1

    print("Spec schema lint OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
