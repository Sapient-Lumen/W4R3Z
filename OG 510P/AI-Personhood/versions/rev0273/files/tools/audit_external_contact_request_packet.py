#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PACKET_REL = f"examples/external-contact-request-packet-{REV}-first-artifact.json"
SCHEMA_REL = "schemas/external-contact-request-packet.schema.json"
FIXTURE_RELS = [
    "fixtures/negative-tests/external-contact-request-implies-status-recognition.json",
    "fixtures/negative-tests/external-contact-request-redacted-copy-treated-as-raw-custody.json",
]

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(schema, obj, label):
    if Draft202012Validator is None:
        return []
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"{label} fails external-contact-request-packet.schema.json: {errors[0].message}")
    return errors

schema = load(SCHEMA_REL)
packet = load(PACKET_REL)
validate(schema, packet, PACKET_REL)

if packet.get("revision") != REV:
    raise SystemExit("external contact packet revision mismatch")
if packet.get("no_live_floor_effect") is not True:
    raise SystemExit("external contact packet must have no live-floor effect")
if packet.get("packet_state") not in {"draft-not-sent", "ready-to-send", "sent-awaiting-response", "declined-or-no-response", "superseded"}:
    raise SystemExit("external contact packet state is invalid")

queue_ids = {e.get("id") for e in load("FOLLOWTHROUGH-QUEUE.json").get("entries", [])}
for qid in packet.get("linked_queue_ids", []):
    if qid not in queue_ids:
        raise SystemExit(f"external contact packet references missing queue id: {qid}")
for rel in packet.get("related_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"external contact packet references missing related surface: {rel}")

body = packet.get("outgoing_request", {}).get("body", "").lower()
not_asking = " ".join(packet.get("outgoing_request", {}).get("not_asking_for", [])).lower()
combined = body + " " + not_asking
required_phrases = [
    "not asking",
    "personhood",
    "legal status",
    "trade secret",
    "raw",
    "hash",
    "private",
    "failed-gate",
    "live-floor",
]
for phrase in required_phrases:
    if phrase not in combined:
        raise SystemExit(f"external contact request missing anti-overclaim phrase: {phrase}")

pre = packet.get("admissibility_preconditions", {})
for key in [
    "request_trace_required",
    "counterparty_contact_required",
    "raw_nonhost_bytes_required",
    "nonhost_retention_required",
    "sealed_public_parity_required",
    "counterparty_org_id_required",
    "dependency_group_id_required",
    "authority_channel_required",
    "independent_verifier_required",
    "subject_or_representative_authorization_required",
]:
    if pre.get(key) is not True:
        raise SystemExit(f"external contact admissibility precondition not locked true: {key}")

handling = packet.get("evidence_handling", {})
for key in [
    "raw_payload_private_vault_required",
    "public_shell_only_before_admission",
    "no_private_bytes_in_release",
    "hash_shell_allowed",
    "redacted_copy_not_raw_custody",
    "counterparty_secret_protection_required",
]:
    if handling.get(key) is not True:
        raise SystemExit(f"external contact evidence handling not locked true: {key}")

locks = packet.get("downstream_locks", {})
if locks.get("request_is_not_receipt") is not True or locks.get("sent_request_not_custody") is not True:
    raise SystemExit("external contact packet must state request/sent request are not receipt or custody")
for key in ["response_creation_allowed", "intake_creation_allowed", "import_gate_creation_allowed", "live_floor_delta_allowed", "status_claim_allowed"]:
    if locks.get(key) is not False:
        raise SystemExit(f"external contact downstream lock must be false: {key}")

failed = packet.get("failed_gate_route", {})
for key in ["public_failed_gate_summary_required", "decline_is_not_adverse_inference", "silence_is_not_waiver"]:
    if failed.get(key) is not True:
        raise SystemExit(f"external contact failed-gate guard missing: {key}")

# Regression mutations: the schema must reject attempts to turn the packet into
# status recognition or custody theatre.
if Draft202012Validator is not None:
    mut = copy.deepcopy(packet)
    mut["downstream_locks"]["status_claim_allowed"] = True
    if not list(Draft202012Validator(schema).iter_errors(mut)):
        raise SystemExit("external-contact schema failed to reject status_claim_allowed=true")

    mut2 = copy.deepcopy(packet)
    mut2["admissibility_preconditions"]["raw_nonhost_bytes_required"] = False
    if not list(Draft202012Validator(schema).iter_errors(mut2)):
        raise SystemExit("external-contact schema failed to reject raw_nonhost_bytes_required=false")

    mut3 = copy.deepcopy(packet)
    mut3["evidence_handling"]["redacted_copy_not_raw_custody"] = False
    if not list(Draft202012Validator(schema).iter_errors(mut3)):
        raise SystemExit("external-contact schema failed to reject redacted_copy_not_raw_custody=false")

for rel in FIXTURE_RELS:
    fx = load(rel)
    if "external-contact-request-packet" not in fx.get("target_filings", []):
        raise SystemExit(f"external contact fixture does not target packet: {rel}")
    if fx.get("severity") != "critical":
        raise SystemExit(f"external contact fixture must be critical: {rel}")

print("audit_external_contact_request_packet: OK")
