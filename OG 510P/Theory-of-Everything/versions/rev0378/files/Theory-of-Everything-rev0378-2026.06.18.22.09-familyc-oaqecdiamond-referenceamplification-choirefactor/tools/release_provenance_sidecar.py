#!/usr/bin/env python3
"""Generate/check the minimal release provenance sidecars.

The archive already has strong internal manifests.  This tool adds a small
external-facing metadata bridge without creating a second authority source:
`ro-crate-metadata.json` for research-object discovery, and
`RELEASE-BUILD-PROVENANCE.json` for unsigned local build/material replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

RO_CRATE = "ro-crate-metadata.json"
BUILD_PROVENANCE = "RELEASE-BUILD-PROVENANCE.json"
EXCLUDED_DIGEST_REL = {RO_CRATE, BUILD_PROVENANCE}
TRANSIENT_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git"}
TRANSIENT_FILE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".tmp", ".swp", ".zip"}
TRANSIENT_FILE_NAMES = {".DS_Store"}
CORE_MATERIALS = [
    "RELEASE-MANIFEST.json",
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "context-pack.json",
    "SOURCE-SNAPSHOT-MANIFEST.json",
    "FOLLOWTHROUGH-QUEUE.json",
    "KERNEL-TESTCARD.json",
    "docs/40-model/positive-kernel-testcard.md",
    "docs/30-program/kernel-testcard-audit.generated.md",
    "README.md",
    "START_HERE.md",
    "AGENTS.md",
    "tools/package_release.py",
    "tools/smoke_package_release.py",
    "tools/run_lint_steps.py",
    "tools/lint_steps_config.py",
    "tools/kernel_testcard_audit.py",
    "tools/lint_archive.py",
    "tools/source_role_negative_replay_tests.py",
    "tools/validate_registered_json_schemas.py",
    "tools/release_provenance_sidecar.py",
    "tools/candidate_docket_duplication_audit.py",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_transient(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in TRANSIENT_DIR_NAMES for part in rel.parts):
        return True
    if path.name in TRANSIENT_FILE_NAMES:
        return True
    if path.suffix in TRANSIENT_FILE_SUFFIXES:
        return True
    return False


def iter_material_files(root: Path) -> list[Path]:
    return sorted(
        (
            p for p in root.rglob("*")
            if p.is_file()
            and not is_transient(p, root)
            and p.relative_to(root).as_posix() not in EXCLUDED_DIGEST_REL
        ),
        key=lambda p: p.relative_to(root).as_posix(),
    )


def material_record(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {
        "path": rel,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def tree_digest(root: Path) -> tuple[str, int, int]:
    lines: list[str] = []
    total_bytes = 0
    files = iter_material_files(root)
    for path in files:
        rel = path.relative_to(root).as_posix()
        digest = sha256_file(path)
        size = path.stat().st_size
        total_bytes += size
        lines.append(f"{digest}  {rel}\n")
    h = hashlib.sha256()
    for line in lines:
        h.update(line.encode("utf-8"))
    return h.hexdigest(), len(files), total_bytes


def encoding_for(rel: str) -> str:
    if rel.endswith(".json"):
        return "application/json"
    if rel.endswith(".md"):
        return "text/markdown"
    if rel.endswith(".py"):
        return "text/x-python"
    if rel.endswith(".txt"):
        return "text/plain"
    return "application/octet-stream"


def timestamp_to_date(timestamp: str) -> str:
    parts = str(timestamp).split(".")
    if len(parts) >= 3:
        return "-".join(parts[:3])
    return str(timestamp)


def build_sidecars(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text())
    receipt = json.loads((root / "REVISION-RECEIPT.json").read_text())
    materials = [material_record(root, rel) for rel in CORE_MATERIALS if (root / rel).exists()]
    digest, file_count, byte_count = tree_digest(root)
    revision = manifest["revision"]
    bundle = manifest["bundle"]
    timestamp = manifest["timestamp"]

    file_nodes = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.2"},
            "about": {"@id": "./"},
        }
    ]
    for item in materials:
        file_nodes.append({
            "@id": item["path"],
            "@type": "File",
            "name": item["path"],
            "encodingFormat": encoding_for(item["path"]),
            "contentSize": item["bytes"],
            "sha256": item["sha256"],
        })

    ro_crate: dict[str, Any] = {
        "@context": [
            "https://w3id.org/ro/crate/1.2/context",
            {"prov": "http://www.w3.org/ns/prov#", "sha256": "https://schema.org/sha256"},
        ],
        "@graph": [
            *file_nodes,
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "Theory-of-Everything archive release",
                "identifier": bundle,
                "version": revision,
                "datePublished": timestamp_to_date(timestamp),
                "description": manifest.get("summary", ""),
                "license": "Archive bundle metadata only; external source payloads retain their original public terms.",
                "hasPart": [{"@id": item["path"]} for item in materials],
                "mentions": [
                    {"@id": "RELEASE-MANIFEST.json"},
                    {"@id": "REVISION-RECEIPT.json"},
                    {"@id": "SOURCE-SNAPSHOT-MANIFEST.json"},
                    {"@id": "RELEASE-BUILD-PROVENANCE.json"},
                ],
            },
            {
                "@id": "#package-build-action",
                "@type": "CreateAction",
                "name": "Deterministic local package build",
                "instrument": {"@id": "tools/package_release.py"},
                "object": [{"@id": item["path"]} for item in materials],
                "result": {"@id": bundle},
                "prov:used": [{"@id": item["path"]} for item in materials],
            },
            {
                "@id": "#archive-operator",
                "@type": "Organization",
                "name": "Theory-of-Everything archive continuation operator",
            },
        ],
    }

    build_provenance: dict[str, Any] = {
        "project": manifest.get("project"),
        "revision": revision,
        "previous_revision": manifest.get("previous_revision"),
        "schema_version": "0.1",
        "attestation_state": "unsigned-local-pre-output-provenance",
        "bundle_subject": bundle,
        "bundle_digest_policy": "The zip digest is printed by tools/package_release.py after this in-bundle provenance file is written; recording the final zip digest inside the zip would be self-referential.",
        "build_type": "deterministic-zip-from-release-manifest",
        "build_commands": ["make clean", "make index", "make lint", "make package"],
        "standards_bridge": {
            "ro_crate": "ro-crate-metadata.json describes the release as a JSON-LD research object using RO-Crate 1.2 vocabulary.",
            "prov": "The RO-Crate sidecar includes a CreateAction / prov:used bridge for the package build materials.",
            "slsa": "This is not a signed SLSA attestation; it records local material digests and build intent so a future signed attestation has a stable input map.",
            "swhid": "No Software Heritage identifiers are asserted in this revision; add them only for archived code objects with verified SWHIDs.",
        },
        "material_manifest": {
            "excluded_self_referential_files": sorted(EXCLUDED_DIGEST_REL),
            "file_count": file_count,
            "byte_count": byte_count,
            "sha256": digest,
        },
        "selected_materials": materials,
        "revision_receipt_move_classes": receipt.get("move_classes", []),
        "non_promotion_boundary": "Release provenance records package custody only. It does not promote a route, evidence unit, forecast, decision outcome, or public-record credit state.",
    }
    return ro_crate, build_provenance


def write_json_if_changed(path: Path, data: dict[str, Any]) -> bool:
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text() == rendered:
        return False
    path.write_text(rendered)
    return True


def check_json(path: Path, data: dict[str, Any]) -> list[str]:
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if not path.exists():
        return [f"missing generated provenance sidecar: {path.name}"]
    if path.read_text() != rendered:
        return [f"generated provenance sidecar drifted: {path.name}; run make index"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated sidecars are missing or stale")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    ro_crate, build_provenance = build_sidecars(root)
    if args.check:
        failures = []
        failures.extend(check_json(root / RO_CRATE, ro_crate))
        failures.extend(check_json(root / BUILD_PROVENANCE, build_provenance))
        if failures:
            print("RELEASE PROVENANCE SIDECAR FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("RELEASE PROVENANCE SIDECAR OK")
        return 0
    changed = []
    if write_json_if_changed(root / RO_CRATE, ro_crate):
        changed.append(RO_CRATE)
    if write_json_if_changed(root / BUILD_PROVENANCE, build_provenance):
        changed.append(BUILD_PROVENANCE)
    print("RELEASE PROVENANCE SIDECAR wrote " + (", ".join(changed) if changed else "no changes"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
