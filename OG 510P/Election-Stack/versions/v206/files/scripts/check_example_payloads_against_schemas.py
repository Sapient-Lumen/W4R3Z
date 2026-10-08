#!/usr/bin/env python3
"""scripts/check_example_payloads_against_schemas.py

Release-gate drift firewall: ensure shipped *example packet payloads* remain
compatible with their declared payload_schema.

Why a separate check?
- `scripts/check_example_packets.py` verifies envelopes, digests, and attachment
  integrity, but intentionally does not validate payload instances.
- `scripts/validate_schemas.py` validates a small set of templates and envelopes
  (and may meta-validate schemas when `jsonschema` is available), but it does
  not currently enforce payload validation for all shipped packets.

Constraints:
- stdlib-only (no hard dependency on jsonschema)
- bounded: this is a *drift tripwire*, not a full JSON Schema implementation

What we check (best-effort):
- For payload schemas under `schemas/` where:
  - type == object
  - additionalProperties == false
  - properties is a dict
  we enforce:
    - required[] keys exist
    - no unknown top-level keys
  and we recurse into a small subset of nested shapes:
    - object properties with additionalProperties == false
    - arrays whose items are object schemas with additionalProperties == false

If a schema uses advanced JSON Schema features ($ref/oneOf/anyOf/allOf), this
script skips deeper validation for that sub-tree rather than guessing.

This keeps the archive lean while preventing silent example rot.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def payload_from_envelope(packet_dir: Path, env: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, str]:
    if isinstance(env.get("payload_inline"), dict):
        return env["payload_inline"], "payload_inline"

    ptr = env.get("payload_pointer")
    if not isinstance(ptr, dict):
        return None, "missing_payload_pointer"
    uri = (ptr.get("uri") or "").strip()
    if not uri:
        return None, "missing_payload_pointer_uri"

    rel = uri if uri.startswith("objects/") else f"objects/{uri}"
    path = (packet_dir / rel).resolve()
    try:
        path.relative_to(packet_dir.resolve())
    except Exception:
        return None, "payload_pointer_uri_escapes_packet"
    if not path.exists():
        return None, "missing_payload_object"
    obj = load_json(path)
    return (obj if isinstance(obj, dict) else None), rel


def _can_object_check(schema: Any) -> bool:
    return (
        isinstance(schema, dict)
        and schema.get("type") == "object"
        and schema.get("additionalProperties") is False
        and isinstance(schema.get("properties"), dict)
        and ("$ref" not in schema)
        and ("oneOf" not in schema)
        and ("anyOf" not in schema)
        and ("allOf" not in schema)
    )


def _schema_required(schema: Dict[str, Any]) -> List[str]:
    req = schema.get("required")
    return [str(x) for x in req] if isinstance(req, list) else []


def _schema_properties(schema: Dict[str, Any]) -> Dict[str, Any]:
    props = schema.get("properties")
    return props if isinstance(props, dict) else {}


def _validate_object(instance: Any, schema: Dict[str, Any], path: str, failures: List[str]) -> None:
    if not _can_object_check(schema):
        return
    if not isinstance(instance, dict):
        failures.append(f"{path}: expected object")
        return

    props = _schema_properties(schema)
    req = _schema_required(schema)

    for k in req:
        if k not in instance:
            failures.append(f"{path}: missing required key '{k}'")

    for k in instance.keys():
        if k not in props:
            failures.append(f"{path}: unknown key '{k}' (schema additionalProperties=false)")

    # Best-effort recursion for a subset of shapes.
    for k, subschema in props.items():
        if k not in instance:
            continue
        v = instance.get(k)
        if isinstance(subschema, dict):
            # Nested object.
            if _can_object_check(subschema):
                _validate_object(v, subschema, f"{path}.{k}", failures)
                continue

            # Array-of-object.
            if subschema.get("type") == "array" and isinstance(subschema.get("items"), dict):
                items = subschema["items"]
                if _can_object_check(items):
                    if not isinstance(v, list):
                        failures.append(f"{path}.{k}: expected array")
                        continue
                    for i, item in enumerate(v):
                        _validate_object(item, items, f"{path}.{k}[{i}]", failures)


def check_packet(packet_dir: Path) -> List[str]:
    failures: List[str] = []
    env_dir = packet_dir / "envelopes"
    if not env_dir.exists():
        return failures

    for env_path in sorted(env_dir.glob("*.json")):
        try:
            env = load_json(env_path)
        except Exception as e:
            failures.append(f"{packet_dir.name}:{env_path.name}: envelope JSON parse failed: {e}")
            continue
        if not isinstance(env, dict):
            continue

        schema_ref = env.get("payload_schema")
        if not isinstance(schema_ref, str) or not schema_ref.startswith("schemas/"):
            continue
        schema_path = ROOT / schema_ref
        if not schema_path.exists():
            failures.append(f"{packet_dir.name}:{env_path.name}: missing payload_schema file: {schema_ref}")
            continue

        payload, where = payload_from_envelope(packet_dir, env)
        if payload is None:
            failures.append(f"{packet_dir.name}:{env_path.name}: missing/invalid payload ({where})")
            continue

        try:
            schema = load_json(schema_path)
        except Exception as e:
            failures.append(f"{packet_dir.name}:{env_path.name}: schema JSON parse failed: {schema_ref}: {e}")
            continue

        # Only enforce when the schema is in the "simple strict object" shape.
        if not _can_object_check(schema if isinstance(schema, dict) else None):
            continue

        kind = str(env.get("kind") or "")
        base = f"{packet_dir.name}:{env_path.name}:{kind}:payload"
        _validate_object(payload, schema, base, failures)

    return failures


def main() -> int:
    if not EXAMPLES.exists():
        print("PASS: no examples directory")
        return 0

    packets = sorted([p for p in EXAMPLES.iterdir() if p.is_dir() and p.name.startswith("evidence_packet_")])
    failures: List[str] = []
    for pkt in packets:
        failures.extend(check_packet(pkt))

    if failures:
        for f in failures:
            print("ERROR:", f, file=sys.stderr)
        return 2

    print(f"PASS: example payloads vs schemas ({len(packets)} packet(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
