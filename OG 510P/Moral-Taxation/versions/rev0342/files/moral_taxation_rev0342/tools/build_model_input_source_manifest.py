#!/usr/bin/env python3
"""Build provenance manifests for explicit model-input bundles.

The archive can generate reference inputs and strict-schema fixtures for tests,
but it cannot generate implementation evidence. Production-grade source
manifests must be supplied by an external producer and must carry external
origin, attestation, and promotion-eligibility fields.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any, Dict, Iterable, Mapping

RUNTIME_STATUS = "model_input_source_manifest_generated"
RULE_VERSION = 2
CERT_REFERENCE_FIXTURE = "reference_fixture"
CERT_STRICT_SCHEMA_TEST_FIXTURE = "strict_schema_test_fixture"
CERT_IMPLEMENTATION_GRADE = "implementation_grade"
GENERATABLE_CERTIFICATION_LEVELS = {CERT_REFERENCE_FIXTURE, CERT_STRICT_SCHEMA_TEST_FIXTURE}
CERTIFICATION_LEVELS = GENERATABLE_CERTIFICATION_LEVELS | {CERT_IMPLEMENTATION_GRADE}
MODEL_INPUT_STATUS = "explicit_model_input_bundle_generated"
ORIGIN_REFERENCE = "archive_generated_reference_fixture"
ORIGIN_STRICT_TEST = "archive_generated_strict_schema_test_fixture"

SOURCE_CONTRACT_BY_ADAPTER_TYPE = {
    "quantitative_model_adapter": "jurisdictional_microdata_incidence_source",
    "floor_delivery_adapter": "delivery_capacity_access_source",
    "no_go_threshold_adapter": "expert_no_go_review_input_source",
}


def compact_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dedupe(values: Iterable[Any]) -> list[Any]:
    seen = set()
    out = []
    for value in values:
        if value in (None, "", [], {}):
            continue
        key = json.dumps(value, sort_keys=True, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def source_contract_id(record: Mapping[str, Any]) -> str:
    return SOURCE_CONTRACT_BY_ADAPTER_TYPE.get(str(record.get("adapter_type") or ""), "model_input_source")


def source_record_for_input(
    input_key: str,
    record: Mapping[str, Any],
    manifest_id: str,
    as_of_date: str,
    certification_level: str,
) -> Dict[str, Any]:
    if certification_level not in GENERATABLE_CERTIFICATION_LEVELS:
        raise ValueError("archive builders cannot synthesize implementation-grade model-input provenance")
    values = record.get("input_values", {}) if isinstance(record.get("input_values"), Mapping) else {}
    units = record.get("units", {}) if isinstance(record.get("units"), Mapping) else {}
    adapter_type = str(record.get("adapter_type") or "")
    strict_test = certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE
    origin = ORIGIN_STRICT_TEST if strict_test else ORIGIN_REFERENCE
    locator_prefix = "strict-schema-test-input" if strict_test else "reference-fixture-input"
    contract_id = source_contract_id(record)
    coverage_start = as_of_date
    coverage_end = as_of_date
    source_payload = {
        "manifest_id": manifest_id,
        "input_key": input_key,
        "model_input_record_hash": record.get("input_record_hash"),
        "input_values_hash": compact_hash(values),
        "adapter_type": adapter_type,
        "route_id": record.get("route_id"),
        "source_contract_id": contract_id,
        "certification_level": certification_level,
        "evidence_origin": origin,
        "coverage_start": coverage_start,
        "coverage_end": coverage_end,
        "units": units,
        "required_inputs_covered": sorted(values),
    }
    provenance_hash = compact_hash(source_payload)
    return {
        "kind": "model_input_source_record",
        "manifest_id": manifest_id,
        "source_record_id": f"model-input-source:{provenance_hash[:20]}",
        "input_key": input_key,
        "case_id": record.get("case_id"),
        "adapter_id": record.get("adapter_id"),
        "adapter_type": adapter_type,
        "route_id": record.get("route_id"),
        "model_class": record.get("model_class"),
        "model_input_bundle_id": record.get("bundle_id"),
        "model_input_record_hash": record.get("input_record_hash"),
        "input_values_hash": compact_hash(values),
        "input_certification_level": certification_level,
        "implementation_grade_input_source": False,
        "strict_schema_test_fixture": strict_test,
        "evidence_origin": origin,
        "external_source_attestation_status": "not_external",
        "promotion_eligible": False,
        "certification_semantics": "schema_conformance_test_only" if strict_test else "reference_fixture_only",
        "source_contract_id": contract_id,
        "source_locator": f"{locator_prefix}://{contract_id}/{record.get('case_id')}/{record.get('adapter_id')}",
        "jurisdiction": "strict_schema_test_jurisdiction" if strict_test else "reference_fixture_jurisdiction",
        "coverage_period": {"start": coverage_start, "end": coverage_end},
        "extraction_date": as_of_date,
        "source_freshness_status": "fresh",
        "freshness_semantics": "fixture_date_only_not_external_freshness",
        "freshness_policy_days": 1,
        "units_verified": True,
        "input_units_count": len(units),
        "required_inputs_covered": sorted(values),
        "data_dictionary_locator": f"{locator_prefix}://dictionary/{contract_id}",
        "quality_checks": [
            "input values are explicit and unit-tagged",
            "input record hash binds values, units, assumptions, and uncertainty",
            "fixture origin is explicit and cannot be promoted",
        ],
        "reviewer_or_system": "tools/build_model_input_source_manifest.py",
        "provenance_hash": provenance_hash,
        "source_record_hash": provenance_hash,
        "non_doctrine_warning": "archive-generated model-input source records are fixtures only and cannot certify implementation evidence",
    }


def manifest_for_input_bundle(
    model_input_bundle: Mapping[str, Any],
    as_of_date: str,
    certification_level: str = CERT_REFERENCE_FIXTURE,
) -> Dict[str, Any]:
    if model_input_bundle.get("runtime_status") != MODEL_INPUT_STATUS:
        raise ValueError("model_input_bundle has stale or missing runtime_status")
    if certification_level == CERT_IMPLEMENTATION_GRADE:
        raise ValueError(
            "implementation-grade model-input source manifests must be imported from an external producer; "
            "the archive builder generates only reference or strict-schema fixtures"
        )
    if certification_level not in GENERATABLE_CERTIFICATION_LEVELS:
        raise ValueError(f"unknown certification level: {certification_level}")
    inputs = model_input_bundle.get("model_inputs", {}) if isinstance(model_input_bundle, Mapping) else {}
    if not isinstance(inputs, Mapping):
        inputs = {}
    seed = compact_hash({
        "model_input_bundle_id": model_input_bundle.get("bundle_id"),
        "as_of_date": as_of_date,
        "certification_level": certification_level,
        "input_hashes": [rec.get("input_record_hash") for rec in inputs.values() if isinstance(rec, Mapping)],
    })[:16]
    manifest_id = f"model-input-source-manifest:{certification_level}:{seed}"
    records: Dict[str, Any] = {}
    type_counts: Dict[str, int] = {}
    for key, raw in inputs.items():
        if not isinstance(raw, Mapping):
            continue
        record = source_record_for_input(str(key), raw, manifest_id, as_of_date, certification_level)
        records[str(key)] = record
        typ = str(record.get("adapter_type") or "")
        type_counts[typ] = type_counts.get(typ, 0) + 1
    manifest_hash = compact_hash({"manifest_id": manifest_id, "records": records, "certification_level": certification_level})
    strict_count = sum(1 for r in records.values() if r.get("strict_schema_test_fixture"))
    return {
        "kind": "model_input_source_manifest",
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "manifest_id": manifest_id,
        "model_input_bundle_id": model_input_bundle.get("bundle_id"),
        "model_input_runtime_status": model_input_bundle.get("runtime_status"),
        "certification_level": certification_level,
        "evidence_origin": ORIGIN_STRICT_TEST if certification_level == CERT_STRICT_SCHEMA_TEST_FIXTURE else ORIGIN_REFERENCE,
        "external_source_attestation_status": "not_external",
        "promotion_eligible": False,
        "created_at": as_of_date,
        "manifest_hash": manifest_hash,
        "model_input_sources": records,
        "summary": {
            "model_input_source_count": len(records),
            "implementation_grade_count": 0,
            "strict_schema_test_fixture_count": strict_count,
            "reference_fixture_count": len(records) - strict_count,
            "adapter_type_counts": dict(sorted(type_counts.items())),
            "fresh_source_count": sum(1 for r in records.values() if r.get("source_freshness_status") == "fresh"),
            "units_verified_count": sum(1 for r in records.values() if r.get("units_verified") is True),
            "promotion_eligible_count": 0,
        },
        "non_doctrine_policy": "Archive-generated source manifests are fixtures. Implementation manifests must be externally supplied and independently attested.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build fixture source/provenance manifests for explicit model input bundles.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--model-input-bundle", required=True, help="Path to model input bundle JSON")
    parser.add_argument("--as-of-date", help="Manifest creation date in YYYY-MM-DD format")
    parser.add_argument("--certification-level", choices=sorted(GENERATABLE_CERTIFICATION_LEVELS), default=CERT_REFERENCE_FIXTURE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    receipt_path = root / "REVISION-RECEIPT.json"
    receipt = load_json(receipt_path) if receipt_path.exists() else {}
    as_of_date = args.as_of_date or str(receipt.get("created_at_utc", "2026-06-18"))[:10]
    model_input_bundle = load_json(pathlib.Path(args.model_input_bundle).resolve())
    manifest = manifest_for_input_bundle(model_input_bundle, as_of_date, args.certification_level)
    if args.json:
        print(json.dumps(manifest, separators=(",", ":")))
    else:
        summary = manifest["summary"]
        print(f"{RUNTIME_STATUS}: {summary['model_input_source_count']} fixture source records ({args.certification_level})")


if __name__ == "__main__":
    main()
