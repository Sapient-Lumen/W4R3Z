#!/usr/bin/env python3
"""Audit rev0074 packet-status authority and PB-01 artifact classification.

The audit intentionally excludes its generated inventory from the inventory it
measures, then recomputes after writing to catch self-referential drift.
"""
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
REVISION = "rev0074"
GENERATED = {
    "data/rev0074_pb01_artifact_inventory.csv",
    "data/rev0074_pb01_artifact_inventory.json",
    "data/rev0074_packet_status_audit.json",
    "evidence/rev0074-packet-status-audit.md",
}
REQUIRED_ACTIVE = {
    "README.md": ("PB-01A / U-168", "PB-01B / U-176", "selected patch: none"),
    "docs/START-HERE.md": ("PB-01A / U-168", "PB-01B / U-176", "Status authority"),
    "docs/PB01-CURRENT-DISPOSITION-REV0074.md": ("No selected patch", "retired as a defect", "superseded"),
    "docs/PACKET-DISPOSITION-LEDGER-REV0074.md": ("Open correctness/protocol-hardening research", "Retired as a defect"),
    "report_drafts/README.md": ("PB01-CURRENT-STATUS-REV0074.md", "superseded"),
    "report_drafts/PB01-CURRENT-STATUS-REV0074.md": ("no selected patch", "retired as a defect", "superseded"),
    "maintainer_artifacts/pb01/README.md": ("not selected", "four roles"),
    "workspace/NEXT-REVISION-QUEUE.md": ("SEARCH-RESP-01A", "Do not spend another turn"),
}
FORBIDDEN_ASSERTIONS = (
    re.compile(r"PB-01 is (?:promoted|production-ready|production-gated)", re.I),
    re.compile(r"PB-01[^\n]{0,100}selected patch is", re.I),
    re.compile(r"file PB-01.*private", re.I),
)
ARCHIVE_HASHES = {
    "docs/archive/rev0073-active-pb01/probe_rev0010_pb01_peer_binding.py": "9c8ca117d9b485407bb6e5f0fc113cf5065df974672dbb26ff35f9e6563be0da",
    "docs/archive/rev0073-active-pb01/test_peer_connection_primary_election_reproducer.py": "278003b1cab84e79f8a86ef89d09104871f6fc5c0fde4fbd2e91636cc0c93f5a",
    "docs/archive/rev0073-active-pb01/test_peer_connection_primary_election_fixed_regression.py": "5b02cbcab457fb964319dc57d5078d8be9444ca72ae71fe04893f633232fc8bb",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def is_pb01_path(relative: str) -> bool:
    low = relative.lower()
    name = Path(relative).name.lower()
    tokens = ("pb01", "pb-01", "peer-binding", "peer_binding", "primary-election", "primary_election")
    if any(token in low for token in tokens):
        return True
    # Patch-stack files can contain PB-01 while having a generic filename.
    if relative.startswith(("handoff/", "report_drafts/", "docs/", "tools/")):
        path = ROOT / relative
        if path.suffix.lower() in {".md", ".txt", ".py", ".diff", ".patch"} and path.stat().st_size <= 2_000_000:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return False
            return bool(re.search(r"\bPB-01\b|\bU-168\b|\bU-176\b", text))
    return False


def classify(relative: str) -> tuple[str, bool, str]:
    low = relative.lower()
    if relative.startswith("docs/archive/rev0073-active-pb01/"):
        return "archived-original", False, "pre-rev0074 active bytes preserved for provenance"
    if relative in {
        "README.md",
        "docs/START-HERE.md",
        "docs/PB01-CURRENT-DISPOSITION-REV0074.md",
        "docs/PB01-REACHABILITY-AND-COMPATIBILITY-AUDIT-REV0074.md",
        "docs/PB01-ARTIFACT-COHERENCE-REFACTOR-REV0074.md",
        "docs/CLAIM-EVIDENCE-LADDER-REV0074.md",
        "docs/PACKET-DISPOSITION-LEDGER-REV0074.md",
        "docs/SUPERSEDED-PACKET-INDEX-REV0074.md",
        "data/current_packet_dispositions.json",
        "data/rev0074_packet_dispositions.json",
        "maintainer_artifacts/pb01/README.md",
        "report_drafts/PB01-CURRENT-STATUS-REV0074.md",
        "workspace/NEXT-REVISION-QUEUE.md",
        "tools/probe_rev0074_pb01_disposition.py",
        "tools/audit_rev0074_packet_status.py",
        "tools/apply_pb01_origin_aware_patch_rev0074.py",
    } or relative.startswith(("maintainer_artifacts/pb01/test_pb01_", "maintainer_artifacts/pb01/pb01_harness.py", "data/rev0074_pb01_", "evidence/rev0074-pb01-", "handoff/rev0074/")):
        return "current-rev0074", True, "current authority, evidence, or explicitly unselected experiment"
    superseded_markers = (
        "rev0038", "production-ready", "selected-patch", "selected-fix",
        "strict-front-selected-stack", "pb-01-rev0059.patch",
    )
    if any(marker in low for marker in superseded_markers):
        return "superseded-experiment", False, "inherits or asserts the rev0038 blanket policy"
    if relative.startswith("handoff/"):
        return "duplicate-export", False, "historical handoff copy; current ledger overrides status"
    return "historical-evidence", False, "revision-scoped history; not current authority"


def collect_inventory() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in GENERATED or "/__pycache__/" in f"/{relative}/" or relative.endswith((".pyc", ".pyo")):
            continue
        if not is_pb01_path(relative):
            continue
        category, current, reason = classify(relative)
        rows.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "category": category,
            "current_authority": current,
            "reason": reason,
        })
    return rows


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    csv_path = ROOT / "data/rev0074_pb01_artifact_inventory.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["path"])
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "data/rev0074_pb01_artifact_inventory.json").write_bytes(canonical(rows))
    (ROOT / "data/rev0074_packet_status_audit.json").write_bytes(canonical(summary))
    lines = [
        "# rev0074 packet-status audit",
        "",
        f"Status: **{summary['status']}**",
        "",
        "```text",
        f"inventory rows: {summary['inventory_rows']}",
        f"current rows: {summary['category_counts'].get('current-rev0074', 0)}",
        f"superseded experiment rows: {summary['category_counts'].get('superseded-experiment', 0)}",
        f"duplicate hash groups: {summary['duplicate_hash_groups']}",
        f"duplicate bytes beyond one canonical copy: {summary['duplicate_wasted_bytes']}",
        f"active status checks: {summary['active_checks_passed']}/{summary['active_checks_total']}",
        f"archive hash checks: {summary['archive_hashes_passed']}/{summary['archive_hashes_total']}",
        f"self-reference stability: {summary['self_reference_stability']}",
        "```",
        "",
        "Historical PB-01 files remain in place but are explicitly non-authoritative. The current ledger has no selected PB-01 patch.",
    ]
    (ROOT / "evidence/rev0074-packet-status-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []

    ledger_path = ROOT / "data/current_packet_dispositions.json"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "fail", "errors": [f"ledger: {exc}"]}, indent=2))
        return 1
    by_id = {row["packet_id"]: row for row in ledger.get("packets", [])}
    expected = {
        "PB-01A/U-168": ("open-protocol-hardening-research", None, "not supported by current evidence"),
        "PB-01B/U-176": ("retired-as-defect-on-current-evidence", None, "not supported"),
    }
    for packet_id, (status, patch, route) in expected.items():
        row = by_id.get(packet_id)
        if row is None:
            errors.append(f"missing ledger packet {packet_id}")
            continue
        if row.get("status") != status: errors.append(f"{packet_id} status")
        if row.get("selected_patch") is not patch: errors.append(f"{packet_id} selected patch")
        if row.get("security_route") != route: errors.append(f"{packet_id} security route")

    active_checks = 0
    active_passed = 0
    for relative, phrases in REQUIRED_ACTIVE.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing active surface: {relative}")
            active_checks += len(phrases) + 1
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        for phrase in phrases:
            active_checks += 1
            if phrase.lower() in text.lower():
                active_passed += 1
            else:
                errors.append(f"active phrase missing: {relative}: {phrase}")
        for pattern in FORBIDDEN_ASSERTIONS:
            active_checks += 1
            if pattern.search(text):
                errors.append(f"forbidden current assertion: {relative}: {pattern.pattern}")
            else:
                active_passed += 1

    archive_passed = 0
    for relative, expected_hash in ARCHIVE_HASHES.items():
        path = ROOT / relative
        if path.is_file() and sha256(path) == expected_hash:
            archive_passed += 1
        else:
            errors.append(f"archive hash mismatch: {relative}")

    rows_before = collect_inventory()
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows_before:
        groups[row["sha256"]].append(row)
    duplicate_groups = [group for group in groups.values() if len(group) > 1]
    duplicate_wasted = sum(sum(int(row["bytes"]) for row in group) - int(group[0]["bytes"]) for group in duplicate_groups)
    category_counts: dict[str, int] = defaultdict(int)
    category_bytes: dict[str, int] = defaultdict(int)
    for row in rows_before:
        category_counts[row["category"]] += 1
        category_bytes[row["category"]] += int(row["bytes"])

    summary = {
        "revision": REVISION,
        "status": "pass",  # finalized after stability check
        "ledger_revision": ledger.get("revision"),
        "inventory_rows": len(rows_before),
        "inventory_sha256": hashlib.sha256(canonical(rows_before)).hexdigest(),
        "category_counts": dict(sorted(category_counts.items())),
        "category_bytes": dict(sorted(category_bytes.items())),
        "duplicate_hash_groups": len(duplicate_groups),
        "duplicate_wasted_bytes": duplicate_wasted,
        "active_checks_passed": active_passed,
        "active_checks_total": active_checks,
        "archive_hashes_passed": archive_passed,
        "archive_hashes_total": len(ARCHIVE_HASHES),
        "pb01a_selected_patch": by_id.get("PB-01A/U-168", {}).get("selected_patch"),
        "pb01b_selected_patch": by_id.get("PB-01B/U-176", {}).get("selected_patch"),
        "self_reference_stability": "pending",
        "errors": [],
    }

    if args.write_data:
        # Write the inventory, then prove generated outputs do not perturb it.
        write_outputs(rows_before, summary)
        rows_after = collect_inventory()
        stable = canonical(rows_before) == canonical(rows_after)
    else:
        stable = True
    summary["self_reference_stability"] = "pass" if stable else "fail"
    if not stable: errors.append("self-referential inventory drift")
    if active_passed != active_checks: errors.append("active status checks")
    if archive_passed != len(ARCHIVE_HASHES): errors.append("archive hashes")
    summary["errors"] = sorted(set(errors))
    summary["status"] = "pass" if not errors else "fail"
    if args.write_data:
        write_outputs(rows_before, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
