#!/usr/bin/env python3
"""Validate rev0851 mission-alignment and cloudtainer-waste review surfaces."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"mission-alignment-waste-rev0851: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(rel: str) -> dict:
    try:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        fail(f"invalid JSON in {rel}: {exc}")
    if not isinstance(data, dict):
        fail(f"{rel} must be a JSON object")
    return data


def require_text(rel: str, snippets: list[str]) -> str:
    path = ROOT / rel
    if not path.is_file() or path.is_symlink():
        fail(f"missing regular file: {rel}")
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        fail(f"{rel} must end with a newline")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        fail(f"{rel} missing required snippets: {missing}")
    return text


def main() -> int:
    audit = load_json("AUDIT/MISSION_ALIGNMENT_WASTE_ROADMAP_REV0851.json")
    review = load_json("SESSION_REVIEW_REV0851.json")
    rights = load_json("RIGHTS/component_license_ledger.json")
    release = load_json("RELEASE_MANIFEST.json")

    if audit.get("status") != "mission_alignment_review_publication_block_preserved":
        fail("unexpected audit status")
    if review.get("not_publication_ready") is not True:
        fail("session review must preserve publication block")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights ledger no longer records the expected publication block")
    blockers = {row.get("id") for row in rights.get("blocking_findings", [])}
    required_blockers = {"missing_root_license_or_notice", "missing_local_license_reference_targets"}
    if not required_blockers.issubset(blockers):
        fail(f"rights blockers changed unexpectedly: {sorted(blockers)}")
    if release.get("revision") != "rev0826":
        fail("expected carried canonical release manifest revision rev0826 for overlay/canonical split check")

    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"rev0851 must not invent root rights sentinel: {sentinel}")

    require_text(
        "AUDIT/MISSION_ALIGNMENT_WASTE_ROADMAP_REV0851.md",
        ["Heart of the mission", "What is missing", "Speculative read", "Research notes"],
    )
    require_text(
        "SESSION_REVIEW_REV0851.md",
        ["Heart of the mission", "What changed in rev0851", "publication-blocked"],
    )
    require_text(
        "OVERLAY_COMMANDS.md",
        ["Do not use `make gate`", "validate_overlay_bundle_integrity_rev0848.py", "validate_mission_alignment_waste_rev0851.py"],
    )
    require_text(
        "README.md",
        ["EvidenceVault rev0851 mission/waste audit overlay bundle", "Use these overlay checks first", "Do **not** treat `make gate`"],
    )

    metrics = audit.get("metrics", {})
    if metrics.get("spdx_package_count") != 0:
        fail("expected current carried SPDX package count to remain zero for this audit")
    if metrics.get("canonical_manifest_paths_missing_from_overlay", 0) < 4000:
        fail("overlay/canonical split metric unexpectedly low")
    if metrics.get("dedupe_duplicate_extra_bytes", 0) <= 0:
        fail("dedupe waste metric missing")

    print("mission-alignment-waste-rev0851: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
