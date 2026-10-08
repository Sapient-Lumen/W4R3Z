#!/usr/bin/env python3
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-18T08:27:00Z"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _schema_has_actual_ref_condition(schema_rel, state_field, state_value, required_refs):
    schema = load(ROOT / schema_rel)
    for block in schema.get("allOf", []):
        if block.get("if", {}).get("properties", {}).get(state_field, {}).get("const") == state_value:
            then = block.get("then", {})
            required = set(then.get("required", []))
            nested_required = set()
            for prop_schema in then.get("properties", {}).values():
                nested_required.update(prop_schema.get("required", []))
            if set(required_refs) <= required | nested_required:
                return True
    return False


def _schema_has_enum_state_required(schema_rel, state_field, state_value, required_refs):
    schema = load(ROOT / schema_rel)
    for block in schema.get("allOf", []):
        state_schema = block.get("if", {}).get("properties", {}).get(state_field, {})
        enum_values = state_schema.get("enum", [])
        if state_value in enum_values:
            then = block.get("then", {})
            required = set(then.get("required", []))
            nested_required = set()
            for prop_schema in then.get("properties", {}).values():
                nested_required.update(prop_schema.get("required", []))
            if set(required_refs) <= required | nested_required:
                return True
    return False


def _schema_requires_response_gate_for_intake_candidate():
    schema = load(ROOT / "schemas/external-receipt-response-record.schema.json")
    for block in schema.get("allOf", []):
        if_schema = block.get("if", {})
        props = if_schema.get("properties", {})
        if props.get("response_state", {}).get("const") == "actual-response-received":
            vr = props.get("verification_result", {}).get("properties", {})
            if vr.get("can_generate_actual_intake", {}).get("const") is True:
                if "linked_response_verification_gate_ref" in set(block.get("then", {}).get("required", [])):
                    return True
    return False


def _schema_requires_intake_conversion_gate_for_response_intake_ref():
    schema = load(ROOT / "schemas/external-receipt-response-record.schema.json")
    if "linked_intake_conversion_gate_ref" not in schema.get("properties", {}):
        return False
    for block in schema.get("allOf", []):
        if block.get("if", {}).get("properties", {}).get("resulting_intake_record_ref", {}).get("type") == "string":
            if "linked_intake_conversion_gate_ref" in set(block.get("then", {}).get("required", [])):
                return True
    return False


def _schema_requires_intake_conversion_gate_for_lineaged_intake():
    schema = load(ROOT / "schemas/external-receipt-intake-record.schema.json")
    if "linked_intake_conversion_gate_ref" not in schema.get("properties", {}):
        return False
    for block in schema.get("allOf", []):
        if block.get("description") == "lineaged actual-external intake records require an intake conversion gate reference":
            if "linked_intake_conversion_gate_ref" in set(block.get("then", {}).get("required", [])):
                return True
    return False


