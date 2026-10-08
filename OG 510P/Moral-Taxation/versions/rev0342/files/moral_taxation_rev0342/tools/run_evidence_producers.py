#!/usr/bin/env python3
"""Run registered evidence producers for decision-adapter packets.

The archive must not become a stale-law or stale-model database. This runner
therefore has three separate jobs:

* produce interface fixtures for audit-only contract checks;
* produce local model evidence only from an explicit model-input bundle; and
* accept/merge externally supplied current-law or jurisdiction evidence without
  treating that external bundle as archive doctrine.

Use tools/build_model_input_bundle.py to create reference input fixtures, and use
 tools/execute_decision_adapters.py to validate the emitted evidence bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Mapping, Sequence

RUNTIME_STATUS = "evidence_producer_runner_invoked"
RULE_VERSION = 5
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
MODEL_INPUT_STATUS = "explicit_model_input_bundle_generated"
MODEL_INPUT_SOURCE_STATUS = "model_input_source_manifest_generated"
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
MODE_INTERFACE_FIXTURE = "interface-fixture"
MODE_LOCAL_MODEL_ONLY = "local-model-only"
MODEL_ADAPTER_TYPES = {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}
EXTERNAL_ADAPTER_TYPES = {"current_law_refresh_adapter", "jurisdiction_scope_adapter"}


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def dedupe(values: Iterable[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for value in values:
        if value in (None, "", [], {}):
            continue
        key = json.dumps(value, sort_keys=True, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def load_answers(root: pathlib.Path, case_id: str | None, all_cases: bool, route_limit: int, facts_only_limit: int) -> List[Dict[str, Any]]:
    cache_path = os.environ.get("MT_ANSWER_PACKET_CACHE")
    if cache_path and pathlib.Path(cache_path).exists() and all_cases and not case_id:
        return json.loads(pathlib.Path(cache_path).read_text(encoding="utf-8")).get("answers", [])
    args = [
        sys.executable,
        str(root / "tools/answer_case.py"),
        str(root),
        "--route-limit",
        str(route_limit),
        "--facts-only-candidate-limit",
        str(facts_only_limit),
        "--json",
    ]
    if case_id:
        args.extend(["--case-id", case_id])
    elif all_cases:
        args.append("--all")
    else:
        raise SystemExit("provide --case-id or --all")
    raw = subprocess.check_output(args, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    payload = json.loads(raw)
    if payload.get("runtime_status") != ANSWER_STATUS:
        raise SystemExit("answer_case.py returned a stale runtime status")
    return payload.get("answers", [])


def contract_by_adapter_type(contracts: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for contract in contracts.get("producer_contracts", []):
        for typ in contract.get("adapter_types", []):
            out[str(typ)] = dict(contract)
    return out


def mode_for_packet(packet: Mapping[str, Any], execution_mode: str) -> str:
    typ = str(packet.get("adapter_type") or "")
    if execution_mode == MODE_INTERFACE_FIXTURE:
        return "registered_interface_fixture"
    if typ == "quantitative_model_adapter":
        return "local_reference_model_run_with_explicit_inputs"
    if typ == "floor_delivery_adapter":
        return "local_reference_model_run_with_explicit_inputs"
    if typ == "no_go_threshold_adapter":
        return "local_reference_threshold_screen_with_explicit_inputs"
    return "external_evidence_required"


def producer_fields(packet: Mapping[str, Any], contracts_by_type: Mapping[str, Mapping[str, Any]], as_of_date: str, execution_mode: str) -> Dict[str, Any]:
    contract = contracts_by_type.get(str(packet.get("adapter_type") or ""), {})
    return {
        "producer_id": contract.get("producer_id"),
        "producer_contract_version": contract.get("contract_version"),
        "evidence_kind": packet.get("adapter_type"),
        "created_at": as_of_date,
        "producer_mode": mode_for_packet(packet, execution_mode),
    }


def model_input_lookup_keys(packet: Mapping[str, Any]) -> List[str]:
    aid = str(packet.get("adapter_id") or "")
    case_id = str(packet.get("case_id") or "")
    rid = str(packet.get("route_id") or "")
    model = str(packet.get("model_class") or "")
    typ = str(packet.get("adapter_type") or "")
    case_aid = f"{case_id}:{aid}" if case_id and aid else aid
    return dedupe([
        case_aid,
        aid,
        f"model_input:{case_aid}" if case_aid else None,
        f"model_input:{aid}" if aid else None,
        f"model_input:{rid}:{model}" if rid and model else None,
        f"model_input:{typ}:{rid}:{model}" if typ and rid and model else None,
    ])


def input_for_packet(packet: Mapping[str, Any], model_input_bundle: Mapping[str, Any] | None) -> Dict[str, Any] | None:
    if not model_input_bundle:
        return None
    pools: List[Mapping[str, Any]] = []
    for name in ["model_inputs", "inputs", "adapter_inputs"]:
        value = model_input_bundle.get(name, {}) if isinstance(model_input_bundle, Mapping) else {}
        if isinstance(value, Mapping):
            pools.append(value)
    for key in model_input_lookup_keys(packet):
        for pool in pools:
            found = pool.get(key)
            if isinstance(found, Mapping):
                return dict(found)
    return None


def input_source_for_record(packet: Mapping[str, Any], input_record: Mapping[str, Any] | None, source_manifest: Mapping[str, Any] | None) -> Dict[str, Any] | None:
    if not input_record or not source_manifest:
        return None
    pools: List[Mapping[str, Any]] = []
    for name in ["model_input_sources", "input_sources", "source_records"]:
        value = source_manifest.get(name, {}) if isinstance(source_manifest, Mapping) else {}
        if isinstance(value, Mapping):
            pools.append(value)
    input_hash = str(input_record.get("input_record_hash") or "")
    keys = dedupe(model_input_lookup_keys(packet) + [
        str(input_record.get("adapter_id") or ""),
        f"{input_record.get('case_id')}:{input_record.get('adapter_id')}" if input_record.get("case_id") and input_record.get("adapter_id") else "",
        input_hash,
    ])
    for key in keys:
        for pool in pools:
            found = pool.get(key)
            if isinstance(found, Mapping):
                return dict(found)
    for pool in pools:
        for found in pool.values():
            if isinstance(found, Mapping) and str(found.get("model_input_record_hash") or "") == input_hash:
                return dict(found)
    return None


def input_source_proof_fields(source_record: Mapping[str, Any] | None, source_manifest: Mapping[str, Any] | None) -> Dict[str, Any]:
    if not source_record:
        return {}
    return {
        "model_input_source_manifest_id": source_record.get("manifest_id") or (source_manifest or {}).get("manifest_id"),
        "model_input_source_runtime_status": (source_manifest or {}).get("runtime_status"),
        "input_source_record_hash": source_record.get("source_record_hash") or source_record.get("provenance_hash"),
        "input_source_manifest_hash": (source_manifest or {}).get("manifest_hash") or compact_hash({"manifest_id": (source_manifest or {}).get("manifest_id")}),
        "input_certification_level": source_record.get("input_certification_level"),
        "implementation_grade_input_source": source_record.get("implementation_grade_input_source"),
        "source_contract_id": source_record.get("source_contract_id"),
        "source_locator": source_record.get("source_locator"),
        "source_coverage_period": source_record.get("coverage_period"),
        "source_extraction_date": source_record.get("extraction_date"),
        "source_freshness_status": source_record.get("source_freshness_status"),
        "source_freshness_policy_days": source_record.get("freshness_policy_days"),
        "units_verified": source_record.get("units_verified"),
        "provenance_hash": source_record.get("provenance_hash"),
        "strict_schema_test_fixture": source_record.get("strict_schema_test_fixture"),
        "evidence_origin": source_record.get("evidence_origin"),
        "external_source_attestation_status": source_record.get("external_source_attestation_status"),
        "promotion_eligible": source_record.get("promotion_eligible"),
    }


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def output_estimate(input_values: Mapping[str, Any], output_name: str, adapter_type: str) -> tuple[float, str]:
    name = output_name.lower()
    population = _number(input_values.get("population"), 1000.0)
    affected = max(0.0, min(1.0, _number(input_values.get("affected_share"), 0.1)))
    base = _number(input_values.get("monetary_base_index"), 100.0)
    rate = max(0.0, _number(input_values.get("baseline_rate"), 0.05))
    width = max(0.05, _number(input_values.get("uncertainty_scale"), 0.2))
    if "population" in name or "eligible" in name:
        return population * affected, "persons_or_cases"
    if "take_up" in name or "take-up" in name:
        return _number(input_values.get("expected_take_up_rate"), affected), "ratio"
    if "capacity" in name:
        return _number(input_values.get("fallback_capacity_units"), population * affected), "capacity_units"
    if "coverage" in name or "accessibility" in name or "language" in name:
        return min(1.0, max(0.0, (_number(input_values.get("language_access_coverage"), 0.7) + _number(input_values.get("digital_access_coverage"), 0.7)) / 2)), "ratio"
    if "false_positive" in name or "error" in name or "failure" in name:
        return min(1.0, max(0.0, _number(input_values.get("error_rate"), _number(input_values.get("false_positive_base_rate"), 0.02)))), "ratio"
    if "false_negative" in name:
        return min(1.0, max(0.0, _number(input_values.get("error_rate"), 0.02) * 0.8)), "ratio"
    if "time" in name or "delay" in name or "window" in name:
        return _number(input_values.get("appeal_window_days"), 45.0), "days"
    if "friction" in name or "burden" in name or "contest" in name:
        return _number(input_values.get("admin_cost_index"), 10.0) * (1 + _number(input_values.get("error_rate"), 0.02)), "index"
    if "harm" in name or "severity" in name or "rights" in name:
        return max(_number(input_values.get("harm_severity_index"), 0.5), _number(input_values.get("rights_burden_index"), 0.5)), "index"
    if "revenue" in name or "cost" in name or "yield" in name or "amount" in name:
        return base * rate * population * affected / 1000.0, "index_not_currency"
    if "elastic" in name or "behavior" in name:
        return _number(input_values.get("elasticity_abs"), _number(input_values.get("behavior_response_index"), 0.25)), "ratio_or_elasticity"
    if adapter_type == "no_go_threshold_adapter":
        return max(_number(input_values.get("harm_severity_index"), 0.5), _number(input_values.get("irreversibility_index"), 0.5), _number(input_values.get("rights_burden_index"), 0.5)), "index"
    return base * affected * (1 + rate), "index"


def model_outputs(packet: Mapping[str, Any], execution_mode: str, input_record: Mapping[str, Any] | None) -> Dict[str, Any]:
    outputs: Dict[str, Any] = {}
    adapter_type = str(packet.get("adapter_type") or "")
    if execution_mode == MODE_INTERFACE_FIXTURE:
        for name in packet.get("required_outputs", []):
            outputs[str(name)] = f"registered-interface-fixture:{name}"
        return outputs
    values = input_record.get("input_values", {}) if isinstance(input_record, Mapping) else {}
    width = max(0.05, _number(values.get("uncertainty_scale"), 0.2))
    for name in packet.get("required_outputs", []):
        estimate, unit = output_estimate(values, str(name), adapter_type)
        spread = max(0.01, abs(estimate) * width)
        outputs[str(name)] = {
            "estimate": round(estimate, 4),
            "low": round(estimate - spread, 4),
            "high": round(estimate + spread, 4),
            "unit": unit,
            "method": "local_reference_model_from_explicit_input_bundle",
            "input_record_hash": input_record.get("input_record_hash"),
        }
    return outputs


def input_proof_fields(input_record: Mapping[str, Any] | None, model_input_bundle: Mapping[str, Any] | None, source_record: Mapping[str, Any] | None = None, source_manifest: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    if not input_record:
        return {}
    values = input_record.get("input_values", {}) if isinstance(input_record, Mapping) else {}
    record_hash = input_record.get("input_record_hash")
    proof = {
        "model_input_bundle_id": input_record.get("bundle_id") or (model_input_bundle or {}).get("bundle_id"),
        "model_input_record_hash": record_hash,
        "inputs_hash": record_hash,
        "input_hash_basis": "explicit_model_input_bundle",
        "input_locator": input_record.get("input_locator"),
        "assumption_set_id": input_record.get("assumption_set_id"),
        "input_values_hash": compact_hash(values),
        "input_bundle_runtime_status": (model_input_bundle or {}).get("runtime_status"),
        "input_certification_level": input_record.get("input_certification_level"),
    }
    proof.update(input_source_proof_fields(source_record, source_manifest))
    return proof


def evidence_for_packet(
    packet: Mapping[str, Any],
    contracts_by_type: Mapping[str, Mapping[str, Any]],
    as_of_date: str,
    execution_mode: str,
    model_input_bundle: Mapping[str, Any] | None = None,
    model_input_source_manifest: Mapping[str, Any] | None = None,
) -> Dict[str, Any] | None:
    typ = str(packet.get("adapter_type") or "")
    rid = str(packet.get("route_id") or "")
    common = producer_fields(packet, contracts_by_type, as_of_date, execution_mode)
    if execution_mode == MODE_LOCAL_MODEL_ONLY and typ in EXTERNAL_ADAPTER_TYPES:
        return None
    if typ == "current_law_refresh_adapter":
        return {
            **common,
            "source_id": packet.get("source_id"),
            "checked_at": as_of_date,
            "retrieval_method": "registered_interface_fixture_no_live_law_claim",
            "authority_locator": f"fixture://producer/current-law/{packet.get('source_id')}",
            "jurisdiction": packet.get("jurisdiction") or "external_authority_fixture_jurisdiction",
            "effective_date": packet.get("effective_date") or as_of_date,
            "result_status": "confirmed_current",
            "reviewer_or_system": "tools/run_evidence_producers.py",
            "claim_supported": True,
            "non_doctrine_warning": "fixture evidence only; do not store as live-law doctrine",
        }
    if typ == "jurisdiction_scope_adapter":
        return {
            **common,
            "jurisdiction": packet.get("jurisdiction") or "external_authority_fixture_jurisdiction",
            "effective_date": packet.get("effective_date") or as_of_date,
            "authority_level": "fixture_authority_level",
            "preemption_or_treaty_conflict": "none_identified_in_registered_interface_fixture",
            "implementation_status": "in_force_for_registered_interface_fixture",
            "conflict_resolution": "fixture_conflict_rule_recorded",
            "non_doctrine_warning": "fixture evidence only; do not store as jurisdiction doctrine",
        }
    if typ in MODEL_ADAPTER_TYPES:
        input_record = input_for_packet(packet, model_input_bundle)
        if execution_mode == MODE_LOCAL_MODEL_ONLY and not input_record:
            return None
        outputs = model_outputs(packet, execution_mode, input_record)
        source_record = input_source_for_record(packet, input_record, model_input_source_manifest)
        proof = input_proof_fields(input_record, model_input_bundle, source_record, model_input_source_manifest)
        if execution_mode == MODE_INTERFACE_FIXTURE:
            fixture_hash = compact_hash({"adapter_id": packet.get("adapter_id"), "mode": MODE_INTERFACE_FIXTURE})
            proof = {
                "model_input_bundle_id": "interface-fixture-model-input-bundle",
                "model_input_record_hash": fixture_hash,
                "inputs_hash": fixture_hash,
                "input_hash_basis": "explicit_model_input_bundle",
                "input_locator": f"fixture://producer/model-input/{packet.get('adapter_id')}",
                "assumption_set_id": f"fixture-assumption-set:{fixture_hash[:16]}",
                "input_values_hash": fixture_hash,
                "input_bundle_runtime_status": "registered_interface_fixture",
                "model_input_source_manifest_id": "interface-fixture-input-source-manifest",
                "model_input_source_runtime_status": "registered_interface_fixture",
                "input_source_record_hash": fixture_hash,
                "input_source_manifest_hash": fixture_hash,
                "input_certification_level": "reference_fixture",
                "implementation_grade_input_source": False,
                "strict_schema_test_fixture": False,
                "evidence_origin": "archive_generated_reference_fixture",
                "external_source_attestation_status": "not_external",
                "promotion_eligible": False,
                "source_contract_id": "registered_interface_fixture_source",
                "source_locator": f"fixture://producer/model-input-source/{packet.get('adapter_id')}",
                "source_coverage_period": {"start": as_of_date, "end": as_of_date},
                "source_extraction_date": as_of_date,
                "source_freshness_status": "fresh",
                "source_freshness_policy_days": 1,
                "units_verified": True,
                "provenance_hash": fixture_hash,
            }
        assumptions = list((input_record or {}).get("assumptions", [])) or [
            "registered interface fixture; not a real model run",
            "requires replacement with explicit jurisdictional input bundle before implementation",
        ]
        model_name = packet.get("model_class") or {
            "quantitative_model_adapter": "fiscal_incidence_distribution_model",
            "floor_delivery_adapter": "protected_floor_delivery_model",
            "no_go_threshold_adapter": "no_go_threshold_review",
        }.get(typ, "model")
        base = {
            **common,
            **proof,
            "model_name": model_name,
            "model_version": "local-reference-v2-explicit-inputs" if execution_mode == MODE_LOCAL_MODEL_ONLY else "registered-interface-fixture-v2",
            "assumptions": assumptions,
            "run_at": as_of_date,
            "uncertainty_method": "explicit_input_reference_interval" if execution_mode == MODE_LOCAL_MODEL_ONLY else "registered_interface_fixture",
            "outputs": outputs,
            "run_locator": f"evidence-bundle://local-model-explicit-inputs/{rid}/{packet.get('model_class')}",
        }
        if typ == "quantitative_model_adapter":
            base["result_status"] = "model_run_complete"
        elif typ == "floor_delivery_adapter":
            base["result_status"] = "delivery_reference_run_complete"
        else:
            base.update({
                "threshold_result": "not_triggered" if execution_mode == MODE_INTERFACE_FIXTURE else "uncertain",
                "reviewer_or_system": "tools/run_evidence_producers.py",
            })
        return base
    return None


def merge_external_bundle(target: Dict[str, Any], external: Mapping[str, Any]) -> None:
    for pool_name in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        incoming = external.get(pool_name, {}) if isinstance(external, Mapping) else {}
        if isinstance(incoming, Mapping):
            target.setdefault(pool_name, {}).update(dict(incoming))
    incoming_context = external.get("execution_context", {}) if isinstance(external, Mapping) else {}
    if isinstance(incoming_context, Mapping):
        target.setdefault("execution_context", {}).update(dict(incoming_context))
    for key in ["evidence_producer_contracts", "producer_contracts"]:
        if external.get(key) and not target.get(key):
            target[key] = external[key]


def bundle_for_answers(
    root: pathlib.Path,
    answers: Sequence[Mapping[str, Any]],
    execution_mode: str,
    as_of_date: str,
    external_bundle: Mapping[str, Any] | None = None,
    model_input_bundle: Mapping[str, Any] | None = None,
    model_input_source_manifest: Mapping[str, Any] | None = None,
    strict_model_input_sources: bool = False,
    strict_authority_evidence: bool = False,
) -> Dict[str, Any]:
    contracts = load_json(root / "docs/00-meta/evidence-producer-contracts.json")
    by_type = contract_by_adapter_type(contracts)
    evidence: Dict[str, Any] = {}
    skipped: List[Dict[str, Any]] = []
    produced_by_type: Dict[str, int] = {}
    skipped_by_type: Dict[str, int] = {}
    skipped_by_reason: Dict[str, int] = {}
    for answer in answers:
        for packet in answer.get("disposition", {}).get("adapter_checks", []):
            packet = dict(packet)
            packet.setdefault("case_id", answer.get("case_id"))
            typ = str(packet.get("adapter_type") or "")
            produced = evidence_for_packet(packet, by_type, as_of_date, execution_mode, model_input_bundle, model_input_source_manifest)
            if produced is None:
                reason = "external_current_law_or_jurisdiction_evidence_required" if typ in EXTERNAL_ADAPTER_TYPES else "explicit_model_input_bundle_required"
                skipped.append({
                    "case_id": answer.get("case_id"),
                    "adapter_id": packet.get("adapter_id"),
                    "adapter_type": typ,
                    "skip_reason": reason,
                })
                skipped_by_type[typ] = skipped_by_type.get(typ, 0) + 1
                skipped_by_reason[reason] = skipped_by_reason.get(reason, 0) + 1
                continue
            aid = str(packet.get("adapter_id") or "")
            case_id = str(packet.get("case_id") or "")
            key = f"{case_id}:{aid}" if case_id and aid else aid
            evidence[key] = produced
            produced_by_type[typ] = produced_by_type.get(typ, 0) + 1
    bundle: Dict[str, Any] = {
        "kind": "adapter_evidence_bundle",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "execution_context": {
            "execution_mode": execution_mode,
            "as_of_date": as_of_date,
            "model_input_bundle_id": (model_input_bundle or {}).get("bundle_id"),
            "model_input_runtime_status": (model_input_bundle or {}).get("runtime_status"),
            "model_input_source_manifest_id": (model_input_source_manifest or {}).get("manifest_id"),
            "model_input_source_runtime_status": (model_input_source_manifest or {}).get("runtime_status"),
            "strict_model_input_source_certification_required": strict_model_input_sources,
            "strict_authority_evidence_required": strict_authority_evidence,
            "allow_internal_strict_schema_test_fixture": (
                (model_input_source_manifest or {}).get("certification_level") == "strict_schema_test_fixture"
            ),
            "non_doctrine_policy": "evidence is supplied to tools/execute_decision_adapters.py and must not be copied into route memos, source-currentness claims, or cube doctrine as a live legal/model conclusion",
        },
        "producer_contracts": contracts.get("producer_contracts", []),
        "adapter_evidence": evidence,
        "skipped_adapters": skipped,
        "summary": {
            "answer_count": len(answers),
            "evidence_count": sum(produced_by_type.values()),
            "evidence_unique_key_count": len(evidence),
            "skipped_count": len(skipped),
            "produced_adapter_type_counts": dict(sorted(produced_by_type.items())),
            "skipped_adapter_type_counts": dict(sorted(skipped_by_type.items())),
            "skipped_reason_counts": dict(sorted(skipped_by_reason.items())),
            "model_input_bundle_supplied": bool(model_input_bundle),
            "model_input_count": len((model_input_bundle or {}).get("model_inputs", {})) if isinstance(model_input_bundle, Mapping) else 0,
            "model_input_source_manifest_supplied": bool(model_input_source_manifest),
            "strict_model_input_sources": strict_model_input_sources,
            "strict_authority_evidence": strict_authority_evidence,
        },
    }
    if external_bundle:
        merge_external_bundle(bundle, external_bundle)
        bundle["summary"]["merged_external_bundle"] = True
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Run registered evidence producers for adapter evidence bundles.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Produce evidence for one case id")
    parser.add_argument("--all", action="store_true", help="Produce evidence for all golden cases")
    parser.add_argument("--execution-mode", choices=[MODE_INTERFACE_FIXTURE, MODE_LOCAL_MODEL_ONLY], default=MODE_LOCAL_MODEL_ONLY)
    parser.add_argument("--as-of-date", help="Evidence creation/run date in YYYY-MM-DD format")
    parser.add_argument("--external-evidence", help="Optional external current-law/jurisdiction/model evidence bundle to merge")
    parser.add_argument("--model-inputs", help="Explicit model-input bundle for local model evidence")
    parser.add_argument("--model-input-source-manifest", help="Optional source/provenance manifest for explicit model inputs")
    parser.add_argument("--strict-model-input-sources", action="store_true", help="Require implementation-grade model input source manifests during downstream execution")
    parser.add_argument("--strict-authority-evidence", action="store_true", help="Require implementation-grade authority evidence for current-law and jurisdiction adapters during downstream execution")
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    receipt = load_json(root / "REVISION-RECEIPT.json")
    as_of_date = args.as_of_date or str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    external_bundle = load_json(pathlib.Path(args.external_evidence).resolve()) if args.external_evidence else None
    model_input_bundle = load_json(pathlib.Path(args.model_inputs).resolve()) if args.model_inputs else None
    model_input_source_manifest = load_json(pathlib.Path(args.model_input_source_manifest).resolve()) if args.model_input_source_manifest else None
    bundle = bundle_for_answers(root, answers, args.execution_mode, as_of_date, external_bundle, model_input_bundle, model_input_source_manifest, args.strict_model_input_sources, args.strict_authority_evidence)
    if args.json:
        print(json.dumps(bundle, separators=(",", ":")))
    else:
        s = bundle.get("summary", {})
        print(f"{bundle.get('runtime_status')}: {s.get('evidence_count')} produced, {s.get('skipped_count')} skipped")
        for typ, count in s.get("produced_adapter_type_counts", {}).items():
            print(f"  produced {typ}: {count}")
        for typ, count in s.get("skipped_adapter_type_counts", {}).items():
            print(f"  skipped {typ}: {count}")


if __name__ == "__main__":
    main()
