#!/usr/bin/env python3
"""Build authority/current-law and jurisdiction evidence bundles for adapter execution.

Rev0333 moves implementation-grade authority intake behind an explicit
authority-source manifest before the raw intake bundle. Reference fixtures may still be generated for regression tests,
but implementation-grade current-law or jurisdiction evidence is emitted only
when a matching authority-intake record supplies raw locator, claim hash,
reviewer attestation, conflict-search hash, certification level, freshness, and
non-doctrine proof fields.
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

RUNTIME_STATUS = "authority_evidence_bundle_generated"
RULE_VERSION = 4
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
INTAKE_STATUS = "authority_intake_bundle_generated"
CERT_REFERENCE_FIXTURE = "reference_fixture"
CERT_STRICT_SCHEMA_TEST_FIXTURE = "strict_schema_test_fixture"
CERT_IMPLEMENTATION_GRADE = "implementation_grade"
CERTIFICATION_LEVELS = {CERT_REFERENCE_FIXTURE, CERT_STRICT_SCHEMA_TEST_FIXTURE, CERT_IMPLEMENTATION_GRADE}
AUTHORITY_ADAPTER_TYPES = {"current_law_refresh_adapter", "jurisdiction_scope_adapter"}
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8

AUTHORITY_INTAKE_PROOF_FIELDS = [
    "authority_intake_bundle_id",
    "authority_intake_record_hash",
    "authority_intake_bundle_hash",
    "authority_raw_locator",
    "authority_raw_record_hash",
    "authority_claim_locator",
    "authority_claim_support_map_hash",
    "authority_reviewer_attestation_hash",
    "authority_conflict_search_hash",
    "authority_intake_certification_level",
    "implementation_grade_authority_intake",
    "authority_source_type",
    "authority_primary_authority",
    "authority_retrieved_at",
    "authority_intake_freshness_status",
    "authority_record_claim_supported",
    "authority_source_manifest_id",
    "authority_source_record_hash",
    "authority_source_manifest_hash",
    "authority_source_certification_level",
    "implementation_grade_authority_source",
    "authority_source_contract_id",
    "authority_retrieval_source_locator",
    "authority_retrieval_claim_locator",
    "authority_retrieval_source_type",
    "authority_source_retrieval_date",
    "authority_source_freshness_status",
    "authority_source_primary_authority",
    "authority_source_claim_support_hash",
    "authority_source_conflict_review_hash",
    "authority_source_provenance_hash",
    "strict_schema_test_fixture",
    "evidence_origin",
    "external_source_attestation_status",
    "promotion_eligible",
]


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


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


def contract_by_adapter_type(contracts: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for contract in contracts.get("producer_contracts", []):
        if not isinstance(contract, Mapping):
            continue
        for typ in contract.get("adapter_types", []):
            out[str(typ)] = dict(contract)
    return out


def authority_lookup_keys(packet: Mapping[str, Any], case_id: str) -> List[str]:
    aid = str(packet.get("adapter_id") or "")
    typ = str(packet.get("adapter_type") or "")
    rid = str(packet.get("route_id") or "")
    sid = str(packet.get("source_id") or "")
    scope = str(packet.get("scope") or "")
    keys = [f"{case_id}:{aid}" if case_id and aid else aid, aid]
    if typ == "current_law_refresh_adapter" and sid:
        keys.extend([f"current_law:{sid}", sid])
    if typ == "jurisdiction_scope_adapter":
        keys.extend([f"jurisdiction_scope:{rid}", f"jurisdiction_scope:{rid}:{scope}", rid])
    return dedupe(keys)


def _producer_mode(adapter_type: str, certification_level: str) -> str:
    if certification_level in {CERT_REFERENCE_FIXTURE, CERT_STRICT_SCHEMA_TEST_FIXTURE}:
        return "registered_interface_fixture"
    if adapter_type == "current_law_refresh_adapter":
        return "human_verified_authority_retrieval"
    return "human_jurisdiction_review"


def _reference_intake_record(packet: Mapping[str, Any], case_id: str, as_of_date: str, seed: str) -> Dict[str, Any]:
    aid = str(packet.get("adapter_id") or "")
    typ = str(packet.get("adapter_type") or "")
    rid = str(packet.get("route_id") or "")
    source_id = packet.get("source_id")
    scope = packet.get("scope") or "general"
    raw_locator = (
        f"authority-intake-reference://current-law/{source_id}/{aid}"
        if typ == "current_law_refresh_adapter"
        else f"authority-intake-reference://jurisdiction/{rid}/{scope}/{aid}"
    )
    raw_hash = compact_hash({"case_id": case_id, "adapter_id": aid, "raw_locator": raw_locator, "certification": CERT_REFERENCE_FIXTURE})
    source_hash_basis = {
        "case_id": case_id,
        "adapter_id": aid,
        "adapter_type": typ,
        "route_id": rid,
        "source_id": source_id,
        "scope": scope,
        "raw_locator": raw_locator,
        "claim_locator": f"{raw_locator}#claim",
        "certification_level": CERT_REFERENCE_FIXTURE,
    }
    source_hash = compact_hash(source_hash_basis)
    common = {
        "authority_intake_bundle_id": f"authority-intake-bundle:{CERT_REFERENCE_FIXTURE}:{seed}",
        "authority_intake_record_hash": compact_hash({"raw_hash": raw_hash, "adapter_id": aid}),
        "authority_intake_bundle_hash": seed,
        "authority_raw_locator": raw_locator,
        "authority_raw_record_hash": raw_hash,
        "authority_claim_locator": f"{raw_locator}#claim",
        "authority_claim_support_map_hash": compact_hash({"adapter_id": aid, "claim_supported": True}),
        "authority_reviewer_attestation_hash": compact_hash({"reviewer": "reference_fixture", "adapter_id": aid}),
        "authority_conflict_search_hash": compact_hash({"scope": scope, "route_id": rid, "fixture": True}),
        "authority_intake_certification_level": CERT_REFERENCE_FIXTURE,
        "implementation_grade_authority_intake": False,
        "authority_source_type": "reference_fixture",
        "authority_primary_authority": False,
        "authority_retrieved_at": as_of_date,
        "authority_intake_freshness_status": "fresh",
        "authority_record_claim_supported": True,
        "authority_record_non_doctrine_warning": "reference authority intake fixture; cannot satisfy strict implementation clearance",
        "authority_source_manifest_id": "authority-intake-source-manifest:reference_fixture:inline",
        "authority_source_record_hash": source_hash,
        "authority_source_manifest_hash": compact_hash({"inline_reference_source_hash": source_hash}),
        "authority_source_certification_level": CERT_REFERENCE_FIXTURE,
        "implementation_grade_authority_source": False,
        "authority_source_contract_id": "reference_authority_source_fixture",
        "authority_retrieval_source_locator": raw_locator,
        "authority_retrieval_claim_locator": f"{raw_locator}#claim",
        "authority_retrieval_source_type": "reference_authority_fixture",
        "authority_source_retrieval_date": as_of_date,
        "authority_source_freshness_status": "fresh",
        "authority_source_primary_authority": False,
        "authority_source_claim_support_hash": compact_hash({"claim_locator": f"{raw_locator}#claim", "claim_supported": True}),
        "authority_source_conflict_review_hash": compact_hash({"route_id": rid, "scope": scope, "fixture": True}),
        "authority_source_provenance_hash": compact_hash(source_hash_basis),
        "strict_schema_test_fixture": False,
        "evidence_origin": "archive_generated_reference_fixture",
        "external_source_attestation_status": "not_external",
        "promotion_eligible": False,
        "jurisdiction": packet.get("jurisdiction") or "reference_fixture_jurisdiction",
        "effective_date": packet.get("effective_date") or as_of_date,
        "checked_at": as_of_date,
        "result_status": "confirmed_current",
        "claim_supported": True,
        "retrieval_method": "registered_reference_authority_intake_fixture",
        "reviewer_or_system": "tools/build_authority_evidence_bundle.py",
        "authority_level": "reference_fixture_authority_level",
        "preemption_or_treaty_conflict": "none_identified_in_reference_fixture",
        "implementation_status": "in_force_for_reference_fixture",
        "conflict_resolution": "reference_fixture_conflict_rule_recorded",
    }
    return common


def authority_intake_records(bundle: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(bundle, Mapping):
        return {}
    raw = bundle.get("authority_records") or bundle.get("records") or {}
    return raw if isinstance(raw, Mapping) else {}


def intake_for_packet(packet: Mapping[str, Any], case_id: str, bundle: Mapping[str, Any] | None) -> Dict[str, Any] | None:
    records = authority_intake_records(bundle)
    for key in authority_lookup_keys(packet, case_id):
        found = records.get(str(key))
        if isinstance(found, Mapping):
            return dict(found)
    return None


def intake_proof_fields(intake: Mapping[str, Any] | None) -> Dict[str, Any]:
    if not intake:
        return {}
    return {field: intake.get(field) for field in AUTHORITY_INTAKE_PROOF_FIELDS if field in intake}


def authority_record_for_packet(
    packet: Mapping[str, Any],
    case_id: str,
    contracts_by_type: Mapping[str, Mapping[str, Any]],
    as_of_date: str,
    certification_level: str,
    bundle_seed: str,
    authority_intake_bundle: Mapping[str, Any] | None = None,
) -> Dict[str, Any] | None:
    typ = str(packet.get("adapter_type") or "")
    if typ not in AUTHORITY_ADAPTER_TYPES:
        raise ValueError(f"not an authority adapter: {typ}")
    if certification_level not in CERTIFICATION_LEVELS:
        raise ValueError(f"unknown certification level: {certification_level}")
    contract = contracts_by_type.get(typ, {})
    implementation_grade = certification_level == CERT_IMPLEMENTATION_GRADE
    strict_test = certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE
    intake = intake_for_packet(packet, case_id, authority_intake_bundle)
    if certification_level in {CERT_IMPLEMENTATION_GRADE, CERT_STRICT_SCHEMA_TEST_FIXTURE} and not intake:
        return None
    if not intake:
        intake = _reference_intake_record(packet, case_id, as_of_date, bundle_seed)
    producer_mode = _producer_mode(typ, certification_level)
    aid = str(packet.get("adapter_id") or "")
    rid = str(packet.get("route_id") or "")
    source_id = packet.get("source_id")
    authority_locator = str(intake.get("authority_raw_locator") or intake.get("authority_claim_locator") or "")
    payload_basis = {
        "case_id": case_id,
        "adapter_id": aid,
        "adapter_type": typ,
        "route_id": rid,
        "source_id": source_id,
        "scope": packet.get("scope"),
        "as_of_date": as_of_date,
        "certification_level": certification_level,
        "producer_mode": producer_mode,
        "authority_locator": authority_locator,
        "authority_intake_record_hash": intake.get("authority_intake_record_hash"),
    }
    record_hash = compact_hash(payload_basis)
    proof = intake_proof_fields(intake)
    common = {
        "producer_id": contract.get("producer_id"),
        "producer_contract_version": contract.get("contract_version"),
        "evidence_kind": typ,
        "created_at": as_of_date,
        "producer_mode": producer_mode,
        "authority_evidence_bundle_id": f"authority-evidence-bundle:{certification_level}:{bundle_seed}",
        "authority_evidence_record_hash": record_hash,
        "authority_evidence_bundle_hash": bundle_seed,
        "authority_certification_level": certification_level,
        "implementation_grade_authority_evidence": implementation_grade,
        "strict_schema_test_fixture": strict_test,
        "evidence_origin": intake.get("evidence_origin") or ("archive_generated_strict_schema_test_fixture" if strict_test else "archive_generated_reference_fixture"),
        "external_source_attestation_status": intake.get("external_source_attestation_status") or "not_external",
        "promotion_eligible": intake.get("promotion_eligible") is True if implementation_grade else False,
        "authority_source_contract_id": contract.get("producer_id"),
        "authority_source_locator": authority_locator,
        "authority_checked_at": intake.get("checked_at") or intake.get("authority_retrieved_at") or as_of_date,
        "authority_coverage_period": {"start": intake.get("effective_date") or as_of_date, "end": intake.get("effective_date") or as_of_date},
        "authority_freshness_status": intake.get("authority_intake_freshness_status") or "fresh",
        "authority_provenance_hash": compact_hash({"evidence": payload_basis, "intake_hash": intake.get("authority_intake_record_hash")}),
        "external_authority_claim_hash": intake.get("authority_claim_support_map_hash") or compact_hash({"claim": payload_basis, "record_hash": record_hash}),
        "non_doctrine_warning": "authority evidence bundles are execution evidence; do not copy current-law or jurisdiction conclusions into cube doctrine",
        **proof,
    }
    if typ == "current_law_refresh_adapter":
        return {
            **common,
            "source_id": source_id,
            "checked_at": intake.get("checked_at") or intake.get("authority_retrieved_at") or as_of_date,
            "retrieval_method": intake.get("retrieval_method") or ("strict_schema_test_authority_intake" if strict_test else "registered_reference_authority_intake_fixture"),
            "authority_locator": authority_locator,
            "jurisdiction": intake.get("jurisdiction") or packet.get("jurisdiction") or ("strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction"),
            "effective_date": intake.get("effective_date") or packet.get("effective_date") or as_of_date,
            "result_status": intake.get("result_status") or "confirmed_current",
            "reviewer_or_system": intake.get("reviewer_or_system") or "tools/build_authority_evidence_bundle.py",
            "claim_supported": intake.get("claim_supported", True),
        }
    return {
        **common,
        "jurisdiction": intake.get("jurisdiction") or packet.get("jurisdiction") or ("strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction"),
        "effective_date": intake.get("effective_date") or packet.get("effective_date") or as_of_date,
        "authority_level": intake.get("authority_level") or ("strict_schema_test_authority_level" if strict_test else "reference_fixture_authority_level"),
        "preemption_or_treaty_conflict": intake.get("preemption_or_treaty_conflict") or ("none_identified_in_strict_schema_test_fixture" if strict_test else "none_identified_in_reference_fixture"),
        "implementation_status": intake.get("implementation_status") or ("in_force_for_strict_schema_test" if strict_test else "in_force_for_reference_fixture"),
        "conflict_resolution": intake.get("conflict_resolution") or ("schema_test_resolved" if strict_test else "reference_fixture_conflict_rule_recorded"),
    }


def bundle_for_answers(
    root: pathlib.Path,
    answers: Sequence[Mapping[str, Any]],
    as_of_date: str,
    certification_level: str = CERT_REFERENCE_FIXTURE,
    strict_authority_evidence: bool = True,
    authority_intake_bundle: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    contracts = load_json(root / "docs/00-meta/evidence-producer-contracts.json")
    by_type = contract_by_adapter_type(contracts)
    adapter_packets: List[tuple[Mapping[str, Any], str]] = []
    for answer in answers:
        case_id = str(answer.get("case_id") or "")
        for packet in answer.get("disposition", {}).get("adapter_checks", []):
            if packet.get("adapter_type") in AUTHORITY_ADAPTER_TYPES:
                adapter_packets.append((dict(packet), case_id))
    seed = compact_hash({
        "as_of_date": as_of_date,
        "certification_level": certification_level,
        "adapters": [f"{case_id}:{packet.get('adapter_id')}" for packet, case_id in adapter_packets],
        "authority_intake_bundle_hash": (authority_intake_bundle or {}).get("bundle_id") or (authority_intake_bundle or {}).get("manifest_hash"),
        "rule_version": RULE_VERSION,
    })[:16]
    bundle_id = f"authority-evidence-bundle:{certification_level}:{seed}"
    evidence: Dict[str, Any] = {}
    type_counts: Dict[str, int] = {}
    emitted_records = 0
    missing_intake = 0
    for packet, case_id in adapter_packets:
        record = authority_record_for_packet(packet, case_id, by_type, as_of_date, certification_level, seed, authority_intake_bundle)
        if record is None:
            missing_intake += 1
            continue
        emitted_records += 1
        record["authority_evidence_bundle_id"] = bundle_id
        record["authority_evidence_bundle_hash"] = seed
        for key in authority_lookup_keys(packet, case_id):
            evidence[str(key)] = record
        typ = str(packet.get("adapter_type"))
        type_counts[typ] = type_counts.get(typ, 0) + 1
    return {
        "kind": "authority_evidence_bundle",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "bundle_id": bundle_id,
        "created_at": as_of_date,
        "certification_level": certification_level,
        "producer_contracts": contracts.get("producer_contracts", []),
        "execution_context": {
            "as_of_date": as_of_date,
            "strict_authority_evidence_required": strict_authority_evidence,
            "authority_evidence_bundle_id": bundle_id,
            "authority_evidence_runtime_status": RUNTIME_STATUS,
            "authority_certification_level": certification_level,
            "authority_intake_required_for_implementation_grade": True,
            "authority_intake_bundle_id": (authority_intake_bundle or {}).get("bundle_id"),
            "authority_intake_runtime_status": (authority_intake_bundle or {}).get("runtime_status"),
            "authority_source_manifest_id": ((authority_intake_bundle or {}).get("execution_context") or {}).get("authority_source_manifest_id"),
            "authority_source_runtime_status": ((authority_intake_bundle or {}).get("execution_context") or {}).get("authority_source_runtime_status"),
            "authority_source_required_for_implementation_grade": True,
            "allow_internal_strict_schema_test_fixture": certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE,
            "non_doctrine_policy": "authority evidence is an execution bundle only; do not store current-law or jurisdiction conclusions as route doctrine",
        },
        "adapter_evidence": evidence,
        "summary": {
            "answer_count": len(answers),
            "authority_adapter_count": len(adapter_packets),
            "authority_evidence_record_count": emitted_records,
            "authority_evidence_unique_key_count": len(evidence),
            "missing_authority_intake_count": missing_intake,
            "current_law_record_count": type_counts.get("current_law_refresh_adapter", 0),
            "jurisdiction_record_count": type_counts.get("jurisdiction_scope_adapter", 0),
            "implementation_grade_count": emitted_records if certification_level == CERT_IMPLEMENTATION_GRADE else 0,
            "strict_schema_test_fixture_count": emitted_records if certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE else 0,
            "reference_fixture_count": emitted_records if certification_level == CERT_REFERENCE_FIXTURE else 0,
            "promotion_eligible_count": sum(1 for r in evidence.values() if isinstance(r, Mapping) and r.get("promotion_eligible") is True),
            "fresh_authority_count": emitted_records,
            "strict_authority_evidence": strict_authority_evidence,
            "authority_intake_bundle_supplied": bool(authority_intake_bundle),
            "adapter_type_counts": dict(sorted(type_counts.items())),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build current-law and jurisdiction authority evidence bundles.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Build authority evidence for one case id")
    parser.add_argument("--all", action="store_true", help="Build authority evidence for all golden cases")
    parser.add_argument("--as-of-date", help="Evidence date in YYYY-MM-DD format")
    parser.add_argument("--certification-level", choices=sorted(CERTIFICATION_LEVELS), default=CERT_REFERENCE_FIXTURE)
    parser.add_argument("--authority-intake-bundle", help="JSON authority-intake bundle required for implementation-grade evidence")
    parser.add_argument("--no-strict-authority-evidence", action="store_true", help="Do not set strict authority execution context")
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    receipt = load_json(root / "REVISION-RECEIPT.json") if (root / "REVISION-RECEIPT.json").exists() else {}
    as_of_date = args.as_of_date or str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    intake = load_json(pathlib.Path(args.authority_intake_bundle).resolve()) if args.authority_intake_bundle else None
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    bundle = bundle_for_answers(root, answers, as_of_date, args.certification_level, not args.no_strict_authority_evidence, intake)
    if args.json:
        print(json.dumps(bundle, separators=(",", ":")))
    else:
        s = bundle.get("summary", {})
        print(f"{RUNTIME_STATUS}: {s.get('authority_evidence_record_count')} authority records ({args.certification_level}); missing intake {s.get('missing_authority_intake_count')}")


if __name__ == "__main__":
    main()
