#!/usr/bin/env python3
"""Audit custody authority evidence binder.

The binder prevents authority-looking booleans from being treated as custody
eligibility unless each prerequisite has a cited, class-scoped evidence ref.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel_or_path):
    p = Path(rel_or_path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def validate(schema_rel: str, data_path: Path) -> None:
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{data_path.name} fails {schema_rel}: {errors[0].message}")


schema_rel = "schemas/custody-authority-evidence-binder.schema.json"
example_rel = f"examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json"
example_path = ROOT / example_rel
validate(schema_rel, example_path)
example = load(example_path)

if example.get("revision") != REV or example.get("no_live_floor_effect") is not True:
    raise SystemExit("custody authority binder revision/no-floor guard mismatch")
if example.get("binder_state") != "pre-dispatch-no-authority":
    raise SystemExit("checked-in binder must remain pre-dispatch/no-authority")
if example.get("decision", {}).get("may_feed_custody_authority_gate") is not False:
    raise SystemExit("pre-dispatch binder may not feed custody gate")
locks = example.get("downstream_locks", {})
for key in [
    "custody_gate_may_consume_binder",
    "response_creation_allowed",
    "intake_creation_allowed",
    "import_gate_creation_allowed",
    "live_floor_delta_allowed",
    "status_or_waiver_claim_allowed",
    "raw_payload_publication_allowed",
]:
    if locks.get(key) is not False:
        raise SystemExit(f"pre-dispatch binder unlocked {key}")
for name, ref in example.get("evidence_refs", {}).items():
    if ref.get("present") is not False or ref.get("can_satisfy_custody_authority") is not False:
        raise SystemExit(f"pre-dispatch evidence ref unexpectedly satisfies authority: {name}")

# Positive synthetic control: every prerequisite has cited, human-reviewed,
# class-scoped evidence, but even then the binder creates no custody/response/etc.
positive = copy.deepcopy(example)
positive["binder_id"] = f"CAEB-2026-{REV}-positive-control"
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
    "reason": "Synthetic positive control only: class-scoped authority evidence refs are present and manually reviewed; binder may feed custody gate but creates no custody or downstream reliance.",
})
positive["downstream_locks"]["custody_gate_may_consume_binder"] = True
positive["authority_limitations"] = ["synthetic positive control only; not an actual live receipt"]
pos_path = ROOT / ".tmp-custody-authority-binder-positive.json"
pos_path.write_text(json.dumps(positive, indent=2) + "\n", encoding="utf-8")
try:
    validate(schema_rel, pos_path)
finally:
    pos_path.unlink(missing_ok=True)

# Checked-in negative fixtures and red-team registry coverage.
required_fixtures = {
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
    raise SystemExit("fixture suite missing custody authority binder fixtures")
if not set(required_fixtures) <= report_ids:
    raise SystemExit("fixture report missing custody authority binder fixtures")

# Release-fast custody gate must name the binder and still block.
gate = load(f"examples/counterparty-artifact-custody-gate-{REV}-pending-challenge.json")
gate_binder = gate.get("authority_evidence_binder", {})
if gate_binder.get("binder_id") != example.get("binder_id"):
    raise SystemExit("current custody gate is not bound to the current authority evidence binder")
if gate_binder.get("may_feed_custody_authority_gate") is not False:
    raise SystemExit("current custody gate consumed a pre-dispatch binder")

print("audit_custody_authority_evidence_binder: OK")
