#!/usr/bin/env python3
"""Validate evidence bundles against decision-adapter requirements.

This is the execution boundary after adapter resolution. It deliberately does
not fetch live law or run fiscal models by itself. Instead, it checks whether an
external evidence bundle contains the exact current-law, jurisdiction, delivery,
no-go, or quantitative-model evidence required by each adapter packet. Rev0327 adds a producer boundary: supplied evidence must identify a registered evidence
producer contract before it can satisfy an adapter. Rev0333 adds an authority-source-manifest proof gate before raw authority intake can clear strict current-law and jurisdiction adapters.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
TOOLS_DIR = pathlib.Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
import verify_external_attestation
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

RUNTIME_STATUS = "decision_adapter_execution_evidence_checked"
RULE_VERSION = 9
STATUS_MISSING = "blocked_missing_external_evidence"
STATUS_INCOMPLETE = "blocked_incomplete_external_evidence"
STATUS_INVALID_PRODUCER = "blocked_invalid_or_unregistered_evidence_producer"
STATUS_STALE = "blocked_stale_or_expired_external_evidence"
STATUS_INPUT_HASH_MISMATCH = "blocked_model_input_hash_mismatch"
STATUS_INPUT_SOURCE_NOT_CERTIFIED = "blocked_model_input_source_not_certified"
STATUS_AUTHORITY_NOT_CERTIFIED = "blocked_authority_evidence_not_certified"
STATUS_ATTESTATION_NOT_VERIFIED = "blocked_external_attestation_not_verified"
STATUS_BLOCKS = "executed_evidence_blocks_finalization"
STATUS_SATISFIED = "executed_evidence_satisfies_adapter"

PRODUCER_REQUIRED_FIELDS = [
    "producer_id",
    "producer_contract_version",
    "evidence_kind",
    "created_at",
    "producer_mode",
]
CURRENT_LAW_REQUIRED_FIELDS = [
    "source_id",
    "checked_at",
    "retrieval_method",
    "authority_locator",
    "jurisdiction",
    "effective_date",
    "result_status",
    "reviewer_or_system",
    "claim_supported",
]
JURISDICTION_REQUIRED_FIELDS = [
    "jurisdiction",
    "effective_date",
    "authority_level",
    "preemption_or_treaty_conflict",
    "implementation_status",
    "conflict_resolution",
]
MODEL_REQUIRED_FIELDS = [
    "model_name",
    "model_version",
    "inputs_hash",
    "assumptions",
    "run_at",
    "uncertainty_method",
    "outputs",
    "model_input_bundle_id",
    "model_input_record_hash",
    "input_hash_basis",
    "input_locator",
    "assumption_set_id",
    "input_values_hash",
]
MODEL_ADAPTER_TYPES = {"quantitative_model_adapter", "floor_delivery_adapter", "no_go_threshold_adapter"}
AUTHORITY_ADAPTER_TYPES = {"current_law_refresh_adapter", "jurisdiction_scope_adapter"}
INPUT_SOURCE_PROOF_FIELDS = [
    "model_input_source_manifest_id",
    "input_source_record_hash",
    "input_source_manifest_hash",
    "input_certification_level",
    "implementation_grade_input_source",
    "source_contract_id",
    "source_locator",
    "source_coverage_period",
    "source_extraction_date",
    "source_freshness_status",
    "units_verified",
    "provenance_hash",
    "strict_schema_test_fixture",
    "evidence_origin",
    "external_source_attestation_status",
    "promotion_eligible",
]
NO_GO_EXTRA_FIELDS = ["threshold_result", "reviewer_or_system"]


AUTHORITY_PROOF_FIELDS = [
    "authority_evidence_bundle_id",
    "authority_evidence_record_hash",
    "authority_evidence_bundle_hash",
    "authority_certification_level",
    "implementation_grade_authority_evidence",
    "authority_source_contract_id",
    "authority_source_locator",
    "authority_checked_at",
    "authority_coverage_period",
    "authority_freshness_status",
    "authority_provenance_hash",
    "external_authority_claim_hash",
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

BLOCKING_CURRENT_LAW_RESULTS = {"changed", "superseded", "uncertain", "not_found"}
BLOCKING_NO_GO_RESULTS = {"triggered", "uncertain"}


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_answer_case(tools_dir: pathlib.Path):
    spec = importlib.util.spec_from_file_location("answer_case", tools_dir / "answer_case.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load answer_case.py")
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


def compact_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def adapter_binding(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the narrow adapter/case scope that external evidence may satisfy.

    A valid external signature over an evidence payload is not enough by itself:
    the evidence must be cryptographically bound to the specific adapter packet
    that will consume it, otherwise one signed record can be replayed into a
    neighboring route, case, source, or model slot.
    """
    return {
        "case_id": packet.get("case_id"),
        "adapter_id": packet.get("adapter_id"),
        "adapter_type": packet.get("adapter_type"),
        "route_id": packet.get("route_id"),
        "source_id": packet.get("source_id"),
        "model_class": packet.get("model_class"),
        "scope": packet.get("scope"),
        "required_outputs": sorted([str(x) for x in packet.get("required_outputs", [])]),
    }


