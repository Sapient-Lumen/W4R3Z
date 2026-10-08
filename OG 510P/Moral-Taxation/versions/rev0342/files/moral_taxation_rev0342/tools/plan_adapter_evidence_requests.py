#!/usr/bin/env python3
"""Plan evidence requests for decision-adapter execution.

This tool does not fetch law and does not run models. It converts answer-packet
adapter checks into producer-specific request packets so external systems can
produce evidence bundles that `tools/execute_decision_adapters.py` can validate.
The request plan is the anti-stale-output boundary: the archive stores the
contract and the request shape, not the perishable answer.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Mapping, Sequence

RUNTIME_STATUS = "evidence_producer_requests_planned"
RULE_VERSION = 5


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


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


def contract_by_adapter_type(contracts: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for contract in contracts.get("producer_contracts", []):
        if not isinstance(contract, Mapping):
            continue
        for typ in contract.get("adapter_types", []):
            out.setdefault(str(typ), []).append(dict(contract))
    return out


def request_for_adapter(case_id: str, title: str, packet: Mapping[str, Any], contracts: Mapping[str, Any], executor: Any) -> Dict[str, Any]:
    typ = str(packet.get("adapter_type") or "")
    candidates = contract_by_adapter_type(contracts).get(typ, [])
    packet_for_lookup = dict(packet)
    packet_for_lookup.setdefault("case_id", case_id)
    return {
        "runtime_status": RUNTIME_STATUS,
        "request_id": f"adapter_evidence_request:{case_id}:{packet.get('adapter_id')}",
        "case_id": case_id,
        "case_title": title,
        "adapter_id": packet.get("adapter_id"),
        "adapter_type": typ,
        "route_id": packet.get("route_id"),
        "source_id": packet.get("source_id"),
        "model_class": packet.get("model_class"),
        "scope": packet.get("scope"),
        "accepted_lookup_keys": executor.evidence_lookup_keys(packet_for_lookup),
        "required_evidence_fields": executor.required_fields_for_adapter(packet),
        "required_outputs": [str(x) for x in packet.get("required_outputs", [])],
        "requires_explicit_model_input_bundle": typ in getattr(executor, "MODEL_ADAPTER_TYPES", set()),
        "requires_implementation_grade_input_source": typ in getattr(executor, "MODEL_ADAPTER_TYPES", set()),
        "requires_implementation_grade_authority_evidence": typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()),
        "requires_raw_authority_intake_bundle": typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()),
        "requires_authority_source_manifest": typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()),
        "required_input_source_fields": list(getattr(executor, "INPUT_SOURCE_PROOF_FIELDS", [])) if typ in getattr(executor, "MODEL_ADAPTER_TYPES", set()) else [],
        "required_authority_evidence_fields": list(getattr(executor, "AUTHORITY_PROOF_FIELDS", [])) if typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()) else [],
        "accepted_model_input_lookup_keys": (
            [
                f"{case_id}:{packet.get('adapter_id')}" if packet.get("adapter_id") else "",
                str(packet.get("adapter_id") or ""),
                f"model_input:{case_id}:{packet.get('adapter_id')}" if packet.get("adapter_id") else "",
                f"model_input:{packet.get('adapter_id')}" if packet.get("adapter_id") else "",
                f"model_input:{packet.get('route_id')}:{packet.get('model_class')}" if packet.get("route_id") and packet.get("model_class") else "",
            ] if typ in getattr(executor, "MODEL_ADAPTER_TYPES", set()) else []
        ),
        "producer_contract_ids": [c.get("producer_id") for c in candidates],
        "producer_contract_versions": {c.get("producer_id"): c.get("contract_version") for c in candidates},
        "accepted_model_input_source_lookup_keys": (
            [
                f"{case_id}:{packet.get('adapter_id')}" if packet.get("adapter_id") else "",
                str(packet.get("adapter_id") or ""),
                f"model_input_source:{case_id}:{packet.get('adapter_id')}" if packet.get("adapter_id") else "",
                f"model_input_source:{packet.get('route_id')}:{packet.get('model_class')}" if packet.get("route_id") and packet.get("model_class") else "",
            ] if typ in getattr(executor, "MODEL_ADAPTER_TYPES", set()) else []
        ),
        "accepted_authority_evidence_lookup_keys": (
            executor.evidence_lookup_keys(packet_for_lookup) if typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()) else []
        ),
        "accepted_authority_intake_lookup_keys": (
            executor.evidence_lookup_keys(packet_for_lookup) if typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()) else []
        ),
        "accepted_authority_source_lookup_keys": (
            executor.evidence_lookup_keys(packet_for_lookup) if typ in getattr(executor, "AUTHORITY_ADAPTER_TYPES", set()) else []
        ),
        "permitted_execution_modes": sorted({str(mode) for c in candidates for mode in c.get("permitted_execution_modes", [])}),
        "output_retention": sorted({str(c.get("output_retention")) for c in candidates}),
        "non_doctrine_policy": "return an external evidence bundle to tools/execute_decision_adapters.py; do not write current-law conclusions or model outputs into route memos, cube-index.json, or source-currentness claims",
    }


def requests_for_answers(answers: Sequence[Mapping[str, Any]], contracts: Mapping[str, Any], executor: Any) -> List[Dict[str, Any]]:
    requests: List[Dict[str, Any]] = []
    for answer in answers:
        case_id = str(answer.get("case_id") or "")
        title = str(answer.get("title") or "")
        for packet in answer.get("disposition", {}).get("adapter_checks", []):
            requests.append(request_for_adapter(case_id, title, packet, contracts, executor))
    return dedupe(requests)


def summarize_requests(requests: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    type_counts: Dict[str, int] = {}
    producer_counts: Dict[str, int] = {}
    cases = set()
    missing_producers = 0
    for req in requests:
        cases.add(str(req.get("case_id")))
        typ = str(req.get("adapter_type"))
        type_counts[typ] = type_counts.get(typ, 0) + 1
        producers = [p for p in req.get("producer_contract_ids", []) if p]
        if not producers:
            missing_producers += 1
        for pid in producers:
            producer_counts[str(pid)] = producer_counts.get(str(pid), 0) + 1
    return {
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "request_count": len(requests),
        "case_count": len(cases),
        "requests_missing_producer_contract": missing_producers,
        "adapter_type_counts": dict(sorted(type_counts.items())),
        "producer_contract_request_counts": dict(sorted(producer_counts.items())),
    }


def load_answers(root: pathlib.Path, case_id: str | None, all_cases: bool, route_limit: int, facts_only_limit: int) -> List[Dict[str, Any]]:
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
    payload = json.loads(subprocess.check_output(args, text=True, env={"PYTHONDONTWRITEBYTECODE": "1"}))
    return payload.get("answers", [])


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan external evidence-producer requests for adapter execution.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Plan one case id")
    parser.add_argument("--all", action="store_true", help="Plan all golden cases")
    parser.add_argument("--route-limit", type=int, default=5, help="Selected route count to include")
    parser.add_argument("--facts-only-candidate-limit", type=int, default=8, help="Facts-only candidate count to include")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    contracts = load_json(root / "docs/00-meta/evidence-producer-contracts.json")
    executor = load_module("execute_decision_adapters", root / "tools/execute_decision_adapters.py")
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    requests = requests_for_answers(answers, contracts, executor)
    payload = {
        "kind": "adapter_evidence_request_plan",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "summary": summarize_requests(requests),
        "requests": requests,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        summary = payload["summary"]
        print(f"planned {summary['request_count']} evidence requests across {summary['case_count']} cases")
        for typ, count in summary.get("adapter_type_counts", {}).items():
            print(f"  {typ}: {count}")


if __name__ == "__main__":
    main()
