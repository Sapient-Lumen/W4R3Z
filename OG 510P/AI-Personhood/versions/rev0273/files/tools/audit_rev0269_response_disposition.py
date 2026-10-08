#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema_rel, data_rel):
    if Draft202012Validator is None:
        return
    schema = load(schema_rel)
    data = load(data_rel)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

packet_rel = f"examples/reviewer-first-contact-packet-{REV}-eleos-not-sent.json"
body_rel = f"examples/reviewer-first-contact-body-{REV}-eleos-not-sent.txt"
eml_rel = f"examples/reviewer-first-contact-mail-ready-draft-{REV}-eleos-not-sent.eml"
workbook_rel = f"examples/field-artifact-capture-workbook-{REV}-reviewer-first-no-send.json"
six_rel = f"examples/six-artifact-pilot-state-{REV}-preservation-review.json"
branch_rel = f"examples/human-branch-decision-record-{REV}-unsigned-template.json"
precommit_rel = f"examples/pre-send-custody-precommit-{REV}-no-private-root-selected.json"
playbook_rel = f"examples/reviewer-response-disposition-playbook-{REV}.json"
failed_rel = f"examples/failed-gate-public-summary-{REV}-reviewer-route-unavailable-template.json"

for schema, rel in [
    ("schemas/reviewer-first-contact-packet.schema.json", packet_rel),
    ("schemas/field-artifact-capture-workbook.schema.json", workbook_rel),
    ("schemas/six-artifact-pilot-state.schema.json", six_rel),
    ("schemas/human-branch-decision-record.schema.json", branch_rel),
    ("schemas/pre-send-custody-precommit.schema.json", precommit_rel),
    ("schemas/failed-gate-public-summary.schema.json", failed_rel),
]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing response-disposition surface: {rel}")
    validate(schema, rel)

packet = load(packet_rel)
workbook = load(workbook_rel)
six = load(six_rel)
branch = load(branch_rel)
precommit = load(precommit_rel)
playbook = load(playbook_rel)
failed = load(failed_rel)

for label, obj in [("packet", packet), ("workbook", workbook), ("six", six), ("branch", branch), ("precommit", precommit), ("playbook", playbook)]:
    if obj.get("revision") != REV or obj.get("no_live_floor_effect") is not True:
        raise SystemExit(f"{label} revision/no-floor mismatch")

if branch.get("record_state") != "template-unsigned-no-authority" or branch.get("selected_choice", {}).get("selected_now") is not False:
    raise SystemExit("branch must remain unsigned/no-authority")
if precommit.get("precommit_state") != "template-no-private-root-selected":
    raise SystemExit("precommit must remain no-private-root-selected")
for key in ["raw_sent_copy_root_selected", "transport_proof_root_selected", "raw_inbound_root_selected", "sealed_evidence_root_selected"]:
    if precommit.get("private_roots", {}).get(key) is not False:
        raise SystemExit(f"private root unexpectedly selected: {key}")

body = (ROOT / body_rel).read_text(encoding="utf-8").strip()
eml_path = ROOT / eml_rel
eml = eml_path.read_text(encoding="utf-8")
if packet.get("exact_message", {}).get("body_sha256") != hashlib.sha256(body.encode("utf-8")).hexdigest():
    raise SystemExit("body hash stale")
if packet.get("exact_message", {}).get("mail_ready_draft_sha256") != hashlib.sha256(eml_path.read_bytes()).hexdigest():
    raise SystemExit("eml hash stale")
for term in ["one-line disposition", "decline", "referral", "wrong route", "do not contact further", "not be treated as waiver"]:
    if term not in body:
        raise SystemExit(f"reviewer body missing disposition term: {term}")
for header in ["X-AI-Personhood-Draft-State: NOT-SENT", "X-AI-Personhood-Response-Disposition-Guard", "X-AI-Personhood-Clock-Guard"]:
    if header not in eml:
        raise SystemExit(f"eml missing header: {header}")
chan = packet.get("channel", {})
for key in ["send_authorized_now", "counterparty_contacted", "response_clock_started"]:
    if chan.get(key) is not False:
        raise SystemExit(f"packet overclaims {key}")

