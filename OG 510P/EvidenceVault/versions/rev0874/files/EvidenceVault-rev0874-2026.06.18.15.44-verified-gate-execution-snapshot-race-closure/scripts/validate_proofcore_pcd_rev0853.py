#!/usr/bin/env python3
"""Validate rev0853 PROOFCORE transparent PCD lane and path-role refactor."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def infer_current_revision() -> int:
    import re
    candidates = [ROOT.name]
    checks = ROOT / "CHECKS"
    if checks.is_dir():
        candidates.extend(path.name for path in checks.glob("patch-bundle-identity-rev*.json"))
    found: list[int] = []
    for text in candidates:
        found.extend(int(match.group(1)) for match in re.finditer(r"rev(\d{4})", text))
    return max(found) if found else 853


def validate_historical_checkpoint_carried() -> int:
    """For rev0854+ bundles, the rev0853 exact checkpoint is replayed by the successor.

    The rev0853 accept fixture intentionally described the exact rev0853 tree. Running
    that exact fixture directly against a later overlay is an operator trap. In later
    bundles this compatibility validator confirms the checkpoint is still carried and
    that a successor parent-replay verifier has taken over.
    """
    for rel in [
        "PROOFCORE/claims/ev-overlay-integrity.rev0853.claim.json",
        "PROOFCORE/public_inputs/ev-overlay-integrity.rev0853.public-input.json",
        "PROOFCORE/certificates/ev-overlay-integrity.rev0853.pcd.json",
        "PROOFCORE/verifiers/verify_pcd_envelope.py",
        "PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json",
        "PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json",
        "PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py",
        "scripts/validate_proofcore_frontier_pcd_rev0854.py",
        "AUDIT/PROOFCORE_FRONTIER_PCD_REV0854.json",
    ]:
        require_file(rel)
    manifest = load_json("PROOFCORE/proofcore_manifest.json")
    lanes = manifest.get("lanes") or []
    if not any(lane.get("claim_id") == "ev.pcd.overlay_integrity.rev0853" and lane.get("role") == "historical_parent_checkpoint" for lane in lanes if isinstance(lane, dict)):
        fail("rev0853 checkpoint is not marked as a historical parent checkpoint in PROOFCORE/proofcore_manifest.json")
    audit = load_json("AUDIT/PROOFCORE_FRONTIER_PCD_REV0854.json")
    if audit.get("status") != "parent_linked_frontier_pcd_lane_added":
        fail("rev0854 frontier audit does not record parent-linked replay")
    require_text("OVERLAY_COMMANDS.md", ["historical checkpoint", "verify_proofcore_frontier_rev0854.py"])
    print("proofcore-pcd-rev0853: OK (historical checkpoint carried; use rev0854 parent replay)")
    return 0


def fail(message: str) -> None:
    print(f"proofcore-pcd-rev0853: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(rel: str):
    path = ROOT / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {rel}: {exc}")


def require_file(rel: str) -> None:
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        fail(f"missing regular file: {rel}")


def require_text(rel: str, snippets: list[str]) -> None:
    require_file(rel)
    text = (ROOT / rel).read_text(encoding="utf-8")
    missing = [s for s in snippets if s not in text]
    if missing:
        fail(f"{rel} missing snippets: {missing}")


def run_ok(args: list[str], expect_fragment: str) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        fail(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if expect_fragment not in output:
        fail(f"command {args} output missing {expect_fragment!r}: {output!r}")
    return output


def main() -> int:
    if infer_current_revision() > 853:
        return validate_historical_checkpoint_carried()

    required = [
        "PROOFCORE/README.md",
        "PROOFCORE/GLOSSARY.md",
        "PROOFCORE/THREAT_MODEL.md",
        "PROOFCORE/proofcore_manifest.json",
        "PROOFCORE/schemas/pcd_claim.schema.rev0853.json",
        "PROOFCORE/schemas/pcd_envelope.schema.rev0853.json",
        "PROOFCORE/claims/ev-overlay-integrity.rev0853.claim.json",
        "PROOFCORE/public_inputs/ev-overlay-integrity.rev0853.public-input.json",
        "PROOFCORE/witness_policy/ev-overlay-integrity.rev0853.md",
        "PROOFCORE/commitments/ev-overlay-integrity.rev0853.commitments.json",
        "PROOFCORE/certificates/ev-overlay-integrity.rev0853.pcd.json",
        "PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json",
        "PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json",
        "PROOFCORE/maps/canonical_path_to_role.rev0853.csv",
        "PROOFCORE/verifiers/verify_pcd_envelope.py",
        "AUDIT/PROOFCORE_PATH_ROLE_AUDIT_REV0853.json",
        "AUDIT/PROOFCORE_PATH_ROLE_AUDIT_REV0853.md",
        "AUDIT/PROOFCORE_PCD_LANE_REV0853.json",
        "AUDIT/PROOFCORE_PCD_LANE_REV0853.md",
    ]
    for rel in required:
        require_file(rel)

    claim = load_json("PROOFCORE/claims/ev-overlay-integrity.rev0853.claim.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-overlay-integrity.rev0853.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-overlay-integrity.rev0853.pcd.json")
    manifest = load_json("PROOFCORE/proofcore_manifest.json")
    path_audit = load_json("AUDIT/PROOFCORE_PATH_ROLE_AUDIT_REV0853.json")
    lane_audit = load_json("AUDIT/PROOFCORE_PCD_LANE_REV0853.json")

    if claim.get("revision") != "rev0853" or public_inputs.get("revision") != "rev0853":
        fail("claim/public input revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge"):
        fail("transparent certificate must not claim SNARK/ZK")
    if claim.get("claim_id") != "ev.pcd.overlay_integrity.rev0853":
        fail("unexpected claim id")
    if manifest.get("first_lane", {}).get("claim_id") != claim.get("claim_id"):
        fail("proofcore manifest does not point at first lane claim")

    with (ROOT / "PROOFCORE/maps/canonical_path_to_role.rev0853.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 1000:
        fail(f"path-role map unexpectedly small: {len(rows)}")
    if len(rows) != public_inputs.get("path_role_map_expectation", {}).get("expected_rows"):
        fail("public input map row count mismatch")
    if len(rows) != path_audit.get("metrics", {}).get("proof_signal_paths_mapped"):
        fail("path audit map row count mismatch")
    roles = {row.get("role") for row in rows}
    for role in ["paper_or_render", "verifier_code", "attestation_or_receipt", "schema", "abi_ir_or_protocol_ir"]:
        if role not in roles:
            fail(f"expected role not present: {role}")
    sentinel_paths = set(public_inputs.get("canonical_index_expectation", {}).get("required_sentinel_paths", []))
    mapped_paths = {row.get("path") for row in rows}
    missing = sorted(sentinel_paths - mapped_paths)
    if missing:
        fail("required sentinel paths missing from role map: " + ", ".join(missing))
    if any(row.get("present_in_overlay") != "false" for row in rows):
        fail("role map should record indexed proof payloads as absent from overlay")

    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    require_text("PROOFCORE/README.md", ["first executable PCD lane", "not a zk-SNARK", "accept", "reject"])
    require_text("PROOFCORE/THREAT_MODEL.md", ["No zero-knowledge property", "Completion trigger", "publication permission"])
    require_text("AUDIT/PROOFCORE_PCD_LANE_REV0853.md", ["claim -> public inputs", "not a SNARK", "Commands"])
    require_text("OVERLAY_COMMANDS.md", ["validate_proofcore_pcd_rev0853.py", "verify_pcd_envelope.py"])
    require_text("README.md", ["EvidenceVault rev0853", "first executable proof-carrying-data lane", "Use these overlay checks first"])

    run_ok([
        sys.executable,
        "PROOFCORE/verifiers/verify_pcd_envelope.py",
        "--fixture",
        "PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json",
    ], "pcd-envelope-rev0853: OK")
    run_ok([
        sys.executable,
        "PROOFCORE/verifiers/verify_pcd_envelope.py",
        "--fixture",
        "PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json",
        "--expect-fail",
    ], "expected failure observed")

    if lane_audit.get("status") != "executable_transparent_pcd_lane_added":
        fail("lane audit status drifted")
    print("proofcore-pcd-rev0853: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
