#!/usr/bin/env python3
"""Validate spec/examples/*.json against spec/*schema.json.

This is a lightweight hygiene check to prevent schema/example drift.

Rules:
  - For each schema named: spec/<name>.schema.json
    validate spec/examples/<name>.json if present.
  - Additional examples may use dotted suffixes like spec/examples/<name>.<variant>.json
    and still validate against spec/<name>.schema.json.
  - Also warn if an example exists without a matching schema.

Exit codes:
  0: all validated examples pass
  1: validation failures
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except Exception as e:  # pragma: no cover
    raise SystemExit(f"Missing dependency: referencing (via jsonschema). Error: {e}")

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "spec"
EX_DIR = SPEC_DIR / "examples"

BASE_URI = "https://derivebsd.local/spec/"  # stable synthetic base for local $ref resolution


def _read_json(p: Path) -> object:
    return json.loads(p.read_text(encoding="utf-8"))


def build_registry(schema_paths: list[Path]) -> Registry:
    reg: Registry = Registry()
    for p in schema_paths:
        uri = BASE_URI + p.name
        schema = _read_json(p)
        # jsonschema's ref resolution behaves best when each schema has a stable $id.
        if isinstance(schema, dict) and "$id" not in schema:
            schema = dict(schema)
            schema["$id"] = uri
        reg = reg.with_resource(uri, Resource.from_contents(schema, default_specification=DRAFT202012))
    return reg


def main() -> int:
    schema_paths = sorted(SPEC_DIR.glob("*.schema.json"))
    if not schema_paths:
        print("No schemas found under spec/*.schema.json")
        return 0

    reg = build_registry(schema_paths)

    failures: list[str] = []

    schema_by_name = {p.name.removesuffix(".schema.json"): p for p in schema_paths}

    def _match_schema_name(example_stem: str) -> str | None:
        best: str | None = None
        for name in schema_by_name:
            if example_stem == name or example_stem.startswith(name + "."):
                if best is None or len(name) > len(best):
                    best = name
        return best

    # Validate each example that has a matching schema name (including dotted variants).
    validated = 0
    example_paths = sorted(EX_DIR.glob("*.json"))
    matched_examples: set[Path] = set()
    for ep in example_paths:
        stem = ep.name.removesuffix(".json")
        schema_name = _match_schema_name(stem)
        if schema_name is None:
            continue
        matched_examples.add(ep)
        sp = schema_by_name[schema_name]

        schema = _read_json(sp)
        if isinstance(schema, dict) and "$id" not in schema:
            schema = dict(schema)
            schema["$id"] = BASE_URI + sp.name
        instance = _read_json(ep)

        v = Draft202012Validator(schema, registry=reg)
        errs = sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path))
        if errs:
            failures.append(f"{ep.relative_to(ROOT)} failed against {sp.relative_to(ROOT)}")
            for e in errs[:25]:
                path = "/".join(str(x) for x in e.absolute_path) or "<root>"
                failures.append(f"  - {path}: {e.message}")
            if len(errs) > 25:
                failures.append(f"  - ... ({len(errs) - 25} more errors)")
        else:
            validated += 1

    # Warn about examples with no schema.
    warnings: list[str] = []
    for ep in example_paths:
        if ep not in matched_examples:
            stem = ep.name.removesuffix(".json")
            warnings.append(f"{ep.relative_to(ROOT)}: no matching schema named spec/{stem}.schema.json")

    if failures:
        print("Spec example validation failed:")
        for line in failures:
            print(line)
        if warnings:
            print("\nWarnings:")
            for w in warnings:
                print(w)
        print(f"Validated examples: {validated}")
        return 1

    if warnings:
        print("Spec example validation OK (with warnings):")
        for w in warnings:
            print(w)
        print(f"Validated examples: {validated}")
        return 0

    print(f"Spec example validation OK (validated {validated} examples)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
