#!/usr/bin/env python3
"""Validate the rev0857 streamfold payload-admission and transcript-prefix lane."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"streamfold-payload-admission-rev0857: FAIL: {message}", file=sys.stderr)
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
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        fail(f"{rel} missing snippets: {missing}")


def run_ok(args: list[str], marker: str) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        fail(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        fail(f"command output missing {marker!r}: {output!r}")
    return output


def main() -> int:
    if (ROOT / "PROOFCORE" / "certificates" / "ev-streamfold-framed-receipt.rev0858.pcd.json").is_file():
        # rev0857 is a historical checkpoint in rev0858. The active endpoint
        # reconstructs and replays rev0857 by reversing the rev0858 patch, so
        # this carried validator must not rerun rev0857 directly against a
        # deliberately changed verifier surface.
        require_file("PROOFCORE/fixtures/accept/ev-streamfold-payload-admission.rev0857.accept.json")
        require_file("PROOFCORE/parent_snapshots/rev0857/CHECKS-overlay-manifest.json")
        require_file("PROOFCORE/verifiers/verify_streamfold_framed_receipt_lane_rev0858.py")
        print("streamfold-payload-admission-rev0857: OK (historical checkpoint carried; use rev0858 parent replay)")
        return 0

    required = [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_admission_contract.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/protocol_profile.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/transcript_prefix_contract.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_candidate_absence_report.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_candidate_minimum_absence_report.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_accept.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_reject_bad_prefix.rev0857.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_reject_payload_contract_tamper.rev0857.json",
        "PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py",
        "PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py",
        "PROOFCORE/verifiers/verify_streamfold_payload_admission_lane_rev0857.py",
        "PROOFCORE/parent_snapshots/rev0856/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0856/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0856/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-payload-admission.rev0857.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-payload-admission.rev0857.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-payload-admission.rev0857.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-payload-admission.rev0857.pcd.json",
        "PROOFCORE/witness_policy/ev-streamfold-payload-admission.rev0857.md",
        "PROOFCORE/fixtures/accept/ev-streamfold-payload-admission.rev0857.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-payload-admission.rev0857.reject.json",
        "AUDIT/PAYLOAD_ADMISSION_TRANSCRIPT_PREFIX_REV0857.json",
        "AUDIT/PAYLOAD_ADMISSION_TRANSCRIPT_PREFIX_REV0857.md",
    ]
    for rel in required:
        require_file(rel)

    audit = load_json("AUDIT/PAYLOAD_ADMISSION_TRANSCRIPT_PREFIX_REV0857.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-payload-admission.rev0857.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-payload-admission.rev0857.pcd.json")
    accept = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_accept.rev0857.json")
    absence = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_candidate_absence_report.rev0857.json")
    if audit.get("status") != "payload_admission_executable_transcript_prefix_bound_payloads_still_missing":
        fail("audit status drifted")
    if public_inputs.get("revision") != "rev0857" or cert.get("revision") != "rev0857":
        fail("revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge") or cert.get("proof_system", {}).get("succinct"):
        fail("rev0857 certificate must not claim SNARK/ZK/succinct")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0856":
        fail("parent checkpoint mismatch")
    payload = public_inputs.get("payload_admission", {})
    if payload.get("expected_path_count") != 17 or payload.get("expected_missing_in_overlay") != 17 or payload.get("minimum_first_recovery_set_count") != 4:
        fail("payload admission counts drifted")
    if absence.get("candidate_admission_status") != "blocked_waiting_for_candidate_root" or absence.get("overlay_payloads_absent") != 17:
        fail("absence report drifted")
    rounds = accept.get("transcript", {}).get("rounds", [])
    if [r.get("challenge") for r in rounds] != public_inputs.get("transcript_prefix_harness", {}).get("derived_accept_challenges"):
        fail("derived challenge values drifted")
    if not rounds or "previous_round_message_hashes" not in rounds[1]:
        fail("second round does not bind previous_round_message_hashes")
    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")
    require_text("PROOFCORE/README.md", ["rev0857 payload admission", "verify_streamfold_payload_candidate_rev0857.py", "prefix-bound"])
    require_text("OVERLAY_COMMANDS.md", ["validate_streamfold_payload_admission_rev0857.py", "rev0856 historical checkpoint", "--mode minimum"])
    require_text("AUDIT/PAYLOAD_ADMISSION_TRANSCRIPT_PREFIX_REV0857.md", ["Minimum first recovery set", "previous public transcript-message hashes", "Candidate-root commands"])

    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py", "--mode", "full"], "streamfold-payload-candidate-rev0857: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py", "--mode", "minimum"], "streamfold-payload-candidate-rev0857: OK")
    with tempfile.TemporaryDirectory(prefix="ev-rev0857-bad-candidate-") as tmp:
        bad_root = Path(tmp)
        first_path = payload.get("minimum_first_recovery_set", ["artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2.json"])[0]
        target = bad_root / first_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n", encoding="utf-8")
        run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py", "--candidate-root", str(bad_root), "--mode", "minimum", "--expect-fail"], "streamfold-payload-candidate-rev0857: expected failure observed")

    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_accept.rev0857.json"], "sumcheck-fs-prefix-transcript-rev0857: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_reject_bad_prefix.rev0857.json", "--expect-fail"], "sumcheck-fs-prefix-transcript-rev0857: expected failure observed")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_reject_payload_contract_tamper.rev0857.json", "--expect-fail"], "sumcheck-fs-prefix-transcript-rev0857: expected failure observed")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_admission_lane_rev0857.py", "--fixture", "PROOFCORE/fixtures/accept/ev-streamfold-payload-admission.rev0857.accept.json", "--skip-parent-replay"], "streamfold-payload-admission-lane-rev0857: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_admission_lane_rev0857.py", "--fixture", "PROOFCORE/fixtures/reject/ev-streamfold-payload-admission.rev0857.reject.json", "--expect-fail"], "streamfold-payload-admission-lane-rev0857: expected failure observed")
    print("streamfold-payload-admission-rev0857: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
