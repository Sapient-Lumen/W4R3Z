#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from crypto_adapter_lib import load_verified_live_adapters
from live_floor_lib import REQUIRED_CLASSES, apply_independence_discount, eligible_import_gate

REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-18T08:27:00Z"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def all_json(root, prefix):
    return sorted((root / "examples").glob(prefix))


def challenge_exclusions(challenge_records):
    exclusions = []
    challenged_gate_ids = set()
    for data in challenge_records:
        cid = data.get("challenge_record_id", "unknown")
        floor = data.get("receipt_floor_effect", {})
        gate_ref = data.get("linked_import_gate")
        state = data.get("challenge_state")
        decision = data.get("decision", {})
        if state in {"rollback-required", "rollback-complete", "post-import-challenge"} or decision.get("challenge_upheld") is True:
            if gate_ref:
                challenged_gate_ids.add(gate_ref)
            exclusions.append({
                "source_ref": cid,
                "source_type": "receipt-import-challenge-rollback-record",
                "receipt_class": floor.get("challenged_receipt_class") or data.get("challenged_receipt_class", "unknown"),
                "exclusion_reason": f"challenge_state={state} live_floor_after_recompute={floor.get('live_floor_after_recompute')}",
                "failed_gate_summary_required": True,
            })
    return challenged_gate_ids, exclusions


