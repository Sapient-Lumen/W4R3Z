#!/usr/bin/env python3
"""Check ASSURANCE_ARTIFACTS.json / .md parity and path existence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

from render_assurance_artifacts import render


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    catalog_path = root / "ASSURANCE_ARTIFACTS.json"
    markdown_path = root / "ASSURANCE_ARTIFACTS.md"
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    catalog: dict[str, Any] = {}
    if not catalog_path.exists():
        failures.append({"category": "catalog_json_missing", "path": "ASSURANCE_ARTIFACTS.json"})
    else:
        catalog = load_json(catalog_path)
        if catalog.get("generated_for_revision") != release["revision"]:
            failures.append({"category": "catalog_revision_mismatch", "actual": catalog.get("generated_for_revision"), "expected": release["revision"]})

    expected_md = render(catalog) if catalog else ""
    actual_md = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
    if not markdown_path.exists():
        failures.append({"category": "catalog_markdown_missing", "path": "ASSURANCE_ARTIFACTS.md"})
    elif actual_md != expected_md:
        failures.append({
            "category": "catalog_markdown_drift",
            "path": "ASSURANCE_ARTIFACTS.md",
            "expected_sha256": sha256_text(expected_md),
            "actual_sha256": sha256_text(actual_md),
        })

    groups = catalog.get("groups", []) if isinstance(catalog.get("groups", []), list) else []
    seen_paths: list[str] = []
    missing_paths: list[str] = []
    duplicate_paths: list[str] = []
    seen_set: set[str] = set()
    for group in groups:
        if not isinstance(group, dict):
            failures.append({"category": "malformed_group", "group": repr(group)[:200]})
            continue
        paths = group.get("paths", [])
        if not isinstance(paths, list):
            failures.append({"category": "malformed_group_paths", "group_id": group.get("id")})
            continue
        for path in paths:
            rel = str(path)
            seen_paths.append(rel)
            if rel in seen_set:
                duplicate_paths.append(rel)
            seen_set.add(rel)
            if rel.endswith("/"):
                if not (root / rel).is_dir():
                    missing_paths.append(rel)
            elif not (root / rel).exists():
                missing_paths.append(rel)

    if missing_paths:
        failures.append({"category": "catalog_path_missing", "count": len(missing_paths), "paths": sorted(missing_paths)[:80]})
    duplicate_unique_paths = sorted(set(duplicate_paths))

    expected_required = {
        "ASSURANCE_ARTIFACTS.json",
        "ASSURANCE_ARTIFACTS.md",
        "reports/assurance_catalog_integrity.json",
        "publishing/check_assurance_catalog.py",
        "publishing/render_assurance_artifacts.py",
    }
    # The catalog should visibly include its own checker/renderer/report once this
    # invariant exists.  The JSON itself may be listed in the identity group or an
    # integrity group; only membership matters here.
    missing_required = sorted(expected_required - seen_set)
    if missing_required:
        failures.append({"category": "required_assurance_surface_not_cataloged", "paths": missing_required})

    summary = {
        "checks_failed": len(failures),
        "warning_count": len(warnings),
        "group_count": len(groups),
        "catalog_path_count": len(seen_paths),
        "unique_catalog_path_count": len(seen_set),
        "missing_path_count": len(missing_paths),
        "duplicate_path_count": len(duplicate_paths),
        "duplicate_unique_path_count": len(duplicate_unique_paths),
        "duplicate_catalog_paths_are_cross_group_memberships": True,
        "markdown_matches_json": actual_md == expected_md and bool(actual_md),
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "catalog_json": "ASSURANCE_ARTIFACTS.json",
        "catalog_markdown": "ASSURANCE_ARTIFACTS.md",
        "failures": failures[:80],
        "warnings": warnings[:80],
        "summary": summary,
        "fail_closed_rule": "If the assurance catalog Markdown drifts from JSON, or cataloged paths are missing, default to no publication and regenerate the catalog before relying on assurance surfaces. Duplicate path appearances are tracked as intentional cross-group memberships, not warnings.",
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
