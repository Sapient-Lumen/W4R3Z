#!/usr/bin/env python3
"""Audit rev0216 custody-record response-only lock."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-16T19:06:00Z"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel_or_path):
    p = Path(rel_or_path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def make_positive_binder(template: dict, rev: str) -> dict:
    positive = json.loads(json.dumps(template))
    positive["binder_id"] = f"CAEB-2026-{rev}-custody-response-lock-positive-control"
    positive["binder_state"] = "verified-for-custody-gate"
    positive["counterparty_org_id"] = "org:synthetic-nonhost-counterparty"
    positive["dependency_group_id"] = "dep:synthetic-independent-request-trace"
    for key in positive["evidence_refs"]:
        source_type = "human-confirmed-log"
        if key == "verifier_adapter":
            source_type = "verifier-adapter"
        elif key == "independent_timestamp":
            source_type = "independent-timestamp"
        elif key in {"nonhost_retention", "sealed_public_parity"}:
            source_type = "sealed-vault"
        elif key == "authority_limitations_publication":
            source_type = "policy-publication"
        positive["evidence_refs"][key] = {
            "present": True,
            "ref": f"synthetic-positive-control:{key}",
            "source_type": source_type,
            "human_reviewed": True,
            "can_satisfy_custody_authority": True,
        }
    positive["decision"].update({
        "authority_evidence_complete": True,
        "receipt_class_authority_scoped": True,
        "may_feed_custody_authority_gate": True,
        "reason": "Synthetic positive control only: evidence-backed authority binder for custody response lock audit.",
    })
    positive["downstream_locks"]["custody_gate_may_consume_binder"] = True
    positive["authority_limitations"] = ["synthetic audit only; not an actual live receipt"]
    return positive

def make_eligible_disposition(template: dict, rev: str) -> dict:
    disp = copy.deepcopy(template)
    disp["disposition_record_id"] = f"LACD-2026-{rev}-custody-response-lock-positive-control"
    disp["disposition_state"] = "closed-objection-rejected-after-review"
    disp["closure_evidence"].update({
        "affirmative_counterparty_message_present": True,
        "manual_counterparty_contact_confirmed": True,
        "request_trace_confirmed": True,
        "counterparty_identity_verified": True,
        "subject_or_representative_authority_verified": True,
        "receipt_class_authority_scoped": True,
        "authority_limitations_published": True,
        "independent_timestamp_or_log_ref": "timestamp:synthetic",
        "objection_received": True,
        "objection_reviewed_by_human": True,
        "objection_review_result": "rejected",
        "closure_evidence_refs": ["synthetic-audit-only:reviewed-objection"],
    })
    disp["decision"].update({
        "challenge_status_effective": "closed-rejected",
        "may_feed_custody_authority_gate": True,
        "custody_gate_consumption_reason": "synthetic positive control disposition supplies reviewed objection rejection",
        "reason": "Synthetic positive control only: reviewed objection rejected; no custody record or live-floor effect created by disposition.",
    })
    disp["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    return disp

def validate(schema_rel, data_path):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{Path(data_path).name} fails {schema_rel}: {errors[0].message}")

schema_rel = "schemas/counterparty-artifact-custody-record.schema.json"
validate(schema_rel, ROOT / "examples/counterparty-artifact-custody-record-result-return-dryrun.json")
dryrun = load("examples/counterparty-artifact-custody-record-result-return-dryrun.json")
if not dryrun.get("linked_custody_gate_ref"):
    raise SystemExit("dry-run custody record lacks linked_custody_gate_ref after schema refactor")

with tempfile.TemporaryDirectory(prefix="ai-personhood-custody-response-lock-") as td:
    tmp = Path(td)
    source = tmp / "raw-counterparty-artifact.eml"
    secret = "SYNTHETIC_CUSTODY_RESPONSE_LOCK_PRIVATE_BYTES_REV0216_DO_NOT_PACKAGE"
    source.write_text(secret, encoding="utf-8")
    vault = tmp / "external-vault"
    pilot_out = tmp / "pilot-output"
    pilot_cmd = [
        sys.executable, str(ROOT / "tools" / "prepare_first_real_artifact_pilot.py"),
        "--input", str(source),
        "--drop-id", "rev0216-synthetic-custody-response-lock",
        "--output-dir", str(pilot_out),
        "--vault-root", str(vault),
        "--created-at", CREATED_AT,
        "--permit-leap-candidate",
        "--request-trace-present",
        "--counterparty-contact-present",
        "--nonhost-retention-present",
        "--sealed-public-parity-present",
        "--counterparty-org-id", "org:synthetic-nonhost-counterparty",
        "--dependency-group-id", "dep:synthetic-independent-request-trace",
    ]
    pilot_proc = subprocess.run(pilot_cmd, check=True, capture_output=True, text=True)
    pilot_report = Path(pilot_proc.stdout.strip())

    challenge_out = tmp / "challenge-output"
    challenge_cmd = [
        sys.executable, str(ROOT / "tools" / "prepare_candidate_challenge_packet.py"),
        "--pilot-report", str(pilot_report),
        "--vault-root", str(vault),
        "--output-dir", str(challenge_out),
        "--challenge-id", "rev0216-synthetic-response-lock",
        "--created-at", CREATED_AT,
    ]
    challenge_proc = subprocess.run(challenge_cmd, check=True, capture_output=True, text=True)
    challenge_path = Path(challenge_proc.stdout.strip())
    validate("schemas/live-artifact-candidate-challenge-report.schema.json", challenge_path)

    binder_template = load(f"examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json")
    positive_binder = make_positive_binder(binder_template, REV)
    positive_binder_path = tmp / "positive-authority-binder.json"
    positive_binder_path.write_text(json.dumps(positive_binder, indent=2) + "\n", encoding="utf-8")
    validate("schemas/custody-authority-evidence-binder.schema.json", positive_binder_path)

    disposition_template = load(f"examples/candidate-challenge-disposition-record-{REV}-open-stayed.json")
    eligible_disp = make_eligible_disposition(disposition_template, REV)
    generated_challenge = load(challenge_path)
    eligible_disp["source_challenge_report_ref"] = str(challenge_path)
    eligible_disp["candidate_challenge_snapshot"]["challenge_report_id"] = generated_challenge.get("challenge_report_id")
    eligible_disp_path = tmp / "eligible-disposition.json"
    eligible_disp_path.write_text(json.dumps(eligible_disp, indent=2) + "\n", encoding="utf-8")
    validate("schemas/candidate-challenge-disposition-record.schema.json", eligible_disp_path)

    gate_out = tmp / "gate-output"
    base_gate_cmd = [
        sys.executable, str(ROOT / "tools" / "prepare_custody_authority_gate.py"),
        "--challenge-report", str(challenge_path),
        "--output-dir", str(gate_out),
        "--gate-id", "rev0216-synthetic-response-lock",
        "--created-at", CREATED_AT,
        "--manual-counterparty-contact-confirmed",
        "--request-trace-confirmed",
        "--subject-or-representative-authority-verified",
        "--receipt-class", "result-return",
        "--counterparty-org-id", "org:synthetic-nonhost-counterparty",
        "--dependency-group-id", "dep:synthetic-independent-request-trace",
        "--authority-basis", "synthetic audit authority only",
        "--authority-scope", "result-return",
        "--authority-limitation", "synthetic audit only; not an actual live receipt",
        "--verifier-adapter-ref", "adapter:synthetic",
        "--independent-timestamp-ref", "timestamp:synthetic",
        "--nonhost-retention-ref", "nonhost:synthetic",
        "--sealed-public-parity-ref", "parity:synthetic",
        "--redaction-boundary-ref", "redaction:synthetic",
        "--dependency-group-independence-checked",
        "--authority-limitations-published",
        "--authority-evidence-binder", str(positive_binder_path),
    ]

    # Open challenge remains blocked and must produce only quarantined custody.
    blocked_proc = subprocess.run(base_gate_cmd, check=True, capture_output=True, text=True)
    blocked_gate = Path(blocked_proc.stdout.strip())
    custody_blocked_out = tmp / "custody-blocked"
    blocked_custody_proc = subprocess.run([
        sys.executable, str(ROOT / "tools" / "prepare_counterparty_artifact_custody_record.py"),
        "--custody-gate", str(blocked_gate),
        "--vault-root", str(vault),
        "--output-dir", str(custody_blocked_out),
        "--custody-id", "rev0216-blocked-open-challenge",
        "--created-at", CREATED_AT,
    ], check=True, capture_output=True, text=True)
    blocked_custody_path = Path(blocked_custody_proc.stdout.strip())
    validate(schema_rel, blocked_custody_path)
    blocked_custody = load(blocked_custody_path)
    if blocked_custody.get("artifact_state") != "quarantined":
        raise SystemExit("blocked custody gate should emit quarantined custody record only")
    if blocked_custody.get("import_readiness", {}).get("may_create_response_record") is not False:
        raise SystemExit("blocked custody record allowed response creation")

    # Resolved challenge plus evidence-backed authority prerequisites permits only response preparation.
    eligible_cmd = list(base_gate_cmd) + ["--challenge-disposition-record", str(eligible_disp_path)]
    eligible_cmd[eligible_cmd.index("--output-dir") + 1] = str(tmp / "gate-eligible")
    eligible_cmd[eligible_cmd.index("--gate-id") + 1] = "rev0216-resolved-response-lock"
    eligible_proc = subprocess.run(eligible_cmd, check=True, capture_output=True, text=True)
    eligible_gate_path = Path(eligible_proc.stdout.strip())
    eligible_gate = load(eligible_gate_path)
    if eligible_gate.get("gate_state") != "eligible-for-custody-record":
        raise SystemExit("synthetic complete evidence-backed gate did not become eligible")
    if eligible_gate.get("authority_evidence_binder", {}).get("may_feed_custody_authority_gate") is not True:
        raise SystemExit("eligible gate did not consume authority evidence binder")

    custody_out = tmp / "custody-output"
    custody_proc = subprocess.run([
        sys.executable, str(ROOT / "tools" / "prepare_counterparty_artifact_custody_record.py"),
        "--custody-gate", str(eligible_gate_path),
        "--vault-root", str(vault),
        "--output-dir", str(custody_out),
        "--custody-id", "rev0216-response-only-candidate",
        "--created-at", CREATED_AT,
        "--linked-request-packet", "ERRP-2026-synthetic-response-lock",
    ], check=True, capture_output=True, text=True)
    custody_path = Path(custody_proc.stdout.strip())
    validate(schema_rel, custody_path)
    custody = load(custody_path)
    if custody.get("artifact_state") != "live-candidate-artifact":
        raise SystemExit("eligible custody gate should create a live-candidate custody record")
    if custody.get("linked_custody_gate_ref") != eligible_gate.get("custody_gate_id"):
        raise SystemExit("custody record not bound to custody gate id")
    raw = custody.get("raw_artifacts", [{}])[0]
    if not raw.get("path_or_locator", "").startswith("private-vault://"):
        raise SystemExit("custody record leaked or failed to use private-vault locator")
    if raw.get("may_be_used_for_live_import") is not False:
        raise SystemExit("custody raw artifact should not be direct live-import input")
    readiness = custody.get("import_readiness", {})
    if readiness.get("may_create_response_record") is not True:
        raise SystemExit("eligible custody should permit response preparation")
    for key in ["may_create_intake_record", "may_run_import_gate"]:
        if readiness.get(key) is not False:
            raise SystemExit(f"custody record incorrectly unlocked {key}")
    if readiness.get("live_import_floor_delta") != 0:
        raise SystemExit("custody record changed live floor")
    if secret in json.dumps(custody):
        raise SystemExit("custody record leaked raw private bytes")
    generated_names = "\n".join(p.name for p in custody_out.glob("*.json"))
    if any(name in generated_names for name in ["external-receipt-response-record", "external-receipt-intake-record", "actual-receipt-import-gate"]):
        raise SystemExit("custody tool generated downstream response/intake/import objects")

    if Draft202012Validator is not None:
        schema = load(schema_rel)
        validator = Draft202012Validator(schema)
        missing_gate = copy.deepcopy(custody)
        missing_gate.pop("linked_custody_gate_ref", None)
        if not list(validator.iter_errors(missing_gate)):
            raise SystemExit("live-candidate custody without gate ref unexpectedly validates")
        imports_unlocked = copy.deepcopy(custody)
        imports_unlocked["import_readiness"]["may_run_import_gate"] = True
        if not list(validator.iter_errors(imports_unlocked)):
            raise SystemExit("live-candidate custody with import gate unlocked unexpectedly validates")
        intake_unlocked = copy.deepcopy(custody)
        intake_unlocked["import_readiness"]["may_create_intake_record"] = True
        if not list(validator.iter_errors(intake_unlocked)):
            raise SystemExit("live-candidate custody with intake unlocked unexpectedly validates")

required_fixtures = {
    "NF-CUSTODY-2026-0010": "fixtures/negative-tests/custody-record-live-candidate-without-gate-ref.json",
    "NF-CUSTODY-2026-0011": "fixtures/negative-tests/custody-record-unlocks-intake-import.json",
}
for fid, rel in required_fixtures.items():
    fixture = load(rel)
    if fixture.get("fixture_id") != fid:
        raise SystemExit(f"fixture id mismatch for {rel}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required_fixtures) <= suite_ids:
    raise SystemExit("fixture suite missing custody response-lock fixtures")
if not set(required_fixtures) <= report_ids:
    raise SystemExit("fixture report missing custody response-lock fixtures")

print("audit_counterparty_custody_response_lock: OK")
