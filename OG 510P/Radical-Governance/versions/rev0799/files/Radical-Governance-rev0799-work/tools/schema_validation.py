#!/usr/bin/env python3
"""Dependency-free JSON Schema validation for the archive's supported subset.

The repository schemas intentionally use a small subset of draft 2020-12:
``type``, ``required``, ``properties``, ``additionalProperties``, ``items``,
``const``, and ``pattern``. Keeping validation here avoids turning ``make lint``
into an environment-dependent command while still making schema files active
controls rather than documentation only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema",
    "$id",
    "title",
    "type",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "const",
    "pattern",
}


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported JSON Schema type: {expected!r}")


def _type_label(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    return type(value).__name__


def validate_instance(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate one instance against the repository's schema subset."""
    errors: list[str] = []

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}, got {value!r}")

    expected_type = schema.get("type")
    if expected_type is not None:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if not all(isinstance(item, str) for item in allowed):
            errors.append(f"{path}: schema type declaration is invalid: {expected_type!r}")
            return errors
        if not any(_matches_type(value, item) for item in allowed):
            errors.append(f"{path}: expected type {allowed!r}, got {_type_label(value)}")
            return errors

    if isinstance(value, str) and "pattern" in schema:
        pattern = schema["pattern"]
        try:
            matches = re.search(pattern, value) is not None
        except re.error as exc:
            errors.append(f"{path}: invalid schema pattern {pattern!r}: {exc}")
        else:
            if not matches:
                errors.append(f"{path}: value {value!r} does not match pattern {pattern!r}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        if required is not None:
            if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
                errors.append(f"{path}: schema required declaration must be an array of strings")
            else:
                for key in required:
                    if key not in value:
                        errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            errors.append(f"{path}: schema properties declaration must be an object")
            properties = {}
        for key, subschema in properties.items():
            if key in value:
                if not isinstance(subschema, dict):
                    errors.append(f"{path}.{key}: property schema must be an object")
                else:
                    errors.extend(validate_instance(value[key], subschema, f"{path}.{key}"))

        additional = schema.get("additionalProperties", True)
        for key in value:
            if key in properties:
                continue
            child_path = f"{path}.{key}"
            if additional is False:
                errors.append(f"{child_path}: additional property is not allowed")
            elif isinstance(additional, dict):
                errors.extend(validate_instance(value[key], additional, child_path))
            elif additional is not True:
                errors.append(f"{path}: additionalProperties must be boolean or object")
                break

    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        if not isinstance(item_schema, dict):
            errors.append(f"{path}: schema items declaration must be an object")
        else:
            for index, item in enumerate(value):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))

    return errors


def _scan_schema_keywords(node: Any, path: str = "$") -> list[str]:
    """Reject unsupported control keywords while ignoring property names."""
    errors: list[str] = []
    if not isinstance(node, dict):
        return errors

    # At schema-object level, known control keys are validated. Property names
    # live beneath `properties` and are not themselves schema keywords.
    for key, value in node.items():
        if key == "properties":
            if isinstance(value, dict):
                for property_name, property_schema in value.items():
                    errors.extend(_scan_schema_keywords(property_schema, f"{path}.properties.{property_name}"))
            continue
        if key == "additionalProperties" and isinstance(value, dict):
            errors.extend(_scan_schema_keywords(value, f"{path}.additionalProperties"))
            continue
        if key == "items" and isinstance(value, dict):
            errors.extend(_scan_schema_keywords(value, f"{path}.items"))
            continue
        if key not in SUPPORTED_SCHEMA_KEYWORDS:
            errors.append(f"{path}: unsupported JSON Schema keyword {key!r}")
    return errors


def validate_repository_json(root: Path) -> tuple[list[str], dict[str, int]]:
    """Validate all canonical metadata/source JSON files and schema coverage."""
    schema_dir = root / "schema"
    errors: list[str] = []
    schemas_by_const: dict[str, tuple[Path, dict[str, Any]]] = {}

    schema_paths = sorted(schema_dir.glob("*.schema.json"))
    for path in schema_paths:
        rel = path.relative_to(root)
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: cannot load schema: {exc}")
            continue
        if not isinstance(schema, dict):
            errors.append(f"{rel}: schema root must be an object")
            continue
        errors.extend(f"{rel}: {item}" for item in _scan_schema_keywords(schema))
        schema_const = schema.get("properties", {}).get("schema", {}).get("const")
        if not isinstance(schema_const, str) or not schema_const:
            errors.append(f"{rel}: missing properties.schema.const identity")
            continue
        if schema_const in schemas_by_const:
            first = schemas_by_const[schema_const][0].relative_to(root)
            errors.append(f"{rel}: duplicate schema const {schema_const!r}; first declared by {first}")
            continue
        schemas_by_const[schema_const] = (path, schema)

    canonical_paths = sorted((root / "metadata").glob("*.json")) + sorted((root / "sources").glob("*.json"))
    schema_use_count = {key: 0 for key in schemas_by_const}
    validated_files = 0
    for path in canonical_paths:
        rel = path.relative_to(root)
        try:
            instance = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: cannot load canonical JSON: {exc}")
            continue
        if not isinstance(instance, dict):
            errors.append(f"{rel}: canonical JSON root must be an object")
            continue
        schema_const = instance.get("schema")
        if not isinstance(schema_const, str) or not schema_const:
            errors.append(f"{rel}: missing non-empty top-level schema identifier")
            continue
        match = schemas_by_const.get(schema_const)
        if match is None:
            errors.append(f"{rel}: no schema file declares const {schema_const!r}")
            continue
        schema_use_count[schema_const] += 1
        schema_path, schema = match
        instance_errors = validate_instance(instance, schema)
        errors.extend(
            f"{rel} against {schema_path.relative_to(root)}: {item}"
            for item in instance_errors
        )
        if not instance_errors:
            validated_files += 1

    for schema_const, count in schema_use_count.items():
        if count == 0:
            schema_path = schemas_by_const[schema_const][0].relative_to(root)
            errors.append(f"{schema_path}: schema const {schema_const!r} is not used by any canonical JSON file")
        elif count > 1:
            errors.append(f"schema const {schema_const!r} is used by {count} canonical JSON files; expected one")

    stats = {
        "schema_files": len(schema_paths),
        "canonical_json_files": len(canonical_paths),
        "validated_files": validated_files,
    }
    return errors, stats


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    errors, stats = validate_repository_json(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print(
        "OK: schema validation passed "
        f"({stats['validated_files']} canonical JSON files; {stats['schema_files']} schemas)"
    )


if __name__ == "__main__":
    main()
