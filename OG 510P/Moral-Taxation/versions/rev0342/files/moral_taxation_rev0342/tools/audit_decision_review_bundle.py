#!/usr/bin/env python3
"""Audit the exported decision review bundle boundary."""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
from typing import Any, Dict, Iterable, List, Mapping

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
CASE_ID = "GC-001"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
AS_OF_DATE = "2026-06-18"


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def walk_keys(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            current = f"{path}.{key}"
            yield current
            yield from walk_keys(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_keys(child, f"{path}[{index}]")


exporter = load_module("export_decision_review_bundle", root / "tools/export_decision_review_bundle.py")
verifier = load_module("verify_external_attestation", root / "tools/verify_external_attestation.py")
executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")

packet = exporter.build_review_bundle(root, CASE_ID, ROUTE_LIMIT, FACTS_ONLY_LIMIT, AS_OF_DATE)

if packet.get("runtime_status") != exporter.RUNTIME_STATUS:
    errors.append("decision review bundle runtime status is stale")
if packet.get("kind") != exporter.BUNDLE_KIND_SANDBOX:
    errors.append("decision review bundle kind is stale")
if packet.get("production_finalization_allowed") is not False:
    errors.append("sandbox review bundle must not allow production finalization")
if packet.get("all_review_gates_passed") is not True:
    errors.append("review gates did not all pass")
if not packet.get("review_bundle_hash"):
    errors.append("review bundle is missing its self hash")

text = json.dumps(packet, sort_keys=True)
if "PRIVATE KEY" in text or "private_key" in text.lower() or "secret_key" in text.lower():
    errors.append("review bundle leaked private or secret key material")
for key_path in walk_keys(packet):
    lower = key_path.lower()
    if "private" in lower or "secret" in lower:
        errors.append(f"review bundle exposes secret-looking key path: {key_path}")

scope = packet.get("review_scope", {})
ledger_summary = packet.get("ledger_summary", {})
promo_summary = packet.get("promotion_summary", {})
output_summary = packet.get("decision_output_summary", {})
records = packet.get("ledger_record_index", [])
evidence_records = packet.get("evidence_review_records", [])

if scope.get("promotion_mode") != "sandbox_positive_path_test":
    errors.append("review bundle must preserve sandbox promotion mode")
if scope.get("route_limit") != ROUTE_LIMIT or scope.get("facts_only_candidate_limit") != FACTS_ONLY_LIMIT:
    errors.append("review bundle scope lost default route/facts limits")
if scope.get("adapter_record_count") != 22:
    errors.append("GC-001 review bundle should cover the full default selected route set")
if len(records) != scope.get("adapter_record_count") or len(evidence_records) != scope.get("adapter_record_count"):
    errors.append("review bundle must carry one ledger and evidence review record per adapter")
if ledger_summary.get("trusted_external_attestation_verified_record_count") != scope.get("adapter_record_count"):
    errors.append("review bundle did not verify every attestation")
if ledger_summary.get("strict_model_input_source_proof_record_count") != ledger_summary.get("strict_model_input_source_required_record_count"):
    errors.append("review bundle missing strict model-input source proofs")
if ledger_summary.get("strict_authority_evidence_proof_record_count") != ledger_summary.get("strict_authority_evidence_required_record_count"):
    errors.append("review bundle missing strict authority-source proofs")
if packet.get("replay_summary", {}).get("mismatch_count") != 0:
    errors.append("review bundle replay must be clean")
if promo_summary.get("promoted_case_count") != 0 or promo_summary.get("sandbox_positive_path_case_count") != 1:
    errors.append("sandbox review bundle must pass mechanics but not production promotion")
if output_summary.get("finalized_case_count") != 0 or output_summary.get("held_case_count") != 1:
    errors.append("decision output inside review bundle must remain held")
case_output = packet.get("case_decision_output", {})
if case_output.get("can_issue_final_determination") is not False:
    errors.append("case decision output must not issue a final determination")
if not case_output.get("hold_reasons"):
    errors.append("held review output must carry hold reasons")

# Re-verify every embedded evidence payload and attestation from the exported
# packet rather than trusting the builder's verification summary.
verification_bundle = {"trusted_external_attestation_verifier": packet.get("trust_store_public_view", {})}
seen_bindings = set()
for item in evidence_records:
    evidence = dict(item.get("evidence_payload", {}))
    evidence["external_attestation"] = item.get("external_attestation", {})
    verification = verifier.verification_for_evidence(evidence, verification_bundle)
    if verification.get("verifier_status") != verifier.STATUS_VERIFIED or verification.get("trusted_external_attestation") is not True:
        errors.append(f"embedded evidence failed independent verification: {item.get('lookup_key')}")
    if verification.get("evidence_payload_hash") != item.get("evidence_payload_hash"):
        errors.append(f"embedded evidence hash mismatch: {item.get('lookup_key')}")
    signed = item.get("external_attestation", {}).get("signed_payload", {})
    if signed.get("adapter_binding_hash") != item.get("adapter_binding_hash"):
        errors.append(f"signed adapter binding does not match evidence record: {item.get('lookup_key')}")
    seen_bindings.add(item.get("adapter_binding_hash"))
if len(seen_bindings) != len(evidence_records):
    errors.append("review bundle adapter bindings should be unique across the selected adapter set")

# Prove tampering the review packet breaks re-verification.
if evidence_records:
    tampered = copy.deepcopy(evidence_records[0])
    tampered_payload = dict(tampered.get("evidence_payload", {}))
    tampered_payload["adapter_binding_hash"] = "tampered-binding-hash"
    tampered_payload["external_attestation"] = tampered.get("external_attestation", {})
    tampered_verification = verifier.verification_for_evidence(tampered_payload, verification_bundle)
    if tampered_verification.get("verifier_status") == verifier.STATUS_VERIFIED:
        errors.append("tampered embedded evidence unexpectedly verified")
else:
    errors.append("review bundle did not expose evidence records for tamper probe")

# Exercise the CLI/export serialization path as a separate handoff surface.
with tempfile.TemporaryDirectory() as tmp:
    out = pathlib.Path(tmp) / "review-bundle.json"
    subprocess.run(
        [sys.executable, str(root / "tools/export_decision_review_bundle.py"), str(root), "--case-id", CASE_ID, "--output", str(out), "--json"],
        check=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )
    exported = json.loads(out.read_text(encoding="utf-8"))
    if exported.get("review_bundle_hash") != packet.get("review_bundle_hash"):
        errors.append("CLI-exported review bundle hash drifted from in-process builder")
    if "PRIVATE KEY" in out.read_text(encoding="utf-8"):
        errors.append("CLI-exported review bundle leaked private key text")

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected = {
    "decision_review_bundle_required": True,
    "decision_review_bundle_runtime_status": exporter.RUNTIME_STATUS,
    "decision_review_bundle_case_id": CASE_ID,
    "decision_review_bundle_adapter_record_count": scope.get("adapter_record_count"),
    "decision_review_bundle_verified_record_count": ledger_summary.get("trusted_external_attestation_verified_record_count"),
    "decision_review_bundle_replay_mismatch_count": packet.get("replay_summary", {}).get("mismatch_count"),
    "decision_review_bundle_finalized_case_count": output_summary.get("finalized_case_count"),
    "decision_review_bundle_sandbox_case_count": promo_summary.get("sandbox_positive_path_case_count"),
    "decision_review_bundle_production_finalization_allowed": packet.get("production_finalization_allowed"),
    "decision_review_bundle_private_key_leak_count": 0,
}
for key, value in expected.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("decision_review_bundle_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json decision_review_bundle_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    required_lines = [
        f"Decision review bundle runtime status: {exporter.RUNTIME_STATUS}",
        f"Review case: {CASE_ID}",
        f"Review adapter records: {scope.get('adapter_record_count')}",
        f"Embedded attestations verified: {ledger_summary.get('trusted_external_attestation_verified_record_count')}/{scope.get('adapter_record_count')}",
        f"Replay mismatches: {packet.get('replay_summary', {}).get('mismatch_count')}",
        f"Finalized cases inside review bundle: {output_summary.get('finalized_case_count')}",
        f"Sandbox positive-path cases inside review bundle: {promo_summary.get('sandbox_positive_path_case_count')}",
        "Private key material exported: no",
    ]
    for line in required_lines:
        if line not in report:
            errors.append(f"decision review bundle report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("decision review bundle audit ok")
