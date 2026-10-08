#!/usr/bin/env python3
"""Validate the rev0862 streamfold archive payload search lane."""
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
    print(f"streamfold-archive-payload-search-rev0862: FAIL: {message}", file=sys.stderr)
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


def run_ok(args: list[str], marker: str, timeout: int = 90) -> str:
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
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_contract.rev0862.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_absence.full.rev0862.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_absence.minimum.rev0862.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_selftest.rev0862.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/cloudtainer_zip_search_receipt.rev0862.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/README.md",
        "PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py",
        "PROOFCORE/verifiers/verify_streamfold_archive_payload_search_lane_rev0862.py",
        "PROOFCORE/parent_snapshots/rev0861/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0861/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0861/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-archive-payload-search.rev0862.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-archive-payload-search.rev0862.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-archive-payload-search.rev0862.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-archive-payload-search.rev0862.pcd.json",
        "PROOFCORE/fixtures/accept/ev-streamfold-archive-payload-search.rev0862.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-archive-payload-search.rev0862.reject.json",
        "PROOFCORE/witness_policy/ev-streamfold-archive-payload-search.rev0862.md",
        "PROOFCORE/verifier_surface.rev0862.json",
        "AUDIT/ARCHIVE_PAYLOAD_SEARCH_REV0862.json",
        "AUDIT/ARCHIVE_PAYLOAD_SEARCH_REV0862.md",
    ]
    for rel in required:
        require_file(rel)

    contract = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_contract.rev0862.json")
    audit = load_json("AUDIT/ARCHIVE_PAYLOAD_SEARCH_REV0862.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-archive-payload-search.rev0862.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-archive-payload-search.rev0862.pcd.json")
    full = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_absence.full.rev0862.json")
    minimum = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_absence.minimum.rev0862.json")
    selftest = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_selftest.rev0862.json")
    cloud = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/cloudtainer_zip_search_receipt.rev0862.json")

    if contract.get("revision") != "rev0862" or audit.get("revision") != "rev0862" or public_inputs.get("revision") != "rev0862" or cert.get("revision") != "rev0862":
        fail("revision mismatch")
    if contract.get("status") != "zipaware_archive_search_ready_no_payload_bytes_in_overlay":
        fail("archive search contract status drifted")
    if audit.get("status") != "zipaware_archive_search_ready_payloads_still_absent":
        fail("archive search audit status drifted")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0861":
        fail("parent checkpoint mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge") or cert.get("proof_system", {}).get("succinct"):
        fail("rev0862 certificate must not claim SNARK/ZK/succinct")
    if full.get("selected_path_count") != 17 or full.get("status_counts", {}).get("missing") != 17:
        fail("full archive absence report drifted")
    if minimum.get("selected_path_count") != 4 or minimum.get("status_counts", {}).get("missing") != 4:
        fail("minimum archive absence report drifted")
    if full.get("archive_locator_status") != "blocked_waiting_for_candidate_sources" or minimum.get("archive_locator_status") != "blocked_waiting_for_candidate_sources":
        fail("absence report locator status drifted")
    controls = selftest.get("controls", {})
    required_controls = [
        "directory_payload_found",
        "zip_payload_found",
        "mixed_sources_staged_to_canonical_targets",
        "duplicate_hash_ambiguous",
        "ambiguous_stage_rejected",
        "zip_symlink_entry_skipped",
        "unsafe_zip_member_skipped",
        "stage_inside_overlay_rejected",
        "stage_inside_candidate_directory_rejected",
        "partial_stage_rejected",
    ]
    if selftest.get("required_controls_passed") is not True or not all(controls.get(key) is True for key in required_controls):
        fail("archive search self-test controls incomplete")
    if cloud.get("portable_validation_required") is not False or cloud.get("candidate_archive_count") != 12 or cloud.get("total_matches") != 0:
        fail("cloudtainer ZIP search receipt drifted")
    if len(cloud.get("source_reports") or []) != 12:
        fail("cloudtainer ZIP search receipt source count drifted")

    engine = import_module("PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py", "ev_rev0862_archive_engine_validator")
    recomputed_full = engine.locate_report([], None, mode="full")  # type: ignore[attr-defined]
    recomputed_minimum = engine.locate_report([], None, mode="minimum")  # type: ignore[attr-defined]
    recomputed_selftest = engine.self_test()  # type: ignore[attr-defined]
    if recomputed_full != full:
        fail("full archive absence report is not reproducible")
    if recomputed_minimum != minimum:
        fail("minimum archive absence report is not reproducible")
    if recomputed_selftest != selftest:
        fail("archive self-test report is not reproducible")

    lane = import_module("PROOFCORE/verifiers/verify_streamfold_archive_payload_search_lane_rev0862.py", "ev_rev0862_archive_lane_validator")
    accept = ROOT / "PROOFCORE/fixtures/accept/ev-streamfold-archive-payload-search.rev0862.accept.json"
    result = lane.verify_fixture(accept, skip_parent_replay=True)  # type: ignore[attr-defined]
    if not isinstance(result, dict) or result.get("ok") is not True:
        fail("archive payload search lane accept fixture returned unexpected result")
    reject = ROOT / "PROOFCORE/fixtures/reject/ev-streamfold-archive-payload-search.rev0862.reject.json"
    try:
        lane.verify_fixture(reject, skip_parent_replay=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    else:
        fail("archive payload search lane reject fixture unexpectedly verified")

    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    require_text("OVERLAY_COMMANDS.md", ["validate_streamfold_archive_payload_search_rev0862.py", "locate_streamfold_payload_archives_rev0862.py", "rev0861 historical checkpoint"])
    require_text("PROOFCORE/README.md", ["rev0862", "ZIP-aware archive payload search", "cloudtainer ZIP artifacts"])
    require_text("AUDIT/ARCHIVE_PAYLOAD_SEARCH_REV0862.md", ["ZIP-aware", "Cloudtainer EvidenceVault ZIP artifacts scanned", "Payload matches"])

    print("streamfold-archive-payload-search-rev0862: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