def adapter_binding_hash(packet: Mapping[str, Any]) -> str:
    return compact_hash(adapter_binding(packet))


def adapter_key(packet: Mapping[str, Any]) -> str:
    return str(packet.get("adapter_id") or "")


def case_adapter_key(packet: Mapping[str, Any]) -> str:
    case_id = str(packet.get("case_id") or "")
    aid = adapter_key(packet)
    return f"{case_id}:{aid}" if case_id and aid else aid


def evidence_lookup_keys(packet: Mapping[str, Any]) -> List[str]:
    aid = adapter_key(packet)
    case_aid = case_adapter_key(packet)
    typ = str(packet.get("adapter_type", ""))
    rid = str(packet.get("route_id", ""))
    model = str(packet.get("model_class", ""))
    sid = str(packet.get("source_id", ""))
    scope = str(packet.get("scope", ""))
    keys = [case_aid, aid]
    if typ == "current_law_refresh_adapter" and sid:
        keys.extend([f"current_law:{sid}", sid])
    if typ == "jurisdiction_scope_adapter":
        keys.extend([f"jurisdiction_scope:{rid}", f"jurisdiction_scope:{rid}:{scope}", rid])
    if typ == "quantitative_model_adapter":
        keys.extend([f"model:{rid}:{model}", f"quantitative_model:{rid}:{model}", f"model:{model}"])
    if typ == "floor_delivery_adapter":
        keys.extend([f"floor_delivery:{rid}", f"model:{rid}:{model}"])
    if typ == "no_go_threshold_adapter":
        keys.extend([f"no_go_threshold:{rid}", f"model:{rid}:{model}"])
    return dedupe(keys)


def evidence_for_adapter(packet: Mapping[str, Any], bundle: Mapping[str, Any]) -> Dict[str, Any] | None:
    pools: List[Mapping[str, Any]] = []
    for name in ["adapter_evidence", "current_law", "jurisdiction_scope", "models", "floor_delivery", "no_go_threshold"]:
        value = bundle.get(name, {}) if isinstance(bundle, Mapping) else {}
        if isinstance(value, Mapping):
            pools.append(value)
    for key in evidence_lookup_keys(packet):
        for pool in pools:
            found = pool.get(key)
            if isinstance(found, Mapping):
                return dict(found)
    return None


def producer_contract_entries(bundle: Mapping[str, Any]) -> List[Dict[str, Any]]:
    raw = bundle.get("evidence_producer_contracts") or bundle.get("producer_contracts") or {}
    if isinstance(raw, Mapping) and isinstance(raw.get("producer_contracts"), list):
        return [dict(x) for x in raw.get("producer_contracts", []) if isinstance(x, Mapping)]
    if isinstance(raw, list):
        return [dict(x) for x in raw if isinstance(x, Mapping)]
    if isinstance(raw, Mapping):
        return [dict(x) for x in raw.values() if isinstance(x, Mapping)]
    return []


def producer_contract_lookup(bundle: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(c.get("producer_id")): c for c in producer_contract_entries(bundle) if c.get("producer_id")}


