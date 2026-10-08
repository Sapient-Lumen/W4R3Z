#!/usr/bin/env python3
"""Validate the rev0856 streamfold sumcheck transcript-binding lane."""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CURRENT_REVISION_RE = re.compile(r"rev(\d{4})")


def current_revision_number() -> int | None:
    candidates = [ROOT.name]
    checks = ROOT / "CHECKS"
    if checks.is_dir():
        candidates.extend(path.name for path in checks.glob("patch-bundle-identity-rev*.json"))
    found: list[int] = []
    for text in candidates:
        found.extend(int(match.group(1)) for match in CURRENT_REVISION_RE.finditer(text))
    return max(found) if found else None


def fail(message: str) -> None:
    print(f"streamfold-sumcheck-fs-lane-rev0856: FAIL: {message}", file=sys.stderr)
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
    # Execute through a shell command string so nested parent-replay subprocesses
    # inherit terminal streams as they do in operator use. This avoids observed
    # hangs from nested Python subprocess descriptors in this cloudtainer.
    command = " ".join(shlex.quote(str(arg)) for arg in args)
    result = subprocess.run(["bash", "-lc", command], cwd=ROOT, text=True, check=False)
    if result.returncode != 0:
        fail(f"command failed {args}: returncode={result.returncode}")
    return marker


def main() -> int:
    required = [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/transcript_challenge_contract.rev0856.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/protocol_profile.rev0856.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/payload_admission_contract.rev0856.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_accept.rev0856.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_reject_bad_challenge.rev0856.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_reject_omit_payload_binding.rev0856.json",
        "PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py",
        "PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py",
        "PROOFCORE/parent_snapshots/rev0855/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0855/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0855/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-sumcheck-fs-lane.rev0856.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-sumcheck-fs-lane.rev0856.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-sumcheck-fs-lane.rev0856.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-sumcheck-fs-lane.rev0856.pcd.json",
        "PROOFCORE/witness_policy/ev-streamfold-sumcheck-fs-lane.rev0856.md",
        "PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-fs-lane.rev0856.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-fs-lane.rev0856.reject.json",
        "AUDIT/SUMCHECK_TRANSCRIPT_BINDING_REV0856.json",
        "AUDIT/SUMCHECK_TRANSCRIPT_BINDING_REV0856.md",
        "AUDIT/PROOFCORE_VERIFIER_SURFACE_AUDIT_REV0856.json",
        "AUDIT/PROOFCORE_VERIFIER_SURFACE_AUDIT_REV0856.md",
    ]
    for rel in required:
        require_file(rel)

    current_rev = current_revision_number() or 856
    if current_rev > 856:
        require_file("PROOFCORE/parent_snapshots/rev0856/CHECKS-overlay-manifest.json")
        require_file("PROOFCORE/parent_snapshots/rev0856/CHECKS-overlay-manifest.sha256")
        require_file("PROOFCORE/parent_snapshots/rev0856/CHECKS-patches.sha256")
        require_file("PROOFCORE/verifiers/verify_streamfold_payload_admission_lane_rev0857.py")
        require_text("OVERLAY_COMMANDS.md", ["rev0856 historical checkpoint", "verify_streamfold_payload_admission_lane_rev0857.py"])
        print("streamfold-sumcheck-fs-lane-rev0856: OK (historical checkpoint carried; use rev0857 parent replay)")
        return 0

    contract = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/transcript_challenge_contract.rev0856.json")
    profile = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/protocol_profile.rev0856.json")
    accept = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_accept.rev0856.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-sumcheck-fs-lane.rev0856.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-sumcheck-fs-lane.rev0856.pcd.json")
    if contract.get("revision") != "rev0856" or profile.get("revision") != "rev0856" or public_inputs.get("revision") != "rev0856" or cert.get("revision") != "rev0856":
        fail("revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge"):
        fail("rev0856 lane must not claim SNARK/ZK")
    rounds = accept.get("transcript", {}).get("rounds", [])
    if [r.get("challenge") for r in rounds] != public_inputs.get("fs_sumcheck_harness", {}).get("derived_accept_challenges"):
        fail("derived challenge values drifted")
    context = accept.get("transcript_context", {})
    for field in contract.get("must_bind_public_context_fields", []):
        if field not in context:
            fail(f"accept fixture context missing {field}")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0855":
        fail("parent checkpoint revision mismatch")
    if public_inputs.get("payload_gate", {}).get("expected_path_count") != 17:
        fail("payload gate count mismatch")
    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")
    audit = load_json("AUDIT/SUMCHECK_TRANSCRIPT_BINDING_REV0856.json")
    if audit.get("status") != "transcript_challenge_binding_added_payloads_still_missing":
        fail("transcript binding audit status drifted")
    surface = load_json("AUDIT/PROOFCORE_VERIFIER_SURFACE_AUDIT_REV0856.json")
    if surface.get("status") != "proofcore_verifier_surface_refactored_and_audited":
        fail("verifier surface audit status drifted")
    require_text("PROOFCORE/README.md", ["rev0856 transcript-bound streamfold sumcheck lane", "verify_streamfold_sumcheck_fs_lane_rev0856.py", "not a production Fiat-Shamir transform"])
    require_text("OVERLAY_COMMANDS.md", ["validate_sumcheck_fs_lane_rev0856.py", "rev0855 historical checkpoint", "sumcheck_fs_accept.rev0856.json"])
    require_text("AUDIT/SUMCHECK_TRANSCRIPT_BINDING_REV0856.md", ["unbound challenge", "payload_manifest_sha256", "bad challenge"])
    print("rev0856 validation: raw FS accept", flush=True)
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_accept.rev0856.json"], "sumcheck-fs-transcript-rev0856: OK")
    print("rev0856 validation: raw FS reject bad challenge", flush=True)
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_reject_bad_challenge.rev0856.json", "--expect-fail"], "sumcheck-fs-transcript-rev0856: expected failure observed")
    print("rev0856 validation: raw FS reject omitted binding", flush=True)
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py", "--fixture", "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_reject_omit_payload_binding.rev0856.json", "--expect-fail"], "sumcheck-fs-transcript-rev0856: expected failure observed")
    print("rev0856 validation: lane accept fast path (parent replay intentionally skipped here)", flush=True)
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py", "--fixture", "PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-fs-lane.rev0856.accept.json", "--skip-parent-replay"], "streamfold-sumcheck-fs-lane-rev0856: OK")
    print("rev0856 validation: lane reject", flush=True)
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py", "--fixture", "PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-fs-lane.rev0856.reject.json", "--expect-fail"], "streamfold-sumcheck-fs-lane-rev0856: expected failure observed")
    print("streamfold-sumcheck-fs-lane-rev0856: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
