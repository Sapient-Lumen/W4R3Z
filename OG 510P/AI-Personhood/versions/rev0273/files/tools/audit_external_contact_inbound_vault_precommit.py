#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json"
SCHEMA_REL = "schemas/external-contact-inbound-vault-precommit.schema.json"
FIXTURE_REL = "fixtures/negative-tests/external-contact-inbound-vault-precommit-screenshot-as-raw.json"

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-inbound-vault-precommit.schema.json: {errors[0].message}")


schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("inbound-vault precommit revision mismatch")
if record.get("schema_version") != "external-contact-inbound-vault-precommit-v0.2":
    raise SystemExit("inbound-vault precommit schema version mismatch")
if record.get("precommit_state") != "pre-dispatch-no-inbound":
    raise SystemExit("current inbound-vault precommit must stay pre-dispatch/no-inbound")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("inbound-vault precommit must have no live-floor effect")

sources = {
    "send-proof": record.get("source_send_proof_record_ref"),
    "response-triage": record.get("source_response_triage_record_ref"),
    "vault-intake": record.get("source_vault_intake_record_ref"),
    "execution": record.get("source_execution_record_ref"),
    "dispatch-card": record.get("source_dispatch_authorization_card_ref"),
    "inbound-capture-shell": record.get("source_inbound_capture_shell_ref"),
}
for label, rel in sources.items():
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"inbound-vault precommit missing source: {label}={rel}")
    src = load(rel)
    if src.get("revision") != REV or src.get("no_live_floor_effect") is not True:
        raise SystemExit(f"inbound-vault precommit source is not current/no-floor: {label}")

send_proof = load(sources["send-proof"])
execution = load(sources["execution"])
triage = load(sources["response-triage"])
vault_intake = load(sources["vault-intake"])
card = load(sources["dispatch-card"])
capture_shell = load(sources["inbound-capture-shell"])

if capture_shell.get("capture_state") != "pre-dispatch-no-inbound":
    raise SystemExit("pre-dispatch inbound-vault precommit must bind a pre-dispatch inbound-capture shell")
if capture_shell.get("source_inbound_vault_precommit_ref") != RECORD_REL:
    raise SystemExit("inbound-capture shell is not bound back to current inbound-vault precommit")

if send_proof.get("send_proof_state") != "not-sent-no-proof":
    raise SystemExit("pre-dispatch inbound-vault precommit must bind a not-sent send-proof record")
if execution.get("execution_state") != "no-send-recorded":
    raise SystemExit("pre-dispatch inbound-vault precommit must bind no-send execution record")
if triage.get("triage_state") != "pre-dispatch-no-inbound":
    raise SystemExit("pre-dispatch inbound-vault precommit must bind pre-dispatch response triage")
if vault_intake.get("record_state") != "pre-dispatch-no-inbound":
    raise SystemExit("pre-dispatch inbound-vault precommit must bind pre-dispatch vault intake")
if card.get("raw_reply_vault_precommit", {}).get("root_selected_now") is not False:
    raise SystemExit("dispatch card unexpectedly claims a selected raw-reply vault root")
if record.get("vault_boundary", {}).get("locator_prefix") != card.get("raw_reply_vault_precommit", {}).get("locator_prefix") + "inbound/":
    raise SystemExit("inbound-vault precommit locator prefix must extend the dispatch-card precommit prefix")

vault = record.get("vault_boundary", {})
expected_vault = {
    "off_release_private_vault_required": True,
    "actual_root_selected_now": False,
    "raw_payload_private_vault_locator": None,
    "raw_payload_present_now": False,
    "precommit_is_not_vault_root": True,
    "precommit_is_not_retention_permission": True,
    "precommit_is_not_counterparty_authority": True,
    "public_release_may_include_raw_reply_bytes": False,
    "hash_shell_may_satisfy_raw_custody": False,
    "redacted_copy_may_satisfy_raw_custody": False,
    "screenshot_may_satisfy_raw_reply": False,
    "protocol_output_may_satisfy_raw_reply": False,
}
for key, expected in expected_vault.items():
    if vault.get(key) is not expected:
        raise SystemExit(f"inbound-vault boundary unsafe: {key}")
if vault.get("stage_tool") != "tools/stage_external_contact_inbound_capture.py" or not (ROOT / vault.get("stage_tool", "")).exists():
    raise SystemExit("inbound-vault precommit must route through stage_external_contact_inbound_capture.py")

contract = record.get("raw_reply_acceptance_contract", {})
for key in [
    "raw_rfc822_or_provider_export_required",
    "summary_or_screenshot_rejected_as_raw",
    "private_bytes_before_public_shell_required",
    "retention_permission_required_before_candidate_use",
    "nonhost_retention_required_before_candidate_use",
    "capture_shell_required_before_public_claim",
]:
    if contract.get(key) is not True:
        raise SystemExit(f"inbound-vault raw acceptance contract missing: {key}")
if contract.get("capture_shell_may_satisfy_custody") is not False:
    raise SystemExit("inbound-vault capture shell must not satisfy custody")
if contract.get("capture_stage_tool") != "tools/stage_external_contact_inbound_capture.py":
    raise SystemExit("inbound-vault raw acceptance contract must bind the inbound-capture staging tool")
