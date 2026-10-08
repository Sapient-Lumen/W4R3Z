#!/usr/bin/env python3
"""Validate the cube's revision authority and current navigation surface.

The contract keeps revision-specific paths out of multiple independent package
and runtime contracts. Historical artifacts remain readable, but only the
current revision contract may nominate open-first documents and active tools.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import (  # noqa: E402
    canonical_json,
    derive_revision,
    safe_relative,
    sha256_path,
    write_csv,
    write_json,
)

CONTRACT_PATH = Path("data/current_revision_contract.json")


def _current_json_references(value: object) -> set[str]:
    """Return revision-neutral authority references embedded in a JSON value."""
    found: set[str] = set()
    if isinstance(value, dict):
        for item in value.values():
            found.update(_current_json_references(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_current_json_references(item))
    elif isinstance(value, str) and value.startswith("data/current_") and value.endswith(".json"):
        found.add(value)
    return found


def audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    revision = derive_revision(root)
    contract_path = root / CONTRACT_PATH
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("contract version", contract.get("version") == 2, contract.get("version"))
    add("contract revision", contract.get("revision") == revision, contract.get("revision"))
    primary_packet_id = contract.get("primary_packet_id")
    add("primary packet id format", isinstance(primary_packet_id, str) and len(primary_packet_id) >= 2, primary_packet_id)
    try:
        ledger = json.loads((root / "data/current_packet_dispositions.json").read_text(encoding="utf-8"))
        packet_ids = {
            packet.get("packet_id") for packet in ledger.get("packets", [])
            if isinstance(packet, dict) and isinstance(packet.get("packet_id"), str)
        }
    except Exception as exc:
        packet_ids = set()
        add("primary packet ledger readable", False, exc)
    else:
        add("primary packet ledger readable", True)
    add("primary packet id exists in ledger", primary_packet_id in packet_ids, primary_packet_id)

    list_fields = (
        "authority_paths",
        "current_navigation_files",
        "current_scripts",
        "forbidden_navigation_targets",
        "nonempty_csv",
        "status_files",
        "immutable_origin_paths",
    )
    for field in list_fields:
        values = contract.get(field)
        valid = isinstance(values, list) and all(isinstance(value, str) for value in values)
        add(f"{field} string list", valid, type(values).__name__)
        if valid:
            add(f"{field} unique", len(values) == len(set(values)), len(values))
            unsafe = [value for value in values if not safe_relative(value)]
            add(f"{field} safe paths", not unsafe, unsafe)

    authority = list(contract.get("authority_paths", []))
    navigation = list(contract.get("current_navigation_files", []))
    scripts = list(contract.get("current_scripts", []))
    add("navigation files are authorities", set(navigation) <= set(authority), navigation)
    add("current scripts are authorities", set(scripts) <= set(authority), scripts)
    add("revision contract is authoritative", CONTRACT_PATH.as_posix() in authority, CONTRACT_PATH)

    inventory: list[dict[str, object]] = []
    for relative in authority:
        path = root / relative
        exists = path.is_file() and not path.is_symlink()
        add(f"authority exists: {relative}", exists)
        inventory.append({
            "path": relative,
            "kind": "script" if relative in scripts else "navigation" if relative in navigation else "authority",
            "exists": exists,
            "bytes": path.stat().st_size if exists else 0,
            "sha256": sha256_path(path) if exists else "",
        })

    marker = revision.upper().replace("REV", "REV")
    for relative in navigation:
        path = root / relative
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        add(f"navigation revision marker: {relative}", revision in content or marker in content, revision)
        for forbidden in contract.get("forbidden_navigation_targets", []):
            add(f"no stale target in {relative}: {forbidden}", forbidden not in content)

    mentions = contract.get("required_mentions")
    add("required_mentions mapping", isinstance(mentions, dict), type(mentions).__name__)
    if isinstance(mentions, dict):
        for relative, targets in mentions.items():
            valid_targets = isinstance(targets, list) and all(isinstance(target, str) for target in targets)
            add(f"required mentions list: {relative}", valid_targets, targets)
            path = root / relative
            content = path.read_text(encoding="utf-8") if path.is_file() else ""
            if valid_targets:
                for target in targets:
                    add(f"navigation mention: {relative} -> {target}", target in content)

    current_revision_targets = [
        relative for relative in authority
        if "REV00" in relative.upper() or f"/{revision}/" in f"/{relative}/"
    ]
    immutable_origin_paths = set(contract.get("immutable_origin_paths", []))
    add("immutable origin paths are authorities", immutable_origin_paths <= set(authority), sorted(immutable_origin_paths - set(authority)))
    stale_revision_targets = [
        relative for relative in current_revision_targets
        if revision not in relative.lower() and relative not in immutable_origin_paths
    ]
    add("revision-specific authority paths are current or immutable origins", not stale_revision_targets, stale_revision_targets)

    # A rollover used to be able to leave the navigation text on the new
    # revision while one or more ``current_*`` JSON authorities still named
    # the previous revision.  Treat the complete current-authority graph as a
    # single fail-closed surface rather than validating each contract only
    # when a later probe happens to consume it.
    current_json_paths = sorted((root / "data").glob("current_*.json"))
    current_json_relatives = [path.relative_to(root).as_posix() for path in current_json_paths]
    add("current JSON authorities discovered", bool(current_json_relatives), current_json_relatives)
    add(
        "all current JSON authorities are nominated",
        set(current_json_relatives) <= set(authority),
        sorted(set(current_json_relatives) - set(authority)),
    )

    referenced_current_json: set[str] = set()
    current_json_inventory: list[dict[str, object]] = []
    for path, relative in zip(current_json_paths, current_json_relatives):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            add(f"current JSON readable: {relative}", False, exc)
            continue
        add(f"current JSON object: {relative}", isinstance(payload, dict), type(payload).__name__)
        if not isinstance(payload, dict):
            continue
        bound_revision = payload.get("revision")
        if bound_revision is not None:
            add(f"current JSON revision: {relative}", bound_revision == revision, bound_revision)
        references = _current_json_references(payload)
        referenced_current_json.update(references)
        current_json_inventory.append({
            "path": relative,
            "kind": "current-json-authority",
            "exists": True,
            "bytes": path.stat().st_size,
            "sha256": sha256_path(path),
        })

    missing_current_references = sorted(
        relative for relative in referenced_current_json if not (root / relative).is_file()
    )
    unnominated_current_references = sorted(referenced_current_json - set(authority))
    add("current JSON references exist", not missing_current_references, missing_current_references)
    add(
        "current JSON references are nominated",
        not unnominated_current_references,
        unnominated_current_references,
    )

    status_files = list(contract.get("status_files", []))
    nonempty_csv = list(contract.get("nonempty_csv", []))
    stale_status_names = [path for path in status_files if not path.startswith(f"data/{revision}_")]
    stale_csv_names = [path for path in nonempty_csv if not path.startswith(f"data/{revision}_")]
    add("status files use current revision prefix", not stale_status_names, stale_status_names)
    add("CSV files use current revision prefix", not stale_csv_names, stale_csv_names)

    inventory.extend(current_json_inventory)

    result = {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "contract": CONTRACT_PATH.as_posix(),
        "authority_paths": len(authority),
        "navigation_files": len(navigation),
        "current_scripts": len(scripts),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "errors": errors,
        "inventory": inventory,
    }
    return result


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = str(result["revision"])
    write_json(root / f"data/{revision}_navigation_audit.json", result)
    write_csv(
        root / f"data/{revision}_navigation_inventory.csv",
        result["inventory"],
        fields=("path", "kind", "exists", "bytes", "sha256"),
    )
    lines = [
        f"# {revision} current-authority navigation audit",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"authority paths: {result['authority_paths']}",
        f"navigation files: {result['navigation_files']}",
        f"current scripts: {result['current_scripts']}",
        f"checks: {result['checks_passed']}/{result['checks_total']}",
        "```",
        "",
        "Revision-specific authority now lives in one machine-readable contract; package and runtime audits consume it rather than maintaining separate path lists.",
        "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in result["errors"]])
    (root / f"evidence/{revision}-navigation-audit.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json({key: value for key, value in result.items() if key != "inventory"}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
