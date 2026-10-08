#!/usr/bin/env python3
"""Audit the candidate challenge disposition layer.

This audit closes a risky seam: a candidate challenge report can be open while a
later operator tries to pass a raw `--challenge-status closed-*` override into
the custody gate. A separate human-reviewed disposition record is now required
before any closed challenge status may be consumed by the custody authority gate.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SCHEMA_REL = "schemas/candidate-challenge-disposition-record.schema.json"
RECORD_REL = f"examples/candidate-challenge-disposition-record-{REV}-open-stayed.json"
CHALLENGE_REL = f"examples/live-artifact-candidate-challenge-report-{REV}-synthetic-pending.json"
CUSTODY_GATE_REL = f"examples/counterparty-artifact-custody-gate-{REV}-pending-challenge.json"
NORMALIZATION_REL = f"examples/counterparty-artifact-normalization-decision-{REV}-pre-dispatch.json"
CREATED_AT = "2026-06-16T19:06:00Z"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel_or_path):
    path = Path(rel_or_path)
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))



def make_positive_binder(template: dict, rev: str) -> dict:
    binder = copy.deepcopy(template)
    binder["binder_id"] = f"CAEB-2026-{rev}-candidate-disposition-positive-control"
    binder["binder_state"] = "verified-for-custody-gate"
    binder["counterparty_org_id"] = "org:synthetic-counterparty"
    binder["dependency_group_id"] = "dep:synthetic-independent"
    for key in binder["evidence_refs"]:
        source_type = "human-confirmed-log"
        if key == "verifier_adapter":
            source_type = "verifier-adapter"
        elif key == "independent_timestamp":
            source_type = "independent-timestamp"
        elif key in {"nonhost_retention", "sealed_public_parity"}:
            source_type = "sealed-vault"
        elif key == "authority_limitations_publication":
            source_type = "policy-publication"
        binder["evidence_refs"][key] = {
            "present": True,
            "ref": f"synthetic-positive-control:{key}",
            "source_type": source_type,
            "human_reviewed": True,
            "can_satisfy_custody_authority": True,
        }
    binder["decision"].update({
        "authority_evidence_complete": True,
        "receipt_class_authority_scoped": True,
        "may_feed_custody_authority_gate": True,
        "reason": "Synthetic positive control only: authority evidence refs are present and manually reviewed; binder may feed custody gate but creates no custody or downstream reliance.",
    })
    binder["downstream_locks"]["custody_gate_may_consume_binder"] = True
    binder["authority_limitations"] = ["synthetic positive control only; not an actual live receipt"]
    return binder

def validate(schema_rel, obj_or_path, label):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    obj = load(obj_or_path) if isinstance(obj_or_path, (str, Path)) else obj_or_path
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails {schema_rel}: {errors[0].message}")


schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(SCHEMA_REL, RECORD_REL, RECORD_REL)

if record.get("revision") != REV or record.get("no_live_floor_effect") is not True:
    raise SystemExit("candidate disposition revision/no-floor mismatch")
if record.get("source_challenge_report_ref") != CHALLENGE_REL:
    raise SystemExit("candidate disposition is not bound to current challenge report")
if record.get("source_normalization_decision_ref") != NORMALIZATION_REL:
    raise SystemExit("candidate disposition is not bound to current normalization decision")

challenge = load(CHALLENGE_REL)
normalization = load(NORMALIZATION_REL)
if challenge.get("revision") != REV or challenge.get("no_live_floor_effect") is not True:
    raise SystemExit("source candidate challenge is stale or has floor effect")
if normalization.get("revision") != REV or normalization.get("no_live_floor_effect") is not True:
    raise SystemExit("source normalization decision is stale or has floor effect")
if record["candidate_challenge_snapshot"].get("challenge_report_id") != challenge.get("challenge_report_id"):
    raise SystemExit("candidate disposition snapshot does not bind challenge id")

if record.get("disposition_state") != "challenge-open-stayed":
    raise SystemExit("checked-in candidate disposition should stay open, not close challenge")
if record.get("decision", {}).get("may_feed_custody_authority_gate") is not False:
    raise SystemExit("open candidate disposition must not feed custody authority gate")
if record.get("decision", {}).get("challenge_status_effective") != "open":
    raise SystemExit("open candidate disposition must preserve open challenge status")
locks = record.get("downstream_locks", {})
for key in [
    "custody_gate_may_consume_disposition",
    "custody_record_created_by_disposition",
    "response_creation_allowed",
    "intake_creation_allowed",
    "import_gate_creation_allowed",
    "live_floor_delta_allowed",
    "silence_or_elapsed_time_can_close_challenge",
    "automated_ack_can_close_challenge",
    "protocol_output_can_close_challenge",
    "redacted_copy_can_close_challenge",
]:
    if locks.get(key) is not False:
        raise SystemExit(f"candidate disposition lock must be false: {key}")

prohibited = " ".join(record.get("decision", {}).get("prohibited_inferences", [])).lower()
for term in ["custody", "elapsed", "silence", "automated", "protocol", "redacted", "operator", "response", "intake", "live floor", "status"]:
    if term not in prohibited:
        raise SystemExit(f"candidate disposition prohibited inference missing term: {term}")

# The current custody gate must expose the new disposition seam and not consume it.
gate = load(CUSTODY_GATE_REL)
if gate.get("revision") != REV or gate.get("no_live_floor_effect") is not True:
    raise SystemExit("current custody gate is stale or has floor effect")
ch_disp = gate.get("challenge_disposition", {})
if ch_disp.get("may_feed_custody_authority_gate") is not False or ch_disp.get("raw_status_override_used") is not False:
    raise SystemExit("current pending custody gate should not consume a disposition or raw override")

# Schema must reject closure by silence, automated ack, protocol output, or redacted-only copy.
if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)

    def expect_invalid(mut, label):
        if not list(validator.iter_errors(mut)):
            raise SystemExit(f"candidate disposition schema failed to reject {label}")

    mut = copy.deepcopy(record)
    mut["disposition_state"] = "closed-no-objection-affirmative"
    mut["closure_evidence"]["silence_elapsed"] = True
    mut["decision"]["challenge_status_effective"] = "closed-no-objection"
    mut["decision"]["may_feed_custody_authority_gate"] = True
    mut["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    expect_invalid(mut, "silence-as-no-objection")

    mut = copy.deepcopy(record)
    mut["disposition_state"] = "closed-no-objection-affirmative"
    mut["closure_evidence"].update({
        "automated_ack_only": True,
        "affirmative_counterparty_message_present": True,
        "manual_counterparty_contact_confirmed": True,
        "request_trace_confirmed": True,
        "counterparty_identity_verified": True,
        "subject_or_representative_authority_verified": True,
        "receipt_class_authority_scoped": True,
        "authority_limitations_published": True,
        "independent_timestamp_or_log_ref": "timestamp:synthetic",
    })
    mut["decision"]["challenge_status_effective"] = "closed-no-objection"
    mut["decision"]["may_feed_custody_authority_gate"] = True
    mut["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    expect_invalid(mut, "automated-ack closure")

    mut = copy.deepcopy(record)
    mut["disposition_state"] = "closed-no-objection-affirmative"
    mut["closure_evidence"].update({
        "protocol_or_tool_output_only": True,
        "affirmative_counterparty_message_present": True,
        "manual_counterparty_contact_confirmed": True,
        "request_trace_confirmed": True,
        "counterparty_identity_verified": True,
        "subject_or_representative_authority_verified": True,
        "receipt_class_authority_scoped": True,
        "authority_limitations_published": True,
        "independent_timestamp_or_log_ref": "timestamp:synthetic",
    })
    mut["decision"]["challenge_status_effective"] = "closed-no-objection"
    mut["decision"]["may_feed_custody_authority_gate"] = True
    mut["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    expect_invalid(mut, "protocol-output closure")

    mut = copy.deepcopy(record)
    mut["disposition_state"] = "closed-no-objection-affirmative"
    mut["closure_evidence"].update({
        "redacted_copy_only": True,
        "affirmative_counterparty_message_present": True,
        "manual_counterparty_contact_confirmed": True,
        "request_trace_confirmed": True,
        "counterparty_identity_verified": True,
        "subject_or_representative_authority_verified": True,
        "receipt_class_authority_scoped": True,
        "authority_limitations_published": True,
        "independent_timestamp_or_log_ref": "timestamp:synthetic",
    })
    mut["decision"]["challenge_status_effective"] = "closed-no-objection"
    mut["decision"]["may_feed_custody_authority_gate"] = True
    mut["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    expect_invalid(mut, "redacted-copy closure")

# Tool seam: raw closed challenge status without disposition must remain blocked.
with tempfile.TemporaryDirectory(prefix="ai-personhood-disposition-gate-") as td:
    tmp = Path(td)
    raw_out = tmp / "raw-override"
    raw_cmd = [
        sys.executable, str(ROOT / "tools" / "prepare_custody_authority_gate.py"),
        "--challenge-report", str(ROOT / CHALLENGE_REL),
        "--output-dir", str(raw_out),
        "--gate-id", f"{REV}-raw-status-override",
        "--created-at", CREATED_AT,
        "--challenge-status", "closed-rejected",
        "--manual-counterparty-contact-confirmed",
        "--request-trace-confirmed",
        "--subject-or-representative-authority-verified",
        "--receipt-class", "result-return",
        "--counterparty-org-id", "org:synthetic-counterparty",
        "--dependency-group-id", "dep:synthetic-independent",
        "--authority-basis", "synthetic audit authority only",
        "--authority-scope", "result-return",
        "--authority-limitation", "synthetic audit only",
        "--verifier-adapter-ref", "adapter:synthetic",
        "--independent-timestamp-ref", "timestamp:synthetic",
        "--nonhost-retention-ref", "nonhost:synthetic",
        "--sealed-public-parity-ref", "parity:synthetic",
        "--redaction-boundary-ref", "redaction:synthetic",
        "--dependency-group-independence-checked",
        "--authority-limitations-published",
    ]
    raw_proc = subprocess.run(raw_cmd, check=True, capture_output=True, text=True)
    raw_gate = load(Path(raw_proc.stdout.strip()))
    validate("schemas/counterparty-artifact-custody-gate.schema.json", Path(raw_proc.stdout.strip()), "raw override custody gate")
    if raw_gate.get("gate_state") != "blocked-missing-authority":
        raise SystemExit("raw closed challenge status override must not open custody gate")
    if raw_gate.get("challenge_disposition", {}).get("status_override_without_disposition_blocked") is not True:
        raise SystemExit("raw override gate did not record disposition block")

    # Positive control: with a valid disposition, custody gate may authorize only preparation of a separate custody record.
    eligible_disp = copy.deepcopy(record)
    eligible_disp["disposition_record_id"] = f"LACD-2026-{REV}-synthetic-objection-rejected"
    eligible_disp["disposition_state"] = "closed-objection-rejected-after-review"
    eligible_disp["closure_evidence"].update({
        "affirmative_counterparty_message_present": True,
        "manual_counterparty_contact_confirmed": True,
        "request_trace_confirmed": True,
        "counterparty_identity_verified": True,
        "subject_or_representative_authority_verified": True,
        "receipt_class_authority_scoped": True,
        "authority_limitations_published": True,
        "independent_timestamp_or_log_ref": "timestamp:synthetic-disposition",
        "objection_received": True,
        "objection_reviewed_by_human": True,
        "objection_review_result": "rejected",
        "automated_ack_only": False,
        "protocol_or_tool_output_only": False,
        "redacted_copy_only": False,
        "silence_elapsed": False,
        "closure_evidence_refs": ["synthetic-audit-only:counterparty-objection-review"],
    })
    eligible_disp["decision"].update({
        "challenge_status_effective": "closed-rejected",
        "may_feed_custody_authority_gate": True,
        "custody_gate_consumption_reason": "synthetic positive control disposition supplies reviewed objection rejection and may feed the custody authority gate",
        "reason": "Synthetic positive control only: a human-reviewed objection was rejected with request trace, identity, authority scope, published limitations, and timestamp support. This still creates no custody record or live-floor effect.",
    })
    eligible_disp["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    disp_path = tmp / "eligible-disposition.json"
    disp_path.write_text(json.dumps(eligible_disp, indent=2) + "\n", encoding="utf-8")
    validate(SCHEMA_REL, disp_path, "eligible synthetic disposition")

    positive_binder = make_positive_binder(load(f"examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json"), REV)
    positive_binder_path = tmp / "positive-authority-binder.json"
    positive_binder_path.write_text(json.dumps(positive_binder, indent=2) + "\n", encoding="utf-8")
    validate("schemas/custody-authority-evidence-binder.schema.json", positive_binder_path, "positive synthetic authority binder")

    eligible_out = tmp / "eligible-gate"
    eligible_cmd = raw_cmd.copy()
    eligible_cmd[eligible_cmd.index("--output-dir") + 1] = str(eligible_out)
    eligible_cmd[eligible_cmd.index("--gate-id") + 1] = f"{REV}-disposition-bound-eligible"
    # Remove raw challenge-status; disposition supplies effective status.
    idx = eligible_cmd.index("--challenge-status")
    del eligible_cmd[idx:idx+2]
    eligible_cmd.extend(["--challenge-disposition-record", str(disp_path)])
    eligible_cmd.extend(["--authority-evidence-binder", str(positive_binder_path)])
    eligible_proc = subprocess.run(eligible_cmd, check=True, capture_output=True, text=True)
    eligible_gate = load(Path(eligible_proc.stdout.strip()))
    validate("schemas/counterparty-artifact-custody-gate.schema.json", Path(eligible_proc.stdout.strip()), "disposition-bound custody gate")
    if eligible_gate.get("gate_state") != "eligible-for-custody-record":
        raise SystemExit("valid disposition did not authorize custody-record preparation")
    if eligible_gate.get("downstream_locks", {}).get("may_prepare_counterparty_artifact_custody_record") is not True:
        raise SystemExit("valid disposition gate did not prepare custody handoff")
    for key in ["custody_record_admitted", "response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed"]:
        if eligible_gate.get("downstream_locks", {}).get(key) is not False:
            raise SystemExit(f"valid disposition gate incorrectly unlocked downstream {key}")

required_fixtures = {
    "NF-CUSTODY-2026-0016": "fixtures/negative-tests/candidate-disposition-silence-as-no-objection.json",
    "NF-CUSTODY-2026-0017": "fixtures/negative-tests/candidate-disposition-auto-ack-closes-challenge.json",
    "NF-PROTOCOL-PIVOT-2026-0009": "fixtures/negative-tests/candidate-disposition-protocol-output-closes-challenge.json",
}
for fid, rel in required_fixtures.items():
    fixture = load(rel)
    if fixture.get("fixture_id") != fid:
        raise SystemExit(f"fixture id mismatch for {rel}")
    if "candidate-challenge-disposition-record" not in fixture.get("target_filings", []):
        raise SystemExit(f"fixture does not target candidate disposition: {rel}")
    if fixture.get("severity") != "critical":
        raise SystemExit(f"candidate disposition fixture must be critical: {rel}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required_fixtures) <= suite_ids:
    raise SystemExit("fixture suite missing candidate disposition fixtures")
if not set(required_fixtures) <= report_ids:
    raise SystemExit("fixture report missing candidate disposition fixtures")

print("audit_candidate_challenge_disposition: OK")
