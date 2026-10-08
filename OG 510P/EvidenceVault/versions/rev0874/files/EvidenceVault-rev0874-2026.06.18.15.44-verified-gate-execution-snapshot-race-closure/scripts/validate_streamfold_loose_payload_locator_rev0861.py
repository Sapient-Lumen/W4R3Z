#!/usr/bin/env python3
"""Validate the rev0861 streamfold loose payload locator lane."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"streamfold-loose-payload-locator-rev0861: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def require_file(rel: str) -> None:
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        fail(f"missing regular file: {rel}")


def load_json(rel: str) -> dict:
    require_file(rel)
    try:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {rel}: {exc}")
    if not isinstance(data, dict):
        fail(f"JSON object expected: {rel}")
    return data


def require_text(rel: str, snippets: list[str]) -> None:
    require_file(rel)
    text = (ROOT / rel).read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        fail(f"{rel} missing snippets: {missing}")


def import_module(rel: str, name: str):
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        fail(f"module path is not a regular file: {rel}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"cannot import module: {rel}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    if hasattr(module, "ROOT"):
        module.ROOT = ROOT  # type: ignore[attr-defined]
    return module


def run_ok(args: list[str], marker: str, timeout: int = 80) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=timeout)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        fail(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        fail(f"command output missing {marker!r}: {output!r}")
    return output


def main() -> int:
    required = [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_contract.rev0861.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_absence.full.rev0861.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_absence.minimum.rev0861.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_selftest.rev0861.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/README.md",
        "PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py",
        "PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py",
        "PROOFCORE/parent_snapshots/rev0860/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0860/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0860/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-loose-payload-locator.rev0861.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-loose-payload-locator.rev0861.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-loose-payload-locator.rev0861.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-loose-payload-locator.rev0861.pcd.json",
        "PROOFCORE/fixtures/accept/ev-streamfold-loose-payload-locator.rev0861.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-loose-payload-locator.rev0861.reject.json",
        "PROOFCORE/witness_policy/ev-streamfold-loose-payload-locator.rev0861.md",
        "PROOFCORE/verifier_surface.rev0861.json",
        "AUDIT/LOOSE_PAYLOAD_LOCATOR_REV0861.json",
        "AUDIT/LOOSE_PAYLOAD_LOCATOR_REV0861.md",
    ]
    for rel in required:
        require_file(rel)

    contract = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_contract.rev0861.json")
    audit = load_json("AUDIT/LOOSE_PAYLOAD_LOCATOR_REV0861.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-loose-payload-locator.rev0861.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-loose-payload-locator.rev0861.pcd.json")
    full = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_absence.full.rev0861.json")
    minimum = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_absence.minimum.rev0861.json")
    selftest = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/loose_payload_locator_selftest.rev0861.json")

    if contract.get("revision") != "rev0861" or audit.get("revision") != "rev0861" or public_inputs.get("revision") != "rev0861" or cert.get("revision") != "rev0861":
        fail("revision mismatch")
    if contract.get("status") != "loose_hash_locator_ready_no_payload_bytes_in_overlay":
        fail("loose locator contract status drifted")
    if audit.get("status") != "loose_hash_locator_ready_payloads_still_absent":
        fail("loose locator audit status drifted")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0860":
        fail("parent checkpoint mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge") or cert.get("proof_system", {}).get("succinct"):
        fail("rev0861 certificate must not claim SNARK/ZK/succinct")
    if full.get("selected_path_count") != 17 or full.get("status_counts", {}).get("missing") != 17:
        fail("full absence report drifted")
    if minimum.get("selected_path_count") != 4 or minimum.get("status_counts", {}).get("missing") != 4:
        fail("minimum absence report drifted")
    if full.get("locator_status") != "blocked_waiting_for_candidate_roots" or minimum.get("locator_status") != "blocked_waiting_for_candidate_roots":
        fail("absence report locator status drifted")
    controls = selftest.get("controls", {})
    required_controls = [
        "loose_paths_found",
        "loose_paths_staged_to_canonical_targets",
        "duplicate_hash_ambiguous",
        "ambiguous_stage_rejected",
        "symlink_file_skipped",
        "path_escape_rejected",
        "stage_inside_overlay_rejected",
        "stage_inside_candidate_rejected",
        "partial_stage_rejected",
    ]
    if selftest.get("required_controls_passed") is not True or not all(controls.get(key) is True for key in required_controls):
        fail("loose locator self-test controls incomplete")

    locator_module = import_module("PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py", "ev_rev0861_locator_validator")
    recomputed_full = locator_module.locate_report([], None, mode="full")  # type: ignore[attr-defined]
    recomputed_minimum = locator_module.locate_report([], None, mode="minimum")  # type: ignore[attr-defined]
    recomputed_selftest = locator_module.self_test()  # type: ignore[attr-defined]
    if recomputed_full != full:
        fail("full locator absence report is not reproducible")
    if recomputed_minimum != minimum:
        fail("minimum locator absence report is not reproducible")
    if recomputed_selftest != selftest:
        fail("loose locator self-test report is not reproducible")

    lane_module = import_module("PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py", "ev_rev0861_locator_lane_validator")
    accept = ROOT / "PROOFCORE/fixtures/accept/ev-streamfold-loose-payload-locator.rev0861.accept.json"
    result = lane_module.verify_fixture(accept, skip_parent_replay=True)  # type: ignore[attr-defined]
    if not isinstance(result, dict) or result.get("ok") is not True:
        fail("loose locator lane accept fixture returned unexpected result")
    reject = ROOT / "PROOFCORE/fixtures/reject/ev-streamfold-loose-payload-locator.rev0861.reject.json"
    try:
        lane_module.verify_fixture(reject, skip_parent_replay=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    else:
        fail("loose locator lane reject fixture unexpectedly verified")

    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    require_text("OVERLAY_COMMANDS.md", ["validate_streamfold_loose_payload_locator_rev0861.py", "locate_streamfold_payloads_rev0861.py", "rev0860 historical checkpoint"])
    require_text("PROOFCORE/README.md", ["rev0861", "loose payload locator", "candidate-root"])
    require_text("AUDIT/LOOSE_PAYLOAD_LOCATOR_REV0861.md", ["hash-first locator", "Still blocked", "duplicate"])
    require_text("scripts/validate_streamfold_payload_graft_rev0860.py", ["historical checkpoint carried; use rev0861 loose payload locator parent replay"])

    print("streamfold-loose-payload-locator-rev0861: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
