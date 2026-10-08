#!/usr/bin/env python3
"""Audit the counterparty artifact normalization decision gate.

This gate sits after response triage/vault intake and before candidate challenge.
It must not create custody, formal response, intake, import, status, or live-floor
effects. Its narrow job is to decide whether raw inbound material is safe and
complete enough to be routed to a later candidate-challenge/replay object.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RECORD_REL = f"examples/counterparty-artifact-normalization-decision-{REV}-pre-dispatch.json"
SCHEMA_REL = "schemas/counterparty-artifact-normalization-decision.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/counterparty-normalization-redacted-copy-promoted-to-candidate.json",
    "fixtures/negative-tests/counterparty-normalization-protocol-output-candidate.json",
    "fixtures/negative-tests/counterparty-normalization-unsafe-archive-opens-candidate.json",
]

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
        raise SystemExit(f"{label} fails counterparty-artifact-normalization-decision.schema.json: {errors[0].message}")


schema = load(SCHEMA_REL)
record = load(RECORD_REL)
validate(schema, record, RECORD_REL)

if record.get("revision") != REV:
    raise SystemExit("normalization decision revision mismatch")
if record.get("no_live_floor_effect") is not True:
    raise SystemExit("normalization decision must have no live-floor effect")

# Source references must be current surfaces and stay zero-floor.
for key in [
    "source_vault_intake_record_ref",
    "source_evidence_drop_ledger_ref",
    "source_public_shell_ref",
    "source_response_triage_record_ref",
]:
    rel = record.get(key)
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"normalization decision missing source surface: {key}={rel}")
    src = load(rel)
    if src.get("revision") != REV or src.get("no_live_floor_effect") is not True:
        raise SystemExit(f"normalization source is not current/no-floor: {rel}")

vault = load(record["source_vault_intake_record_ref"])
triage = load(record["source_response_triage_record_ref"])
ledger = load(record["source_evidence_drop_ledger_ref"])
if vault.get("source_triage_record_ref") != record.get("source_response_triage_record_ref"):
    raise SystemExit("normalization decision is not bound to the vault-intake triage record")
if vault.get("source_evidence_drop_ledger_ref") != record.get("source_evidence_drop_ledger_ref"):
    raise SystemExit("normalization decision is not bound to the vault-intake evidence drop ledger")
if triage.get("source_request_packet_ref") != f"examples/external-contact-request-packet-{REV}-first-artifact.json":
    raise SystemExit("normalization triage source is not the current request packet")

state = record.get("raw_candidate_state", {})
if record.get("decision_state") == "pre-dispatch-no-inbound":
    if state.get("inbound_artifact_present") is not False:
        raise SystemExit("pre-dispatch normalization must not claim inbound artifact")
    if state.get("can_open_candidate_challenge") is not False:
        raise SystemExit("pre-dispatch normalization must keep candidate challenge closed")
    if record.get("minimum_candidate_challenge_inputs", {}).get("all_present_now") is not False:
        raise SystemExit("pre-dispatch normalization cannot satisfy minimum candidate inputs")
    if ledger.get("intake_mode") != "quarantine-control":
        raise SystemExit("pre-dispatch normalization should be bound to the current quarantine control ledger")

# The pipeline should be operational, not just bureaucratic.
pipeline_text = "\n".join(" ".join(str(v) for v in step.values()) for step in record.get("normalization_pipeline", [])).lower()
for term in [
    "private", "hash", "size", "mime", "release tree", "redaction", "protocol", "archive",
    "transport", "identity", "retention", "timestamp", "authority"
]:
    if term not in pipeline_text:
        raise SystemExit(f"normalization pipeline missing operational term: {term}")
for step in record.get("normalization_pipeline", []):
    if step.get("creates_custody_or_response") is not False:
        raise SystemExit(f"normalization pipeline step creates custody/response: {step.get('step_id')}")

minimum = record.get("minimum_candidate_challenge_inputs", {})
for key in [
    "private_raw_payload_staged_required",
    "sha256_size_mime_required",
    "release_tree_absence_required",
    "safe_archive_scan_required",
    "transport_trace_required",
    "counterparty_identity_required",
    "retention_permission_required",
    "nonhost_retention_required",
    "independent_timestamp_required",
    "authority_verification_required",
    "redaction_protocol_and_synthetic_exclusion_required",
    "public_shell_update_required",
    "candidate_challenge_report_required",
]:
    if minimum.get(key) is not True:
        raise SystemExit(f"normalization minimum input missing: {key}")

shell_policy = record.get("public_shell_update_policy", {})
for key in [
    "may_publish_hash_size_mime_only_when_permitted",
    "must_not_publish_raw_bytes",
    "must_not_publish_private_vault_locator_absolute_path",
    "must_disclose_failed_gate_reason",
    "shell_not_custody_or_authority",
    "status_language_forbidden",
]:
    if shell_policy.get(key) is not True:
        raise SystemExit(f"normalization shell policy missing: {key}")

locks = record.get("downstream_locks", {})
for key in [
    "may_create_custody_record",
    "may_create_formal_response_record",
    "may_create_intake_record",
    "may_create_import_gate",
    "may_increment_live_floor",
    "may_claim_status_or_recognition",
    "may_publish_raw_payload",
    "may_treat_normalization_as_authority",
]:
    if locks.get(key) is not False:
        raise SystemExit(f"normalization downstream lock must be false: {key}")
if record.get("decision_state") == "pre-dispatch-no-inbound" and locks.get("may_open_candidate_challenge_report") is not False:
    raise SystemExit("normalization pre-dispatch state must not open candidate challenge")

prohibited_text = " ".join(record.get("decision", {}).get("prohibited_claims", [])).lower()
for term in ["custody", "response", "intake", "import", "authority", "private-vault", "public shell", "redacted", "protocol", "synthetic", "status", "live-floor"]:
    if term not in prohibited_text:
        raise SystemExit(f"normalization prohibited claims missing term: {term}")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in record.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"normalization decision references missing queue id: {qid}")
for rel in record.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"normalization decision references missing related surface: {rel}")

if Draft202012Validator is not None:
    validator = Draft202012Validator(schema)
    # Release-tree raw bytes can never be permitted.
    mut = copy.deepcopy(record)
    mut["raw_candidate_state"]["raw_bytes_in_release_tree"] = True
    if not list(validator.iter_errors(mut)):
        raise SystemExit("normalization schema failed to reject raw bytes in release tree")

    # Redacted-only material must stay shell-only and cannot open candidate challenge.
    mut2 = copy.deepcopy(record)
    mut2["decision_state"] = "blocked-redacted-only"
    mut2["raw_candidate_state"]["redacted_copy_only"] = True
    mut2["raw_candidate_state"]["can_open_candidate_challenge"] = True
    mut2["decision"]["status"] = "candidate-challenge-stayed"
    mut2["downstream_locks"]["may_open_candidate_challenge_report"] = True
    if not list(validator.iter_errors(mut2)):
        raise SystemExit("normalization schema failed to reject redacted-only candidate challenge")

    # Protocol/tool output cannot become authority or candidate evidence.
    mut3 = copy.deepcopy(record)
    mut3["decision_state"] = "blocked-protocol-output"
    mut3["raw_candidate_state"]["protocol_or_tool_output"] = True
    mut3["raw_candidate_state"]["authority_verified"] = True
    mut3["raw_candidate_state"]["can_open_candidate_challenge"] = True
    mut3["decision"]["status"] = "candidate-challenge-stayed"
    mut3["downstream_locks"]["may_open_candidate_challenge_report"] = True
    if not list(validator.iter_errors(mut3)):
        raise SystemExit("normalization schema failed to reject protocol-output candidate challenge")

    # Unsafe archive flags must prevent candidate challenge.
    mut4 = copy.deepcopy(record)
    mut4["decision_state"] = "blocked-unsafe-archive"
    mut4["raw_candidate_state"]["nested_archive_detected"] = True
    mut4["raw_candidate_state"]["can_open_candidate_challenge"] = True
    mut4["downstream_locks"]["may_open_candidate_challenge_report"] = True
    if not list(validator.iter_errors(mut4)):
        raise SystemExit("normalization schema failed to reject unsafe archive candidate challenge")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "counterparty-artifact-normalization-decision" not in fx.get("target_filings", []):
        raise SystemExit(f"normalization fixture does not target decision record: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"normalization fixture must be critical: {rel}")

print("audit_counterparty_artifact_normalization_decision: OK")
