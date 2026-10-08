#!/usr/bin/env python3
"""Fail-closed, revision-neutral audit for the current cube package."""
from __future__ import annotations

import argparse
import csv
import json
import re
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
    write_json,
)
from audit_current_contract_coherence import audit as audit_contract_coherence  # noqa: E402

CONTRACT_PATH = Path("data/current_package_contract.json")
ARCHIVE_SUFFIXES = (".zip", ".tar", ".tar.gz", ".tgz", ".7z")
SOURCE_TREE_MARKERS = {"source-trees", "git-full"}


def parse_manifest(path: Path) -> tuple[dict[str, str], list[str]]:
    rows: dict[str, str] = {}
    errors: list[str] = []
    if not path.is_file():
        return rows, ["manifest missing"]
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            errors.append(f"manifest line {number} malformed")
            continue
        digest, relative = match.groups()
        if not safe_relative(relative):
            errors.append(f"manifest line {number} unsafe path: {relative}")
            continue
        if relative in rows:
            errors.append(f"manifest duplicate path: {relative}")
            continue
        rows[relative] = digest
    return rows, errors


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return []
    return list(value)


def audit(root: Path, *, allow_missing_manifest: bool = False) -> dict[str, Any]:
    root = root.resolve()
    revision = derive_revision(root)
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("package contract version", contract.get("version") == 11, contract.get("version"))
    revision_contract_relative = contract.get("revision_contract")
    add(
        "revision contract path",
        isinstance(revision_contract_relative, str) and safe_relative(revision_contract_relative),
        revision_contract_relative,
    )
    try:
        revision_contract = json.loads(
            (root / str(revision_contract_relative)).read_text(encoding="utf-8")
        )
    except Exception as exc:
        revision_contract = {}
        add("revision contract readable", False, exc)
    else:
        add("revision contract readable", True, revision_contract_relative)
        add("revision contract version", revision_contract.get("version") == 2, revision_contract.get("version"))
        add("revision contract matches", revision_contract.get("revision") == revision, revision_contract.get("revision"))

    add("revision marker", (root / "REVISION.txt").read_text(encoding="utf-8").strip() == revision, revision)
    add("README current revision", revision in (root / "README.md").read_text(encoding="utf-8"), revision)
    add("START-HERE current revision", revision in (root / "docs/START-HERE.md").read_text(encoding="utf-8"), revision)

    try:
        coherence = audit_contract_coherence(root)
    except Exception as exc:
        coherence = {}
        add("live contract coherence", False, f"{type(exc).__name__}: {exc}")
    else:
        add(
            "live contract coherence",
            coherence.get("status") == "pass",
            {
                "status": coherence.get("status"),
                "checks": f"{coherence.get('checks_passed', 0)}/{coherence.get('checks_total', 0)}",
                "mutations": f"{coherence.get('mutation_checks_passed', 0)}/{coherence.get('mutation_checks_total', 0)}",
                "errors": coherence.get("errors", []),
            },
        )

    base_paths = _string_list(contract.get("base_required_paths"))
    authority_paths = _string_list(revision_contract.get("authority_paths"))
    status_files = _string_list(revision_contract.get("status_files"))
    nonempty_csv = _string_list(revision_contract.get("nonempty_csv"))
    required_paths = list(dict.fromkeys(base_paths + authority_paths + status_files + nonempty_csv))
    add("required paths unique", len(required_paths) == len(set(required_paths)), len(required_paths))
    for relative in required_paths:
        add(f"required path: {relative}", safe_relative(relative) and (root / relative).is_file())

    for relative in status_files:
        path = root / relative
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            add(f"status pass: {relative}", payload.get("status") == "pass", payload.get("status"))
            add(f"revision match: {relative}", payload.get("revision") == revision, payload.get("revision"))
        except Exception as exc:
            add(f"status readable: {relative}", False, exc)

    for relative in nonempty_csv:
        path = root / relative
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            add(f"nonempty CSV: {relative}", bool(rows), len(rows))
        except Exception as exc:
            add(f"nonempty CSV: {relative}", False, exc)

    package_paths = sorted(root.rglob("*"))
    files = [path for path in package_paths if path.is_file()]
    directories = [path for path in package_paths if path.is_dir()]
    symlinks = [path.relative_to(root).as_posix() for path in package_paths if path.is_symlink()]
    add("no symlinks", not symlinks, symlinks)

    forbidden_parts = set(_string_list(contract.get("forbidden_path_parts")))
    forbidden_hits = [
        path.relative_to(root).as_posix()
        for path in package_paths
        if forbidden_parts.intersection(path.relative_to(root).parts)
    ]
    add("no forbidden cache or VCS paths", not forbidden_hits, forbidden_hits[:20])

    source_tree_hits = [
        path.relative_to(root).as_posix()
        for path in files
        if SOURCE_TREE_MARKERS.intersection(path.relative_to(root).parts)
    ]
    add("no embedded upstream source trees", not source_tree_hits, source_tree_hits[:20])

    evidence_names = set(_string_list(contract.get("forbidden_evidence_directory_names")))
    evidence_templates = _string_list(contract.get("current_evidence_roots"))
    add("evidence residue names configured", bool(evidence_names), sorted(evidence_names))
    add("current evidence roots configured", bool(evidence_templates), evidence_templates)
    evidence_roots: list[str] = []
    residue_directories: list[str] = []
    residue_files: list[str] = []
    for template in evidence_templates:
        try:
            relative = template.format(revision=revision)
        except (KeyError, ValueError) as exc:
            add(f"current evidence template: {template}", False, exc)
            continue
        safe = safe_relative(relative)
        evidence_path = root / relative
        add(f"current evidence root: {relative}", safe and evidence_path.is_dir())
        if not safe or not evidence_path.is_dir():
            continue
        evidence_roots.append(relative)
        for path in sorted(evidence_path.rglob("*")):
            if not path.is_dir() or path.name not in evidence_names:
                continue
            residue_directories.append(path.relative_to(root).as_posix())
            residue_files.extend(
                item.relative_to(root).as_posix()
                for item in sorted(path.rglob("*"))
                if item.is_file() or item.is_symlink()
            )
    add(
        "current evidence has no transient environment or source trees",
        not residue_directories,
        residue_directories[:20],
    )

    allowed_archives = contract.get("allowed_fixture_archives", {})
    if not isinstance(allowed_archives, dict):
        allowed_archives = {}
        add("allowed archive mapping", False, "not a mapping")
    archive_hits: list[str] = []
    archive_hash_errors: list[str] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        if not relative.lower().endswith(ARCHIVE_SUFFIXES):
            continue
        archive_hits.append(relative)
        expected = allowed_archives.get(relative)
        if expected is None:
            archive_hash_errors.append(f"unapproved archive: {relative}")
        elif sha256_path(path) != expected:
            archive_hash_errors.append(f"fixture hash mismatch: {relative}")
    add("archive set approved", not archive_hash_errors, archive_hash_errors)
    add("approved fixture archive count", set(archive_hits) == set(allowed_archives), archive_hits)

    python_errors: list[str] = []
    current_python = sorted(relative for relative in authority_paths if relative.endswith(".py"))
    for relative in current_python:
        path = root / relative
        try:
            compile(path.read_text(encoding="utf-8"), relative, "exec")
        except Exception as exc:
            python_errors.append(f"{relative}: {type(exc).__name__}: {exc}")
    add("current Python compiles", not python_errors, python_errors)

    manifest_relative = f"handoff/{revision}/MANIFEST.sha256"
    manifest_path = root / manifest_relative
    if not manifest_path.is_file() and allow_missing_manifest:
        add("manifest deferred", True, manifest_relative)
        manifest_rows: dict[str, str] = {}
    else:
        manifest_rows, manifest_errors = parse_manifest(manifest_path)
        add("manifest syntax", not manifest_errors, manifest_errors)
        actual = {
            path.relative_to(root).as_posix(): sha256_path(path)
            for path in files
            if path.relative_to(root).as_posix() != manifest_relative
        }
        missing = sorted(set(actual) - set(manifest_rows))
        extra = sorted(set(manifest_rows) - set(actual))
        mismatched = sorted(
            relative for relative in set(actual) & set(manifest_rows)
            if actual[relative] != manifest_rows[relative]
        )
        add("manifest complete", not missing, missing[:20])
        add("manifest has no extras", not extra, extra[:20])
        add("manifest hashes match", not mismatched, mismatched[:20])
        add("manifest row count", len(manifest_rows) == len(actual), f"manifest={len(manifest_rows)} actual={len(actual)}")

    ledger = json.loads((root / "data/current_packet_dispositions.json").read_text(encoding="utf-8"))
    packets_by_id = {
        packet.get("packet_id"): packet
        for packet in ledger.get("packets", [])
        if isinstance(packet, dict) and isinstance(packet.get("packet_id"), str)
    }
    selected = [packet.get("selected_patch") for packet in packets_by_id.values() if packet.get("selected_patch")]
    add("current ledger revision", ledger.get("revision") == revision, ledger.get("revision"))
    for requirement in contract.get("ledger_requirements", []):
        packet_id = requirement.get("packet_id") if isinstance(requirement, dict) else None
        packet = packets_by_id.get(packet_id)
        add(f"ledger packet present: {packet_id}", packet is not None)
        if packet is None or not isinstance(requirement, dict):
            continue
        for field, expected in requirement.items():
            if field == "packet_id":
                continue
            add(
                f"ledger {packet_id} {field}",
                packet.get(field) == expected,
                {"actual": packet.get(field), "expected": expected},
            )
    add(
        "selected path artifacts exist",
        all(not isinstance(value, str) or "/" not in value or (root / value).is_file() for value in selected),
        selected,
    )

    return {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "files": len(files),
        "directories": len(directories),
        "symlinks": len(symlinks),
        "current_evidence_roots": evidence_roots,
        "evidence_residue_directories": residue_directories,
        "evidence_residue_files": residue_files,
        "approved_archives": len(archive_hits),
        "manifest_rows": len(manifest_rows),
        "authority_paths": len(authority_paths),
        "status_files": len(status_files),
        "nonempty_csv": len(nonempty_csv),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = str(result["revision"])
    write_json(root / f"data/{revision}_package_audit.json", result)
    lines = [
        f"# {revision} package validation",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"files: {result['files']}",
        f"directories: {result['directories']}",
        f"current evidence roots: {len(result['current_evidence_roots'])}",
        f"evidence residue directories: {len(result['evidence_residue_directories'])}",
        f"evidence residue files: {len(result['evidence_residue_files'])}",
        f"authority paths: {result['authority_paths']}",
        f"status files: {result['status_files']}",
        f"nonempty CSV outputs: {result['nonempty_csv']}",
        f"symlinks: {result['symlinks']}",
        f"approved fixture archives: {result['approved_archives']}",
        f"manifest rows: {result['manifest_rows']}",
        f"checks: {result['checks_passed']}/{result['checks_total']}",
        "```",
        "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in result["errors"]])
    (root / f"evidence/{revision}-package-validation.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--allow-missing-manifest", action="store_true")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root, allow_missing_manifest=args.allow_missing_manifest)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
