#!/usr/bin/env python3
"""Audit the cube's upstream-use boundary and U-123 duplicate semantics.

Historical files are inventoried, not rewritten.  Only current entrypoints and
artifact landing pages are policy-gated.  Exact duplicate bytes are not assumed
to be disposable when their paths carry distinct handoff or evidence provenance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REVISION = "rev0073"
TEXT_SUFFIXES = {
    ".md", ".txt", ".csv", ".json", ".jsonl", ".py", ".patch", ".diff",
    ".toml", ".yaml", ".yml", ".sh", ".ini", ".rst",
}
SENSITIVE_PATTERNS = {
    "production-ready": re.compile(r"production[ -]ready", re.I),
    "maintainer-ready": re.compile(r"maintainer[ -]ready", re.I),
    "filing-ready": re.compile(r"filing[ -]ready", re.I),
}
ACTIVE_SURFACES = (
    "README.md",
    "docs/START-HERE.md",
    "workspace/NEXT-REVISION-QUEUE.md",
    "maintainer_artifacts/README.md",
    "maintainer_artifacts/u123/README.md",
    "report_drafts/README.md",
)
U123_PATTERNS = ("test_downloads_duplicate_transfer_token*.py",)
GENERATED_EXCLUSIONS = {
    "data/rev0073_submission_language_inventory.csv",
    "data/rev0073_submission_language_inventory.json",
    "data/rev0073_u123_duplicate_semantics.csv",
    "data/rev0073_u123_duplicate_semantics.json",
    "data/rev0073_research_boundary_summary.json",
    "tools/audit_rev0073_research_boundary.py",
}



def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["status"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def iter_text_files() -> list[Path]:
    output: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in GENERATED_EXCLUSIONS:
            continue
        output.append(path)
    return sorted(output)


def classify_path(relative: str) -> str:
    if relative in ACTIVE_SURFACES or relative.startswith("docs/") and "REV0073" in relative.upper():
        return "current-active"
    if relative.startswith("handoff/rev0073/"):
        return "current-active"
    if relative.startswith(("evidence/", "handoff/", "data/", "docs/archive/")):
        return "historical-or-evidence"
    if relative.startswith("report_drafts/"):
        return "historical-report-draft"
    return "other-history"


def policy_inventory() -> tuple[list[dict[str, Any]], Counter[str], list[str]]:
    rows: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    errors: list[str] = []
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT).as_posix()
        for label, pattern in SENSITIVE_PATTERNS.items():
            count = len(pattern.findall(text))
            if not count:
                continue
            rows.append({
                "path": relative,
                "classification": classify_path(relative),
                "term": label,
                "occurrences": count,
                "action": "preserve as history; do not treat label as current upstream-use authorization",
            })
            totals[label] += count

    forbidden_active = set(ACTIVE_SURFACES)
    for relative in ACTIVE_SURFACES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing active boundary surface: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"current surface retains legacy readiness label {label}: {relative}")

    required_fragments = {
        "README.md": ("research-only",),
        "docs/START-HERE.md": ("research-only",),
        "maintainer_artifacts/README.md": ("research-only", "independent human"),
        "report_drafts/README.md": ("research-only", "independent human"),
        "maintainer_artifacts/u123/README.md": ("classified state matrix", "superseded"),
    }
    for relative, fragments in required_fragments.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        lowered = path.read_text(encoding="utf-8").lower()
        for fragment in fragments:
            if fragment.lower() not in lowered:
                errors.append(f"missing boundary phrase {fragment!r}: {relative}")

    return rows, totals, errors


def duplicate_semantics() -> list[dict[str, Any]]:
    candidates: set[Path] = set()
    for pattern in U123_PATTERNS:
        candidates.update(path for path in ROOT.rglob(pattern) if path.is_file())

    hashes: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(candidates):
        hashes[sha256_path(path)].append(path)

    rows: list[dict[str, Any]] = []
    for digest, paths in sorted(hashes.items()):
        group_size = len(paths)
        for path in sorted(paths):
            relative = path.relative_to(ROOT).as_posix()
            if relative.startswith("maintainer_artifacts/u123/"):
                purpose = "current readable research artifact"
            elif relative.startswith("docs/archive/rev0072-active-u123/"):
                purpose = "byte-preserved rev0072 active-packet archive"
            elif relative.startswith("handoff/"):
                purpose = "revision-scoped handoff/provenance copy"
            elif relative.startswith("evidence/"):
                purpose = "revision-scoped runtime evidence copy"
            else:
                purpose = "other historical research copy"

            rows.append({
                "sha256": digest,
                "bytes": path.stat().st_size,
                "matching_path": relative,
                "exact_group_size": group_size,
                "semantic_purpose": purpose,
                "delete_recommendation": "preserve" if group_size > 1 else "not-an-exact-duplicate",
                "reason": (
                    "revision path records provenance or archive identity; byte identity alone is not safe deletion evidence"
                    if group_size > 1
                    else "unique within the U-123 filename family"
                ),
            })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="rev0073 research boundary and duplicate-semantics audit")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()

    inventory_rows, totals, errors = policy_inventory()
    duplicate_rows = duplicate_semantics()
    idempotence_verified = True

    if args.write_data:
        write_csv(ROOT / "data" / "rev0073_submission_language_inventory.csv", inventory_rows)
        write_json(ROOT / "data" / "rev0073_submission_language_inventory.json", inventory_rows)
        write_csv(ROOT / "data" / "rev0073_u123_duplicate_semantics.csv", duplicate_rows)
        write_json(ROOT / "data" / "rev0073_u123_duplicate_semantics.json", duplicate_rows)

        inventory_check, totals_check, errors_check = policy_inventory()
        duplicate_check = duplicate_semantics()
        idempotence_verified = (
            inventory_check == inventory_rows
            and totals_check == totals
            and errors_check == errors
            and duplicate_check == duplicate_rows
        )
        if not idempotence_verified:
            errors.append("audit outputs changed their own inventory or duplicate result")

    duplicate_groups = len({row["sha256"] for row in duplicate_rows if int(row["exact_group_size"]) > 1})
    exact_copy_rows = sum(1 for row in duplicate_rows if int(row["exact_group_size"]) > 1)

    summary = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "active_surfaces": list(ACTIVE_SURFACES),
        "generated_inventory_exclusions": sorted(GENERATED_EXCLUSIONS),
        "idempotence_verified": idempotence_verified,
        "historical_sensitive_term_totals": dict(sorted(totals.items())),
        "files_with_sensitive_terms": len({row["path"] for row in inventory_rows}),
        "inventory_rows": len(inventory_rows),
        "u123_exact_duplicate_groups": duplicate_groups,
        "u123_exact_copy_rows": exact_copy_rows,
        "u123_safe_deletions_identified": 0,
        "duplicate_decision": "preserve provenance-bearing copies; refactor navigation and classification instead of deleting by hash",
        "boundary_decision": "all generated patches, tests, and reports are research-only and require independent human reproduction/authorship before upstream use",
        "errors": errors,
    }

    if args.write_data:
        write_json(ROOT / "data" / "rev0073_research_boundary_summary.json", summary)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
