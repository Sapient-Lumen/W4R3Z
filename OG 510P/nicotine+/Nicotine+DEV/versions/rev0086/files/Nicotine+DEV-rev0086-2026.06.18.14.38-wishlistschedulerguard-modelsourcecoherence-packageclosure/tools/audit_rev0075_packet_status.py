#!/usr/bin/env python3
"""Audit rev0075 SEARCH-RESP authority, artifact roles, and status coherence.

Generated inventory files are excluded from the measured set. When --write-data
is used, the inventory is recomputed after writing and must remain byte-stable.
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
REVISION = "rev0075"
GENERATED = {
    "data/rev0075_search_resp_artifact_inventory.csv",
    "data/rev0075_search_resp_artifact_inventory.json",
    "data/rev0075_packet_status_audit.json",
    "evidence/rev0075-packet-status-audit.md",
    "data/rev0075_search_resp_duplicate_groups.csv",
    "data/rev0075_search_resp_duplicate_groups.json",
}
REQUIRED_ACTIVE = {
    "README.md": (
        "SEARCH-RESP-01A",
        "claimed-name filter",
        "selected patch: none",
        "not supported by current evidence",
    ),
    "docs/START-HERE.md": (
        "SEARCH-RESP-01A / U-163A",
        "wire PeerInit",
        "no selected patch",
        "Status authority",
    ),
    "docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md": (
        "confirmed local request-scope consistency gap",
        "not proof of peer identity",
        "selected patch: none",
        "private security route: not supported by current evidence",
    ),
    "docs/SEARCH-RESP-01A-IDENTITY-AND-REACHABILITY-AUDIT-REV0075.md": (
        "counterexample to authentication interpretation",
        "Token model",
        "no selected patch",
    ),
    "docs/PACKET-DISPOSITION-LEDGER-REV0075.md": (
        "open defense-in-depth research",
        "none selected",
        "Not supported by current evidence",
    ),
    "docs/SUPERSEDED-PACKET-INDEX-REV0075.md": (
        "superseded decision",
        "unselected defense-in-depth experiment",
        "Current SEARCH-RESP-01A authority",
    ),
    "report_drafts/README.md": (
        "SEARCH-RESP-01A-CURRENT-STATUS-REV0075.md",
        "unselected claimed-name defense-in-depth experiment",
    ),
    "report_drafts/SEARCH-RESP-01A-CURRENT-STATUS-REV0075.md": (
        "selected patch: none",
        "wire PeerInit claim",
        "not supported by current evidence",
    ),
    "maintainer_artifacts/search-resp-01/README.md": (
        "evidence by role",
        "test_search_resp_identity_counterexample.py",
        "research-only",
    ),
    "workspace/NEXT-REVISION-QUEUE.md": (
        "SEARCH-RESP-01B-BUDDY",
        "Add an expected-name `PeerInit` spoof counterexample",
        "private security routing",
    ),
}
FORBIDDEN_ASSERTIONS = (
    re.compile(r"SEARCH-RESP-01A\s+is\s+(?:production[- ]ready|production[- ]gated)", re.I),
    re.compile(r"SEARCH-RESP-01A[^\n]{0,120}selected patch:\s*(?!none\b|null\b)", re.I),
    re.compile(r"SEARCH-RESP-01A[^\n]{0,120}private security route:\s*(?:supported|file|yes)\b", re.I),
    re.compile(r"the rev0039 guard\s+(?:authenticates|proves the identity of)", re.I),
)
ARCHIVE_HASHES = {
    "docs/archive/rev0074-active-search-resp-01/test_search_response_scope_and_parse_order_reproducer.py":
        "d7f98b7fca31085e10df98782ebd824e4d10e950567b5826079a4fa2f6507e6e",
    "docs/archive/rev0074-active-search-resp-01/test_search_response_user_scope_fixed_regression.py":
        "fc91da0e93f9086f0193e7d2903b56f06e0d5978c730c9295b02989a3966a9c1",
}
CURRENT_EXACT = {
    "README.md",
    "docs/START-HERE.md",
    "docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md",
    "docs/SEARCH-RESP-01A-IDENTITY-AND-REACHABILITY-AUDIT-REV0075.md",
    "docs/SEARCH-RESP-ARTIFACT-COHERENCE-REFACTOR-REV0075.md",
    "docs/CLAIM-EVIDENCE-LADDER-REV0075.md",
    "docs/PACKET-DISPOSITION-LEDGER-REV0075.md",
    "docs/SUPERSEDED-PACKET-INDEX-REV0075.md",
    "docs/PACKAGE-COHERENCE-GATE-REV0075.md",
    "data/current_packet_dispositions.json",
    "data/rev0075_packet_dispositions.json",
    "maintainer_artifacts/search-resp-01/README.md",
    "report_drafts/README.md",
    "report_drafts/SEARCH-RESP-01A-CURRENT-STATUS-REV0075.md",
    "workspace/NEXT-REVISION-QUEUE.md",
    "tools/probe_rev0075_search_resp_disposition.py",
    "tools/audit_rev0075_packet_status.py",
    "tools/apply_search_resp_user_scope_patch_rev0039.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def is_search_resp_path(relative: str) -> bool:
    low = relative.lower()
    tokens = (
        "search-resp",
        "search_resp",
        "search-response",
        "search_response",
        "searchresp",
        "u-163",
        "u163",
    )
    if any(token in low for token in tokens):
        return True
    if relative.startswith(("handoff/", "report_drafts/", "docs/", "tools/", "workspace/")):
        path = ROOT / relative
        if path.suffix.lower() in {".md", ".txt", ".py", ".diff", ".patch"} and path.stat().st_size <= 2_000_000:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return False
            return bool(re.search(r"\bSEARCH-RESP-01A\b|\bU-163A?\b", text, re.I))
    return False


def is_adjacent_packet(relative: str) -> bool:
    low = relative.lower()
    adjacent = (
        "01b", "buddy", "01c", "room-scope", "room_scope",
        "prefix-budget", "prefix_budget", "result-budget", "result_budget",
        "parse-budget", "parse_budget",
    )
    return any(token in low for token in adjacent) and "01a" not in low


def classify(relative: str) -> tuple[str, bool, str]:
    low = relative.lower()
    if relative.startswith("docs/archive/rev0074-active-search-resp-01/"):
        return "archived-original", False, "pre-rev0075 active bytes preserved for provenance"
    if (
        relative in CURRENT_EXACT
        or relative.startswith("maintainer_artifacts/search-resp-01/test_search_resp_")
        or relative == "maintainer_artifacts/search-resp-01/search_resp_harness.py"
        or relative.startswith("data/rev0075_search_resp_")
        or relative.startswith("evidence/rev0075-search-resp-")
        or relative.startswith("handoff/rev0075/")
    ):
        return "current-rev0075", True, "current authority, role-classified evidence, or explicit unselected experiment"
    if is_adjacent_packet(relative):
        return "adjacent-unreviewed-packet", False, "related SEARCH-RESP packet not adjudicated by rev0075"
    strong_markers = (
        "production-ready",
        "production_ready",
        "production-gate",
        "production_gate",
        "selected-patch",
        "selected_patch",
        "selected-fix",
        "selected_fix",
    )
    if any(marker in low for marker in strong_markers):
        return "superseded-strong-status", False, "historical strong-status language; current ledger selects no patch"
    if relative.startswith("handoff/"):
        return "duplicate-export", False, "historical handoff copy; current ledger overrides status"
    if any(marker in low for marker in ("rev0056", "rev0058", "roundtrip", "rerun", "patch-stack", "patch_stack")):
        return "mechanical-rerun", False, "historical mechanical evidence without current disposition authority"
    return "historical-evidence", False, "revision-scoped provenance; not current authority"


def collect_inventory() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in GENERATED or "/__pycache__/" in f"/{relative}/" or relative.endswith((".pyc", ".pyo")):
            continue
        if not is_search_resp_path(relative):
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


def write_outputs(
    rows: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    csv_path = ROOT / "data/rev0075_search_resp_artifact_inventory.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["path"])
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "data/rev0075_search_resp_artifact_inventory.json").write_bytes(canonical(rows))
    duplicate_csv = ROOT / "data/rev0075_search_resp_duplicate_groups.csv"
    with duplicate_csv.open("w", newline="", encoding="utf-8") as handle:
        fields = list(duplicate_rows[0]) if duplicate_rows else ["sha256"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(duplicate_rows)
    (ROOT / "data/rev0075_search_resp_duplicate_groups.json").write_bytes(canonical(duplicate_rows))
    (ROOT / "data/rev0075_packet_status_audit.json").write_bytes(canonical(summary))
    lines = [
        "# rev0075 packet-status audit",
        "",
        f"Status: **{summary['status']}**",
        "",
        "```text",
        f"inventory rows: {summary['inventory_rows']}",
        f"current rows: {summary['category_counts'].get('current-rev0075', 0)}",
        f"superseded strong-status rows: {summary['category_counts'].get('superseded-strong-status', 0)}",
        f"adjacent unreviewed rows: {summary['category_counts'].get('adjacent-unreviewed-packet', 0)}",
        f"duplicate hash groups: {summary['duplicate_hash_groups']}",
        f"duplicate bytes beyond one canonical copy: {summary['duplicate_wasted_bytes']}",
        f"active status checks: {summary['active_checks_passed']}/{summary['active_checks_total']}",
        f"archive hash checks: {summary['archive_hashes_passed']}/{summary['archive_hashes_total']}",
        f"self-reference stability: {summary['self_reference_stability']}",
        "```",
        "",
        "Historical SEARCH-RESP files remain addressable but are non-authoritative. The current ledger selects no SEARCH-RESP-01A patch.",
    ]
    (ROOT / "evidence/rev0075-packet-status-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []

    try:
        ledger = json.loads((ROOT / "data/current_packet_dispositions.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "fail", "errors": [f"ledger: {exc}"]}, indent=2))
        return 1
    by_id = {row["packet_id"]: row for row in ledger.get("packets", [])}
    row = by_id.get("SEARCH-RESP-01A/U-163A")
    if row is None:
        errors.append("missing ledger packet SEARCH-RESP-01A/U-163A")
    else:
        if row.get("status") != "open-defense-in-depth-research":
            errors.append("SEARCH-RESP-01A status")
        if row.get("selected_patch") is not None:
            errors.append("SEARCH-RESP-01A selected patch")
        if row.get("security_route") != "not supported by current evidence":
            errors.append("SEARCH-RESP-01A security route")
        if row.get("current_document") != "docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md":
            errors.append("SEARCH-RESP-01A current document")
    if ledger.get("revision") != REVISION:
        errors.append("ledger revision")

    active_checks = 0
    active_passed = 0
    for relative, phrases in REQUIRED_ACTIVE.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing active surface: {relative}")
            active_checks += len(phrases) + len(FORBIDDEN_ASSERTIONS)
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
    for inventory_row in rows_before:
        groups[inventory_row["sha256"]].append(inventory_row)
    duplicate_groups = [group for group in groups.values() if len(group) > 1]
    duplicate_rows = []
    for group in duplicate_groups:
        one_bytes = int(group[0]["bytes"])
        duplicate_rows.append({
            "sha256": group[0]["sha256"],
            "file_count": len(group),
            "bytes_each": one_bytes,
            "total_bytes": one_bytes * len(group),
            "wasted_bytes": one_bytes * (len(group) - 1),
            "categories": " | ".join(sorted({str(item["category"]) for item in group})),
            "paths": " | ".join(str(item["path"]) for item in sorted(group, key=lambda item: str(item["path"]))),
        })
    duplicate_rows.sort(key=lambda item: (-int(item["wasted_bytes"]), str(item["sha256"])))
    duplicate_wasted = sum(
        sum(int(item["bytes"]) for item in group) - int(group[0]["bytes"])
        for group in duplicate_groups
    )
    category_counts: dict[str, int] = defaultdict(int)
    category_bytes: dict[str, int] = defaultdict(int)
    for inventory_row in rows_before:
        category_counts[inventory_row["category"]] += 1
        category_bytes[inventory_row["category"]] += int(inventory_row["bytes"])

    summary = {
        "revision": REVISION,
        "status": "pass",
        "ledger_revision": ledger.get("revision"),
        "inventory_rows": len(rows_before),
        "inventory_sha256": hashlib.sha256(canonical(rows_before)).hexdigest(),
        "category_counts": dict(sorted(category_counts.items())),
        "category_bytes": dict(sorted(category_bytes.items())),
        "duplicate_hash_groups": len(duplicate_groups),
        "duplicate_wasted_bytes": duplicate_wasted,
        "largest_duplicate_groups": duplicate_rows[:10],
        "active_checks_passed": active_passed,
        "active_checks_total": active_checks,
        "archive_hashes_passed": archive_passed,
        "archive_hashes_total": len(ARCHIVE_HASHES),
        "search_resp_selected_patch": row.get("selected_patch") if row else "missing",
        "search_resp_security_route": row.get("security_route") if row else "missing",
        "self_reference_stability": "pending",
        "errors": [],
    }

    if args.write_data:
        write_outputs(rows_before, duplicate_rows, summary)
        rows_after = collect_inventory()
        stable = canonical(rows_before) == canonical(rows_after)
    else:
        stable = True
    summary["self_reference_stability"] = "pass" if stable else "fail"
    if not stable:
        errors.append("self-referential inventory drift")
    if active_passed != active_checks:
        errors.append("active status checks")
    if archive_passed != len(ARCHIVE_HASHES):
        errors.append("archive hashes")
    summary["errors"] = sorted(set(errors))
    summary["status"] = "pass" if not errors else "fail"
    if args.write_data:
        write_outputs(rows_before, duplicate_rows, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
