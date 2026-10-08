#!/usr/bin/env python3
"""Validate the current packet-disposition ledger with a revision-neutral engine.

The current revision, snapshot name, and output names are derived from
REVISION.txt. Packet-specific policy belongs in the JSON contract, not Python.
No third-party package is required.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    safe_relative,
    write_json,
)

LEDGER_PATH = Path("data/current_packet_dispositions.json")
SCHEMA_PATH = Path("data/current_packet_dispositions.schema.json")
CONTRACT_PATH = Path("data/current_packet_disposition_contract.json")
REQUIRED_LEDGER_KEYS = {"authority", "revision", "source_lane", "source_ref", "packets"}
REQUIRED_PACKET_KEYS = {
    "packet_id",
    "title",
    "status",
    "behavior",
    "impact",
    "security_route",
    "selected_patch",
    "current_document",
}
OPTIONAL_PACKET_KEYS = {
    "missing_evidence",
    "source_lane",
    "source_ref",
    "executable_source_ref",
    "source_scope",
}
ALLOWED_PACKET_KEYS = REQUIRED_PACKET_KEYS | OPTIONAL_PACKET_KEYS
NO_PATCH_STATUS_PREFIXES = ("open-", "retired-")
REVISION_PATTERN = re.compile(r"rev[0-9]{4}")
REF_PATTERN = re.compile(r"[0-9a-f]{40}")
STATUS_PATTERN = re.compile(r"[a-z0-9-]+")
LANE_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/+()-]+")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))





def looks_like_artifact_path(value: str) -> bool:
    return "/" in value or value.endswith((".patch", ".diff"))


def _load_or_override(root: Path, path: Path, override: Any | None) -> Any:
    return deepcopy(override) if override is not None else load_json(root / path)


def validate(
    root: Path,
    *,
    ledger_data: Any | None = None,
    snapshot_data: Any | None = None,
    schema_data: Any | None = None,
    contract_data: Any | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({
            "check": name,
            "status": "pass" if passed else "fail",
            "detail": str(detail),
        })
        if not passed:
            errors.append(f"{name}: {detail}")

    try:
        revision = derive_revision(root)
        snapshot_path = Path(f"data/{revision}_packet_dispositions.json")
        ledger = _load_or_override(root, LEDGER_PATH, ledger_data)
        snapshot = _load_or_override(root, snapshot_path, snapshot_data)
        schema = _load_or_override(root, SCHEMA_PATH, schema_data)
        contract = _load_or_override(root, CONTRACT_PATH, contract_data)
    except Exception as exc:
        return {
            "revision": "unknown",
            "status": "fail",
            "checks": checks,
            "errors": [f"load: {exc}"],
        }

    add("ledger object", isinstance(ledger, dict), type(ledger).__name__)
    if not isinstance(ledger, dict):
        return {
            "revision": revision,
            "status": "fail",
            "checks": checks,
            "errors": errors,
        }

    add("ledger keys exact", set(ledger) == REQUIRED_LEDGER_KEYS, sorted(set(ledger) ^ REQUIRED_LEDGER_KEYS))
    add("revision matches REVISION.txt", ledger.get("revision") == revision, ledger.get("revision"))
    add("authority meaningful", isinstance(ledger.get("authority"), str) and len(ledger.get("authority", "")) >= 20)
    add("source lane format", isinstance(ledger.get("source_lane"), str) and LANE_PATTERN.fullmatch(ledger.get("source_lane", "")) is not None, ledger.get("source_lane"))
    add("source ref format", isinstance(ledger.get("source_ref"), str) and REF_PATTERN.fullmatch(ledger.get("source_ref", "")) is not None, ledger.get("source_ref"))
    add("snapshot parsed equality", ledger == snapshot)
    add("snapshot canonical equality", canonical_json(ledger) == canonical_json(snapshot))

    add("schema object", isinstance(schema, dict), type(schema).__name__)
    schema_properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
    revision_schema = schema_properties.get("revision", {})
    source_ref_schema = schema_properties.get("source_ref", {})
    packet_schema = schema_properties.get("packets", {}).get("items", {})
    schema_text = canonical_json(schema) if isinstance(schema, dict) else ""
    add("schema revision-neutral id", REVISION_PATTERN.search(str(schema.get("$id", ""))) is None if isinstance(schema, dict) else False, schema.get("$id") if isinstance(schema, dict) else "")
    add("schema has no revision const", "const" not in revision_schema, revision_schema)
    add("schema revision pattern", revision_schema.get("pattern") == "^rev[0-9]{4}$", revision_schema)
    add("schema has no source ref const", "const" not in source_ref_schema, source_ref_schema)
    add("schema source ref pattern", source_ref_schema.get("pattern") == "^[0-9a-f]{40}$", source_ref_schema)
    add("schema contains no concrete revision", REVISION_PATTERN.search(schema_text) is None, "concrete revision found" if REVISION_PATTERN.search(schema_text) else "")
    add("schema disallows ledger extras", isinstance(schema, dict) and schema.get("additionalProperties") is False)
    add("schema disallows packet extras", packet_schema.get("additionalProperties") is False)
    add("schema packet requirements", set(packet_schema.get("required", [])) == REQUIRED_PACKET_KEYS, packet_schema.get("required"))
    schema_packet_fields = set(packet_schema.get("properties", {}))
    add("schema packet fields match engine", schema_packet_fields == ALLOWED_PACKET_KEYS, sorted(schema_packet_fields ^ ALLOWED_PACKET_KEYS))

    packets = ledger.get("packets")
    add("packets nonempty list", isinstance(packets, list) and bool(packets), type(packets).__name__)
    if not isinstance(packets, list):
        packets = []

    packet_ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    documents: list[str] = []
    selected_artifacts: list[str] = []
    for index, packet in enumerate(packets):
        prefix = f"packet[{index}]"
        add(f"{prefix} object", isinstance(packet, dict), type(packet).__name__)
        if not isinstance(packet, dict):
            continue
        keys = set(packet)
        add(f"{prefix} required keys", REQUIRED_PACKET_KEYS <= keys, sorted(REQUIRED_PACKET_KEYS - keys))
        add(f"{prefix} allowed keys", keys <= ALLOWED_PACKET_KEYS, sorted(keys - ALLOWED_PACKET_KEYS))
        packet_id = packet.get("packet_id")
        add(f"{prefix} id", isinstance(packet_id, str) and len(packet_id) >= 2, packet_id)
        add(f"{prefix} title", isinstance(packet.get("title"), str) and len(packet.get("title", "")) >= 4)
        status = packet.get("status")
        add(f"{prefix} status format", isinstance(status, str) and STATUS_PATTERN.fullmatch(status or "") is not None, status)
        for field in ("behavior", "impact", "security_route"):
            add(f"{prefix} {field}", isinstance(packet.get(field), str) and len(packet.get(field, "")) >= 3)

        selected = packet.get("selected_patch")
        add(f"{prefix} selected patch type", selected is None or isinstance(selected, str), type(selected).__name__)
        if isinstance(status, str) and status.startswith(NO_PATCH_STATUS_PREFIXES):
            add(f"{prefix} open/retired has no patch", selected is None, selected)
        if isinstance(selected, str) and looks_like_artifact_path(selected):
            path_ok = safe_relative(selected) and PurePosixPath(selected).suffix in {".patch", ".diff"}
            add(f"{prefix} selected artifact safe", path_ok, selected)
            if path_ok:
                add(f"{prefix} selected artifact exists", (root / selected).is_file(), selected)
                selected_artifacts.append(selected)

        document = packet.get("current_document")
        document_ok = safe_relative(document, prefix="docs", suffix=".md")
        add(f"{prefix} current document safe", document_ok, document)
        if document_ok:
            add(f"{prefix} current document exists", (root / str(document)).is_file(), document)
            documents.append(str(document))

        missing = packet.get("missing_evidence")
        if missing is not None:
            missing_ok = isinstance(missing, list) and all(isinstance(item, str) and len(item) >= 4 for item in missing)
            add(f"{prefix} missing evidence list", missing_ok)
            if isinstance(missing, list):
                add(f"{prefix} missing evidence unique", len(missing) == len(set(missing)), missing)

        source_lane = packet.get("source_lane")
        if source_lane is not None:
            add(f"{prefix} source lane format", isinstance(source_lane, str) and LANE_PATTERN.fullmatch(source_lane or "") is not None, source_lane)
        for field in ("source_ref", "executable_source_ref"):
            value = packet.get(field)
            if value is not None:
                add(f"{prefix} {field} format", isinstance(value, str) and REF_PATTERN.fullmatch(value or "") is not None, value)
        source_scope = packet.get("source_scope")
        if source_scope is not None:
            add(f"{prefix} source scope", isinstance(source_scope, str) and len(source_scope) >= 12)

        if isinstance(packet_id, str):
            packet_ids.append(packet_id)
            if packet_id not in by_id:
                by_id[packet_id] = packet

    add("packet ids unique", len(packet_ids) == len(set(packet_ids)), packet_ids)
    add("current document coverage", len(documents) == len(packets), documents)

    add("contract object", isinstance(contract, dict), type(contract).__name__)
    if isinstance(contract, dict):
        expected_contract_keys = {
            "version",
            "allow_additional_packets",
            "required_packet_ids",
            "top_level_constraints",
            "packet_constraints",
        }
        add("contract keys exact", set(contract) == expected_contract_keys, sorted(set(contract) ^ expected_contract_keys))
        add("contract version", contract.get("version") == 1, contract.get("version"))
        required_ids = contract.get("required_packet_ids")
        add("contract required ids list", isinstance(required_ids, list) and all(isinstance(item, str) for item in required_ids), required_ids)
        if isinstance(required_ids, list):
            add("contract required ids unique", len(required_ids) == len(set(required_ids)), required_ids)
            required_set = set(required_ids)
            actual_set = set(packet_ids)
            add("contract required ids present", required_set <= actual_set, sorted(required_set - actual_set))
            if contract.get("allow_additional_packets") is False:
                add("contract exact packet set", actual_set == required_set, {"missing": sorted(required_set - actual_set), "extra": sorted(actual_set - required_set)})

        top_constraints = contract.get("top_level_constraints")
        add("contract top constraints object", isinstance(top_constraints, dict), type(top_constraints).__name__)
        if isinstance(top_constraints, dict):
            for field, expected in top_constraints.items():
                add(f"contract top {field}", ledger.get(field) == expected, {"actual": ledger.get(field), "expected": expected})

        packet_constraints = contract.get("packet_constraints")
        add("contract packet constraints object", isinstance(packet_constraints, dict), type(packet_constraints).__name__)
        if isinstance(packet_constraints, dict):
            add("contract constraints cover required ids", set(packet_constraints) == set(contract.get("required_packet_ids", [])), sorted(set(packet_constraints) ^ set(contract.get("required_packet_ids", []))))
            for packet_id, constraints in packet_constraints.items():
                packet = by_id.get(packet_id)
                add(f"contract packet exists {packet_id}", packet is not None)
                add(f"contract constraints object {packet_id}", isinstance(constraints, dict), type(constraints).__name__)
                if packet is None or not isinstance(constraints, dict):
                    continue
                for field, expected in constraints.items():
                    add(f"contract {packet_id} {field}", packet.get(field) == expected, {"actual": packet.get(field), "expected": expected})

    return {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "packet_count": len(packets),
        "packet_ids": packet_ids,
        "current_documents": documents,
        "selected_artifacts": selected_artifacts,
        "snapshot": f"data/{revision}_packet_dispositions.json",
        "contract": CONTRACT_PATH.as_posix(),
        "checks": checks,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result.get("revision", "unknown")
    output = root / f"data/{revision}_packet_disposition_validation.json"
    evidence = root / f"evidence/{revision}-packet-disposition-validation.md"
    write_json(output, result)
    lines = [
        f"# {revision} packet-disposition validation",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"checks: {result.get('checks_passed', 0)}/{result.get('checks_total', 0)}",
        f"packets: {result.get('packet_count', 0)}",
        f"snapshot: {result.get('snapshot')}",
        f"selected path artifacts: {len(result.get('selected_artifacts', []))}",
        "```",
        "",
    ]
    if result.get("errors"):
        lines.extend(["## Errors", ""] + [f"- {item}" for item in result["errors"]])
    evidence.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = validate(root)
    if args.write_data and result.get("revision") != "unknown":
        write_outputs(root, result)
    print(canonical_json(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
