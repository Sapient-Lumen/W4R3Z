#!/usr/bin/env python3
"""Validate path references in compact control-plane JSON surfaces.

Archive coherence already checks a curated path subset.  This guard traverses the
control-plane JSON surfaces and fails closed when a string that is clearly a
repo-relative path points outside the tree, names a missing shipped file, or is
not portable.  Directory references must end in '/' and exist as directories.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

PATH_PREFIXES = (
    "reports/",
    "publishing/",
    "release_queue/",
    "published/",
    "series/",
    "schemas/",
)
ROOT_PATHS = {
    "VERSION",
    "Makefile",
    "LICENSE",
    "NOTICE",
    "CITATION.cff",
    "CONTEXT_PACK.json",
    "RELEASE_MANIFEST.json",
    "REVISION_RECEIPT.json",
    "REVISION_LINEAGE.json",
    "ARCHIVE_INDEX.json",
    "ARCHIVE_INDEX.md",
    "ASSURANCE_ARTIFACTS.json",
    "ASSURANCE_ARTIFACTS.md",
    "MANIFEST.json",
    "MANIFEST.sha256",
    "PATCH_NOTES.md",
    "PRUNING_POLICY.md",
    "PRUNED_TRANSIENT.paths",
    "README.md",
    "START_HERE.md",
    "TRANSFER_INPUTS.sha256",
    "TRANSFER_SOURCES.json",
    "TRANSFER_SOURCES.md",
    "DATACUBE_TRANSFER_LEDGER.json",
    "DATACUBE_TRANSFER_LEDGER.md",
    "codemeta.json",
    "ro-crate-metadata.json",
    "release_provenance.intoto.jsonl",
}
CONTROL_JSON = [
    "CONTEXT_PACK.json",
    "publishing/CANONICAL_POLICY.json",
    "publishing/control_surfaces.json",
    "ASSURANCE_ARTIFACTS.json",
    "publishing/archive_invariants.json",
    "publishing/archive_budget_policy.json",
    "release_queue/EVIDENCE_PACK_REGISTRY.json",
    "release_queue/FREEZE_PACKET_REGISTRY.json",
    "release_queue/NEXT_RELEASE_FREEZE_PLAN.json",
    "release_queue/PUBLICATION_BLOCKERS.json",
]
PORTABLE_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
PROSPECTIVE_PUBLISHED_TARGET_RE = re.compile(r"^published/\d{4}-\d{2}-\d{2}_[a-z0-9]+(?:_[a-z0-9]+)*$")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def looks_like_repo_path(value: str) -> bool:
    return value in ROOT_PATHS or value.startswith(PATH_PREFIXES)


def walk_strings(value: Any, pointer: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            out.extend(walk_strings(child, f"{pointer}/{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.extend(walk_strings(child, f"{pointer}/{index}"))
    elif isinstance(value, str):
        out.append((pointer or "/", value))
    return out


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for rel in CONTROL_JSON:
        surface = root / rel
        if not surface.exists():
            row = {"surface": rel, "pointer": "/", "path": rel, "status": "fail", "failures": [{"category": "control_surface_missing"}]}
            rows.append(row)
            failures.append(row)
            continue
        data = load_json(surface)
        for pointer, value in walk_strings(data):
            if not looks_like_repo_path(value):
                continue
            row_failures: list[dict[str, Any]] = []
            if value.startswith("/") or ".." in pathlib.PurePosixPath(value).parts:
                row_failures.append({"category": "unsafe_path_reference"})
            if not PORTABLE_RE.match(value):
                row_failures.append({"category": "nonportable_path_reference"})
            target = root / value.rstrip("/")
            is_prospective_publication_target = bool(PROSPECTIVE_PUBLISHED_TARGET_RE.match(value)) and any(token in pointer for token in ("prospective_target", "/target"))
            if value.endswith("/"):
                if not target.is_dir():
                    row_failures.append({"category": "missing_directory_reference"})
            elif is_prospective_publication_target:
                # Prospective publication targets are intentionally not materialized until
                # an explicit publication decision exists; portability is checked above.
                pass
            elif not target.is_file():
                row_failures.append({"category": "missing_file_reference"})
            row = {"surface": rel, "pointer": pointer, "path": value, "status": "pass" if not row_failures else "fail", "failures": row_failures}
            rows.append(row)
            if row_failures:
                failures.append(row)

    unique_paths = sorted({row["path"] for row in rows})
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "control_surfaces_checked": CONTROL_JSON,
        "path_rows": rows,
        "failures": failures[:100],
        "summary": {
            "checks_failed": len(failures),
            "control_surface_count": len(CONTROL_JSON),
            "path_reference_count": len(rows),
            "unique_path_reference_count": len(unique_paths),
            "missing_reference_count": sum(1 for row in failures for failure in row.get("failures", []) if failure.get("category", "").startswith("missing_")),
            "nonportable_reference_count": sum(1 for row in failures for failure in row.get("failures", []) if failure.get("category") == "nonportable_path_reference"),
            "unsafe_reference_count": sum(1 for row in failures for failure in row.get("failures", []) if failure.get("category") == "unsafe_path_reference"),
        },
        "fail_closed_rule": "If a compact control-plane JSON surface points to a missing, unsafe, or nonportable archive path, default to no publication and repair the reference before relying on operator navigation.",
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
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
