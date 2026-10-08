#!/usr/bin/env python3
"""Validate the rev0860 streamfold payload graft lane."""
from __future__ import annotations

import importlib.util
import json
import os
import re
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
    print(f"streamfold-payload-graft-rev0860: FAIL: {message}", file=sys.stderr)
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


def run_ok(args: list[str], marker: str, timeout: int = 60) -> str:
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
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/payload_graft_contract.rev0860.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/payload_graft_dry_run.full.rev0860.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/payload_graft_dry_run.minimum.rev0860.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/graft_engine_selftest.rev0860.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/README.md",
        "PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py",
        "PROOFCORE/verifiers/verify_streamfold_payload_graft_lane_rev0860.py",
        "PROOFCORE/parent_snapshots/rev0859/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0859/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0859/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-payload-graft.rev0860.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-payload-graft.rev0860.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-payload-graft.rev0860.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-payload-graft.rev0860.pcd.json",
        "PROOFCORE/fixtures/accept/ev-streamfold-payload-graft.rev0860.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-payload-graft.rev0860.reject.json",
        "PROOFCORE/witness_policy/ev-streamfold-payload-graft.rev0860.md",
        "PROOFCORE/verifier_surface.rev0860.json",
        "AUDIT/PAYLOAD_GRAFT_ENGINE_REV0860.json",
        "AUDIT/PAYLOAD_GRAFT_ENGINE_REV0860.md",
    ]
    for rel in required:
        require_file(rel)

    current_rev = current_revision_number() or 860
    if current_rev > 860:
        require_file("PROOFCORE/parent_snapshots/rev0860/CHECKS-overlay-manifest.json")
        require_file("PROOFCORE/parent_snapshots/rev0860/CHECKS-overlay-manifest.sha256")
        require_file("PROOFCORE/parent_snapshots/rev0860/CHECKS-patches.sha256")
        require_file("PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py")
        require_text("OVERLAY_COMMANDS.md", ["rev0860 historical checkpoint", "verify_streamfold_loose_payload_locator_lane_rev0861.py"])
        print("streamfold-payload-graft-rev0860: OK (historical checkpoint carried; use rev0861 loose payload locator parent replay)")
        return 0

    contract = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0860/payload_graft_contract.rev0860.json")
    audit = load_json("AUDIT/PAYLOAD_GRAFT_ENGINE_REV0860.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-payload-graft.rev0860.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-payload-graft.rev0860.pcd.json")
    if contract.get("revision") != "rev0860" or audit.get("revision") != "rev0860" or public_inputs.get("revision") != "rev0860" or cert.get("revision") != "rev0860":
        fail("revision mismatch")
    if contract.get("status") != "graft_engine_ready_no_payload_bytes_in_overlay":
        fail("graft contract status drifted")
    if audit.get("status") != "candidate_graft_engine_ready_payloads_still_absent":
        fail("audit status drifted")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0859":
        fail("parent checkpoint mismatch")
    if public_inputs.get("payload_state", {}).get("canonical_streamfold_payloads_present_in_overlay") != 0:
        fail("payload presence drifted")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge") or cert.get("proof_system", {}).get("succinct"):
        fail("rev0860 certificate must not claim SNARK/ZK/succinct")

    graft_module = import_module("PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py", "ev_rev0860_graft_engine_validator")
    full = graft_module.prepare_report(None, None, mode="full")  # type: ignore[attr-defined]
    minimum = graft_module.prepare_report(None, None, mode="minimum")  # type: ignore[attr-defined]
    selftest = graft_module.self_test()  # type: ignore[attr-defined]
    if full.get("selected_path_count") != 17 or full.get("overlay_payloads_absent") != 17:
        fail("full dry-run report drifted")
    if minimum.get("selected_path_count") != 4 or minimum.get("overlay_payloads_absent") != 4:
        fail("minimum dry-run report drifted")
    controls = selftest.get("rejected_controls", {})
    if not all(controls.get(k) is True for k in ["hash_mismatch", "path_escape", "stage_inside_overlay", "symlink_parent"]):
        fail("graft self-test reject controls incomplete")

    lane_module = import_module("PROOFCORE/verifiers/verify_streamfold_payload_graft_lane_rev0860.py", "ev_rev0860_graft_lane_validator")
    accept = ROOT / "PROOFCORE/fixtures/accept/ev-streamfold-payload-graft.rev0860.accept.json"
    result = lane_module.verify_fixture(accept, skip_parent_replay=True)  # type: ignore[attr-defined]
    if not isinstance(result, dict) or result.get("ok") is not True:
        fail("graft lane accept fixture returned unexpected result")
    reject = ROOT / "PROOFCORE/fixtures/reject/ev-streamfold-payload-graft.rev0860.reject.json"
    try:
        lane_module.verify_fixture(reject, skip_parent_replay=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    else:
        fail("graft lane reject fixture unexpectedly verified")

    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    require_text("OVERLAY_COMMANDS.md", ["validate_streamfold_payload_graft_rev0860.py", "prepare_streamfold_payload_graft_rev0860.py", "rev0859 historical checkpoint"])
    require_text("PROOFCORE/README.md", ["rev0860", "payload graft", "candidate-root"])
    require_text("AUDIT/PAYLOAD_GRAFT_ENGINE_REV0860.md", ["graft engine", "Still blocked", "minimum first recovery set"])
    require_text("scripts/validate_payload_receipt_liveness_rev0859.py", ["historical checkpoint carried; use rev0860 payload graft parent replay"])

    print("streamfold-payload-graft-rev0860: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
