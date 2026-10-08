#!/usr/bin/env python3
"""Audit rev0215 custody authority gate and graph refactor."""
from __future__ import annotations

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
    path = Path(rel_or_path)
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text(encoding="utf-8"))


def make_positive_binder(template: dict, rev: str) -> dict:
    positive = json.loads(json.dumps(template))
    positive["binder_id"] = f"CAEB-2026-{rev}-custody-gate-positive-control"
    positive["binder_state"] = "verified-for-custody-gate"
    positive["counterparty_org_id"] = "org:synthetic-counterparty"
    positive["dependency_group_id"] = "dep:synthetic-independent"
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
        "reason": "Synthetic positive control only: cited authority evidence refs are present and manually reviewed.",
    })
    positive["downstream_locks"]["custody_gate_may_consume_binder"] = True
    positive["authority_limitations"] = ["synthetic audit only; no actual live receipt"]
    return positive

def validate(schema_rel, data_path):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{Path(data_path).name} fails {schema_rel}: {errors[0].message}")

schema_rel = "schemas/counterparty-artifact-custody-gate.schema.json"
current_rel = f"examples/counterparty-artifact-custody-gate-{REV}-pending-challenge.json"
validate(schema_rel, ROOT / current_rel)
example = load(current_rel)
if example.get("revision") != REV:
    raise SystemExit("custody gate example revision mismatch")
if example.get("gate_state") != "blocked-challenge-pending":
    raise SystemExit("checked-in custody gate example should block while challenge is pending")
if example.get("downstream_locks", {}).get("may_prepare_counterparty_artifact_custody_record") is not False:
    raise SystemExit("pending challenge must not permit custody record preparation")
for key in ["response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed"]:
    if example.get("downstream_locks", {}).get(key) is not False:
        raise SystemExit(f"custody gate unlocked {key}")
if example.get("decision", {}).get("reliance_effect") != "stayed" or example.get("no_live_floor_effect") is not True:
    raise SystemExit("custody gate changed reliance or live floor")
if example.get("candidate_challenge", {}).get("silence_treated_as_waiver") is not False:
    raise SystemExit("custody gate treats silence as waiver")
gate_binder = example.get("authority_evidence_binder", {})
if gate_binder.get("may_feed_custody_authority_gate") is not False or gate_binder.get("checkbox_only_authority_blocked") is not True:
    raise SystemExit("pending custody gate did not block missing authority evidence binder")

binder_example = ROOT / f"examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json"
validate("schemas/custody-authority-evidence-binder.schema.json", binder_example)

challenge = ROOT / f"examples/live-artifact-candidate-challenge-report-{REV}-synthetic-pending.json"
validate("schemas/live-artifact-candidate-challenge-report.schema.json", challenge)
disposition_example = ROOT / f"examples/candidate-challenge-disposition-record-{REV}-open-stayed.json"
validate("schemas/candidate-challenge-disposition-record.schema.json", disposition_example)

