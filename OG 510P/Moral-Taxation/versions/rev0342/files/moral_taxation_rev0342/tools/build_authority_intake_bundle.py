#!/usr/bin/env python3
"""Build raw authority-intake records for current-law and jurisdiction adapters.

This is the pre-evidence boundary for strict authority execution. The archive may
plan which current-law and jurisdiction facts are needed, but implementation
clearance must come from an explicit authority-intake bundle: raw locator,
record hash, claim locator, reviewer attestation, conflict-search hash,
certification level, retrieval date, and non-doctrine warning.

The builder can create reference records and can normalize strict-schema test
fixtures, but implementation-grade intake is accepted only from an externally
supplied source manifest that carries the actual claim result and attestation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
from typing import Any, Dict, Iterable, List, Mapping, Sequence

RUNTIME_STATUS = "authority_intake_bundle_generated"
RULE_VERSION = 3
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
CERT_REFERENCE_FIXTURE = "reference_fixture"
CERT_STRICT_SCHEMA_TEST_FIXTURE = "strict_schema_test_fixture"
CERT_IMPLEMENTATION_GRADE = "implementation_grade"
CERTIFICATION_LEVELS = {CERT_REFERENCE_FIXTURE, CERT_STRICT_SCHEMA_TEST_FIXTURE, CERT_IMPLEMENTATION_GRADE}
AUTHORITY_ADAPTER_TYPES = {"current_law_refresh_adapter", "jurisdiction_scope_adapter"}
AUTHORITY_SOURCE_STATUS = "authority_intake_source_manifest_generated"
AUTHORITY_SOURCE_PROOF_FIELDS = [
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
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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



def authority_source_records(manifest: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(manifest, Mapping):
        return {}
    raw = manifest.get("authority_source_records") or manifest.get("records") or {}
    return raw if isinstance(raw, Mapping) else {}


def source_for_packet(packet: Mapping[str, Any], case_id: str, manifest: Mapping[str, Any] | None) -> Dict[str, Any] | None:
    records = authority_source_records(manifest)
    for key in authority_lookup_keys(packet, case_id):
        found = records.get(str(key))
        if isinstance(found, Mapping):
            return dict(found)
    return None


def source_proof_fields(source: Mapping[str, Any] | None) -> Dict[str, Any]:
    if not source:
        return {}
    return {field: source.get(field) for field in AUTHORITY_SOURCE_PROOF_FIELDS if field in source}

def _locator_prefix(certification_level: str) -> str:
    if certification_level == CERT_REFERENCE_FIXTURE:
        return "authority-intake-reference"
    if certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE:
        return "authority-intake-strict-schema-test"
    return "authority-intake-import"


def implementation_source_claim_fields(packet: Mapping[str, Any]) -> List[str]:
    if packet.get("adapter_type") == "current_law_refresh_adapter":
        return ["jurisdiction", "effective_date", "checked_at", "result_status", "claim_supported", "retrieval_method", "reviewer_or_system"]
    return ["jurisdiction", "effective_date", "authority_level", "preemption_or_treaty_conflict", "implementation_status", "conflict_resolution"]


def implementation_source_claim_complete(packet: Mapping[str, Any], source: Mapping[str, Any] | None) -> bool:
    if not isinstance(source, Mapping):
        return False
    if not all(source.get(field) not in (None, "", [], {}) for field in implementation_source_claim_fields(packet)):
        return False
    if source.get("authority_source_certification_level") != CERT_IMPLEMENTATION_GRADE:
        return False
    if source.get("implementation_grade_authority_source") is not True:
        return False
    if source.get("evidence_origin") != "external_observed":
        return False
    if source.get("external_source_attestation_status") != "verified_external_attestation":
        return False
    if source.get("promotion_eligible") is not True:
        return False
    if source.get("authority_source_primary_authority") is not True:
        return False
    if source.get("authority_source_freshness_status") != "fresh":
        return False
    locator = str(source.get("authority_retrieval_source_locator") or "")
    source_type = str(source.get("authority_retrieval_source_type") or "")
    if not locator or "fixture" in locator or locator.startswith(("fixture://", "reference-authority-source://", "strict-schema-test-authority-source://")):
        return False
    if not source_type or "fixture" in source_type:
        return False
    return True


def authority_intake_record_for_packet(
    packet: Mapping[str, Any],
    case_id: str,
    as_of_date: str,
    certification_level: str,
    bundle_seed: str,
    authority_source: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    typ = str(packet.get("adapter_type") or "")
    if typ not in AUTHORITY_ADAPTER_TYPES:
        raise ValueError(f"not an authority adapter: {typ}")
    if certification_level not in CERTIFICATION_LEVELS:
        raise ValueError(f"unknown certification level: {certification_level}")
    implementation_grade = certification_level == CERT_IMPLEMENTATION_GRADE
    strict_test = certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE
    source_proof = source_proof_fields(authority_source)
    aid = str(packet.get("adapter_id") or "")
    rid = str(packet.get("route_id") or "")
    source_id = packet.get("source_id")
    scope = packet.get("scope") or "general"
    prefix = _locator_prefix(certification_level)
    fallback_raw_locator = (
        f"{prefix}://current-law/{source_id}/{aid}"
        if typ == "current_law_refresh_adapter"
        else f"{prefix}://jurisdiction/{rid}/{scope}/{aid}"
    )
    raw_locator = str((authority_source or {}).get("authority_retrieval_source_locator") or fallback_raw_locator)
    claim_locator = str((authority_source or {}).get("authority_retrieval_claim_locator") or f"{raw_locator}#claim")
    if not source_proof and certification_level == CERT_REFERENCE_FIXTURE:
        source_hash_basis = {
            "case_id": case_id,
            "adapter_id": aid,
            "adapter_type": typ,
            "route_id": rid,
            "source_id": source_id,
            "scope": scope,
            "raw_locator": raw_locator,
            "claim_locator": claim_locator,
            "certification_level": CERT_REFERENCE_FIXTURE,
        }
        source_hash = compact_hash(source_hash_basis)
        source_proof = {
            "authority_source_manifest_id": "authority-intake-source-manifest:reference_fixture:inline",
            "authority_source_record_hash": source_hash,
            "authority_source_manifest_hash": compact_hash({"inline_reference_source_hash": source_hash}),
            "authority_source_certification_level": CERT_REFERENCE_FIXTURE,
            "implementation_grade_authority_source": False,
            "authority_source_contract_id": "reference_authority_source_fixture",
            "authority_retrieval_source_locator": raw_locator,
            "authority_retrieval_claim_locator": claim_locator,
            "authority_retrieval_source_type": "reference_authority_fixture",
            "authority_source_retrieval_date": as_of_date,
            "authority_source_freshness_status": "fresh",
            "authority_source_primary_authority": False,
            "authority_source_claim_support_hash": compact_hash({"claim_locator": claim_locator, "claim_supported": True}),
            "authority_source_conflict_review_hash": compact_hash({"route_id": rid, "scope": scope, "fixture": True}),
            "authority_source_provenance_hash": compact_hash(source_hash_basis),
            "strict_schema_test_fixture": False,
            "evidence_origin": "archive_generated_reference_fixture",
            "external_source_attestation_status": "not_external",
            "promotion_eligible": False,
        }
    raw_basis = {
        "case_id": case_id,
        "adapter_id": aid,
        "adapter_type": typ,
        "route_id": rid,
        "source_id": source_id,
        "scope": scope,
        "retrieved_at": as_of_date,
        "certification_level": certification_level,
        "raw_locator": raw_locator,
        "authority_source_record_hash": (authority_source or {}).get("authority_source_record_hash"),
    }
    raw_record_hash = compact_hash(raw_basis)
    source_claim_supported = (authority_source or {}).get("claim_supported") if implementation_grade else True
    source_result_status = (authority_source or {}).get("result_status") if implementation_grade else ("confirmed_current" if typ == "current_law_refresh_adapter" else "scope_resolved")
    claim_support_map = {
        "claim_locator": claim_locator,
        "source_id": source_id,
        "route_id": rid,
        "adapter_type": typ,
        "claim_supported": source_claim_supported,
        "result_status": source_result_status,
        "claim_support_semantics": "external_supplied" if implementation_grade else ("strict_schema_test_only" if strict_test else "reference_fixture_only"),
    }
    conflict_search = {
        "route_id": rid,
        "scope": scope,
        "jurisdiction": (authority_source or {}).get("jurisdiction") if implementation_grade else ("strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction"),
        "preemption_or_treaty_conflict": (authority_source or {}).get("preemption_or_treaty_conflict") if implementation_grade else ("none_identified_in_strict_schema_test_fixture" if strict_test else "none_identified_in_reference_fixture"),
        "conflict_resolution": (authority_source or {}).get("conflict_resolution") if implementation_grade else ("schema_test_resolved" if strict_test else "reference_fixture_conflict_rule_recorded"),
    }
    reviewer_attestation = {
        "reviewer_or_system": (authority_source or {}).get("reviewer_or_system") if implementation_grade else "tools/build_authority_intake_bundle.py",
        "reviewed_at": as_of_date,
        "authority_source_type": (authority_source or {}).get("authority_retrieval_source_type") or ("strict_schema_authority_fixture" if strict_test else "reference_fixture"),
        "non_doctrine_policy_acknowledged": True,
        "record_hash": raw_record_hash,
    }
    record_hash = compact_hash({"raw": raw_basis, "claim_support": claim_support_map, "conflict_search": conflict_search, "reviewer_attestation": reviewer_attestation})
    common = {
        "authority_intake_bundle_id": f"authority-intake-bundle:{certification_level}:{bundle_seed}",
        "authority_intake_record_hash": record_hash,
        "authority_intake_bundle_hash": bundle_seed,
        "authority_raw_locator": raw_locator,
        "authority_raw_record_hash": raw_record_hash,
        "authority_claim_locator": claim_locator,
        "authority_claim_support_map_hash": compact_hash(claim_support_map),
        "authority_reviewer_attestation_hash": compact_hash(reviewer_attestation),
        "authority_conflict_search_hash": compact_hash(conflict_search),
        "authority_intake_certification_level": certification_level,
        "implementation_grade_authority_intake": implementation_grade,
        "strict_schema_test_fixture": strict_test,
        "evidence_origin": (authority_source or {}).get("evidence_origin") or ("archive_generated_strict_schema_test_fixture" if strict_test else "archive_generated_reference_fixture"),
        "external_source_attestation_status": (authority_source or {}).get("external_source_attestation_status") or "not_external",
        "promotion_eligible": (authority_source or {}).get("promotion_eligible") is True if implementation_grade else False,
        "authority_source_type": (authority_source or {}).get("authority_retrieval_source_type") or ("strict_schema_authority_fixture" if strict_test else "reference_fixture"),
        "authority_primary_authority": (authority_source or {}).get("authority_source_primary_authority") is True if implementation_grade else False,
        "authority_retrieved_at": as_of_date,
        "authority_intake_freshness_status": "fresh",
        "authority_record_claim_supported": source_claim_supported is True,
        "authority_record_non_doctrine_warning": "raw authority intake is execution evidence only; do not copy current-law or jurisdiction conclusions into route doctrine",
        **source_proof,
        "case_id": case_id,
        "adapter_id": aid,
        "adapter_type": typ,
        "route_id": rid,
        "scope": scope,
        "source_id": source_id,
        "accepted_lookup_keys": authority_lookup_keys(packet, case_id),
    }
    if typ == "current_law_refresh_adapter":
        common.update({
            "jurisdiction": (authority_source or {}).get("jurisdiction") if implementation_grade else ("strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction"),
            "effective_date": (authority_source or {}).get("effective_date") if implementation_grade else as_of_date,
            "checked_at": (authority_source or {}).get("checked_at") if implementation_grade else as_of_date,
            "result_status": (authority_source or {}).get("result_status") if implementation_grade else "confirmed_current",
            "claim_supported": (authority_source or {}).get("claim_supported") if implementation_grade else True,
            "retrieval_method": (authority_source or {}).get("retrieval_method") if implementation_grade else ("strict_schema_test_authority_intake" if strict_test else "registered_reference_authority_intake_fixture"),
            "reviewer_or_system": reviewer_attestation["reviewer_or_system"],
        })
    else:
        common.update({
            "jurisdiction": (authority_source or {}).get("jurisdiction") if implementation_grade else ("strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction"),
            "effective_date": (authority_source or {}).get("effective_date") if implementation_grade else as_of_date,
            "authority_level": (authority_source or {}).get("authority_level") if implementation_grade else ("strict_schema_test_authority_level" if strict_test else "reference_fixture_authority_level"),
            "preemption_or_treaty_conflict": conflict_search["preemption_or_treaty_conflict"],
            "implementation_status": (authority_source or {}).get("implementation_status") if implementation_grade else ("in_force_for_strict_schema_test" if strict_test else "in_force_for_reference_fixture"),
            "conflict_resolution": conflict_search["conflict_resolution"],
        })
    return common


def bundle_for_answers(
    answers: Sequence[Mapping[str, Any]],
    as_of_date: str,
    certification_level: str = CERT_REFERENCE_FIXTURE,
    authority_source_manifest: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
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
        "runtime_status": RUNTIME_STATUS,
    })[:16]
    bundle_id = f"authority-intake-bundle:{certification_level}:{seed}"
    records: Dict[str, Any] = {}
    type_counts: Dict[str, int] = {}
    missing_source = 0
    invalid_implementation_source = 0
    source_required = certification_level in {CERT_IMPLEMENTATION_GRADE, CERT_STRICT_SCHEMA_TEST_FIXTURE}
    for packet, case_id in adapter_packets:
        source_record = source_for_packet(packet, case_id, authority_source_manifest)
        if source_required and not source_record:
            missing_source += 1
            continue
        if certification_level == CERT_IMPLEMENTATION_GRADE and not implementation_source_claim_complete(packet, source_record):
            invalid_implementation_source += 1
            continue
        record = authority_intake_record_for_packet(packet, case_id, as_of_date, certification_level, seed, source_record)
        record["authority_intake_bundle_id"] = bundle_id
        record["authority_intake_bundle_hash"] = seed
        for key in authority_lookup_keys(packet, case_id):
            records[str(key)] = record
        typ = str(packet.get("adapter_type"))
        type_counts[typ] = type_counts.get(typ, 0) + 1
    unique_record_hashes = {str(record.get("authority_intake_record_hash")) for record in records.values() if isinstance(record, Mapping)}
    return {
        "kind": "authority_intake_bundle",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "bundle_id": bundle_id,
        "created_at": as_of_date,
        "certification_level": certification_level,
        "execution_context": {
            "as_of_date": as_of_date,
            "authority_intake_bundle_id": bundle_id,
            "authority_intake_runtime_status": RUNTIME_STATUS,
            "authority_intake_certification_level": certification_level,
            "authority_source_manifest_id": (authority_source_manifest or {}).get("manifest_id"),
            "authority_source_runtime_status": (authority_source_manifest or {}).get("runtime_status"),
            "authority_source_required_for_implementation_grade": True,
            "allow_internal_strict_schema_test_fixture": certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE,
            "non_doctrine_policy": "authority intake records are execution evidence only; keep live-law and jurisdiction conclusions outside archive doctrine",
        },
        "authority_records": records,
        "summary": {
            "answer_count": len(answers),
            "authority_adapter_count": len(adapter_packets),
            "authority_intake_record_count": len(unique_record_hashes),
            "authority_intake_unique_key_count": len(records),
            "authority_intake_unique_record_count": len(unique_record_hashes),
            "missing_authority_source_count": missing_source,
            "invalid_implementation_authority_source_count": invalid_implementation_source,
            "authority_source_manifest_supplied": bool(authority_source_manifest),
            "current_law_record_count": type_counts.get("current_law_refresh_adapter", 0),
            "jurisdiction_record_count": type_counts.get("jurisdiction_scope_adapter", 0),
            "implementation_grade_count": len(unique_record_hashes) if certification_level == CERT_IMPLEMENTATION_GRADE else 0,
            "strict_schema_test_fixture_count": len(unique_record_hashes) if certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE else 0,
            "reference_fixture_count": len(unique_record_hashes) if certification_level == CERT_REFERENCE_FIXTURE else 0,
            "promotion_eligible_count": sum(1 for r in records.values() if isinstance(r, Mapping) and r.get("promotion_eligible") is True),
            "fresh_intake_count": len(unique_record_hashes),
            "adapter_type_counts": dict(sorted(type_counts.items())),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build raw current-law and jurisdiction authority-intake bundles.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Build authority intake for one case id")
    parser.add_argument("--all", action="store_true", help="Build authority intake for all golden cases")
    parser.add_argument("--as-of-date", help="Evidence date in YYYY-MM-DD format")
    parser.add_argument("--certification-level", choices=sorted(CERTIFICATION_LEVELS), default=CERT_REFERENCE_FIXTURE)
    parser.add_argument("--authority-source-manifest", help="JSON authority-intake source manifest required for implementation-grade intake")
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    receipt = load_json(root / "REVISION-RECEIPT.json") if (root / "REVISION-RECEIPT.json").exists() else {}
    as_of_date = args.as_of_date or str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    authority_source_manifest = load_json(pathlib.Path(args.authority_source_manifest).resolve()) if args.authority_source_manifest else None
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    bundle = bundle_for_answers(answers, as_of_date, args.certification_level, authority_source_manifest)
    if args.json:
        print(json.dumps(bundle, separators=(",", ":")))
    else:
        s = bundle.get("summary", {})
        print(f"{RUNTIME_STATUS}: {s.get('authority_intake_record_count')} authority intake records ({args.certification_level})")


if __name__ == "__main__":
    main()
