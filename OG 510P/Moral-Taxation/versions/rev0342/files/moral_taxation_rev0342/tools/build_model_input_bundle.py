#!/usr/bin/env python3
"""Build explicit model-input bundles for evidence producers.

The evidence producer runner must not fabricate fiscal, delivery, or no-go
outputs from adapter ids alone. This tool creates the separate input side of the
boundary: every model-style adapter gets a record with values, units,
assumptions, uncertainty parameters, and a stable input-record hash. Real
implementations should replace the reference-fixture records with jurisdictional
microdata, delivery-capacity data, or expert threshold review inputs.
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

RUNTIME_STATUS = "explicit_model_input_bundle_generated"
RULE_VERSION = 2
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
INPUT_MODE_REFERENCE_FIXTURE = "reference_input_fixture"
INPUT_CERTIFICATION_LEVEL_REFERENCE = "reference_fixture"
MODEL_ADAPTER_TYPES = {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    payload = json.loads(subprocess.check_output(args, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}))
    if payload.get("runtime_status") != ANSWER_STATUS:
        raise SystemExit("answer_case.py returned a stale runtime status")
    return payload.get("answers", [])


def model_adapter_packets(answers: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    packets: List[Dict[str, Any]] = []
    for answer in answers:
        for packet in answer.get("disposition", {}).get("adapter_checks", []):
            if packet.get("adapter_type") in MODEL_ADAPTER_TYPES:
                item = dict(packet)
                item["case_id"] = answer.get("case_id")
                item["case_title"] = answer.get("title")
                packets.append(item)
    return packets


def _seed(packet: Mapping[str, Any], name: str) -> int:
    raw = f"{packet.get('case_id')}|{packet.get('adapter_id')}|{packet.get('route_id')}|{packet.get('model_class')}|{name}"
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10], 16)


def _ratio(packet: Mapping[str, Any], name: str, low: float, high: float) -> float:
    seed = _seed(packet, name) % 10000
    return round(low + (high - low) * (seed / 9999), 4)


def _integer(packet: Mapping[str, Any], name: str, low: int, high: int) -> int:
    seed = _seed(packet, name)
    return low + (seed % max(1, high - low + 1))


def input_values_for_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    typ = packet.get("adapter_type")
    common = {
        "population": _integer(packet, "population", 2500, 2500000),
        "affected_share": _ratio(packet, "affected_share", 0.005, 0.72),
        "monetary_base_index": _ratio(packet, "monetary_base_index", 10.0, 1000.0),
        "baseline_rate": _ratio(packet, "baseline_rate", 0.001, 0.45),
        "elasticity_abs": _ratio(packet, "elasticity_abs", 0.02, 1.7),
        "admin_cost_index": _ratio(packet, "admin_cost_index", 0.5, 120.0),
        "error_rate": _ratio(packet, "error_rate", 0.0005, 0.18),
        "uncertainty_scale": _ratio(packet, "uncertainty_scale", 0.08, 0.45),
    }
    if typ == "floor_delivery_adapter":
        common.update({
            "eligible_population": _integer(packet, "eligible_population", 500, 900000),
            "expected_take_up_rate": _ratio(packet, "expected_take_up_rate", 0.25, 0.96),
            "fallback_capacity_units": _integer(packet, "fallback_capacity_units", 100, 650000),
            "expected_demand_units": _integer(packet, "expected_demand_units", 150, 700000),
            "language_access_coverage": _ratio(packet, "language_access_coverage", 0.35, 0.99),
            "digital_access_coverage": _ratio(packet, "digital_access_coverage", 0.35, 0.99),
            "appeal_window_days": _integer(packet, "appeal_window_days", 14, 180),
        })
    elif typ == "no_go_threshold_adapter":
        common.update({
            "harm_severity_index": _ratio(packet, "harm_severity_index", 0.25, 0.98),
            "irreversibility_index": _ratio(packet, "irreversibility_index", 0.2, 0.98),
            "rights_burden_index": _ratio(packet, "rights_burden_index", 0.2, 0.99),
            "evidence_confidence_index": _ratio(packet, "evidence_confidence_index", 0.15, 0.9),
            "threshold_clearance_margin": _ratio(packet, "threshold_clearance_margin", -0.3, 0.3),
        })
    else:
        common.update({
            "behavior_response_index": _ratio(packet, "behavior_response_index", 0.01, 0.85),
            "incidence_shift_share": _ratio(packet, "incidence_shift_share", 0.02, 0.92),
            "enforcement_capacity_index": _ratio(packet, "enforcement_capacity_index", 0.15, 0.95),
            "false_positive_base_rate": _ratio(packet, "false_positive_base_rate", 0.0005, 0.12),
            "distributional_weight_index": _ratio(packet, "distributional_weight_index", 0.2, 2.5),
        })
    return common


def units_for_values(values: Mapping[str, Any]) -> Dict[str, str]:
    units: Dict[str, str] = {}
    for key in values:
        if key.endswith("_rate") or key.endswith("_share") or key.endswith("_coverage") or key.endswith("_index") or key.endswith("_abs") or key.endswith("_scale") or key.endswith("_margin"):
            units[key] = "ratio_or_index"
        elif key.endswith("_days"):
            units[key] = "days"
        elif key.endswith("_population") or key.endswith("_units") or key == "population":
            units[key] = "persons_or_cases"
        else:
            units[key] = "index"
    return units


def input_record_for_packet(packet: Mapping[str, Any], bundle_id: str, as_of_date: str, input_mode: str) -> Dict[str, Any]:
    values = input_values_for_packet(packet)
    units = units_for_values(values)
    assumptions = [
        "reference input fixture; replace with jurisdictional data before implementation",
        "values are explicit inputs, not route doctrine and not legal advice",
        "outputs derived from this record must preserve uncertainty intervals",
    ]
    if packet.get("adapter_type") == "no_go_threshold_adapter":
        assumptions.append("local no-go inputs cannot clear a rights or noncompensable-harm threshold without external review")
    uncertainty = {
        "interval_method": "reference_input_uncertainty_band",
        "default_relative_width": values.get("uncertainty_scale"),
        "must_not_collapse_to_point_estimate": True,
    }
    hash_payload = {
        "bundle_id": bundle_id,
        "adapter_id": packet.get("adapter_id"),
        "adapter_type": packet.get("adapter_type"),
        "route_id": packet.get("route_id"),
        "model_class": packet.get("model_class"),
        "required_outputs": [str(x) for x in packet.get("required_outputs", [])],
        "input_values": values,
        "units": units,
        "assumptions": assumptions,
        "uncertainty_parameters": uncertainty,
        "input_mode": input_mode,
    }
    record_hash = compact_hash(hash_payload)
    return {
        "kind": "model_input_record",
        "bundle_id": bundle_id,
        "input_mode": input_mode,
        "case_id": packet.get("case_id"),
        "case_title": packet.get("case_title"),
        "adapter_id": packet.get("adapter_id"),
        "adapter_type": packet.get("adapter_type"),
        "route_id": packet.get("route_id"),
        "model_class": packet.get("model_class"),
        "required_outputs": [str(x) for x in packet.get("required_outputs", [])],
        "input_values": values,
        "units": units,
        "assumptions": assumptions,
        "uncertainty_parameters": uncertainty,
        "assumption_set_id": f"assumption-set:{record_hash[:16]}",
        "input_locator": f"model-input-bundle://{bundle_id}/{packet.get('adapter_id')}",
        "input_certification_level": INPUT_CERTIFICATION_LEVEL_REFERENCE,
        "source_manifest_required": True,
        "implementation_grade_source_required_for_finalization": True,
        "created_at": as_of_date,
        "input_record_hash": record_hash,
        "hash_basis": "explicit_model_input_bundle",
        "non_doctrine_warning": "model inputs are external execution evidence; do not copy values into route doctrine or source-currentness claims",
    }


def bundle_for_answers(answers: Sequence[Mapping[str, Any]], as_of_date: str, input_mode: str = INPUT_MODE_REFERENCE_FIXTURE) -> Dict[str, Any]:
    packets = model_adapter_packets(answers)
    bundle_seed = compact_hash({"as_of_date": as_of_date, "input_mode": input_mode, "adapter_ids": [p.get("adapter_id") for p in packets]})[:16]
    bundle_id = f"model-input-bundle:{input_mode}:{bundle_seed}"
    inputs: Dict[str, Any] = {}
    type_counts: Dict[str, int] = {}
    for packet in packets:
        record = input_record_for_packet(packet, bundle_id, as_of_date, input_mode)
        aid = str(packet.get("adapter_id") or "")
        case_id = str(packet.get("case_id") or "")
        key = f"{case_id}:{aid}" if case_id and aid else aid
        inputs[key] = record
        typ = str(packet.get("adapter_type") or "")
        type_counts[typ] = type_counts.get(typ, 0) + 1
    return {
        "kind": "explicit_model_input_bundle",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "bundle_id": bundle_id,
        "input_mode": input_mode,
        "created_at": as_of_date,
        "model_inputs": inputs,
        "summary": {
            "answer_count": len(answers),
            "model_input_count": len(inputs),
            "unique_model_input_count": len(inputs),
            "adapter_type_counts": dict(sorted(type_counts.items())),
            "explicit_input_hash_count": sum(1 for r in inputs.values() if r.get("input_record_hash")),
        },
        "non_doctrine_policy": "Input bundles are execution evidence. They may be validated by tools/run_evidence_producers.py only when paired with a source manifest; they must not become cube doctrine or stale model outputs.",
        "source_manifest_required": True,
        "implementation_grade_source_required_for_finalization": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build explicit model-input bundles for model evidence producers.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Build inputs for one case id")
    parser.add_argument("--all", action="store_true", help="Build inputs for all golden cases")
    parser.add_argument("--as-of-date", help="Input creation date in YYYY-MM-DD format")
    parser.add_argument("--input-mode", choices=[INPUT_MODE_REFERENCE_FIXTURE], default=INPUT_MODE_REFERENCE_FIXTURE)
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    receipt = load_json(root / "REVISION-RECEIPT.json")
    as_of_date = args.as_of_date or str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    bundle = bundle_for_answers(answers, as_of_date, args.input_mode)
    if args.json:
        print(json.dumps(bundle, separators=(",", ":")))
    else:
        summary = bundle["summary"]
        print(f"{RUNTIME_STATUS}: {summary['model_input_count']} explicit model input records")
        for typ, count in summary.get("adapter_type_counts", {}).items():
            print(f"  {typ}: {count}")


if __name__ == "__main__":
    main()