with tempfile.TemporaryDirectory(prefix="ai-personhood-custody-gate-") as td:
    tmp = Path(td)
    positive_binder = make_positive_binder(load(binder_example), REV)
    positive_binder_path = tmp / "positive-authority-binder.json"
    positive_binder_path.write_text(json.dumps(positive_binder, indent=2) + "\n", encoding="utf-8")
    validate("schemas/custody-authority-evidence-binder.schema.json", positive_binder_path)

    # Open challenge must block even if an operator supplies authority-looking flags and a positive binder.
    outdir = tmp / "blocked"
    cmd = [
        sys.executable, str(ROOT / "tools" / "prepare_custody_authority_gate.py"),
        "--challenge-report", str(challenge),
        "--output-dir", str(outdir),
        "--gate-id", "rev0215-open-challenge",
        "--created-at", CREATED_AT,
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
        "--authority-evidence-binder", str(positive_binder_path),
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    blocked = load(Path(proc.stdout.strip()))
    validate(schema_rel, Path(proc.stdout.strip()))
    if blocked.get("gate_state") != "blocked-challenge-pending":
        raise SystemExit("open challenge did not block custody gate")

    # A resolved challenge with all prerequisites may authorize only preparation
    # of a separate custody record, but rev0235+ requires a separate
    # candidate-challenge-disposition-record and rev0236+ requires a cited
    # custody-authority-evidence-binder rather than raw booleans.
    eligible_disp = load(disposition_example)
    eligible_disp["disposition_record_id"] = f"LACD-2026-{REV}-custody-gate-positive-control"
    eligible_disp["disposition_state"] = "closed-objection-rejected-after-review"
    eligible_disp["closure_evidence"].update({
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
    eligible_disp["decision"].update({
        "challenge_status_effective": "closed-rejected",
        "may_feed_custody_authority_gate": True,
        "custody_gate_consumption_reason": "synthetic positive control disposition supplies a reviewed objection rejection before custody gate consumption",
        "reason": "Synthetic positive control only: a reviewed objection was rejected after human review and scoped authority checks. It may feed custody gate but creates no custody record or live-floor effect.",
    })
    eligible_disp["downstream_locks"]["custody_gate_may_consume_disposition"] = True
    eligible_disp_path = tmp / "eligible-disposition.json"
    eligible_disp_path.write_text(json.dumps(eligible_disp, indent=2) + "\n", encoding="utf-8")
    validate("schemas/candidate-challenge-disposition-record.schema.json", eligible_disp_path)

    eligible_out = tmp / "eligible"
    cmd2 = cmd.copy()
    cmd2[cmd2.index("--output-dir") + 1] = str(eligible_out)
    cmd2[cmd2.index("--gate-id") + 1] = "rev0215-resolved-authority"
    cmd2.extend(["--challenge-disposition-record", str(eligible_disp_path)])
    proc2 = subprocess.run(cmd2, check=True, capture_output=True, text=True)
    eligible = load(Path(proc2.stdout.strip()))
    validate(schema_rel, Path(proc2.stdout.strip()))
    if eligible.get("gate_state") != "eligible-for-custody-record":
        raise SystemExit("resolved complete prerequisites should be eligible for custody-record preparation")
    if eligible.get("challenge_disposition", {}).get("may_feed_custody_authority_gate") is not True:
        raise SystemExit("eligible custody gate did not consume disposition evidence")
    if eligible.get("authority_evidence_binder", {}).get("may_feed_custody_authority_gate") is not True:
        raise SystemExit("eligible custody gate did not consume authority evidence binder")
    locks = eligible.get("downstream_locks", {})
    if locks.get("may_prepare_counterparty_artifact_custody_record") is not True:
        raise SystemExit("eligible gate did not authorize custody-record preparation")
    for key in ["custody_record_admitted", "response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed"]:
        if locks.get(key) is not False:
            raise SystemExit(f"eligible gate incorrectly unlocked {key}")

    # A closed-no-objection without counterparty contact/request trace remains blocked;
    # no-objection is not silence-as-waiver.
    silence_out = tmp / "silence"
    cmd3 = [
        sys.executable, str(ROOT / "tools" / "prepare_custody_authority_gate.py"),
        "--challenge-report", str(challenge),
        "--output-dir", str(silence_out),
        "--gate-id", "rev0215-silence-waiver-trap",
        "--created-at", CREATED_AT,
        "--challenge-status", "closed-no-objection",
        "--receipt-class", "result-return",
        "--authority-scope", "result-return",
        "--authority-limitation", "synthetic audit only",
    ]
    proc3 = subprocess.run(cmd3, check=True, capture_output=True, text=True)
    silence = load(Path(proc3.stdout.strip()))
    if silence.get("gate_state") != "blocked-missing-authority":
        raise SystemExit("closed-no-objection without manual contact should not open custody gate")
    if silence.get("candidate_challenge", {}).get("silence_treated_as_waiver") is not False:
        raise SystemExit("silence trap marked silence as waiver")

# Checked-in negative fixtures and suite/report registration.
required_fixtures = {
    "NF-CUSTODY-2026-0008": "fixtures/negative-tests/custody-gate-silence-treated-as-waiver.json",
    "NF-CUSTODY-2026-0009": "fixtures/negative-tests/custody-gate-authority-unscoped.json",
    "NF-CUSTODY-2026-0018": "fixtures/negative-tests/custody-authority-binder-checkbox-only.json",
    "NF-CUSTODY-2026-0019": "fixtures/negative-tests/custody-authority-binder-protocol-output-as-authority.json",
    "NF-CUSTODY-2026-0020": "fixtures/negative-tests/custody-authority-binder-private-vault-uri-as-authority.json",
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
    raise SystemExit("fixture suite missing custody gate fixtures")
if not set(required_fixtures) <= report_ids:
    raise SystemExit("fixture report missing custody gate fixtures")

graph = load(f"examples/live-artifact-admission-graph-{REV}.json")
node_ids = {n.get("node_id") for n in graph.get("nodes", [])}
edge_pairs = {(e.get("from"), e.get("to")) for e in graph.get("edges", [])}
for node_id in ["CANDIDATE_CHALLENGE", "CANDIDATE_DISPOSITION", "AUTHORITY_EVIDENCE_BINDER", "CUSTODY_GATE"]:
    if node_id not in node_ids:
        raise SystemExit(f"admission graph missing node {node_id}")
for edge in [("LEAP", "CANDIDATE_CHALLENGE"), ("CANDIDATE_CHALLENGE", "CANDIDATE_DISPOSITION"), ("CANDIDATE_DISPOSITION", "AUTHORITY_EVIDENCE_BINDER"), ("AUTHORITY_EVIDENCE_BINDER", "CUSTODY_GATE"), ("CUSTODY_GATE", "CUSTODY")]:
    if edge not in edge_pairs:
        raise SystemExit(f"admission graph missing edge {edge}")
required_checks = {"candidate-challenge-before-disposition", "candidate-disposition-before-authority-binder", "authority-binder-before-custody-gate", "custody-gate-before-custody"}
missing_checks = required_checks - {c.get("check_id") for c in graph.get("bypass_checks", [])}
if missing_checks:
    raise SystemExit("admission graph missing custody gate bypass checks: " + ", ".join(sorted(missing_checks)))

print("audit_custody_authority_gate: OK")
