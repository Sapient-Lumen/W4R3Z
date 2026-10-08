#!/usr/bin/env python3
"""Build fixture source manifests for authority-intake interfaces.

This builder may generate reference fixtures and strict-schema test fixtures. It
must never manufacture implementation-grade authority provenance. Production
manifests are externally supplied records with actual retrieval locators,
primary-authority review, conflict review, and independent attestation.
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

RUNTIME_STATUS = "authority_intake_source_manifest_generated"
RULE_VERSION = 2
ANSWER_STATUS = "profile_backed_answer_packet_emitted"
CERT_REFERENCE_FIXTURE = "reference_fixture"
CERT_STRICT_SCHEMA_TEST_FIXTURE = "strict_schema_test_fixture"
CERT_IMPLEMENTATION_GRADE = "implementation_grade"
GENERATABLE_CERTIFICATION_LEVELS = {CERT_REFERENCE_FIXTURE, CERT_STRICT_SCHEMA_TEST_FIXTURE}
CERTIFICATION_LEVELS = GENERATABLE_CERTIFICATION_LEVELS | {CERT_IMPLEMENTATION_GRADE}
AUTHORITY_ADAPTER_TYPES = {"current_law_refresh_adapter", "jurisdiction_scope_adapter"}
ROUTE_LIMIT = 5
FACTS_ONLY_LIMIT = 8
ORIGIN_REFERENCE = "archive_generated_reference_fixture"
ORIGIN_STRICT_TEST = "archive_generated_strict_schema_test_fixture"

SOURCE_CONTRACT_BY_ADAPTER_TYPE = {
    "current_law_refresh_adapter": "current_law_primary_authority_source",
    "jurisdiction_scope_adapter": "jurisdiction_scope_primary_authority_source",
}


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
        "--route-limit", str(route_limit),
        "--facts-only-candidate-limit", str(facts_only_limit),
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


def source_contract_id(packet: Mapping[str, Any]) -> str:
    return SOURCE_CONTRACT_BY_ADAPTER_TYPE.get(str(packet.get("adapter_type") or ""), "authority_source")


def source_record_for_packet(
    packet: Mapping[str, Any],
    case_id: str,
    manifest_id: str,
    manifest_hash_seed: str,
    as_of_date: str,
    certification_level: str,
) -> Dict[str, Any]:
    if certification_level not in GENERATABLE_CERTIFICATION_LEVELS:
        raise ValueError("archive builders cannot synthesize implementation-grade authority provenance")
    typ = str(packet.get("adapter_type") or "")
    if typ not in AUTHORITY_ADAPTER_TYPES:
        raise ValueError(f"not an authority adapter: {typ}")
    strict_test = certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE
    origin = ORIGIN_STRICT_TEST if strict_test else ORIGIN_REFERENCE
    aid = str(packet.get("adapter_id") or "")
    rid = str(packet.get("route_id") or "")
    source_id = packet.get("source_id")
    scope = packet.get("scope") or "general"
    contract_id = source_contract_id(packet)
    locator_prefix = "strict-schema-test-authority-source" if strict_test else "reference-authority-source"
    if typ == "current_law_refresh_adapter":
        locator = f"{locator_prefix}://current-law/{source_id}/{aid}"
        claim_locator = f"{locator}#current-law-claim"
    else:
        locator = f"{locator_prefix}://jurisdiction/{rid}/{scope}/{aid}"
        claim_locator = f"{locator}#jurisdiction-scope-claim"
    raw_retrieval_payload = {
        "manifest_id": manifest_id,
        "case_id": case_id,
        "adapter_id": aid,
        "adapter_type": typ,
        "route_id": rid,
        "source_id": source_id,
        "scope": scope,
        "source_contract_id": contract_id,
        "source_locator": locator,
        "claim_locator": claim_locator,
        "certification_level": certification_level,
        "evidence_origin": origin,
        "retrieval_date": as_of_date,
    }
    source_record_hash = compact_hash(raw_retrieval_payload)
    conflict_review_payload = {
        "route_id": rid,
        "scope": scope,
        "adapter_type": typ,
        "jurisdiction": "strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction",
        "conflict_review_status": "schema_test_completed" if strict_test else "reference_fixture_only",
        "source_record_hash": source_record_hash,
    }
    claim_support_payload = {
        "claim_locator": claim_locator,
        "adapter_type": typ,
        "route_id": rid,
        "source_id": source_id,
        "claim_supported": True,
        "claim_support_semantics": "schema_test_only" if strict_test else "reference_fixture_only",
        "source_record_hash": source_record_hash,
    }
    provenance_hash = compact_hash({
        "raw_retrieval": raw_retrieval_payload,
        "conflict_review": conflict_review_payload,
        "claim_support": claim_support_payload,
        "manifest_hash_seed": manifest_hash_seed,
    })
    return {
        "kind": "authority_intake_source_record",
        "authority_source_manifest_id": manifest_id,
        "authority_source_record_hash": source_record_hash,
        "authority_source_manifest_hash": manifest_hash_seed,
        "authority_source_certification_level": certification_level,
        "implementation_grade_authority_source": False,
        "strict_schema_test_fixture": strict_test,
        "evidence_origin": origin,
        "external_source_attestation_status": "not_external",
        "promotion_eligible": False,
        "certification_semantics": "schema_conformance_test_only" if strict_test else "reference_fixture_only",
        "authority_source_contract_id": contract_id,
        "authority_retrieval_source_locator": locator,
        "authority_retrieval_claim_locator": claim_locator,
        "authority_retrieval_source_type": "strict_schema_authority_fixture" if strict_test else "reference_authority_fixture",
        "authority_source_retrieval_date": as_of_date,
        "authority_source_freshness_status": "fresh",
        "authority_source_freshness_semantics": "fixture_date_only_not_external_freshness",
        "authority_source_primary_authority": False,
        "authority_source_claim_support_hash": compact_hash(claim_support_payload),
        "authority_source_conflict_review_hash": compact_hash(conflict_review_payload),
        "authority_source_provenance_hash": provenance_hash,
        "authority_source_non_doctrine_warning": "archive-generated authority source records are fixtures only and cannot certify current law or jurisdiction",
        "case_id": case_id,
        "adapter_id": aid,
        "adapter_type": typ,
        "route_id": rid,
        "scope": scope,
        "source_id": source_id,
        "accepted_lookup_keys": authority_lookup_keys(packet, case_id),
    }


def manifest_for_answers(
    answers: Sequence[Mapping[str, Any]],
    as_of_date: str,
    certification_level: str = CERT_REFERENCE_FIXTURE,
) -> Dict[str, Any]:
    if certification_level == CERT_IMPLEMENTATION_GRADE:
        raise ValueError(
            "implementation-grade authority source manifests must be imported from an external retrieval/review producer; "
            "the archive builder generates only reference or strict-schema fixtures"
        )
    if certification_level not in GENERATABLE_CERTIFICATION_LEVELS:
        raise ValueError(f"unknown certification level: {certification_level}")
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
        "rule_version": RULE_VERSION,
    })[:16]
    manifest_id = f"authority-intake-source-manifest:{certification_level}:{seed}"
    records: Dict[str, Any] = {}
    type_counts: Dict[str, int] = {}
    unique_hashes = set()
    for packet, case_id in adapter_packets:
        record = source_record_for_packet(packet, case_id, manifest_id, seed, as_of_date, certification_level)
        unique_hashes.add(str(record.get("authority_source_record_hash")))
        for key in authority_lookup_keys(packet, case_id):
            records[str(key)] = record
        typ = str(packet.get("adapter_type") or "")
        type_counts[typ] = type_counts.get(typ, 0) + 1
    manifest_hash = compact_hash({"manifest_id": manifest_id, "record_hashes": sorted(unique_hashes), "certification_level": certification_level})
    for record in records.values():
        if isinstance(record, dict):
            record["authority_source_manifest_hash"] = manifest_hash
    strict_count = len(adapter_packets) if certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE else 0
    return {
        "kind": "authority_intake_source_manifest",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "manifest_id": manifest_id,
        "created_at": as_of_date,
        "certification_level": certification_level,
        "evidence_origin": ORIGIN_STRICT_TEST if strict_count else ORIGIN_REFERENCE,
        "external_source_attestation_status": "not_external",
        "promotion_eligible": False,
        "manifest_hash": manifest_hash,
        "authority_source_records": records,
        "summary": {
            "answer_count": len(answers),
            "authority_adapter_count": len(adapter_packets),
            "authority_source_record_count": len(adapter_packets),
            "authority_source_unique_key_count": len(records),
            "authority_source_unique_record_count": len(unique_hashes),
            "implementation_grade_count": 0,
            "strict_schema_test_fixture_count": strict_count,
            "reference_fixture_count": len(adapter_packets) - strict_count,
            "fresh_source_count": len(adapter_packets),
            "primary_authority_count": 0,
            "promotion_eligible_count": 0,
            "adapter_type_counts": dict(sorted(type_counts.items())),
        },
        "non_doctrine_policy": "Archive-generated authority source manifests are fixtures. Implementation manifests must be externally supplied and independently attested.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build fixture source/provenance manifests for authority-intake interfaces.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Build authority source manifest for one case id")
    parser.add_argument("--all", action="store_true", help="Build authority source manifest for all golden cases")
    parser.add_argument("--as-of-date", help="Manifest creation date in YYYY-MM-DD format")
    parser.add_argument("--certification-level", choices=sorted(GENERATABLE_CERTIFICATION_LEVELS), default=CERT_REFERENCE_FIXTURE)
    parser.add_argument("--route-limit", type=int, default=ROUTE_LIMIT)
    parser.add_argument("--facts-only-candidate-limit", type=int, default=FACTS_ONLY_LIMIT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    receipt = load_json(root / "REVISION-RECEIPT.json") if (root / "REVISION-RECEIPT.json").exists() else {}
    as_of_date = args.as_of_date or str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    answers = load_answers(root, args.case_id, args.all, args.route_limit, args.facts_only_candidate_limit)
    manifest = manifest_for_answers(answers, as_of_date, args.certification_level)
    if args.json:
        print(json.dumps(manifest, separators=(",", ":")))
    else:
        s = manifest.get("summary", {})
        print(f"{RUNTIME_STATUS}: {s.get('authority_source_record_count')} fixture authority source records ({args.certification_level})")


if __name__ == "__main__":
    main()
