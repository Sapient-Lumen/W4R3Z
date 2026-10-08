#!/usr/bin/env python3
"""Audit rev0076 status authority and SEARCH-RESP-01B artifact duplication."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REVISION = "rev0076"
ARCHIVE = Path("docs/archive/rev0075-active-search-resp-buddy/test_search_response_buddy_scope_fixed_regression.py")
ARCHIVE_SHA256 = "6b4d9ae5e246e70bcbce34790938ba252fbdd970f0f06382279bb3e328935c86"
ACTIVE_FILES = (
    "buddy_search_harness.py",
    "test_search_resp_buddy_current_behavior.py",
    "test_search_resp_buddy_identity_counterexample.py",
    "test_search_resp_buddy_master_resend_epoch.py",
    "test_search_resp_buddy_rev0040_policy.py",
    "test_search_resp_buddy_snapshot_presence.py",
)
GENERATED = {
    "data/rev0076_search_resp_buddy_artifact_inventory.csv",
    "data/rev0076_search_resp_buddy_artifact_inventory.json",
    "data/rev0076_search_resp_buddy_duplicate_groups.csv",
    "data/rev0076_search_resp_buddy_duplicate_groups.json",
    "data/rev0076_status_authority_audit.json",
    "evidence/rev0076-status-authority-audit.md",
}
CURRENT_FILES = {
    "README.md": ("selected patch: none", "request epoch", "not supported by current evidence"),
    "docs/START-HERE.md": ("SEARCH-RESP-01B / U-163B", "wire PeerInit", "no selected patch"),
    "docs/SEARCH-RESP-01B-CURRENT-DISPOSITION-REV0076.md": (
        "not authentication", "request-epoch counterexample", "selected patch: none",
    ),
    "docs/SEARCH-RESP-01B-IDENTITY-AND-EPOCH-AUDIT-REV0076.md": (
        "Counterexample to authentication interpretation", "Counterexample to timeless-snapshot interpretation",
    ),
    "docs/PACKET-DISPOSITION-LEDGER-REV0076.md": (
        "open request-epoch design research", "none selected", "Schema",
    ),
    "docs/SUPERSEDED-PACKET-INDEX-REV0076.md": (
        "SEARCH-RESP-01B / U-163B", "superseded decision", "unselected experiment",
    ),
    "report_drafts/SEARCH-RESP-01B-CURRENT-STATUS-REV0076.md": (
        "selected patch: none", "wire PeerInit claim", "not supported by current evidence",
    ),
    "workspace/NEXT-REVISION-QUEUE.md": (
        "new-wire-token-per-resend", "request-epoch semantics", "private security routing",
    ),
}
FORBIDDEN = (
    re.compile(r"SEARCH-RESP-01B\s+is\s+(?:production[- ]ready|production[- ]gated)", re.I),
    re.compile(r"SEARCH-RESP-01B[^\n]{0,100}selected patch:\s*(?!none\b|null\b)", re.I),
    re.compile(r"the rev0040 guard\s+(?:authenticates|proves(?: the)? buddy identity)", re.I),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def metrics(paths: list[Path]) -> dict[str, int]:
    lines = bytes_total = long_lines = 0
    for path in paths:
        data = path.read_bytes()
        bytes_total += len(data)
        decoded = data.decode("utf-8")
        rows = decoded.splitlines()
        lines += len(rows)
        long_lines += sum(len(row) > 100 for row in rows)
    return {"files": len(paths), "lines": lines, "bytes": bytes_total, "lines_over_100": long_lines}


def related(relative: str) -> bool:
    low = relative.lower()
    return any(token in low for token in (
        "search-resp-01b", "search_resp_buddy", "search-response-buddy",
        "buddy_scope", "buddy-source", "buddy_source", "u-163b", "u163b",
    ))


def inventory(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in GENERATED or not related(rel):
            continue
        row = {"path": rel, "bytes": path.stat().st_size, "sha256": digest(path)}
        rows.append(row)
        groups[row["sha256"]].append(row)
    duplicates: list[dict[str, Any]] = []
    for sha, members in groups.items():
        if len(members) < 2:
            continue
        size = int(members[0]["bytes"])
        duplicates.append({
            "sha256": sha,
            "copies": len(members),
            "bytes_each": size,
            "wasted_bytes": size * (len(members) - 1),
            "paths": [str(row["path"]) for row in members],
        })
    duplicates.sort(key=lambda row: (-int(row["wasted_bytes"]), str(row["sha256"])))
    return rows, duplicates


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def audit(root: Path) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    add("revision marker", (root / "REVISION.txt").read_text().strip() == REVISION)
    for rel, phrases in CURRENT_FILES.items():
        path = root / rel
        add(f"current file exists: {rel}", path.is_file())
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            add(f"current phrase: {rel}: {phrase}", phrase.lower() in text.lower())
        for pattern in FORBIDDEN:
            add(f"no forbidden current claim: {rel}: {pattern.pattern}", pattern.search(text) is None)

    archive = root / ARCHIVE
    add("archived monolith exists", archive.is_file())
    add("archived monolith hash", archive.is_file() and digest(archive) == ARCHIVE_SHA256)
    active_dir = root / "maintainer_artifacts/search-resp-01"
    active = [active_dir / name for name in ACTIVE_FILES]
    add("all active role files exist", all(path.is_file() for path in active))
    add("old monolith absent from active", not (active_dir / "test_search_response_buddy_scope_fixed_regression.py").exists())
    observed = metrics(active) if all(path.is_file() for path in active) else {}
    add("active file count", observed.get("files") == 6, observed)
    add("active line count", observed.get("lines") == 167, observed)
    add("active byte count", observed.get("bytes") == 6504, observed)
    add("active long lines", observed.get("lines_over_100") == 0, observed)
    add("active smaller in lines", int(observed.get("lines", 9999)) < 212, observed)
    add("active no larger in bytes", int(observed.get("bytes", 9999)) <= 6556, observed)

    rows, duplicates = inventory(root)
    second_rows, second_duplicates = inventory(root)
    add("inventory self-stable", canonical(rows) == canonical(second_rows))
    add("duplicate inventory self-stable", canonical(duplicates) == canonical(second_duplicates))
    strong = [row for row in rows if re.search(r"PRODUCTION|SELECTED.PATCH|SELECTED.FIX", str(row["path"]), re.I)]
    add("historical strong artifacts retained", len(strong) > 0, len(strong))

    result = {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "artifact_files": len(rows),
        "artifact_bytes": sum(int(row["bytes"]) for row in rows),
        "duplicate_hash_groups": len(duplicates),
        "duplicate_wasted_bytes": sum(int(row["wasted_bytes"]) for row in duplicates),
        "historical_strong_name_files": len(strong),
        "active_metrics": observed,
        "archive_sha256": digest(archive) if archive.is_file() else None,
        "self_reference_stability": "pass" if canonical(rows) == canonical(second_rows) and canonical(duplicates) == canonical(second_duplicates) else "fail",
        "checks": checks,
        "errors": errors,
    }
    result["_inventory"] = rows
    result["_duplicates"] = duplicates
    return result


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    rows = result.pop("_inventory")
    duplicates = result.pop("_duplicates")
    data = root / "data"
    evidence = root / "evidence"
    data.mkdir(exist_ok=True)
    evidence.mkdir(exist_ok=True)
    (data / "rev0076_status_authority_audit.json").write_text(canonical(result), encoding="utf-8")
    (data / "rev0076_search_resp_buddy_artifact_inventory.json").write_text(canonical(rows), encoding="utf-8")
    (data / "rev0076_search_resp_buddy_duplicate_groups.json").write_text(canonical(duplicates), encoding="utf-8")
    with (data / "rev0076_search_resp_buddy_artifact_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("path", "bytes", "sha256"))
        writer.writeheader()
        writer.writerows(rows)
    with (data / "rev0076_search_resp_buddy_duplicate_groups.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("sha256", "copies", "bytes_each", "wasted_bytes", "paths"))
        writer.writeheader()
        for row in duplicates:
            flat = dict(row)
            flat["paths"] = " | ".join(row["paths"])
            writer.writerow(flat)
    lines = [
        "# rev0076 status-authority audit",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"checks: {result['checks_passed']}/{result['checks_total']}",
        f"SEARCH-RESP-01B-related files: {result['artifact_files']}",
        f"related bytes: {result['artifact_bytes']}",
        f"exact duplicate groups: {result['duplicate_hash_groups']}",
        f"redundant exact-copy bytes: {result['duplicate_wasted_bytes']}",
        f"historical strong-name files retained: {result['historical_strong_name_files']}",
        f"self-reference stability: {result['self_reference_stability']}",
        "```",
        "",
        "Historical strong filenames are retained as provenance; the validated current ledger controls status.",
    ]
    (evidence / "rev0076-status-authority-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = audit(root)
    if args.write_data:
        write_outputs(root, result)
        stable = audit(root)
        stable.pop("_inventory", None)
        stable.pop("_duplicates", None)
        if canonical(stable) != canonical(result):
            result["status"] = "fail"
            result["errors"].append("post-write self-reference instability")
            write_outputs(root, {**result, "_inventory": inventory(root)[0], "_duplicates": inventory(root)[1]})
    else:
        result.pop("_inventory", None)
        result.pop("_duplicates", None)
    print(canonical(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