expected_codes = [
    "NO-HUMAN-AUTHORITY", "SEND-FAILED", "DELIVERY-ONLY", "AUTO-ACK-OR-BOT", "HUMAN-DECLINE", "REFERRAL-OR-WRONG-ROUTE", "NARROW-YES-SCOPING", "NO-RESPONSE-EXPIRED", "RAW-PRIVATE-DATA-REQUESTED",
]
actual_codes = [row.get("code") for row in playbook.get("disposition_rows", [])]
if actual_codes != expected_codes:
    raise SystemExit(f"disposition code order mismatch: {actual_codes}")
locks = playbook.get("overclaim_locks", {})
for key in ["auto_ack_as_response", "delivery_status_as_response", "decline_as_waiver", "referral_as_reviewer_appointment", "no_response_as_status_finding", "public_shell_as_raw_custody", "custody_intake_import_floor_from_disposition"]:
    if locks.get(key) is not False:
        raise SystemExit(f"playbook lock not false: {key}")

if failed.get("public_shell_state") != "draft":
    raise SystemExit("failed-gate shell must remain draft")
closure = failed.get("closure_effect", {})
if closure.get("reliance_effect") != "stayed" or closure.get("live_quorum_satisfied") is not False or closure.get("public_failed_gate_satisfies_receipt") is not False:
    raise SystemExit("failed-gate shell overclaims closure")
fg_types = {item.get("gate_type") for item in failed.get("failed_gate_items", [])}
for typ in ["request-not-receipt", "defective-response", "declined-response", "single-class-insufficient", "expired-no-response"]:
    if typ not in fg_types:
        raise SystemExit(f"failed-gate shell missing type: {typ}")
prohibited_text = " ".join(failed.get("prohibited_inferences", [])).lower()
for term in ["live receipt", "waives", "referral", "auto-ack", "silence", "raw custody"]:
    if term not in prohibited_text:
        raise SystemExit(f"failed-gate prohibited inference missing {term}")

rows = {row.get("artifact_id"): row for row in workbook.get("artifact_rows", [])}
for rel in [playbook_rel, failed_rel]:
    if rel not in rows["A3-RAW-RESPONSE-OR-FAILED-GATE"].get("current_evidence", []):
        raise SystemExit(f"A3 workbook missing {rel}")
if failed_rel not in rows["A6-PUBLIC-FINDING-REMEDY"].get("current_evidence", []):
    raise SystemExit("A6 workbook missing failed-gate shell")
fg_routes = " ".join(workbook.get("failed_gate_routes", [])).lower()
for term in ["auto-ack", "delivery failure", "decline", "raw response", "referral", "expired no-response"]:
    if term not in fg_routes:
        raise SystemExit(f"workbook missing failed-gate route term: {term}")

six_text = json.dumps(six).lower()
for term in ["response-disposition", "failed-gate", "auto-ack", "referral", "decline", "silence"]:
    if term not in six_text:
        raise SystemExit(f"six-artifact pilot missing term: {term}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
if queue.get("revision") != REV:
    raise SystemExit("queue revision mismatch")
entries = {e.get("id"): e for e in queue.get("entries", [])}
for qid in ["FT-0205-FIRST-REAL-ARTIFACT-DROP", "FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION", "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]:
    text = json.dumps(entries.get(qid, {})).lower()
    for term in [playbook_rel.lower(), failed_rel.lower(), "do not close by narrative", "auto-ack", "referral", "decline", "silence"]:
        if term not in text:
            raise SystemExit(f"{qid} missing response-disposition queue term: {term}")

status = load("SURFACE-STATUS.json")
for rel in [playbook_rel, failed_rel, f"docs/00-meta/{REV}-response-disposition-and-failedgate-refactor.md", f"docs/30-transition/{REV}-response-disposition-operator-runbook.md", f"tools/audit_rev0269_response_disposition.py"]:
    if rel not in status.get("new_surfaces", []):
        raise SystemExit(f"SURFACE-STATUS missing response-disposition surface: {rel}")
    if not (ROOT / rel).exists():
        raise SystemExit(f"SURFACE-STATUS names missing path: {rel}")
if status.get("no_live_floor_effect") is not True:
    raise SystemExit("SURFACE-STATUS must preserve no live floor")

print("audit_rev0269_response_disposition: OK")