def producer_contract_for_evidence(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> Dict[str, Any]:
    return producer_contract_lookup(bundle).get(str(evidence.get("producer_id") or ""), {})


def _parse_date(value: Any) -> _dt.date | None:
    if not value:
        return None
    text = str(value)
    if "T" in text:
        text = text.split("T", 1)[0]
    try:
        return _dt.date.fromisoformat(text[:10])
    except ValueError:
        return None


def bundle_as_of_date(bundle: Mapping[str, Any], evidence: Mapping[str, Any]) -> _dt.date | None:
    context = bundle.get("execution_context", {}) if isinstance(bundle, Mapping) else {}
    if isinstance(context, Mapping):
        parsed = _parse_date(context.get("as_of_date"))
        if parsed:
            return parsed
    return _parse_date(bundle.get("as_of_date")) or _parse_date(evidence.get("created_at"))


def evidence_reference_date(evidence: Mapping[str, Any]) -> _dt.date | None:
    return _parse_date(evidence.get("checked_at")) or _parse_date(evidence.get("run_at")) or _parse_date(evidence.get("created_at"))


def freshness_validation(packet: Mapping[str, Any], evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> Dict[str, Any]:
    contract = producer_contract_for_evidence(evidence, bundle)
    policy_days = contract.get("freshness_policy_days")
    if policy_days in (None, "", [], {}):
        return {"freshness_status": "no_policy"}
    as_of = bundle_as_of_date(bundle, evidence)
    reference = evidence_reference_date(evidence)
    if not as_of or not reference:
        return {"freshness_status": "unknown_date", "freshness_policy_days": policy_days}
    age = (as_of - reference).days
    stale = age > int(policy_days)
    return {
        "freshness_status": "stale" if stale else "fresh",
        "freshness_policy_days": int(policy_days),
        "evidence_age_days": age,
        "evidence_reference_date": reference.isoformat(),
        "as_of_date": as_of.isoformat(),
    }


def contract_blocking_statuses(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> set[str]:
    contract = producer_contract_for_evidence(evidence, bundle)
    return {str(x) for x in contract.get("blocking_statuses", [])}


def missing_fields(evidence: Mapping[str, Any], fields: Sequence[str]) -> List[str]:
    return [field for field in fields if evidence.get(field) in (None, "", [], {})]


def missing_outputs(evidence: Mapping[str, Any], required_outputs: Sequence[str]) -> List[str]:
    outputs = evidence.get("outputs", {})
    if not isinstance(outputs, Mapping):
        return list(required_outputs)
    return [out for out in required_outputs if outputs.get(out) in (None, "", [], {})]


def required_fields_for_adapter(packet: Mapping[str, Any]) -> List[str]:
    typ = packet.get("adapter_type")
    fields: List[str] = list(PRODUCER_REQUIRED_FIELDS)
    if typ == "current_law_refresh_adapter":
        fields.extend(CURRENT_LAW_REQUIRED_FIELDS)
    elif typ == "jurisdiction_scope_adapter":
        fields.extend(JURISDICTION_REQUIRED_FIELDS)
        for field in packet.get("required_inputs", []):
            if field not in fields:
                fields.append(str(field))
    elif typ in {"quantitative_model_adapter", "floor_delivery_adapter"}:
        fields.extend(MODEL_REQUIRED_FIELDS)
    elif typ == "no_go_threshold_adapter":
        fields.extend(MODEL_REQUIRED_FIELDS + NO_GO_EXTRA_FIELDS)
    return dedupe(fields)


def strict_model_input_source_required(bundle: Mapping[str, Any]) -> bool:
    context = bundle.get("execution_context", {}) if isinstance(bundle, Mapping) else {}
    if isinstance(context, Mapping) and context.get("strict_model_input_source_certification_required") is True:
        return True
    return bundle.get("strict_model_input_source_certification_required") is True


def strict_authority_evidence_required(bundle: Mapping[str, Any]) -> bool:
    context = bundle.get("execution_context", {}) if isinstance(bundle, Mapping) else {}
    if isinstance(context, Mapping) and context.get("strict_authority_evidence_required") is True:
        return True
    return bundle.get("strict_authority_evidence_required") is True


def interface_fixture_evidence(evidence: Mapping[str, Any]) -> bool:
    mode = str(evidence.get("producer_mode") or "")
    return "interface" in mode or mode == "registered_interface_fixture"


def allow_internal_strict_schema_test_fixture(bundle: Mapping[str, Any]) -> bool:
    context = bundle.get("execution_context", {}) if isinstance(bundle, Mapping) else {}
    return isinstance(context, Mapping) and context.get("allow_internal_strict_schema_test_fixture") is True


def strict_schema_test_fixture_evidence(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> bool:
    return (
        allow_internal_strict_schema_test_fixture(bundle)
        and evidence.get("strict_schema_test_fixture") is True
        and evidence.get("evidence_origin") == "archive_generated_strict_schema_test_fixture"
        and evidence.get("external_source_attestation_status") == "not_external"
        and evidence.get("promotion_eligible") is False
    )


def external_attestation_required_for_promotion(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> bool:
    if strict_schema_test_fixture_evidence(evidence, bundle):
        return False
    implementation_grade_markers = [
        evidence.get("evidence_origin") == "external_observed",
        evidence.get("external_source_attestation_status") == "verified_external_attestation",
        evidence.get("promotion_eligible") is True,
        evidence.get("implementation_grade_input_source") is True,
        evidence.get("implementation_grade_authority_evidence") is True,
        evidence.get("implementation_grade_authority_intake") is True,
        evidence.get("implementation_grade_authority_source") is True,
    ]
    if interface_fixture_evidence(evidence) and not any(implementation_grade_markers):
        return False
    return any(implementation_grade_markers)


def external_attestation_verification_for_evidence(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> Dict[str, Any]:
    if not external_attestation_required_for_promotion(evidence, bundle):
        return {
            "runtime_status": verify_external_attestation.RUNTIME_STATUS,
            "verifier_profile": verify_external_attestation.PROFILE,
            "verifier_status": verify_external_attestation.STATUS_NOT_REQUIRED,
            "trusted_external_attestation": False,
            "errors": [],
            "evidence_payload_hash": verify_external_attestation.evidence_payload_hash(evidence),
            "adapter_binding_hash": evidence.get("adapter_binding_hash"),
            "attestation_hash": None,
            "signed_payload_hash": None,
            "trust_policy_hash": verify_external_attestation.trust_policy_hash(bundle),
        }
    return verify_external_attestation.verification_for_evidence(evidence, bundle)


def adapter_binding_validation_errors(packet: Mapping[str, Any], evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> List[str]:
    if not external_attestation_required_for_promotion(evidence, bundle):
        return []
    expected = adapter_binding_hash(packet)
    errors: List[str] = []
    actual = evidence.get("adapter_binding_hash")
    if actual in (None, "", [], {}):
        errors.append("missing_adapter_binding_hash")
    elif actual != expected:
        errors.append("adapter_binding_hash_mismatch")
    attestation = evidence.get("external_attestation") or evidence.get("attestation") or {}
    signed_payload = attestation.get("signed_payload") if isinstance(attestation, Mapping) else {}
    if not isinstance(signed_payload, Mapping):
        signed_payload = {}
    if signed_payload.get("adapter_binding_hash") in (None, "", [], {}):
        errors.append("signed_payload_missing_adapter_binding_hash")
    elif signed_payload.get("adapter_binding_hash") != expected:
        errors.append("signed_payload_adapter_binding_hash_mismatch")
    for field in ["case_id", "adapter_id", "route_id", "source_id", "model_class", "scope"]:
        if evidence.get(field) not in (None, "", [], {}) and str(evidence.get(field)) != str(packet.get(field) or ""):
            errors.append(f"evidence_{field}_mismatch")
    return dedupe(errors)


def external_attestation_validation_errors(evidence: Mapping[str, Any], bundle: Mapping[str, Any], packet: Mapping[str, Any] | None = None) -> List[str]:
    if not external_attestation_required_for_promotion(evidence, bundle):
        return []
    binding_errors = adapter_binding_validation_errors(packet, evidence, bundle) if packet is not None else []
    verification = external_attestation_verification_for_evidence(evidence, bundle)
    verifier_errors: List[str] = []
    if verification.get("verifier_status") != verify_external_attestation.STATUS_VERIFIED:
        verifier_errors = [
            f"external_attestation_verifier_not_verified:{verification.get('verifier_status')}",
            *[str(err) for err in verification.get("errors", [])],
        ]
    return dedupe(binding_errors + verifier_errors)


def trusted_attestation_verifier_status(bundle: Mapping[str, Any]) -> str:
    return verify_external_attestation.configured_verifier_status(bundle)


def model_input_source_validation_errors(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> List[str]:
    if not strict_model_input_source_required(bundle):
        return []
    errors: List[str] = []
    strict_test = strict_schema_test_fixture_evidence(evidence, bundle)
    if interface_fixture_evidence(evidence) and not strict_test:
        errors.append("registered_interface_fixture_cannot_satisfy_strict_model_input_source_certification")
    missing = missing_fields(evidence, INPUT_SOURCE_PROOF_FIELDS)
    if missing:
        errors.append("missing_input_source_fields:" + ",".join(missing))
    if strict_test:
        if evidence.get("input_certification_level") != "strict_schema_test_fixture":
            errors.append("strict_test_input_certification_level_must_be_strict_schema_test_fixture")
        if evidence.get("implementation_grade_input_source") is not False:
            errors.append("strict_test_implementation_grade_input_source_must_be_false")
    else:
        if evidence.get("input_certification_level") != "implementation_grade":
            errors.append("input_certification_level_must_be_implementation_grade")
        if evidence.get("implementation_grade_input_source") is not True:
            errors.append("implementation_grade_input_source_must_be_true")
        if evidence.get("evidence_origin") != "external_observed":
            errors.append("implementation_evidence_origin_must_be_external_observed")
        if evidence.get("external_source_attestation_status") != "verified_external_attestation":
            errors.append("implementation_external_source_attestation_must_be_verified")
        if evidence.get("promotion_eligible") is not True:
            errors.append("implementation_evidence_must_be_promotion_eligible")
    if evidence.get("source_freshness_status") != "fresh":
        errors.append("input_source_must_be_fresh")
    if evidence.get("units_verified") is not True:
        errors.append("input_source_units_must_be_verified")
    if not isinstance(evidence.get("source_coverage_period"), Mapping):
        errors.append("source_coverage_period_must_be_structured")
    return dedupe(errors)



def authority_evidence_validation_errors(evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> List[str]:
    if not strict_authority_evidence_required(bundle):
        return []
    errors: List[str] = []
    strict_test = strict_schema_test_fixture_evidence(evidence, bundle)
    if interface_fixture_evidence(evidence) and not strict_test:
        errors.append("registered_interface_fixture_cannot_satisfy_strict_authority_evidence")
    missing = missing_fields(evidence, AUTHORITY_PROOF_FIELDS)
    if missing:
        errors.append("missing_authority_proof_fields:" + ",".join(missing))
    if strict_test:
        for field in ["authority_certification_level", "authority_intake_certification_level", "authority_source_certification_level"]:
            if evidence.get(field) != "strict_schema_test_fixture":
                errors.append(f"strict_test_{field}_must_be_strict_schema_test_fixture")
        for field in ["implementation_grade_authority_evidence", "implementation_grade_authority_intake", "implementation_grade_authority_source"]:
            if evidence.get(field) is not False:
                errors.append(f"strict_test_{field}_must_be_false")
    else:
        if evidence.get("authority_certification_level") != "implementation_grade":
            errors.append("authority_certification_level_must_be_implementation_grade")
        if evidence.get("implementation_grade_authority_evidence") is not True:
            errors.append("implementation_grade_authority_evidence_must_be_true")
        if evidence.get("authority_intake_certification_level") != "implementation_grade":
            errors.append("authority_intake_certification_level_must_be_implementation_grade")
        if evidence.get("implementation_grade_authority_intake") is not True:
            errors.append("implementation_grade_authority_intake_must_be_true")
        if evidence.get("authority_source_certification_level") != "implementation_grade":
            errors.append("authority_source_certification_level_must_be_implementation_grade")
        if evidence.get("implementation_grade_authority_source") is not True:
            errors.append("implementation_grade_authority_source_must_be_true")
        if evidence.get("authority_primary_authority") is not True:
            errors.append("authority_primary_authority_must_be_true")
        if evidence.get("authority_source_primary_authority") is not True:
            errors.append("authority_source_primary_authority_must_be_true")
        if evidence.get("evidence_origin") != "external_observed":
            errors.append("implementation_evidence_origin_must_be_external_observed")
        if evidence.get("external_source_attestation_status") != "verified_external_attestation":
            errors.append("implementation_external_source_attestation_must_be_verified")
        if evidence.get("promotion_eligible") is not True:
            errors.append("implementation_evidence_must_be_promotion_eligible")
        source_type = str(evidence.get("authority_source_type") or "")
        if source_type in {"reference_fixture", "registered_interface_fixture", "fixture"} or "fixture" in source_type:
            errors.append("authority_source_type_must_not_be_fixture")
        raw_locator = str(evidence.get("authority_raw_locator") or evidence.get("authority_source_locator") or "")
        source_locator = str(evidence.get("authority_retrieval_source_locator") or "")
        retrieval_source_type = str(evidence.get("authority_retrieval_source_type") or "")
        if "fixture" in raw_locator or raw_locator.startswith("fixture://") or raw_locator.startswith("authority-intake-reference://"):
            errors.append("authority_raw_locator_must_not_be_fixture")
        if "fixture" in source_locator or source_locator.startswith("fixture://") or source_locator.startswith("reference-authority-source://"):
            errors.append("authority_retrieval_source_locator_must_not_be_fixture")
        if "fixture" in retrieval_source_type:
            errors.append("authority_retrieval_source_type_must_not_be_fixture")
    if evidence.get("authority_freshness_status") != "fresh":
        errors.append("authority_evidence_must_be_fresh")
    if not isinstance(evidence.get("authority_coverage_period"), Mapping):
        errors.append("authority_coverage_period_must_be_structured")
    if evidence.get("authority_record_claim_supported") is not True:
        errors.append("authority_record_claim_supported_must_be_true")
    if evidence.get("authority_intake_freshness_status") != "fresh":
        errors.append("authority_intake_must_be_fresh")
    if evidence.get("authority_source_freshness_status") != "fresh":
        errors.append("authority_source_must_be_fresh")
    return dedupe(errors)


def producer_validation_errors(packet: Mapping[str, Any], evidence: Mapping[str, Any], bundle: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    lookup = producer_contract_lookup(bundle)
    producer_id = str(evidence.get("producer_id") or "")
    if not lookup:
        errors.append("missing_producer_contract_manifest")
        return errors
    contract = lookup.get(producer_id)
    if not contract:
        errors.append(f"unregistered_producer:{producer_id or 'blank'}")
        return errors
    adapter_type = str(packet.get("adapter_type") or "")
    if adapter_type not in [str(x) for x in contract.get("adapter_types", [])]:
        errors.append(f"producer_does_not_cover_adapter_type:{adapter_type}")
    if str(evidence.get("producer_contract_version") or "") != str(contract.get("contract_version") or ""):
        errors.append("producer_contract_version_mismatch")
    if str(evidence.get("evidence_kind") or "") != adapter_type:
        errors.append("evidence_kind_does_not_match_adapter_type")
    modes = {str(x) for x in contract.get("permitted_execution_modes", [])}
    if modes and str(evidence.get("producer_mode") or "") not in modes:
        errors.append("producer_mode_not_permitted")
    if contract.get("stores_doctrine") is not False:
        errors.append("producer_contract_must_not_store_doctrine")
    if contract.get("output_retention") != "external_evidence_bundle_only":
        errors.append("producer_contract_output_retention_must_be_external_bundle_only")
    return errors


def cannot_finalize_marker(packet: Mapping[str, Any], status: str) -> str:
    typ = str(packet.get("adapter_type", "unknown_adapter"))
    rid = str(packet.get("route_id", "unknown_route"))
    sid = packet.get("source_id")
    model = packet.get("model_class") or packet.get("scope")
    suffix = sid or model or adapter_key(packet) or "evidence"
    return f"execute_{typ}:{rid}:{suffix}:{status}"


def execute_adapter(packet: Mapping[str, Any], bundle: Mapping[str, Any]) -> Dict[str, Any]:
    evidence = evidence_for_adapter(packet, bundle)
    required_fields = required_fields_for_adapter(packet)
    required_outputs = [str(x) for x in packet.get("required_outputs", [])]
    base = {
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "adapter_id": packet.get("adapter_id"),
        "adapter_type": packet.get("adapter_type"),
        "route_id": packet.get("route_id"),
        "source_id": packet.get("source_id"),
        "model_class": packet.get("model_class"),
        "adapter_binding_hash": adapter_binding_hash(packet),
        "required_fields": required_fields,
        "required_outputs": required_outputs,
    }
    if not evidence:
        status = STATUS_MISSING
        base.update({
            "execution_status": status,
            "finalization_status": "blocked",
            "missing_fields": required_fields,
            "missing_outputs": required_outputs,
            "cannot_finalize_marker": cannot_finalize_marker(packet, status),
        })
        return base

    missing = missing_fields(evidence, required_fields)
    missing_out = missing_outputs(evidence, required_outputs)
    if missing or missing_out:
        status = STATUS_INCOMPLETE
        base.update({
            "execution_status": status,
            "finalization_status": "blocked",
            "missing_fields": missing,
            "missing_outputs": missing_out,
            "cannot_finalize_marker": cannot_finalize_marker(packet, status),
            "evidence_locator": evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
            "producer_id": evidence.get("producer_id"),
        })
        return base

    producer_errors = producer_validation_errors(packet, evidence, bundle)
    if producer_errors:
        status = STATUS_INVALID_PRODUCER
        base.update({
            "execution_status": status,
            "finalization_status": "blocked",
            "missing_fields": [],
            "missing_outputs": [],
            "producer_id": evidence.get("producer_id"),
            "producer_validation_errors": producer_errors,
            "cannot_finalize_marker": cannot_finalize_marker(packet, status),
            "evidence_locator": evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
        })
        return base

    attestation_verification = external_attestation_verification_for_evidence(evidence, bundle)
    attestation_errors = external_attestation_validation_errors(evidence, bundle, packet)
    if attestation_errors:
        status = STATUS_ATTESTATION_NOT_VERIFIED
        base.update({
            "execution_status": status,
            "finalization_status": "blocked",
            "missing_fields": [],
            "missing_outputs": [],
            "producer_id": evidence.get("producer_id"),
            "producer_contract_version": evidence.get("producer_contract_version"),
            "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
            "external_attestation_validation_errors": attestation_errors,
            "adapter_binding_validation_errors": adapter_binding_validation_errors(packet, evidence, bundle),
            "external_attestation_verification_hash": compact_hash(attestation_verification),
            "cannot_finalize_marker": cannot_finalize_marker(packet, status),
            "evidence_locator": evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
        })
        return base

    typ = packet.get("adapter_type")
    if typ in AUTHORITY_ADAPTER_TYPES:
        authority_errors = authority_evidence_validation_errors(evidence, bundle)
        if authority_errors:
            status = STATUS_AUTHORITY_NOT_CERTIFIED
            base.update({
                "execution_status": status,
                "finalization_status": "blocked",
                "missing_fields": [],
                "missing_outputs": [],
                "producer_id": evidence.get("producer_id"),
                "producer_contract_version": evidence.get("producer_contract_version"),
                "authority_evidence_validation_errors": authority_errors,
                "authority_certification_level": evidence.get("authority_certification_level"),
                "authority_evidence_bundle_id": evidence.get("authority_evidence_bundle_id"),
                "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
                "external_attestation_verification_hash": compact_hash(attestation_verification),
                "cannot_finalize_marker": cannot_finalize_marker(packet, status),
                "evidence_locator": evidence.get("authority_source_locator") or evidence.get("authority_locator") or evidence.get("evidence_locator"),
            })
            return base
    if typ in MODEL_ADAPTER_TYPES:
        input_errors: List[str] = []
        if evidence.get("input_hash_basis") != "explicit_model_input_bundle":
            input_errors.append("input_hash_basis_must_be_explicit_model_input_bundle")
        if evidence.get("inputs_hash") != evidence.get("model_input_record_hash"):
            input_errors.append("inputs_hash_must_equal_model_input_record_hash")
        if input_errors:
            status = STATUS_INPUT_HASH_MISMATCH
            base.update({
                "execution_status": status,
                "finalization_status": "blocked",
                "missing_fields": [],
                "missing_outputs": [],
                "producer_id": evidence.get("producer_id"),
                "producer_contract_version": evidence.get("producer_contract_version"),
                "model_input_validation_errors": input_errors,
                "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
                "external_attestation_verification_hash": compact_hash(attestation_verification),
                "cannot_finalize_marker": cannot_finalize_marker(packet, status),
                "evidence_locator": evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
            })
            return base
        source_errors = model_input_source_validation_errors(evidence, bundle)
        if source_errors:
            status = STATUS_INPUT_SOURCE_NOT_CERTIFIED
            base.update({
                "execution_status": status,
                "finalization_status": "blocked",
                "missing_fields": [],
                "missing_outputs": [],
                "producer_id": evidence.get("producer_id"),
                "producer_contract_version": evidence.get("producer_contract_version"),
                "model_input_source_validation_errors": source_errors,
                "input_certification_level": evidence.get("input_certification_level"),
                "model_input_source_manifest_id": evidence.get("model_input_source_manifest_id"),
                "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
                "external_attestation_verification_hash": compact_hash(attestation_verification),
                "cannot_finalize_marker": cannot_finalize_marker(packet, status),
                "evidence_locator": evidence.get("source_locator") or evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
            })
            return base

    freshness = freshness_validation(packet, evidence, bundle)
    if freshness.get("freshness_status") == "stale":
        status = STATUS_STALE
        base.update({
            "execution_status": status,
            "finalization_status": "blocked",
            "missing_fields": [],
            "missing_outputs": [],
            "producer_id": evidence.get("producer_id"),
            "producer_contract_version": evidence.get("producer_contract_version"),
            "freshness": freshness,
            "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
            "external_attestation_verification_hash": compact_hash(attestation_verification),
            "cannot_finalize_marker": cannot_finalize_marker(packet, status),
            "evidence_locator": evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
        })
        return base

    blocks = False
    block_reason = ""
    blocking_statuses = contract_blocking_statuses(evidence, bundle)
    if typ == "current_law_refresh_adapter":
        result = str(evidence.get("result_status", ""))
        claim_supported = evidence.get("claim_supported")
        if result in (BLOCKING_CURRENT_LAW_RESULTS | blocking_statuses) or claim_supported is False:
            blocks = True
            block_reason = "current-law evidence changed, superseded, did not support, or could not verify the source claim"
    if typ == "jurisdiction_scope_adapter":
        implementation_status = str(evidence.get("implementation_status", ""))
        conflict_resolution = str(evidence.get("conflict_resolution", ""))
        conflict = str(evidence.get("preemption_or_treaty_conflict", ""))
        if (implementation_status in blocking_statuses or conflict_resolution in blocking_statuses
                or implementation_status in {"not_in_force", "uncertain_scope", "uncertain", "unknown"}
                or conflict_resolution in {"unresolved_conflict", "uncertain", "not_resolved"}
                or conflict in {"unresolved_conflict", "uncertain", "unknown"}):
            blocks = True
            block_reason = "jurisdiction or effective-date evidence leaves scope, force, preemption, treaty, or implementation conflict unresolved"
    if typ in {"quantitative_model_adapter", "floor_delivery_adapter"}:
        result = str(evidence.get("result_status", ""))
        if result in blocking_statuses:
            blocks = True
            block_reason = "model evidence reports a blocking status under the registered producer contract"
    if typ == "no_go_threshold_adapter":
        result = str(evidence.get("threshold_result", ""))
        if result in (BLOCKING_NO_GO_RESULTS | blocking_statuses):
            blocks = True
            block_reason = "no-go threshold evidence triggers or leaves unresolved a nonpricing/noncompensable harm gate"

    status = STATUS_BLOCKS if blocks else STATUS_SATISFIED
    base.update({
        "execution_status": status,
        "finalization_status": "blocked" if blocks else "satisfied",
        "missing_fields": [],
        "missing_outputs": [],
        "producer_id": evidence.get("producer_id"),
        "producer_contract_version": evidence.get("producer_contract_version"),
        "evidence_kind": evidence.get("evidence_kind"),
        "evidence_hash": compact_hash(evidence),
        "evidence_adapter_binding_hash": evidence.get("adapter_binding_hash"),
        "evidence_locator": evidence.get("authority_locator") or evidence.get("run_locator") or evidence.get("evidence_locator"),
        "evidence_checked_at": evidence.get("checked_at") or evidence.get("run_at") or evidence.get("created_at"),
        "evidence_result_status": evidence.get("result_status") or evidence.get("threshold_result") or "executed",
        "external_attestation_verifier_status": attestation_verification.get("verifier_status"),
        "external_attestation_verification_hash": compact_hash(attestation_verification),
        "freshness": freshness,
    })
    if blocks:
        base["block_reason"] = block_reason
        base["cannot_finalize_marker"] = cannot_finalize_marker(packet, status)
    return base


def summarize_execution(results: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    type_counts: Dict[str, int] = {}
    status_counts: Dict[str, int] = {}
    finalization_counts: Dict[str, int] = {}
    producer_counts: Dict[str, int] = {}
    for result in results:
        typ = str(result.get("adapter_type"))
        status = str(result.get("execution_status"))
        finality = str(result.get("finalization_status"))
        producer = result.get("producer_id")
        type_counts[typ] = type_counts.get(typ, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        finalization_counts[finality] = finalization_counts.get(finality, 0) + 1
        if producer:
            producer_counts[str(producer)] = producer_counts.get(str(producer), 0) + 1
    blocked = sum(1 for r in results if r.get("finalization_status") != "satisfied")
    satisfied = sum(1 for r in results if r.get("finalization_status") == "satisfied")
    return {
        "execution_check_count": len(results),
        "satisfied_count": satisfied,
        "blocked_count": blocked,
        "registered_producer_result_count": sum(producer_counts.values()),
        "all_adapters_satisfied": bool(results) and blocked == 0,
        "can_finalize": bool(results) and blocked == 0,
        "execution_status_counts": dict(sorted(status_counts.items())),
        "finalization_status_counts": dict(sorted(finalization_counts.items())),
        "adapter_type_counts": dict(sorted(type_counts.items())),
        "producer_id_counts": dict(sorted(producer_counts.items())),
    }


def attach_default_producer_contracts(root: pathlib.Path, bundle: Mapping[str, Any]) -> Dict[str, Any]:
    out = dict(bundle)
    if out.get("producer_contracts") or out.get("evidence_producer_contracts"):
        return out
    path = root / "docs/00-meta/evidence-producer-contracts.json"
    if path.exists():
        out["producer_contracts"] = load_json(path).get("producer_contracts", [])
    return out


def execute_disposition(disposition: Mapping[str, Any], evidence_bundle: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    bundle = evidence_bundle or {}
    case_id = disposition.get("case_id")
    checks = []
    for packet in disposition.get("adapter_checks", []):
        item = dict(packet)
        item.setdefault("case_id", case_id)
        checks.append(item)
    results = [execute_adapter(packet, bundle) for packet in checks]
    summary = summarize_execution(results)
    markers = dedupe([r.get("cannot_finalize_marker") for r in results if r.get("cannot_finalize_marker")])
    return {
        "runtime_status": RUNTIME_STATUS,
        "rule_version": RULE_VERSION,
        "case_id": disposition.get("case_id"),
        "adapter_execution_results": results,
        "execution_summary": summary,
        "cannot_finalize_until": markers,
        "substance_note": "Adapter execution validates supplied external evidence from registered producer contracts only; it does not fetch live law, run fiscal models, or turn archive references into current legal advice.",
    }


def execute_answer(answer: Mapping[str, Any], evidence_bundle: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    packet = execute_disposition(answer.get("disposition", {}), evidence_bundle)
    packet["case_id"] = answer.get("case_id") or packet.get("case_id")
    packet["title"] = answer.get("title")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate evidence bundles against decision-adapter packets.")
    parser.add_argument("root", nargs="?", default=".", help="Archive root")
    parser.add_argument("--case-id", help="Execute adapters for one case id")
    parser.add_argument("--all", action="store_true", help="Execute adapters for all golden cases")
    parser.add_argument("--evidence", help="JSON evidence bundle keyed by adapter_id or adapter-specific lookup keys")
    parser.add_argument("--route-limit", type=int, default=5, help="Selected route count to include")
    parser.add_argument("--facts-only-candidate-limit", type=int, default=8, help="Facts-only candidate count to include")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    evidence_bundle = load_json(pathlib.Path(args.evidence).resolve()) if args.evidence else {}
    evidence_bundle = attach_default_producer_contracts(root, evidence_bundle)
    answer_case = load_answer_case(root / "tools")
    golden = load_json(root / "docs/00-meta/golden-cases.json")
    cases = golden.get("cases", [])
    if args.case_id:
        cases = [case for case in cases if case.get("case_id") == args.case_id]
        if not cases:
            raise SystemExit(f"unknown case id: {args.case_id}")
    elif not args.all:
        raise SystemExit("provide --case-id or --all")

    runtime = answer_case.AnswerRuntime(root, args.route_limit, args.facts_only_candidate_limit)
    answers = [runtime.answer_case(case) for case in cases]
    executions = [execute_answer(answer, evidence_bundle) for answer in answers]
    all_results = [r for packet in executions for r in packet.get("adapter_execution_results", [])]
    payload = {
        "kind": "decision_adapter_execution_packets",
        "runtime_status": RUNTIME_STATUS,
        "case_count": len(executions),
        "execution_summary": summarize_execution(all_results),
        "executions": executions,
    }
    if args.json:
        print(json.dumps(payload, separators=(",", ":")))
    else:
        for packet in executions:
            summary = packet.get("execution_summary", {})
            print(f"{packet.get('case_id')}: {summary.get('satisfied_count', 0)} satisfied, {summary.get('blocked_count', 0)} blocked")


if __name__ == "__main__":
    main()
