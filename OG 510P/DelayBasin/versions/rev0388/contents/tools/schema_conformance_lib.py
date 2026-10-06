import json
import pathlib
from typing import Any

SCHEMA_SURFACES = {
    "schemas/revision-receipt.schema.json": "REVISION-RECEIPT.json",
    "schemas/surface-status.schema.json": "SURFACE-STATUS.json",
    "schemas/context-pack.schema.json": "context-pack.json",
    "schemas/frontier-ticket.schema.json": "frontier-ticket.json",
    "schemas/innovation-packet.schema.json": "innovation-packet.json",
    "schemas/reentry-contract.schema.json": "REENTRY-CONTRACT.json",
    "schemas/validation-index.schema.json": "VALIDATION-INDEX.json",
    "schemas/path-alias-ledger.schema.json": "PATH-ALIAS-LEDGER.json",
    "schemas/validation-toolchain-manifest.schema.json": "VALIDATION-TOOLCHAIN-MANIFEST.json",
    "schemas/currentness-cue-audit.schema.json": "CURRENTNESS-CUE-AUDIT.json",
    "schemas/package-identity-audit.schema.json": "PACKAGE-IDENTITY-AUDIT.json",
    "schemas/basis-provenance-audit.schema.json": "BASIS-PROVENANCE-AUDIT.json",
    "schemas/lint-idempotence-audit.schema.json": "LINT-IDEMPOTENCE-AUDIT.json",
    "schemas/schema-conformance-audit.schema.json": "SCHEMA-CONFORMANCE-AUDIT.json",
    "schemas/schema-coverage-audit.schema.json": "SCHEMA-COVERAGE-AUDIT.json",
}

JSON_TYPE_TO_PYTHON = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    py = JSON_TYPE_TO_PYTHON.get(expected)
    return py is not None and isinstance(value, py)


def _validate(schema: dict[str, Any], instance: Any, path: str, rows: list[dict[str, Any]]) -> None:
    if "const" in schema:
        expected = schema["const"]
        rows.append({
            "path": path,
            "constraint": "const",
            "expected": expected,
            "observed": instance,
            "status": "pass" if instance == expected else "fail",
        })
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        ok = any(_type_matches(instance, item) for item in expected_types)
        rows.append({
            "path": path,
            "constraint": "type",
            "expected": expected_types if len(expected_types) > 1 else expected_types[0],
            "observed": json_type(instance),
            "status": "pass" if ok else "fail",
        })
        if not ok:
            return
    if isinstance(instance, dict):
        required = schema.get("required", []) or []
        for key in required:
            rows.append({
                "path": f"{path}.{key}" if path != "$" else key,
                "constraint": "required",
                "expected": "present",
                "observed": "present" if key in instance else "missing",
                "status": "pass" if key in instance else "fail",
            })
        properties = schema.get("properties", {}) or {}
        for key, sub_schema in properties.items():
            if key not in instance:
                continue
            if not isinstance(sub_schema, dict):
                continue
            if not ({"type", "const", "required", "properties", "items"} & set(sub_schema)):
                rows.append({
                    "path": f"{path}.{key}" if path != "$" else key,
                    "constraint": "typed-public-property",
                    "expected": "type/const/required/properties/items",
                    "observed": "description-only",
                    "status": "fail",
                })
                continue
            _validate(sub_schema, instance[key], f"{path}.{key}" if path != "$" else key, rows)
    if isinstance(instance, list) and isinstance(schema.get("items"), dict):
        item_schema = schema["items"]
        for index, value in enumerate(instance[:25]):
            _validate(item_schema, value, f"{path}[{index}]", rows)


