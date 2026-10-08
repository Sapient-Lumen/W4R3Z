#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

schema_rel = "schemas/external-receipt-response-verification-gate.schema.json"
example_rel = f"examples/external-receipt-response-verification-gate-{REV}-blocked-no-response.json"
for rel in [schema_rel, example_rel, "tools/prepare_external_receipt_response_gate.py"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing response gate surface: {rel}")

if Draft202012Validator is not None:
    schema = load(schema_rel)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(load(example_rel)), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{example_rel} fails schema: {errors[0].message}")

    response_schema = load("schemas/external-receipt-response-record.schema.json")
    response_validator = Draft202012Validator(response_schema)
    response_probe = load("examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json")
    if not response_probe.get("linked_response_verification_gate_ref"):
        raise SystemExit("eligible conversion fixture must carry controlled response verification gate ref")
    missing_gate = copy.deepcopy(response_probe)
    missing_gate.pop("linked_response_verification_gate_ref", None)
    if not list(response_validator.iter_errors(missing_gate)):
        raise SystemExit("actual response capable of intake without response verification gate unexpectedly validates")

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    custody = {
        "custody_record_id": "CACR-2026-response-gate-probe",
        "schema_version": "counterparty-artifact-custody-record-v0.1",
        "created_at": "2026-06-16T06:39:00Z",
        "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
        "linked_import_attempt": "not-yet-created:live-counterparty-import-attempt",
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "linked_artifact_envelope": "not-yet-created:nonhost-response-artifact-envelope",
        "linked_custody_gate_ref": "CAG-2026-response-gate-probe",
        "artifact_state": "live-candidate-artifact",
        "receipt_class": "result-return",
        "counterparty_authority": {
            "role": "counterparty artifact custody reviewer",
            "identity_ref": "org:probe-counterparty",
            "external_to_host": True,
            "dependency_group": "probe-independent",
            "authority_basis": "scoped response gate probe",
            "authority_limitations": ["response preparation only"],
            "authority_verified": True,
            "class_scope": ["result-return"],
        },
        "raw_artifacts": [{"artifact_id":"CACR-A-001","artifact_type":"raw-email","path_or_locator":"private-vault://probe","sha256":"0"*64,"size_bytes":1,"mime_type":"message/rfc822","collection_context":"live-counterparty","raw_available":True,"sealed":True,"public_redaction_ref":"public-shell:probe","may_be_used_for_live_import":False}],
        "collection_chain": [{"event_id":"CACR-EV-001","event_type":"authority-checked","at":"2026-06-16T06:39:00Z","actor":"probe","system_boundary":"neutral-infrastructure","evidence_ref":"CAG-2026-response-gate-probe","can_satisfy_live_receipt":False}],
        "integrity_checks": {"raw_artifact_available":True,"sha256_verified":True,"locator_resolvable":True,"timestamp_independent":True,"identity_authority_checked":True,"dependency_group_checked":True,"nonhost_storage_confirmed":True,"sealed_public_parity_checked":True,"redaction_not_substituted_for_raw":True},
        "redaction_and_subject_access": {"sealed_material_present":True,"public_shell_ref":"public-shell:probe","subject_readable_summary_required":True,"privacy_controls":["raw private bytes never packaged"],"prohibited_inferences":["custody is not intake"]},
        "import_readiness": {"may_create_response_record":True,"may_create_intake_record":False,"may_run_import_gate":False,"live_import_floor_delta":0,"disqualification_reasons":[],"next_gate":"external receipt response verification gate"},
        "decision": {"live_reliance_effect":"stayed","custody_admission":"admitted-for-live-import-review","reason":"probe custody","blocked_actions":["intake from custody"],"next_actions":["run response gate"]},
    }
    custody_path = tmp / "custody.json"
    write(custody_path, custody)
    good_desc = {
        "counterparty_reply_received": True,
        "counterparty_identity_ref": "org:probe-counterparty",
        "response_channel": "non-host-email",
        "received_at": "2026-06-16T06:39:00Z",
        "dry_run": False,
        "artifacts": [{"artifact_id":"ERVG-A-001","artifact_type":"signed-response","locator_or_hash":"private-vault://probe-response","generated_by":"external-counterparty","retained_by":"non-host","sealed":True,"dry_run":False}],
        "counterparty_confirmed": True,
        "signature_or_equivalent_verified": True,
        "timestamp_independent": True,
        "request_trace_matches": True,
        "nonhost_retention_verified": True,
        "dependency_checked": True,
        "receipt_class_matches": True,
        "scoped_acceptance_present": True,
        "not_stale_or_superseded": True,
        "manual_review_completed": True,
        "private_material_not_in_public_release": True,
    }
    good_path = tmp / "good.json"
    write(good_path, good_desc)
    out_dir = tmp / "out"
    subprocess.run([sys.executable, str(ROOT/"tools/prepare_external_receipt_response_gate.py"), "--custody-record", str(custody_path), "--response-descriptor", str(good_path), "--output-dir", str(out_dir), "--gate-id", "probe-good"], check=True)
    gate = json.loads(next(out_dir.glob("*.json")).read_text())
    if gate.get("gate_state") != "eligible-for-response-record":
        raise SystemExit("good response descriptor did not produce eligible response gate")
    locks = gate.get("downstream_locks", {})
    if locks.get("may_prepare_external_receipt_response_record") is not True:
        raise SystemExit("eligible gate did not allow response record preparation")
    for key in ["may_create_intake_record", "may_run_import_gate", "live_floor_delta_allowed"]:
        if locks.get(key) is not False:
            raise SystemExit(f"eligible response gate incorrectly unlocked {key}")
    if gate.get("decision", {}).get("can_generate_actual_intake") is not False:
        raise SystemExit("response gate must not generate actual intake directly")
    if Draft202012Validator is not None:
        errors = sorted(Draft202012Validator(load(schema_rel)).iter_errors(gate), key=lambda e: list(e.path))
        if errors:
            raise SystemExit("eligible generated gate failed schema: " + errors[0].message)
        bad = copy.deepcopy(gate)
        bad["downstream_locks"]["may_create_intake_record"] = True
        if not list(Draft202012Validator(load(schema_rel)).iter_errors(bad)):
            raise SystemExit("eligible response gate with intake unlocked unexpectedly validates")
        bad2 = copy.deepcopy(gate)
        bad2["decision"]["can_generate_actual_intake"] = True
        if not list(Draft202012Validator(load(schema_rel)).iter_errors(bad2)):
            raise SystemExit("eligible response gate generating actual intake unexpectedly validates")

    bad_desc = copy.deepcopy(good_desc)
    bad_desc["scoped_acceptance_present"] = False
    bad_path = tmp / "bad.json"
    write(bad_path, bad_desc)
    out_dir2 = tmp / "out2"
    subprocess.run([sys.executable, str(ROOT/"tools/prepare_external_receipt_response_gate.py"), "--custody-record", str(custody_path), "--response-descriptor", str(bad_path), "--output-dir", str(out_dir2), "--gate-id", "probe-bad"], check=True)
    blocked = json.loads(next(out_dir2.glob("*.json")).read_text())
    if blocked.get("gate_state") != "blocked-unscoped-acceptance":
        raise SystemExit("missing scoped acceptance did not block response gate")
    if blocked.get("decision", {}).get("response_record_may_be_prepared") is not False:
        raise SystemExit("blocked response gate allowed response record preparation")

required_fixtures = {
    "NF-CUSTODY-2026-0012": "fixtures/negative-tests/response-gate-unverified-reply-creates-intake.json",
    "NF-CUSTODY-2026-0013": "fixtures/negative-tests/response-gate-scoped-acceptance-missing.json",
}
for fid, rel in required_fixtures.items():
    data = load(rel)
    if data.get("fixture_id") != fid:
        raise SystemExit(f"fixture id mismatch for {rel}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_ids = {f.get("fixture_id") for f in report.get("fixtures_run", [])}
if not set(required_fixtures) <= suite_ids:
    raise SystemExit("fixture suite missing response gate fixtures")
if not set(required_fixtures) <= report_ids:
    raise SystemExit("fixture report missing response gate fixtures")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "EXTERNAL-RECEIPT-RESPONSE-VERIFICATION-GATE" not in families:
    raise SystemExit("registry missing response verification gate family")

graph = load(f"examples/live-artifact-admission-graph-{REV}.json")
node_ids = {n.get("node_id") for n in graph.get("nodes", [])}
if "RESPONSE_GATE" not in node_ids:
    raise SystemExit("admission graph missing RESPONSE_GATE node")
checks = {c.get("check_id"): c for c in graph.get("bypass_checks", [])}
if checks.get("response-gate-before-response-intake", {}).get("passed") is not True:
    raise SystemExit("admission graph response gate check not passing")

print("audit_external_receipt_response_verification_gate: OK")
