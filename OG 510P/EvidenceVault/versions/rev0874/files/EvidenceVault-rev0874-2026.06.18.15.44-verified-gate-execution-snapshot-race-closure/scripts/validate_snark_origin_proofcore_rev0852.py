#!/usr/bin/env python3
"""Validate rev0852 SNARK-origin proofcore recovery surfaces."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_RE = re.compile(r"(zkrtp|streamfold|snark|zero|sumcheck|fri|pcs|halo2|lookup|fold|proof|receipt|attestation|witness|verifier|verify|constraint|circuit|commitment)", re.I)


def fail(message: str) -> None:
    print(f"snark-origin-proofcore-rev0852: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(rel: str) -> dict:
    try:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {rel}: {exc}")
    if not isinstance(data, dict):
        fail(f"{rel} must be a JSON object")
    return data


def require_text(rel: str, snippets: list[str]) -> str:
    path = ROOT / rel
    if not path.is_file() or path.is_symlink():
        fail(f"missing regular file: {rel}")
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        fail(f"{rel} must end with a newline")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        fail(f"{rel} missing required snippets: {missing}")
    return text


def index_rows() -> list[dict[str, str]]:
    path = ROOT / "INDEX" / "files.csv"
    if not path.is_file() or path.is_symlink():
        fail("missing carried canonical INDEX/files.csv")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def component(ledger: dict, component_id: str) -> dict:
    for row in ledger.get("components", []):
        if row.get("component_id") == component_id:
            return row
    fail(f"missing rights component {component_id}")


def main() -> int:
    audit = load_json("AUDIT/SNARK_ORIGIN_PROOFCORE_RECOVERY_REV0852.json")
    review = load_json("SESSION_REVIEW_REV0852.json")
    rights = load_json("RIGHTS/component_license_ledger.json")
    rows = index_rows()

    if audit.get("status") != "snark_origin_review_publication_block_preserved":
        fail("unexpected rev0852 audit status")
    if review.get("not_publication_ready") is not True or review.get("publication_block_preserved") is not True:
        fail("session review must preserve publication block")
    if rights.get("status") != "publication_blocked_pending_rights_decision":
        fail("rights ledger no longer records expected publication block")

    blockers = {row.get("id") for row in rights.get("blocking_findings", [])}
    if {"missing_root_license_or_notice", "missing_local_license_reference_targets"} - blockers:
        fail(f"rights blockers changed unexpectedly: {sorted(blockers)}")

    zkrtp = component(rights, "zkrtp")
    streamfold = component(rights, "streamfold")
    if zkrtp.get("observed_file_count_under_existing_paths") != 193:
        fail("unexpected zkrtp rights-ledger file count")
    if streamfold.get("observed_file_count_under_existing_paths") != 83:
        fail("unexpected streamfold rights-ledger file count")
    if "without retained sources/ root" not in zkrtp.get("note", ""):
        fail("zkrtp source/root limitation is no longer recorded")
    if "without retained sources/ root" not in streamfold.get("note", ""):
        fail("streamfold source/root limitation is no longer recorded")

    proof_rows = [row for row in rows if PROOF_RE.search(row.get("path", ""))]
    if len(proof_rows) < 1000:
        fail(f"proof-signal index scan unexpectedly low: {len(proof_rows)}")
    present = [row for row in proof_rows if (ROOT / row["path"]).exists()]
    if present:
        fail("overlay unexpectedly contains canonical proof payload paths; audit assumptions need update")

    required_index_paths = {
        "papers/ev_zkrtp.tex",
        "papers/ev_streamfold.tex",
        "artifacts/curated/streamfold/abi_ir/sumcheck_toy_v2.json",
        "artifacts/curated/streamfold/abi_ir/fri_open_toy_v3_mined.json",
        "artifacts/curated/streamfold/abi_ir/halo2_multiopen_toy_v1.json",
        "certs/curated/zkrtp_v2/attestations/policy_proof_accept.dsse.json",
        "schemas/policy_circuit_cost_model.schema.json",
        "sources/ocf_llm/tools/verifiers/toy_sic_zk_verifier_v1.py",
    }
    index_paths = {row.get("path") for row in rows}
    missing = sorted(required_index_paths - index_paths)
    if missing:
        fail("carried canonical index missing proofcore sentinel paths: " + ", ".join(missing))

    for sentinel in ["LICENSE", "COPYING", "NOTICE"]:
        if (ROOT / sentinel).exists():
            fail(f"rev0852 must not invent root rights sentinel: {sentinel}")

    require_text(
        "AUDIT/SNARK_ORIGIN_PROOFCORE_RECOVERY_REV0852.md",
        ["SNARK-origin proofcore recovery", "What is missing", "What should change", "Speculative read", "Publication remains blocked"],
    )
    require_text(
        "PROOFCORE_RECOVERY_PLAN_REV0852.md",
        ["proof-carrying research vault", "Phase 1", "Phase 3", "stop conditions", "Publication remains blocked"],
    )
    require_text(
        "SESSION_REVIEW_REV0852.md",
        ["SNARK-origin proofcore recovery", "proof-carrying evidence vault", "0 of the", "Still publication-blocked"],
    )
    require_text(
        "OVERLAY_COMMANDS.md",
        ["validate_snark_origin_proofcore_rev0852.py", "Do not use `make gate`"],
    )
    require_text(
        "README.md",
        ["EvidenceVault rev0852 SNARK-origin proofcore recovery overlay bundle", "proof-carrying evidence", "Use these overlay checks first"],
    )

    metrics = audit.get("metrics", {})
    if metrics.get("broad_proof_signal_paths") != len(proof_rows):
        fail("audit proof-signal metric does not match carried index scan")
    if metrics.get("broad_proof_signal_paths_present_in_overlay") != 0:
        fail("audit must record proof payload absence from overlay")
    if metrics.get("rights_status") != "publication_blocked_pending_rights_decision":
        fail("audit rights status drifted")

    print("snark-origin-proofcore-rev0852: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
