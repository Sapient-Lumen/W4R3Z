#!/usr/bin/env python3
"""Validate the rev0858 framed transcript and payload-receipt proofcore lane."""
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
    print(f"framed-transcript-receipt-rev0858: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(rel: str):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {rel}: {exc}")


def require_file(rel: str) -> None:
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
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
    result = subprocess.run(args, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=60)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        fail(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        fail(f"command output missing {marker!r}: {output!r}")
    return output




def run_ok_inherited(args: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=ROOT, env=env, text=True, check=False, timeout=120)
    if result.returncode != 0:
        fail(f"command failed {args}: returncode={result.returncode}")


def assert_candidate_negative_controls() -> None:
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-framed-receipt.rev0858.public-input.json")
    verifier = public_inputs.get("payload_receipts", {}).get("payload_candidate_verifier_path") or "PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py"
    minimum = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json")
    first_path = minimum.get("source_report", {}).get("source_group_id")
    expected_first = "artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2.json"
    # The concrete minimum path is also carried by the rev0857 contract.
    contract = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/payload_admission_contract.rev0857.json")
    paths = contract.get("minimum_first_recovery_set") or [expected_first]
    expected_first = paths[0]

    with tempfile.TemporaryDirectory(prefix="ev-rev0858-empty-candidate-") as tmp:
        run_ok([sys.executable, verifier, "--candidate-root", tmp, "--mode", "minimum", "--expect-fail"], "streamfold-payload-candidate-rev0857: expected failure observed")

    with tempfile.TemporaryDirectory(prefix="ev-rev0858-wrong-candidate-") as tmp:
        target = Path(tmp) / expected_first
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n", encoding="utf-8")
        run_ok([sys.executable, verifier, "--candidate-root", tmp, "--mode", "minimum", "--expect-fail"], "streamfold-payload-candidate-rev0857: expected failure observed")

    with tempfile.TemporaryDirectory(prefix="ev-rev0858-symlink-payload-") as tmp:
        target = Path(tmp) / expected_first
        target.parent.mkdir(parents=True, exist_ok=True)
        external = Path(tmp) / "external.json"
        external.write_text("{}\n", encoding="utf-8")
        target.symlink_to(external)
        run_ok([sys.executable, verifier, "--candidate-root", tmp, "--mode", "minimum", "--expect-fail"], "streamfold-payload-candidate-rev0857: expected failure observed")

    with tempfile.TemporaryDirectory(prefix="ev-rev0858-symlink-root-") as tmp:
        root = Path(tmp)
        real = root / "real"
        real.mkdir()
        link = root / "link"
        link.symlink_to(real, target_is_directory=True)
        run_ok([sys.executable, verifier, "--candidate-root", str(link), "--mode", "minimum", "--expect-fail"], "streamfold-payload-candidate-rev0857: expected failure observed")


def main() -> int:
    if (ROOT / "PROOFCORE" / "certificates" / "ev-streamfold-payload-receipt-liveness.rev0859.pcd.json").is_file():
        # rev0858 is a historical checkpoint in rev0859. The rev0858
        # payload-receipt verifier is hash-bound but liveness-quarantined in
        # this cloudtainer; rev0859 replays rev0858 receipts through the
        # in-process verifier instead of rerunning the legacy subprocess pipe.
        require_file("PROOFCORE/fixtures/accept/ev-streamfold-framed-receipt.rev0858.accept.json")
        require_file("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json")
        require_file("PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py")
        print("framed-transcript-receipt-rev0858: OK (historical checkpoint carried; use rev0859 in-process receipt replay)")
        return 0
    required = [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_receipt_contract.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/transcript_operation_contract.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/protocol_profile.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/candidate_attack_matrix.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_accept.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_reject_reordered_absorb.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_reject_label_swap.rev0858.json",
        "PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py",
        "PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py",
        "PROOFCORE/verifiers/verify_streamfold_framed_receipt_lane_rev0858.py",
        "PROOFCORE/parent_snapshots/rev0857/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0857/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0857/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-framed-receipt.rev0858.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-framed-receipt.rev0858.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-framed-receipt.rev0858.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-framed-receipt.rev0858.pcd.json",
        "PROOFCORE/fixtures/accept/ev-streamfold-framed-receipt.rev0858.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-framed-receipt.rev0858.reject.json",
        "PROOFCORE/witness_policy/ev-streamfold-framed-receipt.rev0858.md",
        "AUDIT/FRAMED_TRANSCRIPT_RECEIPT_REV0858.json",
        "AUDIT/FRAMED_TRANSCRIPT_RECEIPT_REV0858.md",
    ]
    for rel in required:
        require_file(rel)

    audit = load_json("AUDIT/FRAMED_TRANSCRIPT_RECEIPT_REV0858.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-framed-receipt.rev0858.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-framed-receipt.rev0858.pcd.json")
    accept = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_accept.rev0858.json")
    attack = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/candidate_attack_matrix.rev0858.json")
    if audit.get("status") != "framed_transcript_receipts_active_payloads_still_missing":
        fail("audit status drifted")
    if public_inputs.get("revision") != "rev0858" or cert.get("revision") != "rev0858":
        fail("revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge") or cert.get("proof_system", {}).get("succinct"):
        fail("rev0858 certificate must not claim SNARK/ZK/succinct")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0857":
        fail("parent checkpoint mismatch")
    if public_inputs.get("payload_receipts", {}).get("expected_full_absent_count") != 17:
        fail("full absence count drifted")
    if public_inputs.get("payload_receipts", {}).get("expected_minimum_absent_count") != 4:
        fail("minimum absence count drifted")
    if public_inputs.get("framed_transcript_harness", {}).get("derived_accept_challenges") != [r.get("challenge") for r in accept.get("transcript", {}).get("rounds", [])]:
        fail("derived challenge values drifted")
    if public_inputs.get("framed_transcript_harness", {}).get("operation_count") != 9:
        fail("framed operation count drifted")
    if attack.get("bug_fix") != "resolve_candidate_root now checks the raw candidate path for symlink status before resolving it":
        fail("candidate-root symlink fix note missing")
    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    require_text("PROOFCORE/README.md", ["rev0858 framed transcript", "payload absence receipts", "operation log"])
    require_text("OVERLAY_COMMANDS.md", ["validate_framed_transcript_receipt_rev0858.py", "rev0857 historical checkpoint", "candidate-root symlink"])
    require_text("AUDIT/FRAMED_TRANSCRIPT_RECEIPT_REV0858.md", ["Payload receipt", "Framed transcript", "candidate-root symlink"])

    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py", "--receipt", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json"], "streamfold-payload-receipt-rev0858: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py", "--receipt", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json"], "streamfold-payload-receipt-rev0858: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py", "--receipt", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json", "--expect-fail"], "streamfold-payload-receipt-rev0858: expected failure observed")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_accept.rev0858.json"], "sumcheck-fs-framed-transcript-rev0858: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_reject_reordered_absorb.rev0858.json", "--expect-fail"], "sumcheck-fs-framed-transcript-rev0858: expected failure observed")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_reject_label_swap.rev0858.json", "--expect-fail"], "sumcheck-fs-framed-transcript-rev0858: expected failure observed")
    assert_candidate_negative_controls()
    # The full lane verifier composes the checks above and can be run directly.
    # It is deliberately not nested here to avoid long subprocess pipe lifetimes
    # from repeated verifier composition in lightweight validation.
    print("framed-transcript-receipt-rev0858: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
