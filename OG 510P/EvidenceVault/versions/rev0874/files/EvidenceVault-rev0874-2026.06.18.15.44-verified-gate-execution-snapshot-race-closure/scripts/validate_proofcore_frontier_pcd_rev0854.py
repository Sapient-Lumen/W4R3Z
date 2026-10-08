#!/usr/bin/env python3
"""Validate rev0854 parent-linked proofcore frontier PCD lane."""
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
    for path in (ROOT / "CHECKS").glob("patch-bundle-identity-rev*.json"):
        candidates.append(path.name)
    numbers: list[int] = []
    for text in candidates:
        for match in REVISION_RE.finditer(text):
            numbers.append(int(match.group(1)))
    return max(numbers) if numbers else None

def fail(message: str) -> None:
    print(f"proofcore-frontier-pcd-rev0854: FAIL: {message}", file=sys.stderr)
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
        "PROOFCORE/frontier/rev0854/proof_obligation_frontier.rev0854.json",
        "PROOFCORE/frontier/rev0854/proof_obligation_frontier.rev0854.csv",
        "PROOFCORE/parent_snapshots/rev0853/CHECKS-overlay-manifest.json",
        "PROOFCORE/parent_snapshots/rev0853/CHECKS-overlay-manifest.sha256",
        "PROOFCORE/parent_snapshots/rev0853/CHECKS-patches.sha256",
        "PROOFCORE/claims/ev-proofcore-frontier.rev0854.claim.json",
        "PROOFCORE/public_inputs/ev-proofcore-frontier.rev0854.public-input.json",
        "PROOFCORE/commitments/ev-proofcore-frontier.rev0854.commitments.json",
        "PROOFCORE/certificates/ev-proofcore-frontier.rev0854.pcd.json",
        "PROOFCORE/witness_policy/ev-proofcore-frontier.rev0854.md",
        "PROOFCORE/fixtures/accept/ev-proofcore-frontier.rev0854.accept.json",
        "PROOFCORE/fixtures/reject/ev-proofcore-frontier.rev0854.reject.json",
        "PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py",
        "AUDIT/PROOFCORE_FRONTIER_PCD_REV0854.json",
        "AUDIT/PROOFCORE_FRONTIER_PCD_REV0854.md",
    ]
    for rel in required:
        require_file(rel)
    claim = load_json("PROOFCORE/claims/ev-proofcore-frontier.rev0854.claim.json")
    public_inputs = load_json("PROOFCORE/public_inputs/ev-proofcore-frontier.rev0854.public-input.json")
    cert = load_json("PROOFCORE/certificates/ev-proofcore-frontier.rev0854.pcd.json")
    frontier = load_json("PROOFCORE/frontier/rev0854/proof_obligation_frontier.rev0854.json")
    audit = load_json("AUDIT/PROOFCORE_FRONTIER_PCD_REV0854.json")
    if claim.get("revision") != "rev0854" or public_inputs.get("revision") != "rev0854" or cert.get("revision") != "rev0854":
        fail("revision mismatch")
    if cert.get("proof_system", {}).get("snark") or cert.get("proof_system", {}).get("zero_knowledge"):
        fail("frontier certificate must not claim SNARK/ZK")
    exp = public_inputs.get("frontier_expectation", {})
    if exp.get("recommended_next_group_id") != "streamfold_sumcheck_toy_v2_family":
        fail("unexpected recommended frontier group")
    groups = frontier.get("groups", [])
    if len(groups) != exp.get("selected_group_count") or len(groups) < 4:
        fail("frontier group count mismatch or too small")
    rec = [g for g in groups if g.get("group_id") == "streamfold_sumcheck_toy_v2_family"]
    if len(rec) != 1:
        fail("recommended group absent")
    role_counts = rec[0].get("role_counts", {})
    for role in ["abi_ir_or_protocol_ir", "public_input_or_commitment", "attestation_or_receipt"]:
        if role not in role_counts:
            fail(f"recommended group missing role {role}")
    if rec[0].get("path_count", 0) < 10:
        fail("recommended group unexpectedly small")
    with (ROOT / "PROOFCORE/frontier/rev0854/proof_obligation_frontier.rev0854.csv").open(newline="", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    if len({row.get("path") for row in csv_rows}) != exp.get("selected_unique_path_count"):
        fail("frontier CSV unique path count mismatch")
    if any((ROOT / str(row.get("path"))).exists() for row in csv_rows):
        fail("selected frontier payload unexpectedly present in overlay")
    rights = load_json("RIGHTS/component_license_ledger.json")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights status drifted")
    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"root rights sentinel was invented: {sentinel}")
    if audit.get("status") != "parent_linked_frontier_pcd_lane_added":
        fail("audit status drifted")
    require_text("AUDIT/PROOFCORE_FRONTIER_PCD_REV0854.md", ["Recommended next lane", "streamfold_sumcheck_toy_v2_family", "parent-linked"])
    require_text("PROOFCORE/README.md", ["rev0854 parent-linked frontier lane", "streamfold_sumcheck_toy_v2_family", "not a zk-SNARK"])
    require_text("OVERLAY_COMMANDS.md", ["validate_proofcore_frontier_pcd_rev0854.py", "historical checkpoint", "verify_proofcore_frontier_rev0854.py"])
    current_rev = current_revision_number() or 854
    if current_rev > 854:
        require_file("PROOFCORE/parent_snapshots/rev0854/CHECKS-overlay-manifest.json")
        require_file("PROOFCORE/parent_snapshots/rev0854/CHECKS-overlay-manifest.sha256")
        require_file("PROOFCORE/parent_snapshots/rev0854/CHECKS-patches.sha256")
        require_text("OVERLAY_COMMANDS.md", ["rev0854 historical checkpoint", "verify_streamfold_sumcheck_lane_rev0855.py"])
        print("proofcore-frontier-pcd-rev0854: OK (historical checkpoint carried; use rev0855 parent replay)")
        return 0
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py", "--fixture", "PROOFCORE/fixtures/accept/ev-proofcore-frontier.rev0854.accept.json"], "proofcore-frontier-pcd-rev0854: OK")
    run_ok([sys.executable, "PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py", "--fixture", "PROOFCORE/fixtures/reject/ev-proofcore-frontier.rev0854.reject.json", "--expect-fail"], "expected failure observed")
    print("proofcore-frontier-pcd-rev0854: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
