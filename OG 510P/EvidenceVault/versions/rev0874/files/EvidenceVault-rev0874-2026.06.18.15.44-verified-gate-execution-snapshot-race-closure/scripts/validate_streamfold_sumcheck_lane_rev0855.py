#!/usr/bin/env python3
"""Validate the rev0855 streamfold sumcheck payload-gate lane."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REVISION_RE = re.compile(r"rev(\d{4})")

def current_revision_number() -> int | None:
    candidates = [ROOT.name]
    checks = ROOT / "CHECKS"
    if checks.is_dir():
        candidates.extend(path.name for path in checks.glob("patch-bundle-identity-rev*.json"))
    numbers: list[int] = []
    for value in candidates:
        numbers.extend(int(match.group(1)) for match in REVISION_RE.finditer(value))
    return max(numbers) if numbers else None


def fail(message: str) -> None:
    print(f"streamfold-sumcheck-lane-rev0855: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(rel: str):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {rel}: {exc}")


def require_file(rel: str) -> None:
    p = ROOT / rel
    if p.is_symlink() or not p.is_file():
        fail(f"missing regular file: {rel}")


def require_text(rel: str, snippets: list[str]) -> None:
    require_file(rel)
    text = (ROOT / rel).read_text(encoding="utf-8")
    missing = [s for s in snippets if s not in text]
    if missing:
        fail(f"{rel} missing snippets: {missing}")


def run_ok(args: list[str], marker: str) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        fail(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        fail(f"command output missing {marker!r}: {output!r}")
    return output


def main() -> int:
    required = [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.csv",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/protocol_profile.rev0855.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_accept.rev0855.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_reject_bad_round.rev0855.json",
        "PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py",
        "PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py",
        "PROOFCORE/parent_snapshots/rev0854/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0854/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0854/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-sumcheck-lane.rev0855.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-sumcheck-lane.rev0855.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-sumcheck-lane.rev0855.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-sumcheck-lane.rev0855.pcd.json",
        "PROOFCORE/witness_policy/ev-streamfold-sumcheck-lane.rev0855.md",
        "PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-lane.rev0855.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-lane.rev0855.reject.json",
        "AUDIT/STREAMFOLD_SUMCHECK_LANE_REV0855.json",
        "AUDIT/STREAMFOLD_SUMCHECK_LANE_REV0855.md",
    ]
    for rel in required:
        require_file(rel)

    manifest = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.json")
    if manifest.get("source_group_id") != "streamfold_sumcheck_toy_v2_family":
        fail("payload manifest group mismatch")
    if manifest.get("status") != "blocked_waiting_for_canonical_payloads":
        fail("payload manifest status mismatch")
    summary = manifest.get("summary", {})
    if summary.get("expected_path_count") != 17 or summary.get("expected_missing_in_overlay") != 17:
        fail("payload manifest expected path/missing count mismatch")
    role_counts = summary.get("role_counts", {})
    for role in ["abi_ir_or_protocol_ir", "public_input_or_commitment", "attestation_or_receipt"]:
        if role not in role_counts:
            fail(f"payload manifest missing role {role}")
    payload_paths = [row.get("path") for row in manifest.get("expected_payloads", [])]
    if len(payload_paths) != len(set(payload_paths)):
        fail("payload manifest contains duplicate paths")
    if any((ROOT / str(path)).exists() for path in payload_paths):
        fail("canonical streamfold payload unexpectedly present in overlay")

    with (ROOT / "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/payload_manifest.rev0855.csv").open(newline="", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    if len(csv_rows) != 17:
        fail("payload CSV row count mismatch")

    profile = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/protocol_profile.rev0855.json")
    if profile.get("field", {}).get("modulus") != 97 or profile.get("claimed_sum_mod_p") != 9:
        fail("sumcheck profile arithmetic constants drifted")
    for phrase in ["not zero knowledge", "not a SNARK"]:
        if phrase not in "\n".join(profile.get("non_claims", [])):
            fail(f"protocol profile missing non-claim {phrase}")

    claim = load_json("PROOFCORE/claims/ev-streamfold-sumcheck-lane.rev0855.claim.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-sumcheck-lane.rev0855.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-sumcheck-lane.rev0855.pcd.json")
    if claim.get("revision") != "rev0855" or public_inputs.get("revision") != "rev0855" or cert.get("revision") != "rev0855":
        fail("revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge"):
        fail("rev0855 lane must not claim SNARK/ZK")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0854":
        fail("parent checkpoint revision mismatch")
    if public_inputs.get("payload_gate", {}).get("expected_path_count") != 17:
        fail("public input payload gate count mismatch")

    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    audit = load_json("AUDIT/STREAMFOLD_SUMCHECK_LANE_REV0855.json")
    if audit.get("status") != "streamfold_sumcheck_lane_gate_added_payloads_still_missing":
        fail("audit status drifted")
    require_text("AUDIT/STREAMFOLD_SUMCHECK_LANE_REV0855.md", ["Minimum first recovery set", "toy sumcheck verifier", "No payload bytes"])
    require_text("PROOFCORE/README.md", ["rev0855 streamfold sumcheck lane gate", "verify_streamfold_sumcheck_lane_rev0855.py", "not a zk-SNARK"])
    require_text("OVERLAY_COMMANDS.md", ["validate_streamfold_sumcheck_lane_rev0855.py", "rev0854 historical checkpoint", "--candidate-root"])
    current_rev = current_revision_number() or 855
    if current_rev > 855:
        require_file("PROOFCORE/parent_snapshots/rev0855/CHECKS-overlay-manifest.json")
        require_file("PROOFCORE/parent_snapshots/rev0855/CHECKS-overlay-manifest.sha256")
        require_file("PROOFCORE/parent_snapshots/rev0855/CHECKS-patches.sha256")
        require_file("PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py")
        require_text("OVERLAY_COMMANDS.md", ["rev0855 historical checkpoint", "verify_streamfold_sumcheck_fs_lane_rev0856.py"])
        print("streamfold-sumcheck-lane-rev0855: OK (historical checkpoint carried; use rev0856 parent replay)")
        return 0

    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_accept.rev0855.json"], "sumcheck-transcript-rev0855: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_reject_bad_round.rev0855.json", "--expect-fail"], "sumcheck-transcript-rev0855: expected failure observed")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py", "--fixture", "PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-lane.rev0855.accept.json"], "streamfold-sumcheck-lane-rev0855: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py", "--fixture", "PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-lane.rev0855.reject.json", "--expect-fail"], "streamfold-sumcheck-lane-rev0855: expected failure observed")
    print("streamfold-sumcheck-lane-rev0855: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
