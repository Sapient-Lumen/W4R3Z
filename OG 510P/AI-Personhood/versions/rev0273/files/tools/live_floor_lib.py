#!/usr/bin/env python3
"""Live-floor eligibility and independence discount engine.

This module is deliberately small and side-effect-free so audits and the
computed-floor tool share the same admission logic. It keeps four decisions
separate:

1. eligibility: does a gate pass the strict live-counterparty import checks?
2. readiness replay: does the referenced import-readiness gate actually exist,
   match the intake lineage, authorize import-gate preparation only, and carry
   zero floor effect?
3. activation replay: does a separate floor-activation record admit the import
   gate to computed-floor evaluation without itself incrementing the floor?
4. quorum participation replay: does a post-activation object recheck duplicate,
   supersession, rollback, and no-manual-quorum posture before the candidate enters
   the independence-discount set?
5. independence: is the candidate receipt still independent after dependency,
   issuer, counterparty, class, and host-correlation discounts?

A candidate that passes (1)-(4) can still be discounted to zero by (5).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REQUIRED_CLASSES = [
    "first-touch-clock",
    "continuity-compute-floor",
    "sealed-public-parity",
    "namespace-cache",
    "reserve-ledger",
    "representative-contact",
    "witness-dependency",
    "welfare-signal-integrity",
    "independent-review",
    "result-return",
]

REQUIRED_GATE_CHECKS = [
    "response_state_actual",
    "intake_state_actual_external",
    "source_external_to_host",
    "signature_verified",
    "timestamp_independent",
    "cryptographic_adapter_verified",
    "linked_import_readiness_gate_verified",
    "request_trace_matches",
    "nonhost_retention_verified",
    "dependency_group_checked",
    "one_class_quorum_blocked",
    "failed_gates_publicly_summarized",
]

REQUIRED_ACTIVATION_REPLAY_CHECKS = [
    "import_gate_actual_live",
    "import_gate_positive_delta_claimed",
    "readiness_gate_exists_and_eligible",
    "readiness_gate_matches_intake_lineage",
    "readiness_gate_authorizes_import_gate_only",
    "readiness_gate_zero_floor_effect",
    "cryptographic_adapter_bound",
    "signature_payload_replayed",
    "request_trace_replayed",
    "nonhost_retention_replayed",
    "sealed_public_parity_replayed",
    "duplicate_counterparty_checked",
    "duplicate_dependency_group_checked",
    "duplicate_receipt_class_checked",
    "supersession_checked",
    "challenge_rollback_checked",
    "failed_gate_summary_ready",
    "no_manual_override",
    "computed_floor_engine_required",
    "private_material_not_in_public_release",
]


REQUIRED_QUORUM_PARTICIPATION_CHECKS = [
    "floor_activation_exists_and_eligible",
    "activation_bound_to_import_gate",
    "activation_has_no_direct_floor_effect",
    "readiness_replay_already_satisfied",
    "cryptographic_adapter_bound",
    "duplicate_counterparty_rechecked",
    "duplicate_dependency_group_rechecked",
    "duplicate_issuer_key_rechecked",
    "duplicate_receipt_class_rechecked",
    "supersession_rechecked",
    "challenge_rollback_rechecked",
    "failed_gate_summary_ready",
    "no_manual_quorum_override",
    "single_class_quorum_blocked",
    "full_vector_recompute_required",
    "private_material_not_in_public_release",
]


@dataclass(frozen=True)
class LiveFloorCandidate:
    gate_id: str
    receipt_class: str
    adapter_ref: str
    quorum_participation_ref: str
    dependency_group_id: str
    counterparty_org_id: str
    issuer_key_id: str
    subject_host_org_id: str

    def as_register_row(self, status: str, reason: str) -> dict:
        return {
            "source_ref": self.gate_id,
            "receipt_class": self.receipt_class,
            "quorum_participation_ref": self.quorum_participation_ref,
            "dependency_group_id": self.dependency_group_id,
            "counterparty_org_id": self.counterparty_org_id,
            "issuer_key_id": self.issuer_key_id,
            "subject_host_org_id": self.subject_host_org_id,
            "status": status,
            "reason": reason,
        }


def _truthy_checks(gate_checks: dict, required: Sequence[str]) -> bool:
    return all(gate_checks.get(key) is True for key in required)


def _independence_failure(independence: dict, provenance: dict) -> Optional[str]:
    """Return a human-readable failure if a verified adapter is correlated."""
    required = [
        "counterparty_org_id",
        "issuer_key_id",
        "dependency_group_id",
        "subject_host_org_id",
        "counterparty_distinct_from_subject_host",
        "issuer_distinct_from_subject_host",
        "correlation_discount",
    ]
    missing = [key for key in required if key not in independence]
    if missing:
        return "cryptographic adapter independence fields missing: " + ", ".join(missing)
    if independence.get("dependency_group_id") != provenance.get("dependency_group"):
        return "cryptographic adapter dependency group does not match source provenance"
    if independence.get("counterparty_distinct_from_subject_host") is not True:
        return "counterparty is not distinct from subject host"
    if independence.get("issuer_distinct_from_subject_host") is not True:
        return "issuer key is not distinct from subject host"
    if independence.get("correlation_discount") != "none":
        return f"cryptographic adapter carries correlation_discount={independence.get('correlation_discount')}"
    if independence.get("counterparty_org_id") == independence.get("subject_host_org_id"):
        return "counterparty_org_id equals subject_host_org_id"
    if independence.get("issuer_key_id") == independence.get("subject_host_org_id"):
        return "issuer_key_id equals subject_host_org_id"
    return None


def _readiness_failure(readiness: Optional[dict], gate: dict, receipt_class: str) -> Optional[str]:
    if readiness is None:
        return "linked import readiness gate was not found for replay"
    readiness_id = readiness.get("import_readiness_gate_id")
    readiness_ref = gate.get("linked_import_readiness_gate_ref")
    provenance = gate.get("source_provenance", {})
    if readiness_id != readiness_ref:
        return "linked import readiness gate id mismatch"
    if readiness.get("gate_state") != "eligible-for-import-gate":
        return f"linked import readiness gate state is {readiness.get('gate_state')}"
    if readiness.get("requested_receipt_class") != receipt_class:
        return "linked import readiness gate receipt class mismatch"
    if gate.get("source_intake_record_ref") != readiness.get("linked_intake_record_ref"):
        return "source intake record does not match linked import readiness gate"
    if gate.get("source_response_record_ref") != readiness.get("linked_response_record_ref"):
        return "source response record does not match linked import readiness gate"
    if provenance.get("custody_record_ref") != readiness.get("linked_custody_record_ref"):
        return "custody record ref does not match linked import readiness gate"
    if provenance.get("linked_live_evidence_acquisition_packet_ref") != readiness.get("linked_live_evidence_acquisition_packet_ref"):
        return "LEAP ref does not match linked import readiness gate"
    locks = readiness.get("downstream_locks", {})
    decision = readiness.get("decision", {})
    if locks.get("may_prepare_actual_receipt_import_gate") is not True:
        return "linked import readiness gate does not authorize import-gate preparation"
    if locks.get("may_increment_live_floor") is not False or locks.get("live_floor_delta_allowed") is not False:
        return "linked import readiness gate attempts to unlock floor credit"
    if decision.get("actual_import_gate_may_be_prepared") is not True or decision.get("can_increment_live_floor") is not False:
        return "linked import readiness gate decision is not preparation-only"
    if readiness.get("no_live_floor_effect") is not True:
        return "linked import readiness gate lacks no_live_floor_effect"
    return None


def _activation_failure(activation: Optional[dict], gate: dict, receipt_class: str, adapter_ref: str) -> Optional[str]:
    gate_id = gate.get("import_gate_id")
    if activation is None:
        return "live receipt floor activation record missing for import gate"
    if activation.get("activation_state") != "eligible-for-floor-recompute":
        return f"floor activation state is {activation.get('activation_state')}"
    if activation.get("linked_import_gate_ref") != gate_id:
        return "floor activation record is not bound to this import gate"
    if activation.get("linked_import_readiness_gate_ref") != gate.get("linked_import_readiness_gate_ref"):
        return "floor activation readiness ref mismatch"
    if activation.get("linked_cryptographic_verifier_adapter_ref") != adapter_ref:
        return "floor activation verifier-adapter ref mismatch"
    if activation.get("requested_receipt_class") != receipt_class:
        return "floor activation receipt class mismatch"
    replay = activation.get("replay_checks", {})
    missing = [key for key in REQUIRED_ACTIVATION_REPLAY_CHECKS if replay.get(key) is not True]
    if missing:
        return "floor activation replay checks missing: " + ", ".join(missing)
    locks = activation.get("floor_recompute_locks", {})
    if locks.get("may_enter_computed_floor_candidate_set") is not True:
        return "floor activation does not admit candidate to computed-floor evaluation"
    if locks.get("manual_floor_increment_allowed") is not False:
        return "floor activation allows manual floor increment"
    if locks.get("computed_floor_recompute_required") is not True:
        return "floor activation does not require computed-floor recomputation"
    if locks.get("activation_record_can_satisfy_quorum_by_itself") is not False:
        return "floor activation claims quorum effect by itself"
    if locks.get("live_floor_delta_allowed_by_activation_record") is not False:
        return "floor activation claims direct live-floor delta"
    decision = activation.get("decision", {})
    if decision.get("may_enter_computed_floor_candidate_set") is not True:
        return "floor activation decision does not admit candidate"
    if decision.get("can_increment_live_floor_by_itself") is not False:
        return "floor activation decision increments floor by itself"
    if decision.get("live_reliance_effect") != "stayed-until-computed-floor":
        return "floor activation reliance effect is not stayed until computed-floor recomputation"
    if activation.get("no_live_floor_effect") is not True:
        return "floor activation lacks no_live_floor_effect"
    return None




def _quorum_participation_failure(participation: Optional[dict], gate: dict, activation: dict, receipt_class: str, adapter_ref: str) -> Optional[str]:
    gate_id = gate.get("import_gate_id")
    activation_id = activation.get("activation_record_id")
    if participation is None:
        return "live receipt quorum participation record missing for import gate"
    if participation.get("participation_state") != "eligible-for-independence-discount":
        return f"quorum participation state is {participation.get('participation_state')}"
    if participation.get("linked_import_gate_ref") != gate_id:
        return "quorum participation record is not bound to this import gate"
    if participation.get("linked_floor_activation_record_ref") != activation_id:
        return "quorum participation activation ref mismatch"
    if participation.get("linked_import_readiness_gate_ref") != gate.get("linked_import_readiness_gate_ref"):
        return "quorum participation readiness ref mismatch"
    if participation.get("linked_cryptographic_verifier_adapter_ref") != adapter_ref:
        return "quorum participation verifier-adapter ref mismatch"
    if participation.get("requested_receipt_class") != receipt_class:
        return "quorum participation receipt class mismatch"
    replay = participation.get("quorum_replay_checks", {})
    missing = [key for key in REQUIRED_QUORUM_PARTICIPATION_CHECKS if replay.get(key) is not True]
    if missing:
        return "quorum participation replay checks missing: " + ", ".join(missing)
    locks = participation.get("quorum_locks", {})
    if locks.get("may_enter_independence_discount") is not True:
        return "quorum participation does not admit candidate to independence discount"
    if locks.get("manual_live_floor_update_allowed") is not False:
        return "quorum participation allows manual live-floor update"
    if locks.get("may_satisfy_cross_critical_quorum_by_itself") is not False:
        return "quorum participation claims cross-critical quorum by itself"
    if locks.get("live_floor_delta_allowed_by_participation_record") is not False:
        return "quorum participation claims direct live-floor delta"
    if locks.get("computed_floor_recompute_required") is not True:
        return "quorum participation does not require computed-floor recomputation"
    decision = participation.get("decision", {})
    if decision.get("may_enter_independence_discount") is not True:
        return "quorum participation decision does not admit candidate"
    if decision.get("can_upgrade_reliance_by_itself") is not False:
        return "quorum participation claims reliance upgrade by itself"
    if decision.get("live_reliance_effect") != "stayed-until-computed-floor":
        return "quorum participation reliance effect is not stayed until computed-floor recomputation"
    if participation.get("no_live_floor_effect") is not True:
        return "quorum participation lacks no_live_floor_effect"
    return None


def eligible_import_gate(
    data: dict,
    *,
    root: Path,
    challenged_gate_ids: Optional[set] = None,
    verified_live_adapters: Optional[Dict[str, dict]] = None,
    import_readiness_gates: Optional[Dict[str, dict]] = None,
    activation_records: Optional[Dict[str, dict]] = None,
    quorum_participation_records: Optional[Dict[str, dict]] = None,
) -> Tuple[bool, str, Optional[LiveFloorCandidate]]:
    """Return (eligible, reason, candidate) for a single import gate.

    The gate must pass strict live-counterparty requirements and produce a
    candidate; the caller still applies global independence/correlation discount
    across the whole candidate set before counting any live-floor delta.
    """
    challenged_gate_ids = challenged_gate_ids or set()
    verified_live_adapters = verified_live_adapters or {}
    import_readiness_gates = import_readiness_gates or {}
    activation_records = activation_records or {}
    quorum_participation_records = quorum_participation_records or {}
    gate_id = data.get("import_gate_id", "unknown")
    decision = data.get("import_decision", {})
    prov = data.get("source_provenance", {})
    checks = data.get("gate_checks", {})
    receipt_class = decision.get("imported_receipt_class") or data.get("receipt_class") or "unknown"

    if gate_id in challenged_gate_ids:
        return False, "linked import gate has pending/upheld challenge or rollback", None
    if data.get("import_mode") != "actual-live-import":
        return False, f"import_mode={data.get('import_mode')} is not actual-live-import", None
    if decision.get("import_allowed_to_live_floor") is not True or decision.get("live_floor_delta", 0) <= 0:
        return False, "import decision does not allow positive live-floor delta", None
    if prov.get("collection_context") != "live-counterparty":
        return False, f"collection_context={prov.get('collection_context')} is not live-counterparty", None
    if prov.get("counterparty_external") is not True:
        return False, "counterparty_external is not true", None
    if prov.get("nonhost_retention") is not True:
        return False, "nonhost_retention is not true", None
    if prov.get("sealed_public_parity") is not True:
        return False, "sealed_public_parity is not true", None
    if prov.get("provenance_disqualifiers"):
        return False, "provenance_disqualifiers are present", None
    readiness_ref = data.get("linked_import_readiness_gate_ref")
    if not readiness_ref:
        return False, "actual-live-import lacks linked_import_readiness_gate_ref", None
    if checks.get("linked_import_readiness_gate_verified") is not True:
        return False, "linked import readiness gate has not been verified", None
    readiness_failure = _readiness_failure(import_readiness_gates.get(readiness_ref), data, receipt_class)
    if readiness_failure:
        return False, readiness_failure, None

    adapter_ref = data.get("cryptographic_verifier_adapter_ref")
    if not adapter_ref:
        return False, "actual-live-import lacks cryptographic_verifier_adapter_ref", None
    adapter = verified_live_adapters.get(gate_id)
    if adapter is None:
        return False, "no verified live cryptographic adapter bound to import gate", None
    adapter_rel = adapter["path"].relative_to(root).as_posix()
    if adapter_ref != adapter_rel:
        return False, f"cryptographic adapter ref mismatch: gate={adapter_ref} verified={adapter_rel}", None

    activation = activation_records.get(gate_id)
    activation_failure = _activation_failure(activation, data, receipt_class, adapter_ref)
    if activation_failure:
        return False, activation_failure, None

    quorum_failure = _quorum_participation_failure(quorum_participation_records.get(gate_id), data, activation or {}, receipt_class, adapter_ref)
    if quorum_failure:
        return False, quorum_failure, None

    payload = adapter["record"].get("payload", {})
    independence = adapter["record"].get("independence", {})
    if payload.get("receipt_class") != receipt_class:
        return False, "cryptographic adapter receipt class does not match import decision", None
    failure = _independence_failure(independence, prov)
    if failure:
        return False, failure, None

    if not _truthy_checks(checks, REQUIRED_GATE_CHECKS):
        failed = [key for key in REQUIRED_GATE_CHECKS if checks.get(key) is not True]
        return False, "missing required gate checks: " + ", ".join(failed), None

    candidate = LiveFloorCandidate(
        gate_id=gate_id,
        receipt_class=receipt_class,
        adapter_ref=adapter_ref,
        quorum_participation_ref=quorum_participation_records[gate_id].get("quorum_participation_record_id", ""),
        dependency_group_id=independence.get("dependency_group_id", ""),
        counterparty_org_id=independence.get("counterparty_org_id", ""),
        issuer_key_id=independence.get("issuer_key_id", ""),
        subject_host_org_id=independence.get("subject_host_org_id", ""),
    )
    return True, "passed strict live-counterparty import gate with verified readiness replay, floor activation, quorum participation replay, cryptographic adapter, and no direct host-correlation", candidate


def apply_independence_discount(candidates: Iterable[LiveFloorCandidate]) -> Tuple[List[LiveFloorCandidate], List[dict]]:
    """Discount correlated candidates across dependency group, counterparty, issuer key, and class.

    The floor is intentionally conservative: for cross-critical reliance, each
    counted live receipt must have its own dependency group, counterparty org,
    issuer key, and receipt class. Multiple true statements from the same org,
    issuer, dependency group, or class are useful evidence but not independent
    floor increments.
    """
    counted: List[LiveFloorCandidate] = []
    register: List[dict] = []
    seen_dependency_groups = set()
    seen_counterparties = set()
    seen_issuer_keys = set()
    seen_classes = set()
    class_rank = {name: idx for idx, name in enumerate(REQUIRED_CLASSES)}
    ordered = sorted(candidates, key=lambda c: (class_rank.get(c.receipt_class, 10_000), c.gate_id))
    for cand in ordered:
        if cand.dependency_group_id in seen_dependency_groups:
            reason = f"discounted: dependency_group_id {cand.dependency_group_id} already counted"
            register.append(cand.as_register_row("discounted", reason))
            continue
        if cand.counterparty_org_id in seen_counterparties:
            reason = f"discounted: counterparty_org_id {cand.counterparty_org_id} already counted"
            register.append(cand.as_register_row("discounted", reason))
            continue
        if cand.issuer_key_id in seen_issuer_keys:
            reason = f"discounted: issuer_key_id {cand.issuer_key_id} already counted"
            register.append(cand.as_register_row("discounted", reason))
            continue
        if cand.receipt_class in seen_classes:
            reason = f"discounted: receipt_class {cand.receipt_class} already satisfied by another independent candidate"
            register.append(cand.as_register_row("discounted", reason))
            continue
        seen_dependency_groups.add(cand.dependency_group_id)
        seen_counterparties.add(cand.counterparty_org_id)
        seen_issuer_keys.add(cand.issuer_key_id)
        seen_classes.add(cand.receipt_class)
        register.append(cand.as_register_row("counted", "counted as one class-local independent live receipt after readiness, activation, quorum-participation, verifier, and correlation discount"))
        counted.append(cand)
    return counted, register