def compute_from_records(root, rev, created_at, import_gate_records, challenge_records, input_scope, live_packet_floor=0, frontdoor_ok=True, stale_qrr=False, failed_gate_paths=None, verified_live_adapters=None, import_readiness_gates=None, activation_records=None, quorum_participation_records=None):
    challenged_gate_ids, exclusions = challenge_exclusions(challenge_records)
    verified_live_adapters = verified_live_adapters or {}
    import_readiness_gates = import_readiness_gates or {}
    activation_records = activation_records or {}
    quorum_participation_records = quorum_participation_records or {}
    candidate_register = []
    pre_discount_candidates = []
    for data in import_gate_records:
        decision = data.get("import_decision", {})
        gate_id = data.get("import_gate_id", "unknown")
        receipt_class = decision.get("imported_receipt_class") or data.get("receipt_class") or "unknown"
        ok, reason, candidate = eligible_import_gate(
            data,
            root=root,
            challenged_gate_ids=challenged_gate_ids,
            verified_live_adapters=verified_live_adapters,
            import_readiness_gates=import_readiness_gates,
            activation_records=activation_records,
            quorum_participation_records=quorum_participation_records,
        )
        if ok and candidate is not None:
            pre_discount_candidates.append(candidate)
            candidate_register.append(candidate.as_register_row("candidate", reason))
        else:
            exclusions.append({
                "source_ref": gate_id,
                "source_type": "actual-receipt-import-gate",
                "receipt_class": receipt_class,
                "exclusion_reason": reason[:600],
                "failed_gate_summary_required": True,
            })

    counted_candidates, discount_register = apply_independence_discount(pre_discount_candidates)
    for row in discount_register:
        if row.get("status") == "discounted":
            exclusions.append({
                "source_ref": row.get("source_ref", "unknown"),
                "source_type": "actual-receipt-import-gate",
                "receipt_class": row.get("receipt_class", "unknown"),
                "exclusion_reason": row.get("reason", "discounted by independence engine")[:600],
                "failed_gate_summary_required": True,
            })

    eligible = [c.gate_id for c in counted_candidates]
    classes = [c.receipt_class for c in counted_candidates]
    independent = len(counted_candidates)
    missing = [c for c in REQUIRED_CLASSES if c not in set(classes)]
    failed_gate_paths = failed_gate_paths or []
    failed_gate_ok = len(failed_gate_paths) > 0 and bool(exclusions)
    discount_applied = any(row.get("status") == "discounted" for row in discount_register)
    return {
        "snapshot_id": f"LRFCS-2026-live-floor-computed-{rev}",
        "schema_version": "live-receipt-floor-computed-snapshot-v0.1",
        "created_at": created_at,
        "revision": rev,
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "generated_by_tool": "tools/compute_live_receipt_floor.py",
        "input_scope": input_scope,
        "computation_rules": {
            "source_of_truth": "Computed snapshot overrides hand-edited quorum ledgers and public narratives.",
            "eligible_import_rule": "Only strict actual-live-import gates with live-counterparty collection context, clean provenance, external non-host retention, class-specific authority checks, a replayed import-readiness gate, a separate live-floor activation record, a quorum participation replay record, a verified cryptographic adapter bound to the gate, no direct host-correlation, no disqualifiers, and no upheld challenge may enter the candidate set.",
            "activation_rule": "Import-gate booleans do not create floor credit by themselves: the linked import-readiness gate must be replayed and a live-receipt-floor activation record must admit the gate to quorum participation while preserving no direct floor effect.",
            "quorum_participation_rule": "Floor activation is not enough: the live receipt quorum participation record must recheck duplicate, supersession, rollback/challenge, no-manual-quorum, and single-class-quorum blocks before the candidate enters independence discount and required-class recomputation.",
            "challenge_rule": "Pending or upheld challenges stay reliance and can reverse any claimed live-floor increment.",
            "class_local_rule": "A valid class-local import can satisfy only its receipt class unless all required live classes are recomputed as present.",
            "independence_discount_rule": "Before the floor is counted, candidates are discounted across dependency group, counterparty org, issuer key, host correlation, and receipt class; duplicate or correlated receipts remain evidence but are zero-weight for independent floor increments.",
            "manual_override_rule": "Narrative, request, checklist, dry-run, scenario projection, positive-control case, edited ledger fields, protocol success, provenance labels, or asserted booleans such as signature_verified carry zero archive live weight without passed import gates, verifier-adapter evidence, and independence discount.",
            "publication_rule": "The computed snapshot is not itself a reliance publication. A live-receipt-floor recompute receipt must hash this snapshot, compare it to a fresh engine replay, and keep reliance stayed unless the required-class vector is complete."
        },
        "computed_floor": {
            "live_floor_before": 0,
            "live_floor_delta": independent,
            "independent_receipts_present": independent,
            "eligible_live_imports": eligible,
            "candidate_live_imports_before_independence_discount": [c.gate_id for c in pre_discount_candidates],
            "live_classes_satisfied": sorted(set(classes)),
            "required_live_classes": REQUIRED_CLASSES,
            "missing_live_classes": missing,
            "dependency_groups_counted": sorted({c.dependency_group_id for c in counted_candidates}),
            "counterparty_orgs_counted": sorted({c.counterparty_org_id for c in counted_candidates}),
            "issuer_keys_counted": sorted({c.issuer_key_id for c in counted_candidates}),
            "independence_discount_register": discount_register,
            "live_quorum_satisfied": independent >= len(REQUIRED_CLASSES) and not missing,
            "cross_critical_quorum_satisfied": independent >= len(REQUIRED_CLASSES) and not missing,
            "reliance_effect": "ordinary-reliance" if independent >= len(REQUIRED_CLASSES) and not missing else "stayed",
        },
        "exclusion_register": exclusions,
        "mismatch_checks": {
            "live_packet_floor_matches": live_packet_floor == independent,
            "manual_ledger_override_detected": live_packet_floor != independent,
            "stale_report_detected": stale_qrr,
            "failed_gate_public_summary_present_for_exclusions": failed_gate_ok,
            "frontdoor_revision_matches": frontdoor_ok,
            "verified_live_crypto_adapters_present": bool(verified_live_adapters),
            "independence_discount_applied": discount_applied,
        },
        "decision": {
            "archive_live_floor_update_allowed": independent > 0,
            "may_upgrade_reliance": independent >= len(REQUIRED_CLASSES) and not missing,
            "next_live_action": "Collect a genuine non-host artifact via live evidence acquisition packet and rerun custody, cryptographic verifier adapter, envelope, response, intake conversion, intake, import readiness gate, import gate, floor activation record, quorum participation record, independence discount, challenge/rollback if contested, class-local replay, computed-floor snapshot, and floor recompute receipt.",
            "blocked_actions": [
                "manual live-floor override",
                "checklist treated as admission",
                "dry-run, fixture, or positive-control import counted as archive live receipt",
                "signature_verified or timestamp_independent JSON booleans counted without a verifier adapter",
                "actual-live-import counted without a replayed import-readiness gate, live-receipt-floor activation record, and quorum participation record",
                "computed-floor snapshot published or relied upon without a floor recompute receipt",
                "protocol transport, A2A task state, MCP tool output, or provenance label treated as authority",
                "counterparty-, issuer-, class-, or dependency-correlated receipts counted as independent floor increments",
                "single class-local import treated as cross-critical quorum",
                "failed gate omitted from public shell",
            ],
        },
    }