if contract.get("all_present_now") is not False:
    raise SystemExit("inbound-vault precommit must not claim all raw-reply requirements are present")
joined_formats = " ".join(contract.get("accepted_raw_formats", [])).lower()
for term in ["rfc 5322", "provider", "headers", "bytes"]:
    if term not in joined_formats:
        raise SystemExit(f"raw reply accepted formats missing term: {term}")
joined_metadata = " ".join(contract.get("minimum_metadata_fields", [])).lower()
for term in ["received", "transport", "counterparty", "retention", "confidentiality", "public"]:
    if term not in joined_metadata:
        raise SystemExit(f"raw reply metadata requirements missing term: {term}")

headers = record.get("transport_header_requirements", {})
for key in [
    "rfc5322_message_required",
    "message_id_required",
    "in_reply_to_or_references_required_after_sent_message_id_exists",
    "received_chain_or_provider_trace_required",
    "date_header_and_observed_timestamp_required",
    "envelope_or_provider_export_required",
    "sent_message_binding_required",
]:
    if headers.get(key) is not True:
        raise SystemExit(f"transport header requirement missing: {key}")
for key in ["message_id_present_now", "headers_present_now", "sent_message_id_available_now", "deadline_may_start_now"]:
    if headers.get(key) is not False:
        raise SystemExit(f"transport header current-state guard must be false: {key}")

auth = record.get("authentication_results_policy", {})
for key in ["dkim_check_required_if_email", "spf_check_required_if_available", "dmarc_alignment_check_required_if_email", "arc_chain_may_be_collected", "arc_chain_is_not_authority", "auth_results_may_support_transport_assessment"]:
    if auth.get(key) is not True:
        raise SystemExit(f"authentication policy missing: {key}")
for key in ["auth_results_may_satisfy_counterparty_authority", "pass_fail_may_create_custody", "all_present_now"]:
    if auth.get(key) is not False:
        raise SystemExit(f"authentication policy overclaims: {key}")
if "RFC 9989" not in auth.get("dmarc_policy_reference", ""):
    raise SystemExit("authentication policy must reference current DMARC RFC 9989")

routes = record.get("classification_and_routing", {})
route_text = "\n".join(str(v).lower() for v in routes.values())
for term in ["automated", "decline", "human", "redacted", "protocol", "malformed", "silence", "waiver", "adverse", "live-floor"]:
    if term not in route_text:
        raise SystemExit(f"classification/routing text missing term: {term}")
if routes.get("no_inbound_state_now") is not True or routes.get("routes_may_create_response_record_directly") is not False:
    raise SystemExit("classification/routing current-state guard unsafe")

shell = record.get("public_shell_contract", {})
for key in ["shell_required_before_public_claim", "shell_is_not_response", "shell_is_not_custody", "shell_is_not_authority", "shell_is_not_live_floor"]:
    if shell.get(key) is not True:
        raise SystemExit(f"public shell contract missing: {key}")
for term in ["raw", "personal", "trade secret", "headers", "waiver", "adverse", "status", "live-floor"]:
    if term not in " ".join(shell.get("forbidden_public_fields", [])).lower():
        raise SystemExit(f"public shell forbidden fields missing term: {term}")

reject = "\n".join(record.get("evidence_rejection_rules", [])).lower()
for term in ["screenshot", "hash shell", "dkim", "spf", "dmarc", "arc", "automated", "protocol", "silence", "raw reply bytes"]:
    if term not in reject:
        raise SystemExit(f"evidence rejection rules missing term: {term}")

for key, value in record.get("downstream_locks", {}).items():
    if value is not False:
        raise SystemExit(f"inbound-vault downstream lock must be false: {key}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"inbound-vault precommit references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"inbound-vault precommit references missing surface: {rel}")

fx = load(FIXTURE_REL)
if "external-contact-inbound-vault-precommit" not in fx.get("target_filings", []):
    raise SystemExit("inbound-vault fixture does not target precommit")
if fx.get("severity") != "critical":
    raise SystemExit("inbound-vault fixture must be critical")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    mut = copy.deepcopy(record)
    mut["vault_boundary"]["screenshot_may_satisfy_raw_reply"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("inbound-vault schema failed to reject screenshot-as-raw")
    mut2 = copy.deepcopy(record)
    mut2["authentication_results_policy"]["auth_results_may_satisfy_counterparty_authority"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("inbound-vault schema failed to reject auth-results as authority")
    mut3 = copy.deepcopy(record)
    mut3["downstream_locks"]["may_create_response_record"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("inbound-vault schema failed to reject direct response creation")
    mut4 = copy.deepcopy(record)
    mut4["transport_header_requirements"]["deadline_may_start_now"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("inbound-vault schema failed to reject pre-dispatch deadline start")
    mut5 = copy.deepcopy(record)
    mut5["raw_reply_acceptance_contract"]["capture_shell_may_satisfy_custody"] = True
    if not list(validator.iter_errors(mut5)):
        raise SystemExit("inbound-vault schema failed to reject capture-shell-as-custody")

print("audit_external_contact_inbound_vault_precommit: OK")
