#!/usr/bin/env python3
"""Validate the schema catalog itself before trusting schema validation.

Surface schema validation proves that selected JSON instances match selected
schemas.  This checker proves the shipped schemas are valid Draft 2020-12 schema
documents and that schemas referenced by check_surface_schemas.py exist.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
from typing import Any

from jsonschema import Draft202012Validator

EXPECTED_META_SCHEMA = "https://json-schema.org/draft/2020-12/schema"
GENERIC_REPORT_SCHEMA = "schemas/generic_report.schema.json"


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def import_surface_schema_module(root: pathlib.Path):
    path = root / "publishing" / "check_surface_schemas.py"
    spec = importlib.util.spec_from_file_location("check_surface_schemas_for_schema_catalog", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot import check_surface_schemas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    schema_rows: list[dict[str, Any]] = []

    module = import_surface_schema_module(root)
    target_pairs = list(module.schema_targets(root))
    referenced_schemas = sorted({schema for _, schema in target_pairs})

    for schema_rel in sorted(p.relative_to(root).as_posix() for p in (root / "schemas").glob("*.schema.json")):
        path = root / schema_rel
        row: dict[str, Any] = {"schema": schema_rel, "status": "pass"}
        try:
            schema = load_json(path)
            if schema.get("$schema") != EXPECTED_META_SCHEMA:
                row.setdefault("failures", []).append({"category": "unexpected_meta_schema", "value": schema.get("$schema")})
            if not isinstance(schema.get("type"), str):
                row.setdefault("failures", []).append({"category": "missing_or_non_string_type"})
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - fail-closed diagnostics
            row.setdefault("failures", []).append({"category": "schema_document_invalid", "detail": str(exc)})
        if row.get("failures"):
            row["status"] = "fail"
            failures.append(row)
        schema_rows.append(row)

    missing_referenced = sorted(schema for schema in referenced_schemas if not (root / schema).exists())
    for schema in missing_referenced:
        failures.append({"schema": schema, "status": "fail", "failures": [{"category": "referenced_schema_missing"}]})

    schema_paths = sorted(row["schema"] for row in schema_rows)
    unreferenced_schema_paths = sorted(set(schema_paths) - set(referenced_schemas))
    summary = {
        "checks_failed": len(failures),
        "schema_document_count": len(schema_rows),
        "referenced_schema_count": len(referenced_schemas),
        "missing_referenced_schema_count": len(missing_referenced),
        "unreferenced_schema_count": len(unreferenced_schema_paths),
        "target_binding_count": len(target_pairs),
        "expected_meta_schema": EXPECTED_META_SCHEMA,
        "generic_report_schema_present": (root / GENERIC_REPORT_SCHEMA).exists(),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "schema_directory": "schemas",
        "schema_target_source": "publishing/check_surface_schemas.py",
        "schema_rows": schema_rows,
        "referenced_schemas": referenced_schemas,
        "unreferenced_schema_paths": unreferenced_schema_paths,
        "failures": failures[:100],
        "summary": summary,
        "fail_closed_rule": "If any schema document is invalid or a schema validation target references a missing schema, default to no publication and repair the schema catalog before trusting schema reports.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
