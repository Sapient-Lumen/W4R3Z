#!/usr/bin/env python3
"""Validate the rev0859 payload-receipt liveness proofcore lane."""
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
    print(f"payload-receipt-liveness-rev0859: FAIL: {message}", file=sys.stderr)
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


def run_ok(args: list[str], marker: str, timeout: int = 45) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(args, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=timeout)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        fail(f"command failed {args}: stdout={result.stdout!r} stderr={result.stderr!r}")
    if marker not in output:
        fail(f"command output missing {marker!r}: {output!r}")
    return output



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


def assert_inprocess_verifiers() -> None:
    receipt_module = import_module("PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py", "ev_rev0859_receipt_validator")
    for receipt in [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json",
    ]:
        result = receipt_module.verify_receipt(ROOT, receipt)  # type: ignore[attr-defined]
        if not isinstance(result, dict) or result.get("ok") is not True:
            fail(f"in-process receipt verifier returned unexpected result for {receipt}")
    try:
        receipt_module.verify_receipt(ROOT, "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json")  # type: ignore[attr-defined]
    except Exception:
        pass
    else:
        fail("tampered receipt unexpectedly verified")
    lane_module = import_module("PROOFCORE/verifiers/verify_streamfold_payload_receipt_liveness_lane_rev0859.py", "ev_rev0859_liveness_lane_validator")
    accept = ROOT / "PROOFCORE/fixtures/accept/ev-streamfold-payload-receipt-liveness.rev0859.accept.json"
    result = lane_module.verify_fixture(accept, skip_parent_replay=True)  # type: ignore[attr-defined]
    if not isinstance(result, dict) or result.get("ok") is not True:
        fail("liveness lane accept fixture returned unexpected result")
    reject = ROOT / "PROOFCORE/fixtures/reject/ev-streamfold-payload-receipt-liveness.rev0859.reject.json"
    try:
        lane_module.verify_fixture(reject, skip_parent_replay=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    else:
        fail("liveness lane reject fixture unexpectedly verified")

def main() -> int:
    required = [
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0859/receipt_liveness_contract.rev0859.json",
        "PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0859/README.md",
        "PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py",
        "PROOFCORE/verifiers/verify_streamfold_payload_receipt_liveness_lane_rev0859.py",
        "PROOFCORE/parent_snapshots/rev0858/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0858/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0858/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-streamfold-payload-receipt-liveness.rev0859.claim.json",
        "PROOFCORE/public_inputs/ev-streamfold-payload-receipt-liveness.rev0859.public-input.json",
        "PROOFCORE/commitments/ev-streamfold-payload-receipt-liveness.rev0859.commitments.json",
        "PROOFCORE/certificates/ev-streamfold-payload-receipt-liveness.rev0859.pcd.json",
        "PROOFCORE/fixtures/accept/ev-streamfold-payload-receipt-liveness.rev0859.accept.json",
        "PROOFCORE/fixtures/reject/ev-streamfold-payload-receipt-liveness.rev0859.reject.json",
        "PROOFCORE/witness_policy/ev-streamfold-payload-receipt-liveness.rev0859.md",
        "PROOFCORE/verifier_surface.rev0859.json",
        "AUDIT/PAYLOAD_RECEIPT_LIVENESS_REV0859.json",
        "AUDIT/PAYLOAD_RECEIPT_LIVENESS_REV0859.md",
    ]
    for rel in required:
        require_file(rel)

    current_rev = current_revision_number() or 859
    if current_rev > 859:
        require_file("PROOFCORE/parent_snapshots/rev0859/CHECKS-overlay-manifest.json")
        require_file("PROOFCORE/parent_snapshots/rev0859/CHECKS-overlay-manifest.sha256")
        require_file("PROOFCORE/parent_snapshots/rev0859/CHECKS-patches.sha256")
        require_file("PROOFCORE/verifiers/verify_streamfold_payload_graft_lane_rev0860.py")
        require_text("OVERLAY_COMMANDS.md", ["rev0859 historical checkpoint", "verify_streamfold_payload_graft_lane_rev0860.py"])
        print("payload-receipt-liveness-rev0859: OK (historical checkpoint carried; use rev0860 payload graft parent replay)")
        return 0

    public_inputs = load_json("PROOFCORE/public_inputs/ev-streamfold-payload-receipt-liveness.rev0859.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-streamfold-payload-receipt-liveness.rev0859.pcd.json")
    audit = load_json("AUDIT/PAYLOAD_RECEIPT_LIVENESS_REV0859.json")
    contract = load_json("PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0859/receipt_liveness_contract.rev0859.json")
    if public_inputs.get("revision") != "rev0859" or cert.get("revision") != "rev0859" or audit.get("revision") != "rev0859" or contract.get("revision") != "rev0859":
        fail("revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge") or cert.get("proof_system", {}).get("succinct"):
        fail("rev0859 certificate must not claim SNARK/ZK/succinct")
    if audit.get("status") != "legacy_subprocess_receipt_verifier_quarantined_inprocess_replay_active":
        fail("audit status drifted")
    live = public_inputs.get("receipt_liveness", {})
    if live.get("legacy_receipt_verifier_status") != "historical_hash_bound_liveness_quarantined_not_active_endpoint":
        fail("legacy verifier quarantine status drifted")
    if live.get("expected_full_absent_count") != 17 or live.get("expected_minimum_absent_count") != 4:
        fail("payload absence count drifted")
    if public_inputs.get("parent_checkpoint", {}).get("parent_revision") != "rev0858":
        fail("parent checkpoint mismatch")
    if public_inputs.get("payload_state", {}).get("canonical_streamfold_payloads_present_in_overlay") != 0:
        fail("payload presence drifted")
    legacy_text = (ROOT / live.get("legacy_receipt_verifier_path")).read_text(encoding="utf-8")
    source_block = legacy_text[legacy_text.find("def run_source_verifier"):legacy_text.find("def verify_rights_blocked")]
    if "stdout=subprocess.PIPE" not in source_block or "timeout=" in source_block:
        fail("legacy liveness-risk source shape no longer matches audit")
    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")

    require_text("PROOFCORE/README.md", ["rev0859", "in-process", "liveness-quarantined"])
    require_text("OVERLAY_COMMANDS.md", ["validate_payload_receipt_liveness_rev0859.py", "verify_streamfold_payload_receipt_inprocess_rev0859.py", "liveness-quarantined"])
    require_text("AUDIT/PAYLOAD_RECEIPT_LIVENESS_REV0859.md", ["in-process verifier", "liveness-quarantined", "Still blocked"])
    require_text("scripts/validate_framed_transcript_receipt_rev0858.py", ["historical checkpoint carried; use rev0859 in-process receipt replay"])

    assert_inprocess_verifiers()
    print("payload-receipt-liveness-rev0859: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