def _compute_floor():
    spec = importlib.util.spec_from_file_location("compute_live_receipt_floor", ROOT / "tools" / "compute_live_receipt_floor.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compute(root=ROOT, rev=REV, created_at=CREATED_AT)


def _json_examples(prefix):
    return sorted((ROOT / "examples").glob(prefix))


def build():
    drop_paths = _json_examples("live-evidence-drop-ledger*.json")
    leap_paths = _json_examples("live-evidence-acquisition-packet*.json")
    challenge_paths = _json_examples("live-artifact-candidate-challenge-report*.json")
    custody_disposition_paths = _json_examples("candidate-challenge-disposition-record*.json")
    authority_binder_paths = _json_examples("custody-authority-evidence-binder*.json")
    custody_gate_paths = _json_examples("counterparty-artifact-custody-gate*.json")
    custody_paths = _json_examples("counterparty-artifact-custody-record*.json")
    response_gate_paths = _json_examples("external-receipt-response-verification-gate*.json")
    response_paths = _json_examples("external-receipt-response-record*.json")
    intake_conversion_gate_paths = _json_examples("external-receipt-intake-conversion-gate*.json")
    intake_paths = _json_examples("external-receipt-intake-record*.json")
    import_readiness_gate_paths = _json_examples("external-receipt-import-readiness-gate*.json")
    activation_record_paths = _json_examples("live-receipt-floor-activation-record*.json")
    quorum_participation_record_paths = _json_examples("live-receipt-quorum-participation-record*.json")
    floor_recompute_receipt_paths = _json_examples("live-receipt-floor-recompute-receipt*.json")
    publication_rollback_paths = _json_examples("live-receipt-publication-rollback-adjudication*.json")
    late_change_ingress_paths = _json_examples("live-receipt-late-change-ingress-record*.json")
    late_change_notice_dispatch_paths = _json_examples("live-receipt-late-change-notice-dispatch-record*.json")
    late_change_remedy_resolution_paths = _json_examples("live-receipt-late-change-remedy-resolution-record*.json")
    late_change_remedy_execution_paths = _json_examples("live-receipt-late-change-remedy-execution-record*.json")
    envelope_paths = _json_examples("nonhost-response-artifact-envelope*.json")
    import_gate_paths = _json_examples("actual-receipt-import-gate*.json")
    floor = _compute_floor()

    drop_records = [load(p) for p in drop_paths]
    leap_records = [load(p) for p in leap_paths]
    challenge_records = [load(p) for p in challenge_paths]
    custody_disposition_records = [load(p) for p in custody_disposition_paths]
    authority_binder_records = [load(p) for p in authority_binder_paths]
    custody_gate_records = [load(p) for p in custody_gate_paths]
    custody_records = [load(p) for p in custody_paths]
    response_gate_records = [load(p) for p in response_gate_paths]
    response_records = [load(p) for p in response_paths]
    intake_conversion_gate_records = [load(p) for p in intake_conversion_gate_paths]
    intake_records = [load(p) for p in intake_paths]
    import_readiness_gate_records = [load(p) for p in import_readiness_gate_paths]
    activation_records = [load(p) for p in activation_record_paths]
    quorum_participation_records = [load(p) for p in quorum_participation_record_paths]
    floor_recompute_receipt_records = [load(p) for p in floor_recompute_receipt_paths]
    publication_rollback_records = [load(p) for p in publication_rollback_paths]
    late_change_ingress_records = [load(p) for p in late_change_ingress_paths]
    late_change_notice_dispatch_records = [load(p) for p in late_change_notice_dispatch_paths]
    late_change_remedy_resolution_records = [load(p) for p in late_change_remedy_resolution_paths]
    late_change_remedy_execution_records = [load(p) for p in late_change_remedy_execution_paths]
    envelope_records = [load(p) for p in envelope_paths]
    import_records = [load(p) for p in import_gate_paths]

    live_candidate_drops = [r for r in drop_records if r.get("intake_mode") == "live-candidate-drop"]
    quarantined_drops = [r for r in drop_records if r.get("intake_mode") == "quarantine-control"]
    rejected_drops = [r for r in drop_records if r.get("intake_mode") == "rejected"]
    drop_lineage_ok = all(
        r.get("no_live_floor_effect") is True
        and r.get("classification", {}).get("can_create_response_record") is False
        and r.get("mandatory_blocks", {}).get("downstream_objects_blocked") is True
        and r.get("mandatory_blocks", {}).get("live_floor_delta_blocked") is True
        for r in drop_records
    )

    actual_leap_admitted = [r for r in leap_records if r.get("state") == "admitted-to-custody"]
    actual_leap_candidates = [r for r in leap_records if r.get("state") == "candidate-artifact-received"]
    candidate_challenges = [r for r in challenge_records if r.get("candidate_state") == "hash-reverified-challenge-pending"]
    pending_challenges = [r for r in candidate_challenges if r.get("challenge_window", {}).get("status") == "open"]
    custody_dispositions = [r for r in custody_disposition_records if r.get("schema_version") == "candidate-challenge-disposition-record-v0.1"]
    gate_consumable_dispositions = [r for r in custody_dispositions if r.get("decision", {}).get("may_feed_custody_authority_gate") is True]
    open_stayed_dispositions = [r for r in custody_dispositions if r.get("disposition_state") == "challenge-open-stayed"]
    authority_binders = [r for r in authority_binder_records if r.get("schema_version") == "custody-authority-evidence-binder-v0.1"]
    gate_consumable_authority_binders = [r for r in authority_binders if r.get("decision", {}).get("may_feed_custody_authority_gate") is True]
    predispatch_authority_binders = [r for r in authority_binders if r.get("binder_state") == "pre-dispatch-no-authority"]
    custody_gates = [r for r in custody_gate_records if r.get("schema_version") == "counterparty-artifact-custody-gate-v0.1"]
    eligible_custody_gates = [r for r in custody_gates if r.get("gate_state") == "eligible-for-custody-record" and r.get("authority_evidence_binder", {}).get("may_feed_custody_authority_gate") is True]
    blocked_custody_gates = [r for r in custody_gates if r.get("gate_state", "").startswith("blocked-")]
    live_custody = [r for r in custody_records if r.get("artifact_state") == "live-candidate-artifact"]
    response_gates = [r for r in response_gate_records if r.get("schema_version") == "external-receipt-response-verification-gate-v0.1"]
    eligible_response_gates = [r for r in response_gates if r.get("gate_state") == "eligible-for-response-record"]
    actual_shaped_responses = [r for r in response_records if r.get("response_state") == "actual-response-received"]
    intake_conversion_gates = [r for r in intake_conversion_gate_records if r.get("schema_version") == "external-receipt-intake-conversion-gate-v0.1"]
    eligible_intake_conversion_gates = [r for r in intake_conversion_gates if r.get("gate_state") == "eligible-for-intake-record"]
    actual_shaped_intakes = [r for r in intake_records if r.get("receipt_state") == "actual-external"]
    import_readiness_gates = [r for r in import_readiness_gate_records if r.get("schema_version") == "external-receipt-import-readiness-gate-v0.1"]
    eligible_import_readiness_gates = [r for r in import_readiness_gates if r.get("gate_state") == "eligible-for-import-gate"]
    floor_activation_records = [r for r in activation_records if r.get("schema_version") == "live-receipt-floor-activation-record-v0.1"]
    eligible_floor_activation_records = [r for r in floor_activation_records if r.get("activation_state") == "eligible-for-floor-recompute"]
    quorum_participation_records = [r for r in quorum_participation_records if r.get("schema_version") == "live-receipt-quorum-participation-record-v0.1"]
    eligible_quorum_participation_records = [r for r in quorum_participation_records if r.get("participation_state") == "eligible-for-independence-discount"]
    floor_recompute_receipts = [r for r in floor_recompute_receipt_records if r.get("schema_version") == "live-receipt-floor-recompute-receipt-v0.1"]
    eligible_floor_recompute_receipts = [r for r in floor_recompute_receipts if str(r.get("decision", {}).get("floor_publication_state", "")).startswith("eligible-")]
    publication_rollback_adjudications = [r for r in publication_rollback_records if r.get("schema_version") == "live-receipt-publication-rollback-adjudication-v0.1"]
    eligible_publication_rollback_adjudications = [r for r in publication_rollback_adjudications if str(r.get("decision", {}).get("publication_adjudication_state", "")).startswith("eligible-")]
    late_change_ingresses = [r for r in late_change_ingress_records if r.get("schema_version") == "live-receipt-late-change-ingress-v0.1"]
    opened_late_change_ingresses = [r for r in late_change_ingresses if r.get("decision", {}).get("late_change_state") != "monitoring-no-signal"]
    late_change_notice_dispatches = [r for r in late_change_notice_dispatch_records if r.get("schema_version") == "live-receipt-late-change-notice-dispatch-v0.1"]
    live_late_change_notice_dispatches = [r for r in late_change_notice_dispatches if r.get("notice_context", {}).get("live_late_signal_present") is True]
    ready_late_change_notice_dispatches = [r for r in late_change_notice_dispatches if r.get("decision", {}).get("notice_dispatch_state") == "dispatch-ready-publication-stayed"]
    late_change_remedy_resolutions = [r for r in late_change_remedy_resolution_records if r.get("schema_version") == "live-receipt-late-change-remedy-resolution-v0.1"]
    live_late_change_remedy_resolutions = [r for r in late_change_remedy_resolutions if r.get("remedy_context", {}).get("live_late_signal_present") is True]
    ready_late_change_remedy_resolutions = [r for r in late_change_remedy_resolutions if r.get("decision", {}).get("remedy_resolution_state") == "resolution-ready-publication-stayed"]
    late_change_remedy_executions = [r for r in late_change_remedy_execution_records if r.get("schema_version") == "live-receipt-late-change-remedy-execution-v0.1"]
    live_late_change_remedy_executions = [r for r in late_change_remedy_executions if r.get("execution_context", {}).get("live_late_signal_present") is True]
    ready_late_change_remedy_executions = [r for r in late_change_remedy_executions if r.get("decision", {}).get("remedy_execution_state") == "execution-ready-publication-stayed"]
    live_envelopes = [r for r in envelope_records if r.get("artifact_mode") == "live-counterparty"]
    actual_imports = [r for r in import_records if r.get("import_mode") == "actual-live-import"]

    drop_ids = {r.get("ledger_id") for r in drop_records}
    leap_drop_ref_ok = all(r.get("source_evidence_drop_ledger_ref") in drop_ids for r in actual_leap_candidates + actual_leap_admitted)

    def _has_response_lineage(record):
        return bool(record.get("linked_live_evidence_acquisition_packet_ref") and record.get("linked_custody_record_ref"))

    def _has_response_gate_ref(record):
        ref = record.get("linked_response_verification_gate_ref")
        return bool(ref and (ref.startswith("ERVG-") or ref.startswith("controlled-fixture:")))

    def _has_intake_conversion_gate_ref(record):
        ref = record.get("linked_intake_conversion_gate_ref")
        return bool(ref and (ref.startswith("ERICG-") or ref.startswith("controlled-fixture:")))

    def _has_import_readiness_gate_ref(record):
        ref = record.get("linked_import_readiness_gate_ref")
        return bool(ref and ref.startswith("ERIRG-"))

    def _has_intake_lineage(record):
        return bool(record.get("linked_live_evidence_acquisition_packet_ref") and record.get("linked_custody_record_ref"))

    def _response_is_quarantined_fixture(record):
        quorum = record.get("quorum_effect", {})
        return (
            record.get("response_state") == "actual-response-received"
            and quorum.get("can_increment_independent_receipts_present") is False
            and quorum.get("live_weight") == 0
            and quorum.get("dry_run_weight", 0) > 0
        )

    def _intake_is_quarantined_fixture(record):
        decision = record.get("reliance_decision", {})
        return (
            record.get("receipt_state") == "actual-external"
            and decision.get("can_satisfy_quorum") is False
            and decision.get("reliance_effect") in {"conditional", "stayed", "blocked"}
        )

    actual_responses = [r for r in actual_shaped_responses if _has_response_lineage(r)]
    actual_intakes = [r for r in actual_shaped_intakes if _has_intake_lineage(r)]
    quarantined_actual_responses = [r for r in actual_shaped_responses if not _has_response_lineage(r) and _response_is_quarantined_fixture(r)]
    quarantined_actual_intakes = [r for r in actual_shaped_intakes if not _has_intake_lineage(r) and _intake_is_quarantined_fixture(r)]
    unlineaged_actual_responses = [r for r in actual_shaped_responses if not _has_response_lineage(r) and r not in quarantined_actual_responses]
    unlineaged_actual_intakes = [r for r in actual_shaped_intakes if not _has_intake_lineage(r) and r not in quarantined_actual_intakes]

    response_ref_ok = not unlineaged_actual_responses
    intake_ref_ok = not unlineaged_actual_intakes
    envelope_ref_ok = all(r.get("linked_live_evidence_acquisition_packet_ref") and r.get("linked_custody_record") for r in live_envelopes)
    import_ref_ok = all(r.get("source_provenance", {}).get("linked_live_evidence_acquisition_packet_ref") and r.get("source_provenance", {}).get("custody_record_ref") and _has_import_readiness_gate_ref(r) and r.get("gate_checks", {}).get("linked_import_readiness_gate_verified") is True for r in actual_imports)

    response_to_intake_gate_ok = all(
        not r.get("resulting_intake_record_ref") or _has_intake_conversion_gate_ref(r)
        for r in response_records
    )
    lineaged_intake_conversion_ref_ok = all(_has_intake_conversion_gate_ref(r) for r in actual_intakes)

    schema_conditions = {
        "leap_drop_ref": _schema_has_enum_state_required("schemas/live-evidence-acquisition-packet.schema.json", "state", "candidate-artifact-received", ["source_evidence_drop_ledger_ref"]),
        "custody_authority_evidence_binder_schema": (ROOT / "schemas" / "custody-authority-evidence-binder.schema.json").exists(),
        "custody_gate_schema": (ROOT / "schemas" / "counterparty-artifact-custody-gate.schema.json").exists(),
        "response_gate_schema": (ROOT / "schemas" / "external-receipt-response-verification-gate.schema.json").exists(),
        "intake_conversion_gate_schema": (ROOT / "schemas" / "external-receipt-intake-conversion-gate.schema.json").exists(),
        "import_readiness_gate_schema": (ROOT / "schemas" / "external-receipt-import-readiness-gate.schema.json").exists(),
        "floor_activation_schema": (ROOT / "schemas" / "live-receipt-floor-activation-record.schema.json").exists(),
        "quorum_participation_schema": (ROOT / "schemas" / "live-receipt-quorum-participation-record.schema.json").exists(),
        "floor_recompute_receipt_schema": (ROOT / "schemas" / "live-receipt-floor-recompute-receipt.schema.json").exists(),
        "publication_rollback_adjudication_schema": (ROOT / "schemas" / "live-receipt-publication-rollback-adjudication.schema.json").exists(),
        "late_change_ingress_schema": (ROOT / "schemas" / "live-receipt-late-change-ingress-record.schema.json").exists(),
        "late_change_notice_dispatch_schema": (ROOT / "schemas" / "live-receipt-late-change-notice-dispatch-record.schema.json").exists(),
        "late_change_remedy_resolution_schema": (ROOT / "schemas" / "live-receipt-late-change-remedy-resolution-record.schema.json").exists(),
        "late_change_remedy_execution_schema": (ROOT / "schemas" / "live-receipt-late-change-remedy-execution-record.schema.json").exists(),
        "response_gate_required_for_intake_candidate": _schema_requires_response_gate_for_intake_candidate(),
        "intake_conversion_gate_required_for_response_intake_ref": _schema_requires_intake_conversion_gate_for_response_intake_ref(),
        "intake_conversion_gate_required_for_lineaged_intake": _schema_requires_intake_conversion_gate_for_lineaged_intake(),
        "response": _schema_has_actual_ref_condition("schemas/external-receipt-response-record.schema.json", "response_state", "actual-response-received", ["linked_live_evidence_acquisition_packet_ref", "linked_custody_record_ref"]),
        "intake": _schema_has_actual_ref_condition("schemas/external-receipt-intake-record.schema.json", "receipt_state", "actual-external", ["linked_live_evidence_acquisition_packet_ref", "linked_custody_record_ref"]),
        "envelope": _schema_has_actual_ref_condition("schemas/nonhost-response-artifact-envelope.schema.json", "artifact_mode", "live-counterparty", ["linked_live_evidence_acquisition_packet_ref", "linked_custody_record"]),
        "import_gate": _schema_has_actual_ref_condition("schemas/actual-receipt-import-gate.schema.json", "import_mode", "actual-live-import", ["linked_live_evidence_acquisition_packet_ref", "custody_record_ref", "linked_import_readiness_gate_ref", "linked_import_readiness_gate_verified"]),
    }

    dryrun_custody_nonlive = all(
        r.get("artifact_state") != "institutional-dry-run-artifact" or (
            r.get("import_readiness", {}).get("live_import_floor_delta") == 0
            and all(a.get("may_be_used_for_live_import") is False for a in r.get("raw_artifacts", []))
        ) for r in custody_records
    )
    custody_gate_authority_binder_ok = all(
        r.get("gate_state") != "eligible-for-custody-record" or (
            r.get("authority_evidence_binder", {}).get("may_feed_custody_authority_gate") is True
            and r.get("authority_evidence_binder", {}).get("authority_evidence_complete") is True
        ) for r in custody_gates
    )

    custody_response_only_ok = all(
        r.get("artifact_state") != "live-candidate-artifact" or (
            bool(r.get("linked_custody_gate_ref"))
            and r.get("import_readiness", {}).get("may_create_response_record") is True
            and r.get("import_readiness", {}).get("may_create_intake_record") is False
            and r.get("import_readiness", {}).get("may_run_import_gate") is False
            and r.get("import_readiness", {}).get("live_import_floor_delta") == 0
            and r.get("decision", {}).get("live_reliance_effect") == "stayed"
        ) for r in custody_records
    )
    response_gate_lock_ok = all(
        r.get("no_live_floor_effect") is True
        and r.get("downstream_locks", {}).get("may_create_intake_record") is False
        and r.get("downstream_locks", {}).get("may_run_import_gate") is False
        and r.get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and r.get("decision", {}).get("can_generate_actual_intake") is False
        for r in response_gates
    )
    intake_conversion_gate_lock_ok = all(
        r.get("no_live_floor_effect") is True
        and r.get("downstream_locks", {}).get("may_run_import_gate") is False
        and r.get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and r.get("decision", {}).get("can_run_import_gate") is False
        for r in intake_conversion_gates
    )
    intake_candidate_response_gate_ok = all(
        not (r.get("response_state") == "actual-response-received" and r.get("verification_result", {}).get("can_generate_actual_intake") is True) or _has_response_gate_ref(r)
        for r in response_records
    )
    import_readiness_gate_lock_ok = all(
        r.get("no_live_floor_effect") is True
        and r.get("downstream_locks", {}).get("may_increment_live_floor") is False
        and r.get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and r.get("decision", {}).get("can_increment_live_floor") is False
        for r in import_readiness_gates
    )
    floor_activation_lock_ok = all(
        r.get("no_live_floor_effect") is True
        and r.get("floor_recompute_locks", {}).get("manual_floor_increment_allowed") is False
        and r.get("floor_recompute_locks", {}).get("computed_floor_recompute_required") is True
        and r.get("floor_recompute_locks", {}).get("activation_record_can_satisfy_quorum_by_itself") is False
        and r.get("floor_recompute_locks", {}).get("live_floor_delta_allowed_by_activation_record") is False
        and r.get("decision", {}).get("can_increment_live_floor_by_itself") is False
        for r in floor_activation_records
    )
    quorum_participation_lock_ok = all(
        r.get("no_live_floor_effect") is True
        and r.get("quorum_locks", {}).get("may_enter_independence_discount") is (r.get("participation_state") == "eligible-for-independence-discount")
        and r.get("quorum_locks", {}).get("may_satisfy_cross_critical_quorum_by_itself") is False
        and r.get("quorum_locks", {}).get("manual_live_floor_update_allowed") is False
        and r.get("quorum_locks", {}).get("live_floor_delta_allowed_by_participation_record") is False
        and r.get("quorum_locks", {}).get("computed_floor_recompute_required") is True
        and r.get("decision", {}).get("can_upgrade_reliance_by_itself") is False
        for r in quorum_participation_records
    )

    floor_recompute_receipt_lock_ok = bool(floor_recompute_receipts) and all(
        r.get("no_direct_floor_effect") is True
        and r.get("publication_locks", {}).get("manual_live_floor_update_allowed") is False
        and r.get("publication_locks", {}).get("may_increment_live_floor_from_receipt") is False
        and r.get("publication_locks", {}).get("recompute_receipt_required_for_reliance_upgrade") is True
        and r.get("recompute_checks", {}).get("snapshot_matches_fresh_recompute") is True
        and r.get("recompute_checks", {}).get("no_manual_ledger_override") is True
        and r.get("recompute_checks", {}).get("no_stale_quorum_report") is True
        and r.get("decision", {}).get("may_upgrade_reliance") is (floor.get("computed_floor", {}).get("cross_critical_quorum_satisfied") is True)
        for r in floor_recompute_receipts
    )

    publication_rollback_lock_ok = bool(publication_rollback_adjudications) and all(
        r.get("no_direct_floor_effect") is True
        and r.get("publication_rollback_locks", {}).get("may_increment_live_floor_from_adjudication") is False
        and r.get("publication_rollback_locks", {}).get("manual_publication_override_allowed") is False
        and r.get("publication_rollback_locks", {}).get("recompute_receipt_required_after_late_change") is True
        and r.get("publication_rollback_locks", {}).get("late_challenge_reopens_publication") is True
        and r.get("adjudication_checks", {}).get("snapshot_hash_matches_recompute_receipt") is True
        and r.get("adjudication_checks", {}).get("manual_publication_override_absent") is True
        and r.get("decision", {}).get("may_upgrade_reliance") is (floor.get("computed_floor", {}).get("cross_critical_quorum_satisfied") is True)
        for r in publication_rollback_adjudications
    )
    late_change_ingress_lock_ok = bool(late_change_ingresses) and all(
        r.get("no_direct_floor_effect") is True
        and r.get("publication_freeze_locks", {}).get("may_continue_published_snapshot_from_ingress") is False
        and r.get("publication_freeze_locks", {}).get("may_continue_reliance_from_ingress") is False
        and r.get("publication_freeze_locks", {}).get("may_increment_live_floor_from_ingress") is False
        and r.get("publication_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and r.get("publication_freeze_locks", {}).get("must_rerun_publication_rollback_adjudication_if_signal_present") is True
        and r.get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and r.get("decision", {}).get("may_upgrade_reliance") is False
        for r in late_change_ingresses
    )

    late_change_notice_dispatch_lock_ok = bool(late_change_notice_dispatches) and all(
        r.get("no_direct_floor_effect") is True
        and r.get("notice_freeze_locks", {}).get("may_continue_published_snapshot_from_notice") is False
        and r.get("notice_freeze_locks", {}).get("may_continue_reliance_from_notice") is False
        and r.get("notice_freeze_locks", {}).get("may_increment_live_floor_from_notice") is False
        and r.get("notice_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and r.get("notice_freeze_locks", {}).get("notice_silence_counts_as_waiver") is False
        and r.get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and r.get("decision", {}).get("may_upgrade_reliance") is False
        for r in late_change_notice_dispatches
    )

    late_change_remedy_resolution_lock_ok = bool(late_change_remedy_resolutions) and all(
        r.get("no_direct_floor_effect") is True
        and r.get("resolution_freeze_locks", {}).get("may_continue_published_snapshot_from_resolution") is False
        and r.get("resolution_freeze_locks", {}).get("may_continue_reliance_from_resolution") is False
        and r.get("resolution_freeze_locks", {}).get("may_increment_live_floor_from_resolution") is False
        and r.get("resolution_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and r.get("resolution_freeze_locks", {}).get("remedy_silence_counts_as_waiver") is False
        and r.get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and r.get("decision", {}).get("may_upgrade_reliance") is False
        and r.get("decision", {}).get("may_increment_live_floor") is False
        for r in late_change_remedy_resolutions
    )
    late_change_remedy_execution_lock_ok = bool(late_change_remedy_executions) and all(
        r.get("no_direct_floor_effect") is True
        and r.get("execution_freeze_locks", {}).get("may_continue_published_snapshot_from_execution") is False
        and r.get("execution_freeze_locks", {}).get("may_continue_reliance_from_execution") is False
        and r.get("execution_freeze_locks", {}).get("may_increment_live_floor_from_execution") is False
        and r.get("execution_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and r.get("execution_freeze_locks", {}).get("execution_silence_counts_as_completion") is False
        and r.get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and r.get("decision", {}).get("may_upgrade_reliance") is False
        and r.get("decision", {}).get("may_increment_live_floor") is False
        for r in late_change_remedy_executions
    )

    activation_by_gate = {r.get("linked_import_gate_ref"): r for r in floor_activation_records if r.get("linked_import_gate_ref")}
    floor_activation_ref_ok = all(
        r.get("import_gate_id") in activation_by_gate
        and activation_by_gate[r.get("import_gate_id")].get("activation_state") == "eligible-for-floor-recompute"
        for r in actual_imports
    )
    quorum_by_gate = {r.get("linked_import_gate_ref"): r for r in quorum_participation_records if r.get("linked_import_gate_ref")}
    quorum_participation_ref_ok = all(
        r.get("import_gate_id") in quorum_by_gate
        and quorum_by_gate[r.get("import_gate_id")].get("participation_state") == "eligible-for-independence-discount"
        for r in actual_imports
    )
    downstream_blocked = (
        not live_candidate_drops and not actual_leap_admitted and not actual_leap_candidates and not gate_consumable_dispositions and not gate_consumable_authority_binders and not eligible_custody_gates and not live_custody and not eligible_response_gates and not eligible_intake_conversion_gates and not eligible_import_readiness_gates and not eligible_floor_activation_records and not eligible_quorum_participation_records
        and not actual_responses and not actual_intakes and not live_envelopes and not actual_imports
        and response_ref_ok and intake_ref_ok and drop_lineage_ok and leap_drop_ref_ok and custody_gate_authority_binder_ok and response_gate_lock_ok and intake_conversion_gate_lock_ok and import_readiness_gate_lock_ok and floor_activation_lock_ok and quorum_participation_lock_ok and floor_recompute_receipt_lock_ok and publication_rollback_lock_ok and late_change_ingress_lock_ok and late_change_notice_dispatch_lock_ok and late_change_remedy_resolution_lock_ok and late_change_remedy_execution_lock_ok and intake_candidate_response_gate_ok and response_to_intake_gate_ok and lineaged_intake_conversion_ref_ok
    )
    floor_n = floor.get("computed_floor", {}).get("independent_receipts_present", -1)
    checks = [
        {"check_id":"evidence-drop-quarantine-blocks-downstream","passed":drop_lineage_ok and not live_candidate_drops,"severity":"critical","observed":f"drop_ledgers={len(drop_records)} live_candidate_drops={len(live_candidate_drops)} quarantined_drops={len(quarantined_drops)} rejected_drops={len(rejected_drops)}","expected":"evidence drop ledgers stage raw payloads in quarantine only; no response/intake/import/live-floor action is allowed from the ledger alone","failure_effect":"stop before LEAP; route to failed-gate public summary or manual review"},
        {"check_id":"schema-conditionals-present","passed":all(schema_conditions.values()),"severity":"critical","observed":json.dumps(schema_conditions, sort_keys=True),"expected":"candidate LEAP requires evidence-drop ledger reference; actual response, response-to-intake, intake, live envelope, and actual-live import schemas require the proper upstream refs","failure_effect":"parallel actual-artifact path can bypass evidence-drop/LEAP/custody/response-gate/intake-conversion graph"},
        {"check_id":"leap-before-drop-blocked","passed":leap_drop_ref_ok and (not (actual_leap_candidates or actual_leap_admitted) or bool(live_candidate_drops)),"severity":"critical","observed":f"candidate_leap={len(actual_leap_candidates)} admitted_leap={len(actual_leap_admitted)} live_candidate_drops={len(live_candidate_drops)}","expected":"candidate/admitted LEAP must descend from a staged live-candidate evidence drop ledger","failure_effect":"close LEAP candidate state and keep downstream locks active"},
        {"check_id":"candidate-challenge-before-disposition","passed":(not gate_consumable_dispositions and not live_custody and not actual_leap_admitted) or bool(candidate_challenges),"severity":"critical","observed":f"candidate_challenges={len(candidate_challenges)} pending={len(pending_challenges)} consumable_dispositions={len(gate_consumable_dispositions)} live_custody={len(live_custody)} admitted_leap={len(actual_leap_admitted)}","expected":"no challenge disposition/custody/admitted LEAP may appear without a candidate challenge report that rereads the external private vault and keeps challenge non-waiver protections","failure_effect":"revoke custody candidate and rerun candidate challenge/replay before disposition review"},
        {"check_id":"candidate-disposition-before-authority-binder","passed":(not eligible_custody_gates and not live_custody) or bool(gate_consumable_dispositions),"severity":"critical","observed":f"candidate_dispositions={len(custody_dispositions)} open_stayed={len(open_stayed_dispositions)} consumable={len(gate_consumable_dispositions)} authority_binders={len(authority_binders)} live_custody={len(live_custody)}","expected":"authority evidence binder and custody gate eligibility require a separate candidate-challenge-disposition-record; raw challenge status or elapsed silence cannot feed custody","failure_effect":"block authority binder/custody gate eligibility and rerun tools/audit_candidate_challenge_disposition.py"},
        {"check_id":"authority-binder-before-custody-gate","passed":custody_gate_authority_binder_ok and not gate_consumable_authority_binders,"severity":"critical","observed":f"authority_binders={len(authority_binders)} consumable={len(gate_consumable_authority_binders)} predispatch={len(predispatch_authority_binders)} custody_gates={len(custody_gates)} eligible={len(eligible_custody_gates)}","expected":"custody gate eligibility requires a class-scoped custody-authority-evidence-binder; operator booleans, protocol output, private-vault locators, redactions, and silence cannot satisfy authority","failure_effect":"block custody gate and rerun tools/audit_custody_authority_evidence_binder.py plus tools/audit_custody_authority_gate.py"},
        {"check_id":"custody-gate-before-custody","passed":not live_custody or bool(eligible_custody_gates),"severity":"critical","observed":f"custody_gates={len(custody_gates)} eligible={len(eligible_custody_gates)} blocked={len(blocked_custody_gates)} live_custody={len(live_custody)}","expected":"live custody requires a custody authority gate fed by valid disposition and evidence-backed authority binder; pending/blocked gates cannot create response, intake, import, or live-floor effects","failure_effect":"block custody record preparation and publish failed-gate shell"},
        {"check_id":"actual-response-before-custody-blocked","passed":response_ref_ok and (not actual_responses or bool(actual_leap_admitted and live_custody)),"severity":"critical","observed":f"actual_shaped_responses={len(actual_shaped_responses)} lineaged_actual_responses={len(actual_responses)} quarantined_fixture_responses={len(quarantined_actual_responses)} unlineaged_unquarantined_responses={len(unlineaged_actual_responses)} admitted_leap={len(actual_leap_admitted)} live_custody={len(live_custody)}","expected":"no live-lineage actual response exists unless LEAP is admitted-to-custody and a live custody record is present; old conversion fixtures stay quarantined with zero live weight","failure_effect":"delete or quarantine response record before any intake/import step"},
        {"check_id":"response-gate-before-response-intake","passed":response_gate_lock_ok and intake_candidate_response_gate_ok and (not actual_responses or bool(eligible_response_gates)),"severity":"critical","observed":f"response_gates={len(response_gates)} eligible={len(eligible_response_gates)} actual_responses={len(actual_responses)} actual_shaped_responses={len(actual_shaped_responses)}","expected":"custody may open only a response verification gate; response records capable of intake require a response gate ref, and response gates never unlock intake/import/floor","failure_effect":"quarantine response record and rerun tools/audit_external_receipt_response_verification_gate.py"},
        {"check_id":"intake-conversion-gate-before-intake-import","passed":intake_conversion_gate_lock_ok and response_to_intake_gate_ok and lineaged_intake_conversion_ref_ok and (not actual_intakes or bool(actual_responses and eligible_intake_conversion_gates)),"severity":"critical","observed":f"intake_conversion_gates={len(intake_conversion_gates)} eligible={len(eligible_intake_conversion_gates)} actual_intakes={len(actual_intakes)} response_intake_refs_ok={response_to_intake_gate_ok}","expected":"a response record cannot create or name intake without a separate intake conversion gate; conversion gates may prepare intake only and never unlock import/floor","failure_effect":"quarantine response/intake records and rerun tools/audit_external_receipt_intake_conversion_gate.py"},
        {"check_id":"actual-intake-before-custody-blocked","passed":intake_ref_ok and (not actual_intakes or bool(actual_leap_admitted and live_custody and eligible_intake_conversion_gates)),"severity":"critical","observed":f"actual_shaped_intakes={len(actual_shaped_intakes)} lineaged_actual_intakes={len(actual_intakes)} quarantined_fixture_intakes={len(quarantined_actual_intakes)} unlineaged_unquarantined_intakes={len(unlineaged_actual_intakes)} admitted_leap={len(actual_leap_admitted)} live_custody={len(live_custody)}","expected":"no live-lineage actual intake exists unless it descends from admitted LEAP, live custody, and an eligible intake conversion gate; old conversion fixtures stay quarantined with no quorum effect","failure_effect":"do not run import gate; publish failed-gate shell"},
        {"check_id":"import-readiness-gate-before-actual-import","passed":import_readiness_gate_lock_ok and (not actual_imports or bool(actual_intakes and eligible_import_readiness_gates)) and import_ref_ok,"severity":"critical","observed":f"import_readiness_gates={len(import_readiness_gates)} eligible={len(eligible_import_readiness_gates)} actual_imports={len(actual_imports)} import_refs_ok={import_ref_ok}","expected":"intake records can only prepare an import-readiness gate; actual-live import requires a readiness gate ref and verified check while readiness gates never increment floor","failure_effect":"quarantine import gate and rerun tools/audit_external_receipt_import_readiness_gate.py"},
        {"check_id":"floor-activation-before-computed-floor","passed":floor_activation_lock_ok and floor_activation_ref_ok and (not actual_imports or bool(eligible_floor_activation_records)),"severity":"critical","observed":f"floor_activation_records={len(floor_activation_records)} eligible={len(eligible_floor_activation_records)} actual_imports={len(actual_imports)} activation_refs_ok={floor_activation_ref_ok}","expected":"actual-live import may enter computed-floor evaluation only through a separate floor activation record that replays readiness, adapter, duplicate/supersession, and challenge checks while preserving no direct floor effect","failure_effect":"exclude import gate from computed floor and rerun tools/audit_live_receipt_floor_activation_record.py"},
        {"check_id":"quorum-participation-before-independence-discount","passed":quorum_participation_lock_ok and quorum_participation_ref_ok and (not actual_imports or bool(eligible_quorum_participation_records)),"severity":"critical","observed":f"quorum_participation_records={len(quorum_participation_records)} eligible={len(eligible_quorum_participation_records)} actual_imports={len(actual_imports)} quorum_refs_ok={quorum_participation_ref_ok}","expected":"actual-live import may enter independence discount only through a separate quorum participation record that rechecks duplicate, supersession, challenge/rollback, no-manual-quorum, and single-class quorum boundaries while preserving no direct floor effect","failure_effect":"exclude import gate from computed floor and rerun tools/audit_live_receipt_quorum_participation_record.py"},
        {"check_id":"live-envelope-before-custody-blocked","passed":envelope_ref_ok and (not live_envelopes or bool(actual_leap_admitted and live_custody)),"severity":"critical","observed":f"live_envelopes={len(live_envelopes)} admitted_leap={len(actual_leap_admitted)} live_custody={len(live_custody)}","expected":"non-host/live-counterparty envelope must reference LEAP and custody and cannot substitute for raw admission","failure_effect":"treat envelope as protocol/transport artifact only; no response/intake/import"},
        {"check_id":"actual-import-before-leap-custody-blocked","passed":import_ref_ok and (not actual_imports or bool(actual_leap_admitted and live_custody and actual_responses and actual_intakes and eligible_intake_conversion_gates)),"severity":"critical","observed":f"actual_imports={len(actual_imports)} admitted_leap={len(actual_leap_admitted)} live_custody={len(live_custody)} lineaged_actual_responses={len(actual_responses)} lineaged_actual_intakes={len(actual_intakes)} eligible_intake_gates={len(eligible_intake_conversion_gates)}","expected":"actual-live import requires admitted LEAP, live custody, actual response, intake conversion gate, actual intake lineage, and import readiness gate","failure_effect":"remove import gate and recompute live floor to zero"},
        {"check_id":"dry-run-custody-remains-nonlive","passed":dryrun_custody_nonlive,"severity":"high","observed":f"custody_records={len(custody_records)} live_custody={len(live_custody)}","expected":"institutional dry-run custody remains usable only for rehearsal and never for live floor","failure_effect":"block package; revert custody record or mark quarantined"},
        {"check_id":"custody-record-response-only-lock","passed":custody_response_only_ok,"severity":"critical","observed":f"custody_records={len(custody_records)} live_custody={len(live_custody)}","expected":"live-candidate custody records must bind a custody gate and may unlock only response preparation; intake, import, and live-floor credit remain locked","failure_effect":"quarantine custody record and rerun tools/audit_counterparty_custody_response_lock.py"},
        {"check_id":"floor-recompute-receipt-publication-lock","passed":floor_recompute_receipt_lock_ok,"severity":"critical","observed":f"floor_recompute_receipts={len(floor_recompute_receipts)} eligible={len(eligible_floor_recompute_receipts)}","expected":"computed snapshots require a recompute receipt that hashes fresh replay, blocks manual floor updates, and keeps partial/zero evidence stayed","failure_effect":"block floor publication and rerun tools/audit_live_receipt_floor_recompute_receipt.py"},
        {"check_id":"publication-rollback-adjudication-lock","passed":publication_rollback_lock_ok,"severity":"critical","observed":f"publication_rollback_adjudications={len(publication_rollback_adjudications)} eligible={len(eligible_publication_rollback_adjudications)}","expected":"published floor posture requires rollback adjudication after recompute receipt; late challenges reopen publication and adjudication has zero direct floor effect","failure_effect":"block continued floor publication and rerun tools/audit_live_receipt_publication_rollback_adjudication.py"},
        {"check_id":"late-change-ingress-publication-freeze-lock","passed":late_change_ingress_lock_ok and not opened_late_change_ingresses,"severity":"critical","observed":f"late_change_ingresses={len(late_change_ingresses)} opened={len(opened_late_change_ingresses)}","expected":"late-change ingress records are replayable freeze/routing objects only; any live signal reopens publication and cannot continue reliance from ingress","failure_effect":"freeze publication and rerun tools/audit_live_receipt_late_change_ingress_record.py plus publication rollback adjudication"},
        {"check_id":"late-change-notice-dispatch-remedy-lock","passed":late_change_notice_dispatch_lock_ok and not live_late_change_notice_dispatches,"severity":"critical","observed":f"late_change_notice_dispatches={len(late_change_notice_dispatches)} live_signal_dispatches={len(live_late_change_notice_dispatches)} ready={len(ready_late_change_notice_dispatches)}","expected":"late-change notice dispatch records are affected-party notice/remedy routing objects only; live dispatch cannot continue publication, count silence as waiver, or increment floor","failure_effect":"freeze publication and rerun tools/audit_live_receipt_late_change_notice_dispatch_record.py"},
        {"check_id":"late-change-remedy-resolution-recompute-lock","passed":late_change_remedy_resolution_lock_ok and not live_late_change_remedy_resolutions,"severity":"critical","observed":f"late_change_remedy_resolutions={len(late_change_remedy_resolutions)} live_signal_resolutions={len(live_late_change_remedy_resolutions)} ready={len(ready_late_change_remedy_resolutions)}","expected":"late-change remedy resolution records are appeal/remedy decision routing objects only; they cannot continue publication, count silence as waiver, or increment floor","failure_effect":"freeze publication and rerun tools/audit_live_receipt_late_change_remedy_resolution_record.py plus publication rollback adjudication"},
        {"check_id":"late-change-remedy-execution-completion-lock","passed":late_change_remedy_execution_lock_ok and not live_late_change_remedy_executions,"severity":"critical","observed":f"late_change_remedy_executions={len(late_change_remedy_executions)} live_signal_executions={len(live_late_change_remedy_executions)} ready={len(ready_late_change_remedy_executions)}","expected":"late-change remedy execution records are corrective-action completion and recompute-routing objects only; they cannot continue publication, count silence as completion, or increment floor","failure_effect":"freeze publication and rerun tools/audit_live_receipt_late_change_remedy_execution_record.py plus publication rollback adjudication"},
        {"check_id":"computed-floor-zero-after-graph","passed":floor_n == 0 and floor.get("computed_floor", {}).get("reliance_effect") == "stayed","severity":"critical","observed":f"floor={floor_n} reliance={floor.get('computed_floor', {}).get('reliance_effect')}","expected":"admission graph does not itself alter live floor; floor stays zero without genuine artifact","failure_effect":"rollback graph/report and rerun computed floor/invariant replay"},
    ]
    nodes = [
        {"node_id":"EVIDENCE_DROP","surface_ref":f"examples/live-evidence-drop-ledger-{REV}-quarantine-control.json","object_count":len(drop_paths),"actual_live_count":len(live_candidate_drops),"state":"quarantine-only" if not live_candidate_drops else "live-candidate-staged", "blocks_downstream_until":["raw payload copied into quarantine","no redacted-only substitution","archive/path traversal scan","protocol output filtered","LEAP candidate opened explicitly"]},
        {"node_id":"LEAP","surface_ref":f"examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json","object_count":len(leap_paths),"actual_live_count":len(actual_leap_admitted),"state":"ready-no-artifact" if not actual_leap_admitted else "admitted", "blocks_downstream_until":["evidence drop ledger ref","raw payload custody","authority scope","verifier adapter","non-host retention","independence fields"]},
        {"node_id":"CANDIDATE_CHALLENGE","surface_ref":f"examples/live-artifact-candidate-challenge-report-{REV}-synthetic-pending.json","object_count":len(challenge_paths),"actual_live_count":0,"state":"pending-or-synthetic-only" if pending_challenges else "none-or-resolved", "blocks_downstream_until":["external private-vault reread","hash and size reverified","challenge window resolved","silence not treated as waiver","separate disposition record"]},
        {"node_id":"CANDIDATE_DISPOSITION","surface_ref":f"examples/candidate-challenge-disposition-record-{REV}-open-stayed.json","object_count":len(custody_disposition_paths),"actual_live_count":len(gate_consumable_dispositions),"state":"open-stayed" if not gate_consumable_dispositions else "may-feed-authority-binder", "blocks_downstream_until":["human-reviewed closure","affirmative counterparty message or reviewed objection","authority and request trace checks","no redacted-only/protocol/silence closure"]},
        {"node_id":"AUTHORITY_EVIDENCE_BINDER","surface_ref":f"examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json","object_count":len(authority_binder_paths),"actual_live_count":len(gate_consumable_authority_binders),"state":"pre-dispatch-no-authority" if not gate_consumable_authority_binders else "may-feed-custody-gate", "blocks_downstream_until":["manual counterparty contact evidence ref","request trace evidence ref","class-scoped authority evidence ref","verifier/timestamp/non-host/sealed parity refs","no checkbox/protocol/vault-uri/redaction substitutions"]},
        {"node_id":"CUSTODY_GATE","surface_ref":f"examples/counterparty-artifact-custody-gate-{REV}-pending-challenge.json","object_count":len(custody_gate_paths),"actual_live_count":len(eligible_custody_gates),"state":"blocked" if not eligible_custody_gates else "eligible-for-custody-record", "blocks_downstream_until":["valid challenge disposition consumed","custody-authority-evidence-binder consumed","manual counterparty contact","receipt-class authority","verifier adapter","timestamp","non-host retention","sealed/public parity","redaction boundary","dependency check"]},
        {"node_id":"CUSTODY","surface_ref":"schemas/counterparty-artifact-custody-record.schema.json","object_count":len(custody_paths),"actual_live_count":len(live_custody),"state":"dry-run-only" if not live_custody else "live-candidate-response-only", "blocks_downstream_until":["raw hash verified","sealed/public parity","redaction boundary","non-host retention","custody gate eligibility","response-only lock; no intake/import/floor from custody alone"]},
        {"node_id":"RESPONSE_GATE","surface_ref":"schemas/external-receipt-response-verification-gate.schema.json","object_count":len(response_gate_paths),"actual_live_count":len(eligible_response_gates),"state":"no-eligible-response-gate" if not eligible_response_gates else "eligible-for-response-record", "blocks_downstream_until":["verified counterparty reply","scoped acceptance","receipt class match","request trace","independent timestamp","non-host retention","manual review","response-only output; no intake/import/floor from gate"]},
        {"node_id":"RESPONSE","surface_ref":"schemas/external-receipt-response-record.schema.json","object_count":len(response_paths),"actual_live_count":len(actual_responses),"state":"no-live-lineage-response", "blocks_downstream_until":["LEAP/custody refs","response verification gate ref"], "quarantined_actual_shaped_count": len(quarantined_actual_responses)},
        {"node_id":"INTAKE_CONVERSION_GATE","surface_ref":"schemas/external-receipt-intake-conversion-gate.schema.json","object_count":len(intake_conversion_gate_paths),"actual_live_count":len(eligible_intake_conversion_gates),"state":"no-eligible-intake-conversion-gate" if not eligible_intake_conversion_gates else "eligible-for-intake-record", "blocks_downstream_until":["response record actual and lineaged","response gate eligibility","gate/response match","manual conversion review","no import/floor from conversion gate"]},
        {"node_id":"INTAKE","surface_ref":"schemas/external-receipt-intake-record.schema.json","object_count":len(intake_paths),"actual_live_count":len(actual_intakes),"state":"no-live-lineage-intake", "blocks_downstream_until":["LEAP/custody refs","intake conversion gate ref","import readiness gate before actual import"], "quarantined_actual_shaped_count": len(quarantined_actual_intakes)},
        {"node_id":"IMPORT_READINESS_GATE","surface_ref":"schemas/external-receipt-import-readiness-gate.schema.json","object_count":len(import_readiness_gate_paths),"actual_live_count":len(eligible_import_readiness_gates),"state":"no-eligible-import-readiness-gate" if not eligible_import_readiness_gates else "eligible-for-import-gate", "blocks_downstream_until":["intake record actual and lineaged","intake conversion gate eligibility","non-host retention artifact","manual import readiness review","cryptographic adapter required next","no floor from readiness gate"]},
        {"node_id":"ENVELOPE","surface_ref":"schemas/nonhost-response-artifact-envelope.schema.json","object_count":len(envelope_paths),"actual_live_count":len(live_envelopes),"state":"no-live-envelope", "blocks_downstream_until":["LEAP/custody refs"]},
        {"node_id":"IMPORT_GATE","surface_ref":"schemas/actual-receipt-import-gate.schema.json","object_count":len(import_gate_paths),"actual_live_count":len(actual_imports),"state":"no-actual-live-import", "blocks_downstream_until":["actual response","intake conversion gate","actual intake","import readiness gate","cryptographic adapter","floor activation record"]},
        {"node_id":"FLOOR_ACTIVATION","surface_ref":"schemas/live-receipt-floor-activation-record.schema.json","object_count":len(activation_record_paths),"actual_live_count":len(eligible_floor_activation_records),"state":"no-eligible-floor-activation" if not eligible_floor_activation_records else "eligible-for-floor-recompute", "blocks_downstream_until":["readiness gate object replay","verifier adapter binding","duplicate/counterparty/class checks","supersession checks","challenge/rollback checks","quorum participation record"]},
        {"node_id":"QUORUM_PARTICIPATION","surface_ref":"schemas/live-receipt-quorum-participation-record.schema.json","object_count":len(quorum_participation_record_paths),"actual_live_count":len(eligible_quorum_participation_records),"state":"no-eligible-quorum-participation" if not eligible_quorum_participation_records else "eligible-for-independence-discount", "blocks_downstream_until":["duplicate/counterparty/issuer/class rechecks","supersession recheck","challenge/rollback recheck","single-class quorum block","computed-floor recomputation required"]},
        {"node_id":"COMPUTED_FLOOR","surface_ref":f"examples/live-receipt-floor-computed-snapshot-{REV}.json","object_count":1,"actual_live_count":floor_n,"state":floor.get("computed_floor", {}).get("reliance_effect", "unknown"), "blocks_downstream_until":["all class-local required receipts survive independence discount", "floor recompute receipt hashes fresh replay before publication"]},
        {"node_id":"FLOOR_RECOMPUTE_RECEIPT","surface_ref":"schemas/live-receipt-floor-recompute-receipt.schema.json","object_count":len(floor_recompute_receipt_paths),"actual_live_count":len([r for r in eligible_floor_recompute_receipts if r.get("decision", {}).get("may_upgrade_reliance") is True]),"state":"zero-floor-stayed-publication-ready" if eligible_floor_recompute_receipts and floor_n == 0 else ("eligible-reliance-publication" if eligible_floor_recompute_receipts else "missing-recompute-receipt"), "blocks_downstream_until":["snapshot hash matches fresh replay", "no manual override", "rollback/challenge replay", "full required-class vector for reliance upgrade"]},
        {"node_id":"PUBLICATION_ROLLBACK_ADJUDICATION","surface_ref":"schemas/live-receipt-publication-rollback-adjudication.schema.json","object_count":len(publication_rollback_paths),"actual_live_count":len([r for r in eligible_publication_rollback_adjudications if r.get("decision", {}).get("may_upgrade_reliance") is True]),"state":"zero-floor-stayed-continuation-ready" if eligible_publication_rollback_adjudications and floor_n == 0 else ("eligible-reliance-continuation" if eligible_publication_rollback_adjudications else "missing-publication-rollback-adjudication"), "blocks_downstream_until":["floor recompute receipt current", "snapshot hash still matches", "late challenges replayed", "no uncompleted upheld rollback", "supersession and public notice checked"]},
        {"node_id":"LATE_CHANGE_INGRESS","surface_ref":"schemas/live-receipt-late-change-ingress-record.schema.json","object_count":len(late_change_ingress_paths),"actual_live_count":len(opened_late_change_ingresses),"state":"monitoring-no-live-signal" if late_change_ingress_lock_ok and not opened_late_change_ingresses else "publication-reopened-by-late-signal", "blocks_downstream_until":["late signal retained outside release tree", "public shell redacts private material", "affected publication or receipt lineage is bound", "floor recompute receipt and publication rollback adjudication rerun"]},
        {"node_id":"LATE_CHANGE_NOTICE_DISPATCH","surface_ref":"schemas/live-receipt-late-change-notice-dispatch-record.schema.json","object_count":len(late_change_notice_dispatch_paths),"actual_live_count":len(live_late_change_notice_dispatches),"state":"monitoring-no-notice-required" if late_change_notice_dispatch_lock_ok and not live_late_change_notice_dispatches else "notice-dispatch-required-publication-stayed", "blocks_downstream_until":["affected parties identified", "public freeze notice prepared", "delivery proof retained outside release tree", "remedy/appeal window opened", "silence not treated as waiver"]},
        {"node_id":"LATE_CHANGE_REMEDY_RESOLUTION","surface_ref":"schemas/live-receipt-late-change-remedy-resolution-record.schema.json","object_count":len(late_change_remedy_resolution_paths),"actual_live_count":len(live_late_change_remedy_resolutions),"state":"monitoring-no-remedy-required" if late_change_remedy_resolution_lock_ok and not live_late_change_remedy_resolutions else "remedy-resolution-required-publication-stayed", "blocks_downstream_until":["remedy/appeal window closed", "affected-party submissions retained", "resolution authority scoped", "decision recorded", "non-host proof retained", "recompute plus publication rollback rerun"]},
        {"node_id":"LATE_CHANGE_REMEDY_EXECUTION","surface_ref":"schemas/live-receipt-late-change-remedy-execution-record.schema.json","object_count":len(late_change_remedy_execution_paths),"actual_live_count":len(live_late_change_remedy_executions),"state":"monitoring-no-execution-required" if late_change_remedy_execution_lock_ok and not live_late_change_remedy_executions else "remedy-execution-required-publication-stayed", "blocks_downstream_until":["ordered rollback/correction/supersession carried out", "non-host execution proof retained", "affected-party completion notice prepared", "private material redacted", "floor recompute plus publication rollback rerun"]},
    ]
    edges = [
        {"from":"EVIDENCE_DROP","to":"LEAP","required_ref":"ledger_id -> source_evidence_drop_ledger_ref","enforced_by":["schemas/live-evidence-drop-ledger.schema.json","tools/stage_live_evidence_drop.py","tools/audit_live_evidence_drop_quarantine.py","schemas/live-evidence-acquisition-packet.schema.json"],"current_state":"quarantine-control-only"},
        {"from":"LEAP","to":"CANDIDATE_CHALLENGE","required_ref":"packet_id -> linked_refs.leap_packet_id","enforced_by":["schemas/live-artifact-candidate-challenge-report.schema.json","tools/prepare_candidate_challenge_packet.py","tools/audit_candidate_challenge_replay.py"],"current_state":"blocked-pending-real-artifact"},
        {"from":"CANDIDATE_CHALLENGE","to":"CANDIDATE_DISPOSITION","required_ref":"challenge_report_id -> linked_candidate_challenge_report_ref; no silence/waiver shortcut","enforced_by":["schemas/live-artifact-candidate-challenge-report.schema.json","schemas/candidate-challenge-disposition-record.schema.json","tools/audit_candidate_challenge_replay.py","tools/audit_candidate_challenge_disposition.py"],"current_state":"blocked-open-stayed-disposition"},
        {"from":"CANDIDATE_DISPOSITION","to":"AUTHORITY_EVIDENCE_BINDER","required_ref":"disposition_record_id -> source_candidate_disposition_ref; raw status override blocked before authority proof","enforced_by":["schemas/candidate-challenge-disposition-record.schema.json","schemas/custody-authority-evidence-binder.schema.json","tools/audit_candidate_challenge_disposition.py","tools/audit_custody_authority_evidence_binder.py"],"current_state":"blocked-no-consumable-disposition"},
        {"from":"AUTHORITY_EVIDENCE_BINDER","to":"CUSTODY_GATE","required_ref":"binder_id -> authority_evidence_binder.binder_id; booleans/protocol/vault URI/redaction cannot substitute","enforced_by":["schemas/custody-authority-evidence-binder.schema.json","schemas/counterparty-artifact-custody-gate.schema.json","tools/audit_custody_authority_evidence_binder.py","tools/audit_custody_authority_gate.py"],"current_state":"blocked-no-consumable-authority-binder"},
        {"from":"CUSTODY_GATE","to":"CUSTODY","required_ref":"custody_gate_id -> pre-custody authorization for custody record","enforced_by":["schemas/counterparty-artifact-custody-gate.schema.json","tools/audit_custody_authority_gate.py","tools/audit_counterparty_artifact_custody.py"],"current_state":"blocked-no-authority-gate-eligibility"},
        {"from":"CUSTODY","to":"RESPONSE_GATE","required_ref":"custody_record_id -> linked_custody_record_ref","enforced_by":["schemas/counterparty-artifact-custody-record.schema.json","tools/prepare_counterparty_artifact_custody_record.py","tools/audit_counterparty_custody_response_lock.py","schemas/external-receipt-response-verification-gate.schema.json","tools/prepare_external_receipt_response_gate.py","tools/audit_external_receipt_response_verification_gate.py"],"current_state":"blocked-no-eligible-response-gate; custody can authorize response verification only"},
        {"from":"RESPONSE_GATE","to":"RESPONSE","required_ref":"response_gate_id -> linked_response_verification_gate_ref","enforced_by":["schemas/external-receipt-response-verification-gate.schema.json","schemas/external-receipt-response-record.schema.json","tools/audit_external_receipt_response_verification_gate.py"],"current_state":"blocked-no-actual-response"},
        {"from":"RESPONSE","to":"INTAKE_CONVERSION_GATE","required_ref":"response_record_id + response_gate_id -> linked_response_record_ref / linked_response_verification_gate_ref","enforced_by":["schemas/external-receipt-intake-conversion-gate.schema.json","tools/prepare_external_receipt_intake_conversion_gate.py","tools/audit_external_receipt_intake_conversion_gate.py"],"current_state":"blocked-no-eligible-intake-conversion-gate"},
        {"from":"INTAKE_CONVERSION_GATE","to":"INTAKE","required_ref":"intake_conversion_gate_id -> linked_intake_conversion_gate_ref","enforced_by":["schemas/external-receipt-response-record.schema.json","schemas/external-receipt-intake-record.schema.json","tools/audit_external_receipt_intake_conversion_gate.py"],"current_state":"blocked-no-actual-intake"},
        {"from":"INTAKE","to":"IMPORT_READINESS_GATE","required_ref":"receipt_record_id + intake_conversion_gate_id -> linked_intake_record_ref / linked_intake_conversion_gate_ref","enforced_by":["schemas/external-receipt-import-readiness-gate.schema.json","tools/prepare_external_receipt_import_readiness_gate.py","tools/audit_external_receipt_import_readiness_gate.py"],"current_state":"blocked-no-eligible-import-readiness-gate"},
        {"from":"IMPORT_READINESS_GATE","to":"IMPORT_GATE","required_ref":"import_readiness_gate_id -> linked_import_readiness_gate_ref","enforced_by":["schemas/external-receipt-import-readiness-gate.schema.json","schemas/actual-receipt-import-gate.schema.json","tools/live_floor_lib.py","tools/compute_live_receipt_floor.py"],"current_state":"blocked-no-actual-live-import"},
        {"from":"IMPORT_GATE","to":"FLOOR_ACTIVATION","required_ref":"import_gate_id -> linked_import_gate_ref","enforced_by":["schemas/live-receipt-floor-activation-record.schema.json","tools/prepare_live_receipt_floor_activation_record.py","tools/audit_live_receipt_floor_activation_record.py"],"current_state":"blocked-no-eligible-floor-activation"},
        {"from":"FLOOR_ACTIVATION","to":"QUORUM_PARTICIPATION","required_ref":"activation_record_id -> linked_floor_activation_record_ref","enforced_by":["schemas/live-receipt-quorum-participation-record.schema.json","tools/prepare_live_receipt_quorum_participation_record.py","tools/audit_live_receipt_quorum_participation_record.py"],"current_state":"blocked-no-eligible-quorum-participation"},
        {"from":"QUORUM_PARTICIPATION","to":"COMPUTED_FLOOR","required_ref":"quorum_participation_record admits import_gate_id to independence_discount_register after recompute","enforced_by":["tools/live_floor_lib.py","tools/compute_live_receipt_floor.py","tools/audit_live_receipt_quorum_participation_record.py"],"current_state":"floor-zero"},
        {"from":"COMPUTED_FLOOR","to":"FLOOR_RECOMPUTE_RECEIPT","required_ref":"snapshot_id -> linked_computed_snapshot_ref plus sha256/fresh replay match","enforced_by":["schemas/live-receipt-floor-recompute-receipt.schema.json","tools/prepare_live_receipt_floor_recompute_receipt.py","tools/audit_live_receipt_floor_recompute_receipt.py"],"current_state":"zero-floor-publication-stayed"},
        {"from":"FLOOR_RECOMPUTE_RECEIPT","to":"PUBLICATION_ROLLBACK_ADJUDICATION","required_ref":"recompute_receipt_id -> linked_floor_recompute_receipt_ref plus late challenge/rollback replay","enforced_by":["schemas/live-receipt-publication-rollback-adjudication.schema.json","tools/prepare_live_receipt_publication_rollback_adjudication.py","tools/audit_live_receipt_publication_rollback_adjudication.py"],"current_state":"zero-floor-publication-continuation-stayed"},
        {"from":"PUBLICATION_ROLLBACK_ADJUDICATION","to":"LATE_CHANGE_INGRESS","required_ref":"publication_adjudication_id -> linked_publication_adjudication_ref for any later revocation/supersession/challenge signal","enforced_by":["schemas/live-receipt-late-change-ingress-record.schema.json","tools/prepare_live_receipt_late_change_ingress_record.py","tools/audit_live_receipt_late_change_ingress_record.py"],"current_state":"monitoring-no-live-signal"},
        {"from":"LATE_CHANGE_INGRESS","to":"LATE_CHANGE_NOTICE_DISPATCH","required_ref":"late_change_ingress_id -> linked_late_change_ingress_ref for any affected-party freeze/remedy notice","enforced_by":["schemas/live-receipt-late-change-notice-dispatch-record.schema.json","tools/prepare_live_receipt_late_change_notice_dispatch_record.py","tools/audit_live_receipt_late_change_notice_dispatch_record.py"],"current_state":"monitoring-no-notice-required"},
        {"from":"LATE_CHANGE_NOTICE_DISPATCH","to":"LATE_CHANGE_REMEDY_RESOLUTION","required_ref":"late_change_notice_dispatch_id -> linked_late_change_notice_dispatch_ref before any remedy resolution or recompute rerun","enforced_by":["schemas/live-receipt-late-change-remedy-resolution-record.schema.json","tools/prepare_live_receipt_late_change_remedy_resolution_record.py","tools/audit_live_receipt_late_change_remedy_resolution_record.py"],"current_state":"monitoring-no-remedy-required"},
        {"from":"LATE_CHANGE_REMEDY_RESOLUTION","to":"LATE_CHANGE_REMEDY_EXECUTION","required_ref":"late_change_remedy_resolution_id -> linked_late_change_remedy_resolution_ref before any executed rollback/correction/supersession can be treated as ready","enforced_by":["schemas/live-receipt-late-change-remedy-execution-record.schema.json","tools/prepare_live_receipt_late_change_remedy_execution_record.py","tools/audit_live_receipt_late_change_remedy_execution_record.py"],"current_state":"monitoring-no-execution-required"},
    ]
    return {
        "graph_id": f"LAAG-2026-{REV}-live-artifact-admission-graph",
        "schema_version": "live-artifact-admission-graph-v0.1",
        "created_at": CREATED_AT,
        "revision": REV,
        "generated_by_tool": "tools/build_live_artifact_admission_graph.py",
        "nodes": nodes,
        "edges": edges,
        "bypass_checks": checks,
        "live_path_state": {
            "evidence_drop_count": len(drop_records),
            "live_candidate_drop_count": len(live_candidate_drops),
            "quarantined_drop_count": len(quarantined_drops),
            "rejected_drop_count": len(rejected_drops),
            "candidate_challenge_count": len(challenge_records),
            "candidate_disposition_count": len(custody_disposition_records),
            "gate_consumable_candidate_disposition_count": len(gate_consumable_dispositions),
            "custody_gate_count": len(custody_gate_records),
            "eligible_custody_gate_count": len(eligible_custody_gates),
            "response_gate_count": len(response_gate_records),
            "eligible_response_gate_count": len(eligible_response_gates),
            "intake_conversion_gate_count": len(intake_conversion_gate_records),
            "eligible_intake_conversion_gate_count": len(eligible_intake_conversion_gates),
            "import_readiness_gate_count": len(import_readiness_gate_records),
            "eligible_import_readiness_gate_count": len(eligible_import_readiness_gates),
            "floor_activation_record_count": len(floor_activation_records),
            "eligible_floor_activation_record_count": len(eligible_floor_activation_records),
            "quorum_participation_record_count": len(quorum_participation_records),
            "eligible_quorum_participation_record_count": len(eligible_quorum_participation_records),
            "floor_recompute_receipt_count": len(floor_recompute_receipts),
            "eligible_floor_recompute_receipt_count": len(eligible_floor_recompute_receipts),
            "publication_rollback_adjudication_count": len(publication_rollback_adjudications),
            "eligible_publication_rollback_adjudication_count": len(eligible_publication_rollback_adjudications),
            "late_change_ingress_count": len(late_change_ingresses),
            "opened_late_change_ingress_count": len(opened_late_change_ingresses),
            "late_change_notice_dispatch_count": len(late_change_notice_dispatches),
            "live_late_change_notice_dispatch_count": len(live_late_change_notice_dispatches),
            "late_change_remedy_resolution_count": len(late_change_remedy_resolutions),
            "live_late_change_remedy_resolution_count": len(live_late_change_remedy_resolutions),
            "late_change_remedy_execution_count": len(late_change_remedy_executions),
            "live_late_change_remedy_execution_count": len(live_late_change_remedy_executions),
            "actual_live_artifact_count": len(live_custody),
            "actual_response_count": len(actual_responses),
            "actual_intake_count": len(actual_intakes),
            "actual_shaped_response_count": len(actual_shaped_responses),
            "actual_shaped_intake_count": len(actual_shaped_intakes),
            "quarantined_actual_shaped_response_count": len(quarantined_actual_responses),
            "quarantined_actual_shaped_intake_count": len(quarantined_actual_intakes),
            "actual_live_import_count": len(actual_imports),
            "computed_live_floor": floor_n,
            "downstream_creation_blocked": downstream_blocked,
            "reliance_effect": floor.get("computed_floor", {}).get("reliance_effect", "unknown"),
        },
        "public_summary": f"{REV} computes an evidence-drop -> LEAP -> candidate challenge -> custody gate -> custody(response-only) -> response gate -> response -> intake conversion gate -> intake -> import readiness gate -> import -> floor activation -> quorum participation -> computed-floor -> floor recompute receipt -> publication rollback adjudication -> late-change ingress -> late-change notice dispatch -> late-change remedy resolution -> late-change remedy execution admission graph; no actual live artifact is present, downstream creation is blocked, and live floor remains zero.",
        "no_live_floor_effect": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    graph = build()
    if args.check:
        path = ROOT / "examples" / f"live-artifact-admission-graph-{REV}.json"
        existing = load(path)
        if existing != graph:
            raise SystemExit(f"live artifact admission graph mismatch: {path.relative_to(ROOT)}")
        print("build_live_artifact_admission_graph: OK")
        return
    text = json.dumps(graph, indent=2) + "\n"
    if args.output:
        out = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
        out.write_text(text, encoding="utf-8")
        print(out)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
