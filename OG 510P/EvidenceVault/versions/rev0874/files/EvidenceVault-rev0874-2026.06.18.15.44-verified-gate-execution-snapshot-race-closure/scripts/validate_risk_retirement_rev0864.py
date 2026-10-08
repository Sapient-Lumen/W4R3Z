#!/usr/bin/env python3
"""Validate the rev0864 rights-byte recovery and operational refactor."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
LICENSE_REL = "sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE"
README_REL = "sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md"
LICENSE_SHA = "0382b0057770ca05e9c350a50aa3b1c1fea84da0bc81d723bf00b9aa841be58a"
LICENSE_BYTES = 12227
README_SHA = "0f7174a89094f7695b899fad71c2e6d0fb12cd6041734d779aacd8a8bfe400c2"
README_BYTES = 356744
COMMIT = "f4244583a6af9425633e433a3eec000d23f4e011"


def fail(message: str) -> None:
    print(f"risk-retirement-rev0864: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        fail(f"missing or unsafe JSON surface: {rel}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {rel}: {exc}")
    if not isinstance(value, dict):
        fail(f"{rel} must contain a JSON object")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_exact_license() -> None:
    path = ROOT / LICENSE_REL
    if path.is_symlink() or not path.is_file():
        fail(f"recovered license is missing or unsafe: {LICENSE_REL}")
    if path.stat().st_size != LICENSE_BYTES or digest(path) != LICENSE_SHA:
        fail("recovered license identity mismatch")
    text = path.read_text(encoding="utf-8")
    for token in ("licensing transition", "Apache-2.0", "CC-BY-4.0", "MIT License"):
        if token not in text:
            fail(f"recovered license is missing expected transition token: {token}")


def assert_readme_index_identity() -> None:
    rows = []
    with (ROOT / "INDEX/files.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("path") == README_REL:
                rows.append(row)
    if len(rows) != 1:
        fail(f"expected one canonical index row for {README_REL}, found {len(rows)}")
    row = rows[0]
    if int(row.get("size", -1)) != README_BYTES or row.get("sha256") != README_SHA:
        fail("canonical README index identity changed or is malformed")


def assert_recovery_surfaces() -> None:
    recovery = load_json("RIGHTS/MCP_SERVERS_LICENSE_RECOVERY_REV0864.json")
    if recovery.get("status") != "exact_upstream_snapshot_identified_and_referenced_license_bytes_recovered":
        fail("upstream recovery status is not closed")
    upstream = recovery.get("upstream", {})
    if upstream.get("commit") != COMMIT:
        fail("upstream recovery commit is not pinned to the expected full SHA")
    readme = recovery.get("archived_readme_identity", {})
    if readme.get("indexed_sha256") != README_SHA or readme.get("exact_byte_identity_match") is not True:
        fail("README exact-identity evidence is missing")
    recovered = recovery.get("recovered_license_identity", {})
    if recovered.get("archive_path") != LICENSE_REL or recovered.get("sha256") != LICENSE_SHA:
        fail("recovered license evidence does not identify the embedded bytes")
    profile = recovery.get("license_text_profile", {})
    if profile.get("component_license_conclusion") != "NOASSERTION":
        fail("recovery evidence improperly promotes a component license conclusion")

    audit = load_json("RIGHTS/license_reference_integrity_audit.json")
    if audit.get("status") != "license_references_locally_resolved":
        fail("local reference audit remains blocked")
    if audit.get("local_references_missing") != 0 or audit.get("local_references_ok") != 1:
        fail("local reference counts do not reflect the exact recovery")
    refs = audit.get("references")
    if not isinstance(refs, list) or len(refs) != 1 or refs[0].get("resolved_archive_path") != LICENSE_REL or refs[0].get("status") != "ok":
        fail("local reference audit does not preserve the resolved path")


def assert_rights_block_narrowed_not_erased() -> None:
    ledger = load_json("RIGHTS/component_license_ledger.json")
    blockers = ledger.get("blocking_findings")
    if not isinstance(blockers, list) or [x.get("id") for x in blockers if isinstance(x, dict)] != ["missing_root_license_or_notice"]:
        fail("rights ledger must retain exactly the root-rights blocker")
    if ledger.get("missing_or_outside_local_license_reference_count") != 0:
        fail("rights ledger still reports a missing local reference")
    if ledger.get("root_license_or_notice_file_present") is not False or ledger.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights ledger erased or weakened the root publication block")
    pact = next((row for row in ledger.get("components", []) if isinstance(row, dict) and row.get("component_id") == "pact"), None)
    if not pact or pact.get("license_concluded") != "NOASSERTION" or pact.get("observed_file_count_under_existing_paths") != 648:
        fail("PACT ledger row does not preserve NOASSERTION with the one-file delta")
    for name in ("LICENSE", "LICENSE.md", "COPYING", "NOTICE"):
        if (ROOT / name).exists() or (ROOT / name).is_symlink():
            fail(f"rev0864 must not invent root rights file: {name}")

    evidence = load_json("RIGHTS/license_evidence_scan.json")
    counts = evidence.get("summary", {}).get("aggregate_finding_counts", {})
    if counts.get("referenced_license_file_present") != 1 or "referenced_license_file_missing" in counts:
        fail("rights evidence scan does not replace missing-reference evidence with present-reference evidence")

    packet = load_json("RIGHTS/RIGHTS_DECISION_PACKET_REV0864.json")
    if packet.get("missing_or_outside_local_license_reference_count") != 0:
        fail("rev0864 decision packet did not close the mechanical reference question")
    if packet.get("root_license_or_notice_file_present") is not False:
        fail("rev0864 decision packet improperly claims a root rights file")
    closed = packet.get("closed_actions")
    if not isinstance(closed, list) or not any(x.get("id") == "missing_local_license_reference_targets" for x in closed if isinstance(x, dict)):
        fail("rev0864 decision packet omits the closed action")


def assert_patch_recovery_stop_condition() -> None:
    audit = load_json("AUDIT/OPERATIONAL_RISK_RETIREMENT_REV0864.json")
    search = audit.get("streamfold_patch_body_search", {})
    if search.get("target_count") != 17 or search.get("targets_with_exact_diff_headers") != 0:
        fail("patch-body search did not establish the 17-target stop condition")
    rows = search.get("rows")
    if not isinstance(rows, list) or len(rows) != 17:
        fail("patch-body search row set is incomplete")
    if any(row.get("reconstructable_from_examined_patch_sections") is not False for row in rows if isinstance(row, dict)):
        fail("patch-body search overstates reconstructability")
    listed = search.get("patch_files")
    if not isinstance(listed, list) or len(listed) != search.get("patch_file_count"):
        fail("patch-body search does not carry its examined patch list")
    for rel in listed:
        path = ROOT / str(rel)
        if not path.is_file() or path.is_symlink():
            fail(f"patch-body search references absent or unsafe patch: {rel}")


def assert_gate_configuration() -> None:
    manifest = load_json("PATCH_BUNDLE_MANIFEST.json")
    if manifest.get("overlay_revision") != "rev0864":
        fail("patch bundle manifest is not rev0864")
    checks = manifest.get("gate_checks")
    expected = ["risk-retirement-rev0864", "overlay-integrity", "overlay-chain", "streamfold-archive-search"]
    if not isinstance(checks, list) or [row.get("id") for row in checks if isinstance(row, dict)] != expected:
        fail("manifest gate_checks order or membership is wrong")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/overlay_gate.py"), "--list", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if proc.returncode != 0:
        fail(f"overlay gate list mode failed: {(proc.stderr or proc.stdout).strip()}")
    try:
        listed = json.loads(proc.stdout)
    except Exception as exc:
        fail(f"overlay gate list mode did not emit JSON: {exc}")
    if [row.get("id") for row in listed.get("checks", [])] != expected:
        fail("overlay gate list mode diverges from manifest configuration")


def assert_operator_surfaces() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if not readme.startswith("# EvidenceVault rev0864") or "python3 scripts/overlay_gate.py" not in readme[:5000]:
        fail("README does not lead with the rev0864 single gate")
    commands = (ROOT / "OVERLAY_COMMANDS.md").read_text(encoding="utf-8")
    if not commands.startswith("# Overlay commands — rev0864") or "python3 scripts/overlay_gate.py" not in commands[:3000]:
        fail("OVERLAY_COMMANDS does not lead with the rev0864 single gate")


def main() -> int:
    assert_exact_license()
    assert_readme_index_identity()
    assert_recovery_surfaces()
    assert_rights_block_narrowed_not_erased()
    assert_patch_recovery_stop_condition()
    assert_gate_configuration()
    assert_operator_surfaces()
    print("risk-retirement-rev0864: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
