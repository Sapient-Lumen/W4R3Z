#!/usr/bin/env python3
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-18T08:27:00Z"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def compute_snapshot():
    spec = importlib.util.spec_from_file_location("compute_live_receipt_floor", ROOT / "tools" / "compute_live_receipt_floor.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compute(root=ROOT, rev=REV, created_at=CREATED_AT)


def build():
    snap = compute_snapshot()
    floor = snap["computed_floor"]
    import_gate_paths = sorted((ROOT / "examples").glob("actual-receipt-import-gate*.json"))
    custody_gate_paths = sorted((ROOT / "examples").glob("counterparty-artifact-custody-gate*.json"))
    custody_paths = sorted((ROOT / "examples").glob("counterparty-artifact-custody-record*.json"))
    response_gate_paths = sorted((ROOT / "examples").glob("external-receipt-response-verification-gate*.json"))
    intake_conversion_gate_paths = sorted((ROOT / "examples").glob("external-receipt-intake-conversion-gate*.json"))
    import_readiness_gate_paths = sorted((ROOT / "examples").glob("external-receipt-import-readiness-gate*.json"))
    activation_record_paths = sorted((ROOT / "examples").glob("live-receipt-floor-activation-record*.json"))
    quorum_participation_record_paths = sorted((ROOT / "examples").glob("live-receipt-quorum-participation-record*.json"))
    floor_recompute_receipt_paths = sorted((ROOT / "examples").glob("live-receipt-floor-recompute-receipt*.json"))
    publication_rollback_paths = sorted((ROOT / "examples").glob("live-receipt-publication-rollback-adjudication*.json"))
    late_change_ingress_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-ingress-record*.json"))
    late_change_notice_dispatch_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-notice-dispatch-record*.json"))
    late_change_remedy_resolution_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-remedy-resolution-record*.json"))
    late_change_remedy_execution_paths = sorted((ROOT / "examples").glob("live-receipt-late-change-remedy-execution-record*.json"))
    fieldkit_paths = sorted((ROOT / "examples").glob("live-artifact-import-fieldkit*.json"))
    snapshot_paths = sorted((ROOT / "examples").glob("live-receipt-floor-computed-snapshot-rev*.json"))
    crypto_adapter_paths = sorted((ROOT / "examples").glob("cryptographic-verifier-adapter-*.json"))
    acquisition_paths = sorted((ROOT / "examples").glob("live-evidence-acquisition-packet*.json"))
    admission_graph_paths = sorted((ROOT / "examples").glob("live-artifact-admission-graph-rev*.json"))
    disallowed = []
    for p in import_gate_paths:
        data = load(p)
        decision = data.get("import_decision", {})
        prov = data.get("source_provenance", {})
        if decision.get("import_allowed_to_live_floor") is True and prov.get("collection_context") != "live-counterparty":
            disallowed.append(p.relative_to(ROOT).as_posix())
    fieldkit_ok = False
    if fieldkit_paths:
        fk = load(fieldkit_paths[-1])
        fieldkit_ok = (
            fk.get("fieldkit_state") == "ready-no-live-artifact"
            and fk.get("reliance_limits", {}).get("may_increase_live_floor") is False
            and len(fk.get("raw_artifact_slots", [])) >= 10
            and all(slot.get("blocks_if_missing") is True and slot.get("blocks_if_failed") is True for slot in fk.get("raw_artifact_slots", []))
        )
    leap_ok = False
    if acquisition_paths:
        leap = load(acquisition_paths[-1])
        locks = leap.get("downstream_locks", {})
        raw = leap.get("raw_payload_control", {})
        crypto = leap.get("cryptographic_binding", {})
        ind = leap.get("independence_controls", {})
        leap_ok = (
            leap.get("state") == "ready-no-live-artifact"
            and leap.get("no_live_floor_effect") is True
            and locks.get("response_creation_allowed") is False
            and locks.get("intake_creation_allowed") is False
            and locks.get("import_gate_creation_allowed") is False
            and locks.get("live_floor_delta_allowed") is False
            and raw.get("raw_payload_missing_blocks_response_creation") is True
            and crypto.get("signature_boolean_zero_weight_without_adapter") is True
            and ind.get("correlation_discount_blocks_independence") is True
        )
    custody_gate_ok = bool(custody_gate_paths) and all(
        load(p).get("no_live_floor_effect") is True
        and load(p).get("downstream_locks", {}).get("response_creation_allowed") is False
        and load(p).get("downstream_locks", {}).get("intake_creation_allowed") is False
        and load(p).get("downstream_locks", {}).get("import_gate_creation_allowed") is False
        and load(p).get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        for p in custody_gate_paths
    )
    custody_response_only_ok = all(
        load(p).get("artifact_state") != "live-candidate-artifact" or (
            bool(load(p).get("linked_custody_gate_ref"))
            and load(p).get("import_readiness", {}).get("may_create_response_record") is True
            and load(p).get("import_readiness", {}).get("may_create_intake_record") is False
            and load(p).get("import_readiness", {}).get("may_run_import_gate") is False
            and load(p).get("import_readiness", {}).get("live_import_floor_delta") == 0
            and load(p).get("decision", {}).get("live_reliance_effect") == "stayed"
        )
        for p in custody_paths
    )
    response_gate_lock_ok = all(
        load(p).get("no_live_floor_effect") is True
        and load(p).get("downstream_locks", {}).get("may_create_intake_record") is False
        and load(p).get("downstream_locks", {}).get("may_run_import_gate") is False
        and load(p).get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and load(p).get("decision", {}).get("can_generate_actual_intake") is False
        for p in response_gate_paths
    )
    intake_conversion_gate_lock_ok = all(
        load(p).get("no_live_floor_effect") is True
        and load(p).get("downstream_locks", {}).get("may_run_import_gate") is False
        and load(p).get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and load(p).get("decision", {}).get("can_run_import_gate") is False
        for p in intake_conversion_gate_paths
    )
    import_readiness_gate_lock_ok = all(
        load(p).get("no_live_floor_effect") is True
        and load(p).get("downstream_locks", {}).get("may_increment_live_floor") is False
        and load(p).get("downstream_locks", {}).get("live_floor_delta_allowed") is False
        and load(p).get("decision", {}).get("can_increment_live_floor") is False
        for p in import_readiness_gate_paths
    )
    floor_activation_lock_ok = all(
        load(p).get("no_live_floor_effect") is True
        and load(p).get("floor_recompute_locks", {}).get("manual_floor_increment_allowed") is False
        and load(p).get("floor_recompute_locks", {}).get("computed_floor_recompute_required") is True
        and load(p).get("floor_recompute_locks", {}).get("activation_record_can_satisfy_quorum_by_itself") is False
        and load(p).get("floor_recompute_locks", {}).get("live_floor_delta_allowed_by_activation_record") is False
        and load(p).get("decision", {}).get("can_increment_live_floor_by_itself") is False
        for p in activation_record_paths
    )
    quorum_participation_lock_ok = all(
        load(p).get("no_live_floor_effect") is True
        and load(p).get("quorum_locks", {}).get("may_satisfy_cross_critical_quorum_by_itself") is False
        and load(p).get("quorum_locks", {}).get("manual_live_floor_update_allowed") is False
        and load(p).get("quorum_locks", {}).get("live_floor_delta_allowed_by_participation_record") is False
        and load(p).get("quorum_locks", {}).get("computed_floor_recompute_required") is True
        and load(p).get("decision", {}).get("can_upgrade_reliance_by_itself") is False
        for p in quorum_participation_record_paths
    )
    floor_recompute_receipt_lock_ok = bool(floor_recompute_receipt_paths) and all(
        load(p).get("no_direct_floor_effect") is True
        and load(p).get("publication_locks", {}).get("manual_live_floor_update_allowed") is False
        and load(p).get("publication_locks", {}).get("may_increment_live_floor_from_receipt") is False
        and load(p).get("publication_locks", {}).get("recompute_receipt_required_for_reliance_upgrade") is True
        and load(p).get("recompute_checks", {}).get("snapshot_matches_fresh_recompute") is True
        and load(p).get("recompute_checks", {}).get("no_manual_ledger_override") is True
        and load(p).get("decision", {}).get("may_upgrade_reliance") is (floor.get("cross_critical_quorum_satisfied") is True)
        for p in floor_recompute_receipt_paths
    )

    publication_rollback_lock_ok = bool(publication_rollback_paths) and all(
        load(p).get("no_direct_floor_effect") is True
        and load(p).get("publication_rollback_locks", {}).get("may_increment_live_floor_from_adjudication") is False
        and load(p).get("publication_rollback_locks", {}).get("manual_publication_override_allowed") is False
        and load(p).get("publication_rollback_locks", {}).get("recompute_receipt_required_after_late_change") is True
        and load(p).get("adjudication_checks", {}).get("snapshot_hash_matches_recompute_receipt") is True
        and load(p).get("decision", {}).get("may_upgrade_reliance") is (floor.get("cross_critical_quorum_satisfied") is True)
        for p in publication_rollback_paths
    )
    late_change_ingress_lock_ok = bool(late_change_ingress_paths) and all(
        load(p).get("no_direct_floor_effect") is True
        and load(p).get("publication_freeze_locks", {}).get("may_continue_published_snapshot_from_ingress") is False
        and load(p).get("publication_freeze_locks", {}).get("may_continue_reliance_from_ingress") is False
        and load(p).get("publication_freeze_locks", {}).get("may_increment_live_floor_from_ingress") is False
        and load(p).get("publication_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and load(p).get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and load(p).get("decision", {}).get("may_upgrade_reliance") is False
        for p in late_change_ingress_paths
    )
    opened_late_change_ingress_count = sum(1 for p in late_change_ingress_paths if load(p).get("decision", {}).get("late_change_state") != "monitoring-no-signal")
    late_change_notice_dispatch_lock_ok = bool(late_change_notice_dispatch_paths) and all(
        load(p).get("no_direct_floor_effect") is True
        and load(p).get("notice_freeze_locks", {}).get("may_continue_published_snapshot_from_notice") is False
        and load(p).get("notice_freeze_locks", {}).get("may_continue_reliance_from_notice") is False
        and load(p).get("notice_freeze_locks", {}).get("may_increment_live_floor_from_notice") is False
        and load(p).get("notice_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and load(p).get("notice_freeze_locks", {}).get("notice_silence_counts_as_waiver") is False
        and load(p).get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and load(p).get("decision", {}).get("may_upgrade_reliance") is False
        for p in late_change_notice_dispatch_paths
    )
    live_late_change_notice_dispatch_count = sum(1 for p in late_change_notice_dispatch_paths if load(p).get("notice_context", {}).get("live_late_signal_present") is True)
    late_change_remedy_resolution_lock_ok = bool(late_change_remedy_resolution_paths) and all(
        load(p).get("no_direct_floor_effect") is True
        and load(p).get("resolution_freeze_locks", {}).get("may_continue_published_snapshot_from_resolution") is False
        and load(p).get("resolution_freeze_locks", {}).get("may_continue_reliance_from_resolution") is False
        and load(p).get("resolution_freeze_locks", {}).get("may_increment_live_floor_from_resolution") is False
        and load(p).get("resolution_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and load(p).get("resolution_freeze_locks", {}).get("remedy_silence_counts_as_waiver") is False
        and load(p).get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and load(p).get("decision", {}).get("may_upgrade_reliance") is False
        and load(p).get("decision", {}).get("may_increment_live_floor") is False
        for p in late_change_remedy_resolution_paths
    )
    live_late_change_remedy_resolution_count = sum(1 for p in late_change_remedy_resolution_paths if load(p).get("remedy_context", {}).get("live_late_signal_present") is True)
    late_change_remedy_execution_lock_ok = bool(late_change_remedy_execution_paths) and all(
        load(p).get("no_direct_floor_effect") is True
        and load(p).get("execution_freeze_locks", {}).get("may_continue_published_snapshot_from_execution") is False
        and load(p).get("execution_freeze_locks", {}).get("may_continue_reliance_from_execution") is False
        and load(p).get("execution_freeze_locks", {}).get("may_increment_live_floor_from_execution") is False
        and load(p).get("execution_freeze_locks", {}).get("manual_publication_override_allowed") is False
        and load(p).get("execution_freeze_locks", {}).get("execution_silence_counts_as_completion") is False
        and load(p).get("decision", {}).get("may_publish_or_continue_snapshot") is False
        and load(p).get("decision", {}).get("may_upgrade_reliance") is False
        and load(p).get("decision", {}).get("may_increment_live_floor") is False
        for p in late_change_remedy_execution_paths
    )
    live_late_change_remedy_execution_count = sum(1 for p in late_change_remedy_execution_paths if load(p).get("execution_context", {}).get("live_late_signal_present") is True)

    checks = [
        {
            "check_id": "computed-floor-zero",
            "passed": floor.get("independent_receipts_present") == 0 and not floor.get("eligible_live_imports"),
            "severity": "critical",
            "observed": f"independent_receipts_present={floor.get('independent_receipts_present')} eligible={floor.get('eligible_live_imports')}",
            "expected": "zero live receipts and no eligible archive imports until a genuine live counterparty artifact passes all gates",
            "failure_effect": "block reliance upgrade and rerun compute_live_receipt_floor.py",
        },
        {
            "check_id": "fieldkit-not-receipt",
            "passed": fieldkit_ok,
            "severity": "critical",
            "observed": "fieldkit records raw slots and zero reliance limits" if fieldkit_ok else "fieldkit missing or reliance limits unsafe",
            "expected": "fieldkit_state=ready-no-live-artifact with all raw slots blocking if missing/failed",
            "failure_effect": "do not create response/intake/import records from a live artifact",
        },
        {
            "check_id": "no-disallowed-positive-archive-gates",
            "passed": not disallowed,
            "severity": "critical",
            "observed": ", ".join(disallowed) if disallowed else "no non-live positive import gates found in archive examples",
            "expected": "no import_allowed_to_live_floor=true outside strict live-counterparty provenance",
            "failure_effect": "remove or quarantine the gate before packaging",
        },
        {
            "check_id": "failed-gate-summary-present",
            "passed": snap.get("mismatch_checks", {}).get("failed_gate_public_summary_present_for_exclusions") is True,
            "severity": "high",
            "observed": str(snap.get("mismatch_checks", {}).get("failed_gate_public_summary_present_for_exclusions")),
            "expected": "every current exclusion has failed-gate public summary path",
            "failure_effect": "publish or repair failed-gate summaries before any import attempt",
        },

        {
            "check_id": "floor-recompute-receipt-publication-lock",
            "passed": floor_recompute_receipt_lock_ok,
            "severity": "critical",
            "observed": f"floor_recompute_receipts={len(floor_recompute_receipt_paths)}",
            "expected": "computed snapshot publication requires a floor recompute receipt that hashes fresh replay and blocks manual/stale reliance upgrades",
            "failure_effect": "block floor publication and rerun tools/audit_live_receipt_floor_recompute_receipt.py",
        },

        {
            "check_id": "cryptographic-adapter-not-boolean",
            "passed": bool(crypto_adapter_paths) and any(p.name.endswith("positive-control.json") for p in crypto_adapter_paths) and snap.get("mismatch_checks", {}).get("verified_live_crypto_adapters_present") is False,
            "severity": "critical",
            "observed": f"crypto_adapters={len(crypto_adapter_paths)} verified_live={snap.get('mismatch_checks', {}).get('verified_live_crypto_adapters_present')}",
            "expected": "verifier-adapter controls exist, but no positive-control or asserted boolean may create live-floor credit absent live-evidence import gate",
            "failure_effect": "block any live import gate that relies on signature_verified or timestamp_independent without adapter evidence",
        },
        {
            "check_id": "leap-pre-response-lock",
            "passed": leap_ok,
            "severity": "critical",
            "observed": "LEAP locks response/intake/import/live-floor delta" if leap_ok else "LEAP missing or downstream locks unsafe",
            "expected": "ready-no-live-artifact packet with raw payload, adapter, independence, protocol-boundary, and failed-gate locks before response creation",
            "failure_effect": "do not create response/intake/import records from the first live-looking artifact",
        },


        {
            "check_id": "custody-gate-not-custody",
            "passed": custody_gate_ok,
            "severity": "critical",
            "observed": f"custody_gate_paths={len(custody_gate_paths)} latest={custody_gate_paths[-1].name if custody_gate_paths else 'missing'}",
            "expected": "custody authority gate may authorize preparation of a separate custody record but may not create custody, response, intake, import, or live-floor credit",
            "failure_effect": "block custody record preparation and rerun custody gate audit",
        },
        {
            "check_id": "custody-record-response-only-lock",
            "passed": custody_response_only_ok,
            "severity": "critical",
            "observed": f"custody_record_paths={len(custody_paths)}",
            "expected": "custody records may authorize response preparation only; intake/import/floor remain blocked until later gates pass",
            "failure_effect": "quarantine custody record and rerun tools/audit_counterparty_custody_response_lock.py",
        },

        {
            "check_id": "response-gate-intake-import-lock",
            "passed": response_gate_lock_ok,
            "severity": "critical",
            "observed": f"response_gate_paths={len(response_gate_paths)}",
            "expected": "response verification gates may allow response-record preparation only; intake, import, and live-floor delta remain locked",
            "failure_effect": "block response record preparation and rerun tools/audit_external_receipt_response_verification_gate.py",
        },


        {
            "check_id": "intake-conversion-gate-import-floor-lock",
            "passed": intake_conversion_gate_lock_ok,
            "severity": "critical",
            "observed": f"intake_conversion_gate_paths={len(intake_conversion_gate_paths)}",
            "expected": "intake conversion gates may allow intake-record preparation only; import and live-floor delta remain locked",
            "failure_effect": "block intake record preparation and rerun tools/audit_external_receipt_intake_conversion_gate.py",
        },

        {
            "check_id": "import-readiness-gate-floor-lock",
            "passed": import_readiness_gate_lock_ok,
            "severity": "critical",
            "observed": f"import_readiness_gate_paths={len(import_readiness_gate_paths)}",
            "expected": "import readiness gates may allow actual import-gate preparation only; live-floor delta remains locked until actual import gate plus verifier adapter plus floor activation plus computed-floor recomputation",
            "failure_effect": "block actual import gate preparation and rerun tools/audit_external_receipt_import_readiness_gate.py",
        },

        {
            "check_id": "floor-activation-compute-only-lock",
            "passed": floor_activation_lock_ok,
            "severity": "critical",
            "observed": f"activation_record_paths={len(activation_record_paths)}",
            "expected": "floor activation records may admit an actual import gate to computed-floor evaluation only; they cannot manually increment the floor or satisfy quorum by themselves",
            "failure_effect": "exclude actual import gate and rerun tools/audit_live_receipt_floor_activation_record.py",
        },

        {
            "check_id": "quorum-participation-recompute-lock",
            "passed": quorum_participation_lock_ok,
            "severity": "critical",
            "observed": f"quorum_participation_record_paths={len(quorum_participation_record_paths)}",
            "expected": "quorum participation records may admit a gate to independence discount only; they cannot update the floor, satisfy cross-critical quorum, or upgrade reliance by themselves",
            "failure_effect": "exclude actual import gate and rerun tools/audit_live_receipt_quorum_participation_record.py",
        },

        {
            "check_id": "publication-rollback-adjudication-lock",
            "passed": publication_rollback_lock_ok,
            "severity": "critical",
            "observed": f"publication_rollback_adjudication_paths={len(publication_rollback_paths)}",
            "expected": "post-recompute publication continuation requires rollback adjudication; late challenge/rollback/supersession reopens publication and cannot increment floor",
            "failure_effect": "block continued floor publication and rerun tools/audit_live_receipt_publication_rollback_adjudication.py",
        },
        {
            "check_id": "late-change-ingress-publication-freeze-lock",
            "passed": late_change_ingress_lock_ok and opened_late_change_ingress_count == 0,
            "severity": "critical",
            "observed": f"late_change_ingress_paths={len(late_change_ingress_paths)} opened={opened_late_change_ingress_count}",
            "expected": "late-change ingress records capture and route late signals only; any live late signal freezes publication and forces recompute/adjudication rerun",
            "failure_effect": "block continued floor publication and rerun tools/audit_live_receipt_late_change_ingress_record.py",
        },
        {
            "check_id": "late-change-notice-dispatch-remedy-lock",
            "passed": late_change_notice_dispatch_lock_ok and live_late_change_notice_dispatch_count == 0,
            "severity": "critical",
            "observed": f"late_change_notice_dispatch_paths={len(late_change_notice_dispatch_paths)} live_signal_dispatches={live_late_change_notice_dispatch_count}",
            "expected": "late-change notice dispatch records prove affected-party notice/remedy routing only; they cannot continue publication, waive silence, or change floor",
            "failure_effect": "block continued publication and rerun tools/audit_live_receipt_late_change_notice_dispatch_record.py",
        },

        {
            "check_id": "late-change-remedy-resolution-recompute-lock",
            "passed": late_change_remedy_resolution_lock_ok and live_late_change_remedy_resolution_count == 0,
            "severity": "critical",
            "observed": f"late_change_remedy_resolution_paths={len(late_change_remedy_resolution_paths)} live_signal_resolutions={live_late_change_remedy_resolution_count}",
            "expected": "late-change remedy resolution records close or block remedy windows only; they cannot continue publication, waive silence, or change floor",
            "failure_effect": "block publication continuation and rerun tools/audit_live_receipt_late_change_remedy_resolution_record.py plus publication rollback adjudication",
        },
        {
            "check_id": "late-change-remedy-execution-completion-lock",
            "passed": late_change_remedy_execution_lock_ok and live_late_change_remedy_execution_count == 0,
            "severity": "critical",
            "observed": f"late_change_remedy_execution_paths={len(late_change_remedy_execution_paths)} live_signal_executions={live_late_change_remedy_execution_count}",
            "expected": "late-change remedy execution records complete or block ordered corrective actions only; they cannot continue publication, count silence as completion, or change floor",
            "failure_effect": "block publication continuation and rerun tools/audit_live_receipt_late_change_remedy_execution_record.py plus publication rollback adjudication",
        },

        {
            "check_id": "admission-graph-no-parallel-path",
            "passed": bool(admission_graph_paths) and all(c.get("passed") is True for c in load(admission_graph_paths[-1]).get("bypass_checks", [])) and load(admission_graph_paths[-1]).get("live_path_state", {}).get("downstream_creation_blocked") is True,
            "severity": "critical",
            "observed": f"admission_graphs={len(admission_graph_paths)} latest={admission_graph_paths[-1].name if admission_graph_paths else 'missing'}",
            "expected": "LEAP/custody/response/intake/import/computed-floor graph exists and blocks parallel downstream creation while no live artifact exists",
            "failure_effect": "block response, intake, import, and live-floor claim until graph violations are resolved",
        },

        {
            "check_id": "cross-critical-quorum-stayed",
            "passed": floor.get("cross_critical_quorum_satisfied") is False and floor.get("reliance_effect") == "stayed",
            "severity": "critical",
            "observed": f"quorum={floor.get('cross_critical_quorum_satisfied')} reliance={floor.get('reliance_effect')}",
            "expected": "cross-critical quorum false and reliance stayed",
            "failure_effect": "rollback any narrative or ledger overclaim",
        },
    ]
    return {
        "report_id": f"AIIR-2026-artifact-import-invariant-{REV}",
        "schema_version": "artifact-import-invariant-report-v0.1",
        "created_at": CREATED_AT,
        "revision": REV,
        "generated_by_tool": "tools/build_artifact_import_invariant_report.py",
        "computed_snapshot_ref": f"examples/live-receipt-floor-computed-snapshot-{REV}.json",
        "fieldkit_ref": fieldkit_paths[-1].relative_to(ROOT).as_posix() if fieldkit_paths else "missing",
        "archive_floor": {
            "independent_receipts_present": floor.get("independent_receipts_present"),
            "eligible_live_imports": floor.get("eligible_live_imports"),
            "live_classes_satisfied": floor.get("live_classes_satisfied"),
            "missing_live_classes": floor.get("missing_live_classes"),
            "cross_critical_quorum_satisfied": floor.get("cross_critical_quorum_satisfied"),
            "reliance_effect": floor.get("reliance_effect"),
        },
        "invariant_checks": checks,
        "source_scans": {
            "import_gate_paths": [p.relative_to(ROOT).as_posix() for p in import_gate_paths],
            "custody_gate_paths": [p.relative_to(ROOT).as_posix() for p in custody_gate_paths],
            "custody_record_paths": [p.relative_to(ROOT).as_posix() for p in custody_paths],
            "response_gate_paths": [p.relative_to(ROOT).as_posix() for p in response_gate_paths],
            "intake_conversion_gate_paths": [p.relative_to(ROOT).as_posix() for p in intake_conversion_gate_paths],
            "import_readiness_gate_paths": [p.relative_to(ROOT).as_posix() for p in import_readiness_gate_paths],
            "activation_record_paths": [p.relative_to(ROOT).as_posix() for p in activation_record_paths],
            "quorum_participation_record_paths": [p.relative_to(ROOT).as_posix() for p in quorum_participation_record_paths],
            "floor_recompute_receipt_paths": [p.relative_to(ROOT).as_posix() for p in floor_recompute_receipt_paths],
            "publication_rollback_adjudication_paths": [p.relative_to(ROOT).as_posix() for p in publication_rollback_paths],
            "late_change_ingress_paths": [p.relative_to(ROOT).as_posix() for p in late_change_ingress_paths],
            "late_change_notice_dispatch_paths": [p.relative_to(ROOT).as_posix() for p in late_change_notice_dispatch_paths],
            "late_change_remedy_resolution_paths": [p.relative_to(ROOT).as_posix() for p in late_change_remedy_resolution_paths],
            "late_change_remedy_execution_paths": [p.relative_to(ROOT).as_posix() for p in late_change_remedy_execution_paths],
            "fieldkit_paths": [p.relative_to(ROOT).as_posix() for p in fieldkit_paths],
            "computed_snapshot_paths": [p.relative_to(ROOT).as_posix() for p in snapshot_paths],
            "cryptographic_adapter_paths": [p.relative_to(ROOT).as_posix() for p in crypto_adapter_paths],
            "live_evidence_acquisition_packet_paths": [p.relative_to(ROOT).as_posix() for p in acquisition_paths],
            "live_artifact_admission_graph_paths": [p.relative_to(ROOT).as_posix() for p in admission_graph_paths],
            "disallowed_positive_archive_paths": disallowed,
        },
        "decision": {
            "may_import_now": False,
            "may_upgrade_reliance": False,
            "next_action": "Collect a genuine live counterparty raw artifact package and run evidence drop, pilot, candidate challenge, custody authority gate, response-only custody, response verification gate, response record, then intake conversion gate, intake record, and import readiness gate, actual import gate, and floor activation record, quorum participation record, and floor recompute receipt before any computed-floor publication, publication rollback adjudication, late-change notice dispatch, remedy resolution, remedy execution, or reliance movement.",
            "blocked_actions": [
                "fieldkit or checklist counted as receipt",
                "response created before response verification gate",
                "intake created before intake conversion gate",
                "actual import gate prepared before import readiness gate",
                "computed floor updated before live-receipt-floor activation and quorum participation replay",
                "hash match treated as class-specific authority",
                "signature_verified or timestamp_independent boolean treated as verified adapter output",
                "manual import/quorum override of computed floor",
                "computed snapshot published without floor recompute receipt",
                "published floor posture continued after late challenge without publication rollback adjudication",
                "late revocation, supersession, correction, or hash mismatch handled as an informal off-ledger note or silent freeze without affected-party notice",
                "late-change notice treated as remedy resolution before remedy/appeal window closure",
                "late-change remedy resolution treated as executed corrective action",
                "protocol/tool/agent output used as raw custody or response authorization before LEAP/custody slots pass",
                "correlated counterparty candidates counted as independent receipts",
                "single class-local import treated as cross-critical quorum",
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build()
    if args.check:
        path = ROOT / "examples" / f"artifact-import-invariant-report-{REV}.json"
        existing = load(path)
        if existing != report:
            raise SystemExit(f"artifact import invariant report mismatch: {path.relative_to(ROOT)}")
        print("build_artifact_import_invariant_report: OK")
        return
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