def validate_schema_surface(root: pathlib.Path, schema_rel: str, surface_rel: str) -> dict[str, Any]:
    schema_path = root / schema_rel
    surface_path = root / surface_rel
    row: dict[str, Any] = {
        "schema": schema_rel,
        "surface": surface_rel,
        "status": "pass",
        "checks": [],
        "failures": [],
    }
    if not schema_path.exists() or not surface_path.exists():
        row["status"] = "fail"
        row["failures"].append({"path": "$", "constraint": "exists", "expected": "schema and surface", "observed": "missing", "status": "fail"})
        return row
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        surface = json.loads(surface_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - lint target reports message
        row["status"] = "fail"
        row["failures"].append({"path": "$", "constraint": "parse", "expected": "valid JSON", "observed": str(exc), "status": "fail"})
        return row
    meta_checks = [
        {"path": "$schema", "constraint": "const", "expected": "https://json-schema.org/draft/2020-12/schema", "observed": schema.get("$schema"), "status": "pass" if schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema" else "fail"},
        {"path": "title", "constraint": "non-empty-string", "expected": "non-empty", "observed": json_type(schema.get("title")), "status": "pass" if isinstance(schema.get("title"), str) and schema.get("title") else "fail"},
        {"path": "type", "constraint": "const", "expected": "object", "observed": schema.get("type"), "status": "pass" if schema.get("type") == "object" else "fail"},
    ]
    rows: list[dict[str, Any]] = []
    _validate(schema, surface, "$", rows)
    checks = meta_checks + rows
    failures = [item for item in checks if item.get("status") != "pass"]
    row["checks"] = checks
    row["failures"] = failures
    row["status"] = "pass" if not failures else "fail"
    return row


def build_schema_conformance_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
    rows = [validate_schema_surface(root, schema_rel, surface_rel) for schema_rel, surface_rel in SCHEMA_SURFACES.items()]
    failures = []
    for row in rows:
        for failure in row.get("failures", []):
            enriched = dict(failure)
            enriched["schema"] = row["schema"]
            enriched["surface"] = row["surface"]
            failures.append(enriched)
    return {
        "project": "DelayBasin",
        "revision": receipt["revision"],
        "surface": "SCHEMA-CONFORMANCE-AUDIT.json",
        "guide_surface": "docs/00-meta/schema-conformance-audit.md",
        "state": "generated-schema-conformance-audit",
        "generated_from": sorted(SCHEMA_SURFACES.keys()) + sorted(SCHEMA_SURFACES.values()),
        "non_claim": "schema-conformance-court, type-sovereign, contract-adjudication-board, schema-waiver-senate, generated-audit-notary, public-shape-tribunal, validation-authority-court, and typed-surface-certifier are forbidden; this surface checks public JSON shape/type conformance but does not certify semantic truth, canon sufficiency, release legitimacy, legal status, minimality, or continuation authority.",
        "schema_surfaces": rows,
        "counts": {
            "schema_count": len(rows),
            "check_count": sum(len(row.get("checks", [])) for row in rows),
            "failures": len(failures),
        },
        "failures": failures,
    }


def render_schema_conformance_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Schema conformance audit",
        "",
        "This generated surface records whether public JSON surfaces conform to their published JSON Schema shape and type constraints.",
        "It exists because a schema file is not evidence unless the paired surface is checked against it.",
        "",
        "## Non-authority boundary",
        "",
        "This is not a schema-conformance-court, type-sovereign, contract-adjudication-board, schema-waiver-senate, generated-audit-notary, public-shape-tribunal, validation-authority-court, or typed-surface-certifier.",
        "Schema conformance is a public-shape hygiene witness only; it does not certify semantic truth, canon sufficiency, release legitimacy, legal status, minimality, or continuation authority.",
        "",
        "## Counts",
        "",
        f"- Schemas checked: `{audit['counts']['schema_count']}`",
        f"- Constraint checks: `{audit['counts']['check_count']}`",
        f"- Failures: `{audit['counts']['failures']}`",
        "",
        "## Surfaces",
    ]
    for row in audit["schema_surfaces"]:
        lines.append(f"- `{row['schema']}` -> `{row['surface']}`: `{row['status']}` ({len(row.get('checks', []))} checks)")
    if audit["failures"]:
        lines.append("")
        lines.append("## Failures")
        for failure in audit["failures"][:25]:
            lines.append(f"- `{failure['schema']}` / `{failure['surface']}` / `{failure['path']}` expected `{failure['expected']}` observed `{failure['observed']}`")
    return "\n".join(lines).rstrip() + "\n"


def write_schema_conformance_audit(root: pathlib.Path) -> dict[str, Any]:
    audit = build_schema_conformance_audit(root)
    (root / "SCHEMA-CONFORMANCE-AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "docs/00-meta/schema-conformance-audit.md").write_text(render_schema_conformance_markdown(audit), encoding="utf-8")
    return audit