def _index_import_readiness_gates(records):
    return {r.get("import_readiness_gate_id"): r for r in records if r.get("import_readiness_gate_id")}


def _index_activation_records(records):
    return {r.get("linked_import_gate_ref"): r for r in records if r.get("linked_import_gate_ref")}


def _index_quorum_participation_records(records):
    return {r.get("linked_import_gate_ref"): r for r in records if r.get("linked_import_gate_ref")}


def compute(root=ROOT, rev=REV, created_at=CREATED_AT):
    import_gate_paths = all_json(root, "actual-receipt-import-gate*.json")
    import_attempt_paths = all_json(root, "live-counterparty-import-attempt*.json")
    import_readiness_gate_paths = all_json(root, "external-receipt-import-readiness-gate*.json")
    activation_record_paths = all_json(root, "live-receipt-floor-activation-record*.json")
    quorum_participation_record_paths = all_json(root, "live-receipt-quorum-participation-record*.json")
    challenge_paths = all_json(root, "receipt-import-challenge-rollback-record*.json")
    class_replay_paths = all_json(root, "live-class-local-import-replay*.json")
    qrr_paths = all_json(root, "quorum-recomputation-report*.json")
    fgps_paths = all_json(root, "failed-gate-public-summary*.json")
    crypto_paths = all_json(root, "cryptographic-verifier-adapter-*.json")
    acquisition_paths = all_json(root, "live-evidence-acquisition-packet*.json")

    import_gate_records = [load(p) for p in import_gate_paths]
    import_readiness_gate_records = [load(p) for p in import_readiness_gate_paths]
    activation_records = [load(p) for p in activation_record_paths]
    quorum_participation_records = [load(p) for p in quorum_participation_record_paths]
    challenge_records = [load(p) for p in challenge_paths]
    verified_live_adapters = load_verified_live_adapters(root)
    live = load(root / "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
    live_packet_floor = live.get("receipt_floor", {}).get("independent_receipts_present", 0)
    frontdoor_ok = all(rev in (root / rel).read_text(encoding="utf-8")[:3500] for rel in ["README.md", "START_HERE.md", "docs/README.md"])
    stale_qrr = any(rev not in p.name and load(p).get("decision", {}).get("live_floor_delta", 0) != 0 for p in qrr_paths)
    input_scope = {
        "import_gate_paths": [p.relative_to(root).as_posix() for p in import_gate_paths],
        "import_attempt_paths": [p.relative_to(root).as_posix() for p in import_attempt_paths],
        "import_readiness_gate_paths": [p.relative_to(root).as_posix() for p in import_readiness_gate_paths],
        "activation_record_paths": [p.relative_to(root).as_posix() for p in activation_record_paths],
        "quorum_participation_record_paths": [p.relative_to(root).as_posix() for p in quorum_participation_record_paths],
        "challenge_record_paths": [p.relative_to(root).as_posix() for p in challenge_paths],
        "class_local_replay_paths": [p.relative_to(root).as_posix() for p in class_replay_paths],
        "quorum_report_paths": [p.relative_to(root).as_posix() for p in qrr_paths],
        "failed_gate_summary_paths": [p.relative_to(root).as_posix() for p in fgps_paths],
        "cryptographic_adapter_paths": [p.relative_to(root).as_posix() for p in crypto_paths],
        "live_evidence_acquisition_packet_paths": [p.relative_to(root).as_posix() for p in acquisition_paths],
    }
    return compute_from_records(
        root,
        rev,
        created_at,
        import_gate_records,
        challenge_records,
        input_scope,
        live_packet_floor,
        frontdoor_ok,
        stale_qrr,
        fgps_paths,
        verified_live_adapters,
        _index_import_readiness_gates(import_readiness_gate_records),
        _index_activation_records(activation_records),
        _index_quorum_participation_records(quorum_participation_records),
    )

def _control_verified_adapters(case):
    """Build synthetic verified-adapter records for quarantined control gates only.

    The positive-control harness must still prove that the live-floor engine can
    count strict eligible imports. Synthetic adapter records include independence
    fields so the same correlation-discount engine used for archive records is
    exercised in control mode. No adapter file is written, and compute() for the
    archive only loads verified live-evidence adapters from examples/.
    """
    adapters = {}
    for gate in case.get("import_gate_records", []):
        gate_id = gate.get("import_gate_id", "unknown")
        ref = gate.get("cryptographic_verifier_adapter_ref")
        decision = gate.get("import_decision", {})
        provenance = gate.get("source_provenance", {})
        receipt_class = decision.get("imported_receipt_class") or gate.get("receipt_class") or "unknown"
        if not ref:
            continue
        dep = provenance.get("dependency_group") or f"control-dependency-{gate_id}"
        org = provenance.get("counterparty_org_id") or f"control-org-{dep}"
        issuer = provenance.get("issuer_key_id") or f"control-key-{dep}"
        host = provenance.get("subject_host_org_id") or "control-subject-host"
        adapters[gate_id] = {
            "path": ROOT / ref,
            "record": {
                "payload": {
                    "linked_import_gate_id": gate_id,
                    "receipt_class": receipt_class,
                    "dependency_group_id": dep,
                    "counterparty_org_id": org,
                    "issuer_key_id": issuer,
                },
                "independence": {
                    "dependency_group_id": dep,
                    "counterparty_org_id": org,
                    "issuer_key_id": issuer,
                    "subject_host_org_id": host,
                    "counterparty_distinct_from_subject_host": org != host,
                    "issuer_distinct_from_subject_host": issuer != host,
                    "correlation_discount": provenance.get("correlation_discount", "none"),
                },
            },
        }
    return adapters



def _control_import_readiness_gates(case):
    gates = {}
    for gate in case.get("import_gate_records", []):
        gate_id = gate.get("import_gate_id", "unknown")
        readiness_ref = gate.get("linked_import_readiness_gate_ref") or f"CONTROL-READINESS-{gate_id}"
        decision = gate.get("import_decision", {})
        provenance = gate.get("source_provenance", {})
        receipt_class = decision.get("imported_receipt_class") or gate.get("receipt_class") or "unknown"
        gates[readiness_ref] = {
            "import_readiness_gate_id": readiness_ref,
            "gate_state": "eligible-for-import-gate",
            "linked_intake_record_ref": gate.get("source_intake_record_ref"),
            "linked_response_record_ref": gate.get("source_response_record_ref"),
            "linked_custody_record_ref": provenance.get("custody_record_ref"),
            "linked_live_evidence_acquisition_packet_ref": provenance.get("linked_live_evidence_acquisition_packet_ref"),
            "requested_receipt_class": receipt_class,
            "downstream_locks": {
                "may_prepare_actual_receipt_import_gate": True,
                "may_increment_live_floor": False,
                "live_floor_delta_allowed": False,
            },
            "decision": {
                "actual_import_gate_may_be_prepared": True,
                "can_increment_live_floor": False,
            },
            "no_live_floor_effect": True,
        }
    return gates


def _control_activation_records(case):
    records = {}
    for gate in case.get("import_gate_records", []):
        gate_id = gate.get("import_gate_id", "unknown")
        decision = gate.get("import_decision", {})
        provenance = gate.get("source_provenance", {})
        receipt_class = decision.get("imported_receipt_class") or gate.get("receipt_class") or "unknown"
        adapter_ref = gate.get("cryptographic_verifier_adapter_ref") or f"CONTROL-ADAPTER-{gate_id}"
        replay = {key: True for key in [
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
        ]}
        records[gate_id] = {
            "activation_record_id": f"LRFAR-2026-control-{gate_id}",
            "schema_version": "live-receipt-floor-activation-record-v0.1",
            "linked_import_gate_ref": gate_id,
            "linked_import_readiness_gate_ref": gate.get("linked_import_readiness_gate_ref"),
            "linked_cryptographic_verifier_adapter_ref": adapter_ref,
            "linked_live_evidence_acquisition_packet_ref": provenance.get("linked_live_evidence_acquisition_packet_ref"),
            "linked_custody_record_ref": provenance.get("custody_record_ref"),
            "requested_receipt_class": receipt_class,
            "activation_state": "eligible-for-floor-recompute",
            "replay_checks": replay,
            "floor_recompute_locks": {
                "may_enter_computed_floor_candidate_set": True,
                "manual_floor_increment_allowed": False,
                "computed_floor_recompute_required": True,
                "activation_record_can_satisfy_quorum_by_itself": False,
                "live_floor_delta_allowed_by_activation_record": False,
            },
            "decision": {
                "may_enter_computed_floor_candidate_set": True,
                "can_increment_live_floor_by_itself": False,
                "live_reliance_effect": "stayed-until-computed-floor",
            },
            "no_live_floor_effect": True,
        }
    return records




def _control_quorum_participation_records(case, activation_records):
    records = {}
    for gate in case.get("import_gate_records", []):
        gate_id = gate.get("import_gate_id", "unknown")
        activation = activation_records.get(gate_id, {})
        decision = gate.get("import_decision", {})
        provenance = gate.get("source_provenance", {})
        receipt_class = decision.get("imported_receipt_class") or gate.get("receipt_class") or "unknown"
        checks = {key: True for key in [
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
        ]}
        records[gate_id] = {
            "quorum_participation_record_id": f"LRQPR-2026-control-{gate_id}",
            "schema_version": "live-receipt-quorum-participation-record-v0.1",
            "created_at": CREATED_AT,
            "linked_import_gate_ref": gate_id,
            "linked_floor_activation_record_ref": activation.get("activation_record_id", f"LRFAR-2026-control-{gate_id}"),
            "linked_import_readiness_gate_ref": gate.get("linked_import_readiness_gate_ref"),
            "linked_cryptographic_verifier_adapter_ref": gate.get("cryptographic_verifier_adapter_ref"),
            "linked_challenge_or_rollback_refs": [],
            "requested_receipt_class": receipt_class,
            "participation_state": "eligible-for-independence-discount",
            "input_candidate_summary": {
                "import_gate_id": gate_id,
                "activation_record_id": activation.get("activation_record_id", f"LRFAR-2026-control-{gate_id}"),
                "activation_state": "eligible-for-floor-recompute",
                "import_readiness_gate_ref": gate.get("linked_import_readiness_gate_ref"),
                "cryptographic_adapter_ref": gate.get("cryptographic_verifier_adapter_ref"),
                "imported_receipt_class": receipt_class,
                "dependency_group": provenance.get("dependency_group", "missing"),
                "counterparty_org_id": provenance.get("counterparty_org_id", "missing"),
                "issuer_key_id": provenance.get("issuer_key_id", "missing"),
                "subject_host_org_id": provenance.get("subject_host_org_id", "missing"),
            },
            "quorum_replay_checks": checks,
            "quorum_locks": {
                "may_enter_independence_discount": True,
                "may_satisfy_cross_critical_quorum_by_itself": False,
                "manual_live_floor_update_allowed": False,
                "live_floor_delta_allowed_by_participation_record": False,
                "computed_floor_recompute_required": True,
            },
            "decision": {
                "may_enter_independence_discount": True,
                "can_upgrade_reliance_by_itself": False,
                "live_reliance_effect": "stayed-until-computed-floor",
                "reason": "Synthetic control quorum participation record admits gate to independence discount only.",
                "blocked_actions": ["manual quorum upgrade", "direct floor delta from participation"],
                "next_actions": ["run computed floor engine"],
            },
            "no_live_floor_effect": True,
        }
    return records


def evaluate_control_case(path):
    data = load(Path(path))
    results = []
    for case in data.get("cases", []):
        input_scope = {
            "import_gate_paths": [f"embedded-control:{case['case_id']}:import-gates"],
            "import_attempt_paths": [],
            "challenge_record_paths": [f"embedded-control:{case['case_id']}:challenges"] if case.get("challenge_records") else [],
            "class_local_replay_paths": [],
            "quorum_report_paths": [],
            "failed_gate_summary_paths": [f"embedded-control:{case['case_id']}:failed-gate-summary"],
            "cryptographic_adapter_paths": [f"embedded-control:{case['case_id']}:synthetic-cryptographic-adapters"],
            "import_readiness_gate_paths": [f"embedded-control:{case['case_id']}:synthetic-import-readiness-gates"],
            "activation_record_paths": [f"embedded-control:{case['case_id']}:synthetic-floor-activation-records"],
            "live_evidence_acquisition_packet_paths": [],
        }
        control_activation_records = _control_activation_records(case)
        snap = compute_from_records(
            ROOT,
            "control",
            CREATED_AT,
            case.get("import_gate_records", []),
            case.get("challenge_records", []),
            input_scope,
            live_packet_floor=case.get("expected", {}).get("independent_receipts_present", 0),
            frontdoor_ok=True,
            stale_qrr=False,
            failed_gate_paths=input_scope["failed_gate_summary_paths"],
            verified_live_adapters=_control_verified_adapters(case),
            import_readiness_gates=_control_import_readiness_gates(case),
            activation_records=control_activation_records,
            quorum_participation_records=_control_quorum_participation_records(case, control_activation_records),
        )
        observed = snap["computed_floor"]
        expected = case.get("expected", {})
        ok = True
        reasons = []
        for key in ["independent_receipts_present", "live_classes_satisfied", "missing_live_classes", "cross_critical_quorum_satisfied", "reliance_effect"]:
            if observed.get(key) != expected.get(key):
                ok = False
                reasons.append(f"{key}: observed={observed.get(key)!r} expected={expected.get(key)!r}")
        results.append({"case_id": case.get("case_id"), "ok": ok, "reasons": reasons, "observed": observed})
    return {"control_case_id": data.get("control_case_id"), "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--control-case")
    args = parser.parse_args()
    if args.control_case:
        result = evaluate_control_case(args.control_case)
        if not all(r["ok"] for r in result["results"]):
            raise SystemExit(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return
    snap = compute()
    if args.check:
        path = ROOT / "examples" / f"live-receipt-floor-computed-snapshot-{REV}.json"
        existing = load(path)
        if existing != snap:
            raise SystemExit(f"computed snapshot mismatch: {path.relative_to(ROOT)}")
        print("compute_live_receipt_floor: OK")
        return
    text = json.dumps(snap, indent=2) + "\n"
    if args.output:
        out = ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
        out.write_text(text, encoding="utf-8")
        print(out)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
