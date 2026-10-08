#!/usr/bin/env python3
"""Audit promotion-gated decision-output materialization.

The audit reuses the strict replay ledger instead of materializing the same
ledger repeatedly; tamper replay remains explicit.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Mapping

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors: List[str] = []
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
OUTPUT_STATUS = "decision_output_packets_materialized"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def load_answers() -> Dict[str, Any]:
    cache_path = os.environ.get("MT_ANSWER_PACKET_CACHE")
    if cache_path and pathlib.Path(cache_path).exists():
        raw = pathlib.Path(cache_path).read_text(encoding="utf-8")
    else:
        raw = subprocess.check_output(
            [sys.executable, str(root / "tools/answer_case.py"), str(root), "--all", "--route-limit", str(ROUTE_LIMIT), "--facts-only-candidate-limit", str(FACTS_ONLY_LIMIT), "--json"],
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    return json.loads(raw)


def tamper_all_evidence(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(dict(bundle))
    for pool_name in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        pool = out.get(pool_name, {})
        if isinstance(pool, dict):
            for key, evidence in pool.items():
                if isinstance(evidence, dict):
                    evidence["decision_output_tamper_probe"] = f"tampered:{key}"
    return out


materializer = load_module("materialize_decision_outputs", root / "tools/materialize_decision_outputs.py")
ledger_builder = load_module("build_evidence_replay_ledger", root / "tools/build_evidence_replay_ledger.py")
promoter = load_module("promote_decision_release", root / "tools/promote_decision_release.py")
runner = load_module("run_evidence_producers", root / "tools/run_evidence_producers.py")

receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
as_of_date = str(receipt.get("created_at_utc", "2026-06-18"))[:10]
payload = load_answers()
if payload.get("runtime_status") != ANSWER_STATUS:
    errors.append("answer payload runtime_status is stale")
answers = payload.get("answers", [])
case_count = len(answers)
adapter_check_count = sum(len(a.get("disposition", {}).get("adapter_checks", [])) for a in answers)

strict_bundle = materializer.strict_schema_test_evidence_bundle_for_answers(root, answers, as_of_date)
ledger = ledger_builder.ledger_for_answers(root, answers, strict_bundle)
strict_promotion = promoter.promotion_from_ledger(ledger, None)
strict_outputs = materializer.materialize_outputs_from_promotion(answers, ledger, strict_promotion)
empty_outputs = materializer.materialize_outputs_for_answers(root, answers, {}, replay_check=False)
interface_bundle = runner.bundle_for_answers(root, answers, runner.MODE_INTERFACE_FIXTURE, as_of_date, strict_model_input_sources=True, strict_authority_evidence=True)
interface_outputs = materializer.materialize_outputs_for_answers(root, answers, interface_bundle, replay_check=False)

tampered_ledger = ledger_builder.ledger_for_answers(root, answers, tamper_all_evidence(strict_bundle))
tamper_comparison = ledger_builder.replay_compare(ledger, tampered_ledger)
tamper_promotion = promoter.promotion_from_ledger(ledger, tamper_comparison)
tamper_outputs = materializer.materialize_outputs_from_promotion(answers, ledger, tamper_promotion)

summary = strict_outputs.get("summary", {})
if strict_outputs.get("runtime_status") != OUTPUT_STATUS:
    errors.append("decision-output materializer runtime_status is stale")
if strict_outputs.get("promotion_runtime_status") != "decision_promotion_gate_evaluated":
    errors.append("decision outputs must derive from the promotion gate")
if strict_outputs.get("ledger_runtime_status") != "evidence_replay_ledger_generated":
    errors.append("decision outputs must derive from a replay ledger")
if summary.get("case_count") != case_count:
    errors.append("decision output count must equal answer count")
if summary.get("adapter_record_count") != adapter_check_count:
    errors.append("decision output adapter-record count must equal adapter checks")
if summary.get("finalized_case_count") != 0 or summary.get("held_case_count") != case_count:
    errors.append("archive-generated strict-schema evidence must finalize zero cases and hold all cases")
if summary.get("raw_evidence_stored") is not False:
    errors.append("decision outputs must report raw_evidence_stored=false")
if materializer.recursive_forbidden_key_hits(strict_outputs):
    errors.append("decision outputs contain forbidden raw evidence/model snapshots")
if "not current law" not in str(strict_outputs.get("non_doctrine_warning", "")):
    errors.append("decision-output packet must carry a non-doctrine warning")
if not strict_outputs.get("decision_output_packet_hash"):
    errors.append("decision-output packet missing top-level hash")

case_outputs = strict_outputs.get("case_decision_outputs", [])
if len(case_outputs) != case_count:
    errors.append("decision outputs must emit one case packet per answer")
for out in case_outputs:
    cid = out.get("case_id")
    if out.get("can_issue_final_determination") is not False:
        errors.append(f"strict-schema decision output {cid} was incorrectly finalized")
    for field in ["decision_output_hash", "case_promotion_hash", "ledger_hash", "evidence_bundle_hash", "producer_contract_manifest_hash"]:
        if not out.get(field):
            errors.append(f"decision output {cid} missing {field}")
    if "not current law" not in str(out.get("decision_output_non_doctrine_warning", "")):
        errors.append(f"decision output {cid} missing non-doctrine warning")
    if not out.get("ordered_route_ids") or not out.get("recommended_sequence"):
        errors.append(f"decision output {cid} missing route/sequence substance")
    if not out.get("hold_reasons") or not out.get("remaining_cannot_finalize_until"):
        errors.append(f"held decision output {cid} missing hold reasons")
    if "held" not in str(out.get("decision_output_status", "")):
        errors.append(f"strict-schema decision output {cid} must have held status")
    records = out.get("case_record_hashes", [])
    if not records:
        errors.append(f"decision output {cid} missing adapter record hashes")
    for record in records:
        for field in ["adapter_packet_hash", "adapter_binding_hash", "evidence_hash", "producer_contract_hash", "evidence_truth_boundary_hash", "decision_trace_hash", "result_hash"]:
            if not record.get(field):
                errors.append(f"decision output {cid} record {record.get('record_key')} missing {field}")
        if record.get("strict_schema_test_fixture") is not True:
            errors.append(f"decision output {cid} record {record.get('record_key')} obscures strict-test origin")
        if record.get("evidence_origin") != "archive_generated_strict_schema_test_fixture":
            errors.append(f"decision output {cid} record {record.get('record_key')} has stale evidence origin")
        if record.get("promotion_eligible") is not False:
            errors.append(f"decision output {cid} record {record.get('record_key')} must be non-promotable")

for label, packet in [("empty", empty_outputs), ("interface", interface_outputs), ("tamper", tamper_outputs)]:
    if packet.get("summary", {}).get("finalized_case_count") != 0:
        errors.append(f"{label} decision outputs must finalize zero cases")
    if packet.get("summary", {}).get("held_case_count") != case_count:
        errors.append(f"{label} decision outputs must hold every case")
    if materializer.recursive_forbidden_key_hits(packet):
        errors.append(f"{label} decision outputs contain forbidden raw evidence/model snapshots")
if tamper_comparison.get("mismatch_count", 0) < adapter_check_count:
    errors.append("decision-output tamper comparison must detect evidence drift for every adapter")
if tamper_outputs.get("replay_mismatch_count", 0) <= 0:
    errors.append("tampered decision-output packet must expose replay mismatch count")

cube = json.loads((root / "cube-index.json").read_text(encoding="utf-8"))
expected = {
    "decision_output_materialization_required": True,
    "decision_output_runtime_status": OUTPUT_STATUS,
    "decision_output_case_count": case_count,
    "decision_output_adapter_record_count": adapter_check_count,
    "decision_output_strict_test_finalized_case_count": summary.get("finalized_case_count"),
    "decision_output_strict_test_held_case_count": summary.get("held_case_count"),
    "decision_output_empty_finalized_case_count": empty_outputs.get("summary", {}).get("finalized_case_count"),
    "decision_output_interface_finalized_case_count": interface_outputs.get("summary", {}).get("finalized_case_count"),
    "decision_output_tamper_mismatch_count": tamper_comparison.get("mismatch_count"),
    "decision_output_tamper_finalized_case_count": tamper_outputs.get("summary", {}).get("finalized_case_count"),
    "decision_output_raw_evidence_stored": summary.get("raw_evidence_stored"),
    "decision_output_status_counts": summary.get("decision_output_status_counts"),
}
for key, value in expected.items():
    if cube.get("audit_summary", {}).get(key) != value:
        errors.append(f"cube audit_summary {key} is stale")

report_rel = cube.get("decision_output_audit_report_path")
if not report_rel or not (root / report_rel).exists():
    errors.append("cube-index.json decision_output_audit_report_path must point to an existing file")
else:
    report = (root / report_rel).read_text(encoding="utf-8")
    lines = [
        f"Decision output runtime status: {OUTPUT_STATUS}",
        f"Answer packets checked: {case_count}",
        f"Adapter record hashes materialized: {adapter_check_count}/{adapter_check_count}",
        f"Strict-schema finalized cases: {summary.get('finalized_case_count')}/{case_count}",
        f"Strict-schema held cases: {summary.get('held_case_count')}/{case_count}",
        f"Empty-bundle finalized cases: {empty_outputs.get('summary', {}).get('finalized_case_count')}/{case_count}",
        f"Interface-fixture finalized cases: {interface_outputs.get('summary', {}).get('finalized_case_count')}/{case_count}",
        f"Tamper replay mismatches: {tamper_comparison.get('mismatch_count')}",
        f"Tamper finalized cases: {tamper_outputs.get('summary', {}).get('finalized_case_count')}/{case_count}",
        "Raw evidence stored: no",
    ]
    for line in lines:
        if line not in report:
            errors.append(f"decision output audit report is stale; missing line: {line}")

if errors:
    raise SystemExit("\n".join(errors))
print("decision output packet audit ok")
